# C. Where Wave 2 stalls, and the orchestrator's own slips (2026-10-16 to 2026-10-29 13:00)

Research agent C's findings (read-only, 2026-10-29). Builds on part B's close counts (`drafts/state/B-progress.md` §3–§4) and does not recount them.

**Abbreviations:**
- `LOG` = `.gov-runtime/scratch/orchestrator/log/`; `Q-<stamp>` = `LOG/close-queue-<stamp>/queue.txt`;
- `REG` = `docs/DECISION_REGISTER.md` (line numbers are the entry's heading line);
- `PKG` = `governance/project/orchestration/packages/`;
- `ARCH` = `.gov-runtime/scratch/orchestrator/CHECKPOINT-ARCHIVE.md`; `CP` = `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`;
- `B §n` = part B's section n; B's refusal numbers are written `R#n` (B §4 table).

**Times:** queue logs are local time (BST until 10-25, GMT after). Commit times come from `git log --format=%ci`.

**Method:**
- Slot and gate times were computed from every `Q-*` file. A slot runs from "rebuild before X" to "close X exit n" or to "STOPPED". The gate runs from "rebuild before X" to "check ok; close X".
- Lead-run durations and costs come from each `LOG/W2-*-A5-*.json` (`duration_ms`, `total_cost_usd`).
- Guard refusals come from the `result` text of those files: sentences that name a refusal, then read by hand.
- The working scripts are outside the repository, in the session scratchpad; they changed nothing.

---

## 1. Recurring stalls, measured

### 1.1 Overview: where the close queue's time went

| Measure | Value | Source |
|---|---|---|
| Queue wall time, all 22 queue runs | **28.1 h** | every `Q-*` (first to last line) |
| Slots that produced a clean close (13) | 12.5 h (747 min) | `Q-20261020-1422`, `Q-20261021-1924`, `Q-20261022-1511`, `Q-20261022-2044`, `Q-20261027-1546`, `Q-20261027-1957` |
| Slots of refused attempts (13 in the queue) | **14.7 h** (881.8 min) | `Q-2026-10-20`, `Q-run2`, `Q-20261020-1108`, `-1212`, `Q-20261021-0108`, `-1401`, `-1550`, `-2241`, `Q-20261022-0952`, `-1153`, `Q-20261026-2157`, `Q-20261027-1823`, `Q-20261028-2007` |
| Gate stops, no close started (4 logged) | 45.0 min | `Q-20261020-1422` (W2-54), `Q-20261021-1924` (W2-62), `Q-20261022-1335`, `Q-20261027-1546` (W2-66) |
| Share of queue wall time with no close | **55 %** (15.45 of 28.1 h) | the rows above |
| Pre-close gates, 30 passes | **6.1 h** in total; 10.3 to 13.9 min each, mean 12.2 min | every `Q-*` |
| Days with no clean close, between closes | 10-22 22:17 BST to 10-27 17:12 GMT: **4 d 19 h 55 min** | `Q-20261022-2044`, `Q-20261027-1546` |

### 1.2 The stalls

| # | Stall | What happened | Root cause, as measured | Time cost | What removes it |
|---|---|---|---|---|---|
| S-1 | **Refused closes and their repair rounds** | 18 refused of 31 finished attempts (B §3). Time from the first refusal or gate stop to the clean close, per ticket: W2-53 62.0 h, W2-54 34 h 36 min, W2-02 18 h 21 min, W2-62 18 h 05 min, W2-70 17 h 48 min, W2-50 10 h 37 min, W2-66 4 h 07 min. Still open: W2-58 (first refused 10-22 13:28 BST) and W2-63 (10-22 00:11 BST), each more than 7 days. | No refusal names the ticket's own work (B §4). The orchestrator's tooling or process appears in 14 of 18 and is the sole cause in 6 (B §4). | Machine time: refused full runs 13.7 h of test time (B §3). Of that, refusals that carry kind (d) used **10.5 h** (37,935 s) and those caused by (d) alone **3.1 h** (10,996 s). Queue slots with (d) as sole cause, plus the orchestrator-caused gate stops: **4.9 h** (`Q-20261020-1108`, `Q-20261021-0108`, `Q-20261022-0952`, `Q-20261026-2157`, `Q-20261027-1823`, plus gate stops in `Q-20261021-1924` and `Q-20261027-1546`). Ticket wait from refusal to clean close: **165.6 ticket-hours** over the 7 tickets that then closed. | The pre-close gates (DEC-868, REG 9476; DEC-896 item 4, REG 10189); merge-time stale-probe check (DEC-895, REG 10164); `close_queue.sh` gates (a) to (h) (CP lines 52–54). Since gates (d), (e) and (h) were added, no refusal has had cause TREE_NOT_COMMITTED, a missing trailer or WORK_WITHOUT_TASK (B §4, R#15 to R#18). |
| S-2 | **Full closes of 60 to 90 minutes, and the 11 to 14 minutes of gates before each close** | Full passing closes took 66.5 to 79.2 min (`Q-*`). The gates took 10.3 to 13.9 min: rebuild with collection about 4 to 6 min, record suites about 2 min, `gov check` about 5 min (`Q-20261027-1957`, 21:29:05 to 21:41:02). On 10-27 the six scoped closes' gates took **68.0 min**, against 78.8 min for the closes (56.7 against 50.7 min without W2-69). | Every queued close repeats the rebuild and `gov check` on code that has not changed: only records are committed between closes (DEC-883 basis, REG 9744). A record-only commit forces a full rebuild (DEC-883 item 4). A scoped close turns full whenever shared core or an unplaced file changed since its base (DEC-929 basis, REG 11200; CP line 3). | 6.1 h of gates over 30 passes. Scoped close slots: about 22 min, of which gates are about 11 to 12 (B §2.2). | W2-68's batch: one rebuild, one check and one regression per head, and two fingerprints. It is merged (`848f5ab3`) but **not switched on until row W2-M406's fix**: ticket W2-77 (P1-MORNING item 5; `drafts/DEC-939.md` item 5, uncommitted). Re-pin 3 is also needed. P-SCOPE-RECORDS-1 (DEC-929 item 1) stops record edits widening closes; not yet delivered (CP line 83). |
| S-3 | **Load-sensitive reds** | W1-38's rulesync probe (DEC-871, REG 9509; DEC-892), W1-07 `doctor` (DEC-885/886, REG 9814/9832), W1-30 r13 (R#5), W1-46 network (R#13), W2-54 time-limit (nightly 10-28 and re-pin 2's ladder, DEC-934, REG 11287). W2-53's 10-20 close started at load 28.87 (`Q-2026-10-20` line 3). | Under the close's parallel load, cases with fixed time limits or a 10-second probe fail. They pass alone (DEC-871 item 2; DEC-885). | Present in 9 of 18 refusals (B §4: kind c). Their full runs used **8.7 h** of test time (31,463 s, without the sweep). Load was the sole cause in one: R#5, 3,540 s. | W2-57 merged `57e363c5`. ACT-W2-57-LS-1 removed 6 entries (`6367e965`, DEC-931, REG 11224). The nightly route takes 15 serial entries out of the close (DEC-935, REG 11323). **Still open:** ACT-W2-57-LS-2 (24 entries) after re-pin 2 (CP line 18); the W2-54 time-limit case is a flaky candidate (row W2-L450, ARCH line 27). |
| S-4 | **Base reds after the settings regeneration (DEC-925)** | The first re-pin's settings commit (`8ba8b231`, 10-26 20:48) went in without a full run. W2-70's close then ran 68.5 min and was refused on 9 reds, none of them W2-70's (PKG/P-REPIN-R1.md §2). | Six `docs/source` cases enforced deny rules the regeneration removed: a DEC-866 sweep missed them. One lifecycle-hook case expected 0 and got 1. One registry line cited DEC-921, not DEC-922 (`repin_registry.py`). One leftover `__pycache__` folder (PKG/P-REPIN-R1.md §2). | Slot 81.6 min (`Q-20261026-2157`). The queue was then idle from 23:24 to 15:52 next day, **16 h 28 min** (`Q-20261027-1546`). W2-74's lead: 191 min, $3.09 (`LOG/W2-74-A5-run1.json`). W2-57's lead met the same eight reds (PKG/P-REPIN-R1.md §1). | DEC-925 item 2 (standing, REG 11050): any settings change gets a full run in the close's form on a clone, plus a dependent-test sweep, before the owner's commit. Cost of that rule per ACT: the ACT-W2-57-LS-1 clone run took 2 h 49 min (00:52 to 03:41; `LOG/act-runs/ACT-W2-57-LS-1-20261028-0052/run.txt`). |
| S-5 | **Waits for re-pins** | **Re-pin 1:** DEC-884 (REG 9778) held all re-pins until W2-66 was built, reviewed, merged and trialled. W2-66 merged 10-24 20:29 BST (`c60c9704`). ACT-REPIN-1 was sent 10-25 19:04 (`8455edd6`); the owner's act came 10-26 20:44 (`82f2d453`). **Re-pin 2:** W2-07 round 2 merged 10-28 03:17 (`8555aafc`). ACT-REPIN-2 was sent 13:08 (`a47f1b3c`); the act came 19:51 (`bc37c419`); the queue started 20:12 (`Q-20261028-2007`). | By decision, not defect: the closes of W2-58 and W2-63 waited for a judge holding W2-07 (DEC-896 item 4, REG 10189). Owner acts that need a plain terminal take longest (DEC-928 item 3, REG 11186). | Re-pin 1: from W2-66's merge to the ACT, 22 h 35 min (it includes slip S4's reset, §2); from ACT to act, **25 h 40 min**. Re-pin 2: preparation 9 h 51 min (including the ladder's full run, 5,707 s, B §5); from ACT to act, **6 h 43 min**. The close drought of 4 d 19 h 55 min (§1.1) falls mostly here. | DEC-933 item 1 (REG 11254): re-pin each judge improvement as it lands, not bundled. Not measured yet: re-pin 3 has not run. |
| S-6 | **Stale probes after merges (DEC-895)** | Before DEC-895, W2-50's close was refused PROBE_INVALID: W2-58's merge `eb0f1454` had rewritten its probed files (DEC-894, REG 10142). After DEC-895, `probe_impact.py` found stale probes at merge time: W2-69 after W2-74's merge (DEC-926, REG 11095), W2-57 after W2-07 round 2 (ARCH line 12), W2-67 after the W2-59/W2-65 merges (CP line 27), and W2-57 again after W2-68 (CP line 3). | Two tickets change the same files; the second merge outdates the first ticket's FULL review (DEC-894 finding 1: "caught as designed"). | Before the rule: W2-50's refused slot, 85.6 min (`Q-20261022-0952`), and W2-50 run 9 for a fresh probe, 310 min, $5.13 (`LOG/W2-50-A5-run9.json`). After the rule: re-probes run in parallel, e.g. W2-57's took 6 h 46 min, from 03:17 to 10:03 (`8555aafc` to `4904a60f`). W2-67 has been held since 10-25 with a stale probe (CP line 27). **No close has been refused PROBE_INVALID since 10-22** (B §4, R#15 to R#18). | DEC-895 item 2 (in force). Row W2-M403 (the close's own early check) and W2-07's KPI (DEC-896 item 3). |
| S-7 | **Waits for owner decisions** | **Daytime packages, n = 18:** answered in 3 to 155 min, median about 28 min. Examples: P-W2-55 14:05 to DEC-871 14:14 (`8dfd54e9`); P-W2-62-G1 14:18 to "answered by 15:01" (ARCH line 4689); P-REPIN-R1 11:10 to DEC-925 12:04 (`ecc49cc4`); P-TRACE-IMPL-1 17:40 to DEC-927 18:07 (`a652c48a`); P1-MORNING 10:56 (`d8882b3f`) to an answer drafted by 12:32 (`drafts/DEC-939.md`; CP line 3). **Overnight packages, n = 4:** P-W2-52 7 h 17 min (to `74d22909`); P-W2-59-8 8 h 40 min (to `b772b2fe`); P-W2-63-C1 9 h 32 min (`4166d8d9` to `8d625805`); P-W2-07-DR2 13 h 06 min at most (`ef9812b1` to `ec639fbb`). **ACTs:** ACT-W2-57-LS-1 1 h 29 min (`5c401220` to `6367e965`); ACT-P-TRACE-IMPL-1 46 min (`b99c75ce` to `e95d3520`); ACT-REPIN-2 6 h 43 min; ACT-REPIN-1 25 h 40 min. | Package-sent times are taken from each package's own "From:"/"Raised:" line where it gives one (PKG headers); otherwise from the package's commit. The decision time is its record commit, so the measure is an upper bound on the owner's answer time. | The owner is not the bottleneck by day. Overnight packages held work: P-W2-63-C1 held the closes of W2-50, W2-58 and W2-62 overnight (ARCH line 4572). | DEC-936 item 2.5 (REG 11347): P2s decided as delegated. DEC-938 (REG 11422): one morning package. Re-pin ACTs stay the owner's own act. |
| S-8 | **Guard refusals met by leads and workers** | By hand, about **45 of the 74 non-empty lead returns** (10-16 to 10-29) name a refused command form: a shell-variable write target ("guard-unresolvable"), a here-document, backticks, or an unreadable `python3 -c` (DEC-409). Examples: `LOG/W2-02-A5-run4.json`, `W2-57-A5-run1.json`, `W2-68-A5-run1.json` ("cost every worker turns"), `W2-71-A5-run1.json`. Read refusals (DEC-849) were mostly 0. A few refusals blocked work: W2-50 run 1's CIT-P write by a product-spec worker on an engineer ticket (`W2-50-A5-run1.json`); W2-67 run 1, the launcher refusing an engineer on a ticket filed as test-designer (DEC-907, REG 10616); W2-65 run 1, a stacked branch's base read refused (Policy 2 (c) reads against `w2/integrate`); W2-68 run 1, the design note refused to the test designer (DEC-820 (c)) although its brief says to read it. | `governance/project/briefs/LEAD-w2-common.md` does not mention variable write targets, here-documents, backticks or DEC-409 (a grep finds none). The orchestrator's own CP carries the rule (CP line 99), but every lead relearns it. | **Not measured** in minutes (turns, not timed). W2-67 run 1 ended PACKAGES after 192 min, $10.05 (`LOG/W2-67-A5-run1.json`). | **None yet.** The rule could go into `LEAD-w2-common.md` (a proposal; DEC-936 item 3.3 asks where each practice lives). |
| S-9 | **The secrets check's chance reds (row W2-M404; row W2-L423)** | 10-22 13:56: gate (b) red on a chance match inside an 84-character identifier (DEC-897, REG 10231). Row W2-L423: row W2-L423's rule flags a full 40-hex hash beside its keyword in scratch logs (`docs/plan/WAVE_2_LIST.md` line 1073). On 10-26 the keyword warning would have stopped every close (P-W2-L423-Q, DEC-922/923). On 10-27 the JUnit of W2-69's case held the keyword (DEC-925 item 1, DEC-926). | The raw store bytes were scanned at arbitrary offsets (DEC-897). The keyword warning also read index stores (DEC-923). | Gate stop of 12.4 min (`Q-20261022-1335`), then 1 h 25 min idle until the proven re-run (`Q-20261022-1511`). Re-pin queue held 21:27 to 22:02 on 10-26 (35 min; DEC-922 to DEC-923; `Q-20261026-2157`). The fix tickets: W2-69 runs 1 to 3, 1,115 min, $31.26 (`LOG/W2-69-A5-run1..3.json`); W2-71 run 1, 323 min, $7.01. W2-71's reviewer F1 delays re-pin 3 by about 3 h (P1-MORNING item 4). | W2-69 is closed (`07a8d624`). Row W2-L423: DEC-911 interim (12-digit hashes, `keyword_warn.py`). W2-71 (run 2 in flight, CP line 3) rides re-pin 3. |
| S-10 | **The green-here fixture timeout (row W2-L429, DEC-937)** | W2-58's second close (10-28 20:25 to 21:31) had 0 failures and 3 setup errors: W2-54's `gov_check_here` fixture timed out past 900 s under load (DEC-937, REG 11401). | The fixture runs `gov check` itself, which takes about 6 min alone. Row W2-L429 had recorded the same timeout on 10-24 and named this fix (`docs/plan/WAVE_2_LIST.md` line 1079). | Slot 79.2 min (`Q-20261028-2007`). Queue held from 21:31 to 12:45 next day, **15 h 14 min** (`Q-20261029-1228`; this includes the nightly and S-11). W2-75's lead: 325 min, $5.50 (`LOG/W2-75-A5-run1.json`). | W2-75 merged (`b52e3a96`). W2-58's re-close was decided (`drafts/DEC-939.md` item 3, uncommitted). |
| S-11 | **The 6 h 39 min rebuild (10-29)** | After W2-75's merge, a main-tree `gov rebuild` ran from about 04:10 to 10:49 and exited 0 (PKG/P1-MORNING-2026-10-29.md item 2). | **Not found.** Ruled out: a failure, and disk space. Suspects: the embedder or a network wait, or the code-graph daemon lock; `drafts/DEC-939.md` names concurrent rebuilds as likeliest. The 12:23 rebuild took 271 s and did not reproduce it. A rebuild's output times only its lexical stage (`LOG/rebuild-after-W2-57.txt`: `lexical_s` only). | **6 h 39 min.** It also made the morning package 3 h 25 min late (slip S8) and delayed the queue: W2-75 merged 03:59, the queue started 12:45 (8 h 46 min; `b52e3a96`, `Q-20261029-1228`). | Ticket W2-76: per-stage timings, a 30-minute watchdog, a machine-wide rebuild lock. Until then rebuilds run under `flock /tmp/gov-os-rebuild.lock` (`drafts/DEC-939.md` item 2, uncommitted; CP line 3). |
| S-12 | **Holds by the owner's decision (not defects)** | The Wave 2 pause for the independent assessment (10-19) ran from about 12:30 (ARCH line 4348) to the next claim, `162f17ea` at 22:22: about 10 h. The review point (DEC-889 item 14) held W2-66/67/68 work from `611955fa` (10-21 19:24) to DEC-899 `2f048613` (10-23 10:08). | Owner decisions. | About 10 h; 38 h 44 min. | n/a |
| S-13 | **Lost or empty lead runs** | 9 lead returns are empty: W2-05 r2, W2-37 r1, W2-50 r7, W2-52 r1 and r2, W2-54 r3 and r4 (all 10-18 14:07 to 10-19 00:35), W2-57 r4 and W2-71 r2 (both still running at 12:24 on 10-29). | W2-50 run 7 was stopped by the orchestrator's watcher before any engineer (ARCH line 222). For the other 10-18 runs, **the cause is not recorded** in the sources read. | Not measured. | n/a |

### 1.3 Ranking by measured time cost

1. **Close drought and re-pin waits** (S-5): 4 d 19 h 55 min with no clean close; owner terminal acts of 25 h 40 min and 6 h 43 min.
2. **Refused closes** (S-1): 14.7 h of queue wall time, 13.7 h of test time, 165.6 ticket-hours waiting. The orchestrator's tooling or process carries 10.5 h of the test time and is the sole cause of 3.1 h.
3. **Queue idle after a refusal**: 16 h 28 min (S-4, the regeneration) and 15 h 14 min (S-10, green-here).
4. **The 6 h 39 min rebuild** (S-11), plus 8 h 46 min of queue delay.
5. **Gates** (S-2): 6.1 h over 30 passes; longer than the scoped closes they guard.
6. **Load-sensitive reds** (S-3): present in 8.7 h of refused test time.

---

## 2. The orchestrator's own slips, 2026-10-16 to 2026-10-29

**Kinds:** R = record/commit discipline; T = tool bug; S = scheduling/process; P = scope/selection; E = environment assumption.

**Prevented?** "Yes (check)" means a tool or gate now catches it. "Yes (rule)" means a written standing practice only. "No" means it could recur.

| # | Kind | Date | Slip | Cost, where measured | Prevented? | Source |
|---|---|---|---|---|---|---|
| R1 | R | 10-17 | Edited W2-01's ticket file on `w2/integrate` after its probe (`d09e8c1b`, `ee30c9de`): PROBE_INVALID at W2-01's close | Part of R#1: 4,835 s of test time | Yes (rule: never edit a reviewed ticket's file, ARCH line 130; check: `probe_impact.py`, DEC-895) | ARCH lines 130–132; B §4 R#1 |
| R2 | R | 10-20 | W2-63's `sources` cited superseded DEC-636; the sweep put W1-35's tests into W2-11's paths | Part of R#6: slot 81.5 min | Yes (check: `record_checks.sh`, DEC-868 item 2) | DEC-867 items 1–2 (REG 9458) |
| R3 | R | 10-20 | `P-W2-53.md` left uncommitted: TREE_NOT_COMMITTED for W2-54 | Slot 10.3 min | Yes (check: gate (d), `tree_diff.py`) | `Q-20261020-1108`; B §4 R#8; ARCH line 4466 |
| R4 | R | 10-21 | Decision-record commits changed ticket files without that ticket's `Task:` (`b772b2fe` for W2-58, `8d625805` for W2-63): WORK_WITHOUT_TASK | Slot 82.9 min (`Q-20261022-1153`); W2-58 still not closed | Yes (check: gate (h), DEC-896 item 2) | ARCH lines 4526–4532; DEC-896 (REG 10189) |
| R5 | R | 10-19 | W2-62's claim commit `162f17ea9caf` lacks `Implements:` ("my slip") | Gate stop 11.1 min; DEC-891 | Yes (check: gate (e), `trailer_gate.py`) | ARCH line 4579; `Q-20261021-1924` |
| R6 | R | 10-22 | DEC-892's entry named its test without the file path; the ratchet refused it | Part of R#14: slot 85.6 min | Yes (check: `validate_entry.py`, DEC-895 item 1) | DEC-894 finding 2 (REG 10142) |
| R7 | R | 10-21/22 | Placeholder times ("00:2x") in 8 packages and an owner-committed entry | None measured | Yes (check: `placeholder_scan.py`, DEC-893) | ARCH lines 4547–4551 |
| R8 | R | 10-23 | W2-13's ticket committed with core-schema only: an unquoted colon (schema red) and five MR-3 paths (core-mutation red) | Not measured | Yes (check: `record_checks.sh` runs W1-08's ticket test) | ARCH lines 4865–4867 |
| R9 | R | 10-23 | W2-67's ticket file named the test-designer role; its card puts the builder tests on an engineer, so the launcher refused the engineer | W2-67 run 1 ended PACKAGES: 192 min, $10.05 | Partly (the launcher refuses at the start; no check matches a ticket's role to its card) | DEC-907 (REG 10616, line 10620); `LOG/W2-67-A5-run1.json` |
| R10 | R | 10-21 | DEC-880's sweep marked all of DEC-843 superseded, wider than the owner's order, and suite logs were copied into the record: three reds in every tree | Found by W2-58's lead before a close; not measured | Partly (DEC-882: suite logs out of the record; scope is practice only) | DEC-882 (REG 9720) |
| R11 | R | 10-27 | ACT `.patch` file committed under `orchestration/`: W2-66's own record-only case refused the close | Slot 83.3 min (`Q-20261027-1823`; 3,633 s of test time) | Partly (`508571d3`: the patch removed and the record-only list holds only `.md`; ACT patches kept in scratch, PKG/ACT-W2-57-LS-1.md; no pre-commit check) | ARCH lines 103–105; B §4 R#17 |
| R12 | R | 10-28 | The nightly's folder committed outside every path-map namespace (`a999f97b`): W1-08 red | 16 min until `95a810a6` | No: the lesson "record checks on untracked files prove nothing" is practice only | DEC-936 (REG line 11353); ARCH line 24 |
| R13 | R | 10-28 | Commit `1916501d` chained with `;` after a red check | Within those 16 min | Yes (rule: "commits are now conditional on green checks") | REG line 11353; ARCH line 25 |
| R14 | R | 10-28 | Wave 2 list rows marked in place instead of moved to §4 (`76fb5f18`) | 50 min until `4f2fc3d6` | No (practice) | DEC-932 (REG 11238, "Also") |
| R15 | R | 10-28 | W2-75's ticket (`f13701be`, 21:57:41) committed before DEC-937, which it cites (`6a195eca`, 22:07:19) | Not measured | No (lesson in CP line 23 only) | git times; CP line 23 |
| R16 | R | 10-22/23 | W2-69 left out of two reports' ticket totals | None | No | ARCH lines 4861–4862 |
| R17 | R | now | CP's RESUME sections are stale: "Plan in force (DEC-896..DEC-919)", "Merged, not closed (11)", "Next free: DEC-932; ticket W2-75" | Risk on resume; not measured | No | CP lines 69–93 |
| T1 | T | 10-20 | The queue's checkpoint commits carried no `Implements:` (three commits) | Part of R#9: slot 90.5 min | Yes (`Implements: DEC-868`; gate (e)) | DEC-871 item 1 (REG 9509) |
| T2 | T | 10-21 | `sync_context.py` copied W2-48's self-ignoring cache stores: TREE_NOT_COMMITTED for W2-02 | Slot 13.3 min | Yes (`c3b32d31`; gate (d)) | `Q-20261021-0108`; ARCH line 4477 |
| T3 | T | 10-21 | `sync_context.py` copied a scratch folder into paths in no namespace (`21302ae9`): W1-08 red | Part of R#11: slot 89.5 min | Yes for the sync (DEC-885 item 2); the same red recurred by hand as R12 | DEC-885 (REG 9814) |
| T4 | T | 10-26 | `repin_registry.py` wrote `approved_by: DEC-921`, not DEC-922: W1-06 red | Part of R#16 | Unknown: fixed by hand; re-pin 2's entry cited DEC-933 correctly (DEC-935); no record of a tool change | PKG/P-REPIN-R1.md §2 |
| T5 | T | 10-27 | `skip_gate.py` compared dotted and path test ids, so it would have stopped after every passing close | None (caught before use) | Yes (reads both forms) | PKG/P-REPIN-R1.md §2; ARCH line 4979 |
| T6 | T | 10-26 | `keyword_warn.py` read the index stores, so it would have stopped every close | Queue held 35 min (DEC-922 to DEC-923) | Yes (DEC-923 item 1; DEC-926) | DEC-922, DEC-923 (REG 10919, 10984) |
| T7 | T | 10-23 to 10-27 | `build_lead_brief.py`'s IMPL slot was filled with a role: 39 commits on `w2/integrate` plus 2 on W2-57's branch named a role in `Implements:` | Gate stop 10.8 min (`Q-20261027-1546`); 41 accepted-history entries by the owner's commit (`e95d3520`, `f06ccf4b`) | Yes (check: the builder refuses a non-id IMPL; gate (e); leads run `trailer_gate.py`, DEC-927 item 2) | DEC-927 (REG 11117); PKG/P-TRACE-IMPL-1.md; ARCH line 5008 |
| T8 | T | 10-27 | `close_queue.sh` exited 0 after a refused close (`break`) | Not measured | Yes (exit 4 plus `test_close_queue_refusal.sh`) | DEC-929 item 3 (REG 11200) |
| T9 | T | 10-27 | The queue's collection log kept the whole output | None | Yes (errors and summary only) | ARCH lines 4980–4981 |
| S1 | S | 10-19 | Close started without a rebuild before it: STORE_STALE | 1 s | Yes (the queue rebuilds right before each close) | B §4 R#4 |
| S2 | S | 10-20 | W2-53's close started at load 28.87 although the queue had logged "quiet" (the agent's reading) | Part of R#6 | Yes in practice: every later close started at load 2.7 to 6.4 (`Q-*`) | `Q-2026-10-20` lines 1–3 |
| S3 | S | 10-23 | The owner's commit B (`c9a08678`) was validated without a full regression: W1-01's MR-3 history case went red on `w2/integrate` | Red from 11:02 to 23:21 (12 h 19 min, to `efdc4188`); every lead's full run red meanwhile | Yes (rule: DEC-906, an owner commit touching tests gets a full run first; DEC-925 item 2) | ARCH lines 4831–4833; PKG/P-W1-01-H.md |
| S4 | S | 10-25 | Merge order: W2-59 then W2-65 made a criss-cross history that containment would refuse (P-W2-65-M1, "my error in the merge order") | 13 h 53 min from `e77ffb54` (04:59) to the replacement merge `6a4696eb` (18:52); needed the owner's yes to a rewrite | Partly (DEC-921; `judge_commits` before a re-pin, ARCH line 4913) | PKG/P-W2-65-M1.md; DEC-921 (REG 10896) |
| S5 | S | 10-26 | Settings regeneration sent without a full run or sweep (the DEC-866 sweep missed six `docs/source` cases) | S-4: slot 81.6 min plus 16 h 28 min idle plus W2-74 (191 min) | Yes (rule: DEC-925 item 2, standing) | REG 11050; PKG/P-REPIN-R1.md |
| S6 | S | 10-21 to 10-28 | The nightly was never scheduled although DEC-852 item 3 asked for one every night: it ran on 2 of about 8 nights ("a lapse, the orchestrator's") | Not measured (reds found late; no green base for scoped closes) | Yes (cron, ACT-NIGHTLY-1, DEC-936; first cron night green, B §5). Depends on the PC being awake (DEC-934 item 4) | DEC-933 (REG line 11278) |
| S7 | S | 10-22 | Lens I area 4's brief let the auditor end with background runs pending and set no scratch budget: no report; disk inodes at 94 % | Resume auditor 187 min, $32.54 (`LOG/assessment-I4-resume.json`) | Yes (rule: foreground runs in auditor briefs; DEC-898 budgets and the disk gate) | ARCH lines 4708–4740; DEC-898 (REG 10274) |
| S8 | S | 10-29 | A long rebuild ran in the foreground, so the 07:30 wake-ups waited | Morning package 3 h 25 min late | **No, not yet** (`drafts/DEC-939.md` item 1, uncommitted) | PKG/P1-MORNING-2026-10-29.md item 1 |
| S9 | S | 10-24 to 10-28 | Row W2-L429 named the green-here fix on 10-24, but it was not scheduled before the full closes it would hit (the agent's reading) | S-10: slot 79.2 min plus 15 h 14 min held plus W2-75 (325 min) | No (no rule ranks a known close-breaking row ahead of the queue) | WAVE_2_LIST line 1079; DEC-937 (REG 11401) |
| S10 | S | whole period | The lead brief omits the guard's command-form rules, so about 45 of 74 returns relearn them; the orchestrator also met one in the re-pin smoke test (DEC-922) | Not measured (turns) | No | `LEAD-w2-common.md` (grep: none); S-8; REG line 10948 |
| P1 | P | 10-16 | A product-spec worker launched on an engineer-role ticket, so W2-50's CIT-P write was refused | The CIT-P stayed uncommitted in run 1 (62 min, $3.22) | Rule (row W2-L389: brief A4 needs an engineer there, DEC-879 item 4) | `LOG/W2-50-A5-run1.json`; REG 9645 |
| P2 | P | 10-28 | W2-68's brief told the test designer to read the design note, which DEC-820 (c) refuses | Not measured | No (not recorded as fixed) | `LOG/W2-68-A5-run1.json` (discoveries) |
| E1 | E | 10-18 | The premise "workers are OS-blocked" (P-W2-29) was wrong: no Wave 2 worker was OS-sandboxed | Not measured | Corrected (P-W2-36; DEC-873; row W2-L374) | ARCH lines 149–151 |
| E2 | E | 10-28 | The clone-run script's `-E` dropped `PYTHONPATH`: the first ACT-W2-57-LS-1 run read 0 serial entries | One clone run lost (its start was not recorded); restarted 00:55 | Yes ("fixed + guard") | ARCH line 36 |
| E3 | E | 10-28 | ACT-NIGHTLY-1 assumed `owner-ping` from cron reaches the owner's phone; it only writes `pings.log` | Night P1s reach the owner only through the 07:30 package | **No, not yet**: an emergency notifier is an ACT (`drafts/DEC-939.md` item 7, uncommitted) | DEC-936 (REG line 11389); P1-MORNING item 7 |
| E4 | E | 10-22 onward | Assumed the orchestrator could remove run clones and stray folders; the guard refuses its `rm`. `~/gov-os-runs/W2-00` holds 3 GB or more, never removed, and W2-65's stray `pytest-of-usain/` remains | Disk only | **No** (P-TOOLS-REVIEW-1 not delivered) | ARCH lines 29, 59, 4742; CP lines 16–17, 25 |

### 2.1 Count by kind

| Kind | Count | Prevented by a check | Prevented by a rule only | Partly, or unknown | Not prevented |
|---|---|---|---|---|---|
| R: record/commit discipline | 17 | 7 (R2–R8) | 2 (R1, R13) | 3 (R9, R10, R11) | 5 (R12, R14, R15, R16, R17) |
| T: tool bug | 9 | 8 | 0 | 1 (T4) | 0 |
| S: scheduling/process | 10 | 2 (S1, S6) | 4 (S2, S3, S5, S7) | 1 (S4) | 3 (S8, S9, S10) |
| P: scope/selection | 2 | 0 | 1 (P1) | 0 | 1 (P2) |
| E: environment assumption | 4 | 1 (E2) | 0 | 1 (E1, corrected) | 2 (E3, E4) |
| **Total** | **42** | **18** | **7** | **6** | **11** |

**Measured cost of the slips that refused or stopped closes:**
- Queue slots: R2, R3, R4, R6, R11, T1, T2, T3 and S5/T4, plus gate stops R5 and T7.
- Where the slip was the sole cause: **4.9 h** (S-1). Where it was one of several causes: up to 12.2 h.
- Queue idle after S5 and S9: **31 h 42 min**.

## 3. Where the data is incomplete

- **Guard refusals:** counted by reading the extracted sentences, not timed. A run may name a refusal of another session. The count "about 45 of 74" may be off by a few.
- **Owner answer times:** the decision's record commit is an upper bound. When a package was committed together with its decision (P-W2-58-C1, P-W2-62-G1, P-REC-1), the sent time comes from the package's "From:" line or from ARCH.
- **The 10-21 08:22 queue run** (B: "cause unrecorded"): ARCH line 4479 records it. It was stopped by the orchestrator at about 08:25 to give W2-58 the machine (DEC-880); only its rebuild was lost.
- **Not measured:**
  - the cause of the six empty lead returns of 10-18/19;
  - the first E2 clone run's start;
  - the cost of S6, S10 and R15.
- **The classifications are this agent's reading** (especially S2 and S9), for the auditor to dispute.
- **Two items rest on an uncommitted draft:** DEC-939 (`drafts/DEC-939.md`) is drafted, not committed, so S8, E3 and the S-11 safeguards are "decided, not yet in force".

---

## Summary (at most 300 words)

**Top stalls by measured time:**
1. **No clean close for 4 d 19 h 55 min (10-22 to 10-27).** This was mostly the wait for re-pin 1. The owner's re-pin act took 25 h 40 min after its ACT, and 6 h 43 min for re-pin 2.
2. **Refused closes:**
   - 14.7 h of queue wall time (55 % of the queue's 28.1 h produced no close) and 13.7 h of test time;
   - the orchestrator's tooling carries 10.5 h of that test time and is the sole cause of 3.1 h;
   - tickets waited 165.6 ticket-hours from refusal to a clean close; W2-58 and W2-63 have been waiting more than 7 days.
3. **Queue idle after base reds:** 16 h 28 min after the unswept settings regeneration; 15 h 14 min after the green-here timeout.
4. **The unexplained 6 h 39 min rebuild:** it caused 8 h 46 min of queue delay and a package 3 h 25 min late.
5. **Gates:** 6.1 h over 30 passes, longer than the scoped closes they guard. W2-68's batch is merged but off until W2-77.

By day the owner answers in a median of about 28 minutes; only overnight packages (7 to 13 h) and re-pin ACTs wait long.

**Slips, by kind (42):**

| Kind | Count |
|---|---|
| Record/commit discipline | 17 |
| Tool bug | 9 |
| Scheduling/process | 10 |
| Scope/selection | 2 |
| Environment assumption | 4 |

18 are now caught by a check, 7 are held by a rule only, and 6 are partly fixed or unknown.

**11 slips are not yet prevented:**
- record discipline: namespace check on tracked files (R12), rows moved, not marked (R14), register before ticket (R15), report totals (R16), stale RESUME sections (R17);
- process: long commands in the background (S8, decided in the uncommitted DEC-939); unscheduled known close-breaking rows (S9); lead brief lacking the guard's command-form rules (S10, about 45 of 74 leads relearn them);
- scope: W2-68 brief against the guard (P2);
- environment: cron pings never reach the phone (E3); run clones the guard won't let the orchestrator remove (E4).
