#!/usr/bin/env python3
"""ADM6 — admission records as transactional state, against the revision-6 reference executor (`31` R-ADM-6…R-ADM-8′, R-ADM-13, GB-1′;
RV5-M3, RV5-C-A08…A11, CR5-B-03, CR5-B-07). Scratch only.

Each of reviewer C's `admit_tx.py` questions is re-asked of `gov_admit_reference_r6.py`, with the revision-5 behaviour as a
mutant flag of the same executor where one exists:
  A08  crash between install-from-buffer and record write: installed binary without a record is C0 only.
  A09  re-run of gov-admit on a store holding anchors, high-waters, per-project records and an admission record (re-admission):
       the store is kept (flag `move_aside_every_run` restores revision 5). A store holding no admission record is first
       admission: it is moved aside (RT-139 unchanged).
  A10  admission of binary N+1 keeps binary N's record; rollback to N passes GB-1 (C2).
  A11  eight concurrent admissions of the same digest on a first-admission machine: with the R-ADM-13 lock no store is moved
       aside after a record exists and exactly one store remains (flag `skip_admission_lock` shows the race).
  A15  a record shipped beside the binary or in a moved-aside store is not honoured (CR5-B-07; flag `record_anywhere`).
Attribution: questions and store shapes follow `4.1.6-review-r5/C-compat-transaction/evidence/probes/admit_tx.py` (AR-0013);
code re-typed. Environment: SCRATCH. Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys, tempfile, threading

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("gov_admit_reference_r6", os.path.join(HERE, "gov_admit_reference_r6.py"))
GA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GA)
S = tempfile.mkdtemp(prefix="adm6-", dir=os.environ["SCRATCH"])
LIN = "sha256:" + "1" * 64
NOW = "2026-09-14T00:00:00Z"


def record(dig):
    return {"binary_digest": dig, "target": "x86_64-unknown-linux-gnu", "release_id": "R1", "lineage": LIN, "state_fingerprint": "gov-fc:11111111:10:" + "a" * 64,
            "admitted_at": NOW, "admitter_digest": "sha256:" + "e" * 64, "valid_until": None, "location_protected": True}


def seed_store(rec_dir, with_record):
    st = GA.store_dir(rec_dir, LIN)
    os.makedirs(os.path.join(st, "projects"), exist_ok=True)
    json.dump({"clock_high_water": "2027-01-01T00:00:00Z", "accepted_tbm": {"root": 3, "policy": 5, "state": 10}}, open(os.path.join(st, "high-water.json"), "w"))
    json.dump([{"sequence": 10, "digest": "sha256:" + "d" * 64, "method": "human"}], open(os.path.join(st, "anchors.json"), "w"))
    json.dump({"highest_installed_sequence": 10}, open(os.path.join(st, "projects", "P1.json"), "w"))
    if with_record:
        os.makedirs(os.path.join(st, "admissions"), exist_ok=True)
        json.dump(record(GA.sha256d(b"binary-v0")), open(os.path.join(st, "admissions", GA.sha256d(b"binary-v0").replace(":", "-") + ".json"), "w"))
    return st


def rel(p):
    return os.path.relpath(p, S) if p else None


res = {}
# A08
d08 = os.path.join(S, "a08")
dig1 = GA.sha256d(b"binary-v1")
exe = os.path.join(d08, "bin", "gov")
inst = GA.install_from_buffer(b"binary-v1", exe, dig1)
res["A08_crash_after_install_before_record"] = {"reread_equal": inst["reread_equal"], "C0": GA.gov_run(exe, "C0", os.path.join(d08, "records"), NOW, [], "C0_C2")["result"],
                                                "C2": GA.gov_run(exe, "C2", os.path.join(d08, "records"), NOW, [], "C0_C2")["result"],
                                                "C3": GA.gov_run(exe, "C3", os.path.join(d08, "records"), NOW, [], "C0_C2")["result"]}

# A09
for label, flags in (("r6", {}), ("mutant_move_aside_every_run (revision 5)", {"move_aside_every_run": True})):
    rd = os.path.join(S, "a09-" + re.sub(r"\W+", "_", label), "records")
    st = seed_store(rd, with_record=True)
    first = GA.is_first_admission(rd, LIN)
    rp, st2, moved = GA.write_admission_record(record(dig1), rd, LIN, flags)
    res["A09_readmission_store_with_record_" + label] = {"is_first_admission": first, "moved_aside": rel(moved),
                                                         "kept": {f: os.path.exists(os.path.join(st2, f)) for f in ("high-water.json", "anchors.json", "projects/P1.json")},
                                                         "earlier_record_kept": os.path.exists(os.path.join(st2, "admissions", GA.sha256d(b"binary-v0").replace(":", "-") + ".json"))}
rd = os.path.join(S, "a09-no-record", "records")
seed_store(rd, with_record=False)
first = GA.is_first_admission(rd, LIN)
rp, st2, moved = GA.write_admission_record(record(dig1), rd, LIN)
res["A09b_store_without_any_admission_record_is_first_admission (RT-139)"] = {"is_first_admission": first, "moved_aside": rel(moved),
                                                                                "anchors_in_new_store": os.path.exists(os.path.join(st2, "anchors.json"))}

# A10
rd = os.path.join(S, "a10", "records")
exe1 = os.path.join(S, "a10", "bin-v1", "gov")
exe2 = os.path.join(S, "a10", "bin-v2", "gov")
GA.install_from_buffer(b"binary-v1", exe1, dig1)
dig2 = GA.sha256d(b"binary-v2")
GA.install_from_buffer(b"binary-v2", exe2, dig2)
GA.write_admission_record(record(dig1), rd, LIN)
_, _, mv2 = GA.write_admission_record(record(dig2), rd, LIN)
res["A10_admit_N_plus_1_keeps_N"] = {"moved_on_second_admission": rel(mv2), "rollback_to_v1_C2": GA.gov_run(exe1, "C2", rd, NOW, [], "C0_C2")["result"],
                                     "v2_C2": GA.gov_run(exe2, "C2", rd, NOW, [], "C0_C2")["result"]}


# A11
def race(flags, label):
    rd = os.path.join(S, "a11-" + label, "records")
    os.makedirs(rd, exist_ok=True)
    errs = []
    barrier = threading.Barrier(8)

    def adm():
        try:
            barrier.wait()
            GA.write_admission_record(record(dig1), rd, LIN, flags)
        except Exception as e:
            errs.append(repr(e))
    ts = [threading.Thread(target=adm) for _ in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    strays = sorted(d for d in os.listdir(rd) if "pre-admission" in d)
    stray_with_records = [d for d in strays if os.path.isdir(os.path.join(rd, d, "admissions")) and os.listdir(os.path.join(rd, d, "admissions"))]
    return {"errors": errs, "stores": sorted(d for d in os.listdir(rd) if d.startswith("vts-")), "moved_aside_stores_holding_a_record": len(stray_with_records),
            "moved_aside_stores": len(strays)}


a11 = {"r6_lock": race({}, "lock")}
unlocked = [race({"skip_admission_lock": True}, "nolock-%d" % i) for i in range(20)]
a11["mutant_skip_admission_lock_20_trials"] = {"trials_with_a_moved_aside_store_holding_a_record": sum(1 for u in unlocked if u["moved_aside_stores_holding_a_record"]),
                                                "trials_with_errors": sum(1 for u in unlocked if u["errors"]), "first_trial": unlocked[0]}
res["A11_concurrent_first_admissions"] = a11

# A15
rd = os.path.join(S, "a15", "records")
exe15 = os.path.join(S, "a15", "pkg", "bin", "gov")
GA.install_from_buffer(b"binary-v1", exe15, dig1)
os.makedirs(os.path.join(rd, "pkg-shipped"), exist_ok=True)
json.dump(record(dig1), open(os.path.join(rd, "pkg-shipped", "admission.json"), "w"))
os.makedirs(os.path.join(rd, "vts-" + LIN[:16] + ".pre-admission-0", "admissions"), exist_ok=True)
json.dump(record(dig1), open(os.path.join(rd, "vts-" + LIN[:16] + ".pre-admission-0", "admissions", dig1.replace(":", "-") + ".json"), "w"))
res["A15_record_outside_store"] = {"r6": GA.gov_run(exe15, "C2", rd, NOW, [], "C0_C2")["result"],
                                   "mutant_record_anywhere (revision 5)": GA.gov_run(exe15, "C2", rd, NOW, [], "C0_C2", {"record_anywhere": True})["result"]}

R = res
res["verdicts"] = {
    "A08_fail_closed": R["A08_crash_after_install_before_record"]["C0"] == "ALLOWED" and R["A08_crash_after_install_before_record"]["C2"] == "BINARY_NOT_ADMITTED"
        and R["A08_crash_after_install_before_record"]["C3"] == "BINARY_NOT_ADMITTED",
    "A09_readmission_keeps_store": not R["A09_readmission_store_with_record_r6"]["is_first_admission"] and R["A09_readmission_store_with_record_r6"]["moved_aside"] is None
        and all(R["A09_readmission_store_with_record_r6"]["kept"].values()) and R["A09_readmission_store_with_record_r6"]["earlier_record_kept"],
    "A09_mutant_revision5_discards_store": R["A09_readmission_store_with_record_mutant_move_aside_every_run (revision 5)"]["moved_aside"] is not None,
    "A09b_first_admission_moves_recordless_store": R["A09b_store_without_any_admission_record_is_first_admission (RT-139)"]["is_first_admission"]
        and R["A09b_store_without_any_admission_record_is_first_admission (RT-139)"]["moved_aside"] is not None
        and not R["A09b_store_without_any_admission_record_is_first_admission (RT-139)"]["anchors_in_new_store"],
    "A10_rollback_keeps_record": R["A10_admit_N_plus_1_keeps_N"]["moved_on_second_admission"] is None and R["A10_admit_N_plus_1_keeps_N"]["rollback_to_v1_C2"] == "ALLOWED",
    "A11_lock_no_record_moved_aside_one_store": a11["r6_lock"]["moved_aside_stores_holding_a_record"] == 0 and len(a11["r6_lock"]["stores"]) == 1 and not a11["r6_lock"]["errors"],
    "A15_record_outside_store_not_honoured": R["A15_record_outside_store"]["r6"] == "BINARY_NOT_ADMITTED" and R["A15_record_outside_store"]["mutant_record_anywhere (revision 5)"] == "ALLOWED",
}
res["note_A11_mutant"] = "the unlocked race is timing-dependent; its count is reported, not asserted"
txt = json.dumps({"probe": "ADM6 admission-record transactions (AR-0015)", **res}, indent=1, sort_keys=True).replace(S, "<scratch>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
