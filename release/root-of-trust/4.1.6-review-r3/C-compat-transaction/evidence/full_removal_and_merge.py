#!/usr/bin/env python3
"""(A) Full occupation removal (incl framework.lock dir) + legacy install-over, governance/trust kept: does the legacy
binary fully install & operate & expose restricted material while governance/trust persists?
(B) Divergent dir/file merge: a legacy branch updates governance/kernel/ (dir) after the fork; rot-1 main makes it a
file. Merge. Observe resulting types and whether a legacy binary treats the merged tree as installed and mutates."""
import json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import yaml


def trust_digest(root):
    p = root + "/governance/trust"
    return digest(file_map(p, False)) if os.path.isdir(p) else "<absent>"


def is_installed(root):
    return os.path.exists(root + "/governance/framework.lock") and not os.path.isdir(root + "/governance/framework.lock") and os.path.exists(root + "/governance/kernel/KERNEL_MANIFEST.json")


def restr(p):
    try:
        return any(x.get("pattern") == "product/restricted-plan.md" for x in (yaml.safe_load(open(p)).get("classifications") or []))
    except Exception:
        return None


def A_full_removal(scratch, L3):
    d = os.path.join(scratch, "wcA"); git(scratch, "clone", "-q", L3, d); env = child_env(scratch, "wcA")
    # remove ALL occupation entries (kernel/project/generated files + framework.lock dir + adoption + migration)
    git(d, "rm", "-q", "-r", "governance/kernel", "governance/project", "governance/generated",
        "governance/framework.lock", "spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/migration")
    git(d, "commit", "-q", "-m", "cleanup weird files")
    tb = trust_digest(d)
    r = gov(BINS["4.1.5"], d, ["init", "--force", "--name", "x", "--skip-index"], env)
    ta = trust_digest(d)
    q = gov(BINS["4.1.5"], d, ["rebuild-memory"], env)
    mq = gov(BINS["4.1.5"], d, ["memory", "query", MARK], env)
    hits = [h.get("path") for h in ((mq.get("result") or {}).get("hits") or []) if "restricted-plan" in (h.get("path") or "")]
    kt = gov(BINS["4.1.5"], d, ["kernel", "trust"], env)
    return {"trust_present_after": os.path.isdir(d + "/governance/trust"), "governance_trust_mutated": tb != ta,
            "init_ok": r.get("ok"), "init_code": code(r), "legacy_is_installed_after": is_installed(d),
            "rebuild_ok": q.get("ok"), "restricted_retrievable_by_legacy": hits,
            "legacy_kernel_trust_verified": (kt.get("result") or {}).get("verified"),
            "rot1_overlay_still_has_restriction": restr(d + "/governance/overlay/DATA_SENSITIVITY.yaml"),
            "rot1_verdict": "PARTIAL(occupation)->fail-closed (occupation absent, trust present)" if os.path.isdir(d + "/governance/trust") else "ABSENT/LEGACY"}


def B_divergent_merge(scratch, base, L3):
    # Build a legacy branch from the pre-migration commit that ALSO modifies governance/kernel (a legacy kernel edit),
    # then attempt to merge it into the rot-1 main (where governance/kernel is a FILE).
    d = os.path.join(scratch, "wcB"); git(scratch, "clone", "-q", L3, d); env = child_env(scratch, "wcB")
    git(d, "checkout", "-q", "-b", "legacy", "HEAD~1")  # legacy layout: kernel is a dir
    open(d + "/governance/kernel/MARKER.txt", "w").write("legacy kernel edit\n")
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "legacy kernel edit (dir)")
    git(d, "checkout", "-q", "main")
    m = git(d, "merge", "--no-edit", "-m", "merge legacy", "legacy", check=False)
    types = {}
    for p in ("governance/kernel", "governance/framework.lock", "governance/trust", "governance/kernel/KERNEL_MANIFEST.json"):
        fp = d + "/" + p
        types[p] = ("dir" if os.path.isdir(fp) else "file" if os.path.isfile(fp) else "link" if os.path.islink(fp) else "absent")
    # run legacy remedy on whatever merged state resulted (abort leaves index conflicted)
    tb = trust_digest(d)
    r = gov(BINS["4.1.5"], d, ["update", "--rollback", "--reason", "d"], env)
    rr = gov(BINS["4.1.5"], d, ["init", "--force", "--name", "x", "--skip-index"], env)
    ta = trust_digest(d)
    return {"merge_rc": m.returncode, "merge_out": (m.stdout + m.stderr)[-500:], "types_after_merge": types,
            "legacy_is_installed": is_installed(d), "governance_trust_mutated": tb != ta,
            "legacy_update_rollback": {"ok": r.get("ok"), "code": code(r)},
            "legacy_init_force": {"ok": rr.get("ok"), "code": code(rr)}}


def main():
    scratch = os.path.abspath(sys.argv[1]); base = sys.argv[2]; L3 = sys.argv[3]
    os.makedirs(scratch, exist_ok=True)
    print(json.dumps({"A_full_removal": A_full_removal(scratch, L3),
                      "B_divergent_dirfile_merge": B_divergent_merge(scratch, base, L3)}, indent=1))


if __name__ == "__main__":
    main()
