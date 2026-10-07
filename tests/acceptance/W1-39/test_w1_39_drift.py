"""KPI success 2 [CAP-02.a]: editing one kernel file makes doctor report DRIFT naming it.

And the rule that a result is measured or it is refused (DEC-449, DEC-454):
the lock part of ``gov doctor`` never says MATCH, and never counts as passed,
without having hashed the files the installed kernel holds. DEC-488 makes it
exact: an absent or empty manifest is not a match; a kernel file the manifest
does not list is drift, named, whether or not git ignores it; only what lies
in a ``__pycache__/`` folder is left out. ``gov doctor`` reports that
comparison's answer (DEC-493).

Every case changes a project created by ``copier copy`` in a temporary folder
and runs ``gov doctor --json`` there.
"""

from __future__ import annotations

import os

import pytest

import w1_39_support as support


def _a_kernel_file(project, below):
    files = [rel for rel in support.kernel_files(project) if rel.startswith(f"{support.KERNEL_REL}/{below}/")]
    assert files, f"the project has no kernel file under {support.KERNEL_REL}/{below}/"
    return files[0]


def _append_one_byte(path):
    with open(path, "ab") as handle:
        handle.write(b"\n")


# --------------------------------------------------------------------------
# The KPI line: a one-byte edit
# --------------------------------------------------------------------------

@pytest.mark.parametrize("below", ("hooks", "skills"))
def test_a_one_byte_edit_of_a_kernel_file_is_drift_naming_it(project, sandbox, below):
    """One byte appended to one kernel file: DRIFT, the file named, doctor unhealthy."""
    rel = _a_kernel_file(project, below)
    _append_one_byte(project / rel)
    result = support.doctor(project, sandbox)
    support.assert_drift_naming(result, rel, f"one byte was appended to {rel}")


def test_drift_names_the_edited_file_and_no_other(project, sandbox):
    """The report names the file that was edited, not a kernel file that was left alone."""
    files = support.kernel_files(project)
    edited, untouched = files[0], files[-1]
    assert edited != untouched
    _append_one_byte(project / edited)
    result = support.doctor(project, sandbox)
    support.assert_drift_naming(result, edited, f"one byte was appended to {edited}")
    assert not result.names(untouched), f"the drift report names {untouched}, which was not edited\n{result.describe()}"


def test_the_edit_taken_back_is_a_match_again(project, sandbox):
    """The verdict follows the bytes: the original content restored, doctor reports MATCH and passes."""
    rel = _a_kernel_file(project, "hooks")
    original = (project / rel).read_bytes()
    _append_one_byte(project / rel)
    support.assert_drift_naming(support.doctor(project, sandbox), rel, f"one byte was appended to {rel}")
    (project / rel).write_bytes(original)
    result = support.doctor(project, sandbox)
    assert result.claims_match and not result.reports_drift and result.run.returncode == 0, \
        f"gov doctor does not report MATCH once the edit is taken back\n{result.describe()}"


# --------------------------------------------------------------------------
# Measured or refused
# --------------------------------------------------------------------------

def test_a_listed_file_that_is_missing_is_reported_by_name(project, sandbox):
    """A kernel file the manifest lists and the project no longer holds is DRIFT naming it, not a file skipped."""
    rel = _a_kernel_file(project, "hooks")
    (project / rel).unlink()
    support.assert_drift_naming(support.doctor(project, sandbox), rel, f"{rel} was deleted")


def test_a_listed_file_that_cannot_be_read_is_reported_by_name(project, sandbox):
    """A kernel file that cannot be hashed is reported by name; the lock part is not a match."""
    rel = _a_kernel_file(project, "hooks")
    path = project / rel
    path.chmod(0)
    try:
        assert not os.access(path, os.R_OK), "this case needs a user for whom a file without permissions is unreadable"
        result = support.doctor(project, sandbox)
    finally:
        path.chmod(0o644)
    support.assert_not_a_match(result, f"{rel} cannot be read")
    assert result.names(rel) and result.run.returncode != 0, \
        f"gov doctor does not report the unreadable file {rel}\n{result.describe()}"


def test_a_kernel_file_the_manifest_does_not_list_is_drift_naming_it(project, sandbox):
    """A file added under the Copier-owned ``governance/kernel/`` is not part of the release: DRIFT naming it.

    CAP-43: doctor fails when the manifest disagrees with the installed kernel;
    ADR-0002 section 5: ``governance/kernel/`` is Copier-owned.
    """
    rel = f"{support.HOOKS_REL}/w1_39_added_by_hand.py"
    (project / rel).write_text("print('not part of any release')\n", encoding="utf-8")
    support.commit_all(project, "a file added to the kernel by hand")
    support.assert_drift_naming(support.doctor(project, sandbox), rel, f"{rel} is in the kernel and not in the manifest")


