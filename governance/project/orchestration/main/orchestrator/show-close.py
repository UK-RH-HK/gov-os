"""Print a gov close envelope in short: python3 show-close.py <log name>."""
import json
import sys

L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/"
d = json.load(open(L + sys.argv[1], encoding="utf-8"))
print("ok:", d.get("ok"))
r = d.get("result") or d.get("error") or {}


def show(o, depth=0, key=""):
    pad = "  " * depth
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)) and depth < 3:
                print(f"{pad}{k}:")
                show(v, depth + 1, k)
            else:
                print(f"{pad}{k}: {json.dumps(v)[:500]}")
    elif isinstance(o, list):
        for v in o[:40]:
            if isinstance(v, (dict, list)) and depth < 4:
                show(v, depth + 1, key)
                print(pad + "  -")
            else:
                print(f"{pad}- {json.dumps(v)[:500]}")


show(r)
