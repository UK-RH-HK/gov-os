# The review bundle, all in one file (2026-10-23)

The parts the owner asked for, in reading order. Each is copied verbatim from the file named under its heading; only top-level headings inside a part are demoted one level so the parts stay distinct. Nothing here is committed or started.


---

# 1. The index

*Source: `drafts/review-bundle/00-INDEX.md`*

## The review bundle (DEC-889 item 14): drafts, results and the decisions they need

From: the W2 orchestrator, 2026-10-22. Nothing in this bundle is committed or started. W2-66, W2-67 and W2-68 wait for your written confirmation (the review point).

## What is in it (Windows paths)

Folder: `\\wsl.localhost\Ubuntu-24.04\home\usain\Dynamic-Agentic-Engineering-OS\.gov-runtime\scratch\orchestrator\drafts\review-bundle\`

| File | What |
|---|---|
| `00-INDEX.md` | This page |
| `01-W2-66-ticket.md` | W2-66's ticket file, replacing `DAEO-c1uz.md`: selection and evidence only, the test map, P-IS-1 (a), P-IS-2 (a) |
| `02-W2-66-card.md` | W2-66's WBS card, replacing §2's |
| `03-W2-68-card.md` | W2-68's card: batching, reuse, two fingerprints, the red batch, the trial |
| `04-W2-67-card.md` | W2-67's card: copies, nested runs, temp folders, the weak tests' revisions (P-IS-3's unit part, P-IS-7 (a)) |
| `05-W2-57-ticket.md` | W2-57's ticket file (new) and its route out for every list entry (P-IS-6 (a)) |
| `06-W2-07-card.md` | W2-07's card with DEC-896's three KPIs, P-IS-4 (a) and DEC-898's disk reading |
| `07-REPIN-PLAN.md` | The two re-pins: what each carries, the order before it, your acts, the rollback |
| `08-corrections-P-IS-5.md` | P-IS-5 (a): the W2-65, W2-69 and W2-66 ticket-file corrections |

**The results behind them:**
- **Lens I's synthesis:** `\\wsl.localhost\Ubuntu-24.04\home\usain\Dynamic-Agentic-Engineering-OS\.gov-runtime\scratch\assessment\2026-10\I-SYNTHESIS.md`. It is copied byte for byte to `docs\assessment\2026-10\` with the four area reports after the running close: `I1-guard-launcher-sandbox.md`, `I2-close-checks-ratchet.md`, `I3-retrieval-context-resume.md` and `I4-records-plan-rest.md`, in the same folder.
- **The tool trials:** `\\wsl.localhost\Ubuntu-24.04\home\usain\Dynamic-Agentic-Engineering-OS\governance\project\orchestration\packages\TOOL-TRIALS-2026-10-22.md`.
- **Lens H:** `docs\assessment\2026-10\H-test-strategy.md`.

## Lens I in five lines (the synthesis, section 1)

1. 3,256 verdicts on 8,212 cases; 86 % valid and needed; the guard, Policy 2, containment and the launcher are the strongest part.
2. 208 weak functions, in a few early suites. 48 of 119 planted faults passed every test run against them; 24 of those would fail open or lose work, but the code is right today.
3. Three gaps are live today. No round is needed: each rides in a planned ticket (W2-04, W2-57) or is an entry criterion (W2-27).
   - a context packet without a lexical index is silently empty;
   - the path-map checks measure nothing on a real path map;
   - a rulesync timeout silently skips up to 181 cases.
4. Five planned tickets would be refused at their own close unless their ticket files change first: W2-13, W2-14, W2-19, W2-57 and W2-65.
5. Placement saves more than retirement. The serial phase can drop from about 31 to about 11 minutes, mostly by the nested reruns' retirement and the live tests' move to the nightly.

## The decisions, in the order the work needs them

### A. The review point: your confirmation of the drafts, with these packages (the synthesis's section 6)

| # | Package | Recommended | What the draft assumes |
|---|---|---|---|
| 1 | **P-IS-1** W2-66's shared core and couplings | (a) widen now (`cli/main.py`, `errors.py`, the eight retrieval modules, W1-07's contract files on every close), measure in the nightly later | `01`, `02` |
| 2 | **P-IS-2** the record-reading set | (a) one rule (every test reading a declared record-only path), a first list, DEC-891's record-only list exactly, read the gate's `gov check` result | `01`, `02`, `03` |
| 3 | **P-IS-3** the nested reruns | (a) retire W1-05's switch-over and W1-47's builder rerun now; W2-67 bounds the 15 unit nested runs; then re-measure worksteal | `04`; the retirements in a small new ticket, **W2-70** (LITE, independent test designer, one commit plus the `serial-only.txt` line). It merges early and closes once W2-07's revision class is pinned |
| 4 | **P-IS-4** W2-07's KPIs | (a) the commit gates first, stopping before any test; the W1-30 cases named | `06` |
| 5 | **P-IS-5** three ticket-file corrections before the first re-pin | (a) W2-65's paths gain the hook's second copy and W1-29's file; W2-69 names W2-50's scale cases and takes W2-L373's rename; W2-66's file names the test map | `08` |
| 6 | **P-IS-6** W2-57's ticket file | (a) the two tables; paths widened; the probe's four effects first; the live-case KPI replaced by the nightly move. **You choose** for the two p95 entries (W1-02, W1-05): keep them as declared second tries, or remove them | `05` |
| 7 | **P-IS-7** where the test revisions go | (a) files an open ticket holds ride in it; everything else goes to W2-67 | `04` |
| 8 | **The re-pin plan** | Two re-pins: the first carries W2-58, W2-59, W2-65, W2-66, W2-07 and W2-69; the second W2-68 | `07` |

### B. They gate other tickets' starts (not the review point; you can decide them later)

- **P-IS-8:** W1-42's two accepted reds. They gate W2-13, W2-14 and W2-19, and I2 and I3 disagree.
- **P-IS-9:** the path-map rule in adopted projects (W2-27, W2-22, W2-23).
- **P-IS-10:** Policy 2 (c)'s base branch, which is written into the guard (W2-27, W2-29, Wave 3).
- **P-IS-11:** DEC-769 item 3 (W2-21).
- **P-IS-12:** CAP-15's synthesis notes and W2-04's entry criteria (W2-04).
- **P-IS-13:** DEC-833's line of 85 (W2-32).
- **P-IS-14:** the A5 record type (W2-52, EXAMIN's A5).

### C. The rest

- **P-IS-15:** the retirements. One owner decision each (DEC-889 item 16 d); the synthesis's table 5.1.
- **P-IS-16:** DEC-281's context threshold of 0.30.

### Also open from today

- **DEC-898's figures:** 100 GiB and 10,000,000 inodes as the floor; 30 GB and 2,000,000 per auditor, trial or research session; 20 GB and 1,000,000 per lead. They are in force provisionally until you confirm them.
- **Area 4's resume:** recommended no. The nightly full run supplies the missing run evidence, and any red or flaky result in area 4's suites comes as an addendum.

## What I do once you answer

- I record your answers (one DEC entry per group).
- I commit the confirmed drafts, each ticket file in its own commit with its Task (DEC-896).
- I create W2-70 if P-IS-3 (a) is taken.
- I start W2-66 and W2-07 in the first slots, and W2-69 in the next.



---

# 2. Lens I's packages P-IS-1 to P-IS-7, in full

*Source: `docs/assessment/2026-10/I-SYNTHESIS.md, section 6`*

### P-IS-1. W2-66: what widens a scoped close to a full run, and the couplings the map must name
*Merges I4 F12 and §4.1; I3 §4.1; I2 §4.1; I1 §4.1; the tool trials.*

1. **Context.**
   - W2-66 makes a close run the ticket's own suite, the unit tests, and the suites of every ticket whose allowed paths overlap the change. A change to the **shared core** runs everything (DEC-880 item 2 (a)).
   - The lists live in a test map of their own (DEC-896 item 2).
   - The owner already added the three widest-reaching modules (DEC-892 c). DEC-889 item 1 asks for named paths for "the retrieval core" and for test-side imports.
2. **What happened.**
   - `src/gov/cli/main.py` runs under 30 suite folders and `errors.py` under 59, yet neither is shared core. A change to the envelope or the exit codes selects only W1-07 and W1-46 (I4 F12).
   - W1-07's three contract files run every command. They execute 45 modules outside both W1-07's paths and the shared core (I4 §4.1 item 1).
   - The retrieval core's wide modules are eight: `src/gov/retrieval/{__init__, chunking, lexical, semantic, ollama, rerank, fusion, retrieve}.py`, each reached by 12 to 25 suites (I3 §4.1 item 1).
   - Several couplings are invisible to imports and to coverage: text reads, a separate process, two hook copies, fixture inputs, W1-28's file scan, the CLI and the network (§4, W2-66 block).
   - In the trials, the declared map caught all 32 planted faults. In the three widest modules, though, it selected only 10 to 46 % of the catching tests (the tool trials).
3. **Why it matters.** A selection that misses a red passes a close that should be refused; the nightly finds it within a day (DEC-880 (c)). Faster closes must not cost safety.
4. **Options.**
   - **(a) Widen now, measure later.**
     - `src/gov/cli/main.py` and `errors.py` join the shared core until measured.
     - The retrieval core is named as its eight modules.
     - W1-07's three contract files run on every close: about 335 case-seconds once P-I4-1 to P-I4-3 are taken, under a minute of wall time.
     - Every coupling of §4 is written into the test map.
     - Cost: a full run for changes to the CLI's entry (few tickets touch it), and about a minute per scoped close. Changes: W2-66's card and the test map; nothing in the Contract.
   - **(b) Measure first.** Lens H's planted-fault method on `main.py` and `errors.py`, as was done for DEC-892 c, before deciding; the nightly covers the gap meanwhile. Cost: one trial. Risk: a miss is found a day late.
   - **(c) All of `src/gov/cli/**` is shared core.** Cost: more full runs. Risk: little.
5. **Classification:** I4 F12, "Ordinary work: yes; Consequence: other (a red found by the nightly)". I would say "fails open, bounded by the nightly", for the reason given in P-IS-2. Either way it is a W2-66 matter, not a round.
   **Recommendation: (a)**, with (b)'s measurement in the nightly afterwards. Confidence: medium.
6. **What it blocks.** W2-66's test design (DEC-881, DEC-889 item 14). Waiting costs nothing until its tests are written.

### P-IS-2. The record-reading set, for W2-66 and W2-68
*Merges P-I2-2, I3 F5 and R5 (a), I4 F6, and I1's rows.*

1. **Context.**
   - DEC-883 item 3 lets a passing run stand for a later head with the same code fingerprint; the fingerprint leaves record-only paths out.
   - DEC-889 item 2 therefore runs a declared set of record-reading tests on every head. It starts from gate (f)'s four files, W2-54's green-here cases, W1-33's definitions and W1-49's window.
   - W2-66 builds the set; W2-68 builds reuse (DEC-890).
2. **What happened.** Three reports found record readers outside the set:
   - **area 2:** W1-48 (172 cases: the registry and the register's approvals), W1-26's two probe-record cases, W1-40's registry cases, W1-42 (24 cases), W1-30's r11 file (I2 F6);
   - **area 3:** W1-10's register case and its ticket-and-ADR completeness case (I3 F5);
   - **area 4:** W2-02's green-here (625 files read), W1-08's ticket, probe and floor cases, six W1-06 files, W1-07's config cases, W1-09's vendoring, W1-27's doctor files, W1-33's roster, W1-44's lessons, W1-38 and W1-39 (I4 F6);
   - **area 1:** W1-01's ticket-file test, proposed for retirement (I1 §4.1).
   - **Which tests need the set depends on which paths W2-66 declares record-only.** DEC-891's list is `.tickets/`, `docs/checkpoints/`, `docs/close/`, `docs/probes/`, the register, the plan files and `governance/project/orchestration/`. It leaves out the tool registry, the path map and `docs/lessons/`, so tests that read only those are fingerprinted as code and run fresh on a change (my reading of DEC-891; I1 §4.1 reasons the same).
   - W2-54's green-here fixture runs `gov check` on the repository, 5 to 6 minutes, after the pre-close gate has already run it (I3 F15, R5).
   - All three record reds of 2026-10-21 came from record-only commits (lens H finding 18).
3. **Why it matters.** Under reuse, a record-only commit can turn a test red while a close cites a passing run. That is a close passing on a red head.
4. **Options.**
   - **(a) One rule, and a first list.**
     - Every test that reads a declared record-only path, directly or by scanning the tree, is in the set.
     - W2-66's card lists the set now, from the four reports, filtered by that rule.
     - The record-only list is DEC-891's, exactly.
     - The set reads the pre-close gate's own `gov check` result instead of recomputing it (I3 R5 (a), about 20 lines).
     - Cost: minutes per head. Changes: W2-66's and W2-68's cards; DEC-889 item 2's list widened.
   - **(b) As (a), with a `repository_state` marker** that test designers set (lens H P-H-9; I4 F6), seeded with (a)'s list. Cost: marking a few hundred functions. Risk: a forgotten marker.
   - **(c) Map record paths to suites in the test map** and widen on them (P-I2-2 (b)). Risk: a missed path fails open.
   - **(d) Keep the set as decided** and rely on the nightly. Risk: a close passes on a red head for up to a day (lens H P-H-9 (b)).
5. **Classification:** I2 F6 and I3 F5, "Ordinary work: yes; Consequence: fails open, feature-gated" (an entry criterion of W2-66's set and of W2-68). I4 F6, "Ordinary work: yes; Consequence: other (found late)". I side with I2 and I3: the nightly bounds how long a red head goes unseen, but the reused close has already passed.
   **Recommendation: (a)**; take (b)'s marker as the mechanism if W2-66's design prefers it. Confidence: high for the rule; medium that the first list is complete.
6. **What it blocks.** W2-66's test design, and W2-68's start. Waiting costs nothing before W2-66's tests are written.

### P-IS-3. Retire the two nested reruns now; bound the unit nested runs; then re-measure worksteal
*Merges P-I1-5, I2 F5, the tool trials (trial b), DEC-892 a.*

1. **Context.** DEC-889 item 7 gives the nested reruns to W2-67, after W2-66. DEC-892 a keeps worksteal out of the close, the nightly and the leads until they are removed.
2. **What happened.**
   - W1-05's switch-over case re-runs W1-02, W1-03 and W1-04 (4,355 cases) in a child process: 874 s alone, 47 % of the serial phase, 14.6 minutes of every close. Its KPI was a one-time order at W1-05's close (I1 F-5).
   - W1-47's builder case re-runs `tests/unit/guard`. It took 78 s, and timed out at 300 s under worksteal (I1 F-5).
   - 15 unit close functions start a nested pytest with a 60-second limit. Five to nine of them failed under worksteal in the trials; none failed in their own suite in I2's six runs (I2 F5).
   - Worksteal saved 9 % in the trial, inside one run's noise, and every trial run was shuffled by pytest-randomly (the tool trials).
3. **Why it matters.** About 15 minutes of every close's quiet window, worksteal blocked, and leads re-running both.
4. **Options.**
   - **(a) Now:**
     - retire both acceptance reruns in one test-designer commit, and remove the switch-over line from `serial-only.txt`;
     - in W2-67, the engineer bounds the 15 unit cases;
     - then worksteal is re-measured in the nightly, in file order.
     - Cost: one commit, and a small builder-test change. Changes: W2-67's card; DEC-892 a's condition is met in two steps.
   - **(b) Wait for W2-67.** Cost: about 15 minutes per close until then.
   - **(c) Move both reruns to the nightly only.** They still block worksteal there.
5. **Classification:** I1 F-5, "Ordinary work: yes; Consequence: other". I2 F5, "Ordinary work: yes; Consequence: other (fails closed)". No round.
   **Recommendation: (a).** Confidence: high.
6. **What it blocks.** Worksteal (DEC-892 a). Waiting costs about 15 minutes of every close.

### P-IS-4. W2-07: stop on commit findings before any test runs; name the cases it changes
*Merges I2 F13 and F9, I4 F14 and F17.*

1. **Context.** W2-07 moves forward to sit with W2-66 and rides the first re-pin. Its KPIs: decision records measured by their decision; test-revision tickets judged on their declared `acceptance_tests.path`; a stale probe named before the run (DEC-896 item 3). DEC-868 puts a fast gate inside the close, before any test.
2. **What happened.**
   - On 2026-10-22, W2-50's and W2-58's closes ran their full regression and serial phase (about 70 minutes each), then refused on commit findings: a stale probe, a ratchet entry that did not count, and work without a task. Each was knowable from the commits alone (I2 F13; I4 F14, F17).
   - The orchestrator's gates (a) to (h) now predict most of these (DEC-896 item 4). They do not run the ratchet's reading of the two lists (I4 F14).
   - W2-07 will turn named W1-30 cases red: `test_w1_30_no_acceptance_tests.py` and the collection-error cases (I2 F9).
3. **Why it matters.** Each such refusal costs a quiet window and a count. A ticket that lands without naming the tests it changes meets a red in its own close.
4. **Options.**
   - **(a) Add to W2-07's KPIs:**
     - the close runs its commit gates first (trailers, task-less work, accepted history, the probe gate, the ratchet's reading of its entries), and stops before any test when one refuses, spending no attempt (DEC-868 item 3);
     - name the W1-30 cases for its test designer, and the unit case for its engineer.
     - Meanwhile, the orchestrator adds the ratchet's reading to its pre-close gates under DEC-895's standing rule (no decision needed).
     - Cost: small. Changes: W2-07's card.
   - **(b) Rely on the orchestrator's gates (a) to (h)** and name only the W1-30 cases. Risk: the gates live in scratch scripts, not in the product that adopted projects receive.
   - **(c) Defer.**
5. **Classification:** I2 F13, "Ordinary work: yes; Consequence: other (fails closed)". I2 F9, "Ordinary work: yes; Consequence: other". No round.
   **Recommendation: (a).** Confidence: medium-high.
6. **What it blocks.** W2-07's card at the review point. Waiting risks another refused close spent before a commit finding shows.

### P-IS-5. The first re-pin: three ticket-file corrections before it
*Merges I3 F4; I1 P-I1-7 and I2 F8 (for W2-69); DEC-896 item 2 (W2-66's file); P-I1-2 (the settings regeneration).*

1. **Context.** The first re-pin carries W2-58, W2-59, W2-65, W2-66 and W2-07 (DEC-896 item 3), and W2-69 (DEC-897). The owner regenerates the settings after it (DEC-884).
2. **What happened.**
   - **W2-65 cannot make its own change without refusing its own close.** W1-29's hook cases run the copies in `src/gov/hooks/`, and `TestHookCopiesIdentical` requires each to equal the template's copy. W2-65's paths hold the template's `subagentstop.py` only, so its fix turns that test red. W1-29's SubagentStop case also accepts the undocumented form the fix removes (I3 F4; checked in `DAEO-e82f.md`).
   - **W2-69 names no earlier test it may change.** It changes what the secrets check scans. I1 expects W2-50's scale cases to be revised with it (P-I1-7), but its paths do not hold `tests/acceptance/W2-50/**`. It does hold `tests/unit/secrets/**`, the folder that shadows the standard library (I2 F8; row W2-L373).
   - **W2-66's ticket file still names the path map,** not the test map (DEC-896 item 2; `DAEO-c1uz.md`).
   - **P-I1-2:** the `docs/source` read deny rules protect a folder that left the tree on 2026-10-01. Removing them is a settings change, which could ride the regeneration after the re-pin.
3. **Why it matters.** A ticket in the re-pin that is refused at its own close delays the re-pin for everyone.
4. **Options.**
   - **(a) Correct the three files now:**
     - W2-65's paths gain `src/gov/hooks/subagentstop.py` (kept identical to the template) and `tests/acceptance/W1-29/test_session_hooks.py`, for its test designer (`Rewrite-Reason: DEC-889 item 8`);
     - W2-69 names the W2-50 cases its change affects, for its test designer, and takes W2-L373's rename (its paths gain the new folder name);
     - W2-66's file names the test map;
     - the regeneration carries P-I1-2's removal if the owner takes it.
     - Cost: three ticket-file edits. Changes: those files; the settings only if P-I1-2 is taken.
   - **(b) Leave W2-65 as it is,** and handle the red in its close: a repair round.
   - **(c) Take W2-65 out of the first re-pin.**
5. **Classification:** I3 F4, "Ordinary work: yes; Consequence: loses work" for the hook (decided by DEC-889 item 8). For W2-65's scope, "other (fails closed)": an entry criterion of W2-65 (DEC-803), not a round.
   **Recommendation: (a).** Confidence: high for W2-65 and W2-66; medium for W2-69, whose effect on W2-50's cases its design will show.
6. **What it blocks.** W2-65's and W2-69's work toward the re-pin. Waiting costs a refused close and a repair round.

### P-IS-6. W2-57's ticket file: the serial-only list, `load_sensitive`, and a route out for every entry
*Merges P-I2-1 B and C, P-I4-5, P-I1-8, I3 O3; I1 F-1, F-2, F-7, F-10, F-14; I2 F10, F12, F14; I3 F6, F7, F8; I4 §4.2.*

1. **Context.**
   - W2-57 takes load out of the close and fixes the `load_sensitive` entries. It must close before W2-24 (DEC-813).
   - Its first item is the rulesync probe (DEC-892 item 2).
   - DEC-889 item 5: latency tests stay alone; W1-16's daemon tests and W1-09's races are tried in parallel; live and real-model tests move to the nightly.
   - Its ticket file comes at the review point. The lists only shrink, and every entry names its fix (DEC-762, DEC-766).
2. **What happened.**
   - **Its card contradicts DEC-889 item 5** on W1-46's live cases (I2 F14).
   - **Its planned paths cannot reach four of its entries** (W1-38 ×3, W1-07's `[doctor]`), nor the list it must change (I2 F12).
   - **The probe's limit reaches 40 W1-38 cases, not 3,** and its timeout turns into a silent skip (I4 F2).
   - **26 of the 32 entries name cases the close already runs alone,** so for them an entry is a second try under the same condition (I2 F14).
   - **The serial phase** holds 55 entries and 263 cases, 30.7 minutes:
     - live and real-model files (I3 F6);
     - W1-16's 94 cases that start no daemon, which passed three times in parallel (I3 F7);
     - W1-09's two races, which pass in parallel and still catch their planted faults there (I4 §4.2);
     - W1-05's nested rerun (I1 F-5);
     - true latency cases, which fail on any loaded machine and pass on a quiet one (I1 §2.6; I2 §2.3; I3 F8).
   - **W2-58's five launched sessions** run in the parallel phase, on neither list (I1 F-2).
3. **Why it matters.** This is where most close time goes, and where most refused closes came from.
4. **Options.**
   - **(a) W2-57's ticket file as the two tables below,** with:
     - its paths widened as in §4 (W2-57 block);
     - its first item widened to the probe's four effects (P-I4-5 (a));
     - its live-case KPI replaced by the nightly move (P-I2-1 C).
     - Cost: a larger first item (one fixture, one helper, three functions' assertions), and two small probe fixes. Changes: W2-57's card and ticket file; the serial-only list; the nightly's set.
   - **(b) As (a), and add the 27 red-on-timeout W1-38 cases to `load_sensitive` now** (P-I4-5 (b)). Cost: one owner commit, validated under DEC-895. Risk: the list grows past what W2-57 will remove.
   - **(c) W2-57 as drafted under DEC-813.** Risk: its KPI fights a later owner decision; four entries cannot leave; the silent skip stays.
5. **Classification:**
   - I4 F2: "Ordinary work: yes; Consequence: fails open" (the silent skip).
   - I2 F12 and F14, I1 F-1, F-2, F-7, F-14, I3 F6, F7, F8: "Ordinary work: yes; Consequence: other".
   - No round: the fixes ride in W2-57, a planned ticket (DEC-802).
   **Recommendation: (a).** Confidence: high for the probe and the paths; medium for keeping the two p95 entries (I1 and I2 differ, §7.1).
   - **An interim guard, mine:** until W2-57 lands, the orchestrator's queue checks that a close's skip count equals the expected 31, so a silent skip stops the queue. It is a few lines of glue with no product change; it rests on I4 F2's record of 31 skips in every close since 2026-10-20.
6. **What it blocks.** W2-57's start, and through it W2-24 (DEC-813). Waiting costs a refused close each time one of the 27 unlisted W1-38 cases meets the limit, and leaves the silent skip in place.

**The serial-only list after (a):**

| Entries | Now | After | Source |
|---|---|---|---|
| W1-05's switch-over case | Serial, 874 s | Retired (P-IS-3) | I1 F-5 |
| W1-46's live file; W1-50's two live freeze cases | Serial | The nightly | I1 §4.2; DEC-889 item 5 |
| W1-19's real-model file, W1-21's dev-tier file, W1-49's live file, W1-25's live file | Serial, 208.8 s | The nightly (W1-25's file retired if R4 is taken) | I3 §4.2 |
| W2-58's five launched sessions; W2-62's live resume; W2-54's sandboxed worker and real embedder; W1-21's family check | Parallel, on neither list | The nightly (or serial until then) | I1 F-2; I3 F6 |
| W1-16: the 94 cases that start no daemon | Serial, 35.5 s | Parallel | I3 F7 |
| W1-16: the 67 daemon cases; W1-20's 10 daemon cases | Serial, 599 s | Stay; W1-20's tried in parallel later | I3 F7, §4.2 |
| W1-09's two race cases | Serial, ≈ 14 s | Parallel, after one green nightly there | I4 §4.2 |
| W1-50's read-merge latency case | Serial, 0.3 s | Parallel | I1 §4.2 |
| W1-02 and W1-05 p95; W1-15's bound; W1-07's help; W1-10, W1-17, W1-18 latency cases | Serial | Stay alone | I1 §2.6; I2 §2.3; I3 §4.2; I4 §4.2 |

**Every list entry's route out** (32 in `load_sensitive`, 2 in `accepted_reds`):

| Entry (count) | `fixed_by` | Verdict on the test | Route out | Source |
|---|---|---|---|---|
| W1-42 RETR-X-02 (1, accepted red) | W2-13 | ⚑ obsolete (I3); valid, a known red (I2) | P-IS-8 | I2 F1; I3 F1 |
| W1-42 governance share (1, accepted red) | W2-14 | The same | P-IS-8 | The same |
| W1-02 p95 (1; 5 cases) | W2-M332 | Flaky: machine load | Stays serial. Its entry stays as a declared second try, or leaves (owner); W2-M332 dated before W2-24 (DEC-890) | I1 §4.3; I2 F14 |
| W1-05 p95 (1; 9 cases) | W2-M332 | Flaky: machine load | The same | The same |
| W1-19 warm p95 (1) | W2-M332 | Flaky: a busy machine; green in 11 of 11 close records | Leaves when its file moves to the nightly (orchestrator's removal, DEC-861) | I3 O3; I2 P-I2-1 C |
| W1-46 live (23: 6 setup, 17 hosts) | W2-M364 (W2-57 by DEC-813) | Flaky: setup under load; the hosts fail on the network, even alone | Leave when the file moves to the nightly. Meanwhile the 17 host entries' reason names the network (P-I1-8 (b)) | I1 F-1, P-I1-8; I2 F10, F14 |
| Unit close follow-up (1) | W2-L352 | Not reproducible: 6 green runs | Leaves with W2-57's list work (a removal) | I2 §2.2, F10 |
| W1-30 r13 (1) | W2-M384 (W2-57 by DEC-823) | Flaky: its own 5-second limit | Leaves when W2-57 revises its timing | I2 §2.2 |
| W1-38 rulesync (3) | W2-57 | Flaky: the 10-second probe | Leave when W2-57's first item closes, with the paths widened | I2 F12; I4 F2; P-I4-5 |
| W1-07 `[doctor]` (1) | W2-57 | Not reproducible: 12 green runs | Leaves when W2-57 closes, with the paths widened; failure text kept so the cause shows next time | I2 F12; I4 F5 |

### P-IS-7. One home for the test revisions, and what that home waits for
*Merges P-I2-3, I3 §4.5 (T-A3), I4 §2's carriers, lens H P-H-5; DEC-892 item 1; P-I1-6.*

1. **Context.** No test is changed by the review. Revisions go to independent test designers (acceptance tests) or engineers (builder tests), each with a `Rewrite-Reason:`, in the owning ticket or a small new one (DEC-889 item 16 d). W2-67 (test hygiene) follows W2-66 (DEC-889 item 7).
2. **What happened.**
   - 277 weak or outdated functions need a home. Well over a third sit in files that an open ticket already holds; the rest are in closed suites (§5.2, my count).
   - The reports propose three homes:
     - I2: widen W2-67 by about 55 acceptance and 15 builder cases, 600 to 900 lines (P-I2-3);
     - I3: its own small LITE ticket, T-A3, with 42 rows and 4 to 5 hours of work, or folded into W2-67 (§4.5);
     - I4: the open ticket that holds each file (W2-11, W2-34, W2-64, W2-57, W2-65), else small per-suite tickets or W2-67 (§2.2).
   - **Two constraints.**
     - A ticket that only revises other tickets' acceptance tests can close only once W2-07's test-revision class lands (I4 §2; DEC-892 item 1). W2-63 waits on the same rule.
     - Once DEC-769 item 3 is built, a designer writes only the folders its ticket names (P-IS-11).
   - Builder tests are the engineer's (DEC-042). Several weak unit cases sit in folders that open tickets already hold: `tests/unit/hooks/**` (W2-65), `tests/unit/containment/**` (W2-44), `tests/unit/codeintel` (W2-37 once widened), `tests/unit/context/**` (W2-04).
3. **Why it matters.** Without a named home, a weak case keeps passing until a gate breaks unseen.
4. **Options.**
   - **(a) Two homes by kind.**
     - Revisions of files an open, planned ticket already holds ride along in that ticket (DEC-802): §5.2's carrier column.
     - Everything else goes to W2-67's card, which takes T-A3's list and I4's small-ticket items.
     - W2-67 is planned to close after W2-07 lands.
     - Cost: W2-67 grows by roughly 150 to 200 functions (my count from §5.2), most of them one fixture line and one assertion each; I2 puts its own share at 600 to 900 lines of test code. Changes: W2-67's card and the cards of the riding tickets.
   - **(b) As (a), but T-A3 as a separate small ticket for area 3,** beside W2-67. Cost: one more ticket. Benefit: smaller reviews.
   - **(c) Wave 3's hygiene pass.** Risk: the weak cases keep passing for a wave, while W2-11, W2-22 and W2-52 change the code they claim to guard.
5. **Classification:** I2 F2, F3 (for the tests), F4, F5, F7, F8, F9; I3 F3 (for the "other" gaps); I4 F7, F10, F16: "Ordinary work: yes; Consequence: other". For the gaps of §3.3: "fails open" or "loses work", latent. No round: they ride along or wait in planned hygiene work.
   **Recommendation: (a).** Order the weak cases that guard code a planned ticket will change first: doctor (before W2-22, W2-18, W2-09), the skills (in W2-11), adoption's A8 (before EXAMIN). Confidence: medium-high.
6. **What it blocks.** W2-67's card. Waiting costs about 1.4 minutes of every close on cases that cannot fail, and the risk that a gate change passes on a weak case.



---

# 3. The p95 question

*Source: `docs/assessment/2026-10/I-SYNTHESIS.md, section 7.1 and P-IS-6`*

**The question (yours, P-IS-6):** do W1-02's and W1-05's p95 `load_sensitive` entries stay as declared second tries until W2-M332 (with its date), or does the orchestrator remove them now? The synthesis gives no recommendation; it puts this to the owner.

**Where the reports disagree (the synthesis, section 7.1):**

| Question | One report, and its evidence | The other, and its evidence | My reading |
|---|---|---|---|
| W1-02's and W1-05's p95 `load_sensitive` entries | I1: still justified. They fail whenever the machine is loaded, pass on a quiet one, and the entry is the net if the quiet window breaks (§4.3) | I2: the entry adds nothing while the case runs serially; it is a second try under the same condition, a narrow fail-open for an intermittent latency fault (F14) | Both measured the same behaviour. Keeping or dropping the two entries is the owner's call (P-IS-6). The fix is W2-M332 with a date |

**The two entries (the synthesis, P-IS-6's route-out table):**

| Entry (count) | `fixed_by` | Verdict on the test | Route out | Source |
|---|---|---|---|---|
| W1-02 p95 (1; 5 cases) | W2-M332 | Flaky: machine load | Stays serial. Its entry stays as a declared second try, or leaves (owner); W2-M332 dated before W2-24 (DEC-890) | I1 §4.3; I2 F14 |
| W1-05 p95 (1; 9 cases) | W2-M332 | Flaky: machine load | The same | The same |



---

# 4. The re-pin plan, with its rollback

*Source: `drafts/review-bundle/07-REPIN-PLAN.md`*

## The re-pin plan (DEC-889 item 15, as amended by DEC-896 and DEC-897), for the owner's review

**Today's pin:** `fecb870c` (`~/.local/share/gov-os/pin-fecb870c/`). It predates W2-50's merge and W2-58. Every close is judged by it: `gov close`, `gov check` and the guard hooks. A fix on `w2/integrate` reaches a close only through a re-pin.

## The first re-pin

- **It carries:**
  - W2-58 (Policy 2);
  - W2-59 (the hooks and declared checks run from the pin);
  - W2-65 (hook lines fail closed);
  - W2-66 (scoped selection and evidence);
  - W2-07 (the close by ticket class; the commit gates first);
  - W2-69 (the secrets check reads what the stores hold).
- **Order of work before it:**
  1. **W2-66 and W2-07**, side by side, each to its FULL or STANDARD ladder. W2-66 also passes its fixture trial.
  2. **W2-69** in a free slot, now that W2-50 is closing. Its tests decide the design question (DEC-897).
  3. **W2-65**, stacked on `w2/W2-59` (built in a free slot), after the P-IS-5 correction to its paths.
  4. **Just before the re-pin, W2-59 and W2-65 merge together.** Each first merges `w2/integrate` back with trailers and is re-verified (DEC-884). An earlier merge of either still needs a package first.
  5. `tools/probe_impact.py` after every merge (DEC-895). A FULL ticket whose probe went stale gets its fresh probe before the re-pin.
- **The owner's acts, in order** (one ACT ping, with the exact commands and their checks):
  1. **The re-pin itself:** build the wheel at the merge commit that holds all six, install it under a new pin folder named for that commit (as `pin-fecb870c` is for today's), and point `~/.local/bin/gov` at it.
  2. **The settings regeneration** (DEC-884). If P-I1-2 is taken, it drops the `docs/source` read-deny rules, which protect a folder that left the tree on 2026-10-01.
  3. **A smoke run** of the pinned `gov check` and one guard decision, which I run and report.
- **What it changes for the closes:**
  - closes become scoped (W2-66);
  - decision-record commits count as measured (W2-07);
  - the commit gates refuse within minutes;
  - DEC-897 (b)'s re-run exception ends (W2-69).
  The merged-not-closed tickets close in the queue after it: W2-58, W2-63 (on W2-07's revision class), and any held this way. Under DEC-896 item 4, nothing closes before it unless gates (a) to (h) all predict a pass.
- **Rollback:** the old pin folder stays. Re-pointing `~/.local/bin/gov` at `pin-fecb870c` restores today's judge in one command.

## The second re-pin

- **It carries W2-68** (batching, reuse, the two fingerprints), after its FULL review and its trial (DEC-884 item 4), and whatever else has merged by then.
- **From it on,** queued closes run as batches, and a close on code that already passed reuses its run (DEC-883).

## What waits for which re-pin

| Waits for | Item |
|---|---|
| The first | W2-58's and W2-63's closes; the end of DEC-897 (b); scoped closes; the commit gates in `gov close` |
| The second | Batched closes; reuse; the store fresh by code fingerprint |
| Neither | The nightly full run (now, as a script); W2-57 (its close is judged by whichever pin is current); W2-67 (after W2-66 merges; closes after W2-07 is pinned) |



---

# 5. DEC-898's figures (committed as 17515bba; the figures provisional until confirmed)

*Source: `docs/DECISION_REGISTER.md, DEC-898`*

### DEC-898 — The resource gate checks free disk space and free inodes; every auditor, trial and lead has a scratch budget, cleans up as it goes and reports its scratch size
- **Status:** ACCEPTED (owner, 2026-10-22, in the chat, standing; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`). The rule is the owner's. The figures in items 1 and 2 are the orchestrator's proposal, in force provisionally until the owner confirms or changes them. They are stricter only. · **Under:** DEC-798, DEC-847, DEC-880, DEC-889 item 16, DEC-855, DEC-851, DEC-861 · **Basis:**
  - **Lens I area 4's folder** (`/tmp/gov-os-assessment-I4/`) held about 7.0 million files and folders (61 GB). About 5.3 million files (46 GB) were in `tmp/bt/`: from 18:31 to 19:04 that auditor gave each planted-fault run its own pytest base folder, which skips pytest's clean-up of old folders, and the suites it ran make whole-tree copies per test.
  - **The disk's inodes reached 98 % use.** One run could not write its result (ENOSPC).
  - **Before the orchestrator's clean-up of the four lens I folders** (about 20:15): 62,589,143 of 67,108,864 inodes used (94 %); 640 GB of 1,007 GB used (67 %).
  - **After the clean-up** (20:30): 45,983,305 inodes used (69 %); 486 GB used (51 %). The cited evidence folders were kept.
- **Decision:**
  1. **The resource gate checks free disk space and free inodes.**
     - It refuses a launch, a trial or a close when the shared disk has less than **100 GiB free or fewer than 10,000,000 inodes free**.
     - Until W2-20 builds this into `gov launch` and `gov close`, the orchestrator's `tools/disk_gate.sh` does it, in the same command as each launch and inside `close_queue.sh`, `nightly.sh` and `tooltrials.sh`.
     - W2-20's ticket gains the KPI. Its gate counts every Gov OS session on the machine, as before.
     - `gov close`'s call to the same reading goes to W2-07's or W2-66's card (the review bundle), because their paths hold the close and W2-20's do not.
  2. **Every auditor, trial, research and lead brief gets a scratch budget:** size, and the number of files and folders.
     - **The budgets:**
       - an auditor, trial or research session: **30 GB and 2,000,000** in its own folder;
       - a lead with all its workers: **20 GB and 1,000,000** outside the tracked tree (its worktree's untracked and ignored files, and its own temp folder);
       - the nightly run: **30 GB and 2,000,000**.
     - **How a session keeps to it:**
       - it sets `TMPDIR` to a folder of its own (where the sandbox sets one, it keeps that one);
       - it keeps pytest's own retention of three base folders, never a per-run `--basetemp`;
       - it removes its clones, worktrees and temp trees as it goes, not only at the end;
       - it measures its scratch (`du -s --inodes` and `du -sh` of its folders) before every heavy run and at the end, and reports the figures in its return's `evidence` line.
  3. **A scratch that passes its budget stops that session's heavy work at once.**
     - The session cleans what it can and returns at once: a lead as PACKAGES, an auditor or trial as PARTIAL, with the measure and the cause.
     - **The orchestrator then pings the owner** (P1). Leads and workers never ping (DEC-855); the orchestrator's ping is the owner's notice.
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §3 (the resource gate), §4 (the launch form), §15 (the gate by hand, the closes, the nightly run and the trials), v3.18;
  - RESUME HERE;
  - `governance/project/briefs/LEAD-w2-common.md` (leads and their workers);
  - `governance/project/briefs/AUDITOR-common.md` (W2-25's, W2-28's, W2-30's and W2-47's auditors) and every lens, trial and research brief the orchestrator writes;
  - W2-20's ticket file and card (the KPI; its own commit with `Task: DAEO-r30l`, DEC-896);
  - the orchestrator's `disk_gate.sh`, `close_queue.sh`, `nightly.sh` and `tooltrials.sh`.
- Next free id: DEC-899.



---

# 6. W2-66: the ticket file

*Source: `drafts/review-bundle/01-W2-66-ticket.md`*

```yaml
id: DAEO-c1uz
status: open
deps: []
links: []
created: 2026-10-21T07:33:34Z
type: task
priority: 0
assignee: engineer
external-ref: W2-66
tags: [wave-2, close, regression, selection, keystone-2]
wbs_id: W2-66
title: 'Path-scoped regression at close: selection and evidence (the lite W2-38)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/select.py
- src/gov/close/nightly.py
- src/gov/close/evidence.py
- src/gov/close/command.py
- governance/project/test-map.yaml
- template/governance/kernel/schemas/test-map.schema.json
- template/governance/project/test-map.yaml
- tests/unit/close/test_select*
- tests/unit/close/test_nightly*
- tests/unit/close/test_evidence*
- tests/acceptance/W1-30/test_w1_30_regression*
- docs/research/W2-66-scoped-close.md
kpis:
  success:
  - 'A close runs the ticket''s own acceptance suite, tests/unit, and the acceptance suites of every ticket (Wave 1 and Wave 2) whose allowed_paths overlap a file changed since the last fully green commit (the base, so record-only commits between closes are inside the scope), following test-side imports of shared helpers (such as w1_07_support, imported by 14 suites); it selects in the full run''s form (pytest tests --ignore=...), so W1-35''s collection holds; the close record names each suite and why it was chosen [DEC-880 item 2, DEC-889 item 1, DEC-890 item 1]'
  - 'Any change under the shared core runs the full regression. The shared core is one list in the test map: src/gov/close, src/gov/guard, src/gov/check, src/gov/records; the retrieval core as its eight modules (src/gov/retrieval/__init__.py, chunking.py, lexical.py, semantic.py, ollama.py, rerank.py, fusion.py, retrieve.py); both copies of the kernel hooks (template/governance/kernel/hooks/ and src/gov/hooks/); the path map and the test map; the three widest-reaching modules (src/gov/config/loader.py, src/gov/tasks/tickets.py, src/gov/store/loader.py); and src/gov/cli/main.py and src/gov/errors.py until a planted-fault measurement shows a narrower selection catches their faults. A changed file the mapping cannot place, and a test map that is missing or cannot be read, run the full regression too [DEC-880 item 2 (a), DEC-892 c, P-IS-1 (a)]'
  - 'The couplings imports and coverage cannot see are declared in the test map and followed: text reads (W1-42 reads src/gov/cli/main.py and kernel templates; W1-30''s r11 reads serial-only.txt), a separate process (src/gov/retrieval/rerank_worker.py to W1-19''s real-model file, W1-21''s dev-tier file and tests/unit/semantic/test_rerank_process.py), the two hook copies (to W1-29, W1-49, W2-62, tests/unit/hooks; the session-start and PreCompact hooks also to W1-31, W1-37, W1-38, tests/unit/telemetry), fixture inputs (the live path map and the gitleaks configurations, to W1-16, W1-17, W1-19, W1-20, W1-21, W1-22, W1-24 and W2-54; W1-18''s unit-file listing), declared checks to W1-26, and the named lines of the synthesis''s section 4; W1-07''s three contract files run on every close [P-IS-1 (a)]'
  - 'The serial-only tests are scoped by the same selection: a scoped close runs the serial cases of the suites it selected, one at a time, and the record says which [DEC-889 item 1]'
  - 'A declared record-reading set runs on every head, whatever was selected: every test that reads a declared record-only path, directly or by scanning the tree, is in it; the first list is in the test map, from lens I''s four reports filtered by that rule; the record-only paths are exactly DEC-891''s list (.tickets/, docs/checkpoints/, docs/close/, docs/probes/, the decision register, the plan files, governance/project/orchestration/); for context-reproducibility and core-schema the set reads the pre-close gate''s own gov check result instead of running gov check again [DEC-889 item 2, P-IS-2 (a)]'
  - 'The close record''s evidence block states the scope (scoped, full), the base commit, the head, the tree, every suite and case run, every suite left out and why, every skip with its reason and the skip count, the failing tests with their failure text kept, and the run''s JUnit XML file; the schema line is W2-64''s [DEC-889 item 12, DEC-890 item 1, I4 F5]'
  - 'gov close --full runs the full regression and the record says so; W2-24 and W2-46 use it [DEC-880 item 2 (d)]'
  - 'Every test has a per-test time limit (pytest-timeout with the signal method, an owner install package at this ticket''s start), set above the slowest test''s measured time (900 s held in the trial); a test that passes it fails, naming the limit [DEC-889 item 11 b, DEC-892 b]'
  - 'The parallel run''s distribution mode is one setting; it stays the default (no worksteal) until the nested reruns are gone and worksteal is re-measured in the nightly [DEC-892 a, P-IS-3]'
  - 'One command runs the nightly full uncached regression on w2/integrate''s head in the close''s form, with JUnit XML: every failing test is re-run alone; a red that fails alone is a P1 package with git bisect run over the commits since the last green night; a red that passes alone is a flaky candidate; a test that fails there and that a scoped close since the last green night passed or did not run is a P1 package with the test map corrected in it; coverage.py with lens H''s shim writes the measured map weekly [DEC-880 item 2 (c), DEC-852 item 3, DEC-889 items 4 and 12]'
  - 'Measured and reported in docs/research/W2-66-scoped-close.md, on a quiet machine: the time of a typical scoped close (one module outside the shared core and its tests) against the full close, and the selection''s catch rate on lens H''s planted faults, the three widest modules included; the 15-minute target is stated as reached by W2-66 with W2-68, W2-57''s serial rework and worksteal together [DEC-889 item 11 e]'
  - 'The lead''s full verification before every return is unchanged [DEC-880 item 2 (b)]'
  - 'The valid case this ticket turns red is revised by its test designer with a Rewrite-Reason: W1-30''s test_regression_includes_other_acceptance_folders [I2 F9]; W1-01''s MR-3 whole-history test stays in the nightly and every full run'
  failure:
  - A change under the shared core, a change no mapping places, or a missing or unreadable test map runs anything less than the full regression.
  - A scoped close whose record says full; a skip, a left-out suite or a failure the record does not name; a record without its JUnit XML or failure text.
  - A record-reading test outside the set on a head with record-only commits; a record-only path list that hides a code path.
  - A per-test limit that lets a hung test hold the close; worksteal switched on before the nested reruns are gone.
profile: FULL
sources:
- DEC-880
- DEC-726
- DEC-852
- DEC-841
- DEC-881
- DEC-883
- DEC-884
- DEC-889
- DEC-890
- DEC-892
- DEC-896
- DEC-891
est_loc: 400
acceptance_tests:
  path: tests/acceptance/W2-66/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- P-W2-48-8
list_rows: [W2-H044, W2-M153]
```
## W2-66 Path-scoped regression at close: selection and evidence (the lite W2-38)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-66), from DEC-880 item 2, DEC-883, DEC-884, DEC-889, DEC-890 (the split), DEC-892, DEC-896 item 2 (the test map), lens I's synthesis (P-IS-1, P-IS-2) and the owner's review point (DEC-889 item 14).

- **Why:** W2-48's cache, glued to testmon, reused 11.5 % of the tests and saved 3 % of a close (79 min against 81). Per-test tracking made almost every test "always run" here. The measured causes (lens H finding 12, DEC-889 item 11 d):
  - folder listings: 7,076 tests;
  - reads of undeclared files: 3,750;
  - dot-files: 125;
  - child processes the cache could not follow: only about 500.
  The owner withdrew the cache and brought back the lite form of W2-38. A close runs what the change can affect, the full regression stays as the backstop, and the nightly full run catches a miss within a day (DEC-880). Batching, reuse and the fingerprints are W2-68's (DEC-890).
- **Place:**
  - The first slot, once the owner has confirmed this draft at the review point (DEC-889 item 14).
  - Before its test designer starts, the owner settles P-IS-1 and P-IS-2.
  - It shares `src/gov/close/command.py` with W2-07 and W2-57. W2-07 sits beside it (DEC-896); the record's lines here, the gates there.
- **The ladder (DEC-884 item 4, DEC-889 item 15, DEC-896):**
  - its FULL review;
  - a trial of the scoped close on a fixture repository: a planted change in the shared core runs everything; a planted change in one module runs its suites; a record-only commit runs the record-reading set;
  - then the first re-pin (W2-58, W2-59, W2-65, W2-66, W2-07, W2-69).
- **Allowed paths:**
  - new modules:
    - `src/gov/close/select.py` (the selection);
    - `src/gov/close/nightly.py` (the nightly run and its record);
    - `src/gov/close/evidence.py` (the evidence block);
  - `src/gov/close/command.py`: the calls into these, `--full`, and the record's lines only;
  - **the test map (DEC-896 item 2):**
    - `governance/project/test-map.yaml`: the shared core, the couplings, the record-only list and the record-reading set;
    - its schema `template/governance/kernel/schemas/test-map.schema.json`;
    - the template's copy for adopted projects.
    The path map is named by no ticket. The path map's `test_inputs` key (DEC-876 item 2) moves into the test map; its removal from the path map is the orchestrator's record edit.
  - tests and records:
    - `tests/unit/close/test_select*`, `test_nightly*`, `test_evidence*`;
    - W1-30's regression files, for the one revision named above;
    - `docs/research/W2-66-scoped-close.md`.
- **Install (DEC-892 b):** pytest-timeout (the signal method), an owner install package at the ticket's start, into the tool registry.
- **Not in this ticket:**
  - batching, the red batch, reuse and the two fingerprints (W2-68);
  - the serial-only list's rework and the load fixes (W2-57);
  - the commit gates before any test, and the disk gate in the close (W2-07);
  - the test hygiene (W2-67).



---

# 7. W2-66: the card

*Source: `drafts/review-bundle/02-W2-66-card.md`*

#### W2-66 Path-scoped regression at close: selection and evidence, the lite W2-38 (FULL, engineer; DEC-880 item 2, DEC-889, DEC-890, DEC-892, DEC-896; keystone 2)
- **Why:** W2-48's cache saved 3 %, because per-test tracking made almost every test "always run" here. The measured causes were folder listings (7,076 tests), undeclared reads (3,750), dot-files (125) and only about 500 child processes (DEC-880, DEC-889 item 11 d). So a close runs what the change can affect, and the full regression and the nightly run are the backstop. Batching, reuse and fingerprints are W2-68's (DEC-890). Ticket `DAEO-c1uz`; it takes in W2-H044 and W2-M153.
- **Place:** the first slot once the owner confirms this card at the review point (DEC-889 item 14), with P-IS-1 and P-IS-2 settled before its test designer starts. W2-07 sits beside it (DEC-896). Both ride the first re-pin.
- **Allowed paths:**
  - new: `src/gov/close/select.py`, `src/gov/close/nightly.py`, `src/gov/close/evidence.py`;
  - `src/gov/close/command.py`: the calls, `--full` and the record's lines only;
  - **the test map:** `governance/project/test-map.yaml`, its schema `template/governance/kernel/schemas/test-map.schema.json`, and the template's copy (DEC-896 item 2: the path map is named by no ticket);
  - `tests/unit/close/test_select*`, `test_nightly*`, `test_evidence*`;
  - W1-30's regression files (one named revision);
  - `docs/research/W2-66-scoped-close.md`.
- **KPIs, success:**
  - **Selection:** a close runs the ticket's own suite, `tests/unit`, and the suites of every ticket whose `allowed_paths` overlap the change since the last fully green commit. It follows test-side imports, selects in the full run's form, and the record names each suite and why.
  - **The shared core runs everything (P-IS-1 (a)):**
    - `src/gov/close`, `guard`, `check`, `records`;
    - the retrieval core's eight modules;
    - both hook copies;
    - the path map and the test map;
    - DEC-892 c's three widest modules;
    - `src/gov/cli/main.py` and `src/gov/errors.py`, until measured.
    An unplaced file or a missing map also runs everything.
  - **The couplings that imports cannot see** are declared in the test map (text reads, the rerank worker's process, the hook copies, fixture inputs, declared checks). W1-07's three contract files run on every close.
  - **The serial-only tests** are scoped by the same selection.
  - **The record-reading set runs on every head (P-IS-2 (a)):** every test that reads a declared record-only path is in it, from a first list in the test map. The record-only paths are exactly DEC-891's list. It reads the pre-close gate's own `gov check` result.
  - **The evidence block:** scope, base commit, head, tree, what ran, what was left out and why, every skip and the skip count, failure text kept, and the JUnit XML (schema line in W2-64).
  - **The rest:**
    - `gov close --full`, which W2-24 and W2-46 use;
    - per-test limits (pytest-timeout, signal method, above the slowest test);
    - the distribution mode as a setting, with worksteal off until the nested reruns are gone (P-IS-3);
    - the nightly command (failures re-run alone, `git bisect run`, a scoped miss as a P1 with the map corrected, the weekly coverage map);
    - the time measured and the 15-minute target's scope stated;
    - the lead's verification unchanged.
  - **The test designer revises** W1-30's `test_regression_includes_other_acceptance_folders` (a valid case this ticket turns red).
- **KPIs, failure:**
  - less than the full regression for the shared core, an unplaced file or a missing map;
  - a scoped record that says full;
  - an unreported skip, left-out suite or failure;
  - a record-reading test outside the set;
  - a record-only list that hides code;
  - a hung test holding the close;
  - worksteal before the nested reruns are gone.
- **Ladder:** its FULL review; a fixture trial (a shared-core change runs everything; a one-module change runs its suites; a record-only commit runs the set); then the first re-pin (DEC-896).



---

# 8. W2-07: the ticket file

*Source: `drafts/review-bundle/06b-W2-07-ticket.md`*

```yaml
id: DAEO-r9ss
status: open
deps: [DAEO-g0ip, DAEO-zflj, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-07
tags: [wave-2, implementation, standard, close, keystone-1]
wbs_id: W2-07
title: gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-zflj
- DAEO-7rr2
allowed_paths:
- src/gov/close/**
- src/gov/telemetry/**
- tests/unit/close/**
- tests/unit/telemetry/**
- tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py
- tests/acceptance/W1-30/test_w1_30_collection*
kpis:
  success:
  - 'gov close judges a ticket by its class [W2-H045]: an implementation ticket on its acceptance tests; a specification ticket on its closed readiness record and its acceptance tests; an audit ticket on its report and the audit validator; a research ticket on its evidence record; an integration or coordination ticket on its named evidence files'
  - 'A test-revision ticket is judged on the acceptance tests its ticket file names in acceptance_tests.path (another ticket''s folder), not on a folder of its own [DEC-892, DEC-896 item 3]'
  - 'A decision-record commit that changes only governance records (the register, the plan files, the prompts, the briefs, governance/project/orchestration/, the path map) and names an ACCEPTED decision counts as measured for the work-without-a-task gate; a decision-record commit that names no ACCEPTED decision, or changes code, tests or the kernel, still counts as unmeasured [DEC-896 item 1]'
  - 'The commit gates run first, before any test: the trailers, work without a task, accepted history, the probe gate (a stale probe named before the run, W2-M403), and the ratchet''s own reading of both lists'' entries (an entry the ratchet would not count is named); when one refuses, the close stops at once, names its cause and spends no ratchet attempt [DEC-868 item 3, DEC-896 item 3, P-IS-4 (a), I2 F13, I4 F14, F17]'
  - 'The pre-close gate inside gov close: it collects every suite it will run, in one process, as it runs them; it runs gov check with no commit since the rebuild; and it checks that the ticket''s checkpoint is fresh. Any failure refuses at once, before any test runs [DEC-868]'
  - 'Before its regression, gov close reads the shared disk''s free space and free inodes (W2-20''s reading once it lands; until then the floors 100 GiB and 10,000,000 inodes from the configuration) and refuses below either floor, naming the reading [DEC-898]'
  - 'The probe gate accepts a failed probe record whose every finding is named, with its row, in an ACCEPTED owner decision that names the record and its probed commit; any finding not so named still refuses [W2-M371, DEC-790]'
  - A refused close writes a complete repair ticket (role, allowed paths, KPIs) that stays tracked in .tickets/ [F-m8, W2-L209, W2-L236, AR-9].
  - The close record carries the measured governance share [W2-M166, W2-M286].
  - Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal reuses its repair ticket [W2-H038, W2-M249, W2-M252].
  - An interrupted close leaves nothing that blocks the next close [W2-M158].
  - 'The cases this ticket turns red are revised by its test designer, each with a Rewrite-Reason: W1-30''s test_w1_30_no_acceptance_tests.py (3 functions, 6 cases) and test_collection_error_refuses_close; its engineer revises the unit test_a_collection_error_is_a_finding [I2 F9]'
  failure:
  - A research ticket without an evidence record closes; an audit ticket whose report fails the validator closes.
  - A collection error, a RED gov check, a stale checkpoint, a stale probe, an unmeasured commit, a ratchet entry the ratchet would not count, or a disk below the floor refused only after the regression.
  - A decision-record commit outside an ACCEPTED decision counted as measured.
profile: STANDARD
sources:
- DEC-729
- DEC-738
- DEC-790
- DEC-868
- DEC-892
- DEC-896
- DEC-898
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-07/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-9 (claims)
- F-m8
- W2-H045
list_rows:
- W2-H038
- W2-H045
- W2-L107
- W2-L108
- W2-L123
- W2-L124
- W2-L165
- W2-L196
- W2-L197
- W2-L208
- W2-L209
- W2-L210
- W2-L236
- W2-M149
- W2-M157
- W2-M158
- W2-M166
- W2-M178
- W2-M248
- W2-M249
- W2-M252
- W2-M263
- W2-M276
- W2-M286
- W2-M348
- W2-M349
- W2-M354
- W2-M403
```
## W2-07 gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-07), as approved (DEC-729), with DEC-868, DEC-892, DEC-896 item 3, DEC-898 and lens I's P-IS-4.

- **Place (DEC-896 item 3):** it comes forward to sit with W2-66, before the first re-pin, and rides in it.
  - It shares `src/gov/close/command.py` with W2-66: W2-66 writes the record's evidence lines, W2-07 the gates. The two run in sequence, or stacked under DEC-786.
- **Allowed paths:** `src/gov/close/**`, except W2-66's and W2-68's new modules (`select.py`, `nightly.py`, `evidence.py`, `batch.py`, `fingerprint.py`). Also `src/gov/telemetry/**`, `tests/unit/close/**` and `tests/unit/telemetry/**`, and, for its test designer only, the W1-30 cases named above.
- **It unblocks** the test-revision tickets: W2-63, W2-67's revisions and W2-70 close on its class once it is pinned.
- **Row W2-M263 (DEC-738 item 4):** RED stays when nothing comes after the base (DEC-479; W1-30's test); this ticket owns how the close reports it.



---

# 9. W2-07: the card

*Source: `drafts/review-bundle/06-W2-07-card.md`*

#### W2-07 `gov close` by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close (STANDARD, engineer; DEC-868, DEC-892, DEC-896 item 3, DEC-898; keystone 1)
- **Place (DEC-896 item 3):** comes forward to sit with W2-66, before the first re-pin, and rides in it.
  - It shares `src/gov/close/command.py` with W2-66: W2-66 writes the record's evidence lines, W2-07 the gates. The two run in sequence or stacked under DEC-786.
  - Its close is judged by the pin, so its own gates help from the re-pin on.
- **Allowed paths:** `src/gov/close/**` (except W2-66's and W2-68's new modules `select.py`, `nightly.py`, `evidence.py`, `batch.py`, `fingerprint.py`), `src/gov/telemetry/**`, `tests/unit/close/**`, `tests/unit/telemetry/**`, `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` and W1-30's collection-error cases (one named revision batch for its test designer).
- **KPIs, success (the existing ones kept):**
  - judged by its class:
    - implementation on its acceptance tests;
    - specification on its readiness record and tests;
    - audit on its report and validator;
    - research on its evidence record;
    - integration or coordination on its named evidence files;
  - a complete, tracked repair ticket;
  - the measured governance share;
  - adoption-gap and baseline refusals not counted;
  - an interrupted close blocks nothing;
  - the probe gate's named-finding acceptance (W2-M371, DEC-790);
  - DEC-868's pre-close gate inside `gov close`.
- **Added by DEC-896 item 3 (owner):**
  - **Decision records measured by their decision:** a decision-record commit that changes only governance records, under an ACCEPTED decision, counts as measured for the work-without-a-task gate. A decision-close would hide the gap and is not this.
  - **Test-revision tickets** are judged on their declared `acceptance_tests.path` (DEC-892). W2-63, W2-67's revisions and W2-70 wait for this.
  - **A stale probe is named before the close spends its run** (W2-M403).
- **Added from lens I (P-IS-4 (a), for the owner's decision):**
  - **The commit gates run first,** and stop before any test when one refuses, spending no ratchet attempt (DEC-868 item 3). They are the trailers, task-less work, accepted history, the probe gate, and the ratchet's own reading of both lists' entries. On 2026-10-22 two closes spent about 70 minutes each before refusing on commit findings (I2 F13, I4 F14, F17).
  - **Named for its test designer** (cases this ticket turns red): `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` (3 functions, 6 cases) and `test_collection_error_refuses_close`. **For its engineer:** the unit `test_a_collection_error_is_a_finding` (I2 F9).
  - **Optional:** the missing case for the close record's packet hash, made a constant in a planted fault that nothing caught (I2 PF9).
- **Added by DEC-898 (owner):** before its regression, `gov close` reads the shared disk's free space and free inodes (W2-20's reading once it lands; until then the same floors, 100 GiB and 10,000,000 inodes, from the configuration). Below the floor it refuses at once, naming the reading, and spends no attempt.
- **KPIs, failure:**
  - a research ticket without an evidence record, or an audit ticket whose report fails the validator, closes;
  - a tree with a collection error, a red `gov check`, a stale checkpoint, a stale probe, an unmeasured commit, a ratchet entry the ratchet would not count, or a disk below the floor is refused only after the regression;
  - a decision-record commit outside an ACCEPTED decision counts as measured.



---

# 10. W2-68: the ticket file

*Source: `drafts/review-bundle/03b-W2-68-ticket.md`*

```yaml
id: (assigned by tk at creation, when W2-66 has merged; W2-68 has no ticket yet)
status: open
type: task
priority: 1
assignee: engineer
external-ref: W2-68
tags: [wave-2, close, batch, reuse, fingerprint, full, keystone-2]
wbs_id: W2-68
title: 'Batched closes, reuse on the same code, and two fingerprints'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-c1uz]
allowed_paths:
- src/gov/close/batch.py
- src/gov/close/fingerprint.py
- src/gov/close/command.py
- src/gov/close/repo.py
- src/gov/store/**
- tests/unit/close/test_batch*
- tests/unit/close/test_fingerprint*
- tests/unit/store/test_fingerprint*
- tests/acceptance/W1-30/test_w1_30_store*
- docs/research/W2-68-batched-close.md
kpis:
  success:
  - 'A batch: queued closes on one integrated head share one rebuild, one gov check and one full regression on that head, then each ticket''s own checks one after another (its acceptance suite, the record-reading set, its trailers, paths, probe record and checkpoint); no code merges into w2/integrate while a batch runs; each close record cites the batch''s run (fingerprint, commit, JUnit XML) and its scope [DEC-883 item 1]'
  - 'A red batch: failing tests are re-run alone first, and a red that passes alone is a flaky candidate, not bisected; a red that fails alone is attributed by git bisect over the batch''s merges or by the failing tests'' own ticket, recorded with the evidence; nothing closes on a red run; the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run; an outside cause is fixed by the orchestrator and recorded [DEC-883 item 2, DEC-889 item 2 b]'
  - 'Same code: a close whose code fingerprint (the test map''s record-only paths left out) equals the last fully passing run''s reuses that run, and runs its own checks and the record-reading set; a failing run is never reused; any code difference runs fresh; the reused evidence states the reused run''s skip count [DEC-883 item 3, DEC-889 item 2, I4 F2]'
  - 'Two fingerprints: the code fingerprint governs the code index; changed record files refresh their lexical and semantic chunks incrementally; a lexical index whose record files differ is never fresh [DEC-889 item 2 (item 4)]'
  - 'The path map counts as code for the fingerprint (it is in the shared core, DEC-880), so a change to it runs fresh [P-IS-2, I-SYNTHESIS §4]'
  - 'W1-30''s test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later is re-read against two fingerprints by its test designer, with a Rewrite-Reason [I2 §2.6]'
  - 'The trial on a fixture repository or a dev-tier programme, measured and reported in docs/research/W2-68-batched-close.md: the time per batch; reuse correct; a planted code change forcing a fresh run; a planted record-only commit running the set and nothing else; a red batch attributed, nothing closing on it [DEC-884 item 4]'
  failure:
  - A close citing a red run or another fingerprint's run; a reused run on different code; a store accepted on another code fingerprint; a lexical index fresh with changed records; a code merge during a batch; a red that passes alone being bisected; reused evidence hiding a skip.
profile: FULL
sources:
- DEC-883
- DEC-884
- DEC-889
- DEC-890
- DEC-896
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W2-68/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: []
```
## W2-68 Batched closes, reuse on the same code, and two fingerprints

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-68), from DEC-883, DEC-889 item 2, DEC-890 (the split) and lens I's P-IS-2.

- **Starts** when W2-66 has merged and passed its ladder. Its entry criterion is the record-reading set settled in W2-66's test map. The second re-pin follows it (DEC-889 item 15).
- **Reads, never writes,** the test map's record-only list (W2-66's file).



---

# 11. W2-68: the card

*Source: `drafts/review-bundle/03-W2-68-card.md`*

#### W2-68 Batched closes, reuse on the same code, and two fingerprints (FULL, engineer; DEC-883, DEC-889 item 2, DEC-890; keystone 2)
- **Why:** the queue of 2026-10-21 ran six closes on the same code, about 85 minutes each (DEC-883). Queued closes on one head share one regression. A close on code that already passed reuses that run. A store built on the same code fingerprint is fresh.
- **Starts** when W2-66 has merged and passed its ladder (DEC-890). The second re-pin follows it (DEC-889 item 15).
- **Entry criterion:** the record-reading set is settled and in W2-66's test map (P-IS-2). Without it, reuse would let a close pass on a red head (I2 F6, I3 F5).
- **Allowed paths:**
  - new: `src/gov/close/batch.py`, `src/gov/close/fingerprint.py`;
  - `src/gov/close/command.py`: the calls and the record's lines only;
  - `src/gov/close/repo.py`: the store-freshness check only;
  - `src/gov/store/**`: the fingerprints a rebuild records and the incremental record load only;
  - `tests/unit/close/test_batch*`, `test_fingerprint*`, `tests/unit/store/test_fingerprint*`;
  - `docs/research/W2-68-batched-close.md`.
  It reads the test map's record-only list; it does not write it.
- **KPIs, success:**
  - **A batch (DEC-883 item 1):**
    - queued closes on one integrated head share one rebuild, one `gov check` and one full regression on that head;
    - then each ticket's own checks run, one after another: its acceptance suite, the record-reading set, its trailers, paths, probe record and checkpoint;
    - no code merges while a batch runs;
    - each close record cites the batch's run (fingerprint, commit, JUnit XML) and its scope.
  - **A red batch (DEC-883 item 2, DEC-889 item 2 b):**
    - failing tests re-run alone first; a red that passes alone is a flaky candidate, not bisected;
    - a red that fails alone is attributed by `git bisect` over the batch's merges, or by the failing tests' own ticket, with the evidence;
    - nothing closes on a red run; the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run;
    - an outside cause is fixed by the orchestrator and recorded.
  - **Same code (DEC-883 item 3, DEC-889 item 2):**
    - a close whose code fingerprint (record-only paths left out) equals the last fully passing run's reuses it, and runs its own checks and the record-reading set;
    - a failing run is never reused;
    - the reused evidence states the reused run's skip count, so a silent skip is not inherited unseen (I4 F2).
  - **Two fingerprints (DEC-889 item 2, item 4):**
    - the code fingerprint governs the code index;
    - changed record files refresh their lexical and semantic chunks incrementally;
    - a lexical index whose record files differ is never fresh.
  - **The path map counts as code for the fingerprint:** it is in the shared core (DEC-880), so a change to it runs fresh. The synthesis asks this question; the recommendation is to keep DEC-880's answer.
  - **Re-read against two fingerprints:** W1-30's `test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later` (I2 §2.6), by its test designer with a `Rewrite-Reason:`.
  - **Its trial (DEC-884 item 4),** on a fixture or dev-tier programme, measured:
    - the time per batch;
    - reuse correct;
    - a planted code change forcing a fresh run;
    - a planted record-only commit running the set and nothing else;
    - a red batch attributed, with nothing closing on it.
- **KPIs, failure:**
  - a close that cites a red run or another fingerprint's run;
  - a reused run on different code;
  - a store accepted on another code fingerprint;
  - a lexical index fresh with changed records;
  - a code merge during a batch;
  - a red that passes alone being bisected;
  - reused evidence that hides a skip.
- About 300 lines (DEC-890).



---

# 12. W2-67: the ticket file

*Source: `drafts/review-bundle/04b-W2-67-ticket.md`*

```yaml
id: (assigned by tk at creation, when W2-66 has merged; W2-67 has no ticket yet)
status: open
type: task
priority: 2
assignee: independent-test-designer
external-ref: W2-67
tags: [wave-2, tests, hygiene, revision, full]
wbs_id: W2-67
title: 'Test hygiene: per-test copies, nested runs, temp folders, and the weak tests'' revisions'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: [DAEO-c1uz, DAEO-r9ss]
allowed_paths:
- tests/acceptance/W1-07/w1_07_support.py
- tests/acceptance/W1-25/**
- tests/acceptance/W1-26/**
- tests/acceptance/W1-27/**
- tests/acceptance/W1-30/**
- tests/acceptance/W2-02/**
- tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py
- tests/unit/close/**
- tests/unit/guard/**
- tests/conftest.py
kpis:
  success:
  - 'Every per-test copy commits with gc.auto=0 or copies the working files without .git; W1-27''s old-path case gets a project of its own instead of a whole-tree copy; a planted 7,000-object tree runs every copying case green in parallel [I3 F9, I4 F5, I4 §2.1]'
  - 'The 15 unit close functions that start a nested pytest get a bound a loaded machine meets (one worker, or a measured limit); worksteal is then re-measured in the nightly in file order [I2 F5, DEC-892 a, P-IS-3]'
  - 'W2-50''s large-store and hang cases run against a declared short limit; the guard unit test''s fixed /tmp folder becomes tmp_path [I1 F-11, I1 §2.3]'
  - 'The suites keep pytest''s own retention of three base folders and nothing passes a per-run --basetemp; a full run leaves at most three base folders behind [DEC-898]'
  - 'Each weak case revised is first shown red against a planted fault, then green on the head, each with a Rewrite-Reason; in this order: gov doctor''s 40 W1-27 cases (before W2-22, W2-18 or W2-09 changes doctor); W1-26''s 45 planted-defect cases, their fixture shown green before any defect; W1-30''s 13 first-round cases; W2-02''s unmeasured case; I3''s T-A3 rows (their folders named in this file when it is written) [P-IS-7 (a), I2 F2, F3, I4 F1]'
  failure:
  - A revised case that cannot fail for its fault; an expectation lowered; a copy that still races gc; an unbounded nested run; a per-run base folder; a test changed in a folder this file does not name.
profile: FULL
sources:
- DEC-889
- DEC-892
- DEC-898
est_loc: 750
acceptance_tests:
  path: tests/acceptance/W1-27/
  author: independent-test-designer (MR-3); the revisions of other tickets' acceptance tests, each with a Rewrite-Reason
track: A
list_rows: [W2-L373]
```
## W2-67 Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-67), from DEC-889 item 7 (P-H-5), DEC-892 item 1, DEC-898 and lens I's P-IS-3 and P-IS-7.

- **Starts** after W2-66 merges. As a test-revision ticket, it closes on its declared `acceptance_tests.path` once W2-07's class is pinned (DEC-896 item 3). That is why `acceptance_tests.path` names another ticket's folder.
- **Roles:**
  - its independent test designer revises the acceptance tests;
  - its engineer changes the builder tests (`tests/unit/**`) and the shared fixtures (DEC-042).
- **Riding elsewhere (P-IS-7 (a)):** revisions of files an open ticket already holds:
  - W2-11: the skills' 41 cases;
  - W2-34: W1-09's and W1-14's;
  - W2-65: the unit hooks;
  - W2-44: containment's PF-7 case;
  - W2-04: W1-24's.
- **W2-L373's rename** rides in W2-69 if P-IS-5 (a) is taken; otherwise here.



---

# 13. W2-67: the card

*Source: `drafts/review-bundle/04-W2-67-card.md`*

#### W2-67 Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions (FULL, independent-test-designer for the acceptance revisions, engineer for the builder tests; DEC-889 item 7, P-H-5, DEC-892 item 1, DEC-898; lens I's P-IS-3 and P-IS-7)
- **Why:** lens H and lens I found these.
  - **Per-test copies race git's garbage collection.** A copied tree past about 6,700 loose objects races git's background gc. It errored W1-25's and W1-07's cases in refused closes (I3 F9, I4 F5).
  - **Nested runs fail under load and block worksteal** (I1 F-5, I2 F5).
  - **pytest's temp folders are not cleaned:** `/tmp/pytest-of-usain` holds 61 run folders since 2026-10-20. One auditor's per-run base folders filled the disk's inodes on 2026-10-22 (DEC-898).
  - **About 277 weak or outdated functions** cannot fail for the fault they claim to catch, or encode an old rule (I-SYNTHESIS §5.2).
- **Place:**
  - Starts after W2-66 merges (DEC-889 item 7).
  - Its acceptance-test revisions can close only once W2-07's test-revision class lands, so it is planned to close after W2-07 (DEC-892 item 1, P-IS-7).
  - Once DEC-769 item 3 is built, its designer writes only the folders this card names (P-IS-11).
  - The two acceptance reruns are not here: P-IS-3 (a) retires them now, in a small ticket of their own (W2-70 in the bundle's index).
- **Allowed paths:**
  - for the engineer: the fixtures and helpers that make whole-tree copies (`tests/acceptance/W1-07/w1_07_support.py`, `tests/acceptance/W1-25/**`, the W1-27 old-path case's fixture);
  - `tests/unit/close/**` (the 15 nested-run functions only; it runs after W2-07, which holds that folder);
  - `tests/unit/guard/**` (the fixed `/tmp` folder only);
  - the root `tests/conftest.py` (the temp-folder rule only).
  - For the test designer, each with a `Rewrite-Reason:` and no expectation lowered:
    - `tests/acceptance/W1-26/**`, `W1-27/**`, `W1-30/**`, `W2-02/**`, `W2-50/**` (the large-store and hang cases only);
    - the folders of I3's T-A3 rows (I3 §4.5), each named in the ticket file when it is written.
- **KPIs, success:**
  - **Copies (I3 F9, I4 §2.1):** every per-test copy either commits with `gc.auto=0` or copies the working files without `.git`. W1-27's old-path case gets a project of its own instead of a whole-tree copy. A planted 7,000-object tree runs every copying case green in parallel.
  - **Nested runs (I2 F5):** the 15 unit close functions that start a nested pytest get a bound a loaded machine meets (one worker, or a measured limit). After them, worksteal is re-measured in the nightly in file order (DEC-892 a, P-IS-3).
  - **Long cases (I1 F-11):** W2-50's large-store and hang cases run against a declared short limit. The guard unit test's fixed `/tmp` folder becomes `tmp_path`.
  - **Temp folders (DEC-898):** the suites keep pytest's own retention of three base folders, and nothing passes a per-run `--basetemp`. A full run leaves at most three base folders behind.
  - **The weak tests (P-IS-7 (a)):** each revised case is first shown red against a planted fault, then green on the head. The order is the code a planned ticket will change first:
    - `gov doctor`'s 40 W1-27 cases, before W2-22, W2-18 or W2-09 changes doctor;
    - W1-26's 45 planted-defect cases, their fixture shown green before any defect;
    - W1-30's 13 first-round cases;
    - W2-02's unmeasured case;
    - T-A3's 42 rows.
    Revisions of files that an open ticket already holds ride in that ticket instead (P-IS-7 (a)): W2-11 the skills' 41, W2-34 W1-09's and W1-14's, W2-65 the unit hooks, W2-44 containment's PF-7 case, W2-04 W1-24's.
  - **Slimming, optional:** W1-02's 121 spelling functions merged; 27 renames ("as a read", "four worker roles"); the two dead modules and the stale help line (`src/gov/cli/commands/status.py`, `check.py`) go to W2-22.
- **KPIs, failure:**
  - a revised case that cannot fail for its fault;
  - an expectation lowered;
  - a copy that still races gc;
  - a nested run left unbounded;
  - a per-run base folder;
  - a test changed in a folder this card does not name.
- About 600 to 900 lines of test code (I2's estimate for its share), and about 150 to 200 functions, most one fixture line and one assertion each.



---

# 14. W2-57: the ticket file

*Source: `drafts/review-bundle/05-W2-57-ticket.md`*

```yaml
id: (assigned by tk at creation; W2-57 has no ticket file yet)
status: open
type: task
priority: 1
assignee: engineer
external-ref: W2-57
tags: [wave-2, close, load, serial, full]
wbs_id: W2-57
title: 'Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/adapters/portability.py
- src/gov/doctor/command.py
- src/gov/close/serial.py
- tests/acceptance/serial-only.txt
- tests/acceptance/W1-30/test_w1_30_r11_declared_here.py
- tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py
- tests/acceptance/W1-38/**
- tests/acceptance/W1-33/w1_33_support.py
- tests/acceptance/W1-07/**
- tests/acceptance/W1-46/**
- tests/acceptance/W1-50/**
- tests/acceptance/W1-02/**
- tests/acceptance/W2-57/**
- tests/unit/close/test_serial*
- tests/unit/adapters/test_portability*
- docs/changes/W2-57-CIT-E.md
kpis:
  success:
  - 'First item, the rulesync probe, with its four effects (DEC-892 item 2, P-I4-5 (a)): the portability check''s two rulesync calls get a limit a loaded machine meets, measured under the close''s parallel load; W1-38''s session fixture fails, never skips, when rulesync times out (a timeout is not "not installed"); the 9 cases whose "not green" assertion a timeout satisfies assert the reason; W1-33''s research case fails, not skips, the same way. Three closes'' worth of parallel runs show 0 rulesync skips and 0 timeouts [I4 F2, DEC-871, DEC-892]'
  - 'The doctor probes (src/gov/doctor/command.py, the probes only) get limits a loaded machine meets, and a probe exception gov doctor does not catch fails with its failure text kept, so W1-07 [doctor]''s cause shows if it recurs [I4 F5, I2 F12]'
  - 'The serial-only list is reworked as the two tables of P-IS-6 (I-SYNTHESIS): every entry kept serial names its reason in the list; W1-16''s 94 cases that start no daemon, W1-09''s two race cases (after one green nightly in parallel) and W1-50''s read-merge latency case run in parallel; the live and real-model files (W1-46, W1-50''s two freeze cases, W1-19''s real-model file, W1-21''s dev-tier file and family check, W1-49''s and W1-25''s live files, W2-58''s five launched sessions, W2-62''s live resume, W2-54''s sandboxed worker and real embedder) leave the close for the nightly, as DEC-889 item 5 orders; true latency cases stay alone [DEC-883 item 5, DEC-889 item 5, I1 F-2, I3 F6, F7, I4 §4.2]'
  - 'W1-30''s r11 test, which holds today''s serial entries one by one, is revised to read the reworked list and its reasons (Rewrite-Reason: DEC-889 item 5) [I2 F9]'
  - 'W1-30''s r13 case gets a limit a loaded start meets (Rewrite-Reason: W2-M384) [I2 §2.2]; W1-50''s two live freeze cases remove every CLAUDE* variable, as DEC-784 requires [I1 F-7]; one p95 case covers a test designer''s read [I1 F-10]; W2-M332 times W1-19''s queries without its memory sampler in the same process [I3 O3 (b)]'
  - 'The close''s resource gate covers the wall-clock limits that went red under load: W1-02''s 5-second bound (168 cases) and the guard''s 20-second deadline, either by a limit a loaded machine meets or by running them alone [I1 F-14]'
  - 'The network check probes the live tests'' hosts through the route the session uses, close to when it runs [I1 F-1]'
  - 'Then the orchestrator commits the removal of every load_sensitive entry this ticket makes unnecessary (DEC-861: a removal only shrinks the list): W1-38''s three, W1-07 [doctor], W1-30''s r13, the unit close follow-up (not reproducible in 6 runs), and W1-46''s 23 and W1-19''s warm p95 once their files run in the nightly; the two p95 entries (W1-02, W1-05) stay as declared second tries, or leave, as the owner decides in P-IS-6 [DEC-766, DEC-813, P-IS-6]'
  failure:
  - A rulesync or doctor timeout that skips or passes a case; a serial entry without its reason; a live or real-model file left in the close; a case weakened, skipped or serialised by marker alone to pass; a list entry added (only the owner adds, DEC-862).
profile: FULL
sources:
- DEC-813
- DEC-823
- DEC-871
- DEC-883
- DEC-889
- DEC-890
- DEC-892
- DEC-784
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-57/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: [W2-M364, W2-M384, W2-M332, W2-L352, W2-L409]
```
## W2-57 Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-57). Sources: DEC-813, DEC-823, DEC-883 item 5, DEC-889 item 5, DEC-890 item 2, DEC-892 item 2, and lens I's P-IS-6 (I-SYNTHESIS, which merges P-I2-1 B and C, P-I4-5, P-I1-8 and I3 O3).

- **Why:**
  - The serial phase takes about 31 minutes of every close.
  - Most refused closes since 2026-10-20 came from cases on the two lists, or from load-caused reds.
  - The rulesync probe's timeout silently skips up to 181 W1-38 cases, and the close still passes. That is a live fail-open (I4 F2).
  - The card of DEC-813 asked W1-46's live cases to pass under the close's parallel load. That is replaced: DEC-889 item 5 moves live and real-model tests to the nightly (I2 F14).
- **Starts** in a free slot after the review point, the rulesync probe first. It **closes** before W2-24 starts (DEC-813).
- **Paths widened (I2 F12):** the old card's paths could not reach four of its entries (W1-38 ×3 and W1-07's `[doctor]`), nor the list it must change.
- **Until it lands (the orchestrator's interim guard, no product change):** the close queue checks that a close's skip count equals the expected 31, so a silent rulesync skip stops the queue (P-IS-6, from I4 F2).
- **Route out for every entry:** P-IS-6's second table. The two `accepted_reds` are W1-42's, not this ticket's (P-IS-8).
- **The 28 entries that name list rows** rather than a ticket are outside W2-19's check. Their removal rests on the orchestrator's commit, on the dates DEC-890 gives rows (P-IS-6, the W2-57 block).



---

# 15. W2-57: the card

*Source: `drafts/review-bundle/05b-W2-57-card.md`*

#### W2-57 Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry (FULL, independent-test-designer then engineer; DEC-813, DEC-823, DEC-883 item 5, DEC-889 item 5, DEC-892 item 2; lens I's P-IS-6)
- **Why:**
  - The serial phase takes about 31 minutes of every close, and most refused closes since 2026-10-20 came from listed cases or load-caused reds.
  - The rulesync probe's 10-second limit turns load into reds, greens and a silent skip of up to 181 W1-38 cases. That is a live fail-open (I4 F2).
  - **This card replaces DEC-813's KPI.** That KPI had W1-46's live cases pass under the close's parallel load; DEC-889 item 5 moves live and real-model tests to the nightly instead (I2 F14).
- **Starts** in a free slot after the review point, the probe first (DEC-892 item 2). It **closes** before W2-24 starts (DEC-813).
- **Allowed paths (widened, I2 F12):**
  - `src/gov/adapters/portability.py` and `src/gov/doctor/command.py` (the probes only);
  - `src/gov/close/serial.py` (new: the serial phase and its reasons);
  - `tests/acceptance/serial-only.txt`;
  - W1-30's r11 and r13 files;
  - `tests/acceptance/W1-38/**`, `W1-07/**`, `W1-46/**`, `W1-50/**`, `W1-02/**`;
  - W1-33's `w1_33_support.py`;
  - `tests/acceptance/W2-57/**`;
  - `tests/unit/close/test_serial*`, `tests/unit/adapters/test_portability*`;
  - `docs/changes/W2-57-CIT-E.md`.
- **KPIs, success:**
  - **The probe's four effects (P-I4-5 (a)):**
    - a limit a loaded machine meets;
    - W1-38's fixture fails, never skips, on a timeout;
    - the 9 cases a timeout satisfies assert the reason;
    - W1-33's research case fails the same way;
    - 0 rulesync skips or timeouts in three closes' worth of parallel runs.
  - **The doctor probes:** limits a loaded machine meets, with failure text kept (W1-07 `[doctor]`).
  - **The serial-only list reworked as P-IS-6's table:**
    - every kept entry names its reason;
    - W1-16's 94 non-daemon cases, W1-09's two races and W1-50's read-merge case run in parallel;
    - the live and real-model files move to the nightly;
    - latency cases stay alone.
  - **Revisions:** W1-30's r11 test reads the reworked list. Also W1-30's r13 limit, W1-50's `CLAUDE*` removal (DEC-784), a p95 case for a designer's read, and W2-M332's timing without the memory sampler.
  - **The close's resource gate** covers W1-02's 5-second bound and the guard's 20-second deadline. The network check probes through the session's route.
  - **Then the orchestrator commits the removal** of every entry this ticket makes unnecessary (DEC-861).
- **KPIs, failure:**
  - a timeout that skips or passes a case;
  - a serial entry without a reason;
  - a live file left in the close;
  - a case weakened, skipped or serialised by marker alone;
  - a list entry added.
- **Until it lands:** the close queue checks that each close's skip count equals the expected 31 (the orchestrator's interim guard).



---

# 16. W2-70: the ticket file and the card

*Source: `drafts/review-bundle/09-W2-70-ticket-and-card.md`*

## W2-70: the ticket file and the card (new, only if the owner takes P-IS-3 (a))

## Ticket file

```
---
id: (assigned by tk at creation)
status: open
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-70
tags: [wave-2, tests, retirement, lite]
wbs_id: W2-70
title: 'Retire the two nested reruns: W1-05''s switch-over case and W1-47''s builder rerun'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W1-05/**
- tests/acceptance/W1-47/**
- tests/acceptance/serial-only.txt
- tests/acceptance/W1-30/test_w1_30_r11_declared_here.py
kpis:
  success:
  - 'W1-05''s switch-over case, which re-runs W1-02, W1-03 and W1-04 (4,355 cases) in a child process (874 s alone, 14.6 minutes of every close), is retired in one commit with a Retire-Reason naming the owner''s decision; its KPI was a one-time order at W1-05''s close [P-IS-3 (a), I1 F-5]'
  - 'W1-47''s builder case, which re-runs tests/unit/guard (78 s; timed out at 300 s under worksteal), is retired in the same commit [P-IS-3 (a), I1 F-5]'
  - 'The switch-over line leaves tests/acceptance/serial-only.txt, and W1-30''s r11 test, which holds the entries one by one, drops it with a Rewrite-Reason [I2 F9]'
  - 'Nothing else changes: the suites the reruns covered still run in every close as themselves'
  failure:
  - A retired case whose suites no longer run in the close; any other test changed.
profile: LITE
sources:
- DEC-889
- DEC-892
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W1-05/
  author: independent-test-designer (MR-3); a retirement by the owner's decision
track: A
list_rows: []
---
## W2-70 Retire the two nested reruns

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-70), from P-IS-3 (a) (owner, at the review point).

- **Why:** the two reruns cost about 15 minutes of every close's quiet window, and they block worksteal (DEC-892 a).
- **Place:** starts now, merges early, and closes on its declared `acceptance_tests.path` once W2-07's class is pinned (DEC-896 item 3), as W2-63 does. The 15 unit nested runs are bounded in W2-67.
```

## Card (for `docs/plan/WAVE_2_WBS.md` §2)

#### W2-70 Retire the two nested reruns: W1-05's switch-over case and W1-47's builder rerun (LITE, independent-test-designer; P-IS-3 (a))
- **Why:** W1-05's switch-over case re-runs three suites the same close has already run, taking 14.6 minutes of every close. W1-47's builder case re-runs `tests/unit/guard`. Both block worksteal (I1 F-5, DEC-892 a).
- **Starts now; merges early; closes** once W2-07's test-revision class is pinned.
- **Allowed paths:** `tests/acceptance/W1-05/**`, `tests/acceptance/W1-47/**`, `tests/acceptance/serial-only.txt`, W1-30's r11 file.
- **KPIs, success:**
  - both cases retired in one commit with a `Retire-Reason:`;
  - the switch-over line out of `serial-only.txt`, and W1-30's r11 test updated;
  - the suites they re-ran still run as themselves.
- **KPIs, failure:**
  - a covered suite that no longer runs;
  - any other test changed.



---

# 17. P-IS-5's three ticket-file corrections (W2-65, W2-69, W2-66)

*Source: `drafts/review-bundle/08-corrections-P-IS-5.md`*

## P-IS-5 (a): three ticket-file corrections before the first re-pin, as they would be committed

Each correction is its own commit, carrying that ticket's `Task:` (DEC-896 item 2), once the owner takes P-IS-5 (a).

## W2-65 (`DAEO-e82f`)

- **allowed_paths gains:**
  - `src/gov/hooks/subagentstop.py`: kept byte-identical to the template's copy, which `TestHookCopiesIdentical` requires;
  - `tests/acceptance/W1-29/test_session_hooks.py`: for its test designer only, with `Rewrite-Reason: DEC-889 item 8`. W1-29's SubagentStop case accepts the undocumented form this ticket removes (I3 F4).
- **A note for its test designer:** the launcher recognises the guard by `hooks/pretooluse.py`, and the new hook line must keep that (I1 §2.3).
- **Riding along (P-IS-7 (a)):** the weak unit hook cases in `tests/unit/hooks/**`, which its engineer already holds. The weak PreCompact case (I3 P9) is one of them.

## W2-69 (`DAEO-rmbe`)

- **Named for its test designer:** W2-50's scale cases in `tests/acceptance/W2-50/` (the large-store and time-limit cases of the secrets scan). Rows-as-text scanning or compaction may change what they expect (I1 P-I1-7).
  - allowed_paths gains, for its test designer only, each change with a `Rewrite-Reason: DEC-897`:
    - `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py`;
    - `tests/acceptance/W2-50/w2_50_scan_support.py`;
    - the secrets cases of `test_w2_50_never_indexed.py` and `test_w2_50_last_review.py`.
  - W2-50's contained duplicate can be retired then (P-I1-7; the retirement is the owner's, P-IS-15).
- **W2-L373's rename rides here.** `tests/unit/secrets/` shadows the standard library's `secrets` under some plugins: a collection red in all five tool trials (I2 F8). The folder becomes `tests/unit/secrets_check/`, and allowed_paths gains `tests/unit/secrets_check/**`.

## W2-66 (`DAEO-c1uz`)

- **The file names the test map** (`governance/project/test-map.yaml` and its schema), not the path map (DEC-896 item 2).
- **It is replaced by the draft in this bundle** (`01-W2-66-ticket.md`).



---

# 18. The register draft for your answers (DEC-899)

*Source: `drafts/review-bundle/10-register-draft-DEC-899.md`*

## The register draft for the owner's answers at the review point (DRAFT: written for the recommended options; edited to the owner's actual answers before it is committed)

## 286. The owner's answers of 2026-10-23 at the review point (register v0.286, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-899 — The review point: W2-66, W2-68, W2-67, W2-57 and W2-07 confirmed as drafted; lens I's packages P-IS-1 to P-IS-7; the two re-pins; DEC-898's figures; W2-70
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** DEC-880, DEC-883, DEC-884, DEC-889 items 14 to 16, DEC-890, DEC-892, DEC-896, DEC-897, DEC-898, DEC-866, DEC-861 · **Basis:** the review bundle (`governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md`, filed with this record) and lens I's synthesis (`docs/assessment/2026-10/I-SYNTHESIS.md`) with its four area reports.
- **Decision:**
  1. **P-IS-1 (a):** W2-66's shared core gains:
     - `src/gov/cli/main.py` and `src/gov/errors.py`, until measured;
     - the retrieval core as its eight named modules;
     - both hook copies;
     - the test map.
     W1-07's three contract files run on every close. Every coupling of the synthesis's §4 is declared in the test map. The nightly measures the CLI pair later.
  2. **P-IS-2 (a):** the record-reading set is every test that reads a declared record-only path, directly or by scanning the tree.
     - Its first list goes in W2-66's test map.
     - The record-only list is exactly DEC-891's.
     - The set reads the pre-close gate's own `gov check` result.
     - The path map counts as code for W2-68's fingerprint (DEC-880's shared core).
  3. **P-IS-3 (a):** W1-05's switch-over case and W1-47's builder rerun are retired now, in a new LITE ticket W2-70.
     - W2-70 merges early and closes once W2-07's class is pinned.
     - W2-67 bounds the 15 unit nested runs.
     - Worksteal is then re-measured in the nightly (DEC-892 a).
  4. **P-IS-4 (a):** W2-07's KPIs gain:
     - the commit gates first, stopping before any test and spending no attempt;
     - the named W1-30 and unit cases.
     The orchestrator adds the ratchet's reading of both lists to its pre-close gates under DEC-895 meanwhile.
  5. **P-IS-5 (a):**
     - W2-65's paths gain `src/gov/hooks/subagentstop.py` and W1-29's `test_session_hooks.py`;
     - W2-69 names W2-50's secrets-scale cases for its test designer and takes W2-L373's rename;
     - W2-66's file names the test map.
     Each correction is its own commit with its ticket's Task (DEC-896).
  6. **P-IS-6 (a):** W2-57's ticket file as drafted. Its paths are widened, the probe's four effects come first, and the live-case KPI is replaced by the nightly move (DEC-889 item 5). Every list entry gets a route out, per P-IS-6's table.
     - **The p95 entries:** W1-02's and W1-05's p95 `load_sensitive` entries are kept as declared second tries until W2-M332, with its date (if the owner chooses to keep them), or removed by the orchestrator's commit now (if the owner chooses to remove them).
  7. **P-IS-7 (a):** revisions of files an open, planned ticket already holds ride in that ticket (DEC-802). Everything else goes to W2-67, which closes after W2-07 is pinned.
  8. **The re-pin plan:** two re-pins.
     - The first carries W2-58, W2-59, W2-65, W2-66, W2-07 and W2-69, after W2-66's ladder.
     - The second carries W2-68.
     - The old pin folder stays for a one-command rollback.
     DEC-884's and DEC-889 item 15's texts are marked "Changed by DEC-899".
  9. **The drafts confirmed:** W2-66's ticket file and card; W2-68's, W2-67's, W2-57's and W2-70's ticket files and cards; W2-07's ticket file and card. Each ticket file is committed in its own commit with its ticket's Task (DEC-896).
  10. **DEC-898's figures confirmed:**
      - floors of 100 GiB and 10,000,000 inodes free;
      - 30 GB and 2,000,000 files and folders per auditor, trial or research session, and per nightly run;
      - 20 GB and 1,000,000 per lead with its workers.
      DEC-898's status line drops "provisional".
  11. **Lens I's area 4 is not resumed.** The nightly full run gives the missing run evidence; a red or flaky result in area 4's suites comes to the owner as an addendum.
  12. **Packages P-IS-8 to P-IS-16** come before the tickets they gate start (the synthesis's §6, B and C).
- **Changes:**
  - DEC-884 (the re-pin);
  - DEC-889 items 7, 14 and 15;
  - DEC-890 (W2-66's and W2-68's paths and KPIs as drafted);
  - DEC-892 a (worksteal's condition met in two steps);
  - DEC-898 (the figures confirmed);
  - DEC-813's W2-57 KPI on W1-46's live cases (replaced by DEC-889 item 5's nightly move).
- **Where it goes (DEC-851):**
  - this register, with the changed entries marked;
  - the prompt §3 (the order and the re-pins), v3.19;
  - RESUME HERE;
  - the WBS cards and ticket files named in item 9, each ticket file in its own commit;
  - the corrections of item 5;
  - `LEAD-w2-common.md` only if a lead rule changes (none expected).
- Next free id: DEC-900.

| Version | Date | Change |
|---|---|---|
| 0.286 | 2026-10-23 | Owner (recorded by the orchestrator, DEC-861): DEC-899 (the review point: P-IS-1 to P-IS-7 (a); the p95 entries as the owner chose; two re-pins; the drafts of W2-66, W2-68, W2-67, W2-57, W2-07 and the new W2-70 confirmed; DEC-898's figures confirmed; lens I's area 4 not resumed). Next free id: DEC-900. |
