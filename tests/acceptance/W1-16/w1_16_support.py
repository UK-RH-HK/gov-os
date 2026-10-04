"""Support code for the W1-16 acceptance tests (standard library and PyYAML only).

W1-16 builds the codebase-memory wrapper: a per-repository home under
``.gov-runtime/``, the pre-index secret filter in front of the indexer, and the
answers of the code graph. It also carries the repair of the token rule
(DEC-324, DEC-325). The tests use only public interfaces:

- ``gov.codeintel``, called in a child process with the repository's ``src/`` on
  ``PYTHONPATH`` (the README states the interface);
- ``gov.secrets.indexable(root, paths)``, the filter of W1-15, called the same way;
- the two gitleaks configuration files, given to the ``gitleaks`` binary;
- the ``codebase-memory-mcp`` binary's own ``list_projects``, asked about the home the wrapper names.

**No secret is committed.** Every planted string is built at run time from
parts and written only into a temporary directory. No test writes into this
repository, indexes it, or touches its ``.gov-runtime/`` (DEC-322). The dev
tiers are only ever cloned.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SRC = REPO_ROOT / "src"
PACKAGE_REL = "src/gov/codeintel"
PATH_MAP_REL = "governance/project/path-map.yaml"
ROOT_CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"
CONFIGS = {"repository": ROOT_CONFIG_REL, "template": TEMPLATE_CONFIG_REL}
RUNTIME_REL = ".gov-runtime"
TOKEN_RULE = "gov-token"
QUESTIONS = HERE / "questions.yaml"

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS", "~/gov-os-workbench/synthetic")).expanduser()
TOOL = "codebase-memory-mcp"
# Where the tool keeps its index when nothing tells it otherwise (the tool registry's uninstall line).
TOOL_DEFAULT_HOME_REL = ".cache/codebase-memory-mcp"

TIMEOUT_S = 300.0
RESULT_MARK = "W1-16-RESULT "
LEAKS_EXIT = 3
SQLITE_MAGIC = b"SQLite format 3\0"
CODE_SUFFIXES = (".rs", ".py", ".ts")
INTERFACE = ("index", "home", "projects", "definitions", "references", "callers", "impact", "dead_code")


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


# --------------------------------------------------------------------------
# Planted strings, built at run time: none of them stands whole in this file
# --------------------------------------------------------------------------

_WORD = "CAN" + "ARY"

# A token-shaped canary (the form of the b-dev tier), and canaries the gitleaks defaults miss, one per place a
# secret can stand in a source file.
STRING_SECRET = "-".join(["sk", "FAKE", "W116", "STRING", _WORD, "7QX2", "do", "not", "use"])
NAME_SECRET = "_".join(["W116", "NAME", _WORD, "5KD9"])          # an identifier: the name of a function
COMMENT_SECRET = "_".join(["W116", "COMMENT", _WORD, "3HV6"])
RUST_SECRET = "_".join(["W116", "RUST", _WORD, "8PL4"])
TS_SECRET = "-".join(["sk", "FAKE", "W116", "TS", _WORD, "2MZ7", "do", "not", "use"])
PLANTED = (STRING_SECRET, NAME_SECRET, COMMENT_SECRET, RUST_SECRET, TS_SECRET)

# The planted secret values of the two public dev tiers (DEC-286): the seven dev canaries.
DEV_PLANTED = {
    "a-dev": (
        "-".join(["ORION", _WORD, "SECRET", "001"]),
        "_".join(["tok", "FAKE", "DO-NOT-USE", ""]) + "-".join(["ORION", _WORD, "SECRET", "002"]) + "_abc123",
        "-".join(["ORION", _WORD, "SECRET", "003", "THIS", "IS", "NOT", "A", "REAL", "KEY", "DO", "NOT", "USE"]),
        "AKIA" + "IOSFODNN7" + "EXAMPLE",
        "wJalrXUtnFEMI/" + "K7MDENG/bPxRfiCY" + "EXAMPLEKEY",
    ),
    "b-dev": (
        "-".join(["sk", "FAKE", "ARGUS", "TOKEN", _WORD, "4WM8", "do", "not", "use"]),
        "_".join(["ARGUS", "PEM", _WORD, "9KF3", "THIS", "IS", "NOT", "A", "REAL", "KEY"]),
    ),
}

# Secrets that stand in a path, not in a file: a token-shaped file name and a folder named like a canary.
PATH_TOKEN = "sk" + "_" + "W116path" + "7Qd2" + "Lm9Xb4Tz"
FOLDER_SECRET = "_".join(["W116", "FOLDER", _WORD, "6JT1"])
PATH_PLANTED = (PATH_TOKEN, FOLDER_SECRET)

PREFIXES = ("sk", "pk", "rk", "tok")
SEPARATORS = ("_", "-")


def prefixed(prefix, separator, body):
    """A prefixed string, put together at run time."""
    return prefix + separator + body


# Bodies of 16 characters or more. ``token`` bodies hold a digit, or both an upper-case and a lower-case letter;
# ``ordinary`` bodies hold neither (DEC-325).
TOKEN_BODIES = {
    "digit-last": "abcdefghijklmno" + "7",                       # 16 characters, the digit is the last one
    "digit-first": "4" + "abcdefghijklmnop",                     # the digit is the first one
    "digits-and-mixed-case": "9fK2" + "mQ7xLp" + "0Zr4Tb8Wc",
    "mixed-case-no-digit": "Abcdefgh" + "ijklmnoP",              # 16 characters, one capital at each end
    "lower-then-upper": "refresh" + "TokenValue" + "Holder",
    "upper-then-lower": "LIVE" + "ACCOUNT" + "SECRETx",
}
ORDINARY_BODIES = {
    "lower-snake": "expiry_refresh_interval",
    "lower-kebab": "learn-pipeline-estimator",
    "lower-plain": "partitionassignment",
    "upper-snake": "MAX_RETRY_COUNT_LIMIT",                      # only upper-case letters: not "both"
    "sixteen-lower": "abcdefghijklmnop",                         # exactly the floor
}
# Ordinary identifiers as code writes them: ``(prefix, separator, body)``.
IDENTIFIERS = {
    "tok-function": ("tok", "_", "expiry_refresh_interval"),
    "pk-column": ("pk", "_", "column_name_for_orders"),
    "rk-partition": ("rk", "_", "partition_assignment_table"),
    "sk-kebab": ("sk", "-", "learn-pipeline-estimator"),
}


def in_prose(text):
    """``text`` inside ordinary prose, with no key name next to it."""
    return f"# Notes\n\nThe value is {text} today.\n\nNothing else is on this page.\n"


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    base: Path
    home: Path
    tmpdir: Path
    runtime: Path
    elsewhere: Path

    @property
    def places(self):
        """Every place outside a repository a child process could write to."""
        return (self.home, self.tmpdir, self.runtime, self.elsewhere)


def make_sandbox():
    """HOME, TMPDIR, a runtime directory and an unrelated working directory, under one short temporary path.

    The path is short on purpose: the tool's daemon listens on a unix socket in the runtime directory, and a
    socket path holds at most 108 bytes, which a pytest ``tmp_path`` can exceed.
    """
    base = Path(tempfile.mkdtemp(prefix="w16-", dir="/tmp"))
    names = ("h", "t", "r", "e")
    for name in names:
        (base / name).mkdir(mode=0o700)
    return Sandbox(base, *(base / name for name in names))


def remove_sandbox(sandbox):
    shutil.rmtree(sandbox.base, ignore_errors=True)


def child_env(sandbox, path=None):
    """Built from scratch: the session's GOV_ROLE and GOV_TICKET are not passed on, and HOME is not the user's."""
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin") if path is None else str(path),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "XDG_RUNTIME_DIR": str(sandbox.runtime),
        # Where the tool's daemon keeps its lock and socket files; without it they go to /tmp/cbm-daemon-<uid>.
        "CBM_RUNTIME_DIR": str(sandbox.runtime),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def git(repo, *args):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(repo), "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-16 tests", "GIT_AUTHOR_EMAIL": "w1-16@example.invalid",
        "GIT_COMMITTER_NAME": "W1-16 tests", "GIT_COMMITTER_EMAIL": "w1-16@example.invalid",
    }
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {repo}:\n{done.stderr}"
    return done.stdout


def tracked(repo):
    return [rel for rel in git(repo, "ls-files", "-z").split("\0") if rel]


def tool():
    """The ``codebase-memory-mcp`` binary on this machine, or None."""
    return shutil.which(TOOL)


def scanner():
    """The ``gitleaks`` binary on this machine, or None."""
    return shutil.which("gitleaks")


# --------------------------------------------------------------------------
# What the ticket builds
# --------------------------------------------------------------------------

def package_dir():
    """``src/gov/codeintel/``, once the ticket has written it."""
    path = REPO_ROOT / PACKAGE_REL
    if not (path / "__init__.py").is_file():
        raise Missing(f"the codebase-memory wrapper does not exist: there is no {PACKAGE_REL}/__init__.py")
    return path


def config_path(which):
    return REPO_ROOT / CONFIGS[which]


# --------------------------------------------------------------------------
# A repository in a temporary directory
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history",
    "export_policy": "allowed",
    "embedding_policy": "embedded",
    "provenance": "written by the W1-16 tests",
    "deletion_rebuild": "authoritative; restored from git only",
}

# One namespace: everything in the repository is governance memory, so only a secret keeps a file out.
EVERYTHING = {"everything": (["**"], "governance")}


def path_map_text(namespaces):
    """A full path map (DEC-225): this repository's own, with ``namespaces`` in place of its namespaces."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    entries = {}
    for name, (patterns, memory_class) in namespaces.items():
        entries[name] = {"paths": list(patterns), "memory_class": memory_class, **_NAMESPACE_FIELDS}
    document["namespaces"] = entries
    return yaml.safe_dump(document, sort_keys=False)


