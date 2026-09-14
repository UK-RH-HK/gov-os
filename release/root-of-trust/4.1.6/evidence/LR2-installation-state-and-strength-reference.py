#!/usr/bin/env python3
"""LR2 — reference evaluation of the RoT-1 installation state (`18` §9) and of the project-strength vector (`26` §6) on the
real trees that the legacy-binary probes leave behind (RV3-M6 / C-1; RV3-D-A05, A06, A07; RV3-L7).

No RoT-1 binary exists. This script applies the architecture's state machine and the revision-4 overlay strength vector
(`constitutional-surface/csi_lib.py`) to trees produced by the real 4.1.5 binary and real Git in the re-runs of reviewer C's
and synthesis D's probes. It answers the two bounds residual LR-2 keeps: (1) does a RoT-1 binary fail closed on the
resulting tree (never COMPLETE with a legacy install beside it), and (2) is an overlay classification removed by a legacy
CIT reported as PROJECT_STRENGTH_WEAKENED on a machine that recorded the vector.

Read-only over the trees (Git is used only for `git show HEAD:<path>`). Input: a JSON file mapping labels to
{"tree": <dir>, "recorded_from_head": true|false}. Output: JSON on stdout with scratch paths replaced by <scratch>.
Usage: python3 LR2-installation-state-and-strength-reference.py <spec.json> [<scratch-root-for-placeholders>]
"""
import json, os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "constitutional-surface"))
import csi_lib as L  # noqa: E402

INV = yaml.safe_load(open(os.path.join(HERE, "..", "constitutional-surface", "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
OCCUPATION = {"governance/kernel": "file", "governance/project": "file", "governance/generated": "file", "governance/framework.lock": "dir",
              "spec/audits/GOVERNANCE-ADOPTION": "file", ".governance-runtime/migration": "file"}
TRUST_REQUIRED = ["governance/trust/FORMAT", "governance/trust/framework.lock", "governance/trust/kernel"]
STRAY = ["governance/framework.lock~legacy", "governance/kernel/KERNEL_MANIFEST.json", "governance/project/DATA_SENSITIVITY.yaml"]


def kind(p):
    if os.path.islink(p):
        return "link"
    if os.path.isdir(p):
        return "dir"
    if os.path.isfile(p):
        return "file"
    return "absent"


def installation_state(root):
    """`18` §9 revision 4, evaluated on the tree (occupation entries compared by entry type, never by name: C-4)."""
    occ = {p: kind(os.path.join(root, p)) for p in OCCUPATION}
    trust_present = os.path.isdir(os.path.join(root, "governance/trust"))
    trust_complete = trust_present and all(os.path.exists(os.path.join(root, p)) for p in TRUST_REQUIRED)
    legacy_entries = occ["governance/framework.lock"] == "file" or occ["governance/kernel"] == "dir"
    wrong = {p: {"expected": t, "observed": occ[p]} for p, t in OCCUPATION.items() if occ[p] != t}
    stray = [p for p in STRAY if os.path.exists(os.path.join(root, p))]
    if not trust_present and all(v == "absent" for v in occ.values()):
        state = "ABSENT"
    elif legacy_entries and not trust_present:
        state = "LEGACY"
    elif trust_complete and not wrong:
        state = "COMPLETE"
    else:
        state = "PARTIAL(occupation)" if trust_present else "PARTIAL(mixed)"
    return {"state": state, "governance_trust_present": trust_present, "legacy_entries_present": legacy_entries, "occupation_missing_or_retyped": wrong,
            "stray_legacy_artefacts_named_by_doctor": stray,
            "rot1_policy_root": "KernelSnapshot if verified and eligible" if state == "COMPLETE" else "EmbeddedSnapshot joined with floors (fail closed)",
            "rot1_mutations": "per verdict and freshness" if state == "COMPLETE" else "refused INSTALL_STATE_PARTIAL / INSTALL_STATE_LEGACY; doctor D033 CRITICAL names the mixed layout"}


def overlay_docs_worktree(root):
    od = os.path.join(root, "governance", "overlay")
    docs = {}
    if not os.path.isdir(od):
        return docs
    for dp, dns, fns in os.walk(od):
        dns.sort()
        for fn in sorted(fns):
            if fn.endswith(".yaml"):
                try:
                    docs[os.path.relpath(os.path.join(dp, fn), od).replace(os.sep, "/")] = yaml.safe_load(open(os.path.join(dp, fn)))
                except Exception as e:
                    docs[os.path.relpath(os.path.join(dp, fn), od).replace(os.sep, "/")] = {"$unparseable": str(e)}
    return docs


def overlay_docs_head(root):
    env = {"PATH": "/usr/bin:/bin", "HOME": root}
    ls = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "governance/overlay"], cwd=root, capture_output=True, text=True, env=env)
    docs = {}
    for path in ls.stdout.splitlines():
        if path.endswith(".yaml"):
            show = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=root, capture_output=True, text=True, env=env)
            docs[path[len("governance/overlay/"):]] = yaml.safe_load(show.stdout)
    return docs


def main():
    spec = json.load(open(sys.argv[1]))
    scratch = sys.argv[2] if len(sys.argv) > 2 else None
    out = {"inventory_overlay_surface_files": [f.get("path") or f.get("glob") for f in INV["overlay_surface"]["files"]], "trees": {}}
    for label, item in spec.items():
        root = item["tree"]
        row = {"exists": os.path.isdir(root)}
        if row["exists"]:
            row["installation_state"] = installation_state(root)
            if item.get("recorded_from_head"):
                recorded = overlay_docs_head(root)
                current = overlay_docs_worktree(root)
                reqs = L.strength_requirements(INV, recorded, {}, {})
                fails = L.strength_failures(INV, reqs, current, {})
                row["project_strength"] = {"recorded_on": "the committed overlay at HEAD (the machine's last recorded vector)", "requirements": len(reqs),
                                           "failures": fails, "PROJECT_STRENGTH_WEAKENED": bool(fails)}
        out["trees"][label] = row
    text = json.dumps(out, indent=1, default=str)
    if scratch:
        text = text.replace(scratch, "<scratch>")
    print(text)


if __name__ == "__main__":
    main()
