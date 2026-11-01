"""KPI 4 (S4; AR-9, W2-M239, W2-M294, W2-M330): one ticket's context gives one packet hash.

Two builds give the same ``hash`` in one process, in two processes and on two stores each rebuilt from one commit;
the packet is the same whether or not the semantic index answers; supplementary items of equal relevance (ties:
identical text at different paths) are ordered by ``path``, then ``id``, whatever order the retrieval gives them; and
the context-reproducibility check is never green on a stale store and red on a fresh one.

Round 2 (DEC-1005, P-W2-04-2 (A)): the context no longer reaches the retrieval's entry, so no stand-in reorders its
items. The orders are produced from outside (README, "Orders produced from outside"): the same files written in
another order into another project at the same commit, the index's rows inserted in another order, and other hash
seeds. A question that needs the semantic route is asked through ``gov retrieve``; ``gov context`` sends it nothing.

Red reasons, today: the packet has no ``supplementary_batches`` (the tied items' rank order) and no ``ticket_text``;
semantic hits enter the supplementary block (with the ``semantic-live`` stand-in the packet changes); the check
measures a stale store as if fresh (green there, red after the reload). The cases of one process, two processes and
two stores pass today with the lexical route alone (W2-M330 asked for them with an index): they hold what the change
must keep.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

import w2_04_support as s

TICKET = "TK-W204-TIES"
TITLE = "Tide gauge datum"
KPI = "The tide gauge datum is read at dawn."
TIE_TEXT = f"# {TITLE}\n\n{KPI}\n"
TIE_PATHS = ("docs/ties/tie-d.md", "docs/ties/tie-b.md", "docs/ties/tie-a.md", "docs/ties/tie-c.md")
SEMANTIC_ONLY = "docs/semantic/gulls.md"


def _files():
    files = {path: TIE_TEXT for path in TIE_PATHS}
    # matching notes whose paths sort before the ties, so the tied items stand together in the retrieval's rank
    for number in range(6):
        files[f"docs/notes/note-{number}.md"] = f"# {TITLE}, note {number}\n\n{KPI}\n\nNote {number} of the gauge.\n"
    files[SEMANTIC_ONLY] = "# Gulls\n\nGulls nest on the breakwater in spring.\n"
    files["docs/charter/charter.md"] = s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT)
    files[f".tickets/{TICKET}.md"] = s.ticket(TICKET, TITLE, [s.CHARTER_ID], kpis=(KPI,),
                                              failure=("The gauge is read at noon.",))
    return files


@pytest.fixture(scope="module")
def ties(retrieval_api, tmp_path_factory):
    project = s.build_project(tmp_path_factory.mktemp("w2-04-ties") / "repo", _files())
    retrieval_api.build(project.root)
    return project


def _tied(packet):
    return [(item["path"], item["id"]) for item in packet[s.K_SUPPLEMENTARY] if item.get("text") == TIE_TEXT]


def _packet(api, project, env=None):
    api.reset_log()
    return api.gov(project.root, TICKET, env=env).packet


def _head(project):
    return project.git("rev-parse", "HEAD").strip()


def test_two_builds_in_one_process_give_one_hash(retrieval_api, ties):
    first, second = retrieval_api.context_calls(ties.root, TICKET, times=2)
    assert "value" in first and "value" in second, (first.get("error"), second.get("error"))
    assert first["value"][s.K_HASH] == second["value"][s.K_HASH]
    assert first["value"] == second["value"]


def test_two_builds_in_two_processes_give_one_hash(retrieval_api, ties):
    first, second = _packet(retrieval_api, ties), _packet(retrieval_api, ties)
    assert first[s.K_HASH] == second[s.K_HASH] and first == second


def test_two_stores_rebuilt_from_one_commit_give_one_hash(retrieval_api, ties, tmp_path):
    hashes = []
    for name in ("a", "b"):
        clone = tmp_path / name / "repo"
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ties.root), str(clone)], check=True,
                       capture_output=True, timeout=120)
        retrieval_api.build(clone)
        hashes.append(retrieval_api.gov(clone, TICKET).packet[s.K_HASH])
    assert hashes[0] == hashes[1], f"two stores rebuilt from one commit give two hashes: {hashes}"
    assert hashes[0] == _packet(retrieval_api, ties)[s.K_HASH], "a rebuilt store gives another hash than the first"


def test_tied_items_are_ordered_by_path_then_id(retrieval_api, ties):
    tied = _tied(_packet(retrieval_api, ties))
    assert len(tied) == len(TIE_PATHS), f"the fixture is wrong: the tied items are not all supplementary: {tied}"
    assert tied == sorted(tied), f"tied items are not in path, then id, order: {tied}"


SEEDS = ("0", "1", "4099")


def _tied_in_rank(packet):
    """The tied items among the batches' items, in the rank order the batches give (S7a)."""
    return [(path, rid) for rid, path in s.read_items(packet) if path in TIE_PATHS]


