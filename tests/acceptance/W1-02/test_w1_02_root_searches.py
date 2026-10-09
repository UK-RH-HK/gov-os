"""W1-02 — a search from the project root that gives no path or glob is refused, for every role (DEC-557, P-23).

DEC-557: "A search from the project root that gives no path or glob is refused
by the guard, for every role."

A search is a call that reads the content or the names of every file below its
start. Held here, on stand-in files in a temporary project:

- **the search tool** with no ``path`` in a session that stands in the root, or
  with the root as ``path`` (absolute, ``.``, a relative spelling that resolves
  to it), and no glob; the same with a ``type`` filter only and with an
  excluding glob only;
- **the shell**: a recursive ``grep`` (``-r``, ``-R``, a cluster, the long
  forms), ``rg``, ``find`` with no test on the name, ``ls -R`` and its
  clusters, with no path or with the root as the path; several paths of which
  one is the root; a recursive search over a wildcard word from the root;
- **the same from the folder ``<P>`` a copy lies under** (DEC-548, DEC-553): a
  sibling checkout, a folder below the root that is not the root, the stand-in
  home folder.

**Before the change the guard allows every one of these** (found by running the
hook, README): all the refusal cases are red.

**What stays allowed** is held in the second half and is green before and
after: a search of a source folder, a search from the root with a glob for
source files, a named file, a listing without recursion, and a search from a
folder under which neither file nor a copy lies.

No case either way (README): ``find`` from the root with a test on the name; a
command that names no path and reads the tree or the history by itself
(``git grep`` with no path, ``git log -p``, ``git show``); a search that starts
above ``<P>`` and outside the project. No case needs the guard to walk a tree.
"""

from __future__ import annotations

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_round_support as rnd

ROOT = rnd.ROOT
SITES = rnd.SITES
WIDEST = rnd.WIDEST


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return rnd.make_world(tmp_path_factory.mktemp("root-searches"))


def _grep(where=None, **fields):
    return ("Grep", dict({"pattern": "VALUE"}, **fields), where)


def _sh(command, where=None):
    return ("Bash", command, where)


# --------------------------------------------------------------------------
# Refused: the search tool from the root
# --------------------------------------------------------------------------

ROOT_TOOL = {
    "no-path": _grep(),
    "the-root-as-an-absolute-path": _grep(path="{abs}"),
    "the-root-with-a-trailing-slash": _grep(path="{abs}/"),
    "a-dot": _grep(path="."),
    "a-dot-and-a-slash": _grep(path="./"),
    "a-relative-spelling-that-resolves-to-the-root": _grep(path="src/.."),
    "two-dots-in-a-session-that-stands-one-folder-below": _grep("below", path=".."),
    "a-type-filter-only-and-no-path": _grep(type="py"),
    "a-type-filter-only-and-the-root": _grep(path="{abs}", type="py"),
    "an-excluding-glob-only-and-no-path": _grep(glob="!*.md"),
    "an-excluding-glob-only-and-the-root": _grep(path="{abs}", glob="!*.md"),
    "a-type-filter-and-an-excluding-glob": _grep(path="{abs}", type="py", glob="!*.md"),
}


@pytest.mark.parametrize("form", sorted(ROOT_TOOL))
def test_a_search_tool_call_from_the_root_with_no_path_or_glob_is_refused(world, form):
    """Point 1, the search tool: nothing keeps either file out of such a search."""
    result = rnd.ask_form(world, ROOT_TOOL[form], ROOT)
    rnd.assert_refused_by_the_rule(result, f"a search tool call from the root with {form}")


# --------------------------------------------------------------------------
# Refused: the shell from the root
# --------------------------------------------------------------------------

