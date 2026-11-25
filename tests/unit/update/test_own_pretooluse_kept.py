"""A project's own PreToolUse entries stay beside the kit's model hook through the merge and the dedupe (MR-4)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from gov.adapters.merge import merge_settings, unmerge_value  # noqa: E402
from gov.update import hooks  # noqa: E402

OWN = {"matcher": "Read", "hooks": [{"type": "command", "command": 'python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/own_pre.py"'}]}
KIT = {"matcher": "Agent|Task", "hooks": [{"type": "command", "timeout": 10, "command":
       'h="$CLAUDE_PROJECT_DIR/governance/kernel/hooks/agent_model.py"; exec "$p" -E "$h"'}]}


def test_the_merge_keeps_an_own_pretooluse_group_first_and_adds_the_kit_s():
    merged = merge_settings({"hooks": {"PreToolUse": [OWN]}}, {"hooks": {"PreToolUse": [KIT]}})
    assert merged["hooks"]["PreToolUse"] == [OWN, KIT]


def test_the_unmerge_of_the_old_generation_leaves_an_own_group():
    assert unmerge_value({"hooks": {"PreToolUse": [OWN, KIT]}}, {"hooks": {"PreToolUse": [KIT]}}) == {
        "hooks": {"PreToolUse": [OWN]}}


def test_the_dedupe_leaves_an_own_pretooluse_program_under_dot_claude_hooks_alone():
    twice = {"hooks": {"PreToolUse": [OWN, KIT, KIT]}}
    assert hooks.dedupe(twice)["hooks"]["PreToolUse"] == [OWN, KIT]
    assert hooks.dedupe({"hooks": {"PreToolUse": [OWN, KIT]}}) is None
