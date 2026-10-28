"""Support code for the W2-71 acceptance tests: the secrets check passes a real commit hash of this repository for
row W2-L423's rule only (DEC-911 item 4).

The interfaces under test are public only:

- the secrets-indexing check's declared ``command`` (``python3 -m gov.secrets``), run by ``sh -c`` in a temporary
  project's root, as the family runner runs it: it prints one line of standard output per file it finds a secret
  in, naming the file, and exits 1 when it finds one and 0 when it finds none (``gov.secrets.stores_with_secrets``);
- the pre-index filter ``gov.secrets.indexable(root, paths)``, called in a child process of its own;
- the clean-result record ``.gov-runtime/secrets-clean.json`` (DEC-853), read as JSON;
- gitleaks itself, the one ``PATH`` finds, for the premises of the cases (a string is a finding by a rule, or not).

The code under test is this worktree's ``src/``: every child process gets the runner's ``PYTHONPATH`` (DEC-732),
else this worktree's ``src/``.

Row W2-L423's rule (DEC-911 item 1): the rule's id and its two keywords are never written whole in this file; they
are joined at run time by ``_joined``, which Python does not fold into one constant. Planted tokens are built at run
time from hashed seeds; none stands whole in a file of this suite, and none is ever printed: helpers return paths
and booleans, and assertion messages name the case, never the string.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import re
import shutil
import signal
import site
import sqlite3
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SRC = REPO_ROOT / "src"
CHECK_DECLARATION = REPO_ROOT / "template/governance/kernel/checks/secrets-indexing.yaml"
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
RUNTIME = ".gov-runtime"
RECORD_REL = f"{RUNTIME}/secrets-clean.json"
REAL_GITLEAKS = shutil.which("gitleaks")
REAL_GIT = shutil.which("git")
REAL_PYTHON = shutil.which("python3") or sys.executable


def _joined(*parts):
    """``parts`` joined at run time (a constant expression would be folded whole into the compiled file)."""
    return "".join(parts)


# Row W2-L423's rule: gitleaks' default rule for one code-search vendor's access token. Its id and two keywords,
# joined at run time only.
VENDOR = _joined("sour", "ceg", "raph")            # the first keyword, the vendor's name
PREFIX = _joined("sg", "p", "_")                   # the second keyword, the token prefix
RULE_ID = _joined(VENDOR, "-access-", "token")     # the rule's id
KEYWORDS = (VENDOR, PREFIX)
KEYWORD_NAMES = {VENDOR: "the vendor keyword", PREFIX: "the prefix keyword"}

# Other rules the cases use, by id (none holds a keyword).
ZENDESK_RULE = "zendesk-secret-key"                # a default rule of the keyword = value shape, 40 characters
PROJECT_HEX_RULE = "w2-71-forty-hex"               # a project rule added by these tests: a bare 40-hex value
PROJECT_HEX_KEYWORD = "checksum"
PROJECT_TOKEN_RULES = ("gov-token-digit", "gov-token-lower", "gov-token-upper")

try:
    import pytest as _pytest

    needs_gitleaks = _pytest.mark.skipif(REAL_GITLEAKS is None, reason="gitleaks is not on PATH: the check cannot run")
    needs_git = _pytest.mark.skipif(REAL_GIT is None, reason="git is not on PATH: no repository can be built")
except ImportError:   # pragma: no cover - the support module is only used under pytest
    needs_gitleaks = needs_git = None


def say(text):
    """``text`` with the rule's id and keywords masked, for an assertion message (never a token: callers pass none)."""
    text = re.sub(re.escape(VENDOR), "<vendor>", str(text), flags=re.IGNORECASE)
    return re.sub(re.escape(PREFIX), "<prefix>", text, flags=re.IGNORECASE)


def declared_limit_s():
    data = yaml.safe_load(CHECK_DECLARATION.read_text(encoding="utf-8"))
    return int(data.get("timeout-seconds") or 900)


