"""W1-25 -- KPI success 4 [CAP-38.b]: the fresh-agent-reconstruction family check is registered.

Settled by the sources (no package affects this file): DEC-186 says a ticket
registers a check by adding a YAML declaration (``id``, ``family``, ``tier``,
``severity``, ``command``) under ``template/governance/kernel/checks/``, and
``gov check --list --json`` lists it; the ticket's ``allowed_paths`` name the
file ``fresh-agent-reconstruction*``. Running checks is W1-26 (DEC-186,
DEC-187). What the declared command does is in ``test_w1_25_resume.py`` (DP-6).
"""

from __future__ import annotations

import w1_25_support as support

FIELDS = ("id", "family", "tier", "severity", "command")


def test_the_declaration_is_a_file_of_the_kernel_checks(raw_project):
    found = sorted((raw_project / support.CHECKS_REL).glob(f"{support.FAMILY}*.yaml"))
    assert len(found) == 1, (f"expected one declaration {support.CHECKS_REL}/{support.FAMILY}*.yaml, "
                             f"found {[path.name for path in found]}")


def test_gov_check_list_names_the_family_check(raw_gov, interface):
    declaration = support.declaration(raw_gov("check", "--list", "--json"), interface)
    for field in FIELDS:
        assert isinstance(declaration.get(field), str) and declaration[field].strip(), \
            f"the declaration's '{field}' is not a non-empty string: {declaration}"
    assert declaration["severity"] in ("hard-block", "warning"), declaration
