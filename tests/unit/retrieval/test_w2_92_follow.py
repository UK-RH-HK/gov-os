"""Builder tests for W2-92 S8 and S9 (DEC-1072 (1), DEC-1073 (2)): retrieval follows the stated links one bounded hop,
and every register chunk it carries names its entry's status and changers.

Regression evidence only (DEC-136). ``follow`` is asked on planted links; ``retrieve`` on a planted repository whose
store and lexical index are built in a temporary folder (the store test's register, ticket and records, and one
proposed specification), with no embedder, reranker or model. The hop goes from a ticket to its decisions and from an
amended or superseded decision to the decision that changes it, never back; it is bounded; today's closure chunks keep
their places; a decision superseded in part stays current, and the decision changing it is in reach and named in the
closure facet. The links never reach the edges or the authority order. A record not in force is marked so on its
evidence item, its text unchanged.
"""
from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests/unit/store"))

from gov import store  # noqa: E402
from gov.retrieval import authority, graph_route, lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieval  # noqa: E402
from gov.store import loader  # noqa: E402
from test_w2_92_links import FILES  # noqa: E402

REGISTER = "docs/DECISION_REGISTER.md"
SPEC = "docs/specs/SPEC-1.md"  # a record of a file that is not in force
S9_KEYS = ("entry", "status", "changed_by", "in_force", "not_in_force", "also")

LINKS = [{"type": kind, "source": source, "target": target, "via": "x"} for kind, source, target in [
    ("CITES", "T-1", "DEC-3"), ("CITES", "T-1", "DEC-1"), ("CITES", "T-2", "DEC-5"), ("CITES", "CP-1", "DEC-9"),
    ("OF_TASK", "CP-1", "T-1"), ("UNDER", "DEC-3", "DEC-2"), ("AMENDS", "DEC-7", "DEC-3"),
    ("AMENDS", "DEC-10", "DEC-3"), ("SUPERSEDES", "DEC-8", "DEC-1"), ("AMENDS", "DEC-6", "DEC-5")]]
DECISIONS = {f"DEC-{n}" for n in range(1, 11)}


def test_the_hop_goes_from_a_ticket_to_its_decisions_and_from_a_decision_to_its_changers():
    hop = graph_route.follow(LINKS, ["T-1"], {"T-1"}, DECISIONS)
    # what T-1 cites, then the changers of what that added (newest first); never what cites T-1 (CP-1)
    assert hop == {"records": ["DEC-1", "DEC-3", "DEC-8", "DEC-10", "DEC-7"], "left": 0,
                   "changed_by": {"DEC-1": ["DEC-8"], "DEC-3": ["DEC-10", "DEC-7"]}}
    # from a decision: its changers and what it stands under; never the tickets that cite it
    assert graph_route.follow(LINKS, ["DEC-3"], {"DEC-3"}, DECISIONS)["records"] == ["DEC-10", "DEC-7", "DEC-2"]
    # from the changer, nothing goes back to what it changes
    assert graph_route.follow(LINKS, ["DEC-7"], {"DEC-7"}, DECISIONS)["records"] == []


def test_the_start_records_come_before_the_rest_of_the_closure(monkeypatch):
    monkeypatch.setattr(graph_route, "FOLLOW_RECORDS", 3)
    hop = graph_route.follow(LINKS, ["T-2"], {"T-1", "T-2"}, DECISIONS)
    # T-2's decision and its changer, then what the rest of the closure cites; the changers of those are two hops
    assert hop["records"] == ["DEC-5", "DEC-6", "DEC-1"] and hop["left"] == 1
    assert hop["changed_by"] == {"DEC-1": ["DEC-8"], "DEC-5": ["DEC-6"]}  # what the bound kept out is not named


def test_the_hop_is_bounded_and_says_how_much_it_left():
    many = [{"type": "CITES", "source": "T-1", "target": f"DEC-{n}", "via": "sources"} for n in range(1, 41)]
    hop = graph_route.follow(many, ["T-1"], {"T-1"}, set())
    assert (graph_route.FOLLOW_RECORDS, graph_route.FOLLOW_CHUNKS) == (12, 2)  # the prototype's bound: 24 chunks
    assert len(hop["records"]) == 12 and hop["left"] == 40 - 12
    assert hop["records"][:3] == ["DEC-1", "DEC-2", "DEC-3"]  # by id, as numbers
    assert graph_route.follow(many, ["T-1"], {"T-1"}, set()) == hop


def test_a_record_already_reached_is_not_added_again():
    assert graph_route.follow(LINKS, ["T-1"], {"T-1", "DEC-1", "DEC-3"}, DECISIONS)["records"] == [
        "DEC-8", "DEC-10", "DEC-7", "DEC-2"]  # the reached decisions' changers, then what DEC-3 stands under


needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """The store test's planted repository, with a path map that indexes everything, indexed and loaded."""
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    planted = {**FILES, SPEC: "---\nid: SPEC-1\ntype: specification\nstatus: PROPOSED\n---\n# The crane spec\n\n"
                              "The crane lifts two boats.\n"}
    for rel, text in planted.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map["decision_register"] = "docs/DECISION_REGISTER.md"
    (tmp_path / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    return tmp_path


@pytest.fixture()
def seen(monkeypatch):
    """The routes each retrieve fused, the last call's."""
    routes = {}
    fuse = retrieval.rrf

    def kept(given, **kwargs):
        routes.clear()
        routes.update(given)
        return fuse(given, **kwargs)

    monkeypatch.setattr(retrieval, "rrf", kept)
    return routes


def _entry_lines(root: Path, *ids: str) -> list[int]:
    lines = (root / "docs/DECISION_REGISTER.md").read_text(encoding="utf-8").split("\n")
    return [next(n for n, line in enumerate(lines, 1) if line.startswith(f"### {rid} ")) for rid in ids]


def _ask(root, query, **kwargs):
    return retrieval.retrieve(root, query, reranker=lambda: None, **kwargs)


@needs_gitleaks
def test_a_decision_superseded_in_part_stays_current_and_its_changer_is_in_reach(repo, seen):
    bundle = _ask(repo, "What does DEC-104 say about mooring?")
    assert bundle["merge"]["dropped"] == []
    (own,) = _entry_lines(repo, "DEC-104")
    assert any(item["start_line"] == own and item["path"] == "docs/DECISION_REGISTER.md"
               for item in bundle["evidence"])
    changer = _entry_lines(repo, "DEC-103")[0]
    assert [chunk["start_line"] for chunk in seen["closure"]] == [own, changer]
    assert bundle["facets"]["closure"] == {"available": True, "reason": None,
                                           "followed": {"records": ["DEC-103"], "left": 0},
                                           "changed_by": {"DEC-104": ["DEC-103"]}}
    assert bundle == _ask(repo, "What does DEC-104 say about mooring?")


@needs_gitleaks
def test_a_tickets_decisions_join_after_todays_closure_chunks(repo, seen, monkeypatch):
    _ask(repo, "What does DAEO-aaaa need?")
    now = list(seen["closure"])
    monkeypatch.setattr(graph_route, "stated_links", lambda _root: [])
    today = _ask(repo, "What does DAEO-aaaa need?")
    assert "followed" not in today["facets"]["closure"]
    assert now[:len(seen["closure"])] == seen["closure"]  # today's closure, in its order, first
    assert {chunk["path"] for chunk in seen["closure"]} == {".tickets/DAEO-aaaa.md", ".tickets/DAEO-bbbb.md"}
    added = now[len(seen["closure"]):]
    assert [chunk["start_line"] for chunk in added if chunk["path"] == "docs/DECISION_REGISTER.md"] == _entry_lines(
        repo, "DEC-101", "DEC-104", "DEC-102", "DEC-103")  # its decisions, then the decisions that change them
    assert [chunk["path"] for chunk in added][0] == "docs/contract/CAP-01.md"


@needs_gitleaks
def test_the_closure_grows_by_at_most_the_bound(repo, seen, monkeypatch):
    stored = graph_route.stated_links(repo)
    sizes = {}
    for name, links, records, chunks in [("today", [], 12, 2), ("unbounded", stored, 99, 99),
                                         ("bounded", stored, 2, 1)]:
        monkeypatch.setattr(graph_route, "stated_links", lambda _root, links=links: links)
        monkeypatch.setattr(graph_route, "FOLLOW_RECORDS", records)
        monkeypatch.setattr(graph_route, "FOLLOW_CHUNKS", chunks)
        bundle = _ask(repo, "What does DAEO-aaaa need?")
        sizes[name] = len(seen["closure"])
    assert bundle["facets"]["closure"]["followed"] == {"records": ["CAP-01", "DEC-101"], "left": 3}
    assert sizes["unbounded"] == sizes["today"] + 5  # five records found, one chunk each in this register
    assert sizes["bounded"] == sizes["today"] + 2  # FOLLOW_RECORDS records of FOLLOW_CHUNKS chunks at most




def _without_status(bundle: dict) -> dict:
    """The bundle with S9's marks taken off its evidence items: what it was before them."""
    return {**bundle, "evidence": [{key: value for key, value in item.items() if key not in S9_KEYS}
                                   for item in bundle["evidence"]]}


@needs_gitleaks
def test_the_links_never_reach_the_edges_or_the_authority_order(repo, monkeypatch):
    """S4, S7: a whole supersession the links state (DEC-106 over DEC-105) is no edge for the authority order; a partial
    one (DEC-103 over DEC-104) drops nothing from what is current."""
    given = []
    order = authority.order
    monkeypatch.setattr(authority, "order", lambda root, known, edges, entry_of: (
        given.extend(edges), order(root, known, edges, entry_of))[1])
    bundle = _ask(repo, "What is DEC-105, and DEC-104?")
    assert sorted((edge["source"], edge["target"]) for edge in given) == [("DEC-108", "DEC-109")]  # the store's
    assert bundle["facets"]["closure"]["changed_by"] == {"DEC-104": ["DEC-103"], "DEC-105": ["DEC-106"]}
    assert bundle["merge"]["dropped"] == []


@needs_gitleaks
def test_a_question_naming_no_record_is_unchanged_but_for_the_status_marks(repo, monkeypatch):
    asked = _ask(repo, "Where is the pier kept dry?")
    assert "closure" not in asked["facets"]
    assert any(item["path"] == REGISTER for item in asked["evidence"])
    stored = graph_route.stated_links
    monkeypatch.setattr(graph_route, "stated_links", lambda _root: [])
    today = _ask(repo, "Where is the pier kept dry?")
    assert _without_status(today) == _without_status(asked)  # today's bundle, item for item, but for the marks
    monkeypatch.setattr(graph_route, "stated_links", stored)
    assert _ask(repo, "Where is the pier kept dry?") == asked  # two runs on one store: the same bundle


@needs_gitleaks
def test_a_store_built_before_the_links_names_it_and_gives_todays_closure(repo, seen, monkeypatch):
    connection = sqlite3.connect(repo / store.STORE_REL)
    connection.execute(f"DROP TABLE {loader.LINKS_TABLE}")
    connection.commit()
    connection.close()
    bundle = _ask(repo, "What does DAEO-aaaa need?")
    assert bundle["facets"]["closure"] == {"available": True, "reason": None,
                                           "stated_links": retrieval.NO_STATED_LINKS}
    before = list(seen["closure"])
    monkeypatch.setattr(graph_route, "stated_links", lambda _root: [])
    today = _ask(repo, "What does DAEO-aaaa need?")
    assert seen["closure"] == before and today["evidence"] == bundle["evidence"]


@needs_gitleaks
def test_every_register_chunk_names_its_status_and_changers_and_one_not_in_force_says_so(repo):
    """S9, DEC-1073 (2): PROPOSED and SUPERSEDED are not in force; a whole supersession stated by the links leaves the
    word ACCEPTED and is not in force; one in part leaves its target in force, its changer named."""
    bundle = _ask(repo, "What do DEC-111, DEC-105, DEC-109 and DEC-104 say?")
    lines = dict(zip(("DEC-111", "DEC-105", "DEC-109", "DEC-104"),
                     _entry_lines(repo, "DEC-111", "DEC-105", "DEC-109", "DEC-104")))
    register = [item for item in bundle["evidence"] if item["path"] == REGISTER]
    assert register and all({"entry", "status", "changed_by", "in_force"} <= item.keys() for item in register)
    marked = {item["start_line"]: {key: item[key] for key in S9_KEYS if key in item} for item in register}
    assert marked[lines["DEC-111"]] == {"entry": "DEC-111", "status": "PROPOSED", "changed_by": [],
                                        "in_force": False, "not_in_force": "PROPOSED"}
    assert marked[lines["DEC-105"]] == {"entry": "DEC-105", "status": "ACCEPTED", "changed_by": ["DEC-106"],
                                        "in_force": False, "not_in_force": "SUPERSEDED"}
    assert marked[lines["DEC-109"]] == {"entry": "DEC-109", "status": "SUPERSEDED", "changed_by": ["DEC-108"],
                                        "in_force": False, "not_in_force": "SUPERSEDED"}
    assert marked[lines["DEC-104"]] == {"entry": "DEC-104", "status": "ACCEPTED", "changed_by": ["DEC-103"],
                                        "in_force": True}
    text = (repo / REGISTER).read_text(encoding="utf-8").split("\n")
    for item in register:  # the text is unchanged: the mark stands beside it
        assert item["text"] == "\n".join(text[item["start_line"] - 1:item["end_line"]]) + "\n"


@needs_gitleaks
def test_a_register_chunk_carries_its_status_whatever_the_question(repo):
    """S9: a question naming no record still gets each register chunk's status and changers."""
    bundle = _ask(repo, "Where is the pier kept dry?")
    (own,) = _entry_lines(repo, "DEC-101")
    item = next(item for item in bundle["evidence"] if item["path"] == REGISTER and item["start_line"] == own)
    assert (item["entry"], item["status"], item["changed_by"], item["in_force"]) == (
        "DEC-101", "ACCEPTED", ["DEC-102"], True)


@needs_gitleaks
def test_a_record_file_not_in_force_says_so_and_records_of_work_carry_no_mark(repo):
    bundle = _ask(repo, "What does SPEC-1 say about the crane?")
    spec = [item for item in bundle["evidence"] if item["path"] == SPEC]
    assert spec and all((item["status"], item["in_force"], item["not_in_force"]) == ("PROPOSED", False, "PROPOSED")
                        for item in spec)
    work = _ask(repo, "What does DAEO-aaaa need?")  # a ticket's state is no rule: no mark on its chunks
    tickets = [item for item in work["evidence"] if item["path"].startswith(".tickets/")]
    assert tickets and not any(key in item for item in tickets for key in S9_KEYS)
    in_force = [item for item in work["evidence"] if item["path"] == "docs/contract/CAP-01.md"]
    assert not any(key in item for item in in_force for key in S9_KEYS)  # a record in force: nothing added
