"""Lead's probe of F-1, part 2: does the tool's Cypher take SKIP/LIMIT under its 100k-row cap, and the edge count."""
import sys
from pathlib import Path

from gov import codeintel as ci

root = Path(sys.argv[1]).resolve()
E = "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name"
with ci._Session(root) as s:
    for q in ("MATCH (a)-[r]->(b) RETURN count(r)",
              E + " LIMIT 50000",
              E + " SKIP 50000 LIMIT 50000",
              E + " SKIP 100000 LIMIT 50000"):
        try:
            page = s.tool("query_graph", project=ci.PROJECT, format="json", query=q, max_rows=500000,
                          max_output_tokens=10**9, offset=0)
            rows = page.get("rows") or []
            print("OK", q, "rows", len(rows), "first", rows[:1], "has_more", page.get("has_more"), flush=True)
        except Exception as exc:
            print("FAIL", q, exc, flush=True)
