#!/usr/bin/env python3
"""RoT-1 revision 7 (CP-1) — schema-validated illustrative instances of the records revision 7 adds or changes, and refusal of the
withdrawn and excluded shapes (AR-0019). Illustrative only: no key, signature, digest or ceremony is real. Deterministic.

Records: first-contact authority record; environment lock; environment manifest v2; environment reproduction v2; input manifest v3;
release registration v3; binary reproduction v3; verification attestation v5; admission record v3; trust state v4; trust root v5;
Trust Policy v4 (minimal surface); revocation v3; trust-state pin v3; trust-gate confirmation v3; decision pin v4; Trust Base Manifest v4.
Refused shapes: every exclusion that has a schema mechanism in `profile/CP-1.yaml`, and the revision-6 shapes revision 7 replaces.
Usage: python3 make_rev7.py   (writes `*.json` and `validation.json` next to this script)
"""
import copy, glob, hashlib, json, os, sys

import jsonschema

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SD = os.path.join(HERE, "..", "..", "schemas")


def sd(label):
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


def kid(label):
    return "ed25519:" + hashlib.sha256(("key:" + label).encode()).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def validate(name, inst):
    v = jsonschema.Draft202012Validator(json.load(open(os.path.join(SD, name))))
    errs = sorted(e.message for e in v.iter_errors(inst))
    return {"schema": name, "valid": not errs, "errors": errs[:4]}


T = "x86_64-unknown-linux-musl"
LIN = sd("example-lineage-root-v1")
SRC = {"release_commit": "1" * 40, "git_tree": "2" * 40, "content_digest": sd("source-v2")}
NOW = "2026-09-14T00:00:00Z"
SOURCES = [{"source_id": "src-private", "kind": "authenticated-private-release-channel", "locator": "https://releases.owner.invalid/private", "custodian_role": "release-channel-custodian", "custody_domain": "owner-release-operations"},
           {"source_id": "src-mirror", "kind": "immutable-release-mirror", "locator": "https://mirror.owner-archive.invalid/immutable", "custodian_role": "archive-custodian", "custody_domain": "owner-archive-trust"}]
fca = {"fca_sequence": 2, "lineage": LIN, "root_version": 2, "profile_id": "governance-os.rot1/CP-1", "admitters": {T: sd("gov-admit-x86_64-musl")}, "certified_targets": [T], "sources": SOURCES,
       "procedure_digest": sd("FC-PROC-1"), "admitter_evidence": {"registration_digest": sd("admitter-registration"), "reproduction_digests": [sd("adm-rep-1"), sd("adm-rep-2")],
                                                                   "verification_records": [sd("adm-va-1"), sd("adm-va-2")]}, "supersedes_fca_digest": sd("fca-1"), "issued_at": NOW}
trust_code = "gov-fct:%s:%d:%s" % (LIN[7:15], 2, hashlib.sha256(canon(fca)).hexdigest())
lock = {"schema": "governance-os.environment-lock/1", "environments": [
    {"target": T, "supplier_id": "sup-A", "components": [{"name": "musl-cross-toolchain-base", "version": "1.2.5-1", "sha256": sd("comp-a-1"), "placement_path": "bin/cc", "mode": 493}]},
    {"target": T, "supplier_id": "sup-B", "components": [{"name": "musl-dev", "version": "1.2.5-r1", "sha256": sd("comp-b-1"), "placement_path": "bin/cc", "mode": 493}]}]}
entry = lock["environments"][0]
manifest = {"schema": "governance-os.environment-manifest/2", "target": T, "supplier_id": "sup-A", "lock_digest": sd("lock-entry-A"),
            "components": [dict(entry["components"][0], checksum_key_id=kid("upstream-A"), checksum_file_digest=sd("SHA256SUMS-A"))], "assembly_function": "gov-envassemble/1",
            "environment_tree_digest": sd("tree-A")}
