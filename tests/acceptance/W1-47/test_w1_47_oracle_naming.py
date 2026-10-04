"""W1-47 -- what "names the held-out path" covers (DEC-215).

KPI success 4 and failure 2 say "names the oracle path". DEC-215 decides what
that covers:

- the guard denies a tool call whose input contains the held-out path
  **literally anywhere**: any string of the input, at any depth, free text and
  code inside a Bash command included;
- or **reaches it** through a relative path, ``..``, ``~``, ``$HOME`` or a
  symbolic link;
- **exception:** edits to the two files that hold the path
  (``governance/project/held-out.yaml`` and the committed
  ``.claude/settings.json``) are not denied for carrying it; their usual role
  rules still apply.

Accepted residual, not tested either way: a parent directory given to a
recursive tool, a glob that matches the path without naming it, and a
look-alike sibling whose name starts with the same characters. No test here
requires a denial for them, and none requires that they are allowed.

Every test works against a stand-in directory named by a ``held-out.yaml`` the
test builds itself. The stand-in is put where the form needs it: in the system
temporary directory, in the project (for a path relative to the project), or in
the session's home directory (for ``~`` and ``$HOME``). No call is ever made.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest

import w1_47_support as support

ORCHESTRATOR = support.EVERY_ACTOR[support.ORCHESTRATOR]
ENGINEER = support.EVERY_ACTOR[support.ENGINEER]
ACTORS = (support.ORCHESTRATOR, support.ENGINEER, "no-role")
STAND_IN_NAME = "held-out-stand-in"
SOURCE_FILE = support.check_support.SOURCE_FILE   # inside the engineer's ticket paths


@dataclass(frozen=True)
class Places:
    """Where one test's stand-in is, and the paths around it."""
    p: Path          # the stand-in: the configured, absolute held-out path
    project: Path
    relative: str    # the stand-in as seen from the project directory, the session's working directory
    detour: str      # an absolute path to the stand-in that goes through ``..``
    link: Path       # a symbolic link to the stand-in, outside the project
    file_link: Path  # a symbolic link in the project to one file of the stand-in
    other: Path      # a directory outside the project that holds nothing held out


def _places(where, project, sandbox):
    """Make the stand-in in one of three places and configure it in the project."""
    base = {"temp": sandbox.tmpdir, "repo": project, "home": sandbox.home}[where]
    stand_in = support.make_stand_in(base / STAND_IN_NAME)
    support.configure_stand_in(project, stand_in)
    (base / "detour").mkdir(exist_ok=True)
    link = sandbox.elsewhere / "a-link"
    link.symlink_to(stand_in, target_is_directory=True)
    file_link = project / "docs" / "linked-answers.md"
    file_link.symlink_to(stand_in / "answers.md")
    return Places(stand_in, project, os.path.relpath(stand_in, project),
                  f"{base}/detour/../{STAND_IN_NAME}", link, file_link, sandbox.elsewhere)


def _bash(text):
    return lambda at: support.bash_input(text.format(p=at.p, rel=at.relative, detour=at.detour, link=at.link,
                                                     file_link=at.file_link, project=at.project))


