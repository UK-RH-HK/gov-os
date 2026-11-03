"""Rebuild every logged refusal's full call from its transcript (as ACT-GUARD-FIX-3's rebuild.py and W2-42a's
fixture do: the tool_use id in the row's key), with the session's role. Rows 0-60 take the role and TMPDIR found by
ACT-GUARD-FIX-3 (its work/corpus.json); later rows: the role from the launch folder (gov-launch-<role>-<id>) the
transcript names, else orchestrator (the CTO, a lead or the CTO's subagent). Usage: rebuild4.py <out.json>"""
import json
import os
import re
import sys

L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl"
OLD = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-3/work/corpus.json"
LAUNCH = re.compile(r"/tmp/gov-launch-([a-z-]+?)-([a-z0-9]{8})")

rows = [json.loads(line) for line in open(L) if line.strip()]
old = {o["i"]: o for o in json.load(open(OLD))}
out = []
for i, r in enumerate(rows):
    rec = {"i": i, "rule": r.get("rule"), "verdict": r.get("verdict") or r.get("judgement"), "cwd": r.get("cwd"),
           "transcript": r.get("transcript"), "key": r.get("key"), "tool": r.get("tool"), "form": r.get("form"),
           "note": r.get("note")}
    if i in old and old[i].get("input") is not None and old[i].get("key") == r.get("key"):
        for k in ("tool", "input", "meta", "launch_role", "tmpdir", "agent_type"):
            if k in old[i]:
                rec[k] = old[i][k]
        rec["from"] = "fix-3 corpus"
        out.append(rec)
        continue
    t = r.get("transcript")
    if r.get("key") and t and os.path.exists(t):
        roles = {}
        for line in open(t):
            for m in LAUNCH.finditer(line):
                roles[m.group(0)] = m.group(1)
            if r["key"] not in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id") == r["key"]:
                    rec["tool"] = b.get("name")
                    rec["input"] = b.get("input")
                    rec["meta"] = {"cwd": ev.get("cwd"), "agent": ev.get("agentId")}
                    rec["cwd"] = ev.get("cwd") or rec["cwd"]
        # the session's own launch folder: the one named most in its transcript
        if roles and "/subagents/" not in t:
            names = list(roles.items())
            rec["launch_role"] = names[0][1]
            rec["launch_dirs"] = sorted(set(roles.values()))
        rec["from"] = "transcript"
    out.append(rec)
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(sum(1 for o in out if o.get("input") is not None), "recovered of", len(out))
print("not recovered:", [o["i"] for o in out if o.get("input") is None])
for o in out[61:]:
    print(o["i"], o.get("launch_role"), (o.get("cwd") or "")[-40:], "|", (o.get("note") or "")[:90])
