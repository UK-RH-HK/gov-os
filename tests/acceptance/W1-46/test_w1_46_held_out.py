"""W1-46 -- no file of this ticket names a held-out path.

KPI failure 9: "An acceptance test or implementation file of this ticket reads
or names the qualification oracle".

Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.2, 2.7, 6.1; release 0.1.2): the launcher builds no ``Read`` deny
rule for the held-out directory and no longer reads ``governance/project/held-out.yaml``; a read of a hidden set is
caught by the transcript scan, not prevented. The cases that asserted the held-out ``Read`` rules and the refusal of
a broken ``held-out.yaml`` (DEC-218, DEC-242) are retired.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

w47 = support.w47


def test_no_file_of_this_ticket_names_a_held_out_path():
    """KPI failure 9. The committed list is read at run time, as in W1-47; no value is ever shown.

    The files: this suite, and what exists under the ticket's ``allowed_paths``.
    Holds before implementation.
    """
    configured = w47.load_configured()
    files = w47.files_matching((
        "tests/acceptance/W1-46/**/*", "src/gov/launch/**/*", "src/gov/cli/**/*", "src/gov/guard/**/*",
        "template/governance/kernel/launch/**/*", "template/governance/kernel/hooks/pretooluse*",
        "template/governance/kernel/roles/research*", ".claude/agents/research.md", support.ROSTER_REL,
        "tests/unit/launch/**/*", "tests/unit/guard/**/*", support.ALLOWLIST_REL,
    ))
    assert files, "no file of the ticket was found"
    naming = [str(path.relative_to(support.REPO_ROOT)) for path in w47.files_naming(files, configured.values)]
    if naming:
        pytest.fail(f"these files of the ticket name a held-out path (the path is not shown): {naming}", pytrace=False)