ENV_A, ENV_B = sd("environment-manifest-A"), sd("environment-manifest-B")
env_repro = {"_type": "https://agentic-engineering-os/statement/environment-reproduction/v2", "trust_root_id": LIN, "environment_id": ENV_A, "environment_tree_digest": sd("tree-A"),
             "lock_digest": sd("lock-entry-A"), "target": T, "supplier_id": "sup-A", "reproduced_at": NOW}
inputs = {"schema": "governance-os.input-manifest/3", "toolchains": [{"toolchain_id": "tc-up", "compiler_version": "1.98.1", "archive_sha256": sd("rustc-upstream")},
                                                                    {"toolchain_id": "tc-boot", "compiler_version": "1.98.1", "archive_sha256": sd("rustc-bootstrapped")}],
          "lockfile_sha256": sd("Cargo.lock"), "environment_lock_digest": sd("ENVIRONMENT_LOCK.json"),
          "build_profile": {"remap_path_prefixes": ["/src=/build", "/cargo=/cargo", "/toolchain=/toolchain"], "profile": "release", "flags": ["-C", "codegen-units=1"], "linking": "static-self-contained"}, "targets": [T]}
registration = {"_type": "https://agentic-engineering-os/statement/release-registration/v3", "trust_root_id": LIN, "release_id": "agentic-engineering-os@4.1.6#0123456789abcdef", "sequence": 1600,
                "final_statement_digest": sd("final"), "candidate_statement_digest": sd("candidate"), "source": SRC, "inputs_manifest_digest": sd("inputs"), "environment_lock_digest": sd("ENVIRONMENT_LOCK.json"),
                "targets": [T], "verification_records": [sd("va-1"), sd("va-2")], "constitution": {"kernel_tree_digest": sd("kernel"), "units": {}}, "migrations": {},
                "environments": [{"target": T, "environment_id": ENV_A, "supplier_id": "sup-A", "environment_reproductions": [sd("er-a-1"), sd("er-a-2")]},
                                 {"target": T, "environment_id": ENV_B, "supplier_id": "sup-B", "environment_reproductions": [sd("er-b-1"), sd("er-b-2")]}],
                "toolchains": [{"target": T, "toolchain_id": "tc-up"}, {"target": T, "toolchain_id": "tc-boot"}], "binary_digests": {T: sd("gov-binary")}, "security_relevant_change": False, "issued_at": NOW}
reproduction = {"_type": "https://agentic-engineering-os/statement/binary-reproduction/v3", "trust_root_id": LIN, "release_id": registration["release_id"], "source": SRC, "inputs_manifest_digest": sd("inputs"),
                "target": T, "binary_digest": sd("gov-binary"), "tbm_digest": sd("tbm"), "environment_id": ENV_B, "toolchain_id": "tc-boot", "reproduced_at": NOW}
attestation = {"_type": "https://agentic-engineering-os/statement/verification-attestation/v5", "trust_root_id": LIN, "issued_at": NOW, "candidate_statement_digest": sd("candidate"),
               "release_id": registration["release_id"], "verdict": "ACCEPTED", "source": SRC, "inputs_manifest_digest": sd("inputs"), "kernel_tree_digest": sd("kernel"), "environment_ids": [ENV_A, ENV_B],
               "toolchain_ids": ["tc-up", "tc-boot"], "verification_report_digest": sd("report-1"), "verifier_execution_id": "verifier-1-run-2026-09-13", "verifier_label": "independent verifier 1"}
tss = {"_type": "https://agentic-engineering-os/statement/trust-state/v4", "trust_profile": "production", "framework": "agentic-engineering-os", "trust_root_id": LIN, "issued_at": NOW, "sequence": 11,
       "previous_state_digest": sd("tss-10"), "prior_states": [{"sequence": 10, "statement_digest": sd("tss-10")}],
       "references": {"root": {"version": 2, "digest": sd("root-v2")}, "trust_policy": {"version": 2, "digest": sd("tps-v2")}, "first_contact_authority": {"fca_sequence": 2, "digest": sd("fca-2")}},
       "registrations": [sd("reg-1600")], "published_binaries": [sd("gov-binary")], "revocations": [sd("revoked-binary")], "revocation_statements": [sd("revocation-statement-9")]}
