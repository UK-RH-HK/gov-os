"""MODEL-TIERS-1: CTO helpers' list-price cost by agentType (sessions.json meta) and by ACT/non-ACT ticket id."""
import json, collections
U = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/usage-1/"
S = json.load(open(U + "sessions.json")); cost = collections.Counter()
for l in open(U + "calls.jsonl"):
    c = json.loads(l)
    if c["kind"] == "cto-helper": cost[c["key"]] += c["cost"]
t = collections.Counter(); n = collections.Counter()
for k, v in cost.items():
    s = S[k]; at = (s["meta"] or {}).get("agentType") or "?"
    act = any(i.startswith("ACT") for i in s["ids"])
    t[(at, "ACT" if act else "-")] += v; n[(at, "ACT" if act else "-")] += 1
for k, v in t.most_common(): print(k, round(v, 2), n[k])
print("total", round(sum(cost.values()), 2))
