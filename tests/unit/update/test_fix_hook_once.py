"""W2-17 fix F4 (EXAMIN report 28): ``gov update`` leaves a kernel hook registered once. Builder evidence.

``dedupe`` keeps one entry per event, matcher and kernel hook program, whatever the command text; the project's own
hooks (those that run no ``governance/kernel/hooks/`` program) are never touched; ``dedupe_settings`` writes through the
journal only where something changed.
"""

from __future__ import annotations

import json
from pathlib import Path

from gov.update import core, hooks

NEW = 'python3 -I "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py"'
OLD = 'g=pinned; exec "$p" -E "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py"'
OWN = 'python3 -I "$CLAUDE_PROJECT_DIR/tools/context_watch.py"'


def _hook(command):
    return {"type": "command", "command": command, "timeout": 10}


def _group(*commands, matcher="Bash"):
    return {"matcher": matcher, "hooks": [_hook(c) for c in commands]}


def _commands(settings, event="PostToolUse"):
    return [[h["command"] for h in g["hooks"]] for g in settings["hooks"][event]]


def test_two_forms_become_the_last_one_and_the_projects_own_entry_stays_in_place():
    settings = {"hooks": {"PostToolUse": [_group(OWN), _group(OLD), _group(NEW)]}}
    after = hooks.dedupe(settings)
    assert _commands(after) == [[OWN], [NEW]]


def test_the_same_command_twice_in_one_group_is_left_once_and_the_group_stays():
    after = hooks.dedupe({"hooks": {"PostToolUse": [_group(NEW, NEW)]}})
    assert _commands(after) == [[NEW]]


def test_a_group_holding_another_hook_beside_the_duplicate_keeps_the_other():
    settings = {"hooks": {"PostToolUse": [_group(OLD, OWN), _group(NEW)]}}
    assert _commands(hooks.dedupe(settings)) == [[OWN], [NEW]]


def test_the_same_program_under_another_matcher_or_event_is_not_a_duplicate():
    settings = {"hooks": {"PostToolUse": [_group(NEW, matcher="Bash"), _group(NEW, matcher="Edit")],
                          "Stop": [_group(NEW, matcher="Bash")]}}
    assert hooks.dedupe(settings) is None


def test_nothing_is_changed_where_every_program_is_there_once():
    assert hooks.dedupe({"hooks": {"PostToolUse": [_group(NEW)]}}) is None
    assert hooks.dedupe({}) is None
    assert hooks.dedupe({"hooks": []}) is None


def test_the_input_is_not_changed_and_odd_shapes_are_left_alone():
    settings = {"hooks": {"PostToolUse": [_group(OLD), "odd", {"matcher": "Bash", "hooks": "odd"}, _group(NEW)]}}
    before = json.dumps(settings)
    after = hooks.dedupe(settings)
    assert json.dumps(settings) == before
    assert after["hooks"]["PostToolUse"] == ["odd", {"matcher": "Bash", "hooks": "odd"}, _group(NEW)]


class _Journal:
    def __init__(self):
        self.written = {}

    def write(self, rel, data, *rest):
        self.written[rel] = data


def test_dedupe_settings_writes_through_the_journal_only_a_changed_file(tmp_path: Path):
    (tmp_path / ".claude").mkdir()
    path = tmp_path / core.SETTINGS
    path.write_text(json.dumps({"hooks": {"PostToolUse": [_group(OLD), _group(NEW)]}}), encoding="utf-8")
    journal = _Journal()
    hooks.dedupe_settings(tmp_path, journal)
    written = json.loads(journal.written[core.SETTINGS])
    assert _commands(written) == [[NEW]]
    assert journal.written[core.SETTINGS].endswith(b"\n")

    path.write_text(json.dumps({"hooks": {"PostToolUse": [_group(NEW)]}}), encoding="utf-8")
    again = _Journal()
    hooks.dedupe_settings(tmp_path, again)
    assert again.written == {}


def test_dedupe_settings_leaves_a_missing_or_unreadable_file_alone(tmp_path: Path):
    journal = _Journal()
    hooks.dedupe_settings(tmp_path, journal)
    (tmp_path / ".claude").mkdir()
    (tmp_path / core.SETTINGS).write_text("not json", encoding="utf-8")
    hooks.dedupe_settings(tmp_path, journal)
    assert journal.written == {}
