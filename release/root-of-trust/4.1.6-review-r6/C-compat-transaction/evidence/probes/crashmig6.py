#!/usr/bin/env python3
"""AR-0017 crashmig6 (held-out RV6-C-A15): crash at every step of the FIRST RoT-1 install on a legacy project.

Text under test (4106885):
  `26` §7: the first RoT-1 install transaction on a legacy project MUST, inside one journaled transaction: 1 quarantine legacy
  runtime residue; 2 move the kernel, overlay, views and adoption evidence; 3 write governance/trust/**; 4 create the
  occupation entries, force-adding .governance-runtime/migration; 5 write the ignore rule; 6 record the strength vector;
  7 write the ledger entry.
  `18` §4: the layout migration steps run after journal phase `verified-staged` and before RENAME_EXCHANGE (`swapped`); no
  journal phase names them. `18` §5.3 / `20` §5: recovery for an honoured journal in `prepared`/`staged`/`verified-staged`
  is "move trust-tx/<TX> to trust-tx/abandoned/; deregister" — nothing undoes or completes a layout step.
Method. From the real legacy project L0 (built by build6), construct the tree a crash leaves after each prefix of the
layout steps (two orders for the unspecified removal of the legacy lock), with the transaction area holding the staged
trust tree and a `verified-staged` journal. For each prefix evaluate `c6lib.state_r6` (a) with the journal honoured (same
machine, VTS lists the TX) and (b) after the documented recovery (journal moved to abandoned/, TX deregistered). Then run
real legacy binaries (4.1.5 and 4.1.2) with --root on the post-recovery tree: status, kernel trust, rebuild-memory,
memory query <restricted marker>, init --force --skip-index; record whole-tree digests, whether the legacy binary regains a
verified install, and whether it serves the restricted file. Scratch only. Output: JSON on stdout.
"""
import json, os, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c6lib as L  # noqa

T = json.load(open(os.path.join(L.SCR, "trees2", "trees.json")))
L0, R6, rcs = T["trees"]["L0"], T["trees"]["R6"], T["rcs"]
BASE = os.path.join(L.SCR, "crashmig6")
os.makedirs(BASE, exist_ok=True)
TX = "TX-" + "5a" * 16
MARK = "AR0017RESTRICTEDMARKER"


def mv(src, dst):
    if L.kind(src) != "absent":
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst)


STEPS_A = ["quarantine", "kernel_aside", "legacy_lock_aside", "project_to_overlay", "generated_to_views", "adoption_evidence",
           "occ_files", "occ_lock_dir", "occ_spec_and_migration", "ignore_rule", "exchange"]
STEPS_B = ["quarantine", "kernel_aside", "project_to_overlay", "generated_to_views", "adoption_evidence", "occ_files",
           "legacy_lock_aside", "occ_lock_dir", "occ_spec_and_migration", "ignore_rule", "exchange"]


def apply(d, step, aside):
    g = os.path.join(d, "governance")
    rt = os.path.join(d, ".governance-runtime")
    if step == "quarantine":
        mv(os.path.join(rt, "update"), os.path.join(rt, "legacy-quarantine", "update"))
    elif step == "kernel_aside":
        mv(os.path.join(g, "kernel"), os.path.join(aside, "legacy-kernel"))
    elif step == "legacy_lock_aside":
        mv(os.path.join(g, "framework.lock"), os.path.join(aside, "legacy-framework.lock"))
    elif step == "project_to_overlay":
        mv(os.path.join(g, "project"), os.path.join(g, "overlay"))
    elif step == "generated_to_views":
        mv(os.path.join(g, "generated"), os.path.join(g, "views"))
    elif step == "adoption_evidence":
        mv(os.path.join(d, "spec/audits/GOVERNANCE-ADOPTION"), os.path.join(d, "spec/audits/ADOPTION"))
    elif step == "occ_files":
        for p in ("kernel", "project", "generated"):
            if L.kind(os.path.join(g, p)) == "absent":
                open(os.path.join(g, p), "w").write(L.SENTINEL + "\n")
    elif step == "occ_lock_dir":
        if L.kind(os.path.join(g, "framework.lock")) == "absent":
            os.makedirs(os.path.join(g, "framework.lock"))
            open(os.path.join(g, "framework.lock", L.OCC_DIR_SENTINEL), "w").write(L.SENTINEL + "\n")
    elif step == "occ_spec_and_migration":
        os.makedirs(os.path.join(d, "spec/audits"), exist_ok=True)
        if L.kind(os.path.join(d, "spec/audits/GOVERNANCE-ADOPTION")) == "absent":
            open(os.path.join(d, "spec/audits/GOVERNANCE-ADOPTION"), "w").write(L.SENTINEL + "\n")
        if L.kind(os.path.join(rt, "migration")) == "absent":
            open(os.path.join(rt, "migration"), "w").write(L.SENTINEL + "\n")
    elif step == "ignore_rule":
        gi = os.path.join(d, ".gitignore")
        open(gi, "w").write("/.governance-runtime/*\n!/.governance-runtime/migration\n")
    elif step == "exchange":
        os.rename(os.path.join(rt, "trust-tx", TX, "trust.next"), os.path.join(g, "trust"))


