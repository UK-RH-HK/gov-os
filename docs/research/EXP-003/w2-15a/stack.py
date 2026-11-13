"""W2-15a's stacking test, once: ``python3 stack.py <gov> <root> <question.yaml> [batch tokens] [stack tokens]``.
The question is asked of ``gov retrieve`` (bundle budget = one batch) with its continuations; the items are stacked
whole into batches of at most 8k tokens until 24k (or no continuation). Checked: each item's sha256 equals its span's
bytes in the root (assembled complete), no span hash twice, no two spans overlapping, and the gold pieces held."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

from gov.retrieval.measure import _span

gov, root, qfile = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
BATCH, STACK = (int(a) for a in (sys.argv[4:6] + ["8000", "24000"][len(sys.argv[4:6]):]))
q = yaml.safe_load(qfile.read_text())
gold = [[(a["path"], *_span(a, root, "visible", q["id"])) for a in (s if isinstance(s, list) else [s])]
        for s in q["sources"]]
opts = [*(["--ticket", q["ticket"]] if q.get("ticket") else []), *(["--radius", str(q["radius"])]
        if q.get("radius") is not None else []), "--bundle-budget", str(BATCH)]
batches, cur, used, token, calls, every = [], [], 0, None, [], []
while used < STACK:
    out = subprocess.run([gov, "retrieve", *opts, *(["--continue", token] if token else []), q["question"], "--json"],
                         cwd=root, capture_output=True, text=True, check=True)
    doc = json.loads(out.stdout)
    bundle = doc.get("result", doc)
    calls.append({"items": len(bundle["evidence"]), "tokens": sum(-(-len(e["text"]) // 4) for e in bundle["evidence"]),
                  "rerank": bundle.get("rerank", {}).get("by"), "stopping": bundle["stopping_reason"]})
    for e in bundle["evidence"]:
        size = -(-len(e["text"]) // 4)
        if used + size > STACK:
            used = STACK
            break
        if sum(-(-len(x["text"]) // 4) for x in cur) + size > BATCH and cur:
            batches.append(cur)
            cur = []
        cur.append(e)
        every.append(e)
        used += size
    token = bundle.get("continuation")
    if not token:
        break
batches += [cur] if cur else []
lines = {}
whole = all(hashlib.sha256(b"".join(lines.setdefault(e["path"], (root / e["path"]).read_bytes().splitlines(True))
                                    [e["start_line"] - 1:e["end_line"]])).hexdigest() == e["sha256"] for e in every)
hashes = [e["sha256"] for e in every]
spans = sorted((e["path"], e["start_line"], e["end_line"]) for e in every)
overlaps = sum(a[0] == b[0] and b[1] <= a[2] for a, b in zip(spans, spans[1:]))
held = sum(any(e["path"] == p and e["start_line"] <= last and first <= e["end_line"] for e in every for p, first, last
               in s) for s in gold)
print(json.dumps({"question": q["id"], "batch_tokens": BATCH, "stack_tokens": STACK, "calls": calls,
                  "batches": [{"items": len(b), "tokens": sum(-(-len(e["text"]) // 4) for e in b)} for b in batches],
                  "items": len(every), "tokens": sum(-(-len(e["text"]) // 4) for e in every), "complete": whole,
                  "duplicate_hashes": len(hashes) - len(set(hashes)), "overlapping_spans": overlaps,
                  "gold_pieces": f"{held} of {len(gold)}", "spans": [list(s) for s in spans]}, indent=1))
