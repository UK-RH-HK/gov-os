#!/usr/bin/env python3
"""AR-0021 held-out RV7-C-A25: a Trust State from offline media (or any stored code pair) older than 24 hours used, on an ADMITTED
machine, for the anchoring event and the currency proof of a C3 transition. Checked against the owner's OT-1 resolution
(OWNER-DESIGN-REQUIREMENTS-0002: "offline media receives no special longer freshness window; stale trust state on otherwise
authentic media cannot become current merely because the medium is trusted ... must NOT complete governed production
admission/install or enter C1-C3 based on stale state").

Executed against the pack's revision-7 reference executor and statement world (`gov_admit_reference_r7.py`, `w7world.py`,
imported unmodified; real Ed25519 through OpenSSL). World: T10 (issued 2026-09-13T12:00Z) publishes release R8, not revoked;
T11 (issued 2026-09-14T00:00Z) revokes R8.
  M1  2026-09-13T13:00Z: an air-gapped workstation is admitted with media prepared within 24 hours (both codes name T10): `accept`.
  M2  2026-10-20: the same T10 codes (the only media the machine has) at RE-ADMISSION: `accept` with the store -> FC-9 applies.
  M3  2026-10-20: the admitted binary anchors with `confirm-state <T10 code> <T10 code>` read from that media (a human confirmation
      made now) and runs C3 within 24 hours of the confirmation: `gov_run(..., "C3", anchor={anchored_at: now-30m, currency_at:
      now-30m})`. `gov_run` receives no issued_at of the state the anchor names (signature printed); R-CUR-1 bounds the EVENT.
  M4  control: the machine that did receive T11 (held negative R8) -> BINARY_REVOKED_SELF / refusal.
Text (quoted by design7/this probe): `24` §3.2 human confirmation "a currency proof for C3 within 24 hours of confirmed_at";
R-CUR-1 "a pin provisioning or human confirmation whose two state codes name n itself is no older than 24 hours"; R-CUR-2
in-gate confirmation "Clock: none"; `31` §3 running executor "a currency proof of at most 24 hours (P1 two-source state codes,
P2 in-gate state codes)"; `32` FC-9 and `06` §3 apply the 24-hour state age to admission only.
Usage: cur7x.py <scratch> <archprobes-dir> <export-root>
"""
import inspect, json, os, re, sys, tempfile
sys.dont_write_bytecode = True
S = os.path.abspath(sys.argv[1])
os.makedirs(S, exist_ok=True)
sys.path.insert(0, os.path.abspath(sys.argv[2]))
import w7world as W  # noqa: E402
GA = W.GA
X = os.path.join(os.path.abspath(sys.argv[3]), "release/root-of-trust/4.1.6")
V = GA.Verifier(tempfile.mkdtemp(prefix="cur7x-", dir=S))
out = {"world": {"T10_issued_at": W.T10["payload"]["issued_at"], "T11_issued_at": W.T11["payload"]["issued_at"], "R8_revoked_in_T11": W.R8.D in W.T11["payload"]["revocations"],
                 "R8_revoked_in_T10": W.R8.D in W.T10["payload"]["revocations"]}}
ADMIT_AT, LATER = "2026-09-13T13:00:00Z", "2026-10-20T06:00:00Z"
m1 = W.admit(W.R8.binary, W.FCA2, W.T10, W.FULL, now=ADMIT_AT, verifier=V, workdir=S)
out["M1_first_admission_media_within_24h"] = m1["result"]
root = tempfile.mkdtemp(prefix="machine-", dir=S)
floors_t10 = W.floors_from(W.T10, 2, 1, 2, {"root": 2, "policy": 1, "state": 9})
if m1["result"].startswith("ACCEPTED"):
    GA.write_admission(GA.make_record(W.R8.D, W.TARGET, "R8", W.LINEAGE, *W.codes(W.FCA2, W.T10), W.ADM_D, ADMIT_AT, "workstation"), floors_t10, root, W.LINEAGE)
