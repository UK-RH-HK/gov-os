#!/usr/bin/env python3
"""RV7-B-A02 (AR-0020, reviewer B, held-out) — the running-mode currency proof bounds the age of the anchoring EVENT, not the age of
the Trust State it names: a stored or replayed state code typed (or pinned) now yields a C3 currency proof for a state of any age.

Part E (executed, reference executor UNMODIFIED): a machine holds an admission record for R7 (admitted 2026-08-01, within 90 days),
a retained workstation anchor at T5 (2026-08-01), and never received T9 (which revokes R7). The operator types the T7 state code
stored from 2026-05 (both "sources" read from a runbook); `gov_run` is asked C3 with currency_at = NOW naming the effective state.
Compare: the SAME code pair presented to `gov-admit` (bootstrap mode) is refused by the compiled 24-hour state age (FC-9).
Part C (computed): the architect's BA11r7 re-expression (copied with attribution, AR-0019; itself after RV6-B-A11, AR-0016) hard-codes
that a C3 currency proof names `sources_latest` (what the sources publish now). The rules R-CUR-1/R-CUR-2 cannot check that: they check
that the typed codes are identical and name the effective state, and the event age. This part re-evaluates BA11r7's rows with the
typed codes naming the machine's effective state (stored codes), everything else unchanged, and counts the rows where C3 is allowed
on a state below t9 (R7 revoked at t9).
Environment: A02_SCRATCH, PACK. Output: JSON on stdout.
"""
import copy, importlib.util, io, json, os, re, sys, tempfile, contextlib
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
R7DIR = os.path.join(PACK, "evidence", "r7")
sys.path.insert(0, R7DIR)
import w7world as W  # noqa: E402
GA = W.GA
SCR = tempfile.mkdtemp(prefix="a02-", dir=os.environ["A02_SCRATCH"])
V = GA.Verifier(SCR)
out = {"probe": "RV7-B-A02 C3 currency names a state of unbounded age (AR-0020)"}

# ---------------------------------------------------------------- Part E
rd = os.path.join(SCR, "machine")
rec7 = GA.make_record(W.R7.D, W.TARGET, "R7", W.LINEAGE, *W.codes(W.FCA1, W.T7), W.ADM_D, "2026-08-01T00:00:00Z", "workstation")
GA.write_admission(rec7, W.floors_from(W.T7, 1, 1, 1, {"root": 1, "policy": 1, "state": 5}), rd, W.LINEAGE)
anchor_stored_codes = {"class": "workstation", "anchored_at": "2026-08-01T00:00:00Z", "currency_at": W.NOW, "names_effective_state": True}
E = {
    "T7_issued_at": W.T7["payload"]["issued_at"], "NOW": W.NOW,
    "gov_run_C3_with_stored_T7_codes_typed_now (effective state T7, T9 withheld)": GA.gov_run(W.R7.binary, "C3", rd, W.LINEAGE, W.NOW, [], [W.ADM_D], anchor=anchor_stored_codes)["result"],
    "gov_run_signature_has_no_state_issued_at_input": "issued" not in " ".join(GA.gov_run.__code__.co_varnames),
    "control_gov_run_C3_currency_25h_old": GA.gov_run(W.R7.binary, "C3", rd, W.LINEAGE, W.NOW, [], [W.ADM_D], anchor=dict(anchor_stored_codes, currency_at="2026-09-13T05:00:00Z"))["result"],
    "control_gov_run_C3_after_T9_held (negative held)": GA.gov_run(W.R7.binary, "C3", rd, W.LINEAGE, W.NOW, [W.R7.D], [W.ADM_D], anchor=anchor_stored_codes)["result"],
    "same_codes_at_gov_admit_bootstrap (FC-9)": W.admit(W.R7.binary, W.FCA1, W.T7, [W.ROOT1, W.TPS1, W.FCA1, W.T5, W.T7] + W.R7.all(), verifier=V, workdir=SCR)["result"],
}
# CI runner: image admitted 6 days ago (record valid 7 days); the provisioning automation re-stamps the pin's provisioned_at daily
# with the state code it copied at image build (TA-9 operator); R-CUR-1 bounds provisioned_at, not the named state's issued_at.
rc = os.path.join(SCR, "ci")
rec9 = GA.make_record(W.R9.D, W.TARGET, "R9", W.LINEAGE, *W.codes(W.FCA2, W.T10), W.ADM_D, "2026-09-08T06:00:00Z", "ci-image")
GA.write_admission(rec9, W.floors_from(W.T10, 2, 1, 2, {"root": 2, "policy": 1, "state": 10}), rc, W.LINEAGE)
E["CI_gov_run_C3_pin_restamped_today_naming_the_state_of_image_build_6_days_ago"] = GA.gov_run(W.R9.binary, "C3", rc, W.LINEAGE, "2026-09-14T06:00:00Z", [], [W.ADM_D],
    anchor={"class": "ci-image", "anchored_at": "2026-09-14T05:00:00Z", "currency_at": "2026-09-14T05:00:00Z", "names_effective_state": True})["result"]
E["CI_control_pin_as_provisioned_6_days_ago"] = GA.gov_run(W.R9.binary, "C3", rc, W.LINEAGE, "2026-09-14T06:00:00Z", [], [W.ADM_D],
    anchor={"class": "ci-image", "anchored_at": "2026-09-08T06:00:00Z", "names_effective_state": True})["result"]
out["E_executed"] = E

# ---------------------------------------------------------------- Part C (BA11r7 re-evaluated; source copied from evidence/r7/BA11r7-machine-classes.py)
src = open(os.path.join(R7DIR, "BA11r7-machine-classes.py")).read()
marker = 'sources_latest = "t12x" if adv == "TS-thief" else "t11"'
assert marker in src
variants = {}
for name, repl in (("as_committed", marker), ("stored_codes_name_the_effective_state", 'sources_latest = (eff["d"] if eff else None) if STORED else ("t12x" if adv == "TS-thief" else "t11")')):
    code = src.replace(marker, repl).replace('HERE = os.path.dirname(os.path.abspath(__file__))', 'HERE = %r' % R7DIR)
    g = {"__name__": "ba11_variant", "__file__": os.path.join(R7DIR, "BA11r7-machine-classes.py"), "STORED": name != "as_committed"}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "BA11r7-variant", "exec"), g)
    variants[name] = json.loads(buf.getvalue())
C = {}
for name, res in variants.items():
    rows = res["rows"]
    C[name] = {"verdicts": res["verdicts"],
               "rows_C3_on_state_below_t9": sorted(k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") in ("t1", "t5")),
               "rows_C3_on_state_below_t9_and_anchor_valid": sorted(k for k, v in rows.items() if v.get("C3_with_currency_naming_effective") and v.get("effective_tss") in ("t1", "t5") and not v.get("cp1_anchor_expired_C0"))}
out["C_computed_BA11r7"] = C
out["verdicts"] = {
    "C3_allowed_with_stored_codes_naming_a_4_month_old_state": E["gov_run_C3_with_stored_T7_codes_typed_now (effective state T7, T9 withheld)"] == "ALLOWED",
    "same_codes_refused_at_admission": E["same_codes_at_gov_admit_bootstrap (FC-9)"] == "FIRST_CONTACT_STATE_TOO_OLD",
    "committed_BA11r7_shows_no_C3_below_t9": not C["as_committed"]["rows_C3_on_state_below_t9"],
    "stored_code_variant_shows_C3_below_t9": bool(C["stored_codes_name_the_effective_state"]["rows_C3_on_state_below_t9"]),
}
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(out, indent=1, sort_keys=True, default=str)))
