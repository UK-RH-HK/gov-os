#!/usr/bin/env python3
"""RV7-B-A04 and RV7-B-A05 (AR-0020, reviewer B, held-out). Executed with the revision-7 reference executor UNMODIFIED.

A04  Supplier-class independence "by provenance" is inequality of four free-text attribute strings plus disjoint checksum-key sets
     in the root-signed registry (`independent_classes`, `33` R-BENV-5″). A registry entry sup-A2 that names the SAME upstream
     (Debian bookworm images, the Debian archive, Debian buildd, the Debian archive keyring) under different spellings and a second
     checksum key of that upstream is counted as a second independent class: reproductions in ENV_A (sup-A) and ENV_A2 (sup-A2) are
     accepted. Controls: identical attribute strings (the committed ENV7 A08 / FA7 R8 shape) refuse; a shared key refuses.
A05  The certified trust-root schema accepts CP-1-nonconforming grants for the root-held purposes: `trust-policy` and
     `first-contact-authority` at threshold 1 on keys other than the root keys validate against `trust-root.schema.json`; the compiled
     `root_conforms` refuses them. (Schema acceptance of a root shape below OP-1's threshold; refused only by the compiled check.)
Environment: A04_SCRATCH, PACK. Output: JSON on stdout.
"""
import copy, json, os, re, sys, tempfile
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
sys.path.insert(0, os.path.join(PACK, "evidence", "r7"))
import w7world as W  # noqa: E402
GA = W.GA
SCR = tempfile.mkdtemp(prefix="a04-", dir=os.environ["A04_SCRATCH"])
V = GA.Verifier(SCR)
out = {"probe": "RV7-B-A04/A05 provenance labels and schema shapes (AR-0020)"}
T = W.T11
ENV_A2 = W.sha256d(b"environment-manifest-A2-same-upstream")


def run_with_supplier(extra_supplier):
    sup = W.SUPPLIERS + [extra_supplier]
    pol = W.envelope("trust-policy+json", W.tps_payload(version=3, min_seq=9, supply_chain={"suppliers": sup, "toolchains": W.TOOLCHAINS}), ["r1", "r2"])
    rel = W.Release("R9", 9, 2, 1, 10, ("g3", "g4"), ("p2", "p4"), security_relevant_change=True, envs=((W.ENV_A, "sup-A"), (ENV_A2, extra_supplier["supplier_id"])),
                    toolchains=("tc-up", "tc-boot"), rep_plan=[("p2", W.ENV_A, "tc-up"), ("p4", ENV_A2, "tc-boot")])
    p = copy.deepcopy(T["payload"])
    p["registrations"] = [x for x in p["registrations"] if x != W.R9.reg["digest"]] + [rel.reg["digest"]]
    p["references"] = dict(p["references"], trust_policy={"version": 3, "digest": pol["digest"]})
    t = W.envelope("trust-state+json", p, ["ts1", "ts2"])
    bundle = [e for e in W.FULL if e not in W.R9.all()] + rel.all() + [t, pol]
    return W.admit(rel.binary, W.FCA2, t, bundle, verifier=V, workdir=SCR)["result"]


same_upstream_other_spelling = {"supplier_id": "sup-A2", "provenance": {"base_image_lineage": "debian-12-official-images", "package_source": "cdn-fastly.deb.debian.org",
                                "build_system": "buildd.debian.org", "signing_infrastructure": "debian-archive-keyring-2023"}, "checksum_keys": [W.kid("upA-second-key")]}
identical_strings = {"supplier_id": "sup-A2", "provenance": dict(W.SUPPLIERS[0]["provenance"]), "checksum_keys": [W.kid("upA-second-key")]}
shared_key = dict(same_upstream_other_spelling, checksum_keys=[W.kid("upA")])
A04 = {"same_upstream_four_other_spellings_second_key": run_with_supplier(same_upstream_other_spelling),
       "control_identical_provenance_strings": run_with_supplier(identical_strings),
       "control_shared_checksum_key": run_with_supplier(shared_key),
       "independent_classes_count_same_upstream_spellings": GA.independent_classes({"sup-A", "sup-A2"}, {"sup-A": W.SUPPLIERS[0], "sup-A2": same_upstream_other_spelling}, GA.SUPPLIER_ATTRS, "checksum_keys")}
out["A04"] = A04

# A05
try:
    import jsonschema
    have_js = True
except Exception:  # noqa: BLE001
    have_js = False
schema = json.load(open(os.path.join(PACK, "schemas", "trust-root.schema.json")))
ex = json.load(open(os.path.join(PACK, "examples", "rev7", "trust-root.payload.example.json")))
A05 = {"jsonschema_available": have_js}
if have_js:
    val = lambda inst: sorted(e.message[:160] for e in jsonschema.Draft202012Validator(schema).iter_errors(inst))
    A05["committed_example_errors"] = val(ex)
    bad = copy.deepcopy(ex)
    other = [k for k in bad["keys"] if k not in bad["purposes"]["root"]["key_ids"]][:1]
    bad["purposes"]["trust-policy"] = {"key_ids": other, "threshold": 1}
    bad["purposes"]["first-contact-authority"] = {"key_ids": other, "threshold": 1}
    A05["trust_policy_and_fca_threshold_1_on_a_non_root_key_schema_errors"] = val(bad)
g = W.grants(**{"trust-policy": {"keys": [W.kid("ts1")], "threshold": 1}, "first-contact-authority": {"keys": [W.kid("r1")], "threshold": 1}})
A05["compiled_root_conforms_same_shape"] = GA.root_conforms(W.root_payload(1, None, W.V1_KEYS, g), {})
out["A05"] = A05
out["verdicts"] = {
    "A04_same_upstream_counted_as_two_independent_classes": A04["same_upstream_four_other_spellings_second_key"] == "ACCEPTED" and A04["independent_classes_count_same_upstream_spellings"] == 2,
    "A04_controls_refuse": A04["control_identical_provenance_strings"] == "ENVIRONMENT_DIVERSITY_NOT_MET" and A04["control_shared_checksum_key"] == "ENVIRONMENT_DIVERSITY_NOT_MET",
    "A05_schema_accepts_threshold_1_root_purposes": have_js and not A05.get("trust_policy_and_fca_threshold_1_on_a_non_root_key_schema_errors") and not A05.get("committed_example_errors"),
    "A05_compiled_check_refuses": A05["compiled_root_conforms_same_shape"][0] is False,
}
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(out, indent=1, sort_keys=True, default=str)))
