"""Builder tests for W2-107: the rebuild's record gives the secrets filter's counts (DEC-970 P-W2-107-3, KPI 7).

Regression evidence only (DEC-136). A small git tree with one planted secret is rebuilt twice, unchanged: the lexical
index and the code index's filter run for real, with the real gitleaks; the record store, the semantic vectors and the
code-index tool are stand-ins, so no embedder and no indexing binary is started. The scan record is the test's own, by
GOV_SECRETS_CACHE, never the machine's. No secret stands whole in this file: the planted string is built at run time.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import pytest

from gov import secrets
from gov.rebuild.command import add_arguments, run

REPO = Path(__file__).resolve().parents[3]
PLANTED = "_".join(["ARGUS", "TOKEN", "CAN" + "ARY", "4WM8"])
MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
CONFIG = {"path-map.yaml": {"namespaces": {"everything": {"paths": ["**"], "memory_class": "governance"}}}}

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None or shutil.which("git") is None,
                                reason="gitleaks or git is not on PATH")


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def tree(tmp_path, monkeypatch):
    """Seven tracked files, one of them holding a planted secret; the stores but the lexical index stood in."""
    project = tmp_path / "project"
    _write(project, "governance/project/path-map.yaml", MAP)
    _write(project, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    _write(project, ".gitignore", ".gov-runtime/\n")
    for number in range(3):
        _write(project, f"notes/{number}.md", f"Ordinary text {number}.\n")
    _write(project, "notes/planted.md", f"The value is {PLANTED} today.\n")
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        monkeypatch.delenv(name, raising=False)
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(["git", "-C", str(project), "add", "-A"], check=True)
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(tmp_path / "cache" / "secrets-scan.sqlite"))
    monkeypatch.delenv("GOV_SECRETS_FULL_SCAN", raising=False)
    monkeypatch.setenv("GOV_REBUILD_LOCK", str(tmp_path / "rebuild.lock"))
    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.semantic.refresh", lambda root: {"available": False, "reason": "stood in"})
    monkeypatch.setattr("gov.codeintel._tool", lambda *given, **named: {})
    return project


def _rebuild(project: Path) -> dict:
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    result = run(project, parser.parse_args([]), CONFIG)
    assert result["stores"]["lexical"] == {"status": "recreated"}
    assert result["stores"]["codeintel"] == {"status": "recreated"}
    return result["secrets_counts"]


def test_the_record_holds_every_kind_with_both_numbers(tree):
    counts = _rebuild(tree)
    assert set(counts) == set(secrets.scan_counts())
    for each in counts.values():
        assert set(each) == {"scanned", "remembered"} and all(isinstance(number, int) for number in each.values())


def test_an_unchanged_second_rebuild_scans_only_the_planted_secret_again(tree):
    """Seven contents, six clean. The first rebuild's lexical stage scans all seven; its code-index stage answers the
    six clean ones from those verdicts and scans the planted one again, then scans the six clean paths' names. The
    second rebuild's lexical stage asks nothing (its blobs are unchanged); its code-index stage answers every clean
    content and name from the record and scans the planted content alone."""
    first = _rebuild(tree)
    second = _rebuild(tree)
    assert first == {"content": {"scanned": 8, "remembered": 6}, "path": {"scanned": 6, "remembered": 0}}
    assert second == {"content": {"scanned": 1, "remembered": 6}, "path": {"scanned": 0, "remembered": 6}}
