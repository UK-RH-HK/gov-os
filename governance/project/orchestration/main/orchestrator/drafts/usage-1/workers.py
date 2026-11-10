#!/usr/bin/env python3
"""USAGE-1: the launched workers' own result JSONs (launch_worker.sh: <tree>/.gov-runtime/scratch/lead/log/<name>.json)
and any other `claude -p --output-format json` result files since the reset in the named folders.
Reads only: session_id, total_cost_usd, usage, modelUsage, num_turns, duration_ms; the file's name and mtime.

    python3 -I workers.py     writes results.json beside this file
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESET_TS = datetime(2026, 11, 8, 9, 0, tzinfo=timezone.utc).timestamp()
SKIP = "gov-os-" + "eval"
HOME = Path.home()
ROOTS = [HOME / "gov-os-worktrees", HOME / "gov-os-runs", HOME / "gov-os-operator" / "log",
         HOME / "Dynamic-Agentic-Engineering-OS" / ".gov-runtime" / "scratch"]


def results_in(path):
    out = []
    try:
        if path.stat().st_size > 30_000_000:
            return out
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    if '"total_cost_usd"' not in text:
        return out
    cands = []
    try:
        cands.append(json.loads(text))
    except ValueError:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("{") and '"total_cost_usd"' in line:
                try:
                    cands.append(json.loads(line))
                except ValueError:
                    pass
    flat = []
    for c in cands:
        flat.extend(c if isinstance(c, list) else [c])
    for d in flat:
        if isinstance(d, dict) and d.get("type") == "result" and "total_cost_usd" in d:
            out.append(dict(session_id=d.get("session_id"), cost=d.get("total_cost_usd"), turns=d.get("num_turns"),
                            duration_ms=d.get("duration_ms"), usage={k: (d.get("usage") or {}).get(k) for k in (
                                "input_tokens", "output_tokens", "cache_read_input_tokens",
                                "cache_creation_input_tokens")},
                            models={m: {k: v.get(k) for k in ("inputTokens", "outputTokens", "cacheReadInputTokens",
                                                              "cacheCreationInputTokens", "costUSD")}
                                    for m, v in (d.get("modelUsage") or {}).items()}))
    return out


def main():
    rows = []
    for root in ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            if SKIP in dirpath:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".venv", "venv", "__pycache__")
                           and SKIP not in d]
            for fn in filenames:
                if not (fn.endswith(".json") or fn.endswith(".jsonl") or fn.endswith(".out") or fn.endswith(".log")):
                    continue
                p = Path(dirpath) / fn
                try:
                    if p.stat().st_mtime < RESET_TS:
                        continue
                except OSError:
                    continue
                for r in results_in(p):
                    r["file"] = str(p)
                    r["mtime"] = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()[:16]
                    rows.append(r)
    (HERE / "results.json").write_text(json.dumps(rows, indent=0))
    print(len(rows), "result records; $%.2f" % sum(r["cost"] or 0 for r in rows))


if __name__ == "__main__":
    main()
