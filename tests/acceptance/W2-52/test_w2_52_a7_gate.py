"""The lite A7 gate: independent migration verification [CAP-44.f, CAP-44.h; DEC-741, DEC-722].

CAP-44.f (lite): "A7 ... by a fresh Independent Auditor session and recorded as its own stage; A7 checks the A6
migration against the A3 path map and the A4 plan reviewed at A5". Every case copies the project the session
fixture carried through A6 (three move batches done) and runs ``gov adopt --lite --stage A7 --verdict <path>``
with the auditor's committed record (the A5 precedent). What a pass, a failing record and a refusal are is in
the README ("The interface the cases hold").
"""

from __future__ import annotations

import pytest

import w2_52_support as gates

support = gates.support

GUIDE, GUIDE_TARGET = support.GUIDE, support.GUIDE_TARGET
NOTES, NOTES_TARGET = support.NOTES, support.NOTES_TARGET
ALTERED_TARGET = "docs/elsewhere/guide.md"


@pytest.fixture(scope="module")
def a7_passed(after_a6, tmp_path_factory, interface, stand_in, vector_site):
    """One A7 run on a copy of the project after A6, with the auditor's passing record."""
    adoption = gates.copy_adoption(after_a6, tmp_path_factory.mktemp("a7-passed"), interface,
                                   endpoint=stand_in.host, site=vector_site)
    gates.write_gate_verdict(adoption, "A7")
    before = {stage.record: support.at_head(adoption.project, stage.record) for stage in adoption.stages.values()}
    return adoption, gates.run_gate(adoption, "A7"), before


# --------------------------------------------------------------------------
# Success 1 and 2: the gate runs, is its own stage, checks what v4.2 names, names what stays for Wave 3
# --------------------------------------------------------------------------

def test_a7_passes_on_the_auditors_pass_and_is_recorded_as_its_own_stage(a7_passed):
    """Success 1 [CAP-44.f]: A7 is a stage of its own; its record lies in the adoption run's folder, next to
    the records of A0 to A6, at a path of its own."""
    adoption, outcome, _ = a7_passed
    rel, front, _ = gates.assert_passed(outcome)
    assert front.get("stage") == "A7", f"{rel}: the record does not name its stage A7"
    others = {stage.record for stage in adoption.stages.values()}
    assert rel not in others, f"{rel} is the path of another stage's record"
    assert all(gates.posixpath.dirname(other) == gates.posixpath.dirname(rel) for other in others), \
        f"{rel} is not in the folder of the other stages' records: {sorted(others)}"


def test_a7_writes_over_no_other_stages_record(a7_passed):
    """Success 1: every record of A0 to A6 is at HEAD as it was before A7."""
    adoption, outcome, before = a7_passed
    gates.assert_passed(outcome)
    changed = [rel for rel, data in before.items() if support.at_head(adoption.project, rel) != data]
    assert not changed, f"A7 changed the records of other stages: {changed}"


def test_a7_record_names_what_it_checked(a7_passed):
    """Success 2 [CAP-44.f]: the A6 migration, against the A3 path map and the A4 plan reviewed at A5, by a
    fresh Independent Auditor session: the record names the four records, the auditor's record and its session."""
    adoption, outcome, _ = a7_passed
    rel, _, text = gates.assert_passed(outcome)
    for stage in gates.GATE_CHECKS["A7"]:
        assert adoption.stages[stage].record in text, \
            f"{rel} does not name the {stage} record {adoption.stages[stage].record}"
    assert gates.GATE_VERDICT_REL["A7"] in text, f"{rel} does not name the auditor's record"
    assert gates.GATE_SESSION["A7"] in text, f"{rel} does not name the auditor's session"


def test_a7_record_names_what_stays_for_wave_3(a7_passed):
    """Success 2 [CAP-44.k; CIT-P §3.2]: a separate verifier role under CAP-47.a stays for Wave 3."""
    _, outcome, _ = a7_passed
    rel, _, text = gates.assert_passed(outcome)
    gates.assert_names_wave_3(rel, text, "A7")


def test_a7_record_gives_a_met_condition_a_verdict_can_carry(a7_passed):
    """Success 3 [CAP-44.h (4)]: the record gives a condition in W2-02's form (name, source item, state), its
    name naming A7, its source CAP-44.f or CAP-44.h, its state 'met'."""
    _, outcome, _ = a7_passed
    rel, front, _ = gates.assert_passed(outcome)
    found = gates.conditions(front)
    assert gates.lite_verdict(found) == "ADOPTED_HEALTHY", f"{rel}: {found}"


