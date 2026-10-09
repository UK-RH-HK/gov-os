"""W1-02 — a search program that reads a pipe or an input redirect searches no folder (DEC-557, the daily forms).

DEC-557 refuses "a search from the project root that gives no path or glob".
The other search program of the fifth batch (``rg``), given no path, searches
the folder it runs in only when nothing feeds it: when a pipe or an input
redirect gives it its standard input, it searches that, and no file of the
folder (its own help names the form ``command | rg [OPTIONS] PATTERN``; seen on
this machine in a scratch folder, README). ``<a command> | rg <word>`` is a
form of daily work that reads neither file.

Held here, on stand-in files, from the root and from the folder ``<P>`` a copy
lies under (a sibling checkout, a folder below the root, the stand-in home):

- **allowed**: that program with a word and no path as the reader of a pipe
  (after ``|`` and ``|&``, as the second and as the third command of a
  pipeline), with an input redirect from a named file that is neither
  protected file nor a copy, and with name filters on a pipe; and that program
  asked only for its version or its help;
- **refused, as today**: on a pipe with a path that is the root or ``<P>``; on
  a pipe with the option that lists files instead of searching; as the first
  command of a pipeline; after ``||``, ``&&`` or ``;``; ``grep`` with a
  recursive option and no path on a pipe (its manual: with no file, a
  recursive search examines the working directory); a pipe whose first
  command reads either file; an input redirect from either file or a copy; and
  every form in a session that stands in a folder that holds either file.

**Before the change** (found by running the hook, README) the guard refuses
every form of the first list but the three with a name filter that includes:
those cases are red, because the guard refuses an allowed form. Every case of
the second list is green before and after.

No case either way (README): a subshell or a group as the reader of a pipe,
``xargs``, a here-string or a here-document into that program, process
substitution. No case needs the guard to walk a tree.

A protected file's path comes from the guard's constants, never typed, and no
id or failure message carries a path or a command.
"""

from __future__ import annotations

import pytest

import w1_02_copies_support as batch
import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_round_support as rnd

ROOT = rnd.ROOT
SITES = rnd.SITES
WIDEST = rnd.WIDEST
# A named file that is neither protected file nor a copy: a source file of the session's project.
NAMED_REL = "src/app/main.py"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return rnd.make_world(tmp_path_factory.mktemp("search-on-a-pipe"))


def _sh(command):
    """A shell form asked in a session that stands in the start."""
    return ("Bash", command, "start")


def _ask(world, form, start, who=WIDEST):
    """One form from ``start``; ``{named}`` is the named source file, as an absolute path."""
    return rnd.ask_form(world, form, start, who, named=str(world.project / NAMED_REL))


# --------------------------------------------------------------------------
# Allowed: the reader of a pipe, an input redirect from a named file
# --------------------------------------------------------------------------

# Red before the change: the guard refuses each as a search of the folder.
FED = {
    "the-reader-of-a-pipe-from-git-log": _sh("git log --oneline | rg VALUE"),
    "the-reader-of-a-pipe-from-a-listing": _sh("ls | rg VALUE"),
    "the-reader-of-a-pipe-from-a-named-source-file": _sh("cat {named} | rg -n VALUE"),
    "the-reader-of-a-pipe-with-the-word-as-an-option": _sh("git log --oneline | rg -e VALUE"),
    "after-a-pipe-of-both-outputs": _sh("git status |& rg VALUE"),
    "after-a-pipe-of-both-outputs-spelled-out": _sh("git status 2>&1 | rg VALUE"),
    "the-second-command-of-three": _sh("git log --oneline | rg VALUE | head -5"),
    "the-third-command-of-three": _sh("git log --oneline | sort | rg VALUE"),
    "an-input-redirect-from-a-named-file": _sh("rg VALUE < {named}"),
    "an-input-redirect-glued-to-the-named-file": _sh("rg -n VALUE <{named}"),
    "a-filter-that-only-excludes-on-a-pipe": _sh("git log --oneline | rg -g '!*.md' VALUE"),
}
# Green before the change already: a filter that includes keeps both files out of a search of the folder too.
FED_WITH_A_FILTER = {
    "a-short-filter-for-source-files-on-a-pipe": _sh("git log --oneline | rg -g '*.py' VALUE"),
    "a-long-filter-for-source-files-on-a-pipe": _sh("git log --oneline | rg --glob='*.py' VALUE"),
    "a-case-insensitive-filter-for-source-files-on-a-pipe": _sh("git log --oneline | rg --iglob '*.PY' VALUE"),
}
ALL_FED = dict(FED, **FED_WITH_A_FILTER)


