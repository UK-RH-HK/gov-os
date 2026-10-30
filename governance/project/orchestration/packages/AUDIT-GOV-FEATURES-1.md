# AUDIT-GOV-FEATURES-1: the Gov OS features used to run its own development

From: a fresh, independent, read-only auditor (`independent-auditor`, DAEO-sdxk), 2026-10-30. Period: 2026-10-16 17:29 (the Wave 2 plan, `7d60dec6`) to 2026-10-30 13:30. Every figure is measured, with its source in §2 to §4; an estimate is marked as one.

## 1. Summary (one page)

**What the evidence shows**
- **The gates mostly caught their own machinery.** Since 10-16, 24 closes were refused or stopped before closing. Counting each cause they carry (a refusal can carry several):
  - **1** named the closing ticket's own work (W2-71's own test);
  - **17** came from faults of the machinery itself or the orchestrator's records (11 of them the only cause);
  - **9** were load or network (2 of them the only cause);
  - **5** found real gaps elsewhere in the Gov OS, but refused an unrelated ticket to do it;
  - **1** was the designed escalation stop.
- **The real defects were found by ordinary practices** the Gov OS also uses:
  - independent reviews: real defects in 12 tickets, most of them classed fails open or loses work (§4.5);
  - the nightly full run: 3;
  - plain test runs;
  - the disk inventory: a launcher regression that left 36 GiB behind.

  The most expensive gates caught **no product defect**: containment, trailers, the ratchet's owner-only entries, probe staleness, checkpoint freshness, escalation, quiet windows and re-pins.
- **Only 3 of the 52 planned tickets have closed through `gov close`:** W2-02, W2-07 and W2-50. Of the 18 tickets it has closed, 15 were added mid-wave, and 12 of those exist to fix the machinery (3 more are borderline).
- **The Charter's cost rule is not measured.** Principle 5 says governance is at most 10–15 % of a task. All 18 close records say "not measured", and every proxy is far above that (see the table below).
- **Standard practice is not on here today.** The git hooks are uninstalled (DEC-712). CI cannot run the tests ("pytest is not on the runner", `ci.yml`, unchanged since 10-07). DEC-830 approved pytest for the runner on 10-19, but its lines ride in W2-43, not yet built. Lifting gates therefore needs §5's minimum set in their place first.

**Top causes of stalls and loops, ranked by measured cost**

| # | Cause | Measured cost |
|---|---|---|
| 1 | Fixing the machinery so closes can pass | 18 added tickets; **168.5 h of lead time (42 %), $283 (45 %)** |
| 2 | The close judges the whole repository, so any red anywhere refuses it | **16 refused full runs (18.8 h)**; **20.5 h of 40.1 h** of queue time produced no close; **521 ticket-hours** waiting; 16 repair tickets |
| 3 | Waiting for the machine: resource gate, pending close, locks | **16.4 h** of lead launch waits in 20 h; 2.8 h of lock waits; 230 min of brief gaps |
| 4 | Every judge fix needs an owner re-pin | 48 h and 16.6 h from fix to pin; **4 d 20 h** with no clean close; W2-58 and W2-63 waited 7.2 and 7.6 days |
| 5 | The owner's load | **187 of 232** register entries exist for the machinery, 113 because something refused or stalled; 58 pings; 29 owner commits |
| 6 | The guard's command-form refusals | **335** denials measured (estimate 6 to 25 h); 103 helper scripts, 40 of them single-use |
| 7 | Pre-close and record checks | 7.5 h of queue gates; estimate 10 to 20 h of record checks |
| — | Review loops before DEC-801 | W2-50: 10 runs, 36.5 h; W2-01: 5 runs. **These found real defects;** DEC-801 already cut the loops |

**Recommendations**

| Feature | Recommendation | Risk of the change | Confidence |
|---|---|---|---|
| `gov close` as a whole | **Replace until whole** with §5: the change's tests on the merged commit, review, nightly | a red outside the change is found the next night | high |
| Containment | **Lift until whole**; the guard's write scope stays | a stray change brought by a merge is seen only in review | high |
| Trailers, traceability | **Replace:** a warning, plus an exit report | some commits lack a ticket link | high |
| Ratchet lists, owner-only | **Replace:** one quarantine list the orchestrator keeps, reported daily | the list grows (shown weekly) | med-high |
| Probe gate | **Keep the review**; lift staleness and form checks | another merge changes reviewed code | high |
| Test map, scoped runs | **Keep**; ACT-TESTMAP-1: **lift** (prose lines only) | a prose edit breaks a reader; nightly finds it | med-high |
| Re-pin ladder | **Lift until whole:** the judge at the integration head; the owner pins releases only | a judge bug passes closes until noticed | med-high |
| Locks, quiet windows, cut-offs | **Replace:** one mutex; timing tests nightly only | load reds until the routing is done | medium |
| Resource gate | **Keep** disk and budgets; a fixed lead cap for memory | an OOM kill | medium |
| Nightly | **Keep**; a red night opens a ticket, holds nothing else | none | high |
| Record checks | **Replace:** a seconds-long check of changed files; heavy checks nightly | a record slip found next night | med-high |
| Guard refusals | **Keep** scope, secrets, held-out, separation, installs; **relax** command forms in own scratch | an unparsed write; sandbox and review catch it | medium |
| Readiness at claim | **Keep** | none | high |
| Brief rules | **Keep**; drop the 90-minute rule with the waits | low | medium |
| Reporting, packages | **Keep** for real decisions; one-line status | low | medium |
| Others (§4.16) | Keep gitleaks and the skip guard; secrets-indexing nightly; **lift** the queue's duplicate gates, escalation, checkpoint and context gates, work-without-a-task (warn) and repair tickets for non-own refusals | low | high |

**What only the owner can decide (§7, §8):**
- Lifting conflicts with Wave 2's exit criterion 1: every ticket closes through a clean `gov close` (WBS §0 rule 1; AR-8).
- It also changes standing rules, among them DEC-862, DEC-891, DEC-933 and DEC-938 (the full list is in §7).
- It touches the Contract's close capabilities as used here (CAP-31, CAP-38, CAP-39, CAP-58, CAP-59) and the guard (CAP-33).
- §8 gives DEC-105's three costed options. **Recommended: (a), apply now, and prove the clean `gov close` once the Gov OS is whole.**

## 2. What was audited, and how

**Period:** from the Wave 2 plan's approval, 2026-10-16 17:29 (`7d60dec6`, DEC-719 to DEC-729), to this audit's start, 2026-10-30 13:30. That is 14 days.

**Scope:** every Gov OS feature used to run this repository's development, as distinct from the features the tickets build. Where a ticket builds a governance feature (the Gov OS's product is governance), the line is drawn by use. Running the gate on this repository is in scope; the ticket that changes the gate is product work, but it is counted as a cost when it exists only because the gate stalled closes here.

**Sources read (reads are open, DEC-820):**
- The pinned judge `~/.local/share/gov-os/pin-5c401220/` (`gov/close/command.py`, `gates.py`, `select.py`), and the orchestrator's `tools/close_queue.sh`, `record_checks.sh`, `gate_check.py`, `disk_gate.sh`, `gate-config.json`, `lead_chain2.sh`, `dor_hand.py`, `skip_gate.py` and `keyword_warn.py`.
- All 37 close-queue logs (`log/close-queue-*/queue.txt`), all 39 close results (`close-*.json`), the five pre-queue close results, and the 16 Wave 2 repair tickets.
- 109 lead returns (`log/W2-*-A5-*.json`), 138 surviving worker results (`~/gov-os-worktrees/*/.gov-runtime/scratch/lead/log/*.json`), the lead chain logs (`log/chain-*.log`), the nightly's `status.txt`, `digest.txt` and `history.jsonl`, `oom-watch.txt`, `drift-2026-w44.txt` and `brief-gaps.md`.
- The 908 commits of `w2/integrate` since `7d60dec6` (trailers, paths, times), `record/w2` (116 commits), and `~/.config/gov-os-notify/pings.log` (58 lines).
- The register, DEC-720 to DEC-951 (232 entries). It was read in full by four read-only helpers, one slice each, and classified against the feature list below. I checked their classification against the cited lines and the raw logs.
- `docs/close/`, `docs/probes/`, `.gov-runtime/iterations/`, `governance/project/test-map.yaml`, `path-map.yaml`, the w2 prompt and its history, `LEAD-w2-common.md`, `docs/plan/WAVE_2_WBS.md` §0, `docs/adr/ADR-0001-threat-model.md`, `.github/workflows/ci.yml` and `lefthook.yml`.
- The orchestrator's own draft state-of-the-Gov-OS annexes (`drafts/state/B-progress.md`, `C-stalls-slips.md`, `E-weekly.md`) were read as claims to verify, not as evidence. Where a figure below matches them, it was re-derived from the raw logs.

**How things were measured:**
- Read-only Python scripts under `/tmp/gov-os-audit-features/` parsed the logs and git. Nothing was run that changes state or competes for the machine.
- Times in queue logs are local: BST until 2026-10-25, GMT after. No single queue run spans the change.
- "Measured" means computed from a named file or commit. "Estimate" means a bounded figure, labelled as such, with its basis.

**Limits:**
- Worker results of removed worktrees are gone, so the guard-denial count is a floor.
- The orchestrator's own session transcripts are not in the logs, so its own guard refusals and minutes are not measured.
- Owner minutes are not measured. The figures used are decision-record commit times, which are an upper bound.
- How each refusal is classified is my reading of its result file and of the entry or package that names its cause. Each is listed in §3.3, so it can be checked.

## 3. The whole picture, measured

### 3.1 Throughput

