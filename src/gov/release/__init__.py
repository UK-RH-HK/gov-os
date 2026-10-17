"""Immutable, hash-pinned releases of the Gov OS (W2-16, CAP-43.b lite, DEC-722).

``build`` writes the record of a release under ``docs/releases/<version>/`` of the Gov OS repository, from a
clean commit that ``w2/integrate`` contains: ``manifest.json`` (the version, the commit, every shipped file of
``template/`` with its sha256, the wheel's sha256, the CLI version, the schema versions, the vendored skills'
version and licence, release notes) and ``manifest.sha256``, the manifest's own hash. It neither commits,
tags nor signs: the owner commits the record and tags the release commit, unsigned (CAP-02.c stays in Wave 3).
A version that has a record is never built again (CAP-43).

``verify`` is the one check of a release against its hashes, for every install path: the template's Copier
task (``lock_from``) today, ``gov install`` and ``gov update`` when they exist (W2-18, W2-17).
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path

import yaml

from gov import lock

RELEASES_REL = "docs/releases"
TEMPLATE_REL = "template"
INTEGRATION_BRANCH = "w2/integrate"
MANIFEST_NAME, HASH_NAME = "manifest.json", "manifest.sha256"
SCHEMAS_REL = f"{lock.KERNEL_REL}/schemas"
# semver.org 2.0.0
SEMVER = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
                    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?")


class ReleaseError(Exception):
    """A release is refused: not built, not verified, or not installed."""


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if done.returncode:
        raise ReleaseError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def _hash(path: Path) -> str | None:
    """The sha256 of a file's bytes, or of a link's target as git stores it; ``None`` if it cannot be read."""
    try:
        data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()


def _wheel(repo: Path, commit: str) -> dict:
    """Build the gov wheel from ``commit`` in a temporary folder; its name and sha256."""
    archive = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", commit, "pyproject.toml", "src"],
                             capture_output=True)
    if archive.returncode:
        raise ReleaseError(f"cannot read pyproject.toml and src/ at {commit}: {archive.stderr.decode().strip()}")
    with tempfile.TemporaryDirectory() as folder:
        source, out = Path(folder) / "source", Path(folder) / "wheel"
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(source, filter="data")
        epoch = _git(repo, "show", "-s", "--format=%ct", commit).strip()
        built = subprocess.run([sys.executable, "-c", "import sys; from setuptools import build_meta; "
                                "print(build_meta.build_wheel(sys.argv[1]))", str(out)],
                               cwd=source, capture_output=True, text=True, env={**os.environ, "SOURCE_DATE_EPOCH": epoch})
        wheels = sorted(out.glob("*.whl")) if out.is_dir() else []
        if built.returncode or len(wheels) != 1:
            raise ReleaseError(f"the wheel could not be built: {built.stderr.strip()[-2000:]}")
        return {"name": wheels[0].name, "sha256": _hash(wheels[0])}


def _previous(releases: Path) -> str | None:
    """The commit of the highest release already recorded, for the notes; ``None`` without one."""
    found = []
    for path in releases.glob(f"*/{MANIFEST_NAME}"):
        match = SEMVER.fullmatch(path.parent.name)
        try:
            commit = json.loads(path.read_bytes()).get("commit")
        except (OSError, ValueError, AttributeError):
            continue
        if match and isinstance(commit, str):
            found.append((tuple(int(part) for part in match.groups()[:3]), commit))
    return max(found)[1] if found else None


def build(repo: Path, version: str) -> Path:
    """Write the record of release ``version`` from the repository's HEAD; its folder. Refused: ``ReleaseError``."""
    if not SEMVER.fullmatch(version or ""):
        raise ReleaseError(f"{version!r} is not a semantic version (MAJOR.MINOR.PATCH)")
    repo = Path(_git(Path(repo), "rev-parse", "--show-toplevel").strip())
    dirty = _git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
    if dirty:
        raise ReleaseError(f"the tree has uncommitted or untracked changes: {', '.join(line[3:] for line in dirty[:10])}")
    commit = _git(repo, "rev-parse", "HEAD").strip()
    contained = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", commit,
                                f"refs/heads/{INTEGRATION_BRANCH}"], capture_output=True)
    if contained.returncode:
        raise ReleaseError(f"HEAD {commit} is not a commit of {INTEGRATION_BRANCH}")
    releases = repo / RELEASES_REL
    folder = releases / version
    if lock._present(folder):
        raise ReleaseError(f"release {version} exists ({RELEASES_REL}/{version}): a release is immutable")
    listed = [rel for rel in _git(repo, "ls-tree", "-r", "-z", "--name-only", commit, "--", TEMPLATE_REL).split("\0")
              if rel]
    files = {rel[len(TEMPLATE_REL) + 1:]: _hash(repo / rel) for rel in listed}
    if not files or None in files.values():
        raise ReleaseError(f"cannot hash the shipped files of {TEMPLATE_REL}/")
    try:
        cli_version = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    except (OSError, ValueError, KeyError, TypeError):
        raise ReleaseError("pyproject.toml declares no project version (the CLI version)") from None
    schemas = {rel.rsplit("/", 1)[1].removesuffix(".schema.json"): digest for rel, digest in files.items()
               if rel.startswith(SCHEMAS_REL + "/") and rel.endswith(".schema.json")}
    vendored = {}
    for rel in files:
        parts = rel.split("/")
        if rel.startswith(f"{lock.KERNEL_REL}/skills/") and len(parts) == 5 and parts[4] == "vendored.yaml":
            name = parts[3]
            licence = repo / TEMPLATE_REL / lock.KERNEL_REL / "vendor" / name / "LICENSE"
            try:
                record = yaml.safe_load((repo / TEMPLATE_REL / rel).read_text(encoding="utf-8"))
                vendored[name] = {"version": str(record["version"]), "skills": sorted(record.get("token_sizes") or ()),
                                  "licence_file": f"{lock.KERNEL_REL}/vendor/{name}/LICENSE",
                                  "licence": licence.read_text(encoding="utf-8")}
            except (OSError, UnicodeDecodeError, yaml.YAMLError, KeyError, TypeError):
                raise ReleaseError(f"the vendored skills {name} have no readable version or licence") from None
    previous = _previous(releases)
    subjects = _git(repo, "log", "--max-count=100", "--format=%s", f"{previous}..{commit}" if previous else commit)
    notes = [f"Release {version} of the Gov OS, built from {commit} on {INTEGRATION_BRANCH}."]
    notes += [f"- {line}" for line in subjects.splitlines() if line.strip()]
    manifest = {"version": version, "commit": commit, "cli_version": str(cli_version), "wheel": _wheel(repo, commit),
                "schema_versions": schemas, "vendored": vendored, "release_notes": notes, "files": files}
    data = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    try:
        folder.mkdir(parents=True)
        (folder / MANIFEST_NAME).write_bytes(data)
        (folder / HASH_NAME).write_text(f"{hashlib.sha256(data).hexdigest()}  {MANIFEST_NAME}\n", encoding="utf-8")
    except OSError as exc:
        shutil.rmtree(folder, ignore_errors=True)
        raise ReleaseError(f"the record of release {version} could not be written: {exc}") from None
    return folder


