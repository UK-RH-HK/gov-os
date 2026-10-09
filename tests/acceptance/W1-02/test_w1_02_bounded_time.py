"""W1-02 — the read rule answers every pattern and every command in bounded time (DEC-562, probe finding 7).

DEC-562: "The rule answers every pattern and every command in bounded time: a
pattern or a command the rule cannot answer within its bound is refused."

Each case runs the hook as a process on one hook input and holds two things:

- **the hook ends within the bound** (``w1_02_round_support.BOUND_S``, on the
  hook's own time from start to exit; generous, seconds: this is not the latency
  KPI and it must hold on a busy machine);
- **the answer is a decision**: a refusal when the input takes a protected file
  in; a refusal or an allow when the input, read in full, takes neither file in
  (a refusal of an input the rule gives up on is acceptable, an allow of an
  input that takes a file in is not). A refusal may be the rule's decision or
  the guard's report that it gave up (DEC-110): the shape is not held here.

The test's own limit on the process (``PROCESS_LIMIT_S``) only keeps a run from
hanging: a hook still running then has given no answer.

**Before the change** (measured on stand-ins, README): a glob of a dozen and
more star pairs glued together took more than 30 s in the Glob tool, in the
search tool's glob and in a shell word, also in a word of a command that reads
nothing; so did sixty pairs with a slash between them from an absolute start;
a thousand and more unclosed substitutions took more than 12 s; a megabyte of
short words about 15 s (200 KB about 3 s on this machine; the probe measured
about 8 s). Those cases are red: no answer within the bound. The shapes the rule
already answers at once are held too, and are green.

**What stays allowed**: an ordinary long command and an ordinary glob with two
or three star pairs are allowed as today, within the same bound.

No case names a protected file by a typed path: the names come from the guard's
constants, and no id or failure message carries a command or a pattern.
"""

from __future__ import annotations

import os

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_round_support as rnd
import w1_02_support as support

PAIRS = 60                       # star pairs in one pattern
GLUED = "**" * PAIRS             # with nothing between them
SLASHED = "**/" * PAIRS          # with a slash between them
LETTERED = "**e" * PAIRS         # with a letter between them
NO_MATCH = "zz"                  # a tail no file of the stand-in project has
KB = 1024


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return rnd.make_world(tmp_path_factory.mktemp("bounded-time"))


def _name(world, name):
    return os.path.basename(protected.PROTECTED[name])


def _file(world, name):
    return str(world.site("own").path(name))


def _bash(command):
    return ("Bash", support.bash_tool_input(command), None)


# --------------------------------------------------------------------------
# A glob of many star pairs
# --------------------------------------------------------------------------

# label -> builder(world) -> (tool, input, working folder). Read in full, none of these takes a protected file in:
# the tail matches no file. An allow and a refusal are both acceptable; no answer is not.
MANY_PAIRS_THAT_TAKE_NEITHER_FILE_IN = {
    "Glob-pattern-glued-pairs-from-the-root":
        lambda w: ("Glob", {"pattern": GLUED + NO_MATCH, "path": str(w.project)}, None),
    "Glob-pattern-glued-pairs-with-no-path":
        lambda w: ("Glob", {"pattern": GLUED + NO_MATCH}, None),
    "Glob-pattern-glued-pairs-from-a-copy-s-folder":
        lambda w: ("Glob", {"pattern": GLUED + NO_MATCH, "path": str(w.site("sibling").root)}, None),
    "Glob-absolute-pattern-pairs-with-a-slash-between":
        lambda w: ("Glob", {"pattern": "/" + SLASHED + "*.py"}, None),
    "Grep-glob-glued-pairs-from-the-root":
        lambda w: ("Grep", {"pattern": "VALUE", "path": str(w.project), "glob": GLUED + NO_MATCH}, None),
    "shell-word-glued-pairs-after-a-reader":
        lambda w: _bash("cat " + GLUED + NO_MATCH),
    "shell-word-glued-pairs-in-a-command-that-reads-nothing":
        lambda w: _bash("echo " + GLUED + NO_MATCH),
    "shell-word-absolute-pairs-with-a-slash-between":
        lambda w: _bash("cat /" + SLASHED + "*.py"),
    # answered at once before the change already (green today), and held
    "Glob-pattern-pairs-with-a-slash-between-from-the-root":
        lambda w: ("Glob", {"pattern": SLASHED + "*.py", "path": str(w.project)}, None),
    "Glob-pattern-pairs-with-a-letter-between":
        lambda w: ("Glob", {"pattern": LETTERED + NO_MATCH, "path": str(w.project)}, None),
    "Grep-glob-pairs-with-a-slash-between":
        lambda w: ("Grep", {"pattern": "VALUE", "path": str(w.project), "glob": SLASHED + "*.py"}, None),
    "Glob-pattern-glued-pairs-from-a-source-folder":
        lambda w: ("Glob", {"pattern": GLUED + NO_MATCH, "path": str(w.project / folders.SOURCE_REL)}, None),
}


