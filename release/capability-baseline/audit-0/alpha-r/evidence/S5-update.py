#!/usr/bin/env python3
"""S5 — gov update (nine bullets) with the genuine shipped releases release/releases/4.1.4 -> 4.1.5 (unprovisioned
machine), plus: automatic rollback on a failing update (synthetic 4.1.6 whose migration breaks the overlay),
compatibility refusal, and the refused-update / rollback interaction on a PROVISIONED machine.
The authenticated-source bullet on a provisioned machine is A2-02 [P9] (cross-reference).
Run: PROBE_TMP=<scratch> python3 S5-update.py
"""
import os, sys, json, shutil, hashlib, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

def tree_hash(d, skip=()):
    h = hashlib.sha256()
    for dp, dn, fn in sorted(os.walk(d)):
        dn.sort()
        for f in sorted(fn):
            ab = os.path.join(dp, f); rel = os.path.relpath(ab, d)
            if any(rel.startswith(s) for s in skip):
                continue
            h.update(rel.encode()); h.update(open(ab, "rb").read())
    return h.hexdigest()[:16]
R14 = os.path.join(REPO, "release/releases/4.1.4/kernel"); R15 = os.path.join(REPO, "release/releases/4.1.5/kernel")
sb = Sandbox("s5")
p = sb.new_repo("proj", {"README.md": "# s5\n", "product/app.py": "def run():\n    return 1\n"})
o = sb.gov("init", "--source", R14, "--name", "s5", "--alias", "s5-a", cwd=p, quiet=True)
print("## [U0] installed 4.1.4:", o["ok"], "| lock version =", yaml.safe_load(open(os.path.join(p, "governance/framework.lock")))["version"])
PP = os.path.join(p, "governance/project/PROJECT_POLICY.yaml"); y = yaml.safe_load(open(PP))
y["policy_overrides"] = {"AUTHORITY_POLICY.authority_levels_required.create_task": "L3"}; y["project"]["name"] = "s5-customised"
open(PP, "w").write(yaml.safe_dump(y, sort_keys=False))
DS = os.path.join(p, "governance/project/DATA_SENSITIVITY.yaml"); d = yaml.safe_load(open(DS)); d["classifications"] = [{"pattern": "product/data/**", "class": "restricted", "reason": "customer"}]
open(DS, "w").write(yaml.safe_dump(d, sort_keys=False))
os.makedirs(os.path.join(p, "spec/decisions"), exist_ok=True)
open(os.path.join(p, "spec/decisions/D-0001.yaml"), "w").write(yaml.safe_dump({"id": "D-0001", "type": "decision", "title": "keep", "status": "ACTIVE"}))
sb.gov("task", "create", "--objective", "survive the update", role="change-controller", cwd=p, quiet=True)
sb.git(p, "add", "-A"); sb.git(p, "commit", "-q", "-m", "customised")
spec_before = tree_hash(os.path.join(p, "spec"), skip=("reports/framework-updates.jsonl", "reports/checkpoints", "audits/"))
ov_before = open(PP).read()
adapters_before = json.load(open(os.path.join(p, "governance/generated/adapter-manifest.json")))
idx_before = json.load(open(os.path.join(p, "governance/generated/index-manifest.json"))).get("manifest_hash") if os.path.exists(os.path.join(p, "governance/generated/index-manifest.json")) else None

print("\n## [U1] gov update --check (impact simulation)")
c = sb.gov("update", "--check", "--source", R15, cwd=p, quiet=True)["result"]
print("[U1]", json.dumps({k: c[k] for k in ("current", "available", "up_to_date", "downgrade", "compatible", "migration_path", "certification", "human_gate_required", "recommendation")}))
print("[U1] impact:", json.dumps(c["impact"])[:700])

print("\n## [U2] gov update --apply (human gate, then apply)")
o = sb.gov("update", "--apply", "--source", R15, cwd=p, quiet=True)
print("[U2] apply without --approve:", "ok " + json.dumps(o["result"])[:200] if o["ok"] else f"REFUSED {err(o)}: {o['error']['message'][:200]}")
gid = (o.get("error") or {}).get("details", {}).get("gate") if not o["ok"] else o["result"].get("human_gate")
o = sb.gov("update", "--apply", "--source", R15, "--approve", cwd=p, quiet=True)
print("[U2] --approve alone (gate not presented/answered):", json.dumps(o.get("result") or o.get("error"))[:220])
gid = gid or (o.get("result") or {}).get("human_gate")
sb.gov("gate", "present", gid, cwd=p, quiet=True); sb.gov("decide", gid, "--option", "A", "--by", "product-owner", role="human", cwd=p, quiet=True)
o = sb.gov("update", "--apply", "--source", R15, "--approve", "--by", "product-owner", cwd=p, quiet=True)
r = o.get("result") or {}
print("[U2] apply after the gate:", o["ok"], "| applied =", r.get("applied"), "| from", r.get("from"), "to", r.get("to"))
det = r.get("details") or {}
print("[U2] migrations =", det.get("migrations"), "| operations =", json.dumps(det.get("operations"))[:300])
print("[U2] overlay_keys_changed =", det.get("overlay_keys_changed"), "| overlay_reconciled =", det.get("overlay_reconciled"))
print("[U2] index_manifest =", det.get("index_manifest"), "| doctor =", det.get("doctor"), "| audit =", det.get("audit"), "| lock =", det.get("lock"))
print("[U2] release_authenticity =", (det.get("release_authenticity") or {}).get("authenticity"))

