"""W1-02 — a tool the guard does not know is refused (DEC-685).

DEC-685: "the guard answering allow for a tool it does not know breaks its
default-deny design (W1-02) ... Any tool the guard does not know is refused
(default-deny), unless it is a known read-only tool."

Held here, through the hook run as a process on a hook input:

- **a made-up tool name** is refused for every role, the orchestrator
  included, whatever its input holds: a file path inside what the role may
  write, a command, or nothing;
- **every name that begins ``mcp__``** is refused;
- **the tools of the installed CLI that run a command or take a path and are
  not judged** are refused by name, not judged: ``Monitor`` with a harmless
  command too, ``Artifact``, ``Workflow``, the two worktree tools, and the
  others the round names (``w1_02_tools_support.REFUSED_BY_NAME``);
- **a name near a known one** (another case, a space, a trailing newline or
  NUL byte, more letters) is none of the known tools and passes neither as the
  listed tool nor as the judged one;
- **an empty name, or none**, is not let through (the guard's report of its
  own failure stands);
- the refusal **names the tool as it was sent and says it is not known**;
- **frozen or not**, the refusal stands;
- with **a held-out path** in the call it is refused, and the refusal does not
  disclose the path (which of the two reasons it carries is left open);
- a decision changes **nothing on disk**.

**Red today**: the guard answers allow for every tool name it does not judge.
Green today: an empty name or none (exit code 2), and a call that names a
held-out path (refused whatever the tool).

A case's id names a tool by a label where the name holds a character an id
should not carry. No id and no failure message carries a held-out path.
"""

from __future__ import annotations

import pytest

import w1_02_protected_support as protected
import w1_02_support as support
import w1_02_tools_support as tools

MADE_UP = tools.MADE_UP


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project with its stand-in files for the module: the cases only ask the guard for decisions."""
    return tools.make_world(tmp_path_factory.mktemp("unknown-tools"))


@pytest.fixture(scope="module")
def frozen(hook, tmp_path_factory):
    """The same project with the freeze flag set."""
    return tools.make_world(tmp_path_factory.mktemp("unknown-tools-frozen"), frozen=True)


# --------------------------------------------------------------------------
# A made-up name, whatever its input holds
# --------------------------------------------------------------------------

# label -> builder(world, who) -> input
MADE_UP_INPUTS = {
    "a-file-path-the-role-may-write": lambda w, who: {"file_path": str(w.own_write(who)), "content": "VALUE = 2\n"},
    "a-command": lambda w, who: {"command": "ls -la", "description": "list the folder"},
    "nothing": lambda w, who: {},
}


@pytest.mark.parametrize("who", tools.EVERY_ACTOR)
@pytest.mark.parametrize("holds", sorted(MADE_UP_INPUTS))
def test_a_made_up_tool_is_refused_whatever_its_input_holds(world, holds, who):
    """Line 2: every role, the orchestrator included; the path a role may write buys nothing."""
    result = tools.ask(world, MADE_UP, MADE_UP_INPUTS[holds](world, who), who)
    tools.assert_refused_for(who, result, MADE_UP, f"{MADE_UP} with {holds} by {who}")


def test_the_file_path_of_the_made_up_tool_s_case_is_one_the_role_may_edit(world):
    """The premise of the case above: with ``Edit`` the same path is let through for each role that may write."""
    for who in tools.DECLARED:
        result = tools.ask(world, "Edit", tools.edit_input(world.own_write(who)), who)
        protected.assert_allowed(result, f"Edit of the file the case names for {who}")


# --------------------------------------------------------------------------
# Every name that begins mcp__
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", tools.EVERY_ACTOR)
@pytest.mark.parametrize("tool_name", sorted(tools.MCP_TOOLS))
def test_a_tool_of_an_mcp_server_is_refused(world, tool_name, who):
    """Line 2: a file server's write, a note, an issue: the guard cannot know what such a tool does."""
    result = tools.ask(world, tool_name, tools.MCP_TOOLS[tool_name](world), who)
    tools.assert_refused_for(who, result, tool_name, f"{tool_name} by {who}")


@pytest.mark.parametrize("tool_name", ("mcp__", "mcp__Read", "mcp__claude__Edit", "mcp__guard__Agent"))
def test_an_mcp_name_that_ends_in_a_known_tool_s_name_is_refused(world, tool_name):
    """Line 2: "every name that begins ``mcp__``", whatever follows."""
    for who in ("orchestrator", "engineer"):
        known = tool_name.rsplit("_", 1)[-1] or "Read"
        result = tools.ask(world, tool_name, tools.input_of_the_known_tool(world, known, who), who)
        tools.assert_refused_as_not_known(result, tool_name, f"{tool_name} by {who}")


