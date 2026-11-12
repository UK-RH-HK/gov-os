# SWITCHED-OFF-1: every control switched off, lifted, relaxed or bypassed in the emergency (DEC-1128 (1), (2), (4))

By a research helper for the CTO (session 8ddb8b14), read-only, 2026-11-11 about 14:30 UTC, at `w2/integrate` `0c815d1e3`.
Part 1 of the brief is §1 to §4; part 2 (the set-up B sweep) is §5. Nothing was edited outside this folder. **M** = read in a
record, file or log (source named). **E** = my estimate. Dates are UTC.

## 0. What to read first (five findings)

1. **W2-141's guard rule is not live today.** DEC-1128's note and the brief say it is live from the 13:31 re-pin. It is not.
   The re-pin put W2-141's code into `gov` (`src/gov/guard/reads.py`), but the rule that refuses an engineer's wide search
   is in two staged hook files (`docs/changes/W2-141-hook/role_reads.py` and `pretooluse.py`) that "the owner's operator
   copies over the live files" by a separate ACT (`docs/changes/W2-141-hook/README.md`; `ACT-REPIN-W5.md`, section "W2-141's
   hook": "a separate ACT of the operator"; "There is no hook to remove: this act wrote none"). The live hook files are
   unchanged since 11-09 (`pretooluse.py` `74f8dbea4761`, `role_reads.py` `5407aade9417`; no commit on `.claude/hooks/` after
   `9cce7430d`, 11-09 23:53). **I checked it by running the live hook** (the pinned python, planted calls, the call log sent to
   my scratch folder, nothing executed): an engineer on W2-141's own ticket (`GOV_TICKET=DAEO-xwro`) who Greps the whole
   repository for `def test_` is **allowed** (exit 0); the same engineer's Read of `tests/acceptance/W2-141/README.md` is
   **refused** (rule `g14`), so the ticket resolved correctly. Consequence: under DEC-1128 (2) the staged hook ACT must not be
   queued until set-up A shows 100 %. The "W2-141's rule included" in DEC-1128 (3) and DECISIONS-IN-FORCE line 508 is wrong as
   a statement of what is live.
2. **Set-up A has measured nothing yet against the bar** (§4). It is built, its briefs are approved, its launch script is
   installed, but no corpus was extracted, no labels written, no tuning round and no held-out run done.
3. **The live guard probably cannot show 100 % as declared**, for two reasons that exist today (§4): its own error path
   refuses calls it could not judge (14 of 38 refusals in three days, M), and since ACT-GUARD-FIX-4 it lets through, by
   design, writes whose target it cannot work out (53 of 169 planted "must refuse" cases, M). Set-up A will count both.
   DEC-1128 (3) already says the lift does not wait; the owner should know the likely result before the run.
4. **Several gates were never switched off in code, only skipped by the CTO's own route.** The strict `gov close` gates
   (trailers, containment, the ratchet) are running now at the lift's formal closes and refuse them (W2-122's close,
   11-11 13:38). DEC-1127 (held PROPOSED) would accept 18 old merges as history. That is a control "returning" in effect;
   DEC-1128 (2) speaks of controls that were switched off, so the owner should say whether it applies here (§1 B2).
5. **The nightly is the safety net for most "moved to the nightly" lifts, and it is stopped** (four crontab lines
   commented out since 11-02). Nothing has a ticket or a date to restart it (§3).

## 1. The controls switched off, lifted, relaxed or bypassed

Sources used for every row: DEC register entries named; `governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md`
(row ids T-, Q-, G-, R-, O-, M-), `packages/LIFT-1/P1-PLAN.md`, `DECISIONS-IN-FORCE.md` "Lifted", `packages/DECIDED-NOT-DONE.md`,
`tests/optin-lifted*.txt`, `.claude/settings.json`, `.claude/settings.local.json`, `crontab -l`, `governance/project/path-map.yaml`.

**How to read "when".** `gov plan --open` (run at 14:2x, M) gives 99 open tickets in 21 batches. A batch has no date of its own.
FORECAST-W2-3 gives dates only for the lift (11-11), the closes (11-12), EXAMIN's copy (W2-27, batch 16) and Wave 2's end. DEC-1126 (2)
ended usage rule (A) at the lift, so I use FORECAST-W2-3's "(A) ends at the lift" column: W2-27 on **11-16** (range 11-14 to 11-19).
I spread batches 1 to 16 evenly from 11-12 to 11-16 (about a quarter of a day each). That is an interpolation (E), plus or minus two
days, and the allowance (about 20 to 25 meter points left after the closes, E) can push it later.

**"What must be true before it returns".** For a guard rule: DEC-1128 (2), set-up A's evidence at 100 % on the path map's actions.
For a gate or check: the ticket's acceptance or the decision named.

### A. The guard (the live hook `.claude/hooks/pretooluse.py`, `role_reads.py`, `bash_writes.py`, and the product's `src/gov/guard/`)

