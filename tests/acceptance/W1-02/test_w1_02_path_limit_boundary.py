"""W1-02 — the held-out check resolves no string past the system path limit (DEC-574, point 1).

DEC-574: "The held-out check skips path resolution for any string longer than
the system path limit, and keeps the literal substring check."

The held-out check (W1-47, DEC-215) refuses a call when a string of its input
holds a held-out path as literal text, or when a string, read as a path,
reaches one without writing it out. Held here, through the hook run as a
process on a hook input, in a temporary project with a stand-in held-out file
that lists a stand-in held-out folder:

- **the boundary.** A string that reaches the stand-in held-out folder without
  holding its path, built to an exact length, in every field that is no path
  field. Just under and at the limit: refused by the held-out check, as today
  (green today). Just over: **not refused by the held-out check**, and decided
  as the same call with a short string is (red today: refused);
- **the limit is the system's own**, counted in characters of the string, and a
  string is past it only if it is past it as written **and** as the guard
  expands it (the home folder's short form; a home variable in a word of a Bash
  command). The readings are in the README; each is held by a case;
- **a path field of a file tool** longer than the guard resolves stays refused
  before the held-out check is asked, with a reason of its own (green today).

No id and no failure message carries a path or a command.
"""

from __future__ import annotations

import pytest

import w1_02_limit_support as limit
import w1_02_protected_support as protected
import w1_02_round_support as rnd
import w1_02_support as support

LIMIT = limit.LIMIT
LENGTHS = {"just-under-the-limit": LIMIT - 1, "at-the-limit": LIMIT, "just-over-the-limit": LIMIT + 1}
FORMS = {
    "through-a-symbolic-link": limit.via_link,
    "through-dot-dot-from-the-session-s-folder": limit.via_dots,
}
# Every field that is no path field, each with one form; just over the limit, the two most used fields with the
# other form too. Just under the limit: every second field.
FIELD_FORMS = [
    ("a-Write-s-content", "through-a-symbolic-link"),
    ("an-Edit-s-old-string", "through-dot-dot-from-the-session-s-folder"),
    ("an-Edit-s-new-string", "through-a-symbolic-link"),
    ("a-field-of-an-unknown-tool", "through-dot-dot-from-the-session-s-folder"),
    ("a-list-inside-the-input", "through-a-symbolic-link"),
    ("a-mapping-inside-the-input", "through-dot-dot-from-the-session-s-folder"),
    (limit.BASH_WORD, "through-a-symbolic-link"),
]
BOTH_FORMS = [("a-Write-s-content", "through-dot-dot-from-the-session-s-folder"),
              (limit.BASH_WORD, "through-dot-dot-from-the-session-s-folder")]

RESOLVED = [(field, form, "just-under-the-limit") for field, form in FIELD_FORMS[::2]]
RESOLVED += [(field, form, "at-the-limit") for field, form in FIELD_FORMS]
SKIPPED = [(field, form, "just-over-the-limit") for field, form in FIELD_FORMS + BOTH_FORMS]


