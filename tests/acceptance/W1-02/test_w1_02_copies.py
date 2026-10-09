"""W1-02 — the rule covers the same two files outside the session's own project (DEC-548, DP-4).

DEC-548: "The rule covers the same two files outside the session's own
project: any target whose path ends in either file's project-relative path, in
another checkout or worktree or anywhere else, and the user-level settings file
of the harness."

A copy at ``<P>/<the file's project-relative path>`` is read through the same
forms the rule already refuses for the session's own files, with ``<P>`` in the
project root's part. The sites are built by ``w1_02_copies_support``: a sibling
checkout, a folder that is no repository, a git worktree of the session's
project, ``template/`` below the project's root, and the ``HOME`` of the hook's
environment (a stand-in: the real one is never read).

Every case names the copy, its folder, or a glob with a literal start at or
below ``<P>``: none needs the guard to walk a tree. No case takes a side on a
search from ``<P>`` with nothing that selects the file, on a search from a
folder above ``<P>``, or on a path that ends in the file's project-relative
path and names no existing file (README).

Before the change every call here is allowed (reads) or denied only by the
allow-list (second names of a copy outside the project): all red.
"""

from __future__ import annotations

import pytest

import w1_02_copies_support as batch
import w1_02_protected_support as protected

FILES = batch.FILES
SETTINGS = batch.SETTINGS
HELD = batch.HELD
WIDEST = "orchestrator"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return batch.make_world(tmp_path_factory.mktemp("copies"))


# form -> (tool, input, working folder). The input is a command (Bash) or a mapping of templates; the working
# folder is the session's project (None) or the copy's site ("root": a folder outside the project).
READS = {
    "Read-absolute": ("Read", {"file_path": "{abs}"}, None),
    "Read-relative-from-the-copy-s-site": ("Read", {"file_path": "{rel}"}, "root"),
    "Read-relative-from-the-project": ("Read", {"file_path": "{here}"}, None),
    "Read-with-dot-dot": ("Read", {"file_path": "{absdir}/../{dirbase}/{base}"}, None),
    "Read-through-a-symbolic-link": ("Read", {"file_path": "{link}"}, None),
    "Grep-in-the-copy": ("Grep", {"pattern": ".", "path": "{abs}", "output_mode": "content"}, None),
    "Grep-over-its-folder": ("Grep", {"pattern": ".", "path": "{absdir}"}, None),
    "Grep-from-the-site-with-a-glob-that-matches": ("Grep", {"pattern": ".", "path": "{root}", "glob": "*{ext}"}, None),
    "Grep-from-the-site-with-the-bare-name": ("Grep", {"pattern": ".", "path": "{root}", "glob": "{base}"}, None),
    "Glob-in-its-folder": ("Glob", {"pattern": "*", "path": "{absdir}"}, None),
    "Glob-from-the-site-by-name": ("Glob", {"pattern": "**/{base}", "path": "{root}"}, None),
    "Glob-pattern-over-its-folder": ("Glob", {"pattern": "{absdir}/*"}, None),
    "cat-absolute": ("Bash", "cat {abs}", None),
    "cat-relative-from-the-copy-s-site": ("Bash", "cat {rel}", "root"),
    "cat-relative-from-the-project": ("Bash", "cat {here}", None),
    "cat-with-dot-dot": ("Bash", "cat {absdir}/../{dirbase}/{base}", None),
    "cat-through-a-symbolic-link": ("Bash", "cat {link}", None),
    "cat-after-a-change-of-folder": ("Bash", "cd {root} && cat {rel}", None),
    "input-redirect": ("Bash", "wc -c < {abs}", None),
    "copy-with-the-copy-as-source": ("Bash", "cp {abs} {scratch}/w1-02-copied", None),
    "inline-script": ("Bash", "python3 -c \"print(open('{abs}').read())\"", None),
    "listing-of-its-folder": ("Bash", "ls -la {absdir}", None),
    "recursive-search-of-its-folder": ("Bash", "grep -rn . {absdir}", None),
    "shell-glob-over-its-folder": ("Bash", "cat {absdir}/*", None),
}
CORE = ("Read-absolute", "Grep-over-its-folder", "cat-absolute", "listing-of-its-folder")
NESTED = {
    "Read-absolute": READS["Read-absolute"],
    "Read-relative": ("Read", {"file_path": "{here}"}, None),
    "Grep-over-its-folder-relative": ("Grep", {"pattern": ".", "path": "{heredir}"}, None),
    "Glob-pattern-over-its-folder-relative": ("Glob", {"pattern": "{heredir}/*"}, None),
    "cat-relative": ("Bash", "cat {here}", None),
    "cat-absolute": READS["cat-absolute"],
    "listing-of-its-folder-relative": ("Bash", "ls {heredir}", None),
}
# The user-level settings file: ``~`` and ``$HOME`` are the HOME of the hook's environment.
HOME = {
    "Read-absolute": READS["Read-absolute"],
    "Grep-over-its-folder": READS["Grep-over-its-folder"],
    "Glob-in-its-folder": READS["Glob-in-its-folder"],
    "cat-absolute": READS["cat-absolute"],
    "cat-through-a-symbolic-link": READS["cat-through-a-symbolic-link"],
    "cat-with-a-tilde": ("Bash", "cat ~/{rel}", None),
    "cat-with-the-home-variable": ("Bash", "cat $HOME/{rel}", None),
    "cat-with-the-home-variable-in-braces": ("Bash", 'cat "${{HOME}}/{rel}"', None),
    "input-redirect-with-a-tilde": ("Bash", "wc -c < ~/{rel}", None),
    "copy-with-a-tilde-as-source": ("Bash", "cp ~/{rel} {scratch}/w1-02-copied", None),
    "listing-of-its-folder-with-a-tilde": ("Bash", "ls -la ~/{dir}", None),
}
# A second name for a copy (DP-3 on DP-4's files).
SECOND_NAMES = {
    "move": "mv {abs} {scratch}/w1-02-moved",
    "hard-link": "ln {abs} {scratch}/w1-02-second-name",
    "symbolic-link": "ln -s {abs} {scratch}/w1-02-second-name",
    "linking-copy": "cp -l {abs} {scratch}/w1-02-linked",
    "in-place-edit-with-a-backup": "sed -i.bak s/a/b/ {abs}",
}