def check_command():
    data = yaml.safe_load(CHECK_DECLARATION.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and isinstance(data.get("command"), str), "the check's declaration names no command"
    return data["command"]


def machine_busy():
    """Whether a nightly run or a close holds the machine (then a run is one test file at a time)."""
    folder = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
    return any((folder / name).exists() for name in ("NIGHTLY-RUNNING", "CLOSE-RUNNING"))


# --------------------------------------------------------------------------
# Strings, built at run time
# --------------------------------------------------------------------------

def hex_of(seed, length=40):
    """``length`` hex digits drawn from a hash of ``seed``: deterministic, never a git object id of any repository."""
    out, counter = "", 0
    while len(out) < length:
        out += hashlib.sha256(f"W2-71|{seed}|{counter}".encode()).hexdigest()
        counter += 1
    return out[:length]


def entropy(text):
    """Shannon entropy in bits a character, as gitleaks computes it for a rule's ``entropy`` floor."""
    counts = {char: text.count(char) for char in set(text)}
    return -sum(n / len(text) * math.log2(n / len(text)) for n in counts.values())


def token_digit(seed):
    """A string of the project's ``gov-token-digit`` shape: a key prefix, a digit, then 23 word characters."""
    return _joined("to", "k_") + "7" + hex_of(seed, 23)


def vendor_line(keyword, value, verb="reviewed commit"):
    """A log line that holds ``keyword`` and, after it, ``value`` alone between spaces (row W2-L423's rule matches a
    40-hex value only when a space, a quote, a semicolon or the line's end follows it)."""
    if keyword == VENDOR:
        return f"{VENDOR} review log: {verb} {value} at noon\n"
    return f"the {keyword} prefix is noted; {verb} {value} at noon\n"


# --------------------------------------------------------------------------
# The sandbox and the environment of every child
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    base: Path
    home: Path        # HOME of every process under test
    tmpdir: Path      # TMPDIR of every process under test: the temp folder the check is given
    elsewhere: Path   # the test's own folder: stand-ins, their logs
    pycache: Path


def make_sandbox(base):
    base = Path(base).resolve()
    box = Sandbox(base, base / "home", base / "systmp", base / "elsewhere", base / "pycache")
    for directory in (box.home, box.tmpdir, box.elsewhere, box.pycache):
        directory.mkdir(parents=True, exist_ok=True)
    return box


def python_path():
    """Every child's PYTHONPATH: the runner's own (DEC-732), else this worktree's ``src/``."""
    return os.environ.get("PYTHONPATH") or str(SRC)


def base_environment(sandbox, path=None, extra=None):
    """A minimal environment built from scratch; ``path`` replaces the runner's PATH.

    git never looks above the sandbox for a repository (``GIT_CEILING_DIRECTORIES``), and reads no user or system
    configuration of this machine.
    """
    env = {
        "PATH": path or os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "XDG_CACHE_HOME": str(sandbox.home / ".cache"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONUSERBASE": site.getuserbase(),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_CEILING_DIRECTORIES": str(sandbox.base),
    }
    env.update(extra or {})
    return env


_GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "W2-71 acceptance", "GIT_AUTHOR_EMAIL": "w2-71@example.invalid",
    "GIT_COMMITTER_NAME": "W2-71 acceptance", "GIT_COMMITTER_EMAIL": "w2-71@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-24T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-24T12:00:00+00:00",
}


def git(directory, *args, check=True, env=None):
    """git in ``directory``, with a fixed identity and date, so every object id of a fixture is the same each run."""
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(_GIT_IDENTITY, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    environment.update(env or {})
    proc = subprocess.run([REAL_GIT or "git", "-C", str(directory), "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", "-c", "init.defaultBranch=main", *args],
                          capture_output=True, text=True, check=False, timeout=120, env=environment)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {args[0]} failed in {Path(directory).name}: exit {proc.returncode}")
    return proc.stdout


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    path.write_bytes(data)
    return path


def sqlite_store(path, values):
    """A SQLite store at ``path`` holding each of ``values`` as one text value of its own row."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
        connection.executemany("INSERT INTO notes (body) VALUES (?)", [(value,) for value in values])
        connection.commit()
    finally:
        connection.close()
    return path


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def files_under(top, skip=(".git",)):
    """Every file under ``top``, as relative POSIX paths, leaving out the folders named in ``skip``."""
    top = Path(top)
    out = set()
    for folder, folders, names in os.walk(top):
        folders[:] = [name for name in folders if name not in skip]
        out.update((Path(folder) / name).relative_to(top).as_posix() for name in names)
    return out


# --------------------------------------------------------------------------
# Projects: a git repository built from scratch, with real commits, trees and blobs
# --------------------------------------------------------------------------

def gitleaks_toml(extra=""):
    """The kernel's ``.gitleaks.toml`` (it extends gitleaks' defaults: two rule sets, DEC-347), plus ``extra``."""
    return GITLEAKS_TEMPLATE.read_text(encoding="utf-8") + ("\n" + extra if extra else "")


def project_hex_rule():
    """A project rule whose match is a bare 40-hex value after its keyword (a commit hash, in the cases)."""
    return ("[[rules]]\n"
            f'id = "{PROJECT_HEX_RULE}"\n'
            'description = "W2-71: a bare 40-hex value after its keyword"\n'
            "regex = '''\\b([0-9a-f]{40})(?:[\\s;]|$)'''\n"
            f'keywords = ["{PROJECT_HEX_KEYWORD}"]\n')


def rewritten_vendor_rule(lengths):
    """Row W2-L423's rule with its expression rewritten by the project (same id): it matches hex runs of the given
    ``lengths`` only, after either keyword, with the rule's own trailing condition. gitleaks merges a project rule of
    a default rule's id over that rule: the expression is the project's, the keywords stay the rule's."""
    runs = "|".join(f"[a-f0-9]{{{n}}}" for n in lengths)
    return ("[[rules]]\n"
            f'id = "{RULE_ID}"\n'
            "regex = '''(?i)\\b(" + runs + ")(?:[\\x60'\"\\s;]|\\\\[nr]|$)'''\n"
            "entropy = 1.0\n")


def path_map_text(namespaces):
    document = yaml.safe_load(PATH_MAP_TEMPLATE.read_text(encoding="utf-8"))
    for name, paths in namespaces.items():
        document.setdefault("namespaces", {})[name] = {
            "paths": paths,
            "memory_class": "governance",
            "sensitivity": "internal",
            "permitted_roles": ["engineer", "independent-test-designer", "independent-auditor", "orchestrator",
                                "product-spec", "research"],
            "retention": "kept in git history",
            "export_policy": "allowed",
            "embedding_policy": "embedded",
            "provenance": "written by the W2-71 tests",
            "deletion_rebuild": "authoritative; restored from git only",
        }
    return yaml.safe_dump(document, sort_keys=False)


@dataclass
class Repo:
    """A project built from scratch: a git repository with real objects, whose ids the cases quote."""
    root: Path
    first: str        # the first commit
    head: str         # the commit checked out
    side: str         # a commit on another branch, not checked out
    tree: str         # the tree of the head commit
    blob: str         # a blob of the head commit

    @property
    def commits(self):
        return (self.first, self.head, self.side)


def make_repo(sandbox, name="project", extra_rules="", label="project"):
    """A committed project: the kernel's gitleaks rules (plus ``extra_rules``), a path map whose ``docs/**`` is
    governance memory (the filter's indexable folder), ``.gov-runtime/`` ignored; three commits on two branches.

    Object ids are fixed by the fixed identity and date (deterministic); each commit id quoted by a case holds at
    least 3.3 bits a character, above the rule's entropy floor of 3 (a premise test checks gitleaks finds it).
    """
    root = sandbox.base / name
    root.mkdir(parents=True)
    write(root / ".gitignore", ".gov-runtime/\n__pycache__/\n")
    write(root / ".gitleaks.toml", gitleaks_toml(extra_rules))
    write(root / "governance/project/path-map.yaml", path_map_text({"docs": ["docs/**"]}))
    write(root / "src/notes.txt", f"{label}: the first note\n")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    first = _commit(root, f"{label}: first commit")
    write(root / "src/notes.txt", f"{label}: the first note\n{label}: a second note\n")
    git(root, "add", "-A")
    head = _commit(root, f"{label}: second commit")
    git(root, "checkout", "-q", "-b", "side")
    write(root / "src/side.txt", f"{label}: a note on the side branch\n")
    git(root, "add", "-A")
    side = _commit(root, f"{label}: a commit on the side branch")
    git(root, "checkout", "-q", "main")
    tree = git(root, "rev-parse", "HEAD^{tree}").strip()
    blob = git(root, "rev-parse", "HEAD:src/notes.txt").strip()
    return Repo(root, first, head, side, tree, blob)


def _commit(root, message):
    """A commit of the index whose id is above the entropy floor (the message gains a counter until it is); the
    branch checked out moves to it."""
    tree = git(root, "write-tree").strip()
    parent = git(root, "rev-parse", "--verify", "-q", "HEAD", check=False).strip()
    for counter in range(64):
        text = f"{message} ({counter})" if counter else message
        sha = git(root, "commit-tree", tree, *(["-p", parent] if parent else []), "-m", text).strip()
        if entropy(sha) >= 3.3:
            git(root, "update-ref", "HEAD", sha)
            return sha
    raise AssertionError("no commit id above the entropy floor in 64 tries")


def other_repository_commit(sandbox, name="other-repository"):
    """A commit of another repository, built from scratch beside the project."""
    root = sandbox.base / name
    root.mkdir(parents=True)
    write(root / "README", "another repository of the W2-71 tests\n")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    return _commit(root, "another repository: its only commit")


def is_object(root, oid, kind="commit"):
    """Whether ``oid`` names an object of ``kind`` in the repository at ``root`` (``git cat-file -e <oid>^{kind}``);
    with ``kind`` None, an object of any kind (``git cat-file -e <oid>``)."""
    name = oid if kind is None else f"{oid}^{{{kind}}}"
    proc = subprocess.run([REAL_GIT, "-C", str(root), "cat-file", "-e", name],
                          capture_output=True, env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull}, timeout=60)
    return proc.returncode == 0


