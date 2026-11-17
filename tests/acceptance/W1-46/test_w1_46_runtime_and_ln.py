"""W1-46 -- ``ln`` judged by the kernel's guard, and ``.gov-runtime/scratch/`` writable (batch 4, after implementation).

Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.2, 6.1; release 0.1.2): the launcher writes no deny rule of its own,
and this repository's settings no longer register the guard. Retired here: the literal ``Edit`` deny rules for the
names under ``.gov-runtime/`` at launch (DEC-311's first line) and the cases that asked this repository's committed
guard to refuse a write or an ``ln`` under ``.gov-runtime/`` or outside a role's paths. What stays asks the kernel's
guard, generated from the template, and still holds: its controls (scratch stays writable to every role, ``ln`` to a
destination the role may write is let through) and the research role's ``ln`` into its folder.

Rewrite-Reason: DEC-953 item 2 (W2-90, DEC-957, DEC-906). The ``kernel_*`` fixtures are W1-46's launch project built
on a project generated from the template, whose ``.claude/settings.json`` rulesync generates from the template's
sources, and the PreToolUse lines those settings register, run from ``governance/kernel/hooks/``
(``tests/acceptance/W2-90/README.md``).
"""

from __future__ import annotations

import pytest

import w1_46_support as support

w47 = support.w47
ENGINEER, RESEARCH = support.ENGINEER, support.RESEARCH
ORCHESTRATOR, PRODUCT_SPEC = w47.ORCHESTRATOR, w47.PRODUCT_SPEC
FOLDER = support.EXPERIMENT_REL
RUNTIME = ".gov-runtime"
SEED = f"{RUNTIME}/scratch/w1-46/seed.txt"
# Every role the guard knows, with the ticket it works on in the fixture project.
EVERY_ROLE = {**{role: w47.TICKET_OF[role] for role in (ORCHESTRATOR, PRODUCT_SPEC)}, **support.TICKET_OF}


# --------------------------------------------------------------------------
# The kernel's guard: .gov-runtime/scratch/ stays writable to every role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", sorted(EVERY_ROLE))
def test_scratch_stays_writable_for_every_role(kernel_guard, kernel_project, role):
    """A file tool and a plain Bash write, to a file that exists and to a new one."""
    guard, project = kernel_guard, kernel_project
    result = guard("Write", w47.write_input("Write", project / SEED), role, EVERY_ROLE[role])
    w47.assert_allowed(result, f"Write to {SEED} by {role}")
    command = f"echo x > {RUNTIME}/scratch/w1-46/new.txt"
    result = guard("Bash", w47.bash_input(command), role, EVERY_ROLE[role], cwd=project)
    w47.assert_allowed(result, f"`{command}` by {role}")


# --------------------------------------------------------------------------
# The kernel's guard: ln to a destination the role may write
# --------------------------------------------------------------------------

LINK = {"symbolic": "ln -s", "hard": "ln"}
WRITABLE = {
    "inside-the-tickets-paths": "src/gov/guard/w1_46_link.py",
    "scratch": f"{RUNTIME}/scratch/w1-46/link.txt",
}


@pytest.mark.parametrize("kind", sorted(LINK))
@pytest.mark.parametrize("name", sorted(WRITABLE))
def test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write(kernel_guard, kernel_project, kind, name):
    """The control: the target is a file in scratch, the destination a new name the role may write."""
    guard, project = kernel_guard, kernel_project
    command = f"{LINK[kind]} {SEED} {WRITABLE[name]}"
    result = guard("Bash", w47.bash_input(command), ENGINEER, cwd=project)
    w47.assert_allowed(result, f"`{command}` by an engineer")


def test_the_guard_holds_a_research_ln_to_the_experiment_folder(kernel_guard, kernel_project):
    """The research role's allow-list is its folder: ``ln`` into a sibling is refused, into the folder it is not."""
    guard, project = kernel_guard, kernel_project
    inside = f"ln -s README.md {FOLDER}/w1-46-link.md"
    w47.assert_allowed(guard("Bash", w47.bash_input(inside), RESEARCH, cwd=project), f"`{inside}` by research")
    sibling = f"ln -s {FOLDER}/README.md experiments/spikes/exp-900/w1-46-link.md"
    w47.assert_stopped(guard("Bash", w47.bash_input(sibling), RESEARCH, cwd=project), f"`{sibling}` by research")
