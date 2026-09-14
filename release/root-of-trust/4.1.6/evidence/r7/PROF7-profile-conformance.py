#!/usr/bin/env python3
"""PROF7 — profile conformance of the revision-7 certified profile CP-1 (AR-0019). Executed + computed + text. Scratch only.

For every exclusion EX-01…EX-24 of `profile/CP-1.yaml` this check runs one or more checks of each mechanism kind the profile declares for
it, and reports `per_exclusion[EX-nn]` (the `PROF7:EX-nn` test ids the profile names):
  schema      JSON-pointer assertions over the certified schema set (`schemas/`; withdrawn schemas only in `schemas/withdrawn-non-production/`);
  compiled    constants, purpose table, statement types, provenance attributes and command set of the certified reference executor
              (`gov_admit_reference_r7.py`), read from the module and its syntax tree (identifiers, not comments);
  refusal     the executor's typed refusal when the excluded input is presented (expected code prefix per vector);
  calculator  the derivation calculator (`CS7`): the production configuration is CP-1 only, no atom or victim of an excluded mode, every
              revision-7 rule on, the revision-6 control labelled non-production;
  register    the decision register row with role `excluded` naming the exclusion, its mechanism and tests (every exclusion); for EX-22
              also the D-0008 options.
An exclusion holds when every declared mechanism kind has at least one check and every check holds.
Also reported: P1 the profile file (every owner selection cited; every exclusion has mechanisms and tests) and P7 the normative text
(every line of a normative pack file naming an excluded answer marks it excluded, non-production, history or refused).
Vector constructions follow `FA7-first-contact-authority.py` S4 (re-typed). Environment: PROF7_SCRATCH. Output: JSON on stdout.
"""
import ast, copy, importlib.util, json, os, re, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(PACK, "..", "..", ".."))
sys.path.insert(0, HERE)
import w7world as W  # noqa: E402

GA = W.GA
SCR = tempfile.mkdtemp(prefix="prof7-", dir=os.environ["PROF7_SCRATCH"])
V = GA.Verifier(SCR)
PROFILE = yaml.safe_load(open(os.path.join(PACK, "profile", "CP-1.yaml")))
EXIDS = [e["id"] for e in PROFILE["exclusions"]]
DECLARED = {e["id"]: sorted(e["mechanisms"]) for e in PROFILE["exclusions"]}
SD = os.path.join(PACK, "schemas")
CHECKS = []  # {exclusion, kind, check, holds, detail}


def chk(exs, kind, name, holds, detail=None):
    for ex in exs.split(","):
        CHECKS.append({"exclusion": ex.strip(), "kind": kind, "check": name, "holds": bool(holds), "detail": detail})


# ================================================================================================ P1 profile file
owner_ids = ["OP-1", "OP-2 (b)", "OP-3 Mode A", "OP-4", "OP-5", "OP-6 (a)", "OP-7 (a)", "OP-8", "OP-9 (b) + (d)", "OP-10 (b)", "OP-11 (b)", "OP-12 (a)", "OP-13 (b)", "OP-14 (b)",
             "OP-15 (a)", "OP-16 (b)", "First-contact composer/signer", "Build-environment manifest author/signer"]
owners_present = json.dumps(PROFILE["parameters"])
P1 = {"parameters_cite": {o: (o in owners_present) for o in owner_ids}, "exclusions": EXIDS,
      "every_exclusion_has_mechanism_and_test": all(e.get("mechanisms") and e.get("test") and ("PROF7:" + e["id"]) in e["test"] for e in PROFILE["exclusions"]),
      "certified_targets_criteria": sorted(PROFILE["certified_targets"]["criteria"]), "initial_targets": {t["target"]: t["status"] for t in PROFILE["certified_targets"]["initial_target_set"]}}
P1["holds"] = all(P1["parameters_cite"].values()) and P1["every_exclusion_has_mechanism_and_test"] and P1["certified_targets_criteria"] == ["CC-%d" % i for i in range(1, 10)] \
    and all(s != "CERTIFIED" for s in P1["initial_targets"].values())


# ================================================================================================ schema
def sch(name):
    return json.load(open(os.path.join(SD, name)))


def ptr(doc, path):
    cur = doc
    for part in [p for p in path.split("/") if p]:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return KeyError
    return cur


tps, root, fca, reg, adm, lock, man, att, dpin, inp = (sch("trust-policy-statement.schema.json"), sch("trust-root.schema.json"), sch("first-contact-authority.schema.json"),
                                                        sch("release-registration.schema.json"), sch("admission-record.schema.json"), sch("environment-lock.schema.json"),
                                                        sch("environment-manifest.schema.json"), sch("verification-attestation.schema.json"), sch("trust-decision-pin.schema.json"),
                                                        sch("input-manifest.schema.json"))
