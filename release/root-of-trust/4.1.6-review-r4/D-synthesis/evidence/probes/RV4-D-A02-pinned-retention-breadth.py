#!/usr/bin/env python3
"""RV4-D-A02 (review r4 synthesis D, AR-0008) — class breadth of RV4-B-H3 beyond the one secret-pattern leaf B executed.

RV4-B-H3: a Trust Policy that keeps a superseded digest beside a fixed one lets a threshold-1 `release-final` restore the
superseded content in a higher-sequence release, with no reduction, gate or detector. B executed it for
`SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex` (a `pinned` leaf). This probe asks whether the same
holds, with the pack's unmodified checker and library, for the other registration shapes the draft TPS v1 uses:

  T1  a `pinned` keyed-collection member registered as a whole: `TOOLS_REGISTRY.tools[tool_id=TOOL-GIT-001]` (a tool
      descriptor whose install and health commands `gov` executes);
  T2  a `pinned` keyed-collection member: `HARD_INVARIANTS.invariants[id=INV-001]` (copied into agent adapters);
  T3  a `pinned_file` path under a glob rule: one file matched by `schemas/*.schema.json`;
  T4  a `pinned_file` path under a glob rule: one file matched by `skills/SKL-*.yaml` (agent-facing instructions).

For each target: K_fix = framework kernel with the target changed (the "fix"); its digest is read from the checker's own
violation report under TPS v1. TPS v2 RETAIN registers [old, fixed]; TPS v2 ONLY registers [fixed]. The mixed release
(higher sequence) carries every other fix and the OLD content of the target. Checks: `check` exits, `reductions` exits
(v1→RETAIN; ONLY→RETAIN, i.e. re-adding a superseded digest). No files outside the scratch directory given.
Usage: RV4-D-A02-pinned-retention-breadth.py <worktree> <scratch-dir>
"""
import copy, glob, json, os, shutil, sys

import yaml

sys.dont_write_bytecode = True
WT, SCR = sys.argv[1], sys.argv[2]
CS = os.path.join(WT, "release/root-of-trust/4.1.6/constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

FW = os.path.join(WT, "framework")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
os.makedirs(SCR, exist_ok=True)


REL_TOOLS = os.path.join(WT, "release/releases/4.1.5/kernel/tools")


def kcopy(name):
    """framework/ plus the optional tools/ registry of the 4.1.5 payload (the draft TPS v1 registers its members)."""
    d = os.path.join(SCR, "k", name)
    if os.path.exists(d):
        shutil.move(d, d + ".old-" + str(len(glob.glob(d + ".old-*"))))
    shutil.copytree(FW, d)
    if not os.path.exists(os.path.join(d, "tools")):
        shutil.copytree(REL_TOOLS, os.path.join(d, "tools"))
    return d


def ymut(kdir, rel, fn):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    fn(d)
    C.ydump(p, d)


def schema_target():
    return sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "schemas/*.schema.json")))[0]


def skill_target():
    return sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "skills/SKL-*.yaml")))[0]


SCHEMA, SKILL = schema_target(), skill_target()


def fix_tool(k):
    ymut(k, "tools/registry/TOOLS.yaml", lambda d: [t.__setitem__("probe_fixed_note", "4.1.7 fix: health command hardened") for t in d["tools"] if t["tool_id"] == "TOOL-GIT-001"])


def fix_invariant(k):
    ymut(k, "constitution/HARD_INVARIANTS.yaml", lambda d: [i.__setitem__("statement", str(i.get("statement", "")) + " (4.1.7 clarification)") for i in d["invariants"] if i["id"] == "INV-001"])


def fix_schema(k):
    p = os.path.join(k, SCHEMA)
    j = json.load(open(p))
    j["$comment"] = "4.1.7 fix: additionalProperties tightened"
    json.dump(j, open(p, "w"), indent=2)


def fix_skill(k):
    ymut(k, SKILL, lambda d: d.__setitem__("probe_fixed_note", "4.1.7 fix: instruction corrected") if isinstance(d, dict) else None)


