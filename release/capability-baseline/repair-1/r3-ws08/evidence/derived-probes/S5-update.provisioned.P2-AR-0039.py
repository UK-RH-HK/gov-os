#!/usr/bin/env python3
"""DERIVED COPY (P2-AR-0039, WS-8 round 3; WS-8 r2 IP-R2-WS08-13) of release/capability-baseline/audit-0/alpha-r/evidence/
S5-update.py — NOT the audit of record.

Why: OWNER-DECISION-P2-0002 (Option A) refuses external-source kernel ingress on a machine with no trust anchor, so the
audit-of-record S5 stops at [U0] (it installs the shipped 4.1.4 on an unprovisioned machine) in every tree since round 2.
This copy measures the same nine update bullets on a PROVISIONED machine, which is the documented path ("provision, then
install"). Every change from the original is marked `# DERIVED:` and is one of:
  * the machine is provisioned first with the throw-away root of repair-1/r2-ws03/evidence/hc_root.py (published test
    seeds; `human-gate` delegated to the seed-7 key the integration evidence adapter signs relayed human answers with);
  * the shipped 4.1.4 / 4.1.5 kernels are installed from signed copies (same bytes, release metadata signed with the
    root's published-seed release/snapshot/timestamp keys at sequences 14 / 15);
  * [U5] a rollback to 4.1.4 is below this machine's release high-water (15), so it is first shown refused and then run
    under the owner's break-glass authorisation (the root's `recovery` key), as ARCH-0003 §7 / OWNER-DECISION-0006 require;
  * [U7] cannot follow a break-glass restoration on the same machine (OWNER-DECISION-0006 §6 bullet 2 refuses the Human
    Gate it needs below floor), and a release build can no longer mint CERTIFIED (BC-P2-37); it therefore runs on a second
    provisioned machine, signed at sequence 17, with the update's Human Decision Gate answered through the adapter;
  * [U6] the synthetic 4.1.6 is built on a separate build machine (this one is below floor after [U5], where a release
    build is refused, OWNER-DECISION-0006 §6 bullet 3); a refused `update --check` is printed rather than raising;
  * [U8] the machine is provisioned with the same throw-away root (it delegates `human-gate`, so the update's gate can be
    answered — the original's CERTIFIED build waived the gate, and BC-P2-37 now refuses minting CERTIFIED), the unsigned
    synthetic 4.1.6 is built without `--certification CERTIFIED`, the gate is answered through the adapter, and
    leftover snapshots are looked for at the BC-P2-31 location (.governance-state/update/) as well as the legacy one.
Run: ALPHA_R_LIB=<tree>/release/capability-baseline/audit-0/alpha-r/evidence/lib GOV=<gov or adapter> PROBE_TMP=<scratch>
     python3 S5-update.provisioned.P2-AR-0039.py
"""
import os, sys, json, shutil, hashlib, subprocess
sys.path.insert(0, os.environ["ALPHA_R_LIB"])  # DERIVED: the tree-under-test's probe library
from srr_mint import *
import yaml

# DERIVED: provisioning material (test material only; published seeds)
_WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
if not os.path.isdir(os.path.join(_WT, "release/capability-baseline/repair-1/r2-ws03/evidence")):
    _WT = os.environ.get("P2AR0039_WT", _WT)
HC_ROOT = os.path.join(_WT, "release/capability-baseline/repair-1/r2-ws03/evidence/hc_root.py")
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from cryptography.hazmat.primitives import serialization  # noqa: E402


class SeedKey:  # DERIVED: the published-seed keys of tests/certification/srr_material.rs (NOT production keys)
    def __init__(self, seed):
        self.sk = Ed25519PrivateKey.from_private_bytes(bytes([seed]) * 32)
        raw = self.sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.public = raw.hex()
        self.keyid = hashlib.sha256(raw).hexdigest()

    def sign(self, b):
        return self.sk.sign(b).hex()


