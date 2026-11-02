"""One measured 'search' session: reranks one visible question's candidates through gov.retrieval.rerank.

Usage: python3 driver.py <candidates.json> <question index> [private]
Prints one JSON line: id, wall seconds, the outcome (last_outcome), the scores in the order given.
With 'private', it scores every question with one private reranker started directly (the same-answers check).
"""
import json
import os
import sys
import time

from gov.retrieval import rerank


def main(path, index, mode=""):
    questions = json.load(open(path))
    if mode == "private":
        interpreter = os.path.join(os.environ["HOME"], rerank.PYTHON_REL)
        t0 = time.time()
        started = rerank._started(interpreter)
        score, device = (started[0], started[1]) if isinstance(started, tuple) else (started, None)
        load_s = time.time() - t0
        rows = []
        for q in questions:
            t = time.time()
            scores = [float(s) for s in score(q["query"], q["texts"])] if score else None
            rows.append({"id": q["id"], "s": time.time() - t, "scores": scores})
        print(json.dumps({"mode": "private", "device": str(device), "load_s": load_s, "pid": os.getpid(),
                          "rows": rows}), flush=True)
        return
    q = questions[int(index)]
    candidates = [{"text": text, "i": i} for i, text in enumerate(q["texts"])]
    t0 = time.time()
    ranked = rerank.rerank(q["query"], candidates)
    wall = time.time() - t0
    by_given = {c["i"]: c.get("rerank_score") for c in ranked}
    print(json.dumps({"id": q["id"], "wall_s": wall, "outcome": rerank.last_outcome(),
                      "scores": [by_given[i] for i in range(len(candidates))],
                      "order": [c["i"] for c in ranked]}), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:4])
