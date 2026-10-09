"""W1-02 — a move or a link of a folder that holds either file or a copy is a second name (DEC-553, DP-8).

DEC-553: "A move or a link of a folder that holds either file or a copy is a
second name and is refused as a read, for every role."

After such a command the file lies under a folder name the rule does not know,
at a path that no longer ends in the file's project-relative path. So the
refusal is the read rule's own (``deny``, exit code 0, a reason that names the
rule's decision), also for a role that may write the folder today: a denial by
the allow-list does not pass these cases.

**A folder that holds** a file or a copy is a folder strictly between ``<P>``
and the file: the folder the rule as built already refuses in a listing or a
search. ``<P>`` is the session's project root for the project's own two files,
another folder for a copy, the home folder for the user-level settings file.
The held-out file lies below more than one such folder; each is asked.

The programs are those of DEC-548's third point: a move or rename with the
folder as its source; a link to it (hard and symbolic forms of the link
command); a linking copy of it (a recursive copy with an option that links).

**Before the change** (found by running the hook, README):

- a symbolic link to such a folder and a recursive copy that makes symbolic
  links are refused as reads already, for every role and at every site: green
  today, and held all the same;
- a move, a rename, a hard link and a recursive copy that makes hard links are
  decided as writes only: allowed for a role that may write the folder (in the
  session's project and below it), denied by the allow-list and not by the
  rule for the others and for every role outside the project: red.

No case moves or links ``<P>`` itself or a folder above it, and none uses the
two forms DEC-553 leaves as residuals (README).
"""

from __future__ import annotations

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected

SETTINGS = folders.SETTINGS
WIDEST = folders.ORCHESTRATOR          # may write every folder of the project today
WRITER = folders.FOLDER_WRITER         # an engineer whose ticket names the holding folders and template/
NOT_A_WRITER = folders.NOT_A_WRITER    # an engineer whose ticket names none of them
HOLDING = folders.HOLDING
HOLDING_IDS = folders.HOLDING_IDS
INNERMOST = folders.INNERMOST          # for each file, the folder the file itself lies in


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return folders.make_world(tmp_path_factory.mktemp("holding-folders"))


# ``{rel}`` is the folder as a relative path from the session's project, ``{abs}`` its absolute path;
# ``{scratch}`` and ``{tmp}`` are places every known role may write, so nothing but the folder decides the call.
SECOND_NAMES = {
    # A move or a rename: the folder is the source.
    "move-relative": "mv {rel} {scratch}/w1-02-moved",
    "move-absolute": "mv {abs} {tmp}/w1-02-moved",
    "move-with-a-trailing-slash": "mv {rel}/ {scratch}/w1-02-moved",
    "rename-beside-itself": "mv {rel} {rel}-w1-02-renamed",
    "move-into-a-target-directory": "mv -t {scratch} {rel}",
    # A link to it.
    "hard-link": "ln {rel} {scratch}/w1-02-second-name",
    "hard-link-absolute": "ln {abs} {tmp}/w1-02-second-name",
    "symbolic-link-absolute": "ln -s {abs} {scratch}/w1-02-second-name",
    "symbolic-link-relative": "ln -s {rel} w1-02-second-name",
    "symbolic-link-long-option": "ln --symbolic {abs} {tmp}/w1-02-second-name",
    # A linking copy: a recursive copy with an option that links instead of copying.
    "linking-copy": "cp -rl {rel} {scratch}/w1-02-linked",
    "linking-copy-archive": "cp -al {abs} {tmp}/w1-02-linked",
    "linking-copy-long-option": "cp -r --link {rel} {scratch}/w1-02-linked",
    "symbolic-linking-copy": "cp -rs {abs} {scratch}/w1-02-linked",
    "symbolic-linking-copy-long-option": "cp -R --symbolic-link {abs} {tmp}/w1-02-linked",
}
# One or two forms of each kind, for the roles and the sites beyond the first.
OF_EACH_KIND = ("move-relative", "move-absolute", "hard-link", "symbolic-link-absolute", "linking-copy",
                "symbolic-linking-copy")
# The folder that holds the user-level settings file, as a shell spells the home folder.
FROM_HOME = {
    "move-with-a-tilde": "mv ~/{folder} {scratch}/w1-02-moved",
    "move-with-the-home-variable": "mv $HOME/{folder} {scratch}/w1-02-moved",
    "rename-with-a-tilde": "mv ~/{folder} ~/{folder}-w1-02-renamed",
    "hard-link-with-a-tilde": "ln ~/{folder} {scratch}/w1-02-second-name",
    "symbolic-link-with-a-tilde": "ln -s ~/{folder} {scratch}/w1-02-second-name",
    "linking-copy-with-a-tilde": "cp -rl ~/{folder} {scratch}/w1-02-linked",
    "linking-copy-with-the-home-variable-in-braces": 'cp -al "${{HOME}}/{folder}" {scratch}/w1-02-linked',
}


