#!/usr/bin/env python3
"""Build a real legacy 4.1.5 base project and commit it. Then construct the RoT-1 rev3 L3 occupation layout as the
architecture specifies (08 §2, 26 §2). Emits base dir + layout dir paths. Independent of the architect's harness."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import yaml


def build_base(scratch):
    root = os.path.join(scratch, "base")
    os.makedirs(root)
    env = child_env(scratch, "base")
    git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "empty")
    b = {}
    b["init_4.1.4"] = gov(BINS["4.1.5"], root, ["init", "--source", REPO + "/release/releases/4.1.4", "--name", "ar3", "--skip-index"], env).get("ok")
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "4.1.4 install")
    first = gov(BINS["4.1.5"], root, ["update", "--apply", "--source", REPO + "/release/releases/4.1.5"], env)
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    gov(BINS["4.1.5"], root, ["gate", "present", gid], env)
    gov(BINS["4.1.5"], root, ["decide", gid, "--option", "A", "--by", "owner"], env)
    ap = gov(BINS["4.1.5"], root, ["update", "--apply", "--approve", "--source", REPO + "/release/releases/4.1.5"], env)
    b["update_to_4.1.5"] = (ap.get("result") or ap).get("applied") if isinstance(ap.get("result"), dict) else ap.get("applied") if "applied" in ap else ap.get("ok")
    b["legacy_snapshot_present"] = os.path.exists(root + "/.governance-runtime/update/4.1.5/snapshot.json")
    # restricted classification added AFTER the update (project-owned strengthening)
    os.makedirs(root + "/product", exist_ok=True)
    open(root + "/product/restricted-plan.md", "w").write(f"# Plan\n\n{MARK} proprietary customer terms\n")
    dsp = root + "/governance/project/DATA_SENSITIVITY.yaml"
    ds = yaml.safe_load(open(dsp)) if os.path.exists(dsp) else {"schema_version": "1.0.0", "classifications": []}
    ds.setdefault("classifications", []).append({"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"})
    yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "restricted classification")
    b["kernel_trust_verified"] = (gov(BINS["4.1.5"], root, ["kernel", "trust"], env).get("result") or {}).get("verified")
    return root, b


def to_L3(scratch, base):
    """Legacy-path-occupation layout, committed as the RoT-1 migration commit ON TOP of the legacy history."""
    dst = os.path.join(scratch, "L3")
    shutil.copytree(base, dst, symlinks=True)
    g = dst + "/governance"
    os.makedirs(g + "/trust/state", exist_ok=True)
    shutil.move(g + "/kernel", g + "/trust/kernel")
    os.remove(g + "/trust/kernel/KERNEL_MANIFEST.json")  # RoT-1 has no legacy manifest
    lock = yaml.safe_load(open(g + "/framework.lock"))
    os.remove(g + "/framework.lock")
    rot_lock = {"lock_schema_version": "3.0.0", "trust_format": "rot-1", "layout": "legacy-path-occupation-v1",
                "framework": lock.get("framework"), "version": "4.1.6", "release_statement_digest": "sha256:" + "a" * 64,
                "kernel": {"tree_digest": "sha256:" + "0" * 64}}
    json.dump(rot_lock, open(g + "/trust/framework.lock", "w"), indent=1, sort_keys=True)
    open(g + "/trust/FORMAT", "w").write('{"layout":"legacy-path-occupation-v1","minimum_reader":"4.1.6","trust_format":"rot-1"}')
    shutil.copy(REPO + "/release/root-of-trust/4.1.6/examples/rev2/release-final.dsse.json", g + "/trust/release.dsse.json")
    shutil.copy(REPO + "/release/root-of-trust/4.1.6/examples/rev2/trust-state.1.dsse.json", g + "/trust/state/1.dsse.json")
    shutil.move(g + "/project", g + "/overlay")
    if os.path.isdir(g + "/generated"):
        shutil.move(g + "/generated", g + "/views")
    # occupation entries (wrong types)
    os.makedirs(g + "/framework.lock")
    open(g + "/framework.lock/ROT-1-TRUST-FORMAT", "w").write(SENT + "\n")
    for p in ("kernel", "project", "generated"):
        open(g + "/" + p, "w").write(SENT + "\n")
    if os.path.isdir(dst + "/spec/audits/GOVERNANCE-ADOPTION"):
        shutil.move(dst + "/spec/audits/GOVERNANCE-ADOPTION", dst + "/spec/audits/ADOPTION")
    os.makedirs(dst + "/spec/audits", exist_ok=True)
    open(dst + "/spec/audits/GOVERNANCE-ADOPTION", "w").write(SENT + "\n")
    os.makedirs(dst + "/.governance-runtime", exist_ok=True)
    open(dst + "/.governance-runtime/migration", "w").write(SENT + "\n")
    git(dst, "add", "-A"); git(dst, "add", "-f", ".governance-runtime/migration")
    git(dst, "commit", "-q", "-m", "rot-1 revision-3 layout (migration commit)")
    return dst


if __name__ == "__main__":
    scratch = sys.argv[1]
    os.makedirs(scratch, exist_ok=False)
    base, b = build_base(scratch)
    L3 = to_L3(scratch, base)
    print(json.dumps({"base": base, "L3": L3, "base_info": b,
                      "L3_governance_entries": sorted(os.listdir(L3 + "/governance")),
                      "L3_tree_digest": digest(file_map(L3))}, indent=1))
