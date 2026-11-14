---
id: W2-188-CIT-P
type: change-impact-proposal
status: 'PROPOSED: the bytes are written; the independent review and the owner''s approval of the skill''s bytes come before the merge (CAP-33)'
date: 2026-11-14
branch: w2/W2-188
base: '5336a6fca (the adopt skill at sha256 16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0)'
head: 'd782640dee6b0ff547ea7254498c482f416a4e69 (the commit holding the skill''s final bytes, sha256 6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489)'
ticket: DAEO-zlog (W2-188)
author: product-spec session of W2-188, from the CTO's draft (DAEO-sdxk)
review: 'PASS (round 1, docs/probes/DAEO-zlog/PR-DAEO-zlog.md)'
decisions_carried: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1074, DEC-1072, DEC-1071, DEC-105, CAP-33]
owner_approval: 'pending'
state_class: EVIDENCE
---

# W2-188: change-impact proposal (CIT-P) for the adopt skill's step 6 and the practice record

This change re-words one step of a kernel skill, `template/governance/kernel/skills/adopt/SKILL.md` (A9's step 6), adds one paragraph after A9's steps,
extends the governing sources line, and bumps the version, in the kernel copy and its two `.rulesync` copies. It
re-words three places of the practice record `docs/research/W2-88-memory-practice.md` (four lines of text) and adds one section. It is a kernel skill
change, so it goes through CIT-P (CAP-33): evidence, an independent review and the owner's approval of the bytes before
the merge. DEC-1179 is the owner's MEMORY-AUDIT decision, recorded and ACCEPTED on 2026-11-14; DEC-1176 (the W2-88b
decision) is recorded.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | The owner's MEMORY-AUDIT (a): "G1 to G6 as you set them out, the standing hidden set judged end to end every week as we measured Gov OS, with double search and agents as second rerankers, at 95 %, counts only, with the monthly fresh-set check against fitting" | the owner, chat, 2026-11-14; DEC-1179 | Step 6 says the verdict set is measured once and never run again |
| T2 | DEC-1176 (1): memory is proven per repository, kept by weekly maintenance and re-measuring; "until then DEC-1101 (1), DEC-1125 (2), DEC-1098 (1) and the adopt skill's step 6 stand as written" | DEC-1176 (1), spent by DEC-1179 | Step 6 stood until DEC-1179 |
| T3 | The reconciliation's G6: the skill's step 6 and the practice record's §3, §5 and §6 say "measured once" | MEMORY-AUDIT.md §3 G6 | Open |
| T4 | G4: each adopted repository's weekly audit runs from one cron line in A9's ACT package, never installed by adoption | MEMORY-AUDIT.md §3 G4; DEC-1179 (5); W2-88 S22 | The ACT package had no cron line |

## 2. What changes, old and new

All text below is quoted from the files as finally written (the old text from `5336a6fca`).

### 2.1 The adopt skill (three copies, byte-equal)

**Front matter, line 4.** Old: `version: "1.0.0"`. New: `version: "1.1.0"`. (W2-88a is closed and left the kernel copy at 1.0.0; the
next minor is 1.1.0.)

**A9, step 6 (line 58).** Old:

> 6. Declare and measure the verdict set once. A miss stands as it is: the set is never run again. [DEC-1071 (1)-(3), DEC-1098 (1)]

New:

> 6. Declare and measure the verdict set once, at Wave 0, as the first verdict. From then on it is the repository's standing set: judged end to end every week on the same questions (monthly once the repository is stable), as Gov OS's memory is judged (the standard's bundle read whole by the reader, which ranks it itself, and search again once), against 95 %, behind the walls, counts only: only counts leave its run. It never chooses or judges a fix: fixes are chosen on the tuning set and on the fresh sets' misses. Each month a fresh set, measured once, checks it for fitting, and a standing set found fitted is replaced. A miss stands as it is: it is never re-run in the same week and never re-scored. [DEC-1179 (1)-(4), DEC-1071 (1), DEC-1074 (1), DEC-1098 (1)]

**After A9's step 7 (a new paragraph, one blank line before it, before the `## Verify clauses for adopted tickets`
heading; line 61).** New:

