"""The lite A10 gate: independent memory verification [CAP-44.f, CAP-44.h; DEC-741, DEC-722].

CAP-44.f (lite): "A10 ... by a fresh Independent Auditor session and recorded as its own stage; ... A10 checks
the A8 legacy memory extraction and retirement, the derived state rebuilt from git and the canary of each index
(CAP-55)". Every case copies the project the session fixture carried through A8 (straight after A6, as W2-24's
fixture adoption does) without its derived state, and runs ``gov adopt --lite --stage A10 --verdict <path>``
with the auditor's committed record. The indexes are built through the stand-in embedding endpoint; the
project holds the kernel's canary declarations, so each index's canary can hit.
"""

from __future__ import annotations

import pytest

import w2_52_support as gates

support = gates.support


@pytest.fixture(scope="module")
def a10_passed(after_a8, tmp_path_factory, interface, stand_in, vector_site):
    """One A10 run with the auditor's passing record, its derived state deleted first; the digest a rebuild
    from git gives at the commit the gate checks."""
    adoption = gates.copy_adoption(after_a8, tmp_path_factory.mktemp("a10-passed"), interface,
                                   endpoint=stand_in.host, site=vector_site)
    gates.write_gate_verdict(adoption, "A10")
    digest = gates.rebuild_digest(adoption)
    gates.remove_derived_state(adoption.project)
    before = {stage.record: support.at_head(adoption.project, stage.record) for stage in adoption.stages.values()}
    return adoption, gates.run_gate(adoption, "A10"), before, digest


# --------------------------------------------------------------------------
# Success 1 and 2
# --------------------------------------------------------------------------

def test_a10_passes_on_the_auditors_pass_and_is_recorded_as_its_own_stage(a10_passed, needs_vectors):
    """Success 1 [CAP-44.f]: A10 is a stage of its own, recorded next to the records of A0 to A8."""
    adoption, outcome, _, _ = a10_passed
    rel, front, _ = gates.assert_passed(outcome)
    assert front.get("stage") == "A10", f"{rel}: the record does not name its stage A10"
    others = {stage.record for stage in adoption.stages.values()}
    assert rel not in others, f"{rel} is the path of another stage's record"
    assert all(gates.posixpath.dirname(other) == gates.posixpath.dirname(rel) for other in others), \
        f"{rel} is not in the folder of the other stages' records: {sorted(others)}"


def test_a10_writes_over_no_other_stages_record(a10_passed, needs_vectors):
    adoption, outcome, before, _ = a10_passed
    gates.assert_passed(outcome)
    changed = [rel for rel, data in before.items() if support.at_head(adoption.project, rel) != data]
    assert not changed, f"A10 changed the records of other stages: {changed}"


def test_a10_record_names_the_a8_record_and_the_auditor(a10_passed, needs_vectors):
    """Success 2 [CAP-44.f]: the A8 legacy memory extraction and retirement, by a fresh auditor session."""
    adoption, outcome, _, _ = a10_passed
    rel, _, text = gates.assert_passed(outcome)
    assert adoption.stages["A8"].record in text, f"{rel} does not name the A8 record"
    assert gates.GATE_VERDICT_REL["A10"] in text, f"{rel} does not name the auditor's record"
    assert gates.GATE_SESSION["A10"] in text, f"{rel} does not name the auditor's session"


def test_a10_record_carries_the_digest_of_the_derived_state_rebuilt_from_git(a10_passed, needs_vectors):
    """Success 2 [CAP-44.f; CAP-20; CAP-44.h (9)]: the derived state was deleted before the gate; the gate's
    record carries the digest a rebuild from git gives at the commit it checked."""
    _, outcome, _, digest = a10_passed
    rel, _, text = gates.assert_passed(outcome)
    assert digest in text, f"{rel} does not carry the rebuild's digest {digest}"


def test_a10_record_names_the_canary_of_each_index(a10_passed, needs_vectors):
    """Success 2 [CAP-44.f; CAP-55]: the canary of each index (lexical, semantic)."""
    _, outcome, _, _ = a10_passed
    rel, _, text = gates.assert_passed(outcome)
    lowered = text.lower()
    assert "canar" in lowered, f"{rel} does not name the canaries"
    missing = [index for index in gates.INDEXES if index not in lowered]
    assert not missing, f"{rel} does not name the canary of the indexes {missing}"


def test_a10_record_names_what_stays_for_wave_3(a10_passed, needs_vectors):
    """Success 2 [CAP-44.k; CIT-P §3.2]: the A9 knowledge fabric, CAP-49's memory checks, CAP-47.a's role."""
    _, outcome, _, _ = a10_passed
    rel, _, text = gates.assert_passed(outcome)
    gates.assert_names_wave_3(rel, text, "A10")


def test_a10_record_gives_a_met_condition_a_verdict_can_carry(a10_passed, needs_vectors):
    """Success 3 [CAP-44.h (6), (9)]: conditions in W2-02's form, one naming A10, all 'met'."""
    _, outcome, _, _ = a10_passed
    rel, front, _ = gates.assert_passed(outcome)
    assert gates.lite_verdict(gates.conditions(front)) == "ADOPTED_HEALTHY", rel


# --------------------------------------------------------------------------
# Failure: a gate that fails writes a failing record
# --------------------------------------------------------------------------

