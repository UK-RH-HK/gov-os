Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-61h-d10r2-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10 run 1's red group G, W2-61 part (4 cases): the visible questions behind HEAD (DAEO-h2k3, W2-61h)

You are a fresh **independent test designer**, launched under W2-61h's ticket (`.tickets/DAEO-h2k3.md`). D-10
(DEC-1122 (3)) needs these records current before run 2. Visible half only.

## The reds (integrate's head `c9742b08910a`; each red alone too)
- `tests/acceptance/W2-61/test_w2_61_visible_half.py::test_each_question_is_table_2_s_command_with_its_options`:
  `lens B's 20 files are not Table 2's commands; Table 2 rows not matched: ['Q07', 'Q14']; files not in Table 2: ['q07.yaml', 'q14.yaml']`.
  Q07 and Q14 were re-worded on 11-09 (`55d1c0297`, DEC-1070 (13), DEC-1097 (12), DEC-1098 (6)); Table 2 was not.
- `..._visible_half.py::test_every_source_exists_at_head_and_every_heading_is_found_there`:
  `q23.yaml: heading 'MAP_REL = "governance/project/test-map.yaml"' is not a line of src/gov/close/select.py`.
- `tests/acceptance/W2-61h/test_w2_61h_visible_new.py` (2): `q22.yaml: source entry 1: its cited lines at HEAD differ
  from the question's commit` and `source 1 does not hold ['set_fault(']`.

## The task
1. Bring the records to HEAD the way the suite's README and DEC-1070/DEC-1097 say a visible question is kept: Table 2's
   Q07 and Q14 rows to the re-worded questions (or the files to the table, whichever the decisions name as the
   source of truth); q22's and q23's sources re-pointed to where the cited facts now live at HEAD (same facts, new
   lines/headings, the question's commit updated as the suite requires). If a fact no longer exists at HEAD, change
   nothing for it and report it (the question needs re-wording by the owner's process, not here).
2. Run, through the heavy slot (`EMG-common.md`), with `PYTHONPATH=<your tree>/src`:
   `python3 -m pytest tests/acceptance/W2-61 tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
   Report counts before and after.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-61h-d10r2-tests`, branch `w2/W2-61h-d10r2-tests` (from integrate at
  `c9742b08910a`). Write only `fixtures/evaluation/memory-retrieval/visible/**` and the Table 2 document the suite
  reads (name it in your return).

## Rules
- `EMG-common.md` holds. **The hidden-half rule, strictly:** never open anything under `~/gov-os-eval/`,
  `~/gov-os-runs/`, any `hidden`, `memory-verdict` or `memory-verdict-2` folder, or the evaluation set's hidden half.
  No installs, never the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-h2k3" --trailer "Implements: DEC-1122, DEC-1097"
  --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short: each record changed, counts before and after, the head commit.
