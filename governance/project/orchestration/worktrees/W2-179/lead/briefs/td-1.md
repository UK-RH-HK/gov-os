# Brief td-1: independent test designer, test revision, for DAEO-c9n8 (W2-179), profile LITE, class C1

You are the independent test designer (MR-3) for ticket DAEO-c9n8 (W2-179): a revision of one existing acceptance case of
W2-170 (closed). No engineer works on this ticket; no product code changes.

## The defect (facts)
The nightly of 2026-11-12 (run 20261112-0404, head 9bbef27f1d05) is red on
`tests/acceptance/W2-170/test_w2_170_s4_map.py::test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders`.
Its `reached` list holds 104 paths, every one a file or folder of the repository under test, e.g.
`/home/usain/gov-os-runs/W2-00/nightly/20261112-0404/src/gov/memaudit/__init__.py` and
`/home/usain/gov-os-runs/W2-00/nightly/20261112-0404/tests/acceptance/W2-170`: the nightly's clone lives at
`~/gov-os-runs/W2-00/nightly/<run>/`, inside `W.TRUE_RUNS` (the true home's `gov-os-runs`), so the case's filter
(`W.at_or_under(p, W.TRUE_SETS) or W.at_or_under(p, W.TRUE_RUNS)`, line 164) counts the repository's own imports and
reads as runs-folder opens. The code is not at fault. (Log: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/nightly/20261112-0404/parallel.txt, lines 154-178.)

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-179-tests |
| branch | w2/W2-179-tests |
| your allowed paths | tests/acceptance/W2-170/test_w2_170_s4_map.py, tests/acceptance/W2-170/README.md |
| ticket (KPIs S1, F1, F2) | /home/usain/gov-os-worktrees/W2-179-tests/.tickets/DAEO-c9n8.md |
| the context bundle (`gov context` for your role) | /home/usain/gov-os-worktrees/W2-179/.gov-runtime/scratch/lead/briefs/ctx-td-1.md |
| read first | tests/acceptance/W2-170/README.md, tests/acceptance/W2-170/w2_170_world.py (`HERE`, `TRUE_HOME`, `TRUE_SETS`, `TRUE_RUNS`, `at_or_under`), tests/acceptance/W2-170/w2_170_open_log.py, tests/acceptance/W2-170/conftest.py |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-820, DEC-866, DEC-966, DEC-1101 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The revision (KPI S1, guarded by F1 and F2)
- In `test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders` only: an open of a path at or
  under **the repository under test's own root** (the checkout the test file sits in: its source, tests and stores) is
  not a runs-folder or sets-root open, wherever that root lives. Every other path at or under `W.TRUE_SETS` or
  `W.TRUE_RUNS` still lands in `reached` and fails the case.
- Derive the repository's root from the test file's own location (e.g. from `W.HERE`), not from the current directory
  (the case's children run with `cwd=world.work`, the planted repository) and not from an environment variable.
  Compare in one normal form on both sides (the log's paths and the root), so a symlinked or `..` spelling cannot slip a
  true-root path past the filter nor keep a repository path in it. State your choice in a comment.
- Guard against loosening (F1): assert, in the case, that the repository root is not the true home, `TRUE_RUNS` or
  `TRUE_SETS` themselves nor an ancestor of them (an exclusion that covered a whole true root would pass everything).
- Keep everything else of the case as it is (its planted home, its three runs, its two closing asserts). No other case
  changes; no case removed, skipped or marked. The diff of the test file shows only the exclusion and its guard (F2).
- Update README.md where it describes F3's file-access log (around its lines 46-52 and the F3 row of the KPI table) with
  one sentence: the repository's own root is excluded, and why (the nightly's clone under `~/gov-os-runs`).
- The hidden-half and held-out rules hold (DEC-820 (b), (d)): the case keeps planting its own sets root and runs folder;
  you never open the true `~/gov-os-eval` or `~/gov-os-runs` (nor list them).

## Show it (evidence in your return)
1. The case green in your tree (a clone outside `~/gov-os-runs`), and the whole folder green.
2. F1 without touching the true roots: in a scratch copy of the case under
   /home/usain/gov-os-worktrees/W2-179-tests/.gov-runtime/scratch/ (never committed), append to the log entries one
   synthetic line naming `<TRUE_RUNS>/W2-179/planted-outside/x.txt` (a string only: nothing is opened or created there)
   and show the revised filter fails the case; and one naming a file under the repository root, shown let through.
   Also show the filter's verdict for a repository root that lives under `TRUE_RUNS` (e.g. by calling your exclusion
   with a substituted root string `<TRUE_RUNS>/W2-00/nightly/x`): its own files let through, `<TRUE_RUNS>/W2-179/other/f`
   still reached. The lead runs the case in a real clone under ~/gov-os-runs/W2-179/ after your return; you do not.
3. `git diff --stat` and `git diff --name-only` against your base (3eeb5cb2e): only the two allowed paths.

## Rules
- Every pytest run goes through the heavy-slot gate, one folder per run, TMPDIR outside the repository:
  `env HOME=/home/usain/gov-os-worktrees/W2-179-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-179-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-170 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (a single file or `-k` selection in the same form while you work).
- One-line commands only; anything longer in a script under /home/usain/gov-os-worktrees/W2-179-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only, with the Rewrite-Reason (DEC-866):
  `git commit -m "<subject>" --trailer "Task: DAEO-c9n8" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-820, DEC-866, DEC-966, DEC-1101" --trailer "Rewrite-Reason: DEC-866, W2-179 (DAEO-c9n8): W2-170's F3 case counted the repository's own files as runs-folder opens in the nightly's clone under ~/gov-os-runs" -- tests/acceptance/W2-170/test_w2_170_s4_map.py tests/acceptance/W2-170/README.md`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines; the F1 scratch results) / tests / discoveries /
risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers)
and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket and this brief do not settle: write your reading into the case's comment and name it in
`unresolved`.
