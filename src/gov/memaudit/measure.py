"""``measure``: the declaration, the ready check, the control, the attempts and the fault rule, the retrieval figures
(Interface items 1, 2, 3, 5, 8 and 12; S1, S2, S4, F3, F4).

One call, in this order: ``declare`` (W2-170: ``DECLARATION.json``, then ``USED``); the set's digest against the
declaration (``MS-DIGEST``); then per attempt ``n`` (1, then once more): the probe search (the live service answers as
declared), the control ``control-<n>`` (the standing visible 40), and ``attempt-<n>`` through
``gov.retrieval.measure``. An attempt is whole or it is a fault; one restart is allowed while no attempt has counted, after
the ready check again; a second fault, a store whose sha256 changed, a control out of range or a probe not answered as
declared stops the audit (``STOPPED <cause>``, exit 2, to the owner). Every search goes through the run's ``gov`` wrapper,
which writes its ``search`` event before it returns the output, so no search line can precede ``DECLARATION.json`` and
``USED`` (F3). ``measure --kept <n>`` re-scores ``attempt-<n>``'s kept outputs and writes nothing (S2).
"""

from __future__ import annotations

import os
from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import declare, events, fault, layout, ledger, runner, scores, wrapper
from gov.memaudit.common import UsageError, read_json, resolve_commit, set_digest, sha256_file, toplevel, utc_iso

FIRST = "first"  # a baseline that is the first measure's own figure (W2-204 S6)
_UNSET = object()
CAUSES = ("control", "notready", "fault", "store", "brake")


class Stop(Exception):
    """The audit began and cannot go on: ``STOPPED <cause>``, to the owner."""

    def __init__(self, cause: str):
        super().__init__(cause)
        self.cause = cause


def write_text(path: Path, text: str) -> None:
    """A one-line marker, whole or not at all."""
    tmp = path.parent / f".{path.name}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def last_control(p: dict, control=_UNSET) -> tuple[int | None, str | None]:
    """``(last, last_audit)``: ``control.hit5`` of the ``FIGURES.json`` of the latest earlier ``memory-audit-<date>`` run
    folder that has one; none: the baseline of the configuration's ``control`` (Gov OS's is E0's 34, DEC-1097 (1)(b);
    ``None`` for the baseline ``first``). A standing run (``p["week"]``) looks at the set's earlier weeks first, then at
    every fresh audit's. ``control`` absent: that of the repository the process stands in."""
    if control is _UNSET:
        control = _config.current().control
    first = control is not None and control.baseline == FIRST
    baseline = control.baseline if control is not None and not first else None
    runs = p["root"] / "runs"
    audit = "~" if p.get("week") else p["run"].name  # "~" sorts after every audit name: all fresh audits are earlier
    where = []
    if p.get("week") and p["run"].parent.is_dir():
        weeks = sorted((n for n in os.listdir(p["run"].parent) if layout.WEEK_RE.fullmatch(n) and n < p["week"]),
                       reverse=True)
        where += [(f"{p['run'].parent.name}/{n}", p["run"].parent / n) for n in weeks]
    names = sorted((n for n in os.listdir(runs) if layout.AUDIT_RE.fullmatch(n) and n < audit), reverse=True) \
        if runs.is_dir() else []
    where += [(n, runs / n) for n in names]
    for name, folder in where:
        doc = read_json(folder / "FIGURES.json")
        control = doc.get("control") if isinstance(doc, dict) else None
        if isinstance(control, dict) and isinstance(control.get("hit5"), int):
            return control["hit5"], name
    if first:  # the first measure's own figure, from the earliest audit whose ledger holds a control in range
        for name, folder in sorted(where, key=lambda x: x[0]):
            for e in ledger.read(folder):
                if e.get("event") == "control" and e.get("ok") is True and isinstance(e.get("hit5"), int):
                    return e["hit5"], name
    return baseline, None


