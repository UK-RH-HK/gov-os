"""W2-124 S3: adoption never fails for a semantic store not recreated: stage A6 finishes, and its committed record and
its result hold the finding ``SEMANTIC_NOT_RECREATED`` with the reason and the rebuild command (DEC-1027 C).

Planted repositories (the ``root`` fixture of ``test_adopt``); ``gov rebuild`` is a stand-in that fails as the real one
does, with a ``REBUILD_FAILED`` of the semantic store. No embedder runs."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from gov.adopt import project, stages
from gov.cli.errors import GovError

from .test_adopt import record, refused, root, stage  # noqa: F401
from .test_safety import THREE, audited, at_move

REAL_REBUILD = stages.rebuild  # the fixture of ``test_adopt`` replaces ``stages.rebuild`` in each test

REASON = "the embedding endpoint is unavailable"
STORES = {"lexical": {"status": "recreated"}, "semantic": {"status": "not_recreated", "reason": REASON},
          "codeintel": {"status": "recreated"}}
FINDING = {"code": "SEMANTIC_NOT_RECREATED", "store": "semantic", "reason": REASON, "command": "gov rebuild"}


def _semantic_failure(*_):
    raise GovError("REBUILD_FAILED", f"rebuild failed on the semantic store (store: semantic): {REASON}",
                   {"store": "semantic", "reason": REASON, "stores": STORES})


def _rebuilt(monkeypatch, does):
    """The real ``stages.rebuild`` over a stand-in ``gov rebuild`` that does ``does``; the calls it was asked."""
    asked = []
    monkeypatch.setattr(stages, "rebuild", REAL_REBUILD)
    monkeypatch.setattr("gov.rebuild.command.run", lambda *given: asked.append(given) or does(*given))
    return asked


def test_a6_finishes_and_its_committed_record_and_result_hold_the_finding(root, monkeypatch):
    asked = _rebuilt(monkeypatch, _semantic_failure)
    audited(root, *THREE)
    result = stage(root, "A6")
    assert len(asked) == 1
    committed = record(root, "A6")
    assert committed["status"] == "done" and committed["findings"] == [FINDING]
    assert result["findings"] == [FINDING] and result["rebuild"] == STORES
    assert project.dirty(root) == []
    assert project.record_path("A6") in project.git(root, "show", "--name-only", "--format=", "HEAD")


def test_a6s_record_is_committed_with_the_finding_not_amended_after_it(root, monkeypatch):
    _rebuilt(monkeypatch, _semantic_failure)
    audited(root, *THREE)
    before = project.git(root, "rev-list", "--count", "HEAD").strip()
    stage(root, "A6")
    # the three batches' commits (two batches) and one record commit; the finding is in that one
    assert int(project.git(root, "rev-list", "--count", "HEAD").strip()) - int(before) == 3
    assert "SEMANTIC_NOT_RECREATED" in project.git(root, "show", "HEAD:" + project.record_path("A6"))


def test_a_refresh_that_recreated_everything_leaves_no_findings(root, monkeypatch):
    stores = {"lexical": {"status": "recreated"}, "semantic": {"status": "recreated"}}
    _rebuilt(monkeypatch, lambda *given: {"stores": stores})
    audited(root, *THREE)
    result = stage(root, "A6")
    assert "findings" not in record(root, "A6") and "findings" not in result and result["rebuild"] == stores


def test_any_other_rebuild_failure_stays_index_refresh_failed_after_the_record_is_committed(root, monkeypatch):
    def lexical_failure(*_):
        raise GovError("REBUILD_FAILED", "rebuild failed on the lexical index: boom", {"store": "lexical"})

    _rebuilt(monkeypatch, lexical_failure)
    audited(root, *THREE)
    error = refused("INDEX_REFRESH_FAILED", root, "A6")
    assert "boom" in error.message and "done and committed" in error.message
    committed = record(root, "A6")
    assert committed["status"] == "done" and "findings" not in committed


def test_a_semantic_failure_with_no_lexical_index_is_still_an_index_refresh_failure(root, monkeypatch):
    def no_path_map(*_):
        raise GovError("REBUILD_FAILED", "x (store: semantic)", {
            "store": "semantic", "reason": REASON,
            "stores": {"lexical": {"status": "not_recreated", "reason": "no path map"}}})

    _rebuilt(monkeypatch, no_path_map)
    audited(root, *THREE)
    refused("INDEX_REFRESH_FAILED", root, "A6")


def test_a_failed_batch_runs_no_rebuild_and_its_record_holds_no_finding(root, monkeypatch):
    asked = _rebuilt(monkeypatch, _semantic_failure)
    audited(root, *THREE)
    at_move(monkeypatch, 2, project.refuse("GIT_FAILED", "planted"))
    refused("BATCH_FAILED", root, "A6")
    assert asked == [] and record(root, "A6")["status"] == "failed" and "findings" not in record(root, "A6")


def test_the_rebuild_stage_itself_reads_the_error_s_details(tmp_path, monkeypatch):
    """The refresh after A8 (``legacy.retire``) calls the same function: the same catch, the finding in its result."""
    _rebuilt(monkeypatch, _semantic_failure)
    run = SimpleNamespace(root=tmp_path, args=SimpleNamespace(), config={}, stage="A8")
    result = stages.rebuild(run, {"stage": "A8", "record": "r.md"})
    assert result == {"stage": "A8", "record": "r.md", "rebuild": STORES, "findings": [FINDING]}


@pytest.mark.parametrize("code, details", [("REBUILD_FAILED", {"store": "record"}), ("REBUILD_FAILED", {}),
                                           ("OTHER", {"store": "semantic"})])
def test_only_a_rebuild_failure_of_the_semantic_store_is_a_finding(tmp_path, monkeypatch, code, details):
    def fails(*_):
        raise GovError(code, "planted", details)

    _rebuilt(monkeypatch, fails)
    run = SimpleNamespace(root=tmp_path, args=SimpleNamespace(), config={}, stage="A8")
    with pytest.raises(GovError) as raised:
        stages.rebuild(run, {"stage": "A8", "record": "r.md"})
    assert raised.value.code == "ADOPT_INDEX_REFRESH_FAILED" and "planted" in raised.value.message
