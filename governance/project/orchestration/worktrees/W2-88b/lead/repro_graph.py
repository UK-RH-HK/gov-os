"""Reproduce the code tool's edges query on a clone (the copy), printing the tool's error text and row counts only.
Usage: python3 repro_graph.py <clone root> <max_rows>"""
import json
import subprocess
import sys
from pathlib import Path

from gov import codeintel

root, rows = Path(sys.argv[1]), int(sys.argv[2])
for query in ("MATCH (n) RETURN count(n)", "MATCH (a)-[r]->(b) RETURN count(r)",
              "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name"):
    args = {"project": codeintel.PROJECT, "format": "json", "query": query, "max_rows": rows,
            "max_output_tokens": codeintel._BUDGET, "offset": 0}
    done = subprocess.run([codeintel.TOOL, "cli", "--quiet", "--json", "query_graph", json.dumps(args)],
                          capture_output=True, text=True, stdin=subprocess.DEVNULL, env=codeintel._env(root, "query_graph"))
    try:
        env = json.loads(done.stdout)
        text = env["content"][0]["text"]
        if env.get("isError"):
            print(query[:40], "ERROR:", text[:600])
        else:
            body = json.loads(text)
            print(query[:40], "ok rows", len(body.get("rows", [])), "has_more", body.get("has_more"),
                  body["rows"][:1] if "count" in query else "")
    except Exception as exc:  # noqa: BLE001
        print(query[:40], "unparsed rc", done.returncode, type(exc).__name__, done.stdout[:300], done.stderr[:300])
