# W2-149 — the engineer's brief, the F11 follow-up: `--setting-sources project` (DAEO-52ku)

You are a fresh engineer for **W2-149** (`.tickets/DAEO-52ku.md`). Read the changed line **S10** (marked
`[changed, DEC-1112 (3): F11]`) and the ticket's last note, "The F11 follow-up placed here". **One small pass, S10's
change only.**

## The point
W2-149's review (round 1, F11) found that a wall session started with the real HOME may load the user's own
`~/.claude/settings.json` (allow-all lines, `defaultMode: acceptEdits`, any user hook or `CLAUDE.md` added later),
because the launch line names no `--setting-sources`. The CTO decided (DEC-1112 (3)), as defence in depth:
**`session_flags` in `governance/project/orchestration/tools/indep_launch.py` (about line 721) adds
`--setting-sources project`, so the real session and the canary both carry it.** Only the wall's own project settings
then load: the wall's `.claude/settings.json` is the project source (the session runs from the wall) and is also passed
by `--settings`, so nothing the wall needs is lost.

- Place it beside `--restricted` (one flag, value `project`, exactly once on each line).
- Nothing else changes: the canary still differs from the session only by its own `--add-dir` and its own drawn
  `--session-id`; the order of the other flags, the prompt and its sha256 constant, the environment and everything
  after the session stay byte for byte.
- Update your unit tests (`tests/unit/orchestration/test_w2_149*`): the one that checks the session's flag slice
  (`a[6:-3]` today) and the canary-against-session comparison, for the new flag.
- Add a short "F11 (DEC-1112 (3))" section to `docs/changes/W2-149-evidence.md`: what changed, where (lines), the
  tests.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149-f11`, branch `w2/W2-149-f11`, head `5e3c9abf4` (`w2/integrate` at `d1e53016e`
  with the designer's F11 case merged; `.gov-runtime/scratch/lead/TESTS-READY` names it).
- Your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/W2-149/`.** You see only `gov accept`'s results.
- **The exclusion line:**
  - recursive grep carries `--exclude-dir=W2-149`;
  - Grep and Glob carry `!tests/acceptance/W2-149/**`. A brace glob does not exclude: pass a separate pattern.

## Verify
Run everything through the heavy slot that `EMG-common.md` names, with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-f11/src`, a scratch HOME with `.local` linked in, and
`PYTHONUSERBASE=/home/usain/.local`:
1. `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-f11`. Every line must be green
   but the three live cases, which skip; today success-10 is 4/5.
2. `tests/unit/orchestration/test_w2_149*`.

Commit as you go.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. Never run the script against the real `~/gov-os-eval`, `~/gov-os-runs`,
  `~/gov-os-wall-trees` or `~/.claude`; no real `claude` session.
- No GPU, network or installs. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **DEC-1080:** one simple command per Bash call. Waits by pid only. Do not merge `w2/integrate`.
- **Commit** on `w2/W2-149-f11` with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Report your scratch size.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
  discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), first, as labelled lines;
- the commits;
- `gov accept W2-149` per line;
- the unit counts, with every red named and whether it was red before.
Refused twice for the same call: stop and say so; no third try.
