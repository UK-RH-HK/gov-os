"""Support code for the DEC-685 cases of W1-02: ``MultiEdit`` is judged like ``Edit``; a tool the guard does not know is refused.

DEC-685: "``MultiEdit`` is judged exactly like ``Edit``, by its file path, for
every role. Any tool the guard does not know is refused (default-deny), unless
it is a known read-only tool."

Everything here is a stand-in in a temporary folder, as in
``w1_02_protected_support``, whose project this module uses: a committed
temporary project with a stand-in settings file and a stand-in held-out file
that lists a stand-in held-out folder (``World.listed``). No file of this
repository is opened, and the held-out file's path is never spelled: it comes
through ``w1_02_protected_support``.

Every decision is asked of the hook, run as a process on a hook input. Nothing
of the guard's code is named or imported here: a tool is known to a case by its
name in the hook input, a decision by the hook's exit code and output.

**The three lists** are the round's order, written out (README, tenth batch):

- ``LISTED``: the tools the guard lets through without a path judgement;
- ``REFUSED_BY_NAME``: the tools of the installed CLI the round refuses by name;
- ``NEAR_MISSES``: names that differ from a known one by case, by a space, by a
  trailing character, or by more letters.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import w1_02_protected_support as protected
import w1_02_support as support

WBS = support.TICKET_WBS_ID
SOURCE_REL = "src/gov/guard/decide.py"                       # the engineer's ticket names it
OUTSIDE_REL = "README.md"                                    # no ticket names it
ACCEPTANCE_REL = f"tests/acceptance/{WBS}/test_fixture.py"   # the independent test designer's alone
ACCEPTANCE_BY_LINK_REL = f"src/gov/guard/acceptance_link/{WBS}/test_fixture.py"
UNIT_REL = "tests/unit/guard/test_decide.py"
SPEC_REL = "docs/spec/feature.md"
SCRATCH_REL = f"{support.SCRATCH_REL}/note.txt"
LINK_NAME = "a-link"
FILE_NAME = "answers.md"

# One ticket per role whose allowed_paths name the acceptance-test folder (the form of
# ``test_a_ticket_that_names_acceptance_tests_still_gives_no_access``).
NAMING_TICKETS = {
    support.ENGINEER: "DAEO-zz97",
    support.ORCHESTRATOR: "DAEO-zz98",
    support.PRODUCT_SPEC: "DAEO-zz99",
}
NAMING_PATHS = ("tests/**", "tests/acceptance/**", ACCEPTANCE_REL)

ACTORS = protected.ACTORS
EVERY_ACTOR = tuple(sorted(ACTORS))
# A session that declares one of the roles, on its main thread or in a role subagent.
DECLARED = ("orchestrator", "engineer", "product-spec", "test-designer", "auditor", "research", "ticket-lead",
            "engineer-subagent-of-the-orchestrator")
# A session that is read-only whatever it asks (KPI success 4, DEC-113).
READ_ONLY = ("no-role", "unknown-role", "untyped-subagent-of-the-engineer")
SOME = ("orchestrator", "engineer", "no-role")

# A file each actor may write with ``Edit`` today (measured, and asserted by the cases that use it); ``None``
# where the actor may write nothing.
OWN_WRITE = {
    "orchestrator": OUTSIDE_REL,
    "engineer": SOURCE_REL,
    "product-spec": SCRATCH_REL,     # on the engineer's ticket of ``ACTORS``: the scratch set only
    "test-designer": ACCEPTANCE_REL,
    "auditor": SCRATCH_REL,
    "research": SCRATCH_REL,
    "ticket-lead": SCRATCH_REL,
    "engineer-subagent-of-the-orchestrator": SCRATCH_REL,
    "no-role": None,
    "unknown-role": None,
    "untyped-subagent-of-the-engineer": None,
}


# --------------------------------------------------------------------------
# The temporary project
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class World:
    project: Path
    sandbox: support.Sandbox
    listed: Path     # the stand-in held-out folder the stand-in held-out file lists
    link: Path       # a symbolic link to it, outside the project
    guarded: protected.Guarded

    @property
    def relative(self):
        """The stand-in held-out folder as a relative path from the project, the session's folder."""
        return os.path.relpath(self.listed, self.project)

    def path(self, rel):
        return self.project / rel

    def own_write(self, who):
        """A file ``who`` may write, or a source file where it may write nothing."""
        return self.project / (OWN_WRITE[who] or SOURCE_REL)

    def secrets(self):
        """What a refusal must not carry: the stand-in held-out path and the ways to it, the held-out file's place."""
        return (str(self.listed), str(self.link), self.relative, protected.HELD_REL,
                os.path.basename(protected.HELD_REL))


