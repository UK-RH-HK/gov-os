#!/usr/bin/env python3
"""P2-AR-0015 (WS-2 repair builder) supplementary scenarios — builder regression evidence only (Contract v3 O3).

Drives `target/release/gov` of this worktree on disposable copies of fixtures/greenfield, one scenario per project,
and prints CHECK lines. Covers what the audit-of-record probes cannot observe without new surfaces:

  S-A  scheduler: impacted selection, cache reuse, concurrency, currency re-established by `gov health run`
  S-B  isolation: a deep check never touches the live state.db
  S-C  hard-block vs warning: a declared hard-block refuses governed operations (G0 guard) and clears when repaired
  S-D  health-result provenance: doctor and suite results persisted with tier, checks, inputs, runtime, repository,
       actor and time
  S-E  product tests: per-family governed evidence, failure changes health, close verified from evidence
  S-F  task-close currency gate: governance-affecting by class; stale evidence re-checked before reliance
  S-G  skill regression: executable scenarios, false expectation reported, version bound to content
  S-H  tier contract: tiers, declared checks, tier-scoped run
  S-I  runtime identity: a modified gov binary makes the green record stale

Run from anywhere:  WS02_SCRATCH=<dir> python3 WS02-supplementary.py
Environment: WS02_SCRATCH (default: mkdtemp), GOV (default <worktree>/target/release/gov), GOV_KERNEL_CACHE honoured.
"""
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GOV = os.environ.get("GOV", os.path.join(WT, "target", "release", "gov"))
SCRATCH = os.environ.get("WS02_SCRATCH") or tempfile.mkdtemp(prefix="ws02-")
os.makedirs(SCRATCH, exist_ok=True)
RESULTS = []


def check(name, ok, what, detail=None):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name} {'PASS' if ok else 'FAIL'} {what}")
    if detail is not None:
        print("      detail:", json.dumps(detail, sort_keys=True, default=str)[:1500])


def note(msg):
    print("#", msg)


def run(root, *args, gov=None, role="orchestrator", session="S-ws02"):
    env = dict(os.environ)
    env.pop("GOV_ROLE", None)
    env.pop("GOV_SESSION", None)
    env["GOV_CANONICAL_ROOT"] = WT
    env["XDG_STATE_HOME"] = root + ".machine"
    env["PATH"] = os.path.expanduser("~/.cargo/bin") + os.pathsep + env.get("PATH", "")
    t0 = time.time()
    p = subprocess.run([gov or GOV, "--json", "--root", root, "--session", session, "--role", role, *args],
                       capture_output=True, text=True, env=env)
    ms = int((time.time() - t0) * 1000)
    try:
        e = json.loads(p.stdout)
    except Exception:
        e = {"ok": False, "error": {"code": "NON_JSON", "message": p.stdout[:300] + p.stderr[:300]}}
    e["_exit"] = p.returncode
    e["_ms"] = ms
    return e


def body(e):
    return e.get("result") if e.get("ok") else ((e.get("error") or {}).get("details") or {})


def code(e):
    return None if e.get("ok") else (e.get("error") or {}).get("code")


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, capture_output=True)


def mkproj(name):
    root = os.path.join(SCRATCH, name)
    shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), root)
    git(root, "init", "-q")
    git(root, "config", "user.email", "ws02@example.invalid")
    git(root, "config", "user.name", "ws02")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "fixture")
    e = run(root, "init", "--name", name, "--alias", "ws02-" + name)
    assert e.get("ok"), e
    git(root, "add", "-A")
    git(root, "commit", "-qm", "gov init")
    return root


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def d021(root):
    b = body(run(root, "doctor"))
    return [c for c in b.get("checks", []) if c["id"] == "D021"][0]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


print(f"# gov: {GOV} sha256 {sha(GOV)}\n# scratch: {SCRATCH}")

