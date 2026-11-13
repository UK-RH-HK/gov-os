"""The model calls of the judged run (Interface items 6, 7 and 11; S3, S8, F1).

One call is the fresh 80's own: ``claude -p --safe-mode --tools "" --no-session-persistence --output-format json --model
<m> --effort high --max-budget-usd <b> --system-prompt <s> --json-schema <j>``, the prompt on standard input, one JSON on
standard output with ``structured_output``, ``usage`` and ``total_cost_usd``. ``run_claude`` is the one Python seam the
tests replace; its standard error goes to ``claude.err`` in ``cwd`` (F1). A call that returned nothing is run once more
and never a third time (FRESH-80-1 section 3.5). Every call's ``total_cost_usd`` is a ``spend`` event of the run's
ledger (S8): ``total`` is the run's sum so far, read back from the ledger at start.
"""

from __future__ import annotations

import json
import subprocess
import threading
import time
from pathlib import Path

from gov.memaudit import events


def run_claude(argv: list[str], prompt: str, cwd) -> str:
    """The seam: the call's standard output. Standard error is appended to ``<cwd>/claude.err``, never printed."""
    cwd = Path(cwd)
    with open(cwd / "claude.err", "ab") as err:
        return subprocess.run(argv, input=prompt, stdout=subprocess.PIPE, stderr=err, text=True, cwd=cwd,
                              check=False).stdout


def argv_of(claude: str, model: str, system: str, schema: dict, budget: float) -> list[str]:
    return [claude, "-p", "--safe-mode", "--tools", "", "--no-session-persistence", "--output-format", "json",
            "--model", model, "--effort", "high", "--max-budget-usd", str(budget), "--system-prompt", system,
            "--json-schema", json.dumps(schema)]


class Caller:
    """The run's model calls: four workers share one ``Caller``; its total and its ledger lines are kept under a lock."""

    def __init__(self, claude: str, run, work):
        self.claude, self.run, self.work = str(claude), Path(run), Path(work)
        self.lock = threading.Lock()
        self.total = events.spent(self.run)

    def _once(self, model, system, schema, prompt, budget, call, qid):
        started = time.monotonic()
        stdout = run_claude(argv_of(self.claude, model, system, schema, budget), prompt, self.work)
        wall = round(time.monotonic() - started, 1)
        try:
            doc = json.loads(stdout)
        except (ValueError, TypeError):
            return {"error": "unparsed output", "wall_s": wall}, None
        if not isinstance(doc, dict):
            return {"error": "unparsed output", "wall_s": wall}, None
        out = doc.get("structured_output")
        if out is None:
            try:
                out = json.loads(doc.get("result") or "")
            except (ValueError, TypeError):
                out = None
        cost = doc.get("total_cost_usd") or 0
        usage = doc.get("usage") if isinstance(doc.get("usage"), dict) else {}
        with self.lock:
            self.total += cost
            events.append(self.run, "spend", call=call, qid=qid, usd=cost, total=round(self.total, 6))
        return {"wall_s": wall, "cost_usd": cost, "is_error": doc.get("is_error"),
                "tokens": {k: usage.get(k) for k in ("input_tokens", "cache_creation_input_tokens",
                                                     "cache_read_input_tokens", "output_tokens")}}, out

    def call(self, model, system, schema, prompt, budget, call: str, qid: str):
        """``(meta, out)``; ``out`` is None only when two calls in a row returned nothing."""
        meta, out = self._once(model, system, schema, prompt, budget, call, qid)
        if out is None:
            again, out = self._once(model, system, schema, prompt, budget, call, qid)
            meta = {**again, "retried": True, "first_error": meta.get("error") or "no structured output",
                    "cost_usd": (meta.get("cost_usd") or 0) + (again.get("cost_usd") or 0)}
        return meta, out