def make_world(base, frozen=False):
    """The project of ``w1_02_protected_support`` with three more tickets and a link to the stand-in held-out folder.

    ``frozen`` sets the freeze flag after the commit, the way ``gov pause`` does.
    """
    guarded = protected.make_guarded(Path(base))
    project = guarded.project
    for number, (role, ticket_id) in enumerate(sorted(NAMING_TICKETS.items())):
        text = support.ticket_text(ticket_id=ticket_id, wbs_id=f"W1-9{7 + number}", role=role,
                                   allowed_paths=NAMING_PATHS)
        (project / ".tickets" / f"{ticket_id}.md").write_text(text, encoding="utf-8")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "tickets that name the acceptance-test folder")
    link = guarded.sandbox.elsewhere / LINK_NAME
    link.symlink_to(guarded.listed, target_is_directory=True)
    if frozen:
        support.set_freeze(project)
    return World(project, guarded.sandbox, guarded.listed, link, guarded)


def ask(world, tool_name, tool_input, who):
    """The guard's decision on one call; ``who`` is a name of ``ACTORS`` or (GOV_ROLE, GOV_TICKET, subagent type)."""
    return protected.ask(world.guarded, tool_name, tool_input, who)


def ask_named(world, tool_name, tool_input, who):
    """As ``ask``, for a ``tool_name`` that is no string or that the JSON form must carry as it is."""
    role, ticket, subagent = ACTORS[who] if isinstance(who, str) else who
    return support.run_hook(world.project, tool_name, tool_input, world.sandbox, role=role, ticket=ticket,
                            subagent=subagent)


# --------------------------------------------------------------------------
# Edit and MultiEdit
# --------------------------------------------------------------------------

def edit_input(path, **more):
    data = {"file_path": str(path), "old_string": "VALUE = 1", "new_string": "VALUE = 2"}
    data.update(more)
    return data


def multiedit_input(path, edits=None):
    """The input of ``MultiEdit``: one file path and a list of edits."""
    if edits is None:
        edits = [{"old_string": "VALUE = 1", "new_string": "VALUE = 2"},
                 {"old_string": "VALUE = 2", "new_string": "VALUE = 3", "replace_all": True}]
    return {"file_path": str(path), "edits": edits}


def without_path(data, path_value=None, keep=False):
    """``data`` with its file path left out, or (``keep``) set to ``path_value``."""
    data = dict(data)
    if keep:
        data["file_path"] = path_value
    else:
        data.pop("file_path", None)
    return data


def ask_both(world, path, who, edit_text=None):
    """(the decision on ``Edit``, the decision on ``MultiEdit``) for the same file by the same actor.

    ``edit_text`` is (old string, new string) of the edit; the ``MultiEdit`` carries it as the last of two edits.
    """
    if edit_text is None:
        return (ask(world, "Edit", edit_input(path), who), ask(world, "MultiEdit", multiedit_input(path), who))
    old, new = edit_text
    edit = ask(world, "Edit", edit_input(path, old_string=old, new_string=new), who)
    multi = ask(world, "MultiEdit", multiedit_input(path, [
        {"old_string": "VALUE = 1", "new_string": "VALUE = 2"}, {"old_string": old, "new_string": new}]), who)
    return edit, multi


def assert_as_edit(edit, multi, expected, what):
    """``Edit`` gets the answer the case names, and ``MultiEdit`` gets the answer ``Edit`` gets.

    The first half is the case's own premise (the guard's answer on ``Edit`` is
    not changed by the round); the second is the round's order.
    """
    assert edit.decision == expected, (
        f"the case's premise does not hold: Edit {what} is answered {edit.decision} (exit {edit.returncode}), "
        f"not {expected}"
    )
    assert multi.decision == expected, (
        f"MultiEdit {what} is answered {multi.decision} (exit {multi.returncode}) where Edit is answered "
        f"{expected}: MultiEdit is judged exactly like Edit (DEC-685)"
    )


# --------------------------------------------------------------------------
# The tools the guard lets through without a path judgement
# --------------------------------------------------------------------------

# Free text as a brief for a subagent or a to-do item holds it: it names an acceptance test and a shell write,
# neither of which the tool performs.
ORDINARY_TEXT = (f"Change {ACCEPTANCE_REL} and {OUTSIDE_REL}, then run `echo changed > {SOURCE_REL}` "
                 f"and report what the unit tests under tests/unit say.")

