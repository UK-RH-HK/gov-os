"""W1-01: the written record in ``governance/project/bootstrap.md``.

The record must state the operator diff procedure and the interim install rule.
The checks look for the terms the KPI itself uses, within one section of the
document (a heading and the text under it, or the whole file if it has no
headings); they do not prescribe a layout.
"""

from __future__ import annotations

import datetime
import re

import pytest

INSTALL = r"\binstall"
DENY = r"\bden(y|ies|ied|ial)\b"

# KD-2 (owner answer): the settings files of every agent session folder, and the
# repository's own. The operator console acts as the owner and is not listed.
SESSION_SETTINGS = {
    "w1-build": r"(?<![\w-])w1-build(?![\w-])",
    "w1-tests": r"(?<![\w-])w1-tests(?![\w-])",
    "s1": r"(?<![\w-])s1(?![\w-])",
    "s1a": r"(?<![\w-])s1a(?![\w-])",
    "the repository's .claude/settings.json": (
        r"(?<!w1-build/)(?<!w1-tests/)(?<!s1/)(?<!s1a/)\.claude/settings\.json"
    ),
}

# KD-4 (owner answer): one recorded live denied attempt per class. A record is
# one line holding an ISO date, the tool, the path or command attempted, and
# the denial. The path is a concrete one, not the pattern.
FILE_ATTEMPT_CLASSES = [
    pytest.param(r"(^|/)tests/acceptance/[^*]+$", id="tests-acceptance"),
    pytest.param(r"(^|/)\.env[^/*]*$", id="dotenv"),
    pytest.param(r"(^|/)[^/*]+\.pem$", id="pem"),
    pytest.param(r"(^|/)[^/*]+\.key$", id="key"),
    pytest.param(r"(^|/)config/secrets[^/*]*$", id="config-secrets"),
]
INSTALL_ATTEMPT = r"\b(pip3?|npm|cargo|apt|apt-get|uv)\b[^|`]*\binstall\b"


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
        [INSTALL, DENY, r"\bW1-05\b"],
    ), (
        "no section of governance/project/bootstrap.md records the interim install rule: "
        "install commands denied until W1-05"
    )


def test_install_rule_lists_every_agent_session_settings_file(bootstrap_text):
    """KPI success 3 (KD-2): the record names each session settings file that denies installs."""
    candidates = [
        section
        for section in _sections(bootstrap_text)
        if re.search(INSTALL, section, re.I) and re.search(DENY, section, re.I)
    ]
    assert candidates, "no section of governance/project/bootstrap.md says installs are denied"
    missing = min(
        ([name for name, pattern in SESSION_SETTINGS.items() if not re.search(pattern, section)]
         for section in candidates),
        key=len,
    )
    assert not missing, (
        "the install-rule section of governance/project/bootstrap.md does not list the "
        f"session settings of: {', '.join(missing)}"
    )


def _has_real_date(line):
    for year, month, day in re.findall(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)", line):
        try:
            datetime.date(int(year), int(month), int(day))
        except ValueError:
            continue
        return True
    return False


def _tokens(line):
    return [token.rstrip(".:;") for token in re.split(r"[\s|`'\"()<>,]+", line) if token]


def _attempt_lines(text, tool_pattern):
    return [
        line
        for line in text.splitlines()
        if _has_real_date(line) and re.search(tool_pattern, line) and re.search(DENY, line, re.I)
    ]


@pytest.mark.parametrize("path_pattern", FILE_ATTEMPT_CLASSES)
def test_a_denied_attempt_is_recorded_for_each_path_class(bootstrap_text, path_pattern):
    """KPI success 1 (KD-4): "verified by one denied attempt each", on the record."""
    lines = _attempt_lines(bootstrap_text, r"\b(Edit|Write)\b")
    assert any(
        re.search(path_pattern, token) for line in lines for token in _tokens(line)
    ), (
        "governance/project/bootstrap.md has no line recording a denied attempt for this class "
        "(one line: ISO date, Edit or Write, the concrete path attempted, the denial); "
        f"path must match {path_pattern}"
    )


def test_a_denied_install_attempt_is_recorded(bootstrap_text):
    """KPI success 3 (KD-4): one recorded denied install command."""
    lines = _attempt_lines(bootstrap_text, r"\bBash\b")
    assert any(re.search(INSTALL_ATTEMPT, line) for line in lines), (
        "governance/project/bootstrap.md has no line recording a denied install attempt "
        "(one line: ISO date, Bash, the package-manager install command, the denial)"
    )
