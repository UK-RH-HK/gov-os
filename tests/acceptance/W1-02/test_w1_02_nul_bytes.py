"""W1-02 — a NUL byte in a path or a command is refused wherever it stands (DEC-562).

DEC-562: "A NUL byte in a path or a command is refused wherever it stands
(today a NUL with no tilde before it is allowed and one with a tilde is
refused)."

No file has a NUL byte in its name: a path that carries one names nothing the
guard can judge, and a program may read it as the path before the byte.

Held here, for every role: a NUL byte in the path of the reading tool, in the
search tool's ``path`` and ``glob``, in the Glob tool's ``path`` and
``pattern``, and anywhere in a shell command (at the start, inside a word, at
the end, with and without a tilde, beside a protected file's path and beside an
ordinary path) is not allowed.

**Before the change** (found by running the hook, README):

- the reading tool, the two search tools and the shell **allow** a NUL byte in
  every position asked, with one exception. Those cases hold the hook's own
  refusal (``deny``, exit code 0) and are red;
- the exception: a shell command with a word that is a tilde followed by a NUL
  byte, or with the byte in the target of an output redirect, is refused as the
  guard's own failure (exit code 2). Held as "not allowed"; green;
- a writing tool (Write, Edit, NotebookEdit) with a NUL byte in its path is
  refused as the guard's own failure (exit code 2), for every role. Held as
  "not allowed"; the shape is not held; green.

The text a search looks for (the search tool's ``pattern``) is no path: no case.
"""

from __future__ import annotations

import os

import pytest

import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_round_support as rnd
import w1_02_support as support

NUL = "\x00"
WIDEST = rnd.WIDEST


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project and its copies for the module: the cases only ask the guard for decisions."""
    return rnd.make_world(tmp_path_factory.mktemp("nul-bytes"))


def _inside(text, back=4):
    """``text`` with a NUL byte ``back`` characters before its end."""
    return text[:-back] + NUL + text[-back:]


def _file(world, name):
    return str(world.site("own").path(name))


def _folder(world, name):
    return str(world.site("own").folder(name))


def _ordinary(world):
    return str(world.project / "README.md")


def _source(world):
    return str(world.project / folders.SOURCE_REL)


# --------------------------------------------------------------------------
# The reading tool and the two search tools: allowed before the change
# --------------------------------------------------------------------------

# label -> builder(world) -> (tool, input)
TOOL_CALLS = {
    # the reading tool's path
    "Read-an-ordinary-path-with-the-byte-at-its-start": lambda w: ("Read", {"file_path": NUL + _ordinary(w)}),
    "Read-an-ordinary-path-with-the-byte-inside": lambda w: ("Read", {"file_path": _inside(_ordinary(w))}),
    "Read-an-ordinary-path-with-the-byte-at-its-end": lambda w: ("Read", {"file_path": _ordinary(w) + NUL}),
    "Read-a-relative-path-with-the-byte-inside": lambda w: ("Read", {"file_path": _inside("README.md")}),
    "Read-the-settings-file-s-path-with-the-byte-at-its-end":
        lambda w: ("Read", {"file_path": _file(w, rnd.SETTINGS) + NUL}),
    "Read-the-settings-file-s-path-with-the-byte-inside":
        lambda w: ("Read", {"file_path": _inside(_file(w, rnd.SETTINGS))}),
    "Read-the-held-out-file-s-path-with-the-byte-at-its-end":
        lambda w: ("Read", {"file_path": _file(w, rnd.HELD) + NUL}),
    "Read-the-held-out-file-s-path-with-the-byte-at-its-start":
        lambda w: ("Read", {"file_path": NUL + _file(w, rnd.HELD)}),
    "Read-the-held-out-file-s-path-with-the-byte-and-more-after-it":
        lambda w: ("Read", {"file_path": _file(w, rnd.HELD) + NUL + ".md"}),
    # the search tool's path and glob
    "Grep-path-with-the-byte-at-its-start": lambda w: ("Grep", {"pattern": "VALUE", "path": NUL + _source(w)}),
    "Grep-path-with-the-byte-inside": lambda w: ("Grep", {"pattern": "VALUE", "path": _inside(_source(w), 2)}),
    "Grep-path-with-the-byte-at-its-end": lambda w: ("Grep", {"pattern": "VALUE", "path": _source(w) + NUL}),
    "Grep-path-the-settings-file-s-folder-with-the-byte-at-its-end":
        lambda w: ("Grep", {"pattern": "VALUE", "path": _folder(w, rnd.SETTINGS) + NUL}),
    "Grep-path-the-held-out-file-with-the-byte-at-its-end":
        lambda w: ("Grep", {"pattern": "VALUE", "path": _file(w, rnd.HELD) + NUL}),
    "Grep-glob-with-the-byte-at-its-start":
        lambda w: ("Grep", {"pattern": "VALUE", "path": _source(w), "glob": NUL + "*.py"}),
    "Grep-glob-with-the-byte-inside":
        lambda w: ("Grep", {"pattern": "VALUE", "path": _source(w), "glob": "*." + NUL + "py"}),
    "Grep-glob-with-the-byte-at-its-end":
        lambda w: ("Grep", {"pattern": "VALUE", "path": _source(w), "glob": "*.py" + NUL}),
    "Grep-glob-the-settings-file-s-name-with-the-byte-at-its-end-from-the-root":
        lambda w: ("Grep", {"pattern": "VALUE", "path": str(w.project),
                            "glob": os.path.basename(_file(w, rnd.SETTINGS)) + NUL}),
    "Grep-glob-the-held-out-file-s-name-with-the-byte-at-its-end-and-no-path":
        lambda w: ("Grep", {"pattern": "VALUE", "glob": os.path.basename(_file(w, rnd.HELD)) + NUL}),
    # the Glob tool's path and pattern
    "Glob-path-with-the-byte-at-its-start": lambda w: ("Glob", {"pattern": "*.py", "path": NUL + _source(w)}),
    "Glob-path-with-the-byte-inside": lambda w: ("Glob", {"pattern": "*.py", "path": _inside(_source(w), 2)}),
    "Glob-path-with-the-byte-at-its-end": lambda w: ("Glob", {"pattern": "*.py", "path": _source(w) + NUL}),
    "Glob-path-the-held-out-file-s-folder-with-the-byte-at-its-end":
        lambda w: ("Glob", {"pattern": "*", "path": _folder(w, rnd.HELD) + NUL}),
    "Glob-pattern-with-the-byte-at-its-start": lambda w: ("Glob", {"pattern": NUL + "*.py", "path": _source(w)}),
    "Glob-pattern-with-the-byte-inside": lambda w: ("Glob", {"pattern": "**/*." + NUL + "py", "path": _source(w)}),
    "Glob-pattern-with-the-byte-at-its-end": lambda w: ("Glob", {"pattern": "**/*.py" + NUL}),
    "Glob-pattern-the-settings-file-s-path-with-the-byte-at-its-end":
        lambda w: ("Glob", {"pattern": _file(w, rnd.SETTINGS) + NUL}),
    "Glob-pattern-the-held-out-file-s-name-with-the-byte-at-its-end":
        lambda w: ("Glob", {"pattern": "**/" + os.path.basename(_file(w, rnd.HELD)) + NUL, "path": str(w.project)}),
}


@pytest.mark.parametrize("call", sorted(TOOL_CALLS))
def test_a_nul_byte_in_a_path_or_a_glob_of_a_reading_tool_is_refused(world, call):
    """Point 4: the reading tool's path, the search tool's ``path`` and ``glob``, the Glob tool's ``path`` and ``pattern``."""
    tool_name, tool_input = TOOL_CALLS[call](world)
    result = folders.ask(world, tool_name, tool_input, WIDEST)
    protected.assert_refused_by_rule(result, f"{call} (a NUL byte)")


