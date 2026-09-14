#!/usr/bin/env python3
"""RoT-1 revision 6 — schema-validated illustrative instances of the records revision 6 adds or changes (AR-0015).

Instances are built from the revision-5 examples (`../rev5/`) where a record already existed, upgraded to the revision-6
fields, plus the new records: first-contact manifest (`32` §3), environment manifest and environment reproduction (`33`),
registration revocation (`30` R-REG-11). The script also records:
  - meta-validation of every schema in `../../schemas/`;
  - validation of every revision-6 instance;
  - refusal by the revision-6 schemas of the revision-5 shapes revision 6 withdraws (input manifest with `build_image_digest`,
    admission record with `state_fingerprint`, verification attestation without `kernel_tree_digest`, release registration
    without `environments` or `source.git_tree`, a root purpose with threshold 1, an empty registration revocation);
  - the first-contact code computed for the example manifest.
Illustrative only: no key, signature, digest or ceremony is real. Deterministic.
Usage: python3 make_rev6.py   (writes `*.json` and `validation.json` next to this script)
"""
import copy, glob, hashlib, json, os, sys

import jsonschema

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMAS = os.path.join(HERE, "..", "..", "schemas")
REV5 = os.path.join(HERE, "..", "rev5")


def sd(label):
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def schema(name):
    return json.load(open(os.path.join(SCHEMAS, name)))


def validate(name, inst):
    v = jsonschema.Draft202012Validator(schema(name))
    errs = sorted(e.message for e in v.iter_errors(inst))
    return {"schema": name, "valid": not errs, "errors": errs[:5]}