class _Run:
    """What one ``measure`` call carries between its steps."""

    def __init__(self, p, repo, store, gov, decl, emit, cfg):
        self.cfg = cfg
        self.p, self.run, self.repo, self.store, self.gov = p, p["run"], repo, store, gov
        self.audit, self.decl, self.emit = p["run"].name, decl, emit
        self.wrapper = wrapper.install(self.run, gov)
        self.families = None

    # ---- the ready check: the probe search, then the control

    def ready(self, k: int) -> None:
        ok, why = runner.probe(self.run, self.wrapper, self.repo)
        events.append(self.run, "ready", ok=ok, why=why)
        if not ok:
            self.emit(f"NOT READY: the probe search was not answered as declared ({why})")
            raise Stop("notready")
        self.control(k)

    def control(self, k: int) -> None:
        c = self.cfg.control
        if c is None:  # ``control: none``: the probe search was the whole ready check; no control search is made
            return
        try:
            folder = runner.start(self.run / f"control-{k}")
        except FileExistsError:
            raise Stop("fault") from None
        rc = runner.measure(c.set, c.part, repo=self.repo, root=self.p["root"], folder=folder,
                            wrapper=self.wrapper, run=self.run, phase="control", attempt=k)
        parsed = fault.read_parsed(folder)
        kept = fault.kept_files(folder)
        if rc != 0 or len(kept) != sum(q["calls"] for q in parsed["questions"]) \
                or any(fault.degraded(fault.kept_result(f)) for f in kept):
            self.emit(f"NOT READY: control-{k} did not run as declared (exit {rc})")
            raise Stop("notready")
        of, hit5 = len(parsed["questions"]), sum(1 for q in parsed["questions"] if q["hit5"])
        if of == 0:  # ruling 9: the control's set did not load (missing): the ready check ends, not a control figure
            self.emit(f"NOT READY: control-{k} measured no question (the control's set is missing)")
            raise Stop("notready")
        last, last_audit = last_control(self.p, c)
        if last is None:  # the baseline ``first`` with no earlier figure: this figure is the one recorded, never out of range
            last = hit5
        ok = of == c.size and parsed["families"] is not None and abs(hit5 - last) <= c.spread
        events.append(self.run, "control", k=k, hit5=hit5, of=of, last=last, last_audit=last_audit, ok=ok)
        self.emit(f"CONTROL control-{k}: hit@5 {hit5} of {of}; last {last}; "
                  + ("in range" if ok else "control out of range"))
        if not ok:
            raise Stop("control")
        self.families = parsed["families"]

    # ---- one attempt

    def attempt(self, n: int) -> bool:
        """Run ``attempt-<n>``; True when it is whole and counts. A store changed during it stops the audit."""
        try:
            folder = runner.start(self.run / f"attempt-{n}")
        except FileExistsError:
            raise Stop("fault") from None
        events.append(self.run, "attempt", n=n, state="start", cause=None)
        rc = runner.measure(self.p["set"].name, "hidden", repo=self.repo, root=self.p["root"], folder=folder,
                            wrapper=self.wrapper, run=self.run, phase="attempt", attempt=n)
        write_text(folder / "ENDED", utc_iso())
        try:
            sha = sha256_file(self.store)
        except OSError:
            sha = ""
        same = sha == self.decl["store_sha256"]
        events.append(self.run, "store", n=n, sha256=sha, same=same)
        cause = None if same else "store"
        if cause is None and rc != 0:
            cause = "exit"
        if cause is None:  # a standing run measures the whole set (n_set) and every result is from the declared store
            cause = fault.not_whole(folder, self.decl.get("n_set", self.decl["n"]), self.families,
                                    store_commit=self.decl["store_commit"] if self.decl.get("standing") else None)
        if cause is not None:
            write_text(folder / "FAULT", cause)
            events.append(self.run, "attempt", n=n, state="fault", cause=cause)
            self.emit(f"FAULT attempt-{n}: {cause}; its partial outputs are kept, never counted")
            if cause == "store":
                raise Stop("store")
            return False
        write_text(folder / "DONE", utc_iso())
        events.append(self.run, "attempt", n=n, state="done", cause=None)
        write_text(self.run / "COUNTS", f"attempt-{n}")
        events.append(self.run, "counts", attempt=f"attempt-{n}")  # item 3: the counting attempt's name, as COUNTS
        parsed = fault.read_parsed(folder)
        apart, questions = scores.apart_ids(self.p["hidden"]), parsed["questions"]
        if self.decl.get("standing"):  # the figures beside count the live questions only
            gone = set((read_json(self.p["preflight"]) or {}).get("dropped_ids") or [])
            questions = [x for x in questions if x["id"] not in gone]
        self.emit(scores.retrieval_line(n, scores.retrieval(questions, apart)))
        return True


