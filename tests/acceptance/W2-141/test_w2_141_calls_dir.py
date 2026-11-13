"""W2-141 S4 (DEC-1108 (5), DEC-1109 (2)): the suites write no real guard call log.

The live hook ``.claude/hooks/pretooluse.py`` appends one line per decision to ``~/.gov-os/guard-calls/<UTC
day>.jsonl``, or to ``GOV_GUARD_CALLS_DIR`` (an absolute path) when it is set (ACT-GUARD-CALLLOG-1, its ``CALLS_ENV``).
``tests/conftest.py`` gives every test a folder of its own under the run's base folder. This case runs the tree's
live hook once as a process, with the test's own environment (so the conftest's variable), a planted project and a
planted ``HOME``, and checks where the line went.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import w2_141_hook_support as hook_support
import w2_141_support as support

CALLS_ENV = "GOV_GUARD_CALLS_DIR"
HOOK_REL = ".claude/hooks/pretooluse.py"


def _run_live_hook(tree, project, event):
    """The tree's live hook on one event, as Claude Code runs it: the event on standard input, the test's own
    environment (PYTHON* replaced by the tree's src), the planted HOME, role and project."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update(PYTHONPATH=str(Path(tree) / "src"), PYTHONDONTWRITEBYTECODE="1", HOME=str(project.home),
               GOV_ROLE=support.ORCHESTRATOR, GOV_TICKET=support.TICKET, CLAUDE_PROJECT_DIR=str(project.root))
    return subprocess.run([sys.executable, str(Path(tree) / HOOK_REL)], input=json.dumps(event),
                          capture_output=True, text=True, env=env, cwd=str(project.root), timeout=60)


def test_s4_guard_the_conftest_gives_each_test_an_absolute_folder_under_the_base_temp(tmp_path_factory):
    where = os.environ.get(CALLS_ENV)
    assert where, f"{CALLS_ENV} is not set for this test: tests/conftest.py sets it for every test (S4)"
    assert os.path.isabs(where), f"{CALLS_ENV}={where!r} is not an absolute path (the hook ignores it)"
    base = tmp_path_factory.getbasetemp().resolve()
    assert Path(where).resolve().is_relative_to(base), f"{CALLS_ENV}={where!r} is not under the base temp {base}"
    real = Path(os.path.realpath(os.path.expanduser("~"))) / ".gov-os" / "guard-calls"
    assert Path(where).resolve() != real, f"{CALLS_ENV} names the real log folder {real}"


def test_s4_a_live_hook_call_s_line_lands_in_the_test_s_own_folder(tmp_path):
    tree = hook_support.tree_under_test()
    assert (tree / HOOK_REL).is_file(), f"premise: no live hook at {tree / HOOK_REL}"
    given = os.environ.get(CALLS_ENV) or ""
    where = Path(given) if os.path.isabs(given) else None
    assert where is None or not where.exists(), f"premise: the test's own folder {where} exists before the hook ran"
    project = support.make_project(tmp_path / "w2-141-s4")
    hook_support.git_init(project.root)
    event = {"session_id": "w2-141-s4", "cwd": str(project.root), "hook_event_name": "PreToolUse",
             "tool_name": "Read", "tool_input": {"file_path": str(project.root / "README.md")}}

    done = _run_live_hook(tree, project, event)

    label = f"[hook {tree / HOOK_REL}] exit {done.returncode}, stderr {done.stderr[-600:]!r}: "
    assert done.returncode in (0, 2), label + "the hook did not decide"
    planted = project.home / ".gov-os" / "guard-calls"
    assert not planted.exists(), label + (f"the hook wrote the HOME's log folder {planted}, not {CALLS_ENV} "
                                          f"({given!r}): the test's environment does not move the log")
    assert where is not None, label + f"{CALLS_ENV} is not an absolute path in the test's environment ({given!r})"
    days = sorted(where.glob("*.jsonl")) if where.is_dir() else []
    assert len(days) == 1, label + f"no day file (or more than one) in {where}: {days}"
    lines = days[0].read_text(encoding="ascii").splitlines()
    assert len(lines) == 1, label + f"{len(lines)} lines in {days[0]}, one hook call made"
    row = json.loads(lines[0])
    assert row.get("tool") == "Read" and row.get("decision") in ("allow", "deny", "ask"), label + repr(row)
