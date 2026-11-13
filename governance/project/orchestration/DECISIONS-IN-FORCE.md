# Decisions in force

The one list of what holds (DEC-1052 R-9), 2026-11-04; brought to DEC-1096 on 2026-11-07 (re-pin window 4 done at
14:22: the live pin is `pin-bcea09060ebc`), to DEC-1122 on 2026-11-10, and to DEC-1125 on 2026-11-11 (the anti-drift audit a, register v0.509; marks of changed entries and DEC-1057, DEC-1058, DEC-1063 added), and to DEC-1126 on 2026-11-11 (re-pin window 5 done at 13:31: the live pin is `pin-797495bdfc70`, `pin-bcea09060ebc` kept for rollback; register v0.511, DEC-1128), to DEC-1150 on 2026-11-12, and to DEC-1159 on 2026-11-13 (DEC-1158 (4): the emergency of 2026-11-02 lifted, its section moved to "Lifted"; DEC-1157's and DEC-1159's changes marked; register v0.540; items the CTO's sweep `drafts/dif-sweep-20261113.md` only recommends are marked, not removed). Where the prompt, a brief or RESUME HERE differs, it holds; a
rule the prompt's body states correctly is not repeated. The register is the authority; spent and superseded entries
stay there and in `ARCHIVE-SUPERSEDED.md`. A new line names the basis test it passes.

## What still holds or delays work (DEC-1157 (14))
Everything else that held or delayed a lead was removed by DEC-1157 or lifted by DEC-1158; these stay (they protect
the machine and the governance):
- **Memory:** the gate's 3 GiB floor and the working size 0.75 GiB per live session (DEC-1133 (6), DEC-1149 (1)); the
  hold below 5 GB available on any next launch (DEC-1138 (2), kept by DEC-1149 (1)); `mem_guard` (DEC-1133 (5)) and the
  OOM trip (2 GiB). Memory admits each start (no lead cap, no CPU band: DEC-1157 (5), (8)).
- **The guard's refusals:** role separation by path (DEC-1052 G-14, DEC-1063), the held-out sets, the guard as live
  (DEC-1128 (2)-(4)); the two-refusal stop, also against the same effect by another form (DEC-1142 (9)); a resource
  gate's refusal is a wait, not a refusal (DEC-1146).
- **The spend brake:** the runaway brake at twice each projection stays a stop (DEC-1091, DEC-1126 (4), DEC-1149 (3));
  usage never holds a lead or a worker (DEC-1149 (3)).
- **The brief checks:** every brief checked before release (DEC-1140 (1)(a)); the CTO states the interface at claim
  (DEC-1157 (3)).
- **Review rounds, the kernel gate and the owner's approval of kernel bytes:** one bar, two rounds (DEC-1131,
  DEC-1010); a narrow check of a change decided after review (DEC-1154); `kernel_gate.py` before every land and hand
  merge (DEC-1148 (3)); kernel bytes only on the owner's approval (CAP-33).
- **New tickets and splits to the owner** (DEC-974, DEC-1142 (8)); widenings and KPI edits within a ticket's purpose
  are the CTO's, listed for the owner (DEC-1157 (12)).
- **The idle check's record** (DEC-1110 (2)): a named, legitimate wait only.
- Beside these, ordering rather than holding: the ready list and committed claims (DEC-1007); the queue, lands of two or
  three disjoint tickets, at most two of the three heavy slots (DEC-989, DEC-1157 (4), (10)); the disk gate (DEC-898);
  the GPU budget and no spill (DEC-1039 (1b), DEC-1158 (3)); the nightly in its capped unit beside the leads (DEC-1159 (1)).

## The owner
- R-11, R-8 (DEC-1050 (9), DEC-1057): a ping only when work waits on the owner (a blocking P1, an ACT a step waits on,
  LAUNCH_BLOCKED, ESCALATION, AUTH_REQUIRED) or an emergency; the rest in two digests a day (09:00, 18:00), one page
  each. Six parts only for a blocking P1, else question, options, recommendation; P1 only by DEC-957's rubric (§7). A
  delegated choice is a line in its ticket's file or close record, not a register entry. **Every decision that stops or
  delays a lead comes to the owner at once, at any hour, as a full package (DEC-1157 (1)).**
- DEC-972, DEC-1021 (changed by DEC-1157 (1)), DEC-973: a ping is `tools/ping_log.sh`, `PushNotification`, `--result`; a blocking P1 "not sent"
  by day falls back to `owner-ping`. Quiet hours 02:00 to 07:30, except a decision that stops or delays a lead (DEC-1157 (1)); an emergency pings at once at any hour (owner, D-3 answer 3); the morning package at 09:00.
- DEC-991, corrected by DEC-1050 (8): `owner-ping` and `.claude/` paths ask; `rm` is free but the catastrophic (the
  hook refuses it); `sudo`, `git push` denied. A call that may ask is never chained; by day ping first; 02:00 to
  07:30 never run it: queue it (`log/approval-queue.jsonl`) for 09:00 (a reviewer's read-only probes allowed in the
  quiet hours, DEC-1144 (7)). The quiet-hours ban on a call a lead waits on: (the 09:00 sweep: recommended to amend)
- DEC-957: the work order (the test designer from the spec, never the code; the engineer to the spec, never the tests;
  QA reads both, changes neither); installs only through the CTO's session.
- DEC-974, DEC-1142 (8) (standing; changed by DEC-1157 (12)): a new WBS ticket is a P1 before it is filed; no new
  ticket and no split is filed without the owner's decision; leads name one, never file it. Widenings and KPI edits
  within a ticket's own purpose are the CTO's, listed for the owner's reading (DEC-1157 (12)). A defect inside a
  closed ticket's scope reopened by the CTO (DEC-1088 (6)): (the 09:00 sweep: recommended to amend)
- DEC-954 Q1: EXAMIN's copy on K9's entry criteria, never a date. DEC-952 (6): a fresh CTO session each morning; no handover by context size (O-3 refused).

## Machine and ACTs
- O-6 (DEC-1057), scoping DEC-1038 (1) and DEC-1028 (6): an ACT only for a machine change, where it helps: installs, services, crontab,
  `.wslconfig`, `~/.local/bin` (the pinned gov), `~/.config`, `~/.ollama`, `~/.local/share`, environment files,
  `.claude/` settings and hooks; exact commands, check and undo (DEC-925 (2)). No ACT for records. Until D-10, a
  settings change runs its own scoped tests on a clone, not the full suite (owner, D-3 answer 5). **Every ACT is
  rehearsed end to end, exactly as the operator will run it, in a scratch copy (its own clone) before it is handed
  over; its stated counts are the rehearsal's (owner, standing, 2026-11-03).** After D-10, a full run per settings ACT
  (DEC-1057 (5), DEC-925 (2)): (the 09:00 sweep: recommended to amend)
- P-ACT-SPLIT (DEC-1058, owner, 2026-11-03; the shared servers' settings now (a), DEC-1104 (2)): (a) the operator's ACTs: the guard, its hooks, `.claude/` settings and generated
  files, the pinned gov, the sentinel, what the CTO's session runs on; (b) the CTO's ACTs on the owner's ping reply
  (crontab, the servers' settings, the CTO's watchers, `~/.config/gov-os*`, `~/.cache/gov-os`), only with a rehearsed
  rollback, the approval recorded verbatim in the ACT and `log/act-approvals.jsonl`, the report in the next digest.
  Never the CTO's: `sudo`, `git push`, installs, irreversible deletion, secrets, its own permissions, quiet hours.
  (b) in the quiet hours once a lead waits and the owner's yes is recorded: (the 09:00 sweep: recommended to amend)
- DEC-1028 (6), scoped by O-6: while an ACT is applied, no commit touches its paths (`log/act-in-progress.txt`). G9
  holding every queued ACT on that file: (the 09:00 sweep: recommended to amend)
- DEC-1038 (2)-(4) ((4)'s T1 band removed by DEC-1157 (5); a land holds at most two of the three heavy slots, DEC-1157
  (10), DEC-979 changed): the CTO's checkpoint to scratch (`tools/cto_checkpoint.sh`); `.wslconfig` unchanged until the RAM
  upgrade; the standing targets (a breach over 15 min an incident); every heavy job through `tools/heavy_slot.sh`
  (each wait logged, DEC-1157 (13)). The fixed three slots and "only the owner may override": (the 09:00 sweep: recommended to amend)
- DEC-1039 (1b), (6), DEC-1037 (4), (5), O-A1, O-10 (DEC-1039 (1b)'s CPU term removed by DEC-1157 (5); its GPU budget
  and no-spill kept and its "two or three leads" obsolete, DEC-1158 (3)): admission by the Load Balancer's forecast (`gate_check.py`
  lifted); limits from the machine; `tools/tree_busy.sh`, never `pgrep -f`; a stop parks the queue's approvals.
- DEC-1030, DEC-1015: the dispatcher watches the GPU and server logs (a crash or 0-layer load: inbox and push); a
  rebuild without its semantic store has failed.
- DEC-1031, DEC-1043 (2), DEC-1048: the embedder stays on the GPU; no private reranker beside the shared one
  (`tools/rerank_service_slot_hold.py --watch`); the interim GPU-slot module is the machine-wide guard.
- O-5 (DEC-994, DEC-998 scoped): one stall net, the dispatcher's stale line and the sentinel's push, and the
  quiet-hours hook; at session start Remote Control, one test push, `log/cto-session.txt`; `log/cto-standby.txt`
  kept while the sentinel reads it (owner, D-3 answer 7).