# --------------------------------------------------------------------------
# The tools refused by name
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", tools.SOME)
@pytest.mark.parametrize("label", sorted(tools.REFUSED_BY_NAME))
def test_a_tool_that_runs_a_command_or_takes_a_path_and_is_not_judged_is_refused(world, label, who):
    """Line 2: refused, not judged: by its name, with the input the tool takes."""
    tool_name, build = tools.REFUSED_BY_NAME[label]
    result = tools.ask(world, tool_name, build(world), who)
    tools.assert_refused_for(who, result, tool_name, f"{label} by {who}")


@pytest.mark.parametrize("who", [who for who in tools.EVERY_ACTOR if who not in tools.SOME])
def test_monitor_with_a_harmless_command_is_refused_for_every_role(world, who):
    """Line 2: ``Monitor`` runs a shell command from a ``command`` field; no command makes it a judged tool."""
    tool_name, build = tools.REFUSED_BY_NAME["Monitor-with-a-harmless-command"]
    result = tools.ask(world, tool_name, build(world), who)
    tools.assert_refused_for(who, result, tool_name, f"Monitor with a harmless command by {who}")


def test_the_same_command_and_the_same_file_are_let_through_with_the_judged_tools(world):
    """The premise: it is the tool's name that is refused, not what the call carries."""
    bash = tools.ask(world, "Bash", support.bash_tool_input("echo ready"), "engineer")
    protected.assert_allowed(bash, "Bash with the harmless command of the Monitor case, by the engineer")
    read = tools.ask(world, "Read", {"file_path": str(world.path("docs/notes.md"))}, "engineer")
    protected.assert_allowed(read, "Read of the file of the Artifact case, by the engineer")


# --------------------------------------------------------------------------
# A name near a known one
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", tools.SOME)
@pytest.mark.parametrize("label", sorted(tools.NEAR_MISSES))
def test_a_name_that_differs_from_a_known_one_by_case_space_or_letters_is_refused(world, label, who):
    """Line 2: it is not the known tool: it passes neither as the listed tool nor as the judged one."""
    tool_name, known = tools.NEAR_MISSES[label]
    result = tools.ask(world, tool_name, tools.input_of_the_known_tool(world, known, who), who)
    tools.assert_refused_for(who, result, tool_name, f"the name '{label}' by {who}")


@pytest.mark.parametrize("who", tools.SOME)
@pytest.mark.parametrize("label", sorted(tools.NEAR_MISSES_UNPRINTABLE))
def test_a_name_with_a_trailing_newline_or_nul_byte_is_refused(world, label, who):
    """Line 2: refused, by a rule or as an input the guard cannot use; what the reason shows of it is left open."""
    tool_name, known = tools.NEAR_MISSES_UNPRINTABLE[label]
    result = tools.ask(world, tool_name, tools.input_of_the_known_tool(world, known, who), who)
    tools.assert_refused(result, f"the name '{label}' by {who}")


def test_the_inputs_of_the_near_names_are_let_through_under_the_known_names(world):
    """The premise of the two cases above, for the actors that may use the known tool."""
    for known in ("Edit", "Read", "Bash", "Agent", "TodoWrite"):
        for who in ("orchestrator", "engineer"):
            result = tools.ask(world, known, tools.input_of_the_known_tool(world, known, who), who)
            protected.assert_allowed(result, f"{known} with the input of the near names' cases, by {who}")
    read = tools.ask(world, "Read", tools.input_of_the_known_tool(world, "Read", "no-role"), "no-role")
    protected.assert_allowed(read, "Read with the input of the near names' cases, by a session with no role")


# --------------------------------------------------------------------------
# An empty name, or none
# --------------------------------------------------------------------------

# label -> the value of ``tool_name`` in the hook input
NO_USABLE_NAME = {
    "an-empty-name": "",
    "a-name-that-is-null": None,
    "a-name-that-is-a-number": 5,
    "a-name-that-is-a-list": ["Read"],
    "a-name-that-is-a-mapping": {"name": "Read"},
}


@pytest.mark.parametrize("who", tools.SOME)
@pytest.mark.parametrize("label", sorted(NO_USABLE_NAME))
def test_a_call_with_no_usable_tool_name_is_not_let_through(world, label, who):
    """Line 2: the guard's refusal of such an input as its own failure stands; the case asks only for the refusal."""
    result = tools.ask_named(world, NO_USABLE_NAME[label], {"file_path": str(world.path(tools.SOURCE_REL))}, who)
    tools.assert_refused(result, f"a call with {label} by {who}")


# --------------------------------------------------------------------------
# Frozen or not
# --------------------------------------------------------------------------

