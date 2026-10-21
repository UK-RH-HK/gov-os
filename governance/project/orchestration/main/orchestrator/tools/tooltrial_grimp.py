"""Tool trial c (DEC-889 item 13 c): grimp's selection against W2-66's declared map, on lens H's planted faults.

    /tmp/gov-os-tooltrial/bin/python tooltrial_grimp.py <clone of w2/integrate>

It scores four selectors, at the granularity each would really select, with lens H's definitions (analyse_b2.py):
  declared         tests/unit + suites whose ticket's allowed_paths match the file (the shared core -> everything)
  grimp            test files that import the module or any module grimp finds upstream of it (in-process imports)
  grimp_or_decl    the union of the two (the declared map widened by grimp's test-side reach)
  lensH_static     lens H's own stdlib import graph, for comparison
A selector detects a fault when it selects at least one test of F (the tests that failed with the fault, less the
module's control). Time = the sum of lens H's part-1 durations of what it selects. Reads lens H's logs; writes none.
"""
import json
import sys
import time
from pathlib import Path

import grimp

H = Path("/tmp/gov-os-assessment-H")
clone = Path(sys.argv[1])
sys.path.insert(0, str(clone / "src"))
results = [json.loads(line) for line in open(H / "logs/results_b2.jsonl")]
amap = json.load(open(H / "logs/allowed_map.json"))["files"]
ig = json.load(open(H / "logs/import_graph.json"))
dur = {k: v["t"] for k, v in json.load(open(H / "logs/p1_summary.json"))["tests"].items()}
all_tests = set(dur)


def norm(t):
    return t[len(".py::"):].replace(".", "/") + ".py" if t.startswith(".py::") else t


def suite(t):
    p = norm(t).split("::", 1)[0].split("/")
    return p[2] if p[1] == "acceptance" else "unit"


def hits(F, s):
    files = {t.split("::", 1)[0] for t in s}
    return {t for t in F if (t in s) or ("::" not in t and t in files)}


def module_name(path):
    m = path[len("src/"):-3].replace("/", ".")
    return m[:-len(".__init__")] if m.endswith(".__init__") else m


t0 = time.time()
graph = grimp.build_graph("gov", include_external_packages=False, cache_dir=None)
build_s = time.time() - t0
controls = {}
for r in results:
    if r["id"].startswith("B2-control:"):
        controls.setdefault(r["file"], set()).update(r["failed"])
if (H / "logs/results_a6.jsonl").exists():
    for line in open(H / "logs/results_a6.jsonl"):
        r = json.loads(line)
        if r["id"].startswith("A6-control:"):
            controls.setdefault(r["file"], set()).update(r["failed"])

STRATS = ("declared", "grimp", "grimp_or_decl", "lensH_static")
rows = []
for r in results:
    if r["id"].startswith("B2-control:"):
        continue
    f = r["file"].replace(str(clone) + "/", "").replace("/tmp/gov-os-assessment-H/repo/", "")
    F = {norm(t) for t in r["failed"]} - {norm(t) for t in controls.get(r["file"], set())}
    core = amap.get(f, {}).get("core", False)
    declared_suites = {"unit"} | set(amap.get(f, {}).get("suites", []))
    mod = module_name(f)
    ups_grimp = ({mod} | set(graph.find_upstream_modules(mod))) if mod in graph.modules else {mod}
    grimp_files = {tf for tf, imps in ig["test_imports"].items() if ups_grimp & set(imps)}
    ups_h = set(ig["upstream"].get(mod, []))
    h_files = {tf for tf, imps in ig["test_imports"].items() if ups_h & set(imps)}
    sel = {
        "declared": all_tests if core else {t for t in all_tests if suite(t) in declared_suites},
        "grimp": {t for t in all_tests if t.split("::", 1)[0] in grimp_files},
        "lensH_static": {t for t in all_tests if t.split("::", 1)[0] in h_files},
    }
    sel["grimp_or_decl"] = sel["declared"] | sel["grimp"]
    row = {"id": r["id"], "file": f, "core": core, "F": len(F), "upstream_grimp": len(ups_grimp)}
    for name in STRATS:
        s = sel[name]
        hit = hits(F, s)
        row[name] = {"detect": bool(hit) if F else None, "recall": (len(hit) / len(F)) if F else None,
                     "time": round(sum(dur.get(t, 0) for t in s), 1)}
    rows.append(row)

killable = [x for x in rows if x["F"]]
total = sum(dur.values())
print(f"grimp {grimp.__version__ if hasattr(grimp, '__version__') else '3.17'}: graph of gov built in {build_s:.2f} s, "
      f"{len(graph.modules)} modules")
print(f"planted faults run: {len(rows)}; detected by the full run: {len(killable)}")
for name in STRATS:
    det = sum(1 for x in killable if x[name]["detect"])
    rec = sum(x[name]["recall"] for x in killable) / max(len(killable), 1)
    t = sum(x[name]["time"] for x in killable) / max(len(killable), 1)
    med = sorted(x[name]["time"] for x in killable)[len(killable) // 2] if killable else 0
    low = min((x[name]["recall"] for x in killable), default=0)
    print(f"{name:14s} detects {det}/{len(killable)}  mean recall {rec:.2f} (lowest {low:.2f})  mean time {t:7.0f} s "
          f"({100 * t / total:4.1f}% of the full run's {total:.0f} s; median {100 * med / total:4.1f}%)")
print()
for x in rows:
    flags = " ".join(f"{n}={'Y' if x[n]['detect'] else ('-' if x[n]['detect'] is None else 'N')}" for n in STRATS)
    print(f"{x['id'][3:70]:67s} core={'Y' if x['core'] else 'N'} F={x['F']:4d} ups={x['upstream_grimp']:3d} {flags}")
json.dump(rows, open(Path(sys.argv[0]).with_name("tooltrial_grimp_last.json"), "w"), indent=1)
