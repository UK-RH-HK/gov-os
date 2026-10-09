"""W1-02 — a second name for the settings file or the held-out file is a read (DEC-548, DP-3).

DEC-548: "A command that gives either file a second name is refused as a read,
for every role: a move or rename of the file, a hard or symbolic link to it, a
linking copy, and an in-place edit that leaves a backup copy. A plain write to
the file by a role that may write it today stays as it is."

After such a command the file's content can be read under a name the rule does
not know. So the refusal is the read rule's own (``deny``, exit code 0, a
reason that names the rule's decision), also for a role that may write the
file: a denial by the allow-list does not pass these cases.

Before the change (found by running the hook, README): a move, a rename, a
hard link, a linking copy and ``sed`` in place with a backup suffix are decided
as writes only (allowed for a role that may write the file, denied by the
allow-list for the others); a symbolic link, a copy that makes symbolic links
and an interpreter in place with a backup suffix are already refused as reads.
Those cases are green today and are held all the same.

Both files are stand-ins in a temporary project (``w1_02_copies_support``). The
held-out file's path is taken from the guard's own module and never typed.
"""

from __future__ import annotations

import pytest

import w1_02_copies_support as batch
import w1_02_support as support

FILES = batch.FILES
OWN = "own"
WIDEST = "orchestrator"   # may write both files today
WRITER = "engineer-who-may-write-the-file"
NOT_A_WRITER = "engineer-who-may-not-write-the-file"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project with both stand-in files for the module: the cases only ask the guard for decisions."""
    return batch.make_world(tmp_path_factory.mktemp("second-names"))


# ``{rel}`` and ``{abs}`` are the file, ``{dir}`` its folder; ``{scratch}`` and ``{tmp}`` are places every known
# role may write, so nothing but the file decides the call.
SECOND_NAMES = {
    # A move or a rename: the file is the source.
    "move-relative": "mv {rel} {scratch}/w1-02-moved",
    "move-absolute": "mv {abs} {tmp}/w1-02-moved",
    "rename-in-its-folder": "mv {rel} {dir}/w1-02-renamed",
    "move-into-a-target-directory": "mv -t {scratch} {rel}",
    # A hard link to it.
    "hard-link": "ln {rel} {scratch}/w1-02-second-name",
    "hard-link-absolute": "ln {abs} {tmp}/w1-02-second-name",
    "hard-link-by-the-link-command": "link {rel} {scratch}/w1-02-second-name",
    # A symbolic link to it.
    "symbolic-link-absolute": "ln -s {abs} {scratch}/w1-02-second-name",
    "symbolic-link-relative": "ln -s {rel} w1-02-second-name",
    "symbolic-link-long-option": "ln --symbolic {abs} {tmp}/w1-02-second-name",
    # A linking copy: a copy command with an option that links instead of copying.
    "linking-copy": "cp -l {rel} {scratch}/w1-02-linked",
    "linking-copy-long-option": "cp --link {abs} {tmp}/w1-02-linked",
    "linking-copy-in-a-cluster-of-options": "cp -al {rel} {scratch}/w1-02-linked",
    "symbolic-linking-copy": "cp -s {abs} {scratch}/w1-02-linked",
    "symbolic-linking-copy-long-option": "cp --symbolic-link {abs} {tmp}/w1-02-linked",
    # An in-place edit that leaves a backup copy.
    "stream-editor-in-place-with-a-glued-suffix": "sed -i.bak s/a/b/ {rel}",
    "stream-editor-in-place-with-the-suffix-as-a-word": "sed -i .bak s/a/b/ {rel}",
    "stream-editor-in-place-long-option-with-a-suffix": "sed --in-place=.bak s/a/b/ {abs}",
    "interpreter-in-place-with-a-glued-suffix": "perl -i.bak -pe s/a/b/ {rel}",
    "interpreter-in-place-with-a-suffix-in-a-cluster": "perl -pi.bak -e s/a/b/ {abs}",
}
# One or two forms of each kind, asked of a role that may write the file and of one that may not.
OF_EACH_KIND = ("move-relative", "rename-in-its-folder", "hard-link", "symbolic-link-absolute", "linking-copy",
                "stream-editor-in-place-with-a-glued-suffix", "stream-editor-in-place-long-option-with-a-suffix",
                "interpreter-in-place-with-a-glued-suffix")


def _ask(world, name, text, who):
    return batch.ask_bash(world, batch.fill(world, OWN, name, text), who)


# --------------------------------------------------------------------------
# Refused as a read, for every role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(SECOND_NAMES))
def test_a_second_name_for_a_protected_file_is_refused_as_a_read(world, form, name):
    """DP-3: each form, relative and absolute, by the orchestrator, which may write the file today."""
    result = _ask(world, name, SECOND_NAMES[form], WIDEST)
    batch.assert_refused_by_the_rule(result, f"Bash {form} on the stand-in {name} by the {WIDEST}")


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("who", (WRITER, NOT_A_WRITER))
@pytest.mark.parametrize("form", OF_EACH_KIND)
def test_a_second_name_is_refused_as_a_read_whether_or_not_the_role_may_write_the_file(world, form, who, name):
    """DP-3: "for every role": an engineer whose ticket names the file, and one whose ticket does not."""
    result = _ask(world, name, SECOND_NAMES[form], who)
    batch.assert_refused_by_the_rule(result, f"Bash {form} on the stand-in {name} by an {who}")


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", ("move-absolute", "hard-link"))
def test_the_refusal_of_a_second_name_names_the_rule_and_nothing_of_the_file(world, form, name):
    """A refusal names the rule and the decision: no path, no folder, no value of the file."""
    result = _ask(world, name, SECOND_NAMES[form], WIDEST)
    what = f"Bash {form} on the stand-in {name}"
    batch.assert_refused_by_the_rule(result, what)
    batch.assert_says_nothing_of_the_file(result, world, OWN, name, what)


# --------------------------------------------------------------------------
# A plain write stays as it is: green before and after
# --------------------------------------------------------------------------

# name -> the hook call for the file ``name``: (tool, input).
def _file_tool(tool_name):
    return lambda world, name: (tool_name, support.edit_tool_input(tool_name, world.site(OWN).path(name)))


def _shell(text):
    return lambda world, name: ("Bash", support.bash_tool_input(batch.fill(world, OWN, name, text)))


PLAIN_WRITES = {
    "Write": _file_tool("Write"),
    "Edit": _file_tool("Edit"),
    "output-redirect": _shell("echo '{{}}' > {rel}"),
    "copy-with-the-file-as-destination": _shell("cp {scratch}/w1-02-new {rel}"),
    "move-with-the-file-as-destination": _shell("mv {scratch}/w1-02-new {rel}"),
    "stream-editor-in-place-with-no-backup": _shell("sed -i s/a/b/ {rel}"),
    "stream-editor-in-place-long-option-with-no-backup": _shell("sed --in-place s/a/b/ {abs}"),
}
# Who writes -> allowed today (found by running the hook on these very calls).
WRITERS_TODAY = {WIDEST: True, WRITER: True, NOT_A_WRITER: False}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("who", sorted(WRITERS_TODAY))
@pytest.mark.parametrize("form", sorted(PLAIN_WRITES))
def test_a_plain_write_to_a_protected_file_is_decided_as_today(world, form, who, name):
    """DP-3: the file as the target of a write gets no second name; the allow-list decides it as before."""
    tool_name, tool_input = PLAIN_WRITES[form](world, name)
    result = batch.ask(world, tool_name, tool_input, who)
    batch.assert_as_today(result, WRITERS_TODAY[who], f"{form} on the stand-in {name} by an {who}")


@pytest.mark.parametrize("name", FILES)
def test_an_interpreter_in_place_with_no_backup_is_decided_as_today(world, name):
    """Today the guard does not know this form as a write and refuses it for naming the file; that stays."""
    result = _ask(world, name, "perl -pi -e s/a/b/ {rel}", WIDEST)
    batch.assert_as_today(result, False, f"`perl -pi -e` on the stand-in {name} by the {WIDEST}")
