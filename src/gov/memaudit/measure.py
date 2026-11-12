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

from gov.memaudit import declare, events, fault, layout, runner, scores, wrapper
from gov.memaudit.common import UsageError, read_json, set_digest, sha256_file, toplevel, utc_iso

CONTROL_SET, CONTROL_PART, CONTROL_N = "memory-retrieval", "visible", 40
CONTROL_FIRST, CONTROL_SPREAD = 34, 2  # E0's figure on the visible 40, and the spread allowed (DEC-1097 (1)(b))
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


def last_control(p: dict) -> tuple[int, str | None]:
    """``(last, last_audit)``: ``control.hit5`` of the ``FIGURES.json`` of the latest earlier ``memory-audit-<date>`` run
    folder that has one; none: E0's 34."""
    runs = p["root"] / "runs"
    audit = p["run"].name
    names = sorted((n for n in os.listdir(runs) if layout.AUDIT_RE.fullmatch(n) and n < audit), reverse=True) \
        if runs.is_dir() else []
    for name in names:
        doc = read_json(runs / name / "FIGURES.json")
        control = doc.get("control") if isinstance(doc, dict) else None
        if isinstance(control, dict) and isinstance(control.get("hit5"), int):
            return control["hit5"], name
    return CONTROL_FIRST, None


class _Run:
    """What one ``measure`` call carries between its steps."""

    def __init__(self, p, repo, store, gov, decl, emit):
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
        try:
            folder = runner.start(self.run / f"control-{k}")
        except FileExistsError:
            raise Stop("fault") from None
        rc = runner.measure(CONTROL_SET, CONTROL_PART, repo=self.repo, root=self.p["root"], folder=folder,
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
        last, last_audit = last_control(self.p)
        ok = of == CONTROL_N and parsed["families"] is not None and abs(hit5 - last) <= CONTROL_SPREAD
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
        if cause is None:
            cause = fault.not_whole(folder, self.decl["n"], self.families)
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
        self.emit(scores.retrieval_line(n, scores.retrieval(parsed["questions"], scores.apart_ids(self.p["hidden"]))))
        return True


def _flags(sets_root, audit, repo, store, gov):
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    store = Path(os.path.expanduser(str(store))) if store is not None else repo / ".gov-runtime/store.db"
    gov = os.path.abspath(os.path.expanduser(str(gov) if gov is not None else "~/.local/bin/gov"))
    return p, repo, store, gov


def run(sets_root, audit, *, commit, repo=None, store=None, gov=None, decision=None, emit) -> str:
    """The exit word (``ok``, ``refused``, ``used`` or ``stopped``); every line goes to ``emit``."""
    p, repo, store, gov = _flags(sets_root, audit, repo, store, gov)
    word, counts = declare.declare(sets_root, audit, commit=commit, repo=repo, store=store, gov=gov, decision=decision)
    for line in declare.lines(word, counts):
        emit(line)
    if word != "ok":
        return word
    decl = read_json(p["declaration"])
    if set_digest(p["hidden"]) != decl["set_digest"]:
        emit("MS-DIGEST")
        return "refused"
    ctx = _Run(p, repo, store, gov, decl, emit)
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


def rescore(sets_root, audit, n: int, *, repo=None, emit) -> str:
    """``measure --kept <n>``: ``attempt-<n>``'s kept outputs through ``gov.retrieval.measure --kept``; the ``RETRIEVAL``
    line; nothing is written. ``ok``, or ``refused`` with ``MS-KEPT``; never ``used``."""
    p = layout.paths(sets_root, audit)
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
