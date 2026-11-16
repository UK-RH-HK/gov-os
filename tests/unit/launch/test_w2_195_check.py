"""W2-195 (DAEO-d8df) S3, the launch's half: ``read_role`` (which ``gov launch`` calls) refuses
``LAUNCH_JUDGING_RULE_MISSING`` for a judging role (independent-auditor, as which the reviewer and the probe launch;
qa-engineer) whose role file does not name judging-work, or whose preloaded copy is missing or of another version
than the kernel file's (DEC-1204 (5)). Other roles are not checked.

Regression evidence only (DEC-136), on planted trees.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import role  # noqa: E402

from .test_w2_195_preload import KERNEL, plant  # noqa: E402

CODE = "LAUNCH_JUDGING_RULE_MISSING"
JUDGES = ("independent-auditor", "qa-engineer")
WITH = "- **Skills:** judging-work"
PRELOADED = role.SKILLS_REL + "/judging-work/SKILL.md"
KERNEL_REL = "template/governance/kernel/skills/judging-work/SKILL.md"


def _rulesync_form(data: bytes) -> bytes:
    return data.replace(b'version: "1.0.0"\nmetadata:', b"metadata:").replace(b"---\n\n#", b"---\n#")


def _lacks(tmp_path, name):
    return plant(tmp_path, name, "- **Skills:** audit")


def _no_line(tmp_path, name):
    return plant(tmp_path, name, "")


def _copy_removed(tmp_path, name):
    tree = plant(tmp_path, name, WITH)
    (tree / PRELOADED).unlink()
    return tree


def _other_version(tmp_path, name):
    return plant(tmp_path, name, WITH, preloaded=_rulesync_form(KERNEL.read_bytes()).replace(b"1.0.0", b"0.9.0"))


def _kernel_removed(tmp_path, name):
    tree = plant(tmp_path, name, WITH)
    (tree / KERNEL_REL).unlink()
    return tree


def _kernel_other_version(tmp_path, name):
    return plant(tmp_path, name, WITH, kernel=KERNEL.read_bytes().replace(b"1.0.0", b"1.0.1"),
                 preloaded=KERNEL.read_bytes())


BREAKS = {"skills-line-lacks-judging-work": _lacks, "no-skills-line": _no_line,
          "preloaded-copy-removed": _copy_removed, "preloaded-copy-other-version": _other_version,
          "kernel-file-removed": _kernel_removed, "kernel-file-other-version": _kernel_other_version}


@pytest.mark.parametrize("name", JUDGES)
@pytest.mark.parametrize("brk", sorted(BREAKS))
def test_a_judging_launch_without_the_skill_or_of_another_version_is_refused_by_name(tmp_path, name, brk):
    tree = BREAKS[brk](tmp_path, name)
    if brk == "skills-line-lacks-judging-work":  # the named skill is there: only the judging rule refuses
        (tree / role.SKILLS_REL / "audit").mkdir()
        (tree / role.SKILLS_REL / "audit/SKILL.md").write_text("---\nname: audit\nversion: 1.0.0\n---\n# A\n")
    with pytest.raises(GovError) as raised:
        role.read_role(tree, name)
    assert raised.value.code == CODE, raised.value.message


@pytest.mark.parametrize("name", JUDGES)
def test_the_judging_code_wins_over_the_generic_not_at_refusal(tmp_path, name):
    tree = _copy_removed(tmp_path, name)
    with pytest.raises(GovError) as raised:
        role.read_role(tree, name)
    assert raised.value.code == CODE and PRELOADED in raised.value.message


@pytest.mark.parametrize("name", JUDGES)
def test_a_preloaded_copy_in_rulesyncs_form_passes(tmp_path, name):
    tree = plant(tmp_path, name, WITH, preloaded=_rulesync_form(KERNEL.read_bytes()))
    assert b'\nversion: "1.0.0"' not in (tree / PRELOADED).read_bytes()
    entry = [skill for skill in role.read_role(tree, name)["skills"] if skill["name"] == "judging-work"]
    assert entry[0]["named"] is True and entry[0]["version"] == "1.0.0"


def test_an_adopted_tree_compares_with_its_governance_kernel(tmp_path):
    tree = plant(tmp_path, "qa-engineer", WITH)
    (tree / "template").rename(tree / "moved")
    (tree / "governance/kernel/roles").mkdir(parents=True)
    (tree / "moved/governance/kernel/roles/qa-engineer.md").rename(tree / "governance/kernel/roles/qa-engineer.md")
    with pytest.raises(GovError) as raised:
        role.read_role(tree, "qa-engineer")
    assert raised.value.code == CODE and "governance/kernel/skills/judging-work/SKILL.md" in raised.value.message
    (tree / "governance/kernel/skills/judging-work").mkdir(parents=True)
    (tree / "governance/kernel/skills/judging-work/SKILL.md").write_bytes(KERNEL.read_bytes())
    assert role.read_role(tree, "qa-engineer")["role_text"]["path"] == "governance/kernel/roles/qa-engineer.md"


@pytest.mark.parametrize("name", ("engineer", "independent-test-designer", "orchestrator", "ticket-lead"))
def test_other_roles_are_not_checked(tmp_path, name):
    tree = plant(tmp_path, name, "")
    (tree / PRELOADED).unlink()
    (tree / KERNEL_REL).unlink()
    assert role.read_role(tree, name)["role_text"]["version"] == "1.0.0"
