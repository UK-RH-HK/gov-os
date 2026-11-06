#!/usr/bin/env python3
"""The live window's eligibility lines (D4B-SCORE-ONCE §4), per cell, from the files the window leaves; run by the
window's trap on every exit path, so a cell whose folder exists is judged even when the window stops later.

    live_verdict.py OUT BUDGET SERVICE_LOG_ONE SERVICE_LOG_TWO CELL ...

Per cell folder OUT/CELL:
- **speed (judged):** ``alone/summary-alone.json``: the full median of a whole search (the harness's GPU reads
  included, as in the earlier windows) at most 3.0 s, and none failed or unranked; ``median_less_gpu_reads_s`` is
  printed beside it, reported only;
- **10 at once (judged):** ``once/summary-once.json``: no request timed out (30 s), none failed or unranked;
- **probe (judged):** ``probe-one.rc`` and ``probe-two.rc`` both 0;
- **GPU (judged):** ``gpu.txt``, the 1 Hz samples from after the warm-up to the end of the 10 at once: none at or
  above BUDGET. Reported only: ``gpu-load.txt``'s peak (from the first load to the warm-up), the readings
  ``gpu-after-loads-raw.txt`` and ``gpu-after-warmup.txt``, and a derived bound: the GPU after the warm-up plus, for
  each service, its largest (peak reserved - reserved after) over its requests in this cell (the trial worker's
  request lines, from line ``service-<k>.from`` to ``service-<k>.to`` of its service log; no ``.to``: to the end).
A measure whose file is missing is "not measured" and its line is not met. Writes ``verdict.json`` per cell."""
import json
import sys
from pathlib import Path


def load(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def number(p: Path):
    try:
        return int(p.read_text().split()[0])
    except (OSError, ValueError, IndexError):
        return None


def samples(p: Path) -> list[int]:
    try:
        return [int(x) for x in p.read_text().split() if x.isdigit()]
    except OSError:
        return []


def service_rows(d: Path, k: str, log: Path) -> list[dict]:
    start = number(d / f"service-{k}.from")
    if start is None:
        return []
    end = number(d / f"service-{k}.to")
    try:
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    rows = []
    for line in lines[start:end]:
        if line.startswith('{"trial": "request"'):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return rows


def judge(out: Path, budget: int, logs: dict, cell: str) -> dict:
    d = out / cell
    alone, once = load(d / "alone/summary-alone.json"), load(d / "once/summary-once.json")
    probes = {k: (d / f"probe-{k}.rc").read_text().strip() if (d / f"probe-{k}.rc").exists() else None
              for k in ("one", "two")}
    judged, loaded = samples(d / "gpu.txt"), samples(d / "gpu-load.txt")
    raw, warm = number(d / "gpu-after-loads-raw.txt"), number(d / "gpu-after-warmup.txt")
    over = sum(1 for x in judged if x >= budget)
    svc = {}
    for k in ("one", "two"):
        rows = service_rows(d, k, logs[k])
        svc[k] = {"requests": len(rows),
                  "peak_reserved_mib": max([r.get("peak_reserved_mib", 0) for r in rows] or [None], key=lambda x: x or 0),
                  "rise_mib": max([r.get("peak_reserved_mib", 0) - r.get("reserved_after_mib", 0) for r in rows] or [None],
                                  key=lambda x: x or 0),
                  "slowest_s": max([r.get("seconds", 0) for r in rows] or [None], key=lambda x: x or 0)}
    bound = (warm + svc["one"]["rise_mib"] + svc["two"]["rise_mib"]
             if warm is not None and svc["one"]["rise_mib"] is not None and svc["two"]["rise_mib"] is not None else None)
    lines = [
        ("median search alone at most 3.0 s, none failed or unranked",
         alone is not None and alone["median_s"] <= 3.0 and alone["failed"] == 0 and alone["unranked"] == 0,
         (f"median {alone['median_s']:.2f} s (the harness's GPU reads included), p90 {alone['p90_s']:.2f} s, failed "
          f"{alone['failed']}, unranked {alone['unranked']}; reported only: less the GPU reads "
          f"{alone['median_less_gpu_reads_s']:.2f} s") if alone else "not measured"),
        ("no request timed out at 10 at once (30 s), none failed or unranked",
         once is not None and once["timeouts"] == 0 and once["failed"] == 0 and once["unranked"] == 0,
         (f"median {once['median_s']:.2f} s, slowest {once['slowest_s']:.2f} s, timed out {once['timeouts']}, failed "
          f"{once['failed']}, unranked {once['unranked']}, slowest request {once['slowest_request_s']:.2f} s")
         if once else "not measured"),
        ("no probe shape at the budget", probes["one"] == "0" and probes["two"] == "0",
         f"probe exits: one {probes['one']}, two {probes['two']}"),
        (f"the GPU never at or above {budget} MiB (judged: after the warm-up to the end of the 10 at once)",
         bool(judged) and over == 0,
         (f"peak {max(judged)} MiB, {over} of {len(judged)} samples at or above" if judged else "not measured")
         + f"; reported only: load peak {max(loaded) if loaded else None} MiB, after the loads (raw) {raw}, after the "
           f"warm-up {warm}, derived bound {warm} + {svc['one']['rise_mib']} + {svc['two']['rise_mib']} = {bound} MiB"),
    ]
    eligible = all(ok for _, ok, _ in lines)
    result = {"cell": cell, "eligible": eligible, "lines": [[w, ok, x] for w, ok, x in lines],
              "gpu": {"judged_peak": max(judged) if judged else None, "judged_over": over, "judged_samples": len(judged),
                      "load_peak": max(loaded) if loaded else None, "after_loads_raw": raw, "after_warmup": warm,
                      "derived_bound": bound},
              "services": svc}
    (d / "verdict.json").write_text(json.dumps(result, indent=1))
    for what, ok, detail in lines:
        print(f"{cell} {'MET    ' if ok else 'NOT MET'} {what}: {detail}")
    print(f"{cell}: {'ELIGIBLE' if eligible else 'NOT ELIGIBLE'}")
    return result


def main(argv):
    out, budget = Path(argv[1]), int(argv[2])
    logs = {"one": Path(argv[3]), "two": Path(argv[4])}
    judged = 0
    for cell in argv[5:]:
        if (out / cell).is_dir():
            judge(out, budget, logs, cell)
            judged += 1
        else:
            print(f"{cell}: not started, not judged")
    return 0 if judged else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
