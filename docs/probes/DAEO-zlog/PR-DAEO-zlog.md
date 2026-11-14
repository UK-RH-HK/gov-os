---
type: probe
task: DAEO-zlog
ticket: W2-188
round: 1
reviewer_role: independent-auditor
reviewer_session: "independent-auditor au-1 2bd2339c-ba97-4e67-bf75-69f84af5a970 (Opus, high, read-only through gov launch, class C2, 2026-11-14); not an author of the change"
implementer_session: "product-spec ps-1 1b67d74f-70d7-418e-970e-99b8f12aee8d (d782640de); product-spec ps-2 f7f2e9bc-d577-49b8-a2a6-15a5e99b3b47 (8aa930660, 857e5b3bf, 8ee9b7c36); product-spec ps-3 7eb0249a-85dc-48a5-8121-b3bdf82c22ac (be8b99ccb, 8c2e5d7ff, b75472d48)"
test_designer_session: "independent-test-designer td-1 50730df3-4f6a-4ad2-8788-d3ac8363236e (3c5167c47, merged 599fa2a22)"
reviewer_wrote_nothing: true
probed_commit: b75472d4825cece64936451f21b259787b5ecf97
base: 5336a6fca
decisions: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1074, DEC-1072, DEC-1071, DEC-105, CAP-33, DEC-801, DEC-808, DEC-1010]
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
---

# PR-DAEO-zlog: independent review, round 1

The probed head is b75472d48 on `w2/W2-188`. `git status --porcelain` was empty at the start and at the end. I re-ran the three suites (W2-11, W2-88a, W2-188) through the heavy slot only to check the CIT-P's impact claims.

## Checks

### 1. The skill (S1, S2, S4, F1, F3; DEC-1179 (1)-(6))
- **Three copies byte-equal:** `template/governance/kernel/skills/adopt/SKILL.md`, `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md` all have sha256 `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`. All three were `16fd341f…d0a0` at 5336a6fca. Only d782640de changed them.
- **Version:** `version: "1.1.0"` (was `"1.0.0"`).
- **Diff of the kernel copy:** `git diff --numstat` gives 5 added and 3 removed. With `-U0` there are exactly four hunks: `@@ -4 +4`, `@@ -58 +58`, `@@ -60,0 +61,2`, `@@ -74 +76`. These are the version, step 6, the new paragraph and the sources line. At git's default context, step 6 and the paragraph merge into one hunk, so three `@@` show; that is a display difference, not a fifth place. Steps 1 to 5, step 7, the Verify section and everything else are unchanged.
- **Step 6 against S1 and DEC-1179.** Step 6 contains every literal S1 names: `standing set`, `every week`, `same questions`, `95 %`, `counts only`, `never chooses or judges a fix`, `fresh set` with `month`, `fitted` with `replaced`, `DEC-1179`. It also says "never re-run in the same week and never re-scored" (DEC-1179 (4) R1). In more detail:
  - It reads the method as DEC-1179 (1) records it: the standard's bundle read whole by the reader, search again once.
  - It states the cadence as O3 (b): weekly, monthly once stable.
  - It states the walls and counts only, as in (2).
  - It says a fitted set is replaced, as in (3).
  - It says fixes are chosen on the tuning set and the fresh sets' misses, as in (4) R6.
  - It grants no permission. It names no `gov.memaudit` and no `standing declare` (`grep -c` gives 0 in all three copies). It never calls the reader a reranking model ("which ranks it itself"). It prints or reads no question id.
