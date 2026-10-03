"""W1-48 — Claude Code is a registry entry, pinned at 2.1.285 or later, on a recorded owner approval.

KPI success 1: "Claude Code is recorded in governance/project/tool-registry.yaml
pinned at 2.1.285 or later, with install and uninstall commands, date and
approving decision; the upgrade is installed by the orchestrator through a
DEC-083 decision package (DEC-157) [CAP-25.d]".

KPI failure 3: "The pin is raised without a recorded owner approval".

CAP-25.d: "Claude Code is a tool registry entry pinned at 2.1.285 or later;
raising the pin is an orchestrator install under DEC-083".

DEC-203 answers "installed by the orchestrator": the owner made the install as
an owner action, outside agent sessions, and DEC-203 is the recorded approval.
So the tests ask for the recorded owner approval, not for who ran the command.

DEC-197: the approval is a register entry of its own that names the tool and
its exact version, and ``approved_by`` cites it. The tests do not fix the
entry's id or the version: they read what the registry cites, so that a later
raise of the pin needs a new approval and no new test.
"""

from __future__ import annotations

import datetime
import re

import w1_48_support as support

NAMES = support.CLAUDE_CODE


def _entry(registry):
    return support.one(registry, NAMES)


def _raised(version):
    """The next patch version: ``2.1.288`` gives ``2.1.289``."""
    parts = list(support.version_key(version))
    parts[-1] += 1
    return ".".join(str(part) for part in parts)


# --------------------------------------------------------------------------
# Success 1 / CAP-25.d: the entry
# --------------------------------------------------------------------------

def test_claude_code_is_recorded_in_the_registry(registry):
    _entry(registry)


def test_claude_code_is_pinned_to_one_exact_version(registry):
    version = support.field(_entry(registry), "version")
    assert support.EXACT_VERSION.fullmatch(version), (
        f"the Claude Code entry's version is {version!r}: a pin is one exact version, not a range, a tag or `latest`"
    )


def test_the_claude_code_pin_is_2_1_285_or_later(registry):
    version = support.field(_entry(registry), "version")
    key = support.version_key(version)
    assert key is not None, f"the Claude Code entry's version {version!r} cannot be compared with {support.FLOOR}"
    assert key >= support.version_key(support.FLOOR), (
        f"the registry pins Claude Code at {version}; strict sandbox mode needs {support.FLOOR} or later (DEC-153)"
    )


def test_the_recorded_install_command_installs_the_pinned_version(registry):
    entry = _entry(registry)
    install = support.field(entry, "install")
    version = support.norm_version(entry.get("version", ""))
    assert "claude" in install.lower(), f"the Claude Code entry's install command does not name claude: {install!r}"
    assert version and support.names_version(install, version), (
        f"the Claude Code entry's install command does not name the pinned version {version!r}: {install!r}"
    )


def test_the_recorded_uninstall_command_removes_claude_code(registry):
    entry = _entry(registry)
    uninstall = support.field(entry, "uninstall")
    assert uninstall, "the Claude Code entry has no uninstall command"
    assert uninstall != support.field(entry, "install"), (
        f"the Claude Code entry's uninstall command is its install command: {uninstall!r}"
    )
    assert "claude" in uninstall.lower(), (
        f"the Claude Code entry's uninstall command does not name claude: {uninstall!r}"
    )


def test_claude_code_carries_a_sha256_digest(registry):
    """DEC-196: the binary's own digest; which binary is checked by a ``local_only`` case of ``test_w1_48_cli.py``."""
    value = support.field(_entry(registry), "sha256")
    assert support.SHA256.fullmatch(value), f"the Claude Code entry's sha256 is not a SHA-256 digest: {value!r}"


def test_claude_code_carries_a_calendar_date(registry):
    value = support.field(_entry(registry), "date")
    assert support.ISO_DATE.match(value), f"the Claude Code entry's date is not YYYY-MM-DD: {value!r}"
    datetime.date.fromisoformat(value[:10])


# --------------------------------------------------------------------------
# Success 1 ("approving decision", "through a DEC-083 decision package") and failure 3
# --------------------------------------------------------------------------

