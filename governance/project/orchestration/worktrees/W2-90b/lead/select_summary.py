#!/usr/bin/env python3
"""Summarise select_tests.py's JSON: scope, core_changed, unplaced, targets and pytest_options."""
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
print("scope:", data.get("scope"), "| core_changed:", data.get("core_changed"), "| unplaced:", data.get("unplaced"))
print("targets:", [s["target"] for s in data.get("selected", [])])
print("keys:", sorted(data.keys()))
print("pytest_options:", json.dumps(data.get("pytest_options")))