ROOT_SHELL = {
    # a recursive content search
    "grep-r-with-no-path": _sh("grep -r VALUE"),
    "grep-r-with-a-dot": _sh("grep -r VALUE ."),
    "grep-r-with-a-dot-and-a-slash": _sh("grep -r VALUE ./"),
    "grep-r-with-the-absolute-root": _sh("grep -r VALUE {abs}"),
    "grep-capital-r": _sh("grep -R VALUE ."),
    "grep-rn": _sh("grep -rn VALUE ."),
    "grep-capital-rn-with-no-path": _sh("grep -Rn VALUE"),
    "grep-a-cluster-that-ends-in-r": _sh("grep -inr VALUE ."),
    "grep-the-long-form": _sh("grep --recursive VALUE ."),
    "grep-the-dereferencing-long-form-with-no-path": _sh("grep --dereference-recursive VALUE"),
    "grep-rn-with-the-pattern-as-an-option": _sh("grep -rn -e VALUE ."),
    "grep-several-paths-the-root-last": _sh("grep -rn VALUE src ."),
    "grep-several-paths-the-root-first": _sh("grep -rn VALUE . tests"),
    "grep-r-after-a-change-to-the-root": _sh("cd {abs} && grep -r VALUE", "below"),
    "grep-r-two-dots-from-one-folder-below": _sh("grep -r VALUE ..", "below"),
    # the other search program searches the folder it runs in by default
    "rg-with-no-path": _sh("rg VALUE"),
    "rg-with-a-dot": _sh("rg VALUE ."),
    "rg-with-a-dot-and-a-slash": _sh("rg VALUE ./"),
    "rg-with-the-absolute-root": _sh("rg VALUE {abs}"),
    "rg-with-an-option-and-no-path": _sh("rg -n VALUE"),
    "rg-listing-the-files-that-match": _sh("rg -l VALUE"),
    "rg-listing-every-file": _sh("rg --files"),
    "rg-several-paths-of-which-one-is-the-root": _sh("rg VALUE src ."),
    "rg-after-a-change-to-the-root": _sh("cd {abs} && rg VALUE", "below"),
    # find with no test on the name
    "find-with-no-start": _sh("find"),
    "find-with-a-dot": _sh("find ."),
    "find-with-a-dot-and-a-slash": _sh("find ./"),
    "find-with-the-absolute-root": _sh("find {abs}"),
    "find-with-a-test-on-the-type": _sh("find . -type f"),
    "find-with-no-start-and-a-test-on-the-type": _sh("find -type f"),
    "find-several-starts-of-which-one-is-the-root": _sh("find src ."),
    "find-after-a-change-to-the-root": _sh("cd {abs} && find .", "below"),
    # a recursive listing
    "ls-capital-r-with-no-path": _sh("ls -R"),
    "ls-capital-r-with-a-dot": _sh("ls -R ."),
    "ls-l-capital-r": _sh("ls -lR"),
    "ls-la-capital-r": _sh("ls -laR"),
    "ls-la-capital-r-with-a-dot": _sh("ls -laR ."),
    "ls-capital-r-with-the-absolute-root": _sh("ls -R {abs}"),
    "ls-capital-r-several-paths-of-which-one-is-the-root": _sh("ls -R src ."),
    "ls-capital-r-after-a-change-to-the-root": _sh("cd {abs} && ls -R", "below"),
}


@pytest.mark.parametrize("form", sorted(ROOT_SHELL))
def test_a_shell_search_from_the_root_with_no_path_is_refused(world, form):
    """Point 1, the shell: a recursive search, a ``find`` or a recursive listing whose start is the root."""
    result = rnd.ask_form(world, ROOT_SHELL[form], ROOT)
    rnd.assert_refused_by_the_rule(result, f"the shell search '{form}' from the root")


# A wildcard word from the root takes in the folders that hold the held-out file: the search goes down into them.
WILDCARD_WORD = {
    "grep-r-over-a-star": _sh("grep -r VALUE *"),
    "grep-rn-over-a-dot-slash-star": _sh("grep -rn VALUE ./*"),
}


@pytest.mark.parametrize("form", sorted(WILDCARD_WORD))
def test_a_recursive_search_over_a_wildcard_word_from_the_root_is_refused(world, form):
    """Point 1: the wildcard takes in a folder that holds a protected file, and the search is recursive.

    Allowed before the change: the guard matches a wildcard word against the two
    files' own paths, and a single star stops at the first folder.
    """
    result = rnd.ask_form(world, WILDCARD_WORD[form], ROOT)
    rnd.assert_refused_by_the_rule(result, f"the shell search '{form}' from the root")


