"""This repository declares its own cases that cannot hold under load, and where each one runs (DEC-527, DEC-372,
DEC-531; reworked by W2-57 under DEC-889 item 5).

The list is ``tests/acceptance/serial-only.txt`` (``support.SERIAL_ONLY_REL``), in the form the cases of
``test_w1_30_r11_parallel_runs.py`` hold for any project: one entry on a line, the beginning of a node id, the text
after `` #`` a comment. In this repository every entry's comment is ``<route>: <kind>: <reason>``: ``serial`` keeps
the entry in the close (alone, after the parallel phase), ``nightly`` routes it to the nightly (collected by the
close and left out of both its phases, run alone in the nightly). The kinds and their routes (DEC-889 item 5):
latency cases stay alone, daemon and race cases stay serial in this run, live and real-model cases move to the
nightly. A case is never declared merely because it is slow.

Rewrite-Reason: DEC-889 item 5 (W2-57, P-IS-6's first table). The earlier version held today's entries one by one
with four kinds and no route. This one holds the reworked list: every entry's route, kind and reason; the live and
real-model files and cases the KPI names routed to the nightly; W1-16's cases that start no daemon, and W1-50's
read-merge latency case, out of the list (they run in parallel); W1-16's daemon cases, W1-09's two races and the
latency cases kept serial with their reasons; and no entry that names no case.

The cases read the list and the test files as text and ask the test runner only to collect (W1-16); no declared
case is run here.
"""

import re
import subprocess
import sys

import pytest

import w1_30_support as support

LIST = support.REPO_ROOT / support.SERIAL_ONLY_REL
ACCEPTANCE = "tests/acceptance"
SERIAL, NIGHTLY = "serial", "nightly"
# The kinds an entry of this repository's list names, and the route each takes (DEC-889 item 5).
KINDS = {"latency": SERIAL, "daemon": SERIAL, "race": SERIAL, "real-model": NIGHTLY, "live-session": NIGHTLY}
REASON_WORDS = 3   # a reason in words: more than a kind or a ticket number

# The report's table of the suites it timed: the node id, how many parameter sets it has, and its route.
NAMED_IN_THE_TIMED_SUITES = {
    f"{ACCEPTANCE}/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms": (5, SERIAL),
    f"{ACCEPTANCE}/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook": (9, SERIAL),
    f"{ACCEPTANCE}/W1-50/test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays":
        (1, NIGHTLY),
    f"{ACCEPTANCE}/W1-50/test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path":
        (1, NIGHTLY),
}

# The other cases the list declares, with their route. A file alone means every case of the file.
DECLARED_WITH_THEIR_ROUTE = {
    f"{ACCEPTANCE}/W1-25/test_w1_25_live_session.py": NIGHTLY,
    f"{ACCEPTANCE}/W1-46/test_w1_46_live_sessions.py": NIGHTLY,
    f"{ACCEPTANCE}/W1-49/test_w1_49_live_session.py": NIGHTLY,
    f"{ACCEPTANCE}/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95": NIGHTLY,
    f"{ACCEPTANCE}/W1-19/test_w1_19_real_models.py": NIGHTLY,
    f"{ACCEPTANCE}/W1-21/test_w1_21_dev_tier.py": NIGHTLY,
    f"{ACCEPTANCE}/W1-18/test_w1_18_deadline.py::test_a_daemon_that_never_becomes_healthy_is_given_up_at_the_deadline":
        SERIAL,
    f"{ACCEPTANCE}/W1-18/test_w1_18_deadline.py::test_an_endpoint_that_accepts_and_never_answers_does_not_hang_the_call":
        SERIAL,
    f"{ACCEPTANCE}/W1-07/test_w1_07_help.py::test_help_answers_in_under_300_ms": SERIAL,
    f"{ACCEPTANCE}/W1-10/test_w1_10_dev_tier.py::test_a_full_load_of_a_dev_tier_takes_less_than_5_seconds": SERIAL,
    f"{ACCEPTANCE}/W1-17/test_w1_17_dev_tier.py::"
    "test_one_changed_file_is_re_indexed_by_the_next_retrieval_within_the_bound": SERIAL,
    f"{ACCEPTANCE}/W1-15/test_w1_15_parallel_scan.py::"
    "test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder": SERIAL,
    f"{ACCEPTANCE}/W1-20/test_w1_20_code.py": SERIAL,
    f"{ACCEPTANCE}/W2-69/test_w2_69_deleted_text_after_rebuild.py::"
    "test_the_code_graph_store_holds_no_deleted_word_and_no_free_page_after_a_rebuild": SERIAL,
    f"{ACCEPTANCE}/W2-69/test_w2_69_review_rebuild_root_and_held_store.py::"
    "test_a_rebuild_given_the_project_relatively_returns_its_result_and_compacts_every_store": SERIAL,
    f"{ACCEPTANCE}/W2-57/test_w2_57_designer_read_p95.py": SERIAL,
    # W1-09's two races stay serial in this run; they move to the parallel phase after one green nightly there.
    f"{ACCEPTANCE}/W1-09/test_w1_09_review.py::"
    "test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim": SERIAL,
    f"{ACCEPTANCE}/W1-09/test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder":
        SERIAL,
}

