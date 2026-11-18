"""Support code for the W2-107 acceptance tests: gitleaks verdicts remembered by content hash (DEC-966 item 4).

The interfaces under test are public only: ``gov.secrets.indexable(root, paths)``, ``gov.secrets.path_holds_secret(root,
path)``, ``gov.secrets.scan_counts()``, the variables ``GOV_SECRETS_CACHE`` and ``GOV_SECRETS_FULL_SCAN``, and the cache
file as a file. gitleaks is a stand-in first on ``PATH`` that counts its scan calls in a log of its own and hands every
call, unchanged, to the real gitleaks (found before any test changes ``PATH``). A scan call is one gitleaks process given
texts to judge: ``gitleaks stdin`` (one text; a path's names) or ``gitleaks dir`` (folder mode, DEC-1183 (2): a whole
batch of texts, each a numbered file of a private folder, one process per rule set). The log holds one line a call: the
sub-command and the sha256 of the rule set it was given; never content.

What a call costs, so what a case may expect: a text judged by ``indexable`` costs one ``dir`` call per rule set for its
whole batch (up to nineteen texts with two rule sets are one batch), a path judged by ``path_holds_secret`` one ``stdin``
call per rule set each. A case never hard-codes a number: it takes the cost of the same work with no cache (``uncached``)
as the base, and expects that, or nothing when every text is remembered.

The code under test is the ``gov`` the run's ``PYTHONPATH`` gives (DEC-732): in-process cases import it, and every child
process gets the folder that ``gov`` was imported from, so a child runs the same code.

The planted secret and row W2-L423's rule's keyword are joined at run time from parts: no file of this suite holds one
whole, and none is printed (helpers return paths, booleans and counts).
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

import gov
from gov import secrets as gov_secrets

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
RUNNER = HERE / "w2_107_run.py"
REAL_GITLEAKS = shutil.which("gitleaks")  # before any case puts a stand-in first on PATH
REAL_GIT = shutil.which("git")
BASE_PATH = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
GOV_SRC = str(Path(gov.__file__).resolve().parents[1])  # the folder the run's ``gov`` comes from
CACHE_NAME = "secrets-scan.sqlite"
CHILD_TIMEOUT_S = 180  # a child that has not answered by then is taken to hang
SETTINGS = ("GOV_SECRETS_CACHE", "GOV_SECRETS_FULL_SCAN", "XDG_CACHE_HOME")
needs_tools = pytest.mark.skipif(REAL_GITLEAKS is None or REAL_GIT is None, reason="gitleaks or git is not on PATH")

# The path map: everything is governance memory, but ``exports/`` is also product memory, so a file there is dropped.
MAP = ("namespaces:\n"
       "  everything: {paths: ['**'], memory_class: governance}\n"
       "  exports: {paths: ['exports/**'], memory_class: product}\n")


def joined(*parts):
    """``parts`` joined at run time (a constant expression would be folded whole into the compiled file)."""
    return "".join(parts)


def planted():
    """The planted secret: a string of the project's canary rule, joined at run time."""
    return joined("ARGUS", "_TOKEN", "_CAN", "ARY", "_4WM8")


KEYWORD = joined("sour", "ceg", "raph")  # the first keyword of row W2-L423's rule


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def make_project(root, extra_rules=""):
    """A project at ``root``: the kernel's ``.gitleaks.toml`` (gitleaks' defaults and its own rules, so two rule sets),
    plus ``extra_rules``, and a path map whose ``**`` is governance memory and whose ``exports/**`` is product memory."""
    root = Path(root)
    write(root / "governance/project/path-map.yaml", MAP)
    write(root / ".gitleaks.toml", GITLEAKS_TEMPLATE.read_text(encoding="utf-8") + extra_rules)
    return root


def put(root, files):
    """Each ``rel: text`` of ``files`` written under ``root``; the relative paths, in order."""
    for rel, text in files.items():
        write(Path(root) / rel, text)
    return list(files)


# --------------------------------------------------------------------------
# The stand-in gitleaks
# --------------------------------------------------------------------------

SCAN_COMMANDS = ("stdin", "dir")  # the sub-commands that are given texts to judge


