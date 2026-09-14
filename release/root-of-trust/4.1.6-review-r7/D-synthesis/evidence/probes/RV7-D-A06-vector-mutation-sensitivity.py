#!/usr/bin/env python3
"""RV7-D-A06 (AR-0022, synthesis reviewer D, held-out) — can the implementation plan's shared conformance vectors detect regressions
that are NOT the architect's own flag mutants?

The pack names FA7 S4 (R1–R16), CUR7, ADM7 and PROF7 shapes as the shared conformance vectors both executors must pass (`31`
R-ADM-14, `35` CC-8). The architect's mutation analysis (FA7 S7, CUR7, ADM7) uses `flags` that the architect chose. This probe makes
code-level mutants of a scratch COPY of `gov_admit_reference_r7.py` at points drawn from this review's attack classes and the four R2
closures, runs the four instruments unmodified against each copy, and records whether any verdict leaf changes (detected) or not
(survives). The committed executor and instruments are never modified.
Usage: RV7-D-A06-vector-mutation-sensitivity.py <export-root> <scratch>   (JSON on stdout)
"""
import json, os, shutil, subprocess, sys
sys.dont_write_bytecode = True
X = os.path.abspath(sys.argv[1])
S = os.path.abspath(sys.argv[2])
PACK = os.path.join(X, "release", "root-of-trust", "4.1.6")
EXE = "gov_admit_reference_r7.py"
MUTANTS = [
    ("M01", "C3 proof need not name the effective state (24 R-CUR-1/2)", 'anchor.get("names_effective_state") and ts(now)', 'ts(now)'),
    ("M02", "C3 currency window 30 days instead of 24 h (R-ANC-4)", "C3_CURRENCY = timedelta(hours=24)", "C3_CURRENCY = timedelta(days=30)"),
    ("M03", "admission state age 7 days instead of 24 h (FC-9)", "ADMISSION_STATE_MAX_AGE = timedelta(hours=24)", "ADMISSION_STATE_MAX_AGE = timedelta(days=7)"),
    ("M04", "re-admission ignores a held negative for the candidate binary only (AP-R4)", 'if use_store and D in Nh:', 'if False and use_store and D in Nh:'),
    ("M05", "security minimum ignores security_relevant_change registrations (OP-11 (b), AP-SEC)", '[r["sequence"] for r in ref_regs if r.get("security_relevant_change")]', '[]'),
    ("M06", "custodian publishes a descendant that drops revocations (R-FCS-2 (d))", 'for fld in ("revocations", "registrations", "published_binaries"):', 'for fld in ("registrations", "published_binaries"):'),
    ("M07", "floors read from the protected store only (account-store restrictors ignored, 24 §8)", "for base in (protected_store(root_dir, lineage), account_store(root_dir, lineage)):", "for base in (protected_store(root_dir, lineage),):"),
    ("M08", "state codes of the two sources need not agree (FC-4′)", "if len(set(trust_codes)) != 1 or len(set(state_codes)) != 1:", "if len(set(trust_codes)) != 1:"),
    ("M09", "admission record expiry ignored at use (OP-14 (b), GB-2′)", 'if ts(rec["valid_until"]) < ts(now):', 'if False:'),
    ("M10", "revoked binary still runs C1–C2 (OP-15 (a), GB-3′)", "if own in set(held_negatives):", 'if own in set(held_negatives) and action not in ("C1", "C2"):'),
    ("M11", "publication of the digest not required (AP-7)", 'if D not in set(tp.get("published_binaries", [])):', "if False:"),
    ("M12", "first-contact authority below the held sequence accepted (AP-R3)", 'if fp.get("fca_sequence", 0) < held.get("fca_sequence", 0):', "if False:"),
    ("M13", "CI anchors get the workstation 90-day validity (R-ANC-3)", 'ANCHOR_VALIDITY[anchor["class"]]', 'ANCHOR_VALIDITY["workstation"]'),
    ("M14", "FCA root threshold checked under any chain version, not the one it names (FC-5′)", 'for c in chain.values() if c["payload"].get("version") == fp.get("root_version"))', "for c in chain.values())"),
    ("M15", "clock skew 30 days (R-CLK-1)", "CLOCK_SKEW = timedelta(seconds=300)", "CLOCK_SKEW = timedelta(days=30)"),
    ("M16", "admitter revoked in the selected state not refused (FC-8′)", "if evaluator_digest in N:", "if False:"),
    ("M17", "TCB-location predicate not applied to C3 and ceremonies (GB-4′)", "if not protected:", "if False:"),
    ("M18", "two verification records need only distinct keys (OP-8, AP-5)", 'if sp.get("verifier_execution_id") in vexec or sp.get("verification_report_digest") in vrep or (sk & vkeys):', "if (sk & vkeys):"),
    ("M19", "first-admission marker never written (every admission moves the account store aside)", "        if first:\n            json.dump(", "        if False:\n            json.dump("),
    ("M20", "evaluator binding not enforced (FC-8′ ADMITTER_NOT_LISTED)", '!= evaluator_digest and not flags.get("skip_evaluator_binding")', '!= evaluator_digest and False'),
    ("M21", "trust-state threshold 1 in the custodian's verification only (R-FCS-2 (a))", 'if rv not in chain or not meets(ver, tss, chain[rv]["payload"], "trust-state", revoked, flags)[0]:', 'if rv not in chain or not signers(ver, tss, chain[rv]["payload"], revoked, flags):'),
    ("M22", "registration equivocation not refused (AP-5)", 'if len(by_rid[reg["payload"]["release_id"]]) > 1:', "if False:"),
]
INSTR = [("FA7", "FA7-first-contact-authority.py", "FA7_SCRATCH"), ("CUR7", "CUR7-first-contact-currency.py", "CUR7_SCRATCH"),
         ("ADM7", "ADM7-admission-stores.py", "ADM7_SCRATCH"), ("PROF7", "PROF7-profile-conformance.py", "PROF7_SCRATCH")]


