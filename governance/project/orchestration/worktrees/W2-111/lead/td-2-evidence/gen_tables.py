"""Builds the README tables' numbers from the instrumented runs (real2-*), the committed-code runs (final-*)."""
import json, collections, statistics as st, sys
def p95(v):
    v = sorted(v); return v[max(0, -(-95 * len(v) // 100) - 1)]
def instr(files, n=40):
    """-> {test: [(judged, raw, ref, wall, load) per round]} from instrumented per-call records (3 warm-up first)."""
    rows = collections.OrderedDict()
    for f in files:
        for l in open(f):
            r = json.loads(l); rows.setdefault(r["test"], []).append(r)
    out = collections.OrderedDict()
    for t, rs in rows.items():
        rs = sorted(rs, key=lambda r: r["k"])[3:]
        res = []
        for i in range(0, len(rs), n):
            c = rs[i:i+n]
            if len(c) < n: continue
            raw = p95([r["cpu"] for r in c]); ref = st.median(r["stub"] for r in c)
            res.append((raw - ref, raw, ref, p95([r["wall"] for r in c]), c[-1]["la"]))
        out[t] = res
    return out
def final(f):
    p = collections.OrderedDict(); r = collections.OrderedDict()
    for l in open(f):
        d = json.loads(l); p.setdefault(d["test"], []).append(d["p95_ms"])
    for l in open(f + ".ref"):
        d = json.loads(l); r.setdefault(d["test"], []).append(d["ref_ms"])
    out = collections.OrderedDict()
    for t, v in p.items():
        cpu, wall = v[0::2], v[1::2]; refs = r[t][3:]; res = []
        for i, c in enumerate(cpu):
            m = st.median(refs[i*40:(i+1)*40]); res.append((c - m, c, m, wall[i], ""))
        out[t] = res
    return out
def name(t): return t.split("[")[-1].rstrip("]") if "[" in t else "designer-read"
def fmt(rounds, which=0):
    return " / ".join(f"{x[which]:.0f}" for x in rounds) if rounds else "-"
if __name__ == "__main__":
    D = "/home/usain/gov-os-worktrees/W2-111-tests/.gov-runtime/scratch/td/"
    quiet = instr([D + "real2-quiet.figs"])
    l25 = instr([D + f"real2-w3-{x}.figs" for x in "abc"])
    l50 = instr([D + f"real2-w4-{x}.figs" for x in "abc"])
    pl50 = instr([D + f"real2-w4-pl-{x}.figs" for x in "abc"], n=8)
    fin = final(D + "final-quiet.figs")
    try: plamb = final(D + "final-planted-amb.figs")
    except Exception: plamb = {}
    print("test | quiet judged(raw-ref) | ~25 judged (raw) rounds | 50+ judged (raw) | planted50 judged (raw) | committed ambient | planted ambient judged rounds")
    for t in quiet:
        print(name(t), "|", f"{quiet[t][0][0]:.1f} ({quiet[t][0][1]:.1f}-{quiet[t][0][2]:.1f})", "|",
              "; ".join(f"{x[0]:.1f} ({x[1]:.1f}-{x[2]:.1f}, la {x[4]})" for x in l25.get(t, [])), "|",
              "; ".join(f"{x[0]:.1f} ({x[1]:.1f}-{x[2]:.1f}, la {x[4]})" for x in l50.get(t, [])), "|",
              "; ".join(f"{x[0]:.1f} ({x[1]:.1f}-{x[2]:.1f})" for x in pl50.get(t, [])), "|",
              "; ".join(f"{x[0]:.1f}" for x in fin.get(t, [])), "|", "; ".join(f"{x[0]:.1f}" for x in plamb.get(t, [])))
