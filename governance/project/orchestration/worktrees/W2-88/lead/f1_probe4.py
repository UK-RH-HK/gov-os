"""Lead's probe for package 2 (run 8), part 2: a label-filtered node read and its count against the label count."""
import sys
from pathlib import Path
from gov import codeintel as ci
root = Path(sys.argv[1]).resolve()
with ci._Session(root) as s:
    labels = s.tool("query_graph", project=ci.PROJECT, format="json", query="MATCH (n) RETURN n.label, count(n)", max_rows=1000, max_output_tokens=10**9, offset=0)["rows"]
    total = 0
    for label, count in labels:
        rows = s.tool("query_graph", project=ci.PROJECT, format="json", query=f"MATCH (n:{label}) RETURN n.qualified_name, n.name, n.label, n.file_path", max_rows=500000, max_output_tokens=10**9, offset=0)
        total += len(rows["rows"])
        print(label, count, len(rows["rows"]), rows.get("has_more"), flush=True)
    print("total", total)