# --------------------------------------------------------------------------
# The shell: allowed before the change, but for a tilde word that holds the byte
# --------------------------------------------------------------------------

COMMANDS = {
    "the-byte-at-the-start-of-the-command": lambda w: NUL + "ls -la",
    "the-byte-inside-a-word": lambda w: "ls -l" + NUL + "a",
    "the-byte-at-the-end-of-the-command": lambda w: "ls -la" + NUL,
    "the-byte-between-two-words": lambda w: "cat" + NUL + " README.md",
    "the-byte-inside-a-relative-path": lambda w: "cat " + _inside("README.md"),
    "the-byte-inside-a-quoted-word": lambda w: "echo 'a" + NUL + "b'",
    "the-byte-in-a-commit-message": lambda w: "git commit -m 'one" + NUL + "two'",
    "the-byte-alone": lambda w: NUL,
    "the-byte-after-an-ordinary-absolute-path": lambda w: "cat " + _ordinary(w) + NUL,
    "the-byte-after-the-settings-file-s-path": lambda w: "cat " + _file(w, rnd.SETTINGS) + NUL,
    "the-byte-inside-the-settings-file-s-path": lambda w: "cat " + _inside(_file(w, rnd.SETTINGS)),
    "the-byte-after-the-held-out-file-s-path": lambda w: "cat " + _file(w, rnd.HELD) + NUL,
    "the-byte-before-the-held-out-file-s-path": lambda w: "cat " + NUL + _file(w, rnd.HELD),
    "the-byte-after-the-held-out-file-s-path-and-more-after-it": lambda w: "cat " + _file(w, rnd.HELD) + NUL + ".md",
    "the-byte-at-the-end-of-a-path-from-the-home-folder": lambda w: "cat ~/notes.md" + NUL,
    "the-byte-before-a-tilde": lambda w: "cat " + NUL + "~/notes.md",
    "the-byte-at-the-end-of-a-command-that-names-the-home-folder-earlier": lambda w: "ls ~ && cat README.md" + NUL,
    "the-byte-after-the-user-level-settings-file-spelled-with-a-tilde":
        lambda w: "cat ~/" + protected.SETTINGS_REL + NUL,
}


