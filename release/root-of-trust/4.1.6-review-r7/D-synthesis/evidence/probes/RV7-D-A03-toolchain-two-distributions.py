#!/usr/bin/env python3
"""RV7-D-A03 (AR-0022, synthesis reviewer D, held-out) — OP-10 (b) under OWNER-DESIGN-REQUIREMENTS-0002 OT-2: "Do NOT accept 'two
different distributions' or 'two mirrors of the same compiler binary' as independence"; the criterion must be explicit,
executable/testable and non-circular.

`33` R-BENV-6″ / `30` R-REP-9′ / `35` CC-3 state: two lineages independent when all four provenance strings differ, and "at least one
lineage's bootstrap_root is not an upstream binary compiler archive, and its compiler is itself a registered, reproduced bootstrap
release". Executed with the reference executor UNMODIFIED: a root-signed Trust Policy registers
  tc-up     the upstream rustc archive lineage (as w7world);
  tc-distro a distribution's rustc package, itself bootstrapped from the upstream stage0 archive, described with the distribution's
            own strings (bootstrap_root, package_source, build_system, signing_infrastructure all differ), with NO
            bootstrap_registration and NO archive_sha256.
Reproductions under (sup-A, tc-up) and (sup-B, tc-distro). Controls: the w7world `tc-up-relabelled` entry (identical strings) and the
honest tc-boot entry. Code facts: which toolchain registry fields the executor reads; which the schema requires. Target label facts:
the pack's label versus the owner's label.
Environment: A03_SCRATCH, PACK. Output: JSON on stdout.
"""
import ast, json, os, re, sys, tempfile
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
R7DIR = os.path.join(PACK, "evidence", "r7")
sys.path.insert(0, R7DIR)
import w7world as W  # noqa: E402
import yaml  # noqa: E402
GA = W.GA
SCR = tempfile.mkdtemp(prefix="d-a03-", dir=os.environ["A03_SCRATCH"])
V = GA.Verifier(SCR)
DISTRO = {"toolchain_id": "tc-distro", "provenance": {"bootstrap_root": "distribution-rustc-package-bootstrap", "package_source": "deb.debian.org/debian",
                                                     "build_system": "debian-buildd", "signing_infrastructure": "debian-archive-keyring"}}
TPS3 = W.envelope("trust-policy+json", W.tps_payload(version=3, min_seq=9, supply_chain={"suppliers": W.SUPPLIERS, "toolchains": W.TOOLCHAINS + [DISTRO]}), ["r1", "r3"])
B11 = W.T11["payload"]


def world(tag, tc2):
    rel = W.Release(tag, 10, 2, 3, 12, ("g3", "g4"), ("p3", "p4"), toolchains=("tc-up", tc2), rep_plan=[("p3", W.ENV_A, "tc-up"), ("p4", W.ENV_B, tc2)])
    t = W.tss(12, "2026-09-14T02:00:00Z", W.ROOT2, 2, TPS3, W.FCA2, W.PRIOR11 + [{"sequence": 11, "digest": W.T11["digest"]}],
              B11["registrations"] + [rel.reg["digest"]], B11["published_binaries"] + [rel.D], B11["revocations"], revocation_statements=B11["revocation_statements"])
    res = W.admit(rel.binary, W.FCA2, t, W.FULL + [TPS3] + rel.all() + [t], verifier=V, workdir=SCR)
    return res["result"]


src = open(os.path.join(R7DIR, "gov_admit_reference_r7.py")).read()
schema = json.load(open(os.path.join(PACK, "schemas", "trust-policy-statement.schema.json")))
tc_item = schema["properties"]["supply_chain"]["properties"]["toolchains"]["items"]
prof = yaml.safe_load(open(os.path.join(PACK, "profile", "CP-1.yaml")))
cp35 = open(os.path.join(PACK, "35-CERTIFIED-PROFILE.md")).read()
names_in_code = {n.id if isinstance(n, ast.Name) else n.value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
out = {"probe": "RV7-D-A03 toolchain lineage independence by distribution strings (AR-0022)",
       "results": {"two_distributions_distinct_strings_no_bootstrap_registration": world("RD", "tc-distro"),
                   "control_relabelled_identical_strings": world("RL", "tc-up-relabelled"),
                   "control_honest_bootstrapped_lineage": world("RB", "tc-boot")},
       "code": {"executor_reads_bootstrap_registration": "bootstrap_registration" in names_in_code,
                "executor_reads_archive_sha256": "archive_sha256" in names_in_code,
                "executor_toolchain_attrs": list(GA.TOOLCHAIN_ATTRS),
                "executor_checks_one_lineage_not_upstream_archive": bool(re.search(r"upstream|bootstrap_registration", src.split("def independent_classes")[1].split("def refuse")[0]))},
       "schema": {"toolchain_required_fields": tc_item.get("required"), "bootstrap_registration_required": "bootstrap_registration" in tc_item.get("required", []),
                  "provenance_fields_are_free_strings": all(v.get("type") == "string" for v in tc_item["properties"]["provenance"]["properties"].values())},
       "labels": {"profile_initial_target_statuses": sorted({t["status"] for t in prof["certified_targets"]["initial_target_set"]}),
                  "owner_required_label_present_in_35": "TOOLCHAIN ASSURANCE INCOMPLETE" in cp35,
                  "CC3_text": prof["certified_targets"]["criteria"]["CC-3"]}}
r = out["results"]
out["verdicts"] = {
    "two_distributions_accepted_as_independent_lineages": r["two_distributions_distinct_strings_no_bootstrap_registration"] == "ACCEPTED",
    "control_identical_strings_refused": r["control_relabelled_identical_strings"] == "TOOLCHAIN_DIVERSITY_NOT_MET",
    "control_honest_accepted": r["control_honest_bootstrapped_lineage"] == "ACCEPTED",
    "not_rooted_in_upstream_archive_is_not_checked_by_the_verifier": not out["code"]["executor_reads_bootstrap_registration"] and not out["code"]["executor_checks_one_lineage_not_upstream_archive"],
    "schema_does_not_require_bootstrap_evidence": not out["schema"]["bootstrap_registration_required"],
    "owner_label_not_adopted": not out["labels"]["owner_required_label_present_in_35"],
}
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(out, indent=1, sort_keys=True, default=str)))
