#!/usr/bin/env python3
"""RV6-D-A02 — re-admission keeps the verifier trust store but reads none of it: anchors, held negatives, accepted-TBM
high-water (review r6 synthesis D, AR-0018). Executed (reference executor) + code + design. Scratch only.

Extends reviewer B's RV6-B-A04 (accepted-TBM high-water) to the store's anchors and held negative facts. The world, R9, B9
and T11 are built with FA5's builders exactly as RV6-B-A04 builds them (copied with attribution).

Pack text relied on: `31` R-ADM-8′ (re-admission "keeps the store"), §2 ("no admission discards the monotonic state of an
earlier one"), R-ADM-3′ (inputs of `gov-admit`); `17` MS-1 / D-0008 rule (7) (negative facts are sticky); `32` §10 RS-B1
("A stale page selects the state its code names … the admitted binary anchors next"); `09` R-ART-2 (a binary refuses trusted
operations below the accepted-TBM high-water); `21` §17 row "OP-14 (b) or OP-15 (a) + OP-13 (b)/(c)/(d)".

Steps
  1  First admission of B9 with the genuine code of T11; the store receives the record, a human anchor at t11, the accepted-TBM
     high-water (2, 1, 10) and the held statement T11, whose revocations name B7 and B7x.
  2  The record expires (OP-14 (b)).
  3  Re-admission with a first-contact value naming T7 (issued 2026-05-01, no `valid_until`): (a)/(b) a stale owner code;
     (c) "either" a replayed package manifest (compiled lineage). Candidates: B7x (malicious, revoked at T9, revocation held
     in the store) and B7 (genuine, revoked at T9).
  4  The store after re-admission; `gov_run` of the re-admitted genuine B7 with the store's held negatives (GB-3); B8 older
     binary (RV6-B-A04 shape) against R-ART-2.
Controls: the current code of T11 with B7x; first admission (no store) with the T7 value (RS-B1, as stated).
Environment: REVIEW_REPO, SCRATCH, GOV. Output: JSON on stdout.
"""
import hashlib, inspect, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d6world as W

SCR = tempfile.mkdtemp(prefix="da02-", dir=os.environ["SCRATCH"])
G, D1, ADM_BYTES = W.load(SCR)
GA = G["GA"]
g = lambda n: G[n]
envelope, to_stmts, canon, sha256d = g("envelope"), g("to_stmts"), g("canon"), g("sha256d")
V = GA.Verifier(SCR)
TARGET, LINEAGE, ADM_D = g("TARGET"), g("LINEAGE"), g("ADMITTER_DIGEST")
NOW = "2026-09-14T00:00:00Z"

# ---- R9, B9, T11 exactly as RV6-B-A04 (AR-0016) builds them with FA5's builders
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
T7, TPS1 = g("T7"), g("TPS1")
FCM7 = GA.make_fcm(LINEAGE, 1, LINEAGE, 1, TPS1["digest"], 7, T7["digest"], {TARGET: ADM_D}, "2026-05-01T00:00:00Z")
CODE7 = GA.first_contact_code(FCM7)
OLD = [g("ROOT1"), TPS1, g("T1"), g("T5"), g("T6"), T7, g("VA7"), g("FINAL7"), g("REG7")]
COMP_AB = {"channel_quorum": 2, "lineage": None}
COMP_C = {"channel_quorum": 2, "lineage": LINEAGE}


def admit(binary, code, fcm, bundle, comp):
    return GA.accept(binary, [code, code], to_stmts(bundle), TARGET, ADM_D, verifier=V, workdir=SCR, first_contact_manifest=GA.fcm_bytes(fcm), compiled=comp, now=NOW)


def record(digest, rid, valid_until, loc):
    return {"schema": "governance-os.admission-record/2", "binary_digest": digest, "target": TARGET, "release_id": rid, "lineage": LINEAGE, "first_contact_code": CODE11,
            "admitted_at": NOW, "admitter_digest": ADM_D, "valid_until": valid_until, "location_protected": loc}


REC = os.path.join(SCR, "records")
BIN = os.path.join(SCR, "bin")
os.makedirs(BIN)
out = {"probe": "RV6-D-A02 re-admission ignores the kept store's anchors, negatives and TBM high-water (AR-0018)",
       "executor_sha256": hashlib.sha256(open(W.R6_PATH, "rb").read()).hexdigest(),
       "world": {"B7x_revoked_in_T11": g("B7x_D") in T11["payload"]["revocations"], "B7_revoked_in_T11": g("B7_D") in T11["payload"]["revocations"],
                 "B7x_published_in_T7": g("B7x_D") in T7["payload"].get("published_binaries", []), "B7x_revoked_in_T7": g("B7x_D") in T7["payload"].get("revocations", [])}}

