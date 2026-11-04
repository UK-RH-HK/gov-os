# Decisions in force

The one list of what holds (DEC-1052 R-9), 2026-11-03. Where the prompt, a brief or RESUME HERE differs, it holds; a
rule the prompt's body states correctly is not repeated. The register is the authority; spent and superseded entries
stay there and in `ARCHIVE-SUPERSEDED.md`. A new line names the basis test it passes.

## The emergency, until the owner lifts it
- DEC-1047, DEC-1051 (with DEC-1032, DEC-1033): everything stopped until the refactoring and the re-pins; nothing
  scheduled but the dispatcher (ready list empty, approvals parked); each item resumes from
  `log/emergency-stops-20261102.md`. DEC-1010 stays.
- DEC-1049: no nightly and no full suite until the owner's word (D-10); the nightly's crontab lines stay commented.
- DEC-1052, DEC-1055: the plan (`packages/LIFT-1/P1-PLAN.md`): G-14, D-3, D-4 beside D-4b (memory, as refactoring
  work, no leads; D-4 two heavy slots, D-4b one and the rebuild lock), the final memory measure, re-pin window 3 and
  the integration store, D-5 to D-9, D-10, the lift. No run the old way.
- DEC-1052, the basis (standing): one question, five tests (`INTENT-DEC-1052.md`); applied at adoption, on symptoms
  and weekly with measured costs; the lift-or-remove list to the owner first; a practice enters the product once proven.
- DEC-1052: templates per session kind, ticket and brief, READY and DONE computed from their required fields by code;
  the suite cut to about 5,000 before D-10, every kept KPI line covered, the list to the owner first; memory embeds
  no `tests/**`, close, checkpoint or probe records, nor orchestration closes, reviews, sessions or nightly (M-4,
  DEC-1055 (3)); the hidden half lives in `~/gov-os-eval/`, outside every worktree (G-3, DEC-1055 (4)).
- DEC-1052 G-14, DEC-1054, DEC-1056, DEC-1059 (live since ACT-G14, `4edd196c`): role separation by path checks; the test designer never reads the ticket's new
  code or new unit-test files; the engineer never reads its own ticket's acceptance tests, wherever they sit; shared
  test files, other tickets' tests and the integrated code stay readable (DEC-963).
