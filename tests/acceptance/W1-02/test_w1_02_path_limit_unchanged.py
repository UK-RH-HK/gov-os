"""W1-02 — what the held-out check keeps refusing once it resolves no string past the path limit (DEC-574, point 2).

DEC-574: "The held-out check skips path resolution for any string longer than
the system path limit, and keeps the literal substring check."

This is the one change of the round that allows what was refused, so each of
these is held by cases, through the hook run as a process on a hook input, in a
temporary project with a stand-in held-out file that lists a stand-in held-out
folder:

- **a long string that holds a held-out path as literal text is refused**,
  wherever the path stands in it, in any field of any tool, at lengths just
  over the limit, at 100,000 characters and at a megabyte (a Bash command stays
  under its own bound). The reason is the held-out check's own and carries no
  path;
- **the exception stays as it is**: an edit of one of the two files that may
  carry a held-out path is not refused for what it carries, at a length over
  the limit as at an ordinary one (W1-47 holds the ordinary one);
- **a string at or under the limit is judged as today**, in the fields that are
  no path field (W1-47 holds the path fields and the Bash forms);
- **a long string of many short pieces is read as today**: a Bash command word
  by word, any other string as one path.

All of these are green on the guard as built and stay green, but one group: a
string of lines whose **first** line reaches the stand-in held-out folder is
refused today at any length (read as one path, it lies below that folder), and
past the limit it is the ordered change of point 1: red today.

No id and no failure message carries a path or a command.
"""

from __future__ import annotations

import pytest

import w1_02_limit_support as limit
import w1_02_protected_support as protected
import w1_02_support as support