state_code = "gov-fcs:%s:%d:%s" % (LIN[7:15], 11, hashlib.sha256(canon(tss)).hexdigest())
record = {"schema": "governance-os.admission-record/3", "binary_digest": sd("gov-binary"), "target": T, "release_id": registration["release_id"], "lineage": LIN, "trust_code": trust_code,
          "state_code": state_code, "admitted_at": NOW, "admitter_digest": sd("gov-admit-x86_64-musl"), "admitter_kind": "compiled-gov-admit", "path_class": "workstation", "valid_until": "2026-12-13T00:00:00Z"}
PK = lambda l: {"alg": "ed25519", "public_key": ("A" * 42 + l[:1].upper() + "=")[-44:], "label": l, "added_in_version": 1}
labels = ["r1", "r2", "r3", "ts1", "ts2", "ts3", "rv1", "rv2", "rv3", "g1", "g2", "g3", "p1", "p2", "p3", "v1", "v2", "f1", "f2", "c1", "cs1", "cs2", "rp1"]
purp = lambda ls, th: {"key_ids": [kid(x) for x in ls], "threshold": th}
root = {"_type": "https://agentic-engineering-os/statement/trust-root/v2", "trust_profile": "production", "framework": "agentic-engineering-os", "version": 1, "lineage": {"trust_root_id": None},
        "keys": {kid(l): PK(l) for l in labels}, "purposes": {"root": purp(["r1", "r2", "r3"], 2), "trust-policy": purp(["r1", "r2", "r3"], 2), "first-contact-authority": purp(["r1", "r2", "r3"], 2),
                                                             "trust-state": purp(["ts1", "ts2", "ts3"], 2), "revocation": purp(["rv1", "rv2", "rv3"], 2), "release-registration": purp(["g1", "g2", "g3"], 2),
                                                             "reproducer": purp(["p1", "p2", "p3"], 1), "verification-attestation": purp(["v1", "v2"], 1), "release-final": purp(["f1", "f2"], 2),
                                                             "release-candidate": purp(["c1"], 1), "certification-status": purp(["cs1", "cs2"], 2), "retrieval-profile": purp(["rp1"], 1)},
        "revoked_keys": [], "issued_at": NOW, "quorums": {"reproducer": 2}, "profile_id": "governance-os.rot1/CP-1"}
tps = {"_type": "https://agentic-engineering-os/statement/trust-policy/v4", "trust_profile": "production", "framework": "agentic-engineering-os", "trust_root_id": LIN, "issued_at": NOW, "policy_version": 2,
       "supersedes_policy_digest": sd("tps-1"), "floor_schema_version": 3, "profile_id": "governance-os.rot1/CP-1",
       "eligibility": {"min_release_sequence": 1600, "min_binary_version": "4.1.6", "production_stage": "final", "evaluation_candidates": "refuse", "historical_releases": []},
       "install_authority": {k: "L4" for k in ("allow_unsigned_development", "install_evaluation_candidate", "install_kernel", "override_kernel_integrity", "recover", "rollback_apply", "trust_confirm_root", "trust_confirm_state", "trust_refresh", "update_apply")},
       "gating": {"mode": "always_gate", "refuse_known_rejected": True, "refuse_known_withdrawn": True, "local_terminal_only": ["init_ack", "project_first_use", "framework_update", "downgrade", "rollback", "recovery_exchange", "adopt_lineage"]},
       "bootstrap": {"clock_reset": None, "accepted_tbm_reset": None, "admission_ceilings": {"workstation_anchor_days": 90, "ci_anchor_days": 7, "production_currency_hours": 24, "admission_state_hours": 24}},
       "registration": {"min_verification_records": 2},
       "supply_chain": {"suppliers": [{"supplier_id": "sup-A", "provenance": {"base_image_lineage": "debian-bookworm-images", "package_source": "deb.debian.org", "build_system": "debian-buildd", "signing_infrastructure": "debian-archive-keyring"}, "checksum_keys": [kid("upstream-A")]},
                                      {"supplier_id": "sup-B", "provenance": {"base_image_lineage": "alpine-3.20-images", "package_source": "dl-cdn.alpinelinux.org", "build_system": "alpine-builders", "signing_infrastructure": "alpine-keys"}, "checksum_keys": [kid("upstream-B")]}],
                        "toolchains": [{"toolchain_id": "tc-up", "provenance": {"bootstrap_root": "upstream-binary-stage0", "package_source": "static.rust-lang.org", "build_system": "rust-ci", "signing_infrastructure": "rust-release-key"}, "archive_sha256": sd("rustc-upstream")},
                                       {"toolchain_id": "tc-boot", "provenance": {"bootstrap_root": "mrustc-source-bootstrap", "package_source": "owner-source-mirror", "build_system": "owner-bootstrap-builders", "signing_infrastructure": "owner-registration-quorum"}, "bootstrap_registration": sd("tc-boot-registration")}]},
       "certified_targets": [{"target": T, "status": "CERTIFIED", "criteria_evidence_digest": sd("CC-evidence-x86_64-musl")}],
       "sensitivity_order": ["public", "internal", "confidential", "restricted"], "unrevokes": [], "surface": {"schema": "governance-os.constitutional-surface-inventory", "floor_schema_version": 3, "default": "deny", "precedence": {}, "files": []},
       "prior_policies": [{"policy_version": 1, "statement_digest": sd("tps-1")}], "lowering_history": [], "state_chain_reset": None}
