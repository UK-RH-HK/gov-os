"""The planted scenarios (ranks, verdicts, costs) and the oracle that says what the tool must print and write.

A scenario names, for each of the 40 questions of the set, the first gold rank the fake ``gov`` plants and what the
fake reader and graders say. The oracle is written from the Interface and the ticket's KPI lines, independently of the
tool: ``outcome`` is the fresh 80's cut as FRESH-80's ``e2_run.py`` states it (the pinned ``outcome``), re-implemented
here from its stated meaning, the interval is Clopper-Pearson by bisection on the binomial tails, the McNemar test is
exact.
"""

from __future__ import annotations

import math

import w2_171_world as W

CYCLE = [1, 2, 3, 4, 5, 1, 8, 1, 12, 2, 17, 1, None]
APART = W.NONEXISTENT
# behaviour -> (final verdict, attempts, answered at, the grader's grade, the citation matches a gold place)
BEHAVIOURS = {
    "A1": ("answer", 1, 1, "correct", True),
    "A2": ("answer", 2, 2, "correct", True),
    "A3": ("answer", 3, 3, "correct", True),
    "A1_wrong": ("answer", 1, 1, "wrong", True),
    "A1_cite": ("answer", 1, 1, "correct", False),
    "A1_gradenf": ("answer", 1, 1, "not_found", True),
    "NF": ("not_found", 1, None, "not_found", False),
    "CAP": ("not_found", 3, None, "not_found", False),
    "EMPTY2": ("error", 1, None, None, False),
}
CITE_OTHER = {"path": "docs/plan/p90.md", "start_line": 3, "end_line": 6}


def calls_for(rank, routes=("lexical", "semantic")):
    """The fake gov's calls that put the one gold item at stacked rank ``rank`` (None: nowhere)."""
    gold = {"k": "g0", "routes": list(routes)}
    if rank is None:
        return [["d"] * 6]
    if rank <= 10:
        return [["d"] * (rank - 1) + [gold] + ["d"] * (10 - rank)]
    if rank <= 20:
        return [["d"] * 10, ["d"] * (rank - 11) + [gold]]
    return [["d"] * 10, ["d"] * 10, ["d"] * (rank - 21) + [gold]]


def outcome(r: dict, cut: int) -> dict:
    """Under condition A<cut>: right end to end, correct, wrong claim, not found (the pinned ``outcome``)."""
    grade = r["grade"]
    answered = r["answered_at"] is not None and r["answered_at"] <= cut
    if r["apart"]:
        nf = not answered
        right = nf or (answered and grade == "correct")
        return {"right": right, "correct": right, "wrong": answered and grade != "correct", "nf": nf}
    if answered:
        return {"right": grade == "correct" and r["citation_right"], "correct": grade == "correct",
                "wrong": grade != "correct", "nf": False}
    return {"right": False, "correct": False, "wrong": False, "nf": True}


def _tail_ge(x, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x, n + 1))


def _tail_le(x, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(0, x + 1))


