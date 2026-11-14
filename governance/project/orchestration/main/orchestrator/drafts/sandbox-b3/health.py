"""B3 item 4 control: the very call `gov retrieve`'s semantic route makes first (gov.retrieval.ollama._healthy: GET /api/version,
urllib with ProxyHandler({}), i.e. no proxy), at 127.0.0.1:11434 only. Run unsandboxed (control) and inside each sandbox variant."""
import json, os, sys, time
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/src")
from gov.retrieval import ollama
res = {"ProxyHandler_empty_client_healthy": ollama._healthy("http://127.0.0.1:11434/api/version", time.monotonic() + 3.0)}
out = os.environ.get("PROBE_OUT")
if out:
    try: open(os.path.join(out, "health.json"), "w").write(json.dumps(res) + "\n")
    except Exception as e: res["write_error"] = repr(e)
print(json.dumps(res))
