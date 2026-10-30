"""Support code for the W2-50 tests of the owner's DEC-853: the secrets scan's size, pool and reuse by hash.

The one interface under test is the secrets-indexing check's public command
(``python3 -m gov.secrets``, read from its declaration and run by ``sh -c`` in
a temporary project's root, as ``w2_50_support.run_check`` runs it), and
``gov check`` where it adds the runner's own limit.

**What gitleaks is given** is seen through a public means only: a stand-in
named ``gitleaks``, first on ``PATH``, that hands every decision to the real
gitleaks (the one ``PATH`` finds without it) and logs, in the test's own
``elsewhere/`` folder, what it received: its size, which of the test's own
marker words it saw, and which rule set it ran with (a short hash of the
configuration gitleaks reads: ``GITLEAKS_CONFIG_TOML``, else ``--config`` or
``GITLEAKS_CONFIG``). It never logs content. The stand-in can also:

- read its input more slowly, at a stated rate (bytes per second), while the
  real gitleaks reads it at the same time (so a run lasts about the larger of
  the two); this makes "today's fixed limit of 60 seconds is too short"
  deterministic, since sleeping only ever makes a run longer;
- on an input that holds a given marker word, never finish, kill itself by a
  signal, or exit with a code gitleaks does not give (a scan that cannot
  finish).

The stand-in reads its input from standard input (``gitleaks stdin``, how the
check runs gitleaks today and how ``gitleaks stdin --help`` describes it); for
``gitleaks dir``/``detect`` with paths, it reads the named files (throttled the
same way) before handing over.

**Fresh file.** Every run first writes ``.gov-runtime/scratch/fresh.txt`` with
a word of that run only, so every run has one store that must be scanned: its
word in the stand-in's log shows the stand-in was the gitleaks the check ran.

Planted secrets are built at run time from parts; none stands whole here, and
none is ever logged or printed by these helpers.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import w2_50_support as support

REAL_GITLEAKS = shutil.which("gitleaks")
RUNTIME = ".gov-runtime"
FRESH_REL = f"{RUNTIME}/scratch/fresh.txt"
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")

# --------------------------------------------------------------------------
# Figures (README, "tests added for the owner's DEC-853")
# --------------------------------------------------------------------------

TODAY_LIMIT_S = 60                  # today's fixed limit on one gitleaks run
WORKING_RATE = 1_000_000            # DEC-853's working figure: decided whenever gitleaks reads at 1 MB/s or faster
SLOW_RATE = 2_000_000               # the stand-in's rate in the large cases: twice the working figure
LARGE_SIZE = 160 * 1024 * 1024      # 167,772,160 bytes: 83.9 s at SLOW_RATE (> 60 s), 167.8 s at WORKING_RATE


def declared_limit_s():
    """The check's own declared limit (``timeout-seconds``), the bound on every run here."""
    data = yaml.safe_load(support.CHECK_DECLARATION.read_text(encoding="utf-8"))
    return int(data.get("timeout-seconds") or 900)


# --------------------------------------------------------------------------
# Planted values, built from parts
# --------------------------------------------------------------------------

def _body(seed, length):
    out = ""
    for count in itertools.count():
        if len(out) >= length:
            break
        out += hashlib.sha256(f"{seed}{count}".encode()).hexdigest()
    return "".join(ch.upper() if i % 3 == 0 else ch for i, ch in enumerate(out))[:length]


