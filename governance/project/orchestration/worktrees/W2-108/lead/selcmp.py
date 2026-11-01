"""Compare two selections. usage: selcmp.py <a.json> <b.json>"""
import json
import sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])
print("scope", b["scope"], "| core_changed", b["core_changed"], "| unplaced", b["unplaced"], "| why_full", b["why_full"],
      "| head", b["head"][:12], "| governance_left_out", b["governance_left_out"])
print("same targets:", [s["target"] for s in a["selected"]] == [s["target"] for s in b["selected"]],
      "| same options:", a["pytest_options"] == b["pytest_options"], "| targets", len(b["selected"]),
      "| options", len(b["pytest_options"]), "| per_test_timeout", b.get("per_test_timeout"))
