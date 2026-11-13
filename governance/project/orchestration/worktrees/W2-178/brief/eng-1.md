Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-178/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-1: engineer for DAEO-7oxm (W2-178), profile FULL, class C2

You implement ticket DAEO-7oxm (W2-178): the auditor's copy of a set leaves out its dropped questions. An independent
test designer writes the acceptance tests (tests/acceptance/W2-178/) in parallel; you never read them (the guard refuses
the counterpart's work). Write your own unit tests as you go (test first).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-178 |
| branch | w2/W2-178 |
| allowed paths | governance/project/orchestration/tools/indep_launch.py, tests/unit/orchestration/test_w2_178*, docs/changes/W2-178-evidence.md |
| ticket (read it first; KPI lines S1 and F1-F3 are the spec) | /home/usain/gov-os-worktrees/W2-178/.tickets/DAEO-7oxm.md |
| base (the claim commit, also the merge-base with w2/integrate; holds W2-173's merge 6a5d5321b) | `03393ee51` |
| W2-170's Interface (the rule's origin) | governance/project/orchestration/packages/MEMORY-AUDIT-1.md (grep `dropped`: lines ~134-143 and ~335-338) |
| existing unit tests that must still pass unchanged | tests/unit/orchestration/test_w2_149_indep_launch.py, test_w2_149_setup_a.py, test_w2_173_indep_launch.py; tests/acceptance/W2-149/, tests/acceptance/W2-173/ |
| the sources (read by id in docs/DECISION_REGISTER.md; grep it only by id) | DEC-1101 (2), DEC-820 (b), (d), DEC-1052, DEC-1120 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## The change (the ticket's S1; the lead's reading where marked)
- `plan_inputs(kind, rnd, root, set_name, audit)` (indep_launch.py ~line 756) stages a set's files with `set_copies()`:
  every plain file under `<root>/fixtures/evaluation/<set>/hidden/`, recursively, to `input/set/<rel>`.
- **New, auditor only:** for `kind == "auditor"`, leave out every file whose path relative to `hidden/` lies under the
  folder `dropped/` (first path component `dropped`, any depth below it). Every other file (other subfolders included,
  e.g. `hidden/sub/q03.yaml`) is staged exactly as today. A plain FILE named `hidden/dropped` (not a folder) is not
  "under the folder": lead's reading, keep it staged; say so in the evidence.
- **Unchanged:** the writer (round 2) and checker copies, including their `dropped/` files; every existing refusal
  (a link anywhere under `hidden/` still refuses 10 `input`, as `plain_files` does today, the dropped folder included);
  the set-up A flows (the overlap auditor goes through `plan_sgx`, not here). Lead's reading: if the auditor's set is
  empty after the exclusion, refuse 10 `input` exactly as an empty set does today.
- Update the module docstring with one short paragraph naming this rule (W2-178; W2-170's Interface; DEC-1101 (2)).
  No other change to the script: exit codes, counts, WALL.json shape, file budget rules keep their meaning. The
  counts schema, the stop word and the delivery checks are W2-173's and are non-goals here.
- Expected size: about 40 lines with tests (est_loc 40).

## Rules
- Unit tests in tests/unit/orchestration/test_w2_178_indep_launch.py: planted sets roots under tmp_path, with their
  own `hidden/dropped/` files; never the real sets root (`~/gov-os-eval`), ~/gov-os-runs, ~/.claude, any hidden half,
  the held-out material, or a real walled session (DEC-820 (b), (d)). Do not write the real root's path in your tests
  (F2 greps for it). Cover: auditor without dropped files and with every other file byte-identical; a nested
  `dropped/x/` file; a non-dropped subfolder still staged; checker and writer round 2 still staging `dropped/`.
- Every pytest goes through the heavy-slot gate, one folder or file set per run, TMPDIR outside the repository:
  `env HOME=/home/usain/gov-os-worktrees/W2-178/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp/w2-178-eng PYTHONPATH=/home/usain/gov-os-worktrees/W2-178/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (make /tmp/w2-178-eng and the empty-home folder first). Before you return, run your test file,
  tests/unit/orchestration/test_w2_149_*.py and test_w2_173_*.py, tests/acceptance/W2-149 and tests/acceptance/W2-173
  this way and report each summary line.
- Write docs/changes/W2-178-evidence.md: the KPI lines, what implements each (function and lines), the test that shows
  it, your readings above, and `git diff --stat 03393ee51 -- governance/project/orchestration/tools/`.
- Commit in small batches (the lead merges the tests between them), your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-7oxm" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-820, DEC-1052, DEC-1120" -- <your paths>`
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-178/.gov-runtime/scratch/;
  literal paths as write targets. Never touch .gov-runtime/scratch/lead/.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