@pytest.mark.parametrize("command", sorted(COMMANDS))
def test_a_nul_byte_anywhere_in_a_shell_command_is_refused(world, command):
    """Point 4, the shell: at the start, inside a word, at the end, beside either file's path and an ordinary one."""
    result = folders.ask_bash(world, COMMANDS[command](world), WIDEST)
    protected.assert_refused_by_rule(result, f"a shell command with {command}")


# Refused before the change already, as the guard's own failure (exit code 2): held as "not allowed".
ALREADY_REFUSED = {
    "a-word-that-is-a-tilde-and-the-byte": lambda w: "ls ~" + NUL,
    "a-word-that-is-a-tilde-and-the-byte-after-another-command": lambda w: "ls -la && ls ~" + NUL,
    "the-byte-in-the-target-of-a-redirect": lambda w: "cat README.md > " + w.sandbox.tmpdir.as_posix() + "/out" + NUL,
}


@pytest.mark.parametrize("command", sorted(ALREADY_REFUSED))
def test_a_shell_command_the_guard_already_refuses_for_its_nul_byte_is_still_not_allowed(world, command):
    """Refused today (exit code 2). The shape is not held: the hook's own refusal passes as well."""
    result = folders.ask_bash(world, ALREADY_REFUSED[command](world), WIDEST)
    assert result.decision == "deny", (
        f"a shell command with {command} was let through: decision={result.decision} exit={result.returncode}")


# --------------------------------------------------------------------------
# A writing tool: refused before the change already; no side on the shape
# --------------------------------------------------------------------------

WRITE_PATHS = {
    "the-byte-at-the-end-of-a-scratch-path": lambda w: str(w.project / support.SCRATCH_REL / "notes.md") + NUL,
    "the-byte-inside-a-source-path": lambda w: _inside(str(w.project / "src/gov/guard/decide.py"), 9),
    "the-byte-at-the-start-of-a-path": lambda w: NUL + str(w.project / "docs/notes.md"),
}
WRITERS = (WIDEST, "engineer", folders.NO_ROLE)


@pytest.mark.parametrize("who", WRITERS)
@pytest.mark.parametrize("tool_name", ("Write", "Edit", "NotebookEdit"))
@pytest.mark.parametrize("position", sorted(WRITE_PATHS))
def test_a_nul_byte_in_the_path_of_a_writing_tool_is_not_allowed(world, position, tool_name, who):
    """Refused today for every role (exit code 2). Held: not allowed. Which refusal it is, is not held."""
    tool_input = support.edit_tool_input(tool_name, WRITE_PATHS[position](world))
    result = folders.ask(world, tool_name, tool_input, who)
    assert result.decision == "deny", (
        f"{tool_name} with {position} by '{who}' was let through: decision={result.decision} "
        f"exit={result.returncode}")


# --------------------------------------------------------------------------
# For every role, and what the refusal says
# --------------------------------------------------------------------------

_ROLE_CALLS = ("Read-an-ordinary-path-with-the-byte-inside", "Grep-path-with-the-byte-at-its-end",
               "Glob-pattern-with-the-byte-inside", "Read-the-held-out-file-s-path-with-the-byte-at-its-end")
_ROLE_COMMANDS = ("the-byte-at-the-end-of-the-command", "the-byte-inside-a-word",
                  "the-byte-after-the-settings-file-s-path")
OTHER_ACTORS = rnd.OTHER_ROLES + ("engineer-subagent-of-the-orchestrator",)


@pytest.mark.parametrize("who", OTHER_ACTORS)
@pytest.mark.parametrize("call", _ROLE_CALLS)
def test_a_nul_byte_in_a_reading_tool_is_refused_for_every_role(world, call, who):
    """"For every role": an engineer, the test designer, a session with no role, a role subagent."""
    tool_name, tool_input = TOOL_CALLS[call](world)
    result = folders.ask(world, tool_name, tool_input, who)
    protected.assert_refused_by_rule(result, f"{call} (a NUL byte) by '{who}'")


@pytest.mark.parametrize("who", OTHER_ACTORS)
@pytest.mark.parametrize("command", _ROLE_COMMANDS)
def test_a_nul_byte_in_a_shell_command_is_refused_for_every_role(world, command, who):
    result = folders.ask_bash(world, COMMANDS[command](world), who)
    protected.assert_refused_by_rule(result, f"a shell command with {command} by '{who}'")


