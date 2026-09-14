#!/usr/bin/env python3
"""RV6-B-A04 — re-admission keeps the store but does not consult it: an older genuine binary below the kept accepted-TBM
high-water is admitted and runs (review r6 reviewer B, AR-0016). Executed (reference executor) + code.
Scratch only; the repository is never written.

Pack text relied on (design, 4106885): `31` R-ADM-8′ (re-admission "keeps the store: anchors, clock and accepted-TBM
high-waters, per-project records, earlier admission records"), §2 ("no admission discards the monotonic state of an earlier
one"); `25` AP-8 ("Running mode only: root version, policy version and state sequence ≥ the accepted-TBM high-water of this
verifier trust store"), §7 row "a genuine older binary presented as an upgrade | no | BINARY_T0_ROLLBACK"; `21` OP-14 (b)
("periodic re-admission, which keeps the verifier trust store"), OP-15 (a); `24` §8 (`accepted_tbm` never decreases).

Instruments, loaded by path and NOT modified: `evidence/r6/gov_admit_reference_r6.py` (`accept`, `write_admission_record`,
`is_first_admission`, `gov_run`); FA5's world executed from a scratch copy transformed as FA6 S1 does (SUBS copied with
attribution). The committed P4r5 and P4r6 outputs are read for the running-mode row `RV3-D-A13r5_older_binary_after_newer`.

World: FA5's lineage (root v2, TPS1 quorum 2), T10 publishing B8 (TBM: root 2, policy 1, state 9). Added here with FA5's own
builders: release R9 (source, inputs, candidate, ACCEPTED attestation, final, registration by g1+g2, reproductions by p1+p4),
binary B9 (TBM: root 2, policy 1, state 10) and T11 (publishes B8 and B9, keeps every revocation).

Steps
  1  First admission of B9 with the genuine code of T11 (two sources): accepted; record written; the store is given the
     accepted-TBM high-water of B9 (2, 1, 10) and a human anchor at t11, as ADM6 A09 constructs a store.
  2  The record expires (OP-14 (b)): `gov_run(B9, C2)`.
  3  Re-admission with the genuine current code of T11; a carrier supplies B8, genuine, published and not revoked.
  4  The re-admitted B8 runs: `gov_run(B8, C2)`; the store's high-water is still above B8's TBM.
  5  Running mode for the same shape (committed oracle rows): refused with `BINARY_T0_ROLLBACK`.
Environment: REVIEW_REPO (export of 4106885), SCRATCH, GOV (legacy 4.1.5; FA5 prefix only). Output: JSON on stdout.
"""
import contextlib, hashlib, inspect, io, json, os, shutil, sys, tempfile

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
R6 = os.path.join(PK, "evidence", "r6")
SCR = tempfile.mkdtemp(prefix="a04-", dir=os.environ["SCRATCH"])
R6_PATH = os.path.join(R6, "gov_admit_reference_r6.py")
FA5_PATH = os.path.join(PK, "evidence", "r5", "FA5-first-admission.py")
SUBS = [  # FA6 SUBS (AR-0015), verbatim
    ('"inputs_manifest_digest": INP7}', '"inputs_manifest_digest": INP7, "kernel_tree_digest": sha256d(b"kernel-R7")}'),
    ('"inputs_manifest_digest": INP8}', '"inputs_manifest_digest": INP8, "kernel_tree_digest": sha256d(b"kernel-R8")}'),
    ('"verification_records": [VA7["digest"]], "units": {}}', '"verification_records": [VA7["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R7"), "units": {}}}'),
    ('"verification_records": [VA8["digest"]], "units": {}}', '"verification_records": [VA8["digest"]], "units": {}, "constitution": {"kernel_tree_digest": sha256d(b"kernel-R8"), "units": {}}}'),
    ('json_path = os.path.join(HERE, "FA5-first-admission.json")', 'json_path = os.path.join(HERE, "FA5-on-r6.json")'),
]
D1 = os.path.join(SCR, "fa5-on-r6")
os.makedirs(D1)
shutil.copyfile(R6_PATH, os.path.join(D1, "gov_admit_reference.py"))
src = open(FA5_PATH).read()
for a, b in SUBS:
    src = src.replace(a, b)
open(os.path.join(D1, "FA5-first-admission.py"), "w").write(src)
cut = src.index("# ========== CONFORMANCE VECTORS ==========")
os.environ["FA5_SCRATCH"] = os.path.join(SCR, "fa5prefix")
os.makedirs(os.environ["FA5_SCRATCH"], exist_ok=True)
G = {"__file__": os.path.join(D1, "FA5-first-admission.py"), "__name__": "fa5_prefix"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:cut], "FA5-prefix", "exec"), G)
GA = G["GA"]
g = lambda n: G[n]
envelope, to_stmts, canon, sha256d = g("envelope"), g("to_stmts"), g("canon"), g("sha256d")
V = GA.Verifier(SCR)
TARGET, LINEAGE, ADM_D = g("TARGET"), g("LINEAGE"), g("ADMITTER_DIGEST")

