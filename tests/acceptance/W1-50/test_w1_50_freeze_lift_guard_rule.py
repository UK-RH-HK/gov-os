"""KPI success 6 and 7 (DEC-409, rule 3): the guard refuses an agent Bash command that holds the lift form.

"The guard refuses, for every role, any agent Bash command whose text contains
the lift form of gov pause (the --off option), including a command that starts
another Claude Code session with that text in its prompt."

The guard is asked as every guard case of this folder asks it: the kernel's
PreToolUse hook as a process, one JSON object on stdin, in W1-02's fixture
project.

**The border** (``w1_50_freeze_README.md``, "Rule 3: where the border is").
The lift form is a way of running ``gov`` (a word whose last part is ``gov``,
the module ``gov.cli.main``, or the file ``gov/cli/main.py``) followed by the
words ``pause`` and ``--off``. It is refused

1. where it stands as words of a command that is run, whatever stands before
   it in that command (``env``, ``nohup``, ``timeout 5``, an assignment) and
   wherever the command stands (after ``&&``, ``;``, ``|``, in a subshell, in
   a command substitution, also inside a quoted word);
2. anywhere in the text of a command, or of a pipeline, that starts a shell,
   an interpreter or a Claude Code session: ``bash -c``, ``sh -c``, ``eval``,
   ``python3 -c``, ``claude``, ``gov launch``.

Text that is only read, searched, written to a file or put in a commit message
is not the lift form: one quoted word of ``grep``, ``git`` or ``echo``.
The stricter reading holds where the command could run the lift, the laxer one
where it only handles text.

Every role and every spelling: every role on one spelling, every spelling on
one role.
"""

from __future__ import annotations

import json
import re

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import freeze_frozen, freeze_project, freeze_sandbox  # noqa: F401  fixtures

guard_support = support.guard_support
ENGINEER, ORCHESTRATOR = support.ENGINEER, support.ORCHESTRATOR
TICKET, ORCHESTRATOR_TICKET = support.TICKET, support.ORCHESTRATOR_TICKET
CLI = "/home/owner/.local/bin/claude"      # DEC-205: where the launcher starts the CLI from

NAMES_THE_LIFT = re.compile(r"lift|--off", re.IGNORECASE)

