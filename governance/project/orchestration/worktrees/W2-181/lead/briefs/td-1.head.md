# Brief td-1: W2-181 (DAEO-ywb5), independent test designer, revision of W2-157's F4 path case

You are the independent test designer (MR-3) for ticket DAEO-ywb5 (W2-181), profile LITE, class C1, class test-revision.
Work only in your worktree /home/usain/gov-os-worktrees/W2-181-tests, branch w2/W2-181-tests. No engineer exists on this ticket:
the revised test file is the whole deliverable.

## Allowed paths (write only these)
- tests/acceptance/W2-157/test_w2_157_nothing_else.py
- tests/acceptance/W2-157/README.md
Scratch (not committed): /home/usain/gov-os-worktrees/W2-181-tests/.gov-runtime/scratch/

## The job (KPI lines; the ticket file text is in the context bundle below)
- S1: `test_f4_the_branch_changes_only_the_tickets_allowed_paths` judges only W2-157's own branch. On any other branch,
  a merge queue candidate merge (a detached HEAD), w2/integrate itself or a clone's checkout, it is SKIPPED with its
  reason (the branch found, e.g. "this is the branch w2/W2-121c", or "detached HEAD"), never red. On `w2/W2-157` it
  judges as today (merge-base with w2/integrate, `git diff --name-only <base>...HEAD`, each path matched by the ticket's
  `allowed_paths` (the existing `allowed_paths()` reading of .tickets/DAEO-ozyt.md, comments dropped, fnmatch) or under
  `tests/acceptance/W2-157/`; the sanitised git env it uses today stays).
- F1: a change outside W2-157's paths on W2-157's own branch must still fail.
- F2: change nothing outside the two allowed paths.
- Non-goal: any other ticket's path case. Leave the S5 cases in the file untouched.

## The form to copy (read only)
W2-180 (DAEO-weh2) revised W2-170's F5 the same way. Read, with `git -C /home/usain/gov-os-worktrees/W2-181-tests show
w2/W2-180:tests/acceptance/W2-170/test_w2_170_f5_paths.py` (and `...:tests/acceptance/W2-173/test_w2_173_unchanged.py`):
- one judge function `judge_f4_paths(root)` that the real case calls with this tree's ROOT and the planted cases call
  with each planted repository; the branch is read from `root` (`git symbolic-ref -q HEAD`), never from the cwd or an
  environment variable;
- skips with the reason where w2/integrate does not resolve or the ticket file is absent (a plain clone);
- skip messages of the form `F4 judges only the branch w2/W2-157; this is the branch <b>: not judged here` and
  `F4 judges only the branch w2/W2-157; this is a detached HEAD: not judged here`;
- planted repositories under tmp_path (`git init`, an isolated HOME, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1,
  identity by `-c`, hooks off), w2/integrate holding a base commit with W2-157's ticket file copied from this tree, and
  the branch adding one path. Planted cases at least: (a) a check that the planted OUTSIDE path is outside W2-157's
  paths and INSIDE is inside; (b) branch `w2/W2-157` with OUTSIDE fails, naming the path; (c) `w2/W2-157` with INSIDE
  passes; (d) branch `w2/W2-121c` with OUTSIDE is skipped with "w2/W2-121c" in the reason; (e) a detached candidate
  merge (`--no-ff` of w2/W2-121c onto a detached w2/integrate; check it is detached and a two-parent commit) is skipped
  with "detached HEAD"; (f) `w2/integrate` itself is skipped with its reason. Choose OUTSIDE as a path in
  `src/gov/resources/` that is not W2-157's (W2-121c's area), INSIDE as e.g. `src/gov/resources/backstop.py`.
- Also update the F4 row of tests/acceptance/W2-157/README.md (the map's last row and anything that says F4 is judged
  on every branch) to say what the revised case does and that it is skipped off w2/W2-157.

## Expected outcome on your branch
On w2/W2-181-tests the real F4 case is SKIPPED (this is the branch w2/W2-181-tests); every planted case passes; the
rest of the folder is unchanged in outcome (W2-157's code is on the base, so the S/F cases are green there; a red that
also fails on w2/integrate's head is a shared base red: name it with that evidence, do not fix it).
Also show one mutation is caught: temporarily drop the branch check in a scratch copy and show case (d) or (e) goes red
(do this in scratch, never in the committed file).

## Rules
- Every pytest through the heavy slot, one folder per run, with TMPDIR outside the repository and outside ~/gov-os-runs:
  `env TMPDIR=/tmp/w2-181-td PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-181-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-181-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-157 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (create /tmp/w2-181-td and the empty-home folder first with mkdir -p; anything longer than one line goes in a script
  file under your scratch, run with bash).
- Search with Read and Grep (no `gov retrieve`, no `gov context` inside the sandbox); search again once in different
  words if the first search does not answer.
- No merge, no push, no edit of .tickets/ or the register. Do not read any engineer's work (there is none).
- Commit on w2/W2-181-tests, your paths only, in this form:
  git commit -m "W2-181 (DAEO-ywb5): W2-157's F4 case judges only w2/W2-157, skips with its reason elsewhere; planted cases" --trailer "Task: DAEO-ywb5" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-866, DEC-253, DEC-966, DEC-989" --trailer "Rewrite-Reason: DEC-866, W2-181 (DAEO-ywb5): W2-157's F4 case judged every branch against W2-157's own paths, red on the next ticket in src/gov/resources/ and the queue's candidate merge (DECIDED-NOT-DONE row 171)" -- tests/acceptance/W2-157/test_w2_157_nothing_else.py tests/acceptance/W2-157/README.md
- Refused twice for the same call: stop and report it; never work around a refusal.

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing):
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests`: the folder's counts (passed/skipped/failed), each planted case's outcome, the real F4 case's skip reason
as printed (`-rs`), and the mutation's result. In `evidence`: the commit hash and `git diff --name-only HEAD~1`.

## Context bundle (gov context DAEO-ywb5 --role independent-test-designer)
```json
