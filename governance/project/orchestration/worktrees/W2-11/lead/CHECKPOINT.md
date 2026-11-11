# W2-11 (DAEO-k7hz) lead checkpoint: round 2 of 2 (DEC-916), run r6-resume (hand-built brief, DEC-1130 (1))

STATE: step 3 done (verify + accept), starting step 4/5 | HEAD: c96136eb6xxx (see git) | NEXT: tests worktree, then td-r2 + ps-r2 in parallel | WAITING ON: none

task: DAEO-k7hz · decisions_applied: DEC-1137, DEC-866, DEC-959, DEC-963, DEC-983, DEC-991, DEC-995, DEC-996, DEC-1010

## Step 1 (first calls)
- identity orchestrator DAEO-k7hz; tree /home/usain/gov-os-worktrees/W2-11, w2/W2-11; status clean.
- Pre-run commits above merge 4e265aabed5c: c174e2c7f (product-spec, Task DAEO-k7hz, Implements DEC-1137, DEC-866, DEC-959, DEC-847),
  c96136eb6 (independent-test-designer, Task DAEO-k7hz, Implements DEC-1137, Rewrite-Reason: DEC-1137 re-baseline). Both present.
- README map numbering: success-1..12 and failure-2 = the ticket's numbering (S5 = loose citations, F2 = DEC-866). OK.

## Step 2 (read-only verification of the restored skills)
| line | met? | where |
|---|---|---|
| S1 | met | test-design/SKILL.md "How much is enough" (DEC-221, DEC-951 item 5; 2,980/713 named) |
| S2 | met | orchestration/SKILL.md Briefs bullet 2 (twelve fields, payload after, two-refusal stop, AR-6); briefs-and-returns.md "The return" |
| S3 | met | SKILL.md Temp hygiene bullet 2 (DEC-820); Decisions bullet 5 (DEC-861, DEC-862); briefs-and-returns.md Policy 2 + decision-record sections |
| S4 | met | briefs-and-returns.md "The exit audit's reading of MR-3 (DEC-430)"; audit/SKILL.md line 75 |
| S5 | met | identity DEC-371 (Sessions b1); stop block DEC-537, DEC-948 (Stops b3); DEC-486 kept only for the closed count |
| S6 | met in sources | no LEAD_CHECKPOINT / context-limit stop / listing refusal / fixed ceiling in skill folder, role file, .rulesync; "No fixed number" (DEC-847); decision-record (DEC-861). .claude copy stale (copies ACT) |
| S7 | met | test-design SKILL "Kinds and cost" + test-kinds.md |
| S8 | met (repository-state cases green) | governance/project/orchestration/brief-gaps.md vs common brief |
| S9 r1 half | met | templates/skill.md sections in order; r2 half NOT met (front matter not closed / no `output`, no Never statement on reads/writes) |
| S10 | met | test-design SKILL work order, red against base, ISTQB, proportion, README map |
| S11 | met | orchestration integration-queue.md, nightly-sheriff.md, incident-response.md; qa-review/SKILL.md + scenarios.md |
| S12 | no case by design | first half retired (DEC-1137 (1)), second half Wave 3 (DEC-1083) |
| S13, S14, S16 | not met | no text in skill folder |
| S15 | partly | test-kinds.md load-sensitive row "times the code's own work, never the machine's load (DEC-979 item 1)"; no CPU-time / quiet-reference / same-bound statement |
| F1 | not met | no rule, no case |
- body_tokens: orchestration 9976 chars = 2494 tok OK; test-design 5377 = 1345 OK; audit 6534 = 1634 OK; qa-review 4975 = 1244 OK.
- version == metadata.version in every kernel skill (adopt has no metadata, W2-52's).
- copies_diff: exactly discovery (copy 1.0.0), retrieval (copy 1.0.0), orchestration (body differs, no metadata), test-design (body differs, no metadata).

## Step 3
- disk gate open (816 GiB, 64.7M inodes). rebuild-r6 exit 0 (log/rebuild-r6.log).
- gov accept (log/accept-r6-base.json): exit 3, fail; 99 passed, 7 failed, 1 skipped. Lines pass: S1-S5, S7-S10, F2. Fail: S6 (1), S11 (2), unmapped (4).
- The 7 failing = exactly the seven copy cases of the brief (pytest -rf confirmed). No other red.
- No case: S12 (by design), S13, S14, S15, S16, F1, S9 r2 half. Confirms the brief's "Round 2's lines" bullet.

## Workers
(none yet)

## Decisions taken
- none

## Open packages
- P-a (open point 3): S16's template half has no file in W2-11's paths.
- P-b (open point 1): metadata.version read as the one carried repeat (only if a conflict appears).
- Housekeeping (open point 4, CTO): allowed_paths brief-*.md entry; W2-L257, W2-L258 no longer applicable.

## Brief gaps (running)
- the whole-folder pytest form with HOME empty finds no pytest (user site) | ticket's part / common brief | 2 (est.)

## Guard refusals
- none so far
