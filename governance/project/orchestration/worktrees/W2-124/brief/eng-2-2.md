# Brief: engineer, DAEO-mb2t (W2-124), STANDARD, class C2 — fix round 1 (build run 2, eng-2)

Budget: projection 4 USD. Keep your context short: read only what the fix needs; cut long outputs to head and tail.
(Hand-built by the lead: `gov context DAEO-mb2t --role engineer` refuses this ticket with CONTEXT_OVER_CEILING.)

You are a fresh engineer for ticket DAEO-mb2t (W2-124), in `/home/usain/gov-os-worktrees/W2-124` on branch
`w2/W2-124`. The ticket's change is built (commit 799b2b65f) and its acceptance suite `tests/acceptance/W2-124/` is
merged (c3e57a2c8). The lead's verification left the failures in
`/home/usain/gov-os-worktrees/W2-124/.gov-runtime/scratch/brief/eng-2-failing.txt`: make those cases green by
changing the code, never the tests.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-124/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-mb2t`. If it fails, stop and return. Then read `EMG-common.md` beside it (its engineer paragraph applies).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-mb2t`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-124`, `w2/W2-124`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-mb2t.md`: its KPI lines, `## Interface` and
  run 1's P2 (b) are binding. P2 (b) reads: `gov rebuild` keeps exit 0 and `"ok": true`, and the result carries
  `complete: false` and `not_built: [{store, reason}]` for every store not built (no path map, **no `.gitleaks.toml`**,
  a store the path map calls for not built).
- **Writes (nothing else):** `src/gov/rebuild/command.py`, `src/gov/adopt/stages.py`, `src/gov/close/rebuild_gate.py`,
  `tests/unit/rebuild/test_w2_124*`, `tests/unit/adopt/test_w2_124*`. Never `tests/acceptance/` or an earlier suite.
  If the fix truly needs another file, stop and return PACKAGES naming it.
- **Every pytest** through the heavy slot with the sandbox's TMPDIR (outside the repository and `~/gov-os-runs`):
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-124/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-124/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
  The slots may queue for minutes: run it in the background with a long timeout and read its output file.
- No `gov retrieve` or `gov context`; search with Read and Grep, and once more in other words (DEC-1065). No `$(…)` or
  variable as a write target, **no here-document**, no `bash -c`; scripts as files under your TMPDIR. No reset,
  checkout, clean, amend, rebase, push, merge or install. No real embedder.
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file.

## After the fix

Run `tests/acceptance/W2-124 tests/unit/rebuild/test_w2_124_semantic.py tests/unit/rebuild/test_w2_124_gate.py
tests/unit/adopt/test_w2_124_semantic_finding.py` and, because a missing `.gitleaks.toml` is also read by them,
`tests/unit/secrets_check tests/unit/retrieval/test_w2_13_lexical_policy.py tests/acceptance/W1-16`. Report every
red by node id with its one-line reason and whether it fails before your fix too (`git stash` is forbidden: compare
against the reds' text in the failing file, or name it unknown). For the two S1 timing cases, say what spends the
time if your code does (the test patches `TIMEOUT_S` and `RETRY_WAITS_S` only).

## Commit

    git commit -m "W2-124: <what>" --trailer "Task: DAEO-mb2t" --trailer "Role: engineer" --trailer "Implements: DEC-1027, DEC-1015, DEC-1014, DEC-1083, DEC-530, DEC-954, DAEO-2ds6, DAEO-2bdu" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>

Then quote `git log --oneline -3` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why.
In `evidence`: the sandbox check, each run's last line, the commit hash with trailers, `du -sh` of your TMPDIR.
Also the refusals met.
