"""Fixtures for the W2-107 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_107_support as support  # noqa: E402


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    """No case sees the runner's own cache settings, and HOME is the case's own folder, so even a filter that ignored
    ``GOV_SECRETS_CACHE`` would never reach the real ``~/.cache/gov-os/``."""
    for name in support.SETTINGS:
        monkeypatch.delenv(name, raising=False)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture()
def engine(tmp_path, monkeypatch):
    """A stand-in gitleaks first on PATH: it counts its scan calls and hands each to the real gitleaks."""
    made = support.make_engine(tmp_path / "engine-a", tag="a")
    monkeypatch.setenv("PATH", made.path())
    return made


@pytest.fixture()
def cache(tmp_path, monkeypatch):
    """The case's own cache file, named by ``GOV_SECRETS_CACHE``, in a folder of its own that exists."""
    folder = tmp_path / "cache"
    folder.mkdir()
    path = folder / support.CACHE_NAME
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(path))
    return path


@pytest.fixture()
def project(tmp_path):
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def per_text(engine, project):
    """The scan calls one clean text costs with no cache (one per rule set in force, as the filter runs them)."""
    rel = support.put(project, {"docs/w2-107-baseline.md": "W2-107: a baseline text, judged with no cache.\n"})
    kept, calls = support.uncached(engine, lambda: support.gov_secrets.indexable(project, rel))
    assert kept == rel and calls >= 1, "premise: a clean text is scanned and let through"
    (project / rel[0]).unlink()
    return calls
