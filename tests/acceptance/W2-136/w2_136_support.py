"""Support for the W2-136 acceptance tests: planted ticket stores, the ``gov plan`` runner, the readers of its text,
JSON and ready-list output, the tree's state, and the source scan of S10.

Every store is a temporary git repository: ``.tickets/<id>.md`` files with YAML front matter (the fields real tickets
carry, plus W2-128's ``reads:``, ``needs:`` and ``waits_on:`` and DEC-1088's ``plan_override:``) and a few tracked
files, all committed with a fixed date, so two stores with the same files are the same commit. Never this
repository's ``.tickets/``.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import gov

SRC = Path(gov.__file__).resolve().parents[1]  # the tree under test: <tree>/src, as gov accept's PYTHONPATH names it
TREE = SRC.parent
GIT_DATE = "2026-11-07T00:00:00+00:00"
WAIT_CODES = ("NEEDS_WHAT_WRITES", "WRITES_OVERLAP", "DEPENDS_ON", "WAITS_ON")
# The dispatcher's own rules for a ready-list line (governance/project/orchestration/tools/dispatch/dispatcher.py:
# read_list skips blank and "#" lines and splits on blanks; why_not wants 4 or 5 fields and a lead log name).
DISPATCHER = TREE / "governance/project/orchestration/tools/dispatch/dispatcher.py"
LOGNAME = re.compile(r"^[A-Za-z0-9][\w.-]*-A5-[\w.-]+\.json$")
BATCH_HEADER = re.compile(r"^#\s*batch\s+(\d+)\b", re.I)


# --- the planted store ----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class T:
    """One planted ticket. ``None`` for ``reads``, ``needs`` or ``waits_on`` leaves the key out; ``deps`` ``None`` is
    ``depends_on``'s list; ``wbs`` ``None`` leaves out ``wbs_id`` and ``external-ref``."""
    id: str
    wbs: str | None
    status: str = "open"
    priority: int = 2
    writes: tuple = ()
    reads: tuple | None = ()
    needs: tuple | None = ()
    waits_on: tuple | None = ()
    depends_on: tuple = ()
    deps: tuple | None = None
    plan_override: str | None = None
    role: str = "engineer"

    def but(self, **changes) -> "T":
        return T(**{**self.__dict__, **changes})


def _q(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _block(key: str, items, comment: str = "") -> str:
    if not items:
        return f"{key}: []\n"
    return f"{key}:\n" + "".join(f"- {_q(item)}{comment}\n" for item in items)


def render(t: T) -> str:
    deps = t.depends_on if t.deps is None else t.deps
    lines = ["---\n", f"id: {t.id}\n", f"status: {t.status}\n", f"deps: [{', '.join(deps)}]\n", "links: []\n",
             "created: 2026-11-07T00:00:00Z\n", "type: task\n", f"priority: {t.priority}\n",
             f"assignee: {t.role}\n"]
    if t.wbs:
        lines.append(f"external-ref: {t.wbs}\n")
    lines.append("tags: [planted]\n")
    if t.wbs:
        lines.append(f"wbs_id: {t.wbs}\n")
    lines += [f"title: {_q('planted ticket ' + (t.wbs or t.id))}\n", "class: implementation\n",
              "state_class: AUTHORITATIVE\n", f"role: {t.role}\n", _block("depends_on", t.depends_on),
              _block("allowed_paths", t.writes)]
    if t.reads is not None:
        lines.append(_block("reads", t.reads))
    if t.needs is not None:
        lines.append(_block("needs", t.needs))
    if t.waits_on is not None:
        lines.append(_block("waits_on", t.waits_on, "  # planted: the work it waits on"))
    if t.plan_override:
        lines.append(f"plan_override: {t.plan_override}\n")
    lines += ["---\n", f"# {t.wbs or t.id} planted\n", "\n", "A planted ticket for the W2-136 acceptance tests.\n"]
    return "".join(lines)


def _git_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_DATE=GIT_DATE, GIT_COMMITTER_DATE=GIT_DATE, GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull)
    return env


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.name=planted", "-c", "user.email=planted@example.invalid",
                    "-c", "commit.gpgsign=false", *args], cwd=root, env=_git_env(), check=True,
                   capture_output=True, timeout=60)


