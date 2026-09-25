import pytest

from govbridge.core import exact


def test_parse_ref_path_spec_with_and_without_line_range():
    assert exact.parse_ref_path_spec("HEAD:a/b.rs") == ("HEAD", "a/b.rs", None, None)
    assert exact.parse_ref_path_spec("HEAD:a/b.rs:12") == ("HEAD", "a/b.rs", 12, 12)
    assert exact.parse_ref_path_spec("HEAD:a/b.rs:12-20") == ("HEAD", "a/b.rs", 12, 20)
    assert exact.parse_ref_path_spec("3c880d8:release/x/y.yaml") == ("3c880d8", "release/x/y.yaml", None, None)
    with pytest.raises(ValueError):
        exact.parse_ref_path_spec("no-colon-here")


def test_show_returns_canonical_for_the_owning_commit(fixture_repo, view_path, rules_path):
    repo = str(fixture_repo.root)
    r = exact.show(f"{fixture_repo.product_pin}:runtime/src/init.rs:1", view_path=view_path,
                    rules_path=rules_path, repo=repo)
    assert r["version_status"] == "CANONICAL"
    assert r["canonical_ref"] == "product"
    assert "native_layout_rules" in r["text"]
    assert r["line_start"] == 1 and r["line_end"] == 1


def test_show_returns_historical_version_for_a_records_owned_path_at_an_old_commit(fixture_repo, view_path,
                                                                                      rules_path):
    repo = str(fixture_repo.root)
    r = exact.show(f"{fixture_repo.c1}:docs/NOTES.md", view_path=view_path, rules_path=rules_path, repo=repo)
    assert r["version_status"] == "HISTORICAL_VERSION"
    assert r["canonical_ref"] == "records"
    assert "version 1" in r["text"]


def test_show_excludes_content_for_a_secret_path(fixture_repo, view_path, rules_path):
    repo = str(fixture_repo.root)
    r = exact.show(f"{fixture_repo.c1}:secrets/token.pem", view_path=view_path, rules_path=rules_path, repo=repo)
    assert r["excluded"] is True
    assert r["corpus_rule"] == "X-SEC-PATH"
    assert "text" not in r


def test_show_reports_path_not_found(fixture_repo, view_path, rules_path):
    repo = str(fixture_repo.root)
    r = exact.show(f"{fixture_repo.c1}:does/not/exist.txt", view_path=view_path, rules_path=rules_path, repo=repo)
    assert r["error"] == "PATH_NOT_FOUND"


def test_grep_finds_literal_and_filters_excluded_paths(fixture_repo, view_path, rules_path):
    repo = str(fixture_repo.root)
    r = exact.grep("native_layout_rules", ref="records", view_path=view_path, rules_path=rules_path, repo=repo)
    assert any(h["path"] == "runtime/src/init.rs" for h in r["hits"])

    # a literal that only occurs inside an excluded (secret-content) file must not surface its text
    r2 = exact.grep("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", ref="records", view_path=view_path,
                     rules_path=rules_path, repo=repo)
    assert r2["hits"] == []
    assert r2["excluded_skipped"] >= 1


def test_path_resolve_unique_and_ambiguous(fixture_repo, view_path):
    repo = str(fixture_repo.root)
    r = exact.path_resolve("init.rs", ref="records", view_path=view_path, repo=repo)
    assert r["ambiguous"] is False
    assert r["resolved"] == "runtime/src/init.rs"

    r2 = exact.path_resolve("nonexistent-suffix.zzz", ref="records", view_path=view_path, repo=repo)
    assert r2["ambiguous"] is True
    assert r2["candidates"] == []


def test_id_lookup_reports_mentions_and_no_definitions(fixture_repo, view_path, rules_path):
    repo = str(fixture_repo.root)
    r = exact.id_lookup("native_layout_rules", ref="records", view_path=view_path, repo=repo)
    assert r["definition_sites"] == []
    assert any(h["path"] == "runtime/src/init.rs" for h in r["mention_sites"])
    assert "id-grammar" in r["note"]
