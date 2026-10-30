"""KPI 5 of W2-67 (P-IS-7 (a); I2 §2.7 R1, F3): the planted-defect cases' base project is green before any defect.

W1-26's base project (``support.Project``) is red under ``gov check`` before any defect is planted: six hard-block
checks need what a temporary project does not hold (a tool registry, a store, a lexical index, ``.gitleaks.toml``,
the dev tiers). A case that judged its defect by "``gov check`` failed" could therefore never fail. The revised
cases plant their defect on ``support.green_base``, which leaves those six declarations out, and judge the check
they name by its own entry. These cases hold that base green, and show that the six left out are the only checks
red on the full base, none of them a check the revised cases judge.
"""

from __future__ import annotations

import pytest

import w1_26_support as support


@pytest.mark.parametrize("base", ("green_project", "green_project_with_dimensions"))
def test_the_base_project_is_green_before_any_defect(base, request, sandbox, interface):
    """``ok`` and exit 0; no check RED; each check the revised cases judge GREEN with no finding; the checks left
    out are not run, and their families are not GREEN (unmeasured, DEC-425)."""
    project = request.getfixturevalue(base)
    run = support.run_check(project, sandbox)
    result, envelope = support.result_and_envelope(run, interface)
    red = sorted(str(entry.get("id")) for entry in support.checks_of(result)
                 if isinstance(entry, dict) and entry.get("status") == support.RED)
    assert envelope["ok"] is True and run.returncode == support.EXIT_OK and not red, (
        f"the base project is not green before any defect: red checks {red}\n{run.describe()}"
    )
    for check_id in support.JUDGED_CHECKS:
        support.assert_check_green(run, interface, check_id)
    ran = {entry.get("id") for entry in support.checks_of(result) if isinstance(entry, dict)}
    assert not ran & set(support.NOT_MEASURABLE_HERE), \
        f"a check left out of the base still ran: {sorted(ran & set(support.NOT_MEASURABLE_HERE))}"
    for family in ("index freshness", "retrieval regression", "context reproducibility",
                   "adapter/model portability", "secrets indexing", "recovery/rebuild"):
        assert support.family_status(result, family) not in (None, support.GREEN), (
            f"the family {family!r}, whose check is left out of the base, is "
            f"{support.family_status(result, family)!r}: unmeasured must never be GREEN"
        )


def test_the_checks_left_out_of_the_base_are_the_only_red_checks_of_the_full_base(project, sandbox, interface):
    """On the base as built (every kernel declaration), the RED checks are among those ``green_base`` leaves out,
    and every check the revised cases judge is GREEN with no finding: the checks left out are not the checks
    under test."""
    project.commit()
    run = support.run_check(project, sandbox)
    result, _ = support.result_and_envelope(run, interface)
    red = {str(entry.get("id")) for entry in support.checks_of(result)
           if isinstance(entry, dict) and entry.get("status") == support.RED}
    assert red <= set(support.NOT_MEASURABLE_HERE), (
        f"checks red on the full base that green_base does not leave out: {sorted(red - set(support.NOT_MEASURABLE_HERE))}"
        f"\n{run.describe()}"
    )
    for check_id in support.JUDGED_CHECKS:
        support.assert_check_green(run, interface, check_id)