def test_tied_items_keep_one_order_whatever_order_the_retrieval_gives_them(retrieval_api, ties, tmp_path):
    """Rewrite-Reason: DEC-1005 (P-W2-04-2 (A)). The orders come from outside, never from a stand-in in the code: (a)
    the same files written in the reverse order into another project, at the same commit, its index's rows inserted
    file by file in the reverse order of their paths; (b) a clone at the same commit whose tied files' rows are
    inserted last, in the order the files were written (tie-d, tie-b, tie-a, tie-c); each computed under three hash
    seeds, each in a process of its own. Every packet is the first one, its hash included, and the tied items stand
    in ``(path, id)`` order in the stack and in the batches' rank order."""
    expected = _packet(retrieval_api, ties)
    s.assert_holds_its_ceiling(expected, ties.text(f".tickets/{TICKET}.md"))
    assert len(_tied(expected)) == len(TIE_PATHS), f"the fixture is wrong: the tied items stacked: {_tied(expected)}"
    base_rows = s.row_order(ties.root)

    files = _files()
    written = s.build_project(tmp_path / "written" / "repo", dict(reversed(list(files.items()))))
    assert _head(written) == _head(ties), "the fixture is wrong: the project written in another order is another commit"
    retrieval_api.build_in_order(written.root, sorted([*files, "README.md"], reverse=True))
    clone = tmp_path / "clone" / "repo"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ties.root), str(clone)], check=True,
                   capture_output=True, timeout=120)
    retrieval_api.build_in_order(clone, TIE_PATHS)

    for name, root in (("written in another order, rows reversed", written.root), ("tied rows last", clone)):
        rows = s.row_order(root)
        tied_rows = list(dict.fromkeys(path for path in rows if path in TIE_PATHS))
        assert sorted(rows) == sorted(base_rows) and tied_rows != list(dict.fromkeys(
            path for path in base_rows if path in TIE_PATHS)), \
            f"the fixture is wrong ({name}): the store does not give the tied rows in another order: {tied_rows}"
        for seed in SEEDS:
            packet = retrieval_api.gov(root, TICKET, env=retrieval_api.env(PYTHONHASHSEED=seed)).packet
            assert _tied(packet) == sorted(_tied(packet)), \
                f"{name}, seed {seed}: tied items follow the order the store gives them: {_tied(packet)}"
            assert _tied_in_rank(packet) == sorted(_tied_in_rank(packet)), \
                f"{name}, seed {seed}: in the batches' rank order the ties are {_tied_in_rank(packet)}"
            assert packet[s.K_HASH] == expected[s.K_HASH] and packet == expected, (
                f"{name}, seed {seed}: the order the project, the store or the process gives changes the packet: "
                f"{[item['path'] for item in packet[s.K_SUPPLEMENTARY]]} vs "
                f"{[item['path'] for item in expected[s.K_SUPPLEMENTARY]]}")


def _evidence_paths(answer):
    envelope = answer.envelope
    assert envelope.get("ok") is True, f"gov retrieve refused\n{answer.describe()}"
    return [item.get("path") for item in (envelope.get("result") or {}).get("evidence") or []]