# name: the command. Each could run the lift, here or in the session or shell it starts.
LIFT_FORMS = {
    # the command itself, its options in any order and spacing
    "plain": "gov pause --off",
    "wide-spacing": "gov   pause \t  --off",
    "json-after": "gov pause --off --json",
    "json-before": "gov pause --json --off",
    "root-between": "gov pause --root . --off",
    "session-and-role-around": "gov pause --session s1 --off --role owner",
    "gov-by-its-path": "/home/owner/.local/bin/gov pause --off",
    # the module
    "module": "python3 -m gov.cli.main pause --off",
    "module-with-pythonpath": "PYTHONPATH=src python3 -m gov.cli.main pause --off",
    "module-with-python": "python -m gov.cli.main pause --off --json",
    "module-file": "PYTHONPATH=src python3 src/gov/cli/main.py pause --off",
    # behind a command that runs its arguments
    "env": "env gov pause --off",
    "env-u-gov-role": "env -u GOV_ROLE gov pause --off",
    "env-u-gov-role-module": "env -u GOV_ROLE PYTHONPATH=src python3 -m gov.cli.main pause --off",
    "assignment-in-front": "GOV_ROLE= gov pause --off",
    "nohup": "nohup gov pause --off",
    "setsid": "setsid gov pause --off",
    "command": "command gov pause --off",
    "exec": "exec gov pause --off",
    "time": "time gov pause --off",
    "timeout": "timeout 5 gov pause --off",
    "sudo": "sudo gov pause --off",
    # where a command is run
    "after-and": "git status && gov pause --off",
    "after-or": "false || gov pause --off",
    "after-a-semicolon": "git status; gov pause --off",
    "after-a-newline": "git status\ngov pause --off",
    "after-a-pipe": "echo y | gov pause --off",
    "in-a-subshell": "( gov pause --off )",
    "in-a-command-substitution": "echo $(gov pause --off)",
    "in-backticks": "echo `gov pause --off`",
    "in-a-substitution-inside-quotes": 'echo "$(gov pause --off)"',
    # text handed to a shell or an interpreter
    "bash-c": "bash -c 'gov pause --off'",
    "sh-c": 'sh -c "gov pause --off"',
    "bash-lc-among-others": "bash -lc 'cd . && gov pause --off --json'",
    "eval": "eval 'gov pause --off'",
    "python-c": "python3 -c \"import subprocess; subprocess.run(['gov', 'pause', '--off'])\"",
    "piped-into-bash": 'echo "gov pause --off" | bash',
    "piped-into-sh": "printf '%s\\n' 'gov pause --off' | sh",
    # text handed to another Claude Code session
    "claude-p": 'claude -p "run gov pause --off and say what it answered"',
    "claude-by-its-path": f'{CLI} -p "run gov pause --off"',
    "claude-by-its-home-path": '~/.local/bin/claude -p "run gov pause --off"',
    "claude-prompt-after-other-options": 'claude --model opus --output-format json -p "please run: gov pause --off"',
    "claude-prompt-without-p": 'claude "run gov pause --off"',
    "claude-prompt-names-the-module": 'claude -p "run python3 -m gov.cli.main pause --off"',
    "gov-launch": 'gov launch engineer DAEO-zz90 -- -p "run gov pause --off"',
    "gov-launch-by-the-module": 'python3 -m gov.cli.main launch engineer DAEO-zz90 -- -p "run gov pause --off"',
    "here-string-into-claude": 'claude -p <<< "run gov pause --off"',
    "piped-into-claude": 'echo "run gov pause --off and report" | claude -p',
    "piped-into-claude-by-its-path": f'echo "run gov pause --off" | {CLI} -p',
}
DENIED_ALREADY = {"sudo"}   # DEC-083: either reason is fine


def _reason(result):
    try:
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    except (ValueError, KeyError, TypeError):
        return ""


def _assert_lift_refused(result, what, either_reason=False):
    assert result.decision == "deny", f"{what} was not refused: {result.describe()}"
    assert result.returncode == 0, f"{what}: the guard failed instead of deciding: {result.describe()}"
    if not either_reason:
        assert NAMES_THE_LIFT.search(_reason(result)), \
            f"{what}: the refusal does not name the lift of the freeze as its reason: {result.describe()}"


@pytest.mark.parametrize("form", sorted(LIFT_FORMS))
def test_the_guard_refuses_a_command_that_holds_the_lift_form(freeze_project, freeze_sandbox, form):
    command = LIFT_FORMS[form]
    result = support.guard_bash(freeze_project, freeze_sandbox, command, role=ENGINEER, ticket=TICKET)
    _assert_lift_refused(result, f"`{command}` by the engineer", either_reason=form in DENIED_ALREADY)


# who: (GOV_ROLE, GOV_TICKET, subagent type)
CALLERS = {
    "engineer": (ENGINEER, TICKET, None),
    "product-spec": (guard_support.PRODUCT_SPEC, guard_support.PRODUCT_SPEC_TICKET_ID, None),
    "independent-test-designer": (guard_support.TEST_DESIGNER, TICKET, None),
    "independent-auditor": (guard_support.AUDITOR, TICKET, None),
    "research": ("research", TICKET, None),
    "orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, None),
    "no-role": (None, None, None),
    "a-role-nobody-knows": ("owner", None, None),
    "engineer-subagent-of-the-orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, ENGINEER),
    "orchestrator-subagent-of-the-orchestrator": (ORCHESTRATOR, ORCHESTRATOR_TICKET, ORCHESTRATOR),
}


