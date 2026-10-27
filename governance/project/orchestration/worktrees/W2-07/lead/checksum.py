"""Summarise a `gov check --json` log: overall status and every check that is not GREEN."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
data = json.JSONDecoder().raw_decode(text[text.find("{"):])[0]
result = data.get("result") or {}
print("ok:", data.get("ok"), "status:", result.get("status"), "error:", data.get("error"))


def walk(node):
    if isinstance(node, dict):
        if "id" in node and "status" in node and node.get("status") != "GREEN":
            print(" ", node.get("id"), node.get("status"), node.get("code") or node.get("reason") or "")
        for value in node.values():
            walk(value)
    elif isinstance(node, list):
        for value in node:
            walk(value)


walk(result)
