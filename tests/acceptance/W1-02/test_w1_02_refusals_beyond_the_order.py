"""W1-02 — the refusals beyond the order (DEC-548, DP-5): under Policy 2, decided as for any file.

Rewritten by W2-58's test designer (DEC-821 item 3, DEC-857 item 3): each
refusal below existed for the two protected files' sake; under Policy 2
(DEC-820) each call is decided as the same command on another file of the
folder (or on ``src/``) is, by the same role, and is never refused as a read
of the two files. The two git commands held as allowed are unchanged.

Before Policy 2:

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


def assert_decided_as_for_an_ordinary_file(world, name, text, control, who, what):
    """W2-58 (DEC-821 item 3, DEC-857 item 3): the call is decided as the same command on an ordinary file or folder
    (``control``) is, by the same role; a refusal, if any, is not the read rule's."""
    result, ordinary = _ask(world, name, text, who), _ask(world, name, control, who)
    assert (result.decision, result.returncode) == (ordinary.decision, ordinary.returncode), (
        f"{what}: decided {result.decision} (exit {result.returncode}), but the same command on an ordinary file is "
        f"decided {ordinary.decision} (exit {ordinary.returncode})")
    assert not batch.RULE_RE.search(protected.reason_of(result)), f"{what} was refused as a read of the two files"


# --------------------------------------------------------------------------
# Refused as built before W2-58; under Policy 2 decided as for any file (rewritten: DEC-821 item 3, DEC-857 item 3)
# --------------------------------------------------------------------------

MENTIONS = {
    "a-commit-message": 'git commit -m "the hooks of {rel} are listed by the helper"',
    "an-echo": "echo {rel}",
    "an-echo-of-a-sentence": 'echo "see {rel} for the hooks"',
}


@pytest.mark.parametrize("who", (WIDEST, "engineer-who-may-not-write-the-file"))
@pytest.mark.parametrize("form", sorted(MENTIONS))
def test_a_command_that_only_mentions_the_settings_file_s_path_is_decided_as_for_any_file(world, form, who):
    """DP-5 before Policy 2: the path as text was refused as a read; now it is decided as the same text naming
    another file of the folder."""
    assert_decided_as_for_an_ordinary_file(world, SETTINGS, MENTIONS[form], MENTIONS[form].replace("{rel}", "{nrel}"),
                                           who, f"{form} that mentions the stand-in settings file's path, by '{who}'")


FOLDER_WORDS = {
    "git-add-of-the-folder": "git add {dir}",
    "git-add-of-the-folder-absolute": "git add {absdir}",
    "test-for-the-folder": "test -d {dir}",
    "git-log-of-the-folder": "git log --oneline -- {dir}",
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(FOLDER_WORDS))
def test_a_folder_that_holds_either_file_is_decided_as_any_folder_in_a_command_that_does_not_read(world, form, name):
    control = FOLDER_WORDS[form].replace("{dir}", "src").replace("{absdir}", "{project}/src")
    assert_decided_as_for_an_ordinary_file(world, name, FOLDER_WORDS[form], control, WIDEST,
                                           f"{form} (the folder of the stand-in {name})")


@pytest.mark.parametrize("command", ("git add {above}", "test -d {above}"), ids=("git-add", "test"))
def test_a_folder_above_the_held_out_file_inside_the_project_is_decided_as_any_folder(world, command):
    above = world.site(OWN).rel(HELD).split("/")[0]
    result = batch.ask_bash(world, command.format(above=above), WIDEST)
    ordinary = batch.ask_bash(world, command.format(above="src"), WIDEST)
    what = "a command that names a folder above the stand-in held-out file"
    assert (result.decision, result.returncode) == (ordinary.decision, ordinary.returncode), (
        f"{what}: decided {result.decision}, the same command on src/ {ordinary.decision}")
    assert not batch.RULE_RE.search(protected.reason_of(result)), f"{what} was refused as a read of the two files"


GIT_WITH_A_FOLDER_OPTION = {
    "the-project-s-folder": "git -C {project} diff --stat {rel}",
    "the-working-folder": "git -C . diff --stat {rel}",
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(GIT_WITH_A_FOLDER_OPTION))
def test_git_diff_stat_with_a_folder_option_is_decided_as_for_any_file(world, form, name):
    text = GIT_WITH_A_FOLDER_OPTION[form]
    assert_decided_as_for_an_ordinary_file(world, name, text, text.replace("{rel}", "{nrel}"), WIDEST,
                                           f"`git -C <dir> diff --stat` with {form} on the stand-in {name}")


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
