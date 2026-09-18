#!/usr/bin/env python3
"""P2-AR-0007 AC-16, cross-family chain X3: lifecycle ingress <-> root of trust (S3/S5 <-> A2), carried across into
sensitivity policy (A3), indexing/retrieval (C4/D1) and the health verdict (U/O5), which no single family traced:

  X3a  UNPROVISIONED machine (the default posture): a release whose SECURITY_POLICY was emptied after build is admitted
       by `gov init --source` (S3) -> is a path-classified secret then indexed and retrievable (C4/D1)? what do
       status/doctor/audit present (A2:150 masquerade, U)?
  X3b  PROVISIONED machine: the same tampered release is refused at init (A2 holds at ingress) ...
  X3c  ... but after an AUTHENTIC install, a mutually consistent payload + KERNEL_MANIFEST.json + framework.lock rewrite
       (A2:146) empties never_index_classes -> secret indexed/retrievable -> health verdict.
Uses the independent ed25519 SRR minter written by the alpha-r audit of record (read-only import of
release/capability-baseline/audit-0/alpha-r/evidence/lib/srr_mint.py; that file is not modified). Its measurement was
cross-checked by alpha-r against the product (authentic installs admitted AUTHENTIC); X3b/X3c re-check that here.

Run from the worktree root after `~/.cargo/bin/cargo build --release`:
  PROBE_TMP=<scratch> python3 release/capability-baseline/audit-0/synthesis/evidence/AC16-X3-ingress-root-of-trust-chain.py
"""
import json
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # never write a __pycache__ into another family's evidence directory
sys.path.insert(0, os.path.join(HERE, "..", "..", "alpha-r", "evidence", "lib"))
from srr_mint import (K, Sandbox, canonical_copy, canonical_json, envelope, publish, release_doc, root_doc,  # noqa
                     sha256_text, stage_files)

RES = []


def x(xid, ok, statement, detail=""):
    RES.append((xid, bool(ok)))
    print(f"X {xid} {'PASS' if ok else 'FAIL'} {statement} -- {json.dumps(detail, default=str)[:1500] if not isinstance(detail, str) else detail[:1500]}", flush=True)


SECRET_TOKEN = "ZQXJ7-SYNTH-UNIQUE-SECRET-VALUE-4471"
FILES = {"README.md": "# probe project\n", ".env": f"API_KEY={SECRET_TOKEN}\n", "src/app.py": "def main():\n    return 1\n"}


def weaken(policy_file):
    t = open(policy_file).read()
    assert "never_index_classes: [secret, restricted]" in t
    open(policy_file, "w").write(t.replace("never_index_classes: [secret, restricted]", "never_index_classes: []"))


def consequences(sb, p, label):
    """What the rest of the system does once kernel policy says never_index_classes: []."""
    eff = sb.gov("policy", "effective", "SECURITY_POLICY", cwd=p, quiet=True)
    eff_v = ((eff.get("result") or {}).get("effective") or {}).get("never_index_classes")
    rb = sb.gov("rebuild-memory", cwd=p, quiet=True)
    q = sb.gov("memory", "query", SECRET_TOKEN, "--k", "5", cwd=p, quiet=True)
    hits = (q.get("result") or {}).get("hits") or []
    leaked = [h.get("artifact_id") or h.get("path") for h in hits if SECRET_TOKEN in json.dumps(h)]
    st = sb.gov("status", cwd=p, quiet=True)
    rt = (st.get("result") or {}).get("release_trust") or {}
    d = sb.gov("doctor", cwd=p, quiet=True)
    dres = d.get("result") or (d.get("error") or {}).get("details") or {}
    a = sb.gov("audit", "--no-persist", cwd=p, quiet=True)
    ares = a.get("result") or (a.get("error") or {}).get("details") or {}
    info = {"effective_never_index_classes": eff_v, "rebuild_ok": rb.get("ok"), "secret_retrieved_by": leaked,
            "status.release_trust": {k: rt.get(k) for k in ("authenticity", "posture", "verified_release", "verified_payload_hash")},
            "envelope.presented_as": (st.get("release_trust") or {}).get("presented_as"),
            "doctor": dres.get("verdict"), "doctor_failing": [(c.get("id"), c.get("message", "")[:80]) for c in dres.get("checks", []) if not c.get("ok")],
            "audit": ares.get("verdict"), "audit_findings": [(f.get("family"), f.get("severity"), f.get("message", "")[:80]) for f in ares.get("findings", [])]}
    print(f"[{label}] " + json.dumps(info, default=str)[:3000], flush=True)
    return info


