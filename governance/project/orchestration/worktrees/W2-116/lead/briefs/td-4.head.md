# Brief: independent test designer, W2-116 (DAEO-f58b) pass 2c: seven other tickets' test files, revised to two decided behaviours

You are a fresh independent test designer (MR-3) for ticket DAEO-f58b (W2-116). The ticket has two decided
behaviours that turn 17 cases of other tickets red. The CTO routes them to you as revisions of decided behaviour
(DEC-1156 (7)) and widened the ticket by exactly these seven files (9a467f336). Revise each so it holds against the
decided behaviour, with no case losing its point. Change nothing else.

The two decided behaviours (both already in the code of your branch; read it if you need to):
- **R2-F3, the CTO's Q3 (a) under DEC-1157 (12):** a continuation token now carries an `f` key, the folder (store half)
  it was made on, beside W2-138's `s` key (the store's commit). `src/gov/retrieval/retrieve.py` lines ~195-225. Two
  stores in two folders give two different `f` values, as they already gave two `s` values.
- **S2's status part (in the ticket):** `gov status` has a new part `integration_store`, placed after `reranker` and
  before `not_read` (`src/gov/status/command.py` lines 195-209). In a project whose `governance/project/rebuild.yaml`
  names no `integration_store`, the part is `{"read": false, "reason": "governance/project/rebuild.yaml names no
  integration_store: there is no integration store"}`, so `not_read` names it (`integration_store: <reason>`).

## Where you work
- Worktree /home/usain/gov-os-worktrees/W2-116-tests, branch w2/W2-116-tests (at 9e9428942). Write only these seven
  files there; commit there; never merge, never push:
  1. `tests/acceptance/W2-131/test_w2_131_unchanged.py`
  2. `tests/acceptance/W2-133/test_w2_133_unchanged.py`
  3. `tests/acceptance/W2-135/test_w2_135_unchanged.py`
  4. `tests/unit/retrieval/test_w2_131_register_ids.py`
  5. `tests/unit/retrieval/test_w2_133_gap_label.py`
  6. `tests/unit/retrieval/test_w2_135_item_cap.py`
  7. `tests/unit/status/test_status.py`

## What to do
**Files 1 to 6:** the helper that drops the `s` key before comparing continuation tokens from two folders drops `f` as
well. Nothing else changes. Where it is today:
- file 1: `STORE_KEY = "s"` (line 27), used to drop the key at line 50 (`_without...`), and read at lines 42 and 56;
- file 2: `STORE_COMMIT_KEY = "s"` (line 48), dropped at line 61;
- file 3: `STORE_KEY = "s"` (line 34), dropped at line 52, read at lines 56 and 62;
- files 4, 5, 6: `payload.pop("s", None)` (lines 171, 152, 331) in the `_without_s`-style helper.
Only the dropping changes: drop `f` beside `s` (for example a second constant `FOLDER_KEY = "f"` with a comment
naming R2-F3 / Q3 (a), DEC-1157 (12), and `key not in (STORE_KEY, FOLDER_KEY)`; or a second `payload.pop("f", None)`).
The reads of the `s` key (the store-commit premise and comparisons at file 1 lines 42/56, file 3 lines 56/62) stay as
they are: they test the `s` key's own point. If a helper's name or docstring says "without s", its docstring may name
`f` too; do not rename functions.

**File 7** (`test_a_status_with_a_part_not_read_names_every_such_place`, line ~167-178, and `PARTS` at line 27): the
exact `PARTS` tuple gains `"integration_store"` in the position the code gives it (after `"reranker"`), with a comment
naming W2-116 S2. The case still pins the whole tuple (`tuple(answer) == ("root", "config_files", *PARTS,
"not_read")`). `not_read` stays asserted exactly, as the code's behaviour now is: run the case after the tuple change,
and if the fixture project (no `integration_store` configured) now gets the `integration_store` place in `not_read`,
the two exact assertions name it in the place the code gives it (the first `== []` and the later list of places
`["tickets.ready", "tickets.blocked", "decision_packages"]`). Each assertion stays exact: never loosen to a subset,
`in`, or a filter. Check that `PARTS` is used nowhere else in the file in a way the new member breaks.

**One commit per file** (seven commits), each:
```
git -C /home/usain/gov-os-worktrees/W2-116-tests commit -m "W2-116 pass 2c (DAEO-f58b): <file's short name>: <what changed>" --trailer "Task: DAEO-f58b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-983, DEC-982, DEC-963, DEC-1087" --trailer "Rewrite-Reason: DEC-1156 (7), R2-F3's token key / S2's status part (W2-116 pass 2c)" -- <that one file>
```
(For file 7 the subject names S2's status part; for files 1-6, R2-F3's `f` key.)

## Check (run it after the edits; every case must pass)
The 17 cases red on the branch before your change (from the lead's scoped run):
```
tests/acceptance/W2-131/test_w2_131_unchanged.py  (2: test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[a-ticket-batched], test_s3_the_continued_pages_are_todays_but_for_the_ids_of_register_items)
tests/acceptance/W2-133/test_w2_133_unchanged.py  (4: the bundle [every-chunk-batched-gov-retrieve], [every-chunk-batched-retrieve-alone]; the continued pages [gov-retrieve], [retrieve-alone])
tests/acceptance/W2-135/test_w2_135_unchanged.py  (4: [register-every-chunk-batched-gov-retrieve], [almanac-batched], [every-file-batched], [almanac-batched-budget-1000])
tests/unit/retrieval/test_w2_131_register_ids.py  (2), test_w2_133_gap_label.py (2), test_w2_135_item_cap.py (2)
tests/unit/status/test_status.py::test_a_status_with_a_part_not_read_names_every_such_place  (1)
```
Run the seven whole files (all their cases must pass, not only the 17), from the tests worktree:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-116-tests/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest <the seven files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Put it in a script under /home/usain/gov-os-worktrees/W2-116-tests/.gov-runtime/scratch/td/ (make the folder with the
Write tool) and run it with `bash`. `/tmp` is read-only in the sandbox: keep the sandbox's own `TMPDIR` (outside the
repository). A resource gate's refusal is a wait (DEC-1146). The `heavy-slot-waits.jsonl: Read-only file system` line
is harmless. Run it before your edits too, to see the 17 red, and after, to see them green.

## Rules
- Write only the seven files. Never read the evaluation sets' root or any hidden or memory-verdict folder.
- No `gov retrieve` or `gov context` in the sandbox: search with Read and Grep, and once more in other words if the
  first does not answer (DEC-1065).
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it
  (DEC-1142 (9)).
- If a case cannot keep its point with only these changes, do not stretch the change: say so in `unresolved`.

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence (the pytest summary line, before and after) / tests / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then `commits:` with hash12 and subject, one per file.

## The ticket's context (gov context DAEO-f58b --role independent-test-designer)