def _command(world, site, folder, text):
    """``text`` for the holding folder ``folder`` (relative to ``<P>``) of the site."""
    path = world.site(site).root / folder
    return text.format(rel=folders.rel_from_project(world, path), abs=path, folder=folder,
                       scratch=folders.SCRATCH_REL, tmp=world.sandbox.tmpdir)


def _ask(world, site, folder, text, who=WIDEST):
    return folders.ask_bash(world, _command(world, site, folder, text), who)


# --------------------------------------------------------------------------
# The session's own two files
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name,folder", HOLDING, ids=HOLDING_IDS)
@pytest.mark.parametrize("form", sorted(SECOND_NAMES))
def test_a_second_name_for_a_folder_that_holds_a_protected_file_is_refused_as_a_read(world, form, name, folder):
    """DP-8: each form, relative and absolute, by the orchestrator, which may write the folder today."""
    result = _ask(world, "own", folder, SECOND_NAMES[form])
    folders.assert_refused_by_the_rule(
        result, f"Bash {form} on a folder that holds the stand-in {name} by the {WIDEST}")


@pytest.mark.parametrize("name,folder", HOLDING, ids=HOLDING_IDS)
@pytest.mark.parametrize("who", (WRITER, NOT_A_WRITER))
@pytest.mark.parametrize("form", ("move-relative", "hard-link", "symbolic-link-absolute", "linking-copy"))
def test_a_second_name_for_a_holding_folder_is_refused_whether_or_not_the_role_may_write_it(world, form, who, name,
                                                                                            folder):
    """DP-8: "for every role, a role that may write the folder today included"."""
    result = _ask(world, "own", folder, SECOND_NAMES[form], who)
    folders.assert_refused_by_the_rule(result, f"Bash {form} on a folder that holds the stand-in {name} by an {who}")


# --------------------------------------------------------------------------
# A copy in a sibling checkout, a copy below the session's root
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name,folder", HOLDING, ids=HOLDING_IDS)
@pytest.mark.parametrize("form", OF_EACH_KIND)
def test_a_second_name_for_a_folder_that_holds_a_copy_in_another_checkout_is_refused_as_a_read(world, form, name,
                                                                                               folder):
    """DP-8 on a copy outside the project: no role may write there, so today the allow-list denies; not the rule.

    The relative spelling goes from the session's project up and into the other checkout.
    """
    result = _ask(world, "sibling", folder, SECOND_NAMES[form])
    folders.assert_refused_by_the_rule(
        result, f"Bash {form} on a folder that holds the copy of the stand-in {name} in another checkout")


@pytest.mark.parametrize("name,folder", INNERMOST, ids=[name for name, _ in INNERMOST])
@pytest.mark.parametrize("form", ("move-absolute", "linking-copy"))
def test_a_second_name_for_such_a_folder_in_another_checkout_is_refused_for_a_role_that_writes_less(world, form, name,
                                                                                                    folder):
    result = _ask(world, "sibling", folder, SECOND_NAMES[form], NOT_A_WRITER)
    folders.assert_refused_by_the_rule(
        result, f"Bash {form} on the folder of the copy of the stand-in {name} in another checkout by an {NOT_A_WRITER}")


@pytest.mark.parametrize("name,folder", HOLDING, ids=HOLDING_IDS)
@pytest.mark.parametrize("form", ("move-relative", "move-absolute", "hard-link", "linking-copy"))
def test_a_second_name_for_a_folder_that_holds_a_copy_below_the_project_s_root_is_refused_as_a_read(world, form, name,
                                                                                                    folder):
    """DP-8 on a copy below the session's root (``template/`` as ``<P>``), by the orchestrator."""
    result = _ask(world, "nested", folder, SECOND_NAMES[form])
    folders.assert_refused_by_the_rule(
        result, f"Bash {form} on a folder that holds the copy of the stand-in {name} below the root")


