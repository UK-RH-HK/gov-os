"""Held-out probe library for Governance OS Phase 2, verification iteration 1, family zeta (Gate W).

Written by run P2-AR-0051 from Contract v3 Gate W (lines 1066-1194) and the product's observable CLI behaviour.
No builder test, builder probe or audit-of-record probe was copied. These files never enter the product tree.

Every probe builds its own disposable governed repository: `gov init` (bootstrap embedded payload, admitted on an
unprovisioned machine by OWNER-DECISION-P2-0002) into a throw-away directory with its own XDG_STATE_HOME, then
authors governed records directly as a project author would.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

WT = os.environ.get("ZETA_WT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)
GOV = os.environ.get("ZETA_GOV") or os.path.join(WT, "target", "release", "gov")
WORK = os.environ.get("ZETA_WORK") or os.path.join(tempfile.gettempdir(), "zeta-v1-work")

_RESULTS = []


def log(msg):
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def check(cid, desc, ok, detail=""):
    """One held-out assertion. Prints one PASS/FAIL line."""
    _RESULTS.append((cid, ok))
    line = "%s %-26s %s" % ("PASS" if ok else "FAIL", cid, desc)
    if detail:
        line += "\n        -> " + str(detail).replace("\n", "\n        ")
    log(line)
    return ok


def summary():
    bad = [c for c, ok in _RESULTS if not ok]
    log("---- %d checks, %d passed, %d failed%s" % (
        len(_RESULTS), len(_RESULTS) - len(bad), len(bad),
        (": " + ", ".join(bad)) if bad else ""))
    return 1 if bad else 0


class Repo:
    """A disposable governed repository on its own simulated machine."""

    def __init__(self, name, init=True):
        self.name = name
        self.root = os.path.join(WORK, name)
        self.state = os.path.join(WORK, name + ".machine")
        if os.path.exists(self.root):
            shutil.move(self.root, self.root + ".old-%d" % time.time())
        os.makedirs(self.root)
        os.makedirs(self.state, exist_ok=True)
        shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), self.root,
                        dirs_exist_ok=True)
        self.git("init", "-q")
        self.git("config", "user.email", "zeta@example.invalid")
        self.git("config", "user.name", "zeta")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "baseline")
        if init:
            r = self.run("init", "--name", name)
            assert r["ok"], r

    @classmethod
    def attach(cls, name):
        """Re-open a repository a previous probe built (no re-init), for interactive inspection."""
        r = cls.__new__(cls)
        r.name = name
        r.root = os.path.join(WORK, name)
        r.state = os.path.join(WORK, name + ".machine")
        return r

    # ---------------------------------------------------------------- plumbing
    def env(self, extra=None):
        e = dict(os.environ)
        e["XDG_STATE_HOME"] = self.state
        e["GOV_CANONICAL_ROOT"] = WT
        e.pop("GOV_SESSION", None)
        e.pop("GOV_ROLE", None)
        if extra:
            e.update(extra)
        return e

    def git(self, *args):
        return subprocess.run(["git"] + list(args), cwd=self.root,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, msg="probe"):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def run(self, *args, role="orchestrator", session="z1", env=None):
        """`gov --json ...`; returns the parsed envelope (never raises on a product refusal)."""
        cmd = [GOV, "--json", "--root", self.root, "--session", session, "--role", role] + [
            str(a) for a in args]
        p = subprocess.run(cmd, capture_output=True, text=True, env=self.env(env))
        try:
            return json.loads(p.stdout.strip() or "{}")
        except Exception:
            return {"ok": False, "error": {"code": "NO_JSON", "message": p.stdout + p.stderr}}

    def ok(self, *args, **kw):
        r = self.run(*args, **kw)
        if not r.get("ok"):
            raise AssertionError("gov %s failed: %s" % (" ".join(map(str, args)),
                                                        json.dumps(r.get("error"))))
        return r["result"]

    def err(self, *args, **kw):
        r = self.run(*args, **kw)
        assert not r.get("ok"), "gov %s unexpectedly succeeded" % " ".join(map(str, args))
        return r["error"]

    # ---------------------------------------------------------------- authoring
    def put(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        return path

    def read(self, rel):
        with open(os.path.join(self.root, rel)) as f:
            return f.read()

    def path(self, rel):
        return os.path.join(self.root, rel)

    def report_file(self, obj, name="report.json"):
        """`gov task close --report` takes a file path; keep it outside the repository tree."""
        p = os.path.join(self.state, name)
        with open(p, "w") as f:
            json.dump(obj, f)
        return p

    def close(self, task, report, **kw):
        return self.run("task", "close", task, "--report", self.report_file(report, task + ".json"),
                        **kw)

    def receipt(self, task, files, work="work done", **over):
        """A consumption receipt built from the task's own compiled packet's `receipt_contract`."""
        pkt = self.ok("context", "compile", task)
        c = pkt["receipt_contract"]
        rec = {
            "work_completed": work,
            "tests": {"status": "passed"},
            "files_changed": list(files),
            "context_packet_hash": pkt["packet_hash"],
            "inputs_consumed": ["%s@%s" % (i["id"], i["content_hash"]) for i in
                                c["acknowledge_inputs"]],
            "outputs_produced": list(files),
            "requirements_implemented": list(c["trace"].get("requirements", [])),
            "scenarios_implemented": list(c["trace"].get("scenarios", [])),
            "features_implemented": list(c["trace"].get("features", [])),
            "decisions_applied": list(c["trace"].get("decisions", [])),
            "constraints_applied": list(c["trace"].get("constraints", [])),
            "acceptance_evidence": [{"test": t, "result": "passed",
                                     "evidence": "tests/export_acceptance.rs::export_two_rows"}
                                    for t in c.get("tests_requiring_evidence", [])],
            "deviations": [],
            "unresolved": [],
        }
        rec.update(over)
        return rec


# --------------------------------------------------------------------- seed set
# A governed artefact flow that exercises every W1 artefact type the contract names.

READINESS_CELLS = [
    "intent_outcome", "user_actor", "journey_workflow", "scenarios", "inputs",
    "data_model_schema", "representative_test_data", "processing_algorithm",
    "expected_outputs", "functional_requirements", "non_functional_requirements",
    "ux_interactions", "backend_service_behaviour", "database_state_requirements",
    "interface_api_event_contracts", "security_privacy", "integrations", "devops_runtime",
    "observability", "performance_capacity", "cost_constraints", "recovery_fallback",
    "success_criteria", "failure_criteria", "independent_acceptance_tests",
    "documentation_operations",
]


def set_product_test_command(r, cmd=None):
    """Give the project a real, fast product-test command, so `tests.status: passed` is evidenced
    rather than asserted (the product refuses a passed claim it cannot run: PRODUCT_TEST_EVIDENCE_REQUIRED)."""
    script = r.path("run-product-tests.sh")
    with open(script, "w") as f:
        f.write("#!/bin/sh\necho 'test result: ok. 1 passed; 0 failed'\nexit 0\n")
    os.chmod(script, 0o755)
    pp = r.read("governance/project/PROJECT_POLICY.yaml")
    pp = pp.replace('product_test_command: []', 'product_test_command: ["./run-product-tests.sh"]')
    r.put("governance/project/PROJECT_POLICY.yaml", pp)


def seed_flow(r, feature="F-0001"):
    readiness = "\n".join("  %s: PRESENT" % c for c in READINESS_CELLS)
    r.put("spec/features/F-0001.yaml", """id: F-0001
