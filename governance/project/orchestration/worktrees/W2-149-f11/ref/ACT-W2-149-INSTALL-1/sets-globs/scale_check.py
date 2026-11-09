"""ACT-SETS-GLOBS-1: the hidden part's walk at the real sets root's scale, timed under the machine's working load.

  python3 scale_check.py <hook> <map> <work folder>

Builds a synthetic sets root in <work folder> (empty files, names only) at about the real root's scale as the CTO's
check of 2026-11-09 measured it (4,560 hidden files there): about 9,000 hidden files here, and a large open part
(visible halves, work folders, 60 run folders with nested outputs: about 130,000 open files), so a recursive walk of
runs/ or fixtures/ costs at least what it does there. Then,
the median of 10 fresh walks each (the caches cleared): the judge's _Part with the live globs (what the guard walks
today), the judge's _Part with the candidate globs (the map alone), and the candidate hook's Narrow with the candidate
globs (what the guard walks after the ACT). It checks that Narrow finds exactly the judge's files. Last line PASS or
FAIL (FAIL: the lists differ, or Narrow's median is over 5 times the live walk's plus 20 ms).
"""
import importlib.util
import os
import statistics
import sys
import time

hook_path, map_path, work = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("hook", hook_path)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)
from gov.guard import reads  # noqa: E402

SetsRoot, Judge, Narrow = hook.classes()
import yaml  # noqa: E402

cand = yaml.safe_load(open(map_path))["sets_root_hidden"]["hidden"]
live = [g for g in cand if "/*/" not in g]
root = os.path.join(work, "gov-os-eval")
if not os.path.exists(root):
    def touch(rel, n, ext=".yaml"):
        d = os.path.join(root, rel)
        os.makedirs(d, exist_ok=True)
        for i in range(n):
            open(os.path.join(d, f"f{i:05d}{ext}"), "w").close()
    for s, hid in (("memory-retrieval", 800), ("memory-verdict", 600), ("memory-verdict-2", 900),
                   ("sandbox-guard-exp-1", 900), ("memory-verdict-3", 300), ("memory-verdict-4", 0)):
        if hid:
            touch(f"fixtures/evaluation/{s}/hidden", hid)
        touch(f"fixtures/evaluation/{s}/visible", 400)
        for sub in range(20):
            touch(f"fixtures/evaluation/{s}/work/w{sub:02d}", 100, ".json")
    touch("transcripts", 500, ".md")
    touch("runs/fresh-80/rows", 500, ".json")
    for r in range(60):
        for sub in range(10):
            touch(f"runs/run-{r:03d}/out/{sub:02d}", 200, ".json")
        if r % 10 == 0:
            open(os.path.join(root, f"runs/run-{r:03d}/misses.jsonl"), "w").close()
            open(os.path.join(root, f"runs/run-{r:03d}/miss-classes.json"), "w").close()
    touch("indep-walls/writer/R1", 50)
total = sum(len(f) for _d, _s, f in os.walk(root))


def timed(make):
    ms, files = [], None
    for _ in range(10):
        for c in Narrow.caches:
            c.clear()
        t0 = time.monotonic()
        files = make().files
        ms.append((time.monotonic() - t0) * 1000)
    return statistics.median(ms), files


load = os.getloadavg()
t_live, f_live = timed(lambda: reads._Part(root, live, reads.HIDDEN_REFUSAL))
t_map, f_map = timed(lambda: reads._Part(root, cand, reads.HIDDEN_REFUSAL))
t_nar, f_nar = timed(lambda: Narrow(root, cand, reads.HIDDEN_REFUSAL))
same = f_map == f_nar
fast = t_nar <= 5 * t_live + 20
print(f"synthetic sets root: {total} files; load average {load[0]:.1f} {load[1]:.1f} {load[2]:.1f}")
print(f"the judge, live globs ({len(live)}): {len(f_live)} hidden files, median {t_live:.1f} ms")
print(f"the judge, candidate globs ({len(cand)}), the map alone: {len(f_map)} hidden files, median {t_map:.1f} ms")
print(f"Narrow, candidate globs ({len(cand)}), the ACT: {len(f_nar)} hidden files, median {t_nar:.1f} ms")
print(f"{'ok  ' if same else 'FAIL'} Narrow's files equal the judge's: {same}")
print(f"{'ok  ' if fast else 'FAIL'} Narrow within 5 x the live walk + 20 ms: {fast}")
print("PASS" if same and fast else "FAIL")
sys.exit(0 if same and fast else 1)
