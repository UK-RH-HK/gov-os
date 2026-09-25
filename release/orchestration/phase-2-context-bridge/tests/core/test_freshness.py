import subprocess

from govbridge.core import freshness, store
import repobuilder


def test_first_run_is_full_and_second_is_noop(monkeypatch, tmp_path, fixture_repo, rules_path, view_path):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))

    r1 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert r1["trigger"] == "FULL"
    assert r1["blobs_processed"] > 0
    assert r1["occurrences_processed"] > 0
    assert r1["llm_invocations"] == 0
    assert r1["manifest_sha256"]

    r2 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert r2["trigger"] == "NOOP"
    assert r2["blobs_processed"] == 0
    assert r2["occurrences_processed"] == 0
    assert r2["chunks_processed"] == 0
    assert r2["llm_invocations"] == 0
    assert r2["wall_seconds"] < 2.0
    assert r2["manifest_sha256"] == r1["manifest_sha256"]


def test_from_clean_forces_full_even_when_nothing_changed(monkeypatch, tmp_path, fixture_repo, rules_path,
                                                            view_path):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    r2 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root), from_clean=True)
    assert r2["trigger"] == "FULL"


def test_incremental_when_a_named_ref_moves(monkeypatch, tmp_path, fixture_repo, rules_path, view_path):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    root = str(fixture_repo.root)

    r1 = freshness.run(view_path=view_path, rules_path=rules_path, repo=root)
    assert r1["trigger"] == "FULL"

    repobuilder.write(fixture_repo.root, "docs/NOTES.md", "# Notes\nversion 4 (new commit)\n")
    repobuilder._commit(fixture_repo.root, "c4: one more records change")

    r2 = freshness.run(view_path=view_path, rules_path=rules_path, repo=root)
    assert r2["trigger"] == "INCREMENTAL"
    assert "records" in r2["refs_changed"]
    assert r2["blobs_processed"] >= 1  # the new docs/NOTES.md blob, at minimum
    assert r2["manifest_sha256"] != r1["manifest_sha256"]

    r3 = freshness.run(view_path=view_path, rules_path=rules_path, repo=root)
    assert r3["trigger"] == "NOOP"


def test_full_trigger_when_a_config_file_changes(monkeypatch, tmp_path, fixture_repo, rules_path, view_path):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    r1 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert r1["trigger"] == "FULL"

    # a config change (corpus-rules.yaml) must invalidate the whole store, per ARCHITECTURE.md section 3
    mutated_rules = tmp_path / "mutated-corpus-rules.yaml"
    mutated_rules.write_text(open(rules_path).read() + "\n# a harmless comment that changes the file's sha256\n")
    r2 = freshness.run(view_path=view_path, rules_path=str(mutated_rules), repo=str(fixture_repo.root))
    assert r2["trigger"] == "FULL"


def test_two_govbridge_store_values_build_independent_stores(monkeypatch, tmp_path, fixture_repo, rules_path,
                                                                view_path):
    """BR-DAG-AMEND-1 point 3: two different GOVBRIDGE_STORE values build independent stores, and a freshness
    update in one never touches the other."""
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    store_a = tmp_path / "store-A"
    store_b = tmp_path / "store-B"

    monkeypatch.setenv("GOVBRIDGE_STORE", str(store_a))
    ra = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert ra["trigger"] == "FULL"

    monkeypatch.setenv("GOVBRIDGE_STORE", str(store_b))
    rb = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert rb["trigger"] == "FULL"  # store B has never been built; it does NOT inherit store A's manifest

    assert store_a.exists() and store_b.exists()
    assert (store_a / "store.db").exists() and (store_b / "store.db").exists()

    b_db_before = (store_b / "store.db").read_bytes()
    b_manifest_before = (store_b / "manifest.json").read_text()

    # advance the repo and rebuild ONLY store A
    repobuilder.write(fixture_repo.root, "docs/NOTES.md", "# Notes\nversion 4, store A only\n")
    repobuilder._commit(fixture_repo.root, "advance for store A")
    monkeypatch.setenv("GOVBRIDGE_STORE", str(store_a))
    ra2 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert ra2["trigger"] == "INCREMENTAL"
    assert ra2["manifest_sha256"] != ra["manifest_sha256"]

    # store B's files are byte-for-byte untouched by rebuilding store A
    assert (store_b / "store.db").read_bytes() == b_db_before
    assert (store_b / "manifest.json").read_text() == b_manifest_before

    # store B, queried next, correctly sees the SAME live repository change (freshness reflects the repo, not the
    # store) and rebuilds independently into its own directory -- store A is untouched by store B's rebuild
    a_db_after_a_rebuild = (store_a / "store.db").read_bytes()
    a_manifest_after_a_rebuild = (store_a / "manifest.json").read_text()
    monkeypatch.setenv("GOVBRIDGE_STORE", str(store_b))
    rb2 = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert rb2["trigger"] == "INCREMENTAL"
    assert rb2["manifest_sha256"] != rb["manifest_sha256"]
    assert (store_a / "store.db").read_bytes() == a_db_after_a_rebuild
    assert (store_a / "manifest.json").read_text() == a_manifest_after_a_rebuild
    # each store's manifest reflects the SAME underlying view commit, independently rebuilt
    assert rb2["manifest_sha256"] == ra2["manifest_sha256"]


def test_layer_builder_registration_is_extensible(monkeypatch, tmp_path, fixture_repo, rules_path, view_path):
    calls = []

    def fake_builder(conn, resolved, rules, repo, from_clean, changed_refs=None):
        calls.append((from_clean, tuple(changed_refs or [])))
        return {"blobs": 0, "occurrences": 0, "chunks": 0}

    freshness.register_layer_builder("fake_future_layer", fake_builder)
    try:
        monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
        monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
        r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root),
                           layer="fake_future_layer")
        assert r["layer"] == "fake_future_layer"
        assert calls  # the registered builder was actually invoked
    finally:
        freshness._LAYER_BUILDERS.pop("fake_future_layer", None)
