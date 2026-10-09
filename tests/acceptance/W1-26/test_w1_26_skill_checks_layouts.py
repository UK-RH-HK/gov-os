"""The three skill-regression checks run where the kernel is installed (DEC-521; the follow-up after W1-41, DEC-569).

DEC-521 orders, for the follow-up: "the declared check commands that name ``template/`` paths".

Three declared checks call the skill validator with paths under ``template/governance/kernel/skills/``:
``skill-regression-a``, ``skill-regression-b1`` and ``skill-regression-orchestration``. In a project with an
installed kernel the skills lie under ``governance/kernel/skills/`` and those paths do not exist, so each of
the three answers "unmeasured" there, whatever the skills hold.

What the cases hold, for each of the three (README, section "The skill checks in both layouts"):

- **Installed layout.** With the check's skills well-formed under ``governance/kernel/skills/``: measured,
  no finding, exit code 0. With a defect planted in one of them: a finding that names that skill's file. With
  one of the check's skills absent: never green.
- **Template layout**, as today: green on well-formed skills, a finding on a planted defect.
- **Both layouts** (the stricter reading): both are measured. A defect in either is a finding, whatever the
  other holds.
- **Neither layout**: the unmeasured answer, exit code 1. Never green without having measured.

Each check is run as it is declared: the ``command`` of the kernel's declaration, started by a shell in the
temporary project's root, as the runner of ``gov check`` starts it, with this worktree's code. The skills are
fixtures written by the case; the names of each check's skills are those its declaration measures today. No
case names a path of this repository to the check.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402
import test_w1_26_skill_validator as skills  # noqa: E402

REPO_ROOT = support.REPO_ROOT
TIMEOUT_S = 60.0

TEMPLATE = "template/governance/kernel/skills"
INSTALLED = "governance/kernel/skills"

# check id -> the skills it measures
CHECKS = {
    "skill-regression-a": ("discovery", "planning", "test-design", "change"),
    "skill-regression-b1": ("retrieval", "audit", "checkpoint", "adopt"),
    "skill-regression-orchestration": ("orchestration",),
}
CHECK_IDS = sorted(CHECKS)
NO_FRONTMATTER = "SKILL_NO_FRONTMATTER"


def declared_command(check_id):
    path = REPO_ROOT / support.CHECKS_REL / f"{check_id}.yaml"
    declaration = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(declaration, dict) and isinstance(declaration.get("command"), str), \
        f"the kernel declares no command for {check_id}"
    return declaration["command"]


class Answer:
    def __init__(self, done):
        self.returncode = done.returncode
        self.said = f"exit code {done.returncode}\nstdout: {done.stdout[:3000]}\nstderr: {done.stderr[:3000]}"
        try:
            parsed = json.loads(done.stdout) if done.stdout.strip() else {}
        except ValueError:
            parsed = {"_raw": done.stdout}
        self.output = parsed if isinstance(parsed, dict) else {"findings": parsed}

    @property
    def measured(self):
        return "findings" in self.output and not self.output.get("unmeasured")

    @property
    def findings(self):
        return self.output.get("findings") or []

    @property
    def green(self):
        return self.returncode == 0


def run_declared(check_id, root):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(Path(root).parent),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(support.SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    done = subprocess.run(declared_command(check_id), shell=True, cwd=str(root), env=env, capture_output=True,
                          text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    return Answer(done)


@pytest.fixture()
def root(tmp_path):
    """A project that holds nothing yet. No file of this repository is in it."""
    folder = tmp_path / "project"
    folder.mkdir()
    (folder / "README.md").write_text("# A project\n", encoding="utf-8")
    return folder


def write_skills(root, layout, names, broken=None):
    """Well-formed skills ``names`` under ``layout``; the one named ``broken`` has no frontmatter."""
    for name in names:
        if name == broken:
            skills.make_skill(root / layout, name=name, raw=f"# {name}\n\nA skill whose frontmatter is gone.\n")
        else:
            skills.make_skill(root / layout, name=name, version="1.0.0", description=f"The {name} skill",
                              body=f"# {name}\n\nUse `gov status` first.\n")


def assert_green(answer, what):
    assert answer.measured, f"{what}: the check did not measure\n{answer.said}"
    assert answer.green and not answer.findings, f"{what}: the check is not green\n{answer.said}"


def assert_finding(answer, layout, name, what):
    """A measured answer, not green, with a finding about the broken skill's file in ``layout``."""
    assert answer.measured, f"{what}: the check did not measure (no findings in its answer)\n{answer.said}"
    assert not answer.green, f"{what}: the check is green\n{answer.said}"
    rel = f"{layout}/{name}/SKILL.md"
    # the installed path is the end of the template path: a finding about the template's file does not count for it
    named = [finding for finding in answer.findings
             if finding.get("code") == NO_FRONTMATTER and rel in json.dumps(finding)
             and (layout == TEMPLATE or f"template/{rel}" not in json.dumps(finding))]
    assert named, f"{what}: no {NO_FRONTMATTER} finding names {rel}\n{answer.said}"


