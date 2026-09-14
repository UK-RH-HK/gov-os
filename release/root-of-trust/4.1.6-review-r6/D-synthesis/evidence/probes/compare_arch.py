# AR-0018: compare re-run outputs with committed outputs (byte, then leaf-level after path normalisation).
# Adapted from review r6 B compare_reruns.py (AR-0016), with attribution.
import gzip, hashlib, json, os, re, sys
S = sys.argv[1]
EV = os.path.join(S, "pristine", "release", "root-of-trust", "4.1.6", "evidence")
RB = os.path.join(S, "pristine", "release", "root-of-trust", "4.1.6-review-r6", "B-trust-security", "evidence", "outputs")
def norm(t): return re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratch>", t)
def load(p):
    try: return json.load(open(p))
    except Exception as e: return {"_unparsed": str(e)}
def flat(o, pre=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from flat(v, pre + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from flat(v, pre + "[%d]" % i)
    else: yield pre, o
def cmp(a, b):
    if not os.path.exists(a): return {"missing_rerun": a}
    A, B = open(a, "rb").read(), open(b, "rb").read()
    if A == B: return {"byte_identical": True, "sha256": hashlib.sha256(A).hexdigest()}
    fa, fb = dict(flat(load(a))), dict(flat(load(b)))
    diff = sorted(k for k in set(fa) | set(fb) if norm(json.dumps(fa.get(k))) != norm(json.dumps(fb.get(k))))
    return {"byte_identical": False, "differing_leaves": len(diff), "examples": [(k, str(fa.get(k))[:140], str(fb.get(k))[:140]) for k in diff[:8]]}
R = os.path.join(S, "runs", "arch")
pairs = {
 "CSI6-selftest": ("CSI6-selftest.json", "r6/CSI6-selftest.json"),
 "CSI6-framework": ("CSI6-CSI-check-framework.json", "r6/CSI6-CSI-check-framework.json"),
 "CSI6-4.1.5": ("CSI6-CSI-check-release-4.1.5.json", "r6/CSI6-CSI-check-release-4.1.5.json"),
 "CSI6-4.1.2": ("CSI6-CSI-check-legacy-4.1.2.json", "r6/CSI6-CSI-check-legacy-4.1.2.json"),
 "CSI6-4.1.3": ("CSI6-CSI-check-legacy-4.1.3.json", "r6/CSI6-CSI-check-legacy-4.1.3.json"),
 "CSI6-4.1.4": ("CSI6-CSI-check-legacy-4.1.4.json", "r6/CSI6-CSI-check-legacy-4.1.4.json"),
 "P4r6": ("P4r6-conformance-oracle.json", "r6/P4r6-conformance-oracle.json"),
 "CS6": ("CS6-derivation-calculator.json", "r6/CS6-derivation-calculator.json"),
 "REGISTER-CHECK": ("REGISTER-CHECK.json", "r6/REGISTER-CHECK.json"),
 "STATEMENTS-CHECK": ("STATEMENTS-CHECK.json", "r6/STATEMENTS-CHECK.json"),
 "DA03r6": ("DA03r6-oracle-regression-sensitivity.json", "r6/DA03r6-oracle-regression-sensitivity.json"),
 "FA6-run1": ("FA6-first-admission.json", "r6/FA6-first-admission.json"),
 "FA6-run2": ("FA6-first-admission.run2.json", "r6/FA6-first-admission.json"),
 "CON6": ("CON6-first-hand-constitutional-content.json", "r6/CON6-first-hand-constitutional-content.json"),
 "SRC6": ("SRC6-source-identity-v2.json", "r6/SRC6-source-identity-v2.json"),
 "ADM6": ("ADM6-admission-transactions.json", "r6/ADM6-admission-transactions.json"),
 "UW6": ("UW6-user-writable-install.json", "r6/UW6-user-writable-install.json"),
 "ATTR6": ("ATTR6-gitattributes-condition.json", "r6/ATTR6-gitattributes-condition.json"),
 "DA07r6": ("DA07r6-plan-regression-detection.json", "r6/DA07r6-plan-regression-detection.json"),
 "ENV6": ("ENV6-build-environment.json", "r6/ENV6-build-environment.json"),
 "P4r5": ("P4r5-conformance-oracle.json", "r5/P4r5-conformance-oracle.json"),
 "DA03r5": ("DA03r5-oracle-regression-sensitivity.json", "r5/DA03r5-oracle-regression-sensitivity.json"),
 "REG5": ("REG5-release-scoped-registration.json", "r5/REG5-release-scoped-registration.json"),
 "P1r4": ("P1r4-project-strength-and-absence.json", "P1r4-project-strength-and-absence.json"),
 "CS5": ("CS5-tcb-capability-sets.json", "r5/CS5-tcb-capability-sets.json"),
}
res = {"architect": {}, "reviewer_B": {}}
for k, (a, b) in pairs.items():
    res["architect"][k] = cmp(os.path.join(R, a), os.path.join(EV, b))
res["architect"]["FA5(json written in export)"] = cmp(os.path.join(S, "export/release/root-of-trust/4.1.6/evidence/r5/FA5-first-admission.json"), os.path.join(EV, "r5/FA5-first-admission.json"))
ga, gb = gzip.decompress(open(os.path.join(R, "CS6-results.json.gz"), "rb").read()), gzip.decompress(open(os.path.join(EV, "r6/CS6-results.json.gz"), "rb").read())
res["architect"]["CS6-results(uncompressed)"] = {"byte_identical": ga == gb}
for f in sorted(os.listdir(os.path.join(S, "runs", "B"))):
    if f.endswith(".json"):
        res["reviewer_B"][f] = cmp(os.path.join(S, "runs", "B", f), os.path.join(RB, f))
print(json.dumps(res, indent=1))
