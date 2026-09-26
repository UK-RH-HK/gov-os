#!/usr/bin/env python3
"""BR-AR-0016: structural check of REPAIR_DAG.yaml -- required node keys (IMPLEMENTATION_DAG format), every
dependency in an earlier parallel group, every mutation_scope inside the domain, no two nodes of one parallel group
with overlapping scopes, every node in exactly one group, and the brief's required coverage."""
import fnmatch
import sys

import yaml

d = yaml.safe_load(open(sys.argv[1]))
D = d["conventions"]["domain"]
KEYS = {"id", "title", "depends_on", "mutation_scope", "deliverables", "acceptance_checks", "routing", "size",
        "parallel_group"}
problems = []
nodes = {n["id"]: n for n in d["nodes"]}
order = {g: i for i, g in enumerate(d["parallel_groups"])}
for n in d["nodes"]:
    miss = KEYS - set(n)
    if miss:
        problems.append(f"{n['id']}: missing {sorted(miss)}")
    for c in n.get("acceptance_checks") or []:
        if not {"cmd", "expect"} <= set(c):
            problems.append(f"{n['id']}: acceptance check without cmd/expect")
    for s in n.get("mutation_scope") or []:
        if not s.startswith(D + "/"):
            problems.append(f"{n['id']}: scope outside domain {s}")
    for dep in n.get("depends_on") or []:
        if dep not in nodes:
            problems.append(f"{n['id']}: unknown dependency {dep}")
        elif order[nodes[dep]["parallel_group"]] >= order[n["parallel_group"]]:
            problems.append(f"{n['id']}: dependency {dep} is not in an earlier group")
    if n["id"] not in d["parallel_groups"].get(n["parallel_group"], []):
        problems.append(f"{n['id']}: not listed in its parallel group")
for g, members in d["parallel_groups"].items():
    for a in members:
        for b in members:
            if a < b:
                for x in nodes[a]["mutation_scope"]:
                    for y in nodes[b]["mutation_scope"]:
                        if x == y or fnmatch.fnmatch(x, y) or fnmatch.fnmatch(y, x):
                            problems.append(f"{g}: {a} and {b} both touch {x}")
text = open(sys.argv[1]).read()
required = ["facet", "parallel", "follow-up", "continuation", "batch", "stop", "merge", "provenance", "supplementary",
            "notes", "telemetry", "GD-1", "GD-2", "GD-3", "GD-4", "GD-5", "GD-6", "GD-7", "GD-8", "GD-9", "OBS-BR-07",
            "OBS-BR-08", "fresh test-author", "sealed", "OD-BR-05 s9", "unrelated"]
for r in required:
    if r.lower() not in text.lower():
        problems.append(f"coverage: '{r}' not found")
print(f"nodes={len(nodes)} groups={len(order)} problems={len(problems)}")
for p in problems:
    print(" -", p)
sys.exit(1 if problems else 0)