def assert_never_green(answer, what):
    assert not answer.green, f"{what}: the check is green without having measured every skill\n{answer.said}"
    assert answer.output.get("unmeasured") is True or answer.findings, \
        f"{what}: the check says neither that it could not measure nor what it found\n{answer.said}"


# --------------------------------------------------------------------------
# The installed layout
# --------------------------------------------------------------------------

@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_in_an_installed_project_the_check_measures_and_is_green_on_well_formed_skills(check_id, root):
    write_skills(root, INSTALLED, CHECKS[check_id])
    assert_green(run_declared(check_id, root), f"{check_id}, the installed layout, well-formed skills")


@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_in_an_installed_project_a_planted_defect_is_a_finding(check_id, root):
    names = CHECKS[check_id]
    broken = names[-1]
    write_skills(root, INSTALLED, names, broken=broken)
    assert_finding(run_declared(check_id, root), INSTALLED, broken,
                   f"{check_id}, the installed layout, {broken} without frontmatter")


@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_in_an_installed_project_an_absent_skill_is_never_green(check_id, root):
    """The installed kernel holds another skill, and one of the check's own is not there."""
    names = CHECKS[check_id]
    write_skills(root, INSTALLED, names[:-1] + ("a-skill-of-no-check",))
    answer = run_declared(check_id, root)
    assert_never_green(answer, f"{check_id}, the installed layout without {names[-1]}")
    assert names[-1] in json.dumps(answer.output), \
        f"{check_id}: the answer does not name the absent skill {names[-1]}\n{answer.said}"


# --------------------------------------------------------------------------
# The template layout, as today
# --------------------------------------------------------------------------

@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_in_the_template_layout_the_check_is_green_on_well_formed_skills(check_id, root):
    write_skills(root, TEMPLATE, CHECKS[check_id])
    assert_green(run_declared(check_id, root), f"{check_id}, the template layout, well-formed skills")


@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_in_the_template_layout_a_planted_defect_is_a_finding(check_id, root):
    names = CHECKS[check_id]
    broken = names[0]
    write_skills(root, TEMPLATE, names, broken=broken)
    assert_finding(run_declared(check_id, root), TEMPLATE, broken,
                   f"{check_id}, the template layout, {broken} without frontmatter")


@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_in_the_template_layout_an_absent_skill_is_never_green(check_id, root):
    names = CHECKS[check_id]
    write_skills(root, TEMPLATE, names[:-1] + ("a-skill-of-no-check",))
    assert_never_green(run_declared(check_id, root), f"{check_id}, the template layout without {names[-1]}")


# --------------------------------------------------------------------------
# Both layouts, and neither
# --------------------------------------------------------------------------

@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_with_both_layouts_well_formed_the_check_is_green(check_id, root):
    write_skills(root, TEMPLATE, CHECKS[check_id])
    write_skills(root, INSTALLED, CHECKS[check_id])
    assert_green(run_declared(check_id, root), f"{check_id}, both layouts, well-formed skills")


@pytest.mark.parametrize("check_id", CHECK_IDS)
@pytest.mark.parametrize("layout", (INSTALLED, TEMPLATE), ids=("installed", "template"))
def test_with_both_layouts_a_defect_in_either_is_a_finding(layout, check_id, root):
    """Neither layout hides the other: the skills a role could load are all measured."""
    names = CHECKS[check_id]
    broken = names[0]
    for each in (TEMPLATE, INSTALLED):
        write_skills(root, each, names, broken=broken if each == layout else None)
    assert_finding(run_declared(check_id, root), layout, broken,
                   f"{check_id}, both layouts, {broken} without frontmatter in {layout}")


@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_in_a_project_with_neither_layout_the_check_is_unmeasured_and_never_green(check_id, root):
    answer = run_declared(check_id, root)
    assert answer.returncode == 1, f"{check_id}, no skills folder: the exit code is not 1\n{answer.said}"
    assert answer.output.get("unmeasured") is True and str(answer.output.get("reason", "")).strip(), \
        f"{check_id}, no skills folder: not the unmeasured answer with its reason\n{answer.said}"
    assert not answer.findings, f"{check_id}, no skills folder: findings without a skill\n{answer.said}"


@pytest.mark.parametrize("check_id", CHECK_IDS)
def test_a_skills_folder_without_the_check_s_skills_is_unmeasured(check_id, root):
    """An installed kernel that holds only skills of other checks: nothing of this check was measured."""
    write_skills(root, INSTALLED, ("a-skill-of-no-check",))
    answer = run_declared(check_id, root)
    assert_never_green(answer, f"{check_id}, an installed kernel without any of the check's skills")
    assert answer.output.get("unmeasured") is True, \
        f"{check_id}: not the unmeasured answer where none of its skills exists\n{answer.said}"
