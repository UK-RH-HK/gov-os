"""The CI job where a tool is not on the runner, and what one run of it reports (DEC-494, DEC-497) [CAP-39.a].

DEC-497: a step whose tool is not on the runner prints the word "unmeasured" with the tool's name and fails; it
is never green and never skipped in silence. Inside the job's own gate that holds for a check of ``gov check``
that reports its tool absent: the job names that check as unmeasured and is red. The later steps still run after
a failed one, so one run reports every step. A check whose family ``gov check`` does not know fails the job as
it fails ``gov check``; and the checkout brings the parent commit, so a defect that only a comparison with the
commit before shows is red in the job.

Every case states a result of the job: its colour, and words of its output. The simulated runner has a stand-in
``openspec`` and the designer's ``pytest`` unless a case withholds one (``w1_40_support.Machine``).
"""

from __future__ import annotations

import yaml

import w1_40_support as support

OPENSPEC_CHECK = "openspec-validate"                   # the id `gov check` gives its openspec check (W1-26)
ADAPTER_CHECK = yaml.safe_load(support.ADAPTER_CHECK.read_text(encoding="utf-8"))["id"]   # W1-38's declaration
UNKNOWN_FAMILY = "w1-40 a family gov check does not know"
SKILL = "---\nname: w1-40-skill\nversion: 1.0.0\n---\n# A skill\n\n{body}\n"


def _statuses(project, machine):
    done = project.gov(machine, "check", "--json")
    return done, support.check_statuses(done)


# -- a step whose tool is not on the runner ---------------------------------

def test_the_tests_step_says_unmeasured_and_fails_where_pytest_is_not_on_the_runner(project, pushed, ci):
    assert ci().green, "the fixture is not green on a runner that has pytest"
    result = ci(pytest=False)
    assert not result.green, f"the job is green on a runner where the project's tests could not run:\n{result}"
    said = result.said_by_one_step(support.UNMEASURED, "pytest", failed=True)
    assert said, (
        f"no failed step says '{support.UNMEASURED}' with the name pytest on a runner without pytest (DEC-497):\n"
        f"{result}")
    assert result.failed == said, f"a step other than the one that needs pytest failed:\n{result}"


def test_the_job_names_the_openspec_check_unmeasured_and_fails_where_openspec_is_not_on_the_runner(
        project, pushed, machine, ci):
    """``gov check`` itself reports the absent tool as YELLOW and ends with exit 0 (W1-26). The job does not
    take that for green (DEC-494: never green; DEC-497 replaces "take the yellow")."""
    done, statuses = _statuses(project, machine(openspec=False))
    assert done.returncode == 0 and statuses.get(OPENSPEC_CHECK) == "YELLOW", (
        f"the fixture does not hold: gov check without openspec is not exit 0 with {OPENSPEC_CHECK} YELLOW: "
        f"{statuses}\n{support.said(done)}")
    assert ci().green, "the fixture is not green on a runner that has openspec"
    result = ci(openspec=False)
    assert not result.green, (
        f"the job is green on a runner without openspec: the check {OPENSPEC_CHECK} was not measured:\n{result}")
    said = result.said_by_one_step(support.UNMEASURED, OPENSPEC_CHECK, failed=True)
    assert said, (
        f"no failed step names the check {OPENSPEC_CHECK} with the word '{support.UNMEASURED}' (DEC-497):\n{result}")
    assert result.failed == said, f"a step other than the one that runs the checks failed:\n{result}"


def test_the_job_names_the_adapter_check_unmeasured_and_fails_where_rulesync_is_not_on_the_runner(
        project, machine, ci):
    """The adapter check (W1-38) reports rulesync absent as a finding. The project holds what the check needs to
    find nothing else: with a rulesync on the runner the job is green, without one it is red and says why."""
    version = str(support.registry()["rulesync"]["version"])
    dev = machine(rulesync=version)
    project.adapter_sources(version)
    done, moved = project.commit_tree(dev)
    assert moved, f"the fixture cannot be built: the hook refused the commit\n{support.said(done)}"
    done, arrived = project.push(dev)
    assert arrived, f"the fixture cannot be built: the hook refused the push\n{support.said(done)}"
    done, statuses = _statuses(project, dev)
    assert statuses.get(ADAPTER_CHECK) == "GREEN", (
        f"the fixture does not hold: with rulesync there the adapter check is not GREEN: {statuses}\n"
        f"{support.said(done)}")
    assert ci(rulesync=version).green, "the fixture is not green on a runner that has rulesync"
    result = ci()
    assert not result.green, f"the job is green on a runner without rulesync:\n{result}"
    said = result.said_by_one_step(support.UNMEASURED, ADAPTER_CHECK, failed=True)
    assert said, (
        f"no failed step names the check {ADAPTER_CHECK} with the word '{support.UNMEASURED}' (DEC-497):\n{result}")


