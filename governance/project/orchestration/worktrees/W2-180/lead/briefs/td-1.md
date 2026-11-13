# Brief td-1: independent test designer, test revision, for DAEO-weh2 (W2-180), profile LITE, class C1

You are the independent test designer (MR-3) for ticket DAEO-weh2 (W2-180): a revision of one existing acceptance case of
W2-170 (DAEO-61vm, closed). No engineer works on this ticket; no product code changes.

## The defect (facts)
`tests/acceptance/W2-170/test_w2_170_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows` diffs
whatever branch the suite runs on against its merge-base with `w2/integrate` and checks every changed path against
W2-170's own `allowed_paths` (from `.tickets/DAEO-61vm.md`). On any other ticket's branch it is wrong: W2-171
(DAEO-k1e2) rightly changes `src/gov/memaudit/` files W2-170's paths do not list, so the case is red on `w2/W2-171`,
and the merge queue's candidate merge of W2-171 into `w2/integrate` (a detached HEAD) would be red too, attributed to
W2-171's batch, and its land refused. The CTO's ruling (PKG-W2-171-F5-1, in `.tickets/DAEO-k1e2.md` under its heading):
this ticket makes the case judge only W2-170's own branch.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-180-tests |
| branch | w2/W2-180-tests (base 8930dce6c) |
| your allowed paths | tests/acceptance/W2-170/test_w2_170_f5_paths.py, tests/acceptance/W2-170/README.md |
| ticket (KPIs S1, F1, F2) | /home/usain/gov-os-worktrees/W2-180-tests/.tickets/DAEO-weh2.md |
| the context bundle (`gov context` for your role) | /home/usain/gov-os-worktrees/W2-180/.gov-runtime/scratch/lead/briefs/ctx-td-1.md |
| read first | tests/acceptance/W2-170/test_w2_170_f5_paths.py, tests/acceptance/W2-170/README.md (its F5 bullet and the F5 row of the KPI table), tests/acceptance/W2-170/conftest.py, tests/acceptance/W2-170/w2_170_world.py (`TREE`), src/gov/close/select.py (`match`) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-866, DEC-253, DEC-966, DEC-989 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The revision (KPI S1, guarded by F1 and F2)
- The case judges **only on W2-170's own branch**: HEAD is the branch `w2/W2-170` (read the checked-out branch, e.g.
  `git symbolic-ref --short -q HEAD`, of the repository the test file sits in, `W.TREE`; never the current directory or an
  environment variable). On it, the case judges exactly as today (same base, same diff, same `allowed_paths` plus
  acceptance folder, same `match`, same assert).
- On **any other checkout** it is **skipped with its reason named** (the branch it found, or "detached HEAD"), never red
  and never passed silently: another ticket's branch (`w2/W2-171`), the merge queue's candidate merge (a detached HEAD
  at a merge of `w2/W2-171` into `w2/integrate`), `w2/integrate` itself, the nightly's clone (whatever it has checked out).
  Keep today's two skips (no `w2/integrate` reference, no ticket file), with their reasons.
- Make the judgement testable on planted repositories: put the case's logic in one function of the same file that takes
  the repository root (and reaches the skip and the assert itself, e.g. by `pytest.skip` and `assert`), and have the
  real case call it with `W.TREE`. The planted cases must exercise that same function, not a copy.
- **Planted cases (S1's verify, F1)**, in the same file, each in its own `git init` repository under `tmp_path`
  (TMPDIR outside the repository), with `w2/integrate` holding a base commit and `.tickets/DAEO-61vm.md` (copy the real
  one from `W.TREE`, so the paths are W2-170's), and one commit changing a path outside W2-170's `allowed_paths` (e.g.
  `src/gov/memaudit/outside_w2_170.py` if that is outside them; check with `match`):
  1. that change on a branch named `w2/W2-170` **fails** the judgement (an `AssertionError` naming the path) (F1);
  2. the same change on a branch named `w2/W2-171` **skips** with the reason;
  3. a **detached** candidate merge of `w2/W2-171` into `w2/integrate` (`git checkout --detach w2/integrate`, then
     `git merge --no-ff w2/W2-171`) **skips** with the reason;
  4. on `w2/integrate` it **skips**;
  and a pass control: a change only inside W2-170's paths on `w2/W2-170` passes.
  Set the planted git's identity per command (`-c user.name=... -c user.email=...`) and keep the planted repositories
  free of the true home's git config effects you depend on (no signing, no hooks).
- Keep the docstring true: rewrite it for the branch scope. No other case changes; no case removed or marked; no
  file outside your two paths (F2).
- README.md: update the F5 bullet ("How the tests reach the code under test") and the F5 row of the KPI table to say the
  case judges only on `w2/W2-170` and skips with its reason elsewhere, and list the planted cases; add a short
  "Revision (W2-180, DAEO-weh2)" paragraph naming the reason (DEC-866). Keep the rest of the README as it is.

## Show it (evidence in your return)
1. The planted cases: their outcomes (1 fails as expected inside the case, i.e. the planted cases themselves pass by
   asserting the judgement's fail or skip), and the real case's outcome in your tree (`w2/W2-180-tests`: skipped, with
   the reason line from `-rs`).
2. The whole folder: `tests/acceptance/W2-170` green except the real F5 case's skip (state the counts).
3. `git diff --stat` and `git diff --name-only 8930dce6c...HEAD`: only the two allowed paths.

## Rules
- Every pytest run goes through the heavy-slot gate, one folder per run, TMPDIR outside the repository and outside
  ~/gov-os-runs:
  `env HOME=/home/usain/gov-os-worktrees/W2-180-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-180-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-170 -q -rs -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (a single file or `-k` selection in the same form while you work). Make the empty-home folder first
  (`mkdir -p /home/usain/gov-os-worktrees/W2-180-tests/.gov-runtime/scratch/empty-home`).
- One-line commands only; anything longer in a script under /home/usain/gov-os-worktrees/W2-180-tests/.gov-runtime/scratch/.
  Literal paths only as write targets. No test, class, parameter id or file name holds `real`, `green_here` or `time_limit`.
- Commit your paths only, with the Rewrite-Reason (DEC-866):
  `git commit -m "<subject>" --trailer "Task: DAEO-weh2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-866, DEC-253, DEC-966, DEC-989" --trailer "Rewrite-Reason: DEC-866, W2-180 (DAEO-weh2): W2-170's F5 case judged every branch against W2-170's own paths, red on W2-171's branch and the queue's candidate merge (PKG-W2-171-F5-1)" -- tests/acceptance/W2-170/test_w2_170_f5_paths.py tests/acceptance/W2-170/README.md`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines; the skip reason; the diff names) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket and this brief do not settle: write your reading into the case's comment and name it in
`unresolved`.
