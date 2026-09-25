"""The class table equals ORCHESTRATOR_STATE.yaml mandatory_bridge_inputs.authority_classes plus the ladder
(node B5 acceptance check; ARCHITECTURE.md section 5.2's two build-failure conditions)."""
from govbridge.authority import classes


def test_class_table_matches_live_state_file():
    state_classes = classes.load_state_authority_classes()
    problems = classes.diff_against_state(state_classes)
    assert problems == []


def test_state_classes_are_exactly_seven_names():
    # ORCHESTRATOR_STATE.yaml mandatory_bridge_inputs.authority_classes: OWNER_DECISION plus the six non-ladder
    # classes that carry classificatory-force warnings.
    state_classes = classes.load_state_authority_classes()
    assert set(state_classes) == {
        "OWNER_DECISION", "OWNER_DIRECTION_TO_TEST", "HYPOTHESIS_TO_TEST", "HYPOTHESIS_RELEVANT_OBSERVATION",
        "EVIDENCE", "EVIDENCE_WITHDRAWN", "ORCHESTRATION_RECORD",
    }


def test_non_ladder_classes_never_admissible_in_a_or_d1():
    for spec in classes.NON_LADDER:
        assert spec.admissible_in_a is False
        assert spec.admissible_in_d1 is False


def test_ladder_ranks_are_1_through_7_unique():
    ranks = sorted(c.rank for c in classes.LADDER)
    assert ranks == [1, 2, 3, 4, 5, 6, 7]


def test_owner_decision_is_rank_1_and_admissible_everywhere():
    spec = classes.ALL_CLASSES["OWNER_DECISION"]
    assert spec.rank == 1
    assert spec.admissible_in_a is True
    assert spec.admissible_in_d1 is True


def test_derived_never_admissible_in_a():
    spec = classes.ALL_CLASSES["DERIVED"]
    assert spec.admissible_in_a is False


def test_orchestration_record_d1_is_adjudications_only():
    spec = classes.ALL_CLASSES["ORCHESTRATION_RECORD"]
    assert spec.admissible_in_d1 == classes.ADJUDICATIONS_ONLY


def test_map_lifecycle_word_precedence_supersedes_before_active():
    # "SUPERSEDED" must never read as ACTIVE just because a status string mentions being "in force" elsewhere.
    assert classes.map_lifecycle_word("SUPERSEDED by D-0002") == classes.LIFECYCLE_SUPERSEDED
    assert classes.map_lifecycle_word("IN FORCE for Phase 2") == classes.LIFECYCLE_ACTIVE
    assert classes.map_lifecycle_word("HISTORICAL_PHASE_1_OPERATOR_EVIDENCE") == classes.LIFECYCLE_HISTORICAL
    assert classes.map_lifecycle_word("retired as the Phase-1 target") == classes.LIFECYCLE_HISTORICAL
    assert classes.map_lifecycle_word("PROVISIONAL") == classes.LIFECYCLE_PROPOSED
    assert classes.map_lifecycle_word("something else entirely") == classes.LIFECYCLE_UNKNOWN
    assert classes.map_lifecycle_word(None) == classes.LIFECYCLE_UNKNOWN


def test_map_in_effect():
    assert classes.map_in_effect(True) == classes.LIFECYCLE_ACTIVE
    assert classes.map_in_effect(False) == classes.LIFECYCLE_PROPOSED
    assert classes.map_in_effect(None) is None
