"""Success line 1 "on b-dev": the eight stages on a clone of the dev tier of the second synthetic programme.

Marked ``local_only``. Each case clones ``$GOV_DEV_TIERS/b-dev`` (by default ``~/gov-os-workbench/synthetic/b-dev``)
into its own temporary folder and is skipped where this machine has no such tier. The tier itself is never the
project: the tool runs on the clone. The clone is given a path map that classes all of it (as W1-21's dev-tier
cases do), with code intelligence off, and a proposal that retires its legacy rule files and moves nothing.
"""

from __future__ import annotations

import pytest
import yaml

import w1_41_support as support

pytestmark = pytest.mark.local_only

TIER = "b-dev"
TIER_RULE_FILES = ("AGENTS.md", ".cursorrules", ".windsurfrules", ".mcp/tools.json")


@pytest.fixture(scope="module")
def tier_adoption(tmp_path_factory, interface):
    base = tmp_path_factory.mktemp("w1-41-b-dev")
    project = support.clone_tier(TIER, base / TIER)
    if project is None:
        pytest.skip(f"no dev tier at {support.DEV_TIERS / TIER} (GOV_DEV_TIERS)")
    with open(project / ".git" / "info" / "exclude", "a", encoding="utf-8") as exclude:
        exclude.write("\n.gov-runtime/\n")
    support.write(project, support.PATH_MAP_REL,
                  yaml.safe_dump(support.path_map(patterns=("**",), code_intelligence=False), sort_keys=False))
    if not (project / ".gitleaks.toml").exists():
        support.write(project, ".gitleaks.toml", support.base_files()[".gitleaks.toml"])
    support.commit(project, "a path map for the W1-41 tests")
    tracked = support.tree(project)
    rules = [rel for rel in tracked if rel in TIER_RULE_FILES or (rel.startswith(".cursor/rules/")
                                                                  and rel.endswith(".mdc"))]
    adoption = support.Adoption(project, support.make_sandbox(base / "sandbox"), interface)
    adoption.baseline = tracked
    adoption.rules = rules
    adoption.through("A8", [support.entry(rel, "RETIRE", kind="rule-file") for rel in rules])
    return adoption


def test_the_eight_stages_each_leave_an_evidence_record_on_b_dev(tier_adoption):
    records = {stage: tier_adoption.stages[stage].record for stage in support.STAGES}
    assert len(set(records.values())) == len(support.STAGES), \
        f"the eight stages did not leave eight records on the clone of {TIER}: {records}"
    inventory = tier_adoption.stages["A1"]
    missing = sorted(set(tier_adoption.baseline) - set(support.entries_by_path(inventory.front, inventory.record)))
    assert not missing, f"the inventory of the clone leaves out {len(missing)} tracked artefacts, e.g. {missing[:5]}"
    assert tier_adoption.stages["A2"].front.get("unknown") == [], "an artefact of the clone is unknown under '**'"
    backup = tier_adoption.stages["A0"].front.get("backup_ref")
    assert backup and support.resolve(tier_adoption.project, backup), "the backup ref does not resolve in the clone"


def test_b_devs_legacy_rule_files_are_retired_and_everything_else_is_kept(tier_adoption):
    project, now = tier_adoption.project, support.tree(tier_adoption.project)
    assert tier_adoption.rules, f"the clone of {TIER} tracks none of the legacy rule files this case knows"
    for rel in tier_adoption.rules:
        legacy = tier_adoption.baseline[rel]
        assert now.get(rel) != legacy, f"{rel} is still at HEAD as the legacy file"
    assert any(rel.startswith(support.RULESYNC_REL + "/") for rel in now), "nothing was imported into .rulesync/"
    changed = sorted(rel for rel, blob in tier_adoption.baseline.items()
                     if rel not in tier_adoption.rules and not rel.startswith(support.RULESYNC_REL + "/")
                     and now.get(rel) != blob)
    assert not changed, f"artefacts the path map keeps changed or left (native layouts included): {changed[:10]}"
    assert support.porcelain(project) == ""
