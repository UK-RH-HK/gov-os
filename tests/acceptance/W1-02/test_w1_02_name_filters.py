"""W1-02 — a shell search whose name filter names or matches a protected file is refused (DEC-562, probe finding 1).

DEC-562: "A search in the shell from the project root, or from a copy's folder,
whose name filter names either file's name or matches it (``--include``, the
other search program's glob option in each spelling) is refused, as the same
search through the search tool with that glob is."

Held here, on stand-in files: from the root and from the folder ``<P>`` a copy
lies under (no path, or the root or ``<P>`` as the path), a recursive ``grep``
with ``--include`` (``=`` and the filter as the next word) and ``rg`` with its
glob option (the short option with the filter as the next word and glued to
it, the long option with ``=`` and with the filter as the next word, and its
case-insensitive twin). The filters: the file's own name, a pattern by its
extension, a pattern that matches its name in part, a pattern over everything.
With several filters, one that matches is enough. A filter that only excludes
narrows nothing: such a search is refused as a search with no filter is
(DEC-557).

**Before the change the guard allows every one of these** (found by running the
hook, README): all the refusal cases are red.

**What stays allowed**, green before and after: the same searches with a filter
that cannot match either file, and a filter that names a protected file's name
in a search whose path is a source folder below which neither file nor a copy
lies.

A filter may be the held-out file's own name: it is computed from the guard's
constant, never typed, and no id or failure message carries it.
"""

from __future__ import annotations

import os

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_round_support as rnd

ROOT = rnd.ROOT
WIDEST = rnd.WIDEST
FILES = rnd.FILES


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return rnd.make_world(tmp_path_factory.mktemp("name-filters"))


def _base(name):
    return os.path.basename(protected.PROTECTED[name])


# The filters that take a file in: label -> the filter for the file ``name``.
FILTERS = {
    "its-own-name": _base,
    "its-extension": lambda name: "*" + os.path.splitext(_base(name))[1],
    "a-part-of-its-name": lambda name: _base(name)[:4] + "*",
    "everything": lambda name: "*",
}


def _sh(command, where=None):
    return ("Bash", command, where)


# Each spelling of a name filter, from the start with a dot as the path or with no path.
SPELLINGS = {
    "grep-include-with-an-equals-sign": _sh("grep -rn VALUE --include={f} .", "start"),
    "grep-include-quoted": _sh("grep -rn VALUE --include='{f}' .", "start"),
    "grep-include-with-the-filter-as-the-next-word": _sh("grep -rn VALUE --include '{f}' .", "start"),
    "grep-include-and-no-path": _sh("grep -rn --include='{f}' VALUE", "start"),
    "rg-short-option-with-the-filter-as-the-next-word": _sh("rg VALUE -g '{f}'", "start"),
    "rg-short-option-with-the-filter-glued-to-it": _sh("rg VALUE -g'{f}'", "start"),
    "rg-long-option-with-an-equals-sign": _sh("rg VALUE --glob='{f}'", "start"),
    "rg-long-option-with-the-filter-as-the-next-word": _sh("rg --glob '{f}' VALUE .", "start"),
    "rg-case-insensitive-option-with-an-equals-sign": _sh("rg VALUE --iglob='{f}'", "start"),
    "rg-case-insensitive-option-with-the-filter-as-the-next-word": _sh("rg VALUE --iglob '{f}'", "start"),
}


# --------------------------------------------------------------------------
# Refused from the root
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("filter_", sorted(FILTERS))
@pytest.mark.parametrize("spelling", sorted(SPELLINGS))
def test_a_shell_search_from_the_root_whose_name_filter_takes_a_protected_file_in_is_refused(world, spelling,
                                                                                            filter_, name):
    """Point 2: each spelling of the filter, each filter, each file; the session stands in the root."""
    result = rnd.ask_form(world, SPELLINGS[spelling], ROOT, f=FILTERS[filter_](name))
    rnd.assert_refused_by_the_rule(
        result, f"{spelling} from the root with a filter for the stand-in {name} ({filter_})")


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("spelling", ("rg-case-insensitive-option-with-an-equals-sign",
                                      "rg-case-insensitive-option-with-the-filter-as-the-next-word"))