type: feature
title: Export ledger
status: ACTIVE
version: 1
readiness:
%s
requirements: [REQ-0001]
scenarios: [SCN-0001]
acceptance_tests: [TO-0001]
interfaces: [IFC-0001]
summary: Export the ledger to CSV
""" % readiness)
    r.put("spec/requirements/REQ-0001.yaml", """id: REQ-0001
type: requirement
title: Ledger CSV export
status: ACTIVE
version: 1
feature: F-0001
kind: functional
acceptance_criteria: [CSV contains one row per ledger entry]
summary: The system must export the ledger as CSV.
consumers: [TASK-0001]
""")
    r.put("spec/decisions/D-0100.yaml", """id: D-0100
type: decision
title: Use RFC4180 CSV
status: ACTIVE
version: 1
question: Which CSV dialect?
options:
  - {id: RFC4180, description: the RFC 4180 dialect}
  - {id: TSV, description: tab separated}
chosen_option: RFC4180
rationale: interoperability
affects: [TASK-0001]
summary: CSV output follows RFC4180.
""")
    r.put("spec/scenarios/SCN-0001.yaml", """id: SCN-0001
type: scenario
title: Export a two-entry ledger
status: ACTIVE
feature: F-0001
actor: operator
given: [a ledger with two entries]
when: [the operator exports]
then: [a CSV with two rows is produced]
data_requirements: [DATA-0001]
success_criteria: [two rows present]
failure_criteria: [missing rows]
""")
    r.put("spec/tasks/TO-0001.yaml", """id: TO-0001
