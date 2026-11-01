The hook needs each label with its content on the same line ("task: …"), so I've put them that way here. That overrides your request for content on its own line.

task: Check every open or in-progress ticket against DEC-995: each ticket must be workable by one role. Propose splits for the mixed tickets, with W2-33 and W2-83a in most detail.
status: Done. Read-only; I wrote only scratch scripts under /tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/20804c5c-af51-4450-934e-42f650effce2/scratchpad/sweep/.
work_completed: I read the six role files, the launcher (src/gov/launch/launcher.py), the five-rule guard (.claude/hooks/pretooluse.py), ROLES-SPEC-1 §3 and §6, and the adapter check (src/gov/adapters/portability.py). I parsed all 87 open or in-progress tickets and sorted each allowed path and each KPI line by the role it needs.
files_changed: None in the repository.
evidence: launcher.py:37-40,124-132,187-194 (which roles the launcher starts, the files every worker is barred from, a role works only its own tickets); install.py:194-219 (a research ticket names exactly one folder ending /**); pretooluse.py:33-34,93-102,152-170 (rule 5 limits reviewers and auditors to docs/probes, docs/audit and docs/assessment); portability.py:142-160 (every kernel role file needs a .rulesync/subagents source, or SOURCE_MISSING); schema.py:28-40 (a record type with no SCHEMA_MAP entry is refused).
tests: None run. This was analysis only.
discoveries: (1) W2-40, W2-15a and W2-15b each name two paths, so the launcher would refuse all three. (2) W2-93, W2-94 and W2-61h are auditor tickets that write fixtures/evaluation/**, which rule 5 refuses; no role may write there today. (3) Nine engineer tickets (W2-05, 55, 60a, 86, 88, 91, 92, 112, 115) and the repair ticket DAEO-s1wp write records under docs/research/, which no launched research session could write either (research writes one folder under experiments/). (4) Four tickets hold the adopt skill: W2-52 (in progress, under DEC-738 item 1), W2-88, W2-83a and W2-11; W2-83a's "no open ticket holds it" is now wrong. (5) Three tickets hold roles/orchestrator.md: W2-11, W2-33 and W2-113. (6) W2-60b reads the role files (S7, S9) but does not depend on W2-33, and W2-60a's body still says W2-11 writes the default lines (W2-33 r1 does now). (7) The live guard does not enforce allowed_paths; a worker's writes are bounded only by rules 1 and 5 and the launcher's deny rules.
risks: If the docs/research and CIT-P questions are settled strictly, about twelve more child tickets follow. W2-52 contradicts DEC-995 while it is in progress (DEC-105 applies).
lessons: Paths alone do not show mixing: W2-96's sixth KPI and W2-33's handoff "refused" line only show up in the KPI text.
proposed_decisions: DP-A: a ticket's own CIT-E is written by the role that made the change; a CIT-P goes to the product-spec child when there is one, otherwise the lead drafts it. DP-B: a ticket's measurement of its own change is the implementer's evidence (I recommend docs/changes/<id>-evidence.md); the research role is kept for work that needs the network, a venv or an open question. DP-C: an evaluation-set author: either rule 5 lets an auditor write its own ticket's hidden folder, or the test designer's scope gains fixtures/evaluation/**. DP-D: research tickets name one folder, with the record inside it. DP-E: kernel checks/*.yaml, project maps and registries, lefthook and workflows are engineer config; schemas, templates and .rulesync sources are product-spec.
unresolved: Whether W2-33's handoff record must be validated by gov check; the configuration key that names the quiet hours, shared by W2-33 and W2-113.
recommended_next_action: Record DEC-995 with DP-A to DP-E. Then file the children below, fix the research and auditor paths, and add the missing W2-60b → W2-33 dependency.

---

### (1) What each role may write

| Role | Writes | Source |
|---|---|---|
| engineer | its own ticket's allowed_paths and scratch; never acceptance tests, .tickets, .claude or .gov-runtime outside scratch | engineer.md; launcher (own-ticket rule, protected folders); guard rule 1 |
| product-spec | the same mechanism. By kind: schemas, templates, skills, role files, briefs, docs, .rulesync sources, CIT-Ps | product-spec.md; ROLES-SPEC §3.6; DEC-995 |
| test designer | tests/acceptance/** only, on any in-progress ticket | its role file; guard rule 1; the launcher's folder rules |
| auditor / reviewer / QA | docs/probes, docs/audit, docs/assessment, its review scratch and /tmp | guard rule 5 |
| research | exactly one folder under experiments/ and scratch | research.md; experiment_folder; launcher (DEC-273) |
| orchestrator / CTO | anything except tests/acceptance and .gov-runtime outside scratch | orchestrator.md |
| .claude/** copies | no worker (barred by the launcher and Claude Code's safety check); the CTO copies with the owner's approval | launcher (DEC-315) |

### (2) W2-33 (DAEO-lrre, product-spec, STANDARD)

**Verdict:** single-role, plus a CTO copy step and gaps in its paths. One child only if the handoff record must be validated.

**Belongs to W2-33 (all spec work):** S1–S9.
- S3: W2-60a's launcher reads the defaults; W2-33 only writes them.
- S6: making qa-engineer a known role is already W2-60b S9 (engineer). Its line in this repository's hook is a CTO copy.
- S9: W2-33 only states the quiet hours. The configuration key and its reader belong to W2-113 S4; fix the key's name first, in DEC-994 or in W2-113's KPI.

**Paths missing:**
- .rulesync/subagents/** and template/.rulesync/subagents/**. Without them each new role fails the portability check with SOURCE_MISSING.
- governance/project/roster.yaml, which takes the new roles' entries.

**CTO copy step:** .claude/agents/**. The failure line "placed by hand rather than generated" means the CTO runs the adapter and commits the output.

**Possible child, W2-33-c (engineer, LITE, about 20 lines):** a handoff entry in SCHEMA_MAP in schema.py, with a unit test. Needed only if a handoff record kept under docs/ must be refused for a missing field. It depends on W2-33's schema.

**"A fresh agent states it identically":** this is the test designer's live test, not a split.

**Order:** W2-33 → W2-60b, W2-21 and W2-113's role text.

### (2) W2-83a (DAEO-dy7j, product-spec, STANDARD)

**Verdict:** MIXED.

**Stays with W2-83a (product-spec):**
- KPI 1: the template and the schema.
- KPI 3: the adopt skill step and its three .rulesync and kernel copies.
- KPI 4: the CIT-P and CIT-E.
- KPI 5: nothing project-specific in the kernel.

**Moves to child W2-83a-c (engineer, LITE, about 15 lines plus a test):**
- KPI 2: the playbook entry in SCHEMA_MAP.
- KPI 3's gov check half: the temporary product passes with one playbook and is refused with a planted faulty one.
- Paths: src/gov/check/schema.py and tests/unit/check/test_schema_playbook*.

**Order:** the parent's CIT-P is approved → the parent writes the schema and template → the child adds the map entry → the parent closes. The map must never name a schema file that does not exist yet.

**CTO copy step:** .claude/skills/adopt/**.

**Also:** update the stale "no open ticket holds the adopt skill" line, and fold W2-52's skill clause in here.

### (3) Every open or in-progress ticket

| WBS (id) | Role | Verdict | Split or fix |
|---|---|---|---|
| W2-83a dy7j | product-spec | mixed | above |
| W2-33 lrre | product-spec | copies, path gaps | above |
| W2-11 k7hz | product-spec | mixed (decided) + copies | validator child, as decided; also take W2-96 S6's kernel brief half |
| W2-113 g29a | engineer | mixed | Move S2 (orchestrator.md, both copies) to W2-33 and drop those 2 paths; add the quiet-hours configuration file to its paths; estimate 60 → about 200 lines |
| W2-21 1ahb | engineer | mixed (path only) | Drop roles/ticket-lead.md (W2-33 S2 writes it); depend on W2-33 |
| W2-88 2bdu | engineer | mixed | product-spec child (STANDARD): adopt SKILL.md ×3 and the CIT-P. Research child (STANDARD): S8–S11 proofs on GitHub clones, which need the network, in experiments/W2-88/. Both after the engineer part; .claude copy by the CTO |
| W2-82 4k3l | engineer | mixed | product-spec child (LITE): S5's template and stacked_on schema, S6's CIT-P; the child goes first |
| W2-109 6b2q | product-spec | mixed | engineer child (LITE): S4's contract-forms check in validate_w2.py plus unit tests; parent's text → child → parent's CIT-E |
| W2-35 2keg | engineer | mixed | product-spec child (LITE): schemas/readiness* |
| W2-55 arrl | engineer | mixed | product-spec child (LITE): schemas/decision*; the backfill record falls under DP-B |
| W2-19 jzvg | engineer | mixed | product-spec child (LITE): the test-commands field in path-map.schema.json; the child goes first |
| W2-78 v4is | engineer | mixed | product-spec child (LITE): schemas for the record files |
| W2-34 yadm | engineer | mixed only if S3 needs the template changed | product-spec child (LITE): the openspec tasks.md template |
| W2-52 siiz | engineer, in progress | mixed (DEC-738 item 1 vs DEC-995) | DEC-105 options. Recommended: apply now by moving "the adopt skill names both steps" to W2-83a. W2-52 also lacks the .rulesync sources |
| W2-96 ouet | engineer, in progress | mixed (KPI 6) | The kernel brief-* half goes to W2-11; the common brief is already done (DEC-991) |
| W2-60a cv58 | engineer, in progress | mixed (S9 probe) | research child (LITE) or the lead (DP-B); fix the W2-33 dependency |
| W2-09 a3m2 | engineer | CIT-P only | DP-A |
| W2-23 kmcr | engineer | copies plus root docs | Drop CLAUDE.md, AGENTS.md and .claude/settings.json (S2 is shown on fixtures); the CTO copies any generated output |
| W2-60b ecac | engineer | copies only | The hook's reviewer line is a CTO copy; add a dependency on W2-33 |
| pr0y, s1wp (repairs) | engineer | mixed only if a schema changes | Drop the schema path, or add a product-spec child (LITE) if needed; s1wp's research record: DP-B |
| W2-98 wi46, 99 lxzn, 100 uw5h, 101 6icv, 102 rpfv, 103 hgv3 | product-spec | copies only | CTO copies .claude/skills/*; scenarios run through W2-104 |
| W2-05 0z8c, 86 jsg1, 91 a3u2, 92 n0wb, 112 clon, 115 emq1 | engineer | single-role under DP-B | the evidence record stays with the engineer |
| W2-56 wnnz, cv6c | engineer | single-role (own CIT-E) | — |
| W2-04 u4oz, 06 kia7, 10 cuao, 12 j8gn, 13 zqvn, 17 sdhj, 18 057v, 20 r30l, 22 xm6l, 31 wbdh, 32 0pyc, 36 w19l, 37 6n5k, 38 g23i, 39 wudw, 41 s694, 42 fau3, 43 u5g6, 44 zndm, 45 neam, 104 drhj, 110 3r1j, 116 f58b, 117 zkr9, 118 ts4y, 119 168f, 2d6f | engineer | single-role | — (kernel hooks, check YAML and maps count as engineer config under DP-E) |
| W2-83b mc6n, W2-105 zpdj | product-spec | single-role | — |
| W2-81 l78m, 90b nqa2, 111 qvff, 114 4eux, 2upp, sg6x | test designer | single-role | — |
| W2-25 btt7, 28 csj8, 30 60rw, 47 jip3 | auditor | single-role | — |
| W2-93 6y0x, 94 g87r, 61h h2k3 | auditor | role and path conflict (rule 5) | DP-C, not a split |
| W2-40 6ox0, 15a rd0g, 15b swdu | research | single-role, but the launcher refuses them | DP-D: one folder |
| W2-00 sdxk, 08 7r5e, 14 7y6v, 24 0mab, 27 h4rh, 29 b926, 46 nn1s | orchestrator | single-role | — |