# ---------------------------------------------------------------------------------------------------------- S-A
print("\n=== S-A scheduler: impacted selection, cache reuse, concurrency, currency re-established")
R = mkproj("sa")
first = run(R, "health", "run")
check("S-A.1", first.get("ok") and body(first)["complete"], "a full scheduler run completes the suite", {k: body(first).get(k) for k in ("verdict", "complete", "summary", "parallelism")})
check("S-A.2", len(body(first)["parallelism"]["threads_used"]) > 1, "independent checks ran on more than one worker thread", body(first)["parallelism"])
second = run(R, "health", "run")
s2 = body(second)["summary"]
check("S-A.3", s2["reused"] >= 20 and set(s2["executed_checks"]) <= {"concurrency_claims", "fresh_agent_reconstruction", "audit_reproducibility"},
      "an identical second run is served from the cache (only the never-cached, time/session-dependent checks execute)", {"executed": s2["executed_checks"], "reused": s2["reused"], "ms_first": first["_ms"], "ms_second": second["_ms"]})
write(R, "spec/decisions/D-0001.yaml", "id: D-0001\ntype: decision\ntitle: t\nstatus: ACTIVE\nquestion: q\nchosen_option: A\n")
run(R, "rebuild-memory", "--incremental")
git(R, "add", "-A"); git(R, "commit", "-qm", "decision")
run(R, "health", "run")
open(os.path.join(R, "spec/decisions/D-0001.yaml"), "a").write("\n")  # trivial whitespace-only mutation
run(R, "rebuild-memory", "--incremental")
cur = body(run(R, "health", "currency"))["currency"]
check("S-A.4", not cur["current"] and {c["class"] for c in cur["changed_classes"]} >= {"spec_decisions"},
      "a one-line decision change makes the green record stale and names the changed input classes", cur["changed_classes"])
third = run(R, "health", "run")
s3 = body(third)["summary"]
check("S-A.5", 0 < s3["executed"] < 25 and s3["reused"] > 0 and "command_contract_consistency" in s3["reused_checks"] and "schema_invariants" in s3["executed_checks"],
      "after the trivial mutation only the checks whose declared inputs changed re-execute; the rest are reused", {"executed": s3["executed_checks"], "reused": s3["reused_checks"], "ms": third["_ms"]})
check("S-A.6", d021(R)["ok"], "the impacted re-check re-established currency (D021 current) without a full serial suite", d021(R)["message"])

# ---------------------------------------------------------------------------------------------------------- S-B
print("\n=== S-B isolation: a deep check never touches the live state.db")
R = mkproj("sb")
db = os.path.join(R, ".governance-runtime", "state.db")
st = lambda: (os.stat(db).st_ino, sha(db))
before = st()
deep = run(R, "audit", "--deep", "--no-persist")
after = st()
rr = body(deep)["families"]["recovery_rebuild"]["detail"]
check("S-B.1", before == after and rr.get("isolated_in_sandbox") and rr.get("rebuild_1") == rr.get("rebuild_2"),
      "two full rebuilds ran in a disposable sandbox; the live state.db is byte-identical (same inode, same hash)", {"before": before, "after": after, "recovery_rebuild": rr})
conn = sqlite3.connect(db); arts0 = {r[0]: r[1] for r in conn.execute("SELECT path, content_hash FROM artifacts")}; conn.close()
persisted = run(R, "audit", "--deep")
conn = sqlite3.connect(db); arts1 = {r[0]: r[1] for r in conn.execute("SELECT path, content_hash FROM artifacts")}; conn.close()
changed = sorted(set(k for k in set(arts0) | set(arts1) if arts0.get(k) != arts1.get(k)))
check("S-B.2", changed == [f"spec/audits/{body(persisted)['audit']}.yaml"],
      "with persistence the only live index change is the new governed evidence record itself", {"changed_artifacts": changed})
sandboxes = os.path.join(R, ".governance-runtime", "health", "sandboxes")
check("S-B.3", not os.path.isdir(sandboxes) or not os.listdir(sandboxes), "sandboxes are removed after the run", os.listdir(sandboxes) if os.path.isdir(sandboxes) else [])

