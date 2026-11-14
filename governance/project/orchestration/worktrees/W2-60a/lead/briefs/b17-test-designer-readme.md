You are a fresh independent test designer. Ticket: DAEO-cv58 (W2-60a), profile FULL. Worktree `/home/usain/gov-os-worktrees/W2-60a-tests`, branch `w2/W2-60a-tests`. One small job: bring `tests/acceptance/W2-60a/README.md` (the KPI → tests map) up to date with the cases added today. Time budget about 25 minutes. No pytest run is needed beyond `--collect-only` on the folder.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a-tests`, `w2/W2-60a-tests`). If anything differs, stop and say so.

## Rules

- Foreground only. Your one file: `tests/acceptance/W2-60a/README.md`. Write with the Edit tool and its absolute path. A guard refusal is the answer: stop and report it (twice for the same call: stop; never another form).
- Any pytest (only `--collect-only -q`) through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, TMPDIR your session's `$TMPDIR`, `HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a-tests/src`, `-p no:cacheprovider`.
- Commit your file only: `git commit -m "<subject>" --trailer "Task: DAEO-cv58" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-826, DEC-839, DEC-832" -- tests/acceptance/W2-60a/README.md`. No merge, checkout, reset, stash, clean, rebase or push.

## What to add (read the commits: `git log --oneline -8 -- tests/acceptance/W2-60a` and their diffs)

- A row for the ticket's KPI line on the launcher's plan (S12 in today's briefs: "Routed from W2-33 (its S2, DEC-1156 (3))"): `test_w2_60a_plan.py`, its cases, and that its refusal exits 1 (P-6 (a), the CTO, recorded in the ticket).
- In the S2 row: the skill versioned only under `metadata: version:` (b12's case), and P-7 (a)'s cases (a vendored skill's version from `vendored.yaml`, `version_source`; an unlisted unversioned one still refuses).
- The fixture description: the template copies and the open gate (b12 may have added these lines already; do not duplicate), and the vendored manifest the P-7 cases plant.
- A short note on the revisions of today: the argv-tail checks now find the caller's arguments as one contiguous run with the appended-file pair last (W2-153's order), and the `[orchestrator]` case expects integrate's lead-launch refusal (DEC-1088 (5)). Each with the commit that made it.
- S10 is no longer this ticket's (moved to W2-184 by the CTO, 2026-11-13): if the README names it, say so in one line.
Keep every other line as it is.

## Return

The twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line: the sandbox check, the collect count, the guard refusals met (count), and your commit's hash and trailers.
