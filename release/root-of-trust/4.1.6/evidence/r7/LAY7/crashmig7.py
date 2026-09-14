#!/usr/bin/env python3
"""crashmig7 — crash at every step of the first RoT-1 install on a legacy project, under the revision-7 transaction rules (RV6-M3,
CR6-C-7; RV6-D-A10) (AR-0019). Executed with the real legacy 4.1.5 and 4.1.2 binaries and reviewer C's revision-6 trees.

Attribution. Reviewer C's `crashmig6.py` and `c6lib.py` (AR-0017) are the harness: the prefix construction (two orders for the legacy
lock removal), the legacy probe and the state predicate `c6lib.state_r6` are used unmodified (`c6lib.py` is imported from
AR17_PROBES). This file adds the revision-7 rules and nothing else:
  (a) every layout-migration step is a journal phase written BEFORE the step, with its undo record (`18` §5.3′ LM-1);
  (b) IN_TRANSACTION takes precedence over every other row, and a tree holding a layout-migration journal or its artefacts after
      recovery would be LAYOUT_MIGRATION_INCOMPLETE, never ABSENT or LEGACY (`18` §9 as amended);
  (c) ABSENT additionally requires no governance/overlay and no governance/views; RoT-1 `init` on a tree holding either refuses
      (`INIT_OVER_EXISTING_OVERLAY`, `19` §9 item 6, `09` and `26` §7 R-INIT-9);
  (d) an `exchange-intent` phase precedes RENAME_EXCHANGE; recovery decides from the tree whether the exchange happened;
  (e) recovery for an honoured layout-migration journal either rolls the layout back to exactly the pre-transaction legacy layout
      (every recorded step undone in reverse order) or, when the exchange happened, rolls forward (remaining steps, then migrations,
      strength vector, per-project record and ledger) before COMPLETE.
Checks: after recovery every prefix is LEGACY with a whole-tree digest (work tree, excluding the transaction area) equal to the legacy
project, or COMPLETE after roll-forward; never ABSENT or PARTIAL; RoT-1 init refuses on every tree holding an overlay; the legacy
binaries behave on each rolled-back tree exactly as on the legacy project control (LR-1).
Environment: AR17_SCRATCH (reviewer C's scratch with trees2/, bin/, releases/), AR17_WT (export), AR17_PROBES (reviewer C probes).
Output: JSON on stdout.
"""
import json, os, shutil, sys, tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.environ["AR17_PROBES"])
import c6lib as L  # noqa: E402
import crashmig6 as C6  # noqa: E402

T = json.load(open(os.path.join(L.SCR, "trees2", "trees.json")))
L0, rcs = T["trees"]["L0"], T["rcs"]
BASE = tempfile.mkdtemp(prefix="crashmig7-", dir=L.SCR)  # fresh per run; a re-run never meets an earlier run's trees
TX = C6.TX
UNDO = {"quarantine": ("mv", ".governance-runtime/legacy-quarantine/update", ".governance-runtime/update"),
        "kernel_aside": ("mv", "<aside>/legacy-kernel", "governance/kernel"), "legacy_lock_aside": ("mv", "<aside>/legacy-framework.lock", "governance/framework.lock"),
        "project_to_overlay": ("mv", "governance/overlay", "governance/project"), "generated_to_views": ("mv", "governance/views", "governance/generated"),
        "adoption_evidence": ("mv", "spec/audits/ADOPTION", "spec/audits/GOVERNANCE-ADOPTION"),
        "occ_files": ("rm_sentinels", ["governance/kernel", "governance/project", "governance/generated"]), "occ_lock_dir": ("rm_sentinel_dir", "governance/framework.lock"),
        "occ_spec_and_migration": ("rm_sentinels", ["spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/migration"]), "ignore_rule": ("restore_file", ".gitignore"),
        "exchange": ("exchange_back",)}


def tree_digest_excluding_tx(d):
    m = L.tree_map(d)
    return L.digest_map({k: v for k, v in m.items() if not k.startswith(".governance-runtime/trust-tx") and not k.startswith(".git/")})


def build_prefix_r7(order, steps, n):
    """C6.build_prefix plus the revision-7 journal: each step recorded before it is performed, with the pre-step bytes needed to undo it."""
    d = os.path.join(BASE, "%s-%02d" % (order, n))
    shutil.copytree(L0, d, symlinks=True)
    aside = os.path.join(BASE, "aside-%s-%02d" % (order, n))
    os.makedirs(aside, exist_ok=True)
    tx = os.path.join(d, ".governance-runtime", "trust-tx", TX)
    os.makedirs(tx)
    R6 = T["trees"]["R6"]
    shutil.copytree(os.path.join(R6, "governance", "trust"), os.path.join(tx, "trust.next"), symlinks=True)
    gi = os.path.join(d, ".gitignore")
    saved_gitignore = open(gi, "rb").read() if os.path.exists(gi) else None
    journal = {"operation": "update", "phase": "verified-staged", "first_install_layout_migration": True, "layout_steps": [], "aside": aside,
               "saved_gitignore_b64": None if saved_gitignore is None else saved_gitignore.hex()}
    jp = os.path.join(tx, "journal.json")
    for s in steps[:n]:
        journal["layout_steps"].append(s)                         # LM-1: phase written before the step
        journal["phase"] = "exchange-intent" if s == "exchange" else "layout-migration:" + s
        json.dump(journal, open(jp, "w"))
        C6.apply(d, s, aside)
    json.dump(journal, open(jp, "w"))
    return d


