"""The pending-update report (W2-17 fix S5, CAP-45.b; DEC-1223 (6)): behind ``gov doctor``'s part ``updates`` and the
session start line.

Local reads only: the lock's held release, the source named by ``_src_path`` of ``.copier-answers.yml`` (relative to
the project), its tags ``v<X>`` and the records at them (``gov.release.verify_at``, manifest only), ``git`` on the
source. No network, no copier, nothing written. ``pending`` never raises: a read that fails is ``pending: false`` with
a ``reason``.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from gov import lock, release
from gov.update import core

PATCH_STEP = "at the next quiet point"
HELD_STEP = "held: rolled back here; waits for a newer release"


def _step_bigger(version: str) -> str:
    return f"bigger: the owner decides, gov update {version}"


def _key(version: str) -> tuple:
    return tuple(int(part) if part.isdigit() else 0 for part in re.split(r"[.\-+]", version))


def _git(src: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(src), *args], capture_output=True, text=True)


def _source(project: Path, source) -> Path | None:
    named = os.fspath(source) if source else (lock._read_map(project / lock.ANSWERS_REL) or {}).get("_src_path")
    if not isinstance(named, str) or not named:
        return None
    src = Path(named).expanduser()
    return src if src.is_absolute() else project / src


def _candidates(src: Path, held: str) -> list[str]:
    """The versions newer than ``held`` that have a tag ``v<X>`` and a verified record in ``src``, oldest first."""
    done = _git(src, "tag", "--list", "v*")
    if done.returncode:
        raise RuntimeError(f"{src} cannot be read as a git repository: {(done.stderr or done.stdout).strip()[:200]}")
    found = []
    for tag in done.stdout.split():
        version = tag[1:]
        if _key(version) <= _key(held):
            continue
        try:
            release.verify_at(src, version, files=False)
        except release.ReleaseError:
            continue
        found.append(version)
    return sorted(found, key=_key)


def _kind(src: Path, version: str) -> str:
    done = _git(src, "show", f"v{version}:{release.RELEASES_REL}/{version}/kind.json")
    if done.returncode:
        return "bigger"
    try:
        value = json.loads(done.stdout)
    except ValueError:
        return "bigger"
    return "patch" if isinstance(value, dict) and value.get("kind") == "patch" else "bigger"


def _fixes(src: Path, held: str, newest: str) -> int:
    done = _git(src, "log", "--no-merges", "--format=%B%x00", f"v{held}..v{newest}")
    if done.returncode:
        return 0
    return sum(1 for message in done.stdout.split("\0") if re.search(r"^Fix:", message, re.M))


def _burned() -> set[str]:
    """The releases marked burned in ``~/.local/share/gov-os/burned`` (W2-209): never a candidate."""
    from gov.release import repin

    return set(repin.burned(Path.home()))


def _none(held: str | None, reason: str) -> dict:
    summary = f"no update pending: {reason}"
    return {"status": "report", "held": held, "newest": None, "pending": False, "kind": None, "fixes": 0,
            "next": None, "summary": summary, "reason": reason}


def pending(project, source=None) -> dict:
    """The doctor part ``updates`` for the adopted project at ``project`` (``source`` replaces ``_src_path``)."""
    held = None
    try:
        project = Path(os.path.abspath(os.fspath(project)))
        try:
            held = core.held_release(project)
        except core.UpdateRefused as exc:
            return _none(None, f"no held release: {exc}")
        src = _source(project, source)
        if src is None:
            return _none(held, f"no source: {lock.ANSWERS_REL} names no _src_path")
        found = _candidates(src, held)
        if not found:
            return {**_none(held, f"no verified release newer than {held} in {src}"),
                    "summary": f"up to date ({held})"}
        burned = _burned()
        offered = [version for version in found if version not in burned]
        if not offered:  # W2-209 S9: a release whose post-pin check failed is never offered
            newest = found[-1]
            reason = f"release {newest} is burned (its post-pin check failed on this machine): never offered"
            return {**_none(held, reason), "pending": False, "burned": True, "newest": newest,
                    "summary": f"no update pending: {reason}"}
        newest = offered[-1]
        kind = _kind(src, newest)
        fixes = _fixes(src, held, newest)
        base = {"status": "report", "held": held, "newest": newest, "kind": kind, "fixes": fixes}
        if (project / core.UPDATES_REL / f"{newest}.rolled-back.json").is_file():
            return {**base, "pending": False, "rolled_back": True, "next": HELD_STEP,
                    "summary": f"release {newest} was rolled back here; held at {held} until a newer release"}
        step = PATCH_STEP if kind == "patch" else _step_bigger(newest)
        plural = "fix" if fixes == 1 else "fixes"
        return {**base, "pending": True, "next": step,
                "summary": f"update pending: holds {held}, {newest} is the newest ({kind}, {fixes} {plural}): {step}"}
    except Exception as exc:  # never raises: a read that fails is a reason
        return _none(held, f"the update report could not be read: {type(exc).__name__}: {exc}")
