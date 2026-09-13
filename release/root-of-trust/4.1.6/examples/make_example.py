#!/usr/bin/env python3
"""RoT-1 revision 2 — ILLUSTRATIVE statement set and reference-model checks.

Builds a complete TEST-lineage statement set from the immutable 4.1.5 payload with EPHEMERAL keys (one per purpose,
generated in memory, never written): trust root v1, Trust Policy v1 (floors derived from the kernel's constitutional
files), candidate and promoted final release statements, verification attestation, certification, revocation, Trust
State 1-3, historical-identity registry (4.1.2-4.1.5), artifact, retrieval profile, lock 2.0.0 and FORMAT.

It then validates every payload and envelope against ../schemas and runs a small REFERENCE MODEL of the verification
rules (05 SV-1..SV-10), purpose separation (05 KS), admissibility and certification views (17 S4-S6), and the floor join
(19 §5). The model is illustrative, not the implementation. Nothing here is a real release, attestation or
certification: trust_profile is "test" and the verifier report is a placeholder.

Usage: python3 make_example.py <repo-root>
Writes next to this script: rev2/*.json, release-statement.payload.example.json, release.dsse.example.json.
"""
import base64, copy, hashlib, json, os, sys
import jsonschema, yaml
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", ".."))
SCHEMAS = os.path.join(HERE, "..", "schemas")
OUT = os.path.join(HERE, "rev2")
os.makedirs(OUT, exist_ok=True)
PT = "application/vnd.agentic-engineering-os."
ST = "https://agentic-engineering-os/statement/"
TS = "2026-09-13T00:00:00Z"
SENTINEL = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-verify-this-project"
VER = "4.1.5"
REL = os.path.join(ROOT, "release", "releases", VER)


def jcs(o):
    # GOV-JCS-1 for this data: ASCII member names, integers/strings/bools/null only -> sorted compact JSON equals RFC 8785
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dg(b):
    return "sha256:" + sha(b)


# payloadType suffix -> (purpose, _type suffix, schema file, accepted sources)
TABLE = {
    "trust-root.v2+json": ("root", "trust-root/v2", "trust-root.schema.json", "any"),
    "trust-policy.v1+json": ("trust-policy", "trust-policy/v1", "trust-policy-statement.schema.json", "any"),
    "trust-state.v1+json": ("trust-state", "trust-state/v1", "trust-state-statement.schema.json", "any"),
    "release-final.v1+json": ("release-final", "release/v2", "release-statement.schema.json", "any"),
    "release-candidate.v1+json": ("release-candidate", "release/v2", "release-statement.schema.json", "any"),
    "artifact-final.v1+json": ("release-final", "artifact/v2", "artifact-statement.schema.json", "any"),
    "artifact-candidate.v1+json": ("release-candidate", "artifact/v2", "artifact-statement.schema.json", "any"),
    "verification-attestation.v1+json": ("verification-attestation", "verification-attestation/v1", "verification-attestation.schema.json", "any"),
    "certification-status.v1+json": ("certification-status", "certification/v2", "certification-statement.schema.json", "any"),
    "revocation.v2+json": ("revocation", "revocation/v2", "revocation-statement.schema.json", "any"),
    "historical-identity.v1+json": ("release-final", "historical-identity/v1", "legacy-identity-statement.schema.json", "compiled"),
    "retrieval-profile.v1+json": ("retrieval-profile", "retrieval-profile/v1", "profile-statement.schema.json", "any"),
}
_VALIDATORS = {}


def validator(name):
    if name not in _VALIDATORS:
        s = json.load(open(os.path.join(SCHEMAS, name)))
        jsonschema.Draft202012Validator.check_schema(s)
        _VALIDATORS[name] = jsonschema.Draft202012Validator(s)
    return _VALIDATORS[name]


def errors(name, instance):
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator(name).iter_errors(instance)]


class Key:
    def __init__(self, label):
        self.sk = Ed25519PrivateKey.generate()  # ephemeral; never persisted
        self.pk = self.sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.id = "ed25519:" + sha(self.pk)
        self.label = label


def pae(ptype, body):
    return b"DSSEv1 %d %s %d %s" % (len(ptype), ptype.encode(), len(body), body)


def envelope(ptype_suffix, stmt, keys):
    t = PT + ptype_suffix
    body = jcs(stmt)
    return {"payloadType": t, "payload": base64.b64encode(body).decode(),
            "signatures": [{"keyid": k.id, "sig": base64.b64encode(k.sk.sign(pae(t, body))).decode()} for k in keys]}


def body_of(env):
    return base64.b64decode(env["payload"])


def digest_of(env):
    return dg(body_of(env))


# ------------------------------------------------------------------ reference model: 05 KS and SV rules
KS_DISJOINT = [("release-final", "certification-status"), ("release-final", "verification-attestation"),
               ("certification-status", "verification-attestation"), ("release-candidate", "certification-status"),
               ("release-candidate", "verification-attestation")]


