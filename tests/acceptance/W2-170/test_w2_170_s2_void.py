"""S2 and F4: the drop and void rule (Interface 5, ``void``).

``python3 -m gov.memaudit void --sets-root <root> --audit <A>`` reads the highest ``XCHECK-r<n>.md``; every
question whose verdict is not exactly ``accept`` is moved to ``hidden/dropped/`` (never deleted); the kept count and
the scales are recomputed; ``VOID-COUNT`` (kept < 36) or ``VOID-DOMAIN`` (a domain under its scaled minimum) makes the
audit void: exit 2, no ``USED`` and no ``DECLARATION.json``.
"""

from __future__ import annotations

import pytest

import w2_170_world as W

THREE = {"q27": ("revise", "R6-SPAN-MISSES"), "q33": ("reject", "R1-WRONG")}      # and q34: no line
FIVE = dict(THREE, q28=("reject", "R9-DUPLICATE"), q35=("revise", "R2-ALL-KW"))


def _plant(world, specs=None, **notes):
    world.write_set(specs or W.clean_specs())
    originals = {p.name: p.read_bytes() for p in world.hidden.glob("q*.yaml")}
    world.write_notes(1)                                   # round 1: every question accepted
    world.write_notes(2, **notes)                          # round 2: the checker's second pass decides
    return originals


def _dropped_intact(world, originals, qids):
    found = sorted(p.stem for p in world.dropped.glob("*.yaml")) if world.dropped.exists() else []
    assert found == sorted(qids), found
    for qid in qids:
        assert (world.dropped / f"{qid}.yaml").read_bytes() == originals[f"{qid}.yaml"]
    kept = sorted(p.name for p in world.hidden.glob("*.yaml"))
    assert len(kept) + len(found) == len(originals)             # nothing deleted
    for name in kept:
        assert (world.hidden / name).read_bytes() == originals[name]


def _not_declared(world):
    assert not (world.run_dir / "USED").exists()
    assert not (world.run_dir / "DECLARATION.json").exists()


def test_s2_three_drops_go_on_with_37_kept_and_the_scales_recomputed(world):
    originals = _plant(world, verdicts=THREE, missing=("q34",))
    run = world.void()
    assert run.code == 0, run
    assert "DROPS: kept 37 dropped 3" in run.lines, run
    _dropped_intact(world, originals, ["q27", "q33", "q34"])
    doc = world.json_of("DROPS.json")
    assert all(key in doc for key in W.DROPS_KEYS), doc
    assert (doc["kept"], doc["dropped"], doc["void"], doc["notes_round"]) == (37, 3, None, 2)
    assert doc["by_code"] == {"R6-SPAN-MISSES": 1, "R1-WRONG": 1, "NOLINE": 1}
    domains, subsystems = W.kept_counts(W.without(W.clean_specs(), "q27", "q33", "q34"))
    assert {d: doc["domains"].get(d, 0) for d in W.DOMAINS} == domains, doc["domains"]
    assert {s: doc["subsystems"].get(s, 0) for s in W.SUBSYSTEMS} == subsystems, doc["subsystems"]
    assert doc["subsystem_over"] == []
    assert doc["set_digest"] == W.set_digest(world.hidden)
    events = [e["event"] for e in world.ledger()]
    assert "drop" in events and "void" not in events, events
    _not_declared(world)


def test_f4_five_drops_void_the_audit_with_no_used_and_no_declaration(world):
    originals = _plant(world, verdicts=FIVE, missing=("q34",))
    run = world.void()
    assert run.code == 2, run
    assert "VOID VOID-COUNT kept 35 dropped 5" in run.lines, run
    _dropped_intact(world, originals, ["q27", "q28", "q33", "q34", "q35"])
    doc = world.json_of("DROPS.json")
    assert (doc["kept"], doc["dropped"], doc["void"]) == (35, 5, "VOID-COUNT")
    events = [e["event"] for e in world.ledger()]
    assert "drop" in events and "void" in events and events.index("drop") < events.index("void"), events
    _not_declared(world)


def test_s2_a_drop_that_leaves_a_domain_at_3_voids_the_audit(world):
    originals = _plant(world, verdicts={"q08": ("reject", "R1-WRONG")})
    run = world.void()
    assert run.code == 2, run
    assert "VOID VOID-DOMAIN kept 39 dropped 1" in run.lines, run
    _dropped_intact(world, originals, ["q08"])
    doc = world.json_of("DROPS.json")
    assert doc["void"] == "VOID-DOMAIN" and doc["domains"].get("contract") == 3
    _not_declared(world)


