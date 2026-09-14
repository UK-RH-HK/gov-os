#!/usr/bin/env python3
"""AR-0022: reproduction comparison of every re-run against the committed output (byte-identical, run-dependent leaves, or
differing verdict leaves). Paths are normalised. Output: JSON on stdout."""
import gzip, hashlib, json, os, re, sys

S = os.environ.get("AR0022_SCRATCH", "<scratch>")  # the AR-0022 scratch root (export, outputs)
X = S + "/export"
P = X + "/release/root-of-trust/4.1.6"
R7 = P + "/evidence/r7"
BO = X + "/release/root-of-trust/4.1.6-review-r7/B-trust-security/evidence/outputs"
CO = X + "/release/root-of-trust/4.1.6-review-r7/C-compat-transaction/evidence/outputs"


def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, p + "[%d]" % i)
    else:
        yield p, o


def norm_text(s):
    s = re.sub(r"/tmp/claude-1000/[^\"\s]*?/ar-00(21|22)/(c7/)?t7/?", "<t7>/", s)
    s = re.sub(r"/tmp/claude-1000/[^\"\s]*?/ar-00(21|22)/[^\"\s]*", "<scratch>", s)
    s = re.sub(r"<ar21>/t7/?", "<t7>/", s)
    s = re.sub(r"(txn7|gitops7|g7|struct7)-[a-z0-9_]{8}", "X", s)
    return s


def cmp(mine, theirs, verdict_key="verdicts", normalise=False):
    a, b = open(mine, "rb").read(), open(theirs, "rb").read()
    if a == b:
        return {"status": "BYTE_IDENTICAL"}
    try:
        ja, jb = json.loads(a), json.loads(b)
    except Exception as e:
        return {"status": "NOT_JSON", "error": str(e)}
    if normalise:
        ja, jb = json.loads(norm_text(json.dumps(ja))), json.loads(norm_text(json.dumps(jb)))
    la, lb = dict(leaves(ja)), dict(leaves(jb))
    diff = sorted(k for k in set(la) | set(lb) if la.get(k, "<absent>") != lb.get(k, "<absent>"))
    vdiff = [k for k in diff if k.startswith("/" + verdict_key)]
    return {"status": "EQUAL_AFTER_NORMALISATION" if not diff else "DIFFER", "differing_leaves": len(diff), "differing_verdict_leaves": vdiff, "examples": diff[:12]}


out = {"architect_r7": {}, "architect_retained": {}, "reviewer_B": {}, "reviewer_C": {}, "stale_claims_B_L5": {}}
for f in ("CS7-derivation-calculator", "FA7-first-contact-authority", "CUR7-first-contact-currency", "ADM7-admission-stores", "ENV7-environment-authority",
          "BA11r7-machine-classes", "BA12r7-key-subsets-below-threshold", "PPR7-project-records", "DA05r7-combinations-under-CP1",
          "DA06r7-rendering-and-classifier-vocabulary", "STATEMENTS-CHECK", "PROF7-profile-conformance", "REGISTER-CHECK",
          "DA09r7-schema-fields-versus-register", "DA04r7-plan-regression-detection"):
    out["architect_r7"][f] = cmp(S + "/out/arch/%s.json" % f, R7 + "/%s.json" % f)
out["architect_r7"]["FA7-first-contact-authority (second run)"] = cmp(S + "/out/arch/FA7-first-contact-authority.run2.json", R7 + "/FA7-first-contact-authority.json")
out["architect_r7"]["CS7-results.json.gz (uncompressed)"] = {"status": "BYTE_IDENTICAL" if gzip.open(S + "/out/arch/CS7-results.json.gz").read() == gzip.open(R7 + "/CS7-results.json.gz").read() else "DIFFER"}
for a, b in (("CSI-selftest", "CSI6-selftest"), ("CSI-check-framework", "CSI6-CSI-check-framework"), ("CSI-check-release-4.1.5", "CSI6-CSI-check-release-4.1.5"),
             ("CSI-check-legacy-4.1.2", "CSI6-CSI-check-legacy-4.1.2"), ("CSI-check-legacy-4.1.3", "CSI6-CSI-check-legacy-4.1.3"), ("CSI-check-legacy-4.1.4", "CSI6-CSI-check-legacy-4.1.4")):
    out["architect_retained"][a] = cmp(S + "/out/arch/%s.json" % a, P + "/evidence/r6/%s.json" % b)
