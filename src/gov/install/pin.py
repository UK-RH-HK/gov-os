"""``gov install <version>`` (W2-18, DAEO-057v; CAP-43): the release's gov in the repository's own pinned environment.

Checks first, writing nothing: the tag ``v<version>`` in the source (``--source``, else ``_src_path`` of the
project's ``.copier-answers.yml``); at the tag, the record's manifest against its ``manifest.sha256`` and naming the
version (``gov.release.verify_at``); the wheel (``--wheel <file>``, else built from the manifest's commit by
``gov.release._wheel``, the route ``gov release`` itself takes) with the manifest's name and sha256. Then it creates
``<common>/gov/envs/<version>/`` (``python -m venv --system-site-packages``; a venv cannot move, so it is made where it
stays), installs the wheel with ``pip --no-deps --no-index`` (never ``-e``), checks the installed gov is the
environment's own and not editable, writes ``pin.json`` and switches ``bin/gov`` by an atomic rename.

A refusal (``InstallRefused``, ``reason`` one of ``no_release``, ``manifest``, ``wheel``, ``environment``) leaves
``<common>/gov/`` exactly as it was: an environment of the same version already there is moved aside and moved back.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from gov import lock, release
from gov.install import probe
from gov.install.locate import common_dir, pin_root

RECORD = "pin.json"


class InstallRefused(Exception):
    """``gov install`` refused; ``reason`` names the check, the message what failed."""

    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


def source_of(project: Path, source=None) -> Path:
    """The Gov OS source: ``source``, else ``_src_path`` of the project's answers file (relative to the project)."""
    if source:
        return Path(os.path.abspath(os.fspath(source)))
    answers = lock._read_map(Path(project) / lock.ANSWERS_REL) or {}
    named = answers.get("_src_path")
    if not isinstance(named, str) or not named:
        raise InstallRefused("no_release", f"no source: --source is not given and {lock.ANSWERS_REL} names no "
                                           "_src_path")
    path = Path(named).expanduser()
    return path if path.is_absolute() else Path(project) / path


def verified(source: Path, version: str, files: bool = False) -> tuple[bytes, str, dict]:
    """The release's manifest bytes, sha256 and manifest, verified at its tag; refused as ``InstallRefused``."""
    try:
        return release.verify_at(source, version, files=files)
    except release.ReleaseError as exc:
        raise InstallRefused(exc.reason or "manifest", str(exc)) from None


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _cut_or_rebuilt(source: Path, version: str, manifest: dict, folder: Path, expected: dict) -> tuple[Path, str]:
    """The release's own wheel (I-17): the cut wheel kept at ``~/.local/share/gov-os/wheels/<commit12>/`` when its
    sha256 is the manifest's; else a rebuild from the manifest's commit, with the build info a gov since F3 writes
    and, if that hashes otherwise, without it (the wheel an older gov cut). The caller still refuses any hash that is
    not the manifest's."""
    commit = str(manifest.get("commit"))
    kept = Path.home() / ".local/share/gov-os/wheels" / commit[:12] / str(expected.get("name"))
    if len(commit) >= 12 and kept.is_file() and _sha256(kept) == expected.get("sha256"):
        return kept, expected["sha256"]
    first = None
    for build_info in (True, False):
        try:
            built = release._wheel(source, commit, keep=folder, build_info=build_info)
        except release.ReleaseError as exc:
            raise InstallRefused("wheel", f"the wheel of release {version} could not be built from its commit "
                                          f"{manifest.get('commit')}: {exc}") from None
        first = first or built
        if built["sha256"] == expected.get("sha256"):
            return Path(built["path"]), built["sha256"]
    return Path(first["path"]), first["sha256"]


def wheel_for(source: Path, version: str, manifest: dict, wheel, folder: Path) -> Path:
    """The wheel file to install: ``wheel``, else built from the manifest's commit into ``folder``; refused unless its
    name and sha256 are the manifest's."""
    expected = manifest["wheel"]
    if wheel:
        path = Path(os.path.abspath(os.fspath(wheel)))
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise InstallRefused("wheel", f"the wheel {path} cannot be read: {exc}") from None
    else:
        path, digest = _cut_or_rebuilt(source, version, manifest, folder, expected)
    if path.name != expected.get("name") or digest != expected.get("sha256"):
        raise InstallRefused("wheel", f"the wheel {path.name} has sha256 {digest}, not the manifest's sha256 "
                                      f"{expected.get('sha256')} (release {version} names {expected.get('name')}): "
                                      "nothing is installed")
    return path


def _clean_env() -> dict:
    return {key: value for key, value in os.environ.items()
            if key not in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "PYTHONSAFEPATH")}