def test_s2_void_count_is_reported_first_when_both_causes_hold(world):
    _plant(world, verdicts=dict(FIVE, q08=("reject", "R1-WRONG")), missing=("q34",))
    run = world.void()
    assert run.code == 2, run
    assert "VOID VOID-COUNT kept 34 dropped 6" in run.lines, run
    assert world.json_of("DROPS.json")["void"] == "VOID-COUNT"
    _not_declared(world)


def test_s2_a_subsystem_over_its_scaled_maximum_after_drops_is_recorded_and_does_not_void(world):
    specs = W.clean_specs()
    for qid, path in zip(["q23", "q24", "q25", "q26", "q27", "q28"], W.SPARE_RETRIEVAL):
        W.repoint(specs, qid, path)                      # retrieval 10: allowed at 40, over at 39
    _plant(world, specs, verdicts={"q36": ("reject", "R11-MOVES")})
    run = world.void()
    assert run.code == 0, run
    doc = world.json_of("DROPS.json")
    assert doc["void"] is None and doc["kept"] == 39
    assert "retrieval" in W.json.dumps(doc["subsystem_over"]), doc["subsystem_over"]


def test_s2_the_highest_notes_round_is_the_one_read(world):
    world.write_set(W.clean_specs())
    world.write_notes(1, THREE, missing=("q34",))           # round 1 dropped three
    world.write_notes(2)                                    # round 2 accepts all: it decides
    run = world.void()
    assert run.code == 0, run
    doc = world.json_of("DROPS.json")
    assert (doc["kept"], doc["dropped"], doc["notes_round"]) == (40, 0, 2)


def test_s2_the_highest_round_is_numeric_not_by_name(world):
    world.write_set(W.clean_specs())
    world.write_notes(2)
    world.write_notes(10, THREE, missing=("q34",))
    run = world.void()
    assert run.code == 0, run
    doc = world.json_of("DROPS.json")
    assert (doc["kept"], doc["dropped"], doc["notes_round"]) == (37, 3, 10)


def test_s2_a_line_that_does_not_fit_or_is_not_exactly_accept_is_dropped(world):
    originals = _plant(world, raw={"q29": "q29 accept the line has no fields",
                                   "q35": "q35 | Accept | - | also: none | a verdict in another case."})
    run = world.void()
    assert run.code == 0, run
    _dropped_intact(world, originals, ["q29", "q35"])
    doc = world.json_of("DROPS.json")
    assert doc["kept"] == 38 and doc["by_code"].get("UNFIT") == 1, doc


def test_s2_dr_notes_refuses_when_no_notes_exist_and_moves_nothing(world):
    world.write_set(W.clean_specs())
    before = W.snapshot(world.set_dir)
    run = world.void()
    assert run.code == 1 and "DR-NOTES" in run.out, run
    assert W.snapshot(world.set_dir) == before                  # nothing moved
    assert not (world.run_dir / "DROPS.json").exists()


def test_s2_dr_notes_refuses_notes_without_a_questions_section(world):
    world.write_set(W.clean_specs())
    world.write_notes(2, THREE, missing=("q34",), questions_section=False)
    run = world.void()
    assert run.code == 1 and "DR-NOTES" in run.out, run
    assert not world.dropped.exists() or not any(world.dropped.iterdir())
    assert not (world.run_dir / "DROPS.json").exists()


def test_s2_dr_done_refuses_a_second_void(world):
    _plant(world, verdicts=THREE, missing=("q34",))
    assert world.void().code == 0
    world.write_notes(3, FIVE, missing=("q34",))             # later notes cannot drop more once DROPS.json exists
    before = W.snapshot(world.set_dir)
    drops = (world.run_dir / "DROPS.json").read_bytes()
    run = world.void()
    assert run.code == 1 and "DR-DONE" in run.out, run
    assert W.snapshot(world.set_dir) == before                  # nothing moved
    assert (world.run_dir / "DROPS.json").read_bytes() == drops


def test_s2_void_writes_no_used_and_no_declaration_even_when_it_goes_on(world):
    _plant(world)
    run = world.void()
    assert run.code == 0, run
    assert "DROPS: kept 40 dropped 0" in run.lines, run
    _not_declared(world)


@pytest.mark.parametrize("drops", [3, 5])
def test_f4_no_dropped_question_is_deleted(world, drops):
    verdicts = THREE if drops == 3 else FIVE
    originals = _plant(world, verdicts=verdicts, missing=("q34",))
    assert world.void().code == (0 if drops == 3 else 2)
    assert len(list(world.dropped.glob("*.yaml"))) == drops
    every = {p.name for p in world.hidden.glob("*.yaml")} | {p.name for p in world.dropped.glob("*.yaml")}
    assert every == set(originals)
