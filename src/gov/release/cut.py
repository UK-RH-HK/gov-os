"""The cut of a release by code, patch or approved (W2-209, RELEASE-ON-BEHALF "The cut"): the record committed on a side
branch whose only parent is C, tagged ``v<version>`` (annotated, unsigned, local) and merged into ``w2/integrate`` with
an ordinary merge.

The record is built by ``gov.release.build`` exactly as ``gov release`` builds it; ``kind.json``, ``gates.json``,
``suite.json`` and ``NOTE.md`` are added beside ``manifest.json`` and ``manifest.sha256`` (the manifest's hash
covers the manifest only). The record's commit is made with git's plumbing and a temporary index, so the working
tree and the index are never the record's staging place; the folder ``build`` wrote is removed from the work tree
once its files are in the commit (the merge brings them back). A failure after the first ref was made removes the
refs this cut made. Nothing here contacts a remote.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from gov import release
from gov.release import ReleaseError

SIDE_BRANCH = "release/{version}"
ZERO = "0" * 40
_DEFAULT_IDENTITY = {"GIT_AUTHOR_NAME": "Gov OS release", "GIT_AUTHOR_EMAIL": "gov-release@localhost",
                     "GIT_COMMITTER_NAME": "Gov OS release", "GIT_COMMITTER_EMAIL": "gov-release@localhost"}


def _git(root: Path, *args: str, env: dict | None = None, stdin: str | None = None) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env, input=stdin)
    if done.returncode:
        raise ReleaseError(f"git {' '.join(args)}: {(done.stderr or done.stdout).strip()[:300]}")
    return done.stdout


def _env(root: Path, **more) -> dict:
    """The environment of the cut's git calls: the caller's, with an identity where git has none."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_INDEX") and key != "GIT_DIR"}
    for who in ("AUTHOR", "COMMITTER"):
        if subprocess.run(["git", "-C", str(root), "var", f"GIT_{who}_IDENT"], capture_output=True, env=env).returncode:
            env.update({k: v for k, v in _DEFAULT_IDENTITY.items() if who in k})
    env.update(more)
    return env


def commit_record(root: Path, version: str, c: str, files: dict[str, bytes], message: str) -> str:
    """The commit of ``files`` (record-relative names, written under ``docs/releases/<version>/``) on top of ``c``,
    made without touching the work tree's index: the commit's id."""
    folder = f"{release.RELEASES_REL}/{version}"
    with tempfile.TemporaryDirectory(prefix="gov-cut-") as scratch:
        env = _env(root, GIT_INDEX_FILE=str(Path(scratch) / "index"))
        _git(root, "read-tree", c, env=env)
        for name, data in files.items():
            blob = subprocess.run(["git", "-C", str(root), "hash-object", "-w", "--stdin"], input=data,
                                  capture_output=True, env=env)
            if blob.returncode:
                raise ReleaseError(f"git hash-object: {blob.stderr.decode('utf-8', 'replace').strip()[:300]}")
            _git(root, "update-index", "--add", "--cacheinfo", f"100644,{blob.stdout.decode().strip()},{folder}/{name}",
                 env=env)
        tree = _git(root, "write-tree", env=env).strip()
        return _git(root, "-c", "commit.gpgSign=false", "commit-tree", tree, "-p", c, "-F", "-", env=env,
                    stdin=message).strip()


def _checked_out(root: Path, branch: str) -> Path | None:
    """The work tree where ``branch`` is checked out, or None."""
    where = None
    for line in _git(root, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            where = Path(line[len("worktree "):])
        elif line == f"branch refs/heads/{branch}":
            return where
    return None


def merge_into_integration(root: Path, record: str, version: str) -> None:
    """An ordinary merge of ``record`` into ``w2/integrate``: where the branch is checked out (here or in another work
    tree) by ``git merge``; where it is not, by the same merge made with git's plumbing and a ref update."""
    branch = release.INTEGRATION_BRANCH
    message = f"Merge the record of release {version} into {branch}"
    env = _env(root)
    where = _checked_out(root, branch)
    if where is not None:
        try:
            _git(where, "-c", "commit.gpgSign=false", "merge", "-q", "-m", message, record, env=env)
        except ReleaseError:
            subprocess.run(["git", "-C", str(where), "merge", "--abort"], capture_output=True, env=env)
            raise
        return
    old = _git(root, "rev-parse", f"refs/heads/{branch}", env=env).strip()
    if subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", old, record], capture_output=True,
                      env=env).returncode == 0:
        new = record  # the branch is at the record's parent: the merge is a fast-forward
    else:
        tree = _git(root, "merge-tree", "--write-tree", branch, record, env=env).strip().splitlines()[0]
        new = _git(root, "-c", "commit.gpgSign=false", "commit-tree", tree, "-p", old, "-p", record, "-m", message,
                   env=env).strip()
    _git(root, "update-ref", f"refs/heads/{branch}", new, old, env=env)


def cut(root: Path, version: str, c: str, extras: dict[str, bytes], decision: str, kind: str) -> dict:
    """Build the record at ``c`` (the work tree's HEAD), add ``extras`` (name -> bytes), commit it on the side branch,
    tag it and merge it into ``w2/integrate``; ``{"record", "record_commit", "tag"}``. ``extras`` holds the files
    that need the build's manifest: they are given as a callable's result by the caller, see ``release._cut``."""
    root = Path(root)
    side, tag = SIDE_BRANCH.format(version=version), f"v{version}"
    made: list[tuple[str, str]] = []
    folder = root / release.RELEASES_REL / version
    try:
        built = release.build(root, version)
        record_files = {path.name: path.read_bytes() for path in sorted(built.iterdir())}
        record_files.update(extras(record_files) if callable(extras) else extras)
        shutil.rmtree(built)
        message = (f"Record of release {version} ({kind} release, cut under the owner's standing yes)\n\n"
                   f"The record of {version} built at {c}: its manifest, kind, gates, suite record and note.\n\n"
                   f"Role: orchestrator\nDecided-by: owner (standing, {decision})\nTask: release\n")
        commit = commit_record(root, version, c, record_files, message)
        _git(root, "update-ref", f"refs/heads/{side}", commit, ZERO)
        made.append(("branch", side))
        env = _env(root)
        _git(root, "-c", "tag.gpgSign=false", "tag", "-a", tag, "-m", f"Gov OS release {version}", commit, env=env)
        made.append(("tag", tag))
        merge_into_integration(root, commit, version)
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)
        for kind, name in reversed(made):
            subprocess.run(["git", "-C", str(root), "tag", "-d", name] if kind == "tag"
                           else ["git", "-C", str(root), "branch", "-D", name], capture_output=True)
        raise
    return {"record": f"{release.RELEASES_REL}/{version}", "record_commit": commit, "tag": tag}
