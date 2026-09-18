#!/usr/bin/env python3
"""A2 bullet 3 / S5 bullet 8 — failure atomicity of `gov kernel reinstall` when the source is an AUTHENTIC release of a
different version (no break-glass, above the floor). cli/src/main.rs commits the new payload with install_kernel and
only afterwards compares it with framework.lock.release_hash (KERNEL_MISMATCH). This probe observes what state a
refused reinstall leaves behind on a PROVISIONED machine (authentic 4.1.5 seq 10 installed; reinstall from authentic
4.1.6 seq 20).
[V0] installed state before; [V1] the reinstall; [V2] state after (kernel on disk, lock, protected installed record,
floors, whether ordinary governed mutations still work); [V3] the documented remedy.
Run: PROBE_TMP=<scratch> python3 A2-08-reinstall-version-change.py
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("a2-reinst")
R = [K("root-a"), K("root-b"), K("root-c")]
REL1, SNAP, TS = K("release-1"), K("snapshot-1"), K("timestamp-1")
roles = {"root": (2, R), "release": (1, [REL1]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS])}
anchor = os.path.join(sb.admin, "root-1.json"); open(anchor, "w").write(envelope(root_doc(1, roles), R[:2]))
o = sb.gov("trust", "provision", "--anchor", anchor, cwd=sb.home, quiet=True); assert o["ok"], o
V = [0]
def build_signed(name, version, seq, supported=None, migration=None):
    canon = canonical_copy(sb.path(name + "-canon"), version=version, supported_from=supported, extra_migration=migration)
    out = sb.gov("release", "build", "--version", version, "--canonical", canon, "--out", sb.path(name), quiet=True); assert out.get("ok"), out
    d = sb.path(name, "releases", version); V[0] += 1
    publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=seq, version=V[0]), [REL1], [SNAP], [TS], snap_version=V[0], ts_version=V[0])
    return os.path.join(d, "kernel")
k15 = build_signed("r15", "4.1.5", 10)
mig = ("M-4.1.5-4.1.6.yaml", {"id": "M-4.1.5-4.1.6", "from_version": "4.1.5", "to_version": "4.1.6", "description": "synthetic audit release",
       "breaking": False, "human_gate": "none", "affected_indexes": [], "operations": [{"op": "note", "text": "audit"}], "rollback": "gov update --rollback"})
k16 = build_signed("r16", "4.1.6", 20, supported=["4.1.5"], migration=mig)
p = sb.new_repo("p", {"README.md": "# p\n"})
o = sb.gov("init", "--source", k15, "--name", "p", "--alias", "pa", "--skip-index", cwd=p, quiet=True); assert o["ok"], o
def state(tag):
    kv = sb.gov("kernel", "verify", cwd=p, quiet=True).get("result") or {}
    lock = yaml.safe_load(open(os.path.join(p, "governance/framework.lock")))
    man = json.load(open(os.path.join(p, "governance/kernel/KERNEL_MANIFEST.json")))
    ts = sb.gov("trust", "status", quiet=True)["result"]
    t = sb.gov("task", "create", "--objective", f"probe {tag}", cwd=p, quiet=True)
    print(f"[{tag}] kernel on disk: version={man.get('version')} payload_hash={str(man.get('payload_hash'))[:16]}… | lock: version={lock['version']} release_hash={lock['release_hash'][:16]}…")
    print(f"[{tag}] kernel verify ok={kv.get('ok')} trust.verified={(kv.get('trust') or {}).get('verified')} problems={[x[:110] for x in ((kv.get('trust') or {}).get('problems') or [])][:2]}")
    print(f"[{tag}] protected installed record: version={ts['installed_release'].get('release_version')} seq={ts['installed_release'].get('sequence')} payload_hash={ts['installed_release'].get('payload_hash','')[:16]}… | floors.release_high_water={ts['floors']['release_high_water']}")
    print(f"[{tag}] ordinary governed mutation (task create): {'ok' if t['ok'] else 'REFUSED ' + err(t)}")
print("## [V0] authentic 4.1.5 (seq 10) installed on a provisioned machine")
state("V0")
print("\n## [V1] gov kernel reinstall --source <authentic 4.1.6, seq 20> (above floor, no break-glass)")
o = sb.gov("kernel", "reinstall", "--source", k16, cwd=p)
print("\n## [V2] state after the refused reinstall")
state("V2")
print("\n## [V3] remedy: reinstall the release the lock names (authentic 4.1.5)")
o = sb.gov("kernel", "reinstall", "--source", k15, cwd=p, quiet=True)
print("[V3] reinstall 4.1.5 ->", "ok" if o["ok"] else f"REFUSED {err(o)}: {o['error']['message'][:160]}")
state("V3")
print("\nDONE")
