"""B3 item 4, run inside the sandbox: one `gov retrieve` question against the integration store (GOV_STORE, as a launched worker's) (read-only: the sandbox
allows no write there). Prints which route answered: facets (lexical, semantic), merge.reranked, warnings."""
import json, os, subprocess, sys
ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
cmd = ["/home/usain/.local/bin/gov", "retrieve", "--json", "which file builds the launcher sandbox block"]  # no --root: GOV_STORE names the store, as in a launched worker
p = subprocess.run(cmd, capture_output=True, text=True, timeout=240, cwd=os.environ.get("PROBE_OUT", "/tmp"))
res = {"exit": p.returncode, "stderr": p.stderr[-1200:]}
try:
    d = json.loads(p.stdout); res["ok"] = d.get("ok"); d = d.get("result") or d
    res.update({"facets": d.get("facets"), "merge": d.get("merge"), "n_evidence": len(d.get("evidence", [])),
                "keys": sorted(d)[:20], "warnings": d.get("warnings"), "stopping_reason": d.get("stopping_reason")})
except Exception as e:
    res["parse_error"] = repr(e); res["stdout_head"] = p.stdout[:800]
out = os.path.join(os.environ.get("PROBE_OUT", "/tmp"), "retr.json")
try: open(out, "w").write(json.dumps(res, indent=1) + "\n")
except Exception as e: res["write_error"] = repr(e)
print(json.dumps(res))