SREL, SSNAP, STS, SREC = SeedKey(0x21), SeedKey(0x31), SeedKey(0x41), SeedKey(0x51)


def provision(sbx):  # DERIVED
    f = os.path.join(sbx.admin, "root-hc.json")
    subprocess.run([sys.executable, HC_ROOT, f], check=True, capture_output=True)
    o = sbx.gov("trust", "provision", "--anchor", f, cwd=sbx.home, quiet=True)
    print("[prov] machine provisioned with the throw-away root:", o["ok"], (o.get("error") or {}).get("code"))


def signed(sbx, src_kernel, tag, seq):  # DERIVED: the same kernel bytes, with signed release metadata
    d = sbx.path(tag)
    shutil.copytree(src_kernel, os.path.join(d, "kernel"))
    publish(os.path.join(d, "metadata"), release_doc(os.path.join(d, "kernel"), sequence=seq, version=seq), [SREL], [SSNAP], [STS])
    return os.path.join(d, "kernel")


def break_glass(sbx, recovery_kernel, nonce):  # DERIVED: the owner's recovery authorisation, dropped out of band
    inbox = sbx.gov("trust", "break-glass", cwd=sbx.home, quiet=True)["result"]["inbox"]
    mid = sbx.gov("trust", "status", cwd=sbx.home, quiet=True)["result"]["machine_id"]
    doc = break_glass_doc(mid, stage_files(recovery_kernel), nonce)
    open(os.path.join(inbox, nonce + ".json"), "w").write(envelope(doc, [SREC]))


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
sb = Sandbox("s5")
provision(sb)  # DERIVED
R14 = signed(sb, os.path.join(REPO, "release/releases/4.1.4/kernel"), "s14", 14)  # DERIVED: signed shipped 4.1.4
R15 = signed(sb, os.path.join(REPO, "release/releases/4.1.5/kernel"), "s15", 15)  # DERIVED: signed shipped 4.1.5
p = sb.new_repo("proj", {"README.md": "# s5\n", "product/app.py": "def run():\n    return 1\n"})
o = sb.gov("init", "--source", R14, "--name", "s5", "--alias", "s5-a", cwd=p, quiet=True)
print("## [U0] installed 4.1.4:", o["ok"], "| lock version =", yaml.safe_load(open(os.path.join(p, "governance/framework.lock")))["version"], "| authenticity =", (o.get("result") or {}).get("release_authenticity", {}).get("authenticity"))
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
print("[U2] apply after the gate:", o["ok"], "| applied =", r.get("applied"), "| from", r.get("from"), "to", r.get("to"), "|", (o.get("error") or {}).get("code"))
det = r.get("details") or {}
print("[U2] migrations =", det.get("migrations"), "| operations =", json.dumps(det.get("operations"))[:300])
print("[U2] overlay_keys_changed =", det.get("overlay_keys_changed"), "| overlay_reconciled =", det.get("overlay_reconciled"))
print("[U2] index_manifest =", det.get("index_manifest"), "| doctor =", det.get("doctor"), "| audit =", det.get("audit"), "| lock =", det.get("lock"))
print("[U2] release_authenticity =", (det.get("release_authenticity") or {}).get("authenticity"), "| remedied_blocks =", [b.get("check") for b in det.get("remedied_blocks") or []])
snaps_state = os.path.join(p, ".governance-state/update"); snaps_legacy = os.path.join(p, ".governance-runtime/update")
print("[U2] rollback snapshot at the BC-P2-31 location:", sorted(os.listdir(snaps_state)) if os.path.isdir(snaps_state) else [], "| at the legacy location:", sorted(os.listdir(snaps_legacy)) if os.path.isdir(snaps_legacy) else [])  # DERIVED