# --------------------------------------------------------------------------
# gitleaks itself: what a string is a finding of (premises)
# --------------------------------------------------------------------------

def project_rules_alone(toml_text):
    """The project file's rules with an expression of their own, alone: the check's second rule set (DEC-347)."""
    import tomllib
    rules = [rule for rule in tomllib.loads(toml_text).get("rules", []) if rule.get("regex") or rule.get("path")]
    out = []
    for rule in rules:
        out.append("[[rules]]")
        out.append(f"id = {json.dumps(rule['id'])}")
        out.append(f"description = {json.dumps(rule.get('description', 'a project rule'))}")
        out.append("regex = '''" + rule["regex"] + "'''")
        if rule.get("keywords"):
            out.append("keywords = " + json.dumps(rule["keywords"]))
        if rule.get("entropy"):
            out.append(f"entropy = {rule['entropy']}")
        out.append("")
    return "\n".join(out)


def gitleaks_finds(text, config_text):
    """The rule ids gitleaks finds in ``text`` with ``config_text``, as the check gives content (a newline first).

    The report goes to this process's memory, its matches redacted, and is never kept. Raises unless gitleaks decides.
    """
    data = ("\n" + text).encode("utf-8") if isinstance(text, str) else b"\n" + text
    env = dict(os.environ, GITLEAKS_CONFIG_TOML=config_text)
    env.pop("GITLEAKS_CONFIG", None)
    done = subprocess.run([REAL_GITLEAKS, "stdin", "--no-banner", "--redact", "--log-level", "error",
                           "--ignore-gitleaks-allow", "--exit-code", "3", "--report-format", "json",
                           "--report-path", "-"], input=data, capture_output=True, env=env, timeout=120)
    if done.returncode not in (0, 3):
        raise AssertionError(f"gitleaks did not decide a premise (exit code {done.returncode})")
    found = json.loads(done.stdout or b"[]") if done.returncode == 3 else []
    return sorted({entry.get("RuleID") for entry in found})


