---
task: nightly-beside-leads-check
decisions: [DEC-1159, DEC-1132, DEC-984, DEC-1001, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1073]
reviewed: .gov-runtime/scratch/orchestrator/drafts/nightly-beside-leads/{before,after}/ (quiet_check.py, nightly_restart.sh, test_nightly_restart.sh); repo HEAD df8ba7007540bdf7d36c955b602921ebe89b23e6
reviewer: a fresh read-only independent auditor (Opus, high), 2026-11-13 ~00:45, commissioned and judged by the CTO
amends: ACT-NIGHTLY-RESTART-1 (class (b)); the owner's yes: "The 04:00 nightly: (a), start now" (chat, 2026-11-13 ~00:30)
---
# Narrow review: the nightly beside the leads (an amendment to ACT-NIGHTLY-RESTART-1, DEC-1159 (1))

## What was checked and found sound
- **No-flag behaviour.** quiet_check.py without `--beside-leads` is identical. Every change is gated on the flag, and before and after gave the same exit code in 96 planted cases (6 status files × 4 process lists × 2 loads × with and without `--no-load`).
- **Still counted under the flag.** Probed one by one: the status's land_running, close_running and queue_busy flags; landing, close and nightly jobs; land.py, merge_queue.py and close_build.py (cwd outside the busy folders); the queue's run lock; CLOSE-RUNNING, NIGHTLY-RUNNING and MEASURE-RUNNING; the ACT marker; the operator's freeze; a merge in progress, a dirty tree, a head under 5 minutes old; 150 rg processes; an unreadable or stale status. The CTO's dispatch/OFF also still counts.
- **Left out under the flag, as decided:** a lead, a pending launch, lead and slot jobs, a heavy step outside a slot, held slots and rebuild locks, processes in worktrees and the runs folder, pytest, the four lead scripts, and the load.
- **Wrapper.** It writes no OFF. Every path either runs the nightly or refuses (exit 2) at the latest start; a crash of the quiet check counts as busy. The cleanup trap is correct with HAVE_OFF at 0. The stale-OFF removal still removes only a dead wrapper's token. The lock, committed-code check, latest start, memory probe, cap, watchdog and result handling are unchanged.
- **Rehearsal.** `bash after/test_nightly_restart.sh after`, with TMPDIR outside the repo: 75 cases, 0 failures.

## Findings
| id | behaviour | ordinary work | consequence | scope | reverse if |
|---|---|---|---|---|---|
| F1 | Under the flag, a landing or close running from a worktree or the runs folder is not seen by the process check; only the status (up to 180 s old) and CLOSE-RUNNING see it. The code comment wrongly says the job scripts name it. | yes, because a lead's close runs from its worktree | other | in | land.py and close_build.py never run there, or the status is written at least every 60 s |
| F2 | The evaluation, writer, checker and walled-session folders are left out as well, beyond the decided "worktrees and the runs folder". | yes, because such sessions can run at 04:00 | other | in | the owner confirms they count as leads' work |
| F3 | The nightly's rebuild runs before it takes the slots, under a lock no lead takes since DEC-1001 (d), so it can run beside three slot jobs (memory). | yes | other | out | a lead rebuild path still takes /tmp/gov-os-rebuild.lock |
| F4 | The wrapper's header still describes the old wait; the OFF variables are dead code. | yes, because a reader may follow the stale text | other | in | the text is meant as a record of the old rule |
| F5 | Workers' rebuilds (started with setsid, outside the lead's tree) are still counted as "rebuild" jobs, which can delay the nightly to NOT STARTED. | yes | other (fails closed) | in | the dispatcher attributes them to the lead |
| F6 | The revised rehearsal does not cover queue_busy, close_running, the run lock, a merge in progress, a young head, rg, an unreadable status or non-lead job kinds under the flag, and does not check merge_queue.py or close_build.py by name. | yes | other | in | cases elsewhere cover them |

Classification: 6 findings; 0 block (none is in scope, ordinary work and failing open or losing work); all are rows.

## Risks for the owner
- The nightly holds all three heavy slots for its suites (an estimate of about 59 minutes). Leads' tests, closes and landings wait for it, with no limit.
- Leads holding slots at 04:00 delay the nightly by up to 30 minutes, after which it runs with fewer slots and its estimate grows.
- The cap needs at least 12 GiB available at the start. With leads running, memory refusals or watchdog stops become likely (P1 nights); the leads stay protected.
- Landings, closes and new leads are not checked after the start, as decided; nightly.sh's own head-quiet loop still holds before the clone.

## The CTO's judgement
PASS accepted. F1 is not acted on tonight: counting land.py and close_build.py inside worktrees could count leads' own verification and refuse every night; the dispatcher's land_running and close_running see queue landings and closes from any folder. F1-F6 are rows (DECIDED-NOT-DONE); F3 (the nightly's rebuild and leads' slots) and the memory risk are named to the owner.

```verdict
{"kpis": [{"kpi": "nightly-beside-leads-check", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```

---

# Follow-up: F5 fixed (rebuild jobs left out), with F2 of its check (test helpers' rebuilds) — narrow check `nightly-f5-check`, PASS

- **The change (on 60917fb0d):** under `--beside-leads`, a dispatcher status job of kind "rebuild" is left out (a lead's or worker's store; a landing's or close's rebuild is classed landing or close and still counted), and so is a `gov rebuild` process outside the busy folders (a test helper's rebuild in a temporary project; F2 of the check, ridden along as the reviewer allowed). Four rehearsal cases added (each with and without the flag). Rehearsal with a planted memory file: 79 cases, 0 failures.
- **The check (a fresh read-only independent auditor, Opus high, 2026-11-13 ~01:00):** the diff only that; no-flag behaviour unchanged; landings, closes and the merge queue still seen (their kinds, land_running, close_running, queue_busy, the run lock, the job scripts, CLOSE-RUNNING). Rows: F1 the integration store's refresh no longer waited for (it writes the standby half; the nightly reads the ready half; both share the heavy slots); F2 the temp rebuilds (fixed in this commit).

```verdict
{"kpis": [{"kpi": "nightly-f5-check", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
