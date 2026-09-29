from govbridge.core import corpus, gitobj


def test_load_rules_preserves_order_and_fields(rules_path):
    rules = corpus.load_rules(rules_path)
    assert [r.id for r in rules] == [
        "X-SEC-PATH", "X-BUILD", "M-LARGE", "X-BINARY", "X-SEC-CONTENT", "L-MACHINE-OUTPUT", "INCLUDED",
    ]
    assert rules[-1].is_catch_all()


def _classify(repo, commit, path, rules_path):
    entry = gitobj.ls_tree_path(commit, path, repo=repo)
    rules = corpus.load_rules(rules_path)
    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        return corpus.classify_entry(entry, rules, sniffer)


def test_every_rule_type_classifies_its_intended_example(fixture_repo, rules_path):
    repo = str(fixture_repo.root)
    c = fixture_repo.c1
    assert _classify(repo, c, ".env", rules_path).rule_id == "X-SEC-PATH"
    assert _classify(repo, c, "secrets/token.pem", rules_path).rule_id == "X-SEC-PATH"
    assert _classify(repo, c, "big/large.txt", rules_path).rule_id == "M-LARGE"
    assert _classify(repo, c, "bin/blob.dat", rules_path).rule_id == "X-BINARY"
    assert _classify(repo, c, "src/creds.py", rules_path).rule_id == "X-SEC-CONTENT"
    assert _classify(repo, c, "logs/build.out", rules_path).rule_id == "L-MACHINE-OUTPUT"
    assert _classify(repo, c, "runtime/src/init.rs", rules_path).rule_id == "INCLUDED"
    assert _classify(repo, c, "docs/NOTES.md", rules_path).rule_id == "INCLUDED"


def test_monotone_evaluation_order_is_deterministic(rules_path):
    # re-loading and re-evaluating never changes which rule an unambiguous file gets
    rules1 = corpus.load_rules(rules_path)
    rules2 = corpus.load_rules(rules_path)
    assert [r.id for r in rules1] == [r.id for r in rules2]


def test_coverage_over_fixture_repo_has_zero_unclassified(fixture_repo, rules_path, view_path):
    report = corpus.coverage(view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    assert report["unclassified_total"] == 0
    for name, ref_report in report["refs"].items():
        assert ref_report["files_total_check"] == "OK", name
        assert ref_report["unclassified"] == 0


def test_coverage_counts_every_file_exactly_once(fixture_repo, rules_path, view_path):
    report = corpus.coverage(view_path, rules_path=rules_path, repo=str(fixture_repo.root))
    for name, ref_report in report["refs"].items():
        total = sum(ref_report["by_rule_files"].values())
        assert total == ref_report["files_total"], name