# ---------------------------------------------------------------------------------------------------------- S-C
print("\n=== S-C hard-block vs warning")
R = mkproj("sc")
chk = body(run(R, "health", "checks"))
modes = {c["id"]: c["enforcement"]["mode"] for c in chk["checks"]}
check("S-C.1", modes.get("D011") == "hard-block" and modes.get("index_freshness") == "warning" and modes.get("path_map_compliance") == "hard-block",
      "every check declares hard-block or warning", {k: modes[k] for k in ("D011", "D012", "path_map_compliance", "graph_integrity", "product_test_health", "index_freshness", "D021")})
write(R, "src/creds.rs", 'pub const K: &str = "AKIAIOSFODNN7EXAMPLE";\n')
doc = run(R, "doctor")
stt = body(run(R, "health", "status"))
check("S-C.2", body(doc).get("verdict") == "UNHEALTHY" and stt["state"] == "RED" and any(b["check"] == "D011" for b in stt["blocks"]),
      "a critical secret finding makes the health state RED with an active hard-block", {"state": stt["state"], "blocks": [(b["check"], b["severity"], b["operations"]) for b in stt["blocks"]][:4]})
for op in ("task.create", "task.claim", "task.close", "cit.propose"):
    g = run(R, "health", "guard", op)
    check(f"S-C.3[{op}]", code(g) == "HEALTH_HARD_BLOCK", f"the G0 guard refuses {op} while the hard-block is active", (g.get("error") or {}).get("message", "")[:200])
g = run(R, "health", "guard", "checkpoint.create")
check("S-C.4", g.get("ok"), "a remedy/continuity operation outside the hard-block vocabulary stays available", body(g))
os.remove(os.path.join(R, "src/creds.rs"))
g = run(R, "health", "guard", "task.create")
check("S-C.5", g.get("ok") and "doctor" in body(g).get("reevaluated", []), "after the repair the guard re-evaluates the stale blocking check and allows the operation", body(g))
write(R, "spec/tasks/TASK-0801.yaml", "id: TASK-0801\ntype: task\ntitle: a\nstatus: ACTIVE\ntask_status: READY\nclass: documentation\nobjective: o\ndependencies: [TASK-0802]\nallowed_paths: ['docs/**']\n")
write(R, "spec/tasks/TASK-0802.yaml", "id: TASK-0802\ntype: task\ntitle: b\nstatus: ACTIVE\ntask_status: READY\nclass: documentation\nobjective: o\ndependencies: [TASK-0801]\nallowed_paths: ['docs/**']\n")
run(R, "rebuild-memory", "--incremental")
hr = run(R, "health", "run")
gc = run(R, "health", "guard", "task.claim")
gcr = run(R, "health", "guard", "task.create")
check("S-C.6", code(hr) == "UNHEALTHY" and code(gc) == "HEALTH_HARD_BLOCK" and gcr.get("ok"),
      "a DAG cycle (graph_integrity high) refuses task.claim, which it governs, but not task.create, which it does not", {"claim": (gc.get("error") or {}).get("message", "")[:160]})
doc = body(run(R, "doctor"))
d031 = [c for c in doc["checks"] if c["id"] == "D031"][0]
check("S-C.7", not d031["ok"], "doctor reports the suite-origin hard-block (D031)", d031["message"][:200])

# ---------------------------------------------------------------------------------------------------------- S-D
print("\n=== S-D health-result provenance")
R = mkproj("sd")
doc = body(run(R, "doctor"))
hid = doc["health_result"]["id"]
res = body(run(R, "health", "show", hid))
need = ["tier", "checks", "inputs", "inputs_hash", "runtime", "repository", "actor", "started_at", "finished_at", "trigger"]
check("S-D.1", all(k in res for k in need) and res["runtime"].get("binary_sha256") and res["repository"].get("git_commit"),
      "a doctor run is persisted as a health result with tier, checks, inputs, runtime identity, repository state, actor and time", {k: (res[k] if k not in ("checks", "inputs") else f"<{len(res[k])} entries>") for k in need})
