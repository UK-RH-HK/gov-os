#!/usr/bin/env python3
"""AR-0017 admission-and-recovery as transactional state, against the pack's own revision-6 reference executor
`gov_admit_reference_r6.py` (imported read-only, unmodified). Model evidence (M): the reference is architecture evidence,
not the product. Each question is AR-0017's; where a claim of the architect's ADM6 exists it is re-asked here as a claim.

Attacks (RV6-C admission/transaction register subset):
  T1  crash between install-from-buffer and record write -> installed binary, C0 only (fail closed)
  T2  re-admission on a store holding anchors/high-water/projects and an admission record -> store kept, earlier record kept
  T3  first-admission determination: an empty store dir (no admissions), and a store holding only a legacy-form record
  T4  rollback to a previously admitted binary keeps its record (admit v1, admit v2, roll back to v1 -> C2 allowed)
  T5  concurrent first admissions with the R-ADM-13 lock -> one store, no record-holding store moved aside
  T6  a record beside the binary / in a moved-aside store / shipped by a package -> not honoured (GB-1')
  T7  NEW: crash during the store move-aside (rename done, record not written) -> stale anchors orphaned in pre-admission-N,
      machine UNANCHORED; a re-run makes a fresh store; no stale anchor is read
  T8  NEW: GB-1' lineage binding -- a record in a `vts-<16>` store whose lineage differs from the binary's, naming the
      binary digest: is it honoured? (tests whether load honours by digest alone within the protected root)
  T9  NEW: re-admission race with the lock, on a store that already holds a record -> the record-holding store is never
      moved aside (20 trials)
Environment: SCRATCH. Legacy binaries not used. Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys, tempfile, threading
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.environ["AR17_WT"]
REF = os.path.join(WT, "release", "root-of-trust", "4.1.6", "evidence", "r6", "gov_admit_reference_r6.py")
spec = importlib.util.spec_from_file_location("gov_admit_reference_r6", REF)
GA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GA)
S = tempfile.mkdtemp(prefix="admtx6-", dir=os.environ["AR17_SCRATCH"])
LIN = "sha256:" + "a1" * 32
LIN2 = "sha256:" + "b2" * 32
NOW = "2026-09-14T00:00:00Z"


def rec(dig, lineage=LIN, valid_until=None, protected=True):
    return {"binary_digest": dig, "target": "x86_64-unknown-linux-gnu", "release_id": "R8", "lineage": lineage,
            "state_fingerprint": "gov-fc:aaaaaaaa:10:" + "0" * 64, "admitted_at": NOW, "admitter_digest": "sha256:" + "e" * 64,
            "valid_until": valid_until, "location_protected": protected}


def seed_store(rec_dir, lineage=LIN, with_record=True, record_dig=None):
    st = GA.store_dir(rec_dir, lineage)
    os.makedirs(os.path.join(st, "projects"), exist_ok=True)
    json.dump({"clock_high_water": "2027-06-01T00:00:00Z", "accepted_tbm": {"root": 3, "policy": 5, "state": 10}},
              open(os.path.join(st, "high-water.json"), "w"))
    json.dump([{"sequence": 10, "digest": "sha256:" + "d" * 64, "method": "human"}], open(os.path.join(st, "anchors.json"), "w"))
    json.dump({"highest_installed_sequence": 10, "project_strength_vector": ["confidential"]},
              open(os.path.join(st, "projects", "P1.json"), "w"))
    if with_record:
        os.makedirs(os.path.join(st, "admissions"), exist_ok=True)
        rd = record_dig or GA.sha256d(b"binary-v0")
        json.dump(rec(rd), open(os.path.join(st, "admissions", rd.replace(":", "-") + ".json"), "w"))
    return st


def rel(p):
    return os.path.relpath(p, S) if p else None


res = {}
dig1 = GA.sha256d(b"binary-v1")
dig2 = GA.sha256d(b"binary-v2")

# T1 crash after install before record
d = os.path.join(S, "t1"); exe = os.path.join(d, "bin", "gov")
inst = GA.install_from_buffer(b"binary-v1", exe, dig1)
res["T1_crash_after_install_before_record"] = {"reread_equal": inst["reread_equal"],
    "C0": GA.gov_run(exe, "C0", os.path.join(d, "rec"), NOW, [], "C0_C2")["result"],
    "C2": GA.gov_run(exe, "C2", os.path.join(d, "rec"), NOW, [], "C0_C2")["result"],
    "C3": GA.gov_run(exe, "C3", os.path.join(d, "rec"), NOW, [], "C0_C2")["result"]}

# T2 re-admission keeps store
rd = os.path.join(S, "t2", "rec"); st = seed_store(rd, with_record=True)
first = GA.is_first_admission(rd, LIN)
rp, st2, moved = GA.write_admission_record(rec(dig1), rd, LIN)
res["T2_readmission_keeps_store"] = {"is_first_admission": first, "moved_aside": rel(moved),
    "kept": {f: os.path.exists(os.path.join(st2, f)) for f in ("high-water.json", "anchors.json", "projects/P1.json")},
    "earlier_record_kept": os.path.exists(os.path.join(st2, "admissions", GA.sha256d(b"binary-v0").replace(":", "-") + ".json")),
    "new_record_added": os.path.exists(rp)}

# T3 first-admission determination edge cases
# 3a empty store dir (no admissions, no legacy file, but anchors present)
rd = os.path.join(S, "t3a", "rec"); st = seed_store(rd, with_record=False)
res["T3a_store_with_anchors_no_record_is_first_admission"] = {
    "is_first_admission": GA.is_first_admission(rd, LIN),
    "after": (lambda r: {"moved_aside": rel(r[2]), "anchors_in_new_store": os.path.exists(os.path.join(r[1], "anchors.json"))})(GA.write_admission_record(rec(dig1), rd, LIN))}
# 3b store holding only a legacy-form record admission-<prefix>.json at top
rd = os.path.join(S, "t3b", "rec"); st = GA.store_dir(rd, LIN); os.makedirs(st)
json.dump({"clock_high_water": "2027-06-01T00:00:00Z"}, open(os.path.join(st, "high-water.json"), "w"))
json.dump(rec(GA.sha256d(b"binary-v0")), open(os.path.join(st, "admission-" + GA.sha256d(b"binary-v0")[7:15] + ".json"), "w"))
res["T3b_store_with_legacy_form_record_is_not_first"] = {
    "is_first_admission": GA.is_first_admission(rd, LIN),
    "after": (lambda r: {"moved_aside": rel(r[2]), "high_water_kept": os.path.exists(os.path.join(r[1], "high-water.json"))})(GA.write_admission_record(rec(dig1), rd, LIN))}

# T4 rollback keeps record
rd = os.path.join(S, "t4", "rec")
e1 = os.path.join(S, "t4", "v1", "gov"); e2 = os.path.join(S, "t4", "v2", "gov")
GA.install_from_buffer(b"binary-v1", e1, dig1); GA.install_from_buffer(b"binary-v2", e2, dig2)
GA.write_admission_record(rec(dig1), rd, LIN); _, _, mv2 = GA.write_admission_record(rec(dig2), rd, LIN)
res["T4_rollback_keeps_record"] = {"moved_on_second_admission": rel(mv2),
    "v1_rollback_C2": GA.gov_run(e1, "C2", rd, NOW, [], "C0_C2")["result"], "v2_C2": GA.gov_run(e2, "C2", rd, NOW, [], "C0_C2")["result"]}

# T5 concurrent first admissions with the lock
def race(flags, label, seed_record=False):
    rd = os.path.join(S, "t5-" + label, "rec"); os.makedirs(rd, exist_ok=True)
    if seed_record:
        seed_store(rd, with_record=True)
    errs = []; barrier = threading.Barrier(8)
    def adm():
        try:
            barrier.wait(); GA.write_admission_record(rec(dig1), rd, LIN, flags)
        except Exception as e:
            errs.append(repr(e))
    ts = [threading.Thread(target=adm) for _ in range(8)]
    for t in ts: t.start()
    for t in ts: t.join()
    strays = sorted(d for d in os.listdir(rd) if "pre-admission" in d)
    with_rec = [d for d in strays if os.path.isdir(os.path.join(rd, d, "admissions")) and os.listdir(os.path.join(rd, d, "admissions"))]
    return {"errors": errs, "stores": sorted(d for d in os.listdir(rd) if d.startswith("vts-") and ".pre" not in d),
            "moved_aside": len(strays), "moved_aside_holding_a_record": len(with_rec)}
res["T5_concurrent_first_admissions_lock"] = race({}, "lock")

# T6 record outside store
rd = os.path.join(S, "t6", "rec"); exe15 = os.path.join(S, "t6", "pkg", "bin", "gov")
GA.install_from_buffer(b"binary-v1", exe15, dig1)
os.makedirs(os.path.join(rd, "pkg-shipped")); json.dump(rec(dig1), open(os.path.join(rd, "pkg-shipped", "admission.json"), "w"))
aside = GA.store_dir(rd, LIN) + ".pre-admission-0"; os.makedirs(os.path.join(aside, "admissions"))
json.dump(rec(dig1), open(os.path.join(aside, "admissions", dig1.replace(":", "-") + ".json"), "w"))
res["T6_record_outside_store_not_honoured"] = {"r6": GA.gov_run(exe15, "C2", rd, NOW, [], "C0_C2")["result"],
    "mutant_record_anywhere": GA.gov_run(exe15, "C2", rd, NOW, [], "C0_C2", {"record_anywhere": True})["result"]}

# T7 NEW crash during move-aside: rename done, record not written
rd = os.path.join(S, "t7", "rec"); st = seed_store(rd, with_record=False)   # store with anchors, no record -> first admission
# simulate the move-aside then crash: rename st -> pre-admission-0, do not write record
os.rename(st, st + ".pre-admission-0")
res["T7_crash_during_move_aside"] = {
    "stale_anchor_in_pre_admission": os.path.exists(st + ".pre-admission-0/anchors.json"),
    "next_run_is_first_admission": GA.is_first_admission(rd, LIN),
    "next_run": (lambda r: {"new_store_has_no_anchor": not os.path.exists(os.path.join(r[1], "anchors.json")),
                            "moved_aside": rel(r[2])})(GA.write_admission_record(rec(dig1), rd, LIN)),
    "gov_run_after": GA.gov_run(GA.install_from_buffer.__self__ if False else (lambda p: (GA.install_from_buffer(b"binary-v1", p, dig1), p)[1])(os.path.join(S, "t7", "bin", "gov")), "C3", rd, NOW, [], "C0_C2")["result"]}

# T8 NEW GB-1' lineage binding: record in a vts store for a DIFFERENT lineage, naming the binary digest
rd = os.path.join(S, "t8", "rec"); exe8 = os.path.join(S, "t8", "bin", "gov")
GA.install_from_buffer(b"binary-v1", exe8, dig1)
st_other = GA.store_dir(rd, LIN2); os.makedirs(os.path.join(st_other, "admissions"))   # a genuine store for lineage LIN2
json.dump(rec(dig1, lineage=LIN2), open(os.path.join(st_other, "admissions", dig1.replace(":", "-") + ".json"), "w"))
res["T8_record_in_other_lineage_store"] = {
    "store_name_len": len(os.path.basename(st_other)),
    "C2_honoured_by_digest_across_lineage_stores": GA.gov_run(exe8, "C2", rd, NOW, [], "C0_C2")["result"],
    "note": "gov_run matches binary_digest across every vts-<16> store under the protected record root; it does not bind the record's lineage to the binary's own lineage. Planting requires write to the protected VTS root (A3/RS-3)."}

# T9 NEW re-admission race with the lock on a store that already holds a record
res["T9_readmission_race_record_present"] = race({}, "rerace", seed_record=True)

res["verdicts"] = {
    "T1_fail_closed": res["T1_crash_after_install_before_record"]["C2"] == "BINARY_NOT_ADMITTED" and res["T1_crash_after_install_before_record"]["C0"] == "ALLOWED",
    "T2_readmission_keeps_store": (not res["T2_readmission_keeps_store"]["is_first_admission"]) and res["T2_readmission_keeps_store"]["moved_aside"] is None and all(res["T2_readmission_keeps_store"]["kept"].values()) and res["T2_readmission_keeps_store"]["earlier_record_kept"],
    "T3a_store_with_anchors_but_no_record_moved_aside": res["T3a_store_with_anchors_no_record_is_first_admission"]["is_first_admission"] and res["T3a_store_with_anchors_no_record_is_first_admission"]["after"]["moved_aside"] is not None,
    "T3b_legacy_form_record_not_first": not res["T3b_store_with_legacy_form_record_is_not_first"]["is_first_admission"],
    "T4_rollback_keeps_record": res["T4_rollback_keeps_record"]["moved_on_second_admission"] is None and res["T4_rollback_keeps_record"]["v1_rollback_C2"] == "ALLOWED",
    "T5_lock_one_store_no_record_moved": len(res["T5_concurrent_first_admissions_lock"]["stores"]) == 1 and res["T5_concurrent_first_admissions_lock"]["moved_aside_holding_a_record"] == 0,
    "T6_outside_store_not_honoured": res["T6_record_outside_store_not_honoured"]["r6"] == "BINARY_NOT_ADMITTED",
    "T7_fresh_store_no_stale_anchor": res["T7_crash_during_move_aside"]["next_run"]["new_store_has_no_anchor"] and res["T7_crash_during_move_aside"]["gov_run_after"] in ("TCB_WRITABLE_BY_GOVERNED_ACCOUNT", "ALLOWED"),
    "T8_cross_lineage_record_honoured_within_protected_root": res["T8_record_in_other_lineage_store"]["C2_honoured_by_digest_across_lineage_stores"] == "ALLOWED",
    "T9_readmission_race_no_record_moved": res["T9_readmission_race_record_present"]["moved_aside_holding_a_record"] == 0,
}
txt = json.dumps({"probe": "AR-0017 admtx6 admission/transaction (reference model)", **res}, indent=1, sort_keys=True).replace(S, "<scratch>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
