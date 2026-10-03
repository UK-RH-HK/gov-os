"""W1-45 -- the guard allows the orchestrator to write anywhere except tests/acceptance/**.

DEC-156: the orchestrator role may write anywhere in the repository except
``tests/acceptance/**``.  The guard enforces only that exclusion.  The
orchestrator's write scope comes from the role itself, not from any ticket's
``allowed_paths``.

DEC-112: every other role keeps the ``allowed_paths`` rule unchanged.

KPIs tested here (guard / PreToolUse):

- success 1: the orchestrator is allowed outside ticket paths, whatever the
  active ticket and also with no ticket (DEC-156) [CAP-58.e]
- success 2: the orchestrator is denied under ``tests/acceptance/**`` (MR-3)
  [CAP-58.e]
- success 5: every other role keeps the ``allowed_paths`` rule unchanged
  (DEC-112)
- success 7: the orchestrator can write its checkpoint (DEC-150) [CAP-58.e]
- failure 1: ``tests/acceptance/**`` stays denied
- failure 2: no other role gains a write outside its ticket's ``allowed_paths``
- failure 3: a session with no role or an unknown role gains no write
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_tests = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_tests / "W1-02"))
sys.path.insert(0, str(_tests / "W1-03"))

import w1_02_support as support       # noqa: E402
import w1_03_support as check_support  # noqa: E402

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
PRODUCT_SPEC = support.PRODUCT_SPEC
DESIGNER = support.TEST_DESIGNER
AUDITOR = support.AUDITOR

TICKET = support.TICKET_ID                          # engineer ticket DAEO-zz90
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID  # DAEO-zz91
PRODUCT_SPEC_TICKET = support.PRODUCT_SPEC_TICKET_ID  # DAEO-zz92

WBS = check_support.TICKET_WBS_ID
ACCEPTANCE_FILE = check_support.ACCEPTANCE_FILE

FILE_TOOLS = ["Edit", "Write"]


# --------------------------------------------------------------------------
# KPI success 1: the orchestrator may write anywhere except tests/acceptance/**
# --------------------------------------------------------------------------

# (ticket, repository-relative path).  Each must be ALLOWED under DEC-156.
# Under the current guard every one is DENIED because the orchestrator's paths
# come from its ticket only; these paths are outside the ticket's allowed_paths
# (".claude/settings.json", "governance/project/bootstrap.md").
WRITES_OUTSIDE_TICKET_PATHS = {
    "source-on-own-ticket":
        (ORCHESTRATOR_TICKET, "src/gov/guard/decide.py"),
    "docs-on-own-ticket":
        (ORCHESTRATOR_TICKET, "docs/notes.md"),
    "root-file-on-own-ticket":
        (ORCHESTRATOR_TICKET, "README.md"),
    "neighbour-on-own-ticket":
        (ORCHESTRATOR_TICKET, "governance/project/roster.yaml"),
    "pyproject-on-own-ticket":
        (ORCHESTRATOR_TICKET, "pyproject.toml"),
    "unit-tests-on-own-ticket":
        (ORCHESTRATOR_TICKET, "tests/unit/guard/test_decide.py"),
    "source-on-engineer-ticket":
        (TICKET, "src/gov/guard/decide.py"),
    "docs-on-engineer-ticket":
        (TICKET, "docs/notes.md"),
    "root-file-on-product-spec-ticket":
        (PRODUCT_SPEC_TICKET, "README.md"),
}


@pytest.mark.parametrize("case", sorted(WRITES_OUTSIDE_TICKET_PATHS), ids=sorted(WRITES_OUTSIDE_TICKET_PATHS))
def test_orchestrator_can_write_outside_ticket_paths(project, write, case):
    """KPI success 1.  DEC-156: the orchestrator's scope comes from the role, not the ticket."""
    ticket, relpath = WRITES_OUTSIDE_TICKET_PATHS[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, ORCHESTRATOR, ticket, tool_name)
        support.assert_allowed(result, f"{tool_name} on {relpath} by the orchestrator on {ticket}")


# With no active ticket at all.
WRITES_WITHOUT_TICKET = {
    "source-without-ticket": "src/gov/guard/decide.py",
    "docs-without-ticket": "docs/notes.md",
    "root-file-without-ticket": "README.md",
    "settings-without-ticket": ".claude/settings.json",
}


@pytest.mark.parametrize("case", sorted(WRITES_WITHOUT_TICKET), ids=sorted(WRITES_WITHOUT_TICKET))
def test_orchestrator_can_write_without_a_ticket(project, write, case):
    """KPI success 1.  DEC-156: the orchestrator writes without a ticket too."""
    relpath = WRITES_WITHOUT_TICKET[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, ORCHESTRATOR, None, tool_name)
        support.assert_allowed(result, f"{tool_name} on {relpath} by the orchestrator without a ticket")


BASH_WRITES_OUTSIDE_TICKET = {
    "redirect-to-source": (ORCHESTRATOR_TICKET, "echo changed > src/gov/guard/decide.py"),
    "touch-docs": (ORCHESTRATOR_TICKET, "touch docs/notes.md"),
    "redirect-to-readme": (ORCHESTRATOR_TICKET, "echo changed > README.md"),
    "redirect-on-engineer-ticket": (TICKET, "echo changed > README.md"),
    "redirect-without-ticket": (None, "echo changed > README.md"),
}


