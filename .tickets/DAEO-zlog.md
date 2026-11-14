---
id: DAEO-zlog
wbs_id: W2-188
external-ref: W2-188
title: "The adopt skill's step 6 and the practice record say the verdict set becomes the standing set, judged every week at 95 %, counts only, checked monthly against a fresh set; A9's weekly cron line named (MEMORY-AUDIT G6 and G4's text; CIT-P)"
type: task
class: spec
role: product-spec
profile: STANDARD
status: in_progress
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-14
deps: [DAEO-pg6i]
allowed_paths:
- template/governance/kernel/skills/adopt/SKILL.md
- .rulesync/skills/adopt/SKILL.md
- template/.rulesync/skills/adopt/SKILL.md
- docs/research/W2-88-memory-practice.md
- docs/changes/W2-188-CIT-P.md
- docs/probes/DAEO-zlog/**
reads:
- .gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md
- governance/project/orchestration/packages/MEMORY-AUDIT-P1.md
- .gov-runtime/scratch/orchestrator/drafts/memory-scope-20261113/MEMORY-AUDIT.md
- docs/changes/W2-88a-CIT-P.md
- docs/changes/W2-98-CIT-P.md
- tests/acceptance/W2-88a/**
- tests/acceptance/W2-11/**
- governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md
- governance/project/orchestration/packages/LIFT-1/E3-RESULT.md
needs:
- template/governance/kernel/skills/adopt/SKILL.md
waits_on:
- ref: DAEO-0cd2
  reason: 'the promotion and the copies ACT follow W2-187''s merge, so the generated copy never states a mode the product lacks; the text itself names no subcommand and is written in parallel'
est_loc: 60
kpis:
  success:
  - 'S1 A9''s step 6 in the adopt skill says, in its own words: the verdict set is declared and measured once at Wave 0 as the first verdict; from then on it is the repository''s standing set, judged end to end every week on the same questions (monthly once the repository is stable, under the package''s O3 (b)) as Gov OS''s memory is judged (the standard''s bundle read whole by the reader, search again once), against 95 %, behind the walls, with only counts leaving its run; it never chooses or judges a fix (fixes chosen on the tuning set and the fresh sets'' misses); a fresh set each month checks it for fitting and a fitted set is replaced; a miss is never re-run in the same week and never re-scored; it cites DEC-1179 [DEC-1179 (1)-(4), DEC-1176 (1), DEC-1098 (1)] Verify: a string test on step 6''s stretch of the three copies finds each of these statements (standing set, every week, same questions, 95 %, counts only, never chooses a fix, fresh set monthly, fitted replaced, DEC-1179); W2-88a''s step matcher (`check_steps`) returns no problem on A9''s section'
  - 'S2 After A9''s seven steps, one paragraph says the weekly audit runs from one cron line that A9''s ACT package gives the repository''s owner''s operator beside the walls, never installed by adoption, and that a fall below 95 % is handled as the practice record''s section 9 states [DEC-1179 (4), (5), DEC-1101 (2)] Verify: a string test finds the paragraph between step 7 and the `## Verify clauses for adopted tickets` heading in all three copies, with "cron", "ACT", "operator", "never installs" (or "never installed") and "95 %"'
  - 'S3 The practice record states the standing set: §3''s confirmation line, §5 item 6''s practice lines and §6 step 6 re-worded as the CIT-P quotes, and a new §9 "The standing set (DEC-1179)" with what it is, the method (the reader ranking the whole bundle and searching again once, A2, with the E2 and E3 figures), the bar, the walls (counts only, no id read by anyone), fixes never chosen on it, staleness by count, the monthly check against fitting with its two 5-point rules, and DEC-1179 (4)''s rule below 95 % word for word [DEC-1179, DEC-1074 (1), DEC-1074 (4), DEC-1072 (2)] Verify: a string test on each named place of `docs/research/W2-88-memory-practice.md`; §6 still passes W2-88a''s step matcher; §9''s below-95 text equals DEC-1179 (4)''s as recorded'
  - 'S4 The three copies of the skill are byte-equal; the version goes from "1.0.0" to "1.1.0" in all three (the next minor if W2-88a''s promotion has taken 1.1.0 by then); nothing else in the skill changes but step 6, the new paragraph, the governing sources line (adding DEC-1101, DEC-1125 and DEC-1179) and the version [CAP-33, DEC-832 item 2, DEC-981] Verify: sha256 of the three copies equal; `git diff` of the kernel copy against the base touches only those four places; `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0'
  - 'S5 The CIT-P record `docs/changes/W2-188-CIT-P.md` gives the skill''s sha256 before and after, the lines added and removed, the old and new text of each changed place, the impact table (W2-11''s body case red until the copies ACT; W2-88a''s cases unchanged), the independent review''s verdict and the owner''s approval line of the bytes before the merge [CAP-33, DEC-105] Verify: the record holds both hashes (the after equal to the kernel copy at the ticket''s last commit), the counts, a `verdict: PASS` as the last verdict and an `owner_approval:` line naming the sha256'
  failure:
  - 'F1 Any other step, section or rule of the adopt skill changes, or the skill grants a permission, names a `gov.memaudit` subcommand or states a mode the product lacks. Verify: the S4 diff; a grep of the three copies for `gov.memaudit` and `standing declare` finds nothing'
  - 'F2 The ticket writes `.claude/skills/adopt/SKILL.md` or any test under `tests/acceptance/`. Verify: the close''s diff names neither; the copies ACT regenerates the `.claude` copy after the owner''s approval'
  - 'F3 The text says the standing set may be used to choose, judge, adopt or reject a fix, prints or reads a question id, or calls the reader a second reranking model. Verify: a string test on step 6 and §9 for "never chooses or judges a fix" and "counts only"; §9 says W2-88 S10''s second reranker stays forbidden'
non_goals:
- 'no code: the standing mode, the bar, the per-repository state, the maintenance pass and the cron line in the ACT package''s text are W2-187'
- 'no `.claude/` copy (the copies ACT) and no acceptance test (the test designer)'
- 'no change to A9''s other six steps, to the Verify section or to W2-88''s closed ticket (its lines are re-baselined by the CTO''s record edit under DEC-1179 (7))'
- 'no change to W2-88 S10''s standard or the forbidden second reranking model'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1074, DEC-1071, DEC-1072, DEC-105, DEC-974, CAP-33, DAEO-pg6i, DAEO-2bdu]
acceptance_tests: {path: tests/acceptance/W2-188/}
---

# W2-188 The adopt skill's step 6 and the practice record: the standing set

**Problem.** The adopt skill's A9 step 6 (`template/governance/kernel/skills/adopt/SKILL.md:58`, and the two `.rulesync`
copies) says: "Declare and measure the verdict set once. A miss stands as it is: the set is never run again." The
practice record says "measured once" in three places (`docs/research/W2-88-memory-practice.md:91-92, 190-191, 221`).
DEC-1176 (1) kept them standing until the weekly re-measure was decided. The owner decided it on 2026-11-14 (DEC-1179,
provisional): the verdict set stays as each repository's standing set, judged every week at 95 %, counts only, checked
monthly against a fresh set.

**Approach.** Re-word step 6 and add one paragraph after the seven steps, as `drafts/memory-audit-p1/W2-188-CIT-P.md`
§2.1 quotes. The proposed step 6 keeps "declare", "measure", "the verdict set" and "once", so W2-88a's matcher passes
unrevised; this was checked on the draft's text. Re-word the practice record's three places and add its §9 (§2.2). Bump
the version and write the CIT-P. The skill names no subcommand, so the text does not wait for W2-187. Its promotion and
the `.claude` copies ACT come after W2-187 merges (W2-88a's finding F4).

**Rabbit holes.**
- Do not restate the method's figures in the skill: they belong in the practice record.
- Do not touch step 5's 5 points or §3's 3 points (a known older wording, left as is).
- Do not write the below-95 rule before DEC-1179 (4) is recorded. Copy it word for word.

**Filed 2026-11-14 on the owner's decision (DEC-1179, MEMORY-AUDIT-P1), by the CIT-P route (W2-188's CIT-P draft: `.gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md`).** The kernel bytes need the owner's approval of the CIT-P before the merge (DEC-1166 (4)); the `.claude` copy follows by a copies ACT.

## Interface (the CTO at claim, DEC-1179 (8), DEC-1157 (3) and (12); listed for the owner's reading)

- **I1, the skill's three copies and the four places (S1, S2, S4, F1).** `template/governance/kernel/skills/adopt/SKILL.md`
  is edited. `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md` are then byte copies of it,
  all three at base sha256 `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0`, 74 lines. Exactly four
  places change:
  - **Line 4:** `version: "1.0.0"` becomes `version: "1.1.0"` (W2-88a is closed and the kernel copy still reads 1.0.0
    at `10c0ca52b`). If the version line reads anything other than 1.0.0 at claim, use the next minor after it (S4).
  - **Line 58, step 6:** replaced in place by one numbered line, `6. Declare ...`.
  - **A new paragraph** after line 59 (step 7), with one blank line before it, before line 61's
    `## Verify clauses for adopted tickets`.
  - **Line 74, the sources line:** adds DEC-1101, DEC-1125 and DEC-1179 in numeric order.

  `git diff <base> -- template/governance/kernel/skills/adopt/SKILL.md` shows those four hunks and no other.
  `.claude/skills/adopt/SKILL.md` is not touched (the copies ACT).

- **I2, step 6's text constraints (S1, F1, F3; W2-88a's `check_steps` at `tests/acceptance/W2-88a/w2_88a_support.py:207`).**
  - **The step-6 anchor:** step 6 opens with `Declare`, and no word starting `declar` stands earlier in steps 1 to 5.
  - **The step-6 checks:** it says `measure`, `the verdict set` and `once`.
  - **The step-7 anchor** (`record\w*` then, within one sentence, `every|each|all` then `method`) must not occur in step 6.
  - **No subcommand:** it names no `gov.memaudit` and no `standing declare`.
  - **No second reranking model:** it never calls the reader one.
  - **The literal phrases step 6 holds:** `standing set`, `every week`, `same questions`, `95 %`, `counts only`,
    `never chooses or judges a fix`, `fresh set` with `month`, `fitted` with `replaced`, and `DEC-1179`. S1's
    statement that a miss is never re-run in the same week and never re-scored is kept in words as well, though the
    S1 Verify list does not test it.

- **I3, the paragraph after step 7 (S2).** One paragraph that holds the literal words `cron`, `ACT`, `operator`,
  `never installs` (or `never installed`) and `95 %`, and points to the practice record's section 9. It names no
  subcommand, and the step-7 anchor rule does not apply after step 7.

- **I4, the practice record `docs/research/W2-88-memory-practice.md` (280 lines at the base; S3, F3).**
  - **The places re-worded as the CIT-P quotes:** §3's bullet at lines 91-92; §5 item 6's two sub-bullets at lines
    190-191; §6 step 6 at line 221.
  - **§6 still passes `check_steps`:** the same anchor rules as I2, and step 6 keeps `Declare`, `measure`,
    `the verdict set` and `once`.
  - **A new `## 9. The standing set (DEC-1179)`,** appended after §8 at the end of the file. It holds:
    - what the set is;
    - the method: the reader ranking the whole bundle and searching again once, A2, with E2's 115 and 128 of 138 and
      E3's 114 against 84;
    - the bar, ceil(0.95 n);
    - the walls, with the literal `counts only`;
    - the literal `never chooses or judges a fix`;
    - the sentence that W2-88 S10's second reranking model stays forbidden;
    - staleness by count;
    - the monthly check with its two 5-point rules;
    - DEC-1179 (4)'s text as recorded, word for word: the bytes of the register's DEC-1179 line `  - (4) ...` after
      `(4) `, from `**Below 95 %:**` to its closing `.`.

- **I5, the checks the session runs and records under `docs/probes/DAEO-zlog/` (S1, S3, S4).**
  - `check_steps` on A9's region of each copy (`a9_regions`) and on the practice record's §6: no problems;
  - `check_pointer` on A9's region: no problems;
  - `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt`: exit 0;
  - `sha256sum` of the three copies: equal;
  - `grep -c 'gov.memaudit\|standing declare'` of the three copies: 0;
  - the I1 `git diff --stat` and hunk count.

  It runs no test suite.

- **I6, the CIT-P record `docs/changes/W2-188-CIT-P.md` (S5).** Built from the draft
  `.gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md`. It holds:
  - the skill's sha256 before (`16fd341f...`) and after; the after equals the kernel copy at the ticket's last commit, so
    the record is the last file changed;
  - the lines added and removed;
  - the old and new text of each changed place;
  - the impact table: W2-11's body case `test_every_copy_carries_the_kernel_skills_body[adopt]` red until the copies ACT;
    W2-88a's cases unchanged;
  - the reviewer's `verdict: PASS` as the last verdict line;
  - in the front matter, `owner_approval: '<sha256 after> approved by the owner, <date>, <reference>'`, written before
    the merge.

- **How the code-bound clauses read:**
  - **S1:** "never chooses a fix" reads as F3's literal `never chooses or judges a fix`. "Fresh set monthly" reads as
    `fresh set` and `month` within step 6. "Fitted replaced" reads as `fitted` and `replaced` within step 6. "Counts only"
    is the literal phrase.
  - **S4:** "the next minor" is 1.1.0. "Those four places" are I1's four hunks.
  - **S3:** "equals DEC-1179 (4)'s as recorded" is I4's verbatim substring.
  - **F2:** the close's diff names no `.claude/` path and no `tests/` path.

- **Gaps:** none inside `allowed_paths`. The draft's text needs four changes to meet these clauses (see discoveries):
  - its step 6 says "with only counts leaving its run" and lacks the literal `counts only`;
  - its §9 lacks the literal `counts only` and `never chooses or judges a fix`;
  - its §9 last bullet must be replaced by DEC-1179 (4)'s recorded text, recorded at `976e53791`.