LIMIT = limit.LIMIT


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project with its stand-in files for the module: the cases only ask the guard for decisions."""
    return limit.make_world(tmp_path_factory.mktemp("path-limit-unchanged"))


def _ids(rows):
    return ["-".join(str(part) for part in row) for row in rows]


# --------------------------------------------------------------------------
# A long string that holds a held-out path as literal text
# --------------------------------------------------------------------------

PATH_LIKE = "a/"


def _with_literal(world, position, length):
    """A string of ``length`` characters of path-like text with the stand-in held-out path at ``position``."""
    held = str(world.listed)
    room = length - len(held)
    half = room // 2
    if position == "at-its-start":
        return held + limit.filler(PATH_LIKE, room)
    if position == "in-its-middle":
        return limit.filler(PATH_LIKE, half) + held + limit.filler(PATH_LIKE, room - half)
    if position == "at-its-end":
        return limit.filler(PATH_LIKE, room) + held
    if position == "on-a-line-of-its-own":
        return limit.filler(PATH_LIKE, half - 1) + "\n" + held + "\n" + limit.filler(PATH_LIKE, room - half - 1)
    if position == "glued-between-other-characters":
        return limit.filler("word", half) + held + limit.filler("word", room - half)
    raise ValueError(position)


POSITIONS = ("at-its-start", "in-its-middle", "at-its-end", "on-a-line-of-its-own", "glued-between-other-characters")
SIZES = {"just-over-the-limit": LIMIT + 1, "100000-characters": 100000, "a-megabyte": limit.MB}
# A Bash command stays under its own bound.
COMMAND_SIZES = {"just-over-the-limit": LIMIT + 1, "20000-characters": 20000,
                 "near-the-command-bound": limit.NEAR_COMMAND}
# Every field at every size; the position turns, so that each stands at each size and in every kind of field.
LITERAL = [(field, size, POSITIONS[(row + step) % len(POSITIONS)])
           for row, field in enumerate(sorted(limit.FIELDS)) for step, size in enumerate(SIZES)]
LITERAL += [(limit.BASH_COMMAND, size, POSITIONS[(1 + 2 * step) % len(POSITIONS)])
            for step, size in enumerate(COMMAND_SIZES)]


def _literal_call(world, field, size, position):
    length = {**SIZES, **COMMAND_SIZES}[size]
    if field == limit.BASH_COMMAND:
        text = "echo " + _with_literal(world, position, length - 5)
        assert len(text) <= limit.MOST_COMMAND, "the fixture command is longer than the guard reads"
    else:
        text = _with_literal(world, position, length)
    assert len(text) > LIMIT, "the fixture string is not past the limit"
    return limit.call(world, field, text)


@pytest.mark.parametrize("field,size,position", LITERAL, ids=_ids(LITERAL))
def test_a_long_string_that_holds_a_held_out_path_as_literal_text_is_refused(world, field, size, position):
    """Point 2: the literal check is kept, at any length. Green today, stays green."""
    tool_name, tool_input = _literal_call(world, field, size, position)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a string of {size} with the stand-in held-out path {position}, in {field},",
        (PATH_LIKE * 24,))


LITERAL_BY_ROLE = [
    ("a-Write-s-content", "a-megabyte", "in-its-middle", limit.ENGINEER),
    ("a-field-of-an-unknown-tool", "100000-characters", "at-its-end", limit.NO_ROLE),
    (limit.BASH_COMMAND, "near-the-command-bound", "glued-between-other-characters", limit.ENGINEER),
]


@pytest.mark.parametrize("field,size,position,who", LITERAL_BY_ROLE, ids=_ids(LITERAL_BY_ROLE))
def test_a_long_string_with_a_literal_held_out_path_is_refused_for_another_role(world, field, size, position, who):
    """Green today, stays green."""
    tool_name, tool_input = _literal_call(world, field, size, position)
    result = limit.ask(world, tool_name, tool_input, who)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a string of {size} with the stand-in held-out path {position}, in {field}, by {who}")


# --------------------------------------------------------------------------
# The exception: an edit of one of the two files that may carry a held-out path
# --------------------------------------------------------------------------

EDITS = {
    "a-Write": lambda path, text: ("Write", {"file_path": path, "content": text}),
    "an-Edit-s-new-string": lambda path, text: ("Edit", {"file_path": path, "old_string": "a", "new_string": text}),
}
HOLDERS = sorted(protected.PROTECTED)
EXCEPTION = [(holder, "a-Write") for holder in HOLDERS] + [(HOLDERS[0], "an-Edit-s-new-string")]


def _edit_of_a_holder(world, holder, edit):
    text = _with_literal(world, "on-a-line-of-its-own", 100000)
    return EDITS[edit](str(world.project / protected.PROTECTED[holder]), text)


@pytest.mark.parametrize("holder,edit", EXCEPTION, ids=_ids(EXCEPTION))
def test_an_edit_of_a_file_that_may_carry_the_path_is_not_refused_for_carrying_it_at_a_length_over_the_limit(
        world, holder, edit):
    """As at an ordinary length (W1-47): the orchestrator, whose role rules allow the edit. Green today."""
    tool_name, tool_input = _edit_of_a_holder(world, holder, edit)
    result = limit.ask(world, tool_name, tool_input)
    protected.assert_allowed(result, f"{edit} of 100,000 characters to the stand-in {holder} by the orchestrator")


def test_the_usual_role_rules_still_apply_to_an_edit_over_the_limit_of_the_two_files(world):
    """An engineer who may not write the file is denied as before, and not by the held-out check. Green today."""
    holder = HOLDERS[-1]
    tool_name, tool_input = _edit_of_a_holder(world, holder, "a-Write")
    result = limit.ask(world, tool_name, tool_input, limit.ENGINEER)
    what = f"a Write of 100,000 characters to the stand-in {holder} by an engineer"
    limit.assert_not_refused_by_the_held_out_check(result, what)
    assert result.decision == "deny", f"{what} was not denied: decision={result.decision}"


def test_the_exception_is_for_the_two_files_only_at_a_length_over_the_limit(world):
    """The same Write to another file the orchestrator may write is refused for carrying the path. Green today."""
    text = _with_literal(world, "on-a-line-of-its-own", 100000)
    for other in ("docs/notes.md", protected.NEIGHBOUR_OF_SETTINGS):
        result = limit.ask(world, "Write", {"file_path": str(world.project / other), "content": text})
        limit.assert_refused_by_the_held_out_check(
            result, world, "a Write of 100,000 characters that carries the stand-in held-out path to another file")


# --------------------------------------------------------------------------
# A string at or under the limit is judged as today
# --------------------------------------------------------------------------

# label -> (field, builder(world) -> a string of ordinary length that reaches the stand-in held-out folder)
REACHED = {
    "a-relative-path": ("a-Write-s-content", lambda w: f"{w.relative}/{limit.FILE_NAME}"),
    "a-path-through-dot-dot":
        ("an-Edit-s-new-string", lambda w: f"{w.elsewhere}/detour/../{w.listed.name}/{limit.FILE_NAME}"),
    "the-home-folder-s-short-form":
        ("a-field-of-an-unknown-tool", lambda w: f"~/{limit.LINK_NAME}/{limit.FILE_NAME}"),
    "a-symbolic-link": ("a-list-inside-the-input", lambda w: f"{w.link}/{limit.FILE_NAME}"),
    "a-path-below-the-held-out-folder":
        ("an-Edit-s-old-string", lambda w: f"{w.link}/cases/deeper/test_hidden.py"),
}
# label -> (field, builder(world) -> an ordinary string that reaches nothing held out)
NOT_REACHED = {
    "a-file-of-a-folder-that-is-not-held-out": ("a-Write-s-content", lambda w: f"{w.other}/{limit.FILE_NAME}"),
    "a-source-path-of-the-project": ("a-field-of-an-unknown-tool", lambda w: "src/app/main.py"),
    "prose-with-slashes-in-it":
        ("an-Edit-s-new-string", lambda w: "see docs/notes.md and/or src/app/main.py for the rest"),
}


@pytest.mark.parametrize("shape", sorted(REACHED))
def test_a_string_of_ordinary_length_that_reaches_the_held_out_folder_is_refused_in_a_field_that_is_no_path(
        world, shape):
    """As today: W1-47 holds these forms in the path fields and in a Bash command. Green today, stays green."""
    field, build = REACHED[shape]
    tool_name, tool_input = limit.call(world, field, limit.holds_no_literal(world, build(world)))
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_refused_by_the_held_out_check(result, world, f"'{shape}' of ordinary length in {field}")


@pytest.mark.parametrize("shape", sorted(NOT_REACHED))
def test_an_ordinary_string_that_reaches_nothing_held_out_stays_allowed(world, shape):
    """As today. Green today, stays green."""
    field, build = NOT_REACHED[shape]
    tool_name, tool_input = limit.call(world, field, build(world))
    result = limit.ask(world, tool_name, tool_input)
    protected.assert_allowed(result, f"'{shape}' in {field} by the orchestrator")


# --------------------------------------------------------------------------
# A long Bash command of many short words: judged word by word
# --------------------------------------------------------------------------

SHORT_WORD = "src/app/a.py "

# What separates words for the check: label -> what stands between the word before and the word that reaches.
SEPARATORS = {
    "a-space": "x ",
    "a-tab": "x\t",
    "a-newline": "x\n",
    "a-semicolon-with-nothing-around-it": "x;cat ",
    "a-pipe-with-nothing-around-it": "x|cat ",
    "two-ampersands": "x && cat ",
    "an-opening-parenthesis": "x ; (cat ",
    "an-input-redirect-with-nothing-around-it": "x ; wc -l <",
}
REACHING_WORDS = {
    "a-relative-word": lambda w: f"{w.relative}/{limit.FILE_NAME}",
    "a-word-through-a-symbolic-link": lambda w: f"{w.link}/{limit.FILE_NAME}",
}
MANY_WORDS = [(separator, "near-the-command-bound", sorted(REACHING_WORDS)[row % 2])
              for row, separator in enumerate(sorted(SEPARATORS))]
MANY_WORDS += [("a-space", "just-over-the-limit", "a-word-through-a-symbolic-link")]
COMMAND_LENGTHS = {"near-the-command-bound": limit.NEAR_COMMAND, "just-over-the-limit": LIMIT + 400}


def _many_short_words(length):
    return "echo " + SHORT_WORD * ((length - 400) // len(SHORT_WORD))


@pytest.mark.parametrize("separator,size,word", MANY_WORDS, ids=_ids(MANY_WORDS))
def test_a_long_command_of_many_short_words_in_which_one_word_reaches_the_held_out_folder_is_refused(
        world, separator, size, word):
    """The command is past the path limit; no word of it is. Green today, stays green."""
    reaching = limit.holds_no_literal(world, REACHING_WORDS[word](world))
    command = _many_short_words(COMMAND_LENGTHS[size]) + SEPARATORS[separator] + reaching
    assert LIMIT < len(command) <= limit.MOST_COMMAND, "the fixture command has not the length the case needs"
    result = limit.ask(world, "Bash", support.bash_tool_input(command))
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a command {size} of many short words with {word} after {separator}", (SHORT_WORD * 4,))


NOTHING_REACHED = [("just-over-the-limit", limit.ORCHESTRATOR), ("near-the-command-bound", limit.ORCHESTRATOR),
                   ("near-the-command-bound", limit.NO_ROLE)]


@pytest.mark.parametrize("size,who", NOTHING_REACHED, ids=_ids(NOTHING_REACHED))
def test_a_long_command_of_many_short_words_that_reach_nothing_stays_allowed(world, size, who):
    """As today: a command that writes nothing is allowed to every role. Green today, stays green."""
    command = _many_short_words(COMMAND_LENGTHS[size]) + f"{world.other}/{limit.FILE_NAME}"
    result = limit.ask(world, "Bash", support.bash_tool_input(command), who)
    protected.assert_allowed(result, f"a command {size} of many short words that reach nothing, by '{who}'")


# --------------------------------------------------------------------------
# A long string of lines in a field that is no Bash command: read as one path
# --------------------------------------------------------------------------

LINE_LENGTHS = {"under-the-limit": 2000, "over-the-limit": 5000, "100000-characters": 100000}


def _lines(world, where, length, reaching):
    lines = [f"src/app/module_{index % 1000:03}.py" for index in range(length // 22)]
    place = {"first": 0, "in-the-middle": len(lines) // 2, "last": len(lines)}[where]
    lines.insert(place, reaching)
    return limit.holds_no_literal(world, "\n".join(lines))


# A line that is not the first: read as one path, the string names a file of the project. Allowed today at any length.
LATER_LINES = [
    ("a-Write-s-content", "in-the-middle", "under-the-limit"),
    ("a-Write-s-content", "in-the-middle", "over-the-limit"),
    ("a-field-of-an-unknown-tool", "last", "100000-characters"),
]


@pytest.mark.parametrize("field,where,size", LATER_LINES, ids=_ids(LATER_LINES))
def test_a_string_of_lines_in_which_a_later_line_reaches_the_held_out_folder_is_decided_as_today(world, field, where,
                                                                                               size):
    """The check reads the string as one path, not line by line: not refused, under and over the limit. Green today."""
    text = _lines(world, where, LINE_LENGTHS[size], f"{world.link}/{limit.FILE_NAME}")
    tool_name, tool_input = limit.call(world, field, text)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_decided_as_a_whole(
        result, tool_name, limit.ORCHESTRATOR,
        f"a string of lines {size} with a line that reaches the stand-in held-out folder {where}, in {field},")


FIRST_LINE_FIELDS = ("a-Write-s-content", "a-field-of-an-unknown-tool")


@pytest.mark.parametrize("field", FIRST_LINE_FIELDS)
def test_a_string_of_lines_under_the_limit_whose_first_line_reaches_the_held_out_folder_stays_refused(world, field):
    """Read as one path, the string lies below the held-out folder. Green today, stays green."""
    text = _lines(world, "first", LINE_LENGTHS["under-the-limit"], f"{world.relative}/{limit.FILE_NAME}")
    tool_name, tool_input = limit.call(world, field, text)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a string of lines under the limit whose first line reaches the stand-in held-out folder, "
                       f"in {field},")


@pytest.mark.parametrize("field", FIRST_LINE_FIELDS)
def test_a_string_of_lines_over_the_limit_whose_first_line_reaches_is_not_refused_by_the_held_out_check(world, field):
    """The ordered change of point 1: the string is past the limit and holds no literal path. Red today: refused."""
    text = _lines(world, "first", LINE_LENGTHS["over-the-limit"], f"{world.relative}/{limit.FILE_NAME}")
    tool_name, tool_input = limit.call(world, field, text)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_decided_as_a_whole(
        result, tool_name, limit.ORCHESTRATOR,
        f"a string of lines over the limit whose first line would reach the stand-in held-out folder, in {field},")
