"""ACT-GUARD-FIX-6: judge a list of calls by two hooks (the live one and the after copy), as Claude Code runs them.

  import pairs
  rows = pairs.run(items, before_dir, after_dir, workers=6)
  item: {"id", "tool", "input", "cwd", "role", "ticket", "project", "tmpdir"(optional), "agent_type"(optional)}
  row:  item's id, role, tool, then b / a = [decision, rule]  (decision allow | deny | ask | error)

classify(row) -> "same" | "stricter" | "looser" | "error-changed": by the order allow < ask < deny; error counts as deny
for the order and is named when it changes."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hookrun  # noqa: E402

ORDER = {"allow": 0, "ask": 1, "deny": 2, "error": 2}


def one(args):
    item, before, after = args
    out = {"id": item["id"], "role": item["role"], "tool": item["tool"]}
    for key, hooks in (("b", before), ("a", after)):
        d, rule, why = hookrun.decide(hooks, item["project"], item["role"], item["ticket"], item["tool"],
                                      item["input"], cwd=item.get("cwd"), agent_type=item.get("agent_type"),
                                      tmpdir=item.get("tmpdir"))
        out[key] = [d, rule]
        out[key + "_why"] = why[:240]
    return out


def run(items, before, after, workers=6):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, [(i, before, after) for i in items]))


def classify(row):
    b, a = row["b"][0], row["a"][0]
    if b == a:
        return "same"
    if b == "error" and a != "error" or a == "error":
        return "error-changed"
    return "stricter" if ORDER[a] > ORDER[b] else "looser"
