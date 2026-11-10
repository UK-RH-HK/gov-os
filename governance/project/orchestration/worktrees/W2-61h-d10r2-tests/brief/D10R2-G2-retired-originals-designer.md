Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-61h-d10r2-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10 group G, round 2: Q07 and Q14 into W2-61's RETIRED_ORIGINALS (DAEO-h2k3, W2-61h)

You are a fresh **independent test designer**, launched under W2-61h's ticket (`.tickets/DAEO-h2k3.md`). Round 1
(`a2104dc5f` on your branch) fixed Q22 and Q24. It proposed, and the CTO approves, option A for Q07 and Q14.

## The red
`tests/acceptance/W2-61/test_w2_61_visible_half.py::test_each_question_is_table_2_s_command_with_its_options`:
`Table 2 rows not matched: ['Q07', 'Q14']; files not in Table 2: ['q07.yaml', 'q14.yaml']`. Q07 and Q14 were re-worded
on 11-09 (`55d1c0297`, DEC-1070 (13), DEC-1097 (12), DEC-1098 (6)), and their pre-reword originals are kept under the
visible set's `retired/` folder. Table 2 (`docs/assessment/2026-10/B-memory-retrieval.md`) is a dated report and stays
as written.

## The task
1. Add `"q07.yaml"` and `"q14.yaml"` to the test's `RETIRED_ORIGINALS` mapping, pointing at their retired originals
   (check the exact file names under `fixtures/evaluation/memory-retrieval/visible/retired/`), so Table 2 is compared
   with the original wording. Add one line to the case's docstring about the 11-09 re-word. Lower nothing else.
2. Run, through the heavy slot (`EMG-common.md`), with `PYTHONPATH=<your tree>/src`:
   `python3 -m pytest tests/acceptance/W2-61 tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
   Expected after this round: only Q23's 3 cases still red (left for the owner's re-word). Report the counts.
3. One line in W2-61's README.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-61h-d10r2-tests`, branch `w2/W2-61h-d10r2-tests` (head `a2104dc5f`). Write
  only `tests/acceptance/W2-61/**`.

## Rules
- `EMG-common.md` holds. **The hidden-half rule, strictly:** never open the evaluation sets' hidden half, the run
  folders or any held-out material. No installs, never the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-h2k3" --trailer "Implements: DEC-1123, DEC-1097"
  --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 15 minutes. Return the twelve fields, short: the change, counts before and after, the head commit.
