"""Scratch: for visible questions, the shipped retrieve's first 12 items and which hit gold (visible half only)."""
import json, subprocess, sys
from pathlib import Path
import yaml
from gov.retrieval.measure import _span

gov, root = sys.argv[1], Path(sys.argv[2])
for qid in sys.argv[3:]:
    f = root / "fixtures/evaluation/memory-retrieval/visible" / f"{qid}.yaml"
    q = yaml.safe_load(f.read_text())
    gold = [(a["path"], *_span(a, root, "visible", qid)) for s in q["sources"] for a in (s if isinstance(s, list) else [s])]
    opts = [*(["--ticket", q["ticket"]] if q.get("ticket") else []), *[w for i in q.get("ids") or [] for w in ("--id", str(i))],
            *(["--radius", str(q["radius"])] if q.get("radius") is not None else [])]
    out = subprocess.run([gov, "retrieve", *opts, q["question"], "--json"], cwd=root, capture_output=True, text=True)
    b = json.loads(out.stdout); b = b.get("result", b)
    print(f"== {qid}: {q['question']}  gold={gold}")
    for n, e in enumerate(b["evidence"][:12], 1):
        g = any(e["path"] == p and e["start_line"] <= l and fl <= e["end_line"] for p, fl, l in gold)
        print(f"  {n:2} {'GOLD' if g else '    '} {e['path']}:{e['start_line']}-{e['end_line']} {e['routes']}")
