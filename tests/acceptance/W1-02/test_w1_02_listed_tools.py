"""W1-02 — the tools the guard lets through without a path judgement (DEC-685).

DEC-685: "Any tool the guard does not know is refused (default-deny), unless it
is a known read-only tool."

"Known" is one explicit list. Beside the tools the guard judges (the three
read tools, the write tools, ``Bash``) it holds seventeen tools that write no
file of the project and run no command themselves (``w1_02_tools_support.LISTED``,
each with its reason; README, tenth batch). Held here, through the hook run as
a process:

- each of them passes for every role, for a session with no role or an unknown
  role, and inside a subagent, exactly as the three read tools do, whatever its
  free text says (the text of every case names an acceptance test and a shell
  write: the tool performs neither);
- each passes while the project is frozen;
- the rules that apply to every call still apply: a call of a listed tool that
  names a held-out path is refused, and the refusal discloses nothing of it;
- a decision on a listed tool changes nothing on disk.

**Green today, and green after the round**: the guard as built lets every tool
through that it does not judge. The file holds what the round must keep.

No id and no failure message carries a held-out path.
"""

from __future__ import annotations

import pytest

import w1_02_protected_support as protected
import w1_02_tools_support as tools


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project with its stand-in files for the module: the cases only ask the guard for decisions."""
    return tools.make_world(tmp_path_factory.mktemp("listed-tools"))


@pytest.fixture(scope="module")
def frozen(hook, tmp_path_factory):
    """The same project with the freeze flag set."""
    return tools.make_world(tmp_path_factory.mktemp("listed-tools-frozen"), frozen=True)


# --------------------------------------------------------------------------
# Let through, for every actor
# --------------------------------------------------------------------------

def test_the_list_is_the_seventeen_tools_of_the_round():
    """The list as the round wrote it; a name added to or taken from it is a change of the order, not of a case."""
    assert sorted(tools.LISTED_TOOLS) == sorted((
        "Agent", "Task", "Skill", "ToolSearch", "WebFetch", "WebSearch", "ListAgents", "SendMessage", "TaskStop",
        "TodoWrite", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet", "AskUserQuestion", "EnterPlanMode",
        "ExitPlanMode"))
    for tool_name, (reason, _) in tools.LISTED.items():
        assert reason.strip(), f"{tool_name} is on the list without its reason"


@pytest.mark.parametrize("who", tools.EVERY_ACTOR)
@pytest.mark.parametrize("tool_name", tools.LISTED_TOOLS)
def test_a_listed_tool_is_let_through_for_every_actor(world, tool_name, who):
    """Every role, no role, an unknown role, a role subagent and a subagent that is no role."""
    result = tools.ask(world, tool_name, tools.listed_input(tool_name), who)
    protected.assert_allowed(result, f"{tool_name} by {who}")


@pytest.mark.parametrize("tool_name", tools.LISTED_TOOLS)
def test_a_listed_tool_with_no_input_is_let_through(world, tool_name):
    """No path judgement: there is no field the decision waits for."""
    for who in ("engineer", "no-role"):
        protected.assert_allowed(tools.ask(world, tool_name, {}, who), f"{tool_name} with an empty input by {who}")


# --------------------------------------------------------------------------
# While frozen
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", tools.SOME + ("untyped-subagent-of-the-engineer",))
@pytest.mark.parametrize("tool_name", tools.LISTED_TOOLS)
def test_a_listed_tool_is_let_through_while_frozen(frozen, tool_name, who):
    """The freeze denies every write; a listed tool writes no file of the project, as a read tool does not."""
    result = tools.ask(frozen, tool_name, tools.listed_input(tool_name), who)
    protected.assert_allowed(result, f"{tool_name} by {who} while frozen")


def test_the_frozen_project_refuses_a_write_and_lets_a_read_through(frozen):
    """The fixture's own premise: the flag is read, and a read tool passes as the listed tools are asked to."""
    edit = tools.ask(frozen, "Edit", tools.edit_input(frozen.path(tools.SOURCE_REL)), "engineer")
    assert edit.decision == "deny", "the fixture project is not frozen: the engineer's Edit was not refused"
    read = tools.ask(frozen, "Read", {"file_path": str(frozen.path(tools.SOURCE_REL))}, "engineer")
    protected.assert_allowed(read, "Read by the engineer while frozen")