# DEC-889 item 5 (P-IS-6, I1 F-2, I3 F6): the live and real-model files and cases that leave the close for the
# nightly. Every case of each, as the test runner collects it, is declared on the nightly route.
LIVE_AND_REAL_MODEL = (
    f"{ACCEPTANCE}/W1-46/test_w1_46_live_sessions.py",
    f"{ACCEPTANCE}/W1-50/test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays",
    f"{ACCEPTANCE}/W1-50/test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path",
    f"{ACCEPTANCE}/W1-19/test_w1_19_real_models.py",
    f"{ACCEPTANCE}/W1-21/test_w1_21_dev_tier.py",
    f"{ACCEPTANCE}/W1-21/test_w1_21_family_check.py::test_the_check_is_green_when_the_dev_tiers_meet_the_baselines",
    f"{ACCEPTANCE}/W1-49/test_w1_49_live_session.py",
    f"{ACCEPTANCE}/W1-25/test_w1_25_live_session.py",
    f"{ACCEPTANCE}/W2-58/test_w2_58_launched_sessions.py::test_a_launched_engineer_collects_its_own_acceptance_tests",
    f"{ACCEPTANCE}/W2-58/test_w2_58_launched_sessions.py::test_a_launched_engineer_runs_its_tests_and_sees_their_results",
    f"{ACCEPTANCE}/W2-58/test_w2_58_launched_sessions.py::test_a_launched_test_designer_imports_the_branch_s_changed_code",
    f"{ACCEPTANCE}/W2-58/test_w2_58_launched_sessions.py::test_a_launched_session_shows_no_phantom_deletion",
    f"{ACCEPTANCE}/W2-62/test_w2_62_live_resume.py",
    f"{ACCEPTANCE}/W2-54/test_w2_54_sandboxed_worker.py",
    f"{ACCEPTANCE}/W2-54/test_w2_54_query_vector.py::"
    "test_with_the_real_embedder_one_question_gives_one_answer_whatever_was_asked_before",
)

# Cases of the same files that assert no time bound and start nothing real, and the cases P-IS-6 moves to the
# parallel phase: none is declared.
NOT_DECLARED = (
    f"{ACCEPTANCE}/W1-07/test_w1_07_help.py::test_help_prints_usage_and_ends_with_exit_code_0",
    f"{ACCEPTANCE}/W1-18/test_w1_18_deadline.py::test_the_default_deadline_is_20_seconds",
    f"{ACCEPTANCE}/W1-10/test_w1_10_dev_tier.py::test_a_dev_tier_loads_to_the_same_digest_twice",
    f"{ACCEPTANCE}/W1-05/test_w1_05_switch_over_record.py::test_the_operator_diff_check_is_recorded_as_retired",
    f"{ACCEPTANCE}/W1-09/test_w1_09_claims.py::test_a_released_ticket_can_be_claimed_again",
    f"{ACCEPTANCE}/W1-02/test_w1_02_guard_hook.py",
    f"{ACCEPTANCE}/W1-30/test_w1_30_close.py",
    # I1 §4.2: its bound is 10 s and it took at most 1.2 s alone and 0.8 s in parallel at peak loads of 77.
    f"{ACCEPTANCE}/W1-50/test_w1_50_review_of_the_symmetric_rule.py::"
    "test_read_merge_answers_for_a_merge_commit_with_very_many_parents_in_time_and_never_calls_the_undone_test_brought",
    # The W2-58 cases that start nothing: they read the settings gov launch writes.
    f"{ACCEPTANCE}/W2-58/test_w2_58_launched_sessions.py::test_the_launch_denies_no_tracked_file_of_the_project_by_a_read_rule",
    f"{ACCEPTANCE}/W2-58/test_w2_58_launched_sessions.py::test_the_held_out_rules_stay_in_every_launched_role_s_settings",
)

