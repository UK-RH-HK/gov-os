"""READY from a reviewer log's last result, through the CTO's verdict.py (DEC-1010 item 1)."""
import json
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
import verdict  # noqa: E402

text = open(sys.argv[1], encoding="utf-8").read()
dec = json.JSONDecoder()
last, i = None, 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
    except ValueError:
        i = j + 1
        continue
    if isinstance(obj, dict) and "result" in obj:
        last = obj
    i = end
print(verdict.ready(last["result"]))
