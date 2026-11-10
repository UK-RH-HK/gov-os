"""MODEL-TIERS-1: aggregate USAGE-1's sessions.json (metadata only) by kind: models, efforts, agentType, tools."""
import json, collections, sys
U = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/usage-1/"
S = json.load(open(U + "sessions.json"))
calls = [json.loads(l) for l in open(U + "calls.jsonl")]
by = collections.defaultdict(lambda: collections.Counter())
cost = collections.defaultdict(float)
for c in calls:
    k = (c["kind"], c["model"], str(c.get("effort")))
    cost[k] += c["cost"]; by[k]["calls"] += 1
tot = sum(cost.values())
print("kind | model | effort | calls | $ | %")
for k, v in sorted(cost.items(), key=lambda x: -x[1]):
    if v > 0.5: print(" | ".join(k), "|", by[k]["calls"], "|", round(v, 2), "|", round(100*v/tot, 1))
print("total", round(tot, 2))
m = collections.Counter(); e = collections.Counter()
for c in calls: m[c["model"]] += c["cost"]; e[str(c.get("effort"))] += c["cost"]
print("by model", {a: round(100*b/tot, 2) for a, b in m.items()})
print("by effort", {a: round(100*b/tot, 2) for a, b in e.items()})
at = collections.Counter(); pe = collections.Counter()
for s in S.values():
    if s["meta"]:
        at[(s["kind"], s["meta"].get("agentType"))] += 1
        pe[json.dumps(s["meta"].get("pickedEffortModel"))[:80]] += 1
print("agentType", at.most_common(15)); print("pickedEffortModel", pe.most_common(8))
