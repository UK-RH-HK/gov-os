"""Acceptance tests for the zero-result canaries (W1-22, S2, F2, CAP-17.c, CAP-55.a).

Each derived index (lexical, semantic) has a small set of canary queries with known expected hits (DEC-037).
The declarations live under ``template/governance/kernel/canaries/``. A canary miss sets FACET_UNAVAILABLE,
never "no evidence exists" (CAP-55.a). NOT_FOUND is not a stopping reason: an empty index is a facet that is
unavailable, not proof that evidence is absent.

Interface fixed by this test suite (DP-2):

    ``gov.retrieval.canary.run_canaries(root: Path) -> dict``

    Returns a per-index report::

        {
            "lexical":  {"passed": bool, "status": str, "misses": [...]},
            "semantic": {"passed": bool, "status": str, "misses": [...]},
        }

    ``status`` is ``"AVAILABLE"`` when all canaries hit, ``"FACET_UNAVAILABLE"`` otherwise.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from w1_22_support import (
    build_fixture, CANARY_TEMPLATE_REL, INDEXES, FACET_UNAVAILABLE,
    REPO_ROOT, RUNTIME_REL,
)


# ---------------------------------------------------------------------------
# S2 (declarations): canary declarations exist for each index
# ---------------------------------------------------------------------------

class TestDeclarations:
    """No module needed — these tests check the template files on disk."""

    def test_canary_declarations_exist_for_each_index(self):
        """At least one canary declaration per derived index under the template directory (DEC-037)."""
        canary_dir = REPO_ROOT / CANARY_TEMPLATE_REL
        assert canary_dir.is_dir(), f"{CANARY_TEMPLATE_REL} does not exist"
        files = sorted(canary_dir.glob("*.yaml")) + sorted(canary_dir.glob("*.yml"))
        names = {f.stem for f in files}
        for index in INDEXES:
            assert index in names, \
                f"no canary declaration for the {index} index in {CANARY_TEMPLATE_REL}: found {sorted(names)}"


# ---------------------------------------------------------------------------
# S2 (runner): canaries per index, run after reindex [CAP-17.c, CAP-55.a]
# ---------------------------------------------------------------------------

class TestCanaryRunner:

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_runner_returns_per_index_results(self, canary_api, base, ollama, tmp_path):
        """The result has a key for each derived index with ``passed`` and ``status`` fields."""
        root = _indexed(base, canary_api, ollama, tmp_path)
        result = canary_api.run_canaries(root, env=canary_api.scratch_env(ollama.host))
        assert isinstance(result, dict), f"run_canaries returned {type(result).__name__}, expected dict"
        for index in INDEXES:
            assert index in result, f"the result has no key for the {index} index: {list(result)}"
            report = result[index]
            assert "passed" in report, f"the {index} report has no 'passed' field: {report}"
            assert "status" in report, f"the {index} report has no 'status' field: {report}"

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_lexical_canary_hits_after_reindex(self, canary_api, base, ollama, tmp_path):
        """After indexing a project with representative content, lexical canaries pass [CAP-17.c]."""
        root = _indexed(base, canary_api, ollama, tmp_path)
        result = canary_api.run_canaries(root, env=canary_api.scratch_env(ollama.host))
        lex = result["lexical"]
        assert lex["passed"] is True, f"lexical canaries failed after reindex: {lex}"

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_semantic_canary_hits_after_reindex(self, canary_api, base, ollama, tmp_path):
        """After indexing a project with representative content, semantic canaries pass [CAP-17.c]."""
        root = _indexed(base, canary_api, ollama, tmp_path)
        result = canary_api.run_canaries(root, env=canary_api.scratch_env(ollama.host))
        sem = result["semantic"]
        assert sem["passed"] is True, f"semantic canaries failed after reindex: {sem}"

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_canary_runner_is_callable_standalone(self, canary_api, base, ollama, tmp_path):
        """The runner is a standalone function, not tied to ``gov doctor`` (W1-27)."""
        root = _indexed(base, canary_api, ollama, tmp_path)
        result = canary_api.run_canaries(root, env=canary_api.scratch_env(ollama.host))
        assert isinstance(result, dict)
        assert all(index in result for index in INDEXES)


# ---------------------------------------------------------------------------
# S2 (miss): canary miss → FACET_UNAVAILABLE [CAP-55.a]
# ---------------------------------------------------------------------------

class TestCanaryMiss:

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_empty_project_canaries_fail_as_facet_unavailable(self, canary_api, tmp_path):
        """A project that has never been indexed: canaries miss, status is FACET_UNAVAILABLE [CAP-55.a]."""
        root = build_fixture(tmp_path / "empty")
        result = canary_api.run_canaries(root)
        for index in INDEXES:
            report = result[index]
            assert report["passed"] is False, f"{index} canaries passed on a project that was never indexed"
            assert report["status"] == FACET_UNAVAILABLE, \
                f"{index} status is {report['status']!r}, expected FACET_UNAVAILABLE"

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_deleted_store_canaries_fail_as_facet_unavailable(self, canary_api, base, ollama, tmp_path):
        """After deleting the store, canaries miss and report FACET_UNAVAILABLE [CAP-55.a]."""
        root = _indexed(base, canary_api, ollama, tmp_path)
        store = root / RUNTIME_REL / "store.db"
        if store.is_file():
            store.unlink()
        result = canary_api.run_canaries(root, env=canary_api.scratch_env(ollama.host))
        for index in INDEXES:
            assert result[index]["passed"] is False, \
                f"{index} canaries passed after deleting the store"

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_corrupted_store_reports_facet_unavailable(self, canary_api, base, ollama, tmp_path):
        """A corrupted store must report FACET_UNAVAILABLE, not crash (DEC-136)."""
        root = _indexed(base, canary_api, ollama, tmp_path)
        store = root / RUNTIME_REL / "store.db"
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_bytes(b"this is not a valid sqlite database")
        result = canary_api.run_canaries(root, env=canary_api.scratch_env(ollama.host))
        for index in INDEXES:
            assert index in result, f"canary runner crashed — no result for {index}"
            assert result[index]["status"] == FACET_UNAVAILABLE, \
                f"{index} status is {result[index]['status']!r}, expected FACET_UNAVAILABLE"


# ---------------------------------------------------------------------------
# F2: an empty index must NOT answer NOT_FOUND as absence [CAP-55.a]
# ---------------------------------------------------------------------------

class TestF2:

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_empty_index_never_reports_not_found(self, canary_api, tmp_path):
        """F2: an empty or missing index must give FACET_UNAVAILABLE, never NOT_FOUND.

        NOT_FOUND is not a stopping reason (CAP-55.a). Absence of an index is a facet being unavailable,
        not evidence that the answer does not exist."""
        root = build_fixture(tmp_path / "empty")
        result = canary_api.run_canaries(root)
        for index in INDEXES:
            assert result[index].get("status") != "NOT_FOUND", \
                f"F2 violated: {index} canaries reported NOT_FOUND on an empty index"
        assert "NOT_FOUND" not in str(result), \
            f"F2 violated: the canary result contains NOT_FOUND: {result}"

    @pytest.mark.needs("gitleaks", "sqlite_vec")
    def test_missing_store_never_reports_not_found(self, canary_api, base, ollama, tmp_path):
        """F2: after deleting the store, the canary runner must not say NOT_FOUND."""
        root = _indexed(base, canary_api, ollama, tmp_path)
        store = root / RUNTIME_REL / "store.db"
        if store.is_file():
            store.unlink()
        result = canary_api.run_canaries(root, env=canary_api.scratch_env(ollama.host))
        for index in INDEXES:
            assert result[index].get("status") != "NOT_FOUND", \
                f"F2 violated: {index} canaries reported NOT_FOUND after store deletion"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _indexed(base, api, ollama, tmp_path):
    """A copy of the base fixture, indexed through the stand-in endpoint."""
    root = tmp_path / "project"
    shutil.copytree(base, root)
    api.build(root, host=ollama.host)
    return root
