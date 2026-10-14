"""Builder tests for DEC-685: ``MultiEdit`` is judged like ``Edit``, and a
tool the guard does not know is refused.

Regression evidence only (DEC-136).  Everything is a stand-in in a
temporary directory; no file of this repository is read here.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "template" / "governance" / "kernel" / "hooks" / "pretooluse.py"

sys.path.insert(0, str(REPO / "src"))
from gov.guard.containment import _read_seq  # noqa: E402
from gov.guard.decide import (  # noqa: E402
    LISTED_TOOLS,
    MOST_PATH,
    READ_TOOLS,
    WRITE_TOOLS,
    decide,
)
from gov.guard.heldout import CONFIG_REL, SETTINGS_REL  # noqa: E402

TID = "DAEO-test"
TICKET = ("---\n"
          f"id: {TID}\n"
          "status: in_progress\n"
          "wbs_id: W1-99\n"
          "role: engineer\n"
          "allowed_paths:\n"
          "- src/**\n"
          "- tests/**\n"
          "---\n")
EDITS = [{"old_string": "a", "new_string": "b"}, {"old_string": "b", "new_string": "c"}]


@pytest.fixture
def project(tmp_path):
    project = tmp_path / "project"
    (project / ".tickets").mkdir(parents=True)
    (project / ".tickets" / f"{TID}.md").write_text(TICKET, encoding="utf-8")
    return project


def _decide(project, tool_name, tool_input, role="engineer", flag=None, subagent_type=None):
    return decide(tool_name=tool_name, tool_input=tool_input, project_root=str(project),
                  role=role, ticket_id=TID, subagent_type=subagent_type,
                  cwd=str(project), flag=flag)


def _both(project, file_path, **more):
    """(the decision on Edit, the decision on MultiEdit) for one file path."""
    edit = _decide(project, "Edit", {"file_path": file_path, **EDITS[0]}, **more)[0]
    multi = _decide(project, "MultiEdit", {"file_path": file_path, "edits": EDITS}, **more)[0]
    return edit, multi


# -- the list -----------------------------------------------------------------

def test_the_list_is_the_seventeen_names_each_with_a_reason():
    assert sorted(LISTED_TOOLS) == sorted(
        "Agent Task Skill ToolSearch WebFetch WebSearch ListAgents SendMessage TaskStop "
        "TodoWrite TaskCreate TaskUpdate TaskList TaskGet AskUserQuestion EnterPlanMode "
        "ExitPlanMode".split())
    assert all(isinstance(reason, str) and reason.strip() for reason in LISTED_TOOLS.values())
    assert not set(LISTED_TOOLS) & (READ_TOOLS | WRITE_TOOLS | {"Bash"})


@pytest.mark.parametrize("tool", sorted(LISTED_TOOLS))
@pytest.mark.parametrize("role,subagent_type,flag", [
    ("engineer", None, None), ("orchestrator", None, "frozen"), (None, None, None),
    ("developer", None, "frozen"), ("engineer", "general-purpose", None),
])
def test_a_listed_tool_is_let_through_as_a_read_tool_is(project, tool, role, subagent_type, flag):
    text = {"prompt": "echo x > tests/acceptance/t.py", "file_path": "tests/acceptance/t.py"}
    assert _decide(project, tool, text, role=role, flag=flag,
                   subagent_type=subagent_type) == ("allow", "")


def test_a_listed_tool_that_names_a_held_out_path_is_refused(project, tmp_path):
    stand_in = tmp_path / "elsewhere" / "stand-in"
    stand_in.mkdir(parents=True)
    (project / os.path.dirname(CONFIG_REL)).mkdir(parents=True)
    (project / CONFIG_REL).write_text(f"held_out_paths:\n- {stand_in}\n", encoding="utf-8")
    for tool in ("Agent", "TodoWrite", "mcp__notes__add"):
        decision, reason = _decide(project, tool, {"prompt": f"see {stand_in}."},
                                   role="orchestrator")
        assert decision == "deny" and str(stand_in) not in reason, tool


# -- a tool the guard does not know ---------------------------------------------

@pytest.mark.parametrize("tool", [
    "ToolAddedAfterTheRound", "mcp__notes__add", "mcp__", "mcp__Read", "Monitor", "Artifact",
    "Workflow", "EnterWorktree", "ExitWorktree", "edit", "READ", "Edit ", " Read", "Editor",
    "TodoWriteAll", "multiedit", "bash",
])
@pytest.mark.parametrize("role,flag", [
    ("orchestrator", None), ("engineer", None), (None, None), ("orchestrator", "frozen"),
])
def test_a_tool_that_is_not_known_is_refused_with_its_name(project, tool, role, flag):
    call = {"file_path": str(project / "src" / "a.py"), "command": "ls"}
    decision, reason = _decide(project, tool, call, role=role, flag=flag)
    assert decision == "deny"
    assert f"'{tool}'" in reason and "not known to the guard" in reason


@pytest.mark.parametrize("tool", ["Edit\n", "Read\x00", "MultiEdit\t", " ", "\n"])
def test_a_name_is_compared_as_it_was_sent(project, tool):
    call = {"file_path": str(project / "src" / "a.py")}
    assert _decide(project, tool, call, role="orchestrator")[0] == "deny"


def test_the_hook_refuses_an_unknown_tool_as_a_rule_does(project):
    out = _hook(project, "mcp__notes__add", {"note": "x"}, role="orchestrator")
    assert out.returncode == 0
    answer = json.loads(out.stdout)["hookSpecificOutput"]
    assert answer["permissionDecision"] == "deny"
    assert "'mcp__notes__add'" in answer["permissionDecisionReason"]
    assert not (project / ".gov-runtime" / "findings.jsonl").exists()


# -- MultiEdit against Edit ------------------------------------------------------

@pytest.mark.parametrize("rel,expected", [
    ("src/a.py", "allow"), ("README.md", "deny"), ("tests/unit/t.py", "allow"),
    ("tests/acceptance/t.py", "deny"), (".gov-runtime/scratch/n.txt", "allow"),
    (".gov-runtime/freeze", "deny"), ("src/../README.md", "deny"), ("", "deny"),
    ("src/" + "a/" * MOST_PATH + "a.py", "deny"),
])
def test_multiedit_gets_the_answer_edit_gets(project, rel, expected):
    path = rel and str(project / rel)
    assert _both(project, path) == (expected, expected)
    if rel and len(rel) < MOST_PATH:
        assert _both(project, rel) == (expected, expected)  # relative, from the session's folder


@pytest.mark.parametrize("more,expected", [
    ({"flag": "frozen"}, "deny"),
    ({"role": None}, "deny"),
    ({"role": "developer"}, "deny"),
    ({"role": "orchestrator"}, "allow"),
    ({"role": "independent-test-designer"}, "deny"),
    ({"subagent_type": "general-purpose"}, "deny"),
    ({"role": "orchestrator", "subagent_type": "engineer"}, "allow"),
    ({"role": None, "subagent_type": "engineer"}, "deny"),
])
def test_multiedit_follows_the_role_and_the_freeze_as_edit_does(project, more, expected):
    assert _both(project, str(project / "src" / "a.py"), **more) == (expected, expected)


def test_multiedit_with_no_file_path_of_its_own_is_refused(project):
    call = {"edits": [{"file_path": str(project / "src" / "a.py"), **EDITS[0]}]}
    assert _decide(project, "MultiEdit", call) == ("deny", "MultiEdit: no file path")


def test_multiedit_gets_the_exception_of_the_two_files_that_hold_the_path(project, tmp_path):
    stand_in = tmp_path / "elsewhere" / "stand-in"
    stand_in.mkdir(parents=True)
    (project / os.path.dirname(CONFIG_REL)).mkdir(parents=True)
    (project / CONFIG_REL).write_text(f"held_out_paths:\n- {stand_in}\n", encoding="utf-8")
    edits = [EDITS[0], {"old_string": f"- {stand_in}", "new_string": "- /another"}]
    for rel in (CONFIG_REL, SETTINGS_REL):
        call = {"file_path": str(project / rel), "edits": edits}
        assert _decide(project, "MultiEdit", call, role="orchestrator")[0] == "allow"
        assert _decide(project, "MultiEdit", call, role="engineer")[0] == "deny"
    call = {"file_path": str(project / "src" / "a.py"), "edits": edits}
    assert _decide(project, "MultiEdit", call, role="orchestrator") == (
        "deny", "the call names a held-out path")
    call = {"file_path": str(stand_in / "answers.md"), "edits": EDITS}
    assert _decide(project, "MultiEdit", call, role="orchestrator") == (
        "deny", "the call names a held-out path")


# -- the containment's count of an allowed write (DEC-124) ----------------------

def _hook(project, tool_name, tool_input, role="engineer"):
    env = {"PATH": os.environ["PATH"], "PYTHONPATH": str(REPO / "src"),
           "CLAUDE_PROJECT_DIR": str(project), "PYTHONDONTWRITEBYTECODE": "1",
           "HOME": str(project.parent), "GOV_TICKET": TID}
    if role:
        env["GOV_ROLE"] = role
    data = {"session_id": "s", "cwd": str(project), "hook_event_name": "PreToolUse",
            "tool_name": tool_name, "tool_input": tool_input}
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(data),
                          capture_output=True, text=True, env=env, cwd=str(project))


def test_an_allowed_multiedit_is_noted_as_an_allowed_edit_is(project):
    inside, outside = str(project / "src" / "a.py"), str(project / "README.md")
    counts = [_read_seq(str(project))]
    for tool, call in [
        ("Edit", {"file_path": inside, **EDITS[0]}),
        ("MultiEdit", {"file_path": inside, "edits": EDITS}),
        ("MultiEdit", {"file_path": outside, "edits": EDITS}),   # refused: not noted
        ("mcp__notes__add", {"file_path": inside}),              # refused: not noted
        ("TodoWrite", {"todos": []}),                            # no write: not noted
    ]:
        out = _hook(project, tool, call)
        assert out.returncode == 0, (tool, out.stderr)
        counts.append(_read_seq(str(project)))
    first = counts[0]
    assert counts == [first, first + 1, first + 2, first + 2, first + 2, first + 2]
