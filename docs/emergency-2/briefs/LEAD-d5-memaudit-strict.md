# Lead brief: D5, the strict forbidden-citation rule in `gov memaudit`'s grading (a fix under W2-204, `DAEO-ma4q`)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `d5-memaudit-strict`; worktree
`/home/usain/gov-os-worktrees/E2-d5-memaudit-strict`, branch `e2/d5-memaudit-strict` from `w2/integrate`. **Do not merge.**
It rides release 0.1.5. **Models (DEC-1225, in force):** every helper Sonnet, the test designer included; spawn with no
`model` (the C3 trial's Opus test designer is over).

**The owner's decision, DEC-1227 D5 (a):** keep W2-81's strict forbidden-citation rule, and "apply the same strict rule
to the product's own measure, so EXAMIN's 95 % is graded the same way as the proving run". Read
`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` rows T7 and line 169: W2-81's scorer
(`w2_81_score.py:51-55`, `:66-69`) counts an answer wrong when it cites a forbidden (stale, superseded, legacy) source;
`gov.memaudit.prompts.outcome` (`:60-72`) has no forbidden concept, so 24 of the proving run's 30 misses would have
been graded right by the product.

## The fix lines (failing test first; recorded in DAEO-ma4q's record as a fix, `Fix:` trailer)
- **S1 A question may name forbidden sources.** The measure's question format (visible and hidden sets, the writer's
  instructions and schema, `gov memaudit`'s steps) carries an optional list of forbidden sources per question, in the
  same shape W2-81's sets use. Verify: a set with and without the field both load; a malformed one is refused by name.
- **S2 Citing a forbidden source makes the answer wrong,** whatever the grader says of the answer, exactly as W2-81's
  scorer rules it (one rule; if both can share one function, share it). Verify: planted grades: correct + gold cited =
  right; correct + forbidden cited = wrong; correct + gold and forbidden cited = wrong (or as W2-81 rules it: match it
  and say which); wrong = wrong.
- **S3 The question writer is told to name the forbidden sources** where a stale or superseded source exists for a
  question (prompt text in `src/gov/memaudit`; kernel text is not touched).
- **S4 The record says it.** The measure's record names the rule (`forbidden_rule: strict`) and counts the
  forbidden-cited misses apart, so a figure graded before this fix is never compared with one after without saying so.
- Out of scope: the reader and grader models (lead `models-rubric` has them, R4); hit@k (a diagnostic only, EMERGENCY-2 5.2).

## Green and return
`gov accept W2-204` green (the test designer adds the cases; any that pin the old grading get a Rewrite-Reason naming
DEC-1227 D5), `tests/unit/memaudit`, `tests/acceptance/W2-81` if it imports the scorer, `tests/unit/optin`. Return:
branch and head; each S line with its tests; whether W2-81's scorer and the product now share the rule; the trial
figures (runs to green, send-backs, minutes, cost); reds not yours.
