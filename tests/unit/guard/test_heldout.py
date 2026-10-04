"""Builder tests for W1-47: the escape hatch, the held-out rule, the
session-role default and the script that writes the ``Read`` deny rules.

Regression evidence only (DEC-136).  The held-out path is a made-up
stand-in in a temporary directory; the committed ``held-out.yaml`` is
never read here.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import _get_allowed_paths, decide  # noqa: E402
from gov.guard.heldout import (  # noqa: E402
    CONFIG_REL,
    SETTINGS_REL,
    HeldOutError,
    load_held_out,
    write_read_rules,
)


def _project(tmp_path, config=None):
    project = tmp_path / "project"
    (project / "governance" / "project").mkdir(parents=True)
    (project / ".claude").mkdir()
    (project / "docs").mkdir()
    if config is not None:
        (project / CONFIG_REL).write_text(config, encoding="utf-8")
    return project


def _stand_in(tmp_path, project):
    """A made-up held-out directory, configured in *project*."""
    stand_in = tmp_path / "elsewhere" / "stand-in"
    stand_in.mkdir(parents=True)
    (stand_in / "answers.md").write_text("x\n", encoding="utf-8")
    (project / CONFIG_REL).write_text(
        f"held_out_paths:\n- {stand_in}\n", encoding="utf-8")
    return stand_in


def _decide(project, tool_name, tool_input, role="orchestrator"):
    return decide(tool_name=tool_name, tool_input=tool_input,
                  project_root=str(project), role=role, ticket_id=None,
                  cwd=str(project))[0]


# -- DEC-179: the session-role default fails closed ------------------------

def test_no_session_role_argument_gives_no_wide_scope(tmp_path):
    project = _project(tmp_path)
    assert _get_allowed_paths("orchestrator", None, str(project)) == []
    assert _get_allowed_paths("orchestrator", None, str(project),
                              session_role="orchestrator") == ["**"]


# -- CAP-62.a: the escape hatch ---------------------------------------------

@pytest.mark.parametrize("role", ["orchestrator", "engineer", None])
def test_escape_hatch_denied(tmp_path, role):
    project = _project(tmp_path)
    call = {"command": "ls -la", "dangerouslyDisableSandbox": True}
    assert _decide(project, "Bash", call, role) == "deny"
    call["dangerouslyDisableSandbox"] = False
    assert _decide(project, "Bash", call, role) == "allow"


# -- DEC-215: what names a held-out path -------------------------------------

def test_literal_path_denied_for_any_tool(tmp_path):
    project = _project(tmp_path)
    p = _stand_in(tmp_path, project)
    for tool, call in [
        ("Read", {"file_path": f"{p}/answers.md"}),
        ("Grep", {"pattern": "x", "path": str(p)}),
        ("Bash", {"command": f"python3 -c \"open('{p}/answers.md')\""}),
        ("Bash", {"command": "ls", "description": f"then {p}"}),
        ("mcp__notes__add", {"note": {"body": [f"see {p}."]}}),
    ]:
        assert _decide(project, tool, call) == "deny", (tool, call)


def test_reached_path_denied(tmp_path, monkeypatch):
    project = _project(tmp_path)
    p = _stand_in(tmp_path, project)
    monkeypatch.setenv("HOME", str(p.parent))
    rel = os.path.relpath(p, project)
    link = tmp_path / "a-link"
    link.symlink_to(p, target_is_directory=True)
    for tool, call in [
        ("Read", {"file_path": f"{rel}/answers.md"}),
        ("Bash", {"command": f"cat {rel}/answers.md"}),
        ("Bash", {"command": f"ls docs/../{rel}"}),
        ("Read", {"file_path": "~/stand-in/answers.md"}),
        ("Bash", {"command": "cat \"$HOME/stand-in/answers.md\""}),
        ("Read", {"file_path": f"{link}/answers.md"}),
        ("Bash", {"command": f"ls -la {link}/"}),
    ]:
        assert str(p) not in json.dumps(call)
        assert _decide(project, tool, call) == "deny", (tool, call)


def test_other_paths_stay_open(tmp_path):
    project = _project(tmp_path)
    _stand_in(tmp_path, project)
    assert _decide(project, "Read", {"file_path": f"{project}/README.md"}) == "allow"
    assert _decide(project, "Bash", {"command": "ls -la docs"}) == "allow"


def test_exception_for_the_two_files_that_hold_the_path(tmp_path):
    project = _project(tmp_path)
    p = _stand_in(tmp_path, project)
    for rel in (CONFIG_REL, SETTINGS_REL):
        call = {"file_path": str(project / rel), "content": f"- {p}\n"}
        assert _decide(project, "Write", call) == "allow"
        assert _decide(project, "Write", call, role="engineer") == "deny"
    call = {"file_path": str(project / "docs" / "notes.md"), "content": f"- {p}\n"}
    assert _decide(project, "Write", call) == "deny"
    call = {"command": f"cp {p}/answers.md {project / CONFIG_REL}"}
    assert _decide(project, "Bash", call) == "deny"


# -- DEC-218: the configuration ----------------------------------------------

def test_missing_file_means_no_rule(tmp_path):
    assert load_held_out(str(_project(tmp_path))) == []


@pytest.mark.parametrize("text", [
    "", "paths:\n- /srv/x\n", "held_out_paths: [\n", "- /srv/x\n",
    "held_out_paths:\n", "held_out_paths: []\n", "held_out_paths: /srv/x\n",
    "held_out_paths:\n- 42\n", "held_out_paths:\n- srv/x\n",
])
def test_broken_file_fails_closed(tmp_path, text):
    project = _project(tmp_path, text)
    with pytest.raises(HeldOutError):
        load_held_out(str(project))
    assert _decide(project, "Read", {"file_path": f"{project}/README.md"}) == "deny"


def test_no_message_carries_the_path(tmp_path):
    project = _project(tmp_path)
    p = _stand_in(tmp_path, project)
    _, reason = decide(tool_name="Read", tool_input={"file_path": str(p)},
                       project_root=str(project), role="engineer", ticket_id=None)
    assert reason and str(p) not in reason


# -- DEC-218: the script that writes the Read deny rules ----------------------

def test_write_read_rules(tmp_path, capsys):
    project = _project(tmp_path)
    p = _stand_in(tmp_path, project)
    settings = project / SETTINGS_REL
    settings.write_text(json.dumps(
        {"permissions": {"deny": ["Bash(sudo:*)"]}, "hooks": {}}), encoding="utf-8")
    assert write_read_rules(str(project)) == 1
    assert write_read_rules(str(project)) == 0  # run twice, one rule
    data = json.loads(settings.read_text(encoding="utf-8"))
    assert data["permissions"]["deny"] == ["Bash(sudo:*)", f"Read(/{p}/**)"]
    assert data["hooks"] == {}
    assert capsys.readouterr().out == ""
