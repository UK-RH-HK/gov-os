"""MODEL-TIERS-1 Q2/Q3/Q5: tool-call metadata from the transcripts USAGE-1 listed (sessions.json keys only; no new
folders opened). Reads only: tool names, the presence of Read's offset/limit keys, the Agent tool's model and
subagent_type parameters, whether a Bash command calls `gov retrieve` (a boolean from a regex; nothing kept), and
tool-result lengths. No message text is printed or stored."""
import json, re, collections, statistics
from pathlib import Path
U = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/usage-1/"
ROOT = Path.home() / ".claude/projects"
S = json.load(open(U + "sessions.json"))
T0, T1 = "2026-11-08T09:00", "2026-11-10T11:36:43"
RETR = re.compile(r"(gov(\.cli\.main)?\s+retrieve|gov_retrieve|retrieve\.py)")
GROUP = {"worktree": "workers", "cto-helper": "helpers", "cto": "cto"}
agg = collections.defaultdict(lambda: collections.Counter())
sizes = collections.defaultdict(list)
agent_params = collections.Counter()
per_session = {}
for key, s in S.items():
    g = GROUP.get(s["kind"])
    if not g or not s.get("calls"):
        continue
    p = ROOT / key
    if not p.exists():
        continue
    names = {}; info = {}
    ps = collections.Counter()
    for line in open(p, errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts = d.get("timestamp") or ""
        if not (T0 <= ts <= T1):
            continue
        msg = d.get("message") or {}
        c = msg.get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if not isinstance(b, dict):
                continue
            if d.get("type") == "assistant" and b.get("type") == "tool_use":
                n = b.get("name"); i = b.get("input") or {}
                names[b.get("id")] = n
                agg[g]["tool:" + n] += 1
                if n == "Read":
                    whole = "offset" not in i and "limit" not in i
                    info[b.get("id")] = "Read-whole" if whole else "Read-part"
                    agg[g]["Read-whole" if whole else "Read-part"] += 1
                elif n == "Bash":
                    cmd = str(i.get("command", ""))
                    if RETR.search(cmd):
                        agg[g]["retrieve"] += 1; ps["retrieve"] += 1
                        info[b.get("id")] = "Bash-retrieve"
                elif n in ("Agent", "Task"):
                    agent_params[(g, i.get("subagent_type"), i.get("model"))] += 1
                elif "retriev" in n.lower() or "memory" in n.lower():
                    agg[g]["retrieve-tool"] += 1
            elif d.get("type") == "user" and b.get("type") == "tool_result":
                tid = b.get("tool_use_id"); n = names.get(tid, "?")
                L = len(json.dumps(b.get("content"), ensure_ascii=False))
                lab = info.get(tid, n)
                sizes[(g, lab)].append(L)
                ps["chars:" + lab] += L; ps["n:" + lab] += 1
    per_session[key] = (g, ps)
for g in ("workers", "helpers", "cto"):
    a = agg[g]
    print(f"== {g}: Read whole {a['Read-whole']} part {a['Read-part']} | gov retrieve via Bash {a['retrieve']} | retrieve tools {a['retrieve-tool']}")
    print("   top tools", [(k[5:], v) for k, v in a.most_common() if k.startswith("tool:")][:8])
    for lab in ("Read-whole", "Read-part", "Bash", "Bash-retrieve", "Grep", "Agent", "TaskOutput"):
        v = sizes.get((g, lab))
        if v:
            v2 = sorted(v)
            print(f"   {lab}: n={len(v)} chars={sum(v)/1e6:.2f}M median={int(statistics.median(v))} p90={v2[int(.9*len(v2))-1]} max={v2[-1]} over20k={sum(x>20000 for x in v)} chars_over20k={sum(x for x in v if x>20000)/1e6:.2f}M")
n_ret = collections.Counter(g for k, (g, ps) in per_session.items() if ps["retrieve"])
n_all = collections.Counter(g for k, (g, ps) in per_session.items())
print("sessions using gov retrieve:", dict(n_ret), "of", dict(n_all))
print("Agent calls (group, subagent_type, model param):")
for k, v in agent_params.most_common(20): print("  ", k, v)
