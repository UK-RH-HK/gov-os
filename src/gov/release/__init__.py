"""Immutable, hash-pinned releases of the Gov OS (W2-16, CAP-43.b lite, DEC-722).

``build`` writes the record of a release under ``docs/releases/<version>/`` of the Gov OS repository, from a
clean commit that ``w2/integrate`` contains: ``manifest.json`` (the version, the commit, every shipped file of
``template/`` with its sha256, the wheel's sha256, the CLI version, the schema versions, the vendored skills'
version and licence, release notes) and ``manifest.sha256``, the manifest's own hash. It neither commits,
tags nor signs: the owner commits the record and tags the release commit, unsigned (CAP-02.c stays in Wave 3).
A version the repository already knows (a record in the tree or in any ref's history, or a tag), build
metadata aside, is never built again (CAP-43); the files are hashed as the commit holds them.

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
    """A release is refused: not built, not verified, or not installed. ``reason`` names the check that refused, where
    a caller tells them apart (``verify_at``: ``no_release``, ``manifest``, ``files``)."""

    def __init__(self, message: str, reason: str | None = None):
        super().__init__(message)
        self.reason = reason


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if done.returncode:
        raise ReleaseError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def _blobs(repo: Path, commit: str, folder: str) -> dict[str, bytes]:
    """Every file under ``folder`` as ``commit`` holds it (a link as its target), by path; never the work tree's
    bytes, which ``--assume-unchanged`` or ``--skip-worktree`` can hide from ``git status``."""
    entries = []
    for entry in _git(repo, "ls-tree", "-r", "-z", "--full-tree", commit, "--", folder).split("\0"):
        if not entry:
            continue
        meta, rel = entry.split("\t", 1)
        kind, oid = meta.split()[1:3]
        if kind != "blob":
            raise ReleaseError(f"{rel} at {commit} is a {kind}, not a file: it cannot be hashed")
        entries.append((rel, oid))
    done = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], capture_output=True,
                          input="".join(f"{oid}\n" for _, oid in entries).encode())
    if done.returncode:
        raise ReleaseError(f"the files of {folder}/ at {commit} cannot be read: {done.stderr.decode().strip()}")
    out, at, blobs = done.stdout, 0, {}
    for rel, oid in entries:
        end = out.find(b"\n", at)
        header = out[at:end].split() if end >= 0 else []
        if len(header) != 3 or header[0].decode() != oid or header[1] != b"blob":
            raise ReleaseError(f"{rel} at {commit} cannot be read")
        size = int(header[2])
        blobs[rel] = out[end + 1:end + 1 + size]
        at = end + 1 + size + 1
    return blobs


def _precedence(version: str) -> str:
    """A version without its build metadata: two versions with the same one are the same version (semver.org §10)."""
    return version.split("+", 1)[0]


def _known(repo: Path, version: str) -> str | None:
    """Where the repository already knows ``version`` (build metadata aside), or ``None``: a record folder in the
    tree, a record path in the history of any of its refs (a record removed later, or one an older HEAD lacks),
    or a tag ``v<version>`` or ``<version>``. A place that cannot be read refuses (``ReleaseError``)."""
    key = _precedence(version)
    same = lambda name: bool(SEMVER.fullmatch(name)) and _precedence(name) == key  # noqa: E731
    releases = repo / RELEASES_REL
    if lock._present(releases / version):
        return f"{RELEASES_REL}/{version}"
    try:
        names = os.listdir(releases) if lock._present(releases) else []
    except OSError as exc:
        raise ReleaseError(f"{RELEASES_REL}/ cannot be listed: {exc}") from None
    for name in names:
        if same(name):
            return f"{RELEASES_REL}/{name}"
    history = _git(repo, "log", "--all", "--format=", "--name-only", "-z", "--", RELEASES_REL)
    for rel in history.replace("\n", "\0").split("\0"):
        parts = rel.split("/")
        if len(parts) > 3 and same(parts[2]):
            return f"{rel}, in the history of the repository"
    for tag in _git(repo, "for-each-ref", "--format=%(refname:lstrip=2)", "refs/tags").splitlines():
        if same(tag[1:] if tag.startswith("v") else tag):
            return f"the tag {tag}"
    return None


def _hash(path: Path) -> str | None:
    """The sha256 of a file's bytes, or of a link's target as git stores it; ``None`` if it cannot be read."""
    try:
        data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()


BUILD_INFO = "_build_info.py"  # written into the wheel's package by ``_wheel``; read by ``gov --version``


def _wheel(repo: Path, commit: str, keep: Path | None = None, build_info: bool = True) -> dict:
    """Build the gov wheel from ``commit`` in a temporary folder; its name and sha256. With ``keep`` (a folder), the
    built file is kept there too and its ``path`` given: the one route for ``gov release``, ``gov install`` and
    ``gov update``, so a wheel built for an install reproduces the manifest's sha256. ``build_info=False`` builds the
    variant a gov older than F3 cut (no ``gov/_build_info.py``): the one difference between builders (I-17)."""
    archive = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", commit, "pyproject.toml", "src"],
                             capture_output=True)
    if archive.returncode:
        raise ReleaseError(f"cannot read pyproject.toml and src/ at {commit}: {archive.stderr.decode().strip()}")
    with tempfile.TemporaryDirectory() as folder:
        source, out = Path(folder) / "source", Path(folder) / "wheel"
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(source, filter="data")
        sha = _git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").strip()
        # F3: the wheel names the commit it is built from, for ``gov --version`` where no git checkout is around it
        if build_info and (source / "src" / "gov").is_dir():
            (source / "src" / "gov" / BUILD_INFO).write_text(f'COMMIT = "{sha}"\n', encoding="utf-8")
        epoch = _git(repo, "show", "-s", "--format=%ct", commit).strip()
        built = subprocess.run([sys.executable, "-c", "import sys; from setuptools import build_meta; "
                                "print(build_meta.build_wheel(sys.argv[1]))", str(out)],
                               cwd=source, capture_output=True, text=True, env={**os.environ, "SOURCE_DATE_EPOCH": epoch})
        wheels = sorted(out.glob("*.whl")) if out.is_dir() else []
        if built.returncode or len(wheels) != 1:
            raise ReleaseError(f"the wheel could not be built: {built.stderr.strip()[-2000:]}")
        result = {"name": wheels[0].name, "sha256": _hash(wheels[0])}
        if keep is not None:
            kept = Path(keep) / wheels[0].name
            shutil.copyfile(wheels[0], kept)
            result["path"] = str(kept)
        return result


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
    known = _known(repo, version)
    if known:
        raise ReleaseError(f"release {_precedence(version)} exists ({known}): a release is immutable")
    blobs = {rel[len(TEMPLATE_REL) + 1:]: data for rel, data in _blobs(repo, commit, TEMPLATE_REL).items()}
    files = {rel: hashlib.sha256(data).hexdigest() for rel, data in blobs.items()}
    if not files:
        raise ReleaseError(f"cannot hash the shipped files of {TEMPLATE_REL}/")
    try:
        pyproject = _blobs(repo, commit, "pyproject.toml")["pyproject.toml"].decode("utf-8")
        cli_version = tomllib.loads(pyproject)["project"]["version"]
    except (ReleaseError, UnicodeDecodeError, ValueError, KeyError, TypeError):
        raise ReleaseError("pyproject.toml declares no project version (the CLI version)") from None
    schemas = {rel.rsplit("/", 1)[1].removesuffix(".schema.json"): digest for rel, digest in files.items()
               if rel.startswith(SCHEMAS_REL + "/") and rel.endswith(".schema.json")}
    vendored = {}
    for rel in files:
        parts = rel.split("/")
        if rel.startswith(f"{lock.KERNEL_REL}/skills/") and len(parts) == 5 and parts[4] == "vendored.yaml":
            name = parts[3]
            licence = f"{lock.KERNEL_REL}/vendor/{name}/LICENSE"
            try:
                record = yaml.safe_load(blobs[rel].decode("utf-8"))
                vendored[name] = {"version": str(record["version"]), "skills": sorted(record.get("token_sizes") or ()),
                                  "licence_file": licence, "licence": blobs[licence].decode("utf-8")}
            except (UnicodeDecodeError, yaml.YAMLError, KeyError, TypeError, AttributeError):
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


def verify_at(source: Path, version: str, files: bool = True) -> tuple[bytes, str, dict]:
    """Check release ``version`` of the Gov OS repository at ``source`` from git objects at its tag ``v<version>``,
    never the work tree's bytes (W2-18, W2-17): the record's manifest against its ``manifest.sha256`` and, with
    ``files``, every file under ``template/`` at the tag against the manifest's ``files``.

    Returns the manifest's bytes, its sha256 and the manifest. Refused (``ReleaseError`` with ``reason``): no tag
    (``no_release``); a record that cannot be read, does not hash to its sha256 or is not that version's
    (``manifest``); a template file added, removed or changed (``files``)."""
    source, tag = Path(source), f"v{version}"
    found = subprocess.run(["git", "-C", str(source), "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}"],
                           capture_output=True, text=True)
    if found.returncode or not found.stdout.strip():
        raise ReleaseError(f"no release v{version} in {source}: it has no tag {tag}", "no_release")
    commit = found.stdout.strip()
    folder = f"{RELEASES_REL}/{version}"
    try:
        record = _blobs(source, commit, folder)
    except ReleaseError:
        record = {}
    data, stated = record.get(f"{folder}/{MANIFEST_NAME}"), record.get(f"{folder}/{HASH_NAME}")
    if data is None or stated is None:
        raise ReleaseError(f"release {version}: {folder}/{MANIFEST_NAME} or {HASH_NAME} cannot be read at {tag}",
                           "manifest")
    digest = hashlib.sha256(data).hexdigest()
    stated_digest = (stated.decode("utf-8", "replace").split() or [""])[0]
    if stated_digest != digest:
        raise ReleaseError(f"release {version}: {MANIFEST_NAME} at {tag} does not match the sha256 in {HASH_NAME} "
                           f"({HASH_NAME} states {stated_digest}, {MANIFEST_NAME} hashes to {digest})", "manifest")
    try:
        manifest = json.loads(data)
    except ValueError:
        manifest = None
    listed = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(manifest, dict) or manifest.get("version") != version or not isinstance(listed, dict) \
            or not listed or not isinstance(manifest.get("wheel"), dict):
        raise ReleaseError(f"release {version}: {MANIFEST_NAME} at {tag} is not the manifest of release {version}",
                           "manifest")
    if files:
        shipped = {rel[len(TEMPLATE_REL) + 1:]: hashlib.sha256(blob).hexdigest()
                   for rel, blob in _blobs(source, commit, TEMPLATE_REL).items()}
        added = sorted(set(shipped) - set(listed))
        removed = sorted(set(listed) - set(shipped))
        changed = sorted(rel for rel in set(listed) & set(shipped) if listed[rel] != shipped[rel])
        if added or removed or changed:
            named = "; ".join(f"{what}: {', '.join(rels[:20])}" for what, rels in
                              (("added", added), ("removed", removed), ("changed", changed)) if rels)
            raise ReleaseError(f"release {version}: files of {TEMPLATE_REL}/ at {tag} do not match their sha256 in "
                               f"{MANIFEST_NAME} ({named})", "files")
    return data, digest, manifest


def _held(project: Path) -> str | None:
    """The release the project's lock records, or ``None`` where it has no lock or states ``release: null``.
    A lock that cannot be read, or that does not state its release (its release entries deleted), refuses: whether
    it holds a release cannot be told (DEC-761)."""
    path = project / lock.LOCK_REL
    if not lock._present(path):
        return None
    data = lock._read_map(path)
    if data is None:
        raise ReleaseError(f"{lock.LOCK_REL} is not a readable map: whether it records a release cannot be told")
    if "release" not in data:
        raise ReleaseError(f"{lock.LOCK_REL} does not state the release it holds (its release entries are gone)")
    release = data["release"]
    if release is None:
        return None
    version = release.get("version") if isinstance(release, dict) else None
    return version if isinstance(version, str) else repr(release)


def _records_in_history(source: Path) -> str | None:
    """A release record in the history of the git repository at ``source`` (any ref), or ``None``; ``None`` for a
    source that is no git repository (it has no history). A history that cannot be read refuses."""
    if not lock._present(source / ".git"):
        return None
    top = Path(_git(source, "rev-parse", "--show-toplevel").strip())
    if top.resolve() != source.resolve():
        raise ReleaseError(f"{source} holds .git but is not the top of a git repository: its history cannot be read")
    history = _git(source, "log", "--all", "--no-renames", "--format=", "--name-only", "-z", "--", RELEASES_REL)
    for rel in history.replace("\n", "\0").split("\0"):
        parts = rel.split("/")
        if len(parts) > 3 and SEMVER.fullmatch(parts[2]):
            return rel
    return None


def lock_from(project: Path, source: Path) -> tuple[Path, str | None]:
    """The template's Copier task: verify the release the project's answers name in the template ``source``,
    then write the project's lock with it. A source with no release record installs as before (W1-39); one
    with a record installs release tags only.

    Refused (DEC-761): a source with no release record where the project's lock records a release (the lock is
    never rewritten without it), or where the source's history holds release records (they were removed)."""
    project, source = Path(project), Path(source)
    held = _held(project)
    answers = lock._read_map(project / lock.ANSWERS_REL) or {}
    tag = answers.get("_commit")
    releases = source / RELEASES_REL
    if not any(releases.glob(f"*/{MANIFEST_NAME}")):
        if held is not None:
            raise ReleaseError(f"{lock.LOCK_REL} records release {held} and {source} holds no release record: "
                               "a lock that records a release is never rewritten without one")
        removed = _records_in_history(source)
        if removed:
            raise ReleaseError(f"{source} holds no release record but its history does ({removed}): a source whose "
                               "release records were removed is not installed; install a release tag")
        return lock.write(project), None
    version = tag[1:] if isinstance(tag, str) and tag.startswith("v") else tag
    if not isinstance(version, str) or not SEMVER.fullmatch(version) or not (releases / version).is_dir():
        raise ReleaseError(f"{tag!r} names no release under {RELEASES_REL}/ of the template: install a release tag")
    data, _ = verify(source, version)
    return lock.write(project, release=(version, data)), version


