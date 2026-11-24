"""W1-46 -- the arguments after ``--`` and the repository's hook wiring (batch 3, after implementation).

Described behaviours A and B of the review after implementation (DEC-136), as
Emergency 2 leaves them (docs/emergency-2/EMERGENCY-2.md 2.1, 2.2, 6.1; release
0.1.2): the guard is switched off and retired, so ``gov launch`` no longer
requires it in the repository's settings (DEC-314's refusal of an unwired guard,
of ``disableAllHooks`` and of ``--bare`` is superseded). Those refusal cases are
retired; each is asserted in its positive form: the launch starts.

**A, the arguments after ``--``** (DEC-231: "everything after ``--`` is passed
to the CLI unchanged"). The ordinary arguments of a headless worker (DEC-183,
DEC-232) pass, unchanged and in order; ``--bare`` is passed too.
``--setting-sources`` is still refused with any value: the launcher sets the
session's sources itself. The settings the launcher builds register no hook and
carry no ``disableAllHooks``.

**B, a project whose settings do not wire the guard**: no
``.claude/settings.json``, one that registers no PreToolUse command, or
``disableAllHooks: true`` in the committed or the local settings: launched.

Permission bypass and added directories are in
``test_w1_46_bypass_and_added_directories.py``.

No session is started.
"""

from __future__ import annotations

import json

import pytest

import w1_46_support as support

ENGINEER, RESEARCH = support.ENGINEER, support.RESEARCH

# What a ticket lead gives a headless worker (DEC-183, DEC-232). The prompt names two arguments as words. Since
# W2-60a a model after -- must be the session's. Rewrite-Reason: DEC-1225 (every role launches Sonnet).
HEADLESS = ("-p", "Do the ticket's work. Do not use --bare or --add-dir.", "--output-format", "json",
            "--permission-mode", "acceptEdits", "--allowedTools", "Bash,Write", "--model", "claude-sonnet-5-5",
            "--max-turns", "8")


# --------------------------------------------------------------------------
# A: the arguments after "--"
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", (ENGINEER, RESEARCH))
def test_a_headless_workers_ordinary_arguments_pass_unchanged(launch, role):
    """DEC-231. The control of the cases below; holds since the implementation."""
    result = launch(role, None, *HEADLESS)
    assert result.run.returncode == 0, f"gov launch refused a headless worker's ordinary arguments\n{result.describe()}"
    args = result.session()["args"]
    assert support.caller_args_then_template_pair(args, HEADLESS), (
        f"the CLI did not get the arguments unchanged, in order, followed by nothing or the one template pair: {args}")


@pytest.mark.parametrize("arguments", (("--bare",), HEADLESS + ("--bare",), ("--bare",) + HEADLESS),
                         ids=("alone", "after-the-ordinary-arguments", "before-the-ordinary-arguments"))
def test_the_argument_that_skips_the_hooks_is_now_passed(launch, arguments):
    """Emergency 2: ``--bare`` is no longer refused; the CLI gets it with the caller's other arguments, in order."""
    result = launch(ENGINEER, None, *arguments)
    assert result.run.returncode == 0, f"gov launch refused --bare\n{result.describe()}"
    assert support.caller_args_then_template_pair(result.session()["args"], arguments), result.describe()


@pytest.mark.parametrize("arguments", (("--setting-sources", "user"), ("--setting-sources=user",),
                                       ("--setting-sources", "")),
                         ids=("user-only", "user-only-joined", "no-source"))
def test_no_session_is_started_without_the_projects_settings_unless_the_launcher_wires_the_guard(launch, arguments):
    """The launcher sets the session's setting sources itself: refused (DEC-314, kept by Emergency 2)."""
    launch(ENGINEER).session()
    support.assert_refused(launch(ENGINEER, None, *HEADLESS, *arguments), "--setting-sources", "hook", "guard")


@pytest.mark.parametrize("arguments", (("--setting-sources", "project"), ("--setting-sources=user,project,local",)),
                         ids=("project-only", "every-source-joined"))
def test_setting_sources_refuses_the_launch_with_any_value(launch, arguments):
    """DEC-314: "``--setting-sources`` with any value", also one that names the project's settings."""
    launch(ENGINEER).session()
    support.assert_refused(launch(ENGINEER, None, *HEADLESS, *arguments), "--setting-sources", "hook", "guard")


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_launcher_does_not_register_the_hooks_itself(launch, role):
    """DEC-314: the guard comes from the project's settings alone; the built settings carry no hook key."""
    found = support.hook_keys(launch(role, None, *HEADLESS).settings())
    assert found == [], f"the settings the launcher built for a {role} session carry {found}"


# --------------------------------------------------------------------------
# B: a project whose settings do not wire the guard
# --------------------------------------------------------------------------

def _rewrite(project, change):
    path = project / support.SETTINGS_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _unwire(project, how):
    if how == "no-settings-file":
        (project / support.SETTINGS_REL).unlink()
    elif how == "no-hooks-block":
        _rewrite(project, lambda data: data.pop("hooks", None))
    elif how == "no-pretooluse-command":
        _rewrite(project, lambda data: data.get("hooks", {}).pop("PreToolUse", None))
    elif how == "hooks-off-in-the-committed-settings":
        _rewrite(project, lambda data: data.update(disableAllHooks=True))
    else:
        support.write(project, support.LOCAL_SETTINGS_REL, json.dumps({"disableAllHooks": True}))


UNWIRED = ("no-settings-file", "no-hooks-block", "no-pretooluse-command", "hooks-off-in-the-committed-settings",
           "hooks-off-in-the-local-settings")


@pytest.mark.parametrize("how", UNWIRED)
def test_a_project_that_does_not_wire_the_guard_is_launched(launch, project, how):
    """Emergency 2 (2.2): no guard is required; the launch starts and the built settings still register no hook."""
    _unwire(project, how)
    result = launch(ENGINEER)
    assert result.run.returncode == 0, f"gov launch refused a project without the guard ({how})\n{result.describe()}"
    assert support.hook_keys(result.settings()) == [], result.describe()


def test_hooks_left_on_explicitly_do_not_refuse_the_launch(launch, project):
    """The control: ``disableAllHooks: false`` switches nothing off."""
    support.write(project, support.LOCAL_SETTINGS_REL, json.dumps({"disableAllHooks": False}))
    result = launch(ENGINEER)
    assert result.run.returncode == 0, f"gov launch refused a project whose hooks are on\n{result.describe()}"
    result.session()
