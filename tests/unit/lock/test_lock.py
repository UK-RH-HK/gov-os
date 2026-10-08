"""Unit tests for gov.lock (DEC-135: regression evidence). Every project is built from scratch in tmp_path."""

from __future__ import annotations

import hashlib
import os

import pytest
import yaml

from gov.lock import ANSWERS_REL, HEADER, KERNEL_REL, LOCK_REL, LockError, compare, write

HOOK = f"{KERNEL_REL}/hooks/guard.py"
COMMIT = "a" * 40


def _project(root):
    for rel, text in ((HOOK, "print('hook')\n"), (f"{KERNEL_REL}/settings.json", "{}\n")):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    (root / ANSWERS_REL).write_text(f"_commit: v0.1.0\n_src_path: /elsewhere\n_template_commit: \"{COMMIT}\"\n",
                                    encoding="utf-8")
    write(root)
    return root


def _rewrite(root, change):
    lock = yaml.safe_load((root / LOCK_REL).read_text(encoding="utf-8"))
    change(lock)
    (root / LOCK_REL).write_text(yaml.safe_dump(lock), encoding="utf-8")


def test_write_gives_header_identity_answers_reference_and_manifest(tmp_path):
    root = _project(tmp_path)
    text = (root / LOCK_REL).read_text(encoding="utf-8")
    assert text.startswith(HEADER)
    lock = yaml.safe_load(text)
    assert lock["template_tag"] == "v0.1.0" and lock["template_commit"] == COMMIT
    assert lock["answers_file"] == ANSWERS_REL
    assert sorted(lock["manifest"]) == [HOOK, f"{KERNEL_REL}/settings.json"]
    assert compare(root) == compare(root).__class__("MATCH", (), None)


def test_write_refuses_without_the_commit_or_without_a_kernel(tmp_path):
    root = _project(tmp_path)
    (root / ANSWERS_REL).write_text("_commit: v0.1.0\n", encoding="utf-8")
    with pytest.raises(LockError):
        write(root)
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / ANSWERS_REL).write_text(f"_commit: v0.1.0\n_template_commit: \"{COMMIT}\"\n", encoding="utf-8")
    with pytest.raises(LockError):
        write(empty)


def test_no_lock_is_missing(tmp_path):
    answer = compare(tmp_path)
    assert (answer.verdict, answer.reason) == ("MISSING", "no framework.lock")


def test_no_lock_beside_an_answers_file_is_unlocked_and_names_the_lock(tmp_path):
    root = _project(tmp_path)
    (root / HOOK).write_text("print('edited')\n", encoding="utf-8")
    (root / LOCK_REL).unlink()
    answer = compare(root)
    assert answer.verdict == "UNLOCKED" and answer.drifted_files == ()
    assert "framework.lock" in answer.reason and ANSWERS_REL in answer.reason
    (root / ANSWERS_REL).unlink()
    assert compare(root).verdict == "MISSING"


@pytest.mark.parametrize("answers", ("empty", "not a map", "folder", "dangling link"))
def test_no_lock_beside_any_entry_named_as_the_answers_file_is_unlocked(tmp_path, answers):
    path = tmp_path / ANSWERS_REL
    if answers == "folder":
        path.mkdir()
    elif answers == "dangling link":
        path.symlink_to(tmp_path / "nowhere")
    else:
        path.write_text("" if answers == "empty" else "- not a map\n", encoding="utf-8")
    assert compare(tmp_path).verdict == "UNLOCKED"


@pytest.mark.parametrize("lock", ("folder", "dangling link"))
def test_a_lock_that_is_no_file_is_an_error_with_or_without_an_answers_file(tmp_path, lock):
    path = tmp_path / LOCK_REL
    path.parent.mkdir()
    if lock == "folder":
        path.mkdir()
    else:
        path.symlink_to(tmp_path / "nowhere")
    assert compare(tmp_path).verdict == "ERROR"
    (tmp_path / ANSWERS_REL).write_text("_commit: v0.1.0\n", encoding="utf-8")
    answer = compare(tmp_path)
    assert answer.verdict == "ERROR" and "framework.lock" in answer.reason


def test_a_governance_folder_that_cannot_be_searched_is_not_taken_for_no_lock(tmp_path):
    root = _project(tmp_path)
    (root / ANSWERS_REL).unlink()
    (root / "governance").chmod(0)
    try:
        if os.access(root / "governance", os.X_OK):
            pytest.skip("permissions do not bind this user")
        assert compare(root).verdict == "ERROR"
    finally:
        (root / "governance").chmod(0o755)


