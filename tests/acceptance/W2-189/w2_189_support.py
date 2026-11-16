"""The planted adopted repository of the W2-189 acceptance tests, its store, the later commits and the command line.

- ``plant(base, ...)``: a git repository as an adopted one is after A9 (README, "The planted repository"): tracked
  source and notes with planted unique words, a project path map, and a store built in place at the repository's
  HEAD, ``X`` (``lexical.refresh`` and ``store.load``: A9's lexical and record stages; with ``semantic=True`` also
  ``semantic.refresh``, whose model calls the conftest's ``semantic_endpoint`` stands in for). No rebuild after it.
- ``commit`` / ``add_record`` / ``ordinary_commits``: what happens in the repository after A9, one commit at a time.
- ``gov`` / ``search``: ``gov.cli.main.main`` in this process, stdout captured (``--json`` is the envelope).
- ``evidence_paths``, ``store_of_result``: readers of a run.

Every git call is pinned (no system or user configuration, no hooks), so the planted repository has no refresh hook.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if importlib.util.find_spec("gov") is None:  # a PYTHONPATH given names the tree under test; else this one
    sys.path.insert(0, str(REPO / "src"))

REGISTER = "decisions/REGISTER.md"
PATH_MAP_REL = "governance/project/path-map.yaml"
REBUILD_REL = "governance/project/rebuild.yaml"

# The words each planted file holds (one unique token each, so a query for it finds that file and no other).
STEADY_NOTE, STEADY_NOTE_WORD = "notes/steady.md", "marmalade"      # never changes after X
STEADY_SRC, STEADY_SRC_WORD = "src/steady.py", "tamarind"          # never changes after X
CHANGING, CHANGING_WORD = "notes/changing.md", "zeppelin"          # the word is removed after X
SHIFTED, SHIFTED_WORD = "notes/shifted.md", "gryphon"              # two lines are put before it after X
DOOMED, DOOMED_WORD = "notes/doomed.md", "kestrel"                 # deleted after X
ENGINE, ENGINE_OLD_WORD, ENGINE_NEW_WORD = "src/engine.py", "ocelot", "wyvern"  # changed after X
NEWCOMER, NEWCOMER_WORD = "notes/newcomer.md", "kraken"            # added after X
RECORD, RECORD_WORD = "governance/adoption/A10-record.md", "sandpiper"  # a stage record, added after X
WALLED, WALLED_WORD = "walled/ledger.md", "cormorant"              # a path the planted path map walls from a role
WALLED_ROLE = "engineer"

PATH_MAP = (f"namespaces:\n"
            f"  open:\n"
            f"    paths: ['notes/**', 'src/**']\n"
            f"    embedding_policy: embedded\n"
            f"decision_register: {REGISTER}\n"
            f"role_paths:\n"
            f"  {WALLED_ROLE}:\n"
            f"    reads_denied:\n"
            f"      - 'walled/**'\n")
REGISTER_TEXT = ("# Decision register\n\n"
                 "### DEC-101 — The juniper rule\n- **Status:** ACCEPTED\n"
                 "- **Decision:** the juniper lantern stays lit.\n")
FILES_X = {
    ".gitignore": ".gov-runtime/\nignored/\n",
    PATH_MAP_REL: PATH_MAP,
    REGISTER: REGISTER_TEXT,
    STEADY_NOTE: f"# The steady note\n\nThe {STEADY_NOTE_WORD} lighthouse keeps its lamp lit.\n",
    STEADY_SRC: f'"""The steady module."""\n\n\ndef steady():\n    return "{STEADY_SRC_WORD} rhythm"\n',
    CHANGING: f"# The changing note\n\nThe {CHANGING_WORD} clause stands in this note.\n",
    SHIFTED: f"# The shifted note\n\nThe {SHIFTED_WORD} clause sits on line three.\n",
    DOOMED: f"# The doomed note\n\nThe {DOOMED_WORD} clause is in a note that goes away.\n",
    ENGINE: f'"""The engine."""\n\n\ndef spin():\n    return "{ENGINE_OLD_WORD} gear"\n',
    WALLED: f"# The walled ledger\n\nThe {WALLED_WORD} ledger is walled from the {WALLED_ROLE}.\n",
}
# Files that exist at X but no commit holds: a gitignored file and an untracked one.
LOOSE_X = {"ignored/cache.txt": "an ignored cache, as it stood\n", "scratch/early.txt": "an untracked note, as it stood\n"}

_GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
            "GIT_AUTHOR_DATE": "2026-11-16T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-16T12:00:00Z"}


def git(folder: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(folder), "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                           *args], capture_output=True, env={**_GIT_ENV, "HOME": str(folder)}, check=False)
    if done.returncode:
        raise AssertionError(f"git {' '.join(args)} failed in {folder}: {done.stderr.decode(errors='replace')}")
    return done.stdout.decode("utf-8", "replace")


def head(folder: Path) -> str:
    return git(folder, "rev-parse", "HEAD").strip()


def write(root: Path, files: dict) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))


def commit(repo: Path, files: dict | None = None, remove=(), message: str = "a later commit") -> str:
    """One commit that writes ``files`` and removes ``remove``, adding exactly those paths (an untracked file the case
    planted is never swept in). With neither, an empty commit. The new HEAD."""
    files = files or {}
    write(repo, files)
    if files:
        git(repo, "add", "--", *files)
    for rel in remove:
        git(repo, "rm", "-q", "--", rel)
    git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return head(repo)


def add_record(repo: Path) -> str:
    """The adoption's closing commit: one stage record under governance/adoption/ and nothing else."""
    return commit(repo, {RECORD: f"# The A10 stage record\n\nThe {RECORD_WORD} gate was checked.\n"},
                  message="A10: the stage record")


