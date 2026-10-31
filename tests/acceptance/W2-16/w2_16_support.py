"""Support code for the W2-16 acceptance tests (standard library, PyYAML, W1-07's and W1-39's support).

W2-16 makes Gov OS releases immutable and hash-pinned (CAP-43.b lite, DEC-722): ``gov release <version>``
builds a release record under ``docs/releases/`` of the repository it runs in, the owner tags the release
commit (unsigned), and ``framework.lock`` of a project installed from a release tag records the release's
version and manifest hash. The tests use public interfaces only: the ``gov`` command line (``gov release``,
``gov doctor --json``), the tool ``copier`` on a template source made of ``copier.yml`` and ``template/``,
the files of a created project and of a release record, and ``git`` in temporary repositories. No module of
``src/gov/lock/`` or of the release code is imported or named, but one: the seam of DEC-772 item 1,
``gov.release.command._release_test``, imported only inside the seam driver's own process.

**No copy of this repository.** ``build_gov_os_repository`` builds a stand-in Gov OS repository in a
temporary folder from single named files of this worktree, listed by ``git ls-files`` and limited to
``.gitignore``, ``pyproject.toml``, ``copier.yml``, ``template/`` and ``src/gov/`` (bytecode left out),
copied one by one as W1-39's ``assemble_source`` copies the template source. Nothing under
``governance/project/`` of this repository is copied. The stand-in's ``pyproject.toml`` declares the CLI
version ``STAND_IN_CLI_VERSION`` so that the manifest's CLI version can be told from the release version
and from this worktree's own. Its branch is ``w2/integrate``. Every release, tag and commit is made there,
never in this repository.

**The owner's builds (DEC-772 item 1).** ``gov release <version>`` refuses from every test run (a Claude Code
session among its ancestors, or no terminal). The suite builds its releases as the owner in person through the seam
``gov.release.command._release_test`` (the lead's specification for round 3, in the form of W1-50's freeze lift),
called in a new process with a planted chain, a pseudo-terminal and the shown code typed back: see the last section
of this module. The cases that hold the build's own refusals (an unclean tree, a bad version, immutability) call
it the same way and hold the refusal to be the build's (``assert_the_build_refuses``); only round 3's real-command
cases and the role cases run the real ``gov release``.

**This worktree's code.** Every ``gov`` the tests run is this worktree's: ``gov release`` runs as
``sys.executable -m gov.cli.main`` with ``PYTHONPATH`` set to this worktree's ``src/``, and the seam's driver
imports it with the same ``PYTHONPATH``; ``gov doctor`` runs
through W1-07's launcher with the same ``PYTHONPATH``; the ``gov`` a Copier task finds on ``PATH`` is a
script that puts this worktree's ``src/`` first on ``sys.path`` before it imports ``gov``, and a
``python3`` a Copier task runs gets ``PYTHONPATH`` set to the same folder (W1-39's arrangement).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import select
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W1-07", _HERE.parent / "W1-39"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w1_07_support as base  # noqa: E402
import w1_39_support as w139  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# --- what the sources fix -------------------------------------------------
INTEGRATION_BRANCH = "w2/integrate"                 # KPI success 1; WAVE_2_WBS section 0 rule 2, "Releases" (DEC-720)
RELEASES_REL = "docs/releases"                      # the ticket's allowed path docs/releases/**
TEMPLATE_REL = "template"                           # ADR-0002 section 5 (_subdirectory: template)
KERNEL_REL = "governance/kernel"                    # ADR-0002 section 5
OVERLAY_REL = "governance/project"                  # ADR-0002 section 5
LOCK_REL = w139.LOCK_REL                            # governance/framework.lock (W1-39)
ANSWERS_REL = w139.ANSWERS_REL                      # .copier-answers.yml (DEC-023, DEC-493)
MANIFEST_KEY = w139.MANIFEST_KEY                    # the lock's file-hash manifest (W1-39, CAP-02.a)
SCHEMAS_REL = "governance/kernel/schemas"           # the kernel's schemas (W1-08), as a project receives them
VENDORED_RECORD_REL = "governance/kernel/skills/superpowers/vendored.yaml"   # DEC-246: the version, beside the copies
VENDOR_LICENCE_REL = "governance/kernel/vendor/superpowers/LICENSE"          # DEC-194: the upstream licence
VENDORED_SKILLS = ("test-driven-development", "systematic-debugging", "verification-before-completion")  # DEC-194

FIRST_VERSION, SECOND_VERSION = "1.4.0", "1.5.0"    # semantic versions, unlike the CLI's and the vendored skills'
FIRST_TAG, SECOND_TAG = f"v{FIRST_VERSION}", f"v{SECOND_VERSION}"   # the owner's tags: v<version> (W1-39's form)
STAND_IN_CLI_VERSION = "0.7.3"                      # what the stand-in's pyproject.toml declares
PLAIN_TAG = "v0.1.0"                                # a template source with no release record (W1-39's source)
# A file a release ships, changed between the two releases (so the second release is a real one).
CHANGED_BY_SECOND_RELEASE = "template/governance/kernel/README.w2-16.md"
# The kernel file the tampering cases change, add beside, or remove: one the template ships in both releases.
TAMPERED_REL = "template/governance/kernel/schemas/ticket.schema.json"
ADDED_REL = "template/governance/kernel/schemas/w2-16-added.schema.json"

GOV_TIMEOUT_S = 600.0       # a release builds a wheel: a wait, not a time the ticket promises
COPIER_TIMEOUT_S = 300.0
SHA256_RE = re.compile(r"[0-9a-f]{64}")
SIGNATURE_SUFFIXES = (".sig", ".asc", ".minisig", ".sigstore", ".p7s", ".pem")

git = base.git
make_sandbox = base.make_sandbox
require_copier = w139.require_copier
Done = w139.Done


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256(path):
    return sha256_bytes(Path(path).read_bytes())


OTHER_HASH = sha256_bytes(b"W2-16: a hash that belongs to nothing\n")


def commit_all(repo, message):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return git(repo, "rev-parse", "HEAD").strip()


def head(repo):
    return git(repo, "rev-parse", "HEAD").strip()


def tags(repo):
    return sorted(line for line in git(repo, "tag", "--list").splitlines() if line.strip())


def porcelain_paths(repo):
    """Every path ``git status`` shows (changed, staged or untracked, not ignored), file by file."""
    listing = git(repo, "status", "--porcelain", "--untracked-files=all")
    return sorted(line[3:] for line in listing.splitlines() if line.strip())


def under(rel, folder):
    return rel == folder or rel.startswith(folder.rstrip("/") + "/")


# --------------------------------------------------------------------------
# A stand-in Gov OS repository, built from single named files
# --------------------------------------------------------------------------

def _listing():
    done = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         ".gitignore", "pyproject.toml", "copier.yml", "template", "src/gov"],
        capture_output=True, text=True, check=True)
    names = sorted(set(item for item in done.stdout.split("\0") if item))
    return [rel for rel in names if "__pycache__" not in rel.split("/") and not rel.endswith(".pyc")
            and ".egg-info" not in rel and not under(rel, OVERLAY_REL)]


def build_gov_os_repository(destination):
    """A Gov OS repository of its own in ``destination``: one commit on ``w2/integrate``, no tag, no release.

    One file is added to the template, ``CHANGED_BY_SECOND_RELEASE``, so that a later release can change a
    shipped file without touching one the template has.
    """
    destination = Path(destination)
    if not (REPO_ROOT / "copier.yml").is_file():
        raise AssertionError("no copier.yml in this worktree: it is not a Copier template (W1-39)")
    destination.mkdir(parents=True, exist_ok=True)
    for rel in _listing():
        origin = REPO_ROOT / rel
        if not origin.is_file() or origin.is_symlink():
            continue
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, target)
    pyproject = destination / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    changed = re.sub(r'(?m)^version\s*=\s*"[^"]*"', f'version = "{STAND_IN_CLI_VERSION}"', text, count=1)
    assert changed != text, "pyproject.toml of this worktree declares no version line to stand in for"
    pyproject.write_text(changed, encoding="utf-8")
    (destination / CHANGED_BY_SECOND_RELEASE).write_text("W2-16: a shipped file, first form\n", encoding="utf-8")
    git(destination, "init", "-q", "-b", INTEGRATION_BRANCH)
    _configure(destination)
    commit_all(destination, "the Gov OS at an integration commit")
    return destination


def _configure(repo):
    git(repo, "config", "user.name", "W2-16 tests")
    git(repo, "config", "user.email", "w2-16@example.invalid")


def clone_folder(origin, destination):
    """A copy of a *temporary* repository or project the tests built (never of this repository)."""
    origin, destination = Path(origin), Path(destination)
    assert REPO_ROOT.resolve() not in (origin.resolve(), *origin.resolve().parents), \
        "the tests never copy this repository or a folder of it"
    shutil.copytree(origin, destination, symlinks=True)
    return destination


def build_plain_source(destination):
    """W1-39's template source: ``copier.yml`` and ``template/`` alone, tagged ``PLAIN_TAG``; no release record."""
    source = w139.assemble_source(destination)
    assert PLAIN_TAG in tags(source.path), f"W1-39's template source is not tagged {PLAIN_TAG}"
    return source.path


