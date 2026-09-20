#!/usr/bin/env python3
"""AC-5 / O5 held-out probes — P2-AR-0050, verification iteration 1, family epsilon.

Every behaviour AC-5 names, established by *exercising* the scheduler on a disposable provisioned project:
impacted-check selection from a real mutation; parallel execution of independent checks; safe isolation; cache
reuse; cache invalidation; stale evidence; RED/YELLOW/GREEN aggregation; hard-block vs warning semantics;
health-result provenance; remediation/task generation; and that a trivial mutation does not serially re-run the
whole suite. Also the G0-G6 tier duties (Contract v3:793-799).
"""
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Project, check, main  # noqa: E402
import srr  # noqa: E402


def tree_digest(root, rel):
    d = root / rel
    if not d.exists():
        return "absent"
    h = hashlib.sha256()
    for dp, _dn, fn in sorted(os.walk(d)):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            h.update(os.path.relpath(p, d).encode())
            try:
                h.update(open(p, "rb").read())
            except OSError:
                pass
    return h.hexdigest()


def provisioned(name):
    """A project on a machine provisioned with the verifier's throw-away root, installed from a signed release."""
    p = Project(name)
    pub = srr.Publisher()
    admin = p.root.parent / f"admin-{p.root.name}"
    admin.mkdir(parents=True, exist_ok=True)
    root_file = pub.root_file(admin / "root.json")
    assert p.run("trust", "provision", "--anchor", str(root_file)).ok, "provision"
    # stage the payload the binary would install, and publish it as a signed release under that root
    boot = Project(name + "-boot")
    assert boot.init().ok, "bootstrap init"
    rel = admin / "release-current"
    rel.mkdir(parents=True, exist_ok=True)
    srr.stage_payload(str(boot.root / "governance" / "kernel"), str(rel / "kernel"))
    srr.publish(pub, str(rel))
    o = p.run("init", "--source", str(rel / "kernel"))
    assert o.ok, f"init --source: {o.error}"
    p.commit("init")
    return p, pub


def converge(p, label="converge", n=3):
    last = None
    for i in range(n):
        last = p.run("health", "run", "--event", f"{label}-{i}")
    return last


def res(o):
    return o.result if o.ok else (o.details or {})