def check_root(root):
    keys, purposes = root["keys"], root["purposes"]
    pubs = []
    for kid, rec in keys.items():
        if "ed25519:" + sha(base64.b64decode(rec["public_key"])) != kid:
            return "TRUST_ROOT_INVALID"
        pubs.append(rec["public_key"])
    if len(pubs) != len(set(pubs)):
        return "TRUST_ROOT_INVALID"
    root_keys = set(purposes["root"]["key_ids"])
    for p, spec in purposes.items():
        if spec["threshold"] > len(spec["key_ids"]):
            return "TRUST_ROOT_INVALID"
        if p not in ("root", "trust-policy") and root_keys & set(spec["key_ids"]):
            return "PURPOSE_SEPARATION_VIOLATION"  # KS-1
    tp = purposes["trust-policy"]
    if not set(tp["key_ids"]) <= root_keys or tp["threshold"] < purposes["root"]["threshold"]:
        return "PURPOSE_SEPARATION_VIOLATION"  # KS-2
    for a, b in KS_DISJOINT:  # KS-3..KS-6
        if set(purposes[a]["key_ids"]) & set(purposes[b]["key_ids"]):
            return "PURPOSE_SEPARATION_VIOLATION"
    return None


def verify(env, root, lineage, source="bundle", profile="test"):
    if errors("dsse-envelope.schema.json", env):
        return "STATEMENT_MALFORMED"
    suffix = env["payloadType"][len(PT):]
    if suffix not in TABLE:
        return "STATEMENT_TYPE_UNKNOWN"
    purpose, type_suffix, schema_name, accepted = TABLE[suffix]
    if accepted == "compiled" and source != "compiled":
        return "STATEMENT_SOURCE_NOT_PERMITTED"
    body = body_of(env)
    stmt = json.loads(body)
    if jcs(stmt) != body:
        return "STATEMENT_MALFORMED"
    bad_root = check_root(root)
    if bad_root:
        return bad_root
    revoked = {r["key_id"] for r in root["revoked_keys"]}
    valid = set()
    for s in env["signatures"]:
        rec = root["keys"].get(s["keyid"])
        if rec is None:
            return "SIGNER_UNKNOWN"
        if s["keyid"] not in root["purposes"][purpose]["key_ids"]:
            return "PURPOSE_NOT_GRANTED"
        if s["keyid"] in revoked:
            return "SIGNER_REVOKED"
        try:
            Ed25519PublicKey.from_public_bytes(base64.b64decode(rec["public_key"])).verify(
                base64.b64decode(s["sig"]), pae(env["payloadType"], body))
        except InvalidSignature:
            return "SIGNATURE_INVALID"
        valid.add(s["keyid"])
    if len(valid) < root["purposes"][purpose]["threshold"]:
        return "THRESHOLD_NOT_MET"
    if errors(schema_name, stmt):
        return "STATEMENT_MALFORMED"
    if stmt.get("_type") != ST + type_suffix:
        return "STATEMENT_TYPE_MISMATCH"
    if suffix.startswith("release-"):
        if stmt["signing"]["purpose"] != purpose or stmt["release"]["stage"] != suffix.split("-")[1].split(".")[0]:
            return "STATEMENT_TYPE_MISMATCH"
    if suffix.startswith("artifact-") and stmt["stage"] != suffix.split("-")[1].split(".")[0]:
        return "STATEMENT_TYPE_MISMATCH"
    if stmt.get("trust_profile") != profile:
        return "TRUST_PROFILE_MISMATCH"
    if suffix != "trust-root.v2+json" and stmt.get("trust_root_id") != lineage:
        return "STATEMENT_LINEAGE_MISMATCH"
    return "OK"


# ------------------------------------------------------------------ reference model: 17 S4-S6
def admissible(T, T_digest, lowers, cert_seq):
    """T admissible over every lower (statement, digest) in `lowers` (17 S4)."""
    for L, L_digest in lowers:
        if L["sequence"] >= T["sequence"]:
            continue
        if not set(T["revocations"]) >= set(L["revocations"]):
            return False, "revocations"
        tmap = {c["release_statement_digest"]: cert_seq[c["certification_statement_digest"]] for c in T["certifications"]}
        for c in L["certifications"]:
            r = c["release_statement_digest"]
            if r not in tmap or tmap[r] < cert_seq[c["certification_statement_digest"]]:
                return False, "certifications"
        if not set(T["attestations"]) >= set(L["attestations"]):
            return False, "attestations"
        if T["references"]["root_version"] < L["references"]["root_version"]:
            return False, "root_version"
        if T["references"]["trust_policy"]["policy_version"] < L["references"]["trust_policy"]["policy_version"]:
            return False, "policy_version"
        if L["sequence"] == T["sequence"] - 1 and T["previous_state_digest"] != L_digest:
            return False, "chain"
    return True, None


