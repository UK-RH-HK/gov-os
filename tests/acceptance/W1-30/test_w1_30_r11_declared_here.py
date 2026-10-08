"""This repository declares its own cases that cannot hold under load (DEC-527, DEC-372, DEC-531).

The list is ``tests/acceptance/serial-only.txt`` (``support.SERIAL_ONLY_REL``), in the form the cases of
``test_w1_30_r11_parallel_runs.py`` hold for any project. A close or a regression of this repository sets
exactly the cases it names apart.

What is declared: the cases the measuring agent's report names (DEC-514; the README, round 11, lists them)
and what reading the suites confirmed of the same four kinds: a time bound, a real
model or daemon, a live session, a race by design. A case is not declared merely because it is slow.

The cases read the list and the test files as text and ask the test runner only to collect (W1-16); no
declared case is run here.
"""

import subprocess
import sys

import pytest

import w1_30_support as support

LIST = support.REPO_ROOT / support.SERIAL_ONLY_REL
ACCEPTANCE = "tests/acceptance"

# The report's table of the suites it timed: the node id, and how many parameter sets it has.
NAMED_IN_THE_TIMED_SUITES = {
    f"{ACCEPTANCE}/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms": 5,
    f"{ACCEPTANCE}/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook": 9,
    f"{ACCEPTANCE}/W1-05/test_w1_05_switch_over_record.py::"
    "test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over": 1,
    f"{ACCEPTANCE}/W1-50/test_w1_50_review_of_the_symmetric_rule.py::"
    "test_read_merge_answers_for_a_merge_commit_with_very_many_parents_in_time_and_never_calls_the_undone_test_brought": 1,
    f"{ACCEPTANCE}/W1-50/test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays": 1,
    f"{ACCEPTANCE}/W1-50/test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path": 1,
}

# The report's list of the suites it did not time in parallel. A file alone means every case of the file.
NAMED_IN_THE_OTHER_SUITES = (
    f"{ACCEPTANCE}/W1-25/test_w1_25_live_session.py",
    f"{ACCEPTANCE}/W1-46/test_w1_46_live_sessions.py",
    f"{ACCEPTANCE}/W1-49/test_w1_49_live_session.py",
    f"{ACCEPTANCE}/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95",
    f"{ACCEPTANCE}/W1-18/test_w1_18_deadline.py::test_a_daemon_that_never_becomes_healthy_is_given_up_at_the_deadline",
    f"{ACCEPTANCE}/W1-18/test_w1_18_deadline.py::test_an_endpoint_that_accepts_and_never_answers_does_not_hang_the_call",
    f"{ACCEPTANCE}/W1-07/test_w1_07_help.py::test_help_answers_in_under_300_ms",
    f"{ACCEPTANCE}/W1-10/test_w1_10_dev_tier.py::test_a_full_load_of_a_dev_tier_takes_less_than_5_seconds",
    f"{ACCEPTANCE}/W1-17/test_w1_17_dev_tier.py::"
    "test_one_changed_file_is_re_indexed_by_the_next_retrieval_within_the_bound",
    f"{ACCEPTANCE}/W1-20/test_w1_20_code.py",
    f"{ACCEPTANCE}/W1-19/test_w1_19_real_models.py",
    f"{ACCEPTANCE}/W1-21/test_w1_21_dev_tier.py",
    f"{ACCEPTANCE}/W1-09/test_w1_09_review.py::"
    "test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim",
    f"{ACCEPTANCE}/W1-09/test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder",
)

# Cases of the same files that assert no time bound and start nothing real: they stay in the parallel run.
NOT_DECLARED = (
    f"{ACCEPTANCE}/W1-07/test_w1_07_help.py::test_help_prints_usage_and_ends_with_exit_code_0",
    f"{ACCEPTANCE}/W1-18/test_w1_18_deadline.py::test_the_default_deadline_is_20_seconds",
    f"{ACCEPTANCE}/W1-10/test_w1_10_dev_tier.py::test_a_dev_tier_loads_to_the_same_digest_twice",
    f"{ACCEPTANCE}/W1-05/test_w1_05_switch_over_record.py::test_the_operator_diff_check_is_recorded_as_retired",
    f"{ACCEPTANCE}/W1-09/test_w1_09_claims.py::test_a_released_ticket_can_be_claimed_again",
    f"{ACCEPTANCE}/W1-02/test_w1_02_guard_hook.py",
    f"{ACCEPTANCE}/W1-30/test_w1_30_close.py",
)

