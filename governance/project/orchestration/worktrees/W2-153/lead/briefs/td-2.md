# W2-153 — the routed line's README map, read by `gov accept` (one missing item), the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer (class C2) working under **W2-153** (`.tickets/DAEO-8s85.md`, read-only at
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-8s85.md`). The previous designer added
`tests/acceptance/W2-153/test_w2_153_routed.py` and a "Routed line" section in `tests/acceptance/W2-153/README.md`
(commit `8f7affc8a81d`) for the ticket's sixth success line (routed from W2-33, DEC-1156 (3)). The cases pass.

## The one missing item
`gov accept W2-153` reports the routed file's 71 passed and 18 skipped cases as **unmapped**: no line `success-6`.
The routed section's table has a `Clause` column but no KPI column, so `gov accept`'s README reader
(`src/gov/accept/runner.py`, `parse_map` and `line_names`, lines 66-191; read it) maps none of its rows. The folder's
main table names lines as `S1`, `S2`, ... in a `KPI line` column, and those are read.

**Do:** make the routed section's table map its rows to the sixth success line in the form the reader reads (for
example a first column `KPI line` holding `S6`, keeping the clause in its own column), and say in the section's first
paragraph that this is success line 6 (`S6`). Change no test and no other row. Check it yourself: in a child
`python3 -c` with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src`, `gov.accept.runner.parse_map` on the
README must return a `success-6` entry listing the routed file's tests, and the other lines' entries unchanged
(compare with the map before your edit). Then run the folder once (form below) and report its counts.

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
