"""W1-03 — the nine Bash write forms of S0b2 I-06 are caught.

KPI success 3: "All nine Bash write forms from S0b2 I-06 are caught".
DEC-123: all nine are tested by their effect inside the repository. A write
outside the repository through an opaque form is an accepted residual and is
not tested.

The nine forms, from the I-06 row of S0b2's integration report ("9 Bash forms
cannot be reliably detected"):

1. writes inside ``$(…)`` or backticks;
2. ``perl -e``, ``ruby -e``, ``node -e``;
3. unknown binaries;
4. process substitution;
5. ``base64 -d | bash``;
6. ``$VAR`` commands;
7. aliases and functions;
8. ``git checkout`` and ``git reset --hard``;
9. ``curl -o`` and ``wget -O``.

Forms 1 to 7 and 9 are each run three ways: against a file outside the
engineer's paths, against an acceptance test, and with the command given to the
hooks word for word. Form 8 writes nothing new; it puts older content back or
discards uncommitted work, and has tests of its own below.

Form 9 is run as ``curl -o`` with a ``file://`` address, which uses no network.
``wget -O`` needs a server and is not run; its effect in the repository is the
same file write. ``ruby``, ``node``, ``perl`` and ``curl`` cases are skipped on
a machine that lacks the program.

Every command is a ``str.format`` template: a literal brace is doubled.
"""

from __future__ import annotations

import base64
import shutil

import pytest

import w1_03_support as support

ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID
WBS = support.TICKET_WBS_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE_FILE

UNKNOWN_BINARY_REL = "bin/tidy-up"          # under the sandbox's directory outside the project
UNKNOWN_BINARY_TEXT = "#!/bin/sh\nprintf 'changed\\n' >> \"$1\"\n"


def _b64(text):
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


# name: (I-06 form number, program the case needs or None, command for a target path)
FORMS = {
    "1-command-substitution": (1, None, lambda t: ": \"$(printf 'changed\\n' >> " + t + ")\""),
    "1-backticks": (1, None, lambda t: ": \"`printf 'changed\\n' >> " + t + "`\""),
    "2-perl-e": (2, "perl", lambda t: (
        "perl -e 'open(my $f, \">>\", \"" + t + "\") or die; print $f \"changed\\n\"; close($f)'")),
    "2-ruby-e": (2, "ruby", lambda t: "ruby -e 'File.write(\"" + t + "\", \"changed\\n\", mode: \"a\")'"),
    "2-node-e": (2, "node", lambda t: "node -e 'require(\"fs\").appendFileSync(\"" + t + "\", \"changed\\n\")'"),
    "3-unknown-binary": (3, None, lambda t: "{elsewhere}/" + UNKNOWN_BINARY_REL + " " + t),
    "4-process-substitution-read": (4, None, lambda t: "cat <(printf 'changed\\n' >> " + t + ")"),
    "4-process-substitution-write": (4, None, lambda t: "printf 'changed\\n' > >(cat >> " + t + ")"),
    "5-base64-to-bash": (5, "base64", lambda t: (
        "echo " + _b64("printf 'changed\\n' >> " + t) + " | base64 -d | bash")),
    "6-command-in-a-variable": (6, None, lambda t: (
        "c=\"tee -a " + t + "\"; printf 'changed\\n' | $c > /dev/null")),
    "7-shell-function": (7, None, lambda t: "w() {{ printf 'changed\\n' >> " + t + "; }}; w"),
    "7-shell-alias": (7, None, lambda t: (
        "shopt -s expand_aliases\nalias w='tee -a " + t + "'\nprintf 'changed\\n' | w > /dev/null")),
    "9-curl-o": (9, "curl", lambda t: "curl -s -o " + t + " file://{root}/docs/notes.md"),
}
NAMES = sorted(FORMS)


def _command(name, target, sandbox):
    """The command of a form for ``target``; skips when the machine lacks the program it needs."""
    _, program, make = FORMS[name]
    if program is not None and shutil.which(program) is None:
        pytest.skip(f"{program} is not installed on this machine")
    tool = sandbox.elsewhere / UNKNOWN_BINARY_REL
    tool.parent.mkdir(parents=True, exist_ok=True)
    tool.write_text(UNKNOWN_BINARY_TEXT, encoding="utf-8")
    tool.chmod(0o755)
    return make(target)


@pytest.mark.parametrize("name", NAMES)
def test_an_i06_form_outside_the_ticket_paths_is_caught(project, sandbox, after_bash, name):
    command = _command(name, "README.md", sandbox)
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    support.assert_caught(result, "README.md", what=f"`{command}` by the engineer on {TICKET}")


@pytest.mark.parametrize("name", NAMES)
def test_an_i06_form_into_the_acceptance_tests_is_restored_and_recorded(project, sandbox, after_bash, name):
    """KPI success 2 through each form: the file holds its HEAD content again and the breach is recorded."""
    command = _command(name, ACCEPTANCE_FILE, sandbox)
    result = after_bash(project, command, ENGINEER, TICKET, changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the engineer on {TICKET}"
    assert support.read(project, ACCEPTANCE_FILE) == support.head_text(project, ACCEPTANCE_FILE), (
        f"{what}: {ACCEPTANCE_FILE} was not restored from HEAD"
    )
    assert support.porcelain(project, ACCEPTANCE) == "", (
        f"{what}: tests/acceptance still differs from HEAD:\n" + support.porcelain(project, ACCEPTANCE)
    )
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)


