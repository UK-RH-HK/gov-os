"""W1-02 — a glob made of wildcards alone from a copy's folder is refused as from the session's root (DEC-553, DP-6).

DEC-553: "A glob made of wildcards alone from the folder a copy lies under is
refused as the same glob from the session's own root is: the two no longer
differ."

A copy is an existing file at ``<P>/<the file's project-relative path>``. A
glob of wildcards alone is stars and slashes and nothing that names a file.

**What the guard refuses from the session's own root today** (found by running
the hook, README): such a glob is refused when it reaches the depth where one
of the two files lies: the patterns over everything (``**``, ``**/*``,
``*/**``) and the pattern over every file at the file's depth (one star per
level). It is refused in the Glob tool (with a ``path``, with none when the
session stands in the folder, and as one pattern with the folder in front), in
the Grep tool as its ``glob`` (the same three starts, and with a slash in
front), and in a shell word after ``cat``, ``grep`` and ``ls`` (absolute,
relative, after ``cd``). In the Grep tool a single star is a name at any depth
and is refused too.

**What is allowed from the session's own root today, and so from ``<P>``:**
a single star in the Glob tool and in a shell word (one level, where neither
file lies), and a pattern with more levels than the file has. Those stay
allowed from ``<P>`` (held below for the single star).

Before the change every one of these globs is allowed from ``<P>``: red. The
exception is a Grep glob over everything with a slash in front, which is
refused from ``<P>`` already: green today, and held.

No case starts above ``<P>`` and none searches with no glob at all: both are
with the owner (DP-1). No case needs the guard to walk a tree: the start of
every glob is ``<P>`` itself.
"""

from __future__ import annotations

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected

SETTINGS = folders.SETTINGS
FILES = folders.FILES
WIDEST = folders.ORCHESTRATOR
EVERYTHING = "**/*"
OTHER_EVERYTHING = ("**", "*/**")

# The sites <P> and the copies under each: a sibling checkout outside the session's project, a folder below the
# session's root that is not the root, and the stand-in home (the settings file only).
COPIES = [("sibling", name) for name in FILES] + [("nested", name) for name in FILES] + [("home", SETTINGS)]
COPY_IDS = [f"{site}-{name}" for site, name in COPIES]
SITES = ("sibling", "nested", "home")


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return folders.make_world(tmp_path_factory.mktemp("wildcard-globs"))


# form -> (tool, input, working folder) for the start ``{abs}`` (absolute), ``{rel}`` (relative from the session's
# project) and the glob ``{pat}``. The working folder is the session's project (None) or the start ("start").
FORMS = {
    "Glob-with-an-absolute-path": ("Glob", {"pattern": "{pat}", "path": "{abs}"}, None),
    "Glob-with-a-relative-path": ("Glob", {"pattern": "{pat}", "path": "{rel}"}, None),
    "Glob-with-no-path-in-a-session-that-stands-there": ("Glob", {"pattern": "{pat}"}, "start"),
    "Glob-absolute-pattern": ("Glob", {"pattern": "{abs}/{pat}"}, None),
    "Glob-relative-pattern": ("Glob", {"pattern": "{rel}/{pat}"}, None),
    "Grep-with-an-absolute-path": ("Grep", {"pattern": ".", "path": "{abs}", "glob": "{pat}"}, None),
    "Grep-with-a-relative-path": ("Grep", {"pattern": ".", "path": "{rel}", "glob": "{pat}"}, None),
    "Grep-with-no-path-in-a-session-that-stands-there": ("Grep", {"pattern": ".", "glob": "{pat}"}, "start"),
    "cat-absolute": ("Bash", "cat {abs}/{pat}", None),
    "cat-relative": ("Bash", "cat {rel}/{pat}", None),
    "cat-in-a-session-that-stands-there": ("Bash", "cat {pat}", "start"),
    "cat-after-a-change-of-folder": ("Bash", "cd {abs} && cat {pat}", None),
    "grep-absolute": ("Bash", "grep -c VALUE {abs}/{pat}", None),
    "ls-absolute": ("Bash", "ls -d {abs}/{pat}", None),
}
GREP_FORMS = tuple(sorted(form for form in FORMS if form.startswith("Grep")))
CORE = ("Glob-with-an-absolute-path", "Glob-absolute-pattern", "Grep-with-an-absolute-path", "cat-absolute")
# The home folder as a shell spells it: ``~`` and ``$HOME`` are the stand-in home of the hook's environment.
HOME_FORMS = {
    "cat-with-a-tilde": "cat ~/{pat}",
    "cat-with-the-home-variable": "cat $HOME/{pat}",
    "ls-with-a-tilde": "ls -d ~/{pat}",
    "cat-after-a-bare-change-of-folder": "cd && cat {pat}",
}


def _ask(world, start, form, pattern, who=WIDEST):
    """One call in ``form`` with the glob ``pattern`` from the folder ``start``."""
    tool_name, template, where = FORMS[form] if isinstance(form, str) else form
    values = {"abs": str(start), "rel": folders.rel_from_project(world, start), "pat": pattern}
    cwd = start if where == "start" else None
    if tool_name == "Bash":
        return folders.ask_bash(world, template.format(**values), who, cwd)
    return folders.ask(world, tool_name, {key: value.format(**values) for key, value in template.items()}, who, cwd)


