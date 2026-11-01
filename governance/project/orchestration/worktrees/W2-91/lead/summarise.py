"""Summarises measure records (scores only: ids, counts, ranks, digests; never a question's text or a retrieved
item's text) into a facts file for the evidence record.

    python3 summarise.py <out.md> <label>=<record.json> [<label>=<record.json> ...]
"""
import json
import sys

out = sys.argv[1]
runs = []
for arg in sys.argv[2:]:
    label, path = arg.split("=", 1)
    runs.append((label, path, json.load(open(path, encoding="utf-8"))))

lines = ["# W2-91 measure facts (lead's summary of the records; scores only)", ""]
for label, path, d in runs:
    t = d["total"]
    inb = sum(1 for q in d["questions"] if q["in_bundle"])
    lines.append(f"- **{label}:** record `{path}`; root `{d['root']}`; commit `{d['commit']}`; part `{d['part']}`; "
                 f"retriever `{d['retriever']['executable']}` ({d['retriever']['version']}); budget {d['budget']}; "
                 f"hit@5 {t['hit_at_5']['count']} of {t['hit_at_5']['of']} ({t['hit_at_5']['percent']} %, floor {t['hit_at_5']['floor']}); "
                 f"full evidence {t['full_evidence']['count']} of {t['full_evidence']['of']} ({t['full_evidence']['percent']} %, target {t['full_evidence']['target']}); "
                 f"in the bundle {inb} of {len(d['questions'])}.")
    if "comparison" in d or "compare" in d:
        lines.append(f"  - comparison block: `{json.dumps(d.get('comparison') or d.get('compare'))[:3000]}`")
lines += ["", "Per question: hit@5, first gold rank, in the bundle, full evidence (pieces found/needed), calls, stacked digest.", ""]
header = "| Q | " + " | ".join(label for label, _, _ in runs) + " |"
lines += [header, "|" + "---|" * (len(runs) + 1)]
by = [{q["id"]: q for q in d["questions"]} for _, _, d in runs]
for qid in sorted(by[0]):
    cells = []
    for m in by:
        q = m.get(qid)
        if not q:
            cells.append("—")
            continue
        yn = lambda b: "yes" if b else "no"  # noqa: E731
        rank = q["first_gold_rank"] if q["first_gold_rank"] is not None else "none"
        cmp = ""
        if q.get("compare"):
            cmp = "; compare: " + "; ".join("same" if c["same"] else "differs in " + ", ".join(c["differs"])
                                            for c in q["compare"])
        cells.append(f"{yn(q['hit_at_5'])}, {rank}, {yn(q['in_bundle'])}, {yn(q['full_evidence'])} "
                     f"({q['pieces_found']}/{q['pieces_needed']}), {q['calls']}, {q['stacked_digest']}{cmp}")
    lines.append(f"| {qid} | " + " | ".join(cells) + " |")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