# ---------------------------------------------------------------------------
# The patch release (W2-209, RELEASE-ON-BEHALF slice (a); DEC-1223)
# ---------------------------------------------------------------------------

PATCH_CALLER = "orchestrator"
_UNSET = object()


def _refuse(message: str, details: dict):
    from gov.cli.errors import GovError

    return GovError("RELEASE_REFUSED", message, details)


def _caller(caller) -> None:
    """Only ``GOV_ROLE=orchestrator`` cuts or checks a patch release, before anything is read (DEC-772 stays the
    owner's for the plain form, which this never is). The caller is the role in the process's environment."""
    role = os.environ.get("GOV_ROLE") if caller is _UNSET else caller
    if role != PATCH_CALLER:
        raise _refuse(f"gov release --patch is refused for GOV_ROLE={role!r}: only the orchestrator "
                      "(GOV_ROLE=orchestrator) cuts a patch release; the owner uses the plain gov release",
                      {"caller": role})


def _patch_check(root: Path, version: str, caller=_UNSET) -> dict:
    """``gov release <X> --patch --check``: the patch rule at HEAD, nothing read beyond git objects, nothing written."""
    from gov.release import patch

    _caller(caller)
    try:
        result = patch.evaluate(Path(root), version)
    except ReleaseError as exc:
        raise _refuse(f"the patch rule cannot be read: {exc}", {"gate": "G1", "reason": str(exc)}) from None
    if result["kind"] != "patch":
        named = "; ".join(f"{rule}: {result['rules'][rule]['detail']}" for rule in result["failed"])
        raise _refuse(f"this is a bigger release ({named}): only the owner builds it, gov release {version}",
                      {"kind": "bigger", "from": result["from"], "commit": result["commit"], "rules": result["rules"],
                       "failed": result["failed"]})
    return result