# A github-pat shape that a default rule finds (not a credential), and the same with one byte off, which no rule finds.
_PAT_BODY = _body("w2-50-dec-853", 36)
SECRET = "ghp" + "_" + _PAT_BODY
NEAR_SECRET = "ghp" + "-" + _PAT_BODY          # one byte from SECRET, same length
# DEC-347: a value only the project's own token rule finds, and only in the scan with its rules alone: the
# alphabet run in it is sheltered by gitleaks' built-in global allowlist under ``extend``.
_RUN = "abcdefghijklm" + "nopqrstuvwxyz"
OWN_ONLY = "sk" + "_" + "7Qd2" + _RUN + "X9"
NEAR_OWN_ONLY = "sk" + "." + "7Qd2" + _RUN + "X9"   # one byte off: no rule finds it
# A value only a rule the test adds later finds, and that rule.
ADDED_VALUE = "zqxw" + "5853added" + "604217"
ADDED_RULE = ('\n[[rules]]\nid = "w2-50-added"\ndescription = "A rule the W2-50 test adds"\n'
              "regex = '''zqxw5853added[0-9]{6}'''\nkeywords = [\"zqxw5853added\"]\n")


def marker(name):
    """A plain word only these tests write, that no rule finds."""
    return "zqxw" + "5853" + re.sub(r"[^a-z0-9]", "", name.lower())


# --------------------------------------------------------------------------
# The stand-in gitleaks
# --------------------------------------------------------------------------

