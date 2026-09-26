"""Git object access. The bridge reads Git objects, never the working tree (ARCHITECTURE.md section 0: "Git is the
only source of truth"). Every function here takes an explicit ``repo_root`` (defaulting to the repository containing
the current working directory) and shells out to the ``git`` binary -- no libgit2/pygit2 dependency, matching the
architecture's "thin, deterministic wrapper over Git" (section 4.2).

This module is deliberately generic: it knows nothing about which refs, paths or repository this is. Higher layers
(``view``, ``corpus``, ``exact``) supply those.
"""
from __future__ import annotations

import dataclasses
import functools
import subprocess
from pathlib import Path
from typing import Iterator, Optional, Sequence


class GitError(RuntimeError):
    """A git subprocess failed or returned something the caller cannot use."""


@functools.lru_cache(maxsize=64)
def _repo_root_cached(start: str) -> str:
    r = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode != 0:
        raise GitError(f"not a git repository (from {start}): {r.stderr.strip()}")
    return r.stdout.strip()


def repo_root(start: Optional[str] = None) -> str:
    """The absolute path of the repository containing ``start`` (default: the current working directory).

    BR-DAG-AMEND-R1-6: cached PER RESOLVED STARTING DIRECTORY, not per raw argument. This used to be
    ``functools.lru_cache`` directly on this function, keyed on ``start`` verbatim -- every bare ``repo_root()``
    call (every ``repo or repo_root()`` caller in this package passes exactly this, ``None``) shared the SAME cache
    key, so the FIRST bare caller's current working directory won that one slot for the rest of the process, and a
    later ``os.chdir`` in the same process was invisible to it (the same process-global-cache class of defect as
    ``govbridge.authority.classes``'s import-time config read, BR-DAG-AMEND-R1-12). Resolving ``start`` -- or the
    CURRENT working directory, read fresh at THIS call, when ``start`` is not given -- before the value ever
    reaches the cache means two ``os.chdir`` calls in one process resolve two distinct cache keys, each memoised
    independently, and a caller that always passes ``start`` (or ``repo=``) explicitly is completely unaffected
    either way."""
    key = str(Path(start).resolve()) if start is not None else str(Path.cwd())
    return _repo_root_cached(key)


def run_git(args: Sequence[str], repo: Optional[str] = None, input_bytes: Optional[bytes] = None,
            check: bool = True) -> subprocess.CompletedProcess:
    root = repo or repo_root()
    cmd = ["git", "-C", root, *args]
    r = subprocess.run(cmd, capture_output=True, input=input_bytes)
    if check and r.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed ({r.returncode}): {r.stderr.decode('utf-8', 'replace')}")
    return r


def rev_parse(ref: str, repo: Optional[str] = None) -> Optional[str]:
    """Resolve ``ref`` (which may itself be ``<rev>:<path>``) to the object id it names, or None if it cannot be
    resolved. Never raises for an absent ref -- absence is routine (a path missing at a commit, a branch not yet
    created in a fixture)."""
    r = run_git(["rev-parse", "--verify", "-q", ref], repo=repo, check=False)
    if r.returncode != 0:
        return None
    return r.stdout.decode().strip()


def resolve_commit(ref: str, repo: Optional[str] = None) -> Optional[str]:
    """Resolve ``ref`` to the commit id it points at (dereferencing tags/branches), or None."""
    return rev_parse(f"{ref}^{{commit}}", repo=repo)


def for_each_ref(pattern: str, repo: Optional[str] = None) -> list[tuple[str, str]]:
    """[(refname, commit)] for every ref matching a for-each-ref pattern, e.g. 'refs/heads/phase2/*'."""
    r = run_git(["for-each-ref", "--format=%(refname)%09%(objectname)", pattern], repo=repo)
    out = []
    for line in r.stdout.decode().splitlines():
        if not line:
            continue
        name, oid = line.split("\t")
        out.append((name, oid))
    return out


@dataclasses.dataclass(frozen=True)
class TreeEntry:
    mode: str
    type: str
    oid: str
    size: Optional[int]
    path: str


def ls_tree(commit: str, repo: Optional[str] = None) -> Iterator[TreeEntry]:
    """Every entry reachable from ``commit`` (git ls-tree -r -l -z): the whole tree, one row per tracked path."""
    r = run_git(["ls-tree", "-r", "-l", "-z", commit], repo=repo)
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, oid, size = meta.split()
        yield TreeEntry(
            mode=mode.decode(), type=typ.decode(), oid=oid.decode(),
            size=(int(size) if size != b"-" else None),
            path=path.decode("utf-8", "surrogateescape"),
        )


def ls_tree_path(commit: str, path: str, repo: Optional[str] = None) -> Optional[TreeEntry]:
    """The single tree entry for ``path`` at ``commit``, or None if it does not exist there."""
    r = run_git(["ls-tree", "-l", commit, "--", path], repo=repo, check=False)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    line = r.stdout.decode("utf-8", "surrogateescape").splitlines()[0]
    meta, entry_path = line.split("\t", 1)
    mode, typ, oid, size = meta.split()
    return TreeEntry(mode=mode, type=typ, oid=oid, size=(int(size) if size != "-" else None), path=entry_path)


def ls_tree_paths(commit: str, repo: Optional[str] = None) -> list[str]:
    """Every tracked path at ``commit`` (git ls-tree -r --name-only), for path-suffix resolution."""
    r = run_git(["ls-tree", "-r", "--name-only", "-z", commit], repo=repo)
    return [p.decode("utf-8", "surrogateescape") for p in r.stdout.split(b"\0") if p]


