"""Support code for the W2-17 acceptance tests: ``gov update <B>`` moves an adopted project from release A to B.

Public interfaces only: the ``gov`` command line (``gov update``, ``gov adapters generate``, ``gov doctor --json``,
``<common>/gov/bin/gov --version``), ``copier`` and ``git`` in temporary folders, and the files of the project
(its tree, ``governance/framework.lock``, ``.copier-answers.yml``, ``governance/updates/<B>.json``,
``<common>/gov/``). No module of the update, the install or the release code is imported by a test.

**The fixtures, as the owner makes them.** W2-16's support builds the stand-in Gov OS repository from single
named files of this worktree (``template/``, ``src/gov/``, ``pyproject.toml``, ``copier.yml``), builds each
release through the release seam as the owner in person (``build_release``), and creates a project with
``copier copy --vcs-ref vA --trust`` (its Copier task, ``gov release --lock-from``, writes the lock with this
worktree's gov). On top of it this module:

- gives the stand-in release A (``A`` = 0.9.0, ``pyproject.toml`` 0.9.0) with the files ``W2-17 files`` below,
  then changes ``template/`` for release B (``B`` = 0.9.1, ``pyproject.toml`` 0.9.1): one shipped file updated,
  one added, one removed, one overlay file changed, one skill under ``.rulesync/skills/`` changed, one file the
  project also changes in other lines (a clean merge) and one in the same line (a conflict); each release is
  tagged ``v<version>`` on its record commit;
- adopts a project at ``vA``, runs ``gov adapters generate`` in it (rulesync), makes the project's own local
  changes, and commits them all.

Every ``gov`` the tests run is this worktree's (``python -m gov.cli.main`` with ``PYTHONPATH`` this worktree's
``src/``), but the pinned gov the update installs (``<common>/gov/bin/gov``), which the tests run without
``PYTHONPATH``. Every run has a fake ``HOME``; ``PYTHONUSERBASE`` stays the real user base so the packages gov
needs import; ``GOV_REBUILD_LOCK`` is a file of the case's own sandbox (the machine's rebuild lock is shared).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import site
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W2-16", _HERE.parent / "W1-39", _HERE.parent / "W1-07"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_16_support as w216  # noqa: E402

REPO_ROOT = w216.REPO_ROOT
SRC = w216.SRC
git = w216.git
make_sandbox = w216.make_sandbox
sha256_bytes = w216.sha256_bytes
commit_all = w216.commit_all
head = w216.head
porcelain_paths = w216.porcelain_paths

# --- what the ticket and the interface fix ------------------------------------
A, B = "0.9.0", "0.9.1"                      # release versions; each pyproject.toml declares the same CLI version
TAG_A, TAG_B = f"v{A}", f"v{B}"
LOCK_REL = "governance/framework.lock"
ANSWERS_REL = ".copier-answers.yml"
OVERLAY = "governance/project"
RECORD_REL = f"governance/updates/{B}.json"
RELEASE_COPY_DIR = f"governance/updates/{B}/release"
OUTCOMES = ("updated", "added", "removed", "merged", "kept", "conflicts", "overlay")
UPDATE_REFUSED, UPDATE_FAILED = "UPDATE_REFUSED", "UPDATE_FAILED"
CONFLICT_MARKER = b"<<<<<<<"

# --- the W2-17 files (paths as a project sees them; the stand-in holds them under template/) ----------------
KIT = "governance/kernel/w2-17"
UPDATED = f"{KIT}/updated.md"                # B changes it; the project does not
ADDED = f"{KIT}/added.md"                    # B adds it
REMOVED = f"{KIT}/removed.md"                # B removes it
KEPT = f"{KIT}/kept.md"                      # the project changes it; B does not
MERGED = f"{KIT}/merged.md"                  # both change it, in different lines
CONFLICT = f"{KIT}/conflict.md"              # both change it, in the same line
UNCHANGED = f"{KIT}/unchanged.md"            # neither changes it
OVERLAY_CHANGED = f"{OVERLAY}/path-map.yaml"  # B changes it; the project does not
OVERLAY_LOCAL = f"{OVERLAY}/test-map.yaml"   # the project changes it; B does not
SKILL_NAME = "audit"
SKILL = f".rulesync/skills/{SKILL_NAME}/SKILL.md"   # B changes it; the project does not
SKILL_GENERATED = f".claude/skills/{SKILL_NAME}/SKILL.md"
SKILL_MARKER = "W2-17 marker: a line release B adds to the audit skill."
OWN_FILE = "openspec/specs/w2-17-own.md"     # the project's own file, in no release

EXPECTED = {UPDATED: "updated", SKILL: "updated", ADDED: "added", REMOVED: "removed", KEPT: "kept",
            MERGED: "merged", CONFLICT: "conflicts", OVERLAY_CHANGED: "overlay"}
LOCALLY_CHANGED = (KEPT, MERGED, CONFLICT, OVERLAY_LOCAL)


def _lines(label, count, changes=None):
    changes = changes or {}
    return "".join(f"{changes.get(n, f'{label} line {n}: as release A ships it')}\n" for n in range(1, count + 1))


A_FILES = {
    UPDATED: "W2-17: a shipped file, release A's form\n",
    REMOVED: "W2-17: a shipped file that release B removes\n",
    KEPT: _lines("kept", 6),
    MERGED: _lines("merged", 14),
    CONFLICT: _lines("conflict", 6),
    UNCHANGED: "W2-17: a shipped file neither release B nor the project changes\n",
}
B_CHANGES = {
    UPDATED: "W2-17: a shipped file, release B's form\n",
    ADDED: "W2-17: a shipped file release B adds\n",
    MERGED: _lines("merged", 14, {12: "merged line 12: changed by release B"}),
    CONFLICT: _lines("conflict", 6, {3: "conflict line 3: changed by release B"}),
}
B_REMOVES = (REMOVED,)
PROJECT_CHANGES = {
    KEPT: _lines("kept", 6, {2: "kept line 2: changed by the project"}),
    MERGED: _lines("merged", 14, {2: "merged line 2: changed by the project"}),
    CONFLICT: _lines("conflict", 6, {3: "conflict line 3: changed by the project"}),
    OWN_FILE: "W2-17: the project's own file\n",
}
MERGED_RESULT = _lines("merged", 14, {2: "merged line 2: changed by the project",
                                     12: "merged line 12: changed by release B"})

GOV_TIMEOUT_S = 900.0        # an update builds a wheel, a virtual environment and two renders: a wait, not a promise
SHA256_RE = re.compile(r"[0-9a-f]{64}")


def sha256(path):
    return sha256_bytes(Path(path).read_bytes())


# --------------------------------------------------------------------------
# The tools the update runs
# --------------------------------------------------------------------------

def _tool_folder(name, fallback):
    found = shutil.which(name)
    if found:
        return str(Path(found).parent)
    return str(fallback) if Path(fallback, name).exists() else None


def tool_path():
    """The folders of copier, rulesync and node (rulesync's), then this Python's, then the caller's PATH."""
    home = Path.home()
    folders = []
    nodes = sorted(home.glob(".nvm/versions/node/v22*/bin"))
    if nodes:
        folders.append(str(nodes[-1]))
    for name in ("copier", "rulesync"):
        folder = _tool_folder(name, home / ".local/bin")
        if folder:
            folders.append(folder)
    folders.append(str(Path(sys.executable).parent))
    folders += os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
    unique = []
    for folder in folders:
        if folder and folder not in unique:
            unique.append(folder)
    return unique


def user_base():
    return os.environ.get("PYTHONUSERBASE") or site.getuserbase()


def environment(sandbox, first=(), with_src=True):
    """A fake HOME and TMPDIR, the real user base, this case's rebuild lock, the tools on PATH (``first`` before)."""
    env = {
        "PATH": os.pathsep.join([*map(str, first), *tool_path()]),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONUSERBASE": user_base(),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "GOV_REBUILD_LOCK": str(Path(sandbox.elsewhere) / "rebuild.lock"),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W2-17 tests", "GIT_AUTHOR_EMAIL": "w2-17@example.invalid",
        "GIT_COMMITTER_NAME": "W2-17 tests", "GIT_COMMITTER_EMAIL": "w2-17@example.invalid",
    }
    if with_src:
        env["PYTHONPATH"] = str(SRC)
    return env


@dataclass(frozen=True)
class Run:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + "\n" + self.stderr

    def describe(self):
        return (f"{' '.join(map(str, self.argv))}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-5000:]}\n"
                f"stderr:\n{self.stderr[-5000:]}")

    def envelope(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON document (`--json`)\n{self.describe()}") from None
        assert isinstance(data, dict), f"standard output is not a JSON object\n{self.describe()}"
        return data

    def result(self):
        envelope = self.envelope()
        assert envelope.get("ok") is True and isinstance(envelope.get("result"), dict), (
            f"the command did not succeed with a result\n{self.describe()}")
        return envelope["result"]

    def error(self):
        envelope = self.envelope()
        error = envelope.get("error")
        assert envelope.get("ok") is False and isinstance(error, dict), (
            f"the command did not end with an error envelope\n{self.describe()}")
        return error


def _run(argv, cwd, env, timeout=GOV_TIMEOUT_S):
    assert Path(cwd).resolve() != REPO_ROOT.resolve(), "no command of these tests runs in this worktree"
    try:
        done = subprocess.run([str(a) for a in argv], cwd=str(cwd), env=env, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{' '.join(map(str, argv))} did not end within {timeout:.0f} s") from None
    return Run(tuple(map(str, argv)), done.returncode, done.stdout, done.stderr)


def gov(project, sandbox, *args, first=()):
    """``gov <args>`` in the project, with this worktree's code."""
    return _run((sys.executable, "-m", "gov.cli.main", *args), project, environment(sandbox, first))


def update(project, sandbox, *args, json_form=True, first=()):
    """``gov update <B> [args] [--json]`` in the project."""
    extra = ("--json",) if json_form else ()
    return gov(project, sandbox, "update", B, *args, *extra, first=first)


def pinned(project, sandbox, *args):
    """``<common>/gov/bin/gov <args>`` in the project, without PYTHONPATH (the pin's own code)."""
    binary = common_dir(project) / "gov" / "bin" / "gov"
    assert binary.exists(), f"no pinned gov at {binary}"
    return _run((binary, *args), project, environment(sandbox, with_src=False))


def failing_rulesync(folder):
    """A ``rulesync`` in ``folder`` that exits 1, to be put first on PATH."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "rulesync"
    path.write_text("#!/bin/sh\necho 'rulesync: failing on purpose (W2-17 rollback case)' >&2\nexit 1\n",
                    encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return folder


# --------------------------------------------------------------------------
# The stand-in source with releases A and B
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Source:
    repo: Path
    first: object            # W2-16's ReleaseRecord of A
    second: object           # W2-16's ReleaseRecord of B

    @property
    def manifest_b(self):
        return json.loads(self.second.manifest_bytes)

    @property
    def manifest_b_sha256(self):
        return self.second.manifest_hash

    def template_bytes(self, tag, rel):
        """The bytes of ``template/<rel>`` at ``tag``, or None."""
        done = subprocess.run(["git", "-C", str(self.repo), "show", f"{tag}:template/{rel}"], capture_output=True)
        return done.stdout if done.returncode == 0 else None

    def shipped(self, tag):
        """Every path under ``template/`` at ``tag``, as a project sees it."""
        listing = git(self.repo, "ls-tree", "-r", "--name-only", tag, "--", "template").splitlines()
        return sorted(item[len("template/"):] for item in listing if item)


def _set_version(repo, version):
    path = Path(repo) / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    changed = re.sub(r'(?m)^version\s*=\s*"[^"]*"', f'version = "{version}"', text, count=1)
    assert changed != text or f'version = "{version}"' in text, "pyproject.toml has no version line"
    path.write_text(changed, encoding="utf-8")


def _write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_source(destination, sandbox):
    """The stand-in Gov OS repository holding releases A and B, each tagged on its record commit."""
    repo = w216.build_gov_os_repository(destination)
    template = Path(repo) / "template"
    for rel, text in A_FILES.items():
        _write(template, rel, text)
    _set_version(repo, A)
    commit_all(repo, "release A's template")
    first = w216.build_release(repo, sandbox, A, tag=TAG_A)
    for rel, text in B_CHANGES.items():
        _write(template, rel, text)
    for rel in B_REMOVES:
        (template / rel).unlink()
    path_map = template / OVERLAY_CHANGED
    path_map.write_text(path_map.read_text(encoding="utf-8") + "# W2-17: a line release B adds to the overlay.\n",
                        encoding="utf-8")
    skill = template / SKILL
    skill.write_text(skill.read_text(encoding="utf-8").rstrip("\n") + f"\n\n{SKILL_MARKER}\n", encoding="utf-8")
    _set_version(repo, B)
    commit_all(repo, "release B's template")
    second = w216.build_release(repo, sandbox, B, tag=TAG_B)
    return Source(Path(repo), first, second)


# --------------------------------------------------------------------------
# The adopted project
# --------------------------------------------------------------------------

def adopt(copier_bin, source_repo, destination, sandbox, tag=TAG_A, local_changes=True):
    """``copier copy`` at ``tag``, ``gov adapters generate``, the project's local changes; all committed."""
    project = w216.create_project(copier_bin, sandbox, source_repo, destination, tag)
    done = gov(project, sandbox, "adapters", "generate", "--json")
    assert done.returncode == 0, f"`gov adapters generate` failed in the adopted project\n{done.describe()}"
    commit_all(project, "the adapters, generated")
    if local_changes:
        for rel, text in PROJECT_CHANGES.items():
            _write(project, rel, text)
        local = Path(project) / OVERLAY_LOCAL
        local.write_text(local.read_text(encoding="utf-8") + "# W2-17: the project's own line in its overlay.\n",
                         encoding="utf-8")
        commit_all(project, "the project's own changes")
    assert not porcelain_paths(project), f"the adopted project is not clean: {porcelain_paths(project)}"
    return Path(project)


def copy_project(origin, destination):
    """A copy of a temporary project (``.git`` with it), never of this repository."""
    return w216.clone_folder(origin, destination)


def common_dir(project):
    return Path(git(project, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())


def pin_state(project):
    """Every entry under ``<common>/gov/`` (links by target, files by sha256), or None where it is absent."""
    root = common_dir(project) / "gov"
    if not os.path.lexists(root):
        return None
    found = {}
    for path in sorted([root, *root.rglob("*")]):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            found[rel] = ("link", os.readlink(path))
        elif path.is_file():
            found[rel] = ("file", sha256(path))
        else:
            found[rel] = ("folder",)
    return found


def tree_state(project):
    """Every file, link and folder outside ``.git`` (bytes and mode), and HEAD."""
    root = Path(project)
    entries = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            entries[rel] = ("link", os.readlink(path))
        elif stat.S_ISDIR(info.st_mode):
            entries[rel + "/"] = ("folder", stat.S_IMODE(info.st_mode))
        else:
            entries[rel] = (sha256(path), stat.S_IMODE(info.st_mode))
    return {"files": entries, "head": head(project)}


def tree_difference(before, after):
    changed = ["HEAD"] if before["head"] != after["head"] else []
    for rel in sorted(set(before["files"]) | set(after["files"])):
        if before["files"].get(rel) != after["files"].get(rel):
            changed.append(rel)
    return changed


def overlay_hashes(project):
    root = Path(project) / OVERLAY
    return {path.relative_to(project).as_posix(): sha256(path) for path in sorted(root.rglob("*")) if path.is_file()}


def read_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def lock_release(project):
    data = read_yaml(Path(project) / LOCK_REL)
    return data.get("release") if isinstance(data, dict) else None


def outcome_lists(files):
    """``{outcome: set(paths)}`` from a report's or record's ``files``; paths as a project sees them."""
    assert isinstance(files, dict), f"`files` is not a map of outcomes: {files!r}"
    found = {}
    for outcome in OUTCOMES:
        items = files.get(outcome, [])
        assert isinstance(items, list), f"`files.{outcome}` is not a list: {items!r}"
        found[outcome] = {str(item).removeprefix("./").removeprefix("template/") for item in items}
    return found


def assert_outcomes(files, what):
    """Each W2-17 path under its expected outcome and no other; the files neither side changed under none."""
    lists = outcome_lists(files)
    wrong = []
    for rel, outcome in EXPECTED.items():
        where = sorted(name for name, items in lists.items() if rel in items)
        if where != [outcome]:
            wrong.append(f"{rel}: expected under {outcome!r}, found under {where}")
    for rel in (UNCHANGED, OWN_FILE, OVERLAY_LOCAL):
        where = sorted(name for name, items in lists.items() if rel in items)
        if where:
            wrong.append(f"{rel}: release B does not change it, so it has no outcome; found under {where}")
    assert not wrong, f"{what}: the files are not each under their outcome:\n" + "\n".join(wrong) + \
        f"\nfiles: {json.dumps(files, indent=1)[:4000]}"


APPLIED = re.compile(r"\b(update (was |has been |is )?applied|applied the update)\b", re.I)
NEGATION = re.compile(r"\b(not|no|never|nothing)\b[^.;:]{0,20}$", re.I)


def assert_never_applied(run, what):
    """The run's envelope is not a success and its output never says the update was applied (a negated phrase,
    "the update was not applied", is no claim)."""
    claims = [found.group(0) for found in APPLIED.finditer(run.output)
              if not NEGATION.search(run.output[max(0, found.start() - 30):found.start()])]
    assert run.envelope().get("ok") is False and not claims, (
        f"{what}: the output says the update was applied ({claims})\n{run.describe()}")
