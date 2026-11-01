"""Prints why a `gov rebuild --json` output's semantic store is not built, or nothing when it is (or was not asked
for, --no-embeddings). Reads the output file named by argv[1]. Output that cannot be read prints its reason."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
try:
    envelope = json.loads(text[text.find("{"):text.rfind("}") + 1])
except ValueError:
    print("the rebuild's output is not JSON")
    sys.exit(0)
semantic = ((envelope.get("result") or {}).get("stores") or {}).get("semantic") or {}
if semantic.get("status") != "recreated" and semantic.get("requested", True) is not False:
    print(f"semantic store {semantic.get('status', 'absent')}: {semantic.get('reason', 'no reason given')}")
