"""Read-only: print the containment findings of the two exit clones that restored an acceptance test (DEC-688)."""
import json

C = "/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/"
for clone in ("a-dev-exit", "b-dev-exit"):
    rows = []
    for line in open(C + clone + "/.gov-runtime/findings.jsonl", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            rows.append({"raw": line[:200]})
    print("==", clone, "findings:", len(rows))
    kinds = {}
    for r in rows:
        k = str(r.get("kind") or r.get("code") or r.get("action") or r.get("reason") or "")[:60]
        kinds[k] = kinds.get(k, 0) + 1
    print("kinds:", kinds)
    hits = [r for r in rows if "restored from HEAD" in json.dumps(r)]
    print("restores:", len(hits))
    if hits:
        print("keys:", sorted(hits[0].keys()))
    for r in hits:
        short = {k: (str(v)[:260]) for k, v in r.items()}
        print(json.dumps(short, ensure_ascii=False))
