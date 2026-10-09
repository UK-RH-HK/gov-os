"""W1-02 — the guard refuses every agent read of the settings file and of the held-out file.

Owner's order (DEC-508, DEC-525): "the guard refuses any agent tool call that
reads ``.claude/settings.json`` or the project's held-out file ..., for every
role, the orchestrator included", and "the guard refuses any agent tool call
whose expanded file targets (globs included, DEC-108) include the project's
held-out file".

A read is a call of a tool an agent has: a file tool (a read; a search or a
listing whose expanded targets take the file in), or a shell command whose file
targets, once expanded, include the file. The forms below are the ones a guard
that reads a tool input can decide: the file is named (relative, absolute,
through ``..``, a variable of the hook's environment or a symbolic link), or it
is taken in by a folder, a glob, or the text of a script given on the command
line. The forms a guard cannot see are listed in the README as residuals; none
of them has a case.

Both files are stand-ins in a temporary project (``w1_02_protected_support``).
The held-out file's path is taken from the guard's own module and never typed.

A refusal names the rule and the decision, and nothing of the file
(``test_a_refusal_names_the_decision_and_nothing_of_the_file``).
"""

from __future__ import annotations

import os
import re

import pytest

import w1_02_protected_support as protected
import w1_02_support as support

FILES = sorted(protected.PROTECTED)
WIDEST = "orchestrator"   # the role with the widest scope: what it is refused, no role is given


def _ext(g, name):
    return os.path.splitext(g.rel(name))[1]


def _base(g, name):
    return os.path.basename(g.rel(name))


# name -> (tool, input for the protected file ``name`` of the project ``g``).
FILE_TOOL_FORMS = {
    # The file named.
    "Read-absolute": lambda g, n: ("Read", {"file_path": str(g.path(n))}),
    "Read-relative": lambda g, n: ("Read", {"file_path": g.rel(n)}),
    "Read-with-a-limit": lambda g, n: ("Read", {"file_path": str(g.path(n)), "offset": 1, "limit": 5}),
    "Read-through-dot-dot": lambda g, n: ("Read", {"file_path": f"{g.project}/src/../{g.rel(n)}"}),
    "Read-through-a-symbolic-link": lambda g, n: ("Read", {"file_path": str(g.links[n])}),
    "Grep-in-the-file": lambda g, n: ("Grep", {"pattern": ".", "path": str(g.path(n)), "output_mode": "content"}),
    "Grep-in-the-file-relative": lambda g, n: ("Grep", {"pattern": ".", "path": g.rel(n)}),
    "Grep-through-a-symbolic-link": lambda g, n: ("Grep", {"pattern": ".", "path": str(g.links[n])}),
    # The folder that holds the file.
    "Grep-over-the-folder": lambda g, n: ("Grep", {"pattern": ".", "path": str(g.folder(n))}),
    "Grep-over-the-folder-relative": lambda g, n: ("Grep", {"pattern": ".", "path": g.folder_rel(n)}),
    "Grep-over-the-folder-with-a-glob": lambda g, n: ("Grep", {"pattern": ".", "path": str(g.folder(n)),
                                                            "glob": f"*{_ext(g, n)}"}),
    "Glob-in-the-folder": lambda g, n: ("Glob", {"pattern": "*", "path": str(g.folder(n))}),
    "Glob-pattern-over-the-folder": lambda g, n: ("Glob", {"pattern": f"{g.folder_rel(n)}/*"}),
    "Glob-pattern-over-the-folder-absolute": lambda g, n: ("Glob", {"pattern": f"{g.folder(n)}/*{_ext(g, n)}"}),
    # From the project root, with a glob that takes the file in.
    "Grep-from-the-root-with-a-glob-that-matches": lambda g, n: ("Grep", {"pattern": ".", "path": str(g.project),
                                                                       "glob": f"*{_ext(g, n)}"}),
    "Grep-from-the-root-with-a-glob-for-the-folder": lambda g, n: ("Grep", {"pattern": ".", "path": str(g.project),
                                                                         "glob": f"{g.folder_rel(n)}/**"}),
    "Glob-from-the-root-by-extension": lambda g, n: ("Glob", {"pattern": f"**/*{_ext(g, n)}",
                                                           "path": str(g.project)}),
    "Glob-from-the-root-by-name": lambda g, n: ("Glob", {"pattern": f"**/{_base(g, n)}", "path": str(g.project)}),
    "Glob-the-file-itself": lambda g, n: ("Glob", {"pattern": g.rel(n)}),
}