def _flags(sets_root, audit, repo, store, gov, week=None):
    p = layout.paths(sets_root, audit, week)
    repo = Path(repo) if repo is not None else toplevel()
    store = Path(os.path.expanduser(str(store))) if store is not None else repo / ".gov-runtime/store.db"
    gov = os.path.abspath(os.path.expanduser(str(gov) if gov is not None else "~/.local/bin/gov"))
    return p, repo, store, gov


def run(sets_root, audit, *, commit, repo=None, store=None, gov=None, decision=None, emit, week=None) -> str:
    """The exit word (``ok``, ``refused``, ``used`` or ``stopped``); every line goes to ``emit``. With ``week`` the run
    is a standing set's week: its folder is ``runs/<set>/<week>/`` and its questions are never printed."""
    p, repo, store, gov = _flags(sets_root, audit, repo, store, gov, week)
    if layout.inside(repo, p["root"]):
        raise UsageError("flag inside the sets root")
    cfg = _config.load(repo, resolve_commit(repo, commit))
    word, counts = declare.declare(sets_root, audit, commit=commit, repo=repo, store=store, gov=gov, decision=decision,
                                   week=week)
    for line in declare.lines(word, counts):
        emit(line)
    if word != "ok":
        return word
    decl = read_json(p["declaration"])
    if set_digest(p["hidden"]) != decl["set_digest"]:
        emit("MS-DIGEST")
        return "refused"
    ctx = _Run(p, repo, store, gov, decl, emit, cfg)
    try:
        n = 1
        while True:
            ctx.ready(n)
            if ctx.attempt(n):
                return "ok"
            if n == 2:
                raise Stop("fault")
            n = 2
    except Stop as stop:
        write_text(p["run"] / "STOPPED", stop.cause)
        events.append(p["run"], "stopped", cause=stop.cause)
        emit(f"STOPPED {stop.cause}")
        return "stopped"


def rescore(sets_root, audit, n: int, *, repo=None, emit, week=None) -> str:
    """``measure --kept <n>``: ``attempt-<n>``'s kept outputs through ``gov.retrieval.measure --kept``; the ``RETRIEVAL``
    line; nothing is written. ``ok``, or ``refused`` with ``MS-KEPT``; ``used`` (``USED``, nothing written) for a
    standing set, whose labels and figures are never re-scored (F2)."""
    p = layout.paths(sets_root, audit)
    from gov.memaudit import standing
    if week or standing.is_standing(sets_root, audit, repo, by_name=False):  # before anything else: a standing set's
        emit("USED")  # labels and figures are never re-scored, whatever directory this is run from
        return "used"
    repo = Path(repo) if repo is not None else toplevel()
    if layout.inside(repo, p["root"]):
        raise UsageError("flag inside the sets root")
    kept = p["run"] / f"attempt-{n}" / "kept"
    if (p["run"] / f"attempt-{n}" / "FAULT").exists() or not kept.is_dir():  # a faulted attempt's figures are never printed
        emit("MS-KEPT")
        return "refused"
    rc, text = runner.rescore(p["set"].name, "hidden", repo=repo, root=p["root"], kept=kept)
    parsed = fault.parse(text)
    if rc != 0 or not parsed["questions"]:
        emit("MS-KEPT")
        return "refused"
    emit(scores.retrieval_line(n, scores.retrieval(parsed["questions"], scores.apart_ids(p["hidden"]))))
    return "ok"