def _run(argv: list, what: str) -> None:
    try:
        done = subprocess.run([str(part) for part in argv], capture_output=True, text=True, env=_clean_env())
    except OSError as exc:
        raise InstallRefused("environment", f"{what}: {exc}") from None
    if done.returncode:
        raise InstallRefused("environment", f"{what} ended with {done.returncode}: "
                                            f"{(done.stderr or done.stdout).strip()[-1500:]}")


def _create_env(env: Path) -> None:
    base = getattr(sys, "_base_executable", None) or sys.executable
    _run([base, "-m", "venv", "--system-site-packages", env], f"python -m venv {env}")


def _pip_install(env: Path, wheel: Path) -> None:
    _run([env / "bin" / "python", "-m", "pip", "install", "--no-deps", "--no-index", "--ignore-installed",
          "--disable-pip-version-check", "--no-warn-script-location", "-q", wheel], f"pip install {wheel.name}")


def _check_env(env: Path) -> None:
    dist = probe.distribution(env)
    if dist is None or dist["editable"] or not (Path(dist["site"]) / "gov" / "__init__.py").is_file() \
            or not (env / "bin" / "gov").is_file():
        raise InstallRefused("environment", f"the environment {env} holds no gov installed from the wheel in its own "
                                            "site-packages")


def _write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _link(link: Path, target: str) -> None:
    temporary = link.with_name(f".{link.name}.{os.getpid()}.new")
    if os.path.lexists(temporary):
        os.unlink(temporary)
    os.symlink(target, temporary)
    os.replace(temporary, link)


def place(common: Path, version: str, wheel: Path, record: dict) -> dict:
    """Create the environment, install the wheel, write the record, switch the link; on any failure, put
    ``<common>/gov/`` back as it was and raise."""
    root = pin_root(common)
    envs, bin_dir = root / "envs", root / "bin"
    env, link, record_path = envs / version, bin_dir / "gov", root / RECORD
    made = next((folder for folder in (root, envs, bin_dir) if not os.path.lexists(folder)), None)
    old_record = record_path.read_bytes() if record_path.is_file() else None
    old_link = os.readlink(link) if os.path.islink(link) else None
    aside = None
    try:
        envs.mkdir(parents=True, exist_ok=True)
        bin_dir.mkdir(exist_ok=True)
        if os.path.lexists(env):
            aside = envs / f".{version}.replaced-{os.getpid()}"
            os.rename(env, aside)
        _create_env(env)
        _pip_install(env, wheel)
        _check_env(env)
        record = {**record, "environment": str(env), "hash_check": "passed"}
        _write_atomic(record_path, (json.dumps(record, indent=2) + "\n").encode())
        _link(link, str(env / "bin" / "gov"))
    except BaseException as exc:
        shutil.rmtree(env, ignore_errors=True)
        if aside is not None:
            os.rename(aside, env)
        if made is not None:
            shutil.rmtree(made, ignore_errors=True)
        if made != root:  # the folder was there before: its record and link go back as they were
            if old_record is None:
                if os.path.lexists(record_path):
                    os.unlink(record_path)
            elif not record_path.is_file() or record_path.read_bytes() != old_record:
                _write_atomic(record_path, old_record)
            if old_link is None:
                if os.path.lexists(link):
                    os.unlink(link)
            elif not os.path.islink(link) or os.readlink(link) != old_link:
                _link(link, old_link)
            for leftover in list(root.glob(f".*.{os.getpid()}.*")) + list(bin_dir.glob(f".*.{os.getpid()}.*")):
                leftover.unlink(missing_ok=True)
        if isinstance(exc, OSError):
            raise InstallRefused("environment", f"the pin under {root} could not be written: {exc}") from None
        raise
    if aside is not None:
        shutil.rmtree(aside, ignore_errors=True)
    return {"version": version, "environment": str(env), "wheel": dict(record["wheel"]), "hash_check": "passed",
            "link": str(link)}


def install(project, version: str, source=None, wheel=None) -> dict:
    """Install release ``version``'s gov as the pin of the repository holding ``project``; the result."""
    project = Path(os.path.abspath(os.fspath(project)))
    common = common_dir(project)
    if common is None:
        raise InstallRefused("environment", f"{project} is in no git repository: the pin lives in its git common dir")
    src = source_of(project, source)
    data, digest, manifest = verified(src, version)
    with tempfile.TemporaryDirectory(prefix="gov-install-") as folder:
        path = wheel_for(src, version, manifest, wheel, Path(folder))
        record = {"version": version, "wheel": {"name": manifest["wheel"]["name"], "sha256": manifest["wheel"]["sha256"]},
                  "manifest_sha256": digest, "source": str(src), "commit": manifest.get("commit")}
        return place(common, version, path, record)
