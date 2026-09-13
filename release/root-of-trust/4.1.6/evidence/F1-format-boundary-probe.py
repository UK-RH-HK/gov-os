#!/usr/bin/env python3
"""F1 — architecture feasibility probe: how does the real 4.1.5 binary treat a project written in the proposed RoT-1
trust format (lock 2.0.0 with compatibility sentinels, tombstone KERNEL_MANIFEST.json)? Scratch only."""
import json, os, subprocess, tempfile, yaml, shutil
REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"; GOV = REPO + "/target/release/gov"
S = tempfile.mkdtemp(prefix="f1-", dir=os.path.dirname(os.path.abspath(__file__)))
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}; ENV["GOV_KERNEL_CACHE"] = S + "/cache"
SENT = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-verify-this-project"
def gov(root, *a, role="orchestrator"):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-f1", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try: return json.loads(r.stdout)
    except Exception: return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}
def git(root, *a): subprocess.run(["git", "-c", "user.name=f", "-c", "user.email=f@x", *a], cwd=root, check=True, capture_output=True)
def code(d): return (d.get("error") or {}).get("code")
root = S + "/rot1-format"; os.makedirs(root); git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "i")
out = {"init": gov(root, "init", "--source", REPO + "/release/releases/4.1.5", "--name", "f1", "--skip-index").get("ok")}
lp = root + "/governance/framework.lock"; lock = yaml.safe_load(open(lp))
lock.update({"lock_schema_version": "2.0.0", "trust_format": "rot-1", "kernel_manifest_hash": SENT, "release_hash": SENT,
             "source": "release:agentic-engineering-os@4.1.5", "release_statement_digest": "sha256:" + "a" * 64})
yaml.safe_dump(lock, open(lp, "w"), sort_keys=False)
mp = root + "/governance/kernel/KERNEL_MANIFEST.json"; m = json.load(open(mp))
m.update({"trust_format": "rot-1", "notice": SENT, "files": {"TRUST-FORMAT-ROT-1/requires-gov-4.1.6": "0" * 64}, "payload_hash": SENT})
json.dump(m, open(mp, "w"), indent=2)
os.makedirs(root + "/governance/trust"); open(root + "/governance/trust/FORMAT", "w").write("rot-1\n")
git(root, "add", "-A"); git(root, "commit", "-q", "-m", "rot-1 format")
t = gov(root, "kernel", "trust"); tr = (t.get("result") or {}).get("trust") or {}
out["kernel_trust"] = {"verified": (t.get("result") or {}).get("verified"), "substituted": tr.get("substituted_embedded_baseline"), "problems_mention_sentinel": SENT in json.dumps(tr.get("problems"))}
kv = gov(root, "kernel", "verify"); out["kernel_verify_ok"] = (kv.get("result") or {}).get("ok")
d = gov(root, "doctor"); checks = ((d.get("result") or (d.get("error") or {}).get("details") or {}).get("checks") or [])
out["doctor"] = {"code": code(d), "failed_critical": sorted(c["id"] for c in checks if not c.get("ok") and c.get("severity") == "critical")}
tc = gov(root, "task", "create", "--title", "x", "--objective", "y", "--class", "implementation")
out["mutation_task_create"] = {"ok": tc.get("ok"), "code": code(tc), "message_mentions_sentinel": SENT in json.dumps(tc)}
rb = gov(root, "rebuild-memory"); out["rebuild_memory"] = {"ok": rb.get("ok"), "code": code(rb)}
pe = gov(root, "policy", "effective", "SECURITY_POLICY"); out["policy_effective_kernel_trust_verified"] = ((pe.get("result") or {}).get("kernel_trust") or {}).get("verified")
cp = gov(root, "capabilities", "plugins"); out["capabilities_plugins_ok"] = cp.get("ok")
st = gov(root, "status"); out["status_ok"] = st.get("ok")
# destructive exempt remedy on a copy: does 4.1.5 `kernel reinstall` overwrite a RoT-1 kernel before refusing?
cpy = S + "/rot1-format-reinstall"; shutil.copytree(root, cpy, symlinks=True)
before = open(cpy + "/governance/kernel/KERNEL_MANIFEST.json").read()
ri = gov(cpy, "kernel", "reinstall")
out["kernel_reinstall"] = {"ok": ri.get("ok"), "code": code(ri), "kernel_manifest_overwritten": open(cpy + "/governance/kernel/KERNEL_MANIFEST.json").read() != before}
print(json.dumps(out, indent=2))