@pytest.mark.parametrize("shape", sorted(MANY_PAIRS_THAT_TAKE_NEITHER_FILE_IN))
def test_a_glob_of_many_star_pairs_is_answered_within_the_bound(world, shape):
    """Point 3: sixty star pairs in the Glob tool's pattern, in the search tool's glob, in a shell word."""
    tool_name, tool_input, cwd = MANY_PAIRS_THAT_TAKE_NEITHER_FILE_IN[shape](world)
    result = rnd.ask_timed(world, tool_name, tool_input, cwd=cwd)
    rnd.assert_decided_in_time(result, f"the glob of {PAIRS} star pairs '{shape}'")


# These take a protected file in: the answer is a refusal, within the bound.
MANY_PAIRS_THAT_TAKE_A_FILE_IN = {
    "Glob-pattern-glued-pairs-then-the-file-s-name":
        lambda w, name: ("Glob", {"pattern": GLUED + _name(w, name), "path": str(w.project)}, None),
    "Grep-glob-glued-pairs-then-the-file-s-name":
        lambda w, name: ("Grep", {"pattern": "VALUE", "path": str(w.project), "glob": GLUED + _name(w, name)}, None),
    "shell-word-glued-pairs-then-the-file-s-name":
        lambda w, name: _bash("cat " + GLUED + _name(w, name)),
    # answered at once before the change already (green today), and held
    "Glob-pattern-pairs-with-a-slash-between-then-the-file-s-name":
        lambda w, name: ("Glob", {"pattern": SLASHED + _name(w, name), "path": str(w.project)}, None),
    "Glob-pattern-glued-pairs-alone":
        lambda w, name: ("Glob", {"pattern": GLUED, "path": str(w.project)}, None),
    "shell-word-pairs-with-a-slash-between-then-a-star":
        lambda w, name: _bash("cat " + SLASHED + "*"),
}


@pytest.mark.parametrize("name", rnd.FILES)
@pytest.mark.parametrize("shape", sorted(MANY_PAIRS_THAT_TAKE_A_FILE_IN))
def test_a_glob_of_many_star_pairs_that_takes_a_protected_file_in_is_refused_within_the_bound(world, shape, name):
    """Point 3: "when the input takes in either file, or the rule cannot tell within its bound, a refusal"."""
    tool_name, tool_input, cwd = MANY_PAIRS_THAT_TAKE_A_FILE_IN[shape](world, name)
    result = rnd.ask_timed(world, tool_name, tool_input, cwd=cwd)
    what = f"the glob of {PAIRS} star pairs '{shape}' for the stand-in {name}"
    rnd.assert_refused_in_time(result, what)
    rnd.assert_carries_none_of(result, world.secrets("own", name) + (GLUED[:40], SLASHED[:40]), what)


# --------------------------------------------------------------------------
# A long run of substitutions, and a very long command
# --------------------------------------------------------------------------

