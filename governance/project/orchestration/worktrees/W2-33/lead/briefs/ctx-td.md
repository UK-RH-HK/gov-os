{
  "ticket": "DAEO-lrre",
  "ticket_text": "---\nid: DAEO-lrre\nstatus: in_progress\ndeps: [DAEO-g0ip]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 2\nassignee: product-spec\nexternal-ref: W2-33\ntags: [wave-2, role-definition, standard, three-layers]\nwbs_id: W2-33\ntitle: 'The three layers'' roles and the typed handoff: the CTO, the Senior Engineer, the ticket lead''s role file, machine-readable defaults per role (the roles spec defines it)'\nclass: role-definition\nstate_class: AUTHORITATIVE\nrole: product-spec\ndepends_on:\n- DAEO-g0ip\nallowed_paths:\n- template/governance/kernel/roles/**\n- template/governance/kernel/schemas/handoff*\n- template/governance/kernel/templates/handoff.md\n# .claude/agents/** out of the paths: generated from the kernel role files by the copies ACT, and a launched session cannot edit it (DEC-315); the CTO's delegated decision (DEC-1112 (3))\n- docs/probes/DAEO-lrre/**  # the probe record (the CTO, 2026-11-12)\n- template/.rulesync/subagents/orchestrator.md  # W2-113's S2/F2 moved here (DEC-1156 (4))\n- docs/changes/W2-33-CIT-P.md  # the kernel role files' CIT-P for the owner (CAP-33; DEC-1156 (3))\nkpis:\n  success:\n  - 'The ticket lead''s own role file (today a section of orchestrator.md). Verify: the kernel roles folder holds a role file of its own for the ticket lead that names its reads, writes and handover, and `orchestrator.md` no longer carries the ticket lead''s section (a grep for the section''s heading in `orchestrator.md` finds 0 lines) [DEC-954, DEC-236] (folds W2-21 S2)'\n  - 'Machine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a''s launcher; effort high for the CTO and the Senior Engineers. Verify: a test reads every role file''s defaults block and finds model, effort and skills in each; the launcher''s plan for a planted ticket prints the file''s model and effort; the CTO''s and the Senior Engineer''s files give effort high; a role file with a missing key fails the test [DEC-954, DEC-839 item 5, DEC-957]'\n  - 'The QA engineer replaces the planned independent reviewer: `qa-engineer.md` (not `independent-reviewer.md`) is the per-stream checking role, which reads the spec, the KPIs, the tests and the code, changes neither, writes only its findings report, and works per stream: tickets that touch the core (the guard, the close, memory''s retrieval, anything that could fail open) one by one before they merge, the others in batches of up to about five (more when they batch well and the machine and context allow), a large stream''s QA split; the independent auditor keeps the milestone audits. Verify: `qa-engineer.md` exists and `independent-reviewer.md` does not; the role file''s allowed tools and paths give read access to spec, KPIs, tests and code and write access only to its findings report (a planted write elsewhere is refused by the guard); the file states the per-stream rule (core tickets one by one, others in batches of up to about five); the independent auditor''s file still names the milestone audits [DEC-959 item 3, ROLES-RESEARCH-1 \u00a72.9]'\n  - 'Every role file states the work order in one line: product-spec writes the spec and KPIs; the test designer and the engineer work in parallel from it, never reading each other''s work; the engineer runs the acceptance tests once ready (through gov accept); the QA engineer alone reads both. Verify: a test reads every role file and finds the work-order line (the same sentence) in each; a role file without it fails the test; the test designer''s and the engineer''s files each deny reads of the other''s work in their allowed paths [DEC-959 item 7, DEC-957]'\n  - 'Every role file states one writer per worktree: two sessions that write never share a worktree; a ticket''s test designer works in its own tests worktree, merged by the lead. Verify: a test reads every role file and finds the one-writer-per-worktree statement in each; a role file without it fails; a planted launch of two writing sessions into one worktree is refused by the launcher, naming the worktree [DEC-847, DEC-963, DEC-983, DEC-982]'\n  - 'The QA engineer''s role file makes it the moderator: it triages every finding against the ticket''s own scope and KPIs; a finding out of scope, or needing an unusual construction, is a Wave 3 row, never a round; it returns the structured verdict per KPI; at most two review rounds per ticket. Verify: the QA engineer''s role file states the moderator duty, the Wave 3 row rule, the structured verdict per KPI and the two-round limit (a test reads each statement); a planted review brief with one out-of-scope finding yields a returned verdict that lists it as a Wave 3 row and starts no third round [DEC-1010 item 1, SMART-WORK-3]'\n  - 'RUBRIC-2''s model and effort by role and criticality, in each role file: a line `Launch default: model <m>, effort <e>` and, where the rubric varies by criticality class, a line `Launch by criticality: C3 ..., C2 ..., C1 ..., C0 ...`, with these values: orchestrator, ticket lead and senior engineer Opus high; engineer Sonnet high (C3 Opus high); test designer C3 Opus high, otherwise Sonnet high; QA engineer C3 Opus high, C2 Opus high on a FULL ticket and Sonnet high otherwise, C1 Sonnet high; independent auditor Opus high; product-spec and research Sonnet high. The `Model tier` field stays and names the line; the through-D-10 rule for engineers is the CTO''s launch practice and is written into no role file; the generated agents carry the same lines (W2-153 S3). Verify: a test per role file reads both lines and the values equal the table; a role file with a missing or malformed line fails it [DEC-1120 (2), DEC-1119 (2)] [added, DEC-1120 (5)]'\n  - 'Role files for the CTO (the master orchestrator) and the Senior Engineer (a stream''s sub-orchestrator, with its stream''s skills), generated as agents, each with its reads and writes, skills, model, brief contents and handover, as ROLES-SPEC-1 (approved, DEC-957) states them [DEC-954 Q6, Q13, DEC-957] [restored to Wave 2 by DEC-1087 (13); DEC-1156 (3): W2-33 creates `senior-engineer.md`; the generated agents are W2-153''s] Verify: the kernel roles folder holds `senior-engineer.md` with its reads and writes, skills, `Launch default` (claude-opus-5-5, effort high), brief contents and handover, and `orchestrator.md` is the CTO''s file (id kept); a test reads each'\n  - 'Both copies of the template''s orchestrator role file state the CTO-only install rule, name the key and the CTO''s `GOV_TICKET`, and no longer say the guard asks on every install (W2-110''s review F3) Verify: grep of `template/governance/kernel/roles/orchestrator.md` and `template/.rulesync/subagents/orchestrator.md` finds in each the CTO-only install rule, the key name and `GOV_TICKET`, and finds no sentence saying the guard asks on every install. [DEC-971 item 4, DEC-957] [moved from W2-113 (was its S2), DEC-1156 (4)]'\n  failure:\n  - 'A role file that tells the CTO the old rule. Verify: grep of both orchestrator role file copies for the old wording (the guard asks on every install) finds 0 lines. [moved from W2-113 (was its F2), DEC-1156 (4)]'\n  - 'A role built other than as the approved roles spec states it; a role file placed by hand rather than generated; a role without its machine-readable defaults. Verify: a planted role file that departs from the roles spec, one edited by hand in the generated folder (the generation check names it as drifted), and one without its defaults block each fail the role test, naming the file; none passes.'\n  lifted:\n  - 'The CTO''s role file states the approval classes (a call that may need the owner''s approval: the host''s ask rules and safety checks) and the quiet hours and morning package time as role defaults read from the project''s configuration, so an adopted product sets its own hours [DEC-991, DEC-994 item 3] [lifted (was S9), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n  moved:\n  - 'A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically; the twelve-field return is one [CAP-22.b (lite), AR-6] (to Wave 3, W-10) [re-scoped, DEC-1083] (was S4)'\n  - 'Any role the roles spec finds undefined is scoped and drafted here [DEC-954 Q13a] (to Wave 3, W-10) [re-scoped, DEC-1083] (was S5)'\nprofile: STANDARD\nsources:\n- CAP-22.b\n- CAP-22.c\n- DEC-094\n- DEC-954\n- DEC-957\n- DEC-959\n- DEC-983\n- DEC-1010\n- DEC-1083\n- DEC-236\n- DEC-839\n- DEC-847\n- DEC-963\n- DEC-982\n- DEC-991\n- DEC-994\n- DEC-315\n- DEC-1112\n- DEC-1119\n- DEC-1120\nest_loc: 260\nacceptance_tests:\n  path: tests/acceptance/W2-33/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- CAP-22.b\nlist_rows:\n- W2-L250\n- W2-L251\n- W2-L252\n- W2-M084\n- W2-M085\n- W2-M321\n---\n# W2-33 Wave 2 roles and typed handoff records\n\n**DEC-963 (owner, 2026-10-30):** the role files state the work order in parallel with one writer per worktree: the test designer works in its own tests worktree and retrieves only from the integration branch's store; the engineer works in the ticket's worktree, merges the tests when they are ready and runs them once.\n\n**DEC-959 (2026-10-30):** the QA engineer replaces `independent-reviewer.md` (item 3), and every role file states the work order in parallel (item 7).\n\n**Re-scoped by DEC-954 (Q6, Q13).** The earlier KPIs (test-execution, integration and UX roles) and CAP-22.c become Wave 3 rows unless the roles spec places them; CAP-22.b is carried lite (DEC-841 had moved CAP-22.b/c to Wave 3). **Roles spec approved (DEC-957);** builds to ROLES-SPEC-1 as approved, with the work order and the escalation rubric. Its CIT-P is part of the one combined K3 CIT-P (DEC-954 Q7).\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-33), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `template/governance/kernel/roles/**`, `template/governance/kernel/schemas/handoff*`, `template/governance/kernel/templates/handoff.md` (new), `.claude/agents/**` (generated through the adapter).\n- **KPIs:**\n  - Distinct test-execution and integration roles, each with its own rights [CAP-22.c, DEC-094, W2-M321].\n  - A UX role [W2-M322].\n  - A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically [CAP-22.b].\n  - The twelve-field return is a handoff record [AR-6].\n  - The agent definitions are generated, not placed by hand [W2-M084].\n\n## Interface (DEC-1052; the lead's package Option A, the owner, DEC-1156 (3), 2026-11-12)\n\n- **Files:** new `roles/ticket-lead.md` (ROLES-SPEC-1 \u00a73.3, DEC-957 Q2), `roles/qa-engineer.md` and `roles/senior-engineer.md` (DEC-1087 (13) puts the Senior Engineer back in Wave 2: the file is created, its S2 and S7 clauses are unconditional); no `independent-reviewer.md`; `orchestrator.md` loses the heading `## The ticket lead` and is the CTO's file (id kept).\n- **Line forms** (ROLES-SPEC-1 \u00a75.1, Q3; W2-60a's reader, `src/gov/launch/role.py:35-40` on w2/W2-60a), each once and whole in every role file:\n  `- **Version:** x.y.z` \u00b7 `- **Launch default:** model claude-opus-5-5|claude-sonnet-5-5, effort high` \u00b7\n  `- **Launch by criticality:** C3 model <id>, effort <e>; C2 \u2026; C1 \u2026; C0 \u2026` (only where RUBRIC-2 varies; QA's C2 written `C2 model claude-opus-5-5, effort high on FULL, model claude-sonnet-5-5, effort high otherwise`) \u00b7\n  `- **Skills:** a, b` \u00b7 `- **Model tier:** see Launch default` (kept; it names the line). S7's \"Opus\"/\"Sonnet\" mean claude-opus-5-5 / claude-sonnet-5-5.\n- **Work order, word for word in every file:** `- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are ready, through gov accept; the QA engineer alone reads both.`\n- **One writer, word for word in every file:** `- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works in its own tests worktree, merged by the lead.`\n- **QA engineer line heads:** `- **Per stream:**`, `- **Moderator:**`, `- **Wave 3 row:**`, `- **Verdict:**` (per KPI), `- **Rounds:**` (at most two), each with the KPI's wording.\n- **Clauses judged elsewhere (the role-file statement stays here):** S2's \"the launcher's plan prints the file's model and effort\" \u2192 W2-60a (its success line routed from W2-33); S3's guard refusal of a QA write elsewhere \u2192 W2-60b (its own `qa-engineer` line); S5's launcher refusal of two writers in one worktree \u2192 W2-60b (a success line routed from W2-33); S7's \"the generated agents carry the same lines\" and F1's \"the generation check names it as drifted\" \u2192 W2-153 (its generation check, after the copies ACT).\n- **S6's planted review brief:** run by the reviewer as a probe; the probe record (`docs/probes/DAEO-lrre/`) carries the returned verdict; not a deterministic acceptance case.\n- **CIT-P:** `docs/changes/W2-33-CIT-P.md` with the sha256 before and after of every kernel role file changed; the owner's approval before the merge (CAP-33).\n- **From W2-113 (DEC-1156 (4)):** its S2 and F2 (the CTO-only install rule in both orchestrator copies) are this ticket's; `template/.rulesync/subagents/orchestrator.md` is in the paths for them.\n",
  "authority": [
    {
      "id": "DEC-094",
      "sha256": "00ad24b2fd017587400020d630fdd2a7aa58771652bf8fe5f20d1839e32fa7c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "00ad24b2fd017587400020d630fdd2a7aa58771652bf8fe5f20d1839e32fa7c9",
      "reason": "declared in sources",
      "tokens": 85
    },
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-959",
      "sha256": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "reason": "declared in sources",
      "tokens": 1329
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-236",
      "sha256": "b3749e78802c8229b9fe063f9c54fb41bd1c4a01a9ca5d5748d5249b1edcdf18",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b3749e78802c8229b9fe063f9c54fb41bd1c4a01a9ca5d5748d5249b1edcdf18",
      "reason": "declared in sources",
      "tokens": 263
    },
    {
      "id": "DEC-839",
      "sha256": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "reason": "declared in sources",
      "tokens": 429
    },
    {
      "id": "DEC-847",
      "sha256": "396ef921618074d99b42182948500922b0cc839f69c0eb77cbc2e98fcaff28e3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "396ef921618074d99b42182948500922b0cc839f69c0eb77cbc2e98fcaff28e3",
      "reason": "declared in sources",
      "tokens": 553
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-991",
      "sha256": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "reason": "declared in sources",
      "tokens": 934
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-1120",
      "sha256": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "CAP-22.b",
      "sha256": "ec3423e5d961b3eadff311525b9703527eab447557b5566cd2f25d7455298424",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "ec3423e5d961b3eadff311525b9703527eab447557b5566cd2f25d7455298424",
      "reason": "declared in sources",
      "tokens": 115
    },
    {
      "id": "CAP-22.c",
      "sha256": "5d29bf9c4d7d17c85fcd5ba6d8c560e94d086d93c30e1dfddc35232f8ff2e7ac",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "5d29bf9c4d7d17c85fcd5ba6d8c560e94d086d93c30e1dfddc35232f8ff2e7ac",
      "reason": "declared in sources",
      "tokens": 114
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    }
  ],
  "mandatory": [
    {
      "id": "DEC-094",
      "sha256": "00ad24b2fd017587400020d630fdd2a7aa58771652bf8fe5f20d1839e32fa7c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "00ad24b2fd017587400020d630fdd2a7aa58771652bf8fe5f20d1839e32fa7c9",
      "reason": "declared in sources",
      "tokens": 85
    },
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-959",
      "sha256": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "reason": "declared in sources",
      "tokens": 1329
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-236",
      "sha256": "b3749e78802c8229b9fe063f9c54fb41bd1c4a01a9ca5d5748d5249b1edcdf18",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b3749e78802c8229b9fe063f9c54fb41bd1c4a01a9ca5d5748d5249b1edcdf18",
      "reason": "declared in sources",
      "tokens": 263
    },
    {
      "id": "DEC-839",
      "sha256": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "reason": "declared in sources",
      "tokens": 429
    },
    {
      "id": "DEC-847",
      "sha256": "396ef921618074d99b42182948500922b0cc839f69c0eb77cbc2e98fcaff28e3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "396ef921618074d99b42182948500922b0cc839f69c0eb77cbc2e98fcaff28e3",
      "reason": "declared in sources",
      "tokens": 553
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-991",
      "sha256": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "reason": "declared in sources",
      "tokens": 934
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DEC-315",
      "sha256": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5829c00741273430a74062deec7271744e868fa85e74789993f14e81ff373dd8",
      "reason": "declared in sources",
      "tokens": 124
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-1120",
      "sha256": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "CAP-22.b",
      "sha256": "ec3423e5d961b3eadff311525b9703527eab447557b5566cd2f25d7455298424",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "ec3423e5d961b3eadff311525b9703527eab447557b5566cd2f25d7455298424",
      "reason": "declared in sources",
      "tokens": 115
    },
    {
      "id": "CAP-22.c",
      "sha256": "5d29bf9c4d7d17c85fcd5ba6d8c560e94d086d93c30e1dfddc35232f8ff2e7ac",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "5d29bf9c4d7d17c85fcd5ba6d8c560e94d086d93c30e1dfddc35232f8ff2e7ac",
      "reason": "declared in sources",
      "tokens": 114
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    }
  ],
  "supplementary": [],
  "supplementary_query": "The three layers' roles and the typed handoff: the CTO, the Senior Engineer, the ticket lead's role file, machine-readable defaults per role (the roles spec defines it)\nThe ticket lead's own role file (today a section of orchestrator.md). Verify: the kernel roles folder holds a role file of its own for the ticket lead that names its reads, writes and handover, and `orchestrator.md` no longer carries the ticket lead's section (a grep for the section's heading in `orchestrator.md` finds 0 lines) [DEC-954, DEC-236] (folds W2-21 S2)\nMachine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a's launcher; effort high for the CTO and the Senior Engineers. Verify: a test reads every role file's defaults block and finds model, effort and skills in each; the launcher's plan for a planted ticket prints the file's model and effort; the CTO's and the Senior Engineer's files give effort high; a role file with a missing key fails the test [DEC-954, DEC-839 item 5, DEC-957]\nThe QA engineer replaces the planned independent reviewer: `qa-engineer.md` (not `independent-reviewer.md`) is the per-stream checking role, which reads the spec, the KPIs, the tests and the code, changes neither, writes only its findings report, and works per stream: tickets that touch the core (the guard, the close, memory's retrieval, anything that could fail open) one by one before they merge, the others in batches of up to about five (more when they batch well and the machine and context allow), a large stream's QA split; the independent auditor keeps the milestone audits. Verify: `qa-engineer.md` exists and `independent-reviewer.md` does not; the role file's allowed tools and paths give read access to spec, KPIs, tests and code and write access only to its findings report (a planted write elsewhere is refused by the guard); the file states the per-stream rule (core tickets one by one, others in batches of up to about five); the independent auditor's file still names the milestone audits [DEC-959 item 3, ROLES-RESEARCH-1 \u00a72.9]\nEvery role file states the work order in one line: product-spec writes the spec and KPIs; the test designer and the engineer work in parallel from it, never reading each other's work; the engineer runs the acceptance tests once ready (through gov accept); the QA engineer alone reads both. Verify: a test reads every role file and finds the work-order line (the same sentence) in each; a role file without it fails the test; the test designer's and the engineer's files each deny reads of the other's work in their allowed paths [DEC-959 item 7, DEC-957]\nEvery role file states one writer per worktree: two sessions that write never share a worktree; a ticket's test designer works in its own tests worktree, merged by the lead. Verify: a test reads every role file and finds the one-writer-per-worktree statement in each; a role file without it fails; a planted launch of two writing sessions into one worktree is refused by the launcher, naming the worktree [DEC-847, DEC-963, DEC-983, DEC-982]\nThe QA engineer's role file makes it the moderator: it triages every finding against the ticket's own scope and KPIs; a finding out of scope, or needing an unusual construction, is a Wave 3 row, never a round; it returns the structured verdict per KPI; at most two review rounds per ticket. Verify: the QA engineer's role file states the moderator duty, the Wave 3 row rule, the structured verdict per KPI and the two-round limit (a test reads each statement); a planted review brief with one out-of-scope finding yields a returned verdict that lists it as a Wave 3 row and starts no third round [DEC-1010 item 1, SMART-WORK-3]\nRUBRIC-2's model and effort by role and criticality, in each role file: a line `Launch default: model <m>, effort <e>` and, where the rubric varies by criticality class, a line `Launch by criticality: C3 ..., C2 ..., C1 ..., C0 ...`, with these values: orchestrator, ticket lead and senior engineer Opus high; engineer Sonnet high (C3 Opus high); test designer C3 Opus high, otherwise Sonnet high; QA engineer C3 Opus high, C2 Opus high on a FULL ticket and Sonnet high otherwise, C1 Sonnet high; independent auditor Opus high; product-spec and research Sonnet high. The `Model tier` field stays and names the line; the through-D-10 rule for engineers is the CTO's launch practice and is written into no role file; the generated agents carry the same lines (W2-153 S3). Verify: a test per role file reads both lines and the values equal the table; a role file with a missing or malformed line fails it [DEC-1120 (2), DEC-1119 (2)] [added, DEC-1120 (5)]\nRole files for the CTO (the master orchestrator) and the Senior Engineer (a stream's sub-orchestrator, with its stream's skills), generated as agents, each with its reads and writes, skills, model, brief contents and handover, as ROLES-SPEC-1 (approved, DEC-957) states them [DEC-954 Q6, Q13, DEC-957] [restored to Wave 2 by DEC-1087 (13); DEC-1156 (3): W2-33 creates `senior-engineer.md`; the generated agents are W2-153's] Verify: the kernel roles folder holds `senior-engineer.md` with its reads and writes, skills, `Launch default` (claude-opus-5-5, effort high), brief contents and handover, and `orchestrator.md` is the CTO's file (id kept); a test reads each\nBoth copies of the template's orchestrator role file state the CTO-only install rule, name the key and the CTO's `GOV_TICKET`, and no longer say the guard asks on every install (W2-110's review F3) Verify: grep of `template/governance/kernel/roles/orchestrator.md` and `template/.rulesync/subagents/orchestrator.md` finds in each the CTO-only install rule, the key name and `GOV_TICKET`, and finds no sentence saying the guard asks on every install. [DEC-971 item 4, DEC-957] [moved from W2-113 (was its S2), DEC-1156 (4)]\nA role file that tells the CTO the old rule. Verify: grep of both orchestrator role file copies for the old wording (the guard asks on every install) finds 0 lines. [moved from W2-113 (was its F2), DEC-1156 (4)]\nA role built other than as the approved roles spec states it; a role file placed by hand rather than generated; a role without its machine-readable defaults. Verify: a planted role file that departs from the roles spec, one edited by hand in the generated folder (the generation check names it as drifted), and one without its defaults block each fail the role test, naming the file; none passes.",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 18279,
  "budget": {
    "limit": 20000,
    "used": 18279
  },
  "hash": "215c68387251c34f64e52c30b0c34fae7b11f1cf46d0b64de4002543554ef500"
}
