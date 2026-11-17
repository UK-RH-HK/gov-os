---
milestone: "Owner's retrospective 2026-10-16 to 2026-11-16: combined short list (parts P1 to P5)"
commit: 78f641d47f939d1ea6139593440dfb4077e54011
pack_sha256: "none: no context pack; inputs are the five parts, perticket.csv, the repository at the commit, and the parts' own evidence folders"
task: retro-2026-11-combine
decisions: [DEC-1047, DEC-1158, DEC-1204, DEC-1010, DEC-1050, DEC-1052, DEC-1131, DEC-1157, DEC-1205, DEC-974]
author: independent combining auditor (fresh, read-only; wrote none of the parts)
---

# Retrospective 2026-11: the short list

The yardstick is DEC-1047's aim paragraph, which still stands. DEC-1158 (1) superseded only DEC-1047's items (1) and (2), the stop and the investigation (DEC-1073: both ids named). The judging rule is DEC-1204. Nothing here is lifted; every row is for the owner to decide.

**One guard refusal while auditing.** A `git show` of a scratch path at a commit was refused by the unresolved-revision rule, because the path is not tracked. I did not retry it. It is a live example of P4 S13 and P3 F3: an honest call refused.

## 1. The parts checked against each other

**Where two parts differ, which figure holds**

| subject | the parts say | which holds, and why |
|---|---|---|
| CTO's share of spend | P1: 54 % (main tree plus subagents); P2: ~46 %; P5: $3,450 (11-02 to 11-16) | Both hold. P1's denominator is every session; P2's is the CTO plus ticket roles. Read it as "about half". |
| ticket leads | P2: 404 runs, $1,927; P4: 587 runs, $2,686 | Per ticket, P2 holds: it counts tickets closed in the window, and P1's 15 % × $12,753 ≈ $1,913 agrees. P4 counts every return log, including open tickets and adopters. |
| test designers | P1: 13 % (≈$1,660 notional); P2: $928; P4: ~$1.0k; P5: $880 | P2, P4 and P5 hold: they come from run logs. P1's per-message classification over-counts. All four agree that test designers cost more than engineers. |
| review catches | P2: 32 % of FULL reviewer runs had a blocking label; P4: 5 % of 502 findings were blocking | No conflict: P2 counts runs and P4 counts findings. P2 uses labels before moderation, P4 the committed records. Use them as the upper and lower bounds. |
| landing ejections | P2: 11 red + 1 conflict; P4: 12 ejected, "9 red" | P2 holds. `land-done.txt` shows 9 red, plus 2 marked "red: no single ticket explains", plus 1 conflict. |
| ACTs | P2: 95 ids; P3: 86 since 11-04; P4: 61 bundles (11-10 to 11-16); P1: 40 applied | These are different measures, not a conflict. My count: 109 distinct ACT ids named in commits since 10-16, 80 since 11-04. P1's "GUARD-FIX 1 to 7" is stale: fixes 1 to 9 exist, so P4 holds. CLAUDE-COPIES 1 to 12: all parts agree. |
| decision-record commits | P1: 160 in the window, W1 = 0; P4: 127 in 8 days | P4 holds (I count 138 trailers from 11-09). P1 does not hold: the window has 461 `Task: decision-record` trailers, 60 of them in W1. |
| register entries per week | P1: W1 106, W2 29, W4 183 | P1's total of 497 holds (new ids DEC-715 to DEC-1209). Its weekly split does not: by next-free-id rows, W1 has ~185, W2 ~49 and W4 ~79. P3's 59 and 82 hold. |
| memory index | P3: 102; P4: "about 95" | P3 holds; MEMORY.md has 104 entries now. |
| "review rounds" | P2's table | The CSV column counts reviewer runs, not rounds. Read it as runs. |

**Spot checks: 3 or more figures per part**

- **P1.** These hold:
  - commits: P1 says 5,167; I count 5,184 at its commit.
  - register words: P1 says 328,000; I count 327,808.
  - plan limit: 100 % (reset 11-08) and 97 % peak (reset 11-15), confirmed in `log/usage.txt`.
  - commits with `Role: owner`: P1 says 90; I count 93.

  This does not hold: decision-record commits (see above). P1's token table uses a separate method and was not re-run.
