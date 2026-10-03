"""W1-06 — each install has its own register entry, and ``approved_by`` cites it.

KPI success 1: "ccusage installed and pinned through a DEC-083 decision
package". KPI failure 1: "Any tool installed without a recorded owner approval".

DEC-197 (DP-4): "Each install has its own register entry naming the tool and
its exact version, and the registry's ``approved_by`` cites it. Older pins cite
the decision that names them (DEC-074, DEC-191, DEC-141)."

DEC-192 approves ccusage 20.0.26, installed with
``~/.nvm/versions/node/v22.23.3/bin/npm install -g ccusage@20.0.26`` and
"uninstalled with the same npm". DEC-193 approves the Superpowers v6.4.2
source, ``git clone --depth 1 --branch v6.4.2 https://github.com/obra/superpowers``.

The tests do not name the approving entry's id: they read the entry the
registry cites and ask whether it is the approval of that tool at that version.
A decision's text is its heading and its own lines (``support.own_text``).
"""

from __future__ import annotations

import datetime
import re

import pytest

import w1_06_support as support
from test_w1_06_pins import PINS

# The installs this ticket makes: tool -> (names accepted for the entry, the approved version)
INSTALLS = {
    "ccusage": (("ccusage",), "20.0.26"),
    "superpowers": (("superpowers",), "6.4.2"),
}

STACK_NAMES = {support.norm_name(name) for names, _, _, _ in PINS.values() for name in names}
NODE_22_NPM = re.compile(r"\.nvm/versions/node/v22\.23\.3/bin/npm(?![\w-])")


def _cited(registry, decisions, tool):
    """The entry of ``tool`` and the decision it cites."""
    entry = support.one(registry, INSTALLS[tool][0])
    cited = support.approved_by(entry)
    assert cited in decisions, (
        f"the {tool} entry's approved_by is {cited!r}, which is not an entry of {support.REGISTER_REL}"
    )
    return entry, decisions[cited]


# --------------------------------------------------------------------------
# The two installs of this ticket (DEC-192, DEC-193)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool", sorted(INSTALLS))
def test_an_install_of_this_ticket_is_recorded_at_the_approved_version(registry, tool):
    names, version = INSTALLS[tool]
    found = support.norm_version(support.one(registry, names).get("version", ""))
    assert found == version, f"the registry records {tool} at {found!r}; the owner approved {version!r}"


@pytest.mark.parametrize("tool", sorted(INSTALLS))
def test_an_install_of_this_ticket_cites_a_decision_that_names_the_tool_and_its_version(registry, decisions, tool):
    entry, decision = _cited(registry, decisions, tool)
    version = support.norm_version(entry.get("version", ""))
    text = support.own_text(decision)
    assert support.names_tool(text, tool), (
        f"{decision.id}, cited as the approval of {tool}, does not name {tool}: {decision.title!r}"
    )
    assert version and support.names_version(text, version), (
        f"{decision.id}, cited as the approval of {tool} {version}, does not name the version {version}: "
        f"{decision.title!r}"
    )


@pytest.mark.parametrize("tool", sorted(INSTALLS))
def test_an_install_of_this_ticket_has_its_own_register_entry(registry, decisions, tool):
    """ "Its own": the decision that approves this install approves no other entry of the registry."""
    entry, decision = _cited(registry, decisions, tool)
    shared = sorted(support.norm_name(other.get("name", "")) for other in support.entries(registry)
                    if other is not entry and support.approved_by(other) == decision.id)
    assert shared == [], f"{decision.id} is cited as the approval of {tool} and also of: {shared}"


@pytest.mark.parametrize("tool", sorted(INSTALLS))
def test_the_approval_of_an_install_of_this_ticket_is_made_under_dec_083(registry, decisions, tool):
    """KPI success 1: "through a DEC-083 decision package". The approving entry's status line says so."""
    _, decision = _cited(registry, decisions, tool)
    assert decision.accepted_by_owner, f"{decision.id} is not accepted by the owner (status: {decision.status!r})"
    assert re.search(r"DEC-083(?!\d)", decision.status), (
        f"{decision.id}, cited as the approval of {tool}, is not recorded under DEC-083: {decision.status!r}"
    )


