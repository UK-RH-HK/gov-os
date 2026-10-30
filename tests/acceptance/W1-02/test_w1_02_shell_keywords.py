"""W1-02 — a search after a shell keyword is judged as the search it is (DEC-570).

Rewritten by W2-58's test designer (DEC-821 item 3, DEC-857 item 3): the
search is still judged as the search it is, and under Policy 2 (DEC-820) that
search, from the root, from a copy's folder or in a folder that holds a
protected file, is allowed; so is a read of either file found after a keyword.
For every role, the engineer's content search from the root stays refused, now
for (c): the root holds its ticket's acceptance folder (DEC-821 item 1).

DEC-570: "A search after a shell keyword (``do``, ``then``, ``else``, ``if``,
``while``, ``until``, and a ``!`` in front) is judged as the search it is."
``elif`` is held with them.

Held here, through the hook run as a process, on stand-in files, in a session
that stands in the project root, in the folder ``<P>`` a copy lies under, and in
a folder that holds a protected file:

- **refused**: a search with no path, or with the root as its path, as the body
  of a loop, as the condition or a branch of an ``if``, as the condition of a
  ``while`` or an ``until``, and with ``!`` in front;
- **refused, before and after**: a read of a protected file after a keyword
  (the guard refuses it today already; the cases hold it);
- **stays allowed**: the same shapes around a search of a source folder or of a
  named source file, and a loop that reads a named source file.

**Before the change** (found by running the hook, README) the guard allows every
form of the first list: those cases are red. The other two lists are green
before and after.

A protected file's path comes from the guard's constants, never typed, and no
id or failure message carries a path or a command.
"""

from __future__ import annotations

import pytest

import w1_02_copies_support as batch
import w1_02_folders_support as folders
import w1_02_fix_support as fix

ROOT = fix.ROOT
PROG = fix.PROG


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return fix.make_world(tmp_path_factory.mktemp("shell-keywords"))


def assert_policy_2(result, command, who, start, what):
    """W2-58 (DEC-821 item 3, DEC-857 item 3): allowed; but an engineer's content search from the root takes in its
    ticket's acceptance folder (``tests/acceptance/W1-90/``) and is refused for (c) (DEC-821 item 1). A listing
    from above (``ls``, ``find``) is not aimed inside that folder and stays allowed."""
    listing = any(f" {word} " in f" {command} " for word in ("ls", "find"))
    if who == folders.NOT_A_WRITER and start == ROOT and not listing:
        assert result.decision == "deny", f"{what} was not refused (Policy 2 (c)): {result.describe()}"
    else:
        fix.assert_allowed(result, what)


# --------------------------------------------------------------------------
# Refused before W2-58, allowed under Policy 2: a search of the folder after a keyword
# --------------------------------------------------------------------------

AFTER_A_KEYWORD = {
    "the-body-of-a-loop-over-words-grep-recursive-over-a-dot": "for p in A B; do grep -rn $p .; done",
    "the-body-of-a-loop-over-words-the-other-program": "for p in A B; do " + PROG + " $p; done",
    "the-condition-of-an-if-the-other-program": "if " + PROG + " -q VALUE; then echo y; fi",
    "the-branch-of-an-if-grep-recursive-over-a-dot": "if true; then grep -rn VALUE .; fi",
    "the-else-branch-ls-recursive": "if false; then :; else ls -R; fi",
    "the-condition-of-an-elif-the-other-program": "if false; then :; elif " + PROG + " -q VALUE; then :; fi",
    "the-body-of-a-loop-over-lines-the-other-program": "while read f; do " + PROG + " VALUE; done",
    "the-condition-of-an-until-grep-recursive-over-a-dot": "until grep -rq VALUE .; do sleep 1; done",
    "a-bang-in-front-of-the-other-program": "! " + PROG + " -q VALUE",
    "the-condition-of-a-while-the-other-program": "while " + PROG + " -q VALUE; do :; done",
}


@pytest.mark.parametrize("form", sorted(AFTER_A_KEYWORD))
def test_a_search_of_the_root_after_a_shell_keyword_is_allowed_under_policy_2(world, form):
    """Point 2: the keyword is not the command; the search is judged as the search it is, which Policy 2 opens."""
    result = fix.ask_command(world, AFTER_A_KEYWORD[form])
    fix.assert_allowed(result, f"a search as {form}, at the root")


AT_A_COPY = ("the-body-of-a-loop-over-words-the-other-program", "the-condition-of-an-if-the-other-program",
             "the-else-branch-ls-recursive", "the-condition-of-an-until-grep-recursive-over-a-dot")


# Two forms from each <P>, in turn.
COPY_CASES = [(AT_A_COPY[(2 * row + step) % len(AT_A_COPY)], site)
              for row, site in enumerate(fix.SITES) for step in range(2)]


