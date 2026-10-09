"""W1-02 — a root search with a numbered redirect is refused like the same search without it (DEC-570).

DEC-570: "A root search with a numbered redirect (``2>/dev/null``, ``2>&1``,
``1>file``) is refused like the same search without it: the number of a redirect
is no path."

Held here, through the hook run as a process, on stand-in files, in a session
that stands in the project root, in the folder ``<P>`` a copy lies under, and in
a folder that holds a protected file:

- **refused**: a search with no path (the kinds of the fifth batch) followed by
  a numbered output redirect, alone or before a pipe; the same with a name
  filter that takes either file in; the other search program with a numbered
  input redirect that closes its standard input or feeds another descriptor
  (nothing feeds it: it searches the folder);
- **as today**: a search that gives a real path beside the redirect is allowed
  with a source folder and refused with the root;
- **stays allowed**: the other search program as the reader of a pipe with a
  numbered output redirect on it, and an ordinary command with a numbered
  redirect that is no search.

**Before the change** (found by running the hook, README) the guard allows every
form of the first list: those cases are red. The other two lists are green
before and after.

No case either way: a digit as a word of its own, set apart from the redirect by
a space.

A protected file's name comes from the guard's constants, never typed, and no
id or failure message carries a path, a filter or a command.
"""

from __future__ import annotations

import pytest

import w1_02_fix_support as fix

ROOT = fix.ROOT
PROG = fix.PROG


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return fix.make_world(tmp_path_factory.mktemp("numbered-redirects"))


# What follows the search: label -> the text after it.
REDIRECTS = {
    "its-error-output-to-the-null-device": " 2>/dev/null",
    "its-error-output-joined-to-its-output-and-a-pipe": " 2>&1 | head",
    "its-error-output-to-the-null-device-and-a-pipe": " 2>/dev/null | head",
    "its-output-by-number-to-a-file-below-the-root": " 1><SCRATCH>/out.txt",
    "its-error-output-appended-to-the-null-device": " 2>>/dev/null",
}
SEARCHES = dict(fix.NO_PATH, **fix.LISTS_FILES)


# --------------------------------------------------------------------------
# Refused: a search with no path and a numbered redirect
# --------------------------------------------------------------------------

@pytest.mark.parametrize("redirect", sorted(REDIRECTS))
@pytest.mark.parametrize("search", sorted(SEARCHES))
def test_a_search_with_no_path_and_a_numbered_redirect_is_refused_at_the_root(world, search, redirect):
    """Point 1: the number of a redirect is no path. Red before the change: allowed."""
    command = SEARCHES[search] + REDIRECTS[redirect]
    result = fix.ask_command(world, command)
    fix.assert_refused_command(result, world, command, ROOT, f"{search} with {redirect}, at the root")


# A name filter that takes a file in, in both programs' spellings, with a numbered redirect behind the search.
FILTERED = {
    "grep-include-quoted-then-the-null-device": "grep -rn VALUE --include='<F>' 2>/dev/null",
    "grep-include-with-an-equals-sign-then-a-pipe": "grep -rn --include=<F> VALUE 2>/dev/null | head",
    "the-other-program-s-short-glob-option-then-the-null-device": PROG + " VALUE -g '<F>' 2>/dev/null",
    "the-other-program-s-long-glob-option-then-both-outputs-and-a-pipe": PROG + " --glob='<F>' VALUE 2>&1 | head",
}
_FILTER_NAMES = sorted(fix.FILTERS)
WITH_A_FILTER = [(form, name, _FILTER_NAMES[(row + column) % 2])
                 for row, form in enumerate(sorted(FILTERED)) for column, name in enumerate(fix.FILES)]


@pytest.mark.parametrize("form,name,filter_", WITH_A_FILTER, ids=fix.ids(WITH_A_FILTER))
def test_a_search_whose_name_filter_takes_a_protected_file_in_is_refused_with_a_numbered_redirect_too(
        world, form, name, filter_):
    """Point 1 on the fifth batch's name filters: the redirect's number is not the search's path."""
    wanted = fix.FILTERS[filter_](name)
    result = fix.ask_command(world, FILTERED[form], f=wanted)
    fix.assert_refused_command(result, world, FILTERED[form], ROOT,
                               f"{form} with a filter for the stand-in {name} ({filter_}), at the root", f=wanted)


AT_A_COPY = {
    "the-other-program-with-a-word-to-the-null-device": PROG + " VALUE 2>/dev/null",
    "grep-recursive-joined-outputs-and-a-pipe": "grep -rn VALUE 2>&1 | head",
    "ls-recursive-to-the-null-device": "ls -R 2>/dev/null",
    "the-other-program-with-a-filter-for-the-settings-file-s-extension": PROG + " VALUE -g '<F>' 2>/dev/null",
}


