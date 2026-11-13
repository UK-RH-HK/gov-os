"""Support for W2-147's acceptance tests: planted ticket stores, the oracle, and integrate's plan code from git.

- **Planted stores** (``plant``): each ticket a ``.tickets/<name>.md`` file in a temporary folder, never this
  repository's ``.tickets/``. The file name is free (the ticket's id is in its frontmatter), so a shuffled file order
  is a shuffled set of names.
- **The oracle** (``cycles``, ``expected_breaks``, ``kept_waits``): read from the planted graph alone, never from the
  code under test. A cycle is a strongly connected component with two or more tickets, or one ticket that waits on
  itself; its break falls on its first ticket by the fixed key (priority, then WBS order, then id), and only that
  ticket's waits on tickets of the same component are broken.
- **Today's code** (``today``): ``src/gov/plan/*.py`` as ``w2/integrate`` held them at ``PIN``, read with
  ``git show`` and loaded as a package of its own (``w2147_today_plan``) beside the running tree's.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
PIN = "003f0bc23d47"  # w2/integrate's head on 2026-11-09; src/gov/plan last changed at 69aa361ab73c (W2-136)
PLAN_FILES = ("__init__", "overlap", "tickets", "derive", "render", "command")
TODAY = "w2147_today_plan"
BREAK = "CYCLE_TIEBREAK"


@dataclass(frozen=True)
class T:
    """One planted ticket: ``waits`` are its ``waits_on`` entries, each an id (or WBS id), with a reason or not."""
    id: str
    wbs: str
    priority: int = 1
    waits: tuple = ()
    status: str = "open"
    extra: dict = field(default_factory=dict)

    def front(self) -> dict:
        n = re.sub(r"\W", "_", self.id.lower())
        front = {"id": self.id, "status": self.status, "priority": self.priority, "wbs_id": self.wbs,
                 "role": "engineer", "allowed_paths": [f"src/w2147/{n}.py"], "depends_on": [], "deps": [],
                 "needs": []}
        if self.waits:
            front["waits_on"] = list(self.waits)
        front.update(self.extra)
        return front


def wait_ids(t: T) -> list[str]:
    """The ids its ``waits_on`` entries name: the first word, as the ticket form writes ``W2-12 — the reason``."""
    return [entry.split()[0] for entry in t.waits if isinstance(entry, str)]


def plant(root: Path, tickets, names=None, files: dict | None = None) -> Path:
    """A fresh store at ``root``: ``names[i]`` is the file name of ``tickets[i]`` (default ``<id>.md``)."""
    if root.exists():
        shutil.rmtree(root)
    folder = root / ".tickets"
    folder.mkdir(parents=True)
    for rel, text in (files or {}).items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    pairs = list(zip(tickets, names or [f"{t.id}.md" for t in tickets]))
    for t, name in reversed(pairs) if names else pairs:  # written in another order too
        front = t.front()
        text = "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n# " + t.id + "\n"
        (folder / name).write_text(text, encoding="utf-8")
    return root


def shuffled_names(tickets, seed: int) -> list[str]:
    """File names whose sorted order is a permutation of the tickets' order, different for each seed."""
    n = len(tickets)
    perm = [(i * (2 * seed + 3) + seed) % n for i in range(n)] if n > 1 else [0]
    if sorted(perm) != list(range(n)):
        perm = list(reversed(range(n))) if seed % 2 else list(range(n))
    return [f"f{seed}-{perm[i]:02d}-{chr(97 + (i * 7 + seed) % 26)}.md" for i in range(n)]


# -- running gov plan ------------------------------------------------------------------------------------------------

def run(root: Path, *flags: str) -> tuple[int, str]:
    """``gov plan --root <root> [flags]`` in process on the running tree: (exit code, stdout)."""
    from gov.cli.main import main

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            code = main(["plan", "--root", str(root), *flags])
        except SystemExit as stop:
            code = stop.code
    return code, out.getvalue()


def run_json(root: Path) -> tuple[int, dict]:
    code, out = run(root, "--json")
    return code, json.loads(out)