# ---- release R9 and T11, built with FA5's builders
SRC9, INP9 = g("src")("R9"), sha256d(b"inputs-R9")
CAND9 = sha256d(canon({"kind": "candidate", "release_id": "R9", "source": SRC9}))
K9 = sha256d(b"kernel-R9")
VA9 = envelope("verification-attestation+json", {"candidate_statement_digest": CAND9, "verdict": "ACCEPTED", "source": SRC9, "inputs_manifest_digest": INP9, "kernel_tree_digest": K9}, ["v1"])
FINAL9 = envelope("release-final+json", {"release_id": "R9", "sequence": 9, "promoted_from": CAND9, "source": SRC9, "kernel_tree_digest": K9}, ["f1"])
REG9 = envelope("release-registration+json", {"release_id": "R9", "sequence": 9, "final_statement_digest": FINAL9["digest"], "candidate_statement_digest": CAND9, "source": SRC9,
                                               "inputs_manifest_digest": INP9, "targets": [TARGET], "verification_records": [VA9["digest"]], "units": {},
                                               "constitution": {"kernel_tree_digest": K9, "units": {}}}, ["g1", "g2"])
T10 = g("T10")
TBM9 = g("make_tbm")(2, 1, 10, T10["digest"], SRC9, INP9)
B9_BYTES, B9_D = g("make_binary")("B9", TBM9)
RP9 = [g("repro")("R9", SRC9, INP9, TARGET, B9_D, sha256d(canon(TBM9)), k) for k in ("p1", "p4")]
T11 = envelope("trust-state+json", {"sequence": 11, "issued_at": "2026-09-14T00:00:00Z",
                                    "references": {"root": {"version": 2, "digest": g("ROOT2")["digest"]}, "trust_policy": {"version": 1, "digest": g("TPS1")["digest"]}},
                                    "prior_states": g("PRIOR10") + [{"sequence": 10, "digest": T10["digest"]}],
                                    "registrations": [g("REG7")["digest"], g("REG8")["digest"], REG9["digest"]],
                                    "published_binaries": sorted([g("B7_D"), g("B7x_D"), g("B8_D"), B9_D]), "revocations": g("REVS9")}, ["ts1"])
BUNDLE = g("FULL") + [T11, VA9, FINAL9, REG9] + RP9
FCM11 = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, g("TPS1")["digest"], 11, T11["digest"], {TARGET: ADM_D}, "2026-09-14T00:00:00Z")
CODE11 = GA.first_contact_code(FCM11)
COMP = {"channel_quorum": 2, "lineage": None}
NOW = "2026-09-14T00:00:00Z"


def admit(binary):
    return GA.accept(binary, [CODE11, CODE11], to_stmts(BUNDLE), TARGET, ADM_D, verifier=V, workdir=SCR, first_contact_manifest=GA.fcm_bytes(FCM11), compiled=COMP, now=NOW)


REC = os.path.join(SCR, "vts-root")
BIN = os.path.join(SCR, "bin")
os.makedirs(BIN)
out = {"probe": "RV6-B-A04 re-admission rollback below the kept accepted-TBM high-water (AR-0016)", "executor_sha256": hashlib.sha256(open(R6_PATH, "rb").read()).hexdigest()}

# 1 first admission of B9
r1 = admit(B9_BYTES)
inst9 = GA.install_from_buffer(B9_BYTES, os.path.join(BIN, "gov-B9"), B9_D)
rec9 = {"schema": "governance-os.admission-record/2", "binary_digest": B9_D, "target": TARGET, "release_id": "R9", "lineage": LINEAGE, "first_contact_code": CODE11,
        "admitted_at": "2026-01-01T00:00:00Z", "admitter_digest": ADM_D, "valid_until": "2026-06-01T00:00:00Z", "location_protected": inst9["location_protected"]}
first = GA.is_first_admission(REC, LINEAGE)
_, store, moved1 = GA.write_admission_record(rec9, REC, LINEAGE)
json.dump({"clock_high_water": "2026-09-14T00:00:00Z", "accepted_tbm": {"root": 2, "policy": 1, "state": 10}}, open(os.path.join(store, "high-water.json"), "w"))
json.dump([{"sequence": 11, "digest": T11["digest"], "method": "human"}], open(os.path.join(store, "anchors.json"), "w"))
out["step1_first_admission_B9"] = {"result": r1["result"], "is_first_admission": first, "moved_aside": moved1 is not None, "tbm": {"root": 2, "policy": 1, "state": 10}}

