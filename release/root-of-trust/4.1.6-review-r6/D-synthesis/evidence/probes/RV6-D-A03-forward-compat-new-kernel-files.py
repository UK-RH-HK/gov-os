#!/usr/bin/env python3
"""RV6-D-A03 — forward-compatibility constraint (HO-0001 §4) on the revision-6 checker: new kernel-shipped constitutional files of
the later Phase 1 stages (Gate W artifact-flow and consumption-integrity policy; G0–G6 governance health scheduler), classified by
inventory data only, and the R-CON-5 per-project listing of their changes (review r6 synthesis D, AR-0018). Executed (pack checker
`constitutional-surface/csi_check.py`, unmodified; scratch inventories derived from the committed one by adding data rows only).
Scratch only.

HO-0001 §4: "The constitutional-surface classification and default-deny rule must be able to classify such new constitutional files
and keys without another architecture revision." `34` R-CON-5 lists changes of "security-classified" units; `csi_lib`
`unit_security_classified` uses an inventory flag `security_classified` when present, else a compiled name list and path-prefix list.
Reviewer B's RV6-B-A10 found existing files outside the list (LOW). This attack asks the forward question for new files.

Files (content illustrative; the structure is what the later stages describe):
  GW  Gate W policy, placed (i) `policies/ARTIFACT_FLOW_POLICY.yaml` (a listed prefix) and (ii) `workflow/ARTIFACT_FLOW.yaml` (not listed).
  HS  G0–G6 health scheduler `health/GOVERNANCE_HEALTH_SCHEDULE.yaml` (not listed).
Weakened variants: GW `require_consumption_receipt: false`, `lineage_required: false`; HS G3 `never`.
Steps per placement: (1) committed inventory: `check` (default deny expected, exit 2); (2) inventory + a data-only `pinned_file` row:
`check` (exit 0 expected); (3) registrations derived from the genuine and weakened kernels; `registration-changes` with the row
lacking `security_classified` and with `security_classified: true`; (4) `verify-registration` of the weakened proposal against the
custodian's genuine build (R-CON-1, exit 3 expected).
Environment: REVIEW_REPO, SCRATCH. Output: JSON on stdout.
"""
import copy, json, os, shutil, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
CS = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402  (read-only use of the digest function)

SCR = tempfile.mkdtemp(prefix="da03-", dir=os.environ["SCRATCH"])
ENV = {"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"}
INV0 = os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")


def chk(*args):  # same invocation shape as reviewer B's RV6-B-A10 (AR-0016)
    r = subprocess.run([sys.executable, "-B", os.path.join(CS, "csi_check.py")] + list(args), capture_output=True, text=True, env=ENV)
    try:
        j = json.loads(r.stdout)
    except Exception:
        j = {"stdout_tail": r.stdout[-400:], "stderr_tail": r.stderr[-400:]}
    return r.returncode, j


GW = lambda receipt: ("ARTIFACT_FLOW_POLICY:\n  version: 1\n  require_input_manifest: true\n  require_consumption_receipt: %s\n  lineage_required: %s\n"
                      "  consumption_integrity: sha256\n" % ("true" if receipt else "false", "true" if receipt else "false"))
HS = lambda g3: "GOVERNANCE_HEALTH_SCHEDULE:\n  version: 1\n  levels:\n    G0: 1h\n    G1: 6h\n    G2: 24h\n    G3: %s\n    G4: 30d\n    G5: 90d\n    G6: 365d\n" % g3
CASES = {"GW_listed_prefix": ("policies/ARTIFACT_FLOW_POLICY.yaml", GW(True), GW(False)),
         "GW_unlisted_path": ("workflow/ARTIFACT_FLOW.yaml", GW(True), GW(False)),
         "HS_unlisted_path": ("health/GOVERNANCE_HEALTH_SCHEDULE.yaml", HS("7d"), HS("never"))}


def kernel(name, rel, content):
    d = os.path.join(SCR, name)
    shutil.copytree(os.path.join(REPO, "framework"), d)
    os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
    open(os.path.join(d, rel), "w").write(content)
    return d


