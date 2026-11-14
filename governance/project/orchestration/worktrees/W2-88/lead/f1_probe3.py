"""Lead's probe for package 2 (run 8): on the redis copy's code index, the edge counts by type, the node count, and
whether the tool's Cypher takes a typed match and SKIP/LIMIT under its 100k-row cap."""
import sys
import time
from pathlib import Path

from gov import codeintel as ci

root = Path(sys.argv[1]).resolve()
E = "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name"


def ask(s, q):
    t = time.time()
    try:
        page = s.tool("query_graph", project=ci.PROJECT, format="json", query=q, max_rows=500000,
                      max_output_tokens=10**9, offset=0)
        rows = page.get("rows") or []
        print("OK %.1fs" % (time.time() - t), q, "rows", len(rows), "first", rows[:3] if "count" in q else rows[:1],
              "has_more", page.get("has_more"), flush=True)
        return rows
    except Exception as exc:
        print("FAIL %.1fs" % (time.time() - t), q, str(exc)[:300], flush=True)
        return None


with ci._Session(root) as s:
    ask(s, "MATCH (n) RETURN count(n)")
    ask(s, "MATCH (a)-[r]->(b) RETURN count(r)")
    by_type = ask(s, "MATCH (a)-[r]->(b) RETURN type(r), count(r)")
    ask(s, "MATCH (n) RETURN n.label, count(n)")
    ask(s, E + " LIMIT 50000")
    ask(s, E + " SKIP 50000 LIMIT 50000")
    ask(s, E + " SKIP 100000 LIMIT 50000")
    for row in by_type or []:
        kind = row[0]
        ask(s, f"MATCH (a)-[r:{kind}]->(b) RETURN a.qualified_name, type(r), b.qualified_name")