def test_edited_missing_and_unreadable_files_are_named(tmp_path):
    root = _project(tmp_path)
    (root / HOOK).write_text("print('edited')\n", encoding="utf-8")
    assert compare(root).drifted_files == (HOOK,) and compare(root).verdict == "DRIFT"
    (root / HOOK).chmod(0)
    try:
        if not os.access(root / HOOK, os.R_OK):
            assert compare(root).drifted_files == (HOOK,)
    finally:
        (root / HOOK).chmod(0o644)
    (root / HOOK).unlink()
    assert compare(root).drifted_files == (HOOK,) and compare(root).verdict == "DRIFT"


def test_a_missing_file_listed_without_a_hash_is_drift(tmp_path):
    root = _project(tmp_path)
    (root / HOOK).unlink()
    _rewrite(root, lambda lock: lock["manifest"].update({HOOK: None}))
    assert compare(root).drifted_files == (HOOK,)


def test_unlisted_kernel_file_is_drift_and_pycache_is_not(tmp_path):
    root = _project(tmp_path)
    cache = root / KERNEL_REL / "hooks" / "__pycache__" / "guard.pyc"
    cache.parent.mkdir()
    cache.write_bytes(b"\0")
    (root / "src.py").write_text("x = 1\n", encoding="utf-8")
    assert compare(root).verdict == "MATCH"
    added = f"{KERNEL_REL}/hooks/added.py"
    (root / added).write_text("x = 1\n", encoding="utf-8")
    assert compare(root).drifted_files == (added,)


@pytest.mark.parametrize("mode", (0, 0o100))
def test_a_kernel_folder_that_cannot_be_listed_is_an_error_naming_it_and_no_lock_is_written(tmp_path, mode):
    root = _project(tmp_path)
    folder = root / KERNEL_REL / "closed"
    folder.mkdir()
    (folder / "added.py").write_text("x = 1\n", encoding="utf-8")
    before = (root / LOCK_REL).read_text(encoding="utf-8")
    folder.chmod(mode)
    try:
        try:
            os.listdir(folder)
            pytest.skip("permissions do not bind this user")
        except OSError:
            pass
        answer = compare(root)
        assert answer.verdict == "ERROR" and f"{KERNEL_REL}/closed" in answer.reason
        with pytest.raises(LockError, match="closed"):
            write(root)
    finally:
        folder.chmod(0o755)
    assert (root / LOCK_REL).read_text(encoding="utf-8") == before


def test_a_manifest_that_lists_no_installed_kernel_file_is_an_error(tmp_path):
    root = _project(tmp_path)
    (root / "other.txt").write_text("x\n", encoding="utf-8")
    digest = hashlib.sha256(b"x\n").hexdigest()
    _rewrite(root, lambda lock: lock.update(manifest={"other.txt": digest}))
    for rel in (HOOK, f"{KERNEL_REL}/settings.json"):
        (root / rel).unlink()
    assert compare(root).verdict == "ERROR"                 # a kernel folder with no file in it
    (root / KERNEL_REL / "hooks").rmdir()
    (root / KERNEL_REL).rmdir()
    answer = compare(root)                                  # no kernel folder at all
    assert answer.verdict == "ERROR" and KERNEL_REL in answer.reason


@pytest.mark.parametrize("change", (
    lambda lock: lock.update(manifest={}),
    lambda lock: lock.pop("manifest"),
    lambda lock: lock.pop("template_tag"),
    lambda lock: lock.pop("template_commit"),
))
def test_a_lock_without_manifest_or_identity_is_an_error(tmp_path, change):
    root = _project(tmp_path)
    _rewrite(root, change)
    answer = compare(root)
    assert answer.verdict == "ERROR" and answer.reason


def test_a_lock_that_is_not_a_map_is_an_error(tmp_path):
    root = _project(tmp_path)
    (root / LOCK_REL).write_text("- not a map\n", encoding="utf-8")
    assert compare(root).verdict == "ERROR"


@pytest.mark.parametrize("answers", (None, ": not yaml: [", "_commit: v0.1.0\n"))
def test_an_answers_file_absent_unreadable_or_without_the_commit_is_an_error(tmp_path, answers):
    root = _project(tmp_path)
    (root / ANSWERS_REL).unlink()
    if answers is not None:
        (root / ANSWERS_REL).write_text(answers, encoding="utf-8")
    assert compare(root).verdict == "ERROR"


@pytest.mark.parametrize("key, other", (("template_tag", "v9.9.9"), ("template_commit", "0" * 40)))
def test_identity_that_differs_from_the_answers_file_is_drift(tmp_path, key, other):
    root = _project(tmp_path)
    _rewrite(root, lambda lock: lock.update({key: other}))
    answer = compare(root)
    assert answer.verdict == "DRIFT" and key in answer.reason and answer.drifted_files == ()
