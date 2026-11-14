import json, sys
D = "/home/usain/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/ad44f5fe-276d-46b7-85cd-df9f8d97a3ec/subagents/"
for name in ("agent-abeeaeb52fe9d7a0a.jsonl", "agent-a52efa638bd5e5784.jsonl"):
    first = last = None
    hits = []
    for line in open(D + name):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        ts = o.get("timestamp")
        if ts:
            first = first or ts
            last = ts
        s = line
        for needle in ("Verdict: READY to commit a1, a2 and b1", "Verdict: READY to commit f1, f2, f3 and f5"):
            if needle in s:
                hits.append((needle[:40], ts, o.get("type")))
    print(name, "first", first, "last", last)
    for h in hits[:6]:
        print("  ", h)
