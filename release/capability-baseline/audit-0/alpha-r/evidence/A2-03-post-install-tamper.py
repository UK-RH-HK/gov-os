#!/usr/bin/env python3
"""A2 bullet 4 — installed-kernel verification detects post-install tampering (D-0007 integrity, kernel_trust).

T1 naive tamper: edit one installed kernel file.
T2 consistent tamper: edit the installed kernel file AND regenerate KERNEL_MANIFEST.json AND framework.lock so all three
   agree (what any agent with write access to governance/ can do with sha256 alone).
Both are run on a PROVISIONED machine after an AUTHENTIC install, so the machine's protected installed record holds the
authenticated payload digest and could in principle expose T2.
Run: PROBE_TMP=<scratch> python3 A2-03-post-install-tamper.py
"""
import os, sys, json, shutil, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("a2-tamper")
R = [K("root-a"), K("root-b"), K("root-c")]
REL1, SNAP, TS, REC = K("release-1"), K("snapshot-1"), K("timestamp-1"), K("recovery-1")
roles = {"root": (2, R), "release": (1, [REL1]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS]), "recovery": (1, [REC])}
anchor = os.path.join(sb.admin, "root-1.json"); open(anchor, "w").write(envelope(root_doc(1, roles), R[:2]))
sb.gov("trust", "provision", "--anchor", anchor, cwd=sb.home, quiet=True)
canon = canonical_copy(sb.path("canon"))
sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("rel"), quiet=True)
reldir = sb.path("rel", "releases", "4.1.5"); kern = os.path.join(reldir, "kernel")
publish(os.path.join(reldir, "metadata"), release_doc(kern, sequence=10, version=1), [REL1], [SNAP], [TS])

def fresh(name):
    p = sb.new_repo(name)
    o = sb.gov("init", "--source", kern, "--name", name, "--alias", name + "-a", "--skip-index", cwd=p, quiet=True)
    assert o["ok"] and o["result"]["release_authenticity"]["authenticity"] == "AUTHENTIC", o
    return p

def weaken(p):
    f = os.path.join(p, "governance/kernel/policies/SECURITY_POLICY.yaml")
    t = open(f).read(); open(f, "w").write(t.replace("never_index_classes: [secret, restricted]", "never_index_classes: []"))

def observe(p, label):
    kv = sb.gov("kernel", "verify", cwd=p, quiet=True)["result"]
    print(f"[{label}] gov kernel verify: ok={kv['ok']} modified={kv['modified']} trust.verified={kv['trust']['verified']} substituted={kv['trust']['substituted_embedded_baseline']}")
    eff = sb.gov("policy", "effective", "SECURITY_POLICY", cwd=p, quiet=True)["result"]["effective"]["never_index_classes"]
    print(f"[{label}] effective SECURITY_POLICY.never_index_classes = {eff}")
    t = sb.gov("task", "create", "--objective", "probe mutation", cwd=p, quiet=True)
    print(f"[{label}] mutating op `gov task create`: {'ok' if t['ok'] else 'REFUSED ' + str(err(t))}")
    d = sb.gov("doctor", cwd=p, quiet=True)
    res = d.get("result") or (d.get("error") or {}).get("details") or {}
    print(f"[{label}] doctor verdict={res.get('verdict')} D003={[ (c['ok'], c['message'][:90]) for c in res.get('checks', []) if c['id'] in ('D003','D004','D029')]}")
    st = sb.gov("status", cwd=p, quiet=True)["result"]
    print(f"[{label}] status.framework.release_hash={st['framework']['release_hash'][:16]}… status.release_trust.verified_payload_hash={str(st['release_trust']['verified_payload_hash'])[:16]}… authenticity={st['release_trust']['authenticity']}")
    a = sb.gov("audit", "--no-persist", "--family", "mutation_scope", cwd=p, quiet=True)
    res = a.get("result") or (a.get("error") or {}).get("details") or {}
    print(f"[{label}] audit mutation_scope verdict={res.get('verdict')} findings={[f['message'][:100] for f in res.get('findings', [])][:3]}")

print("## [T1] naive post-install tamper: one installed kernel file edited")
p1 = fresh("p-naive"); weaken(p1); observe(p1, "T1")
print("[T1] remedy: gov kernel reinstall --source <authentic release>")
o = sb.gov("kernel", "reinstall", "--source", kern, cwd=p1, quiet=True)
print("[T1] reinstall ok =", o["ok"], "| authenticity =", (o.get("result") or {}).get("release_authenticity", {}).get("authenticity"))
observe(p1, "T1-after-reinstall")

print("\n## [T2] consistent post-install tamper: kernel file + KERNEL_MANIFEST.json + framework.lock rewritten to agree")
p2 = fresh("p-consistent"); weaken(p2)
kd = os.path.join(p2, "governance/kernel")
m = json.load(open(os.path.join(kd, "KERNEL_MANIFEST.json")))
st = stage_files(kd)          # re-measure the tampered installed payload
m["files"] = st["files"]; m["payload_hash"] = st["payload_hash"]
json.dump(m, open(os.path.join(kd, "KERNEL_MANIFEST.json"), "w"), indent=2)
lp = os.path.join(p2, "governance/framework.lock")
lk = yaml.safe_load(open(lp))
lk["release_hash"] = st["payload_hash"]
lk["kernel_manifest_hash"] = sha256_text(canonical_json({k: m[k] for k in ("framework", "version", "files", "payload_hash")}))
open(lp, "w").write(yaml.safe_dump(lk, sort_keys=False))
print("[T2] rewrote KERNEL_MANIFEST.json payload_hash ->", st["payload_hash"][:16], "… and framework.lock release_hash/kernel_manifest_hash")
observe(p2, "T2")
ts = sb.gov("trust", "status", quiet=True)["result"]["installed_release"]
print("[T2] protected machine record (authenticated at install): payload_hash =", ts["payload_hash"][:16], "… ; installed payload now =", st["payload_hash"][:16], "…; equal =", ts["payload_hash"] == st["payload_hash"])
print("\nDONE")
