"""A tier that is named and has no declared check is never passed over (DEC-489; DEC-449, DEC-454) [CAP-39.a].

The pre-commit hook names two tiers, G1 and G2 (KPI S1). Where the project declares a check for one and none for
the other, running the one and saying nothing of the other would be a gate that ends green without having run
what it names. DEC-489: it refuses. A tier name that is mistyped, or is no tier at all, refuses too.

Two ways in:

- through the hook, as lefthook runs it: a project that declares no check of one of the two tiers cannot commit;
- through the command line the tree has today, ``gov ci checks <tier>...``, where the tiers can be chosen by the
  case. These cases need neither lefthook nor gitleaks, and neither the hook file: they are red today because the
  command runs the tiers that have a declaration and exits 0.

G3 is the one exception DEC-489 makes (a project with no G3 check can push; ``test_w1_40_evidence_record.py``).
"""

from __future__ import annotations

import pytest

import w1_40_support as support


@pytest.mark.parametrize("undeclared", ["G1", "G2"])
def test_a_commit_is_refused_when_a_tier_the_hook_names_has_no_declared_check(new_project, machine, undeclared):
    tiers = tuple(tier for tier in support.TIER_CHECKS if tier != undeclared)
    project = new_project(tiers=tiers)
    done, moved = project.commit(machine())
    assert not moved, (
        f"the project declares no {undeclared} check and the commit passed: the pre-commit gate ran the tier that "
        f"has a declaration and passed over the other:\n{support.said(done)}")
    assert done.returncode != 0


def test_gov_refuses_named_tiers_when_one_of_them_has_no_declared_check(new_project, machine):
    project = new_project(tiers=("G1",), hooks=False)
    dev = machine(lefthook=False, gitleaks=False)
    alone = project.gov(dev, "ci", "checks", "G1")
    assert alone.returncode == 0 and project.ran("G1") == 1, (
        f"the fixture does not hold: the declared G1 check alone does not pass:\n{support.said(alone)}")
    done = project.gov(dev, "ci", "checks", "G1", "G2")
    assert done.returncode != 0, (
        "gov ci checks G1 G2 ended with exit 0 in a project that declares a G1 check and no G2 check: the tier "
        f"without a declaration was passed over:\n{support.said(done)}")


@pytest.mark.parametrize("name", ["G22", "tier2"])
def test_gov_refuses_a_tier_name_that_is_no_tier_beside_a_declared_one(new_project, machine, name):
    """``G22`` is a slip of the hand, ``tier2`` is no tier at all (CAP-39: the tiers are G0 to G6)."""
    project = new_project(tiers=("G1", "G2"), hooks=False)
    dev = machine(lefthook=False, gitleaks=False)
    done = project.gov(dev, "ci", "checks", "G1", name)
    assert done.returncode != 0, (
        f"gov ci checks G1 {name} ended with exit 0: a tier name that is no tier was passed over:\n"
        f"{support.said(done)}")
