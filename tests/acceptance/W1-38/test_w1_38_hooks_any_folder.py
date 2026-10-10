"""W1-38 -- the template's rulesync hooks source: every hook starts from any folder (DEC-603, DEC-607).

DEC-603: "the seven command lines of the template's rulesync hooks source (``template/.rulesync/hooks.jsonc``)
take the kernel template's form, with ``$CLAUDE_PROJECT_DIR`` in the path, so hooks start from any folder."

Measured before it (the orchestrator, harness 2.1.288): the harness starts every hook in the session's current
folder; after one ``cd`` a hook registered by a relative path cannot start. An adopted project's sessions run
under the settings rulesync generates from the source, so the cases generate from it in a temporary project
(rulesync 24.0.0) and run each registered command through the shell exactly as registered, with the project's
folder in ``CLAUDE_PROJECT_DIR`` and another folder as working directory. No real session is started; that is
the orchestrator's measurement after the merge (DEC-607).

No case here chooses between a command line with the ``PYTHONPATH`` prefix and one without it: that is package
P-7 of the README. The stand-in home holds the ``gov`` package as an installed one and the project holds none,
which both forms serve alike.
"""

from __future__ import annotations

import json

import pytest

import w1_38_hooks_support as hooks
import w1_38_support as support

needs_rulesync = pytest.mark.needs_rulesync
EVENTS = hooks.source_events()
FOLDERS = hooks.FOLDER_KINDS


@pytest.fixture(scope="module")
def programs():
    """The file names of the kernel template's hook programs."""
    return hooks.kernel_programs()


@pytest.fixture()
def product(generated_project):
    """The generated project with a product's files and one engineer ticket in progress."""
    return hooks.add_product_work(generated_project)


@pytest.fixture()
def session_sandbox(tmp_path):
    """A stand-in home with the ``gov`` package installed, and a temporary folder, outside the project."""
    return hooks.make_session_sandbox(tmp_path / "session")


def _one_command(settings, programs, event):
    commands = hooks.registered_commands(settings, programs, event)
    assert len(commands) == 1, (
        f"{hooks.GENERATED_REL}, generated from {hooks.SOURCE_REL}, registers {len(commands)} guard hook entries "
        f"under {event}; one is expected: {commands}"
    )
    return commands[0]


def _assert_started(started, where):
    assert started.own_answer, (
        f"{started.event}: the command {hooks.GENERATED_REL} registers, generated from {hooks.SOURCE_REL}, did not "
        f"start its program and give the program's own answer when the session's current folder is {where} "
        f"(DEC-603: hooks start from any folder): {started.describe()}"
    )


# ===================================================================
# The seven entries, as rulesync generates them
# ===================================================================

def test_the_source_holds_the_seven_entries_the_cases_start():
    """The cases below are made for the events of the source as it stands; an entry added later gets a case
    only when this list is read again, so the count is held."""
    assert sorted(EVENTS) == sorted(
        ("PreToolUse", "PostToolUse", "PostToolUseFailure", "SessionStart", "Stop", "PreCompact", "SubagentStop")
    ), f"{hooks.SOURCE_REL} holds entries under {EVENTS}"


@needs_rulesync
def test_the_events_started_are_the_events_rulesync_generates_guard_entries_under(generated_project, programs):
    """No generated guard hook entry is left out of the cases below, and none is started that is not generated."""
    generated = hooks.guard_events(support.load_settings(generated_project), programs)
    assert sorted(generated) == sorted(EVENTS), (
        f"{hooks.GENERATED_REL} registers guard hook entries under {generated}; the cases start {EVENTS}"
    )


class TestEveryEntryStartsFromAnyFolder:
    """Each of the seven registered commands, run through the shell as registered and as the harness runs it,
    starts its program and gives the program's own answer whatever the session's current folder is. What that
    answer is for each program: ``w1_38_hooks_support.start_entry``. An exit code alone is never taken for it."""

    @needs_rulesync
    @pytest.mark.parametrize("folder", FOLDERS)
    @pytest.mark.parametrize("event", EVENTS)
    def test_the_registered_command_starts_its_program(self, product, session_sandbox, programs, tmp_path,
                                                       event, folder):
        settings = support.load_settings(product)
        where = hooks.folder_of(product, folder, tmp_path / "elsewhere")
        started = hooks.start_entry(event, _one_command(settings, programs, event), product, session_sandbox,
                                    where, settings)
        _assert_started(started, f"{folder} ({where})")


# ===================================================================
# A project folder whose name holds a space
# ===================================================================

@pytest.fixture()
def spaced_product(tmp_path, rulesync_bin):
    """The same project in a folder whose name holds a space, generated and given a product's files."""
    root = tmp_path / "a folder with spaces" / "the project"
    root.mkdir(parents=True)
    support.init_git(root)
    support.build_project_from_template(root)
    result = support.run_rulesync_generate(root)
    assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
    support.commit_all(root, "generated")
    return hooks.add_product_work(root)


