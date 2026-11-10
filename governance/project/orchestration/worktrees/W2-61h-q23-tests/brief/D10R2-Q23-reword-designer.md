Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-61h-q23-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Q23 of the memory-retrieval visible half: re-word it to a stable fact (owner, 2026-11-10; DEC-1124)

You are a fresh **independent session**, independent of the retrieval work, launched as an independent test designer
under W2-61h's ticket (`.tickets/DAEO-h2k3.md`). The owner decided that Q23 is re-worded **by the process used for Q07
and Q14** on 11-09 (DEC-1070 (13), DEC-1097 (12), DEC-1098 (6); commit `55d1c0297`): an independent session re-words
it to a stable fact. **You choose the wording.** The CTO gives none and will not review your choice of fact, only the
form.

## Why
`fixtures/evaluation/memory-retrieval/visible/q23.yaml` cites a line that has moved at HEAD: its heading
`MAP_REL = "governance/project/test-map.yaml"` is no longer a line of `src/gov/close/select.py`. So 3 cases are red:
`tests/acceptance/W2-61/test_w2_61_visible_half.py::test_every_source_exists_at_head_and_every_heading_is_found_there`
and two in `tests/acceptance/W2-61h/test_w2_61h_visible_new.py` (the cited lines, and the source holding its answer).
A question tied to a line that moves is volatile. The set needs a question whose answer stays true.

## The task
1. Read the form first: `fixtures/evaluation/memory-retrieval/retired/README.md`, especially the section "The
   questions re-worded 2026-11-09 under DEC-1070 (13)", the two files `retired/q07-pre-reword-2026-11-09.yaml` and
   `retired/q14-pre-reword-2026-11-09.yaml`, today's `visible/q07.yaml` and `visible/q14.yaml`, and the W2-61 and
   W2-61h suites' READMEs and support modules, which say what a visible question must hold.
2. Keep `id: Q23` and its category, unless the form requires otherwise. Re-word it to a fact that is stable at HEAD
   and will not move with ordinary edits: a decision's rule, a documented contract, or a defined name with its
   meaning, rather than a line number. Write the gold answer and the sources so the suites' checks hold at HEAD,
   including the question's commit.
3. Keep the original byte for byte as `retired/q23-pre-reword-2026-11-10.yaml`. Add a README entry in the 11-09
   section's form: what it was, why it was retired (the line moved; the owner's decision of 2026-11-10, DEC-1124),
   and its replacement.
4. If W2-61h's support or cases hold an anchor for Q23 (`NEW_VISIBLE` and anything keyed on q23), keep them
   consistent with the new question. Lower no check.
5. Run, through the heavy slot (`EMG-common.md`), with `PYTHONPATH=<your tree>/src`:
   `python3 -m pytest tests/acceptance/W2-61 tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
   Expected: Q23's 3 cases green. Q07/Q14's Table 2 case may still be red in your tree, because another worker is
   fixing it on another branch. Report the counts.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-61h-q23-tests`, branch `w2/W2-61h-q23-tests` (from integrate at
  `0edfcda88`). Write only `fixtures/evaluation/memory-retrieval/visible/q23.yaml`,
  `fixtures/evaluation/memory-retrieval/retired/**` and, only if step 4 needs it, `tests/acceptance/W2-61h/**`.

## Rules
- `EMG-common.md` holds. **The hidden-half rule, strictly:** never open the evaluation set's hidden half, the run
  folders or any held-out material. Do not use the retrieval system to search for the answer: read the sources directly.
  No installs, never the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-h2k3" --trailer "Implements: DEC-1124, DEC-1070"
  --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short: the new question in one line, its sources, the counts before
  and after, the head commit.
