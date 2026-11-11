#!/usr/bin/env python3
"""ACT-MEMORY-AUDIT-INSTALL-1's rehearsal check (the same script as ACT-W2-149-INSTALL-1's, unchanged otherwise): for each brief line of a list, the launch script's own two stage-10 checks
at a commit, as build_and_run makes them (indep_launch.py: the approval line, then the front matter), by its own code.

    python3 install_check.py <tree> <list file> <commit>

Prints one line per brief line: the kind, the path, whether the bytes at the commit and the APPROVED line agree (the
"approved" check), and whether the front matter passes (kind, sample, model, result_schema, each from the front matter,
else the template's `briefs:` entry its `brief:` id names, else (model only) the kind's model in kinds.yaml, as W2-149's
set-up A wiring reads them (S22); budget and timeout within the kind's), naming each key that fails and where each
value came from. The dry launches are the script's own check; this one says why. Prints names and counts only.
"""
import importlib.util
import os
import subprocess
import sys

import yaml

tree, listfile, commit = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("indep_launch_rehearsal",
                                              os.path.join(tree, "governance/project/orchestration/tools/indep_launch.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
data = open(listfile, "rb").read()
t_lines, b_lines = m.parse_approved(data)
kinds_bytes = subprocess.run(["git", "-C", tree, "show", f"{commit}:governance/project/indep-walls/kinds.yaml"],
                             capture_output=True, check=True).stdout
kinds = m.load_kinds(kinds_bytes)
entries = (yaml.safe_load(kinds_bytes.decode("utf-8")) or {}).get("briefs") or {}
print(f"list: {len(t_lines)} template lines, {len(b_lines)} brief lines")
ok_lines = 0
for h, kind, path in b_lines:
    p = m.norm_repo_path(path)
    blob = m.blob(tree, commit, p) if p else None
    approved = blob is not None and m.sha_bytes(blob) == h and any(
        hh == h and k == kind and m.norm_repo_path(pp) == p for hh, k, pp in b_lines)
    if kind not in m.KINDS:
        print(f"  {kind:9} {path}: approved line {'ok' if approved else 'NO'}; not a launch kind (the script refuses "
              f"--kind {kind} with 17): a record only")
        ok_lines += approved
        continue
    fm = m.front_matter(blob) if blob is not None else None
    fails = []
    if fm is None:
        fails.append("no front matter")
    else:
        spec_k = kinds.get(kind, {})
        entry = entries.get(fm.get("brief")) if isinstance(fm.get("brief"), str) else None
        if entry is not None and entry.get("kind") != kind:
            fails.append("entry kind")
            entry = None
        if kind == "labeller" and entry is None:
            fails.append("labeller without an entry")
        got, src = {}, {}
        for key in ("model", "result_schema", "sample"):
            if key in fm:
                got[key], src[key] = fm[key], "front matter"
            elif entry is not None and key in entry:
                got[key], src[key] = entry[key], "entry"
            elif key == "model" and "model" in spec_k:
                got[key], src[key] = spec_k["model"], "kind"
            else:
                got[key], src[key] = None, "nowhere"
        if fm.get("kind") != kind:
            fails.append("kind")
        if not m.is_count(got["sample"]):
            fails.append("sample")
        if not m.full(m.MODEL_RX, got["model"]):
            fails.append("model")
        if not m.full(m.SCHEMA_NAME_RX, got["result_schema"]):
            fails.append("result_schema")
        b = fm.get("budget_usd", spec_k.get("budget_usd"))
        if not (m.is_number(b) and 0 < b <= spec_k.get("budget_usd", 0)):
            fails.append("budget_usd")
        ts = fm.get("timeout_s", spec_k.get("timeout_s"))
        if not (m.is_number(ts) and 0 < ts <= spec_k.get("timeout_s", 0)):
            fails.append("timeout_s")
    where = "" if fm is None else " (" + ", ".join(f"{k} {got[k]!r} from {src[k]}" for k in ("model", "result_schema", "sample")) + ")"
    print(f"  {kind:9} {path}: approved line {'ok' if approved else 'NO'}; front matter "
          + ("ok" if not fails else "refused (10 front_matter): " + ", ".join(fails)) + where)
    ok_lines += approved
print(f"approved lines that match their bytes at the commit: {ok_lines} of {len(b_lines)}")
