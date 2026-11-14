---
id: W2-188-CIT-P
type: change-impact-proposal
status: 'DRAFT: for the P1 package; nothing written in the tree'
date: 2026-11-14
branch: w2/W2-188
base: 'w2/integrate at filing (the adopt skill at sha256 16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0)'
head: 'to be filled by the ticket'
ticket: DAEO-NEW2 (W2-188)
author: 'a helper of the CTO (DAEO-sdxk), drafting for the product-spec session of W2-188'
review: PENDING
decisions_carried: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1074, DEC-1071, DEC-105, CAP-33]
owner_approval: 'PENDING: the owner approves the skill''s bytes by sha256 after the independent review, before the merge (CAP-33)'
state_class: EVIDENCE
---

# W2-188: change-impact proposal (CIT-P) for the adopt skill's step 6 and the practice record

This change re-words one step of a kernel skill, `template/governance/kernel/skills/adopt/SKILL.md` (A9's step 6), adds
one sentence after A9's steps, extends the governing sources line, and bumps the version, in the kernel copy and its two
`.rulesync` copies. It re-words three places of the practice record `docs/research/W2-88-memory-practice.md` and adds
one section. It is a kernel skill change, so it goes through CIT-P (CAP-33): evidence, an independent review and the
owner's approval of the bytes before the merge. DEC-1179 is the provisional number of the owner's MEMORY-AUDIT decision
(DEC-1176 is the W2-88b decision, said yes on 2026-11-14 00:33 and not yet recorded).

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | The owner's MEMORY-AUDIT (a): "G1 to G6 as you set them out, the standing hidden set judged end to end every week as we measured Gov OS, with double search and agents as second rerankers, at 95 %, counts only, with the monthly fresh-set check against fitting" | the owner, chat, 2026-11-14; DEC-1179 (provisional) | Step 6 says the verdict set is measured once and never run again |
| T2 | DEC-1176 (1): memory is proven per repository, kept by weekly maintenance and re-measuring; "until then DEC-1101 (1), DEC-1125 (2), DEC-1098 (1) and the adopt skill's step 6 stand as written" | DEC-1176 (1) | Step 6 stands until this decision |
| T3 | The reconciliation's G6: the skill's step 6 and the practice record §5 and §6 say "measured once" | `drafts/memory-scope-20261113/MEMORY-AUDIT.md` §3 G6 | Open |
| T4 | G4: each adopted repository's weekly audit runs from one cron line in A9's ACT package, never installed by adoption | MEMORY-AUDIT.md §3 G4; W2-88 S22 | The ACT package has no cron line |

## 2. What changes, old and new

### 2.1 The adopt skill (three copies, byte-equal)

**Front matter, line 4.** Old: `version: "1.0.0"`. New: `version: "1.1.0"`. (W2-88a left the version at 1.0.0 and named
the versioned promotion as following the owner's approval, `docs/changes/W2-88a-CIT-P.md:88-89`. If that promotion has
taken 1.1.0 by the time this lands, this change takes 1.2.0.)

**A9, step 6 (line 58).** Old:

> 6. Declare and measure the verdict set once. A miss stands as it is: the set is never run again. [DEC-1071 (1)-(3), DEC-1098 (1)]

New:

> 6. Declare and measure the verdict set once, at Wave 0, as the first verdict. From then on it is the repository's standing set: judged end to end every week on the same questions (monthly once the repository is stable), as Gov OS's memory is judged (the standard's bundle read whole by the reader, which ranks it itself, and search again once), against 95 %, behind the walls, with only counts leaving its run. It never chooses or judges a fix: fixes are chosen on the tuning set and on the fresh sets' misses. Each month a fresh set, measured once, checks it for fitting, and a standing set found fitted is replaced. A miss stands as it is: it is never re-run in the same week and never re-scored. [DEC-1179 (1)-(4), DEC-1071 (1), DEC-1074 (1), DEC-1098 (1)]

**After A9's step 7 (a new paragraph between line 59 and the `## Verify clauses for adopted tickets` heading).** New:

> The weekly audit runs from one cron line that A9's ACT package gives the repository's owner's operator, beside the walls; adoption never installs it. A standing set that falls below 95 % is a miss with counts only, handled as the practice record's section 9 states. [DEC-1179 (5), DEC-1101 (2), DEC-1125 (2)]

**Governing sources (line 74).** Old:

> DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1130, CAP-44, CAP-54.

New:

> DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1101, DEC-1125, DEC-1130, DEC-1179, CAP-44, CAP-54.

The parenthesis "(monthly once the repository is stable)" carries the package's open choice O3 as recommended (b),
DEC-1125 (2)'s cadence kept for the standing set. Under O3 (a) (every week, always) it is deleted, in step 6 and in §9's
first bullet.

Nothing else in the skill changes. The step names no `gov.memaudit` subcommand, so it does not depend on W2-187's
command names (W2-88a's review finding F4: a skill stating a tool not yet built).

### 2.2 The practice record `docs/research/W2-88-memory-practice.md` (not a kernel file; carried in this record for one review)

**§3, lines 91-92.** Old:

> - **Consistency is the proof:** the same product must score within 3 points on different sets. Then the measurement set is measured once, as the confirmation.

New:

> - **Consistency is the proof:** the same product must score within 3 points on different sets. Then the measurement set is measured once, as the confirmation, and kept from then on as the standing set, judged every week (§9; DEC-1179).

(The 3 points here predate DEC-1074 (4)'s 5 points; it is left as written, since §5 item 6 and §6 step 5 carry the 5.)

**§5 item 6, lines 190-191.** Old:

> - a set used to judge a fix is a tuning set from then on;
> - only a fresh blind set gives a verdict, used once;

New:

> - a set used to choose or judge a fix is a tuning set from then on;
> - a verdict comes only from a set nothing was tuned on: a fresh blind set, used once, or the standing set behind its walls, judged every week with counts only, never used to choose or judge a fix, and checked each month against a fresh set (§9; DEC-1179);

**§6 step 6, line 221.** Old:

> 6. Declare and measure the verdict set once.

New:

> 6. Declare and measure the verdict set once, at Wave 0. From then on it is the standing set: judged end to end every week against 95 %, counts only, never used to choose or judge a fix, and checked each month against a fresh set (§9).

**A new §9, at the end of the record.** New:

> ## 9. The standing set (DEC-1179)
> - **What it is:** the verdict set of Wave 0 (about 80 questions, written by the independent writer and checked by the independent checker under the rubric), kept after its first measure and judged end to end every week on the same questions (monthly once the repository is stable, back to weekly at once on a miss, a retrieval change or churn of 10 % or more: DEC-1125 (2), W2-172 S5).
> - **How it is judged, the same way as Gov OS's memory (FRESH-80-1, DEC-1097 (1), DEC-1098 (1)):** the store at the audit commit, served with the standard; each question's first bundle from the retrieval measure; the reader (pinned prompt and model, no tools) reads the whole ranked bundle and chooses what answers, so it ranks the bundle a second time after the 0.6B reranker (E3: the ranked, widened bundle read whole gave 114 of 138 in one call, against 84 for the top 5); it may search again once with its own words (A2: E2 gave 115 at one search and 128 at two, of 138; a second search never lost a right answer); graded by a named grader with a second grader's agreement; the citation checked by the measure's matcher. The figure is right end to end at A2. "A second reranker" in W2-88 S10 is a second reranking model, which stays forbidden; the reader is not one.
> - **The bar:** at least ceil(0.95 n) right end to end; wrong claims reported beside it.
> - **The walls:** the set and its run folder are hidden from every measured role; only counts leave the run: right, wrong, not found, the outcome and rank buckets, the questions dropped by the anchor check. No id, question, gold or answer is printed, logged or read, not even by the auditor.
> - **Fixes:** chosen only on the tuning set and on the fresh sets' misses, structural only (DEC-1071 (1)), brought to the owner; the standing set never chooses, adopts or rejects a fix.
> - **Staleness:** a question whose gold no longer resolves at the audit commit is dropped from that week's count and never re-labelled.
> - **The monthly check against fitting:** each month a fresh set, measured once, is compared with the mean of the standing set's last four weekly figures. Standing 5 points or more above fresh: the standing set is declared fitted, joins the pool as a diagnostic set, and the writer writes its replacement. Fresh 5 points or more above standing: the checker's staleness pass on the standing set.
> - **Below 95 %:** the rule the owner decided in DEC-1179 (4), copied here word for word when it is recorded.

## 3. sha256 of every file, before and after

Before is at the filing base. After is filled by the ticket at its head.

| File | Before (sha256) | After (sha256) | Lines before |
|---|---|---|---|
| `template/governance/kernel/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | to be filled | 74 |
| `.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | equal to the kernel copy | 74 |
| `template/.rulesync/skills/adopt/SKILL.md` | `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0` | equal to the kernel copy | 74 |
| `docs/research/W2-88-memory-practice.md` | at the base | to be filled | 280 |

Lines changed in the skill (expected): 3 removed (version, step 6, governing sources), 5 added (version, step 6, the
blank line and the new paragraph, governing sources).

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
| Generated copies | `.rulesync/skills/adopt/` and `template/.rulesync/skills/adopt/` byte-equal to the kernel copy. `.claude/skills/adopt/SKILL.md` (sha256 `77faaa13...`, front matter without a version) comes from the copies ACT; until then its body differs |
| W2-11's cases | `test_every_copy_carries_the_kernel_skills_body[adopt]` (`tests/acceptance/W2-11/test_w2_11_skills.py:125`) is red from the merge until the copies ACT regenerates the `.claude` copy, as W2-98's was. W2-11's version case (`:139-140`) and its round-2 twin (`test_w2_11_round2.py:214`) exclude `adopt`, so the bump does not touch them |
| W2-88a's cases | Step 6's matcher (`tests/acceptance/W2-88a/w2_88a_support.py:199-201`: "declar...", "measur...", "verdict set", "once") passes on the new text, the seven steps in order (checked on this draft's text with `check_steps`, no problems). The COPIES case (`test_w2_88a_citp_and_copies.py`) diffs the base against the current kernel copy, so it passes while the three copies are byte-equal. The CIT-P cases read W2-88a's own record and fixed commits; unchanged. No W2-88a test is revised |
| W2-188's own acceptance | `tests/acceptance/W2-188/`, written by an independent test designer from the KPI lines |
| Decisions | None changed by this record; it carries DEC-1179, which changes DEC-1101 (1), DEC-1125 (2), DEC-1098 (1), DEC-1097 (1)(d) as carried forward, DEC-1074 (1) as the practice reads it, and DEC-1126 (5) (the P1 package's §5.4) |

## 6. Independent review and approval

Review: PENDING. One fresh read-only reviewer (independent-auditor, Opus) reads the three copies, the practice record,
this record and DEC-1179 as recorded, and states `verdict: PASS` or `verdict: FAIL` with findings; at most two rounds
(DEC-1131).

The owner's approval of the skill's bytes (sha256 after, §3) is written here before the merge, in `owner_approval:` of
the front matter (CAP-33).