@pytest.mark.parametrize("form,site", COPY_CASES, ids=fix.ids(COPY_CASES))
def test_a_search_after_a_shell_keyword_is_allowed_from_a_copy_s_folder(world, form, site):
    """Point 2 from ``<P>``: a sibling checkout, a folder below the root, the stand-in home; open under Policy 2."""
    result = fix.ask_command(world, AFTER_A_KEYWORD[form], site)
    fix.assert_allowed(result, f"a search as {form}, in a session that stands in the site '{site}'")


IN_A_HOLDING_FOLDER = ("the-condition-of-an-if-the-other-program", "the-body-of-a-loop-over-words-the-other-program",
                       "the-else-branch-ls-recursive")


@pytest.mark.parametrize("start", sorted(fix.HOLDING))
@pytest.mark.parametrize("form", IN_A_HOLDING_FOLDER)
def test_a_search_after_a_shell_keyword_is_allowed_in_a_folder_that_holds_a_protected_file(world, form, start):
    """Before Policy 2 the search with no path was refused there; now the folder is read as any folder."""
    result = fix.ask_command(world, AFTER_A_KEYWORD[form], start)
    fix.assert_allowed(result, f"a search as {form}, in {start}")


BY_ROLE = fix.share(AFTER_A_KEYWORD)


@pytest.mark.parametrize("who,form", BY_ROLE, ids=fix.ids(BY_ROLE))
def test_a_search_after_a_shell_keyword_is_decided_by_policy_2_for_every_role(world, who, form):
    """An engineer, the test designer and a session with no role (the orchestrator asks every form above)."""
    result = fix.ask_command(world, AFTER_A_KEYWORD[form], ROOT, who)
    assert_policy_2(result, AFTER_A_KEYWORD[form], who, ROOT, f"a search as {form}, at the root, by '{who}'")


# --------------------------------------------------------------------------
# Refused before W2-58, allowed under Policy 2: a read of a protected file (or a copy) after a keyword
# --------------------------------------------------------------------------

# ``{rel}`` the file's project-relative path, ``{abs}`` the file or the copy (``w1_02_copies_support.fill``).
READS = {
    "the-branch-of-an-if": ("own", "if true; then cat {rel}; fi"),
    "the-body-of-a-loop": ("own", "for f in a; do cat {rel}; done"),
    "a-bang-in-front": ("own", "! cat {abs}"),
    "the-else-branch-a-copy": ("sibling", "if false; then :; else cat {abs}; fi"),
}


@pytest.mark.parametrize("name", fix.FILES)
@pytest.mark.parametrize("form", sorted(READS))
def test_a_read_of_a_protected_file_after_a_shell_keyword_is_allowed_under_policy_2(world, form, name):
    """The guard reads every word of a command; the read it finds (of the file, or of a copy in a sibling checkout)
    is open under Policy 2."""
    site, command = READS[form]
    what = f"a read of the stand-in {name} as {form}"
    result = folders.ask_bash(world, batch.fill(world, site, name, command), fix.WIDEST)
    fix.assert_allowed(result, what)


# --------------------------------------------------------------------------
# Stays allowed: the same shapes around a search that names its source
# --------------------------------------------------------------------------

DAILY = {
    "a-loop-over-names-grep-in-a-named-source-file": "for f in a b; do grep -n VALUE src/$f; done",
    "a-loop-over-words-grep-recursive-over-a-source-folder": "for p in A B; do grep -rn $p src; done",
    "the-condition-of-an-if-grep-in-a-named-source-file": "if grep -q VALUE <NAMED>; then echo y; fi",
    "a-loop-over-the-lines-of-a-named-source-file": "while read f; do echo $f; done < <NAMED>",
    "a-bang-in-front-of-grep-in-a-named-source-file": "! grep -q VALUE <NAMED>",
    "the-branch-of-an-if-the-other-program-over-a-source-folder": "if true; then " + PROG + " VALUE src; fi",
    "the-condition-of-a-while-ls-recursive-of-a-source-folder": "while ls -R src; do break; done",
}


@pytest.mark.parametrize("form", sorted(DAILY))
def test_a_search_of_a_source_folder_or_a_named_file_after_a_shell_keyword_stays_allowed(world, form):
    """Green before and after: judged as the search it is, it names a folder or a file that is neither protected."""
    result = fix.ask_command(world, DAILY[form])
    fix.assert_allowed(result, f"{form}, at the root")


DAILY_BY_ROLE = fix.share(DAILY)


@pytest.mark.parametrize("who,form", DAILY_BY_ROLE, ids=fix.ids(DAILY_BY_ROLE))
def test_a_search_of_a_source_folder_or_a_named_file_after_a_shell_keyword_stays_allowed_for_every_role(
        world, who, form):
    result = fix.ask_command(world, DAILY[form], ROOT, who)
    fix.assert_allowed(result, f"{form}, at the root, by '{who}'")
