"""W1-02 — the helper that lists the registered hooks (DEC-525).

Owner's order: "For hook listings, a small helper prints only the hook events,
with the deny lines redacted", so that no session needs to open the settings
file to know which hooks are registered.

The interface these cases require (README, "The helper"):

- **Invocation.** ``python3 -m gov.guard.hooks``, no argument. The project is
  ``CLAUDE_PROJECT_DIR`` or, without it, the working directory; the file read
  is that project's ``.claude/settings.json`` and nothing else.
- **Output.** One JSON array on standard output, exit code 0: one object per
  registered hook command, with exactly the keys ``event``, ``matcher`` and
  ``command``, in the file's order. A matcher that is left out is ``""``.
- **Redaction.** A value of ``permissions.deny`` that appears inside a hook
  command is replaced by ``[redacted]``.
- **No hooks** (no ``hooks`` key, or an empty one): ``[]``, exit code 0.
- **No settings file,** or one that is not valid JSON: exit code 1, nothing on
  standard output, one line on standard error that names
  ``.claude/settings.json`` and carries nothing of the file.

The settings file is a stand-in written here. The helper is run as a process;
that the guard lets its command through is held in
``test_w1_02_protected_reads_open.py``.

Red before the change: the module does not exist.
"""

from __future__ import annotations

import json

import pytest

import w1_02_protected_support as protected
import w1_02_support as support


@pytest.fixture()
def listed(tmp_path):
    """The stand-in directory a stand-in deny line names. It is never created."""
    return tmp_path / "sandbox" / "elsewhere" / "w1-02-stand-in-held-out"


@pytest.fixture()
def settings(project, listed):
    """The fixture project with the stand-in settings file in place."""
    protected.write_settings(project, protected.stand_in_settings(listed))
    return project


def _listing(run):
    assert run.returncode == 0, f"the helper exited with {run.returncode}: {run.stderr.strip()[:300]!r}"
    try:
        return json.loads(run.stdout)
    except ValueError:
        pytest.fail("the helper's standard output is not one JSON document", pytrace=False)


def _assert_nothing_of(run, secrets, what):
    said = run.stdout + "\n" + run.stderr
    shown = [index for index, secret in enumerate(secrets) if secret in said]
    assert not shown, f"{what} carries {len(shown)} value(s) of the settings file that are no hook (positions {shown})"


def test_the_helper_prints_the_registered_hooks_and_nothing_else(settings, sandbox, listed):
    """Line 4: event, matcher and command of every registered hook; a deny value inside a command is redacted."""
    run = protected.run_helper(settings, sandbox)
    assert _listing(run) == protected.expected_listing()


def test_the_listing_carries_no_deny_line_permission_or_environment_entry(settings, sandbox, listed):
    """Line 4: no deny line, no permission entry, no environment entry, nothing but hooks."""
    run = protected.run_helper(settings, sandbox)
    assert run.returncode == 0, f"the helper exited with {run.returncode}"
    _assert_nothing_of(run, protected.settings_secrets(listed), "the listing")
    for key in ("permissions", "deny", "allow", "env", "sandbox", "timeout"):
        assert f'"{key}"' not in run.stdout, f"the listing carries the key {key!r}"


def test_a_deny_value_inside_a_hook_command_is_redacted(settings, sandbox, listed):
    """Line 4: the command stays listed, with the deny value replaced."""
    commands = [row["command"] for row in _listing(protected.run_helper(settings, sandbox))]
    assert f"{protected.LEAK_PREFIX}{protected.REDACTED}{protected.LEAK_SUFFIX}" in commands
    assert not [c for c in commands if protected.deny_read_rule(listed) in c], "a deny value is in a listed command"


def test_the_working_directory_names_the_project_without_the_variable(settings, sandbox):
    """An agent's shell starts in the project root; ``CLAUDE_PROJECT_DIR`` may not be set there."""
    run = protected.run_helper(settings, sandbox, project_dir=False)
    assert _listing(run) == protected.expected_listing()


def test_the_variable_names_the_project_from_another_directory(settings, sandbox):
    """``CLAUDE_PROJECT_DIR`` wins over the working directory, as it does for the hooks."""
    run = protected.run_helper(settings, sandbox, cwd=sandbox.elsewhere)
    assert _listing(run) == protected.expected_listing()


@pytest.mark.parametrize("name", ["no-hooks-key", "empty-hooks", "empty-object"])
def test_a_settings_file_without_hooks_gives_an_empty_listing(project, sandbox, listed, name):
    """Line 4: no hook is registered; the answer is an empty list and nothing of the file."""
    value = {
        "no-hooks-key": {k: v for k, v in protected.stand_in_settings(listed).items() if k != "hooks"},
        "empty-hooks": {**protected.stand_in_settings(listed), "hooks": {}},
        "empty-object": {},
    }[name]
    protected.write_settings(project, value)
    run = protected.run_helper(project, sandbox)
    assert _listing(run) == []
    _assert_nothing_of(run, protected.settings_secrets(listed), "the empty listing")


def _assert_stated_failure(run, what):
    assert run.returncode == 1, f"the helper exited with {run.returncode} on {what}; the stated result is 1"
    assert run.stdout == "", f"the helper printed a listing on {what}"
    lines = run.stderr.strip().splitlines()
    assert len(lines) == 1, f"the helper's message on {what} is {len(lines)} lines, not one (a traceback?)"
    assert protected.SETTINGS_REL in lines[0], (
        f"the helper's message on {what} does not name {protected.SETTINGS_REL}: {lines[0][:200]!r}"
    )


def test_a_missing_settings_file_gives_a_stated_failure(project, sandbox):
    """Line 4: no file, no listing: exit code 1 and one line."""
    (project / protected.SETTINGS_REL).unlink()
    _assert_stated_failure(protected.run_helper(project, sandbox), "a missing settings file")


@pytest.mark.parametrize("name", ["cut-off", "not-json-at-all"])
def test_a_settings_file_that_is_not_valid_json_gives_a_stated_failure(project, sandbox, listed, name):
    """Line 4: the message carries nothing of the file, though a parser's own message could quote it."""
    whole = json.dumps(protected.stand_in_settings(listed), indent=2)
    text = {
        "cut-off": whole[: whole.index('"hooks"')],
        "not-json-at-all": f"deny: {protected.deny_read_rule(listed)}\nenv: {protected.STAND_IN_ENV_VALUE}\n",
    }[name]
    protected.write_settings(project, text)
    run = protected.run_helper(project, sandbox)
    _assert_stated_failure(run, f"a settings file that is not valid JSON ({name})")
    _assert_nothing_of(run, protected.settings_secrets(listed), "the helper's message")


def test_the_helper_writes_nothing(settings, sandbox):
    """A listing is a read: the project is as git saw it before."""
    before = support.porcelain(settings)
    run = protected.run_helper(settings, sandbox)
    assert run.returncode == 0, f"the helper exited with {run.returncode}"
    assert support.porcelain(settings) == before, "the helper changed the working tree"