@dataclass(frozen=True)
class Engine:
    """A stand-in gitleaks: ``folder`` holds it (put first on PATH), ``log`` counts its scan calls."""
    folder: Path
    log: Path
    fail: Path  # while this file exists the stand-in cannot decide (see ``make_engine``)

    @property
    def binary(self):
        return self.folder / "gitleaks"

    def calls(self):
        """How many scan calls (``gitleaks stdin`` and ``gitleaks dir``: a process given texts to judge) this stand-in
        has had."""
        return sum(self.count(command) for command in SCAN_COMMANDS)

    def count(self, command):
        """How many calls of one sub-command (``stdin`` or ``dir``) this stand-in has had."""
        if not self.log.exists():
            return 0
        return sum(1 for line in self.log.read_text(encoding="utf-8").splitlines() if line.startswith(f"{command} "))

    def path(self):
        """A PATH with this stand-in first, then the runner's own."""
        return f"{self.folder}{os.pathsep}{BASE_PATH}"


_STANDIN = '''import hashlib, os, sys
# W2-107 stand-in gitleaks, {tag}: counts its scan calls and hands every call, unchanged, to the real gitleaks.
REAL = {real!r}
LOG = {log!r}
FAIL = {fail!r}
args = sys.argv[1:]
if args[:1] in (["stdin"], ["dir"]):
    rules = os.environ.get("GITLEAKS_CONFIG_TOML", "").encode("utf-8", "replace")
    handle = os.open(LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(handle, (args[0] + " " + hashlib.sha256(rules).hexdigest() + "\\n").encode())
    finally:
        os.close(handle)
    if os.path.exists(FAIL):
        mode = open(FAIL, encoding="utf-8").read().strip()
        if mode == "all" or os.path.exists(FAIL + ".first"):
            if args[0] == "stdin":
                sys.stdin.buffer.read()
            print("W2-107 stand-in: this gitleaks cannot decide", file=sys.stderr)
            sys.exit(1)
        open(FAIL + ".first", "w").close()
os.execv(REAL, [REAL] + args)
'''


def make_engine(folder, tag="a"):
    """A stand-in gitleaks in ``folder``; ``tag`` makes its bytes its own (another tag, another engine).

    While ``engine.fail`` exists, its scan calls (``stdin`` and ``dir``) exit 1 (gitleaks could not decide): every one when the file says
    ``all``; every one after the first when it says ``after-first``.
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    engine = Engine(folder, folder.parent / f"{folder.name}-calls.log", folder.parent / f"{folder.name}-fail")
    write_standin(engine, tag)
    return engine


def write_standin(engine, tag):
    """(Re)write the stand-in's bytes in place, with ``tag`` in them."""
    body = _STANDIN.format(tag=tag, real=REAL_GITLEAKS, log=str(engine.log), fail=str(engine.fail))
    engine.binary.write_text(f"#!{sys.executable}\n" + body, encoding="utf-8")
    engine.binary.chmod(engine.binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def counted(engines, work):
    """``work()``'s result, and how many scan calls ``engines`` (one, or several) had during it."""
    engines = engines if isinstance(engines, (list, tuple)) else [engines]
    before = sum(engine.calls() for engine in engines)
    result = work()
    return result, sum(engine.calls() for engine in engines) - before


@contextlib.contextmanager
def cache_off():
    """``GOV_SECRETS_CACHE`` set to the empty string for the block: no cache at all, every text scanned."""
    old = os.environ.get("GOV_SECRETS_CACHE")
    os.environ["GOV_SECRETS_CACHE"] = ""
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("GOV_SECRETS_CACHE", None)
        else:
            os.environ["GOV_SECRETS_CACHE"] = old


def uncached(engine, work):
    """``work()`` with no cache: its result and its scan calls (what a scan of the same texts costs in full)."""
    with cache_off():
        return counted(engine, work)


def cost(engine, work):
    """What ``work()`` costs in scan calls with no cache: the base a case expects when it scans every text it is given
    (one ``dir`` call per rule set for a batch of files, one ``stdin`` call per rule set for each path name)."""
    return uncached(engine, work)[1]


def texts_judged(work):
    """``work()``'s result and how many file contents it gave to gitleaks (``scanned``) and answered from the record
    (``remembered``), by the public ``scan_counts()``. One ``dir`` call judges a whole batch, so the calls say how many
    processes ran; this says how many texts they judged."""
    before = gov_secrets.scan_counts()["content"]
    result = work()
    after = gov_secrets.scan_counts()["content"]
    return result, {key: after[key] - before[key] for key in ("scanned", "remembered")}


def cache_files(cache):
    """The cache file and its ``-wal`` and ``-shm`` companions that exist."""
    cache = Path(cache)
    return [path for path in (cache, Path(f"{cache}-wal"), Path(f"{cache}-shm")) if path.exists()]


def files_under(top):
    """Every file under ``top``, as relative POSIX paths."""
    top = Path(top)
    return sorted(path.relative_to(top).as_posix() for path in top.rglob("*") if path.is_file() or path.is_symlink())


# --------------------------------------------------------------------------
# A repository built from scratch (row W2-L423's exemption needs a real commit of the project)
# --------------------------------------------------------------------------

_GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "W2-107 acceptance", "GIT_AUTHOR_EMAIL": "w2-107@example.invalid",
    "GIT_COMMITTER_NAME": "W2-107 acceptance", "GIT_COMMITTER_EMAIL": "w2-107@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-31T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-31T12:00:00+00:00",
}


