"""The reader and grader sessions of the W2-81 real run (DEC-1221 (1), EMERGENCY-2 5.3). Not collected as a test.

One question is asked as the product's memory measure asks it (``gov.memaudit.judge``), with one change that is the
rule of this proving ground: **every session runs ``E2E_MODEL``** (``claude-sonnet-5-5``), the reader and the grader
alike.

- The **reader** (``prompts.READER_SYS``, ``prompts.READER_SCHEMA``) is shown the whole ranked ``gov retrieve``
  bundle, may ask for one more search in its own words (``READER_ATTEMPTS`` is 2: the product's A2 cut), and answers
  with citations. A second ``search_again``, or a verdict outside the schema, is not an answer.
- The **grader** (``prompts.GRADER_SYS``, ``prompts.GRADER_SCHEMA``, ``prompts.GRADER_PROMPT``) judges the answer
  against the gold answer.
- A **session** is started by an injectable function ``start(argv, prompt, cwd) -> standard output``. Its argv is
  ``gov.memaudit.claude.argv_of`` with the model forced to ``E2E_MODEL``; the default starter is the product's own
  ``run_claude``. The self-tests pass a stand-in and no model runs.

The answer text is in the row ``ask`` returns (the runner writes it in the run folder alone); the verdicts are ids and
fixed words.
"""

from __future__ import annotations

import json

from gov.memaudit import claude as product_claude
from gov.memaudit import prompts

from w2_81_score import E2E_MODEL

READER_ATTEMPTS = 2        # the first attempt and the one more search: the product's cut 2
READER_BUDGET, GRADER_BUDGET = 1.5, 0.5   # USD a call, as the product's judge sets them
WORKERS = 4

run_claude = product_claude.run_claude    # the default starter: the product's seam


class Caller:
    """The model calls of a run: ``start`` is the injectable starter; the model is always ``E2E_MODEL``."""

    def __init__(self, claude, start, cwd):
        self.claude, self.start, self.cwd = str(claude), start, cwd

    def _once(self, system, schema, prompt, budget):
        argv = product_claude.argv_of(self.claude, E2E_MODEL, system, schema, budget)
        try:
            doc = json.loads(self.start(argv, prompt, self.cwd))
        except (ValueError, TypeError):
            return None
        if not isinstance(doc, dict):
            return None
        out = doc.get("structured_output")
        if out is None:
            try:
                out = json.loads(doc.get("result") or "")
            except (ValueError, TypeError):
                out = None
        return out if isinstance(out, dict) else None

    def call(self, system, schema, prompt, budget):
        """The structured output, or None when two calls in a row returned nothing (as the product's caller)."""
        return self._once(system, schema, prompt, budget) or self._once(system, schema, prompt, budget)


def ask(question, first, search, caller):
    """One question through the reader and the grader. ``first``: the whole ranked bundle as (path, start, end,
    text) items; ``search(words)``: one more ``gov retrieve``, the same kind of items. Returns ``{"reader": ...,
    "grader": ..., "row": ...}``: ``reader`` and ``grader`` as ``w2_81_score.judge_question`` reads them; ``row``
    holds the answers and is for the run folder alone."""
    bundles, attempts, final, verdict = [list(first)], [], None, None
    for k in range(1, READER_ATTEMPTS + 1):
        out = caller.call(prompts.READER_SYS, prompts.READER_SCHEMA, prompts.prompt_of(question.question, bundles),
                          READER_BUDGET)
        attempts.append({"attempt": k, "verdict": (out or {}).get("verdict"), "answer": (out or {}).get("answer"),
                         "citations": (out or {}).get("citations"), "search": (out or {}).get("search")})
        if not out or out.get("verdict") not in ("answer", "search_again", "not_found"):
            verdict = "error"
            break
        final, verdict = out, out["verdict"]
        if verdict != "search_again" or k == READER_ATTEMPTS:
            break
        bundles.append(list(search(out.get("search") or question.question) or []))
    if verdict == "search_again":  # a second search is asked for: the answer is not found
        verdict = "not_found"
    grade, reason = None, None
    if final is not None and verdict in ("answer", "not_found"):
        said = final.get("answer") if verdict == "answer" else "Not found."
        out = caller.call(prompts.GRADER_SYS, prompts.GRADER_SCHEMA,
                          prompts.GRADER_PROMPT.format(question=question.question, gold=question.gold_answer,
                                                       said=said), GRADER_BUDGET)
        grade, reason = (out or {}).get("grade"), (out or {}).get("reason")
    cites = []
    for c in (final or {}).get("citations") or []:
        try:
            cites.append((str(c["path"]), int(c["start_line"]), int(c["end_line"])))
        except (TypeError, ValueError, KeyError):
            continue
    reader = {"verdict": verdict, "citations": cites if verdict == "answer" else [], "attempts": len(attempts)}
    return {"reader": reader, "grader": grade,
            "row": {"id": question.id, "reader": {**reader, "attempts": attempts}, "grade": grade, "reason": reason}}
