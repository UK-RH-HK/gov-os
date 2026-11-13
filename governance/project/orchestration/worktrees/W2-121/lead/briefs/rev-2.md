# Brief rev-2: independent auditor (FULL review, round 2, the last) for DAEO-cb2b (W2-121, part a), class C2

You are the independent auditor for ticket DAEO-cb2b (W2-121, part a): `gov dispatch tick` and `gov dispatch status`, the
generic core of the dispatcher. Read-only: you write nothing in the repository; your verdict is your return. Probe head
`f1f950479641` of branch `w2/W2-121` (`git -C /home/usain/gov-os-worktrees/W2-121 rev-parse HEAD` must show it; if not,
stop and say so). This is round 2, the last round (DEC-1010): round 1 (head 1ec89f0efdbb) failed on S4 with six
findings; a fix round followed. Judge the whole part again, not only the fixes.

## What to read
| what | path |
|---|---|
| ticket: KPI lines S1-S10 and F1 with their Verify are the spec; then its last sections: "Part a", "Interface", "P-W2-121-5", "P-W2-121-6 and P-W2-121-7" | /home/usain/gov-os-worktrees/W2-121/.tickets/DAEO-cb2b.md |
| round 1's probe record (its findings F-1 to F-6) | /home/usain/gov-os-worktrees/W2-121/docs/probes/DAEO-cb2b/PR-DAEO-cb2b-round-1.md |
| the code (start at `__init__.py`'s docstring, the KPI map) | src/gov/dispatch/ |
| the fix round's change | `git diff 1ec89f0efdbb f1f950479641 -- src/gov/dispatch tests/unit/dispatch tests/acceptance/W2-121` (c6ca85d07 is a merge of w2/integrate only) |
| the whole part's change | `git diff 6e46f985b f1f950479641 -- src/gov/dispatch tests/unit/dispatch tests/acceptance/W2-121` |
| the lead's readings of the ticket's silences (claims to check, not to trust): round 1's, and the fix round's for F-1 to F-6 | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/interface-1.md, /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/interface-2.md |
| tests | tests/acceptance/W2-121/ (the independent test designer's: `0384e71db`, and the fix round's `5045148c8`, `db682531d`), tests/unit/dispatch/ (the engineers') |
| what the code depends on | src/gov/resources/{gate,config,machine}.py (W2-20's gate); src/gov/launch/launcher.py `build_lead_settings` (the identity marker); src/gov/plan/render.py `ready_text` (S10) |
| the model, as a description (a reference, never a target) | /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/README.md |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-998, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003, DEC-1052 |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer from
both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

Out of part a (do not judge as missing): the host's installed cron or service entry, the switch-over of this repository's
dispatcher (both at the last part's close by the CTO's ACT), landings (`land.txt`, `land-done.txt`, the landing command,
F1's landing half: W2-121b), health checks (W2-121c), `gov watch` and `gov launch lead` (W2-121d). Who writes the job
history (round 1's open question) is not part a's: the dispatcher reads it.

## What to probe (at least these; find more)
1. Round 1's findings, each re-planted as round 1 planted it: F-1 (an item read, then deleted; one deleted unread; a
   never-ran and an owner item deleted; an item planted by hand then deleted: never written again); F-2 (a notifier that
   exits 1, times out, or cannot start: not recorded, retried after `notify_retry_s`, named in every pass's status while
   due; a read item never retried; the escalations after a timeout in the same pass not recorded); F-3 (no
   `notifier_command`: exit 2 at load, nothing started, PASS FAILED naming it); F-4 (untracked and staged-only paths
   unresolved; ignored-and-present resolved; committed resolved); F-5 (a load- or CPU-shut gate with ample memory refuses
   with a gate reason; a test catches the gate check's removal); F-6 (a hung git while resolving writes `unchecked:`, not
   `unresolved:`). Is each fixed, and did a fix open a new hole (e.g. the record of written items growing without bound in
   ordinary use, a crash between an item's write and its record, a notifier retried every pass forever, a slow pass)?
2. Each of S1-S5, S7-S10 and F1's start half again: does the code do what the line says, including each Verify's planted
   cases, and fail closed (round 1's list: lock and loser writes nothing; OFF; one start per pass in list order; every
   skip named; room formula with the gate's floor and working size; S7 count; no watcher; status never stale)?
3. S6: grep `src/gov/dispatch/` for this repository's branch names (`w2/`, `integrate`), paths, W2- or DAEO- ids: 0 lines.
   Each named refusal has a planted test that fails if the refusal is removed.
4. Scope: `git diff --name-only 1ec89f0efdbb f1f950479641` less the w2/integrate merge (c6ca85d07's second parent's
   changes) lists only `src/gov/dispatch/**`, `tests/unit/dispatch/**`, `tests/acceptance/W2-121/**`. The acceptance
   tests changed only in the test designer's commits.
5. The tests: would they catch a wrong implementation of each fix (one planted mutation per fix, run on a copy under
   your sandbox TMPDIR, never in the tree; the unit conftest pins the tree's src, so mutate a mirror copy)?

Runs: planted folders only (pytest's tmp_path or your TMPDIR), never the real `.gov-runtime/dispatch/` of any tree, never a
real `gov launch`, never cron. Every pytest run goes through the heavy-slot gate, TMPDIR outside the repository:
`env HOME=/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-121/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(if TMPDIR=/tmp is refused in your sandbox, use your sandbox's TMPDIR). Known and not this ticket's (P-W2-121-5, the
base-red rule of P-W2-121-6): the six W2-96 signal cases in tests/unit/accept/test_w2_96_{run2,review3,review4}.py.

Judge against ADR-0001's threat model (DEC-801): a finding is blocking only if an honest agent or operator hits it in
ordinary work and it fails open (starts what it must not, loses or duplicates an item or a wake, shows a stale status as
current) or loses work. This is the last round: for each blocking finding, say the smallest fix and what would reverse it.

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
Then the per-KPI block in round 1's form (a fenced block with the info string `verdict`, JSON: `{"kpis": [{"kpi": "S1",
"verdict": "pass|fail", "findings": [{"id", "scope", "ordinary_work", "consequence"}]}, ...]}`, S1-S10 and F1).
Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