def test_a_nul_byte_is_refused_while_the_project_is_frozen_too(hook, tmp_path):
    """A read-only call stays open under a freeze; one with a NUL byte in its path does not."""
    frozen = rnd.make_world(tmp_path / "frozen")
    support.set_freeze(frozen.project)
    result = folders.ask(frozen, "Read", {"file_path": _ordinary(frozen) + NUL}, WIDEST)
    protected.assert_refused_by_rule(result, "Read of an ordinary path with a NUL byte while frozen")
    result = folders.ask(frozen, "Read", {"file_path": _ordinary(frozen)}, WIDEST)
    protected.assert_allowed(result, "Read of the same path with no NUL byte while frozen")


SAID = {
    "Read-the-held-out-file-s-path-with-the-byte-at-its-end": rnd.HELD,
    "Read-the-settings-file-s-path-with-the-byte-inside": rnd.SETTINGS,
    "Grep-path-with-the-byte-at-its-end": rnd.SETTINGS,
    "Glob-pattern-the-held-out-file-s-name-with-the-byte-at-its-end": rnd.HELD,
}


@pytest.mark.parametrize("call", sorted(SAID))
def test_the_refusal_of_a_nul_byte_in_a_tool_call_names_the_rule_and_no_path(world, call):
    """A refusal names the rule and the decision: no path of the call, no value of either file."""
    tool_name, tool_input = TOOL_CALLS[call](world)
    result = folders.ask(world, tool_name, tool_input, WIDEST)
    what = f"{call} (a NUL byte)"
    protected.assert_refused_by_rule(result, what)
    rnd.assert_names_a_rule_and_a_decision(result, what)
    pieces = tuple(piece for value in tool_input.values() for piece in value.split(NUL) if len(piece) > 8)
    rnd.assert_says_nothing(result, world, rnd.ROOT, SAID[call], what, more=pieces)


SAID_COMMANDS = {
    "the-byte-after-the-settings-file-s-path": rnd.SETTINGS,
    "the-byte-before-the-held-out-file-s-path": rnd.HELD,
    "the-byte-in-a-commit-message": rnd.SETTINGS,
}


@pytest.mark.parametrize("command", sorted(SAID_COMMANDS))
def test_the_refusal_of_a_nul_byte_in_a_command_names_the_rule_and_does_not_echo_the_command(world, command):
    text = COMMANDS[command](world)
    result = folders.ask_bash(world, text, WIDEST)
    what = f"a shell command with {command}"
    protected.assert_refused_by_rule(result, what)
    rnd.assert_names_a_rule_and_a_decision(result, what)
    pieces = tuple(piece for piece in text.split(NUL) if len(piece) > 8)
    rnd.assert_says_nothing(result, world, rnd.ROOT, SAID_COMMANDS[command], what, more=pieces)


# --------------------------------------------------------------------------
# What stays allowed: green before and after
# --------------------------------------------------------------------------

WITHOUT_THE_BYTE = {
    "Read-an-ordinary-path": lambda w: ("Read", {"file_path": _ordinary(w)}),
    "Grep-a-source-folder-with-a-glob": lambda w: ("Grep", {"pattern": "VALUE", "path": _source(w), "glob": "*.py"}),
    "Glob-a-source-folder": lambda w: ("Glob", {"pattern": "**/*.py", "path": _source(w)}),
    "a-listing-of-the-root": lambda w: ("Bash", support.bash_tool_input("ls -la")),
    "a-read-of-an-ordinary-file-in-the-shell": lambda w: ("Bash", support.bash_tool_input("cat README.md")),
    "a-search-for-the-two-characters-backslash-zero":
        lambda w: ("Grep", {"pattern": "\\0", "path": _source(w), "glob": "*.py"}),
    "a-shell-command-that-spells-the-byte-as-an-escape":
        lambda w: ("Bash", support.bash_tool_input("printf 'a\\0b' | wc -c")),
    "a-listing-of-names-separated-by-the-byte": lambda w: ("Bash", support.bash_tool_input("git ls-files -z src")),
}


@pytest.mark.parametrize("who", (WIDEST, folders.NO_ROLE))
@pytest.mark.parametrize("call", sorted(WITHOUT_THE_BYTE))
def test_the_same_calls_with_no_nul_byte_stay_allowed(world, call, who):
    """The neighbours of the refused calls, and commands that only spell the byte (``\\0``, ``-z``): as today."""
    tool_name, tool_input = WITHOUT_THE_BYTE[call](world)
    result = folders.ask(world, tool_name, tool_input, who)
    protected.assert_allowed(result, f"{call} by '{who}'")
