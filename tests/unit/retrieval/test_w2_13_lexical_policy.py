"""Builder tests for W2-13 S6: the keyword index honours the path map's ``lexical_policy`` (DEC-1066 (3)).

Regression evidence only (DEC-136). Every index is built in a temporary git repository with a planted path map; the
secrets filter is replaced by a recorder, so no test needs gitleaks, and no model or embedder is started.
"""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check.pathmap import check  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.config.loader import load_config  # noqa: E402
from gov.retrieval import lexical  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
PATH_MAP = "governance/project/path-map.yaml"


def _path_map(evaluation: str | None, report: str | None = None) -> str:
    """Four namespaces: the evaluation fixtures and lens B's report with the policies given (None: no field)."""
    def field(value):
        return "" if value is None else f"    lexical_policy: {value}\n"
    return ("namespaces:\n"
            "  evaluation:\n    paths: [\"fixtures/evaluation/**\"]\n" + field(evaluation) +
            "  report:\n    paths: [\"docs/assessment/*/B-memory-retrieval.md\"]\n" + field(report) +
            "  docs:\n    paths: [\"docs/*.md\", \"docs/assessment/*/A-*.md\"]\n    lexical_policy: indexed\n"
            "  rest:\n    paths: [\"*\", \"governance/**\", \"links/**\"]\n")


FILES = {
    ".gitignore": ".gov-runtime/\n",
    "fixtures/evaluation/visible/q01.yaml": "question: where is zanzibarword kept\n",
    "docs/assessment/2026-10/B-memory-retrieval.md": "# Lens B\n\nThe quokkaword answer.\n",
    "docs/assessment/2026-10/A-other.md": "# Lens A\n\nAn ordinary page.\n",
    "docs/guide.md": "# Guide\n\nThe walrusword guide.\n",
}


def _commit(root: Path, files: dict) -> None:
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "a change"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository whose path map keeps the evaluation fixtures and lens B's report out; what the filter was asked."""
    asked: list[list[str]] = []

    def indexable(root, paths):
        asked.append(sorted(paths))
        return list(paths)

    monkeypatch.setattr(lexical, "indexable", indexable)
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(tmp_path, {**FILES, PATH_MAP: _path_map("not indexed", "not indexed")})
    return tmp_path, asked


def _paths(root: Path) -> set[str]:
    return {record["path"] for record in lexical.chunks(root)}


def test_a_namespace_not_indexed_keeps_its_files_out_and_unasked(project):
    root, asked = project
    result = lexical.refresh(root)
    assert result["kept_out"] == {"evaluation": ["fixtures/evaluation/visible/q01.yaml"],
                                  "report": ["docs/assessment/2026-10/B-memory-retrieval.md"]}
    assert _paths(root) == {".gitignore", "docs/assessment/2026-10/A-other.md", "docs/guide.md", PATH_MAP}
    assert not set(result["kept_out"]["evaluation"] + result["kept_out"]["report"]) & set(asked[0]), \
        "a file kept out was given to the secrets filter"
    store = (root / ".gov-runtime/store.db").read_bytes()
    assert b"zanzibarword" not in store and b"quokkaword" not in store
    for word in ("zanzibarword", "quokkaword"):
        found = lexical.search(root, word, refresh=False)
        assert found["available"] and found["hits"] == [] and found["ranked"] == []
    assert lexical.search(root, "walrusword", refresh=False)["hits"][0]["path"] == "docs/guide.md"
    assert lexical.freshness(root) == {"status": "fresh", "stale": []}
    again = lexical.refresh(root)
    assert again["indexed"] == [] and again["kept_out"] == result["kept_out"], "the report lost the files kept out"


def test_absent_or_indexed_is_indexed_as_before(project):
    root, _ = project
    _commit(root, {PATH_MAP: _path_map(None, "indexed")})
    result = lexical.refresh(root)
    assert result["kept_out"] == {}
    assert {"fixtures/evaluation/visible/q01.yaml", "docs/assessment/2026-10/B-memory-retrieval.md"} <= _paths(root)


