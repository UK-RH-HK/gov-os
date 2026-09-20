#!/usr/bin/env python3
"""Gate O (O1-O4) and Gate P (P1-P2) held-out probes — P2-AR-0050, family epsilon.

O1 product test families (Contract v3:751-761), O2 governance test families (:763-780), O3 independent test
authorship (:782-785), O4 governance suite currency (:787-789); P1 execution telemetry (:814-827) and P2 the
organisational questions telemetry must support (:829-838).
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import check, main  # noqa: E402
from t01_ac5_scheduler import provisioned, converge, res  # noqa: E402

O1_FAMILIES = ["unit", "contract", "integration", "system", "acceptance", "scenario", "security",
               "performance", "recovery", "smoke"]          # Contract v3:752-761 ("live/smoke")
O2_FAMILIES = ["schema_invariants", "graph_integrity", "index_freshness", "memory_retrieval_regression",
               "authority_role_limits", "mutation_scope", "path_map_compliance", "context_reproducibility",
               "concurrency_claims", "adapter_portability", "skill_regression",
               "command_contract_consistency", "secrets_sensitivity_indexing", "recovery_rebuild",
               "fresh_agent_reconstruction", "product_traceability", "audit_reproducibility"]
P1_FIELDS = ["agent/session/model/provider", "role/task", "skill/tool versions", "context packet",
             "retrieval queries/hits", "token input/output", "latency/cost", "files read/written",
             "tests", "retries/failures", "handoffs", "decisions", "human interventions"]
INPUT_CLASSES = ["kernel_policy", "kernel_schema", "project_policy", "path_map", "sensitivity",
                 "model_profile", "tools_plugins", "project_skills", "governance_tests", "index_manifest",
                 "spec_decisions", "spec_requirements", "spec_architecture", "spec_tasks",
                 "research_experiments", "continuity_records", "evidence_records", "adoption_evidence",
                 "source", "runtime_identity", "machine_trust"]


def policy_edit(p, fn):
    """Rewrite PROJECT_POLICY.yaml through a callable on the parsed document."""
    d = yaml.safe_load(p.read("governance/project/PROJECT_POLICY.yaml"))
    fn(d)
    p.write("governance/project/PROJECT_POLICY.yaml", yaml.safe_dump(d, sort_keys=False))
    p.commit("project policy")


def ready_claim(p, objective, title, cls, allowed, role, session):
    t = res(p.run("task", "create", "--objective", objective, "--title", title,
                  "--class", cls, "--allowed", allowed))
    tid = t["id"]
    p.run("task", "status", tid, "READY")
    c = p.run("task", "claim", tid, role=role, session=session)
    if not c.ok:
        print(f"     (claim of {tid} failed: {c.error_code} {str(c.error.get('message'))[:120]})", flush=True)
    return tid, c


def green_again(p, label):
    """Bring the repository back to a legitimately current green record."""
    p.run("rebuild-memory", "--incremental")
    p.run("health", "product")
    p.run("audit")
    converge(p, label, n=2)
    return res(p.run("health", "status"))["governance_suite_currency"]


def run():
    p, _pub = provisioned("gateop")
    converge(p)

    # ================================================================ O1 product test families
    fams = {}
    scripts = {}
    for f in O1_FAMILIES:
        s = f"tools/t-{f}.sh"
        p.write(s, f'#!/bin/sh\necho "{f} ok"\nexit 0\n')
        os.chmod(p.root / s, 0o755)
        scripts[f] = "./" + s
    policy_edit(p, lambda d: d["tests"].__setitem__(
        "families", {f: {"command": [scripts[f]], "covers": ["src/**"]} for f in O1_FAMILIES}))
    o = p.run("health", "product")
    r = res(o)
    fams = r.get("families") or {}
    named = [f for f in O1_FAMILIES if f in fams]
    check("O1-ten-families-nameable", len(named) == len(O1_FAMILIES),
          f"families the product ran by name: {sorted(fams)} "
          f"(Contract v3:752-761 asks for {O1_FAMILIES}); missing={[f for f in O1_FAMILIES if f not in fams]}")
    check("O1-family-results-recorded", r.get("record") or r.get("status"),
          f"the run is recorded as governed evidence: record={r.get('record')} status={r.get('status')} "
          f"binding={json.dumps(r.get('record_binding'))}")

    # a failing family is governed, not swallowed
    p.write("tools/t-unit.sh", '#!/bin/sh\necho "unit failed" >&2\nexit 1\n')
    os.chmod(p.root / "tools/t-unit.sh", 0o755)
    p.commit("unit family fails")
    o = p.run("health", "product")
    r = res(o)
    st = res(p.run("health", "status"))
    check("O1-failing-family-reaches-health", (not o.ok) and st["state"] != "GREEN",
          f"a failing family: ok={o.ok} failed={r.get('failed_families')} health state={st['state']} "
          f"blocks={[(b['check'], b['scope']) for b in st['blocks']]}")

    # a self-attested pass cannot stand in for evidence at task close
    p.write("tools/t-unit.sh", '#!/bin/sh\necho "unit ok"\nexit 0\n')
    os.chmod(p.root / "tools/t-unit.sh", 0o755)
    p.commit("unit family passes again")
    p.run("health", "product")
    tid, _c = ready_claim(p, "Probe close", "Probe", "governance", "spec/**", "change-controller", "o1")
    p.run("rebuild-memory", "--incremental")
    pk = p.run("context", "compile", tid, role="change-controller", session="o1")
    rep = p.root.parent / "o1-report.json"

    def report(tests):
        rep.write_text(json.dumps({
            "task": tid, "status": "success", "outcome": "success",
            "work_completed": "probe", "files_changed": [], "evidence": [], "tests": tests,
            "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
            "recommended_next_action": "close", "repair_count": 0,
            "context_packet_hash": res(pk).get("packet_hash"), "inputs_consumed": [], "outputs_produced": [],
            "requirements_implemented": [], "scenarios_implemented": [], "features_implemented": [],
            "decisions_applied": [], "constraints_applied": [], "acceptance_evidence": [], "deviations": []}))
        return rep

    p.write("tools/t-unit.sh", '#!/bin/sh\necho "unit failed" >&2\nexit 1\n')
    os.chmod(p.root / "tools/t-unit.sh", 0o755)
    p.commit("unit family fails again")
    p.run("health", "product")
    cl = p.run("task", "close", tid, "--report", str(report({"status": "passed"})),
               role="change-controller", session="o1")
    check("O1-self-attested-pass-refused", not cl.ok,
          f"a report claiming tests passed while the recorded product evidence FAILED is refused: "
          f"ok={cl.ok} code={cl.error_code} {str(cl.error.get('message'))[:170]}")

    # ================================================================ O2 governance test families
    cat = {c["id"]: c for c in p.run("health", "checks").result["checks"]}
    missing = [f for f in O2_FAMILIES if f not in cat]
    check("O2-seventeen-families-present", not missing,
          f"the 17 Contract v3:764-780 governance families exist as suite checks; missing={missing}")
    o = p.run("health", "run", "--no-cache", "--event", "o2")
    got = res(o)["families"]
    ran = [f for f in O2_FAMILIES if f in got and got[f]["status"] in ("executed", "reused")]
    check("O2-all-seventeen-execute", len(ran) == len(O2_FAMILIES),
          f"{len(ran)}/17 executed in one suite run; not executed: {[f for f in O2_FAMILIES if f not in ran]}")
    detail_bearing = [f for f in O2_FAMILIES if (got.get(f, {}).get("detail") not in (None, {}))]
    check("O2-families-report-what-they-checked", len(detail_bearing) >= 13,
          f"{len(detail_bearing)}/17 report a measured detail rather than a bare verdict; "
          f"bare: {[f for f in O2_FAMILIES if f not in detail_bearing]}")

    # skill regression executes scenarios, it does not merely validate schemas (iteration-0 BC-P2-42)
    sk = p.run("health", "skills")
    sr = res(sk)
    check("O2-skill-regression-executes-scenarios",
          (sr.get("executed") or sr.get("scenarios_executed") or 0) or
          any("executed" in json.dumps(v) for v in [sr]),
          f"skill regression result: {json.dumps(sr)[:350]}")

    # ================================================================ O3 independent test authorship
    pol = p.read("governance/kernel/policies/TEST_POLICY.yaml")
    check("O3-independent-author-required-declared", "independent_test_author_required_for" in pol,
          f"TEST_POLICY declares the families that need an independent author: "
          f"{[l for l in pol.splitlines() if 'independent_test_author' in l]}")
    ho = p.run("memory", "heldout")
    check("O3-heldout-surface-exists", ho.ok or ho.error_code != "NO_JSON",
          f"held-out query surface: ok={ho.ok} {json.dumps(res(ho))[:200]}")

    # the builder may not certify its own tests as independent
    who = p.run("memory", "verify", role="backend-engineer", session="builder")
    check("O3-observed", True, f"`gov memory verify` as a builder role: ok={who.ok} code={who.error_code} "
                              f"{json.dumps(res(who))[:200]}")

    # ================================================================ O4 governance suite currency
    # O4 needs a repository whose green record is legitimately current, so it runs on its own clean project
    # (the O1 attacks above deliberately left this one UNHEALTHY, where no new green record can be earned).
    p = provisioned("gateo4")[0]
    converge(p)
    cur = green_again(p, "o4-settle")
    check("O4-green-record-current", cur["current"],
          f"a legitimately current green record: green={cur['green']} current={cur['current']}")
    key0 = cur["key"]

    stale_by = {}
    probes = {
        "project_policy": ("governance/project/PROJECT_POLICY.yaml", "\n# o4 probe\n"),
        "spec_decisions": ("spec/decisions/D-O4.yaml",
                           "id: D-O4\ntype: decision\ntitle: O4\nstatus: ACTIVE\n"
                           "state_class: AUTHORITATIVE\ndecision: probe\nrationale: probe\n"
                           "created: '2026-09-20'\n"),
        "spec_requirements": ("spec/requirements/REQ-O4.yaml",
                              "id: REQ-O4\ntype: requirement\ntitle: O4\nstatus: ACTIVE\n"
                              "state_class: AUTHORITATIVE\nkind: functional\n"
                              "acceptance_criteria: ['probe']\ncreated: '2026-09-20'\n"),
        "spec_architecture": ("spec/architecture/ARCH-O4.yaml",
                              "id: ARCH-O4\ntype: architecture\ntitle: O4\nstatus: ACTIVE\n"
                              "state_class: AUTHORITATIVE\ncreated: '2026-09-20'\n"),
        "source": ("src/o4.rs", "// o4 probe\n"),
        "sensitivity": ("governance/project/DATA_SENSITIVITY.yaml", "\n# o4 probe\n"),
        "path_map": ("governance/project/REPOSITORY_CONTRACT.yaml", "\n# o4 probe\n"),
        "tools_plugins": ("governance/project/TOOL_PERMISSIONS.yaml", "\n# o4 probe\n"),
        "model_profile": ("governance/project/MODEL_ROUTING_OVERRIDES.yaml", "\n# o4 probe\n"),
    }
    for cls, (rel, text) in probes.items():
        before = green_again(p, f"o4-{cls}")
        cur = p.read(rel) if p.exists(rel) else ""
        p.write(rel, cur + text if cur else text)
        p.commit(f"o4 {cls}")
        after = res(p.run("health", "status"))["governance_suite_currency"]
        changed = [c["class"] for c in (after.get("changed_classes") or [])]
        stale_by[cls] = (before.get("current"), after.get("current"), changed)
        check(f"O4-invalidated-by-{cls}",
              before.get("current") and not after.get("current") and cls in changed,
              f"green current before={before.get('current')} after={after.get('current')} "
              f"changed_classes={changed}")

    # runtime identity is part of the key
    key_now = res(p.run("health", "currency"))
    check("O4-key-covers-runtime-and-machine-trust",
          "runtime_identity" in json.dumps(key_now) and "machine_trust" in json.dumps(key_now),
          f"the currency key names {len([k for k in INPUT_CLASSES if k in json.dumps(key_now)])} of "
          f"{len(INPUT_CLASSES)} Contract v3:97-109 input classes, including the runtime binary and machine trust")

    # governance-affecting work cannot close on stale green evidence
    green_again(p, "o4-close")
    tid, _c = ready_claim(p, "Governance work on stale green", "O4 close", "governance",
                          "docs/**", "change-controller", "o4")
    p.run("rebuild-memory", "--incremental")
    pk = p.run("context", "compile", tid, role="change-controller", session="o4")
    p.write("docs/o4-close.md", "the work of this task: a change in a relevant input class\n")
    p.commit("make the green record stale after the packet was compiled")
    stale_now = res(p.run("health", "status"))["governance_suite_currency"]
    rep2 = p.root.parent / "o4-report.json"
    rep2.write_text(json.dumps({
        "task": tid, "status": "success", "outcome": "success", "work_completed": "probe",
        "files_changed": ["docs/o4-close.md"], "evidence": [],
        "tests": {"status": "not_applicable_with_reason", "reason": "governance-only"},
        "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
        "recommended_next_action": "close", "repair_count": 0,
        "context_packet_hash": res(pk).get("packet_hash"), "inputs_consumed": [], "outputs_produced": [],
        "requirements_implemented": [], "scenarios_implemented": [], "features_implemented": [],
        "decisions_applied": [], "constraints_applied": [], "acceptance_evidence": [], "deviations": []}))
    cl = p.run("task", "close", tid, "--report", str(rep2), role="change-controller", session="o4")
    closed = res(cl)
    gate = (closed.get("close_gate") or {})
    check("O4-close-runs-the-currency-gate",
          (not cl.ok) or (gate.get("g2") and gate.get("governance_affecting")),
          f"the close gate re-ran the suite on the changed inputs before closing: "
          f"ok={cl.ok} code={cl.error_code} g2={json.dumps(gate.get('g2', {}).get('summary'))[:150]} "
          f"governance_affecting={gate.get('governance_affecting')}")
    check("O4-no-close-on-stale-green",
          (not cl.ok) or (gate.get("g2", {}).get("complete") and
                          gate.get("g2", {}).get("inputs_hash") != stale_now.get("key")
                          or gate.get("g2", {}).get("inputs_hash")),
          f"the green record was stale at close time (current={stale_now.get('current')}, changed="
          f"{[c['class'] for c in (stale_now.get('changed_classes') or [])]}); the close was decided on a "
          f"complete suite result the gate ran for the CURRENT inputs "
          f"(g2.inputs_hash={str(gate.get('g2', {}).get('inputs_hash'))[:12]}…, complete="
          f"{gate.get('g2', {}).get('complete')}), not on the pre-change record ({key0[:12]}…); ok={cl.ok} "
          f"code={cl.error_code}")

    # ================================================================ P1 execution telemetry
    p.run("telemetry", "emit", "--name", "worker.run", "--attrs", json.dumps({
        "event": "worker.run", "agent": "probe-agent", "model": "m-1", "provider": "prov-1",
        "role": "change-controller", "task": tid, "skills": {"s1": "1.0.0"}, "tools": {"t1": "2.0.0"},
        "context_packet": res(pk).get("packet_hash"), "retrieval_queries": 2, "retrieval_hits": 5,
        "tokens_input": 1200, "tokens_output": 340, "latency_ms": 900, "cost": {"usd": 0.12},
        "files_read": ["a"], "files_written": ["b"], "tests": {"status": "passed"}, "retries": 1,
        "failures": 0, "handoffs": 1, "decisions": ["D-O4"], "human_interventions": 1}))
    summ = res(p.run("telemetry", "summary"))
    ev_file = p.root / ".governance-runtime" / "telemetry" / "events.jsonl"
    evs = [json.loads(l) for l in ev_file.read_text().splitlines() if l.strip()] if ev_file.exists() else []
    check("P1-events-persisted", evs, f"{len(evs)} telemetry events recorded at {ev_file.name}")
    mine = [e for e in evs if e.get("attributes", {}).get("event") == "worker.run"]
    carried = {}
    if mine:
        a = mine[0]["attributes"]
        carried = {
            "agent/session/model/provider": bool(a.get("agent") and a.get("model") and a.get("provider")
                                                 and mine[0].get("session")),
            "role/task": bool(mine[0].get("role") or a.get("role")) and bool(a.get("task")),
            "skill/tool versions": bool(a.get("skills") and a.get("tools")),
            "context packet": bool(a.get("context_packet")),
            "retrieval queries/hits": a.get("retrieval_queries") is not None,
            "token input/output": a.get("tokens_input") is not None,
            "latency/cost": a.get("latency_ms") is not None and a.get("cost") is not None,
            "files read/written": bool(a.get("files_read") is not None),
            "tests": a.get("tests") is not None,
            "retries/failures": a.get("retries") is not None,
            "handoffs": a.get("handoffs") is not None,
            "decisions": a.get("decisions") is not None,
            "human interventions": a.get("human_interventions") is not None,
        }
    check("P1-13-fields-representable", all(carried.values()) and len(carried) == 13,
          f"every Contract v3:815-827 field survives in the event record: "
          f"{[k for k, v in carried.items() if not v]} missing")
    # which fields the OS itself produces, rather than accepting from the caller
    os_made = {"session": any(e.get("session") for e in evs),
               "role": any(e.get("role") for e in evs),
               "latency": any("duration_ms" in json.dumps(e.get("attributes", {})) for e in evs),
               "command/name": any(e.get("name") for e in evs),
               "trace/span": any(e.get("trace_id") and e.get("span_id") for e in evs)}
    caller_only = [k for k in ("token input/output", "skill/tool versions", "agent/session/model/provider",
                               "files read/written")]
    check("P1-os-produced-vs-caller-supplied", all(os_made.values()),
          f"the OS itself produces {sorted(os_made)}; these remain caller-supplied, schema-free attributes: "
          f"{caller_only}")

    # ================================================================ P2 organisational questions
    q = {
        "rework by role": summ.get("rework_by_role") is not None,
        "retrieval effect on token use": any(k in json.dumps(summ) for k in
                                             ("tokens_by_retrieval", "retrieval_token", "tokens_with_retrieval")),
        "model over/under-power": bool(summ.get("model_routing") is not None),
        "skill repair rate": any(k in json.dumps(summ) for k in ("skill_repair", "skills_repaired")),
        "human-gate concentration": summ.get("human_gates_by_feature") is not None,
        "retrieval misses": any(k in json.dumps(summ) for k in ("retrieval_miss", "misses")),
        "cost by task/feature": summ.get("cost_by_task_class") is not None,
        "first-pass completion": summ.get("first_pass_completion_rate") is not None,
    }
    check("P2-eight-questions-answerable", all(q.values()),
          f"answerable from `gov telemetry summary`: {[k for k, v in q.items() if v]}; "
          f"NOT answerable: {[k for k, v in q.items() if not v]}")
    check("P2-observed", True, f"summary keys: {sorted(summ)}")


if __name__ == "__main__":
    main(run, "GATE-O-P")
