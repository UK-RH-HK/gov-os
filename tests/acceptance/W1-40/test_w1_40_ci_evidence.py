"""The CI job: the deterministic checks, and the evidence record of the head commit (KPI S2, F1, F2) [CAP-39.a].

``ci()`` runs the ``run:`` steps of every push workflow of this repository on a fresh checkout of what the bare
repository holds, as the hosted runner would after a push (see ``w1_40_support.Runner``). The project is green by
construction, so the job is green exactly when the record of the head commit is there and every step passed.
"""

from __future__ import annotations

import pytest

import w1_40_support as support

# A change folder of the temporary project whose proposal holds no specification record (gov.readiness.checker).
UNJUDGED_CHANGE = "openspec/changes/w1-40-unjudged/proposal.md"


# -- the evidence record ---------------------------------------------------

def test_ci_is_red_when_no_record_exists(project, ci):
    """A commit pushed past the hook has no record."""
    project.unhooked_commit()
    done, arrived = project.push(project.setup, verify=False)
    assert arrived, support.said(done)
    result = ci()
    assert not result.green, f"CI is green for a commit that was pushed without the pre-push gate:\n{result}"


def test_ci_is_red_when_the_record_is_for_another_commit(project, pushed, ci):
    """The record of the commit before does not vouch for the head commit."""
    assert ci().green, "the fixture is not green before the second commit"
    head = project.unhooked_commit("more.txt")
    done, arrived = project.push(project.setup, verify=False)
    assert arrived and head != pushed, support.said(done)
    result = ci()
    assert not result.green, f"CI is green on {head[:8]} with the record of {pushed[:8]} alone:\n{result}"


def test_a_push_with_a_failing_g3_check_never_leaves_ci_green(project, machine, ci):
    """Failure line 2. The hook refuses the push; forced past the hook, the commit has no passing record."""
    dev = machine()
    project.commit(dev)
    project.fail("G3")
    done, arrived = project.push(dev)
    assert not arrived, f"a failing G3 check did not stop the push:\n{support.said(done)}"
    done, arrived = project.push(dev, verify=False)
    assert arrived, support.said(done)
    project.fail("G3", failing=False)  # the check fails on the developer's machine only: CI must not depend on it
    result = ci()
    assert not result.green, f"a push with a failing G3 check left CI green:\n{result}"


def test_a_failed_attempt_leaves_nothing_that_a_later_bypass_can_use(project, machine, pushed, ci):
    """A green record of the last good commit, then a failing G3 on a new commit pushed past the hook: CI is red."""
    dev = machine()
    project.commit(dev, "more.txt")
    project.fail("G3")
    project.push(dev)
    done, arrived = project.push(dev, verify=False)
    assert arrived, support.said(done)
    result = ci()
    assert not result.green, f"CI is green for a commit whose G3 check failed:\n{result}"


# -- the deterministic checks ----------------------------------------------

def test_ci_does_not_run_the_g3_check_and_calls_no_model_tool(project, pushed, ci):
    """Failure line 1. CI reads the record; it does not run what needs a model (DEC-087)."""
    project.forget_runs()
    result = ci()
    assert result.green, f"CI is red for a commit pushed through the hook:\n{result}"
    assert project.ran("G3") == 0, "the CI job ran the project's G3 check"
    assert project.model_tool_calls() == [], f"the CI job called a model tool: {project.model_tool_calls()}"


def test_ci_does_not_go_red_for_a_g3_check_that_would_fail_on_the_runner(project, pushed, ci):
    """The runner has no model: a G3 check that cannot pass there does not decide the job. The record does."""
    project.fail("G3")
    result = ci()
    assert result.green, f"the CI job depends on a G3 check passing on the runner:\n{result}"


def test_ci_runs_the_g1_and_g2_checks(project, pushed, ci):
    project.forget_runs()
    result = ci()
    assert project.ran("G1") >= 1 and project.ran("G2") >= 1, f"the CI job did not run the G1 and G2 checks:\n{result}"


@pytest.mark.parametrize("tier", ["G1", "G2"])
def test_ci_is_red_when_a_deterministic_check_fails(project, pushed, ci, tier):
    """The record is there; the check fails on the runner; its exit code is not dropped."""
    project.fail(tier)
    result = ci()
    assert not result.green, f"a failing {tier} hard-block check left CI green:\n{result}"


def test_ci_is_red_when_a_check_of_gov_check_that_carries_no_tier_fails(project, machine, pushed, ci):
    """DEC-087 names readiness among what the job runs; DEC-489: "CI runs the whole of the deterministic checks,
    so no check runs nowhere". ``gov check`` runs its readiness check beside the declared ones; it carries no
    tier, so no hook runs it, and the job is the one place left for it.

    The defect: a change folder whose ``proposal.md`` holds no specification record. The readiness check cannot
    judge it and is RED, hard-block (W1-13, W1-26). It needs no tool, and it is in the tree that is pushed.
    """
    assert ci().green, "the fixture is not green before the defect"
    dev = machine()
    done, moved = project.commit(dev, UNJUDGED_CHANGE, "# A change with no specification record\n")
    assert moved, f"the hook refused the commit: the fixture cannot be built\n{support.said(done)}"
    done, arrived = project.push(dev)
    assert arrived, f"the hook refused the push: the fixture cannot be built\n{support.said(done)}"
    head = project.head()
    assert any(head in text for text in project.records(head).values()), "the head commit has no evidence record"
    statuses = support.check_statuses(project.gov(dev, "check", "--json"))
    red = sorted(check for check, status in statuses.items() if status == "RED")
    assert red == ["readiness"], f"the fixture is not red by its readiness check alone: {statuses}"
    result = ci()
    assert not result.green, (
        "the CI job is green for a project whose readiness check is red: the check carries no tier, so the job "
        f"is the only place it could have run (DEC-087, DEC-489):\n{result}")


def test_ci_is_red_when_gitleaks_reports_a_finding(project, pushed, ci):
    result = ci(leak=True)
    assert not result.green, f"a gitleaks finding left CI green:\n{result}"


@pytest.mark.parametrize("missing", ["gitleaks", "gov"])
def test_ci_is_red_when_a_tool_it_names_is_missing(project, pushed, ci, missing):
    """DEC-449, DEC-454: a step whose tool is not on the runner fails; it is never skipped to green."""
    result = ci(**{missing: False})
    assert not result.green, f"CI is green although {missing} could not run:\n{result}"


def test_ci_is_red_when_a_test_of_the_project_fails(project, machine, ci):
    """DEC-087: the tests that need no local model run in CI. The test fails on the runner only, so the record is there."""
    dev = machine()
    done, moved = project.commit(
        dev, "tests/test_ok.py", "import os\n\n\ndef test_ok():\n    assert os.environ.get('GITHUB_ACTIONS') != 'true'\n")
    assert moved, support.said(done)
    done, arrived = project.push(dev)
    assert arrived, support.said(done)
    result = ci()
    assert not result.green, f"a failing test of the project left CI green:\n{result}"
