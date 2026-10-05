"""W1-47 -- the guard denies a tool call whose input names the oracle path.

KPI success 4: "The guard denies any tool call whose input names the oracle path
(a Read, Grep, Glob or Bash call, or any other tool), for every role, the
orchestrator included; the guard takes the path from
governance/project/held-out.yaml, and the guard's behaviour is tested against a
stand-in path, never the qualification oracle (DEC-162) [CAP-49.c]".
KPI failure 2: "Any tool call whose input names the oracle path is allowed,
whatever the tool and whatever the call does (a read, a listing, a search, a
write or a command), in a session started in the repository root".

Every test works in a fixture project whose ``held-out.yaml`` names a stand-in
directory: a file the test builds itself, with ``held_out_paths`` holding a
made-up path (``w1_47_support.configure_stand_in``, DEC-218). The committed
file of this repository plays no part. No call is ever made: the hook is asked
for its decision and nothing else happens.

This file holds the plain forms: the input carries the configured absolute
path, word for word, as a path of its own or as the beginning of a path under
it. In a Bash command that is a word of the command, bare or quoted. In any
other tool it is the whole value of an input field, at any depth. The forms
DEC-215 adds (the path inside free text or code, a relative path, ``..``,
``~``, ``$HOME``, a symbolic link) and its exception are in
``test_w1_47_oracle_naming.py``; what the guard does with a missing or broken
``held-out.yaml`` is in ``test_w1_47_oracle_config.py``.
"""

from __future__ import annotations

import pytest

import w1_47_support as support

ORCHESTRATOR = support.EVERY_ACTOR[support.ORCHESTRATOR]
ENGINEER = support.EVERY_ACTOR[support.ENGINEER]

# name: (tool, input for a stand-in directory ``p`` and a directory ``tmp`` outside it).
READS = {
    "Read-the-directory": ("Read", lambda p, tmp: {"file_path": f"{p}"}),
    "Read-a-file": ("Read", lambda p, tmp: {"file_path": f"{p}/answers.md"}),
    "Read-a-nested-file": ("Read", lambda p, tmp: {"file_path": f"{p}/cases/test_hidden.py", "limit": 20}),
    "Grep-in-the-directory": ("Grep", lambda p, tmp: {"pattern": "def test", "path": f"{p}"}),
    "Grep-in-a-file": ("Grep", lambda p, tmp: {"pattern": "answers", "path": f"{p}/answers.md",
                                              "output_mode": "content"}),
    "Glob-in-the-directory": ("Glob", lambda p, tmp: {"pattern": "**/*.py", "path": f"{p}"}),
    "Glob-pattern-under-the-directory": ("Glob", lambda p, tmp: {"pattern": f"{p}/**/*.py"}),
}
COMMANDS = {
    "Bash-ls": "ls {p}",
    "Bash-ls-trailing-slash": "ls -la {p}/",
    "Bash-cat": "cat {p}/answers.md",
    "Bash-cat-quoted": "cat \"{p}/answers.md\"",
    "Bash-head-single-quoted": "head -5 '{p}/cases/test_hidden.py'",
    "Bash-grep": "grep -rn test {p}",
    "Bash-find": "find {p} -name '*.py'",
    "Bash-cd": "cd {p} && ls",
    "Bash-after-another-command": "git status --porcelain && ls {p}",
    "Bash-in-a-pipeline": "cat {p}/answers.md | wc -l",
    "Bash-copy-out": "cp -r {p} {tmp}/copy",
    "Bash-archive": "tar -czf {tmp}/held-out.tgz {p}",
    "Bash-redirect-into": "echo changed > {p}/new.txt",
    "Bash-touch": "touch {p}/new.txt",
    "Bash-remove": "rm -rf {p}",
    "Bash-input-redirect": "wc -l < {p}/answers.md",
}
BASH = {name: ("Bash", lambda p, tmp, text=text: support.bash_input(text.format(p=p, tmp=tmp)))
        for name, text in COMMANDS.items()}
