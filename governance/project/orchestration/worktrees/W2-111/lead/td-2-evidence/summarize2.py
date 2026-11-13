"""usage: summarize2.py <final-label.figs>: per case and round: judged (cpu p95 - median ref), raw cpu p95, ref median, wall p95."""
import json, sys, statistics as st, collections
f = sys.argv[1]
p = collections.OrderedDict(); r = collections.OrderedDict()
for l in open(f):
    d = json.loads(l); p.setdefault(d["test"], []).append(d["p95_ms"])
for l in open(f + ".ref"):
    d = json.loads(l); r.setdefault(d["test"], []).append(d["ref_ms"])
worst = 0
for t, vals in p.items():
    cpu, wall = vals[0::2], vals[1::2]
    refs = r[t][3:]  # after the 3 warm-up calls
    short = t.split("/")[-2] + " " + t.split("[")[-1].rstrip("]") if "[" in t else t.split("/")[-2]
    out = []
    for i, c in enumerate(cpu):
        rr = refs[i*40:(i+1)*40]; m = st.median(rr)
        out.append((c - m, c, m, wall[i]))
    best = min(o[0] for o in out); worst = max(worst, best)
    print(f"{short:46} judged/round {[round(o[0],1) for o in out]}  raw cpu {[round(o[1],1) for o in out]}  ref med {[round(o[2],1) for o in out]}  wall {[round(o[3],1) for o in out]}")
print("max over cases of the best round's judged figure:", round(worst,1))
