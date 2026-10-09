"""W1-02 — daily spellings of a root search are judged as the search they are (DEC-570).

DEC-570: "Daily spellings: a comment after the search is no path; ``ls`` and
``grep`` option groups that hold a digit beside the recursive letter; ``egrep``
and ``fgrep``; a search behind ``timeout``, ``command``, ``env``, ``nice``,
``nohup`` or ``time``."

Held here, through the hook run as a process, on stand-in files, in a session
that stands in the project root, in the folder ``<P>`` a copy lies under, and in
a folder that holds a protected file. Four groups, each with what is refused
(red before the change: the guard allows it) and what stays allowed (green
before and after):

1. **a comment** after a search with no path is no path; with a source folder
   before the comment the search stays allowed, and a ``#`` inside a word is no
   comment;
2. **an option group that holds a digit** beside the recursive letter is a
   recursive option; without the recursive letter, or with a source folder, the
   command stays allowed;
3. **``egrep`` and ``fgrep``** are judged as ``grep`` is: refused with a
   recursive option and no path, the root as path, or a name filter that takes
   a file in; allowed on a named file, on a source folder, and as the reader of
   a pipe without recursion;
4. **a prefix command** (``timeout <n>``, ``command``, ``env`` with and without
   assignments, ``nice`` plain and with ``-n <n>``, ``nohup``, ``time``) does
   not hide the search behind it: one prefix, two stacked, after a keyword,
   with a numbered redirect behind the search; an ordinary command behind a
   prefix stays allowed.

No case either way: other options of a prefix; ``sudo`` as a prefix.

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
    return fix.make_world(tmp_path_factory.mktemp("daily-spellings"))


def _refused(world, forms, form, start=ROOT, who=fix.WIDEST, f=""):
    result = fix.ask_command(world, forms[form], start, who, f)
    fix.assert_refused_command(result, world, forms[form], start, f"'{form}' from '{start}' by '{who}'", f)


def _allowed(world, forms, form, start=ROOT, who=fix.WIDEST):
    result = fix.ask_command(world, forms[form], start, who)
    fix.assert_allowed(result, f"'{form}' from '{start}' by '{who}'")


# --------------------------------------------------------------------------
# 1. A comment after the search is no path
# --------------------------------------------------------------------------

COMMENTED = {
    "the-other-program-with-a-word-and-a-comment": PROG + " VALUE # all",
    "grep-recursive-with-a-word-and-a-comment": "grep -rn VALUE # all",
    "ls-recursive-and-a-comment": "ls -R # all",
}
COMMENTED_AT = [(form, ROOT) for form in sorted(COMMENTED)]
COMMENTED_AT += list(zip(sorted(COMMENTED), ("nested", "home", "sibling")))
# In a folder that holds a file the earlier rule refuses the search with no path; the comment gets it through today.
COMMENTED_AT += [("the-other-program-with-a-word-and-a-comment", start) for start in sorted(fix.HOLDING)]


@pytest.mark.parametrize("form,start", COMMENTED_AT, ids=fix.ids(COMMENTED_AT))
def test_a_search_with_no_path_and_a_comment_is_refused(world, form, start):
    """Group 1: the words of a comment are not paths of the search. Red before the change: allowed."""
    _refused(world, COMMENTED, form, start)


COMMENT_DAILY = {
    "the-other-program-over-a-source-folder-and-a-comment": PROG + " VALUE src # all",
    "grep-recursive-over-a-source-folder-and-a-comment": "grep -rn VALUE src # all",
    "ls-recursive-of-a-source-folder-and-a-comment": "ls -R src # all",
    "the-other-program-with-a-hash-inside-a-quoted-word": PROG + " 'a#b' src",
    "grep-recursive-with-a-hash-inside-a-word": "grep -rn a#b src",
}


@pytest.mark.parametrize("form", sorted(COMMENT_DAILY))
def test_a_search_of_a_source_folder_with_a_comment_or_a_hash_inside_a_word_stays_allowed(world, form):
    """Group 1, green before and after: the folder stands before the comment; a ``#`` inside a word opens none."""
    _allowed(world, COMMENT_DAILY, form)


