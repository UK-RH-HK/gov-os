"""Print a launched worker's result and its permission denials from its log (the last JSON object)."""
import json
import sys

text = open(sys.argv[1]).read()
data = json.loads(text[text.find("{"):])
print(data["result"])
print("SESSION", data.get("session_id"))
print("DENIALS", len(data.get("permission_denials", [])))
for item in data.get("permission_denials", []):
    print(" -", item["tool_name"], str(item["tool_input"])[:300])