def certification_view(final_digest, tss, certs, atts, candidate_digest, other_references=()):
    """17 S4-S7 and §6 for one final digest. tss: list of (stmt, digest); certs/atts: {digest: stmt}."""
    cert_seq = {d: c["certification_sequence"] for d, c in certs.items()}
    ordered = sorted(tss, key=lambda x: x[0]["sequence"])
    effective = None
    for T, Td in ordered:
        ok, why = admissible(T, Td, [x for x in ordered if x[0]["sequence"] < T["sequence"]], cert_seq)
        if not ok:
            return {"view": "TRUST_STATE_REGRESSION", "at_sequence": T["sequence"], "violation": why}
        effective = (T, Td)
    mine = {d: c for d, c in certs.items() if c["release_statement_digest"] == final_digest}
    top = max(mine.items(), key=lambda kv: kv[1]["certification_sequence"], default=None)
    required = max([T["sequence"] for T, _ in ordered] + [c["issued_under"]["trust_state_sequence"] for c in certs.values()] + list(other_references))
    state = "STALE" if effective is None or effective[0]["sequence"] < required else f"CURRENT_KNOWN({effective[0]['sequence']})"
    if top and top[1]["status"] in ("REJECTED", "WITHDRAWN"):
        return {"view": top[1]["status"], "trust_state": state}
    if not top:
        return {"view": "NOT_CERTIFIED", "trust_state": state}
    referenced = effective and any(c["certification_statement_digest"] == top[0] for c in effective[0]["certifications"])
    if not referenced:
        return {"view": "CERTIFICATION_UNREFERENCED", "trust_state": state}
    att = atts.get(top[1]["verification_attestation_digest"])
    if not att or att["verdict"] != "ACCEPTED" or att["candidate_statement_digest"] != candidate_digest:
        return {"view": "NOT_CERTIFIED", "trust_state": state}
    return {"view": f"CERTIFIED_AS_OF({effective[0]['sequence']})", "trust_state": state,
            "relaxes_gate_under_mode_A": False}


# ------------------------------------------------------------------ reference model: 19 §5 floor join
def level(v):
    return int(v[1:]) if isinstance(v, str) and v.startswith("L") else -1


def tree(kdir):
    out = {}
    for dp, dns, fns in os.walk(kdir):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            if os.path.islink(p) or not os.path.isfile(p):
                raise SystemExit(f"RELEASE_TREE_INVALID: {p}")
            rel = os.path.relpath(p, kdir).replace(os.sep, "/")
            if rel == "KERNEL_MANIFEST.json":
                continue
            out[rel] = sha(open(p, "rb").read())
    return dict(sorted(out.items()))


def y(kdir, rel):
    return yaml.safe_load(open(os.path.join(kdir, rel)))


checks = {}
kdir = os.path.join(REL, "kernel")
hexmap = tree(kdir)
tree_hex = sha(jcs(hexmap))
meta = y(kdir, "KERNEL.yaml")
published = json.load(open(os.path.join(REL, "manifest.json")))
km = json.load(open(os.path.join(kdir, "KERNEL_MANIFEST.json")))
manifest_hex = sha(jcs({"framework": meta["framework"], "version": str(meta["version"]), "files": hexmap, "payload_hash": tree_hex}))
checks["continuity"] = {
    "tree_digest_equals_published_release_hash": tree_hex == published["release_hash"],
    "manifest_digest_equals_KERNEL_MANIFEST_hash": manifest_hex == sha(jcs({k: km[k] for k in ["framework", "version", "files", "payload_hash"]})),
    "all_paths_ascii_tree_rule": all(__import__("re").fullmatch(r"[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*", p) for p in hexmap),
    "file_count": len(hexmap),
}

# ---- keys: one per purpose (root x3, threshold 2; trust-policy = root keys)
K = {p: Key(p) for p in ["release-final", "release-candidate", "verification-attestation", "certification-status", "revocation", "trust-state", "retrieval-profile"]}
R = [Key(f"root-{i}") for i in range(3)]
all_keys = R + list(K.values())
root = {
    "_type": ST + "trust-root/v2", "trust_profile": "test", "framework": "agentic-engineering-os", "version": 1,
    "lineage": {"trust_root_id": None},
    "keys": {k.id: {"alg": "ed25519", "public_key": base64.b64encode(k.pk).decode(), "label": k.label, "added_in_version": 1} for k in all_keys},
    "purposes": {"root": {"key_ids": [k.id for k in R], "threshold": 2},
                 "trust-policy": {"key_ids": [k.id for k in R], "threshold": 2},
                 **{p: {"key_ids": [K[p].id], "threshold": 1} for p in K}},
    "revoked_keys": [], "issued_at": TS,
}
root_env = envelope("trust-root.v2+json", root, R[:2])
LINEAGE = dg(body_of(root_env))