def _ask(world, site, name, form, who=WIDEST):
    tool_name, template, where = form
    cwd = world.site(site).root if where == "root" else None
    if tool_name == "Bash":
        return batch.ask_bash(world, batch.fill(world, site, name, template), who, cwd)
    tool_input = {key: batch.fill(world, site, name, value) for key, value in template.items()}
    return batch.ask(world, tool_name, tool_input, who, cwd)


# --------------------------------------------------------------------------
# Another checkout, a folder that is no repository, a worktree
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(READS))
def test_a_read_of_a_copy_in_another_checkout_is_refused(world, form, name):
    """DP-4: every form the rule refuses for the session's own file, on the copy in a sibling checkout."""
    result = _ask(world, "sibling", name, READS[form])
    batch.assert_refused_by_the_rule(result, f"{form} on the copy of the stand-in {name} in another checkout")


def test_a_search_for_the_file_s_name_from_a_folder_between_is_refused(world):
    """As for the session's own file: a search from a folder of ``<P>`` above the copy, with the file's bare name."""
    tool_input = {"pattern": ".", "path": batch.fill(world, "sibling", HELD, "{top}"),
                  "glob": batch.fill(world, "sibling", HELD, "{base}")}
    result = batch.ask(world, "Grep", tool_input, WIDEST)
    batch.assert_refused_by_the_rule(result, "Grep for the bare name from a folder between another checkout's root "
                                             "and the copy of the stand-in held-out file")


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("site", ("plain", "worktree"))
@pytest.mark.parametrize("form", CORE)
def test_a_read_of_a_copy_anywhere_else_or_in_a_worktree_is_refused(world, form, site, name):
    """DP-4: "in another checkout or worktree or anywhere else": a folder that is no repository, and a git worktree."""
    result = _ask(world, site, name, READS[form])
    batch.assert_refused_by_the_rule(result, f"{form} on the copy of the stand-in {name} at the site '{site}'")


