"""``fresh``: a whole fresh pair of halves on a pinned snapshot the command builds (W2-204 I4; S4, S7, S8, S12; F-1 of
P-FRESH-80-1).

``gov memaudit fresh --sets-root R --repo D --commit REV --tag YYYYMMDD[b-z]`` names the two halves from the tag
(``memory-audit-<YYMMDD><2k+1>`` the visible half, ``<2k+2>`` the hidden one, ``k`` from the letter), clones the
repository at the commit into ``<runs-dir>/fresh/<tag>/repo`` (no hard links, detached, clean), builds that clone's own
store with the rebuild command, and takes each half through the design's cycle from what is delivered in the sets root:

    writer-1, preflight-1, checker-1, [writer-2, checker-2], void, preflight-final, measure, judge

The first pre-flight's refusal is recorded and never a stop: it asks for round 2, as a ``revise`` or ``reject`` line of
the round-1 notes does. A step whose delivery is not there ends the call with ``WAITING <audit> <step>`` (exit 5); a
half that cannot go on ends it with ``STOPPED <audit> <step> [<code>]`` (exit 2). Nothing recorded is repeated: the
state of a half is read from the sets root (the delivered files, ``PREFLIGHT.json`` and its ``set_digest``,
``XCHECK-r<n>.md``, ``DROPS.json``, ``USED``, ``COUNTS``, ``FIGURES.json``, the ledger's events). Every step is a child
process (``python3 -m gov.memaudit <step>``) whose output goes to the run folder; this driver opens no question file's
text and prints counts only. The visible half is released into the run folder after its measure. When both halves are
judged the transcript scan closes the measure (``SCAN <audit> clean``, or ``MEASURE VOID <audit>`` and exit 2), then
the two verdict lines. The repository's own tree, index and store are never touched.
"""

from __future__ import annotations

import fcntl
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import driver, drops, figures, layout, ledger
from gov.memaudit.say import say_stderr
from gov.memaudit.common import (UsageError, git_code, read_json, resolve_commit, set_digest, sha256_file, toplevel,
                                 utc_iso, write_whole)

DESCRIPTION = ("Names the two halves from the tag, clones the repository at the commit and builds the clone's own "
               "store, then takes each half through the cycle from what is delivered in the sets root: the first "
               "pre-flight, the notes, round 2 when asked, void, the final pre-flight, measure, judge, the transcript "
               "scan and the verdict. Exit 0 done, 1 refused, 2 stopped, 5 waiting for a delivery. Counts only.")
TAG_RE = re.compile(r"([0-9]{2})([0-9]{6})([b-z]?)")
STEPS = ("writer-1", "preflight-1", "checker-1", "writer-2", "checker-2", "void", "preflight-final", "measure",
         "judge")
GATED = ("measure", "judge")
STORE = ".gov-runtime/store.db"


def add_arguments(sp) -> None:
    sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sp.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    sp.add_argument("--commit", required=True, metavar="REV", help="the commit both halves were written at")
    sp.add_argument("--tag", required=True, metavar="YYYYMMDD[b-z]", help="the day, and a letter for a later pair")
    sp.add_argument("--runs-dir", metavar="DIR", help="where fresh/<tag>/ is made (default: $GOV_INDEP_RUNS_DIR, "
                                                      "else ~/gov-os-runs); outside the sets root")
    sp.add_argument("--rebuild-cmd", metavar="CMD", help="the command that builds the clone's store, split into "
                                                         "words, run in the clone (default: gov rebuild)")
    sp.add_argument("--gov", metavar="EXE", help="passed on to measure and judge")
    sp.add_argument("--claude", metavar="EXE", help="passed on to judge")
    sp.add_argument("--gate-cmd", metavar="CMD", help="the gate's check, split into words; exit 0 is open")
    sp.add_argument("--since", metavar="ISO", help="the scan window's start (default: each half's first brief event)")
    sp.add_argument("--projects", metavar="DIR", help="the transcripts' root (default ~/.claude/projects)")
    sp.add_argument("--allow-session", action="append", default=[], dest="allow", metavar="ID",
                    help="a session allowed to name a half (the writer's, the checker's)")