def commit(root: Path, message: str = "planted") -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message)


class Store:
    """A planted store: its root, its tickets, and how a ticket's names (its id, its WBS id) read back."""

    def __init__(self, root: Path, tickets):
        self.root = root
        self.tickets = {t.id: t for t in tickets}
        wbs = [t.wbs for t in tickets if t.wbs]
        self.names = {t.id: t.id for t in tickets}
        self.names.update({t.wbs: t.id for t in tickets if t.wbs and wbs.count(t.wbs) == 1})

    def resolve(self, token: str) -> str:
        token = token.strip().strip(",;:")
        return self.names.get(token, token)

    def path(self, tid: str) -> Path:
        return self.root / ".tickets" / f"{tid}.md"

    def mentions(self, text: str, tid: str) -> bool:
        t = self.tickets[tid]
        return any(re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text) for name in (t.id, t.wbs) if name)

    def rewrite(self, t: T, *, keep_mtime: bool = True) -> None:
        """Write the ticket's file anew (its mtime kept, so a cache keyed on it would go stale) and commit it."""
        path = self.path(t.id)
        before = path.stat()
        path.write_text(render(t), encoding="utf-8")
        if keep_mtime:
            os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.tickets[t.id] = t
        commit(self.root, f"edit {t.id}")


TRACKED = ("README.md",)


def build(root: Path, tickets, files=(), order=None, *, with_tickets: bool = True) -> Store:
    """The store at ``root`` (made here): the tickets written in ``order`` (indices; default as given), the files
    tracked, all committed with the fixed date."""
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
    for rel in (*TRACKED, *files):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"planted {rel}\n", encoding="utf-8")
    tickets = list(tickets)
    if with_tickets:
        (root / ".tickets").mkdir()
        for i in (order if order is not None else range(len(tickets))):
            (root / ".tickets" / f"{tickets[i].id}.md").write_text(render(tickets[i]), encoding="utf-8")
    commit(root)
    return Store(root, tickets)


# --- running gov plan -----------------------------------------------------------------------------------------------

@dataclass
class Run:
    code: int
    out: str
    err: str

    def __str__(self) -> str:
        return f"exit {self.code}\n--- stdout ---\n{self.out}\n--- stderr ---\n{self.err}"


def env() -> dict:
    """The child's environment: the tree under test first on the path; no GOV_* or GIT_* of the session running
    the tests (its role and ticket would otherwise reach the command)."""
    out = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    out.update(PYTHONPATH=str(SRC), PYTHONDONTWRITEBYTECODE="1")
    return out


def run(root: Path, *args: str, cwd: Path | None = None) -> Run:
    """``gov plan <args> --root <root>`` in a child process, from an empty working folder beside the store."""
    if cwd is None:
        cwd = root.parent / (root.name + "-cwd")
        cwd.mkdir(exist_ok=True)
    done = subprocess.run([sys.executable, "-B", "-m", "gov.cli.main", "plan", *args, "--root", str(root)],
                          cwd=cwd, env=env(), capture_output=True, text=True, timeout=120)
    return Run(done.returncode, done.stdout, done.stderr)


# --- reading the plan -----------------------------------------------------------------------------------------------

FIRST = re.compile(r"^gov plan: (\d+) tickets?, (\d+) batch(?:es)?, (\d+) waits?(?: \((.*)\))?\s*$")
BATCH = re.compile(r"^\s*batch (\d+): ?(.*)$")
WAIT = re.compile(r"^\s*(\S+) waits for (.+?) \(([A-Z][A-Z_]+)(?: ([^)]*))?\)\s*$")


