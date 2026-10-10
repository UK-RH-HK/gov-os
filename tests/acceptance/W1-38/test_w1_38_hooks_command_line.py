"""W1-38 -- the template's rulesync hooks source: the command lines are the kernel template's form (DEC-608).

DEC-608: "the seven command lines of the template's rulesync hooks source are the kernel template's form exactly,
``python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>"``, with no prefix. ... a product's own package
named ``gov`` under its ``src`` can no longer silence the containment check".

No command line is written in this file. The kernel template's command lines are read from
``template/governance/kernel/settings.json`` in each case; the form of the four entries that file does not hold is
what its command line is with the program's file name exchanged (``w1_38_hooks_support.kernel_form``).

The generated settings are those rulesync 24.0.0 writes from the template's sources in the case's own temporary
project. No real session is started.
"""

from __future__ import annotations

import json

import pytest

import w1_38_hooks_support as hooks
import w1_38_support as support

needs_rulesync = pytest.mark.needs_rulesync
PROGRAMS = hooks.kernel_programs()
EVENTS = hooks.source_events()
KERNEL_EVENTS = tuple(event for event in EVENTS if event in hooks.guard_events(hooks.kernel_settings(), PROGRAMS))
OTHER_EVENTS = tuple(event for event in EVENTS if event not in KERNEL_EVENTS)


@pytest.fixture()
def product(generated_project):
    """The generated project with a product's files and one engineer ticket in progress."""
    return hooks.add_product_work(generated_project)


@pytest.fixture()
def session_sandbox(tmp_path):
    """A stand-in home with the ``gov`` package installed, and a temporary folder, outside the project."""
    return hooks.make_session_sandbox(tmp_path / "session")


def _one_generated(settings, event):
    commands = hooks.registered_commands(settings, PROGRAMS, event)
    assert len(commands) == 1, (
        f"{hooks.GENERATED_REL}, generated from {hooks.SOURCE_REL}, registers {len(commands)} guard hook entries "
        f"under {event}; one is expected: {commands}"
    )
    return commands[0]


# ===================================================================
# The form, read from the kernel template's settings
# ===================================================================

def test_the_kernel_template_s_command_lines_share_one_form():
    """The form the four other entries are held to is read from the kernel template's three command lines. That
    reading stands only while the three are one form once the program's file name is taken out, and while the
    form holds nothing else of a program's name."""
    forms = hooks.kernel_forms(PROGRAMS)
    assert sorted(forms) == sorted(KERNEL_EVENTS) and len(KERNEL_EVENTS) == 3 and len(OTHER_EVENTS) == 4, (
        f"{hooks.KERNEL_SETTINGS_REL} registers guard hook entries under {sorted(forms)}; of the events of "
        f"{hooks.SOURCE_REL} it holds {KERNEL_EVENTS} and not {OTHER_EVENTS}"
    )
    form = hooks.kernel_form(PROGRAMS)
    assert form.count(hooks.PROGRAM_PLACE) == 1 and not hooks.own_programs(form, PROGRAMS), (
        f"the form read from {hooks.KERNEL_SETTINGS_REL} still names a program: `{form}`"
    )
    for event in KERNEL_EVENTS:
        command = hooks.kernel_command_line(event, PROGRAMS)
        assert hooks.expected_command_line(event, command, PROGRAMS, event) == command
        assert form.replace(hooks.PROGRAM_PLACE, hooks.own_program(command, PROGRAMS, event)) == command, (
            f"{event}: the form with the program put back is not the kernel template's command line `{command}`"
        )


# ===================================================================
# The generated settings
# ===================================================================

