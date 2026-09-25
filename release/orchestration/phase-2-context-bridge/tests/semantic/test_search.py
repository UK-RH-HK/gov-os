from govbridge.semantic import search as searchmod


def test_search_results_carry_authority_class_lifecycle_version_status_and_delivery(
    built, fixture_repo, view_path
):
    _result, _conn, _pin_id = built
    out = searchmod.search("notes about the project", k=5, view_path=view_path, repo=str(fixture_repo.root))
    assert out["route"] == "semantic"
    assert out["results"], "expected at least one semantic hit on the fixture corpus"
    for item in out["results"]:
        assert item["delivery"] == "RETRIEVED"
        assert item["route"] == "semantic"
        assert item["authority_class"] == "UNCLASSIFIED"  # B5 not merged into this branch's base -- see docstring
        assert item["lifecycle"] == "UNKNOWN"
        assert "version_status" in item
        assert item["version_status"]
        assert "occurrence" in item and item["occurrence"] is not None
        assert item["rank"] >= 1
        assert isinstance(item["score"], float)


def test_search_results_are_ranked_best_first(built, fixture_repo, view_path):
    _result, _conn, _pin_id = built
    out = searchmod.search("notes about the project", k=5, view_path=view_path, repo=str(fixture_repo.root))
    scores = [item["score"] for item in out["results"]]
    assert scores == sorted(scores, reverse=True)


def test_a_custom_classify_hook_overrides_the_placeholder(built, fixture_repo, view_path):
    _result, _conn, _pin_id = built

    def fake_classify(_blob_id):
        return "EVIDENCE", "ACTIVE"

    out = searchmod.search("notes about the project", k=3, view_path=view_path, repo=str(fixture_repo.root),
                            classify=fake_classify)
    assert out["results"]
    for item in out["results"]:
        assert item["authority_class"] == "EVIDENCE"
        assert item["lifecycle"] == "ACTIVE"