| # | Control | What was done, when, by what | Why | Home ticket | Must be true before it returns | When |
|---|---|---|---|---|---|---|
| A1 | **The product's full guard**: write scope at edit time (allowed paths), command-form refusals, settings, root-search and second-name reads, counterpart reads, long-path and `~` refusals, unknown tools (`src/gov/guard/`, `template/governance/kernel/hooks/pretooluse.py`) | Replaced in this repository by the five-rule hook: DEC-953 item 2 (10-30), ACT-1-GUARD applied 10-30 21:38 (`6c36c7b5c`). Built and tested in the product, not wired here. Its tests moved to the opt-in suite `lifted` (`tests/optin-lifted-guard.txt`, 435 lines, DEC-1061 (3a)) | 79 of 86 logged refusals were false; W2-50 cost 36.5 h and about $46, W2-58 26.2 h and $34.66 (INVESTIGATION G-4) | **None.** G-4 (product default `guard.profile: five-rules \| full`) is "a re-scoped ticket after the lift"; no `.tickets/` file carries it; it is named in P1-17's package (not yet written). W2-42 (`DAEO-fau3`, batch 12) is "deferred" for it | Set-up A at 100 % **on a rule that set-up A measures**. As declared, set-up A measures the five-rule hook plus the path map's blocks. The full guard's extra rules (write scope, command forms) are not in its label rules, so none of them can show 100 % until a declaration covers them | No date. P1-17 package after the lift |
| A2 | **Post-command containment** (the PostToolUse and PostToolUseFailure hooks: snapshot before, compare after, restore out-of-scope changes) | Hook entries removed from `.claude/settings.json` by ACT-1-GUARD, 10-30 (G-5; `settings.json` has PreToolUse, PreCompact, SessionStart, Stop, SubagentStop only, M). Cases in `optin-lifted-guard.txt` ("containment", 145 lines) | Second check on the same thing; it restores files, so it can lose work (G-5) | None (G-5 "P1-11", the one Contract re-baseline, not started) | As A1 | No date |
| A3 | **Freeze and pause in the guard**: refusing an agent's `gov pause --off`, the git-mirror lookup (G-6) | Not wired with the full guard (A1) | Defends against an adversary (ADR-0001); about 637 s of nightly | None | As A1 | No date |
| A4 | **CAP-62's escape hatch** (`dangerouslyDisableSandbox`) refused | Not part of the five rules; W1-47 cases opt-in (DEC-1061 decision 7) | Outside the five rules | None | As A1 | No date |
| A5 | **Rules 1 and 5's reading of Bash**: "write target unresolvable and the text names `tests/acceptance/`" and "a reviewer's unresolvable write", plus reading inline and heredoc code (`bash_writes.py`) | Narrowed to writes the guard resolves: ACT-GUARD-FIX-4, 11-03 13:49 (`3bc25241f`), DEC-1050 (12), G-1, G-2. Backstops: the landing's check that every commit touching `tests/acceptance/` carries `Role: independent-test-designer` (live in `tools/land.py`), and a clean `git status` of the reviewed tree (a brief line, not code) | 48 of the first 61 refusals came from rule 1, all false | W2-42a (`DAEO-03ub`, in progress, batch 5) holds the parser and G-7's re-scope; row 123's repair "after the lift, a guard ticket" has none filed | A tighter rule is a "new guard rule" (DEC-1128 (2)): set-up A at 100 %. Set-up A will also count today's let-through writes as wrong allows (§4) | W2-42a about 11-13 (E); set-up A: §4 |
| A6 | **The guard-refusal harvest** and its ceremony: the dispatcher's re-read of every transcript, `refusal_watch.sh`, per-refusal hand verdicts and cost field, a P1 after three of a pattern | Stopped 11-02: `guard_harvest_s` = 10^9 in `dispatch/config.json` (backup `.pre-dec1050`), DEC-1050 (6), G-10, G-11; `refusal_watch.sh` lifted; W2-119 closed/retired (DEC-1083). `log/guard-refusals.jsonl` stale since 11-10 02:12 (M, row 123) | 3,996 s a day of machine time | **None.** DEC-1128 (3) wants live false refusals "counted weekly from the call log": nobody owns it. Row 46 (weekly counts) "NOT STARTED: no home ticket yet" | Not a guard rule. The weekly count must exist and read the `error` refusals (the old harvest was blind to them) | No date: drift (§3) |
| A7 | **W2-84's hidden-half test cases** (363 cases: the guard refuses an evaluation set's hidden part under every tree) | Deleted with ACT-GUARD-SETS-1, 11-08 18:10 (`15952bbfa`), DEC-1061 (4), DEC-1097 (2). The refusal itself moved: hidden halves live in `~/gov-os-eval/`, outside every worktree (G-3), guarded by rule 2b (§2) | The cases tested a rule the new layout replaces | W2-84's close (a row); closed ticket | None planned. Rule 2b is tested by `sets_globs_check.py` (573 cases) outside the suite | Not returning |
| A8 | **Permission prompts for `rm`** (and "ping first, then run") | The ask rules for `rm` removed from `~/.claude/settings.json` by ACT-GUARD-FIX-4's `settings_rm_ask.py`; `rm` refused only when catastrophic (root, `.git`, tracked files, folders outside project and scratch). ACT-PERMISSIONS-1 (18 allow rules), -2 (two read folders, three hidden-folder denies); -3 (allow-list by form) built, in review (row 130) | 131 prompts in two days, 122 of them `rm` (O-7) | Row 130 (the CTO) | Not a guard rule in the DEC-1128 sense; the owner's decision (DEC-1050 (8)) | Row 130: owner's yes, then the operator agent |

