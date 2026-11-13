import os, sys, json, traceback
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/src")
from gov.retrieval import rerank
out = os.path.join(os.environ.get("PROBE_OUT", os.environ.get("TMPDIR", "/tmp")), "probe.json")
res = {}
try:
    scores, device = rerank._ask(str(os.path.expanduser("~/" + rerank.PYTHON_REL)), "which file builds the sandbox", ["the sandbox block is built in sandbox.py", "a recipe for bread"])
    res = {"ranked": True, "scores": scores, "device": device}
except Exception as e:
    res = {"ranked": False, "error": f"{type(e).__name__}: {e}"}
print(json.dumps(res))
open(out, "w").write(json.dumps(res) + "\n")
