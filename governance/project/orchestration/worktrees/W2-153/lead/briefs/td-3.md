# W2-153 — check and commit the routed line's README map (left uncommitted), the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer (class C2) working under **W2-153** (`.tickets/DAEO-8s85.md`, read-only at
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-8s85.md`).

## Where it stands
`tests/acceptance/W2-153/test_w2_153_routed.py` covers the ticket's sixth success line (routed from W2-33,
DEC-1156 (3)); commit `8f7affc8a81d`. `gov accept W2-153` reported its cases as unmapped, because the README's
"Routed line" table had no KPI column. The previous designer edited `tests/acceptance/W2-153/README.md` (a `KPI line`
column holding `S6`, and "success line 6, `S6`" in the section's first paragraph) but ended its session before
committing: the edit is **uncommitted in your worktree** (`git diff` shows it). That session ended while its pytest
waited for a heavy slot in the background.

## Do
1. Read the uncommitted diff. Keep it if it is right; correct it if not (only that README's routed section).
2. Check with `gov accept`'s reader (`src/gov/accept/runner.py`, `parse_map`, lines 66-191): in a child
   `python3 -c` with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src`, `parse_map` on the README returns
   a `success-6` entry listing the routed file's tests, and the other lines' entries equal those from the committed
   README (`git show HEAD:tests/acceptance/W2-153/README.md`).
3. Run the folder once, **in the foreground** (form below). The slot tool may queue for some minutes: wait for it in
   that same call (Bash timeout 600000 ms; if it times out, run the same command again in the foreground). Never run
   it in the background, never use Monitor, and never end your session while a command is still running.
4. Commit that file (form below). No test changes.

## Where you work, rules, return
- Worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`. Write only
  `tests/acceptance/W2-153/README.md`.
- Pytest form: `env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-153 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
  (if the slot tool cannot run in your sandbox, run the same pytest without it and say so).
- No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. One simple command per Bash call. No merge inside the sandbox.
  Refused twice for the same call: stop and say so; never work around a refusal.
- **Commit** on `w2/W2-153-tests`, only that file, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), the map before and after (line → number of items), the
  folder's counts, the commit and `TESTS-READY <hash12>`.
