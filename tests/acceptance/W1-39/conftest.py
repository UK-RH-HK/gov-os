"""Fixtures for the W1-39 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W1-07"))

import w1_39_support as support  # noqa: E402


@pytest.fixture(scope="session")
def copier_bin():
    """The registered Copier. Where it is absent or another version, the case fails with its need; it never skips."""
    return support.require_copier()


@pytest.fixture(scope="session")
def pristine_source(tmp_path_factory):
    """The template source of the first release: ``copier.yml`` and ``template/`` alone, in a temporary git
    repository, tagged. Never changed: every test works on a copy of this temporary folder."""
    try:
        return support.assemble_source(tmp_path_factory.mktemp("w1-39-source") / "gov-os-template")
    except support.TemplateMissing as exc:
        pytest.fail(str(exc), pytrace=False)


@pytest.fixture(scope="session")
def pristine_creation(copier_bin, pristine_source, tmp_path_factory):
    """A project created once by ``copier copy`` from the first release, and the run that created it."""
    base = tmp_path_factory.mktemp("w1-39-pristine")
    return support.create_project_and_run(copier_bin, support.make_sandbox(base / "sandbox"), pristine_source,
                                          base / "product")


@pytest.fixture(scope="session")
def pristine_project(pristine_creation):
    """The project created once for the session. Never changed."""
    return pristine_creation[0]


@pytest.fixture(scope="session")
def copy_run(pristine_creation):
    """The run of ``copier copy`` that created the session's project: what Copier printed."""
    return pristine_creation[1]


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the commands' folder and the bytecode cache, outside the project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def source(pristine_source, tmp_path):
    """This test's own template source: a copy of the temporary one (never of this repository), same tag and commit."""
    target = tmp_path / "gov-os-template"
    shutil.copytree(pristine_source.path, target, symlinks=True)
    return support.Source(target, pristine_source.first)


@pytest.fixture()
def project(copier_bin, source, sandbox, tmp_path):
    """This test's own project, created by ``copier copy`` from this test's template source and committed."""
    return support.create_project(copier_bin, sandbox, source, tmp_path / "product")


@pytest.fixture()
def installed(pristine_project):
    """The project created once for the session, for cases that only read it."""
    return pristine_project
