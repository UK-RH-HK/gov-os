---
milestone: "retro-2026-11 part 3 (what DEC-1047/DEC-1050 lifted: what stayed lifted, what crept back)"
commit: 4416b8403a386da14cd2a9f7a631846e4a8e2a1b
pack_sha256: "none (no gov context pack given; inputs = the repository at the commit, the CTO's scratch, the memory folder)"
---

task: retro-2026-11-P3
decisions: DEC-1047, DEC-1050, DEC-1052, DEC-1057, DEC-1082, DEC-1103, DEC-1110, DEC-1128, DEC-1133, DEC-1134, DEC-1136, DEC-1157, DEC-1158, DEC-1159, DEC-1164, DEC-1169, DEC-1180, DEC-1186, DEC-1201, DEC-1204

Written 2026-11-16 17:22 UTC by an independent auditor (read-only, fresh session). Requested path
`.gov-runtime/scratch/orchestrator/drafts/retro-2026-11/P3-lifts.md` was **refused by the guard** (rule 5: an auditor
writes only docs/probes|audit|assessment, `.gov-runtime/scratch/orchestrator/reviews/`, its own scratch or /tmp);
not retried; this file is in the auditor's scratch for the orchestrator to move.

## 0. Scope and method
- **What was lifted.** DEC-1047 lifted nothing itself: it stopped work, ordered the investigation and kept DEC-1010
  ("nothing is lifted before the owner decides"). The lifts are DEC-1050 (the twelve decide-first rows: 9 approved,
  3 refused: R-1..R-5, O-1/O-2/O-4, G-12) and DEC-1052 (the remaining rows of `packages/INVESTIGATION-1-COMBINED.md`).
  DEC-1049/DEC-1050 (5)/DEC-1051 were *stops* (no nightly, nothing scheduled), not lifts; their end (DEC-1158, the
  nightly back by DEC-1132 (4)) is not counted as creep.
