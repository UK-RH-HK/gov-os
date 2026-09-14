#!/usr/bin/env python3
"""RV7-B-A01 (AR-0020, reviewer B, held-out) — a revocation issued by the dedicated revocation authority that no later Trust State
lists stays ineffective at first contact and at re-admission for as long as the daily Trust States keep omitting it.

Executed with the architect's revision-7 reference executor UNMODIFIED (`evidence/r7/gov_admit_reference_r7.py`, loaded through
`evidence/r7/w7world.py`; real Ed25519 through OpenSSL; `sha256sum`). Nothing of the executor is patched. The world adds:
  REVOC_R9  revocation of R9 (the newest registered release; found malicious after publication) signed rv1+rv2 (the revocation
            threshold), issued 2026-09-10T00:00:00Z (102 h before NOW) and present in every bundle below;
  T11o      sequence 11, issued 2026-09-14T00:00:00Z, signed ts1+ts2, a descendant of T10 with the content of the genuine T11
            (R9 registered and published; R8 revoked) but with neither R9 in `revocations` nor REVOC_R9 in `revocation_statements`:
            an omission of a revocation no state ever published, not a drop;
  T12o..T21o daily descendants with the same omission.
Controls: T11L (lists the revocation); T11s (lists REVOC_R9 only in `revocation_statements`); T11d (drops the published R7
revocations); re-admission over a store that holds the negative; a custodian with no publication history (a rotated source).
Environment: A01_SCRATCH, PACK (path of release/root-of-trust/4.1.6). Output JSON on stdout.
"""
import json, os, re, sys, tempfile
from datetime import timedelta
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
sys.path.insert(0, os.path.join(PACK, "evidence", "r7"))
import w7world as W  # noqa: E402
GA = W.GA
SCR = tempfile.mkdtemp(prefix="a01-", dir=os.environ["A01_SCRATCH"])
V = GA.Verifier(SCR)
iso = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")
REV_AT = "2026-09-10T00:00:00Z"
REVOC_R9 = W.envelope("revocation+json", {"revokes": [W.R9.D], "reason": "R9 found malicious after publication (held-out A01)", "issued_at": REV_AT}, ["rv1", "rv2"])
T10 = W.T10
REVS, RSTM = W.T11["payload"]["revocations"], W.T11["payload"]["revocation_statements"]


def state(seq, issued, prior, revs, rstm):
    b = W.T11["payload"]
    return W.tss(seq, issued, W.ROOT2, 2, W.TPS2, W.FCA2, prior, b["registrations"], b["published_binaries"], revs, revocation_statements=rstm)


T11o = state(11, "2026-09-14T00:00:00Z", W.PRIOR11, REVS, RSTM)
T11s = state(11, "2026-09-14T00:00:00Z", W.PRIOR11, REVS, RSTM + [REVOC_R9["digest"]])
T11L = state(11, "2026-09-14T00:00:00Z", W.PRIOR11, REVS + [W.R9.D], RSTM + [REVOC_R9["digest"]])
T11d = state(11, "2026-09-14T00:00:00Z", W.PRIOR11, [W.R8.D], [])
chain, prior = [T11o], W.PRIOR11 + [{"sequence": 11, "digest": T11o["digest"]}]
for i in range(1, 11):
    t = state(11 + i, iso(GA.ts("2026-09-14T00:00:00Z") + timedelta(days=i)), list(prior), REVS, RSTM)
    chain.append(t)
    prior = prior + [{"sequence": 11 + i, "digest": t["digest"]}]
BUNDLE = W.FULL + [REVOC_R9]


def publish(tss_env, last):
    st = W.to_stmts(BUNDLE + [tss_env] + ([last] if last else []))
    lp = W.to_stmts([last])[0] if last else None
    return GA.custodian_publish(V, st, W.LINEAGE, W.FCA2["digest"], tss_env["digest"], lp)


def admit(binary, tss_env, now, store=None):
    return W.admit(binary, W.FCA2, tss_env, BUNDLE + [tss_env] + chain, now=now, store=store, verifier=V, workdir=SCR)["result"]