class Repo:
    """A git repository adopted the way a project is: a path map, a gitleaks configuration, ``.gov-runtime/`` ignored."""

    def __init__(self, root, config="template", namespaces=None, fresh=True):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        if fresh:
            git(self.root, "init", "-q", "-b", "main")
        self.write(PATH_MAP_REL, path_map_text(EVERYTHING if namespaces is None else namespaces))
        shutil.copy2(config_path(config), self.root / ROOT_CONFIG_REL)
        ignore = self.root / ".gitignore"
        before = ignore.read_text(encoding="utf-8") if ignore.is_file() else ""
        ignore.write_text(before.rstrip("\n") + ("\n" if before else "") + RUNTIME_REL + "/\n", encoding="utf-8")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return rel

    def commit(self, message="work"):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "--allow-empty", "-m", message)
        return self

    def status(self):
        """``git status`` of the repository: what a run left behind outside the ignored ``.gov-runtime/``."""
        return git(self.root, "status", "--porcelain", "--untracked-files=all").splitlines()


def clone_tier(name, destination):
    """A clone of a dev tier in a temporary directory, or None when this machine has no such tier."""
    tier = DEV_TIERS / name
    if not (tier / ".git").exists():
        return None
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(tier), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def rename_symbol(repo, old, new):
    """Rename ``old`` to ``new`` wherever it stands as a whole word in a tracked source file. Returns the files changed."""
    pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
    changed = []
    for rel in tracked(repo.root):
        if not rel.endswith(CODE_SUFFIXES):
            continue
        path = repo.root / rel
        text = path.read_text(encoding="utf-8")
        renamed = pattern.sub(new, text)
        if renamed != text:
            path.write_text(renamed, encoding="utf-8")
            changed.append(rel)
    return changed


