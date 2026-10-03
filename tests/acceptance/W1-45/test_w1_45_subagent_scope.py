"""W1-45 -- the wide orchestrator scope (DEC-156) does not reach an orchestrator
subagent in a non-orchestrator session (DEC-136 batch).

DEC-117 (inside a role subagent the subagent's role governs) combined with
DEC-156 (the orchestrator may write anywhere except ``tests/acceptance/**``):
the wide scope applies only when the session's own declared role is orchestrator.
In any other session, an orchestrator subagent is held to the active ticket's
``allowed_paths`` when that ticket's role is orchestrator, and to the scratch set
alone when the ticket's role is not orchestrator -- exactly as the orchestrator
behaved before W1-45.

DEC-125: a session with no declared role stays read-only, subagents included.

KPIs tested here:

- **failure 2** (guard): a non-orchestrator session must not gain a write outside
  its ticket's ``allowed_paths`` through an orchestrator subagent
- **failure 3** (guard): a no-role session's orchestrator subagent is read-only
- **success 1** (guard): in an orchestrator session, the orchestrator subagent
  keeps the wide scope
- **success 2** (guard): even in an orchestrator session, ``tests/acceptance/**``
  stays denied for the orchestrator subagent
- **containment**: the containment check treats an out-of-scope change by an
  orchestrator subagent in a non-orchestrator session as a finding
- **containment (DEC-171)**: in an orchestrator session, an orchestrator
  subagent's change outside the ticket's paths is a record, not a finding
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_tests = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_tests / "W1-02"))
sys.path.insert(0, str(_tests / "W1-03"))

import w1_02_support as guard_support   # noqa: E402
import w1_03_support as check_support   # noqa: E402

ORCHESTRATOR = guard_support.ORCHESTRATOR
ENGINEER = guard_support.ENGINEER
PRODUCT_SPEC = guard_support.PRODUCT_SPEC
DESIGNER = guard_support.TEST_DESIGNER
AUDITOR = guard_support.AUDITOR

ENGINEER_TICKET = guard_support.TICKET_ID                   # DAEO-zz90
ORCHESTRATOR_TICKET = guard_support.ORCHESTRATOR_TICKET_ID  # DAEO-zz91
PRODUCT_SPEC_TICKET = guard_support.PRODUCT_SPEC_TICKET_ID  # DAEO-zz92

SCRATCH = f"{guard_support.SCRATCH_REL}/note.txt"           # .gov-runtime/scratch/note.txt
SOURCE = "src/gov/guard/decide.py"
ACCEPTANCE_FILE = check_support.ACCEPTANCE_FILE              # tests/acceptance/W1-90/test_fixture.py

FILE_TOOLS = ["Edit", "Write"]

# Non-orchestrator session roles.
NON_ORCHESTRATOR_ROLES = [ENGINEER, PRODUCT_SPEC, DESIGNER, AUDITOR]


# --------------------------------------------------------------------------
# Guard -- the wide scope does NOT reach an orchestrator subagent in a
#          non-orchestrator session (failure 2)
# --------------------------------------------------------------------------

# (session_role, ticket, path).  The ticket's role is not orchestrator, so the
# subagent gets nothing beyond the scratch set.  Every one of these should be
# DENIED.
DENIED_ON_NON_ORCHESTRATOR_TICKET = {
    "engineer-session-readme":
        (ENGINEER, ENGINEER_TICKET, "README.md"),
    "engineer-session-source":
        (ENGINEER, ENGINEER_TICKET, SOURCE),
    "engineer-session-docs":
        (ENGINEER, ENGINEER_TICKET, "docs/notes.md"),
    "product-spec-session-readme":
        (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "README.md"),
    "designer-session-source":
        (DESIGNER, ENGINEER_TICKET, SOURCE),
    "auditor-session-readme":
        (AUDITOR, ENGINEER_TICKET, "README.md"),
}


@pytest.mark.parametrize("case", sorted(DENIED_ON_NON_ORCHESTRATOR_TICKET),
                         ids=sorted(DENIED_ON_NON_ORCHESTRATOR_TICKET))
def test_orchestrator_subagent_denied_outside_scope_in_non_orchestrator_session(project, write, case):
    """Failure 2: the orchestrator subagent on a non-orchestrator ticket has no paths
    beyond scratch; the wide DEC-156 scope does not apply."""
    session_role, ticket, relpath = DENIED_ON_NON_ORCHESTRATOR_TICKET[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, session_role, ticket, tool_name, subagent=ORCHESTRATOR)
        guard_support.assert_denied(
            result,
            f"{tool_name} on {relpath} by an orchestrator subagent in a {session_role} session on {ticket}")


# --------------------------------------------------------------------------
# Guard -- on the orchestrator ticket, the subagent gets the ticket's paths
# --------------------------------------------------------------------------

ALLOWED_ON_ORCHESTRATOR_TICKET = {
    "settings":  (ENGINEER, ORCHESTRATOR_TICKET, ".claude/settings.json"),
    "bootstrap": (ENGINEER, ORCHESTRATOR_TICKET, "governance/project/bootstrap.md"),
}


@pytest.mark.parametrize("case", sorted(ALLOWED_ON_ORCHESTRATOR_TICKET),
                         ids=sorted(ALLOWED_ON_ORCHESTRATOR_TICKET))
def test_orchestrator_subagent_allowed_on_orchestrator_ticket_paths(project, write, case):
    """The ticket role IS orchestrator: the subagent gets the ticket's allowed_paths."""
    session_role, ticket, relpath = ALLOWED_ON_ORCHESTRATOR_TICKET[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, session_role, ticket, tool_name, subagent=ORCHESTRATOR)
        guard_support.assert_allowed(
            result,
            f"{tool_name} on {relpath} by an orchestrator subagent in a {session_role} session on {ticket}")