def load_today():
    """Integrate's ``src/gov/plan`` at ``PIN`` as the package ``w2147_today_plan``; its ``command`` module."""
    if f"{TODAY}.command" in sys.modules:
        return sys.modules[f"{TODAY}.command"]
    package = types.ModuleType(TODAY)
    package.__path__ = []
    sys.modules[TODAY] = package
    for name in PLAN_FILES:
        done = subprocess.run(["git", "-C", str(REPO), "show", f"{PIN}:src/gov/plan/{name}.py"],
                              capture_output=True, text=True, timeout=60)
        if done.returncode != 0:
            raise RuntimeError(f"git show {PIN}:src/gov/plan/{name}.py failed: {done.stderr.strip()}")
        source = re.sub(r"\bgov\.plan\b", TODAY, done.stdout)
        module = types.ModuleType(f"{TODAY}.{name}")
        module.__file__ = f"<{PIN}:src/gov/plan/{name}.py>"
        module.__package__ = TODAY
        sys.modules[module.__name__] = module
        exec(compile(source, module.__file__, "exec"), module.__dict__)
        setattr(package, name, module)
    return sys.modules[f"{TODAY}.command"]


def run_today(root: Path, *flags: str) -> tuple[int, str]:
    """Integrate's ``gov plan`` at ``PIN`` on ``root``: what ``gov.cli.main`` prints for it (no envelope of its own,
    ``CHILD_EXIT_CODE``), with the same defaults (``--session ""``)."""
    command = load_today()
    args = argparse.Namespace(root=str(root), json="--json" in flags, tickets=None, open=False, ready=None,
                              session="", role=None, command="plan", passthrough=None)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = command.run(Path(root), args, {})
    return code, out.getvalue()


# -- reading the output ----------------------------------------------------------------------------------------------

def breaks(data: dict) -> list[dict]:
    return [w for w in data["result"]["waits"] if w["code"] == BREAK]


def batch_of(data: dict) -> dict[str, int]:
    return {tid: k for k, batch in enumerate(data["result"]["batches"], 1) for tid in batch}


def mentions(entry: dict, tid: str) -> bool:
    return tid in (entry["ticket"], entry["waits_for"])


# -- the oracle ------------------------------------------------------------------------------------------------------

def _natural(text: str) -> tuple:
    return tuple(int(p) if p.isdigit() else p for p in re.split(r"(\d+)", text) if p)


def fixed_key(t: T) -> tuple:
    return (t.priority, _natural(t.wbs), t.id)


def _graph(tickets) -> tuple[dict, dict]:
    """``(by, edges)``: each ticket by id and by WBS id; ``edges[id]`` the ``(target id, wid)`` it waits on."""
    by = {t.wbs: t for t in tickets}
    by.update({t.id: t for t in tickets})
    edges = {t.id: [(by[w].id, w) for w in wait_ids(t) if w in by and by[w].status != "closed"] for t in tickets}
    return by, edges


def cycles(tickets) -> list[set[str]]:
    """The strongly connected components that are cycles, by mutual reachability (the graphs here are small)."""
    _, edges = _graph(tickets)
    reach = {}
    for t in tickets:
        seen, todo = set(), [t.id]
        while todo:
            for nxt, _ in edges[todo.pop()]:
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        reach[t.id] = seen
    found = []
    for t in tickets:
        comp = {t.id} | {o for o in reach[t.id] if t.id in reach[o]}
        if (len(comp) > 1 or t.id in reach[t.id]) and comp not in found:
            found.append(comp)
    return found


def expected_breaks(tickets) -> list[dict]:
    """Per cycle: its first ticket by the key is chosen, and each of its waits on a ticket of the same cycle is
    broken, named as integrate names a break (``ticket`` the one it had waited on, ``waits_for`` the chosen)."""
    by, edges = _graph(tickets)
    out = []
    for comp in cycles(tickets):
        chosen = min((by[c] for c in comp), key=fixed_key)
        for target, wid in edges[chosen.id]:
            if target in comp:
                out.append({"ticket": target, "waits_for": chosen.id, "code": BREAK, "what": f"WAITS_ON {wid}"})
    return out


def kept_waits(tickets) -> list[dict]:
    """Every planted wait that is not broken, as a ``WAITS_ON`` entry: ``ticket`` waits for ``waits_for``."""
    _, edges = _graph(tickets)
    broken = {(b["waits_for"], b["what"].split(" ", 1)[1]) for b in expected_breaks(tickets)}
    return [{"ticket": tid, "waits_for": target, "code": "WAITS_ON", "what": wid}
            for tid, targets in edges.items() for target, wid in targets if (tid, wid) not in broken]


def outside_every_cycle(tickets) -> set[str]:
    inside = set().union(*cycles(tickets)) if cycles(tickets) else set()
    return {t.id for t in tickets} - inside


def text_line(entry: dict) -> str:
    """A wait as the text output writes it: ``T2 waits for T1 (<CODE> <what>)``."""
    return f"{entry['ticket']} waits for {entry['waits_for']} ({entry['code']} {entry['what']})"