def verify(source: Path, version: str) -> tuple[bytes, str]:
    """Check release ``version`` of the Gov OS repository at ``source`` against its hashes.

    Returns the manifest's bytes and sha256. Refused (``ReleaseError``, naming what is at fault) where the
    manifest does not hash to its stated sha256, or a file of ``template/`` is changed, added or removed.
    """
    folder = Path(source) / RELEASES_REL / version
    try:
        data = (folder / MANIFEST_NAME).read_bytes()
        stated = (folder / HASH_NAME).read_text(encoding="utf-8").split()[0]
        manifest = json.loads(data)
    except (OSError, UnicodeDecodeError, IndexError, ValueError):
        raise ReleaseError(f"release {version}: {MANIFEST_NAME} or {HASH_NAME} cannot be read") from None
    digest = hashlib.sha256(data).hexdigest()
    if stated != digest:
        raise ReleaseError(f"release {version}: {MANIFEST_NAME} does not match the sha256 in {HASH_NAME}")
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if manifest.get("version") != version or not isinstance(files, dict) or not files:
        raise ReleaseError(f"release {version}: {MANIFEST_NAME} is not the manifest of release {version}")
    template = Path(source) / TEMPLATE_REL
    shipped = {}
    for top, names, found in os.walk(template):
        names[:] = [name for name in names if not (top == str(template) and name == ".git")]
        links = [name for name in names if os.path.islink(os.path.join(top, name))]
        for name in found + links:
            path = Path(top) / name
            shipped[path.relative_to(template).as_posix()] = _hash(path)
    wrong = sorted(rel for rel in set(files) | set(shipped) if files.get(rel) is None or files.get(rel) != shipped.get(rel))
    if wrong:
        raise ReleaseError(f"release {version}: shipped files do not match their sha256 in {MANIFEST_NAME}: "
                           f"{', '.join(wrong[:20])}")
    return data, digest


def lock_from(project: Path, source: Path) -> tuple[Path, str | None]:
    """The template's Copier task: verify the release the project's answers name in the template ``source``,
    then write the project's lock with it. A source with no release record installs as before (W1-39); one
    with a record installs release tags only."""
    answers = lock._read_map(Path(project) / lock.ANSWERS_REL) or {}
    tag = answers.get("_commit")
    releases = Path(source) / RELEASES_REL
    if not any(releases.glob(f"*/{MANIFEST_NAME}")):
        return lock.write(project), None
    version = tag[1:] if isinstance(tag, str) and tag.startswith("v") else tag
    if not isinstance(version, str) or not SEMVER.fullmatch(version) or not (releases / version).is_dir():
        raise ReleaseError(f"{tag!r} names no release under {RELEASES_REL}/ of the template: install a release tag")
    data, _ = verify(source, version)
    return lock.write(project, release=(version, data)), version
