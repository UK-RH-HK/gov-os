#!/usr/bin/env python3
"""RV7-D-A01 (AR-0022, synthesis reviewer D, held-out) — is RV7-B-H1 a revocation-only defect, or a class over every
restrictive fact whose issuing authority is not the trust-state authority?

Executed with the architect's revision-7 reference executor UNMODIFIED (`evidence/r7/gov_admit_reference_r7.py` through
`evidence/r7/w7world.py`; real Ed25519 through OpenSSL). Two restrictive facts B did not test:
  (1) ADMITTER revocation: the dedicated revocation authority (rv1+rv2) revokes the listed `gov-admit` digest (a vulnerable
      admitter). Daily Trust States signed by two trust-state keys omit it. FC-8′ "the admitter is not revoked in the selected
      state" reads only the selected state's listing.
  (2) OP-11 (b) SECURITY MINIMUM: the 2-of-3 registration quorum registers R10 (sequence 10, security_relevant_change=true). Daily
      Trust States omit the new registration (an omission, not a drop), so AP-SEC never raises the minimum above 9 and the
      superseded R9 stays admissible at first contact.
For each: both source custodians' `custodian_publish` (R-FCS-2 drop check), first admission on the omitting state and on ten
daily descendants, and a control where the state lists the fact.
Environment: A01_SCRATCH, PACK. Output: JSON on stdout.
"""
import json, os, re, sys, tempfile
from datetime import timedelta
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
sys.path.insert(0, os.path.join(PACK, "evidence", "r7"))
import w7world as W  # noqa: E402
GA = W.GA
SCR = tempfile.mkdtemp(prefix="d-a01-", dir=os.environ["A01_SCRATCH"])
V = GA.Verifier(SCR)
iso = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")
B11 = W.T11["payload"]

# (1) admitter revocation by the revocation authority, issued 2026-09-10
REVOC_ADM = W.envelope("revocation+json", {"revokes": [W.ADM_D], "reason": "gov-admit defect (held-out D-A01)", "issued_at": "2026-09-10T00:00:00Z"}, ["rv1", "rv2"])
# (2) R10: security-relevant registration by the registration quorum under root v2 (g3, g4); its binary is irrelevant here
R10 = W.Release("R10", 10, 2, 2, 11, ("g3", "g4"), ("p3", "p4"), security_relevant_change=True)


def state(seq, issued, prior, regs, pubs, revs, rstm):
    return W.tss(seq, issued, W.ROOT2, 2, W.TPS2, W.FCA2, prior, regs, pubs, revs, revocation_statements=rstm)


def chain_of(first_kwargs, n=10):
    """T11 descendant with the given content and n daily descendants carrying the same content."""
    t = state(11, "2026-09-14T00:00:00Z", W.PRIOR11, **first_kwargs)
    out, prior = [t], W.PRIOR11 + [{"sequence": 11, "digest": t["digest"]}]
    for i in range(1, n + 1):
        d = state(11 + i, iso(GA.ts("2026-09-14T00:00:00Z") + timedelta(days=i)), list(prior), **first_kwargs)
        out.append(d)
        prior = prior + [{"sequence": 11 + i, "digest": d["digest"]}]
    return out


BASE_CONTENT = {"regs": B11["registrations"], "pubs": B11["published_binaries"], "revs": B11["revocations"], "rstm": B11["revocation_statements"]}
omit = chain_of(BASE_CONTENT)                                                        # omits REVOC_ADM and R10
list_adm = state(11, "2026-09-14T00:00:00Z", W.PRIOR11, B11["registrations"], B11["published_binaries"], B11["revocations"] + [W.ADM_D], B11["revocation_statements"] + [REVOC_ADM["digest"]])
list_r10 = state(11, "2026-09-14T00:00:00Z", W.PRIOR11, B11["registrations"] + [R10.reg["digest"]], B11["published_binaries"], B11["revocations"], B11["revocation_statements"])
BUNDLE = W.FULL + [REVOC_ADM] + R10.all()


def publish(t, last):
    st = W.to_stmts(BUNDLE + [t] + ([last] if last else []))
    return GA.custodian_publish(V, st, W.LINEAGE, W.FCA2["digest"], t["digest"], W.to_stmts([last])[0] if last else None)


def admit(binary, t, now, chain=()):
    return W.admit(binary, W.FCA2, t, BUNDLE + [t] + list(chain), now=now, verifier=V, workdir=SCR)


out = {"probe": "RV7-D-A01 omission class extension (AR-0022)",
       "executor_sha256": W.sha256d(open(os.path.join(PACK, "evidence", "r7", "gov_admit_reference_r7.py"), "rb").read()),
       "world": {"NOW": W.NOW, "REVOC_ADM_signers": "rv1+rv2", "R10_security_relevant_change": True, "R10_sequence": 10, "R9_sequence": 9,
                 "TPS2_min_release_sequence": W.TPS2["payload"]["eligibility"]["min_release_sequence"]}}
pub = {"custodian_publishes_T11_omitting_admitter_revocation_and_R10_after_T10": publish(omit[0], W.T10).get("published"),
       "custodian_publishes_T12_after_T11": publish(omit[1], omit[0]).get("published"),
       "control_custodian_publishes_state_listing_the_admitter_revocation": publish(list_adm, W.T10).get("published"),
       "control_custodian_publishes_state_referencing_R10": publish(list_r10, W.T10).get("published")}
out["publication"] = pub
adm = {}
for t in omit:
    now = iso(GA.ts(t["payload"]["issued_at"]) + timedelta(hours=6))
    adm["seq_%02d_admitter_revocation_age_%dh" % (t["payload"]["sequence"], (GA.ts(now) - GA.ts("2026-09-10T00:00:00Z")).total_seconds() // 3600)] = admit(W.R9.binary, t, now, omit)["result"]
adm["control_state_lists_admitter_revocation"] = admit(W.R9.binary, list_adm, W.NOW)["result"]
out["admitter_revocation_omitted"] = adm
mn = {}
for t in omit:
    now = iso(GA.ts(t["payload"]["issued_at"]) + timedelta(hours=6))
    r = admit(W.R9.binary, t, now, omit)
    mn["seq_%02d_R9_admitted_while_R10_unreferenced" % t["payload"]["sequence"]] = r["result"]
r = admit(W.R9.binary, list_r10, W.NOW)
mn["control_state_references_R10"] = {"result": r["result"], "minimum": r.get("minimum"), "release_sequence": r.get("release_sequence")}
out["security_minimum_registration_omitted"] = mn
daily = lambda d, prefix: [v for k, v in d.items() if k.startswith(prefix)]
out["verdicts"] = {
    "custodians_publish_states_omitting_both_facts (R-FCS-2 (d) checks drops only)": pub["custodian_publishes_T11_omitting_admitter_revocation_and_R10_after_T10"] is True and pub["custodian_publishes_T12_after_T11"] is True,
    "revoked_admitter_evaluates_first_contact_on_every_daily_state": all(v == "ACCEPTED" for v in daily(adm, "seq_")),
    "control_listed_admitter_revocation_refuses": adm["control_state_lists_admitter_revocation"] == "ADMITTER_REVOKED",
    "superseded_release_admitted_on_every_daily_state_while_the_security_relevant_registration_is_unreferenced": all(v == "ACCEPTED" for v in daily(mn, "seq_")),
    "control_referenced_registration_raises_the_minimum": mn["control_state_references_R10"]["result"] == "RELEASE_BELOW_SECURITY_MINIMUM",
}
out["openssl_verifications"] = V.calls
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(out, indent=1, sort_keys=True, default=str)))