revocation = {"_type": "https://agentic-engineering-os/statement/revocation/v2", "trust_profile": "production", "framework": "agentic-engineering-os", "trust_root_id": LIN, "issued_at": NOW, "revocation_sequence": 9,
              "authority": "revocation-quorum", "targets": [{"kind": "binary", "statement_digest": sd("revoked-binary"), "release_id": None, "effect": "refuse_operation", "reason": "enforcement defect"}]}
pin = {"lineage": LIN, "root_version": 2, "root_digest": sd("root-v2"), "policy_version": 2, "policy_digest": sd("tps-v2"), "state_sequence": 11, "state_digest": sd("tss-11"), "state_code": state_code,
       "machine_class": "ci", "provisioned_by": "image operator", "provisioned_at": NOW, "valid_until": "2026-09-21T00:00:00Z"}
gate = {"gate_kind": "project_first_use", "gate_id": "G-1", "project_trust_id": "0" * 32, "repository_path": "/work/project", "bound_digests": [sd("release-final")], "presented_digest": sd("package"),
        "state_codes": [state_code, state_code], "method": "interactive_terminal", "confirmed_at": NOW, "operator": "operator", "consumed_by_transaction": None}
dpin = {"gate_kind": "weakening", "bound_digests": [sd("failure-list")], "project_trust_id": "0" * 32, "approved_under_state": {"sequence": 11, "statement_digest": sd("tss-11")},
        "provisioned_by": "operator", "provisioned_at": NOW, "expires_at": "2026-09-20T00:00:00Z"}
tbm = {"_type": "https://agentic-engineering-os/manifest/trust-base/v2", "framework": "agentic-engineering-os", "trust_profile": "production",
       "binary": {"name": "gov-admit", "version": "4.1.6", "target": T, "build": "release", "source": SRC, "toolchain": "tc-up", "inputs_manifest_digest": sd("inputs")}, "lineage": LIN,
       "root_chain": [{"version": 1, "statement_digest": LIN}], "trust_policy": {"policy_version": 2, "statement_digest": sd("tps-v2")}, "trust_state": {"sequence": 10, "statement_digest": sd("tss-10")},
       "embedded_release": {"final_statement_digest": sd("final"), "kernel_tree_digest": sd("kernel")},
       "compiled_rules": {"floor_schema_version": 3, "operator_vocabulary": "floor-ops/3", "purpose_table_digest": sd("purposes-cp1"), "statement_schemas_digest": sd("schemas-cp1"), "format_readers": ["rot-1"],
                          "command_register_digest": sd("commands-cp1"), "profile_id": "governance-os.rot1/CP-1", "decision_register_digest": sd("register-r7")}}