def test_a_kernel_file_hidden_from_git_by_an_ignore_rule_is_still_drift_naming_it(project, sandbox):
    """An ignore rule is the project's to write: a kernel file it hides from git does not escape the comparison.

    DEC-488: git-ignored files in general are not left out of "a kernel file the manifest does not list".
    """
    rel = f"{support.HOOKS_REL}/w1_39_hidden_by_an_ignore_rule.py"
    with open(project / support.IGNORE_REL, "a", encoding="utf-8") as handle:
        handle.write(f"\n/{rel}\n")
    support.commit_all(project, "an ignore rule of the project")
    (project / rel).write_text("print('not part of any release')\n", encoding="utf-8")
    assert support.is_ignored(project, rel) and rel not in support.untracked(project), \
        f"this case needs {rel} hidden from git by the project's ignore rule"
    support.assert_drift_naming(support.doctor(project, sandbox), rel,
                                f"{rel} is in the kernel, not in the manifest, and only hidden from git")


def test_a_file_in_a_bytecode_folder_inside_the_kernel_is_not_drift(project, sandbox):
    """Only ``__pycache__/`` folders are left out (DEC-488): what Python writes beside a hook it ran is not drift."""
    rels = (f"{support.HOOKS_REL}/{support.PYCACHE}/w1_39_hook.cpython-312.pyc",
            f"{support.KERNEL_REL}/{support.PYCACHE}/w1_39_top.cpython-312.pyc")
    for rel in rels:
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_bytes(b"\x00bytecode\n")
    result = support.doctor(project, sandbox)
    named = [rel for rel in rels if result.names(rel)]
    assert result.claims_match and result.section.get("status") == "pass" and not result.reports_drift and not named, \
        f"gov doctor reports files of a {support.PYCACHE}/ folder inside the kernel against the lock\n{result.describe()}"


def test_a_kernel_file_struck_from_the_manifest_is_drift_naming_it(project, sandbox):
    """The same from the other side: an installed kernel file whose manifest entry was removed is not passed over."""
    rel = _a_kernel_file(project, "hooks")
    support.rewrite_lock(project, lambda lock: lock[support.MANIFEST_KEY].pop(rel))
    support.assert_drift_naming(support.doctor(project, sandbox), rel, f"{rel} was struck from the manifest")


@pytest.mark.parametrize("rel", ("governance/project/notes.md", "src/app.py", ".tickets/DAEO-zz01.md"))
def test_a_file_the_project_adds_outside_the_kernel_is_not_drift(project, sandbox, rel):
    """A project's own file is told from a kernel file by its place: outside ``governance/kernel/`` it is not drift."""
    path = project / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("the project's own\n", encoding="utf-8")
    support.commit_all(project, "the project's own file")
    result = support.doctor(project, sandbox)
    assert result.claims_match and not result.reports_drift and not result.names(rel), \
        f"gov doctor reports the project's own file {rel} against the lock\n{result.describe()}"


def test_a_missing_lock_is_not_a_match(project, sandbox):
    """A project installed by Copier whose lock was removed: nothing was hashed, so nothing matches.

    Whether doctor must also fail there is not decided by a source, and is not asserted.
    """
    support.lock_path(project).unlink()
    support.assert_not_a_match(support.doctor(project, sandbox), f"{support.LOCK_REL} was removed")


@pytest.mark.parametrize("how", ("empty", "absent"))
def test_a_lock_without_manifest_entries_is_not_a_match(project, sandbox, how):
    """An empty manifest, or none, hashes no file: the lock part fails, it does not pass by default."""
    def change(lock):
        if how == "empty":
            lock[support.MANIFEST_KEY] = {}
        else:
            del lock[support.MANIFEST_KEY]

    support.manifest_of(project)
    support.rewrite_lock(project, change)
    result = support.doctor(project, sandbox)
    support.assert_not_a_match(result, f"the manifest of {support.LOCK_REL} is {how}")
    assert result.run.returncode != 0, \
        f"gov doctor exits 0 on a lock whose manifest is {how}\n{result.describe()}"


def test_a_lock_that_is_not_readable_as_a_map_is_not_a_match(project, sandbox):
    """A lock that cannot be read fails the lock part."""
    support.lock_text(project)
    support.lock_path(project).write_text("- this\n- is: not a lock\n", encoding="utf-8")
    result = support.doctor(project, sandbox)
    support.assert_not_a_match(result, f"{support.LOCK_REL} is not a map")
    assert result.run.returncode != 0, f"gov doctor exits 0 on a lock that is not a map\n{result.describe()}"
