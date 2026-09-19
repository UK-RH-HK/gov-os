"""P2-AR-0032 (round-2 integration builder) evidence helper — NOT product code, TEST MATERIAL ONLY.

P2-ADJ-0001 (applied by WS-3 in round 2, merged here) turned the standalone human-gate anchor off: on a machine with
no Signed Release Root no human answer exists, and a machine's human channel is its provisioned root's `human-gate`
delegation. Builder probes written on the round-1 base provision a standalone anchor for the test owner's key
(repair-1/ws03/evidence/hc_owner.py, published seed 7), which the integrated binary refuses
(HUMAN_CHANNEL_STANDALONE_DISABLED). P2-HO-0030: such probes "must use the provisioned root, not re-enable the anchor".

`provision(run, root, where)` does exactly what WS-3's own derived named checks (repair-1/r2-ws03/evidence/
ws03_named_checks.r2-derived.py, `channel`) do:
  1. provision the machine with the throw-away root of repair-1/r2-ws03/evidence/hc_root.py (the published seeds of
     tests/certification/srr_material.rs, with `human-gate` delegated to seed 7 — the key hc_owner.py signs with),
     written outside the project;
  2. if the project already installed a kernel while unprovisioned, re-verify it on this machine: publish signed
     release metadata (same published seeds, through the alpha-r audit-of-record minter, read-only import) for exactly
     the installed payload and `gov kernel reinstall --source` it (orchestrator).
`run(*args)` must run gov for the probe's machine as an L4-capable role (orchestrator) and return the JSON envelope.
Nothing else in a derived probe changes because of this helper.
"""
import os
import shutil
import subprocess
import sys
import uuid

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 7))
R2WS03 = os.path.join(WT, "release/capability-baseline/repair-1/r2-ws03/evidence")
HC_ROOT = os.path.join(R2WS03, "hc_root.py")
sys.path.insert(0, R2WS03)
from r2_machine import REL, SNAP, TS, publish, release_doc, stage_files  # noqa: E402


def provision(run, root, where):
    st = run("trust", "human-channel")
    if (st.get("result") or {}).get("available"):
        return "available"
    os.makedirs(where, exist_ok=True)
    f = os.path.join(where, f"root-{uuid.uuid4().hex[:6]}.json")
    subprocess.run([sys.executable, HC_ROOT, f], check=True, capture_output=True)
    r = run("trust", "provision", "--anchor", f)
    if not r.get("ok"):
        raise RuntimeError(f"provisioning the throw-away root failed: {r.get('error')}")
    lock = os.path.join(root, "governance", "framework.lock")
    if os.path.exists(lock):
        pin = yaml.safe_load(open(lock))["release_hash"]
        src = os.path.join(root, "governance", "kernel")
        if stage_files(src)["payload_hash"] != pin:
            raise RuntimeError("the installed kernel does not measure to framework.lock's pin")
        rel = os.path.join(where, f"reanchor-{uuid.uuid4().hex[:6]}")
        shutil.copytree(src, os.path.join(rel, "kernel"))
        publish(os.path.join(rel, "metadata"), release_doc(os.path.join(rel, "kernel"), sequence=1, version=1),
                [REL], [SNAP], [TS])
        r = run("kernel", "reinstall", "--source", os.path.join(rel, "kernel"))
        if not r.get("ok"):
            raise RuntimeError(f"re-verifying the installed kernel failed: {r.get('error')}")
    st = run("trust", "human-channel")
    if not (st.get("result") or {}).get("available"):
        raise RuntimeError(f"no human channel after provisioning: {st}")
    return "provisioned"
