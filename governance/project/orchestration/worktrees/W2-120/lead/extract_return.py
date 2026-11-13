import json
import sys

path = sys.argv[1]
texts = []
with open(path, encoding="utf-8") as fh:
    for line in fh:
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("type") != "assistant":
            continue
        content = rec.get("message", {}).get("content", [])
        for part in content if isinstance(content, list) else []:
            if part.get("type") == "text" and "task:" in part.get("text", ""):
                texts.append(part["text"])
print(texts[-1] if texts else "NO RETURN FOUND")