out = {"probe": "RV7-B-A01 revocation omission (AR-0020)",
       "executor_sha256": W.sha256d(open(os.path.join(PACK, "evidence", "r7", "gov_admit_reference_r7.py"), "rb").read()),
       "world": {"NOW": W.NOW, "REVOC_R9_issued_at": REV_AT, "REVOC_R9_signers": "rv1+rv2 (revocation threshold 2 of 3)", "T11o_issued_at": T11o["payload"]["issued_at"],
                 "T11o_lists_R9_revocation": W.R9.D in T11o["payload"]["revocations"], "REVOC_R9_in_every_bundle": True}}
pub = {"custodian_publishes_T11o_after_T10": publish(T11o, T10).get("published"),
       "custodian_publishes_T12o_after_T11o": publish(chain[1], T11o).get("published"),
       "control_custodian_publishes_T11L_after_T10": publish(T11L, T10).get("published"),
       "control_custodian_refuses_T11d_that_drops_published_revocations": publish(T11d, T10),
       "custodian_with_no_publication_history_publishes_T11d (rotated source)": publish(T11d, None).get("published")}
out["publication"] = pub
adm = {"FA_R9_T11o_state_6h_revocation_102h": admit(W.R9.binary, T11o, W.NOW)}
for t in chain:
    now = iso(GA.ts(t["payload"]["issued_at"]) + timedelta(hours=6))
    age = int((GA.ts(now) - GA.ts(REV_AT)).total_seconds() // 3600)
    adm["FA_R9_state_seq_%02d_state_age_6h_revocation_age_%dh" % (t["payload"]["sequence"], age)] = admit(W.R9.binary, t, now)
fl_unheld = W.floors_from(T10, 2, 1, 2, {"root": 2, "policy": 1, "state": 9})
fl_held = dict(fl_unheld, negatives=sorted(fl_unheld["negatives"] + [W.R9.D]))
adm["RA_unheld_R9_T11o (store predates the revocation)"] = admit(W.R9.binary, T11o, W.NOW, store=fl_unheld)
adm["control_RA_held_R9_T11o (store holds the negative)"] = admit(W.R9.binary, T11o, W.NOW, store=fl_held)
adm["control_T11L_lists_the_revocation"] = admit(W.R9.binary, T11L, W.NOW)
adm["control_T11s_lists_REVOC_R9_only_in_revocation_statements"] = admit(W.R9.binary, T11s, W.NOW)
adm["control_R8_listed_revocation_T11o"] = admit(W.R8.binary, T11o, W.NOW)
out["admission"] = adm
fa_chain = [v for k, v in adm.items() if k.startswith("FA_R9_state_seq_")]
out["verdicts"] = {
    "both_custodians_publish_the_omitting_states (R-FCS-2 checks drops only)": pub["custodian_publishes_T11o_after_T10"] is True and pub["custodian_publishes_T12o_after_T11o"] is True,
    "control_custodian_refuses_a_drop": pub["control_custodian_refuses_T11d_that_drops_published_revocations"].get("reason") == "STATE_DROPS_REVOCATIONS",
    "revoked_R9_admitted_with_the_threshold_revocation_in_the_bundle": adm["FA_R9_T11o_state_6h_revocation_102h"] == "ACCEPTED",
    "admitted_on_every_daily_state_for_ten_days (revocation up to 342 h old; CUR-R1 states 24 h)": bool(fa_chain) and all(v == "ACCEPTED" for v in fa_chain),
    "readmission_over_a_store_predating_the_revocation_admits": adm["RA_unheld_R9_T11o (store predates the revocation)"] == "ACCEPTED",
    "control_store_holding_the_negative_refuses": adm["control_RA_held_R9_T11o (store holds the negative)"] == "BINARY_REVOKED_IN_HELD_STATE",
    "control_listing_refuses": adm["control_T11L_lists_the_revocation"].startswith("BINARY_REVOKED") and adm["control_T11s_lists_REVOC_R9_only_in_revocation_statements"].startswith("BINARY_REVOKED"),
}
out["openssl_verifications"] = V.calls
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(out, indent=1, sort_keys=True, default=str)))
