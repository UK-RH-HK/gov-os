"""BR-AR-0014 follow-ups 1 and 2 (orchestrator reopen after the first COMPLETED return):

1. Corpus-rule exclusion. The orchestrator measured 11 real ``.rs`` blobs at the eager refs classified
   ``X-SEC-CONTENT``/EXCLUDE by ``config/corpus-rules.yaml``, all still reaching ``code_symbol``/``code_call_site``/
   ``code_literal`` -- a SECURITY_POLICY content-exclusion bypass. These tests prove, on hermetic fixture repos with
   SYNTHETIC rules (never coupled to the real corpus-rules.yaml content, so they stay meaningful whatever that file
   says tomorrow): a path-glob exclusion, a content-regex exclusion, and a non-EXCLUDE effect (LEXICAL_ONLY) are all
   treated generically as "not code-indexable" by both the eager builder and the lazy ``ensure_indexed`` path, that
   an excluded blob never reaches the parse tables, and that it is recorded with its rule id.

2. The ``code_blob.eager`` migration: a store built before that column existed (the demonstration store,
   store-BR-AR-0010, which this run must never touch) gains it in place, idempotently, and the store keeps working.

See tests/code/test_eager_build.py for BR-HO-0014's original five acceptance checks (unaffected by either
follow-up: those fixtures' files are ordinary INCLUDE-verdict Rust with no secret-shaped content).
"""
from __future__ import annotations

import sqlite3

from govbridge.code import build as codebuild
from govbridge.code import store as codestore
from govbridge.code import symbols as codesymbols
from govbridge.core import corpus, store as corestore
from govbridge.core.view import Partition, ResolvedRef, ResolvedView, RefSpec, ViewConfig

import _repobuilder as rb

CATCH_ALL = corpus.Rule(id="INCLUDED", effect="INCLUDE", match={})


def _glob_rule(rule_id: str, effect: str, globs: list[str]) -> corpus.Rule:
    return corpus.Rule(id=rule_id, effect=effect, match={"globs": globs})


def _content_rule(rule_id: str, effect: str, patterns: dict) -> corpus.Rule:
    return corpus.Rule(id=rule_id, effect=effect, match={"content_regex": patterns})


def _view(refs: list[RefSpec]) -> ViewConfig:
    return ViewConfig(view_id="test-view", refs=refs,
                       partitions=[Partition(name="all", owner="records", fallback=[], paths=["**"])], raw={})


def _eager_view_for(root, commit) -> ResolvedView:
    view = _view([RefSpec(name="records", ref="refs/heads/main", ref_glob=None, follow="tip", pinned_commit=None,
                           role="primary", layers=None)])
    return ResolvedView(view_id=view.view_id, config=view,
                         named={"records": ResolvedRef(name="records", commit=commit, status="OK")},
                         history=[], repo=str(root))


def _no_rows_for(conn, blob_id: str) -> None:
    for table in ("code_symbol", "code_call_site", "code_literal"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE blob_id=?", (blob_id,)).fetchone()[0]
        assert n == 0, f"{table} has {n} row(s) for an excluded blob"


# ---------------------------------------------------------------------------------------------------------------
# Follow-up 1: exclusion, eager path
# ---------------------------------------------------------------------------------------------------------------

def test_eager_builder_excludes_a_blob_by_path_glob(repo):
    rb.write(repo, "runtime/src/ok.rs", "pub fn kept() {}\n")
    rb.write(repo, "runtime/src/secrets.rs", "pub fn leaked() {}\n")
    c1 = rb.commit(repo, "one excluded by path glob")
    rules = [_glob_rule("X-SECRET-PATH", "EXCLUDE", ["**/secrets.rs"]), CATCH_ALL]

    conn = corestore.open_db()
    stats = codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=rules, repo=str(repo),
                                          from_clean=True)
    assert stats["excluded_blobs"] == 1
    assert stats["eager_blobs"] == 1  # only ok.rs

    excluded_ids = codestore.eager_excluded_blob_ids(conn)
    assert len(excluded_ids) == 1
    row = conn.execute("SELECT path, rule_id, effect FROM code_excluded_blob").fetchone()
    assert row == ("runtime/src/secrets.rs", "X-SECRET-PATH", "EXCLUDE")
    _no_rows_for(conn, excluded_ids[0])

    digest = codebuild.code_layer_digest(conn)
    assert digest.extra["blobs_parsed"] == 1
    assert digest.extra["excluded_blobs"] == 1


