"""A register chunk in a bundle carries its own entry's id, not the register's last entry's (W2-131; DEC-1082 (2)).

Regression evidence only (DEC-136). The planted register holds DEC-1082, DEC-476 and DEC-999: as text, DEC-999 sorts
last, so it is the id the path map gave every register chunk before the fix. Each store is built in a temporary git
repository, with the secret filter replaced, no vectors and no model: the lexical route only, the reranker and the
semantic route stood in for.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import records, store  # noqa: E402
from gov.retrieval import lexical, retrieve, semantic  # noqa: E402

BEFORE = "72cf8df13a041f285dd1b77f0461c547cefc3173"  # w2/W2-131 before the fix: integrate with the acceptance cases
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
REGISTER = "decisions/REGISTER.md"
TICKET, LESSON = "work/T-001.md", "lessons/L-001.md"
# DEC-1082 is long enough to be cut into several chunks under one parent: a hit on its last chunk is expanded
FILLER = "".join(f"- **Note {n}:** the label rule is applied to the bundle's register items, one by one.\n"
                 for n in range(40))
TEXT = ("# Decision register\n\nThe register's preface names the zinnia rule.\n\n"
        "### DEC-1082 — Labels\n- **Status:** ACCEPTED\n- **Decision:** a label names its own entry.\n"
        f"{FILLER}- **Last:** the tamarind clause closes the entry.\n\n"
        "### DEC-476 — The pool\n- **Status:** ACCEPTED\n- **Decision:** the pool holds marigold workers.\n\n"
        "## Interlude\n\nA note between the entries on the lotus rule.\n\n"
        "### DEC-999 — The queue\n- **Status:** ACCEPTED\n- **Decision:** the queue holds juniper tasks.\n")
FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
    REGISTER: TEXT,
    TICKET: "---\nid: T-001\ntype: task\nstatus: OPEN\ndepends_on: [L-001]\n---\n# T-001\n\n"
            "The ticket on marigold, marigold and marigold again: marigold workers.\n",
    # the lesson answers no question below but "heron": it reaches a "marigold" bundle only by the ticket's closure
    LESSON: "---\nid: L-001\ntype: lesson\nstatus: ACCEPTED\n---\n# L-001\n\nA lesson on the heron ledger.\n",
}


def _stand_ins(monkeypatch, module):
    """No model: no reranker, no semantic route."""
    monkeypatch.setattr(module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository whose path map names a register of DEC-1082, DEC-476 and DEC-999, with a ticket and a lesson."""
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": False, "reason": "off", "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda root: False)
    _stand_ins(monkeypatch, retrieve)
    for rel, text in FILES.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the register"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(tmp_path)})
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    return tmp_path


def _line(text):
    return TEXT.split("\n").index(text) + 1


def _register_items(bundle):
    return [item for item in bundle["evidence"] if item["path"] == REGISTER]


# -- S1: each register item is its own entry ----------------------------------------------------------------------

def test_the_planted_store_holds_three_entries_and_dec_999_sorts_last(project):
    entries = [record["id"] for record in records.records(project) if record.get("span") is not None]
    assert entries == ["DEC-1082", "DEC-476", "DEC-999"]


def test_a_chunk_inside_dec_476_is_labelled_dec_476(project):
    items = _register_items(retrieve.retrieve(project, "marigold"))
    assert [(item["id"], item["start_line"]) for item in items] == [("DEC-476", _line("### DEC-476 — The pool"))]
    assert items[0]["entry"] == "DEC-476"


def test_a_chunk_in_the_preface_carries_its_chunk_id(project):
    items = _register_items(retrieve.retrieve(project, "zinnia"))
    assert len(items) == 1 and items[0]["start_line"] == 1
    assert items[0]["id"] == items[0]["chunk_id"] and "entry" not in items[0]


def test_a_chunk_between_entries_carries_its_chunk_id(project):
    items = _register_items(retrieve.retrieve(project, "lotus"))
    assert [item["start_line"] for item in items] == [_line("## Interlude")]
    assert items[0]["id"] == items[0]["chunk_id"] and "entry" not in items[0]


def test_a_parent_expansion_carries_its_first_entry_s_id(project):
    bundle = retrieve.retrieve(project, "tamarind")
    heading = _line("### DEC-1082 — Labels")
    assert [(e["path"], e["start_line"]) for e in bundle["expansions"]] == [(REGISTER, heading)]
    assert bundle["expansions"][0]["chunk_id"] != bundle["expansions"][0]["parent_id"]
    items = _register_items(bundle)
    assert [(item["id"], item["entry"], item["start_line"]) for item in items] == [("DEC-1082", "DEC-1082", heading)]
    assert items[0]["end_line"] > _line("- **Last:** the tamarind clause closes the entry.") - 1


def test_every_register_item_s_id_agrees_with_its_entry_key(project):
    for query in ("marigold", "tamarind", "juniper", "zinnia", "lotus", "label rule"):
        for item in _register_items(retrieve.retrieve(project, query)):
            assert item["id"] == item.get("entry", item["chunk_id"]), (query, item["start_line"])
            assert item["id"] != "DEC-999" or item["entry"] == "DEC-999"


