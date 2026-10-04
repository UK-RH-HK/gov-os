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

**Who wires the guard (DEC-314, batch 4).** "``gov launch`` refuses when the
project's settings do not register the guard. The launcher does not register the
hooks itself. As built, the refusal covers a missing or unwired
``.claude/settings.json``, ``disableAllHooks``, ``--bare``, and
``--setting-sources`` with any value." The tests of ``--setting-sources`` and of
B, which accepted either answer of DP-11 in batch 3, now assert the refusal
only: a non-zero exit, a named reason, nothing started. The settings the
launcher builds register no hook and carry no ``disableAllHooks``.

Permission bypass and added directories (DEC-313) are in
``test_w1_46_bypass_and_added_directories.py``.

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
    """Without the project's settings their PreToolUse command is not loaded: refused (DEC-314)."""
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
    """The same project launches before the change, so the change is the reason. Refused (DEC-314)."""
    launch(ENGINEER).session()
    _unwire(project, how)
    support.assert_refused(launch(ENGINEER), "hook", "guard", "settings")


def test_a_research_session_is_not_started_without_the_guard_either(launch, project):
    """The research fence leans on the guard for every path created after launch (KPI success 4)."""
    launch(RESEARCH).session()
    _unwire(project, "no-pretooluse-command")
    support.assert_refused(launch(RESEARCH), "hook", "guard", "settings")


def test_hooks_left_on_explicitly_do_not_refuse_the_launch(launch, project):
    """The control: ``disableAllHooks: false`` switches nothing off."""
    support.write(project, support.LOCAL_SETTINGS_REL, json.dumps({"disableAllHooks": False}))
    result = launch(ENGINEER)
    assert result.run.returncode == 0, f"gov launch refused a project whose hooks are on\n{result.describe()}"
    result.session()
