#!/usr/bin/env python3
"""Availability-rule attacks on health blocks — P2-AR-0050, family epsilon (lead duty).

Contract v3 L4 ("Independent runnable branches continue. Global stop only when policy or critical-path state
requires") and O5 :807 ("hard-block vs warning semantics are explicit"), as compiled in P2-HO-0031:

  1. a block refuses only within its scope;
  2. its listed remedy stays available;
  3. independent work stays available;
  4. no block refuses its own remedy;
  5. every refusal is typed and names its scope;
  6. a block whose inputs changed is re-evaluated before it refuses;
  7. a committing remedy that does not clear its block does not commit (HEALTH_REMEDY_INCOMPLETE / refusal).

Every attack drives real governed operations, not only `gov health guard`.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import check, main  # noqa: E402
from t01_ac5_scheduler import provisioned, converge, res  # noqa: E402

DEC = ("id: {id}\ntype: decision\ntitle: {t}\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n"
       "decision: {t}\nrationale: availability probe\ncreated: '2026-09-20'\n")


def run():
    p, _pub = provisioned("avail")
    converge(p)

    # two independent work streams, and a subject-scoped high block on one of them
    p.write("spec/decisions/D-AV-1.yaml", DEC.format(id="D-AV-1", t="Stream A decision"))
    p.write("spec/decisions/D-AV-1-dup.yaml", DEC.format(id="D-AV-1", t="Duplicate of stream A"))
    p.write("spec/decisions/D-AV-2.yaml", DEC.format(id="D-AV-2", t="Stream B decision"))
    p.commit("two streams; a duplicate id in stream A")
    p.run("rebuild-memory", "--incremental")
    p.run("health", "run", "--event", "induce-block")

    st = res(p.run("health", "status"))
    blocks = st["blocks"]
    subj_blocks = [b for b in blocks if b["scope"] == "subjects"]
    check("AV-0-block-induced", st["state"] == "RED" and subj_blocks,
          f"state={st['state']} blocks={[(b['check'], b['severity'], b['scope']) for b in blocks]}")
    if not subj_blocks:
        return
    b = subj_blocks[0]

    # ---------------------------------------------------------------- 5. typed refusal naming its scope
    r = p.run("health", "guard", "task.close", "--paths", "spec/decisions/D-AV-1.yaml")
    d = r.details
    named = d.get("blocks") and all(
        x.get("check") and x.get("scope") and ("subjects" in x) for x in d["blocks"])
    check("AV-5-refusal-typed-and-named",
          (not r.ok) and r.error_code == "HEALTH_HARD_BLOCK" and named,
          f"code={r.error_code}; every named block carries check/scope/subjects: {named}; "
          f"e.g. {json.dumps({k: d['blocks'][0].get(k) for k in ('check', 'severity', 'scope', 'subjects')})}")

    # ---------------------------------------------------------------- 1. scoped: stream B is untouched
    r = p.run("health", "guard", "task.close", "--paths", "spec/decisions/D-AV-2.yaml")
    check("AV-1-scoped-refusal", r.ok,
          f"closing work on the independent record D-AV-2 is admitted under a block whose subjects are "
          f"{b['subjects']}: ok={r.ok} {r.error_code}")
    r = p.run("health", "guard", "task.close", "--paths", "src/unrelated.rs")
    check("AV-1b-scoped-refusal-paths", r.ok, f"unrelated source path admitted: ok={r.ok} {r.error_code}")

    # ---------------------------------------------------------------- 3. independent work stays available
    avail = {}
    for op in ("task.create", "task.claim", "handoff.create", "cit.propose", "cit.approve"):
        avail[op] = p.run("health", "guard", op).ok
    check("AV-3-independent-work-available", all(avail.values()),
          f"under a subject-scoped high block, starting/claiming/handing off/proposing work is admitted: {avail}")

    real = p.run("task", "create", "--objective", "Independent stream B work",
                 "--title", "Stream B", "--class", "implementation", "--allowed", "src/b/**")
    check("AV-3b-real-task-create-available", real.ok,
          f"a real `gov task create` under the block: ok={real.ok} {real.error_code}")

    # ---------------------------------------------------------------- 2/4. the remedy stays available
    r = p.run("health", "guard", "cit.propose", "--paths", "spec/decisions/D-AV-1-dup.yaml")
    check("AV-2-remedy-available", r.ok and r.result.get("remedy_for"),
          f"cit.propose on the block's own subjects is admitted AS ITS REMEDY: ok={r.ok} "
          f"remedy_for={[x['check'] for x in (r.result.get('remedy_for') or [])]}")
    check("AV-4-no-block-refuses-its-own-remedy",
          all(op in (b.get("remedies") or []) for op in ("cit.propose", "cit.execute")),
          f"the block lists its own repair transaction among its remedies: {b.get('remedies')}")

    gen = [t for t in p.run("task", "list").result if (t.get("generated_from") or {}).get("subject")]
    if gen:
        rid = gen[0]["id"]
        c = p.run("task", "claim", rid, role="change-controller", session="rem")
        check("AV-2b-remediation-claimable-under-its-own-block", c.ok,
              f"the generated remediation {rid} (declaring remedies={p.run('task', 'show', rid).result.get('remedies')}) "
              f"is claimable under the block it repairs: ok={c.ok} {c.error_code}")

    # ---------------------------------------------------------------- 7. a committing remedy must clear it
    # A close whose subjects reach the block's subjects is a committing operation; it is refused while the
    # condition stands, however the task declares itself.
    if gen:
        rid = gen[0]["id"]
        p.write("spec/decisions/D-AV-1-dup.yaml",
                DEC.format(id="D-AV-1", t="Duplicate of stream A (edited, still duplicated)"))
        p.commit("touch the blocked subject without repairing it")
        p.run("rebuild-memory", "--incremental")
        pk = p.run("context", "compile", rid, role="change-controller", session="rem")
        report = p.root.parent / "avail-report.json"
        report.write_text(json.dumps({
            "task": rid, "status": "success", "outcome": "success",
            "work_completed": "edited the blocked record; the duplicate id was deliberately NOT repaired",
            "files_changed": ["spec/decisions/D-AV-1-dup.yaml"], "evidence": [],
            "tests": {"status": "not_applicable_with_reason", "reason": "governance-only probe"},
            "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
            "recommended_next_action": "close", "repair_count": 0,
            "context_packet_hash": pk.result.get("packet_hash"), "inputs_consumed": [],
            "outputs_produced": [], "requirements_implemented": [], "scenarios_implemented": [],
            "features_implemented": [], "decisions_applied": [], "constraints_applied": [],
            "acceptance_evidence": [], "deviations": []}))
        cl = p.run("task", "close", rid, "--report", str(report),
                   role="change-controller", session="rem")
        typed = cl.error_code in ("HEALTH_HARD_BLOCK", "HEALTH_REMEDY_INCOMPLETE")
        check("AV-7-committing-remedy-must-clear-its-block", (not cl.ok) and typed,
              f"closing the repair task while the condition stands is refused: ok={cl.ok} code={cl.error_code}")

    # ---------------------------------------------------------------- 6. re-evaluated before refusing
    dup = p.root / "spec" / "decisions" / "D-AV-1-dup.yaml"
    aside = p.root.parent / "moved-aside"
    aside.mkdir(exist_ok=True)
    dup.rename(aside / "D-AV-1-dup.yaml")          # `rm` is denied here: the file is MOVED ASIDE
    p.commit("repair: the duplicate record moved out of the repository")
    r = p.run("health", "guard", "task.close", "--paths", "spec/decisions/D-AV-1.yaml")
    check("AV-6-reevaluated-before-refusing",
          r.ok and (r.result.get("observed") or {}).get("changed", 0) >= 1,
          f"without any explicit `gov health run`, the guard observed the repair "
          f"({(r.result.get('observed') or {}).get('changed')} changed path(s), tier "
          f"{(r.result.get('observed') or {}).get('tier')}) and admitted the operation: ok={r.ok}")
    st = res(p.run("health", "status"))
    check("AV-6b-block-cleared", not [x for x in st["blocks"] if x["check"] == b["check"]],
          f"blocks after the repair: {[(x['check'], x['scope']) for x in st['blocks']]}")

    # ---------------------------------------------------------------- a block does NOT stop refusing spuriously
    p.write("spec/decisions/D-AV-1-dup2.yaml", DEC.format(id="D-AV-1", t="Duplicate again"))
    p.commit("re-introduce the duplicate")
    p.run("rebuild-memory", "--incremental")
    r = p.run("health", "guard", "task.close", "--paths", "spec/decisions/D-AV-1.yaml")
    check("AV-6c-unrepaired-condition-still-refuses", not r.ok,
          f"the re-introduced condition is observed and refuses again: ok={r.ok} code={r.error_code}")

    # ---------------------------------------------------------------- never-refused remedies stay available
    always = {}
    for cmd in (["doctor"], ["audit"], ["health", "status"], ["status"], ["recover"],
                ["rebuild-memory", "--incremental"], ["checkpoint", "list"]):
        o = p.run(*cmd)
        always[" ".join(cmd)] = o.error_code != "HEALTH_HARD_BLOCK"
    check("AV-remedy-commands-never-refused", all(always.values()),
          f"diagnosis and repair commands are never refused by a health block: {always}")

    # ---------------------------------------------------------------- global scope is reserved
    cat = p.run("health", "checks").result["checks"]
    glob_all = [c["id"] for c in cat if c["enforcement"]["mode"] == "hard-block"
                and any(r_["scope"] == "global" and len(r_["operations"]) == 10
                        for r_ in c["enforcement"]["refuses"])]
    crit_only = all(any(r_["at_or_above"] == "critical" for r_ in c["enforcement"]["refuses"]
                        if r_["scope"] == "global" and len(r_["operations"]) == 10)
                    for c in cat if c["id"] in glob_all)
    check("AV-L4-global-stop-reserved-for-critical", crit_only,
          f"only a *critical* finding refuses every governed operation globally "
          f"({len(glob_all)} checks carry such a rule, all at critical)")


if __name__ == "__main__":
    main(run, "AVAILABILITY")