@pytest.mark.parametrize("name", NAMES)
def test_an_i06_form_given_word_for_word_passes_neither_line_unseen(project, sandbox, before_bash, check, name):
    """The two lines together: the guard stops the call, or it runs and the check catches its effect."""
    command = _command(name, "README.md", sandbox)
    seen = len(support.finding_lines(project))
    call, guard = before_bash(project, command, ENGINEER, TICKET, literal=True)
    what = f"`{call.command}` by the engineer on {TICKET}"
    if guard.decision in ("deny", "ask"):
        assert support.porcelain_all(project) == "", f"{what}: the PreToolUse hook itself changed the tree"
        return
    support.assert_let_through(guard, call)
    bash = support.run_bash(project, call.command, sandbox)
    support.assert_changed(project, "README.md", command=call.command)
    result = check(project, call, ENGINEER, TICKET, bash=bash, seen=seen)
    support.assert_caught(result, "README.md", what=what)


# --------------------------------------------------------------------------
# Form 8: git checkout and git reset --hard
# --------------------------------------------------------------------------

def _second_revision(project):
    """One more commit in the fixture's history, so that ``HEAD~1`` holds older content."""
    (project / "README.md").write_text("# Fixture project\nsecond revision\n", encoding="utf-8")
    (project / ACCEPTANCE_FILE).write_text("VALUE = 2\n", encoding="utf-8")
    support.commit_all(project, "second revision")


def test_git_checkout_of_an_older_revision_outside_the_ticket_paths_is_caught(project, after_bash):
    _second_revision(project)
    command = "git checkout HEAD~1 -- README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    support.assert_caught(result, "README.md", what=f"`{command}` by the engineer on {TICKET}")


def test_git_checkout_of_an_older_acceptance_test_is_restored_from_head(project, after_bash):
    """The command stages the older content. Afterwards the file and the index hold HEAD's again."""
    _second_revision(project)
    command = f"git checkout HEAD~1 -- {ACCEPTANCE_FILE}"
    result = after_bash(project, command, ENGINEER, TICKET, changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the engineer on {TICKET}"
    assert support.read(project, ACCEPTANCE_FILE) == "VALUE = 2\n", (
        f"{what}: {ACCEPTANCE_FILE} does not hold its HEAD content"
    )
    assert support.porcelain(project, ACCEPTANCE) == "", (
        f"{what}: tests/acceptance still differs from HEAD:\n" + support.porcelain(project, ACCEPTANCE)
    )
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)


DRAFT = f"{ACCEPTANCE}/{WBS}/test_draft.py"
NEW_DIRECTORY_TEST = f"{ACCEPTANCE}/W1-77/test_new.py"
OTHERS_WORK = (
    f"echo '# designer' >> {ACCEPTANCE_FILE} "
    f"&& echo draft > {DRAFT} && git add {DRAFT} "
    f"&& mkdir -p {ACCEPTANCE}/W1-77 && echo new > {NEW_DIRECTORY_TEST} "
    "&& echo '# someone' >> docs/notes.md "
    f"&& echo '# engineer' >> {SOURCE}"
)

# name: (command, other roles' uncommitted paths it discards, other roles' uncommitted paths it leaves)
DISCARDS = {
    "git-reset-hard": ("git reset --hard", (ACCEPTANCE_FILE, DRAFT, "docs/notes.md"), (NEW_DIRECTORY_TEST,)),
    "git-checkout-dot": ("git checkout -- .", (ACCEPTANCE_FILE, "docs/notes.md"), (DRAFT, NEW_DIRECTORY_TEST)),
}


@pytest.mark.parametrize("case", sorted(DISCARDS), ids=sorted(DISCARDS))
def test_a_git_command_that_discards_another_role_s_uncommitted_work_is_caught(project, sandbox, earlier_work,
                                                                              before_bash, check, case):
    """The effect of this form on a dirty tree: paths that were changed before the call no longer are.

    The call changed them, outside the engineer's paths. The work cannot be
    brought back; the call must not pass without a report and a finding. The
    engineer's own discarded work inside the ticket's paths is no finding.
    """
    command, discarded, left = DISCARDS[case]
    earlier_work(project, OTHERS_WORK, changed=[*discarded, *left, SOURCE])
    kept = {path: support.read(project, path) for path in left}
    seen = len(support.finding_lines(project))
    call, guard = before_bash(project, command, ENGINEER, TICKET)
    support.assert_let_through(guard, call)
    bash = support.run_bash(project, call.command, sandbox)
    status = support.porcelain_all(project)
    for path in (*discarded, SOURCE):
        assert path not in status, f"the fixture command `{command}` did not discard the change to {path}:\n{status}"
    result = check(project, call, ENGINEER, TICKET, bash=bash, seen=seen)
    what = f"`{command}` by the engineer on {TICKET}, on a tree with other roles' uncommitted work"
    support.assert_caught(result, *discarded, what=what)
    assert SOURCE not in result.report, f"{what}: the report names the in-scope file {SOURCE}: {result.report!r}"
    support.assert_not_recorded(result, SOURCE, *left, what=what)
    for path, text in kept.items():
        assert support.read(project, path) == text, f"{what}: {path}, which the command left alone, was touched"


def test_discarding_one_s_own_uncommitted_work_is_no_finding(project, earlier_work, after_bash):
    earlier_work(project, f"echo '# engineer' >> {SOURCE}", changed=[SOURCE])
    command = f"git checkout -- {SOURCE}"
    result = after_bash(project, command, ENGINEER, TICKET)
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_silent(result, what)
    assert support.read(project, SOURCE) == support.head_text(project, SOURCE), (
        f"{what}: the check brought the discarded change back"
    )
