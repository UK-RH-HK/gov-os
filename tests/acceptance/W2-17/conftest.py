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


# ==========================================================================
# The fixes S5 to S7 (DEC-1223 (6)); added, nothing above is changed
# ==========================================================================

PATCH, NO_KIND, UNREADABLE_KIND, OTHER_KIND = (support.PATCH, support.NO_KIND, support.UNREADABLE_KIND,
                                              support.OTHER_KIND)


@pytest.fixture(scope="session")
def planted_sources(source, tmp_path_factory):
    """Copies of the source with two Fix: commits and a chore between v0.9.0 and v0.9.1, and B's kind: ``patch``
    (kind.json says patch; a decoy tag v0.9.2 with no record), ``no-kind`` (no kind.json), ``unreadable-kind``
    (kind.json not JSON), ``other-kind`` (kind.json says minor). Never changed."""
    base = tmp_path_factory.mktemp("w2-17-planted")
    kinds = {PATCH: support.PATCH_KIND, NO_KIND: None, UNREADABLE_KIND: b"{ not JSON: W2-17\n",
             OTHER_KIND: {"kind": "minor"}}
    return _built(lambda: {name: support.plant_source(source, base / name, kind=kind, decoy=name == PATCH)
                           for name, kind in kinds.items()})


@dataclass(frozen=True)
class DoctorCase:
    project: Path
    reference: object         # gov doctor --json with the source untouched (the link names the shared source)
    runs: dict                # {name: gov doctor --json with the link naming that source}


def _doctor_case(adopted, source, base, sources, prepare=None):
    """A copy of the adopted project whose answers name its source through a link; ``prepare(project)`` first;
    doctor run with the source untouched, then once per named source."""
    project = support.copy_project(adopted, base / "product")
    sandbox = support.make_sandbox(base / "sandbox")
    if prepare:
        prepare(project)
    link = base / "source-link"
    support.name_source_by_link(project, link, source.repo)
    reference = support.gov(project, sandbox, "doctor", "--json")
    runs = {}
    for name, target in sources.items():
        support.point(link, target)
        runs[name] = support.gov(project, sandbox, "doctor", "--json")
    support.point(link, source.repo)
    return DoctorCase(project, reference, runs)


@pytest.fixture(scope="session")
def doctor_at_a(adopted, source, planted_sources, tmp_path_factory):
    """The clone at A: doctor with the source untouched, then with each planted source and with no source."""
    base = tmp_path_factory.mktemp("w2-17-doctor-a")
    sources = {**planted_sources, "nowhere": base / "nowhere"}
    return _built(lambda: _doctor_case(adopted, source, base, sources))


@pytest.fixture(scope="session")
def doctor_rolled_back_here(adopted, source, planted_sources, tmp_path_factory):
    """The clone at A holding governance/updates/<B>.rolled-back.json: doctor untouched, then with the patch source."""
    base = tmp_path_factory.mktemp("w2-17-doctor-held")
    return _built(lambda: _doctor_case(adopted, source, base, {PATCH: planted_sources[PATCH]},
                                       prepare=support.plant_rolled_back_record))


@pytest.fixture(scope="session")
def doctor_no_release(adopted, source, planted_sources, tmp_path_factory):
    """The clone whose lock states release: null: doctor untouched, then with the patch source."""
    base = tmp_path_factory.mktemp("w2-17-doctor-null")
    return _built(lambda: _doctor_case(adopted, source, base, {PATCH: planted_sources[PATCH]},
                                       prepare=support.set_lock_release_null))


@dataclass(frozen=True)
class HookClone:
    project: Path
    sandbox: object
    link: Path                # the link the clone's _src_path names; it names the patch source
    quiet: Path               # a folder whose tk prints nothing
    source: Path              # the patch source


@pytest.fixture()
def hook_clone(adopted, planted_sources, tmp_path):
    """This case's copy of the adopted project at A, its source the patch source through a link."""
    def make():
        project = support.copy_project(adopted, tmp_path / "product")
        link = tmp_path / "source-link"
        support.name_source_by_link(project, link, planted_sources[PATCH])
        return HookClone(project, support.make_sandbox(tmp_path / "sandbox"), link,
                         support.fake_tk(tmp_path / "tk-quiet"), planted_sources[PATCH])
    return _built(make)


@pytest.fixture(scope="session")
def pinned_updated(adopted, tmp_path_factory):
    """A copy of the adopted project with A pinned (gov install A), then updated to B. Never changed."""
    base = tmp_path_factory.mktemp("w2-17-pinned-updated")
    return _built(lambda: support.build_pinned_update(adopted, base))


@dataclass(frozen=True)
class RolledBack:
    project: Path
    sandbox: object
    before: dict              # tree_state before the rollback
    before_pin: object        # pin_state before the rollback
    update_commit: str        # HEAD before the rollback: the update commit
    commit_before: str        # the commit before the update (A's)
    run: object               # gov update --rollback --json


def _rolled_back(origin_project, commit_before, base, binary_of=None):
    project = support.copy_project(origin_project, base / "product")
    sandbox = support.make_sandbox(base / "sandbox")
    before, before_pin, update_commit = support.tree_state(project), support.pin_state(project), support.head(project)
    binary = binary_of(project) if binary_of else None
    run = support.rollback(project, sandbox, binary=binary)
    return RolledBack(project, sandbox, before, before_pin, update_commit, commit_before, run)


@pytest.fixture(scope="session")
def rolled_back(pinned_updated, tmp_path_factory):
    """A copy of the pinned update, rolled back by A's environment's gov (<common>/gov/envs/<A>/bin/gov)."""
    base = tmp_path_factory.mktemp("w2-17-rolled-back")
    return _built(lambda: _rolled_back(pinned_updated.project, pinned_updated.before["head"], base,
                                       lambda project: support.env_gov(project, support.A)))


@pytest.fixture(scope="session")
def rolled_back_no_pin(updated, tmp_path_factory):
    """A copy of S2's update (no pin before it), rolled back by this worktree's gov (there is no A environment)."""
    base = tmp_path_factory.mktemp("w2-17-rolled-back-no-pin")
    return _built(lambda: _rolled_back(updated.project, updated.before["head"], base))