# ---- Trust Policy v1: floors derived from the constitutional files (19 §4)
auth, sec, hg, tool, prec = (y(kdir, f"policies/{n}.yaml") for n in ["AUTHORITY_POLICY", "SECURITY_POLICY", "HUMAN_GATE_POLICY", "TOOL_POLICY", "POLICY_PRECEDENCE"])
inv = y(kdir, "constitution/HARD_INVARIANTS.yaml")
floors = [{"key": f"AUTHORITY_POLICY.authority_levels_required.{op}", "op": "level_at_least", "value": lv} for op, lv in auth["authority_levels_required"].items()]
floors += [{"key": "SECURITY_POLICY.never_index_classes", "op": "set_superset", "value": sec["never_index_classes"]},
           {"key": "SECURITY_POLICY.never_export_classes", "op": "set_superset", "value": sec["never_export_classes"]},
           {"key": "SECURITY_POLICY.on_secret_in_export_payload", "op": "equals", "value": sec["on_secret_in_export_payload"]},
           {"key": "SECURITY_POLICY.agent_read_default_for_secret_class", "op": "equals", "value": sec["agent_read_default_for_secret_class"]},
           {"key": "HUMAN_GATE_POLICY.raise_for", "op": "set_superset", "value": hg["raise_for"]},
           {"key": "HUMAN_GATE_POLICY.must_be_presented_in_chat", "op": "bool_required", "value": hg["must_be_presented_in_chat"]},
           {"key": "TOOL_POLICY.plugins.min_authority", "op": "level_at_least", "value": tool["plugins"]["min_authority"]},
           {"key": "TOOL_POLICY.plugins.elevated_permission_classes", "op": "set_superset", "value": tool["plugins"]["elevated_permission_classes"]},
           {"key": "TOOL_POLICY.plugins.registration_binds", "op": "set_superset", "value": tool["plugins"]["registration_binds"]},
           {"key": "TOOL_POLICY.plugins.refuse_on_pin_drift", "op": "bool_required", "value": tool["plugins"]["refuse_on_pin_drift"]},
           {"key": "TOOL_POLICY.plugins.require_valid_descriptor", "op": "bool_required", "value": tool["plugins"]["require_valid_descriptor"]},
           {"key": "POLICY_PRECEDENCE.default_mode", "op": "equals", "value": prec["default_mode"]},
           {"key": "HARD_INVARIANTS.invariants[*].id", "op": "set_superset", "value": sorted(str(i["id"]) for i in inv["invariants"])}]
floors += [{"key": f"POLICY_PRECEDENCE.rules[key={r['key']}]", "op": "rule_mode_at_least", "value": r["mode"]} for r in prec["rules"]]
install_ops = ["install_kernel", "update_apply", "rollback_apply", "recover", "override_kernel_integrity", "trust_refresh", "trust_confirm_root", "allow_unsigned_development", "install_evaluation_candidate"]
levels = auth["authority_levels_required"]
tps = {"_type": ST + "trust-policy/v1", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LINEAGE, "issued_at": TS,
       "policy_version": 1, "supersedes_policy_digest": None, "floor_schema_version": 1, "floors": floors,
       "eligibility": {"min_release_sequence": 5, "min_binary_version": "4.1.6", "production_stage": "final", "historical_releases": "never_eligible", "evaluation_candidates": "flag_and_gate"},
       "install_authority": {op: levels.get(op, "L4") for op in install_ops},
       "gating": {"mode": "always_gate", "refuse_known_rejected": True, "refuse_known_withdrawn": True},
       "sensitivity_order": sec["sensitivity_classes"], "lowers": [], "unrevokes": []}
tps_env = envelope("trust-policy.v1+json", tps, R[:2])
tps_d = digest_of(tps_env)

# ---- release candidate and promoted final
components = {"KERNEL.yaml": "sha256:" + hexmap["KERNEL.yaml"]}
for d in meta["payload_dirs"]:
    sub = {p: h for p, h in hexmap.items() if p.startswith(d + "/")}
    if sub:
        components[d] = "sha256:" + sha(jcs(sub))
migrations = []
for p in sorted(x for x in hexmap if x.startswith("migrations/") and x.endswith(".yaml")):
    m = y(kdir, p)
    migrations.append({"id": m["id"], "from_version": str(m["from_version"]), "to_version": str(m["to_version"]), "path": p,
                       "digest": "sha256:" + hexmap[p], "breaking": bool(m.get("breaking", False)), "human_gate": str(m.get("human_gate", "none"))})
from_versions = [m["from_version"] for m in migrations]
checks["migration_chain_unique"] = len(from_versions) == len(set(from_versions))


