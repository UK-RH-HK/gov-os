"""``governance/framework.lock`` (W1-39): written at ``copier copy`` and ``copier update``, compared by ``gov doctor``.

The lock is one YAML map below a comment header: the template tag and commit, the reference to Copier's
answers file, the sha256 manifest of every installed file under the shipped paths (``governance/kernel/`` and
the declared paths outside it, W2-M174), the executable files and the folders there, and, for a project
installed from a release (W2-16), the release's version, its manifest's sha256 and the manifest itself; without a
release the lock states ``release: null``, and a lock that does not state its release fails (DEC-761).
``compare`` is the one comparison of a project with its lock (DEC-488): it never answers MATCH without having
hashed.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

import yaml

from gov.util.digest import sha256_file

LOCK_REL = "governance/framework.lock"
KERNEL_REL = "governance/kernel"
ANSWERS_REL = ".copier-answers.yml"
# The paths a release ships and the lock compares: the kernel, and the framework's paths outside it (W2-M174).
# The overlay (governance/project/) is the project's and is never one of them (ADR-0002 section 5).
SHIPPED_PATHS = (KERNEL_REL, "openspec/schemas/feature-readiness")
# The lock's key, and the answers file's key it is compared with.
IDENTITY = (("template_tag", "_commit"), ("template_commit", "_template_commit"))

HEADER = """\
# governance/framework.lock -- written by `copier copy` and `copier update`; never edit it by hand.
# It records the kernel release this project holds, and the sha256, the executable bit and the folders of
# every file under governance/kernel/ and the other shipped paths it names.
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
    # "MATCH", "DRIFT", "ERROR" (could not compare), "UNLOCKED" (an installed project without its lock:
    # an answers file or an installed kernel and no lock, DEC-499, W2-H029) or "MISSING" (none of them:
    # never installed from the template)
    verdict: str
    drifted_files: tuple    # paths relative to the project root; empty unless the verdict is "DRIFT"
    reason: str | None      # why it is not a match, where files alone do not say


def _present(path: Path) -> bool:
    """Whether anything has this name: a file, a folder or a link, readable or not (DEC-499).

    Only a name the system reports as absent is absent; a name that cannot be looked at counts as present,
    so that an installed project is never taken for one that was never installed.
    """
    try:
        os.lstat(path)
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError:
        return True
    return True


def _read_map(path: Path) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) else None


def _shipped(root: Path) -> tuple[list[str], list[str], list[str]]:
    """Every file and every folder under the shipped paths, git-ignored or not, and the folders that could
    not be listed.

    Only ``__pycache__/`` folders are left out. A folder that cannot be listed is returned by name with the
    system's reason: its files were not seen, so the caller must not answer for them. A declared path outside
    the kernel that is absent is walked no further (its locked files are then missing); the kernel always is.
    """
    found, folders, unlisted = [], [], []

    def refused(error: OSError) -> None:
        unlisted.append(f"{Path(error.filename).relative_to(root).as_posix()} ({error.strerror})")

    for shipped in SHIPPED_PATHS:
        if shipped != KERNEL_REL and not _present(root / shipped):
            continue
        for folder, names, files in os.walk(root / shipped, onerror=refused):
            names[:] = [name for name in names if name != "__pycache__"]
            links = [name for name in names if os.path.islink(os.path.join(folder, name))]
            folders.append(Path(folder).relative_to(root).as_posix())
            found.extend((Path(folder) / name).relative_to(root).as_posix() for name in files + links)
    return sorted(found), sorted(folders), sorted(unlisted)


def _is_shipped(rel: str) -> bool:
    return any(rel == path or rel.startswith(path + "/") for path in SHIPPED_PATHS)


def _executable(path: Path) -> bool | None:
    try:
        return bool(os.stat(path).st_mode & stat.S_IXUSR)
    except OSError:
        return None


def released_files(release) -> tuple[dict | None, str | None]:
    """The files of the release the lock records, ``{path: sha256}``, or why they cannot be trusted (W2-16).

    The lock holds the release manifest's bytes (base64) beside their sha256: the bytes must hash to it and
    name the recorded version, or nothing of the release is believed.
    """
    if not isinstance(release, dict):
        return None, "the release in framework.lock is not a map"
    version, digest = release.get("version"), release.get("manifest_sha256")
    try:
        data = base64.b64decode(release.get("manifest"), validate=True)
    except (TypeError, ValueError, binascii.Error):
        return None, "the release manifest in framework.lock cannot be read"
    if not isinstance(digest, str) or hashlib.sha256(data).hexdigest() != digest:
        return None, f"the release manifest in framework.lock does not hash to its manifest_sha256 {digest}"
    try:
        manifest = json.loads(data)
    except ValueError:
        return None, "the release manifest in framework.lock is not JSON"
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(version, str) or manifest.get("version") != version or not isinstance(files, dict):
        return None, f"the release manifest in framework.lock is not that of release {version} with its files"
    return {str(rel): value for rel, value in files.items()}, None


