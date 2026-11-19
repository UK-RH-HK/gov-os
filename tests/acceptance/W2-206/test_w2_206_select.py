"""A6 S2 (L2 §3 A6): ``gov queue <T>... --select`` prints the selection and runs nothing.

Success line 2 (A6 S2) and the ``--select`` part of failure line 1 (A6 F1). README, "The planted runs": dry.
"""

from __future__ import annotations

import pytest

import w2_206_support as support
from w2_206_support import A, B, kit


@pytest.fixture(scope="module")
def dry(landing):
    return landing("dry")


def _selection(dry, name):
    """The object a ``--select`` step printed (on the base the flag is unknown: exit 2, nothing on stdout)."""
    run = dry.extra["steps"][name]["run"]
    assert run["code"] == 0, f"gov queue --select exited {run['code']}, not 0\n{kit.describe(run)}"
    chosen = support.one_object(run["stdout"])
    assert chosen is not None, f"stdout is not one JSON object\n{kit.describe(run)}"
    return chosen


# -- success line 2 (A6 S2) ---------------------------------------------------------------------------------------

def test_select_prints_one_ticket_s_selection_as_gov_close_select_does_on_the_same_tree(dry):
    chosen = _selection(dry, "select_one")
    reference = dry.extra["reference"][A.id]
    assert chosen.get("ticket") == A.id and chosen.get("tickets") == [A.id], f"the object names {chosen}"
    for key in ("ticket", "suites", "pytest_options"):
        assert chosen.get(key) == reference[key], f"{key}: {chosen.get(key)!r} is not gov close --select's " \
                                                  f"{reference[key]!r}"


def test_select_of_two_tickets_prints_the_union_of_their_selections(dry):
    chosen = _selection(dry, "select_two")
    assert "ticket" not in chosen and chosen.get("tickets") == [A.id, B.id], f"the object names {chosen}"
    reference = dry.extra["reference"]
    union = sorted(set(reference[A.id]["suites"]) | set(reference[B.id]["suites"]))
    assert sorted(chosen.get("suites") or []) == union, f"suites {chosen.get('suites')!r} are not the union {union}"
    assert len(chosen["suites"]) == len(set(chosen["suites"])), f"a suite is named twice: {chosen['suites']}"
    assert chosen.get("pytest_options") == reference[A.id]["pytest_options"]


def test_select_runs_no_test_and_leaves_the_integration_branch_where_it_was(dry):
    for name in ("select_one", "select_two"):
        _selection(dry, name)
        taken = dry.extra["steps"][name]
        assert taken["after"]["told"] == taken["before"]["told"], \
            f"{name}: a planted test ran: {taken['before']['told']} -> {taken['after']['told']}"
        assert kit.heads(taken["after"]) == kit.heads(taken["before"]), f"{name}: a branch moved"


def test_a_ticket_changing_a_path_the_test_map_does_not_map_is_selection_refused_on_stderr_with_exit_2(dry):
    taken = dry.extra["steps"]["select_unmapped"]
    run = taken["run"]
    assert "SELECTION_REFUSED" in run["stderr"], f"stderr does not name SELECTION_REFUSED\n{kit.describe(run)}"
    assert run["code"] == support.EXIT_REFUSED_SELECTION, f"exit {run['code']}, not 2\n{kit.describe(run)}"
    printed = support.one_object(run["stdout"]) or {}
    assert "suites" not in printed, f"a refused selection is printed on stdout\n{kit.describe(run)}"
    assert support.UNMAPPED in run["stderr"], f"the refusal does not name the unmapped path\n{kit.describe(run)}"
    assert taken["after"]["told"] == taken["before"]["told"], "a planted test ran"
    support.moved_nothing(taken)


# -- failure line 1 (A6 F1), --select -----------------------------------------------------------------------------

def test_select_leaves_the_root_clean_and_creates_no_ref_no_commit_and_no_record(dry):
    for name in ("select_one", "select_two"):
        _selection(dry, name)
        taken = dry.extra["steps"][name]
        support.moved_nothing(taken)
        after = taken["after"]
        assert "refs/gov-queue/land" not in after["refs"] and "refs/gov-close/land" not in after["refs"]
        if after["clone_head"] is not None:  # a warm clone, where --select makes one, is left at the base
            assert after["clone_head"] == dry.old_head and after["clone_status"] == "", \
                f"{name}: the warm clone is at {after['clone_head']}, status {after['clone_status']!r}"