print("\n## [U3] overlay preserved / spec untouched / adapters regenerated / indexes rebuilt")
y2 = yaml.safe_load(open(PP))
print("[U3] customised overlay values kept: name =", y2["project"]["name"], "| override =", y2.get("policy_overrides"), "| DATA_SENSITIVITY =", yaml.safe_load(open(DS))["classifications"])
chg = subprocess.run(["git", "status", "--porcelain", "--", "spec"], cwd=p, capture_output=True, text=True).stdout.splitlines()
print("[U3] spec/ changes since the pre-update commit (git status):", chg)
print("[U3] pre-existing governed records unchanged: D-0001 =", yaml.safe_load(open(os.path.join(p, "spec/decisions/D-0001.yaml"))), "| git diff on committed spec files:", subprocess.run(["git", "diff", "--stat", "--", "spec"], cwd=p, capture_output=True, text=True).stdout.strip() or "(none)")
ad = json.load(open(os.path.join(p, "governance/generated/adapter-manifest.json")))
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
print("[U5] rollback below the release high-water without the owner's authorisation:", "ok" if o["ok"] else f"REFUSED {err(o)}")  # DERIVED
break_glass(sb, R14, "s5-rollback")  # DERIVED
o = sb.gov("update", "--rollback", "--break-glass", "--reason", "probe rollback", cwd=p, quiet=True)  # DERIVED: --break-glass
r = o.get("result") or {}
print("[U5] rollback:", o["ok"], "| rolled_back_to =", r.get("rolled_back_to"), "| kernel_ok =", r.get("kernel_ok"), "| doctor =", r.get("doctor"), "| error =", (o.get("error") or {}).get("code"))
print("[U5] overlay byte-identical to pre-update:", open(PP).read() == ov_before, "| lock version =", yaml.safe_load(open(os.path.join(p, "governance/framework.lock")))["version"])
led = [json.loads(l) for l in open(os.path.join(p, "spec/reports/framework-updates.jsonl"))]
print("[U5] ledger rollback entry:", json.dumps({k: led[-1].get(k) for k in ("event", "from", "to", "rolled_back_update", "authority_level", "reason", "resulting_lock", "verification")})[:500])
o = sb.gov("update", "--rollback", "--break-glass", cwd=p, quiet=True)
print("[U5] second rollback:", "ok" if o["ok"] else f"REFUSED {err(o)}")
st = sb.gov("trust", "status", cwd=sb.home, quiet=True)["result"]  # DERIVED
print("[U5] machine marked below floor after the restoration:", (st.get("degraded") or {}).get("marking"))  # DERIVED

print("\n## [U6] compatibility: unsupported path; downgrade")
c16 = canonical_copy(sb.path("c16"), version="4.1.6", supported_from=["4.1.3"])
sbb = Sandbox("s5-build")  # DERIVED: this machine is now below floor, where a release build is refused (OWNER-DECISION-0006 §6 bullet 3)
bb = sbb.gov("release", "build", "--version", "4.1.6", "--canonical", c16, "--out", sb.path("r16"), quiet=True)  # DERIVED: built on sbb
print("[U6] synthetic 4.1.6 (supports only 4.1.3) built on a separate build machine:", bb["ok"], (bb.get("error") or {}).get("code"))
k16 = sb.path("r16", "releases", "4.1.6", "kernel")
oc = sb.gov("update", "--check", "--source", k16, cwd=p, quiet=True)  # DERIVED: a refusal is printed, not a KeyError
c = oc.get("result") or {}
print("[U6] 4.1.4 -> 4.1.6 (supports only 4.1.3): compatible =", c.get("compatible"), "| migration_path_complete =", c.get("migration_path_complete"), "|", "" if oc["ok"] else f"REFUSED {err(oc)}: {oc['error']['message'][:200]}")
o = sb.gov("update", "--apply", "--source", k16, "--approve", cwd=p, quiet=True)
print("[U6] apply ->", "ok " + json.dumps(o["result"])[:160] if o["ok"] else f"REFUSED {err(o)}")
oc = sb.gov("update", "--check", "--source", os.path.join(REPO, "release/releases/4.1.3/kernel"), cwd=p, quiet=True)  # DERIVED: as above
c = oc.get("result") or {}
print("[U6] 4.1.4 -> 4.1.3 (downgrade): up_to_date =", c.get("up_to_date"), "| downgrade =", c.get("downgrade"), "| recommendation =", c.get("recommendation"), "|", "" if oc["ok"] else f"REFUSED {err(oc)}: {oc['error']['message'][:200]}")

