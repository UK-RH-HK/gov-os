"""KPI 4 (S4; AR-9, W2-M239, W2-M294, W2-M330): one ticket's context gives one packet hash.

Two builds give the same ``hash`` in one process, in two processes and on two stores each rebuilt from one commit;
the packet is the same whether or not the semantic index answers; supplementary items of equal relevance (ties:
identical text at different paths) are ordered by ``path``, then ``id``, whatever order the retrieval gives them; and
the context-reproducibility check is never green on a stale store and red on a fresh one.

Red reasons, today: the packet keeps whatever order the retrieval gives tied items in (the ``ties-reversed``
stand-in changes the packet and its hash); semantic hits enter the supplementary block (the ``semantic-live``
stand-in changes the packet); the check measures a stale store as if fresh (green there, red after the reload).
The cases of one process, two processes and two stores pass today with the lexical route alone (W2-M330 asked for
them with an index): they hold what the change must keep.
"""

from __future__ import annotations

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


def _packet(api, project, mode=None, **extra):
    api.reset_log()
    env = api.env(mode=mode, **extra) if mode else None
    return api.gov(project.root, TICKET, env=env).packet


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


def test_tied_items_keep_one_order_whatever_order_the_retrieval_gives_them(retrieval_api, ties):
    expected = _packet(retrieval_api, ties, mode="log")
    reordered = _packet(retrieval_api, ties, mode="ties-reversed")
    calls = retrieval_api.calls()
    assert any(call["in"] != call["out"] for call in calls), \
        f"the fixture is wrong: the stand-in saw no tied items to reorder: {calls}"
    assert _tied(reordered) == sorted(_tied(reordered)), f"tied items follow the retrieval's order: {_tied(reordered)}"
    assert reordered[s.K_HASH] == expected[s.K_HASH], "the retrieval's order of tied items changes the packet's hash"


def test_the_packet_is_the_same_whether_or_not_the_semantic_route_answers(retrieval_api, ties):
    """No vector is built, so the semantic route is unavailable; the ``semantic-live`` stand-in makes it answer (one
    hit, the gulls note, which no lexical query finds). The packet and its hash do not change."""
    unavailable = _packet(retrieval_api, ties, mode="log")
    answering = _packet(retrieval_api, ties, mode="semantic-live", W204_SEMANTIC_PATH=SEMANTIC_ONLY)
    assert retrieval_api.calls(), "the fixture is wrong: the retrieval was not reached"
    assert answering[s.K_HASH] == unavailable[s.K_HASH], (
        "the packet changes when the semantic index answers: "
        f"{[item['path'] for item in answering[s.K_SUPPLEMENTARY]]} vs "
        f"{[item['path'] for item in unavailable[s.K_SUPPLEMENTARY]]}")


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
