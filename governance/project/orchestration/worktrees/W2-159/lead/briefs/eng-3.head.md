# Brief eng-3: engineer for DAEO-6lid (W2-159), review round 1's fix, profile STANDARD, class C2

`gov session-watch stop-check waiter|idle` is built and green (tests/acceptance/W2-159 85 passed). The reviewer found
two behaviours it does not hold (below). Fix them inside your paths, test first, change nothing else. An independent
test designer writes acceptance cases for the same behaviours in parallel; you never read them.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-159 |
| branch | w2/W2-159 (head 2a67c4a63da0) |
| allowed paths | src/gov/session_watch/**, tests/unit/session_watch/** (nothing else is needed for this fix) |
| the ticket (KPI lines; the `## Interface` section is the contract) | /home/usain/gov-os-worktrees/W2-159/.tickets/DAEO-6lid.md |
| where the behaviours live (the reviewer's reading) | src/gov/session_watch/running.py (pid files), state.py and checks.py (the once-a-turn record) |
| the reference's rule for B1 (read only; never copy its project-specific names) | governance/project/orchestration/tools/stop_idle_check.py, `START_SLACK_S` and the "reused pid" lines (~237-240) |

