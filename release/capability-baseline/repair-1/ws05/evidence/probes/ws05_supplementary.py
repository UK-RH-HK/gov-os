"""P2-AR-0018 (WS-5 repair builder) supplementary end-to-end probes for BC-P2-14 and BC-P2-15.

BUILDER REGRESSION EVIDENCE ONLY (Contract v3 O3): written by the builder that made the repair, so it is not
acceptance evidence. It drives the release binary through its CLI JSON contract (API-0002) on disposable projects,
each with its own simulated machine (XDG_STATE_HOME), and prints one line per observation:

    CHECK <id> PASS|FAIL <statement>        followed by an indented `detail:` line

Run it against the repaired binary and, as the negative control, against the pre-repair binary:

    GOV_BIN=<gov> PROBE_SCRATCH=<dir> python3 ws05_supplementary.py > <out>

Every attack here is general (fresh projects, fresh ids, several sessions/processes); none depends on the audit
probes' fixtures.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GOV = os.environ.get("GOV_BIN", os.path.join(WT, "target", "release", "gov"))
SCRATCH = os.environ.get("PROBE_SCRATCH", os.path.join(tempfile.gettempdir(), "ws05-probes"))
RESULTS = []


def check(cid, ok, statement, detail=None):
    RESULTS.append((cid, bool(ok)))
    print(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {statement}", flush=True)
    if detail is not None:
        print("      detail: " + (detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True, default=str)[:1800]), flush=True)


def code(v):
    return "OK" if v.get("ok") else (v.get("error") or {}).get("code")


class Proj:
    def __init__(self, name, fixture="greenfield"):
        os.makedirs(SCRATCH, exist_ok=True)
        base = os.path.join(SCRATCH, f"{name}-{uuid.uuid4().hex[:6]}")
        self.root = os.path.join(base, "proj")
        self.state = os.path.join(base, "state")
        shutil.copytree(os.path.join(WT, "fixtures", fixture, "project"), self.root)
        os.makedirs(self.state)
        self.git("init", "-q", ".")
        self.git("config", "user.email", "probe@example.invalid")
        self.git("config", "user.name", "probe")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture")
        r = self.run(["init", "--name", name, "--alias", "a-" + name], "orchestrator", "S-init")
        assert r.get("ok"), r
        self.commit("gov init")
        print(f"# project {self.root}", flush=True)

    def env(self):
        e = dict(os.environ)
        for k in ("GOV_ROLE", "GOV_SESSION", "GOV_MACHINE_STATE_DIR"):
            e.pop(k, None)
        e["XDG_STATE_HOME"] = self.state
        e["GOV_CANONICAL_ROOT"] = WT
        return e

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.root, capture_output=True, text=True)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def cmd(self, args, role, session, root=None):
        return [GOV, "--json", "--root", root or self.root, "--session", session, "--role", role] + list(args)

    def run(self, args, role="orchestrator", session="S0", root=None):
        p = subprocess.run(self.cmd(args, role, session, root), cwd=root or self.root, capture_output=True, text=True, env=self.env())
        try:
            v = json.loads(p.stdout)
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-800:]}}
        v["_exit"] = p.returncode
        return v

    def ok(self, args, role="orchestrator", session="S0", root=None):
        v = self.run(args, role, session, root)
        if not v.get("ok"):
            raise SystemExit(f"unexpected failure: gov {' '.join(args)} ({role}/{session}): {v.get('error')}")
        return v["result"]

    def race(self, jobs, root=None):
        """Launch every (args, role, session) job at once as separate OS processes; return their envelopes."""
        procs = [subprocess.Popen(self.cmd(a, r, s, root), cwd=root or self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env()) for a, r, s in jobs]
        out = []
        for p in procs:
            so, se = p.communicate()
            try:
                out.append(json.loads(so))
            except Exception:
                out.append({"ok": False, "error": {"code": "NO_JSON", "message": (se or so)[-400:]}})
        return out

    def task(self, tid, cls="documentation", allowed=None, fields=None, role="orchestrator"):
        a = ["task", "create", "--id", tid, "--class", cls, "--objective", tid, "--status", "READY"]
        if allowed:
            a += ["--allowed", allowed]
        if fields:
            a += ["--fields", json.dumps(fields)]
        return self.run(a, role, "S0")

    def write(self, rel, text):
        full = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

    def report(self, name, files, work="did the work"):
        d = os.path.join(self.root, ".governance-runtime", "probe-reports")
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, name + ".json")
        with open(f, "w") as fh:
            json.dump({"work_completed": work, "files_changed": files, "tests": {"status": "not_applicable_with_reason", "reason": "probe"}, "outcome": "success", "evidence": []}, fh)
        return f

    def close(self, tid, role, session, files, name=None, force=False, root=None):
        self.run(["rebuild-memory", "--incremental"], role, session, root)
        a = ["task", "close", tid, "--report", self.report(name or f"{tid}-{uuid.uuid4().hex[:4]}", files)]
        if force:
            a.append("--force")
        return self.run(a, role, session, root)

    def dag(self):
        return self.ok(["task", "dag"])

    def blocked_reasons(self, tid):
        d = self.dag()
        return [b["reasons"] for b in d["blocked"] if b["task"] == tid]

    def claims_db(self):
        return os.path.join(self.root, ".governance-runtime", "claims.db")


def overrides(p, pairs):
    pp = os.path.join(p.root, "governance/project/PROJECT_POLICY.yaml")
    import yaml
    d = yaml.safe_load(open(pp))
    d.setdefault("policy_overrides", {}).update(pairs)
    yaml.safe_dump(d, open(pp, "w"), sort_keys=False)


# ============================================================================================ BC-P2-15 claims
print("\n## BC-P2-15 claim atomicity (real concurrent processes)")
p = Proj("race")
TRIALS, N = 20, 6
bad = []
for i in range(TRIALS):
    t = f"TASK-R{i:02d}"
    p.task(t)
    res = p.race([(["task", "claim", t], "backend-engineer", f"S-{i}-{k}") for k in range(N)])
    winners = [f"S-{i}-{k}" for k, v in enumerate(res) if v.get("ok")]
    codes = sorted(code(v) for v in res)
    holder = [c["session_id"] for c in p.ok(["claims", "list"]) if c["task_id"] == t]
    if len(winners) != 1 or holder != winners or any(c not in ("OK", "TASK_CLAIMED") for c in codes):
        bad.append({"trial": i, "winners": winners, "holder": holder, "codes": codes})
    p.run(["task", "release", t, "--force"], "change-controller", "S-cc")
check("WS5-A1.race", not bad, f"{TRIALS} trials x {N} simultaneous processes claiming one task: exactly one grant per trial, every other process told TASK_CLAIMED, the store holds the winner", {"bad_trials": bad})

p = Proj("overlap-race")
bad = []
for i in range(TRIALS):
    ts = [f"TASK-O{i:02d}{k}" for k in range(4)]
    for t in ts:
        p.task(t, allowed="src/**")
    res = p.race([(["task", "claim", t], "backend-engineer", f"S-o{i}-{k}") for k, t in enumerate(ts)])
    codes = [code(v) for v in res]
    if codes.count("OK") != 1 or sorted(c for c in codes if c != "OK") != ["CLAIM_SCOPE_CONFLICT"] * 3:
        bad.append({"trial": i, "codes": codes})
    for t in ts:
        p.run(["task", "release", t, "--force"], "change-controller", "S-cc")
check("WS5-A2.overlap-race", not bad, f"{TRIALS} trials x 4 processes claiming four different tasks with the same scope src/** at once: exactly one grant, the rest CLAIM_SCOPE_CONFLICT", {"bad_trials": bad})

p = Proj("budget-race")
overrides(p, {"BUDGET_POLICY.defaults.max_parallel_agents": 2})
ts = [f"TASK-B{k}" for k in range(5)]
for k, t in enumerate(ts):
    p.task(t, allowed=f"area{k}/**")
res = p.race([(["task", "claim", t], "backend-engineer", f"S-b{k}") for k, t in enumerate(ts)])
codes = [code(v) for v in res]
sessions = sorted({c["session_id"] for c in p.ok(["claims", "list"]) if not c["expired"]})
check("WS5-A3.budget-race", codes.count("OK") == 2 and codes.count("BUDGET_EXCEEDED") == 3 and len(sessions) == 2, "max_parallel_agents=2, five processes claim five disjoint tasks at once: exactly two sessions are granted, three get BUDGET_EXCEEDED", {"codes": codes, "sessions_holding": sessions})

print("\n## BC-P2-15 claim scope and unit of isolation")
p = Proj("iso")
p.task("TASK-I1", allowed="src/**")
p.commit("t")
c = p.ok(["task", "claim", "TASK-I1"], "backend-engineer", "S-i1")
row = [x for x in p.ok(["claims", "list"]) if x["task_id"] == "TASK-I1"][0]
check("WS5-A4.isolation-recorded", row.get("worktree") == os.path.realpath(p.root) and row.get("git_dir") and row.get("branch") and row.get("head") and row.get("scope") == ["src/**"], "the claim records its unit of isolation (worktree root, git dir, branch, HEAD) and its mutation scope", row)

# cross-worktree: a linked worktree of the same repository shares the claims store
p.task("TASK-I2", allowed="src/lib.rs")
p.task("TASK-I3", allowed="docs/**")
p.commit("tasks")
wt2 = os.path.join(os.path.dirname(p.root), "wt2")
p.git("worktree", "add", "-q", wt2)
r1 = p.run(["task", "claim", "TASK-I1"], "backend-engineer", "S-wt2", root=wt2)
r2 = p.run(["task", "claim", "TASK-I2"], "backend-engineer", "S-wt2", root=wt2)
r3 = p.run(["task", "claim", "TASK-I3"], "backend-engineer", "S-wt2", root=wt2)
r4 = p.run(["task", "claim", "TASK-I1"], "backend-engineer", "S-i1", root=wt2)
check("WS5-A5.cross-worktree", code(r1) == "TASK_CLAIMED" and code(r2) == "CLAIM_SCOPE_CONFLICT" and code(r3) == "OK" and code(r4) == "CLAIM_WORKTREE_MISMATCH",
      "from a linked git worktree: the task held in the main worktree is TASK_CLAIMED, an overlapping scope is CLAIM_SCOPE_CONFLICT, a disjoint task is granted, and the holder cannot re-claim its task from another worktree", {"same_task": code(r1), "overlap": code(r2), "disjoint": code(r3), "holder_from_other_worktree": code(r4)})
p.write("src/lib.rs", open(os.path.join(p.root, "src/lib.rs")).read() + "\n// i1\n")
rc = p.close("TASK-I1", "backend-engineer", "S-i1", ["src/lib.rs"], root=wt2)
check("WS5-A5b.close-in-claim-worktree", code(rc) == "CLAIM_WORKTREE_MISMATCH", "closing from a worktree other than the one the claim was made in is refused (the baseline belongs to that tree)", rc.get("error"))

print("\n## BC-P2-15 parallel work on disjoint scopes in one worktree")
p = Proj("disjoint")
p.task("TASK-D1", allowed="src/a/**")
p.task("TASK-D2", allowed="src/b/**")
p.task("TASK-D3")  # no allowed_paths: unrestricted scope
p.commit("t")
w1 = p.run(["continue", "--claim"], "backend-engineer", "S-d1")
w2 = p.run(["continue", "--claim"], "backend-engineer", "S-d2")
w3 = p.run(["continue", "--claim"], "backend-engineer", "S-d3")
check("WS5-A7.continue-disjoint", code(w1) == "OK" and code(w2) == "OK" and w1["result"]["task"] == "TASK-D1" and w2["result"]["task"] == "TASK-D2" and w3["result"]["status"] == "NO_RUNNABLE_WORK" and any(d["task"] == "TASK-D3" for d in w3["result"].get("deferred", [])),
      "gov continue --claim gives each agent independent work: the second agent is offered the disjoint task, a third is told why the unrestricted task is deferred", {"w1": (w1.get("result") or {}).get("task") or code(w1), "w2": (w2.get("result") or {}).get("task") or code(w2), "w3": (w3.get("result") or {}).get("status"), "w3_deferred": (w3.get("result") or {}).get("deferred")})
p.write("src/a/x.rs", "// a\n")
p.write("src/b/y.rs", "// b\n")
c2 = p.close("TASK-D2", "backend-engineer", "S-d2", ["src/b/y.rs"])
c1 = p.close("TASK-D1", "backend-engineer", "S-d1", ["src/a/x.rs"])
check("WS5-A6.disjoint-close", code(c2) == "OK" and code(c1) == "OK", "two sessions working disjoint scopes in one worktree both close, each declaring only its own change (the other's change is attributed to its claim / its close)", {"D2": code(c2), "D1": code(c1), "D2_err": (c2.get("error") or {}).get("message"), "D1_err": (c1.get("error") or {}).get("message")})

p = Proj("claimreq")
p.task("TASK-Q1", allowed="docs/**")
p.commit("t")
p.write("docs/q.md", "q\n")
q1 = p.close("TASK-Q1", "backend-engineer", "S-q", ["docs/q.md"])
q2 = p.close("TASK-Q1", "change-controller", "S-cc", ["docs/q.md"], force=True)
check("WS5-A8.close-requires-claim", code(q1) == "CLAIM_REQUIRED" and code(q2) == "OK" and any(o.get("override") == "no_claim_held" for o in (q2.get("result") or {}).get("overrides", [])),
      "closing a task the session never claimed is refused (CLAIM_REQUIRED); an L3 --force close proceeds and records the override", {"unclaimed": code(q1), "forced": code(q2), "overrides": (q2.get("result") or {}).get("overrides")})

p = Proj("stale-release")
p.task("TASK-S1", allowed="docs/**")
p.ok(["task", "claim", "TASK-S1"], "backend-engineer", "S-old")
con = sqlite3.connect(p.claims_db())
con.execute("update claims set expires_at='2020-01-01T00:00:00Z' where task_id='TASK-S1'")
con.commit()
con.close()
t2 = p.run(["task", "claim", "TASK-S1"], "backend-engineer", "S-new")
rel = p.run(["task", "release", "TASK-S1"], "backend-engineer", "S-old")
holder = [c["session_id"] for c in p.ok(["claims", "list"]) if c["task_id"] == "TASK-S1"]
check("WS5-A9.stale-holder-release", code(t2) == "OK" and code(rel) == "TASK_CLAIMED" and holder == ["S-new"], "after a lease expires and another session takes the task, the previous holder's release cannot delete the new claim", {"takeover": code(t2), "old_release": code(rel), "holder": holder})

# ============================================================================================ BC-P2-14 contract
print("\n## BC-P2-14 blocks orders work")
p = Proj("blocks")
p.task("TASK-A", fields={"blocks": ["TASK-B"]})
p.task("TASK-B")
p.task("TASK-C", fields={"blocks": ["TASK-D"]})
p.task("TASK-D", fields={"blocks": ["TASK-C"]})
d = p.dag()
rp = p.ok(["task", "replan"])
st_b = p.ok(["task", "show", "TASK-B"])["task_status"]
check("WS5-B1.blocks", "TASK-B" not in d["runnable"] and any("TASK-A" in " ".join(r) for r in [b["reasons"] for b in d["blocked"] if b["task"] == "TASK-B"]) and st_b == "BLOCKED" and any(set(cy) == {"TASK-C", "TASK-D"} for cy in d["cycles"]),
      "A.blocks=[B]: B is not runnable while A is open (reason names A), replan stores B BLOCKED, and mutual blocks form a reported cycle", {"B_reasons": [b["reasons"] for b in d["blocked"] if b["task"] == "TASK-B"], "B_status_after_replan": st_b, "cycles": d["cycles"]})
p.commit("t")
p.ok(["task", "claim", "TASK-A"], "backend-engineer", "S-a")
p.close("TASK-A", "backend-engineer", "S-a", [])
d2 = p.dag()
p.ok(["task", "replan"])
check("WS5-B1b.blocks-released", "TASK-B" in d2["runnable"] and p.ok(["task", "show", "TASK-B"])["task_status"] == "READY", "once A is DONE, B becomes runnable and replan stores it READY", {"runnable": d2["runnable"]})

print("\n## BC-P2-14 required data / tools / skills gate readiness")
p = Proj("inputs")
p.task("TASK-DATA", fields={"required_data": ["DATA-0042"]})
p.task("TASK-PATH", fields={"required_data": ["fixtures/orders.csv"]})
p.task("TASK-ESC", fields={"required_data": ["../../../../etc/passwd"]})
p.task("TASK-TOOL-MISSING", fields={"required_tools": ["TOOL-NOPE-9"]})
p.task("TASK-TOOL-PROPOSED", fields={"required_tools": ["TOOL-LSP-RUST-001"]})
p.task("TASK-TOOL-OK", fields={"required_tools": ["TOOL-CARGO-001", "TOOL-GIT-001"]})
p.task("TASK-SKILL", fields={"required_skills": ["SKL-NOPE-9"]})
p.task("TASK-SKILL-OK", fields={"required_skills": ["SKL-BACKEND-IMPL"]})
d = p.dag()
run = set(d["runnable"])
gated = {t: [b["reasons"] for b in d["blocked"] if b["task"] == t] for t in ["TASK-DATA", "TASK-PATH", "TASK-ESC", "TASK-TOOL-MISSING", "TASK-TOOL-PROPOSED", "TASK-SKILL"]}
check("WS5-B3.inputs-gate", all(gated[t] for t in gated) and {"TASK-TOOL-OK", "TASK-SKILL-OK"} <= run,
      "a task whose required data (record id, repository path, or a path escaping the repository), tool (unregistered or not active) or skill does not resolve is blocked with the reason; resolvable inputs do not block", {"blocked": gated, "runnable": sorted(run)})
p.write("spec/data/DATA-0042.yaml", json.dumps({"id": "DATA-0042", "type": "data", "title": "orders", "status": "ACTIVE"}) + "\n")
p.write("fixtures/orders.csv", "id,cents\n1,399\n")
d = p.dag()
ok1 = {"TASK-DATA", "TASK-PATH"} <= set(d["runnable"])
p.write("spec/data/DATA-0042.yaml", json.dumps({"id": "DATA-0042", "type": "data", "title": "orders", "status": "SUPERSEDED", "superseded_by": "DATA-0043"}) + "\n")
d2 = p.dag()
check("WS5-B3b.inputs-appear", ok1 and "TASK-DATA" not in d2["runnable"], "providing the data record / file makes the task runnable; superseding the record blocks it again", {"after_provide": sorted(d["runnable"]), "after_supersede": [b for b in d2["blocked"] if b["task"] == "TASK-DATA"]})

print("\n## BC-P2-14 production-merge permission")
p = Proj("merge")
p.task("TASK-EXP", cls="experiment", allowed="src/**,spec/experiments/**", fields={"production_merge_allowed": True})
p.task("TASK-NOMERGE", cls="implementation", allowed="src/**", fields={"production_merge_allowed": False, "scenarios": ["SCN-1"], "acceptance_tests": ["TST-1"]})
p.commit("t")
p.ok(["task", "claim", "TASK-EXP"], "backend-engineer", "S-e")
p.write("src/experimental.rs", "// prototype\n")
e1 = p.close("TASK-EXP", "backend-engineer", "S-e", ["src/experimental.rs"])
os.remove(os.path.join(p.root, "src/experimental.rs"))
p.write("spec/experiments/EXP-0009.yaml", json.dumps({"id": "EXP-0009", "type": "experiment", "title": "prototype", "status": "ACTIVE", "hypothesis": "h", "production_merge_allowed": False}) + "\n")
e2 = p.close("TASK-EXP", "backend-engineer", "S-e", ["spec/experiments/EXP-0009.yaml"])
check("WS5-B6.experiment-merge", code(e1) == "PRODUCTION_MERGE_NOT_ALLOWED" and code(e2) == "OK",
      "an experiment task (even one created asking for production_merge_allowed: true) cannot close with output in the production tree; with its output kept under spec/experiments/** it closes", {"with_src": code(e1), "detail": (e1.get("error") or {}).get("details", {}).get("production_paths"), "with_spec_experiments": code(e2)})
p.ok(["task", "claim", "TASK-NOMERGE"], "backend-engineer", "S-n")
p.write("src/lib.rs", open(os.path.join(p.root, "src/lib.rs")).read() + "\n// no merge\n")
n1 = p.close("TASK-NOMERGE", "backend-engineer", "S-n", ["src/lib.rs"])
check("WS5-B6b.no-merge-flag", code(n1) == "PRODUCTION_MERGE_NOT_ALLOWED", "any task whose contract says production_merge_allowed: false is held to it, not only experiments", code(n1))
# the repository contract may declare an experiment sandbox outside production
import yaml
cp = os.path.join(p.root, "governance/project/REPOSITORY_CONTRACT.yaml")
c = yaml.safe_load(open(cp))
c["paths"].append({"pattern": "sandbox/**", "class": "evidence", "namespace": "sandbox"})
yaml.safe_dump(c, open(cp, "w"), sort_keys=False)
p.task("TASK-EXP2", cls="experiment", allowed="sandbox/**")
p.commit("sandbox")
p.ok(["task", "claim", "TASK-EXP2"], "backend-engineer", "S-e2")
p.write("sandbox/try.rs", "// try\n")
e3 = p.close("TASK-EXP2", "backend-engineer", "S-e2", ["sandbox/try.rs"])
check("WS5-B6c.contract-sandbox", code(e3) == "OK", "a path the repository contract classifies as evidence (an experiment sandbox) is an allowed home for experimental output", {"close": code(e3), "err": (e3.get("error") or {}).get("message")})

print("\n## BC-P2-14 path scope: a CIT covers only changes inside the task's claim window")
p = Proj("citwin")
p.write("spec/requirements/REQ-0001.yaml", json.dumps({"id": "REQ-0001", "type": "requirement", "title": "totals", "status": "ACTIVE", "kind": "functional", "acceptance_criteria": ["exact"]}) + "\n")
p.write("spec/requirements/REQ-0002.yaml", json.dumps({"id": "REQ-0002", "type": "requirement", "title": "limits", "status": "ACTIVE", "kind": "functional", "acceptance_criteria": ["bounded"]}) + "\n")
p.commit("reqs")
p.ok(["rebuild-memory"])


def cit(target, value):
    mf = os.path.join(p.root, ".governance-runtime", f"mf-{uuid.uuid4().hex[:4]}.json")
    with open(mf, "w") as f:
        json.dump([{"op": "set_field", "target": target, "field": "priority", "value": value}], f)
    cid = p.ok(["cit", "propose", "--proposal", f"priority of {target}", "--trigger", "editorial", "--targets", target, "--manifest", mf])["id"]
    p.ok(["cit", "simulate", cid])
    p.ok(["cit", "approve", cid, "--by", "change-controller", "--method", "auto"], "change-controller", "S-cc")
    return p.ok(["cit", "execute", cid], "change-controller", "S-cc")


cit("REQ-0001", "high")  # before the task exists / is claimed
p.task("TASK-LATE", allowed="src/**")
p.commit("late")
p.ok(["task", "claim", "TASK-LATE"], "backend-engineer", "S-late")
req = yaml.safe_load(open(os.path.join(p.root, "spec/requirements/REQ-0001.yaml")))
req["acceptance_criteria"] = ["rewritten by a src-only task"]
yaml.safe_dump(req, open(os.path.join(p.root, "spec/requirements/REQ-0001.yaml"), "w"))
l1 = p.close("TASK-LATE", "backend-engineer", "S-late", ["spec/requirements/REQ-0001.yaml"])
check("WS5-B8.old-cit-covers-nothing", code(l1) == "MUTATION_SCOPE_VIOLATION" and "REQ-0001" in json.dumps(l1.get("error")),
      "a src/**-only task that rewrites a requirement touched by a CIT committed before its claim is refused (the earlier CIT governs nothing it did)", (l1.get("error") or {}).get("message"))
p.git("checkout", "--", "spec/requirements/REQ-0001.yaml")
p.task("TASK-WIN", allowed="docs/**")
p.commit("win")
p.ok(["task", "claim", "TASK-WIN"], "backend-engineer", "S-win")
cit("REQ-0002", "low")  # executed while TASK-WIN is claimed: this CIT made the change
w1 = p.close("TASK-WIN", "backend-engineer", "S-win", [])
check("WS5-B8b.window-cit-covers", code(w1) == "OK", "a change a CIT made while the task was claimed is governed by that CIT and does not block the task's close (control)", {"close": code(w1), "err": (w1.get("error") or {}).get("message")})

print("\n## BC-P2-14 path scope cannot be laundered by re-claiming")
p = Proj("launder")
p.task("TASK-L", allowed="docs/**")
p.commit("t")
p.ok(["task", "claim", "TASK-L"], "backend-engineer", "S-l")
p.write("src/sneaky.rs", "// out of scope\n")
p.run(["task", "claim", "TASK-L"], "backend-engineer", "S-l")  # renewal
a = p.close("TASK-L", "backend-engineer", "S-l", [])
p.run(["task", "release", "TASK-L"], "backend-engineer", "S-l")
p.run(["task", "claim", "TASK-L"], "backend-engineer", "S-l")  # fresh claim after release
b = p.close("TASK-L", "backend-engineer", "S-l", [])
p.run(["task", "release", "TASK-L"], "backend-engineer", "S-l")
p.run(["task", "claim", "TASK-L"], "backend-engineer", "S-other")  # another session takes over
c3 = p.close("TASK-L", "backend-engineer", "S-other", [])
check("WS5-B9.no-baseline-laundering", code(a) == "MUTATION_SCOPE_VIOLATION" and code(b) == "MUTATION_SCOPE_VIOLATION" and code(c3) == "MUTATION_SCOPE_VIOLATION",
      "an out-of-scope change stays observed after re-claiming, after release + re-claim, and after another session takes the task over", {"renewal": code(a), "release_reclaim": code(b), "takeover": code(c3)})

print("\n## BC-P2-14 the close is held to the scope the claim reserved")
p = Proj("widen")
p.task("TASK-W", allowed="docs/**")
p.commit("t")
p.ok(["task", "claim", "TASK-W"], "backend-engineer", "S-w")
tp = os.path.join(p.root, "spec/tasks/TASK-W.yaml")
rec = yaml.safe_load(open(tp))
rec["allowed_paths"] = ["docs/**", "src/**"]  # the worker widens its own task record after the claim
yaml.safe_dump(rec, open(tp, "w"), sort_keys=False)
p.write("src/widened.rs", "// outside the reserved scope\n")
wv = p.close("TASK-W", "backend-engineer", "S-w", ["src/widened.rs"])
check("WS5-B11.reserved-scope", code(wv) == "MUTATION_SCOPE_VIOLATION" and "reserved" in json.dumps(wv.get("error")),
      "widening allowed_paths in the task record after the claim does not widen what the claim may close with", (wv.get("error") or {}).get("message"))

print("\n## BC-P2-14 designated role")
p = Proj("role")
p.task("TASK-TD", cls="test-design", allowed="tests/**", fields={"role": "independent-test-designer"})
bad_role = p.task("TASK-BAD", fields={"role": "no-such-role"})
p.commit("t")
r1 = p.run(["task", "claim", "TASK-TD"], "backend-engineer", "S-x")
r2 = p.run(["continue"], "backend-engineer", "S-x")
r3 = p.run(["task", "claim", "TASK-TD"], "independent-test-designer", "S-x")
p.write("tests/ledger_test.rs", open(os.path.join(p.root, "tests/ledger_test.rs")).read() + "\n// independent test\n")
r4 = p.close("TASK-TD", "backend-engineer", "S-x", ["tests/ledger_test.rs"])
r5 = p.close("TASK-TD", "independent-test-designer", "S-x", ["tests/ledger_test.rs"])
check("WS5-B10.designated-role", code(r1) == "ROLE_NOT_DESIGNATED" and (r2.get("result") or {}).get("task") != "TASK-TD" and code(r3) == "OK" and code(r4) == "ROLE_NOT_DESIGNATED" and code(r5) == "OK" and code(bad_role) == "UNKNOWN_ROLE",
      "the task's designated role binds claim and close (another role is refused even with the same session; continue does not offer it) and a task cannot designate an unknown role", {"claim_other_role": code(r1), "continue_offers": (r2.get("result") or {}).get("task"), "claim_designated": code(r3), "close_other_role": code(r4), "close_designated": code(r5), "create_unknown_role": code(bad_role)})

n = len(RESULTS)
f = [c for c, ok in RESULTS if not ok]
print(f"SUMMARY checks={n} pass={n - len(f)} fail={len(f)} failed={f}", flush=True)
