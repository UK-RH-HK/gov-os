"""Fixtures for W2-93's acceptance tests (form only: counts, fields, sources exist).

The tests plant a stand-in sets root in their own temporary folders and run the validator and the runner as
subprocesses. W2-81's modules are integrated code and are imported read-only: its folder is put on ``sys.path`` here.
Nothing here reads or writes the real hidden half, and nothing is written in this repository.
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
W2_81 = REPO_ROOT / "tests" / "acceptance" / "W2-81"

for folder in (W2_81, HERE):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

import w2_93_standin as standin  # noqa: E402


@dataclass
class Valid:
    """The valid stand-in sets root, and the one validator run on it that several cases read."""

    root: Path
    base: Path
    run: object
    root_before: dict
    root_after: dict
    repo_before: str
    repo_after: str


@pytest.fixture(scope="session")
def valid(tmp_path_factory):
    """The valid stand-in, planted once per process, with one validator run on it (``--sets-root`` only)."""
    base = tmp_path_factory.mktemp("w2-93-valid")
    root = standin.make_root(base)
    root_before, repo_before = standin.snapshot(root), standin.porcelain()
    run = standin.validate(root, base)
    return Valid(root, base, run, root_before, standin.snapshot(root), repo_before, standin.porcelain())


@pytest.fixture(scope="session")
def visible(tmp_path_factory):
    """The kinds each repository's visible build holds, read from a build without variants (never a fixed list)."""
    import w2_81_build as build

    folder = tmp_path_factory.mktemp("w2-93-visible")
    built = build.build_all(folder, standin.SEED, standin.LARGE)
    kinds = standin.visible_kinds(built)
    shutil.rmtree(folder)
    return kinds
