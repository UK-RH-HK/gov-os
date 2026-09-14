#!/usr/bin/env python3
"""PPR7 — per-project record identity and re-record rules (review r6 RV6-M4 / CR6-C-8 and RV6-M5 / CR6-C-9), reference model for the
revision-7 text of `20` §9 and `18` §5.1 (AR-0019). Computed; scratch-free; a model of the rules, not of the product code.

Rules modelled (revision 7):
  PR-1  A per-project record is keyed by `project_trust_id` AND a locally recorded repository identity (the identity of the Git
        common directory recorded by the first install transaction on this machine; a repository writer cannot copy it into an
        unrelated clone because it is machine-local, never committed).
  PR-2  A known id at a new path with the same repository identity (worktree, moved checkout, bind-mount) inherits the strongest
        recorded strength vector and the highest installed sequence, adds the path and is reported (`PROJECT_PATH_ADDED`).
  PR-3  A known id with a different repository identity (second clone, fork, template copy) is reported
        (`PROJECT_IDENTITY_MISMATCH`), never overwrites the original record, and fails closed for gated operations until a
        `project_strength` gate adopts it.
  PR-4  A re-record never drops a failing strength requirement unless the `weakening` or `project_strength` gate accepted it;
        every remedy (`kernel reinstall`, `update --apply` from PARTIAL, recover exchange-back, `init --force`) commits with failing
        requirements retained.
  PR-5  Pending `policy_lowering` and `registration_change` obligations are record fields cleared only by their gates; no install
        transaction clears them.
Mutants: `path_keyed` (the revision-6 reading: the record is keyed by path), `id_only` (keyed by id without repository identity),
`remedy_rerecords` (a remedy recomputes the vector and clears obligations).
Output: JSON on stdout.
"""
import copy, json, sys

sys.dont_write_bytecode = True


class Machine:
    def __init__(self, mode=None):
        self.mode = mode or set()
        self.records = {}   # key -> record
        self.reports = []

    def key(self, pid, ident, path):
        if "path_keyed" in self.mode:
            return ("path", path)
        if "id_only" in self.mode:
            return ("id", pid)
        return ("id", pid, ident)

    def find(self, pid, ident, path):
        k = self.key(pid, ident, path)
        if k in self.records:
            return k, self.records[k]
        if "path_keyed" in self.mode:
            return k, None
        if "id_only" not in self.mode:
            other = [r for kk, r in self.records.items() if kk[1] == pid and kk[2] != ident]
            if other:
                self.reports.append(("PROJECT_IDENTITY_MISMATCH", pid, path))
                return k, {"identity_mismatch": True}
        return k, None

    def install(self, pid, ident, path, seq, strength, remedy=False, gates=()):
        """An install transaction on project `pid` at `path`; `strength` maps requirement -> failing (True) computed now."""
        k, rec = self.find(pid, ident, path)
        if rec and rec.get("identity_mismatch"):
            return "PROJECT_IDENTITY_MISMATCH"
        if rec is None:
            rec = {"paths": set(), "seq": 0, "failing": set(), "pending": set()}
            self.records[k] = rec
        if path not in rec["paths"] and rec["paths"]:
            self.reports.append(("PROJECT_PATH_ADDED", pid, path))
        rec["paths"].add(path)
        if seq < rec["seq"] and "downgrade" not in gates:
            return "DOWNGRADE_WITHOUT_TRANSACTION"
        rec["seq"] = max(rec["seq"], seq)
        now_failing = {r for r, f in strength.items() if f}
        if remedy and "remedy_rerecords" in self.mode:
            rec["failing"] = now_failing
            rec["pending"] = set()
        else:
            accepted = {r for r in rec["failing"] if ("weakening" in gates or "project_strength" in gates)}
            rec["failing"] = (rec["failing"] - accepted) | now_failing
        return "COMMITTED"

    def add_pending(self, pid, ident, path, kind):
        k, rec = self.find(pid, ident, path)
        rec["pending"].add(kind)

    def gated_operation(self, pid, ident, path, kind):
        k, rec = self.find(pid, ident, path)
        if rec is None:
            return "NO_RECORD_ALLOWED_AS_NEW_PROJECT"
        if rec.get("identity_mismatch"):
            return "PROJECT_IDENTITY_MISMATCH"
        if kind in rec["pending"]:
            return "GATE_REQUIRED:%s" % kind
        if rec["failing"]:
            return "STRENGTH_REPORT:%s" % ",".join(sorted(rec["failing"]))
        return "ALLOWED"

    def clear_by_gate(self, pid, ident, path, kind):
        k, rec = self.find(pid, ident, path)
        rec["pending"].discard(kind)


