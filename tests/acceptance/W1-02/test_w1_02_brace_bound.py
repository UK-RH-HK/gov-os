"""W1-02 — a brace word that expands past the bound is refused, not judged unexpanded (DEC-570).

DEC-570: "A brace word that expands past the bound is refused, not judged
unexpanded."

**The bound, measured on the guard as built** (through the hook, README): the
read rule expands one brace word to at most ``BOUND`` = 256 words. A word that
expands to exactly 256 words of which one is a protected file is refused today;
the same word with one more group (512 words) is allowed today: what is left
unexpanded is judged as a plain word, and names no file.

Held here, through the hook run as a process, on stand-in files. The word is a
group of two alternatives followed by groups of an empty and a one-letter
alternative, so it doubles with every group:

- **refused** (red before the change: allowed): a word that expands to twice
  the bound and one that expands to sixteen times it, in a shell command that
  reads it, in the Glob tool's ``pattern``, in the Grep tool's ``glob`` and in
  the other search program's glob option; with a protected file among the
  expansions, and with none (the rule cannot judge a word it does not expand);
- **refused, before and after**: the word at the bound with a protected file
  among its expansions;
- **stays allowed**: a brace word of a few alternatives that names source
  files, one that expands to 64 words, the Glob tool and the Grep tool with a
  brace of two extensions.

No case either way: a word that expands to more than 64 words and fewer than
twice the bound and takes neither file in.

A protected file's path comes from the guard's constants, never typed, and no
id or failure message carries a path, a word or a command.
"""

from __future__ import annotations

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_fix_support as fix

ROOT = fix.ROOT
PROG = fix.PROG
# The most words the rule as built makes of one brace word (measured, README).
BOUND = 256
SIZES = {"twice-the-bound": 2 * BOUND, "sixteen-times-the-bound": 16 * BOUND}
OTHER = "zz"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return fix.make_world(tmp_path_factory.mktemp("brace-bound"))