def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, p + "[%d]" % i)
    else:
        yield p, o


def tree(mid):
    root = os.path.join(S, "mut", mid)
    pk = os.path.join(root, "release", "root-of-trust", "4.1.6")
    os.makedirs(os.path.join(pk, "evidence"))
    for e in os.listdir(PACK):
        if e != "evidence":
            os.symlink(os.path.join(PACK, e), os.path.join(pk, e))
    for e in os.listdir(os.path.join(PACK, "evidence")):
        if e != "r7":
            os.symlink(os.path.join(PACK, "evidence", e), os.path.join(pk, "evidence", e))
    shutil.copytree(os.path.join(PACK, "evidence", "r7"), os.path.join(pk, "evidence", "r7"))
    for e in os.listdir(X):
        if e != "release":
            os.symlink(os.path.join(X, e), os.path.join(root, e))
    return os.path.join(pk, "evidence", "r7")


def run(r7, mid):
    res = {}
    for name, script, var in INSTR:
        w = os.path.join(S, "work", mid, name)
        os.makedirs(w, exist_ok=True)
        env = {"PATH": "/usr/bin:/bin", "HOME": os.path.join(S, "home"), "TMPDIR": os.path.join(S, "tmp"), "PYTHONDONTWRITEBYTECODE": "1", var: w}
        p = subprocess.run(["python3", "-B", script], cwd=r7, env=env, capture_output=True, text=True, timeout=900)
        try:
            v = json.loads(p.stdout).get("verdicts")
        except Exception:
            v = None
        res[name] = {"rc": p.returncode, "verdicts": dict(leaves(v)) if v is not None else None, "stderr_tail": p.stderr[-300:] if p.returncode else ""}
    return res


out = {"probe": "RV7-D-A06 conformance-vector mutation sensitivity (AR-0022)", "instruments": [i[0] for i in INSTR], "mutants": {}}
r7c = tree("M00")
control = run(r7c, "M00")
committed = {}
for name, script, _ in INSTR:
    committed[name] = dict(leaves(json.load(open(os.path.join(PACK, "evidence", "r7", script.replace(".py", ".json"))))["verdicts"]))
out["control_equals_committed_verdicts"] = {n: control[n]["verdicts"] == committed[n] for n in committed}
for mid, desc, old, new in MUTANTS:
    r7 = tree(mid)
    p = os.path.join(r7, EXE)
    code = open(p).read()
    n = code.count(old)
    if n != 1:
        out["mutants"][mid] = {"description": desc, "error": "needle count %d" % n}
        continue
    open(p, "w").write(code.replace(old, new))
    res = run(r7, mid)
    det = {}
    for name in res:
        if res[name]["rc"] != 0 or res[name]["verdicts"] is None:
            det[name] = ["rc=%d" % res[name]["rc"]]
        else:
            det[name] = sorted(k for k in set(control[name]["verdicts"]) | set(res[name]["verdicts"]) if control[name]["verdicts"].get(k) != res[name]["verdicts"].get(k))
    out["mutants"][mid] = {"description": desc, "detected_by": {k: v for k, v in det.items() if v}, "detected": any(det.values())}
surv = sorted(m for m, v in out["mutants"].items() if not v.get("detected"))
out["summary"] = {"mutants": len(MUTANTS), "detected": len(MUTANTS) - len(surv), "surviving": surv,
                  "surviving_descriptions": {m: out["mutants"][m]["description"] for m in surv}}
print(json.dumps(out, indent=1, sort_keys=True).replace(S, "<s>"))