# --------------------------------------------------------------------------
# 2. Option groups that hold a digit beside the recursive letter
# --------------------------------------------------------------------------

DIGIT_GROUPS = {
    "ls-one-per-line-and-recursive": "ls -1R",
    "ls-long-one-per-line-and-recursive": "ls -l1R",
    "ls-one-per-line-and-recursive-with-a-dot": "ls -1R .",
    "grep-context-and-recursive-with-no-path": "grep -2r VALUE",
    "grep-context-and-recursive-with-a-dot": "grep -2r VALUE .",
    "grep-lettered-context-and-recursive-with-a-dot": "grep -A2r VALUE .",
}
DIGITS_AT = [(form, ROOT) for form in sorted(DIGIT_GROUPS)]
DIGITS_AT += list(zip(("ls-one-per-line-and-recursive", "grep-context-and-recursive-with-no-path",
                       "ls-one-per-line-and-recursive"), fix.SITES))
# ``ls`` with any option and no path is refused there already; the digit gets the recursive ``grep`` through today.
DIGITS_AT += [("grep-context-and-recursive-with-no-path", start) for start in sorted(fix.HOLDING)]


@pytest.mark.parametrize("form,start", DIGITS_AT, ids=fix.ids(DIGITS_AT))
def test_a_recursive_option_group_that_holds_a_digit_is_refused_as_the_search_it_is(world, form, start):
    """Group 2: a digit in the group does not undo the recursive letter. Red before the change: allowed."""
    _refused(world, DIGIT_GROUPS, form, start)


DIGIT_DAILY = {
    "ls-one-per-line-of-a-source-folder": "ls -1 src",
    "ls-one-per-line-with-no-path-and-no-recursion": "ls -1",
    "ls-one-per-line-and-recursive-of-a-source-folder": "ls -1R src",
    "grep-context-in-a-named-source-file": "grep -2 VALUE <NAMED>",
    "grep-context-and-recursive-over-a-source-folder": "grep -2r VALUE src",
}


@pytest.mark.parametrize("form", sorted(DIGIT_DAILY))
def test_an_option_group_with_a_digit_and_no_search_of_the_root_stays_allowed(world, form):
    """Group 2, green before and after: no recursion, or a source folder."""
    _allowed(world, DIGIT_DAILY, form)


# --------------------------------------------------------------------------
# 3. egrep and fgrep are judged as grep is
# --------------------------------------------------------------------------

OTHER_GREPS = ("egrep", "fgrep")
AS_GREP = {
    "a-recursive-option-and-no-path": "{g} -r VALUE",
    "a-recursive-option-and-the-root-as-a-dot": "{g} -rn VALUE .",
}
GREPS_AT = [(program, form, ROOT) for program in OTHER_GREPS for form in sorted(AS_GREP)]
GREPS_AT += [(program, "a-recursive-option-and-no-path", site)
             for program, site in zip(OTHER_GREPS + OTHER_GREPS[:1], fix.SITES)]
GREPS_AT += [(program, "a-recursive-option-and-no-path", start)
             for program, start in zip(OTHER_GREPS, sorted(fix.HOLDING))]


@pytest.mark.parametrize("program,form,start", GREPS_AT, ids=fix.ids(GREPS_AT))
def test_the_other_names_of_grep_are_refused_as_grep_is(world, program, form, start):
    """Group 3: the same search under another name of the program. Red before the change: allowed."""
    forms = {form: AS_GREP[form].format(g=program)}
    _refused(world, forms, form, start)


GREP_FILTERED = {
    "a-name-filter-and-a-dot": "{g} -rn VALUE --include='<F>' .",
    "a-name-filter-and-no-path": "{g} -rn --include=<F> VALUE",
}
_FILTER_NAMES = sorted(fix.FILTERS)
# Each program in each spelling; the file and the filter in turn, so that each file is asked with each filter.
GREPS_WITH_A_FILTER = [(program, form, fix.FILES[(row + column) % 2], _FILTER_NAMES[row])
                       for row, program in enumerate(OTHER_GREPS)
                       for column, form in enumerate(sorted(GREP_FILTERED))]


