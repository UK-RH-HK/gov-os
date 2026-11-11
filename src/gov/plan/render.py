"""The plan as text lines, as the ``--json`` result, and as the dispatcher's ready list (W2-136 S1, S7).

Text: ``gov plan: N tickets, B batches, W waits (codes...)``; then ``batch k: T1, T3, T5``; then for each wait
``T2 waits for T1 (<CODE> <path or id>)``; then the held tickets, the overrides, the warnings and the findings.

Ready list (DEC-1007 (2)): ``# batch k`` headers, then one line per ticket in the dispatcher's form
``<W2> <id> <brief>.md <W2>-A5-<run>.json``. The orchestrator reviews it and commits it as the ready list.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from gov.plan.derive import FINDING_CODES, Plan

RUN = "run1"  # the run name a proposed ready line carries; the orchestrator renames it when a brief is built


def lines(plan: Plan) -> list[str]:
    codes = ", ".join(plan.codes) or "none"
    out = [f"gov plan: {len(plan.tickets)} tickets, {len(plan.batches)} batches, {len(plan.waits)} waits ({codes})"]
    out += [f"batch {k}: {', '.join(batch)}" for k, batch in enumerate(plan.batches, 1)]
    out += [f"{w.ticket} waits for {w.on} ({w.code} {w.what})" for w in plan.waits]
    if plan.held:
        out.append(f"held: {', '.join(plan.held)} (a wait outside the plan is not met)")
    out += [f"{o.ticket} overrides its wait for {o.on} (OVERRIDE {o.decision} {o.code} {o.what})"
            for o in plan.overrides]
    out += [f"{n.ticket} warning {n.code} ({n.detail})" for n in plan.warnings]
    out += [f"{n.ticket} finding {n.code} ({n.detail})" for n in plan.findings]
    return out


def has_findings(plan: Plan) -> bool:
    return any(note.code in FINDING_CODES for note in plan.findings)


def result(plan: Plan) -> dict:
    text = lines(plan)
    wbs = {t.id: t.wbs for t in plan.tickets}
    return {
        "summary": text[0],
        "counts": {"tickets": len(plan.tickets), "batches": len(plan.batches), "waits": len(plan.waits)},
        "codes": plan.codes,
        "tickets": [{"id": t.id, "wbs_id": t.wbs, "status": t.status, "priority": t.priority} for t in plan.tickets],
        "batches": [list(batch) for batch in plan.batches],
        "batch_wbs": [[wbs[tid] or tid for tid in batch] for batch in plan.batches],
        "waits": [{"ticket": w.ticket, "waits_for": w.on, "code": w.code, "what": w.what} for w in plan.waits],
        "held": list(plan.held),
        "overrides": [{"ticket": o.ticket, "on": o.on, "code": "OVERRIDE", "decision": o.decision,
                       "overrides": o.code, "what": o.what} for o in plan.overrides],
        "warnings": [{"ticket": n.ticket, "code": n.code, "detail": n.detail} for n in plan.warnings],
        "findings": [{"ticket": n.ticket, "code": n.code, "detail": n.detail} for n in plan.findings],
        "lines": text,
    }


def ready_text(plan: Plan) -> str:
    wbs = {t.id: t.wbs for t in plan.tickets}
    out = []
    for k, batch in enumerate(plan.batches, 1):
        out.append(f"# batch {k}")
        for tid in batch:
            name = wbs[tid] or tid
            out.append(f"{name} {tid} {name}-A5-{RUN}.md {name}-A5-{RUN}.json")
    return "\n".join(out) + "\n"


def write_ready(plan: Plan, file: Path) -> None:
    """The ready list written whole to ``file``, through a temporary file beside it (never half a list)."""
    file = Path(file)
    handle, temporary = tempfile.mkstemp(prefix=f".{file.name}.", dir=file.parent or Path("."))
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(ready_text(plan))
        os.replace(temporary, file)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
