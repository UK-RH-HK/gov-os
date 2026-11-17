"""W1-46 -- the no-prompt mode and added directories are accepted (Emergency 2, release 0.1.2).

DEC-313 had ``gov launch`` refuse ``--dangerously-skip-permissions``,
``--allow-dangerously-skip-permissions``, ``--permission-mode bypassPermissions``
and ``--add-dir``, and the matching settings keys. Emergency 2
(docs/emergency-2/EMERGENCY-2.md 2.2, 2.3, 2.9; release 0.1.2) supersedes it: agents
have full permission in their repository, worktree and run folder, and the no-prompt
mode is set in the project settings. The refusal cases are retired; in their place
each former refusal is asserted in its positive form: the launch starts and the CLI
gets the arguments unchanged, and the matching keys in the repository's two settings
files no longer refuse the launch.

Controls kept: a harmless permission mode launches, as an argument and as the
settings key; an argument's name inside the prompt's text is passed through.

No session is started.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

ENGINEER, RESEARCH = support.ENGINEER, support.RESEARCH

# A headless worker's ordinary arguments (DEC-183), without a permission mode.
ORDINARY = ("-p", "Do the ticket's work.", "--output-format", "json", "--allowedTools", "Bash,Write", "--model",
            "claude-opus-5-5", "--max-turns", "8")   # W2-60a: a model after -- must be the role's (DEC-839 item 1)
ADDED_DIRECTORY = "/w1-46-added-directory"

FORMERLY_REFUSED = {
    "skip-permissions": ("--dangerously-skip-permissions",),
    "allow-skip-permissions": ("--allow-dangerously-skip-permissions",),
    "bypass-mode": ("--permission-mode", "bypassPermissions"),
    "add-dir": ("--add-dir", ADDED_DIRECTORY),
}


def _placed(arguments, position):
    if position == "alone":
        return arguments
    if position == "last":
        return ORDINARY + arguments
    if position == "first":
        return arguments + ORDINARY
    return ORDINARY[:4] + arguments + ORDINARY[4:]   # in the middle, between two ordinary options


@pytest.mark.parametrize("position", ("alone", "first", "middle", "last"))
@pytest.mark.parametrize("name", sorted(FORMERLY_REFUSED))
def test_a_bypass_or_an_added_directory_is_now_passed_to_the_session_in_any_position(launch, name, position):
    """Emergency 2 (2.2, 2.3): the launch starts and the CLI gets the caller's arguments unchanged, in order."""
    passed = _placed(FORMERLY_REFUSED[name], position)
    result = launch(ENGINEER, None, *passed)
    assert result.run.returncode == 0, f"gov launch refused {FORMERLY_REFUSED[name]}\n{result.describe()}"
    assert support.caller_args_then_template_pair(result.session()["args"], passed), (
        f"the CLI did not get the arguments unchanged: {result.session()['args']}")


@pytest.mark.parametrize("arguments", (("--permission-mode=bypassPermissions",), (f"--add-dir={ADDED_DIRECTORY}",)),
                         ids=("bypass-mode-joined", "add-dir-joined"))
def test_the_joined_spelling_is_passed_too(launch, arguments):
    passed = ORDINARY + arguments
    result = launch(RESEARCH, None, *passed)
    assert result.run.returncode == 0, f"gov launch refused {arguments}\n{result.describe()}"
    assert support.caller_args_then_template_pair(result.session()["args"], passed), result.describe()


def _set_permissions(project, rel, key, value):
    support.rewrite_settings(project, lambda data: data.setdefault("permissions", {}).update({key: value}), rel)


@pytest.mark.parametrize("rel", (support.SETTINGS_REL, support.LOCAL_SETTINGS_REL), ids=("committed", "local"))
@pytest.mark.parametrize("key, value", (("defaultMode", "bypassPermissions"),
                                        ("additionalDirectories", [ADDED_DIRECTORY])),
                         ids=("bypass-default-mode", "additional-directories"))
def test_the_matching_keys_in_the_repositorys_settings_no_longer_refuse_the_launch(launch, project, rel, key, value):
    """Emergency 2 (2.3): the no-prompt mode lives in the project settings; the launcher leaves it to them."""
    _set_permissions(project, rel, key, value)
    result = launch(ENGINEER, None, *ORDINARY)
    assert result.run.returncode == 0, f"gov launch refused permissions.{key} in {rel}\n{result.describe()}"
    result.session()


# --------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------

@pytest.mark.parametrize("arguments", (("--permission-mode", "acceptEdits"), ("--permission-mode=acceptEdits",)),
                         ids=("accept-edits", "accept-edits-joined"))
def test_a_harmless_permission_mode_is_launched(launch, arguments):
    passed = ORDINARY + arguments
    result = launch(ENGINEER, None, *passed)
    assert result.run.returncode == 0, f"gov launch refused a harmless permission mode\n{result.describe()}"
    assert support.caller_args_then_template_pair(result.session()["args"], passed), (
        f"the CLI did not get the arguments unchanged, followed by nothing or the one template pair: "
        f"{result.session()['args']}")


@pytest.mark.parametrize("rel", (support.SETTINGS_REL, support.LOCAL_SETTINGS_REL), ids=("committed", "local"))
def test_a_harmless_default_mode_in_the_repositorys_settings_is_launched(launch, project, rel):
    _set_permissions(project, rel, "defaultMode", "acceptEdits")
    result = launch(ENGINEER, None, *ORDINARY)
    assert result.run.returncode == 0, f"gov launch refused permissions.defaultMode acceptEdits\n{result.describe()}"
    result.session()


def test_an_arguments_name_inside_the_prompt_is_passed_through(launch):
    """A word of the prompt the worker is given is passed through as it is."""
    prompt = "Never use --dangerously-skip-permissions, --add-dir or --permission-mode bypassPermissions."
    result = launch(ENGINEER, None, "-p", prompt, "--permission-mode", "acceptEdits")
    assert result.run.returncode == 0, f"gov launch refused a prompt that names an argument\n{result.describe()}"
    assert prompt in result.session()["args"]
