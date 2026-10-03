"""W1-06 — ccusage: installed, pinned, recorded.

KPI success 1: "ccusage installed and pinned through a DEC-083 decision package
and recorded in the registry" (DEC-086: ccusage reads the session logs for the
governance share's denominator, CAP-40).

DEC-083: the package names the tool, its exact version, its checksum and its
uninstall command; the install is recorded with version, sha256, install and
uninstall commands, date and approving decision.

The two tests of what is on this machine are ``local_only``. They read the
version from the installed package's own ``package.json``; nothing is installed,
downloaded or removed.

Revised in the second batch (before implementation): DEC-192 approves the
install with the npm of Node v22.23.3, whose ``bin`` is not on ``PATH`` (the
nvm default stays v18.20.8, ADR-0002 §2). The two ``local_only`` tests looked
for ``ccusage`` on ``PATH``; they now look under ``~/.nvm/versions/node/v22.23.3``.
What DEC-192 and DEC-197 add is in ``test_w1_06_install_approvals.py``.
"""

from __future__ import annotations

import datetime
import re

import pytest

import w1_06_support as support

NAMES = ("ccusage",)


def _entry(registry):
    return support.one(registry, NAMES)


def test_ccusage_is_recorded_in_the_registry(registry):
    _entry(registry)


def test_ccusage_is_pinned_to_one_exact_version(registry):
    version = str(_entry(registry).get("version", "")).strip()
    assert support.EXACT_VERSION.fullmatch(version), (
        f"the ccusage entry's version is {version!r}: a pin is one exact version, not a range, a tag or `latest`"
    )


def test_the_recorded_install_command_installs_the_pinned_version(registry):
    entry = _entry(registry)
    install = str(entry.get("install", ""))
    version = support.norm_version(entry.get("version", ""))
    assert "ccusage" in install.lower(), f"the ccusage entry's install command does not name ccusage: {install!r}"
    assert version and re.search(rf"(?<![0-9.]){re.escape(version)}(?![0-9])", install), (
        f"the ccusage entry's install command does not name the pinned version {version!r}: {install!r}"
    )


def test_the_recorded_uninstall_command_removes_ccusage(registry):
    uninstall = str(_entry(registry).get("uninstall", ""))
    assert "ccusage" in uninstall.lower(), (
        f"the ccusage entry's uninstall command does not name ccusage: {uninstall!r}"
    )


def test_ccusage_carries_a_sha256_digest(registry):
    value = str(_entry(registry).get("sha256", "")).strip()
    assert support.SHA256.fullmatch(value), f"the ccusage entry's sha256 is not a SHA-256 digest: {value!r}"


def test_ccusage_was_approved_by_an_owner_decision_of_the_register(registry, decisions):
    approved_by = str(_entry(registry).get("approved_by", "")).strip()
    assert support.DECISION_ID.fullmatch(approved_by), (
        f"the ccusage entry's approved_by is {approved_by!r}, not a decision id"
    )
    assert approved_by in decisions, f"{approved_by}, which approves ccusage, is not in {support.REGISTER_REL}"
    decision = decisions[approved_by]
    assert decision.accepted_by_owner, (
        f"{approved_by}, which approves ccusage, is not accepted by the owner (status: {decision.status!r})"
    )


def test_ccusage_was_not_installed_before_its_approval(registry, decisions):
    """DEC-083: the orchestrator "installs only after the owner's explicit approval"."""
    entry = _entry(registry)
    decision = decisions.get(str(entry.get("approved_by", "")).strip())
    assert decision is not None, f"the ccusage entry's approving decision is not in {support.REGISTER_REL}"
    assert decision.date, f"{decision.id} carries no date the install date can be compared with"
    installed = datetime.date.fromisoformat(str(entry.get("date", "")).strip()[:10])
    approved = datetime.date.fromisoformat(decision.date)
    assert installed >= approved, (
        f"the registry dates the ccusage install {installed}, before its approval {decision.id} of {approved}"
    )


NOT_INSTALLED = (
    f"ccusage is not a global package of ~/{support.NODE_22_REL}: it is not installed where DEC-192 installs it"
)


@pytest.mark.local_only
def test_ccusage_is_installed_on_this_machine(registry):
    """Revised for DEC-192: the approved install is under Node v22.23.3, which is not the ``node`` on PATH."""
    path, _ = support.node_22_package("ccusage", "ccusage")
    assert path is not None, NOT_INSTALLED


@pytest.mark.local_only
def test_the_installed_ccusage_is_the_pinned_version(registry):
    """Revised for DEC-192: the version is read from the package under Node v22.23.3."""
    pinned = support.norm_version(_entry(registry).get("version", ""))
    path, found = support.node_22_package("ccusage", "ccusage")
    assert path is not None, NOT_INSTALLED
    assert found is not None and support.norm_version(found) == pinned, (
        f"{path} is ccusage {found!r}; the registry pins {pinned!r}"
    )
