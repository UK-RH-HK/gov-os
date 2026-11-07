Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-138/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-138 — the engineer's second pass (DAEO-rmhj)

Your first pass is built (`dcda2701`; `gov accept W2-138` 18/18). Read the ticket's "Built" section. The six unit
"same as before" guards that fail on the token's new `s` key are now in your paths:
- `tests/unit/retrieval/test_w2_131_register_ids.py`: `test_the_bundle_is_the_same_before_and_after_but_for_register_ids`,
  `test_the_continuation_carries_on_the_same_before_and_after`;
- `tests/unit/retrieval/test_w2_133_gap_label.py`: the same two kinds;
- `tests/unit/retrieval/test_w2_135_item_cap.py`: the same two kinds.

Change only their token comparison, so a decoded token is compared without its `s` key, each change commented
`DEC-1090 (3)`, keeping everything else they compare.

**Your own ticket's acceptance folder** `tests/acceptance/W2-138/` stays unread: keep `!tests/acceptance/W2-138/**` in
every Grep glob (your first pass saw six call-site lines through a wide glob; say so if it happens again).

Your worktree `/home/usain/gov-os-worktrees/W2-138`, branch `w2/W2-138` (integrate merged). Run those three files and
your `test_w2_138_store.py` through the heavy slot, then `gov accept W2-138` again. The rules of your first brief
(`W2-138-engineer.md`) hold. Commit with
`--trailer "Task: DAEO-rmhj" --trailer "Implements: DEC-1090" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
Return the twelve fields, short.