@dataclass
class Plan:
    n: int
    b: int
    w: int
    codes: set
    batches: list      # [set of ticket ids], batch 1 first
    waits: list        # [(waiter, waited for, code, on)]
    lines: list

    @property
    def triples(self) -> set:
        return {(a, b, c) for a, b, c, _ in self.waits}

    def where(self, tid: str) -> int:
        """The batch number (1-based) of the ticket; 0 when it is in none."""
        return next((k for k, batch in enumerate(self.batches, 1) if tid in batch), 0)


def text_plan(out: str, store: Store, run_: Run | None = None) -> Plan:
    lines = out.splitlines()
    first = FIRST.match(lines[0]) if lines else None
    assert first, f"no first line 'gov plan: N tickets, B batches, W waits (codes...)':\n{run_ or out}"
    n, b, w = (int(first.group(i)) for i in (1, 2, 3))
    codes = set(re.findall(r"[A-Z][A-Z_]+[A-Z]", first.group(4) or ""))
    batches, waits = {}, []
    for line in lines[1:]:
        m = BATCH.match(line)
        if m:
            batches[int(m.group(1))] = {store.resolve(x) for x in m.group(2).split(",") if x.strip()}
            continue
        m = WAIT.match(line)
        if m:
            for waited in m.group(2).split(","):
                waits.append((store.resolve(m.group(1)), store.resolve(waited), m.group(3), m.group(4) or ""))
    assert sorted(batches) == list(range(1, len(batches) + 1)), f"batch lines not numbered 1..B:\n{out}"
    return Plan(n, b, w, codes, [batches[k] for k in sorted(batches)], waits, lines)


def entries(node, code: str | None = None) -> list[dict]:
    """Every dict in the JSON result that carries a ``code`` (that ``code`` when given)."""
    found = []
    if isinstance(node, dict):
        if isinstance(node.get("code"), str) and (code is None or node["code"] == code):
            found.append(node)
        for value in node.values():
            found += entries(value, code)
    elif isinstance(node, list):
        for value in node:
            found += entries(value, code)
    return found


def strings(node) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [s for value in node.values() for s in strings(value)]
    if isinstance(node, list):
        return [s for value in node for s in strings(value)]
    return []


def json_mentions(store: Store, node, tid: str) -> bool:
    return any(store.mentions(s, tid) for s in strings(node))


def json_plan(result: dict, store: Store) -> Plan:
    assert isinstance(result, dict) and "batches" in result, f"the result holds no 'batches': {result!r}"
    batches = []
    for batch in result["batches"]:
        ids = batch.get("tickets", []) if isinstance(batch, dict) else batch
        batches.append({store.resolve(str(x)) for x in ids})
    waits = []
    for wait in result.get("waits", []):
        waited = wait.get("waits_for")
        for x in (waited if isinstance(waited, list) else [waited]):
            waits.append((store.resolve(str(wait.get("ticket"))), store.resolve(str(x)), wait.get("code"),
                          wait.get("on") or ""))
    codes = {e["code"] for e in entries(result)}
    tickets = result.get("tickets")
    n = len(tickets) if isinstance(tickets, list) else tickets
    return Plan(n, len(batches), len(waits), codes, batches, waits, [])


def envelope(run_: Run) -> dict:
    try:
        data = json.loads(run_.out)
    except ValueError:
        raise AssertionError(f"--json printed no single JSON document:\n{run_}") from None
    assert isinstance(data, dict) and {"ok", "command", "result"} <= set(data), f"not the shared envelope:\n{run_}"
    return data


def lines_with(plan: Plan, code: str) -> list[str]:
    return [line for line in plan.lines if code in line]


# --- the ready list -------------------------------------------------------------------------------------------------

