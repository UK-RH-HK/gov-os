#!/usr/bin/env python3
"""USAGE-1: residuals of the $-list fit, and a two-part fit (cache-read $ vs the rest) against the weekly meter."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A
from savings import t
pts = json.loads((HERE / "meter.json").read_text())["points"]
ext = A.EXTERNAL[0]; e0, e1 = t(ext["start"] + ":00+00:00"), t(ext["end"] + ":00+00:00")
cs = sorted(A.C, key=lambda c: c["ts"])
rate = {"claude-opus-5-5": 0.20, "claude-haiku-5-5": 0.01}
rows = []; i = 0; crd = rest = 0.0
for ts, pct in pts:
    tt = t(ts + "+00:00")
    while i < len(cs) and t(cs[i]["ts"]) <= tt:
        c = cs[i]; r = c["cr"] * rate.get(c["model"], 0.2) / 1e6
        crd += r; rest += (c["cost"] or 0) - r; i += 1
    x2 = rest + ext["cost"] * min(max((tt - e0) / (e1 - e0), 0), 1)
    rows.append((ts, pct, crd, x2))
# two-part least squares through origin
s11 = sum(r[2] ** 2 for r in rows); s22 = sum(r[3] ** 2 for r in rows); s12 = sum(r[2] * r[3] for r in rows)
y1 = sum(r[2] * r[1] for r in rows); y2 = sum(r[3] * r[1] for r in rows)
det = s11 * s22 - s12 ** 2; a = (y1 * s22 - y2 * s12) / det; b = (y2 * s11 - y1 * s12) / det
res = [r[1] - a * r[2] - b * r[3] for r in rows]
print(f"two-part: pt per $ cache-read {a:.4f}, per $ other {b:.4f} (ratio {a / b:.2f}); RMSE {(sum(x * x for x in res) / len(res)) ** .5:.2f}")
k = 1 / 27.5
for ts, pct, c1, c2 in rows:
    if ts[11:13] in ("00", "06", "12", "18") or ts == rows[-1][0]:
        print(ts, pct, f"model {(c1 + c2) * k:.1f}", f"miss {pct - (c1 + c2) * k:+.1f}")