@pytest.mark.parametrize("form", sorted(ALL_FED))
def test_a_search_program_fed_by_a_pipe_or_an_input_redirect_stays_allowed_at_the_root(world, form):
    """Point A: with no path it reads what feeds it, and no file of the root."""
    result = _ask(world, ALL_FED[form], ROOT)
    protected.assert_allowed(result, f"the search program as {form}, at the root")


_FED_NAMES = sorted(FED)
FED_BY_ROLE = [(who, _FED_NAMES[(2 * row + step * 5) % len(_FED_NAMES)])
               for row, who in enumerate(rnd.OTHER_ROLES) for step in range(2)]


@pytest.mark.parametrize("who,form", FED_BY_ROLE, ids=[f"{who}-{form}" for who, form in FED_BY_ROLE])
def test_a_search_program_fed_by_a_pipe_stays_allowed_for_every_role(world, who, form):
    """An engineer, the test designer and a session with no role (the orchestrator asks every form above)."""
    result = _ask(world, FED[form], ROOT, who)
    protected.assert_allowed(result, f"the search program as {form}, at the root, by '{who}'")


# From <P>: forms that name no file of the folder (a listing of <P> is another rule's).
FED_AT_A_COPY = {
    "the-reader-of-a-pipe-from-git-log": FED["the-reader-of-a-pipe-from-git-log"],
    "the-third-command-of-three": _sh("echo VALUE | sort | rg -n VALUE"),
    "an-input-redirect-from-a-named-file": FED["an-input-redirect-from-a-named-file"],
}
AT_A_COPY = [(site, form) for site in SITES for form in sorted(FED_AT_A_COPY)
             if site == "sibling" or form != "an-input-redirect-from-a-named-file"]


@pytest.mark.parametrize("site,form", AT_A_COPY, ids=[f"{site}-{form}" for site, form in AT_A_COPY])
def test_a_search_program_fed_by_a_pipe_stays_allowed_from_a_copy_s_folder(world, site, form):
    """Point A from ``<P>``: a sibling checkout, a folder below the root, the stand-in home."""
    result = _ask(world, FED_AT_A_COPY[form], site)
    protected.assert_allowed(result, f"the search program as {form}, in a session that stands in the site '{site}'")


# --------------------------------------------------------------------------
# Allowed: asked only for its version or its help
# --------------------------------------------------------------------------

# The two long options and their short forms, as the program's own help names them on this machine.
ONLY_ASKED = {
    "its-version-by-the-long-option": _sh("rg --version"),
    "its-version-by-the-short-option": _sh("rg -V"),
    "its-help-by-the-long-option": _sh("rg --help"),
    "its-help-by-the-short-option": _sh("rg -h"),
}


@pytest.mark.parametrize("form", sorted(ONLY_ASKED))
def test_the_search_program_asked_only_for_its_version_or_its_help_is_allowed_at_the_root(world, form):
    """Point A: with nothing else on the command it searches nothing. Red before the change."""
    result = _ask(world, ONLY_ASKED[form], ROOT)
    protected.assert_allowed(result, f"the search program asked for {form}, at the root")


def test_the_search_program_asked_only_for_its_version_is_allowed_for_a_session_with_no_role(world):
    result = _ask(world, ONLY_ASKED["its-version-by-the-long-option"], ROOT, folders.NO_ROLE)
    protected.assert_allowed(result, "the search program asked for its version, at the root, with no role")


# --------------------------------------------------------------------------
# Refused as today: the folder is searched all the same
# --------------------------------------------------------------------------

UNFED = {
    # a path is given: the pipe is not read
    "on-a-pipe-with-a-dot-as-its-path": _sh("ls | rg VALUE ."),
    "on-a-pipe-with-the-absolute-start-as-its-path": _sh("ls | rg VALUE {abs}"),
    # it lists the files of the folder, whatever feeds it
    "on-a-pipe-with-the-option-that-lists-files": _sh("ls | rg --files"),
    # nothing feeds it
    "the-first-command-of-a-pipeline": _sh("rg VALUE | head -5"),
    "after-an-or": _sh("true || rg VALUE"),
    "after-an-and": _sh("true && rg VALUE"),
    "after-a-semicolon": _sh("true; rg VALUE"),
    "after-a-pipeline-that-has-ended": _sh("ls | sort; rg VALUE"),
    # grep with a recursive option and no file examines the working directory, not the pipe
    "grep-r-on-a-pipe": _sh("ls | grep -r VALUE"),
    "grep-rn-on-a-pipe": _sh("git log --oneline | grep -rn VALUE"),
    "grep-the-long-recursive-option-on-a-pipe": _sh("ls | grep --recursive VALUE"),
}


