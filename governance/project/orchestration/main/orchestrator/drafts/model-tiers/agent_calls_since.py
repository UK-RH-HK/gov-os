"""MODEL-TIERS-1: Agent-tool calls in the main project's top-level transcripts after USAGE-1's cutoff: subagent_type and
model/effort parameters only; and the models of subagent transcripts started since (metadata only)."""
import json, collections, glob, os
D = os.path.expanduser("~/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/")
T = "2026-11-10T11:36:43"
c = collections.Counter(); m = collections.Counter()
for p in glob.glob(D + "*.jsonl"):
    if os.path.getmtime(p) < 1762774603: continue  # 2026-11-10 11:36 UTC
    for line in open(p, errors="replace"):
        try: d = json.loads(line)
        except ValueError: continue
        if (d.get("timestamp") or "") < T or d.get("type") != "assistant": continue
        for b in (d.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Agent", "Task"):
                i = b.get("input") or {}; c[(i.get("subagent_type"), i.get("model"), i.get("effort"))] += 1
for p in glob.glob(D + "*/subagents/*.jsonl"):
    if os.path.getmtime(p) < 1762774603: continue
    for line in open(p, errors="replace"):
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") == "assistant" and (d.get("timestamp") or "") >= T:
            m[((d.get("message") or {}).get("model"), d.get("effort"))] += 1
print("Agent calls since cutoff (type, model, effort):", c.most_common())
print("subagent assistant lines since cutoff (model, effort):", m.most_common())