> The weekly audit runs from one cron line that A9's ACT package gives the repository's owner's operator, beside the walls; adoption never installs it. A standing set that falls below 95 % is a miss with counts only, handled as the practice record's section 9 states. [DEC-1179 (4), (5), DEC-1101 (2), DEC-1125 (2)]

**Governing sources (line 74, now line 76).** Old:

> DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1130, CAP-44, CAP-54.

New:

> DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1101, DEC-1125, DEC-1130, DEC-1179, CAP-44, CAP-54.

The parenthesis "(monthly once the repository is stable)" carries the package's open choice O3 as the owner decided it,
(b) (DEC-1179 (5)): weekly while a repository is actively worked on, monthly once stable, back to weekly at once on a
miss, a retrieval change or churn of 10 % or more. The step names no `gov.memaudit` subcommand, so it does not depend on
W2-187's command names (W2-88a's review finding F4). Nothing else in the skill changes: `git diff --numstat 5336a6fca`
gives 5 added and 3 removed lines in four hunks (`@@ -4 +4`, `@@ -58 +58`, `@@ -60,0 +61,2`,
`@@ -74 +76`).

### 2.2 The practice record `docs/research/W2-88-memory-practice.md` (not a kernel file; carried in this record for one review)

**§3, the bullet at lines 91-92.** Old:

> - **Consistency is the proof:** the same product must score within 3 points on different sets. Then the measurement
>   set is measured once, as the confirmation.

New:

> - **Consistency is the proof:** the same product must score within 3 points on different sets. Then the measurement
>   set is measured once, as the confirmation, and kept from then on as the standing set, judged every week (§9; DEC-1179).