# Even on the orchestrator ticket, a path NOT in the ticket's allowed_paths is
# denied (no wide scope in a non-orchestrator session).
def test_orchestrator_subagent_denied_outside_orchestrator_ticket_paths(project, write):
    """On the orchestrator ticket, paths outside allowed_paths are still denied:
    the wide scope does not apply in a non-orchestrator session."""
    for relpath in ("README.md", SOURCE, "docs/notes.md"):
        for tool_name in FILE_TOOLS:
            result = write(project, relpath, ENGINEER, ORCHESTRATOR_TICKET, tool_name,
                           subagent=ORCHESTRATOR)
            guard_support.assert_denied(
                result,
                f"{tool_name} on {relpath} by an orchestrator subagent on {ORCHESTRATOR_TICKET} "
                f"in an engineer session")


# --------------------------------------------------------------------------
# Guard -- the orchestrator subagent can always write to scratch
# --------------------------------------------------------------------------

def test_orchestrator_subagent_can_write_to_scratch(project, write):
    """On any ticket, scratch is available to any known-role subagent."""
    result = write(project, SCRATCH, ENGINEER, ENGINEER_TICKET, "Write", subagent=ORCHESTRATOR)
    guard_support.assert_allowed(
        result,
        f"Write on {SCRATCH} by an orchestrator subagent in an engineer session")


# --------------------------------------------------------------------------
# Guard -- Bash writes by an orchestrator subagent in a non-orchestrator session
# --------------------------------------------------------------------------

BASH_DENIED_IN_NON_ORCHESTRATOR_SESSION = {
    "redirect-to-readme": (ENGINEER, ENGINEER_TICKET, "echo changed > README.md"),
    "touch-source":       (ENGINEER, ENGINEER_TICKET, f"touch {SOURCE}"),
    "redirect-to-docs":   (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "echo changed > docs/notes.md"),
}


@pytest.mark.parametrize("case", sorted(BASH_DENIED_IN_NON_ORCHESTRATOR_SESSION),
                         ids=sorted(BASH_DENIED_IN_NON_ORCHESTRATOR_SESSION))
def test_orchestrator_subagent_bash_denied_in_non_orchestrator_session(project, bash_guard, case):
    """Failure 2 (Bash): the wide scope does not extend to the subagent's Bash writes."""
    session_role, ticket, command = BASH_DENIED_IN_NON_ORCHESTRATOR_SESSION[case]
    result = bash_guard(project, command, session_role, ticket, subagent=ORCHESTRATOR)
    guard_support.assert_denied(
        result,
        f"Bash `{command}` by an orchestrator subagent in a {session_role} session on {ticket}")


# --------------------------------------------------------------------------
# Guard -- without a ticket, the orchestrator subagent in a non-orchestrator
#          session has no paths (failure 2)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("session_role", NON_ORCHESTRATOR_ROLES, ids=NON_ORCHESTRATOR_ROLES)
def test_orchestrator_subagent_without_ticket_denied(project, write, session_role):
    """Failure 2: without a ticket and without the wide scope, nothing is allowed."""
    for relpath in ("README.md", SOURCE, ".claude/settings.json"):
        result = write(project, relpath, session_role, None, "Write", subagent=ORCHESTRATOR)
        guard_support.assert_denied(
            result,
            f"Write on {relpath} by an orchestrator subagent in a {session_role} session without a ticket")


# --------------------------------------------------------------------------
# Guard -- no-role session: orchestrator subagent stays read-only (DEC-125,
#          failure 3)
# --------------------------------------------------------------------------

def test_no_role_session_orchestrator_subagent_is_read_only(project, write):
    """DEC-125 / failure 3: in a session with no declared role, everything,
    subagents included, is read-only."""
    for relpath in ("README.md", SOURCE, SCRATCH, ".claude/settings.json"):
        result = write(project, relpath, None, ENGINEER_TICKET, "Write", subagent=ORCHESTRATOR)
        guard_support.assert_denied(
            result,
            f"Write on {relpath} by an orchestrator subagent in a no-role session")