# --------------------------------------------------------------------------
# Failure: a gate that fails writes a failing record
# --------------------------------------------------------------------------

@pytest.mark.parametrize("verdict", ["fail", "inconclusive", "pass_with_findings"])
def test_an_auditor_who_does_not_pass_the_migration_gets_a_failing_a7_record(a6_copy, verdict):
    """Failure [CAP-44.f]: only 'pass' passes (DEC-490); the gate fails and its record says so, names the
    auditor's record, and still names what stays for Wave 3."""
    gates.write_gate_verdict(a6_copy, "A7", verdict=verdict)
    outcome = gates.run_gate(a6_copy, "A7")
    rel, _, text = gates.assert_failing_record(outcome, gates.GATE_VERDICT_REL["A7"])
    gates.assert_names_wave_3(rel, text, "A7")


def _moved_back(adoption):
    support.git(adoption.project, "mv", GUIDE_TARGET, GUIDE)
    support.commit(adoption.project, "the guide is back where it was")
    return (GUIDE, GUIDE_TARGET)


def _target_gone(adoption):
    support.git(adoption.project, "rm", "-q", NOTES_TARGET)
    support.commit(adoption.project, "the notes are gone")
    return (NOTES, NOTES_TARGET)


@pytest.mark.parametrize("undo", [_moved_back, _target_gone], ids=["moved-back", "target-gone"])
def test_a_migration_the_project_no_longer_holds_fails_a7(a6_copy, undo):
    """Failure [CAP-44.f]: A7 checks the A6 migration against the A3 path map. After A6, a planned move is
    undone; the auditor passes the records, which did not change. The gate checks the project and fails."""
    names = undo(a6_copy)
    gates.write_gate_verdict(a6_copy, "A7")
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_failing_record(outcome, any_of=names)


def test_a_path_map_changed_after_its_a5_review_fails_a7(a6_copy):
    """Failure [CAP-44.f, CAP-44.c]: the A3 path map is no longer the one A5 reviewed (its hash is not the A5
    record's ``path_map_hash``). The auditor's record names the path map as it now stands."""
    path_map = a6_copy.stages["A3"].record
    text = (a6_copy.project / path_map).read_text(encoding="utf-8")
    support.write(a6_copy.project, path_map, text + "\nA line added after the A5 review.\n")
    support.commit(a6_copy.project, "the path map, changed after A5")
    gates.write_gate_verdict(a6_copy, "A7")
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_failing_record(outcome, any_of=(path_map, a6_copy.stages["A5"].record, "path_map_hash"))


def test_a_plan_that_is_not_the_one_executed_fails_a7(a6_copy):
    """Failure [CAP-44.f]: the A4 plan, changed after A6, takes the guide elsewhere than A6 took it. A7 checks
    the migration against the plan reviewed at A5, and fails."""
    plan = a6_copy.stages["A4"].record
    text = (a6_copy.project / plan).read_text(encoding="utf-8")
    front = support.frontmatter(text, plan)
    for batch in front["batches"]:
        for item in batch["artefacts"]:
            if item.get("path") == GUIDE:
                item["target"] = ALTERED_TARGET
    changed = support.replaced(front, {GUIDE_TARGET: ALTERED_TARGET})
    support.write(a6_copy.project, plan, support.with_frontmatter(text, changed))
    assert ALTERED_TARGET in (a6_copy.project / plan).read_text(encoding="utf-8"), "the fixture did not change it"
    support.commit(a6_copy.project, "the plan, changed after A6")
    gates.write_gate_verdict(a6_copy, "A7")
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_failing_record(outcome, any_of=(ALTERED_TARGET, plan, GUIDE))


# --------------------------------------------------------------------------
# Failure: a missing record is a named failure; what the gate checks is absent; no auditor's pass
# --------------------------------------------------------------------------

def test_a_missing_a6_record_is_a_named_failure_of_a7(a6_copy):
    """Failure ("a missing record is a named failure, never healthy"): the A6 record is gone; A7 never passes
    and names A6."""
    support.git(a6_copy.project, "rm", "-q", a6_copy.stages["A6"].record)
    support.commit(a6_copy.project, "the A6 record is gone")
    gates.write_gate_verdict(a6_copy, "A7", checked=[a6_copy.stages[s].record for s in ("A3", "A4", "A5")])
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_never_passes(outcome, "A6")