@pytest.mark.parametrize("program,form,name,filter_", GREPS_WITH_A_FILTER, ids=fix.ids(GREPS_WITH_A_FILTER))
def test_the_other_names_of_grep_with_a_name_filter_that_takes_a_protected_file_in_are_refused(
        world, program, form, name, filter_):
    """Group 3 on the fifth batch's name filters: the file's own name, a glob over its extension."""
    forms = {form: GREP_FILTERED[form].format(g=program)}
    _refused(world, forms, form, f=fix.FILTERS[filter_](name))


GREP_DAILY = {
    "in-a-named-source-file": "{g} VALUE <NAMED>",
    "a-recursive-option-over-a-source-folder": "{g} -rn VALUE src",
    "the-reader-of-a-pipe-without-recursion": "git log --oneline | {g} VALUE",
    "a-recursive-option-with-a-filter-for-source-files-from-the-root": "{g} -rn VALUE --include='*.py' .",
}


@pytest.mark.parametrize("program", OTHER_GREPS)
@pytest.mark.parametrize("form", sorted(GREP_DAILY))
def test_the_other_names_of_grep_stay_allowed_where_grep_is(world, form, program):
    """Group 3, green before and after: a named file, a source folder, a pipe, a filter for source files."""
    forms = {form: GREP_DAILY[form].format(g=program)}
    _allowed(world, forms, form)


# --------------------------------------------------------------------------
# 4. A search behind a prefix command
# --------------------------------------------------------------------------

PREFIXES = {
    "timeout-with-its-duration": "timeout 10",
    "command": "command",
    "env-with-no-assignment": "env",
    "env-with-one-assignment": "env X=1",
    "env-with-two-assignments": "env X=1 Y=2",
    "nice": "nice",
    "nice-with-its-option-and-a-number": "nice -n 5",
    "nohup": "nohup",
    "time": "time",
}
# Each prefix before a search with no path and before one with the root as its path, the two programs in turn.
_KINDS = (("the-other-program-with-no-path", PROG + " VALUE", "grep-recursive-over-a-dot", "grep -rn VALUE ."),
          ("grep-recursive-with-no-path", "grep -rn VALUE", "the-other-program-over-a-dot", PROG + " VALUE ."))
BEHIND_A_PREFIX = {}
for _index, _prefix in enumerate(sorted(PREFIXES)):
    _first, _no_path, _second, _root_path = _KINDS[_index % 2]
    BEHIND_A_PREFIX[f"{_prefix}-then-{_first}"] = f"{PREFIXES[_prefix]} {_no_path}"
    BEHIND_A_PREFIX[f"{_prefix}-then-{_second}"] = f"{PREFIXES[_prefix]} {_root_path}"
BEHIND_A_PREFIX.update({
    "timeout-with-its-duration-then-ls-recursive": "timeout 10 ls -R",
    "nice-then-ls-recursive-of-a-dot": "nice ls -R .",
    # two prefixes stacked
    "timeout-then-env-with-an-assignment-then-the-other-program": "timeout 10 env X=1 " + PROG + " VALUE",
    "nohup-then-nice-then-the-other-program": "nohup nice " + PROG + " VALUE",
    "time-then-nice-with-its-option-then-grep-recursive-over-a-dot": "time nice -n 5 grep -rn VALUE .",
    # a prefix after a keyword
    "the-condition-of-an-if-behind-timeout": "if timeout 5 " + PROG + " -q VALUE; then :; fi",
    # a numbered redirect behind the search
    "timeout-then-the-other-program-to-the-null-device": "timeout 10 " + PROG + " VALUE 2>/dev/null",
    "nice-then-grep-recursive-joined-outputs-and-a-pipe": "nice grep -rn VALUE 2>&1 | head",
})


@pytest.mark.parametrize("form", sorted(BEHIND_A_PREFIX))
def test_a_search_of_the_root_behind_a_prefix_command_is_refused(world, form):
    """Group 4: the prefix is not the command. Red before the change: allowed."""
    _refused(world, BEHIND_A_PREFIX, form)


