# Brief td-1: independent test designer for DAEO-7oxm (W2-178), profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-7oxm (W2-178): the auditor's copy of a set leaves out its
dropped questions. You write the acceptance tests from the ticket's KPI lines, before the engineer's code exists. You
never read the engineer's work on this ticket (its branch w2/W2-178 after this brief, its unit tests
`tests/unit/orchestration/test_w2_178*`, its evidence `docs/changes/W2-178-evidence.md`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-178-tests |
| branch | w2/W2-178-tests |
| your allowed paths | tests/acceptance/W2-178/** |
| ticket (read it first; KPI lines S1 and F1-F3 are the spec) | /home/usain/gov-os-worktrees/W2-178-tests/.tickets/DAEO-7oxm.md |
| the script under test (read its CLI, docstring, exit codes; test its behaviour, not its internals) | governance/project/orchestration/tools/indep_launch.py |
| the base (the script before this change; the ticket's claim commit, also the merge-base with w2/integrate) | `03393ee51` (holds W2-173's merge 6a5d5321b) |
| W2-149's and W2-173's acceptance tests: reuse their planted world (import their helpers, never copy-edit them) | tests/acceptance/W2-149/w2_149_support.py, tests/acceptance/W2-173/w2_173_support.py and their test_*.py files (W2-149's `World.plant` already plants a set `memory-verdict-3` with `hidden/q01.yaml`, `hidden/q02.yaml` and `hidden/sub/q03.yaml`, and `runs/audit-1/misses.jsonl`) |
| W2-170's Interface (the rule's origin) | governance/project/orchestration/packages/MEMORY-AUDIT-1.md (grep `dropped`: lines ~134-143 and ~335-338) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1101 (2), DEC-820 (b), (d), DEC-1052, DEC-1120 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words, then
answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The interface (as the ticket states it; the lead's reading where marked)
- A set's files are the plain files under `<sets root>/fixtures/evaluation/<set>/hidden/`; the script stages them into
  the wall at `input/set/<path relative to hidden/>` (writer round 2, checker, auditor; see `plan_inputs`' callers only
  through behaviour: build dry walls with `--dry` and a fixed `--seed`, and read the wall left in place).
- **S1 / F1 (new):** for `--kind auditor` (the memory auditor: `--set <set> --audit <audit>`), the wall's `input/set/`
  holds every file of the set EXCEPT those under `hidden/dropped/` (the whole subtree: `hidden/dropped/q07.yaml`,
  `hidden/dropped/x/q08.yaml`). Every other file (including files in other subfolders such as `hidden/sub/q03.yaml`)
  is there and byte-identical to its source. No path under `input/set/dropped/` exists in the auditor's wall.
- **S1 / F1 (unchanged):** a writer's (round 2) and a checker's wall built from the same planted set (dropped folder
  included) are byte-identical to the walls the base script (`03393ee51`'s indep_launch.py) builds from the same set
  with the same arguments and seed. The lead's reading: run the base script's copy (`git show 03393ee51:<path>` into
  your planted repository or tmp_path, however W2-149's world runs the script) and the head's on twin planted worlds;
  compare every file of the two walls byte for byte; a field that differs between two runs of the SAME script with the
  same seed (a time, a run id, a temporary path) is not a change: show that by running one script twice, and exclude
  only those fields, naming them in the test's docstring. Before this change a checker's wall DOES carry
  `input/set/dropped/...`; it must still carry them after.
- Lead's reading, not a KPI (do not test): an auditor's set whose every file is under `dropped/` refuses as an empty set
  does today. The set-up A overlap auditor (`--set tuning|held-out`) is a different path and out of scope.
- **F2:** every test plants its own sets root under pytest's tmp_path (W2-149's world does); one case greps the files of
  `tests/acceptance/W2-178/` for the real sets root's path (`gov-os-eval`, as `~/gov-os-eval` or `/home/usain/gov-os-eval`)
  and expects 0 lines (write that string in the test so that the test file itself does not match, e.g. by joining
  two halves).
- **F3:** `git diff --name-only <base>...HEAD` lists only paths matched by the ticket's allowed_paths plus
  `tests/acceptance/W2-178/**` (base: the merge-base with `w2/integrate`, else `03393ee51`). W2-173's
  `test_w2_173_unchanged.py` F4 case shows a form to reuse.
- Non-goals (do not test): the counts schema, the stop word and the delivery checks (W2-173).

## Rules
- Planted sets root, HOME and repository under pytest's tmp_path, and a stub `claude` on PATH; never the real sets root,
  ~/gov-os-runs, ~/.claude, any hidden half, the held-out material, or a real walled session (DEC-820 (b), (d)).
- Tests must be red now where the KPI is new (the auditor's copy without `dropped/`) and green where it holds today
  (the writer's and checker's walls unchanged, F2, F3). Run them and say which are red and why.
- Every pytest goes through the heavy-slot gate, one folder per run, TMPDIR outside the repository:
  `env HOME=/home/usain/gov-os-worktrees/W2-178-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp/w2-178-td PYTHONPATH=/home/usain/gov-os-worktrees/W2-178-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-178 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (make /tmp/w2-178-td and the empty-home folder first). Run W2-173's acceptance folder the same way once to confirm
  your imports break nothing.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-178-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-7oxm" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-820, DEC-1052, DEC-1120" -- tests/acceptance/W2-178`
- Keep the suite small and fast (dry walls, stubbed session; seconds per case).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket does not settle: write your reading into the test's docstring and name it in `unresolved`.
