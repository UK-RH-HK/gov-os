"""W2-15a's tables from the measure's records: ``python3 table.py <mode>=<record.json>...`` prints, as Markdown, hit@5
and full evidence per mode and half, and per question each mode's first gold rank (``-``: never retrieved) and full
evidence. The records hold ids, counts, ranks and digests only, so the hidden half shows nothing else."""
import json
import sys

modes = dict(arg.split("=", 1) for arg in sys.argv[1:])
docs = {m: {(q["part"], q["id"]): q for q in json.load(open(p))["questions"]} for m, p in modes.items()}
keys = list(next(iter(docs.values())))
print("| mode | hit@5 visible | hit@5 hidden | hit@5 all | full ev. visible | full ev. hidden | full ev. all |")
print("|---|---|---|---|---|---|---|")
for m, qs in docs.items():
    def n(key, part=None):
        sel = [q for k, q in qs.items() if part in (None, k[0])]
        return f"{sum(q[key] for q in sel)}/{len(sel)}"
    print(f"| {m} | {n('hit_at_5', 'visible')} | {n('hit_at_5', 'hidden')} | {n('hit_at_5')} "
          f"| {n('full_evidence', 'visible')} | {n('full_evidence', 'hidden')} | {n('full_evidence')} |")
print("\nPer question: first gold rank (bold: hit@5), then F when the full evidence is stacked.\n")
print("| id | " + " | ".join(modes) + " | hit@5 in |")
print("|---|" + "---|" * (len(modes) + 1))
for k in keys:
    cells = []
    for m in modes:
        q = docs[m][k]
        rank = str(q["first_gold_rank"] or "-")
        cells.append((f"**{rank}**" if q["hit_at_5"] else rank) + (" F" if q["full_evidence"] else ""))
    hit = [m for m in modes if docs[m][k]["hit_at_5"]]
    print(f"| {k[1]} | " + " | ".join(cells) + f" | {', '.join(hit) or 'none'} |")
