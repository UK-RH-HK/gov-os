"""MODEL-TIERS-1 Q5: what large tool results cost as context. For each tool result, its size and the number of model
calls after it in the same session (each re-reads it from cache). Read targets compared only as sha1 hashes of the
path (as USAGE-1 did) against the session's Edit/Write targets. No message text is printed or stored."""
import json, re, hashlib, collections
from pathlib import Path
U = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/usage-1/"
ROOT = Path.home() / ".claude/projects"
S = json.load(open(U + "sessions.json"))
T0, T1 = "2026-11-08T09:00", "2026-11-10T11:36:43"
GROUP = {"worktree": "workers", "cto-helper": "helpers", "cto": "cto"}
CPT = 3.7          # characters per token (E)
READ, WRITE = {"workers": (0.20, 8.0), "helpers": (0.20, 5.0), "cto": (0.20, 5.0)}, None
import os
REPL = int(os.environ.get("REPL", "22200"))  # chars of a search answer: gov retrieve's 6,000-token bundle (BUNDLE_BUDGET) x 3.7 (E)
h = lambda x: hashlib.sha1(str(x).encode()).hexdigest()[:12]
out = collections.defaultdict(collections.Counter)
for key, s in S.items():
    g = GROUP.get(s["kind"])
    if not g or not s.get("calls") or not (ROOT / key).exists():
        continue
    seen_mid = set(); ncalls = 0; events = []; edited = set(); tu = {}; readcount = collections.Counter()
    for line in open(ROOT / key, errors="replace"):
        try: d = json.loads(line)
        except ValueError: continue
        ts = d.get("timestamp") or ""
        if not (T0 <= ts <= T1): continue
        msg = d.get("message") or {}
        if d.get("type") == "assistant":
            mid = msg.get("id") or d.get("uuid")
            if mid not in seen_mid:
                seen_mid.add(mid); ncalls += 1
            for b in msg.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    i = b.get("input") or {}; n = b.get("name")
                    if n in ("Edit", "Write", "MultiEdit", "NotebookEdit"): edited.add(h(i.get("file_path", "")))
                    if n == "Read":
                        ph = h(i.get("file_path", "")); readcount[ph] += 1
                        tu[b.get("id")] = ("Read-whole" if "offset" not in i and "limit" not in i else "Read-part", ph, readcount[ph])
                    else:
                        tu[b.get("id")] = (n, None, 0)
        elif d.get("type") == "user" and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    lab, ph, k = tu.get(b.get("tool_use_id"), ("?", None, 0))
                    events.append((ncalls, lab, ph, k, len(json.dumps(b.get("content"), ensure_ascii=False))))
    r, w = READ[g]
    for pos, lab, ph, k, L in events:
        after = ncalls - pos
        tok = L / CPT
        cost = tok * (w + r * after) / 1e6
        out[g]["$all"] += cost
        out[g]["$" + lab] += cost
        if lab == "Read-whole" and L > max(20000, REPL) and ph not in edited:
            out[g]["$big-whole-unedited"] += cost
            out[g]["n big-whole-unedited"] += 1
            out[g]["$saved if searched"] += (L - REPL) / CPT * (w + r * after) / 1e6
        if lab.startswith("Read") and k > 1:
            out[g]["$repeat-reads"] += cost; out[g]["n repeat-reads"] += 1
        if lab == "Bash" and L > 10000:
            out[g]["$bash>10k"] += cost; out[g]["n bash>10k"] += 1
            out[g]["$saved if bash capped 4k"] += (L - REPL) / CPT * (w + r * after) / 1e6
for g, c in out.items():
    print(g, {k: (round(v, 1) if k.startswith("$") else v) for k, v in sorted(c.items()) if v})
