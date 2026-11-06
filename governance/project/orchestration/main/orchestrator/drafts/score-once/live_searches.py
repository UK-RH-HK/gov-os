#!/usr/bin/env python3
"""The live window's searches (D4B-SCORE-ONCE §4): the first calls of the first N visible memory-retrieval questions,
each a whole search through the score-once harness (rx.py retrieve) with a fresh cache of its own, so every search
routes, embeds and reranks as it would run. The live switches (GOV_RX_RERANK_DIR, ..._DIR2, GOV_RX_LIVE_RULE, the
bounds, GOV_RX_GPU_LIMIT_MIB) come from the caller's environment.

    live_searches.py alone N --clone C --rx RX --variant JSON --out DIR [--questions DIR] [--timeout S]
    live_searches.py once  N ...

``alone``: one search at a time; the median and the p90 (nearest rank) seconds of a whole search. ``once``: N started
together; the median, the slowest, any failed, timed out or unranked. A first call is the measure's (gov.retrieval
.measure ``_ask``): the question's --ticket, --id and --radius, --batch-size 10, --bundle-budget 6000, --json.
Kept per search: its exit code, seconds, ``rerank.by``, the number of items, and its rx log (LIVE lines: counts and
seconds only). No question text and no bundle is written; only the questions' file names. Prints one line per search
and the summary; writes ``summary-<mode>.json``. Visible questions only: a path under gov-os-eval, or naming a hidden
or memory-verdict folder, is refused."""
import json
import math
import os
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TIMEOUT_REQ_S = float(os.environ.get("GOV_RERANK_TIMEOUT_S", "30"))  # the product's answer timeout, for the report


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def visible_only(folder: Path) -> None:
    parts = [p.lower() for p in folder.resolve().parts]
    if "gov-os-eval" in parts or any("hidden" in p or "memory-verdict" in p for p in parts):
        sys.exit(f"live_searches: {folder} is not a visible questions folder: refused (the hidden-half rule)")


def first_calls(folder: Path, n: int) -> list[tuple[str, list[str]]]:
    """(file name, the first call's arguments after ``retrieve``) of the first n questions, sorted by file name."""
    import yaml
    files = sorted(folder.glob("*.yaml"))[:n]
    if len(files) < n:
        sys.exit(f"live_searches: {len(files)} questions in {folder}, {n} asked")
    out = []
    for f in files:
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        opts = [*(["--ticket", str(data["ticket"])] if data.get("ticket") else []),
                *[w for i in (data.get("ids") or []) for w in ("--id", str(i))],
                *(["--radius", str(data["radius"])] if data.get("radius") is not None else []),
                "--batch-size", "10", "--bundle-budget", "6000"]
        out.append((f.name, [*opts, str(data["question"]), "--json"]))
    return out


def rx_log(path: Path) -> dict:
    """A search's LIVE figures from its rx log: request seconds per service, the GPU reads, failures, timeouts."""
    got = {"one_s": 0.0, "two_s": 0.0, "requests": 0, "gpu_s": 0.0, "fails": 0, "timeouts": 0, "slowest_req_s": 0.0}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return got
    for line in lines:
        f = line.split("\t")
        if f[0] == "LIVE" and len(f) >= 3:
            got[f"{f[1]}_s"] = got.get(f"{f[1]}_s", 0.0) + float(f[2])
            got["requests"] += 1
            got["slowest_req_s"] = max(got["slowest_req_s"], float(f[2]))
        elif f[0] == "LIVEGPU" and len(f) >= 3:
            got["gpu_s"] += float(f[2])
        elif f[0] == "LIVEFAIL":
            got["fails"] += 1
            got["timeouts"] += len(f) >= 3 and f[2].startswith(("TimeoutError", "timeout"))
    return got