INST = {"first-contact-authority.payload.example.json": ("first-contact-authority.schema.json", fca), "environment-lock.example.json": ("environment-lock.schema.json", lock),
        "environment-manifest.example.json": ("environment-manifest.schema.json", manifest), "environment-reproduction.payload.example.json": ("environment-reproduction.schema.json", env_repro),
        "input-manifest.example.json": ("input-manifest.schema.json", inputs), "release-registration.payload.example.json": ("release-registration.schema.json", registration),
        "binary-reproduction.payload.example.json": ("binary-reproduction.schema.json", reproduction), "verification-attestation.payload.example.json": ("verification-attestation.schema.json", attestation),
        "admission-record.example.json": ("admission-record.schema.json", record), "trust-state.payload.example.json": ("trust-state-statement.schema.json", tss), "trust-root.payload.example.json": ("trust-root.schema.json", root),
        "trust-policy.payload.example.json": ("trust-policy-statement.schema.json", tps), "revocation.payload.example.json": ("revocation-statement.schema.json", revocation),
        "trust-state-pin.example.json": ("trust-state-pin.schema.json", pin), "trust-gate-confirmation.example.json": ("trust-gate-confirmation.schema.json", gate),
        "trust-decision-pin.example.json": ("trust-decision-pin.schema.json", dpin), "trust-base-manifest.example.json": ("trust-base-manifest.schema.json", tbm)}


def mutate(o, path, value, delete=False):
    o = copy.deepcopy(o)
    cur = o
    for p in path[:-1]:
        cur = cur[p]
    if delete:
        cur.pop(path[-1], None)
    else:
        cur[path[-1]] = value
    return o