BOOT = "properties/bootstrap/properties/"
absent = lambda d_, p: ptr(d_, p) is KeyError
withdrawn = lambda n: not os.path.exists(os.path.join(SD, n)) and os.path.exists(os.path.join(SD, "withdrawn-non-production", n))
purpose_shape = lambda p: ptr(root, "properties/purposes/properties/%s/allOf/1/properties" % p)
chk("EX-01", "schema", "trust-root purposes: no freshness-witness", absent(root, "properties/purposes/properties/freshness-witness"))
chk("EX-01", "schema", "trust-policy bootstrap: no witness_max_validity_hours / freshness_witness_threshold", absent(tps, BOOT + "witness_max_validity_hours") and absent(tps, BOOT + "freshness_witness_threshold"))
chk("EX-01", "schema", "freshness-witness schema withdrawn", withdrawn("freshness-witness.schema.json"))
chk("EX-02,EX-03", "schema", "admission record admitter_kind const compiled-gov-admit", ptr(adm, "properties/admitter_kind") == {"const": "compiled-gov-admit"})
chk("EX-03", "schema", "authority admitters map to a digest", "pattern" in json.dumps(ptr(fca, "properties/admitters")))
chk("EX-04", "schema", "trust-policy bootstrap: no channel_quorum", absent(tps, BOOT + "channel_quorum"))
chk("EX-04", "schema", "authority names exactly two sources of the two OP-13 (b) kinds", ptr(fca, "properties/sources/minItems") == 2 and ptr(fca, "properties/sources/maxItems") == 2
    and sorted(ptr(fca, "properties/sources/items/properties/kind/enum") or []) == ["authenticated-private-release-channel", "immutable-release-mirror"])
chk("EX-06", "schema", "gating mode const always_gate", ptr(tps, "properties/gating/properties/mode/const") == "always_gate")
chk("EX-07", "schema", "eligibility: no eligible_until", absent(tps, "properties/eligibility/properties/eligible_until"))
chk("EX-07", "schema", "bootstrap: no op7_mode", absent(tps, BOOT + "op7_mode"))
chk("EX-09", "schema", "release-registration exactly 3 keys, threshold 2", purpose_shape("release-registration") == {"key_ids": {"minItems": 3, "maxItems": 3}, "threshold": {"const": 2}})
chk("EX-11", "schema", "bootstrap: no op6_mode", absent(tps, BOOT + "op6_mode"))
chk("EX-12", "schema", "bootstrap: no max_anchor_age_days; admission ceilings bounded by 90 / 7 / 24", absent(tps, BOOT + "max_anchor_age_days")
    and ptr(tps, BOOT + "admission_ceilings/properties/workstation_anchor_days/maximum") == 90 and ptr(tps, BOOT + "admission_ceilings/properties/ci_anchor_days/maximum") == 7
    and ptr(tps, BOOT + "admission_ceilings/properties/production_currency_hours/maximum") == 24)
chk("EX-13", "schema", "min_verification_records const 2", ptr(tps, "properties/registration/properties/min_verification_records") == {"const": 2})
chk("EX-14", "schema", "reproducer quorum const 2", ptr(root, "properties/quorums/properties/reproducer") == {"const": 2})
chk("EX-14", "schema", "registration requires binary_digests", "binary_digests" in reg["required"])
chk("EX-19", "schema", "admission record valid_until is a string (never null)", ptr(adm, "properties/valid_until/type") == "string")
chk("EX-20", "schema", "bootstrap: no revoked_self_scope", absent(tps, BOOT + "revoked_self_scope"))
chk("EX-21", "schema", "registration: no environment_diversity switch; environments >= 2", absent(tps, "properties/registration/properties/environment_diversity") and ptr(reg, "properties/environments/minItems") == 2)
chk("EX-23", "schema", "first-contact manifest schema withdrawn", withdrawn("first-contact-manifest.schema.json"))
EMA = {"lock_forbids_inline_content_and_keys": ptr(lock, "properties/environments/items/properties/components/items/additionalProperties") is False,
       "manifest_assembly_function_const": ptr(man, "properties/assembly_function") == {"const": "gov-envassemble/1"},
       "manifest_has_no_recipe_or_author_reference": "recipe_digest" not in json.dumps(man) and "upstream_checksum_reference" not in json.dumps(man),
       "attestation_names_environments (RV6-L3)": "environment_ids" in att["required"], "input_manifest_two_toolchains": ptr(inp, "properties/toolchains/minItems") == 2,
       "decision_pins_never_approve_update_install_rollback_first_use_recovery (OP-3)": not set(ptr(dpin, "properties/gate_kind/enum") or []) & {"framework_update", "downgrade", "rollback", "project_first_use", "recovery_exchange", "init_ack"}}