def run():
    p, _pub = provisioned("ac5")
    last = converge(p)
    r = res(last)
    check("AC5-green-baseline", r.get("state") == "GREEN",
          f"a legitimately green baseline under Contract v3 (P2-ADJ-0003): state={r.get('state')} "
          f"counts={json.dumps(r.get('counts'))}")

    total = len(p.run("health", "checks").result["checks"])
    fam_total = len([c for c in p.run("health", "checks").result["checks"]
                     if c["surface"] == "governance-family"])

    # ---------------------------------------------------------------- 1. impacted-check selection
    p.write("src/trivial.rs", "// a trivial comment\n")
    p.commit("trivial source comment")
    t0 = time.time()
    o = p.run("health", "run", "--changed", "src/trivial.rs", "--event", "trivial-mutation")
    wall_sel = time.time() - t0
    s = res(o)["summary"]
    sel_exec, sel_reuse = s["executed"], s["reused"]
    check("AC5-1-impacted-selection", sel_reuse > 0 and sel_exec < fam_total,
          f"a one-line source comment executed {sel_exec}/{fam_total} checks and reused {sel_reuse}")

    # a *different* input class selects a different set
    p.write("spec/decisions/D-EPS-1.yaml",
            "id: D-EPS-1\ntype: decision\ntitle: Probe decision\nstatus: ACTIVE\n"
            "state_class: AUTHORITATIVE\ndecision: probe\nrationale: probe\ncreated: '2026-09-20'\n")
    p.commit("decision record")
    o2 = p.run("health", "run", "--changed", "spec/decisions/D-EPS-1.yaml", "--event", "decision-mutation")
    s2 = res(o2)["summary"]
    check("AC5-1b-selection-is-dependency-aware",
          set(s2["executed_checks"]) != set(s["executed_checks"]),
          f"a decision-record change selects a different set ({len(s2['executed_checks'])} checks) "
          f"from a source change ({len(s['executed_checks'])})")

    # ---------------------------------------------------------------- 2. parallel execution
    o = p.run("health", "run", "--no-cache", "--event", "parallel-probe")
    par = res(o).get("parallelism") or {}
    check("AC5-2-parallel-workers", par.get("workers", 0) > 1 and len(par.get("threads_used", [])) > 1,
          f"workers={par.get('workers')} threads={par.get('threads_used')}")
    rid = res(o)["health_result"]
    rec = p.run("health", "show", rid).result
    per_check_ms = sum(c.get("duration_ms", 0) for c in rec["checks"] if c.get("cached_from") is None)
    check("AC5-2b-wall-clock-below-serial-sum", rec["duration_ms"] < per_check_ms,
          f"run wall {rec['duration_ms']}ms < sum of executed check durations {per_check_ms}ms "
          f"(serial execution is impossible below the sum)")

    # ---------------------------------------------------------------- 3. isolation
    before = (tree_digest(p.root, ".governance-runtime/index"),
              tree_digest(p.root, "governance/generated"),
              tree_digest(p.root, ".governance-state"))
    sandbox_checks = [c["id"] for c in p.run("health", "checks").result["checks"]
                      if c["isolation"] in ("Sandbox", "OwnSandboxes")]
    o = p.run("health", "run", "--no-cache", *sum([["--check", c] for c in sandbox_checks], []),
              "--event", "isolation-probe")
    fams = res(o).get("families", {})
    isolated = [k for k, v in fams.items() if (v.get("detail") or {}).get("isolated_in_sandbox") is True]
    after = (tree_digest(p.root, ".governance-runtime/index"),
             tree_digest(p.root, "governance/generated"),
             tree_digest(p.root, ".governance-state"))
    check("AC5-3-isolation", before == after and len(isolated) >= 1,
          f"state-writing checks {sandbox_checks} ran; {len(isolated)} report isolated_in_sandbox; "
          f"live derived state unchanged: {before == after}")
    sbox = p.root / ".governance-runtime" / "health" / "sandboxes"
    check("AC5-3b-sandboxes-disposed", (not sbox.exists()) or not any(sbox.iterdir()),
          f"no sandbox left behind under {sbox}")

    # ---------------------------------------------------------------- 4/5. cache reuse and invalidation
    converge(p, "settle")
    o = p.run("health", "run", "--event", "cache-reuse")
    s = res(o)["summary"]
    never = [c["id"] for c in p.run("health", "checks").result["checks"] if c["cache"] == "Never"]
    check("AC5-4-cache-reuse", s["reused"] > s["executed"] and set(s["executed_checks"]) <= set(never + ["health_slos"]),
          f"unchanged inputs: reused={s['reused']} executed={s['executed']} "
          f"(only never-cacheable checks re-executed: {s['executed_checks']})")
    rid = res(o)["health_result"]
    rec = p.run("health", "show", rid).result
    reused_from = [c["cached_from"] for c in rec["checks"] if c.get("cached_from")]
    check("AC5-4b-cache-entry-names-its-source", len(reused_from) == s["reused"] and all(reused_from),
          f"every reused result names the health result it was computed in ({len(set(reused_from))} distinct)")

    # invalidation keyed on the *declared* inputs: a policy change re-executes every check that reads policy
    pol = p.read("governance/project/PROJECT_POLICY.yaml")
    p.write("governance/project/PROJECT_POLICY.yaml", pol + "\n# probe: policy overlay touched\n")
    p.commit("policy change")
    o = p.run("health", "run", "--event", "policy-invalidation")
    s = res(o)["summary"]
    check("AC5-5-cache-invalidation-policy", s["executed"] >= fam_total - 1,
          f"a project-policy change (an implicit dependency of every check) re-executed {s['executed']}/{fam_total}")

    # invalidation is *keyed*, not global: an unrelated class re-executes only its dependants
    converge(p, "settle2")
    p.write("docs/notes-eps.md", "probe note\n")
    p.commit("doc change")
    o = p.run("health", "run", "--event", "narrow-invalidation")
    s = res(o)["summary"]
    check("AC5-5b-invalidation-is-keyed", 0 < s["reused"] and s["executed"] < fam_total,
          f"an unrelated file change re-executed {s['executed']}/{fam_total}, reused {s['reused']}")

    # ---------------------------------------------------------------- 6. stale evidence
    p.run("rebuild-memory", "--incremental")
    p.run("audit")            # re-establish a recorded green governance-suite record
    converge(p, "settle-currency")
    st = res(p.run("health", "status"))
    cur_before = st["governance_suite_currency"]["current"]
    p.write("governance/project/PROJECT_POLICY.yaml", pol + "\n# probe: second policy touch\n")
    p.commit("second policy change")
    st2 = res(p.run("health", "status"))
    check("AC5-6-stale-evidence",
          cur_before and not st2["governance_suite_currency"]["current"]
          and st2["governance_suite_currency"]["changed_classes"],
          f"green record current before={cur_before}; after a policy change current="
          f"{st2['governance_suite_currency']['current']} changed={st2['governance_suite_currency']['changed_classes']}")
    check("AC5-6b-stale-checks-listed", isinstance(st2.get("stale_checks"), list),
          f"{len(st2.get('stale_checks') or [])} checks reported stale")

    # ---------------------------------------------------------------- 7/8. RGY and block-vs-warn
    # GREEN was established on the clean baseline above (AC5-green-baseline); YELLOW and RED are induced here.
    p.run("rebuild-memory", "--incremental")
    converge(p, "settle3")

    # a *warning-only* check failing lowers the state but refuses nothing
    # (index_freshness is declared warning-only; adding a governed record makes the index stale)
    p.write("spec/decisions/D-EPS-2.yaml",
            "id: D-EPS-2\ntype: decision\ntitle: Probe decision two\nstatus: ACTIVE\n"
            "state_class: AUTHORITATIVE\ndecision: probe two\nrationale: probe\ncreated: '2026-09-20'\n")
    p.commit("second decision")
    o = p.run("health", "run", "--event", "warning-probe")
    st = res(p.run("health", "status"))
    warn_only = [c for c in st["failing_checks"] if c["enforcement"] == "warning"]
    g = p.run("health", "guard", "task.create")
    check("AC5-8-warning-refuses-nothing",
          st["state"] == "YELLOW" and warn_only and g.ok and not st["blocks"],
          f"state={st['state']} failing(warning)={[c['check'] for c in warn_only]} "
          f"blocks={len(st['blocks'])} task.create allowed={g.ok}")

    # a *hard-block* check failing turns the state RED and refuses in-scope operations
    p.write("spec/decisions/D-EPS-DUP.yaml",
            "id: D-EPS-1\ntype: decision\ntitle: Duplicate id\nstatus: ACTIVE\n"
            "state_class: AUTHORITATIVE\ndecision: clash\nrationale: probe\ncreated: '2026-09-20'\n")
    p.commit("duplicate id")
    p.run("health", "run", "--event", "block-probe")
    st = res(p.run("health", "status"))
    blocked = p.run("health", "guard", "task.close", "--paths", "spec/decisions/D-EPS-1.yaml")
    check("AC5-7b-RED-on-hard-block",
          st["state"] == "RED" and st["blocks"] and not blocked.ok,
          f"state={st['state']} blocks={[(b['check'], b['severity'], b['scope']) for b in st['blocks']]} "
          f"refusal={blocked.error_code}")
    check("AC5-8b-hard-block-vs-warning-declared",
          all(("enforcement" in c and c["enforcement"]["mode"] in ("hard-block", "warning"))
              for c in p.run("health", "checks").result["checks"]),
          f"all {total} catalogue entries declare an explicit enforcement mode")

    # ---------------------------------------------------------------- 9. provenance
    rid = st["last_result"]
    rec = p.run("health", "show", rid).result
    need = ["tier", "trigger", "checks", "inputs", "inputs_hash", "runtime", "repository", "actor",
            "started_at", "finished_at", "cache_mode", "selection", "parallelism", "state", "machine_trust"]
    missing = [k for k in need if not rec.get(k)]
    check("AC5-9-provenance", not missing,
          f"health result carries tier/trigger/checks/inputs/runtime identity/repository state/actor/time; "
          f"missing={missing}")
    check("AC5-9b-provenance-runtime-identity",
          rec["runtime"].get("binary_sha256") and rec["repository"].get("content_key"),
          f"binary_sha256={rec['runtime']['binary_sha256'][:12]}… content_key={rec['repository']['content_key'][:12]}…")
    hist = p.run("health", "history", "--limit", "5").result
    check("AC5-9c-results-persisted", len(hist) >= 5, f"{len(hist)} recorded health results")

    # ---------------------------------------------------------------- 10. remediation / task generation
    tasks = p.run("task", "list").result
    gen = [t for t in tasks if (t.get("generated_from") or {}).get("subject")]
    check("AC5-10-remediation-generated", gen,
          f"health failures generated linked remediation work: "
          f"{[(t['id'], t['generated_from']['subject']) for t in gen][:3]}")
    if gen:
        t = p.run("task", "show", gen[0]["id"]).result
        check("AC5-10b-remediation-linked-to-check",
              t.get("remedies") and t.get("generation", {}).get("source") == "audit-finding",
              f"remedies={t.get('remedies')} source={t.get('generation', {}).get('source')} "
              f"class={t.get('class')}")

    # ---------------------------------------------------------------- 11. not the whole suite, serially
    check("AC5-11-not-whole-suite-serially",
          sel_exec < fam_total and wall_sel < 60,
          f"the trivial mutation executed {sel_exec} of {fam_total} governance-suite checks in "
          f"{wall_sel:.1f}s wall (whole-suite serial re-run would be {fam_total})")

    # ---------------------------------------------------------------- G0-G6 tier duties
    tiers = {t["tier"]: t for t in p.run("health", "checks").result["tiers"]}
    missing_tiers = [t for t in ["G0", "G1", "G2", "G3", "G4", "G5", "G6"] if t not in tiers]
    check("AC5-tiers-declared", not missing_tiers,
          f"declared tiers {sorted(tiers)}; each carries a duty: "
          f"{all(tiers[t]['duty'] for t in tiers)}")
    empties = [t for t in ["G1", "G2", "G3", "G4", "G5", "G6"] if not tiers[t]["checks"]]
    check("AC5-tiers-populated", not empties, f"tiers with no checks: {empties}")
    ran = {}
    for t in ["G1", "G2", "G3", "G4", "G5"]:
        o = p.run("health", "run", "--tier", t, "--event", f"tier-{t}")
        ran[t] = res(o)["summary"]["executed"] + res(o)["summary"]["reused"]
    check("AC5-tiers-executable", all(v > 0 for v in ran.values()), f"checks evaluated per tier: {ran}")

    # G5 is the *full suite*: every check the catalogue declares at G5 must be evaluated by a G5 run
    o = p.run("health", "run", "--tier", "G5", "--event", "tier-G5-coverage")
    s = res(o)["summary"]
    evaluated = set(s["executed_checks"]) | set(s["reused_checks"])
    declared_g5 = set(tiers["G5"]["checks"])
    check("AC5-G5-covers-its-declared-tier", declared_g5 <= evaluated,
          f"declared at G5 but not evaluated by a G5 run: {sorted(declared_g5 - evaluated)}")


if __name__ == "__main__":
    main(run, "AC-5")
