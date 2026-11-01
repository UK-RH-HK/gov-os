"""Print a rebuild's digest, its stores' states and timing from its --json output, and the store files' sha256."""
import hashlib
import json
import sys
from pathlib import Path

data = json.load(open(sys.argv[1]))
result = data.get("result", data)
print("digest", result.get("digest"))
print("store.digest", (result.get("store") or {}).get("digest"))
print("stores", {name: (value.get("state") if isinstance(value, dict) else value)
                 for name, value in (result.get("stores") or {}).items()})
print("timing", result.get("timing"))
print("warnings", data.get("warnings"), "status", data.get("status"))
if len(sys.argv) > 2:
    for rel in (".gov-runtime/store.db", ".gov-runtime/codeintel/home/code.db", ".gov-runtime/codeintel/home/_config.db"):
        path = Path(sys.argv[2]) / rel
        print(rel, hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "absent")
