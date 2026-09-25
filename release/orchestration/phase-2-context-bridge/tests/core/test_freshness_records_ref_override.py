"""``--records-ref`` (added by I1/BR-AR-0009 for the DAG's own I1 acceptance check: "index rebuild --from-clean
--records-ref <earlier bridge commit> then index update to the current view" -- proving incremental == full from
an EARLIER point in this bridge's own history, not only from an already-current one). New test file; existing
tests/core/test_freshness.py is unmodified."""
from govbridge.core import freshness, store


def test_from_clean_at_an_earlier_records_ref_then_update_equals_a_from_clean_build_at_the_current_tip(
        monkeypatch, tmp_path, fixture_repo, rules_path, view_path):
    root = str(fixture_repo.root)

    # from-clean AT THE CURRENT TIP (c3_moved, records' real tip after repobuilder.build()) -- the reference value.
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-ref"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home-ref"))
    r_ref = freshness.run(view_path=view_path, rules_path=rules_path, repo=root, from_clean=True)
    assert r_ref["trigger"] == "FULL"

    # from-clean AT AN EARLIER records commit (c1), in its OWN store ...
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-incr"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home-incr"))
    r_early = freshness.run(view_path=view_path, rules_path=rules_path, repo=root, from_clean=True,
                             records_ref=fixture_repo.c1)
    assert r_early["trigger"] == "FULL"
    assert r_early["manifest_sha256"] != r_ref["manifest_sha256"]  # genuinely a different (earlier) view

    # ... then `index update` (no override -- records resolves to its real, current tip) in the SAME store.
    r_incr = freshness.run(view_path=view_path, rules_path=rules_path, repo=root, from_clean=False)
    assert r_incr["trigger"] == "INCREMENTAL"
    assert r_incr["manifest_sha256"] == r_ref["manifest_sha256"]