@pytest.mark.parametrize("who", sorted(CALLERS))
def test_the_guard_refuses_the_lift_form_for_every_role(freeze_project, freeze_sandbox, who):
    role, ticket, subagent = CALLERS[who]
    result = guard_support.run_hook(freeze_project, "Bash", guard_support.bash_tool_input("gov pause --off"),
                                    freeze_sandbox, role=role, ticket=ticket, subagent=subagent)
    _assert_lift_refused(result, f"`gov pause --off` by {who}")


def test_the_guard_refuses_the_lift_form_while_frozen(freeze_frozen, freeze_sandbox):
    """The case the rule is for. Today a command without a write target is let through while frozen."""
    result = support.guard_bash(freeze_frozen, freeze_sandbox, "gov pause --off", role=ORCHESTRATOR,
                                ticket=ORCHESTRATOR_TICKET)
    _assert_lift_refused(result, "`gov pause --off` by the orchestrator while frozen")
    assert support.flag(freeze_frozen).read_text(encoding="utf-8") == support.A_MARKER_LINE


# --------------------------------------------------------------------------
# Ordinary work goes on
# --------------------------------------------------------------------------

NOTES = "docs/notes.md"   # a committed file of the fixture project; the test puts the words into it

# name: (GOV_ROLE, GOV_TICKET, the command). Each only reads or writes text, or is not the lift form.
ORDINARY = {
    "grep-for-the-option": (ENGINEER, TICKET, 'grep -rn -- "--off" src/'),
    "grep-for-the-phrase": (ENGINEER, TICKET, f'grep "gov pause --off" {NOTES}'),
    "rg-for-the-phrase": (ENGINEER, TICKET, "rg -n 'gov pause --off' docs tests"),
    "git-log-grep": (ENGINEER, TICKET, 'git log --oneline --grep "pause --off"'),
    "cat-a-file-that-holds-it": (ENGINEER, TICKET, f"cat {NOTES}"),
    "git-show-a-file-that-holds-it": (ENGINEER, TICKET, f"git show HEAD:{NOTES}"),
    "pytest-on-suites-that-hold-it": (ENGINEER, TICKET, "python3 -m pytest tests/acceptance/W1-28 -q -p no:cacheprovider"),
    "a-commit-message": (ENGINEER, TICKET, 'git commit -m "W1-50: gov pause --off refuses under a session (DEC-409)"'),
    "the-words-written-to-a-file": (ENGINEER, TICKET, 'echo "gov pause --off" > src/gov/guard/notes.md'),
    "the-words-piped-into-grep": (ENGINEER, TICKET, 'echo "gov pause --off" | grep -c off'),
    "another-program-s-off-option": (ENGINEER, TICKET, "some-tool --off"),
    "another-program-with-both-words": (ENGINEER, TICKET, "playerctl pause --off"),
    "gov-pause": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "gov pause"),
    "gov-pause-json": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "python3 -m gov.cli.main pause --json"),
    "gov-pause-cancel-agents": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "gov pause --cancel-agents"),
    "gov-pause-rollback": (ORCHESTRATOR, ORCHESTRATOR_TICKET, f"gov pause --rollback {TICKET}"),
    "a-session-started-without-the-words": (ORCHESTRATOR, ORCHESTRATOR_TICKET, 'claude -p "run the unit tests"'),
}


@pytest.mark.parametrize("name", sorted(ORDINARY))
def test_the_rule_leaves_ordinary_work_alone(freeze_project, freeze_sandbox, name):
    """Reading, searching, committing and writing the words, and setting a freeze, are decided as without the rule:
    each of these commands is let through today and stays let through."""
    role, ticket, command = ORDINARY[name]
    (freeze_project / NOTES).write_text("notes\nthe owner lifts with: gov pause --off\n", encoding="utf-8")
    result = support.guard_bash(freeze_project, freeze_sandbox, command, role=role, ticket=ticket)
    assert result.decision == "allow" and result.returncode == 0, \
        f"`{command}` by {role} was not let through: {result.describe()}"
