import json, sys, statistics as st
def p95(v):
    v = sorted(v); return v[max(0, -(-95 * len(v) // 100) - 1)]
def load(lbl): return json.load(open(f"/home/usain/gov-os-worktrees/W2-111-tests/.gov-runtime/scratch/td/exp2-{lbl}.json"))["rows"]
Q = [load("quiet1"), load("w2-5"), load("w2-6")]
print("== per-run: judged figures (ms)")
print("run        hook   raw_cpu_p95 | cpu-stub_med | wall_p95 wall-stub_wall_med | cpu_p95/start_med | cpu_p95/stub_med | cpu_p95/loop_med | cpu_p95/mix_med")
for lbl in ["quiet1","w2-5","w2-6","w2-1","w2-2","w2-3","w2-4"]:
    rows = load(lbl)
    for h in ("hook_eng","hook_des"):
        c = [r[h][0]*1000 for r in rows]; w=[r[h][1]*1000 for r in rows]
        med = lambda k,i: st.median(r[k][i]*1000 for r in rows)
        print(f"{lbl:7} {h:9} {p95(c):7.1f} | {p95(c)-med('stub',0):7.1f} | {p95(w):7.1f} {p95(w)-med('stub',1):7.1f} | "
              f"{p95(c)/med('start',0):6.2f} | {p95(c)/med('stub',0):6.2f} | {p95(c)/med('loop',0):6.2f} | {p95(c)/med('mix',0):6.2f}")
print("== quiet-to-loaded ratio of medians (loaded = w2-1..3 pooled; quiet = quiet1,w2-5,w2-6 pooled)")
import itertools
L = [r for l in ("w2-1","w2-2","w2-3") for r in load(l)]
Qp = [r for l in ("quiet1","w2-5","w2-6") for r in load(l)]
for k in ("stub","start","loop","mix","plant150","hook_eng","hook_des"):
    for i,nm in ((0,"cpu"),(1,"wall")):
        ql = [r[k][i]*1000 for r in Qp]; ll=[r[k][i]*1000 for r in L]
        print(f"{k:9} {nm}: quiet min {min(ql):6.1f} med {st.median(ql):6.1f} | loaded min {min(ll):6.1f} med {st.median(ll):6.1f} p05 {sorted(ll)[len(ll)//20]:6.1f} | med ratio {st.median(ll)/st.median(ql):.2f} min ratio {min(ll)/min(ql):.2f}")