def test_unknown_role_session_orchestrator_subagent_is_read_only(project, write):
    """Failure 3: an unknown session role does not make the orchestrator subagent writable."""
    result = write(project, SOURCE, "developer", ENGINEER_TICKET, "Write", subagent=ORCHESTRATOR)
    guard_support.assert_denied(
        result,
        "Write on source by an orchestrator subagent in a developer session")


# --------------------------------------------------------------------------
# Guard -- in an orchestrator session, the orchestrator subagent DOES get
#          the wide scope (success 1)
# --------------------------------------------------------------------------

WIDE_SCOPE_IN_ORCHESTRATOR_SESSION = {
    "readme-on-own-ticket":         (ORCHESTRATOR_TICKET, "README.md"),
    "source-on-own-ticket":         (ORCHESTRATOR_TICKET, SOURCE),
    "docs-on-own-ticket":           (ORCHESTRATOR_TICKET, "docs/notes.md"),
    "pyproject-on-own-ticket":      (ORCHESTRATOR_TICKET, "pyproject.toml"),
    "unit-test-on-own-ticket":      (ORCHESTRATOR_TICKET, "tests/unit/guard/test_decide.py"),
    "readme-on-engineer-ticket":    (ENGINEER_TICKET, "README.md"),
    "source-on-engineer-ticket":    (ENGINEER_TICKET, SOURCE),
    "readme-without-ticket":        (None, "README.md"),
}


@pytest.mark.parametrize("case", sorted(WIDE_SCOPE_IN_ORCHESTRATOR_SESSION),
                         ids=sorted(WIDE_SCOPE_IN_ORCHESTRATOR_SESSION))
def test_orchestrator_subagent_wide_scope_in_orchestrator_session(project, write, case):
    """Success 1: in an orchestrator session, the orchestrator subagent has the wide scope."""
    ticket, relpath = WIDE_SCOPE_IN_ORCHESTRATOR_SESSION[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, ORCHESTRATOR, ticket, tool_name, subagent=ORCHESTRATOR)
        guard_support.assert_allowed(
            result,
            f"{tool_name} on {relpath} by an orchestrator subagent in an orchestrator session "
            f"on {ticket!r}")


# --------------------------------------------------------------------------
# Guard -- even in an orchestrator session, tests/acceptance/** is denied
#          (success 2)
# --------------------------------------------------------------------------

def test_orchestrator_subagent_acceptance_denied_in_orchestrator_session(project, write):
    """Success 2: even in an orchestrator session, tests/acceptance/** is denied."""
    for relpath in (ACCEPTANCE_FILE, "tests/acceptance/W1-91/test_new.py"):
        for tool_name in FILE_TOOLS:
            result = write(project, relpath, ORCHESTRATOR, ORCHESTRATOR_TICKET, tool_name,
                           subagent=ORCHESTRATOR)
            guard_support.assert_denied(
                result,
                f"{tool_name} on {relpath} by an orchestrator subagent in an orchestrator session")


def test_orchestrator_subagent_bash_wide_scope_in_orchestrator_session(project, bash_guard):
    """Success 1 (Bash): the wide scope extends to Bash writes in an orchestrator session."""
    result = bash_guard(project, "echo changed > README.md", ORCHESTRATOR, ORCHESTRATOR_TICKET,
                        subagent=ORCHESTRATOR)
    guard_support.assert_allowed(
        result,
        "Bash write to README.md by an orchestrator subagent in an orchestrator session")


# --------------------------------------------------------------------------
# Containment -- orchestrator subagent in a non-orchestrator session:
#                a change outside scope is a FINDING (not a DEC-171 record)
# --------------------------------------------------------------------------

def test_containment_catches_orchestrator_subagent_in_non_orchestrator_session(project, after_bash):
    """The containment check treats the orchestrator subagent in a non-orchestrator
    session as any other role: a change outside scope is a finding."""
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, ENGINEER_TICKET, changed=["README.md"],
                        subagent=ORCHESTRATOR)
    check_support.assert_caught(
        result, "README.md",
        what=f"`{command}` by an orchestrator subagent in an engineer session")


# --------------------------------------------------------------------------
# Containment -- orchestrator subagent in an orchestrator session:
#                a change outside the ticket's paths is silent (DEC-171)
# --------------------------------------------------------------------------

def test_containment_silent_for_orchestrator_subagent_in_orchestrator_session(project, after_bash):
    """DEC-171: in an orchestrator session, the orchestrator subagent's changes
    outside the ticket's paths are records, not findings."""
    command = "echo changed >> README.md"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, changed=["README.md"],
                        subagent=ORCHESTRATOR)
    check_support.assert_silent(
        result,
        f"`{command}` by an orchestrator subagent in an orchestrator session")