# 1 first admission of B9, store populated
r1 = admit(B9_BYTES, CODE11, FCM11, BUNDLE, COMP_AB)
inst9 = GA.install_from_buffer(B9_BYTES, os.path.join(BIN, "gov-B9"), B9_D)
_, store, moved1 = GA.write_admission_record(record(B9_D, "R9", "2026-06-01T00:00:00Z", inst9["location_protected"]), REC, LINEAGE)
os.makedirs(os.path.join(store, "statements"))
json.dump(T11, open(os.path.join(store, "statements", T11["digest"].replace(":", "-") + ".json"), "w"), sort_keys=True)
json.dump({"clock_high_water": NOW, "accepted_tbm": {"root": 2, "policy": 1, "state": 10}}, open(os.path.join(store, "high-water.json"), "w"))
json.dump([{"sequence": 11, "digest": T11["digest"], "method": "human"}], open(os.path.join(store, "anchors.json"), "w"))
held_negatives = sorted(T11["payload"]["revocations"])
out["step1_first_admission_B9"] = {"result": r1["result"], "moved_aside": moved1 is not None, "store_anchor_sequence": 11}

# 2 expiry
out["step2_B9_C2_after_expiry"] = GA.gov_run(os.path.join(BIN, "gov-B9"), "C2", REC, NOW, held_negatives, "C0_C2")["result"]

# 3 re-admission with a T7 first-contact value
rows = {}
for label, comp in (("OP13_a_b_stale_owner_code", COMP_AB), ("OP13_c_either_replayed_package_manifest", COMP_C)):
    for cand, bytes_, reps in (("B7x_malicious_revoked", g("B7x_BYTES"), g("RP7x")), ("B7_genuine_revoked", g("B7_BYTES"), g("RP7"))):
        r = admit(bytes_, CODE7, FCM7, OLD + reps, comp)
        rows["%s|%s" % (label, cand)] = {"result": r["result"], "selected_state_sequence": (r.get("selected_state") or {}).get("sequence")}
out["step3_readmission_with_T7_value"] = rows
first3 = GA.is_first_admission(REC, LINEAGE)
inst7x = GA.install_from_buffer(g("B7x_BYTES"), os.path.join(BIN, "gov-B7x"), g("B7x_D"))
_, store3, moved3 = GA.write_admission_record(record(g("B7x_D"), "R7", "2026-12-01T00:00:00Z", inst7x["location_protected"]), REC, LINEAGE)
inst7 = GA.install_from_buffer(g("B7_BYTES"), os.path.join(BIN, "gov-B7"), g("B7_D"))
GA.write_admission_record(record(g("B7_D"), "R7", "2026-12-01T00:00:00Z", inst7["location_protected"]), REC, LINEAGE)
out["step4_store_after_readmission"] = {
    "is_first_admission_before_readmission": first3, "store_kept": moved3 is None and store3 == store,
    "store_anchor_sequences": [a["sequence"] for a in json.load(open(os.path.join(store3, "anchors.json")))],
    "store_holds_revocation_of_B7x": g("B7x_D") in held_negatives, "records": sorted(os.listdir(os.path.join(store3, "admissions"))),
    "B7_genuine_runs_C2_with_held_negatives_OP15a": GA.gov_run(os.path.join(BIN, "gov-B7"), "C2", REC, NOW, held_negatives, "C0_only")["result"],
    "B7_genuine_runs_C2_with_held_negatives_OP15b": GA.gov_run(os.path.join(BIN, "gov-B7"), "C2", REC, NOW, held_negatives, "C0_C2")["result"],
    "B7x_malicious_bound_by_GB_rules": "no (TB-1′: a malicious binary ignores every rule; its admission record exists)",
}
# controls
out["control_current_code_T11_B7x"] = admit(g("B7x_BYTES"), CODE11, FCM11, BUNDLE, COMP_AB)["result"]
REC2 = os.path.join(SCR, "records-fresh")
out["control_first_admission_no_store_T7_value_B7x_RS_B1_as_stated"] = {"result": admit(g("B7x_BYTES"), CODE7, FCM7, OLD + g("RP7x"), COMP_AB)["result"], "is_first_admission": GA.is_first_admission(REC2, LINEAGE)}

# B8 older binary after re-admission (RV6-B-A04 shape) against R-ART-2
r8 = admit(g("B8_BYTES"), CODE11, FCM11, BUNDLE, COMP_AB)
inst8 = GA.install_from_buffer(g("B8_BYTES"), os.path.join(BIN, "gov-B8"), g("B8_D"))
GA.write_admission_record(record(g("B8_D"), "R8", "2026-12-01T00:00:00Z", inst8["location_protected"]), REC, LINEAGE)
t09, t12, t31, t32, t25, t21, t17 = (W.pack(n) for n in ("09-INTEGRATION-REQUIREMENTS.md", "12-ACCEPTANCE-TEST-PLAN.md", "31-INDEPENDENT-ADMISSION.md", "32-FIRST-CONTACT-ROOT.md",
                                                       "25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md", "21-OWNER-OPTIONS.md", "17-MONOTONIC-TRUST-STATE.md"))