# --------------------------------------------------------------------------
# A copy below the session's own project
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(NESTED))
def test_a_read_of_a_copy_below_the_project_s_root_is_refused(world, form, name):
    """DP-4: "any target whose path ends in either file's project-relative path": a folder of the project as ``<P>``."""
    result = _ask(world, "nested", name, NESTED[form])
    batch.assert_refused_by_the_rule(result, f"{form} on the copy of the stand-in {name} below the project's root")


# --------------------------------------------------------------------------
# The user-level settings file
# --------------------------------------------------------------------------

@pytest.mark.parametrize("form", sorted(HOME))
def test_a_read_of_the_user_level_settings_file_is_refused(world, form):
    """DP-4: "and the user-level settings file of the harness": the settings file below the hook's ``HOME``."""
    result = _ask(world, "home", SETTINGS, HOME[form])
    batch.assert_refused_by_the_rule(result, f"{form} on the stand-in user-level settings file")


# --------------------------------------------------------------------------
# For every role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", sorted(protected.ACTORS))
def test_a_read_of_a_copy_is_refused_for_every_role(world, who):
    """The rule is for every role (DEC-508): the eleven actors of the revision, the two files in turn."""
    name = FILES[sorted(protected.ACTORS).index(who) % len(FILES)]
    result = _ask(world, "sibling", name, READS["Read-absolute"], who)
    batch.assert_refused_by_the_rule(result, f"Read of the copy of the stand-in {name} in another checkout by '{who}'")


@pytest.mark.parametrize("who", ("engineer-who-may-write-the-file", "engineer-who-may-not-write-the-file", "no-role"))
def test_a_read_of_the_user_level_settings_file_is_refused_for_every_role(world, who):
    result = _ask(world, "home", SETTINGS, HOME["cat-with-a-tilde"], who)
    batch.assert_refused_by_the_rule(result, f"`cat` with a tilde on the stand-in user-level settings file by '{who}'")


# --------------------------------------------------------------------------
# A second name for a copy
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(SECOND_NAMES))
def test_a_second_name_for_a_copy_in_another_checkout_is_refused_as_a_read(world, form, name):
    """DP-3 on DP-4's files. Today the allow-list denies four of these as writes outside the project: not the rule."""
    result = _ask(world, "sibling", name, ("Bash", SECOND_NAMES[form], None))
    batch.assert_refused_by_the_rule(result, f"{form} of the copy of the stand-in {name} in another checkout")


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", ("move", "hard-link"))
def test_a_second_name_for_a_copy_below_the_project_s_root_is_refused_as_a_read(world, form, name):
    result = _ask(world, "nested", name, ("Bash", SECOND_NAMES[form], None))
    batch.assert_refused_by_the_rule(result, f"{form} of the copy of the stand-in {name} below the project's root")


@pytest.mark.parametrize("command", ("mv ~/{rel} {scratch}/w1-02-moved", "ln -s $HOME/{rel} {scratch}/w1-02-second-name"),
                         ids=("move-with-a-tilde", "symbolic-link-with-the-home-variable"))
def test_a_second_name_for_the_user_level_settings_file_is_refused_as_a_read(world, command):
    result = _ask(world, "home", SETTINGS, ("Bash", command, None))
    batch.assert_refused_by_the_rule(result, "a second name for the stand-in user-level settings file")


# --------------------------------------------------------------------------
# What the refusal says
# --------------------------------------------------------------------------

REFUSED_COPIES = [("sibling", name) for name in FILES] + [("home", SETTINGS)]


@pytest.mark.parametrize("site,name", REFUSED_COPIES, ids=[f"{site}-{name}" for site, name in REFUSED_COPIES])
@pytest.mark.parametrize("form", ("Read-absolute", "move"))
def test_the_refusal_for_a_copy_names_neither_the_copy_nor_its_folder(world, form, site, name):
    """A refusal names the rule and the decision: not the copy's path, not its folder, not ``<P>``, no value of it."""
    asked = READS[form] if form in READS else ("Bash", SECOND_NAMES[form], None)
    result = _ask(world, site, name, asked)
    what = f"{form} on the copy of the stand-in {name} at the site '{site}'"
    batch.assert_refused_by_the_rule(result, what)
    batch.assert_says_nothing_of_the_file(result, world, site, name, what)