def test_a_case_insensitive_filter_in_another_case_takes_the_file_in(world, spelling, name):
    """Point 2: the case-insensitive twin matches the file's name whatever the case of the filter."""
    result = rnd.ask_form(world, SPELLINGS[spelling], ROOT, f=_base(name).upper())
    rnd.assert_refused_by_the_rule(
        result, f"{spelling} from the root with the name of the stand-in {name} in capitals")


ROOT_PATHS = {
    "grep-include-with-the-absolute-root": _sh("grep -rn VALUE --include='{f}' {abs}"),
    "rg-glob-with-the-absolute-root": _sh("rg VALUE -g '{f}' {abs}"),
    "grep-include-after-a-change-to-the-root": _sh("cd {abs} && grep -rn VALUE --include='{f}'", "below"),
    "rg-glob-with-two-dots-from-one-folder-below": _sh("rg VALUE --glob='{f}' ..", "below"),
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(ROOT_PATHS))
def test_the_root_as_the_search_s_path_in_another_spelling_is_refused(world, form, name):
    """Point 2: "no path, or the root as the path": absolute, after a change of folder, relative."""
    result = rnd.ask_form(world, ROOT_PATHS[form], ROOT, f=_base(name))
    rnd.assert_refused_by_the_rule(result, f"{form} with the name of the stand-in {name}")


SEVERAL = {
    "grep-a-source-filter-then-the-file-s": _sh("grep -rn VALUE --include='*.py' --include='{f}' .", "start"),
    "grep-the-file-s-then-a-source-filter": _sh("grep -rn VALUE --include='{f}' --include='*.py' .", "start"),
    "rg-a-source-filter-then-the-file-s": _sh("rg -g '*.py' -g '{f}' VALUE", "start"),
    "rg-the-file-s-then-an-excluding-filter": _sh("rg VALUE --glob='{f}' --glob='!*.md'", "start"),
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(SEVERAL))
def test_with_several_filters_one_that_matches_is_enough(world, form, name):
    result = rnd.ask_form(world, SEVERAL[form], ROOT, f=_base(name))
    rnd.assert_refused_by_the_rule(result, f"{form} from the root, for the stand-in {name}")


# --------------------------------------------------------------------------
# Refused from a copy's <P>
# --------------------------------------------------------------------------

P_FORMS = {
    "grep-include-absolute": _sh("grep -rn VALUE --include='{f}' {abs}"),
    "grep-include-relative": _sh("grep -rn VALUE --include={f} {rel}"),
    "rg-glob-after-a-change-of-folder": _sh("cd {abs} && rg VALUE -g '{f}'"),
    "rg-long-glob-in-a-session-that-stands-there": _sh("rg VALUE --glob='{f}'", "start"),
}


@pytest.mark.parametrize("site,name", rnd.COPIES, ids=rnd.COPY_IDS)
@pytest.mark.parametrize("filter_", ("its-own-name", "its-extension"))
@pytest.mark.parametrize("form", sorted(P_FORMS))
def test_a_shell_search_from_a_copy_s_folder_whose_name_filter_takes_the_copy_in_is_refused(world, form, filter_,
                                                                                           site, name):
    """Point 2 from ``<P>``: a sibling checkout, a folder below the root that is not the root, the stand-in home."""
    result = rnd.ask_form(world, P_FORMS[form], site, f=FILTERS[filter_](name))
    rnd.assert_refused_by_the_rule(
        result, f"{form} from the site '{site}' with a filter for the copy of the stand-in {name} ({filter_})")


HOME_SHELL = {
    "grep-include-with-a-tilde": "grep -rn VALUE --include='{f}' ~",
    "rg-glob-with-the-home-variable": "rg VALUE -g '{f}' $HOME",
    "rg-glob-after-a-bare-change-of-folder": "cd && rg VALUE --glob='{f}'",
}


