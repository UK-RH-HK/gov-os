"""The WHY chain (ARCHITECTURE.md section 6.2) on the fixture repo: stages in the owner's order, every present hop
carries its edge label and citation, and an absent stage is reported MISSING (never silently filled)."""
from govbridge.graph import why


def test_why_stages_present_in_order(fixture_repo, view_path, registry_path):
    result = why.why("FX-0001", repo=str(fixture_repo.root), view_path=view_path, registry_path=registry_path)
    assert list(result["stages"].keys()) == list(why.STAGES)


def test_why_lessons_stage_present_for_research_mention(fixture_repo, view_path, registry_path):
    result = why.why("FX-0001", repo=str(fixture_repo.root), view_path=view_path, registry_path=registry_path)
    lessons = result["stages"]["lessons"]
    assert lessons["status"] == "PRESENT"
    assert any(h["type"] == "MENTIONS" and "FX-RES-0001" in h["evidence_occurrence"] for h in lessons["hops"])


def test_why_dependency_stage_missing_without_code_route(fixture_repo, view_path, registry_path):
    result = why.why("FX-0001", repo=str(fixture_repo.root), view_path=view_path, registry_path=registry_path)
    dep = result["stages"]["dependency"]
    assert dep["status"] == "MISSING: dependency"
    assert dep["hops"] == []


def test_why_implementation_stage_finds_code_cite(fixture_repo, view_path, registry_path):
    result = why.why("FX-0001", repo=str(fixture_repo.root), view_path=view_path, registry_path=registry_path)
    impl = result["stages"]["implementation"]
    assert impl["status"] == "PRESENT"
    assert any("fx_module" in h["evidence_occurrence"] for h in impl["hops"])


def test_why_current_status_stage_always_present(fixture_repo, view_path, registry_path):
    result = why.why("FX-0001", repo=str(fixture_repo.root), view_path=view_path, registry_path=registry_path)
    status = result["stages"]["current_status"]
    assert status["status"] == "PRESENT"
    assert status["hops"][0]["dst"] == "SUPERSEDED"


def test_why_missing_seed_reports_missing_everywhere_except_status(fixture_repo, view_path, registry_path):
    result = why.why("NOTHING-LIKE-THIS-9999", repo=str(fixture_repo.root), view_path=view_path,
                      registry_path=registry_path)
    for stage_name, stage in result["stages"].items():
        if stage_name == "current_status":
            assert stage["status"] == "PRESENT"  # classify() always returns a Classification, UNCLASSIFIED/UNKNOWN
        else:
            assert stage["status"].startswith("MISSING"), stage_name
