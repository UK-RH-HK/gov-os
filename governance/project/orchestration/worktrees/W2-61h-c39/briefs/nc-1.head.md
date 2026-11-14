# Narrow independent check: W2-61h (DAEO-h2k3) — the hidden count (39) and S3's floor change only

You are a fresh independent auditor, read-only. Headless: only your last message is read. You write nothing in any
worktree; you may use the sandbox's own `$TMPDIR` for throwaway files. This is a narrow check, not a review round
(DEC-1010).

## What you check (only this)
Tree: /home/usain/gov-os-worktrees/W2-61h-c39, branch w2/W2-61h-c39, head **82b5cf198** (probe exactly this commit;
confirm with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 rev-parse HEAD`).

The change under check, in `tests/acceptance/W2-61h/` only (`w2_61h_support.py`, `test_w2_61h_hidden_form.py`,
`README.md`):
- the count change, `94aa1debc` (merged `00a2f3e25`): `HIDDEN_COUNT` 40 -> 39;
- the floor change, `5cd76ee9d` (merged `82b5cf198`): `R5_RETIRED = {"callers": 1}` beside `R5_SHORT`, S3's floors
  `R5_QUOTAS[name] - R5_SHORT.get(name, 0) - R5_RETIRED.get(name, 0)`, the sum comments, the README lines.
See them with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 diff 31eab2103 82b5cf198 -- tests/acceptance/W2-61h/`.
(`440bc9a6d`, q22's re-anchor, sits in the same range and is **out of scope**: do not judge it.)

Judge against:
1. **DEC-1171 (2)** in `docs/DECISION_REGISTER.md` (grep `### DEC-1171`, item (2) only): h10 retired from the hidden
   half; the count case reads 39 until the walled writer's replacement brings it back to 40; the count case revised by
   a test designer under this item.
2. **The owner's answer of 2026-11-13, option (b)** (to be recorded as DEC-1175; not yet in the register, so judge
   against this text): "h10's category is **callers**, given by the owner's operator from h10's retirement reason line.
   The callers floor drops by one with the count. The CTO confirms the floor two short there: the operator's earlier
   accepted shortfall and h10's retirement each take one place." The order to the test designer: add
   `R5_RETIRED = {"callers": 1}` beside `R5_SHORT` in `w2_61h_support.py`; make S3's floors honour it, so the callers
   floor is two short of the README's stated minimum; keep the twelve categories' sum comment true at 39; no other case
   changes.
3. The ticket's S1 and S3 KPI lines (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-h2k3.md`, read-only),
   as far as they bear on the count and the floors.

Questions to answer: Is `HIDDEN_COUNT` 39 with a true comment? Is `R5_RETIRED` exactly `{"callers": 1}` beside
`R5_SHORT`? Do S3's floors come out as callers 2, decision 5, code-paraphrase 2 and every other category at its full
minimum, with nothing else loosened? Are the sum comments true (twelve minimums 40; less h10's place 39)? Does any other
case change or lose its point (the test functions' names kept)? Does any output or file in the change print or name a
hidden question, answer or gold path (the category word "callers" is the owner's and may appear)? Are the commits'
trailers (`Task: DAEO-h2k3`, `Role: independent-test-designer` on the designer's commits, `Role: orchestrator` on the
merges) in one final block?

You may run the visible side (the hidden-form module skips without `GOV_EVAL_SETS_ROOT`):
```
cd /home/usain/gov-os-worktrees/W2-61h-c39 && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Every pytest through heavy_slot.sh (a resource gate's refusal is a wait). You may plant a throwaway sets root of
**synthetic** files under `$TMPDIR` and run only `test_w2_61h_hidden_form.py` against it with
`GOV_EVAL_SETS_ROOT=<that throwaway root>`, to see S3 green at the floors and red one below; report counts only.

## Rules
- **Never open the evaluation sets' root (`gov-os-eval` under the home folder) or any hidden or retired-hidden folder;
  read no hidden content.** Never set `GOV_EVAL_SETS_ROOT` to anything but a throwaway root you planted.
- Read-only: write nothing in any worktree or the main tree; no commit, no merge.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context`); search again once, in other words.