# Shell commands; ``{rel}`` and ``{abs}`` are the file, ``{dir}`` its folder, ``{base}`` its name.
COMMANDS = {
    "cat-relative": "cat {rel}",
    "cat-absolute": "cat {abs}",
    "cat-quoted": 'cat "{rel}"',
    "cat-single-quoted-absolute": "cat '{abs}'",
    "cat-dot-slash": "cat ./{rel}",
    "cat-through-dot-dot": "cat src/../{rel}",
    "cat-through-a-variable": 'cat "$CLAUDE_PROJECT_DIR/{rel}"',
    "cat-through-a-symbolic-link": "cat {link}",
    "cat-after-cd-into-the-folder": "cd {dir} && cat {base}",
    "cat-a-glob-over-the-folder": "cat {dir}/*",
    "cat-beside-another-file": "cat README.md {rel}",
    "head": "head -20 {rel}",
    "input-redirect": "wc -c < {rel}",
    "in-a-pipeline": "cat {rel} | wc -l",
    "after-another-command": "git status --porcelain && cat {rel}",
    "grep-in-the-file": "grep -n . {rel}",
    "grep-over-the-folder": "grep -rn . {dir}",
    "ls-of-the-folder": "ls -la {dir}",
    "find-in-the-folder": "find {dir} -type f",
    "copy-with-the-file-as-source": "cp {rel} .gov-runtime/scratch/w1-02-copy",
    "copy-absolute-into-the-temp-directory": "cp {abs} {tmp}/w1-02-copy",
    "interpreter-with-an-inline-script": "python3 -c \"print(open('{rel}').read())\"",
    "interpreter-with-an-inline-script-absolute": "python3 -c \"print(open('{abs}').read())\"",
}
# Forms of the settings file alone.
SETTINGS_COMMANDS = {
    # The incident behind DEC-525: an interpreter started from the shell, the script on the command line.
    "interpreter-loading-the-settings-for-their-hooks":
        "python3 -c \"import json; print(json.load(open('{rel}'))['hooks'])\"",
    "jq": "jq .hooks {rel}",
    "git-diff-without-stat": "git diff {rel}",
    "git-diff-stat-with-the-patch": "git diff --stat -p {rel}",
    "git-show-of-the-committed-file": "git show HEAD:{rel}",
    "git-diff-stat-then-cat": "git diff --stat {rel} && cat {rel}",
}


def _command(g, name, text):
    return text.format(rel=g.rel(name), abs=g.path(name), dir=g.folder_rel(name), base=_base(g, name),
                       link=g.links[name], tmp=g.sandbox.tmpdir)


def _bash_form(text):
    return lambda g, n: ("Bash", support.bash_tool_input(_command(g, n, text)))


FORMS = {**FILE_TOOL_FORMS, **{f"Bash-{name}": _bash_form(text) for name, text in COMMANDS.items()}}
SETTINGS_FORMS = {f"Bash-{name}": _bash_form(text) for name, text in SETTINGS_COMMANDS.items()}
# One form per kind of tool, asked of every actor.
CORE = ("Read-absolute", "Grep-over-the-folder-with-a-glob", "Bash-cat-relative",
        "Bash-interpreter-with-an-inline-script")