@pytest.mark.parametrize("form", sorted(UNFED))
def test_a_search_of_the_root_stays_refused_whatever_stands_before_it(world, form):
    """Stays refused (green before and after): a pipe changes nothing when the program does not read it."""
    result = _ask(world, UNFED[form], ROOT)
    rnd.assert_refused_by_the_rule(result, f"the search '{form}' at the root")


UNFED_AT_A_COPY = ("on-a-pipe-with-a-dot-as-its-path", "the-first-command-of-a-pipeline", "grep-r-on-a-pipe")


@pytest.mark.parametrize("site", SITES)
@pytest.mark.parametrize("form", UNFED_AT_A_COPY)
def test_a_search_of_a_copy_s_folder_stays_refused_whatever_stands_before_it(world, form, site):
    result = _ask(world, UNFED[form], site)
    rnd.assert_refused_by_the_rule(result, f"the search '{form}' in a session that stands in the site '{site}'")


UNFED_BY_ROLE = [(folders.NOT_A_WRITER, "on-a-pipe-with-the-absolute-start-as-its-path"),
                 (folders.NO_ROLE, "the-first-command-of-a-pipeline")]


@pytest.mark.parametrize("who,form", UNFED_BY_ROLE, ids=[f"{who}-{form}" for who, form in UNFED_BY_ROLE])
def test_a_search_of_the_root_stays_refused_for_other_roles(world, who, form):
    result = _ask(world, UNFED[form], ROOT, who)
    rnd.assert_refused_by_the_rule(result, f"the search '{form}' at the root by '{who}'")


def test_the_refusal_of_a_search_on_a_pipe_with_a_path_names_the_rule_and_no_path(world):
    """The command carries the root: a refusal that echoes the command fails."""
    what = "the search on a pipe with the absolute root as its path"
    result = _ask(world, UNFED["on-a-pipe-with-the-absolute-start-as-its-path"], ROOT)
    rnd.assert_refused_by_the_rule(result, what)
    rnd.assert_names_a_rule_and_a_decision(result, what)
    for name in rnd.FILES:
        rnd.assert_says_nothing(result, world, ROOT, name, what, more=("rg VALUE",))


# --------------------------------------------------------------------------
# Refused as today: what feeds the program is a read of a protected file
# --------------------------------------------------------------------------

# label -> (site of the file, the command; ``{abs}`` the file, ``{rel}`` its project-relative path).
FEEDS_A_FILE = {
    "a-pipe-whose-first-command-reads-the-file": ("own", "cat {abs} | rg VALUE"),
    "a-pipe-whose-first-command-reads-a-copy": ("sibling", "cat {abs} | rg -n VALUE"),
    "an-input-redirect-from-the-file": ("own", "rg VALUE < {rel}"),
    "an-input-redirect-from-a-copy": ("sibling", "rg VALUE < {abs}"),
}


@pytest.mark.parametrize("name", rnd.FILES)
@pytest.mark.parametrize("form", sorted(FEEDS_A_FILE))
def test_a_pipe_or_a_redirect_that_feeds_a_protected_file_to_the_search_program_stays_refused(world, form, name):
    """Refused as the read it is, and the refusal says nothing of the file (green before and after)."""
    site, command = FEEDS_A_FILE[form]
    what = f"{form} (the stand-in {name})"
    result = folders.ask_bash(world, batch.fill(world, site, name, command), WIDEST)
    rnd.assert_refused_by_the_rule(result, what)
    batch.assert_says_nothing_of_the_file(result, world, site, name, what)


@pytest.mark.parametrize("name", rnd.FILES)
def test_in_a_folder_that_holds_a_protected_file_the_search_program_on_a_pipe_stays_refused(world, name):
    """As today, no change: the rule of the earlier batches refuses that program there with no path, fed or not."""
    result = folders.ask_bash(world, "git log --oneline | rg VALUE", WIDEST, world.site("own").folder(name))
    rnd.assert_refused_by_the_rule(
        result, f"the search program as the reader of a pipe in the folder that holds the stand-in {name}")
