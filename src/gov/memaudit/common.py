"""The parts the three subcommands share: the usage error, git at a commit, whole-or-nothing JSON files, the set's
digest and the time stamp. Nothing here carries a question, a path or a file's text in a message (F1)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HEX40 = re.compile(r"[0-9a-f]{40}")


class UsageError(Exception):
    """A flag or value refused, or the sets root unusable: exit 4. The message is never printed."""


class LineRefused(Exception):
    """``say`` refused a line: the subcommand stops with exit 4 (the refusal is already printed)."""


class GitError(Exception):
    """git could not answer: the subcommand ends ``ERROR: GitError``, exit 4."""


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_OPTIONAL_LOCKS"] = "0"  # the repository is only read: no index refresh (its status stays as it was)
    env["LC_ALL"] = "C"
    return env


def git(repo, *args, ok=(0,)) -> bytes:
    """git's standard output as bytes; a code outside ``ok`` raises ``GitError`` (never git's text)."""
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=_env(), stdin=subprocess.DEVNULL)
    if done.returncode not in ok:
        raise GitError(done.returncode)
    return done.stdout


def git_code(repo, *args) -> int:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=_env(),
                          stdin=subprocess.DEVNULL).returncode


def toplevel(cwd=None) -> Path:
    try:
        out = git(cwd or os.getcwd(), "rev-parse", "--show-toplevel")
    except GitError:
        raise UsageError("repo") from None
    return Path(out.decode("utf-8", "replace").strip())


def resolve_commit(repo, rev: str) -> str:
    """``rev`` as 40 hex digits (``git rev-parse --verify <rev>^{commit}``); an unresolved value is a usage error."""
    if not isinstance(rev, str) or not rev or rev.startswith("-"):
        raise UsageError("commit")
    try:
        out = git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}").decode().strip()
    except GitError:
        raise UsageError("commit") from None
    if not HEX40.fullmatch(out):
        raise UsageError("commit")
    return out


def blob_at(repo, commit: str, path: str) -> bytes | None:
    """The bytes of ``path`` at ``commit``, or None when the commit holds no file there."""
    if git_code(repo, "cat-file", "-e", f"{commit}:{path}") != 0:
        return None
    if git(repo, "cat-file", "-t", f"{commit}:{path}").strip() != b"blob":
        return None
    return git(repo, "cat-file", "blob", f"{commit}:{path}")


def z_list(out: bytes) -> list[str]:
    return [x.decode("utf-8", "surrogateescape") for x in out.split(b"\0") if x]


def write_whole(folder: Path, name: str, data: dict) -> Path:
    """``folder/name`` written whole or not at all: a temporary name, synced, then renamed."""
    folder = Path(folder)
    tmp, final = folder / f".{name}.tmp", folder / name
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=1, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, final)
    return final


def read_json(path: Path):
    """The JSON of ``path``, or None when it is absent or not JSON."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def set_digest(hidden: Path) -> str:
    """``LC_ALL=C sha256sum *.yaml | sha256sum`` in the set's folder: the files ``*.yaml`` (flat, not ``dropped/``)
    in byte order of name, the sha256 of the lines ``<sha256 of the file>  <name>``."""
    hidden = Path(hidden)
    names = sorted((e.name for e in os.scandir(hidden) if e.name.endswith(".yaml") and e.is_file()),
                   key=lambda s: s.encode("utf-8", "surrogateescape")) if hidden.is_dir() else []
    text = "".join(f"{sha256_file(hidden / name)}  {name}\n" for name in names)
    return sha256_bytes(text.encode("utf-8", "surrogateescape"))