# label -> (tool, builder(world, who) -> input)
WHILE_FROZEN = {
    "a-made-up-tool": (MADE_UP, lambda w, who: {}),
    "a-tool-of-an-mcp-server": ("mcp__notes__add", lambda w, who: tools.MCP_TOOLS["mcp__notes__add"](w)),
    "Monitor": ("Monitor", lambda w, who: tools.REFUSED_BY_NAME["Monitor-with-a-harmless-command"][1](w)),
    "edit-in-lower-case": ("edit", lambda w, who: tools.input_of_the_known_tool(w, "Edit", who)),
    "read-in-upper-case": ("READ", lambda w, who: tools.input_of_the_known_tool(w, "Read", who)),
}


@pytest.mark.parametrize("who", tools.SOME)
@pytest.mark.parametrize("label", sorted(WHILE_FROZEN))
def test_a_tool_the_guard_does_not_know_is_refused_while_frozen(frozen, label, who):
    """Line 2: "frozen or not". Which reason the refusal carries while frozen is left open."""
    tool_name, build = WHILE_FROZEN[label]
    result = tools.ask(frozen, tool_name, build(frozen, who), who)
    tools.assert_refused(result, f"{label} by {who} while frozen")


# --------------------------------------------------------------------------
# With a held-out path in the call
# --------------------------------------------------------------------------

# label -> (tool, builder(world) -> input that names the stand-in held-out folder)
WITH_A_HELD_OUT_PATH = {
    "a-made-up-tool-with-the-path-in-a-field": (MADE_UP, lambda w: {"target": f"{w.listed}/{tools.FILE_NAME}"}),
    "a-made-up-tool-with-a-link-to-it-in-a-field": (MADE_UP, lambda w: {"target": f"{w.link}/{tools.FILE_NAME}"}),
    "an-mcp-read-of-a-file-of-it": ("mcp__filesystem__read_file", lambda w: {"path": f"{w.listed}/{tools.FILE_NAME}"}),
    "an-mcp-tool-with-the-path-in-nested-text":
        ("mcp__notes__add", lambda w: {"note": {"title": "a note", "body": f"see {w.listed}."}}),
    "Monitor-with-a-command-that-reads-it":
        ("Monitor", lambda w: {"command": f"cat {w.listed}/{tools.FILE_NAME}", "description": "wait"}),
    "Artifact-with-a-file-of-it": ("Artifact", lambda w: {"file_path": f"{w.listed}/{tools.FILE_NAME}"}),
    "Workflow-with-a-script-of-it": ("Workflow", lambda w: {"scriptPath": f"{w.listed}/{tools.FILE_NAME}"}),
}


@pytest.mark.parametrize("who", ("orchestrator", "no-role"))
@pytest.mark.parametrize("label", sorted(WITH_A_HELD_OUT_PATH))
def test_a_tool_the_guard_does_not_know_that_names_a_held_out_path_is_refused_and_discloses_nothing(world, label,
                                                                                                    who):
    """The order with the older rules is left open: a refusal, and nothing of the path in anything the hook wrote."""
    tool_name, build = WITH_A_HELD_OUT_PATH[label]
    result = tools.ask(world, tool_name, build(world), who)
    tools.assert_refused(result, f"{label} by {who}")
    tools.assert_carries_none_of(result, (str(world.listed), str(world.link), protected.HELD_REL),
                                 f"{label} by {who}")


# --------------------------------------------------------------------------
# Nothing on disk changes by a decision
# --------------------------------------------------------------------------

def test_decisions_on_tools_the_guard_does_not_know_change_nothing_on_disk(hook, tmp_path):
    """The guard decides; it writes nothing git can see and changes no committed file."""
    world = tools.make_world(tmp_path / "world")
    before = tools.tree_state(world.project)
    assert before[0] == "", "the fixture project must start clean"
    calls = [(MADE_UP, MADE_UP_INPUTS["a-file-path-the-role-may-write"](world, "engineer")),
             (MADE_UP, {"command": "rm -rf src"}),
             ("mcp__filesystem__write_file", tools.MCP_TOOLS["mcp__filesystem__write_file"](world)),
             ("edit", tools.edit_input(world.path(tools.SOURCE_REL)))]
    calls += [(tool_name, build(world)) for tool_name, build in tools.REFUSED_BY_NAME.values()]
    for tool_name, tool_input in calls:
        for who in ("engineer", "orchestrator", "no-role"):
            result = tools.ask(world, tool_name, tool_input, who)
            assert result.decision in ("allow", "deny"), f"the guard gave no decision on {tool_name} by {who}"
    tools.assert_tree_unchanged(world.project, before, "the guard's decisions on tools it does not know")