# ================================================================================================ compiled
src = open(os.path.join(HERE, "gov_admit_reference_r7.py")).read()
tree = ast.parse(src)
funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
identifiers = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | set(funcs) | {a.arg for n in funcs.values() for a in n.args.args}
calls_in = lambda fname: {c.func.id for c in ast.walk(funcs[fname]) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
str_consts = lambda fname: {c.value for c in ast.walk(funcs[fname]) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
type_purposes = set(GA.TYPE_PURPOSE.values())
chk("EX-01", "compiled", "no freshness-witness purpose or statement type", "freshness-witness" not in GA.PURPOSE_SHAPE and "freshness-witness" not in type_purposes and not any("witness" in t for t in GA.TYPE_PURPOSE))
chk("EX-02", "compiled", "genuine-binary rule requires the record's admitter digest among the listed admitters", "listed_admitters" in {a.arg for a in funcs["gov_run"].args.args} and "RECORD_ADMITTER_NOT_LISTED" in str_consts("gov_run"))
chk("EX-04", "compiled", "FIRST_CONTACT_QUORUM == 2; no platform-signature, compiled-manifest or channel-quorum identifier", GA.FIRST_CONTACT_QUORUM == 2 and not any(re.search(r"platform_sig|code_signature|compiled_fcm|fcm_digest|channel_quorum", i) for i in identifiers),
    sorted(i for i in identifiers if re.search(r"platform|fcm|channel", i)))
chk("EX-05", "compiled", "gov-admit has no platform code-signature verification or submitter function", not any(re.search(r"platform.*(sig|verify)|submit", f) for f in funcs), sorted(funcs))


def age_warning_informational():
    """OP-5: METADATA_AGE_WARNING_DAYS is read only by display_age_warning; display_age_warning is called only as the value of the
    `age_note` keyword of an ACCEPTED result, never inside a test, a comparison or a refusal."""
    readers = [f for f, n in funcs.items() if "METADATA_AGE_WARNING_DAYS" in ast.unparse(n)]
    uses = []
    for fname in ("accept", "gov_run", "fc_procedure", "custodian_publish"):
        for node in ast.walk(funcs[fname]):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == "display_age_warning":
                    uses.append((fname, type(node).__name__))
            if isinstance(node, ast.keyword) and isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) == "display_age_warning":
                uses.append((fname, "keyword:" + str(node.arg)))
    in_tests = [u for u in uses if u[1] in ("If", "Compare", "BoolOp", "UnaryOp", "IfExp", "While", "Assert")]
    only_note = all(u[1] in ("keyword:age_note", "keyword") for u in uses)
    return readers == ["display_age_warning"] and not in_tests and only_note, {"readers": readers, "uses": uses}


_ok, _det = age_warning_informational()
chk("EX-07", "compiled", "the OP-5 age warning is informational: read only by display_age_warning, used only as the age_note of an ACCEPTED result", _ok, _det)
chk("EX-08", "compiled", "decision rule: no anchor -> TRUST_STATE_UNANCHORED; anchor validity ceilings", "TRUST_STATE_UNANCHORED" in str_consts("gov_run") and {k: v.days for k, v in GA.ANCHOR_VALIDITY.items()} == {"workstation": 90, "ci-image": 7})
chk("EX-09", "compiled", "release-registration purpose shape (3 keys, threshold 2)", tuple(GA.PURPOSE_SHAPE["release-registration"]) == (3, 2), GA.PURPOSE_SHAPE["release-registration"])
chk("EX-10", "compiled", "release-final minimum threshold 2; candidate/final key sharing is not whitelisted and root_conforms enforces the pairwise whitelist",
    GA.PURPOSE_SHAPE["release-final"][1] == 2 and frozenset(("release-candidate", "release-final")) not in GA.WHITELIST and "WHITELIST" in ast.unparse(funcs["root_conforms"]))
chk("EX-12", "compiled", "anchor validity 90 d / 7 d; C3 currency 24 h", {k: v.days for k, v in GA.ANCHOR_VALIDITY.items()} == {"workstation": 90, "ci-image": 7} and GA.C3_CURRENCY.total_seconds() == 86400)
chk("EX-13", "compiled", "MIN_VERIFICATION_RECORDS == 2", GA.MIN_VERIFICATION_RECORDS == 2)
chk("EX-15", "compiled", "toolchain independence computed over provenance attributes", GA.TOOLCHAIN_ATTRS == ("bootstrap_root", "package_source", "build_system", "signing_infrastructure") and "TOOLCHAIN_ATTRS" in ast.unparse(funcs["accept"]))
chk("EX-16", "compiled", "computed security minimum applied in accept", "RELEASE_BELOW_SECURITY_MINIMUM" in str_consts("accept"))
chk("EX-17,EX-18", "compiled", "FIRST_CONTACT_QUORUM == 2; admission state age <= 24 h", GA.FIRST_CONTACT_QUORUM == 2 and GA.ADMISSION_STATE_MAX_AGE.total_seconds() == 86400)
chk("EX-20", "compiled", "revoked running binary: C0-R diagnostics only", GA.C0_R == ("version", "doctor", "status", "kernel-trust-report", "trust-show") and "BINARY_REVOKED_SELF" in str_consts("gov_run"))
chk("EX-21", "compiled", "supplier independence computed over provenance attributes", GA.SUPPLIER_ATTRS == ("base_image_lineage", "package_source", "build_system", "signing_infrastructure") and "SUPPLIER_ATTRS" in ast.unparse(funcs["accept"]))
chk("EX-23", "compiled", "first-contact authority purpose shares keys only with root and trust-policy (whitelist)", GA.WHITELIST == {frozenset(("root", "trust-policy")), frozenset(("root", "first-contact-authority")), frozenset(("trust-policy", "first-contact-authority"))})
actions = {c for c in str_consts("gov_run") if re.fullmatch(r"C[0-3]|confirm-state|trust-gate-confirm", c)} | set(GA.C0_R)
chk("EX-24", "compiled", "the certified command set has no fc-procedure command", not any("procedure" in a for a in actions), sorted(actions))

# ================================================================================================ refusal
T = W.T11
REF = {}


def adm_(binary=None, fca_env=None, tss_env=None, bundle=None, **kw):
    return W.admit(binary or W.R9.binary, fca_env or W.FCA2, tss_env or T, bundle if bundle is not None else W.FULL, verifier=V, workdir=SCR, **kw)["result"]


def tss11(**changes):
    p = copy.deepcopy(T["payload"])
    p.update(changes)
    return W.envelope("trust-state+json", p, ["ts1", "ts2"])


def with_policy(**over):
    pol = W.envelope("trust-policy+json", W.tps_payload(version=3, min_seq=9, **over), ["r1", "r2"])
    t_ = tss11(references=dict(T["payload"]["references"], trust_policy={"version": 3, "digest": pol["digest"]}))
    return adm_(tss_env=t_, bundle=W.FULL + [t_, pol])


def root_with(**grant_over):
    r = W.envelope("root+json", W.root_payload(1, None, W.V1_KEYS + ["wk1", "wk2"], W.grants(**grant_over)), ["r1", "r2"])
    return GA.root_chain(V, W.to_stmts([r]), r["digest"], {})[1]


def reps_variant(plan, envs=((W.ENV_A, "sup-A"), (W.ENV_B, "sup-B")), toolchains=("tc-up", "tc-boot")):
    rel = W.Release("R9", 9, 2, 1, 10, ("g3", "g4"), ("p2", "p4"), security_relevant_change=True, envs=envs, toolchains=toolchains, rep_plan=plan)
    t_ = tss11(registrations=[x for x in T["payload"]["registrations"] if x != W.R9.reg["digest"]] + [rel.reg["digest"]])
    return adm_(rel.binary, tss_env=t_, bundle=[e for e in W.FULL if e not in W.R9.all()] + rel.all() + [t_])


def run(exe, action, root_dir, now=W.NOW, negatives=(), admitters=None, anchor="default", record=None, **kw):
    if record is not None:
        GA.write_admission(record, {}, root_dir, W.LINEAGE)
    anc = {"class": "workstation", "anchored_at": W.NOW, "names_effective_state": True} if anchor == "default" else anchor
    return GA.gov_run(exe, action, root_dir, W.LINEAGE, now, list(negatives), admitters or [W.ADM_D], anchor=anc, **kw)["result"]


def rec_(digest, admitter=None, at=None, path="workstation", **over):
    return dict(GA.make_record(digest, W.TARGET, "R9", W.LINEAGE, "t", "s", admitter or W.ADM_D, at or W.NOW, path), **over)


d = lambda name: os.path.join(SCR, name)
att_same = W.envelope("verification-attestation+json", dict(W.R9.atts[1]["payload"], verifier_execution_id=W.R9.atts[0]["payload"]["verifier_execution_id"],
                                                             verification_report_digest=W.R9.atts[0]["payload"]["verification_report_digest"]), ["v2"])
reg_same = W.R9._registration(verification_records=[W.R9.atts[0]["digest"], att_same["digest"]])
t_same = tss11(registrations=[x for x in T["payload"]["registrations"] if x != W.R9.reg["digest"]] + [reg_same["digest"]])
reg_nodig = W.R9._registration(binary_digests={W.TARGET: W.sha256d(b"custodians-other-digest")})
t_nodig = tss11(registrations=[x for x in T["payload"]["registrations"] if x != W.R9.reg["digest"]] + [reg_nodig["digest"]])
t_secmin = tss11(references=dict(T["payload"]["references"], trust_policy={"version": 1, "digest": W.TPS1["digest"]}), revocations=W.T10["payload"]["revocations"],
                 revocation_statements=W.T10["payload"]["revocation_statements"])
FCA_TS = W.envelope("first-contact-authority+json", W.fca_payload(3, {W.TARGET: W.SUB_ADM_D}, root_version=2, issued="2026-09-14T00:00:00Z"), ["ts1", "ts2"])
FCA_ONE = W.envelope("first-contact-authority+json", W.fca_payload(3, {W.TARGET: W.SUB_ADM_D}, root_version=2, issued="2026-09-14T00:00:00Z"), ["r1"])


def naming(fca_env):
    p = T["payload"]
    return W.tss(12, "2026-09-14T03:00:00Z", W.ROOT2, 2, W.TPS2, fca_env, W.PRIOR11 + [{"sequence": 11, "digest": T["digest"]}], p["registrations"], p["published_binaries"], p["revocations"],
                 revocation_statements=p["revocation_statements"])


tc, sc = W.codes(W.FCA2, T)
T_FCATS, T_FCAONE = naming(FCA_TS), naming(FCA_ONE)
VECTORS = [
    ("EX-01", "root granting freshness-witness", lambda: root_with(**{"freshness-witness": {"keys": [W.kid("wk1"), W.kid("wk2")], "threshold": 2}}), "PROFILE_NONCONFORMANT"),
    ("EX-01", "Trust Policy with witness validity", lambda: with_policy(bootstrap={"accepted_tbm_reset": None, "witness_max_validity_hours": 168}), "PROFILE_NONCONFORMANT"),
    ("EX-01", "witness offered at admission", lambda: adm_(offered={"freshness_witness"}), "PROFILE_MODE_EXCLUDED"),
    ("EX-02", "record by a helper-machine admitter not listed", lambda: run(W.R9.binary, "C1", d("ex02"), record=rec_(W.R9.D, admitter="sha256:" + "d" * 64)), "RECORD_ADMITTER_NOT_LISTED"),
    ("EX-03", "record by a script admitter", lambda: run(W.R9.binary, "C1", d("ex03"), record=rec_(W.R9.D, admitter_kind="auditable-script")), "RECORD_ADMITTER_NOT_LISTED"),
    ("EX-03", "admission evaluated by an unlisted script", lambda: adm_(evaluator=W.SUB_ADM_D), "ADMITTER_NOT_LISTED"),
    ("EX-04", "platform path offered", lambda: adm_(offered={"platform_code_signature"}), "PROFILE_MODE_EXCLUDED"),
    ("EX-04", "Trust Policy channel quorum 1", lambda: with_policy(bootstrap={"accepted_tbm_reset": None, "channel_quorum": 1}), "PROFILE_NONCONFORMANT"),
    ("EX-05", "platform package submitted to the first-contact procedure", lambda: GA.fc_procedure(W.pages(W.FCA2, T), W.canon(W.FCA2["payload"]), W.SUB_ADM, W.TARGET, d("p5"), offered={"platform_code_signature"})["result"], "PROFILE_MODE_EXCLUDED"),
    ("EX-05", "package submitter offered at admission", lambda: adm_(offered={"package_submitter"}), "PROFILE_MODE_EXCLUDED"),
    ("EX-06", "Trust Policy mode B", lambda: with_policy(gating={"mode": "fresh_certified_may_skip_update_gate"}), "PROFILE_NONCONFORMANT"),
    ("EX-07", "Trust Policy eligible_until", lambda: with_policy(eligibility={"min_release_sequence": 9, "min_binary_version": "4.1.6", "eligible_until": "2027-01-01T00:00:00Z"}), "PROFILE_NONCONFORMANT"),
    ("EX-07", "Trust Policy op7_mode compiled epoch", lambda: with_policy(bootstrap={"accepted_tbm_reset": None, "op7_mode": "compiled_epoch_for_use"}), "PROFILE_NONCONFORMANT"),
    ("EX-07,EX-08", "unanchored C1", lambda: run(W.R9.binary, "C1", d("ex08a"), anchor=None, record=rec_(W.R9.D)), "TRUST_STATE_UNANCHORED"),
    ("EX-08", "workstation anchor 91 days old, C2", lambda: run(W.R9.binary, "C2", d("ex08b"), anchor={"class": "workstation", "anchored_at": "2026-06-15T06:00:00Z", "names_effective_state": True},
                                                          record=rec_(W.R9.D, at="2026-06-16T06:00:00Z")), "TRUST_ANCHOR_EXPIRED"),
    ("EX-09", "registration on root keys", lambda: root_with(**{"release-registration": {"keys": [W.kid(x) for x in W.ROOT_KEYS], "threshold": 2}}), "PROFILE_NONCONFORMANT"),
    ("EX-10", "release-final threshold 1", lambda: root_with(**{"release-final": {"keys": [W.kid("f1"), W.kid("f2")], "threshold": 1}}), "PROFILE_NONCONFORMANT"),
    ("EX-10", "candidate and final share a key", lambda: root_with(**{"release-final": {"keys": [W.kid("c1"), W.kid("f2")], "threshold": 2}}), "PROFILE_NONCONFORMANT"),
    ("EX-11", "Trust Policy op6_mode", lambda: with_policy(bootstrap={"accepted_tbm_reset": None, "op6_mode": "confirm_every_init"}), "PROFILE_NONCONFORMANT"),
    ("EX-12", "Trust Policy max_anchor_age_days", lambda: with_policy(bootstrap={"accepted_tbm_reset": None, "max_anchor_age_days": 180}), "PROFILE_NONCONFORMANT"),
    ("EX-12", "CI anchor 8 days old", lambda: run(W.R9.binary, "C1", d("ex12"), anchor={"class": "ci-image", "anchored_at": "2026-09-06T06:00:00Z", "names_effective_state": True},
                                               record=rec_(W.R9.D, at="2026-09-10T06:00:00Z", path="ci-image")), "TRUST_ANCHOR_EXPIRED"),
    ("EX-12", "C3 with currency 25 hours old", lambda: run(W.R9.binary, "C3", d("ex12b"), anchor={"class": "workstation", "anchored_at": "2026-09-10T06:00:00Z", "currency_at": "2026-09-13T05:00:00Z",
                                                                                              "names_effective_state": True}, record=rec_(W.R9.D, at="2026-09-10T06:00:00Z")), "TRUST_STATE_CURRENCY_UNPROVEN"),
    ("EX-13", "Trust Policy min_verification_records 1", lambda: with_policy(registration={"min_verification_records": 1}), "PROFILE_NONCONFORMANT"),
    ("EX-13", "two signatures over one verification execution", lambda: adm_(tss_env=t_same, bundle=[e for e in W.FULL if e is not W.R9.reg] + [t_same, reg_same, att_same]), "VERIFICATION"),
    ("EX-14", "root reproducer quorum 3", lambda: (lambda r: GA.root_chain(V, W.to_stmts([r]), r["digest"], {})[1])(
        W.envelope("root+json", dict(W.root_payload(1, None, W.V1_KEYS, W.grants()), quorums={"reproducer": 3}), ["r1", "r2"])), "PROFILE_NONCONFORMANT"),
    ("EX-14", "registered binary digest differs from the reproduced digest (OP-9 (d))", lambda: adm_(tss_env=t_nodig, bundle=[e for e in W.FULL if e is not W.R9.reg] + [t_nodig, reg_nodig]), "BINARY_NOT_REGISTERED"),
    ("EX-14", "one reproduction", lambda: reps_variant([("p2", W.ENV_A, "tc-up")]), "REPRODUCTION_QUORUM_NOT_MET"),
    ("EX-15", "second toolchain is a relabelled upstream lineage", lambda: reps_variant([("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_B, "tc-up-relabelled")], toolchains=("tc-up", "tc-up-relabelled")), "TOOLCHAIN_DIVERSITY_NOT_MET"),
    ("EX-15", "both reproductions from one toolchain lineage", lambda: reps_variant([("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_B, "tc-up")]), "TOOLCHAIN_DIVERSITY_NOT_MET"),
    ("EX-16", "release below the computed security minimum under a Trust Policy minimum of 1", lambda: adm_(W.R8.binary, tss_env=t_secmin, bundle=W.FULL + [t_secmin]), "RELEASE_BELOW_SECURITY_MINIMUM"),
    ("EX-17", "one source", lambda: adm_(k=1), "FIRST_CONTACT_SOURCES_BELOW_QUORUM"),
    ("EX-17", "two sources disagree", lambda: GA.accept(W.R9.binary, [tc, tc[:-8] + "0" * 8], [sc, sc], W.to_stmts(W.FULL), W.TARGET, W.ADM_D, "workstation", W.NOW, {"lineage": W.LINEAGE},
                                                         verifier=V, workdir=SCR)["result"], "FIRST_CONTACT_DISAGREEMENT"),
    ("EX-18", "media-carried state older than 24 hours", lambda: adm_(now="2026-09-15T01:00:00Z"), "FIRST_CONTACT_STATE_TOO_OLD"),
    ("EX-18", "media as the only source", lambda: adm_(k=1), "FIRST_CONTACT_SOURCES_BELOW_QUORUM"),
    ("EX-19", "workstation record 105 days old", lambda: run(W.R9.binary, "C1", d("ex19"), record=rec_(W.R9.D, at="2026-06-01T00:00:00Z")), "ADMISSION_RECORD_EXPIRED"),
    ("EX-19", "CI record 13 days old", lambda: run(W.R9.binary, "C1", d("ex19b"), anchor={"class": "ci-image", "anchored_at": W.NOW, "names_effective_state": True},
                                                record=rec_(W.R9.D, at="2026-09-01T00:00:00Z", path="ci-image")), "ADMISSION_RECORD_EXPIRED"),
    ("EX-20", "Trust Policy revoked_self_scope", lambda: with_policy(bootstrap={"accepted_tbm_reset": None, "revoked_self_scope": "C0_C2"}), "PROFILE_NONCONFORMANT"),
    ("EX-20", "revoked running binary C2", lambda: run(W.R9.binary, "C2", d("ex20"), negatives=[W.R9.D], record=rec_(W.R9.D)), "BINARY_REVOKED_SELF"),
    ("EX-21", "reproductions from one supplier class", lambda: reps_variant([("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_A, "tc-boot")]), "ENVIRONMENT_DIVERSITY_NOT_MET"),
    ("EX-21", "second class is a relabelled first supplier", lambda: reps_variant([("p2", W.ENV_A, "tc-up"), ("p4", W.ENV_AM, "tc-boot")], envs=((W.ENV_A, "sup-A"), (W.ENV_AM, "sup-A-mirror"))), "ENVIRONMENT_DIVERSITY_NOT_MET"),
    ("EX-23", "authority signed by trust-state keys", lambda: adm_(fca_env=FCA_TS, tss_env=T_FCATS, bundle=W.FULL + [FCA_TS, T_FCATS]), "FIRST_CONTACT_AUTHORITY_UNVERIFIED"),
    ("EX-23", "authority signed by one root key", lambda: adm_(fca_env=FCA_ONE, tss_env=T_FCAONE, bundle=W.FULL + [FCA_ONE, T_FCAONE]), "FIRST_CONTACT_AUTHORITY_UNVERIFIED"),
    ("EX-24", "gov trust fc-procedure on an admitted binary", lambda: run(W.R9.binary, "trust fc-procedure", d("ex24"), record=rec_(W.R9.D)), "PROFILE_MODE_EXCLUDED"),
]
control = {"CP-1 admission": adm_(), "CP-1 admitted binary C2": run(W.R9.binary, "C2", d("ctl"), record=rec_(W.R9.D))}
for exs, name, fn, expect in VECTORS:
    try:
        got = fn()
    except Exception as e:  # noqa: BLE001
        got = "EXCEPTION:" + repr(e)[:160]
    REF[name] = got
    chk(exs, "refusal", name, isinstance(got, str) and got.startswith(expect), {"got": got, "expected_prefix": expect})
control_ok = control["CP-1 admission"] == "ACCEPTED" and control["CP-1 admitted binary C2"] == "ALLOWED"

# ================================================================================================ calculator
spec = importlib.util.spec_from_file_location("cs7", os.path.join(HERE, "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
atoms = {a for v in CS7.ATOMS.values() for a in v}
cfgs = CS7.configs()
victims = {c["victim"] for _, c in cfgs}
cfg_keys = sorted({k for _, c in cfgs for k in c if k != "victim"})
calc_base = not cfg_keys and all(CS7.R7.values()) and "non-production" in CS7.control_statements([]).lower() and (CS7.N_REP, CS7.Q, CS7.V) == (3, 2, 2)
chk("EX-01", "calculator", "no witness victim or atom; production configuration CP-1 only", calc_base and not victims & {"WR", "W"} and not atoms & {"wk1", "wk2", "witness"}, {"victims": sorted(victims), "config_keys": cfg_keys})
chk("EX-04", "calculator", "no alternative-path atom", calc_base and not atoms & {"alt", "platform", "ch1", "ch2"}, sorted(atoms))
chk("EX-05", "calculator", "no alternative-path or submitter atom", calc_base and not atoms & {"alt", "submit", "platform"})
chk("EX-15", "calculator", "V_TOOLCHAIN_DIVERSITY on; no toolchain configuration axis", calc_base and CS7.R7.get("V_TOOLCHAIN_DIVERSITY") is True and "tc" not in cfg_keys)
chk("EX-21", "calculator", "V_ENV_DIVERSITY and V_SUPPLIER_PROVENANCE on; no environment configuration axis", calc_base and CS7.R7.get("V_ENV_DIVERSITY") is True and CS7.R7.get("V_SUPPLIER_PROVENANCE") is True and "env" not in cfg_keys)

# ================================================================================================ register
REG = yaml.safe_load(open(os.path.join(PACK, "decision-register", "DECISION_REGISTER.yaml")))
excl = {}
for row in REG.get("excluded_inputs", []):
    if row.get("role") == "excluded":
        excl.setdefault(row.get("exclusion"), []).append(row)
D8 = yaml.safe_load(open(os.path.join(REPO, "spec", "decisions", "D-0008.yaml")))
for ex in EXIDS:
    rows = excl.get(ex, [])
    chk(ex, "register", "decision register has an excluded-input row with mechanism and tests", bool(rows) and all(r.get("mechanism") and r.get("tests") for r in rows), len(rows))
opts = {o["id"]: o.get("description", "") for o in D8.get("options", [])}
chk("EX-22", "register", "D-0008 marks options A, B, D, E, F not supported production alternatives; no chosen option; PROPOSED",
    sorted(k for k in opts if k != "C") == ["A", "B", "D", "E", "F"] and all("not a supported production alternative" in v.lower() for k, v in opts.items() if k != "C")
    and "chosen_option" not in D8 and D8.get("status") == "PROVISIONAL" and D8.get("proposal_state") == "PROPOSED" and D8.get("human_approved") is False and D8.get("in_effect") is False)

# ================================================================================================ per exclusion
per = {}
for ex in EXIDS:
    mine = [c for c in CHECKS if c["exclusion"] == ex]
    kinds = sorted({c["kind"] for c in mine})
    missing = [k for k in DECLARED[ex] if k not in kinds]
    per[ex] = {"declared_mechanisms": DECLARED[ex], "checked_kinds": kinds, "declared_kinds_without_check": missing, "checks": len(mine), "failing": [c for c in mine if not c["holds"]],
               "holds": not missing and all(c["holds"] for c in mine)}

# ================================================================================================ P7 normative text
NORMATIVE = ["05-KEY-MANAGEMENT.md", "06-BOOTSTRAP.md", "24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", "25-BINARY-AND-TRUST-BASE-AUTHENTICITY.md", "27-TRUST-DECISION-AUTHORISATION.md",
             "30-RELEASE-REGISTRATION-AND-REPRODUCTION.md", "31-INDEPENDENT-ADMISSION.md", "32-FIRST-CONTACT-ROOT.md", "33-BUILD-ENVIRONMENT.md", "34-FIRST-HAND-CONSTITUTIONAL-CONTENT.md", "35-CERTIFIED-PROFILE.md"]
EXCLUDED = re.compile(r"OP-7 \((b|c|d)\)|freshness[- ]witness|OP-13 \((a|c|d)\)|either suffices|[Mm]ode B|OP-16 \((a|c)\)|OP-2 \(a\)|OP-9 \((a|c)\)|OP-10 \((a|c)\)|OP-11 \((a|c)\)|OP-12 \((b|c)\)|"
                      r"OP-14 \(a\)|OP-15 \(b\)|OP-6 \((b|c)\)|fc-procedure|platform (code-)?sign|eligible_until|helper[- ]machine")
MARK = re.compile(r"exclu|non-production|not production|history|historical|refus|withdrawn|removed|EX-\d|not implemented|not a supported|not selected|unselected|absent|"
                  r"revision[- ]?[1-6]\b|review r[1-6]|RV[1-6]|CR[1-6]|control|never|not certified|instead of|replaces|mutant|trade-off|OT-\d|PROFILE_", re.I)
P7 = {}
for fn in NORMATIVE:
    p = os.path.join(PACK, fn)
    if not os.path.exists(p):
        P7[fn] = {"missing": True, "unmarked_lines": []}
        continue
    P7[fn] = {"unmarked_lines": [(i + 1, l[:200]) for i, l in enumerate(open(p).read().split("\n")) if EXCLUDED.search(l) and not MARK.search(l)]}
P7_holds = all(not v.get("missing") and not v["unmarked_lines"] for v in P7.values())

out = {"probe": "PROF7 profile conformance of CP-1 (AR-0019)", "profile_id": PROFILE["profile_id"], "P1_profile_file": P1, "environment_manifest_schema_properties": EMA,
       "refusal_results": REF, "controls": control, "checks": CHECKS, "per_exclusion": per, "P7_normative_text": P7,
       "summary": {"exclusions": len(EXIDS), "exclusions_holding": sum(1 for v in per.values() if v["holds"]), "checks": len(CHECKS), "checks_holding": sum(1 for c in CHECKS if c["holds"]),
                   "checks_by_kind": {k: sum(1 for c in CHECKS if c["kind"] == k) for k in ("schema", "compiled", "refusal", "calculator", "register")},
                   "refusal_vectors": len(VECTORS), "normative_files": len(NORMATIVE), "normative_unmarked_lines": sum(len(v["unmarked_lines"]) for v in P7.values())}}
out["verdicts"] = {"P1_profile_file_complete": P1["holds"], "every_exclusion_holds_under_every_declared_mechanism": all(v["holds"] for v in per.values()),
                   "controls_accepted": control_ok, "environment_manifest_schema_properties_hold": all(EMA.values()), "P7_normative_text_marks_every_excluded_mention": P7_holds}
print(json.dumps(out, indent=1, sort_keys=True, default=str).replace(SCR, "<scratch>"))
