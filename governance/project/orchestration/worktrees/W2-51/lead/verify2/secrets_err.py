"""Print the secrets-indexing check's full stderr from gov check's JSON."""
import json
import sys

doc = json.load(open(sys.argv[1]))
for c in doc["error"]["details"]["checks"]:
    if c["id"] == "secrets-indexing":
        for f in c["findings"]:
            print(f.get("stderr") or json.dumps(f))
