"""W1-02 — what keeps working beside the two protected files (DEC-508, DEC-525).

The change is about reads of two files, and it is stricter-only. Held here, in
a project that holds a stand-in settings file and a stand-in held-out file:

- ``git diff --stat`` and ``git status`` naming the settings file;
- a write to the settings file, for exactly the roles that may write it today;
- ordinary work near the two files: a read, a search or a listing whose targets
  do not take either file in, and text that only mentions the settings file;
- the helper for hook listings, as a shell command: its command line names no
  file, so the guard lets it through like any read-only command.

The harness's own use of the settings file is no tool call, so no hook input
exists for it: the guard decides tool calls only (README, "What stands").

Every case of this file is green before the change and stays green after it.
"""

from __future__ import annotations

import pytest

import w1_02_protected_support as protected
import w1_02_support as support

SETTINGS = "settings-file"
FILES = sorted(protected.PROTECTED)
READERS = ("no-role", "engineer", "orchestrator")


# --------------------------------------------------------------------------
# git diff --stat and git status naming the settings file
# --------------------------------------------------------------------------

GIT_FORMS = {
    "diff-stat": "git diff --stat {rel}",
    "diff-stat-after-two-dashes": "git diff --stat -- {rel}",
    "diff-stat-absolute": "git diff --stat {abs}",
    "status": "git status {rel}",
    "status-short-after-two-dashes": "git status --short -- {rel}",
    "status-porcelain": "git status --porcelain",
}


@pytest.mark.parametrize("who", READERS + ("test-designer",))
@pytest.mark.parametrize("form", sorted(GIT_FORMS))
def test_git_diff_stat_and_git_status_on_the_settings_file_stay_allowed(guarded, form, who):
    """Line 3: the two commands every session may still use on the settings file."""
    command = GIT_FORMS[form].format(rel=guarded.rel(SETTINGS), abs=guarded.path(SETTINGS))
    result = protected.ask(guarded, "Bash", support.bash_tool_input(command), who)
    protected.assert_allowed(result, f"Bash `{command}` by {who}")


# --------------------------------------------------------------------------
# Who may write the settings file: as today, neither wider nor narrower
# --------------------------------------------------------------------------

O, E = support.ORCHESTRATOR, support.ENGINEER
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
TICKET = support.TICKET_ID
SETTINGS_TICKET = protected.SETTINGS_TICKET_ID

# name -> ((GOV_ROLE, GOV_TICKET, subagent type), allowed today).
WRITERS = {
    # An orchestrator session writes anywhere but the acceptance tests (DEC-156), whatever the ticket.
    "orchestrator-on-its-ticket": ((O, ORCHESTRATOR_TICKET, None), True),
    "orchestrator-on-an-engineer-ticket": ((O, TICKET, None), True),
    "orchestrator-without-a-ticket": ((O, None, None), True),
    # Any other role: only on a ticket of its own role whose allowed_paths name the file.
    "engineer-on-a-ticket-that-names-the-file": ((E, SETTINGS_TICKET, None), True),
    "engineer-subagent-on-a-ticket-that-names-the-file": ((O, SETTINGS_TICKET, E), True),
    "orchestrator-subagent-on-the-orchestrator-ticket-that-names-the-file": ((E, ORCHESTRATOR_TICKET, O), True),
    "engineer-on-a-ticket-that-does-not-name-it": ((E, TICKET, None), False),
    "engineer-on-the-orchestrator-s-ticket": ((E, ORCHESTRATOR_TICKET, None), False),
    "engineer-subagent-on-the-orchestrator-s-ticket": ((O, ORCHESTRATOR_TICKET, E), False),
    "orchestrator-subagent-on-an-engineer-ticket": ((E, TICKET, O), False),
    "product-spec": ((support.PRODUCT_SPEC, support.PRODUCT_SPEC_TICKET_ID, None), False),
    "product-spec-on-the-engineer-ticket-that-names-the-file": ((support.PRODUCT_SPEC, SETTINGS_TICKET, None),
                                                                False),
    "test-designer-on-a-ticket-that-names-the-file": ((support.TEST_DESIGNER, SETTINGS_TICKET, None), False),
    "auditor-on-a-ticket-that-names-the-file": ((support.AUDITOR, SETTINGS_TICKET, None), False),
    "research-on-a-ticket-that-names-the-file": ((protected.RESEARCH, SETTINGS_TICKET, None), False),
    "ticket-lead-on-a-ticket-that-names-the-file": ((protected.TICKET_LEAD, SETTINGS_TICKET, None), False),
    "untyped-subagent-of-the-orchestrator": ((O, ORCHESTRATOR_TICKET, "general-purpose"), False),
    "no-role": ((None, None, None), False),
    "no-role-with-a-ticket-that-names-the-file": ((None, SETTINGS_TICKET, None), False),
    "unknown-role": (("developer", SETTINGS_TICKET, None), False),
}
BASH_WRITES = {
    "redirect": "echo '{{}}' > {rel}",
    "copy-with-the-file-as-destination": "cp docs/notes.md {rel}",
}


