"""Support for the W2-121 acceptance tests (part a: ``gov dispatch tick`` and ``gov dispatch status``).

Everything is planted under the test's own ``tmp_path``: a project root that is a git repository with an integration
branch, one worktree per W2 (``git worktree add``), ``.tickets/<id>.md`` files, briefs, ``dispatch.yaml``, a tmp
``HOME`` with W2-20's ``gate.json``, the ``GOV_RESOURCES_*`` variables, a planted ``/proc`` folder for the marker
processes, and two stub programs (the launch command and the notifier) that record their argv and stdin to a file.
Never the real HOME, ``~/.claude``, ``~/gov-os-worktrees``, the real ``/proc`` for counting, or a real session.

``Project.tick()`` runs ``python3 -m gov.cli.main dispatch tick --root <root>`` as a child process with the tree
under test first on ``PYTHONPATH`` and no ``GIT_*`` or ``GOV_*`` variable of the session running the tests.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import gov

SRC = Path(gov.__file__).resolve().parents[1]  # the tree under test: <tree>/src
TREE = SRC.parent
GIB = 1024 ** 3
MIB = 1024 ** 2
PAGE = os.sysconf("SC_PAGE_SIZE")
GIT_DATE = "2026-11-12T00:00:00+00:00"

ISO = re.compile(r"(\d{4}-\d{2}-\d{2})([T ])(\d{2}:\d{2}:\d{2})(\.\d+)?(Z|[+-]\d{2}:?\d{2})?")


# --- stub programs ------------------------------------------------------------------------------------------------

LAUNCH_STUB = r'''
import json, os, sys, time
rec, state = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
stdin = sys.stdin.read()

def read(name, default=""):
    try:
        with open(os.path.join(rec, name)) as handle:
            return handle.read().strip()
    except OSError:
        return default

try:
    with open(os.path.join(state, "started.txt")) as handle:
        started = handle.read()
except OSError:
    started = ""
doc = {"argv": args, "stdin": stdin, "pid": os.getpid(), "sid": os.getsid(0), "cwd": os.getcwd(),
       "started_txt": started, "time": time.time()}
os.makedirs(rec, exist_ok=True)
tmp = os.path.join(rec, ".tmp-%d" % os.getpid())
with open(tmp, "w") as handle:
    handle.write(json.dumps(doc))
os.replace(tmp, os.path.join(rec, "launch-%d.json" % os.getpid()))
open(os.path.join(rec, "pid-%d" % os.getpid()), "w").close()
out = read("output.txt")
if out:
    print(out, flush=True)
time.sleep(float(read("sleep", "0") or 0))
sys.exit(int(read("exitcode", "0") or 0))
'''

NOTIFY_STUB = r'''
import json, os, sys, time
rec = sys.argv[1]
doc = {"argv": sys.argv[2:], "time": time.time()}
os.makedirs(rec, exist_ok=True)
name = "notify-%d-%d.json" % (time.time_ns(), os.getpid())
tmp = os.path.join(rec, ".tmp-" + name)
with open(tmp, "w") as handle:
    handle.write(json.dumps(doc))
os.replace(tmp, os.path.join(rec, name))
open(os.path.join(rec, "pid-%d" % os.getpid()), "w").close()
try:
    with open(os.path.join(rec, "notify-sleep")) as handle:
        nap = float(handle.read().strip() or 0)
except OSError:
    nap = 0.0
time.sleep(nap)
'''

HUNG_GIT = "#!/bin/sh\nexec sleep 8\n"


# --- small readers ------------------------------------------------------------------------------------------------

@dataclass
class Run:
    code: int
    out: str
    err: str
    seconds: float = 0.0

    def __str__(self) -> str:
        return f"exit {self.code} in {self.seconds:.1f}s\n--- stdout ---\n{self.out}\n--- stderr ---\n{self.err}"


@dataclass
class Entry:
    w2: str
    ticket: str
    brief: str
    log: str
    n: int = 0
    brief_text: str | None = None

    @property
    def line(self) -> str:
        return f"{self.w2} {self.ticket} {self.brief} {self.log}"


@dataclass
class Item:
    path: Path
    text: str

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    @property
    def fields(self) -> dict:
        out = {}
        for line in self.lines:
            m = re.match(r"^([A-Za-z][A-Za-z0-9_]*):\s*(.*)$", line)
            if m and m.group(1) not in out:
                out[m.group(1)] = m.group(2).strip()
        return out

    def line_starting(self, key: str) -> str | None:
        return next((l for l in self.lines if l.startswith(key + ":")), None)


def iso(moment: datetime.datetime | None = None) -> str:
    moment = moment or datetime.datetime.now(datetime.timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def hist(kind: str, cpu: float, mem_gib: float, hours_ago: float = 1.0) -> dict:
    at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours_ago)
    return {"kind": kind, "at": iso(at), "cpu": cpu, "mem_bytes": int(mem_gib * GIB)}


def wait_for(predicate, timeout: float = 20.0, step: float = 0.05, what: str = "the condition"):
    """A bounded poll; the predicate's last truthy value, else AssertionError."""
    end = time.monotonic() + timeout
    while True:
        value = predicate()
        if value:
            return value
        if time.monotonic() >= end:
            raise AssertionError(f"timed out after {timeout:.0f}s waiting for {what}")
        time.sleep(step)