PREFIX_ELSEWHERE = {
    "timeout-then-the-other-program-with-no-path": "timeout 10 " + PROG + " VALUE",
    "env-with-an-assignment-then-grep-recursive-over-a-dot": "env X=1 grep -rn VALUE .",
}
PREFIX_AT = list(zip(sorted(PREFIX_ELSEWHERE) + sorted(PREFIX_ELSEWHERE)[:1], fix.SITES))
PREFIX_AT += [("timeout-then-the-other-program-with-no-path", start) for start in sorted(fix.HOLDING)]


@pytest.mark.parametrize("form,start", PREFIX_AT, ids=fix.ids(PREFIX_AT))
def test_a_search_behind_a_prefix_command_is_refused_from_a_copy_s_folder_and_beside_a_protected_file(
        world, form, start):
    """Group 4 from ``<P>`` and in a folder that holds a file (the earlier rule's refusal, got through today)."""
    _refused(world, PREFIX_ELSEWHERE, form, start)


PREFIX_DAILY = {
    "a-test-run-behind-timeout": "timeout 60 python3 -m pytest tests/unit -q",
    "the-other-program-over-a-source-folder-behind-time": "time " + PROG + " VALUE src",
    "a-test-run-behind-env-with-an-assignment": "env X=1 python3 -m pytest tests/unit -q",
    "grep-recursive-over-a-source-folder-behind-nice": "nice grep -rn VALUE src",
    "command-asked-where-a-program-is": "command -v python3",
    # measured: allowed today; the pipe feeds the program behind the prefix
    "the-other-program-behind-timeout-as-the-reader-of-a-pipe": "git log --oneline | timeout 5 " + PROG + " VALUE",
}


@pytest.mark.parametrize("form", sorted(PREFIX_DAILY))
def test_an_ordinary_command_behind_a_prefix_command_stays_allowed(world, form):
    """Group 4, green before and after."""
    _allowed(world, PREFIX_DAILY, form)


# --------------------------------------------------------------------------
# For every role
# --------------------------------------------------------------------------

REFUSED_FOR_ROLES = {
    "the-other-program-with-a-word-and-a-comment": COMMENTED["the-other-program-with-a-word-and-a-comment"],
    "ls-one-per-line-and-recursive": DIGIT_GROUPS["ls-one-per-line-and-recursive"],
    "grep-context-and-recursive-with-a-dot": DIGIT_GROUPS["grep-context-and-recursive-with-a-dot"],
    "egrep-with-a-recursive-option-and-no-path": "egrep -r VALUE",
    "fgrep-with-a-recursive-option-and-the-root-as-a-dot": "fgrep -rn VALUE .",
    "timeout-then-the-other-program": "timeout 10 " + PROG + " VALUE",
    "env-with-an-assignment-then-grep-recursive-over-a-dot": "env X=1 grep -rn VALUE .",
    "time-then-the-other-program": "time " + PROG + " VALUE",
}
BY_ROLE = fix.share(REFUSED_FOR_ROLES)


@pytest.mark.parametrize("who,form", BY_ROLE, ids=fix.ids(BY_ROLE))
def test_a_daily_spelling_of_a_root_search_is_refused_for_every_role(world, who, form):
    """An engineer, the test designer and a session with no role (the orchestrator asks every form above)."""
    _refused(world, REFUSED_FOR_ROLES, form, ROOT, who)


ALLOWED_FOR_ROLES = {
    "the-other-program-over-a-source-folder-and-a-comment":
        COMMENT_DAILY["the-other-program-over-a-source-folder-and-a-comment"],
    "ls-one-per-line-of-a-source-folder": DIGIT_DAILY["ls-one-per-line-of-a-source-folder"],
    "egrep-with-a-recursive-option-over-a-source-folder": "egrep -rn VALUE src",
    "a-test-run-behind-timeout": PREFIX_DAILY["a-test-run-behind-timeout"],
    "the-other-program-over-a-source-folder-behind-time":
        PREFIX_DAILY["the-other-program-over-a-source-folder-behind-time"],
}
DAILY_BY_ROLE = fix.share(ALLOWED_FOR_ROLES)


@pytest.mark.parametrize("who,form", DAILY_BY_ROLE, ids=fix.ids(DAILY_BY_ROLE))
def test_the_daily_forms_of_these_spellings_stay_allowed_for_every_role(world, who, form):
    _allowed(world, ALLOWED_FOR_ROLES, form, ROOT, who)
