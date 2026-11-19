"""W2-201 S8: no inbox waiter and no idle-check wake-up hook is written by the product.

The hooks the product ships (``template/.rulesync/hooks.jsonc``, ``template/governance/kernel/settings.json``, this
repository's ``.rulesync/hooks.jsonc`` and ``.claude/settings.json``) and the ``--settings`` of a worker launch hold no
hook whose command names ``stop_waiter_check``, ``stop_idle_check``, ``gov session-watch`` or ``gov msg wait``. A worker
launch whose repository settings file (``.claude/settings.json`` or ``.claude/settings.local.json``) holds such a hook
in a ``Stop``, ``SubagentStop`` or ``UserPromptSubmit`` entry is refused, ``LAUNCH_REFUSED``, naming the file and the
command; a launch with the kernel hooks only (this repository's own ``.claude/settings.json`` hooks) starts.
"""

from __future__ import annotations

import json
import re

import pytest

import w2_201_support as k

s = k.s
WAKE = ("stop_waiter_check", "stop_idle_check", "gov session-watch", "gov msg wait")
SHIPPED = ("template/.rulesync/hooks.jsonc", "template/governance/kernel/settings.json", ".rulesync/hooks.jsonc",
           ".claude/settings.json")


def _commands(node):
    """Every ``command`` string anywhere in a hooks or settings structure."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "command" and isinstance(value, str):
                yield value
            else:
                yield from _commands(value)
    elif isinstance(node, list):
        for item in node:
            yield from _commands(item)


def _load(text):
    """JSON, or JSONC with whole-line ``//`` comments."""
    try:
        return json.loads(text)
    except ValueError:
        return json.loads("\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//")))


def _wake_commands(data):
    return [(word, command) for command in _commands(data) for word in WAKE if word in command]


@pytest.mark.parametrize("rel", SHIPPED)
def test_s8_a_shipped_hooks_file_holds_no_wake_up_hook(rel):
    """Guard on the base."""
    data = _load((k.REPO_ROOT / rel).read_text(encoding="utf-8"))
    found = _wake_commands(data.get("hooks", data) if isinstance(data, dict) else data)
    assert not found, f"{rel} holds a wake-up hook: {found}"


def _hooks_entry(event, command):
    return {event: [{"hooks": [{"type": "command", "command": command}]}]}


PLANTS = {
    "stop_waiter_check": ("Stop", ".claude/settings.json",
                          'python3 "$CLAUDE_PROJECT_DIR/governance/project/orchestration/tools/stop_waiter_check.py"'),
    "stop_idle_check": ("SubagentStop", ".claude/settings.json",
                        'python3 "$CLAUDE_PROJECT_DIR/governance/project/orchestration/tools/stop_idle_check.py"'),
    "gov session-watch": ("UserPromptSubmit", ".claude/settings.local.json", "gov session-watch --once"),
    "gov msg wait": ("Stop", ".claude/settings.local.json", "gov msg wait --timeout 600"),
}


@pytest.mark.parametrize("word", WAKE)
def test_s8_a_worker_launch_with_a_wake_up_hook_in_the_repository_settings_is_refused(project, launch, word):
    event, rel, command = PLANTS[word]
    s.b.rewrite_settings(project, lambda data: data.setdefault("hooks", {}).update(_hooks_entry(event, command)),
                         rel=rel)
    tk = s.ticket(project, k.ENGINEER, "C2")
    s.refused(launch(k.ENGINEER, tk), rel, word)


def _kernel_hooks():
    return json.loads((k.REPO_ROOT / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]


def test_s8_a_worker_launch_with_the_kernel_hooks_only_starts_and_its_settings_hold_no_wake_up_hook(project, launch):
    """Guard on the base: the repository's own hooks (context watch, precompact, session start, stop, subagent stop,
    the helper model hook) in the fixture's ``.claude/settings.json``; the session's ``--settings`` names no wake-up
    command."""
    s.b.rewrite_settings(project, lambda data: data.update({"hooks": _kernel_hooks()}))
    tk = s.ticket(project, k.ENGINEER, "C2")
    result = launch(k.ENGINEER, tk)
    s.b.assert_launched(result)
    found = _wake_commands(result.settings())
    assert not found, f"the worker's --settings holds a wake-up hook: {found}"
    assert not any(re.search(word, entry) for word in WAKE for entry in result.session()["settings"]), (
        "the worker's --settings text names a wake-up command")