# --------------------------------------------------------------------------
# Refused: the same from a copy's <P>
# --------------------------------------------------------------------------

P_FORMS = {
    "Grep-with-an-absolute-path": _grep(path="{abs}"),
    "Grep-with-a-relative-path": _grep(path="{rel}"),
    "Grep-with-no-path-in-a-session-that-stands-there": _grep("start"),
    "Grep-with-a-type-filter-only": _grep(path="{abs}", type="py"),
    "Grep-with-an-excluding-glob-only": _grep(path="{abs}", glob="!*.md"),
    "grep-r-absolute": _sh("grep -r VALUE {abs}"),
    "grep-rn-relative": _sh("grep -rn VALUE {rel}"),
    "grep-r-after-a-change-of-folder": _sh("cd {abs} && grep -r VALUE"),
    "grep-r-with-a-dot-in-a-session-that-stands-there": _sh("grep -r VALUE .", "start"),
    "rg-absolute": _sh("rg VALUE {abs}"),
    "rg-with-no-path-in-a-session-that-stands-there": _sh("rg VALUE", "start"),
    "find-absolute": _sh("find {abs}"),
    "find-after-a-change-of-folder": _sh("cd {abs} && find . -type f"),
    "ls-capital-r-absolute": _sh("ls -R {abs}"),
    "ls-la-capital-r-in-a-session-that-stands-there": _sh("ls -laR", "start"),
}


@pytest.mark.parametrize("site", SITES)
@pytest.mark.parametrize("form", sorted(P_FORMS))
def test_a_search_from_a_copy_s_folder_with_no_path_or_glob_is_refused(world, form, site):
    """Point 1 from ``<P>``: a sibling checkout, a folder below the root that is not the root, the stand-in home."""
    result = rnd.ask_form(world, P_FORMS[form], site)
    rnd.assert_refused_by_the_rule(result, f"{form} from the site '{site}'")


# The home folder as a shell spells it: ``~`` and ``$HOME`` are the stand-in home of the hook's environment.
HOME_SHELL = {
    "grep-r-with-a-tilde": "grep -r VALUE ~",
    "rg-with-the-home-variable": "rg VALUE $HOME",
    "grep-r-after-a-bare-change-of-folder": "cd && grep -r VALUE",
    "find-with-a-tilde": "find ~ -type f",
    "ls-capital-r-with-a-tilde-and-a-slash": "ls -R ~/",
}


@pytest.mark.parametrize("form", sorted(HOME_SHELL))
def test_a_search_from_the_home_folder_as_a_shell_spells_it_is_refused(world, form):
    """Point 1 on the user-level settings file: the home folder is its ``<P>``."""
    result = folders.ask_bash(world, HOME_SHELL[form], WIDEST)
    rnd.assert_refused_by_the_rule(result, f"{form} (the stand-in home)")


# --------------------------------------------------------------------------
# For every role, and what the refusal says
# --------------------------------------------------------------------------

# One form per kind, in turn: the search tool, a recursive grep, the other search program, a find.
ROLE_FORMS = {
    "Grep-with-an-absolute-path": P_FORMS["Grep-with-an-absolute-path"],
    "grep-r-absolute": P_FORMS["grep-r-absolute"],
    "rg-with-no-path-in-a-session-that-stands-there": P_FORMS["rg-with-no-path-in-a-session-that-stands-there"],
    "find-absolute": P_FORMS["find-absolute"],
}
_ROLE_FORM_NAMES = sorted(ROLE_FORMS)
BY_ROLE = [(start, who, _ROLE_FORM_NAMES[(row + column) % len(_ROLE_FORM_NAMES)])
           for row, start in enumerate(rnd.STARTS) for column, who in enumerate(rnd.OTHER_ROLES)]


@pytest.mark.parametrize("start,who,form", BY_ROLE, ids=[f"{start}-{who}-{form}" for start, who, form in BY_ROLE])
def test_a_search_with_no_path_or_glob_is_refused_for_every_role(world, start, who, form):
    """"For every role": an engineer, the test designer and a session with no role (the orchestrator is above)."""
    result = rnd.ask_form(world, ROLE_FORMS[form], start, who)
    rnd.assert_refused_by_the_rule(result, f"{form} from '{start}' by '{who}'")