def _cut(root: Path, version: str, *, suite=None, kept=None, rehearse=None, repin=None, push=None, caller=_UNSET) -> dict:
    """The cut: the caller, then G0 to G4 in order (the first red refuses, naming the gate), then the record committed
    on a side branch of C, tagged and merged, then the re-pin. ``rehearse`` and ``repin`` default to the real ones;
    only ``_patch_test`` passes others."""
    from gov.release import cut, gates, patch, proving, repin as repinning

    _caller(caller)
    root = Path(root)
    rehearse = rehearse or proving.rehearse
    repin = repin or repinning.repin
    try:
        authority = gates.g0(root)
        result = gates.g1(root, version)
        commit = result["commit"]
        evidence = gates.g2(root, suite, commit)
        report = gates.g3(root, commit, version, lambda: rehearse(root, commit, version, kept))
        gates.g4(root, commit, version, result["from"])
    except gates.GateRefused as red:
        raise _refuse(f"patch release {version} refused at {red.gate}: {red.reason}", red.details) from None
    decision = authority["decision"]
    kind = patch.kind_record(result)

    def extras(record: dict) -> dict:
        fixes, chores = patch.changes(root, result["from"], commit)
        listed = Path.home() / ".gov-os" / "update" / "repositories"
        try:
            repositories = [line.strip() for line in listed.read_text(encoding="utf-8").splitlines() if line.strip()]
        except OSError:
            repositories = []
        shown = {"record": evidence["record"], "head": evidence["head"], "verdict": report.get("verdict"),
                 "kind": kind["kind"]}
        gates_json = {"suite": {key: evidence[key] for key in ("record", "head", "tree", "optin")}, "proving": report,
                      "rule": {"kind": kind["kind"], "rules": kind["rules"]}}
        return {"kind.json": patch.dumps(kind).encode("utf-8"), "gates.json": patch.dumps(gates_json).encode("utf-8"),
                "suite.json": evidence["raw"],
                "NOTE.md": repinning.note_text(version, result["from"], fixes, chores, shown, repositories).encode("utf-8")}

    try:
        made = cut.cut(root, version, commit, extras, decision)
    except ReleaseError as exc:
        raise _refuse(f"patch release {version} not cut: {exc}", {"gate": "G4", "reason": str(exc)}) from None
    pinned = repin(root, version, Path.home(), push=push)
    return {"version": version, "commit": commit, "tag": made["tag"], "record": made["record"],
            "record_commit": made["record_commit"], "kind": kind, "repin": pinned}


def _patch_test(root: Path, version: str, *, suite=None, rehearse=None, repin=None, push=None, caller=_UNSET) -> dict:
    """Test seam for the cut, beside ``gov release --patch`` as ``command._release_test`` is beside the plain form:
    G3, the re-pin and the push may be stood in, and ``caller`` named. The command line never reaches it: it calls
    ``_cut`` with the real rehearsal and re-pin only, so no flag or variable stands in for a gate."""
    return _cut(root, version, suite=suite, rehearse=rehearse, repin=repin, push=push, caller=caller)
