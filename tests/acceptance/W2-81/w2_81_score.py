"""The scorer of the W2-81 proving ground: memory judged end to end, per repository (DEC-1221 (1), DEC-1210 (1)).

The rule (EMERGENCY-2 5.3): a reader reads the whole ranked ``gov retrieve`` bundle and searches once more in its own
words, then answers with a citation; a grader judges the answer; the question is right only when BOTH the answer and
its citation are right. A citation is right when a cited place holds a gold source's line and no cited path is a
forbidden one (the stale spec, the superseded plan): an answer that is right with a forbidden citation is wrong.

- **The figure** of a repository is the share of its questions judged right: ``100 * right / asked``, never rounded.
  The bar is ``E2E_BAR`` (95): met at 95 or more. A question with no verdict is wrong, never dropped; a repository
  with no question has no figure, so its bar is not met.
- **What reuses the product:** the rule "right end to end" is ``gov.memaudit.prompts.outcome(row, 2)``, the product's
  own cut (the answer given by the second attempt, the one more search): this module builds the row that function
  reads and calls it. **What is W2-81's own:** the citation check (``gov.memaudit.matcher`` takes the product's
  question form, not this proving ground's ``Question``) and the forbidden-citation rule.
- **hit@5 and the stacked share** (``DIAGNOSTIC``) are computed from the stacked context ``gov retrieve`` returned and
  printed beside the figure, labelled diagnostic: they carry no floor, no target and no pass line (EMERGENCY-2 5.2).
- **Every session** (the adopter, the reader, the grader) runs ``E2E_MODEL``; ``check_models`` refuses a run record
  that does not say so.

The results name questions by id only, with booleans, fixed reason words and a rank: never a question's text or an
answer. A question's row also holds the ranked bundle the retrieval gave (``bundle``: ``[path, start, end]`` in rank
order, ``None`` when it gave none) and ``forbidden_rank`` and ``gold_rank``, the 1-based rank of the first item whose
path is a forbidden source or a gold source (``None`` when none): paths, line numbers and ranks only (T6).
"""

from __future__ import annotations

import math

from gov.memaudit import prompts

E2E_BAR = 95.0                     # the share of questions judged right, per repository (EMERGENCY-2 5.3, DEC-1221 (1))
E2E_MODEL = "claude-sonnet-5-5"    # the model of every session of a run: adopter, reader and grader (DEC-1221 (1))
ROLES = ("adopter", "reader", "grader")
CUT = 2                            # the product's A2 cut: the answer comes by the second attempt (one more search)
DIAGNOSTIC = ("hit_at_5", "stacked_share")
GRADES = ("correct", "wrong", "not_found")  # the product's grader vocabulary (``prompts.GRADER_SCHEMA``)


def _citations(citations):
    """The well-formed (path, start, end) items of what a reader cited; anything else cites nothing."""
    out = []
    for item in citations or []:
        try:
            path, start, end = item
            if isinstance(path, str) and not isinstance(start, bool) and not isinstance(end, bool):
                out.append((path, int(start), int(end)))
        except (TypeError, ValueError):
            continue
    return out


def cited(question, citations):
    """``(holds a gold line, cites a forbidden path)`` for the citations of one answer."""
    items = _citations(citations)
    holds = any(c[0] == s[0] and c[1] <= s[1] <= c[2] for c in items for s in question.sources)
    return holds, any(c[0] in question.forbidden for c in items)


def judge_question(question, reader, grader):
    """One question judged end to end.

    ``reader``: None (no verdict) or ``{"verdict": "answer"|"not_found"|"error", "citations": [(path, start, end)],
    "attempts": n}`` (``attempts`` defaults to 1). ``grader``: None, a grade (``correct``, ``wrong`` or ``not_found``;
    ``incorrect`` and anything else is not correct) or ``{"grade": ...}``. Returns the question id, ``right`` and a
    fixed-word ``reason``: never text from the question or the answer."""
    grade = grader.get("grade") if isinstance(grader, dict) else grader
    reader = reader if isinstance(reader, dict) else {}
    verdict, attempts = reader.get("verdict"), reader.get("attempts", 1)
    holds, forbidden = cited(question, reader.get("citations"))
    result = {"id": question.id, "right": False, "reason": "", "citation_right": holds and not forbidden,
              "forbidden_cited": forbidden, "grade": grade if grade in GRADES else None,
              "reader": verdict if verdict in ("answer", "not_found", "error") else None}
    if verdict not in ("answer", "not_found", "error"):
        result["reason"] = "no verdict"
        return result
    if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 1:
        attempts = 1
    row = {"final_verdict": verdict, "attempts": [None] * attempts,
           "answered_at": attempts if verdict == "answer" else None, "apart": False,
           "citation_right": result["citation_right"], "grades": {"grader": {"grade": grade}}}
    result["right"] = bool(prompts.outcome(row, CUT)["right"])
    result["reason"] = ("right" if result["right"] else "reader error" if verdict == "error"
                        else "reader not found" if verdict == "not_found"
                        else "answered after the one more search" if attempts > CUT
                        else "the grade is not correct" if grade != "correct"
                        else "forbidden citation" if forbidden else "citation misses the gold sources")
    return result


