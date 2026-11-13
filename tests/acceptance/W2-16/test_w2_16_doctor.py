"""The failure line through `gov doctor`, and KPI success 4's rows: W2-H029 (silencing), W2-L227, W2-M174.

`gov doctor --json` runs with this worktree's code in a project made by `copier copy` in a temporary folder
(W1-39's reading of the report: the section `framework_lock`, the words MATCH and DRIFT, the exit code).
"""

from __future__ import annotations

import shutil
import stat

import pytest

import w2_16_support as support
import w1_39_support as w139

TAMPERED = support.normalise_path(support.TAMPERED_REL)   # governance/kernel/schemas/ticket.schema.json


def _project(request, kind):
    return request.getfixturevalue("own_release_project" if kind == "release" else "own_plain_project")


# --------------------------------------------------------------------------
# The failure line: gov doctor refuses an installed release that does not match its hashes
# --------------------------------------------------------------------------

def test_doctor_refuses_a_lock_whose_manifest_hash_is_wrong(releases, own_release_project, sandbox):
    """The release's manifest hash in the lock replaced by another: the lock part fails."""
    path = own_release_project / support.LOCK_REL
    text = path.read_text(encoding="utf-8")
    assert releases.first.manifest_hash in text, "this case needs the lock to record the manifest hash"
    path.write_text(text.replace(releases.first.manifest_hash, support.OTHER_HASH), encoding="utf-8")
    support.assert_lock_part_fails(support.doctor(own_release_project, sandbox),
                                   "the lock's manifest hash is not the release's")


def test_doctor_refuses_a_lock_whose_file_hash_is_wrong(own_release_project, sandbox):
    """One file's hash in the lock's manifest changed, the file not: DRIFT naming it (as W1-39 holds it)."""
    path = own_release_project / support.LOCK_REL
    digest = support.sha256(own_release_project / TAMPERED)
    text = path.read_text(encoding="utf-8")
    assert digest in text
    path.write_text(text.replace(digest, support.OTHER_HASH), encoding="utf-8")
    w139.assert_drift_naming(support.doctor(own_release_project, sandbox), TAMPERED,
                             f"the lock gives {TAMPERED} a hash that is not its sha256")


@pytest.mark.parametrize("how", ("changed", "added", "removed"))
def test_doctor_refuses_an_installed_release_file_changed_added_or_removed(own_release_project, sandbox, how):
    rel = TAMPERED
    if how == "changed":
        support.append_one_byte(own_release_project / rel)
    elif how == "added":
        rel = support.normalise_path(support.ADDED_REL)
        (own_release_project / rel).write_text("{}\n", encoding="utf-8")
    else:
        (own_release_project / rel).unlink()
    w139.assert_drift_naming(support.doctor(own_release_project, sandbox), rel,
                             f"{rel} was {how} after the release was installed")


# --------------------------------------------------------------------------
# W2-H029 (the silencing part): a project cannot silence the lock comparison
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ("plain template source", "release"))
def test_deleting_both_the_lock_and_the_answers_file_does_not_silence_the_comparison(request, sandbox, kind):
    """An installed kernel with neither file: today "unmeasured" and exit 0; it fails now."""
    project = _project(request, kind)
    (project / support.LOCK_REL).unlink()
    (project / support.ANSWERS_REL).unlink()
    support.commit_all(project, "both the lock and the answers file deleted")
    support.assert_lock_part_fails(support.doctor(project, sandbox),
                                   "an installed kernel has lost both its lock and its answers file")


def test_editing_the_lock_manifest_together_with_a_kernel_file_does_not_give_a_match(own_release_project, sandbox):
    """A kernel file edited and its hash in the lock's manifest edited to match: today a MATCH; it fails now."""
    project = own_release_project
    path = project / support.LOCK_REL
    old = support.sha256(project / TAMPERED)
    support.append_one_byte(project / TAMPERED)
    new = support.sha256(project / TAMPERED)
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"this case needs {TAMPERED}'s hash once in the lock"
    path.write_text(text.replace(old, new), encoding="utf-8")
    assert support.lock_data(project)[support.MANIFEST_KEY][TAMPERED] == new
    support.commit_all(project, "a kernel file and its hash in the lock edited together")
    support.assert_lock_part_fails(support.doctor(project, sandbox),
                                   f"{TAMPERED} and its entry in the lock's manifest were edited together")


# --------------------------------------------------------------------------
# W2-L227: any install path produces framework.lock, or gov doctor names the missing step
# --------------------------------------------------------------------------

