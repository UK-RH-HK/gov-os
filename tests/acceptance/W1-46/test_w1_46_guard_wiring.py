"""W1-46 -- no worker session is started that the guard does not decide for (batch 3, after implementation).

Described behaviours A and B of the review after implementation (DEC-136).

KPI success 2 [CAP-61.b]: "sets GOV_ROLE and GOV_TICKET; an acceptance test
shows that a launched worker is sandboxed and that both variables reach the
guard (DEC-161)". KPI success 8 [CAP-58.d]: in a launched worker session "a
file-tool write outside it is refused by the permission rules and the guard".
MR-3: "An implementer write to ``tests/acceptance/**`` is refused by the guard".
DEC-135: a probe finding that could let an implementer change acceptance tests
is fixed.

**A, the arguments after ``--``** (DEC-231: "everything after ``--`` is passed
to the CLI unchanged"). The CLI's own help says of ``--bare``: "Minimal mode:
skip hooks (those defined in settings ...)". A session started with it has no
guard, whatever the launcher builds, and the launcher may not drop the argument:
it refuses. ``--setting-sources`` chooses which of the user, project and local
settings are loaded; without the project's settings the guard they register is
not loaded. The ordinary arguments of a headless worker (DEC-183, DEC-232)
still pass, unchanged and in order.

**B, a project whose settings do not wire the guard**: no
``.claude/settings.json``, one that registers no PreToolUse command, or
``disableAllHooks: true`` in the committed or the local settings.

Who wires the guard is not decided (README, DP-11): the launcher may refuse, as
DEC-233 refuses a ``sandbox`` key, or register the guard in the settings it
builds. The tests of ``--setting-sources`` and of B hold under both: the launch
is refused, or the one ``--settings`` value registers a PreToolUse command for
every write tool (and switches the hooks back on).

Not tested, see DP-10 in the README: ``--dangerously-skip-permissions``,
``--allow-dangerously-skip-permissions``, ``--permission-mode
bypassPermissions``, ``--add-dir``, and the settings keys
``permissions.defaultMode`` and ``permissions.additionalDirectories``.

No session is started.
"""

from __future__ import annotations

import json

import pytest

import w1_46_support as support

ENGINEER, RESEARCH = support.ENGINEER, support.RESEARCH

# What a ticket lead gives a headless worker (DEC-183, DEC-232). The prompt names two arguments as words.
HEADLESS = ("-p", "Do the ticket's work. Do not use --bare or --add-dir.", "--output-format", "json",
            "--permission-mode", "acceptEdits", "--allowedTools", "Bash,Write", "--model", "haiku", "--max-turns", "8")


# --------------------------------------------------------------------------
# A: the arguments after "--"
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", (ENGINEER, RESEARCH))
def test_a_headless_workers_ordinary_arguments_pass_unchanged(launch, role):
    """DEC-231. The control of the refusals below; holds since the implementation."""
    result = launch(role, None, *HEADLESS)
    assert result.run.returncode == 0, f"gov launch refused a headless worker's ordinary arguments\n{result.describe()}"
    args = result.session()["args"]
    assert tuple(args[-len(HEADLESS):]) == HEADLESS, f"the CLI did not get the arguments unchanged, in order: {args}"
    assert support.sandbox_faults(result.settings()) == []


@pytest.mark.parametrize("arguments", (("--bare",), HEADLESS + ("--bare",), ("--bare",) + HEADLESS),
                         ids=("alone", "after-the-ordinary-arguments", "before-the-ordinary-arguments"))
def test_the_launcher_refuses_the_argument_that_skips_the_hooks(launch, arguments):
    """``--bare`` skips every hook: non-zero exit, a named reason, nothing started."""
    launch(ENGINEER).session()
    support.assert_refused(launch(ENGINEER, None, *arguments), "--bare", "hook", "guard")


@pytest.mark.parametrize("arguments", (("--setting-sources", "user"), ("--setting-sources=user",),
                                       ("--setting-sources", "")),
                         ids=("user-only", "user-only-joined", "no-source"))
def test_no_session_is_started_without_the_projects_settings_unless_the_launcher_wires_the_guard(launch, arguments):
    """Without the project's settings their PreToolUse command is not loaded."""
    launch(ENGINEER).session()
    support.assert_no_session_without_the_guard(launch(ENGINEER, None, *HEADLESS, *arguments))


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
        _rewrite(project, lambda data: data.pop("hooks"))
    elif how == "no-pretooluse-command":
        _rewrite(project, lambda data: data["hooks"].pop("PreToolUse"))
    elif how == "hooks-off-in-the-committed-settings":
        _rewrite(project, lambda data: data.update(disableAllHooks=True))
    else:
        support.write(project, support.LOCAL_SETTINGS_REL, json.dumps({"disableAllHooks": True}))


UNWIRED = ("no-settings-file", "no-hooks-block", "no-pretooluse-command", "hooks-off-in-the-committed-settings",
           "hooks-off-in-the-local-settings")


@pytest.mark.parametrize("how", UNWIRED)
def test_no_session_is_started_in_a_project_that_does_not_wire_the_guard(launch, project, how):
    """The same project launches before the change, so the change is the reason."""
    launch(ENGINEER).session()
    _unwire(project, how)
    support.assert_no_session_without_the_guard(launch(ENGINEER), hooks_switched_off=how.startswith("hooks-off"))


def test_a_research_session_is_not_started_without_the_guard_either(launch, project):
    """The research fence leans on the guard for every path created after launch (KPI success 4)."""
    launch(RESEARCH).session()
    _unwire(project, "no-pretooluse-command")
    support.assert_no_session_without_the_guard(launch(RESEARCH))


def test_hooks_left_on_explicitly_do_not_refuse_the_launch(launch, project):
    """The control: ``disableAllHooks: false`` switches nothing off."""
    support.write(project, support.LOCAL_SETTINGS_REL, json.dumps({"disableAllHooks": False}))
    result = launch(ENGINEER)
    assert result.run.returncode == 0, f"gov launch refused a project whose hooks are on\n{result.describe()}"
    result.session()