@pytest.mark.parametrize("tool", sorted(INSTALLS))
def test_an_install_of_this_ticket_is_not_dated_before_its_approval(registry, decisions, tool):
    """DEC-083: the orchestrator "installs only after the owner's explicit approval"."""
    entry, decision = _cited(registry, decisions, tool)
    assert decision.date, f"{decision.id} carries no date the install date can be compared with"
    recorded = datetime.date.fromisoformat(str(entry.get("date", "")).strip()[:10])
    approved = datetime.date.fromisoformat(decision.date)
    assert recorded >= approved, (
        f"the registry dates {tool} {recorded}, before its approval {decision.id} of {approved}"
    )


def test_the_ccusage_install_command_is_the_approved_one(registry):
    """DEC-192: the npm of Node v22.23.3, ``install -g ccusage@20.0.26``."""
    install = str(support.one(registry, INSTALLS["ccusage"][0]).get("install", ""))
    assert NODE_22_NPM.search(install), (
        f"the ccusage entry's install command does not use the npm of Node v22.23.3 (DEC-192): {install!r}"
    )
    assert re.search(r"\binstall\b", install) and re.search(r"(?<!\S)(-g|--global)(?!\S)", install), (
        f"the ccusage entry's install command is not a global npm install: {install!r}"
    )
    assert re.search(r"(?<![\w@/-])ccusage@20\.0\.26(?![\w.])", install), (
        f"the ccusage entry's install command does not install ccusage@20.0.26: {install!r}"
    )


def test_the_ccusage_uninstall_command_uses_the_same_npm(registry):
    """DEC-192: "It is uninstalled with the same npm"."""
    uninstall = str(support.one(registry, INSTALLS["ccusage"][0]).get("uninstall", ""))
    assert NODE_22_NPM.search(uninstall), (
        f"the ccusage entry's uninstall command does not use the npm of Node v22.23.3 (DEC-192): {uninstall!r}"
    )
    assert re.search(r"\b(uninstall|remove|rm|un|unlink)\b", uninstall) and "ccusage" in uninstall, (
        f"the ccusage entry's uninstall command does not uninstall ccusage: {uninstall!r}"
    )


def test_the_superpowers_install_command_fetches_the_approved_source(registry):
    """DEC-193: the tag v6.4.2 of ``github.com/obra/superpowers``."""
    install = str(support.one(registry, INSTALLS["superpowers"][0]).get("install", ""))
    assert "github.com/obra/superpowers" in install, (
        f"the Superpowers entry's install command does not name the approved source: {install!r}"
    )
    assert support.names_version(install, "6.4.2"), (
        f"the Superpowers entry's install command does not name v6.4.2: {install!r}"
    )


# --------------------------------------------------------------------------
# Older pins (DEC-197, second sentence)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("pin", sorted(PINS))
def test_a_stack_pin_cites_dec_074(registry, pin):
    """DP-4 option (a), accepted as DEC-197: "DEC-074 for the stack"."""
    cited = support.approved_by(support.one(registry, PINS[pin][0]))
    assert cited == "DEC-074", f"the {pin} entry's approved_by is {cited!r}; a pin of the stack cites DEC-074"


def test_pyyaml_cites_dec_191(registry):
    cited = support.approved_by(support.one(registry, ("pyyaml",)))
    assert cited == "DEC-191", f"the PyYAML entry's approved_by is {cited!r}; DEC-191 is the decision that names it"


def test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool(registry, decisions):
    """Every entry but the ten stack pins: the cited decision's own text holds the entry's name.

    This covers gitleaks, PyYAML, ccusage, Superpowers and anything else the
    registry records (bubblewrap and socat cite DEC-141 when they are recorded).
    """
    checked, wrong = 0, []
    for entry in support.entries(registry):
        name = support.norm_name(entry.get("name", ""))
        if name in STACK_NAMES:
            continue
        checked += 1
        decision = decisions.get(support.approved_by(entry))
        if decision is None:
            wrong.append(f"{name}: {support.approved_by(entry)!r} is not in the register")
        elif not support.names_tool(support.own_text(decision), name):
            wrong.append(f"{name}: {decision.id} ({decision.title!r}) does not name it")
    assert checked, f"{support.REGISTRY_REL} records no tool outside the ten stack pins"
    assert wrong == [], f"entries of {support.REGISTRY_REL} approved by a decision that does not name the tool: {wrong}"
