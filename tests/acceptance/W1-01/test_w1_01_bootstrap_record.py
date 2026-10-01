"""W1-01: the written record in ``governance/project/bootstrap.md``.

The record must state the operator diff procedure and the interim install rule.
The checks look for the terms the KPI itself uses, within one section of the
document (a heading and the text under it, or the whole file if it has no
headings); they do not prescribe a layout.
"""

from __future__ import annotations

import re


def _sections(text):
    sections, current = [], []
    for line in text.splitlines():
        if line.lstrip().startswith("#") and current:
            sections.append("\n".join(current))
            current = []
        current.append(line)
    sections.append("\n".join(current))
    return sections


def _a_section_has(text, patterns):
    return any(
        all(re.search(pattern, section, re.I) for pattern in patterns)
        for section in _sections(text)
    )


def test_operator_diff_procedure_is_written(bootstrap_text):
    """KPI success 2: ``git diff --name-only`` against ``allowed_paths`` at each ticket close."""
    assert _a_section_has(
        bootstrap_text,
        [r"git diff --name-only", r"allowed_paths", r"\bclos(e|es|ed|ing|ure)\b"],
    ), (
        "no section of governance/project/bootstrap.md gives the operator diff procedure: "
        "`git diff --name-only` checked against the ticket's `allowed_paths` at ticket close"
    )


def test_interim_install_rule_is_recorded(bootstrap_text):
    """KPI success 3: install commands are denied, and nothing is installed, until W1-05."""
    assert _a_section_has(
        bootstrap_text,
        [r"\binstall", r"\b(deny|denies|denied)\b", r"\bW1-05\b"],
    ), (
        "no section of governance/project/bootstrap.md records the interim install rule: "
        "install commands denied until W1-05"
    )
