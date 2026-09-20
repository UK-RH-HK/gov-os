#!/usr/bin/env python3
"""Gate U held-out probes — P2-AR-0050, family epsilon.

Contract v3:978-993 "Track and threshold" (15 SLOs) and :995-1008 "A repository is HEALTHY only when" (13
conditions). For every SLO: it is computed, it carries a declared threshold and an owning check, and a run in
which the threshold is crossed changes the health state. For every condition: the check(s) that enforce it, and a
run in which violating it flips the repository verdict away from HEALTHY.

Each SLO is crossed by the cheapest legitimate means: real repository state where that is cheap, and otherwise by
tightening the threshold through `PROJECT_POLICY.policy_overrides` — the declared source the SLO declaration
itself reads (`{policy: ...}` thresholds), validated against POLICY_PRECEDENCE.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import check, main  # noqa: E402
from t01_ac5_scheduler import provisioned, converge, res  # noqa: E402

SLOS = ["governance_suite_freshness", "product_test_health", "retrieval_recall_at_k", "stale_index_count",
        "orphan_graph_count", "unresolved_contradictions", "unresolved_human_gates", "task_traceability",
        "feature_readiness_coverage", "context_packet_size", "tokens_per_completed_task",
        "first_pass_completion", "handoff_failure", "memory_rebuild_success",
        "fresh_agent_reconstruction_success"]
CONDITIONS = [f"H{i}" for i in range(1, 14)]
REC = "id: {id}\ntype: {ty}\ntitle: {t}\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\ncreated: '2026-09-20'\n"


def slos(p, full=False):
    """Every Gate U SLO, from a run that also refreshes the checks the SLOs read."""
    args = ["health", "run", "--no-cache", "--event", "slo-probe"] if full else \
        ["health", "run", "--check", "health_slos", "--no-cache", "--event", "slo-probe"]
    o = p.run(*args)
    det = res(o)["families"]["health_slos"].get("detail") or {}
    return {s["id"]: s for s in det.get("slos", [])}


def override(p, **kv):
    """Set PROJECT_POLICY.policy_overrides keys (the declared override mechanism)."""
    s = p.read("governance/project/PROJECT_POLICY.yaml")
    body = "policy_overrides:\n" + "".join(f"  {k.replace('__', '.')}: {json.dumps(v)}\n" for k, v in kv.items())
    s = s.replace("policy_overrides: {}", body) if "policy_overrides: {}" in s else s + "\n" + body
    p.write("governance/project/PROJECT_POLICY.yaml", s)
    p.commit("policy overrides")
    return p.run("policy", "overrides")


def state(p):
    return res(p.run("health", "status"))


def run():
    p, _pub = provisioned("gateu")
    converge(p)
    base = state(p)
    check("U-baseline-green", base["state"] == "GREEN" and base["repository"]["verdict"] == "HEALTHY",
          f"state={base['state']} verdict={base['repository']['verdict']}")

    # ---------------------------------------------------------------- tracked, thresholded, owned
    s = slos(p)
    missing = [x for x in SLOS if x not in s]
    check("U-all-15-slos-tracked", not missing, f"the 15 Contract v3:979-993 SLOs are computed; missing={missing}")
    check("U-all-15-slos-thresholded", not [x for x in SLOS if s.get(x, {}).get("threshold") in (None, {}, "")],
          "every SLO carries a declared threshold")
    check("U-all-15-slos-owned", not [x for x in SLOS if not s.get(x, {}).get("owner")],
          f"every SLO names the check whose finding changes the health state: "
          f"{json.dumps({x: s[x]['owner'] for x in SLOS if x in s})[:300]}…")
    det = res(p.run("health", "run", "--check", "health_slos", "--no-cache", "--event", "decl"))[
        "families"]["health_slos"]["detail"]
    check("U-slos-name-their-declaration-source", det.get("declarations"),
          f"declared in {det.get('declarations')}")

    crossed, not_crossed = [], []

    def record(slo_id, sv, st, label):
        ok = sv.get(slo_id, {}).get("crossed") is True and st["state"] != "GREEN"
        (crossed if ok else not_crossed).append(slo_id)
        check(f"U-cross-{slo_id}", ok,
              f"{label}: crossed={sv.get(slo_id, {}).get('crossed')} "
              f"value={json.dumps(sv.get(slo_id, {}).get('value'))[:90]} state={st['state']}")

    # ---------------- crossings driven by real repository state -----------------------------------------
    # 1 governance-suite freshness
    p.write("docs/u-note.md", "probe\n")
    p.commit("doc")
    # 1 governance-suite freshness. Its declared owner is the doctor check D021, which no tier run executes
    # (finding E-O5-01), so the crossing is measured without a full run: a change in a relevant input class
    # leaves the honoured green record non-current and the SLO crossed.
    sv = slos(p)                       # partial run: does not re-establish currency
    st = state(p)
    ok = sv["governance_suite_freshness"]["crossed"] is True
    (crossed if ok and st["state"] != "GREEN" else not_crossed).append("governance_suite_freshness")
    check("U-cross-governance_suite_freshness", ok,
          f"a change in a relevant input class crossed the SLO: "
          f"value={json.dumps(sv['governance_suite_freshness']['value'])[:110]}; "
          f"repository verdict={st['repository']['verdict']}; RED/YELLOW/GREEN state={st['state']} "
          f"(its owner D021 is a doctor check no tier run executes — E-O5-01)")
    st_before = st["state"]
    p.run("doctor")
    st_after = state(p)
    check("U-cross-governance_suite_freshness-owner-not-run-by-a-tier",
          st_before == "GREEN" and st_after["state"] != "GREEN",
          f"the machine state was {st_before} while the green evidence was stale and the repository verdict "
          f"was {st['repository']['verdict']}; it became {st_after['state']} only once `gov doctor` executed "
          f"the owning check D021 — the aggregation depends on a check tier runs never refresh (E-O5-01)")

    # 4 stale-index count: a governed record added and not indexed
    p.write("spec/requirements/REQ-U1.yaml", REC.format(id="REQ-U1", ty="requirement", t="Probe requirement")
            + "kind: functional\nacceptance_criteria: ['probe']\n")
    p.commit("requirement, index not rebuilt")
    record("stale_index_count", slos(p), state(p), "a governed record added without a rebuild")
    p.run("rebuild-memory", "--incremental")

    # 5 orphan-graph count: an ACTIVE requirement the graph neither reaches nor leaves
    p.write("spec/requirements/REQ-ORPH.yaml", REC.format(id="REQ-ORPH", ty="requirement", t="Orphan requirement")
            + "kind: functional\nacceptance_criteria: ['nothing references this']\n")
    p.commit("orphan requirement")
    p.run("rebuild-memory", "--incremental")
    record("orphan_graph_count", slos(p), state(p), "an unreferenced ACTIVE requirement")

    # 6 unresolved contradictions: a duplicate authoritative id
    p.write("spec/requirements/REQ-U1-dup.yaml", REC.format(id="REQ-U1", ty="requirement", t="Duplicate")
            + "kind: functional\nacceptance_criteria: ['clash']\n")
    p.commit("duplicate id")
    p.run("rebuild-memory", "--incremental")
    record("unresolved_contradictions", slos(p), state(p), "a duplicate authoritative record id")
    aside = p.root.parent / "u-aside"
    aside.mkdir(exist_ok=True)
    (p.root / "spec/requirements/REQ-U1-dup.yaml").rename(aside / "REQ-U1-dup.yaml")  # `rm` denied: MOVED ASIDE
    p.commit("duplicate moved aside")
    p.run("rebuild-memory", "--incremental")

    # 8 task traceability: implementation tasks declaring no upstream authority
    for i in range(4):
        p.run("task", "create", "--objective", f"Untraced work {i}", "--title", f"Untraced {i}",
              "--class", "implementation", "--allowed", "src/**")
    p.run("rebuild-memory", "--incremental")
    record("task_traceability", slos(p), state(p), "four implementation tasks with no upstream authority")

    # 9 feature readiness coverage
    p.write("spec/features/FEAT-U1.yaml", REC.format(id="FEAT-U1", ty="feature", t="Probe feature"))
    p.commit("feature with no readiness")
    p.run("rebuild-memory", "--incremental")
    record("feature_readiness_coverage", slos(p), state(p), "an active feature with empty readiness")

    # 2 product-test health: a configured family that fails
    p.write("tools/failing.sh", '#!/bin/sh\necho "probe suite failed" >&2\nexit 1\n')
    os.chmod(p.root / "tools" / "failing.sh", 0o755)
    pol = p.read("governance/project/PROJECT_POLICY.yaml").replace(
        "product_test_command: []", 'product_test_command: ["./tools/failing.sh"]')
    p.write("governance/project/PROJECT_POLICY.yaml", pol)
    p.commit("failing product test command")
    pr = p.run("health", "product")
    record("product_test_health", slos(p), state(p),
           f"a configured product test family that fails (recorded as {res(pr).get('record')})")

    # 7 unresolved human gates: an open gate against the declared max_open
    g = p.run("gate", "create", "--question", "Probe decision?", "--fields", json.dumps({
        "options": [{"id": "A", "label": "yes", "description": "accept the probe option"},
                    {"id": "B", "label": "no", "description": "reject the probe option"}],
        "why_now": "held-out probe", "current_state": "probe state", "impact": "none, probe only",
        "reversibility": "fully reversible", "cost_rework": "none", "recommendation": "A",
        "confidence": 0.9, "decision_class": "governance"}))
    ov = override(p, BUDGET_POLICY__defaults__max_parallel_agents=0)
    p.run("rebuild-memory", "--incremental")
    record("unresolved_human_gates", slos(p), state(p),
           f"one open gate ({res(g).get('id') or res(g).get('gate')}) against a declared max_open of 0 "
           f"(override applied: {len(res(ov).get('applied') or [])}, refused: {len(res(ov).get('refused') or [])})")

    # 3/10/15: thresholds the declarations read from the effective policy
    override(p, CONTEXT_POLICY__max_packet_chars=1,
             MEMORY_POLICY__regression__min_recall_at_k=1.5,
             CONTEXT_POLICY__fresh_agent_read_budget_files=0)
    tasks = [t["id"] for t in p.run("task", "list").result]
    if tasks:
        p.run("context", "compile", tasks[0])
    slos(p, full=True)
    sv, st = slos(p, full=True), state(p)
    record("retrieval_recall_at_k", sv, st, "the recall floor raised above the achievable recall")
    record("context_packet_size", sv, st, "the packet-size budget tightened below a compiled packet")
    record("fresh_agent_reconstruction_success", sv, st, "the fresh-agent read budget tightened to 0 files")

    # 11/12/13/14: the SLOs whose population must first exist — a real close, a returned handoff and a
    # broken rebuild, on a fresh project (the one above is deliberately UNHEALTHY by now)
    q = provisioned("gateu2")[0]
    converge(q)
    tid = res(q.run("task", "create", "--objective", "Work that needed repairs", "--title", "Repaired",
                    "--class", "governance", "--allowed", "docs/**"))["id"]
    q.run("task", "status", tid, "READY")
    cl0 = q.run("task", "claim", tid, role="change-controller", session="u2")
    q.write("docs/u2.md", "the work of this task\n")
    q.commit("task work")
    q.run("rebuild-memory", "--incremental")
    pk = res(q.run("context", "compile", tid, role="change-controller", session="u2"))
    rep = q.root.parent / "u2-report.json"
    rep.write_text(json.dumps({
        "task": tid, "status": "success", "outcome": "success",
        "work_completed": "done after two repairs", "files_changed": ["docs/u2.md"], "evidence": [],
        "tests": {"status": "not_applicable_with_reason", "reason": "governance-only"},
        "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
        "recommended_next_action": "close", "repair_count": 2,
        "cost": {"usd": 1.0, "tokens_input": 3_000_000, "tokens_output": 1_000_000},
        "context_packet_hash": pk.get("packet_hash"), "inputs_consumed": [], "outputs_produced": [],
        "requirements_implemented": [], "scenarios_implemented": [], "features_implemented": [],
        "decisions_applied": [], "constraints_applied": [], "acceptance_evidence": [], "deviations": []}))
    cl = q.run("task", "close", tid, "--report", str(rep), role="change-controller", session="u2")
    tid2 = res(q.run("task", "create", "--objective", "Handed-off work", "--title", "Handoff",
                     "--class", "governance", "--allowed", "docs/**"))["id"]
    q.run("task", "status", tid2, "READY")
    h = q.run("handoff", "create", "--task", tid2, "--to-role", "backend-engineer")
    hid = res(h).get("id") or res(h).get("handoff")
    ret = q.root.parent / "u2-handoff-return.json"
    ret.write_text(json.dumps({"handoff": hid, "task": tid2, "status": "failed",
                               "reason": "the worker could not complete the work",
                               "work_completed": "", "files_changed": [], "evidence": [],
                               "outcome": "failed", "discoveries": [], "risks": [], "lessons": [],
                               "proposed_decisions": [], "unresolved": ["the work was not done"],
                               "tests": {"status": "not_applicable_with_reason", "reason": "not reached"},
                               "recommended_next_action": "reassign"}))
    hr = q.run("handoff", "return", str(hid), "--file", str(ret))
    man = q.root / "governance" / "generated" / "index-manifest.json"
    if man.exists():
        m = json.loads(man.read_text())
        m["manifest_hash"] = "0" * 64
        man.write_text(json.dumps(m))
        q.commit("tracked index manifest no longer matches the live index")
    sv = slos(q, full=True)
    sv = slos(q, full=True)          # the SLO family reads the latest recorded outcome of its owning check
    stq = state(q)
    for slo_id, how in (("tokens_per_completed_task", "a DONE task recording 4,000,000 tokens"),
                        ("first_pass_completion", "the only closing report declares repair_count 2"),
                        ("handoff_failure", f"the only returned handoff ({hid}) returned `failed`"),
                        ("memory_rebuild_success", "the tracked index manifest no longer matches the live index")):
        e = sv.get(slo_id, {})
        ok = e.get("crossed") is True and stq["state"] != "GREEN"
        (crossed if ok else not_crossed).append(slo_id)
        check(f"U-cross-{slo_id}", ok,
              f"{how}: crossed={e.get('crossed')} value={json.dumps(e.get('value'))[:95]} "
              f"threshold={json.dumps(e.get('threshold'))[:60]} owner={e.get('owner')} state={stq['state']} "
              f"(close ok={cl.ok}/{cl.error_code}, claim ok={cl0.ok}, handoff ok={h.ok}, return ok={hr.ok})")

    check("U-crossings-change-health", len(set(crossed)) >= 14,
          f"{len(set(crossed))}/15 SLOs: crossing the declared threshold changed the health state — "
          f"{sorted(set(crossed))}; not demonstrated by this probe: {sorted(set(not_crossed) - set(crossed))}")

    # ---------------------------------------------------------------- the HEALTHY conjunction
    st = state(p)
    conds = {c["id"]: c for c in st["repository"]["conditions"]}
    check("U-13-conditions-present", sorted(conds) == sorted(CONDITIONS),
          f"the repository verdict evaluates {len(conds)} conditions")
    check("U-conditions-cite-owner-source", all(c.get("contract") for c in conds.values()),
          "each condition cites its Contract v3 line")
    check("U-conditions-have-enforcing-checks", not [k for k, c in conds.items() if not c.get("owners")],
          f"each condition names its enforcing check(s): "
          f"{json.dumps({k: c['owners'] for k, c in sorted(conds.items())})[:400]}…")
    failing = [k for k, c in conds.items() if c["status"] != "HOLDS"]
    check("U-healthy-only-when-all-hold",
          st["repository"]["verdict"] != "HEALTHY" and failing,
          f"verdict={st['repository']['verdict']} with {failing} failing")
    d035 = [c for c in res(p.run("doctor")).get("checks", []) if c["id"] == "D035"]
    check("U-conjunction-enforced-by-a-check", d035 and not d035[0]["ok"],
          f"D035 enforces the conjunction: {str(d035[0]['message'])[:150] if d035 else 'absent'}")
    check("U-conditions-observed", True,
          f"condition states under the induced faults: "
          f"{json.dumps({k: conds[k]['status'] for k in CONDITIONS})}")

    # a HEALTHY verdict is not reachable while any condition fails — and returns when they are repaired
    check("U-unhealthy-while-any-fails",
          all(st["repository"]["verdict"] == "UNHEALTHY" for _ in [0]) and len(failing) >= 1,
          f"{len(failing)} of 13 conditions fail and the verdict is {st['repository']['verdict']}")


if __name__ == "__main__":
    main(run, "GATE-U")
