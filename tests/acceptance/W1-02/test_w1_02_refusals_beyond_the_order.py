"""W1-02 — the refusals beyond the order stand as built (DEC-548, DP-5).

DEC-548: "The refusals beyond the order stand as built: a shell command that
only mentions the settings file's path as text; a shell word that is a folder
holding either file or a folder above it inside the project, also in a command
that does not read; ``git -C <dir> diff --stat <file>``. ``git status`` and
``git diff --stat`` with no other option stay allowed on both files."

The guard as built already decides every call here this way (found by running
the hook): the cases are green today. They hold the decision, so that a later
change neither opens one of these refusals nor closes the two git commands.

Both files are stand-ins in a temporary project; the held-out file's path
comes from the guard's own module.
"""

from __future__ import annotations

import pytest

import w1_02_copies_support as batch
import w1_02_protected_support as protected

FILES = batch.FILES
SETTINGS = batch.SETTINGS
HELD = batch.HELD
OWN = "own"
WIDEST = "orchestrator"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    return batch.make_world(tmp_path_factory.mktemp("beyond-the-order"))


def _ask(world, name, text, who=WIDEST):
    return batch.ask_bash(world, batch.fill(world, OWN, name, text), who)


# --------------------------------------------------------------------------
# Refused, as built
# --------------------------------------------------------------------------

MENTIONS = {
    "a-commit-message": 'git commit -m "the hooks of {rel} are listed by the helper"',
    "an-echo": "echo {rel}",
    "an-echo-of-a-sentence": 'echo "see {rel} for the hooks"',
}


@pytest.mark.parametrize("who", (WIDEST, "engineer-who-may-not-write-the-file"))
@pytest.mark.parametrize("form", sorted(MENTIONS))
def test_a_command_that_only_mentions_the_settings_file_s_path_is_refused(world, form, who):
    """DP-5: the path as text is a read as far as the guard can tell; sessions write "the settings file"."""
    result = _ask(world, SETTINGS, MENTIONS[form], who)
    batch.assert_refused_by_the_rule(result, f"{form} that mentions the stand-in settings file's path, by '{who}'")


FOLDER_WORDS = {
    "git-add-of-the-folder": "git add {dir}",
    "git-add-of-the-folder-absolute": "git add {absdir}",
    "test-for-the-folder": "test -d {dir}",
    "git-log-of-the-folder": "git log --oneline -- {dir}",
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(FOLDER_WORDS))
def test_a_folder_that_holds_either_file_is_refused_in_a_command_that_does_not_read(world, form, name):
    result = _ask(world, name, FOLDER_WORDS[form])
    batch.assert_refused_by_the_rule(result, f"{form} (the folder of the stand-in {name})")


@pytest.mark.parametrize("command", ("git add {above}", "test -d {above}"), ids=("git-add", "test"))
def test_a_folder_above_the_held_out_file_inside_the_project_is_refused_in_a_command_that_does_not_read(world, command):
    above = world.site(OWN).rel(HELD).split("/")[0]
    result = batch.ask_bash(world, command.format(above=above), WIDEST)
    batch.assert_refused_by_the_rule(result, "a command that names a folder above the stand-in held-out file")


GIT_WITH_A_FOLDER_OPTION = {
    "the-project-s-folder": "git -C {project} diff --stat {rel}",
    "the-working-folder": "git -C . diff --stat {rel}",
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(GIT_WITH_A_FOLDER_OPTION))
def test_git_diff_stat_with_a_folder_option_is_refused(world, form, name):
    result = _ask(world, name, GIT_WITH_A_FOLDER_OPTION[form])
    batch.assert_refused_by_the_rule(result, f"`git -C <dir> diff --stat` with {form} on the stand-in {name}")


# --------------------------------------------------------------------------
# Allowed, as built
# --------------------------------------------------------------------------

GIT_ALONE = {
    "status": "git status {rel}",
    "status-after-two-dashes": "git status -- {rel}",
    "diff-stat": "git diff --stat {rel}",
    "diff-stat-absolute": "git diff --stat {abs}",
    "diff-stat-after-two-dashes": "git diff --stat -- {rel}",
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(GIT_ALONE))
def test_git_status_and_diff_stat_with_no_other_option_stay_allowed(world, form, name):
    result = _ask(world, name, GIT_ALONE[form])
    protected.assert_allowed(result, f"git {form} on the stand-in {name}")


@pytest.mark.parametrize("command", ("git status", "git diff --stat"))
def test_git_status_and_diff_stat_with_no_file_stay_allowed(world, command):
    protected.assert_allowed(batch.ask_bash(world, command, WIDEST), f"`{command}`")