def compare(root: Path) -> Comparison:
    """Compare the project at ``root`` with its lock: match or drift, the drifted files, the reason."""
    root = Path(root)
    if not os.path.isfile(root / LOCK_REL):
        if _present(root / LOCK_REL):
            return Comparison("ERROR", (), "framework.lock is not a file that can be read")
        if _present(root / ANSWERS_REL):
            return Comparison("UNLOCKED", (), f"framework.lock is missing from an installed project "
                                              f"({ANSWERS_REL} exists): nothing of the kernel was compared")
        if _present(root / KERNEL_REL):
            return Comparison("UNLOCKED", (), f"framework.lock and {ANSWERS_REL} are missing, and {KERNEL_REL}/ "
                                              "is installed: install it with `copier copy` (its task writes "
                                              "framework.lock); nothing of the kernel was compared")
        return Comparison("MISSING", (), "no framework.lock")
    lock = _read_map(root / LOCK_REL)
    if lock is None:
        return Comparison("ERROR", (), "framework.lock is not a readable map")
    manifest = lock.get("manifest")
    if not isinstance(manifest, dict) or not manifest:
        return Comparison("ERROR", (), "framework.lock has no manifest entries")
    executables, folders = lock.get("executables"), lock.get("folders")
    if not isinstance(executables, list) or not isinstance(folders, list):
        return Comparison("ERROR", (), "framework.lock lacks executables or folders: modes and folders were not "
                                       "compared")
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
    if "release" not in lock:
        return Comparison("ERROR", (), "framework.lock does not state the release it holds (a release, or "
                                       "release: null for none): its release entries may have been deleted")
    released = None
    if lock["release"] is not None:
        released, why = released_files(lock["release"])
        if why:
            return Comparison("ERROR", (), why)
    installed_files, installed_folders, unlisted = _shipped(root)
    if unlisted:
        return Comparison("ERROR", (), f"cannot list the kernel folders {unlisted}: their files were not compared")
    if not any(rel in manifest for rel in installed_files if rel.startswith(KERNEL_REL + "/")):
        return Comparison("ERROR", (), f"no installed file under {KERNEL_REL}/ is listed in the manifest: "
                                       "nothing of the kernel was hashed")
    executable = {str(rel) for rel in executables}
    drifted = set()
    for rel, recorded in manifest.items():
        rel = str(rel)
        actual = sha256_file(root / rel)
        if actual is None or actual != recorded or _executable(root / rel) != (rel in executable):
            drifted.add(rel)
        if released is not None and _is_shipped(rel) and released.get(rel) != recorded:
            drifted.add(rel)
    drifted.update(rel for rel in installed_files if rel not in manifest)
    drifted.update(set(installed_folders) ^ {str(rel) for rel in folders})
    if released is not None:
        drifted.update(rel for rel in released if _is_shipped(rel) and rel not in manifest)
    if drifted or differing:
        reason = f"{' and '.join(differing)} of framework.lock differ from {ANSWERS_REL}" if differing else None
        return Comparison("DRIFT", tuple(sorted(drifted)), reason)
    return Comparison("MATCH", (), None)


def write(root: Path, release: tuple[str, bytes] | None = None) -> Path:
    """Write the lock of the project at ``root`` from its answers file and its installed shipped paths.

    ``release`` is ``(version, manifest bytes)`` of a release already verified (``gov.release.verify``).
    """
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
    installed_files, installed_folders, unlisted = _shipped(root)
    if unlisted:
        raise LockError(f"cannot list the kernel folders {unlisted}")
    lock["release"] = None  # stated even without a release: a lock without the key is refused (DEC-761)
    if release is not None:
        version, data = release
        lock["release"] = {"version": version, "manifest_sha256": hashlib.sha256(data).hexdigest(),
                           "manifest": base64.b64encode(data).decode("ascii")}
    lock["shipped_paths"] = list(SHIPPED_PATHS)
    lock["manifest"] = {rel: sha256_file(root / rel) for rel in installed_files}
    unreadable = sorted(rel for rel, digest in lock["manifest"].items() if digest is None)
    if unreadable or not any(rel.startswith(KERNEL_REL + "/") for rel in installed_files):
        raise LockError(f"cannot hash the kernel files {unreadable}" if unreadable else f"no file under {KERNEL_REL}/")
    lock["executables"] = [rel for rel in installed_files if _executable(root / rel)]
    lock["folders"] = installed_folders
    path = root / LOCK_REL
    path.write_text(HEADER + yaml.safe_dump(lock, sort_keys=False), encoding="utf-8")
    return path