def test_an_auditor_who_does_not_pass_the_memory_gets_a_failing_a10_record(a8_copy):
    """Failure [CAP-44.f]: the auditor's 'fail' (A7's cases hold the other values that are no pass)."""
    gates.write_gate_verdict(a8_copy, "A10", verdict="fail")
    outcome = gates.run_gate(a8_copy, "A10")
    rel, _, text = gates.assert_failing_record(outcome, gates.GATE_VERDICT_REL["A10"])
    gates.assert_names_wave_3(rel, text, "A10")


def test_a_lexical_canary_miss_fails_a10(a8_copy):
    """Failure [CAP-55]: the canary's phrase is no longer in the project, so the canary of the lexical index
    misses (FACET_UNAVAILABLE); the gate fails and names the index."""
    for name in gates.CANARY_FILES:
        support.git(a8_copy.project, "rm", "-q", f"{gates.PROJECT_CANARIES}/{name}")
    support.commit(a8_copy.project, "the canary declarations are gone")
    gates.write_gate_verdict(a8_copy, "A10")
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_failing_record(outcome, "lexical")


def test_a_semantic_canary_miss_fails_a10(a8_copy):
    """Failure [CAP-55]: the embedding endpoint is out of reach, so the semantic index holds no vector and its
    canary misses; the gate fails and names the index."""
    a8_copy.endpoint = None
    gates.write_gate_verdict(a8_copy, "A10")
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_failing_record(outcome, "semantic")


MEMORY_FILE = "legacy/memory/decisions/leg-001.md"
RETIRED = {"rule-file": ".cursorrules", "memory-store": MEMORY_FILE, "chat-database": support.CHAT_DB}


def _bring_back(adoption, rel):
    """The file, as the legacy project held it, back in the active tree, committed."""
    if rel == support.CHAT_DB:
        support.chat_database_bytes(adoption.project / rel)
    else:
        support.write(adoption.project, rel, support.base_files()[rel])
    support.commit(adoption.project, f"{rel} is back")


@pytest.mark.parametrize("kind", list(RETIRED))
def test_a_retirement_the_project_no_longer_holds_fails_a10(a8_copy, kind):
    """Failure [CAP-44.e, CAP-44.f]: after A8, a file A8 retired is back in the active tree; the auditor passes
    the records, which did not change. The gate checks the retirement and fails, naming the file."""
    rel = RETIRED[kind]
    assert support.at_head(a8_copy.project, rel) is None, f"the fixture: A8 left {rel} in the active tree"
    _bring_back(a8_copy, rel)
    gates.write_gate_verdict(a8_copy, "A10")
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_failing_record(outcome, rel)


def test_an_extraction_the_project_no_longer_holds_fails_a10(a8_copy):
    """Failure [CAP-44.e, CAP-44.f]: the chat database was retired because its knowledge is in a record; that
    record is gone after A8. The gate checks the extraction and fails, naming it."""
    support.git(a8_copy.project, "rm", "-q", gates.EXTRACTION_REL)
    support.commit(a8_copy.project, "the extraction record is gone")
    gates.write_gate_verdict(a8_copy, "A10")
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_failing_record(outcome, any_of=(gates.EXTRACTION_REL, gates.EXTRACTION_ID))


# --------------------------------------------------------------------------
# Failure: a missing record is a named failure; no auditor's pass
# --------------------------------------------------------------------------

def test_a_missing_a8_record_is_a_named_failure_of_a10(a8_copy):
    support.git(a8_copy.project, "rm", "-q", a8_copy.stages["A8"].record)
    support.commit(a8_copy.project, "the A8 record is gone")
    gates.write_gate_verdict(a8_copy, "A10", checked=[])
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_never_passes(outcome, "A8")


def test_an_auditors_record_that_does_not_cover_the_a8_record_never_passes(a8_copy):
    """The auditor's pass names the A6 record instead of the A8 record A10 checks."""
    gates.write_gate_verdict(a8_copy, "A10", checked=[a8_copy.stages["A6"].record])
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_never_passes(outcome, any_of=(a8_copy.stages["A8"].record, "A8"))


def test_an_auditors_record_about_another_a8_record_never_passes(a8_copy):
    rel = a8_copy.stages["A8"].record
    gates.write_gate_verdict(a8_copy, "A10", hashes={rel: "0" * 64})
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_never_passes(outcome, any_of=(rel, "A8", "sha256"))


def test_an_auditors_record_that_does_not_exist_never_passes(a8_copy):
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_never_passes(outcome, gates.GATE_VERDICT_REL["A10"])


def test_an_auditors_record_not_committed_by_the_independent_auditor_never_passes(a8_copy):
    gates.write_gate_verdict(a8_copy, "A10", role="engineer")
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_never_passes(outcome, gates.AUDITOR_ROLE)


def test_an_auditors_record_from_the_session_that_ran_a8_never_passes(a8_copy):
    gates.write_gate_verdict(a8_copy, "A10", session=gates.ADOPTER_SESSION)
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_never_passes(outcome, gates.ADOPTER_SESSION)


def test_the_a5_verdict_given_to_a10_never_passes(a8_copy):
    outcome = gates.run_gate(a8_copy, "A10", verdict_rel=support.VERDICT_REL)
    gates.assert_never_passes(outcome, any_of=(support.VERDICT_REL, "stage"))


def test_a10_with_an_unreadable_auditors_record_never_passes(a8_copy):
    """An unreadable record is never read as a pass (DEC-449)."""
    gates.write_gate_verdict(a8_copy, "A10", text="---\nid: AV-0010\nverdict: [pass\n---\n\nUnreadable.\n")
    outcome = gates.run_gate(a8_copy, "A10")
    gates.assert_never_passes(outcome, gates.GATE_VERDICT_REL["A10"])
