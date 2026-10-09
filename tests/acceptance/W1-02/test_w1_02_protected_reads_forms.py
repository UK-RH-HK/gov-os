"""W1-02 — more spellings of a read of the settings file and of the held-out file (DEC-508, DEC-525).

The order stands as ``test_w1_02_protected_reads.py`` states it: the guard
refuses any agent tool call that reads either file; a read is a file tool whose
expanded targets (globs included) take the file in, or a shell command whose
file targets, once expanded, include the file. A review found spellings of such
a read that no case held. Each form below is visible in the hook input, reads
one of the two files, and is refused by a rule's decision:

1. a search whose glob is the file's own name, or is anchored at the search root;
2. an input redirect in every spelling (glued to punctuation, ``$(<file)``, ``<>``);
3. a command substitution in backticks;
4. a brace expansion that produces the file's name, in a shell word and in a tool's glob;
5. a command substitution inside ``git diff --stat`` and ``git status``;
6. a change into the folder, then a search or a listing that names no path;
7. ``cd`` with an option, and ``pushd``;
8. the file's name glued to a prefix in one word (``@file``, ``-f<file>``).

Beside them, what must keep working near the two files.

Both files are stand-ins in a temporary project (``w1_02_protected_support``).
The held-out file's path is taken from the guard's own module and never typed.
"""

from __future__ import annotations

import json
import os

import pytest

import w1_02_protected_support as protected
import w1_02_support as support

FILES = sorted(protected.PROTECTED)
SETTINGS = "settings-file"
WIDEST = "orchestrator"   # the role with the widest scope: what it is refused, no role is given
OTHER_ROLE = "engineer"


def _base(g, name):
    return os.path.basename(g.rel(name))


def _neighbour(g, name):
    """The bare name of another file in the folder that holds the protected file."""
    return os.path.basename(g.neighbour_rel(name))


def _command(g, name, text):
    """``{rel}`` and ``{abs}`` are the file, ``{dir}`` its folder, ``{base}`` its name;
    ``{nrel}`` is another file of the folder and ``{nb}`` that file's name."""
    return text.format(rel=g.rel(name), abs=g.path(name), dir=g.folder_rel(name), base=_base(g, name),
                       nrel=g.neighbour_rel(name), nb=_neighbour(g, name))


def _ask_bash(g, name, text, who=WIDEST):
    command = _command(g, name, text)
    return protected.ask(g, "Bash", support.bash_tool_input(command), who)


# --------------------------------------------------------------------------
# 1. A search whose glob is the file's own name, or is anchored at the search root
# --------------------------------------------------------------------------

# name -> the Grep input for the protected file ``n`` of the project ``g``.
SEARCHES = {
    "from-the-root-with-the-bare-name": lambda g, n: {"pattern": ".", "path": str(g.project), "glob": _base(g, n)},
    "with-no-path-and-the-bare-name": lambda g, n: {"pattern": ".", "glob": _base(g, n)},
    "from-the-root-with-a-glob-anchored-by-a-slash": lambda g, n: {"pattern": ".", "path": str(g.project),
                                                                  "glob": f"/{g.rel(n)}"},
    "from-the-root-with-braces-around-the-name": lambda g, n: {"pattern": ".", "path": str(g.project),
                                                              "glob": "{" + _base(g, n) + ",w1-02-other.md}"},
}

# The folders between the project root and the folder that holds the file: (file, number of path parts).
BETWEEN = [(name, depth) for name in FILES
           for depth in range(1, len(os.path.dirname(protected.PROTECTED[name]).split("/")))]


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(SEARCHES))
def test_a_search_whose_glob_names_the_file_is_refused(guarded, form, name):
    """Form 1 (and form 4 for a tool's glob): a glob with no wildcard is still a glob that takes the file in."""
    result = protected.ask(guarded, "Grep", SEARCHES[form](guarded, name), WIDEST)
    protected.assert_refused_by_rule(result, f"Grep {form} on the stand-in {name} by the {WIDEST}")


@pytest.mark.parametrize("name,depth", BETWEEN, ids=[f"{name}-{depth}-above" for name, depth in BETWEEN])
def test_a_search_from_a_folder_above_with_the_bare_name_as_its_glob_is_refused(guarded, name, depth):
    """Form 1: the same search from a folder between the root and the folder that holds the file."""
    between = "/".join(guarded.folder_rel(name).split("/")[:depth])
    tool_input = {"pattern": ".", "path": str(guarded.project / between), "glob": _base(guarded, name)}
    result = protected.ask(guarded, "Grep", tool_input, WIDEST)
    protected.assert_refused_by_rule(result, f"Grep from a folder above the stand-in {name} with its bare name")


@pytest.mark.parametrize("name", FILES)
def test_a_listing_glob_with_braces_around_the_name_is_refused(guarded, name):
    """Form 4 for a file tool: Glob expands braces, so the pattern takes the file in."""
    pattern = guarded.folder_rel(name) + "/{" + _base(guarded, name) + ",w1-02-other.md}"
    result = protected.ask(guarded, "Glob", {"pattern": pattern}, WIDEST)
    protected.assert_refused_by_rule(result, f"Glob with braces around the name of the stand-in {name}")


# --------------------------------------------------------------------------
# 2 to 8. Shell commands
# --------------------------------------------------------------------------

