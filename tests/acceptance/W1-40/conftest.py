"""Fixtures for the W1-40 acceptance tests (lefthook hooks and the CI workflow)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_40_support as support  # noqa: E402


@pytest.fixture(scope="session")
def lefthook():
    """lefthook runs here, at its registered version; where it does not, the hook cases skip by name."""
    path = support.real_tool("lefthook")
    if not path:
        pytest.skip("lefthook is not on this machine: the hook cases need the binary (tool registry: lefthook)")
    return path


@pytest.fixture(scope="session")
def gitleaks():
    path = support.real_tool("gitleaks")
    if not path:
        pytest.skip("gitleaks is not on this machine: the secret cases need the binary (DEC-287)")
    return path


@pytest.fixture()
def marks(tmp_path):
    return tmp_path / "marks"


@pytest.fixture()
def project(lefthook, gitleaks, tmp_path, marks):
    """A temporary project, green by construction, with the hooks of ``lefthook.yml`` installed."""
    try:
        return support.Project(tmp_path, marks)
    except support.Absent as absent:
        pytest.fail(str(absent), pytrace=False)


@pytest.fixture()
def machine(tmp_path, marks):
    """``machine(**what)``: a machine with lefthook, gitleaks and gov, unless ``what`` withholds one."""
    made = []

    def make(**what):
        made.append(support.Machine(tmp_path / f"machine-{len(made)}", marks, **what))
        return made[-1]
    return make


@pytest.fixture()
def new_project(request, tmp_path, marks):
    """``new_project(tiers=..., hooks=...)``: a temporary project that declares checks for ``tiers`` only.

    With ``hooks=False`` it has no hook file and needs neither lefthook nor gitleaks. Not to be mixed with the
    ``project`` fixture in one case: both build in the case's temporary folder.
    """
    def make(tiers=tuple(support.TIER_CHECKS), hooks=True):
        if hooks:
            request.getfixturevalue("lefthook")
            request.getfixturevalue("gitleaks")
        try:
            return support.Project(tmp_path, marks, tiers=tiers, hooks=hooks)
        except support.Absent as absent:
            pytest.fail(str(absent), pytrace=False)
    return make


@pytest.fixture()
def ci(request, machine, tmp_path):
    """``ci(**what)``: the push workflows' steps run on a fresh checkout of what ``origin`` holds.

    The project is the ``project`` fixture, or the one given as ``of=``.
    """
    count = []

    def run(of=None, **what):
        count.append(1)
        subject = of if of is not None else request.getfixturevalue("project")
        try:
            return support.Runner(subject, machine(**what), tmp_path / f"ci-{len(count)}").run()
        except support.Absent as absent:
            pytest.fail(str(absent), pytrace=False)
        except support.Unsupported as unsupported:
            pytest.fail(f"the workflow cannot be run offline: {unsupported}", pytrace=False)
    return run


@pytest.fixture()
def pushed(project, machine):
    """A new commit, made and pushed through the hooks on a complete machine, all checks passing."""
    return project.through_the_hooks(machine())