for f in ("RV7-B-A01", "RV7-B-A01m", "RV7-B-A02", "RV7-B-CS7", "RV7-B-A04-A05", "RV7-B-A09"):
    out["reviewer_B"][f] = cmp(S + "/out/B/%s.json" % f, BO + "/%s.json" % f)
for f, mine in (("cur7x", "cur7x.json"), ("adm7x", "adm7x.json"), ("design7", "design7.json"), ("ident7", "ident7.json"), ("registers7", "registers7.json"),
                ("struct7", "struct7.json"), ("build7", "build7.json")):
    out["reviewer_C"][f] = cmp(S + "/out/C/" + mine, CO + "/%s.json" % f, normalise=True)
g = json.loads(norm_text(open(S + "/out/C/gitops7/gitops7.json").read()))
h = json.loads(norm_text(open(CO + "/gitops7.json").read()))
st = lambda f: {k: (v.get("state"), v.get("kernel_tampered"), v.get("classifications"), v.get("occupation_tracked")) if isinstance(v, dict) else v for k, v in f["facts"].items()}
out["reviewer_C"]["gitops7"] = {"operations": len(g["facts"]), "state_tamper_classification_occupation_equal_for_every_operation": st(g) == st(h)}
t = json.loads(norm_text(open(S + "/out/C/txn7/txn7.json").read()))
u = json.loads(norm_text(open(CO + "/txn7.json").read()))
out["reviewer_C"]["txn7"] = {k + "_equal": t.get(k) == u.get(k) for k in ("summary", "first_install_honouring", "rollforward_model", "uninstall", "absent_with_legacy_named_content", "shared_record")}
rowdiff = {}
for k in set(t["rows"]) | set(u["rows"]):
    a, b = t["rows"].get(k) or {}, u["rows"].get(k) or {}
    for kk in set(a) | set(b):
        if a.get(kk) != b.get(kk):
            rowdiff.setdefault(kk, 0)
            rowdiff[kk] += 1
out["reviewer_C"]["txn7"]["row_fields_that_differ_with_counts"] = rowdiff
ms = S + "/out/C/matrix7/matrix7-summary.json"
if os.path.exists(ms):
    a, b = json.load(open(ms)), json.load(open(CO + "/matrix7-summary.json"))
    out["reviewer_C"]["matrix7"] = {"rows": [a.get("rows"), b.get("rows")], "active": [a.get("active"), b.get("active")], "skipped": [a.get("skipped"), b.get("skipped")],
                                    "writing_rows_rot1": [a.get("writing_rows_rot1"), b.get("writing_rows_rot1")],
                                    "by_binary_equal": a.get("by_binary") == b.get("by_binary"), "by_kind_equal": a.get("by_kind") == b.get("by_kind"),
                                    "aggregate_equal": a.get("aggregate") == b.get("aggregate"), "binaries_sha256_equal": a.get("binaries_sha256") == b.get("binaries_sha256"),
                                    "properties_mine": a.get("properties"), "properties_committed_equal": a.get("properties") == b.get("properties")}
    if a.get("aggregate") != b.get("aggregate"):
        ag, bg = a.get("aggregate") or {}, b.get("aggregate") or {}
        out["reviewer_C"]["matrix7"]["aggregate_keys_differing"] = sorted(k for k in set(ag) | set(bg) if ag.get(k) != bg.get(k))[:40]
else:
    out["reviewer_C"]["matrix7"] = "NOT_FINISHED"
out["stale_claims_B_L5"]["DA07r6 on the revision-7 plan"] = cmp(S + "/out/stale/DA07r6.json", R7 + "/retained/DA07r6-plan-regression-detection.on-revision-7-plan.json")
out["stale_claims_B_L5"]["RV6-B-A03"] = cmp(S + "/out/stale/RV6-B-A03.json", R7 + "/r6-probes/RV6-B-A03.json")
print(json.dumps(out, indent=1, sort_keys=True))