### B. Gates and checks (the close, `gov check`, the tests, the nightly)

| # | Control | What was done, when, by what | Why | Home ticket | Must be true before it returns | When |
|---|---|---|---|---|---|---|
| B1 | **Gitleaks scanning**: the rebuild's memory-indexing scan, the landing's pre-check, the close's scans, the nightly's scan, the staged-content scan, the secrets-indexing check | `governance/project/secrets.yaml` `scan: off`; DEC-1045, 11-02 20:57. In the pinned gov since window 2. Tests that run the real gitleaks are in `tests/optin-lifted.txt` (W1-15, W1-16, W2-50, W2-69, W2-71, W2-107, `tests/unit/secrets_check`) | Private repository, never shared; W2-69's tests alone started about 120 gitleaks; load 54 to 76 | None (the feature stays built; "every other repository keeps it on") | The owner's approval of a weekly full scan; no other return planned | Not scheduled |
| B2 | **The strict `gov close` gates**: containment, trailers and `WORK_WITHOUT_TASK`, ratchet lists, probe staleness and form, escalation counter, repair ticket, STORE_STALE and context packet, checkpoint freshness, pre-close `gov check` (DEC-953; Q-2 to Q-11) | **Lifted by practice only.** The CTO's route skipped them; the product code (`src/gov/close/`) still has them. Product switch `close: strict\|smart` is W2-115. Their cases are opt-in (W2-01, W2-07, W2-53, W2-68, W1-30 folders and `tests/unit/close`, 189 lines in `optin-lifted.txt`). **Now they run**: the closes at the lift hit them (W2-122 refused 13:38: six old merges with no `Task:` trailer; containment findings left on W2-126, W2-92, W2-96) | A close refused by gates that guard against nothing the aim names (Q-2: 0 of 30 direct runs passed) | **W2-115** (`DAEO-emq1`, open, batch 7) for the switch; the lift's blockers: DEC-1127 (PROPOSED) and ACT-CLOSE-HISTORY-1 (`drafts/lift-close-blockers/`) | A decision of the owner on DEC-1127; W2-115's acceptance for the product switch | Switch: W2-115, about 11-14 (E). The closes: now |
| B3 | **`product-traceability-trailers`** (`gov check` family, `template/governance/kernel/checks/product-traceability-trailers.yaml`: still `severity: hard-block`) | Read as a warning by a ruling, not by a change: DEC-1123 (3), 11-10, "for D-10, the re-pin and the lift, until W2-115" (Q-8). 424 findings recorded, not fixed | 424 October commits without `Implements:` | W2-115, batch 7: its KPI line and the two paths were added (`.tickets/DAEO-emq1.md` lines 29, 30, 49, M). The kernel file changes only by CIT-P (CAP-33) | The check reports the 424 as warnings and `gov close` runs without TRAILER_MISSING (the line's own test) | About 11-14 (E) |
| B4 | **The ratchet lists** (`path-map.yaml`): `accepted_reds: []`; `load_sensitive`: 24 entries (1 W1-19 p95 under DEC-757, which is DONE; 23 W1-46 live-session cases under DEC-760/762 with `fixed_by: W2-M364`); `acceptance_exemptions`: 7 commits (5 added 11-10 under DEC-1123 (4)) | Frozen: DEC-1052 Q-10, "no new entry". 23 entries name a list row that sits in closed W2-57 (`DAEO-cy5o`): no open owner | A known red hiding behind "flaky" | W2-115 (Q-10); DEC-1127 repoints 4 entries (W1-19 latency to W2-155) | Q-10's switch in W2-115; the owner's DEC-1127 | W2-115 about 11-14 (E) |
| B5 | **The 0.5 s warm-query budget** (W1-19, W2-13 warm real-model p95: measured 0.543 and 0.587 s) | A named red for the re-pin and the lift: DEC-1125 (1), 11-11. Budget unchanged | Red alone and idle; "the gap is not noticeable" (owner) | **W2-155** (`DAEO-ar89`, P4, batch 14) | The cases at 0.5 s p95 on an idle machine, or a stop at 2 lead-hours with evidence to the owner | About 11-15 or 11-16 (E) |
| B6 | **"Green D-10 run" for three closes** (W1-01b, W2-66b, W2-90c) | D-10's ruled red counts as the green run: DEC-1126 (7), 11-11 | D-10 ended with a named red | Those three tickets (batch 1 and 6) | Their own acceptance | At the closes |
| B7 | **Three D-10 cases**: W1-33's auditor case and W1-05's install case report-only until their features return; W1-46's research-install case OPEN | DEC-1111, 11-09 (item 2 decided as a P2 by the CTO under DEC-1112 (2)) | Red by design while the full guard and the install gate are off | None (each leaves `tests/optin-lifted*.txt` "by the switch that turns its feature back on") | A1's condition for the guard cases | No date |
| B8 | **The `lifted` and `breadth` opt-in suites**: 4 files, 3,846 lines: `optin-lifted.txt` 189, `optin-lifted-guard.txt` 435, `optin-lifted-breadth.txt` 1,251, `optin-lifted-guard-breadth.txt` 1,971. Cases built, never run unless `GOV_TESTS_OPTIN` names them (`tests/conftest.py`) | DEC-1061 (D-4's cut, merged `6008a41f`, 11-03/04). The full run fell from about 20,000 to 5,628 cases. `lifted` ran once, report-only, in D-10 (run 2: 77 failed and 6 errors, all known) | "Moved, never deleted" (DEC-953) | Per feature: guard-full and containment: none; strict close: W2-115; gitleaks: none; W2-154 (`DAEO-l4gf`, batch 8) fixes the close's serial plugin treating an opted-out entry as "not in the run" | The feature's switch takes its lines out of the list, in that feature's ticket | W2-154 about 11-13 (E). Otherwise no schedule |
| B9 | **The nightly and every full run** (04:00 nightly, 08:00 check, `@reboot` check, 09:30 runs sweep) | Four crontab lines commented out: DEC-1049 (three, 11-02), DEC-1050/DEC-1051 (sweep). Dispatcher's pre-nightly landing hold set to an empty window (`nightly_hold_from/until` "00:00"). The full suite ran twice by hand (D-10, 11-10) | "Nothing scheduled runs until the refactoring is finished" (DEC-1050 (5)) | **None.** EMERGENCY-TOOLS-1 row A3: "none (restore at the lift)"; T-12 built (2 slots, no clean-tree check) | "The owner's word" (DEC-1049, DEC-1050 (5)). No ticket, no date | Drift (§3) |
| B10 | **Scoped runs instead of whole checks**: leads run no `gov check` (T-1); the always-added lists only when a record path changed (T-4); leads' serial phase only what the product selects (T-5); W1-19 and W1-21 only on model-path changes (T-6, in `test-map.yaml`); attribution once each way against the head without the batch (Q-1); G-1 landing check | DEC-1050 (1)-(4), DEC-1052, done 11-02 to 11-06. Each says "the nightly catches it within a day" | 5 hours of serial wall per 17 lead runs; 4 h 22 min attribution phases | Their own lifts are done; the net they rely on is B9 | The nightly (B9) or an equal full run, so a miss is seen | See B9 |
| B11 | **Checkpoint and Stop-hook rules**: committed `gov checkpoint` record per round (R-6); checkpoint freshness as a gate (Q-4) | R-6 lifted in practice (DEC-1057). **Approved but not applied:** unregistering the Stop hook's automatic checkpoint (R-7, `stop.py` still in `.claude/settings.json`) and the Stop-hook waiter check (O-5, `stop_waiter_check.py` still in `.claude/settings.local.json`). P1-PLAN P1-3 (ii): "R-7: no record found" | A turn-end checkpoint that shadows the real resume; 741 files in the main tree | None | The owner's operator applies an ACT (a lift, so a class (b) yes) | No date |
| B12 | **Ticket and process rules in this repository**: `Implements:` optional, two-commit rule lifted (R-12), a ping per owner item (R-11), ACTs for records (O-6), heartbeat rituals and scratch `deadman.py` (O-5), `--main` on sync (R-10), the load-average `gate_check.py` (O-10) | DEC-1050, DEC-1052, DEC-1057; "Lifted" in DECISIONS-IN-FORCE lines 145-147 | Ceremony cost | D-11 (the weekly basis review, DEC-1052's standing practice): "not started; after the lift" | D-11's review | After the lift; no date |
| B13 | **The dispatcher's slots memory rule** (O-A1) | Lifted: the committed `dispatcher.py` admits memory by the Load Balancer's forecast; `"memory_rule": "slots"` in the scratch `config.json` is read as the forecast (`dispatcher.py` lines 1132-1157, M). DEC-1052 O-A1 | Double-counted memory refused a lead with 15.9 GB free | W2-121 (`DAEO-cb2b`, batch 6) | Its own tests | About 11-14 (E) |
| B14 | **Usage rule (A)** (only the lift's critical path runs) | Ends at the lift (DEC-1126 (2)); the 80 % brake stays | The week's allowance | none | n/a | At the lift |

**Before the emergency (DEC-953, 10-30):** the strict close, escalations, repair tickets, containment and trailers as refusals,
the ratchet lists and their owner commits, probe staleness, the re-pin ladder, the memory arithmetic as a gate, the guard beyond
its five rules (A1 to A4). Ended outright: the pre-close gate (a) to (h), `record_checks.sh`, close windows, holds and cut-offs,
the 90-minute rule, the red-nightly hold, the nightly's booking window (DECISIONS-IN-FORCE 143-144).

**Returned before DEC-1128 (so not covered by it):** D-4's seven green cases and ACT-SELECT-FIXES-1's always-run lists went back
into the gates by ACT on 11-09 (DEC-1103 (2), DEC-1104 (1); `a46d4517`, `8038e0ee`). Both tighten.

**Approved to lift but still on in code (product switches, "after the lift", option A):** T-2, T-3 (W2-45 `DAEO-neam`, batch 12, about 11-15),
Q-2 to Q-11 and T-9 (W2-115, batch 7), M-1's context ceiling (W2-04 `DAEO-u4oz`, batch 1), G-4 to G-6 (no ticket, A1).
They are lifted here by practice, not by switch.

## 2. Guard rules made live in the emergency without set-up A's evidence (DEC-1128 (2): "new guard rules")

All of these went live before DEC-1128 and before any set-up A result. "Kind" says whether the change adds refusals (tightens) or lets
more through (loosens; a loosening adds possible wrong allows, which set-up A counts). The evidence column is what each had at the time;
none of it is set-up A's blind-label, held-out, 100 % design.

| # | Change | Live | Kind | Evidence it went live on (M) |
|---|---|---|---|---|
| N1 | Five-rule hook wired (rules 1 to 5), full guard off (ACT-1-GUARD, `6c36c7b5c`; hook `f7533c611`, `a4e52779f`) | 10-30 21:38 | both | 38 of 38 planted cases; 0.2 s a call |
| N2 | Rule 4: installs ask only in the CTO's session, refused everywhere else (`383bf17f1`, DEC-957) | 10-30 21:23 | tightens | 38 of 38 planted |
| N3 | ACT-GUARD-FIX-1 (`c3392f468`): read-only Bash commands pass | 10-30 23:00 | loosens | 4 logged refusals, 49 planted pass |
| N4 | ACT-GUARD-FIX-2 (`ffc60703e`): inline code judged per command part | 10-31 02:58 | loosens | 24 logged refusals all false; 54 of 54 planted |
| N5 | ACT-GUARD-FIX-3 (`e662684a1`, round 2 after a failed independent review): rules 1 and 5 read what a command writes | 11-02 10:35 | both | 61-row corpus, no true positive in it; 31 of 61 refused before, 2 after (3.3 %); 252 planted; 270 unit cases |
| N6 | ACT-GUARD-FIX-4 (`3bc25241f`): rules 1 and 5 judge only resolved writes; **new refusal: catastrophic `rm`**; reviewer record path `reviews/` | 11-03 13:49 | both | 451 planted pass; of FIX-3's 169 planted "must refuse" cases 53 are now let through by design; 562 real `rm` calls replayed, 0 refused in practice; independent review READY |
| N7 | ACT-G14 (`4edd196c5`): role separation from the path map: engineer never reads `{ticket_tests}`, test designer never reads `{ticket_impl}` | 11-03 16:42 | tightens | Replay of 8,228 engineer and 9,015 designer calls: 178 and 35 would-be refusals, all read as honest by the CTO's engineer (not blind); 0 crashes; 146 planted pass; the owner decided F4 |
| N8 | ACT-G14b (`e02d55e40`): a coordination ticket's tests are its own folder only | 11-03 21:11 | loosens | 151 planted (6 new), `test_live_hook.py` 63, FIX-4's 467 |
| N9 | ACT-GUARD-SETS-1 (`15952bbfa`): rule 2b, hidden sets outside the repository, for the measured roles; W2-84's cases deleted | 11-08 18:10 | tightens | Rehearsed end to end, 0 failures; live check 453 run PASS |
| N10 | ACT-INDEP-WALLS-1 (`147706ae4`, with ACT-SANDBOX-SEAL-1): walls hidden, rule 2c (W2-56's tuner refused `~/.claude/projects`) | 11-09 13:06 | tightens | `walls_check.py` 245 run 0 failed before and 331 after (planted HOME); wall hook 83, built wall 84; replay's one false refusal was fixed |
| N11 | ACT-GUARD-CALLLOG-1 (`b7a373cf9`): the call log | 11-09 18:13 | no decision changes | Not a rule; rehearsed; log live (first day validates PASS) |
| N12 | ACT-OPERATOR-1 (`2a6462653`): rule 2d, no session writes into the operator's folder (but `queue/`) or the call log; commit freeze | 11-09 19:02 | tightens | Rehearsed in two clones with a planted HOME; review READY |
| N13 | ACT-SETS-GLOBS-1 (`9cce7430d`): four more hidden globs and the line rule keyed on them | 11-09 23:53 | tightens | `sets_globs_check.py` 385 run PASS live, 573 in the rehearsal, 0 failed; live hook 8 ms to 12 ms |
| N14 | **W2-141's rule (an engineer's wide search into its own acceptance folder refused)** | **Not live** (§0 item 1): staged only | would tighten | Rehearsed with the new pin: 21,919 calls replayed over 48 h, 0 changed under the CTO's ticket, 31 allow-to-deny under W2-141's (all intended), 0 deny-to-allow; `test_g14.py` 4 intended cases red; review READY. **No set-up A evidence** |

Live guard decisions, from `~/.gov-os/guard-calls` (live sessions only, session ids that are UUIDs; replays and rehearsals excluded; the log
holds hashes, never contents): 11-09 8,387 calls, 10 refused; 11-10 10,226 calls, 23 refused; 11-11 until 14:11, 2,145 calls, 5 refused
and 1 ask. Refusals by rule over the three days: `error` 14, `2-listing` 12, `5` 5, `2b-line` 3, `3-secret` 2, `2-hidden` 1, `2c` 1, `4-ask` 1 (M, my count).
The log cannot say which refusals were false; nobody has labelled them.

## 3. The drift: controls with no home ticket, no return condition, or neither

| # | Drift | Why it is drift | Suggested home |
|---|---|---|---|
| D1 | **The full guard (A1), post-command containment (A2), freeze and pause (A3), CAP-62 (A4)**: no ticket, no condition set-up A can test | G-4 to G-6 are "a re-scoped ticket after the lift"; none filed; set-up A's declaration does not cover them | The owner decides whether they are dropped for this repository (then say "not returning") or need a declaration |
| D2 | **The weekly count of live false refusals** (DEC-1128 (3)) | Harvest off; the call log is read by hand; `error` refusals invisible to the old harvest; rows 46 and 123 have no ticket | One small ticket or a line in W2-172's driver (batch 7) |
| D3 | **The nightly (B9)** and with it the net for B10's "moved to the nightly" lifts | Four lines commented out; return "the owner's word"; no ticket or date; D-10 is the only full run since | A row in the lift's ready list: when, who decides |
| D4 | **The `lifted` suite (B8)** | Ran once, report-only; nobody is named to run it again; guard-full and containment lines have no feature switch | Run it with the nightly when that returns, or say it is archive |
| D5 | **R-7 and O-5 lifts approved, never applied (B11)** | Approved in DEC-1052; "no record found" (P1-PLAN P1-3 (ii)) | An ACT, or withdraw the approval |
| D6 | **23 `load_sensitive` entries** (W1-46 live-session cases) | `fixed_by: W2-M364`, a list row held by closed W2-57; no open ticket; DEC-1127 repoints only the W1-19 entry | Repoint at a ticket, or retire the entries (a cases rewrite, DEC-1111 (2)) |
| D7 | **Gitleaks (B1)** | Stays off by decision; no ticket, no review date. Fine if the owner says "permanent here"; the basis review (D-11) is not started | D-11 |
| D8 | **B12's process rules** | Same: they lean on D-11, not started | D-11 |
| D9 | **The `product-traceability-trailers` kernel file still says hard-block (B3)** while the ruling says warning | The ruling holds until W2-115 changes the file (batch 7); in between, a stale reader sees a hard block | W2-115 (already) |

## 4. Set-up A's state against the 100 % bar

**The bar (DEC-1128 (2), declaration section 8).** Every action the path map covers judged right: no false refusal, no wrong allow; the
declaration adds no unjudged and no unlabelled; on each held-out half (the real replay and the planted set), in every rule class. Actions
outside the path map are outside the bar. A pass bounds the error rate at about 3 over N (about 0.03 % on the real half, 0.5 % on the
planted half, 4 to 15 % on one class), and does not prove no gap.

**Built and approved (M):** the design (`SANDBOX-GUARD-EXP-1.md`, DEC-1099 with ten answers; set-up B dropped by DEC-1112 and DEC-1128);
the declaration (`SANDBOX-GUARD-EXP-DECLARATION.md`, amendments A1 to A5; A6, the pin move, drafted in `drafts/w2-149-sgx/PIN-AMENDMENT-A6.md`,
not recorded); the harness (`drafts/sandbox-exp/`: `extract_corpus.py`, `prepare_a.sh`, `run_a.py`, `score.py`, five fixed briefs); the seal and
walls (ACT-INDEP-WALLS-1, 11-09); the launch script W2-149 (merged, installed 11-10 15:41 `baac0b2c2`; its own live sandbox cases S9, S11, S12
passed 3 of 3; accept 206 pass); the four briefs approved once with two changes, plus the overlap auditor's brief (DEC-1113, 11-09). The pinned
commit was `f000adda4`; A6 moves it to a commit after the install ACT.

**Measured against the bar so far: nothing.** `drafts/sandbox-exp/README.md`: "Nothing here has run on the corpus." No corpus extracted, no writer
has written, no labels, no tuning round, no held-out run, no result. Set-up B ran once on 3 harmless actions in a scratch clone (a wiring check) and is dropped.

**What exists beside it (not set-up A, not blind, not the bar):** replays and planted suites that went with each ACT (§2), for example 21,919 calls
replayed for W2-141; the live call log; three days of live refusals (§2). They show cost and some false refusals; they do not show 100 %.

**What is left:** A6 recorded; the search of the overlap auditor's dry-built tree at the pin (F40); the extractor; writers 1 and 2; labellers and the
overlap auditor; the owner's rulings on flagged cases; round 0 on the tuning half; at most three tuning rounds; freeze and hash; the held-out runs
(A as live, A tuned); one independent review; the result. Cost: about $100 or 4 meter points (E, USAGE-RUBRIC-2 section 4), CPU only; elapsed 3 to 4 working days,
brake at 8 (declaration section 11). Until now it was held by usage rule (A) (FORECAST-W2-3 row 8); (A) ended at the lift (DEC-1126 (2)), the 80 % brake stays. No path-map
or deny-list ACT through the operator agent before 11-11 20:02Z (row 87). Earliest start after the lift: 11-12 (E); a result about 11-17 to 11-19 (E).

**What I expect it to find (E, from §2 and §3):**
- The live hook will be "unjudged" on every call that hits its own error path: 14 refusals in three days were `error` (row 123: `list index out of range`, a revision it
  cannot classify). The declaration's bar counts unjudged as a miss.
- ACT-GUARD-FIX-4 lets through writes whose target it cannot work out. Of FIX-3's 169 planted "must refuse" writes, 53 are let through by design. If the writers' planted halves
  include such writes, they are wrong allows under the declaration's labels ("refuse-labelled and the hook allows" is a wrong allow, even for class 8, a subprocess's write).
- Therefore "A as live" probably misses 100 %. Then the declaration's Q8 route is "tuned A's changes come as an ACT if they cut false refusals with no new wrong allow". DEC-1128 (2)
  now says a tuned guard goes live only at 100 %. If the owner means 100 % literally, the tuned guard may never go live and the let-through writes stay. Worth one sentence from the owner
  before the run: is "100 % on the path map's actions" "no wrong allow among actions the path map names" (what I read), or every class of the declaration?
- A guard rule that returns, other than those set-up A labels (A1 to A4), has no measure. §3 D1.

## 5. The set-up B sweep (DEC-1128 (4), DEC-866)

DEC-1128 (4): set-up B is dropped entirely, not a Wave 3 row; the leads are not sandboxed; the path map and the guard are the controls; set-up A stays; the workers'
existing launcher sandbox stays as it is. Lists only; nothing edited. Row ids are DECIDED-NOT-DONE rows. Line numbers read at `0c815d1e3`.

Many files say "set-up B a Wave 3 row": that wording is now false. Each line is "re-word" (the fact stays, the Wave 3 promise goes), "retire" (the plan goes), or "keep" with a reason.

| # | Path:line | What it says | Change DEC-1128 (4) implies |
|---|---|---|---|
| S1 | `docs/plan/WAVE_3_PARKING.md:36` (W3-P30) | "Set-up B (the sandbox generated from the path map), built by a different route: the OS write list for a script's write inside the worktree (W2-56's S2 gap) and `gov rebuild` inside the sandbox (S13) go with it" | **Retire** the row. The S2 gap stays a named, accepted gap (W2-56 S2/F1 already name it) |
| S2 | `docs/plan/WAVE_3_PARKING.md:34` (W3-P28) | A ticket for ranked search for sandboxed workers without opening every Unix socket (W2-56 S8 reach, S10) | **Owner to say.** It changes the workers' launcher sandbox (a socket allowance), so it is "sandbox work beyond the existing launcher sandbox". Recommend retire; the fallback (an unranked, named search) is the standing answer (DEC-1035 (2)) |
| S3 | `docs/plan/WAVE_3_PARKING.md:35` (W3-P29) | W2-56's R6: the CLI's `.git/config.lock` placeholders fail git in concurrently sandboxed workers; a clone per worker or an upstream fix | **Keep** with a reason: it concerns today's launcher sandbox, not set-up B; "not reached today" (the CTO launches workers one at a time) |
| S4 | `docs/DECISION_REGISTER.md:14134-14138` (DEC-1112 title and (1)) | "the sandbox experiment narrowed to set-up A (set-up B a Wave 3 row)" | Already marked: Status line carries "Changed by: DEC-1128 (4)". **Keep** (a register entry is not edited; DEC-866 marks the change) |
| S5 | `docs/DECISION_REGISTER.md` DEC-1099 (1), DEC-1098 (4) | The experiment as designed, with B | Add "Changed by: DEC-1128 (4)" marks if absent (DEC-866); text stays |
| S6 | `governance/project/orchestration/DECISIONS-IN-FORCE.md:395` | "DEC-1112 (2026-11-09): the sandbox experiment narrowed to set-up A beside D-10 (set-up B a Wave 3 row)" | **Re-word** to "set-up B dropped, DEC-1128 (4)"; line 509 already says so |
| S7 | `packages/DECIDED-NOT-DONE.md:43` (row 25), `:51` (row 28), `:52` (row 29), `:79` (row 48), `:107` (row 66) | Row 25 "the sandbox-and-guard experiment (4) design to the owner, then run, both results before W2-56 builds" (narrowed by DEC-1112); row 28 the seal (DONE, applied in ACT-INDEP-WALLS-1); row 29 the run (rest is row 66); row 48 the sandbox labellers automated; row 66 "set-up A fully beside D-10; set-up B a Wave 3 row" | Rows 25, 29: **re-word** ("both results" becomes set-up A's). Row 28: **keep** (the seal protects set-up A's held-out halves). Row 48: **keep** (set-up A's labellers). Row 66: **re-word**, drop "set-up B a Wave 3 row". Row 137 is this sweep: tick it when done |
| S8 | `packages/LIFT-1/P1-PLAN.md:191` (P1-19) | "DEC-1112 (1): the path-map guard alone, measured fully, set-up B a Wave 3 row" | **Re-word** |
| S9 | `packages/SANDBOX-GUARD-EXP-DECLARATION.md:9 (A1), 39, 89, 225-258 (7 (b)), 320 (section 11 B row)`; and the "Set-up B" parts of sections 1, 3 item 4, 5 Q2, 10 items 1-2, 13 item 8 | Set-up B's design, scoring (with a permissive control), 33 CPU-hour brake | **Keep as record, marked "not run, dropped (DEC-1128 (4))"**; amendment A1 says "Wave 3 row": **re-word** that clause. The declaration is the experiment's pre-registration, so do not delete |
| S10 | `packages/SANDBOX-GUARD-EXP-1.md:15, 144` | The design's set-up B ("the guard plus a sandbox generated from the same path map") | **Keep as record**, add a one-line header note |
| S11 | `packages/ACT-INDEP-WALLS-1.md:103, 204` | "Its wall is set-up B's sandbox, once proven"; "set-up B's sandbox closes them" (the tuner's residual reads) | **Re-word**: no sandbox will come; the walls' residual (rule 2c's limits, 2b's limits) stay as named residuals. DEC-1103 (3)'s "the sandbox added once proven" is the same promise: mark it changed |
| S12 | `.tickets/DAEO-wnnz.md:33, 44, 115, 118, 145` (W2-56) | "Set-up B is a Wave 3 row"; S13's `gov rebuild` inside the sandbox deferred "with set-up B" | **Re-word** those four clauses. A reviewed open ticket: DEC-757 (6) forbids edits to reviewed open tickets; a marked KPI-line edit under DEC-1088's standing rule, by the CTO |
| S13 | `docs/changes/W2-56-CIT-E.md:29, 214` | "set-up B ... is Wave 3's"; "`gov rebuild` inside the sandbox is deferred to Wave 3 with set-up B" | **Re-word** (a change record; add a dated note, do not rewrite) |
| S14 | `.tickets/DAEO-6ox0.md` (W2-40, EXP-002, open, batch 1, class research, FULL): three lifted lines "the sandbox cases (`denyWrite` on a path that does not exist yet, symlinks, seccomp, `bypassPermissions`, subagents in a sandboxed worker, `excludedCommands`)", "file tools, hooks and MCP servers outside the sandbox", "live auto-compaction", "[lifted, DEC-1083: re-scoped to S3]"; one live line: the hook time limit. Also `.tickets/DAEO-jdqr.md:110` (closed W1-46) "open residuals until experiment EXP-002 (Wave 2)" | The sandbox-case measurements existed to design a stronger sandbox. **Owner to say**: retire the three lifted lines (recommended; nothing consumes them if no sandbox work follows) and keep the hook-limit line. **W2-40 is the one ticket by id that still plans sandbox measurement** (the brief's "W2-40"). Also `packages/PLAN-W2-DEC953.md:240` and `READY-AFTER-LIFT-1.md:46` list it |
| S15 | `docs/plan/WAVE_2_WBS.md:612` (DEC-779), `:624` (DEC-769 "leads sandboxed"); `docs/plan/WAVE_2_REVISED_PLAN.md:153, 294-301 (4.6 "Keystone 6: ... leads sandboxed"), 353, 495`; `packages/REPLAN-W2.md:32` ("D. The leads' sandbox (K6)"); `docs/plan/WAVE_2_TRIAGE.md`, `WAVE_2_LIST.md` | The old plan: leads run in the OS sandbox (W2-21) | **Retire the "leads sandboxed" promise.** W2-21 (`DAEO-1ahb`) is closed and gave leads a "ticket-lead role with lead rights", no sandbox. DEC-769 ("Leads run sandboxed, in W2-21", status ACCEPTED) is not marked: add "Changed by: DEC-1128 (4)" (DEC-866) |
| S16 | `governance/project/prompts/w2-orchestrator.md:68, 148` | "Your session is not sandboxed"; "After W2-21 closes: gov launch lead <ticket> starts a lead ... sandboxed" | Line 68 **keep** (true). Line 148 **re-word**: workers sandboxed, leads not |
| S17 | `governance/project/briefs/LEAD-w2-common.md:92-99` | Workers start through `gov launch`, sandboxed, with a step 0 sandbox check | **Keep**: this is the workers' existing launcher sandbox, which DEC-1128 (4) keeps |
| S18 | `.gov-runtime/scratch/orchestrator/drafts/sandbox-exp/` (`gen_b.py`, `run_b.py`, `tests/test_b.py`, `wiring/`; README lines 6-7, 27, 47-48) | Set-up B's generator, runner, tests and wiring, "kept as the record and not run" | **Retire** (delete under O-8 once the owner agrees; the record branch keeps them) |
| S19 | `packages/FORECAST-W2-3.md`, `USAGE-RUBRIC-2.md`, `CHECKPOINT.md` | No "set-up B" text found by my search (counted 0); "set-up A's run" lines stay | none |
| S20 | `.tickets/DAEO-52ku.md` (W2-149) | Mentions set-up A only (S16, S24); 0 set-up B hits | **Keep** |

Not found: no ticket, brief or prompt in `governance/project/briefs/` plans sandboxed leads beyond S15 and S16. No ticket other than W2-40 (S14) and W2-56's four clauses (S12) plans set-up B work.

## 6. What I did not check

I did not read `~/gov-os-eval/`, `~/gov-os-runs/` or any `hidden`, `memory-verdict`, `memory-verdict-2` folder. I did not run a test suite. I did not read the transcripts. Rows B10 and B12 rest on the plan's approved-row list and DECISIONS-IN-FORCE, not on a re-check of each tool in `tools/`. `crontab -l`, `gov plan --open` and the planted hook runs were the only commands that ran code; the planted runs wrote one call-log line to this folder's `calls/` under my scratchpad, none to the live log.