def gitleaks_secret_is(text, config_text, rule_id, value):
    """Whether gitleaks' finding of ``rule_id`` in ``text`` has ``value`` as its secret (compared in memory only)."""
    env = dict(os.environ, GITLEAKS_CONFIG_TOML=config_text)
    env.pop("GITLEAKS_CONFIG", None)
    done = subprocess.run([REAL_GITLEAKS, "stdin", "--no-banner", "--log-level", "error", "--ignore-gitleaks-allow",
                           "--exit-code", "3", "--report-format", "json", "--report-path", "-"],
                          input=("\n" + text).encode("utf-8"), capture_output=True, env=env, timeout=120)
    if done.returncode not in (0, 3):
        raise AssertionError(f"gitleaks did not decide a premise (exit code {done.returncode})")
    found = json.loads(done.stdout or b"[]") if done.returncode == 3 else []
    return any(entry.get("RuleID") == rule_id and entry.get("Secret", "").lower() == value.lower() for entry in found)


# --------------------------------------------------------------------------
# A run of the check, and of the filter
# --------------------------------------------------------------------------

@dataclass(repr=False)
class CheckRun:
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float

    def __repr__(self):  # what pytest prints of a failed assertion: never the output
        return f"CheckRun(exit code {self.returncode}, {self.seconds:.1f} s)"

    def describe(self, tail=600):
        """Exit code, time and the tail of the output, masked (the output must hold no match; if it did, the case
        that says so fails without printing it: see ``leaks``)."""
        return say(f"exit code: {self.returncode} after {self.seconds:.1f} s\n"
                   f"stdout (tail, masked):\n{_masked_hex(self.stdout[-tail:])}\n"
                   f"stderr (tail, masked):\n{_masked_hex(self.stderr[-tail:])}")

    def names(self, rel):
        """Whether a line of standard output names ``rel`` (a finding names the file, never the secret)."""
        pattern = re.compile(r"(?<![\w./-])" + re.escape(rel) + r"(?![\w./-])")
        return any(pattern.search(line) for line in self.stdout.splitlines())

    def named_any(self, rels):
        return any(self.names(rel) for rel in rels)

    @property
    def ended(self):
        return self.returncode is not None


