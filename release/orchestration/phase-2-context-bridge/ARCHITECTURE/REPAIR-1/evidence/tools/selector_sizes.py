#!/usr/bin/env python3
"""BR-AR-0016 (RC-1): for every mandatory input that declares a sub-selector in the bridge state (an entry range, a
key list, several paths), measure what the selector denotes versus what the run-1 packet rendered for it."""
import json
import os
import re
import subprocess

import yaml

DOM = "release/orchestration/phase-2-context-bridge"
root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
D = os.path.join(root, DOM)
state = yaml.safe_load(open(os.path.join(D, "ORCHESTRATOR_STATE.yaml")))
man = json.load(open(os.path.join(D, "DEMONSTRATION/run-1/packet/manifest.json")))
records_commit = man["view"][0]["commit"]
a_items = {i["unit"]["id"]: i for i in man["sections"]["A"]["items"]}
out = []
for d in state["mandatory_bridge_inputs"]["items"]:
    sel = {k: d[k] for k in ("entries", "keys") if k in d}
    if len(d.get("paths") or []) > 1:
        sel["paths"] = d["paths"]
    if not sel:
        continue
    it = a_items.get(d["id"], {})
    row = {"id": d["id"], "selector_kinds": sorted(sel), "rendered_bytes": it.get("bytes"),
           "resolved_path": (it.get("source") or {}).get("path"), "resolved_lines": [
               (it.get("source") or {}).get("line_start"), (it.get("source") or {}).get("line_end")]}
    commit = d.get("commit") or records_commit
    if "entries" in sel:
        m = re.findall(r"([A-Z0-9]+-[A-Z]-)(\d{4})", sel["entries"])
        prefix, lo, hi = m[0][0], int(m[0][1]), int(m[1][1])
        text = subprocess.run(["git", "show", f"{commit}:{d['path']}"], capture_output=True, text=True, cwd=root).stdout
        lines = text.split("\n")
        heads = [(i, int(x.group(1))) for i, l in enumerate(lines) for x in [re.match(r"^## " + re.escape(prefix) + r"(\d{4})", l)] if x]
        total = 0
        first_rendered_in_range = False
        for j, (i, n) in enumerate(heads):
            if lo <= n <= hi:
                end = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
                total += len("\n".join(lines[i:end]).encode())
        row["selected_bytes"] = total
        row["rendered_contains_selected_entries"] = any(lo <= n <= hi and i < 40 for i, n in heads)
    if "keys" in sel:
        text = subprocess.run(["git", "show", f"{commit}:{d['path']}"], capture_output=True, text=True, cwd=root).stdout
        doc = yaml.safe_load(text)
        row["selected_keys_present"] = sum(1 for k in sel["keys"] if k in doc)
        row["selected_keys"] = len(sel["keys"])
        row["selected_bytes_yaml_dump"] = sum(len(yaml.safe_dump({k: doc[k]}).encode()) for k in sel["keys"] if k in doc)
    if "paths" in sel:
        row["declared_paths"] = len(sel["paths"])
        row["resolved_paths"] = 1 if it else 0
    out.append(row)
print(json.dumps(out, indent=1, sort_keys=True))