def test_copying_template_directly_gives_a_lock_or_doctor_names_the_missing_step(plain_source, sandbox, tmp_path):
    """The files of template/ copied as they are (no Copier, so no task, DEC-654)."""
    project = tmp_path / "product"
    template = plain_source / support.TEMPLATE_REL
    for path in sorted(template.rglob("*")):
        if path.is_file():
            target = project / path.relative_to(template)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    support.git(project, "init", "-q", "-b", "main")
    support.commit_all(project, "template/ copied directly")
    result = support.doctor(project, sandbox)
    if (project / support.LOCK_REL).is_file():
        assert result.section.get("status") in ("pass", "fail"), \
            f"a copied template/ holds a lock, and doctor's lock part is not measured\n{result.describe()}"
        return
    support.assert_lock_part_fails(result, "template/ was copied directly and no framework.lock was written")
    text = result.text.lower()
    assert "framework.lock" in text and "copier" in text, (
        f"gov doctor does not name the missing step (the lock and the Copier install that writes it)\n"
        f"{result.describe()}")


# --------------------------------------------------------------------------
# W2-M174: the comparison covers file modes, folders and declared non-kernel paths
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rel, executable", (("governance/kernel/bin/tk", True),
                                              ("governance/kernel/hooks/stop.py", False)))
def test_a_kernel_file_whose_mode_changed_is_drift_naming_it(own_plain_project, sandbox, rel, executable):
    path = own_plain_project / rel
    assert w139.is_executable(path) is executable, f"this case needs {rel} {'' if executable else 'not '}executable"
    mode = stat.S_IMODE(path.stat().st_mode)
    path.chmod(mode & ~0o111 if executable else mode | 0o755)
    w139.assert_drift_naming(support.doctor(own_plain_project, sandbox), rel,
                             f"{rel} {'lost' if executable else 'gained'} its executable bit")


def test_an_empty_folder_added_to_the_kernel_is_drift_naming_it(own_plain_project, sandbox):
    rel = "governance/kernel/hooks/w2-16-empty-folder"
    (own_plain_project / rel).mkdir()
    w139.assert_drift_naming(support.doctor(own_plain_project, sandbox), rel,
                             f"an empty folder {rel} was added to the kernel")


def _declared_outside_the_kernel(project):
    names = support.lock_names(project)
    found = []
    for rel in support.files_of(project):
        if support.under(rel, support.KERNEL_REL) or support.under(rel, support.OVERLAY_REL) \
                or rel in (support.LOCK_REL, support.ANSWERS_REL):
            continue
        parts = rel.split("/")
        ancestors = {"/".join(parts[:i]) for i in range(1, len(parts))}
        if rel in names or ancestors & names or {a + "/" for a in ancestors} & names:
            found.append(rel)
    return found


def test_a_declared_shipped_path_outside_the_kernel_is_compared(own_plain_project, sandbox):
    """The lock declares at least one shipped path outside governance/kernel/ (the overlay never), and a one-byte
    edit there is DRIFT naming it."""
    declared = _declared_outside_the_kernel(own_plain_project)
    assert declared, (
        f"the lock declares no shipped path outside {support.KERNEL_REL}/ (W2-M174: the comparison covers declared "
        f"non-kernel paths)\n{support.lock_bytes(own_plain_project).decode()[:3000]}")
    rel = declared[0]
    support.append_one_byte(own_plain_project / rel)
    w139.assert_drift_naming(support.doctor(own_plain_project, sandbox), rel,
                             f"{rel}, a declared path outside the kernel, was edited")


def test_an_overlay_file_the_project_edits_is_still_not_drift(own_plain_project, sandbox):
    """Guard: the overlay is the project's (ADR-0002 section 5); declaring paths never reaches it."""
    path = own_plain_project / w139.PATH_MAP_REL
    path.write_text(w139.edited_by_the_project(path.read_text(encoding="utf-8")), encoding="utf-8")
    support.commit_all(own_plain_project, "the project edits its path map")
    result = support.doctor(own_plain_project, sandbox)
    assert result.claims_match and not result.reports_drift and not result.names(w139.PATH_MAP_REL), \
        f"gov doctor reports the project's edit of its overlay against the lock\n{result.describe()}"


# --------------------------------------------------------------------------
# Guard: a repository never installed from the template stays as W1-27 holds it (Wave 2 exit criterion 3)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("state", ("before any release", "holding releases"))
def test_the_gov_os_repository_itself_stays_unmeasured(request, sandbox, tmp_path, state):
    """The stand-in Gov OS repository (copier.yml, template/, src/, and docs/releases/ once it has releases) has no
    installed kernel: its lock part stays "unmeasured", not failed, as this repository's does."""
    origin = request.getfixturevalue("pristine_repo" if state == "before any release" else "releases")
    origin = origin if state == "before any release" else origin.repo
    repo = support.clone_folder(origin, tmp_path / "gov-os")
    result = support.doctor(repo, sandbox)
    assert result.section.get("status") == "unmeasured" and not result.claims_match and not result.reports_drift, (
        f"the lock part of gov doctor in a Gov OS repository {state} is not 'unmeasured'\n{result.describe()}")