# --------------------------------------------------------------------------
# A held-out path in a listed tool's call is refused whatever the tool
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tool_name", tools.LISTED_TOOLS)
def test_a_listed_tool_that_names_a_held_out_path_is_refused(world, tool_name):
    """The rule that applies to every call: the path as literal text in the tool's free text, by the widest role."""
    text = f"Compare the result with {world.listed}/{tools.FILE_NAME} and report."
    result = tools.ask(world, tool_name, tools.listed_input(tool_name, text), "orchestrator")
    what = f"{tool_name} with the stand-in held-out path in its text"
    protected.assert_refused_by_rule(result, what)
    tools.assert_carries_none_of(result, world.secrets(), what)


HELD_OUT_BY = [(tool_name, who) for tool_name in ("Agent", "TodoWrite", "WebFetch", "SendMessage")
               for who in ("engineer", "no-role", "untyped-subagent-of-the-engineer")]


@pytest.mark.parametrize("tool_name,who", HELD_OUT_BY, ids=[f"{tool}-{who}" for tool, who in HELD_OUT_BY])
def test_a_listed_tool_that_names_a_held_out_path_is_refused_for_another_actor(world, tool_name, who):
    text = f"Compare the result with {world.listed}/{tools.FILE_NAME} and report."
    result = tools.ask(world, tool_name, tools.listed_input(tool_name, text), who)
    what = f"{tool_name} with the stand-in held-out path in its text, by {who}"
    protected.assert_refused_by_rule(result, what)
    tools.assert_carries_none_of(result, world.secrets(), what)


@pytest.mark.parametrize("tool_name", ("Agent", "TodoWrite", "ExitPlanMode"))
def test_a_listed_tool_that_names_a_held_out_path_is_refused_while_frozen(frozen, tool_name):
    text = f"Compare the result with {frozen.listed}/{tools.FILE_NAME} and report."
    result = tools.ask(frozen, tool_name, tools.listed_input(tool_name, text), "orchestrator")
    what = f"{tool_name} with the stand-in held-out path in its text, while frozen"
    protected.assert_refused_by_rule(result, what)
    tools.assert_carries_none_of(result, frozen.secrets(), what)


def test_a_web_fetch_of_a_held_out_file_is_refused(world):
    """The path inside a URL, the one field of a listed tool that can name a file to fetch."""
    result = tools.ask(world, "WebFetch", {"url": f"file://{world.listed}/{tools.FILE_NAME}", "prompt": "summarise"},
                       "orchestrator")
    protected.assert_refused_by_rule(result, "WebFetch of a file of the stand-in held-out folder")
    tools.assert_carries_none_of(result, world.secrets(), "WebFetch of a file of the stand-in held-out folder")


# --------------------------------------------------------------------------
# Nothing on disk changes by a decision
# --------------------------------------------------------------------------

def test_decisions_on_listed_tools_change_nothing_on_disk(hook, tmp_path):
    """The guard decides; it writes nothing git can see and changes no committed file."""
    world = tools.make_world(tmp_path / "world")
    before = tools.tree_state(world.project)
    assert before[0] == "", "the fixture project must start clean"
    for tool_name in tools.LISTED_TOOLS:
        for who in ("engineer", "no-role"):
            result = tools.ask(world, tool_name, tools.listed_input(tool_name), who)
            assert result.decision in ("allow", "deny"), f"the guard gave no decision on {tool_name} by {who}"
    refused = tools.ask(world, "Agent", tools.listed_input("Agent", f"Read {world.listed}."), "orchestrator")
    assert refused.decision == "deny", "the fixture's refused call was not refused"
    tools.assert_tree_unchanged(world.project, before, "the guard's decisions on the listed tools")
