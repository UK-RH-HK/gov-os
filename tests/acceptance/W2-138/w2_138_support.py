"""The planted stores of the W2-138 acceptance tests, the link, the command line in process and the line oracle.

- ``make_stores(base)``: one git repository, two commits, and two store folders as the integration store keeps them
  (W2-116): detached worktrees of the repository, ``a`` at the first commit (C1) and ``b`` at the second (C2), each
  with its lexical index and record store built in place (``lexical.refresh``, ``store.load``). The caller replaces
  the secret filter, as the unit tests do. No vectors, no model.
- ``link_to`` / ``switch``: a symbolic link to a store folder, and its atomic switch (a new link renamed over the old,
  as ``gov rebuild --integration`` switches).
- ``gov(capsys, *argv)``: ``gov.cli.main.main`` in this process, its stdout and stderr captured. In process so the
  stand-ins of ``conftest.py`` (no reranker, no semantic route) hold for the command line too.
- ``lines_at(folder, commit, path, first, last)``: the oracle of S4, from git alone, never from the code under test
  (README, "The byte rule").
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if importlib.util.find_spec("gov") is None:  # a PYTHONPATH given names the tree under test; else this one
    sys.path.insert(0, str(REPO / "src"))

REGISTER = "decisions/REGISTER.md"
ALPHA, CRLF, TAIL, LONG, GAMMA, DELTA = ("notes/alpha.md", "notes/crlf.md", "notes/tail.md", "notes/long.md",
                                        "notes/gamma.md", "notes/delta.md")

# A note long enough to be cut into several chunks under one parent (W2-131's filler): a hit on its last chunk is
# expanded to the parent at the default budget, and sent alone at a small one.
FILLER = "".join(f"- **Row {n}:** the harbour keeps its ledger of lanterns in order, shelf by shelf, row {n}.\n"
                 for n in range(1, 41))
ALPHA_C1 = ("# The alpha note\n\nThe alpha note opens the harbour ledger.\n\n" + FILLER
            + "- **Last:** the quillwort clause closes the alpha note.\n")
# C2 puts two lines before everything, so every line of the alpha note moves down by two in the second store
ALPHA_C2 = "A preface the second commit adds.\n\n" + ALPHA_C1
CRLF_TEXT = b"# The crlf note\r\n\r\nThe bergamot lantern hangs by the door.\r\nA second line ends it.\r\n"
TAIL_TEXT = b"# The tail note\n\nThe marjoram lantern has no final newline."
LONG_LINE = "".join(f"saffron cell {n} " for n in range(1, 400))  # one line over 4,000 characters (W2-135's cut)
LONG_TEXT = f"# The long note\n\n{LONG_LINE}\nThe lantern line after it.\n"
GAMMA_C1 = "# The gamma note\n\nThe fennel lantern is kept in the gamma drawer.\n"
GAMMA_C2 = "# The gamma note\n\nThe fennel lantern is kept in the gamma drawer.\nThe second commit adds a line.\n"
DELTA_TEXT = "# The delta note\n\nThe second commit's lantern, only in the second store.\n"
REGISTER_TEXT = ("# Decision register\n\n"
                 "### DEC-101 — The juniper rule\n- **Status:** ACCEPTED\n"
                 "- **Decision:** the juniper lantern stays lit.\n")

FILES_C1 = {
    ".gitignore": ".gov-runtime/\n",
    # the command line loads the configuration first (DEC-185): a path map with its one required key, no namespace
    "governance/project/path-map.yaml": f"namespaces: {{}}\ndecision_register: {REGISTER}\n",
    REGISTER: REGISTER_TEXT,
    ALPHA: ALPHA_C1,
    CRLF: CRLF_TEXT,
    TAIL: TAIL_TEXT,
    LONG: LONG_TEXT,
    GAMMA: GAMMA_C1,
}
FILES_C2 = {ALPHA: ALPHA_C2, GAMMA: GAMMA_C2, DELTA: DELTA_TEXT}

_GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
            "GIT_AUTHOR_DATE": "2026-11-07T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-07T12:00:00Z"}


def git(folder: Path, *args: str) -> bytes:
    done = subprocess.run(["git", "-C", str(folder), "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                           *args], capture_output=True, env={**_GIT_ENV, "HOME": str(folder)}, check=False)
    if done.returncode:
        raise AssertionError(f"git {' '.join(args)} failed in {folder}: {done.stderr.decode(errors='replace')}")
    return done.stdout


def head(folder: Path) -> str:
    return git(folder, "rev-parse", "HEAD").decode().strip()


def _write(root: Path, files: dict) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_bytes(text.encode("utf-8"))


def build(folder: Path) -> Path:
    """The lexical index and the record store of ``folder``, built in place at its HEAD."""
    from gov import store
    from gov.retrieval import lexical

    lexical.refresh(folder)
    store.load(folder)
    return folder


@dataclass(frozen=True)
class Stores:
    repo: Path
    a: Path    # a store folder at c1
    b: Path    # a store folder at c2
    c1: str
    c2: str


def make_stores(base: Path) -> Stores:
    """The repository and its two store folders (module docstring)."""
    repo = base / "repo"
    repo.mkdir(parents=True)
    _write(repo, FILES_C1)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "C1")
    c1 = head(repo)
    a = base / "halves" / "store-a"
    a.parent.mkdir(parents=True, exist_ok=True)
    git(repo, "worktree", "add", "-q", "--detach", str(a), c1)
    _write(repo, FILES_C2)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "C2")
    c2 = head(repo)
    b = base / "halves" / "store-b"
    git(repo, "worktree", "add", "-q", "--detach", str(b), c2)
    build(a)
    build(b)
    return Stores(repo, a.resolve(), b.resolve(), c1, c2)


def link_to(where: Path, target: Path) -> Path:
    where.parent.mkdir(parents=True, exist_ok=True)
    where.symlink_to(target)
    return where


def switch(link: Path, target: Path) -> None:
    """The link switched to ``target`` at once: a new link renamed over it."""
    temporary = link.with_name(link.name + ".next")
    if os.path.lexists(temporary):
        temporary.unlink()
    temporary.symlink_to(target)
    os.replace(temporary, link)


# --------------------------------------------------------------------------
# The command line, in process
# --------------------------------------------------------------------------

@dataclass
class Run:
    argv: tuple
    code: int
    out: str
    err: str

    def envelope(self) -> dict:
        try:
            value = json.loads(self.out)
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}

    @property
    def ok(self) -> bool:
        return self.code == 0 and self.envelope().get("ok") is True

    @property
    def result(self) -> dict:
        value = self.envelope().get("result")
        return value if isinstance(value, dict) else {}

    @property
    def error(self) -> dict:
        value = self.envelope().get("error")
        return value if isinstance(value, dict) else {}

    def describe(self, tail: int = 3000) -> str:
        return (f"gov {' '.join(map(str, self.argv))}\nexit code {self.code}\nstdout:\n{self.out[:tail]}\n"
                f"stderr:\n{self.err[-tail:]}")


def gov(capsys, *argv) -> Run:
    from gov.cli import main as cli

    capsys.readouterr()  # nothing printed before belongs to this call
    try:
        code = cli.main([str(arg) for arg in argv])
    except SystemExit as stop:  # a usage error
        code = stop.code if isinstance(stop.code, int) else 2
    captured = capsys.readouterr()
    return Run(tuple(argv), code, captured.out, captured.err)


def search(capsys, question: str, *options) -> Run:
    """``gov retrieve --json <options> <question>``."""
    return gov(capsys, "retrieve", "--json", *options, question)


def store_of(run: Run) -> dict:
    value = run.result.get("store")
    assert isinstance(value, dict), (f"the result names no store: result.store is {value!r}; the result's keys: "
                                     f"{sorted(run.result)}\n{run.describe(800)}")
    return value


def names_commit(text: str, commit: str) -> bool:
    """``text`` names ``commit``: its full id or at least its first 12 hex digits."""
    return commit[:12] in text


# --------------------------------------------------------------------------
# The oracle of S4
# --------------------------------------------------------------------------

def blob_lines(folder: Path, commit: str, path: str) -> list[bytes]:
    """The lines of ``path`` at ``commit``, as git holds the file's bytes (``git cat-file blob``: no filter, no
    decoding): each line its bytes up to and including its LF (a CRLF line keeps both bytes); the last line as it
    is, with no newline added where the file has none."""
    blob = git(folder, "cat-file", "blob", f"{commit}:{path}")
    pieces = blob.split(b"\n")
    lines = [piece + b"\n" for piece in pieces[:-1]]
    if pieces[-1]:
        lines.append(pieces[-1])
    return lines


def lines_at(folder: Path, commit: str, path: str, first: int, last: int) -> bytes:
    """Lines ``first`` to ``last`` (1-based, both inclusive) of ``path`` at ``commit``, joined as they are."""
    lines = blob_lines(folder, commit, path)
    assert 1 <= first <= last <= len(lines), (
        f"{path}@{commit[:12]} has {len(lines)} lines; the item names lines {first}-{last}")
    return b"".join(lines[first - 1:last])
