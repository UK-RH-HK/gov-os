Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief rev-1: independent auditor (FULL review, round 1) for DAEO-cb2b (W2-121, part a), class C2

You are the independent auditor for ticket DAEO-cb2b (W2-121, part a): `gov dispatch tick` and `gov dispatch status`, the
generic core of the dispatcher. Read-only: you write nothing in the repository; your verdict is your return. Probe head
`1ec89f0efdbb` of branch `w2/W2-121` (`git -C /home/usain/gov-os-worktrees/W2-121 rev-parse HEAD` must show it; if not,
stop and say so).

## What to read
| what | path |
|---|---|
| ticket: KPI lines S1-S10 and F1 with their Verify are the spec; then its last three sections: "Part a" (what this part keeps), "Interface" (state folder, configuration, identity marker, exit codes), "P-W2-121-5" | /home/usain/gov-os-worktrees/W2-121/.tickets/DAEO-cb2b.md |
| the code (start at `__init__.py`'s docstring, the KPI map) | src/gov/dispatch/ |
| the ticket's own change | `git diff 6e46f985b 63130cf2d -- src/gov/dispatch tests/unit/dispatch tests/acceptance/W2-121` (63130cf2d..1ec89f0ef is the merge of w2/integrate only) |
| the lead's readings of the ticket's silences (claims to check, not to trust) | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/interface-1.md |
| tests | tests/acceptance/W2-121/ (the independent test designer's, `0384e71db`), tests/unit/dispatch/ (the engineers') |
| what the code depends on | src/gov/resources/{gate,config,machine}.py (W2-20's gate: memory floor, working size, S6 admission); src/gov/launch/launcher.py `build_lead_settings` (the identity marker); src/gov/plan/render.py `ready_text` (S10) |
| the model, as a description (a reference, never a target) | /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/README.md |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003, DEC-1052 |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer from
both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

Out of part a (do not judge as missing): the host's installed cron or service entry, the switch-over of this repository's
dispatcher (both at the last part's close by the CTO's ACT), landings (`land.txt`, `land-done.txt`, the landing command,
F1's landing half: W2-121b), health checks (W2-121c), `gov watch` and `gov launch lead` (W2-121d).

## What to probe (at least these; find more)
1. Each of S1-S5, S7-S10 and F1's start half: does the code do what the line says, including each Verify's planted cases,
   and fail closed? In particular:
   - S1: two concurrent `tick`s run one pass; the loser exits 4 and writes nothing (no folder, no file, no mtime change);
     OFF stops a pass before it starts anything.
   - S2: at most one start per pass, staggered; only ready-list entries; each skip reason (uncommitted claim on the
     integration branch or in the worktree, unclean worktree, incomplete brief, running ticket, unread return, shut gate,
     full disk) is named; a malformed list line is refused and named, never guessed.
   - S3: peaks per kind of job, with dates, refreshed at least daily; a start refused when room < new peak + peaks ahead,
     made when over; the floor and working size read from the gate, not re-defined; memory admission left to W2-20's S6.
   - S4 / S9: one inbox item per finished return, exactly once across passes and restarts; a start that never ran gives
     one item; an item unread past the configured time gives one escalation via the notifier command; commit ids and paths
     named in a return are resolved against git and the unresolved ones named.
   - S5: the running count comes from processes by the identity marker (never from started.txt or another file); a
     failing pass says so on the status's top line and never leaves a stale file that looks current.
   - S7: a ticket with two probe records gets no review launch and becomes one owner item; one probe record is started.
   - S8 / S10: every wake is an inbox item; no watcher; the dispatcher never reorders the list.
2. S6: grep `src/gov/dispatch/` for this repository's branch names (`w2/`, `integrate`), paths, W2- or DAEO- ids: 0 lines.
   Each named refusal (uncommitted claim, shut gate, no room for a peak, running ticket, unread return, malformed list line,
   a hung command, a crash after a launch) has a planted test that fails if the refusal is removed.
3. Robustness an honest operator hits: a hung git or launcher command (timeouts); a crash between the launch and the
   `started.txt` write (no double start next pass, no lost item); partial writes of status.json/inbox items (atomic?);
   a clock or timezone edge in the "unread past" and "refreshed daily" checks; the lock released on every exit path.
4. Scope: `git diff --name-only 2a35ec307 1ec89f0efdbb` lists only `src/gov/dispatch/**`, `tests/unit/dispatch/**`,
   `tests/acceptance/W2-121/**` (and `.tickets/DAEO-ozyt.md`, a claim on w2/integrate after the merge: not this ticket's).
   The acceptance tests are unchanged since the test designer's `0384e71db`.
5. The tests: would they catch a wrong implementation of each line (one planted mutation per line, reasoned or run on a
   copy under /tmp, never in the tree)?

Runs: planted folders only (pytest's tmp_path or /tmp), never the real `.gov-runtime/dispatch/` of any tree, never a real
`gov launch`, never cron. Pytest form (HOME empty, user site kept):
`env HOME=/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-121/src python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
Known and not this ticket's (P-W2-121-5): the six W2-96 signal cases in tests/unit/accept/test_w2_96_{run2,review3,review4}.py.

Judge against ADR-0001's threat model (DEC-801): a finding is blocking only if an honest agent or operator hits it in
ordinary work and it fails open (starts what it must not, loses or duplicates an item, shows a stale status as current)
or loses work.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <n>
- <id> | <severity: blocking, major, minor> | <KPI line> | <file:line> | <what is wrong, the planted input and the wrong output>
```
Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
