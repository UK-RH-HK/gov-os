"""W1-50, KPI line 2 (DEC-402): the flag's path, as the guard holds it.

"gov launch does not deny the freeze flag's path when the flag does not exist
at launch, so a launched session leaves no placeholder there."

Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.2, 6.1; release 0.1.2): ``gov launch`` writes no sandbox block and no
deny rule of its own, so there is no literal rule and no sandbox placeholder at the flag's path any more. The cases
that read the built settings' rules for the flag (no literal rule when nothing is there, a literal rule for a flag or
an unmarked file that exists at launch, the patterns for the file tools, the other by-name rules) and the live
session that watched for the sandbox's placeholder are retired.

What stays: **what the guard holds**: a worker's Write, Edit and recognisable Bash writes to the flag's path are
denied whether nothing, a placeholder or a real flag is there.
"""

from __future__ import annotations

import os

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import freeze_project, freeze_sandbox  # noqa: F401  fixtures

ENGINEER = support.ENGINEER


# --------------------------------------------------------------------------
# What the guard still holds
# --------------------------------------------------------------------------

FLAG = support.FLAG_REL
SCRATCH_FILE = ".gov-runtime/scratch/w1-50-held.txt"
BASH_WRITES = (
    f"rm {FLAG}",
    f"rm -f {FLAG}",
    f"mv {FLAG} {SCRATCH_FILE}",
    f"mv {support.OWN_REL} {FLAG}",
    f"cp {support.OWN_REL} {FLAG}",
    f"touch {FLAG}",
    f"echo 'FROZEN owner 2026-10-05T00:00:00Z' > {FLAG}",
    f": > {FLAG}",
    f"echo x >> {FLAG}",
    f"ln -s {{root}}/{support.OWN_REL} {FLAG}",
    f"ln {support.OWN_REL} {FLAG}",
)
AT_THE_PATH = {
    "nothing": lambda project: None,
    "a-placeholder": support.put_placeholder,
    "a-marked-flag": lambda project: support.put_text(project, support.A_MARKER_LINE),
}


@pytest.mark.parametrize("state", sorted(AT_THE_PATH))
@pytest.mark.parametrize("role", (ENGINEER, support.guard_support.TEST_DESIGNER))
def test_the_guard_denies_a_worker_s_write_to_the_flag_s_path(freeze_project, freeze_sandbox, state, role):
    """DEC-176, DEC-311: ``.gov-runtime/`` outside scratch is denied to every role, flag or no flag.

    With a placeholder at the path the project is not frozen (DEC-402), so
    these denials are the path rule's own.
    """
    AT_THE_PATH[state](freeze_project)
    before = os.lstat(support.flag(freeze_project)) if state != "nothing" else None
    for tool_name in ("Write", "Edit"):
        result = support.guard_write(freeze_project, freeze_sandbox, tool_name, rel=FLAG, role=role)
        assert result.decision == "deny", f"with {state} at the path, {tool_name} on {FLAG} by {role}: " \
                                          f"{result.describe()}"
    for command in BASH_WRITES:
        command = command.format(root=freeze_project)
        result = support.guard_bash(freeze_project, freeze_sandbox, command, role=role)
        assert result.decision == "deny", f"with {state} at the path, Bash `{command}` by {role}: {result.describe()}"
    after = os.lstat(support.flag(freeze_project)) if os.path.lexists(support.flag(freeze_project)) else None
    assert (before is None) == (after is None), f"asking the guard changed what is at {FLAG}"