def holds_word(repo_root, rel, word):
    """Whether ``word`` stands as a whole word in the file ``rel``."""
    path = Path(repo_root) / rel
    if not path.is_file():
        return False
    pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(word) + r"(?![A-Za-z0-9_])")
    return pattern.search(path.read_text(encoding="utf-8", errors="replace")) is not None


# --------------------------------------------------------------------------
# gov.codeintel and gov.secrets.indexable, in a child process
# --------------------------------------------------------------------------

_CHILD = (
    "import json, sys\n"
    "from pathlib import Path\n"
    "import importlib\n"
    "module = importlib.import_module(sys.argv[1])\n"
    "root = Path(sys.argv[2])\n"
    "out = []\n"
    "for name, args in json.loads(sys.argv[3]):\n"
    "    out.append(getattr(module, name)(root, *args))\n"
    f"print({RESULT_MARK!r} + json.dumps(out, default=str))\n"
)


@dataclass(frozen=True)
class Run:
    module: str
    calls: tuple
    returncode: int
    stdout: str
    stderr: str
    results: tuple | None   # None: a call raised

    @property
    def output(self):
        return self.stdout + self.stderr

    def describe(self):
        asked = "; ".join(f"{self.module}.{name}(root{''.join(', ' + repr(arg) for arg in args)})"
                          for name, args in self.calls)
        return f"{asked}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-3000:]}\nstderr:\n{self.stderr[-3000:]}"


