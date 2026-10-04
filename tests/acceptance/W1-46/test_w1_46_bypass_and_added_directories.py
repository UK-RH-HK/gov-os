"""W1-46 -- no worker session without the permission checks, or with a directory added (batch 4, after implementation).

DEC-313 (owner, on DP-10): "``gov launch`` refuses ``--dangerously-skip-permissions``,
``--permission-mode bypassPermissions`` and ``--add-dir``, in any position, and
the matching settings keys (``permissions.defaultMode: bypassPermissions``,
``permissions.additionalDirectories``). ``--allow-dangerously-skip-permissions``,
which the package also named, is refused with them".

A refusal is a non-zero exit with a named reason, and nothing is started (KPI
success 1's words). Each refusal test first launches the same role in the same
project, so the argument or the key is the reason.

"The matching settings keys" are tested in the two settings files of the
repository the launcher already refuses a ``sandbox`` key in (DEC-233):
``.claude/settings.json`` and ``.claude/settings.local.json``.

Controls: a harmless permission mode launches, as an argument
(``--permission-mode acceptEdits``, what DEC-183 gives a headless worker) and as
the settings key (``permissions.defaultMode: acceptEdits``); an argument's name
inside the prompt's text refuses nothing.

Not tested: ``permissions.additionalDirectories`` with an empty list, and the
keys in a user's or a managed settings file, which no decision names.

No session is started.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

ENGINEER, RESEARCH = support.ENGINEER, support.RESEARCH

# A headless worker's ordinary arguments (DEC-183), without a permission mode.
ORDINARY = ("-p", "Do the ticket's work.", "--output-format", "json", "--allowedTools", "Bash,Write", "--model",
            "haiku", "--max-turns", "8")
ADDED_DIRECTORY = "/w1-46-added-directory"

REFUSED_ARGUMENTS = {
    "skip-permissions": ("--dangerously-skip-permissions",),
    "allow-skip-permissions": ("--allow-dangerously-skip-permissions",),
    "bypass-mode": ("--permission-mode", "bypassPermissions"),
    "add-dir": ("--add-dir", ADDED_DIRECTORY),
}
REASON = ("bypass", "skip-permissions", "permission", "add-dir", "additionalDirectories", "director")


def _placed(arguments, position):
    if position == "alone":
        return arguments
    if position == "last":
        return ORDINARY + arguments
    if position == "first":
        return arguments + ORDINARY
    return ORDINARY[:4] + arguments + ORDINARY[4:]   # in the middle, between two ordinary options


@pytest.mark.parametrize("position", ("alone", "first", "middle", "last"))
@pytest.mark.parametrize("name", sorted(REFUSED_ARGUMENTS))
def test_the_launcher_refuses_a_bypass_or_an_added_directory_in_any_position(launch, name, position):
    """DEC-313: "in any position" among the arguments passed after ``--``."""
    launch(ENGINEER).session()
    support.assert_refused(launch(ENGINEER, None, *_placed(REFUSED_ARGUMENTS[name], position)), *REASON)


@pytest.mark.parametrize("arguments", (("--permission-mode=bypassPermissions",), (f"--add-dir={ADDED_DIRECTORY}",)),
                         ids=("bypass-mode-joined", "add-dir-joined"))
def test_the_launcher_refuses_the_joined_spelling_too(launch, arguments):
    """The CLI reads ``--option=value`` as ``--option value``."""
    launch(ENGINEER).session()
    support.assert_refused(launch(ENGINEER, None, *ORDINARY, *arguments), *REASON)


def test_a_research_session_is_refused_the_same_arguments(launch):
    """The refusal is the launcher's, not one role's: one case for the role with a network grant."""
    launch(RESEARCH).session()
    for name in sorted(REFUSED_ARGUMENTS):
        support.assert_refused(launch(RESEARCH, None, *ORDINARY, *REFUSED_ARGUMENTS[name]), *REASON)


def _set_permissions(project, rel, key, value):
    support.rewrite_settings(project, lambda data: data.setdefault("permissions", {}).update({key: value}), rel)


@pytest.mark.parametrize("rel", (support.SETTINGS_REL, support.LOCAL_SETTINGS_REL), ids=("committed", "local"))
@pytest.mark.parametrize("key, value", (("defaultMode", "bypassPermissions"),
                                        ("additionalDirectories", [ADDED_DIRECTORY])),
                         ids=("bypass-default-mode", "additional-directories"))
def test_the_launcher_refuses_the_matching_keys_in_the_repositorys_settings(launch, project, rel, key, value):
    """DEC-313: ``permissions.defaultMode: bypassPermissions`` and ``permissions.additionalDirectories``."""
    launch(ENGINEER).session()
    _set_permissions(project, rel, key, value)
    support.assert_refused(launch(ENGINEER, None, *ORDINARY), *REASON, "defaultMode")


# --------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------

@pytest.mark.parametrize("arguments", (("--permission-mode", "acceptEdits"), ("--permission-mode=acceptEdits",)),
                         ids=("accept-edits", "accept-edits-joined"))
def test_a_harmless_permission_mode_is_launched(launch, arguments):
    passed = ORDINARY + arguments
    result = launch(ENGINEER, None, *passed)
    assert result.run.returncode == 0, f"gov launch refused a harmless permission mode\n{result.describe()}"
    assert tuple(result.session()["args"][-len(passed):]) == passed, "the CLI did not get the arguments unchanged"
    assert support.sandbox_faults(result.settings()) == []


@pytest.mark.parametrize("rel", (support.SETTINGS_REL, support.LOCAL_SETTINGS_REL), ids=("committed", "local"))
def test_a_harmless_default_mode_in_the_repositorys_settings_is_launched(launch, project, rel):
    _set_permissions(project, rel, "defaultMode", "acceptEdits")
    result = launch(ENGINEER, None, *ORDINARY)
    assert result.run.returncode == 0, f"gov launch refused permissions.defaultMode acceptEdits\n{result.describe()}"
    result.session()


def test_an_arguments_name_inside_the_prompt_refuses_nothing(launch):
    """Only an argument of the CLI is refused, not a word of the prompt the worker is given."""
    prompt = "Never use --dangerously-skip-permissions, --add-dir or --permission-mode bypassPermissions."
    result = launch(ENGINEER, None, "-p", prompt, "--permission-mode", "acceptEdits")
    assert result.run.returncode == 0, f"gov launch refused a prompt that names an argument\n{result.describe()}"
    assert prompt in result.session()["args"]
