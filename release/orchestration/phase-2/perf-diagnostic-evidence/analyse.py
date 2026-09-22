#!/usr/bin/env python3
"""Aggregate the P2-PERF-0001 per-family sweep into the report tables."""
import glob
import json
import os
import statistics
import sys

D = sys.argv[1]
metas = sorted(glob.glob(f"{D}/fam-*.meta.json"))
fams = []
all_tests = []
for m in metas:
    d = json.load(open(m))
    fam = os.path.basename(m)[4:-10]
    tsv = f"{D}/fam-{fam}.tests.tsv"
    tests = []
    if os.path.exists(tsv):
        for line in open(tsv).read().splitlines()[1:]:
            dur, outcome, name = line.split("\t")
            tests.append((float(dur), outcome, name))
    # completion order = the order libtest ran them under --test-threads=1
    timed = []
    ttsv = f"{D}/fam-{fam}.timed.tsv"
    fams.append({
        "family": fam, "wall": d["wall_s"], "cpu": d["cpu_total_s"],
        "cpu_sys": d["cpu_sys_s"], "cpu_user": d["cpu_user_s"],
        "cpu_per_wall": d["cpu_per_wall"], "n": d["n_test_lines"],
        "rc": d["exit_code"], "result": d["result"],
        "sum_tests": d["sum_test_durations_s"],
        "blk_out": d["block_output_ops"],
        "load_before": d["load_before"].split()[0],
        "load_after": d["load_after"].split()[0],
        "tests": tests,
    })
    all_tests += [(dur, outcome, f"{name}") for dur, outcome, name in tests]

fams.sort(key=lambda f: -f["wall"])
tot_wall = sum(f["wall"] for f in fams)
tot_cpu = sum(f["cpu"] for f in fams)
tot_sys = sum(f["cpu_sys"] for f in fams)
tot_n = sum(f["n"] for f in fams)
tot_blk = sum(f["blk_out"] for f in fams)

print("=" * 100)
print(f"FAMILIES: {len(fams)}   TESTS SEEN: {tot_n}")
print(f"SUM of family wall (serial-within-family):  {tot_wall:9.1f} s")
print(f"SUM of family CPU  (user+sys, incl. gov/git subprocesses): {tot_cpu:9.1f} s")
print(f"   of which SYSTEM time (kernel/IO):        {tot_sys:9.1f} s  = {100*tot_sys/tot_cpu:.1f}% of CPU")
print(f"   of which USER   time (compute in gov):   {tot_cpu-tot_sys:9.1f} s  = {100*(tot_cpu-tot_sys)/tot_cpu:.1f}% of CPU")
print(f"aggregate cpu/wall across sweep:            {tot_cpu/tot_wall:.2f}")
print(f"blocks written (512B units):                {tot_blk:,} = {tot_blk*512/1e9:.1f} GB")
failed = [f for f in fams if f["rc"] != 0]
print(f"NON-ZERO EXIT: {[f['family'] for f in failed] if failed else 'none'}")
print("=" * 100)

print("\n### PER-FAMILY (serial within family; families run 6-at-a-time) ###")
print(f"{'family':<20}{'tests':>6}{'wall_s':>10}{'cpu_s':>10}{'cpu/wall':>9}{'sys%':>6}{'s/test':>8}{'ld_a':>7}")
for f in fams:
    per = f["wall"] / f["n"] if f["n"] else 0
    print(f"{f['family']:<20}{f['n']:>6}{f['wall']:>10.1f}{f['cpu']:>10.1f}"
          f"{f['cpu_per_wall']:>9.2f}{100*f['cpu_sys']/f['cpu'] if f['cpu'] else 0:>6.1f}"
          f"{per:>8.1f}{f['load_after']:>7}")

print("\n### 30 SLOWEST INDIVIDUAL TESTS (per-test timing sound: --test-threads=1) ###")
all_tests.sort(key=lambda t: -t[0])
print(f"{'dur_s':>9}  {'outcome':<8}test")
for dur, outcome, name in all_tests[:30]:
    print(f"{dur:>9.1f}  {outcome:<8}{name}")

print("\n### DISTRIBUTION ###")
durs = sorted(d for d, _, _ in all_tests)
if durs:
    print(f"n={len(durs)}  sum={sum(durs):.1f}s  mean={statistics.mean(durs):.1f}s  median={statistics.median(durs):.1f}s")
    print(f"min={durs[0]:.2f}s  p90={durs[int(.9*len(durs))]:.1f}s  max={durs[-1]:.1f}s")
    for cut in (1, 5, 10, 30, 60, 120):
        sel = [d for d in durs if d >= cut]
        print(f"  tests >= {cut:>4}s: {len(sel):>4}  ({100*len(sel)/len(durs):5.1f}% of tests)  "
              f"{sum(sel):>8.1f}s = {100*sum(sel)/sum(durs):5.1f}% of total test time")
    # Pareto: how few tests hold most of the time
    run = 0
    for i, d in enumerate(reversed(durs), 1):
        run += d
        if run >= 0.5 * sum(durs):
            print(f"  >>> the slowest {i} tests ({100*i/len(durs):.1f}%) hold 50% of all test time")
            break
    run = 0
    for i, d in enumerate(reversed(durs), 1):
        run += d
        if run >= 0.8 * sum(durs):
            print(f"  >>> the slowest {i} tests ({100*i/len(durs):.1f}%) hold 80% of all test time")
            break

print("\n### PER-PROCESS FIXED SETUP (first test in each family absorbs the lazy OnceLock fixtures) ###")
print(f"{'family':<20}{'first_test_s':>13}{'median_rest_s':>15}{'delta_s':>10}  first test")
deltas = []
for f in fams:
    if f["n"] < 3:
        continue
    # reconstruct run order from completed_at ordering: tests.tsv is sorted by duration,
    # so re-read the timed file order instead
    order = []
    for line in open(f"{D}/fam-{f['family']}.timed.tsv").read().splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[1].startswith("test ") and " ... " in parts[1]:
            order.append((float(parts[0]), parts[1]))
    if len(order) < 3:
        continue
    durs_in_order = []
    prev = None
    for t, line in order:
        if prev is None:
            prev = t
        durs_in_order.append(t - prev)
        prev = t
    # first element is bogus (0); recompute against family start = 0
    first = order[0][0]
    rest = [order[i][0] - order[i - 1][0] for i in range(1, len(order))]
    med = statistics.median(rest)
    deltas.append(first - med)
    print(f"{f['family']:<20}{first:>13.1f}{med:>15.1f}{first-med:>10.1f}  "
          f"{order[0][1][5:60]}")
if deltas:
    print(f"\nmedian estimated per-process fixed setup cost: {statistics.median(deltas):.1f} s")
    print(f"(paid once per test PROCESS: sharding into N processes pays it N times)")