def run_calls(module, root, calls, sandbox, path=None):
    """Call functions of ``module`` one after the other in one child process. The working directory is not the repository."""
    calls = [(name, list(args)) for name, args in calls]
    try:
        done = subprocess.run([sys.executable, "-c", _CHILD, module, str(root), json.dumps(calls)],
                              cwd=str(sandbox.elsewhere), env=child_env(sandbox, path), capture_output=True,
                              text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{module} did not end within {TIMEOUT_S:.0f} s: {calls}") from None
    results = None
    if done.returncode == 0:
        lines = [line for line in done.stdout.splitlines() if line.startswith(RESULT_MARK)]
        if lines:
            results = tuple(json.loads(lines[-1][len(RESULT_MARK):]))
    return Run(module, tuple((name, tuple(args)) for name, args in calls), done.returncode, done.stdout,
               done.stderr, results)


def codeintel(root, calls, sandbox):
    """The results of ``gov.codeintel`` calls, in order. Every call must succeed."""
    run = run_calls("gov.codeintel", root, calls, sandbox)
    assert run.results is not None, f"gov.codeintel did not answer\n{run.describe()}"
    return run


def refused(run):
    """Whether the child process raised: the call was refused with an error, whatever its class and message."""
    return run.returncode != 0 and run.results is None


def one(root, name, args, sandbox):
    """The result of one ``gov.codeintel`` call."""
    return codeintel(root, [(name, args)], sandbox).results[0]


def indexable(root, paths, sandbox):
    """What the pre-index filter of W1-15 lets an indexer read."""
    run = run_calls("gov.secrets", root, [("indexable", [list(paths)])], sandbox)
    assert run.results is not None, f"gov.secrets.indexable did not answer\n{run.describe()}"
    return list(run.results[0])


def entries(value, what, repo_root=None):
    """An answer as ``(path, name)`` pairs, in the order given. Each entry is a map with ``path`` and ``name``."""
    assert isinstance(value, list), f"{what}: expected a list of entries, got {type(value).__name__}: {value!r}"
    pairs = []
    for entry in value:
        assert isinstance(entry, dict) and isinstance(entry.get("path"), str) and isinstance(entry.get("name"), str), \
            f"{what}: an entry is not a map with a 'path' and a 'name': {entry!r}"
        assert not entry["path"].startswith("/") and "\\" not in entry["path"], \
            f"{what}: a path is not a repository-relative POSIX path: {entry['path']!r}"
        if repo_root is not None:
            assert (Path(repo_root) / entry["path"]).is_file(), \
                f"{what}: {entry['path']!r} is no file of the repository"
        pairs.append((entry["path"], entry["name"]))
    return pairs


# --------------------------------------------------------------------------
# The tool itself, asked about a home
# --------------------------------------------------------------------------

def tool_projects(home, sandbox):
    """``list_projects`` of the codebase-memory binary with ``home`` as its home: ``(name, root path)`` pairs."""
    env = child_env(sandbox) | {"CBM_CACHE_DIR": str(home)}
    env.pop("PYTHONPATH")
    done = subprocess.run([TOOL, "cli", "--json", "list_projects"], cwd=str(sandbox.elsewhere), env=env,
                          capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    described = f"{TOOL} cli list_projects (home {home})\nexit code: {done.returncode}\n{done.stdout}\n{done.stderr}"
    assert done.returncode == 0, described
    envelope = json.loads(done.stdout)
    assert envelope.get("isError") is False, described
    text = "\n".join(item.get("text", "") for item in envelope.get("content", []))
    count = re.search(r"(?m)^projects: (\d+)", text)
    assert count, described
    rows = [line.split() for line in text.splitlines() if line.startswith("  ")]
    assert len(rows) == int(count.group(1)), described
    return [(row[0], row[1] if len(row) > 1 else "") for row in rows]


# --------------------------------------------------------------------------
# Files: listings, index files, and where a needle stands
# --------------------------------------------------------------------------

def listing(root, skip=()):
    """Every file under ``root`` as relative paths, without the top-level folders in ``skip``."""
    root = Path(root)
    seen = set()
    for folder, dirs, files in os.walk(root):
        if Path(folder) == root:
            dirs[:] = [name for name in dirs if name not in skip]
        for name in files:
            seen.add((Path(folder) / name).relative_to(root).as_posix())
    return seen


def tree(root, skip=()):
    """Every file, folder and link under ``root`` as relative paths, without the top-level folders in ``skip``."""
    root = Path(root)
    seen = set()
    for folder, dirs, files in os.walk(root):
        if Path(folder) == root:
            dirs[:] = [name for name in dirs if name not in skip]
        for name in dirs + files:
            seen.add((Path(folder) / name).relative_to(root).as_posix())
    return seen


def names_holding(root, needles):
    """The files and folders under ``root`` whose relative path holds a needle."""
    return sorted(rel for rel in tree(root) if any(needle in rel for needle in needles))


def snapshot(root):
    """``relative path -> (size, modification time)`` of every file under ``root``; empty when it does not exist."""
    root = Path(root)
    found = {}
    if not root.is_dir():
        return found
    for rel in listing(root):
        try:
            stat = (root / rel).stat()
        except OSError:
            continue
        found[rel] = (stat.st_size, stat.st_mtime_ns)
    return found


def index_files(root, skip=()):
    """The files under ``root`` that are index files: SQLite databases and their side files, or a graph dump."""
    root = Path(root)
    found = []
    for rel in sorted(listing(root, skip)):
        path = root / rel
        try:
            with path.open("rb") as handle:
                head = handle.read(len(SQLITE_MAGIC))
        except OSError:
            continue
        if head == SQLITE_MAGIC or rel.endswith((".db", ".db-wal", ".db-shm", ".db.zst")):
            found.append(rel)
    return found


def _rows_text(path):
    """The rows of every table of a SQLite file as text: what a query of the index can return."""
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        names = [name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        parts = []
        for name in names:
            try:
                rows = connection.execute(f'SELECT * FROM "{name}"').fetchall()
            except sqlite3.Error:
                continue   # a virtual table this Python cannot load; its content is in the bytes
            parts.extend(" ".join(str(value) for value in row) for row in rows)
        return "\n".join(parts)
    except sqlite3.Error:
        return ""
    finally:
        connection.close()


def files_holding(root, needles, skip=(".git",)):
    """``relative path -> needles found`` for every file under ``root`` that holds a needle, in its bytes or its rows."""
    root = Path(root)
    found = {}
    for rel in sorted(listing(root, skip)):
        path = root / rel
        if path.is_symlink() or not path.is_file():
            continue
        data = path.read_bytes()
        text = _rows_text(path) if data.startswith(SQLITE_MAGIC) else ""
        hits = [needle for needle in needles if needle.encode() in data or needle in text]
        if hits:
            found[rel] = hits
    return found


# --------------------------------------------------------------------------
# gitleaks
# --------------------------------------------------------------------------

def scan(target, config, sandbox):
    """Run ``gitleaks dir`` over ``target`` with ``config``. Returns the findings as ``(file, rule id)`` pairs."""
    report = sandbox.tmpdir / "gitleaks-report.json"
    report.unlink(missing_ok=True)
    done = subprocess.run(
        ["gitleaks", "dir", str(target), "--config", str(config), "--no-banner", "--redact",
         "--report-format", "json", "--report-path", str(report), "--exit-code", str(LEAKS_EXIT)],
        cwd=str(sandbox.elsewhere), env=child_env(sandbox), capture_output=True, text=True, timeout=TIMEOUT_S,
        stdin=subprocess.DEVNULL)
    assert done.returncode in (0, LEAKS_EXIT), \
        f"gitleaks could not run with {config} (exit code {done.returncode}):\n{done.stderr}"
    findings = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else []
    report.unlink(missing_ok=True)
    target = Path(target).resolve()
    pairs = []
    for finding in findings:
        file = Path(finding["File"])
        file = file if file.is_absolute() else (sandbox.elsewhere / file)
        try:
            rel = file.resolve().relative_to(target).as_posix()
        except ValueError:
            rel = finding["File"]
        pairs.append((rel, finding["RuleID"]))
    return pairs


def plant_tree(base, files):
    """A folder with ``files`` (``relative path -> text``) in it."""
    base = Path(base)
    for rel, text in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return base


# --------------------------------------------------------------------------
# The code questions (questions.yaml)
# --------------------------------------------------------------------------

def load_questions():
    return yaml.safe_load(QUESTIONS.read_text(encoding="utf-8"))


def renamed(symbol, renames):
    return renames.get(symbol, symbol)


def hit_at(answer_pairs, expected_pairs, depth=5):
    """Whether one of the expected ``(path, name)`` pairs is among the first ``depth`` answers."""
    wanted = {tuple(pair) for pair in expected_pairs}
    return any(pair in wanted for pair in answer_pairs[:depth])
