"""W1-02 — every input under the round's length bounds is decided within the bound (DEC-570).

DEC-570: "The harness lets a call through when the hook passes its time limit
(DEC-110, DEC-179), so a slow decision fails open. [...] The rule's work is
bounded by count times length, or the input is refused; the test designer
states the bound as a time with a wide margin for a loaded machine."

**The bound** is the fifth batch's, unchanged: the hook ends with a decision
within ``w1_02_round_support.BOUND_S`` of its own time, start to exit; a case
stops the process at ``PROCESS_LIMIT_S`` and fails. The bound is generous for a
loaded machine: the engineer is told to answer each of these inputs in well
under a second.

Every input here is under the round's length bounds: a command of at most 32768
characters, a path or a glob of at most 4096 (``test_every_input_is_under_the_
round_s_length_bounds`` holds that of the inputs themselves). Held, through the
hook run as a process:

- **the reviewer's thirteen inputs**, each decided in time: an allow or a
  refusal, never a hook error, never the limit. Measured on the guard as built
  (README): seven of them get no answer within the bound and are red; six are
  answered within it today and are green, and held;
- **the new forms of this round at the length bound**, each decided in time:
  green today (the guard does not judge them yet); they hold the code to come;
- **where such an input takes a protected file in, it is refused in time**;
- **ordinary sizes stay allowed in time.**

No id and no failure message carries a command, a path or a filter.
"""

from __future__ import annotations

import pytest

import w1_02_copies_support as batch
import w1_02_folders_support as folders
import w1_02_fix_support as fix
import w1_02_protected_support as protected
import w1_02_round_support as rnd
import w1_02_support as support

PROG = fix.PROG
MOST_COMMAND = 32768     # the round's bound on a command, in characters
MOST_PATH = 4096         # the round's bound on a path or a glob of a file tool
NEAR = 32000             # "about 32000 characters": the size the new forms are built to
FOLDERS = "a/"           # one short folder name
BRACES_8 = "{a,b}" * 8   # a brace word of 256 expansions
BRACES_4 = "{a,b}" * 4   # of 16


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return fix.make_world(tmp_path_factory.mktemp("fix-round-time"))


def _bash(command):
    return ("Bash", support.bash_tool_input(command))


