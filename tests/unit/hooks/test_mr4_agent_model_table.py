"""The helper-model hook writes the role table's Sonnet model for a spawn that names none (MR-4 follow-up)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / ".claude/hooks/agent_model.py"


def table(*rows):
    return "version: 1\nrows:\n" + "".join(
        f"  - {{role: {r}, model: {m}, effort: high, decided: x}}\n" for r, m in rows)


def run(tmp_path, tool_input, body=None):
    if body is not None:
        (tmp_path / "governance/project").mkdir(parents=True, exist_ok=True)
        (tmp_path / "governance/project/role-table.yaml").write_text(body)
    event = {"tool_name": "Agent", "tool_input": tool_input}
    done = subprocess.run([sys.executable, "-I", str(HOOK)], input=json.dumps(event), capture_output=True, text=True,
                          env={"CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": os.environ["PATH"]}, cwd=str(tmp_path))
    return done


def written(done):
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)["hookSpecificOutput"]["updatedInput"]


def test_the_row_of_the_subagent_type_gives_the_model(tmp_path):
    out = written(run(tmp_path, {"subagent_type": "research", "prompt": "p"},
                      table(("research", "claude-sonnet-5-6"), ("engineer", "claude-sonnet-5-5"))))
    assert out == {"subagent_type": "research", "prompt": "p", "model": "claude-sonnet-5-6"}


@pytest.mark.parametrize("body", (None, "version: 1\nrows: [\n", table(("engineer", "claude-sonnet-5-5")),
                                  table(("general-purpose", "claude-opus-5-5")), "- a\n"))
def test_no_table_no_row_an_opus_row_or_an_unreadable_table_mean_sonnet(tmp_path, body):
    assert written(run(tmp_path, {"prompt": "p"}, body))["model"] == "sonnet"


def test_the_refusal_rules_are_unchanged(tmp_path):
    body = table(("general-purpose", "claude-sonnet-5-6"))
    assert run(tmp_path, {"model": "claude-opus-5-5", "prompt": "p"}, body).returncode == 2
    done = run(tmp_path, {"model": "sonnet", "prompt": "p"})
    assert done.returncode == 0 and done.stdout == ""


def test_the_kit_copy_is_byte_equal():
    assert HOOK.read_bytes() == (REPO / "template/.claude/hooks/agent_model.py").read_bytes()