def exact_interval(x: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Clopper-Pearson, by bisection on the binomial tails."""
    a = (1 - level) / 2

    def solve(f, rising):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if (f(mid) < a) == rising:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if x == 0 else solve(lambda p: _tail_ge(x, n, p), True)
    upper = 1.0 if x == n else solve(lambda p: _tail_le(x, n, p), False)
    return lower, upper


def mcnemar(a, b):
    g = sum(1 for x, y in zip(a, b) if y and not x)
    l = sum(1 for x, y in zip(a, b) if x and not y)
    n, k = g + l, min(g, l)
    return g, l, (min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0)


def pct(x, n) -> str:
    return f"{100 * x / n:.1f} %"


def search_words(qid: str) -> str:
    return f"search words for {qid}"


class Scenario:
    def __init__(self, name, behaviour=None, ranks=None, routes=None, disagree=(), retried=(), later_fail=(),
                 words=False, control_hits=34, cost=None, sleep=0, garbage="", dropped=()):
        self.name = name
        self.dropped = set(dropped)
        self.behaviour = {f"q{i:02d}": "A1" for i in range(1, 40)}
        self.behaviour[APART] = "NF"
        self.behaviour.update(behaviour or {})
        self.ranks = {f"q{i:02d}": CYCLE[(i - 1) % 13] for i in range(1, 40)}
        self.ranks[APART] = None
        self.ranks.update(ranks or {})
        self.routes = dict(routes or {})
        self.disagree, self.retried, self.later_fail = set(disagree), set(retried), set(later_fail)
        self.words, self.control_hits, self.sleep, self.garbage = words, control_hits, sleep, garbage
        self.cost = cost or {"reader": 0.10, "grader": 0.02, "check": 0.01}

    # -- the planted rows
    def row(self, qid: str) -> dict:
        verdict, attempts, answered_at, grade, cite = BEHAVIOURS[self.behaviour[qid]]
        check = None if grade is None else (grade if qid not in self.disagree
                                            else ("wrong" if grade == "correct" else "correct"))
        return {"id": qid, "final_verdict": verdict, "attempts": attempts, "answered_at": answered_at,
                "grade": grade, "check": check, "citation_right": cite, "apart": qid == APART}

    def answer_text(self, qid: str) -> str:
        return f"The {W.AWORD} answer for {qid}." if self.words and qid == W.SPECIAL else f"Answer for {qid}."

    def outcomes(self, cut: int) -> dict:
        return {q: outcome(self.row(q), cut) for q in sorted(self.behaviour) if q not in self.dropped}

    def in_bundle(self, qid):
        r = self.ranks[qid]
        return r is not None and r <= 10

    # -- the plan of the fake gov and the fake claude
    def install(self, world, *, gov_edit=None, claude_edit=None) -> None:
        docs = world.docs()
        gov, claude = {}, {}
        gov[W.PROBE] = {"calls": [["d"] * 10]}
        for k in range(1, W.CONTROL_N + 1):
            gov[W.control_text(k)] = {"gold": [[f"docs/ctl/c{k:02d}.md", 1, 3]],
                                      "calls": calls_for(1 if k <= self.control_hits else None)}
        for qid, doc in docs.items():
            src = doc["sources"][0]
            gold = [src["path"], *(src.get("lines") or [1, 3])]
            if qid == APART:
                gov[doc["question"]] = {"fault": "unresolved"}
            else:
                gov[doc["question"]] = {"gold": [gold], "calls": calls_for(self.ranks[qid], self.routes.get(
                    qid, ("lexical", "semantic")))}
            claude[doc["question"]] = self._claude_spec(qid, doc, gold)
            for words in (search_words(qid),):
                gov[words] = {"gold": [gold], "calls": calls_for(1)}
                if qid in self.later_fail:
                    gov[words]["fault"] = "rerank"
        world.write_plans(gov, claude, cost=self.cost, sleep=self.sleep, garbage=self.garbage)
        if gov_edit or claude_edit:
            import json
            plan = json.loads((world.state / "gov_plan.json").read_text())
            cplan = json.loads((world.state / "claude_plan.json").read_text())
            if gov_edit:
                gov_edit(plan["questions"], docs)
            if claude_edit:
                claude_edit(cplan["q"], docs)
            (world.state / "gov_plan.json").write_text(json.dumps(plan))
            (world.state / "claude_plan.json").write_text(json.dumps(cplan))

    def _claude_spec(self, qid, doc, gold) -> dict:
        cite = [{"path": gold[0], "start_line": gold[1], "end_line": min(gold[2], gold[1] + 3)}]
        beh = self.behaviour[qid]
        sa = {"verdict": "search_again", "answer": "", "citations": [], "search": search_words(qid)}
        ans = {"verdict": "answer", "answer": self.answer_text(qid), "citations": [CITE_OTHER] if beh == "A1_cite" else cite,
               "search": ""}
        nf = {"verdict": "not_found", "answer": "", "citations": [], "search": ""}
        reader = {"A1": [ans], "A2": [sa, ans], "A3": [sa, sa, ans], "A1_wrong": [ans], "A1_cite": [ans],
                  "A1_gradenf": [ans], "NF": [nf], "CAP": [sa, sa, sa], "EMPTY2": ["empty", "empty"]}[beh]
        if qid in self.retried:
            reader = ["empty", *reader]
        r = self.row(qid)
        spec = {"id": qid, "reader": reader, "cost": self.cost}
        if r["grade"] is not None:
            spec["grader"], spec["check"] = [r["grade"]], [r["check"]]
        return spec


SCENARIOS = {
    # five misses, the bar met (35 right, 2 wrong claims), three gains from searching again, one later search that
    # fails, one question run once more, three disagreements of the graders
    "five": Scenario(
        "five",
        behaviour={"q02": "A2", "q04": "A2", "q31": "A2", "q03": "A1_wrong", "q19": "A1_cite", "q25": "NF",
                   "q28": "A1_gradenf", "q33": "CAP"},
        ranks={"q03": 3, "q19": 8, "q25": None, "q28": 14, "q33": 25},
        routes={"q19": ["lexical"], "q28": ["semantic"], "q33": ["graph"]},
        disagree={"q05", "q06", "q07"}, retried={"q08"}, later_fail={"q02"}),
    # no miss at all
    "clean": Scenario("clean", behaviour={"q10": "A2", "q20": "A2"}, disagree={"q30"}),
    # seven misses: 33 right, below the bar's 34 (a MISS is a result)
    "below": Scenario(
        "below",
        behaviour={"q02": "A2", "q04": "A2", "q31": "A2", "q03": "A1_wrong", "q19": "A1_cite", "q25": "NF",
                   "q28": "A1_gradenf", "q33": "CAP", "q10": "A3", "q15": "EMPTY2"},
        ranks={"q03": 3, "q19": 8, "q25": None, "q28": 14, "q33": 25},
        routes={"q19": ["lexical"], "q28": ["semantic"], "q33": ["graph"]},
        disagree={"q05"}, later_fail={"q02"}),
    # a set of 37 (the checker rejected q27, q33 and q34): the scaled bar is 32 right, 1 wrong claim, target 36
    "five37": Scenario(
        "five37",
        behaviour={"q02": "A2", "q04": "A2", "q31": "A2", "q03": "A1_wrong", "q19": "A1_cite", "q25": "NF",
                   "q30": "CAP"},
        ranks={"q03": 3, "q19": 8, "q25": None, "q28": 14, "q30": 25},
        routes={"q19": ["lexical"], "q28": ["semantic"], "q30": ["graph"]},
        disagree={"q05"}, retried={"q08"}, later_fail={"q02"}, dropped=("q27", "q33", "q34")),
    # the five misses and the question that holds the planted words missed too, its answer holding one
    "words": Scenario(
        "words",
        behaviour={"q02": "A2", "q04": "A2", "q31": "A2", "q03": "A1_wrong", "q19": "A1_cite", "q25": "NF",
                   "q28": "A1_gradenf", "q33": "CAP", "q07": "A1_wrong"},
        ranks={"q03": 3, "q19": 8, "q25": None, "q28": 14, "q33": 25},
        routes={"q19": ["lexical"], "q28": ["semantic"], "q33": ["graph"]},
        disagree={"q05"}, retried={"q08"}, later_fail={"q02"}, words=True),
}


def default_decl_n():
    return 40


class Expected:
    """What the tool must print and write for ``scenario`` on the world's set (n = 40, one question apart)."""

    def __init__(self, sc: Scenario, world=None):
        self.sc = sc
        self.world = world
        self.n = 40 - len(sc.dropped)
        self.main = [q for q in sorted(sc.behaviour) if q != APART and q not in sc.dropped]
        self.ng = len(self.main)

    # -- retrieval figures over the questions with a gold place
    def retrieval(self) -> dict:
        ranks = [self.sc.ranks[q] for q in self.main]
        ng = self.ng
        return {"ng": ng, "hit5": sum(1 for r in ranks if r and r <= 5), "hit10": sum(1 for r in ranks if r and r <= 10),
                "hit20": sum(1 for r in ranks if r and r <= 20),
                "mrr": sum(1 / r for r in ranks if r) / ng,
                "in_bundle": sum(1 for q in self.main if self.sc.in_bundle(q)),
                "full": sum(1 for r in ranks if r is not None)}

    def retrieval_line(self, attempt: int = 1) -> str:
        e = self.retrieval()
        return (f"RETRIEVAL attempt {attempt}: hit@5 {e['hit5']} of {e['ng']} ({pct(e['hit5'], e['ng'])}); "
                f"hit@10 {e['hit10']}; hit@20 {e['hit20']}; MRR {e['mrr']:.4f}; in the first bundle "
                f"{e['in_bundle']}; full evidence {e['full']}")

    # -- the verdict
    def right_wrong(self, cut=2):
        o = self.sc.outcomes(cut)
        return sum(x["right"] for x in o.values()), sum(x["wrong"] for x in o.values())

    def mcnemar(self):
        a = [x["right"] for x in self.sc.outcomes(1).values()]
        b = [x["right"] for x in self.sc.outcomes(2).values()]
        return mcnemar(a, b)

    def agreement(self):
        rows = [self.sc.row(q) for q in sorted(self.sc.behaviour) if q not in self.sc.dropped]
        graded = [r for r in rows if r["grade"] is not None]
        return sum(1 for r in graded if r["grade"] == r["check"]), len(graded)

    def retried_calls(self) -> int:
        return len(self.sc.retried | {q for q, b in self.sc.behaviour.items() if b == "EMPTY2"})

    def later_failures(self) -> int:
        count = 0
        for q in self.sc.later_fail:
            count += {"A2": 1, "A3": 2, "CAP": 2}.get(self.sc.behaviour[q], 0)
        return count

    def verdict_lines(self, *, spent: float, projection: float | None = None) -> list[str]:
        projection = 0.157 * self.n if projection is None else projection
        right, wrong = self.right_wrong()
        n, b = self.n, W.bar(self.n)
        lo, hi = exact_interval(right, n)
        o2 = self.sc.outcomes(2)
        e = self.retrieval()
        g, l, p = self.mcnemar()
        agree, graded = self.agreement()
        right_ok, wrong_ok = right >= b["need_right"], wrong <= b["max_wrong"]
        m = lambda ok: "met" if ok else "NOT met"  # noqa: E731
        return [
            f"VERDICT right end to end {right} of {n} ({pct(right, n)}; exact 95 % interval {100 * lo:.1f} to "
            f"{100 * hi:.1f} %); wrong claims {wrong} of {n} ({pct(wrong, n)})",
            f"BAR at least {b['need_right']} right ({m(right_ok)}) and at most {b['max_wrong']} wrong claims "
            f"({m(wrong_ok)}): {'PASSES' if right_ok and wrong_ok else 'MISSES'}; target at least "
            f"{b['target_right']}: {'reached' if right >= b['target_right'] else 'not reached'}",
            f"BESIDE hit@5 {e['hit5']} of {e['ng']} ({pct(e['hit5'], e['ng'])}); in the first bundle {e['in_bundle']}; "
            f"full evidence {e['full']}; answer correct, citation aside {sum(x['correct'] for x in o2.values())} of "
            f"{n}; not found {sum(x['nf'] for x in o2.values())}",
            f"BESIDE one search against two: A1 right {sum(x['right'] for x in self.sc.outcomes(1).values())}, "
            f"A2 right {right}: {g} gains, {l} losses, exact McNemar p {p:.4f}",
            f"BESIDE grader agreement {agree} of {graded}; search failures {self.later_failures()}; calls run once "
            f"more {self.retried_calls()}; spent {spent:.2f} USD (projection {projection:.2f}, brake "
            f"{2 * projection:.2f})",
        ]

    # -- the misses
    def misses(self) -> list[dict]:
        found = []
        o2 = self.sc.outcomes(2)
        docs = self.world.docs() if self.world else {}
        for q in sorted(o2):
            if o2[q]["right"]:
                continue
            r = self.sc.row(q)
            if o2[q]["nf"] or r["grade"] == "not_found":
                kind = "not_found"
            elif r["grade"] == "correct":
                kind = "incomplete"
            else:
                kind = "wrong"
            said = (self.sc.answer_text(q) if r["final_verdict"] == "answer" else
                    None if r["final_verdict"] == "error" else "Not found.")
            doc = docs.get(q, {})
            found.append({"id": q, "outcome": kind, "answer": said, "evidence_in_bundle": self.sc.in_bundle(q),
                          "rank": self.sc.ranks[q], "question": doc.get("question"),
                          "gold_answer": doc.get("gold_answer"), "gold_sources": doc.get("sources"),
                          "category": W.CATEGORY_OF[q], "keyword": bool((doc.get("keyword")) or q == W.KEYWORD_QID),
                          "routes": self.sc.routes.get(q, ["lexical", "semantic"])})
        return found

    def route_of(self, miss: dict) -> str:
        if miss["rank"] is None:
            return "none"
        routes = set(miss["routes"])
        if {"lexical", "semantic"} <= routes:
            return "both"
        if routes == {"lexical"}:
            return "lexical"
        if routes == {"semantic"}:
            return "semantic"
        return "other"

    def figures(self, *, spent: float, projection: float | None = None, control_hit5: int = 34, last=34) -> dict:
        projection = 0.157 * self.n if projection is None else projection
        right, wrong = self.right_wrong()
        n, b = self.n, W.bar(self.n)
        lo, hi = exact_interval(right, n)
        e = self.retrieval()
        g, l, p = self.mcnemar()
        agree, graded = self.agreement()
        o2 = self.sc.outcomes(2)
        misses = self.misses()
        by_rank = {"rank_1_5": 0, "rank_6_20": 0, "not_in_20": 0}
        by_ns, by_cat = {"embedded": 0, "keyword_only": 0}, {c: 0 for c in W.CATEGORIES}
        by_route = {k: 0 for k in ("lexical", "semantic", "both", "other", "none")}
        by_out = {"wrong": 0, "incomplete": 0, "not_found": 0}
        for m in misses:
            r = m["rank"]
            by_rank["rank_1_5" if r and r <= 5 else "rank_6_20" if r and r <= 20 else "not_in_20"] += 1
            by_ns["keyword_only" if m["keyword"] else "embedded"] += 1
            by_cat[m["category"]] += 1
            by_route[self.route_of(m)] += 1
            by_out[m["outcome"]] += 1
        return {
            "audit": W.AUDIT, "n": n, "n_gold": self.ng, "bar": b,
            "verdict": {"right": right, "wrong": wrong, "passes": right >= b["need_right"] and wrong <= b["max_wrong"],
                        "right_ok": right >= b["need_right"], "wrong_ok": wrong <= b["max_wrong"],
                        "target_ok": right >= b["target_right"], "interval_exact": [round(lo, 4), round(hi, 4)]},
            "beside": {"hit5": e["hit5"], "hit10": e["hit10"], "hit20": e["hit20"], "mrr": e["mrr"],
                       "in_bundle": e["in_bundle"], "full_evidence": e["full"],
                       "correct_citation_aside": sum(x["correct"] for x in o2.values()),
                       "not_found": sum(x["nf"] for x in o2.values()),
                       "a1_right": sum(x["right"] for x in self.sc.outcomes(1).values()),
                       "a3_right": sum(x["right"] for x in self.sc.outcomes(3).values()),
                       "mcnemar_a1_a2": {"gains": g, "losses": l, "p": p}, "grader_agree": agree, "graded": graded,
                       "search_failures": self.later_failures()},
            "misses": {"total": len(misses), "by_outcome": by_out, "by_rank": by_rank, "by_namespace": by_ns,
                       "by_category": by_cat, "by_route": by_route},
            "control": {"hit5": control_hit5, "of": 40, "last": last},
            "spend": {"usd": spent, "projection": projection, "brake": 2 * projection},
        }
