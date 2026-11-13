"""S4: the fault rule, as FRESH-80-1 section 3.5 states it (Interface 2, 12; S4's Verify: planted degraded search (one
restart then pass; two faults then stop); planted store change (stop, no restart)).

A search not answered as declared (a bundle not reranked by the shared service, a route missing, the pool's rerank
fallen back), or a store whose sha256 changed during the attempt, makes the attempt not whole. One restart is allowed
while no attempt has counted, after the ready check again; a second fault stops the audit (exit 2, ``STOPPED fault``).
The faults are planted by the question's text and its n-th asking (``by_occ``), so they are independent of the order of
unrelated calls: the attempt's question ``q12`` is asked once in ``attempt-1`` (its first asking) and once in
``attempt-2`` (its second).
"""

from __future__ import annotations

import pytest

import w2_171_scenario as S
import w2_171_world as W

SC = S.SCENARIOS["five"]
TARGET = "q12"


def question(docs, qid=TARGET):
    return docs[qid]["question"]


def fault_at(*occurrences, fault="rerank", qid=TARGET):
    """Edit: ``qid``'s question answered with ``fault`` at each of the given askings."""
    def edit(gov, docs):
        gov[question(docs, qid)]["by_occ"] = {str(n): {"fault": fault} for n in occurrences}
    return edit


def causes(world):
    return {p.parent.name: p.read_text().strip() for p in world.run_dir.glob("attempt-*/FAULT")}


@pytest.mark.parametrize("fault,cause", [("rerank", "degraded"), ("semantic_missing", "degraded"),
                                         ("pool", "degraded"), ("exit", "exit")])
def test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes(world, fault, cause):
    SC.install(world, gov_edit=fault_at(1, fault=fault))
    run = world.measure()
    assert run.code == 0, run
    assert causes(world) == {"attempt-1": cause}, causes(world)
    assert not (world.attempt_dir(1) / "DONE").exists() and (world.attempt_dir(2) / "DONE").is_file()
    assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-2"
    assert (world.run_dir / "control-1").is_dir() and (world.run_dir / "control-2").is_dir(), \
        "the ready check, the probe and a new control, again before the restart"
    expected = S.Expected(SC, world)
    assert [x for x in run.lines if x.startswith("RETRIEVAL")] == [expected.retrieval_line(2)], \
        "a faulted attempt's figures are never printed"
    states = [(e["n"], e["state"], e["cause"]) for e in world.events("attempt")]
    assert states == [(1, "start", None), (1, "fault", cause), (2, "start", None), (2, "done", None)], states
    assert [e["ok"] for e in world.events("ready")] == [True, True]
    assert world.events("counts")[0]["attempt"] == "attempt-2"
    assert not (world.run_dir / "STOPPED").exists()


def test_s4_a_route_that_is_not_available_is_a_degraded_search(world):
    SC.install(world, gov_edit=fault_at(1, fault="lexical"))
    run = world.measure()
    assert run.code == 0, run
    assert causes(world) == {"attempt-1": "degraded"}, causes(world)


def test_s4_a_second_fault_stops_the_audit_and_goes_to_the_owner(world):
    SC.install(world, gov_edit=fault_at(1, 2, fault="rerank"))
    run = world.measure()
    assert run.code == 2 and "STOPPED fault" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "fault"
    assert causes(world) == {"attempt-1": "degraded", "attempt-2": "degraded"}, causes(world)
    assert not (world.run_dir / "COUNTS").exists() and not list(world.run_dir.glob("attempt-3"))
    assert not [x for x in run.lines if x.startswith("RETRIEVAL")], run
    assert world.events("stopped")[0]["cause"] == "fault"
    assert (world.run_dir / "control-2").is_dir()


