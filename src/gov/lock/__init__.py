"""``governance/framework.lock`` (W1-39): written at ``copier copy`` and ``copier update``, compared by ``gov doctor``.

The lock is one YAML map below a comment header: the template tag and commit, the reference to Copier's
answers file, and the sha256 manifest of every installed kernel file (DEC-023). ``compare`` is the one
comparison of a project with its lock (DEC-488): it never answers MATCH without having hashed.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import yaml

LOCK_REL = "governance/framework.lock"
KERNEL_REL = "governance/kernel"
ANSWERS_REL = ".copier-answers.yml"
# The lock's key, and the answers file's key it is compared with.
IDENTITY = (("template_tag", "_commit"), ("template_commit", "_template_commit"))

HEADER = """\
# governance/framework.lock -- written by `copier copy` and `copier update`; never edit it by hand.
# It records the kernel release this project holds and the sha256 of every file under governance/kernel/.
#
# Update procedure:
#   1. Never edit .copier-answers.yml by hand: Copier reads the installed release from it.
#   2. Commit your work, then run `copier update --trust` at the project root. It brings the new
#      governance/kernel/, writes this lock again, and never overwrites governance/project/.
#   3. Run the adapter generation step: rulesync generates .claude/, CLAUDE.md and AGENTS.md
#      from .rulesync/ (`copier copy` and `copier update` do not run it).
#   4. Run `gov doctor`: its framework_lock part compares this lock with the installed kernel
#      and with .copier-answers.yml.
"""


class LockError(Exception):
    """The lock cannot be written."""


@dataclass(frozen=True)
class Comparison:
    verdict: str            # "MATCH", "DRIFT", "MISSING" (no lock) or "ERROR" (could not compare)
    drifted_files: tuple    # paths relative to the project root; empty unless the verdict is "DRIFT"
    reason: str | None      # why it is not a match, where files alone do not say


def _read_map(path: Path) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) else None


def _kernel_files(root: Path) -> tuple[list[str], list[str]]:
    """Every file under ``governance/kernel/``, git-ignored or not, and the folders that could not be listed.

    Only ``__pycache__/`` folders are left out. A folder that cannot be listed is returned by name with the
    system's reason: its files were not seen, so the caller must not answer for them.
    """
    found, unlisted = [], []

    def refused(error: OSError) -> None:
        unlisted.append(f"{Path(error.filename).relative_to(root).as_posix()} ({error.strerror})")

    for folder, folders, files in os.walk(root / KERNEL_REL, onerror=refused):
        folders[:] = [name for name in folders if name != "__pycache__"]
        links = [name for name in folders if os.path.islink(os.path.join(folder, name))]
        found.extend((Path(folder) / name).relative_to(root).as_posix() for name in files + links)
    return sorted(found), sorted(unlisted)


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def compare(root: Path) -> Comparison:
    """Compare the project at ``root`` with its lock: match or drift, the drifted files, the reason."""
    root = Path(root)
    if not (root / LOCK_REL).is_file():
        return Comparison("MISSING", (), "no framework.lock")
    lock = _read_map(root / LOCK_REL)
    if lock is None:
        return Comparison("ERROR", (), "framework.lock is not a readable map")
    manifest = lock.get("manifest")
    if not isinstance(manifest, dict) or not manifest:
        return Comparison("ERROR", (), "framework.lock has no manifest entries")
    answers = _read_map(root / ANSWERS_REL)
    if answers is None:
        return Comparison("ERROR", (), f"{ANSWERS_REL} is absent or not a readable map")
    differing = []
    for lock_key, answers_key in IDENTITY:
        locked, installed = lock.get(lock_key), answers.get(answers_key)
        if not (isinstance(locked, str) and locked and isinstance(installed, str) and installed):
            return Comparison("ERROR", (), f"framework.lock lacks {lock_key} or {ANSWERS_REL} lacks {answers_key}")
        if locked != installed:
            differing.append(lock_key)
    drifted = set()
    for rel, recorded in manifest.items():
        actual = _sha256(root / str(rel))
        if actual is None or actual != recorded:
            drifted.add(str(rel))
    installed_files, unlisted = _kernel_files(root)
    if unlisted:
        return Comparison("ERROR", (), f"cannot list the kernel folders {unlisted}: their files were not compared")
    if not any(rel in manifest for rel in installed_files):
        return Comparison("ERROR", (), f"no installed file under {KERNEL_REL}/ is listed in the manifest: "
                                       "nothing of the kernel was hashed")
    drifted.update(rel for rel in installed_files if rel not in manifest)
    if drifted or differing:
        reason = f"{' and '.join(differing)} of framework.lock differ from {ANSWERS_REL}" if differing else None
        return Comparison("DRIFT", tuple(sorted(drifted)), reason)
    return Comparison("MATCH", (), None)


def write(root: Path) -> Path:
    """Write the lock of the project at ``root`` from its answers file and its installed kernel."""
    root = Path(root)
    answers = _read_map(root / ANSWERS_REL)
    if answers is None:
        raise LockError(f"{ANSWERS_REL} is absent or not a readable map")
    lock = {}
    for lock_key, answers_key in IDENTITY:
        value = answers.get(answers_key)
        if not (isinstance(value, str) and value):
            raise LockError(f"{ANSWERS_REL} lacks {answers_key}")
        lock[lock_key] = value
    lock["answers_file"] = ANSWERS_REL
    installed_files, unlisted = _kernel_files(root)
    if unlisted:
        raise LockError(f"cannot list the kernel folders {unlisted}")
    lock["manifest"] = {rel: _sha256(root / rel) for rel in installed_files}
    unreadable = sorted(rel for rel, digest in lock["manifest"].items() if digest is None)
    if unreadable or not lock["manifest"]:
        raise LockError(f"cannot hash the kernel files {unreadable}" if unreadable else f"no file under {KERNEL_REL}/")
    path = root / LOCK_REL
    path.write_text(HEADER + yaml.safe_dump(lock, sort_keys=False), encoding="utf-8")
    return path
