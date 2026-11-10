Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 — the test designer's skills list switches over, the engineer's brief (DAEO-8s85)

You are a fresh engineer for **W2-153** (`.tickets/DAEO-8s85.md`: its Interface, "the skills lists"). The test
designer's list was to leave out `test-design` "only until W2-128 has reconciled that skill with DEC-963". W2-128's
round 2a is now merged on integrate, and in your branch: the test-design skill permits the integrated code on
`w2/integrate` (DEC-963). So the condition is met. Two S3 cases are red for exactly that reason:
`.rulesync/subagents/independent-test-designer.md` and `template/.rulesync/subagents/independent-test-designer.md`
show `claudecode.skills []`, not `['test-design']`.

## The change
- Set `claudecode.skills: [test-design]` in both sources, and in the launcher's or portability's skills map if it
  holds the exception. Drop the "until W2-128" exception and its comment. Nothing else changes.
- Check:
  - `gov accept W2-153` on your tree (S3 green);
  - `tests/unit/launch`, `tests/unit/adapters` and `tests/unit/resources` in full, with
    `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: 0 failures;
  - `python3 -m gov.adapters.portability` with `RULESYNC_BIN=/home/usain/.local/bin/rulesync`: only
    `GENERATED_DIFFERS` for the six agents, which the next ACT regenerates.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-153`, branch `w2/W2-153`. Your paths: the ticket's
  `allowed_paths`. Use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153/src`.
- **You never read `tests/acceptance/W2-153/`** (DEC-820 (c)). Run it only through `gov accept`, or with
  `python3 -m pytest … -rf` if `gov accept` crashes in the sandbox, and read only the result lines.
- Never start a real session. No GPU, model, network, installs or `gov retrieve`. Never open `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per
  Bash call. Do not merge. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-153`, only your paths, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A one-line round.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the diff, the counts and the portability findings.
