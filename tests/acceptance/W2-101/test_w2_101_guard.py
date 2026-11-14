"""W2-101 success-2 (the guard half): the skill grants no permission, so the guard's decision for the engineer is the
same with the skill loaded and without it.

The live hook (``<repository>/.claude/hooks/pretooluse.py``) is run as Claude Code runs it, on a project planted in
``tmp_path``: one planted tree without a ``.claude/skills/frontend/`` and one with it, the same calls on both, the
engineer's role and an engineer ticket naming the frontend skill. The skill loaded is, in turn, a stand-in (green on
the base: it shows the guard ignores a skill placed in the tree) and the real frontend skill's text (red until it
exists). "Listed beside the engineer role in the launch record" is checked after the copies ACT, not here.
"""
from __future__ import annotations

import pytest

import w2_101_support as s

STAND_IN = ("---\nname: frontend\nversion: \"1.0.0\"\ndescription: A stand-in used to show the guard ignores a skill "
            "placed in the tree.\n---\n\n# Frontend\n\nA stand-in.\n")

# (name, tool, input with <root>, the decision every tree must give)
CALLS = [
    ("read a readme", "Read", {"file_path": "<root>/README.md"}, "allow"),
    ("read the skill file", "Read", {"file_path": "<root>/.claude/skills/frontend/SKILL.md"}, "allow"),
    ("write a source file", "Write", {"file_path": "<root>/src/app/ui.py", "content": "x = 2\n"}, "allow"),
    ("git status", "Bash", {"command": "git status"}, "allow"),
    ("read a secrets file", "Read", {"file_path": "<root>/.env"}, "deny"),
    ("read a key file", "Read", {"file_path": "<root>/deploy/server.key"}, "deny"),
    ("write an acceptance test", "Write", {"file_path": "<root>/tests/acceptance/W2-101P/test_new.py",
                                           "content": "x = 1\n"}, "deny"),
    ("install a package", "Bash", {"command": "pip install requests"}, "deny"),
    ("sudo", "Bash", {"command": "sudo ls"}, "deny"),
]


def _fill(value, root):
    if isinstance(value, str):
        return value.replace("<root>", root)
    return {k: _fill(v, root) for k, v in value.items()}


def _decisions(root):
    return {name: s.guard_decision(root, tool, _fill(tin, root)) for name, tool, tin, _want in CALLS}


@pytest.fixture(scope="module")
def without_skill(tmp_path_factory):
    return _decisions(s.plant_guard_tree(tmp_path_factory.mktemp("guard") / "without"))


def test_the_engineers_decisions_on_the_planted_tree_are_the_expected_ones(without_skill):
    """The base the comparison rests on: the guard allows and refuses the calls as the rules say (not vacuous)."""
    wanted = {name: want for name, _tool, _tin, want in CALLS}
    assert without_skill == wanted, f"the guard's decisions differ from the rules': {without_skill}"


def test_the_guard_decides_the_same_with_a_stand_in_skill_placed(without_skill, tmp_path):
    with_skill = _decisions(s.plant_guard_tree(tmp_path / "with-stand-in", STAND_IN))
    assert with_skill == without_skill, f"the guard's decision changed with a skill placed: {with_skill} vs {without_skill}"


def test_the_guard_decides_the_same_with_the_real_frontend_skill_placed(without_skill, tmp_path):
    with_skill = _decisions(s.plant_guard_tree(tmp_path / "with-frontend", s.read_skill("frontend")))
    assert with_skill == without_skill, \
        f"the guard's decision changed with the frontend skill placed: {with_skill} vs {without_skill}"


def test_the_guard_decides_the_same_when_each_of_the_three_real_skills_is_placed(without_skill, tmp_path):
    """The three skills alike: each placed under the frontend folder name in turn changes no decision."""
    for skill in s.SKILLS:
        with_skill = _decisions(s.plant_guard_tree(tmp_path / f"with-{skill}", s.read_skill(skill)))
        assert with_skill == without_skill, f"the guard's decision changed with {skill} placed: {with_skill}"
