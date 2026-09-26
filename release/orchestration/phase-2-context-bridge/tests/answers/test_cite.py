"""``govbridge.answers.cite`` (REPAIR_DAG.yaml node R1-RA). Hermetic: every test builds its OWN synthetic fixture
repo (``tests/fixtures/answers/answers_repobuilder.py``) and its own isolated ``GOVBRIDGE_STORE``/``GOV_BRIDGE_HOME``
(``monkeypatch.setenv`` -- R1-T1's own hermeticity rule), and passes ``view_path``/``repo`` explicitly to every call
so nothing here ever reads the real domain's own canonical view or the shared store.

Covers every REAL INPUT SHAPE this node's brief names: a bare Rust fn, a mod-nested Rust fn needing trailing-
segment resolution (RESOLVED and AMBIGUOUS), a Python test def (RESOLVED and AMBIGUOUS), an id-grammar id defined
in YAML block style, in YAML flow style, and in a Markdown heading, and a document section anchor (RESOLVED,
AMBIGUOUS and NOT_FOUND).
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest

FIXTURES_ANSWERS = Path(__file__).resolve().parents[1] / "fixtures" / "answers"
if str(FIXTURES_ANSWERS) not in sys.path:
    sys.path.insert(0, str(FIXTURES_ANSWERS))
import answers_repobuilder as repobuilder  # noqa: E402

from govbridge.answers import cite as citemod  # noqa: E402
from govbridge.core import freshness as freshnessmod  # noqa: E402
from govbridge.core import store as storemod  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-test-cite"))
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)


@pytest.fixture()
def built(tmp_path):
    repo = repobuilder.build(tmp_path)
    r = freshnessmod.run(view_path=repo.view_path, rules_path=repo.rules_path, repo=str(repo.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return repo


# ---------------------------------------------------------------------------------------------------------------
# Rust: bare fn (RESOLVED), mod-nested fn needing trailing-segment resolution (RESOLVED unique / AMBIGUOUS shared)
# ---------------------------------------------------------------------------------------------------------------

def test_rust_bare_fn_resolves(built):
    res = citemod.cite_identifier("ra_unique_fn", view_path=built.view_path, repo=str(built.root))
    assert res["kind"] == citemod.KIND_CODE
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["label"] == citemod.LABEL_RUST_EXACT
    assert res["citation"]["path"] == repobuilder.RUST_PATH
    assert res["citation"]["symbol"] == "ra_unique_fn"
    assert res["citation"]["lines"][0] <= res["citation"]["lines"][1]


def test_rust_mod_qualified_trailing_segment_unique(built):
    # `ra_unique_fn` is never inside a `mod` block, so a synthetic "some_mod::ra_unique_fn" query proves the
    # TRAILING-SEGMENT fallback specifically (the direct qualified-name attempt finds nothing; only the trailing
    # segment does), separately from the plain bare-name case above.
    res = citemod.cite_identifier("some_mod::ra_unique_fn", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["label"] == citemod.LABEL_RUST_TRAILING
    assert res["citation"]["path"] == repobuilder.RUST_PATH
    assert res["citation"]["symbol"] == "ra_unique_fn"


def test_rust_mod_qualified_trailing_segment_ambiguous(built):
    # ra_shared_fn is defined in BOTH ra_mod_one and ra_mod_two; the code layer stores neither's module path, so
    # EITHER "ra_mod_one::ra_shared_fn" or "ra_mod_two::ra_shared_fn" must resolve (by trailing segment) to the
    # SAME two candidates -- genuinely AMBIGUOUS, never a silent "pick one".
    for query in ("ra_mod_one::ra_shared_fn", "ra_mod_two::ra_shared_fn"):
        res = citemod.cite_identifier(query, view_path=built.view_path, repo=str(built.root))
        assert res["status"] == citemod.STATUS_AMBIGUOUS, query
        assert res["label"] == citemod.LABEL_RUST_TRAILING
        assert len(res["candidates"]) == 2
        assert {c["symbol"] for c in res["candidates"]} == {"ra_shared_fn"}
        assert {tuple(c["lines"]) for c in res["candidates"]} != {()}  # both candidates carry real line spans


def test_rust_bare_shared_name_is_also_ambiguous(built):
    res = citemod.cite_identifier("ra_shared_fn", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_AMBIGUOUS
    assert len(res["candidates"]) == 2


def test_unresolvable_identifier_is_not_found(built):
    res = citemod.cite_identifier("ra_totally_unknown_fn", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_NOT_FOUND
    assert res["candidates"] == []


# ---------------------------------------------------------------------------------------------------------------
# Python test names: the code layer indexes .rs only -- resolved through the exact route, a distinct label.
# ---------------------------------------------------------------------------------------------------------------

def test_python_def_resolves_via_exact_route(built):
    res = citemod.cite_identifier("test_ra_python_unique", view_path=built.view_path, repo=str(built.root))
    assert res["kind"] == citemod.KIND_CODE
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["label"] == citemod.LABEL_PYTHON
    assert res["citation"]["path"] == repobuilder.PY_UNIQUE_PATH
    assert res["citation"]["symbol"] == "test_ra_python_unique"
    assert res["citation"]["lines"][0] == res["citation"]["lines"][1] == 1


def test_python_def_ambiguous_across_two_files(built):
    res = citemod.cite_identifier("test_ra_python_dup", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_AMBIGUOUS
    assert res["label"] == citemod.LABEL_PYTHON
    paths = {c["path"] for c in res["candidates"]}
    assert paths == {repobuilder.PY_DUP_PATH_1, repobuilder.PY_DUP_PATH_2}


def test_python_def_label_is_distinct_from_rust_labels(built):
    py = citemod.cite_identifier("test_ra_python_unique", view_path=built.view_path, repo=str(built.root))
    rust = citemod.cite_identifier("ra_unique_fn", view_path=built.view_path, repo=str(built.root))
    assert py["label"] != rust["label"]
    assert {citemod.LABEL_RUST_EXACT, citemod.LABEL_RUST_TRAILING}.isdisjoint({py["label"]})


# ---------------------------------------------------------------------------------------------------------------
# id-grammar ids: YAML block style, YAML flow style, and a Markdown heading definition.
# ---------------------------------------------------------------------------------------------------------------

def test_id_grammar_yaml_block_style(built):
    res = citemod.cite_identifier("D-RA-0001", view_path=built.view_path, repo=str(built.root))
    assert res["kind"] == citemod.KIND_ID
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["label"] == citemod.LABEL_ID_GRAMMAR
    assert res["citation"]["path"] == repobuilder.DECISION_BLOCK_PATH


def test_id_grammar_yaml_flow_style(built):
    res = citemod.cite_identifier("D-RA-0002", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["citation"]["path"] == repobuilder.DECISION_FLOW_PATH


def test_id_grammar_markdown_heading(built):
    res = citemod.cite_identifier("RA-L-0001", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["citation"]["path"] == repobuilder.LEDGER_PATH
    assert res["citation"]["symbol"] is None


# ---------------------------------------------------------------------------------------------------------------
# Document section anchors: "<doc> §N" -- RESOLVED, AMBIGUOUS (two same-numbered headings) and NOT_FOUND.
# ---------------------------------------------------------------------------------------------------------------

def test_doc_section_anchor_resolves_nested_heading(built):
    res = citemod.cite_identifier("RA_GUIDE.md §2.1", view_path=built.view_path, repo=str(built.root))
    assert res["kind"] == citemod.KIND_DOC
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["label"] == citemod.LABEL_DOC_ANCHOR
    assert res["citation"]["path"] == repobuilder.GUIDE_PATH
    assert res["citation"]["section_title"].startswith("2.1")


def test_doc_section_anchor_top_level(built):
    res = citemod.cite_identifier("RA_GUIDE.md §1", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_RESOLVED
    assert res["citation"]["section_title"].startswith("1.")


def test_doc_section_anchor_ambiguous(built):
    res = citemod.cite_identifier("RA_DUP.md §3", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_AMBIGUOUS
    assert res["label"] == citemod.LABEL_DOC_ANCHOR
    assert len(res["candidates"]) == 2


def test_doc_section_anchor_not_found_wrong_number(built):
    res = citemod.cite_identifier("RA_GUIDE.md §9", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_NOT_FOUND


def test_doc_section_anchor_not_found_unknown_doc(built):
    res = citemod.cite_identifier("RA_NOPE_DOES_NOT_EXIST.md §1", view_path=built.view_path, repo=str(built.root))
    assert res["status"] == citemod.STATUS_NOT_FOUND


def test_classify_identifier_shapes():
    assert citemod.classify_identifier("RA_GUIDE.md §2.1") == citemod.KIND_DOC
    assert citemod.classify_identifier("D-RA-0001") == citemod.KIND_ID
    assert citemod.classify_identifier("ra_unique_fn") == citemod.KIND_CODE
    assert citemod.classify_identifier("ra_mod_one::ra_shared_fn") == citemod.KIND_CODE


# ---------------------------------------------------------------------------------------------------------------
# CLI: exit codes (0 only for RESOLVED), and QUERY-COMMAND READ-ONLY (BR-DAG-AMEND-R1-15) -- run `cite` (this
# module) AND `answers lint` (tests/answers/test_lint.py's own read-only test covers lint's half) against a
# file-and-directory read-only store; the store's own db file sha256 must be byte-identical before and after.
# ---------------------------------------------------------------------------------------------------------------

def test_cli_exit_codes(built, capsys):
    rc = citemod.main(["ra_unique_fn", "--view", built.view_path, "--repo", str(built.root)])
    assert rc == 0
    out = capsys.readouterr().out
    assert '"status": "RESOLVED"' in out

    rc = citemod.main(["ra_shared_fn", "--view", built.view_path, "--repo", str(built.root)])
    assert rc == 1  # AMBIGUOUS
    capsys.readouterr()

    rc = citemod.main(["ra_totally_unknown_fn", "--view", built.view_path, "--repo", str(built.root)])
    assert rc == 1  # NOT_FOUND


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cite_command_is_read_only_against_a_read_only_store(built):
    store_dir = storemod.store_root()
    db_path = storemod.db_path(store_dir)
    before_sha = _sha256_file(db_path)

    os.chmod(db_path, 0o444)
    os.chmod(store_dir, 0o555)
    try:
        # every identifier kind, once each, against the now read-only store
        for ident in ("ra_unique_fn", "ra_mod_one::ra_shared_fn", "test_ra_python_unique", "D-RA-0001",
                       "RA-L-0001", "RA_GUIDE.md §2.1"):
            res = citemod.cite_identifier(ident, view_path=built.view_path, repo=str(built.root))
            assert res["status"] in (citemod.STATUS_RESOLVED, citemod.STATUS_AMBIGUOUS), (ident, res)
        rc = citemod.main(["ra_unique_fn", "--view", built.view_path, "--repo", str(built.root)])
        assert rc == 0
    finally:
        os.chmod(store_dir, 0o755)
        os.chmod(db_path, 0o644)

    after_sha = _sha256_file(db_path)
    assert after_sha == before_sha, "govbridge cite wrote to the store file"
