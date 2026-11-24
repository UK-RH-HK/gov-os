"""W2-201 (DAEO-k1us) fix F13: the helper hook writes the model into the spawn.

A spawn that names no model ran Opus (audit 1's four built-in Explore helpers) because the hook passed it on the
assumption that the default applies. The hook now answers a PreToolUse JSON on stdout whose ``updatedInput`` is the
full tool input with ``model`` ``sonnet``. Run as a subprocess on planted events."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
HOOKS = [REPO / ".claude" / "hooks" / "agent_model.py"]
FABLE = "claude-fable-5-2"


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    (root / "governance/project").mkdir(parents=True)
    (root / ".tickets").mkdir()
    (root / "governance/project/model-exceptions.yaml").write_text(
        yaml.safe_dump({"exceptions": [{"subagent_type": "independent-auditor", "model": "opus", "decided": "DEC-x",
                                        "task": "DAEO-aaaa"}]}), encoding="utf-8")
    return root


def run(hook, root, args, tool="Agent"):
    event = json.dumps({"tool_name": tool, "tool_input": args})
    return subprocess.run([sys.executable, "-I", str(hook), ], input=event, capture_output=True, text=True,
                          env={"CLAUDE_PROJECT_DIR": str(root), "PATH": "/usr/bin:/bin"}, timeout=30)


def updated(done):
    assert done.returncode == 0, done
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse" and out["permissionDecision"] == "allow", out
    return out["updatedInput"]


@pytest.mark.parametrize("hook", HOOKS, ids=lambda p: str(p.relative_to(REPO)))
@pytest.mark.parametrize("kind", ["Explore", "Plan", "general-purpose", "engineer", None])
@pytest.mark.parametrize("tool", ["Agent", "Task"])
def test_a_spawn_naming_no_model_comes_back_with_sonnet_and_every_other_key(hook, project, kind, tool):
    args = {"prompt": "Look at it.\nTask: DAEO-bbbb", "description": "look", "run_in_background": True,
            **({"subagent_type": kind} if kind else {})}
    new = updated(run(hook, project, dict(args), tool))
    assert new == {**args, "model": "sonnet"}


@pytest.mark.parametrize("hook", HOOKS, ids=lambda p: str(p.relative_to(REPO)))
def test_an_opus_auditor_under_an_exception_keeps_its_model(hook, project):
    args = {"prompt": "Audit.\nTask: DAEO-aaaa", "subagent_type": "independent-auditor", "model": "opus"}
    done = run(hook, project, dict(args))
    assert done.returncode == 0, done
    if done.stdout.strip():
        assert updated(done).get("model") == "opus"


@pytest.mark.parametrize("hook", HOOKS, ids=lambda p: str(p.relative_to(REPO)))
def test_fable_is_refused(hook, project):
    done = run(hook, project, {"prompt": "x", "subagent_type": "Explore", "model": FABLE})
    assert done.returncode == 2 and "fable" in done.stderr.lower(), done


@pytest.mark.parametrize("hook", HOOKS, ids=lambda p: str(p.relative_to(REPO)))
@pytest.mark.parametrize("model", ["sonnet", "claude-sonnet-5-5"])
def test_a_spawn_already_naming_sonnet_passes_with_its_model(hook, project, model):
    args = {"prompt": "x", "subagent_type": "Explore", "model": model}
    done = run(hook, project, dict(args))
    assert done.returncode == 0, done
    if done.stdout.strip():
        assert updated(done) == args


@pytest.mark.parametrize("hook", HOOKS, ids=lambda p: str(p.relative_to(REPO)))
def test_another_tool_is_left_alone(hook, project):
    done = run(hook, project, {"command": "ls"}, tool="Bash")
    assert (done.returncode, done.stdout) == (0, "")
