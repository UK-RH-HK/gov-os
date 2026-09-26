"""BR-DAG-AMEND-R1-15 ("QUERY COMMANDS ARE READ-ONLY"), the ``govbridge answers lint`` half (``tests/answers/
test_cite.py::test_cite_command_is_read_only_against_a_read_only_store`` covers ``cite``). ``answers lint`` calls
``govbridge.answers.cite`` internally for its own NAMED_NOT_CITED check, so it reaches the store the SAME way --
this test forces that path (an answer whose claim names a real Rust symbol, uncited) against a store made read-only
at the FILE AND DIRECTORY level, and asserts the store's own db file sha256 is byte-identical before and after.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

FIXTURES_ANSWERS = Path(__file__).resolve().parents[1] / "fixtures" / "answers"
if str(FIXTURES_ANSWERS) not in sys.path:
    sys.path.insert(0, str(FIXTURES_ANSWERS))
import answers_repobuilder as repobuilder  # noqa: E402

from govbridge.answers import lint as lintmod  # noqa: E402
from govbridge.core import freshness as freshnessmod  # noqa: E402
from govbridge.core import store as storemod  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-test-lint-readonly"))
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_answers_lint_is_read_only_against_a_read_only_store(tmp_path):
    repo = repobuilder.build(tmp_path)
    r = freshnessmod.run(view_path=repo.view_path, rules_path=repo.rules_path, repo=str(repo.root), from_clean=True)
    assert r["trigger"] == "FULL"

    store_dir = storemod.store_root()
    db_path = storemod.db_path(store_dir)
    before_sha = _sha256_file(db_path)

    answers_doc = {
        "schema": "govbridge-answers/1", "run_id": "RA-RO-TEST", "packets_used": [],
        "answers": [
            {
                "query_id": "QRO1", "status": "ANSWERED",
                # ra_unique_fn is named but NOT cited: this is what makes the lint's own NAMED_NOT_CITED check
                # call govbridge.answers.cite -> govbridge.code.symbols (a store read), the exact path this test
                # means to exercise under a read-only store.
                "answer_text": "The change is in ra_unique_fn.",
                "citations": [],
            },
        ],
    }
    packet_dir = tmp_path / "packet"
    packet_dir.mkdir()
    (packet_dir / "manifest.json").write_text(json.dumps({"sections": {}}), encoding="utf-8")
    answers_path = tmp_path / "answers.yaml"
    import yaml as pyyaml
    answers_path.write_text(pyyaml.safe_dump(answers_doc, sort_keys=False), encoding="utf-8")

    os.chmod(db_path, 0o444)
    os.chmod(store_dir, 0o555)
    try:
        result = lintmod.lint_answers(answers_doc, [str(packet_dir)], view_path=repo.view_path, repo=str(repo.root))
        named = [f for f in result["findings"] if f["kind"] == lintmod.KIND_NAMED_NOT_CITED]
        assert any(f["identifier"] == "ra_unique_fn" for f in named), (
            "the read-only-store path was never actually exercised (ra_unique_fn should resolve and be flagged)")

        rc = lintmod.main([str(answers_path), "--packet", str(packet_dir), "--view", repo.view_path,
                            "--repo", str(repo.root)])
        assert rc == 1
    finally:
        os.chmod(store_dir, 0o755)
        os.chmod(db_path, 0o644)

    after_sha = _sha256_file(db_path)
    assert after_sha == before_sha, "govbridge answers lint wrote to the store file"