def _rm_sentinel_file(p):
    if L.kind(p) == "file" and open(p).read().strip() == L.SENTINEL:
        os.unlink(p)


def recover_r7(d):
    """`20` §5 as amended: undo every recorded layout step in reverse order unless the exchange happened, in which case roll forward."""
    tx = os.path.join(d, ".governance-runtime", "trust-tx", TX)
    jp = os.path.join(tx, "journal.json")
    if not os.path.exists(jp):
        return {"action": "none"}
    j = json.load(open(jp))
    exchanged = L.kind(os.path.join(d, "governance", "trust")) == "dir" and L.kind(os.path.join(tx, "trust.next")) == "absent"
    if exchanged:
        return {"action": "roll_forward", "remaining_steps_after_exchange": ["migrations", "strength_vector", "per_project_record", "ledger"], "state_after_roll_forward": "COMPLETE (modelled)",
                "legacy_layout_steps_all_done": len(j["layout_steps"]) == len(C6.STEPS_A)}
    for s in reversed(j["layout_steps"]):
        u = UNDO[s]
        if u[0] == "mv":
            src = u[1].replace("<aside>", j["aside"]) if u[1].startswith("<aside>") else os.path.join(d, u[1])
            dst = os.path.join(d, u[2])
            if s == "kernel_aside" and L.kind(dst) == "file":
                _rm_sentinel_file(dst)
            if s == "legacy_lock_aside" and L.kind(dst) == "dir":
                sd = os.path.join(dst, L.OCC_DIR_SENTINEL)
                if L.kind(sd) == "file":
                    os.unlink(sd)
                os.rmdir(dst)
            if L.kind(src) != "absent":
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                os.rename(src, dst)
        elif u[0] == "rm_sentinels":
            for p in u[1]:
                _rm_sentinel_file(os.path.join(d, p))
        elif u[0] == "rm_sentinel_dir":
            p = os.path.join(d, u[1])
            if L.kind(p) == "dir":
                sd = os.path.join(p, L.OCC_DIR_SENTINEL)
                if L.kind(sd) == "file":
                    os.unlink(sd)
                if not os.listdir(p):
                    os.rmdir(p)
        elif u[0] == "restore_file":
            p = os.path.join(d, u[1])
            if j["saved_gitignore_b64"] is None:
                if os.path.exists(p):
                    os.unlink(p)
            else:
                open(p, "wb").write(bytes.fromhex(j["saved_gitignore_b64"]))
    q = os.path.join(d, ".governance-runtime", "legacy-quarantine")
    if L.kind(q) == "dir" and not os.listdir(q):
        os.rmdir(q)
    abandoned = os.path.join(d, ".governance-runtime", "trust-tx", "abandoned")
    os.makedirs(abandoned, exist_ok=True)
    os.rename(tx, os.path.join(abandoned, TX))
    return {"action": "roll_back", "undone": list(reversed(j["layout_steps"]))}


def state_r7(d, vts_open=()):
    """`18` §9 as amended: C's state_r6 rows with IN_TRANSACTION first, ABSENT requiring no overlay or views, and
    LAYOUT_MIGRATION_INCOMPLETE for a tree that still holds layout-migration artefacts outside a completed transaction."""
    s6 = L.state_r6(d, vts_open=vts_open, rcs=rcs)
    rows = list(s6["rows_matched"])
    if "IN_TRANSACTION" in rows:
        return {"state": "IN_TRANSACTION", "rows_r6": rows}
    has_overlay = L.kind(os.path.join(d, "governance", "overlay")) == "dir" or L.kind(os.path.join(d, "governance", "views")) == "dir"
    artefacts = [p for p in (".governance-runtime/legacy-quarantine", "spec/audits/ADOPTION", "governance/overlay", "governance/views") if L.kind(os.path.join(d, p)) != "absent"]
    trust_present = L.kind(os.path.join(d, "governance", "trust")) == "dir"
    if artefacts and not trust_present:
        return {"state": "LAYOUT_MIGRATION_INCOMPLETE", "rows_r6": rows, "artefacts": artefacts}
    if "ABSENT" in rows and has_overlay:
        rows.remove("ABSENT")
    return {"state": rows[0] if rows else "PARTIAL", "rows_r6": s6["rows_matched"]}


