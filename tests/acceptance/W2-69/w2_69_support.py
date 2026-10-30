"""Support code for the W2-69 acceptance tests: the secrets check reads what the stores hold (DEC-897).

The interfaces under test are public only:

- the secrets-indexing check's declared ``command`` (``python3 -m gov.secrets``), run by ``sh -c`` in a temporary
  project's root, as the family runner runs it; it prints one line of standard output per file it finds a secret
  in, naming the file, and exits 1 when it finds one and 0 when it finds none; it never exits 0 undecided;
- ``gov rebuild --json`` (``python3 -m gov.cli.main rebuild --json``) in a temporary project;
- gitleaks itself, the one ``PATH`` finds, for the premises of the cases (a string is a token by a rule, or not).

What gitleaks is given is seen through a stand-in named ``gitleaks``, first on ``PATH``: it hands every decision to
the real gitleaks, and logs per run which of the test's marker words it saw and with which rule set. In a learning
run, on a store or file that holds no secret, it also keeps a copy of each input it is given, so that a case can
find where the check begins and ends its inputs (README, "Where the check reads").

The code under test is this worktree's ``src/``: every child process gets the runner's ``PYTHONPATH`` (DEC-732),
else this worktree's ``src/``.

Planted secrets and token-shaped strings are built at run time from parts and hashed characters; none stands whole
in a file of this suite, and none is ever printed or logged by these helpers.
"""

from __future__ import annotations

import contextlib
import fcntl
import functools
import hashlib
import itertools
import json
import os
import random
import re
import shutil
import signal
import site
import sqlite3
import string
import struct
import subprocess
import sys
import threading
import time
import tomllib
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import re._constants as sre_c
import re._parser as sre_parse
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SRC = REPO_ROOT / "src"
CHECK_DECLARATION = REPO_ROOT / "template/governance/kernel/checks/secrets-indexing.yaml"
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_TEMPLATE = REPO_ROOT / "template/governance/project/path-map.yaml"
RUNTIME = ".gov-runtime"
REAL_GITLEAKS = shutil.which("gitleaks")
CODE_TOOL = shutil.which("codebase-memory-mcp")
SQLITE_HEADER = b"SQLite format 3\0"
FINDING_EXIT = 1

try:
    import pytest as _pytest

    needs_gitleaks = _pytest.mark.skipif(REAL_GITLEAKS is None, reason="gitleaks is not on PATH: the check cannot run")
    local_only = _pytest.mark.local_only
except ImportError:   # pragma: no cover - the support module is only used under pytest
    needs_gitleaks = local_only = None

# gitleaks 8.30.1's reads of its input, as measured for this ticket (README, "Facts the cases are built on"): a read
# of what the pipe holds (65,536 bytes as Python writes a pipe; 100,000 from a file), then a peek to a blank line or
# 25,000 bytes more; each later read is 3,672 bytes and its peek. On text with no blank line the reads begin at
# 90,536 + 28,672 k (a pipe) or 125,000 + 28,672 k (a file).
FIRST_READ_PIPE, FIRST_READ_FILE, LATER_READ, PEEK = 65_536, 100_000, 3_672, 25_000
PIPE_EDGES = tuple(FIRST_READ_PIPE + PEEK + k * (LATER_READ + PEEK) for k in range(40))
FILE_EDGES = tuple(FIRST_READ_FILE + PEEK + k * (LATER_READ + PEEK) for k in range(40))


def declared_limit_s():
    data = yaml.safe_load(CHECK_DECLARATION.read_text(encoding="utf-8"))
    return int(data.get("timeout-seconds") or 900)


