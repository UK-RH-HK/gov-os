#!/usr/bin/env python3
"""RV6-D-A08 — how old may a first-contact value be when it is not read from a live source? (review r6 synthesis D, AR-0018)
Executed (reference executor) + design. Scratch only.

Reviewer B's RV6-B-A05 showed an old platform package under OP-13 (c) "either". The same unbounded age applies wherever the
first-contact code and manifest are stored rather than read now: OP-13 (d) provisioning media ("code, FCM and admitter",
`32` §7), and CI runner images ("codes and FCM provisioned by the image operator from the OP-13 sources", `32` §8, `06` §3).
`valid_until` is optional (`32` §3; schema). `32` §10 FC-R4's bound is "media custody" and RS-B1 names only "a stale page".
World: FA5's (T7 publishes B7 and the malicious B7x; T9 revokes both). For media (k = 1) a T7 Trust State under the quorum-1
Trust Policy `TPS1_Q1` is built with FA5's own `envelope` and trust-state signer `ts1`, identical to FA5's T7 except for the
policy reference, as FA5 builds `T10_Q1` from T10.
Rows: (d) media prepared at T7 used on 2026-09-14 with B7x; the same media with `valid_until` 2026-06-01 (control); current
media (T10_Q1) with B7x (control); CI image with two codes provisioned at T7 under (a)/(b) (compiled quorum 2) with B7x;
the image record's own `valid_until` rule (it bounds the record, not the manifest's age).
Environment: REVIEW_REPO, SCRATCH, GOV. Output: JSON on stdout.
"""
import hashlib, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d6world as W

SCR = tempfile.mkdtemp(prefix="da08-", dir=os.environ["SCRATCH"])
G, D1, ADM_BYTES = W.load(SCR)
GA = G["GA"]
g = lambda n: G[n]
envelope, to_stmts = g("envelope"), g("to_stmts")
V = GA.Verifier(SCR)
TARGET, LINEAGE, ADM_D = g("TARGET"), g("LINEAGE"), g("ADMITTER_DIGEST")
NOW = "2026-09-14T00:00:00Z"
T7, TPS1, TPS1_Q1 = g("T7"), g("TPS1"), g("TPS1_Q1")
p7 = json.loads(json.dumps(T7["payload"]))
p7["references"]["trust_policy"] = {"version": 1, "digest": TPS1_Q1["digest"]}
T7_Q1 = envelope("trust-state+json", p7, ["ts1"])
OLD_Q1 = [g("ROOT1"), TPS1_Q1, g("T1"), g("T5"), g("T6"), T7_Q1, g("VA7"), g("FINAL7"), g("REG7")]
OLD = [g("ROOT1"), TPS1, g("T1"), g("T5"), g("T6"), T7, g("VA7"), g("FINAL7"), g("REG7")]


def fcm(tps, t, seq, root_v, root_d, valid_until=None, issued="2026-05-01T00:00:00Z"):
    return GA.make_fcm(LINEAGE, root_v, root_d, 1, tps["digest"], seq, t["digest"], {TARGET: ADM_D}, issued, valid_until=valid_until)


def run(binary, codes, bundle, comp, m):
    r = GA.accept(binary, codes, to_stmts(bundle), TARGET, ADM_D, verifier=V, workdir=SCR, first_contact_manifest=GA.fcm_bytes(m), compiled=comp, now=NOW)
    return {"result": r["result"], "selected_state_sequence": (r.get("selected_state") or {}).get("sequence"), "age_note": r.get("age_note")}