def test_eager_builder_excludes_a_blob_by_content_regex_not_path(repo):
    """Generic per govbridge.core.corpus.classify_entry: X-SEC-CONTENT-shaped rules match CONTENT, not a path --
    the file name here gives no hint at all."""
    rb.write(repo, "runtime/src/normal.rs", "pub fn normal() {}\n")
    rb.write(repo, "runtime/src/innocuous_name.rs",
             "const K: &str = \"aws_secret_access_key = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'\";\n")
    c1 = rb.commit(repo, "content-based exclusion")
    rules = [_content_rule("X-SEC-CONTENT", "EXCLUDE",
                            {"aws-secret-key": r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}"}),
             CATCH_ALL]

    conn = corestore.open_db()
    codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=rules, repo=str(repo), from_clean=True)
    row = conn.execute("SELECT path, rule_id FROM code_excluded_blob").fetchone()
    assert row == ("runtime/src/innocuous_name.rs", "X-SEC-CONTENT")
    excluded_id = codestore.eager_excluded_blob_ids(conn)[0]
    _no_rows_for(conn, excluded_id)


def test_any_non_include_effect_is_not_code_indexable_generically(repo):
    """BR-HO-0014 follow-up 1's own instruction: "LEXICAL_ONLY does not apply to .rs files, but handle it
    generically: treat any effect other than INCLUDE as not code-indexable, and say so." Proven with a rule whose
    effect is neither EXCLUDE nor a real corpus-rules.yaml value for .rs -- the code route must not special-case
    the string "EXCLUDE"."""
    rb.write(repo, "runtime/src/kept.rs", "pub fn kept() {}\n")
    rb.write(repo, "runtime/src/logs_like.rs", "pub fn also_kept_syntax() {}\n")
    c1 = rb.commit(repo, "a LEXICAL_ONLY verdict")
    rules = [_glob_rule("X-CUSTOM-LEXICAL-ONLY", "LEXICAL_ONLY", ["**/logs_like.rs"]), CATCH_ALL]

    conn = corestore.open_db()
    stats = codebuild.code_layer_builder(conn, _eager_view_for(repo, c1), rules=rules, repo=str(repo),
                                          from_clean=True)
    assert stats["excluded_blobs"] == 1
    assert stats["eager_blobs"] == 1
    row = conn.execute("SELECT path, rule_id, effect FROM code_excluded_blob").fetchone()
    assert row == ("runtime/src/logs_like.rs", "X-CUSTOM-LEXICAL-ONLY", "LEXICAL_ONLY")


# ---------------------------------------------------------------------------------------------------------------
# Follow-up 1: exclusion, lazy path (acceptance check 7)
# ---------------------------------------------------------------------------------------------------------------

def test_lazy_ensure_indexed_never_parses_an_excluded_blob(repo, monkeypatch):
    rb.write(repo, "runtime/src/kept.rs", "pub fn kept() {}\n")
    rb.write(repo, "runtime/src/secret.rs", "pub fn hidden() {}\n")
    c1 = rb.commit(repo, "lazy path, one excluded")
    rules = [_glob_rule("X-SECRET-PATH", "EXCLUDE", ["**/secret.rs"]), CATCH_ALL]

    from govbridge.code.adapters import rust_treesitter as rt
    parsed_paths = []
    original = rt.parse_module

    def recording(data, path):
        parsed_paths.append(path)
        return original(data, path)

    monkeypatch.setattr(rt, "parse_module", recording)

    conn = codesymbols._open_conn()
    entries = codesymbols.ensure_indexed(conn, c1, repo=str(repo), rules=rules)
    assert {p for p, _ in entries} == {"runtime/src/kept.rs", "runtime/src/secret.rs"}  # contract: BOTH still listed
    assert parsed_paths == ["runtime/src/kept.rs"]  # the excluded one was NEVER handed to the parser

    excluded_id = dict((p, b) for p, b in entries)["runtime/src/secret.rs"]
    assert codestore.is_excluded(conn, excluded_id)
    _no_rows_for(conn, excluded_id)


def test_callers_at_a_commit_discloses_the_exclusion_via_stats(repo, monkeypatch):
    """The "explicit, disclosed exclusion rather than silence" requirement: stats() names the excluded path and
    its rule id."""
    rb.write(repo, "runtime/src/caller.rs", "fn f() {\n    g();\n}\nfn g() {}\n")
    rb.write(repo, "runtime/src/secret.rs", "fn also_g() {}\n")
    c1 = rb.commit(repo, "disclosure via stats")
    rules = [_glob_rule("X-SECRET-PATH", "EXCLUDE", ["**/secret.rs"]), CATCH_ALL]

    conn = codesymbols._open_conn()
    codesymbols.ensure_indexed(conn, c1, repo=str(repo), rules=rules)
    # stats() itself resolves its own rules by default (real corpus-rules.yaml); call ensure_indexed directly
    # above with the SYNTHETIC rules first so the blob is already cached-excluded by the time stats() runs (it
    # will see is_excluded() True and skip reclassifying under the real rules, which would not exclude it).
    result = codesymbols.stats(c1, repo=str(repo))
    assert result["rs_files"] == 2
    excluded_paths = {e["path"]: e["rule_id"] for e in result["files_excluded"]}
    assert excluded_paths.get("runtime/src/secret.rs") == "X-SECRET-PATH"
    assert "runtime/src/caller.rs" not in excluded_paths