_STAND_IN = r'''#!@PYTHON@
"""Stand-in for gitleaks (W2-50 acceptance tests, DEC-853): logs what it is given, hands the decision to the real one."""
import hashlib, json, os, signal, subprocess, sys, threading, time

REAL, LOG, MODE = @REAL@, @LOG@, @MODE@
try:
    with open(MODE, encoding="utf-8") as handle:
        mode = json.load(handle)
except (OSError, ValueError):
    mode = {}
rate = float(mode.get("rate") or 0)
markers = [m.encode() for m in mode.get("markers", [])]
fault, fault_marker = mode.get("fault"), (mode.get("fault_marker") or "").encode()
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


size, seen, tail = 0, set(), b""
longest = max((len(m) for m in markers + [fault_marker]), default=1)


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
    if rate:
        wait = size / rate - (time.monotonic() - began)
        if wait > 0:
            time.sleep(wait)


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
    source = sys.stdin.buffer
    while True:
        chunk = source.read1(1 << 18)
        if not chunk:
            break
        try:
            child.stdin.write(chunk)
        except (BrokenPipeError, OSError):
            pass
        take(chunk)
    try:
        child.stdin.close()
    except (BrokenPipeError, OSError):
        pass
else:
    named = [a for a in args[1:] if not a.startswith("-") and os.path.exists(a)]
    named += [p for p in (option("-s", "--source"),) if p and os.path.exists(p)]
    for top in named:
        paths = [top] if os.path.isfile(top) else [os.path.join(d, n) for d, _, ns in os.walk(top) for n in ns]
        for path in paths:
            try:
                with open(path, "rb") as handle:
                    while True:
                        chunk = handle.read(1 << 18)
                        if not chunk:
                            break
                        take(chunk)
            except OSError:
                pass
    child = subprocess.Popen([REAL, *args], stdin=sys.stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    readers = [threading.Thread(target=drain, args=(child.stdout, out)),
               threading.Thread(target=drain, args=(child.stderr, err))]
    for each in readers:
        each.start()

faulty = fault and (not fault_marker or "\0fault" in seen)
record = {"pid": os.getpid(), "sub": sub, "rules": rules(), "size": size,
          "seen": sorted(s for s in seen if s != "\0fault"), "fault": fault if faulty else None,
          "began": time.time() - (time.monotonic() - began)}


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

    def set(self, markers=(), rate=0, fault=None, fault_marker=""):
        self.mode.write_text(json.dumps({"markers": list(markers), "rate": rate, "fault": fault,
                                         "fault_marker": fault_marker}), encoding="utf-8")

    def entries(self):
        if not self.log.is_file():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line.strip()]


def install_stand_in(sandbox):
    folder = sandbox.elsewhere / "gitleaks-stand-in"
    (folder / "bin").mkdir(parents=True, exist_ok=True)
    stand_in = StandIn(folder / "bin", folder / "calls.jsonl", folder / "mode.json")
    path = stand_in.bin / "gitleaks"
    path.write_text(_STAND_IN.replace("@PYTHON@", sys.executable).replace("@REAL@", repr(REAL_GITLEAKS))
                    .replace("@LOG@", repr(str(stand_in.log))).replace("@MODE@", repr(str(stand_in.mode))),
                    encoding="utf-8")
    path.chmod(0o755)
    stand_in.set()
    return stand_in


# --------------------------------------------------------------------------
# The project and its stores
# --------------------------------------------------------------------------

def make_scan_project(sandbox, gitleaks_toml=None):
    """The fixture project with the kernel's ``.gitleaks.toml`` (extends the defaults with rules of its own)."""
    project = support.make_project(sandbox, extra={"governance/project/path-map.yaml": support.path_map_text()})
    if gitleaks_toml is None:
        shutil.copy2(support.GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    else:
        (project / ".gitleaks.toml").write_text(gitleaks_toml, encoding="utf-8")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "gitleaks rules")
    return project


def filler_block(size=1 << 20, seed="w2-50"):
    """``size`` bytes of plain lines that no rule finds."""
    words = ("north", "river", "stone", "maple", "cloud", "amber", "field", "lantern", "harbor", "willow")
    lines, total, count = [], 0, 0
    while total < size:
        line = f"row {count:09d} {seed} {words[count % 10]} {words[(count * 7) % 10]} walks past the {words[(count * 3) % 10]} gate\n"
        lines.append(line)
        total += len(line)
        count += 1
    return "".join(lines).encode()[:size - 1] + b"\n"


def text_store(path, size, placed):
    """A plain store of ``size`` bytes: filler, with ``placed`` = {offset: text} written over it (one line each)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    block = filler_block()
    with open(path, "wb") as handle:
        written = 0
        while written < size:
            part = block[: size - written]
            handle.write(part)
            written += len(part)
    with open(path, "r+b") as handle:
        for offset, text in placed.items():
            data = f" {text} ".encode()
            offset = max(0, min(offset, size - len(data) - 1))
            handle.seek(offset)
            handle.write(data)
    assert path.stat().st_size == size
    return path


def sqlite_store(path, rows):
    """A small SQLite store, as the index's ``store.db`` is: a table of text chunks."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, path TEXT, body TEXT)")
        filler = filler_block(4096).decode()
        connection.executemany("INSERT INTO chunks (path, body) VALUES (?, ?)",
                               [(f"docs/page-{i}.md", f"{filler[:1500]} {row} {filler[1500:3000]}")
                                for i, row in enumerate(rows)])
        connection.commit()
    finally:
        connection.close()
    return path


def replace_one_byte(path, old, new, keep_stat=True):
    """Change exactly one byte of ``path``: the first place where ``old`` stands becomes ``new`` (same length,
    one byte different). Size and modification time are kept when ``keep_stat``."""
    path = Path(path)
    assert len(old) == len(new) and sum(a != b for a, b in zip(old, new)) == 1
    stat = path.stat()
    data = bytearray(path.read_bytes())
    at = data.find(old.encode())
    assert at >= 0, f"{old[:8]}... is not in {path.name}"
    data[at:at + len(old)] = new.encode()
    with open(path, "r+b") as handle:
        handle.write(bytes(data))
    if keep_stat:
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    after = path.stat()
    assert after.st_size == stat.st_size and (not keep_stat or after.st_mtime_ns == stat.st_mtime_ns)


def flip_byte_at(path, offset, keep_stat=True):
    """Change the one byte at ``offset`` to another plain letter; size and modification time kept."""
    path = Path(path)
    stat = path.stat()
    with open(path, "r+b") as handle:
        handle.seek(offset)
        old = handle.read(1)
        handle.seek(offset)
        handle.write(b"q" if old != b"q" else b"z")
    if keep_stat:
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert path.stat().st_size == stat.st_size


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# A run of the check
# --------------------------------------------------------------------------

@dataclass
class ScanRun:
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float
    calls: list = field(default_factory=list)   # the stand-in's log entries of this run
    fresh: str = ""

    @property
    def output(self):
        return self.stdout + "\n" + self.stderr

    def describe(self):
        return (f"exit code: {self.returncode} after {self.seconds:.1f} s; gitleaks runs: {len(self.calls)}\n"
                f"stdout:\n{self.stdout[-1500:]}\nstderr:\n{self.stderr[-1500:]}")

    def lines_naming(self, rel):
        return [line for line in self.output.splitlines() if rel in line]

    def reuse_lines(self, rel, digest):
        """Lines that label ``rel``'s clean result as reused: they name the path and the digest."""
        return [line for line in self.lines_naming(rel) if digest in line]

    def rule_sets(self):
        """The rule sets this run's gitleaks runs used, as the fresh file's scans show them."""
        return {call["rules"] for call in self.calls if self.fresh in call["seen"]}

    def seen_under(self, word):
        """The rule sets under which the stand-in saw ``word`` in this run."""
        return {call["rules"] for call in self.calls if word in call["seen"]}

    def given(self, word):
        return bool(self.seen_under(word))


_RUN_NUMBER = itertools.count(1)


def environment(sandbox, stand_in):
    env = support.base_environment(sandbox)
    if stand_in is not None:
        env["PATH"] = f"{stand_in.bin}{os.pathsep}{env['PATH']}"
    env["XDG_CACHE_HOME"] = str(sandbox.home / ".cache")
    return env


def _kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run_scan(sandbox, project, stand_in, markers=(), rate=0, fault=None, fault_marker="", limit_s=None,
             via_gov_check=False):
    """One run of the check in ``project``'s root, with the stand-in first on PATH (``stand_in=None``: the real
    gitleaks alone). Writes the fresh file first; returns the run with the stand-in's entries of this run."""
    number = next(_RUN_NUMBER)
    fresh = marker(f"fresh{number}x{os.getpid()}")
    support.write(project / FRESH_REL, f"fresh {fresh} for this run only\n")
    before = len(stand_in.entries()) if stand_in else 0
    if stand_in:
        stand_in.set(markers=[*markers, fresh], rate=rate, fault=fault, fault_marker=fault_marker)
    limit_s = limit_s or declared_limit_s()
    if via_gov_check:
        argv, shell = support.gov_argv("check", "--json"), False
    else:
        argv, shell = support.check_command(), True
    began = time.monotonic()
    proc = subprocess.Popen(argv, shell=shell, cwd=str(project), env=environment(sandbox, stand_in),
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=limit_s)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        stdout, stderr = proc.communicate()
        code = None
    finally:
        _kill_group(proc)   # no gitleaks of this run is left behind
    seconds = time.monotonic() - began
    if stand_in:
        stand_in.set()
    calls = stand_in.entries()[before:] if stand_in else []
    return ScanRun(code, stdout, stderr, seconds, calls, fresh)


def assert_stand_in_used(run):
    assert run.given(run.fresh), (
        "the stand-in gitleaks on PATH never saw this run's fresh file: the check did not run the gitleaks PATH "
        f"finds, so what it was given cannot be seen\n{run.describe()}")


def tree_snapshot(top, skip=()):
    """``relative path -> sha256`` of the regular files under ``top``; folders in ``skip`` (real paths) left out."""
    top = Path(top)
    skip = {os.path.realpath(str(s)) for s in skip}
    result = {}
    for directory, names, files in os.walk(top):
        names[:] = [n for n in names if os.path.realpath(os.path.join(directory, n)) not in skip
                    and not os.path.islink(os.path.join(directory, n))]
        for name in files:
            path = Path(directory) / name
            if path.is_symlink() or not path.is_file():
                continue
            try:
                result[str(path.relative_to(top))] = sha256_file(path)
            except OSError:
                pass
    return result
