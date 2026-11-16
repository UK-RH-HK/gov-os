"""W2-195 (DAEO-d8df) S1: every role that judges work preloads the judging-work skill (DEC-1204 (5)): the Skills line
of the four kernel role files, role-reviewer.md's skills list and the rulesync subagent mirrors name it, and
``read_role`` of a judging role carries it, named, with its version, in the skills the launch record holds.

Regression evidence only (DEC-136). The file checks read this tree; ``read_role`` runs on a planted tree.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.adapters import portability  # noqa: E402
from gov.launch import role  # noqa: E402

KERNEL = REPO / "template/governance/kernel/skills/judging-work/SKILL.md"
FOUR = ("independent-auditor", "qa-engineer", "orchestrator", "ticket-lead")
OLD = {"independent-auditor": ["audit", "retrieval"], "qa-engineer": ["qa-review"],
       "orchestrator": ["orchestration", "planning", "checkpoint", "change", "retrieval"],
       "ticket-lead": ["orchestration", "checkpoint", "retrieval"]}
MIRROR_OLD = {"independent-auditor": ["audit"], "qa-engineer": ["qa-review"], "orchestrator": ["orchestration"],
              "ticket-lead": ["orchestration", "checkpoint", "retrieval"]}


def _front(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("\n---\n", 1)[0][4:])


def _skills_line(path: Path) -> list[str]:
    found = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(role.SKILLS_HEAD)]
    assert len(found) == 1
    match = role.SKILLS_LINE.fullmatch(found[0])
    assert match, found[0]
    return match.group(1).split(", ")


@pytest.mark.parametrize("name", FOUR)
def test_the_kernel_role_files_skills_line_appends_judging_work(name):
    assert _skills_line(REPO / role.ROLES_REL / f"{name}.md") == [*OLD[name], "judging-work"]


def test_the_reviewer_templates_skills_list_appends_judging_work():
    assert _front(REPO / "template/governance/kernel/templates/role-reviewer.md")["skills"] == ["audit",
                                                                                                "judging-work"]


@pytest.mark.parametrize("name", FOUR)
def test_the_rulesync_mirror_preloads_judging_work_and_is_still_the_composition(name):
    mirror = REPO / "template/.rulesync/subagents" / f"{name}.md"
    assert _front(mirror)["claudecode"]["skills"] == [*MIRROR_OLD[name], "judging-work"]
    assert _skills_line(mirror) == [*OLD[name], "judging-work"]
    assert mirror.read_text(encoding="utf-8") == portability.compose(REPO / "template", name)


BEFORE = "bc91df0ab"  # the ticket's base, before any kernel change of W2-195


def _at_base(rel: str) -> list[str]:
    import subprocess
    text = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", f"{BEFORE}:{rel}"], capture_output=True,
                          text=True, check=True).stdout
    assert text, rel
    return text.split("\n")


def _appended(line: str) -> str:
    """The line with judging-work appended to its list: ``a, b`` -> ``a, b, judging-work``; ``[a]`` -> ``[a,
    judging-work]``; ``["a"]`` -> ``["a", "judging-work"]``."""
    if not line.endswith("]"):
        return line + ", judging-work"
    return line[:-1] + (', "judging-work"]' if '"' in line else ", judging-work]")


@pytest.mark.parametrize("rel", [f"{role.ROLES_REL}/{name}.md" for name in FOUR]
                         + [f"template/.rulesync/subagents/{name}.md" for name in FOUR]
                         + ["template/governance/kernel/templates/role-reviewer.md"])
def test_each_file_changes_only_its_skills_lines_by_appending_judging_work(rel):
    old, new = _at_base(rel), (REPO / rel).read_text(encoding="utf-8").split("\n")
    assert len(old) == len(new)
    changed = [(a, b) for a, b in zip(old, new) if a != b]
    assert changed, rel
    for a, b in changed:
        assert re.match(r"^(- \*\*Skills:\*\* |  skills: \[|skills: \[)", a) and b == _appended(a), (a, b)


def plant(tmp_path: Path, name: str, skills_line: str, kernel: bytes | None = None,
          preloaded: bytes | None = None) -> Path:
    """A tree with one role file, the judging-work kernel file and its preloaded copy (``None``: the kernel's)."""
    roles = tmp_path / role.ROLES_REL
    roles.mkdir(parents=True)
    (roles / f"{name}.md").write_text(f"# {name}\n\n- **Version:** 1.0.0\n- **Launch default:** model "
                                      f"claude-opus-5-5, effort high\n{skills_line}\n", encoding="utf-8")
    kernel = KERNEL.read_bytes() if kernel is None else kernel
    target = tmp_path / "template/governance/kernel/skills/judging-work/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(kernel)
    copy = tmp_path / role.SKILLS_REL / "judging-work/SKILL.md"
    copy.parent.mkdir(parents=True)
    copy.write_bytes(kernel if preloaded is None else preloaded)
    return tmp_path


@pytest.mark.parametrize("name", ("independent-auditor", "qa-engineer"))
def test_read_role_of_a_judging_role_carries_judging_work_named_with_its_version(tmp_path, name):
    loaded = role.read_role(plant(tmp_path, name, "- **Skills:** judging-work"), name)
    entry = [skill for skill in loaded["skills"] if skill["name"] == "judging-work"]
    assert len(entry) == 1
    assert (entry[0]["named"], entry[0]["version"], entry[0]["path"]) == (True, "1.0.0",
                                                                          ".claude/skills/judging-work/SKILL.md")
    assert loaded["appended"].endswith(KERNEL.read_bytes())