- **P2.** These hold exactly:
  - 141 tickets: 19 LITE, 72 STANDARD, 50 FULL; 48 closed at the lift.
  - median claim to merge: 0.25, 0.58 and 0.87 days.
  - median lead plus workers: $6.71, $18.88 and $51.19.
  - PACKAGES: 8 of 23, 75 of 172, 95 of 206.
  - lands: 71 closed, 25 with no outcome.

  Lead-only medians differ slightly: 4.06, 11.71 and 17.53 from the CSV over tickets that had lead runs. exa-g6db's timeline is not verified: its commits are not in `/home/usain/EXAMIN APP`.
- **P3.** These hold:
  - `bash_writes.py`: 2,783 lines.
  - register: 2.14 MB (2,143,651 bytes).
  - decisions: 59 (11-04 to 11-10) and 82 (11-11 to 11-16), by id.
- **P4.** These hold:
  - `pretooluse.py`: 1,830 lines.
  - `guard-refusals.jsonl`: 270 refusals, 217 false positives and 53 true.
  - probe records: 192 records over 88 tickets.
  - CHECKPOINT: 337 KB, 28 RESUME HERE blocks.

  `kernel-approved.txt` has grown since (213 lines now).
- **P5.** These hold:
  - `brief.md` line 33 says "No `gov retrieve` in the sandbox".
  - `role-reviewer.md` has 0 memory lines.
  - leads' `gov context` calls: 373 (339 + 34, in `agg.json`).

  Ceiling mentions: P5 says 84; its own `gaps.json` says 80.

## 2. THE SHORT LIST (ranked by what most breaks the cycle)

