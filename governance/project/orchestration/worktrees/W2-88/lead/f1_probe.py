"""Lead's probe of F-1: ask the redis copy's code index the two _graph queries and print what the tool answers."""
import json
import sys
from pathlib import Path

from gov import codeintel as ci

root = Path(sys.argv[1]).resolve()
s = ci._Session(root)
orig_ask = s._ask


def ask(method, **params):
    r = orig_ask(method, **params)
    if method == "tools/call":
        env = r
        txt = (env.get("content") or [{}])[0].get("text", "")
        print("CALL", params.get("arguments", {}).get("query"), params.get("arguments", {}).get("offset"),
              "isError=", env.get("isError"), "len=", len(txt), "head=", txt[:400].replace("\n", " "), flush=True)
    return r


s._ask = ask
with s:
    for q in ("MATCH (n) RETURN n.qualified_name, n.name, n.label, n.file_path",
              "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name"):
        try:
            rows = ci._rows(s, q)
            print("OK", q, len(rows), flush=True)
        except Exception as exc:
            print("FAIL", q, type(exc).__name__, exc, flush=True)
            break