m2 = W.admit(W.R8.binary, W.FCA2, W.T10, W.FULL, now=LATER, store=GA.read_floors(root, W.LINEAGE), verifier=V, workdir=S)
out["M2_readmission_same_media_37_days_later"] = m2["result"]
anchor_from_old_media = {"class": "workstation", "anchored_at": "2026-10-20T05:30:00Z", "currency_at": "2026-10-20T05:30:00Z", "names_effective_state": True}
held_t10 = sorted(W.T10["payload"]["revocations"])
out["M3_running_machine"] = {
    "C1_after_confirm_state_with_T10_codes_from_media": GA.gov_run(W.R8.binary, "C1", root, W.LINEAGE, LATER, held_t10, [W.ADM_D], anchor=anchor_from_old_media)["result"],
    "C3_within_24h_of_that_confirmation": GA.gov_run(W.R8.binary, "C3", root, W.LINEAGE, LATER, held_t10, [W.ADM_D], anchor=anchor_from_old_media)["result"],
    "confirm_state_ceremony_itself": GA.gov_run(W.R8.binary, "confirm-state", root, W.LINEAGE, LATER, held_t10, [W.ADM_D], anchor=anchor_from_old_media)["result"],
    "gov_run_signature": str(inspect.signature(GA.gov_run)),
    "anchor_fields_read_by_gov_run": sorted(set(re.findall(r'anchor(?:\.get\(|\[)"([a-z_]+)"', inspect.getsource(GA.gov_run)))),
    "effective_state_age_at_C3_hours": round((GA.ts(LATER) - GA.ts(W.T10["payload"]["issued_at"])).total_seconds() / 3600, 1),
}
out["M4_control_machine_that_holds_T11"] = GA.gov_run(W.R8.binary, "C3", root, W.LINEAGE, LATER, sorted(set(held_t10) | {W.R8.D}), [W.ADM_D], anchor=anchor_from_old_media)["result"]
txt = {n: open(os.path.join(X, n)).read() for n in ("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", "27-TRUST-DECISION-AUTHORISATION.md", "31-INDEPENDENT-ADMISSION.md", "32-FIRST-CONTACT-ROOT.md", "06-BOOTSTRAP.md")}
q = lambda n, pat: [l.strip()[:420] for l in txt[n].splitlines() if re.search(pat, l)]
out["text"] = {"24_human_confirmation_row": q("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*Human confirmation\*\*"),
               "24_in_gate_row": q("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*In-gate state confirmation\*\*"),
               "24_R_CUR": q("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*R-CUR-[12]\*\*"),
               "31_running_executor": q("31-INDEPENDENT-ADMISSION.md", r"^\| `gov trust verify-artifact`"),
               "32_FC9": q("32-FIRST-CONTACT-ROOT.md", r"^\| \*\*FC-9\*\*"), "32_air_gapped_row": q("32-FIRST-CONTACT-ROOT.md", r"^\| Air-gapped machine"),
               "06_air_gapped": q("06-BOOTSTRAP.md", r"air-gapped machine"),
               "issued_at_bound_outside_admission": [l for n in ("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", "27-TRUST-DECISION-AUTHORISATION.md") for l in q(n, r"issued_at") if "future" not in l.lower() and "skew" not in l.lower()]}
out["verdicts"] = {
    "admission_refuses_the_stale_state": out["M2_readmission_same_media_37_days_later"] == "FIRST_CONTACT_STATE_TOO_OLD",
    "running_machine_allows_C3_on_the_same_stale_state": out["M3_running_machine"]["C3_within_24h_of_that_confirmation"] == "ALLOWED",
    "decision_has_no_state_age_input": "issued" not in out["M3_running_machine"]["gov_run_signature"] and "issued_at" not in out["M3_running_machine"]["anchor_fields_read_by_gov_run"],
    "no_issued_at_bound_in_anchoring_or_gate_text": not out["text"]["issued_at_bound_outside_admission"],
    "control_only_receipt_of_T11_refuses": out["M4_control_machine_that_holds_T11"] != "ALLOWED",
}
print(json.dumps({"probe": "cur7x (AR-0021; RV7-C-A25) against the unmodified revision-7 reference executor and world", **out}, indent=1, sort_keys=True).replace(S, "<s>"))
