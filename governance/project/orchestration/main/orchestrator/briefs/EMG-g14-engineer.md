# G-14 engineer: role separation from the path map (DEC-1052 G-14), resumed 2026-11-03 by CTO session 33b3628c

Read first, whole: `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` (your common rules) and
`governance/project/orchestration/INTENT-DEC-1052.md` (the basis; its "Role separation from the path map" paragraph is
your spec). Then `.gov-runtime/scratch/orchestrator/drafts/g14/NEXT.md`: the design and the exact next steps 1-5,
written by the engineer who stopped at a safe point. Resume from it; do not redo its reading.

**The spec (DEC-1052 G-14, word for word):** role separation is enforced deterministically from the path map: each
role's reads and writes are its paths; the engineer never reads the acceptance tests; the test designer never reads
the engineer's new code (it may read the integrated code, DEC-963); simple path checks, no shell guessing.

**Task id:** DAEO-sdxk (W2-00). **Role:** engineer. **Nothing goes live:** you build a candidate and its evidence; the
live hook (`.claude/hooks/pretooluse.py`), the path map and `~/.claude/` are changed only by the owner's ACT you write.

**Where you write:** only `.gov-runtime/scratch/orchestrator/drafts/g14/` and `TMPDIR=/tmp/gov-os-emg-g14`. No commits
(scratch is not tracked). `rm` only inside those two.

**The work (NEXT.md steps 1-5):**
1. The candidate: copies of the live `pretooluse.py` and `bash_writes.py` in `drafts/g14/`, plus `role_reads.py`, wired
   into `main()` after rule 2's read judge, judged for both the session role and the acting role. Reuse only
   `_Part(...).inside()` and the ticket reader from the pinned `reads.py`, never `_Judge` (W2-58's shell guessing).
   Unresolved targets, searches from above and unreadable commands are let through (rules 1 and 5 work the same way
   since ACT-GUARD-FIX-4). An absent `role_paths:` section means no check (it fails safe to today's behaviour).
2. `drafts/g14/path-map-role_paths.patch`: engineer `reads_denied: ["tests/acceptance/**"]`; independent-test-designer
   `reads_denied: ["{ticket_impl}"]`.
3. The replay over the real transcripts (`~/.claude/projects/-home-usain-gov-os-worktrees-W2-*` and the main tree's).
   **Parse only the tool calls' inputs (tool name, paths, commands); never print or keep tool results or file
   contents** (transcripts can hold material the guard's rules 3 and 4 protect). Report the would-be refusals per
   role and pattern, and classify by hand each as honest (a true separation the rule should make) or false (honest
   work refused). **Run three variants and give the counts of each:** (a) engineer: all of `tests/acceptance/**`;
   (b) engineer: only `{ticket_tests}`; and for the designer, (c1) `{ticket_impl}` = allowed_paths outside `tests/`,
   (c2) `{ticket_impl}` including the engineer's `tests/unit/**` and `tests/conftest.py` paths. (c1) against (c2) is
   the owner's open question: give the extra refusals (c2) adds and what they would have read.
4. Planted cases (each role, each tool form, a true read refused, a near miss let through, the absent-section case);
   then `drafts/act-guard-fix-4/test_guard_fix_4.py` and `tools/guard4_check.py` pointed at the candidate, to show the
   five rules unchanged. Every run through `tools/heavy_slot.sh`, `TMPDIR=/tmp/gov-os-emg-g14`.
5. `drafts/g14/ACT-G14.md`: the owner's ACT (exact operator commands: backups, the copies into place, the path-map
   patch, the checks, a one-command rollback), with one line naming which of the basis's five questions it passes,
   the replay's counts, and the open question (c1)/(c2) with your recommendation. Note in it that a path-map change is
   in the test selection's shared core (it selects everything), so the ACT names the scoped tests to run instead.

**Verified by:** the replay's counts (honest refusals named, false ones zero or each explained), the planted cases,
and the five rules' tests green on the candidate. **Estimate:** about 2 to 3 hours; speed matters.

**Return:** the twelve fields of EMG-common, status DONE, PARTIAL or PACKAGES; the (c1)/(c2) counts in `evidence`; the
file list in `files_changed`; your recommendation on (c1)/(c2) in `proposed_decisions`.
