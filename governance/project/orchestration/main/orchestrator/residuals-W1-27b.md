
## W1-27 follow-up: historical paths in doctor's stale-path check (DEC-456, 2026-10-07)

Merged at `6db36969` (cases `f4ec043c`, code `da877e8a`; sessions on Claude Opus 5.5). `docs/SOURCES.md` and
the old `cli/` tree are historical for the stale-path check; the plan validator's one stale path was fixed in
`4eb9aacd`.

- `gov check` on the branch before the merge (DEC-466, DEC-467; `log/check-at-W1-27b-premerge.json`): no red
  outside the baseline. `secrets-indexing` was not red in that worktree run; it stays in the baseline until
  it is seen green in the main tree.
- Full regression at `6db36969` (`log/reg/at-W1-27b-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- `gov doctor` at `6db36969` (`log/doctor-at-6db36969.json`), exit 3: the stale-path check passes (0 moved
  references, 179 historical excluded). Two parts are still not green: the Claude Code drift (re-recorded at
  the Wave 1 exit, DEC-448), and index freshness (9 stale files): every commit since the one rebuild makes
  the lexical index stale, and no second rebuild is run here (DEC-448). Hooks, canaries and the framework
  lock are reported unmeasured. For the owner at the exit: whether the index is rebuilt once more at
  adoption (W1-41).
- W1-41's adoption review decides whether the old `cli/` tree is archived (DEC-456).
