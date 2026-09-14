#!/usr/bin/env python3
"""RV3-C occupation-removal + legacy install-over. Realistic trigger: an ordinary user deletes the inscrutable
sentinel files governance/{kernel,project,generated} (no extension, one line of 'cannot-operate' text) while
governance/trust/ persists. Then a teammate on a legacy binary runs init --force. Does a legacy-valid state result,
and is governance/trust mutated? Is the restricted classification exposed by the legacy binary afterwards?"""
import json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import *


def trust_map(root):
    p = root + "/governance/trust"
    return file_map(p, False) if os.path.isdir(p) else {}


def is_installed(root):
    return os.path.exists(root + "/governance/framework.lock") and os.path.exists(root + "/governance/kernel/KERNEL_MANIFEST.json")


def main():
    scratch = os.path.abspath(sys.argv[1]); L3 = sys.argv[2]
    os.makedirs(scratch, exist_ok=True)
    out = {}

    # Fresh clone of the RoT-1 project
    d = os.path.join(scratch, "wc")
    git(scratch, "clone", "-q", L3, d)
    env = child_env(scratch, "wc")

    # STEP 1: ordinary user deletes the three inscrutable sentinel files (git rm)
    git(d, "rm", "-q", "governance/kernel", "governance/project", "governance/generated")
    git(d, "commit", "-q", "-m", "remove strange leftover files")
    out["after_deletion"] = {"trust_present": os.path.isdir(d + "/governance/trust"),
                             "trust_digest": digest(trust_map(d)),
                             "legacy_is_installed": is_installed(d)}
    tb = digest(trust_map(d))

    # STEP 2: teammate on a legacy binary runs init --force (a documented reinstall remedy)
    r = gov(BINS["4.1.5"], d, ["init", "--force", "--name", "x", "--skip-index"], env)
    ta = digest(trust_map(d))
    out["legacy_init_force"] = {"ok": r.get("ok"), "code": code(r),
                                "governance_trust_mutated": tb != ta,
                                "legacy_is_installed_after": is_installed(d),
                                "kernel_manifest_created": os.path.exists(d + "/governance/kernel/KERNEL_MANIFEST.json"),
                                "fresh_overlay_DATA_SENSITIVITY_present": os.path.exists(d + "/governance/project/DATA_SENSITIVITY.yaml")}

    # STEP 3: a subsequent legacy command now treats it as installed and operates; does it expose restricted material?
    q = gov(BINS["4.1.5"], d, ["rebuild-memory"], env)
    mq = gov(BINS["4.1.5"], d, ["memory", "query", MARK], env)
    hits = [h.get("path") for h in ((mq.get("result") or {}).get("hits") or []) if "restricted-plan" in (h.get("path") or "")]
    kt = gov(BINS["4.1.5"], d, ["kernel", "trust"], env)
    out["legacy_operates_after"] = {"rebuild_ok": q.get("ok"), "memory_query_ok": mq.get("ok"),
                                    "restricted_plan_retrievable_by_legacy": hits,
                                    "legacy_kernel_trust_verified": (kt.get("result") or {}).get("verified"),
                                    "rot1_overlay_still_has_restriction": _restr(d + "/governance/overlay/DATA_SENSITIVITY.yaml"),
                                    "legacy_overlay_has_restriction": _restr(d + "/governance/project/DATA_SENSITIVITY.yaml")}
    # STEP 4: what does the RoT-1 installation-state machine see? (emulate doc 18 §9 COMPLETE precondition)
    occ_present = all(os.path.lexists(d + "/governance/" + p) for p in ("kernel", "project", "generated"))
    out["rot1_state_machine_emulation"] = {"occupation_all_present": occ_present,
                                           "governance_trust_present": os.path.isdir(d + "/governance/trust"),
                                           "verdict": "PARTIAL(occupation)->fail-closed" if not occ_present else "COMPLETE"}
    print(json.dumps(out, indent=1))


def _restr(p):
    try:
        import yaml
        return any(x.get("pattern") == "product/restricted-plan.md" for x in (yaml.safe_load(open(p)).get("classifications") or []))
    except Exception:
        return None


if __name__ == "__main__":
    main()