- DEC-1065 (standing): no CPU fallback for embeddings anywhere (the shared GPU embedders unreachable: the semantic part
  unavailable, named, keywords answer; never a private embedder on the CPU, as the reranker's ACT-RERANK-WAIT-1);
  search respects role separation (`gov retrieve` filtered by the caller's `role_paths`, before W2-127 and the restart).
  DEC-1064: sandboxed workers run no `gov retrieve` and no real-model test until then.
- DEC-1067 (standing for D-4b): the memory measure's hidden half never chooses a method (adopted only if it wins on
  the visible half alone; the hidden half reported separately; hidden ranks never in the index or on integrate);
  labels change only where wrong, never to fit results; GPU safety for experiments (the 15.5 GB backstop; no measure or
  rebuild beside one; the GPU back in budget between); no install until the owner decides the bigger models.
- DEC-1060: lens B's q03 rewritten to DEC-1033's rule; a measure question never rewards a replaced decision.
- DEC-1053: D-0 done; `w2/W2-78` and the in-flight branches with unmerged work wait for D-9.
- DEC-1050: this repository kept; no full `gov check` in leads' runs (T-1); attribution once each way (Q-1); the
  landing refuses an acceptance-test change but the designer's or owner's (G-1); guard rules 1 and 5 judge only
  targets that resolve (G-2); review effort as it is (G-12).
- DEC-1045: no gitleaks scan here (`secrets.yaml` `scan: off`); a weekly full scan only on the owner's approval.
- DEC-1040 (3), DEC-849: a false refusal is worked round at once by an equivalent form and named; a true one is taken.

## The owner
- R-11, R-8 (DEC-1050 (9)): a ping only when work waits on the owner (a blocking P1, an ACT a step waits on,
  LAUNCH_BLOCKED, ESCALATION, AUTH_REQUIRED) or an emergency; the rest in two digests a day (09:00, 18:00), one page
  each. Six parts only for a blocking P1, else question, options, recommendation; P1 only by DEC-957's rubric (§7). A
  delegated choice is a line in its ticket's file or close record, not a register entry.
- DEC-972, DEC-1021, DEC-973: a ping is `tools/ping_log.sh`, `PushNotification`, `--result`; a blocking P1 "not sent"
  by day falls back to `owner-ping`. Quiet hours 02:00 to 07:30; an emergency pings at once at any hour (owner, D-3 answer 3); the morning package at 09:00.
- DEC-991, corrected by DEC-1050 (8): `owner-ping` and `.claude/` paths ask; `rm` is free but the catastrophic (the
  hook refuses it); `sudo`, `git push` denied. A call that may ask is never chained; by day ping first; 02:00 to
  07:30 never run it: queue it (`log/approval-queue.jsonl`) for 09:00.
- DEC-957: the work order (the test designer from the spec, never the code; the engineer to the spec, never the tests;
  QA reads both, changes neither); installs only through the CTO's session.
- DEC-974: a new WBS ticket is a P1 before it is filed; leads name one, never file it.
- DEC-954 Q1: EXAMIN's copy on K9's entry criteria, never a date. DEC-952 (6): a fresh CTO session each morning; no handover by context size (O-3 refused).

## Machine and ACTs
- O-6, scoping DEC-1038 (1): an ACT only for a machine change, where it helps: installs, services, crontab,
  `.wslconfig`, `~/.local/bin` (the pinned gov), `~/.config`, `~/.ollama`, `~/.local/share`, environment files,
  `.claude/` settings and hooks; exact commands, check and undo (DEC-925 (2)). No ACT for records. Until D-10, a
  settings change runs its own scoped tests on a clone, not the full suite (owner, D-3 answer 5). **Every ACT is
  rehearsed end to end, exactly as the operator will run it, in a scratch copy (its own clone) before it is handed
  over; its stated counts are the rehearsal's (owner, standing, 2026-11-03).**
- P-ACT-SPLIT (owner, 2026-11-03): (a) the operator's ACTs: the guard, its hooks, `.claude/` settings and generated
  files, the pinned gov, the sentinel, what the CTO's session runs on; (b) the CTO's ACTs on the owner's ping reply
  (crontab, the servers' settings, the CTO's watchers, `~/.config/gov-os*`, `~/.cache/gov-os`), only with a rehearsed
  rollback, the approval recorded verbatim in the ACT and `log/act-approvals.jsonl`, the report in the next digest.
  Never the CTO's: `sudo`, `git push`, installs, irreversible deletion, secrets, its own permissions, quiet hours.
- DEC-1028 (6), scoped by O-6: while an ACT is applied, no commit touches its paths (`log/act-in-progress.txt`).
- DEC-1038 (2)-(4): the CTO's checkpoint to scratch (`tools/cto_checkpoint.sh`); `.wslconfig` unchanged until the RAM
  upgrade; the standing targets (a breach over 15 min an incident); every heavy job through `tools/heavy_slot.sh`.
- DEC-1039 (1b), (6), DEC-1037 (4), (5), O-A1, O-10: admission by the Load Balancer's forecast (`gate_check.py`
  lifted); limits from the machine; `tools/tree_busy.sh`, never `pgrep -f`; a stop parks the queue's approvals.
- DEC-1030, DEC-1015: the dispatcher watches the GPU and server logs (a crash or 0-layer load: inbox and push); a
  rebuild without its semantic store has failed.
- DEC-1031, DEC-1043 (2), DEC-1048: the embedder stays on the GPU; no private reranker beside the shared one
  (`tools/rerank_service_slot_hold.py --watch`); the interim GPU-slot module is the machine-wide guard.