class TestAProjectFolderWithASpace:
    @needs_rulesync
    @pytest.mark.parametrize("event", EVENTS)
    def test_the_registered_command_starts_from_a_subfolder(self, spaced_product, session_sandbox, programs,
                                                            tmp_path, event):
        """The path of the program holds the project's folder, so a folder name with a space reaches the shell:
        the registered command still starts its program (the kernel template's form quotes the path)."""
        settings = support.load_settings(spaced_product)
        where = hooks.folder_of(spaced_product, "subfolder", tmp_path / "elsewhere")
        started = hooks.start_entry(event, _one_command(settings, programs, event), spaced_product,
                                    session_sandbox, where, settings)
        _assert_started(started, f"a subfolder of a project whose folder name holds a space ({where})")


# ===================================================================
# A whole Bash call after the session changed its folder
# ===================================================================

class TestABashCallAfterAChangeOfDirectory:
    """One whole Bash call of a session whose current folder is a subfolder of the project (``src/app``), through
    the generated commands: the PreToolUse commands, the command for real in that folder, then the commands of
    the event that follows, each started in that folder. The engineer works on a ticket whose paths are
    ``src/app/**`` and ``tests/unit/**``."""

    def _call(self, product, sandbox, command, **how):
        folder = hooks.folder_of(product, "subfolder", None)
        return hooks.bash_call_in(product, support.load_settings(product), sandbox, folder, command, **how)

    @needs_rulesync
    def test_a_change_left_out_of_scope_by_a_failed_command_is_reported_and_recorded(self, product, session_sandbox):
        command = "echo changed >> ../../README.md; exit 3"
        call = self._call(product, session_sandbox, command)
        assert call.decision == "allow", (
            f"in a subfolder the registered PreToolUse commands did not let the fixture call through, so every "
            f"call of a session that changed its folder is blocked (DEC-603): {call.describe()}"
        )
        assert call.bash_exit == 3 and "README.md" in hooks.check_support.porcelain_all(product), (
            f"the fixture command `{command}` did not fail after changing README.md: exit {call.bash_exit}"
        )
        assert call.event == hooks.FAILED_CALL_EVENT and call.after, (
            f"`{command}` failed in a subfolder and no {hooks.FAILED_CALL_EVENT} command ran: {call.describe()}"
        )
        assert all(result.returncode == 0 for result in call.after), (
            f"`{command}` failed in a subfolder and a registered {hooks.FAILED_CALL_EVENT} command did not end "
            f"cleanly, so no containment check ran: {call.describe()}"
        )
        assert "README.md" in call.report, (
            f"`{command}` failed in a subfolder after changing README.md outside the ticket's paths, and the agent "
            f"is not told: {call.describe()}"
        )
        findings = [json.loads(line) for line in call.new_findings]
        assert any("README.md" in finding.get("paths", []) for finding in findings), (
            f"`{command}`: no finding for README.md was added to {hooks.check_support.FINDINGS_REL}: {findings}"
        )

    @needs_rulesync
    def test_an_ordinary_allowed_call_is_not_blocked(self, product, session_sandbox):
        command = "echo changed >> main.py"
        call = self._call(product, session_sandbox, command)
        assert call.decision == "allow", (
            f"`{command}` in {hooks.SUBFOLDER_REL}, inside the ticket's paths, was not let through: a session that "
            f"changed its folder is blocked at every later call (DEC-603): {call.describe()}"
        )
        assert call.bash_exit == 0 and hooks.IN_SCOPE_FILE in hooks.check_support.porcelain_all(product), (
            f"the fixture command `{command}` did not change {hooks.IN_SCOPE_FILE}: exit {call.bash_exit}"
        )
        assert call.after and all(result.returncode == 0 for result in call.after), (
            f"`{command}`: a registered {call.event} command did not end cleanly in a subfolder: {call.describe()}"
        )
        assert not call.report and not call.new_findings, (
            f"`{command}` changed only {hooks.IN_SCOPE_FILE}, inside the ticket's paths, and the check did not "
            f"stay silent: {call.describe()}; findings {call.new_findings}"
        )

    @needs_rulesync
    def test_a_call_the_guard_refuses_from_the_root_is_refused_in_a_subfolder_too(self, product, session_sandbox):
        """The refusal is the guard's own in both folders: its program ended with 0 and wrote the refusal. An exit
        2 in the subfolder would block the call too, but it is the interpreter not finding the program."""
        command = hooks.refused_call(product)["command"]
        settings = support.load_settings(product)
        before = hooks.check_support.read(product, hooks.OUT_OF_SCOPE_FILE)
        for kind in ("root", "subfolder"):
            folder = hooks.folder_of(product, kind, None)
            call = hooks.bash_call_in(product, settings, session_sandbox, folder, command, literal=True)
            assert call.before and all(hooks.refused_by_the_program(result) for result in call.before), (
                f"`{command}` by the engineer, a write outside the ticket's paths, with the session in the "
                f"project's {kind}: the guard's program did not answer with its refusal: {call.describe()}"
            )
            assert call.bash_exit is None and hooks.check_support.read(product, hooks.OUT_OF_SCOPE_FILE) == before
