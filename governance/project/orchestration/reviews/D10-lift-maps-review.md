# The lift's map fixes: the review of W2-92's and W2-05's README maps made readable by gov accept (W2-96, DAEO-ouet)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-lift-maps-review.md`; branch `w2/W2-96-maps-lift-tests` at `d269ed550` (designer commits `ba5cf0f87`, `d269ed550`); merged `93ac67c0b`; reviewer log `/home/usain/gov-os-worktrees/W2-96-maps-lift-tests/.gov-runtime/scratch/lead/log/D10-lift-maps-review.json`
- verdict.py: READY (no findings).

**Sandbox check:** (a) passed: writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet` failed with "Read-only file system". (b) partly done: `git update-index --refresh` worked. I did not run `git hash-object -w`, because it writes an object and this brief says to write nothing. **ps check:** the sandbox shows only my own shell and the `ps` call. No ollama or llama-server process is visible.

- **task:** DAEO-ouet (W2-96). The lift's map fixes to the W2-92 and W2-05 READMEs, reviewed at head `d269ed550`.
- **status:** DONE
- **work_completed:** Read the diff from `1905b2969` to `d269ed550` and the two commits' trailers. Ran the map reader (`parse_map`) on both READMEs. Checked that every name written in full in rows 132-134 is a real test or test case. Checked where each edge row sits against the ticket's own lines.
- **files_changed:** none. `git status --porcelain` is empty.
- **evidence:** `parse_map` on W2-92 gives failure-1/2/3/6 and success-1, 2, 3, 4, 6, 7, 8, 9, 10, 11. It raises nothing and includes both success-4 and success-6. `parse_map` on W2-05 gives failure-1 and success-1/2/3, and raises nothing. Each of the four full test names appears exactly once in the W2-05 test files: `planted.py:253`, `declared_check.py:141`, `settings.py:102`, `planted.py:423` and `planted.py:488`. The case labels named in the rows also exist: `planted.py:246-248` and `declared_check.py:85`.
- **tests:** none run. The brief allows only the reader check.
- **discoveries:** none.
- **risks:** none in scope.
- **lessons:** none.
- **proposed_decisions:** none.
- **unresolved:** sandbox check (b) is only partly done (no `hash-object -w`), as explained above.
- **recommended_next_action:** the CTO merges W2-96's map fixes, then runs `gov accept` for W2-92 and W2-05 at the lift.

## Checks
1. **Same meaning:**
   - **W2-92:** the only change is "S1's record route" becoming "the record route". The row still names exactly success-6 with success-4, and the Tests cell and the reason column are unchanged. The prose loses nothing, since the record route is S1's anyway.
   - **W2-05:** every edge row keeps its cases and words.
     - The row about a caller that set `GIT_*` on purpose is now filed under **F1**, the planted `GIT_*` line, where it belongs.
     - The row about a check in a linked worktree is now under **S2**, the linked-worktree line (ticket line 32/85).
     - The row about a call in a command, a check and a test helper is now under **S1**, the line about every check, test helper and command (ticket line 30/84).
     - No case is dropped or moved off a line, and no line's requirement is lowered.
2. **Reads:** neither map raises an error. W2-92's set of lines is the other rows' lines plus success-4 and success-6. In rows 132-134 of W2-05, each name that was shortened with "..." is now written out in full. Each full name matches exactly one existing test, and it is the test the shortened name meant: the shortened forms were unique prefixes.
3. **Trailers and scope:** both commits carry Task, Implements (DEC-1112), Role (independent-test-designer), Rewrite-Reason (DEC-866) and Co-Authored-By. Only the two READMEs changed. In W2-92 no Tests cell changed. In W2-05 the Tests cells of rows 133-134 changed only by writing the shortened names in full, which the brief asked for. Nothing else changed.

**What I probed and found sound:** whether the maps read, whether each named test exists, where each row sits against the ticket, the trailers, the scope, and that I left the tree clean.

**Findings:** none. Classification: no findings, so no round is proposed.

```verdict
{"kpis": [{"kpi": "lift-maps-readable", "verdict": "pass", "findings": []}]}
```
