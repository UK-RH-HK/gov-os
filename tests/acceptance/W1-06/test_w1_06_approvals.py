"""W1-06 — no tool is in the registry without a recorded owner approval.

KPI failure 1: "Any tool installed without a recorded owner approval".

DEC-083: every install is recorded in the tool registry with its "approving
decision"; the schema's ``approved_by`` holds that decision's id (DEC-121). The
approval is recorded when that id is an entry of ``docs/DECISION_REGISTER.md``
whose status is ``ACCEPTED (owner…)``.

Whether the approving decision must also name the tool and its version is a
decision package in the README, not a test.
"""

from __future__ import annotations

import w1_06_support as support


def _approvals(registry):
    return [(support.norm_name(entry.get("name", f"entry {index}")), str(entry.get("approved_by", "")).strip())
            for index, entry in enumerate(support.entries(registry))]


def test_every_entry_names_one_decision_as_its_approval(registry):
    assert support.entries(registry), f"{support.REGISTRY_REL} records no tool"
    wrong = [f"{name}: {approved_by!r}" for name, approved_by in _approvals(registry)
             if not support.DECISION_ID.fullmatch(approved_by)]
    assert wrong == [], f"entries of {support.REGISTRY_REL} whose approved_by is not one decision id: {wrong}"


def test_every_approving_decision_is_in_the_register(registry, decisions):
    assert support.entries(registry), f"{support.REGISTRY_REL} records no tool"
    unknown = [f"{name}: {approved_by}" for name, approved_by in _approvals(registry) if approved_by not in decisions]
    assert unknown == [], (
        f"entries of {support.REGISTRY_REL} approved by a decision that {support.REGISTER_REL} does not hold: {unknown}"
    )


def test_every_approving_decision_is_accepted_by_the_owner(registry, decisions):
    assert support.entries(registry), f"{support.REGISTRY_REL} records no tool"
    wrong = []
    for name, approved_by in _approvals(registry):
        decision = decisions.get(approved_by)
        if decision is not None and not decision.accepted_by_owner:
            wrong.append(f"{name}: {approved_by} has status {decision.status!r}")
    assert wrong == [], f"entries of {support.REGISTRY_REL} whose approving decision is not ACCEPTED (owner): {wrong}"
