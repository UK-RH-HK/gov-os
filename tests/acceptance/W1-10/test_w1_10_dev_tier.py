"""KPI success 3: full load of a dev tier < 5 s.

A dev tier is a synthetic product repository under ``GOV_DEV_TIERS``. The tests load a clone, never the tier itself.
"""

from __future__ import annotations

import pytest

import w1_10_support as support


@pytest.fixture()
def tier(request, tmp_path):
    source = support.DEV_TIERS / request.param
    if not (source / ".git").exists():
        pytest.skip(f"no dev tier at {source} (GOV_DEV_TIERS)")
    return support.clone(source, tmp_path / "tier")


@pytest.mark.local_only
@pytest.mark.parametrize("tier", support.DEV_TIER_NAMES, indirect=True)
def test_a_full_load_of_a_dev_tier_takes_less_than_5_seconds(api, tier):
    summary, seconds = api.timed_load(tier)
    assert (tier / support.STORE_REL).is_file(), f"load did not write {support.STORE_REL}"
    assert support.is_digest(summary["digest"])
    assert seconds < support.FULL_LOAD_LIMIT_S, f"the full load took {seconds:.2f} s"


@pytest.mark.local_only
@pytest.mark.parametrize("tier", support.DEV_TIER_NAMES, indirect=True)
def test_a_dev_tier_loads_to_the_same_digest_twice(api, tier):
    first = api.load(tier)
    assert api.load(tier)["digest"] == first["digest"]
    assert sorted(support.by_commit(api.commits(tier))) == support.all_commits(tier)