def ls_tree_count(commit: str, repo: Optional[str] = None) -> int:
    """Count of tracked paths at ``commit`` -- equivalent to ``git ls-tree -r <commit> | wc -l``, used by the
    coverage acceptance check."""
    r = run_git(["ls-tree", "-r", commit], repo=repo)
    if not r.stdout:
        return 0
    return r.stdout.count(b"\n")


class CatFileBatch:
    """A long-lived ``git cat-file --batch`` process for reading many blobs without one subprocess per blob
    (SO-04: 5,787 blobs read in seconds this way). Use as a context manager."""

    def __init__(self, repo: Optional[str] = None):
        self._root = repo or repo_root()
        self._proc: Optional[subprocess.Popen] = None

    def __enter__(self) -> "CatFileBatch":
        self._proc = subprocess.Popen(
            ["git", "-C", self._root, "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        )
        return self

    def __exit__(self, *exc):
        if self._proc is not None:
            try:
                self._proc.stdin.close()
            except Exception:
                pass
            self._proc.wait(timeout=10)
            self._proc = None

    def read(self, oid: str) -> Optional[bytes]:
        """The raw bytes of object ``oid``, or None if it does not exist in this batch stream's view."""
        assert self._proc is not None, "CatFileBatch must be used as a context manager"
        self._proc.stdin.write(oid.encode() + b"\n")
        self._proc.stdin.flush()
        header = self._proc.stdout.readline()
        if not header:
            raise GitError("cat-file --batch stream closed unexpectedly")
        parts = header.split()
        if len(parts) < 2 or parts[1] == b"missing":
            return None
        n = int(parts[2])
        data = self._proc.stdout.read(n)
        self._proc.stdout.read(1)  # trailing newline
        return data


def blob_at(commit: str, path: str, repo: Optional[str] = None) -> Optional[str]:
    """The blob id of ``path`` at ``commit``, or None if the path does not exist there."""
    return rev_parse(f"{commit}:{path}", repo=repo)


def read_blob(oid: str, repo: Optional[str] = None) -> Optional[bytes]:
    """The raw bytes of blob ``oid``, or None if it does not exist."""
    r = run_git(["cat-file", "-t", oid], repo=repo, check=False)
    if r.returncode != 0:
        return None
    r2 = run_git(["cat-file", "blob", oid], repo=repo)
    return r2.stdout


def read_path(commit: str, path: str, repo: Optional[str] = None) -> Optional[bytes]:
    """The raw bytes of ``path`` at ``commit``, or None if it does not exist there."""
    oid = blob_at(commit, path, repo=repo)
    if oid is None:
        return None
    return read_blob(oid, repo=repo)


def diff_tree(old_commit: str, new_commit: str, repo: Optional[str] = None) -> list[tuple[str, str, str, str]]:
    """[(status, path, old_oid, new_oid)] changed between two commits (git diff-tree -r --no-renames), used by
    incremental freshness (ARCHITECTURE.md section 3)."""
    r = run_git(["diff-tree", "-r", "--no-renames", "-z",
                 "--format=", old_commit, new_commit], repo=repo)
    out = []
    parts = [p for p in r.stdout.split(b"\0") if p]
    i = 0
    while i < len(parts):
        rec = parts[i].decode()
        # ":100644 100644 <old> <new> M"
        _, _, old_oid, new_oid, status = rec.lstrip(":").split()
        path = parts[i + 1].decode("utf-8", "surrogateescape")
        out.append((status, path, old_oid, new_oid))
        i += 2
    return out


def blame_last_change(path: str, line_start: int, line_end: int, commit: str = "HEAD",
                       repo: Optional[str] = None) -> Optional[tuple[str, str]]:
    """(commit, author-date-iso) of the most recent commit that changed lines [line_start, line_end] of ``path`` at
    ``commit``, or None if blame cannot resolve it (e.g. the path does not exist there)."""
    r = run_git(
        ["blame", "-L", f"{line_start},{line_end}", "--porcelain", commit, "--", path],
        repo=repo, check=False,
    )
    if r.returncode != 0 or not r.stdout:
        return None
    first_line = r.stdout.decode(errors="replace").splitlines()[0]
    sha = first_line.split()[0]
    date_r = run_git(["show", "-s", "--format=%aI", sha], repo=repo, check=False)
    date = date_r.stdout.decode().strip() if date_r.returncode == 0 else ""
    return sha, date


def git_grep(literal: str, commit: str, paths: Optional[Sequence[str]] = None,
             repo: Optional[str] = None) -> list[tuple[str, int, str]]:
    """[(path, line_no, line_text)] for a fixed-string search over ``commit`` (git grep -n -F)."""
    cmd = ["grep", "-n", "-F", "-I", "-e", literal, commit]
    if paths:
        cmd += ["--", *paths]
    r = run_git(cmd, repo=repo, check=False)
    if r.returncode not in (0, 1):  # 1 == no matches, not an error
        raise GitError(f"git grep failed: {r.stderr.decode('utf-8', 'replace')}")
    out = []
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        # "<commit>:<path>:<lineno>:<text>"
        try:
            _, rest = line.split(":", 1)
            path, lineno, text = rest.split(":", 2)
            out.append((path, int(lineno), text))
        except ValueError:
            continue
    return out
