You are a fresh independent test designer. Ticket: DAEO-cv58 (W2-60a), profile FULL. Worktree `/home/usain/gov-os-worktrees/W2-60a-tests`, branch `w2/W2-60a-tests`. One small job, about 15 minutes: relabel one map row of `tests/acceptance/W2-60a/README.md` so `gov accept` can read it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a-tests`, `w2/W2-60a-tests`). If anything differs, stop and say so.

## Rules

Foreground only. Your one file: `tests/acceptance/W2-60a/README.md`, edited with the Edit tool and its absolute path. A guard refusal is the answer: stop and report it (twice for the same call: stop; never another form). Commit your file only: `git commit -m "<subject>" --trailer "Task: DAEO-cv58" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-826, DEC-839" --trailer "Rewrite-Reason: <one line>" -- tests/acceptance/W2-60a/README.md`. No merge, checkout, reset, stash, clean, rebase or push.

## The job

The CTO moved the old S10 (the second review on a different setting) to W2-184 today, so the ticket's success lines are now S1 to S10, and the line "Routed from W2-33 (its S2, DEC-1156 (3)): the launcher's plan …" is **S10**. `gov accept W2-60a` refuses with: `ACCEPT_MAP_UNREADABLE: … README line 70: "**S12** (routed from W2-33, its S2, DEC-1156 (3)) the launcher's plan prints …"`. Relabel that row's KPI cell to **S10** (and any other mention of "S12" in the README that means this line, so the README says S10 for it, with "called S12 in run 4's briefs" once if that helps a reader). If the README has a row or line for the old S10 (second review), mark it moved to W2-184 (do not leave it labelled S10). Change nothing else. Read the ticket's KPI lines at `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-cv58.md` to check the numbering (success lines in order, S1 first).

## Return

The twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line: the sandbox check, the lines changed, the guard refusals met (count), and your commit's hash and trailers.
