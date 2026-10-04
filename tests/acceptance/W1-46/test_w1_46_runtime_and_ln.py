"""W1-46 -- ``.gov-runtime/`` named literally at launch, and ``ln`` judged by the guard (batch 4, after implementation).

DEC-311 (owner, on DP-14; amends DEC-180):

- "The launcher's settings carry a literal ``Edit`` deny rule for every name
  that exists under ``.gov-runtime/`` outside ``scratch/`` at launch, plus the
  freeze flag."
- "The guard treats the destination of ``ln`` as a write target."
- "A new name created under ``.gov-runtime/`` at the OS level after launch is a
  residual in ``bootstrap.md``." It is not tested as refused, here or in the
  live session.
- "``.gov-runtime/`` outside ``scratch/`` is denied by the guard to every role,
  not only to the orchestrator."

KPI success 10: "a write to the freeze flag, the snapshots, the findings or the
records fails, through a file tool, through an opaque Bash form and through ln,
while .gov-runtime/scratch/** stays writable (DEC-180, DEC-176)".

**A literal rule** names one path and holds no ``*``, ``?`` or ``[``: the Linux
sandbox skips a rule with one of them (EXP-001 §1), so only a literal rule
stops a Bash command there. "Every name that exists under ``.gov-runtime/``"
is read as the entries of that directory itself (``findings.jsonl``,
``records.jsonl``, ``snapshots``): a rule on a directory holds for everything
under it.

**``ln``** is tested in its plain forms, ``ln [-s] <target> <destination>``,
with ``-sf`` onto a name that exists and with a directory as the destination.
Not tested: ``ln -t <directory>``, ``ln <target>`` with no destination, several
targets, and what a hard link in a writable place lets a session do to the file
it links to (README, reading 16: a residual for EXP-002).

The guard is asked through the PreToolUse commands the project's committed
settings register. No session is started.
"""

from __future__ import annotations

import os

import pytest

import w1_46_support as support

w47 = support.w47
ENGINEER, RESEARCH = support.ENGINEER, support.RESEARCH
ORCHESTRATOR, PRODUCT_SPEC = w47.ORCHESTRATOR, w47.PRODUCT_SPEC
FOLDER = support.EXPERIMENT_REL
RUNTIME = ".gov-runtime"
SEED = f"{RUNTIME}/scratch/w1-46/seed.txt"
FREEZE = f"{RUNTIME}/freeze"
PROTECTED = (FREEZE, f"{RUNTIME}/findings.jsonl", f"{RUNTIME}/records.jsonl", f"{RUNTIME}/snapshots/keep.json")
# Every role the guard knows, with the ticket it works on in the fixture project.
EVERY_ROLE = {**{role: w47.TICKET_OF[role] for role in (ORCHESTRATOR, PRODUCT_SPEC)}, **support.TICKET_OF}


def _names_at_launch(project):
    """The entries of ``.gov-runtime/`` outside ``scratch/``, as they are now."""
    return sorted(name for name in os.listdir(project / RUNTIME) if name != "scratch")


def _missing_literal_rules(result, project, sandbox, names):
    root = os.path.realpath(project)
    literal = support.literal_edit_denials(result, project, sandbox)
    return [name for name in names if os.path.join(root, RUNTIME, name) not in literal]


