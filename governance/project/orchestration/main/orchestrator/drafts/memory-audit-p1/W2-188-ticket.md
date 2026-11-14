---
id: DAEO-NEW2
wbs_id: W2-188
external-ref: W2-188
title: "The adopt skill's step 6 and the practice record say the verdict set becomes the standing set, judged every week at 95 %, counts only, checked monthly against a fresh set; A9's weekly cron line named (MEMORY-AUDIT G6 and G4's text; CIT-P)"
type: task
class: spec
role: product-spec
profile: STANDARD
status: open
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
- docs/probes/DAEO-NEW2/**
reads:
- .gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md
- .gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/PACKAGE.md
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
- ref: DAEO-NEW1
  reason: 'the promotion and the copies ACT follow W2-187''s merge, so the generated copy never states a mode the product lacks; the text itself names no subcommand and is written in parallel'
est_loc: 60
kpis:
  success:
  - 'S1 A9''s step 6 in the adopt skill says, in its own words: the verdict set is declared and measured once at Wave 0 as the first verdict; from then on it is the repository''s standing set, judged end to end every week on the same questions (monthly once the repository is stable, under the package''s O3 (b)) as Gov OS''s memory is judged (the standard''s bundle read whole by the reader, search again once), against 95 %, behind the walls, with only counts leaving its run; it never chooses or judges a fix (fixes chosen on the tuning set and the fresh sets'' misses); a fresh set each month checks it for fitting and a fitted set is replaced; a miss is never re-run in the same week and never re-scored; it cites DEC-1177 [DEC-1177 (1)-(4), DEC-1176 (1), DEC-1098 (1)] Verify: a string test on step 6''s stretch of the three copies finds each of these statements (standing set, every week, same questions, 95 %, counts only, never chooses a fix, fresh set monthly, fitted replaced, DEC-1177); W2-88a''s step matcher (`check_steps`) returns no problem on A9''s section'
  - 'S2 After A9''s seven steps, one paragraph says the weekly audit runs from one cron line that A9''s ACT package gives the repository''s owner''s operator beside the walls, never installed by adoption, and that a fall below 95 % is handled as the practice record''s section 9 states [DEC-1177 (4), (5), DEC-1101 (2)] Verify: a string test finds the paragraph between step 7 and the `## Verify clauses for adopted tickets` heading in all three copies, with "cron", "ACT", "operator", "never installs" (or "never installed") and "95 %"'
  - 'S3 The practice record states the standing set: §3''s confirmation line, §5 item 6''s practice lines and §6 step 6 re-worded as the CIT-P quotes, and a new §9 "The standing set (DEC-1177)" with what it is, the method (the reader ranking the whole bundle and searching again once, A2, with the E2 and E3 figures), the bar, the walls (counts only, no id read by anyone), fixes never chosen on it, staleness by count, the monthly check against fitting with its two 5-point rules, and DEC-1177 (4)''s rule below 95 % word for word [DEC-1177, DEC-1074 (1), DEC-1074 (4), DEC-1072 (2)] Verify: a string test on each named place of `docs/research/W2-88-memory-practice.md`; §6 still passes W2-88a''s step matcher; §9''s below-95 text equals DEC-1177 (4)''s as recorded'
  - 'S4 The three copies of the skill are byte-equal; the version goes from "1.0.0" to "1.1.0" in all three (the next minor if W2-88a''s promotion has taken 1.1.0 by then); nothing else in the skill changes but step 6, the new paragraph, the governing sources line (adding DEC-1101, DEC-1125 and DEC-1177) and the version [CAP-33, DEC-832 item 2, DEC-981] Verify: sha256 of the three copies equal; `git diff` of the kernel copy against the base touches only those four places; `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0'
  - 'S5 The CIT-P record `docs/changes/W2-188-CIT-P.md` gives the skill''s sha256 before and after, the lines added and removed, the old and new text of each changed place, the impact table (W2-11''s body case red until the copies ACT; W2-88a''s cases unchanged), the independent review''s verdict and the owner''s approval line of the bytes before the merge [CAP-33, DEC-105] Verify: the record holds both hashes (the after equal to the kernel copy at the ticket''s last commit), the counts, a `verdict: PASS` as the last verdict and an `owner_approval:` line naming the sha256'
  failure:
  - 'F1 Any other step, section or rule of the adopt skill changes, or the skill grants a permission, names a `gov.memaudit` subcommand or states a mode the product lacks. Verify: the S4 diff; a grep of the three copies for `gov.memaudit` and `standing declare` finds nothing'
  - 'F2 The ticket writes `.claude/skills/adopt/SKILL.md` or any test under `tests/acceptance/`. Verify: the close''s diff names neither; the copies ACT regenerates the `.claude` copy after the owner''s approval'
  - 'F3 The text says the standing set may be used to choose, judge, adopt or reject a fix, prints or reads a question id, or calls the reader a second reranking model. Verify: a string test on step 6 and §9 for "never chooses or judges a fix" and "counts only"; §9 says W2-88 S10''s second reranker stays forbidden'
non_goals:
- 'no code: the standing mode, the bar, the per-repository state, the maintenance pass and the cron line in the ACT package''s text are W2-187'
- 'no `.claude/` copy (the copies ACT) and no acceptance test (the test designer)'
- 'no change to A9''s other six steps, to the Verify section or to W2-88''s closed ticket (its lines are re-baselined by the CTO''s record edit under DEC-1177 (7))'
- 'no change to W2-88 S10''s standard or the forbidden second reranking model'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1177, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1074, DEC-1071, DEC-1072, DEC-105, DEC-974, CAP-33, DAEO-pg6i, DAEO-2bdu]
acceptance_tests: {path: tests/acceptance/W2-188/}
---

# W2-188 The adopt skill's step 6 and the practice record: the standing set

**Problem.** The adopt skill's A9 step 6 (`template/governance/kernel/skills/adopt/SKILL.md:58`, and the two `.rulesync`
copies) says: "Declare and measure the verdict set once. A miss stands as it is: the set is never run again." The
practice record says "measured once" in three places (`docs/research/W2-88-memory-practice.md:91-92, 190-191, 221`).
DEC-1176 (1) kept them standing until the weekly re-measure was decided. The owner decided it on 2026-11-14 (DEC-1177,
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
- Do not write the below-95 rule before DEC-1177 (4) is recorded. Copy it word for word.
