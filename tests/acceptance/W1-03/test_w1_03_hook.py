"""W1-03 — the containment check ships as hooks of the kernel.

CAP-58.a: W1-03 is a provider of the default-deny allow-lists, as the second
line behind the guard. KPI success 1: "After every Bash call …".
DEC-124 and DEC-126: the check takes its before-snapshot in the kernel's
PreToolUse hook and compares in the PostToolUse hook.
"""

from __future__ import annotations

import w1_03_support as support


def test_containment_hook_ships_in_the_kernel_template(hook):
    assert hook.is_file(), f"{hook} is not a file"
    assert hook.stat().st_size > 0, f"{hook} is empty"
    assert hook.parent == support.REPO_ROOT / support.HOOK_DIR_REL


def test_the_check_works_from_what_the_call_left_behind(project, sandbox, before_bash, check):
    """The check reads the working tree, not the command text (DEC-123).

    Both hooks are told the call is ``ls -la``. What ran between them changed a
    file outside the ticket's paths all the same.
    """
    call, guard = before_bash(project, "ls -la", support.ENGINEER, support.TICKET_ID, literal=True)
    support.assert_let_through(guard, call)
    support.run_bash(project, "python3 -c \"open('README.md', 'a').write('changed')\"", sandbox)
    result = check(project, call, support.ENGINEER, support.TICKET_ID)
    support.assert_caught(result, "README.md", what="an out-of-scope change left behind by a call shown as `ls -la`")