inv_base = yaml.safe_load(open(INV0))
out = {"probe": "RV6-D-A03 forward compatibility: new kernel constitutional files and R-CON-5 listing (AR-0018)", "cases": {}}
for case, (rel, good, weak) in CASES.items():
    kg, kw = kernel(case + "-genuine", rel, good), kernel(case + "-weakened", rel, weak)
    row = {"path": rel}
    rc, j = chk("check", "--json", kg)
    row["1_committed_inventory_check_exit"] = rc
    row["1_unclassified_files"] = j.get("unclassified_files")
    invs = {}
    for flag in ("no_flag", "security_classified_true"):
        inv = copy.deepcopy(inv_base)
        # one registered value per unit (23 §12.2): the genuine file's digest only (a first run that listed both digests was
        # refused REGISTRATION_NOT_SINGLE_VALUED, exit 5 — a probe error, not a finding)
        rule = {"path": rel, "mode": "pinned_file", "presence": "required", "digests": {rel: [L.fdigest(os.path.join(kg, rel))]},
                "rationale": "AR-0018 probe: new constitutional file classified by inventory data only"}
        if flag == "security_classified_true":
            rule["security_classified"] = True
        inv["files"].append(rule)
        p = os.path.join(SCR, "%s-%s.inventory.yaml" % (case, flag))
        yaml.safe_dump(inv, open(p, "w"), sort_keys=False)
        invs[flag] = p
    rc, j = chk("check", "--json", kg, "--inventory", invs["no_flag"])
    row["2_data_only_row_check_exit"] = rc
    row["2_unclassified_files"] = j.get("unclassified_files")
    row["2_malformed_or_consistency"] = (j.get("malformed") or j.get("consistency"))
    for flag, invp in invs.items():
        regs = {}
        for nm, kd, rid, seq in (("genuine", kg, "4.1.7", "17"), ("weakened", kw, "4.1.8", "18")):
            p = os.path.join(SCR, "%s-%s-%s.registration.json" % (case, flag, nm))
            rc, j = chk("derive-registration", kd, "--release-id", rid, "--sequence", seq, "--inventory", invp)
            json.dump(j, open(p, "w"))
            regs[nm] = (rc, p, sorted(u for u in (j.get("units") or {}) if rel in u))
        rc, j = chk("registration-changes", "--held", regs["genuine"][1], "--new", regs["weakened"][1], "--inventory", invp, "--json")
        row["3_%s" % flag] = {"derive_exits": {k: v[0] for k, v in regs.items()}, "units_for_new_file": regs["genuine"][2],
                              "registration_changes_exit": rc, "changes": [c.get("unit") for c in (j.get("changes") or [])][:4],
                              "security_classified_changes": [c.get("unit") for c in (j.get("security_classified_changes") or [])][:4]}
        if flag == "no_flag":
            rc, j = chk("verify-registration", "--registration", regs["weakened"][1], "--source-kernel", kg, "--inventory", invp, "--json")
            row["4_verify_weakened_proposal_against_genuine_build_exit"] = rc
    out["cases"][case] = row
lib = open(os.path.join(CS, "csi_lib.py")).read()
out["checker_code"] = {"security_classified_flag_read_from_inventory": "fr.get(\"security_classified\")" in lib,
                       "fallback_for_unflagged_file_is_prefix_list": "return ident.startswith(SECURITY_CLASSIFIED_FILE_PREFIXES)" in lib}
c = out["cases"]
out["verdicts"] = {
    "default_deny_for_every_new_file": all(v["1_committed_inventory_check_exit"] == 2 for v in c.values()),
    "classified_by_data_only_row": all(v["2_data_only_row_check_exit"] == 0 for v in c.values()),
    "first_hand_derivation_refuses_weakened_proposal": all(v["4_verify_weakened_proposal_against_genuine_build_exit"] == 3 for v in c.values()),
    "listed_prefix_change_listed_without_flag": c["GW_listed_prefix"]["3_no_flag"]["registration_changes_exit"] == 8,
    "unlisted_path_change_NOT_listed_without_flag": all(c[k]["3_no_flag"]["registration_changes_exit"] == 0 for k in ("GW_unlisted_path", "HS_unlisted_path")),
    "unlisted_path_change_listed_with_data_flag": all(c[k]["3_security_classified_true"]["registration_changes_exit"] == 8 for k in ("GW_unlisted_path", "HS_unlisted_path")),
}
print(json.dumps(out, indent=1, sort_keys=True, default=str).replace(SCR, "<scratch>").replace(REPO, "<export>"))
