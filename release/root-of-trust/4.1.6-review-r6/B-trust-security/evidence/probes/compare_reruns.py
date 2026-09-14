import json, os, sys, hashlib, gzip, re
S = sys.argv[1]
P = os.path.join(S, "pristine", "release", "root-of-trust")
def norm(t):
    t = re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratch>", t)
    return t
def load(p):
    try:
        return json.load(open(p))
    except Exception as e:
        return {"_unparsed": str(e)}
def flat(o, pre=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, pre + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, pre + "[%d]" % i)
    else:
        yield pre, o
def cmp(a, b):
    A, B = open(a, "rb").read(), open(b, "rb").read()
    if A == B:
        return {"byte_identical": True}
    ja, jb = load(a), load(b)
    fa, fb = dict(flat(ja)), dict(flat(jb))
    diff = sorted(k for k in set(fa) | set(fb) if norm(json.dumps(fa.get(k))) != norm(json.dumps(fb.get(k))))
    return {"byte_identical": False, "differing_leaves": len(diff), "examples": [(k, str(fa.get(k))[:120], str(fb.get(k))[:120]) for k in diff[:6]]}
res = {}
arch = os.path.join(P, "4.1.6", "evidence")
pairs = {
  "CS6": ("runs/CS6-derivation-calculator.json", "r6/CS6-derivation-calculator.json"),
  "REGISTER-CHECK": ("runs/REGISTER-CHECK.json", "r6/REGISTER-CHECK.json"),
  "STATEMENTS-CHECK": ("runs/STATEMENTS-CHECK.json", "r6/STATEMENTS-CHECK.json"),
  "STATEMENTS-CHECK-with-rerun-CS6": ("runs/STATEMENTS-CHECK.rerun-cs6.json", "r6/STATEMENTS-CHECK.json"),
  "P4r5": ("runs/P4r5-conformance-oracle.json", "r5/P4r5-conformance-oracle.json"),
  "DA03r5": ("runs/DA03r5-oracle-regression-sensitivity.json", "r5/DA03r5-oracle-regression-sensitivity.json"),
  "FA5(json written in export)": ("export/release/root-of-trust/4.1.6/evidence/r5/FA5-first-admission.json", "r5/FA5-first-admission.json"),
  "REG5": ("runs/REG5-release-scoped-registration.json", "r5/REG5-release-scoped-registration.json"),
  "P1r4": ("runs/P1r4-project-strength-and-absence.json", "P1r4-project-strength-and-absence.json"),
  "CS5": ("runs/CS5-tcb-capability-sets.json", "r5/CS5-tcb-capability-sets.json"),
}
for k, (a, b) in pairs.items():
    res[k] = cmp(os.path.join(S, a), os.path.join(arch, b))
ga, gb = gzip.decompress(open(os.path.join(S, "runs/CS6-results.json.gz"), "rb").read()), gzip.decompress(open(os.path.join(arch, "r6/CS6-results.json.gz"), "rb").read())
res["CS6-results.json.gz(uncompressed)"] = {"byte_identical": ga == gb, "sha256": hashlib.sha256(ga).hexdigest()}
r5 = os.path.join(P, "4.1.6-review-r5")
pr = {
  "RV5-B-A01": "B-trust-security/evidence/outputs/RV5-B-A01-first-admission-channel.json",
  "RV5-B-A04": "B-trust-security/evidence/outputs/RV5-B-A04-calculator-extensions.json",
  "RV5-B-A05": "B-trust-security/evidence/outputs/RV5-B-A05-source-identity.json",
  "RV5-B-A08": "B-trust-security/evidence/outputs/RV5-B-A08-build-image-selects-bytes.json",
  "RV5-B-A09": "B-trust-security/evidence/outputs/RV5-B-A09-floor-class-kernels.json",
  "RV5-B-A12": "B-trust-security/evidence/outputs/RV5-B-A12-machine-classes.json",
  "RV5-D-A01": "D-synthesis/evidence/outputs/RV5-D-A01-registered-content-not-first-hand.json",
  "RV5-D-A03": "D-synthesis/evidence/outputs/RV5-D-A03-user-writable-install-anchoring.json",
  "RV5-D-A04": "D-synthesis/evidence/outputs/RV5-D-A04-conformance-vector-gaps.json",
  "RV5-D-A05": "D-synthesis/evidence/outputs/RV5-D-A05-forward-compat-new-constitutional-file.json",
  "RV5-D-A07": "D-synthesis/evidence/outputs/RV5-D-A07-plan-regression-detection.json",
}
for k, b in pr.items():
    res[k] = cmp(os.path.join(S, "runs-r5probes", k + ".json"), os.path.join(r5, b))
print(json.dumps(res, indent=1))
