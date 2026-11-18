"""Fixtures for the W2-17 acceptance tests (``gov update``).

The source with releases A and B, the project adopted at A, the dry run and the update are built once per session:
the cases that only read an outcome share them. A case that runs ``gov update`` itself (the rollback, the refusals)
works on its own copy of the adopted project (a temporary folder, never this repository).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE, _HERE.parent / "W2-16", _HERE.parent / "W1-39", _HERE.parent / "W1-07"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_17_support as support  # noqa: E402


def _built(make):
    """``make()``, or the case fails with the fixture's own message (a fixture error, never the feature's)."""
    try:
        return make()
    except AssertionError as exc:
        message = f"W2-17 fixture could not be built (not the feature under test): {exc}"
    pytest.fail(message, pytrace=False)


@pytest.fixture(scope="session")
def copier_bin():
    return _built(support.w216.require_copier)


@pytest.fixture(scope="session")
def source(tmp_path_factory):
    """The stand-in Gov OS repository holding releases A (v0.9.0) and B (v0.9.1). Never changed."""
    base = tmp_path_factory.mktemp("w2-17-source")
    return _built(lambda: support.build_source(base / "gov-os", support.make_sandbox(base / "sandbox")))


@pytest.fixture(scope="session")
def adopted(copier_bin, source, tmp_path_factory):
    """The project adopted at A, adapters generated, its own changes made, all committed. Never changed."""
    base = tmp_path_factory.mktemp("w2-17-adopted")
    return _built(lambda: support.adopt(copier_bin, source.repo, base / "product",
                                        support.make_sandbox(base / "sandbox")))


@pytest.fixture(scope="session")
def project_at_b(copier_bin, source, tmp_path_factory):
    """A project adopted at B directly (adapters generated, committed). Never changed."""
    base = tmp_path_factory.mktemp("w2-17-at-b")
    return _built(lambda: support.adopt(copier_bin, source.repo, base / "product",
                                        support.make_sandbox(base / "sandbox"), tag=support.TAG_B,
                                        local_changes=False))


@dataclass(frozen=True)
class Outcome:
    project: Path
    sandbox: object
    before: dict              # tree_state before the run(s)
    before_overlay: dict      # overlay_hashes before
    before_pin: object        # pin_state before
    before_bytes: dict        # {rel: bytes} of the locally changed files before
    run: object               # the --json run
    text: object = None       # the text-form run (the dry run only)
    after: dict = None        # tree_state right after the run(s)
    after_pin: object = None
    porcelain: list = None


def _outcome(adopted, base, args, text_form):
    project = support.copy_project(adopted, base / "product")
    sandbox = support.make_sandbox(base / "sandbox")
    before = support.tree_state(project)
    before_overlay = support.overlay_hashes(project)
    before_pin = support.pin_state(project)
    before_bytes = {rel: (project / rel).read_bytes() for rel in support.LOCALLY_CHANGED}
    run = support.update(project, sandbox, *args)
    text = support.update(project, sandbox, *args, json_form=False) if text_form else None
    return Outcome(project, sandbox, before, before_overlay, before_pin, before_bytes, run, text,
                   support.tree_state(project), support.pin_state(project), support.porcelain_paths(project))


@pytest.fixture(scope="session")
def checked(adopted, tmp_path_factory):
    """``gov update B --check --json``, then ``gov update B --check``, in a copy of the adopted project."""
    return _outcome(adopted, tmp_path_factory.mktemp("w2-17-checked"), ("--check",), True)


@pytest.fixture(scope="session")
def updated(adopted, tmp_path_factory):
    """``gov update B --json`` in a copy of the adopted project."""
    return _outcome(adopted, tmp_path_factory.mktemp("w2-17-updated"), (), False)


@pytest.fixture()
def own_project(adopted, tmp_path):
    """This case's own copy of the adopted project."""
    return support.copy_project(adopted, tmp_path / "product")


@pytest.fixture()
def sandbox(tmp_path):
    return support.make_sandbox(tmp_path / "sandbox")