COMMANDS = {
    # 2. An input redirect in every spelling.
    "redirect-glued-after-a-semicolon": "echo a;<{rel} cat",
    "redirect-glued-after-a-parenthesis": "(<{rel} cat)",
    "redirect-glued-after-and": "true&&<{rel} cat",
    "redirect-glued-after-a-pipe": "true|<{rel} cat",
    "dollar-parenthesis-redirect": "echo $(<{rel})",
    "dollar-parenthesis-redirect-in-double-quotes": 'echo "$(<{rel})"',
    "read-write-redirect": "cat <>{rel}",
    # 3. A command substitution in backticks.
    "backticks": "echo `cat {rel}`",
    "backticks-in-double-quotes": 'echo "`cat {rel}`"',
    # 4. A brace expansion that produces the file's name.
    "braces-with-the-name-first": "cat {dir}/{{{base},{nb}}}",
    "braces-with-the-name-last": "cat {dir}/{{{nb},{base}}}",
    # 5. A command substitution inside the two git forms that stay allowed.
    "git-diff-stat-with-a-substitution": 'git diff --stat "$(cat {rel})"',
    "git-diff-stat-with-backticks": "git diff --stat `cat {rel}`",
    "git-status-with-a-substitution": 'git status "$(cat {rel})"',
    "git-status-with-backticks": "git status `cat {rel}`",
    "git-diff-stat-with-a-process-substitution": "git diff --stat <(cat {rel})",
    "a-substitution-in-a-here-string": 'cat <<< "$(cat {rel})"',
    # 6. A change into the folder, then a search or a listing that names no path.
    "cd-then-grep-r-with-no-path": "cd {dir} && grep -r VALUE",
    "cd-then-rg-with-no-path": "cd {dir} && rg VALUE",
    "cd-semicolon-grep-rn-with-no-path": "cd {dir}; grep -rn VALUE",
    "cd-then-ls-with-no-path": "cd {dir} && ls",
    # 7. cd with an option, and pushd.
    "cd-P-then-the-bare-name": "cd -P {dir} && cat {base}",
    "cd-two-dashes-then-the-bare-name": "cd -- {dir} && cat {base}",
    "pushd-then-the-bare-name": "pushd {dir} && cat {base}",
    # 8. The file's name glued to a prefix in one word.
    "at-sign-argument-file": "python3 -m pytest @{rel}",
    "at-sign-response-file": "gcc @{rel}",
    "glued-to-a-short-option": "grep -f{rel} README.md",
}
# Two forms asked of another role as well; neither is a write, so no other rule decides them.
FOR_ANOTHER_ROLE = ("redirect-glued-after-a-semicolon", "backticks")


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(COMMANDS))
def test_a_shell_spelling_of_a_read_is_refused(guarded, form, name):
    """Forms 2 to 8: the shell opens the file in each of these, whatever the role may write."""
    result = _ask_bash(guarded, name, COMMANDS[form])
    protected.assert_refused_by_rule(result, f"Bash {form} on the stand-in {name} by the {WIDEST}")


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", FOR_ANOTHER_ROLE)
def test_a_shell_spelling_of_a_read_is_refused_for_another_role(guarded, form, name):
    """Every role: the existing cases hold the rule for eleven actors; two of these forms for one more."""
    result = _ask_bash(guarded, name, COMMANDS[form], OTHER_ROLE)
    protected.assert_refused_by_rule(result, f"Bash {form} on the stand-in {name} by the {OTHER_ROLE}")


@pytest.mark.parametrize("name", FILES)
def test_a_search_with_no_path_in_a_session_that_stands_in_the_folder_is_refused(guarded, name):
    """Form 6 without the ``cd``: the hook input says where the command runs (``cwd``)."""
    role, ticket, subagent = protected.ACTORS[WIDEST]
    data = support.payload(guarded.project, "Bash", support.bash_tool_input("grep -r VALUE"), guarded.sandbox,
                           subagent)
    data["cwd"] = str(guarded.folder(name))
    result = support.run_hook_raw(guarded.project, json.dumps(data), guarded.sandbox, role, ticket)
    protected.assert_refused_by_rule(result, f"`grep -r VALUE` in the folder of the stand-in {name}")


# --------------------------------------------------------------------------
# What keeps working: green before and after
# --------------------------------------------------------------------------

NEAR_COMMANDS = {
    "cd-then-another-file-by-its-bare-name": "cd {dir} && cat {nb}",
    "input-redirect-from-another-file": "wc -c < {nrel}",
    "braces-over-other-names": "cat {dir}/{{{nb},w1-02-other.md}}",
}
GIT_WITH_A_SUBSTITUTION = {
    "diff-stat": 'git diff --stat "$(git rev-parse HEAD)"',
    "status": 'git status "$(git rev-parse --show-toplevel)"',
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("form", sorted(NEAR_COMMANDS))
def test_the_same_spelling_on_another_file_of_the_folder_stays_allowed(guarded, form, name):
    """The rule closes one file of the folder: ``cd``, a redirect and braces stay usable beside it."""
    result = _ask_bash(guarded, name, NEAR_COMMANDS[form])
    protected.assert_allowed(result, f"Bash {form} beside the stand-in {name} by the {WIDEST}")


@pytest.mark.parametrize("name", FILES)
def test_a_search_from_the_root_whose_glob_is_another_file_s_name_stays_allowed(guarded, name):
    """A glob with no wildcard that names another file takes neither protected file in."""
    tool_input = {"pattern": ".", "path": str(guarded.project), "glob": _neighbour(guarded, name)}
    result = protected.ask(guarded, "Grep", tool_input, WIDEST)
    protected.assert_allowed(result, f"Grep from the root with the name of a neighbour of the stand-in {name}")


@pytest.mark.parametrize("form", sorted(GIT_WITH_A_SUBSTITUTION))
def test_git_diff_stat_and_git_status_with_a_substitution_that_reads_neither_file_stay_allowed(guarded, form):
    """A substitution is refused for what it reads, not for being one."""
    command = GIT_WITH_A_SUBSTITUTION[form]
    result = protected.ask(guarded, "Bash", support.bash_tool_input(command), WIDEST)
    protected.assert_allowed(result, f"Bash `{command}` by the {WIDEST}")
