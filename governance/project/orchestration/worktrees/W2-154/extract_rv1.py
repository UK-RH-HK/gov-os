import json
src = "/home/usain/.claude/projects/-home-usain-gov-os-worktrees-W2-154/a8944322-f55d-471d-9202-19e93496661e.jsonl"
out = "/home/usain/gov-os-worktrees/W2-154/.gov-runtime/scratch/lead/log/rv-1.return.md"
texts = []
for line in open(src, encoding="utf-8"):
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get("type") != "assistant":
        continue
    content = d.get("message", {}).get("content", [])
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    for c in content:
        if c.get("type") == "text" and "task:" in c.get("text", "") and "verdict" in c.get("text", ""):
            texts.append(c["text"])
open(out, "w", encoding="utf-8").write(texts[-1] if texts else "NONE")
print(len(texts), "candidate(s)")
