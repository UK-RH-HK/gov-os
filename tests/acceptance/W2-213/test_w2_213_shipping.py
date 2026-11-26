"""SL-4: the standard travels with the kit, drifts like a kit file, and the check always reads a shipped copy.

The adopted project, releases A and B and ``gov update`` are W2-17's harness: a stand-in Gov OS repository built from
this worktree's files, release A without the standard, release B with it. The installed release is the gov that
``gov update`` pins from release B's wheel; the "no shipped copy" cases run a plain copy of the ``gov`` package (no
source tree above it) with its shipped standard taken out.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

import w2_213_support as support

_ACCEPTANCE = Path(__file__).resolve().parent.parent
for _folder in ("W2-17", "W2-16", "W1-39", "W1-07"):
    if str(_ACCEPTANCE / _folder) not in sys.path:
        sys.path.insert(0, str(_ACCEPTANCE / _folder))


def _installed_copy(destination):
    """The ``gov`` package alone, as an install lays it out: no ``copier.yml``, ``template/`` or ``src/`` above it."""
    shutil.copytree(support.SRC / "gov", destination / "gov", ignore=shutil.ignore_patterns("__pycache__"))
    return destination


def _repo_without_the_kits_copy(clean_repo, destination):
    root = support.copy_repository(clean_repo, destination)
    support.git(root, "rm", "-q", support.KIT_COPY)
    support.commit(root, "planted: no kit copy of the standard")
    return root, support.without(support.clean_lines(), support.KIT_COPY)


def _built_standard():
    assert support.STANDARD.is_file(), f"the kit holds no standard file: {support.STANDARD_REL}"
    return support.load_yaml(support.STANDARD)


def test_sl4_the_package_ships_the_standard_byte_for_byte_and_names_it_as_package_data():
    _built_standard()
    assert support.SHIPPED_COPY.is_file(), f"no shipped copy at {support.SHIPPED_COPY}"
    assert support.SHIPPED_COPY.read_bytes() == support.STANDARD.read_bytes(), "the shipped copy differs"
    pyproject = (support.TREE / "pyproject.toml").read_text(encoding="utf-8")
    assert f"_shipped/{support.STANDARD_REL}" in pyproject, "pyproject.toml's package data does not name the standard"


@dataclass(frozen=True)
class Adopted:
    project: Path
    sandbox: object
    harness: object
    update: object


@pytest.fixture(scope="module")
def updated_project(tmp_path_factory):
    """A project adopted at release A (no standard), its gov pinned and updated to release B (which holds it)."""
    _built_standard()
    import w2_17_support as w217

    base = tmp_path_factory.mktemp("w2-213-update")
    sandbox = w217.make_sandbox(base / "sandbox")
    copier = w217.w216.require_copier()
    repo = Path(w217.w216.build_gov_os_repository(base / "gov-os"))
    kit = repo / support.STANDARD_REL
    assert kit.is_file(), "fixture: the stand-in Gov OS repository has no standard"
    kept = kit.read_bytes()
    kit.unlink()
    w217._set_version(repo, w217.A)
    w217.commit_all(repo, "release A's template, without the standard")
    w217.w216.build_release(repo, sandbox, w217.A, tag=w217.TAG_A)
    kit.write_bytes(kept)
    w217._set_version(repo, w217.B)
    w217.commit_all(repo, "release B's template, with the standard")
    w217.w216.build_release(repo, sandbox, w217.B, tag=w217.TAG_B)
    project = w217.adopt(copier, repo, base / "product", sandbox, tag=w217.TAG_A, local_changes=False)
    assert not (project / support.KIT_COPY).exists(), "fixture: the project at A already holds the standard"
    run = w217.update(project, sandbox)
    return Adopted(project, sandbox, w217, run)


def test_sl4_an_update_brings_the_standard_into_the_project_and_its_lock(updated_project):
    run, project = updated_project.update, updated_project.project
    assert run.returncode == 0, f"`gov update` to the release holding the standard failed\n{run.describe()}"
    copy_in_project = project / support.KIT_COPY
    assert copy_in_project.is_file(), f"the updated project lacks {support.KIT_COPY}"
    assert copy_in_project.read_bytes() == support.STANDARD.read_bytes(), "the project's copy differs from the kit's"
    lock = support.load_yaml(project / "governance/framework.lock")
    listed = (lock.get("manifest") or {}).get(support.KIT_COPY)
    assert listed == hashlib.sha256(copy_in_project.read_bytes()).hexdigest(), (
        f"framework.lock does not list {support.KIT_COPY} with its sha256: {listed!r}")


def test_sl4_a_changed_copy_in_the_project_is_lock_drift_in_gov_doctor(updated_project, tmp_path):
    harness = updated_project.harness
    assert updated_project.update.returncode == 0, f"`gov update` failed\n{updated_project.update.describe()}"
    project = harness.copy_project(updated_project.project, tmp_path / "product")
    path = project / support.KIT_COPY
    assert path.is_file(), f"the updated project lacks {support.KIT_COPY}"
    sandbox = harness.make_sandbox(tmp_path / "sandbox")

    def lock_part():
        run = harness.gov(project, sandbox, "doctor", "--json")
        part = harness.doctor_report(run).get("framework_lock") or {}
        return run, part

    run, part = lock_part()
    assert support.KIT_COPY not in (part.get("drifted_files") or []), f"drift before any edit\n{run.describe()}"
    path.write_bytes(path.read_bytes() + b"# planted edit\n")
    run, part = lock_part()
    assert part.get("match") == "DRIFT" and support.KIT_COPY in (part.get("drifted_files") or []), (
        f"gov doctor does not report lock drift for the changed standard: {part!r}\n{run.describe()}")


def test_sl4_the_installed_release_checks_a_repository_without_the_kits_copy(updated_project, clean_repo, tmp_path):
    """The gov pinned from release B's wheel (no source tree, no ``PYTHONPATH``) finds its packaged standard."""
    harness = updated_project.harness
    assert updated_project.update.returncode == 0, f"`gov update` failed\n{updated_project.update.describe()}"
    root, lines = _repo_without_the_kits_copy(clean_repo, tmp_path / "meadow")
    plan, _ = support.write_plan(tmp_path / "plan.jsonl", lines)
    binary = harness.common_dir(updated_project.project) / "gov" / "bin" / "gov"
    assert binary.exists(), f"no pinned gov at {binary}"
    sandbox = harness.make_sandbox(tmp_path / "sandbox")
    run = harness._run((binary, "layout", "check", plan, "--root", root, "--json"), updated_project.project,
                       harness.environment(sandbox, with_src=False))
    data = run.envelope()
    result = data.get("result") or {}
    assert run.returncode == 0 and data.get("ok") is True and result.get("findings") == [], (
        f"the installed release's check did not run clean\n{run.describe()}")
    assert result.get("standard") == _built_standard()["version"], f"another standard was read\n{run.describe()}"