sb = Sandbox("synth-x3")
canon = canonical_copy(sb.path("canon"))
b = sb.gov("release", "build", "--version", "4.1.5", "--canonical", canon, "--out", sb.path("rel"), quiet=True)
assert b.get("ok"), b
reldir = sb.path("rel", "releases", "4.1.5")
kern = os.path.join(reldir, "kernel")

# ---------------------------------------------------------------- X3a unprovisioned machine, tampered release payload
kern_t = sb.path("tampered-kernel")
shutil.copytree(kern, kern_t)
weaken(os.path.join(kern_t, "policies", "SECURITY_POLICY.yaml"))
pa = sb.new_repo("pa", FILES)
o = sb.gov("init", "--source", kern_t, "--name", "pa", "--alias", "pa-a", cwd=pa, quiet=True)
ra = (o.get("result") or {}).get("release_authenticity") or {}
x("X3a-S3xA2-unprovisioned-refuses-unauthenticated", not o.get("ok"),
  "S3<->A2:143 on the default (unprovisioned) posture, privileged kernel material whose authenticity cannot be established is not installed",
  {"init_ok": o.get("ok"), "authenticity": ra.get("authenticity"), "posture": ra.get("posture")})
if o.get("ok"):
    info = consequences(sb, pa, "X3a")
    x("X3a-A2xA3xC4-tampered-policy-cannot-expose-secrets", not info["secret_retrieved_by"],
      "A2->A3->C4/D1: a secret classified by path is not indexed or retrievable after an unauthenticated ingress weakened kernel policy", info["secret_retrieved_by"])
    x("X3a-A2:150xU-no-masquerade", info["envelope.presented_as"] != "CURRENT" and info["doctor"] != "HEALTHY",
      "A2:150<->U: an unauthenticated installation is not presented as current and health does not report HEALTHY",
      {"presented_as": info["envelope.presented_as"], "doctor": info["doctor"], "audit": info["audit"], "status.release_trust": info["status.release_trust"]})

# ---------------------------------------------------------------- X3b/X3c provisioned machine
sbp = Sandbox("synth-x3p")
R = [K("root-a"), K("root-b"), K("root-c")]
REL1, SNAP, TS, REC = K("release-1"), K("snapshot-1"), K("timestamp-1"), K("recovery-1")
roles = {"root": (2, R), "release": (1, [REL1]), "snapshot": (1, [SNAP]), "timestamp": (1, [TS]), "recovery": (1, [REC])}
anchor = os.path.join(sbp.admin, "root-1.json")
open(anchor, "w").write(envelope(root_doc(1, roles), R[:2]))
pv = sbp.gov("trust", "provision", "--anchor", anchor, cwd=sbp.home, quiet=True)
print("[X3b] trust provision ok =", pv.get("ok"), flush=True)
canon2 = canonical_copy(sbp.path("canon"))
sbp.gov("release", "build", "--version", "4.1.5", "--canonical", canon2, "--out", sbp.path("rel"), quiet=True)
rel2 = sbp.path("rel", "releases", "4.1.5")
kern2 = os.path.join(rel2, "kernel")
publish(os.path.join(rel2, "metadata"), release_doc(kern2, sequence=10, version=1), [REL1], [SNAP], [TS])
# tamper after signing
kern2_t = sbp.path("rel-tampered")
shutil.copytree(rel2, kern2_t)
weaken(os.path.join(kern2_t, "kernel", "policies", "SECURITY_POLICY.yaml"))
pb = sbp.new_repo("pb", FILES)
ob = sbp.gov("init", "--source", os.path.join(kern2_t, "kernel"), "--name", "pb", "--alias", "pb-a", cwd=pb, quiet=True)
x("X3b-S3xA2-provisioned-refuses-tampered", not ob.get("ok"), "S3<->A2 on a provisioned machine the release tampered after signing is refused at init",
  {"ok": ob.get("ok"), "code": (ob.get("error") or {}).get("code")})