(The "3 points" here predate DEC-1074 (4)'s 5 points; it is left as written, since §5 item 6 and §6 step 5 carry the 5.)

**§5 item 6, the two sub-bullets of "The practice", lines 190-191.** Old:

>      - a set used to judge a fix is a tuning set from then on;
>      - only a fresh blind set gives a verdict, used once;

New:

>      - a set used to choose or judge a fix is a tuning set from then on;
>      - a verdict comes only from a set nothing was tuned on: a fresh blind set, used once, or the standing set, which sits behind its walls, is judged every week with counts only, never chooses or judges a fix, and is checked each month against a fresh set (§9; DEC-1179);

**§6 step 6, line 221.** Old:

> 6. Declare and measure the verdict set once.

New:

> 6. Declare and measure the verdict set once, at Wave 0. From then on it is the standing set: judged end to end every week against 95 %, counts only, never used to choose or judge a fix, and checked each month against a fresh set (§9).

**A new §9, at the end of the record (after §8).** New:

> ## 9. The standing set (DEC-1179)
> - **What it is:** the verdict set of Wave 0 (about 80 questions, written by the independent writer and checked by the independent checker under the rubric), kept after its first measure and judged end to end every week on the same questions (monthly once the repository is stable, back to weekly at once on a miss, a retrieval change or churn of 10 % or more: DEC-1125 (2), W2-172 S5).
> - **How it is judged, the same way as Gov OS's memory (FRESH-80-1, DEC-1097 (1), DEC-1098 (1)):** the store at the audit commit, served with the standard; each question's first bundle from the retrieval measure; the reader (pinned prompt and model, no tools) ranks the whole bundle itself, in its one reading, and chooses what answers (E3: the ranked, widened bundle read whole gave 114 of 138 in one call, against 84 for the top 5); it may search again once with its own words (A2: E2 gave 115 at one search and 128 at two, of 138; a second search never lost a right answer); graded by a named grader with a second grader's agreement; the citation checked by the measure's matcher. The figure is right end to end at A2. The 0.6B reranker is the only reranking model. "A second reranker" in W2-88 S10 is a second reranking model, which stays forbidden; the reader is not one.
> - **The bar:** at least ceil(0.95 n) right end to end; wrong claims reported beside it.
> - **The walls:** the set and its run folder are hidden from every measured role, counts only: only counts leave the run: right, wrong, not found, the outcome and rank buckets, the questions dropped by the anchor check. No id, question, gold or answer is printed, logged or read, not even by the auditor.
> - **Fixes:** chosen only on the tuning set and on the fresh sets' misses, structural only (DEC-1071 (1)), brought to the owner. The standing set never chooses or judges a fix, and never adopts or rejects one.
> - **Staleness:** a question whose gold no longer resolves at the audit commit is dropped from that week's count and never re-labelled.
> - **The monthly check against fitting:** each month a fresh set, measured once, is compared with the mean of the standing set's last four weekly figures. Standing 5 points or more above fresh: the standing set is declared fitted, joins the pool as a diagnostic set, and the writer writes its replacement. Fresh 5 points or more above standing: the checker's staleness pass on the standing set.
> - **The rule below 95 % is the owner's, DEC-1179 (4); the next line is its text word for word, as recorded.**
> - **Below 95 %:** the package's §5.1 rules R1 to R9 (a miss recorded by counts only, never re-run or re-scored; a fault is not a miss; a P1 to the repository's owner in the next digest; the maintenance pass at once; the cadence back to weekly; fixes chosen only on the tuning set and the fresh sets' misses; the standing set re-judged at the next scheduled run only; memory repair on two consecutive misses or one 5 points below; R9 with the check against fitting).

The last bullet is DEC-1179 (4) copied by script from the register's line `  - (4) ...`, from `**Below 95 %:**` to its
closing `.` (463 characters, 464 bytes: the `§` is UTF-8); the check records its byte-for-byte equality
(`docs/probes/DAEO-zlog/checks.md`).

## 3. sha256 of every file, before and after

Before is at the base `5336a6fca`. After is the committed bytes (the skill at `d782640dee6b0ff547ea7254498c482f416a4e69`).

The kernel skill's sha256 before: `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0`

The kernel skill's sha256 after: `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`

The practice record's sha256 after: `76eaaeb5487739643cef6d79d8f736331ee5396756b1f123c5236c9bcb60d312` (the first sub-bullet of §5 item 6's practice lines is unchanged by the re-word in be8b99ccb; the standing-set line was re-worded once, after the independent test designer's acceptance run).

| File | Before (sha256) | After (sha256) | Lines before / after | Added / removed (`git diff --numstat`) |
|---|---|---|---|---|
| `template/governance/kernel/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` | 74 / 76 | 5 / 3 |
| `.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` (equal to the kernel copy) | 74 / 76 | 5 / 3 |
| `template/.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` (equal to the kernel copy) | 74 / 76 | 5 / 3 |
| `docs/research/W2-88-memory-practice.md` | `f4628a01434b0fc1638b8aa8a2fc804c48cef5d0150abd4376bb751459f61158` | `76eaaeb5487739643cef6d79d8f736331ee5396756b1f123c5236c9bcb60d312` | 280 / 291 | 15 / 4 |

The skill's lines changed: 3 removed (version, step 6, governing sources) and 5 added (version, step 6, the blank line
and the new paragraph, governing sources).