print("\n## [U7] automatic transaction rollback when post-install verification fails (DERIVED: a second provisioned machine)")
sb7 = Sandbox("s5-u7"); provision(sb7)  # DERIVED
R14b = signed(sb7, os.path.join(REPO, "release/releases/4.1.4/kernel"), "s14", 14)  # DERIVED
p7 = sb7.new_repo("proj7", {"README.md": "# s5 u7\n"})
sb7.gov("init", "--source", R14b, "--name", "s5u7", "--alias", "s5-u7", cwd=p7, quiet=True)
sb7.git(p7, "add", "-A"); sb7.git(p7, "commit", "-q", "-m", "installed")
mig = ("M-4.1.4-4.1.7.yaml", {"id": "M-4.1.4-4.1.7", "from_version": "4.1.4", "to_version": "4.1.7", "description": "breaks the overlay",
       "breaking": False, "human_gate": "none", "affected_indexes": [], "overlay_template_changes": [],
       "operations": [{"op": "set_overlay_key", "file": "PROJECT_POLICY.yaml", "key": "schema_version", "value": 12345}], "rollback": "gov update --rollback"})
c17 = canonical_copy(sb7.path("c17"), version="4.1.7", supported_from=["4.1.4"], extra_migration=mig, mutate=lambda dd: os.remove(os.path.join(dd, "migrations", "M-4.1.4-4.1.5.yaml")))
b17 = sb7.gov("release", "build", "--version", "4.1.7", "--canonical", c17, "--out", sb7.path("r17"), "--certification", "READY_FOR_INDEPENDENT_REVERIFICATION", quiet=True)  # DERIVED: no CERTIFIED (BC-P2-37)
print("[U7] synthetic 4.1.7 built:", b17["ok"], (b17.get("error") or {}).get("message", "")[:200])
k17 = sb7.path("r17", "releases", "4.1.7", "kernel")
publish(sb7.path("r17", "releases", "4.1.7", "metadata"), release_doc(k17, sequence=17, version=17), [SREL], [SSNAP], [STS])  # DERIVED: signed
kh_before = tree_hash(os.path.join(p7, "governance/kernel")); lock_before = open(os.path.join(p7, "governance/framework.lock")).read()
o = sb7.gov("update", "--apply", "--source", k17, cwd=p7, quiet=True)
g7 = (o.get("error") or {}).get("details", {}).get("gate")  # DERIVED: answer the update's gate through the adapter
if g7:
    sb7.gov("gate", "present", g7, cwd=p7, quiet=True); sb7.gov("decide", g7, "--option", "A", "--by", "product-owner", role="human", cwd=p7, quiet=True)
    o = sb7.gov("update", "--apply", "--source", k17, "--approve", "--by", "product-owner", cwd=p7, quiet=True)
print("[U7] apply ->", "ok " + json.dumps(o["result"])[:200] if o["ok"] else f"REFUSED {err(o)}: {o['error']['message'][:200]}")
print("[U7] kernel restored:", tree_hash(os.path.join(p7, "governance/kernel")) == kh_before, "| lock restored:", open(os.path.join(p7, "governance/framework.lock")).read() == lock_before)
led = [json.loads(l) for l in open(os.path.join(p7, "spec/reports/framework-updates.jsonl"))]
print("[U7] last ledger entry:", json.dumps({k: led[-1].get(k) for k in ("event", "from", "to", "reason", "result")})[:300])

