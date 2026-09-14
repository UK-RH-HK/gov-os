#!/usr/bin/env python3
"""RV7-D-A04 (AR-0022, synthesis reviewer D) — design evidence for held-out attacks A04, A08, A09, A10, A11 and the adjudication of
B and C findings: exact pack, schema, profile and decision-record lines, extracted mechanically from the `git archive` of d07d200.
A pattern that does not match is reported NOT_FOUND (never silently true); an "absence" check reports every line searched.
Usage: RV7-D-A04-design-extractions.py <export-root>   (JSON on stdout)
"""
import json, os, re, sys
import yaml
sys.dont_write_bytecode = True
X = os.path.abspath(sys.argv[1])
PK = os.path.join(X, "release/root-of-trust/4.1.6")


def rd(rel):
    p = os.path.join(X, rel) if rel.startswith(("spec/", "docs/")) else os.path.join(PK, rel)
    return open(p, encoding="utf-8").read()


def lines(rel, pat, flags=0, width=700):
    got = [("%s:%d" % (rel, i + 1), l.strip()[:width]) for i, l in enumerate(rd(rel).splitlines()) if re.search(pat, l, flags)]
    return got or "NOT_FOUND"


def absent(rels, pat, flags=re.I):
    hits = []
    for rel in rels:
        hits += [("%s:%d" % (rel, i + 1), l.strip()[:300]) for i, l in enumerate(rd(rel).splitlines()) if re.search(pat, l, flags)]
    return {"pattern": pat, "files_searched": rels, "hits": hits, "absent": not hits}


MD = sorted(f for f in os.listdir(PK) if f.endswith(".md"))
pin = json.load(open(os.path.join(PK, "schemas/trust-decision-pin.schema.json")))
d8 = yaml.safe_load(open(os.path.join(X, "spec/decisions/D-0008.yaml")))
d7 = yaml.safe_load(open(os.path.join(X, "spec/decisions/D-0007.yaml")))
a2 = yaml.safe_load(open(os.path.join(X, "spec/architecture/ARCH-0002.yaml")))
out = {"probe": "RV7-D-A04 design extractions (AR-0022)"}

