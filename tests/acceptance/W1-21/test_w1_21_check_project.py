"""The follow-up after W1-41, second run: the project the retrieval-regression check measures names no register
it does not hold (DEC-579).

DEC-579: "A project whose path map names a register that is not in the commit is refused", and the copies of
this repository's path map are repaired first, the check's own with them. The check builds a project of its
own from each dev tier. If that project named a register it does not hold, the stricter rule would refuse it
and the check would answer that no tier could be indexed, where it measured before.

The case runs the declared command (DEC-285) over a stand-in dev tier built here and the suite's stand-in
embeddings endpoint: no model, no daemon, no network, and nothing of this machine's dev tiers. It is green
before the rule is built and holds what must stay once it is: a tier that can be indexed is measured.
"""

from __future__ import annotations

import pytest
import yaml

import w1_21_support as support


@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_the_check_measures_a_dev_tier_whose_project_holds_no_register(box, family_check, ollama, tmp_path):
    tiers = tmp_path / "tiers"
    tier = support.build_fixture(tiers / support.TIERS["A"])
    assert not (tier / "docs" / "DECISION_REGISTER.md").exists(), "the fixture is wrong: the tier holds a register"
    queries = [{"programme": "A", "class": "lookup", "query": "Who reads the tide tables at dawn?",
                "gold": {"must_cite": [support.TIDES], "must_not_cite": []}}]
    support.write(tiers, "dev-queryset.yaml", yaml.safe_dump({"queries": queries}, sort_keys=False))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    run = support.run_check(family_check, elsewhere, box.scratch_env(ollama.host, GOV_DEV_TIERS=str(tiers)))

    assert "Traceback" not in run.output, run.describe()
    assert "unmeasured" not in run.output.lower(), \
        f"a dev tier that holds no register was not measured: its project was refused or not indexed\n{run.describe()}"
    assert run.output.strip(), f"the check measured and printed nothing\n{run.describe()}"