def test_s4_a_store_whose_sha256_changed_stops_without_a_restart_and_nothing_is_rebuilt(world):
    def edit(gov, docs):
        gov[question(docs)]["mutate_store"] = {"path": str(world.store), "data": "a page changed in the store"}
    SC.install(world, gov_edit=edit)
    declared_sha = W.sha_file(world.store)
    run = world.measure()
    assert run.code == 2 and "STOPPED store" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "store"
    assert causes(world) == {"attempt-1": "store"}
    assert not list(world.run_dir.glob("attempt-2")) and not list(world.run_dir.glob("control-2"))
    assert not (world.run_dir / "COUNTS").exists() and not [x for x in run.lines if x.startswith("RETRIEVAL")]
    store = world.events("store")
    assert len(store) == 1 and store[0]["n"] == 1 and store[0]["same"] is False, store
    assert store[0]["sha256"] == W.sha_file(world.store) != declared_sha
    assert world.events("attempt")[-1]["cause"] == "store" and world.events("stopped")[0]["cause"] == "store"
    names = {e["event"] for e in world.ledger()}
    assert not [n for n in names if "rebuild" in n or "build" in n], names
    assert {c["argv"][0] for c in world.gov_calls()} <= {"retrieve", "--version"}, "no rebuild call"
    assert (world.run_dir / "USED").is_file() and (world.run_dir / "DECLARATION.json").is_file()


@pytest.mark.parametrize("fault,why", [("rerank", "reranker"), ("lexical", "route"), ("semantic_missing", "route"),
                                       ("pool", "pool"), ("nolist", "no bundle"), ("exit", "exit")])
def test_s4_a_probe_not_answered_as_declared_is_notready_before_any_control(world, fault, why):
    def edit(gov, docs):
        gov[W.PROBE]["fault"] = fault
    SC.install(world, gov_edit=edit)
    run = world.measure()
    assert run.code == 2 and "STOPPED notready" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "notready"
    ready = world.events("ready")
    assert len(ready) == 1 and ready[0]["ok"] is False and ready[0]["why"] == why, ready
    searches = world.events("search")
    assert [e["phase"] for e in searches] == ["ready"], searches
    assert not list(world.run_dir.glob("control-*")) and not list(world.run_dir.glob("attempt-*"))
    assert world.claude_calls() == [] and (world.run_dir / "USED").is_file()


def test_s4_no_restart_into_the_same_outage(world):
    """Attempt 1 faults; before the restart the probe is asked again and is not answered as declared: ``STOPPED
    notready``, no ``control-2``, no ``attempt-2``, nothing spent."""
    def edit(gov, docs):
        fault_at(1)(gov, docs)
        gov[W.PROBE]["by_occ"] = {"2": {"fault": "rerank"}}
    SC.install(world, gov_edit=edit)
    run = world.measure()
    assert run.code == 2 and "STOPPED notready" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "notready"
    assert causes(world) == {"attempt-1": "degraded"}
    assert not list(world.run_dir.glob("attempt-2")) and not list(world.run_dir.glob("control-2"))
    assert [e["ok"] for e in world.events("ready")] == [True, False]
    assert not (world.run_dir / "COUNTS").exists() and not [x for x in run.lines if x.startswith("RETRIEVAL")]
    assert world.claude_calls() == []


def test_s4_the_control_runs_again_before_the_restart_and_may_stop_it(world):
    """The restart's new control out of range (hit@5 30 against 34): ``STOPPED control``, no ``attempt-2``."""
    def edit(gov, docs):
        fault_at(1)(gov, docs)
        for k in range(1, 5):
            gov[W.control_text(k)]["by_occ"] = {"2": {"calls": S.calls_for(None)}}
    SC.install(world, gov_edit=edit)
    run = world.measure()
    assert run.code == 2 and "STOPPED control" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "control"
    assert [(e["k"], e["hit5"], e["ok"]) for e in world.events("control")] == [(1, 34, True), (2, 30, False)]
    assert (world.run_dir / "control-2").is_dir() and not list(world.run_dir.glob("attempt-2"))
    assert causes(world) == {"attempt-1": "degraded"}


def test_s4_a_later_search_that_fails_in_judge_is_counted_and_never_an_attempt_fault(make_world):
    """Item 12 last sentence: ``judge``'s later search that fails or is degraded is counted, named by id, and gives an
    empty bundle; it faults no attempt (the attempt folders keep their ``DONE`` and gain no ``FAULT``)."""
    world = make_world("judged:five")
    assert world.events("search", phase="later") and not list(world.run_dir.glob("attempt-*/FAULT"))
    assert (world.attempt_dir(1) / "DONE").is_file() and not (world.run_dir / "STOPPED").exists()