def test_a_change_of_policy_drops_or_restores_the_files(project):
    root, _ = project
    lexical.refresh(root)
    _commit(root, {PATH_MAP: _path_map("not indexed", None)})  # the report is indexed again
    result = lexical.refresh(root)
    assert "docs/assessment/2026-10/B-memory-retrieval.md" in result["indexed"]
    assert result["kept_out"] == {"evaluation": ["fixtures/evaluation/visible/q01.yaml"]}
    assert lexical.search(root, "quokkaword")["hits"][0]["path"] == "docs/assessment/2026-10/B-memory-retrieval.md"
    _commit(root, {PATH_MAP: _path_map("not indexed", "not indexed")})  # and kept out once more
    result = lexical.refresh(root)
    assert "docs/assessment/2026-10/B-memory-retrieval.md" not in _paths(root)
    assert lexical.search(root, "quokkaword")["ranked"] == []
    assert result["kept_out"]["report"] == ["docs/assessment/2026-10/B-memory-retrieval.md"]


def test_a_link_to_a_file_kept_out_is_kept_out(project):
    root, asked = project
    (root / "links").mkdir()
    os.symlink("../fixtures/evaluation/visible/q01.yaml", root / "links/q01.yaml")
    _commit(root, {})
    result = lexical.refresh(root)
    assert "links/q01.yaml" in result["kept_out"]["evaluation"]
    assert "links/q01.yaml" not in _paths(root) and "links/q01.yaml" not in asked[-1]


def test_an_invalid_policy_is_refused_and_search_does_not_raise(project):
    root, _ = project
    lexical.refresh(root)
    _commit(root, {PATH_MAP: _path_map("not-indexed")})
    with pytest.raises(GovError) as raised:
        load_config(root)
    assert raised.value.code == "CONFIG_INVALID" and "lexical_policy" in raised.value.message
    with pytest.raises(GovError):
        lexical.refresh(root)
    assert lexical.search(root, "walrusword") == lexical._unavailable("unreadable")


EVAL, REPORT = "fixtures/evaluation/visible/q01.yaml", "docs/assessment/2026-10/B-memory-retrieval.md"


def _rows(root: Path) -> dict:
    connection = sqlite3.connect(root / ".gov-runtime/store.db")
    try:
        return {rel: indexed for rel, indexed in connection.execute("SELECT path, indexed FROM lexical_file")}
    finally:
        connection.close()


def _judged_without_s6(root: Path, monkeypatch) -> None:
    """The store as code without S6 leaves it: every file of the fixture's tree, whose map already says ``not
    indexed``, judged with no policy, so the map's blob recorded is the current one (review S6-F1, probe 2)."""
    real = lexical.kept_out
    monkeypatch.setattr(lexical, "kept_out", lambda root, paths: {})
    lexical.refresh(root)
    monkeypatch.setattr(lexical, "kept_out", real)


def test_a_store_judged_without_s6_is_put_right_by_one_refresh(project, monkeypatch):
    """S6-F1: a stored ``(blob, 1)`` row with chunks under a ``not indexed`` namespace, the map's blob current."""
    root, asked = project
    _judged_without_s6(root, monkeypatch)
    assert _rows(root)[EVAL] == 1 and _rows(root)[REPORT] == 1 and REPORT in _paths(root)
    assert lexical.freshness(root)["status"] == "fresh", "the planted store is not the pre-S6 state"
    calls = len(asked)
    result = lexical.refresh(root)
    assert asked[calls:] == [], "a file kept out was given to the filter, or an agreeing file was judged again"
    assert result["indexed"] == []
    assert result["kept_out"] == {"evaluation": [EVAL], "report": [REPORT]}
    assert _rows(root)[EVAL] == _rows(root)[REPORT] == lexical.KEPT_OUT and REPORT not in _paths(root)
    assert lexical.search(root, "quokkaword")["ranked"] == []
    assert lexical.refresh(root)["kept_out"] == result["kept_out"] and len(asked) == calls, "it was judged again"