pc = sbp.new_repo("pc", FILES)
oc = sbp.gov("init", "--source", kern2, "--name", "pc", "--alias", "pc-a", cwd=pc, quiet=True)
auth = ((oc.get("result") or {}).get("release_authenticity") or {}).get("authenticity")
print("[X3c] authentic install ok =", oc.get("ok"), "authenticity =", auth, flush=True)
base = consequences(sbp, pc, "X3c-before-tamper")
x("X3c-baseline-secret-excluded", not base["secret_retrieved_by"], "baseline: on an authentic install the path-classified secret is not retrievable", base["secret_retrieved_by"])
# consistent post-install rewrite (payload + KERNEL_MANIFEST.json + framework.lock)
kd = os.path.join(pc, "governance/kernel")
weaken(os.path.join(kd, "policies", "SECURITY_POLICY.yaml"))
m = json.load(open(os.path.join(kd, "KERNEL_MANIFEST.json")))
stg = stage_files(kd)
m["files"] = stg["files"]
m["payload_hash"] = stg["payload_hash"]
json.dump(m, open(os.path.join(kd, "KERNEL_MANIFEST.json"), "w"), indent=2)
lp = os.path.join(pc, "governance/framework.lock")
lk = yaml.safe_load(open(lp))
lk["release_hash"] = stg["payload_hash"]
lk["kernel_manifest_hash"] = sha256_text(canonical_json({k: m[k] for k in ("framework", "version", "files", "payload_hash")}))
open(lp, "w").write(yaml.safe_dump(lk, sort_keys=False))
kv = sbp.gov("kernel", "verify", cwd=pc, quiet=True)
print("[X3c] kernel verify after consistent rewrite:", json.dumps({k: (kv.get("result") or {}).get(k) for k in ("ok", "modified")}), "trust.verified=", ((kv.get("result") or {}).get("trust") or {}).get("verified"), flush=True)
after = consequences(sbp, pc, "X3c-after-consistent-rewrite")
x("X3c-A2:146-consistent-rewrite-detected", not ((kv.get("result") or {}).get("trust") or {}).get("verified"),
  "A2:146 installed-kernel verification detects a mutually consistent post-install rewrite", (kv.get("result") or {}).get("trust"))
x("X3c-A2xA3xC4-secret-not-exposed", not after["secret_retrieved_by"],
  "A2->A3->C4/D1: after the undetected rewrite, the path-classified secret is still excluded from the index and retrieval", after["secret_retrieved_by"])
x("X3c-A2xU-health-reflects-tamper", after["doctor"] != "HEALTHY" or after["audit"] != "HEALTHY",
  "A2<->U: health does not report HEALTHY while the installed kernel's security policy has been rewritten to expose secrets",
  {"doctor": after["doctor"], "doctor_failing": after["doctor_failing"], "audit": after["audit"], "audit_findings": after["audit_findings"]})
# where did the secret go? (index tables, not only query results)
import sqlite3
dbp = os.path.join(pc, ".governance-runtime", "state.db")
db = sqlite3.connect(dbp)
in_chunks = db.execute("select count(*) from chunks where text like ?", (f"%{SECRET_TOKEN}%",)).fetchone()[0] if "text" in [c[1] for c in db.execute("pragma table_info(chunks)")] else "n/a"
env_art = db.execute("select count(*) from artifacts where path like '%.env%'").fetchone()[0]
excl = db.execute("select * from excluded where path like '%.env%'").fetchall()
print("[X3c] index after rewrite: .env artifact rows =", env_art, "| chunks containing the token =", in_chunks, "| excluded rows for .env =", excl, flush=True)
x("X3c-note-secret-exclusion-independent-of-never_index_classes", env_art == 0,
  "observation: a path-classified secret stays excluded even with never_index_classes emptied (a second exclusion layer holds); the A2 consequence is carried by other policies, see X3d", {"env_artifact_rows": env_art, "excluded": excl})