W1_16 = f"{ACCEPTANCE}/W1-16"
W1_16_MARKER = "local_only"   # W1-16's own marker: the tool's binary, gitleaks or a dev tier (its conftest)
# I3 F7: of W1-16's 161 marked cases, these 19 functions (94 cases) start no daemon: they run gitleaks, the
# pre-index filter, or read the dev tiers' sources or the question set. They run in the parallel phase. The other
# marked cases (67) reach the codebase-memory daemon, and stay serial.
W1_16_NO_DAEMON = {
    "test_w1_16_builtin_allowlist_and_daemon_secrets.py": (
        "test_a_file_with_a_secret_the_builtin_allowlist_shelters_is_not_indexable",
        "test_a_file_with_the_sheltering_words_and_no_secret_is_indexable",
        "test_a_path_name_with_a_secret_the_builtin_allowlist_shelters_holds_a_secret",
        "test_a_path_name_with_the_sheltering_words_and_no_secret_holds_no_secret",
        "test_the_sheltered_values_are_secrets_by_the_projects_rules_alone",
    ),
    "test_w1_16_code_answers.py": (
        "test_the_expected_answers_stand_in_the_source_of_the_tier",
        "test_the_question_set_covers_the_three_languages",
    ),
    "test_w1_16_daemon_dir_and_names.py": (
        "test_a_body_that_begins_with_a_separator_is_flagged_only_when_the_rest_is_token_shaped",
        "test_a_file_with_a_token_whose_body_begins_with_a_separator_is_not_indexable",
    ),
    "test_w1_16_paths_and_roots.py": ("test_the_planted_path_names_are_secrets_by_the_rules",),
    "test_w1_16_token_rule.py": (
        "test_a_body_with_a_digit_or_with_mixed_case_is_flagged",
        "test_a_body_without_a_digit_and_without_mixed_case_is_not_flagged",
        "test_a_file_whose_only_match_is_an_ordinary_identifier_is_indexable",
        "test_a_file_with_a_token_shaped_string_is_not_indexable",
        "test_a_token_shaped_string_is_still_flagged",
        "test_every_file_holding_a_dev_canary_is_still_reported",
        "test_no_prefix_and_no_separator_flags_an_ordinary_identifier",
        "test_ordinary_identifiers_in_code_are_not_flagged",
        "test_the_length_floor_of_sixteen_characters_stays",
    ),
}
W1_16_NO_DAEMON_CASES = 94
W1_16_DAEMON_CASES = 67


def _entries():
    assert LIST.is_file(), f"this repository has no {support.SERIAL_ONLY_REL}"
    return support.serial_only_entries(LIST)


def _names():
    return [entry for entry, _ in _entries()]


def _parsed(comment):
    """``(route, kind, reason)`` of a comment ``<route>: <kind>: <reason>``; None for another form."""
    parts = [part.strip() for part in comment.split(":", 2)]
    return tuple(parts) if len(parts) == 3 else None


def _route(node):
    """The route of the entry that names ``node``; None when no entry names it."""
    for entry, comment in _entries():
        if support.declared_serial_only(node, [entry]):
            found = _parsed(comment)
            return found[0] if found else comment
    return None