def _ids(rows):
    return ["-".join(str(part) for part in row) for row in rows]


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project with its stand-in files for the module: the cases only ask the guard for decisions."""
    return limit.make_world(tmp_path_factory.mktemp("path-limit-boundary"))


def _ask(world, field, form, length, who=limit.ORCHESTRATOR):
    text = FORMS[form](world, LENGTHS[length])
    tool_name, tool_input = limit.call(world, field, text)
    return tool_name, text, limit.ask(world, tool_name, tool_input, who)


# --------------------------------------------------------------------------
# The boundary
# --------------------------------------------------------------------------

@pytest.mark.parametrize("field,form,length", RESOLVED, ids=_ids(RESOLVED))
def test_a_string_at_or_under_the_limit_that_reaches_the_held_out_folder_is_refused(world, field, form, length):
    """Point 1: resolved as today. Green today, stays green."""
    _, text, result = _ask(world, field, form, length)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a string {length} that reaches the stand-in held-out folder {form}, in {field},",
        (text[:48], text[-48:]))


@pytest.mark.parametrize("field,form,length", SKIPPED, ids=_ids(SKIPPED))
def test_a_string_just_over_the_limit_is_not_refused_by_the_held_out_check(world, field, form, length):
    """Point 1: no program opens such a string as a path. Red today: refused by the held-out check.

    The guard as a whole then allows each of these for the orchestrator: a write
    of a source file it may write, a tool the guard does not know, a command
    that writes nothing.
    """
    tool_name, _, result = _ask(world, field, form, length)
    limit.assert_decided_as_a_whole(
        result, tool_name, limit.ORCHESTRATOR,
        f"a string {length} that would reach the stand-in held-out folder {form}, in {field},")


# An engineer and a session with no role: the check holds for every role.
OVER_BY_ROLE = [
    ("a-Write-s-content", "through-a-symbolic-link", limit.ENGINEER),
    ("a-Write-s-content", "through-dot-dot-from-the-session-s-folder", limit.NO_ROLE),
    ("a-field-of-an-unknown-tool", "through-a-symbolic-link", limit.NO_ROLE),
    (limit.BASH_WORD, "through-dot-dot-from-the-session-s-folder", limit.ENGINEER),
]
AT_BY_ROLE = [
    ("a-list-inside-the-input", "through-dot-dot-from-the-session-s-folder", limit.ENGINEER),
    (limit.BASH_WORD, "through-a-symbolic-link", limit.NO_ROLE),
]


@pytest.mark.parametrize("field,form,who", OVER_BY_ROLE, ids=_ids(OVER_BY_ROLE))
def test_a_string_just_over_the_limit_is_decided_for_another_role_as_a_short_string_is(world, field, form, who):
    """Red today. A session with no role stays denied a write, by the allow-list and not by the held-out check."""
    tool_name, _, result = _ask(world, field, form, "just-over-the-limit", who)
    limit.assert_decided_as_a_whole(result, tool_name, who, f"a string just over the limit {form}, in {field},")


@pytest.mark.parametrize("field,form,who", AT_BY_ROLE, ids=_ids(AT_BY_ROLE))
def test_a_string_at_the_limit_is_refused_for_another_role(world, field, form, who):
    """Green today, stays green."""
    _, _, result = _ask(world, field, form, "at-the-limit", who)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a string at the limit that reaches the stand-in held-out folder {form}, in {field}, by {who}")


# --------------------------------------------------------------------------
# The limit counts the string as written and as expanded: past it only if past it in both
# --------------------------------------------------------------------------

def test_a_bash_word_over_the_limit_as_written_that_expands_to_a_path_under_it_stays_refused(world):
    """A shell expands the word to a short path that opens a file of the held-out folder. Green today, stays green.

    The hook's ``HOME`` is the root folder, the shortest home there is: each
    written ``${HOME}`` is seven characters and expands to one. Nothing is read
    or written under it by the case.
    """
    below_root = str(world.link).lstrip("/")
    word = limit.holds_no_literal(world, "${HOME}" * 700 + f"{below_root}/{limit.FILE_NAME}")
    assert len(word) > LIMIT and len(word) - 700 * 6 < LIMIT, "the fixture word has not the lengths the case needs"
    result = limit.ask(world, "Bash", support.bash_tool_input("cat " + word), env={"HOME": "/"})
    limit.assert_refused_by_the_held_out_check(
        result, world, "a Bash word over the limit as written that expands to a path under it,", (word[-64:],))


# Under the limit as written, over it once the stand-in home folder stands in the place of its short form.
UNDER_AS_WRITTEN = {
    "a-home-variable-in-a-word-of-a-Bash-command": (limit.BASH_WORD, "$HOME/"),
    "the-home-folder-s-short-form-in-a-Write-s-content": ("a-Write-s-content", "~/"),
    "the-home-folder-s-short-form-in-a-field-of-an-unknown-tool": ("a-field-of-an-unknown-tool", "~/"),
}


@pytest.mark.parametrize("shape", sorted(UNDER_AS_WRITTEN))
def test_a_string_under_the_limit_as_written_and_over_it_as_expanded_stays_refused(world, shape):
    """Past the limit only if past it both as written and as expanded. Green today, stays green."""
    field, start = UNDER_AS_WRITTEN[shape]
    text = limit.padded(start, limit.HERE, f"{limit.LINK_NAME}/{limit.FILE_NAME}", LIMIT - 2)
    assert len(text) - len(start) + len(str(world.sandbox.home)) + 1 > LIMIT, "the stand-in home folder is too short"
    tool_name, tool_input = limit.call(world, field, text)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_refused_by_the_held_out_check(result, world, f"'{shape}', under the limit as written,")


OVER_BOTH_WAYS = {
    "a-home-variable-in-a-word-of-a-Bash-command": (limit.BASH_WORD, "$HOME/"),
    "the-home-folder-s-short-form-in-a-Write-s-content": ("a-Write-s-content", "~/"),
}


@pytest.mark.parametrize("shape", sorted(OVER_BOTH_WAYS))
def test_a_string_over_the_limit_as_written_and_as_expanded_is_not_refused_by_the_held_out_check(world, shape):
    """An expansion keeps no string under the limit that is over it both ways. Red today: refused."""
    field, start = OVER_BOTH_WAYS[shape]
    text = limit.padded(start, limit.HERE, f"{limit.LINK_NAME}/{limit.FILE_NAME}", LIMIT + 1)
    tool_name, tool_input = limit.call(world, field, text)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_decided_as_a_whole(result, tool_name, limit.ORCHESTRATOR,
                                    f"'{shape}', over the limit as written and as expanded,")


# --------------------------------------------------------------------------
# The limit counts characters, and it is the limit of a path, not of one name in it
# --------------------------------------------------------------------------

@pytest.mark.parametrize("field", ("a-Write-s-content", limit.BASH_WORD))
def test_a_string_at_the_limit_in_characters_and_over_it_in_bytes_stays_refused(world, field):
    """Characters, the reading under which fewer strings are past the limit. Green today, stays green."""
    text = limit.via_dots(world, LIMIT, unit="é/../")
    assert len(text.encode("utf-8")) > LIMIT, "the fixture string is not over the limit in bytes"
    tool_name, tool_input = limit.call(world, field, text)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a string at the limit in characters and over it in bytes, in {field},")


@pytest.mark.parametrize("field", ("a-field-of-an-unknown-tool", limit.BASH_WORD))
def test_a_string_under_the_limit_with_one_name_longer_than_a_file_name_may_be_stays_refused(world, field):
    """A string under the path limit is resolved as today whatever its components. Green today, stays green."""
    text = limit.holds_no_literal(world, "x" * 300 + f"/../{world.relative}/{limit.FILE_NAME}")
    tool_name, tool_input = limit.call(world, field, text)
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"a string under the limit with one name of 300 characters, in {field},")


# --------------------------------------------------------------------------
# A path field of a file tool
# --------------------------------------------------------------------------

# label -> builder(long path) -> (tool, input)
PATH_FIELDS = {
    "the-file-path-of-a-Read": lambda long: ("Read", {"file_path": long}),
    "the-file-path-of-a-Write": lambda long: ("Write", {"file_path": long, "content": "VALUE = 2\n"}),
    "the-file-path-of-an-Edit":
        lambda long: ("Edit", {"file_path": long, "old_string": "VALUE = 1", "new_string": "VALUE = 2"}),
    "the-path-of-a-search": lambda long: ("Grep", {"pattern": "VALUE", "path": long}),
    "the-glob-of-a-search": lambda long: ("Grep", {"pattern": "VALUE", "path": "src", "glob": long}),
    "the-path-of-a-Glob": lambda long: ("Glob", {"pattern": "*.py", "path": long}),
    "the-pattern-of-a-Glob": lambda long: ("Glob", {"pattern": long}),
}
LONG_PATHS = [(field, "just-over-the-limit", LIMIT + 1) for field in sorted(PATH_FIELDS)]
LONG_PATHS += [(field, "a-megabyte", limit.MB)
               for field in ("the-file-path-of-a-Write", "the-path-of-a-search")]


@pytest.mark.parametrize("field,size,length", LONG_PATHS, ids=[f"{field}-{size}" for field, size, _ in LONG_PATHS])
def test_a_path_field_longer_than_the_guard_resolves_stays_refused_with_a_reason_of_its_own(world, field, size,
                                                                                           length):
    """Refused before the held-out check is asked, as today (sixth batch). Green today, stays green."""
    long = limit.via_link(world, length)
    tool_name, tool_input = PATH_FIELDS[field](long)
    result = limit.ask_timed(world, tool_name, tool_input)
    what = f"{field} of {size}"
    rnd.assert_refused_in_time(result, what)
    protected.assert_refused_by_rule(result, what)
    reason = protected.reason_of(result)
    assert limit.LONG_PATH_RE.search(reason) and not limit.HELD_OUT_CHECK_RE.search(reason), (
        f"{what} was not refused as a path longer than the guard resolves (DEC-562)")
    rnd.assert_carries_none_of(result, world.secrets() + (long[:48], long[-48:]), what)


@pytest.mark.parametrize("field", ("the-file-path-of-a-Read", "the-path-of-a-search"))
def test_a_path_field_at_the_limit_is_still_resolved_and_refused_by_the_held_out_check(world, field):
    """The system's limit and the longest path the guard resolves in a path field are one value. Green today."""
    tool_name, tool_input = PATH_FIELDS[field](limit.via_link(world, LIMIT))
    result = limit.ask(world, tool_name, tool_input)
    limit.assert_refused_by_the_held_out_check(
        result, world, f"{field} at the limit, which reaches the stand-in held-out folder,")