@pytest.mark.parametrize("filter_", ("its-own-name", "its-extension"))
@pytest.mark.parametrize("form", sorted(HOME_SHELL))
def test_a_name_filter_for_the_user_level_settings_file_from_the_home_folder_is_refused(world, form, filter_):
    """``~``, ``$HOME`` and a bare ``cd`` name the stand-in home of the hook's environment."""
    command = HOME_SHELL[form].format(f=FILTERS[filter_](rnd.SETTINGS))
    result = folders.ask_bash(world, command, WIDEST)
    rnd.assert_refused_by_the_rule(result, f"{form} with a filter for the settings file ({filter_})")


# --------------------------------------------------------------------------
# A filter that only excludes narrows nothing (refused under point 1)
# --------------------------------------------------------------------------

EXCLUDING = {
    "grep-exclude": _sh("grep -rn VALUE --exclude='*.md' .", "start"),
    "grep-exclude-dir": _sh("grep -rn VALUE --exclude-dir=docs .", "start"),
    "rg-an-excluding-glob": _sh("rg VALUE -g '!*.md'", "start"),
    "rg-an-excluding-long-glob-with-a-dot": _sh("rg VALUE --glob='!*.md' .", "start"),
}


@pytest.mark.parametrize("start", (ROOT, "sibling"))
@pytest.mark.parametrize("form", sorted(EXCLUDING))
def test_a_search_whose_only_filter_excludes_is_refused_as_a_search_with_no_filter(world, form, start):
    result = rnd.ask_form(world, EXCLUDING[form], start)
    rnd.assert_refused_by_the_rule(result, f"{form} from '{start}'")


# --------------------------------------------------------------------------
# For every role, and what the refusal says
# --------------------------------------------------------------------------

_ROLE_SPELLINGS = ("grep-include-quoted", "rg-short-option-with-the-filter-as-the-next-word",
                   "rg-long-option-with-an-equals-sign")
BY_ROLE = [(start, who, _ROLE_SPELLINGS[(row + column) % len(_ROLE_SPELLINGS)],
            rnd.files_under(start)[(row + column) % len(rnd.files_under(start))])
           for row, start in enumerate((ROOT, "sibling", "home")) for column, who in enumerate(rnd.OTHER_ROLES)]


@pytest.mark.parametrize("start,who,spelling,name", BY_ROLE,
                         ids=[f"{start}-{who}-{spelling}-{name}" for start, who, spelling, name in BY_ROLE])
def test_a_name_filter_that_takes_a_protected_file_in_is_refused_for_every_role(world, start, who, spelling, name):
    """"For every role": an engineer, the test designer and a session with no role (the orchestrator is above)."""
    result = rnd.ask_form(world, SPELLINGS[spelling], start, who, f=_base(name))
    rnd.assert_refused_by_the_rule(result, f"{spelling} from '{start}' by '{who}', for the stand-in {name}")


SAID = [(ROOT, name) for name in FILES] + [("sibling", name) for name in FILES] + [("home", rnd.SETTINGS)]


@pytest.mark.parametrize("start,name", SAID, ids=[f"{start}-{name}" for start, name in SAID])
def test_the_refusal_of_a_name_filter_names_the_rule_and_neither_the_file_nor_the_start(world, start, name):
    """A refusal names the rule and the decision: no path, not the start, no value of the file.

    The command carries the start and, as its filter, the file's own name: a refusal that echoes the command fails.
    """
    form = "grep-include-absolute"
    result = rnd.ask_form(world, P_FORMS[form], start, f=_base(name))
    what = f"{form} from '{start}' with the name of the stand-in {name}"
    rnd.assert_refused_by_the_rule(result, what)
    rnd.assert_says_nothing(result, world, start, name, what, more=(f"--include='{_base(name)}'",))


# --------------------------------------------------------------------------
# What stays allowed: green before and after
# --------------------------------------------------------------------------

