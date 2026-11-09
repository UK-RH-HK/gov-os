# D5-STATUS: the templates, item by item (CTO, 2026-11-09; DEC-1109 (2) restarted D-5)

Under DEC-1052 (templates; READY and DONE by code), DEC-1079 (D-5 starts), DEC-1083 (W2-128's ready check), DEC-1088 (3)
(the dependency fields), DEC-1094 (4) (the search-again line). Home ticket: W2-128 (`DAEO-t8mp`), now `in_progress`,
its interface and its two rounds stated in the ticket's body (D5 row 9). Sources: `P1-PLAN.md` D-5 row and §E,
`R3-TEMPLATES.md` §D, `D5-ROWS.md`, `LINK-INTEGRITY.md` §5.

**Counts (22:40):** round 1 **READY, not merged** (`w2/W2-128` **`baa2696f713f`**, tests `bd7732def530` and the
W1-35 revision `7f65bf5a82c7`; `gov accept` 92/92;
review READY by `verdict.py`, `reviews/w2-128-r1.md`): 14 of W2-128's 21 success lines and F1, F7 met on the branch in
their round-1 parts; TPL-3 S5's scripts done; D5 rows 1-17 carried; the MR row moved out (W2-151). Not started: the
round-2 code half (TPL-2 S3, TPL-3, TPL-4, TPL-5 S3), TPL-6, TPL-7, TPL-8. Before the merge: four W1-35 cases
revised and the review's F1-F5, F9 fixed (done, below).

## The eight packages

| item | state | what it waits on |
|---|---|---|
| TPL-1 the kernel template set (T-0 to T-8, S1-S5, F1) | **READY on `w2/W2-128`** (round 1) | nothing; the kernel part's CIT-P review and the owner's approval at the end (CAP-33) |
| TPL-2 the facts file and its schema (S1, S2, S4) | **READY on `w2/W2-128`** | nothing; S3 (a switch flipped in a filled brief) waits on TPL-3's generator |
| TPL-3 S5 the three scripts | **done** 2026-11-06 (`launch_worker.sh`, `lead_verify.sh`, `wait_for.sh` with their shell tests, the CTO's tools) | the facts naming them: round 1 |
| TPL-3 S1-S4, S6, S7 `gov brief` | not started | **the owner:** the split into an engineer's ticket (W2-128's body: its paths hold no `src/`); then TPL-1 and TPL-2 |
| TPL-4 delivery (the launcher flag, the dispatcher, rulesync, `.claude/` copies) | not started | the same split; after TPL-3; **the owner:** the `.claude/` copies ACT |
| TPL-5 S1-S2 the ticket schema and T-1 | **READY on `w2/W2-128`** | nothing |
| TPL-5 S3 the ready check (refuses missing fields, DEC-1083; `READS_MISSING`, `NEEDS_MISSING`, `WAITS_ON_MISSING`, DEC-1088 (3)) | not started | inside `gov brief`: the split (round 2) |
| TPL-6 retire the contradicting layers | not started | after TPL-4 and the owner's row decisions (the `steps` switches); **the owner:** Appendix A of the CTO prompt (S1); S2 (LEAD-w2-common, `build_lead_brief.py`, DEC-1057 item 9) after `gov brief`; S3's two skills in the CIT-P |
| TPL-7 measures (`check_return.py`, `template_report.py`) | not started | the T-0 return form (TPL-1, round 1); the CTO's tools lane; one worker at a time |
| TPL-8 the pilot | not started | last: after TPL-3, TPL-4 and TPL-7 |

## D5-ROWS

| rows | state | where it lands |
|---|---|---|
| 1-9 (the CTO's lines from 2026-11-03) | **READY on `w2/W2-128`**; added to W2-128 as one KPI line (string test per row; marked DEC-1109 (2)) | T-4 (1, 7), T-5 (2), T-7 and T-8 (3, 4, 8, 9), T-0 (5, 6) |
| 10-17 (LINK-INTEGRITY §5, the lines per recording role) | **entered** in `D5-ROWS.md` today (the CTO's step); **READY on `w2/W2-128`** under W2-128's link-lines KPI line | T-0 to T-8, T-1, the record templates; the skills' halves (orchestration, test-design, audit) in TPL-6 S3's CIT-P |

## The MR-1..MR-6 status row (DEC-1074 (8))

**Moved out of D-5:** W2-130's sitting (DECIDED-NOT-DONE row 24) settled it as "regenerate the six
`docs/contract/master-rules/MR-n.md` from `contract.yaml`", and row 65 carries it in **D-6 part 2** (another agent's
lane), now filed as **W2-151** (`DAEO-qzca`, `56ad463a`). Today the six files still say `PROPOSED` against
`contract.yaml`'s ACCEPTED. Not touched here.

## W2-128's KPI lines (21 success, 7 failure)

| line | state |
|---|---|
| TPL-1 S1, S2, S3, S4, S5 | round 1 |
| TPL-2 S1-S4 | round 1 (S1, S2, S4); S3 round 2 |
| TPL-3 S1-S4, S6, S7 | round 2 (the split) |
| TPL-3 S5 | scripts done; the facts line round 1 |
| TPL-4 S1-S4 | round 2 (the split); the ACT for the owner |
| TPL-5 S1-S3 | round 1 (schema, T-1); the ready check round 2 |
| TPL-6 S1-S4 | after TPL-4; Appendix A for the owner |
| TPL-7 S1-S3 | not started (the CTO's tools, after round 1) |
| TPL-8 S1-S3 | last |
| the link lines (DEC-1073 (5)(c)) | round 1 (the string tests; the planted-record `gov links` case where `gov links` runs in the sandbox) |
| the facts' `links` command | round 1 |
| the three schemas' `sources` / `decisions` | round 1 |
| the CIT-P record and the `.claude/` ACT | the record's draft round 1; the review, the owner's approval and the ACT after round 2 |
| the reviewer's reversal line (DEC-1014) | round 1 (T-6) |
| the dependency fields (DEC-1088 (3)) | the template round 1; the ready check's refusals round 2 |
| search again once (DEC-1092 (1), DEC-1094 (4)) | round 1 (T-0 and T-8). W2-142, the kernel skills' half, is merged (`984a3ba9`, review READY) and lands at the lift's re-pin ACT |
| D5-ROWS 1-9 (added today) | round 1 |
| the seven failure lines | with their success lines' rounds |

## For the owner (prepared, not applied)

1. **The split** for W2-128's code half: one engineer's ticket for TPL-3's `gov brief` (with TPL-5 S3's ready check and
   TPL-2 S3) and TPL-4's launcher and dispatcher flag (W2-128's body; `gov launch` starts an engineer only on an
   engineer's ticket). The CTO drafts it when round 1 is READY.
2. **The templates' approval** (R2-3, DEC-1052): after round 1's review, with the CIT-P record `docs/changes/W2-128-CIT-P.md`.
3. **The `.claude/` copies ACT** (TPL-4 S3-S4; W2-128's CIT-P line): after round 2.
4. **TPL-6 S1, Appendix A** of `governance/project/prompts/w2-orchestrator.md` cut to a pointer under 600 characters:
   after TPL-4.

## Log

- 2026-11-09: status written; D5 rows 10-17 entered; W2-128 `in_progress` with its interface, rounds and the D5-ROWS 1-9
  line; round 1's independent test designer launched in `/home/usain/gov-os-worktrees/W2-128-tests` (`w2/W2-128-tests`).
- 2026-11-09: round 1's designer done: `w2/W2-128-tests` **TESTS-READY `97489c19d283`** (S1-S6, S8, S10, S14-S21, F1,
  F7; red on integrate but the green guards: existing tickets and records valid, the record templates' `gov links`);
  tripwire changes all other lanes'. The CTO's P1 (b) (`waits_on` items keyed `ref`, not `on`) and P2 (a) (a string
  or `{ref, reason}`) in the ticket's interface; the designer's revision for `ref` next, then the product-spec worker.
- 2026-11-09: designer revision 2 **TESTS-READY `bd7732def530`** (92 cases); product-spec round 1 `w2/W2-128`
  **`a6c83d497035`** (31 files: T-0 to T-8, `keys.yaml`, `facts.yaml` and its schema, four schemas, record templates'
  link lines, `brief-*.md` pointers, `roles/engineer.md` line 5 and its `.rulesync` copies, the CIT-P draft); the CTO's
  `gov accept W2-128` outside the sandbox 92/92; review **READY** (`reviews/w2-128-r1.md`): F1-F5, F9 in scope but
  `other` (the designer's commands bound to `{TREE}`, two step lines citing lifted rules, `[DEC-254]` to `[DEC-963]`,
  "Ask memory first" against the sandbox, a double evidence quote, a count); F6-F8 out (TPL-6, round 2).
- **Before the merge (the CTO):** (1) four W1-35 cases on `brief-*.md` red by TPL-1 S4 (confirmed by the CTO): a test
  designer's revision under DEC-866 with `Rewrite-Reason:`; (2) F1-F5 and F9 as one small product-spec fix round, or
  carried into round 2 as the reviewer allows (DEC-802); (3) at the merge, `LEAD-w2-common.md` lines 87, 149, 163
  (F6) pointed to the templates; (4) W1-30's template-ticket cases (`test_w1_30_r16_context_own_tickets.py`) run
  outside the sandbox (they build a store; not run here).
- 2026-11-09 22:40: **the before-merge items (1) and (2) done.** W1-35's four cases revised by a test designer under
  W2-128 (`w2/W2-128-tests` **`7f65bf5a82c7`**, `Rewrite-Reason:`, DEC-866: each follows a retired `brief-*.md` to its
  replacement; DEC-462's case wanted one line in T-4), merged into `w2/W2-128` by the CTO (`71817b01`); one product-spec
  fix round **`baa2696f713f`**: F1 (the designer's forms on `{WRITE_TREE}`), F2 and F5 (`checkpoint_record`,
  `collect_only`, `trailer_gate` off: lifted by DEC-1057 and DEC-953), F3 (`[DEC-963]`), F4 ("Ask memory first"
  qualified for the sandbox, DEC-1065), F9, and the DEC-462 line. The CTO's runs outside the sandbox: `gov accept
  W2-128` 92/92; W1-35's brief cases 7/7 (all of W1-35 was 124 passed on the tests branch, the designer's run); schema
  ok. Structural pass on the branch against integrate: 8 of 10 ok; portability NOTICE (the W2-142 skills' and the
  engineer role's `.claude/` copies, regenerated at the ACT, expected); links NOTICE: `DAEO-0000` in
  `templates/checkpoint.md:7`'s example (W2-128's; a placeholder for round 2), the other two other lanes'.
  **Still before the merge (the CTO's):** (3) `LEAD-w2-common.md` lines 87, 149, 163 pointed to the templates; (4) W1-30's
  template-ticket cases outside the sandbox. Review F6-F8 go to round 2 (TPL-6, TPL-4).
