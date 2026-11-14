{
  "ticket": "DAEO-6f0s",
  "ticket_text": "---\nid: DAEO-6f0s\nwbs_id: W2-184\nexternal-ref: W2-184\ntitle: \"RUBRIC-2 at launch: criticality from criticality.yaml, the Launch by criticality line, the effort floor, trials, the second review's setting, promotion (from W2-60a)\"\ntype: task\nclass: implementation\nrole: engineer\nprofile: FULL\nstatus: in_progress\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-13\ndeps: [DAEO-cv58]\nallowed_paths:\n- src/gov/launch/launcher.py\n- src/gov/launch/role.py\n- src/gov/launch/record.py\n- src/gov/launch/criticality.py\n- governance/project/criticality.yaml\n- tests/unit/launch/test_w2_184_*.py\n- docs/changes/W2-184-CIT-E.md\n- docs/probes/DAEO-6f0s/**  # the probe record\nreads:\n- .tickets/DAEO-cv58.md\n- governance/project/orchestration/packages/P1-W2-60a-P5.md\n- governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md\n- template/governance/kernel/roles/**\nneeds: []\nwaits_on: []\nkpis:\n  success:\n  - 'The session''s model and effort are RUBRIC-2''s for its role and criticality: read from the role file''s `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket''s criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket''s `class`, which is its kind); applied on the launch line (--model, --effort) and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses the launch; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3), CAP-35.c lite, lens F R1] (folds W2-21 S4) [from W2-60a S3, DEC-1167]'\n  - 'A model after -- that is not the resolved tier''s is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session''s tier model (CLAUDE_CODE_SUBAGENT_MODEL in the settings'' env), as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after -- with no trial: refused naming both [DEC-1120 (3), lens E F14] (folds W2-21 S4) [from W2-60a S4, DEC-1167]'\n  - 'The launch record also holds `tier`, `criticality`, `model_source` (role default, by criticality, after --, trial, promotion), the trial id and the promotion reason, each null when not given. Verify: a planted launch by criticality, one with a trial and one promoted each record their fields; a plain launch records them null [DEC-1120 (3)] [from W2-60a S8, DEC-1167]'\n  - 'On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [from W2-60a S10, DEC-1167]'\n  - 'A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table''s effort, recorded as `promotion` with the reason and the record''s path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [from W2-60a S11, DEC-1167]'\n  failure:\n  - 'A model below its tier with no trial; a promotion not applied; an effort below the floor. Verify: S3 and S4''s planted cases: a model below its tier with no trial is refused; a promotion is recorded and applied; an effort below high for a judgement role is refused [from W2-60a F4, DEC-1167]'\nnon_goals:\n- 'not W2-60a''s reviewed core (role text, skills, the record''s base fields, no compaction, the refused arguments): W2-60a lands it first'\n- 'not a gate for W2-27 (EXAMIN''s copy): launches during the copy use each role''s `Launch default` line (P1-W2-60a-P5 (B), DEC-1167)'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1167, DEC-1126, DEC-1120, DEC-1119, DEC-839, DEC-1010]\nacceptance_tests: {path: tests/acceptance/W2-184/}\n---\n\n# W2-184 RUBRIC-2 at launch (from W2-60a)\n\nThe owner's P1-W2-60a-P5 (B) (DEC-1167): RUBRIC-2's lines, added to W2-60a by DEC-1126 (3) after its three review\nrounds and never built, move here, so W2-60a lands its reviewed core and EXAMIN's copy runs on each role's\n`Launch default` line. The interface is the CTO's at claim, from W2-60a run 4d's proposal (`log/W2-60a-A5-run4d.json`):\n`criticality.yaml` and `ticket_criticality(root, ticket)`, the `Launch by criticality` line with its \"on FULL ... otherwise\"\nform, the effort floor and `--reason`, `--trial` reading `governance/project/trials/<id>.yaml`, promotion from the probe\nrecords, S10 counting the auditor's launch records with `--owner-named <DEC-id>`. Starts after W2-60a merges; its own\nreview rounds (new scope).\n",
  "authority": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1126",
      "sha256": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "reason": "declared in sources",
      "tokens": 662
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
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
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
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DAEO-cv58",
      "sha256": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "reason": "declared in sources",
      "tokens": 1529
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1126",
      "sha256": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "reason": "declared in sources",
      "tokens": 662
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
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
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
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DAEO-cv58",
      "sha256": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "reason": "declared in sources",
      "tokens": 1529
    }
  ],
  "supplementary": [
    {
      "id": "61820872a72cf41de19815bc",
      "path": "docs/probes/DAEO-cv58/PR-DAEO-cv58.md",
      "text": "   - `gov launch --plan` prints exactly the role file's `Launch default` line, and never reads `Launch by\n     criticality`.\n   - It starts nothing: no CLI call, no record, no temp folder, no lock, no gate.\n   - A missing or malformed line, and the role and ticket refusals, each exit 1 with `LAUNCH_REFUSED`, naming the\n     role file where it is the cause.\n   - Without `--plan`, a launch takes the same path as before.\n4. **S3, S4 and S8 back to their DEC-839 forms, and the merge of w2/integrate (5b7941b66): pass.**\n   - No RUBRIC-2 code (criticality, tier, trial, promotion) is read or recorded.\n   - The merge's resolution of `launcher.py` loses no refusal from either side. The line, the settings and the\n     record keep S3 to S8's behaviour:\n     - the role's model, recorded with `model_source`;\n     - an effort after `--` recorded as the launch's own;\n     - a model that is not the role's refused, naming both;\n     - `CLAUDE_CODE_SUBAGENT_MODEL` equal to the model, in both the settings and the process environment;\n     - no threshold;\n     - S7's arguments refused;\n     - one record, keyed by `--session-id`, present before the start;\n     - an unwritable record folder refused.\n",
      "tokens": 300
    },
    {
      "id": "b8aea606480a92a577b3c117",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md",
      "text": "> S4'' A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)]\n\n**Replaces line 9 (was DEC-1014 item 1: a different setting for the second review):**\n> S9' On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, DEC-1120 (2)]\n\n**Amends line 8 (the launch record):** its fields gain `tier`, `criticality`, `model_source`, the trial id and the promotion\nreason, each null when not given.\n\n**Adds a failure line:** \"A model below its tier with no trial; a promotion not applied; an effort below the floor.\"\n\nFor comparison, d-tools P-2 puts the same change as one line (the table, a refusal unless a promotion with its reason\n",
      "tokens": 298
    },
    {
      "id": "487c15ace9204c9fc37fd9f9",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md",
      "text": "## 2. The lines RUBRIC-2 would add\n\nFrom RUBRIC-2-APPLY \u00a73, in the ticket's form. Replace success lines 3 and 4; amend lines 8 and 9; add one failure\nline. The `Verify:` clauses of S4' and S9' are mine (RUBRIC-2-APPLY gives none for them).\n\n**Replaces line 3 (was: \"The role's default model and effort, read from its role file's default line ... [DEC-839 items 1, 2 and 5 ...]\"):**\n> S3' The session's model and effort are RUBRIC-2's for its role and criticality: read from the role file's `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket's criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket's `class`, which is its kind); applied on the launch line and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after `--`, trial, promotion); a missing or malformed line refuses; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3)]\n\n**Replaces line 4 (was: \"A model given after -- that is not the role's is refused ... [DEC-839 items 1 and 3 ...]\"):**\n",
      "tokens": 300
    },
    {
      "id": "84f315c28c271cfa48f9f2df",
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "text": "the designer is Sh and the rest unchanged (FULL reviewers are Oh).\n\n**W2-60a KPI lines that conflict, and their replacements** (replace success lines 3 and 4; amend 8 and 9; add one):\n- Now (3): \"role's default model and effort, read from its role file's default line ... [DEC-839 items 1, 2 and 5]\". Now (4): \"A model given after --\n  that is not the role's is refused ... subagent model is set to the session's model [DEC-839 items 1 and 3]\".\n- **S3'** The session's model and effort are RUBRIC-2's for its role and criticality: read from the role file's `Launch default` line and its\n  `Launch by criticality` line (C3, C2, C1, C0 overrides), the ticket's criticality derived from its profile and `allowed_paths` by\n  `governance/project/criticality.yaml` (never from the ticket's `class`, which is its kind); applied on the line and recorded with `tier`,\n  `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses; an effort below\n  high for a judgement role, or max with no `--reason`, is refused [DEC-1120 (2)-(3)]. Verify: a case per role x criticality on fixture role files.\n",
      "tokens": 289
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "  - 'The orchestration skill: the resume block comes first and the checkpoint stays under a set token budget; over it, the stop hook names it [DEC-1014, SMART-WORK-4 line 10]'\n  - 'Delegation does not count the recommendation and the proposer''s agreement as corroboration on a decision that touches verification; that needs an independent reviewer''s record [DEC-1014 item 1, row 4, SMART-WORK-5 B]'\n  - 'The daily document gives the week''s net ticket growth (filed minus closed, counted from the tickets) and the share of new tickets that fix the machinery; when net growth passes a configured share of the remaining plan in a week (default 5 %), it goes to the owner as one re-plan package with DEC-105''s three options, not as single P1s [DEC-1014 item 1, row 2, SMART-WORK-5 C]'\n  failure:\n  - 'A skill or template that still teaches the old rule (agreement counted as corroboration; a typed count; a rule with neither a mechanism nor \"prose only\").'\n  - 'A copy (.claude/, .rulesync/, template/.rulesync/) that differs from its kernel source.'\nprofile: STANDARD\nsources:\n- DEC-1022\n- DEC-1010\n- DEC-1014\n- DEC-1015\n- DEC-105\nest_loc: 120\nacceptance_tests:\n  path: tests/acceptance/W2-11b/\n",
      "tokens": 299
    },
    {
      "id": "DAEO-f58b",
      "path": ".tickets/DAEO-f58b.md",
      "text": "  - '`gov launch independent-test-designer` points the session''s retrieval at it; a designer''s retrieval never reads a ticket worktree''s store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role''s plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]'\n  - 'The store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]'\n",
      "tokens": 268
    },
    {
      "id": "DAEO-j9z6",
      "path": ".tickets/DAEO-j9z6.md",
      "text": "  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired Verify: grep of the close and queue code for this repository''s branch names, paths and ticket ids finds 0 lines; a planted second repository''s queue runs with the same code; this repository''s queue runs on it and W2-97''s tool is no longer called. [DEC-983, DEC-982] [moved from W2-117 S3, DEC-1083]'\n  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it Verify: a planted landing: the integration store''s refresh (W2-116) is started once afterwards and the queue''s own warm clones are seeded from that store, both visible in the queue''s record. [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3] [moved from W2-117 S4, DEC-1083]'\n",
      "tokens": 220
    },
    {
      "id": "DAEO-zkr9",
      "path": ".tickets/DAEO-zkr9.md",
      "text": "  - '`gov queue` gives W2-97''s queue in the product: the commit tested is the commit landed; one run per batch on the merged result, in a heavy-job slot (W2-20); a run skipped when the merged code is identical to what the lead tested, with its reason; a red batch''s culprit ejected and the rest advanced (W2-115''s attribution) [DEC-959 item 1, DEC-983, DEC-982]'\n  - 'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run, the close citing the queue''s record instead of running its own tests on the same code; no ticket sits merged but not closed [DEC-989, DEC-959 item 1, DEC-983, DEC-982, DEC-1003, SMART-WORK-2]'\n  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired [DEC-983, DEC-982]'\n  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3]'\n",
      "tokens": 285
    },
    {
      "id": "DEC-1015",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1015 \u2014 The jam of 2026-11-01: the hung embedding server's work re-run; its health and every slot holder's progress watched (standing); SMART-WORK-5 approved; a rebuild without its semantic store is a failed rebuild\n- **Status:** ACCEPTED (owner, 2026-11-01, in the chat, items 1 to 3; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; item 4 delegated, stricter-only, MR-6, DEC-537; items 2 and 4 standing) \u00b7 **Under:** DEC-1003, DEC-1007, DEC-1008, DEC-1012, DEC-1014, DEC-968\n- **Context:** the owner's operator found the shared embedding server (127.0.0.1:11434) hung (its model \"Stopping...\", no CPU) while three rebuilds waited on it for one to two hours in heavy-job slots: W2-04's worktree, the close of W2-05, W2-55 and W2-96, and the landing batch of W2-11, W2-105 and W2-81. It was restarted about 21:51. Each rebuild then answered `ok` with `stores.semantic` `not_recreated`, and each store held part of its vectors (1,536, 35,744 and 21,728 of about 50,000); the close and the batch went on to test on them.\n",
      "tokens": 279
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-66b | A | **New (DEC-1027 B).** W2-66's record-only case reads `win_toast.ps1` as code; a test revision under the owner's named decision (`DAEO-zuiy`). | test-revision | independent-test-designer | LITE | none | 2 | DEC-1027, DEC-906 |\n| W2-11b | A | **New (DEC-1022 item 3, P-W2-11-LINES (a)).** The seven KPI lines W2-11 landed without (SMART-WORK-3's reviewer template and qa-review line; SMART-WORK-4 lines 4, 6, 9, 10; SMART-WORK-5 B and C), word for word; starts once W2-11 closes; withdrawn if W2-11 takes them in another round (`DAEO-9bc0`). | skill | product-spec | STANDARD | W2-11 | 120 | DEC-1022, DEC-1014, DEC-1010 |\n| ACT 2 | \u2014 | **Milestone (DEC-954 item 6; PLAN-GROWTH-1 gap 4).** The one re-pin, an owner ACT, once memory, the roles and the three layers' foundations have landed; W2-100 and W2-101 start after it | milestone | owner | \u2014 | memory landed (K4), the roles landed (W2-33, W2-60b, W2-11), W2-104 | 0 | DEC-954 item 6 |\n| W2-55 | C | Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see (DEC-791) | implementation | engineer | STANDARD | W2-03 | 150 | DEC-791 (i) |\n",
      "tokens": 287
    },
    {
      "id": "85b4eff26dd0e6bc7205707e",
      "path": "governance/project/orchestration/packages/SMART-WORK-5.md",
      "text": "# SMART-WORK-5: DEC-1014 in the Gov OS (item 6, DEC-1003)\n\n**Priority:** P2. The lines marked **done** are already in their tickets. The lines marked **proposed** wait for the\nowner. Once approved, each is applied when its ticket next runs (DEC-1004).\n\n",
      "tokens": 64
    },
    {
      "id": "DEC-1014",
      "path": "docs/DECISION_REGISTER.md",
      "text": "- **Decision:** (1) The package's 9 practices, all approved (claims only through the dispatcher's readiness check; the status block generated from files; the remaining watchers into dispatcher passes; the dispatcher watches the sentinel's heartbeat; the checkpoint under 300 lines with RESUME HERE first, older blocks archived at each handover; a tool change carries its before-and-after measurement; on fail-open FULL tickets the second review uses a different model or effort, and a lead's agreement is not corroboration on a verification P2; the moderator's triage before any round is declared; net ticket growth in the daily document, over 5 % of the remaining plan in a week a re-plan package). (2) Its 15 KPI lines approved, each applied when its ticket next runs (`packages/SMART-WORK-4.md`), with the owner's condition on W2-115's quarantine: **a quarantined test is never left on a list; it is fixed at once or escalated, like any red (DEC-968).** (3) The two Wave 3 rows (W3-P19 canaries, W3-P20 an audit sample of the orchestrator's commits). (4) SIZING-1 option 0: W2-122 (`DAEO-blwa`, seeded rebuilds: the integration store the warm base for every new worktree and close copy, refreshed after every landing) and W2-123 (`DAEO-qzrq`, parallel requests on the embedding server, the 8-core cap checked not to become the limit) filed, at the front of the queue; the 28 GB WSL change not now. (5) A landing never waits for a close it does not conflict with: a mechanism in the dispatcher. (6) All of it reaches the Gov OS (DEC-1003): W2-122 and W2-123 are product tickets, so every adopted repository gets warm seeding and parallel embedding (each with a line: nothing of this repository or machine in the code); item 5 is W2-121's KPI; each of the 9 practices is mapped to its product ticket, with proposed lines where none existed and the ones that stay this repository's own named with why (`packages/SMART-WORK-5.md`).\n",
      "tokens": 483
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "---\nid: DAEO-9bc0\nstatus: closed\ndeps: [DAEO-k7hz]\nlinks: [DAEO-k7hz]\ncreated: 2026-11-02T00:18:23Z\ntype: task\npriority: 1\nassignee: product-spec\nexternal-ref: W2-11b\ntags: [wave-2, skill, standard]\nwbs_id: W2-11b\ntitle: 'The orchestration skill''s and the reviewer template''s seven lines that W2-11 landed without (SMART-WORK-3, SMART-WORK-4 lines 4, 6, 9, 10, SMART-WORK-5 B and C)'\nclass: skill\nstate_class: AUTHORITATIVE\nrole: product-spec\ndepends_on:\n- DAEO-k7hz\nallowed_paths:\n- template/governance/kernel/templates/brief-*.md\n- template/governance/kernel/skills/orchestration/**\n- template/governance/kernel/skills/qa-review/**\n- .claude/skills/orchestration/**\n- .claude/skills/qa-review/**\n- .rulesync/skills/orchestration/**\n- .rulesync/skills/qa-review/**\n- template/.rulesync/skills/orchestration/**\n- template/.rulesync/skills/qa-review/**\n- docs/changes/W2-11b-CIT-P.md\nkpis:\n  success:\n",
      "tokens": 226
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "# W2-11b The orchestration skill's and the reviewer template's seven lines\n\nThe owner's DEC-1022 item 3 (P-W2-11-LINES (a)): seven approved KPI lines meant for W2-11 (SMART-WORK-3's reviewer\ntemplate and qa-review line; SMART-WORK-4 lines 4, 6, 9 and 10; SMART-WORK-5 B and C) could not ride in W2-11's round,\nwhich landed without them. This ticket carries them, word for word. It starts once W2-11 (`DAEO-k7hz`) closes. If\nW2-11 goes back for another round instead, the seven lines ride along in that round and this ticket is withdrawn.\nSMART-WORK-5 B fixes a product defect: the kernel orchestration skill counts the recommendation's and the proposer's\nagreement as corroboration (`template/governance/kernel/skills/orchestration/SKILL.md`).\n\n**D9-FATES (DEC-1083):** Merged into W2-128 by DEC-1083. S1, F1 and F2 fold into W2-128's TPL-1 S3 and TPL-4 (no new line); S2 moved to W2-128 as the reviewer template's line; S3 to S7 lifted. S1's other half (the qa-review skill's triage, its blocking rule, the two-round cap and the two questions) lives in W2-11 S12 and W2-33's moderator line (S10 in D9-FATES' numbering, its S6 since its lifts and moves).\n",
      "tokens": 289
    },
    {
      "id": "W2-60a-CIT-E",
      "path": "docs/changes/W2-60a-CIT-E.md",
      "text": "### Behaviour 9: the launch record\n\n- **One record per launch,** a JSON file `<session id>.json` in the record folder, written whole and flushed before\n  the session starts. Keys:\n\n  | Key | Value |\n  |---|---|\n  | `record`, `format` | `\"gov-launch\"`, `1` |\n  | `session_id` | the UUID given with `--session-id` |\n  | `resumes` | the id given with `--resume`, or `null` |\n  | `started_at` | UTC, `YYYY-MM-DDTHH:MM:SSZ`, when the record is written |\n  | `root` | the real path of the tree the session starts in |\n  | `role`, `ticket` | as given to `gov launch` |\n  | `ticket_class` | the ticket's `class` as written, or `null` when it has none |\n  | `model`, `model_source` | the session's model; `\"role default\"` or `\"after --\"` |\n  | `effort`, `effort_source` | the same for effort |\n  | `subagent_model` | the value set in the settings' `env` |\n  | `compaction_threshold` | `\"none\"` |\n  | `role_text` | `{\"path\": \"template/governance/kernel/roles/<role>.md\", \"version\": \"<x.y.z>\", \"sha256\": \"\u2026\"}` |\n  | `appended_sha256` | the sha256 of `role-<role>.md` as written |\n",
      "tokens": 268
    },
    {
      "id": "DEC-1015",
      "path": "docs/DECISION_REGISTER.md",
      "text": "- **Decision:** (1) The work re-run: the close and the batch stopped and run again; W2-04's lead stopped in its scoped run (its tree clean, its work committed), its store rebuilt, and the lead resumed for the verification only. (2) A mechanism: the dispatcher checks the embedding server's health (a test request answered in time) and every slot holder's progress; a hung server or a holder idle too long becomes an inbox item and an alert, with a safe restart where one is configured. In the Gov OS: W2-121 and W2-123 each carry a KPI line for it (DEC-1003). (3) SMART-WORK-5 lines A to E approved, each applied when its ticket next runs: A (W2-60a), D (W2-116) and E (W2-117) are in their tickets now, since none is running. B and C (W2-11) wait for W2-11's landing: if it closes, their placement comes to the owner as a P1. (4) Delegated, stricter-only: a rebuild that answers `ok` without the semantic store it was asked for is a failed rebuild. `tools/rebuild_slot.sh` exits 75 on it (through `tools/rebuild_semantic_check.py`), so every lead, close and queue run refuses it. In the Gov OS, W2-122 carries \"`gov rebuild` exits non-zero, named, when the semantic store was asked for and not recreated; only `--no-embeddings` skips it\".\n",
      "tokens": 310
    },
    {
      "id": "DEC-1022",
      "path": "docs/DECISION_REGISTER.md",
      "text": "- **Decision:** (1) ACT-PUSH-INPUT-1's live test is re-run by day, after 07:30 on 2026-11-02: the CTO pings first, the owner steps away from the laptop and lets the prompt wait a few minutes (at 00:12 the owner approved from the laptop within 25 s, so the phone push was probably skipped as the owner was active). (2) P-W2-90b-1 (b): W2-90b's KPI S4 for W1-46's live sessions and W1-50's freeze launcher is re-baselined under DEC-822 item 3 (a live session judges the pinned guard by design; the non-live cases judge the worktree's code); the line sits in W2-90c (`DAEO-fu3n`, DEC-1016) and is re-worded there; nothing is lowered. (3) W2-11's seven unplaced lines (SMART-WORK-3's reviewer template and qa-review line; SMART-WORK-4 lines 4, 6, 9, 10; SMART-WORK-5 B and C): option (a), W2-11b (`DAEO-9bc0`, product-spec, STANDARD) filed with them word for word, to start once W2-11 closes; if W2-11 goes back for another round instead, the lines ride along in it and W2-11b is withdrawn. (4) SMART-WORK-4 line 3 (reviewer recall per model): option (c), Wave 3 row W3-P21.\n\n| Version | Date | Change |\n|---|---|---|\n",
      "tokens": 279
    },
    {
      "id": "W2-60a-CIT-E",
      "path": "docs/changes/W2-60a-CIT-E.md",
      "text": "  | `product-spec.md` | `- **Launch default:** model claude-opus-5-5, effort high` |\n  | `independent-auditor.md` | `- **Launch default:** model claude-opus-5-5, effort max` |\n\n  (`orchestrator.md` may carry `effort high` for W2-21; `gov launch` does not start the orchestrator.)\n- **Missing:** no line of the file begins with `- **Launch default:**`. **Malformed:** a line begins with it and is\n  not of the form above, or two lines begin with it. Either refuses the launch, naming the file and the form.\n- **Applied:** the role's model and effort go on the line (`--model`, `--effort`) unless given after `--`.\n- **An effort after `--`** (`--effort <e>` or `--effort=<e>`, `<e>` one of the five) is applied and recorded as the\n  launch's own (`effort_source: \"after --\"`); it may differ from the default (a FULL ticket's test designer at\n  `xhigh`, DEC-839 item 2). An unknown value, a missing value or a second `--effort` is refused.\n- **A model after `--`** (`--model <m>` or `--model=<m>`) that is not the role's, compared as written, is refused,\n  naming both. The role's own is accepted and passed once, where the caller put it (`model_source: \"after --\"`).\n",
      "tokens": 292
    },
    {
      "id": "90db41183fa8027082a4598c",
      "path": "src/gov/launch/launcher.py",
      "text": "def _launch_line(plan: dict, tmpdir: str, cli: Path) -> tuple[list[str], list[str], Path]:\n    \"\"\"W2-60a, once the temp folder exists: the appended file written, the launch record written before the session\n    starts and keyed by its id, and the launcher's own arguments: those before the caller's, and the one appended\n    file after them (W2-153's place). The record's path is returned, for its removal when the session cannot start.\"\"\"\n    given, model, effort = plan[\"given\"], plan[\"model\"], plan[\"effort\"]\n    appended = Path(tmpdir) / f\"role-{plan['role']}.md\"\n    appended.write_bytes(plan[\"composed\"])\n    session_id = str(uuid.uuid4())\n    origin = plan[\"origin\"]\n    written = record.write(plan[\"records\"], {\n        \"record\": \"gov-launch\", \"format\": record.FORMAT, \"session_id\": session_id,\n        \"resumes\": given[\"resume\"], \"started_at\": time.strftime(\"%Y-%m-%dT%H:%M:%SZ\", time.gmtime()),\n        \"root\": str(plan[\"root\"]), \"role\": plan[\"role\"], \"ticket\": plan[\"ticket\"], \"ticket_class\": plan[\"ticket_class\"],\n        \"model\": model, \"model_source\": \"after --\" if given[\"model\"] else \"role default\",\n",
      "tokens": 279
    },
    {
      "id": "0b1273abe270bd19bdbdfb98",
      "path": "tests/acceptance/W2-60a/test_w2_60a_launch_record.py",
      "text": "import json\nimport os\nimport shutil\nimport time\nimport uuid\nfrom pathlib import Path\n\nimport pytest\n\nimport w2_60a_support as s\n\nKEYS = (\"record\", \"format\", \"session_id\", \"resumes\", \"started_at\", \"root\", \"role\", \"ticket\", \"ticket_class\",\n        \"model\", \"model_source\", \"effort\", \"effort_source\", \"subagent_model\", \"compaction_threshold\", \"role_text\",\n        \"appended_sha256\", \"skills\", \"kept_out\", \"cli\")\n\n\n",
      "tokens": 103
    },
    {
      "id": "281cecc1fa879594e5b27306",
      "path": "tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py",
      "text": "def test_the_role_s_own_model_after_the_double_dash_is_passed_once(launch, passed):\n    arguments = (\"-p\", \"Do the ticket's work.\", *passed)\n    result = launch(s.ENGINEER, None, *arguments)\n    s.assert_launched(result)\n    s.assert_passed_through(result, arguments)\n    assert s.occurrences(result.args, \"--model\") == 1, f\"--model is passed more than once: {result.args}\"\n    record = result.record()\n    assert (record.get(\"model\"), record.get(\"model_source\")) == (s.OPUS, \"after --\"), (\n        f\"the record's model: {record.get('model')!r}, {record.get('model_source')!r}\")\n",
      "tokens": 145
    },
    {
      "id": "4e3bbc5bfa75521cca90e0e3",
      "path": "tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py",
      "text": "def test_the_role_s_default_model_and_effort_are_on_the_line_and_recorded(launch, role):\n    model, effort = s.DEFAULTS[role]\n    result = launch(role)\n    s.assert_launched(result)\n    assert result.one(\"--model\") == model, f\"--model on the line is not the role's {model}: {result.args}\"\n    assert result.one(\"--effort\") == effort, f\"--effort on the line is not the role's {effort}: {result.args}\"\n    record = result.record()\n    got = {key: record.get(key) for key in (\"model\", \"model_source\", \"effort\", \"effort_source\")}\n    assert got == {\"model\": model, \"model_source\": \"role default\", \"effort\": effort,\n                   \"effort_source\": \"role default\"}, f\"the record's model and effort: {got}\"\n",
      "tokens": 176
    },
    {
      "id": "27c3590403ff98541d38f37c",
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "text": "## 4. Practice gaps (smallest fix and route)\n| gap | smallest fix | route |\n|---|---|---|\n| launch_worker.sh:37 defaults every role to Opus; effort is positional with no class (:69-71) | `<role> <criticality> <brief>` resolving model and effort from a table; `--trial`, `--reason`; refuse below high and max without a reason | CTO scratch edit and its test (C1) |\n| spend.jsonl has no model, tier, criticality or promotion; effort only on launched rows | spend.py already takes `--extra key=value`: pass `model= tier= criticality= promotion=` from launch_worker.sh and in the helper rows | CTO (C1), no code change |\n| Agent-tool helpers that name no model take `CLAUDE_CODE_SUBAGENT_MODEL` (Opus) and the session effort | every Agent call passes `model` (alias sonnet, opus, haiku) and, on 2.1.292, `effort`; rule 11 already says so; check by the spend log | CTO practice |\n| no criticality field: `class` is the ticket's kind (DEC-1121 adds that same name to template 1.0.1; W2-60a KPI 8 says \"ticket's class\") | name the new one `criticality`, derived from `criticality.yaml` (profile + paths); no template change | W2-60a KPI (S3'), file is C2 |\n",
      "tokens": 288
    },
    {
      "id": "3f5aabfc5b699a6444503c41",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md",
      "text": "\n**Replaces line 4 (was: \"A model given after -- that is not the role's is refused ... [DEC-839 items 1 and 3 ...]\"):**\n> S4' A model after `--` that is not the resolved tier's is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session's tier model, as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after `--` with no trial: refused naming both [DEC-1120 (3)]\n\n**Adds:**\n> S4'' A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)]\n\n**Replaces line 9 (was DEC-1014 item 1: a different setting for the second review):**\n",
      "tokens": 283
    },
    {
      "id": "f048d265448762c41ce4a424",
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "text": "  high for a judgement role, or max with no `--reason`, is refused [DEC-1120 (2)-(3)]. Verify: a case per role x criticality on fixture role files.\n- **S4'** A model after `--` that is not the resolved tier's is refused naming both, unless `--trial <id>` names a recorded trial (role, criticality,\n  model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the\n  session's tier model, as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251) [DEC-1120 (3)].\n- **S4''** (promotion) A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's\n  effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. Verify: planted review records.\n- **S9'** (was DEC-1014 item 1) On a FULL ticket the second review is the probe, Opus max, the first Opus high; the record shows both; the same setting\n  twice is refused unless the owner named it; max on any other review needs `--reason` [DEC-1014, DEC-1120 (2)].\n",
      "tokens": 283
    },
    {
      "id": "560c798434ca02991dbc3f62",
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "text": "| P1-18 | **RUBRIC-2 (DEC-1120) in the product, through W2-33 (roles and typed handoff) and W2-60a (role, skills, model and effort at launch), before EXAMIN's copy** (DEC-1120 (5), DEC-1119 (2)). W2-33 (C3: the kernel) puts `Launch default:` and `Launch by criticality:` lines in each role file with RUBRIC-2's values. W2-60a (C3 recommended, FULL, three review rounds so promotion to Opus is already met) takes S3' (model and effort from the role file by criticality, derived from `governance/project/criticality.yaml`, never the ticket's `class`), S4' (a model not the tier's is refused unless `--trial <id>`), S4'' (promotion after two failed reviews or a fail-open finding), S9' (a FULL ticket's second review is the probe, Opus max; the first Opus high) and a failure line; W2-60b's record takes tier, criticality and promotion. Tests revised by an independent designer (Opus high, `Rewrite-Reason: DEC-1120`). **Drift found:** none of W2-33, W2-60a or W2-60b carries DEC-1120 yet (checked 11-11); W2-60a's ticket says it merges after \"W2-11's widening\" writes the role files' default lines, RUBRIC-2-APPLY \u00a73 puts them in W2-33: the KPI edit settles which; row 105 holds all three for the reset (usage (A)) | `packages/RUBRIC-2-APPLY.md` \u00a73 (the deltas and the draft KPI lines) and \u00a74 (the practice gaps); `.tickets/DAEO-lrre.md`, `DAEO-cv58.md`, `DAEO-ecac.md`; branch `w2/W2-60a` (unreviewed against RUBRIC-2; needs a merge of integrate) | W2-33 7\u20139 lead-h (FORECAST-W2-1); W2-60a 5\u20138 lead-h more (revised tests, build, two reviews); W2-60b about 0.5 (E); the owner's hash approval and one class (b) yes for the agents' copies (a night costs 10.8 h, M, FORECAST-W2-2 \u00a74) | each task on the model and effort its class calls for (DEC-1120's basis) | in aim / yes / a wrong tier refusal fails closed | **Product-spec** (KPI edits, role-file lines), **independent test designer** (Opus high), **engineer** (Opus high, C3), **reviewer** (Opus high; the FULL probe Opus max); the kernel half by CAP-33 (evidence, review, the owner's approval and hash), then a class (b) ACT for `.claude/agents/**` (DEC-315). **Verified:** a case per role \u00d7 criticality on fixture role files; `spend.jsonl` rows with model, effort, tier and criticality (RUBRIC-2-APPLY's draft KPI lines) | tickets, a CIT-P, one ACT | P1-15, P1-16; the reset under (A); W2-60a before W2-60b; the KPI edits first |\n",
      "tokens": 596
    },
    {
      "id": "1de9105a0509c8afe4b700d2",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "text": "> The model and effort a launch applies come from one table by the role and the ticket's criticality class (C0-C3), read from one file in the kernel; a model or effort given after `--` that differs from the table is refused unless a promotion with its recorded reason (two failed review rounds, or a fail-open finding) is given; the launch record holds the class, the tier and any promotion reason. Verify: planted tickets of each class for each role: the built command line carries the table's model and effort; a differing `--model` is refused; a promotion with a reason is recorded, one without is refused [DEC-1120 (2)-(3), DEC-1119 (2)]\n\nand for W2-33: the role file's machine-readable defaults carry the class column the table needs [DEC-1120 (2)].\n\n**P-3. W2-60b (DAEO-ecac), rows D1 and D2 (the spend log's RUBRIC-2 keys).**\n> The session record carries the tier (opus, sonnet, haiku or other, derived from the model's name), the ticket's criticality class and any promotion reason, each null when it is not given. Verify: a planted launch with a promotion: the record holds all three; one without: three nulls [DEC-1120 (3)]\n\n",
      "tokens": 284
    },
    {
      "id": "605669129471221b809406b1",
      "path": "governance/project/prompts/w2-orchestrator.md",
      "text": "    Every other P2 is the CTO's, recorded and listed in the digest (DEC-1112 (3)).\n11. **Context and models (DEC-1118, DEC-1141):** (A) there is no token cap for any session (the CTO, leads, workers\n    and helpers): each uses its model's full window and compacts; before compaction the hook writes the checkpoint\n    and handover, and the summary opens with the read-first line; the CTO starts a fresh session each morning after\n    the digest and its handover (DEC-1140 (4)); (B) the CTO\n    checkpoints and clears before any planned idle of more than an hour; (C) every launch's and helper's model and\n    effort follow **RUBRIC-2 (DEC-1120)**, by role and criticality class (C3/C2/C1/C0): every spawn names its model and\n    effort; ACT preparers, product-spec, research and helpers on Sonnet, high; C3 work, leads, auditors and checkers on\n    Opus, high; promotion to Opus after two failed reviews\n    or a fail-open finding; max only with a recorded reason. Every session's cost is logged at list price in\n    `log/spend.jsonl`, with its tier, class and any promotion.\n\n",
      "tokens": 270
    },
    {
      "id": "DAEO-qzrq",
      "path": ".tickets/DAEO-qzrq.md",
      "text": "---\nid: DAEO-qzrq\nstatus: closed\ndeps: []\nlinks: [DAEO-r30l]\ncreated: 2026-11-01T21:35:00Z\ntype: task\npriority: 0\nassignee: engineer\nexternal-ref: W2-123\ntags: [wave-2, implementation, retrieval, speed, standard]\nwbs_id: W2-123\ntitle: 'The shared embedding server serves several requests at once within its CPU cap, with the vectors unchanged, and the cap is measured not to become the new limit (SIZING-1 option 0, DEC-1014)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/retrieval/ollama.py\n- src/gov/retrieval/semantic.py\n- tests/unit/retrieval/test_w2_123*\n- docs/changes/W2-123-evidence.md\nkpis:\n  success:\n  - 'A rebuild''s embedding request that times out behind other clients on the shared server is retried, bounded (at most three tries with a growing wait, each try under the existing per-request timeout), and the semantic stage still ends not_recreated, named, after the last failed try: never a partial store reported as built; the tries and waits are stated in the rebuild''s result [DEC-1026, DEC-1015 item 4]'\n",
      "tokens": 271
    },
    {
      "id": "DAEO-5rgj",
      "path": ".tickets/DAEO-5rgj.md",
      "text": "  - 'The morning report lists every crash or error in the servers'' logs overnight (CUDA errors, runner exits, model loads and their layers, failed and timed-out requests with their counts), beside the nightly''s tests [DEC-1030 item 3, DEC-1031 item 4] [lifted (was S17), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n  - 'The dispatcher alerts when the orchestrator''s session or its sentinel has no heartbeat for a configured time [DEC-1014 item 2, SMART-WORK-4 line 11] (to Wave 3, W3-P16, W-10) [re-scoped, DEC-1083] (was S12)'\nnon_goals:\n- the dispatcher core (W2-121, part a) and the other parts\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]\nacceptance_tests:\n  path: tests/acceptance/W2-121c/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\n---\n",
      "tokens": 262
    },
    {
      "id": "DAEO-6w5n",
      "path": ".tickets/DAEO-6w5n.md",
      "text": "  - 'A key result or a return reported twice, or not at all. Verify: a planted key-result commit and a planted return, each present through several passes: each is reported once, and each planted one is reported (none missing). [moved from W2-118 F1, DEC-1083]'\nnon_goals:\n- the dispatcher core (W2-121, part a) and the other parts\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]\nacceptance_tests:\n  path: tests/acceptance/W2-121d/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\n---\n",
      "tokens": 192
    },
    {
      "id": "DAEO-blwa",
      "path": ".tickets/DAEO-blwa.md",
      "text": "  - 'Measured, in docs/changes/W2-122-evidence.md: a new worktree''s first rebuild seeded from the integration store against a cold one, alone and with two others running, on this repository (the semantic stage''s seconds and the embedding requests sent) [DEC-1014, DEC-996 item 3 A]'\n  - 'A product feature for every adopted repository: the warm base is the project''s configured integration store (W2-116''s, a path in the project''s configuration), never a path of this repository in the code; a project without one rebuilds cold, named [DEC-1014 item 6, DEC-982]'\n  failure:\n  - 'A seeded store that differs from a cold rebuild''s; a seed from another embedder or schema used [DEC-1014]'\nprofile: STANDARD\nsources:\n- DEC-1014\n- DEC-1011\n- DEC-1001\n- DEC-1015\n- DEC-1027\n- DEC-982\n- DEC-996\nest_loc: 150\nacceptance_tests:\n  path: tests/acceptance/W2-122/\n  author: independent-test-designer (MR-3)\ntrack: A\nlist_rows: []\n---\n",
      "tokens": 232
    }
  ],
  "supplementary_query": "RUBRIC-2 at launch: criticality from criticality.yaml, the Launch by criticality line, the effort floor, trials, the second review's setting, promotion (from W2-60a)\nThe session's model and effort are RUBRIC-2's for its role and criticality: read from the role file's `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket's criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket's `class`, which is its kind); applied on the launch line (--model, --effort) and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses the launch; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3), CAP-35.c lite, lens F R1] (folds W2-21 S4) [from W2-60a S3, DEC-1167]\nA model after -- that is not the resolved tier's is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session's tier model (CLAUDE_CODE_SUBAGENT_MODEL in the settings' env), as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after -- with no trial: refused naming both [DEC-1120 (3), lens E F14] (folds W2-21 S4) [from W2-60a S4, DEC-1167]\nThe launch record also holds `tier`, `criticality`, `model_source` (role default, by criticality, after --, trial, promotion), the trial id and the promotion reason, each null when not given. Verify: a planted launch by criticality, one with a trial and one promoted each record their fields; a plain launch records them null [DEC-1120 (3)] [from W2-60a S8, DEC-1167]\nOn a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [from W2-60a S10, DEC-1167]\nA ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [from W2-60a S11, DEC-1167]\nA model below its tier with no trial; a promotion not applied; an effort below the floor. Verify: S3 and S4's planted cases: a model below its tier with no trial is refused; a promotion is recorded and applied; an effort below high for a judgement role is refused [from W2-60a F4, DEC-1167]",
  "further_batch": [
    {
      "id": "DAEO-cb2b",
      "path": ".tickets/DAEO-cb2b.md"
    },
    {
      "id": "DAEO-f58b",
      "path": ".tickets/DAEO-f58b.md"
    },
    {
      "id": "DAEO-ifgf",
      "path": ".tickets/DAEO-ifgf.md"
    },
    {
      "id": "DAEO-j9z6",
      "path": ".tickets/DAEO-j9z6.md"
    },
    {
      "id": "DAEO-mb2t",
      "path": ".tickets/DAEO-mb2t.md"
    },
    {
      "id": "DAEO-qzrq",
      "path": ".tickets/DAEO-qzrq.md"
    },
    {
      "id": "DEC-1014",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "DEC-1022",
      "path": "docs/DECISION_REGISTER.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "61820872a72cf41de19815bc",
          "path": "docs/probes/DAEO-cv58/PR-DAEO-cv58.md"
        },
        {
          "id": "b8aea606480a92a577b3c117",
          "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md"
        },
        {
          "id": "487c15ace9204c9fc37fd9f9",
          "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md"
        },
        {
          "id": "84f315c28c271cfa48f9f2df",
          "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "DAEO-f58b",
          "path": ".tickets/DAEO-f58b.md"
        },
        {
          "id": "DAEO-j9z6",
          "path": ".tickets/DAEO-j9z6.md"
        },
        {
          "id": "DAEO-zkr9",
          "path": ".tickets/DAEO-zkr9.md"
        },
        {
          "id": "DEC-1015",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "85b4eff26dd0e6bc7205707e",
          "path": "governance/project/orchestration/packages/SMART-WORK-5.md"
        },
        {
          "id": "DEC-1014",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "W2-60a-CIT-E",
          "path": "docs/changes/W2-60a-CIT-E.md"
        },
        {
          "id": "DEC-1015",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1022",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "W2-60a-CIT-E",
          "path": "docs/changes/W2-60a-CIT-E.md"
        },
        {
          "id": "90db41183fa8027082a4598c",
          "path": "src/gov/launch/launcher.py"
        },
        {
          "id": "0b1273abe270bd19bdbdfb98",
          "path": "tests/acceptance/W2-60a/test_w2_60a_launch_record.py"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "281cecc1fa879594e5b27306",
          "path": "tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py"
        },
        {
          "id": "4e3bbc5bfa75521cca90e0e3",
          "path": "tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py"
        },
        {
          "id": "27c3590403ff98541d38f37c",
          "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md"
        },
        {
          "id": "3f5aabfc5b699a6444503c41",
          "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md"
        },
        {
          "id": "f048d265448762c41ce4a424",
          "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md"
        },
        {
          "id": "560c798434ca02991dbc3f62",
          "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md"
        },
        {
          "id": "1de9105a0509c8afe4b700d2",
          "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md"
        },
        {
          "id": "605669129471221b809406b1",
          "path": "governance/project/prompts/w2-orchestrator.md"
        },
        {
          "id": "DAEO-qzrq",
          "path": ".tickets/DAEO-qzrq.md"
        },
        {
          "id": "DAEO-5rgj",
          "path": ".tickets/DAEO-5rgj.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DAEO-6w5n",
          "path": ".tickets/DAEO-6w5n.md"
        },
        {
          "id": "DAEO-blwa",
          "path": ".tickets/DAEO-blwa.md"
        },
        {
          "id": "DAEO-cb2b",
          "path": ".tickets/DAEO-cb2b.md"
        },
        {
          "id": "DAEO-f58b",
          "path": ".tickets/DAEO-f58b.md"
        },
        {
          "id": "DAEO-ifgf",
          "path": ".tickets/DAEO-ifgf.md"
        },
        {
          "id": "DAEO-j9z6",
          "path": ".tickets/DAEO-j9z6.md"
        },
        {
          "id": "DAEO-mb2t",
          "path": ".tickets/DAEO-mb2t.md"
        },
        {
          "id": "DAEO-qzrq",
          "path": ".tickets/DAEO-qzrq.md"
        },
        {
          "id": "DEC-1014",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1022",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "DAEO-cb2b",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-f58b",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-ifgf",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-j9z6",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-mb2t",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-qzrq",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1014",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1022",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-6f0s): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 15849,
  "budget": {
    "limit": 16000,
    "used": 15849
  },
  "left_out": {
    "count": 4,
    "superseded": [
      "DEC-045",
      "DEC-636",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "82837694f3d9a883acc6e44d9656a297cc0981881d1a9ac4c30e76a459835967"
}