def check_command():
    data = yaml.safe_load(CHECK_DECLARATION.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and isinstance(data.get("command"), str), "the check's declaration names no command"
    return data["command"]


# --------------------------------------------------------------------------
# The sandbox and the environment of every child
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    base: Path
    home: Path        # HOME of every process under test
    tmpdir: Path      # TMPDIR of every process under test
    elsewhere: Path   # the test's own folder: logs, copies, a linked folder outside the project
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


def base_environment(sandbox, path=None):
    """A minimal environment built from scratch; ``path`` replaces the runner's PATH."""
    return {
        "PATH": path or os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "XDG_CACHE_HOME": str(sandbox.home / ".cache"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "W2-69 acceptance", "GIT_AUTHOR_EMAIL": "w2-69@example.invalid",
        "GIT_COMMITTER_NAME": "W2-69 acceptance", "GIT_COMMITTER_EMAIL": "w2-69@example.invalid",
    }


def git(directory, *args, check=True):
    proc = subprocess.run(["git", "-C", str(directory), "-c", "user.name=W2-69 acceptance",
                           "-c", "user.email=w2-69@example.invalid", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False, timeout=120)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc.stdout


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    path.write_bytes(data)
    return path


@contextlib.contextmanager
def slot(folder, slots=3):
    """At most ``slots`` heavy check runs of this suite at once, across xdist workers (a lock file each)."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    while True:
        for number in range(slots):
            handle = open(folder / f"w2-69-slot-{number}.lock", "a+")
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                handle.close()
                continue
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
                handle.close()
            return
        time.sleep(0.2)


# --------------------------------------------------------------------------
# A project and a run of the check
# --------------------------------------------------------------------------

def make_check_project(sandbox, name="project", gitleaks_toml=None):
    """A git repository with the kernel's ``.gitleaks.toml`` (it extends gitleaks' defaults: two rule sets)."""
    project = sandbox.base / name
    (project / RUNTIME).mkdir(parents=True, exist_ok=True)
    write(project / ".gitignore", ".gov-runtime/\n")
    if gitleaks_toml is None:
        shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    else:
        write(project / ".gitleaks.toml", gitleaks_toml)
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-69 fixture project")
    return project


@dataclass
class CheckRun:
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float
    calls: list = field(default_factory=list)   # the stand-in's log entries of this run

    def describe(self, tail=1500):
        return (f"exit code: {self.returncode} after {self.seconds:.1f} s; gitleaks runs seen: {len(self.calls)}\n"
                f"stdout (tail):\n{self.stdout[-tail:]}\nstderr (tail):\n{self.stderr[-tail:]}")

    def names(self, rel):
        """Whether a line of standard output names ``rel`` (a finding names the file, never the secret)."""
        pattern = re.compile(r"(?<![\w./-])" + re.escape(rel) + r"(?![\w./-])")
        return any(pattern.search(line) for line in self.stdout.splitlines())

    def named(self, rels):
        return [rel for rel in rels if self.names(rel)]

    def given(self, word):
        """The rule sets under which the stand-in saw ``word`` in this run."""
        return {call["rules"] for call in self.calls if word in call.get("seen", [])}


def run_check(sandbox, project, env=None, timeout=None):
    """The check as the family runner runs it: its declared command by ``sh -c`` in the project's root."""
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


def _kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


# --------------------------------------------------------------------------
# The stand-in gitleaks
# --------------------------------------------------------------------------

_STAND_IN = r'''#!@PYTHON@
"""Stand-in for gitleaks (W2-69 acceptance tests): logs what it is given; the decision is the real gitleaks'."""
import hashlib, json, os, signal, subprocess, sys, threading, time

REAL, LOG, MODE = @REAL@, @LOG@, @MODE@
try:
    with open(MODE, encoding="utf-8") as handle:
        mode = json.load(handle)
except (OSError, ValueError):
    mode = {}
markers = [m.encode() for m in mode.get("markers", [])]
fault, fault_marker = mode.get("fault"), (mode.get("fault_marker") or "").encode()
keep = mode.get("keep")   # a folder: a copy of each input is kept there (learning runs, on clean content only)
args = sys.argv[1:]
began = time.monotonic()


def option(*names):
    for i, arg in enumerate(args):
        for name in names:
            if arg == name and i + 1 < len(args):
                return args[i + 1]
            if arg.startswith(name + "="):
                return arg.split("=", 1)[1]
    return None


def rules():
    text = os.environ.get("GITLEAKS_CONFIG_TOML")
    if text is None:
        path = option("-c", "--config") or os.environ.get("GITLEAKS_CONFIG")
        if path is None:
            return "default"
        try:
            with open(path, "rb") as handle:
                return hashlib.sha256(handle.read()).hexdigest()[:16]
        except OSError:
            return "unreadable"
    return hashlib.sha256(text.encode()).hexdigest()[:16]


seen, longest = set(), max((len(m) for m in markers + [fault_marker]), default=1)
size, tail, kept = 0, b"", []


def take(chunk):
    global size, tail
    size += len(chunk)
    window = tail + chunk
    for m in markers:
        if m in window:
            seen.add(m.decode())
    if fault_marker and fault_marker in window:
        seen.add("\0fault")
    tail = window[-longest:]


def keep_input(data):
    if keep:
        name = os.path.join(keep, f"{os.getpid()}-{len(kept)}-{time.monotonic_ns()}.bin")
        with open(name, "wb") as handle:
            handle.write(data)
        kept.append(name)


def drain(stream, into):
    into.append(stream.read())


sub = args[0] if args else ""
out, err = [], []
if sub == "stdin":
    child = subprocess.Popen([REAL, *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    readers = [threading.Thread(target=drain, args=(child.stdout, out)),
               threading.Thread(target=drain, args=(child.stderr, err))]
    for each in readers:
        each.start()
    source, whole = sys.stdin.buffer, []
    while True:
        chunk = source.read1(1 << 18)
        if not chunk:
            break
        try:
            child.stdin.write(chunk)
        except (BrokenPipeError, OSError):
            pass
        take(chunk)
        if keep:
            whole.append(chunk)
    try:
        child.stdin.close()
    except (BrokenPipeError, OSError):
        pass
    keep_input(b"".join(whole))
else:
    named = [a for a in args[1:] if not a.startswith("-") and os.path.exists(a)]
    named += [p for p in (option("-s", "--source"),) if p and os.path.exists(p)]
    for top in named:
        paths = [top] if os.path.isfile(top) else [os.path.join(d, n) for d, _, ns in os.walk(top) for n in ns]
        for path in paths:
            try:
                with open(path, "rb") as handle:
                    data = handle.read()
            except OSError:
                continue
            take(data)
            tail = b""
            keep_input(data)
    child = subprocess.Popen([REAL, *args], stdin=sys.stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    readers = [threading.Thread(target=drain, args=(child.stdout, out)),
               threading.Thread(target=drain, args=(child.stderr, err))]
    for each in readers:
        each.start()

faulty = fault and (not fault_marker or "\0fault" in seen)
record = {"pid": os.getpid(), "sub": sub, "rules": rules(), "size": size,
          "seen": sorted(s for s in seen if s != "\0fault"), "fault": fault if faulty else None}


def log(entry):
    line = (json.dumps(entry) + "\n").encode()
    fd = os.open(LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)


if faulty:
    child.kill()
    child.wait()
    log(record)
    if fault == "hang":
        while True:
            time.sleep(3600)
    if fault == "signal":
        os.kill(os.getpid(), signal.SIGKILL)
    expected = {0, 1, int(option("--exit-code") or 1)}
    sys.exit(next(code for code in (2, 4, 5, 6) if code not in expected))
code = child.wait()
for each in readers:
    each.join()
record.update(code=code, seconds=round(time.monotonic() - began, 2))
log(record)
sys.stdout.buffer.write(b"".join(out))
sys.stderr.buffer.write(b"".join(err))
sys.exit(code)
'''


@dataclass
class StandIn:
    bin: Path
    log: Path
    mode: Path
    kept: Path

    def set(self, markers=(), fault=None, fault_marker="", keep=False):
        """The next runs' mode. ``keep`` empties the folder of kept inputs first; without it the folder is left."""
        if keep:
            shutil.rmtree(self.kept, ignore_errors=True)
            self.kept.mkdir(parents=True)
        self.mode.write_text(json.dumps({"markers": list(markers), "fault": fault, "fault_marker": fault_marker,
                                         "keep": str(self.kept) if keep else None}), encoding="utf-8")

    def entries(self):
        if not self.log.is_file():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line.strip()]

    def inputs(self):
        return [path.read_bytes() for path in sorted(self.kept.glob("*.bin"))] if self.kept.is_dir() else []

    def environment(self, sandbox):
        env = base_environment(sandbox)
        env["PATH"] = f"{self.bin}{os.pathsep}{env['PATH']}"
        return env


def install_stand_in(sandbox):
    folder = sandbox.elsewhere / "gitleaks-stand-in"
    (folder / "bin").mkdir(parents=True, exist_ok=True)
    stand_in = StandIn(folder / "bin", folder / "calls.jsonl", folder / "mode.json", folder / "kept")
    path = stand_in.bin / "gitleaks"
    path.write_text(_STAND_IN.replace("@PYTHON@", sys.executable).replace("@REAL@", repr(REAL_GITLEAKS))
                    .replace("@LOG@", repr(str(stand_in.log))).replace("@MODE@", repr(str(stand_in.mode))),
                    encoding="utf-8")
    path.chmod(0o755)
    stand_in.set()
    return stand_in


def run_with_stand_in(sandbox, project, stand_in, markers=(), fault=None, fault_marker="", keep=False):
    before = len(stand_in.entries())
    stand_in.set(markers=markers, fault=fault, fault_marker=fault_marker, keep=keep)
    run = run_check(sandbox, project, env=stand_in.environment(sandbox))
    stand_in.set()   # the kept inputs, if any, stay for the caller
    run.calls = stand_in.entries()[before:]
    return run


# --------------------------------------------------------------------------
# Planted strings, built at run time from parts
# --------------------------------------------------------------------------

ALNUM = string.ascii_letters + string.digits
B64 = ALNUM + "+/"
_SHELTERED = ("false", "true", "null", "abcdefghijklmnopqrstuvwxyz")


def chars(seed, n, alphabet=ALNUM):
    """``n`` characters of ``alphabet``, from a hash of ``seed``: the same on every run."""
    out = []
    for count in itertools.count():
        for byte in hashlib.sha256(f"w2-69:{seed}:{count}".encode()).digest():
            out.append(alphabet[byte % len(alphabet)])
            if len(out) == n:
                text = "".join(out)
                assert not any(word in text.lower() for word in _SHELTERED), "a planted body holds a sheltered word"
                return text


def ghp_token(seed):
    """A github-pat shape (40 characters, all word characters; any cut of it is no token). Not a credential."""
    return "gh" + "p_" + chars(f"ghp-{seed}", 36)


def dashed_token(seed):
    """A shape of the project's ``gov-token-digit`` rule at its shortest (19 characters) with five dashes inside, so
    any cut of it is no token, and a cut at a dash falls at a byte that is not a word character."""
    body = "-".join([chars(f"d1-{seed}", 2), chars(f"d2-{seed}", 2), chars(f"d3-{seed}", 2), chars(f"d4-{seed}", 2),
                     chars(f"d5-{seed}", 3)])
    return "sk" + "-" + "7" + body


def pem_key(seed):
    """A private-key block of about 260 bytes over five lines (spaces and newlines inside). Not a key."""
    lines = [chars(f"pem-{seed}-{n}", 64, B64) for n in range(3)]
    return ("-----BEGIN " + "RSA PRIV" + "ATE KEY-----\n" + "\n".join(lines) + "\n-----END " + "RSA PRIV"
            + "ATE KEY-----")


def canary(seed):
    return "zq" + "_" + "CAN" + "ARY" + "_" + chars(f"canary-{seed}", 6)


def own_only(seed):
    """A value only the scan with the project's rules alone finds (DEC-347): the alphabet run in it is sheltered by
    gitleaks' built-in global allowlist under ``extend``."""
    return "sk" + "_" + "7Qd2" + "abcdefghijklm" + "nopqrstuvwxyz" + chars(f"own-{seed}", 2)


def marker(name):
    """A plain word only these tests write, that no rule finds."""
    return "zqxw" + "69" + re.sub(r"[^a-z0-9]", "", name.lower())


# The project's four rules with a leading word boundary, each with a word-internal string built from parts:
# (the word characters before it, the token-shaped string). The string alone is a token by that rule; inside its word
# (the prefix before it) it is no token by any rule.
def project_k2_strings():
    return {
        "gov-token-digit": ("q", "sk" + "_" + "7" + chars("k2-digit", 15)),
        "gov-token-upper": ("q", "pk" + "_" + "A" + "b" + chars("k2-upper", 14)),
        "gov-token-lower": ("q", "tok" + "_" + "a" + "B" + chars("k2-lower", 14)),
        "gov-canary": ("_", "zq" + "_" + "CAN" + "ARY" + "_" + chars("k2-canary", 5)),
    }


# --------------------------------------------------------------------------
# gitleaks' rules, and gitleaks as the judge of a premise
# --------------------------------------------------------------------------

def template_text():
    return GITLEAKS_TEMPLATE.read_text(encoding="utf-8")


def project_rules_alone_text():
    """The project's rules alone, as the second rule set (DEC-347)."""
    rules = tomllib.loads(template_text()).get("rules", [])
    out = []
    for rule in rules:
        out.append("[[rules]]")
        out.append(f"id = {json.dumps(rule['id'])}")
        out.append(f"description = {json.dumps(rule.get('description', rule['id']))}")
        out.append("regex = '''" + rule["regex"] + "'''")
        if rule.get("keywords"):
            out.append("keywords = " + json.dumps(rule["keywords"]))
        out.append("")
    return "\n".join(out)


def rule_sets():
    return {"extended": template_text(), "alone": project_rules_alone_text()}


def gitleaks_finds(data, config_text):
    """The rule ids gitleaks finds in ``data`` with ``config_text``. Raises if gitleaks does not decide. The report's
    matches are redacted and never kept."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    env = dict(os.environ, GITLEAKS_CONFIG_TOML=config_text)
    env.pop("GITLEAKS_CONFIG", None)
    done = subprocess.run([REAL_GITLEAKS, "stdin", "--no-banner", "--redact", "--log-level", "error",
                           "--ignore-gitleaks-allow", "--exit-code", "3", "--report-format", "json",
                           "--report-path", "-"], input=data, capture_output=True, env=env, timeout=120)
    if done.returncode not in (0, 3):
        raise AssertionError(f"gitleaks did not decide a premise (exit code {done.returncode})")
    found = json.loads(done.stdout or b"[]") if done.returncode == 3 else []
    return sorted({entry.get("RuleID") for entry in found})


@functools.lru_cache(maxsize=1)
def default_config():
    """gitleaks' own default configuration, as the binary ``PATH`` finds holds it (it has no command to print it)."""
    data = Path(REAL_GITLEAKS).read_bytes()
    start = data.find(b'title = "gitleaks config"')
    assert start >= 0, f"{REAL_GITLEAKS} holds no default configuration this suite can read"
    end = start
    while end < len(data) and (32 <= data[end] < 127 or data[end] in (9, 10, 13)):
        end += 1
    return tomllib.loads(data[start:end].decode("ascii"))


def leads_with_boundary(regex):
    """Whether the expression begins with a word boundary, after its leading flags and opening groups."""
    rest = re.sub(r"^(?:\(\?[a-z]+\))+", "", regex)
    return bool(re.match(r"(?:\((?:\?:)?)*\\b", rest))


def default_boundary_rules():
    return {rule["id"]: rule for rule in default_config()["rules"]
            if rule.get("regex") and leads_with_boundary(rule["regex"])}


# ---- strings built from a rule's own expression ----------------------------

_POSIX = {"alnum": "a-zA-Z0-9", "alpha": "a-zA-Z", "digit": "0-9", "lower": "a-z", "upper": "A-Z",
          "xdigit": "0-9A-Fa-f", "space": r"\s", "punct": r"!-/:-@\[-`{-~", "word": r"\w"}
_WORD = set(string.ascii_letters + string.digits + "_")


def go_to_python(regex):
    """gitleaks' (Go RE2) expression in Python's syntax: POSIX classes, ``\\z``, and a ``(?i)`` inside the
    expression kept for the rest of its group, its later alternatives included, as Go keeps it."""
    for name, body in _POSIX.items():
        regex = regex.replace(f"[:{name}:]", body)
    regex = regex.replace(r"\z", r"\Z")
    out, stack, i, in_class = [], [[]], 0, False
    while i < len(regex):
        ch = regex[i]
        if ch == "\\":
            out.append(regex[i:i + 2])
            i += 2
            continue
        if in_class:
            in_class = ch != "]"
            out.append(ch)
            i += 1
            continue
        if ch == "[":
            in_class = True
            out.append(ch)
            i += 1
            for lead in ("^", "]"):
                if i < len(regex) and regex[i] == lead:
                    out.append(lead)
                    i += 1
            continue
        flags = re.match(r"\(\?([a-z]*)(?:-([a-z]*))?\)", regex[i:])
        if flags and i > 0:
            text = flags.group(1) + ("-" + flags.group(2) if flags.group(2) else "")
            out.append(f"(?{text}:")
            stack[-1].append(text)
            i += flags.end()
            continue
        if ch == "(":
            stack.append([])
        elif ch == "|":
            opened = stack[-1]
            out.append(")" * len(opened) + "|" + "".join(f"(?{f}:" for f in opened))
            i += 1
            continue
        elif ch == ")":
            out.append(")" * len(stack.pop()))
        out.append(ch)
        i += 1
    out.append(")" * len(stack.pop()))
    return "".join(out)


def _class_chars(items, ignore):
    allowed, negate = set(), False
    for op, av in items:
        if op is sre_c.NEGATE:
            negate = True
        elif op is sre_c.LITERAL:
            allowed.add(chr(av))
        elif op is sre_c.RANGE:
            allowed.update(chr(c) for c in range(av[0], av[1] + 1))
        elif op is sre_c.CATEGORY:
            allowed.update({sre_c.CATEGORY_DIGIT: string.digits, sre_c.CATEGORY_WORD: "".join(_WORD),
                            sre_c.CATEGORY_SPACE: " \t\n", sre_c.CATEGORY_NOT_SPACE: "".join(_WORD) + "+/=.-",
                            sre_c.CATEGORY_NOT_DIGIT: "abcXYZ", sre_c.CATEGORY_NOT_WORD: " .-"}.get(av, ""))
    if ignore:
        allowed |= {c.swapcase() for c in allowed}
    if negate:
        allowed = {chr(c) for c in range(32, 127)} - allowed
    return allowed


def _generate(tree, rng, ignore=False):
    out = []
    for op, av in tree:
        if op is sre_c.LITERAL:
            out.append(chr(av))
        elif op is sre_c.NOT_LITERAL:
            out.append("q" if chr(av) != "q" else "z")
        elif op is sre_c.ANY:
            out.append(".")
        elif op is sre_c.IN:
            allowed = _class_chars(av, ignore)
            alnum = [c for c in ALNUM if c in allowed]
            out.append(rng.choice(alnum) if alnum else "_" if "_" in allowed else " " if " " in allowed
                       else sorted(allowed)[0])
        elif op in (sre_c.MAX_REPEAT, sre_c.MIN_REPEAT, getattr(sre_c, "POSSESSIVE_REPEAT", None)):
            low, high, sub = av
            high = low + 24 if high == sre_c.MAXREPEAT else high
            single = len(sub) == 1 and sub[0][0] in (sre_c.IN, sre_c.LITERAL, sre_c.CATEGORY, sre_c.NOT_LITERAL)
            count = (low if low >= 12 or low == high else min(high, max(low, 16))) if single else max(low, min(1, high))
            out.extend(_generate(sub, rng, ignore) for _ in range(count))
        elif op is sre_c.SUBPATTERN:
            _group, add, remove, sub = av
            out.append(_generate(sub, rng, (ignore or bool(add & re.IGNORECASE)) and not remove & re.IGNORECASE))
        elif op is sre_c.BRANCH:
            branches = av[1]
            out.append(_generate(branches[0] if rng.first_branch else rng.choice(branches), rng, ignore))
        elif op in (sre_c.AT, sre_c.ASSERT, sre_c.ASSERT_NOT):
            pass
        elif op is sre_c.CATEGORY:
            out.append({sre_c.CATEGORY_DIGIT: "7", sre_c.CATEGORY_SPACE: " "}.get(av, "k"))
        else:
            raise ValueError(f"no generation for {op}")
    return "".join(out)


@dataclass(frozen=True)
class RuleString:
    """A token built from one rule, and how it stands inside a word: ``prefix + token + tail`` (start side) holds no
    token by any rule, while ``token + tail`` does; ``token + suffix + tail`` (end side, ``suffix`` empty when the
    rule has none) holds none either. ``tail`` names the rule's keyword where the token itself does not hold one."""
    rule: str
    prefix: str
    token: str
    tail: str
    suffix: str
    why_not: str = ""   # set when no such string could be built: the reason


@functools.lru_cache(maxsize=None)
def rule_string(rule_id):
    """The word-internal string of one of gitleaks' default rules with a leading word boundary, or the reason none
    can be built. Every claim is judged by the real gitleaks with the project's extended rule set."""
    rule = default_boundary_rules()[rule_id]
    if rule.get("path"):
        return RuleString(rule_id, "", "", "", "", f"the rule applies only to paths matching {rule['path']!r}; "
                          "gitleaks stdin gives no path")
    config = template_text()
    python = go_to_python(rule["regex"])
    tree = sre_parse.parse(python)
    keywords = [k.lower() for k in rule.get("keywords") or []]
    why = "no string built from the expression is found alone"
    for attempt in range(12):
        rng = random.Random(f"w2-69-{rule_id}-{attempt}")
        rng.first_branch = attempt < 3
        token = _generate(tree, rng).rstrip(" ")
        if not re.search(python, " " + token + " "):
            continue
        tail = "" if not keywords or any(k in token.lower() for k in keywords) else " " + rule["keywords"][0]
        if rule_id not in gitleaks_finds(" " + token + tail + " \n", config):
            continue
        for prefix in ("q", "_", "9"):
            if not gitleaks_finds(" " + prefix + token + tail + " \n", config):
                break
        else:
            why = "the string inside a word is still found by some rule (a rule without a leading boundary)"
            continue
        suffix = ""
        for candidate in ("q", "q" * 400):
            if not gitleaks_finds(" " + token + candidate + tail + " \n", config):
                suffix = candidate
                break
        return RuleString(rule_id, prefix, token, tail, suffix)
    return RuleString(rule_id, "", "", "", "", why)


# --------------------------------------------------------------------------
# Content: tagged filler whose every cell names its own offset
# --------------------------------------------------------------------------

CELL = 9                        # "t0001234 ": a tag of the cell's own byte offset, and one separator
TAG = re.compile(rb"t(\d{7})")
SWEEP_SIZE = 128 * 1024         # holds gitleaks' first two pipe edges and its first file edge
LAYOUTS = ("oneline", "lines", "blank", "longword")


def tagged(layout, size):
    """``size`` bytes of plain cells ``t<offset>`` that no rule finds, laid out as:

    - ``oneline``: one line, cells parted by spaces, no newline at all;
    - ``lines``: lines of eight cells (72 bytes), no blank line;
    - ``blank``: lines of eight cells, a blank line after every sixth;
    - ``longword``: cells joined by ``_`` into words of 2,000 cells (18,000 bytes), parted by a space.
    """
    out, count = bytearray(), 0
    while len(out) < size:
        if layout == "oneline":
            sep = b" "
        elif layout in ("lines", "blank"):
            sep = b"\n" if count % 8 == 7 else b" "
        elif layout == "longword":
            sep = b" " if count % 2000 == 1999 else b"_"
        else:
            raise ValueError(layout)
        out += b"t%07d" % len(out) + sep
        if layout == "blank" and count % 48 == 47:
            out += b"\n"
        count += 1
    del out[size:]
    out[-1:] = b"\n" if layout != "oneline" else b" "
    return out


def place(content, at, text, before=b" ", after=b" "):
    """``content`` with ``before + text + after`` written over it so that ``text`` begins at ``at``; None when it
    does not fit."""
    start, end = at - len(before), at + len(text) + len(after)
    if start < 0 or end > len(content):
        return None
    out = bytearray(content)
    out[start:end] = before + text + after
    return out


# ---- where the check begins and ends what it gives gitleaks -----------------

def _runs(data, content):
    """The stretches of ``data`` that are a stretch of ``content`` byte for byte: (input start, content start,
    length), found by the tags and grown byte by byte to their exact ends."""
    tags = [(m.start(), int(m.group(1))) for m in TAG.finditer(data)]
    tags = [(i, c) for i, c in tags if c + 8 <= len(content) and content[c:c + 8] == data[i:i + 8]]
    runs = []
    for i, c in tags:
        if runs:
            ri, rc, rn = runs[-1]
            if i - ri == c - rc and i <= ri + rn + CELL and data[ri + rn:i] == content[rc + rn:c]:
                runs[-1] = (ri, rc, i + 8 - ri)
                continue
        runs.append((i, c, 8))
    grown = []
    for i, c, n in runs:
        low = grown[-1][0] + grown[-1][2] if grown else 0
        while i > low and c > 0 and data[i - 1] == content[c - 1]:
            i, c, n = i - 1, c - 1, n + 1
        while i + n < len(data) and c + n < len(content) and data[i + n] == content[c + n]:
            n += 1
        grown.append((i, c, n))
    return grown


_BLANK = re.compile(rb"\n[ \t\r]*\n")


def gitleaks_read_starts(data, first):
    """Where gitleaks begins its reads of ``data`` (positions in it), by the measured mechanism."""
    starts, position, read = [], 0, first
    while True:
        end = position + read
        if end >= len(data):
            return starts
        blank = _BLANK.search(data, max(position, end - 1), min(len(data), end + PEEK + 1))
        following = blank.end() if blank else end + PEEK
        if following >= len(data):
            return starts
        starts.append(following)
        position, read = following, LATER_READ


@dataclass
class Edges:
    """Places of the content where a read of gitleaks begins or ends, as a learning run showed them."""
    splits: list   # where an input the check gave gitleaks, or a stretch of one, begins or ends
    reads: list    # where gitleaks itself begins a read inside an input (pipe or file), as measured
    inputs: int    # the inputs of the learning run that held the content

    def chosen(self, low, high, cap):
        """Up to ``cap`` places within [low, high]: half of them gitleaks' reads, the rest the check's splits (a
        bucket that has fewer gives its share to the other), each bucket's spread evenly over it."""
        reads = sorted({e for e in self.reads if low <= e <= high})
        splits = sorted({e for e in self.splits if low <= e <= high})
        share = min(len(reads), (cap + 1) // 2)
        share_splits = min(len(splits), cap - share)
        share = min(len(reads), cap - share_splits)

        def spread(bucket, count):
            if count <= 0:
                return []
            if count == 1:
                return [bucket[0]]
            return [bucket[round(j * (len(bucket) - 1) / (count - 1))] for j in range(count)]

        merged = []
        for edge in sorted(spread(reads, share) + spread(splits, share_splits)):
            if not merged or edge - merged[-1] > 4:
                merged.append(edge)
        return merged


def edges_of(inputs, content):
    splits, reads, holding = set(), set(), 0
    for data in inputs:
        runs = _runs(data, content)
        if not runs:
            continue
        holding += 1
        for _i, c, n in runs:
            splits.update((c, c + n))
        for first in (FIRST_READ_PIPE, FIRST_READ_FILE):
            for position in gitleaks_read_starts(data, first):
                for i, c, n in runs:
                    if i <= position < i + n:
                        reads.add(c + position - i)
                        break
    splits.discard(0)
    splits.discard(len(content))
    return Edges(sorted(splits), sorted(reads), holding)


def learn(sandbox, project, stand_in, rel, write_case, content):
    """A learning run: the clean case alone in the runtime folder, the stand-in keeping each input. The case must be
    green; returns where its content's reads begin and end. The clean case stays, as a control of the next run."""
    write_case(project / rel)
    run = run_with_stand_in(sandbox, project, stand_in, keep=True)
    assert run.returncode == 0, f"premise: the clean case {rel} is green\n{run.describe()}"
    inputs = stand_in.inputs()
    assert inputs, f"the stand-in gitleaks on PATH was given nothing: the check did not run the gitleaks PATH finds\n" \
                   f"{run.describe()}"
    shutil.rmtree(stand_in.kept, ignore_errors=True)
    edges = edges_of(inputs, bytes(content))
    assert edges.inputs, f"no input the check gave gitleaks held the clean case's content {rel}\n{run.describe()}"
    return edges


# --------------------------------------------------------------------------
# SQLite stores
# --------------------------------------------------------------------------

def sqlite_store(path, schema, rows=(), encoding=None, journal=None, secure_delete=None, after=()):
    """A SQLite file: ``schema`` (statements), ``rows`` as (insert statement, values), then the ``after``
    statements, each committed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, isolation_level=None)
    try:
        if encoding:
            connection.execute(f"PRAGMA encoding = '{encoding}'")
        if secure_delete is not None:
            connection.execute(f"PRAGMA secure_delete = {'ON' if secure_delete else 'OFF'}")
        if journal:
            connection.execute(f"PRAGMA journal_mode = {journal}")
        for statement in schema:
            connection.execute(statement)
        connection.execute("BEGIN")
        for statement, values in rows:
            connection.execute(statement, values)
        connection.execute("COMMIT")
        for statement in after:
            connection.execute(statement)
    finally:
        connection.close()
    return path


def long_value_store(path, text, encoding=None):
    return sqlite_store(path, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                        [("INSERT INTO notes (body) VALUES (?)", (text,))], encoding=encoding)


def values_store(path, values):
    return sqlite_store(path, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                        [("INSERT INTO notes (body) VALUES (?)", (value,)) for value in values])


def fts_store(path, text):
    return sqlite_store(path, ["CREATE VIRTUAL TABLE notes USING fts5(body)"],
                        [("INSERT INTO notes (body) VALUES (?)", (text,))])


def blob_store(path, data):
    return sqlite_store(path, ["CREATE TABLE blobs (id INTEGER PRIMARY KEY, data BLOB)"],
                        [("INSERT INTO blobs (data) VALUES (?)", (sqlite3.Binary(data),))])


def live_values(path):
    """Every value of every table of a SQLite file, the schema table included, as bytes or text."""
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        tables = [name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        values = [value for row in connection.execute("SELECT * FROM sqlite_master") for value in row]
        for name in tables:
            values += [value for row in connection.execute(f'SELECT * FROM "{name}"') for value in row]
        return values
    finally:
        connection.close()


def held_by_a_value(path, needle):
    """Whether any live value holds ``needle`` (text, or bytes as given, UTF-8 or UTF-16)."""
    forms = [needle.encode(), needle.encode("utf-16-le"), needle.encode("utf-16-be")]
    for value in live_values(path):
        data = value if isinstance(value, bytes) else str(value).encode()
        if needle in str(value) or any(form in data for form in forms):
            return True
    return False


FILLER_WORDS = ("north", "river", "stone", "maple", "cloud", "amber", "field", "lantern", "harbor", "willow")


def prose(size, seed="w2-69"):
    """Plain lines that no rule finds, ``size`` characters."""
    lines, total, count = [], 0, 0
    while total < size:
        line = f"row {count:06d} {seed} {FILLER_WORDS[count % 10]} {FILLER_WORDS[(count * 7) % 10]} walks on\n"
        lines.append(line)
        total += len(line)
        count += 1
    return "".join(lines)[:size]


FREED_KINDS = ("a-freeblock", "a-free-page", "a-dropped-table", "the-unused-space-of-a-page", "a-freed-overflow-chain")


def freed_store(path, kind, text, encoding=None):
    """A SQLite store whose only copy of ``text`` is in freed space (secure_delete off, no vacuum):

    - ``a-freeblock``: a row between two others, deleted;
    - ``a-free-page``: a value of many pages, deleted (its pages go to the freelist);
    - ``a-dropped-table``: a table holding it, dropped;
    - ``the-unused-space-of-a-page``: the last row written to a page (the start of its cell area), deleted;
    - ``a-freed-overflow-chain``: a value of many pages updated to a short one.
    """
    schema = ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"]
    insert = "INSERT INTO notes (body) VALUES (?)"
    holding = f"{prose(150, 'before')} {text} {prose(150, 'after')}"
    long_holding = f"{prose(9000, 'long-before')} {text} {prose(9000, 'long-after')}"
    if kind == "a-freeblock":
        rows = [(insert, (prose(300, "a"),)), (insert, (holding,)), (insert, (prose(300, "c"),))]
        after = ["DELETE FROM notes WHERE id = 2"]
    elif kind == "a-free-page":
        rows = [(insert, (prose(300, "a"),)), (insert, (long_holding,))]
        after = ["DELETE FROM notes WHERE id = 2"]
    elif kind == "a-dropped-table":
        schema.append("CREATE TABLE gone (id INTEGER PRIMARY KEY, body TEXT)")
        rows = [(insert, (prose(300, "a"),)), ("INSERT INTO gone (body) VALUES (?)", (holding,))]
        after = ["DROP TABLE gone"]
    elif kind == "the-unused-space-of-a-page":
        rows = [(insert, (prose(300, "a"),)), (insert, (prose(300, "b"),)), (insert, (holding,))]
        after = ["DELETE FROM notes WHERE id = 3"]
    elif kind == "a-freed-overflow-chain":
        rows = [(insert, (prose(300, "a"),)), (insert, (long_holding,))]
        after = ["UPDATE notes SET body = 'short now' WHERE id = 2"]
    else:
        raise ValueError(kind)
    return sqlite_store(path, schema, rows, encoding=encoding, secure_delete=False, after=after)


def corrupt_sqlite(path, text, how):
    """A file that begins as a SQLite store but cannot be opened or read, holding ``text`` in its bytes:

    - ``garbage-after-the-header``: the 16-byte header, then plain bytes;
    - ``a-damaged-page``: a real store whose table's page is damaged (its type byte overwritten);
    - ``truncated``: a real store cut after its second page, its table's later pages missing.
    """
    path = Path(path)
    if how == "garbage-after-the-header":
        return write(path, SQLITE_HEADER + f"{prose(3000, 'g1')} {text} {prose(3000, 'g2')}".encode())
    if how == "a-damaged-page":
        sqlite_store(path, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                     [("INSERT INTO notes (body) VALUES (?)", (f"{prose(200, 'x')} {text} {prose(200, 'y')}",))])
        data = bytearray(path.read_bytes())
        page = struct.unpack(">H", data[16:18])[0] or 65536
        data[page] = 0xFF   # page 2, the table's only page: no b-tree page type
        return write(path, bytes(data))
    if how == "truncated":
        sqlite_store(path, ["CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"],
                     [("INSERT INTO notes (body) VALUES (?)", (f"{prose(100, str(n))} {text if n == 0 else ''}",))
                      for n in range(400)])
        data = path.read_bytes()
        page = struct.unpack(">H", data[16:18])[0] or 65536
        return write(path, data[: page * 3 + page // 2])
    raise ValueError(how)


def sqlite_files(top):
    found = []
    for directory, _names, files in os.walk(top):
        for name in files:
            path = Path(directory) / name
            try:
                with open(path, "rb") as handle:
                    if handle.read(16) == SQLITE_HEADER:
                        found.append(path)
            except OSError:
                pass
    return sorted(found)


def free_pages(path):
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return connection.execute("PRAGMA freelist_count").fetchone()[0]
    finally:
        connection.close()


def fts_terms_holding(path, needle, scratch):
    """The terms of every FTS5 index of the SQLite file at ``path`` that hold ``needle`` (lower case), read through
    ``fts5vocab`` on a copy of it."""
    copy = Path(scratch) / f"vocab-{hashlib.sha256(str(path).encode()).hexdigest()[:12]}.db"
    shutil.copyfile(path, copy)
    for extra in ("-wal",):
        if Path(str(path) + extra).exists():
            shutil.copyfile(str(path) + extra, str(copy) + extra)
    found = []
    connection = sqlite3.connect(copy)
    try:
        names = [name for (name, sql) in connection.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'")
                 if sql and re.search(r"USING\s+fts5", sql, re.IGNORECASE)]
        for number, name in enumerate(names):
            connection.execute(f'CREATE VIRTUAL TABLE temp.w69v{number} USING fts5vocab(main, "{name}", row)')
            found += [f"{name}: a term holding it" for (term,) in
                      connection.execute(f"SELECT term FROM temp.w69v{number} WHERE instr(term, ?) > 0",
                                         (needle.lower(),))]
    finally:
        connection.close()
        for each in (copy, Path(str(copy) + "-wal"), Path(str(copy) + "-shm"), Path(str(copy) + "-journal")):
            with contextlib.suppress(OSError):
                each.unlink()
    return found


def files_holding(top, needles, skip=()):
    """Regular files under ``top`` (links not followed) whose bytes hold any of ``needles`` (bytes)."""
    found = []
    for directory, names, files in os.walk(top):
        names[:] = [n for n in names if n not in skip and not os.path.islink(os.path.join(directory, n))]
        for name in files:
            path = Path(directory) / name
            if path.is_symlink() or not path.is_file():
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if any(needle in data for needle in needles):
                found.append(str(path.relative_to(top)))
    return sorted(found)


def word_forms(word):
    """The byte forms a word can take in a store: as written, in lower case, UTF-16 both ways."""
    forms = {word.encode(), word.lower().encode()}
    forms |= {w.encode(enc) for w in (word, word.lower()) for enc in ("utf-16-le", "utf-16-be")}
    return sorted(forms)


# --------------------------------------------------------------------------
# A rebuild project and the stand-in embedder
# --------------------------------------------------------------------------

EMBED_MODEL = "qwen3-embedding:0.6b"            # the pinned embedder (ADR-0002 §2), as Ollama's model list names it
EMBED_DIGEST = "ac6da0dfba84" + hashlib.sha256(b"w2-69 stand-in embedder").hexdigest()[:52]
DIMENSIONS = 1024                               # a vector of 4 KiB, as the pinned model's


class EmbedderStandIn:
    """A loopback Ollama endpoint (``/api/version``, ``/api/tags``, ``/api/embed``, ``/api/ps``): vectors made from
    a hash of each text, so the semantic index is built and rebuilt without a model."""

    def __init__(self):
        stand_in = self
        self.embedded = 0

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                path = self.path.split("?")[0].rstrip("/")
                if path == "/api/version":
                    reply = {"version": "0.0.0-w2-69"}
                elif path == "/api/tags":
                    reply = {"models": [{"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": EMBED_DIGEST}]}
                elif path == "/api/embed":
                    texts = asked.get("input") or []
                    texts = [texts] if isinstance(texts, str) else texts
                    stand_in.embedded += len(texts)
                    reply = {"model": EMBED_MODEL, "embeddings": [stand_in.vector(text) for text in texts]}
                elif path == "/api/ps":
                    reply = {"models": [{"name": EMBED_MODEL, "model": EMBED_MODEL, "size": 1, "size_vram": 0}]}
                else:
                    reply = {}
                payload = json.dumps(reply).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    @staticmethod
    def vector(text):
        seed = hashlib.sha256(str(text).encode()).digest()
        return [((seed[i % 32] ^ (i * 37 % 251)) - 128) / 128.0 for i in range(DIMENSIONS)]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


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
            "provenance": "written by the W2-69 tests",
            "deletion_rebuild": "authoritative; restored from git only",
        }
    return yaml.safe_dump(document, sort_keys=False)


def make_rebuild_project(sandbox, files):
    """A committed project whose ``docs/**`` and ``src/**`` are indexed and embedded, with the kernel's gitleaks
    rules; ``files`` maps paths to text."""
    project = sandbox.base / "rebuild-project"
    project.mkdir(parents=True)
    write(project / ".gitignore", ".gov-runtime/\n__pycache__/\n")
    shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    write(project / "governance/project/path-map.yaml", path_map_text({"docs": ["docs/**"], "src": ["src/**"]}))
    for rel, text in files.items():
        write(project / rel, text)
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-69 rebuild fixture")
    return project


def commit_all(project, message):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


def rebuild_environment(sandbox, embedder, with_code_tool):
    """The rebuild's environment: the stand-in embedder at OLLAMA_HOST (no real model is ever started), the runner's
    user site (``sqlite_vec``) under the temporary HOME, and the code-graph tool on PATH only when asked."""
    if with_code_tool:
        path = os.environ.get("PATH", "/usr/bin:/bin")
    else:   # gitleaks, git and python, and no code-graph tool: the code index is not built, no daemon starts
        tools = sandbox.elsewhere / "tools"
        tools.mkdir(parents=True, exist_ok=True)
        if not (tools / "gitleaks").exists():
            (tools / "gitleaks").symlink_to(REAL_GITLEAKS)
        path = f"{tools}{os.pathsep}{Path(sys.executable).parent}{os.pathsep}/usr/bin{os.pathsep}/bin"
    env = base_environment(sandbox, path=path)
    env.update({"OLLAMA_HOST": embedder.host, "GOV_QUERY_OLLAMA_HOST": embedder.host,
                "GOV_OLLAMA_BIN": str(sandbox.elsewhere / "no-ollama-here"),
                "PYTHONUSERBASE": site.getuserbase()})
    return env


@dataclass
class GovRun:
    args: tuple
    returncode: int
    stdout: str
    stderr: str

    def envelope(self):
        try:
            return json.loads(self.stdout)
        except ValueError:
            return {}

    def describe(self):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-2500:]}\n"
                f"stderr:\n{self.stderr[-2500:]}")


def run_gov(cwd, env, *args, timeout=900):
    try:
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(cwd), env=env,
                              capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {timeout} s") from None
    return GovRun(tuple(args), done.returncode, done.stdout, done.stderr)


def rebuild(project, env):
    run = run_gov(project, env, "rebuild", "--json")
    assert run.returncode == 0, f"gov rebuild --json did not succeed in the test's project\n{run.describe()}"
    return run


def store_status(run, name):
    stores = (run.envelope().get("result") or {}).get("stores") or {}
    return (stores.get(name) or {}).get("status")


def code_daemon_dir(project):
    """The code-graph tool's runtime folder for ``project`` (``gov.codeintel.daemon_dir``), or None."""
    try:
        from gov.codeintel import daemon_dir
        return Path(daemon_dir(project))
    except Exception:
        return None