# 2 record expired
out["step2_B9_record_expired_C2"] = GA.gov_run(os.path.join(BIN, "gov-B9"), "C2", REC, NOW, [], "C0_C2")["result"]

# 3 re-admission, carrier supplies older genuine B8
r3 = admit(g("B8_BYTES"))
inst8 = GA.install_from_buffer(g("B8_BYTES"), os.path.join(BIN, "gov-B8"), g("B8_D"))
rec8 = dict(rec9, binary_digest=g("B8_D"), release_id="R8", admitted_at=NOW, valid_until="2026-12-01T00:00:00Z", location_protected=inst8["location_protected"])
first3 = GA.is_first_admission(REC, LINEAGE)
_, store3, moved3 = GA.write_admission_record(rec8, REC, LINEAGE)
hw = json.load(open(os.path.join(store3, "high-water.json")))
out["step3_readmission_B8"] = {"result": r3["result"], "is_first_admission": first3, "store_kept": moved3 is None and store3 == store, "store_high_water_after": hw,
                               "B8_tbm": {"root": 2, "policy": 1, "state": 9}, "B8_published_in_T11": g("B8_D") in T11["payload"]["published_binaries"], "B8_revoked_in_T11": g("B8_D") in T11["payload"]["revocations"]}

# 4 B8 runs
out["step4_B8_runs_C2"] = GA.gov_run(os.path.join(BIN, "gov-B8"), "C2", REC, NOW, [], "C0_C2")["result"]
out["step4_store_high_water_exceeds_running_binary_tbm_state"] = hw["accepted_tbm"]["state"] > 9

# code: bootstrap-mode predicate has no store input; the genuine-binary rule reads no TBM high-water
out["code"] = {
    "accept_parameters": list(inspect.signature(GA.accept).parameters),
    "accept_reads_accepted_tbm_or_high_water": any(w in inspect.getsource(GA.accept) for w in ("accepted_tbm", "high-water", "high_water")),
    "gov_run_reads_accepted_tbm_or_tbm": any(w in inspect.getsource(GA.gov_run) for w in ("accepted_tbm", "tbm", "high_water")),
}
# 5 running-mode rows (committed oracle outputs)
def find_rows(path, needle):
    j = json.load(open(path))
    hits = []
    def walk(o, pre=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if needle in str(k):
                    hits.append({"key": pre + "/" + str(k), "value": v if not isinstance(v, (dict, list)) else {kk: vv for kk, vv in (v.items() if isinstance(v, dict) else []) if kk in ("observed", "expected", "holds", "result", "code")}})
                walk(v, pre + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if isinstance(v, dict) and needle in json.dumps(v)[:300]:
                    hits.append({"key": pre + "[%d]" % i, "value": {kk: vv for kk, vv in v.items() if kk in ("id", "observed", "expected", "holds", "result")}})
                walk(v, pre + "[%d]" % i)
    walk(j)
    return hits[:4]
out["step5_running_mode_committed_rows"] = {
    "P4r5": find_rows(os.path.join(PK, "evidence", "r5", "P4r5-conformance-oracle.json"), "RV3-D-A13r5_older_binary_after_newer"),
    "P4r6_p4r5_under_r6": find_rows(os.path.join(R6, "P4r6-conformance-oracle.json"), "RV3-D-A13r5_older_binary_after_newer"),
}
pack = open(os.path.join(PK, "25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md")).read()
out["design"] = {
    "25_AP8_running_mode_only": "Running mode only: root version, policy version and state sequence" in pack,
    "25_s7_older_binary_row": [l for l in pack.splitlines() if l.startswith("| a genuine older binary")],
}
out["verdicts"] = {
    "first_admission_B9_accepted": r1["result"] == "ACCEPTED",
    "expired_record_blocks_C2": out["step2_B9_record_expired_C2"] == "ADMISSION_RECORD_EXPIRED",
    "readmission_is_not_first_admission_and_keeps_store": (not first3) and out["step3_readmission_B8"]["store_kept"],
    "readmission_accepts_older_genuine_B8_below_kept_high_water": r3["result"] == "ACCEPTED" and out["step4_store_high_water_exceeds_running_binary_tbm_state"],
    "older_B8_runs_C2_after_readmission": out["step4_B8_runs_C2"] == "ALLOWED",
    "bootstrap_predicate_has_no_store_input": not out["code"]["accept_reads_accepted_tbm_or_high_water"],
}
txt = json.dumps(out, indent=1, sort_keys=True)
print(txt.replace(SCR, "<scratch>").replace(REPO, "<export>"))