au = body(run(R, "audit"))
import yaml  # noqa: E402
rec = yaml.safe_load(open(os.path.join(R, "spec/audits", au["audit"] + ".yaml")))
check("S-D.2", all(k in rec for k in ["tier", "checks", "inputs", "inputs_hash", "runtime", "repository", "actor", "run_at", "health_result"]),
      "the governed audit record carries the same provenance", sorted(k for k in rec if k not in ("families", "findings")))
hist = body(run(R, "health", "history", "--limit", "5"))
check("S-D.3", len(hist) >= 2 and {h["surface"] for h in hist} >= {"doctor", "audit"}, "`gov health history` lists the recorded results", [(h["id"], h["surface"], h["tier"], h["verdict"]) for h in hist])

# ---------------------------------------------------------------------------------------------------------- S-E
print("\n=== S-E product tests: per-family governed evidence")
R = mkproj("se")
vp = run(R, "verify", "product")
fams = body(vp).get("families", {})
check("S-E.1", vp.get("ok") and set(fams) >= {"unit", "integration"} and all(f["status"] == "passed" for f in fams.values()),
      "product tests run and are recorded per family", {f: {k: v[k] for k in ("status", "exit", "command")} for f, v in fams.items()})
rec = yaml.safe_load(open(os.path.join(R, "spec/audits", body(vp)["record"] + ".yaml")))
check("S-E.2", rec["scope"] == "product-tests" and rec["state_class"] == "EVIDENCE" and all("key" in f for f in rec["families"].values()),
      "the run is a governed evidence record with a freshness key per family", {"record": rec["id"], "verdict": rec["verdict"]})
testfile = os.path.join(R, "tests/ledger_test.rs")
orig = open(testfile).read()
open(testfile, "w").write(orig.replace("assert_eq!(l.total_cents(), 399);", "assert_eq!(l.total_cents(), 400);"))
vf = run(R, "verify", "product")
check("S-E.3", code(vf) == "PRODUCT_TESTS_FAILED" and vf["_exit"] != 0 and body(vf)["families"]["integration"]["status"] == "failed" and body(vf)["families"]["unit"]["status"] == "passed",
      "a failing family is reported per family and the command fails (non-zero exit)", {"exit": vf["_exit"], "families": {f: v["status"] for f, v in body(vf)["families"].items()}})
run(R, "rebuild-memory", "--incremental")
doc = body(run(R, "doctor"))
d030 = [c for c in doc["checks"] if c["id"] == "D030"][0]
aud = run(R, "audit", "--no-persist")
pth = [f for f in body(aud)["findings"] if f["family"] == "product_test_health" and f["severity"] == "high"]
check("S-E.4", doc["verdict"] == "UNHEALTHY" and not d030["ok"] and code(aud) == "UNHEALTHY" and pth,
      "the failing family changes the health state (doctor D030, audit product_test_health)", {"doctor": doc["verdict"], "D030": d030["message"][:160], "audit": body(aud)["verdict"]})