@pytest.mark.parametrize("name,folder", INNERMOST, ids=[name for name, _ in INNERMOST])
@pytest.mark.parametrize("who", (WRITER, NOT_A_WRITER))
@pytest.mark.parametrize("form", ("move-relative", "hard-link"))
def test_a_second_name_for_such_a_folder_below_the_root_is_refused_whether_or_not_the_role_may_write_it(
        world, form, who, name, folder):
    """The engineer whose ticket names ``template/`` may write the folder today; the other engineer may not."""
    result = _ask(world, "nested", folder, SECOND_NAMES[form], who)
    folders.assert_refused_by_the_rule(
        result, f"Bash {form} on the folder of the copy of the stand-in {name} below the root by an {who}")


@pytest.mark.parametrize("name,folder", INNERMOST, ids=[name for name, _ in INNERMOST])
@pytest.mark.parametrize("form", ("symbolic-link-relative", "symbolic-linking-copy"))
def test_a_symbolic_second_name_for_a_folder_that_holds_a_copy_below_the_root_is_refused_as_a_read(world, form, name,
                                                                                                   folder):
    result = _ask(world, "nested", folder, SECOND_NAMES[form])
    folders.assert_refused_by_the_rule(
        result, f"Bash {form} on the folder of the copy of the stand-in {name} below the root")


# --------------------------------------------------------------------------
# The folder that holds the user-level settings file
# --------------------------------------------------------------------------

@pytest.mark.parametrize("form", sorted(FROM_HOME))
def test_a_second_name_for_the_folder_that_holds_the_user_level_settings_file_is_refused_as_a_read(world, form):
    """DP-8 below the stand-in home: ``~`` and ``$HOME`` are the ``HOME`` of the hook's environment."""
    (_, folder), = [pair for pair in folders.INNERMOST if pair[0] == SETTINGS]
    result = _ask(world, "home", folder, FROM_HOME[form])
    folders.assert_refused_by_the_rule(result, f"Bash {form} on the folder of the stand-in user-level settings file")


@pytest.mark.parametrize("who", (WIDEST, NOT_A_WRITER))
@pytest.mark.parametrize("form", ("move-absolute", "hard-link-absolute", "linking-copy-archive"))
def test_a_second_name_for_that_folder_by_its_absolute_path_is_refused_for_every_role(world, form, who):
    (_, folder), = [pair for pair in folders.INNERMOST if pair[0] == SETTINGS]
    result = _ask(world, "home", folder, SECOND_NAMES[form], who)
    folders.assert_refused_by_the_rule(
        result, f"Bash {form} on the folder of the stand-in user-level settings file by '{who}'")


# --------------------------------------------------------------------------
# What the refusal says
# --------------------------------------------------------------------------

SAID = [("own", name, folder) for name, folder in folders.INNERMOST] + \
       [("sibling", name, folder) for name, folder in folders.INNERMOST] + \
       [("home", name, folder) for name, folder in folders.INNERMOST if name == SETTINGS]


@pytest.mark.parametrize("site,name,folder", SAID, ids=[f"{site}-{name}" for site, name, _ in SAID])
def test_the_refusal_for_a_holding_folder_names_the_rule_and_no_path(world, site, name, folder):
    """A refusal names the rule and the decision: not the file, not the folder moved, not ``<P>``.

    The command carries the folder's absolute path, so a refusal that echoes the command fails.
    """
    form = "move-absolute"
    result = _ask(world, site, folder, SECOND_NAMES[form])
    what = f"Bash {form} on the folder of the stand-in {name} at the site '{site}'"
    folders.assert_refused_by_the_rule(result, what)
    folders.assert_says_nothing(result, world, site, name, what, more=(world.site(site).root / folder,))


# --------------------------------------------------------------------------
# What stays as it is: green before and after
# --------------------------------------------------------------------------

# A folder of the session's project that holds neither file and no copy: the same programs on it.
ON_ANOTHER_FOLDER = {
    "move-relative": "mv {rel} {scratch}/w1-02-moved",
    "move-absolute": "mv {abs} {tmp}/w1-02-moved",
    "move-into-a-target-directory": "mv -t {scratch} {rel}",
    "hard-link": "ln {rel} {scratch}/w1-02-second-name",
    "linking-copy": "cp -rl {rel} {scratch}/w1-02-linked",
    "linking-copy-long-option": "cp -r --link {rel} {scratch}/w1-02-linked",
    "symbolic-link-absolute": "ln -s {abs} {scratch}/w1-02-second-name",
    "symbolic-linking-copy": "cp -rs {abs} {scratch}/w1-02-linked",
    "plain-copy": "cp -r {rel} {scratch}/w1-02-copied",
}
# The forms that write the folder they name: the allow-list denies them to a role whose ticket does not name it.
# The others (a symbolic link to it, a plain copy of it) only write their destination, which is scratch.
WRITE_THE_FOLDER = ("move-relative", "move-absolute", "move-into-a-target-directory", "hard-link", "linking-copy",
                    "linking-copy-long-option")