def git(root, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(_GIT_IDENTITY, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    done = subprocess.run([REAL_GIT or "git", "-C", str(root), "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, timeout=120, env=env)
    assert done.returncode == 0, f"git {args[0]} failed in {Path(root).name}: exit {done.returncode}"
    return done.stdout.strip()


def entropy(text):
    """Shannon entropy in bits a character, as gitleaks computes it for a rule's ``entropy`` floor."""
    counts = {char: text.count(char) for char in set(text)}
    return -sum(n / len(text) * math.log2(n / len(text)) for n in counts.values())


def make_repository(root):
    """A project at ``root`` that is a git repository with one commit; the commit's id, above the entropy floor of row
    W2-L423's rule (the message gains a counter until it is)."""
    make_project(root)
    write(Path(root) / "src/page.txt", "W2-107: the first page\n")
    git(root, "init", "-q")
    git(root, "add", "src/page.txt")
    tree = git(root, "write-tree")
    for counter in range(64):
        sha = git(root, "commit-tree", tree, "-m", f"W2-107: the first commit ({counter})")
        if entropy(sha) >= 3.3:
            git(root, "update-ref", "HEAD", sha)
            return sha
    raise AssertionError("no commit id above the entropy floor in 64 tries")


def hex_of(seed):
    """40 hex digits above the entropy floor, drawn from a hash of ``seed``: no object of any repository."""
    for counter in range(64):
        value = hashlib.sha256(f"W2-107|{seed}|{counter}".encode()).hexdigest()[:40]
        if entropy(value) >= 3.3:
            return value
    raise AssertionError("no hex value above the entropy floor in 64 tries")


def review_line(value):
    """A review-log line naming row W2-L423's keyword and, after it, ``value`` alone between spaces."""
    return f"{KEYWORD} review log: reviewed commit {value} at noon\n"


# --------------------------------------------------------------------------
# The filter in a child process of its own
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ChildRun:
    indexable: list | None   # what ``indexable`` returned, or None when it raised
    names: list               # ``path_holds_secret`` per name asked, in order
    counts: dict | None       # ``scan_counts()`` at the end, or None where there is none
    error: str | None         # the type of what was raised, or None
    gov: str                  # the file ``gov.secrets`` was imported from
    seconds: float


def child_env(engine, cache=..., home=None, extra=None, drop=()):
    """The environment of a child: the runner's own, the stand-in first on PATH, the run's ``gov`` on PYTHONPATH.

    ``cache`` sets ``GOV_SECRETS_CACHE`` (None leaves it unset); ``drop`` names variables to unset.
    """
    env = {key: value for key, value in os.environ.items() if key not in SETTINGS}
    env["PATH"] = engine.path() if engine is not None else BASE_PATH
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [GOV_SRC, os.environ.get("PYTHONPATH")]))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if home is not None:
        env["HOME"] = str(home)
    if cache is not ... and cache is not None:
        env["GOV_SECRETS_CACHE"] = str(cache)
    env.update(extra or {})
    for name in drop:
        env.pop(name, None)
    return env


def start_child(root, paths, names, env):
    """A child process that runs ``indexable(root, paths)`` and then ``path_holds_secret(root, name)`` per name."""
    request = json.dumps({"root": str(root), "paths": list(paths), "names": list(names)})
    proc = subprocess.Popen([sys.executable, str(RUNNER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, cwd=str(root))
    return proc, request, time.monotonic()


def finish_child(started):
    proc, request, start = started
    try:
        out, err = proc.communicate(request.encode(), timeout=CHILD_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise AssertionError(f"the filter did not answer within {CHILD_TIMEOUT_S} s: it hangs") from None
    seconds = time.monotonic() - start
    assert proc.returncode == 0, f"the child runner failed (exit {proc.returncode}): {err.decode()[-600:]}"
    data = json.loads(out.decode().strip().splitlines()[-1])
    return ChildRun(data["indexable"], data["names"], data["counts"], data["error"], data["gov"], seconds)


def run_child(root, paths, names, env):
    return finish_child(start_child(root, paths, names, env))