def identity_scenarios(mode):
    m = Machine(mode)
    out = {}
    m.install("P", "git-A", "/work/p", 11, {"R1": False})
    out["worktree_same_identity_downgrade_to_7"] = m.install("P", "git-A", "/work/p-wt", 7, {"R1": False})
    out["moved_checkout_downgrade_to_7"] = m.install("P", "git-A", "/moved/p", 7, {"R1": False})
    out["bind_mount_downgrade_to_7"] = m.install("P", "git-A", "/mnt/p", 7, {"R1": False})
    out["second_clone_other_identity_install"] = m.install("P", "git-B", "/clone/p", 12, {"R1": True})
    out["fork_other_identity_gated_operation"] = m.gated_operation("P", "git-C", "/fork/p", "registration_change")
    orig = m.records.get(("id", "P", "git-A")) or m.records.get(("id", "P")) or {}
    out["original_record_after_clone_and_fork"] = {"seq": orig.get("seq"), "failing": sorted(orig.get("failing", []))}
    out["reports"] = sorted({r[0] for r in m.reports})
    return out


def rerecord_scenarios(mode):
    m = Machine(mode)
    out = {}
    m.install("P", "git-A", "/work/p", 11, {"R-overlay-weakened": True})
    m.add_pending("P", "git-A", "/work/p", "registration_change")
    for remedy in ("kernel_reinstall", "update_apply_from_PARTIAL", "recover_exchange_back", "init_force"):
        m.install("P", "git-A", "/work/p", 11, {"R-overlay-weakened": False}, remedy=True)
        out["after_%s" % remedy] = m.gated_operation("P", "git-A", "/work/p", "registration_change")
    m.install("P", "git-A", "/work/p", 12, {"R-overlay-weakened": False})
    out["after_completed_update_and_second_unit_of_work"] = m.gated_operation("P", "git-A", "/work/p", "registration_change")
    m.clear_by_gate("P", "git-A", "/work/p", "registration_change")
    out["after_registration_change_gate"] = m.gated_operation("P", "git-A", "/work/p", "registration_change")
    m.install("P", "git-A", "/work/p", 12, {"R-overlay-weakened": False}, gates=("weakening",))
    out["after_weakening_gate_accepts"] = m.gated_operation("P", "git-A", "/work/p", "registration_change")
    return out


res = {"probe": "PPR7 per-project record identity and re-record rules (AR-0019)", "identity": {}, "rerecord": {}}
for label, mode in (("r7", set()), ("mutant_path_keyed", {"path_keyed"}), ("mutant_id_only", {"id_only"})):
    res["identity"][label] = identity_scenarios(mode)
for label, mode in (("r7", set()), ("mutant_remedy_rerecords", {"remedy_rerecords"})):
    res["rerecord"][label] = rerecord_scenarios(mode)
I, RR = res["identity"], res["rerecord"]
res["verdicts"] = {
    "worktree_move_bindmount_keep_E10": all(I["r7"][k] == "DOWNGRADE_WITHOUT_TRANSACTION" for k in ("worktree_same_identity_downgrade_to_7", "moved_checkout_downgrade_to_7", "bind_mount_downgrade_to_7")),
    "clone_and_fork_reported_fail_closed_and_never_overwrite": I["r7"]["second_clone_other_identity_install"] == "PROJECT_IDENTITY_MISMATCH" and I["r7"]["fork_other_identity_gated_operation"] == "PROJECT_IDENTITY_MISMATCH"
                                                              and I["r7"]["original_record_after_clone_and_fork"] == {"seq": 11, "failing": []},
    "path_keyed_mutant_detected": I["mutant_path_keyed"]["worktree_same_identity_downgrade_to_7"] == "COMMITTED",
    "id_only_mutant_detected": I["mutant_id_only"]["original_record_after_clone_and_fork"] != {"seq": 11, "failing": []},
    "remedies_keep_strength_report_and_pending_gate": all(v == "GATE_REQUIRED:registration_change" for k, v in RR["r7"].items() if k.startswith("after_") and k not in ("after_registration_change_gate", "after_weakening_gate_accepts")),
    "only_gates_clear": RR["r7"]["after_registration_change_gate"].startswith("STRENGTH_REPORT") and RR["r7"]["after_weakening_gate_accepts"] == "ALLOWED",
    "remedy_rerecord_mutant_detected": RR["mutant_remedy_rerecords"]["after_kernel_reinstall"] == "ALLOWED",
}
print(json.dumps(res, indent=1, sort_keys=True, default=sorted))