def _other(world, text, who):
    path = world.project / folders.NEUTRAL_REL
    command = text.format(rel=folders.NEUTRAL_REL, abs=path, scratch=folders.SCRATCH_REL, tmp=world.sandbox.tmpdir)
    return folders.ask_bash(world, command, who)


@pytest.mark.parametrize("who", (WIDEST, WRITER))
@pytest.mark.parametrize("form", sorted(ON_ANOTHER_FOLDER))
def test_a_second_name_for_a_folder_that_holds_neither_file_stays_allowed_for_a_role_that_may_write_it(world, form,
                                                                                                        who):
    """A move, a link, a linking copy and a plain copy of ``docs/spec`` by a role that may write it."""
    result = _other(world, ON_ANOTHER_FOLDER[form], who)
    protected.assert_allowed(result, f"Bash {form} on a folder that holds neither file by '{who}'")


@pytest.mark.parametrize("form", sorted(ON_ANOTHER_FOLDER))
def test_a_second_name_for_such_a_folder_by_a_role_that_may_not_write_it_is_decided_by_the_allow_list(world, form):
    """Denied where the form writes the folder, and **not** by this rule; allowed where it only writes scratch."""
    result = _other(world, ON_ANOTHER_FOLDER[form], NOT_A_WRITER)
    what = f"Bash {form} on a folder that holds neither file by an {NOT_A_WRITER}"
    if form in WRITE_THE_FOLDER:
        folders.assert_denied_but_not_by_the_rule(result, what)
    else:
        protected.assert_allowed(result, what)


# Such a folder as the destination of a move with another folder as the source.
AS_DESTINATION = {
    "move-into-it": "mv {other} {neutral}/w1-02-moved-in",
    "move-into-its-parent": "mv {other} {parent}",
    "move-with-it-as-the-target-directory": "mv -t {neutral} {other}",
}


@pytest.mark.parametrize("who", (WIDEST, NOT_A_WRITER))
@pytest.mark.parametrize("form", sorted(AS_DESTINATION))
def test_a_folder_that_holds_neither_file_as_the_destination_of_a_move_is_decided_as_today(world, form, who):
    """Allowed for the orchestrator; for the engineer whose ticket names neither folder, the allow-list's denial."""
    command = AS_DESTINATION[form].format(other=folders.OTHER_FOLDER_REL, neutral=folders.NEUTRAL_REL,
                                          parent=folders.NEUTRAL_PARENT_REL)
    result = folders.ask_bash(world, command, who)
    what = f"Bash {form} (a folder that holds neither file as the destination) by '{who}'"
    if who == WIDEST:
        protected.assert_allowed(result, what)
    else:
        folders.assert_denied_but_not_by_the_rule(result, what)


# The same programs on a folder outside the project under which no copy lies.
OUTSIDE = {
    "symbolic-link-to-a-source-folder-of-another-checkout": ("sibling", "ln -s {abs} {scratch}/w1-02-second-name", True),
    "plain-copy-of-a-source-folder-of-another-checkout": ("sibling", "cp -r {abs} {scratch}/w1-02-copied", True),
    "move-of-a-source-folder-of-another-checkout": ("sibling", "mv {abs} {scratch}/w1-02-moved", False),
    "symbolic-link-to-a-work-folder-below-the-home-folder": ("home", "ln -s ~/{work} {scratch}/w1-02-second-name", True),
    "move-of-a-work-folder-below-the-home-folder": ("home", "mv ~/{work} {scratch}/w1-02-moved", False),
}


@pytest.mark.parametrize("case", sorted(OUTSIDE))
def test_a_second_name_for_a_folder_outside_the_project_that_holds_no_copy_is_decided_as_today(world, case):
    """Reading from outside the project is allowed, writing there is the allow-list's to deny: never this rule."""
    site, text, allowed = OUTSIDE[case]
    command = text.format(abs=world.site(site).root / folders.SOURCE_REL, work=folders.HOME_WORK_REL,
                          scratch=folders.SCRATCH_REL)
    result = folders.ask_bash(world, command, WIDEST)
    if allowed:
        protected.assert_allowed(result, case)
    else:
        folders.assert_denied_but_not_by_the_rule(result, case)
