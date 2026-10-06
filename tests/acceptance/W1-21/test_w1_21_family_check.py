"""KPI success 5: the ticket registers the retrieval-regression family check [CAP-38.b].

A check is registered by a declaration under the kernel template (DEC-186) with five fields, and its command is
run by ``sh -c`` in the project's root, exit code 0 being green (DEC-285). These cases hold the registration and
what the command does where it cannot measure. The cases that run the declared command over the dev query set,
green at the recorded baselines and red below them, are not written: how the command finds the query set and
where the baselines are recorded is package DP-7. The baselines themselves are measured in
``test_w1_21_dev_tier.py``.
"""

from __future__ import annotations

import pytest

import w1_21_support as support


def test_the_check_is_registered_with_its_five_fields(family_check):
    for field in support.CHECK_FIELDS:
        assert isinstance(family_check.get(field), (str, int)) and str(family_check[field]).strip(), \
            f"the declaration has no {field}: {family_check!r}"


@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_where_nothing_is_indexed_the_check_is_not_green_and_builds_nothing(box, family_check, repo):
    """As the index-freshness check does where no index exists (DEC-342): it cannot measure, so it is not green;
    it ends with a line that says why, without a traceback, and it builds no index to make itself pass."""
    before = support.tree(repo)
    run = support.run_check(family_check, repo, box.scratch_env())
    assert "Traceback" not in run.output, run.describe()
    assert run.returncode != 0, f"nothing was measured and the check is green\n{run.describe()}"
    assert run.output.strip(), "the check ended red without a line that says why"
    assert support.tree(repo) == before, "the check built or changed a file of the project"


# ---- green, red and "unmeasured" runs (DEC-425)


@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_the_check_is_green_when_the_dev_tiers_meet_the_baselines(box, family_check, repo, ollama):
    """DEC-425: hit@5 >= 80 and forbidden citations <= 2. A project with dev tiers that meet the baselines reports
    green (exit 0)."""
    box.build(repo, ollama.host)
    env = box.scratch_env(ollama.host, GOV_DEV_TIERS=str(support.DEV_TIERS))
    run = support.run_check(family_check, repo, env)
    assert run.returncode == 0, f"the baselines are met and the check is not green\n{run.describe()}"


@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_the_check_is_red_when_the_dev_tiers_fail_the_baselines(box, family_check, repo, ollama):
    """DEC-425: hit@5 < 80 or forbidden > 2. A project with dev tiers that fail the baselines reports red
    (exit != 0)."""
    box.build(repo, ollama.host)
    env = box.scratch_env(ollama.host, GOV_DEV_TIERS=str(support.DEV_TIERS))
    run = support.run_check(family_check, repo, env)
    assert run.returncode != 0, f"the baselines are not met and the check is green\n{run.describe()}"


@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_without_dev_tiers_the_check_reports_unmeasured_and_is_not_green(box, family_check, repo, ollama):
    """DEC-425: where GOV_DEV_TIERS is not configured, the check reports "unmeasured" as a warning and is never
    shown as green. Severity: hard-block where the query set is configured."""
    box.build(repo, ollama.host)
    env = box.scratch_env(ollama.host)
    env.pop("GOV_DEV_TIERS", None)
    run = support.run_check(family_check, repo, env)
    assert run.returncode != 0, f"no dev tiers are configured and the check is green\n{run.describe()}"
    assert "unmeasured" in run.output.lower(), \
        f"no dev tiers are configured and the output does not say 'unmeasured'\n{run.describe()}"
