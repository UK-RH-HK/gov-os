# DAEO-zlog (W2-188): the I5 checks and the literal-phrase checks

Base `5336a6fca`. Run by one script that imports `w2_88a_support` from `tests/acceptance/W2-88a/`; no test suite.

## 1. check_steps and check_pointer (I5)
- `template/governance/kernel/skills/adopt/SKILL.md`: regions found 1; check_steps -> []; check_pointer -> []
- check_steps + check_pointer on template/governance/kernel/skills/adopt/SKILL.md: PASS
- `.rulesync/skills/adopt/SKILL.md`: regions found 1; check_steps -> []; check_pointer -> []
- check_steps + check_pointer on .rulesync/skills/adopt/SKILL.md: PASS
- `template/.rulesync/skills/adopt/SKILL.md`: regions found 1; check_steps -> []; check_pointer -> []
- check_steps + check_pointer on template/.rulesync/skills/adopt/SKILL.md: PASS
- `docs/research/W2-88-memory-practice.md` section 6: sections found 1; check_steps -> []
- check_steps on the practice record's section 6: PASS

## 2. skill_validator --both-layouts
- exit code 0
```
{"findings": []}
```
- skill_validator exit 0: PASS

## 3. sha256sum of the three copies
- `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`  template/governance/kernel/skills/adopt/SKILL.md
- `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`  .rulesync/skills/adopt/SKILL.md
- `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`  template/.rulesync/skills/adopt/SKILL.md
- three copies equal: PASS

## 4. grep -c 'gov.memaudit\|standing declare'
- `template/governance/kernel/skills/adopt/SKILL.md`: 0 (grep exit 1)
- no gov.memaudit / standing declare in template/governance/kernel/skills/adopt/SKILL.md: PASS
- `.rulesync/skills/adopt/SKILL.md`: 0 (grep exit 1)
- no gov.memaudit / standing declare in .rulesync/skills/adopt/SKILL.md: PASS
- `template/.rulesync/skills/adopt/SKILL.md`: 0 (grep exit 1)
- no gov.memaudit / standing declare in template/.rulesync/skills/adopt/SKILL.md: PASS

## 5. The I1 diff against the base
```
template/governance/kernel/skills/adopt/SKILL.md | 8 +++++---
 1 file changed, 5 insertions(+), 3 deletions(-)
```
- hunks (`git diff -U0`): 4
- numstat: `5	3	template/governance/kernel/skills/adopt/SKILL.md`
- hunk headers: @@ -4 +4 @@; @@ -58 +58 @@; @@ -60,0 +61,2 @@; @@ -74 +76 @@
- four hunks, 5 added, 3 removed: PASS
- `.rulesync/skills/adopt/SKILL.md`: ` 1 file changed, 5 insertions(+), 3 deletions(-)`
- `template/.rulesync/skills/adopt/SKILL.md`: ` 1 file changed, 5 insertions(+), 3 deletions(-)`

## 6. Literal phrases
- step 6 is line 58; step 7 is line 59; the heading is line 63; lines between: ['', "The weekly audit runs from one cron line that A9's ACT package gives the repository's owner's operator, beside the walls; adoption never installs it. A standing set that falls below 95 % is a miss with counts only, handled as the practice record's section 9 states. [DEC-1179 (4), (5), DEC-1101 (2), DEC-1125 (2)]",
- exactly one blank line before the paragraph and before the heading, one paragraph: PASS
- step 6 holds 'standing set': PASS
- step 6 holds 'every week': PASS
- step 6 holds 'same questions': PASS
- step 6 holds '95 %': PASS
- step 6 holds 'counts only': PASS
- step 6 holds 'never chooses or judges a fix': PASS
- step 6 holds 'fresh set': PASS
- step 6 holds 'month': PASS
- step 6 holds 'fitted': PASS
- step 6 holds 'replaced': PASS
- step 6 holds 'DEC-1179': PASS
- step 6 holds 'Declare': PASS
- step 6 holds 'measure': PASS
- step 6 holds 'the verdict set': PASS
- step 6 holds 'once': PASS
- step 6 holds 'never re-run': PASS
- step 6 holds 'never re-scored': PASS
- step 6 holds 'the first verdict': PASS
- step 6 starts with 'Declare' and no 'declar' earlier in steps 1 to 5: PASS
- step 6 does not hold the step-7 anchor: PASS
- step 6 has no 'gov.memaudit' / 'standing declare': PASS
- step 6 never calls the reader a second reranking model: PASS
- step 6 holds no method figure (no E2, E3, 115, 128, 114, 138, 84): PASS
- step 6 uses plain ASCII only: PASS
- paragraph holds 'cron': PASS
- paragraph holds 'ACT': PASS
- paragraph holds 'operator': PASS
- paragraph holds 'never installs': PASS
- paragraph holds '95 %': PASS
- paragraph holds 'section 9': PASS
- paragraph holds 'DEC-1179': PASS
- paragraph names no subcommand: PASS
- paragraph is ASCII: PASS
- skill version is 1.1.0: PASS
- sources line holds DEC-1101, DEC-1125, DEC-1179 in numeric order: PASS

## 7. The practice record
- section 9 is the last section, after section 8: PASS
- section 9 holds 'counts only': PASS
- section 9 holds 'never chooses or judges a fix': PASS
- section 9 holds 'ceil(0.95 n)': PASS
- section 9 holds '114': PASS
- section 9 holds '84': PASS
- section 9 holds '115': PASS
- section 9 holds '128': PASS
- section 9 holds '138': PASS
- section 9 holds 'second reranking model': PASS
- section 9 holds 'stays forbidden': PASS
- section 9 holds 'the reader is not one': PASS
- section 9 holds '5 points': PASS
- section 9 holds 'A2': PASS
- section 9 holds 'search again once': PASS
- section 9 holds 'fitted': PASS
- section 9 says the reader ranks the whole bundle itself: PASS
- section 9 never says the reader is a second reranking model: PASS
- DEC-1179 (4) as recorded: 463 characters, 464 bytes; begins `**Below 95 %:** the package's §5.1 rules R1 to R9 (a miss re`; ends `low; R9 with the check against fitting).`
- section 9 holds DEC-1179 (4) byte for byte: PASS
- the verbatim text stands unbroken on one line, as the last bullet: PASS
- section 9's '§' is UTF-8: PASS
- section 3 holds the standing-set bullet and keeps its '3 points': PASS
- section 5 item 6 holds the two sub-bullets: PASS
- section 5 item 6's practice lines (after its last `The practice:`) hold 'standing set', 'every week', 'counts only', 'never chooses or judges a fix', 'fresh set', 'DEC-1179' and '§9' (re-run after the line was re-worded, practice record at sha256 `76eaaeb5487739643cef6d79d8f736331ee5396756b1f123c5236c9bcb60d312`): PASS
- section 5 item 6's first sub-bullet and 'within 5 points' kept; section 6's `check_steps` -> [] again; section 9 still last and untouched: PASS
- section 5 'within 5 points' kept: PASS
- section 6 step 6 re-worded: PASS
- section 6 step 5 keeps '5 points': PASS

## Result
0 failed check(s). All checks passed.