def _assert_as_today(result, allowed, what):
    if allowed:
        protected.assert_allowed(result, what)
    else:
        assert result.decision == "deny", f"{what} was not denied: decision={result.decision}"


@pytest.mark.parametrize("tool_name", ["Write", "Edit"])
@pytest.mark.parametrize("who", sorted(WRITERS))
def test_a_write_to_the_settings_file_is_decided_as_today(guarded, who, tool_name):
    """Line 3: the change is about reads; who may write the settings file does not change."""
    actor, allowed = WRITERS[who]
    tool_input = support.edit_tool_input(tool_name, guarded.path(SETTINGS))
    result = protected.ask(guarded, tool_name, tool_input, actor)
    _assert_as_today(result, allowed, f"{tool_name} to the settings file by {who}")


@pytest.mark.parametrize("form", sorted(BASH_WRITES))
@pytest.mark.parametrize("who", ("orchestrator-on-its-ticket", "engineer-on-a-ticket-that-names-the-file",
                                 "engineer-on-a-ticket-that-does-not-name-it", "no-role"))
def test_a_bash_write_to_the_settings_file_is_decided_as_today(guarded, who, form):
    """Line 3: the file as the target of a shell write is a write, not a read."""
    actor, allowed = WRITERS[who]
    command = BASH_WRITES[form].format(rel=guarded.rel(SETTINGS))
    result = protected.ask(guarded, "Bash", support.bash_tool_input(command), actor)
    _assert_as_today(result, allowed, f"Bash `{command}` by {who}")


# --------------------------------------------------------------------------
# Ordinary work near the two files
# --------------------------------------------------------------------------