g_src = run(R, "health", "guard", "task.close", "--paths", "src/lib.rs")
g_doc = run(R, "health", "guard", "task.close", "--paths", "docs/n.md")
check("S-E.5", code(g_src) == "HEALTH_HARD_BLOCK" and g_doc.get("ok"), "the failure refuses the close of work under the family's covered paths only", {"src": code(g_src), "docs": body(g_doc)})
t = body(run(R, "task", "create", "--class", "documentation", "--objective", "docs", "--allowed", "docs/**", "--status", "READY"))["id"]
run(R, "task", "claim", t)
write(R, "docs/n.md", "note\n")
rep = os.path.join(SCRATCH, "se-rep.json")
json.dump({"work_completed": "docs", "files_changed": ["docs/n.md"], "tests": {"status": "passed"}}, open(rep, "w"))
cc = run(R, "health", "close-check", t, "--report", rep)
check("S-E.6", code(cc) == "PRODUCT_TESTS_FAILED", "a self-attested tests.status=passed is refused against the recorded failing evidence", (cc.get("error") or {}).get("message", "")[:220])
open(testfile, "w").write(orig)
vp2 = run(R, "verify", "product")
cc2 = run(R, "health", "close-check", t, "--report", rep)
check("S-E.7", vp2.get("ok") and cc2.get("ok"), "after a passing run is recorded the same claim is verified from evidence", {"close_check": code(cc2) or "allowed"})
open(os.path.join(R, "src/lib.rs"), "a").write("\npub fn later() {}\n")
t2 = body(run(R, "task", "create", "--class", "implementation", "--objective", "impl", "--allowed", "src/**", "--status", "READY"))
t2id = t2.get("id") if isinstance(t2, dict) else None
rep2 = os.path.join(SCRATCH, "se-rep2.json")
json.dump({"work_completed": "impl", "files_changed": ["src/lib.rs"], "tests": {"status": "passed"}}, open(rep2, "w"))
cc3 = run(R, "health", "close-check", t2id or t, "--report", rep2)
check("S-E.8", code(cc3) == "PRODUCT_TEST_EVIDENCE_STALE", "evidence recorded before a covered source change is stale: a passed claim is refused until re-run", (cc3.get("error") or {}).get("message", "")[:220])

# ---------------------------------------------------------------------------------------------------------- S-F
print("\n=== S-F task-close currency gate (governance-affecting by class and by governed inputs)")
R = mkproj("sf")
t = body(run(R, "task", "create", "--class", "governance", "--objective", "arch", "--allowed", "spec/architecture/**", "--status", "READY"))["id"]
git(R, "add", "-A"); git(R, "commit", "-qm", "task")
run(R, "rebuild-memory", "--incremental")
run(R, "health", "run")
run(R, "task", "claim", t)
write(R, "spec/architecture/ARCH-0001.yaml", "id: ARCH-0001\ntype: architecture\ntitle: new architecture\nstatus: ACTIVE\n")
run(R, "rebuild-memory", "--incremental")
check("S-F.1", not d021(R)["ok"], "the green record is stale (an architecture record changed)", d021(R)["message"])
rep = os.path.join(SCRATCH, "sf-rep.json")
json.dump({"work_completed": "arch", "files_changed": ["spec/architecture/ARCH-0001.yaml"], "tests": {"status": "not_applicable_with_reason", "reason": "record"}}, open(rep, "w"))
cc = run(R, "health", "close-check", t, "--report", rep)
b = body(cc)
check("S-F.2", cc.get("ok") and b["governance_affecting"] and b["g2"]["record"] and b["g2"]["summary"]["reused"] > 0,
      "the stale evidence is re-checked before reliance (impacted checks only) and a new green record is written; the close may proceed", {k: b.get(k) for k in ("governance_affecting", "reasons", "g2")})
write(R, "spec/tasks/TASK-0801.yaml", "id: TASK-0801\ntype: task\ntitle: a\nstatus: ACTIVE\ntask_status: READY\nclass: documentation\nobjective: o\ndependencies: [TASK-0802]\n")
write(R, "spec/tasks/TASK-0802.yaml", "id: TASK-0802\ntype: task\ntitle: b\nstatus: ACTIVE\ntask_status: READY\nclass: documentation\nobjective: o\ndependencies: [TASK-0801]\n")
run(R, "rebuild-memory", "--incremental")
cc = run(R, "health", "close-check", t, "--report", rep)
check("S-F.3", code(cc) in ("GOVERNANCE_SUITE_STALE", "HEALTH_HARD_BLOCK"), "when the re-check does not come back green the governance-affecting close is refused", (cc.get("error") or {}).get("message", "")[:220])

