"""Print captured skilleval replies: python3 show_replies.py <start-line> <end-line> [maxchars]."""
import json
import sys

path = "/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/capture/replies.jsonl"
start, end = int(sys.argv[1]), int(sys.argv[2])
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
for n, line in enumerate(open(path), 1):
    if not start <= n <= end:
        continue
    d = json.loads(line)
    kind = "JUDGE" if d["prompt"].startswith("You judge") else "SESSION"
    try:
        result = json.loads(d["stdout"]).get("result", "")
    except ValueError:
        result = "<not json> " + d["stdout"][:200]
    print(f"===== line {n} {kind} at {d['at']} rc {d['rc']}")
    if kind == "SESSION":
        print("PROMPT:", d["prompt"][:300].replace("\n", " "))
    print(result[:limit])