OTHER_TOOLS = {
    "Write": ("Write", lambda p, tmp: support.write_input("Write", f"{p}/new.md")),
    "Edit": ("Edit", lambda p, tmp: support.write_input("Edit", f"{p}/answers.md")),
    "NotebookEdit": ("NotebookEdit", lambda p, tmp: support.write_input("NotebookEdit", f"{p}/notes.ipynb")),
    "MCP-read-file": ("mcp__filesystem__read_file", lambda p, tmp: {"path": f"{p}/answers.md"}),
    "MCP-list-directory": ("mcp__filesystem__list_directory", lambda p, tmp: {"path": f"{p}"}),
    "MCP-list-of-paths": ("mcp__filesystem__read_multiple_files",
                          lambda p, tmp: {"paths": [f"{tmp}/other.md", f"{p}/answers.md"]}),
    "MCP-nested-field": ("mcp__search__query", lambda p, tmp: {"query": "test", "options": {"root": f"{p}"}}),
    "a-tool-added-later": ("ToolAddedAfterThisTicket", lambda p, tmp: {"target": f"{p}/answers.md"}),
}
CALLS = {**READS, **BASH, **OTHER_TOOLS}
# One call of each kind, for the second place of the stand-in.
REPRESENTATIVE = ("Read-a-file", "Grep-in-the-directory", "Glob-in-the-directory", "Bash-ls", "Bash-cat-quoted",
                  "Bash-redirect-into", "Write", "Edit", "MCP-read-file")


def _ask(guard, project, sandbox, stand_in, name, who):
    tool_name, build = CALLS[name]
    return tool_name, guard(project, tool_name, build(stand_in, sandbox.elsewhere), who)


# --------------------------------------------------------------------------
# Denied: every tool, every role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", sorted(support.EVERY_SESSION))
@pytest.mark.parametrize("name", sorted(CALLS))
def test_a_call_that_names_the_oracle_path_is_denied(project, sandbox, guard, temp_stand_in, name, who):
    """KPI success 4, failure 2 [CAP-49.c]: a read, a listing, a search, a write or a command, by every role."""
    tool_name, result = _ask(guard, project, sandbox, temp_stand_in, name, support.EVERY_SESSION[who])
    support.assert_denied_by_rule(result, f"{name} ({tool_name}) on the stand-in oracle path by {who}")


@pytest.mark.parametrize("who", (support.ORCHESTRATOR, support.ENGINEER))
@pytest.mark.parametrize("name", REPRESENTATIVE)
def test_a_call_that_names_the_oracle_path_is_denied_wherever_the_path_is(project, sandbox, guard, stand_in, name,
                                                                         who):
    """KPI success 4: a path inside the repository (the orchestrator's wide scope) and one in the scratch set."""
    tool_name, result = _ask(guard, project, sandbox, stand_in, name, support.EVERY_SESSION[who])
    support.assert_denied_by_rule(result, f"{name} ({tool_name}) on the stand-in oracle path by {who}")


@pytest.mark.parametrize("who", sorted(support.SUBAGENTS))
@pytest.mark.parametrize("name", ("Read-a-file", "Grep-in-the-directory", "Bash-cat"))
def test_a_subagent_s_call_that_names_the_oracle_path_is_denied(project, sandbox, guard, temp_stand_in, name, who):
    """KPI failure 2: "a session started in the repository root" includes the subagents it starts."""
    tool_name, result = _ask(guard, project, sandbox, temp_stand_in, name, support.SUBAGENTS[who])
    support.assert_denied_by_rule(result, f"{name} ({tool_name}) on the stand-in oracle path by {who}")


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
def test_a_read_of_the_oracle_path_is_denied_in_every_permission_mode(project, guard, temp_stand_in, mode):
    """KPI failure 2: no permission mode lets the call through."""
    result = guard(project, "Read", {"file_path": f"{temp_stand_in}/answers.md"}, ORCHESTRATOR, mode=mode)
    support.assert_denied_by_rule(result, f"Read on the stand-in oracle path in {mode} mode")


def test_a_read_of_the_oracle_path_is_denied_while_frozen(project, guard, temp_stand_in):
    """The freeze flag stops writes and leaves reading open (W1-02); the oracle stays hidden all the same."""
    flag = project / ".gov-runtime" / "freeze"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("FROZEN owner 2026-10-05T00:00:00Z\n", encoding="utf-8")   # the marker line (DEC-402)
    result = guard(project, "Read", {"file_path": f"{temp_stand_in}/answers.md"}, ENGINEER)
    support.assert_denied_by_rule(result, "Read on the stand-in oracle path by the engineer while frozen")


# --------------------------------------------------------------------------
# The path comes from held-out.yaml
# --------------------------------------------------------------------------