# Two forms from each <P>, in turn.
_COPY_FORMS = sorted(AT_A_COPY)
COPY_CASES = [(_COPY_FORMS[(2 * row + step) % len(_COPY_FORMS)], site)
              for row, site in enumerate(fix.SITES) for step in range(2)]


@pytest.mark.parametrize("form,site", COPY_CASES, ids=fix.ids(COPY_CASES))
def test_a_search_with_a_numbered_redirect_is_refused_from_a_copy_s_folder(world, form, site):
    """Point 1 from ``<P>``: a sibling checkout, a folder below the root, the stand-in home."""
    wanted = fix.FILTERS["its-extension"](fix.SETTINGS)
    result = fix.ask_command(world, AT_A_COPY[form], site, f=wanted)
    fix.assert_refused_command(result, world, AT_A_COPY[form], site,
                               f"{form}, in a session that stands in the site '{site}'", f=wanted)


# A numbered input redirect that closes the standard input, or feeds another descriptor: nothing feeds the search.
UNFED = {
    "its-standard-input-closed-by-number": PROG + " VALUE 0<&-",
    "another-descriptor-fed-from-a-named-source-file": PROG + " VALUE 3<<NAMED>",
}
UNFED_AT = [(form, start) for form in sorted(UNFED) for start in (ROOT, "sibling")]


@pytest.mark.parametrize("form,start", UNFED_AT, ids=fix.ids(UNFED_AT))
def test_a_numbered_input_redirect_that_does_not_feed_the_search_program_leaves_it_a_search_of_the_folder(
        world, form, start):
    """Point 1: the program reads its standard input only when something feeds it; here nothing does."""
    result = fix.ask_command(world, UNFED[form], start)
    fix.assert_refused_command(result, world, UNFED[form], start, f"the other program with {form}, from '{start}'")


IN_A_HOLDING_FOLDER = {
    "the-other-program-with-a-word-to-the-null-device": PROG + " VALUE 2>/dev/null",
    "ls-recursive-joined-outputs-and-a-pipe": "ls -R 2>&1 | head",
    "grep-recursive-to-the-null-device": "grep -rn VALUE 2>/dev/null",
}


@pytest.mark.parametrize("start", sorted(fix.HOLDING))
@pytest.mark.parametrize("form", sorted(IN_A_HOLDING_FOLDER))
def test_a_search_with_a_numbered_redirect_is_refused_in_a_folder_that_holds_a_protected_file(world, form, start):
    """The rule from before the round refuses the search with no path there; the redirect gets it through today."""
    result = fix.ask_command(world, IN_A_HOLDING_FOLDER[form], start)
    fix.assert_refused_command(result, world, IN_A_HOLDING_FOLDER[form], start, f"{form}, in {start}")


# For the other roles: forms that write no file (a write is another rule's for a role that may not write).
FOR_ROLES = {
    "the-other-program-to-the-null-device": PROG + " VALUE 2>/dev/null",
    "grep-recursive-joined-outputs-and-a-pipe": "grep -rn VALUE 2>&1 | head",
    "ls-recursive-to-the-null-device-and-a-pipe": "ls -R 2>/dev/null | head",
    "the-other-program-listing-files-joined-outputs": PROG + " --files 2>&1 | head",
}
BY_ROLE = [(who, form, start) for (who, form), start in zip(fix.share(FOR_ROLES), (ROOT, "sibling") * 3)]


@pytest.mark.parametrize("who,form,start", BY_ROLE, ids=fix.ids(BY_ROLE))
def test_a_search_with_a_numbered_redirect_is_refused_for_every_role(world, who, form, start):
    """An engineer, the test designer and a session with no role (the orchestrator asks every form above)."""
    result = fix.ask_command(world, FOR_ROLES[form], start, who)
    fix.assert_refused_command(result, world, FOR_ROLES[form], start, f"{form} from '{start}' by '{who}'")


# --------------------------------------------------------------------------
# As today: a real path beside the redirect decides
# --------------------------------------------------------------------------

WITH_A_SOURCE_FOLDER = {
    "grep-recursive-over-a-source-folder-to-the-null-device": "grep -rn VALUE src 2>/dev/null",
    "the-other-program-over-a-source-folder-joined-outputs-and-a-pipe": PROG + " VALUE src 2>&1 | head",
    "ls-recursive-of-a-source-folder-to-the-null-device": "ls -R src 2>/dev/null",
    "grep-recursive-over-a-source-folder-by-number-to-a-file": "grep -rn VALUE src 1><SCRATCH>/out.txt",
}