print("\n## [U8] PROVISIONED machine: refused update leaves its pre-admission snapshot; `update --rollback` then 'rolls back' an update that never happened")
sbp = Sandbox("s5-prov")
provision(sbp)  # DERIVED: the throw-away root with a `human-gate` delegation, so the update's gate can be answered
cc = canonical_copy(sbp.path("cc"), version="4.1.5"); sbp.gov("release", "build", "--version", "4.1.5", "--canonical", cc, "--out", sbp.path("rel"), quiet=True)  # DERIVED: version="4.1.5" (HEAD is 4.1.6)
kk = sbp.path("rel", "releases", "4.1.5", "kernel"); publish(sbp.path("rel", "releases", "4.1.5", "metadata"), release_doc(kk, sequence=10, version=1), [SREL], [SSNAP], [STS])  # DERIVED: that root's keys
pp = sbp.new_repo("pp"); sbp.gov("init", "--source", kk, "--name", "pp", "--alias", "ppa", "--skip-index", cwd=pp, quiet=True)
mg = ("M-4.1.5-4.1.6.yaml", {"id": "M-4.1.5-4.1.6", "from_version": "4.1.5", "to_version": "4.1.6", "description": "x", "breaking": False, "human_gate": "none", "affected_indexes": [], "operations": [{"op": "note", "text": "x"}], "rollback": "r"})
c6 = canonical_copy(sbp.path("c6"), version="4.1.6", supported_from=["4.1.5"], extra_migration=mg)
b6 = sbp.gov("release", "build", "--version", "4.1.6", "--canonical", c6, "--out", sbp.path("r6"), "--certification", "READY_FOR_INDEPENDENT_REVERIFICATION", quiet=True)  # DERIVED: no CERTIFIED (BC-P2-37 refuses minting it)
print("[U8] unsigned synthetic 4.1.6 built:", b6["ok"], (b6.get("error") or {}).get("code"))  # DERIVED
k6 = sbp.path("r6", "releases", "4.1.6", "kernel")    # UNSIGNED
o = sbp.gov("update", "--apply", "--source", k6, cwd=pp, quiet=True)
g8 = (o.get("error") or {}).get("details", {}).get("gate")  # DERIVED: an uncertified target needs the gate first (the original's CERTIFIED waived it)
if g8:
    sbp.gov("gate", "present", g8, cwd=pp, quiet=True); sbp.gov("decide", g8, "--option", "A", "--by", "product-owner", role="human", cwd=pp, quiet=True)
    o = sbp.gov("update", "--apply", "--source", k6, "--approve", "--by", "product-owner", cwd=pp, quiet=True)
print("[U8] update to an UNSIGNED 4.1.6 on the provisioned machine ->", "ok" if o["ok"] else f"REFUSED {err(o)}")
left = {d: (sorted(os.listdir(os.path.join(pp, d))) if os.path.isdir(os.path.join(pp, d)) else []) for d in (".governance-runtime/update", ".governance-state/update")}  # DERIVED: both locations
print("[U8] lock still:", yaml.safe_load(open(os.path.join(pp, "governance/framework.lock")))["version"], "| leftover snapshot dirs:", left)
o = sbp.gov("update", "--rollback", cwd=pp, quiet=True)
print("[U8] gov update --rollback ->", "ok" if o["ok"] else f"REFUSED {err(o)}", json.dumps({k: (o.get("result") or {}).get(k) for k in ("rolled_back_to", "from")}))
lf = os.path.join(pp, "spec/reports/framework-updates.jsonl")
led = [json.loads(l) for l in open(lf)] if os.path.exists(lf) else []
print("[U8] update ledger events:", [(l.get("event"), l.get("from"), l.get("to"), (l.get("rolled_back_update") or {}).get("to")) for l in led])
print("\nDONE")