# -- one run reports every step ---------------------------------------------

def test_one_run_reports_every_step_after_a_failed_one(project, machine, ci):
    """A failing G1 check, a gitleaks finding, a passing test and a record that is there: one run of the job
    holds all four results. No step is left out because an earlier one failed."""
    dev = machine()
    done, moved = project.commit(
        dev, "tests/test_mark.py",
        "import os\n\n\ndef test_mark():\n    with open(os.path.join(os.environ['W1_40_MARKS'], 'tests'), 'a') as mark:\n"
        "        mark.write('run\\n')\n")
    assert moved, support.said(done)
    done, arrived = project.push(dev)
    assert arrived, support.said(done)
    assert ci().green, "the fixture is not green before the failing check"
    project.forget_runs()
    for mark in ("tests", "gitleaks"):
        (project.marks / mark).unlink(missing_ok=True)
    project.fail("G1")
    result = ci(leak=True)
    assert not result.green and project.ran("G1") >= 1, f"the failing G1 check did not fail the job:\n{result}"
    assert not result.skipped, (
        "steps did not run because an earlier step failed: one run of the job does not report every step "
        f"(DEC-497): {[step.name for step in result.skipped]}\n{result}")
    assert (project.marks / "gitleaks").is_file(), f"gitleaks did not run after the failed check:\n{result}"
    assert (project.marks / "tests").is_file(), f"the project's tests did not run after the failed check:\n{result}"
    notes = support.sh(["git", "for-each-ref", "--format=%(refname)", support.NOTES], result.workspaces[0],
                       project.setup.env(), check=True).stdout.split()
    assert notes, f"the ref of the evidence record was not fetched after the failed check:\n{result}"
    passed = [step for step in result.ran if step.returncode == 0]
    assert len(result.failed) >= 2 and len(passed) >= 2, (
        "the failing check and the gitleaks finding do not each have a failed step, or the tests and the record "
        f"do not each have a passed one:\n{result}")


# -- a defect that only the commit before shows ------------------------------

def test_the_job_is_red_for_a_skill_whose_content_changed_and_whose_version_did_not(project, machine, ci):
    """The skill-version check of ``gov check`` compares the head commit with its parent (W1-26, CAP-24.c). It
    carries no tier, so the job is its one place (DEC-489), and the job has the parent only when the checkout
    brings it (DEC-497)."""
    dev = machine()
    for body in ("first wording", "second wording, the version left as it was"):
        done, moved = project.commit(dev, support.SKILL_REL, SKILL.format(body=body))
        assert moved, f"the fixture cannot be built: the hook refused the commit\n{support.said(done)}"
        done, arrived = project.push(dev)
        assert arrived, f"the fixture cannot be built: the hook refused the push\n{support.said(done)}"
        if body == "first wording":
            assert ci().green, "the fixture is not green for the commit that adds the skill"
    done, statuses = _statuses(project, dev)
    red = sorted(check for check, status in statuses.items() if status == "RED")
    assert red == ["skill-version"], f"the fixture is not red by its skill-version check alone: {statuses}"
    result = ci()
    assert not result.green, (
        "the job is green for a commit that changes a skill's content and not its version: the comparison with "
        f"the commit before did not run or did not count (DEC-497):\n{result}")


# -- a check of a family gov check does not know ------------------------------

def test_the_job_is_red_where_the_project_declares_a_check_of_a_family_gov_check_does_not_know(
        project, pushed, machine, ci):
    assert ci().green, "the fixture is not green before the declaration"
    dev = machine()
    project.unhooked_commit(f"{support.CHECKS_REL}/w1-40-unknown.yaml", yaml.safe_dump(
        {"id": "w1-40-unknown", "family": UNKNOWN_FAMILY, "tier": "G2", "severity": "hard-block", "command": "true"},
        sort_keys=False))
    done, arrived = project.push(dev)
    assert arrived, f"the fixture cannot be built: the hook refused the push\n{support.said(done)}"
    done, statuses = _statuses(project, dev)
    assert done.returncode != 0 and "RED" not in statuses.values(), (
        "the fixture does not hold: gov check does not fail for the unknown family alone (every check passing): "
        f"{statuses}\n{support.said(done)}")
    result = ci()
    assert not result.green, (
        f"gov check fails in this project for a check of the family {UNKNOWN_FAMILY!r} and the job is green "
        f"(DEC-497):\n{result}")