# ---------------------------------------------------------------------------------------------------------- S-G
print("\n=== S-G skill regression")
R = mkproj("sg")
false_skill = """id: SKL-PROBE-FALSE
name: probe false
version: 1.0.0
status: ACTIVE
roles: [all]
task_classes: [documentation]
purpose: p
method:
  - {step: s, description: d}
validation_scenarios:
  - id: V1
    given: a fresh project
    expect: creating a task is refused
    check:
      steps:
        - gov: [task, create, --class, documentation, --objective, x, --allowed, "docs/**"]
          expect: {ok: false}
"""
true_skill = false_skill.replace("SKL-PROBE-FALSE", "SKL-PROBE-TRUE").replace("creating a task is refused", "an unknown task cannot be claimed").replace(
    "- gov: [task, create, --class, documentation, --objective, x, --allowed, \"docs/**\"]\n          expect: {ok: false}",
    "- gov: [task, claim, TASK-9999]\n          expect: {ok: false, error_code: [TASK_NOT_FOUND, NOT_FOUND]}")
write(R, "governance/project/skills/SKL-PROBE-FALSE.yaml", false_skill)
write(R, "governance/project/skills/SKL-PROBE-TRUE.yaml", true_skill)
sk = body(run(R, "health", "skills"))
rows = {s["skill"]: s for s in sk["detail"]["skills"]}
check("S-G.1", rows["SKL-PROBE-FALSE"]["scenarios"][0]["status"] == "failed" and rows["SKL-PROBE-TRUE"]["scenarios"][0]["status"] == "passed",
      "validation scenarios are executed in sandboxes: a false expectation is reported FAILED, a true one PASSES", {k: rows[k]["scenarios"][0]["status"] for k in ("SKL-PROBE-FALSE", "SKL-PROBE-TRUE")})
fam = body(run(R, "audit", "--no-persist", "--family", "skill_regression"))
check("S-G.2", fam["families"]["skill_regression"]["ok"] is False and any("SKL-PROBE-FALSE V1" in f["message"] and "FAILED" in f["message"] for f in fam["findings"]),
      "the skill_regression family fails on the false scenario", [f["message"][:160] for f in fam["findings"] if "PROBE" in f["message"]])
os.remove(os.path.join(R, "governance/project/skills/SKL-PROBE-FALSE.yaml"))
recd = run(R, "health", "skills", "--skill", "SKL-PROBE-TRUE", "--record")
check("S-G.3", recd.get("ok") and "SKL-PROBE-TRUE@1.0.0" in body(recd)["bound"], "a passing version is bound to its content in the tracked skill-bindings.json", body(recd).get("bound"))
p = os.path.join(R, "governance/project/skills/SKL-PROBE-TRUE.yaml")
text = open(p).read()
open(p, "w").write(text.replace("{step: s, description: d}", "{step: s, description: silently rewritten method}"))
fam = body(run(R, "audit", "--no-persist", "--family", "skill_regression"))
hits = [f["message"] for f in fam["findings"] if "SKL-PROBE-TRUE@1.0.0" in f["message"]]
check("S-G.4", any("bound content" in m for m in hits), "a method change without a version change is reported against the tracked binding", hits)
again = run(R, "health", "skills", "--skill", "SKL-PROBE-TRUE", "--record")
check("S-G.5", code(again) == "SKILL_VERSION_CONTENT_CONFLICT", "re-binding changed content under the same version is refused", (again.get("error") or {}).get("message"))

# ---------------------------------------------------------------------------------------------------------- S-H
print("\n=== S-H tier contract")
R = mkproj("sh")
chk = body(run(R, "health", "checks"))
tiers = {t["tier"]: t["checks"] for t in chk["tiers"]}
check("S-H.1", set(tiers) == {"G0", "G1", "G2", "G3", "G4", "G5", "G6"} and tiers["G3"] and tiers["G6"],
      "the tier contract declares G0..G6 and the checks of each tier", {t: len(c) for t, c in tiers.items()})