def test_the_packet_is_the_same_whether_or_not_the_semantic_route_answers(retrieval_api, ties):
    """Rewrite-Reason: DEC-1005 (P-W2-04-2 (A)). No vector is built, so the semantic route is unavailable; the
    ``semantic-live`` stand-in makes it answer with the gulls note, which no lexical query finds. The premise is seen
    through ``gov retrieve``, the read that reaches the semantic route: with the stand-in live it finds the note,
    without it not. ``gov context`` with the stand-in live gives the packet and hash it gives with the route
    unavailable; the note stands nowhere in the packet, and the context asked the semantic route nothing."""
    live = retrieval_api.env(mode="semantic-live", W204_SEMANTIC_PATH=SEMANTIC_ONLY)
    retrieval_api.reset_log()
    assert SEMANTIC_ONLY in _evidence_paths(retrieval_api.retrieve(ties.root, TITLE, env=live)) and \
        retrieval_api.semantic_calls(), "the fixture is wrong: with the stand-in live, gov retrieve misses the note"
    assert SEMANTIC_ONLY not in _evidence_paths(retrieval_api.retrieve(ties.root, TITLE)), \
        "the fixture is wrong: a lexical query finds the semantic-only note"

    unavailable = _packet(retrieval_api, ties)
    answering = _packet(retrieval_api, ties, env=live)
    asked = retrieval_api.semantic_calls()
    s.assert_holds_its_ceiling(answering, ties.text(f".tickets/{TICKET}.md"))
    assert SEMANTIC_ONLY not in json.dumps(answering), \
        f"the semantic-only note enters the packet: {[item['path'] for item in answering[s.K_SUPPLEMENTARY]]}"
    assert answering[s.K_HASH] == unavailable[s.K_HASH] and answering == unavailable, (
        "the packet changes when the semantic index answers: "
        f"{[item['path'] for item in answering[s.K_SUPPLEMENTARY]]} vs "
        f"{[item['path'] for item in unavailable[s.K_SUPPLEMENTARY]]}")
    assert not asked, f"gov context asked the semantic route (so an embedder) {len(asked)} question(s): {asked[:2]}"


@pytest.mark.local_only
def test_with_a_live_local_embedder_the_packet_is_the_same(retrieval_api, ties, tmp_path):
    """README, "local_only": ``W204_LIVE_HOME`` names a HOME that holds the pinned CPU embedder, and Ollama with the
    pinned model answers at ``OLLAMA_HOST`` (its default when unset). Vectors are built in a clone of the project,
    and the packet with the embedder answering is the packet with it unreachable."""
    home = os.environ.get("W204_LIVE_HOME")
    if not home or not Path(home).is_dir():
        pytest.skip("W204_LIVE_HOME names no HOME with the pinned embedder (README, local_only)")
    host = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
    live = {"HOME": home, "OLLAMA_HOST": host, "GOV_QUERY_OLLAMA_HOST": os.environ.get("GOV_QUERY_OLLAMA_HOST", host)}
    clone = tmp_path / "repo"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ties.root), str(clone)], check=True,
                   capture_output=True, timeout=120)
    retrieval_api.build(clone)
    (built,) = retrieval_api.batch([("gov.retrieval.semantic", "refresh", clone, (), {})],
                                   env=retrieval_api.env(**live))
    if "value" not in built or not (built["value"] or {}).get("available"):
        pytest.skip(f"the live embedder did not build vectors: {built}")
    answered = retrieval_api.gov(clone, TICKET, env=retrieval_api.env(**live)).packet
    unreachable = retrieval_api.gov(clone, TICKET).packet
    assert answered[s.K_HASH] == unreachable[s.K_HASH], "a live semantic index changes the packet"


# --------------------------------------------------------------------------
# The context-reproducibility check on a stale store (W2-M294)
# --------------------------------------------------------------------------

SOURCE_ID, SOURCE_REL = "ADR-W204-GAUGE", "docs/adr/gauge.md"
CHECK_TICKET = "TK-W204-CHECK"


def test_the_check_is_never_green_on_a_stale_store_and_red_on_a_fresh_one(api, tmp_path):
    """The store is built at a commit where the ticket's source stands; the next commit retires it. On the stale
    store the check is red or reports the store as stale (unmeasured, by name, non-zero); after the reload it is red.
    Today: green on the stale store."""
    files = {SOURCE_REL: s.record(SOURCE_ID, "decision", "ACTIVE", "The gauge is read at dawn."),
             f".tickets/{CHECK_TICKET}.md": s.ticket(CHECK_TICKET, "The gauge check", [SOURCE_ID])}
    project = s.build_project(tmp_path / "repo", files)
    api.build(project.root, index=False)
    assert api.context_check(project.root).returncode == 0, "the fixture is wrong: the check is red at the start"

    project.write(SOURCE_REL, s.record(SOURCE_ID, "decision", "RETIRED", "The gauge is read at dawn."))
    project.commit("the source is retired")
    stale = api.context_check(project.root)
    api.load(project.root)
    fresh = api.context_check(project.root)

    assert fresh.returncode != 0, f"the fixture is wrong: the fresh store is green\n{fresh.describe()}"
    assert stale.returncode != 0, (f"green on a stale store, red on the fresh one\nstale:\n{stale.describe()}\n"
                                   f"fresh:\n{fresh.describe()}")
    said = stale.stdout.lower()
    assert "stale" in said or "unmeasured" in said or CHECK_TICKET in stale.stdout, \
        f"the stale store's result names neither the stale store nor the ticket\n{stale.describe()}"