| # | what | evidence (figure, part, path) | what it protects or costs | golden-rule lines |
|---|---|---|---|---|
| 1 | **BUILD (finish): take the owner out of the relay.** Give the operator full permission (DEC-1205 (5)) and finish the job runner; the CTO stops handing the owner jobs to run. | 134 of 544 owner messages relay jobs or ACTs and 33 are yes lines (P1 §2); 54 relays in W5's 4 days; exa-g6db lost 26 + 26 min to relays (P2 §4). `drafts/retro-2026-11/P1-usage.md`, `P2-lifecycle.md` | Costs the owner ~5 messages a day and hours of latency. The operator's program gates (G1 to G7) stay. | Ordinary work: yes, because every control-path change goes through it. Consequence: fails open only if the G1 to G7 gates go, so keep them. |
| 2 | **SIMPLIFY: PACKAGES.** Split them into "the owner decides" (P1, DEC-974) and "the lead decides under a standing rule". Lift the second kind, with a one-line register entry (P4 R7, R1). | 180 of 404 lead runs end in PACKAGES (45 %) (P2 §3); 140 owner messages answer packages (P1); each resume costs $3 to $5 (P2) | Costs a lead stop, a resume and a CTO read each time. It protects only where the owner's decision is needed. | Ordinary work: yes. Consequence: other. |
| 3 | **BUILD: the product close.** Compare against the base by default and apply accepted_reds under `close: scoped` (F-028, F-030, F-031). | exa-g6db: green at 44 min, then 1 h 50 min of close with no close at 2 h 30 min; 111 to 133 harness or base reds counted as the change's (P2 §4) | It blocks honest product work on every adopted repository. The close fails closed, so it opens nothing. | Ordinary work: yes, because every adopted repository has reds at its base. Consequence: other. |
| 4 | **BUILD: a creep stop.** No new rule, gate, check or practice without a basis line that names an ordinary-work incident which failed open or lost work. Check it by code at the decision-record commit, and run the weekly basis review (D-11, never built). | Rules with a basis line: 54 of 59, then 19 of 82 (P3 F11); new items went from 2.1 to 3.5 a day, and 2 of 36 earned their place; 15 of 16 returns do not pass the golden rule (P3 §4) | Costs nothing. It is the root of the cycle. | n/a (no protection at stake) |
| 5 | **BUILD (today): keep the transcripts.** Raise `cleanupPeriodDays` or archive the transcripts. | 10-16 and 10-17 are already gone (~1 B tokens, $92 of lead runs) (P1 F4); every measure in §4 reads these files | One setting. | Ordinary work: yes, because the default cleanup runs on its own. Consequence: loses work (the evidence). |
| 6 | **KEEP the walls, STOP building the guard.** After GF-8, GF-9 and the box: carry the static walls as OS mounts (P4 S19); scope the run-time listing refusal (S12) and the unresolved-revision refusal (S13); no further GUARD-FIX without set-up A's 100 % (DEC-1128 (2)). | Security took 19 % of spend and 105 owner messages (P1 F3); the running cost is small (0.36 % of 82,995 real calls refused; 217 of 270 harvested refusals were false positives) (P4); the parser grew from 1,551 to 2,783 lines past the bar (P3 F3) | The building cost is the cost. Keep rules 1, 2, 2b, 3, 5, g14 and catastrophic rm. | Walls: Ordinary work: yes, because broad greps and engineers fixing their own tests are everyday. Consequence: fails open (rm: loses work). S12 and S13 refusals: Ordinary work: yes. Consequence: other (honest work refused). |
| 7 | **SCOPE: reopens and closes.** Close at the land, with no batch close at a lift. Reopen only for a defect; a new KPI line becomes a new ticket. | 48 of 141 closes waited for the lift (median 4 to 7 days); 29 reopen events, most of them added scope; W2-88 had 14 reviewer runs and 4 reopens (P2 §3, `perticket.csv`) | Reopens re-trigger rounds, which is how runs pass the two-round cap. | Ordinary work: yes. Consequence: other. |
| 8 | **SCOPE: review.** Keep the FULL probe on guard, gate and launch work. Drop review for STANDARD work off those surfaces. Ask for blocking findings first, with at most five rows (P4 Q17). | FULL: 20 of 41 tickets had a blocking label (P2); only 25 of 502 findings were blocking (P4); STANDARD: no spot-checked lost work (P2) | Reviews cost ~$780 a month (9 %). | FULL guard work: Ordinary work: yes, because heredocs and `xargs grep` are everyday inputs. Consequence: fails open, so keep. STANDARD off those surfaces: Ordinary work: yes. Consequence: other. |
| 9 | **SIMPLIFY: generated `.claude/` copies go to class (a), checked by code against an approved kernel commit (P4 Q8).** | 12 CLAUDE-COPIES ACTs, 20 % of bundles, each with a review, a rehearsal and an owner's yes (P2, P3 F7, P4) | The source has already passed the kernel gate (Q12). | Ordinary work: no, because the bytes are the generator's output. Consequence: other. |
| 10 | **SCOPE: `lead_verify`.** The import-graph selection on the branch; the full suite once, at the landing and in the nightly. | 22.5 min median per run, several runs per ticket; ~4 change-caused reds in ~444 result lines (P2 §3) | The landing (Q13) and the landing select (13 reds caught, P4 Q10) stay. | Ordinary work: yes. Consequence: other, because the landing catches the same red one step later. |
| 11 | **SIMPLIFY: one CTO watcher, and notices as a daily digest.** Merge the watcher layers (C9) and the idle pressure (C2). Structural notices (Q15) and the guard harvest (R12) become one daily line. | 1,219 inbox items: 151 harvests, 114 idle-headroom, 85 helper-watch, 73 structural (P4); O-5 grew back to more than 8 mechanisms (P3 F4) | A re-arm in every response, and reading noise. | Ordinary work: yes. Consequence: other (delay only). |
| 12 | **BUILD: memory that works.** Size `gov context` to the ticket. Give the sandboxed embedder access so workers can use memory. Log every memory call (P5 F1, F3, F6). | 143 of 373 lead context calls refused; 18 briefs built by hand (~448 min); 10 of 16 worker retrieves degraded (P5 tables B and C) | The aim's core (memory). | Ordinary work: yes. Consequence: other. |
| 13 | **SIMPLIFY: turn workarounds into tool defaults, then prune memory.** The launcher picks model and effort (Q20); writers for trailers and probe records (R8, R9); SubagentStop enforces 4 fields, not 12 (Q25, G-13 never done). | MEMORY.md has 104 entries, at least 25 of them workarounds (P4 H1, P3 F8); 2 trailer-form P1s (P3 F6) | Words loaded into every session and traps repeated. The probe-record form keeps READY fail-closed (R8: keep). | Probe form: Ordinary work: yes. Consequence: fails open if READY were miscomputed, so keep the check and tool it. The rest: other. |
| 14 | **LIFT: freezes and records that crept back.** The nightly's clean-tree and head-age checks (T-12) and the 03:55 freeze; `pgrep land.py` before every commit (C6); hand-written version rows and next-free-id lines (R2); `.pre-*` tool copies (R14); the scratch_measure step (Q24a). Generate DECISIONS-IN-FORCE (R4). Split the register (M-5, never done). | T-12 came back with no incident cited (P3 F1); 589 version rows (P4); the register grew from 1.71 to 2.14 MB (P3) | Before lifting R2, check whether any tool reads the rows. | Ordinary work: yes (an honest commit at 04:00). Consequence: other. |
| 15 | **KEEP: what demonstrably earns its place.** The independent test designer and `gov accept`; rule 1 and the landing's G-1; role reads (g14); SANDBOX-1; the landing and the landing select; the operator's G1 to G7; the kernel gate; catastrophic rm; DEC-1137; READY by code. | exa-g6db: the test designer's F1 stopped a loose fix that failed 16 cases (P2); 11 cross-ticket or allowed-path reds at the landing (P2); 13 reds from the landing select, 4 real control-path edits caught (P4 Q9, Q10) | This is what Gov OS buys. | Ordinary work: yes, because engineers fix their own tests, commits go outside their paths and changes break other suites. Consequence: fails open (rm and SANDBOX-1: loses work). |