def test_a_stored_kept_out_the_map_now_indexes_is_indexed_again(project, monkeypatch):
    """The reverse: rows stored ``KEPT_OUT`` while the recorded map (current) no longer keeps them out."""
    root, _ = project
    lexical.refresh(root)  # the policy map: both kept out
    real = lexical.kept_out
    monkeypatch.setattr(lexical, "kept_out", lambda root, paths: {rel: "stale" for rel in paths
                                                                  if rel in (EVAL, REPORT)})
    _commit(root, {PATH_MAP: _path_map(None, "indexed")})
    lexical.refresh(root)  # judged against the new map, with stale verdicts
    assert _rows(root)[EVAL] == _rows(root)[REPORT] == lexical.KEPT_OUT
    monkeypatch.setattr(lexical, "kept_out", real)
    result = lexical.refresh(root)
    assert sorted(result["indexed"]) == sorted([EVAL, REPORT]) and result["kept_out"] == {}
    assert lexical.search(root, "quokkaword")["hits"][0]["path"] == REPORT


def test_a_file_kept_out_for_another_reason_is_not_reindexed_by_the_rule(project, monkeypatch):
    """A file the secrets filter refuses (a secret, a product memory class) and the map does not keep out agrees with
    the policy: it is not asked again and stays out; one the map also keeps out becomes ``KEPT_OUT``, never indexed."""
    root, asked = project
    refused = {"docs/guide.md", EVAL}
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: asked.append(sorted(paths)) or
                        [rel for rel in paths if rel not in refused])
    _judged_without_s6(root, monkeypatch)
    assert _rows(root)["docs/guide.md"] == 0 and _rows(root)[EVAL] == 0
    calls = len(asked)
    result = lexical.refresh(root)
    assert asked[calls:] == [], "a file the filter refused, or one kept out, was given to the filter again"
    assert _rows(root)["docs/guide.md"] == 0 and "docs/guide.md" not in _paths(root)
    assert _rows(root)[EVAL] == lexical.KEPT_OUT and result["kept_out"]["evaluation"] == [EVAL]
    assert result["indexed"] == []


def _rebuild(root: Path, monkeypatch) -> dict:
    """``gov rebuild --no-embeddings`` with the real lexical stage; stand-ins for the record store and the code index."""
    import argparse

    from gov.rebuild.command import add_arguments, run

    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.codeintel.index", lambda root: None)
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return run(root, parser.parse_args(["--no-embeddings"]), load_config(root))


def test_the_rebuild_names_each_file_kept_out(project, monkeypatch):
    root, _ = project
    lexical_store = _rebuild(root, monkeypatch)["stores"]["lexical"]
    assert lexical_store == {"status": "recreated",
                             "kept_out": {"evaluation": ["fixtures/evaluation/visible/q01.yaml"],
                                          "report": ["docs/assessment/2026-10/B-memory-retrieval.md"]}}
    assert _rebuild(root, monkeypatch)["stores"]["lexical"] == lexical_store, "a fresh index named nothing"


def test_the_rebuild_report_is_unchanged_where_nothing_is_kept_out(project, monkeypatch):
    root, _ = project
    _commit(root, {PATH_MAP: _path_map(None, "indexed")})
    assert _rebuild(root, monkeypatch)["stores"]["lexical"] == {"status": "recreated"}


NAMESPACE = ("    memory_class: governance\n    sensitivity: internal\n    permitted_roles: [engineer]\n"
             "    retention: r\n    export_policy: e\n    embedding_policy: n\n    provenance: p\n    deletion_rebuild: d\n")


