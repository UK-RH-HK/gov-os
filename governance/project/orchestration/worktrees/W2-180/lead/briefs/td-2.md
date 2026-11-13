# Brief td-2: independent test designer, test revision batch 2, for DAEO-weh2 (W2-180), profile LITE, class C1

You are the independent test designer (MR-3) for ticket DAEO-weh2 (W2-180), batch 2: a revision of one existing
acceptance file of W2-173 (DAEO-qz4p). No engineer works on this ticket; no product code changes.

## Where it stands
Batch 1 (another designer, commit e3ff31fc5, already merged) made W2-170's F5 case
(`tests/acceptance/W2-170/test_w2_170_f5_paths.py`) judge only on the branch `w2/W2-170` and skip with its reason on any
other checkout, through one function `judge_f5_paths(root)` and six planted cases. Read that file as the model. The CTO
then widened the ticket (07:35, section "Widened" of the ticket, and its `allowed_paths`): W2-173's
`tests/acceptance/W2-173/test_w2_173_unchanged.py` has the same any-branch form. Its `branch_names()` diffs whatever
branch the suite runs on against the merge-base with `w2/integrate` (else the fallback `dac438772`), and
`test_f3_...` and `test_f4_...` (failure lines 3 and 4) judge those names against W2-173's forbidden list and its
`allowed_paths`. On W2-178's branch (DAEO-7oxm, which changes `indep_launch.py`) and on the merge queue's candidate merge
of it, F4 would be red, attributed to W2-178's batch. This morning the queue already ejected W2-121 and W2-179 on
W2-170's F5 for the same reason.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-180-tests |
| branch | w2/W2-180-tests (base ac906bda8, which holds batch 1 and the widened ticket) |
| your allowed paths (this batch) | tests/acceptance/W2-173/test_w2_173_unchanged.py, tests/acceptance/W2-173/README.md |
| ticket (KPIs S1, F1, F2; section "Widened") | /home/usain/gov-os-worktrees/W2-180-tests/.tickets/DAEO-weh2.md |
| the context bundle | /home/usain/gov-os-worktrees/W2-180/.gov-runtime/scratch/lead/briefs/ctx-td-1.md |
| read first | tests/acceptance/W2-173/test_w2_173_unchanged.py, tests/acceptance/W2-173/w2_173_support.py (`TICKET_ID`, `W2`, `BASE_FALLBACK`, `support`), tests/acceptance/W2-173/conftest.py, tests/acceptance/W2-173/README.md (the S5/F3/F4 bullet and the F3, F4 rows), tests/acceptance/W2-170/test_w2_170_f5_paths.py (batch 1, the model) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-866, DEC-253, DEC-966, DEC-989 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The revision (S1 applied to W2-173, guarded by F1 and F2)
- `test_f3_the_branch_changes_no_template_path_map_guard_approved_list_or_set_up_a_brief` and
  `test_f4_the_branch_changes_only_the_ticket_s_paths` judge **only on W2-173's own branch**: HEAD is the branch
  `w2/W2-173` (read from the repository the test file sits in, `support.TREE`, by its full ref `refs/heads/...`; never the
  current directory or an environment variable). There they judge exactly as today (same base and fallback, same diff,
  same forbidden list, same allowed paths plus the folder and the ticket's own records, same `fnmatch`, same asserts).
- On **any other checkout** both are **skipped with the reason named** (the branch found, or "detached HEAD"), never red
  and never passed silently: another ticket's branch (`w2/W2-178`), the queue's candidate merge (a detached HEAD at a
  `--no-ff` merge of `w2/W2-178` into `w2/integrate`), `w2/integrate` itself, a clone's checkout.
- Make the judgement testable on planted repositories: the judgement in functions of the same file that take the
  repository root (and reach the skip and the assert themselves), the two real cases calling them with `support.TREE`;
  the planted cases call the same functions, not copies. The S5 case (`test_s5_...`) is not touched.
- **Planted cases**, in the same file, each its own `git init` repository under `tmp_path` (as batch 1's `_plant`: git
  identity per command, `commit.gpgsign=false`, `core.hooksPath=/dev/null`, a planted HOME, a planting failure raises):
  `w2/integrate` holds a base commit and a copy of W2-173's ticket file (`.tickets/DAEO-qz4p.md`, from `support.TREE`),
  then one commit adding a path outside W2-173's allowed paths (e.g. W2-178's kind of change; check it with the case's own
  `matched` that it is outside, and inside none of F3's forbidden globs unless you also plant an F3 case):
  1. on a branch `w2/W2-173`, F4's judgement **fails** naming the path (F1); and a forbidden path (e.g.
     `governance/project/path-map.yaml`) on `w2/W2-173` fails F3's judgement;
  2. the same change on `w2/W2-178` **skips** both with the reason;
  3. a **detached** candidate merge of `w2/W2-178` into `w2/integrate` **skips** both with the reason;
  4. on `w2/integrate` both **skip**;
  and a pass control: a change inside W2-173's allowed paths on `w2/W2-173` passes both.
- Keep the module docstring true (its "Readings" paragraph gains the branch scope). No other case changes; no case
  removed or marked; no file outside your two paths (F2). Do not touch W2-170's folder.
- README.md (W2-173's): update the S5/F3/F4 bullet and the F3, F4 rows of its KPI table: judged only on `w2/W2-173`,
  skipped with its reason elsewhere; list the planted cases; add a short "Revision (W2-180, DAEO-weh2)" paragraph naming
  the reason (DEC-866). Keep the rest as it is.

## Show it (evidence in your return)
1. The planted cases' outcomes, and the two real cases' outcomes in your tree (`w2/W2-180-tests`: skipped, the `-rs`
   reason lines).
2. The whole folders `tests/acceptance/W2-173` and `tests/acceptance/W2-170` (one run each): counts; any failure that is
   not yours, named with its output (do not fix it).
3. `git diff --name-only ac906bda8...HEAD`: only your two paths.

## Rules
- Every pytest run goes through the heavy-slot gate, one folder per run, TMPDIR outside the repository and outside
  ~/gov-os-runs:
  `env HOME=/home/usain/gov-os-worktrees/W2-180-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-180-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-173 -q -rs -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (a single file or `-k` selection in the same form while you work). Make the empty-home folder first if absent
  (`mkdir -p /home/usain/gov-os-worktrees/W2-180-tests/.gov-runtime/scratch/empty-home`).
- One-line commands only; anything longer in a script under /home/usain/gov-os-worktrees/W2-180-tests/.gov-runtime/scratch/.
  Literal paths only as write targets. No test, class, parameter id or file name holds `real`, `green_here` or `time_limit`.
- Commit your paths only, with the Rewrite-Reason (DEC-866):
  `git commit -m "<subject>" --trailer "Task: DAEO-weh2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-866, DEC-253, DEC-966, DEC-989" --trailer "Rewrite-Reason: DEC-866, W2-180 (DAEO-weh2): W2-173's branch-names cases (failure lines 3-4) judged every branch against W2-173's own paths, red on W2-178's branch and the queue's candidate merge (the ticket's Widened section)" -- tests/acceptance/W2-173/test_w2_173_unchanged.py tests/acceptance/W2-173/README.md`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines; the skip reasons; the diff names) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket and this brief do not settle: write your reading into the case's comment and name it in
`unresolved`.
