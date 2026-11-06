# Decisions in force

The one list of what holds (DEC-1052 R-9), 2026-11-04. Where the prompt, a brief or RESUME HERE differs, it holds; a
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
  is wrong or keyword-only misjudges memory). *(The trial's (12)-(13) amended by DEC-1070.)*
- DEC-1070 (2026-11-04, standing for the measure): **three sets, three jobs**: the visible 40 tune and choose; the
  hidden 40 check (counts only, never choose; a visible-only gain is suspect); a **new measurement set** (fresh, blind,
  by the rubric, a new writer, outside every tree) is the verdict, measured only at decision points. Memory is reported
  as those three figures. **The choice rule:** hit@5, then MRR of the first gold source from the kept ranks. **Recall
  first:** no new method chosen until the recall diagnosis is in; fixes are generic, never aimed at named misses;
  the rerankers (mxbai, Qwen3-4B) and the embedder trial wait for the 0.6B's new record; M1-M5 also confirmed on the
  measurement set before window 4. **Labels** are audited on a schedule, all questions at once, never because one
  missed. Basis: question 1 and question 2 (selection pressure from named misses fits the tuning set).
- **Standing practice, the owner (2026-11-04):** whenever the CTO waits on the owner or the operator, it writes
  `log/cto-standby.txt` (what it waits for) and ends it when the wait ends, so the sentinel raises no false alarm;
  `tools/sentinel_check.sh` runs while `dispatch/sentinel-expected` exists (the sentinel's login, Remote Control,
  tmux session or watch log down: an inbox item, and the CTO pushes the owner at any hour); **bisect only in a
  throwaway `git clone` under `/tmp`, never `git bisect run` in a linked worktree of the main repository** (it exports
  `GIT_DIR`, and a test's `git init` re-initialised the main repository as bare on 2026-11-04 00:31); a process is
  stopped only by the pids a check named, never by a text match.
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
- DEC-1071 (2026-11-04, standing for the measure): **structural fixes only**, never per question, from one structural
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
- DEC-1073 (2026-11-04): the measurement set is used once, **after the structure is final** (D4B-STRUCTURE steps 2 and
  4-7 measured first), and only if the halves still agree within 3 points; otherwise to the owner. **Drift:** the
  register is the authority. The archive's 110 "spent" decisions go to a separate status-reconciliation list. A
  PROPOSED decision is not current, and retrieval must show its status. M5 is retested with the register links.
  **Link integrity** (clean-up, a cheap incremental checker, link templates in every recording role's skill and brief)
  comes to the owner as one package before anything is built. **Standing (L-0075):** every wait and every stop is by
  process id or process group, never a name match, through `.gov-runtime/scratch/orchestrator/tools/proc.sh` (`wait
  --max`, `stop --grace`, `pgid`).
- DEC-1074 (2026-11-05): **67.8 % is the 0.6B's honest figure** (v456 + the stated links, `memory-verdict`).
  - **The sets:** every used set (visible 40, hidden 40, the spent 60) is now tuning or diagnostic; only a fresh set
    gives a verdict. A **new verdict set of 80** is written blind by a new writer and cross-checked, then used only at
    the next decision point.
  - **The next lever:** the 60's 19 misses are classified by an independent role (kinds and counts) before the owner
    chooses it. Nothing is tuned or trialled until then.
  - **Consistency:** within 5 points, on sets of about 80.
  - **Approved for re-pin window 4,** tests first: v456 into W2-32, the stated links into W2-92.
  - **W2-54's premise** is rewritten by its test designer.
  - **LINK-INTEGRITY is adopted:** O1 (A), O2 (A); unlinked mentions are notices from the start.
- DEC-1075 (2026-11-05): ACT-MSET-3/4 approved: the verdict set of 80 (`memory-verdict-2`, declared in both path maps,
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
- DEC-1080 (2026-11-06, standing): the CTO reads with the Read and Grep tools, runs one simple command per call, no
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
- DEC-1083 (2026-11-06): D9-FATES approved (the auditor checks the 792 lines before any edit); K9's memory bar 85 %
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
