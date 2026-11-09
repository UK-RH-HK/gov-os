Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-f11-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the independent test designer's brief, the F11 follow-up: `--setting-sources project` (DAEO-52ku)

You are the independent test designer for **W2-149** (`.tickets/DAEO-52ku.md`). Read the changed line **S10** (marked
`[changed, DEC-1112 (3): F11]`) and the ticket's last note, "The F11 follow-up placed here". Your earlier cases are in
`tests/acceptance/W2-149/`: read your README, `w2_149_support.py` (the stub `claude`, `STUB`, and `World`) and
`test_w2_149_canary_session.py` first.

## The point
W2-149's review (round 1, F11) found that a wall session started with the real HOME may load the user's own
`~/.claude/settings.json` (allow-all lines such as `Bash(*)`, `Read(*)`; `defaultMode: acceptEdits`; any user hook or
`CLAUDE.md` added later), because the launch line names no `--setting-sources`. The deny rules and the wall hook still
refuse every outside read, so nothing leaks today; the CTO decided (DEC-1112 (3)) to close it as defence in depth:
**the session and the canary both carry `--setting-sources project`**, so only the wall's own project settings load
(the wall's `.claude/settings.json`, which is also passed by `--settings`). Nothing else in the launch changes.

## What the case must show (S10's change; one case, red today)
- **The flag present, the user file not loaded:** a good writer launch in a planted HOME that holds a user settings
  file `<planted HOME>/.claude/settings.json` the stub would load when the user source is on (for example a hook or a
  marker the stub records as "user settings loaded"). Expect:
  - the real session's line carries `--setting-sources` with the value `project` exactly (no `user`, no `local`);
  - the canary's line carries the same flag and value;
  - the stub records that the user file was **not** loaded for either call;
  - the launch still delivers (exit 0) and the wall's own settings still load (the canary is still refused by them).
- **Teach the stub one rule** (it already parses `--setting-sources` as a value flag): with no `--setting-sources`, or
  one that includes `user`, it loads `$HOME/.claude/settings.json` (record it, and let its hook or allow lines act as
  Claude Code would); with a list that leaves `user` out, it does not. Keep every existing case's behaviour: today's
  77 non-live cases must stay green against the merged script except the new one.
- If an existing case asserts the exact flag list or its length, adjust it only as far as S10's change requires, and
  say which in the README.
- You may add the flag check to the live S11 case's command-line assertions if it has any; do not add a live case
  that writes into the real `~/.claude/` (never write there).

Map the case to S10 in the README's table, with the red reason, and update the interface line for S10.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-149-f11-tests`, branch `w2/W2-149-f11-tests`, made from
  `w2/integrate` at `d1e53016e` (W2-149 merged, the ticket's S10 changed). Write only `tests/acceptance/W2-149/`.
- **Your record:** your whole return is your session's final message, in full.

## Rules
- You never read the implementation: not `governance/project/orchestration/tools/indep_launch.py`, not
  `tests/unit/orchestration/test_w2_149*`, not `docs/changes/W2-149-evidence.md`, and never the engineer's worktree
  (base name `W2-149-f11` without `-tests`). Run the script only as your cases do.
- No GPU, model, network or installs; no real `claude` session.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. Every case on planted roots (failure line 10); never the real `~/gov-os-eval`,
  `~/gov-os-runs`, `~/gov-os-wall-trees` or `~/.claude`.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-f11-tests/src`, `TMPDIR=/tmp/gov-os-emg-w2-149-f11-designer`, a
  scratch HOME with `.local` linked in, and `PYTHONUSERBASE=/home/usain/.local`. Then run
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-f11-tests`.
- **DEC-1080:** one simple command per Bash call. **Search again once (DEC-1092 (1)).**
- **Commit** on `w2/W2-149-f11-tests`, only `tests/acceptance/W2-149/`, with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only. Report your scratch size.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
  discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), first, as labelled lines;
- the case: node id, expectation, red today and why; any existing case you adjusted, and why;
- the commit;
- `gov accept`'s counts;
- `TESTS-READY`.
Refused twice for the same call: stop and say so; no third try.
