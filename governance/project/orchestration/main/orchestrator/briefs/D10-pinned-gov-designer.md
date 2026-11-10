# D-10's red-fix list: W1-46's kernel-hook cases need a `gov` on the runner's PATH (W2-20, DAEO-r30l)

You are a fresh **independent test designer**, launched under W2-20's ticket (`.tickets/DAEO-r30l.md`; its D-10
sweep made the launcher suites hermetic about the resource gate tonight, `e74b551bc`). This is the same kind of fix
for another dependency on the runner's environment.

## The red (the CTO's landing check after ACT-CLAUDE-COPIES-2; reproduced by the CTO's helper)
- 20 W1-46 cases run the kernel's template hook from a planted project with a scratch HOME. They fail with
  `decision=deny exit=2 … stderr='gov hook: no pinned gov at …'`. Examples: the research install cases (`uv add
  requests`, `uvx ruff check .`), `test_both_variables_reach_the_guard[…]`, the hard-link case, and the `uv run -w`
  cases. The full list is in the landing run's
  `.gov-runtime/scratch/orchestrator/log/landing-select/20261110-113051-2861407/verify/parallel.xml`.
- **Reproduced:** `tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through`
  gives 4 passed with the CTO's PATH (which has `~/.local/bin`, so `gov`), and 4 failed with `PATH=/usr/bin:/bin`.
- **The cause:** the kernel's hook line (W2-106, `template/governance/kernel/settings.json:13`) runs
  `g="$HOME/.local/bin/gov"; [ -f "$g" ] || g="$(command -v gov)" || { echo "gov hook: no pinned gov at $g"; exit 2; }`.
  The planted HOME has no `.local/bin/gov`, so the cases pass only when the runner's own PATH happens to hold the
  installed `gov`. The landing runs, and any cron or clean environment, have none.
- **The precedent:** W2-106's own suite plants a pinned gov: "a link at `<HOME>/.local/bin/gov`, or a `gov` on
  `PATH`, `HOME` a temporary folder" (`tests/acceptance/W2-106/w2_106_support.py`, about line 17). So do W2-65,
  W2-148 and W2-136 (`grep -l 'local/bin/gov' tests/acceptance`).

## The task
1. In W1-46's support, plant a pinned `gov` in each planted project's HOME (`<HOME>/.local/bin/gov`), the way W2-106
   does: a launcher of this tree's own code, whose first line names the running interpreter, so the hook runs this
   tree's guard.
   - Do it once, where the sandbox HOME is made, so every case that runs the hook gets it.
   - Never write the real HOME.
   - Do not touch the gate readings the D-10 sweep planted.
2. **Sweep:** which other suites run the kernel's template hook from a planted HOME and rely on the runner's PATH for
   `gov`? Run each suspect with `PATH=/usr/bin:/bin` to find them (W1-05, W1-28, W1-47, W1-49, W1-50, W2-90's kernel
   wiring are candidates).
   - Fix those in W1-46-sharing helpers the same way.
   - Name the others, with their red under the clean PATH.
   - Do not touch W2-56's or W2-148's suites; name them only.
3. **Prove it:**
   - W1-46 with both opt-ins, under the runner's normal PATH and under `PATH=/usr/bin:/bin` (keep `python3` reachable
     at `/usr/bin/python3`);
   - the same for each suite you change.
   - Report before and after.
4. One README line per suite.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-866, W2-106: the kernel's hook runs the pinned gov at HOME/.local/bin/gov or on PATH; a planted HOME plants it, so a case no longer depends on the runner's PATH"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-d10d-tests`, branch `w2/W2-20-d10d-tests`, at integrate `09e1ff6e1`.
- Write only under `tests/acceptance/` in the suites you change (not W2-56, W2-148, W1-33's agent-definition file or
  W1-38's builder, which the template helper owns tonight).
- Use the heavy slot, `PYTHONPATH=<worktree>/src`, your own TMPDIR, and `PYTHONUSERBASE=/home/usain/.local` if HOME
  is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-20-d10d-tests` only, one commit per suite, with `--trailer "Task: DAEO-r30l"`
  `--trailer "Implements: DEC-1109, DEC-866" --trailer "Role: independent-test-designer"`
  `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"` plus the Rewrite-Reason trailer. Never
  merge, push, amend or rebase.
- Estimate: 45 minutes. Return the twelve fields, short.
