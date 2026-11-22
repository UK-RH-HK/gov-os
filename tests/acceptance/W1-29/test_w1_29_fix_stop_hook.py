"""W1-29 (DAEO-zsvl) fix F12: the SubagentStop hook stops blocking twice.

It reads a value on the line after its label, and honours ``stop_hook_active`` (exit 0 when set). Run as a
subprocess, the repository's hook and the kit's copy."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOKS = [REPO / "src/gov/hooks/subagentstop.py", REPO / "template/governance/kernel/hooks/subagentstop.py"]
FIELDS = ("task", "status", "work_completed", "files_changed", "evidence", "tests", "discoveries", "risks",
          "lessons", "proposed_decisions", "unresolved", "recommended_next_action")


def run(hook, message, **more):
    event = {"hook_event_name": "SubagentStop", "last_assistant_message": message, **more}
    return subprocess.run([sys.executable, "-I", str(hook)], input=json.dumps(event), capture_output=True, text=True,
                          timeout=30)


ids = lambda p: str(p.relative_to(REPO))  # noqa: E731


@pytest.mark.parametrize("hook", HOOKS, ids=ids)
@pytest.mark.parametrize("style", ["plain", "bold", "heading"])
def test_a_return_with_each_value_on_the_next_line_passes(hook, style):
    label = {"plain": "{}:", "bold": "**{}:**", "heading": "## {}:"}[style]
    message = "\n".join(f"{label.format(f)}\nvalue of {f}" for f in FIELDS)
    done = run(hook, message)
    assert done.returncode == 0, done.stderr


@pytest.mark.parametrize("hook", HOOKS, ids=ids)
def test_a_label_with_nothing_after_it_still_blocks(hook):
    message = "\n".join(f"{f}:" for f in FIELDS)
    done = run(hook, message)
    assert done.returncode == 2 and "task" in done.stderr


@pytest.mark.parametrize("hook", HOOKS, ids=ids)
def test_an_incomplete_return_blocks_once_without_stop_hook_active(hook):
    done = run(hook, "task: x\nstatus: done")
    assert done.returncode == 2 and "work_completed" in done.stderr


@pytest.mark.parametrize("hook", HOOKS, ids=ids)
def test_stop_hook_active_exits_zero_even_for_a_return_that_would_block(hook):
    done = run(hook, "task: x\nstatus: done", stop_hook_active=True)
    assert done.returncode == 0, done.stderr