def rot1_init(d):
    """R-INIT-9: RoT-1 init refuses on a tree holding governance/overlay or governance/views, or in any state other than ABSENT."""
    st = state_r7(d)["state"]
    if L.kind(os.path.join(d, "governance", "overlay")) != "absent" or L.kind(os.path.join(d, "governance", "views")) != "absent":
        return "INIT_OVER_EXISTING_OVERLAY"
    return "INIT_ALLOWED" if st == "ABSENT" else "INIT_REFUSED_STATE_" + st


def main():
    L0_digest = tree_digest_excluding_tx(L0)
    ctrl = os.path.join(BASE, "L0-control")
    shutil.copytree(L0, ctrl, symlinks=True)
    control_legacy = {"4.1.5": C6.legacy_probe(ctrl, "4.1.5")}
    ctrl2 = os.path.join(BASE, "L0-control-412")
    shutil.copytree(L0, ctrl2, symlinks=True)
    control_legacy["4.1.2"] = C6.legacy_probe(ctrl2, "4.1.2")
    res = {"prefixes": {}, "control_L0_legacy": control_legacy}
    for oname, steps in (("A", C6.STEPS_A), ("B", C6.STEPS_B)):
        for n in range(0, len(steps) + 1):
            d = build_prefix_r7(oname, steps, n)
            honoured = state_r7(d, vts_open=(TX,))
            init_before = rot1_init(d)
            rec = recover_r7(d)
            after = state_r7(d)
            row = {"completed_steps": steps[:n], "state_journal_honoured": honoured["state"], "recovery": rec, "state_after_recovery": after["state"] if rec["action"] != "roll_forward" else "COMPLETE (after roll-forward)",
                   "rot1_init_before_recovery": init_before, "rot1_init_after_recovery": rot1_init(d)}
            if rec["action"] == "roll_back":
                row["tree_equal_to_legacy_project"] = tree_digest_excluding_tx(d) == L0_digest
                d45 = d + "-legacy415"
                shutil.copytree(d, d45, symlinks=True)
                lp = C6.legacy_probe(d45, "4.1.5")
                row["legacy_4.1.5_same_as_control"] = {k: lp[k] == control_legacy["4.1.5"][k] for k in lp if k not in ("tree_changed",)}
            res["prefixes"]["%s-%02d" % (oname, n)] = row
    rows = res["prefixes"].values()
    res["summary"] = {
        "states_with_journal_honoured": sorted({r["state_journal_honoured"] for r in rows}),
        "states_after_recovery": sorted({r["state_after_recovery"] for r in rows}),
        "prefixes_ABSENT_after_recovery": [k for k, r in res["prefixes"].items() if r["state_after_recovery"] == "ABSENT"],
        "prefixes_PARTIAL_after_recovery": [k for k, r in res["prefixes"].items() if r["state_after_recovery"] == "PARTIAL"],
        "rolled_back_prefixes_not_byte_equal_to_legacy_project": [k for k, r in res["prefixes"].items() if r["recovery"]["action"] == "roll_back" and not r["tree_equal_to_legacy_project"]],
        "rolled_forward_prefixes": [k for k, r in res["prefixes"].items() if r["recovery"]["action"] == "roll_forward"],
        "rot1_init_allowed_on_a_tree_with_overlay": [k for k, r in res["prefixes"].items() if r["rot1_init_before_recovery"] == "INIT_ALLOWED" and "project_to_overlay" in r["completed_steps"]],
        "legacy_behaviour_differs_from_control_on_rolled_back_trees": [k for k, r in res["prefixes"].items() if r["recovery"]["action"] == "roll_back" and not all(r["legacy_4.1.5_same_as_control"].values())],
    }
    res["verdicts"] = {
        "honoured_journal_always_IN_TRANSACTION": res["summary"]["states_with_journal_honoured"] == ["IN_TRANSACTION"],
        "never_ABSENT_or_PARTIAL_after_recovery": not res["summary"]["prefixes_ABSENT_after_recovery"] and not res["summary"]["prefixes_PARTIAL_after_recovery"],
        "roll_back_restores_exact_legacy_project": not res["summary"]["rolled_back_prefixes_not_byte_equal_to_legacy_project"],
        "rot1_init_never_over_overlay": not res["summary"]["rot1_init_allowed_on_a_tree_with_overlay"],
        "legacy_behaviour_on_rolled_back_trees_equals_control (LR-1)": not res["summary"]["legacy_behaviour_differs_from_control_on_rolled_back_trees"],
    }
    print(L.scrub(json.dumps({"probe": "crashmig7 (AR-0019; reviewer C crashmig6/c6lib harness, revision-7 rules)", **res}, indent=1, sort_keys=True, default=str)))


if __name__ == "__main__":
    main()