- **The paragraph after step 7 (S2):** it sits between step 7 and `## Verify clauses for adopted tickets` in all three copies. It holds `cron`, `ACT`, `operator`, `never installs` and `95 %`, and points to "the practice record's section 9". The A9 intro names that record's path, `docs/research/W2-88-memory-practice.md`, and the record now has a §9. It names no subcommand.
- **W2-88a's matcher:** I ran `check_steps` and `check_pointer` on `a9_regions` of each copy myself: one region per copy, no problems. This matches `docs/probes/DAEO-zlog/checks.md`.
- **Skill validator:** `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0 with `{"findings": []}`.

### 2. The practice record (S3, F3)
- **The three re-worded places:** §3 (line 92), §5 item 6's two practice lines (190-191) and §6 step 6 (line 221) are re-worded exactly as the CIT-P quotes them.
- **§6 still passes the matcher:** I ran `check_steps` on §6 (one section found): no problems.
- **The new §9 holds every element S3 names:**
  - what the set is;
  - the method, with E3 114 against 84 (checked against `packages/LIFT-1/E3-RESULT.md` lines 10 and 13) and E2 115 and 128 of 138 (`E2-RESULT.md:14`), A2 and the named grader;
  - the bar, ceil(0.95 n);
  - the walls, with `counts only`, and no id read "not even by the auditor";
  - `never chooses or judges a fix`;
  - staleness by count;
  - the monthly check with both 5-point rules (matches package §2.4);
  - the sentence "'A second reranker' in W2-88 S10 is a second reranking model, which stays forbidden; the reader is not one".
- **§9's below-95 text is byte-equal to the register:** the bytes from `**Below 95 %:**` to the closing `.` of the register's `  - (4) ` line under `### DEC-1179` occur exactly once in the record, as its own line `- <text>` (script check).
- **No contradiction with the rest of the record:** the remaining "measured once" and "used once" wordings refer to the confirmation (now extended) and to fresh sets. §5 item 6's first line, "a set used to choose or judge a fix is a tuning set", agrees with the standing set never choosing or judging one.

### 3. The CIT-P record (S5, DEC-105)
- **Hashes:** before `16fd341f…d0a0` (`git show 5336a6fca:…`); after `6a884cf1…9489`, which equals the kernel copy at d782640de and at HEAD, each on a line of its own. The practice record's hashes, before `f4628a01…1158` and after `76eaaeb5…d312`, are both true.
- **Counts:** skill 5/3 and practice record 15/4 (`git diff --numstat`); lines 74→76 and 280→291 (`wc -l`). All true.
- **Old and new text:** every quoted block in §2.1 and §2.2 equals the files at the base and at HEAD.
- **DEC-105's three options are present:** apply now, defer, re-baseline.
- **The impact table, claim by claim:**
  - **W2-11:** the record says `test_every_copy_carries_the_kernel_skills_body[adopt]` is not a case. **True:** the test is parametrized over `test-design`, `orchestration`, `audit` and `qa-review` only (`tests/acceptance/W2-11/test_w2_11_skills.py:124`). The version case (`:139`) and `test_w2_11_round2.py:214` exclude `adopt`. W2-11 plus W2-88a give 276 passed, 1 skipped, as stated. **The ticket's S5 and I6, which expect the body case to go red, are wrong.** No acceptance test catches the drift of `.claude/skills/adopt/SKILL.md`, but `gov.adapters.portability` does (F2).
  - **W2-88a:** the record says its cases are unchanged. **True:** `committed_after_hash` keys on `Task: DAEO-pg6i`, and the COPIES case diffs W2-88a's own base `ba27e4c0d` against the kernel copy. All green.
- **`verdict:` and `owner_approval:`:** not written yet, by design. `test_s5_the_last_verdict_is_pass_after_an_independent_review` and `test_s5_the_owner_approval_line_names_the_after_sha256` are red for that reason only.

### 4. F2
The implementer commits d782640de, 8aa930660, 857e5b3bf, 8ee9b7c36, be8b99ccb, 8c2e5d7ff and b75472d48 touch only:
- the three skill copies;
- `docs/research/W2-88-memory-practice.md`;
- `docs/probes/DAEO-zlog/checks.md`;
- `docs/changes/W2-188-CIT-P.md`.

None touches `.claude/` or `tests/`. Only the test designer's 3c5167c47 and its merge 599fa2a22 touch `tests/acceptance/W2-188/**`, and that is their role.

### 5. Trailers
All seven implementer commits carry `Task: DAEO-zlog`, `Role: product-spec` and `Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1074, DEC-1072, DEC-1071, DEC-105, CAP-33`. Every one of those ids is in the ticket's `sources:`.

### Sound
Everything else I probed was sound:
- the step 6 and §9 claims against DEC-1179 (1) to (5) and package §2.1, §2.4 and §5.1;
- the citations DEC-1101 (2) and DEC-1125 (2), which concern the automated independent sessions and the weekly-then-monthly audit;
- the source of the T1 owner quote (`MEMORY-AUDIT-P1.md:29`).