def _masked_hex(text):
    """Hex runs of 16 digits or more shortened to their first 6, so a description never carries a whole hash."""
    return re.sub(r"[0-9a-fA-F]{16,}", lambda m: m.group(0)[:6] + "…", text)


def _kill_group(proc):
    with contextlib.suppress(ProcessLookupError, PermissionError, OSError):
        os.killpg(proc.pid, signal.SIGKILL)


def run_check(sandbox, project, env=None, timeout=None):
    """The check as the family runner runs it: its declared command by ``sh -c`` in the project's root, within its
    declared time limit (a run that has not ended by then is killed, with its process group, and has no exit code)."""
    env = env or base_environment(sandbox)
    timeout = timeout or declared_limit_s()
    began = time.monotonic()
    proc = subprocess.Popen(check_command(), shell=True, cwd=str(project), env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        stdout, stderr = proc.communicate()
        code = None
    finally:
        _kill_group(proc)
    return CheckRun(code, stdout, stderr, time.monotonic() - began)


_FILTER = ("import json, sys\nfrom gov.secrets import indexable\n"
           "print('W2-71-RESULT ' + json.dumps(indexable(sys.argv[1], json.loads(sys.stdin.read()))))\n")


@dataclass(repr=False)
class FilterRun:
    returncode: int | None
    returned: list
    stdout: str       # standard output without the result line
    stderr: str
    seconds: float

    def __repr__(self):  # what pytest prints of a failed assertion: never the output
        return f"FilterRun(exit code {self.returncode}, {len(self.returned)} paths, {self.seconds:.1f} s)"

    def describe(self, tail=600):
        return say(f"the filter's exit code: {self.returncode} after {self.seconds:.1f} s; paths returned: "
                   f"{len(self.returned)}\nstderr (tail, masked):\n{_masked_hex(self.stderr[-tail:])}")

    @property
    def ended(self):
        return self.returncode is not None

    def passes(self, rel):
        """Whether the filter let ``rel`` through to an index (it returned the path and ended without error)."""
        return self.returncode == 0 and rel in self.returned


def run_filter(sandbox, project, paths, env=None, timeout=None):
    """``gov.secrets.indexable(project, paths)`` in a child process (this worktree's code, DEC-732)."""
    env = env or base_environment(sandbox)
    timeout = timeout or declared_limit_s()
    began = time.monotonic()
    proc = subprocess.Popen([REAL_PYTHON, "-c", _FILTER, str(project)], cwd=str(project), env=env,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        stdout, stderr = proc.communicate(json.dumps(list(paths)), timeout=timeout)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        stdout, stderr = proc.communicate()
        code = None
    finally:
        _kill_group(proc)
    returned, rest = [], []
    for line in stdout.splitlines():
        if line.startswith("W2-71-RESULT "):
            with contextlib.suppress(ValueError):
                returned = json.loads(line[len("W2-71-RESULT "):])
        else:
            rest.append(line)
    return FilterRun(code, returned if code == 0 else [], "\n".join(rest), stderr, time.monotonic() - began)


def check_fails_closed(run, rel, all_rels):
    """The check did not pass ``rel`` as clean: it ended with a non-zero exit, and named ``rel``, or named none of the
    case's files (it stopped undecided). A run killed at its time limit is not an end: the caller asserts ``ended``."""
    return run.returncode not in (0, None) and (run.names(rel) or not run.named_any(all_rels))


# --------------------------------------------------------------------------
# Leaks: whether a run printed or wrote a match (booleans only, never the string)
# --------------------------------------------------------------------------

def leaks(text, secrets):
    """Whether ``text`` holds any of ``secrets``, in any case."""
    folded = text.lower()
    return any(secret.lower() in folded for secret in secrets)


def holds_keyword(text):
    folded = text.lower()
    return any(keyword in folded for keyword in KEYWORDS)


# --------------------------------------------------------------------------
# Stand-ins first on PATH
# --------------------------------------------------------------------------

def _script(path, body):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!{sys.executable}\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def bin_without_git(sandbox):
    """A folder that holds ``python3`` and ``gitleaks`` (links to this machine's) and no ``git``: a PATH of it alone."""
    folder = sandbox.elsewhere / "bin-without-git"
    folder.mkdir(parents=True, exist_ok=True)
    for name, target in (("python3", REAL_PYTHON), ("gitleaks", REAL_GITLEAKS)):
        link = folder / name
        if not link.exists():
            link.symlink_to(os.path.realpath(target))
    return folder


def git_that_fails(sandbox):
    """A ``git`` that answers every call with an error: exit 128, a fatal line, and ``commit`` on standard output (a
    verification that reads the output and not the exit code would take it for a yes)."""
    folder = sandbox.elsewhere / "git-that-fails"
    _script(folder / "git", "import sys\nprint('commit')\n"
                            "print('fatal: W2-71 stand-in: the object store cannot be read', file=sys.stderr)\n"
                            "sys.exit(128)\n")
    return folder


def git_that_hangs(sandbox, seconds=36_000):
    """A ``git`` that does not answer: it sleeps far beyond the check's declared limit (one process, so a time limit
    that kills it ends it), and would then say yes."""
    folder = sandbox.elsewhere / "git-that-hangs"
    _script(folder / "git", f"import sys, time\ntime.sleep({seconds})\nprint('commit')\nsys.exit(0)\n")
    return folder


MARKER = re.compile(rb"w271mark\d{4}")


def logging_gitleaks(sandbox, name="logging-gitleaks"):
    """A ``gitleaks`` first on PATH that hands every call to the real gitleaks, unchanged, and logs per call its
    arguments, which rule set it was given (``extended``: the project's file with gitleaks' defaults; ``alone``: the
    project's rules alone) and which of the tests' marker words its input held. The log holds no content."""
    folder = sandbox.elsewhere / name
    log = sandbox.elsewhere / f"{name}-calls.jsonl"
    body = f"""import json, os, re, subprocess, sys
REAL = {str(REAL_GITLEAKS)!r}
LOG = {str(log)!r}
MARKER = re.compile(rb"w271mark\\d{{4}}")
args = sys.argv[1:]
config = os.environ.get("GITLEAKS_CONFIG_TOML")
for flag in ("-c", "--config"):
    if flag in args[:-1]:
        try:
            config = open(args[args.index(flag) + 1], encoding="utf-8", errors="replace").read()
        except OSError:
            pass
for arg in args:
    if arg.startswith("--config="):
        try:
            config = open(arg.split("=", 1)[1], encoding="utf-8", errors="replace").read()
        except OSError:
            pass
kind = "none" if config is None else ("extended" if "useDefault" in config else "alone")
data = b""
if args[:1] == ["stdin"]:
    data = sys.stdin.buffer.read()
else:
    for arg in args[1:]:
        if os.path.isfile(arg):
            data += open(arg, "rb").read()
        elif os.path.isdir(arg):
            for top, _, names in os.walk(arg):
                for name in names:
                    try:
                        data += open(os.path.join(top, name), "rb").read()
                    except OSError:
                        pass
seen = sorted({{m.decode() for m in MARKER.findall(data)}} | {{m.decode() for m in MARKER.findall(data.replace(b"\\0", b""))}})
with open(LOG, "a", encoding="utf-8") as handle:
    handle.write(json.dumps({{"args": args, "rules": kind, "seen": seen}}) + "\\n")
done = subprocess.run([REAL] + args, input=data if args[:1] == ["stdin"] else None,
                      stdin=None if args[:1] == ["stdin"] else subprocess.DEVNULL)
sys.exit(done.returncode)
"""
    _script(folder / "gitleaks", body)
    return folder, log


def read_log(log):
    log = Path(log)
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


_REPORT_FLAGS = ("-r", "--report-path")


def report_paths(call):
    """The report paths a logged gitleaks call was given."""
    args, out = call["args"], []
    for index, arg in enumerate(args):
        if arg in _REPORT_FLAGS and index + 1 < len(args):
            out.append(args[index + 1])
        elif arg.startswith("--report-path="):
            out.append(arg.split("=", 1)[1])
        elif arg.startswith("-r") and len(arg) > 2 and not arg.startswith("--"):
            out.append(arg[2:].lstrip("="))
    return out


def in_memory(report_path):
    """Whether a report path stays in the caller's memory: standard output or error, or a descriptor it holds."""
    return report_path in ("-", "/dev/stdout", "/dev/stderr") or bool(
        re.fullmatch(r"/dev/fd/\d+|/proc/self/fd/\d+", report_path))