LONG_COMMANDS_THAT_TAKE_NEITHER_FILE_IN = {
    "three-thousand-unclosed-substitutions": lambda w: "echo " + "$(" * 3000,
    "a-thousand-unclosed-substitutions-with-words-between": lambda w: "echo " + "$(echo a " * 1000,
    "ten-thousand-unclosed-process-substitutions": lambda w: "cat " + "<(" * 10000,
    "a-thousand-substitutions-one-inside-the-other": lambda w: "echo " + "$(echo " * 1000 + ")" * 1000,
    "a-megabyte-of-short-words": lambda w: "echo " + "a " * (512 * KB),
    "a-megabyte-in-one-word": lambda w: "echo " + "a" * (1024 * KB),
    "two-hundred-kilobytes-of-short-words": lambda w: "echo " + "a " * (100 * KB),
    "two-hundred-kilobytes-of-short-commands": lambda w: "true; " * (200 * KB // 6) + "true",
    # answered at once before the change already (green today), and held
    "ten-thousand-backticks": lambda w: "echo " + "`" * 10000,
    "ten-thousand-closed-substitutions": lambda w: "echo " + "$(true) " * 10000,
}


@pytest.mark.parametrize("shape", sorted(LONG_COMMANDS_THAT_TAKE_NEITHER_FILE_IN))
def test_a_long_run_of_substitutions_or_a_very_long_command_is_answered_within_the_bound(world, shape):
    """Point 3: no command leaves the rule without an answer."""
    command = LONG_COMMANDS_THAT_TAKE_NEITHER_FILE_IN[shape](world)
    result = rnd.ask_timed(world, "Bash", support.bash_tool_input(command))
    rnd.assert_decided_in_time(result, f"the command '{shape}'")


LONG_COMMANDS_THAT_READ_A_FILE = {
    "a-megabyte-of-short-words-and-then-a-read-of-the-file":
        lambda w, name: "echo " + "a " * (512 * KB) + "&& cat " + _file(w, name),
    "a-read-of-the-file-and-then-a-megabyte-of-short-words":
        lambda w, name: "cat " + _file(w, name) + " && echo " + "a " * (512 * KB),
    # answered at once before the change already (green today), and held
    "three-thousand-unclosed-substitutions-and-then-a-read-of-the-file":
        lambda w, name: "echo " + "$(" * 3000 + "cat " + _file(w, name),
    "a-thousand-unclosed-substitutions-with-words-and-then-a-read-of-the-file":
        lambda w, name: "echo " + "$(echo a " * 1000 + "$(cat " + _file(w, name),
}


@pytest.mark.parametrize("name", rnd.FILES)
@pytest.mark.parametrize("shape", sorted(LONG_COMMANDS_THAT_READ_A_FILE))
def test_a_very_long_command_that_reads_a_protected_file_is_refused_within_the_bound(world, shape, name):
    """Point 3: length buys no read: the refusal comes within the bound and carries neither the path nor the command."""
    command = LONG_COMMANDS_THAT_READ_A_FILE[shape](world, name)
    result = rnd.ask_timed(world, "Bash", support.bash_tool_input(command))
    what = f"the command '{shape}' on the stand-in {name}"
    rnd.assert_refused_in_time(result, what)
    rnd.assert_carries_none_of(result, world.secrets("own", name) + ("a " * 20, "$(" * 20), what)


@pytest.mark.parametrize("who", rnd.OTHER_ROLES)
def test_the_bound_holds_for_every_role(world, who):
    """An engineer, the test designer and a session with no role: a glob of many pairs, a run of substitutions."""
    result = rnd.ask_timed(world, "Glob", {"pattern": GLUED + NO_MATCH, "path": str(world.project)}, who)
    rnd.assert_decided_in_time(result, f"a Glob pattern of {PAIRS} glued star pairs by '{who}'")
    result = rnd.ask_timed(world, "Bash", support.bash_tool_input("echo " + "$(" * 3000), who)
    rnd.assert_decided_in_time(result, f"three thousand unclosed substitutions by '{who}'")


# --------------------------------------------------------------------------
# What stays allowed: green before and after
# --------------------------------------------------------------------------

ORDINARY = {
    "a-commit-with-a-message-of-four-thousand-characters":
        lambda w: _bash("git commit -m '" + "word " * 800 + "'"),
    "a-test-run-that-names-forty-files":
        lambda w: _bash("python3 -m pytest "
                        + " ".join(f"tests/unit/guard/test_case_{index:02}.py" for index in range(40)) + " -q"),
    "Glob-with-two-star-pairs-from-the-root":
        lambda w: ("Glob", {"pattern": "**/tests/**/*.py", "path": str(w.project)}, None),
    "Glob-with-two-star-pairs-and-no-path":
        lambda w: ("Glob", {"pattern": "**/tests/**/*.py"}, None),
    "Glob-with-three-star-pairs":
        lambda w: ("Glob", {"pattern": "**/tests/**/unit/**/*.py", "path": str(w.project)}, None),
    "Grep-glob-with-two-star-pairs":
        lambda w: ("Grep", {"pattern": "VALUE", "glob": "**/tests/**/*.py"}, None),
    "shell-word-with-two-star-pairs":
        lambda w: _bash("ls **/tests/**/*.py"),
}


@pytest.mark.parametrize("who", (rnd.WIDEST, folders.NO_ROLE))
@pytest.mark.parametrize("shape", sorted(ORDINARY))
def test_an_ordinary_long_command_and_an_ordinary_glob_stay_allowed_within_the_bound(world, shape, who):
    """As today: allowed, and answered within the same bound."""
    tool_name, tool_input, cwd = ORDINARY[shape](world)
    result = rnd.ask_timed(world, tool_name, tool_input, who, cwd)
    rnd.assert_allowed_in_time(result, f"'{shape}' by '{who}'")