# A04: clean CI runner x project_first_use (OP-3 Mode A x OP-11 (b) x HO-0001 §3.2 M2)
out["A04_ci_runner_first_use"] = {
    "27_project_first_use_row": lines("27-TRUST-DECISION-AUTHORISATION.md", r"^\| `project_first_use`"),
    "27_state_codes_C3_kinds": lines("27-TRUST-DECISION-AUTHORISATION.md", r"\*\*`state_codes`\*\*"),
    "27_local_terminal_only_includes": lines("27-TRUST-DECISION-AUTHORISATION.md", r"always includes `init_ack`, `project_first_use`"),
    "27_needs_terminal": lines("27-TRUST-DECISION-AUTHORISATION.md", r"TRUST_GATE_NEEDS_TERMINAL"),
    "pin_schema_gate_kind_enum": pin["properties"]["gate_kind"]["enum"],
    "pin_enum_contains_project_first_use": "project_first_use" in pin["properties"]["gate_kind"]["enum"],
    "24_ci_row_C1_C2": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^  \| valid pin, intact repository"),
    "06_ci_image_paragraph": lines("06-BOOTSTRAP.md", r"^A \*\*CI runner image\*\*"),
    "29_DR25": lines("29-FACT-DERIVATION-AND-SELECTION-AUTHORITY.md", r"^\| DR-25 ", width=420),
    "per_project_record_provisioned_into_ci_images": absent(["24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", "06-BOOTSTRAP.md", "31-INDEPENDENT-ADMISSION.md", "27-TRUST-DECISION-AUTHORISATION.md", "20-ROLLBACK-AND-RECOVERY.md", "35-CERTIFIED-PROFILE.md"],
                                                            r"(per-project record|project_first_use).{0,120}(\bCI\b|runner image|CI image|\brunner\b)|(\bCI\b|runner image|CI image|\brunner\b).{0,120}(per-project record|project_first_use)", 0),
}
# A10: which C3 transitions carry no trust gate (reachable without a controlling terminal)
out["A10_c3_without_gate"] = {
    "17_s7_verify_artifact_row": lines("17-MONOTONIC-TRUST-STATE.md", r"^\| C3 `trust verify-artifact` acceptance"),
    "24_c3_list": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*C3\*\* trust ingress"),
    "27_gate_kinds": [l for l in lines("27-TRUST-DECISION-AUTHORISATION.md", r"^\| `[a-z_]+` ") if isinstance(l, tuple)],
    "24_pin_currency_row": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*Pin\*\*"),
}
# A08: air-gapped admission and C3, the second channel
out["A08_air_gapped_second_channel"] = {
    "06": lines("06-BOOTSTRAP.md", r"air-gapped machine"),
    "32_s8": lines("32-FIRST-CONTACT-ROOT.md", r"^\| Air-gapped machine"),
    "32_FC1": lines("32-FIRST-CONTACT-ROOT.md", r"^\| \*\*FC-1′\*\*"),
    "private_channel_read_independently_of_media": absent(MD, r"(air-gapped|media).{0,200}(authenticated private release channel|private channel|online source|read .{0,40}separately|independently of the media)"),
    "27_in_gate_codes": lines("27-TRUST-DECISION-AUTHORISATION.md", r"the state code currently published by each of the two first-contact sources"),
}
# A09: OT-1 reading of C1–C2 on an anchored chain
out["A09_ot1_c1_c2_reading"] = {
    "24_anchored_row": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| `ANCHORED`, `KNOWN`, within validity"),
    "24_RS1": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| RS-1 \|"),
    "35_s3_running": lines("35-CERTIFIED-PROFILE.md", r"^- \*\*Running machines\.\*\*"),
}
# A05: clock_reset semantics
out["A05_clock_reset"] = {
    "24_s4_5": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"clock_reset"),
    "24_s8_never_backwards": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^- \*\*Never backwards\.\*\*"),
    "17_s13": lines("17-MONOTONIC-TRUST-STATE.md", r"clock_reset"),
    "schema_description": json.load(open(os.path.join(PK, "schemas/trust-policy-statement.schema.json")))["properties"]["bootstrap"]["properties"]["clock_reset"]["description"],
    "one_shot_or_effective_policy_semantics_stated": absent(MD, r"clock_reset.{0,200}(once|one-shot|effective (Trust Policy|TPS)|policy_version|replay)"),
    "reference_r7_implements_clock_reset": "clock_reset" in open(os.path.join(PK, "evidence/r7/gov_admit_reference_r7.py")).read(),
}
# H1 support: establishing party of revocation listing completeness; issuance cadence
out["H1_listing_and_cadence"] = {
    "32_R_FCS_2": lines("32-FIRST-CONTACT-ROOT.md", r"^\| \*\*R-FCS-2\*\*"),
    "25_AP4": lines("25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md", r"^\| AP-4 "),
    "17_s8_delivered_alone": lines("17-MONOTONIC-TRUST-STATE.md", r"A revocation delivered alone is effective immediately"),
    "32_CUR_R1": lines("32-FIRST-CONTACT-ROOT.md", r"^\| \*\*CUR-R1\*\*"),
    "cadence_rule": absent(MD, r"(issu|publish)\w* .{0,60}(at least daily|every 24 hours|within 24 hours of the previous|cadence)"),
    "listing_completeness_rule": absent(MD, r"(list|include|reference)\w* every (verified )?revocation|revocation.{0,40}(complete|completeness)"),
}
# H2 support: the C3 proofs
out["H2_currency_proofs"] = {
    "24_R_CUR": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| \*\*R-CUR-[12]\*\*"),
    "24_RS1b": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"^\| RS-1b"),
    "24_s6_replayed_codes": lines("24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", r"Replayed first-contact or anchoring codes"),
    "28_A_R7_08": lines("28-CLASS-REMAINDER-ANALYSIS.md", r"^\| A-R7-08"),
    "issued_at_bound_on_running_c3": absent(["24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", "27-TRUST-DECISION-AUTHORISATION.md", "25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md", "31-INDEPENDENT-ADMISSION.md"],
                                            r"(C3|currency proof|R-CUR).{0,160}issued_at|issued_at.{0,160}(C3|currency proof)"),
}
# A02 support: reproduction coverage rules versus the instruments' assumption
out["A02_reproduction_coverage"] = {
    "25_AP6": lines("25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md", r"^\| AP-6 "),
    "30_R_REP_4": lines("30-RELEASE-REGISTRATION-AND-REPRODUCTION.md", r"^\| \*\*R-REP-4′\*\*"),
    "30_R_REG_3_f": lines("30-RELEASE-REGISTRATION-AND-REPRODUCTION.md", r"\*\*\(f\)\*\* the custodian's own reproduction", width=300),
    "21_s4_combinations": lines("21-OWNER-OPTIONS.md", r"^\*\*Combinations \(RV6-L12\)\.\*\*"),
    "ENV7_acceptance_docstring": lines("evidence/r7/ENV7-environment-authority.py", r"Every reproducer builds in every"),
    "CS7_claims_every_combo": lines("evidence/r7/CS7-derivation-calculator.py", r"for c, t in combos\(\)"),
    "coverage_of_every_combination_required": absent(["25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md", "30-RELEASE-REGISTRATION-AND-REPRODUCTION.md", "33-BUILD-ENVIRONMENT.md", "35-CERTIFIED-PROFILE.md"],
                                                     r"every (registered )?(environment|supplier class).{0,40}(and|x|×).{0,40}(toolchain|lineage)|each combination|every combination"),
}
# M1 support: designation
out["M1_designation"] = {"32_R_FCD_2": lines("32-FIRST-CONTACT-ROOT.md", r"^\| \*\*R-FCD-2\*\*"), "06_step1": lines("06-BOOTSTRAP.md", r"Operators receive the source identities")}
# OT-2 label and criterion
out["OT2"] = {"35_targets": lines("35-CERTIFIED-PROFILE.md", r"NOT CERTIFIED"), "35_CC3": lines("35-CERTIFIED-PROFILE.md", r"^\| \*\*CC-3\*\*"),
              "33_R_BENV_6": lines("33-BUILD-ENVIRONMENT.md", r"^\| \*\*R-BENV-6″\*\*"), "ENV7_honesty_note": lines("evidence/r7/ENV7-environment-authority.py", r"diverse double-compilation over two real bootstrap chains is not executed")}
# excluded modes still written as normative rows in 17 (non-production text)
out["17_excluded_mode_rows"] = {"banner": lines("17-MONOTONIC-TRUST-STATE.md", r"that text is non-production history"),
                                "rows": [l for l in lines("17-MONOTONIC-TRUST-STATE.md", r"freshness-witness|WITNESSED|mode B|OP-7 \((b|c|d)\)") if isinstance(l, tuple)]}
out["decision_records"] = {"D-0008": {k: d8.get(k) for k in ("status", "proposal_state", "approval_state", "in_effect", "human_approved", "revision", "chosen_option")},
                           "D-0007": {k: d7.get(k) for k in ("status", "superseded_by")},
                           "ARCH-0002": {k: a2.get(k, "<absent>") for k in ("status", "proposal_state", "in_effect", "human_approved", "revision")},
                           "DECISIONS_rows": lines("docs/DECISIONS.md", r"D-0007\]|D-0008\]|ARCH-0002\]", width=260)}
print(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False))