def ordinary_commits(repo: Path) -> list[str]:
    """Two ordinary commits later in the repository's life: one changes a source file, one adds a note."""
    return [commit(repo, {ENGINE: f'"""The engine."""\n\n\ndef spin():\n    return "{ENGINE_OLD_WORD} gear"\n\n\n'
                                  f'def turn():\n    return "{ENGINE_NEW_WORD} cog"\n'}, message="change the engine"),
            commit(repo, {NEWCOMER: f"# The newcomer\n\nThe {NEWCOMER_WORD} valve was added.\n"}, message="add a note")]


@dataclass(frozen=True)
class Plant:
    repo: Path
    x: str  # the commit the store was built at

    @property
    def head(self) -> str:
        return head(self.repo)


def plant(base: Path, *, semantic: bool = False, empty: bool = False) -> Plant:
    """The repository at X with its store built in place (module docstring). ``empty``: every file kept out of the
    keyword index by the path map, so the store holds no chunk (an empty store)."""
    from gov import store
    from gov.retrieval import lexical

    repo = base / "adopted"
    repo.mkdir(parents=True)
    files = dict(FILES_X)
    if empty:
        files[PATH_MAP_REL] = ("namespaces:\n  all:\n    paths: ['**']\n    lexical_policy: not indexed\n"
                               f"decision_register: {REGISTER}\n")
    write(repo, files)
    write(repo, LOOSE_X)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "X: the adopted repository")
    x = head(repo)
    lexical.refresh(repo)
    store.load(repo)
    if semantic:
        from gov.retrieval import semantic as semantic_module

        report = semantic_module.refresh(repo)
        assert report["available"] is True, f"premise: the vectors are built at X with the stand-in embedder: {report}"
    return Plant(repo, x)


def hooks_installed(repo: Path) -> list[str]:
    """What would run a refresh after a commit: an executable hook file (a ``.sample`` is none) or a configured
    ``core.hooksPath``."""
    found = [p.name for p in (repo / ".git" / "hooks").glob("*") if p.is_file() and not p.name.endswith(".sample")]
    config = (repo / ".git" / "config").read_text(encoding="utf-8")
    return found + (["core.hooksPath"] if re.search(r"hookspath", config, re.IGNORECASE) else [])


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

    def describe(self, tail: int = 2500) -> str:
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


def search(capsys, repo: Path, question: str, *options) -> Run:
    """``gov retrieve --json --root <repo> <options> <question>``."""
    return gov(capsys, "retrieve", "--json", "--root", repo, *options, question)


def evidence_paths(result: dict) -> list[str]:
    return [item.get("path") for item in result.get("evidence") or []]


def lexical_facet(result: dict) -> dict:
    return (result.get("facets") or {}).get("lexical") or {}


def store_entry(run: Run) -> dict:
    value = run.result.get("store")
    assert isinstance(value, dict), (f"the result names no store: result.store is {value!r}; keys {sorted(run.result)}\n"
                                     f"{run.describe(800)}")
    return value


def answered(run: Run, *, path: str, also_not: tuple = ()) -> None:
    """The run answered from the store: the lexical facet is available, the search did not stop FACET_UNAVAILABLE and
    ``path`` is in the evidence (and none of ``also_not``)."""
    assert run.ok, run.describe()
    result = run.result
    assert lexical_facet(result).get("available") is True, (
        f"the lexical facet is not available: {lexical_facet(result)}\n{run.describe(1200)}")
    assert result.get("stopping_reason") != "FACET_UNAVAILABLE", (
        f"the search stopped FACET_UNAVAILABLE (facets {result.get('facets')}), with evidence {evidence_paths(result)}")
    assert path in evidence_paths(result), f"{path} is not in the evidence {evidence_paths(result)}\n{run.describe(1200)}"
    for left_out in also_not:
        assert left_out not in evidence_paths(result), f"{left_out} is in the evidence {evidence_paths(result)}"