def test_sl4_the_source_tree_checks_a_repository_without_the_kits_copy(clean_repo, tmp_path, work):
    root, lines = _repo_without_the_kits_copy(clean_repo, tmp_path / "meadow")
    run, _ = support.check_lines(work, root, lines)
    result = support.assert_clean(run)
    assert result["standard"] == _built_standard()["version"], f"another standard was read\n{run.describe()}"


def test_sl4_the_check_reads_the_shipped_file_not_a_standard_of_its_own(clean_repo, tmp_path, work):
    """An installed copy whose shipped standard states version 2: the check reports version 2."""
    version = _built_standard()["version"]
    site = _installed_copy(tmp_path / "site")
    shipped = site / "gov/_shipped" / support.STANDARD_REL
    assert shipped.is_file(), f"the package ships no standard: {shipped}"
    text = shipped.read_text(encoding="utf-8")
    changed = text.replace(f"version: {version}", f"version: {version + 1}", 1)
    assert changed != text, "fixture: the shipped standard has no `version:` line"
    shipped.write_text(changed, encoding="utf-8")
    root, lines = _repo_without_the_kits_copy(clean_repo, tmp_path / "meadow")
    run, _ = support.check_lines(work, root, lines, src=site)
    assert support.assert_clean(run)["standard"] == version + 1, f"the shipped file was not read\n{run.describe()}"


def test_sl4_with_every_shipped_copy_absent_the_check_refuses_naming_the_file(clean_repo, tmp_path, work):
    _built_standard()
    site = _installed_copy(tmp_path / "site")
    shipped = site / "gov/_shipped" / support.STANDARD_REL
    assert shipped.is_file(), f"the package ships no standard: {shipped}"
    shipped.unlink()
    root, lines = _repo_without_the_kits_copy(clean_repo, tmp_path / "meadow")
    before = support.snapshot(root)
    run, _ = support.check_lines(work, root, lines, src=site)
    error = support.assert_cannot_run(run)
    assert "standard.yaml" in str(error.get("message")), f"the refusal does not name the file\n{run.describe()}"
    support.assert_unchanged(before, support.snapshot(root))
