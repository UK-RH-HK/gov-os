#!/usr/bin/env python3
"""P2-AR-0042 (BC-P2-02) — PLANTED-FAULT evidence: for a sample of tier owners per gate, the owner, run by the
product (`gov health run --check <id>` / `gov doctor`), reports the capability broken once a fault that breaks it is
planted, and reports nothing of the kind on the same project before the fault (negative control).

Builder evidence (Contract v3 O3), labelled PLANTED-FAULT. Drives `gov` (env GOV) on disposable projects: each case gets
its own project (bootstrap installation of the binary's embedded payload on a private unprovisioned machine: HOME,
XDG_STATE_HOME and XDG_CACHE_HOME under the scratch directory, env SCRATCH), every invocation declaring its role.
Prints one line per case:

  CASE <gate> <owner> BEFORE ok=<bool> n=<findings> AFTER ok=<bool> n=<findings> -> DETECTED|NOT_DETECTED  <evidence>
"""
import json
import os
import shutil
import subprocess
import sys

GOV = os.environ["GOV"]
SCR = os.environ["SCRATCH"]
os.makedirs(SCR, exist_ok=True)
BASE_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}


def env_for(tag):
    e = dict(BASE_ENV)
    e.update({"HOME": os.path.join(SCR, tag, "home"), "XDG_STATE_HOME": os.path.join(SCR, tag, "state"),
              "XDG_CACHE_HOME": os.path.join(SCR, tag, "cache"), "GIT_CONFIG_GLOBAL": "/dev/null",
              "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@example.invalid",
              "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid"})
    os.makedirs(e["HOME"], exist_ok=True)
    return e


class Proj:
    def __init__(self, tag):
        self.tag = tag
        self.root = os.path.join(SCR, tag, "proj")
        if os.path.exists(os.path.join(SCR, tag)):
            os.rename(os.path.join(SCR, tag), os.path.join(SCR, f".old-{tag}-{os.getpid()}"))
        os.makedirs(os.path.join(self.root, "src"))
        self.env = env_for(tag)
        self.w("README.md", "# planted-fault probe\n")
        self.w("src/lib.rs", "pub fn total(a: i64, b: i64) -> i64 { a + b }\n")
        self.git("init", "-q")
        self.commit("baseline")
        d = self.gov("init", "--name", tag, "--alias", tag)
        assert d.get("ok"), d
        self.commit("installed")
        d = self.gov("rebuild-memory")
        assert d.get("ok"), d

    def w(self, rel, text):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)

    def wj(self, rel, value):  # YAML is a superset of JSON
        self.w(rel, json.dumps(value, indent=1) + "\n")

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.root, env=self.env, capture_output=True, text=True)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-qm", msg)

    def gov(self, *a, role="orchestrator"):
        r = subprocess.run([GOV, "--json", "--root", self.root, "--session", "S-fault", "--role", role, *a],
                           cwd=self.root, env=self.env, capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            return {"ok": False, "raw": (r.stdout + r.stderr)[-600:]}

    def check(self, owner):
        """(ok, finding messages) of one owner, run by the product."""
        kind, ref = owner.split(":", 1)
        if kind == "doctor":
            d = self.gov("doctor")
            for c in (d.get("result") or {}).get("checks", []):
                if c["id"] == ref:
                    return c["ok"], ([] if c["ok"] else [c.get("message", "")])
            return None, [f"no doctor check {ref}: {str(d)[:300]}"]
        d = self.gov("health", "run", "--check", ref, "--no-persist", "--no-cache")
        r = d.get("result") or {}
        fam = (r.get("families") or {}).get(ref)
        if fam is None:
            return None, [f"not run: {str(d)[:300]}"]
        msgs = [x.get("message", "") for x in r.get("findings", []) if x.get("family") == ref]
        return fam.get("ok"), msgs


results = []


def case(gate, capability, owner, plant, expect, rebuild=False, commit=True):
    p = Proj(f"{gate.lower()}-{owner.split(':')[1].replace(' ', '_')}")
    ok0, m0 = p.check(owner)
    plant(p)
    if commit:
        p.commit("planted fault")
    if rebuild:
        p.gov("rebuild-memory")
    ok1, m1 = p.check(owner)
    hit = [m for m in m1 if expect.lower() in m.lower()]
    before_hit = [m for m in m0 if expect.lower() in m.lower()]
    detected = ok1 is False and bool(hit) and not before_hit
    line = (f"CASE {gate} {capability} {owner} BEFORE ok={ok0} n={len(m0)} AFTER ok={ok1} n={len(m1)} -> "
            f"{'DETECTED' if detected else 'NOT_DETECTED'}  {(hit or m1 or ['-'])[0][:220]}")
    print(line, flush=True)
    results.append((gate, detected))


def secret(p):
    p.w("src/creds.rs", "pub const API_KEY: &str = \"AKIAIOSFODNN7EXAMPLE\";\n")


def gitignore_runtime(p):
    t = open(os.path.join(p.root, ".gitignore")).read()
    p.w(".gitignore", "".join(l for l in t.splitlines(True) if ".governance-runtime" not in l))


def dangling(p):
    p.wj("spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE"})
    p.wj("spec/requirements/REQ-0004.yaml", {"id": "REQ-0004", "type": "requirement", "title": "Dangling",
                                              "status": "ACTIVE", "feature": "F-0001", "depends_on": ["REQ-9999"]})


def stale_index(p):
    p.w("README.md", "# planted-fault probe\nedited after the index was built\n")


