"""S14 and F6: the kernel template's settings carry one narrow allow rule, ``Bash(gov launch:*)``.

Rewrite-Reason: DEC-1217 (6), W2-208 K1: the kit writes no allow line (EMERGENCY-2 2.4: no permission prompts, two deny
lines only), so the template's settings carry no allow rule at all; S14 now holds the allow list empty and F6 keeps its
half that still holds: no raw ``claude`` launch is admitted (nothing is). The ``gov launch`` half of F6 (every launch
admitted by the narrow rule) retires with the prompt it answered.

S14: the kernel template's settings carry one narrow allow rule, Bash(gov launch:*) [DEC-715]. F6: a raw claude
launch stays unallowed in the template (read with DEC-715: the failure is a template whose only launch is a raw
``claude`` command, unallowed, so every launch is blocked; the fix is the one narrow rule for ``gov launch``, which
admits no raw ``claude`` launch beside it).

The template is ``template/governance/kernel/settings.json``, read as a file. A ``Bash(...)`` rule is read as the
CLI reads it: ``Bash`` or ``Bash(*)`` admits every command, ``Bash(<prefix>:*)`` a command that starts with the
prefix, ``Bash(<command>)`` that command alone.
"""

from __future__ import annotations

import json
import re

import w2_56_support as s

RULE = "Bash(gov launch:*)"
LAUNCHES = ("gov launch engineer DAEO-zw56", "gov launch lead DAEO-zw56", "gov launch independent-test-designer "
            "DAEO-zw56 -- -p hello")
RAW = ("claude", "claude -p hello", "claude --settings {} -p hello", "~/.local/bin/claude -p hello",
       "/home/user/.local/bin/claude --dangerously-skip-permissions", "env GOV_ROLE=engineer claude -p hello")


def _template() -> dict:
    data = json.loads(s.TEMPLATE_SETTINGS.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "the template's settings are not a JSON object"
    return data


def _allow(data) -> list:
    permissions = data.get("permissions") or {}
    return list(permissions.get("allow") or []) if isinstance(permissions, dict) else []


def _admits(rule: str, command: str) -> bool:
    match = re.fullmatch(r"\s*Bash(?:\((.*)\))?\s*", str(rule), re.S)
    if not match:
        return False
    spec = match.group(1)
    if spec is None or spec.strip() in ("", "*"):
        return True
    if spec.endswith(":*"):
        return command.startswith(spec[:-2])
    if spec.endswith("*"):
        return command.startswith(spec[:-1])
    return command == spec


def test_s14_the_template_carries_one_allow_rule_bash_gov_launch():
    """Rewrite-Reason: DEC-1217 (6), W2-208 K1: no allow rule (it was exactly ``[RULE]``)."""
    allow = _allow(_template())
    assert allow == [], f"the template's permissions.allow is {allow}, not empty (no allow line the kit wrote)"


def test_f6_the_template_admits_gov_launch_and_no_raw_claude_launch():
    """Rewrite-Reason: DEC-1217 (6), W2-208 K1: the template admits nothing, so no raw claude launch either; the
    assertion that every ``gov launch`` was admitted retires with the allow rule."""
    allow = _allow(_template())
    assert RULE not in allow, f"the template's allow rules {allow} still carry {RULE}"
    raw = [command for command in RAW if any(_admits(rule, command) for rule in allow)]
    assert not raw, f"the template's allow rules {allow} admit a raw claude launch: {raw}"
