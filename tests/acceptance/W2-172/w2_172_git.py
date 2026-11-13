"""Light planted worlds for ``due`` and ``status`` (S5, S8): a sets root (an empty folder), a repository with committer
dates planted by hand, a runs folder, and (for ``due``) the store link detached at the repository's head. No children, no
fakes: only git and the driver's own subcommands.

``DueRepo`` (the churn the rule measures): 100 non-excluded tracked paths (94 plain ``docs/p000.md`` ... and the six
retrieval paths, one for each of the six globs), 10 paths and the walls' ``tree-exclude.txt`` that the exclusion file
removes (``fixtures/evaluation/**``, ``governance/project/indep-walls/**``). History:

* ``C0``  2026-08-01: every file (more than 28 days before the head: outside its window);
* ``C1``  2026-10-20: ``plain`` plain files changed, ``excluded`` of the excluded ones, ``retr_before`` retrieval paths;
* ``L0``  2026-10-27: the last audit's commit (an empty commit);
* ``H``   2026-11-10: the head, the store link's commit: the retrieval paths ``retr_after`` changed (after the last audit).

So the churn at ``H`` is ``(plain + retr_before + retr_after paths not already counted) / 100``: C1's and H's changes
are both inside H's 28-day window; the excluded paths never count.
"""

from __future__ import annotations

import shutil
from datetime import timedelta
from pathlib import Path

from w2_172_world import Driver, NOW, W171, iso, parse_iso

PLAIN = [f"docs/p{k:03d}.md" for k in range(94)]
RETR = ["src/gov/retrieval/a.py", "src/gov/retrieve/b.py", "src/gov/store/c.py", "src/gov/codeintel/d.py",
        "governance/project/retrieval.yaml", "governance/project/path-map.yaml"]
EXCL = [f"fixtures/evaluation/e{k}.md" for k in range(10)]
EXCLUDE_FILE = "governance/project/indep-walls/tree-exclude.txt"
EXCLUDE_TEXT = "# planted exclusions\nfixtures/evaluation/**\ngovernance/project/indep-walls/**\n"
N = len(PLAIN) + len(RETR)


class Light(Driver):
    """A base folder with the pieces ``Driver`` needs; ``repo`` is filled by a builder."""

    def __init__(self, base: Path, now: str = NOW):
        self.base = Path(base)
        self.home, self.work, self.state = (self.base / n for n in ("home", "work", "state"))
        self.sets, self.repo, self.link = self.base / "sets", self.base / "repo", self.base / "link"
        self.runs = self.base / "launch-log"
        self.mem = self.runs / "indep" / "memaudit"
        self.audits_log = self.runs / "indep" / "AUDITS.log"
        self.spy_dir = self.base / "nospy"
        self.now = now
        self.audit_commit = None
        for p in (self.home, self.work, self.state, self.sets, self.runs / "indep", self.repo):
            p.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q")
        self.git("checkout", "-q", "-b", "main")

    def git(self, *args: str, date: str = "2026-08-01T00:00:00+00:00") -> str:
        return W171.git(self.repo, *args, home=self.home, date=date)

    def commit(self, files: dict[str, str], date: str, message: str = "c") -> str:
        for rel, text in files.items():
            W171._write(self.repo, rel, text)
        self.git("add", "-A", date=date)
        self.git("commit", "-q", "--allow-empty", "-m", message, date=date)
        return self.git("rev-parse", "HEAD", date=date).strip()

    def head(self) -> str:
        return self.git("rev-parse", "HEAD").strip()

    def link_at(self, commit: str) -> None:
        if self.link.exists():
            shutil.rmtree(self.link)
        self.git("worktree", "prune")
        self.git("worktree", "add", "--detach", str(self.link), commit)


def changed(text: str) -> str:
    return text + "changed in the window\n"


