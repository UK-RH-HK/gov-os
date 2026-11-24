# Lead brief: fix-dc-forbidden, `gov memaudit declare` notices (never refuses) a set with no forbidden list (a fix under W2-204, `DAEO-ma4q`)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (its test command, with node on PATH; the test
designer's reading bounded). Name: `fix-dc-forbidden`; worktree `/home/usain/gov-os-worktrees/E2-fix-dc-forbidden`, branch
`e2/fix-dc-forbidden` from `w2/integrate`. **Do not merge.** Every helper Sonnet; this lead runs medium. It blocks
release 0.1.5: green **within about 45 minutes**.

**The red** (the 0.1.5 full suite on `461c214a5`, weekly tier): 42 cases of `tests/acceptance/W2-187` fail. Cause:
`fixes-015a` F15 made `src/gov/memaudit/declare.py` (about `:280`) append `DC-FORBIDDEN` and refuse when no hidden
question carries a `forbidden` list. W2-187's standing measure plants sets with no forbidden lists, so every declare is
refused (`measure.out` reads `DC-FORBIDDEN`). The same would refuse EXAMIN's fresh 80 if its set held no stale source.

**The CTO's ruling (P2, DEC-1242 T-1's level; F15 was the CTO's own brief line):** the strict rule stays strict, and a
set with no forbidden list is a legitimate set. `declare` never refuses for it. Instead: the figure's stamp already
carries `questions_with_forbidden` (0 here); `declare` prints one notice line, exactly
`NOTICE DC-FORBIDDEN-NONE: no question carries a forbidden list; the strict rule grades as the lenient rule would`, and
the declaration record carries `forbidden_lists: 0`. The verdict and exit code are unchanged by it.

## The flow
1. Test designer: revise `tests/acceptance/W2-204/test_w2_204_fix_figure_stamp.py` (about `:103`, which asserts the
   refusal) to assert the notice, exit 0, and the record field, with `Rewrite-Reason: the CTO's ruling of 2026-11-24 on
   F15 (DC-FORBIDDEN refused legitimate sets; W2-187's 42 reds)` inside the final trailer paragraph; red on the base.
2. Engineer: the change in `declare.py`.
3. Green: `tests/acceptance/W2-187` with `GOV_TESTS_OPTIN=weekly` (all 210), `tests/acceptance/W2-204`,
   `tests/unit/memaudit` (`--optin=lifted`), `tests/acceptance/W2-201/test_w2_201_r4_memaudit_models.py`,
   `tests/unit/optin`; `gov accept W2-204` exit 0. Record the fix in `.tickets/DAEO-ma4q.md` as a `## Fix:` section.
Return: branch and head; the pytest summary lines; the accept summary.