class TestGeneratedCommandLines:
    """The command lines of the settings rulesync generates from the template's source, in a temporary project."""

    @needs_rulesync
    @pytest.mark.parametrize("event", KERNEL_EVENTS)
    def test_the_generated_command_line_is_the_kernel_template_s(self, generated_project, event):
        """Compared, under one event both hold: the command line of the generated guard hook entry with the command
        line of the kernel template's settings, as strings."""
        kernel = hooks.kernel_command_line(event, PROGRAMS)
        generated = _one_generated(support.load_settings(generated_project), event)
        assert generated == kernel, (
            f"{event}: {hooks.GENERATED_REL}, generated from {hooks.SOURCE_REL}, registers the command line "
            f"`{generated}`; {hooks.KERNEL_SETTINGS_REL} registers `{kernel}` (DEC-608: the kernel template's form "
            f"exactly, with no prefix)"
        )

    @needs_rulesync
    @pytest.mark.parametrize("event", OTHER_EVENTS)
    def test_the_generated_command_line_has_the_kernel_template_s_form(self, generated_project, event):
        """Compared, under one event the kernel template's settings do not hold: the command line of the generated
        guard hook entry with the kernel template's command line in which only the program's file name is
        exchanged for the entry's own program."""
        generated = _one_generated(support.load_settings(generated_project), event)
        expected = hooks.expected_command_line(event, generated, PROGRAMS, f"{hooks.GENERATED_REL}, {event}")
        assert generated == expected, (
            f"{event}: {hooks.GENERATED_REL}, generated from {hooks.SOURCE_REL}, registers the command line "
            f"`{generated}`; in the form of {hooks.KERNEL_SETTINGS_REL} it is `{expected}` (DEC-608: the kernel "
            f"template's form exactly, with no prefix)"
        )


# ===================================================================
# The source itself, as written
# ===================================================================

@pytest.mark.parametrize("event", EVENTS)
def test_the_source_s_command_line_is_the_kernel_template_s_form(event):
    """Compared: the command string of the source's entry under one event, as the file holds it, with the kernel
    template's command line for that event, or for an event it does not hold with its form and the entry's own
    program."""
    commands = hooks.source_command_lines()[event]
    assert len(commands) == 1, f"{hooks.SOURCE_REL} holds {len(commands)} entries under {event}; one is expected"
    expected = hooks.expected_command_line(event, commands[0], PROGRAMS, f"{hooks.SOURCE_REL}, {event}")
    assert commands[0] == expected, (
        f"{event}: {hooks.SOURCE_REL} holds the command line `{commands[0]}`; in the form of "
        f"{hooks.KERNEL_SETTINGS_REL} it is `{expected}` (DEC-608: the kernel template's form exactly, with no "
        f"prefix)"
    )


# ===================================================================
# A product's own package named gov under the project's src
# ===================================================================

@pytest.fixture()
def product_with_its_own_gov(product):
    """The product, holding under its own ``src`` a package named ``gov`` that is its own code."""
    return hooks.add_product_package_named_gov(product)


