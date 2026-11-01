"""Fixtures for the W2-16 acceptance tests.

Copier runs and release builds are slow, so the releases and the projects that no case changes are made once
per session. A case that changes one works on its own copy of the *temporary* folder (never of this
repository).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE, _HERE.parent / "W1-39", _HERE.parent / "W1-07"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_16_support as support  # noqa: E402


@dataclass(frozen=True)
class Releases:
    repo: Path              # the stand-in Gov OS repository holding both releases (never changed)
    first: object           # ReleaseRecord of FIRST_VERSION, tagged FIRST_TAG
    second: object          # ReleaseRecord of SECOND_VERSION, tagged SECOND_TAG


@pytest.fixture(scope="session")
def copier_bin():
    """The registered Copier. Where it is absent or another version, the case fails with its need; it never skips."""
    return support.require_copier()


@pytest.fixture(scope="session")
def pristine_repo(tmp_path_factory):
    """A stand-in Gov OS repository: one clean commit on w2/integrate, no release, no tag. Never changed."""
    return support.build_gov_os_repository(tmp_path_factory.mktemp("w2-16-pristine") / "gov-os")


@pytest.fixture(scope="session")
def releases(pristine_repo, tmp_path_factory):
    """Two releases built by `gov release` in a copy of the stand-in, each committed and tagged (unsigned) as the
    owner would; a shipped file changes between them. Never changed after it is built."""
    base = tmp_path_factory.mktemp("w2-16-releases")
    repo = support.clone_folder(pristine_repo, base / "gov-os")
    sandbox = support.make_sandbox(base / "sandbox")
    try:
        first = support.build_release(repo, sandbox, support.FIRST_VERSION, tag=support.FIRST_TAG)
        (repo / support.CHANGED_BY_SECOND_RELEASE).write_text("W2-16: a shipped file, second form\n",
                                                              encoding="utf-8")
        support.commit_all(repo, "a change to a shipped file, for the second release")
        second = support.build_release(repo, sandbox, support.SECOND_VERSION, tag=support.SECOND_TAG)
    except AssertionError as exc:
        message = str(exc)
    else:
        message = None
    if message:
        pytest.fail(message, pytrace=False)
    return Releases(repo, first, second)


@pytest.fixture(scope="session")
def release_project(copier_bin, releases, tmp_path_factory):
    """A project created by `copier copy` from the first release's tag. Never changed."""
    base = tmp_path_factory.mktemp("w2-16-release-project")
    try:
        return support.create_project(copier_bin, support.make_sandbox(base / "sandbox"), releases.repo,
                                      base / "product", support.FIRST_TAG)
    except AssertionError as exc:
        message = str(exc)
    else:
        message = None
    if message:
        pytest.fail(message, pytrace=False)


@pytest.fixture(scope="session")
def updated_project(copier_bin, releases, tmp_path_factory):
    """A project created from the first release's tag and updated by `copier update` to the second's. Never changed."""
    base = tmp_path_factory.mktemp("w2-16-updated-project")
    sandbox = support.make_sandbox(base / "sandbox")
    try:
        project = support.create_project(copier_bin, sandbox, releases.repo, base / "product", support.FIRST_TAG)
        done = support.update(copier_bin, sandbox, project, support.SECOND_TAG)
        assert done.returncode == 0, f"`copier update` to {support.SECOND_TAG} failed\n{support.copier_report(done)}"
    except AssertionError as exc:
        message = str(exc)
    else:
        message = None
    if message:
        pytest.fail(message, pytrace=False)
    support.commit_all(project, f"updated by copier update to {support.SECOND_TAG}")
    return project


@pytest.fixture(scope="session")
def plain_source(tmp_path_factory):
    """W1-39's template source (copier.yml and template/ alone, tagged), which holds no release record."""
    try:
        return support.build_plain_source(tmp_path_factory.mktemp("w2-16-plain-source") / "gov-os-template")
    except AssertionError as exc:
        message = str(exc)
    else:
        message = None
    if message:
        pytest.fail(message, pytrace=False)


@pytest.fixture(scope="session")
def plain_project(copier_bin, plain_source, tmp_path_factory):
    """A project created by `copier copy` from the plain template source. Never changed."""
    base = tmp_path_factory.mktemp("w2-16-plain-project")
    try:
        return support.create_project(copier_bin, support.make_sandbox(base / "sandbox"), plain_source,
                                      base / "product", support.PLAIN_TAG)
    except AssertionError as exc:
        message = str(exc)
    else:
        message = None
    if message:
        pytest.fail(message, pytrace=False)


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the commands' folder and the bytecode cache, outside every repository."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def repo(pristine_repo, tmp_path):
    """This case's own copy of the pristine stand-in repository."""
    return support.clone_folder(pristine_repo, tmp_path / "gov-os")


@pytest.fixture()
def release_repo(releases, tmp_path):
    """This case's own copy of the repository that holds both releases (same commits, same tags)."""
    return support.clone_folder(releases.repo, tmp_path / "gov-os")


@pytest.fixture()
def own_release_project(release_project, tmp_path):
    """This case's own copy of the project installed from the first release."""
    return support.clone_folder(release_project, tmp_path / "product")


@pytest.fixture()
def own_plain_project(plain_project, tmp_path):
    """This case's own copy of the project installed from the plain template source."""
    return support.clone_folder(plain_project, tmp_path / "product")