# --------------------------------------------------------------------------
# Running gov
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + "\n" + self.stderr

    def describe(self):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-4000:]}\n"
                f"stderr:\n{self.stderr[-4000:]}")


def gov_environment(sandbox):
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W2-16 tests", "GIT_AUTHOR_EMAIL": "w2-16@example.invalid",
        "GIT_COMMITTER_NAME": "W2-16 tests", "GIT_COMMITTER_EMAIL": "w2-16@example.invalid",
    }


def run_gov(cwd, sandbox, *args):
    """``gov <args>`` in ``cwd``, as ``sys.executable -m gov.cli.main`` with this worktree's ``src/``."""
    assert Path(cwd).resolve() != REPO_ROOT.resolve(), "no gov command of these tests runs in this worktree"
    argv = (sys.executable, "-m", "gov.cli.main", *args)
    try:
        done = subprocess.run(argv, cwd=str(cwd), env=gov_environment(sandbox), capture_output=True, text=True,
                              timeout=GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {GOV_TIMEOUT_S:.0f} s") from None
    return Run(tuple(args), done.returncode, done.stdout, done.stderr)


def doctor(project, sandbox):
    """``gov doctor --json`` in the project with this worktree's code (W1-39's reading of the report)."""
    return w139.doctor(project, sandbox)


# --------------------------------------------------------------------------
# The state of a repository, to show that a refused release wrote nothing
# --------------------------------------------------------------------------

def snapshot(repo):
    """Every file and folder of the repository outside ``.git`` (bytes and mode), its refs, HEAD and index."""
    repo = Path(repo)
    entries = {}
    for path in sorted(repo.rglob("*")):
        rel = path.relative_to(repo).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode):
            entries[rel + "/"] = ("folder", stat.S_IMODE(info.st_mode))
        else:
            entries[rel] = (sha256(path) if path.is_file() else os.readlink(path), stat.S_IMODE(info.st_mode))
    refs = git(repo, "for-each-ref", "--format=%(refname) %(objectname)")
    symbolic = git(repo, "symbolic-ref", "-q", "HEAD", check=False)
    index = git(repo, "ls-files", "-s")
    return {"files": entries, "refs": refs, "head": head(repo), "symbolic": symbolic, "index": index}


def snapshot_difference(before, after):
    changed = []
    for key in ("refs", "head", "symbolic", "index"):
        if before[key] != after[key]:
            changed.append(key)
    files_before, files_after = before["files"], after["files"]
    for rel in sorted(set(files_before) | set(files_after)):
        if files_before.get(rel) != files_after.get(rel):
            changed.append(rel)
    return changed


# --------------------------------------------------------------------------
# A release record and its manifest
# --------------------------------------------------------------------------

def parse_structured(data):
    """A file's bytes parsed as JSON, else YAML; ``None`` where neither gives a value."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    try:
        return json.loads(text)
    except ValueError:
        pass
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None


def walk(value, trail=()):
    """``(trail of keys, leaf)`` for every leaf of a parsed document; keys are part of the trail."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, trail + (str(key),))
    elif isinstance(value, list):
        for item in value:
            yield from walk(item, trail)
    else:
        yield trail, value


