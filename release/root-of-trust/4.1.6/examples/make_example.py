#!/usr/bin/env python3
"""Build an ILLUSTRATIVE release-statement payload from an existing immutable payload and check the RoT-1 continuity
claims of 07-RELEASE-ENVELOPE-SPEC.md section 5:
  kernel.tree_digest     == published manifest.json release_hash       (4.1.x payload_hash definition)
  kernel.manifest_digest == kernel::manifest_hash over KERNEL_MANIFEST.json
Then validates the payload against schemas/release-statement.schema.json and, when the `cryptography` package is
available, wraps it in a DSSE envelope signed with an EPHEMERAL test key (never written to disk) and verifies it.

Usage: python3 make_example.py <repo-root> [release-version]   (default 4.1.5). Writes next to this script.
Nothing here is a real release statement; trust_profile is "test".
"""
import base64, hashlib, json, os, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", ".."))
VER = sys.argv[2] if len(sys.argv) > 2 else "4.1.5"
REL = os.path.join(ROOT, "release", "releases", VER)
PT = "application/vnd.agentic-engineering-os.release-statement.v1+json"


def jcs(o):
    # GOV-JCS-1 for this example: ASCII keys, integers/strings/bools/null only -> sorted compact JSON equals RFC 8785
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


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


kdir = os.path.join(REL, "kernel")
hexmap = tree(kdir)
tree_hex = sha(jcs(hexmap))
meta = yaml.safe_load(open(os.path.join(kdir, "KERNEL.yaml")))
manifest_hex = sha(jcs({"framework": meta["framework"], "version": meta["version"], "files": hexmap, "payload_hash": tree_hex}))
published = json.load(open(os.path.join(REL, "manifest.json")))
km = json.load(open(os.path.join(kdir, "KERNEL_MANIFEST.json")))
km_hash = sha(jcs({k: km[k] for k in ["framework", "version", "files", "payload_hash"]}))

components = {"KERNEL.yaml": "sha256:" + hexmap["KERNEL.yaml"]}
for d in meta["payload_dirs"]:
    sub = {p: h for p, h in hexmap.items() if p.startswith(d + "/")}
    if sub:
        components[d] = "sha256:" + sha(jcs(sub))

migrations = []
for p in sorted(x for x in hexmap if x.startswith("migrations/") and x.endswith(".yaml")):
    m = yaml.safe_load(open(os.path.join(kdir, p)))
    migrations.append({"id": m["id"], "from_version": str(m["from_version"]), "to_version": str(m["to_version"]), "path": p,
                       "digest": "sha256:" + hexmap[p], "breaking": bool(m.get("breaking", False)), "human_gate": str(m.get("human_gate", "none"))})

security_critical = [p for p in ["constitution/HARD_INVARIANTS.yaml", "policies/AUTHORITY_POLICY.yaml", "policies/HUMAN_GATE_POLICY.yaml",
                                 "policies/POLICY_PRECEDENCE.yaml", "policies/SECURITY_POLICY.yaml", "policies/TOOL_POLICY.yaml", "roles/ROLES.yaml"] if p in hexmap]
docs = {n: "sha256:" + sha(open(os.path.join(REL, n), "rb").read()) for n in ["RELEASE_NOTES.md", "ROLLBACK.md"] if os.path.exists(os.path.join(REL, n))}

statement = {
    "_type": "https://agentic-engineering-os/statement/release/v1",
    "trust_profile": "test",
    "framework": meta["framework"],
    "manifest_version": 1,
    "release": {"version": str(meta["version"]), "release_id": f"{meta['framework']}@{meta['version']}#{tree_hex[:16]}", "sequence": 4,
                "release_commit": published["release_commit"], "release_tag": f"v{meta['version']}-rc1", "released_at": "2026-09-12T19:12:51Z"},
    "signing": {"role": "release", "algorithm": "ed25519"},
    "compatibility": {"cli": {"min": str(meta["cli_version"]), "max_exclusive": "5.0.0"}, "runtime": {"min": str(meta["runtime_version"]), "max_exclusive": "5.0.0"},
                      "kernel_contract_version": int(meta["kernel_contract_version"]), "supported_from_versions": [str(v) for v in meta["supported_from_versions"]],
                      "index_version": f"{meta['version']}-idx3", "schema_versions": {k: str(v) for k, v in meta["schema_versions"].items()}},
    "kernel": {"tree_rules": "gov-tree-v1", "file_count": len(hexmap), "files": {p: "sha256:" + h for p, h in hexmap.items()},
               "tree_digest": "sha256:" + tree_hex, "manifest_digest": "sha256:" + manifest_hex},
    "components": components,
    "security_critical": security_critical,
    "migrations": migrations,
    "update_impact": {"breaking_changes": [str(x) for x in published.get("breaking_changes", [])], "human_gates": [str(x) for x in published.get("human_gates", [])],
                      "required_index_rebuilds": [str(x) for x in published.get("required_index_rebuilds", [])]},
    "documents": docs,
    "provenance": {"release_branch": f"release/{meta['version']}-rc1", "builder": f"gov release build --version {meta['version']} (illustrative)",
                   "reproduced_from_commit": published["release_commit"], "source_tree": "git archive of release_commit: framework, migrations, tools"},
}

checks = {
    "tree_digest_equals_published_release_hash": tree_hex == published["release_hash"],
    "manifest_digest_equals_KERNEL_MANIFEST_hash": manifest_hex == km_hash,
    "file_count": len(hexmap),
}

payload = jcs(statement)
assert jcs(json.loads(payload)) == payload, "payload is not canonical"
open(os.path.join(HERE, "release-statement.payload.example.json"), "wb").write(payload)
statement_digest = "sha256:" + sha(payload)
checks["statement_digest"] = statement_digest

try:
    import jsonschema
    schema = json.load(open(os.path.join(HERE, "..", "schemas", "release-statement.schema.json")))
    jsonschema.Draft202012Validator(schema).validate(statement)
    checks["schema_valid"] = True
except ImportError:
    checks["schema_valid"] = "jsonschema not installed"

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    sk = Ed25519PrivateKey.generate()  # ephemeral; never persisted
    pk_raw = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    keyid = "ed25519:" + sha(pk_raw)
    pae = b"DSSEv1 %d %s %d %s" % (len(PT), PT.encode(), len(payload), payload)
    env = {"payloadType": PT, "payload": base64.b64encode(payload).decode(), "signatures": [{"keyid": keyid, "sig": base64.b64encode(sk.sign(pae)).decode()}]}
    open(os.path.join(HERE, "release.dsse.example.json"), "w").write(json.dumps(env, indent=2) + "\n")
    sk.public_key().verify(base64.b64decode(env["signatures"][0]["sig"]), pae)
    tampered = bytearray(payload); tampered[-2] ^= 1
    try:
        sk.public_key().verify(base64.b64decode(env["signatures"][0]["sig"]), b"DSSEv1 %d %s %d %s" % (len(PT), PT.encode(), len(tampered), bytes(tampered)))
        checks["tampered_payload_rejected"] = False
    except Exception:
        checks["tampered_payload_rejected"] = True
    checks["dsse_signature_verifies"] = True
    checks["ephemeral_test_public_key_b64"] = base64.b64encode(pk_raw).decode()
    try:
        import jsonschema
        jsonschema.Draft202012Validator(json.load(open(os.path.join(HERE, "..", "schemas", "dsse-envelope.schema.json")))).validate(env)
        checks["envelope_schema_valid"] = True
    except ImportError:
        pass
except ImportError:
    checks["dsse_signature_verifies"] = "cryptography not installed; envelope example not produced"

print(json.dumps(checks, indent=2))
