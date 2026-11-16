---
id: DAEO-d8df
wbs_id: W2-195
external-ref: W2-195
status: in_progress
deps: []
links: []
created: 2026-11-16T16:06:29Z
type: task
priority: 1
assignee: Usain
parent: DAEO-sdxk
tags: [wave-2, kernel, review]
class: implementation
role: engineer
profile: FULL
state_class: AUTHORITATIVE
allowed_paths:
- template/governance/kernel/skills/judging-work/SKILL.md
- template/.rulesync/skills/judging-work/SKILL.md
- template/governance/kernel/roles/independent-auditor.md
- template/governance/kernel/roles/qa-engineer.md
- template/governance/kernel/roles/orchestrator.md
- template/governance/kernel/roles/ticket-lead.md
- template/.rulesync/subagents/**
- template/governance/kernel/templates/role-reviewer.md
- src/gov/brief/build.py
- src/gov/brief/command.py
- src/gov/brief/judging.py
- src/gov/launch/role.py
- src/gov/adopt/fabric.py
- tests/unit/adopt/test_w2_88_shipped.py
- tests/unit/brief/test_w2_195*
- tests/unit/launch/test_w2_195*
- tests/acceptance/W2-88/test_w2_88_p1_shipped_bytes.py
- docs/changes/W2-195-CIT-P.md
reads:
- governance/project/orchestration/packages/P-GOLDEN-RULE-1.md
- governance/project/orchestration/packages/judging-work.SKILL.md
- docs/DECISION_REGISTER.md
- src/gov/brief/**
- src/gov/launch/**
- src/gov/adopt/fabric.py
- template/governance/kernel/roles/**
- template/governance/kernel/templates/**
needs:
- src/gov/brief/build.py
- src/gov/launch/role.py
waits_on: []
est_loc: 450
kpis:
  success:
  - line: "S1 Preloaded: the Skills line of the kernel role files independent-auditor.md, qa-engineer.md, orchestrator.md and ticket-lead.md, and role-reviewer.md's skills list, name judging-work; a launch of each judging role carries the skill in its launch record's skills [DEC-1204 (5), P-GOLDEN-RULE-1 section 3 S1]"
    verify: "tests/unit/launch/test_w2_195_preload.py: each named role file's Skills line and role-reviewer.md's skills list hold judging-work; gov launch --plan for independent-auditor and qa-engineer lists judging-work among the session's skills"
  - line: "S2 Briefed automatically: gov brief for the independent-auditor, reviewer and QA roles, and a lead brief's reviewer and probe steps, include sections 1 to 3 of the installed judging-work skill file (never a hand copy) and name the skill's version [DEC-1204 (5), P-GOLDEN-RULE-1 section 3 S2]"
    verify: "tests/unit/brief/test_w2_195_inject.py: a fixture project with the skill installed; each judging brief holds the skill's sections 1 to 3 byte for byte and its version; a non-judging brief (engineer) does not"
  - line: "S3 Checked: gov brief refuses BRIEF_JUDGING_RULE_MISSING and gov launch refuses LAUNCH_JUDGING_RULE_MISSING for a judging role (independent-auditor, reviewer, probe, QA engineer) whose brief or role lacks the skill or names a different version [DEC-1204 (5), P-GOLDEN-RULE-1 section 3 S3]"
    verify: "tests/unit/brief/test_w2_195_check.py and tests/unit/launch/test_w2_195_check.py: one case per judging role with the skill removed and one with a different version, each refused with its named code; the same roles with the skill pass; one acceptance case under tests/acceptance/W2-195/"
  - line: "S4 Shipped: gov init (the kit) and a wheel of HEAD both deliver the skill (.claude/skills/judging-work/ after gov adapters generate); the shipped-folder lists include it exactly [DEC-1204 (5), P-GOLDEN-RULE-1 section 3 S4]"
    verify: "tests/unit/adopt/test_w2_88_shipped.py THE_SHIPPED and fabric.PACKAGED / KERNEL_FOLDERS name the skill; a copier copy of the template and a wheel built from HEAD each hold the skill's bytes"
  failure:
  - line: "F1 The brief builder edits the skill's text: the sha256 of the sections a brief carries differs from the installed file's sections [DEC-1204 (5), P-GOLDEN-RULE-1 section 3 F1]"
    verify: "tests/unit/brief/test_w2_195_inject.py: the injected text's sha256 equals that of the installed file's sections 1 to 3"
non_goals:
- "the kernel files (the skill, the role files, role-reviewer.md and their rulesync mirrors) merge only after the CIT-P (docs/changes/W2-195-CIT-P.md) with its independent review and the owner's approval of the bytes; the skill's text is the owner-approved 0fc1c502 (DEC-1204), word for word"
- "this repository's generated copies (.claude/skills/, .claude/agents/) follow by their own class (b) ACT after the merge, not by this ticket"
- "EXAMIN receives the text by REPLIES.md meanwhile (P-GOLDEN-RULE-1 section 5 (a)); its copy gets the product in the release carrying this ticket"
- "no change to what a reviewer may block on beyond DEC-1204's text; the rule never lowers a wall"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1204, DEC-039, DEC-801, DEC-1010, DEC-974, CAP-33, CAP-24.b]
acceptance_tests: {path: tests/acceptance/W2-195/}
---
# The golden rule ships: the judging-work skill preloaded, briefed and checked

# W2-195 The golden rule ships: the judging-work skill preloaded, briefed and checked

Filed 2026-11-16 by the CTO on the owner's word (DEC-1204: "P-GOLDEN-RULE-1 (a). yes judging-work 0fc1c502. Both today,
top priority.").

**Problem.** The rule for judging work (ADR-0001 / DEC-039's threat model, DEC-801's blocking test and DEC-1010's
convergence) lived in three register entries and was left out of briefs, so reviews ran extra rounds on findings no
honest agent hits in ordinary work. DEC-1204 merges the three into one golden rule and puts it in one kernel skill.

**Approach.** As P-GOLDEN-RULE-1 section 3: the skill `judging-work` (the owner-approved text, sha256 0fc1c502,
`governance/project/orchestration/packages/judging-work.SKILL.md`) installed in the kernel and its rulesync mirror; the
judging roles' Skills lines; `gov brief` injects sections 1 to 3 from the installed file for every judging brief and
names the version; `gov brief` and `gov launch` refuse a judging brief or launch that lacks it; the skill in the shipped
lists. The launch refusal sits in `gov.launch.role.read_role`, which the launcher already calls (`launcher.py` is W2-156's, in progress). The kernel files by CIT-P (section 4), returned as PACKAGES with the bytes for the owner.

**Started now** as the top of the ready list (the owner: "Both today, top priority").