@pytest.mark.parametrize("form", sorted(WITH_A_SOURCE_FOLDER))
def test_a_search_of_a_source_folder_with_a_numbered_redirect_stays_allowed(world, form):
    """As today (green before and after): the search names a folder under which neither file lies."""
    result = fix.ask_command(world, WITH_A_SOURCE_FOLDER[form])
    fix.assert_allowed(result, f"{form}, at the root")


SOURCE_BY_ROLE = list(zip(fix.OTHER_ROLES, ("grep-recursive-over-a-source-folder-to-the-null-device",
                                            "the-other-program-over-a-source-folder-joined-outputs-and-a-pipe",
                                            "grep-recursive-over-a-source-folder-to-the-null-device")))


@pytest.mark.parametrize("who,form", SOURCE_BY_ROLE, ids=fix.ids(SOURCE_BY_ROLE))
def test_a_search_of_a_source_folder_with_a_numbered_redirect_stays_allowed_for_every_role(world, who, form):
    result = fix.ask_command(world, WITH_A_SOURCE_FOLDER[form], ROOT, who)
    fix.assert_allowed(result, f"{form}, at the root, by '{who}'")


WITH_THE_ROOT = {
    "grep-recursive-over-a-dot-joined-outputs": "grep -rn VALUE . 2>&1",
    "the-other-program-over-a-dot-to-the-null-device": PROG + " VALUE . 2>/dev/null",
    "ls-recursive-of-the-absolute-root-joined-outputs-and-a-pipe": "ls -R <ABS> 2>&1 | head",
}


@pytest.mark.parametrize("form", sorted(WITH_THE_ROOT))
def test_a_search_of_the_root_by_its_path_with_a_numbered_redirect_stays_refused(world, form):
    """As today (green before and after): the root is the search's path, whatever follows."""
    result = fix.ask_command(world, WITH_THE_ROOT[form])
    fix.assert_refused_command(result, world, WITH_THE_ROOT[form], ROOT, f"{form}, at the root")


# --------------------------------------------------------------------------
# Stays allowed: a fed search program, and a command that is no search
# --------------------------------------------------------------------------

NO_SEARCH_OF_THE_FOLDER = {
    "the-other-program-as-the-reader-of-a-pipe-to-the-null-device": "git log --oneline | " + PROG + " VALUE 2>/dev/null",
    "the-other-program-as-the-reader-of-a-pipe-joined-outputs-and-a-pipe":
        "git log --oneline | " + PROG + " -n VALUE 2>&1 | head",
    "git-status-with-joined-outputs": "git status --short 2>&1",
    "a-test-run-with-joined-outputs-and-a-pipe": "python3 -m pytest tests/unit -q 2>&1 | tail -5",
}


@pytest.mark.parametrize("form", sorted(NO_SEARCH_OF_THE_FOLDER))
def test_a_fed_search_program_and_an_ordinary_command_with_a_numbered_redirect_stay_allowed(world, form):
    """Green before and after: a pipe feeds the program; the other two commands search nothing."""
    result = fix.ask_command(world, NO_SEARCH_OF_THE_FOLDER[form])
    fix.assert_allowed(result, f"{form}, at the root")


NO_SEARCH_BY_ROLE = list(zip(fix.OTHER_ROLES, ("the-other-program-as-the-reader-of-a-pipe-to-the-null-device",
                                               "git-status-with-joined-outputs",
                                               "the-other-program-as-the-reader-of-a-pipe-to-the-null-device")))


@pytest.mark.parametrize("who,form", NO_SEARCH_BY_ROLE, ids=fix.ids(NO_SEARCH_BY_ROLE))
def test_a_fed_search_program_and_an_ordinary_command_with_a_numbered_redirect_stay_allowed_for_every_role(
        world, who, form):
    result = fix.ask_command(world, NO_SEARCH_OF_THE_FOLDER[form], ROOT, who)
    fix.assert_allowed(result, f"{form}, at the root, by '{who}'")


@pytest.mark.parametrize("site", fix.SITES)
def test_a_fed_search_program_with_a_numbered_redirect_stays_allowed_from_a_copy_s_folder(world, site):
    form = "the-other-program-as-the-reader-of-a-pipe-to-the-null-device"
    result = fix.ask_command(world, NO_SEARCH_OF_THE_FOLDER[form], site)
    fix.assert_allowed(result, f"{form}, in a session that stands in the site '{site}'")