def write(name, obj):
    with open(os.path.join(HERE, name), "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


r5 = {os.path.basename(p): json.load(open(p)) for p in glob.glob(os.path.join(REV5, "*.example.json"))}
LIN = sd("example-lineage-root-v1")
SRC = {"release_commit": "1" * 40, "git_tree": "2" * 40, "content_digest": sd("example-source-content-digest-v2")}
ENV_A = sd("example-environment-manifest-A")

fcm = {"schema": "governance-os.first-contact-manifest/1", "lineage_id": LIN,
       "state_epoch": {"root_version": 2, "root_digest": sd("root-v2"), "policy_version": 1, "policy_digest": sd("tps-v1"), "state_sequence": 10, "state_digest": sd("tss-10")},
       "admitters": {"x86_64-unknown-linux-gnu": sd("gov-admit-x86_64-linux"), "aarch64-apple-darwin": sd("gov-admit-aarch64-darwin")},
       "issued_at": "2026-09-14T00:00:00Z", "valid_until": "2026-10-14T00:00:00Z"}
code = "gov-fc:%s:%d:%s" % (LIN[7:15], fcm["state_epoch"]["state_sequence"], hashlib.sha256(canon(fcm)).hexdigest())

env_manifest = {"schema": "governance-os.environment-manifest/1", "target": "x86_64-unknown-linux-gnu", "supplier_class": "A",
                "components": [{"name": "libc6-dev", "version": "2.39-0ubuntu8", "sha256": sd("libc6-dev"), "upstream_url": "https://example.invalid/dist-a/libc6-dev.deb",
                                "upstream_checksum_reference": "dist-a Release.gpg / SHA256SUMS"},
                               {"name": "binutils", "version": "2.42-4ubuntu2", "sha256": sd("binutils"), "upstream_url": "https://example.invalid/dist-a/binutils.deb",
                                "upstream_checksum_reference": "dist-a Release.gpg / SHA256SUMS"}],
                "assembly": {"tool": "gov-env-assemble 1", "recipe_digest": sd("recipe")}, "environment_tree_digest": sd("environment-tree-A")}
env_repro = {"_type": "https://agentic-engineering-os/statement/environment-reproduction/v1", "trust_root_id": LIN, "environment_id": ENV_A,
             "environment_tree_digest": sd("environment-tree-A"), "target": "x86_64-unknown-linux-gnu", "supplier_class": "A", "reproduced_at": "2026-09-14T00:00:00Z"}
reg_revocation = {"_type": "https://agentic-engineering-os/statement/registration-revocation/v1", "trust_root_id": LIN, "revokes": [sd("forged-reproduction")],
                  "reason": "forged_reproduction", "evidence": "custodians' first-hand reproductions yield the registered digest", "issued_at": "2026-09-14T00:00:00Z"}

reg = copy.deepcopy(r5["release-registration.payload.example.json"])
reg["_type"] = "https://agentic-engineering-os/statement/release-registration/v2"
reg["source"] = dict(SRC)
reg["environments"] = [{"target": "x86_64-unknown-linux-gnu", "environment_id": ENV_A, "environment_tree_digest": sd("environment-tree-A"), "supplier_class": "A",
                        "environment_reproductions": [sd("env-repro-1"), sd("env-repro-2")]}]

inputs = copy.deepcopy(r5["input-manifest.example.json"])
inputs["schema"] = "governance-os.input-manifest/2"
inputs.pop("build_image_digest", None)
inputs["environments"] = [{"target": "x86_64-unknown-linux-gnu", "environment_id": ENV_A, "environment_tree_digest": sd("environment-tree-A"), "supplier_class": "A"}]

brep = copy.deepcopy(r5["binary-reproduction.payload.example.json"])
brep["_type"] = "https://agentic-engineering-os/statement/binary-reproduction/v2"
brep["source"] = dict(SRC)
brep.pop("environment_digest", None)
brep["environment_id"] = ENV_A

adm = copy.deepcopy(r5["admission-record.example.json"])
adm["schema"] = "governance-os.admission-record/2"
adm.pop("state_fingerprint", None)
adm["first_contact_code"] = code

va = {"_type": "https://agentic-engineering-os/statement/verification-attestation/v4", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LIN,
      "issued_at": "2026-09-14T00:00:00Z", "candidate_statement_digest": sd("candidate-4.1.6"), "release_id": "agentic-engineering-os@4.1.6#0123456789abcdef", "version": "4.1.6",
      "verdict": "ACCEPTED", "report": {"path": "release/verification/4.1.6/report.md", "digest": sd("report")},
      "verdict_record": {"path": "release/verification/4.1.6/verdict.yaml", "digest": sd("verdict")}, "harnesses": [], "findings": {"critical": 0, "high": 0, "medium": 0, "low": 0},
      "verifier_label": "independent verifier (example)", "source": dict(SRC), "inputs_manifest_digest": sd("input-manifest-v2"), "kernel_tree_digest": sd("kernel-tree-4.1.6")}

instances = {
    "first-contact-manifest.example.json": ("first-contact-manifest.schema.json", fcm),
    "environment-manifest.example.json": ("environment-manifest.schema.json", env_manifest),
    "environment-reproduction.payload.example.json": ("environment-reproduction.schema.json", env_repro),
    "registration-revocation.payload.example.json": ("registration-revocation.schema.json", reg_revocation),
    "release-registration.payload.example.json": ("release-registration.schema.json", reg),
    "input-manifest.example.json": ("input-manifest.schema.json", inputs),
    "binary-reproduction.payload.example.json": ("binary-reproduction.schema.json", brep),
    "admission-record.example.json": ("admission-record.schema.json", adm),
    "verification-attestation.payload.example.json": ("verification-attestation.schema.json", va),
}
out = {"generator": "make_rev6.py (AR-0015)", "schemas_valid": {}, "instances": {}, "refused_revision5_shapes": {}, "first_contact_code_of_example_manifest": code}
for p in sorted(glob.glob(os.path.join(SCHEMAS, "*.schema.json"))):
    try:
        jsonschema.Draft202012Validator.check_schema(json.load(open(p)))
        out["schemas_valid"][os.path.basename(p)] = True
    except jsonschema.SchemaError as e:
        out["schemas_valid"][os.path.basename(p)] = "invalid: %s" % e.message
for name, (sch, inst) in instances.items():
    write(name, inst)
    out["instances"][name] = validate(sch, inst)

tr = schema("trust-root.schema.json")
root_purpose = jsonschema.Draft202012Validator({"$defs": tr["$defs"], **tr["properties"]["purposes"]["properties"]["root"]})
purpose_props = sorted((tr["$defs"]["purpose"].get("properties") or {}).keys())
sample_purpose = {k: v for k, v in {"key_ids": ["ed25519:" + "a" * 64, "ed25519:" + "b" * 64], "threshold": 1}.items() if k in purpose_props or not purpose_props}
bad_root = dict(sample_purpose, threshold=1)
good_root = dict(sample_purpose, threshold=2)
refused = {
    "input-manifest v1 shape (build_image_digest, no environments)": validate("input-manifest.schema.json", r5["input-manifest.example.json"]),
    "admission-record v1 shape (state_fingerprint)": validate("admission-record.schema.json", r5["admission-record.example.json"]),
    "binary-reproduction v1 shape (environment_digest)": validate("binary-reproduction.schema.json", r5["binary-reproduction.payload.example.json"]),
    "release-registration v1 shape (no environments, no git_tree)": validate("release-registration.schema.json", r5["release-registration.payload.example.json"]),
    "verification-attestation without kernel_tree_digest": validate("verification-attestation.schema.json", {k: v for k, v in va.items() if k != "kernel_tree_digest"}),
    "registration-revocation with no revoked statement": validate("registration-revocation.schema.json", dict(reg_revocation, revokes=[])),
    "first-contact manifest with an extra selector field": validate("first-contact-manifest.schema.json", dict(fcm, channel_quorum=1)),
}
refused["root purpose with threshold 1 (KS-14)"] = {"valid": not list(root_purpose.iter_errors(bad_root)), "errors": sorted(e.message for e in root_purpose.iter_errors(bad_root))[:3],
                                                    "control_threshold_2_valid": not list(root_purpose.iter_errors(good_root))}
out["refused_revision5_shapes"] = refused
out["verdicts"] = {
    "every_schema_valid": all(v is True for v in out["schemas_valid"].values()),
    "every_instance_valid": all(v["valid"] for v in out["instances"].values()),
    "every_withdrawn_shape_refused": all(not v["valid"] for v in refused.values()),
    "root_threshold_2_control_valid": refused["root purpose with threshold 1 (KS-14)"]["control_threshold_2_valid"],
}
write("validation.json", out)
print(json.dumps(out["verdicts"]))
