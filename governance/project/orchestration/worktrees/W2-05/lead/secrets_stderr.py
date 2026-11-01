"""Print the secrets-indexing entry's status and the full stderr of its findings from a gov check --json file."""
import json
import sys

data = json.load(open(sys.argv[1]))
result = data.get("result", data)
for entry in result.get("checks", []):
    if entry.get("id") == "secrets-indexing":
        print("status:", entry.get("status"))
        for finding in entry.get("findings", []):
            print("code:", finding.get("code"), "|", finding.get("message"))
            print(finding.get("stderr", ""))
