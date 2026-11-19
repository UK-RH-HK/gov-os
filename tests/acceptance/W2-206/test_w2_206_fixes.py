"""The two fixes of W2-202 (its record, the lead's risks).

Success line 7 (fix 1: the runner keeps its JUnit report through ``keep_report``; the queue replaces nothing in the
runner) and failure line 4 (fix 2: an acceptance run that fails without naming a failing test names its ticket as
the culprit). README, "The planted runs": unnamed, unnamed_crash; the fix 1 cases plant a project of their own.
"""

from __future__ import annotations

import inspect
import sys

import pytest

import w2_206_support as support
from w2_206_support import A, B, CHANGED, P, Q, kit, module_rel

TIME_LIMIT = 600


@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    """A planted project checked out at A's branch tip (the widget changed, its suite green)."""
    folder = tmp_path_factory.mktemp("w2-206-fix1")
    p = kit.Planted(folder / "project", folder / "told")
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True)])
    kit.self_check(p, {p.tips[A.id]: {A.node: "passed"}})
    p.checkout("topic/aa")
    return p


# -- success line 7 (W2-202 fix 1) --------------------------------------------------------------------------------

def test_accept_takes_keep_report_and_its_default_is_none():
    from gov.accept import runner

    parameters = inspect.signature(runner.accept).parameters
    assert "keep_report" in parameters, f"gov.accept.runner.accept takes {list(parameters)}"
    assert parameters["keep_report"].default is None


def test_accept_with_keep_report_leaves_the_junit_report_at_the_path_and_answers_as_without_it(tree, tmp_path):
    from gov.accept import runner

    plain, plain_code = runner.accept(tree.root, A.id, TIME_LIMIT)
    assert plain_code == 0 and plain.get("outcome") == "pass", f"fixture: gov accept does not pass A: {plain}"
    kept = tmp_path / "kept.xml"
    answer, code = runner.accept(tree.root, A.id, TIME_LIMIT, keep_report=kept)
    assert kept.is_file(), "no JUnit report at the path keep_report names"
    assert kit.junit_outcomes(kept) == {A.node: "passed"}, f"the kept report holds {kit.junit_outcomes(kept)}"
    assert (answer, code) == (plain, plain_code), f"the answer with keep_report differs:\n{answer}\n{plain}"


def test_the_queue_s_acceptance_run_replaces_nothing_in_the_runner_before_during_or_after(tree, tmp_path):
    from gov.accept import runner
    from gov.queue import acceptance

    before = dict(vars(runner))
    read_cases, file = runner.read_cases, runner.accept.__code__.co_filename
    during = []

    def probe(frame, event, _arg):  # every call of a function of the runner's module, while the run runs
        if event == "call" and frame.f_code.co_filename == file:
            during.append(runner.read_cases is read_cases
                          and all(vars(runner).get(name) is value for name, value in before.items()))

    junit = tmp_path / "kept" / "acceptance.xml"
    sys.setprofile(probe)
    try:
        done = acceptance.run(tree.root, A.id, A.acceptance, TIME_LIMIT, junit)
    finally:
        sys.setprofile(None)
    assert during, "fixture: the queue's acceptance run called nothing of gov.accept.runner"
    assert all(during), "gov.queue.acceptance replaced a name of gov.accept.runner while its run ran"
    assert runner.read_cases is read_cases, "gov.accept.runner.read_cases is not the function it was"
    assert all(vars(runner).get(name) is value for name, value in before.items()), "a name of the runner changed"
    assert done.get("outcome") == "pass" and done.get("failing") == [], f"the run's answer: {done}"
    assert kit.junit_outcomes(junit) == {A.node: "passed"}, "the queue's acceptance run kept no JUnit report"


# -- failure line 4 (W2-202 fix 2) --------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def unnamed(landing):
    return landing("unnamed")


@pytest.fixture(scope="module")
def unnamed_crash(landing):
    return landing("unnamed_crash")


def _culprit_beside_a_landing(landing, ticket):
    result = kit.answer(landing.run, kit.EXIT_NOT_ALL_LANDED)
    assert result.get("culprits") == [ticket.id], f"culprits: {result.get('culprits')!r}"
    assert result.get("landed") == [B.id], f"landed: {result.get('landed')!r}"
    assert not support.named(landing.run, "BATCH_UNEXPLAINED"), "the batch is refused BATCH_UNEXPLAINED"
    return result


def test_a_ticket_whose_readme_maps_a_line_to_a_test_that_does_not_exist_is_the_batch_s_culprit(unnamed):
    _culprit_beside_a_landing(unnamed, P)


def test_the_batch_s_other_ticket_lands_and_closes(unnamed):
    result = _culprit_beside_a_landing(unnamed, P)
    closes = kit.assert_landed_through_close_commits(unnamed, result, "main", unnamed.old_head)
    assert list(closes) == [B.id]
    head = kit.heads(unnamed.extra["taken"]["after"])["refs/heads/main"]
    assert head == closes[B.id], "main is not at the other ticket's close commit"
    assert kit.status_at(unnamed.root, head, B.id) == "closed" and kit.status_at(unnamed.root, head, P.id) == "open"
    assert not kit.is_ancestor(unnamed.root, unnamed.tips[P.id], head), "the culprit's branch is under main"
    assert kit.show(unnamed.root, head, f"docs/close/{P.id}/CL-{P.id}.md") is None


def test_the_same_ticket_alone_is_a_culprit_with_exit_3_and_nothing_lands(unnamed):
    alone = unnamed.extra["alone"]
    result = kit.answer(alone["run"], kit.EXIT_NOT_ALL_LANDED)
    assert result.get("culprits") == [P.id] and result.get("landed") == [], f"the answer: {result}"
    assert result.get("head") is None and result.get("closes") == []
    assert not support.named(alone["run"], "BATCH_UNEXPLAINED"), "the ticket alone is refused BATCH_UNEXPLAINED"
    assert kit.heads(alone["after"]) == kit.heads(alone["before"]), "a branch moved"
    assert kit.status_at(unnamed.root, "main", P.id) == "open"


def test_a_ticket_whose_acceptance_folder_crashes_at_collection_is_the_batch_s_culprit(unnamed_crash):
    result = _culprit_beside_a_landing(unnamed_crash, Q)
    closes = kit.assert_landed_through_close_commits(unnamed_crash, result, "main", unnamed_crash.old_head)
    assert list(closes) == [B.id] and kit.status_at(unnamed_crash.root, "main", Q.id) == "open"