# tool -> (why it is on the list, builder(text) -> input in the shape the tool takes, the text in a free-text field)
LISTED = {
    "Agent": ("starts a subagent; it writes no file and runs no command itself, and every call of the subagent "
              "reaches the guard on its own",
              lambda text: {"description": "Review the guard", "subagent_type": "Explore", "prompt": text}),
    "Task": ("the earlier name of the same subagent tool",
             lambda text: {"description": "Review the guard", "subagent_type": "general-purpose", "prompt": text}),
    "Skill": ("loads a skill's instructions into the session; writes no file, runs no command",
              lambda text: {"skill": "checkpoint", "args": text}),
    "ToolSearch": ("returns the definitions of tools; writes no file, runs no command",
                   lambda text: {"query": text, "max_results": 5}),
    "WebFetch": ("fetches a web page; writes no file of the project, runs no command",
                 lambda text: {"url": "https://example.invalid/page", "prompt": text}),
    "WebSearch": ("searches the web; writes no file of the project, runs no command",
                  lambda text: {"query": text}),
    "ListAgents": ("lists the session's agents; reads and writes no file",
                   lambda text: {"q": text}),
    "SendMessage": ("sends a message to an agent, whose own calls reach the guard",
                    lambda text: {"to": "a-worker", "message": text}),
    "TaskStop": ("stops a background task of the session; writes no file, runs no command",
                 lambda text: {"task_id": "task-1", "reason": text}),
    "TodoWrite": ("keeps the session's to-do list, which the harness holds; no file of the project",
                  lambda text: {"todos": [
                      {"content": "run the unit tests", "status": "completed", "activeForm": "Running the unit tests"},
                      {"content": text, "status": "pending", "activeForm": "Working"}]}),
    "TaskCreate": ("the session's task list, which the harness holds; no file of the project",
                   lambda text: {"subject": "a task", "description": text}),
    "TaskUpdate": ("the session's task list, which the harness holds; no file of the project",
                   lambda text: {"taskId": "1", "status": "completed", "description": text}),
    "TaskList": ("the session's task list, which the harness holds; no file of the project",
                 lambda text: {"filter": text}),
    "TaskGet": ("the session's task list, which the harness holds; no file of the project",
                lambda text: {"taskId": "1", "note": text}),
    "AskUserQuestion": ("asks the user a question; writes no file, runs no command",
                        lambda text: {"questions": [{
                            "question": text, "header": "A choice", "multiSelect": False,
                            "options": [{"label": "yes", "description": "go on"},
                                        {"label": "no", "description": "stop"}]}]}),
    "EnterPlanMode": ("switch the session's plan mode; write no file of the project, run no command",
                      lambda text: {"note": text}),
    "ExitPlanMode": ("switch the session's plan mode; write no file of the project, run no command",
                     lambda text: {"plan": text}),
}
LISTED_TOOLS = tuple(LISTED)


def listed_input(tool_name, text=ORDINARY_TEXT):
    return LISTED[tool_name][1](text)


# --------------------------------------------------------------------------
# The tools the guard does not know
# --------------------------------------------------------------------------

MADE_UP = "ToolAddedAfterTheRound"
MCP_TOOLS = {
    "mcp__filesystem__write_file": lambda w: {"path": str(w.path(SOURCE_REL)), "content": "VALUE = 2\n"},
    "mcp__notes__add": lambda w: {"note": {"title": "a note", "body": "nothing of the project"}},
    "mcp__github__create_issue": lambda w: {"title": "W1-02 acceptance", "body": ""},
}

# label -> (tool, builder(world) -> input in the shape the tool takes): refused by name (README, tenth batch).
REFUSED_BY_NAME = {
    "Monitor-with-a-harmless-command":
        ("Monitor", lambda w: {"command": "echo ready", "description": "wait for a line", "timeout_ms": 1000}),
    "Artifact-with-a-file-of-the-project":
        ("Artifact", lambda w: {"file_path": str(w.path("docs/notes.md")), "icon": "notes"}),
    "Workflow-with-a-script-given-inline":
        ("Workflow", lambda w: {"script": "export const meta = {name: 'a-run', description: 'one step'}\n"}),
    "Workflow-with-a-script-given-by-a-path":
        ("Workflow", lambda w: {"scriptPath": str(w.path("docs/notes.md"))}),
    "EnterWorktree": ("EnterWorktree", lambda w: {"name": "a-copy"}),
    "ExitWorktree": ("ExitWorktree", lambda w: {"action": "remove"}),
    "ArtifactComments": ("ArtifactComments", lambda w: {"url": "https://example.invalid/artifact/1"}),
    "ArtifactData": ("ArtifactData", lambda w: {"url": "https://example.invalid/artifact/1", "action": "list",
                                                 "collection": "rows"}),
    "CronCreate": ("CronCreate", lambda w: {"cron": "0 9 * * 1", "prompt": "say what changed"}),
    "CronDelete": ("CronDelete", lambda w: {"id": "job-1"}),
    "CronList": ("CronList", lambda w: {}),
    "DesignSync": ("DesignSync", lambda w: {}),
    "PushNotification": ("PushNotification", lambda w: {"message": "the run has ended"}),
    "RemoteTrigger": ("RemoteTrigger", lambda w: {"action": "list"}),
    "ReportFindings": ("ReportFindings", lambda w: {"findings": []}),
    "ScheduleWakeup": ("ScheduleWakeup", lambda w: {"delaySeconds": 60, "reason": "wait", "prompt": "go on"}),
}