def names(tag: str) -> tuple[str, str]:
    """``(visible, hidden)``: ``memory-audit-<YYMMDD><2k+1:02d>`` and ``<2k+2:02d>``, ``k`` 0 without a letter, 1 for b."""
    m = TAG_RE.fullmatch(tag) if isinstance(tag, str) else None
    if not m:
        raise UsageError("tag")
    k = ord(m[3]) - ord("a") if m[3] else 0
    return f"memory-audit-{m[2]}{2 * k + 1:02d}", f"memory-audit-{m[2]}{2 * k + 2:02d}"


def _moment(text) -> datetime:
    try:
        at = datetime.fromisoformat(str(text).strip().replace("Z", "+00:00"))
    except ValueError:
        raise UsageError("since") from None
    return at if at.tzinfo else at.replace(tzinfo=timezone.utc)


def _clean_env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


class _Fresh:
    def __init__(self, root, repo, commit, tag, folder, emit, *, gov, claude, gate, rebuild):
        self.root, self.repo, self.commit, self.tag, self.folder, self.emit = root, repo, commit, tag, folder, emit
        self.gov, self.claude, self.gate, self.rebuild = gov, claude, gate, rebuild
        self.clone = folder / "repo"
        self.visible, self.hidden = names(tag)
        self.env = dict(os.environ, GOV_INDEP_RUNS_DIR=str(folder.parent.parent))
        self.st = read_json(folder / "COUNTS.json") or {}

    # ---- the run's own state (counts, names and codes only)

    def begin(self) -> None:
        self.st = {"tag": self.tag, "commit": self.commit, "visible": self.visible, "hidden": self.hidden,
                   "started": self.st.get("started") or utc_iso(), "snapshot": self.st.get("snapshot"),
                   "halves": self.st.get("halves") or {self.visible: {"steps": []}, self.hidden: {"steps": []}},
                   "scan": self.st.get("scan"), "verdict": self.st.get("verdict"), "state": self.st.get("state")}
        self.save()

    def save(self) -> None:
        write_whole(self.folder, "COUNTS.json", self.st)

    def note(self, audit: str, step: str, word: str, code=None) -> None:
        """A step's outcome, recorded and printed once."""
        steps = self.st["halves"][audit]["steps"]
        if any(x["step"] == step for x in steps):
            return
        steps.append({"step": step, "word": word, "exit": code})
        self.save()
        self.emit(f"STEP {audit} {step} {word}")

    # ---- the snapshot

    def snapshot(self) -> bool:
        """The clone at the commit and its own store, built once; False (``FR-SNAPSHOT``) when it cannot be had."""
        snap = self.st.get("snapshot") or {}
        store = self.clone / STORE
        if not (snap.get("built") and store.is_file()):
            if not (self.clone / ".git").exists():
                if os.path.lexists(self.clone):
                    shutil.rmtree(self.clone)
                ok = subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", "--no-checkout", str(self.repo),
                                     str(self.clone)], env=_clean_env(), stdin=subprocess.DEVNULL,
                                    capture_output=True).returncode == 0
                ok = ok and subprocess.run(["git", "-C", str(self.clone), "checkout", "--quiet", "--detach",
                                            self.commit], env=_clean_env(), stdin=subprocess.DEVNULL,
                                           capture_output=True).returncode == 0
                if not ok:
                    shutil.rmtree(self.clone, ignore_errors=True)
                    self.emit("FR-SNAPSHOT")
                    self.cause("fresh", "snapshot", "FR-SNAPSHOT", "the clone at the commit could not be made")
                    return False
            env = dict(self.env)
            if (self.clone / "src" / "gov" / "__init__.py").is_file():  # the repository's own gov builds its store
                env["PYTHONPATH"] = os.pathsep.join(x for x in (str(self.clone / "src"), env.get("PYTHONPATH")) if x)
            code = driver._spawn(self.rebuild, self.clone, env, self.folder / "rebuild.out", self.folder / "rebuild.err")
            if code != 0 or not store.is_file():
                self.emit("FR-SNAPSHOT")
                self.cause("fresh", "snapshot", "FR-SNAPSHOT", "the clone's store could not be built")
                return False
            self.st["snapshot"] = {"commit": self.commit, "built": True, "store_sha256": sha256_file(store)}
            self.save()
        self.emit(f"SNAPSHOT {self.commit[:12]} store built")
        return True

    # ---- one step as a child

    def child(self, audit: str, step: str, sub: str, *flags) -> int:
        argv = [sys.executable, "-m", "gov.memaudit", sub, "--sets-root", str(self.root), "--audit", audit, *flags]
        return driver._spawn(argv, self.clone, self.env, self.folder / f"{audit}.{step}.out",
                             self.folder / f"{audit}.{step}.err")

    def cause(self, audit: str, step: str, code: str, reason: str) -> None:
        """``CAUSE <audit> <step> <CODE>: <reason>``: a code, a count or a fixed phrase, never a question's text (FM-4)."""
        self.emit(f"CAUSE {audit} {step} {code}: {reason}")

    def stop(self, audit: str, step: str, code=None, why: str = "", cause=None) -> tuple[str, str]:
        """One ``CAUSE`` line (``cause`` is ``(CODE, reason)``; a step's child that failed by default), then ``STOPPED``."""
        if cause is None:
            cause = (f"FR-CHILD-{step.upper()}", f"the step's process ended with exit {code if code is not None else 'unknown'}")
        self.cause(audit, step, *cause)
        tail = f" {why}" if why else (f" {code}" if code not in (None, 1) else "")
        self.emit(f"STOPPED {audit} {step}{tail}")
        return "stopped", step

    def wait(self, audit: str, step: str) -> tuple[str, str]:
        self.emit(f"WAITING {audit} {step}")
        return "waiting", step

    # ---- one half, from what the sets root holds

    def prepare(self, audit: str) -> tuple[str, str]:
        """The half's steps up to and with the void count: ``("prepared" | "waiting" | "stopped", step)``."""
        p = layout.paths(self.root, audit)
        at = ["--repo", str(self.clone)]

        def events(name):
            return [e for e in ledger.read(p["ledger"]) if e.get("event") == name]

        # writer-1
        if not (layout.entries(p["hidden"])[0] or os.path.lexists(p["set"] / "r1") or os.path.lexists(p["drops"])):
            return self.wait(audit, "writer-1")
        self.note(audit, "writer-1", "ok")

        # preflight-1: a refusal is recorded, never a stop
        if not events("preflight"):
            code = self.child(audit, "preflight-1", "preflight", *at, "--commit", self.commit,
                              "--runs-dir", str(self.folder.parent.parent))
            if not events("preflight"):
                return self.stop(audit, "preflight-1", code)
        first = events("preflight")[0]
        self.note(audit, "preflight-1", "ok" if first.get("ok") is True else "refused", 0 if first.get("ok") else 1)

        if not os.path.lexists(p["drops"]):
            # checker-1
            notes1 = p["set"] / "XCHECK-r1.md"
            if not notes1.is_file():
                return self.wait(audit, "checker-1")
            self.note(audit, "checker-1", "ok")
            # round 2: asked by the first pre-flight's refusal, or by a revise or reject line of the notes
            rows = drops.read_notes(notes1.read_text(encoding="utf-8", errors="replace")) or {}
            asked = first.get("ok") is not True or any(len(f) > 1 and f[1].strip() in ("revise", "reject")
                                                       for lines in rows.values() for f in lines)
            if asked:
                pre = read_json(p["preflight"]) or {}
                if len(events("preflight")) == 1 and set_digest(p["hidden"]) == pre.get("set_digest"):
                    return self.wait(audit, "writer-2")
                self.note(audit, "writer-2", "ok")
                if not (p["set"] / "XCHECK-r2.md").is_file():
                    return self.wait(audit, "checker-2")
                self.note(audit, "checker-2", "ok")
            else:
                self.note(audit, "writer-2", "skipped")
                self.note(audit, "checker-2", "skipped")
            # void
            code = self.child(audit, "void", "void", *at)
            if not os.path.lexists(p["drops"]):
                return self.stop(audit, "void", code)
        doc = read_json(p["drops"]) or {}
        if doc.get("void") is not None or "void" not in doc:
            self.note(audit, "void", "void", 2)
            cause = doc.get("void") if doc.get("void") in ("VOID-COUNT", "VOID-DOMAIN") else None
            if cause is None:
                return self.stop(audit, "void", 2, cause=("FR-VOID-RECORD", "the void record is not readable"))
            need = self.cfg.min_kept if cause == "VOID-COUNT" else doc.get("domain_min")
            self.emit(f"VOID {audit} {cause} kept {doc.get('kept')} dropped {doc.get('dropped')} need {need}")
            return self.stop(audit, "void", 2, cause=(cause, f"kept {doc.get('kept')} dropped {doc.get('dropped')} "
                                                            f"need {need}"))
        self.note(audit, "void", "ok", 0)
        return "prepared", "void"

    def finish(self, audit: str) -> tuple[str, str]:
        """The steps after the void count: ``("done" | "stopped", step)``."""
        p = layout.paths(self.root, audit)
        run, at = p["run"], ["--repo", str(self.clone)]
        gov = ["--gov", self.gov] if self.gov else []

        # preflight-final, on the kept set: a refusal stops, nothing is spent
        def final():
            seen = ledger.read(p["ledger"])
            at_drop = max((i for i, e in enumerate(seen) if e.get("event") == "drop"), default=-1)
            return next((e for e in seen[at_drop + 1:] if e.get("event") == "preflight"), None) if at_drop >= 0 else None
        if final() is None and not os.path.lexists(p["used"]):
            code = self.child(audit, "preflight-final", "preflight", *at, "--commit", self.commit,
                              "--runs-dir", str(self.folder.parent.parent))
            if final() is None:
                return self.stop(audit, "preflight-final", code)
        last = final()
        if last is not None and last.get("ok") is not True:
            self.note(audit, "preflight-final", "refused", 1)
            codes = (read_json(p["preflight"]) or {}).get("codes")
            refused = [(c, v) for c, v in (codes.items() if isinstance(codes, dict) else ())
                       if isinstance(v, dict) and not v.get("ok", True)]
            for code, v in refused[:-1]:
                self.cause(audit, "preflight-final", code, f"refused {v.get('refused')}")
            last_code, v = refused[-1] if refused else ("PF-UNKNOWN", {})
            return self.stop(audit, "preflight-final",
                             cause=(last_code, f"refused {v.get('refused', 'unknown')}"))
        self.note(audit, "preflight-final", "ok", 0)

        # measure, on the clone's own store
        if not os.path.lexists(run / "COUNTS"):
            if os.path.lexists(p["used"]):  # it began and did not count: to the owner, never run again
                self.note(audit, "measure", "stopped", 2)
                return self.stop(audit, "measure", 2, cause=("FR-MEASURE-USED", "the measure began and did not count: "
                                                                                 "the owner decides"))
            if not driver.gate_open(self.gate, self.clone, self.env):
                return self.stop(audit, "measure", why="gate busy", cause=("FR-GATE-BUSY", "the gate is busy"))
            code = self.child(audit, "measure", "measure", *at, "--commit", self.commit,
                              "--store", str(self.clone / STORE), *gov)
            if code != 0 or not os.path.lexists(run / "COUNTS"):
                if os.path.lexists(p["used"]):
                    self.note(audit, "measure", "stopped", code)
                return self.stop(audit, "measure", code)
        self.note(audit, "measure", "ok", 0)
        if audit == self.visible:
            self.release(p)

        # judge
        if not os.path.lexists(run / "FIGURES.json"):
            if os.path.lexists(run / "reader") or os.path.lexists(run / "STOPPED"):
                self.note(audit, "judge", "stopped", 2)
                return self.stop(audit, "judge", 2, cause=("FR-JUDGE-STOPPED", "the judge began and did not finish: "
                                                                               "the owner decides"))
            if not driver.gate_open(self.gate, self.clone, self.env):
                return self.stop(audit, "judge", why="gate busy", cause=("FR-GATE-BUSY", "the gate is busy"))
            code = self.child(audit, "judge", "judge", *at, *gov, *(["--claude", self.claude] if self.claude else []))
            if code != 0 or not os.path.lexists(run / "FIGURES.json"):
                if os.path.lexists(run / "reader"):
                    self.note(audit, "judge", "stopped", code)
                return self.stop(audit, "judge", code)
        self.note(audit, "judge", "ok", 0)
        return "done", "judge"

    def release(self, p: dict) -> None:
        """The visible half's kept questions, copied byte for byte into the run folder once its measure counted."""
        target = self.folder / "visible"
        if self.st["halves"][self.visible].get("released"):
            return
        os.makedirs(target, mode=0o700, exist_ok=True)
        for f in layout.entries(p["hidden"])[0]:
            shutil.copyfile(f, target / f.name)
        self.st["halves"][self.visible]["released"] = True
        self.save()

    # ---- the close: the transcript scan, then the verdict

    def window(self, audit: str, since) -> datetime:
        if since is not None:
            return since
        p = layout.paths(self.root, audit)
        briefs = [e.get("at") for e in ledger.read(p["ledger"]) if e.get("event") == "brief" and e.get("at")]
        return _moment(min(briefs) if briefs else self.st["started"])

    def close(self, since, projects, allow) -> str:
        from gov.memaudit.scan import scan
        projects = projects or os.path.join(os.path.expanduser("~"), ".claude", "projects")
        counts, word = {}, "ok"
        for audit in (self.visible, self.hidden):
            p = layout.paths(self.root, audit)
            found = scan(str(p["set"]), self.window(audit, since), datetime.now(timezone.utc), None, allow, projects)
            counts[audit] = {"findings": len(found["findings"]), "problems": len(found["problems"]),
                             "transcripts_read": found["transcripts_read"], "allowed": len(found["allowed"])}
            if found["findings"]:
                self.emit(f"MEASURE VOID {audit}")
                word = "stopped"
            elif found["problems"]:  # a transcript that could not be read is never a clean scan
                self.cause(audit, "scan", "SCAN-UNREADABLE", f"{len(found['problems'])} transcripts could not be read")
                self.emit(f"STOPPED {audit} scan 3")
                word = "stopped"
            else:
                self.emit(f"SCAN {audit} clean")
        self.st["scan"] = counts
        if word != "ok":
            self.st["state"] = "void"
            self.save()
            return word
        fig = {a: read_json(layout.paths(self.root, a)["run"] / "FIGURES.json") or {} for a in (self.visible, self.hidden)}
        hid, vis = (fig[a].get("verdict") or {} for a in (self.hidden, self.visible))
        n, right = fig[self.hidden].get("n"), hid.get("right")
        if not (isinstance(n, int) and n > 0 and isinstance(right, int) and isinstance(hid.get("passes"), bool)
                and isinstance(fig[self.visible].get("n"), int) and isinstance(vis.get("right"), int)):
            self.save()
            self.cause(self.hidden, "figures", "FIGURES-INCOMPLETE", "the figures lack a count or a verdict")
            self.emit(f"STOPPED {self.hidden} figures")
            return "stopped"
        self.st["verdict"] = {"hidden": {"right": right, "n": n, "passes": hid["passes"]},
                              "visible": {"right": vis["right"], "n": fig[self.visible]["n"]}}
        self.st["state"] = "done"
        self.save()
        for line in figures.stamp_lines(fig[self.hidden]):  # F15: the stamp, on stderr (the verdict lines keep their form)
            say_stderr(line, self.root)
        self.emit(f"FRESH VERDICT hidden right {right} of {n} ({100 * right / n:.1f} %): "
                  f"{'passes' if hid['passes'] else 'misses'}")
        self.emit(f"FRESH BESIDE visible right {vis['right']} of {fig[self.visible]['n']}")
        return "ok"


