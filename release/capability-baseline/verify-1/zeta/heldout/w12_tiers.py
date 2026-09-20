"""W12 — Gate-W health-scheduler integration across G0-G6 (Contract v3:1185-1192).

Held-out, P2-AR-0051. Each tier's Gate-W duty is exercised at the tier, not read from a catalogue.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def families_at(r, tier):
    h = r.run("health", "run", "--tier", tier)
    res = h.get("result") or (h.get("error") or {}).get("details") or {}
    return res, (res.get("families") or {})


def main():
    r = lib.Repo("w12")
    lib.seed_green(r)
    lib.seed_task(r, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    r.ok("task", "status", "TASK-0001", "READY")
    r.commit("seed")

    # ---- G0: blocks invalid authority / current-version substitution on privileged operations
    # a superseded governing input is a current-version substitution: the privileged operations
    # that would consume it (claim, close) must be refused, by name.
    r.ok("task", "claim", "TASK-0001", role="backend-engineer", session="impl1")
    r.put("spec/requirements/REQ-0050.yaml", """id: REQ-0050
type: requirement
title: Ledger CSV export v2
status: ACTIVE
version: 2
feature: F-0001
kind: functional
supersedes: [REQ-0001]
acceptance_criteria: [CSV contains one row per ledger entry, plus a header]
summary: supersedes REQ-0001
""")
    r.ok("task", "release", "TASK-0001", "--force", role="orchestrator", session="impl1")
    claim = r.run("task", "claim", "TASK-0001", role="backend-engineer", session="impl2")
    guard = r.run("health", "guard", "task.close", "--paths", "src/export.rs")
    lib.check("W12-G0", "G0 refuses the privileged operation that would consume a superseded "
                        "(non-current) authoritative input, naming the input and its successor",
              not claim.get("ok")
              and "REQ-0001" in json.dumps(claim.get("error"))
              and "REQ-0050" in json.dumps(claim.get("error")),
              json.dumps(claim.get("error"))[:450])
    gr = guard.get("result") or {}
    lib.check("W12-G0b", "the G0 guard surface is callable and returns a scoped admission decision "
                         "(operation, subjects, blocks, remedy)",
              guard.get("ok") and set(["operation", "allowed", "subjects", "blocks", "remedy"])
              <= set(gr), json.dumps(gr or guard.get("error"))[:350])
    os.rename(r.path("spec/requirements/REQ-0050.yaml"),
              os.path.join(r.state, "REQ-0050.yaml"))

    # ---- G1: invalidates affected dependency/lineage evidence after material mutations -------
    res5, _ = families_at(r, "G5")        # establish cached evidence
    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml").replace(
              "CSV contains one row per ledger entry",
              "CSV contains one row per ledger entry, plus a header"))
    res1, fam1 = families_at(r, "G1")
    executed = {k: v.get("status") for k, v in fam1.items()}
    lineage_families = {"graph_integrity", "upstream_change_propagation", "index_freshness"}
    reexecuted = [k for k in lineage_families & set(fam1)
                  if executed.get(k) == "executed"]
    lib.check("W12-G1", "after a material mutation the G1 tier re-executes (does not reuse) the "
                        "dependency/lineage evidence it invalidated",
              bool(reexecuted) and set(lineage_families) & set(fam1),
              json.dumps({"tier_families": executed, "re_executed": reexecuted}))
    ucp = fam1.get("upstream_change_propagation") or {}
    lib.check("W12-G1b", "the G1 tier includes the Gate-W dependency/lineage duty and reports the "
                         "invalidated dependents",
              bool(ucp) and "detail" in ucp,
              json.dumps(ucp)[:400])

    # ---- G2: verifies task input / consumption / traceability before task close --------------
    # in its own repository, so the only difference between the two closes is the receipt itself
    g2 = lib.Repo("w12g2")
    lib.seed_green(g2)
    lib.seed_task(g2, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    g2.ok("task", "status", "TASK-0001", "READY")
    g2.ok("task", "claim", "TASK-0001", role="backend-engineer", session="i1")
    g2.put("src/export.rs", "// implements REQ-0001\npub fn export() {}\n")
    g2.ok("rebuild-memory", "--incremental")
    g2.ok("verify", "product")
    good = g2.receipt("TASK-0001", ["src/export.rs"], work="implemented")
    bad = dict(good)
    for k in ("inputs_consumed", "requirements_implemented", "acceptance_evidence"):
        del bad[k]
    closed_bad = g2.close("TASK-0001", bad, role="backend-engineer", session="i1")
    closed_good = g2.close("TASK-0001", good, role="backend-engineer", session="i1")
    gate = (closed_good.get("result") or {}).get("close_gate") or {}
    lib.check("W12-G2", "the enforcing G2 close gate verifies the task's inputs, consumption and "
                        "traceability: a close with an invalid receipt is refused, an honest one "
                        "is accepted and its G2 health result is recorded on the report",
              not closed_bad.get("ok")
              and (closed_bad.get("error") or {}).get("code") == "RECEIPT_INVALID"
              and closed_good.get("ok")
              and (gate.get("g2") or {}).get("health_result"),
              json.dumps({"bad": (closed_bad.get("error") or {}).get("code"),
                          "good_g2": gate.get("g2")})[:500])

    # the *preview* of that gate must agree with it, or an operator is told a close is admissible
    # that the gate then refuses
    g2b = lib.Repo("w12g2b")
    lib.seed_green(g2b)
    lib.seed_task(g2b, "TASK-0001", fields={"required_data": ["DATA-0002"]})
    g2b.ok("task", "status", "TASK-0001", "READY")
    g2b.ok("task", "claim", "TASK-0001", role="backend-engineer", session="i1")
    g2b.put("src/export.rs", "// implements REQ-0001\npub fn export() {}\n")
    g2b.ok("rebuild-memory", "--incremental")
    g2b.ok("verify", "product")
    good2 = g2b.receipt("TASK-0001", ["src/export.rs"], work="implemented")
    bad2 = dict(good2)
    for k in ("inputs_consumed", "requirements_implemented", "acceptance_evidence"):
        del bad2[k]
    cc_bad = g2b.run("health", "close-check", "TASK-0001", "--report",
                     g2b.report_file(bad2, "bad.json"))
    real = g2b.close("TASK-0001", bad2, role="backend-engineer", session="i1")
    lib.check("W12-G2b", "`gov health close-check` (the preview of the G2 close gate) agrees with "
                         "the gate: it refuses the same invalid receipt the close refuses",
              not cc_bad.get("ok") or (cc_bad.get("result") or {}).get("allowed") is not True,
              json.dumps({"close_check_allowed": (cc_bad.get("result") or {}).get("allowed"),
                          "task_close": (real.get("error") or {}).get("code")}))

    # ---- G3: verifies mandatory-input continuity across checkpoint/handoff -------------------
    r.ok("checkpoint", "create", "--next-action", "gov continue", "--task", "TASK-0001")
    res3, fam3 = families_at(r, "G3")
    cch = fam3.get("continuity_checkpoint_handoff") or {}
    far = fam3.get("fresh_agent_reconstruction") or {}
    lib.check("W12-G3", "the G3 tier runs the checkpoint/handoff continuity and fresh-agent "
                        "reconstruction duties and reports their detail",
              bool(cch) and bool(far) and "detail" in cch,
              json.dumps({"continuity": cch, "fresh_agent": far})[:600])
    # and the continuity duty actually observes an input-level change
    r.put("spec/requirements/REQ-0001.yaml",
          r.read("spec/requirements/REQ-0001.yaml").replace(
              "plus a header", "plus a header and a checksum"))
    res3b, fam3b = families_at(r, "G3")
    cch2 = fam3b.get("continuity_checkpoint_handoff") or {}
    findings3 = [f for f in (res3b.get("findings") or [])
                 if f.get("family") == "continuity_checkpoint_handoff"]
    lib.check("W12-G3b", "a mandatory-input change makes the recorded checkpoint stale at G3, "
                         "naming the checkpoint",
              bool(findings3) and any("CKPT-" in json.dumps(f) for f in findings3),
              json.dumps([f.get("message", "")[:150] for f in findings3])[:500])
    _ = cch2

    # ---- G4: wider staleness / impact propagation after spec / decision / architecture change
    res4, fam4 = families_at(r, "G4")
    ucp4 = fam4.get("upstream_change_propagation") or {}
    det = ucp4.get("detail") or {}
    lib.check("W12-G4", "the G4 tier runs the wider staleness/impact propagation duty and names "
                        "the dependents a spec change reached",
              bool(ucp4) and any(det.get(k) for k in
                                 ("unpropagated", "invalidated_completed_tasks",
                                  "retest_open_tasks", "stale_reports")),
              json.dumps(det)[:500])
    # an architecture change is a milestone class: it is observed at G4, not G1
    r.put("spec/architecture/ARCH-0100.yaml",
          r.read("spec/architecture/ARCH-0100.yaml").replace(
              "pure function over the ledger store", "streaming pipeline"))
    res4b, fam4b = families_at(r, "G4")
    lib.check("W12-G4b", "an architecture (milestone-class) change is evaluated at G4",
              bool(fam4b.get("upstream_change_propagation")) and bool(fam4b.get("graph_integrity")),
              json.dumps(sorted(fam4b))[:400])

    # ---- G5: audits end-to-end lineage and orphan states -------------------------------------
    res5b, fam5 = families_at(r, "G5")
    lo = fam5.get("lineage_orphans") or {}
    gi = fam5.get("graph_integrity") or {}
    afh = fam5.get("artifact_flow_health") or {}
    lib.check("W12-G5", "the G5 tier audits end-to-end lineage, orphan states and the artifact-flow "
                        "metrics in one run",
              bool(lo) and bool(gi) and bool(afh)
              and "by_kind" in json.dumps(lo.get("detail") or {}),
              json.dumps({"lineage_orphans": (lo.get("detail") or {}).get("by_kind"),
                          "graph_integrity_ok": gi.get("ok"),
                          "artifact_flow_health_ok": afh.get("ok")})[:500])

    # ---- G6: injects hidden artifact-flow failures in sophisticated qualification -------------
    # Phase 2 generates no hidden fault (frozen gate contract AC-6); what is verifiable here is
    # that the G6 surface exists, names the injection kinds, and fails closed on unsound evidence.
    q_noargs = r.run("health", "qualify", "--kind", "not-a-kind", "--run-id", "Q1",
                     "--oracle", "/nonexistent/oracle.json", "--report", "/nonexistent/s.json")
    fake_oracle = os.path.join(r.state, "oracle.json")
    with open(fake_oracle, "w") as f:
        json.dump({"format": "governance-os.qualification-oracle", "faults": []}, f)
    q_bad = r.run("health", "qualify", "--kind", "hidden-test", "--run-id", "Q2",
                  "--oracle", fake_oracle, "--report", fake_oracle)
    fmt = r.run("oracle", "format")
    fr = fmt.get("result") or {}
    classes = json.dumps(fr)
    lib.check("W12-G6", "the G6 qualification surface exists, names the injection kinds and fails "
                        "closed on an unsound oracle / score report",
              not q_noargs.get("ok") and "hidden-test" in json.dumps(q_noargs.get("error"))
              and not q_bad.get("ok"),
              json.dumps({"unknown_kind": (q_noargs.get("error") or {}).get("message", "")[:200],
                          "unsound": (q_bad.get("error") or {}).get("code")}))
    lib.check("W12-G6b", "the qualification-oracle format covers artifact-flow fault classes and "
                         "is explicitly PROPOSED (no hidden fault may be generated in Phase 2)",
              "PROPOSED" in fr.get("status", "") and "fault_manifest" in classes,
              fr.get("status", "")[:200])

    # ---- every tier is addressable and carries a declared Gate-W duty ------------------------
    cat = r.ok("health", "checks")
    by_tier = {}
    for c in (cat.get("checks") or cat.get("catalogue") or []):
        for t in c.get("tiers") or []:
            by_tier.setdefault(t, []).append(c["id"])
    w_families = {"graph_integrity", "context_reproducibility", "product_traceability",
                  "continuity_checkpoint_handoff", "upstream_change_propagation",
                  "lineage_orphans", "artifact_flow_health", "task_contract_integrity"}
    covered = {t: sorted(set(v) & w_families) for t, v in sorted(by_tier.items())}
    lib.check("W12-01", "every tier G1-G6 has at least one Gate-W duty in the catalogue",
              all(covered.get(t) for t in ("G1", "G2", "G3", "G4", "G5", "G6")),
              json.dumps(covered))

    _ = (res5, res1, res3, res4, res5b)
    return lib.summary()


if __name__ == "__main__":
    sys.exit(main())
