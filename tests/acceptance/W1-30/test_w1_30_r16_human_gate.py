"""Round 16, piece 1 (DEC-627, DEC-613, DEC-633): the authority check declares ``human_gate`` as well.

DEC-627, the owner's words: "``core-authority`` declares ``human_gate`` as well, proven by a planted-violation
case (DEC-613)."

Measured before the round: no declaration of the kernel template states the hard-block policy key
``human_gate``, so ``gov check`` reports ``policy-human_gate`` (``POLICY_NOT_COVERED``) in every project. The
hard-block check ``core-authority`` already holds the gate rule: it reports a record that cites, under
``approval``, a decision package that is not accepted.

The first cases are the proof the declaration rests on and pass before the round: the check, run as the kernel
template declares it (``sh -c`` in the project root, DEC-285) and through ``gov check``, is green where the cited
package is accepted and red, naming the citing record and the package, where it is not. The pair itself is held
in ``test_w1_30_r15_policy_pairs.py``. The last case is red before the round.
"""

from __future__ import annotations

import pytest

import w1_30_r15_support as r15
import w1_30_r16_support as r16

support = r15.support
decisions_support = support.decisions_support

CHECK = r16.AUTHORITY_CHECK
KEY = "human_gate"
TICKET = "PROJ-aaaa"
GATE, CIT = "DP-0001", "CIT-0001"
GATE_REL = f"docs/decisions/packages/{GATE}.md"
ACCEPTED = "ACCEPTED"
NOT_ACCEPTED = ("PROPOSED", "DECLINED", "REVOKED", "STALE")


def _project(scratch, gate_status):
    """A project whose one ticket cites, under ``approval``, a decision package of its own CIT whose status
    is ``gate_status``; the ticket is closed, so that nothing but the citation is at stake."""
    project = scratch()
    project.base_source()
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01", status="closed", approval=[GATE], cit=CIT))
    project.write(GATE_REL, decisions_support.package(GATE, gate_status, CIT))
    project.declare_as_the_kernel_does(CHECK)
    project.commit()
    return project


def test_the_authority_check_is_green_where_the_cited_package_is_accepted(scratch, sandbox):
    """Green before the round: the proof the declaration rests on (the project without the violation)."""
    project = _project(scratch, ACCEPTED)
    done = r15.run_declared_command(CHECK, project, sandbox)
    assert done.returncode == 0, \
        f"the ticket cites an accepted package of its CIT and the check is not green\n{r16.output_of(done)}"
    status, entry, run = r15.status_of(project, sandbox, CHECK)
    assert status == r15.GREEN and entry["findings"] == [], f"{status}: {entry['findings']}\n{run.describe()}"


@pytest.mark.parametrize("gate_status", NOT_ACCEPTED)
def test_the_authority_check_is_red_and_names_the_record_that_cites_a_package_that_is_not_accepted(gate_status,
                                                                                                    scratch, sandbox):
    """Green before the round: the proof the declaration rests on (the planted violation of the gate rule)."""
    project = _project(scratch, gate_status)
    done = r15.run_declared_command(CHECK, project, sandbox)
    output = r16.output_of(done)
    assert done.returncode != 0, \
        f"the ticket cites, under approval, a package that is {gate_status} and the check is green\n{output}"
    assert TICKET in output and GATE in output, \
        f"the check names neither the citing record ({TICKET}) nor the package ({GATE})\n{output}"
    status, entry, run = r15.status_of(project, sandbox, CHECK)
    found = str(entry["findings"])
    assert status == r15.RED and TICKET in found and GATE in found, \
        f"gov check does not report the check RED naming {TICKET} and {GATE}: {status}, {found}\n{run.describe()}"


def test_gov_check_reports_no_human_gate_finding_where_the_kernel_s_authority_check_is_declared(scratch, sandbox):
    """A project that holds the authority check as the kernel template declares it, and no other check. The
    keys no declaration of the project states are still reported (the premise: ``security`` is), and
    ``human_gate`` is not among them, nor is ``authority``.
    Red before the round: ``policy-human_gate``, RED, ``POLICY_NOT_COVERED``."""
    project = _project(scratch, ACCEPTED)
    assert r15.POLICIES.get(KEY) == r15.HARD_BLOCK, f"the kernel minimum of {KEY!r} is {r15.POLICIES.get(KEY)!r}"
    project.write(r15.PATH_MAP_REL, r15.policies_text(r15.POLICIES))    # the thirteen keys at the kernel minimum
    entries, run = r15.checked(project, sandbox)
    reported = r15.policy_entries(entries)
    assert "security" in reported, \
        f"the project reports no uncovered policy key at all: the case shows nothing\n{run.describe()}"
    assert "authority" not in reported, \
        f"the kernel's declaration of {CHECK} does not cover 'authority' in this project\n{run.describe()}"
    assert KEY not in reported and f"policy-{KEY}" not in entries, \
        (f"gov check reports policy-{KEY} in a project that holds the kernel's declaration of {CHECK}: "
         f"{reported.get(KEY) or entries.get(f'policy-{KEY}')}")
    assert entries[CHECK]["status"] == r15.GREEN, \
        f"the check that covers the key is {entries[CHECK]['status']} in the project without a violation"
