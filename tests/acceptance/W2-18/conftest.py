"""Fixtures for the W2-18 acceptance tests (the pinned install, DAEO-057v).

Releases, the adopted product and the pins no case changes are built once per session (per worker under xdist). A
case that changes a product works on its own copy, made before any pin is put in it (a pin's environment holds
absolute paths, so a pinned product is never copied).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import w2_18_support as support  # noqa: E402


def _built(make):
    """The fixture's value; a failed fixture step fails the case with its message, never a skip."""
    try:
        return make()
    except AssertionError as exc:
        message = str(exc)
    pytest.fail(message, pytrace=False)


@dataclass(frozen=True)
class Installed:
    project: Path
    run: object             # the run of `gov install <version>`, whatever its exit code


@pytest.fixture(scope="session")
def copier_bin():
    return _built(support.w216.require_copier)


@pytest.fixture(scope="session")
def releases(tmp_path_factory):
    """The stand-in Gov OS repository with releases A (0.9.0) and B (0.9.1), tagged vA and vB. Never changed."""
    return _built(lambda: support.build_releases(tmp_path_factory.mktemp("w2-18-releases")))


@pytest.fixture(scope="session")
def adopted(copier_bin, releases, tmp_path_factory):
    """A product adopted from vA by `copier copy` (its lock names release A), no pin. Never changed: copy it."""
    return _built(lambda: support.adopt(copier_bin, releases, tmp_path_factory.mktemp("w2-18-adopted") / "product"))


@pytest.fixture(scope="session")
def installed_a(adopted, tmp_path_factory):
    """A copy of the adopted product in which `gov install 0.9.0` ran (no --source: the answers' _src_path)."""
    base = tmp_path_factory.mktemp("w2-18-installed-a")
    project = support.copy_project(adopted, base / "product")
    done = support.worktree_gov(project, support.make_sandbox(base / "sandbox"), "install", support.VERSION_A)
    return Installed(project, done)


def _planted(adopted, releases, tmp_path_factory, version):
    base = tmp_path_factory.mktemp(f"w2-18-planted-{version}")
    project = support.copy_project(adopted, base / "product")
    support.plant_pin(project, releases, version, support.make_sandbox(base / "sandbox"))
    return project


@pytest.fixture(scope="session")
def planted_a(adopted, releases, tmp_path_factory):
    """A copy of the adopted product (lock: A) with a pin of release A made by hand. Never changed."""
    return _built(lambda: _planted(adopted, releases, tmp_path_factory, support.VERSION_A))


@pytest.fixture(scope="session")
def planted_b(adopted, releases, tmp_path_factory):
    """A copy of the adopted product (lock: A) with a pin of release B made by hand. Never changed."""
    return _built(lambda: _planted(adopted, releases, tmp_path_factory, support.VERSION_B))


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, a commands folder and the bytecode cache of one case, outside every repository."""
    return support.make_sandbox(tmp_path / "sandbox")