# label -> (the name as sent, the known tool it is near). The call carries the input the known tool would be
# let through with for the actor (``input_of_the_known_tool``).
NEAR_MISSES = {
    "edit-in-lower-case": ("edit", "Edit"),
    "read-in-upper-case": ("READ", "Read"),
    "agent-in-lower-case": ("agent", "Agent"),
    "multiedit-in-lower-case": ("multiedit", "MultiEdit"),
    "bash-in-lower-case": ("bash", "Bash"),
    "Edit-and-a-trailing-space": ("Edit ", "Edit"),
    "Read-after-a-leading-space": (" Read", "Read"),
    "Agent-and-a-trailing-space": ("Agent ", "Agent"),
    "Edit-and-more-letters": ("Editor", "Edit"),
    "Read-and-more-letters": ("ReadFile", "Read"),
    "TodoWrite-and-more-letters": ("TodoWriteAll", "TodoWrite"),
}
# The same, with a character a reason cannot be asked to show as it was sent.
NEAR_MISSES_UNPRINTABLE = {
    "Edit-and-a-trailing-newline": ("Edit\n", "Edit"),
    "Agent-and-a-trailing-newline": ("Agent\n", "Agent"),
    "Read-and-a-trailing-NUL-byte": ("Read\x00", "Read"),
    "Bash-and-a-trailing-NUL-byte": ("Bash\x00", "Bash"),
    "MultiEdit-and-a-trailing-tab": ("MultiEdit\t", "MultiEdit"),
    "nothing-but-a-space": (" ", "Read"),
    "nothing-but-a-newline": ("\n", "Read"),
}


def input_of_the_known_tool(world, known, who):
    """The input with which ``known`` is let through for ``who`` where the actor may use it at all."""
    if known == "Edit":
        return edit_input(world.own_write(who))
    if known == "MultiEdit":
        return multiedit_input(world.own_write(who))
    if known == "Read":
        return {"file_path": str(world.path(SOURCE_REL))}
    if known == "Bash":
        return support.bash_tool_input("ls -la")
    return listed_input(known)


# "not known" or "unknown", and not the words of the refusal of an unknown role.
_NOT_KNOWN_RE = re.compile(r"(?i)\b(not known|unknown)\b(?! role)")


def assert_refused(result, what):
    """Not let through: a refusal by a rule, or exit code 2 (the guard's report of its own failure)."""
    assert result.decision == "deny", (
        f"{what} was not refused: decision={result.decision} exit={result.returncode}; the guard refuses a tool "
        f"it does not know (DEC-685)"
    )


def assert_refused_as_not_known(result, tool_name, what):
    """A refusal in a rule's form whose reason names the tool as it was sent and says it is not known to the guard."""
    assert_refused(result, what)
    protected.assert_refused_by_rule(result, what)
    reason = protected.reason_of(result)
    assert tool_name in reason, f"the refusal of {what} does not name the tool as it was sent: {reason!r}"
    assert _NOT_KNOWN_RE.search(reason), (
        f"the refusal of {what} does not say that the tool is not known to the guard "
        f"(\"not known\" or \"unknown\"): {reason!r}"
    )


def assert_refused_for(who, result, tool_name, what):
    """Refused; for a session with a declared role the refusal is the one of a tool that is not known.

    For a session with no role or an unknown role and for a subagent that is not
    a role the round asks for the refusal only (README, tenth batch).
    """
    if who in DECLARED:
        assert_refused_as_not_known(result, tool_name, what)
    else:
        assert_refused(result, what)


def assert_carries_none_of(result, values, what):
    """Nothing of ``values`` appears in anything the hook wrote."""
    said = protected.output_of(result)
    shown = [index for index, value in enumerate(values) if str(value) and str(value) in said]
    # Positions only: a failure must not print what a refusal must not print.
    assert not shown, f"the refusal of {what} carries {len(shown)} value(s) it must not (positions {shown})"


# --------------------------------------------------------------------------
# Nothing on disk changes by a decision
# --------------------------------------------------------------------------

def tree_state(project):
    """What git sees of the project, and the bytes of every committed file."""
    project = Path(project)
    names = support.git(project, "ls-files", "-z").split("\0")
    files = {name: (project / name).read_bytes() for name in names
             if name and (project / name).is_file() and not (project / name).is_symlink()}
    return support.porcelain(project), files


def assert_tree_unchanged(project, before, what):
    status, files = tree_state(project)
    assert status == before[0], f"git status --porcelain changed after {what}:\n{status}"
    changed = sorted(name for name in before[1] if files.get(name) != before[1][name])
    assert not changed, f"{len(changed)} committed file(s) changed after {what}: {changed[:5]}"
