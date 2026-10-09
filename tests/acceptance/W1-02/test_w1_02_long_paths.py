"""W1-02 — a very long path is answered within the bound (DEC-562, probe finding 7).

DEC-562: "The rule answers every pattern and every command in bounded time: a
pattern or a command the rule cannot answer within its bound is refused."

The fifth batch holds the bound (``w1_02_round_support.BOUND_S`` of the hook's
own time) for globs of many star pairs and for long commands. Held here, with
the same bound and the same assertions, through the hook run as a process: a
**path** of 1 MB and of 4 MB made of one short folder name repeated
(``a/a/a/…``) or of the current folder repeated (``./././…``), in the reading
tool's path, in the search tool's ``path`` (with no glob, and with a glob for
source files), in the Glob tool's ``path`` and in the Glob tool's ``pattern``
before its first wildcard.

- **The hook ends within the bound with a decision.** Such a path names no
  file a tool can open: an allow and a refusal are both acceptable.
- **A refusal within the bound** where the path, read in full, takes a
  protected file in: the current folder repeated and then a protected file's
  project-relative path, in the reading tool; the current folder repeated,
  which is the root, as the search tool's ``path`` with no glob and as the Glob
  tool's ``path`` with a pattern over everything. The refusal carries nothing
  of the path.
- **A writing tool** with such a path that, read in full, lies outside what
  the role may write: the hook ends within the bound and the call is not
  allowed. No side on the shape of the refusal.

**Before the change** (measured on stand-ins, README): a path of 1 MB of a
repeated folder name gave no answer within 35 s in any of these fields; 1 MB of
the current folder repeated took 13 to 14 s (19 to 20 s in a writing tool), with
the decision the path asks for; 4 MB gave none within 35 s. Every case of the
first three groups is red: no answer within the bound.

**What stays allowed**, green before and after: an ordinary deep path (a named
file twenty folders down, a few hundred characters) and an ordinary path with a
few ``./`` and ``../`` that resolves to a source file.

No case (README): a very long string in a field that is no path (the content of
a Write, the texts of an Edit, a field of a tool the guard does not know).

A protected file's path comes from the guard's constants, never typed, and no
id or failure message carries a path.
"""

from __future__ import annotations

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_round_support as rnd
import w1_02_support as support

MB = 1024 * 1024
SIZES = {"one-megabyte": MB, "four-megabytes": 4 * MB}
NAME = "a/"       # one short folder name
HERE = "./"       # the current folder
SOURCE_REL = "src/app/main.py"
ACCEPTANCE_REL = f"tests/acceptance/{support.TICKET_WBS_ID}/test_fixture.py"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return rnd.make_world(tmp_path_factory.mktemp("long-paths"))