# ---------------------------------------------------------------------------------------------------------------
# Follow-up 2: code_blob.eager migration
# ---------------------------------------------------------------------------------------------------------------

_OLD_CODE_BLOB_DDL = """
CREATE TABLE code_blob (
    blob_id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    language TEXT NOT NULL,
    adapter_id TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    grammar_version TEXT NOT NULL,
    ok_parse INTEGER NOT NULL,
    error_count INTEGER NOT NULL
);
"""  # the pre-BR-AR-0014 schema, byte-for-byte (no `eager` column) -- store-BR-AR-0010's own shape.


def _old_style_store(tmp_path) -> sqlite3.Connection:
    conn = corestore.open_db(root=tmp_path / "store")  # real core tables (occurrence/blob/chunk/store_meta)
    conn.executescript(_OLD_CODE_BLOB_DDL)  # ...but code_blob predates the `eager` column
    conn.execute(
        "INSERT INTO code_blob(blob_id,path,language,adapter_id,adapter_version,grammar_version,ok_parse,"
        "error_count) VALUES ('b1','some/path.rs','rust','rust-treesitter','1.0.1','tree-sitter-rust/0.24.0',1,0)"
    )
    conn.commit()
    return conn


def test_migration_adds_eager_column_to_an_old_style_store(tmp_path):
    conn = _old_style_store(tmp_path)
    cols_before = {r[1] for r in conn.execute("PRAGMA table_info(code_blob)").fetchall()}
    assert "eager" not in cols_before

    codestore.ensure_schema(conn)  # the migration under test

    cols_after = {r[1] for r in conn.execute("PRAGMA table_info(code_blob)").fetchall()}
    assert "eager" in cols_after
    row = conn.execute("SELECT blob_id, eager FROM code_blob WHERE blob_id='b1'").fetchone()
    assert row == ("b1", 0)  # the pre-existing row survives, `eager` at its column default

    # the migrated store is actually usable: set_eager_blobs/eager_blob_ids work against it
    codestore.set_eager_blobs(conn, {"b1"})
    assert codestore.eager_blob_ids(conn) == ["b1"]


def test_migration_is_a_noop_the_second_time(tmp_path):
    conn = _old_style_store(tmp_path)
    codestore.ensure_schema(conn)
    codestore.set_eager_blobs(conn, {"b1"})
    before = conn.execute("SELECT blob_id, eager FROM code_blob ORDER BY blob_id").fetchall()

    codestore.ensure_schema(conn)  # running it again must not error, and must not reset anything
    codestore.ensure_schema(conn)  # ...nor the third time
    after = conn.execute("SELECT blob_id, eager FROM code_blob ORDER BY blob_id").fetchall()
    assert before == after


def test_migrated_store_builds_correctly_end_to_end(tmp_path, repo):
    """A fixture store with the old code_blob DDL gains `eager` and builds correctly (BR-AR-0014 follow-up 2,
    acceptance check 8): after migrating, a real eager build on top of the pre-existing row reaches the same
    digest a from-clean build in a brand-new store would."""
    old = _old_style_store(tmp_path)
    codestore.ensure_schema(old)  # migrate

    rb.write(repo, "runtime/src/a.rs", "pub fn a() {}\n")
    c1 = rb.commit(repo, "one real commit")
    codebuild.code_layer_builder(old, _eager_view_for(repo, c1), rules=[CATCH_ALL], repo=str(repo), from_clean=True)
    digest_migrated = codebuild.code_layer_digest(old)
    assert digest_migrated.rows > 0
    # the pre-existing dummy row ('b1') is untouched by the real build (different blob id, never reachable at c1)
    assert conn_has_row(old, "b1")

    fresh = corestore.open_db(root=tmp_path / "store2")
    codestore.ensure_schema(fresh)
    codebuild.code_layer_builder(fresh, _eager_view_for(repo, c1), rules=[CATCH_ALL], repo=str(repo),
                                  from_clean=True)
    digest_fresh = codebuild.code_layer_digest(fresh)
    assert digest_migrated.digest == digest_fresh.digest
    assert digest_migrated.rows == digest_fresh.rows


def conn_has_row(conn, blob_id: str) -> bool:
    return conn.execute("SELECT 1 FROM code_blob WHERE blob_id=?", (blob_id,)).fetchone() is not None