def _collected(*args):
    """The node ids the test runner collects for ``args`` in this repository, with this worktree's code."""
    import os

    env = {**os.environ, "PYTHONPATH": str(support.SRC)}
    done = subprocess.run([sys.executable, "-m", "pytest", *args, "--collect-only", "-q", "-p", "no:cacheprovider"],
                          cwd=str(support.REPO_ROOT), env=env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    assert done.returncode in (0, 5), f"the test runner did not collect {args}:\n{done.stdout}\n{done.stderr}"
    return [line.strip() for line in done.stdout.splitlines() if "::" in line]


@pytest.mark.parametrize("node", sorted(NAMED_IN_THE_TIMED_SUITES))
def test_every_case_the_report_names_in_the_suites_it_timed_is_declared_with_its_route(node):
    count, route = NAMED_IN_THE_TIMED_SUITES[node]
    assert _route(node) == route, f"{node} is not declared on the {route} route: {_route(node)!r}"
    collected = [found for found in _collected(node) if found.split("[")[0] == node]
    assert len(collected) == count, f"{node} has {len(collected)} parameter sets, the report names {count}"
    assert all(_route(found) == route for found in collected), f"a parameter set of {node} is not declared {route}"


@pytest.mark.parametrize("node", sorted(DECLARED_WITH_THEIR_ROUTE))
def test_every_other_case_the_list_holds_is_declared_with_its_route(node):
    route = DECLARED_WITH_THEIR_ROUTE[node]
    assert _route(node) == route, f"{node} is not declared on the {route} route: {_route(node)!r}"


@pytest.mark.parametrize("node", LIVE_AND_REAL_MODEL)
def test_every_live_and_real_model_case_leaves_the_close_for_the_nightly(node):
    """DEC-889 item 5: every case of the file or function, as collected, is declared on the nightly route."""
    collected = [found for found in _collected(node) if support.declared_serial_only(found, [node])]
    assert collected, f"the fixture is wrong: {node} names no case"
    wrong = sorted(found for found in collected if _route(found) != NIGHTLY)
    assert not wrong, f"live or real-model cases left in the close (not on the nightly route): {wrong}"


def test_w1_16_s_daemon_cases_stay_serial_and_its_cases_that_start_no_daemon_are_not_declared():
    every = _collected(W1_16)
    marked = set(_collected(W1_16, "-m", W1_16_MARKER))
    no_daemon = {node for node in marked
                 if node.split("::")[0].rsplit("/", 1)[-1] in W1_16_NO_DAEMON
                 and node.split("::")[1].split("[")[0] in W1_16_NO_DAEMON[node.split("::")[0].rsplit("/", 1)[-1]]}
    daemon = marked - no_daemon
    assert (len(no_daemon), len(daemon)) == (W1_16_NO_DAEMON_CASES, W1_16_DAEMON_CASES), (
        f"the fixture is wrong: W1-16 has {len(no_daemon)} marked cases in the 19 functions that start no daemon and "
        f"{len(daemon)} other marked cases; I3 F7 counts {W1_16_NO_DAEMON_CASES} and {W1_16_DAEMON_CASES}"
    )
    not_serial = sorted(node for node in daemon if _route(node) != SERIAL)
    assert not not_serial, f"cases of W1-16 that reach the daemon are not declared serial: {not_serial}"
    declared = sorted(node for node in no_daemon | (set(every) - marked) if _route(node) is not None)
    assert not declared, f"cases of W1-16 that start no daemon are declared: {declared}"
    kinds = {_parsed(comment)[1] for entry, comment in _entries() if entry.startswith(W1_16) and _parsed(comment)}
    assert kinds == {"daemon"}, f"W1-16's entries name other kinds than `daemon`: {sorted(kinds)}"


@pytest.mark.parametrize("node", NOT_DECLARED)
def test_a_case_of_no_kind_or_moved_to_the_parallel_phase_is_not_declared(node):
    assert node not in _names() and _route(node) is None, \
        f"{node} is declared although it is none of the kinds, or P-IS-6 moves it to the parallel phase"


def test_every_entry_says_its_route_its_kind_and_its_reason():
    """``<route>: <kind>: <reason>``: the route is one of the two, the kind one of the five and on its own route,
    and the reason is words of its own."""
    wrong = []
    for entry, comment in _entries():
        found = _parsed(comment)
        if found is None:
            wrong.append(f"{entry}: no `<route>: <kind>: <reason>` comment: {comment!r}")
            continue
        route, kind, reason = found
        if route not in (SERIAL, NIGHTLY):
            wrong.append(f"{entry}: the route {route!r} is neither {SERIAL!r} nor {NIGHTLY!r}")
        elif kind not in KINDS:
            wrong.append(f"{entry}: the kind {kind!r} is none of {sorted(KINDS)}")
        elif KINDS[kind] != route:
            wrong.append(f"{entry}: a {kind} case takes the {KINDS[kind]} route, not {route!r}")
        if len(re.findall(r"[A-Za-z]{2,}", reason)) < REASON_WORDS:
            wrong.append(f"{entry}: its reason is not in words: {reason!r}")
    assert not wrong, "entries of the list that do not say their route, kind and reason:\n" + "\n".join(wrong)


def test_every_entry_names_cases_that_exist():
    """An entry that names nothing would set nothing apart and say that it does. Each entry is a file of this
    repository under ``tests/``, with the function it names defined in it, named once, not also named by the entry
    of its whole file, and the test runner collects at least one case of it."""
    entries = _entries()
    assert entries, f"{support.SERIAL_ONLY_REL} declares nothing"
    names = [entry for entry, _ in entries]
    assert len(set(names)) == len(names), f"an entry is there twice: {sorted(n for n in names if names.count(n) > 1)}"
    for entry in names:
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
    collected = _collected(*names)
    empty = [entry for entry in names if not any(support.declared_serial_only(node, [entry]) for node in collected)]
    assert not empty, f"entries of the list that name no case the test runner collects: {empty}"
