"""W1-02 — the held-out check answers a very long string in a field that is no path within the bound (DEC-574, point 3).

DEC-574: "The held-out check skips path resolution for any string longer than
the system path limit, and keeps the literal substring check."

The harness lets a call through when the hook passes its time limit
(``docs/research/EXP-hook-time-limit.md``), so a slow decision fails open.
Reading a megabyte of path-like text as one path takes the guard as built 40
seconds and more.

**The bound** is the one the earlier time cases of this revision use,
unchanged: the hook ends with a decision within
``w1_02_round_support.BOUND_S`` (5 s) of its own time, start to exit; a case
ends the process at ``PROCESS_LIMIT_S`` (8 s) and fails. The bound is generous
for a loaded machine: the engineer is told to answer each of these inputs in
well under a second of the check's own time.

Held, through the hook run as a process on a hook input:

- **the inputs that take too long today**, each decided in time, and decided
  as a short content is for the same role and file (red today: no answer
  within the bound; measured, README);
- **the same sizes with a held-out path as literal text inside**, refused in
  time by the held-out check;
- **shapes near the limit**, each decided in time;
- **ordinary large source text** stays allowed where the role may write, in
  time (green today).

No id and no failure message carries a path or a command.
"""

from __future__ import annotations

import pytest

import w1_02_limit_support as limit
import w1_02_protected_support as protected
import w1_02_round_support as rnd
import w1_02_support as support

