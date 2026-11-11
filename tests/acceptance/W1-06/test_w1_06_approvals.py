"""W1-06 — no tool is in the registry without a recorded owner approval.

KPI failure 1: "Any tool installed without a recorded owner approval".

DEC-083: every install is recorded in the tool registry with its "approving
decision"; the schema's ``approved_by`` holds that decision's id (DEC-121). The
approval is recorded when that id is an entry of ``docs/DECISION_REGISTER.md``
whose status is ``ACCEPTED (owner…)``, or the owner's later DONE ruling written
before it, ``DONE (owner, …); it was ACCEPTED (owner, …`` (DEC-1098 (3)).

Whether the approving decision must also name the tool and its version was
DP-4; the owner answered it (DEC-197) and ``test_w1_06_install_approvals.py``
tests the answer.
"""

from __future__ import annotations

import pytest

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


# Revised for DEC-1098 (3): W2-130's sitting wrote the owner's DONE ruling first on 103 status lines, the old
# line kept after "it was". A decision the owner accepted and then ruled DONE is still accepted by the owner.
# Rows: (status line, accepted by the owner, the acceptance's date).
STATUS_FORMS = {
    "accepted-owner": ("ACCEPTED (owner, 2026-10-03) · **Under:** DEC-083", True, "2026-10-03"),
    "done-then-accepted-owner": (
        "DONE (owner, 2026-11-09, DEC-1098 (3)); it was ACCEPTED (owner, 2026-10-22, in the chat) · **Under:** DEC-083",
        True, "2026-10-22"),
    "superseded": ("SUPERSEDED (2026-10-05) by DEC-397 · **Under:** DEC-083", False, None),
    "withdrawn": ("WITHDRAWN (owner, 2026-10-05)", False, None),
    "deferred": ("DEFERRED (owner, 2026-10-05)", False, None),
    "proposed": ("PROPOSED (orchestrator, 2026-10-05)", False, None),
    "done-then-accepted-delegated": (
        "DONE (owner, 2026-11-09, DEC-1098 (3)); it was ACCEPTED (delegated, orchestrator, 2026-10-22)", False, None),
    "done-then-superseded": (
        "DONE (owner, 2026-11-09, DEC-1098 (3)); it was SUPERSEDED by DEC-397; ACCEPTED (owner, 2026-10-01)",
        False, None),
    "done-alone": ("DONE (2026-09-30) · **Basis:** session report", False, None),
}


@pytest.mark.parametrize("form", sorted(STATUS_FORMS))
def test_an_owner_acceptance_is_read_from_each_status_form(form):
    status, accepted, date = STATUS_FORMS[form]
    decision = support.Decision(id="DEC-999", title="A synthetic entry", status=status, body="")
    assert decision.accepted_by_owner is accepted, (
        f"status {status!r} is read as {'accepted' if decision.accepted_by_owner else 'not accepted'} by the owner"
    )
    if accepted:
        assert decision.date == date, f"status {status!r}: the acceptance's date read as {decision.date!r}, not {date}"