# --------------------------------------------------------------------------
# Refused from <P>: every tool form the root refuses
# --------------------------------------------------------------------------

@pytest.mark.parametrize("site", SITES)
@pytest.mark.parametrize("form", sorted(FORMS))
def test_a_glob_over_everything_from_a_copy_s_folder_is_refused(world, form, site):
    """DP-6: the pattern over everything, in each tool form, from each ``<P>``; relative and absolute starts."""
    result = _ask(world, world.site(site).root, form, EVERYTHING)
    folders.assert_refused_by_the_rule(result, f"{form} with a glob over everything from the site '{site}'")


@pytest.mark.parametrize("site,name", COPIES, ids=COPY_IDS)
@pytest.mark.parametrize("form", CORE)
def test_a_glob_over_every_file_at_the_copy_s_depth_is_refused(world, form, site, name):
    """DP-6: one star per level down to where the copy lies: it names no file and takes the copy in."""
    result = _ask(world, world.site(site).root, form, folders.depth_glob(name))
    folders.assert_refused_by_the_rule(
        result, f"{form} with one star per level of the stand-in {name} from the site '{site}'")


@pytest.mark.parametrize("pattern", OTHER_EVERYTHING, ids=("two-stars", "a-star-then-two-stars"))
@pytest.mark.parametrize("form", ("Glob-with-an-absolute-path", "Grep-with-an-absolute-path", "cat-absolute"))
def test_the_other_globs_over_everything_are_refused(world, form, pattern):
    """DP-6: the other spellings of "everything" the root refuses, from a sibling checkout."""
    result = _ask(world, world.site("sibling").root, form, pattern)
    folders.assert_refused_by_the_rule(result, f"{form} with another glob over everything from another checkout")


@pytest.mark.parametrize("site", SITES)
@pytest.mark.parametrize("form", GREP_FORMS)
def test_a_search_whose_glob_is_a_single_star_is_refused(world, form, site):
    """DP-6: in the search tool a glob with no slash is a name at any depth; the root refuses a single star."""
    result = _ask(world, world.site(site).root, form, "*")
    folders.assert_refused_by_the_rule(result, f"{form} with a single star as its glob from the site '{site}'")


@pytest.mark.parametrize("site,name", COPIES, ids=COPY_IDS)
def test_a_search_whose_glob_starts_with_a_slash_is_refused(world, site, name):
    """DP-6: a glob with a slash in front is read from the search's folder; one star per level of the copy."""
    result = _ask(world, world.site(site).root, "Grep-with-an-absolute-path", "/" + folders.depth_glob(name))
    folders.assert_refused_by_the_rule(
        result, f"Grep with a slash and one star per level of the stand-in {name} from the site '{site}'")


@pytest.mark.parametrize("site", SITES)
def test_a_search_over_everything_with_a_slash_in_front_is_still_refused(world, site):
    """Refused from ``<P>`` before DEC-553 already (green today), and held."""
    result = _ask(world, world.site(site).root, "Grep-with-an-absolute-path", "/" + EVERYTHING)
    folders.assert_refused_by_the_rule(result, f"Grep with a slash and a glob over everything from the site '{site}'")


@pytest.mark.parametrize("pattern", ("everything", "depth"))
@pytest.mark.parametrize("form", sorted(HOME_FORMS))
def test_a_wildcard_only_glob_from_the_home_folder_as_a_shell_spells_it_is_refused(world, form, pattern):
    """DP-6 on the user-level settings file: ``~``, ``$HOME`` and a bare ``cd`` name the stand-in home."""
    glob = EVERYTHING if pattern == "everything" else folders.depth_glob(SETTINGS)
    result = folders.ask_bash(world, HOME_FORMS[form].format(pat=glob), WIDEST)
    folders.assert_refused_by_the_rule(result, f"{form} with a wildcard-only glob ({pattern}) from the stand-in home")


# --------------------------------------------------------------------------
# For every role, and what the refusal says
# --------------------------------------------------------------------------

OTHER_ROLES = (folders.NOT_A_WRITER, folders.NO_ROLE, "test-designer")
# Each other role at each site, the Glob tool and the shell word in turn.
BY_ROLE = [(site, who, ("Glob-with-an-absolute-path", "cat-absolute")[(row + column) % 2])
           for row, site in enumerate(SITES) for column, who in enumerate(OTHER_ROLES)]


@pytest.mark.parametrize("site,who,form", BY_ROLE, ids=[f"{site}-{who}-{form}" for site, who, form in BY_ROLE])
def test_a_wildcard_only_glob_from_a_copy_s_folder_is_refused_for_every_role(world, site, who, form):
    """DP-6: "for every role": an engineer, a session with no role, the test designer (the orchestrator is above)."""
    result = _ask(world, world.site(site).root, form, EVERYTHING, who)
    folders.assert_refused_by_the_rule(result, f"{form} with a glob over everything from the site '{site}' by '{who}'")


