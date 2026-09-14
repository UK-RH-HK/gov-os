#!/usr/bin/env python3
"""RV6-D-A09 — does the decision register see every value that enters a trust decision? (review r6 synthesis D, AR-0018)
Computed (register YAML, schemas, pack text) — an independent method for the class behind reviewer B's RV6-B-M3.

`register_check.py` C2 proves completeness over rule ids of the scoped rule tables. FD-1 §2 (1) requires that every INPUT of
a decision has one role. Inputs are values: fields of statements, manifests and local records, and procedure inputs.
This attack enumerates every leaf field of the revision-6 schemas that feed trust decisions and asks, for each:
  (i)  is the field named anywhere in the register (selectors, restrictors, carriers, bounds)?
  (ii) if named in a selector entry, does that entry name who ESTABLISHES the value (not only who carries or signs it)?
It also asks whether the register names the procedure inputs of first contact that no schema holds: which sources are
consulted (designation), the procedure text, and the party that composes the first-contact manifest.
The heuristics are lexical and are reported with their patterns; the result is a lower bound on unregistered inputs.
Environment: REVIEW_REPO. Output: JSON on stdout.
"""
import json, os, re, sys

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
REG = yaml.safe_load(open(os.path.join(PK, "decision-register", "DECISION_REGISTER.yaml")))
SCHEMAS = ["first-contact-manifest", "environment-manifest", "environment-reproduction", "input-manifest", "release-registration", "registration-revocation",
           "binary-reproduction", "verification-attestation", "admission-record", "trust-policy-statement", "trust-base-manifest", "trust-state-statement",
           "freshness-witness", "trust-state-pin", "trust-decision-pin", "trust-gate-confirmation"]
SKIP = {"schema", "_type", "$schema", "x-schema-version"}


def leaves(node, pre=""):
    if not isinstance(node, dict):
        return
    props = node.get("properties")
    if isinstance(props, dict):
        for k, v in props.items():
            p = pre + "." + k if pre else k
            sub = False
            if isinstance(v, dict) and (v.get("properties") or (isinstance(v.get("items"), dict) and v["items"].get("properties")) or (isinstance(v.get("additionalProperties"), dict) and v["additionalProperties"].get("properties"))):
                sub = True
                yield from leaves(v, p)
                if isinstance(v.get("items"), dict):
                    yield from leaves(v["items"], p + "[]")
                if isinstance(v.get("additionalProperties"), dict):
                    yield from leaves(v["additionalProperties"], p + "{}")
            if not sub and k not in SKIP:
                yield p
    for key in ("items",):
        if isinstance(node.get(key), dict) and not pre:
            yield from leaves(node[key], pre)


def text_of(o):
    return json.dumps(o, ensure_ascii=False).lower()


reg_all = text_of(REG["decisions"])
sel_entries = [(d["id"], s) for d in REG["decisions"] for s in (d.get("selectors") or [])]
res = {"schemas": {}, "totals": {}}
tot = {"fields": 0, "not_named": 0, "named_only_outside_selectors": 0, "named_in_selector_without_establishing_party": 0}
# A selector entry "names an establishing party" when its authority text says who derives, reproduces, recomputes, types or
# measures the value itself. "registered and reproduced" about a DIFFERENT object (the admitter binary) is excluded by requiring
# the verb to govern the input; the heuristic is lexical and the focus fields below are also judged by hand in the report.
EST = re.compile(r"first-hand|establish|deriv|recomput|typed|read now|measured|computed|each custodian", re.I)
for name in SCHEMAS:
    sc = json.load(open(os.path.join(PK, "schemas", name + ".schema.json")))
    fields = sorted(set(leaves(sc)))
    rows = {}
    for f in fields:
        last = re.sub(r"[\[\]{}]", "", f.split(".")[-1]).lower()
        pat = re.compile(r"(?<![a-z0-9_])" + re.escape(last) + r"(?![a-z0-9_])")
        named = bool(pat.search(reg_all))
        in_sel = [(did, s) for did, s in sel_entries if pat.search(text_of(s.get("input", "")))]
        est = [did for did, s in in_sel if EST.search(str(s.get("authority", "")))]
        state = "not_named" if not named else ("selector_with_establishing_party" if est else ("selector_without_establishing_party" if in_sel else "named_outside_selectors"))
        rows[f] = {"state": state, "selector_decisions": sorted({d for d, _ in in_sel})}
        tot["fields"] += 1
        tot["not_named"] += state == "not_named"
        tot["named_only_outside_selectors"] += state == "named_outside_selectors"
        tot["named_in_selector_without_establishing_party"] += state == "selector_without_establishing_party"
    res["schemas"][name] = rows
res["totals"] = tot
focus = {
    "first-contact-manifest": ["valid_until", "issued_at", "admitters", "lineage_id"],
    "environment-manifest": ["assembly.recipe_digest", "assembly.tool", "components[].upstream_checksum_reference", "supplier_class"],
    "admission-record": ["valid_until", "first_contact_code", "location_protected", "admitter_digest"],
    "input-manifest": [],
    "release-registration": ["admitter"],
}
res["focus_fields"] = {s: {f: res["schemas"][s].get(f) or res["schemas"][s].get(f.replace("[]", "")) or "field path not found" for f in fs} for s, fs in focus.items()}
fc_decisions = [d for d in REG["decisions"] if d["id"] in ("DR-02", "DR-03", "DR-04", "DR-05", "DR-06")]
env_decisions = [d for d in REG["decisions"] if d["id"] == "DR-13"]
res["procedure_inputs"] = {
    "register_names_source_designation": bool(re.search(r"designat|which sources|source list", text_of(fc_decisions))),
    "register_names_procedure_text_or_printer": bool(re.search(r"fc-procedure|procedure text|prints? the", text_of(fc_decisions))),
    "register_names_manifest_composer_or_publisher": bool(re.search(r"compos|publisher|signer outputs|external signer", text_of(fc_decisions))),
    "register_names_package_submitter": bool(re.search(r"submit", reg_all)),
    "register_names_environment_manifest_author": bool(re.search(r"\bauthor(?:ed|s)?\b|\bpropos|\bdraft", text_of(env_decisions))),
    "DR-13_selector_authority": [s.get("authority") for s in env_decisions[0].get("selectors", [])] if env_decisions else None,
    "DR-06_selector_authority": [s.get("authority") for d in fc_decisions if d["id"] == "DR-06" for s in d.get("selectors", [])],
}
rc = open(os.path.join(PK, "decision-register", "register_check.py")).read()
res["register_check_scope"] = {"C2_docstring": [l.strip() for l in rc.splitlines() if l.strip().startswith("C2")][:2], "reads_schemas": "schemas" in rc}
res["verdicts"] = {
    "fields_not_named_in_register": tot["not_named"],
    "fields_named_in_a_selector_without_an_establishing_party": tot["named_in_selector_without_establishing_party"],
    "FCM_valid_until_not_named": res["focus_fields"]["first-contact-manifest"]["valid_until"]["state"] == "not_named" if isinstance(res["focus_fields"]["first-contact-manifest"]["valid_until"], dict) else None,
    "register_has_no_designation_printer_composer_submitter_or_manifest_author": not any(res["procedure_inputs"][k] for k in ("register_names_source_designation", "register_names_procedure_text_or_printer", "register_names_manifest_composer_or_publisher", "register_names_package_submitter", "register_names_environment_manifest_author")),
    "register_check_does_not_read_schemas": not res["register_check_scope"]["reads_schemas"],
}
print(json.dumps(res, indent=1, sort_keys=True))
