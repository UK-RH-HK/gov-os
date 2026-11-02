"""Summarise a select_tests.py output: python3 sel_summary.py <select.json> [<older select.json>]."""
import json
import sys

new = json.load(open(sys.argv[1]))
targets = [s["target"] for s in new["selected"]]
opts = new["pytest_options"]
print("scope:", new["scope"], "core_changed:", new["core_changed"], "unplaced:", new["unplaced"])
print("targets:", len(targets), "options:", len(opts), "ignore:", sum(1 for o in opts if o.startswith("--ignore")),
      "deselect:", sum(1 for o in opts if o.startswith("--deselect")))
print("W1-26 selected:", any("W1-26" in t for t in targets))
print(" ".join(targets))
if len(sys.argv) > 2:
    old = json.load(open(sys.argv[2]))
    o = set(s["target"] for s in old["selected"])
    print("added vs old:", sorted(set(targets) - o))
    print("removed vs old:", sorted(o - set(targets)))
    print("options same:", old["pytest_options"] == opts)