print("\n## [U3] overlay preserved / spec untouched / adapters regenerated / indexes rebuilt")
y2 = yaml.safe_load(open(PP))
print("[U3] customised overlay values kept: name =", y2["project"]["name"], "| override =", y2.get("policy_overrides"), "| DATA_SENSITIVITY =", yaml.safe_load(open(DS))["classifications"])
chg = subprocess.run(["git", "status", "--porcelain", "--", "spec"], cwd=p, capture_output=True, text=True).stdout.splitlines()
print("[U3] spec/ changes since the pre-update commit (git status):", chg)
print("[U3] pre-existing governed records unchanged: D-0001 =", yaml.safe_load(open(os.path.join(p, "spec/decisions/D-0001.yaml"))), "| git diff on committed spec files:", subprocess.run(["git", "diff", "--stat", "--", "spec"], cwd=p, capture_output=True, text=True).stdout.strip() or "(none)")
ad = json.load(open(os.path.join(p, "governance/generated/adapter-manifest.json")))
print("[U3] adapter manifest keys:", sorted(ad.keys()) if (ad := json.load(open(os.path.join(p, "governance/generated/adapter-manifest.json")))) else None)
print("[U3] adapter manifest before/after:", json.dumps({k: adapters_before.get(k) for k in ("kernel_version", "framework_version", "generated_at", "overlay_hash")})[:200], "->", json.dumps({k: ad.get(k) for k in ("kernel_version", "framework_version", "generated_at", "overlay_hash")})[:200])
im = json.load(open(os.path.join(p, "governance/generated/index-manifest.json")))
print("[U3] index manifest before/after:", idx_before, "->", im.get("manifest_hash"), "| index_version =", im.get("index_version"))
print("[U3] lock now:", {k: yaml.safe_load(open(os.path.join(p, "governance/framework.lock")))[k] for k in ("version", "release_commit", "source")})

print("\n## [U4] ledger / provenance")
led = [json.loads(l) for l in open(os.path.join(p, "spec/reports/framework-updates.jsonl"))]
for l in led:
    print("[U4]", json.dumps({k: l.get(k) for k in ("event", "from", "to", "by", "session", "role", "result", "release_commit", "source")}))

print("\n## [U5] gov update --rollback (operator-initiated)")
o = sb.gov("update", "--rollback", "--reason", "probe rollback", cwd=p, quiet=True)
r = o.get("result") or {}
print("[U5] rollback:", o["ok"], "| rolled_back_to =", r.get("rolled_back_to"), "| kernel_ok =", r.get("kernel_ok"), "| doctor =", r.get("doctor"), "| error =", (o.get("error") or {}).get("code"))
print("[U5] overlay byte-identical to pre-update:", open(PP).read() == ov_before, "| lock version =", yaml.safe_load(open(os.path.join(p, "governance/framework.lock")))["version"])
led = [json.loads(l) for l in open(os.path.join(p, "spec/reports/framework-updates.jsonl"))]
print("[U5] ledger rollback entry:", json.dumps({k: led[-1].get(k) for k in ("event", "from", "to", "rolled_back_update", "authority_level", "reason", "resulting_lock", "verification")})[:500])
o = sb.gov("update", "--rollback", cwd=p, quiet=True)
print("[U5] second rollback:", "ok" if o["ok"] else f"REFUSED {err(o)}")

print("\n## [U6] compatibility: unsupported path; downgrade")
c16 = canonical_copy(sb.path("c16"), version="4.1.6", supported_from=["4.1.3"])
sb.gov("release", "build", "--version", "4.1.6", "--canonical", c16, "--out", sb.path("r16"), quiet=True)
k16 = sb.path("r16", "releases", "4.1.6", "kernel")
c = sb.gov("update", "--check", "--source", k16, cwd=p, quiet=True)["result"]
print("[U6] 4.1.4 -> 4.1.6 (supports only 4.1.3): compatible =", c["compatible"], "| migration_path_complete =", c["migration_path_complete"])
o = sb.gov("update", "--apply", "--source", k16, "--approve", cwd=p, quiet=True)
print("[U6] apply ->", "ok " + json.dumps(o["result"])[:160] if o["ok"] else f"REFUSED {err(o)}")
c = sb.gov("update", "--check", "--source", os.path.join(REPO, "release/releases/4.1.3/kernel"), cwd=p, quiet=True)["result"]
print("[U6] 4.1.4 -> 4.1.3 (downgrade): up_to_date =", c["up_to_date"], "| downgrade =", c["downgrade"], "| recommendation =", c["recommendation"])