def walk(node):
    """Every ``(key, value)`` of a JSON tree, keys of dicts and ``None`` for list members."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield k, v
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield None, v
            yield from walk(v)


def values_under(node, part: str) -> list:
    """The values of every key whose name contains ``part`` (case-insensitive)."""
    return [v for k, v in walk(node) if isinstance(k, str) and part.lower() in k.lower()]


def numbers(node) -> list[float]:
    out = []
    if isinstance(node, bool):
        return out
    if isinstance(node, (int, float)):
        return [float(node)]
    if isinstance(node, str):  # a figure written as text ("3.50")
        try:
            return [float(node.strip())]
        except ValueError:
            return out
    if isinstance(node, dict):
        for v in node.values():
            out += numbers(v)
    elif isinstance(node, list):
        for v in node:
            out += numbers(v)
    return out


def strings(node) -> list[str]:
    if isinstance(node, str):
        return [node]
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.append(str(k))
            out += strings(v)
    elif isinstance(node, list):
        for v in node:
            out += strings(v)
    return out


def close(a: float, b: float, rel: float = 0.01) -> bool:
    return abs(a - b) <= max(abs(b) * rel, 1e-9)


def has_figure(node, value: float, forms=(1.0,)) -> bool:
    """Whether the subtree holds ``value`` or ``value / f`` for each divisor in ``forms``."""
    found = numbers(node)
    return any(close(n, value / f) for n in found for f in forms)


MEM_FORMS = (1.0, 1024.0, float(MIB), float(GIB), 1e6, 1e9)


def unwrap(document):
    """A command's JSON: the API-0002 envelope's ``result``, else the document itself."""
    if isinstance(document, dict) and {"ok", "command", "result"} <= set(document):
        return document["result"]
    return document


def shift_iso(text: str, seconds: float) -> str:
    """Every ISO-8601 time in ``text`` moved ``seconds`` back (the format kept)."""
    def move(m):
        try:
            base = datetime.datetime.strptime(m.group(1) + " " + m.group(3), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return m.group(0)
        moved = base - datetime.timedelta(seconds=seconds)
        return (moved.strftime("%Y-%m-%d") + m.group(2) + moved.strftime("%H:%M:%S") + (m.group(4) or "")
                + (m.group(5) or ""))
    return ISO.sub(move, text)


def iso_leaves(node) -> list[datetime.datetime]:
    out = []
    for text in strings(node):
        for m in ISO.finditer(text):
            try:
                out.append(datetime.datetime.strptime(m.group(1) + " " + m.group(3), "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                continue
    return out


def near_now(stamps, seconds: float = 300.0) -> bool:
    """Whether some naive time read here is within ``seconds`` of now, taken as UTC or as local time."""
    utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    local = datetime.datetime.now()
    return any(abs((s - ref).total_seconds()) <= seconds for s in stamps for ref in (utc, local))


def snapshot(folder: Path) -> dict:
    """Every file and folder under ``folder``: ``{relative path: (kind, size, mtime_ns)}``."""
    out = {}
    if not folder.exists():
        return out
    for path in sorted(folder.rglob("*")):
        st = path.lstat()
        out[str(path.relative_to(folder))] = ("d" if path.is_dir() else "f", 0 if path.is_dir() else st.st_size,
                                              st.st_mtime_ns)
    return out


def today_strings() -> set[str]:
    return {datetime.datetime.now().strftime("%Y-%m-%d"),
            datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")}


# --- the planted project ------------------------------------------------------------------------------------------

def _git_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    env.update(GIT_AUTHOR_DATE=GIT_DATE, GIT_COMMITTER_DATE=GIT_DATE, GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull)
    return env


def git(cwd: Path, *args: str) -> str:
    done = subprocess.run(["git", "-c", "user.name=planted", "-c", "user.email=planted@example.invalid",
                           "-c", "commit.gpgsign=false", *args], cwd=cwd, env=_git_env(), capture_output=True,
                          text=True, timeout=60)
    assert done.returncode == 0, f"git {' '.join(args)} in {cwd}: {done.stderr}"
    return done.stdout.strip()


def ticket_md(ticket: str, status: str, wbs: str | None = None, priority: int = 2) -> str:
    lines = ["---", f"id: {ticket}", f"status: {status}", "deps: []", "links: []", "created: 2026-11-12T00:00:00Z",
             "type: task", f"priority: {priority}", "assignee: engineer"]
    if wbs:
        lines += [f"external-ref: {wbs}", f"wbs_id: {wbs}"]
    lines += ["tags: [planted]", f"title: 'planted {ticket}'", "class: implementation", "state_class: AUTHORITATIVE",
              "role: engineer", "depends_on: []", "allowed_paths: []", "reads: []", "needs: []", "waits_on: []",
              "---", f"# {ticket}", "", "A planted ticket for the W2-121 acceptance tests.", ""]
    return "\n".join(lines)


DEFAULT_BRIEF = "# Brief for the planted ticket\n\nDo the planted work and return the twelve fields.\n"


class Project:
    """A planted project; see the module's docstring."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.root = tmp / "project"
        self.home = tmp / "home"
        self.wt_root = tmp / "worktrees"
        self.rec = tmp / "records"
        self.machine_dir = tmp / "machine"
        self.proc = tmp / "proc"
        self.stubs = tmp / "stubs"
        self.cwd = tmp / "cwd"
        self.state = self.root / ".gov-runtime" / "dispatch"
        self.entries: dict[int, Entry] = {}
        self.path_prefix: str | None = None
        self.extra_env: dict = {}
        self.raw_config: str | None = None
        self._pid = 41000
        self.popens: list = []
        # the planted machine (the gate's readings) and the gate's two figures
        self.floor, self.work = GIB, GIB
        self.mem = 16 * GIB
        self.load = (0.10, 0.10, 0.10)
        self.nproc = 20
        self.busy = 1.0
        self.disk = {"free_bytes": 500 * GIB, "free_inodes": 50_000_000}
        for folder in (self.root, self.home, self.wt_root, self.rec, self.machine_dir, self.proc, self.stubs,
                       self.cwd, self.tmp / "tmp"):
            folder.mkdir(parents=True, exist_ok=True)
        (self.stubs / "launch.py").write_text(LAUNCH_STUB, encoding="utf-8")
        (self.stubs / "notify.py").write_text(NOTIFY_STUB, encoding="utf-8")
        self.config = {
            "integration_branch": "integ",
            "worktrees_root": str(self.wt_root),
            "max_leads": 5,
            "stagger_s": 0,
            "cpu_band": 1,
            "command_timeout_s": 10,
            "launch_command": [sys.executable, str(self.stubs / "launch.py"), str(self.rec), str(self.state),
                               "{ticket}", "{w2}", "{brief}", "{log}"],
            "notifier_command": [sys.executable, str(self.stubs / "notify.py"), str(self.rec)],
        }
        git(self.root, "init", "-q", "-b", "integ")
        (self.root / "README.md").write_text("planted project\n", encoding="utf-8")
        (self.root / ".tickets").mkdir()
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "planted project")
        self.write_gate()

    # --- configuration ---------------------------------------------------------------------------------------

    def cfg(self, **changes) -> None:
        self.config.update(changes)

    def cfg_drop(self, *keys: str) -> None:
        for key in keys:
            self.config.pop(key, None)

    def write_config(self) -> None:
        target = self.root / "governance" / "project" / "dispatch.yaml"
        if self.raw_config == "<absent>":
            target.unlink(missing_ok=True)
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        text = self.raw_config if self.raw_config is not None else yaml.safe_dump({"dispatch": self.config})
        target.write_text(text, encoding="utf-8")

    def write_gate(self) -> None:
        from gov.resources import config as resource_config

        data = resource_config.template(cpus=list(range(20)))
        data["memory_floor_bytes"]["value"] = int(self.floor)
        data["working_size_bytes"]["value"] = int(self.work)
        resource_config.write(data, env={"HOME": str(self.home)})

    def set_gate(self, floor_gib: float | None = None, work_gib: float | None = None) -> None:
        if floor_gib is not None:
            self.floor = int(floor_gib * GIB)
        if work_gib is not None:
            self.work = int(work_gib * GIB)
        self.write_gate()

    def set_machine(self, mem_gib=None, load=None, nproc=None, busy=None, disk_free_gib=None) -> None:
        if mem_gib is not None:
            self.mem = int(mem_gib * GIB)
        if load is not None:
            self.load = load
        if nproc is not None:
            self.nproc = nproc
        if busy is not None:
            self.busy = busy
        if disk_free_gib is not None:
            self.disk = {"free_bytes": int(disk_free_gib * GIB), "free_inodes": 50_000_000}

    def env(self) -> dict:
        (self.machine_dir / "meminfo").write_text(
            f"MemTotal:       33554432 kB\nMemAvailable:   {self.mem // 1024} kB\n", encoding="utf-8")
        (self.machine_dir / "loadavg").write_text(
            f"{self.load[0]:.2f} {self.load[1]:.2f} {self.load[2]:.2f} 1/100 1234\n", encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
        env.update(HOME=str(self.home), PYTHONPATH=str(SRC), PYTHONDONTWRITEBYTECODE="1",
                   TMPDIR=str(self.tmp / "tmp"),
                   GOV_RESOURCES_MEMINFO=str(self.machine_dir / "meminfo"),
                   GOV_RESOURCES_LOADAVG=str(self.machine_dir / "loadavg"),
                   GOV_RESOURCES_NPROC=str(self.nproc), GOV_RESOURCES_BUSY_CORES=str(self.busy),
                   GOV_RESOURCES_DISK=json.dumps(self.disk), GOV_RESOURCES_PROC=str(self.proc),
                   GOV_RESOURCES_EMBEDDING_CPU=json.dumps({"shared": 0, "query": 0}),
                   GOV_RESOURCES_EMBEDDING_CPU_NOW=json.dumps({"shared": 0, "query": 0}))
        if self.path_prefix:
            env["PATH"] = self.path_prefix + os.pathsep + env.get("PATH", "")
        env.update(self.extra_env)
        return env

    def hung_git(self) -> None:
        folder = self.tmp / "hung-bin"
        folder.mkdir(exist_ok=True)
        stub = folder / "git"
        stub.write_text(HUNG_GIT, encoding="utf-8")
        stub.chmod(0o755)
        self.path_prefix = str(folder)

    # --- tickets, worktrees, briefs ----------------------------------------------------------------------------

    def wt(self, entry: Entry) -> Path:
        return self.wt_root / entry.w2

    def add_ticket(self, n: int, *, claim: str = "both", dirty: bool = False, untracked: bool = False,
                   brief="default", priority: int = 2, name: str | None = None) -> Entry:
        """A ticket ``DAEO-a<n>`` with its worktree ``<wt_root>/W2-<n>`` and its brief.

        ``claim``: ``both`` (``in_progress`` committed on the integration branch, the worktree made after it),
        ``integration_only`` (the worktree made before the claim: its HEAD lacks it), ``worktree_only`` (the claim
        committed on the worktree's branch only), ``none``. ``brief``: ``"default"`` a complete brief, ``None`` no file,
        any other text as written."""
        w2, ticket = f"W2-{n}", f"DAEO-a{n}"
        entry = Entry(w2, ticket, f"b{n}.md" if name is None else f"{name}.md", f"{w2}-A5-run.json", n)
        tpath = self.root / ".tickets" / f"{ticket}.md"
        first = "in_progress" if claim == "both" else "open"
        tpath.write_text(ticket_md(ticket, first, w2, priority), encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", f"planted {ticket} {first}")
        git(self.root, "worktree", "add", "-q", "-b", f"work/{w2}", str(self.wt_root / w2), "integ")
        if claim == "integration_only":
            tpath.write_text(ticket_md(ticket, "in_progress", w2, priority), encoding="utf-8")
            git(self.root, "add", "-A")
            git(self.root, "commit", "-q", "-m", f"planted {ticket} claim")
        elif claim == "worktree_only":
            wpath = self.wt_root / w2 / ".tickets" / f"{ticket}.md"
            wpath.write_text(ticket_md(ticket, "in_progress", w2, priority), encoding="utf-8")
            git(self.wt_root / w2, "add", "-A")
            git(self.wt_root / w2, "commit", "-q", "-m", f"planted {ticket} claim in the worktree")
        if dirty:
            with open(self.wt_root / w2 / "README.md", "a", encoding="utf-8") as handle:
                handle.write("an uncommitted change\n")
        if untracked:
            (self.wt_root / w2 / "untracked-notes.txt").write_text("not tracked\n", encoding="utf-8")
        text = DEFAULT_BRIEF if brief == "default" else brief
        entry.brief_text = text
        if text is not None:
            self.write_brief(entry.brief, text)
        self.entries[n] = entry
        return entry

    def briefs_dir(self) -> Path:
        return self.root / ".gov-runtime" / "dispatch" / "briefs"

    def write_brief(self, name: str, text: str, folder: Path | None = None) -> Path:
        folder = folder or self.briefs_dir()
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8")
        return folder / name

    def commit(self, entry: Entry, rel: str, text: str) -> str:
        """Commit a file in the entry's worktree; the full commit id."""
        path = self.wt(entry) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        git(self.wt(entry), "add", "--", rel)
        git(self.wt(entry), "commit", "-q", "-m", f"planted {rel}")
        return git(self.wt(entry), "rev-parse", "HEAD")

    def probes(self, entry: Entry, count: int, folder: str = "docs/probes", suffix: str = ".md") -> None:
        """``count`` probe records for the entry's ticket in its worktree, committed."""
        for i in range(count):
            self.commit(entry, f"{folder}/{entry.ticket}/probe-{i + 1}{suffix}", f"probe record {i + 1}\n")

    # --- the state folder ----------------------------------------------------------------------------------------

    def ready(self, *items) -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        text = "".join((i.line if isinstance(i, Entry) else str(i)) + "\n" for i in items)
        (self.state / "ready.txt").write_text(text, encoding="utf-8")

    def land(self, text: str) -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "land.txt").write_text(text, encoding="utf-8")

    def history(self, lines: list[dict], rel: str = ".gov-runtime/dispatch/history.jsonl", append: bool = False) -> None:
        target = self.root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a" if append else "w", encoding="utf-8") as handle:
            for line in lines:
                handle.write(json.dumps(line) + "\n")

    def plant_item(self, name: str, log: str, w2: str, status: str = "DONE", read: bool = False) -> Path:
        folder = self.state / "inbox" / ("read" if read else "")
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / name
        target.write_text(f"log: {log}\nW2: {w2}\nstatus: {status}\n\nplanted item\n", encoding="utf-8")
        return target

    def items(self, read: bool = False) -> list[Item]:
        folder = self.state / "inbox" / ("read" if read else "")
        if not folder.is_dir():
            return []
        return [Item(f, f.read_text(encoding="utf-8")) for f in sorted(folder.iterdir()) if f.is_file()]

    def all_items(self) -> list[Item]:
        return self.items() + self.items(read=True)

    def mark_read(self, item: Item) -> None:
        target = self.state / "inbox" / "read"
        target.mkdir(parents=True, exist_ok=True)
        shutil.move(str(item.path), str(target / item.path.name))

    def read_json(self, name: str):
        return json.loads((self.state / name).read_text(encoding="utf-8"))

    def status_json(self) -> dict:
        return self.read_json("status.json")

    def status_text(self) -> str:
        return (self.state / "status.txt").read_text(encoding="utf-8")

    def started(self) -> list[str]:
        path = self.state / "started.txt"
        if not path.is_file():
            return []
        return [l.split()[0] for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    # --- the stubs' records ----------------------------------------------------------------------------------------

    def set_output(self, text: str) -> None:
        (self.rec / "output.txt").write_text(text, encoding="utf-8")

    def set_sleep(self, seconds: float) -> None:
        (self.rec / "sleep").write_text(str(seconds), encoding="utf-8")

    def set_exit(self, code: int) -> None:
        (self.rec / "exitcode").write_text(str(code), encoding="utf-8")

    def set_notify_sleep(self, seconds: float) -> None:
        (self.rec / "notify-sleep").write_text(str(seconds), encoding="utf-8")

    def launches(self) -> list[dict]:
        docs = []
        for f in sorted(self.rec.glob("launch-*.json"), key=lambda f: f.stat().st_mtime_ns):
            docs.append(json.loads(f.read_text(encoding="utf-8")))
        return docs

    def launched_logs(self) -> list[str]:
        return [d["argv"][-1] for d in self.launches()]

    def notifies(self) -> list[dict]:
        return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(self.rec.glob("notify-*.json"))]

    def wait_launches(self, count: int, timeout: float = 20.0) -> list[dict]:
        wait_for(lambda: len(self.launches()) >= count, timeout, what=f"{count} launch record(s) of the stub")
        return self.launches()

    def settle(self, seconds: float = 1.0) -> None:
        """A short fixed wait for a launch that would have been wrongly made to show itself (the launch is detached)."""
        time.sleep(seconds)

    def wait_exit_file(self, log: str, timeout: float = 20.0) -> str:
        path = self.state / "logs" / f"{log}.exit"
        wait_for(path.is_file, timeout, what=f"{path}")
        return path.read_text(encoding="utf-8").strip()

    # --- planted processes ---------------------------------------------------------------------------------------

    def plant_process(self, argv: list[str], rss_bytes: int = 0) -> int:
        self._pid += 1
        pid = self._pid
        folder = self.proc / str(pid)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "cmdline").write_bytes(b"\0".join(a.encode() for a in argv) + b"\0")
        pages = rss_bytes // PAGE
        (folder / "stat").write_text(
            f"{pid} (claude) S 1 {pid} {pid} 0 -1 4194304 100 0 0 0 5 5 0 0 20 0 1 0 100 1000000 {pages}\n",
            encoding="utf-8")
        (folder / "statm").write_text(f"{pages + 100} {pages} 0 0 0 0 0\n", encoding="utf-8")
        return pid

    def plant_lead(self, ticket: str, role: str = "orchestrator", rss_bytes: int = GIB // 2) -> int:
        """A running session as ``gov launch lead`` starts it: ``--settings`` JSON with ``GOV_ROLE`` and ``GOV_TICKET``."""
        settings = {"env": {"GOV_ROLE": role, "GOV_TICKET": ticket}}
        return self.plant_process(["claude", "--settings", json.dumps(settings), "--print"], rss_bytes)

    def remove_process(self, pid: int) -> None:
        shutil.rmtree(self.proc / str(pid), ignore_errors=True)

    # --- running gov -----------------------------------------------------------------------------------------------

    def _argv(self, *args: str) -> list[str]:
        return [sys.executable, "-B", "-m", "gov.cli.main", *args]

    def gov(self, *args: str, timeout: float = 90.0) -> Run:
        self.write_config()
        start = time.monotonic()
        done = subprocess.run(self._argv(*args, "--root", str(self.root)), cwd=self.cwd, env=self.env(),
                              capture_output=True, text=True, timeout=timeout)
        return Run(done.returncode, done.stdout, done.stderr, time.monotonic() - start)

    def tick(self, *extra: str, timeout: float = 90.0) -> Run:
        return self.gov("dispatch", "tick", *extra, timeout=timeout)

    def status_cmd(self, *extra: str) -> Run:
        return self.gov("dispatch", "status", *extra)

    def tick_popen(self) -> subprocess.Popen:
        self.write_config()
        proc = subprocess.Popen(self._argv("dispatch", "tick", "--root", str(self.root)), cwd=self.cwd,
                                env=self.env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.popens.append(proc)
        return proc

    def plan_ready(self, target: Path) -> Run:
        """``gov plan --open --ready <target>`` on the planted project."""
        done = subprocess.run(self._argv("plan", "--open", "--ready", str(target), "--root", str(self.root)),
                              cwd=self.cwd, env=self.env(), capture_output=True, text=True, timeout=120)
        return Run(done.returncode, done.stdout, done.stderr)

    def gate_reading(self) -> dict:
        """W2-20's gate on the planted machine (a child process, the same variables a tick has)."""
        code = ("import json; from gov.resources import gate; r = gate.read(check=True); "
                "print(json.dumps({'open': r['gate']['open'], "
                "'reasons': [gate.describe(x) for x in r['gate']['reasons']]}))")
        done = subprocess.run([sys.executable, "-B", "-c", code], cwd=self.cwd, env=self.env(),
                              capture_output=True, text=True, timeout=90)
        assert done.returncode == 0, done.stderr
        return json.loads(done.stdout.strip().splitlines()[-1])

    # --- teardown --------------------------------------------------------------------------------------------------

    def cleanup(self) -> None:
        for proc in self.popens:
            if proc.poll() is None:
                try:
                    proc.kill()
                except OSError:
                    pass
        for marker in list(self.rec.glob("pid-*")):  # only a pid that still runs one of this test's own stubs
            try:
                pid = int(marker.name.split("-", 1)[1])
                cmd = Path(f"/proc/{pid}/cmdline").read_bytes().decode("utf-8", "replace")
                if str(self.stubs) in cmd:
                    os.kill(pid, signal.SIGKILL)
            except (OSError, ValueError):
                pass


# --- reading the status ---------------------------------------------------------------------------------------------

def candidates(status_json, status_text: str, *idents: str) -> list[str]:
    """The pieces of the status that mention one of ``idents`` (a log name, a W2 id, a line's own words): the
    smallest JSON objects with a string holding it, the strings of a list, ``key: value`` of a dict keyed by it, and
    the lines of the text."""
    out: list[str] = []

    def has(text) -> bool:
        return isinstance(text, str) and any(i in text for i in idents)

    def visit(node):
        if isinstance(node, dict):
            if any(has(v) for v in node.values()):
                out.append(json.dumps(node))
            for k, v in node.items():
                if has(k):
                    out.append(f"{k}: {json.dumps(v)}")
                visit(v)
        elif isinstance(node, list):
            for v in node:
                if has(v):
                    out.append(v)
                visit(v)

    visit(status_json)
    out += [line for line in status_text.splitlines() if has(line)]
    return out


def named_with(project: Project, idents, pattern: str) -> bool:
    """Whether the status names one of ``idents`` together with a reason matching ``pattern``."""
    idents = (idents,) if isinstance(idents, str) else tuple(idents)
    status = project.status_json()
    found = candidates(status, project.status_text(), *idents)
    return any(re.search(pattern, c, re.I) for c in found)


def explain(project: Project, run: Run | None = None) -> str:
    text = project.status_text() if (project.state / "status.txt").is_file() else "(no status.txt)"
    return f"\n{run}\n--- status.txt ---\n{text}" if run else f"\n--- status.txt ---\n{text}"


def kind_entry(document, kind: str):
    """The part of a status or ``peaks.json`` that holds a kind's peak: the value under the key ``kind``, or the
    object whose ``kind`` is it."""
    for k, v in walk(document):
        if k == kind and isinstance(v, (dict, list)):
            return v
        if isinstance(v, dict) and v.get("kind") == kind:
            return v
    return None