| Measure | Value | Source |
|---|---|---|
| Wave 2 tickets | 88: 52 planned, 36 added | `.tickets/*.md` with `wbs_id: W2-…` |
| Closed | 20: 18 by `gov close`, W2-01 by owner decision (`tk close`, DEC-757), W2-48 withdrawn (DEC-880) | `docs/close/`, ticket status |
| Planned tickets closed by `gov close` | **3 of 52**: W2-02, W2-07, W2-50 | `docs/close/` |
| Added tickets that exist to make the governance machinery work here | 18 (W2-53, 54, 57, 59, 63, 66 to 78), 16 of them with readable lead returns | ticket titles; §4 |
| Lead sessions | 109 returns, **399.4 h, $631.91** (the CLI's API-price figure). 44 DONE, 49 PACKAGES, 3 unclear, 13 empty or running | `log/W2-*-A5-*.json` |
| Lead time on those 16 machinery tickets | **168.5 h (42 %), $282.98 (45 %)**; W2-58, W2-65 and W2-62 (borderline) add 38.3 h | same, by ticket |
| Commits on `w2/integrate` | 908: **586 records only**, 250 product (`src/`, `tests/`, `template/` …), 69 merges, 3 other | `git log 7d60dec6..w2/integrate` |
| Records-only commits by area | `.tickets/` 194, `docs/checkpoints/` 170, `docs/plan/` 97, register 93, `orchestration/` 79, prompts 52, probes 28 | same |
| Role of the commits | orchestrator 570, independent test designer 155, engineer 128, **owner 29**, none 22 | trailers |

### 3.2 The close machinery

| Measure | Value | Source |
|---|---|---|
| `gov close` runs with a verdict | 38: **18 passed (47 %)**, 16 refused after a full run, 4 refused at once (TREE_NOT_COMMITTED ×2, STORE_STALE, ESCALATION_BLOCKED) | queue logs; `close-*.json` |
| Queue gate stops before a close | 4 (`gov check` ×3, trailers ×1), plus 1 stopped by the orchestrator for load | `queue.txt` |
| Close-queue wall time | **40.1 h** over 37 queue runs, 2026-10-20 to 2026-10-30 | `queue.txt`, first to last line |
| Slots that produced no close | **20.5 h** (51 % of queue time) | same |
| Pre-close gate passes in the queue | 37, **7.5 h**, mean 12.2 min each (rebuild, keyword warning, collection, record suites, network, `gov check`, trailers, work without a task, tree) | same |
| Passing closes | 9 full, mean **72.5 min**; 9 scoped, mean **12.0 min** (tests about 5 min of it) | same; close records |
| Refused full runs | 16, **18.8 h** of close time (19.7 h with the 2026-10-18 scratch-merge sweep) | queue logs; `W2-01-close.json`, `close-DAEO-7rr2*.json` |
| Ticket-hours from first refusal or gate stop to a clean close | **521 h** over 9 tickets: W2-63 182 h, W2-58 174 h, W2-53 62 h, W2-54 35 h, W2-02 18 h, W2-62 18 h, W2-70 18 h, W2-50 11 h, W2-66 4 h. W2-71, W2-57 and W2-03 were refused today and are still open | queue logs |
| Longest stretch with no clean close | **4 d 19 h 55 min**, 2026-10-22 22:17 to 2026-10-27 17:12 | `close-queue-20261022-2044`, `-20261027-1546` |
| Repair tickets opened by refused closes | 16 in Wave 2. 15 were for causes outside the closing ticket's product code; DAEO-sg6x is the exception (W2-71's own test) | `log/repair-tickets/`, `.tickets/` |
| Verification-lock waits (since 2026-10-29) | **2.8 h** over 3 queue runs; quiet-window waits 0.5 h | `queue.txt` |

### 3.3 Why closes were refused: all 24 refusals and gate stops, classified

Kinds: **A** = a defect in the closing ticket's own work; **B** = a real defect elsewhere in the Gov OS, found by the gate; **C** = a fault of the governance machinery or of the orchestrator's own records or tools (a gate gap, a stale list, a slip); **D** = load, network or environment (a false red); **E** = a designed stop.

