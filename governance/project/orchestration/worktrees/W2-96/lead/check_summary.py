"""Summarise gov check's envelope: the error message and each non-green check's findings (codes and counts)."""
import collections
import json

text = open("/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/check.json", encoding="utf-8").read()
start = text.index('{"ok"')
envelope = json.loads(text[start:].splitlines()[0])
error = envelope.get("error", {})
print(error.get("code"), "|", str(error.get("message"))[:300])
details = error.get("details", {})
print("details keys:", list(details)[:20])
for name, value in details.items():
    if isinstance(value, list):
        print(name, len(value))
        for item in value[:40]:
            if isinstance(item, dict) and item.get("status") not in (None, "GREEN", "green"):
                findings = item.get("findings") or []
                codes = collections.Counter(f.get("code") for f in findings if isinstance(f, dict))
                print(" ", item.get("name") or item.get("id"), item.get("status"), dict(codes.most_common(6)))
                for f in findings[:3]:
                    print("     ", str(f)[:260])