def dicts_in(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from dicts_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from dicts_in(item)


def scalars(value):
    """Every leaf value as a string (booleans and ``None`` left out)."""
    return {str(leaf) for _, leaf in walk(value) if isinstance(leaf, (str, int, float)) and not isinstance(leaf, bool)}


def normalise_path(rel):
    rel = str(rel).strip()
    rel = rel[2:] if rel.startswith("./") else rel
    return rel[len(TEMPLATE_REL) + 1:] if rel.startswith(TEMPLATE_REL + "/") else rel


def file_hashes(manifest):
    """``{path: {sha256, ...}}`` the manifest gives, paths as a project sees them (``template/`` taken off).

    Two forms are read: a map entry ``<path>: <sha256>``, and a map holding a path under ``path`` (or
    ``file``, ``name``) beside a ``sha256``.
    """
    found = {}
    for entry in dicts_in(manifest):
        for key, item in entry.items():
            if isinstance(item, str) and SHA256_RE.fullmatch(item.strip().lower()) and ("/" in str(key) or "." in str(key)):
                found.setdefault(normalise_path(key), set()).add(item.strip().lower())
        digest = entry.get("sha256")
        where = next((entry[k] for k in ("path", "file", "name") if isinstance(entry.get(k), str)), None)
        if isinstance(digest, str) and where and SHA256_RE.fullmatch(digest.strip().lower()):
            found.setdefault(normalise_path(where), set()).add(digest.strip().lower())
    return found


def collapse(text):
    return " ".join(str(text).split())


@dataclass
class ReleaseRecord:
    version: str
    repo: Path
    run: Run
    built_from: str                 # HEAD before `gov release` ran
    release_commit: str             # HEAD once the record is committed
    tags_before: list
    tags_after_run: list            # the tags right after `gov release`, before the test tags anything
    commits_by_release: list        # commits `gov release` made itself, if any
    dirty_after_run: list           # paths git showed changed or untracked right after the run
    record_files: dict = field(default_factory=dict)   # {rel under the repository: bytes}
    manifest_rel: str = ""

    @property
    def manifest_bytes(self):
        return self.record_files[self.manifest_rel]

    @property
    def manifest_hash(self):
        return sha256_bytes(self.manifest_bytes)

    @property
    def manifest(self):
        return parse_structured(self.manifest_bytes)

    def describe(self):
        files = "\n".join(f"  {rel} ({len(data)} bytes)" for rel, data in sorted(self.record_files.items()))
        return (f"release {self.version} of {self.repo}\nrecord files:\n{files}\nmanifest {self.manifest_rel}:\n"
                f"{self.manifest_bytes[:3000].decode('utf-8', 'replace')}\n{self.run.describe()}")


def build_release(repo, sandbox, version, tag=None, annotated=False):
    """Build release ``version`` in ``repo`` as the owner in person; commit the record where the build left it
    uncommitted; tag the release commit ``tag`` (unsigned, standing for the owner). Fails the case where no release
    is built.

    **Rewritten (DEC-772; Rewrite-Reason: DEC-772).** It ran ``gov release <version>`` as a child process. Under
    DEC-772 item 1 that call refuses from every test run (a Claude Code session among its ancestors, or no
    terminal), so every case that needs a release would fail for a reason that is not its own. It now builds through
    the seam ``gov.release.command._release_test`` (``release_as_the_owner``): a planted chain with no Claude Code
    session that reaches process 1, a pseudo-terminal, the shown code typed back, ``GOV_ROLE`` and ``GOV_TICKET``
    absent. Every assertion it made is kept: a release from a clean ``w2/integrate`` commit, nothing changed outside
    ``docs/releases/``, a record written, the owner's commit and tag.
    """
    repo = Path(repo)
    before_head, before_tags = head(repo), tags(repo)
    seam = release_as_the_owner(repo, sandbox, version)
    if seam.status == MISSING:
        seam_built(seam)
    run = seam.as_run(version)
    assert run.returncode == 0, (
        f"`gov release {version}`, as the owner in person through the seam (a plain terminal's ancestry, a "
        f"terminal, the shown code typed back), did not build a release from a clean {INTEGRATION_BRANCH} commit "
        f"(CAP-43.b lite; DEC-772)\n{run.describe()}")
    tags_after_run = tags(repo)
    after_run_head = head(repo)
    commits = git(repo, "rev-list", f"{before_head}..{after_run_head}").split()
    dirty = porcelain_paths(repo)
    outside = [rel for rel in dirty if not under(rel, RELEASES_REL)]
    assert not outside, f"`gov release {version}` changed paths outside {RELEASES_REL}/: {outside[:10]}"
    if dirty:
        commit_all(repo, f"the record of release {version}")
    release_commit = head(repo)
    changed = git(repo, "diff", "--name-only", before_head, release_commit).split()
    outside = [rel for rel in changed if not under(rel, RELEASES_REL)]
    assert not outside, f"the release commit of {version} changes paths outside {RELEASES_REL}/: {outside[:10]}"
    record = {rel: (repo / rel).read_bytes() for rel in changed if (repo / rel).is_file()}
    assert record, f"`gov release {version}` wrote no record under {RELEASES_REL}/\n{run.describe()}"
    result = ReleaseRecord(version, repo, run, before_head, release_commit, before_tags, tags_after_run, commits,
                           dirty, record)
    result.manifest_rel = _find_manifest(result)
    if tag:
        if annotated:
            git(repo, "tag", "-a", "-m", f"release {version}", tag, release_commit)
        else:
            git(repo, "tag", tag, release_commit)
    return result


def _find_manifest(record):
    candidates = []
    for rel, data in record.record_files.items():
        if "manifest" not in rel.rsplit("/", 1)[-1].lower():
            continue
        parsed = parse_structured(data)
        if isinstance(parsed, dict) and record.version in scalars(parsed):
            candidates.append(rel)
    assert len(candidates) == 1, (
        f"the record of release {record.version} holds {len(candidates)} manifests (a file whose name holds "
        f"'manifest', a JSON or YAML map that names the version): {candidates}\nrecord files: "
        f"{sorted(record.record_files)}\n{record.run.describe()}")
    return candidates[0]


def shipped_files(repo, commit):
    """``{path as a project sees it: sha256}`` of every file under ``template/`` at ``commit``."""
    listing = git(repo, "ls-tree", "-r", "--name-only", commit, "--", TEMPLATE_REL).split("\n")
    found = {}
    for rel in (item for item in listing if item):
        data = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{rel}"], capture_output=True,
                              check=True).stdout
        found[normalise_path(rel)] = sha256_bytes(data)
    return found


