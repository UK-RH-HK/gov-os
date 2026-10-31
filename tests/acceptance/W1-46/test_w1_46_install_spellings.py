"""W1-46 -- ``uv run -w<package>``: the short option with its value joined (batch 3, after implementation).

Described behaviour G of the review after implementation (DEC-136).

KPI failure 7: "A role other than research and the orchestrator gets an install
command through". DEC-174: ``uv run --with`` is an install. DEC-216: "the
install rule knows ``uv``'s value options ``--directory``, ``--project``,
``--cache-dir`` and ``--config-file``, plus ``uv run -w``". ``-w<package>`` is
``uv run -w`` written as a short option is commonly written; ``uv run -w
<package>`` and ``uv run --with=<package>`` are decided already.

Only this spelling is tested. The others the review saw are left as residuals
under the proportion rule (DEC-135; Contract item CAP-25.c: argv analysis is a
non-goal): the README lists them.

Each command is text in the hook's input. None is run.

Rewrite-Reason: DEC-953 item 2 (W2-90, DEC-957, DEC-906). The cases that asked this repository's live guard now
ask the kernel's: the ``kernel_*`` fixtures are W1-46's launch project built on a project generated from the
template, whose ``.claude/settings.json`` rulesync generates from the template's sources, and the PreToolUse
lines those settings register, run from ``governance/kernel/hooks/`` (``tests/acceptance/W2-90/README.md``).
Each moved case names its fixtures by their old names in its first line; its verdict is the same.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

w47 = support.w47
RESEARCH = support.RESEARCH
ORCHESTRATOR = "orchestrator"
JOINED = ("uv run -wrequests script.py", "uv run -wrequests==2.32.0 python script.py")


@pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
def test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles(kernel_guard, kernel_project, role):
    guard, project = kernel_guard, kernel_project
    for command in JOINED:
        result = guard("Bash", w47.bash_input(command), role, cwd=project)
        w47.assert_denied_by_rule(result, f"`{command}` by {role}")


def test_uv_run_w_with_its_value_joined_is_denied_to_research_outside_its_folder(kernel_guard, kernel_project):
    guard, project = kernel_guard, kernel_project
    for cwd in (project, project / "experiments/spikes/exp-900"):
        result = guard("Bash", w47.bash_input(JOINED[0]), RESEARCH, cwd=cwd)
        w47.assert_denied_by_rule(result, f"`{JOINED[0]}` by research in {cwd.name}")


def test_uv_run_w_with_its_value_joined_is_let_through_for_research_in_its_folder(kernel_guard, kernel_project):
    """The exception still holds for this spelling (DEC-163, DEC-240). Holds since the implementation."""
    guard, project = kernel_guard, kernel_project
    result = guard("Bash", w47.bash_input(JOINED[0]), RESEARCH, cwd=project / support.EXPERIMENT_REL)
    w47.assert_allowed(result, f"`{JOINED[0]}` by research in its experiment folder")


def test_the_orchestrator_is_asked_about_uv_run_w_with_its_value_joined(kernel_guard, kernel_project):
    """DEC-174: the uv installs "keep their ask for the orchestrator" (DEC-083)."""
    guard, project = kernel_guard, kernel_project
    result = guard("Bash", w47.bash_input(JOINED[0]), ORCHESTRATOR, support.check_support.ORCHESTRATOR_TICKET_ID,
                   cwd=project)
    assert result.decision == "ask", f"`{JOINED[0]}` by the orchestrator did not ask: {result.describe()}"


def test_a_uv_run_whose_script_argument_starts_with_w_is_no_install(kernel_guard, kernel_project):
    """The control: ``-w`` is ``uv run``'s option, not the script's. Holds since the implementation."""
    guard, project = kernel_guard, kernel_project
    command = "uv run script.py -wide"
    result = guard("Bash", w47.bash_input(command), support.ENGINEER, cwd=project)
    w47.assert_allowed(result, f"`{command}` by the engineer")
