"""A registry entry whose quote does not match fails the build (node B5 acceptance check); section_anchors,
supersessions and lifecycle_overrides load correctly off the fixture repo; a registry entry only restricts."""
import pytest

from govbridge.authority import registry


def test_fixture_registry_loads_and_verifies(fixture_repo, registry_path, view_path):
    reg = registry.load(registry_path, verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))
    assert len(reg.section_anchors) == 4
    assert len(reg.supersessions) == 2
    assert len(reg.lifecycle_overrides) == 1
    assert len(reg.class_rules) == 9  # the last class_rules row's {spec/research,spec/reports,lessons}/** expands to 3


def test_wrong_quote_fails_the_build(fixture_repo, registry_path, view_path, tmp_path):
    text = open(registry_path).read()
    bad_path = tmp_path / "bad-registry.yaml"
    bad_path.write_text(text.replace("FX-0010A -- first anchored section", "THIS QUOTE DOES NOT OCCUR ANYWHERE"))
    with pytest.raises(registry.QuoteVerificationError):
        registry.load(str(bad_path), verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))


def test_wrong_line_fails_the_build(fixture_repo, registry_path, view_path, tmp_path):
    text = open(registry_path).read()
    # move the FX-0010A cite's line off by a large amount so the quote is no longer at that line
    bad_path = tmp_path / "bad-line-registry.yaml"
    bad_path.write_text(text.replace("line: 9,\n           quote: 'FX-0010A", "line: 999,\n           quote: 'FX-0010A"))
    with pytest.raises(registry.QuoteVerificationError):
        registry.load(str(bad_path), verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))


def test_anchor_by_item_id_and_for_line(fixture_repo, registry_path, view_path):
    reg = registry.load(registry_path, verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))
    a = reg.anchor_by_item_id("FX-0010A")
    assert a.line_start == 9 and a.line_end == 12
    assert reg.anchor_for_line(a.path, 10) is a
    assert reg.anchor_for_line(a.path, 5) is None  # header lines, unanchored


def test_supersession_whole_vs_scoped(fixture_repo, registry_path, view_path):
    reg = registry.load(registry_path, verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))
    scoped = [s for s in reg.supersessions if s.to_id == "OA-FX-06"][0]
    whole = [s for s in reg.supersessions if s.to_id == "FX-GEN-1"][0]
    assert scoped.is_whole is False
    assert whole.is_whole is True


def test_class_rules_first_match_wins(fixture_repo, registry_path, view_path):
    reg = registry.load(registry_path, verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))
    rule = reg.class_for_path("release/orchestration/fx/GATES/OWNER-DECISION-FX-0007-STOP-CONDITION.md")
    assert rule.cls == "OWNER_DECISION"
    rule2 = reg.class_for_path("fixtures/greenfield/spec/decisions/FX-0001.yaml")
    assert rule2.cls == "FIXTURE"  # fixtures/** must win over spec/decisions/*.yaml (declared first in the file)


def test_lifecycle_override_lookup(fixture_repo, registry_path, view_path):
    reg = registry.load(registry_path, verify_commit="records", view_path=view_path, repo=str(fixture_repo.root))
    override = reg.lifecycle_override_for("FX-WITHDRAWN-0001")
    assert override.lifecycle == "WITHDRAWN"
    assert override.cls == "EVIDENCE_WITHDRAWN"
