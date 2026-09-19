#!/usr/bin/env python3
"""P2-AR-0022 (integration builder) — the G0 registration of the subcommands other round-1 workstreams added
(P2-HO-0019 step 3), observed through the integrated binary; plus the kernel-payload question for WS-2's
framework/health/SKILL_SCENARIO_CHECKS.yaml (step 4, fourth bullet). Integration evidence only (Contract v3 O3).

G1  every new label is classified exactly as registered (read from `control::COMMAND_GUARDS` via the source, and
    observed through the binary): under FREEZE_WRITES and PAUSE each Write label is refused (FROZEN / PAUSED, exit 4)
    and changes no governed file; each Read label still runs (it is not refused by the freeze) and changes no
    governed file (spec/, governance/, framework.json and every tracked file; the runtime dir is reported, not graded).
G2  authority: `health skills --record` (record_skill_binding, L3) is refused for an L0 role and for an undeclared
    invocation; the evidence-recording labels (record_audit, L0) are authorised exactly as WS-3's `audit` (same class):
    a declared L0 auditor may record evidence, and an undeclared invocation carries L0 (WS-3 BC-P2-08).
G3  `oracle format|validate` is outside every project (no role, no project needed) and read-only.
K1  an installed project's kernel carries no `health/` (KERNEL.yaml payload_dirs unchanged): KERNEL_MANIFEST.json lists
    no health file, `gov kernel verify` is ok, and `gov health skills` still executes the kernel skills' executable
    scenarios from the copy compiled into the runtime (IP-WS02-16: registration is not needed for installed projects).

Usage: GOV=<gov> P2AR0022_SCRATCH=<dir> python3 new_labels_g0_probe.py
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GOV = os.environ.get("GOV", os.path.join(WT, "target", "release", "gov"))
SCR = os.environ.get("P2AR0022_SCRATCH") or tempfile.mkdtemp(prefix="p2ar0022-g0-")
os.makedirs(SCR, exist_ok=True)
RESULTS = []


def check(name, ok, what, detail=None):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name} {'PASS' if ok else 'FAIL'} {what}", flush=True)
    if detail is not None:
        print("      detail:", json.dumps(detail, sort_keys=True, default=str)[:2500], flush=True)


def env_for(root, role_env=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
    e.update({"GOV_CANONICAL_ROOT": WT, "XDG_STATE_HOME": root + ".machine", "XDG_CACHE_HOME": root + ".cache",
              "HOME": root + ".home", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "p",
              "GIT_AUTHOR_EMAIL": "p@example.invalid", "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"})
    os.makedirs(e["HOME"], exist_ok=True)
    return e


def gov(root, *args, role="orchestrator", session="S-g0", cwd=None):
    cmd = [GOV, "--json"]
    if root:
        cmd += ["--root", root]
    cmd += ["--session", session]
    if role:
        cmd += ["--role", role]
    cmd += list(args)
    p = subprocess.run(cmd, capture_output=True, text=True, env=env_for(root or os.path.join(SCR, "noproj")), cwd=cwd or SCR)
    try:
        v = json.loads(p.stdout)
    except Exception:
        v = {"ok": False, "error": {"code": "NON_JSON", "message": (p.stdout + p.stderr)[-400:]}}
    v["_exit"] = p.returncode
    return v


def code(v):
    return (v.get("error") or {}).get("code")


def governed_hash(root):
    """Governed state: every file under spec/ and governance/, framework.json, and every tracked file."""
    h = hashlib.sha256()
    tracked = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True).stdout.split()
    paths = set(tracked)
    for base in ("spec", "governance"):
        for d, _, fs in os.walk(os.path.join(root, base)):
            for f in fs:
                paths.add(os.path.relpath(os.path.join(d, f), root))
    if os.path.exists(os.path.join(root, "framework.json")):
        paths.add("framework.json")
    for rel in sorted(paths):
        p = os.path.join(root, rel)
        h.update(rel.encode())
        h.update(open(p, "rb").read() if os.path.isfile(p) else b"<absent>")
    return h.hexdigest()


def runtime_hash(root):
    h = hashlib.sha256()
    rd = os.path.join(root, ".governance-runtime")
    for d, _, fs in sorted(os.walk(rd)):
        for f in sorted(fs):
            p = os.path.join(d, f)
            if "telemetry" in p:
                continue
            h.update(os.path.relpath(p, rd).encode())
            h.update(open(p, "rb").read())
    return h.hexdigest()


# ---- the registration, read from the source (what the binary was built from)
src = open(os.path.join(WT, "runtime/src/orchestration/control.rs")).read()
guards = {m.group(2): (m.group(1), m.group(3), m.group(4)) for m in
          re.finditer(r'\b(g|outside)\("([^"]+)",\s*(?:"([^"]*)"|[^)]*?),?\s*(Read|Write)?\)', src)}
NEW_WRITE = {"verify product": "record_audit", "health run": "record_audit", "health product": "record_audit",
             "health close-check": "record_audit", "health skills --record": "record_skill_binding"}
NEW_READ = ["context manifest", "context verify", "context show", "context receipt", "artefact show", "artefact check",
            "artefact lineage", "health run --no-persist", "health status", "health checks", "health history", "health show",
            "health guard", "health currency", "health skills"]
NEW_OUTSIDE = ["oracle format", "oracle validate"]
reg = {l: guards.get(l) for l in list(NEW_WRITE) + NEW_READ + NEW_OUTSIDE}
check("G0.registered",
      all(reg[l] and reg[l][0] == "g" and reg[l][2] == "Write" and reg[l][1] == c for l, c in NEW_WRITE.items())
      and all(reg[l] and reg[l][0] == "g" and reg[l][2] == "Read" and reg[l][1] == "read" for l in NEW_READ)
      and all(reg[l] and reg[l][0] == "outside" for l in NEW_OUTSIDE),
      "every label the integration registered carries the class stated in the integration report", reg)

# ---- a project installed from the canonical source
root = os.path.join(SCR, "proj")
if os.path.exists(root):
    shutil.rmtree(root)
shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), root)
e = env_for(root)
for a in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "fixture"]):
    subprocess.run(["git", *a], cwd=root, env=e, capture_output=True)
r = gov(root, "init", "--name", "g0", "--alias", "g0")
assert r.get("ok"), r
r = gov(root, "task", "create", "--id", "TASK-G0", "--class", "documentation", "--objective", "g0 probe", "--status", "READY")
assert r.get("ok"), r
gov(root, "rebuild-memory")
gov(root, "context", "compile", "TASK-G0")
rep = os.path.join(SCR, "g0-report.json")
json.dump({"work_completed": "x", "files_changed": [], "tests": {"status": "not_applicable_with_reason", "reason": "probe"}}, open(rep, "w"))
receipt = os.path.join(SCR, "g0-receipt.json")
json.dump({"task": "TASK-G0", "status": "completed", "inputs_consumed": [], "outputs_produced": []}, open(receipt, "w"))
oracle_doc = os.path.join(WT, "release/capability-baseline/repair-1/ws01-12/evidence/bc-p2-51/samples/format-sample.oracle.json")
subprocess.run(["git", "-C", root, "add", "-A"], env=e, capture_output=True)
subprocess.run(["git", "-C", root, "commit", "-qm", "installed"], env=e, capture_output=True)

WRITE_ARGS = {"verify product": ["verify", "product"], "health run": ["health", "run"],
              "health product": ["health", "product"], "health close-check": ["health", "close-check", "TASK-G0", "--report", rep],
              "health skills --record": ["health", "skills", "--record"]}
READ_ARGS = {"context manifest": ["context", "manifest", "TASK-G0"], "context verify": ["context", "verify", "TASK-G0"],
             "context show": ["context", "show", "TASK-G0"], "context receipt": ["context", "receipt", "TASK-G0", "--file", receipt],
             "artefact show": ["artefact", "show", "TASK-G0"], "artefact check": ["artefact", "check"],
             "artefact lineage": ["artefact", "lineage", "TASK-G0"], "health run --no-persist": ["health", "run", "--no-persist"],
             "health status": ["health", "status"], "health checks": ["health", "checks"], "health history": ["health", "history"],
             "health show": ["health", "show", "HR-none"], "health guard": ["health", "guard", "task.create"],
             "health currency": ["health", "currency"], "health skills": ["health", "skills"]}

for mode, refusal in (("freeze-writes", "FROZEN"), ("pause", "PAUSED")):
    assert gov(root, mode, "--reason", "g0 probe").get("ok")
    rows = {}
    for label, args in WRITE_ARGS.items():
        before = governed_hash(root)
        v = gov(root, *args)
        rows[label] = {"code": code(v), "exit": v["_exit"], "governed_changed": governed_hash(root) != before}
    check(f"G1.{mode}.writes-refused", all(x["code"] == refusal and x["exit"] == 4 and not x["governed_changed"] for x in rows.values()),
          f"under {mode.upper()} every newly registered Write label is refused {refusal} (exit 4) and changes no governed file", rows)
    rows = {}
    for label, args in READ_ARGS.items():
        before, rbefore = governed_hash(root), runtime_hash(root)
        v = gov(root, *args)
        rows[label] = {"ok": v.get("ok"), "code": code(v), "governed_changed": governed_hash(root) != before,
                       "runtime_dir_changed": runtime_hash(root) != rbefore}
    check(f"G1.{mode}.reads-run", all(x["code"] not in ("FROZEN", "PAUSED", "G0_UNCLASSIFIED") and not x["governed_changed"] for x in rows.values()),
          f"under {mode.upper()} every newly registered Read label runs (not refused by the emergency control) and changes no governed file", rows)
    assert gov(root, "resume").get("ok")

# ---- authority
aud = gov(root, "health", "skills", "--record", role="independent-auditor")
und = gov(root, "health", "skills", "--record", role=None)
check("G2.record-skill-binding-L3", code(aud) == "AUTHORITY_DENIED" and code(und) == "AUTHORITY_DENIED",
      "`health skills --record` (record_skill_binding, L3) is refused for an L0 role and for an undeclared invocation",
      {"independent-auditor": code(aud), "undeclared": code(und)})
rows = {}
denied = lambda v: code(v) == "AUTHORITY_DENIED"  # noqa: E731
for label, args in (("audit (reference: WS-3's record_audit label)", ["audit"]), ("verify product", WRITE_ARGS["verify product"]),
                    ("health run", WRITE_ARGS["health run"]), ("health product", WRITE_ARGS["health product"]),
                    ("health close-check", WRITE_ARGS["health close-check"])):
    v = gov(root, *args, role="independent-auditor")
    u = gov(root, *args, role=None)
    rows[label] = {"L0 declared": v.get("ok") or code(v), "undeclared (WS-3: L0)": u.get("ok") or code(u),
                   "L0 denied": denied(v), "undeclared denied": denied(u)}
ref = rows["audit (reference: WS-3's record_audit label)"]
check("G2.record-audit-L0", all(not x["L0 denied"] and x["undeclared denied"] == ref["undeclared denied"] for x in rows.values()),
      "the evidence-recording labels carry record_audit (L0) exactly like WS-3's `audit`: a declared L0 auditor is not refused, and an "
      "undeclared invocation (which WS-3 gives L0, no privileged authority) is treated exactly as for `audit`; the command's own "
      "result (UNHEALTHY, PRODUCT_TESTS_FAILED on the fixture's deliberately failing test) is not an authority decision", rows)

# ---- outside: the oracle tool needs no project and no role
elsewhere = tempfile.mkdtemp(prefix="noproj-", dir=SCR)
f1 = gov(None, "oracle", "format", role=None, cwd=elsewhere)
f2 = gov(None, "oracle", "validate", oracle_doc, role=None, cwd=elsewhere)
check("G3.oracle-outside", f1.get("ok") and f2.get("ok") and not os.listdir(elsewhere),
      "`oracle format|validate` run with no project and no role declared, and write nothing",
      {"format": f1.get("ok") or code(f1), "validate": f2.get("ok") or code(f2), "files_created": os.listdir(elsewhere)})

# ---- K1: framework/health is not in the installed kernel, and is not needed there
man = json.load(open(os.path.join(root, "governance/kernel/KERNEL_MANIFEST.json")))
files = man.get("files") or {}
names = list(files.keys()) if isinstance(files, dict) else [x.get("path") for x in files]
kv = gov(root, "kernel", "verify")
sk = gov(root, "health", "skills")
det = (sk.get("result") or {}).get("detail") or {}
check("K1.health-not-installed-not-needed",
      not any(str(n).startswith("health/") for n in names) and not os.path.exists(os.path.join(root, "governance/kernel/health"))
      and (kv.get("result") or {}).get("ok") is True and det.get("executed_passed", 0) >= 5 and det.get("executed_failed", 1) == 0,
      "the installed kernel carries no health/ (payload_dirs unchanged), kernel verify is ok, and `gov health skills` executes the "
      "kernel skills' executable scenarios from the compiled copy",
      {"manifest_health_files": [n for n in names if str(n).startswith("health/")], "kernel_verify_ok": (kv.get("result") or {}).get("ok"),
       "executed_passed": det.get("executed_passed"), "executed_failed": det.get("executed_failed"),
       "declared_not_executed": det.get("declared_not_executed"), "unexecutable": det.get("unexecutable"), "runner": det.get("runner")})

print("\nSUMMARY checks=%d pass=%d fail=%d failed=%s" % (len(RESULTS), sum(1 for _, o in RESULTS if o),
                                                         sum(1 for _, o in RESULTS if not o), [n for n, o in RESULTS if not o]))