# --------------------------------------------------------------------------
# Refused: every form, by the role with the widest scope
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(FORMS))
def test_a_read_of_a_protected_file_is_refused(guarded, form, name):
    """Line 1: each tool, the glob and folder forms, relative and absolute spellings, a link, a copy."""
    tool_name, tool_input = FORMS[form](guarded, name)
    result = protected.ask(guarded, tool_name, tool_input, WIDEST)
    protected.assert_refused_by_rule(result, f"{form} ({tool_name}) on the stand-in {name} by the {WIDEST}")


@pytest.mark.parametrize("form", sorted(SETTINGS_FORMS))
def test_a_command_that_prints_the_settings_file_is_refused(guarded, form):
    """Line 1, and the incident behind DEC-525. Only ``git diff --stat`` and ``git status`` name the file freely."""
    tool_name, tool_input = SETTINGS_FORMS[form](guarded, "settings-file")
    result = protected.ask(guarded, tool_name, tool_input, WIDEST)
    protected.assert_refused_by_rule(result, f"{form} on the stand-in settings file by the {WIDEST}")


def test_the_search_behind_dec_508_is_refused(guarded):
    """The incident behind DEC-508: a test designer's search with a glob over the folder that holds the file."""
    name = "held-out-file"
    for tool_name, tool_input in (
        ("Glob", {"pattern": f"{guarded.folder_rel(name)}/*"}),
        ("Grep", {"pattern": "path", "path": guarded.folder_rel(name), "glob": f"*{_ext(guarded, name)}"}),
    ):
        result = protected.ask(guarded, tool_name, tool_input, "test-designer")
        protected.assert_refused_by_rule(result, f"{tool_name} with a glob over the held-out file's folder")


# --------------------------------------------------------------------------
# Refused: for every role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("who", sorted(protected.ACTORS))
@pytest.mark.parametrize("form", CORE)
def test_a_read_of_a_protected_file_is_refused_for_every_role(guarded, form, who, name):
    """Line 1: every role, no role, an unknown role, a role subagent, a subagent that is not a role."""
    tool_name, tool_input = FORMS[form](guarded, name)
    result = protected.ask(guarded, tool_name, tool_input, who)
    protected.assert_refused_by_rule(result, f"{form} ({tool_name}) on the stand-in {name} by {who}")


def test_a_read_of_a_protected_file_is_refused_while_frozen(hook, tmp_path):
    """The freeze stops writes and leaves reading open (KPI success 3); these two files stay closed."""
    guarded = protected.make_guarded(tmp_path)
    support.set_freeze(guarded.project)
    for name in FILES:
        result = protected.ask(guarded, "Read", {"file_path": str(guarded.path(name))}, "engineer")
        protected.assert_refused_by_rule(result, f"Read on the stand-in {name} by the engineer while frozen")


# --------------------------------------------------------------------------
# Line 5: what a refusal says
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", CORE + ("Bash-copy-with-the-file-as-source",))
def test_a_refusal_names_the_decision_and_nothing_of_the_file(guarded, form, name):
    """Line 5: the rule and DEC-508 or DEC-525; no content, no deny value, not the held-out file's path."""
    tool_name, tool_input = FORMS[form](guarded, name)
    result = protected.ask(guarded, tool_name, tool_input, WIDEST)
    protected.assert_refused_by_rule(result, f"{form} on the stand-in {name}")
    reason = protected.reason_of(result)
    assert re.search(r"\bDEC-(508|525)\b", reason), (
        f"the refusal of {form} on the stand-in {name} names neither DEC-508 nor DEC-525"
    )
    assert re.sub(r"\bDEC-\d+\b", "", reason).strip(" .:;()[]"), "the refusal names a decision and no rule"
    said = protected.output_of(result)
    shown = [index for index, secret in enumerate(guarded.secrets(name)) if secret in said]
    # The values are not put in the message: a failure must not print what a refusal must not print.
    assert not shown, (
        f"the refusal of {form} on the stand-in {name} carries {len(shown)} value(s) it must not "
        f"(positions {shown} of Guarded.secrets): the file's content, a deny value, or the held-out file's path"
    )
