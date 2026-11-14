# Narrow independent check: W2-61h (DAEO-h2k3) — the S4/F3 revision only (DEC-1178 (1), DEC-1154)

You are a fresh independent auditor, read-only. Headless: only your last message is read. You write nothing in any
worktree; you may use the sandbox's own `$TMPDIR` for throwaway files. This is a narrow check of one revision, not a
review round (DEC-1010, DEC-1154).

## What you check (only this)
Tree: /home/usain/gov-os-worktrees/W2-61h-c39, branch w2/W2-61h-c39, head **dda647a49eaa51782442b7c4203bf70de487809d**
(probe exactly this commit; confirm with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 rev-parse HEAD`).

The change under check, in `tests/acceptance/W2-61h/` only: the test designer's commit `3bc8fe6d15b6` (merged
`dda647a49`), files `w2_61h_support.py`, `test_w2_61h_hidden_form.py`, `test_w2_61h_visible_new.py`, `README.md`.
See it with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 diff e0381969c dda647a49 -- tests/acceptance/W2-61h/`.
Everything else in the tree is out of scope.

Judge against:
1. **DEC-1178 (1)** in `docs/DECISION_REGISTER.md` (grep `### DEC-1178`, item (1) only).
2. **The ticket's reworded S4 success line and F3's failure line** ("A gold source that does not hold its answer at its
   own commit", the 4th failure line) in `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-h2k3.md`
   (read-only), and its last paragraph, "Reopened 2026-11-14".
3. **The order's four outcomes**, hidden and visible cases alike:
   (1) each gold source judged at its own commit (the path a file there; the heading or lines a span there that holds
   the answer); (2) at HEAD, a cited block that moved unchanged is no fault; (3) a cited block whose lines changed at
   HEAD is listed by question id and entry number only, never failed, never blocking a close, the list the case's
   output with file names and entry numbers only, never a question, answer, path or span text; (4) a source that does
   not hold its answer at its own commit stays red.

Questions to answer: Do the revised cases give a moved block, a changed block and a missing answer each the outcome
above, and a control a pass? Does any case, message, warning or README line leak a question, answer, category, gold
path or span text (file names and entry numbers only)? Does the hidden-form module still skip without
`GOV_EVAL_SETS_ROOT` and under a measured `GOV_ROLE` (the path map's `measures.roles`)? Does any other case change or
lose its point, and are the test functions' names kept? Is the planted visible case a single case that runs in the
full run (`tests/optin-lifted-breadth.txt` keeps only a parametrised function's first row)? Is the list visible in the
walled command's own output as the README states it? Are the commits' trailers in one final block
(`Task: DAEO-h2k3`, `Role: independent-test-designer` and `Rewrite-Reason: DEC-1178 (1)` on the designer's commit,
`Role: orchestrator` on the merge)?

You may run the visible side (the hidden-form module skips without `GOV_EVAL_SETS_ROOT`):
```
cd /home/usain/gov-os-worktrees/W2-61h-c39 && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=$TMPDIR PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Every pytest through heavy_slot.sh (a resource gate's refusal is a wait). You may plant a throwaway sets root under
`$TMPDIR` (a `fixtures/evaluation/memory-retrieval/hidden/` folder of planted YAML questions citing real commits and
real non-evaluation files of this repository, with a copy of `governance/project/path-map.yaml` under
`governance/project/`) and run only `test_w2_61h_hidden_form.py -k s4 -rA` against it with
`env -u GOV_ROLE -u GOV_TICKET GOV_EVAL_SETS_ROOT=<that throwaway root>`; report outcomes and counts only. (For a moved
and a changed block, `src/gov/retrieval/measure.py` at its first commit `289b9314a` against HEAD has both.)

## Rules
- **Never open the evaluation sets' root (`gov-os-eval` under the home folder) or any hidden, retired-hidden or
  memory-verdict folder; read no hidden content.** Never set `GOV_EVAL_SETS_ROOT` to anything but a throwaway root you
  planted.
- Read-only: write nothing in any worktree or the main tree; no commit, no merge.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context`); search again once, in other words.

