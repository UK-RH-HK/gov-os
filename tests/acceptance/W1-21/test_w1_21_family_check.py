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


@pytest.mark.local_only
@pytest.mark.needs("gitleaks", "sqlite_vec", "ollama", "reranker")
def test_the_check_is_green_when_the_dev_tiers_meet_the_baselines(box, family_check, repo):
    """DEC-425: hit@5 >= 80 and forbidden citations <= 2. A project with dev tiers that meet the baselines reports
    green (exit 0). Needs the real Ollama endpoint and the reranker to produce hit@5 above the pass line; the
    stand-in vectors score only 73.2."""
    box.build(repo, env=box.real_env())
    env = box.real_env()
    env["GOV_DEV_TIERS"] = str(support.DEV_TIERS)
    run = support.run_check(family_check, repo, env)
    assert run.returncode == 0, f"the baselines are met and the check is not green\n{run.describe()}"


def _planted_failing_tiers(folder):
    """Dev tiers that fail the baselines whatever the retrieval: the dev tiers themselves (linked, never changed)
    and a copy of their dev query set whose every ``must_cite`` path is one that no tier holds, so no query can be a
    hit and the mean hit@5 is 0; None when this machine has no dev tiers. The failure is planted, so it does not
    rest on the stand-in vectors scoring under the pass line (they did, 73.2, before W2-13's ranked lexical route;
    with it they score 80.5; DEC-1055)."""
    import yaml

    if not support.QUERY_SET.is_file() or not all((support.DEV_TIERS / tier / ".git").exists()
                                                  for tier in ("a-dev", "b-dev")):
        return None
    folder.mkdir(parents=True)
    for tier in ("a-dev", "b-dev"):
        (folder / tier).symlink_to(support.DEV_TIERS / tier, target_is_directory=True)
    document = yaml.safe_load(support.QUERY_SET.read_text(encoding="utf-8"))
    for entry in document["queries"]:
        gold = entry.get("gold") or {}
        gold["must_cite"] = [f"planted-nowhere/{path}" for path in gold.get("must_cite") or []] or ["planted-nowhere"]
        entry["gold"] = gold
    (folder / support.QUERY_SET.name).write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return folder


@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_the_check_is_red_when_the_dev_tiers_fail_the_baselines(box, family_check, repo, ollama, tmp_path):
    """DEC-425: hit@5 < 80 or forbidden > 2. A project with dev tiers that fail the baselines reports red
    (exit != 0). The tiers are made to fail: their query set's gold names paths no tier holds, so hit@5 is 0; the
    check measures them (it does not stop "unmeasured") and is red."""
    tiers = _planted_failing_tiers(tmp_path / "planted-tiers")
    if tiers is None:
        pytest.skip(f"no dev tiers and dev query set at {support.DEV_TIERS} (GOV_DEV_TIERS)")
    box.build(repo, ollama.host)
    env = box.scratch_env(ollama.host, GOV_DEV_TIERS=str(tiers))
    run = support.run_check(family_check, repo, env)
    assert "unmeasured" not in run.output.lower(), f"the planted tiers were not measured\n{run.describe()}"
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
