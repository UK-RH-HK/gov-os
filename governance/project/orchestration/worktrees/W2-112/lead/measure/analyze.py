"""Summarise measure.py's record. Usage: python3 analyze.py <record.json>"""
import json
import statistics
import sys

r = json.load(open(sys.argv[1]))
GIB = 1024 ** 3


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))] if xs else None


print("gpu before (MiB used, total):", r["gpu_before"], " ram before GiB:", round(r["ram_before"] / GIB, 2))
print("rerankers before:", [(x["kind"], x["tree"], round(x["rss_kb"] / 1048576, 2)) for x in r["rerankers_before"]])
print("slot holders before:", r["slots"].strip().replace("\n", " | ")[:400])
for phase in ("baseline", "cold", "warm20", "warm10", "private", "stop"):
    ss = [s for s in r["samples"] if s["phase"] == phase]
    if not ss:
        continue
    gpu = [s["gpu_used_mib"] for s in ss]
    ram = [s["ram_used"] for s in ss]
    ours = [sum(x["rss_kb"] for x in s["rerankers"] if "W2-112" in x["tree"]) / 1048576 for s in ss]
    n = [len([x for x in s["rerankers"] if "W2-112" in x["tree"]]) for s in ss]
    print(f"{phase:9s} samples {len(ss):4d} | GPU used MiB peak {max(gpu)} mean {int(statistics.mean(gpu))} "
          f"| RAM used GiB peak {max(ram) / GIB:.2f} | our reranker RSS GiB peak {max(ours):.2f} "
          f"| our reranker processes max {max(n)}")
for phase in ("cold", "warm20", "warm10"):
    ss = r[phase]["sessions"]
    walls = [s["wall_s"] for s in ss if "wall_s" in s]
    bys = {}
    for s in ss:
        o = s.get("outcome") or {}
        key = (o.get("by"), o.get("device"), o.get("reason"))
        bys[key] = bys.get(key, 0) + 1
    print(f"{phase}: n={len(ss)} errors={sum('error' in s for s in ss)} wall p50 {pct(walls, 50):.3f}s "
          f"p95 {pct(walls, 95):.3f}s max {max(walls):.3f}s | phase wall {r[phase]['wall_s']:.2f}s | outcomes {bys}")
    for s in ss:
        if "error" in s:
            print("  error:", s["error"][-300:])
priv = r["private"]
print("private:", priv.get("mode"), "device", priv.get("device"), "load_s", round(priv.get("load_s", 0), 2),
      priv.get("error", "")[-300:] if "error" in priv else "")
service = {s["id"]: s for s in r["warm20"]["sessions"] if "id" in s}
worst, order_same, compared = 0.0, 0, 0
for row in priv.get("rows", []):
    s = service.get(row["id"])
    if not s or row["scores"] is None or None in s["scores"]:
        continue
    compared += 1
    worst = max(worst, max(abs(a - b) for a, b in zip(row["scores"], s["scores"])))
    private_order = [i for _, i in sorted(((-v, i) for i, v in enumerate(row["scores"])))]
    order_same += private_order == s["order"]
print(f"same answers: {compared} questions compared, order identical in {order_same}, max |score diff| {worst:.3g}")
print("private per-question s p50:", round(pct([x["s"] for x in priv.get("rows", [])], 50) or 0, 3))
print("stopped:", {k: v for k, v in r["stopped"].items() if k != "compute_apps_after"})
print("compute apps with service:", r["compute_apps_service"].strip().replace("\n", " | "))
print("compute apps after stop:", r["stopped"]["compute_apps_after"].strip().replace("\n", " | "))