def one_search(i: int, name: str, args: list[str], o: dict) -> dict:
    cache, log = o["out"] / f"c-{o['mode']}-{i:02d}", o["out"] / f"rx-{o['mode']}-{i:02d}.log"
    if cache.exists():
        sys.exit(f"live_searches: {cache} exists: every search has a fresh cache")
    env = {k: v for k, v in os.environ.items() if k != "GOV_TICKET"}
    env.update({"GOV_ROLE": "orchestrator", "GOV_RX": o["variant"], "GOV_RX_CACHE": str(cache),
                "GOV_RX_LOG": str(log), "PYTHONPATH": str(o["clone"] / "src")})
    started = time.monotonic()
    try:
        done = subprocess.run([sys.executable, str(o["rx"]), "retrieve", *args], cwd=o["clone"], env=env,
                              capture_output=True, text=True, timeout=o["timeout"])
        rc, out, err = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", f"killed after {o['timeout']} s"
    seconds = time.monotonic() - started
    by, items = None, None
    try:
        doc = json.loads(out)
        bundle = doc["result"] if isinstance(doc.get("result"), dict) else doc
        by, items = (bundle.get("rerank") or {}).get("by"), len(bundle["evidence"])
    except (ValueError, KeyError, TypeError, AttributeError):
        pass
    if rc != 0:
        (o["out"] / f"err-{o['mode']}-{i:02d}.txt").write_text(err[-600:], encoding="utf-8")
    return {"i": i, "file": name, "rc": rc, "seconds": round(seconds, 3), "by": by, "items": items, **rx_log(log)}


def nearest(values: list[float], q: float) -> float:
    s = sorted(values)
    return s[max(0, math.ceil(q * len(s)) - 1)]


def main(argv):
    if len(argv) < 3 or argv[1] not in ("alone", "once"):
        print(__doc__)
        return 2
    mode, n = argv[1], int(argv[2])
    clone = Path(arg(argv, "--clone"))
    o = {"mode": mode, "clone": clone, "rx": Path(arg(argv, "--rx")), "variant": arg(argv, "--variant"),
         "out": Path(arg(argv, "--out")), "timeout": float(arg(argv, "--timeout", "300"))}
    json.loads(o["variant"])
    folder = Path(arg(argv, "--questions", str(clone / "fixtures/evaluation/memory-retrieval/visible")))
    visible_only(folder)
    calls = first_calls(folder, n)
    o["out"].mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    if mode == "alone":
        rows = [one_search(i, name, a, o) for i, (name, a) in enumerate(calls)]
    else:
        with ThreadPoolExecutor(n) as pool:
            rows = list(pool.map(lambda p: one_search(p[0], p[1][0], p[1][1], o), enumerate(calls)))
    wall = time.monotonic() - t0
    for r in rows:
        print(f"{mode} {r['i']:02d} {r['file']}: exit {r['rc']}, {r['seconds']:.2f} s, rerank.by {r['by']}, "
              f"{r['items']} items; requests {r['requests']} (one {r['one_s']:.2f} s, two {r['two_s']:.2f} s, "
              f"slowest {r['slowest_req_s']:.2f} s); GPU reads {r['gpu_s']:.2f} s; live failures {r['fails']}")
    secs = [r["seconds"] for r in rows]
    failed = sum(1 for r in rows if r["rc"] != 0 or r["items"] is None)
    unranked = sum(1 for r in rows if r["rc"] == 0 and r["items"] is not None and r["by"] != "service")
    timeouts = sum(r["timeouts"] for r in rows)
    s = {"mode": mode, "n": n, "wall_s": round(wall, 3), "median_s": round(statistics.median(secs), 3),
         "p90_s": round(nearest(secs, 0.9), 3), "slowest_s": round(max(secs), 3), "failed": failed,
         "unranked": unranked, "timeouts": timeouts, "answer_timeout_s": TIMEOUT_REQ_S,
         "median_less_gpu_reads_s": round(statistics.median(r["seconds"] - r["gpu_s"] for r in rows), 3),
         "median_one_s": round(statistics.median(r["one_s"] for r in rows), 3),
         "median_two_s": round(statistics.median(r["two_s"] for r in rows), 3),
         "slowest_request_s": round(max(r["slowest_req_s"] for r in rows), 3), "rows": rows}
    (o["out"] / f"summary-{mode}.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    if mode == "alone":
        print(f"{n} searches alone: median {s['median_s']:.2f} s, p90 {s['p90_s']:.2f} s (nearest rank), slowest "
              f"{s['slowest_s']:.2f} s; failed {failed}, unranked {unranked}; median less the harness's GPU reads "
              f"{s['median_less_gpu_reads_s']:.2f} s; a search's reranking, median: one {s['median_one_s']:.2f} s, "
              f"two {s['median_two_s']:.2f} s")
    else:
        print(f"{n} at once: {wall:.1f} s in all; median {s['median_s']:.2f} s, slowest {s['slowest_s']:.2f} s; failed "
              f"{failed}, requests timed out (past {TIMEOUT_REQ_S:g} s) {timeouts}, unranked {unranked}; slowest "
              f"request {s['slowest_request_s']:.2f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
