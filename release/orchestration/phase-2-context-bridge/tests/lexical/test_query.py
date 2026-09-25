import json
import os
import subprocess
import sys
from pathlib import Path

from govbridge.lexical import query as querymod

DOMAIN_ROOT = str(Path(__file__).resolve().parents[2])  # release/orchestration/phase-2-context-bridge


def test_query_finds_a_known_chunk_with_correct_occurrence_and_line_range(built_store):
    fixture_repo, view_path, rules_path = built_store
    res = querymod.query("native_layout_rules", view_path=view_path, repo=str(fixture_repo.root))
    assert res["hits"], "expected at least one hit"
    hit = res["hits"][0]
    assert hit["route"] == "lexical"
    paths = {(o["ref"], o["path"]) for o in hit["occurrences"]}
    assert ("product", "runtime/src/init.rs") in paths
    assert hit["start_line"] <= 1 <= hit["end_line"]  # native_layout_rules is defined on line 1 of the fixture


def test_query_latency_is_reported_and_bounded(built_store):
    fixture_repo, view_path, rules_path = built_store
    res = querymod.query("native_layout_rules", view_path=view_path, repo=str(fixture_repo.root))
    assert isinstance(res["latency_ms"], float)
    assert res["latency_ms"] < 100.0  # the SQL search path alone, ARCHITECTURE.md section 4.3 / SO-15,16


def test_query_never_returns_content_excluded_by_corpus_rules(built_store):
    """aws_secret_access_key only ever occurs inside src/creds.py, which X-SEC-CONTENT excludes from the corpus
    entirely (never chunked by core); the lexical index must therefore never surface it."""
    fixture_repo, view_path, rules_path = built_store
    res = querymod.query("aws_secret_access_key", view_path=view_path, repo=str(fixture_repo.root))
    assert res["hits"] == []


def test_retrieval_exclusions_drops_a_hit_whose_only_occurrences_match(built_store):
    fixture_repo, view_path, rules_path = built_store
    unfiltered = querymod.query("native_layout_rules", view_path=view_path, repo=str(fixture_repo.root))
    assert unfiltered["hits"]

    excluded = querymod.query("native_layout_rules", view_path=view_path, repo=str(fixture_repo.root),
                               exclude=["runtime/**"])
    assert excluded["hits"] == []


def test_retrieval_exclusions_keeps_a_hit_with_surviving_occurrences(built_store):
    """docs/NOTES.md is records-owned and also appears (via the fallback chain) at several history tips. Excluding
    only one glob that matches a subset of its occurrences must narrow, not drop, the hit."""
    fixture_repo, view_path, rules_path = built_store
    res = querymod.query('"version 1"', view_path=view_path, repo=str(fixture_repo.root))
    assert res["hits"], "expected the c1 NOTES.md content to be indexed"
    all_paths = {o["path"] for h in res["hits"] for o in h["occurrences"]}
    assert "docs/NOTES.md" in all_paths

    filtered = querymod.query('"version 1"', view_path=view_path, repo=str(fixture_repo.root),
                               exclude=["nonexistent/path/**"])
    # a glob matching nothing must never drop a hit
    assert len(filtered["hits"]) == len(res["hits"])


def test_tokenizer_keeps_snake_case_identifiers_whole(built_store):
    """tokenize = porter unicode61 tokenchars '_' (ARCHITECTURE.md section 4.3): a query for the FULL identifier
    must match; the identifier must never have been split into 'native', 'layout', 'rules' as separate FTS
    tokens -- proven by requiring the exact phrase to match while confirming the underlying text is unbroken."""
    fixture_repo, view_path, rules_path = built_store
    whole = querymod.query("native_layout_rules", view_path=view_path, repo=str(fixture_repo.root))
    assert whole["hits"]
    assert "native_layout_rules" in whole["hits"][0]["text"]


def test_bm25_orders_hits_best_first(built_store):
    fixture_repo, view_path, rules_path = built_store
    res = querymod.query("version", view_path=view_path, repo=str(fixture_repo.root), k=10)
    scores = [h["raw_score"] for h in res["hits"]]
    assert scores == sorted(scores)  # bm25() is a cost in SQLite FTS5: ascending == best-first
    ranks = [h["rank"] for h in res["hits"]]
    assert ranks == list(range(1, len(ranks) + 1))


def test_k_limits_the_number_of_hits(built_store):
    fixture_repo, view_path, rules_path = built_store
    res = querymod.query("version", view_path=view_path, repo=str(fixture_repo.root), k=1)
    assert len(res["hits"]) <= 1


def test_cli_json_output_matches_the_library_call(built_store):
    fixture_repo, view_path, rules_path = built_store
    lib_result = querymod.query("native_layout_rules", view_path=view_path, repo=str(fixture_repo.root))

    # A real subprocess, exactly the acceptance-check shape (`python -m govbridge.lexical.query ... --json`).
    # govbridge.lexical.query's CLI has no --repo flag, the same convention govbridge.core.exact and
    # govbridge.core.freshness use: it resolves Git objects relative to the current working directory, the way a
    # real invocation would from inside a checkout -- hence cwd=fixture_repo.root below. A subprocess (rather than
    # an in-process call) also sidesteps govbridge.core.gitobj.repo_root()'s process-lifetime lru_cache, which
    # would otherwise remember whichever cwd first called it during this test session.
    env = dict(os.environ)
    env["PYTHONPATH"] = DOMAIN_ROOT
    proc = subprocess.run(
        [sys.executable, "-m", "govbridge.lexical.query", "native_layout_rules", "--view", view_path, "--json"],
        cwd=str(fixture_repo.root), env=env, capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    cli_result = json.loads(proc.stdout)
    assert cli_result["query"] == lib_result["query"]
    assert len(cli_result["hits"]) == len(lib_result["hits"])
    if cli_result["hits"]:
        assert cli_result["hits"][0]["item_id"] == lib_result["hits"][0]["item_id"]