type: test-obligation
title: Acceptance test for ledger export
status: ACTIVE
family: acceptance
scenario: SCN-0001
requirements: [REQ-0001]
test_data: [DATA-0002]
test_path: tests/export_acceptance.rs
author_role: independent-tester
independent_of_implementer: true
summary: acceptance test obligation
""")
    # DATA-0001 is the scenario's *data requirement*; DATA-0002 is the test dataset designed for it
    # (Contract v3 H4 FEATURE -> SCENARIO -> DATA -> TEST DATA chain), with provenance recorded.
    # Both data records are registered through the product, so the OS records their authorship itself.
    r.ok("data", "register", "--fields", json.dumps({
        "id": "DATA-0001", "title": "Ledger entries data requirement", "data_kind": "requirement",
        "description": "the ledger entries the export scenario needs", "version": "1",
    }), role="data-engineer")
    r.ok("data", "register", "--fields", json.dumps({
        "id": "DATA-0002", "title": "Two-entry ledger sample", "data_kind": "test-dataset",
        "implements": ["DATA-0001"], "version": "1",
        "provenance": {"source_kind": "synthetic", "origin": "generated by the probe"},
        "summary": "test dataset realising DATA-0001",
    }), role="data-engineer")
    r.put("spec/interfaces/IFC-0001.yaml", """id: IFC-0001
type: interface
title: Export CLI contract
status: ACTIVE
version: "1"
kind: cli
contract:
  command: export --format csv
  exit_code: 0
summary: exported command contract
""")
    r.put("spec/architecture/ARCH-0100.yaml", """id: ARCH-0100
type: architecture
title: Layered export pipeline
status: ACTIVE
version: 1
summary: the exporter is a pure function over the ledger store
""")


TASK_FIELDS = {
    "requirements": ["REQ-0001"],
    "decisions": ["D-0100"],
    "scenarios": ["SCN-0001"],
    "acceptance_tests": ["TO-0001"],
    "required_data": ["DATA-0001"],
    "interfaces": ["IFC-0001"],
    "architecture": ["ARCH-0100"],
    "allowed_paths": ["src/**", "tests/**"],
}


RESEARCH = {
    "id": "RES-0001", "title": "CSV dialect survey", "question": "which CSV dialect?",
    "reason": "the exporter must interoperate with the customers' importers",
    "method": "read the RFCs and test three importers",
    "sources": ["RFC4180", "importer-a docs", "importer-b docs"],
    "measurements": ["3 of 3 importers accept RFC4180", "1 of 3 accepts TSV"],
    "uncertainty": "only three importers were reachable",
    "conclusion": "RFC4180 is the interoperable dialect",
    "confidence": 0.7,
    "summary": "survey of CSV dialects",
    "influences": ["D-0100"],
}

TO_0001 = """id: TO-0001
type: test-obligation
title: Acceptance test for ledger export
status: ACTIVE
family: acceptance
scenario: SCN-0001
requirements: [REQ-0001]
test_data: [DATA-0002]
test_path: tests/export_acceptance.rs
author_role: independent-test-designer
independent_of_implementer: true
summary: acceptance test obligation
"""


def seed_green(r):
    """A legitimately green baseline under Contract v3 (P2-ADJ-0003): the full H4 chain, with the
    acceptance test obligation and its test file authored by an independent session through a governed
    test-design task that closes with a valid consumption receipt."""
    set_product_test_command(r)
    seed_flow(r)
    os.remove(r.path("spec/tasks/TO-0001.yaml"))
    r.commit("seed")
    r.ok("task", "create", "--class", "test-design",
         "--objective", "author the acceptance test obligation", "--feature", "F-0001",
         "--id", "TASK-0100", "--fields", json.dumps({
             "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"],
             "allowed_paths": ["spec/tasks/**", "tests/**"],
             "role": "independent-test-designer",
             "readiness_cell": "independent_acceptance_tests"}))
    r.ok("task", "status", "TASK-0100", "READY")
    r.ok("task", "claim", "TASK-0100", role="independent-test-designer", session="tester1")
    r.put("spec/tasks/TO-0001.yaml", TO_0001)
    r.put("tests/export_acceptance.rs",
          "// acceptance test for REQ-0001 / SCN-0001\n#[test]\nfn export_two_rows() {}\n")
    r.ok("rebuild-memory", "--incremental")
    r.ok("verify", "product")
    files = ["spec/tasks/TO-0001.yaml", "tests/export_acceptance.rs"]
    rep = r.receipt("TASK-0100", files, work="authored TO-0001 and its acceptance test")
    out = r.run("task", "close", "TASK-0100", "--report", r.report_file(rep, "TASK-0100.json"),
                role="independent-test-designer", session="tester1")
    assert out.get("ok"), json.dumps(out.get("error"))[:1500]
    r.commit("test design closed")
    return out["result"]


def seed_task(r, tid="TASK-0001", fields=None, feature="F-0001", cls="implementation"):
    f = dict(TASK_FIELDS)
    if fields:
        f.update(fields)
    return r.ok("task", "create", "--class", cls, "--objective", "implement CSV export",
                "--feature", feature, "--id", tid, "--fields", json.dumps(f))