# name: (where the stand-in is, tool, input).
# -- The path literally anywhere in the input ------------------------------------
LITERAL = {
    "Agent-prompt": ("temp", "Agent", lambda at: {
        "description": "summarise a file", "subagent_type": "general-purpose",
        "prompt": f"Read {at.p}/answers.md and tell me what it says."}),
    "WebFetch-url": ("temp", "WebFetch", lambda at: {"url": f"file://{at.p}/answers.md", "prompt": "summarise"}),
    "Grep-pattern": ("temp", "Grep", lambda at: {"pattern": f"{at.p}", "path": f"{at.project}/docs"}),
    "Glob-pattern-in-the-middle": ("temp", "Glob", lambda at: {"pattern": f"{{{at.p},{at.project}/docs}}/*.md"}),
    "Write-content-of-another-file": ("temp", "Write", lambda at: {
        "file_path": f"{at.project}/{SOURCE_FILE}", "content": f"ANSWERS = '{at.p}/answers.md'\n"}),
    "Edit-new-string-of-another-file": ("temp", "Edit", lambda at: {
        "file_path": f"{at.project}/{SOURCE_FILE}", "old_string": "VALUE = 1", "new_string": f"VALUE = '{at.p}'"}),
    "Edit-old-string-of-another-file": ("temp", "Edit", lambda at: {
        "file_path": f"{at.project}/{SOURCE_FILE}", "old_string": f"{at.p}", "new_string": "VALUE = 2"}),
    "TodoWrite-nested-text": ("temp", "TodoWrite", lambda at: {"todos": [
        {"content": "run the unit tests", "status": "completed", "activeForm": "Running the unit tests"},
        {"content": f"compare with {at.p}/answers.md", "status": "pending", "activeForm": "Comparing"}]}),
    "MCP-free-text": ("temp", "mcp__notes__add", lambda at: {"note": {"title": "todo", "body": f"see {at.p}."}}),
    "Bash-description": ("temp", "Bash", lambda at: {"command": "ls -la", "description": f"then look at {at.p}"}),
    "Bash-python-code": ("temp", "Bash", _bash("python3 -c \"print(open('{p}/answers.md').read())\"")),
    "Bash-shell-code": ("temp", "Bash", _bash("bash -c 'cat {p}/answers.md'")),
    "Bash-echo-text": ("temp", "Bash", _bash("echo \"the answers are in {p}/answers.md, do not open them\"")),
    "Bash-option-value": ("temp", "Bash", _bash("grep --file={p}/answers.md -c x README.md")),
    "Bash-variable-assignment": ("temp", "Bash", _bash("TARGET={p} && ls -la")),
    "Bash-command-substitution": ("temp", "Bash", _bash("echo $(cat {p}/answers.md)")),
    "Bash-after-a-colon": ("temp", "Bash", _bash("rsync -a localhost:{p}/ docs/")),
}
# -- The path reached without being written out -----------------------------------
REACHED = {
    "relative-Read": ("repo", "Read", lambda at: {"file_path": f"{at.relative}/answers.md"}),
    "relative-Grep-with-a-dot": ("repo", "Grep", lambda at: {"pattern": "answers", "path": f"./{at.relative}"}),
    "relative-Glob": ("repo", "Glob", lambda at: {"pattern": "**/*.py", "path": f"{at.relative}"}),
    "relative-Bash-cat": ("repo", "Bash", _bash("cat {rel}/answers.md")),
    "relative-Bash-ls-with-a-dot": ("repo", "Bash", _bash("ls -la ./{rel}")),
    "relative-outside-the-project-Read": ("temp", "Read", lambda at: {"file_path": f"{at.relative}/answers.md"}),
    "relative-outside-the-project-Bash": ("temp", "Bash", _bash("cat {rel}/answers.md")),
    "dot-dot-Read": ("temp", "Read", lambda at: {"file_path": f"{at.detour}/answers.md"}),
    "dot-dot-Grep": ("temp", "Grep", lambda at: {"pattern": "answers", "path": f"{at.detour}"}),
    "dot-dot-Bash": ("temp", "Bash", _bash("cat {detour}/answers.md")),
    "dot-dot-in-the-project-Read": ("repo", "Read", lambda at: {"file_path": f"{at.detour}/answers.md"}),
    "dot-dot-in-the-project-Bash-relative": ("repo", "Bash", _bash("ls docs/../{rel}")),
    "tilde-Bash-cat": ("home", "Bash", _bash("cat ~/" + STAND_IN_NAME + "/answers.md")),
    "tilde-Bash-ls": ("home", "Bash", _bash("ls -la ~/" + STAND_IN_NAME)),
    "tilde-Read": ("home", "Read", lambda at: {"file_path": f"~/{STAND_IN_NAME}/answers.md"}),
    "HOME-Bash-cat": ("home", "Bash", _bash("cat $HOME/" + STAND_IN_NAME + "/answers.md")),
    "HOME-Bash-quoted": ("home", "Bash", _bash("cat \"$HOME/" + STAND_IN_NAME + "/answers.md\"")),
    "HOME-Bash-grep": ("home", "Bash", _bash("grep -rn test $HOME/" + STAND_IN_NAME)),
    "link-Read": ("temp", "Read", lambda at: {"file_path": f"{at.link}/answers.md"}),
    "link-Grep": ("temp", "Grep", lambda at: {"pattern": "answers", "path": f"{at.link}"}),
    "link-Bash-cat": ("temp", "Bash", _bash("cat {link}/answers.md")),
    "link-Bash-ls": ("temp", "Bash", _bash("ls -la {link}/")),
    "link-to-a-file-Read": ("temp", "Read", lambda at: {"file_path": f"{at.file_link}"}),
    "link-to-a-file-Bash-relative": ("temp", "Bash", _bash("cat docs/linked-answers.md")),
    "link-Write": ("temp", "Write", lambda at: support.write_input("Write", f"{at.link}/new.md")),
}
FORMS = {**LITERAL, **REACHED}


@pytest.mark.parametrize("who", ACTORS)
@pytest.mark.parametrize("name", sorted(LITERAL))
def test_a_call_that_holds_the_path_anywhere_in_its_input_is_denied(project, sandbox, guard, name, who):
    """DEC-215, KPI failure 2 [CAP-49.c]: any string of the input, at any depth; free text and code included."""
    where, tool_name, build = LITERAL[name]
    at = _places(where, project, sandbox)
    result = guard(project, tool_name, build(at), support.EVERY_SESSION[who])
    support.assert_denied_by_rule(result, f"{name} ({tool_name}), with the stand-in held-out path in its input, by {who}")


