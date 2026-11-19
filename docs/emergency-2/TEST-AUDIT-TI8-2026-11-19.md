# Audit of the test folders (TI-8): one line each

`docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md` · independent auditor (read-only; Sonnet) · 2026-11-19 · at `w2/integrate` `ed00f823b` · nothing was deleted, moved or run; the owner's yes comes before any cut (DEC-1218 (3))

## 1. Method

- **Folders.** 223 leaf folders under `tests/` hold test files: 168 under `tests/acceptance/` and 55 under `tests/unit/`. That is the 223 of TI-8. Another 20 folders hold none: 3 unit folders (`context`, `guard`, `operator`) have only `__pycache__`; 17 acceptance folders have only `__pycache__` or a support module (`W1-02`, `W1-03`, `W1-47`, `W2-90`, `W2-110` keep fixtures other suites import). They are not rows.
- **Cases.** `pytest --collect-only` with the opt-in suites on, then off, then `lifted` alone. 24,473 cases: 18,653 in the default run, 2,220 in opt-in `lifted`, 3,600 in opt-in `breadth` (the inventory counted 24,471 and 18,651; two more landed since). "Cases" in the table is all / default run.
- **Time.** From the JUnit files of the full suite of 05:18 on `712c71cba` (13,879 s over 18,714 cases): `.gov-runtime/nightly/20261119T051835Z-712c71cba87b/`. It ran the default cases only, and a folder with no default case shows 0 s here (W2-69 timed three cases that have since moved to `lifted`). A few files it timed are gone since (W2-54's context-packet file), so a time can be a little high.
- **Reading.** For each folder: its README or the ticket (`.tickets/`), the test file names, the docstrings, and the cases' names. For the doubtful ones I read the files. I did not read every case. Where I could not tell, the verdict ends in `?`.
- **Rules.** `retire` only where E2 or a decision from DEC-1211 on retires what it asserts, or the cases are a copy of another kept folder. `retire (B1)` is the strict close and the secrets scan (DEC-1218 (3)). `weekly tier` is slow cases that prove a live feature; "slow" means a case over 5 s in that run; one fast case stays in the default run. `thin` is a folder where part is retired or redundant; the Cut column names how many cases.

## 2. The result

| Verdict | Folders (of which `?`) | Cases, all | Cases, default run | Cases the verdict carries |
|---|---|---|---|---|
| retire | 18 (6) | 1,963 | 428 | all 1,963 (12 folders firm: 1,758; 6 with `?`: 205) |
| thin | 30 (17) | 6,232 | 4,228 | 2,136 counted (1,208 in the default run); W2-66 and W2-184 not counted |
| weekly tier | 17 (4) | 2,401 | 2,025 | 346 slow cases (5,830 s) |
| keep | 158 (12) | 13,877 | 11,972 | none |
| **Total** | **223 (39)** | **24,473** | **18,653** | |

- In `thin`, 548 of the counted cases are TI-7 candidates (W2-94 up to 306, W2-98 up to 242: "up to", a designer chooses) and 130 are opt-in cases (W1-26) switched off, not retired by an E2 line.
- `retire (B1)` rows also include 242 s of gitleaks cases inside live folders: W2-88's `scan_folder` and `scan_speed` (38 cases) are counted under W2-88's weekly tier note, not as a retire row.
- Of the 18 retire folders, 12 are B1 or A-2 or L2-4 and need no new decision (W1-30, W2-01, W2-07, W2-53, W2-68, W2-69, W2-71, W2-107 are B1; W2-159 and `unit/session_watch` A-2; W2-97 L2-4; W2-49 CIT-P). Six carry `?` and ask the CTO or the owner: W1-42, W2-51, W2-72, W2-113, W2-130, W2-182.

**Effect on suite time** (the 05:18 run: 13,822 s of test time took 80 minutes on 4 workers, so 1 s of test time is about 0.35 s of wall time; a straight scale, which a few long cases make pessimistic):

| Step | Test time out of the default run | About, wall time |
|---|---|---|
| retire folders (only 428 of their cases are in the default run) | 165 s | 1.0 min |
| thin cuts that are counted by file | 573 s | 3.3 min |
| W2-88 gitleaks files | 242 s | 1.4 min |
| weekly tier (17 folders; one fast case stays) | 5,830 s | 34 min |
| **Total** | **6,810 s, 49 % of the suite** | **about 40 min saved, 80 to about 40** |

The retirements alone save about 6 minutes, 7 %. Three slow groups sit inside folders with another verdict and are not in the 5,830 s: W1-16's 15 code-graph cases (330 s), W1-01's 94 s merge-walk case and W1-26's 69 s planted-defects case (+493 s, +3 min). The weekly tier is the whole of the speed-up, as TI-5 said. TI-5's seven folders carry 180 slow cases and 3,800 s here (the page said about 930 cases and 74 minutes: it counted every case of those folders); the other 10 folders add 166 slow cases and 2,030 s: unit/memaudit, W1-20, W1-27, W2-13, W2-52, W2-54, W2-122, W2-187, W2-116, W2-203. W2-88 alone is 1,264 s of slow cases (22 % of the weekly total; one case, a real redis copy, takes 680 s), and a single long case limits how fast four workers can finish, so the wall-time gain is likely larger than the straight scale.

## 3. What the audit found beyond the inventory

1. **The TI-2 list is smaller than the page said.** W2-54's context-packet cases are already deleted (M1, W2-200); it now holds the schema, the cache and the CPU embedder, plus one 177 s `gov check` over the whole repository (weekly tier ?). W2-50's guard cases are deleted; what is left is the launcher's own folder (keep) and 23 gitleaks cases (retire (B1)). W2-65's one case is the twelve-field SubagentStop block (keep ?). Only W2-159 and `unit/session_watch` retire whole under A-2; W1-42 retires as a past report (?).
2. **Held-out `Read` deny rules.** Five folders still assert the wall that E2 2.2 and 2.7 replaced with the transcript scan: W1-38 `heldout_step` (18), W1-28 `fixture_copies` (24), W1-50 `freeze_fixture_settings` (14), W1-27 and W1-46 `held_out` (3): 59 cases. `gov.util.heldout` and `held-out.yaml` still exist, so the code and the tests go together if the owner agrees (`?` rows).
3. **`judge_commits` goes dark after B1.** Its only caller is the strict close (`src/gov/close/command.py:559`); the queue has its own checks (`queue/checks.py`). W2-72 (41 cases), `unit/containment` (16) and W1-50 (7) test it. `read_merge` (the decisions checker) and the pause freeze cases are live and stay. L2 does not list these; the test designer should confirm.
4. **hit@k floors.** W1-19 `real_models` (6), W1-21 `dev_tier` and `family_check` (16) and W2-61 `scores` and `baseline` (17) hold hit@5 against a pass line of 80 or CAP-10's 85. E2 5.2 says hit@k is no target or floor anywhere (39 cases, `?`).
5. **TI-3 and DEC-1218 (3) differ.** TI-3 keeps the secrets-scan tests for the one pre-public scan (E2 2.11); the owner's DEC-1218 (3) retires them with B1. I marked them `retire (B1)` as told (W1-15 91, W1-16 92, W2-50 23, W2-69, W2-71, W2-107, `unit/secrets_check` 159, W2-88 38). `gov ci staged-secrets` stays (L2 row 17) and is the code the pre-public scan needs, so after B1 it has no test of its engine. If the owner wants one real-gitleaks smoke case kept, name it before the cut.
6. **Guard-era paperwork still pinned.** W1-01 `bootstrap_record` (9: operator diff procedure, install rule, recorded guard denials), W1-05 `switch_over_record` (1), W1-06 install approvals (46, `?`), W2-33 `install_rule` (4 cases: the CTO-only install rule in the role file, which the CTO changes by 3.5), W2-188 `citp` (7), W1-48 `sandbox_prereqs` (19: bubblewrap and socat, for the retired sandbox), W2-49 (160: CIT-P) and W2-182.
7. **L2's list is wider than the strict close.** `unit/close`: the 16 files of Table 3 are 337 cases; three more lifted files (gates, repo, fingerprint, 79 cases) look strict-only (`?`). W2-115 `strict` and `switch` (20), W2-194 `accepted` (4, L2-2), W2-121b `b_s2_closes` (15, B3) and W2-66 follow `gov close` into `gov queue` and are rewrites, not deletions.
8. **Scratch tools.** `unit/orchestration` holds 373 cases for tools that retire at the cut-over or after the proving landing (old dispatcher 215+9, balancer 28, dead-man 13, merge queue 60, W2-97's 48); the other 447 are the walls launch script and the GPU slot module (live). `acceptance/W2-97` (19) repeats the same merge queue (L2-4).
9. **Duplicates.** The inventory's six groups are 7 functions in all; the live ones are `test_f4_planted_integrate_branch_itself_is_skipped` in W2-157, W2-159 and W2-170 (identical bodies; W2-159 retires), and one pair each in W2-98 and W2-130 (my scan counts bodies over 200 characters; the inventory's W2-100/W2-101 pair is shorter). None is worth a folder verdict.
10. **G1-2 and G5 touch live folders.** 13 to 15 reads of P-* packages sit in W2-134, W2-37, `unit/impact` and `unit/retrieval` (G1-2 removes them, revise in that change). TI-6 lists W2-130, W2-49 and W2-61; W2-51 is my addition. W2-49 and W2-51 are named in audit 07 C-5 (regenerate or retire with the Contract); W2-130 and W2-61 wait on G5 and G4.
11. **`gov.tasks.bridge` has no caller.** W1-14 (63 cases) and `unit/bridge` (11) test the proposal-to-ticket library, which nothing in `src/gov` or the template imports (grep). No line retires it, so both stay `keep ?` until someone says whether `gov discover --ticket` replaced it.
12. **The 12 `keep ?` and 17 `thin ?` rows are mostly one question each**: is the thing still wanted (W1-44 lessons, W2-100/W2-101 mirrors, W2-184 against W2-201, W2-193 and `unit/dispatch` after B1/B3).

## 4. What to ask the owner

- Confirm `retire (B1)` for the secrets-scan folders, or keep one real-gitleaks smoke case (item 5).
- Say yes to the held-out `Read`-rule cases (item 2) and the hit@k floors (item 4) as thin cuts.
- Say yes to the weekly tier for the 17 folders (the 4 `?` ones are W1-27, W2-116, W2-203, W2-54).
- The six `retire ?` rows wait on his or the CTO's word.

## 5. The table

Sorted by verdict, then folder. "Cut" is the cases the verdict moves or retires (for `retire`, all of the folder); "slow" is cases over 5 s; "opt-in" cases are not in the default run.

| Folder | Cases (all / default) | Test s | What it proves | Verdict | Cut | Why |
|---|---|---|---|---|---|---|
| `acceptance/W2-49` | 160 / 45 | 5 | Contract v4.2 lite: CIT-P, CIT-E, source map, owner answers | retire | all 160 | pins a past change proposal (CIT-P is retired, E2 3.5 and 2.10); audit 07 C-5 regenerates the Contract's forms and retires W2-49's agreement test |
| `acceptance/W2-159` | 100 / 100 | 8 | the orchestrator's two Stop checks (waiter, idle) | retire (A-2) | all 100 | E2 6.2 A-2 folds the idle-check and waiter Stop hooks into the run-time tool; L2 row 32 retires `gov session-watch`; code unregistered since the switch-off |
| `unit/session_watch` | 59 / 59 | 2 | gov session-watch: idle, once-a-turn, route, waiter, helper watch | retire (A-2) | all 59 | E2 6.2 A-2 and L2 row 32: retires (about 1,040 lines, 5 test files) |
| `acceptance/W1-30` | 485 / 7 | 42 | gov close, the strict close: gates, receipt, repair ticket, probe, iteration | retire (B1) | all 485 | L2-1: the strict close retires (DEC-1217 (1), DEC-1218 (3)); 478 lifted cases; the 7 default cases (close and receipt) are the close record, whose writer stays, so re-home them in W2-202/W2-206 first |
| `acceptance/W2-01` | 88 / 0 | 0 | gov close: trailers base, merge form, owner-accepted history, probe gate | retire (B1) | all 88 | L2-1 strict close (trailer-history and probe gates, DEC-1217 (1)); all 88 cases already opt-in `lifted` |
| `acceptance/W2-07` | 69 / 0 | 0 | gov close by class, commit gates, repair tickets, close share | retire (B1) | all 69 | L2-1 (repair tickets, iteration/escalation, gates) and L2-2; all 69 cases opt-in `lifted` |
| `acceptance/W2-53` | 57 / 0 | 0 | probe gate's merge measure and the ratchet (accepted_reds) | retire (B1) | all 57 | L2-1 and L2-2 (the lists retire); all 57 cases opt-in `lifted` |
| `acceptance/W2-68` | 22 / 0 | 0 | batched closes, reuse on the same code, two fingerprints | retire (B1) | all 22 | L2-1 retires `gov.close.batch run/run_scoped/reuse/refresh`; all 22 cases opt-in `lifted` |
| `acceptance/W2-69` | 352 / 0 | 0 | secrets check over what the stores hold | retire (B1) | all 352 | secrets scan (E2 2.11, DEC-1218 (3)); 352 cases opt-in `lifted`; TI-7 also names its 68- and 48-case planted-string functions |
| `acceptance/W2-71` | 304 / 1 | 0 | secrets check passes a real commit hash for row W2-L423 only | retire (B1) | all 304 | secrets scan; 303 lifted cases plus one default premise case that reads the lifted list itself |
| `acceptance/W2-107` | 43 / 0 | 0 | gitleaks verdicts remembered by content hash | retire (B1) | all 43 | secrets scan (E2 2.11, DEC-1218 (3)); all 43 cases opt-in `lifted`; TI-3 would keep them for the pre-public scan |
| `acceptance/W2-72` | 41 / 41 | 4 | containment's merge rule matches DEC-912 | retire (B1) ? | all 41 | `judge_commits` has one caller, the strict close (close/command.py:559); the queue has its own checks (queue/checks.py); the live post-command hook cases are deleted; 41 cases |
| `acceptance/W2-97` | 19 / 19 | 17 | the local merge queue (merge_queue.py) | retire (L2-4) | all 19 | L2-4 yes (DEC-1217 (1)): the scratch tool retires after one green proving landing through `gov queue`; unit/orchestration repeats its cases (60 more) |
| `acceptance/W1-42` | 22 / 22 | 0 | Wave 1 exit run on the dev tiers | retire ? | all 22 | pins a past report (docs/plan/wave-1-exit/EXIT-REPORT.md); exit runs are replaced by the release acceptance (A-4: W2-46/47; F-8); a Wave 1 history record, no live feature |
| `acceptance/W2-51` | 47 / 39 | 2 | Wave 2 plan validator: counts, CIT-P lines, exit criterion 7 | retire ? | all 47 | validates WAVE_2 plan files against the Contract (CIT-P lines, exit criterion 7); exit runs replaced by the release acceptance (A-4); audit 07 C-5 retires the validator with the Contract it checks |
| `acceptance/W2-113` | 11 / 11 | 6 | adopted product's CTO named at adoption: A0 writes the coordination ticket and roster key | retire ? | all 11 | A-4 retires W2-00's coordination record (no role in §4) and B-4 gives the CTO no operator; the guard half is already deleted; asks the CTO to confirm A0's step goes |
| `acceptance/W2-130` | 83 / 83 | 79 | link clean-up of the old register: 87 drifting decisions marked | retire ? | all 83 | TI-6: reads this repository's old register and git history (record_reading); the register is re-based (DEC-1211, audit 8, W2-203) and the 87 marks are history; waits on G5 |
| `acceptance/W2-182` | 1 / 1 | 0 | the nightly's drift reds of 2026-11-13: no revised case lowered, skipped or marked | retire ? | all 1 | one case checks a past revision against a hard-coded BASELINE of test marks; paperwork on a closed fix, no live feature |
| `acceptance/W1-01` | 50 / 50 | 141 | bootstrap guardrails: only the test designer commits acceptance tests; the bootstrap record; integration merges | thin | 9 | test_w1_01_bootstrap_record (9) pins the guard-era operator diff procedure, install rule and recorded guard denials (E2 2.2-2.4, 2.6); the authorship rule stays (TI-6); one 94 s case walks this repository's merges (weekly tier ?) |
| `acceptance/W1-05` | 6 / 6 | 0 | dogfood switch-over: the five subagent definitions | thin | 1 | switch_over_record (1) pins a past record that the diff check is retired; the five agent definitions stay |
| `acceptance/W1-15` | 124 / 18 | 30 | secret rules and pre-index filter (gitleaks) | thin | 91 | retire (B1): 91 lifted cases run real gitleaks (E2 2.11, DEC-1218 (3)); check_time_limit and product_data stay; TI-3 would keep them for the pre-public scan |
| `acceptance/W1-16` | 167 / 44 | 338 | codebase-memory wrapper (code graph) and its secret rules | thin | 92 | retire (B1): token_rule (80) and builtin_allowlist (12) judge the gov token rule with the gitleaks binary (E2 2.11); 15 slow code-graph cases (330 s) are weekly tier |
| `acceptance/W1-48` | 172 / 43 | 1 | Claude Code version pin | thin | 19 | sandbox_prereqs (19) record bubblewrap and socat as owner installs for the sandbox, retired (E2 2.2); pin, cli, drift stay (breadth 129) |
| `acceptance/W2-33` | 96 / 96 | 0 | the three layers' role files and typed handoff | thin | 4 | install_rule (2 functions, 4 cases) pins the guard-era CTO-only install rule in the orchestrator role file (E2 2.2; DEC-1214 G7 (c)); the role-file text is the CTO's to change (3.5) |
| `acceptance/W2-50` | 65 / 42 | 37 | durable scratch root: launcher's own folder, never-indexed | thin | 23 | secrets_scan_scale (23) runs real gitleaks over large stores: retire (B1); launcher folder, last_review and never_indexed stay |
| `acceptance/W2-115` | 88 / 88 | 193 | gov close, the smart close: batch, reds, selection, record, verify | thin | 20 | strict (14) and switch (6) assert the strict/scoped switch that B1 removes; the other cases move onto `gov queue` (L2 B1 S3: W2-115 stays green, rewritten) |
| `acceptance/W2-121b` | 52 / 52 | 35 | gov dispatch part b: landing hand-off, closes, nightly hold, heavy steps | thin | 15 | b_s2_closes (15) asserts the dispatcher waits on a conflicting `gov close`, which L2 B3 deletes from dispatch/landing.py |
| `acceptance/W2-194` | 11 / 11 | 29 | absent reds against the base, a short --base, accepted reds when scoped | thin | 4 | accepted (4) asserts `accepted_reds`, retired by L2-2 (DEC-1217 (1)); absent and base stay (the queue records base reds) |
| `unit/close` | 721 / 275 | 89 | gov close library: strict builders, nightly, select, serial, queue pieces | thin | 416 | retire (B1): the 16 files of L2 Table 3 (337 cases: history, ratchet, state, repair_ticket, refuse, measured, every_finding, batch_reuse...) and gates, repo, fingerprint (79, ?); select, serial, nightly, evidence, tool, w2_115, w2_191, w2_193, w2_194, w2_200, w2_202 stay |
| `unit/orchestration` | 820 / 542 | 252 | the CTO's scratch tools: old dispatcher, balancer, dead-man, merge queue; walls launch script | thin | 373 | retire (cut-over W2-207, L2-4): balancer 28, dispatcher 215, dispatcher_stall 9, cto_safety_nets 13 (dead-man), merge_queue_base/q1/seed/speed 60, w2_97_merge_queue 48 = 373; the walls launch script, reanchor, GPU slot module (447) stay |
| `unit/secrets_check` | 196 / 67 | 165 | secrets scan builders (gitleaks) and the scan: off switch | thin | 159 | retire (B1): 12 scan files (159 cases, w2_88_folder/s27_bound/scan, w2_107, token_rule ...) run or model gitleaks; dec1045_switch (34, scan: off) and w2_20_pools (3) stay |
| `acceptance/W1-06` | 105 / 55 | 1 | Wave 1 tool prerequisites: registry, pins, vendor digests, ccusage | thin ? | 46 | approvals, ccusage and install_approvals (46) assert past installs cite an owner approval, the guard-era install ledger (E2 2.2-2.4; DEC-1214 G7 (c): the CTO approves); registry, pins, digests and vendor stay (vendor 14, digests/registry mostly breadth) |
| `acceptance/W1-19` | 41 / 31 | 17 | semantic retrieval, RRF and rerank | thin ? | 6 | real_models (6) hold hit@5 at a pass line of 80; hit@k is no target or floor anywhere (E2 5.2); fusion, rerank and index cases stay |
| `acceptance/W1-21` | 127 / 83 | 30 | gov retrieve with completeness (bundle, paging, expansion, authority) | thin ? | 16 | dev_tier (11) and family_check (5) hold hit@5 >= 80 and the dev-tier baselines (E2 5.2: no hit@k target); the rest is live retrieval |
| `acceptance/W1-26` | 430 / 77 | 235 | gov check G0-G2: families, audit and skill validators, planted defects | thin ? | 130 (opt-in) | 130 lifted cases (policy, skill version, decision citations, probe-record form) are checks switched off by DEC-1052, not retired by an E2 line: the owner decides; 223 breadth cases stay opt-in; planted_defects 69 s is weekly tier ? |
| `acceptance/W1-28` | 128 / 126 | 81 | gov pause, fixture copies, launcher cases | thin ? | 24 | fixture_copies (24: no fixture copies held-out.yaml) assert the held-out Read-rule wall that the transcript scan replaced (E2 2.7); pause, cancel, rollback, roles, launch stay |
| `acceptance/W1-38` | 116 / 32 | 51 | rulesync adapters and .claude ownership | thin ? | 18 | heldout_step (18) asserts one Read deny rule per held-out path written after generation (DEC-162), replaced by the transcript scan (E2 2.2, 2.7); rulesync and test_folder_rule stay |
| `acceptance/W1-50` | 119 / 115 | 23 | containment by commit trailers, merge reading, pause freeze | thin ? | 21 | freeze_* cases (gov pause) and read_merge (decisions checker) stay; judge_commits (7 cases here, also unit/containment and W2-72) has one caller, the strict close (close/command.py:559), so it goes dark after B1; freeze_fixture_settings (14) is the held-out deny-line wall (see W1-38) |
| `acceptance/W2-61` | 83 / 66 | 12 | standing 20-question memory measure, split under Policy 2 (d) | thin ? | 17 | scores (9) and baseline (8) report hit@5 against CAP-10's floor of 85 (E2 5.2) and a docs/research baseline record; the measure's other cases stay |
| `acceptance/W2-66` | 204 / 141 | 190 | path-scoped regression: selection, evidence, widening, limits, live test map | thin ? | part (not counted) | L2 Table 3 lists it (3,053 lines) for B1; the cases that run `gov close` move to `gov queue`, W2-115/W2-202/W2-206 cover selection and evidence; the 88-case live test-map file reads this repository's map and stays |
| `acceptance/W2-94` | 596 / 596 | 86 | EXAMIN's question set: form only (visible and hidden half) | thin ? | up to 306 (TI-7 candidates) | TI-7: 596 cases, 306 of them in seven functions of 130, 50, 29, 25, 24, 24 and 24 cases that each plant one bad input and read the refusal; keep boundary cases; 86 s |
| `acceptance/W2-98` | 502 / 502 | 15 | spec-writing skill: problem, goals, KPIs with failure lines, the check script | thin ? | up to 242 (TI-7 candidates) | TI-7: 502 cases, 242 of them in six functions of 88, 56, 25, 25, 24 and 24 cases that plant one placeholder text each (TBD, n/a, none ...); keep the class boundary cases; 15 s |
| `acceptance/W2-160` | 66 / 66 | 11 | gov wait and the helper watch | thin ? | 36 | gov wait stays (L2 row 37); s3_helper_watch (25) and s4_reads_and_writes (11) test `session-watch helper-watch`, retired by A-2 (L2 row 32) |
| `acceptance/W2-184` | 507 / 507 | 327 | RUBRIC-2 at launch: criticality to model and effort | thin ? | part (not counted) | 507 cases (88 parameterised functions, 327 s, none over 3 s) overlap W2-201 (rubric in code, DEC-1214 K1, which replaced DEC-1120's table) and unit/launch w2_184/w2_201 files; keep the cases that read the live rubric |
| `acceptance/W2-188` | 54 / 54 | 0 | adopt skill step 6 and the practice record, standing set | thin ? | 7 | citp (7) pins a CIT-P record, retired (E2 3.5, 2.10); copies, practice, skill, selfchecks stay |
| `unit/adopt` | 481 / 338 | 57 | gov adopt stages A0-A10, AS, MA, facts, lite gates, memory sets, W2-88 assessment | thin ? | 16 | test_w2_113_coordination asserts A0's coordination ticket and roster key (A-4 retires W2-00; see acceptance/W2-113); the rest is live adoption; 57 s |
| `unit/containment` | 30 / 30 | 1 | containment: judge_commits, merge reading, commit trailers | thin ? | 16 | test_judge_commits (12) and dec_572_lift (4) test `judge_commits`, whose only caller is the strict close (close/command.py:559); read_merge cases (decisions checker) stay |
| `unit/plan` | 75 / 75 | 2 | gov plan: dependency map, overlap, cycles; Wave 2 plan validator | thin ? | 9 | validate_w2 asserts the Wave 2 plan validator (retire ? with acceptance/W2-51); the rest stays (plan stays, L2 row 28) |
| `acceptance/W1-07` | 215 / 129 | 633 | gov CLI skeleton: envelope, config, registry, read/act classes | weekly tier | 37 slow | 37 cases of 138 take 484 of 633 s (read commands run for real, e.g. read_act, config on every command); fast envelope/help/registry cases stay |
| `acceptance/W1-20` | 51 / 35 | 136 | gov closure (closure of ids over the record and code graphs) | weekly tier | 9 slow | closure stays (L2 row 7); 9 cases of 35 take 131 of 135 s (real code graph, repeated runs) |
| `acceptance/W1-35` | 169 / 127 | 347 | skills: discovery, planning, independent test design, change | weekly tier | 9 slow | one skill-regression case takes 69 s and 9 slow cases take 346 of 347 s; skill text cases stay in the default run (TI-5) |
| `acceptance/W1-41` | 173 / 68 | 486 | gov adopt --lite and legacy importer | weekly tier | 19 slow | adopt stays; 19 cases of 100 take 434 of 486 s (real rebuilds, embedding policy); the rest stays in the default run (TI-5) |
| `acceptance/W2-13` | 99 / 99 | 266 | RETR-X-02 and the ranked lexical route (BM25, FTS5) | weekly tier | 9 slow | 9 of 100 cases take 230 of 266 s; one red at the 05:18 nightly; the fast lexical-policy and fusion cases stay |
| `acceptance/W2-37` | 120 / 120 | 549 | gov impact: code graph, execution, rows, stated links | weekly tier | 14 slow | 14 of 120 cases take 527 of 549 s (real code graph); 11 reads of P-* packages go with G1-2 |
| `acceptance/W2-52` | 65 / 65 | 187 | lite A7 and A10 stage records | weekly tier | 8 slow | 8 of 65 cases take 171 of 187 s (A10 gate runs a real pass) |
| `acceptance/W2-57` | 20 / 19 | 326 | load out of the close: rulesync probe, doctor probes, serial list | weekly tier | 11 slow | 11 of 19 cases take 316 of 326 s (doctor probes up to 91 s); TI-5 |
| `acceptance/W2-88` | 325 / 325 | 1645 | memory for any repository: assessment, plan, A9 lite, store layout | weekly tier | 47 slow + 38 retire (B1) | 47 of 325 cases take 1,264 of 1,645 s (f1_codegraph alone 860 s, one case a real redis copy 680 s); scan_folder and scan_speed (38 cases, 242 s) run real gitleaks: retire (B1) |
| `acceptance/W2-122` | 22 / 22 | 153 | seeded rebuilds from a warm base | weekly tier | 20 slow | 20 of 22 cases take 150 of 153 s (a real rebuild each); keep the fail-closed case in the default run |
| `acceptance/W2-171` | 141 / 141 | 469 | memory audit measure: control, retrieval figures, judged reader run, fault rule | weekly tier | 43 slow | 43 of 141 cases take 425 of 469 s (seeded pool draws, real retrieval); TI-5 |
| `acceptance/W2-187` | 210 / 210 | 332 | standing hidden set: drift check, repair, state, weekly maintenance | weekly tier | 23 slow | E2 5.9 reopens it for the weekly maintenance; 23 of 210 cases take 295 of 332 s |
| `unit/memaudit` | 411 / 411 | 541 | gov memaudit: pool draws, measure, standing set, maintain, driver | weekly tier | 53 slow | 53 of 386 cases take 460 of 541 s (seeded pool draws of 400 from 900 etc.); fast config, prompts and scan cases stay |
| `acceptance/W1-27` | 179 / 67 | 222 | gov doctor and gov rebuild (+ W2-67 test hygiene) | weekly tier ? | 15 slow | doctor and rebuild stay (L2 rows 4, 5); 15 cases take 127 of 222 s (real registry, real rebuilds); held_out (2) and temp-folder hygiene cases, see W1-38 |
| `acceptance/W2-54` | 78 / 64 | 258 | schema green here, time limit, query vector cache, CPU embedder | weekly tier ? | 5 slow | one case takes 177 of 258 s (gov check over the whole repository, minutes at load); the context-packet cases are already deleted (M1); audit_report, cache, embedder stay |
| `acceptance/W2-116` | 60 / 60 | 231 | integration branch's store, double-buffered, refreshed after each merge | weekly tier ? | 18 slow | live (the designers' store); 18 of 60 cases take 124 of 231 s (real re-index); fast config/status cases stay |
| `acceptance/W2-203` | 63 / 63 | 139 | old register archived and out of memory's index; the kept register in force | weekly tier ? | 6 slow | live (G4); 6 of 61 cases take 136 of 139 s (real citations check); one case still to revise after DEC-1215's revert (CTO handover §6) |
| `acceptance/W1-04` | 12 / 12 | 0 | tool-registry schema (W1-04 success 3) | keep | - | guard cases already deleted; what is left proves the schema the kernel template still ships |
| `acceptance/W1-08` | 235 / 121 | 49 | record schemas and templates (ticket, lesson, path map, frontmatter, id grammar) | keep | - | proves the live record schemas; fast (49 s for 235 cases, 114 breadth); test_w1_08_probe (7) is the probe-record type, ? with the probe gate |
| `acceptance/W1-09` | 87 / 51 | 38 | ticket vendoring, claims, READY rule | keep | - | live ticket model (E2 4.1) and the READY rule; 38 s |
| `acceptance/W1-10` | 101 / 46 | 10 | store and record graph | keep | - | proves the store memory is built on; 10 s |
| `acceptance/W1-11` | 142 / 47 | 12 | decision checker and owner-approval facts | keep | - | decisions checker (gov decisions, W2-45) reads merges for approval facts; fast, live |
| `acceptance/W1-12` | 21 / 21 | 6 | readiness schema and proposal templates | keep | - | live spec pillar (E2 1.1: help with the spec and KPIs); 14 cases read files, 7 need openspec (local_only) |
| `acceptance/W1-13` | 110 / 76 | 44 | gov readiness | keep | - | gov readiness stays (L2 row 3); 44 s |
| `acceptance/W1-17` | 65 / 47 | 37 | lexical index and shared store | keep | - | live memory; 37 s |
| `acceptance/W1-18` | 16 / 16 | 3 | Ollama on-demand lifecycle and fallback | keep | - | live embedder lifecycle; no always-on unit; 3 s |
| `acceptance/W1-22` | 25 / 24 | 8 | evidence validator and zero-result canaries | keep | - | live retrieval safety (canaries); 8 s |
| `acceptance/W1-23` | 10 / 10 | 1 | hierarchical synthesis notes | keep | - | live memory (synthesis); 10 cases |
| `acceptance/W1-25` | 52 / 39 | 54 | gov checkpoint (write, watch, resume) | keep | - | checkpoints are kept (E2 6.1, RT-5); 54 s |
| `acceptance/W1-29` | 45 / 42 | 4 | session hooks (PreCompact, SessionStart, Stop checkpoint hooks) | keep | - | hooks kept (E2 6.1 row 1); 4 s |
| `acceptance/W1-31` | 161 / 56 | 28 | governance share counter (gov telemetry) | keep | - | telemetry stays (L2 row 35; A-7 weekly measure); 105 breadth cases; hook markers are planted data, not the guard |
| `acceptance/W1-32` | 81 / 52 | 60 | gov status and the launcher's two residuals | keep | - | status stays (L2 row 1); 60 s |
| `acceptance/W1-33` | 99 / 99 | 2 | Wave 1 role definitions: agent definitions, kernel role files, roster | keep | - | guard_and_launcher (2) was cut to the launcher decision; 99 cases read role files that still stand; keep unless the CTO renames roles (3.5) |
| `acceptance/W1-34` | 8 / 8 | 0 | decision-package template | keep | - | live template; 8 cases (LITE) |
| `acceptance/W1-36` | 84 / 74 | 8 | skills: retrieval, audit, checkpoint/resume, adopt | keep | - | kernel skill text and declarations; 8 s |
| `acceptance/W1-37` | 4 / 4 | 0 | Superpowers three-skill vendoring | keep | - | vendored skills; 4 cases (LITE) |
| `acceptance/W1-39` | 67 / 39 | 101 | Copier kernel template and lock | keep | - | gov update/adopt rest on the template and lock; 101 s, 5 slow cases (42 s) |
| `acceptance/W1-40` | 73 / 38 | 56 | lefthook and CI workflow (tiers, evidence record) | keep | - | gov ci stays (L2 row 17); 56 s |
| `acceptance/W1-46` | 111 / 111 | 104 | worker session launcher (gov launch) | keep | - | launcher kept (L2 row 23); guard and sandbox cases already deleted; 104 s but no slow case; guard_wiring (20) and sandbox_settings (21) now assert launch without them |
| `acceptance/W1-49` | 98 / 70 | 8 | light auto-resume hooks (PreCompact, SessionStart) | keep | - | checkpoint/compaction hooks kept (E2 6.1 row 1) |
| `acceptance/W2-02` | 53 / 42 | 17 | record types: decision entry, audit report, adoption verdict, close record | keep | - | record schemas are live (the close record stays); 17 s |
| `acceptance/W2-03` | 39 / 30 | 4 | decisions as records, each with its own hash | keep | - | live record model behind the register and the store; 4 s |
| `acceptance/W2-05` | 64 / 32 | 77 | git environment of every check, hook and helper; settings re-sort | keep | - | guard-hook cases already deleted; the rest proves checks run on a clean git environment; 77 s, 32 default cases |
| `acceptance/W2-11` | 248 / 248 | 1 | briefs and the orchestration skill: twelve fields, two-refusal stop, supersession | keep | - | TI-7 names it, but its 77- and 24-case functions run once per kernel file, not per planted string; 1 s |
| `acceptance/W2-16` | 142 / 49 | 60 | immutable, hash-pinned releases (gov release) | keep | - | release stays (L2 row 30); 60 s, 93 breadth |
| `acceptance/W2-17` | 25 / 25 | 45 | gov update | keep | - | release feature (E2 6.1, F-7); 45 s |
| `acceptance/W2-18` | 25 / 25 | 32 | pinned install: a repository runs a fixed release | keep | - | `gov install` stays (L2 row 22); 32 s |
| `acceptance/W2-20` | 171 / 171 | 92 | machine-wide resource gate (slots, CPU, GPU, trip-wire) | keep | - | resources stays (L2 row 31); 92 s, 171 cases |
| `acceptance/W2-23` | 33 / 33 | 110 | adoption safety on a planted repository | keep | - | adopt stays; 110 s, 3 slow cases (69 s) |
| `acceptance/W2-36` | 41 / 41 | 18 | gov discover | keep | - | E2 6.1 build; 18 s |
| `acceptance/W2-45` | 38 / 38 | 52 | gov check runner semantics and scale | keep | - | check stays; 52 s |
| `acceptance/W2-55` | 78 / 53 | 24 | decisions tagged by domain, status, scope; in-force left out | keep | - | `--in-force` moves to gov decisions (L2 row 6, 18); 24 s |
| `acceptance/W2-56` | 154 / 154 | 86 | gov launch usable for every worker | keep | - | launch kept; sandboxed-session cases deleted; 86 s, 154 cases |
| `acceptance/W2-59` | 33 / 33 | 10 | pinned judge: declared checks and hook lines run from the pin | keep | - | guard-line cases deleted; pin kept (`gov install`); 10 s |
| `acceptance/W2-60a` | 223 / 223 | 157 | role, skills, model and effort loaded at launch; the launch record | keep | - | launch kept; 223 cases at under 2 s |
| `acceptance/W2-60b` | 52 / 52 | 40 | one record per session: model, effort, window, tokens, cost | keep | - | telemetry kept; 40 s |
| `acceptance/W2-62` | 58 / 43 | 2 | resume in full: session-start hook delivers the RESUME HERE block | keep | - | checkpoint/compaction hooks kept (E2 6.1); 2 s |
| `acceptance/W2-64` | 83 / 70 | 37 | record validator through check-jsonschema; docs/imported out of the schema check | keep | - | live check; 37 s |
| `acceptance/W2-76` | 22 / 16 | 64 | rebuild timings, 30-minute watchdog, one rebuild at a time | keep | - | rebuild stays (L2 row 5); one red at the nightly |
| `acceptance/W2-77` | 24 / 23 | 39 | the nightly's clean-up removes only its own clone | keep | - | nightly kept (A-1); 39 s |
| `acceptance/W2-81` | 318 / 318 | 29 | adoption proving ground: five synthetic repositories | keep | - | becomes the release's proving run (A-4, F-8); in progress; 29 s |
| `acceptance/W2-86` | 3 / 3 | 1 | kernel template embedded as the path map means it | keep | - | live; 3 cases, one red at the nightly |
| `acceptance/W2-87` | 21 / 17 | 11 | retrieval ranks by authority | keep | - | live retrieval; 11 s |
| `acceptance/W2-88a` | 35 / 35 | 0 | adopt skill text: Wave 0's practice in order, Verify section | keep | - | kernel skill text; 35 cases, 0 s; its README says no CIT-P record |
| `acceptance/W2-91` | 19 / 15 | 10 | full embeddings: root files, governance overlay, schemas | keep | - | live memory; 10 s |
| `acceptance/W2-92` | 144 / 144 | 111 | record and code graphs as routes of plain-question retrieval | keep | - | live memory; 111 s, 8 slow cases (89 s) |
| `acceptance/W2-93` | 81 / 81 | 37 | held-out half's validator and --sets-root (form only) | keep | - | guard case deleted; E2 2.7 set protection; 37 s |
| `acceptance/W2-95` | 28 / 15 | 4 | core-pathmap checks what it says | keep | - | path map is live (E2 1.2); 4 s |
| `acceptance/W2-96` | 190 / 155 | 112 | gov accept: the opaque acceptance runner | keep | - | accept stays (E2 6.1); 112 s |
| `acceptance/W2-104` | 43 / 43 | 21 | gov skilleval: run each skill's three scenarios, record | keep | - | skilleval stays (L2 row 33); 21 s |
| `acceptance/W2-108` | 25 / 25 | 59 | retrieval checks store freshness once per run | keep | - | live retrieval; the context-check part is already deleted; 59 s |
| `acceptance/W2-112` | 59 / 52 | 82 | one shared reranker serves every session | keep | - | GPU-never-spills rule (E2 6.3); 82 s, no case over 12 s |
| `acceptance/W2-115b` | 56 / 56 | 18 | gov queue: the product's deterministic landing | keep | - | the landing is kept and becomes landing-and-close (L2-1, E2 4.3); 18 s |
| `acceptance/W2-120` | 32 / 32 | 4 | skill validator refuses a skill with a permission field | keep | - | still guards against agents adding permission fields; 4 s |
| `acceptance/W2-121` | 179 / 179 | 136 | gov dispatch tick and status (part a) | keep | - | dispatch stays, rebuilt as the run-time tool (E2 6.1, L2 row 20); 179 cases at under 1 s each |
| `acceptance/W2-121c` | 62 / 62 | 54 | run-time tool slice 1: gov msg inbox files, one watch pass | keep | - | RT-6, RT-7 (E2 6.3); 54 s |
| `acceptance/W2-123` | 50 / 35 | 50 | shared embedding server, concurrent requests within its CPU cap | keep | - | embedder rules (E2 6.3); 35 default, 15 breadth |
| `acceptance/W2-124` | 46 / 46 | 88 | a rebuild without its semantic store fails named; adoption records it | keep | - | live adoption/rebuild behaviour; 88 s, 4 slow cases of 46 |
| `acceptance/W2-126` | 28 / 26 | 79 | machine-wide vector cache keyed by the text | keep | - | live; 79 s, one slow case |
| `acceptance/W2-128` | 121 / 121 | 12 | role/ticket/brief templates filled from one facts file | keep | - | E2 4.3 and 5.4 (templates, briefs by code); 12 s |
| `acceptance/W2-129` | 156 / 156 | 11 | gov links: incremental link-integrity check | keep | - | links stays (L2 row 24); 11 s |
| `acceptance/W2-131` | 29 / 29 | 1 | a register chunk in a bundle carries its own entry's id | keep | - | live retrieval of the register; 1 s |
| `acceptance/W2-133` | 48 / 48 | 1 | narrowed or gap-starting register item carries its own id | keep | - | live retrieval of the register; 1 s |
| `acceptance/W2-135` | 83 / 83 | 2 | a bundle line over 4,000 characters is cut and marked | keep | - | live retrieval guard; 2 s (83 cases, 8 functions) |
| `acceptance/W2-136` | 76 / 76 | 10 | gov plan: dependency map, launch batches, gov launch's check | keep | - | plan stays (L2 row 28); 10 s |
| `acceptance/W2-137` | 37 / 37 | 0 | shared reranker request cap raised | keep | - | live; 37 cases at under 1 s |
| `acceptance/W2-138` | 18 / 18 | 2 | the store's commit in each result; line-hash check | keep | - | live memory-by-construction (E2 5.4); 2 s |
| `acceptance/W2-142` | 13 / 13 | 0 | search again once in the kernel skills | keep | - | E2 5.3 "second search by the agent"; 13 cases |
| `acceptance/W2-145` | 79 / 79 | 76 | no private reranker beside the shared service | keep | - | E2 6.3 GPU rule; 76 s, no case over 11 s |
| `acceptance/W2-146` | 192 / 192 | 15 | the id reader reads every id form a repository declares | keep | - | live retrieve stop on a nonexistent id; 192 cases at 15 s |
| `acceptance/W2-147` | 25 / 25 | 0 | gov plan breaks a cycle only at a ticket inside it | keep | - | plan stays; 25 cases, 0 s |
| `acceptance/W2-149` | 198 / 198 | 157 | independent sessions' launch script (the walls) | keep | - | hidden-set protection via walls + transcript scan (E2 2.7, 5.10); guard case deleted; 198 cases at under 1 s each |
| `acceptance/W2-150` | 12 / 12 | 3 | memory's import closure free of the gates | keep | - | guard cases deleted; keeps memory standalone for adoption; 3 s |
| `acceptance/W2-152` | 67 / 67 | 24 | gov brief: a filled brief, refused when not READY | keep | - | brief stays (L2 row 16); 24 s |
| `acceptance/W2-153` | 155 / 155 | 6 | role template delivered at launch | keep | - | E2 1.2 roles stay apart through templates; 155 cases, 6 s; TI-7 lists it, its 81-case function runs once per role and copy, not per planted string |
| `acceptance/W2-156` | 34 / 34 | 17 | gov spend: the runaway brake | keep | - | kept until the run-time tool replaces it (A-1); 17 s |
| `acceptance/W2-157` | 122 / 122 | 42 | GPU backstop in the product | keep | - | E2 6.3 RT-4 (zero GPU spill); one function is a body-for-body copy of W2-159 and W2-170 (3 copies) |
| `acceptance/W2-158` | 61 / 61 | 54 | gov check --structural | keep | - | becomes the landing's after-step (L2 row 2); one red at the 05:18 nightly |
| `acceptance/W2-170` | 185 / 185 | 49 | memory audit: the set record (preflight, void, declare, map, counts) | keep | - | gov memaudit stays (L2 row 25; E2 2.7); 49 s; copies one body with W2-157/W2-159 |
| `acceptance/W2-172` | 163 / 163 | 69 | memory audit driver and schedule (cycle, active/stable rule, digest) | keep | - | E2 5.9 weekly maintenance; 69 s, no slow case |
| `acceptance/W2-173` | 93 / 93 | 31 | launch script follow-ups for the audit (effort, stop word, notes) | keep | - | live; 31 s |
| `acceptance/W2-174` | 222 / 222 | 23 | Verify pass and adoption facts file | keep | - | adopt stays; 23 s; TI-7 does not list it |
| `acceptance/W2-175` | 51 / 51 | 0 | role templates carry Policy 2's refusals and the stop after two refusals | keep | - | E2 1.2; 51 cases, 0 s |
| `acceptance/W2-178` | 21 / 21 | 26 | auditor's copy of a set leaves out dropped questions | keep | - | hidden-set protection (E2 2.7); 21 cases |
| `acceptance/W2-185` | 13 / 13 | 0 | adopted projects get the context watch hook; hook portability per hook | keep | - | hooks kept (E2 6.1); 13 cases |
| `acceptance/W2-189` | 43 / 43 | 8 | gov retrieve answers from the last good store when HEAD moved, naming it | keep | - | live memory; 8 s |
| `acceptance/W2-190` | 14 / 14 | 5 | adoption A3 refuses deleting a referenced or superseded file | keep | - | live adoption safety; 5 s |
| `acceptance/W2-191` | 30 / 30 | 6 | test map accepts any project-relative test target | keep | - | feeds the queue's scoped selection; 6 s |
| `acceptance/W2-192` | 30 / 30 | 5 | adoption stage AS, the spec audit | keep | - | E2 6.1 "finish"; 5 s |
| `acceptance/W2-195` | 45 / 45 | 6 | judging-work skill preloaded, briefed, checked, shipped | keep | - | A-13 trims the text to 3.4: rewrite, not retire; 45 cases, 6 s |
| `acceptance/W2-197` | 90 / 90 | 2 | memory by construction and the memory-use log | keep | - | E2 5.4, 5.6; 2 s |
| `acceptance/W2-198` | 33 / 33 | 3 | gov backup, gov memaudit scan, gov decisions basis | keep | - | E2 2.7, 2.8, 10.1; 3 s |
| `acceptance/W2-199` | 75 / 75 | 59 | run-time tool slice 2: the machine-aware dispatcher and load balancer | keep | - | RT-1, RT-3, RT-4; 59 s |
| `acceptance/W2-200` | 57 / 57 | 0 | gov context retired; the close records decisions from the ticket's sources | keep | - | asserts the retirement stays done (M1); 0 s |
| `acceptance/W2-201` | 240 / 240 | 40 | rubric in code (K1, RT-8); role files and criticality list | keep | - | RT-8; 240 cases, 40 s; one 36-case function reads each role file and class (live, not planted) |
| `acceptance/W2-202` | 39 / 39 | 26 | gov queue part 1: base reds recorded, acceptance at the landing, paused | keep | - | becomes the landing-and-close (L2); 26 s |
| `acceptance/W2-204` | 169 / 169 | 0 | the memory measure on any adopted repository by product commands | keep | - | release item (R-1); 169 cases, 0 s |
| `acceptance/W2-205` | 38 / 38 | 37 | run-time tool slice 3: every end messaged in 2 minutes (RT-2), relaunch | keep | - | RT-2, RT-5; 37 s |
| `acceptance/W2-206` | 45 / 45 | 62 | gov queue part 2: --dry-run, --select, --full, the after-step | keep | - | L2 A6, A8; 62 s |
| `unit/accept` | 215 / 98 | 44 | gov accept unit cases: start forms, clean-up under a signal, reports | keep | - | accept stays (L2 row 13); 44 s, 117 breadth |
| `unit/adapters` | 158 / 118 | 2 | rulesync adapters: generate, portability, adopted copies | keep | - | adapters stays (L2 row 14); 2 s |
| `unit/backup` | 12 / 12 | 0 | gov backup: hourly bundle, retention | keep | - | E2 2.8; 12 cases |
| `unit/brief` | 105 / 105 | 2 | gov brief: build, judging-skill check, memory block | keep | - | E2 5.4 memory by construction; 2 s |
| `unit/check` | 328 / 197 | 26 | gov check families: schemas, citations, path map, structural, runner speed | keep | - | check stays (L2 row 2); 26 s |
| `unit/checkpoint` | 13 / 13 | 3 | gov checkpoint | keep | - | kept (E2 6.1, RT-5); 13 cases |
| `unit/ci` | 17 / 14 | 0 | gov ci tiers and checks | keep | - | ci stays (L2 row 17); 17 cases |
| `unit/cli` | 14 / 9 | 5 | CLI envelope and version | keep | - | core; 14 cases |
| `unit/closure` | 8 / 7 | 0 | gov closure unit cases | keep | - | closure stays (L2 row 7); 8 cases |
| `unit/codeintel` | 82 / 82 | 11 | code graph: daemon, runtime path, stand-in tool | keep | - | live memory (code graph); 11 s |
| `unit/decisions` | 59 / 48 | 2 | decisions: canonical form, register, basis check, narrowed label | keep | - | gov decisions stays (L2 row 18); 2 s |
| `unit/discover` | 14 / 14 | 2 | gov discover: draft, tickets | keep | - | E2 6.1 build; 14 cases |
| `unit/doctor` | 50 / 43 | 0 | gov doctor | keep | - | doctor stays (L2 row 4); 50 cases |
| `unit/gitenv` | 72 / 63 | 2 | git environment of checks and hooks | keep | - | live; 2 s |
| `unit/hooks` | 217 / 216 | 11 | checkpoint, resume, context-watch, precompact and template hook lines | keep | - | hooks kept (E2 6.1 row 1); 11 s |
| `unit/impact` | 42 / 42 | 2 | gov impact unit cases | keep | - | impact stays (L2 row 21); 2 s; 15 reads of P-* packages go with G1-2 |
| `unit/install` | 51 / 51 | 14 | gov install: pinned, hash-checked | keep | - | install stays (L2 row 22); one red at the nightly |
| `unit/launch` | 971 / 971 | 42 | gov launch: role, rubric, record, templates, pause honoured | keep | - | launch stays (L2 row 23); 971 cases in 42 s |
| `unit/links` | 71 / 71 | 8 | gov links unit cases | keep | - | links stays (L2 row 24); 8 s |
| `unit/lock` | 38 / 24 | 0 | kernel lock and shipped paths | keep | - | live (gov update); 38 cases |
| `unit/memory_use` | 15 / 15 | 0 | memory-use log | keep | - | E2 5.6; 15 cases |
| `unit/msg` | 39 / 39 | 3 | gov msg: inbox, digest, stop check | keep | - | RT-6 (E2 6.3); 3 s |
| `unit/ollama` | 3 / 3 | 0 | Ollama lifecycle | keep | - | live embedder; 3 cases |
| `unit/optin` | 16 / 16 | 5 | the opt-in lists (`lifted`, `breadth`) and the conftest | keep | - | needed while any opt-in list exists; cut to the breadth rules when the `lifted` list empties; 5 s |
| `unit/pause` | 23 / 23 | 1 | gov pause | keep | - | pause stays (L2 row 12); 23 cases |
| `unit/queue` | 83 / 83 | 32 | gov queue: checks, land, select change, base reds, flags | keep | - | the landing (L2); 32 s |
| `unit/readiness` | 7 / 7 | 0 | gov readiness | keep | - | readiness stays; 7 cases |
| `unit/rebuild` | 229 / 120 | 12 | gov rebuild: compaction, seeded, integration, when-due, lock | keep | - | rebuild stays (L2 row 5); 12 s |
| `unit/records` | 3 / 3 | 0 | records and dangling links | keep | - | live; 3 cases |
| `unit/release` | 61 / 22 | 2 | gov release | keep | - | the owner's release; 2 s |
| `unit/resources` | 327 / 327 | 20 | resource gate: slots, GPU backstop, query start | keep | - | resources stays (L2 row 31); 20 s |
| `unit/retrieve` | 43 / 43 | 34 | gov retrieve: stated gap, stop on unknown id | keep | - | retrieve stays (L2 row 8); 34 s |
| `unit/semantic` | 11 / 11 | 0 | semantic fusion and rerank process | keep | - | live memory; 11 cases |
| `unit/skilleval` | 35 / 35 | 5 | gov skilleval | keep | - | skilleval stays (L2 row 33); 5 s |
| `unit/spend` | 22 / 22 | 0 | gov spend: runaway brake | keep | - | kept (A-1); 22 cases |
| `unit/status` | 48 / 38 | 3 | gov status and the integration-store line | keep | - | status stays (L2 row 1); 3 s |
| `unit/store` | 74 / 48 | 2 | store: fingerprint, register entries, archive, links | keep | - | live memory store; 2 s |
| `unit/synthesis` | 7 / 7 | 0 | hierarchical synthesis | keep | - | live memory; 7 cases |
| `unit/tasks` | 6 / 6 | 1 | tickets and tk wrapper | keep | - | live; 6 cases |
| `unit/telemetry` | 92 / 34 | 0 | gov telemetry: counter, session log, tokens | keep | - | telemetry stays (L2 row 35); 92 cases, 58 breadth |
| `unit/update` | 25 / 25 | 0 | gov update | keep | - | release feature; 25 cases |
| `unit/util` | 76 / 76 | 0 | shared helpers: digest, frontmatter, git runner, patterns | keep | - | live; 76 cases |
| `unit/validate` | 15 / 15 | 0 | evidence validator and canaries | keep | - | live retrieval safety; 15 cases |
| `unit/wait` | 14 / 14 | 2 | gov wait: liveness, command | keep | - | wait stays (L2 row 37); 2 s |
| `acceptance/W1-14` | 63 / 46 | 7 | proposal-to-ticket bridge | keep ? | - | `gov.tasks.bridge` has no caller in src/gov or the template (grep) and no command in the L2 table; ask whether `gov discover --ticket` (W2-36) replaced it; no retiring line found, so keep until answered |
| `acceptance/W1-44` | 5 / 5 | 2 | Phase-2 lessons as lesson records | keep ? | - | 5 cases read docs/lessons and run one retrieve; cheap; keep unless the lessons folder goes in G1 (?) |
| `acceptance/W2-32` | 268 / 268 | 248 | retrieval components: model pin, swap by configuration, learning loop, lexical tuning | keep ? | - | live memory; 268 cases at 0.9 s, none over 3 s; test_w2_32_record and its support mention hit@5 (check against E2 5.2) |
| `acceptance/W2-61h` | 39 / 30 | 5 | form tests of 28 new memory questions and the hidden half | keep ? | - | form only; G1-2 revises 4 P-* reads; 9 breadth |
| `acceptance/W2-65` | 1 / 1 | 0 | SubagentStop hook gives its block reason for missing twelve-field handoff | keep ? | - | guard half deleted; the twelve-field rule is live (W2-11) but Stop checks fold into the run-time tool (A-2): confirm the hook stays |
| `acceptance/W2-100` | 223 / 223 | 21 | domain skills A (backend, API, data, security): check, copies, imports, scenarios | keep ? | - | 223 cases from 44 parameterised functions repeat one set of skill rules over four skills, mirror W2-101 and share one body with it; a TI-7 candidate if the owner wants fewer, no retired content |
| `acceptance/W2-101` | 273 / 273 | 38 | domain skills B (frontend, UI/UX, DevOps) | keep ? | - | 273 cases mirror W2-100 over three skills; test_w2_101_check repeats the permission-line and missing-section refusals 33 and 24 times; a TI-7 candidate, no retired content |
| `acceptance/W2-134` | 28 / 28 | 15 | the memory measure re-anchors line-cited gold; never writes the sets root | keep ? | - | live measure tool (E2 5.3); 14 reads of P-* packages go with G1-2, revise in that change; s5_family_floor and s6_families_line (15) and four files mention hit@5: check against E2 5.2 |
| `acceptance/W2-193` | 22 / 22 | 72 | gov close's harness in an adopted repository (base run, no repair, no review gate) | keep ? | - | L2 B1 S3: stays green after B1, rewritten where it asserts the review gate or repair tickets (no_repair 4, no_review_gate 4) |
| `unit/bridge` | 11 / 4 | 0 | proposal-to-ticket bridge (gov.tasks.bridge) | keep ? | - | same library as acceptance/W1-14: no caller in src/gov or the template, no command in the L2 table; keep until answered |
| `unit/dispatch` | 192 / 192 | 14 | gov dispatch: start, status, limits, admission, waits, ends, relaunch | keep ? | - | dispatch stays (L2 row 20); L2 B3 rewrites its landing cases when the close guard goes; 14 s |
| `unit/retrieval` | 987 / 585 | 112 | retrieval engine: lexical, semantic, fusion, caps, register ids, reanchor | keep ? | - | core of memory (E2 §5); 112 s, no slow case; reads P-* packages (13) and the register (14) that G1-2 and G4 move: revise |
