"""Per case, per round (3 warm-ups, then 40 samples per round): the raw CPU p95 (round 1's judged figure), the figure
after each candidate form, and the references. usage: an3.py <figs file>... (several files are merged by test id)"""
import json, sys, statistics as st, collections
def p95(v):
    v = sorted(v); return v[max(0, -(-95 * len(v) // 100) - 1)]
rows = collections.OrderedDict()
for f in sys.argv[1:]:
    for l in open(f):
        r = json.loads(l); rows.setdefault(r["test"], []).append(r)
print(f"{'case':44} rd  load  rawCPU  CPU-stub  CPU/stub*15.2  CPU/start*11.5 | wall  stub_med start_med")
for test, rs in rows.items():
    rs = sorted(rs, key=lambda r: r["k"])[3:]
    short = test.split("::")[-1].replace("test_decision_p95_is_under_100_ms","w1-02").replace("test_a_call_waits_under_100_ms_p95_for_the_hook","w1-05").replace("test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95","w2-57")
    for n in range(0, len(rs), 40):
        c = rs[n:n+40]
        if len(c) < 40: continue
        cpu = [r["cpu"] for r in c]; stub = st.median(r["stub"] for r in c); start = st.median(r["start"] for r in c)
        print(f"{short:44} {n//40+1}  {c[-1]['la']:>5} {p95(cpu):7.1f} {p95(cpu)-stub:8.1f} {p95(cpu)/stub*15.2:13.1f} {p95(cpu)/start*11.5:14.1f} | {p95([r['wall'] for r in c]):6.1f} {stub:7.1f} {start:7.1f}")
