#!/usr/bin/env python3
"""Independent architecture-review probes against the rejected 4.1.5 binary (scratch only; repository never written).

R1  legacy-kernel floors: a genuine 4.1.2 kernel (which RoT-1 would authenticate as AUTHENTICATED_REJECTED with
    verified:true and read floors from) versus the 4.1.5 kernel, same binary, same L3 role.
R2  use-time TOCTOU: a same-user process swaps SECURITY_POLICY.yaml after kernel_trust hashed it and restores it when
    the gov process exits. Question: can the verified-bytes / used-bytes gap produce persistent harm while every check
    reports verified:true? (RoT-1 04 section 5 keeps a TrustedKernel "over installed dir".)
"""
import ctypes, ctypes.util, json, os, shutil, struct, subprocess, sys, tempfile, threading, time
import yaml

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
GOV = REPO + "/target/release/gov"
SP = os.path.dirname(os.path.abspath(__file__))
S = tempfile.mkdtemp(prefix="review-r1-", dir=SP)
ENV = {k: v for k, v in os.environ.items() if k not in ("GOV_CANONICAL_ROOT", "GOV_ROLE", "GOV_SESSION", "GOV_KERNEL_SOURCE")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"


def gov(root, role, *args, popen=False):
    cmd = [GOV, "--json", "--root", root, "--session", "S-review", "--role", role, *args]
    if popen:
        return subprocess.Popen(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    r = subprocess.run(cmd, env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def code(d):
    return (d.get("error") or {}).get("code")


def mkrepo(path):
    os.makedirs(path)
    for c in (["git", "init", "-q"], ["git", "-c", "user.name=r", "-c", "user.email=r@x", "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(c, cwd=path, check=True)


def commit(path, msg):
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "-c", "user.name=r", "-c", "user.email=r@x", "commit", "-q", "-m", msg], cwd=path, check=True)


out = {"scratch": S}


r1 = {}
for ver in ("4.1.2", "4.1.5"):
    root = f"{S}/legacy-{ver}"
    mkrepo(root)
    init = gov(root, "orchestrator", "init", "--source", f"{REPO}/release/releases/{ver}", "--name", "l", "--skip-index")
    commit(root, "installed")
    trust = gov(root, "orchestrator", "kernel", "trust")
    eff = gov(root, "orchestrator", "policy", "effective", "AUTHORITY_POLICY")
    ops = json.dumps(eff).count('"update_apply"') > 0
    upd = gov(root, "change-controller", "update", "--apply", "--source", f"{REPO}/release/releases/4.1.5")
    res = gov(root, "change-controller", "resume")
    r1[ver] = {
        "init_ok": init.get("ok"), "version": (init.get("result") or {}).get("version"),
        "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
        "AUTHORITY_POLICY_declares_update_apply": ops,
        "L3_change_controller_update_apply": {"ok": upd.get("ok"), "code": code(upd), "applied": (upd.get("result") or {}).get("applied")},
        "L3_change_controller_resume": {"ok": res.get("ok"), "code": code(res)},
    }
out["R1_legacy_kernel_floors"] = r1

print(json.dumps(out, indent=2))

