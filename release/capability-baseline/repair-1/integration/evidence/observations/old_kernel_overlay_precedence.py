#!/usr/bin/env python3
"""P2-AR-0022 observation (not an integration regression; reproduces on WS-3's branch alone): a project whose installed
kernel predates WS-3's POLICY_PRECEDENCE rules (the shipped releases release/releases/4.1.4 and 4.1.5) has its
descriptive PROJECT_POLICY keys (project.name / alias / created / onboarding_mode, schema_version) and its
MODEL_ROUTING_OVERRIDES keys (providers, preferences.*) refused by BC-P2-45's overlay evaluation ("not declared
overridable by the kernel precedence rules (deny by default)"), so doctor D027 is CRITICAL and the project UNHEALTHY; an
update 4.1.4 -> shipped 4.1.5 (alpha-r S5-update [U2]) is applied and then rolled back by its post-install verification.
The human gate is answered through WS-3's owner-signed channel (test-material signer, published seed).

Usage: python3 old_kernel_overlay_precedence.py <gov binary> <scratch dir>
"""
import json
import os
import subprocess
import sys
import tempfile

GOV, SCR = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
HC = os.path.join(WT, "release/capability-baseline/repair-1/ws03/evidence/hc_owner.py")
os.makedirs(SCR, exist_ok=True)
base = tempfile.mkdtemp(prefix="oldk-", dir=SCR)
p = os.path.join(base, "proj")
os.makedirs(p)
env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
env.update({"HOME": base + "/home", "XDG_STATE_HOME": base + "/state", "XDG_CACHE_HOME": base + "/cache",
            "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
            "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"})
os.makedirs(env["HOME"])
open(os.path.join(p, "README.md"), "w").write("# old kernel\n")
for a in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "b"]):
    subprocess.run(["git", *a], cwd=p, env=env, capture_output=True)


def g(*a):
    r = subprocess.run([GOV, "--json", "--root", p, "--session", "S-oldk", "--role", "orchestrator", *a], capture_output=True,
                       text=True, env=env, cwd=p)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": False, "raw": (r.stdout + r.stderr)[-400:]}


R14 = os.path.join(WT, "release/releases/4.1.4/kernel")
R15 = os.path.join(WT, "release/releases/4.1.5/kernel")
print("# gov", GOV)
print("init from shipped 4.1.4:", g("init", "--source", R14, "--name", "s5", "--alias", "s5-a").get("ok"))
ov = g("policy", "overrides").get("result") or {}
print("refused overlay keys on the 4.1.4 kernel:", [f"{r['policy']}.{r['key']}" for r in ov.get("refused", [])])
if ov.get("refused"):
    print("  e.g.:", ov["refused"][0].get("reason"))
d = g("doctor")
dd = d.get("result") or (d.get("error") or {}).get("details") or {}
print("doctor verdict:", dd.get("verdict"), "| D027:", [(c["id"], c["ok"], c.get("severity")) for c in dd.get("checks", []) if c["id"] == "D027"])
f = g("update", "--apply", "--source", R15)
gid = ((f.get("error") or {}).get("details") or {}).get("gate")
pr = g("gate", "present", gid)["result"]["gate"]
af = os.path.join(base, "anchor.json")
subprocess.run([sys.executable, HC, "anchor", af, "7"], check=True, capture_output=True)
g("trust", "human-channel", "--provision", af)
ans = os.path.join(base, "answer.json")
subprocess.run([sys.executable, HC, "answer", ans, gid, pr["gate_instance"], pr["package_sha256"], "A"], check=True, capture_output=True)
print("gate", gid, "answered through the owner-signed channel:", g("decide", gid, "--option", "A", "--answer-file", ans).get("ok"))
u = g("update", "--apply", "--source", R15, "--approve", "--by", "product-owner")
print("update 4.1.4 -> shipped 4.1.5:", "ok" if u.get("ok") else (u.get("error") or {}).get("code"), "|", (u.get("error") or {}).get("message", "")[:160])