def unregistered_plugin(p):
    p.wj("governance/project/plugins/sneaky.yaml",
         {"plugin_id": "sneaky", "capability": "embed", "version": "1", "command": ["sh", "tools/sneaky.sh"],
          "permissions": {"network": False, "filesystem_write": False}, "required_permission_classes": [],
          "health_check": {"kind": "protocol_ping"}})
    p.w("tools/sneaky.sh", "#!/bin/sh\necho hi\n")


def unknown_cli(p):
    rel = "governance/kernel/commands/COMMAND_CONTRACT.yaml"
    t = open(os.path.join(p.root, rel)).read()
    t = t.replace("internal_operations:\n", "internal_operations:\n  - {operation: planted_op, cli: \"frobnicate --all\"}\n", 1)
    p.w(rel, t)


def silent_readiness(p):
    p.wj("spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE",
                                        "readiness": {"intent_outcome": "N/A"}})


def dag_cycle(p):
    for a, b in [("TASK-0101", "TASK-0102"), ("TASK-0102", "TASK-0101")]:
        p.wj(f"spec/tasks/{a}.yaml", {"id": a, "type": "task", "title": a, "class": "documentation",
                                       "status": "READY", "objective": "o", "depends_on": [b]})


def incomplete_research(p):
    p.wj("spec/research/RES-0001.yaml", {"id": "RES-0001", "type": "research", "title": "Unsupported",
                                          "status": "ACTIVE", "question": "which store?"})
    p.wj("spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Use the store",
                                         "status": "ACTIVE", "question": "which store?", "evidence_refs": ["RES-0001"]})


def unapproved_cit(p):
    p.wj("spec/decisions/CIT-0001.yaml", {"id": "CIT-0001", "type": "cit", "title": "Change without approval",
                                           "status": "ACTIVE", "cit_status": "COMMITTED", "manifest": []})


def forged_gate(p):
    p.wj("spec/decisions/HDG-0001.yaml", {"id": "HDG-0001", "type": "human-gate", "title": "Forged",
                                           "status": "ACTIVE", "gate_status": "ANSWERED", "question": "ship?",
                                           "answer": {"option": "A", "by": "owner"}, "presented_in_chat": True})


def unrouted_class(p):
    p.wj("spec/tasks/TASK-0201.yaml", {"id": "TASK-0201", "type": "task", "title": "t", "class": "astrology",
                                        "status": "READY", "objective": "o"})


def orphan_handoff(p):
    p.wj("spec/planning/HND-0001.yaml", {"id": "HND-0001", "type": "handoff", "title": "h", "status": "ACTIVE",
                                          "task": "TASK-9999", "to_role": "backend-engineer"})


def invalid_record(p):
    p.wj("spec/decisions/D-0009.yaml", {"id": "D-0009", "type": "decision", "status": "NOT_A_STATUS"})


def legacy_rules(p):
    p.w("CLAUDE.md", "# Project rules\nAlways follow these instructions. You must never edit the database.\n")
    p.w(".cursorrules", "Always use tabs. Never touch migrations.\n")


def forged_adoption_baseline(p):
    p.wj("spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml",
         {"id": "AUD-ADOPT-BASELINE", "type": "audit", "title": "baseline", "status": "ACTIVE",
          "scope": "adoption-baseline", "stage": "A0", "verdict": "SAFE"})


def orphan_feature(p):
    p.wj("spec/features/F-0007.yaml", {"id": "F-0007", "type": "feature", "title": "Nobody consumes me",
                                        "status": "ACTIVE"})


def orphan_requirement(p):
    p.wj("spec/requirements/REQ-0007.yaml", {"id": "REQ-0007", "type": "requirement", "title": "Never implemented",
                                              "status": "ACTIVE", "kind": "functional"})


print(f"# gov {GOV}", flush=True)
case("A", "A3", "check:path_map_compliance", secret, "secret")
case("A", "A3", "doctor:D011", secret, "secret")
case("B", "B1", "doctor:D024", gitignore_runtime, ".governance-runtime")
case("C", "C2", "check:graph_integrity", dangling, "REQ-9999", rebuild=True)
case("D", "D1", "check:index_freshness", stale_index, "README.md")
case("F", "F4", "check:plugin_governance", unregistered_plugin, "sneaky")
case("G", "G2", "check:command_contract_consistency", unknown_cli, "frobnicate", commit=False)
case("H", "H2", "check:feature_readiness", silent_readiness, "F-0001")
case("I", "I1", "check:graph_integrity", dag_cycle, "cycle", rebuild=True)
case("J", "J1", "check:research_experiment_data_lifecycle", incomplete_research, "RES-0001")
case("K", "K2", "check:change_control_integrity", unapproved_cit, "CIT-0001")
case("L", "L3", "check:os_binding_integrity", forged_gate, "HDG-0001")
case("M", "M1", "check:model_routing_integrity", unrouted_class, "astrology")
case("N", "N1", "check:continuity_checkpoint_handoff", orphan_handoff, "TASK-9999")
case("O", "O2", "check:schema_invariants", invalid_record, "D-0009")
case("R", "R1", "check:legacy_authority", legacy_rules, "")
case("T", "T3", "check:os_binding_integrity", forged_adoption_baseline, "00-BASELINE")
case("U", "U", "check:health_slos", orphan_feature, "F-0007", rebuild=True)
case("U", "U", "doctor:D035", secret, "")
case("W", "W7", "check:lineage_orphans", orphan_requirement, "REQ-0007", rebuild=True)
print(f"# SUMMARY detected {sum(1 for _, d in results if d)}/{len(results)}; gates "
      f"{sorted(set(g for g, d in results if d))}", flush=True)
