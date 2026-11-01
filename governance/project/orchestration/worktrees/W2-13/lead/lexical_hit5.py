"""The dev queryset's lexical-only hit@5 (W2-13 KPI success 2 evidence), with whatever gov PYTHONPATH gives.

Clones each dev tier (GOV_DEV_TIERS, by name; default ~/gov-os-workbench/synthetic) into a temporary folder under
TMPDIR, adopts it as retrieve_check does, refreshes the lexical index only, and asks each dev query of the lexical
route alone. hit@5: a must_cite path among the first five distinct paths of the lexical hits, in the route's order;
the figure is the mean over classes, as retrieve_check computes it. Prints ids, counts and figures only.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

import gov
from gov.retrieval import lexical
from gov.retrieval.retrieve_check import _adopt
from gov.util.gitenv import git_env

PROJECT = Path(sys.argv[1])
TIERS = {"A": "a-dev", "B": "b-dev"}


def main() -> int:
    dev = Path(os.environ.get("GOV_DEV_TIERS", "~/gov-os-workbench/synthetic")).expanduser()
    queries = yaml.safe_load((dev / "dev-queryset.yaml").read_text(encoding="utf-8"))["queries"]
    out = {"gov_file": gov.__file__, "queries": len(queries)}
    with tempfile.TemporaryDirectory() as tmp:
        roots = {}
        for programme, name in TIERS.items():
            dest = Path(tmp) / name
            subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(dev / name), str(dest)], check=True,
                           capture_output=True, env=git_env(None, pinned=True))
            _adopt(dest, PROJECT)
            git = ["git", "-C", str(dest), "-c", "user.name=check", "-c", "user.email=check@check"]
            subprocess.run([*git, "add", "-A"], check=True, capture_output=True, env=git_env(dest, pinned=True))
            subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "adopted"], check=True, capture_output=True,
                           env=git_env(dest, pinned=True))
            lexical.refresh(dest)
            roots[programme] = dest
        scored, exact_scored, rows, seconds = {}, {}, [], []
        for entry in queries:
            root = roots.get(entry.get("programme", ""))
            if root is None:
                continue
            gold = entry.get("gold", {}).get("must_cite", [])
            started = time.perf_counter()
            try:
                answer = lexical.search(root, entry.get("query", ""), refresh=False)
                error = None
            except Exception as exc:  # counted as a miss, and named
                answer, error = {"available": False, "hits": []}, type(exc).__name__
            seconds.append(time.perf_counter() - started)
            # the list the lexical route hands the fusion: ``ranked`` where the code has one, else ``hits``
            route = answer.get("ranked", answer.get("hits", []))
            cited = list(dict.fromkeys(hit["path"] for hit in route))[:5]
            exact = list(dict.fromkeys(hit["path"] for hit in answer.get("hits", [])))[:5]
            hit = any(path in cited for path in gold)
            scored.setdefault(entry.get("class", "default"), []).append(hit)
            exact_scored.setdefault(entry.get("class", "default"), []).append(any(path in exact for path in gold))
            rows.append({"id": entry.get("id"), "class": entry.get("class"), "hit": hit,
                         "available": answer.get("available"), "hits": len(answer.get("hits", [])),
                         "ranked": len(answer.get("ranked", [])), "raised": error})
    per_class = {name: 100.0 * sum(hits) / len(hits) for name, hits in scored.items()}
    out["per_class"] = per_class
    out["hit_at_5"] = sum(per_class.values()) / len(per_class) if per_class else None
    exact_class = {name: 100.0 * sum(hits) / len(hits) for name, hits in exact_scored.items()}
    out["exact_hits_hit_at_5"] = sum(exact_class.values()) / len(exact_class) if exact_class else None
    out["hits"] = sum(row["hit"] for row in rows)
    out["asked"] = len(rows)
    out["raised"] = sum(1 for row in rows if row["raised"])
    seconds.sort()
    out["p95_s"] = seconds[max(0, int(round(0.95 * len(seconds))) - 1)] if seconds else None
    out["rows"] = rows
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
