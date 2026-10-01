"""W1-03 — the containment check ships as a PostToolUse hook of the kernel.

CAP-58.a: W1-03 is a provider of the default-deny allow-lists, as the second
line behind the guard. KPI success 1: "After every Bash call …".
"""

from __future__ import annotations

import w1_03_support as support


def test_containment_hook_ships_in_the_kernel_template(hook):
    assert hook.is_file(), f"{hook} is not a file"
    assert hook.stat().st_size > 0, f"{hook} is empty"
    assert hook.parent == support.REPO_ROOT / support.HOOK_DIR_REL


def test_the_check_works_from_what_the_call_left_behind(project, sandbox, check):
    """The check reads the working tree, not the command text.

    The command in the hook input is harmless; the tree holds an out-of-scope
    change all the same, as it would after a call the guard did not stop.
    """
    support.run_bash(project, "python3 -c \"open('README.md', 'a').write('changed')\"", sandbox)
    result = check(project, "ls -la", support.ENGINEER, support.TICKET_ID)
    support.assert_reported(result, "README.md", what="an out-of-scope change left behind by a call")
