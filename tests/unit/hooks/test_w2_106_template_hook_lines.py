"""W2-106 (DAEO-0mtg): the template's hook lines run the installed gov's own interpreter with ``-E``.

Builder regression evidence (DEC-966 item 2, DEC-822, W2-59's form) on ``template/.rulesync/hooks.jsonc``.

Rewrite-Reason: EMERGENCY-2 §2 (the guard retired, §2.2 and §6.1) and DAEO-057v (W2-18) S3, S4. The kernel hooks run
the pinned gov, never a product's own package named gov (S3), so the lifecycle lines find the pin first.

Rewrite-Reason: EMERGENCY-2 §6.1 (DAEO-gr7t): the guard's three lines (``pretooluse.py`` in ``preToolUse``,
``posttooluse.py`` in ``postToolUse`` and ``postToolUseFailure``) left the template with the guard, and the kernel
settings register no hook; their cases went with them. What stays: the four lifecycle lines find the pin first, and
the after-call event holds the context watch alone.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SETTINGS = REPO_ROOT / "template" / "governance" / "kernel" / "settings.json"
SOURCE = REPO_ROOT / "template" / ".rulesync" / "hooks.jsonc"

LIFECYCLE = {
    "sessionStart": "sessionstart.py",
    "stop": "stop.py",
    "preCompact": "precompact.py",
    "subagentStop": "subagentstop.py",
}
WATCH_PROGRAM = "context_watch.py"


def _load_jsonc(path):
    text = "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                     if not line.lstrip().startswith("//"))
    return json.loads(text)


def _runs(entry, program):
    """Whether the entry's command runs ``program`` of the kernel's hooks folder (``stop.py`` is not ``subagentstop.py``)."""
    return f"/hooks/{program}\"" in entry.get("command", "")


def source_entries(key, program):
    return [e for e in _load_jsonc(SOURCE)["hooks"].get(key, []) if e.get("type") == "command" and _runs(e, program)]


def source_line(key):
    entries = source_entries(key, LIFECYCLE[key])
    assert len(entries) == 1, f"{SOURCE}: {key} holds {len(entries)} command entries running {LIFECYCLE[key]}; one is expected"
    return entries[0]["command"]


def test_no_guard_line_is_shipped():
    hooks = _load_jsonc(SOURCE)["hooks"]
    assert "preToolUse" not in hooks and "postToolUseFailure" not in hooks, sorted(hooks)
    assert not source_entries("postToolUse", "posttooluse.py")
    assert "hooks" not in json.loads(SETTINGS.read_text(encoding="utf-8"))


def test_post_tool_use_holds_the_context_watch_line_and_no_other():
    """The after-call event's one entry: the context watch's (matcher ``Bash``, timeout 10)."""
    entries = [e for e in _load_jsonc(SOURCE)["hooks"]["postToolUse"] if e.get("type") == "command"]
    assert len(entries) == 1, f"{SOURCE}: postToolUse holds {len(entries)} command entries; one is expected"
    watch = source_entries("postToolUse", WATCH_PROGRAM)
    assert len(watch) == 1, f"{SOURCE}: postToolUse holds {len(watch)} entries running {WATCH_PROGRAM}; one is expected"
    assert watch[0].get("matcher") == "Bash" and watch[0].get("timeout") == 10 and type(watch[0]["timeout"]) is int, (
        f"the {WATCH_PROGRAM} entry is {watch[0]!r}: matcher Bash and timeout 10 are expected")


@pytest.mark.parametrize("key", list(LIFECYCLE))
def test_the_lifecycle_lines_find_the_pin_first(key):
    line = source_line(key)
    assert not re.search(r"(^|[;&|\s])python3?\s", line), f"{key} runs a bare python3: {line!r}"
    assert f'h="$CLAUDE_PROJECT_DIR/governance/kernel/hooks/{LIFECYCLE[key]}"' in line, (
        f"{key} does not run the product's own program {LIFECYCLE[key]}: {line!r}")
    pin = line.find('g="$c/gov/bin/gov"')
    home = line.find('g="$HOME/.local/bin/gov"')
    path = line.find("command -v gov")
    assert "rev-parse --path-format=absolute --git-common-dir" in line, f"{key} does not look up the git common dir"
    assert 0 <= pin < home < path, f"{key} does not look for the pin, then $HOME/.local/bin/gov, then PATH: {line!r}"
    assert '"$p" -E "$h"' in line, f"{key} does not run its program with the gov's interpreter and -E: {line!r}"