def end_to_end(name, questions, verdicts):
    """A repository's end-to-end figure. ``verdicts`` maps a question id to ``{"reader": ..., "grader": ...}``
    (see ``judge_question``); a question with no entry has no verdict and is wrong."""
    results = []
    for q in questions:
        given = (verdicts or {}).get(q.id) or {}
        results.append({**judge_question(q, given.get("reader"), given.get("grader")), "part": q.part})
    n, right = len(results), sum(r["right"] for r in results)
    figure = 100.0 * right / n if n else None  # one division of an exact product: never rounded into the bar
    return {"repository": name, "questions": n, "right": right, "end_to_end": figure, "bar": E2E_BAR,
            "met": figure is not None and figure >= E2E_BAR, "per_question": results}


def score_question(question, stacked):
    """One question's diagnostics: ``stacked`` is a list of (path, start_line, end_line), or None when unanswered."""
    items = list(stacked or [])

    def hits(item, source):
        return item[0] == source[0] and item[1] <= source[1] <= item[2]

    forbidden = any(item[0] in question.forbidden for item in items[:5])
    rank = next((n for n, item in enumerate(items, 1) if any(hits(item, s) for s in question.sources)), None)
    full = all(any(hits(item, s) for item in items) for s in question.sources)
    gold_paths = {source[0] for source in question.sources}
    return {"id": question.id, "part": question.part, "answered": stacked is not None,
            "hit_at_5": rank is not None and rank <= 5 and not forbidden,
            "full_evidence": full and not forbidden, "forbidden_in_top_5": forbidden, "first_gold_rank": rank,
            # the ranked bundle and the ranks of the first forbidden and the first gold source, by path (T6): paths,
            # line numbers and ranks only, never a text; None where the retrieval gave no bundle
            "bundle": None if stacked is None else [[item[0], item[1], item[2]] for item in items],
            "forbidden_rank": next((n for n, item in enumerate(items, 1) if item[0] in question.forbidden), None),
            "gold_rank": next((n for n, item in enumerate(items, 1) if item[0] in gold_paths), None)}


def score_repository(name, questions, answers, verdicts=None):
    """One repository: the end-to-end figure from ``verdicts`` (None: not measured, so no figure) and, labelled
    ``diagnostic``, hit@5 and the stacked share from ``answers`` (question id -> stacked context)."""
    n = len(questions)
    measured = end_to_end(name, questions, verdicts) if verdicts is not None else {
        "right": None, "end_to_end": None, "met": False, "per_question": [
            {"id": q.id, "part": q.part, "right": False, "reason": "no verdict"} for q in questions]}
    diag = [score_question(q, answers.get(q.id)) for q in questions]
    hit = round(100.0 * sum(d["hit_at_5"] for d in diag) / n, 1) if n else None
    stacked = round(100.0 * sum(d["full_evidence"] for d in diag) / n, 1) if n else None
    ranked = ("bundle", "forbidden_rank", "gold_rank")  # beside the diagnostics, not among them (T6)
    per_question = [{**m, **{k: d[k] for k in ranked},
                     "diagnostic": {k: v for k, v in d.items() if k not in ("id", "part", *ranked)}}
                    for m, d in zip(measured["per_question"], diag)]
    return {"repository": name, "questions": n, "right": measured["right"], "end_to_end": measured["end_to_end"],
            "bar": E2E_BAR, "met": measured["met"], "diagnostic": {"hit_at_5": hit, "stacked_share": stacked},
            "per_question": per_question}


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isnan(value)


def figures(scores):
    """Repository -> its figure, as the judge reads it: ``{"end_to_end": f}``, plus the diagnostics when given. A
    repository with diagnostics alone, or whose figure is not a number, has no entry: it has no figure."""
    out = {}
    for score in scores:
        if not _number(score.get("end_to_end")):
            continue
        out[score["repository"]] = {"end_to_end": score["end_to_end"]}
        diagnostic = score.get("diagnostic") if isinstance(score.get("diagnostic"), dict) else {}
        out[score["repository"]].update({k: diagnostic[k] for k in DIAGNOSTIC if _number(diagnostic.get(k))})
    return out


def check_models(record):
    """The reasons a run record is refused: its ``models`` block must name the adopter, the reader and the grader,
    each ``E2E_MODEL``, and the record must hold the ``release`` version read from the pinned install. No reason: the
    record passes."""
    models = record.get("models") if isinstance(record, dict) else None
    if not isinstance(models, dict):
        return ["the run record has no model line"]
    reasons = []
    for role in ROLES:
        model = models.get(role)
        if model is None:
            reasons.append(f"the model line has no {role}")
        elif model != E2E_MODEL:
            reasons.append(f"the {role} session ran {model if isinstance(model, str) else 'no model id'}, "
                           f"not {E2E_MODEL}")
    release = record.get("release")
    if not isinstance(release, str) or not release.strip():
        reasons.append("the run record has no release version")
    return reasons
