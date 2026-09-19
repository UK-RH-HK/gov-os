#!/usr/bin/env python3
# DERIVED COPY (P2-AR-0032, round-2 integration builder) of
#   release/capability-baseline/repair-1/r2-ws09-11/evidence/probes/R2-ws0911-named-checks.py (P2-AR-0030, WS-9/11).
# ORIGINAL-PROBE-ID: ws09-11-r2-named-checks
# Changes, and nothing else:
#  (2) human_answer(): P2-ADJ-0001 (WS-3, merged) turned the standalone human-gate anchor off, so instead of
#      provisioning one the machine is provisioned with the throw-away root that delegates `human-gate` to the same
#      test owner key and the installed kernel is re-verified (p2ar0032_root_channel.provision, WS-3's own method).
# Every check, its scenario and its PASS criterion are P2-AR-0030's.
"""P2-AR-0030 (repair-1 round 2, WS-9/11) named checks — BUILDER REGRESSION EVIDENCE ONLY (Contract v3 O3), not acceptance.

A discriminating reimplementation of the audit-of-record lines this round's classes name, driven through the `gov` JSON
CLI on disposable repositories, using only the paths the product now requires (declared roles and sessions, reviewer-
and verifier-authored tests, owner-signed human answers with WS-3's published test-material signer). Each check prints
`X <id> PASS|FAIL <statement> -- <detail>`. Run against the candidate binary and against the base binary 843d79c
(negative control: the lines must FAIL there, except those marked [control], which state a property both hold).

  BC-P2-34 adoption side   alpha-r S4-T2-B2-negative [N1] [N2] [N7], T1-roles [T1c], epsilon-r O3 §C/§D (adoption part),
                           A10 held-out authorship, A11 independence, role consistency, T2 binding of the adoption record
  BC-P2-11 (adoption gates) a gate answer authorises only the catalogue entry it was raised for
  BC-P2-07 (adopt host)    G0 guard at A6, G4 after migration, G5 at A11
  BC-P2-10 (export use)    epsilon-r Q-learning-upstream Q1.6-8: upstream export approval from the owner-signed channel

Environment: GOV_BIN (the gov binary), R2_SCRATCH (scratch dir), HC_OWNER (WS-3's hc_owner.py test signer).
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid

GOV = os.environ["GOV_BIN"]
SCRATCH = os.environ.get("R2_SCRATCH") or tempfile.mkdtemp(prefix="p2ar0030-")
HC = os.environ["HC_OWNER"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2ar0032_root_channel  # noqa: E402  (2)
EV = "spec/audits/GOVERNANCE-ADOPTION"
RESULTS = []


def log(*a):
    print(*a, flush=True)


def x(xid, ok, statement, detail=""):
    RESULTS.append((xid, bool(ok)))
    d = detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True, default=str)
    log(f"X {xid} {'PASS' if ok else 'FAIL'} {statement} -- {d[:900]}")


class Gov:
    def __init__(self, root, home, role="orchestrator", session="S-plan", env=None):
        self.root, self.home, self.role, self.session, self.extra = root, home, role, session, dict(env or {})

    def as_(self, role="__keep__", session="__keep__", env=None):
        return Gov(self.root, self.home, self.role if role == "__keep__" else role,
                   self.session if session == "__keep__" else session, env if env is not None else self.extra)

    def run(self, *args):
        cmd = [GOV, "--json", "--root", self.root]
        if self.session:
            cmd += ["--session", self.session]
        if self.role:
            cmd += ["--role", self.role]
        cmd += list(args)
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        e.update({"HOME": self.home, "XDG_STATE_HOME": os.path.join(self.home, ".local/state"), "XDG_CACHE_HOME": os.path.join(self.home, ".cache"),
                  "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "r2", "GIT_COMMITTER_NAME": "r2", "GIT_AUTHOR_EMAIL": "r2@example.invalid",
                  "GIT_COMMITTER_EMAIL": "r2@example.invalid", "PATH": os.path.expanduser("~/.cargo/bin") + ":" + os.environ.get("PATH", "")})
        e.update(self.extra)
        p = subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=self.root)
        try:
            v = json.loads(p.stdout)
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-600:]}}
        shown = " ".join(a if (a and " " not in a) else json.dumps(a) for a in args)
        envd = " ".join(f"{k}={w}" for k, w in self.extra.items())
        log(f"$ {envd + ' ' if envd else ''}gov {shown}   [role={self.role} session={self.session} exit={p.returncode}] -> "
            + ("ok" if v.get("ok") else f"ERR {(v.get('error') or {}).get('code')}: {str((v.get('error') or {}).get('message'))[:160]}"))
        return v


def code(v):
    return (v.get("error") or {}).get("code") if not v.get("ok") else "OK"


def cause(v):
    return ((v.get("error") or {}).get("details") or {}).get("cause")


def res(v):
    return v.get("result") or {}


def git(root, *a):
    subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)


def repo(tag, files):
    base = os.path.join(SCRATCH, f"{tag}-{uuid.uuid4().hex[:6]}")
    root, home = os.path.join(base, "proj"), os.path.join(base, "home")
    os.makedirs(root)
    os.makedirs(home)
    for rel, text in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
    git(root, "init", "-q")
    git(root, "config", "user.email", "r2@example.invalid")
    git(root, "config", "user.name", "r2")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "baseline")
    log(f"# repo {tag}: {root}")
    return root, Gov(root, home)


def rd(root, rel):
    p = os.path.join(root, rel)
    return open(p).read() if os.path.exists(p) else None


def wr(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)


def yl(root, rel):
    import yaml
    return yaml.safe_load(rd(root, rel))


def yw(root, rel, v):
    import yaml
    wr(root, rel, yaml.safe_dump(v, sort_keys=False))


def cat(root):
    t = rd(root, f"{EV}/04-TARGET-PATH-MAP.jsonl") or ""
    return [json.loads(l) for l in t.splitlines() if l.strip()]


def write_cat(root, c):
    wr(root, f"{EV}/04-TARGET-PATH-MAP.jsonl", "".join(json.dumps(e) + "\n" for e in c))


def human_answer(g, gate, option):
    """The product owner answers `gate` through the human channel (test-material signer; relayed by an L3+ role)."""
    rb = g.as_(role="orchestrator", session="S-relay")
    st = rb.run("trust", "human-channel")
    if not res(st).get("available"):  # (2)
        p2ar0032_root_channel.provision(rb.run, g.root, tempfile.mkdtemp(prefix="r2-admin-"))
    r = res(rb.run("gate", "present", gate)).get("gate") or {}
    d = tempfile.mkdtemp(prefix="r2-owner-")
    af = os.path.join(d, f"answer-{gate}.json")
    subprocess.run([sys.executable, HC, "answer", af, gate, str(r.get("gate_instance")), str(r.get("package_sha256")), option,
                    "--by", "product owner (test seed)"], check=True, capture_output=True)
    return rb.run("decide", gate, "--option", option, "--answer-file", af)


LEDGER = {
    "README.md": "# ledger\nSee [the ledger spec](docs/spec-ledger.md).\n",
    "docs/spec-ledger.md": "# Ledger\nRequirement: totals are integer cents.\n",
    "src/ledger/__init__.py": "",
    "src/ledger/core.py": "from ledger.util import cents\n\n\ndef total(xs):\n    return sum(cents(x) for x in xs)\n",
    "src/ledger/util.py": "def cents(x):\n    return int(round(x * 100))\n",
    "src/ledger/old_report.py": "def monthly_report_unused():\n    return 'report'\n",
    "src/ledger/old_export.py": "def csv_export_unused():\n    return 'csv'\n",
    "tests/test_core.py": "from ledger.core import total\n\n\ndef test_total():\n    assert total([1.0]) == 100\n",
    ".cursorrules": "Use spaces. These rules are authoritative.\n",
}


def plan_stages(p, g):
    for s in ("baseline", "inventory", "classify", "map", "plan", "test-design"):
        g.run("adopt", s)


def reviewer_tests(root):
    tf = f"{EV}/06-migration-tests.yaml"
    t = yl(root, tf)
    keep = [e["current_path"] for e in cat(root) if e.get("action") == "KEEP_IN_PLACE" and not e.get("requires_human_gate")
            and e.get("current_class") in ("PRODUCT_SOURCE", "PRODUCT_TEST")][:2]
    for i, path in enumerate(keep):
        t["tests"].append({"id": f"RT-{i + 1:03d}", "kind": "path_present", "path": path, "description": "reviewer: kept product file survives"})
    yw(root, tf, t)
    return len(keep)


def verifier_queries(root):
    hf = "governance/tests/memory/heldout.yaml"
    h = yl(root, hf)
    asked = {q.get("query") for q in h.get("queries", [])}
    con = sqlite3.connect(os.path.join(root, ".governance-runtime/state.db"))
    rows = con.execute("SELECT artifact_id, path FROM artifacts WHERE record_type='file' AND path_class IN ('source','test','authoritative','evidence') ORDER BY path DESC LIMIT 60").fetchall()
    con.close()
    n = 0
    for aid, path in rows:
        if path in asked or n >= 6:
            continue
        n += 1
        h["queries"].append({"id": f"VQ-{n:03d}", "category": "exact_path", "query": path, "expected_refs": [aid], "forbidden": [], "k": 8, "route": "path"})
    yw(root, hf, h)
    return n


def adoption_checks():
    log("\n=== A5: designated reviewer role, declared fresh session, reviewer-authored tests (alpha-r N7, O3 §C/§D)")
    root, g = repo("a5", LEDGER)
    plan_stages(root, g)
    rv = lambda gg, *extra: gg.run("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", *extra)
    v = rv(g.as_(role="orchestrator", session="S-plan"))
    x("O3-C", not v.get("ok") and code(v) == "INDEPENDENCE", "[control] the planner session cannot review its own plan", code(v))
    v = rv(g.as_(role=None, session="S-r1"), "--reviewer-role", "migration-executor")
    x("N7-A5-role", not v.get("ok") and code(v) == "INDEPENDENCE", "A5 is refused for a declared role other than migration-reviewer (reviewer-role migration-executor)", [code(v), cause(v)])
    v = rv(g.as_(role="orchestrator", session="S-r2"))
    x("N7-A5-acting-L4", not v.get("ok"), "A5 is refused for the orchestrator (not the designated reviewer role)", [code(v), cause(v)])
    v = rv(g.as_(role="migration-reviewer", session=None))
    x("A5-session-undeclared", not v.get("ok") and code(v) == "ADOPTION_SESSION_UNDECLARED", "A5 is refused when no session is declared (a generated id is not authorship)", code(v))
    v = rv(g.as_(role="migration-reviewer", session=None, env={"GOV_SESSION": "S-plan"}), "--reviewer-session", "S-anything")
    x("O3-D-session", not v.get("ok") and code(v) in ("SESSION_CONFLICT", "INDEPENDENCE"), "the planner's session cannot approve by naming another --reviewer-session", code(v))
    rev = g.as_(role="migration-reviewer", session="S-rev")
    v = rv(rev)
    x("O3-D-zero-tests", not v.get("ok") and code(v) == "INDEPENDENT_TESTS_REQUIRED", "an approval with zero reviewer-authored tests (only the planner's scaffold) is refused", code(v))
    tf = f"{EV}/06-migration-tests.yaml"
    scaffold = rd(root, tf)
    t = yl(root, tf)
    t["tests"][0]["id"] = "RT-RELABEL"
    t["tests"][0]["description"] = "reviewer"
    yw(root, tf, t)
    v = rv(rev)
    x("O3-D-relabel", not v.get("ok") and code(v) == "INDEPENDENT_TESTS_REQUIRED", "a relabelled scaffold test is not a reviewer-authored test", code(v))
    wr(root, tf, scaffold)
    reviewer_tests(root)
    v = rv(rev)
    a5 = res(v).get("verdict") or {}
    x("A5-binds", v.get("ok") and all(len(str(a5.get(k) or "")) == 64 for k in ("catalogue_sha256", "plan_sha256", "tests_sha256")) and a5.get("role") == "migration-reviewer"
      and (a5.get("reviewer_tests_count") or 0) >= 1 and (a5.get("independence") or {}).get("established") is True,
      "the designated reviewer's approval binds catalogue, plan and tests digests and its own tests", {k: a5.get(k) for k in ("role", "session", "reviewer_tests", "catalogue_sha256", "tests_sha256")})


def execution_checks():
    log("\n=== A6/A7: execution and verdicts bound to what was approved (alpha-r N2), T2 record, gate subjects, zero tests")
    root, g = repo("a6", LEDGER)
    plan_stages(root, g)
    reviewer_tests(root)
    rev = g.as_(role="migration-reviewer", session="S-rev")
    rev.run("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    ex = g.as_(role="migration-executor", session="S-exec")
    mig = lambda *a: ex.run("adopt", "migrate", "--name", "ledger", "--alias", "r2-ledger", *a)
    tf, cf, pf, bf = f"{EV}/06-migration-tests.yaml", f"{EV}/04-TARGET-PATH-MAP.jsonl", f"{EV}/05-plan.yaml", f"{EV}/00-BASELINE.yaml"
    tests0, cat0, plan0, b0 = rd(root, tf), rd(root, cf), rd(root, pf), rd(root, bf)
    t = yl(root, tf)
    t["tests"] = []
    yw(root, tf, t)
    v = mig()
    x("N2-tests-emptied", not v.get("ok") and code(v) == "APPROVAL_STALE" and not os.path.exists(os.path.join(root, "governance/framework.lock")),
      "an executor that empties the approved tests after approval executes nothing", [code(v), ((v.get("error") or {}).get("details") or {}).get("changed")])
    wr(root, tf, tests0)
    c = cat(root)
    for e in c:
        if e["current_path"] == "src/ledger/util.py":
            e.update({"action": "DELETE_FROM_ACTIVE_TREE", "batch": 2, "requires_human_gate": False, "reason": "executor decided"})
    write_cat(root, c)
    v = mig()
    x("N2-keep-to-delete", not v.get("ok") and code(v) == "APPROVAL_STALE" and os.path.exists(os.path.join(root, "src/ledger/util.py")),
      "a KEEP turned into an ungated DELETE after approval is refused before any batch runs", [code(v), ((v.get("error") or {}).get("details") or {}).get("changed")])
    wr(root, cf, cat0)
    p = yl(root, pf)
    p["batches"] = p["batches"][:-1]
    yw(root, pf, p)
    v = mig()
    x("N2-plan-changed", not v.get("ok") and code(v) == "APPROVAL_STALE", "a plan changed after approval is refused", [code(v), ((v.get("error") or {}).get("details") or {}).get("changed")])
    wr(root, pf, plan0)
    b = yl(root, bf)
    b["verdicts"]["A5"]["tests_sha256"] = "0" * 64
    yw(root, bf, b)
    v = mig()
    x("T2-record", not v.get("ok") and code(v) == "T2_UNBOUND", "a hand-edited adoption record (verdict digest) is not honoured", code(v))
    wr(root, bf, b0)
    v = mig()
    x("A6-approved-executes", v.get("ok") and res(v).get("complete") is True and (res(v).get("approval") or {}).get("tests_sha256"),
      "[positive] the approved plan executes and reports the approval it executed", res(v).get("approval"))
    health = res(v).get("health") or {}
    x("G4-after-migration", health.get("tier") == "G4" and (health.get("health_result") or health.get("error")),
      "BC-P2-07: a completed migration runs the G4 tier (wider staleness after migration changes)", health)
    dead = [e for e in cat(root) if e.get("requires_human_gate") and e.get("action") == "DELETE_FROM_ACTIVE_TREE" and e.get("human_gate")]
    if len(dead) >= 2:
        e1, e2 = dead[0], dead[1]
        human_answer(g, e1["human_gate"], "A")
        human_answer(g, e2["human_gate"], "B")
        own = rd(root, cf)
        c = cat(root)
        for e in c:
            if e["artifact_id"] == e2["artifact_id"]:
                e["human_gate"] = e1["human_gate"]
        write_cat(root, c)
        ex.run("adopt", "migrate", "--batch", "7")
        x("gate-subject", not os.path.exists(os.path.join(root, e1["current_path"])) and os.path.exists(os.path.join(root, e2["current_path"])),
          "a gate answered A authorises only the entry it was raised for (another entry pointed at it stays)", {"e1": e1["current_path"], "e1_present": os.path.exists(os.path.join(root, e1["current_path"])), "e2": e2["current_path"], "e2_present": os.path.exists(os.path.join(root, e2["current_path"]))})
        wr(root, cf, own)
    else:
        x("gate-subject", False, "fixture yields two gated dead-code entries", [e["current_path"] for e in dead])
    log("--- A7")
    v = ex.run("adopt", "verify-migration")
    x("T1c-A7-executor", not v.get("ok") and code(v) == "INDEPENDENCE", "[control] the executor cannot verify its own migration", code(v))
    v = g.as_(role=None, session="S-v1").run("adopt", "verify-migration", "--verifier-role", "migration-executor")
    x("N7-A7-role", not v.get("ok") and code(v) == "INDEPENDENCE", "A7 is refused for verifier-role migration-executor", [code(v), cause(v)])
    v = g.as_(role="backend-engineer", session="S-v2").run("adopt", "verify-migration")
    x("N7-A7-acting-L1", not v.get("ok") and code(v) == "INDEPENDENCE", "A7 is refused for acting role backend-engineer", [code(v), cause(v)])
    v = g.as_(role="migration-verifier", session="S-rev").run("adopt", "verify-migration")
    x("role-consistency", not v.get("ok"), "the reviewer's session cannot come back as the migration verifier (one session, one role)", code(v))
    ver = g.as_(role="migration-verifier", session="S-ver")
    t = yl(root, tf)
    t["tests"] = []
    yw(root, tf, t)
    v = ver.run("adopt", "verify-migration", "--verdict", "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD")
    v2 = ver.run("adopt", "verify-migration")
    x("A7-zero-tests", not v.get("ok") and code(v) == "VERDICT_CONFLICT" and res(v2).get("verdict") == "MIGRATION_REJECTED_NEEDS_REPAIR",
      "an A7 acceptance is never computed from zero tests (tests emptied after execution)", [code(v), res(v2).get("verdict"), res(v2).get("tests")])
    wr(root, tf, tests0)
    t = yl(root, tf)
    t["tests"] = [x_ for x_ in t["tests"] if not str(x_.get("id", "")).startswith("RT-")]
    yw(root, tf, t)
    v = ver.run("adopt", "verify-migration")
    x("A7-bound-tests", res(v).get("verdict") == "MIGRATION_REJECTED_NEEDS_REPAIR", "A7 rejects when the tests it runs are not the approved ones (reviewer tests removed after approval)",
      [res(v).get("verdict"), res(v).get("approval_problems")])
    wr(root, tf, tests0)
    v = ver.run("adopt", "verify-migration")
    x("A7-accept", res(v).get("verdict") == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD" and ((res(v).get("tests") or {}).get("executed") or 0) >= 1,
      "[positive] the designated verifier accepts the approved migration on executed approved tests", res(v).get("tests"))
    log("--- A8/A9")
    c = cat(root)
    c0 = rd(root, cf)
    for e in c:
        if e["current_path"] == "src/ledger/util.py":
            e["reason"] = "edited after the migration was accepted"
    write_cat(root, c)
    v = ex.run("adopt", "extract-legacy")
    x("A8-bound", not v.get("ok") and code(v) == "APPROVAL_STALE", "A8 refuses a catalogue changed after A7 accepted the migration", code(v))
    wr(root, cf, c0)
    ex.run("adopt", "extract-legacy")
    ex.run("adopt", "build-memory")
    log("--- A10")
    mv = g.as_(role="memory-verifier", session="S-memv")
    v = mv.run("adopt", "verify-memory")
    x("A10-builder-set", not v.get("ok") and code(v) == "INDEPENDENT_HELDOUT_REQUIRED", "A10 does not accept on the builder-generated held-out set", code(v))
    hf = "governance/tests/memory/heldout.yaml"
    h0 = rd(root, hf)
    h = yl(root, hf)
    h["queries"] += [dict(q, id=f"VQ-COPY-{i}", k=5, category="verifier") for i, q in enumerate(h["queries"]) if not q.get("pending")]
    yw(root, hf, h)
    v = mv.run("adopt", "verify-memory")
    x("A10-relabel", not v.get("ok") and code(v) == "INDEPENDENT_HELDOUT_REQUIRED", "relabelled builder queries are not verifier-authored held-out tests", code(v))
    wr(root, hf, h0)
    verifier_queries(root)
    v = g.as_(role="migration-verifier", session="S-mv2").run("adopt", "verify-memory")
    x("A10-role", not v.get("ok") and code(v) == "INDEPENDENCE", "A10 is refused for a role other than memory-verifier", [code(v), cause(v)])
    v = mv.run("adopt", "verify-memory")
    r = res(v)
    x("A10-verifier-set", r.get("verdict") == "MEMORY_ACCEPTED_FOR_V4_AUDIT" and ((r.get("independent_heldout") or {}).get("queries") or 0) >= 5,
      "A10 accepts on held-out queries the memory verifier authored (measured on their own)", r.get("independent_heldout"))
    log("--- A11")
    v = ex.run("adopt", "audit")
    x("T1c-A11-executor", not v.get("ok") and code(v) == "INDEPENDENCE", "A11 is refused for the executor (its own session and role)", [code(v), cause(v)])
    v = g.as_(role="independent-auditor", session="S-exec").run("adopt", "audit")
    x("A11-builder-session", not v.get("ok") and cause(v) == "SAME_SESSION_AS_BUILDER", "A11 is refused in a session that executed the migration, even under the auditor role", [code(v), cause(v)])
    v = g.as_(role="independent-auditor", session="S-aud").run("adopt", "audit")
    r = res(v)
    x("A11-G5", v.get("ok") and r.get("tier") == "G5" and bool(r.get("audit")), "A11 by a fresh independent auditor is the G5 full suite, recorded", {k: r.get(k) for k in ("verdict", "tier", "audit", "health_result")})
    st = res(g.run("adopt", "status"))
    by = {s["stage"]: (s.get("by") or {}) for s in st.get("stages", [])}
    x("status-authorship", st.get("honoured") is True and by.get("A5", {}).get("role") == "migration-reviewer" and by.get("A11", {}).get("role") == "independent-auditor",
      "adopt status reports each independent verdict's role and that the record is honoured", {k: by.get(k) for k in ("A5", "A7", "A10", "A11")})


def single_agent_checks():
    log("\n=== alpha-r [N1]: one agent, one role (the adapter's orchestrator), no --session anywhere")
    root, g = repo("n1", LEDGER)
    one = g.as_(role="orchestrator", session=None)
    done = []
    for st in (["baseline"], ["inventory"], ["classify"], ["map"], ["plan"], ["test-design"], ["review", "--verdict", "MIGRATION_PLAN_APPROVED"], ["migrate"],
               ["verify-migration"], ["extract-legacy"], ["build-memory"], ["verify-memory"], ["audit", "--accept-exceptions"]):
        if one.run("adopt", *st).get("ok"):
            done.append(st[0])
    x("N1-no-sessions", "review" not in done and "audit" not in done, "one agent with no declared session cannot author the adoption (no independent stage passes)", done)
    log("\n=== one agent, one role, one declared session through every stage")
    root, g = repo("n1b", LEDGER)
    one = g.as_(role="orchestrator", session="S-one")
    for st in ("baseline", "inventory", "classify", "map", "plan", "test-design"):
        one.run("adopt", st)
    reviewer_tests(root)
    v = one.run("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    x("N1-one-role", not v.get("ok") and code(v) == "INDEPENDENCE", "[control] one declared role and session cannot approve its own plan", [code(v), cause(v)])


def g0_checks():
    log("\n=== BC-P2-07 host: the G0 guard at A6 refuses migration while a hard-block governs it")
    root, g = repo("g0", LEDGER)
    plan_stages(root, g)
    reviewer_tests(root)
    g.as_(role="migration-reviewer", session="S-rev").run("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    ex = g.as_(role="migration-executor", session="S-exec")
    ex.run("adopt", "migrate", "--batch", "0", "--name", "ledger", "--alias", "r2-g0")
    wr(root, "src/ledger/creds.py", 'KEY = "AKIAIOSFODNN7EXAMPLE"\n')
    g.run("doctor")
    v = ex.run("adopt", "migrate", "--batch", "1")
    x("G0-A6", not v.get("ok") and code(v) == "HEALTH_HARD_BLOCK" and os.path.exists(os.path.join(root, ".cursorrules")),
      "an active critical hard-block refuses the migration batch (operation adopt.migrate) before anything moves", code(v))
    os.remove(os.path.join(root, "src/ledger/creds.py"))
    v = ex.run("adopt", "migrate", "--batch", "1")
    x("G0-A6-released", v.get("ok"), "[positive] after the repair the guard re-evaluates and the batch runs", code(v))


def upstream_checks():
    log("\n=== BC-P2-10 export use (epsilon-r Q1.6-8): approval only from the owner-signed answer to the packet's export gate")
    root, g = repo("up", {"README.md": "# svc\n"})
    g.run("init", "--name", "svc", "--alias", "r2-up")
    inbox = os.path.join(os.path.dirname(root), "canonical", "lessons", "inbox")
    os.makedirs(inbox)
    for lid, what in (("L-0301", "an export"), ("L-0302", "a release")):
        yw(root, f"spec/lessons/{lid}.yaml", {"id": lid, "type": "lesson", "title": "t", "status": "ACTIVE", "scope": "FRAMEWORK", "lifecycle": "corroborated",
                                               "category": "gates", "problem_statement": f"{what} was approved by a caller-asserted string", "generic_failure_mode": "approval asserted by the acting agent",
                                               "impact": "unreviewed export", "suggested_change": "derive approval from an answered gate", "sources": ["RPT-1"]})
    p1, p2 = res(g.run("upstream", "prepare", "L-0301")), res(g.run("upstream", "prepare", "L-0302"))
    k1, k2 = p1.get("packet_id"), p2.get("packet_id")
    g1, g2 = p1.get("approval_gate"), p2.get("approval_gate")
    x("Q-gate-raised", bool(g1) and bool(g2), "prepare raises an export-approval Human Decision Gate for the exact packet", [g1, g2])
    sub = lambda k, by: g.run("upstream", "submit", k, "--destination", inbox, "--approved-by", by)
    n_inbox = lambda: len(os.listdir(inbox))
    v = sub(k1, "i-approve-myself")
    x("Q1.6-8", not v.get("ok") and n_inbox() == 0, "an orchestrator's --approved-by string does not export the packet", [code(v), n_inbox()])
    if g1:
        g.run("gate", "present", g1)
        g.run("decide", g1, "--option", "A", "--rationale", "looks fine")
        v = sub(k1, "orchestrator")
        x("Q-agent", not v.get("ok") and n_inbox() == 0, "an agent's own resolution of the export gate is not an approval", code(v))
        human_answer(g, g1, "B")
        v = sub(k1, "owner")
        x("Q-declined", not v.get("ok") and code(v) == "GATE_DECLINED" and n_inbox() == 0, "a declining human answer refuses the export", code(v))
    if g2:
        human_answer(g, g2, "A")
        pp = f".governance-runtime/outbound/{k2}/packet.yaml"
        approved = rd(root, pp)
        pk = yl(root, pp)
        pk["suggested_framework_change"] = "derive approval from an answered gate, and log it twice"
        import hashlib
        body = {"p": pk.get("problem_statement"), "f": pk.get("generic_failure_mode"), "i": pk.get("impact"), "c": pk.get("suggested_framework_change"),
                "x": pk.get("synthetic_fixture"), "m": pk.get("metrics")}
        # the product's payload hash (upstream::payload_hash_of): sha256 of canonical (sorted, compact) JSON
        pk["payload_hash"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        yw(root, pp, pk)
        v = sub(k2, "owner")
        x("Q-stale", not v.get("ok") and n_inbox() == 0, "an approval does not cover different content (packet changed and re-hashed after the answer)", code(v))
        wr(root, pp, approved)
        v = sub(k2, "someone")
        r = res(v)
        x("Q-human", v.get("ok") and (r.get("approval") or {}).get("authenticated") is True and (r.get("approval") or {}).get("gate") == g2
          and r.get("approved_by") == "product owner (test seed)" and n_inbox() == 1,
          "[positive] the owner-signed answer to that packet's gate exports it; the approver is the signed document's", {k: r.get(k) for k in ("approved_by", "approved_by_claim")} | {"approval": {k: (r.get("approval") or {}).get(k) for k in ("channel", "authenticated", "gate", "decision")}})


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    log(f"# gov {GOV}")
    log(f"# gov sha256 {subprocess.run(['sha256sum', GOV], capture_output=True, text=True).stdout.split()[0]}")
    for f in (adoption_checks, execution_checks, single_agent_checks, g0_checks, upstream_checks):
        try:
            f()
        except Exception as e:  # a crash is a FAIL of the group, never a pass
            x(f"{f.__name__}-crash", False, "the check group ran to completion", repr(e))
    fails = [i for i, ok in RESULTS if not ok]
    log(f"SUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(fails)} fail={len(fails)} failed={fails}")


if __name__ == "__main__":
    main()