def release_statement(stage, sequence, promoted):
    return {
        "_type": ST + "release/v2", "trust_profile": "test", "trust_root_id": LINEAGE, "framework": meta["framework"], "manifest_version": 2,
        "release": {"version": VER, "release_id": f"{meta['framework']}@{VER}#{tree_hex[:16]}", "sequence": sequence, "stage": stage,
                    "promoted_from_candidate": promoted, "release_commit": published["release_commit"], "release_tag": f"v{VER}-rc1", "released_at": "2026-09-12T19:12:51Z"},
        "signing": {"purpose": f"release-{stage}", "algorithm": "ed25519"},
        "trust_references": {"root_version": 1, "trust_policy_version": 1, "trust_state_sequence": 1},
        "compatibility": {"cli": {"min": str(meta["cli_version"]), "max_exclusive": "5.0.0"}, "runtime": {"min": str(meta["runtime_version"]), "max_exclusive": "5.0.0"},
                          "kernel_contract_version": int(meta["kernel_contract_version"]), "floor_schema_version": 1,
                          "supported_from_versions": [str(v) for v in meta["supported_from_versions"]], "index_version": f"{VER}-idx3",
                          "schema_versions": {k: str(v) for k, v in meta["schema_versions"].items()}},
        "kernel": {"tree_rules": "gov-tree-v2", "file_count": len(hexmap), "files": {p: "sha256:" + h for p, h in hexmap.items()},
                   "tree_digest": "sha256:" + tree_hex, "manifest_digest": "sha256:" + manifest_hex},
        "components": components,
        "security_critical": [p for p in ["constitution/HARD_INVARIANTS.yaml", "policies/AUTHORITY_POLICY.yaml", "policies/HUMAN_GATE_POLICY.yaml", "policies/POLICY_PRECEDENCE.yaml", "policies/SECURITY_POLICY.yaml", "policies/TOOL_POLICY.yaml", "roles/ROLES.yaml"] if p in hexmap],
        "migrations": migrations,
        "update_impact": {"breaking_changes": [str(x) for x in published.get("breaking_changes", [])], "human_gates": [str(x) for x in published.get("human_gates", [])], "required_index_rebuilds": [str(x) for x in published.get("required_index_rebuilds", [])]},
        "documents": {n: dg(open(os.path.join(REL, n), "rb").read()) for n in ["RELEASE_NOTES.md", "ROLLBACK.md"] if os.path.exists(os.path.join(REL, n))},
        "provenance": {"release_branch": f"release/{VER}-rc1", "builder": f"gov release build {VER} (illustrative)", "reproduced_from_commit": published["release_commit"], "source_tree": "git archive of release_commit: framework, migrations, tools"},
    }


cand = release_statement("candidate", 5, None)
cand_env = envelope("release-candidate.v1+json", cand, [K["release-candidate"]])
cand_d = digest_of(cand_env)
final = release_statement("final", 6, cand_d)
final_env = envelope("release-final.v1+json", final, [K["release-final"]])
final_d = digest_of(final_env)
placeholder = dg(b"illustrative placeholder - not a real verification report")
att = {"_type": ST + "verification-attestation/v1", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LINEAGE, "issued_at": TS,
       "candidate_statement_digest": cand_d, "release_id": cand["release"]["release_id"], "version": VER, "verdict": "ACCEPTED",
       "report": {"path": "illustrative/INDEPENDENT_VERIFICATION_REPORT.md", "digest": placeholder}, "verdict_record": {"path": "illustrative/VERDICT.md", "digest": placeholder},
       "harnesses": [{"path": "illustrative/harness.py", "digest": placeholder}], "findings": {"critical": 0, "high": 0, "medium": 0, "low": 0},
       "verifier_label": "illustrative test verifier (not a real verdict)"}
att_env = envelope("verification-attestation.v1+json", att, [K["verification-attestation"]])
att_d = digest_of(att_env)
cert = {"_type": ST + "certification/v2", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LINEAGE, "issued_at": TS,
        "release_id": final["release"]["release_id"], "version": VER, "release_statement_digest": final_d, "candidate_statement_digest": cand_d,
        "status": "CERTIFIED", "certification_sequence": 1, "verification_attestation_digest": att_d, "issued_under": {"trust_state_sequence": 1}, "supersedes": None}
cert_env = envelope("certification-status.v1+json", cert, [K["certification-status"]])
cert_d = digest_of(cert_env)
rev = {"_type": ST + "revocation/v2", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LINEAGE, "issued_at": TS, "revocation_sequence": 1,
       "targets": [{"kind": "release_candidate", "statement_digest": dg(b"illustrative earlier rejected candidate"), "release_id": None, "effect": "refuse_install", "reason": "illustrative: rejected candidate"}]}
rev_env = envelope("revocation.v2+json", rev, [K["revocation"]])
rev_d = digest_of(rev_env)


def tss(seq, prev, revocations, certifications, attestations):
    return {"_type": ST + "trust-state/v1", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LINEAGE, "issued_at": TS,
            "sequence": seq, "previous_state_digest": prev, "references": {"root_version": 1, "trust_policy": {"policy_version": 1, "statement_digest": tps_d}},
            "revocations": revocations, "certifications": certifications, "attestations": attestations, "expires_at": None}


