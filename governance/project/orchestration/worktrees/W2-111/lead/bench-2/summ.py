"""W2-111 run 2 (lead): per case, judged figure per round (CPU p95 less the median reference) and the verdict, for each
benchmark label in bench-2/. Judged = the committed form B's figure; raw CPU p95 and the reference median beside it."""
import collections, json, re, statistics as st, sys
from pathlib import Path

D = Path(__file__).resolve().parent


def final(f):
    p, r = collections.OrderedDict(), collections.OrderedDict()
    for l in open(f):
        d = json.loads(l); p.setdefault(d["test"], []).append(d["p95_ms"])
    for l in open(str(f) + ".ref"):
        d = json.loads(l); r.setdefault(d["test"], []).append(d["ref_ms"])
    out = collections.OrderedDict()
    for t, v in p.items():
        cpu, wall = v[0::2], v[1::2]; refs = r.get(t, [])[3:]; res = []
        for i, c in enumerate(cpu):
            chunk = refs[i * 40:(i + 1) * 40]
            m = st.median(chunk) if chunk else float("nan")
            res.append((c - m, c, m, wall[i] if i < len(wall) else float("nan")))
        out[t] = res
    return out


def verdicts(log):
    v = {}
    for line in open(log):
        m = re.match(r"^(PASSED|FAILED) (\S+)", line)
        if m:
            v[m.group(2)] = m.group(1)
        m = re.match(r"^FAILED (\S+)", line)
    return v


for label in sys.argv[1:] or ["quiet", "load20", "load20-planted", "load50", "load50-planted"]:
    log = D / f"{label}.log"
    figs = D / f"{label}.figs"
    if not log.exists():
        continue
    head = [l.strip() for l in open(log) if l.startswith("== ") or re.search(r"\d+ (passed|failed)", l)]
    print(f"### {label}: " + " | ".join(head))
    fails = {l.split()[1] for l in open(log) if l.startswith("FAILED ")}
    try:
        data = final(figs)
    except FileNotFoundError:
        data = {}
    for t, rounds in data.items():
        name = t.split("[")[-1].rstrip("]") if "[" in t else "W2-57 designer-read"
        verdict = "FAIL" if any(t in f for f in fails) else "pass"
        print(f"  {name:40s} {verdict}  judged/raw/ref/wall ms: " + "; ".join(
            f"{j:.1f}/{c:.1f}/{m:.1f}/{w:.0f}" for j, c, m, w in rounds))