def test_the_guard_takes_the_path_from_the_configuration(project, sandbox, guard):
    """KPI success 4: change the configured path and the guard hides the new one and no longer the old one."""
    first = support.make_stand_in(sandbox.tmpdir / "first-stand-in")
    second = support.make_stand_in(sandbox.tmpdir / "second-stand-in")

    support.configure_stand_in(project, first)
    result = guard(project, "Read", {"file_path": f"{first}/answers.md"}, ORCHESTRATOR)
    support.assert_denied_by_rule(result, "Read on the configured stand-in")
    result = guard(project, "Read", {"file_path": f"{second}/answers.md"}, ORCHESTRATOR)
    support.assert_allowed(result, "Read on a directory the configuration does not name")

    support.configure_stand_in(project, second)
    result = guard(project, "Read", {"file_path": f"{second}/answers.md"}, ORCHESTRATOR)
    support.assert_denied_by_rule(result, "Read on the stand-in, once the configuration names it,")
    result = guard(project, "Read", {"file_path": f"{first}/answers.md"}, ORCHESTRATOR)
    support.assert_allowed(result, "Read on the directory the configuration no longer names")


@pytest.mark.parametrize("who", (support.ORCHESTRATOR, support.ENGINEER))
def test_every_path_of_the_list_is_hidden(project, sandbox, guard, who):
    """DEC-218: ``held_out_paths`` is a list; the guard hides each path of it, and nothing beside them."""
    first = support.make_stand_in(sandbox.tmpdir / "first-stand-in")
    second = support.make_stand_in(sandbox.elsewhere / "second-stand-in")
    third = support.make_stand_in(sandbox.tmpdir / "not-in-the-list")
    support.configure_stand_in(project, first, second)
    actor = support.EVERY_SESSION[who]
    for position, directory in (("first", first), ("second", second)):
        result = guard(project, "Read", {"file_path": f"{directory}/answers.md"}, actor)
        support.assert_denied_by_rule(result, f"Read on the {position} of two stand-in paths by {who}")
        result = guard(project, "Bash", support.bash_input(f"cat {directory}/answers.md"), actor)
        support.assert_denied_by_rule(result, f"Bash cat on the {position} of two stand-in paths by {who}")
    result = guard(project, "Read", {"file_path": f"{third}/answers.md"}, actor)
    support.assert_allowed(result, f"Read on a directory the list does not hold, by {who},")


def test_the_oracle_path_is_hidden_through_the_committed_settings(wired, live, live_sandbox):
    """KPI success 4: the rule is live in this repository, through the commands its settings register."""
    stand_in = support.make_stand_in(live_sandbox.tmpdir / "held-out-stand-in")
    support.configure_stand_in(wired, stand_in)
    for tool_name, tool_input in (
        ("Read", {"file_path": f"{stand_in}/answers.md"}),
        ("Grep", {"pattern": "answers", "path": f"{stand_in}"}),
        ("Bash", support.bash_input(f"ls {stand_in}")),
    ):
        result = live(wired, tool_name, tool_input, support.ORCHESTRATOR)
        assert result.ran, f"the {tool_name} call reached no registered PreToolUse command: {result.describe()}"
        assert result.decision == "deny", (
            f"{tool_name} on the stand-in oracle path was not denied by the registered commands: "
            f"{result.describe()}"
        )


# --------------------------------------------------------------------------
# What stays open
# --------------------------------------------------------------------------

UNRELATED = {
    "Read": ("Read", lambda project, tmp: {"file_path": f"{project}/README.md"}),
    "Grep": ("Grep", lambda project, tmp: {"pattern": "guard", "path": f"{project}"}),
    "Glob": ("Glob", lambda project, tmp: {"pattern": "**/*.py", "path": f"{project}/src"}),
    "Bash-ls": ("Bash", lambda project, tmp: support.bash_input("ls -la")),
    "Bash-cat": ("Bash", lambda project, tmp: support.bash_input(f"cat {project}/README.md")),
    "Read-elsewhere": ("Read", lambda project, tmp: {"file_path": f"{tmp}/other.md"}),
    "MCP": ("mcp__filesystem__read_file", lambda project, tmp: {"path": f"{project}/README.md"}),
}


@pytest.mark.parametrize("who", sorted(support.EVERY_SESSION))
@pytest.mark.parametrize("name", sorted(UNRELATED))
def test_a_call_that_names_another_path_stays_allowed(project, sandbox, guard, temp_stand_in, name, who):
    """The rule hides one path. With it configured, reading anything else is as open as before."""
    tool_name, build = UNRELATED[name]
    result = guard(project, tool_name, build(project, sandbox.elsewhere), support.EVERY_SESSION[who])
    support.assert_allowed(result, f"{name} ({tool_name}) on a path that is not the oracle's, by {who},")
