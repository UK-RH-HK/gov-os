import json, re, hashlib, sys, os
S = "<scratchpad>"
P = S + "/ar-0014/export/release/root-of-trust/4.1.6/evidence"
O = S + "/ar-0014/runs/arch"
pairs = {
 "CSI5-selftest.json": P+"/r5/CSI5-selftest.json",
 "CSI5-CSI-check-framework.json": P+"/r5/CSI5-CSI-check-framework.json",
 "CSI5-CSI-check-release-4.1.5.json": P+"/r5/CSI5-CSI-check-release-4.1.5.json",
 "CSI5-CSI-check-legacy-4.1.2.json": P+"/r5/CSI5-CSI-check-legacy-4.1.2.json",
 "CSI5-CSI-check-legacy-4.1.3.json": P+"/r5/CSI5-CSI-check-legacy-4.1.3.json",
 "CSI5-CSI-check-legacy-4.1.4.json": P+"/r5/CSI5-CSI-check-legacy-4.1.4.json",
 "P1r4-project-strength-and-absence.json": P+"/P1r4-project-strength-and-absence.json",
 "P4r4-trust-state-model.json": P+"/P4r4-trust-state-model.json",
 "P4r5-conformance-oracle.json": P+"/r5/P4r5-conformance-oracle.json",
 "DA03r5-oracle-regression-sensitivity.json": P+"/r5/DA03r5-oracle-regression-sensitivity.json",
 "FA5-first-admission.run1.json": P+"/r5/FA5-first-admission.json",
 "FA5-first-admission.run2.json": P+"/r5/FA5-first-admission.json",
 "REG5-release-scoped-registration.json": P+"/r5/REG5-release-scoped-registration.json",
 "CS5-tcb-capability-sets.json": P+"/r5/CS5-tcb-capability-sets.json",
 "SRC5-stdout.json": P+"/r5/SRC5-source-identity.json",
}
R4B = S + "/ar-0014/export/release/root-of-trust/4.1.6-review-r4/B-trust-security/evidence"
for n in ["RV4-B-M-reference-model.json","RV4-B-arch-functions.json","RV4-B-surface-probes.json"]:
    pairs[n] = R4B + "/outputs/" + n if os.path.exists(R4B+"/outputs/"+n) else R4B + "/" + n
for n in ["RV3-B-A01-precedence-immutable","RV3-B-CSI-injections","RV3-D-precedence-lattice"]:
    cands=[R4B+"/r3-probe-copies/outputs/"+n+".json", R4B+"/outputs/r3copy-"+n+".json", R4B+"/r3-probe-copies/"+n+".json"]
    pairs["r3copy-"+n+".json"] = next((c for c in cands if os.path.exists(c)), cands[0])
def norm(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"/tmp/claude-1000/[^\"\s,]*?/scratchpad/ar-00\d\d/[^\"\s,]*", "<scratch>", t)
    t = re.sub(r"<scratch>[^\"\s,]*", "<scratch>", t)
    t = re.sub(r"/tmp/[A-Za-z0-9_./-]*", "<tmp>", t)
    t = re.sub(r"\"(elapsed|elapsed_seconds|generated_utc|seconds)\"\s*:\s*[0-9.\"TZ:-]+", "\"elapsed\":0", t)
    return t
res = {}
for mine, theirs in pairs.items():
    a = os.path.join(O, mine)
    if not os.path.exists(theirs):
        res[mine] = {"committed": theirs, "status": "committed file not found"}; continue
    ba, bb = open(a,"rb").read(), open(theirs,"rb").read()
    same = ba == bb
    ns = norm(ba) == norm(bb)
    r = {"byte_identical": same, "identical_after_path_normalisation": ns, "rerun_sha256": hashlib.sha256(ba).hexdigest(), "committed_sha256": hashlib.sha256(bb).hexdigest()}
    if not ns:
        try:
            ja, jb = json.loads(ba), json.loads(bb)
            diffkeys = [k for k in set(ja)|set(jb) if json.dumps(ja.get(k),sort_keys=True) != json.dumps(jb.get(k),sort_keys=True)] if isinstance(ja, dict) else "list"
            r["differing_top_level_keys"] = diffkeys
        except Exception as e:
            r["json_error"] = str(e)
    res[mine] = r
print(json.dumps(res, indent=1))