def due_repo(base: Path, *, plain: int = 0, excluded: int = 0, retr_before: int = 0, retr_after: tuple = (),
             now: str = NOW) -> Light:
    w = Light(base, now)
    files = {p: f"plain {p}\n" for p in PLAIN}
    files.update({p: f"retrieval {p}\n" for p in RETR})
    files.update({p: f"excluded {p}\n" for p in EXCL})
    files[EXCLUDE_FILE] = EXCLUDE_TEXT
    w.c0 = w.commit(files, "2026-08-01T00:00:00+00:00", "everything")
    step = {p: changed(files[p]) for p in PLAIN[:plain]}
    step.update({p: changed(files[p]) for p in EXCL[:excluded]})
    step.update({p: changed(files[p]) for p in RETR[:retr_before]})
    if excluded:
        step[EXCLUDE_FILE] = EXCLUDE_TEXT + "# edited in the window\n"
    w.c1 = w.commit(step, "2026-10-20T00:00:00+00:00", "the window's changes")
    w.l0 = w.commit({}, "2026-10-27T00:00:00+00:00", "the last audit")
    after = {p: changed(files[p]) + "again\n" for p in retr_after}
    w.h = w.commit(after, "2026-11-10T00:00:00+00:00", "the head")
    w.audit_commit = w.l0
    w.link_at(w.h)
    return w


def plant_history_line(commit: str, *, churn=0.01, retrieval_28d=False, passes=True, pool_regression=False,
                       measured=True, used=True, mode="weekly", audit="memory-audit-20261027") -> dict:
    return {"audit": audit, "commit": commit, "at": "2026-10-27T21:00:00Z", "mode": mode, "churn": churn,
            "retrieval_28d": retrieval_28d, "passes": passes if measured else None,
            "pool_regression": pool_regression, "measured": measured, "used": used}


def plant_state(w: Light, history: list[dict], *, last_start_days: float | None, now: str = NOW) -> None:
    """HISTORY.jsonl with ``history``, STARTS.log whose last line is ``last_start_days`` before ``now`` (none: no
    line), AUDITS.log whose last line is the last audit's commit ``L0`` (the three agree on the last audit)."""
    w.plant_history(*history)
    if last_start_days is None:
        w.plant_starts()
    else:
        at = iso(parse_iso(now) - timedelta(days=last_start_days))
        w.plant_starts(w.start_line(at, commit=w.l0))
    w.plant_audits({"time": "2026-10-27T22:00:00Z", "commit": w.l0, "run": "20261027T220000Z-auditor-r1",
                    "audit": "memory-audit-20261027"})


def stable_history(commit: str) -> list[dict]:
    return [plant_history_line(commit, audit=f"memory-audit-202610{d}") for d in ("06", "13", "20")]


# -- the repository of S8 -----------------------------------------------------------------------------------------------
def status_repo(base: Path) -> Light:
    """``B`` (docs), ``x1`` (retrieval path), ``x2`` (docs), ``x3`` (the path map), ``x4`` (docs): all on ``main``."""
    w = Light(base)
    w.b = w.commit({"docs/a.md": "a\n", "src/gov/retrieval/a.py": "# a\n", "governance/project/path-map.yaml": "v: 1\n"},
                   "2026-10-01T00:00:00+00:00", "B")
    w.x1 = w.commit({"src/gov/retrieval/a.py": "# a changed\n"}, "2026-10-05T00:00:00+00:00", "x1 retrieval")
    w.x2 = w.commit({"docs/a.md": "a2\n"}, "2026-10-10T00:00:00+00:00", "x2 docs")
    w.x3 = w.commit({"governance/project/path-map.yaml": "v: 2\n"}, "2026-10-15T00:00:00+00:00", "x3 path map")
    w.x4 = w.commit({"docs/a.md": "a4\n"}, "2026-10-20T00:00:00+00:00", "x4 docs")
    w.audit_commit = w.x4
    return w


def measured_line(commit: str, *, measured: bool = True) -> dict:
    return plant_history_line(commit, measured=measured)