## Findings

**F1 (S5): the ticket's impact-table clause cannot be met truthfully.**
- **What happened:** S5 and I6 require the CIT-P's impact table to name W2-11's `test_every_copy_carries_the_kernel_skills_body[adopt]` as red until the copies ACT. That case does not exist, because W2-11 parametrizes the body case without `adopt`. The record correctly says so. As a result, W2-188's review case `test_s5_the_impact_table_names_w2_11s_body_case_red_and_w2_88as_cases_unchanged` is red.
- **What should happen:** S5 and I6's clause is re-baselined under DEC-105 to state the true impact, and the test designer revises the case. The record should not be made to contain "red" to pass a substring check.
- **What would reverse this finding:** a collected W2-11 case with id `…[adopt]` that goes red on this branch.
- Ordinary work: yes, because a lead closing the ticket runs `gov accept` and meets the red case.
- Consequence: other (fails closed: a red acceptance case and no lost work).

**F2 (S5): the impact table omits that adapter-portability reports the `.claude` copy's drift.**
- **What happened:** at the probed commit, `python3 -m gov.adapters.portability` gives exactly one finding: `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md`. Its check, `adapter-portability`, is G1 hard-block, and `gov check`'s structural pass runs it when a diff touches the kernel skills or `.rulesync/`. The CIT-P only says no W2-11 case catches the drift.
- **What should happen:** the impact table names this check as red from the bytes' merge until the copies ACT. The ACT should ride in the same landing so integrate is not left red.
- **What would reverse this finding:** a run of the check at this head that reports no finding.
- Ordinary work: yes, because the next session to run `gov check` on integrate after an unpaired merge meets it.
- Consequence: other (fails closed).

**F3 (S5, wording): one parenthesis in the CIT-P misreads against the base.**
- **What happened:** §3 says "the first sub-bullet of §5 item 6's practice lines is unchanged". Against the base, that line did change, from "judge" to "choose or judge", and §2.2 shows this correctly. The parenthesis means unchanged by ps-3's later re-word.
- **What should happen:** it should say "unchanged by the re-word in be8b99ccb".
- **What would reverse this finding:** the base line already reading "choose or judge".
- Ordinary work: yes, because a reader of the record may misread it.
- Consequence: other.

**F4 (S1 and S3, row): the list of what the standing set never does is shorter than the register's.**
- **What happened:** step 6 says the standing set "never chooses or judges a fix", and §9 adds "never adopts or rejects one". DEC-1179 (1) and R6 list "chooses, adopts, rejects or reverts". Nothing in the text permits any of these uses, so F3 of the ticket holds; "reverts" is just not named.
- **What should happen:** optionally, name "reverts" in §9. No change to the skill is needed.
- **What would reverse this finding:** reading "judges" as covering revert, which is a reasonable reading.
- Ordinary work: no, because no agent is told it may revert a fix on the standing set's figures.
- Consequence: other.

Classification: F1 to F3 are in scope, ordinary work yes, consequence other. F4 is ordinary work no. No finding fails open or loses work, so none blocks (DEC-1010). The accepted fixes for F1 to F3 ride along with the work the ticket does anyway: the S5 re-baseline and test revision, plus the record touch-up before the owner's approval (DEC-802).

Merge precondition, unchanged from the ticket: `waits_on` DAEO-0cd2. W2-187 is not on `w2/integrate` (head 121a44c9a), so the promotion and the copies ACT wait for it.

The lead's triage (orchestrator, W2-188's ticket lead; DEC-1010 item 1, DEC-802): F1 accepted; it is a defect of the ticket's S5 and I6, not of the text, and goes to the CTO as package P-W2-188-S5 (a DEC-105 re-baseline of S5's impact clause and the test designer's revision of the one case, DEC-1156 (7)); the record is not changed to say "red". F2 and F3 accepted; they ride along as a wording fix of the CIT-P record only (no change to the skill or the practice record after this probe). F4 is ordinary work no: a row for the Wave 3 hardening list. None blocks.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S4", "verdict": "pass", "findings": []},
 {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": []}
]}
```

verdict: PASS