## 3. Part 6: the two questions

**Is Gov OS making product work cheaper or better yet, or only costing?** On cost: only costing, so far.
- Product took 4 % of the month's spend; coordination and ceremony took 56 % (P1).
- On exa-g6db the workers cost $1.10 and about 3 minutes, but the ticket took 2 h 30 min and ~$22 and did not close (P2).

On quality, there is narrow evidence that it is better: independent tests stopped a loose fix, and the landing caught 11 cross-ticket reds. There is no comparison without Gov OS, so "better" is not yet measured.

**Should EXAMIN's Wave 0 start now while Wave 2 closes?** Yes, now, on a thin loop: test designer, `gov accept`, and a close against the base.
- The only product signal of the month came from product runs (W5, 13 %). exa-g6db found seven product defects in one ticket.
- The plan limit binds: 100 % and 97 % in the last two weeks, and 56 % of this week used 32 h after the reset. So Gov OS work should be capped at closing what is in flight and fixing what EXAMIN hits.
- The product close (row 3) must be fixed first, or every close needs a named exception.

## 4. Measures from here on (product against Gov OS)

| measure | what it counts | where it is read today / what must log it | baseline from these parts |
|---|---|---|---|
| cost per ticket | lead + workers `total_cost_usd` per ticket, plus the CTO's turns on it | Lead and worker result logs (read today). The CTO's cost needs a ticket id per turn (not logged: must log). | Median LITE $6.71, STANDARD $18.88, FULL $51.19; the CTO adds ~$27 a ticket, not attributed; exa-g6db ~$22 |
| time per ticket | claim to green, claim to merge, claim to close | `.tickets` status history and first-parent merges (read today); claim to green needs a `gov accept` green stamp (must log) | Merge median 0.25, 0.58, 0.87 days; own-loop close 0.65, 0.59, 3.05 days; exa-g6db 44 min to green, no close |
| rounds | review rounds, and reviewer runs, per ticket | Verdict blocks in `docs/probes` and worker results; a round number in each record (must log) | Reviewer runs median 0, 1, 2; FULL 18 of 50 had more than 2 runs; maximum 14 (W2-88) |
| owner interruptions | owner messages by purpose (decision, relay, yes line, restart), pushes, night messages | Transcripts with origin human (read today, ±15 % on purpose); an owner-ask log line per package, job and ACT, tagged product or Gov OS (must log) | 544 in 31 days (18 a day; W5 30 a day): 134 relays, 140 package answers, 33 yes lines, 50 restarts; 206 pushes; 104 at night |
| drift incidents | red or allowed-path ejections at the landing; reopens for a defect; blocking findings after moderation; rules that crept back or were decided and not done | `land-done.txt`, `.tickets`, verdict blocks, `DECIDED-NOT-DONE.md` (read today); a drift tag on each (must log) | 11 red + 1 conflict in 90 lands; 25 of 502 findings blocking; 16 rules crept back, 6 decided and not done |
| spend split | weekly share: product, Gov OS building, coordination, ceremony, security | Transcripts (P1's method); a product or Gov OS tag at session start, from the ticket's repository (must log) | 4 %, 22 %, 32 %, 24 %, 19 % |
| rule growth | new rules a day against lifts; share with a basis line | Register (read today); the basis-line check of row 4 (must log) | 3.5 a day; 19 of 82 with a basis line |

Precondition for all of them: row 5, keep the transcripts.

## 5. Probed and found sound
- All five parts apply DEC-1204's two lines and keep their candidates as rows.
- None proposes a round, and none lifts anything.
- P2's CSV reproduces its medians.
- P4's guard and probe counts reproduce from their logs.
- The emergency's continuing items (GF-8, GF-9, the box, the operator's full permission) map onto rows 1 and 6 of this list, not onto new work.

Each finding is reversed by the evidence its part names; for this list, row 4 would be reversed if a weekly basis review exists elsewhere, and row 6 if an OS layer is shown unable to carry a static wall.