tss1 = tss(1, None, [], [], [])
tss1_env = envelope("trust-state.v1+json", tss1, [K["trust-state"]])
tss1_d = digest_of(tss1_env)
tss2 = tss(2, tss1_d, [rev_d], [{"release_statement_digest": final_d, "certification_statement_digest": cert_d}], [att_d])
tss2_env = envelope("trust-state.v1+json", tss2, [K["trust-state"]])
tss2_d = digest_of(tss2_env)
cert_w = dict(cert, status="WITHDRAWN", certification_sequence=2, issued_under={"trust_state_sequence": 2}, supersedes=cert_d, verification_attestation_digest=att_d)
cert_w_env = envelope("certification-status.v1+json", cert_w, [K["certification-status"]])
cert_w_d = digest_of(cert_w_env)
tss3 = tss(3, tss2_d, [rev_d], [{"release_statement_digest": final_d, "certification_statement_digest": cert_w_d}], [att_d])
tss3_env = envelope("trust-state.v1+json", tss3, [K["trust-state"]])
tss3_bad = tss(3, tss2_d, [], [{"release_statement_digest": final_d, "certification_statement_digest": cert_d}], [att_d])  # omits the revocation

# ---- historical identity (4.1.2-4.1.5), compiled source only
hist_rel = []
for v in ["4.1.2", "4.1.3", "4.1.4", "4.1.5"]:
    rd = os.path.join(ROOT, "release", "releases", v)
    hm = tree(os.path.join(rd, "kernel"))
    th = sha(jcs(hm))
    mm = json.load(open(os.path.join(rd, "manifest.json")))
    vdir = os.path.join(ROOT, "release", "verification", v)
    reports = sorted(f for f in os.listdir(vdir) if f.endswith(".md") and "REPORT" in f) if os.path.isdir(vdir) else []
    rp = os.path.join("release", "verification", v, reports[0]) if reports else "release/verification/(none)"
    rdg = dg(open(os.path.join(ROOT, rp), "rb").read()) if reports else placeholder
    mh = sha(jcs({"framework": "agentic-engineering-os", "version": v, "files": hm, "payload_hash": th}))
    hist_rel.append({"version": v, "release_id": f"agentic-engineering-os@{v}#{th[:16]}", "release_commit": mm["release_commit"], "tree_digest": "sha256:" + th,
                     "manifest_digest": "sha256:" + mh, "historical_status": "REJECTED", "verifier_report": {"path": rp, "digest": rdg}})
    checks.setdefault("historical_tree_digest_equals_published", {})[v] = th == mm["release_hash"]
hist = {"_type": ST + "historical-identity/v1", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LINEAGE, "issued_at": TS,
        "accepted_source": "compiled-into-binary", "eligibility": "never", "releases": hist_rel}
hist_env = envelope("historical-identity.v1+json", hist, [K["release-final"]])

art = {"_type": ST + "artifact/v2", "trust_profile": "test", "framework": "agentic-engineering-os", "trust_root_id": LINEAGE, "issued_at": TS, "stage": "candidate",
       "release_id": cand["release"]["release_id"], "release_statement_digest": cand_d,
       "artifacts": [{"name": "gov", "target": "x86_64-unknown-linux-gnu", "digest": dg(b"illustrative binary"), "size": 1, "trust_profile": "test"}],
       "build": {"toolchain": "illustrative", "reproducible": True}}
art_env = envelope("artifact-candidate.v1+json", art, [K["release-candidate"]])
prof = {"_type": ST + "retrieval-profile/v1", "trust_profile": "test", "trust_root_id": LINEAGE, "issued_at": TS, "profile_id": "retrieval-reference/sentence-embedding",
        "profile_version": "1.0.0", "capability": "embed", "compatibility": {"framework_min": "4.1.6", "framework_max_exclusive": "5.0.0", "capability_protocol": "gov-capability/1"},
        "plugin": {"descriptor": {"path": "plugins/embed.yaml", "digest": placeholder, "size": 1}, "implementation_files": [{"path": "plugins/embed.py", "digest": placeholder, "size": 1}]},
        "runtime": {"kind": "python", "requires": ">=3.10", "lock": {"path": "runtime/requirements.lock", "digest": placeholder, "size": 1}, "packages": [{"name": "illustrative", "version": "1.0", "digests": [placeholder]}]},
        "model": {"id": "illustrative/model", "source_kind": "vendored", "revision": "0" * 40, "licence": "Apache-2.0", "dimensions": 384, "normalised": True, "files": [{"path": "model/weights.bin", "digest": placeholder, "size": 1}]},
        "evidence": {"benchmark_record_digest": placeholder, "heldout_set_digest": placeholder, "metrics": {"recall_at_10": "0.90"}}, "offline": True}
