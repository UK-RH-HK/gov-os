# Independent test designer: W2-61h (DAEO-h2k3) — h10's retirement off the callers floor (DEC-1171 (2), the owner's (b))

You are a fresh independent test designer. Headless: only your last message is read.

## Where you work
- Your tree (write here only): /home/usain/gov-os-worktrees/W2-61h-c39-tests, branch w2/W2-61h-c39-tests.
- Files you may change: `tests/acceptance/W2-61h/w2_61h_support.py`, `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py`
  (only the S3 case's floor line and its docstring/message, if the floor must be computed there) and
  `tests/acceptance/W2-61h/README.md`. Nothing else.
- Scratch: /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/ ; use the sandbox's own `$TMPDIR`.

## The decision you implement
- DEC-1171 (2) in `docs/DECISION_REGISTER.md` (grep `### DEC-1171`, read item (2) only): h10 is retired from W2-61h's
  hidden half, so the half counts 39 (already done at `00a2f3e25`: `HIDDEN_COUNT = 39`).
- **The owner's answer (2026-11-13), option (b), to be recorded as DEC-1175 (not yet in the register; name it
  "DEC-1175 (to be recorded)" in comments):** h10's R5 category is **callers** (given by the owner's operator from h10's
  retirement reason line). The callers floor drops by one with the count. The CTO confirms the callers floor is **two
  short** of R5's stated minimum: one for the operator's earlier accepted shortfall (`R5_SHORT`, DEC-1069) and one for
  h10's retirement.

## What to change (three things; no other case changes)
1. In `tests/acceptance/W2-61h/w2_61h_support.py`, beside `R5_SHORT` (line ~57), add
   `R5_RETIRED = {"callers": 1}` with a comment naming DEC-1171 (2) and the owner's (b) (DEC-1175, to be recorded).
2. Make S3's floors honour it: in `test_s3_the_hidden_40_spread_as_r5_s_quotas_state` (`test_w2_61h_hidden_form.py`
   line ~113) the floor for each category is `R5_QUOTAS[name] - R5_SHORT.get(name, 0) - R5_RETIRED.get(name, 0)`, so
   callers' floor is 2 (4 less 2), decision's 5 and code-paraphrase's 2 as before, and every other category at its full
   minimum. The failure message should still show counts per category only, and say which floors carry a reduction.
   Keep the test function's name as it is (the ticket's KPI lines cite it).
3. Keep the comments about the twelve categories' sum true: R5's twelve minimums sum to 40; less h10's retired place
   the half's minimums sum to 39 (matching `HIDDEN_COUNT`). Say so where the sum is stated.
4. README.md: the S3 row and the "DEC-1171 (2)" section (lines ~33 and ~72-77) still say change 2 "waits" on h10's
   category; make them state the change as made (`R5_RETIRED = {"callers": 1}`, callers' floor two short: the accepted
   shortfall and h10's retirement), citing DEC-1171 (2) and the owner's (b) (DEC-1175, to be recorded). Name no hidden
   question, answer or gold path; the category word "callers" is given by the owner and may be written.

No other case changes or loses its point. Do not touch the visible cases.

## Check your change
Run the visible side (the hidden-form module skips without `GOV_EVAL_SETS_ROOT`; never set it to anything real):
```
mkdir -p /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-61h-c39-tests && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39-tests/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Every pytest through heavy_slot.sh. A resource gate's refusal is a wait, not a refusal.
Then show the S3 change works on a throwaway sets root of **synthetic** files under `$TMPDIR` only (never
`/home/usain/gov-os-eval`): plant 39 files that pass every other hidden case's form (copy the shape the module expects;
earlier designers did this, see README's record), with callers at 2 and decision 5 and code-paraphrase 2 → S3 green;
callers at 1 → S3 red; decision at 4 → S3 red. Run only `test_w2_61h_hidden_form.py` against it with
`GOV_EVAL_SETS_ROOT=<that throwaway root>` (other hidden cases may be red on a synthetic plant for reasons of their own,
e.g. S4/S5; report S3's result and the counts). Report counts only.

## Commit
Your paths only; trailers in one final paragraph (no blank line between them):
```
git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests commit -m "<subject>" -m "Rewrite-Reason: DEC-1171 (2), h10 retired (callers), the owner's (b)" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1069, DEC-954, DEC-957" -- tests/acceptance/W2-61h/w2_61h_support.py tests/acceptance/W2-61h/test_w2_61h_hidden_form.py tests/acceptance/W2-61h/README.md
```
(DEC-1171 and DEC-1175 are not in the ticket's `sources:`: name them in `discoveries`, never in `Implements:`.) Check with
`git log -1 --format='%(trailers)'` that Task, Role, Implements and Rewrite-Reason read as trailers. If
`Rewrite-Reason` does not read as a trailer as a separate `-m`, pass it as `--trailer "Rewrite-Reason: ..."` instead.

## Rules
- **Never open `/home/usain/gov-os-eval` or any hidden or retired-hidden folder; read no hidden content.**
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No hidden question, answer or gold path in any commit message, file, log or your return.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context` in the sandbox); search again once, in other words.

## Return (your last message; nothing else is read)
Twelve labelled lines, "none" where nothing: task / status (DONE or PACKAGES) / work_completed / files_changed /
evidence / tests (counts, and the throwaway-root counts) / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then `commits: <hash12> <subject>` and `guard_refusals: none | - <form> | <reason>`.
PACKAGES: each as question, options with cost, recommendation, confidence, what it blocks.

## The ticket's context packet (gov context DAEO-h2k3 --role independent-test-designer --budget 30000)

```json
