---
id: DAEO-z3ss
wbs_id: W2-196
external-ref: W2-196
status: in_progress
deps: []
links: []
created: 2026-11-16T17:21:25Z
type: task
priority: 1
assignee: Usain
parent: DAEO-sdxk
tags: [wave-2, kernel, planning]
class: implementation
role: engineer
profile: FULL
state_class: AUTHORITATIVE
allowed_paths:
- docs/research/W2-196-routing.md
- docs/changes/W2-196-CIT-P.md
- docs/changes/W2-196-evidence.md
- template/governance/kernel/skills/orchestration/SKILL.md
- template/governance/kernel/skills/planning/SKILL.md
- template/.rulesync/skills/orchestration/SKILL.md
- template/.rulesync/skills/planning/SKILL.md
- src/gov/plan/**
- tests/unit/plan/test_w2_196*
reads:
- governance/project/orchestration/packages/PROVISIONAL-RUBRIC.md
- governance/project/orchestration/packages/P-GOLDEN-RULE-1.md
- docs/DECISION_REGISTER.md
- governance/project/operator/class-rules.yaml
- .gov-runtime/scratch/orchestrator/drafts/retro-2026-11/
- template/governance/kernel/skills/**
- src/gov/plan/**
needs:
- src/gov/plan/command.py
waits_on: []
est_loc: 400
kpis:
  success:
  - line: "R0 Research first: docs/research/W2-196-routing.md records how software teams route work by size and risk (standard against normal changes as change-management practice names them, small-change lanes, review scaled to risk), each claim with its source, and what Gov OS takes from each [DEC-1208 (1)]"
    verify: "the file exists before any src or kernel change on the branch (git log order); it names at least four sources with links and one section per topic (standard against normal changes, small-change lanes, risk-scaled review), each ending with what the rubric takes; read by the review"
  - line: "S1 The rubric classes every piece of work by size, risk, reversibility, blast radius over the six protected areas (the guard, acceptance tests, memory, the close, data, the kernel), test coverage and whether it changes a spec or a KPI, into Q (a quick action done directly by the CTO or a senior engineer: the tests stay green, one commit with a Class trailer, listed in the owner's digest), L, S and F, each class naming its route and its needs (tests, review by the golden rule, record, the owner's approval) [DEC-1208 (1)]"
    verify: "tests/unit/plan/test_w2_196_classify.py: gov plan's class function (or the planning skill's table read by it) gives Q for a one-file change with tests outside the protected areas, F for any change under a protected path, F for a spec or KPI change, L and S for the stated middle cases; the orchestration and planning skills carry the same table with the routes and needs"
  - line: "S2 Guardrails: a protected area is never Q whatever its size; a quick action past its time box (30 minutes, a second commit or a red test) becomes a ticket; weekly spot audits of Q commits by an independent auditor, misroutes in the owner's digest [DEC-1208 (1)]"
    verify: "tests/unit/plan/test_w2_196_classify.py: a small change touching .claude/hooks/, tests/acceptance/, the store, src/gov/close/, a data migration or template/governance/kernel/ classes F, never Q; the skills state the time box and the spot audit with who runs it and where its record goes"
  - line: "S3 Machine and operator work: small configuration and permission changes are classed by the same rubric and go the quick way on the owner's yes, with a written rollback [DEC-1208 (1)]"
    verify: "the orchestration skill's rubric section has a machine and operator row (configuration, permission, a cron line, a tool flag) with route Q on the owner's yes line and its rollback; tests/unit/plan/test_w2_196_classify.py classes a planted configuration change Q and a permission widening of a protected path F"
  - line: "S4 It lives where work is decided: the CTO's orchestration skill and the planning skill (kernel, by CIT-P), CLAUDE.md and AGENTS.md (a class (b) ACT on the rulesync source after the merge), the planner (gov plan names each ticket's class, and the planning skill divides work by class), and the kit, so every adopted repository inherits it [DEC-1208 (1)]"
    verify: "tests/unit/plan/test_w2_196_plan.py: gov plan's output names a class per ticket; the CIT-P docs/changes/W2-196-CIT-P.md lists the skill bytes and the ACT's text for CLAUDE.md and AGENTS.md; the two skills are already in the kit's shipped folders (W2-88's lists unchanged), shown by a copier render of HEAD holding the new section"
  - line: "S5 Measured before and after: time, cost and review rounds per change and the owner's interruptions, per class, with the baseline from the retrospective of 2026-11 and the first two weeks after the rubric lands [DEC-1208 (1)]"
    verify: "docs/changes/W2-196-evidence.md holds the baseline table (from drafts/retro-2026-11/ parts 1 and 2) and the measure's definition (sources: lead logs' total_cost_usd and duration_ms, review rounds from docs/probes/, commits' Class trailers, the owner's messages); a script or gov plan sub-command that computes the after table is named and run once"
  failure:
  - line: "F1 A quick action touches a protected path: the planner or the landing check flags it, and it is never recorded as Q [DEC-1208 (1), guardrail 1]"
    verify: "tests/unit/plan/test_w2_196_classify.py: a change list holding one protected path classes F even when it is one line; a commit whose Class trailer says Q and whose diff touches a protected path is reported by the classify check with the path named"
non_goals:
- "the kernel files (the two skills and their rulesync mirrors) merge only after the CIT-P (docs/changes/W2-196-CIT-P.md) with its independent review and the owner's approval of the committed bytes"
- "CLAUDE.md, AGENTS.md and .rulesync/rules/governance.md change by their own class (b) ACT after the merge, not by this ticket's commits"
- "no new kit file: the rubric goes into skill files the kit already ships; a new file would wait for W2-195 (which holds src/gov/adopt/fabric.py and the shipped-list test) to land"
- "the provisional rubric (packages/PROVISIONAL-RUBRIC.md) governs until this ticket lands; class-rules.yaml and the operator's gates are unchanged"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1208, DEC-974, DEC-1204, DEC-1047, CAP-33]
acceptance_tests: {path: tests/acceptance/W2-196/}
---
# A work-sizing rubric: work routed by size and risk

# W2-196 A work-sizing rubric: work routed by size and risk (quick, LITE, STANDARD, FULL)

Filed 2026-11-16 by the CTO on the owner's word (DEC-1208: "a work-sizing rubric, as Wave 2 work in parallel with
EXAMIN's Wave 0. This is my approval of its ticket (DEC-974).").

**Problem.** Every change today runs a ticket's full ceremony whatever its size, so a two-minute fix costs a lead run,
reviews and records, and the owner's interruptions grow with the count of changes, not their risk.

**Approach.** Research first (R0), then the rubric as a spec (S1 to S3), then into the skills, the planner and, by ACT,
CLAUDE.md and AGENTS.md (S4), measured before and after (S5). The provisional rubric
(`governance/project/orchestration/packages/PROVISIONAL-RUBRIC.md`) is the starting point and governs until this lands.