prof_env = envelope("retrieval-profile.v1+json", prof, [K["retrieval-profile"]])
lock = {"lock_schema_version": "2.0.0", "trust_format": "rot-1", "kernel_manifest_hash": SENTINEL, "release_hash": SENTINEL, "framework": "agentic-engineering-os", "version": VER,
        "release_id": final["release"]["release_id"], "release_sequence": 6, "release_stage": "final", "release_commit": published["release_commit"],
        "kernel": {"tree_digest": "sha256:" + tree_hex, "manifest_digest": "sha256:" + manifest_hex}, "release_statement_digest": final_d,
        "signer": {"purpose": "release-final", "algorithm": "ed25519", "key_ids": [K["release-final"].id]},
        "trust_root": {"profile": "test", "id": LINEAGE, "version_min": 1, "confirmation": "pin"},
        "trust_references": {"trust_policy_version_min": 1, "trust_state_sequence_min": 2}, "project_trust_id": "0123456789abcdef0123456789abcdef",
        "verdict_at_install": {"authenticity": "TEST", "eligibility": "ELIGIBLE", "certification_view": "CERTIFIED_AS_OF(2)", "trust_state": "CURRENT_KNOWN(2)"},
        "source": f"bundle:agentic-engineering-os@{VER}", "source_reference": f"bundle:agentic-engineering-os-{VER}.tar#{final_d}", "installed_at": TS, "installed_at_commit": "0" * 40,
        "installed_by": {"gov_version": "4.1.6", "trust_profile": "test", "session": "S-illustrative", "role": "orchestrator", "authority_level": "L4"},
        "install_evidence": {"transaction_id": "TX-illustrative", "ledger_entry": "spec/reports/framework-updates.jsonl#1", "gate": "HG-0001"},
        "informational": {}, "cli_version": "4.1.6", "schema_versions": {"framework-lock": "2.0.0", "release-statement": "2.0.0"}}
fmt = {"minimum_reader": "4.1.6", "trust_format": "rot-1"}

# ---- schema validation of every artefact
artefacts = {"trust-root.v1": (root_env, root), "trust-policy.v1": (tps_env, tps), "release-candidate": (cand_env, cand), "release-final": (final_env, final),
             "verification-attestation": (att_env, att), "certification.1-CERTIFIED": (cert_env, cert), "certification.2-WITHDRAWN": (cert_w_env, cert_w),
             "revocation.1": (rev_env, rev), "trust-state.1": (tss1_env, tss1), "trust-state.2": (tss2_env, tss2), "trust-state.3": (tss3_env, tss3),
             "historical-identity": (hist_env, hist), "artifact-candidate": (art_env, art), "retrieval-profile": (prof_env, prof)}
schema_problems = {}
for name, (env, stmt) in artefacts.items():
    p = errors("dsse-envelope.schema.json", env) + errors(TABLE[env["payloadType"][len(PT):]][2], stmt)
    if p:
        schema_problems[name] = p[:5]
    json.dump(env, open(os.path.join(OUT, f"{name}.dsse.json"), "w"), indent=2)
for name, (schema_name, inst) in {"framework.lock": ("framework-lock-2.0.0.schema.json", lock), "FORMAT": ("trust-format.schema.json", fmt)}.items():
    p = errors(schema_name, inst)
    if p:
        schema_problems[name] = p[:5]
    json.dump(inst, open(os.path.join(OUT, f"{name}.example.json"), "w"), indent=2)
for f in sorted(os.listdir(SCHEMAS)):
    validator(f)  # meta-validates every schema
checks["schemas_meta_valid"] = sorted(os.listdir(SCHEMAS))
checks["schema_problems"] = schema_problems or "none"