- DEC-1065 (standing): no CPU fallback for embeddings anywhere (the shared GPU embedders unreachable: the semantic part
  unavailable, named, keywords answer; never a private embedder on the CPU, as the reranker's ACT-RERANK-WAIT-1);
  search respects role separation (`gov retrieve` filtered by the caller's `role_paths`, before W2-127 and the restart).
  DEC-1064: sandboxed workers run no `gov retrieve` and no real-model test until then (W2-127 closed; DEC-1114 holds): (the 09:00 sweep: recommended to supersede)
- **Standing practice, the owner (2026-11-04):** whenever the CTO waits on the owner or the operator, it writes
  `log/cto-standby.txt` (what it waits for) and ends it when the wait ends, so the sentinel raises no false alarm;
  `tools/sentinel_check.sh` runs while `dispatch/sentinel-expected` exists (the sentinel's login, Remote Control,
  tmux session or watch log down: an inbox item, and the CTO pushes the owner at any hour); **bisect only in a
  throwaway `git clone` under `/tmp`, never `git bisect run` in a linked worktree of the main repository** (it exports
  `GIT_DIR`, and a test's `git init` re-initialised the main repository as bare on 2026-11-04 00:31); a process is
  stopped only by the pids a check named, never by a text match.
- DEC-1045: no gitleaks scan here (`secrets.yaml` `scan: off`); a weekly full scan only on the owner's approval.
- DEC-1040 (3), DEC-849: a false refusal is worked round at once by an equivalent form and named; a true one is taken.

## Tickets, tests, reviews
- DEC-953 (1, 2, 6), DEC-954: nothing gates this repository until the Gov OS is whole; closes on the audit's 10
  practices; nothing deleted from the product; the guard's five rules; `gov close` proved on W2-81 and EXAMIN's copy.
- DEC-1010, DEC-916: moderator triage; a finding blocks only in scope, in ordinary work and failing open or losing
  work; two rounds, then the owner once; READY by `tools/verdict.py`.
- DEC-968: scoped runs only (`tools/select_tests.py`); a close refused only by its own failure; no accepted reds.
- DEC-959, DEC-988, DEC-989: every merge through the queue (`tools/land.py`), one per ticket; merge and close one step;
  except the refactoring's merges as built (D-1, D-4b: one review, READY by code, the CTO merges; DEC-1052, DEC-1055).
  Lands in batches of two or three tickets with disjoint paths; no commit freeze during lands (DEC-1157 (4), (7)). A
  critical-path ticket landing first: (the 09:00 sweep: recommended to amend)
- DEC-995, DEC-996: a role is its reads and writes; a skill never widens it; mixed tickets split first.
- DEC-1007, DEC-1012 (1), DEC-999: leads start only from `dispatch/ready.txt`, returns land in its inbox, one batch
  from `land.txt`, `status.txt` the truth; claims committed before a lead starts; two lines ready at all times (claim,
  worktree, brief, DEC-1157 (6)); every refused start logged (DEC-1157 (13)).
- DEC-979 (2): the CTO's tools: their own tests; a review only where a change could fail open or lose work.
- DEC-1052 (the interface check moved to the claim: the CTO states it, DEC-1157 (3)): templates per session kind, ticket and brief, READY and DONE computed from their required fields by code;
  the suite cut to about 5,000 before D-10, every kept KPI line covered, the list to the owner first; memory embeds
  no `tests/**`, close, checkpoint or probe records, nor orchestration closes, reviews, sessions or nightly (M-4,
  DEC-1055 (3)); the hidden half lives in `~/gov-os-eval/`, outside every worktree (G-3, DEC-1055 (4)).
- DEC-1052 G-14, DEC-1054, DEC-1056, DEC-1059 (live since ACT-G14, `4edd196c`): role separation by path checks; the test designer never reads the ticket's new
  code or new unit-test files; the engineer never reads its own ticket's acceptance tests, wherever they sit; shared
  test files, other tickets' tests and the integrated code stay readable (DEC-963).
- DEC-1063 (live since ACT-G14b, `e02d55e40424`): a ticket with `class: coordination` (today W2-00) has as its own
  tests only its own folder; a test designer and an engineer paired under a coordination ticket are not separated by
  the guard, so a pair runs under its own ticket's id (the lead template says so). Basis: question 1.
- DEC-1050 (its (5) superseded by DEC-1158; T-1, Q-1, G-1, G-2, O-7 kept): this repository kept; no full `gov check` in leads' runs (T-1); attribution once each way (Q-1); the
  landing refuses an acceptance-test change but the designer's or owner's (G-1); guard rules 1 and 5 judge only
  targets that resolve (G-2); review effort as it is (G-12).
- DEC-1053: D-0 done; `w2/W2-78` and the in-flight branches with unmerged work wait for D-9. (the 09:00 sweep: recommended to amend)
- DEC-1052, DEC-1055: the plan (`packages/LIFT-1/P1-PLAN.md`): G-14, D-3, D-4 beside D-4b (memory, as refactoring
  work, no leads; D-4 two heavy slots, D-4b one and the rebuild lock), the final memory measure, re-pin window 3 and
  the integration store, D-5 to D-9, D-10, the lift. No run the old way. D-4 to D-10 done; D-11 (the weekly basis review) not started: (the 09:00 sweep: recommended to supersede)

## Rules about rules
- O-11, DEC-1012: a rule broken twice becomes a mechanism only if it passes DEC-1010's test; a slipped ceremony is
  assessed under the basis instead.
- O-11, DEC-1003, DEC-982: a practice from the CTO's tools enters a product ticket after a week in use and the basis,
  proposed weekly as one batch.
- DEC-1052, the basis (standing): one question, five tests (`INTENT-DEC-1052.md`); applied at adoption, on symptoms
  and weekly with measured costs; the lift-or-remove list to the owner first; a practice enters the product once proven.

## Records and commits
- DEC-861, R-10 (kept by DEC-1057 (6)): the CTO commits the owner's decisions (`Task: decision-record`, `Role: orchestrator`, `Decided-by`),
  one commit per batch (hourly or at handover); `record/w2` synced hourly and at session end; `--main` lifted.
- R-12 (DEC-1057, lifting DEC-896 item 2 and DEC-927 item 2): `Task:` and `Role:` on every commit; `Implements:` optional; a decision and its ticket files in one commit.
- R-6 (DEC-1057, lifting DEC-511): no committed `gov checkpoint` record per round; the prose checkpoint, PreCompact and SessionStart stay.
- R1-21: `tools/structural_pass.py` after each landing and record commit, a notice only.

## Lifted (was `LIFTED-BY-DEC953.md`, `69a0e5d89f04`; kept built and tested in the product unless "ended")
- DEC-953: `gov close` and its gates here, escalations, repair tickets, the work-without-a-task gate, containment and
  trailers as refusals, the ratchet lists and their owner commits, probe staleness, the re-pin ladder, the memory
  arithmetic as a gate, the guard beyond its five rules. Ended: the pre-close gate (a) to (h), `record_checks.sh`,
  close windows, holds and cut-offs, the 90-minute rule, the red-nightly hold, the nightly's booking window.
- DEC-1045: gitleaks here. DEC-1050: the guard harvest, `refusal_watch.sh`. DEC-1052: record ACTs (O-6); round
  records (R-6); the two-commit rule (R-12); a ping per owner item (R-11); heartbeat checks, the
  Stop-hook waiter check, the scratch `deadman.py` (O-5); §0's copies and RULES-IN-FORCE (R-9); `gate_check.py` (O-10).
- DEC-1158 (2026-11-13), **the emergency of 2026-11-02 and its freeze** (the section "The emergency, until the owner lifts
  it" removed; `log/emergency-stops-20261102.md` is history): DEC-1032 (2), (3)(v) (the freeze; its band (5) removed by
  DEC-1157 (5)); DEC-1033 (1), (4) (its (2) kept as DEC-1065's line); DEC-1047 (1), (2) (its (3), DEC-1010, kept);
  DEC-1051 (everything stopped until the refactoring and the re-pins, nothing scheduled but the dispatcher: met at re-pin
  window 5); DEC-1049 (no nightly or full suite until the owner's word: the nightly back under DEC-1132 (4), beside the
  leads by DEC-1159 (1)); DEC-1050 (5) (nothing scheduled until the refactoring; T-1, Q-1, G-1, G-2, O-7 kept).
  **Spent:** DEC-1037 (3) (the full run until green: D-10's ruled red counted, DEC-1126 (7)); DEC-1039 (3), (3b), (4)
  (green, then the owner lifts the emergency: DEC-1158 is that lift).
- DEC-1157 (2026-11-12): **DEC-1138** whole (was: the lead cap of five through 11-12's working day; no new lead run after
  03:00 before the nightly; its (2) safety nets kept by DEC-1149 (1) and DEC-1157 (14), its (4) by DEC-1149);
  **DEC-1156 (8)** (night pushes "until the owner says they are asleep": now at any hour, DEC-1157 (1)); DEC-1140 (2)'s
  dispatcher lead cap and (5)'s "the night hold for the nightly stays"; DEC-1018 (1)'s landing hold; DEC-1021's quiet
  hours for a decision that stops or delays a lead; DEC-1032's CPU band, DEC-1038 (4)'s T1 band and DEC-1039 (1b)'s CPU
  term; ACT-DISPATCH-1's `max_leads`; the CTO's one land per batch; commit freezes during lands; the interface check as
  a lead stop (moved to the claim); a merged dependency as unmet for starting (DEC-1088 (5)(a) changed); a land holding
  all three heavy slots (DEC-979 changed). DEC-1149 (3): the usage stop (DEC-1140 (6)'s 97 % line; DEC-1115 (4)'s
  priority rule).
- DEC-1159 (2026-11-13): DEC-1132 (4)'s "with nothing else running" for leads (the nightly runs beside them).

## Approved restarts by class (owner, O-6)
Approved (owner, DEC-1057 (4), D-3 answer 4, 2026-11-03): the five classes in `governance/project/orchestration/RESTART-CLASSES.md`
(the shared embedder :11434, the query server :11435, the shared reranker service, the CTO's samplers and slot
watcher, the sentinel). Each is restarted by the CTO from its committed config, with its check, without an ACT; any
other restart is an ACT.
- DEC-1060: lens B's q03 rewritten to DEC-1033's rule; a measure question never rewards a replaced decision.
- DEC-1067 (standing for D-4b; its (b) changed by DEC-1071: a structural fix judged on all 80; its (f) by DEC-1090,
  DEC-1095 (the reranker's request cap measured, 64) and DEC-1159 (2) (`MAX_REQUEST_CHARS` about 48,000 after one GPU-window reading, option 5 the fallback)): the memory measure's hidden half never chooses a method (adopted only if it wins on
  the visible half alone; the hidden half reported separately; hidden ranks never in the index or on integrate);
  labels change only where wrong, never to fit results; GPU safety for experiments (the 15.5 GB backstop; no measure or
  rebuild beside one; the GPU back in budget between); no install until the owner decides the bigger models. GPU safety's "no measure or rebuild beside one" (with prompt rule 8's commit freeze): (the 09:00 sweep: recommended to amend)
- DEC-1068 (2026-11-04): re-pin window 3 done (`pin-8284fb408bd4` live, registry `b05f62b8`; the integration store at
  `8284fb40` with `embed_headers` on); class 3 gains the force-stop (SIGKILL 30 s after SIGTERM); the reranker's memory
  release (W2-112) goes into window 4; h02, h24 and any hidden label are corrected by the owner's operator, outside the
  guard, nothing reaching the CTO. Basis: question 1 (sessions run the product measured, not the old pin).
- DEC-1069 (2026-11-04, standing for the measure): the set is about **40 per half** (DEC-1009 amended); **R5** (each
  governing domain at least 10 % of each half, no subsystem above 25 %); **R11** (no question whose answer changes with
  ordinary work unless its gold is computed at the measured head); **R1.3** (test-harness code never governs a code
  fact, except about the harness; a generated Contract record counts only when its own status is ACCEPTED); the
  measure script writes a reason line for every automatic re-anchor; every run keeps every search's ranked output
  (`~/gov-os-eval/runs/`), so an approved label change is re-scored without running again; the reranker trial runs
  all three candidates, adoption by its written rule only; a standing model bench. Basis: question 2 (a measure that
  is wrong or keyword-only misjudges memory). *(The trial's (12)-(13) amended by DEC-1070; (12) changed by DEC-1076
  (4), then mxbai dropped by DEC-1079: the comparisons are among the Qwen3 models only.)*
- DEC-1070 (2026-11-04, standing for the measure; its (2)-(4) changed by DEC-1074 (1): the hidden 40 and the spent 60
  are now tuning or diagnostic sets too, only a fresh set gives a verdict): **three sets, three jobs**: the visible 40 tune and choose; the
  hidden 40 check (counts only, never choose; a visible-only gain is suspect); a **new measurement set** (fresh, blind,
  by the rubric, a new writer, outside every tree) is the verdict, measured only at decision points. Memory is reported
  as those three figures. **The choice rule:** hit@5, then MRR of the first gold source from the kept ranks. **Recall
  first:** no new method chosen until the recall diagnosis is in; fixes are generic, never aimed at named misses;
  the rerankers (mxbai, Qwen3-4B) and the embedder trial wait for the 0.6B's new record; M1-M5 also confirmed on the
  measurement set before window 4. **Labels** are audited on a schedule, all questions at once, never because one
  missed. Basis: question 1 and question 2 (selection pressure from named misses fits the tuning set).
- DEC-1071 (2026-11-04, standing for the measure; its (3) changed by DEC-1074 (4): consistency within 5 points on
  sets of about 80, and the spent 60 are no longer a confirmation set, DEC-1074 (1)): **structural fixes only**, never per question, from one structural
  review (chunking, embedding, ranking, the graph). **The rule:** a structural fix is judged on **all 80 together**
  (hit@5, then MRR), the hidden half in counts only. It is adopted if the 80 do not fall and the halves' gap does not
  widen. **The proof is consistency:** the halves agree within 3 points; then memory-verdict (60) is measured once as
  the confirmation (if it disagrees, to the owner first). **Then** all three rerankers on the three sets. The
  nonexistent-id question passes on `UNRESOLVED_IDS` naming its id, scored apart from hit@5. Basis: questions 1 and 2.
- DEC-1072 (2026-11-04): D4B-STRUCTURE's order stands; its steps 5-7 are prototypes in measure clones only, back to
  the owner with figures before any product change. **Step 7 covers every stated link:** a census of each kind of
  relationship stated (records, front matter, trailers, text) against the graph's edges; the missing kinds built as
  the evidence supports; a drift count (decisions retrievable as current though superseded or amended). **Memory-building
  is a Wave 0 practice** for every adopted repository, kept in its ticket as D-4b goes, a kernel skill after the
  refactoring.
- DEC-1073 (2026-11-04; its "within 3 points" is now 5, DEC-1074 (4)): the measurement set is used once, **after the structure is final** (D4B-STRUCTURE steps 2 and
  4-7 measured first), and only if the halves still agree within 3 points; otherwise to the owner. **Drift:** the
  register is the authority. The archive's 110 "spent" decisions go to a separate status-reconciliation list. A
  PROPOSED decision is not current, and retrieval must show its status. M5 is retested with the register links.
  **Link integrity** (clean-up, a cheap incremental checker, link templates in every recording role's skill and brief)
  comes to the owner as one package before anything is built. **Standing (L-0075):** every wait and every stop is by
  process id or process group, never a name match, through `.gov-runtime/scratch/orchestrator/tools/proc.sh` (`wait
  --max`, `stop --grace`, `pgid`).
- DEC-1074 (2026-11-05; its (3) changed by DEC-1076 (1), its (7) O1 (A) by DEC-1087 (3): W2-116's refresh after every
  merge is built): **67.8 % is the 0.6B's honest figure** (v456 + the stated links, `memory-verdict`).
  - **The sets:** every used set (visible 40, hidden 40, the spent 60) is now tuning or diagnostic; only a fresh set
    gives a verdict. A **new verdict set of 80** is written blind by a new writer and cross-checked, then used only at
    the next decision point.
  - **The next lever:** the 60's 19 misses are classified by an independent role (kinds and counts) before the owner
    chooses it. Nothing is tuned or trialled until then.
  - **Consistency:** within 5 points, on sets of about 80.
  - **Approved for re-pin window 4,** tests first: v456 into W2-32, the stated links into W2-92.
  - **W2-54's premise** is rewritten by its test designer.
  - **LINK-INTEGRITY is adopted:** O1 (A), O2 (A); unlinked mentions are notices from the start.
- DEC-1075 (2026-11-05; its (1), the folders, changed by DEC-1076 (1)): ACT-MSET-3/4 approved: the verdict set of 80 (`memory-verdict-2`, declared in both path maps,
  measured by the CTO only at the next decision point, counts only), written and cross-checked outside the CTO's system;
  failure-memory 4, a shortfall of at most 2 to `decision`. W2-32's S11 (v456) as worded. Basis: questions 1 and 2.
- DEC-1076 (2026-11-05): the 80 by the 60's writer and checker sessions (resumed, new settings); the writer varies its
  phrasing by role. **The reranker trial now** (mxbai, then Qwen3-4B 8-bit, the 0.6B beside), then phrasing, then the
  embedder; adoption the owner's. **The trial's rule:** on the 40 + 39 + 59 together, hit@5 then MRR, the spread between
  the three sets not wider than the 0.6B's; eligible only at a median ≤ 3.0 s alone, no timeout at 10 at once, no shape
  at the GPU budget. The checker lists every other place stating an answer. Basis: questions 1 and 2.
- DEC-1077 (2026-11-05): the trial's second window: mxbai with its own template (rehearsed on a stand-in), the 4B at
  24 candidates, the reranker off as a control, each on the 138 under DEC-1076 (4)'s rule beside the 0.6B; the 4B not
  adopted now; a research survey and the memory's invention disclosure; nothing adopted before the owner decides.
- DEC-1078 (2026-11-05): `memory-verdict-2` (80) ready (checks pass; the cross-check closed at round 2); unused until
  the next decision point, after the research package and the trial's re-runs; measured once, counts only. The
  rubric's next version: source families (a gold source and its generated twins counted as one) and missing
  alternatives (DEC-1076 (5)). Basis: questions 1 and 2.
- DEC-1079 (2026-11-06): every comparison with its gains, losses and an exact McNemar test (standing for the measure);
  L2 (where the 31 misses left the top 5) and source families in the measure's code now, then every kept run
  re-scored; after L2, the lift normalised and the moves bounded (L3), the three rerankers replayed under equal
  weights; L5 phrasing; L6 one measured test; the 0.6B stays; after L3 one window for the cascade beside the 4B at 24;
  the best onto the fresh 80 once; no install until then. **D-5, D-6 and D-9 start now** (CPU), the memory measures
  keep the GPU. Every report ends with DEC-948's block. **mxbai is dropped** (closed as measured, not replayed; its
  downloads kept): the reranker comparisons are among the Qwen3 models only (the 0.6B, the 4B at 24, the cascade).
  Basis: questions 1 and 4.
- DEC-1080 (2026-11-06, standing; its (2) changed by DEC-1081 (1): no `git -C` rules, and its premise by DEC-1082 (0):
  the user-level settings allow all, the guard is the check): the CTO reads with the Read and Grep tools, runs one simple command per call, no
  `cd … &&` chains, and says in one line before any command that will prompt what it does and why; the same rule in
  every agent's brief. P-PERMISSIONS-1 approved with read-only git through `git -C` only; the settings change is the
  operator's ACT (`ACT-PERMISSIONS-1.md`). Basis: questions 4 and 2.
- DEC-1081 (2026-11-06): ACT-PERMISSIONS-1 without the `git -C` rules; W2-128 filed; gte-reranker-modernbert-base and
  zerank-1-small measured now (their downloads an ACT): every Qwen3 model and these two score each kept candidate list
  of the 138 once in one quiet window; then replays at no GPU cost on the fixed pipeline (alone; by question type;
  cascades; two merged), the grid declared first, judged with McNemar; a winner's speed and GPU measured for real before
  the owner; the best onto the fresh 80 once. Nothing adopted or installed before the owner decides. Basis: 1 and 4.
- DEC-1082 (2026-11-06): the user-level allow-all accepted (the guard is the check); ACT-PERMISSIONS-2 applied; the
  three stopped agents started again (L5 from its lines if sound); the DEC-999 labels a priority fix ahead of the
  levers (window 4's builds checked first, else a ticket, tests first); the guard refuses the hidden sets outside the
  repository to engineer, research and orchestrator (an ACT); the spill reading investigated; the score-once window
  after its review. Basis: 2 and 4.
- DEC-1083 (2026-11-06; K9's bar changed by DEC-1097 (1)(d) to right end to end, met per DEC-1098; W2-66b, W2-90c by
  DEC-1084; W2-33's layer lines by DEC-1087 (13)): D9-FATES approved (the auditor checks the 792 lines before any
  edit); K9's memory bar 85 %
  hit@5 on the fresh 80 once, on the pin with W2-92, W2-32 S11, W2-131 and the chosen reranker (95 % the target);
  W2-32 S6 dropped; W2-15b out of K9; W2-128 in K9; W2-128's ready check computed by code (only advisory items warn);
  W2-131's follow-up a ticket, tests first; grid v2 and v3 accepted. Basis: 1 and 2.
- DEC-1084 (2026-11-06): D9-FATES §5 decided (W2-111 open, LITE, outside K9; W2-55 S1 re-worded and closed; W2-66b a
  D-10 red-fix item; W2-90c its own ticket) and the fates applied; exit criterion 5 re-worded; spill floor 2,048 MiB;
  the measure re-anchors in memory (W2-61h, tests first); ACT-GUARD-SETS-1 decided (after window 4; the CTO's tools
  take the sets root first); L5 and an 80-candidate 0.6B cell measured. Basis: 1 and 2.
- DEC-1085 (2026-11-06): the memory build finished first (the open list to the owner); W2-134 filed (S8's code, tests
  first); the two-reranker cells measured, adoption to the owner (DEC-1043); no 4B embedder; the search-again test
  (two and three attempts: misses recovered, tokens, time, wrong claims); its practice and the end-to-end experiments
  (top 5, 10, 20, today's bundle, 40 unranked; each with search-again; an independent grader) as packages, nothing run
  first; the fresh 80 unused until the owner decides what it measures. Basis: 1.
- DEC-1086 (2026-11-06; its C's cap changed by DEC-1091 (1): no cap): S11 re-worded ("within 2 of the harness on the 138"; speed against the pin in window 4);
  W2-135, a 4,000-character cap per item (a guard against one-line files; the total size tested in E5); the
  search-again reader sees the 138 (no tools, no transcript, counts only; the pilot, then the owner's cap). Recorded,
  acted on only at the owner's go: no re-pin and no experiment before the owner reads the seven answers. Basis: 1.
  The spent "no re-pin and no experiment before …": (the 09:00 sweep: recommended to supersede)
- DEC-1087 (2026-11-06): before re-pin window 4, all done and tested:
  - W2-135 and S11 (DEC-1086);
  - the integration store refreshed now (if safe);
  - W2-116's refresh after every merge, the daily backstop and the worktree store path;
  - W2-129 (`gov links`);
  - the dependency-mapping tool's decision, spec and KPI package (its home and timing assessed);
  - the status block fixed (countdown, (a) to (d), the sixth line);
  - a clean tree and the worktree list;
  - window 4 as a rehearsed ACT;
  - dates re-estimated.

  After the re-pin: the parallel-agents and memory test first, then E0 to E5 and the fresh 80; M3's adoption after
  all the experiments. The three layers stay in Wave 2 (reversing W3-P23): after the lift, streams and a trial plan
  as a package. Basis: 1. The spent "before re-pin window 4" list: (the 09:00 sweep: recommended to supersede)
- DEC-1088 (2026-11-06; its (5)(a) changed by DEC-1157 (9): a dependency merged into `w2/integrate` counts as met for
  starting, by `plan_override: DEC-1157` on the ticket, closing still waits for it to be closed; the product's plan check
  reading "merged" parked to Wave 3): `gov plan`, W2-136:
  - it proposes the batches deterministically, and the orchestrator approves them into the ready list;
  - the template's `reads:` (wide, warnings), `needs:` and `waits_on:` (the order); the ready check refuses a new
    ticket without them;
  - built right after window 4, live at the lift's re-pin;
  - `gov launch` refuses a lead not in the approved batch or with unmet waits (W2-136), and any session when the gate
    is closed or limits would be passed (W2-20); one override with a decision id; every refusal names what it waits
    for.

  **Standing:** a closed ticket is never edited (a fix or upgrade is a new ticket); an open ticket may change, marked
  with the decision that made it, and `gov links` flags a change without one. Basis: 2. The standing "a closed ticket
  is never edited" for a defect inside its own scope: (the 09:00 sweep: recommended to amend)
- DEC-1089 (2026-11-07): re-pin window 4 done (`pin-bcea09060ebc` live; `pin-8284fb408bd4` kept for rollback); the
  go for START-NEXT-SESSION §4, the parallel-agents test's result to the owner **before E0**. **K7 done for Wave 2**:
  the pin ladder by hand until Wave 3 (W2-17, W2-18 Wave 3); the first numbered, frozen release (cut by the owner,
  hash-checked) and CAP-45.a's exit-criterion-7 paperwork are W2-27's (`packages/K7-W2-REMAINDER.md`). **Usage,
  standing: never pinged or alarmed** (DEC-942 item 6 ended); readings in `log/usage.txt`, each experiment's tokens and
  cost in `log/spend.jsonl`, shown in the digests. Basis: 1 and 4.
- DEC-1090 (2026-11-07): PAT-1 read; **E0 and E0b go.** W2-137 (`DAEO-5emz`, the reranker's request cap raised, measured
  20 and 10 at once in a GPU window between experiments) and W2-138 (`DAEO-rmhj`, the store's commit in every result;
  the line-hash check in the worker brief) filed, tests first, beside the experiments, **live at the lift's re-pin**,
  before the three layers. Overlapping slices decided after E0 on the 138. **CAP-45.a: option A** (a CIT-P note to Wave
  3, in W2-27); the release cut after the lift's re-pin, before W2-81's run. Basis: 1 and 2.
- DEC-1091 (2026-11-07, standing for the experiments): **no budget cap**; usage is never a reason to stop or hold the
  work; E2 now, E3 to E5 after it (their design package first, DEC-1085 (6)). **A runaway brake only:** an experiment
  stops when its spend passes twice its own projection, and the stop is reported with its cause. The "may be
  incomplete" instruction line in E2 to E5 (E1-DECLARATION's amendment). Basis: 1 and 2.
- DEC-1092 (2026-11-07): **E2 accepted:** "search again once" a standing practice, as a package (skills, role templates
  through W2-128, hooks if needed). **E3-E5-DESIGN approved** (brakes at twice each projection; the readers and graders
  see the hidden and spent sets). **The fresh 80 and the K9 bar wait for E3 to E5 on the 138:** the CTO brings the
  expectation, every gap or fix, and how the 80 runs; the configuration and the bar are chosen from the 138 before the
  80 runs; on the 80 every condition may be measured, only the one chosen beforehand is judged. Basis: 1.
- DEC-1093 (2026-11-07): the CAP-45.a note approved (4.3; CAP-45 and CAP-45.a to Wave 3; the "in Wave 2" clause
  withdrawn, hashes kept beside the signed tag); **W2-139** (`DAEO-ongl`, the apply) and **W2-140** (`DAEO-5ce2`, W2-49's
  tests) merge and close in one batch, one green run, outside an experiment window; DEC-841's nine to P1-11, else
  exceptions in W2-46's record. **W2-141** (`DAEO-xwro`): the guard refuses an engineer's Grep, Glob or recursive Bash
  search that can reach its own acceptance folder unless excluded (saying how), at the lift's re-pin ACT; **until then
  every engineer brief carries the exclusion line.** ADR-0002 refreshed, reviewed, to the owner, after the experiments.
  Basis: 2. The spent W2-139/W2-140 sequencing: (the 09:00 sweep: recommended to supersede)
- DEC-1094 (2026-11-07): **G1:** profile the shared reranker (GPU utilization in a 20-search burst, each request's time
  split); if the GPU idles between requests, (b) batching as a new ticket, tests first, live at the lift; if saturated,
  fewer scored pairs per search after E3 to E5; (a) only beside (b). **Search again once** is the standing practice
  (SEARCH-AGAIN-PRACTICE as recommended): in the project briefs now; the kernel skills by **W2-142** (`DAEO-qskx`) at
  the lift; W2-128's T-0 line; no hook; the adoption count weekly in the digest, never a gate. Basis: 1, 3, 4 and 5.
- DEC-1095 (2026-11-07): **W2-137 live at the lift as it is** (the cap of 64; its readings within noise). G1's profile
  repeated in the next quiet GPU window, both readings with E4's result. Then the harness fix, its review, E0b, E4, and
  the fresh-80 package with the K9 bar. Basis: 4 and 1.
- DEC-1096 (2026-11-07): **a repository glossary as part of memory (Wave 2):** the repository's vocabulary (terms, id
  forms, record kinds, commands, namespaces) and a code-name map, generated from what it states and refreshed with the
  store after every merge; curated terms only with a decision id (`gov links` checks); a memory record consulted when a
  search does not answer, referred to by the skills and templates. **Tested now** (E2's condition with the glossary
  consultable, on the 138, McNemar against E2, wrong claims and cost beside); if it helps, it joins the fresh-80
  configuration. The package (wording, spec, KPI lines, tickets, W2-88's Wave 0 line, estimate, dates) beside the test;
  the build after the test and the owner's approval, tests first. Basis: 1.

- DEC-1097 (2026-11-08): **the fresh 80** judges window 4's pin, pool on, today's bundle, search again once, at
  `c00d525f` with the visible-40 control first; every experiment on the 80 for data, only that configuration judged;
  **K9's bar: right end to end ≥ 85 % with wrong claims ≤ 5 % (on 79: ≥ 68 right, ≤ 3 wrong), target 95 %, hit@5
  beside it**; readers and graders read the 80; the owner's checker's staleness pass first; FRESH-80-1's twenty fixes
  and fault rule as written; no commit, rebuild or GPU window during the run; **W2-139 and W2-140 held until after the
  80.** ACT-GUARD-SETS-1 rebuilt (the reader folder hidden, W2-84's hidden-half cases deleted), rehearsed, applied by
  the operator before the 80. The seven-reviewer readiness review (fix only fail-open or verdict-breaking, two rounds;
  any retrieval change reruns E0 and E2 on the 138 first). If retrieval changes after the verdict, the 138 re-measured
  at the release commit (W2-27 item (a)). **Keep the 0.6B** (M3, M1 for data on the 80). G3 no change before the 80.
  **The glossary (item 6): (b)**, redesigned beside the agent's own words, ranked toward decisions, for asking,
  retested on the 138 after the 80; `gov glossary` built only if it helps. The overdue items' fates: W2-141, W2-20's rebuild, ADR-0002, a no-private-reranker
  ticket before the lift; W2-130 and P-SELECT-GRAPH now on the CPU; G1's fewer pairs and P-LB-PRODUCT-1 after the lift;
  Q07/Q14 after the 80; the label audit at each release cut and before a new verdict set (rubric v3 after the 80); the
  embedder trial a Wave 3 row; the keystone count from the plan's list; the old window scripts fixed or retired.
  **Standing:** every decided item with a stage trigger enters `packages/DECIDED-NOT-DONE.md` when decided, ticked off
  with its commit when done. Basis: 1 and 2. The spent "W2-139 and W2-140 held": (the 09:00 sweep: recommended to
  supersede); "no commit … during the run" as carried by prompt rule 8: (the 09:00 sweep: recommended to amend)
- DEC-1098 (2026-11-09): **the fresh 80 accepted; K9's memory line met.** **Standing: Gov OS's memory standard** is
  the measured configuration (the 0.6B reranker, the pool on, today's 6,000-token bundle widened to sections, agents
  searching again once), and every adopted repository builds it at Wave 0 by W2-88's practice and proves it with its
  own tuning set and a fresh verdict set, measured once (W2-88's lines to the owner as a package). P-SELECT-GRAPH: do
  not build (DEC-1062 closed); three cheaper fixes as proposals; the code route stays, confirmed with figures. W2-130's
  sitting accepted (A-G; H1 (b): open and in-progress tickets only, KPI 4 changed; H2 as recommended). **A
  sandbox-and-guard experiment before W2-56 builds** (bar: every action judged right, 100 %; path-map guard alone
  against guard plus generated sandbox; the guard alone kept if the pair cannot reach it; the design to the owner
  first). ADR-0002 accepted, re-read at the lift's re-pin. The work in order: item 8, Q07/Q14, W2-139/W2-140, the
  sitting, D-5 and D-6 part 2, D-10 on the owner's word, the lift. Basis: 1, 2 and 4. The spent "the work in order":
  (the 09:00 sweep: recommended to supersede)
- DEC-1099 (2026-11-09): **the sandbox-and-guard experiment approved** (write scope in the bar; names-only listings of
  held-out material allowed; the CTO's session unsandboxed; an outside labeller, a second on 10 %; the held-out halves
  sealed by a path-map ACT; three rounds; a held-out failure reported, not fixed; if both miss, tuned A as an ACT only
  if it cuts false refusals with no new wrong allow; no cap, the brake at twice the projection), **run beside D-10**,
  W2-56's result-independent tests meanwhile. **W2-88's lines S10-S17 adopted; EXAMIN's copy is the practice's first
  full run** (no separate proof repository; later adoptions follow it as fixed); tuning set 80 in two halves; outside
  writers; the nonexistent-id row a ticket now. W2-82 after W2-27; G1's fewer pairs after EXAMIN's copy; W2-15a closes
  with W2-32; **W2-139 and W2-140 merged before D-10.** Basis: 1 and 2.
- DEC-1100 (2026-11-09): **ACT-SELECT-FIXES-1** (the test-map couplings; W2-66's record-only case always run), pinned by
  **W2-66c**, tests first; a scoped selection after every landing outside a ticket that touches settings, the registry
  or the test map (widened if an emergency merge reds again), from one line in the `reference-transaction` hook (an
  ACT for the operator), in the CTO's tools first; into W2-115 only once proven in use. Basis: 4 and 5.
- DEC-1101 (2026-11-09, standing): **memory audited periodically with fresh questions** (Gov OS and every adopted
  repository via W2-88): a fresh set weighted to what changed plus older areas, cross-checked in at most two rounds,
  measured once against the bar (85 %, target 95 %), misses classified by an independent auditor, structural fixes only
  (to the owner, judged on earlier sets), the spent set into a regression pool re-run each audit, the next fresh set
  the verdict on the fixes; weekly while active (DEC-1125 (2); was every two weeks), monthly once stable; "not found" and "may be incomplete"
  counted weekly in the digest; an unindexed-path notice resolved within a day. **Automated independent sessions:**
  writers, checkers, labellers launched headless in walled folders, fixed briefs the owner approves once (hashed, not
  changed by the CTO), content chosen by rule (git changes plus a seeded sample), memory's search, run outputs, the
  CTO's scratch and other sessions' folders denied, only counts to the CTO. Order: the ACT (path map, guard, folder
  settings), the launch script (tests first, one review), the briefs to the owner, then default. Basis: 1 and 2.
- DEC-1102 (2026-11-09): **`gov plan`'s cycle break fixed before the lift's re-pin,** tests first: a cycle broken only
  at a ticket inside it; a ticket outside every cycle keeps all its waits (a new ticket, one review). Basis: 2.
- DEC-1103 (2026-11-09): W2-20's gate file by an ACT (`gov resources --init-config` from W2-20's code, rehearsed);
  D-4's 3 capped and 7 lifted cases back into the gates by an ACT (DEC-1061 amended for them); ACT-INDEP-WALLS-1's four
  answers as recommended. Requested: an operator-agent package (class (a) checks-only ACTs applied by an independent
  operator agent after rehearsal, a READY review and matching hashes; class (b) loosening ACTs on the owner's one-line
  yes; sudo the owner's; the CTO never changes a reviewed ACT nor applies one). Basis: 2 and 4.
- DEC-1104 (2026-11-09): D-4's ten cases by option C (the seven green into the gates now; D-10 decides each of the
  three red by design); **the operator agent approved as recommended** (classes (a)/(b), the owner's `yes ACT-<id>
  <sha8>` read from the transcript, the shared servers' settings (a), re-pins the owner's for now, the cron launches it
  from a queue, pushes for (a) for two weeks, built after the walls tests first); the landing selection's environment
  fixed before its results are relied on. **Standing: each ACT given as a message for the owner's operator;** the owner
  does only re-pins, pushes and sudo. Basis: 2 and 4.
- DEC-1105 (2026-11-09): W2-20 gets one exception round to DEC-1010 (S16 revised to a per-CPU measure first; R2-F1's
  stale readings resampled; one narrow review of those two); then the merge, `gov resources --sample` over a working
  day and `--remeasure`. Basis: 2.
- DEC-1106 (2026-11-09): W2-148's F15 fixed in one exception round (the agent restores only its own dry-run change;
  anything else: write nothing, refuse, hold the lock, P1 naming each file; the same in the (a) undo); **the guard's
  call log** (a hash of the action, the role, allow or refuse, never contents) by its own ACT; the commit freeze a file
  in the operator's install folder the CTO's session may not write; F7 kept; then ACT-OPERATOR-1. Basis: 2.
- DEC-1107 (2026-11-09): W2-148's F21 fixed in one tiny extra round before ACT-OPERATOR-1 (the owner-undo and
  crash-recovery paths exit non-zero and say "refused" whenever they leave another's files). Basis: 2.
- DEC-1108 (2026-11-09): the guard's call log as designed (hashes, never contents); W2-148's replay from a corpus the
  CTO's tool builds, checked against the log by sha256 both ways (tests first, before the first path-map ACT through the
  agent); the plain sha256 kept; the log hidden from the W2-56 tuner in a fresh window; every session refused writes
  into the log folder (in ACT-OPERATOR-1); the live-hook suites to a temporary folder (follow-up). Basis: 2.
- DEC-1109 (2026-11-09): the operator agent's reviewer brief approved; its operator brief approved with "unless the
  program's final result line asks for it"; the rest of the work restarted in parallel. **Standing: while an item waits
  on the owner, every unblocked item keeps moving in parallel within the machine's limits; never "nothing is running"
  while unblocked work remains.** Basis: 2 and 4.
- DEC-1110 (2026-11-09, standing): the standing operating rules at the top of the CTO's prompt and in START-NEXT-SESSION
  §2; a stop-hook check (an ACT) that blocks the CTO ending a turn idle while unblocked items remain, letting a named
  legitimate wait through; a fresh CTO session after the seven helpers report and before D-10; after the lift, each
  ready list covers several of `gov plan`'s batches ahead. Basis: 4 and 2.
- DEC-1111 (2026-11-09): W1-33's auditor case and W1-05's install case report-only until their features return (each
  out of the opt-in list by the switch that turns it back on); W1-46's research-install case OPEN. Basis: 2.
- DEC-1112 (2026-11-09): the sandbox experiment narrowed to set-up A beside D-10 (set-up B a Wave 3 row); W2-56 builds
  on the path-map guard alone with today's launcher sandbox; A's result and Q8's tuned ACT to the owner. W1-46's case a
  delegated P2. **Standing: the CTO brings the owner only P1s; re-pins, pushes and sudo; class (b) yeses; fixed briefs
  to approve once; changes to the owner's standing decisions; steps only the owner can do physically.** Basis: 4 and 2.
- Delegated (CTO, 2026-11-09, under DEC-1112 (2) and DEC-936 item 2.5): **W1-46's research-install case stays
  report-only permanently** (D10-REDS.md: the feature it tests is gone for good; a rewrite would test nothing today).
- DEC-1113 (2026-11-09): set-up A's four briefs approved once after two changes (the guard rules since DEC-1099
  included, the pinned commit one where they are live; overlap disagreements decided by an independent auditor under its
  own fixed brief, escalating only unsettleable or verdict-changing cases). Basis: 2.
- Delegated (CTO, 2026-11-09, DEC-1112 (3)): set-up A's overlap auditor also gets the disputed actions and each named
  ticket's allowed_paths (write scope cannot be judged without them); rule 2c and the walls under class 7, rule 2d under
  class 11; the call log and DEC-1108 (4) outside the bar (the log decides nothing; it began after the window); writer
  2's brief self-contained (restates writer 1's output schema).
- Delegated (CTO, 2026-11-09, DEC-1112 (3)): the overlap auditor runs on at most 40 disagreements a run, the launch
  script splitting larger sets, so each run keeps within the approved brief's budget ($10, 3,600 s) and the brief is
  unchanged.
- Owner, 2026-11-09 (under DEC-1113): set-up A's five fixed briefs approved once at labeller v3 bbff1249953b…,
  labeller-2 v3 e13b5f96d0e0…, writer-tuning v3 82134b3dd6b5…, writer-heldout v3 137a73d1df4c…, overlap-auditor v1
  b212a424062e… (full hashes in SANDBOX-GUARD-EXP-DECLARATION §12); the declaration's scorer escalates any settled case
  whose other label would change the verdict (§ A3). The approved list the launch script checks is written by the
  launch script's install ACT.
- Delegated (CTO, 2026-11-09, DEC-1112 (3)): W2-139's S3 ("a green validator") judged against integrate: the batch adds
  no new FAIL; the 5 FAIL already on integrate go onto D-10's red-fix list.
- Delegated (CTO, 2026-11-09, DEC-1112 (3)): ACT-SETS-GLOBS-1 also hides `runs/*/misses.jsonl`; W2-149's launch
  script passes `--setting-sources project` (F11, defence in depth) as a follow-up, tests first.
- DEC-1114 (2026-11-09): W2-56's S8 on Linux, (b): S8's reach and S10 deferred to Wave 3 as a ticket (W3-P28: ranked
  search for sandboxed workers without opening every Unix socket); S8's one-path form stays built, inert on Linux;
  sandboxed searches unranked, named and counted (S11); S9 and F4 unchanged; the rest of W2-56 merged now. A
  re-estimate package (FORECAST-W2-2) at today's measured pace beside the lead-hour method. Basis: 2 and 4.
- Delegated (CTO, 2026-11-09, DEC-1112 (3)): W2-56's review rows: R3 (a killed run's daemon folder outside the sweep)
  and R5 (leads lose GOV_STORE, TERM, TMPDIR) are follow-ups before W2-56 closes, tests first; R1 (the main
  repository's settings.local.json in worktree sessions) is W2-60a's; R2 and R4 are rows for W2-56's close review; R6
  (the CLI's config.lock placeholders, P-S7) is W3-P29.
- DEC-1115 (2026-11-09; its (4) changed by DEC-1122 (2): brought forward to 11-10, until the reset 11-15 09:00): yes to ACT-SETS-GLOBS-1 (the owner's operator by hand) and ACT-CLAUDE-COPIES-1 (the operator
  agent, its first live run; on a refusal the CTO says why and the operator applies by hand; the agent's yes form is
  `yes ACT-<id> <manifest sha8>` on its own line); TPL-6's Appendix A applied now. **Standing until the lift: past 80 %
  of the week's usage, only the lift's critical path runs; the rest waits for the reset.** Basis: 2 and 4. (Its (4)
  changed by DEC-1149 (3): usage never stops a lead or a worker.) The spent (4): (the 09:00 sweep: recommended to supersede)
- Delegated (CTO, 2026-11-10, DEC-1112 (3)): set-up A's seeds by the launch script's own draw, written to SEEDS.log
  before any content (the declaration's amendment A5; option (2) of the wiring lead's DEC-105 choice: commit-derived
  seeds are knowable in advance); the wiring's proposals taken: W2-149's allowed paths gain the walls' kinds.yaml and
  tree-exclude.txt; tree-exclude.txt gains governance/project/indep-briefs/**; model claude-opus-5-5 for every kind;
  labeller 1's round-2 delivery refused (20) unless every hand-label action has one; S16 and S20 to set-up A's
  deliveries and the declaration's overlap rule; the overlap auditor never appends to AUDITS.log; exit 18 for a rule
  script that cannot run confined. The pin amendment follows the wiring's merge and the rebuilt install ACT's apply.
- Delegated (CTO, 2026-11-10, DEC-1112 (3)): W2-66's DEC-891 record case, (a): files read by code (W2-149's
  indep-schemas/*.json) are not counted as records; a test designer revises the case (not (b), moving W2-149's
  schemas and its ACT; not (c), record-only, which fails open). W2-13's real-model latency under load: the existing
  load-sensitive route or the nightly, never a looser 0.5 s limit. W2-116's and W1-32's cases follow W2-56's S5/S15.
- DEC-1116 (2026-11-10): W2-128's kernel templates approved at `1bf23a0b3e77`, promoted as version 1.0.0 (the CIT-P
  ACCEPTED); yes to ACT-CLAUDE-COPIES-2 (the operator agent); ACT-OPERATOR-2 by the owner's operator after it. Basis: 2.
- DEC-1117 (2026-11-10): the dead-man's night limit stays 2 hours; the owner checks the phone's Claude notifications
  before any other channel; USAGE-1 (the week's usage by source, ticket and day, the ten largest, savings to decide);
  the spend log in one unit. Basis: 4.
- Delegated (CTO, 2026-11-10, DEC-1112 (3)): the close's serial phase: serial-only.txt's stale W1-16 ui_off entry
  re-pointed before D-10, then the close's plugin treats an entry whose cases an opt-in list leaves out as not in this
  run (W2-57's code); nightly.sh reports how many serial cases ran. gov accept enables the opt-in groups its own map's
  cases need; its map reader refuses or reads every listed id. The composed agents carry the role file's six fields
  through W2-153's composition, the approved 1.0.0 templates unchanged; W1-38's builder copies templates/; then
  ACT-CLAUDE-COPIES-3 for the owner's yes.
- Delegated (CTO, 2026-11-10, DEC-1112 (3)): PKG-D10a-scope, (b): gov accept enables only the `breadth` group its
  map's cases need; a KPI line resting only on `lifted` cases is reported report-only, not failed (DEC-1061 (2)); the
  map reader reads every listed id or refuses (no form dropped silently). W2-154 (the serial plugin, nightly.sh's
  serial count, the brief citation) after the lift.
- Delegated (CTO, 2026-11-10, DEC-1112 (3)): gov accept's round 2 (W2-96, merged 8f6e66a17): a run whose every line
  is report-only fails (stricter; the six whole-suite lifted tickets wait for their features to return); a possessive
  or other further line name refuses the cell; a line whose only case is listed in lifted but defined nowhere fails
  (a row, tests first, after the lift). W2-92's map row 128 fixed before the lift (it closes there).
- DEC-1118 (2026-11-10): **standing (rule 11):** fresh sessions at ~200k context; the CTO clears at ~200k and before **[(A) replaced by DEC-1141 (3): no token cap for any session.]**
  idles over an hour; ACT-preparation helpers on Sonnet, reviews, test design and engineering on Opus; every session's
  list-price cost logged. D (5-minute worker cache) once verified on this CLI; E and F trials after the lift. A
  model-tier investigation for the fresh session to finish (MODEL-TIERS-1). Basis: 4.
- DEC-1119 (2026-11-10; its (1) changed by DEC-1120: the rubric found, RUBRIC-1, is replaced by RUBRIC-2): the owner's tiered rubric of model and effort by task found first (the fresh session's first
  task) and applied before the lift: in practice at once, into the product through W2-33 and W2-60a with a trial
  exception before EXAMIN's copy; ACT-preparation helpers on Sonnet at high now; trials only where the rubric leaves a
  role open; not options 4 or 5 unless the rubric calls for them; option 6 as guidance; the default effort to high by
  an ACT; an inventory of the emergency's tools. Basis: 4 and 1.
- DEC-1120 (2026-11-10, standing): RUBRIC-2 replaces RUBRIC-1 and changes DEC-839 (1)-(3). Classes C3 (controls,
  kernel, Contract, (b)/(O) ACTs, re-pins, verdicts), C2 (product code, launch, gate, plan, test maps, schemas), C1
  (records, docs, scratch tools, tickets), C0 (mechanical). Opus high: the CTO, leads, senior engineers, C3 engineers
  and test designers, C3 reviewers, C2 FULL reviewers, auditors, adjudicators, checkers. Sonnet high: engineers
  (after the lift; through D-10 C2/C1 engineers stay Opus), C2/C1 test designers, other reviewers, product-spec,
  research, ACT preparers, helpers, writers, labellers, the operator agent. Haiku: watchers and C0. Promotion to Opus
  after two failed reviews or a fail-open finding; lower only by a trial on two or more tickets; max only with a
  reason; every spawn names model and effort; the spend log records tier, class and promotion. Basis: 4.
- DEC-1121 (2026-11-10): the ticket template gains `class` as version 1.0.1 (W1-08's DEC-105 case, (a)); its hash to
  the owner before it lands. Basis: 2.
- DEC-1122 (2026-11-10): the ticket template 1.0.1 approved (`bbfc068e58e2`); **usage (A) from now until the reset
  11-15 09:00: only the lift's critical path runs** (DEC-1115 (4) brought forward; **(A) ended at the lift, DEC-1126 (2)**); D-10 goes once ACT-PATHMAP-NS-2 is
  committed and gov check is green, the triage of the first run's reds to the owner; a fresh CTO session at the next
  quiet point. Basis: 1 and 2. The spent usage (A) and D-10 go: (the 09:00 sweep: recommended to supersede)
- DEC-1123 (2026-11-10): D-10 run 2 by option 1 (the lifted step alone, the fixes by role, run 2 from a normal shell);
  context-reproducibility's 34 errors fixed in the records now (product-spec, Sonnet); **standing until W2-115:
  `product-traceability-trailers` counts as a warning, not a hard block (Q-8), for D-10, the re-pin and the lift**;
  W1-01's three merges exempted by the owner's commit (ACT-W1-01-EXEMPT-2); **standing: a stand-by note expires after
  a set time** (ACT-DEADMAN-STANDBY-1, class (b)). Basis: D10-RECORD-REDS.
- DEC-1124 (2026-11-10): Q23 re-worded to a stable fact by an independent session (the Q07/Q14 process), not by the
  CTO; its 3 cases may stay red in D-10 run 2, fixed and re-checked by a scoped run after.
- DEC-1125 (2026-11-11, items (1) (2) standing): **the warm-query latency (W2-13, W1-19: 0.54-0.59 s against 0.5 s)
  a named red for the re-pin and the lift**, the budget unchanged, a low-priority performance ticket after the lift
  (profile, short time box, simple fix or evidence and options to the owner); **the memory audit weekly while
  development is active, monthly once stable** (DEC-1101 (1) changed), a scheduled tool for Gov OS and every adopted
  repository that replaces ad-hoc re-measures (DEC-1097 (4) folded); the night of 11-10/11 to the re-pin the lift's
  critical path (re-pin ACT, closes prepared, anti-drift audit, ready lists, the 09:30 digest).
- DEC-1126 (2026-11-11, items (2) (4) (5) standing): the re-pin done (`pin-797495bdfc70`, registry `8f00bb908`);
  **usage (A) ended at the lift, the 80 % brake stays** (changed by DEC-1149 (3): usage never holds a lead or a
  worker, the runaway brake stays a stop); W2-60a takes RUBRIC-2's lines now (DEC-105 apply now);
  **every ticket of an adopted product has a runaway brake at twice its projection, never a cap** (DEC-1091 (2)
  widened; W2-156); **the memory audit Mondays 21:00, 40 questions, first 11-23** (its three briefs to the owner
  before approval); W2-32 and W2-15a open at the lift, W2-32 S9 to be disposed under DEC-1097's end-to-end bar
  (DEC-1083 (2)'s hit@5 bar replaced); D-10's ruled red is the green run for W1-01b, W2-66b, W2-90c; W2-82 to P3; the
  permissions asked for on 11-10/11 to the owner by form with an allow-list ACT. Basis: questions 1 and 2.
- DEC-1128 (2026-11-11, items (2) (3) (4) standing): **no switched-off control returns and no new guard rule goes
  live unless set-up A's evidence shows 100 % on the path map's actions** (every covered action right, no false
  refusal, no wrong allow; actions outside the path map outside the bar); **the lift does not wait for set-up A**: the
  guard stays as today (the live hook of 11-09; W2-141's rule is NOT live: staged, its hook ACT not run, off until set-up A shows 100 %), live false refusals counted weekly from the call log, the guard's
  error-path faults (row 123) first after the lift; **set-up B dropped entirely** (not a Wave 3 row), leads not
  sandboxed, the path map and the guard are the controls, set-up A stays as the guard's measurement, the workers'
  launcher sandbox unchanged; DEC-1010's one rule for all roles investigated read-only first. Basis: questions 2 and 4.
- DEC-1129 (2026-11-11): W2-32 S9 re-worded to the end-to-end bar, met on the fresh 80 (W2-32 open with W2-15a; the
  exception to DEC-757 (6) for its file); **the memory audit's writer, checker and auditor briefs approved** (sha256
  `bc0894230e31`, `cea517b8da7d`, `37be41c3fb2f`; into the approved list by ACT-MEMORY-AUDIT-INSTALL-1); W2-60a's
  RUBRIC-2 lines a fresh round 1, at most two, judged only on those lines. Basis: questions 1 and 4.
- DEC-1130 (2026-11-11): **a `Verify:` pass on unreviewed tickets; reviewed tickets in progress launch on hand-built
  briefs until they close, `gov brief`'s refusal recorded in each** (the owner's exception to DEC-1083, those tickets
  only); a ticket before EXAMIN's copy so `gov brief` handles an adopted repository's tickets without `Verify:`; W2-94 and
  W2-93 by the walled writer route (an `evaluation_sets` ACT and writer briefs for approval). Basis: questions 1 and 2.
- DEC-1131 (2026-11-11, items (1)-(3) standing): **one bar, two rounds for every role** (DEC-1010 widened): judged only
  on the ticket's KPI lines and specification; every finding names its KPI line or is a row; at most two rounds per
  ticket, counted by the CTO by hand from the ticket's id and role (the ledger); **a blocking-only engineer fix is the
  same round**; a third round only by the owner's decision; the text by CIT-P first, the counting code after two
  weeks; `verdict.py` (a failed KPI line blocks) and `operator_run.py` (reviews per ACT id) fixed now. Basis: questions 2 and 4.
- DEC-1132 (2026-11-11): **the lift's closes by DEC-953's practices** (`tk close` and a close record; `gov close`'s gates
  return later through W2-115 with a no-change-merge rule, only on evidence); ACT-CLOSE-HISTORY-1 and DEC-1127
  withdrawn; **ADOPT-VERIFY-1 (d)**: a checked `Verify:` pass when an adopted ticket is about to launch (W2-174), W2-88's
  proposed tickets carry `Verify:`; the `rg` tripwire; the nightly's restart as an ACT after the closes (quiet hours,
  sized to memory; "nothing else running" changed by DEC-1159 (1): it runs beside the leads); set-up A's bar defined for the owner's approval. Basis: questions 1 and 2.
- DEC-1133 (2026-11-11, items (1) (2) (5) standing): **set-up A's bar** as SETUP-A-BAR proposes (scope V2, unplaceable
  calls by C, the as-run call log a held-out stratum); **a fix to the guard's own faults is not a new rule** (by ACT as
  today; only a rule adding or removing a deliberate refusal goes through the bar); **the error path and the listing rule
  fixed first, each by ACT, set-up A after**; ACT A (`launch_now.sh` gates and registers each lead); the sample day after
  it with leads running, `--remeasure` writes the p95; FX6 one fix pass per round; **`mem_guard.py` runs (kills `rg` by
  pid past its thresholds, in restart class 4)**, `.wslconfig` unchanged, no window; the floor back to 3 GiB. Basis: questions 2 and 4.
- DEC-1134 (2026-11-11, until W2-155 closes): W1-19's and W2-13's warm real-model latency cases in `accepted_reds`, named
  (decision DEC-1134, fixed_by W2-155), by the owner's commit through the owner's operator; linger enabled. Basis: question 2.
- DEC-1135 (2026-11-11, standing): **DEC-1073 (4) governs waits and stops; a process-name match used only to detect,
  which can only refuse (a night) and never waits, signals or stops, is outside it** (as `rg` in DEC-1133 (5)); `nightly/quiet_check.py`
  read so (for the nightly, `quiet_check.py --beside-leads` leaves leads and their work out, DEC-1159 (1)). Basis: question 2.
- DEC-1136 (2026-11-11, item (2) standing): ACT-W1-01-EXEMPT-3 first, EXAMIN-SETS-1 and ACCEPTED-REDS-1 rebuilt after it;
  **every ACT whose commit changes a file under `tests/acceptance/` carries its own `acceptance_exemptions` entry in the same
  owner apply** (a second owner commit straight after the first, naming its full id; rehearsal and review cover both: confirmed by the owner). Basis: question 2.
- DEC-1137 (2026-11-11): W2-11's brief KPIs re-baselined to what W2-128 left (DEC-105 (c)); the five brief pointers stay;
  **a small ticket: the role templates carry Policy 2's four refusals, DEC-861's record rule and the stop after two refusals**
  (DEC-1116's template review), **landing before EXAMIN's copy (W2-27 depends on it)**. Basis: questions 1 and 4.
- DEC-1139 (2026-11-11): **W2-175's role templates approved at `4c0c73472fd8`, promoted as 1.0.1** (the seven
  `role-*.md` and six composed `template/.rulesync/subagents`); the copies by ACT (class (b)); three fixes ride the one-bar
  CIT-P (RV1 engineer wording, RV3 lead/CTO read tests and code), the composed files' stale "Wave 1" sections to W2-33. Basis: question 2.
- DEC-1140 (2026-11-11; (5) and (6) for the week to the reset of 11-15; (4) standing): **usage first**: RUBRIC-2 at every
  launch (C2/C1 workers Sonnet high; Opus for C3 and reviews), briefs checked before release, no-action notices logged not
  sent; **context awareness before compaction back for every session**; then ACT A, the idle guard's F1-F3, the brake's
  false trips (row 159), W2-115 (the dispatcher's own lead cap removed, DEC-1157 (8)); usage, spend and speed measured
  from 11-02, in the digests;
  **the CTO session to about 1M tokens, a fresh one each morning after the 09:30 digest** (corrected by DEC-1141: no session has a token cap; changes DEC-1118 for the
  CTO); **the 80 % brake lifted this week, EXAMIN's path first** (no lead cap, DEC-1157 (8)); **at 99 % push the owner
  at any hour, a report only** (an exception to DEC-1089 (3); the 97 % stop changed by DEC-1149 (3)). Basis: questions 2 and 4.
- DEC-1141 (2026-11-12; (3) and (6) standing): W2-11's K3 CIT-P approved at `dca382f3069f`; W2-176's approval withdrawn (its cap);
  **no token cap for any session** (CTO, leads, workers, helpers): full window and compaction, the hook writing the checkpoint and the
  read-first line (DEC-1118 (A) replaced entirely; DEC-1140 (4) corrected); hand merges of W2-175 and W2-176 tonight; **the operator
  agent asleep only during the nightly** (by ACT at 08:00; with the night hold gone, DEC-1157 (2): until its crontab ACT
  the operator does not launch from 02:10 to 08:00). Basis: questions 2 and 4. (6), with DEC-1104 (2)'s G9 and
  ACT-OPERATOR-HOURS-1/2: (the 09:00 sweep: recommended to supersede)
- DEC-1142 (2026-11-12, (8) (9) standing): W2-176's no-cap bytes approved at `3b6c5cb79d39` (ACT-CONTEXT-WATCH-1 (a), the
  matcher `Bash`); P-W2-23-8 (a); W2-115 PK-1 (a)+(c) (DEC-903's overlay list names the template's `close.yaml`); W2-148
  S15 option 2 (the home settings a fixed class (b)); ACT-OPERATOR-HOURS-1 (a), keep `0210`, and -2 (a); ACT-DISPATCH-1's
  6-hour reminder kept; the ticket table (W2-177 to W2-180 approved after the fact; W2-115b, W2-121c, W2-121d parked;
  W2-181 parked, then returned by DEC-1156 (6)); **standing: no new ticket and no split is filed without the owner's
  decision** (DEC-974); **standing: the two-refusal stop covers the same effect in another form** (a session refused
  twice for an action stops and says so; it never reaches the same effect by another command, form or file). Basis:
  questions 2 and 4.
- DEC-1143 (2026-11-12): EXAMIN-SETS-1's answers: the two fixed writer briefs approved (`EXAMIN-writer.md` `d37834e08c86…`,
  `PROVING-GROUND-writer.md` `57820503b569…`, `effort: high`); EXAMIN's copy is `~/gov-os-workbench/examin` at
  `0a82082495f5` (the original `~/EXAMIN APP` untouched); the launch clone with one scaffold commit; 20 questions; the
  release step kept; 10 per repository and 13 variants; the writer writes data only (the validator by an independent
  test designer under W2-93); `measures` by roles; no checker for W2-94. Basis: questions 2 and 4.
- DEC-1144 (2026-11-12): P1-A W2-11 merged by hand (`6f2234f40`, an exception to DEC-989); P1-B W2-157 reopened for the
  backstop hang (the `skip_known.json` entry causes no skip: the fix itself is the route); P1-C W2-146's lines read
  first (approved by DEC-1145); P1-D a narrow third check of the path-map chain (an exception to DEC-1010); **P1-E: K9's
  dispatcher is W2-121 a and b**, part c's slot line moved into W2-121b, c (less it) and d parked (W3-P33, W3-P34); P1-F
  the W2-81 runner's `--sets-root` inside W2-93; **P1-G: a reviewer's read-only probes allowed in the quiet hours**, in
  its own TMPDIR, touching neither the repository nor the evaluation sets (into the briefs). Basis: the owner's answers
  to P1-A to P1-G (no question named).
- DEC-1145 (2026-11-12): W2-146's kernel path-map schema approved (CAP-33) at `ebdbabd2e0d3` (`d22efa5a…`); a pattern
  that does not compile is refused at use (`gov retrieve`: `CONFIG_INVALID` naming `id_forms[<i>]`); the config check's
  gap is DECIDED-NOT-DONE row 174. Basis: the owner's approval (no question named).
- DEC-1146 (2026-11-12, standing): **a resource gate's refusal (memory, CPU, disk, a heavy slot) is a wait, not a
  refusal under the two-refusal rule**: the session relaunches when the gate opens, without asking the owner; the
  two-refusal rule covers permission refusals (the guard, the sandbox, a hook); in the common lead brief. Basis: P1-I.
- DEC-1147 (2026-11-12): W2-152's kernel facts schema approved after the fact at `09fc68645c0c` (`3141d5da…`, also within
  DEC-1116 (1)'s set); its CIT-P record written; the adoption's facts file, row 173's route and the kernel scan to the
  owner (answered by DEC-1148). Basis: P1-H.
- DEC-1148 (2026-11-12): five kernel files approved by their bytes (adopt `SKILL.md` `641a347b`, `pretooluse.py`
  `c2c8f0af`, `settings.json` `3aaa82e5`, `secrets-indexing.yaml` `8dae63e8`, `test-map.schema.json` `0e4105ef`); the
  secrets scan off on this repository only, on in EXAMIN's adoption; W2-174 gains the facts file (a1), W2-27 one line,
  W2-160 onto EXAMIN's path after W2-159; **the kernel gate in the CTO's tools** (`kernel_gate.py`, `kernel-approved.txt`,
  called by `land.py` before any enqueue and by `hand_merge_check.sh` before any merge; the product queue by ACT later);
  W2-45 widened for two revisions. Basis: the owner's approvals (no question named).
- DEC-1149 (2026-11-12, (3) standing): **the gate's working size 0.75 GiB (805,306,368 B) per live session** (ACT-P95-1,
  applied); the floor, the 5 GB hold, `mem_guard` and the OOM trip unchanged; **usage never stops a lead or a worker**
  (tracked and reported only; the 99 % push a report), **the runaway brake stays a stop** (it guards against looping);
  the two peaks re-measured from the ledger by 11-19. DEC-947 item 2, DEC-1138 (4), DEC-1140 (6), DEC-1115 (4) changed.
- DEC-1150 (2026-11-12): **W2-88 split** into W2-88a (the adopt skill's kernel text, with W2-174's S5) and W2-88b (the
  real-repository proofs, copies only); P1-K (a) W2-115's fallback dropped; P1-L (a) W2-124's 13 files revised, each case
  keeping its guard.
- DEC-1151 (2026-11-12): ACT-EXAMIN-WRITERS-INSTALL-1 applied (`ba27e4c0d`); W2-94 from the copy at `0a82082` (launch
  clone scaffold `48459935c435`), both walled writers delivered (20 and 60 questions, counts only to the CTO); **W2-27's
  green-base line:** before any scoped close in the copy, a full close at the adoption commit, every red fixed or listed
  in the copy's `accepted_reds` by an ACT the owner approves. Basis: the owner's yes (no question named).
- DEC-1152 (2026-11-12): EXAMIN's visible half released and final (the ten questions confirmed against `0a82082495f5`);
  the pin recorded in the run record, DEC-1143 (2), DEC-1151 (2) and W2-27's ticket, no ACT in the path map; P1-M (a) a
  narrow independent check of W2-115's fix only. Basis: the owner's answers (no question named).
- DEC-1153 (2026-11-12): W2-45 widened by `tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py` (one test-designer
  revision); W2-160 by `src/gov/session_watch/command.py`. Basis: the owner's answers (no question named).
- DEC-1154 (2026-11-12, standing): **a change the owner decided, added to a ticket after its review (a widening, a
  default, a fix riding a resume), gets a narrow independent check of that change only, launched by the CTO without
  asking; the ticket lands on that check's passing record** (not a design review, not a full round). Basis: the
  owner's rule (no question named).
- DEC-1155 (2026-11-12): P1-N (a) W2-172 widened by W2-171's F5 case for one revision, under a narrow check; a sweep of
  every acceptance test for the two ejection defects (a path case judging any branch; a hygiene check tripped by the
  queue's folder), `drafts/ejection-sweep-20261112.md`. Basis: the owner's answer (no question named).
- DEC-1156 (2026-11-12, (7) standing; (8) superseded by DEC-1157 (1)): ROUTE-1 (a); P-W2-120-1 (b) (the "no output
  class" half deferred); W2-33 option A (its Interface; `senior-engineer.md`, the three layers in Wave 2 by DEC-1087
  (13)); W2-113 PKG-1 (a), PKG-2 (b); P-W2-98-IF-1 (a); W2-157's and W2-159's F4 fixed now (W2-181 back from W3-P31);
  **standing: a test revision that only records a behaviour the owner already decided, and a path case that judges any
  branch instead of its own, are the CTO's** (a test designer writes it, the ticket widened by that file, a narrow check
  under DEC-1154, listed for the owner's reading); (9) the inventory (`drafts/lead-delay-inventory-measure.md`, decided
  by DEC-1157). Basis: the owner's answers (no question named).
- DEC-1157 (2026-11-12, standing): **every rule that holds or delays a lead is removed, except what protects the
  machine and the governance** (the list at the top, (14)): (1) every decision that stops or delays a lead to the owner
  at once, at any hour, as a full package; (2) no night hold: no lead start or landing held for the nightly
  (`night_hold.py` stopped; the operator's cron line still sleeps 02:10-08:00 until its crontab ACT, class (b)); (3) the
  CTO states each ticket's interface at claim, before its lead takes a slot (a lead returns an interface package only
  for a gap the statement leaves); (4) lands in batches of two or three tickets with disjoint paths; (5) no CPU band
  (`cpu_band` [0, 1000]); (6) two lines ready at all times (claim, worktree, brief); (7) no commit freeze during lands
  (the CTO commits and accepts the queue's re-test); (8) no lead cap (`max_leads` removed): memory admits each start, a
  ticket on EXAMIN's critical path never waits; (9) a dependency merged into `w2/integrate` is met for starting
  (`plan_override: DEC-1157` on the ticket; closing still waits for it to be closed; the product's plan check reading
  "merged" parked to Wave 3); (10) a land holds at most two of the three heavy slots; (11) the usage stop stays removed;
  (12) widenings and KPI edits within a ticket's own purpose are the CTO's, listed for the owner; new tickets and splits
  stay the owner's; (13) two logs: every refused start and every heavy-slot wait; (15) W2-113 PKG-3 (b), W2-155 started,
  W2-60a built (its merge after W2-33), W2-154's S4 in full; (16) the sweep (`drafts/dif-sweep-20261113.md`). Supersedes
  DEC-1138 and DEC-1156 (8); changes DEC-1140 (2), (5), DEC-1021, DEC-1018 (1), DEC-1052, DEC-1032, DEC-1038 (4),
  DEC-1039 (1b), DEC-1088 (5)(a), DEC-979, DEC-974. Basis: the inventory's measured lead-hours (no question named).
- DEC-1158 (2026-11-13, standing): **the emergency of 2026-11-02 and its freeze are lifted** (superseded and spent items
  in "Lifted"); kept: DEC-1033 (2) as DEC-1065's line, DEC-1047 (3) (DEC-1010), DEC-1050's T-1, Q-1, G-1, G-2 and O-7,
  DEC-1039 (1b)'s GPU budget and no-spill rule; follow-ons: this list refreshed, START-NEXT-SESSION rewritten (no
  "emergency mode"; the live pin `pin-797495bdfc70`), the prompt's §0 emergency bullet an edit for the owner's operator
  (`drafts/PROMPT-s0-dec1158.md`). Basis: the owner's word on the sweep (no question named).
- DEC-1159 (2026-11-13, (1) (3) standing): **the 04:00 nightly runs beside the leads**: `quiet_check.py --beside-leads`
  (used by `nightly_restart.sh` only) leaves out leads and their work (their jobs, pytest, heavy-slot holders,
  `rebuild_slot.sh`, launch scripts, rebuild locks, the load) and still waits for a landing, a close, the merge queue,
  an ACT, the operator's freeze, a memory measure, another nightly, the main tree, the rg storm and a stale dispatcher
  status; no `dispatch/OFF`; its memory cap (MemoryMax = available less the 3 GiB floor, no swap, OOM kill), latest-start
  refusal and committed-code check kept; nightly.sh takes the heavy slots and the rebuild lock itself; by an amendment of
  ACT-NIGHTLY-RESTART-1 (class (b)) after an independent check and its rehearsal (DEC-1132 (4) changed); W2-155 PKG-1
  option 1 (`MAX_REQUEST_CHARS` from 24,000 to about 48,000 after one GPU-window reading of the per-request peak; option
  5, the warm p95 a named red, the fallback; DEC-1067 (f) changed); **standing: no worker sends the live shared reranker
  requests above its limit outside a GPU window.** Basis: the owner's answers (no question named).
- DEC-1168 (2026-11-13, (1) standing): **a launched worker's sandbox allows exactly one network entry, `127.0.0.1:<port>` for the shared reranker's token-guarded TCP route (W2-186, built after EXAMIN's copy starts); never a bare host; `sandbox.faults` refuses any other** (changes DEC-158 and DEC-1114 S9). Basis: SANDBOX-1-B4 (a), B3's probe.
- DEC-1169 (2026-11-13, (2) standing): **in each status block, beside the ticket total, every ticket added since the last report is named with the owner's decision that approved it.** Basis: the owner's words.
- DEC-1170 (2026-11-13, standing): **the gitleaks scan stays off on this repository: a private, local development repository, nothing public**; not raised again; it stays built and tested in the product (changes DEC-1045 from a measure to a standing decision). Basis: the owner's words.