def test_a_record_file_keeps_its_own_id(project):
    items = [item for item in retrieve.retrieve(project, "marigold")["evidence"] if item["path"] != REGISTER]
    assert {item["path"]: item["id"] for item in items} == {TICKET: "T-001"}
    items = retrieve.retrieve(project, "heron")["evidence"]
    assert {item["path"]: item["id"] for item in items} == {LESSON: "L-001"}


# -- S2: no register entry stands for the register's path ----------------------------------------------------------

def test_the_path_map_holds_no_register_entry(project):
    record_of, not_current, types = retrieve._graph(project)
    assert REGISTER not in record_of
    assert not {"DEC-1082", "DEC-476", "DEC-999"} & set(record_of.values())
    assert record_of == {TICKET: "T-001", LESSON: "L-001"}
    assert {rid: types[rid] for rid in ("DEC-476", "DEC-999", "L-001")} == {
        "DEC-476": "decision", "DEC-999": "decision", "L-001": "lesson"}  # the types map still holds every record


def test_dec_424_still_lifts_a_lesson_in_the_ticket_s_closure(project, monkeypatch):
    lifted = [item["path"] for item in retrieve.retrieve(project, "marigold", ticket="T-001", radius=1)["evidence"]]
    monkeypatch.setattr(retrieve, "AHEAD_TYPES", frozenset())
    unlifted = [item["path"] for item in retrieve.retrieve(project, "marigold", ticket="T-001", radius=1)["evidence"]]
    assert LESSON not in [item["path"] for item in retrieve.retrieve(project, "marigold")["evidence"]]
    assert lifted[0] == LESSON, lifted  # DEC-424: the lesson in the ticket's closure, ahead of all
    assert unlifted[0] != LESSON and sorted(lifted) == sorted(unlifted), unlifted  # without the move, not first


# -- S3: nothing else in a bundle changes --------------------------------------------------------------------------

def _before(monkeypatch):
    """``retrieve`` as it stood before the fix, loaded from git; skipped where the history does not hold it."""
    shown = subprocess.run(["git", "-C", str(REPO), "show", f"{BEFORE}:src/gov/retrieval/retrieve.py"],
                           capture_output=True, text=True)
    if shown.returncode:
        pytest.skip(f"the history does not hold {BEFORE[:12]}: {shown.stderr.strip()}")
    spec = importlib.util.spec_from_loader("gov.retrieval._retrieve_before_w2_131", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(shown.stdout, "retrieve_before_w2_131.py", "exec"), module.__dict__)
    _stand_ins(monkeypatch, module)
    return module


CALLS = [("marigold", {}), ("tamarind", {}), ("zinnia", {}), ("lotus", {}), ("label rule", {}),
         ("label rule", {"batch_size": 1}), ("marigold", {"ticket": "T-001", "radius": 1}),
         ("label rule", {"ids": ["DEC-1082"], "radius": 1}), ("label rule", {"bundle_budget": 200})]


def test_the_bundle_is_the_same_before_and_after_but_for_register_ids(project, monkeypatch):
    # one test over every call, not parametrised: the opt-in lists keep only a parametrised test's first row
    before, register_items = _before(monkeypatch), 0
    for query, kwargs in CALLS:
        old = before.retrieve(project, query, **kwargs)
        new = retrieve.retrieve(project, query, **kwargs)
        assert set(old) == set(new), (query, kwargs)
        for key in set(new) - {"evidence"}:  # the batches, budget, gaps, continuation, expansions, drops, facets
            assert old[key] == new[key], (query, kwargs, key)
        assert len(old["evidence"]) == len(new["evidence"]), (query, kwargs)
        for was, now in zip(old["evidence"], new["evidence"]):  # the same items in the same order
            assert {k: v for k, v in was.items() if k != "id"} == {k: v for k, v in now.items() if k != "id"}
            if now["path"] != REGISTER:
                assert was["id"] == now["id"], (query, kwargs)
            else:
                register_items += 1
                assert was["id"] == "DEC-999"  # the cause: the register's last entry by id, on every register item
                assert now["id"] == now.get("entry", now["chunk_id"]), (query, kwargs)
    assert register_items >= len(CALLS)


def test_the_continuation_carries_on_the_same_before_and_after(project, monkeypatch):
    before = _before(monkeypatch)
    old = before.retrieve(project, "label rule", batch_size=1)
    new = retrieve.retrieve(project, "label rule", batch_size=1)
    assert new["continuation"] is not None and old["continuation"] == new["continuation"]
    old_next = before.retrieve(project, "label rule", batch_size=1, continuation=old["continuation"])
    new_next = retrieve.retrieve(project, "label rule", batch_size=1, continuation=new["continuation"])
    strip = lambda bundle: [{k: v for k, v in item.items() if k != "id"} for item in bundle["evidence"]]  # noqa: E731
    assert strip(old_next) == strip(new_next) and old_next["continuation"] == new_next["continuation"]
    assert [item["id"] for item in new_next["evidence"] if item["path"] == REGISTER] == \
        [item.get("entry", item["chunk_id"]) for item in new_next["evidence"] if item["path"] == REGISTER]