| # | When | Ticket | What refused | Kinds | Source |
|---|---|---|---|---|---|
| 1 | 10-17 | W2-01 | probe invalid after the orchestrator's ticket-file edit; W1-42's two known reds; W1-05 p95 under load; stale checkpoint; DEC-750 not yet in the store | C, D | `log/W2-01-close.json`; DEC-757 |
| 2 | 10-18 | W2-53 | `gov check`: context-reproducibility over its limit, with an unstable order; core-schema did not know the audit-report type; a Wave 1 commit without `Implements:`; stale checkpoint | B, C | `log/close-DAEO-7rr2.json`; DEC-768 |
| 3 | 10-19 | W2-53 | STORE_STALE: no rebuild before the close | C | `close-DAEO-7rr2-2.json` |
| 4 | 10-19 | W2-53 | W1-30 time-limit case at load about 25 | D | `close-DAEO-7rr2-3.json` |
| 5 | 10-20 | W2-53 | stale checkpoint; context red from a superseded DEC-636 cited in W2-63's ticket; `tests/unit/secrets` shadowing the standard library; load 28.87 | B, C, D | `close-queue-2026-10-20`; DEC-867 |
| 6 | 10-20 | W2-53 | ESCALATION_BLOCKED after three refusals | E | `close-queue-run2`; DEC-870 |
| 7 | 10-20 | W2-54 | TREE_NOT_COMMITTED: an uncommitted orchestrator package | C | `close-queue-20261020-1108` |
| 8 | 10-20 | W2-53 | the queue's own checkpoint commits lacked `Implements:`; W1-38 under load | C, D | `-20261020-1212`; DEC-871 |
| 9 | 10-20 (stop) | W2-54 | `gov check`: core-schema did not know the `close` type that `gov close` itself writes | B | `-20261020-1422/check-DAEO-0rfi.json`; DEC-872 |
| 10 | 10-21 | W2-02 | TREE_NOT_COMMITTED: the record sync copied cache stores | C | `-20261021-0108` |
| 11 | 10-21 | W2-02 | W1-08 red from the sync's copies; W1-07 `doctor` under load | C, D | `-20261021-1401`; DEC-885 |
| 12 | 10-21 | W2-02 | W1-07 `doctor` under load; fixture copies racing git gc as the record grew | D (C) | `-20261021-1550`; P-W2-02-C3 |
| 13 | 10-21 (stop) | W2-62 | claim commit without `Implements:` (the orchestrator's) | C | `-20261021-1924`; DEC-891 |
| 14 | 10-21 | W2-63 | NO_ACCEPTANCE_TESTS: the close did not read `acceptance_tests.path`; W1-38 under load; W1-46 network | C, D | `-20261021-2241`; DEC-892 |
| 15 | 10-22 | W2-50 | PROBE_INVALID: W2-58's merge touched W2-50's reviewed files. The re-probe passed, the code was unchanged. Also a ratchet entry that did not name its test | C | `-20261022-0952`; DEC-894 |
| 16 | 10-22 | W2-58 | WORK_WITHOUT_TASK: 7 decision-record and owner ratchet commits | C | `-20261022-1153`; DEC-896 |
| 17 | 10-22 (stop) | W2-62 | `gov check`: the secrets check's chance match in a derived store | B | `-20261022-1335/check-DAEO-juee.json`; DEC-897 |
| 18 | 10-26 | W2-70 | 9 reds from the first re-pin's settings regeneration | C | `-20261026-2157`; DEC-925 |
| 19 | 10-27 (stop) | W2-66 | `gov check`: `Implements:` naming a role (the brief builder's slot) | C | `-20261027-1546`; DEC-927 |
| 20 | 10-27 | W2-66 | W2-66's own test map test refused an ACT `.patch` committed under `orchestration/` | C | `-20261027-1823` |
| 21 | 10-28 | W2-58 | W2-54's green-here fixture ran `gov check` past the 900 s per-test limit under load | B, D | `-20261028-2007`; DEC-937 |
| 22 | 10-30 | W2-71 | **W2-71's own premise test, which can pass only on its branch**; W2-54's time limit under load | **A**, D | `-20261030-0007`; DAEO-sg6x |
| 23 | 10-30 | W2-57 | the same W2-71 test, now in the main tree; queued after #22 (drift log) | C | `-20261030-0242`; `drift-2026-w44.txt` line 3 |
| 24 | 10-30 | W2-03 | CONTAINMENT_FINDING: a merge with two merge bases is read as about 350 own files; its real own change is 11 files. All tests passed | C | `-20261030-1031`; `drafts/P-W2-03-CONTAINMENT.md` |

**Counts:**
- A: **1**. B: 5. C: **17**, 11 of them the sole cause. D: 9, 2 of them the sole cause. E: 1.
- **One refusal in 24 named the closing ticket's own work.** That was a test-design defect visible only after the merge, and any post-merge test run finds it.
- The five B refusals found real gaps in the existing Gov OS: two record types the schema did not know, the context check's time and order, a test package named like a standard-library module, and the secrets check's chance match. Dog-fooding found these. As a gate, though, each one refused an unrelated ticket after a full run.

### 3.4 The owner's load

| Measure | Value | Source |
|---|---|---|
| Register entries | **232** in 14 days, DEC-720 to DEC-951 (16.6 a day). Classified in §3.5 | register |
| Owner pings | **58**: 28 P1, 16 ACT, 11 P2, 2 COMMIT, 1 operator test (the 2 test pings are among these). **About 45 of the 56 real pings concern the machinery:** a refused close, a ratchet or history entry, a re-pin, a containment, trailer or probe finding, the nightly or the test map. Read line by line | `pings.log` |
| `Role: owner` commits | 29: 14 change the path map's ratchet or history lists, 3 are pins or settings, and the rest are batches of owner decisions | `git log` |
| ACTs | 8 (REPIN-1, REPIN-2, REPIN-3 pending, P-TRACE-IMPL-1, W2-57-LS-1, NIGHTLY-1, RUNS-SWEEP-1, PUSHOVER-1), plus TESTMAP-1 drafted and the owner commits A, B and C | packages, drafts |
| Rules the sessions carry | the w2 prompt grew from **26,160 to 80,599 bytes** (53 revisions, v3.44); `LEAD-w2-common.md` has had 26 revisions; `RULES-IN-FORCE.md` lists 53 standing decisions | `git log`; drafts |

### 3.5 The register: why each of DEC-720 to DEC-951 exists

**How the entries were classified:**
- Four read-only helpers read the 232 entries in full, one slice each, and gave every entry one primary reason:
  - **R:** a feature refused, stalled or looped;
  - **O:** the entry sets up or operates a feature;
  - **P:** a product or plan decision.
- I checked the borderline calls against the cited lines.
- Independent review rounds are counted under "reviews and other machinery".

**The split:**
- **R: 113 (49 %); O: 74 (32 %); P: 45 (19 %).**
- **4 in 5 register entries in Wave 2 exist because of the governance machinery** (187 of 232).
- Who decided: the owner 188, delegated 43, other 1.

| Feature (main reason) | R | O | Total | Entries |
|---|---|---|---|---|
| `gov close` and its generic gates | 25 | 3 | **28** | whole: 775, 867, 868. Regression run: 726, 782, 784, 813, 823, 864, 865, 874, 883, 885, 937. `gov check`: 768, 773, 781, 805, 844, 872, 908. Record suites: 882. Work without a task: 877, 896, 923, 924. Escalation: 870. Class: 892 |
| Containment and allowed paths | 9 | 1 | **10** | 746, 747, 753, 755, 777, 800, 814, 863, 918, 921 |
| Trailers and traceability | 4 | 2 | **6** | 724, 871, 891, 912, 927, 928 |
| Ratchet lists | 6 | 4 | **10** | 734, 757, 760, 762, 766, 862, 886, 900, 906, 931 |
| Probe gate | 2 | 2 | **4** | 733, 763, 790, 894 |
| Test map and scoped selection (with W2-48's withdrawn cache) | 3 | 7 | **10** | 843, 852, 869, 876, 880, 881, 889, 890, 903, 929 |
| Re-pin ladder | 1 | 8 | **9** | 822, 835, 879, 884, 899, 922, 925, 932, 935 |
| Locks, quiet windows, scheduling | 3 | 1 | **4** | 737, 780, 806, 888 |
| Resource gate | 2 | 7 | **9** | 742, 776, 847, 898, 902, 904, 905, 942, 947 |
| Nightly | 2 | 3 | **5** | 933, 934, 938, 939, 951 |
| Record checks | 5 | 0 | **5** | 730, 744, 893, 895, 926 |
| Guard's refusals and rules | 12 | 7 | **19** | 728, 738, 743, 756, 758, 759, 764, 765, 769, 774, 778, 820, 821, 827, 845, 849, 857, 873, 907 |
| Readiness at claim | 0 | 0 | **0** | DEC-944 founds it, as part of a plan decision |
| Briefs and launches | 8 | 8 | **16** | 731, 732, 752, 786, 789, 793, 799, 824, 826, 836, 838, 839, 840, 854, 919, 943 |
| Reporting and packages | 6 | 16 | **22** | 787, 788, 791, 809, 818, 819, 825, 842, 846, 850, 851, 855, 856, 858, 861, 866, 878, 887, 936, 945, 948, 949 |
| Reviews and other machinery | 25 | 5 | **30** | Review rounds and threat-model rules: 739, 750, 751, 754, 761, 767, 770, 772, 779, 785, 801, 802, 803, 804, 807, 808, 810, 812, 817, 909, 910, 916. Secrets: 853, 897, 911. Skip guard: 915. Others: 792, 794, 830, 848 |
| Product and plan | — | — | **45** | |

**Reading the table:**
- **Most R entries cluster around refused closes and re-pins.** 10-17 to 10-20 (W2-01's and W2-53's closes and the review loops), 10-21 to 10-22 (the queue's first week) and 10-24 to 10-28 (re-pin 1 and its fallout).
- **The review rounds before DEC-801** (10-19) are 22 entries. They also record most of the real product defects found in Wave 2 (§4.5).

**Calls that could move** (between two features, or between R and O):
- DEC-721, 723, 730, 744, 746, 747, 755, 757, 762, 782, 798;
- DEC-801 to 803, 805, 822, 840, 861;
- DEC-894, 899, 912;
- DEC-920, 923 to 925, 929, 938, 940, 944, 947, 950.

At worst, recoding all 24 borderline governance entries as product leaves **163 of 232 (70 %)** existing for the machinery.

## 4. Feature by feature

Each feature has the same five parts:
1. **Protects:** what it protects against, and whether that protection is needed while the Gov OS is still being built. This is judged by ADR-0001's threat model (honest mistakes and plausible accidents in ordinary work) and by JUDGEMENT.md's two questions: can an honest agent hit this in ordinary work, and does it fail open or lose work?
2. **Cost:** measured, each figure with its source. An estimate is labelled as one.
3. **Caught:** real faults it caught, split three ways: a product defect, a fault of the machinery itself, or a false refusal.
4. **Standard practice:** what could replace it now.
5. **Recommendation:** keep, lift now, lift until the Gov OS is whole, or replace. Each comes with the risk of the change and my confidence.

"Owner decisions" counts the register entries whose main reason is the feature, as the four helpers classified them and I checked: R = exists because it refused, stalled or looped; O = operates it.

### 4.1 `gov close` as a whole, and each of its gates

**The pinned code.** `~/.local/bin/gov`'s first line names `pin-5c401220`. Its `gov/close/command.py:run` asks, in this order:
- **before anything:** escalation; tree is HEAD; store is of HEAD; trailers base.
- **the commit gates, uncounted (DEC-868, DEC-896):** probe (FULL tickets only); trailers; accepted history; work without a task; ratchet lists readable.
- **the pre-close gate, uncounted:** collection; `gov check`; checkpoint freshness.
- **then:** disk floors; containment; specification or evidence class; acceptance run; regression run (full or path-scoped by the test map, parallel then serial, a per-test limit of 900 s); reds judged by the ratchet lists, with a load-sensitive red re-run alone; context packet.
- **finally:** the close record, a checkpoint and `tk close`. A refusal is counted, and the third counted refusal escalates. Every refusal, counted or not, opens a repair ticket.

**The queue.** `tools/close_queue.sh` wraps each close in its own gates:
- **before:** the disk gate; (c) a fresh checkpoint, committed; a full `gov rebuild` under the rebuild lock; row W2-L423's keyword warning; (a) collection; (f) four record-reading suites; (g) network; (b) `gov check`; (e) trailers, with `Implements:` ids checked against the register; (h) work without a task; (d) the tree as the close reads it.
- **after:** the skip guard, then gitleaks on the close's outputs, then the output commit.

**The whole close.**
- **Protects:** a ticket being called done while its tests, its records or the repository are not green. This is needed, and it is the one thing every ticket must show.
- **Cost:** 40.1 h of queue time, of which 20.5 h produced no close (§3.2). 18.8 h of refused full runs. 521 ticket-hours waiting from first refusal to clean close. 16 repair tickets. 24 refusals and gate stops (§3.3). A full close takes 72.5 min plus a 12.2 min gate; a scoped close takes 12.0 min plus the same 12.2 min gate.
- **Owner decisions:** **28** entries have the close or one of its generic gates as main reason, **25 of them because it refused or stalled** (§3.5). Each gate's own are below.
- **Caught:** 1 own-work defect (A), 5 real defects elsewhere (B), 17 machinery faults (C), 9 false reds (D) (§3.3).
- **The structural cause:** the close judges the whole repository at the moment it runs: every test, every governance check, every record. It does not judge the ticket's change. So any red anywhere refuses whichever ticket is closing. 23 of 24 refusals did not concern the closing ticket's work.
- **Standard practice:** a merge gate that judges the change. Run the ticket's tests and the tests its change can reach, on the merged commit, in a clean worktree. Add an independent review, and a nightly full run whose red opens a ticket against the change that caused it, not a hold on everyone else's closes.
- **Recommendation:** replace with the minimum practices of §5, until the Gov OS is whole.
  - Risk: a red outside the change is found the next night, not at close.
  - Confidence: high.

**Each gate.** "Stops" counts §3.3's refusals and gate stops in which the gate took part.

| Gate (pinned code, or the queue's letter) | Protects (needed now?) | Measured cost | Caught | Standard practice | Recommendation; risk; confidence |
|---|---|---|---|---|---|
| Escalation at 3 counted refusals (A6) | Endless repair loops (yes in principle) | 1 block (W2-53, 10-20 11:07). P-W2-53, 2 pings, DEC-870, an owner `Role: owner` commit; about 1 h | 0 real. All three counted refusals before it were C or D | A rule: two refusals for the same non-own cause go to the owner as a package (WBS §0 rule 1 already says so) | **Lift until whole**, keeping the rule. Risk: none beyond the rule. High |
| Tree is HEAD (TREE_NOT_COMMITTED) and queue gate (d) | Measuring a tree other than the commit recorded (yes) | 2 refusals (#7, #10), both orchestrator files; seconds per run | 0 product; 2 slips caught (C) | Run in a clean worktree or clone of the merge commit, as CI does | **Keep**, as a clean-checkout run. Risk: none. High |
| Store is of HEAD (STORE_STALE), with the full rebuild before every close | The context packet built from current records (needed only for the context gate) | 1 refusal (#3). The rebuild: 4 to 6 min per close (`queue.txt`); once 6 h 39 min on 10-29, cause not found (C-stalls S-11) | 0 | None needed once the context gate goes | **Lift until whole**, with the context gate. Rebuild only for retrieval. Risk: none. High |
| Probe (FULL tickets) | See §4.5 | | | | §4.5 |
| Trailers, and queue gate (e) | See §4.3 | | | | §4.3 |
| Accepted history; ratchet lists readable | See §4.4 | | | | §4.4 |
| Work without a task, and queue gate (h) | Unreviewed work slipping into a ticket's range (in ordinary work: rarely) | 1 refusal (W2-58 #16: 70.7 min), P-W2-58-C1, DEC-877, DEC-896, DEC-923, DEC-924, W2-07's rule for decision records, an owner accepted-history commit (`048f5758`). W2-58 then waited 7 days | 0 product. The 7 commits were the orchestrator's and the owner's own records | Review the merge diff; a lint that every commit names a ticket | **Lift until whole**, keeping it as a warning. Risk: a stray commit goes unnoticed until review. High |
| Collection in one process, and queue gate (a) | A suite that cannot even be collected (yes) | 6 to 8 s per run; 0 stops in 37 queue passes | 1 real before the gate existed: `tests/unit/secrets` shadowing the standard library (#5) | Any test run collects | **Keep** (cheap). High |
| `gov check`, in the close and in queue gate (b) | The records' invariants: schemas, path map, traceability, secrets indexing, context reproducibility (partly) | Runs twice per close, about 5 to 6 min each (`queue.txt`, `PERF-REPORT.md`). 1 refusal (#2) and 3 stops (#9, #17, #19). Main reason of DEC-768, 773, 781, 805, 844, 872, 908; DEC-897 and DEC-927 beside them | **3 B:** record types unknown to the schema (#2, #9); the context check's time and order (#2). 1 B false positive (the secrets chance match, #17). 1 C (#19) | Run `gov check` nightly and on record-changing commits as a test, not as a per-close gate | **Replace**: nightly, plus a file-scoped record check (§4.11). Risk: a record invariant breaks for up to a day. Medium-high |
| Checkpoint freshness (watchdog) | Resumability of a session (useful at handover, not at close) | In 4 refusals (#1, #2, #5, the sweep), never alone. Forces a checkpoint commit before every close: **101 checkpoint-only orchestrator commits since 10-20.** One of them lacked `Implements:` and refused W2-53 (#8) | 0 | A checkpoint at every handover (DEC-837), as a session habit | **Lift** as a close gate; keep the habit. Risk: none. High |
| Disk floors (DEC-898) and the disk gate | Running out of disk or inodes mid-run (yes: an auditor hit ENOSPC at 98 % inodes, DEC-898) | Seconds; 0 refusals at close | Its weekly inventory found a real launcher regression: 4.1 million inodes and 36 GiB left behind (row W2-M405, DEC-902) | `df` alerting | **Keep.** Risk: none. High |
| Containment | See §4.2 | | | | §4.2 |
| Class, evidence and NO_ACCEPTANCE_TESTS | A ticket closed without its tests or evidence (yes) | 1 refusal (#14, a gap in the close: it did not read `acceptance_tests.path`). W2-63 then waited 7.6 days for W2-07 and a re-pin | 0 product; 1 machinery gap | A checklist: the ticket names its tests or evidence, and they exist | **Keep the rule**, as a quick check. High |
| Acceptance run | The ticket's own KPIs (yes: the core) | Seconds to 16 min (W2-69's suite 962 s) | Every ticket's own tests | The same | **Keep.** High |
| Regression run, full or scoped | Regressions elsewhere (yes) | Full 66 to 79 min; scoped about 5 min of tests. Reds in the run took part in 12 of 16 refused full runs, mostly load reds. Main reason of 11 entries: DEC-726, 782, 784, 813, 823, 864, 865, 874, 883, 885, 937 | #5 (secrets package), #21 (fixture design), #22 (W2-71's premise test) | Affected tests at merge; full suite nightly | **Keep, scoped**, with the full run nightly (§4.6, §4.10). Medium-high |
| Reds judged by the ratchet lists | See §4.4 | | | | §4.4 |
| Context packet (CONTEXT_FAILED) | That a ticket's context can be built from current records | In #1 (DEC-750 not yet in the store). The same context machinery turned W2-54's test red in #5 (a superseded decision cited) | 0 product | The context is a session aid, not a merge criterion | **Lift until whole.** Risk: none for code. High |
| Queue gate (f), four record-reading suites | The orchestrator's record commits turning tests red | 30 passes × 92 to 126 s = **about 0.9 h**; 0 stops | 0 at the gate; the same suites run in `record_checks.sh` | Run them before record commits only | **Lift from the queue** (it duplicates §4.11). High |
| Queue gate (g), network | Spending a close on a network outage (W2-63's W1-46 red) | 2 to 3 s; 0 stops in 25 runs | 0 | Live-network tests run nightly only (W2-57 routes them) | **Keep** while cheap, or drop with routing. High |
| Queue gates (d), (e), (h) since re-pin 2 | Already asked by the pinned close before any test, uncounted (DEC-896, W2-07) | Duplicates of the close's own commit gates | 0 since 10-28 | | **Lift the duplicates.** High |
| Skip guard (DEC-899 item 7) | A test skipping silently (rulesync absent) and hiding a red (yes) | Under 1 s per close; 0 stops in 13 closes. One tool bug (T5) was caught before use | 0 | `pytest -rs` and failing on unexpected skips | **Keep** until W2-57 lands. High |
| gitleaks on the close's outputs | A secret committed (yes) | Seconds | 0 | Standard | **Keep.** High |
| Repair ticket on every refusal | Tracking a refusal's fix | 16 opened. 15 are for causes outside the ticket; 3 are still open | | An issue only when the ticket's own work failed | **Lift** for uncounted and non-own refusals. Medium |

### 4.2 Containment (merge-base attribution, DEC-912, DEC-918)

- **Protects:** a ticket's commits changing paths outside its `allowed_paths`, a merge-back's brought-in changes counted as the ticket's own, or the reverse. **Needed now?** Partly. The honest mistake (an agent editing another ticket's file) is already stopped at edit time by the guard's write scope (DEC-820). The close-time judge is a second check on the same thing.
- **Cost:**
  - **W2-03's refused close (#24):** a 71.6 min full run with every test green, a 14 min gate and a 66 min wait for the lock. Then package P-W2-03-CONTAINMENT and an owner decision, still open. W2-03 is the base of the memory chain: W2-55 and W2-04 wait on it.
  - **P-W2-L437-A and -B, DEC-918:** W2-66's and W2-65's closes would have been refused on their DEC-912 merge-backs. A new FULL ticket, W2-72, took 7.8 h of lead time ($14.73), and re-pin 1 moved back about 5 h (DEC-918 item 3).
  - **P-W2-65-M1, DEC-921:** the merge order made a criss-cross history that containment refuses. **13 h 53 min** passed from `e77ffb54` (10-25 04:59) to the replacement merge `6a4696eb` (18:52), and it needed the owner's yes to replace two unpushed merges.
  - **Owner decisions** (scope and containment as main reason), **10:** DEC-746, 747, 753, 755, 777, 800, 814, 863 (allowed-path widenings after reds outside a ticket's paths); DEC-918, DEC-921. DEC-912 sits beside them, and P-W2-03-CONTAINMENT is still open.
- **Caught:**
  - **No real out-of-scope change** was caught by the close's containment gate in Wave 2. Its one refusal (#24) was false: the merge's real own change, measured against the integration parent, is 11 files, all W2-03's (`git diff --stat b23bf1ac^2 b23bf1ac`, package §2).
  - The live hook's flags are not blocking: 101 since 2026-10-03, 31 of them "change outside allowed paths" (`.gov-runtime/findings.jsonl`). They were not adjudicated.
- **Standard practice:** review the branch's own change with a three-dot diff (for example `git diff w2/integrate...w2/W2-03`), which ignores what merge-backs bring in. Keep the guard's write scope at edit time.
- **Recommendation: lift as a close gate until the Gov OS is whole.**
  - Keep the guard's write scope and the live hook's flags, as an advisory line in the close record.
  - On W2-03: the package's option (a) follows from this.
  - Risk: an out-of-scope change that came in by a merge, not by an edit, is seen only in review. Low, because the guard refuses the edit itself.
  - Confidence: high.

### 4.3 Trailers and traceability (Task, Implements, Role; Implements ids against the register, DEC-927; `trailer_gate.py`)

- **Protects:** every commit traceable to a ticket, a requirement and a role. This is the F-M3/AR-8 proof and CAP-38.b's product traceability. **Needed now?** As a record, yes. As a gate that refuses a close, no: a missing trailer fails neither open nor loses work.
- **Cost:**
  - **One refused full run:** W2-53 #8, 79.2 min, refused on the queue's own checkpoint commits. **Two gate stops:** #13, 11.1 min; #19, 10.8 min. Part of #2.
  - **`accepted_history` now holds 47 entries,** most of them to forgive trailer slips:
    - DEC-871: three of the queue's checkpoint commits;
    - DEC-891: W2-62's claim commit;
    - DEC-924: `611955fa`;
    - DEC-927: **41 entries** for commits whose `Implements:` named a role, because the brief builder's IMPL slot was filled with one;
    - DEC-764 to DEC-772: `93bcb247`.
  - **Packages:** P-W2-55, P-W2-62-H, P-TRACE-IMPL-1, P-W2-07-DR2. **ACT:** ACT-P-TRACE-IMPL-1. **Owner commits:** `e95d3520`, `048f5758`.
  - Leads must run `trailer_gate.py` before returning (DEC-927 item 2).
  - **Owner decisions** with this as main reason, **6:** DEC-724, 871, 891, 912, 927, 928.
- **Caught:** **no product defect.** Four slips, all in the machinery's own commits and tools: the queue's checkpoint commits, the orchestrator's claim commit, the brief builder's slot (39 commits on `w2/integrate` and 2 on W2-57's branch), and one Wave 1 claim commit.
- **Standard practice:** a commit-message lint that warns. A traceability report generated at wave exit from `git log`.
- **Recommendation: replace with a warning and an exit report until the Gov OS is whole.**
  - Stop adding accepted-history entries for slips.
  - Risk: some commits carry no ticket link, a gap the exit report names. Low.
  - Confidence: high.
  - The owner must decide this one: it touches AR-8/F-M3 (DEC-718) and CAP-38.b (the Contract).

### 4.4 The ratchet lists (`accepted_reds`, `load_sensitive`, `accepted_history`, `acceptance_exemptions`; owner-only `Role: owner` commits, DEC-862, DEC-891)

- **Protects:** a new red hidden among known reds, and the exceptions growing silently. **Needed now?** The second, yes, as a count. Owner-only commits for each entry, no: the risk is honest growth of the list, not an adversary.
- **Cost:**
  - **Today's lists:** `accepted_reds` 0, `load_sensitive` 24, `accepted_history` 47, `acceptance_exemptions` 1 (`path-map.yaml`).
  - The path map changed 23 times in Wave 2, **14 of them in owner commits.**
  - **ACTs and owner commits:** DEC-886, DEC-892, the owner commits A, B and C, ACT-W2-57-LS-1, ACT-W2-57-LS-2 (pending). There is also `validate_entry.py`.
  - **Slips this process caused:**
    - The owner commit B (`c9a08678`) was checked without a full run, and W1-01's history case stayed red on `w2/integrate` for **12 h 19 min.** Every lead's full run was red meanwhile (DEC-906; C-stalls S3).
    - The DEC-892 entry did not name its test file, so the ratchet refused it at W2-50's close (#15).
    - **Three of the seven commits that refused W2-58 (#16, 70.7 min, then 7 days' wait) were the owner's own ratchet commits** (`49c24ac9`, `cf8219a8`, `8dfd54e9`). They carry no `Task:` and change `path-map.yaml`, which lies in W2-58's paths.
  - **Owner decisions** with this as main reason, **10:** DEC-734, 757, 760, 762, 766, 862, 886, 900, 906, 931.
- **Caught:** the lists caught nothing themselves. The rule "an unlisted red refuses" is how reds refused closes: **11 of 16 refused full runs** carry "is red and accepted_reds does not list it". The lists began on 10-17, after W2-01's close. Of those reds, one was the closing ticket's own (W2-71), and the rest were load, environment or the orchestrator's changes (§3.3).
- **Standard practice:** a flaky-test quarantine file, changed through ordinary review with a reason. Timing-sensitive tests run nightly; DEC-951 item 3 already routes W2-54's two cases there.
- **Recommendation: replace until the Gov OS is whole.**
  - The orchestrator keeps one quarantine list, each entry with its reason and test.
  - Additions and removals are reported in the daily digest, and the list's size each week.
  - No owner-only commits.
  - Risk: the list grows; the weekly number shows it. Low to medium.
  - Confidence: medium-high.
  - The owner must decide: it changes DEC-757, DEC-766, DEC-862 (a), DEC-891 and DEC-906 item 1, which are standing rules.

### 4.5 The probe gate (FULL tickets' review records, staleness, `probe_impact.py`, DEC-895)

**What it is:** the gate checks that a FULL ticket's committed probe record:
- is by a reviewer who is not the implementer and wrote nothing;
- was committed by the orchestrator role;
- names a full commit id;
- passed, or has every finding accepted by an owner decision;
- and that nothing touched the ticket's paths after the probed commit, other merges included.

**Whether it is needed now:**
- **The independent review is needed:** it found real defects (below).
- **The gate's staleness rule is not needed:** it re-reviewed unchanged code.

**Cost:**
- Refusals: #1 (W2-01, part) and #15 (W2-50: 71.8 min, then run 9 for a fresh probe, 310 min, $5.13).
- **Four staleness re-probes, all of them pass:** `PR-DAEO-rmbe-reprobe-1`, `PR-DAEO-cy5o-reprobe-1`, `PR-DAEO-cy5o-reprobe-2`, `PR-DAEO-kl5e-run-9` (`docs/probes/`).
- W2-67 has been held since 10-25 on a stale probe (CHECKPOINT §Plan in force).
- A `probe_impact.py` run after every merge.
- **Owner decisions:**
  - for the gate: DEC-733, 763, 790, 894, plus DEC-895 (with §4.11);
  - for the review rounds and the threat-model rules, **22:** DEC-739, 750, 751, 754, 761, 767, 770, 772, 779, 785, 801, 802, 803, 804, 807, 808, 810, 812, 817, 909, 910, 916.
  - These are the loops of W2-01 (5 runs), W2-50 (**10 runs, 36.5 h, $46.40**) and W2-16. DEC-801 to DEC-803 (judge by ADR-0001's threat model; no extra round) ended most of them.

**Caught:**
- **The reviews themselves found real product defects:**
  - W2-01: a merge-back could drop probed code and `gov close` still passed (DEC-739, DEC-750, DEC-754; fails open).
  - W2-50: the guard wrote through links and misread option values (DEC-751, 758, 764, 765, 774; some older guard code).
  - W2-16: `gov release --lock-from` turned DRIFT into MATCH (DEC-761), and role spoofing let an auditor write a release (DEC-772).
  - W2-67: the clean-up removed a live run's folder (loses work).
  - W2-69: key blocks over about 4 KB, then over 9,216 bytes, were missed (fails open; the new code was worse than the old, DEC-909).
  - W2-66: a renamed map target selected nothing (fails open, DEC-912).
  - W2-60a: worktree launches skip the main checkout's local settings (fails open, DEC-951 item 4).
  - W2-05: a declared check got no inherited `GIT_INDEX_FILE`, "what happened for real in Wave 1" (DEC-804, DEC-807).
  - W2-37: two fail-open findings, fixed in its resume (DEC-812).
  - W2-52: A10 did not re-check A8's proof, and A7 checked positions, not content (DEC-810).
  - W2-59: a guard program that cannot run let the call through (R2-D1, fails open; fixed by W2-65, DEC-879).
  - W2-58: findings of its reviews, fixed or rowed (DEC-880, DEC-882).
  - In all, **12 tickets.**
- **The gate's staleness and form checks found no defect:** 4 re-probes passed. W2-01's PROBE_INVALID was the orchestrator's ticket-file edit, and W2-50's was another ticket's merge (machinery, C).

**Standard practice:** independent review of the change before merge. Re-review only when a later merge had to resolve conflicts in reviewed files (GitHub's "dismiss stale approvals" covers the branch's own new commits, not other merges).

**Recommendation:**
- **Keep the independent review** for FULL tickets, at merge time, judged by JUDGEMENT.md's two questions.
- **Lift until whole** the close-time gate's staleness-after-other-merges rule and the record-form checks.
- Risk: a later merge changes reviewed code without a new review. Tests and the nightly cover its behaviour. Low.
- Confidence: high.

### 4.6 The test map and scoped selection (`test-map.yaml`, W2-66), and ACT-TESTMAP-1

- **Protects:** close time, without skipping the tests a change can reach. Shared core, an unplaced path, an unreadable map or an unknown base all widen the run to full. **Needed now?** Yes. It is the largest time saver measured.
- **Benefit, measured:** a scoped close takes **12.0 min, a full one 72.5 min** (9 of each, §3.2).
- **Cost:**
  - W2-66 took 13.1 h of lead time ($29.17); W2-78 is still running.
  - W2-66's live test refused a close once (#20, 69.8 min).
  - Governance edits widen closes to full (DEC-929). W2-58's 10-28 close ran full on SHARED_CORE.
  - **Owner decisions** with this as main reason, **10:** DEC-843, 852, 869, 876 and 880 (W2-48's cache, withdrawn), and DEC-881, 889, 890, 903, 929. Also ACT-TESTMAP-1 and P-SCOPE-RECORDS-1.
- **Caught:** no product defect. Twice the live test caught a record-only list that would hide something:
  - an ACT `.patch` under `orchestration/` (#20);
  - ACT-TESTMAP-1.
- **ACT-TESTMAP-1, in particular:**
  - **What the refusal protected.** The live test (`tests/acceptance/W2-66/test_w2_66_live_test_map.py`) holds two rules:
    - **record-only places only DEC-891's places** (lines 237–240). `governance/project/briefs/` and `prompts/` are not among them.
    - **record-only hides no code** (lines 243–247). `governance/project/orchestration/nightly/` holds 10 scripts.
  - **What those rules protect here:**
    - **No pytest test reads this repository's prompts or briefs.** The four tests that name such paths use fixture copies: W2-62's suite, `tests/unit/hooks/test_w29_hooks.py`, and W2-07's decision-record test. The tree-scanning readers, such as W1-27's doctor and W1-08's path map, are already in `record_reading` and run on every scoped close.
    - **No pytest test runs the nightly scripts either.** Only `test_nightly.sh` does, by hand, and a full close does not run it.
    - So the refusal protected the **owner's DEC-891 list** (who may call a path a record). It protected no test of the product.
    - One indirect point: the nightly scripts write the green-night records that the selection uses as its base (`select.base`). A broken nightly script could narrow later scoped closes. No close-time test guards that today, either way.
  - **Lifting costs:**
    - an owner widening of DEC-891's places;
    - a test-designer revision of the live test (`Rewrite-Reason:`). Without it, the live test is red in the main tree and refuses every close;
    - the nightly scripts going unselected by closes, which changes nothing measurable.
  - **Keeping costs:** every close and every lead's DEC-952 verification runs full until W2-78 lands. That is about **+60 min a close** (72.5 against 12.0 min). The five closes now waiting (W2-71, W2-77, W2-57, W2-03, W2-26) come to about 5 h more machine time, plus every lead's own full verification.
- **Standard practice:** select the affected tests (a path-to-suite map, as built), with the full suite every night as the backstop.
- **Recommendation: keep scoped selection.**
  - **ACT-TESTMAP-1: lift it.**
    - Commit its two prose lines (`briefs/**.md`, `prompts/**.md`).
    - Leave `orchestration/nightly/**` unplaced, since it is code and rarely changes (frozen, DEC-946).
    - Widen DEC-891's places by those two, and have the live test revised to match.
  - Risk: a prose edit that breaks a tree-scanning reader not yet in `record_reading` shows up in the nightly within 24 h. Low.
  - Confidence: medium-high.
  - The owner must decide: DEC-891 is the owner's list.

### 4.7 The re-pin ladder (P-REPIN-2, DEC-933, DEC-884; trials, combined re-pins, rollback folders)

- **Protects:** the judge (`gov` used by `gov close`) is a reviewed, versioned build, not the code under change, so a ticket cannot weaken the gate that judges it. A rollback folder is kept. **Needed now?** Not as an owner act per judge fix. Under ADR-0001 the risk is an honest bug in the judge, not an adversary, and tests and review cover that.
- **Cost:**
  - **Re-pin 1:**
    - **22 h 35 min** from W2-66's merge (`c60c9704`, 10-24 20:29) to ACT-REPIN-1 (`8455edd6`, 10-25 19:04);
    - then **25 h 40 min** to the owner's act (`82f2d453`, 10-26 20:44);
    - DEC-884 had held every re-pin until W2-66 was built, reviewed, merged and trialled.
  - **Re-pin 2:** 9 h 51 min (`8555aafc` to `a47f1b3c`), including the ladder's full run of 5,707 s, then **6 h 43 min** to the act (`bc37c419`).
  - **The close drought:** 4 d 19 h 55 min with no clean close, 10-22 to 10-27. This falls mostly in the wait for re-pin 1 and for judge fixes:
    - W2-58 waited 7.2 days: for W2-07's rule on decision records and re-pin 2, then for a fixture fix (#21, W2-75);
    - W2-63 waited 7.6 days, for W2-07's reading of the acceptance path and re-pin 2.
  - **The settings regeneration that rode re-pin 1:**
    - 9 reds;
    - W2-70's refused close (#18, 68.5 min);
    - **16 h 28 min** with the queue idle;
    - W2-74 (191 min);
    - the standing DEC-925 rule (a full run on a clone before every settings ACT; 2 h 49 min for ACT-W2-57-LS-1).
  - **Owner decisions** with this as main reason, **9:** DEC-822 (the bootstrap pin), 835, 879, 884, 899, 922, 925, 932, 935. DEC-921 and DEC-933 sit beside them. Owner ACTs: REPIN-1, REPIN-2, and REPIN-3 pending.
- **Caught:** none recorded. Re-pin 2's ladder run gave "flaky-candidates 1", the W2-54 time limit, a load flake (`nightly/digest.txt`, 10-28).
- **Standard practice:** CI runs the checks as defined on the integration branch. A judge change ships when merged, after its tests and review.
- **Recommendation: lift until the Gov OS is whole.**
  - The close uses the judge at the head of `w2/integrate`, with `PYTHONPATH` at that head's `src`, or an automatic re-pin at each merge that touches `src/gov/close/**`. No owner ACT per judge fix.
  - Keep the owner's pin for releases to product repositories (W2-16, W2-18).
  - Risk: a merged bug in the judge passes later closes until noticed. The judge's own tests and the nightly cover that. Medium.
  - Confidence: medium-high.
  - The owner must decide: DEC-822, DEC-884 and DEC-933 are owner rules, and DEC-772 keeps `gov release` the owner's.

### 4.8 Close and verification locks, quiet windows and cut-offs (DEC-780, DEC-939, `/tmp/gov-os-verify.lock`, `/tmp/gov-os-rebuild.lock`, CLOSE-PENDING, 00:30–05:30, 01:00, no commits during a queue)

- **Protects:**
  - **Timing-sensitive tests going red under load:** W2-53's close started at load 28.87 and met extra reds (#5).
  - **Two heavy runs colliding:** a rebuild alone drives the load to about 32 (LEAD-w2-common line 28).
  - **The nightly finishing.**

  **Needed now?**
  - One mutex for full runs is cheap and sound.
  - Quiet windows and cut-offs exist only because some tests assert wall-clock limits. Routing those tests to the nightly removes the need.
- **Cost:**
  - **Verification-lock waits:** 2.8 h in the last 3 queue runs (00:07 to 00:45, 02:42 to 03:45, 10:31 to 11:37). Quiet-window waits: 0.5 h (`queue.txt`).
  - **Lead launches held:** **4.1 h** because a close was pending, and at least 0.2 h by the night window (`log/chain-*.log`). W2-84 waited from 01:06 past 05:30, an unfinished wait of at least 4.4 h.
  - **Brief gaps:** 230 measured minutes waiting on the lock, the load gate or a pending close (W2-77 60 min; W2-57 150 + 15 min; `brief-gaps.md`). The 90-minute rule exists because of these waits.
  - **"No commits during a queue":** slips (drift log 10-30 12:27; #7). It also delays record commits and merges for the whole of each 1 to 3 h queue.
  - **The rebuild lock** came after the unexplained 6 h 39 min rebuild of 10-29, which made the morning package 3 h 25 min late.
  - **Owner decisions** with this as main reason, **4:** DEC-737, 780, 806, 888. Also items of DEC-939 (2 and 6), DEC-942 (4) and DEC-951 (B).
- **Caught:** no product defect. The quiet window prevents false reds; it finds nothing.
- **Standard practice:** one concurrency group for full runs (a mutex, as CI concurrency groups do). Tests with wall-clock limits run nightly. Closes run in a clean worktree of the exact commit, so commits to the main tree during a queue are harmless.
- **Recommendation: replace.**
  - Keep the verification lock as a simple mutex.
  - Drop the quiet window, the 00:30–05:30 and 01:00 cut-offs, CLOSE-PENDING's hold on leads, and the rule of no commits during a queue, **once** timing-sensitive cases are routed to the nightly (DEC-951 item 3 started this).
  - Risk: more load reds at close until the routing is complete. Medium.
  - Confidence: medium.

### 4.9 The resource gate (`gate_check.py`, `disk_gate.sh`, `gate-config.json`, scratch budgets; DEC-898, DEC-942, DEC-947)

- **Protects:**
  - memory exhaustion and thrash: five leads started at once drove the load to 155 (owner, 10-29, `lead_chain2.sh` line 27);
  - disk or inode exhaustion: an auditor hit ENOSPC at 98 % inodes (DEC-898).

  **Needed now?** The disk gate and the budgets, yes. The memory arithmetic, only in a simpler form.
- **Cost:**
  - **Lead launches held by the gate: 12.2 h** in the 20 h from 10-29 16:30 to 10-30 13:00 (`log/chain-*.log`):
    - load and memory together, 8.4 h;
    - **memory alone, 3.2 h**, often with the CPU idle. On 10-30 at 12:52 the load was 2.1, against a need of 19.1 GB and 18.0 to 18.9 GB held;
    - load alone, 0.5 h.
  - **W2-57's brief gap:** the load gate held its starts from 19:30 to 22:20, 150 min.
  - **Scratch budgets** stopped two leads' full runs (DEC-904). That led to the retention trial (DEC-905).
  - **W2-20's built gate contradicts DEC-942 and DEC-947** (P-W2-20-SCOPE, DEC-950).
  - **Owner decisions** with this as main reason, **9:** DEC-742, 776, 847, 898, 902, 904, 905, 942, 947.
- **Caught:**
  - **Real:** the disk inventory found a launcher regression that left 4.1 million inodes and 36 GiB behind (row W2-M405, DEC-902).
  - **Real:** the budget's pressure cut a full run's footprint from 5,306,782 to 165,707 files (DEC-905).
  - **None:** no OOM kill has been recorded since the watch began on 10-29 at 20:47 (`log/oom-watch.txt`).
- **Standard practice:** a fixed cap on concurrent leads, measured once and re-measured weekly. A memory limit per session (cgroups), and alerting on disk and inodes. pytest's retention policy (in use).
- **Recommendation:**
  - **Keep** the disk gate and the scratch budgets.
  - **Replace** the per-minute memory arithmetic with a fixed lead cap.
  - Risk: an OOM kill under an unusual mix of work. Medium-low.
  - Confidence: medium.

### 4.10 The nightly and its rules (`governance/project/orchestration/nightly/`; DEC-933, DEC-934, DEC-938, DEC-949, DEC-951; the morning package; the route of 15 entries out of the close)

- **Protects:** the full suite on the integration head, every night, on a quiet machine. It catches what scoped closes skip, flaky tests, and the slow, timing-sensitive or live cases routed out of closes (DEC-935: 15 serial entries). **Needed now?** Yes. It is the backstop that makes the other lifts safe.
- **Cost:**
  - **Runs:** 5 runs of 4,249 to 5,707 s each, at night (`nightly/digest.txt`).
  - **W2-77:** 6.5 h of lead time for its clean-up. ACT-NIGHTLY-1.
  - **Missed nights:** it ran on 2 of about 8 nights before the cron job existed (DEC-933).
  - **Morning packages:** both late — 10-29 by 3 h 25 min (a 6 h 39 min rebuild ran in the foreground), 10-30 by 1 h 32 min (the wake-ups came late) (drift log).
  - **Holds:** DEC-938's hold of all closes after a red night held five closes on 10-30 until DEC-951 item A.
  - **Owner decisions** with this as main reason, **5:** DEC-933, 934, 938, 939, 951.
- **Caught:**
  - W1-03's head-move fixture (10-25), a real flaky test, fixed by W2-73;
  - W2-54's time-limit flake (10-28);
  - W2-71's premise test (10-30), which the close also hit.
- **Standard practice:** this is standard practice: a nightly full build.
- **Recommendation: keep.**
  - A red night opens a ticket against the change that caused it (DEC-951 A goes most of the way). It does not hold unrelated closes.
  - The morning package becomes one status line unless a decision is needed.
  - Keep the route of slow and live cases to the nightly, and finish it for every wall-clock assertion.
  - Risk: none.
  - Confidence: high.

### 4.11 Record checks (`record_checks.sh`; placeholder scan, DEC-893; row W2-L423's keyword rule, DEC-911; `validate_entry.py`, DEC-895; schema, path-map and authority checks)

- **Protects:** the orchestrator's own record edits breaking the checks and the record-reading suites. Such edits refused closes (#5, #11) and turned three suites red in every tree (DEC-882). It also keeps placeholders from reaching the owner (DEC-893; 8 packages had them) and unvalidated owner entries from reaching a close (DEC-895).
- **Cost:**
  - **About 5 min a run** (output files of 10-30, 10:26 to 10:31).
  - **243 orchestrator record-only commits since DEC-868,** plus 101 checkpoint-only ones (`git log`). **Estimate: 120 to 243 runs, 10 to 20 h** of the orchestrator's wall-clock, taking one run per one or two commits.
  - **The keyword rule:**
    - 12-digit hashes everywhere under `.gov-runtime/`;
    - `keyword_warn.py` at every close;
    - its tool bug held the queue 35 min (DEC-922, DEC-923);
    - DEC-926's exact-path exclusions.
  - **Slips the rule produced:**
    - record checks on untracked files prove nothing: W1-08 red for 16 min (`a999f97b`);
    - a commit chained with `;` after the checks (10-28, and the drift log for 10-30 06:41).
  - **Owner decisions** with this as main reason: DEC-730, 744, 893, 895, 926.
- **Caught:** real slips in the orchestrator's records, before commit:
  - the W2-20 ticket's broken YAML (drift log, 10-29 22:20);
  - W2-13's ticket schema and mutation reds;
  - placeholders in packages.

  None is a product defect, but each would have refused a later close.
- **Standard practice:** a pre-commit check that parses and schema-validates only the changed record files and scans them for placeholders, in seconds. The heavy checks run nightly.
- **Recommendation: replace.**
  - A fast check on the changed files only: YAML parse, schema, placeholders.
  - `core-graph` and `context-reproducibility` move to the nightly.
  - The keyword warning goes when W2-71 lands.
  - Risk: a record slip reaches `w2/integrate` and the nightly finds it. Low, once closes no longer run `gov check`.
  - Confidence: medium-high.

### 4.12 The guard's refusals, including the command forms (DEC-409, DEC-820, DEC-849)

- **Protects:**
  - writes outside the ticket's paths;
  - secrets;
  - the held-out material;
  - the counterpart's work (DEC-820 (c));
  - the hidden half of an evaluation set;
  - installs.

  For commands it cannot read whole, it refuses rather than guess: a `$VAR` write target, a heredoc, backticks, inline Python with braces, an opaque interpreter. That is DEC-409, failing closed.

  **Needed now?**
  - The write scope, secrets, held-out and separation rules: yes. They catch ordinary-work mistakes cheaply.
  - The command-form refusals: not as hard refusals. They protect the guard's parser. Under ADR-0001 the OS sandbox and git review are the backstop.
- **Cost:**
  - **335 denials measured:**
    - **143 in lead sessions:** 43 variable write targets, 36 removals, 26 heredocs, 13 backticks, 8 command substitutions, 2 reads, 1 inline Python, and 14 others, including launches;
    - **192 in surviving worker sessions:** 75 removals, 19 heredocs, 13 Write-tool path refusals, 11 variable targets, 4 backticks, 2 reads, 2 inline Python, and 66 others;
    - 70 of 109 lead returns, and 89 of 138 worker results, had at least one.

    **Estimate: 6 to 25 h of session time**, taking one to two turns per denial. A lead turn averages 134 s (10,759 turns, 399.4 h).
  - **The orchestrator's 103 tool scripts,** 40 of them single-use and named for one decision or one day (`append_dec934.py`, `apply_dec942.py` …), exist partly to get round the command forms.
  - **Run clones** of 3 GB or more, and a stray folder, that the guard will not let the orchestrator remove (CHECKPOINT; C-stalls E4).
  - **W2-58** (Policy 2, reads open: 26.2 h, $34.66) exists because read refusals blocked work (DEC-849, DEC-857).
  - **This audit** met one refusal: a script whose text held a backtick.
  - **Owner decisions** with this as main reason, **19:** DEC-728, 738, 743, 756, 758, 759, 764, 765, 769, 774, 778, 820, 821, 827, 845, 849, 857, 873, 907.
    - Seven of them (756 to 778) record guard defects that W2-50's reviews found: product work on the guard.
    - The rest set, relax or work round its rules: Policy 2, the read refusals, a refused launch, the sandbox's Read rule.
    - **W2-50 itself (10 runs, 36.5 h) exists to open a durable scratch root that the guard and the sandbox refused** (DEC-728's basis). Its review loops then produced most of these entries.
- **Caught:** the protective rules work as designed. How many mistakes they prevented is not measured. The real guard defects were found by reviews (§4.5), not by refusals. The command-form refusals caught no product defect.
- **Standard practice:** an OS sandbox for write scope (bubblewrap, which `gov launch` already uses for workers), secrets scanning, and review.
- **Recommendation:**
  - **Keep** the write-scope, secrets, held-out, separation and install rules.
  - **Lift until whole** the command-form refusals for targets inside the session's own scratch and worktree:
    - allow `rm`, and `$VAR` targets that resolve there;
    - allow heredocs into the session's scratch;
    - send any other unreadable command to the sandbox instead of refusing it.
  - Risk: an unparsed command writes outside scope. The sandbox and review catch it. Low under ADR-0001.
  - Confidence: medium (I did not test parser variants).
  - The owner must decide: this changes the guard, through CIT-P (CAP-33).

### 4.13 The readiness check at claim (Definition of Ready by hand, DEC-944; `dor_hand.py`)

- **Protects:** a ticket started without resolvable sources, valid paths or KPIs. **Needed now?** Mildly.
- **Cost:**
  - seconds per claim, in use since 10-29;
  - one slip: two claim commits did not name it (drift log, 10-29 20:26);
  - W2-82 is planned.
  - **Owner decisions:** none with this as main reason. DEC-944 founds it, inside a plan decision.
- **Caught:** no NOT READY is recorded.
- **Standard practice:** a ready checklist in the ticket template.
- **Recommendation: keep.** Risk: none. Confidence: high.

### 4.14 The brief builder's rules (`build_lead_brief.py`, `LEAD-w2-common.md`, its drafts, the twelve return fields, the 90-minute rule, brief gaps)

- **Protects:** every lead gets the same rules; returns are structured; a run is not lost to the two-hour limit while it waits; brief gaps are fixed within the week (DEC-943). **Needed now?** Yes, apart from the 90-minute rule, which exists only because of §4.8's waits.
- **Cost:**
  - **The builder's IMPL slot was filled with a role.** That put a role in `Implements:` on 41 commits, which led to:
    - the gate stop #19;
    - DEC-927;
    - 41 accepted-history entries in the owner's commits;
    - P-TRACE-IMPL-1 and its ACT.
  - **Two brief slips** (C-stalls P1, P2):
    - a product-spec worker launched on an engineer ticket;
    - a brief that told a test designer to read what DEC-820 (c) refuses.
  - **`LEAD-w2-common.md`:** 26 revisions, 169 lines, 38 KB, read by every lead.
  - **The 90-minute rule** sends runs back as PACKAGES (W2-51, W2-84 and W2-67 on 10-30, held by the close queue).
  - **18 brief-gap rows in two days,** 278 measured minutes.
  - **The twelve-field check** refused the first return of two of this audit's helpers.
  - **Owner decisions** with this as main reason, **16:** DEC-731, 732, 752, 786, 789, 793, 799, 824, 826, 836, 838, 839, 840, 854, 919, 943.
- **Caught:** the brief-gap loop works: 18 gaps were named and fixed or rowed.
- **Standard practice:** a template and a short checklist. Structured returns are good practice.
- **Recommendation:**
  - **Keep** the builder, the twelve fields and the brief-gap loop. Give the builder its tests (W2-79).
  - **Drop** the 90-minute rule when §4.8's waits go.
  - Risk: low.
  - Confidence: medium.

### 4.15 Reporting and package processes (six-part packages, ACT files, owner-ping, the status block DEC-948, the countdown and progress line DEC-878, the daily document, the morning package, supersession sweeps DEC-866, propagation DEC-851, the checkpoint and Policy 1 record sync DEC-887)

- **Protects:** the owner's decisions are informed, recorded and traceable (MR-6); the owner can be reached; rules are written where sessions read them. **Needed now?** For product and plan decisions, yes. Most of the volume comes from the machinery's exceptions.
- **Cost:**
  - **Volume (§3.4):**
    - 232 register entries in 14 days, 56 package files and 58 pings;
    - the prompt went from 26,160 to 80,599 bytes;
    - `record/w2` has 116 commits;
    - the five-line block and the countdown in every report.
  - **The owner's answer times** (from commit times, an upper bound; C-stalls S-7, checked against `git log`): a median of about 28 min by day, 7 to 13 h overnight, and 46 min to 25 h 40 min for ACTs.
  - **Failures of these processes:**
    - **#5:** a superseded DEC-636 cited in W2-63's ticket refused W2-53.
    - **DEC-882:** DEC-880's sweep marked DEC-843 superseded more widely than ordered: three reds in every tree.
    - **#18:** the DEC-866 sweep missed six `docs/source` cases.
    - **#10 and #11:** the record sync copied cache stores and scratch paths into the tree.
    - **#12:** the record's growth raced git gc in two suites' fixtures. The record then moved to `record/w2` (DEC-887).
  - **Owner decisions** with this as main reason, **22:** DEC-787, 788, 791, 809, 818, 819, 825, 842, 846, 850, 851, 855, 856, 858, 861, 866, 878, 887, 936, 945, 948, 949.
- **Caught:** process slips, logged in the drift log (6 lines this week).
- **Standard practice:** a short daily digest. Packages only for real decisions (scope, risk, the Contract). A register of decisions, not of machinery exceptions.
- **Recommendation: keep, and simplify.**
  - The register and packages stay for product and plan decisions.
  - Most packages and ACTs disappear with the lifts.
  - The status block and countdown become one line.
  - The `record/w2` sync runs once a day.
  - Risk: low.
  - Confidence: medium.
  - The owner sets their own reporting (DEC-850, DEC-855, DEC-948).

### 4.16 Others in use

| Feature | Protects | Measured cost | Caught | Recommendation |
|---|---|---|---|---|
| **Secrets check's chance red; row W2-L423's keyword rule** (DEC-897, DEC-911, DEC-922, DEC-923, DEC-926) | Secrets in derived stores | Gate stop #17 (12.4 min, then 1 h 25 min idle). The queue held 35 min. W2-69: 18.6 h, $31.27. W2-71: 17.1 h, $19.72, and its premise test then refused #22 and #23 (66.4 + 72.5 min) | W2-69's reviews found real fail-open misses in the secrets scan (DEC-909) | **Keep** gitleaks on commits and close outputs. Run secrets-indexing over derived stores **nightly**, not at close. Drop the 12-digit/keyword workaround when W2-71 lands. High |
| **Interim skip guard** (DEC-899 item 7, DEC-915) | A silent skip hiding a red | 0 stops in 13 closes. One bug caught before use (T5). DEC-915 avoided a fixed count of 31 that would have stopped every scoped close | 0 | **Keep** until W2-57 lands. High |
| **Pre-close gate (a)–(h) as a whole** (DEC-868, DEC-896) | Spending a full run on a refusal its gates can predict | 37 passes, 7.5 h. 4 stops, each saving a full run of about 70 min (about 4.7 h) | 4 stops: 2 B, 2 C | Since re-pin 2 the pinned close asks (a), (b), (d), (e) and (h) itself, uncounted, before any test. **Lift the queue's duplicates.** High |
| **Escalation state** | Loops | §4.1 | 0 | §4.1 |
| **Lead return and interim watchers** | Waking the orchestrator | Cheap. One late morning ping | | **Keep** (tooling) |
| **`close_queue.sh`** | Running closes one at a time with gates | 133 lines. Three tool bugs: exit 0 after a refusal (T8); its collection log kept the whole output (T9); gate (d)'s crash hidden by a pipe (10-29). It stops at the first refusal, and W2-57 was queued behind a known red (#23) | | **Shrink** to: a clean worktree of the commit, the close, gitleaks, the output commit |
| **Review rounds and the threat-model rules** (DEC-413, DEC-801 to DEC-803, DEC-916) | Endless review loops on deliberate constructions | The loops of W2-01, W2-50 and W2-16 before DEC-801 (§4.5) | | **Keep** DEC-801 to DEC-803: they cut the loops |
| **The live containment hook** (flags only) | A mistake seen as it happens | 101 flags since 10-03, non-blocking | Not adjudicated | **Keep** as advisory |

## 5. The minimum practices to close a ticket safely while the Gov OS is being built

Each practice below names what it protects and what it costs. Together they cover every A and B fault of §3.3 and the review-found defects of §4.5. None of them needs a re-pin, an owner commit or a quiet window.

1. **Acceptance tests written first, by an independent test designer** (MR-3, DEC-906).
   - Protects: the builder grading its own work.
   - Cost: one test-design run per ticket, already in the plan.
2. **The change tested on the merged commit, in a clean worktree of that exact commit.** That means the ticket's acceptance suite, `tests/unit`, and the suites the change can reach: W2-66's selection, full when shared core changes. One run at a time, under one lock.
   - Protects: regressions, and an untested change. It found #22 and the `tests/unit/secrets` clash.
   - Cost: about 10 to 20 min scoped, about 70 min full.
3. **An independent review before merge, for FULL tickets.** It is judged by JUDGEMENT.md's two questions, each finding with its two lines (DEC-801, DEC-808), and at most two rounds (DEC-413). Re-review only if a later merge had to resolve conflicts in reviewed files.
   - Protects: the defects tests miss (12 tickets in Wave 2, §4.5).
   - Cost: one reviewer run per round.
4. **The nightly full run on the integration head.** Slow, live and wall-clock cases run only there. A red night opens a ticket against the change that caused it and holds nothing else.
   - Protects: what scoped runs skip, flaky tests, drift.
   - Cost: about 1.5 h of machine time at night.
5. **The guard's core rules:** the write scope at edit time; no reads of secrets, the held-out material, the counterpart's work or the hidden half of an evaluation set; no installs (DEC-820).
   - Protects: honest scope and separation mistakes.
   - Cost: small, once the command forms are relaxed (§4.12).
6. **gitleaks** on staged content and on every close's outputs.
   - Protects: a secret reaching a commit.
   - Cost: seconds.
7. **Git discipline:** `w2/integrate` is never rewritten, merges are `--no-ff`, and the owner pushes daily as a backup (DEC-720, DEC-848).
   - Protects: history and recovery.
   - Cost: none.
8. **The disk and inode floor, and the scratch budgets, before heavy runs.**
   - Protects: the machine. Real catches: ENOSPC, and the 36 GiB launcher leak.
   - Cost: seconds.
9. **A close record for every ticket:** the commit closed, the runs and their counts, the review's verdict and the reds with their reasons. A short script writes it, or `gov close` with the lifted gates switched off.
   - Protects: traceability, and the evidence for the later clean-`gov close` proof.
   - Cost: seconds.
10. **A seconds-long check of the record files the orchestrator changes, before it commits them:** YAML parse, schema, placeholders.
    - Protects: record slips. These refused #5 and #11, and broke a ticket on 10-29.
    - Cost: seconds.

## 6. What each lift would need to undo later, when dog-fooding resumes

- **Every gate of the pinned close:** nothing is deleted from the product. The judge keeps every gate, so undoing a lift means closing with `gov close` again.
- **The orchestrator's tools:** `close_queue.sh` and `record_checks.sh` are versioned on `record/w2`. `gate_check.py` is newer than its last sync of 10-29 14:21, so it is saved there first.

| Feature lifted | To undo it later |
|---|---|
| `gov close` as the merge gate | Close with `gov close` again. Re-close every ticket closed meanwhile, batched by W2-68 (§8), or name the exceptions at the exit |
| Escalation | Nothing: it is back with `gov close` |
| Rebuild and STORE_STALE before each close | Put `gov rebuild` back as the queue's first step |
| Probe staleness and form checks | Back with `gov close`. Run `probe_impact.py` over the merges since the lift, and re-probe each FULL ticket whose reviewed files changed |
| Trailers as a refusal | Turn the lint back to a refusal. The exit report lists the commits to fix or accept as history |
| Ratchet lists, owner-only | Restore DEC-862 (a), DEC-891 and DEC-906 item 1. Move the quarantine list into `load_sensitive` in one owner commit |
| Work without a task | Back with `gov close` (DEC-896 and DEC-923 already handle decision records) |
| Containment | Back with `gov close`. Run `judge_commits` once over the ranges closed meanwhile, and decide each finding |
| Context packet | Back with `gov close`, with the store rebuilt |
| Checkpoint freshness | Back with `gov close`, and the queue's checkpoint step |
| `gov check` at close | Back with `gov close` and queue gate (b) |
| ACT-TESTMAP-1 | Revert its commit and the live test's revision, and restore DEC-891's places |
| Re-pin per judge fix | One ACT to pin the judge at that head. Restore DEC-933's ladder |
| Quiet window, cut-offs, CLOSE-PENDING, no commits during a queue | Restore the lines in `close_queue.sh`, `lead_chain2.sh` and LEAD-w2-common |
| Memory arithmetic of the resource gate | Restore the memory clause of `gate_check.py`, kept in `record/w2` |
| Full record checks | Restore `record_checks.sh` as the step before every record commit |
| Guard command forms | Revert the guard's CIT-E, a versioned kernel change |
| Repair tickets for non-own refusals | Back with `gov close` |
| Reporting simplifications | Restore DEC-878's countdown and DEC-948's five-line block |
| The queue's duplicate gates (a), (b), (d), (e), (h) | Restore their lines in `close_queue.sh` |

## 7. Where a recommendation touches the Charter, the master rules, the Contract or the guard (the owner's alone)

**The Charter (v5 §1, principle 5: "governance tokens are at most 10–15 % of a task's tokens", DEC-004, DEC-086).** No change is proposed, only a finding:
- the measure was never taken: `governance_share: not measured` in all 18 close records;
- every proxy is far above it: 42 % of lead time on machinery tickets, 64 % of commits records-only, 81 % of register entries governance-caused.

**The master rules.** Every recommendation keeps:
- **MR-3:** the builder never writes its own acceptance tests;
- **MR-4:** audit and review stay independent;
- **MR-6:** the owner decides; the reporting changes are the owner's own to set.

MR-5, the software company (DEC-944), is served by the standard practices of §5.

**The Contract.** Its close-related capabilities stay built, tested and shown by their acceptance tests. Only their use as gates on this repository is lifted:
- CAP-31: a repair ticket on every failed close;
- CAP-38: CAP-38.f's fresh reviewer is **kept as the review**, and only the gate's staleness rule is lifted; CAP-38.b, product traceability;
- CAP-39: a close fails on a stale index;
- CAP-58: CAP-58.h, containment attribution;
- CAP-59: escalation after three non-converging iterations.

**Wave 2's exit criterion 1.** "Every Wave 2 ticket … closes through a clean `gov close`" (WBS §0 rule 1; AR-8 and F-M3 under DEC-718; DEC-721) is a closed specification. A build-phase close contradicts it, so DEC-105's three options are in §8.

**The owner's standing rules changed by these recommendations:**

| Area | Decisions |
|---|---|
| Ratchet lists | DEC-757, DEC-762, DEC-766 |
| Ratchet and escalation entries as owner commits | DEC-862 (a), DEC-891, DEC-906 item 1 |
| Re-pins | DEC-884, DEC-933 |
| Quiet windows, cut-offs, closes first | DEC-780, DEC-939 items 2 and 6, DEC-942 item 4 |
| Hold on closes after a red night | DEC-938, as amended by DEC-951 A |
| The pre-close gate | DEC-868, DEC-896 item 4 |
| Record checks and the keyword rule | DEC-893, DEC-911 |
| The memory gate | DEC-947 |
| The countdown and the five-line block | DEC-878, DEC-948 |
| DEC-891's record places (ACT-TESTMAP-1) | DEC-891 |

**The guard.** The command-form relaxation (§4.12) changes the guard. It goes through CIT-P, independent review and the owner's approval (CAP-33, DEC-409, DEC-820). Its write scope, the read refusals for secrets, the held-out material, the counterpart's work and the hidden half of an evaluation set, and the install rule all stay.

## 8. The decision for the owner: three costed options (DEC-105)

**The contradiction.** The owner's direction of 2026-10-30 is to build and test the Gov OS first and dog-food it once it is whole. Wave 2's exit criterion 1 requires every ticket to close through a clean `gov close` now.

### (a) Apply now: a build-phase close, with the proof once the Gov OS is whole — recommended

- **What:**
  - Every close uses §5's practices.
  - The gates of §4 are lifted or replaced as recommended.
  - The orchestrator closes each ticket with `tk close`, under one standing owner decision, and writes its close record (§5 item 9).
  - Exit criterion 1 is shown at the end: every Wave 2 ticket re-closed with `gov close`, batched by W2-68, before W2-46.
- **Costs now:**
  - one owner decision;
  - a small close script, or `gov close` flags. The script is a LITE task. Flags change the judge and need one re-pin, slower;
  - each close then takes about 10 to 20 min scoped, or about 70 min full. Today it is 12.2 min of gates plus 12.0 or 72.5 min.
- **Costs later:** the final proof.
  - **Estimate:** about 70 tickets at today's 22 to 85 min each is **26 to 99 h** of machine time.
  - With W2-68's batch (one regression per head) it is roughly **2 to 4 h**, if the batch works as designed.
  - So W2-68's batch belongs to "the Gov OS whole".
- **What it frees:**
  - **Today:** the five closes waiting (W2-71, W2-77, W2-57, W2-03, W2-26).
  - **From now on:** refusals of every kind that 23 of the last 24 were.
  - **Over time:** most re-pin ACTs, ratchet commits and machinery packages.
- **Risk:**
  - **A red outside a change** is found the next night, not at close.
  - **A product defect that only dog-fooding finds** (the five B refusals of §3.3) shows up later, in the nightly's `gov check` and at the final proof. To keep part of that value at no stall cost, run the lifted gates nightly in **report-only mode** and file what they find as product tickets. This is the standard way to bring in a new check: warn first, enforce later.

### (b) Defer: keep the full `gov close` until the machinery tickets land, then lift

- **What waits for:** W2-57, W2-68's batch with W2-77, W2-76, W2-78, W2-85, and re-pin 3.
- **Costs, at the measured rates:**
  - 16 refused full runs and 20.5 h of no-close queue time in 10 days of queue use;
  - 3 refusals on 10-30 alone;
  - 42 % of lead time on the machinery;
  - a re-pin per judge fix, 16.6 to 48 h each.
- **Gain:** dog-fooding keeps finding machinery and product gaps: 5 in 14 days.

### (c) Re-baseline: change exit criterion 1

- **What:** "every Wave 2 ticket closes through the build-phase close, and a clean `gov close` is shown on a named sample at the exit".
- **Cost now:** one owner decision.
- **Cost later:** the sample's runs, an estimate of 2 to 14 h for 5 to 10 tickets.
- **What it gives up:** the every-ticket F-M3 proof is weakened.

### Recommendation

**(a)** — High confidence on the direction, medium on the final proof's cost. That cost depends on W2-68's batch.

**Two open items follow from (a):**
- **P-W2-03-CONTAINMENT:** W2-03 closes under the build-phase close. Its option (c), teaching the judge criss-cross merges, stays a Wave 3 row.
- **ACT-TESTMAP-1:** commit its two prose lines once DEC-891's places are widened and W2-66's live test is revised. Leave `orchestration/nightly/**` out (§4.6).

## 9. Evidence index, limits and corrections

### Scripts and outputs

All are read-only and live under `/tmp/gov-os-audit-features/`, removed at the end:

| Script | What it does |
|---|---|
| `closes.py` | every close result's code and findings |
| `queue_times.py` | queue, gate, lock, quiet and close times |
| `leads.py` | lead returns: minutes, cost, turns, status |
| `denials.py` and `workers.py` | guard denials, by form |
| `commits.py`, `area.py`, `rc.py` | the commits by kind, area, role and task |
| `chain_waits.py` | lead launch waits, by reason |
| `merge_close.py` | merge-to-close times (not used: merge subjects vary) |
| `split.py` | lead time split by ticket kind |
| `dec_keywords.py` | register entries naming each feature, an upper bound |

### Key files

**Logs** (all under `.gov-runtime/scratch/orchestrator/log/`):
- `close-queue-*/queue.txt` and `close-*.json`;
- `W2-01-close.json`, `close-DAEO-7rr2*.json`;
- `W2-*-A5-*.json`;
- `chain-*.log`;
- `nightly/digest.txt`, `nightly/status.txt`;
- `oom-watch.txt`, `drift-2026-w44.txt`;
- `repair-tickets/`.

**The judge and the tools:**
- `pin-5c401220/…/gov/close/{command,gates,select}.py`;
- `tools/close_queue.sh`, `record_checks.sh`, `gate_check.py`, `gate-config.json`, `lead_chain2.sh`, `dor_hand.py`.

**Rules and plans:**
- `governance/project/test-map.yaml`, `path-map.yaml`;
- `tests/acceptance/W2-66/test_w2_66_live_test_map.py`;
- `docs/plan/WAVE_2_WBS.md` §0;
- `docs/adr/ADR-0001-threat-model.md`;
- `docs/charter/CHARTER_v5.md`;
- `.github/workflows/ci.yml`;
- `governance/project/orchestration/brief-gaps.md`.

**Orchestrator drafts:** `drafts/P-W2-03-CONTAINMENT.md`, `drafts/ACT-TESTMAP-1.md`.

**External records:** `~/.config/gov-os-notify/pings.log`, `record/w2`.

### Limits

- **Owner minutes** are not measured. The orchestrator's own guard refusals are not either: its transcripts are not logged.
- **Worker results of removed worktrees are gone,** so 335 guard denials is a floor.
- **Classification is a reading.** Each close refusal is classified with its source (§3.3). Each register entry was classified by a helper and spot-checked; calls that could move are named in §3.5's note.
- **Lead launch waits are measured only since the lead chain existed** (10-29 16:30). Earlier waits were in the leads' own scripts and are not logged.
- **No test or check was run.** The time figures come from the logs.

### Corrections to the orchestrator's drafts

These do not change their conclusions:
- `E-weekly.md` lists the cause of the 10-20 16:04 gate stop as unknown. The check result shows core-schema refusing the `close` type that `gov close` writes (`close-queue-20261020-1422/check-DAEO-0rfi.json`).
- `B-progress.md`'s claim that "no Wave 2 refusal names the closing ticket's own work" held until 10-29. It no longer holds after W2-71's refusal of 10-30 (#22).

END OF PACKAGE
