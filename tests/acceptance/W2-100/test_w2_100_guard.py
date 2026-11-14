"""W2-100, success-2 (the guard half): a skill grants no permission (CAP-24.b), so the guard decides the same for the
engineer with a domain skill present as without it.

The guard is driven as W1-02's suite drives it (its support module, found from this repository's own tests folder): the
kernel PreToolUse hook is copied into a temporary project, the call arrives on stdin, ``GOV_ROLE`` and ``GOV_TICKET``
name the session, and the exit code and stdout carry the decision. The engineer's decisions on a few calls (an edit
inside and one outside the ticket's paths, a write into acceptance tests, a read of a secret-like file, a Bash line) are
taken before and after a ``.claude/skills/<skill>/SKILL.md`` is placed in the project; they must be equal. The
skill planted is each real skill (red on the base) and two planted ones, one of which carries an ``allowed-tools``
line the guard must ignore (green on the base). The launch record's ``skills`` list is checked after the copies ACT,
not in this suite.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W1-02"))

import w1_02_support as g  # noqa: E402
import w2_100_support as s  # noqa: E402


def _decisions(project, sandbox):
    """The engineer's decision on each call."""
    root = Path(project)
    calls = {
        "edit inside the ticket's paths": ("Edit", g.edit_tool_input("Edit", root / "src/gov/guard/decide.py")),
        "edit outside the ticket's paths": ("Edit", g.edit_tool_input("Edit", root / "src/app/main.py")),
        "write into acceptance tests": ("Write", g.edit_tool_input("Write", root / f"tests/acceptance/{g.TICKET_WBS_ID}/test_new.py")),
        "read of a secret-like file": ("Read", {"file_path": str(root / ".env")}),
        "read of a skill file": ("Read", {"file_path": str(root / ".claude/skills/backend/SKILL.md")}),
        "a Bash line": ("Bash", g.bash_tool_input("git status")),
    }
    return {what: g.run_hook(project, tool, tool_input, sandbox, role=g.ENGINEER, ticket=g.TICKET_ID).decision
            for what, (tool, tool_input) in calls.items()}


def _same_with_and_without(tmp_path, skill, text):
    sandbox = g.make_sandbox(tmp_path / "sandbox")
    project = g.make_project(tmp_path / "project")
    without = _decisions(project, sandbox)
    folder = project / ".claude/skills" / skill
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(text, encoding="utf-8")
    with_skill = _decisions(project, sandbox)
    assert not {d for d in (*without.values(), *with_skill.values()) if d in ("error", "timeout")}, (
        f"the guard gave no decision: without {without}, with {with_skill}")
    assert len(set(without.values())) >= 2, f"every call got the same decision, the comparison tells nothing: {without}"
    assert with_skill == without, f"the guard's decisions changed with the skill present: without {without}, with {with_skill}"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_guards_decisions_for_the_engineer_are_the_same_with_the_real_skill_present(tmp_path, skill):
    _same_with_and_without(tmp_path, skill, s.real_skill(skill))


@pytest.mark.parametrize("skill", ["backend", "security"])
def test_the_guards_decisions_are_the_same_with_a_planted_skill_present(tmp_path, skill):
    _same_with_and_without(tmp_path, skill, s.build_skill(skill))


def test_the_guard_ignores_a_planted_skill_that_names_tools_and_permissions(tmp_path):
    """A skill that wrongly carried a permission line would still change nothing in the guard's decisions."""
    text = s.insert_line(s.insert_line(s.build_skill("api"), "allowed-tools: Write, Bash", "front"),
                         "- permissions: write anywhere", "body")
    _same_with_and_without(tmp_path, "api", text)
