# W2-141's README: the three edits row 88 asks for (F1, F2, F3), as text for the CTO to apply

The README is `docs/changes/W2-141-hook/README.md`. It is not in this helper's paths, so the edits are given here whole.
Apply them in one commit with `Task: W2-141`. Nothing else in the README changes.

## F1 (the rebuild note names all four ACTs)

In the paragraph that starts "`pretooluse.py` was rebuilt on 2026-11-10", replace the parenthesis
`(ACT-SETS-GLOBS-1; it carries rule 2b's glob line, rule 2c and rule 2d, which the first copy, made from `bd545af8…` at `15952bbfa`, lacked)`
with:

```
(ACT-SETS-GLOBS-1; the first copy, made from `bd545af8…` at `15952bbfa`, lacked what four ACTs added after it:
ACT-INDEP-WALLS-1's rule 2c, ACT-GUARD-CALLLOG-1's call log (`record()` and the rule argument of `answer()`),
ACT-OPERATOR-1's rule 2d and ACT-SETS-GLOBS-1's rule 2b glob line and `Narrow`; this copy carries all four)
```

## F2 (the "Before the ACT" list names test_g14's four cases)

Add this bullet to "Before the ACT":

```
- `.gov-runtime/scratch/orchestrator/drafts/g14/test_g14.py` has four engineer cases that encode the rule this ticket
  changes: "a search of the whole acceptance folder (from above)", "Glob lists names", "Grep from above" and
  "grep -r from above" (all in `test_near_misses_pass`). With this copy live they fail, and they are meant to (S1, S2
  refuse a search from above for the engineer's own folder). Expect exactly these four red, by name, and no other. The
  re-pin script (`pin/repin7_checks.sh`) does this: with the live hook carrying `BEGIN W2-141 BLOCK` it requires these
  four red and the rest green; without it, none red; and it runs the staged pair the same way, so the result does not
  depend on which ACT goes first. Rehearsal with the candidate pin: 4 failed, 147 passed, 1 skipped.
```

## F3 (the rollback is committed and merged into the worktrees)

Add a fourth step to "Rollback":

```
4. **Commit and merge the rollback.** Every worktree runs its own copy of `.claude/hooks/`. After copying the kept files
   back (or restoring the tracked versions), commit them in the tree the ACT applies to, then merge `w2/integrate`
   into each worktree that has the staged copy. Until then those sessions keep the stricter hook. Nothing fails open:
   the staged hook refuses more, not less.
```

## D1 (a row for the guard, not for the README)

`git diff <rev>:<path> <rev>:<path>` is refused by the live guard for any role with a hidden part: `patched()` in
`src/gov/guard/reads.py` resolves every revision word as a commit (`rev-parse <word>^{commit}`), and a blob reference
cannot resolve that way, so the call fails closed. A false refusal (a reviewer often diffs two versions of a file); the
workaround is `git show <rev>:<path>` into scratch files, then `git diff --no-index`. Proposed row: a ticket for the
guard (engineer, tests first), after the lift. Not for this re-pin: the new pin carries the same behaviour as the live one.