print("\n## [U7] automatic transaction rollback when post-install verification fails")
mig = ("M-4.1.4-4.1.7.yaml", {"id": "M-4.1.4-4.1.7", "from_version": "4.1.4", "to_version": "4.1.7", "description": "breaks the overlay",
       "breaking": False, "human_gate": "none", "affected_indexes": [], "overlay_template_changes": [],
       "operations": [{"op": "set_overlay_key", "file": "PROJECT_POLICY.yaml", "key": "schema_version", "value": 12345}], "rollback": "gov update --rollback"})
c17 = canonical_copy(sb.path("c17"), version="4.1.7", supported_from=["4.1.4"], extra_migration=mig, mutate=lambda dd: os.remove(os.path.join(dd, "migrations", "M-4.1.4-4.1.5.yaml")))
b17 = sb.gov("release", "build", "--version", "4.1.7", "--canonical", c17, "--out", sb.path("r17"), "--certification", "CERTIFIED", quiet=True)
print("[U7] synthetic 4.1.7 built:", b17["ok"], (b17.get("error") or {}).get("message", "")[:200])
k17 = sb.path("r17", "releases", "4.1.7", "kernel")
kh_before = tree_hash(os.path.join(p, "governance/kernel")); lock_before = open(os.path.join(p, "governance/framework.lock")).read()
o = sb.gov("update", "--apply", "--source", k17, cwd=p, quiet=True)
print("[U7] apply ->", "ok " + json.dumps(o["result"])[:200] if o["ok"] else f"REFUSED {err(o)}: {o['error']['message'][:200]}")
print("[U7] kernel restored:", tree_hash(os.path.join(p, "governance/kernel")) == kh_before, "| lock restored:", open(os.path.join(p, "governance/framework.lock")).read() == lock_before)
led = [json.loads(l) for l in open(os.path.join(p, "spec/reports/framework-updates.jsonl"))]
print("[U7] last ledger entry:", json.dumps({k: led[-1].get(k) for k in ("event", "from", "to", "reason", "result")})[:300])

print("\n## [U8] PROVISIONED machine: refused update leaves its pre-admission snapshot; `update --rollback` then 'rolls back' an update that never happened")
sbp = Sandbox("s5-prov")
A_, B_, C_ = K("root-a"), K("root-b"), K("root-c"); REL, SN, TS_ = K("release-1"), K("snapshot-1"), K("timestamp-1")
roles = {"root": (2, [A_, B_, C_]), "release": (1, [REL]), "snapshot": (1, [SN]), "timestamp": (1, [TS_])}
an = os.path.join(sbp.admin, "root-1.json"); open(an, "w").write(envelope(root_doc(1, roles), [A_, B_]))
sbp.gov("trust", "provision", "--anchor", an, cwd=sbp.home, quiet=True)
cc = canonical_copy(sbp.path("cc")); sbp.gov("release", "build", "--version", "4.1.5", "--canonical", cc, "--out", sbp.path("rel"), quiet=True)
kk = sbp.path("rel", "releases", "4.1.5", "kernel"); publish(sbp.path("rel", "releases", "4.1.5", "metadata"), release_doc(kk, sequence=10, version=1), [REL], [SN], [TS_])
pp = sbp.new_repo("pp"); sbp.gov("init", "--source", kk, "--name", "pp", "--alias", "ppa", "--skip-index", cwd=pp, quiet=True)
mg = ("M-4.1.5-4.1.6.yaml", {"id": "M-4.1.5-4.1.6", "from_version": "4.1.5", "to_version": "4.1.6", "description": "x", "breaking": False, "human_gate": "none", "affected_indexes": [], "operations": [{"op": "note", "text": "x"}], "rollback": "r"})
c6 = canonical_copy(sbp.path("c6"), version="4.1.6", supported_from=["4.1.5"], extra_migration=mg)
sbp.gov("release", "build", "--version", "4.1.6", "--canonical", c6, "--out", sbp.path("r6"), "--certification", "CERTIFIED", quiet=True)
k6 = sbp.path("r6", "releases", "4.1.6", "kernel")    # UNSIGNED
o = sbp.gov("update", "--apply", "--source", k6, cwd=pp, quiet=True)
print("[U8] update to an UNSIGNED 4.1.6 on the provisioned machine ->", "ok" if o["ok"] else f"REFUSED {err(o)}")
print("[U8] lock still:", yaml.safe_load(open(os.path.join(pp, "governance/framework.lock")))["version"], "| leftover snapshot dirs:", os.listdir(os.path.join(pp, ".governance-runtime/update")) if os.path.isdir(os.path.join(pp, ".governance-runtime/update")) else [])
o = sbp.gov("update", "--rollback", cwd=pp, quiet=True)
print("[U8] gov update --rollback ->", "ok" if o["ok"] else f"REFUSED {err(o)}", json.dumps({k: (o.get("result") or {}).get(k) for k in ("rolled_back_to", "from")}))
lf = os.path.join(pp, "spec/reports/framework-updates.jsonl")
led = [json.loads(l) for l in open(lf)] if os.path.exists(lf) else []
print("[U8] update ledger events:", [(l.get("event"), l.get("from"), l.get("to"), (l.get("rolled_back_update") or {}).get("to")) for l in led])
print("\nDONE")
