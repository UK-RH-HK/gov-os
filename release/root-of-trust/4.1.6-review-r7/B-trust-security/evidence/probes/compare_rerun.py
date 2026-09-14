#!/usr/bin/env python3
"""AR-0020: compare this review's re-run of the architect's evidence runner (scratch export of d07d200) with the committed outputs.
For each pair: byte-identical, or the number and first paths of differing JSON leaves. Environment: RUN (runner scratch), WT (worktree)."""
import gzip, hashlib, json, os, sys
RUN, WT = os.environ["RUN"], os.environ["WT"]
PK = os.path.join(WT, "release/root-of-trust/4.1.6")
X = os.path.join(RUN, "final/export/release/root-of-trust/4.1.6")
O = os.path.join(RUN, "final/out")
pairs = []
for f in ["CS7-derivation-calculator.json", "FA7-first-contact-authority.json", "CUR7-first-contact-currency.json", "ADM7-admission-stores.json", "ENV7-environment-authority.json",
          "BA11r7-machine-classes.json", "BA12r7-key-subsets-below-threshold.json", "PPR7-project-records.json", "DA05r7-combinations-under-CP1.json", "DA06r7-rendering-and-classifier-vocabulary.json",
          "STATEMENTS-CHECK.json", "PROF7-profile-conformance.json", "REGISTER-CHECK.json", "DA09r7-schema-fields-versus-register.json", "DA04r7-plan-regression-detection.json"]:
    pairs.append(("r7/" + f, os.path.join(PK, "evidence/r7", f), os.path.join(X, "evidence/r7", f)))
pairs.append(("r7/FA7 run2", os.path.join(PK, "evidence/r7/FA7-first-contact-authority.json"), os.path.join(O, "FA7-first-contact-authority.run2.json")))
pairs.append(("r7/CS7-results.json.gz (uncompressed)", os.path.join(PK, "evidence/r7/CS7-results.json.gz"), os.path.join(X, "evidence/r7/CS7-results.json.gz")))
ret = {"CSI6-selftest.json": "r6/CSI6-selftest.json", "CSI6-CSI-check-framework.json": "r6/CSI6-CSI-check-framework.json", "CSI6-CSI-check-release-4.1.5.json": "r6/CSI6-CSI-check-release-4.1.5.json",
       "CSI6-CSI-check-legacy-4.1.2.json": "r6/CSI6-CSI-check-legacy-4.1.2.json", "CSI6-CSI-check-legacy-4.1.3.json": "r6/CSI6-CSI-check-legacy-4.1.3.json", "CSI6-CSI-check-legacy-4.1.4.json": "r6/CSI6-CSI-check-legacy-4.1.4.json",
       "P4r6-conformance-oracle.json": "r6/P4r6-conformance-oracle.json", "CS6-derivation-calculator.json": "r6/CS6-derivation-calculator.json", "DA03r6-oracle-regression-sensitivity.json": "r6/DA03r6-oracle-regression-sensitivity.json",
       "FA6-first-admission.json": "r6/FA6-first-admission.json", "CON6-first-hand-constitutional-content.json": "r6/CON6-first-hand-constitutional-content.json", "SRC6-source-identity-v2.json": "r6/SRC6-source-identity-v2.json",
       "ADM6-admission-transactions.json": "r6/ADM6-admission-transactions.json", "UW6-user-writable-install.json": "r6/UW6-user-writable-install.json", "ATTR6-gitattributes-condition.json": "r6/ATTR6-gitattributes-condition.json",
       "ENV6-build-environment.json": "r6/ENV6-build-environment.json", "DA07r6-plan-regression-detection.json": "r7/retained/DA07r6-plan-regression-detection.on-revision-7-plan.json",
       "P4r5-conformance-oracle.json": "r5/P4r5-conformance-oracle.json", "DA03r5-oracle-regression-sensitivity.json": "r5/DA03r5-oracle-regression-sensitivity.json", "FA5-first-admission.stdout.json": "r5/FA5-first-admission.json",
       "REG5-release-scoped-registration.json": "r5/REG5-release-scoped-registration.json", "P1r4-project-strength-and-absence.json": "P1r4-project-strength-and-absence.json", "CS5-tcb-capability-sets.json": "r5/CS5-tcb-capability-sets.json"}
for a, b in ret.items():
    pairs.append(("retained/" + a, os.path.join(PK, "evidence", b), os.path.join(O, "retained", a)))
for sub, com in (("r6-probes", "r7/r6-probes"), ("r5-probes", "r7/r5-probes")):
    for f in sorted(os.listdir(os.path.join(O, sub))):
        if f.endswith(".json"):
            pairs.append((sub + "/" + f, os.path.join(PK, "evidence", com, f), os.path.join(O, sub, f)))


def load(p):
    raw = open(p, "rb").read()
    if p.endswith(".gz"):
        raw = gzip.decompress(raw)
    return raw


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, path + "/%d" % i)
    else:
        yield path, o


rows = []
for name, committed, rerun in pairs:
    r = {"item": name}
    if not os.path.exists(committed):
        r["status"] = "NO_COMMITTED_FILE"
    elif not os.path.exists(rerun) or os.path.getsize(rerun) == 0:
        r["status"] = "NO_RERUN_OUTPUT"
        err = rerun + ".stderr"
        if os.path.exists(err):
            r["stderr_tail"] = open(err).read().strip().split("\n")[-1][:200]
    else:
        a, b = load(committed), load(rerun)
        if a == b:
            r["status"] = "BYTE_IDENTICAL"
        else:
            try:
                ja, jb = json.loads(a), json.loads(b)
                la, lb = dict(leaves(ja)), dict(leaves(jb))
                diff = sorted(k for k in set(la) | set(lb) if la.get(k, "<absent>") != lb.get(k, "<absent>"))
                r["status"] = "JSON_DIFFERS"
                r["differing_leaves"] = len(diff)
                r["first_paths"] = diff[:8]
                vd = [k for k in diff if "/verdicts/" in k or k.startswith("/verdicts")]
                r["differing_verdict_leaves"] = vd[:8]
            except Exception as e:  # noqa: BLE001
                r["status"] = "BYTES_DIFFER_NOT_JSON"
        r["sha256_committed"], r["sha256_rerun"] = hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest()
    rows.append(r)
summary = {}
for r in rows:
    summary[r["status"]] = summary.get(r["status"], 0) + 1
print(json.dumps({"summary": summary, "rows": rows}, indent=1, sort_keys=True).replace(RUN, "<rerun>").replace(WT, "<worktree>"))