- O-5 (DEC-994, DEC-998 scoped): one stall net, the dispatcher's stale line and the sentinel's push, and the
  quiet-hours hook; at session start Remote Control, one test push, `log/cto-session.txt`; `log/cto-standby.txt`
  kept while the sentinel reads it (owner, D-3 answer 7).

## Tickets, tests, reviews
- DEC-953 (1, 2, 6), DEC-954: nothing gates this repository until the Gov OS is whole; closes on the audit's 10
  practices; nothing deleted from the product; the guard's five rules; `gov close` proved on W2-81 and EXAMIN's copy.
- DEC-1010, DEC-916: moderator triage; a finding blocks only in scope, in ordinary work and failing open or losing
  work; two rounds, then the owner once; READY by `tools/verdict.py`.
- DEC-968: scoped runs only (`tools/select_tests.py`); a close refused only by its own failure; no accepted reds.
- DEC-959, DEC-988, DEC-989: every merge through the queue (`tools/land.py`), one per ticket; merge and close one step;
  except the refactoring's merges as built (D-1, D-4b: one review, READY by code, the CTO merges; DEC-1052, DEC-1055).
- DEC-995, DEC-996: a role is its reads and writes; a skill never widens it; mixed tickets split first.
- DEC-1007, DEC-1012 (1), DEC-999: leads start only from `dispatch/ready.txt`, returns land in its inbox, one batch
  from `land.txt`, `status.txt` the truth; claims committed before a lead starts.
- DEC-979 (2): the CTO's tools: their own tests; a review only where a change could fail open or lose work.

## Rules about rules
- O-11, DEC-1012: a rule broken twice becomes a mechanism only if it passes DEC-1010's test; a slipped ceremony is
  assessed under the basis instead.
- O-11, DEC-1003, DEC-982: a practice from the CTO's tools enters a product ticket after a week in use and the basis,
  proposed weekly as one batch.

## Records and commits
- DEC-861, R-10: the CTO commits the owner's decisions (`Task: decision-record`, `Role: orchestrator`, `Decided-by`),
  one commit per batch (hourly or at handover); `record/w2` synced hourly and at session end; `--main` lifted.
- R-12: `Task:` and `Role:` on every commit; `Implements:` optional; a decision and its ticket files in one commit.
- R-6: no committed `gov checkpoint` record per round; the prose checkpoint, PreCompact and SessionStart stay.
- R1-21: `tools/structural_pass.py` after each landing and record commit, a notice only.

## Lifted (was `LIFTED-BY-DEC953.md`, `69a0e5d89f04`; kept built and tested in the product unless "ended")
- DEC-953: `gov close` and its gates here, escalations, repair tickets, the work-without-a-task gate, containment and
  trailers as refusals, the ratchet lists and their owner commits, probe staleness, the re-pin ladder, the memory
  arithmetic as a gate, the guard beyond its five rules. Ended: the pre-close gate (a) to (h), `record_checks.sh`,
  close windows, holds and cut-offs, the 90-minute rule, the red-nightly hold, the nightly's booking window.
- DEC-1045: gitleaks here. DEC-1050: the guard harvest, `refusal_watch.sh`. DEC-1052: record ACTs (O-6); round
  records (R-6); the two-commit rule (R-12); a ping per owner item (R-11); heartbeat checks, the
  Stop-hook waiter check, the scratch `deadman.py` (O-5); §0's copies and RULES-IN-FORCE (R-9); `gate_check.py` (O-10).

## Approved restarts by class (owner, O-6)
Approved (owner, D-3 answer 4, 2026-11-03): the five classes in `governance/project/orchestration/RESTART-CLASSES.md`
(the shared embedder :11434, the query server :11435, the shared reranker service, the CTO's samplers and slot
watcher, the sentinel). Each is restarted by the CTO from its committed config, with its check, without an ACT; any
other restart is an ACT.