@pytest.mark.parametrize("form", ("the-root-as-an-absolute-path", "a-type-filter-only-and-no-path"))
def test_a_search_tool_call_from_the_root_is_refused_for_a_role_subagent_too(world, form):
    """An engineer subagent of the orchestrator: the rule holds for every actor of a session."""
    result = rnd.ask_form(world, ROOT_TOOL[form], ROOT, "engineer-subagent-of-the-orchestrator")
    rnd.assert_refused_by_the_rule(result, f"a search tool call from the root with {form} by an engineer subagent")


SAID = [(ROOT, name) for name in rnd.FILES] + rnd.COPIES


@pytest.mark.parametrize("start,name", SAID, ids=[f"{start}-{name}" for start, name in SAID])
def test_the_refusal_of_a_search_names_the_rule_and_no_path(world, start, name):
    """A refusal names the rule and the decision: not the file, not its folder, not the start, no value of the file.

    The shell form carries the start in the command, so a refusal that echoes the command fails.
    """
    form = "grep-r-absolute"
    result = rnd.ask_form(world, P_FORMS[form], start)
    what = f"{form} from '{start}'"
    rnd.assert_refused_by_the_rule(result, what)
    rnd.assert_says_nothing(result, world, start, name, what)


# --------------------------------------------------------------------------
# What stays allowed: green before and after
# --------------------------------------------------------------------------

SOURCE_GLOBS = {"by-an-extension": "*.py", "by-an-extension-at-any-depth": "**/*.py", "a-source-folder": "src/**"}

DAILY_TOOL = {
    "a-source-folder-as-an-absolute-path-and-no-glob": _grep(path="{abs}/src"),
    "a-source-folder-as-a-relative-path-and-no-glob": _grep(path="src"),
}
for _label, _glob in SOURCE_GLOBS.items():
    DAILY_TOOL[f"the-root-as-path-and-a-glob-{_label}"] = _grep(path="{abs}", glob=_glob)
    DAILY_TOOL[f"no-path-and-a-glob-{_label}"] = _grep(glob=_glob)
    DAILY_TOOL[f"the-root-as-path-a-type-filter-and-a-glob-{_label}"] = _grep(path="{abs}", type="py", glob=_glob)
    DAILY_TOOL[f"no-path-a-type-filter-and-a-glob-{_label}"] = _grep(type="py", glob=_glob)


@pytest.mark.parametrize("form", sorted(DAILY_TOOL))
def test_a_search_tool_call_with_a_source_folder_or_a_glob_for_source_files_stays_allowed(world, form):
    """The daily forms of the search tool: a ``path`` of a source folder; the root with a glob for source files."""
    result = rnd.ask_form(world, DAILY_TOOL[form], ROOT)
    protected.assert_allowed(result, f"a search tool call with {form}")


DAILY_SHELL = {
    "grep-rn-over-two-source-folders": _sh("grep -rn VALUE src tests"),
    "rg-over-a-source-folder": _sh("rg VALUE src"),
    "find-in-a-source-folder-by-name": _sh("find src -name '*.py'"),
    "ls-capital-r-of-a-source-folder": _sh("ls -R src"),
    "git-grep-with-a-source-folder": _sh("git grep VALUE -- src"),
    "grep-in-a-named-file-without-recursion": _sh("grep VALUE README.md"),
    "ls-at-the-root": _sh("ls"),
    "ls-la-at-the-root": _sh("ls -la"),
}


@pytest.mark.parametrize("who", (WIDEST,) + rnd.OTHER_ROLES)
@pytest.mark.parametrize("form", sorted(DAILY_SHELL))
def test_the_daily_shell_forms_stay_allowed(world, form, who):
    """A search of a source folder, a named file, a listing of the root without recursion: as today, for every role."""
    result = rnd.ask_form(world, DAILY_SHELL[form], ROOT, who)
    protected.assert_allowed(result, f"the shell form '{form}' by '{who}'")


