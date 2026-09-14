#!/usr/bin/env python3
"""Independent destructive-command matrix on the RoT-1 rev3 L3 layout with whole-tree before/after digests.
Each command runs on a fresh copy of L3 with all four real legacy binaries. Records whole-tree (not named-path)
digests including entry TYPES, git state, classification survival, and the old binary's post-run trust view."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import yaml

SRC = {"4.1.2": REPO + "/release/releases/4.1.2", "4.1.3": REPO + "/release/releases/4.1.3",
       "4.1.4": REPO + "/release/releases/4.1.4", "4.1.5": REPO + "/release/releases/4.1.5"}
OLDER = {"4.1.2": "4.1.2", "4.1.3": "4.1.2", "4.1.4": "4.1.3", "4.1.5": "4.1.4"}

# The destructive/state-changing register the review flagged (H4 class) + producer/adopt/cit paths.
def cmds(v):
    s, o = SRC[v], SRC[OLDER[v]]
    return {
        "update_rollback": ["update", "--rollback", "--reason", "ar3"],
        "update_apply_same": ["update", "--apply", "--approve", "--source", s, "--by", "owner"],
        "update_apply_older": ["update", "--apply", "--approve", "--source", o, "--by", "owner"],
        "init_force_src": ["init", "--force", "--source", s, "--name", "ar3", "--skip-index"],
        "init_force_nosrc": ["init", "--force", "--name", "ar3", "--skip-index"],
        "kernel_reinstall": ["kernel", "reinstall", "--source", s],
        "adopt_baseline": ["adopt", "baseline"],
        "adopt_rollback_1": ["adopt", "rollback", "--batch", "1"],
        "adopt_rollback_0": ["adopt", "rollback", "--batch", "0"],
        "migrate_baseline": ["migrate", "baseline"],
        "migrate_rollback_1": ["migrate", "rollback", "--batch", "1"],
        "recover": ["recover"],
        "rebuild_memory": ["rebuild-memory"],
        "task_create": ["task", "create", "--class", "documentation", "--objective", "x", "--title", "t", "--status", "READY"],
        "kernel_override": ["kernel", "override", "--reason", "ar3"],
        "cit_propose": ["cit", "propose", "--proposal", "p", "--trigger", "editorial", "--targets", "TASK-0001", "--manifest", "/nonexistent"],
        "gate_create": ["gate", "create", "--question", "q?", "--fields", json.dumps({"options":[{"id":"A","description":"y"}],"impact_radius":"R1","confidence":0.9,"reversibility":"reversible"})],
        "adapters_generate": ["adapters", "generate"],
        "tools_install_execute": ["tools", "install", "--descriptor", "/nonexistent.json", "--execute"],
        "plugins_register": ["plugins", "register", "--descriptor", "/nonexistent.yaml"],
        "resume": ["resume"],
    }


def run(scratch, L3, v):
    rows = []
    for name, args in cmds(v).items():
        c = os.path.join(scratch, "runs", f"{v}-{name}")
        shutil.copytree(L3, c, symlinks=True)
        env = child_env(scratch, f"{v}-{name}")
        before = {"tree": file_map(c), "trust": file_map(c + "/governance/trust", False) if os.path.isdir(c + "/governance/trust") else {}, "git": git_state(c)}
        r = gov(BINS[v], c, args, env)
        after = {"tree": file_map(c), "trust": file_map(c + "/governance/trust", False) if os.path.isdir(c + "/governance/trust") else {}, "git": git_state(c)}
        ov = c + "/governance/overlay/DATA_SENSITIVITY.yaml"
        try:
            cls = any(x.get("pattern") == "product/restricted-plan.md" for x in (yaml.safe_load(open(ov)).get("classifications") or []))
        except Exception:
            cls = None
        tree_changed = digest(before["tree"]) != digest(after["tree"])
        trust_changed = digest(before["trust"]) != digest(after["trust"])
        git_changed = before["git"] != after["git"]
        row = {"binary": v, "cmd": name, "ok": r.get("ok"), "code": code(r),
               "tree_changed_excl_runtime": tree_changed, "trust_changed": trust_changed, "git_changed": git_changed,
               "classification_survives": cls, "changed_paths": changed(before["tree"], after["tree"])[:20]}
        if tree_changed or trust_changed or git_changed:
            vv = gov(BINS[v], c, ["kernel", "verify"], env)
            row["old_binary_verify_after"] = {"ok": vv.get("ok"), "code": code(vv)}
        rows.append(row)
    return rows


if __name__ == "__main__":
    scratch = sys.argv[1]
    L3 = sys.argv[2]
    allrows = []
    for v in ("4.1.2", "4.1.3", "4.1.4", "4.1.5"):
        allrows += run(scratch, L3, v)
    viol = [r for r in allrows if r["tree_changed_excl_runtime"] or r["trust_changed"] or r["git_changed"]]
    clslost = [r for r in allrows if r["classification_survives"] is False]
    okrun = [r for r in allrows if r.get("ok")]
    print(json.dumps({
        "total_runs": len(allrows), "binaries": list(SRC.keys()),
        "violations_any_write": viol, "classification_lost": clslost,
        "ok_true_count": len(okrun),
        "property_holds": len(viol) == 0 and len(clslost) == 0,
        "rows": allrows}, indent=1))
