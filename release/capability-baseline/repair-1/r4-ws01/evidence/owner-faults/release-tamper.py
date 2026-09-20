#!/usr/bin/env python3
"""P2-AR-0042 (BC-P2-02) — PLANTED-FAULT evidence for gate S's release owners: `gov release build` produces the
release evidence (immutable manifest + PRE_RELEASE_CHECKS.json), and `gov release verify` — the `release:release verify`
owner — accepts it as written and refuses it once one byte of the built release is changed.

Builder evidence (Contract v3 O3), labelled PLANTED-FAULT. Env: GOV (the binary), SCRATCH (private directory), REPO
(the canonical checkout the release is built from: framework, migrations, tools, the contract chain are copied).
"""
import json
import os
import shutil
import subprocess

GOV, SCR, REPO = os.environ["GOV"], os.environ["SCRATCH"], os.environ["REPO"]
if os.path.exists(SCR):
    os.rename(SCR, SCR + f".old-{os.getpid()}")
canon = os.path.join(SCR, "canonical")
for d in ["framework", "migrations", "tools", "tests/governance", "docs/generated"]:
    shutil.copytree(os.path.join(REPO, d), os.path.join(canon, d))
shutil.copy(os.path.join(REPO, "Governance_OS_Capability_Acceptance_Contract_v3.md"), canon)
env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
env.update({"HOME": os.path.join(SCR, "home"), "XDG_STATE_HOME": os.path.join(SCR, "state"),
            "XDG_CACHE_HOME": os.path.join(SCR, "cache")})
os.makedirs(env["HOME"], exist_ok=True)


def gov(*a):
    r = subprocess.run([GOV, "--json", "--root", canon, "--session", "S-rel", *a], env=env, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": False, "raw": (r.stdout + r.stderr)[-500:]}


out = os.path.join(SCR, "out")
version = "4.1.6"  # the kernel version the binary builds (release build refuses any other: VERSION_MISMATCH)
b = gov("release", "build", "--version", version, "--canonical", canon, "--out", out)
print(f"# release build ok={b.get('ok')} capability_contract={(b.get('result') or {}).get('pre_release_checks', {}).get('capability_contract', {}).get('verdict')} "
      f"error={(b.get('error') or {}).get('code')}", flush=True)
rel = os.path.join(out, "releases", version)
v0 = gov("release", "verify", rel)
print(f"CONTROL release verify (as written) ok={v0.get('ok')} result_ok={(v0.get('result') or {}).get('ok')} "
      f"error={(v0.get('error') or {}).get('code')}", flush=True)
victim = None
for dp, dn, fn in sorted(os.walk(rel)):
    for f in sorted(fn):
        if f.endswith(".yaml") and "manifest" not in f and "PRE_RELEASE" not in f:
            victim = os.path.join(dp, f)
            break
    if victim:
        break
with open(victim, "a") as fh:
    fh.write("# one planted byte\n")
v1 = gov("release", "verify", rel)
detected = not ((v1.get("result") or {}).get("ok") is True and v1.get("ok"))
print(f"CASE S S2 release:release verify tampered={os.path.relpath(victim, rel)} ok={v1.get('ok')} "
      f"result_ok={(v1.get('result') or {}).get('ok')} error={(v1.get('error') or {}).get('code')} -> "
      f"{'DETECTED' if detected else 'NOT_DETECTED'}  {json.dumps((v1.get('result') or v1.get('error') or {}))[:300]}",
      flush=True)