- **Counted:** 57 approved rows whose disposition removes, scopes, moves or freezes a rule, gate, check, record or
  ceremony. 7 are product-default rows (Q-2, Q-12, Q-14, G-4, G-5, G-6, T-11's template half), not judged here (part 4/5's
  product reading). **50 judged.** Keep/fix rows (Q-13, O-9, O-12, G-9, K-3, K-4), clean-ups (O-8, O-13) and WBS rows
  (W-1, W-2, W-4..W-10) are not lifts. Refused lifts (R-1..R-5, O-1..O-4, G-12, M-1's ceiling: "W2-04 accepted as
  built") are not "crept back"; their growth is noted where it matters.
- **Golden rule (DEC-1204):** a return earns its place only if the incident behind it was hit in ordinary work and
  failed open or lost work.
- One guard refusal while reading: a `git show` with a loop-variable revision (rule 2's new unresolved-revision
  refusal, live since ACT-GUARD-FIX-6); the sizes were then read with literal hashes as the refusal text directs. One
  write refusal (above). Nothing under ~/gov-os-eval, ~/gov-os-operator, hidden or held-out paths was opened.

## 1. The lifted items and where they stand (50 judged)

| item | class | evidence |
|---|---|---|
| T-1 full `gov check` out of leads' verification | STAYED | .gov-runtime/scratch/orchestrator/tools/lead_verify.sh (no gov check) |
| T-2 gov check scoped | STAYED (no counter-evidence; not traced) | - |
| T-3 ceremony checks lifted | STAYED (not traced) | - |
| T-4 always-added lists to the nightly | STAYED (not traced; lists still present: record_reading 31, every_close 3) | governance/project/test-map.yaml |
| T-5 leads' serial phase = the product's only | STAYED (not traced) | - |
| T-6 real-model tests out of tickets' runs | STAYED (not traced) | - |
| T-7 helper reach | STAYED (not traced) | - |
| T-8 code-graph daemon scoped | STAYED (not traced) | - |
| T-9 shared_core scoped | STAYED (not traced; 24 entries remain) | governance/project/test-map.yaml |
| T-10 lifted suites to opt-in | PARTLY_BACK 11-09 | docs/DECISION_REGISTER.md (DEC-1103 (2), DEC-1104 (1)), governance/project/orchestration/packages/ACT-D4-RESTORE-1.md |
| T-11 CI off here | STAYED (not traced) | - |
| T-12 nightly preconditions (clean tree, head age) lifted | BACK 11-11 | governance/project/orchestration/nightly/quiet_check.py, docs/DECISION_REGISTER.md (DEC-1159 (1), DEC-1164 (5)) |
| T-13 gitleaks off | STAYED (reaffirmed DEC-1170, DEC-1182) | docs/DECISION_REGISTER.md |
| Q-1 attribution once each way | NOT_DONE in the close path (queue: done) | governance/project/orchestration/tools/merge_queue.py, .gov-runtime/scratch/orchestrator/tools/close_build.py |
| Q-3 rebuild/context packet at the close | STAYED for this repo's close (not traced in product) | - |
| Q-4 checkpoint freshness at the close | STAYED | .gov-runtime/scratch/orchestrator/tools/close_build.py |
| Q-5 gov check as pre-close gate | STAYED | .gov-runtime/scratch/orchestrator/tools/close_build.py |
| Q-6 network check | STAYED | .gov-runtime/scratch/orchestrator/tools/close_build.py |
| Q-7 escalation counter | STAYED | .gov-runtime/scratch/orchestrator/tools/close_build.py |
| Q-8 trailers as refusals | PARTLY_BACK 11-09 | governance/project/operator/landing_check.py |
| Q-9 containment (history re-judged by paths) | PARTLY_BACK 11-09 | governance/project/operator/landing_check.py, governance/project/operator/class-rules.yaml |
| Q-10 ratchet lists frozen, no owner commits | PARTLY_BACK 11-10/11-11 | docs/DECISION_REGISTER.md (DEC-1123, DEC-1134, DEC-1136), governance/project/orchestration/packages/ACT-ACCEPTED-REDS-1.md |
| Q-11 probe gate = READY only, form lifted | PARTLY_BACK 11-15/16 | memory probe-record-one-verdict-block.md |
| G-1 rule 1 stops guessing at shell | STAYED for writes; PARTLY_BACK for reads 11-15 | .claude/hooks/pretooluse.py, .claude/hooks/bash_writes.py, governance/project/orchestration/packages/ACT-GUARD-FIX-6.md |
| G-2 rule 5 stops guessing | STAYED | .claude/hooks/pretooluse.py |
| G-3 hidden half outside the trees, "no guard rule needed" | BACK 11-06/11-08 (earned) | docs/DECISION_REGISTER.md (DEC-1082 (3)), .claude/hooks/pretooluse.py (rule 2b) |
| G-7 W2-42a's parser re-scoped, not ported | BACK 11-15 | governance/project/orchestration/packages/ACT-GUARD-FIX-6.md, docs/DECISION_REGISTER.md (DEC-1174, DEC-1186) |
| G-8 hook imports frozen | PARTLY_BACK 11-15 | docs/DECISION_REGISTER.md (DEC-1186 (2), DEC-1187) |
| G-10 guard harvest | STAYED | .gov-runtime/scratch/orchestrator/dispatch/config.json (guard_harvest_s 1e9) |
| G-11 per-refusal ceremony | STAYED (call log holds hashes and counts only) | .claude/hooks/pretooluse.py |
| G-13 SubagentStop scoped by agent type | NOT_DONE | template/governance/kernel/hooks/subagentstop.py |
| M-2 SessionStart without a model | NOT_DONE (docstring still injects gov context --brief) | template/governance/kernel/hooks/sessionstart.py |
| M-3 cold rebuilds | STAYED (DEC-1184 changes-only refresh) | docs/DECISION_REGISTER.md |
| M-4 what memory embeds | STAYED (not traced) | - |
| M-5 register split | NOT_DONE (1.71 MB on 11-03, 1.88 MB 11-10, 2.14 MB 11-16) | docs/DECISION_REGISTER.md |
| R-6 committed gov checkpoint per round | PARTLY_BACK 11-11..11-12, then stopped | docs/checkpoints/ (7 records: W2-05, W2-52, W2-110, W2-152) |
| R-7 Stop hook auto-checkpoint unregistered | NOT_DONE | .claude/settings.json (Stop -> kernel hooks/stop.py), governance/project/orchestration/packages/LIFT-1/P1-PLAN.md |
| R-8 delegated decisions out of the register | STAYED (no delegated entries since 11-04) | docs/DECISION_REGISTER.md |
| R-9 one list of standing rules | PARTLY_BACK 11-09 onward | docs/DECISION_REGISTER.md (DEC-1110 (1)), .gov-runtime/scratch/orchestrator/CHECKPOINT.md, memory MEMORY.md |
| R-10 record commits batched | STAYED (4-24 decision-record commits a day) | git log --grep 'Task: decision-record' |
| R-11 pings only for what gates work | STAYED (DEC-1157 (1) is within it) | docs/DECISION_REGISTER.md |
| R-12 Implements optional, two-commit rule lifted | STAYED | - |
| R-13 status block from status.txt, not hand state | PARTLY_BACK 11-13..11-16 (owner's requests) | .gov-runtime/scratch/orchestrator/tools/status_block.py, docs/DECISION_REGISTER.md (DEC-1169 (2), DEC-1181, DEC-1201) |
| O-5 one stall net | BACK (never fully lifted, then grew) 11-04..11-16 | .claude/settings.local.json, governance/project/orchestration/packages/ACT-DEADMAN-STANDBY-1.md, ACT-DEADMAN-WAKE-1.md, ACT-STOP-IDLE-1.md, ACT-IDLE-GUARD-1.md |
| O-6 ACTs only for machine changes; freeze only an ACT's paths | PARTLY_BACK 11-09 onward | governance/project/operator/class-rules.yaml, .gov-runtime/scratch/orchestrator/acts/ |
| O-7 rm free but the catastrophic | STAYED (widened by DEC-1205) | .claude/hooks/pretooluse.py |
| O-10 load-average gate | STAYED (quiet_check's load test is skipped beside leads) | governance/project/orchestration/nightly/quiet_check.py |
| O-11 ratchets scoped (DEC-1012, DEC-1003) | PARTLY_BACK 11-09, 11-14 | docs/DECISION_REGISTER.md (DEC-1110 basis, DEC-1204 (5)-(6)), memory lesson-to-memory-at-once.md |
| K-1 Contract re-baselined to the lifts | NOT_DONE (only CAP-45 moved, v4.3) | docs/contract/ |
| W-3 process boilerplate out of KPI lines | STAYED (not traced) | - |

Classes used: STAYED, PARTLY_BACK, BACK, NOT_DONE (approved, never carried out); the audit skill's six classes
map as BACK/PARTLY_BACK = CONTRADICTS/WEAKENED of DEC-1050/1052, NOT_DONE = MISSING.

## 2. What crept back: findings (each: what happened, why, golden rule, what would reverse it)

**F1. T-12 BACK (11-11).** The investigation lifted the nightly's clean-tree and head-age checks (it runs on a fresh
clone). The nightly's restart (ACT-NIGHTLY-RESTART-1, DEC-1132 (4)) carried them back in `quiet_check.py`
("nightly.sh's own rule"); DEC-1159 (1) kept them beside the leads; DEC-1164 (5) then had to add a new hold: no CTO
commit on w2/integrate from 03:55 until the nightly starts, or the night refuses and a MISSED P1 follows.
Why: carried over with old code (ceremony accreting); no incident cited.
Ordinary work: yes, because any honest commit near 04:00 trips it. Consequence: other (a missed nightly, a new hold).
Reversal: an incident where the nightly's fresh clone was corrupted by a dirty main tree or a young head.

**F2. G-3 BACK (11-06, live 11-08), earned.** G-3 said moving the hidden half outside the trees made a guard rule
unnecessary. DEC-1082 (3) brought rule 2b back (ACT-GUARD-SETS-1, widened by ACT-SETS-GLOBS-1), with Bash-line word
rules (a line naming the sets root plus a variable, glob or cd).
Why: the health check showed measured roles could still read the hidden sets once outside the repository.
Ordinary work: yes, because a session searching the home folder reaches them. Consequence: fails open (a tainted
memory measure, the aim's core). This return passes the golden rule.
Reversal: evidence that no measured role can reach the sets root by an ordinary search (OS-level separation).

**F3. G-7/G-1(reads)/G-8 BACK (11-15).** G-7 re-scoped W2-42a (do not port the 1,431-line parser) once G-1/G-2 were
applied. ACT-GUARD-FIX-6 brought the live hook to W2-42a's parser (option (B), "stricter-only", a CTO choice):
`bash_writes.py` 1,551 to 2,783 lines; its own replay shows 166 stricter judgements of 15,891 real calls in 48 h, 132
of them `git show/diff <rev>:<path>` whose revision does not resolve. This audit hit one. DEC-1128 (2)'s 100 % bar
("no new guard rule goes live without set-up A's 100 %") did not apply, because DEC-1133 (1) reads it as "a fix to the
guard's own faults is not a new rule". The unresolved-revision refusal is a new deliberate refusal. G-8: the hook's
fixed ~50 ms of imports grew; W2-111 was reopened (DEC-1187). Rules 1 and 5 still let unresolvable writes through.
Why: a review finding (GUARD-HEREDOC, 11-13), not a live incident.
Ordinary work: no for the heredoc hole (found by review); yes for the new refusals (honest calls refused).
Consequence: other (honest work refused, contrary to DEC-1050 (6) "must not refuse honest work again and again").
Reversal: set-up A's 100 % evidence attached to ACT-GUARD-FIX-6, or an owner line waiving the bar for it.

**F4. O-5 BACK (never fully lifted, then grew).** O-5 kept one net (the dispatcher's stale line and the sentinel push)
and lifted the Stop-hook waiter check, `cto-standby.txt`, heartbeat rituals and the scratch deadman. DEC-1057 (7)
kept `cto-standby.txt`; `stop_waiter_check.py` is still registered. Then: sentinel_check.sh and the push at any hour
(11-04), the idle-check Stop hook (ACT-STOP-IDLE-1, 11-09), ACT-DEADMAN-STANDBY-1 and -WAKE-1 (11-10), ACT-IDLE-GUARD-1/2
(11-11/12), helper_watch.py (11-10), waiter_guard.sh (11-15), the sentinel's inbox rule (DEC-1191), and the dead-man as a
Wave 3 product layer (DEC-1195). The CHECKPOINT "Standing" line opens with re-arming two waiters.
Why: real incidents (11-04, the sentinel's login expired silently; 11-10, three dead-man pushes never received; 11-15,
two lead returns unread about 50 min).
Ordinary work: yes, because the incidents happened in ordinary work. Consequence: other (delay; no work lost, nothing
fails open). By the golden rule these do not earn blocking status; the idle-check hook blocks the CTO's turn end.
Reversal: an incident where a stalled CTO lost work or let a fail-open through.

**F5. Q-10 PARTLY_BACK (11-10/11-11).** Q-10 froze `accepted_reds`/`acceptance_exemptions` ("no new entries") and
lifted owner-only commits to them. Since then: W1-01 exemptions by owner commit (ACT-W1-01-EXEMPT-2/-3, DEC-1123), two
`accepted_reds` entries by owner commit (DEC-1134), and a standing rule that every ACT changing `tests/acceptance/`
carries its own exemption in two owner commits (DEC-1136 (2)).
Why: real incidents: W1-01 (G-1's own backstop) went red for every merge after an operator's ACT; two named nightly reds.
Ordinary work: yes. Consequence: other (landings blocked, failing closed). It does not pass the golden rule as a
ratchet; it is a side cost of G-1's backstop failing closed on the owner's own commits.
Reversal: a case where an unlisted exemption let a non-designer's acceptance-test change land.

**F6. Q-8/Q-9 PARTLY_BACK (11-09).** The operator agent's landing check re-judges first-parent history against
`class-rules.yaml`'s control paths and trailer conditions (Task other than DAEO-sdxk, Role, Act, Act-sha). Each hit is
an inbox P1. Two P1s came from trailer slips with no substance (6cc09c7ea on 11-10; 72c6def88 on 11-13, a blank line
hiding trailers). Two memory practices followed (merge-task-trailer, trailers-one-block).
Why: by design of OPERATOR-AGENT-1 (DEC-1104), to protect control paths (kernel, guard, settings).
Ordinary work: yes (slips). Consequence: other (P1 noise); it would catch a governance fail-open (kernel bytes
without approval), which the kernel gate (DEC-1148) also covers.
Reversal: a P1 from it that stopped a real unapproved control-path change.

**F7. O-6 PARTLY_BACK (11-09 onward).** O-6 held ACTs to installs, services and crontab, with no ACTs for records,
and froze only an ACT's paths. Since 11-04 there have been **86 ACTs** (40 in 11-04..11-10, 46 in 11-11..11-16).
Twelve are generated-copy ACTs (ACT-CLAUDE-COPIES-1..12). Record and text ACTs include ACCEPTED-REDS-1, W1-01-EXEMPT-2/3,
GOLDEN-RULE-1 and CLAUDE-RULES-1. `class-rules.yaml` (11-09) makes `.claude/**`, the kernel template and CLAUDE.md
control paths, which go by ACT. Freezes came back too: G9 held every ACT while act-in-progress existed (incident 11-11;
narrowed DEC-1164 (14)), commit freezes during lands (removed DEC-1157 (7)), the release hold on every commit (11-15),
the 03:55 freeze (F1), and `pgrep land.py` before every commit (11-16).
Why: the operator agent's design and CAP-33's owner approval of kernel bytes. Some freezes followed real incidents
(release C moved, 11-15; a commit during a land, 11-16).
Ordinary work: yes. Consequence: other (re-runs and waits; no fail-open cited).
Reversal: evidence that a generated-copy change without an ACT reached a session wrongly.

**F8. O-11/R-9 PARTLY_BACK (11-09, 11-14).** O-11 scoped DEC-1012 ("a rule broken twice becomes a mechanism") to rules
that pass DEC-1010's test. R-9 asked for one list. Instead: DEC-1110 put standing rules at the top of the prompt *and*
in START-NEXT-SESSION §2 ("a rule … is enforced by a check, not by memory"); "lessons to memory at once" (owner, 11-14);
the memory index holds **102 standing practices**, about 80 dated 11-13..11-16. Many are how to avoid tripping Gov OS's
own machinery: verdict-block form, trailer paragraph, act-in-progress, control paths, guard false-positive forms, the
release hold. Rules now live in five places (prompt, START-NEXT-SESSION, DECISIONS-IN-FORCE, CHECKPOINT "Standing",
memory). DEC-1204 put a kernel skill into the product the same day (basis question 5), though it merges rules long in use.
Why: real incidents (compactions erasing rules; the 11-14 trial's repeats).
Ordinary work: yes. Consequence: other.
Reversal: a weekly measure showing fewer repeats and refusals since the memory practices, with no extra checks.

**F9. R-13 PARTLY_BACK (11-13..11-16), owner's requests.** The status block still reads the hand-kept
`report-state.json` (R-13 asked for `dispatch/status.txt` plus open owner items). It gained new tickets (DEC-1169 (2)),
reopens (DEC-1181) and "every report ends with it" (DEC-1201).
Why: the owner reads each report standalone. This is the owner's own choice, not ceremony from the CTO.
Ordinary work: n/a (not a guard). Consequence: other. Reversal: none needed; it is the owner's choice.

**F10. Minor returns.** T-10 (11-09): ten capped or lifted guard cases back into the gates (ACT-D4-RESTORE-1; three of
them red by design). R-6 (11-11..11-12): seven committed `gov checkpoint` records by four leads, then none, a drift of
old habit. Q-11 (11-15/16): the probe record's form is enforced again: a quoted verdict copy fails land.py closed, and
a missing frontmatter reddens W1-08/W1-26.
Ordinary work: yes. Consequence: other.
Reversal: a probe or checkpoint form check that caught real lost work.

**F11. The anti-creep mechanisms themselves eroded.** DEC-1052's standing basis had three triggers:
(1) every new rule states which basis question it passes. That held in 54 of 59 decisions in 11-04..11-10 and in
**19 of 82** in 11-11..11-16. (3) the weekly basis review (D-11) was never built (DECIDED-NOT-DONE row "Not started";
DEC-1164 (2) counts the 11-13 sweep as its first run). DEC-1128 (2)'s 100 % bar was read narrowly (F3). What worked was
the owner's measured sweep: DEC-1157 (45.2 lead-hours lost in one day) and DEC-1164 removed or amended 38 of 43 holds.
Ordinary work: yes. Consequence: other (creep goes unflagged).
Reversal: a basis line per new rule and a weekly review record found elsewhere.

**Approved, never done (not creep, but open):** Q-1 in `close_build.py`, which still traces each red 3 (6) rounds
against a nightly-baseline clone; G-13 (SubagentStop still blocks every subagent's return); M-2; R-7 (the Stop hook's
auto-checkpoint still registered); M-5 (the register +430 KB since 11-03); K-1.

## 3. New rules, gates, checks, records and practices since 11-04 (not a return)

Week 1, 11-04..11-10 (15; one is a lift):
11-04 waits and stops by pid only (DEC-1073 (4); trigger: a name-match stop); 11-05 gpu_backstop (DEC-1067; GPU crash);
11-06 the CTO's command rule in every brief (DEC-1080; owner prompts); 11-06 dependency enforcement at launch, closed
tickets never edited (DEC-1088; traffic, in aim); 11-07 runaway brake (DEC-1091); 11-09 the operator agent's G1-G9 and
its commit freeze (DEC-1104); 11-09 guard call log (DEC-1106 (2)); 11-09 guard rule 2c (indep walls); 11-09 guard rule
2d (operator folder, call log); 11-09 scoped selection after out-of-ticket landings (DEC-1100); 11-09 periodic memory
audit (DEC-1101; in aim); 11-09 "unblocked work keeps moving" (DEC-1109 (3), a lift); 11-10 spend log and RUBRIC-2
launch rule (DEC-1118-1120); 11-10 templates with READY/DONE by code (DEC-1116, from DEC-1052); 11-10 helper watch.

Week 2, 11-11..11-16 (21; three are lifts, one was removed within a day):
11-11 set-up A's 100 % bar (DEC-1128 (2)); 11-11 one bar, two rounds for every role, plus the round ledger (DEC-1131);
11-11 lead cap 5 and night hold (DEC-1138; removed 11-12); 11-11 mem_guard/mem_hold/oom_watch/lead ledgers; 11-12 "a gate
refusal is a wait" (DEC-1146, a lift); 11-12 kernel gate and hand-merge check (DEC-1148; trigger DEC-1147, kernel bytes
merged before approval: ordinary work yes, fails open, earned); 11-12 narrow check after a decided change (DEC-1154);
11-12 context-watch hook for every session (ACT-CONTEXT-WATCH-1); 11-12 every pytest through heavy_slot (incident T1
0556); 11-12 two logs, refused starts and slot waits (DEC-1157 (13)); 11-13 supplementary context cap (DEC-1165);
11-14 standing hidden set at 95 % plus a monthly fresh set (DEC-1179); 11-14 no deferral (DEC-1180 (4), a lift); 11-14
launch effort floor and criticality promotion (W2-184; Sonnet named on Opus tickets three times); 11-14 EXAMIN weekly
gitleaks (DEC-1182/1184); 11-15 rehearse every handed command (P-SESSIONS-1 item 3; failed handed commands); 11-16 the
operator job runner and its rulebook (DEC-1191); 11-16 no rehearsal against a live path (DEC-1196 (5); an install hit
the live operator folder 01:09: ordinary work yes, loses work, earned); 11-16 the golden rule skill, pasted into every
judging brief (DEC-1204); 11-16 a fresh 80 for every memory measure (DEC-1207); 11-16 full permission inside the box
(DEC-1205, a lift).

Volume beside them: decisions 59 (11-04..11-10) to 82 (11-11..11-16); ACTs 40 to 46; commits 977 to 1,682; CTO scratch
tools created about 46 to 58 (with backups); memory practices about 4 to about 98.

## 4. Counts
- Lifted rows: 57 (50 judged here, 7 product defaults left to other parts).
- Stayed lifted: 28 (16 traced, 12 with no counter-evidence, not traced in depth).
- Crept back: 16 (BACK 4: T-12, G-3, G-7, O-5; PARTLY_BACK 12: T-10, Q-8, Q-9, Q-10, Q-11, G-1 reads, G-8, R-6,
  R-9, R-13, O-6, O-11).
- Approved but never done: 6 (Q-1 close path, G-13, M-2, R-7, M-5, K-1).
- Returns earning their place by the golden rule: 1 (G-3). The other 15 rest on incidents of kind "other" (delay,
  noise, fail-closed) or on none.
- New items: week 1, 15 (1 lift); week 2, 21 (3 lifts; 1 removed within a day). About 2.1 a day in week 1 and 3.5 a
  day in week 2. Earned under the golden rule: 2 (kernel gate, no live rehearsal); in the aim (memory, traffic): 5.

## 5. Probed and found sound
T-1 (no gov check in lead_verify); G-2 and rules 1/5 still let unresolvable writes through; the harvest still off
(G-10); rm free but the catastrophic (O-7); R-8 (no delegated register entries); the merge queue applies Q-1;
close_build has no checkpoint, escalation, network or gov-check gate (Q-4..Q-7); gitleaks stays off (T-13); the
owner's DEC-1157/1164 sweep removed the 11-11 holds within a day.

```verdict
{"kpis": [{"kpi": "P3-a lifts stayed lifted", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F9", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F10", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F11", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
Classification: 11 findings. One (F2) is ordinary work that fails open, and it is a return that earned its place, not
a defect. None loses work. All others are "other": recorded rows for the owner's lift-or-keep list, not rounds.