@pytest.mark.parametrize("left_out", ["A3", "A4", "A5", "A6"])
def test_an_auditors_record_that_does_not_cover_a_checked_record_never_passes(a6_copy, left_out):
    """Failure [CAP-44.f]: the auditor's pass must cover each record v4.2 names for A7 (the A6 migration, the A3
    path map, the A4 plan, the A5 review); a pass that leaves one out is no pass of the gate."""
    checked = [a6_copy.stages[s].record for s in gates.GATE_CHECKS["A7"] if s != left_out]
    gates.write_gate_verdict(a6_copy, "A7", checked=checked)
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_never_passes(outcome, any_of=(a6_copy.stages[left_out].record, left_out))


def test_an_auditors_record_about_another_a6_record_never_passes(a6_copy):
    """Failure: the hash the auditor gives for the A6 record is not the A6 record's (the A5 precedent)."""
    rel = a6_copy.stages["A6"].record
    gates.write_gate_verdict(a6_copy, "A7", hashes={rel: "0" * 64})
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_never_passes(outcome, any_of=(rel, "A6", "sha256"))


def test_an_auditors_record_that_does_not_exist_never_passes(a6_copy):
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_never_passes(outcome, gates.GATE_VERDICT_REL["A7"])


def test_an_auditors_record_written_and_not_committed_never_passes(a6_copy):
    """The auditor's record is a committed record (the A5 precedent); one only written is none."""
    rel = gates.write_gate_verdict(a6_copy, "A7", commit=False)
    outcome = gates.run_gate(a6_copy, "A7", untracked=(rel,))
    gates.assert_never_passes(outcome, rel)


@pytest.mark.parametrize("role", ["engineer", "orchestrator", None], ids=["engineer", "orchestrator", "no-role"])
def test_an_auditors_record_not_committed_by_the_independent_auditor_never_passes(a6_copy, role):
    """CAP-44.f: by an Independent Auditor session; read from the commit's ``Role`` trailer (DEC-454)."""
    gates.write_gate_verdict(a6_copy, "A7", role=role)
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_never_passes(outcome, gates.AUDITOR_ROLE)


def test_an_auditors_record_from_the_session_that_ran_the_stages_never_passes(a6_copy):
    """CAP-44.f: a fresh session, not the one that ran A0 to A6."""
    gates.write_gate_verdict(a6_copy, "A7", session=gates.ADOPTER_SESSION)
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_never_passes(outcome, gates.ADOPTER_SESSION)


def test_the_a5_verdict_given_to_a7_never_passes(a6_copy):
    """The auditor's record is for A7: the A5 review of the path map is another stage's verdict."""
    outcome = gates.run_gate(a6_copy, "A7", verdict_rel=support.VERDICT_REL)
    gates.assert_never_passes(outcome, any_of=(support.VERDICT_REL, "stage"))


def _broken_yaml(adoption):
    return "---\nid: AV-0007\nverdict: [pass\n  stage: }\n---\n\nA record nobody can read.\n"


def _no_frontmatter(adoption):
    return "# The A7 gate\n\nverdict: pass\n"


def _no_verdict(adoption):
    return gates.gate_verdict_text(adoption, "A7", verdict=None)


@pytest.mark.parametrize("text", [_broken_yaml, _no_frontmatter, _no_verdict],
                         ids=["broken-yaml", "no-frontmatter", "no-verdict"])
def test_an_auditors_record_that_cannot_be_read_never_passes(a6_copy, text):
    """An unreadable or partial record is never read as a pass (DEC-449)."""
    gates.write_gate_verdict(a6_copy, "A7", text=text(a6_copy))
    outcome = gates.run_gate(a6_copy, "A7")
    gates.assert_never_passes(outcome, gates.GATE_VERDICT_REL["A7"])


def test_the_fixture_auditors_record_is_readable(a6_copy):
    """A guard on the fixture itself (green): the auditor's record the cases write is a readable record."""
    rel = gates.write_gate_verdict(a6_copy, "A7")
    front = support.frontmatter((a6_copy.project / rel).read_text(encoding="utf-8"), rel)
    assert front["stage"] == "A7" and front["verdict"] == "pass" and len(front["checked"]) == 4
    assert all(item["sha256"] == gates.record_hash(a6_copy.project, item["record"]) for item in front["checked"])