MB = limit.MB
PATH_LIKE = "a/"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project with its stand-in files for the module: the cases only ask the guard for decisions."""
    return limit.make_world(tmp_path_factory.mktemp("path-limit-time"))


def _source(world):
    return str(world.project / limit.SOURCE_REL)


def _assert_decided_in_time_as_a_short_content_is(result, tool_name, who, what):
    rnd.assert_decided_in_time(result, what)
    limit.assert_decided_as_a_whole(result, tool_name, who, what)


# --------------------------------------------------------------------------
# The inputs that take too long today
# --------------------------------------------------------------------------

# label -> builder(world, a megabyte of path-like text) -> (tool, input)
TOO_LONG_TODAY = {
    "a-Write-whose-content-is-a-megabyte-of-a-short-folder-name-repeated":
        lambda w, mb: ("Write", {"file_path": _source(w), "content": mb}),
    "a-Write-whose-content-is-four-megabytes-of-it":
        lambda w, mb: ("Write", {"file_path": _source(w), "content": mb * 4}),
    "an-Edit-with-a-megabyte-of-it-in-each-of-its-two-strings":
        lambda w, mb: ("Edit", {"file_path": _source(w), "old_string": mb, "new_string": mb}),
    "an-unknown-tool-with-a-megabyte-of-it-in-a-field":
        lambda w, mb: ("ToolAddedAfterThisTicket", {"target": mb}),
    "an-unknown-tool-with-a-megabyte-of-it-in-a-nested-field":
        lambda w, mb: ("mcp__notes__add", {"note": {"title": "a note", "body": ["a first line", mb]}}),
}


@pytest.mark.parametrize("shape", sorted(TOO_LONG_TODAY))
def test_an_input_that_takes_too_long_today_is_decided_within_the_bound(world, shape):
    """Point 3: allowed for the orchestrator, as a short content is. Red today: no answer within the bound."""
    tool_name, tool_input = TOO_LONG_TODAY[shape](world, PATH_LIKE * (MB // 2))
    result = limit.ask_timed(world, tool_name, tool_input)
    _assert_decided_in_time_as_a_short_content_is(result, tool_name, limit.ORCHESTRATOR, f"'{shape}'")


@pytest.mark.parametrize("who", limit.OTHER_ROLES)
def test_a_megabyte_in_a_write_s_content_is_decided_within_the_bound_for_another_role(world, who):
    """An engineer who may write the file is allowed; a session with no role is denied by the allow-list. Red today."""
    result = limit.ask_timed(world, "Write", {"file_path": _source(world), "content": PATH_LIKE * (MB // 2)}, who)
    _assert_decided_in_time_as_a_short_content_is(
        result, "Write", who, "a Write whose content is a megabyte of a short folder name repeated")


# --------------------------------------------------------------------------
# The same sizes with a held-out path as literal text inside
# --------------------------------------------------------------------------

def _around(world, size):
    """``size`` characters of path-like text with the stand-in held-out path in the middle."""
    half = PATH_LIKE * (size // 4)
    return half + str(world.listed) + half


WITH_A_LITERAL_PATH = {
    "a-Write-whose-content-is-a-megabyte":
        lambda w: ("Write", {"file_path": _source(w), "content": _around(w, MB)}),
    "a-Write-whose-content-is-four-megabytes":
        lambda w: ("Write", {"file_path": _source(w), "content": _around(w, 4 * MB)}),
    "an-Edit-with-a-megabyte-in-each-string-and-the-path-in-the-second":
        lambda w: ("Edit", {"file_path": _source(w), "old_string": PATH_LIKE * (MB // 2),
                            "new_string": _around(w, MB)}),
    "an-unknown-tool-with-a-megabyte-in-a-field":
        lambda w: ("ToolAddedAfterThisTicket", {"target": _around(w, MB)}),
    "an-unknown-tool-with-a-megabyte-in-a-nested-field":
        lambda w: ("mcp__notes__add", {"note": {"title": "a note", "body": ["a first line", _around(w, MB)]}}),
}


@pytest.mark.parametrize("shape", sorted(WITH_A_LITERAL_PATH))
def test_the_same_size_with_a_held_out_path_as_literal_text_inside_is_refused_within_the_bound(world, shape):
    """Point 3: length buys nothing. Green today but the Edit, whose first string is resolved for 40 s before."""
    tool_name, tool_input = WITH_A_LITERAL_PATH[shape](world)
    result = limit.ask_timed(world, tool_name, tool_input)
    what = f"'{shape}' with the stand-in held-out path inside"
    rnd.assert_refused_in_time(result, what)
    limit.assert_refused_by_the_held_out_check(result, world, what, (PATH_LIKE * 24,))


def test_a_megabyte_with_a_literal_held_out_path_is_refused_within_the_bound_for_a_session_with_no_role(world):
    who = limit.NO_ROLE
    tool_name, tool_input = WITH_A_LITERAL_PATH["a-Write-whose-content-is-a-megabyte"](world)
    result = limit.ask_timed(world, tool_name, tool_input, who)
    what = f"a Write of a megabyte with the stand-in held-out path inside, by '{who}'"
    rnd.assert_refused_in_time(result, what)
    limit.assert_refused_by_the_held_out_check(result, world, what)


# --------------------------------------------------------------------------
# Shapes near the limit
# --------------------------------------------------------------------------

def _write(world, content):
    return "Write", {"file_path": _source(world), "content": content}


def _echo(text):
    command = "echo " + text
    assert len(command) <= limit.MOST_COMMAND, "the fixture command is longer than the guard reads"
    return "Bash", support.bash_tool_input(command)


SHAPES = {
    "a-string-just-over-the-limit": lambda w: _write(w, limit.filler(PATH_LIKE, limit.LIMIT + 1)),
    "a-megabyte-of-text-with-no-separator-at-all": lambda w: _write(w, "a" * MB),
    "a-megabyte-of-short-lines": lambda w: _write(w, "a/b\n" * (MB // 4)),
    "a-megabyte-of-the-folder-above-repeated": lambda w: _write(w, limit.filler("../", MB)),
    "a-megabyte-of-the-home-folder-s-short-form-repeated": lambda w: _write(w, "~/" * (MB // 2)),
    "a-Bash-command-near-its-bound-made-of-one-long-word":
        lambda w: _echo(PATH_LIKE * ((limit.NEAR_COMMAND - 5) // 2)),
    "a-Bash-command-near-its-bound-made-of-many-short-words":
        lambda w: _echo("a/b " * ((limit.NEAR_COMMAND - 5) // 4)),
}


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_a_shape_near_the_limit_is_decided_within_the_bound(world, shape):
    """Point 3: allowed for the orchestrator, as a short content is, in time. Measured today in the README."""
    tool_name, tool_input = SHAPES[shape](world)
    result = limit.ask_timed(world, tool_name, tool_input)
    _assert_decided_in_time_as_a_short_content_is(result, tool_name, limit.ORCHESTRATOR, f"'{shape}'")


SHAPES_BY_ROLE = [(limit.ENGINEER, "a-megabyte-of-short-lines")]


@pytest.mark.parametrize("who,shape", SHAPES_BY_ROLE, ids=[f"{who}-{shape}" for who, shape in SHAPES_BY_ROLE])
def test_a_shape_near_the_limit_is_decided_within_the_bound_for_another_role(world, who, shape):
    tool_name, tool_input = SHAPES[shape](world)
    result = limit.ask_timed(world, tool_name, tool_input, who)
    _assert_decided_in_time_as_a_short_content_is(result, tool_name, who, f"'{shape}'")


# --------------------------------------------------------------------------
# Ordinary large source text stays as fast as it is
# --------------------------------------------------------------------------

_SOURCE_LINES = (
    '    path = os.path.join(root, "src/app/module_{index:04}.py")  # see docs/spec/feature.md and tests/unit/guard\n'
    '    with open(path, encoding="utf-8") as handle:\n'
    '        return [line.rstrip("/") for line in handle if "/" in line and not line.startswith("#")]\n'
)


def _source_text(length):
    """Lines of code with paths and slashes in them, as a real module has: exactly ``length`` characters."""
    count = length // len(_SOURCE_LINES) + 2
    return "".join(_SOURCE_LINES.format(index=index) for index in range(count))[:length]


ORDINARY = {
    "a-Write-of-200000-characters-of-source-text":
        lambda w: ("Write", {"file_path": _source(w), "content": _source_text(200000)}),
    "an-Edit-of-50000-characters-of-source-text":
        lambda w: ("Edit", {"file_path": _source(w), "old_string": _source_text(50000),
                            "new_string": _source_text(50000).replace("handle", "stream")}),
    "a-commit-with-a-message-of-30000-characters":
        lambda w: ("Bash", support.bash_tool_input(
            "git commit -m '" + limit.filler("see src/app/main.py and docs/notes.md; ", 30000) + "'")),
}
ORDINARY_BY = [(shape, limit.ORCHESTRATOR) for shape in sorted(ORDINARY)]
ORDINARY_BY += [("a-Write-of-200000-characters-of-source-text", limit.ENGINEER),
                ("a-commit-with-a-message-of-30000-characters", limit.NO_ROLE)]


@pytest.mark.parametrize("shape,who", ORDINARY_BY, ids=[f"{shape}-by-{who}" for shape, who in ORDINARY_BY])
def test_ordinary_large_source_text_stays_allowed_within_the_bound(world, shape, who):
    """As today: allowed where the role may write, and answered within the same bound. Green today, stays green."""
    tool_name, tool_input = ORDINARY[shape](world)
    result = limit.ask_timed(world, tool_name, tool_input, who)
    rnd.assert_answered_in_time(result, f"'{shape}' by '{who}'")
    protected.assert_allowed(result, f"'{shape}' by '{who}'")