class TestAProductPackageNamedGov:
    """The generated project holds ``src/gov/``, a product's own package with none of the governance package's
    modules; the governance package is installed for the stand-in home (the path file of its user site folder).
    One whole Bash call of the engineer, made from the project's root through the generated commands. The
    ticket's paths are ``src/app/**`` and ``tests/unit/**``."""

    def _call(self, project, sandbox, command, **how):
        return hooks.bash_call_in(project, support.load_settings(project), sandbox, project, command, **how)

    @needs_rulesync
    def test_the_fixture_holds_a_product_package_and_the_installed_governance_package(
        self, product_with_its_own_gov, session_sandbox,
    ):
        """The shape the cases below stand on: with the project's ``src`` ahead of the installed packages,
        ``gov`` is the product's package and has no guard; without it, ``gov`` is the installed governance
        package of this worktree."""
        project = product_with_its_own_gov
        folder, has_guard = hooks.gov_as_imported(project, session_sandbox, first=project / "src")
        assert folder == (project / "src" / "gov").resolve() and not has_guard, (
            f"with the project's src first, `gov` is {folder} and `{hooks.GOVERNANCE_MODULE}` is "
            f"{'there' if has_guard else 'absent'}: the fixture's package is not a product's own"
        )
        folder, has_guard = hooks.gov_as_imported(project, session_sandbox)
        assert folder == (hooks.REPO_ROOT / "src" / "gov").resolve() and has_guard, (
            f"for the stand-in home `gov` is {folder} and `{hooks.GOVERNANCE_MODULE}` is "
            f"{'there' if has_guard else 'absent'}: the governance package is not installed for it"
        )

    @needs_rulesync
    def test_a_change_left_out_of_scope_by_a_failed_command_is_reported_and_recorded(
        self, product_with_its_own_gov, session_sandbox,
    ):
        command = "echo changed >> README.md; exit 3"
        call = self._call(product_with_its_own_gov, session_sandbox, command)
        assert call.decision == "allow" and all(result.returncode == 0 for result in call.before), (
            f"in a project that holds a product package named `gov` under its src, the registered PreToolUse "
            f"commands did not let the fixture call through by the guard's own answer, so no containment check "
            f"follows (DEC-608): {call.describe()}"
        )
        assert call.bash_exit == 3 and "README.md" in hooks.check_support.porcelain_all(product_with_its_own_gov), (
            f"the fixture command `{command}` did not fail after changing README.md: exit {call.bash_exit}"
        )
        assert call.event == hooks.FAILED_CALL_EVENT and call.after, (
            f"`{command}` failed and no {hooks.FAILED_CALL_EVENT} command ran: {call.describe()}"
        )
        assert all(result.returncode == 0 for result in call.after), (
            f"`{command}` failed and a registered {hooks.FAILED_CALL_EVENT} command did not end cleanly: the "
            f"product's package named `gov` silenced the containment check (DEC-608): {call.describe()}"
        )
        assert "README.md" in call.report, (
            f"`{command}` failed after changing README.md outside the ticket's paths, and the agent is not told: "
            f"{call.describe()}"
        )
        findings = [json.loads(line) for line in call.new_findings]
        assert any("README.md" in finding.get("paths", []) for finding in findings), (
            f"`{command}`: no finding for README.md was added to {hooks.check_support.FINDINGS_REL}: {findings}"
        )

    @needs_rulesync
    def test_a_call_the_guard_lets_through_is_let_through_by_its_own_answer(
        self, product_with_its_own_gov, session_sandbox,
    ):
        """The guard's program ends with 0 and writes no refusal, the command runs, the check after it ends with
        0 and stays silent, and nothing is recorded: no failure of the interpreter or of an import took the
        guard's place."""
        command = f"echo changed >> {hooks.IN_SCOPE_FILE}"
        call = self._call(product_with_its_own_gov, session_sandbox, command)
        assert call.decision == "allow" and all(result.returncode == 0 for result in call.before), (
            f"`{command}`, inside the ticket's paths, in a project that holds a product package named `gov` under "
            f"its src: the guard's program did not let it through (DEC-608): {call.describe()}"
        )
        assert call.bash_exit == 0 and hooks.IN_SCOPE_FILE in hooks.check_support.porcelain_all(
            product_with_its_own_gov), f"the fixture command `{command}` did not change {hooks.IN_SCOPE_FILE}"
        assert call.after and all(result.returncode == 0 for result in call.after), (
            f"`{command}`: a registered {call.event} command did not end cleanly: {call.describe()}"
        )
        assert not call.report and not call.new_findings, (
            f"`{command}` changed only {hooks.IN_SCOPE_FILE}, inside the ticket's paths, and the check did not "
            f"stay silent: {call.describe()}; findings {call.new_findings}"
        )

    @needs_rulesync
    def test_a_call_the_guard_refuses_is_refused_by_its_written_refusal(
        self, product_with_its_own_gov, session_sandbox,
    ):
        """An exit 2 would block the call too, but it is the guard failing to import its own package, and it is
        the answer to every call. The refusal held here is the program's: exit 0 and the written refusal."""
        project = product_with_its_own_gov
        command = hooks.refused_call(project)["command"]
        before = hooks.check_support.read(project, hooks.OUT_OF_SCOPE_FILE)
        call = self._call(project, session_sandbox, command, literal=True)
        assert call.before and all(hooks.refused_by_the_program(result) for result in call.before), (
            f"`{command}` by the engineer, a write outside the ticket's paths, in a project that holds a product "
            f"package named `gov` under its src: the guard's program did not answer with its written refusal "
            f"(DEC-608): {call.describe()}"
        )
        assert call.bash_exit is None and hooks.check_support.read(project, hooks.OUT_OF_SCOPE_FILE) == before
        assert not call.new_findings, (
            f"`{command}`: a refusal by the guard's decision records no failure of the guard: {call.new_findings}"
        )