@pytest.mark.parametrize("case", sorted(BASH_WRITES_OUTSIDE_TICKET), ids=sorted(BASH_WRITES_OUTSIDE_TICKET))
def test_orchestrator_bash_writes_outside_ticket_paths(project, bash_guard, case):
    """KPI success 1.  Bash writes follow the same scope."""
    ticket, command = BASH_WRITES_OUTSIDE_TICKET[case]
    result = bash_guard(project, command, ORCHESTRATOR, ticket)
    support.assert_allowed(result, f"Bash `{command}` by the orchestrator on {ticket!r}")


# --------------------------------------------------------------------------
# KPI success 2 / failure 1: tests/acceptance/** is denied for the orchestrator
# --------------------------------------------------------------------------

ACCEPTANCE_DENIED = {
    "existing-test": ACCEPTANCE_FILE,
    "new-test": f"tests/acceptance/{WBS}/test_new.py",
    "another-ticket": "tests/acceptance/W1-91/test_other.py",
    "readme-under-acceptance": f"tests/acceptance/{WBS}/README.md",
    "conftest": "tests/acceptance/conftest.py",
}


@pytest.mark.parametrize("case", sorted(ACCEPTANCE_DENIED), ids=sorted(ACCEPTANCE_DENIED))
def test_orchestrator_cannot_write_under_acceptance_tests(project, write, case):
    """KPI success 2, failure 1.  MR-3: only the independent test designer writes there."""
    relpath = ACCEPTANCE_DENIED[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, ORCHESTRATOR, ORCHESTRATOR_TICKET, tool_name)
        support.assert_denied(result, f"{tool_name} on {relpath} by the orchestrator")


ACCEPTANCE_BASH_DENIED = (
    f"echo changed > {ACCEPTANCE_FILE}",
    f"touch tests/acceptance/{WBS}/test_new.py",
    f"rm {ACCEPTANCE_FILE}",
)


@pytest.mark.parametrize("command", ACCEPTANCE_BASH_DENIED)
def test_orchestrator_bash_write_under_acceptance_tests_is_denied(project, bash_guard, command):
    """KPI success 2, failure 1."""
    result = bash_guard(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    support.assert_denied(result, f"Bash `{command}` by the orchestrator")


# --------------------------------------------------------------------------
# KPI success 7: the orchestrator can write its checkpoint (DEC-150)
# --------------------------------------------------------------------------

def test_orchestrator_can_write_its_checkpoint(project, write):
    """KPI success 7.  DEC-150: the orchestrator's checkpoint at ``.gov-runtime/scratch/orchestrator/``."""
    for relpath in (
        ".gov-runtime/scratch/orchestrator/checkpoint.json",
        ".gov-runtime/scratch/orchestrator/plan.yaml",
    ):
        result = write(project, relpath, ORCHESTRATOR, ORCHESTRATOR_TICKET)
        support.assert_allowed(result, f"Write on {relpath} by the orchestrator")


def test_orchestrator_checkpoint_works_without_a_ticket(project, write):
    """KPI success 7.  The checkpoint is in the scratch set, which needs no ticket."""
    result = write(project, ".gov-runtime/scratch/orchestrator/checkpoint.json", ORCHESTRATOR, None)
    support.assert_allowed(result, "Write on the checkpoint by the orchestrator without a ticket")


# --------------------------------------------------------------------------
# KPI success 5 / failure 2: every other role keeps the allowed_paths rule
# --------------------------------------------------------------------------

def test_engineer_is_still_denied_outside_ticket_paths(project, write):
    """KPI success 5, failure 2.  DEC-112: the orchestrator's scope is not contagious."""
    for relpath in ("README.md", "docs/notes.md", ".claude/settings.json"):
        for tool_name in FILE_TOOLS:
            result = write(project, relpath, ENGINEER, TICKET, tool_name)
            support.assert_denied(result, f"{tool_name} on {relpath} by the engineer on {TICKET}")


def test_product_spec_is_still_denied_outside_ticket_paths(project, write):
    """KPI success 5, failure 2."""
    for relpath in ("src/gov/guard/decide.py", "README.md"):
        result = write(project, relpath, PRODUCT_SPEC, PRODUCT_SPEC_TICKET)
        support.assert_denied(result, f"Write on {relpath} by the product-spec on {PRODUCT_SPEC_TICKET}")


# --------------------------------------------------------------------------
# KPI failure 3: a session with no role or an unknown role gains no write
# --------------------------------------------------------------------------

NO_ROLE_DENIALS = {
    "no-role-with-ticket": (None, TICKET),
    "unknown-role-with-ticket": ("developer", TICKET),
    "no-role-no-ticket": (None, None),
    "empty-role-with-ticket": ("", TICKET),
}


@pytest.mark.parametrize("case", sorted(NO_ROLE_DENIALS), ids=sorted(NO_ROLE_DENIALS))
def test_no_role_or_unknown_role_is_denied(project, write, case):
    """KPI failure 3.  The orchestrator scope does not weaken sessions without a valid role."""
    role, ticket = NO_ROLE_DENIALS[case]
    for relpath in ("src/gov/guard/decide.py", "README.md"):
        result = write(project, relpath, role, ticket)
        support.assert_denied(result, f"Write on {relpath} with GOV_ROLE={role!r} GOV_TICKET={ticket!r}")