def test_claude_code_was_approved_by_an_owner_decision_of_the_register(registry, decisions):
    cited = support.approved_by(_entry(registry))
    assert support.DECISION_ID.fullmatch(cited), f"the Claude Code entry's approved_by is {cited!r}, not a decision id"
    assert cited in decisions, f"{cited}, which approves Claude Code, is not in {support.REGISTER_REL}"
    assert decisions[cited].accepted_by_owner, (
        f"{cited}, which approves Claude Code, is not accepted by the owner (status: {decisions[cited].status!r})"
    )


def test_the_approval_names_claude_code_and_the_pinned_version(registry, decisions):
    """DEC-197: "its own register entry naming the tool and its exact version"."""
    entry = _entry(registry)
    decision = decisions.get(support.approved_by(entry))
    assert decision is not None, f"the Claude Code entry's approving decision is not in {support.REGISTER_REL}"
    version = support.norm_version(entry.get("version", ""))
    text = support.own_text(decision)
    assert support.names_tool(text, "claude code"), (
        f"{decision.id}, cited as the approval of Claude Code, does not name Claude Code: {decision.title!r}"
    )
    assert version and support.names_version(text, version), (
        f"{decision.id}, cited as the approval of Claude Code {version}, does not name the version {version}"
    )


def test_the_approval_is_made_under_dec_083(registry, decisions):
    """KPI success 1: "through a DEC-083 decision package". The approving entry's status line says so."""
    decision = decisions.get(support.approved_by(_entry(registry)))
    assert decision is not None, f"the Claude Code entry's approving decision is not in {support.REGISTER_REL}"
    assert re.search(r"DEC-083(?!\d)", decision.status), (
        f"{decision.id}, cited as the approval of Claude Code, is not recorded under DEC-083: {decision.status!r}"
    )


def test_the_approval_is_claude_codes_own(registry, decisions):
    """DEC-197: the decision that approves this install approves no other entry of the registry."""
    entry = _entry(registry)
    cited = support.approved_by(entry)
    shared = sorted(support.norm_name(other.get("name", "")) for other in support.entries(registry)
                    if other is not entry and support.approved_by(other) == cited)
    assert shared == [], f"{cited} is cited as the approval of Claude Code and also of: {shared}"


def test_claude_code_is_not_dated_before_its_approval(registry, decisions):
    """DEC-083: an install is made "only after the owner's explicit approval"."""
    entry = _entry(registry)
    decision = decisions.get(support.approved_by(entry))
    assert decision is not None, f"the Claude Code entry's approving decision is not in {support.REGISTER_REL}"
    assert decision.date, f"{decision.id} carries no date the install date can be compared with"
    recorded = datetime.date.fromisoformat(support.field(entry, "date")[:10])
    approved = datetime.date.fromisoformat(decision.date)
    assert recorded >= approved, (
        f"the registry dates Claude Code {recorded}, before its approval {decision.id} of {approved}"
    )


def test_the_pin_as_recorded_has_a_recorded_owner_approval(registry, decisions):
    """Failure 3, the entry as it stands: every condition of DEC-197 holds at once."""
    entry = _entry(registry)
    problems = support.approval_problems(entry, registry, decisions, NAMES)
    assert problems == [], f"the Claude Code pin has no recorded owner approval: {problems}"


def test_a_raised_pin_is_not_covered_by_the_approval_of_the_recorded_one(registry, decisions):
    """Failure 3, the raise: the same entry one patch version higher is refused.

    The approval names one exact version, so raising the pin without a new
    register entry leaves ``approved_by`` pointing at a decision that does not
    name the new version.
    """
    entry = _entry(registry)
    version = support.field(entry, "version")
    assert support.version_key(version) is not None, f"the Claude Code entry's version {version!r} cannot be raised"
    raised = dict(entry, version=_raised(version))
    registry_raised = {"tools": [raised if other is entry else other for other in support.entries(registry)]}
    problems = support.approval_problems(raised, registry_raised, decisions, NAMES)
    assert any("does not name the version" in problem for problem in problems), (
        f"{support.approved_by(entry)} would also pass as the approval of Claude Code {raised['version']}: "
        "a raise of the pin would go through without a new owner approval"
    )
