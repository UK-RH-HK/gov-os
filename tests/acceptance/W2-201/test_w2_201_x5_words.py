"""W2-201 fix X5 (DEC-1219 (5)): words match code.

A repository-state test (it reads this repository's kernel files and their copies, not a planted tree). The kernel
lines that tell a CTO or lead how to launch work say: a new ticket only for a new feature; a fix launches under its
owning ticket with ``gov launch <role> <ticket> --fix "<line>"``; a chore with ``gov launch <role> --chore "<line>"``.
In each of ``orchestrator.md``, ``senior-engineer.md`` and ``ticket-lead.md`` the ``Tools:`` line (where ``gov launch``
is named) holds ``new ticket only for a new feature``, ``--fix`` and ``--chore``; in the orchestration skill's
``## Parallel tickets`` one line holds the three. Each copy a copy check holds equal to its kernel file
(``.rulesync/subagents``, ``template/.rulesync/subagents``, ``.claude/agents``; the skill's copies under
``.rulesync/skills``, ``template/.rulesync/skills``, ``.claude/skills``) holds the same line, byte for byte (the role
copies' ``Tools:`` line; the skill copies' whole section).
"""

from __future__ import annotations

import pytest

import w2_201_support as k

ROOT = k.REPO_ROOT
ROLES = ("orchestrator", "senior-engineer", "ticket-lead")
ROLE_COPIES = k.COPY_FOLDERS
SKILL = "template/governance/kernel/skills/orchestration/SKILL.md"
SKILL_COPIES = (".rulesync/skills/orchestration/SKILL.md", "template/.rulesync/skills/orchestration/SKILL.md",
                ".claude/skills/orchestration/SKILL.md")
SECTION = "## Parallel tickets"
PHRASE = "new ticket only for a new feature"
TOOLS = "- **Tools:**"


def _missing(line):
    """Which of the three statements ``line`` lacks (the phrase in any letter case, the two options as written)."""
    return [word for word, there in ((PHRASE, PHRASE in line.lower()), ("--fix", "--fix" in line),
                                     ("--chore", "--chore" in line)) if not there]


def _tools_line(rel):
    path = ROOT / rel
    assert path.is_file(), f"{rel} does not exist in this repository"
    found = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(TOOLS)]
    assert len(found) == 1, f"{rel} holds {len(found)} lines starting {TOOLS!r}, not one"
    return found[0]


def _section(rel):
    path = ROOT / rel
    assert path.is_file(), f"{rel} does not exist in this repository"
    lines, inside, found = path.read_text(encoding="utf-8").splitlines(), False, []
    for line in lines:
        if line.startswith("## "):
            inside = line.strip() == SECTION
            continue
        if inside:
            found.append(line)
    assert found, f"{rel} has no section {SECTION!r}"
    return found


@pytest.mark.parametrize("role", ROLES)
def test_x5_the_kernel_role_file_s_tools_line_names_the_three_statements(role):
    rel = f"{k.ROLES_REL}/{role}.md"
    line = _tools_line(rel)
    assert "gov launch" in line, f"{rel}'s Tools line does not name gov launch: {line!r}"
    missing = _missing(line)
    assert not missing, f"{rel}'s Tools line lacks {missing}: {line!r}"


@pytest.mark.parametrize("folder", ROLE_COPIES)
@pytest.mark.parametrize("role", ROLES)
def test_x5_each_role_copy_holds_the_kernel_tools_line(role, folder):
    kernel, copy = _tools_line(f"{k.ROLES_REL}/{role}.md"), _tools_line(f"{folder}/{role}.md")
    assert copy == kernel, f"{folder}/{role}.md's Tools line is not the kernel file's:\n{copy!r}\n{kernel!r}"
    missing = _missing(copy)
    assert not missing, f"{folder}/{role}.md's Tools line lacks {missing}"


def test_x5_one_line_of_the_skill_s_parallel_tickets_names_the_three_statements():
    holding = [line for line in _section(SKILL) if not _missing(line)]
    assert len(holding) == 1, (f"{SKILL}'s {SECTION} has {len(holding)} lines holding {PHRASE!r}, --fix and --chore, "
                               f"not one")


@pytest.mark.parametrize("rel", SKILL_COPIES)
def test_x5_each_skill_copy_holds_the_kernel_section(rel):
    kernel, copy = _section(SKILL), _section(rel)
    assert copy == kernel, f"{rel}'s {SECTION} is not the kernel file's"
    assert [line for line in copy if not _missing(line)], f"{rel}'s {SECTION} has no line holding the three"