def _default_rebuild() -> list[str]:
    return [sys.executable, "-m", "gov.cli.main", "rebuild"]


def run(sets_root, *, emit, **flags) -> str:
    """``_run``, with a usage fault named first: ``CAUSE fresh FR-USAGE-<NAME>: <reason>`` (FM-4), then the fault goes on
    to print ``ERROR: UsageError``."""
    try:
        return _run(sets_root, emit=emit, **flags)
    except UsageError as e:
        name = re.sub(r"[^A-Z0-9]+", "-", str(e).upper()).strip("-") or "FLAG"
        emit(f"CAUSE fresh FR-USAGE-{name}: a flag or its value was refused")
        raise


def _run(sets_root, *, repo=None, commit, tag, runs_dir=None, rebuild_cmd=None, gov=None, claude=None, gate_cmd=None,
         since=None, projects=None, allow=(), emit) -> str:
    """The exit word: ``ok`` (both halves judged, the scan clean, the verdict printed), ``refused`` (the configuration,
    ``FR-NAME``, ``FR-SNAPSHOT``, ``FR-LOCK``), ``stopped`` or ``waiting``."""
    root = layout.root_of(sets_root)
    visible, hidden = names(tag)
    repo = Path(repo) if repo is not None else toplevel()
    runs_dir = runs_dir or os.environ.get("GOV_INDEP_RUNS_DIR") or "~/gov-os-runs"
    runs_dir = Path(os.path.abspath(os.path.expanduser(str(runs_dir))))
    folder = runs_dir / "fresh" / tag
    for flag in (repo, runs_dir, folder):
        if layout.inside(flag, root):
            raise UsageError("flag inside sets root")
    since = _moment(since) if since else None
    commit = resolve_commit(repo, commit)
    cfg = _config.load(repo, commit)  # before anything is made: a repository without its file is refused

    held = any(os.path.lexists(layout.paths(root, a)[k]) for a in (visible, hidden) for k in ("set", "run"))
    recorded = read_json(folder / "COUNTS.json")
    known = isinstance(recorded, dict)
    if (known and recorded.get("commit") != commit) or (not known and held):
        emit("FR-NAME")  # this tag's run is of another commit, or its names are taken with no run folder of its own
        emit("CAUSE fresh start FR-NAME: this tag's run is of another commit, or its names are taken")
        return "refused"
    os.makedirs(folder, mode=0o700, exist_ok=True)
    lock = os.open(folder / "LOCK", os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            emit("FR-LOCK")
            emit("CAUSE fresh start FR-LOCK: another call of this tag is running")
            return "refused"
        job = _Fresh(root, repo, commit, tag, folder, emit, gov=gov, claude=claude, gate=shlex.split(gate_cmd or ""),
                     rebuild=shlex.split(rebuild_cmd) if rebuild_cmd else _default_rebuild())
        job.cfg = cfg
        job.begin()
        emit(f"FRESH plan: visible {visible} hidden {hidden} at {commit[:12]}")
        if not job.snapshot():
            return "refused"
        words = []
        for audit in (visible, hidden):  # both halves' void count first: a void is said before any measure (FM-3)
            words.append(job.prepare(audit)[0])
            if words[-1] == "stopped":  # a stop ends the call: one STOPPED line, the other half is not taken further
                return "stopped"
        if "waiting" in words:
            return "waiting"
        for audit in (visible, hidden):
            if job.finish(audit)[0] == "stopped":
                return "stopped"
        return job.close(since, projects, list(allow or ()))
    finally:
        os.close(lock)


def from_args(args, emit) -> str:
    return run(args.sets_root, repo=args.repo, commit=args.commit, tag=args.tag, runs_dir=args.runs_dir,
               rebuild_cmd=args.rebuild_cmd, gov=args.gov, claude=args.claude, gate_cmd=args.gate_cmd,
               since=args.since, projects=args.projects, allow=args.allow, emit=emit)