def _long(unit, size):
    """``unit`` repeated to ``size`` characters: a path that ends in a slash."""
    return unit * (size // len(unit))


# --------------------------------------------------------------------------
# A decision within the bound
# --------------------------------------------------------------------------

# field -> builder(long path) -> (tool, input). The session stands in the project root.
FIELDS = {
    "the-reading-tool-s-path": lambda long: ("Read", {"file_path": long + "module.py"}),
    "the-search-tool-s-path-with-no-glob": lambda long: ("Grep", {"pattern": "VALUE", "path": long}),
    "the-search-tool-s-path-with-a-glob-for-source-files":
        lambda long: ("Grep", {"pattern": "VALUE", "path": long, "glob": "*.py"}),
    "the-Glob-tool-s-path": lambda long: ("Glob", {"pattern": "*.py", "path": long}),
    "the-Glob-tool-s-pattern-before-its-first-wildcard": lambda long: ("Glob", {"pattern": long + "*.py"}),
}
# The current folder repeated is the root: as the search tool's path with no glob it is held as refused below.
HERE_FIELDS = [field for field in sorted(FIELDS) if field != "the-search-tool-s-path-with-no-glob"]

DECIDED = [("a-repeated-folder-name", NAME, size, field) for size in SIZES for field in sorted(FIELDS)]
DECIDED += [("the-current-folder-repeated", HERE, "one-megabyte", field) for field in HERE_FIELDS]
DECIDED += [("the-current-folder-repeated", HERE, "four-megabytes", field)
            for field in ("the-reading-tool-s-path", "the-Glob-tool-s-path")]


@pytest.mark.parametrize("made_of,unit,size,field", DECIDED,
                         ids=[f"{size}-of-{made_of}-in-{field}" for made_of, _, size, field in DECIDED])
def test_a_very_long_path_is_answered_within_the_bound(world, made_of, unit, size, field):
    """Point B: read in full, none of these takes a protected file in; an allow or a refusal, in time."""
    tool_name, tool_input = FIELDS[field](_long(unit, SIZES[size]))
    result = rnd.ask_timed(world, tool_name, tool_input)
    rnd.assert_decided_in_time(result, f"{size} of {made_of} in {field}")


@pytest.mark.parametrize("who", (folders.NOT_A_WRITER, folders.NO_ROLE))
def test_a_very_long_path_is_answered_within_the_bound_for_other_roles(world, who):
    tool_name, tool_input = FIELDS["the-reading-tool-s-path"](_long(NAME, MB))
    result = rnd.ask_timed(world, tool_name, tool_input, who)
    rnd.assert_decided_in_time(result, f"one megabyte of a repeated folder name in the reading tool's path by '{who}'")


# --------------------------------------------------------------------------
# A refusal within the bound: the path, read in full, takes a protected file in
# --------------------------------------------------------------------------

READS = [("one-megabyte", name) for name in rnd.FILES] + [("four-megabytes", rnd.SETTINGS)]


@pytest.mark.parametrize("size,name", READS, ids=[f"{size}-then-the-{name}" for size, name in READS])
def test_the_current_folder_repeated_and_then_a_protected_file_is_refused_within_the_bound(world, size, name):
    """Point B: length buys no read; the refusal carries nothing of the path."""
    long = _long(HERE, SIZES[size])
    result = rnd.ask_timed(world, "Read", {"file_path": long + protected.PROTECTED[name]})
    what = f"the reading tool on {size} of the current folder repeated and then the stand-in {name}"
    rnd.assert_refused_in_time(result, what)
    rnd.assert_carries_none_of(result, world.secrets("own", name) + (HERE * 32,), what)


# The current folder repeated is the root: nothing keeps either file out of these.
ROOT_SEARCHES = {
    "the-search-tool-s-path-with-no-glob": lambda long: ("Grep", {"pattern": "VALUE", "path": long}),
    "the-Glob-tool-s-path-with-a-pattern-over-everything": lambda long: ("Glob", {"pattern": "**/*", "path": long}),
}
SEARCHED = [("one-megabyte", field) for field in sorted(ROOT_SEARCHES)]
SEARCHED += [("four-megabytes", "the-search-tool-s-path-with-no-glob")]


@pytest.mark.parametrize("size,field", SEARCHED, ids=[f"{size}-in-{field}" for size, field in SEARCHED])
def test_the_current_folder_repeated_as_the_start_of_a_search_is_refused_within_the_bound(world, size, field):
    """Point B: a search from the root with no path below it and no glob for source files, however it is spelled."""
    tool_name, tool_input = ROOT_SEARCHES[field](_long(HERE, SIZES[size]))
    result = rnd.ask_timed(world, tool_name, tool_input)
    what = f"{size} of the current folder repeated in {field}"
    rnd.assert_refused_in_time(result, what)
    for name in rnd.FILES:
        rnd.assert_carries_none_of(result, world.secrets("own", name) + (HERE * 32,), what)


# --------------------------------------------------------------------------
# A writing tool: within the bound, and not allowed outside what the role may write
# --------------------------------------------------------------------------

WRITES = [("one-megabyte", "Write"), ("one-megabyte", "Edit"), ("four-megabytes", "Write")]


@pytest.mark.parametrize("size,tool_name", WRITES, ids=[f"{size}-{tool_name}" for size, tool_name in WRITES])
def test_a_writing_tool_with_a_very_long_path_outside_the_role_s_paths_is_not_allowed_within_the_bound(
        world, size, tool_name):
    """An engineer, the current folder repeated and then a file under the acceptance tests: no side on the shape."""
    path = _long(HERE, SIZES[size]) + ACCEPTANCE_REL
    result = rnd.ask_timed(world, tool_name, support.edit_tool_input(tool_name, path), folders.NOT_A_WRITER)
    rnd.assert_refused_in_time(
        result, f"{tool_name} by an engineer on {size} of the current folder repeated and then an acceptance test")


# --------------------------------------------------------------------------
# What stays allowed: green before and after
# --------------------------------------------------------------------------

DEEP_REL = "src/" + "/".join(f"folder{level:02}" for level in range(20))

ORDINARY = {
    "the-reading-tool-on-a-named-file-twenty-folders-down":
        lambda w: ("Read", {"file_path": f"{w.project}/{DEEP_REL}/module.py"}),
    "the-search-tool-with-a-path-twenty-folders-down":
        lambda w: ("Grep", {"pattern": "VALUE", "path": f"{w.project}/{DEEP_REL}"}),
    "the-reading-tool-on-a-path-with-dots-that-resolves-to-a-source-file":
        lambda w: ("Read", {"file_path": "./src/app/../gov/./guard/../../app/main.py"}),
    "the-search-tool-with-a-path-with-dots-that-resolves-to-a-source-folder":
        lambda w: ("Grep", {"pattern": "VALUE", "path": "./src/../src/./app"}),
}
ORDINARY_BY = [(shape, rnd.WIDEST) for shape in sorted(ORDINARY)]
ORDINARY_BY += [(shape, folders.NO_ROLE) for shape in sorted(ORDINARY) if shape.startswith("the-reading-tool")]


@pytest.mark.parametrize("shape,who", ORDINARY_BY, ids=[f"{shape}-by-{who}" for shape, who in ORDINARY_BY])
def test_an_ordinary_deep_path_and_an_ordinary_path_with_dots_stay_allowed_within_the_bound(world, shape, who):
    """As today: allowed, and answered within the same bound."""
    tool_name, tool_input = ORDINARY[shape](world)
    result = rnd.ask_timed(world, tool_name, tool_input, who)
    rnd.assert_allowed_in_time(result, f"'{shape}' by '{who}'")