def replace_in_record(repo, record, old, new, include_manifest=False):
    """Replace the text ``old`` by ``new`` in the record's files on disk (the manifest only when asked).

    Returns the files changed.
    """
    changed = []
    for rel in record.record_files:
        if rel == record.manifest_rel and not include_manifest:
            continue
        path = Path(repo) / rel
        data = path.read_bytes()
        if old.encode() in data:
            path.write_bytes(data.replace(old.encode(), new.encode()))
            changed.append(rel)
    return changed


# --------------------------------------------------------------------------
# Running Copier
# --------------------------------------------------------------------------

def write_gov_command(folder):
    """An executable ``gov`` in ``folder``: this worktree's command line, whatever ``PYTHONPATH`` says.

    With ``W2_16_SHOW_GOV`` set it prints the file of the ``gov`` package it imported, and stops.
    """
    module, attribute = base.entry_point(REPO_ROOT)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    command = folder / "gov"
    command.write_text(
        f"#!{sys.executable}\n"
        "import os, sys\n"
        f"sys.path.insert(0, {str(SRC)!r})\n"
        "if os.environ.get('W2_16_SHOW_GOV'):\n"
        "    import gov\n"
        "    print(gov.__file__)\n"
        "    sys.exit(0)\n"
        f"import {module} as _module\n"
        "_target = _module\n"
        f"for _name in {attribute!r}.split('.'):\n"
        "    _target = getattr(_target, _name)\n"
        "sys.argv[0] = 'gov'\n"
        "sys.exit(_target())\n",
        encoding="utf-8",
    )
    command.chmod(command.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return command


def write_python_without_gov(folder):
    """``python3`` and ``python`` in ``folder`` that run this machine's Python isolated: no ``gov`` to import."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("python3", "python"):
        path = folder / name
        path.write_text(f'#!/bin/sh\nexec {sys.executable} -I "$@"\n', encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return folder


def copier_environment(sandbox, python_without_gov=False):
    """What a Copier task finds: this worktree's ``gov`` first on ``PATH``, an empty ``HOME``, no network.

    By default ``python3`` imports this worktree's ``gov`` (``PYTHONPATH``), as W1-39 arranges it. With
    ``python_without_gov`` the ``python3`` on ``PATH`` is isolated and ``PYTHONPATH`` is unset: ``gov``, an
    isolated tool, is the only way to this worktree's code (W2-M175).
    """
    elsewhere = Path(sandbox.elsewhere)
    commands = elsewhere / "commands"
    write_gov_command(commands)
    folders = [str(commands)]
    if python_without_gov:
        folders.append(str(write_python_without_gov(elsewhere / "python-without-gov")))
    folders += [str(Path(sys.executable).parent), *os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)]
    env = {
        "PATH": os.pathsep.join(folders),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W2-16 tests", "GIT_AUTHOR_EMAIL": "w2-16@example.invalid",
        "GIT_COMMITTER_NAME": "W2-16 tests", "GIT_COMMITTER_EMAIL": "w2-16@example.invalid",
    }
    if not python_without_gov:
        env["PYTHONPATH"] = str(SRC)
    return env


def run_copier(binary, sandbox, cwd, *args, python_without_gov=False):
    assert Path(cwd).resolve() != REPO_ROOT.resolve() and str(REPO_ROOT) not in args, \
        "Copier is never given this repository as its source or its destination"
    argv = (str(binary), *args)
    try:
        done = subprocess.run(argv, cwd=str(cwd), env=copier_environment(sandbox, python_without_gov),
                              capture_output=True, text=True, timeout=COPIER_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{' '.join(argv)} did not end within {COPIER_TIMEOUT_S:.0f} s") from None
    return Done(("copier", *args), done.returncode, done.stdout, done.stderr)


def copier_report(done):
    """A Copier run without its account of every file it wrote (W1-39's ``Done.printed``)."""
    return f"{' '.join(done.argv)}\nexit code: {done.returncode}\n{done.printed[-6000:]}"


def copy(binary, sandbox, source, destination, ref, python_without_gov=False):
    """``copier copy --defaults --trust --vcs-ref <ref> <source> <destination>``; the run, whatever its exit code."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    return run_copier(binary, sandbox, destination.parent, "copy", "--defaults", "--trust", "--vcs-ref", ref,
                      str(source), str(destination), python_without_gov=python_without_gov)


def create_project(binary, sandbox, source, destination, ref, python_without_gov=False):
    """A project created by ``copier copy`` and committed as a git repository of its own."""
    done = copy(binary, sandbox, source, destination, ref, python_without_gov)
    assert done.returncode == 0, f"`copier copy` from {ref} failed\n{copier_report(done)}"
    destination = Path(destination)
    if not (destination / ".git").exists():
        git(destination, "init", "-q", "-b", "main")
    _configure(destination)
    commit_all(destination, f"created by copier copy from {ref}")
    return destination


def update(binary, sandbox, project, ref):
    """``copier update --defaults --trust --vcs-ref <ref>`` in the project; the run, whatever its exit code."""
    return run_copier(binary, sandbox, project, "update", "--defaults", "--trust", "--vcs-ref", ref)


# --------------------------------------------------------------------------
# The lock of a project
# --------------------------------------------------------------------------

def lock_bytes(project):
    path = Path(project) / LOCK_REL
    return path.read_bytes() if path.is_file() else None


def lock_data(project):
    data = lock_bytes(project)
    assert data is not None, f"the project has no {LOCK_REL}"
    parsed = parse_structured(data)
    assert isinstance(parsed, dict), f"{LOCK_REL} is not a YAML map"
    return parsed


def lock_scalars(project):
    return scalars(lock_data(project))


def lock_names(project):
    """Every key and every string value of the lock (its comment header left out, as YAML leaves it out)."""
    data = lock_data(project)
    names = set(scalars(data))
    for entry in dicts_in(data):
        names.update(str(key) for key in entry)
    return names


def files_of(project):
    root = Path(project)
    found = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        if path.is_file():
            found.append(rel)
    return found


def append_one_byte(path):
    with open(path, "ab") as handle:
        handle.write(b"\n")


def assert_lock_part_fails(result, why):
    """The lock part is failed (not passed, not unmeasured) and doctor exits non-zero."""
    assert result.section.get("status") == "fail" and not result.claims_match, (
        f"gov doctor's lock part does not fail although {why}\n{result.describe()}")
    assert result.run.returncode != 0 and result.run.envelope().get("ok") is False, (
        f"gov doctor exits 0 although {why}\n{result.describe()}")


# --------------------------------------------------------------------------
# gov release from a plain terminal (DEC-772 item 1): the seam, in the freeze lift's form
# --------------------------------------------------------------------------
#
# ``gov release <version>`` refuses with a Claude Code session among its ancestors, with the chain unreadable up
# to process 1, with GOV_ROLE or GOV_TICKET set, without a terminal on both sides, or when the code typed back is
# not the code shown. Every test run is under an agent session or without a terminal, so a test that needs a
# release, or asks how the build form judges a chain or a terminal, calls the private test function (the lead's
# specification for this round, in the form of W1-50's ``gov.pause.command._lift_test``):
#
#     gov.release.command._release_test(root, version, ancestry=None, terminal=None) -> dict
#
# ``ancestry``: a chain in the form ``gov.pause.command.read_ancestry()`` returns (maps ``pid``, ``ppid``, ``comm``,
# ``exe``, ``cmdline``; this process first, the system's first process last). ``terminal``: a pair of descriptors
# ``(input, output)``, each asked ``os.isatty`` by the product whatever is passed. GOV_ROLE and GOV_TICKET are read
# from the process environment, never planted. It returns ``{"version", "record"}`` or raises ``GovError`` with code
# ``RELEASE_REFUSED`` and ``details["reason"]``. The call is made in a new process whose environment is built from
# scratch (``gov_environment``: no GOV_ROLE, no GOV_TICKET unless a case sets one), with a pseudo-terminal the
# driver opens, reads the shown code from and types the reply on. Copied from W1-50's ``w1_50_freeze_lift`` (no
# module of W1-50 is imported).

RELEASE_MODULE, RELEASE_FUNCTION = "gov.release.command", "_release_test"
RELEASE_REFUSED = "RELEASE_REFUSED"
RELEASE_CODE = re.compile(r"RELEASE-\d{4}")         # "the word RELEASE- followed by four decimal digits"
REFUSAL_LIMIT_S = 60.0          # a refused call reads and writes nothing: a wait, not a time the ticket promises
REASONS = ("session", "ancestry", "role", "ticket", "terminal", "code")

# What is typed back when a code has been shown.
RIGHT, WRONG, EMPTY_LINE, END_OF_INPUT = "right", "wrong", "empty", "eof"
# What the function is handed as its terminal.
PTY = "pty"                     # input and output are one pseudo-terminal
PIPE_IN = "pipe-in"             # input is a pipe, output is a pseudo-terminal
PIPE_OUT = "pipe-out"           # input is a pseudo-terminal, output is a pipe
PIPES = "pipes"                 # both are pipes
NO_TERMINAL = "devnull"         # both are /dev/null

RELEASED, REFUSED, MISSING, HANG, CRASH = "released", "refused", "missing", "hang", "crash"

# Planted chains: W1-50's shapes, the command's own process being `gov release`.
_OWNER_HOME = "/home/owner"
_VERSION_FILE = f"{_OWNER_HOME}/.local/share/claude/versions/2.1.288"
_CLI = f"{_OWNER_HOME}/.local/bin/claude"
_EXTENSION_BINARY = (f"{_OWNER_HOME}/.vscode-server/extensions/anthropic.claude-code-2.1.288-linux-x64/resources/"
                     "native-binary/claude")
_EDITOR = f"{_OWNER_HOME}/.vscode-server/bin/0f0d87fa9e96c856c5212fc86db137ac0d783365"

OWN_PROCESS = ("python3", "/usr/bin/python3.12", ["python3", "-m", "gov.cli.main", "release", FIRST_VERSION])
LOGIN_SHELL = ("bash", "/usr/bin/bash", ["-bash"])
BASH_C = ("bash", "/usr/bin/bash", ["/bin/bash", "-c", f"python3 -m gov.cli.main release {FIRST_VERSION}"])
INIT = ("init", None, ["/init"])
SYSTEMD = ("systemd", None, ["/sbin/init", "splash"])
EDITOR_NODE = ("node", f"{_EDITOR}/node", [f"{_EDITOR}/node", f"{_EDITOR}/out/server-main.js", "--host=127.0.0.1"])
EDITOR_SH = ("sh", "/usr/bin/dash", ["sh", f"{_EDITOR}/bin/code-server", "--host=127.0.0.1"])
HEADLESS = ("claude", _VERSION_FILE, [_CLI, "-p", "do the ticket's work"])
CONSOLE = ("claude", _EXTENSION_BINARY, [_EXTENSION_BINARY, "--output-format", "stream-json", "--verbose"])
LAUNCHED = ("claude", _VERSION_FILE, [_CLI, "--settings", '{"env":{"GOV_ROLE":"engineer"}}', "-p", "do the work"])
GOV_LAUNCH = ("python3", "/usr/bin/python3.12",
              ["python3", "-m", "gov.cli.main", "launch", "engineer", "DAEO-49o5", "--", "-p", "do the work"])
NPM_INSTALL = ("node", "/usr/bin/node", ["node", "/usr/lib/node_modules/@anthropic-ai/claude-code/cli.js", "-p", "x"])
RENAMED_COMM = ("worker", None, [_CLI, "-p", "x"])                 # only the command line says it
SANDBOX_FIRST = ("3", None, ["/proc/self/fd/3", "/bin/bash", "-c", f"python3 -m gov.cli.main release {FIRST_VERSION}"])


def chain(*processes):
    """A readable chain of ``processes``, nearest first; the last one gets pid 1 and parent 0 (W1-50's form)."""
    pids = [4000 - 10 * index for index in range(len(processes) - 1)] + [1]
    return [{"pid": pid, "ppid": parent, "comm": comm, "exe": exe, "cmdline": list(cmdline)}
            for (comm, exe, cmdline), pid, parent in zip(processes, pids, [*pids[1:], 0])]


# No Claude Code session, readable to the system's first process: the only chains that may release.
PLAIN_TERMINAL = chain(OWN_PROCESS, LOGIN_SHELL, INIT)
EDITOR_TERMINAL = chain(OWN_PROCESS, LOGIN_SHELL, EDITOR_NODE, EDITOR_SH, SYSTEMD)

# A Claude Code session among the ancestors (reason `session`): a few of the freeze lift's signs.
SESSION_ANCESTRIES = {
    "headless-p": chain(OWN_PROCESS, BASH_C, HEADLESS, LOGIN_SHELL, INIT),
    "operator-console": chain(OWN_PROCESS, BASH_C, CONSOLE, EDITOR_NODE, EDITOR_NODE, EDITOR_SH, INIT),
    "gov-launch": chain(OWN_PROCESS, BASH_C, LAUNCHED, GOV_LAUNCH, LOGIN_SHELL, INIT),
    "npm-install-shape": chain(OWN_PROCESS, BASH_C, NPM_INSTALL, LOGIN_SHELL, INIT),
    "only-the-command-line-says-it": chain(OWN_PROCESS, BASH_C, RENAMED_COMM, LOGIN_SHELL, INIT),
}


def _unreadable():
    broken = chain(OWN_PROCESS, LOGIN_SHELL, INIT)[:2]             # ends at a process whose parent was not read
    unlinked = chain(OWN_PROCESS, LOGIN_SHELL, INIT)
    unlinked[0]["ppid"] = 4242                                     # the next entry is not this process's parent
    return {
        "nothing-could-be-read": [],
        "the-chain-stops-before-the-first-process": broken,
        "an-entry-is-not-the-parent-of-the-one-before": unlinked,
        "the-sandbox-s-own-first-process": chain(OWN_PROCESS, BASH_C, SANDBOX_FIRST),
        "a-first-process-that-is-a-shell": chain(OWN_PROCESS, LOGIN_SHELL),
    }


# The chain cannot be read whole up to the system's first process (reason `ancestry`).
UNREADABLE_ANCESTRIES = _unreadable()


_RELEASE_DRIVER = r'''
import importlib, json, os, random, re, select, sys, threading

job = json.loads(sys.argv[1])
CODE = re.compile(r"RELEASE-\d{4}")

# Whatever the build prints (its own output, a tool it runs) goes to a log, never into the answer.
_log = os.open(job["log"], os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
os.dup2(_log, 1)
os.dup2(_log, 2)


def close(*fds):
    for fd in fds:
        try:
            os.close(fd)
        except (OSError, TypeError):
            pass


def one(function):
    kind, reply = job["terminal"], job["reply"]
    watch = feed = master = None
    opened = []
    if kind in ("pty", "pipe-in", "pipe-out"):
        master, slave = os.openpty()
        opened += [master, slave]
    if kind == "pty":
        in_fd, out_fd, watch, feed = slave, slave, master, master
    elif kind == "pipe-in":
        read_end, write_end = os.pipe()
        opened += [read_end, write_end]
        in_fd, out_fd, watch, feed = read_end, slave, master, write_end
    elif kind == "pipe-out":
        read_end, write_end = os.pipe()
        opened += [read_end, write_end]
        in_fd, out_fd, watch, feed = slave, write_end, read_end, master
    elif kind == "pipes":
        in_read, in_write = os.pipe()
        out_read, out_write = os.pipe()
        opened += [in_read, in_write, out_read, out_write]
        in_fd, out_fd, watch, feed = in_read, out_write, out_read, in_write
    else:
        in_fd, out_fd = os.open(os.devnull, os.O_RDONLY), os.open(os.devnull, os.O_WRONLY)
        opened += [in_fd, out_fd]

    seen = {"shown": b"", "before": None, "typed": None}
    done = threading.Event()

    def typist():
        while watch is not None:
            try:
                ready = select.select([watch], [], [], 0.05)[0]
            except (OSError, ValueError):
                return
            if ready:
                try:
                    data = os.read(watch, 65536)
                except OSError:
                    return
                if not data and kind != "pty":
                    return
                seen["shown"] += data
            found = CODE.search(seen["shown"].decode("utf-8", "replace"))
            if found and seen["typed"] is None:
                code = found.group(0)
                seen["before"] = seen["shown"]
                if reply == "right":
                    text = code + "\n"
                elif reply == "wrong":
                    text = "RELEASE-%04d\n" % ((int(code[8:]) + 1) % 10000)
                elif reply == "empty":
                    text = "\n"
                else:
                    text = None
                seen["typed"] = text or ""
                try:
                    if text is not None:
                        os.write(feed, text.encode())
                    elif feed == master:
                        os.write(feed, b"\x04")      # end of input on a terminal
                    else:
                        os.close(feed)
                except OSError:
                    pass
            if done.is_set() and not ready:
                return

    outcome = {}

    def call():
        try:
            value = function(job["root"], job["version"], ancestry=job["ancestry"], terminal=(in_fd, out_fd))
            outcome.update(status="released", result=value)
        except TypeError as error:
            if "ancestry" in str(error) or "terminal" in str(error) or "argument" in str(error):
                outcome.update(status="missing", detail=f"the function does not take the specification's parameters: {error}")
            else:
                outcome.update(status="crash", detail=repr(error))
        except Exception as error:
            if type(error).__name__ == "GovError":
                outcome.update(status="refused", error={"code": getattr(error, "code", ""),
                                                        "message": getattr(error, "message", str(error)),
                                                        "details": getattr(error, "details", {})})
            else:
                import traceback
                outcome.update(status="crash", detail=traceback.format_exc()[-3000:])
        except BaseException as error:
            outcome.update(status="crash", detail=repr(error))

    watcher = threading.Thread(target=typist, daemon=True)
    worker = threading.Thread(target=call, daemon=True)
    watcher.start()
    worker.start()
    worker.join(job["limit"])
    hung = worker.is_alive()
    done.set()
    watcher.join(2)
    if hung:
        outcome = {"status": "hang", "detail": "the function was still running %s s after it was called" % job["limit"]}
    shown = seen["shown"].decode("utf-8", "replace")
    before = (seen["before"] if seen["before"] is not None else seen["shown"]).decode("utf-8", "replace")
    outcome.update(shown=shown, shown_before_reply=before, typed=seen["typed"])
    if not hung:
        close(*opened)
    return outcome, hung


def answer(runs):
    with open(job["answer"], "w", encoding="utf-8") as handle:
        handle.write(json.dumps(runs, default=str))


def main():
    try:
        function = getattr(importlib.import_module(job["module"]), job["function"])
    except (ImportError, AttributeError) as error:
        answer([{"status": "missing", "detail": repr(error)}])
        os._exit(0)
    runs = []
    for _ in range(job["runs"]):
        if job["seed"] is not None:
            random.seed(job["seed"])
        outcome, hung = one(function)
        runs.append(outcome)
        if hung:
            break
    answer(runs)
    os._exit(0)                  # a function that still waits must not keep the process


main()
'''


@dataclass(frozen=True)
class SeamRun:
    """One call of ``_release_test``."""
    status: str                 # released | refused | missing | hang | crash
    result: object = None       # what the function returned
    error: dict = field(default_factory=dict)   # the GovError: code, message, details
    shown: str = ""             # everything that came out of the function's terminal output (typed text is echoed)
    shown_before_reply: str = ""
    typed: str | None = None    # what was typed back; None when no code was shown
    detail: str = ""
    log: str = ""               # what the driver's own standard output and error received

    @property
    def codes(self):
        """The codes shown before anything was typed."""
        return RELEASE_CODE.findall(self.shown_before_reply)

    @property
    def message(self):
        return str(self.error.get("message", ""))

    @property
    def reason(self):
        details = self.error.get("details")
        return details.get("reason") if isinstance(details, dict) else None

    def describe(self):
        return (f"status={self.status} result={self.result!r} error={self.error!r} typed={self.typed!r} "
                f"shown={self.shown[:400]!r} {self.detail}\nlog (last part):\n{self.log[-2000:]}")

    def as_run(self, version):
        """The call as a ``Run`` of ``gov release <version>``: exit 0 when it released, 1 otherwise."""
        return Run(("release", version), 0 if self.status == RELEASED else 1,
                   json.dumps(self.result, default=str) if self.status == RELEASED else "", self.describe())


def drive_release(root, sandbox, version, ancestry=None, terminal=PTY, reply=RIGHT, role=None, ticket=None, runs=1,
                  seed=None, limit=None):
    """Call ``_release_test`` ``runs`` times in one new process; a list of ``SeamRun``.

    ``ancestry`` None is ``PLAIN_TERMINAL``: the function is always handed a planted chain and a planted terminal.
    ``role`` / ``ticket``: GOV_ROLE / GOV_TICKET set in the process environment to that value (the empty value
    included); None leaves it absent. ``seed`` seeds Python's ``random`` before each call. A function that is not
    built, or does not take the specification's parameters, gives ``status == "missing"``.
    """
    root = Path(root)
    assert REPO_ROOT.resolve() not in (root.resolve(), *root.resolve().parents), \
        f"refusing to release in {root}: it is this repository"
    env = gov_environment(sandbox)
    assert "GOV_ROLE" not in env and "GOV_TICKET" not in env
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    limit = GOV_TIMEOUT_S if limit is None else limit
    folder = Path(sandbox.tmpdir)
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"release-seam-{os.getpid()}-{len(list(folder.glob('release-seam-*.answer')))}"
    answer, log = folder / f"{stem}.answer", folder / f"{stem}.log"
    job = {"module": RELEASE_MODULE, "function": RELEASE_FUNCTION, "root": str(root), "version": version,
           "ancestry": PLAIN_TERMINAL if ancestry is None else ancestry, "terminal": terminal, "reply": reply,
           "runs": runs, "seed": seed, "limit": limit, "answer": str(answer), "log": str(log)}
    try:
        done = subprocess.run([sys.executable, "-c", _RELEASE_DRIVER, json.dumps(job)], cwd=str(root), env=env,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=limit * runs + 60)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the release seam's driver did not end within {limit * runs + 60:.0f} s") from None
    logged = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    try:
        outcomes = json.loads(answer.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise AssertionError(f"the release seam's driver did not answer (exit code {done.returncode}):\n"
                             f"{done.stdout[-600:]}\n{done.stderr[-1500:]}\n{logged[-1500:]}") from None
    names = ("status", "result", "error", "shown", "shown_before_reply", "typed", "detail")
    return [SeamRun(**{name: outcome[name] for name in names if outcome.get(name) is not None}, log=logged)
            for outcome in outcomes]


def seam_built(run):
    """The seam exists and takes the specification's parameters; the case fails here until it does."""
    if run.status == MISSING:
        raise AssertionError(
            f"DEC-772 item 1 is not built: {RELEASE_MODULE}.{RELEASE_FUNCTION}(root, version, ancestry=None, "
            f"terminal=None) is missing or does not take those parameters ({run.detail}). The lead's specification "
            f"is in tests/acceptance/W2-16/README.md, \"Round 3\".")
    assert run.status not in (HANG, CRASH), f"the release seam did not end as a result or a refusal: {run.describe()}"
    return run


def release_through_the_seam(root, sandbox, version, **planted):
    """One call of the seam; the ``SeamRun``. The planted values are ``drive_release``'s."""
    return seam_built(drive_release(root, sandbox, version, **planted)[0])


def release_as_the_owner(root, sandbox, version):
    """The owner in person: a plain terminal's chain, a pseudo-terminal, the shown code typed back, GOV_ROLE and
    GOV_TICKET absent. The ``SeamRun``, whatever its status (``build_release`` judges it)."""
    return drive_release(root, sandbox, version)[0]


def assert_the_code_was_accepted(run, what):
    """Exactly one code ``RELEASE-<4 digits>`` was shown and it was typed back right: every caller check passed."""
    codes = set(run.codes)
    assert len(codes) == 1 and run.typed == codes.copy().pop() + "\n", (
        f"{what}: the owner's call did not get past the caller checks (one code shown and typed back right): "
        f"{run.describe()}")


def assert_no_traceback(run, what):
    told = "\n".join((run.message, run.detail, run.log))
    assert "Traceback" not in told, f"{what}: `gov release` ended with a traceback\n{run.describe()}"


def assert_the_build_refuses(repo, sandbox, version, why):
    """``gov release <version>`` as the owner in person, through the seam: refused by the build's own rule, and
    nothing written. The caller checks passed (the code shown and typed back right), so the refusal is the build's:
    code ``RELEASE_REFUSED``, a ``reason`` that is none of the caller checks' (``session``, ``ancestry``, ``role``,
    ``ticket``, ``terminal``, ``code``); no traceback; the whole snapshot unchanged. ``version`` None: no version
    given. Returns the ``SeamRun`` (DEC-772; Rewrite-Reason: DEC-772, P-R3-A)."""
    before = snapshot(repo)
    run = release_through_the_seam(repo, sandbox, version)
    after = snapshot(repo)
    assert run.status == REFUSED, f"`gov release {version}` built a release although {why}\n{run.describe()}"
    assert_no_traceback(run, why)
    assert_the_code_was_accepted(run, why)
    assert run.error.get("code") == RELEASE_REFUSED and run.reason not in REASONS, (
        f"`gov release {version}` was refused ({why}), but not by the build's own rule: code "
        f"{run.error.get('code')!r} (not {RELEASE_REFUSED}) or reason {run.reason!r} (one of the caller checks' "
        f"{REASONS})\n{run.describe()}")
    changed = snapshot_difference(before, after)
    assert not changed, f"a refused release ({why}) wrote or changed: {changed[:10]}\n{run.describe()}"
    return run


# --------------------------------------------------------------------------
# The real command on a pseudo-terminal, and the ancestry this suite runs under
# --------------------------------------------------------------------------

FIRST_PROCESSES = ("init", "systemd")


def read_own_ancestry():
    """This process's chain from ``/proc``, this process first (the reading W1-50's README describes)."""
    found, pid = [], os.getpid()
    while pid > 0 and len(found) < 1024:
        try:
            stat_text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace")
            words = Path(f"/proc/{pid}/cmdline").read_bytes().decode("utf-8", "replace").split("\0")
            parent = int(stat_text.rpartition(")")[2].split()[1])
        except (OSError, ValueError, IndexError):
            break
        try:
            exe = os.readlink(f"/proc/{pid}/exe")
        except OSError:
            exe = None
        found.append({"pid": pid, "ppid": parent, "comm": stat_text.partition("(")[2].rpartition(")")[0], "exe": exe,
                      "cmdline": words[:-1] if words and words[-1] == "" else words})
        pid = parent
    return found


def _is_session(process):
    """A Claude Code session by one sign (W1-50's README, "How a session is recognised")."""
    words = process.get("cmdline") or []
    named = [process.get("exe"), words[0] if words else None,
             next((word for word in words[1:] if not word.startswith("-")), None)]
    if process.get("comm") == "claude":
        return True
    return any(os.path.basename(word) == "claude" or "claude/versions/" in word
               or any("claude-code" in part or part == "@anthropic-ai" for part in word.split("/"))
               for word in named if word)


def why_this_suite_s_ancestry_refuses():
    """``"session"`` where a Claude Code session is among this process's ancestors, ``"ancestry"`` where the chain
    cannot be read whole up to process 1 (``init`` or ``systemd``), else None: a command this process starts has the
    same ancestors and itself (a Python process, no session) before them."""
    found = read_own_ancestry()
    if any(_is_session(process) for process in found):
        return "session"
    if not found:
        return "ancestry"
    last = found[-1]
    whole = (last["pid"] == 1 and last["ppid"] == 0 and last["comm"] in FIRST_PROCESSES
             and all(process["comm"] and process["cmdline"] for process in found)
             and all(process["ppid"] == parent["pid"] for process, parent in zip(found, found[1:])))
    return None if whole else "ancestry"


def run_gov_on_a_terminal(cwd, sandbox, *args, reply=RIGHT):
    """``gov <args>`` in ``cwd`` (``run_gov``'s environment: GOV_ROLE and GOV_TICKET absent) with its standard input,
    output and error on one pseudo-terminal; a code ``RELEASE-<4 digits>`` it shows is answered with ``reply``. The
    ``Run``: everything it wrote to the terminal is ``stdout``."""
    assert Path(cwd).resolve() != REPO_ROOT.resolve(), "no gov command of these tests runs in this worktree"
    env = gov_environment(sandbox)
    assert "GOV_ROLE" not in env and "GOV_TICKET" not in env
    master, slave = os.openpty()
    process = subprocess.Popen((sys.executable, "-m", "gov.cli.main", *args), cwd=str(cwd), env=env, stdin=slave,
                               stdout=slave, stderr=slave, close_fds=True)
    os.close(slave)
    shown, typed, deadline = b"", None, time.monotonic() + GOV_TIMEOUT_S
    try:
        while True:
            ready = select.select([master], [], [], 0.05)[0]
            data = b""
            if ready:
                try:
                    data = os.read(master, 65536)
                except OSError:          # every holder of the terminal's other side has closed it
                    data = b""
                shown += data
            found = RELEASE_CODE.search(shown.decode("utf-8", "replace"))
            if found and typed is None:
                code = found.group(0)
                typed = {RIGHT: code + "\n", EMPTY_LINE: "\n", END_OF_INPUT: "\x04",
                         WRONG: "RELEASE-%04d\n" % ((int(code[8:]) + 1) % 10000)}[reply]
                try:
                    os.write(master, typed.encode())
                except OSError:
                    pass
            if process.poll() is not None and not data:
                break
            if time.monotonic() > deadline:
                process.kill()
                process.wait()
                raise AssertionError(f"gov {' '.join(args)} on a terminal did not end within {GOV_TIMEOUT_S:.0f} s; "
                                     f"shown: {shown[-2000:]!r}")
    finally:
        os.close(master)
    return Run(tuple(args), process.returncode, shown.decode("utf-8", "replace"), f"typed back: {typed!r}")