# ---- reference-model checks
expect = {}
expect["every_statement_verifies_under_its_purpose"] = {n: verify(e, root, LINEAGE, source="compiled" if n == "historical-identity" else "bundle") for n, (e, _) in artefacts.items()}
tampered = copy.deepcopy(final_env)
b = body_of(tampered).replace(("sha256:" + hexmap["KERNEL.yaml"]).encode(), ("sha256:" + ("0" if hexmap["KERNEL.yaml"][0] != "0" else "1") + hexmap["KERNEL.yaml"][1:]).encode(), 1)
tampered["payload"] = base64.b64encode(b).decode()
bad_root = copy.deepcopy(root)
bad_root["purposes"]["release-final"]["key_ids"].append(K["certification-status"].id)
expect["negative"] = {
    "payload_altered__SIGNATURE_INVALID": verify(tampered, root, LINEAGE),
    "certification_key_signs_release_final__PURPOSE_NOT_GRANTED": verify(envelope("release-final.v1+json", final, [K["certification-status"]]), root, LINEAGE),
    "certification_key_signs_historical_identity__PURPOSE_NOT_GRANTED": verify(envelope("historical-identity.v1+json", hist, [K["certification-status"]]), root, LINEAGE, source="compiled"),
    "historical_identity_from_bundle__STATEMENT_SOURCE_NOT_PERMITTED": verify(hist_env, root, LINEAGE, source="bundle"),
    "release_key_signs_certification__PURPOSE_NOT_GRANTED": verify(envelope("certification-status.v1+json", cert, [K["release-final"]]), root, LINEAGE),
    "attestation_signed_by_release_key__PURPOSE_NOT_GRANTED": verify(envelope("verification-attestation.v1+json", att, [K["release-final"]]), root, LINEAGE),
    "root_grants_release_final_to_certification_key__PURPOSE_SEPARATION_VIOLATION": verify(final_env, bad_root, LINEAGE),
    "other_lineage__STATEMENT_LINEAGE_MISMATCH": verify(final_env, root, dg(b"another lineage")),
    "test_statement_on_production__TRUST_PROFILE_MISMATCH": verify(final_env, root, LINEAGE, profile="production"),
    "candidate_payload_under_final_type__STATEMENT_MALFORMED_or_TYPE_MISMATCH": verify(envelope("release-final.v1+json", cand, [K["release-final"]]), root, LINEAGE),
    "unknown_key__SIGNER_UNKNOWN": verify(envelope("release-final.v1+json", final, [Key("stranger")]), root, LINEAGE),
}
expect["promotion"] = {"final_promoted_from_candidate": final["release"]["promoted_from_candidate"] == cand_d,
                       "identical_tree_digest": final["kernel"]["tree_digest"] == cand["kernel"]["tree_digest"],
                       "attestation_binds_candidate": att["candidate_statement_digest"] == cand_d,
                       "certification_binds_attestation_and_final": cert["verification_attestation_digest"] == att_d and cert["release_statement_digest"] == final_d}
certs_all = {cert_d: cert, cert_w_d: cert_w}
atts = {att_d: att}
expect["certification_views"] = {
    "TSS1_only_certification_present__CERTIFICATION_UNREFERENCED": certification_view(final_d, [(tss1, tss1_d)], {cert_d: cert}, atts, cand_d),
    "TSS1_TSS2__CERTIFIED_AS_OF_2_no_relaxation": certification_view(final_d, [(tss1, tss1_d), (tss2, tss2_d)], {cert_d: cert}, atts, cand_d),
    "TSS1_3_with_WITHDRAWN__WITHDRAWN": certification_view(final_d, [(tss1, tss1_d), (tss2, tss2_d), (tss3, digest_of(tss3_env))], certs_all, atts, cand_d),
    "TSS3_withheld_WITHDRAWN_statement_known__WITHDRAWN_sticky": certification_view(final_d, [(tss1, tss1_d), (tss2, tss2_d)], certs_all, atts, cand_d),
    "TSS3_and_WITHDRAWN_withheld__CERTIFIED_AS_OF_2_residual_RS1": certification_view(final_d, [(tss1, tss1_d), (tss2, tss2_d)], {cert_d: cert}, atts, cand_d),
    "signed_reference_to_sequence_3_present__STALE": certification_view(final_d, [(tss1, tss1_d), (tss2, tss2_d)], {cert_d: cert}, atts, cand_d, other_references=[3]),
    "higher_TSS_omits_revocation__TRUST_STATE_REGRESSION": certification_view(final_d, [(tss1, tss1_d), (tss2, tss2_d), (tss3_bad, dg(jcs(tss3_bad)))], {cert_d: cert}, atts, cand_d),
}
# floor join on the genuine 4.1.2 kernel (review R1): keys the 4.1.2 kernel lacks take the floor
auth412 = y(os.path.join(ROOT, "release", "releases", "4.1.2", "kernel"), "policies/AUTHORITY_POLICY.yaml").get("authority_levels_required", {})
fl = {f["key"]: f["value"] for f in floors}
join = {}
for op in ["update_apply", "resume_control", "install_kernel", "answer_gate"]:
    fv = fl.get(f"AUTHORITY_POLICY.authority_levels_required.{op}")
    kv = auth412.get(op)
    join[op] = {"kernel_4_1_2": kv, "runtime_default_without_floor": kv or "L3", "trust_policy_floor": fv,
                "effective": max([v for v in [fv, kv] if v], key=level) if (fv or kv) else "L3"}
expect["floor_join_on_4_1_2_kernel"] = join
checks["reference_model"] = expect
checks["lineage_trust_root_id"] = LINEAGE
checks["statement_digests"] = {"candidate": cand_d, "final": final_d, "attestation": att_d, "certification": cert_d, "tss2": tss2_d}

open(os.path.join(HERE, "release-statement.payload.example.json"), "wb").write(jcs(final))
json.dump(final_env, open(os.path.join(HERE, "release.dsse.example.json"), "w"), indent=2)
json.dump(checks, open(os.path.join(OUT, "reference-model-checks.json"), "w"), indent=2)
print(json.dumps(checks, indent=2))