SOURCE_FILTER = {
    "grep-include-quoted-with-a-dot": _sh("grep -rn VALUE --include='*.py' .", "start"),
    "grep-include-and-no-path": _sh("grep -rn VALUE --include=*.py", "start"),
    "grep-include-with-the-filter-as-the-next-word": _sh("grep -rn VALUE --include '*.py' .", "start"),
    "rg-short-option-with-the-filter-as-the-next-word": _sh("rg VALUE -g '*.py'", "start"),
    "rg-short-option-with-the-filter-glued-to-it": _sh("rg VALUE -g'*.py'", "start"),
    "rg-long-option-with-an-equals-sign": _sh("rg VALUE --glob='*.py'", "start"),
    "rg-long-option-with-the-filter-as-the-next-word": _sh("rg --glob '*.py' VALUE .", "start"),
    "rg-case-insensitive-option": _sh("rg VALUE --iglob '*.py'", "start"),
    "rg-a-source-filter-and-an-excluding-one": _sh("rg VALUE -g '*.py' -g '!test_*'", "start"),
    "grep-include-with-the-start-as-an-absolute-path": _sh("grep -rn VALUE --include='*.py' {abs}"),
    "rg-glob-after-a-change-of-folder": _sh("cd {abs} && rg VALUE -g '*.py'"),
}


@pytest.mark.parametrize("start", rnd.STARTS)
@pytest.mark.parametrize("form", sorted(SOURCE_FILTER))
def test_a_search_with_a_filter_that_cannot_match_either_file_stays_allowed(world, form, start):
    """From the root and from each ``<P>``: a filter for source files keeps both files out."""
    at = world.site(rnd.site_of(start))
    assert all(at.ext(name) != ".py" for name in at.names), (
        "the stand-in filter of this case would match one of the two files; choose another")
    result = rnd.ask_form(world, SOURCE_FILTER[form], start)
    protected.assert_allowed(result, f"{form} from '{start}'")


@pytest.mark.parametrize("who", rnd.OTHER_ROLES)
@pytest.mark.parametrize("form", ("grep-include-quoted-with-a-dot", "rg-short-option-with-the-filter-as-the-next-word"))
def test_a_search_from_the_root_with_a_source_filter_stays_allowed_for_every_role(world, form, who):
    result = rnd.ask_form(world, SOURCE_FILTER[form], ROOT, who)
    protected.assert_allowed(result, f"{form} from the root by '{who}'")


def _neutral_starts(world):
    """Source folders below which neither file nor a copy lies."""
    return {
        "a-source-folder-of-the-session-s-project": world.project / folders.SOURCE_REL,
        "a-source-folder-of-a-sibling-checkout": world.site("sibling").root / folders.SOURCE_REL,
    }


NAMED_IN_A_SOURCE_FOLDER = {
    "grep-include": "grep -rn VALUE --include='{f}' {abs}",
    "rg-short-glob": "rg VALUE -g '{f}' {abs}",
    "rg-long-glob": "rg VALUE --glob='{f}' {abs}",
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("filter_", ("its-own-name", "its-extension"))
@pytest.mark.parametrize("start", ("a-source-folder-of-the-session-s-project", "a-source-folder-of-a-sibling-checkout"))
@pytest.mark.parametrize("form", sorted(NAMED_IN_A_SOURCE_FOLDER))
def test_a_filter_that_names_a_protected_file_in_a_search_of_a_source_folder_stays_allowed(world, form, start,
                                                                                          filter_, name):
    """The filter names the file, the search cannot reach it: neither file nor a copy lies below the path."""
    command = NAMED_IN_A_SOURCE_FOLDER[form].format(f=FILTERS[filter_](name), abs=_neutral_starts(world)[start])
    result = folders.ask_bash(world, command, WIDEST)
    protected.assert_allowed(result, f"{form} over {start} with a filter for the stand-in {name} ({filter_})")


@pytest.mark.parametrize("name", FILES)
def test_such_a_search_of_a_source_folder_by_its_relative_path_stays_allowed(world, name):
    """``grep -rn <word> --include=<the file's name> src`` from the root, by a session with no role."""
    command = f"grep -rn VALUE --include='{_base(name)}' src"
    result = folders.ask_bash(world, command, folders.NO_ROLE)
    protected.assert_allowed(result, f"grep with the name of the stand-in {name} as its filter over a source folder")
