#!/usr/bin/env python3
"""P3b — attribution control for P3: does the 4.1.2 binary expose restricted material on a plain (non-RoT-1) 4.1.5
project with the same classification? If yes, the P3 V0 `rebuild_memory` exposure is the 4.1.2 binary's own defect
(LC-2 class: it still operates), not something the RoT-1 layout introduced. Scratch only."""
import json, os, subprocess, tempfile
import yaml

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
GOV415 = REPO + "/target/release/gov"
GOV412 = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/f305345b-0820-4eb0-bb85-2afc50580a75/scratchpad/wt-412/target/release/gov"
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
S = tempfile.mkdtemp(prefix="p3b-", dir=SCRATCH)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
MARK = "P3BRESTRICTEDMARKER"


def gov(b, root, *a):
    r = subprocess.run([b, "--json", "--root", root, "--session", "S-p3b", "--role", "orchestrator", *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True)


root = S + "/plain-4.1.5"
os.makedirs(root)
git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "i")
out = {"init": gov(GOV415, root, "init", "--source", REPO + "/release/releases/4.1.5", "--name", "p3b", "--skip-index").get("ok")}
os.makedirs(root + "/product", exist_ok=True)
open(root + "/product/restricted-plan.md", "w").write(f"# Plan\n\n{MARK} proprietary customer terms\n")
dsp = root + "/governance/project/DATA_SENSITIVITY.yaml"
ds = yaml.safe_load(open(dsp))
ds.setdefault("classifications", []).append({"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"})
yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
git(root, "add", "-A"); git(root, "commit", "-q", "-m", "classify")
for label, b in (("4.1.5", GOV415), ("4.1.2", GOV412)):
    rb = gov(b, root, "rebuild-memory")
    q = gov(b, root, "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if "restricted-plan" in (h.get("path") or "")]
    out[label] = {"rebuild_ok": rb.get("ok"), "code": (rb.get("error") or {}).get("code"), "restricted_retrievable": hits}
print(json.dumps(out, indent=2))
