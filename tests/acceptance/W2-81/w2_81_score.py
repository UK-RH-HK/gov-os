"""The scorer of the W2-81 proving ground: both figures per repository, never one without the other (DEC-833).

A question's answer is its stacked context: the evidence items ``gov retrieve`` returned, in order, each taken once
within the stack budget (as ``gov.retrieval.measure`` stacks them, DEC-860). An item matches a gold source when its
path is the source's and its lines (``start`` to ``end``) hold the source's line.

- **hit@5:** a gold source is matched by one of the first five items.
- **The stacked share:** every gold source is matched by the stacked context.
- **A forbidden citation** (a planted stale or superseded source) among the first five items is a miss in both.

The result names questions by id only, with booleans and a rank: never a question's text or its answer.
"""

from __future__ import annotations

HIT_AT_5_FLOOR = 85.0        # CAP-10's floor for hit@5
STACKED_SHARE_TARGET = 99.0  # DEC-833: the owner's 99 % goal, the target W2-61 measures (DEC-957 sets memory's
#                              target at 95 % with 85 % the floor; the owner may change this constant, not this suite)
FLOORS = {"hit_at_5": HIT_AT_5_FLOOR, "stacked_share": STACKED_SHARE_TARGET}


def score_question(question, stacked):
    """One question's result: ``stacked`` is a list of (path, start_line, end_line), or None when unanswered."""
    items = list(stacked or [])

    def hits(item, source):
        return item[0] == source[0] and item[1] <= source[1] <= item[2]

    forbidden = any(item[0] in question.forbidden for item in items[:5])
    rank = next((n for n, item in enumerate(items, 1) if any(hits(item, s) for s in question.sources)), None)
    full = all(any(hits(item, s) for item in items) for s in question.sources)
    return {"id": question.id, "part": question.part, "answered": stacked is not None,
            "hit_at_5": rank is not None and rank <= 5 and not forbidden,
            "full_evidence": full and not forbidden, "forbidden_in_top_5": forbidden, "first_gold_rank": rank}


def score_repository(name, questions, answers):
    """Both figures for one repository: ``answers`` maps a question id to its stacked context."""
    results = [score_question(q, answers.get(q.id)) for q in questions]
    n = len(results)
    if not n:  # no question: no figure, so neither is met
        return {"repository": name, "questions": 0, "hit_at_5": None, "stacked_share": None, "per_question": []}
    return {"repository": name, "questions": n,
            "hit_at_5": round(100.0 * sum(r["hit_at_5"] for r in results) / n, 1),
            "stacked_share": round(100.0 * sum(r["full_evidence"] for r in results) / n, 1),
            "per_question": results}


def figures(scores):
    """Repository -> both figures, as the judge reads them; a repository without both has neither."""
    out = {}
    for score in scores:
        if isinstance(score.get("hit_at_5"), (int, float)) and isinstance(score.get("stacked_share"), (int, float)):
            out[score["repository"]] = {"hit_at_5": score["hit_at_5"], "stacked_share": score["stacked_share"]}
    return out