REFUSED = {
    "EX-01 root granting freshness-witness": ("trust-root.schema.json", mutate(root, ["purposes", "freshness-witness"], purp(["r1", "r2"], 2))),
    "EX-01 Trust Policy witness validity": ("trust-policy-statement.schema.json", mutate(tps, ["bootstrap", "witness_max_validity_hours"], 168)),
    "EX-02/EX-03 script admitter record": ("admission-record.schema.json", mutate(record, ["admitter_kind"], "auditable-script")),
    "EX-04 Trust Policy channel quorum": ("trust-policy-statement.schema.json", mutate(tps, ["bootstrap", "channel_quorum"], 1)),
    "EX-04/EX-17 authority with one source": ("first-contact-authority.schema.json", mutate(fca, ["sources"], SOURCES[:1])),
    "EX-05 authority source of platform kind": ("first-contact-authority.schema.json", mutate(fca, ["sources"], [SOURCES[0], dict(SOURCES[1], kind="platform-code-signing-service")])),
    "EX-06 Trust Policy mode B": ("trust-policy-statement.schema.json", mutate(tps, ["gating", "mode"], "fresh_certified_may_skip_update_gate")),
    "EX-07 grace period": ("trust-policy-statement.schema.json", mutate(tps, ["eligibility", "eligible_until"], "2027-01-01T00:00:00Z")),
    "EX-08/EX-12 op7_mode": ("trust-policy-statement.schema.json", mutate(tps, ["bootstrap", "op7_mode"], "compiled_epoch_for_use")),
    "EX-09 registration threshold 3 of 4": ("trust-root.schema.json", mutate(root, ["purposes", "release-registration"], purp(["g1", "g2", "g3", "r1"], 3))),
    "EX-10 release-final threshold 1": ("trust-root.schema.json", mutate(root, ["purposes", "release-final"], purp(["f1", "f2"], 1))),
    "EX-11 op6_mode": ("trust-policy-statement.schema.json", mutate(tps, ["bootstrap", "op6_mode"], "confirm_every_init")),
    "EX-12 anchor ceiling above 90 days": ("trust-policy-statement.schema.json", mutate(tps, ["bootstrap", "admission_ceilings", "workstation_anchor_days"], 180)),
    "EX-13 one verification record": ("trust-policy-statement.schema.json", mutate(tps, ["registration", "min_verification_records"], 1)),
    "EX-13 registration with one record": ("release-registration.schema.json", mutate(registration, ["verification_records"], [sd("va-1")])),
    "EX-14 registration without binary digests": ("release-registration.schema.json", mutate(registration, ["binary_digests"], None, delete=True)),
    "EX-14 reproducer quorum 3": ("trust-root.schema.json", mutate(root, ["quorums", "reproducer"], 3)),
    "EX-15 one toolchain": ("input-manifest.schema.json", mutate(inputs, ["toolchains"], inputs["toolchains"][:1])),
    "EX-19 record without expiry": ("admission-record.schema.json", mutate(record, ["valid_until"], None)),
    "EX-20 revoked self scope": ("trust-policy-statement.schema.json", mutate(tps, ["bootstrap", "revoked_self_scope"], "C0_C2")),
    "EX-21 environment diversity switch": ("trust-policy-statement.schema.json", mutate(tps, ["registration", "environment_diversity"], False)),
    "EX-21 registration with one environment": ("release-registration.schema.json", mutate(registration, ["environments"], registration["environments"][:1])),
    "EMA lock with inline content": ("environment-lock.schema.json", mutate(lock, ["environments", 0, "components", 0, "content_b64"], "aGk=")),
    "EMA lock naming a checksum key": ("environment-lock.schema.json", mutate(lock, ["environments", 0, "components", 0, "upstream_checksum_reference"], "author key")),
    "EMA revision-6 manifest with recipe": ("environment-manifest.schema.json", mutate(manifest, ["assembly"], {"recipe_digest": sd("recipe"), "tool": "anything"})),
    "EMA manifest with another assembly function": ("environment-manifest.schema.json", mutate(manifest, ["assembly_function"], "author-tool 1")),
    "RV6-L3 attestation without environments": ("verification-attestation.schema.json", mutate(attestation, ["environment_ids"], None, delete=True)),
    "OP-3 decision pin approving an update": ("trust-decision-pin.schema.json", mutate(dpin, ["gate_kind"], "framework_update")),
    "OP-7 CI pin with revision-6 fingerprint": ("trust-state-pin.schema.json", mutate(pin, ["fingerprint"], "gov-state:00000000:11:" + "0" * 32)),
    "OP-13 confirmation with one state code": ("trust-gate-confirmation.schema.json", mutate(gate, ["state_codes"], [state_code])),
}
for name, (schema, inst) in INST.items():
    with open(os.path.join(HERE, name), "w") as f:
        json.dump(inst, f, indent=2, sort_keys=True)
        f.write("\n")
report = {"generator": "make_rev7.py (AR-0019)", "trust_code_of_example_authority": trust_code, "state_code_of_example_state": state_code,
          "schemas_meta_valid": {}, "instances": {n: validate(s, i) for n, (s, i) in INST.items()}, "refused_shapes": {}}
for p in sorted(glob.glob(os.path.join(SD, "*.json"))):
    try:
        jsonschema.Draft202012Validator.check_schema(json.load(open(p)))
        report["schemas_meta_valid"][os.path.basename(p)] = True
    except Exception as e:  # noqa: BLE001
        report["schemas_meta_valid"][os.path.basename(p)] = str(e)[:200]
for n, (s, i) in REFUSED.items():
    r = validate(s, i)
    report["refused_shapes"][n] = {"schema": s, "refused": not r["valid"], "first_error": (r["errors"] or [None])[0]}
report["summary"] = {"schemas": len(report["schemas_meta_valid"]), "schemas_meta_valid": sum(1 for v in report["schemas_meta_valid"].values() if v is True),
                     "instances": len(INST), "instances_valid": sum(1 for v in report["instances"].values() if v["valid"]),
                     "refused_shapes": len(REFUSED), "refused": sum(1 for v in report["refused_shapes"].values() if v["refused"])}
with open(os.path.join(HERE, "validation.json"), "w") as f:
    json.dump(report, f, indent=2, sort_keys=True)
    f.write("\n")
print(json.dumps(report["summary"]))