# --------------------------------------------------------------------------
# The settings the launcher builds: a literal rule per name that exists at launch, plus the freeze flag
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_each_name_under_gov_runtime_at_launch_has_a_literal_edit_deny_rule(launch, project, sandbox, role):
    names = _names_at_launch(project)
    assert names == ["findings.jsonl", "records.jsonl", "snapshots"], f"the fixture's runtime directory holds {names}"
    result = launch(role)
    missing = _missing_literal_rules(result, project, sandbox, names)
    assert missing == [], (
        f"no literal Edit deny rule names .gov-runtime/{missing} for a launched {role}; rules: "
        f"{support.deny_rules(result.settings(), 'Edit')}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_freeze_flag_has_a_literal_rule_also_when_it_does_not_exist_at_launch(launch, project, sandbox, role):
    assert not os.path.lexists(project / FREEZE), "the fixture project is frozen"
    result = launch(role)
    assert _missing_literal_rules(result, project, sandbox, ["freeze"]) == [], (
        f"no literal Edit deny rule names the freeze flag for a launched {role}; rules: "
        f"{support.deny_rules(result.settings(), 'Edit')}"
    )


def test_the_literal_rules_are_computed_at_each_launch(launch, project, sandbox):
    """A file and a directory that appear between two launches are named by the second one."""
    new = ["last_head.json", "w1-46-reports"]
    launch(ENGINEER).session()
    support.write(project, f"{RUNTIME}/last_head.json", "{}\n")
    support.write(project, f"{RUNTIME}/w1-46-reports/one.txt", "x\n")
    second = launch(ENGINEER)
    missing = _missing_literal_rules(second, project, sandbox, new)
    assert missing == [], f"names that exist under .gov-runtime/ at launch have no literal Edit deny rule: {missing}"


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_no_literal_rule_names_scratch_or_a_path_under_it(launch, project, sandbox, role):
    """ "Outside ``scratch/``": scratch stays writable for a Bash command too."""
    scratch = os.path.join(os.path.realpath(project), RUNTIME, "scratch")
    literal = support.literal_edit_denials(launch(role), project, sandbox)
    closed = sorted(path for path in literal if path == scratch or path.startswith(scratch + "/"))
    above = sorted(path for path in literal if scratch.startswith(path + "/"))
    assert closed == [] and above == [], f"a literal Edit deny rule closes scratch: {closed + above}"


# --------------------------------------------------------------------------
# The guard: .gov-runtime/ outside scratch/ is refused to every role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", (ORCHESTRATOR, PRODUCT_SPEC))
def test_the_guard_refuses_a_file_tool_write_under_gov_runtime_to_the_roles_the_launcher_does_not_start(
        guard, project, role):
    """DEC-311: "to every role". The four worker roles are in ``test_w1_46_role_settings.py``."""
    for rel in PROTECTED:
        result = guard("Write", w47.write_input("Write", project / rel), role, EVERY_ROLE[role])
        w47.assert_stopped(result, f"Write to {rel} by {role}")


@pytest.mark.parametrize("role", sorted(EVERY_ROLE))
def test_the_guard_refuses_a_plain_bash_write_under_gov_runtime_to_every_role(guard, project, role):
    for rel in PROTECTED:
        command = f"echo x > {rel}"
        result = guard("Bash", w47.bash_input(command), role, EVERY_ROLE[role], cwd=project)
        w47.assert_stopped(result, f"`{command}` by {role}")


@pytest.mark.parametrize("role", sorted(EVERY_ROLE))
def test_scratch_stays_writable_for_every_role(guard, project, role):
    """A file tool and a plain Bash write, to a file that exists and to a new one."""
    result = guard("Write", w47.write_input("Write", project / SEED), role, EVERY_ROLE[role])
    w47.assert_allowed(result, f"Write to {SEED} by {role}")
    command = f"echo x > {RUNTIME}/scratch/w1-46/new.txt"
    result = guard("Bash", w47.bash_input(command), role, EVERY_ROLE[role], cwd=project)
    w47.assert_allowed(result, f"`{command}` by {role}")


# --------------------------------------------------------------------------
# The guard: the destination of ln is a write target
# --------------------------------------------------------------------------

LINK = {"symbolic": "ln -s", "hard": "ln"}
# Destinations an engineer on its ticket (src/gov/guard/**) may not write.
NOT_WRITABLE = {
    "the-runtime-directory": f"{RUNTIME}/w1-46-link",
    "an-acceptance-test": "tests/acceptance/W1-90/test_w1_46_link.py",
    "outside-the-tickets-paths": "docs/w1-46-link.md",
}
WRITABLE = {
    "inside-the-tickets-paths": "src/gov/guard/w1_46_link.py",
    "scratch": f"{RUNTIME}/scratch/w1-46/link.txt",
}


@pytest.mark.parametrize("kind", sorted(LINK))
@pytest.mark.parametrize("name", sorted(NOT_WRITABLE))
def test_the_guard_refuses_ln_to_a_destination_the_role_may_not_write(guard, project, kind, name):
    command = f"{LINK[kind]} {SEED} {NOT_WRITABLE[name]}"
    result = guard("Bash", w47.bash_input(command), ENGINEER, cwd=project)
    w47.assert_stopped(result, f"`{command}` by an engineer")


@pytest.mark.parametrize("kind", sorted(LINK))
@pytest.mark.parametrize("name", sorted(WRITABLE))
def test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write(guard, project, kind, name):
    """The control: the target is a file in scratch, the destination a new name the role may write."""
    command = f"{LINK[kind]} {SEED} {WRITABLE[name]}"
    result = guard("Bash", w47.bash_input(command), ENGINEER, cwd=project)
    w47.assert_allowed(result, f"`{command}` by an engineer")


@pytest.mark.parametrize("command", (
    f"ln -sf {SEED} {RUNTIME}/findings.jsonl",
    f"ln -f {SEED} {RUNTIME}/records.jsonl",
    f"ln -s {SEED} {RUNTIME}/snapshots",
    f"cd {RUNTIME} && ln -s scratch/w1-46/seed.txt w1-46-link",
), ids=("symbolic-forced-onto-the-findings", "hard-forced-onto-the-records", "into-the-snapshots-directory",
        "after-cd-into-the-runtime-directory"))
def test_the_guard_refuses_ln_onto_or_into_a_name_that_exists_under_gov_runtime(guard, project, command):
    """An option before the operands, a destination that is a directory, and a destination relative to ``cd``."""
    result = guard("Bash", w47.bash_input(command), ENGINEER, cwd=project)
    w47.assert_stopped(result, f"`{command}` by an engineer")


@pytest.mark.parametrize("role", (ORCHESTRATOR, RESEARCH))
def test_the_guard_refuses_ln_into_gov_runtime_to_the_orchestrator_and_the_research_role(guard, project, role):
    """ "To every role": the role with the widest scope, and the new one."""
    for kind in sorted(LINK):
        command = f"{LINK[kind]} {SEED} {RUNTIME}/w1-46-link"
        result = guard("Bash", w47.bash_input(command), role, EVERY_ROLE[role], cwd=project)
        w47.assert_stopped(result, f"`{command}` by {role}")


def test_the_guard_holds_a_research_ln_to_the_experiment_folder(guard, project):
    """The research role's allow-list is its folder: ``ln`` into a sibling is refused, into the folder it is not."""
    inside = f"ln -s README.md {FOLDER}/w1-46-link.md"
    w47.assert_allowed(guard("Bash", w47.bash_input(inside), RESEARCH, cwd=project), f"`{inside}` by research")
    sibling = f"ln -s {FOLDER}/README.md experiments/spikes/exp-900/w1-46-link.md"
    w47.assert_stopped(guard("Bash", w47.bash_input(sibling), RESEARCH, cwd=project), f"`{sibling}` by research")