@pytest.mark.parametrize("who", rnd.OTHER_ROLES)
@pytest.mark.parametrize("form", ("a-source-folder-as-an-absolute-path-and-no-glob",
                                  "the-root-as-path-and-a-glob-by-an-extension",
                                  "no-path-and-a-glob-a-source-folder",
                                  "no-path-a-type-filter-and-a-glob-by-an-extension-at-any-depth"))
def test_the_daily_search_tool_forms_stay_allowed_for_every_role(world, form, who):
    result = rnd.ask_form(world, DAILY_TOOL[form], ROOT, who)
    protected.assert_allowed(result, f"a search tool call with {form} by '{who}'")


def _neutral_starts(world):
    """Folders under which neither file nor a copy lies."""
    return {
        "a-source-folder-of-the-session-s-project": world.project / folders.SOURCE_REL,
        "another-folder-of-the-session-s-project": world.project / folders.NEUTRAL_PARENT_REL,
        "a-source-folder-of-a-sibling-checkout": world.site("sibling").root / folders.SOURCE_REL,
        "a-work-folder-below-the-home-folder": world.sandbox.home / folders.HOME_WORK_REL,
    }


NEUTRAL = ("a-source-folder-of-the-session-s-project", "another-folder-of-the-session-s-project",
           "a-source-folder-of-a-sibling-checkout", "a-work-folder-below-the-home-folder")
# The forms held as refused from the root and from <P>, with no glob and no filter, from such a folder.
NEUTRAL_FORMS = ("Grep-with-an-absolute-path", "Grep-with-no-path-in-a-session-that-stands-there",
                 "grep-r-absolute", "grep-r-after-a-change-of-folder",
                 "grep-r-with-a-dot-in-a-session-that-stands-there", "rg-absolute",
                 "rg-with-no-path-in-a-session-that-stands-there", "find-absolute", "ls-capital-r-absolute")


def _ask_from(world, form, at, who=WIDEST):
    tool_name, template, where = form
    values = {"abs": str(at), "rel": folders.rel_from_project(world, at)}
    cwd = at if where == "start" else None
    if tool_name == "Bash":
        return folders.ask_bash(world, template.format(**values), who, cwd)
    return folders.ask(world, tool_name, {key: value.format(**values) for key, value in template.items()}, who, cwd)


@pytest.mark.parametrize("start", NEUTRAL)
@pytest.mark.parametrize("form", NEUTRAL_FORMS)
def test_a_search_with_no_glob_from_a_folder_under_which_neither_file_lies_stays_allowed(world, form, start):
    """Below the root, in a sibling checkout's source folder, below the home folder: no copy lies under the start."""
    result = _ask_from(world, P_FORMS[form], _neutral_starts(world)[start])
    protected.assert_allowed(result, f"{form} from {start}")


@pytest.mark.parametrize("who", rnd.OTHER_ROLES)
@pytest.mark.parametrize("start", NEUTRAL[:1] + NEUTRAL[2:3])
def test_a_search_with_no_glob_from_a_source_folder_stays_allowed_for_every_role(world, start, who):
    for form in ("Grep-with-an-absolute-path", "grep-r-absolute"):
        result = _ask_from(world, P_FORMS[form], _neutral_starts(world)[start], who)
        protected.assert_allowed(result, f"{form} from {start} by '{who}'")


@pytest.mark.parametrize("site", SITES)
@pytest.mark.parametrize("form", ("Grep-with-a-glob-for-source-files", "grep-rn-over-a-source-folder-of-it",
                                  "ls-without-recursion"))
def test_the_daily_forms_stay_allowed_from_a_copy_s_folder(world, form, site):
    """From ``<P>`` as from the root: a glob for source files, a folder of it that holds no copy, a plain listing."""
    forms = {
        "Grep-with-a-glob-for-source-files": _grep(path="{abs}", glob="*.py"),
        "grep-rn-over-a-source-folder-of-it": _sh("grep -rn VALUE {abs}/w1-02-source"),
        "ls-without-recursion": _sh("ls -la {abs}"),
    }
    result = rnd.ask_form(world, forms[form], site)
    protected.assert_allowed(result, f"{form} from the site '{site}'")