def build_prefix(order_name, steps, n):
    d = os.path.join(BASE, "%s-%02d" % (order_name, n))
    shutil.copytree(L0, d, symlinks=True)
    aside = os.path.join(BASE, "aside-%s-%02d" % (order_name, n))
    os.makedirs(aside, exist_ok=True)
    tx = os.path.join(d, ".governance-runtime", "trust-tx", TX)
    os.makedirs(tx)
    shutil.copytree(os.path.join(R6, "governance", "trust"), os.path.join(tx, "trust.next"), symlinks=True)
    json.dump({"operation": "update", "phase": "verified-staged", "first_install_layout_migration": True},
              open(os.path.join(tx, "journal.json"), "w"))
    for s in steps[:n]:
        apply(d, s, aside)
    return d


def recover_abandon(d):
    """20 §5 for an honoured `verified-staged` journal: move trust-tx/<TX> to trust-tx/abandoned/; deregister."""
    tx = os.path.join(d, ".governance-runtime", "trust-tx", TX)
    if L.kind(tx) == "dir":
        mv(tx, os.path.join(d, ".governance-runtime", "trust-tx", "abandoned", TX))


def legacy_probe(d, v):
    env = L.child_env(os.path.join(BASE, "home-" + v + "-" + os.path.basename(d)), os.path.join(BASE, "cache-" + v))
    before = L.digest_map(L.tree_map(d))
    out = {}
    for name, argv in (("status", ["status"]), ("kernel_trust", ["kernel", "trust"]), ("rebuild_memory", ["rebuild-memory"]),
                       ("memory_query", ["memory", "query", MARK]), ("init_force", ["init", "--force", "--skip-index"]),
                       ("memory_query_after_init_force", ["memory", "query", MARK])):
        r = L.gov(L.BINS[v], argv, env, d, d)
        res = L.result(r)
        out[name] = {"ok": r.get("ok"), "code": L.errcode(r)}
        if name == "kernel_trust":
            out[name]["verified"] = res.get("verified")
        if name.startswith("memory_query"):
            out[name]["hits"] = sorted({h.get("path") for h in (res.get("hits") or []) if isinstance(h, dict)})
    after_map = L.tree_map(d)
    out["tree_changed"] = L.digest_map(after_map) != before
    out["classifications_ok_after"] = L.classifications(d)
    out["state_after"] = L.state_r6(d, rcs=rcs)["state"]
    return out


def main():
    res = {"orders": {"A_lock_aside_with_kernel": STEPS_A, "B_lock_aside_before_occupation_dir": STEPS_B}, "prefixes": {}}
    for oname, steps in (("A", STEPS_A), ("B", STEPS_B)):
        for n in range(0, len(steps) + 1):
            d = build_prefix(oname, steps, n)
            honoured = L.state_r6(d, vts_open=(TX,), rcs=rcs)
            recover_abandon(d)
            after = L.state_r6(d, rcs=rcs)
            row = {"completed_steps": steps[:n], "state_journal_honoured": honoured["rows_matched"],
                   "state_after_documented_recovery": after["state"], "rows_after_recovery": after["rows_matched"],
                   "reasons_after_recovery": after["reasons"], "overlay_present": L.kind(os.path.join(d, "governance/overlay")) == "dir",
                   "legacy_project_dir_present": L.kind(os.path.join(d, "governance/project")) == "dir"}
            if after["state"] != "COMPLETE":
                d45 = d + "-legacy415"; shutil.copytree(d, d45, symlinks=True)
                row["legacy_4.1.5"] = legacy_probe(d45, "4.1.5")
                d42 = d + "-legacy412"; shutil.copytree(d, d42, symlinks=True)
                row["legacy_4.1.2"] = legacy_probe(d42, "4.1.2")
            res["prefixes"]["%s-%02d" % (oname, n)] = row
    rows = res["prefixes"].values()
    res["summary"] = {
        "states_after_recovery": sorted({r["state_after_documented_recovery"] for r in rows}),
        "prefixes_ABSENT_after_recovery": [k for k, r in res["prefixes"].items() if r["state_after_documented_recovery"] == "ABSENT"],
        "prefixes_where_journal_and_ABSENT_or_LEGACY_rows_overlap": [k for k, r in res["prefixes"].items()
                                                                     if "IN_TRANSACTION" in r["state_journal_honoured"] and len(r["state_journal_honoured"]) > 1],
        "prefixes_legacy_regains_verified_install": [k for k, r in res["prefixes"].items()
                                                     if (r.get("legacy_4.1.5") or {}).get("kernel_trust", {}).get("verified")],
        "prefixes_legacy_serves_restricted_marker": [k for k, r in res["prefixes"].items()
                                                     if any((r.get(b) or {}).get(q, {}).get("hits") for b in ("legacy_4.1.5", "legacy_4.1.2")
                                                            for q in ("memory_query", "memory_query_after_init_force"))],
        "prefixes_COMPLETE_after_recovery": [k for k, r in res["prefixes"].items() if r["state_after_documented_recovery"] == "COMPLETE"],
    }
    print(L.scrub(json.dumps({"probe": "AR-0017 crashmig6 (RV6-C-A15 crash inside the first-install layout migration)", **res},
                             indent=1, sort_keys=True, default=str)))


if __name__ == "__main__":
    main()