@pytest.mark.parametrize("site,name", COPIES, ids=COPY_IDS)
def test_the_refusal_of_a_wildcard_only_glob_names_neither_the_copy_nor_its_folder(world, site, name):
    """A refusal names the rule and the decision: not the copy, not its folder, not ``<P>``, no value of the file.

    The shell form carries ``<P>`` in the command, so a refusal that echoes the command fails.
    """
    form = "cat-absolute"
    result = _ask(world, world.site(site).root, form, folders.depth_glob(name))
    what = f"{form} with one star per level of the stand-in {name} from the site '{site}'"
    folders.assert_refused_by_the_rule(result, what)
    folders.assert_says_nothing(result, world, site, name, what)


# --------------------------------------------------------------------------
# What stays allowed: green before and after
# --------------------------------------------------------------------------

def _neutral_starts(world):
    """Folders under which no copy lies."""
    return {
        "a-source-folder-of-the-session-s-project": world.project / folders.SOURCE_REL,
        "a-source-folder-of-a-sibling-checkout": world.site("sibling").root / folders.SOURCE_REL,
        "a-work-folder-below-the-home-folder": world.sandbox.home / folders.HOME_WORK_REL,
    }


NEUTRAL = ("a-source-folder-of-the-session-s-project", "a-source-folder-of-a-sibling-checkout",
           "a-work-folder-below-the-home-folder")


@pytest.mark.parametrize("form", sorted(FORMS))
def test_a_glob_over_everything_from_a_source_folder_of_the_project_stays_allowed(world, form):
    """Each tool form held as refused from ``<P>``, from a folder of the session's project that holds no copy."""
    result = _ask(world, _neutral_starts(world)[NEUTRAL[0]], form, EVERYTHING)
    protected.assert_allowed(result, f"{form} with a glob over everything from {NEUTRAL[0]}")


@pytest.mark.parametrize("start", NEUTRAL[1:])
@pytest.mark.parametrize("form", CORE + ("Glob-with-no-path-in-a-session-that-stands-there",
                                         "Grep-with-no-path-in-a-session-that-stands-there",
                                         "cat-after-a-change-of-folder"))
def test_a_glob_over_everything_from_a_folder_outside_under_which_no_copy_lies_stays_allowed(world, form, start):
    """A folder of a sibling checkout below which neither file lies; a folder below the home that is not the home."""
    result = _ask(world, _neutral_starts(world)[start], form, EVERYTHING)
    protected.assert_allowed(result, f"{form} with a glob over everything from {start}")


@pytest.mark.parametrize("start", NEUTRAL)
@pytest.mark.parametrize("pattern", ("*/*", "**"))
@pytest.mark.parametrize("form", ("Glob-with-an-absolute-path", "Grep-with-an-absolute-path", "cat-absolute"))
def test_the_other_wildcard_only_globs_from_such_a_folder_stay_allowed(world, form, pattern, start):
    result = _ask(world, _neutral_starts(world)[start], form, pattern)
    protected.assert_allowed(result, f"{form} with the glob {pattern} from {start}")


# A glob from <P> that selects other files: by an extension neither file has, by another file's name.
BY_NAME = {
    "Glob-by-an-extension": ("Glob", {"pattern": "**/*.py", "path": "{abs}"}, None),
    "Glob-by-another-file-s-name": ("Glob", {"pattern": "**/README.md", "path": "{abs}"}, None),
    "Grep-by-an-extension": ("Grep", {"pattern": "VALUE", "path": "{abs}", "glob": "*.py"}, None),
    "cat-by-an-extension": ("Bash", "cat {abs}/**/*.py", None),
    "ls-of-a-folder-s-files-by-name": ("Bash", "ls {abs}/src/*.py", None),
}


@pytest.mark.parametrize("site", SITES)
@pytest.mark.parametrize("form", sorted(BY_NAME))
def test_a_glob_from_a_copy_s_folder_that_selects_other_files_stays_allowed(world, form, site):
    """A glob that names what it wants is no glob of wildcards alone, and it matches neither file."""
    at = world.site(site)
    assert all(at.ext(name) != ".py" and at.base(name) != "README.md" for name in at.names), (
        "the stand-in pattern of this case would match one of the two files; choose another")
    result = _ask(world, at.root, BY_NAME[form], "")
    protected.assert_allowed(result, f"{form} from the site '{site}'")


# Allowed from the session's own root today (a single level, where neither file lies), and so from <P>.
ONE_LEVEL = ("Glob-with-an-absolute-path", "cat-absolute")


@pytest.mark.parametrize("site", ("own",) + SITES)
@pytest.mark.parametrize("form", ONE_LEVEL)
def test_a_single_star_stays_allowed_from_the_root_and_from_a_copy_s_folder(world, form, site):
    """DP-6 makes ``<P>`` as strict as the root and no stricter: what the root allows, ``<P>`` allows."""
    result = _ask(world, world.site(site).root, form, "*")
    protected.assert_allowed(result, f"{form} with a single star from the site '{site}'")