open(os.path.join(R, "spec/now/NOW.md"), "a").write("\nnote\n")
run(R, "rebuild-memory", "--incremental")
g3 = body(run(R, "health", "run", "--tier", "G3", "--event", "checkpoint.create"))
ex = set(g3["summary"]["executed_checks"])
check("S-H.2", ex and ex <= set(tiers["G3"]) | {"concurrency_claims", "fresh_agent_reconstruction", "audit_reproducibility"},
      "a G3 run executes only G3 (and never-cached) checks", {"executed": sorted(ex), "tier": g3.get("tier")})

# ---------------------------------------------------------------------------------------------------------- S-I
print("\n=== S-I runtime identity")
R = mkproj("si")
run(R, "health", "run")
mod = os.path.join(SCRATCH, "gov-modified")
shutil.copy2(GOV, mod)
open(mod, "ab").write(b"\n# WS02 supplementary: a different implementation artefact\n")
cur = body(run(R, "health", "currency", gov=mod))["currency"]
check("S-I.1", not cur["current"] and [c["class"] for c in cur["changed_classes"]] == ["runtime_identity"],
      "a modified gov binary makes the green record stale (changed class: runtime_identity only)", cur)

# ---------------------------------------------------------------------------------------------------------- S-J
print("\n=== S-J concurrency safety: checks run concurrently on an untrusted kernel without corrupting shared state")
kc = os.path.join(SCRATCH, "sj-kernel-cache")


def run_embedded(root, *args):
    env = dict(os.environ)
    for k in ("GOV_ROLE", "GOV_SESSION", "GOV_CANONICAL_ROOT"):
        env.pop(k, None)
    env["GOV_KERNEL_CACHE"] = kc
    env["XDG_STATE_HOME"] = root + ".machine"
    p = subprocess.run([GOV, "--json", "--root", root, "--session", "S-ws02", "--role", "orchestrator", *args], capture_output=True, text=True, env=env)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"ok": False, "error": {"code": "NON_JSON"}}


def fresh(name):
    root = os.path.join(SCRATCH, name)
    shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), root)
    git(root, "init", "-q"); git(root, "config", "user.email", "ws02@example.invalid"); git(root, "config", "user.name", "ws02")
    git(root, "add", "-A"); git(root, "commit", "-qm", "fixture")
    return root


R = mkproj("sj1")  # installed from the canonical source: the embedded payload has not been materialised yet
open(os.path.join(R, "governance/kernel/schemas/task.schema.json"), "a").write("\n")  # installed kernel now untrusted
# the first materialisation of the embedded baseline (substituted for the untrusted kernel) happens inside doctor,
# whose check groups run concurrently, then inside a concurrent suite run
run_embedded(R, "doctor")
run_embedded(R, "audit", "--no-persist")
files = sorted(os.path.relpath(os.path.join(d, f), kc) for d, _, fs in os.walk(kc) for f in fs)
R2 = fresh("sj2")
e = run_embedded(R2, "init", "--name", "sj2", "--alias", "sj2")
ref = os.path.join(SCRATCH, "sj-reference-cache")
env = dict(os.environ); env.pop("GOV_CANONICAL_ROOT", None); env["GOV_KERNEL_CACHE"] = ref; env["XDG_STATE_HOME"] = os.path.join(SCRATCH, "sj3.machine")
R3 = fresh("sj3")
subprocess.run([GOV, "--json", "--root", R3, "--session", "S", "--role", "orchestrator", "init", "--name", "sj3", "--alias", "sj3"], capture_output=True, env=env)
reference = sorted(os.path.relpath(os.path.join(d, f), ref) for d, _, fs in os.walk(ref) for f in fs)
check("S-J.1", files == reference and e.get("ok"),
      "the embedded baseline first materialised during concurrent checks is complete (identical file set to a single-threaded materialisation) and a later embedded init succeeds",
      {"files": len(files), "reference_files": len(reference), "second_init": e.get("ok") or (e.get("error") or {}).get("code")})

print("\nSUMMARY checks=%d pass=%d fail=%d failed=%s" % (len(RESULTS), sum(1 for _, o in RESULTS if o), sum(1 for _, o in RESULTS if not o), [n for n, o in RESULTS if not o]))
