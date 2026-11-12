"""``FIGURES.json``, ``misses.jsonl`` and the printed verdict (Interface items 8, 9 and 10; S3, S5, S6, F1).

Counts and fixed words only reach ``FIGURES.json`` and the screen. ``misses.jsonl`` holds the questions, gold answers, gold
sources and answers of the misses, and with ``reader/`` it is the only place any of them is written (F1). The verdict is the
reader run's A2 cut of ``outcome`` (the fresh 80's own), against the bar the declaration scaled to ``n``; hit@5, the first
bundle, the citation aside and one search against two are beside it and never judged.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from gov.memaudit import fault, matcher, prompts, scores, tables
from gov.memaudit.common import write_whole

CLASSES = ("gold_wrong", "question_ambiguous", "out_of_scope", "retrieval_miss", "answer_wrong")
OUTCOMES = ("wrong", "incomplete", "not_found")
ROUTES = ("lexical", "semantic", "both", "other", "none")
MISS_KEYS = ("id", "question", "gold_answer", "gold_sources", "answer", "outcome", "evidence_in_bundle")


def route_of(routes) -> str:
    held = set(routes or [])
    if {"lexical", "semantic"} <= held:
        return "both"
    if held == {"lexical"}:
        return "lexical"
    if held == {"semantic"}:
        return "semantic"
    return "other"


def first_route(run_folder, q: dict, line_start: int, calls: int) -> str:
    """The ``routes`` of the first evidence item (the question's calls in order) that matches a gold source, as a word."""
    for call in range(line_start, line_start + calls):
        result = fault.kept_result(Path(run_folder) / "kept" / f"{call:05d}.json")
        for e in (result or {}).get("evidence") or []:
            try:
                item = (e.get("path"), int(e.get("start_line")), int(e.get("end_line")), str(e.get("text", "")))
            except (TypeError, ValueError):
                continue
            if matcher.hit(item, q):
                return route_of(e.get("routes"))
    return "none"


def starts(parsed: dict) -> dict:
    """``{id: (first call number, calls)}`` from a measure's question lines (the calls are numbered in question order)."""
    out, n = {}, 1
    for q in parsed["questions"]:
        out[q["id"]] = (n, q["calls"])
        n += q["calls"]
    return out


def answer_shown(row: dict) -> str:
    """The string the grader was shown: the reader's answer, or ``Not found.``; nothing when the reader returned nothing."""
    if row["final_verdict"] == "answer":
        return str((row["attempts"][-1].get("answer")) or "")
    if row["final_verdict"] == "not_found":
        return "Not found."
    return ""


def miss_outcome(row: dict, o2: dict) -> str:
    grade = (row["grades"].get("grader") or {}).get("grade")
    if o2["nf"] or grade == "not_found":
        return "not_found"
    if o2["correct"] and not o2["right"]:
        return "incomplete"
    return "wrong"


def build(audit: str, decl: dict, questions: list[dict], rows: dict, counting_folder, parsed: dict, control: dict,
          spend: dict) -> tuple[dict, list[dict]]:
    """``(FIGURES, misses)`` for ``questions`` (the kept set, in file-name order) and their ``rows``."""
    by_line = {q["id"]: q for q in parsed["questions"]}
    where = starts(parsed)
    qids = [q["id"] for q in questions]
    o = {cut: {i: prompts.outcome(rows[i], cut) for i in qids} for cut in (1, 2, 3)}
    right, wrong = (sum(o[2][i][k] for i in qids) for k in ("right", "wrong"))
    bar = decl["bar"]
    n = len(qids)
    lo, hi = scores.exact_interval(right, n)
    apart = {q["id"] for q in questions if q["apart"]}
    ret = scores.retrieval([x for x in parsed["questions"] if x["id"] in set(qids)], apart)
    rt = {cut: [bool(o[cut][i]["right"]) for i in qids] for cut in (1, 2)}
    gains, losses, p = prompts.mcnemar(rt[1], rt[2])
    graded = [r for r in rows.values() if r.get("grades")]
    agree = sum(1 for r in graded if (r["grades"].get("grader") or {}).get("grade")
                == (r["grades"].get("check") or {}).get("grade"))
    misses, by_outcome = [], {k: 0 for k in OUTCOMES}
    by_rank, by_ns = {"rank_1_5": 0, "rank_6_20": 0, "not_in_20": 0}, {"embedded": 0, "keyword_only": 0}
    by_cat, by_route = {c: 0 for c in tables.QUOTAS}, {k: 0 for k in ROUTES}
    for q in questions:
        i = q["id"]
        if o[2][i]["right"]:
            continue
        row, line = rows[i], by_line.get(i) or {}
        outcome = miss_outcome(row, o[2][i])
        misses.append({"id": i, "question": q["question"], "gold_answer": q["gold"], "gold_sources": q["raw_sources"],
                       "answer": answer_shown(row), "outcome": outcome, "evidence_in_bundle": bool(line.get("bundle"))})
        by_outcome[outcome] += 1
        rank = line.get("rank")
        by_rank["rank_1_5" if rank and rank <= 5 else "rank_6_20" if rank and rank <= 20 else "not_in_20"] += 1
        by_ns["keyword_only" if q["keyword"] else "embedded"] += 1
        if q["category"] in by_cat:
            by_cat[q["category"]] += 1
        by_route[first_route(counting_folder, q, *where[i]) if i in where else "none"] += 1
    figures = {
        "audit": audit, "n": n, "n_gold": ret["n"],
        "bar": {k: bar[k] for k in ("need_right", "max_wrong", "target_right")},
        "verdict": {"right": right, "wrong": wrong, "passes": right >= bar["need_right"] and wrong <= bar["max_wrong"],
                    "right_ok": right >= bar["need_right"], "wrong_ok": wrong <= bar["max_wrong"],
                    "target_ok": right >= bar["target_right"], "interval_exact": [round(lo, 4), round(hi, 4)],
                    "not_run": sum(1 for i in qids if i not in rows)},
        "beside": {"hit5": ret["hit5"], "hit10": ret["hit10"], "hit20": ret["hit20"], "mrr": ret["mrr"],
                   "in_bundle": ret["in_bundle"], "full_evidence": ret["full"],
                   "correct_citation_aside": sum(o[2][i]["correct"] for i in qids),
                   "not_found": sum(o[2][i]["nf"] for i in qids), "a1_right": sum(rt[1]),
                   "a3_right": sum(o[3][i]["right"] for i in qids),
                   "mcnemar_a1_a2": {"gains": gains, "losses": losses, "p": round(p, 6)},
                   "grader_agree": agree, "graded": len(graded),
                   "search_failures": sum(r.get("search_failures", 0) for r in rows.values())},
        "misses": {"total": len(misses), "by_outcome": by_outcome, "by_rank": by_rank,
                   "by_namespace": by_ns, "by_category": by_cat, "by_route": by_route},
        "control": {k: control.get(k) for k in ("hit5", "of", "last", "last_audit")},
        "pool": None, "classes": None, "spend": spend,
    }
    return figures, misses


def write_misses(run, misses: list[dict]) -> None:
    """``misses.jsonl``: one object a line with exactly the nine keys' order of item 9; whole, by a rename; empty when none."""
    run = Path(run)
    tmp = run / ".misses.jsonl.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for m in misses:
            f.write(json.dumps({k: m[k] for k in MISS_KEYS}, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, run / "misses.jsonl")


def write_figures(run, figures: dict) -> None:
    write_whole(Path(run), "FIGURES.json", figures)


def verdict_lines(f: dict, retried: int) -> list[str]:
    """The five printed lines of item 8."""
    n, v, b, be, sp = f["n"], f["verdict"], f["bar"], f["beside"], f["spend"]
    lo, hi = scores.exact_interval(v["right"], n)  # from the counts, rounded once: FIGURES.json's 4 places are not reused
    mc = be["mcnemar_a1_a2"]
    word = {True: "met", False: "NOT met"}
    return [
        f"VERDICT right end to end {v['right']} of {n} ({scores.pct(v['right'], n)}; exact 95 % interval "
        f"{100 * lo:.1f} to {100 * hi:.1f} %); wrong claims {v['wrong']} of {n} ({scores.pct(v['wrong'], n)})",
        f"BAR at least {b['need_right']} right ({word[v['right_ok']]}) and at most {b['max_wrong']} wrong claims "
        f"({word[v['wrong_ok']]}): {'PASSES' if v['passes'] else 'MISSES'}; target at least {b['target_right']}: "
        f"{'reached' if v['target_ok'] else 'not reached'}",
        f"BESIDE hit@5 {be['hit5']} of {f['n_gold']} ({scores.pct(be['hit5'], f['n_gold'])}); in the first bundle "
        f"{be['in_bundle']}; full evidence {be['full_evidence']}; answer correct, citation aside "
        f"{be['correct_citation_aside']} of {n}; not found {be['not_found']}",
        f"BESIDE one search against two: A1 right {be['a1_right']}, A2 right {v['right']}: {mc['gains']} gains, "
        f"{mc['losses']} losses, exact McNemar p {mc['p']:.4f}",
        f"BESIDE grader agreement {be['grader_agree']} of {be['graded']}; search failures {be['search_failures']}; "
        f"calls run once more {retried}; spent {sp['usd']:.2f} USD (projection {sp['projection']:.2f}, "
        f"brake {sp['brake']:.2f})",
    ]
