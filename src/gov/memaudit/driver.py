"""``python3 -m gov.memaudit run``: one audit through the launch script and W2-170's and W2-171's subcommands (W2-172
Interface items 2 to 5, 7 and 8; S1-S4, F1-F3).

Every step is a child process with cwd ``--repo``. The driver opens no path under the sets root: every figure it uses is
a child's last line of standard output. Its own folder is ``<runs>/indep/memaudit/``; it holds counts, codes, ids and
repository paths only.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path

from gov.memaudit import digest, schedule
from gov.memaudit.common import GitError, blob_at, git_code, sha256_bytes, write_whole

BRIEFS = "governance/project/indep-briefs/memory-audit"
LAUNCH = "governance/project/orchestration/tools/indep_launch.py"
ORDER = ("writer-1", "preflight", "checker-1", "writer-2", "checker-2", "void", "measure", "judge", "auditor",
         "classes", "pool", "figures")
GATED = ("measure", "judge", "pool")  # the steps that search the store (item 8)
CANARY = 16
SPENT = re.compile(r"spent ([0-9]+(?:\.[0-9]+)?) USD")


def _spawn(argv, repo, env, out: Path, err: Path) -> int:
    try:
        with open(out, "wb") as o, open(err, "wb") as e:
            return subprocess.run(argv, cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=o, stderr=e).returncode
    except OSError:
        return 127


def _last_json(path: Path) -> dict:
    """The last non-blank line of a step's standard output as an object, else ``{}``."""
    try:
        rows = [x for x in path.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
        obj = json.loads(rows[-1]) if rows else None
    except (OSError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def _write_text(path: Path, text: str) -> None:
    tmp = path.with_name("." + path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _held(path: str) -> bool:
    """Whether another process holds ``path``'s exclusive lock (a non-blocking try, released at once)."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return False
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    except OSError:
        return False
    finally:
        os.close(fd)
    return False


def _used(step: str, code: int, gate: bool) -> bool:
    """Whether a stop at ``step`` is after USED (item 5): known from the step and its exit code alone."""
    if step == "measure":
        return False if gate else code not in (1, 4)  # DC- refusals (1, 4) come before declare writes USED
    return ORDER.index(step) > ORDER.index("measure")


class _Cycle:
    def __init__(self, st, a_dir, repo, env, emit, root, gate, launch_argv, link):
        self.st, self.a_dir, self.repo, self.env, self.emit, self.root = st, a_dir, repo, env, emit, root
        self.gate, self.launch_argv, self.link = gate, launch_argv, link
        self.stopped = False

    def save(self):
        write_whole(self.a_dir, "COUNTS.json", {k: self.st.get(k) for k in (
            "audit", "commit", "force", "mode", "reason", "steps", "stop", "refused", "cost")})

    def gate_open(self) -> bool:
        if not self.gate:
            return True
        poll = float(os.environ.get("GOV_MEMAUDIT_GATE_POLL_S") or 60)
        most = float(os.environ.get("GOV_MEMAUDIT_GATE_MAX_S") or 3600)
        seam, waited, began = bool(os.environ.get("GOV_MEMAUDIT_NOW")), 0.0, time.monotonic()
        while True:
            try:
                code = subprocess.run(self.gate, cwd=self.repo, env=self.env, stdin=subprocess.DEVNULL,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            except OSError:
                code = 1
            if code == 0:
                return True
            if waited >= most or time.monotonic() - began >= most:
                return False
            nap = max(0.0, min(poll, most - waited))
            if not seam:  # under the clock seam the wait is counted, not slept: time does not pass there
                time.sleep(nap)
            waited += nap if nap else most  # a zero poll still ends: never an unbounded wait

    def stop(self, step: str, code: int, gate: bool = False):
        used = _used(step, code, gate)
        self.st["stop"] = {"step": step, "exit": code, "used": used}
        if gate:
            self.st["stop"]["reason"] = "gate busy"
        self.emit(f"STOPPED {step} gate busy" if gate else f"STOPPED {step} {code}")
        self.stopped = True
        return False

    def go(self, step: str, argv, *, launch=False) -> bool:
        """Run ``step``: ``True`` to go on, ``False`` after a stop."""
        if step in GATED and not self.gate_open():
            return self.stop(step, 2, gate=True)
        self.emit(f"STEP {step} {shlex.join(argv)}")
        out, err = self.a_dir / f"{step}.out", self.a_dir / f"{step}.err"
        code = _spawn(argv, self.repo, self.env, out, err)
        retried = False
        if launch and code == CANARY:  # only the canary is retried, once, with the same command line
            retried, code = True, _spawn(argv, self.repo, self.env, out, err)
        self.st["steps"].append({"step": step, "exit": code, "retried": retried})
        if launch:
            counts = _last_json(out)
            write_whole(self.a_dir, f"{step}.counts.json", counts)
            self.counts = counts
            cost = (counts.get("session") or {}).get("cost_usd")
            self.st["cost"][step] = float(cost) if isinstance(cost, (int, float)) else 0.0
        if step == "judge":
            spent = SPENT.findall(out.read_text(encoding="utf-8", errors="replace")) if out.exists() else []
            self.st["cost"][step] = float(spent[-1]) if spent else 0.0
        self.save()
        return True if code == 0 else self.stop(step, code)

    def brief(self, kind: str):
        """``(path, sha256)`` of the brief at the audit commit (``git show``), or ``None`` when it holds none."""
        path = f"{BRIEFS}/{kind}.md"
        data = blob_at(self.repo, self.st["commit"], path)
        return None if data is None else (path, sha256_bytes(data))

    def launch(self, step: str, kind: str, *tail) -> bool:
        brief = self.brief(kind)
        if brief is None:  # the launch script's own code for "brief"
            self.st["steps"].append({"step": step, "exit": 10, "retried": False})
            self.save()
            return self.stop(step, 10)
        a, c = self.st["audit"], self.st["commit"]
        argv = [*self.launch_argv, "--sets-root", self.root, "--kind", kind, "--brief", brief[0],
                "--brief-sha256", brief[1], "--commit", c, "--set", a, *tail]
        return self.go(step, argv, launch=True)

    def child(self, step: str, sub: str, *flags) -> bool:
        return self.go(step, [sys.executable, "-m", "gov.memaudit", sub, "--sets-root", self.root,
                              "--audit", self.st["audit"], *flags])

    def run(self, repo_flag, gov, claude) -> bool:
        a = self.st["audit"]
        gov_flag = ["--gov", gov] if gov else []
        c = self.st["commit"]
        if not self.launch("writer-1", "writer", "--round", "1"):
            return False
        if not self.child("preflight", "preflight", "--repo", repo_flag, "--commit", c):
            return False
        if not self.launch("checker-1", "checker", "--round", "1"):
            return False
        counts = self.counts.get("out") or {}
        if (counts.get("revise") or 0) + (counts.get("rejected") or 0) > 0:
            if not self.launch("writer-2", "writer", "--round", "2"):
                return False
            if not self.launch("checker-2", "checker", "--round", "2"):
                return False
        if not self.child("void", "void"):
            return False
        store = f"{self.link}/.gov-runtime/store.db"
        if not self.child("measure", "measure", "--repo", repo_flag, "--commit", c, "--store", store, *gov_flag):
            return False
        if not self.child("judge", "judge", "--repo", repo_flag, *gov_flag, *(["--claude", claude] if claude else [])):
            return False
        if not self.launch("auditor", "auditor", "--audit", a):
            return False
        if not self.child("classes", "classes"):
            return False
        if not self.child("pool", "pool", "--repo", repo_flag, *gov_flag):
            return False
        return self.child("figures", "figures")


def _refusal(st, runs, folder, link_lock, locked, force, at, head, repo) -> str | None:
    """The first check of item 3 that fails: its code, else ``None``."""
    if locked:
        return "RN-LOCK"
    try:
        base = [x for x in (runs / "indep" / "AUDITS.log").read_text(encoding="utf-8").splitlines() if x.strip()]
    except OSError:
        base = []
    if not base:
        return "RN-NOBASE"
    starts = schedule.read_lines(folder / "STARTS.log")
    if starts and not force:
        try:
            recent = at - schedule.parse_time(starts[-1].get("at")) < timedelta(days=schedule.RECENT_DAYS)
        except Exception:  # an unreadable stamp counts as recent: never a start by mistake
            recent = True
        if recent:
            return "RN-RECENT"
    if _held(link_lock):
        return "RN-REBUILD"
    line = schedule.mainline(repo)
    if git_code(repo, "merge-base", "--is-ancestor", head, line) != 0:
        return "RN-SIDE"
    if at.timestamp() - schedule.committer_time(repo, head) > 24 * 3600:
        return "RN-STALE"
    if any(x.get("audit") == st["audit"] for x in starts):
        return "RN-NAME"
    return None


def run(sets_root, *, repo, link, launch, gov, claude, gate_cmd, force, emit) -> str:
    repo, runs, at = schedule.repo_of(repo), schedule.runs_dir(), schedule.now()
    folder = schedule.folder(runs)
    link = schedule.store_link(repo, link)
    head = schedule.head_of(link)
    audit = "memory-audit-" + at.strftime("%Y%m%d")
    before = schedule.decide(repo, runs, head, at)
    st = {"audit": audit, "commit": head, "force": bool(force), "mode": before["mode"], "reason": before["reason"],
          "steps": [], "stop": None, "refused": None, "cost": {}, "figures": None, "retrieval": []}
    os.makedirs(folder, exist_ok=True)
    a_dir = folder / audit
    lock = os.open(folder / "LOCK", os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = False
        except BlockingIOError:
            locked = True
        code = _refusal(st, runs, folder, link + ".lock", locked, force, at, head, repo)
        last = schedule.last_audit_commit(runs)
        st["retrieval"] = schedule.retrieval_changed(repo, last, head)
        if code:
            return _refuse(st, a_dir, code, before, emit)
        a_dir.mkdir(parents=True, exist_ok=True)
        with open(folder / "STARTS.log", "a", encoding="utf-8") as f:
            f.write(json.dumps({"audit": audit, "commit": head, "at": schedule.stamp(at), "force": bool(force)}) + "\n")
        env = dict(os.environ, GOV_INDEP_RUNS_DIR=str(runs))
        launch_argv = [sys.executable, launch or str(repo / LAUNCH)]
        cycle = _Cycle(st, a_dir, repo, env, emit, sets_root, shlex.split(gate_cmd or ""), launch_argv, link)
        cycle.counts = {}
        cycle.save()
        churn, retrieval_28d = schedule.churn_at(repo, head)
        done = cycle.run(str(repo), gov, claude)
        if done:
            fig = _last_json(a_dir / "figures.out")
            st["figures"] = fig
            _history(folder, st, at, churn, retrieval_28d, measured=True, fig=fig)
        elif st["stop"]["used"]:
            _history(folder, st, at, churn, retrieval_28d, measured=False, fig={})
        cycle.save()
        _finish(st, a_dir, repo, runs, head, at, before, emit, write=True)
        return "ok" if done else "stopped"
    finally:
        os.close(lock)


def _history(folder, st, at, churn, retrieval_28d, *, measured: bool, fig: dict) -> None:
    pool = fig.get("pool") if isinstance(fig.get("pool"), dict) else {}
    verdict = fig.get("verdict") if isinstance(fig.get("verdict"), dict) else {}
    line = {"audit": st["audit"], "commit": st["commit"], "at": schedule.stamp(at), "mode": st["mode"],
            "churn": churn, "retrieval_28d": retrieval_28d,
            "passes": verdict.get("passes") if measured and isinstance(verdict.get("passes"), bool) else None,
            "pool_regression": bool(pool.get("regression")), "measured": measured, "used": True}
    with open(folder / "HISTORY.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def _finish(st, a_dir, repo, runs, head, at, before, emit, *, write: bool) -> None:
    try:
        after = schedule.decide(repo, runs, head, at)
    except (GitError, ValueError, OSError):
        after = before
    st["next"], st["next_mode"] = after["next"], after["mode"]
    block = digest.lines(st)
    if write:
        _write_text(a_dir / "DIGEST.txt", "\n".join(block) + "\n")
    for line in block:
        emit(line)


def _refuse(st, a_dir, code, before, emit) -> str:
    """A refusal is not a started audit: it starts no child, prints the digest (whose line 11 is ``REFUSED <code>``) and,
    where the audit's folder is not there yet, writes ``COUNTS.json`` and the digest; where it is, nothing."""
    st["refused"] = code
    fresh = not a_dir.exists()
    if fresh:
        a_dir.mkdir(parents=True)
        write_whole(a_dir, "COUNTS.json", {k: st.get(k) for k in (
            "audit", "commit", "force", "mode", "reason", "steps", "stop", "refused", "cost")})
    st["next"], st["next_mode"] = before["next"], before["mode"]
    block = digest.lines(st)
    if fresh:
        _write_text(a_dir / "DIGEST.txt", "\n".join(block) + "\n")
    for line in block:
        emit(line)
    return "refused"