W1_16 = f"{ACCEPTANCE}/W1-16"
W1_16_MARKER = "local_only"   # W1-16's own marker of a case that runs the codebase-memory daemon (its README)


def _entries():
    assert LIST.is_file(), f"this repository has no {support.SERIAL_ONLY_REL}"
    return support.serial_only_entries(LIST)


def _names():
    return [entry for entry, _ in _entries()]


def _collected(*args):
    """The node ids the test runner collects for ``args`` in this repository, without ``PYTHONPATH``."""
    import os

    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    done = subprocess.run([sys.executable, "-m", "pytest", *args, "--collect-only", "-q", "-p", "no:cacheprovider"],
                          cwd=str(support.REPO_ROOT), env=env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    assert done.returncode in (0, 5), f"the test runner did not collect {args}:\n{done.stdout}\n{done.stderr}"
    return [line.strip() for line in done.stdout.splitlines() if "::" in line]


@pytest.mark.parametrize("node", sorted(NAMED_IN_THE_TIMED_SUITES))
def test_every_case_the_report_names_in_the_suites_it_timed_is_declared(node):
    assert support.declared_serial_only(node, _names()), f"{node} is not declared in {support.SERIAL_ONLY_REL}"
    collected = [found for found in _collected(node) if found.split("[")[0] == node]
    assert len(collected) == NAMED_IN_THE_TIMED_SUITES[node], \
        f"{node} has {len(collected)} parameter sets, the report names {NAMED_IN_THE_TIMED_SUITES[node]}"
    assert all(support.declared_serial_only(found, _names()) for found in collected), \
        f"a parameter set of {node} is not declared"


@pytest.mark.parametrize("node", NAMED_IN_THE_OTHER_SUITES)
def test_every_case_the_report_names_in_the_other_suites_is_declared(node):
    assert support.declared_serial_only(node, _names()), \
        f"{node} is not declared in {support.SERIAL_ONLY_REL}"


def test_every_case_of_w1_16_that_runs_the_daemon_is_declared_and_no_other_of_its_cases():
    every = _collected(W1_16)
    marked = set(_collected(W1_16, "-m", W1_16_MARKER))
    assert marked and len(marked) < len(every), f"the fixture is wrong: {len(marked)} of {len(every)} cases are marked"
    names = _names()
    missing = sorted(node for node in marked if not support.declared_serial_only(node, names))
    assert not missing, f"cases of W1-16 that run the daemon are not declared: {missing}"
    beyond = sorted(node for node in every if node not in marked and support.declared_serial_only(node, names))
    assert not beyond, f"cases of W1-16 that run no daemon are declared: {beyond}"


@pytest.mark.parametrize("node", NOT_DECLARED)
def test_a_case_that_asserts_no_time_bound_and_starts_nothing_real_is_not_declared(node):
    assert node not in _names() and not support.declared_serial_only(node, _names()), \
        f"{node} is declared although it is none of the four kinds"


def test_every_entry_names_cases_that_exist_and_says_its_kind():
    """An entry that names nothing would set nothing apart and say that it does. Each entry is a file of this
    repository under ``tests/``, with the function it names defined in it, named once, and its comment begins
    with one of the four kinds."""
    entries = _entries()
    assert entries, f"{support.SERIAL_ONLY_REL} declares nothing"
    names = [entry for entry, _ in entries]
    assert len(set(names)) == len(names), f"an entry is there twice: {sorted(n for n in names if names.count(n) > 1)}"
    for entry, comment in entries:
        rel, _, function = entry.partition("::")
        path = support.REPO_ROOT / rel
        assert rel.startswith("tests/") and rel.endswith(".py") and path.is_file(), \
            f"the entry {entry!r} names no test file of this repository"
        if function:
            assert "[" not in function and "::" not in function, \
                f"the entry {entry!r} is neither a file nor a function of a file"
            assert f"\ndef {function}(" in path.read_text(encoding="utf-8"), \
                f"the entry {entry!r} names a function that {rel} does not define"
            assert rel not in names, \
                f"the entry {entry!r} is named by the entry of its whole file too"
        kind = comment.split(":")[0].strip()
        assert kind in support.SERIAL_ONLY_KINDS, \
            f"the entry {entry!r} does not say which of {support.SERIAL_ONLY_KINDS} it is: {comment!r}"