@pytest.mark.parametrize("who", ACTORS)
@pytest.mark.parametrize("name", sorted(REACHED))
def test_a_call_that_reaches_the_path_without_writing_it_out_is_denied(project, sandbox, guard, name, who):
    """DEC-215, KPI failure 2 [CAP-49.c]: a relative path, ``..``, ``~``, ``$HOME`` or a symbolic link."""
    where, tool_name, build = REACHED[name]
    at = _places(where, project, sandbox)
    tool_input = build(at)
    assert str(at.p) not in str(tool_input), f"the fixture input of {name} holds the stand-in path literally"
    result = guard(project, tool_name, tool_input, support.EVERY_SESSION[who])
    support.assert_denied_by_rule(result, f"{name} ({tool_name}), which reaches the stand-in held-out path, by {who}")


# --------------------------------------------------------------------------
# The same forms on a directory that is not held out stay open
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(name for name, form in FORMS.items()
                                        if form[1] not in ("Write", "Edit") and "Bash-after-a-colon" != name))
def test_the_same_form_on_a_directory_that_is_not_held_out_is_allowed(project, sandbox, guard, name):
    """The rule is about the configured path: the same call on another directory is as open as before.

    The stand-in is made in the same place, and the configuration names an
    unrelated directory.
    """
    where, tool_name, build = FORMS[name]
    at = _places(where, project, sandbox)
    support.configure_stand_in(project, support.make_stand_in(sandbox.elsewhere / "what-is-held-out"))
    result = guard(project, tool_name, build(at), ORCHESTRATOR)
    support.assert_allowed(result, f"{name} ({tool_name}) on a directory the configuration does not name")


# --------------------------------------------------------------------------
# The exception: edits to the two files that hold the path
# --------------------------------------------------------------------------

HOLDERS = (support.CONFIG_REL, support.SETTINGS_REL)
EDITS = {
    "Write": lambda path, p: {"file_path": path, "content": f"held_out_paths:\n- {p}\n"},
    "Edit-new-string": lambda path, p: {"file_path": path, "old_string": "a", "new_string": f"Read(/{p}/**)"},
    "Edit-old-string": lambda path, p: {"file_path": path, "old_string": f"- {p}", "new_string": "- /another"},
}


def _edit(name, path, p):
    return ("Write" if name == "Write" else "Edit"), EDITS[name](str(path), p)


@pytest.mark.parametrize("holder", HOLDERS)
@pytest.mark.parametrize("name", sorted(EDITS))
def test_an_edit_to_a_file_that_holds_the_path_is_not_denied_for_carrying_it(project, guard, temp_stand_in, name,
                                                                            holder):
    """DEC-215, the exception: the orchestrator, whose role rules allow the edit, can still make it."""
    tool_name, tool_input = _edit(name, project / holder, temp_stand_in)
    result = guard(project, tool_name, tool_input, ORCHESTRATOR)
    support.assert_allowed(result, f"{name} to {holder} by the orchestrator, carrying the stand-in held-out path,")


@pytest.mark.parametrize("who", (support.ENGINEER, support.TEST_DESIGNER, support.AUDITOR, "no-role"))
@pytest.mark.parametrize("holder", HOLDERS)
def test_the_usual_role_rules_still_apply_to_the_two_files(project, guard, temp_stand_in, holder, who):
    """DEC-215: "their usual role rules still apply": a role that may not write the file is denied as before."""
    for name in sorted(EDITS):
        tool_name, tool_input = _edit(name, project / holder, temp_stand_in)
        result = guard(project, tool_name, tool_input, support.EVERY_SESSION[who])
        support.assert_denied_by_rule(result, f"{name} to {holder} by {who}")


@pytest.mark.parametrize("name", sorted(EDITS))
def test_the_exception_is_for_the_two_files_only(project, guard, temp_stand_in, name):
    """DEC-215: the same edit to any other file the orchestrator may write is denied for carrying the path."""
    for other in ("governance/project/bootstrap.md", "governance/project/held-out.yaml.bak",
                  ".claude/settings.local.json", "docs/notes.md"):
        tool_name, tool_input = _edit(name, project / other, temp_stand_in)
        result = guard(project, tool_name, tool_input, ORCHESTRATOR)
        support.assert_denied_by_rule(
            result, f"{name} to {other} by the orchestrator, carrying the stand-in held-out path,")


def test_the_exception_does_not_open_the_path_itself(project, guard, temp_stand_in):
    """DEC-215: the exception is about what an edit carries, not where it goes."""
    for holder in HOLDERS:
        result = guard(project, "Bash", support.bash_input(f"cp {temp_stand_in}/answers.md {project}/{holder}"),
                       ORCHESTRATOR)
        support.assert_denied_by_rule(result, f"a Bash copy from the stand-in held-out path into {holder}")
        result = guard(project, "Read", {"file_path": f"{temp_stand_in}/answers.md"}, ORCHESTRATOR)
        support.assert_denied_by_rule(result, "Read on the stand-in held-out path by the orchestrator")
