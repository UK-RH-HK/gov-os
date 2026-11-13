"""Fixtures for the W2-105 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_105_support as support  # noqa: E402


@pytest.fixture(scope="session")
def pristine(tmp_path_factory):
    """A project generated from this worktree's template, with its tickets. Never run a hook in it."""
    try:
        return support.make_project(tmp_path_factory.mktemp("w2-105-generated"))
    except support.kernel_wiring.GenerationFailed as exc:
        pytest.fail(str(exc), pytrace=False)


@pytest.fixture(scope="session")
def settings(pristine):
    """The generated project's ``.claude/settings.json``."""
    return support.load_settings(pristine)


@pytest.fixture(scope="session")
def base_settings(pristine, tmp_path_factory):
    """What rulesync generates in the same project from the template's permission source before this ticket."""
    return support.generate_with_source(pristine, tmp_path_factory.mktemp("w2-105-base") / "product",
                                        support.base_source_text())


@pytest.fixture(scope="session")
def live(pristine, tmp_path_factory):
    """A copy of the generated project the cases ask the guard in."""
    return support.kernel_wiring.copy_project(pristine, tmp_path_factory.mktemp("w2-105-live") / "product")


@pytest.fixture(scope="session")
def sandbox(tmp_path_factory):
    return support.make_sandbox(tmp_path_factory.mktemp("w2-105-sandbox"))