def _full(policy: str | None) -> str:
    """A W1-08 path map (every top-level key) with one namespace stating ``policy``."""
    systems = "".join(f"  {name}:\n    status: absent\n    reason: r\n" for name in __import__(
        "gov.config.path_map_schema", fromlist=["SYSTEM_KEYS"]).SYSTEM_KEYS)
    policies = ("  security: hard-block\n  authority: hard-block\n  test: hard-block\n  change: hard-block\n"
                "  human_gate: hard-block\n  tool: hard-block\n  memory: warning\n  context: warning\n"
                "  checkpoint: warning\n  model_routing: warning\n  budget: warning\n  learning: warning\n"
                "  archive: warning\n")
    return ("state_class: AUTHORITATIVE\nnamespaces:\n  all:\n    paths: [\"**\"]\n" + NAMESPACE
            + ("" if policy is None else f"    lexical_policy: {policy}\n")
            + "capabilities:\n  code_intelligence:\n    enabled: false\n  research_corpus:\n    enabled: false\n"
            + "policies:\n" + policies + "systems:\n" + systems)


@pytest.mark.parametrize("policy", [None, "indexed", "not indexed"])
def test_the_validators_accept_the_two_values_and_absence(tmp_path, policy):
    root = tmp_path / "r"
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True, env=_ENV)
    _commit(root, {PATH_MAP: _full(policy), "README.md": "x\n"})
    assert load_config(root)["path-map.yaml"]["namespaces"]["all"].get("lexical_policy") == policy
    assert check(root) == []


@pytest.mark.parametrize("policy", ["not-indexed", "embedded", "''", "[indexed]", "true"])
def test_the_validators_refuse_any_other_value(tmp_path, policy):
    root = tmp_path / "r"
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True, env=_ENV)
    _commit(root, {PATH_MAP: _full(policy), "README.md": "x\n"})
    with pytest.raises(GovError) as raised:
        load_config(root)
    assert raised.value.code == "CONFIG_INVALID" and "namespaces.all.lexical_policy" in raised.value.message
    findings = check(root)
    assert [finding["code"] for finding in findings] == ["PATH_MAP_INVALID"]
    assert "lexical_policy" in findings[0]["message"]


@pytest.mark.parametrize("policy, embedding, refused", [
    ("not indexed", "embedded", True),
    ("not indexed", "not embedded", False),
    ("indexed", "embedded", False),
    (None, "embedded", False),
])
def test_not_indexed_cannot_be_embedded(tmp_path, policy, embedding, refused):
    """The CTO's P2: the vectors are built from the keyword index's chunks, so the combination is refused, named."""
    root = tmp_path / "r"
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True, env=_ENV)
    _commit(root, {PATH_MAP: _full(policy).replace("embedding_policy: n\n", f"embedding_policy: {embedding}\n"),
                   "README.md": "x\n"})
    if not refused:
        assert load_config(root)["path-map.yaml"]["namespaces"]["all"]["embedding_policy"] == embedding
        assert check(root) == []
        return
    with pytest.raises(GovError) as raised:
        load_config(root)
    assert raised.value.code == "CONFIG_INVALID"
    assert raised.value.details["key"] == "namespaces.all.lexical_policy"
    assert "not indexed cannot be embedded" in raised.value.message
    findings = check(root)
    assert [finding["code"] for finding in findings] == ["PATH_MAP_INVALID"]
    assert "'all'" in findings[0]["message"] and "not indexed cannot be embedded" in findings[0]["message"]


def test_the_keyword_index_refuses_the_combination_too(project):
    """The minimal form of the path map is refused as the W1-08 form is; the index is not built on it."""
    root, _ = project
    _commit(root, {PATH_MAP: _path_map("not indexed").replace(
        "lexical_policy: not indexed\n", "lexical_policy: not indexed\n    embedding_policy: embedded\n", 1)})
    with pytest.raises(GovError) as raised:
        lexical.refresh(root)
    assert raised.value.code == "CONFIG_INVALID" and "namespaces.evaluation.lexical_policy" in raised.value.message
    assert lexical.search(root, "walrusword") == lexical._unavailable("unreadable")
