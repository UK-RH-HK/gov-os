#!/usr/bin/env python3
"""AR-0013 held-out transaction attacks on the gov-admit reference executor (`31`) as transactional state.

The gov-admit reference (`evidence/r5/gov_admit_reference.py`) is architecture evidence, not the product; these probes test
the transactional PROPERTIES its `install_from_buffer` / `write_admission_record` / `gov_run` claim, to falsify the design's
crash-safety and monotonicity assertions:
  RV5-C-A08  crash between install-from-buffer and record-write -> installed binary but no record -> C0 only (fail closed)?
  RV5-C-A09  re-run gov-admit on an already-provisioned machine (VTS present): does R-ADM-8's move-aside silently discard the
             machine's monotonic verifier trust store (anchors.json, high-water.json, per-project records)?
  RV5-C-A10  rollback to a previously admitted binary: does its admission record survive a later normal admission (no move
             aside), so GB-1 still admits it?
  RV5-C-A11  concurrent same-digest admissions racing on move-aside + record write.
Scratch only.
Usage: admit_tx.py <out-dir>
"""
import importlib.util, json, os, sys, shutil, threading
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c5lib as L  # noqa

GA_PATH = os.path.join(L.PACK, "evidence", "r5", "gov_admit_reference.py")
spec = importlib.util.spec_from_file_location("gov_admit_reference", GA_PATH)
GA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GA)


def main():
    OUT = os.path.abspath(sys.argv[1])
    os.makedirs(OUT, exist_ok=True)
    S = os.path.join(OUT, "scratch")
    os.makedirs(S, exist_ok=True)
    LIN = "sha256:" + "1" * 64
    DIG = GA.sha256d(b"binary-v1-bytes")
    res = {}

    # RV5-C-A08: crash between install and record. Model: install succeeds, record write never happens.
    dest = os.path.join(S, "a08", "bin", "gov")
    r = GA.install_from_buffer(b"binary-v1-bytes", dest, DIG)
    # no record written
    rec_dir = os.path.join(S, "a08", "records")
    gr = GA.gov_run(dest, "C3", rec_dir, "2026-09-14T00:00:00Z", [], "C0_C2")
    gr0 = GA.gov_run(dest, "C0", rec_dir, "2026-09-14T00:00:00Z", [], "C0_C2")
    res["RV5-C-A08_crash_after_install_before_record"] = {
        "installed_digest_equals_measured": r["reread_equal"], "installed_file_present": os.path.isfile(dest),
        "C3_without_record": gr["result"], "C0_without_record": gr0["result"],
        "fail_closed": gr["result"] == "BINARY_NOT_ADMITTED" and gr0["result"] == "ALLOWED"}

    # RV5-C-A09: re-run gov-admit on a machine whose VTS holds monotonic state.
    rec_dir = os.path.join(S, "a09", "records")
    vts = os.path.join(rec_dir, "vts-" + LIN[:16])
    os.makedirs(vts, exist_ok=True)
    # simulate an established monotonic verifier trust store
    json.dump({"clock_high_water": "2027-01-01T00:00:00Z", "accepted_tbm": {"root": 3, "policy": 5, "state": 10}},
              open(os.path.join(vts, "high-water.json"), "w"))
    json.dump([{"sequence": 10, "digest": "sha256:" + "d" * 64, "method": "human"}], open(os.path.join(vts, "anchors.json"), "w"))
    os.makedirs(os.path.join(vts, "projects"), exist_ok=True)
    json.dump({"highest_installed_sequence": 10, "project_strength_vector": ["confidential"]},
              open(os.path.join(vts, "projects", "P1.json"), "w"))
    prior = sorted(os.listdir(vts))
    rec = {"binary_digest": DIG, "target": "x86_64-unknown-linux-gnu", "release_id": "R1", "lineage": LIN,
           "state_fingerprint": "gov-state:11111111:10:" + "a" * 32, "admitted_at": "2026-09-14T00:00:00Z",
           "admitter_digest": "sha256:" + "e" * 64, "valid_until": None, "location_protected": True}
    rp, new_vts, moved = GA.write_admission_record(rec, rec_dir, LIN)
    after = sorted(os.listdir(new_vts))
    res["RV5-C-A09_readmit_moves_aside_monotonic_vts"] = {
        "vts_had_high_water_anchors_projects": prior,
        "moved_aside": moved is not None, "moved_to": (os.path.relpath(moved, S) if moved else None),
        "new_vts_contents": after,
        "high_water_present_after": os.path.exists(os.path.join(new_vts, "high-water.json")),
        "anchors_present_after": os.path.exists(os.path.join(new_vts, "anchors.json")),
        "projects_present_after": os.path.isdir(os.path.join(new_vts, "projects")),
        "note": "R-ADM-8 says move-aside is 'at first admission'; the reference fires whenever the VTS dir exists, so a re-run of gov-admit discards the machine's clock high-water, anchors and per-project records"}

    # RV5-C-A10: rollback to a previously admitted binary — its record must survive a later *normal* record write.
    rec_dir = os.path.join(S, "a10", "records")
    r1 = dict(rec); r1["binary_digest"] = DIG
    GA.write_admission_record(r1, rec_dir, LIN)  # first admission (v1)
    DIG2 = GA.sha256d(b"binary-v2-bytes")
    r2 = dict(rec); r2["binary_digest"] = DIG2
    # a later admission of v2 by an already-admitted gov — the reference write_admission_record still MOVES ASIDE the vts
    _, nv, mv = GA.write_admission_record(r2, rec_dir, LIN)
    v1_present = any("admission-%s" % DIG[:24] in f for f in os.listdir(nv))
    v2_present = any("admission-%s" % DIG2[:24] in f for f in os.listdir(nv))
    res["RV5-C-A10_rollback_prev_binary_record_survival"] = {
        "v2_admission_moved_v1_record_aside": mv is not None, "v1_record_in_current_vts": v1_present,
        "v2_record_in_current_vts": v2_present,
        "note": "AP-10 (running mode) must add a record WITHOUT R-ADM-8; the reference's write_admission_record always move-asides, so a second admission drops the earlier binary's record -> rollback to v1 would be BINARY_NOT_ADMITTED unless the running path is different from gov-admit's"}

    # RV5-C-A11: concurrent same-digest admissions
    rec_dir = os.path.join(S, "a11", "records")
    errs = []
    def adm():
        try:
            GA.write_admission_record(dict(rec), rec_dir, LIN)
        except Exception as e:
            errs.append(repr(e))
    ts = [threading.Thread(target=adm) for _ in range(8)]
    for t in ts: t.start()
    for t in ts: t.join()
    vdir = os.path.join(rec_dir, "vts-" + LIN[:16])
    res["RV5-C-A11_concurrent_admissions"] = {"errors": errs, "final_vts_entries": sorted(os.listdir(vdir)) if os.path.isdir(vdir) else None,
                                             "stray_pre_admission_dirs": sorted(d for d in os.listdir(rec_dir) if "pre-admission" in d)}
    L.dump(res, os.path.join(OUT, "admit_tx.json"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