## 4. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended) | Merge the re-worded step, the new paragraph and the practice record; the copies ACT regenerates `.claude/skills/adopt/SKILL.md` after W2-187 merges | About 60 lines of text; one independent review round; the owner's bytes; one copies ACT, ridden with the next CLAUDE-COPIES ACT |
| Defer | Keep step 6 as written until Wave 3 | The skill tells every adopted repository (EXAMIN's copy first, at W2-27) the opposite of DEC-1179: its verdict set measured once and never run again. W2-47's exit audit finds the contradiction |
| Re-baseline | Re-open W2-88a and rewrite A9's section as a whole | Re-opens a closed ticket and its 4 acceptance files for one step; no gain over apply now |

## 5. Impact

| Area | Impact |
|---|---|
| Kernel skills | One skill: one step re-worded, one paragraph added, the sources line and the version. No other skill, role file, hook or guard rule changes |
| Generated copies | `.rulesync/skills/adopt/` and `template/.rulesync/skills/adopt/` byte-equal to the kernel copy. `.claude/skills/adopt/SKILL.md` (front matter without a version) comes from the copies ACT after the owner's approval; this ticket does not write it, so until then its body differs. The adapter-portability check (`python3 -m gov.adapters.portability`, a G1 hard-block check that `gov check`'s structural pass runs when a diff touches the kernel skills or `.rulesync/`) reports one finding, `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md` ("is not what rulesync generates from its sources"), from the merge of these bytes until the copies ACT regenerates that copy. Run on `b75472d48` it gives exactly that one finding (`compared`: `rulesync_version` true, 78 kernel files, 93 generated files; exit 1). So the copies ACT should ride in the same landing as this merge |
| W2-11's cases | `test_every_copy_carries_the_kernel_skills_body[adopt]` (`tests/acceptance/W2-11/test_w2_11_skills.py`) is not a case: the test is parametrized over `test-design`, `orchestration`, `audit` and `qa-review` only (line 124), so `adopt` is left out. W2-11 therefore stays green after the merge (`tests/acceptance/W2-11` and `tests/acceptance/W2-88a`: 276 passed, 1 skipped on `599fa2a22`), and the `.claude/skills/adopt/SKILL.md` copy's drift from the kernel body, from the merge until the copies ACT regenerates it, is caught by no W2-11 case. W2-11's version case and its round-2 twin (`test_w2_11_round2.py`) exclude `adopt`, so the bump does not touch them |
| W2-88a's cases | Step 6's matcher (`tests/acceptance/W2-88a/w2_88a_support.py`: "declar...", "measur...", "verdict set", "once") passes on the new text, the seven steps in order: `check_steps` was run on A9's region of each of the three copies and on the practice record's §6, and `check_pointer` on A9's region, all with no problem (`docs/probes/DAEO-zlog/checks.md`). The COPIES case diffs the base against the current kernel copy, so it passes while the three copies are byte-equal. The CIT-P cases read W2-88a's own record and fixed commits; unchanged. No W2-88a test is revised |
| Skill check | `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0 on the new text |
| W2-188's own acceptance | `tests/acceptance/W2-188/`, written by an independent test designer from the KPI lines |
| Decisions | None changed by this record; it carries DEC-1179, which changes DEC-1101 (1), DEC-1125 (2), DEC-1098 (1), DEC-1126 (5), DEC-1074 (1) as the practice reads it, and DEC-1097 (1)(d) (a 95 % bar added beside it) |

## 6. Independent review and approval

Review: round 1, by a fresh read-only independent auditor (au-1, session `2bd2339c-ba97-4e67-bf75-69f84af5a970`,
Opus, high), on the probed commit `b75472d4825cece64936451f21b259787b5ecf97`; its record is
`docs/probes/DAEO-zlog/PR-DAEO-zlog.md`. It gave four findings:

- **F1:** the ticket's S5/I6 premise; it goes to the CTO.
- **F2:** the adapter-portability finding on `.claude/skills/adopt/SKILL.md` until the copies ACT; fixed in this record
  (§5, "Generated copies").
- **F3:** the "unchanged" parenthesis of §3 misread against the base; fixed in this record (§3).
- **F4:** ordinary work no; a Wave 3 row.

None blocks (DEC-1010).

verdict: PASS

The owner's approval of the skill's bytes (sha256 after, §3) is written in `owner_approval:` of the front matter by the
CTO after the owner's yes, before the merge (CAP-33). This record holds none yet.
