"""KPI success 2 and 4 (the install side), the failure line through `copier copy` and `copier update`, W2-M175.

The install and update paths this tree has are `copier copy` and `copier update` of the template, whose task
writes the lock (W1-39); there is no `gov install` or `gov update` yet (W2-18, W2-17 build them on this
ticket). A refusal is a Copier run that exits non-zero because its task refused.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import w2_16_support as support


def _tag_is_unsigned(repo, tag):
    done = subprocess.run(["git", "-C", str(repo), "tag", "-v", tag], capture_output=True, text=True,
                          env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(repo),
                               "GIT_CONFIG_NOSYSTEM": "1"})
    return done.returncode != 0


# --------------------------------------------------------------------------
# KPI success 4: framework.lock records the release version and manifest hash, at copy and at update
# --------------------------------------------------------------------------

def test_a_project_copied_from_a_release_tag_records_the_release_version_in_its_lock(release_project, releases):
    scalars = support.lock_scalars(release_project)
    assert support.FIRST_VERSION in scalars, (
        f"the lock of a project copied from {support.FIRST_TAG} does not record the release version "
        f"{support.FIRST_VERSION}\n{support.lock_bytes(release_project).decode()[:3000]}")


def test_a_project_copied_from_a_release_tag_records_the_manifest_hash_in_its_lock(release_project, releases):
    assert releases.first.manifest_hash in support.lock_scalars(release_project), (
        f"the lock of a project copied from {support.FIRST_TAG} does not record the release's manifest hash "
        f"{releases.first.manifest_hash}\n{support.lock_bytes(release_project).decode()[:3000]}")


def test_a_project_updated_to_a_later_release_records_that_release_in_its_lock(updated_project, releases):
    scalars = support.lock_scalars(updated_project)
    assert support.SECOND_VERSION in scalars and releases.second.manifest_hash in scalars, (
        f"after `copier update` to {support.SECOND_TAG} the lock does not record version {support.SECOND_VERSION} "
        f"and manifest hash {releases.second.manifest_hash}\n{support.lock_bytes(updated_project).decode()[:3000]}")
    assert releases.first.manifest_hash not in scalars, \
        "after the update the lock still records the first release's manifest hash"


@pytest.mark.parametrize("which", ("copied", "updated"))
def test_doctor_passes_on_a_project_installed_from_a_release(release_project, updated_project, sandbox, which):
    project = release_project if which == "copied" else updated_project
    result = support.doctor(project, sandbox)
    assert result.claims_match and result.section.get("status") == "pass" and not result.reports_drift, \
        f"gov doctor's lock part is not a measured MATCH on a project {which} from a release\n{result.describe()}"
    assert result.run.returncode == 0, f"gov doctor fails on a project {which} from a release\n{result.describe()}"


# --------------------------------------------------------------------------
# KPI success 2: a release installed from an unsigned tag is accepted
# --------------------------------------------------------------------------

def test_a_release_installed_from_an_unsigned_lightweight_tag_is_accepted(releases, release_project):
    assert _tag_is_unsigned(releases.repo, support.FIRST_TAG), "this case needs an unsigned tag"
    assert support.FIRST_VERSION in support.lock_scalars(release_project)


def test_a_release_installed_from_an_unsigned_annotated_tag_is_accepted(copier_bin, releases, release_repo,
                                                                       sandbox, tmp_path):
    support.git(release_repo, "tag", "-d", support.FIRST_TAG)
    support.git(release_repo, "tag", "-a", "-m", f"release {support.FIRST_VERSION}", support.FIRST_TAG,
                releases.first.release_commit)
    assert _tag_is_unsigned(release_repo, support.FIRST_TAG), "this case needs an unsigned tag"
    project = support.create_project(copier_bin, sandbox, release_repo, tmp_path / "product", support.FIRST_TAG)
    scalars = support.lock_scalars(project)
    assert support.FIRST_VERSION in scalars and releases.first.manifest_hash in scalars, \
        f"the lock of a project installed from an annotated unsigned tag does not record the release"


# --------------------------------------------------------------------------
# The failure line: a release whose files or manifest do not match their hashes is refused
# --------------------------------------------------------------------------

def _tamper(repo, record, tag, how):
    """Change the released commit as ``how`` says, commit it, and move the release's tag onto it.

    Returns the file name a refusal is to name.
    """
    support.git(repo, "checkout", "-q", "-B", "w2-16-tampered", tag)
    tampered = support.normalise_path(support.TAMPERED_REL)
    if how == "a shipped file changed":
        support.append_one_byte(repo / support.TAMPERED_REL)
        named = tampered
    elif how == "a file added":
        (repo / support.ADDED_REL).write_text("{}\n", encoding="utf-8")
        named = support.normalise_path(support.ADDED_REL)
    elif how == "a shipped file removed":
        (repo / support.TAMPERED_REL).unlink()
        named = tampered
    elif how == "the manifest's own hash wrong":
        changed = support.replace_in_record(repo, record, record.manifest_hash, support.OTHER_HASH)
        assert changed, "the record states no manifest hash to make wrong"
        named = "manifest"
    elif how == "a file hash in the manifest wrong":
        digest = support.shipped_files(repo, record.built_from)[tampered]
        manifest = repo / record.manifest_rel
        data = manifest.read_bytes()
        assert digest.encode() in data, f"the manifest does not give {tampered}'s sha256"
        manifest.write_bytes(data.replace(digest.encode(), support.OTHER_HASH.encode()))
        support.replace_in_record(repo, record, record.manifest_hash, support.sha256(manifest))
        named = tampered
    else:
        raise AssertionError(how)
    support.commit_all(repo, f"after the release: {how}")
    support.git(repo, "tag", "-f", tag)
    return named


def _assert_refused(done, named, why, project=None, manifest_hash=None):
    assert done.returncode != 0, f"Copier installed a release although {why}\n{support.copier_report(done)}"
    output = done.stdout + "\n" + done.stderr
    assert "Traceback" not in output, f"the refusal ({why}) ended in a traceback\n{support.copier_report(done)}"
    assert named.rsplit("/", 1)[-1] in output, f"the refusal ({why}) does not name {named}\n{support.copier_report(done)}"
    if project is not None and manifest_hash is not None and (Path(project) / support.LOCK_REL).is_file():
        assert manifest_hash not in support.lock_bytes(project).decode("utf-8", "replace"), \
            f"after the refusal ({why}) the lock records the refused release"


TAMPERINGS = ("a shipped file changed", "a file added", "a shipped file removed", "the manifest's own hash wrong",
              "a file hash in the manifest wrong")


@pytest.mark.parametrize("how", TAMPERINGS)
def test_copier_copy_refuses_a_release_that_does_not_match_its_hashes(copier_bin, releases, release_project,
                                                                     release_repo, sandbox, tmp_path, how):
    """The first release's tag moved onto a commit where ``how``: the copy's task refuses. (`release_project`
    shows the same tag installs before the change.)"""
    named = _tamper(release_repo, releases.first, support.FIRST_TAG, how)
    destination = tmp_path / "product"
    done = support.copy(copier_bin, sandbox, release_repo, destination, support.FIRST_TAG)
    _assert_refused(done, named, f"after release {support.FIRST_VERSION}: {how}", destination,
                    releases.first.manifest_hash)


@pytest.mark.parametrize("how", ("a shipped file changed", "the manifest's own hash wrong"))
def test_copier_update_refuses_a_release_that_does_not_match_its_hashes(copier_bin, releases, updated_project,
                                                                       release_repo, sandbox, tmp_path, how):
    """A project of the first release; the second release's tag moved onto a commit where ``how``: the update's
    task refuses and the lock does not record the second release. (`updated_project` shows the update before.)"""
    project = support.create_project(copier_bin, sandbox, release_repo, tmp_path / "product", support.FIRST_TAG)
    named = _tamper(release_repo, releases.second, support.SECOND_TAG, how)
    done = support.update(copier_bin, sandbox, project, support.SECOND_TAG)
    _assert_refused(done, named, f"after release {support.SECOND_VERSION}: {how}", project,
                    releases.second.manifest_hash)


# --------------------------------------------------------------------------
# W2-M175: the lock task needs no python3 on PATH that imports gov
# --------------------------------------------------------------------------

def _source_for(kind, request):
    if kind == "plain template source":
        return request.getfixturevalue("plain_source"), support.PLAIN_TAG
    return request.getfixturevalue("releases").repo, support.FIRST_TAG


@pytest.mark.parametrize("kind", ("plain template source", "release"))
def test_the_lock_task_runs_where_python3_does_not_import_gov(copier_bin, sandbox, tmp_path, request, kind):
    """`gov` installed as an isolated tool: on PATH it runs, while the python3 on PATH (and every interpreter
    without PYTHONPATH) cannot import gov. The copy succeeds and writes the lock (W2-M175, DEC-499 P-D)."""
    source, ref = _source_for(kind, request)
    env = support.copier_environment(sandbox, python_without_gov=True)
    probe = subprocess.run(["python3", "-c", "import gov"], env=env, capture_output=True, text=True)
    assert probe.returncode != 0, "this case needs a python3 on PATH that cannot import gov"
    shown = subprocess.run(["gov"], env={**env, "W2_16_SHOW_GOV": "1"}, capture_output=True, text=True)
    assert shown.returncode == 0 and shown.stdout.strip().startswith(str(support.SRC)), \
        f"this case needs the gov on PATH to be this worktree's: {shown.stdout} {shown.stderr}"
    destination = tmp_path / "product"
    done = support.copy(copier_bin, sandbox, source, destination, ref, python_without_gov=True)
    assert done.returncode == 0, (
        f"`copier copy` fails where gov is an isolated tool and python3 does not import it: the lock task "
        f"still needs python3 (W2-M175)\n{support.copier_report(done)}")
    assert support.lock_bytes(destination) is not None and support.lock_data(destination).get(support.MANIFEST_KEY), \
        f"the copy wrote no {support.LOCK_REL} with a manifest"


# --------------------------------------------------------------------------
# Guard: the suite runs this worktree's code
# --------------------------------------------------------------------------

def test_every_gov_the_suite_runs_is_this_worktree_s(sandbox):
    """`gov release` (sys.executable -m gov.cli.main), the gov a Copier task finds, and a task's python3."""
    env = support.gov_environment(sandbox)
    direct = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env,
                            capture_output=True, text=True)
    copier_env = support.copier_environment(sandbox)
    task_python = subprocess.run(["python3", "-c", "import gov; print(gov.__file__)"], env=copier_env,
                                 capture_output=True, text=True)
    task_gov = subprocess.run(["gov"], env={**copier_env, "W2_16_SHOW_GOV": "1"}, capture_output=True, text=True)
    for name, done in (("gov release", direct), ("a task's python3", task_python), ("a task's gov", task_gov)):
        assert done.returncode == 0 and done.stdout.strip().startswith(str(support.SRC)), \
            f"{name} does not import this worktree's gov: {done.stdout!r} {done.stderr!r}"