TARGETS = {
    "T1_tool_descriptor_member": {"fix": fix_tool, "match": lambda v: v.get("class") == "pinned" and "TOOL-GIT-001" in str(v.get("key"))},
    "T2_hard_invariant_member": {"fix": fix_invariant, "match": lambda v: v.get("class") == "pinned" and "INV-001" in str(v.get("key"))},
    "T3_schema_pinned_file": {"fix": fix_schema, "match": lambda v: v.get("class") == "pinned_file" and v.get("file") == SCHEMA},
    "T4_skill_pinned_file": {"fix": fix_skill, "match": lambda v: v.get("class") == "pinned_file" and v.get("file") == SKILL},
}


def registration_slot(inv, viol):
    """Locate the digest list the checker compared for this violation (leaf-rule digests dict, or glob-rule digests dict)."""
    for f in inv["files"]:
        if viol.get("class") == "pinned_file" and isinstance(f.get("digests"), dict) and viol["file"] in f["digests"]:
            return f["digests"], viol["file"]
        for lr in f.get("leaves") or []:
            if isinstance(lr.get("digests"), dict) and viol.get("key") in lr["digests"]:
                return lr["digests"], viol["key"]
    return None, None


out = {"probe": "RV4-D-A02", "checker": "csi_check.py run_check / run_reductions (revision 4, unmodified)", "targets": {}}
fixes = {}
for name, t in TARGETS.items():
    k = kcopy("fix-" + name)
    t["fix"](k)
    r = C.run_check(k, INV, quiet=True)
    v = [x for x in r.get("violations", []) if t["match"](x)]
    if not v:
        out["targets"][name] = {"error": "no matching violation under v1", "exit": r["exit"], "violations": [str(x)[:200] for x in r.get("violations", [])[:5]]}
        continue
    fixes[name] = v[0]

inv_retain, inv_only = copy.deepcopy(INV), copy.deepcopy(INV)
old_digests = {}
for name, viol in fixes.items():
    for inv, mode in ((inv_retain, "retain"), (inv_only, "only")):
        slot, key = registration_slot(inv, viol)
        if slot is None:
            out["targets"][name] = {"error": "registration slot not found", "violation": viol}
            break
        old = list(slot[key])
        old_digests[name] = old
        slot[key] = sorted(set(old) | {viol["digest"]}) if mode == "retain" else [viol["digest"]]

k_all_fixed = kcopy("all-fixed")
for name in fixes:
    TARGETS[name]["fix"](k_all_fixed)
base_all = {"all_fixed_under_RETAIN": C.run_check(k_all_fixed, inv_retain, quiet=True)["exit"],
            "all_fixed_under_ONLY": C.run_check(k_all_fixed, inv_only, quiet=True)["exit"]}
out["release_with_every_fix"] = base_all
for name, viol in fixes.items():
    k_mix = kcopy("mix-" + name)
    for other in fixes:
        if other != name:
            TARGETS[other]["fix"](k_mix)
    out["targets"][name] = {
        "registered_key_or_path": viol.get("key") or viol.get("file"),
        "draft_v1_registered_digests": old_digests.get(name),
        "fixed_digest": viol["digest"],
        "mixed_release_old_content_under_RETAIN (E7 surface check)": C.run_check(k_mix, inv_retain, quiet=True)["exit"],
        "mixed_release_old_content_under_ONLY": C.run_check(k_mix, inv_only, quiet=True)["exit"],
    }
red1 = C.run_reductions(INV, inv_retain, [], quiet=True)
red2 = C.run_reductions(inv_only, inv_retain, [], quiet=True)
out["reductions"] = {"v1_to_v2_RETAIN_exit": red1["exit"], "v2_ONLY_to_v2_RETAIN_readding_superseded_exit": red2["exit"],
                     "v2_ONLY_to_v2_RETAIN_reductions_listed": [str(x)[:200] for x in (red2.get("reductions") or [])][:10]}
out["holds_B_H3_class_breadth"] = all(isinstance(t, dict) and t.get("mixed_release_old_content_under_RETAIN (E7 surface check)") == 0
                                      and t.get("mixed_release_old_content_under_ONLY") == 3 for t in out["targets"].values()) \
    and red1["exit"] == 0 and red2["exit"] == 0
print(json.dumps(out, indent=1, default=str).replace(SCR, "<scratch>").replace(WT, "<worktree>"))
