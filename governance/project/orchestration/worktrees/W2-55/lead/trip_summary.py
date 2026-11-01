import json
import subprocess
import sys
from collections import Counter

out = subprocess.run([sys.executable, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/tripwire.py",
                      "compare", sys.argv[1]], capture_output=True, text=True)
print("exit", out.returncode)
try:
    doc = json.loads(out.stdout)
except ValueError:
    print(out.stdout[-3000:], out.stderr[-2000:])
    sys.exit(0)
counts = Counter()
other = []
for c in doc.get("changes", []):
    counts[(c["tree"], c["change"])] += 1
    if c["change"] not in ("status line gone", "status line added"):
        other.append(c)
    elif "pytest-of-usain" not in c.get("line", "") and c["tree"].endswith(("W2-55", "W2-55-tests")):
        other.append(c)
for (tree, change), n in sorted(counts.items()):
    print(f"{n:6d}  {change:22s} {tree}")
print("--- non-status changes, and W2-55 status lines other than pytest-of-usain:")
for c in other:
    print(json.dumps(c))
for k in doc:
    if k != "changes":
        print(k, json.dumps(doc[k])[:500])
