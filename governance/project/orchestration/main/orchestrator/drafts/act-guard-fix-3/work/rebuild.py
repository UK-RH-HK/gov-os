import json, sys, os
L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl"
rows = [json.loads(l) for l in open(L) if l.strip()]
out = []
for i, r in enumerate(rows):
    rec = {"i": i, "rule": r.get("rule"), "verdict": r.get("verdict") or r.get("judgement"), "cwd": r.get("cwd"),
           "transcript": r.get("transcript"), "key": r.get("key"), "tool": r.get("tool"), "form": r.get("form")}
    if r.get("key") and r.get("transcript") and os.path.exists(r["transcript"]):
        found = None
        meta = {}
        for line in open(r["transcript"]):
            if r["key"] not in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            msg = ev.get("message") or {}
            for b in msg.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id") == r["key"]:
                    found = b
                    meta = {"cwd": ev.get("cwd"), "agent": ev.get("agentId"), "sidechain": ev.get("isSidechain")}
        if found:
            rec["tool"] = found.get("name")
            rec["input"] = found.get("input")
            rec["meta"] = meta
    out.append(rec)
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(sum(1 for o in out if o.get("input")), "recovered of", len(out))
print([o["i"] for o in out if not o.get("input")])