def _repeat(unit, size=NEAR):
    """``unit`` repeated to about ``size`` characters."""
    return unit * (size // len(unit))


# --------------------------------------------------------------------------
# The reviewer's thirteen inputs
# --------------------------------------------------------------------------

THIRTEEN = {
    "01-Grep-a-path-of-2047-folders-and-a-glob-of-2047-words":
        lambda: ("Grep", {"pattern": "VALUE", "path": FOLDERS * 2047, "glob": "x " * 2047}),
    "02-Grep-a-path-of-1000-folders-and-a-glob-of-500-words":
        lambda: ("Grep", {"pattern": "VALUE", "path": FOLDERS * 1000, "glob": "x " * 500}),
    "03-Grep-a-glob-of-256-expansions-over-2000-folders":
        lambda: ("Grep", {"pattern": "VALUE", "glob": BRACES_8 + "/" + FOLDERS * 2000 + "*"}),
    "04-Glob-a-pattern-of-256-expansions-over-2000-folders":
        lambda: ("Glob", {"pattern": BRACES_8 + "/" + FOLDERS * 2000 + "*"}),
    "05-Glob-a-path-of-2048-folders-and-a-pattern-of-256-expansions":
        lambda: ("Glob", {"path": FOLDERS * 2048, "pattern": BRACES_8 + "/*"}),
    "06-shell-a-reader-of-256-expansions-over-16000-folders":
        lambda: _bash("cat " + BRACES_8 + "/" + FOLDERS * 16000),
    "07-shell-a-reader-of-16-expansions-over-16000-folders":
        lambda: _bash("cat " + BRACES_4 + "/" + FOLDERS * 16000),
    "08-shell-a-link-from-256-expansions-over-15000-folders":
        lambda: _bash("ln -s " + BRACES_8 + FOLDERS * 15000 + " b"),
    "09-shell-the-other-program-with-300-filters-and-a-path-of-8000-folders":
        lambda: _bash(PROG + " " + "-gx " * 300 + "V " + FOLDERS * 8000),
    "10-shell-the-other-program-with-3000-filters-and-a-path-of-8000-folders":
        lambda: _bash(PROG + " " + "-gx " * 3000 + "V " + FOLDERS * 8000),
    "11-shell-grep-recursive-with-1000-filters-and-a-path-of-8000-folders":
        lambda: _bash("grep -r " + "--include=x " * 1000 + "V " + FOLDERS * 8000),
    "12-shell-a-pipeline-of-1000-fed-searches":
        lambda: _bash("true " + ("| " + PROG + " V ") * 1000),
    "13-shell-a-pipeline-of-4000-fed-searches":
        lambda: _bash("true " + ("| " + PROG + " V ") * 4000),
}


@pytest.mark.parametrize("shape", sorted(THIRTEEN))
def test_each_of_the_reviewer_s_inputs_is_decided_within_the_bound(world, shape):
    """Point 5: an allow or a refusal, in time; never a hook error, never the limit."""
    tool_name, tool_input = THIRTEEN[shape]()
    result = rnd.ask_timed(world, tool_name, tool_input)
    rnd.assert_decided_in_time(result, f"the input '{shape}'")


THIRTEEN_BY_ROLE = list(zip(rnd.OTHER_ROLES, ("02-Grep-a-path-of-1000-folders-and-a-glob-of-500-words",
                                              "09-shell-the-other-program-with-300-filters-and-a-path-of-8000-folders",
                                              "12-shell-a-pipeline-of-1000-fed-searches")))


@pytest.mark.parametrize("who,shape", THIRTEEN_BY_ROLE, ids=fix.ids(THIRTEEN_BY_ROLE))
def test_the_reviewer_s_inputs_are_decided_within_the_bound_for_other_roles(world, who, shape):
    """An engineer, the test designer and a session with no role: one input each."""
    tool_name, tool_input = THIRTEEN[shape]()
    result = rnd.ask_timed(world, tool_name, tool_input, who)
    rnd.assert_decided_in_time(result, f"the input '{shape}' by '{who}'")


# --------------------------------------------------------------------------
# The new forms of this round, at the length bound
# --------------------------------------------------------------------------

_NESTED = (NEAR - 40) // len("if true; then ; fi")
_SOURCE_SEARCH = PROG + " VALUE src"

NEW_FORMS = {
    "one-prefix-repeated-before-a-search": lambda: _repeat("timeout 1 ") + _SOURCE_SEARCH,
    "an-env-prefix-with-an-assignment-repeated-before-a-search": lambda: _repeat("env X=1 ") + "grep -rn VALUE src",
    "a-bang-repeated-before-a-search": lambda: _repeat("! ") + PROG + " -q VALUE src",
    "an-if-nested-many-times-around-a-search":
        lambda: "if true; then " * _NESTED + "grep -rn VALUE src" + "; fi" * _NESTED,
    "a-numbered-redirect-repeated-after-a-search": lambda: _SOURCE_SEARCH + " " + _repeat("2>&1 "),
    "many-short-loops-with-a-search-each": lambda: _repeat("for p in A; do grep -rn $p src; done; ") + "true",
    "a-search-and-a-very-long-comment": lambda: _SOURCE_SEARCH + " # " + _repeat("word "),
    "many-searches-with-a-comment-each-on-lines-of-their-own": lambda: _repeat(_SOURCE_SEARCH + " # all\n"),
    "egrep-recursive-with-1000-filters-and-a-path-of-8000-folders":
        lambda: "egrep -r " + "--include=x " * 1000 + "V " + FOLDERS * 8000,
}


@pytest.mark.parametrize("shape", sorted(NEW_FORMS))
def test_each_new_form_of_the_round_at_the_length_bound_is_decided_within_the_bound(world, shape):
    """Point 5: the forms points 1 to 3 make the rule judge, as long as a command may be. Green today."""
    result = rnd.ask_timed(world, "Bash", support.bash_tool_input(NEW_FORMS[shape]()))
    rnd.assert_decided_in_time(result, f"the command '{shape}'")


NEW_BY_ROLE = list(zip(rnd.OTHER_ROLES, ("one-prefix-repeated-before-a-search",
                                         "many-short-loops-with-a-search-each",
                                         "a-numbered-redirect-repeated-after-a-search")))


@pytest.mark.parametrize("who,shape", NEW_BY_ROLE, ids=fix.ids(NEW_BY_ROLE))
def test_the_new_forms_at_the_length_bound_are_decided_within_the_bound_for_other_roles(world, who, shape):
    result = rnd.ask_timed(world, "Bash", support.bash_tool_input(NEW_FORMS[shape]()), who)
    rnd.assert_decided_in_time(result, f"the command '{shape}' by '{who}'")


# The same shapes with the root as the search's path: refused, within the bound.
SEARCH_THE_ROOT = {
    "one-prefix-repeated-before-a-search-of-the-root": lambda: _repeat("timeout 1 ") + PROG + " VALUE .",
    "many-short-loops-and-then-one-with-a-search-of-the-root":
        lambda: _repeat("for p in A; do grep -rn $p src; done; ") + "for p in A; do grep -rn $p .; done",
    "a-search-with-no-path-and-a-very-long-comment": lambda: PROG + " VALUE # " + _repeat("word "),
    "a-numbered-redirect-repeated-after-a-search-with-no-path": lambda: PROG + " VALUE " + _repeat("2>&1 "),
}


@pytest.mark.parametrize("shape", sorted(SEARCH_THE_ROOT))
def test_a_new_form_at_the_length_bound_that_searches_the_root_is_refused_within_the_bound(world, shape):
    """Point 5: length buys no search of the root. Red before the change: allowed (in time)."""
    command = SEARCH_THE_ROOT[shape]()
    result = rnd.ask_timed(world, "Bash", support.bash_tool_input(command))
    what = f"the command '{shape}'"
    rnd.assert_refused_in_time(result, what)
    rnd.assert_carries_none_of(result, (world.project, command[:64], command[-64:]), what)


# Either file among the words. ``{rel}`` is the file's project-relative path (``w1_02_copies_support.fill``).
READ_A_FILE = {
    "an-if-nested-many-times-around-a-read-of-the-file":
        lambda: "if true; then " * _NESTED + "cat {rel}" + "; fi" * _NESTED,
    "one-prefix-repeated-before-a-read-of-the-file": lambda: _repeat("timeout 1 ") + "cat {rel}",
}


@pytest.mark.parametrize("name", fix.FILES)
@pytest.mark.parametrize("shape", sorted(READ_A_FILE))
def test_a_new_form_at_the_length_bound_that_reads_a_protected_file_is_refused_within_the_bound(world, shape, name):
    """Point 5: the guard refuses these today, in time (it reads every word); held, green before and after."""
    command = batch.fill(world, "own", name, READ_A_FILE[shape]())
    result = rnd.ask_timed(world, "Bash", support.bash_tool_input(command))
    what = f"the command '{shape}' on the stand-in {name}"
    rnd.assert_refused_in_time(result, what)
    rnd.assert_carries_none_of(result, world.secrets("own", name) + (command[:64],), what)


# --------------------------------------------------------------------------
# Ordinary sizes stay allowed, in time
# --------------------------------------------------------------------------

ORDINARY = {
    "a-search-of-sixty-source-paths-with-sixty-filters-for-source-files":
        lambda: _bash("grep -rn VALUE " + " ".join(f"--include='mod_{index:02}*.py'" for index in range(60)) + " "
                      + " ".join(f"src/pkg_{index:02}" for index in range(60))),
    "a-commit-with-a-message-of-thirty-thousand-characters-of-prose":
        lambda: _bash("git commit -m '" + _repeat("word ", 30000) + "'"),
    "a-reader-of-two-hundred-named-source-files":
        lambda: _bash("cat " + " ".join(f"src/app/module_{index:03}.py" for index in range(200))),
    "a-pipeline-of-twenty-grep-filters":
        lambda: _bash("git log --oneline" + " | grep VALUE" * 20),
}


@pytest.mark.parametrize("who", (rnd.WIDEST, folders.NO_ROLE))
@pytest.mark.parametrize("shape", sorted(ORDINARY))
def test_an_ordinary_size_stays_allowed_within_the_bound(world, shape, who):
    """As today: allowed, and answered within the same bound."""
    tool_name, tool_input = ORDINARY[shape]()
    result = rnd.ask_timed(world, tool_name, tool_input, who)
    rnd.assert_allowed_in_time(result, f"'{shape}' by '{who}'")


# --------------------------------------------------------------------------
# The inputs themselves
# --------------------------------------------------------------------------

def test_every_input_is_under_the_round_s_length_bounds():
    """No process: each input of this file is one the round's length bounds let the rule read."""
    inputs = [(shape, *build()) for shape, build in sorted(THIRTEEN.items())]
    inputs += [(shape, *build()) for shape, build in sorted(ORDINARY.items())]
    for forms in (NEW_FORMS, SEARCH_THE_ROOT, READ_A_FILE):
        # The longest a protected file's path makes a command: its place is filled with the longer of the two.
        longest = max(protected.PROTECTED.values(), key=len)
        inputs += [(shape, "Bash", {"command": build().replace("{rel}", longest)})
                   for shape, build in sorted(forms.items())]
    for shape, tool_name, tool_input in inputs:
        if tool_name == "Bash":
            assert len(tool_input["command"]) <= MOST_COMMAND, f"the command '{shape}' is longer than the bound"
        else:
            for field in {"Grep": ("path", "glob"), "Glob": ("path", "pattern")}[tool_name]:
                assert len(tool_input.get(field, "")) <= MOST_PATH, (
                    f"a field of the input '{shape}' is longer than the bound")
    near = [shape for shape, build in sorted(NEW_FORMS.items()) if len(build()) < 28000]
    assert not near, f"{len(near)} new form(s) are not built to the length bound: {near}"
