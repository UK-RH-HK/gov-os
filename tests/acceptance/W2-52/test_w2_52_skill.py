"""The adopt skill names the A7 and A10 steps [CAP-44.f, CAP-44.h; DEC-741; DEC-738 item 1].

``template/governance/kernel/skills/adopt/SKILL.md`` is read as text. A "block" is a list item (with its
continuation lines) or a paragraph. W1-36 holds the skill's form (frontmatter, body size, no permission keys).
"""

from __future__ import annotations

import re

import pytest

import w2_52_support as gates

SKILL = gates.REPO_ROOT / "template/governance/kernel/skills/adopt/SKILL.md"
_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_MISSING = re.compile(r"\bmissing\b|\babsent\b|\bno (?:\w+ ){0,3}record\b|\bwithout (?:\w+ ){0,3}record\b", re.I)


def blocks():
    text = SKILL.read_text(encoding="utf-8")
    parts = text.split("\n---\n", 1)
    body = parts[1] if text.startswith("---") and len(parts) == 2 else text
    found, current = [], []
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or _ITEM.match(line):
            if current:
                found.append(" ".join(current))
            current = [line.strip()] if line.strip() and not line.lstrip().startswith("#") else []
        else:
            current.append(line.strip())
    if current:
        found.append(" ".join(current))
    return found


def _step(gate, *words):
    """The blocks that name ``gate`` and every one of ``words`` (case of letters ignored for words)."""
    return [block for block in blocks() if re.search(rf"\b{gate}\b", block)
            and all(re.search(word, block, re.I) for word in words)]


def test_the_adopt_skill_names_the_a7_step():
    """Success 1 and 2: a step names A7, its auditor, and what it checks (the A6 migration against the A3 path
    map and the A4 plan reviewed at A5)."""
    found = _step("A7", r"auditor", r"\bA6\b", r"\bA3\b", r"\bA4\b", r"\bA5\b")
    assert found, f"{SKILL.name}: no step names A7 with the Independent Auditor and A6, A3, A4 and A5"


def test_the_adopt_skill_names_the_a10_step():
    """Success 1 and 2: a step names A10, its auditor, and what it checks (A8's extraction and retirement, the
    derived state rebuilt from git, the canary of each index)."""
    found = _step("A10", r"auditor", r"\bA8\b", r"rebuil", r"canar")
    assert found, f"{SKILL.name}: no step names A10 with the Independent Auditor, A8, the rebuild and the canaries"


@pytest.mark.parametrize("gate", gates.GATES)
def test_the_adopt_skill_says_a_missing_gate_record_is_a_condition_not_met(gate):
    """Failure line: a missing record is a named failure, never healthy. The verdict is the auditor's (W2-28,
    W2-30); the skill is the method it follows, so it says that a missing record of the gate is a condition
    'not met'."""
    found = [block for block in _step(gate, r"not met") if _MISSING.search(block)]
    assert found, f"{SKILL.name}: no block says that a missing {gate} record is a condition 'not met'"