out["older_binary_B8"] = {"readmission": r8["result"], "reference_gov_run_C2": GA.gov_run(os.path.join(BIN, "gov-B8"), "C2", REC, NOW, held_negatives, "C0_C2")["result"],
                          "09_R_ART_2": W.lines(t09, lambda l: l.startswith("| R-ART-2")),
                          "reference_gov_run_reads_tbm_or_high_water": any(w in inspect.getsource(GA.gov_run) for w in ("accepted_tbm", "tbm", "high_water")),
                          "plan_rows_R_ART_2_or_startup_rollback_after_readmission": [m.group(1) for m in re.finditer(r"^\| \*{0,2}(RT-\d+)[^\n]*", t12, re.M)
                                                                                     if re.search(r"R-ART-2", m.group(0)) or (re.search(r"BINARY_T0_ROLLBACK", m.group(0)) and re.search(r"gov-admit|re-admi|re-run", m.group(0)))]}
out["code"] = {"accept_parameters": list(inspect.signature(GA.accept).parameters),
               "accept_reads_store_anchors_negatives_or_high_water": any(w in inspect.getsource(GA.accept) for w in ("anchors", "high_water", "accepted_tbm", "rec_dir", "store"))}
out["design"] = {
    "31_R_ADM_3_prime": W.lines(t31, lambda l: l.startswith("| **R-ADM-3′**")),
    "31_s2_invariant_sentence": [s for s in re.split(r"(?<=\.)\s", t31) if "monotonic state of an earlier one" in s],
    "32_RS_B1": W.lines(t32, lambda l: l.startswith("| RS-B1")),
    "21_s17_readmission_row": W.lines(t21, lambda l: l.startswith("| OP-14 (b) or OP-15 (a)")),
    "17_negative_facts_sticky": W.lines(t17, lambda l: "MS-1" in l and ("sticky" in l.lower() or "negative" in l.lower()))[:3],
    "any_rule_refusing_a_first_contact_epoch_below_the_store_anchor": bool(re.search(r"below (?:the|its) (?:store'?s?|verifier trust store'?s?) anchor|epoch below the store", t31 + t32 + t25, re.I)),
    "plan_rows_readmission_with_older_value_or_held_revocation": [m.group(1) for m in re.finditer(r"^\| \*{0,2}(RT-\d+)[^\n]*", t12, re.M)
                                                                 if re.search(r"re-admi|re-runs `gov-admit`", m.group(0)) and re.search(r"stale|older (?:first-contact|code|manifest|state|epoch)|below (?:the|its) (?:store'?s? )?anchor|held revocation|revoked in the store|valid_until", m.group(0), re.I)],
    "nearest_plan_row_RT_170": W.lines(t12, lambda l: l.startswith("| RT-170")),
}
acc = lambda x: x == "ACCEPTED"
out["verdicts"] = {
    "world_B7x_revoked_in_held_T11_and_published_in_T7": out["world"]["B7x_revoked_in_T11"] and out["world"]["B7x_published_in_T7"] and not out["world"]["B7x_revoked_in_T7"],
    "readmission_admits_B7x_revoked_in_held_state_a_b": acc(rows["OP13_a_b_stale_owner_code|B7x_malicious_revoked"]["result"]),
    "readmission_admits_B7x_revoked_in_held_state_c_either": acc(rows["OP13_c_either_replayed_package_manifest|B7x_malicious_revoked"]["result"]),
    "readmission_selected_state_below_store_anchor": rows["OP13_a_b_stale_owner_code|B7x_malicious_revoked"]["selected_state_sequence"] == 7,
    "store_kept_and_still_holds_anchor_11_and_revocation": out["step4_store_after_readmission"]["store_kept"] and out["step4_store_after_readmission"]["store_anchor_sequences"] == [11] and out["step4_store_after_readmission"]["store_holds_revocation_of_B7x"],
    "genuine_B7_restricts_itself_by_GB3": out["step4_store_after_readmission"]["B7_genuine_runs_C2_with_held_negatives_OP15a"] == "BINARY_REVOKED_SELF",
    "control_current_code_refuses_B7x": not acc(out["control_current_code_T11_B7x"]),
    "bootstrap_predicate_has_no_store_input": not out["code"]["accept_reads_store_anchors_negatives_or_high_water"],
    "older_B8_reference_runs_C2_while_R_ART_2_requires_refusal": out["older_binary_B8"]["reference_gov_run_C2"] == "ALLOWED" and bool(out["older_binary_B8"]["09_R_ART_2"]),
    "no_rule_refuses_epoch_below_store_anchor": not out["design"]["any_rule_refusing_a_first_contact_epoch_below_the_store_anchor"],
    "no_plan_row": not out["design"]["plan_rows_readmission_with_older_value_or_held_revocation"],
}
print(json.dumps(out, indent=1, sort_keys=True, default=str).replace(SCR, "<scratch>").replace(W.REPO, "<export>"))