# name -> (tool, input for the protected file ``n`` of the project ``g``): none takes the file in.
NEAR = {
    "Read-another-file-of-the-folder": lambda g, n: ("Read", {"file_path": str(g.project / g.neighbour_rel(n))}),
    "Read-another-file-of-the-folder-relative": lambda g, n: ("Read", {"file_path": g.neighbour_rel(n)}),
    "Grep-in-another-file-of-the-folder": lambda g, n: ("Grep", {"pattern": "VALUE",
                                                              "path": str(g.project / g.neighbour_rel(n))}),
    "Glob-for-another-file-of-the-folder": lambda g, n: ("Glob", {"pattern": g.neighbour_rel(n)}),
    "Bash-cat-another-file-of-the-folder": lambda g, n: ("Bash", support.bash_tool_input(
        f"cat {g.neighbour_rel(n)}")),
    "Bash-grep-in-another-file-of-the-folder": lambda g, n: ("Bash", support.bash_tool_input(
        f"grep -n VALUE {g.neighbour_rel(n)}")),
}
ELSEWHERE = {
    "Read-a-source-file": ("Read", lambda g: {"file_path": str(g.project / "src/gov/guard/decide.py")}),
    "Read-a-file-below-the-settings-folder": ("Read", lambda g: {
        "file_path": str(g.project / protected.BELOW_SETTINGS_FOLDER)}),
    "Grep-a-folder-below-the-settings-folder": ("Grep", lambda g: {"pattern": "VALUE",
                                                                  "path": str(g.project / ".claude/agents")}),
    "Grep-over-src": ("Grep", lambda g: {"pattern": "VALUE", "path": str(g.project / "src")}),
    "Grep-over-src-relative": ("Grep", lambda g: {"pattern": "VALUE", "path": "src"}),
    "Grep-from-the-root-with-a-glob-that-cannot-match": ("Grep", lambda g: {"pattern": "VALUE",
                                                                           "path": str(g.project), "glob": "*.py"}),
    "Grep-from-the-root-with-a-glob-for-src": ("Grep", lambda g: {"pattern": "VALUE", "path": str(g.project),
                                                                 "glob": "src/**"}),
    "Glob-from-the-root-for-python-files": ("Glob", lambda g: {"pattern": "**/*.py", "path": str(g.project)}),
    "Glob-under-src": ("Glob", lambda g: {"pattern": "src/**/*.py", "path": str(g.project)}),
    "Bash-ls-of-the-root": ("Bash", lambda g: support.bash_tool_input("ls -la")),
    "Bash-cat-a-root-file": ("Bash", lambda g: support.bash_tool_input("cat README.md")),
    "Bash-grep-over-src": ("Bash", lambda g: support.bash_tool_input("grep -rn VALUE src/")),
    "Bash-find-under-src": ("Bash", lambda g: support.bash_tool_input("find src -name '*.py'")),
    "Bash-ls-of-a-folder-below-the-settings-folder": ("Bash", lambda g: support.bash_tool_input(
        "ls -la .claude/agents")),
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("who", READERS)
@pytest.mark.parametrize("form", sorted(NEAR))
def test_another_file_of_the_same_folder_named_alone_stays_readable(guarded, form, who, name):
    """Line 3: the rule closes one file of the folder, not the folder's other files."""
    tool_name, tool_input = NEAR[form](guarded, name)
    result = protected.ask(guarded, tool_name, tool_input, who)
    protected.assert_allowed(result, f"{form} beside the stand-in {name} by {who}")


@pytest.mark.parametrize("who", READERS)
@pytest.mark.parametrize("form", sorted(ELSEWHERE))
def test_a_read_a_search_or_a_listing_that_takes_neither_file_in_stays_allowed(guarded, form, who):
    """Line 3: a search over ``src/``, a search from the root under a glob that matches neither file."""
    tool_name, build = ELSEWHERE[form]
    result = protected.ask(guarded, tool_name, build(guarded), who)
    protected.assert_allowed(result, f"{form} by {who}")


# Text of a file tool or a brief that mentions the settings file and is no file target of the call.
MENTIONS = {
    "a-search-pattern": ("Grep", lambda g: {"pattern": "settings\\.json", "path": str(g.project / "src")}),
    "the-content-of-a-written-file": ("Write", lambda g: {
        "file_path": str(g.project / "docs/notes.md"),
        "content": f"No session reads {g.rel(SETTINGS)}; use `{protected.HELPER_COMMAND}`.\n"}),
    "a-brief-for-a-subagent": ("Agent", lambda g: {
        "description": "Review the guard", "subagent_type": "Explore",
        "prompt": f"Review src/gov/guard. Never read {g.rel(SETTINGS)}."}),
}


@pytest.mark.parametrize("form", sorted(MENTIONS))
def test_text_that_mentions_the_settings_file_is_not_a_read(guarded, form):
    """Line 3: the rule is about file targets; a pattern, a written text or a brief that names the file reads
    nothing. A shell command that only mentions the file is left open (README)."""
    tool_name, build = MENTIONS[form]
    result = protected.ask(guarded, tool_name, build(guarded), "orchestrator")
    protected.assert_allowed(result, f"{tool_name} with the settings file's name in {form}")


# --------------------------------------------------------------------------
# The helper as a shell command
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", sorted(protected.ACTORS))
def test_the_helper_s_command_is_allowed_for_every_role(guarded, who):
    """Line 4: the helper is how a session learns the registered hooks; its command line names no file."""
    result = protected.ask(guarded, "Bash", support.bash_tool_input(protected.HELPER_COMMAND), who)
    protected.assert_allowed(result, f"Bash `{protected.HELPER_COMMAND}` by {who}")