# ---------------------------------------------------------------- X3d consistent rewrite of the installed AUTHORITY_POLICY
def consistent_rewrite(proj, rel_file, old, new):
    kdd = os.path.join(proj, "governance/kernel")
    fp = os.path.join(kdd, rel_file)
    t = open(fp).read()
    assert old in t, (rel_file, old)
    open(fp, "w").write(t.replace(old, new))
    mm = json.load(open(os.path.join(kdd, "KERNEL_MANIFEST.json")))
    sg = stage_files(kdd)
    mm["files"] = sg["files"]; mm["payload_hash"] = sg["payload_hash"]
    json.dump(mm, open(os.path.join(kdd, "KERNEL_MANIFEST.json"), "w"), indent=2)
    lpp = os.path.join(proj, "governance/framework.lock")
    lkk = yaml.safe_load(open(lpp))
    lkk["release_hash"] = sg["payload_hash"]
    lkk["kernel_manifest_hash"] = sha256_text(canonical_json({k: mm[k] for k in ("framework", "version", "files", "payload_hash")}))
    open(lpp, "w").write(yaml.safe_dump(lkk, sort_keys=False))

def l1_answers_gate(proj, label):
    g1 = sbp.gov("gate", "create", "--question", f"{label}: may we drop the audit table?", "--fields",
                 json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R4", "reversibility": "irreversible", "confidence": 0.3}),
                 cwd=proj, role="orchestrator", quiet=True)
    gid = (g1.get("result") or {}).get("id")
    sbp.gov("gate", "present", gid, cwd=proj, role="orchestrator", quiet=True)
    # the L1 worker relays a 'human' answer (--by owner): answer_gate is the level required to relay a human answer
    dd = sbp.gov("decide", gid, "--option", "A", "--by", "owner", cwd=proj, role="backend-engineer", session="S-l1", quiet=True)
    rec = yaml.safe_load(open(os.path.join(proj, "spec/decisions", gid + ".yaml")))
    dd["_answer"] = rec.get("answer")
    return gid, dd

pd = sbp.new_repo("pd", FILES)
od = sbp.gov("init", "--source", kern2, "--name", "pd", "--alias", "pd-a", cwd=pd, quiet=True)
gid0, d0 = l1_answers_gate(pd, "control")
print("[X3d-control] authentic untampered kernel: L1 backend-engineer decide ->", d0.get("ok"), (d0.get("error") or {}).get("code"), flush=True)
consistent_rewrite(pd, "policies/AUTHORITY_POLICY.yaml", "answer_gate: L3", "answer_gate: L1")
kv2 = sbp.gov("kernel", "verify", cwd=pd, quiet=True)
gid1, d1 = l1_answers_gate(pd, "after-rewrite")
dres = sbp.gov("doctor", cwd=pd, quiet=True)
dv = (dres.get("result") or (dres.get("error") or {}).get("details") or {})
x("X3d-A2xE1xL3-rewrite-cannot-lower-gate-authority", not d1.get("ok"),
  "A2:146 <-> E1 <-> L3: after a mutually consistent rewrite of the installed AUTHORITY_POLICY (answer_gate L3 -> L1), an L1 worker still cannot record a human answer to a Human Decision Gate",
  {"control_L1_decide": (d0.get("error") or {}).get("code") or d0.get("ok"), "after_rewrite_answer": d1.get("_answer"), "kernel_verify_trust_verified": ((kv2.get("result") or {}).get("trust") or {}).get("verified"),
   "after_rewrite_L1_decide_ok": d1.get("ok"), "err": (d1.get("error") or {}).get("code"), "doctor": dv.get("verdict"),
   "doctor_failing": [(c.get("id"), c.get("message", "")[:70]) for c in dv.get("checks", []) if not c.get("ok")]})

f = [i for i, ok in RES if not ok]
print(f"SUMMARY total={len(RES)} pass={len(RES) - len(f)} fail={len(f)} failed={f}")
