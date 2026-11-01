"""Summarise gov check's envelope (the file given): the error and each non-green check's findings (codes, first messages)."""
import collections
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
envelope = json.loads(text[text.index('{"ok"'):].splitlines()[0])
error = envelope.get("error") or {}
print("ok:", envelope.get("ok"), "|", error.get("code"), "|", str(error.get("message"))[:300])
checks = (error.get("details") or {}).get("checks") or (envelope.get("result") or {}).get("checks") or []
print("checks:", len(checks))
for item in checks:
    if isinstance(item, dict) and item.get("status") not in (None, "GREEN", "green"):
        findings = item.get("findings") or []
        codes = collections.Counter(f.get("code") for f in findings if isinstance(f, dict))
        print(" ", item.get("name") or item.get("id"), item.get("status"), dict(codes.most_common(6)))
        for f in findings[:3]:
            print("     ", str(f.get("message") if isinstance(f, dict) else f)[:200])
