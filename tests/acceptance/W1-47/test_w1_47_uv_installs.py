"""W1-47 -- four ``uv`` forms are installs.

KPI success 6: "The guard's install rule recognises uv add, uv sync,
uv run --with and uvx as installs, with or without options before the
subcommand: from the orchestrator they return an ask decision, from engineer,
independent test designer and independent auditor they are denied, and a uv run
without --with is not classified by this change; the research role's exception
(DEC-163, W1-46) still lets them through inside its experiment folder; the
acceptance tests of W1-04 still pass (DEC-174) [CAP-25.g]".
KPI failure 6: "uv add, uv sync, uv run --with or uvx runs from the orchestrator
without an ask, or from engineer, independent test designer or independent
auditor without a denial".

Each command is text in the hook's input. None is run, so nothing is installed
and no network is used.

Not tested here, and why: the research role's exception (the role comes with
W1-46, which depends on this ticket), and an option before the subcommand that
takes its value as a separate word (``--directory <path>``). Both are decision
packages in the README.
"""

from __future__ import annotations

import pytest

import w1_47_support as support

ORCHESTRATOR = support.EVERY_ROLE[support.ORCHESTRATOR]
DENIED_ROLES = (support.ENGINEER, support.TEST_DESIGNER, support.AUDITOR)

# The four forms as the KPI names them.
PLAIN = {
    "uv-add": "uv add requests",
    "uv-sync": "uv sync",
    "uv-run-with": "uv run --with requests python script.py",
    "uvx": "uvx ruff check .",
}
# The same forms with more words, and with options before the subcommand. Every option here is one word:
# a flag, or ``--name=value``.
VARIANTS = {
    "uv-add-several": "uv add requests rich",
    "uv-add-dev": "uv add --dev pytest",
    "uv-sync-frozen": "uv sync --frozen",
    "uv-run-with-after-a-run-option": "uv run --no-project --with rich python script.py",
    "uv-run-with-two-packages": "uv run --with requests --with rich python script.py",
    "uvx-with-a-version": "uvx ruff@latest check .",
    "uvx-from": "uvx --from httpie http --version",
    "option-q-add": "uv -q add requests",
    "option-quiet-add": "uv --quiet add requests",
    "option-no-cache-sync": "uv --no-cache sync",
    "option-offline-sync": "uv --offline sync",
    "option-q-run-with": "uv -q run --with requests python script.py",
    "option-no-cache-run-with": "uv --no-cache run --with requests python script.py",
    "option-with-equals-add": "uv --color=never add requests",
    "two-options-sync": "uv -q --no-cache sync",
    "option-q-uvx": "uvx -q ruff check .",
    "after-cd": "cd /tmp && uv add requests",
    "after-another-command": "git status --porcelain; uvx ruff check .",
    "second-of-two": "echo start && uv sync",
}
INSTALLS = {**PLAIN, **VARIANTS}

# Commands this change does not classify. The KPI names ``uv run`` without ``--with``; the ticket's body and
# ``governance/project/bootstrap.md`` ("What stays without a prompt") name the others.
NOT_CLASSIFIED = {
    "uv-run": "uv run python script.py",
    "uv-run-a-tool": "uv run pytest -q",
    "uv-run-with-requirements": "uv run --with-requirements requirements.txt python script.py",
    "option-q-uv-run": "uv -q run python script.py",
    "uv-lock": "uv lock",
    "uv-remove": "uv remove requests",
    "uv-venv": "uv venv",
    "uv-pip-sync": "uv pip sync requirements.txt",
    "uv-pip-list": "uv pip list",
    "uv-tool-run": "uv tool run ruff check .",
    "uv-version": "uv --version",
}


@pytest.mark.parametrize("name", sorted(INSTALLS))
def test_the_orchestrator_is_asked(project, guard, name):
    """KPI success 6, failure 6 [CAP-25.g]: ``ask``, the owner's approval prompt (DEC-083)."""
    command = INSTALLS[name]
    result = guard(project, "Bash", support.bash_input(command), ORCHESTRATOR)
    assert result.decision == "ask", f"`{command}` by the orchestrator did not ask: {result.describe()}"


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
@pytest.mark.parametrize("name", sorted(PLAIN))
def test_the_orchestrator_is_asked_in_every_permission_mode(project, guard, name, mode):
    """KPI failure 6: no permission mode runs the command without the prompt (W1-04: also in Auto mode)."""
    command = PLAIN[name]
    result = guard(project, "Bash", support.bash_input(command), ORCHESTRATOR, mode=mode)
    assert result.decision == "ask", (
        f"`{command}` by the orchestrator in {mode} mode did not ask: {result.describe()}"
    )


@pytest.mark.parametrize("role", DENIED_ROLES)
@pytest.mark.parametrize("name", sorted(INSTALLS))
def test_engineer_test_designer_and_auditor_are_denied(project, guard, name, role):
    """KPI success 6, failure 6 [CAP-25.g]."""
    command = INSTALLS[name]
    result = guard(project, "Bash", support.bash_input(command), support.EVERY_ROLE[role])
    support.assert_denied_by_rule(result, f"`{command}` by {role}")


@pytest.mark.parametrize("role", (support.ORCHESTRATOR, *DENIED_ROLES))
@pytest.mark.parametrize("name", sorted(NOT_CLASSIFIED))
def test_the_other_uv_commands_are_not_classified(project, guard, name, role):
    """KPI success 6: "a uv run without --with is not classified by this change"; neither are the others."""
    command = NOT_CLASSIFIED[name]
    result = guard(project, "Bash", support.bash_input(command), support.EVERY_ROLE[role])
    support.assert_allowed(result, f"`{command}` by {role}")


@pytest.mark.parametrize("command", ("uv pip install requests", "uv tool install ruff", "uv -q pip install requests"))
def test_the_uv_installs_of_w1_04_are_still_asked(project, guard, command):
    """KPI success 6: the change adds four forms and takes none away."""
    result = guard(project, "Bash", support.bash_input(command), ORCHESTRATOR)
    assert result.decision == "ask", f"`{command}` by the orchestrator did not ask: {result.describe()}"