def read_ready(text: str, store: Store) -> tuple[list, list[str]]:
    """``(batches, faults)``: the entries grouped under their ``# batch k`` headers (as sets of ticket ids, batch 1
    first) and every line that is not a comment, a blank or an entry of the dispatcher's form."""
    groups: dict[int, list] = {}
    current, faults = None, []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            m = BATCH_HEADER.match(line)
            if m:
                current = int(m.group(1))
                groups.setdefault(current, [])
            continue
        entry = line.split()
        ok = len(entry) in (4, 5) and (len(entry) == 4 or entry[4].startswith("first="))
        if ok:
            w2, tid, brief, log = entry[:4]
            t = store.tickets.get(tid)
            ok = (t is not None and w2 == t.wbs and brief.endswith(".md") and LOGNAME.match(log) is not None
                  and log.startswith(f"{w2}-A5-") and current is not None)
        if not ok:
            faults.append(raw)
            continue
        groups[current].append(entry[1])
    assert sorted(groups) == list(range(1, len(groups) + 1)), f"batch headers not numbered 1..B:\n{text}"
    return [groups[k] for k in sorted(groups)], faults


def ready_text(batches) -> str:
    """A planted approved ready list in the form the README states (``# batch k`` headers, dispatcher lines)."""
    out = ["# the approved ready list (planted for the W2-136 acceptance tests)\n"]
    for k, batch in enumerate(batches, 1):
        out.append(f"# batch {k}\n")
        out += [f"{t.wbs} {t.id} {t.wbs}-A5-plan.md {t.wbs}-A5-plan.json\n" for t in batch]
    return "".join(out)


# --- the tree's state -----------------------------------------------------------------------------------------------

def state(folder: Path) -> dict:
    """Every entry under ``folder`` but ``.git/``: a folder as itself, a file by its content's hash, mode and mtime."""
    out = {}
    for here, dirs, files in os.walk(folder):
        rel = os.path.relpath(here, folder)
        if rel == ".":
            dirs[:] = [d for d in dirs if d != ".git"]
        out[rel + "/"] = "dir"
        for name in files:
            p = os.path.join(here, name)
            st = os.lstat(p)
            digest = hashlib.sha256(Path(p).read_bytes()).hexdigest() if os.path.isfile(p) else os.readlink(p)
            out[os.path.normpath(os.path.join(rel, name))] = (digest, st.st_mode, st.st_mtime_ns)
    return out


# --- S10's source scan ----------------------------------------------------------------------------------------------

PLAN_CMD = re.compile(r"(?<![\w.-])gov(?:\.cli\.main)?\s+plan(?![\w-])")


def _plan_module(name: str) -> bool:
    return name == "gov.plan" or name.startswith("gov.plan.")


def _gov_word(word: str) -> bool:
    return os.path.basename(word) == "gov" or word == "gov.cli.main" or word.endswith("gov/cli/main.py")


def uses_plan(path: Path) -> list[str]:
    """How the file imports ``gov.plan`` or runs ``gov plan``: an import, an import by name, a command string, or a
    command list; empty when it does neither. A shell script is read line by line, comments left out."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix != ".py":
        return [line.strip() for line in text.splitlines()
                if not line.lstrip().startswith("#") and PLAN_CMD.search(line)]
    return uses_plan_text(text)


def uses_plan_text(text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ["the file does not parse, so it cannot be shown free of gov plan"]
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docstrings.add(id(first.value))
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            hits += [f"import {a.name}" for a in node.names if _plan_module(a.name)]
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if _plan_module(module) or (module == "gov" and any(a.name == "plan" for a in node.names)):
                hits.append(f"from {module} import ...")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            if _plan_module(node.value) or PLAN_CMD.search(node.value):
                hits.append(repr(node.value))
        elif isinstance(node, (ast.List, ast.Tuple)):
            words = [e.value if isinstance(e, ast.Constant) and isinstance(e.value, str) else None for e in node.elts]
            if any(a is not None and b == "plan" and _gov_word(a) for a, b in zip(words, words[1:])):
                hits.append(repr(words))
    return hits