M_D = {"channel_quorum": 1, "lineage": LINEAGE}
m7q = fcm(TPS1_Q1, T7_Q1, 7, 1, LINEAGE)
m7q_exp = fcm(TPS1_Q1, T7_Q1, 7, 1, LINEAGE, valid_until="2026-06-01T00:00:00Z")
m10q = fcm(TPS1_Q1, g("T10_Q1"), 10, 2, g("ROOT2")["digest"], issued="2026-09-13T00:00:00Z")
m7 = fcm(TPS1, T7, 7, 1, LINEAGE)
out = {"probe": "RV6-D-A08 stale first-contact values on media and CI images (AR-0018)", "executor_sha256": hashlib.sha256(open(W.R6_PATH, "rb").read()).hexdigest(),
       "world": {"T7_Q1_publishes_B7x": g("B7x_D") in T7_Q1["payload"]["published_binaries"], "B7x_revoked_at_T9": g("B7x_D") in g("REVS9")},
       "media_d_prepared_T7_used_now_B7x": run(g("B7x_BYTES"), [GA.first_contact_code(m7q)], OLD_Q1 + g("RP7x"), M_D, m7q),
       "media_d_prepared_T7_used_now_B7_genuine_revoked": run(g("B7_BYTES"), [GA.first_contact_code(m7q)], OLD_Q1 + g("RP7"), M_D, m7q),
       "control_media_with_valid_until_2026_06_01": run(g("B7x_BYTES"), [GA.first_contact_code(m7q_exp)], OLD_Q1 + g("RP7x"), M_D, m7q_exp),
       "control_current_media_T10_Q1_B7x": run(g("B7x_BYTES"), [GA.first_contact_code(m10q)], g("FULL_Q1"), M_D, m10q),
       "ci_image_codes_provisioned_at_T7_a_b_B7x": run(g("B7x_BYTES"), [GA.first_contact_code(m7)] * 2, OLD + g("RP7x"), {"channel_quorum": 2, "lineage": None}, m7)}
t32, t06, t31, t21 = W.pack("32-FIRST-CONTACT-ROOT.md"), W.pack("06-BOOTSTRAP.md"), W.pack("31-INDEPENDENT-ADMISSION.md"), W.pack("21-OWNER-OPTIONS.md")
schema = json.load(open(os.path.join(W.PK, "schemas", "first-contact-manifest.schema.json")))
out["design"] = {
    "schema_requires_valid_until": "valid_until" in schema["required"],
    "32_s3_valid_until_row": W.lines(t32, lambda l: l.startswith("| `issued_at`, `valid_until`")),
    "32_s7_d_row": W.lines(t32, lambda l: l.startswith("| **(d)**")),
    "32_s8_ci_row": W.lines(t32, lambda l: l.startswith("| CI runner image")),
    "32_FC_R4": W.lines(t32, lambda l: l.startswith("| FC-R4")),
    "32_RS_B1": W.lines(t32, lambda l: l.startswith("| RS-B1")),
    "31_R_ADM_7_prime_valid_until_sentence": [s for s in re.split(r"(?<=\.)\s", "\n".join(W.lines(t31, lambda l: l.startswith("| **R-ADM-7′**")))) if "valid_until" in s],
    "any_rule_bounding_manifest_age_for_media_or_images": bool(re.search(r"(?:media|image)[^.\n]*(?:maximum age|valid_until[^.\n]*(?:mandatory|required))|(?:maximum age|compiled maximum)[^.\n]*(?:manifest|first-contact)", t32 + t06 + t31, re.I)),
}
acc = lambda r: r["result"] == "ACCEPTED"
out["verdicts"] = {
    "media_prepared_at_T7_admit_revoked_malicious_B7x_now": acc(out["media_d_prepared_T7_used_now_B7x"]),
    "media_prepared_at_T7_admit_revoked_genuine_B7_now": acc(out["media_d_prepared_T7_used_now_B7_genuine_revoked"]),
    "control_valid_until_refuses": out["control_media_with_valid_until_2026_06_01"]["result"] == "FIRST_CONTACT_MANIFEST_EXPIRED",
    "control_current_media_refuses_B7x": not acc(out["control_current_media_T10_Q1_B7x"]),
    "ci_image_codes_provisioned_at_T7_admit_B7x": acc(out["ci_image_codes_provisioned_at_T7_a_b_B7x"]),
    "valid_until_optional": not out["design"]["schema_requires_valid_until"],
    "no_rule_bounds_stored_value_age": not out["design"]["any_rule_bounding_manifest_age_for_media_or_images"],
}
print(json.dumps(out, indent=1, sort_keys=True, default=str).replace(SCR, "<scratch>").replace(W.REPO, "<export>"))