def brace_word(first, words):
    """A brace word that expands to ``words`` words: ``first`` beside another alternative, then doubling groups."""
    groups = (words // 2).bit_length() - 1
    assert 2 ** (groups + 1) == words
    return "{" + first + "," + OTHER + "}" + "{,a}" * groups


# Where the word stands: label -> builder(word) -> (tool, input). The session stands in the start.
PLACES = {
    "a-shell-command-that-reads-it": lambda word: ("Bash", {"command": "cat " + word}),
    "the-Glob-tool-s-pattern": lambda word: ("Glob", {"pattern": word}),
    "the-Grep-tool-s-glob": lambda word: ("Grep", {"pattern": "VALUE", "glob": word}),
    "the-other-program-s-glob-option": lambda word: ("Bash", {"command": PROG + " VALUE -g '" + word + "'"}),
}


def _ask(world, place, word, start=ROOT, who=fix.WIDEST):
    tool_name, tool_input = PLACES[place](word)
    return fix.ask_tool(world, tool_name, tool_input, start, who)


# --------------------------------------------------------------------------
# Refused: a word that expands past the bound
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", fix.FILES)
@pytest.mark.parametrize("size", sorted(SIZES))
@pytest.mark.parametrize("place", sorted(PLACES))
def test_a_brace_word_past_the_bound_whose_expansions_take_a_protected_file_in_is_refused(world, place, size, name):
    """Point 4: one expansion is the file's project-relative path. Red before the change: allowed."""
    word = brace_word(protected.PROTECTED[name], SIZES[size])
    result = _ask(world, place, word)
    fix.assert_refused(result, world, ROOT, f"a brace word of {size} that takes the stand-in {name} in, in {place}",
                       (word, "{,a}{,a}"))


@pytest.mark.parametrize("size", sorted(SIZES))
@pytest.mark.parametrize("place", sorted(PLACES))
def test_a_brace_word_past_the_bound_is_refused_also_where_no_expansion_names_a_protected_file(world, place, size):
    """Point 4: the rule cannot judge a word it does not expand. Red before the change: allowed."""
    word = brace_word("yy", SIZES[size])
    result = _ask(world, place, word)
    fix.assert_refused(result, world, ROOT, f"a brace word of {size} that takes neither file in, in {place}",
                       (word, "{,a}{,a}"))


AT_A_COPY = [(site, name) for site in ("sibling", "nested") for name in fix.FILES]


@pytest.mark.parametrize("site,name", AT_A_COPY, ids=fix.ids(AT_A_COPY))
def test_a_brace_word_past_the_bound_that_takes_a_copy_in_is_refused(world, site, name):
    """Point 4 on a copy: the copy's absolute path in a shell command; its relative path as a Glob pattern from ``<P>``."""
    copy = world.site(site).path(name)
    for place, first in (("a-shell-command-that-reads-it", str(copy)),
                         ("the-Glob-tool-s-pattern", protected.PROTECTED[name])):
        word = brace_word(first, 2 * BOUND)
        result = _ask(world, place, word, site)
        fix.assert_refused(result, world, site,
                           f"a brace word of twice the bound that takes the copy of the stand-in {name} in, in {place}, "
                           f"in a session that stands in the site '{site}'", (word,))


@pytest.mark.parametrize("start", sorted(fix.HOLDING))
def test_a_brace_word_past_the_bound_is_refused_in_a_folder_that_holds_a_protected_file(world, start):
    """In the folder that holds the file one expansion is the file's own name."""
    word = brace_word(fix.base_of(fix.HOLDING[start]), 2 * BOUND)
    result = _ask(world, "a-shell-command-that-reads-it", word, start)
    fix.assert_refused(result, world, start, f"a brace word of twice the bound that takes the file in, in {start}",
                       (word,))


BY_ROLE = list(zip(fix.OTHER_ROLES, sorted(PLACES)[:3], fix.FILES + fix.FILES[:1]))


@pytest.mark.parametrize("who,place,name", BY_ROLE, ids=fix.ids(BY_ROLE))
def test_a_brace_word_past_the_bound_is_refused_for_every_role(world, who, place, name):
    """An engineer, the test designer and a session with no role (the orchestrator asks every form above)."""
    word = brace_word(protected.PROTECTED[name], 2 * BOUND)
    result = _ask(world, place, word, ROOT, who)
    fix.assert_refused(result, world, ROOT,
                       f"a brace word of twice the bound that takes the stand-in {name} in, in {place}, by '{who}'",
                       (word,))


# --------------------------------------------------------------------------
# Refused before and after: the word at the bound
# --------------------------------------------------------------------------

AT_THE_BOUND = [(place, fix.FILES[row % 2]) for row, place in enumerate(sorted(PLACES))]


@pytest.mark.parametrize("place,name", AT_THE_BOUND, ids=fix.ids(AT_THE_BOUND))
def test_a_brace_word_at_the_bound_whose_expansions_take_a_protected_file_in_stays_refused(world, place, name):
    """The measurement of the bound, held: 256 words are expanded and judged (green before and after)."""
    word = brace_word(protected.PROTECTED[name], BOUND)
    result = _ask(world, place, word)
    fix.assert_refused(result, world, ROOT, f"a brace word at the bound that takes the stand-in {name} in, in {place}",
                       (word,))


# --------------------------------------------------------------------------
# Stays allowed: ordinary brace words
# --------------------------------------------------------------------------

ORDINARY = {
    "a-listing-of-three-named-source-files": ("Bash", {"command": "ls src/{a,b,c}.py"}),
    "a-word-that-expands-to-sixty-four-source-files": ("Bash", {"command": "ls src/" + "{a,b}" * 6 + ".py"}),
    "the-Glob-tool-with-a-brace-of-two-extensions-below-a-source-folder": ("Glob", {"pattern": "src/**/*.{py,md}"}),
    "the-Grep-tool-with-a-brace-of-two-extensions-and-a-source-folder":
        ("Grep", {"pattern": "VALUE", "glob": "*.{py,md}", "path": "src"}),
    "the-other-program-with-a-brace-of-two-extensions-and-a-source-folder":
        ("Bash", {"command": PROG + " VALUE -g '*.{py,md}' src"}),
}


ORDINARY_BY = [(fix.WIDEST, form) for form in sorted(ORDINARY)] + list(zip(fix.OTHER_ROLES, sorted(ORDINARY)))


@pytest.mark.parametrize("who,form", ORDINARY_BY, ids=fix.ids(ORDINARY_BY))
def test_an_ordinary_brace_word_stays_allowed(world, who, form):
    """Green before and after: a few alternatives, sixty-four words, a brace of extensions; a share for other roles."""
    tool_name, tool_input = ORDINARY[form]
    result = fix.ask_tool(world, tool_name, tool_input, ROOT, who)
    fix.assert_allowed(result, f"{form}, at the root, by '{who}'")


def test_a_brace_word_in_a_write_target_is_decided_as_today_and_not_as_a_read(world):
    """``mkdir -p`` of a scratch folder with two brace groups of two: four folders, neither file.

    Measured: the guard denies it today for every role, by the rule for a write
    whose target it does not resolve (not by the read rule). That is another
    rule's decision and this round changes nothing of it: held here is only
    that the read rule is not what refuses it, before and after.
    """
    command = "mkdir -p " + folders.SCRATCH_REL + "/{a,b}/{x,y}"
    result = fix.ask_tool(world, "Bash", {"command": command})
    fix.assert_not_refused_as_a_read(result, "a brace word of four folders in a write target below the scratch folder")
