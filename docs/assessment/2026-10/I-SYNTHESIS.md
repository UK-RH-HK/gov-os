# Lens I: the synthesis of the test review

Independent assessment of the Gov OS, October 2026. Lens I is the test review the owner ordered on 2026-10-21 (DEC-889 item 16). Four auditors each reviewed one area's tests; this is the fifth session, which puts their four reports together for the owner's review point (DEC-889 item 14).

| | |
|---|---|
| **Author** | An independent auditor (`GOV_ROLE=independent-auditor`, Opus 5.5). I wrote none of the work assessed and saw none of the four reports while they were written. |
| **Date** | 2026-10-22 |
| **Head** | `w2/integrate` at `89f043e2` when I started. The four reports measured `4166d8d9` and read the later commits; three of them checked that no later commit changes code, tests or the kernel (`git diff --stat 4166d8d9 89f043e2 -- src tests template` is empty: I1 header, I3 header, I4 §1.1). |
| **Read** | The four reports: I1 (area 1), I2 (area 2), I3 (area 3), I4 (area 4; complete, not PARTIAL). Lens H's report. The owner's tool trials (`TOOL-TRIALS-2026-10-22.md`). The register (DEC-757 to DEC-897 where cited; DEC-880 to DEC-897 in full). The WBS cards, the list rows and the ticket files the reports name. The path map's two lists. Contract v4.2 on `w2/W2-49`. ADR-0001. |
| **Ran** | Reads only. I ran no test. `gov retrieve` twice: both answered `FACET_UNAVAILABLE` (the lexical and semantic facets "stale"), so every fact here comes from reading the sources directly (§7.2). |
| **Cited as** | "I2 F3" is report I2's finding 3; "I1 F-6" is I1's finding F-6; "P-I2-4", "R1", "O2", "P-I4-5" are the reports' packages; "§2.2" is a report's section. My own packages are P-IS-1 to P-IS-16. |

**Words used** (each defined once).
- **A close** (`gov close`): closing a ticket. It runs the ticket's tests, then every other test in parallel (**the regression**, or **parallel phase**), then the **serial-only** cases one at a time (**the serial phase**, from `tests/acceptance/serial-only.txt`). A **refused close** costs its full run (70 to 85 minutes) and a count toward escalation.
- **`accepted_reds`** and **`load_sensitive`** (**the ratchet**): the owner's two lists in the path map. A listed known red does not refuse a close; a listed load-sensitive test that fails is re-run alone and counts only if it fails again. Both lists only shrink (DEC-766); each entry names its fix in `fixed_by` (DEC-762).
- **Valid and needed, outdated, obsolete, duplicate, weak, flaky, not reproducible:** the seven verdicts of DEC-889 item 16 c. **Weak** means the test cannot fail for the fault it claims to catch.
- **A planted fault:** a one-line change made on purpose in an auditor's own copy, to see whether the tests that claim it fail.
- **W2-66:** the ticket that makes a close run only the suites a change can reach (**path-scoped selection**), with a **shared core** whose change runs everything. Its lists go into a **test map** of their own (DEC-896 item 2).
- **W2-68:** batched closes and **same-code reuse**: a close on code identical to the last passing run reuses that run. Its **code fingerprint** leaves record-only paths out, so the **record-reading set** (tests that read records) must run on every head (DEC-883, DEC-889 item 2).
- **W2-67:** test hygiene (per-test copies, nested reruns). **W2-57:** load out of the close, and the serial-only list. **W2-07:** the close by ticket class. **The re-pin:** the owner moving the pinned judge to a new commit (DEC-884, DEC-889 item 15, DEC-896 item 3).
- **A nested rerun:** a test that starts a whole pytest run of other suites inside itself. **Worksteal:** a pytest-xdist mode that lets idle workers take queued tests.
- **The nightly:** the orchestrator's full uncached run each night (DEC-889 item 4).
- **A round, ride along, entry criterion:** a round is a further iteration of a ticket's work (DEC-801). A fix rides along in a ticket that runs anyway (DEC-802). A risk that exists only once a feature is on is an entry criterion of the ticket that switches it on (DEC-803).
- **The two lines** (DEC-808): `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only "yes" with "fails open" or "loses work" justifies a round.

---

## 1. The diagnosis, in one page

**What the test estate is worth today.**
- The four auditors gave 3,256 verdicts on test functions (8,212 cases). That is about 56 % of the estate's 5,770 functions, every case of the serial phase, and 61 % of the parallel phase's case time (§2).
- Areas 3 and 4 were read in full. Areas 1 and 2 were read by risk first, then by seeded samples (§2.5).
- **86 % of what was reviewed is valid and needed** (2,802 functions). By the two samples, the unreviewed rest is about 91 to 95 % sound (I1 §2.3; I2 §3).
- **The tests that keep agents safe are the strongest part.** The guard, Policy 2, containment, the launcher and the sandbox hold 63 % of all cases. Every fault planted in them was caught, except the three that showed three weak tests (I1 §2.7).

**What it fails to catch.**
- **208 weak functions**, clustered in a few early suites:
  - `gov check`'s planted-defect cases, whose fixture is red before any defect is planted (W1-26: 45; I2 F3);
  - `gov doctor`'s cases, which find a key name doctor always prints (W1-27: 40; I4 F1);
  - the kernel skills' word checks (W1-35 and W1-36: 41; I4 F15);
  - the close's first-round cases, refused for a missing checkpoint whatever the gate does (W1-30: 13; I2 F2);
  - context cases on a fixture with no index (W1-24: 13; I3 F3), and hook cases (W1-29 and unit hooks: 10; I3 F3).
- **48 of 119 planted faults got past every test run against them** (§2.2). **24 of those would let a broken gate pass, or lose work, in ordinary work** (§3.3). In most, the code is right today and only the next slip would pass.
- **Three gaps are live today** (§3.1):
  - a context packet built without a lexical index is silently empty (I3 F16);
  - the path-map check and `gov doctor`'s path-map section measure nothing on a real path map. In this repository only W1-08's test, run before every close, holds the rule (I2 F3, I4 F3);
  - when the rulesync probe times out, W1-38's fixture skips up to 181 cases and the close still passes (I4 F2).

**What it costs a close.**
- A close takes about 85 minutes: a rebuild (6), `gov check` (7), the parallel phase (about 32) and the serial phase (about 31) (DEC-883's basis; the rehearsal of 2026-10-21).
- **Tests with a verdict other than valid cost about 20 minutes of every close.** 14.6 of those minutes are one test: W1-05's switch-over case, which re-runs three suites the same close has already run (I1 F-5).
- **Placement matters more than verdicts.** Moving the live and real-model tests to the nightly (already decided, DEC-889 item 5), plus two retirements, would cut the serial phase from about 31 to about 11 minutes (§2.4).
- **The flaky few cost refused closes, not seconds.** On 2026-10-22, three of the four finished closes were refused for area-2 causes (I2 In brief). Since 2026-10-20, an area-4 case or list entry was among the causes of seven refused closes (I4 §3).

**The few things that matter most.**
1. **No finding needs a new round.** Each fix rides along in a ticket that runs anyway, or becomes an entry criterion (§3.5).
2. **Five planned tickets would be refused at their own close** by tests their allowed paths cannot reach, unless their ticket files change first:
   - W2-13 and W2-14, by W1-42's two accepted reds, once W2-19's check is in; before it, their closes would remove entries whose tests stay red, and every later close would be refused (P-IS-8);
   - W2-57, by four `load_sensitive` entries whose fix lies outside its paths, once W2-19's check is in (P-IS-6);
   - W2-65, by W1-29's identity check on the hook it changes (P-IS-5);
   - W2-19, by W2-53's six cases that build entries in the old form (§4).
   W2-07, W2-66, W2-34 and W2-11 will also turn named valid tests red; their cards must name them (§4).
3. **Two decisions save most of the close time:** retire the two nested reruns (P-IS-3), and move the live and real-model files out of the close, as DEC-889 item 5 already says (P-IS-6).
4. **Before W2-66's test designer starts,** the owner settles the record-reading set (P-IS-2) and what widens a scoped close to a full run (P-IS-1).
5. **The weak tests need one home.** Whatever it is, a ticket that only revises other tickets' tests can close only once W2-07's test-revision class lands (P-IS-7).

---

## 2. The combined counts

### 2.1 Per verdict, all four areas

One verdict per test function; a function's parameter sets are its cases. Times are case time in the rehearsal of 2026-10-21 (the close's form).
- **Parallel phase:** a case-second costs about 0.142 s of a close's wall time (13,417 case-seconds ran in 31.8 minutes; I2 §3, I4 §3). I1 and I3 estimated about a twentieth; I use the measured figure for all four.
- **Serial phase:** a second is a second of the close.

| Verdict | Functions | Cases | Parallel case time (s) | About this much of a close: parallel | Serial phase (s) |
|---|---|---|---|---|---|
| Valid and needed | 2,802 | 7,406 | 6,761 | 16.0 min | 825 |
| Weak | 208 | 226 | 605 | 1.4 min | 6 |
| Duplicate | 103 | 243 | 530 | 1.3 min | 874 |
| Outdated | 69 | 175 | 114 | 16 s | 87 |
| Obsolete | 24 | 54 | 8 | 1 s | 0 |
| Flaky | 40 | 94 | 83 | 12 s | 52 |
| Not reproducible | 10 | 14 | 27 | 4 s | 0 |
| **Reviewed** | **3,256** | **8,212** | **8,128** | **19.2 min** | **1,844** |
| Not reviewed (areas 1 and 2) | 2,543 | 7,583 | 5,286 | 12.5 min | 0 |

Sources: I1 §3, I2 §3, I3 §3, I4 §3. Notes:
- The serial column adds to the whole serial phase (1,842.6 s): every serial case was reviewed.
- Two places were reviewed twice: W1-42's two accepted reds (areas 2 and 3) and `tests/unit/hooks` (areas 1 and 3, about 30 functions). The table counts them in each area.
- Area 4 counts 2 flaky functions plus 6 flaky single cases, and 1 not-reproducible single case (I4 §3).

### 2.2 Per area

| | Area 1 (I1) | Area 2 (I2) | Area 3 (I3) | Area 4 (I4) |
|---|---|---|---|---|
| What it covers | The guard, the launcher, the sandbox | `gov close`, the checks, the ratchet | Retrieval, context, checkpoints, resume | Records, plan, tickets, the rest |
| Functions / cases in the area | 2,042 / 9,896 | 1,459 / 2,264 | 878 / 1,217 | 1,420 / 2,418 |
| Reviewed | 540 / 3,844 | 418 / 733 | 878 / 1,217 | 1,420 / 2,418 |
| How | Risk first, a 6 % seeded sample, a static scan of all | Risk first, a 5 % seeded sample | Every function | Every function |
| Valid | 465 | 306 | 796 | 1,235 |
| Weak | 3 | 58 | 38 | 109 |
| Duplicate | 12 | 4 | 26 | 61 |
| Outdated | 34 | 16 | 6 | 13 |
| Obsolete | 15 | 1 | 8 | 0 |
| Flaky | 11 | 23 | 4 | 2 (+6 cases) |
| Not reproducible | 0 | 10 | 0 | 0 (+1 case) |
| Planted faults (got past every test run) | 18 (3) | 23, plus 4 whole-suite reruns (7) | 30 (19) | 48 (19) |
| Share of the parallel phase's case time | 32 % | about 29 % | about 7 % | 33 % |
| Share of the serial phase | 53 % (one test: 47 %) | under 1 % | 46 % | about 1 % |

Sources: I1 In brief and §3; I2 In brief and §3; I3 §2 and §3; I4 §1.5, §2.4 and §3.
- Area 4's 19 uncaught faults: 7 in broad runs (I4 §1.5) and 12 more in narrower runs (I4 §2.4 rows with "nothing" else red: P34-1, P08-3, P08-4, P44-a, PL202-1, P27-11, PS-2, PS-3, PS-5, PS-6, PS-7, PS-13).
- Area 1's 3: PF-5 and PF-6 were run against their own test only; PF-7 passed 1,357 cases (I1 §2.7).

### 2.3 What each class costs beyond its seconds

- **Duplicates: 14.6 minutes of every close,** nearly all W1-05's switch-over case (874 s alone in the serial phase). W1-47's builder rerun sits on the parallel tail, and both block worksteal (I1 F-5; DEC-892 a).
- **Flaky and not reproducible: refused closes.** W1-46's host cases were among the findings of four refused closes, the latest W2-63's on 2026-10-21 (I1 F-1). The copy race, the rulesync probe and W1-07's `doctor` case were among the causes of W2-53's and W2-02's refused closes (I4 §2.1, F2, F5). Each refusal costs 70 to 85 minutes and a count.
- **Weak: no protection for the time spent.** About 1.4 minutes of every close, and the gate each one names can break unseen (I2 §3; I4 §3).
- **Outdated: wrong guidance and forward reds.** They cost little time. But they enforce a replaced rule, or turn red when the ticket that changes their behaviour lands without naming them (I2 F9; I4 F16).
- **Obsolete: noise.** For example, 28 skips counted in every close record (I1 P-I1-1).

### 2.4 What acting on them saves

| Action | Decided by | Serial phase saved | Parallel phase saved | Source |
|---|---|---|---|---|
| Retire W1-05's switch-over case | P-IS-3 | 874 s | — | I1 F-5 |
| Retire W1-47's builder rerun | P-IS-3 | — | 78 case-s (≈ 11 s, more on the tail; 300 s and a timeout under worksteal) | I1 F-5 |
| Live and real-model files out of the serial phase (W1-19, W1-21, W1-49, W1-25, W1-46, W1-50's two live cases) | DEC-889 item 5, through P-IS-6 | ≈ 270 s | — | I3 §3 (208.8 s); I1 §2.1 rows (W1-50: 37.9 s); W1-46's file estimated from I1 §3 |
| Live and real-model cases out of the parallel phase (W1-21's family check, W2-62's live resume, W2-54's sandboxed worker and real embedder, W2-58's five launched sessions) | P-IS-6 | — | ≈ 192 case-s, area 3's slowest parallel case among them; four paid sessions (W2-62's, W2-54's, W2-58's two) | I3 F6; I1 F-2 |
| W1-16's 94 cases that start no daemon, to the parallel phase | P-IS-6 | 35.5 s | adds ≈ 36 case-s | I3 F7 |
| W1-09's two races and W1-50's latency case, to the parallel phase | P-IS-6 | ≈ 14 s | small | I4 §4.2; I1 §4.2 |
| W2-54's repeats of `gov check` | P-IS-15, P-IS-2 | — | ≈ 150 case-s per run; 5 to 6 min per head once the record-reading set runs on every head | I3 F15, R5 |
| W1-07's three whole-tree duplicates | P-IS-15 | — | 93.5 case-s (≈ 13 s) | I4 F10 |
| W2-50's contained large-store case | P-IS-15 | — | 169 case-s (≈ 24 s; up to about 3 min when it is the last to finish) | I1 F-11 |
| The other retirements | P-IS-15 | — (W1-25's live file is counted in the move above; R4 retires it instead) | ≈ 40 case-s | §5.1 |
| **Total** | | **≈ 1,190 s: the serial phase from about 31 to about 11 minutes** | **≈ 690 case-s (≈ 1.6 min), plus the tail** | |

What stays in the serial phase: W1-16's 67 daemon cases (482 s), W1-20's 10 daemon cases (117 s) and the latency cases (I3 §4.2; I1 §4.2; I2 §4.2; I4 §4.2).

### 2.5 What was not reviewed, and why

- **Area 1:** 1,502 functions (6,052 cases), outside the risk-first steps and the 6 % sample. The static scan read all 2,042 for shapes that cannot fail (I1 §2.8). The sample found 104 of 109 valid, so roughly 70 more non-valid functions are expected there, mostly of the shapes already named. They are largely W1-02's guard cases that W2-58's designer rewrote to Policy 2 (I1 In brief).
- **Area 2:** 1,041 functions (1,531 cases, 69 % of the area's case time). The sample found 78 of 86 valid, so roughly 95 more non-valid functions are expected (I2 §3).
- **Not run, by rule:** live Claude sessions (W1-46's 36 live cases, W1-50's two, W2-58's five, W1-25's three, W1-49's nine, W2-62's live resume, W2-54's sandboxed worker). Their verdicts rest on the recorded closes and the rehearsal (I1 Limits; I2 Limits; I3 Limits).
- **Not run, for time or isolation:**
  - W1-05's switch-over case (I1);
  - other areas' `load_sensitive` cases and PF10b, and a whole-area parallel run in area 2 (I2);
  - 24 of 36 mutants (I3);
  - W1-12, W1-14, W1-37 and four unit folders, run in no form; no rebuild, so no retrieval (I4 §1.3).
- **Not reviewed by anyone:** no folder was left out (the 56 acceptance folders and 34 unit folders all fall in an area). No auditor ran the whole estate in the close's form under the close's quiet window (§7.2).

---

## 3. What fails open or loses work

Each item keeps its report's two lines. Where I classify differently, I say so. "Where it goes" says whether it needs a round now, rides along (DEC-802), or is an entry criterion (DEC-803).

### 3.1 Live today

**A. With no lexical index, a context packet is silently empty** (I3 F16; also W1-24's package P-11.2 and a residual DEC-579 left unbuilt).
- Retrieval reports the missing index (`FACET_UNAVAILABLE`), but the packet drops that reason: `supplementary: []`, `dropped: []`, and nothing says why. W1-24's case for this state passes on an always-true `or` (I3 F16). My own two `gov retrieve` calls today met a stale index: retrieval said so; a packet would not.
- Ordinary work: yes, because a fresh clone or worktree before its rebuild has no index, and retrieval never refreshes it (I3 F16).
- Consequence: fails open (a brief reads as if no supplementary evidence existed).
- **Where it goes:** rides along in W2-04, which rewrites the packet's supplementary part anyway (DEC-860), as its entry criterion. The packet names the unavailable index, and W1-24's case drops its `or` (P-IS-12). No round now: W2-04 runs before EXAMIN's adoption (W2-27 depends on it).

**B. The path-map rule is held only by W1-08's test** (I2 F3; I4 F3; known row W2-M214).
- `core-pathmap`, a hard-block check, reads `namespaces` as a list; every real path map holds a mapping, so the check is GREEN on any path in no namespace (I2 F3).
- `gov doctor`'s path-map section matches with `fnmatch`, whose `*` crosses folders. The first namespace, `root-files: ["*"]`, then holds all 2,071 paths, so doctor never reports an unclassified path (I4 F3).
- W1-26's path-map cases pass anyway, because their fixture is red before the defect (I2 F3). W1-08's test caught the real fault of 2026-10-21 (DEC-885).
- Ordinary work: yes, because a new top-level folder before its namespace is ordinary, and two record copies in no namespace refused W2-02's close (I2 F3; I4 F3).
- Consequence: fails open for both checks. In this repository W1-08's test, run in the pre-close gate (f), holds the rule; an adopted project has no W1-08.
- **Where it goes:** an entry criterion of W2-27, whose KPIs need `gov doctor` and `gov check` green in EXAMIN (P-IS-9).
- **A forward risk:** fixed as row W2-M214 reads, with the same `fnmatch`, the check would put 2,063 of 2,071 paths in two namespaces: a hard-block red on every close (I4 F3). That one fails closed.

**C. A rulesync timeout silently skips up to 181 W1-38 cases** (I4 F2).
- The portability check gives `rulesync --version` and `generate` 10 seconds each. On a timeout, W1-38's session fixture skips every rulesync case of that worker as "rulesync is not installed"; W1-33's research case does the same. The close counts a skip without refusing it (DEC-500). 9 more cases pass on the timeout, because the failure also satisfies their "not green" assertion (I4 F2).
- Ordinary work: yes, because every close runs W1-38 under parallel load, where the probe has already timed out in two closes (I4 F2).
- Consequence: fails open.
- **Where it goes:** rides along in W2-57's first item, already decided (DEC-892 item 2), widened to the probe's four effects (P-IS-6). It has not fired yet: every close since 2026-10-20 skipped exactly 31 cases (I4 F2).

### 3.2 Feature-gated: entry criteria

| Finding | Ordinary work | Consequence | Entry criterion of |
|---|---|---|---|
| **D.** Policy 2 (c) for the test designer names `w2/integrate` in code. Where that branch is missing, the designer's reads of its ticket's code are allowed silently (I1 F-12). | Yes, because a test designer launched in EXAMIN or in Wave 3 reads its ticket's code as an ordinary read | Fails open | W2-27, W2-29 and Wave 3's start (P-IS-10) |
| **E.** DEC-769 item 3 (the test designer writes only its own folder) is unbuilt, and W2-21's ticket file does not carry it (I1 F-4). | Yes, because a designer writes in another ticket's folder in every revision round | Fails open against the decision | W2-21 (P-IS-11) |
| **F.** The record-reading set misses many tests that read records (I2 F6; I3 F5; I4 F6). | Yes, because record commits land every day | Fails open once reuse is on (I2, I3). I4 says "other", because the nightly finds it later; I side with I2 and I3 (§7.1) | W2-66's set and W2-68 (P-IS-2) |
| **G.** W1-29's SubagentStop case holds the hook to the form in which its reason is lost (I3 F4; lens H P-H-7). | Yes, because any helper whose return lacks a field meets it | Loses work (the helper's result). For W2-65 as scoped: other (its close is refused by W1-29's identity case) | W2-65, whose paths must gain the hook's second copy and W1-29's file (P-IS-5) |
| **H.** The code graph's own traversal found neither of the checkpoint watchdog's two callers (I3 F13). | Yes, because impact questions are ordinary | Fails open (an empty impact answer), once W2-37 switches agents to the traversal (DEC-859) | W2-37 (§4) |
| **I.** Status words in lower case satisfy a mandatory source (I3 F17, P-11.3). Latent: every such status is in capitals today. | Yes, because a lower-case status is an ordinary slip | Fails open | W2-04. Row W2-L164 sends it to W2-34, which cannot reach the context code (P-IS-12) |
| **J.** A superseded register entry can be served as current evidence, and no test can see it (lens B's F4; I3 F13). | Yes | Fails open | Already packaged by lens B. Its fixing ticket needs a register fixture with several entries in one file (I3 F13) |

### 3.3 Latent gaps: the code is right today; the next slip would pass

Each was shown by a planted fault that no test caught.

| Fault | What would pass unseen | Ordinary work | Consequence | Where it goes |
|---|---|---|---|---|
| PF-7 (I1 F-6) | A failed restore of an acceptance test recorded as "reverted". None of containment's 1,357 cases caught it | Yes, because a restore fails when another git command holds the index lock | Fails open | Rides along in the next ticket that touches containment. W2-44 holds `tests/unit/containment/**` (my reading of its ticket file; I1 says "the next containment ticket") |
| PF3 (I2) | `core-pathmap` measures nothing | As item B | Fails open | P-IS-9 |
| PF6 (I2; lens H finding 19) | The ratchet's field rule dropped: an entry that names no fix counts | Yes, because W2-19 rewrites that check | Fails open | Rides along in W2-19; already its KPI (DEC-890 item 2) |
| PF9 (I2) | The close record's packet hash made a constant. Neither W1-30's 512 cases nor the unit close tests' 386 caught it | Yes, because a refactor of the record writer is ordinary | Fails open: the record no longer binds the close to its context (CAP-50.c). *I2 gives no per-fault classification; this one is mine* | W2-67's receipt revision (P-I2-3), or W2-07, which holds `src/gov/close/**` and its unit tests |
| PF22, PF23 (I2) | The runner ignores the readiness check's answer, or swallows its error | Yes | Fails open: the readiness family is GREEN when it is not. *Classification mine* | W2-L379's revision, plus one runner case (W2-67, P-I2-3). Whether area 4's readiness unit tests hold it was not measured |
| P13 (I3) | A checkpoint's age read in hours: the close's freshness check would pass a ten-day-old checkpoint | Yes | Fails open | W2-67 or a small revision ticket (P-IS-7) |
| P9 (I3) | A non-orchestrator's failed PreCompact checkpoint says nothing | Yes | Loses work | `tests/unit/hooks`. W2-65's engineer holds that folder (its ticket file), so it can ride along there; I3 sends it to its small ticket T-A3 (P-IS-7) |
| P8 (I3) | A code-graph error taken as an answer | Yes | Fails open | W2-37, whose paths gain `tests/unit/codeintel/**` (I3 F13) |
| P23 (I3) | A canary with no hits on a live index counted as a pass | Yes | Fails open | W2-67 or T-A3 (P-IS-7) |
| P22 (I3) | The validator accepts a quote from lines outside the ones it cites | Yes | Fails open | W2-67 or T-A3 (P-IS-7) |
| P27-1, P27-4, P27-7, P27-8, P27-9 (I4 F1) | `gov doctor`'s moved-path references, unclassified paths, path matcher and isolation; rebuild's digest | Yes, because W2-22, W2-18 and W2-09 change doctor | Fails open | W1-27's structural rewrite (W2-67 or a small W1-27 ticket), before the first of those three changes doctor (my timing); the matcher with W2-22 (P-IS-9) |
| P41-c (I4 F4) | A8, the retirement stage, retires legacy files past a changed verdict or plan, or with an unknown artefact | Yes, because W2-52 changes adoption now and EXAMIN's adoption runs A8 | Fails open (no lost work: an archive ref keeps the files) | W2-52's resume, or a small W1-41 ticket, before EXAMIN reaches A8 |
| PS-2, PS-3, PS-5, PS-6, PS-7, PS-13, P34-1 (I4 F15) | A rule removed from a kernel skill or template | Yes, because W2-11 rewrites the skills now | Fails open | Rides along in W2-11 (its test designer revises the 41 word checks) |
| I4 F13 (not planted) | `core-authority` drops the decision checker's `ACTIVE_UNAPPROVED`, with no comment or register entry, since 2026-10-06 | Yes, because a commit that sets a decision ACTIVE without the owner is the slip DEC-360 guards against | Fails open, latent: nothing is affected today | Rides along in W2-12, which holds `src/gov/check/authority.py` (carrier mine; I4 leaves it to area 2, and I2 did not report it) |

### 3.4 Not ordinary work: rows for the Wave 3 hardening pass (DEC-801)

- I1 F-9: the Linux sandbox's handling of glob-named entries is unmeasured for Edit rules (also a row for W2-40, EXP-002).
- I1 PF-5 and PF-6 (two weak unit tests).
- I1 F-13's tripwire: a real `gov pause` during a close would refuse it.
- I3 P3: a ticket id with `../` writes its brief outside the scratch folder.
- I4 P11-1: the decision checker reading a Role trailer outside the final block.

### 3.5 What this means

- **None of these needs a new round now.**
  - The three live gaps ride along in tickets already planned (W2-04, W2-57) or are entry criteria of EXAMIN's adoption (W2-27).
  - The feature-gated risks become entry criteria.
  - The latent gaps ride along in the next ticket that touches the code, or in the hygiene work of P-IS-7.
- **Before the tickets start** (order of need):
  - W2-65: before its work continues for the first re-pin;
  - W2-66 and W2-68: the record-reading set;
  - W2-57;
  - W2-04;
  - W2-11, W2-12 and W2-19: when each starts;
  - W2-21;
  - W2-27, W2-29 and W2-52: before EXAMIN.

---

## 4. What it changes, by ticket

⚑ marks a place where two reports propose different changes to the same ticket.

### W2-66: path-scoped selection and evidence (`DAEO-c1uz`)

- **Its ticket file at the head still names `governance/project/path-map.yaml`** in its allowed paths and KPIs. DEC-896 item 2 moves the lists into the test map (my reading of `DAEO-c1uz.md`).
- **The shared core, and what widens to a full run:** see P-IS-1.
  - DEC-892 c's three modules are decided.
  - Proposed: `src/gov/cli/main.py` and `errors.py`, until measured (I4 F12).
  - The retrieval core as eight named modules (I3 §4.1 item 1).
  - W1-07's three contract files on every close, or mapped to every `src/gov/*/command.py` (I4 §4.1 item 1).
- **Map lines a coverage map cannot see** (write each in the test map):
  - W1-26 ← every module a declared check runs; W1-30 ← `checkpoint/**`, `decisions/**`, `closure/**`, `adapters/**`; W1-31 ← `context/**`, `checkpoint/**`; W1-40 ← `secrets/**`, `guard/runs.py`; `tests/unit/validate` ← `retrieval/validate.py`, `canary.py` (I2 §4.1);
  - W1-38 ← the kernel's `roles/**` and `skills/**` (I4 §4.1 item 3);
  - `retrieval/rerank_worker.py`, which runs in its own process ← W1-19's real-model file, W1-21's dev-tier file, `tests/unit/semantic/test_rerank_process.py` (I3 §4.1 item 2);
  - both hook copies (the template's and `src/gov/hooks/`) ← W1-29, W1-49, W2-62, `tests/unit/hooks`; the session-start and PreCompact hooks also ← W1-31, W1-37, W1-38, `tests/unit/telemetry` (I3 §4.1 item 5);
  - test-side imports: W1-29 → `w1_49_support`; W1-25 → `w1_07_support`; W2-54 → `w1_46_support`; W1-50 → four support modules (I3 §4.1 item 4; I1 §4.1);
  - files read as text: W1-42 reads `src/gov/cli/main.py` and kernel templates; W1-30's r11 reads `serial-only.txt` (I2 §4.1);
  - fixture inputs that are not code: the live path map and the gitleaks configurations, copied into W1-16, W1-17, W1-19, W1-20, W1-21, W1-22, W1-24 and W2-54; W1-18 lists the working tree's unit files (I3 §4.1 item 6);
  - W1-28's file scan, which runs every suite's whole-tree copier: goes if P-I1-4 is taken (I1 §4.1);
  - the live cases depend on the installed CLI and the network: select them on a change of the CLI's pin, or run them in the nightly only (I1 §4.1).
- **W1-01's MR-3 whole-history test** would rarely be selected: keep it in the nightly and every full run (I1 §4.1).
- **A valid case W2-66 will turn red:** W1-30's `test_regression_includes_other_acceptance_folders`. Name it for W2-66's test designer (I2 F9).
- **The record-reading set:** P-IS-2.
- **Worksteal and per-test limits:**
  - worksteal waits until the nested runs are gone (DEC-892 a; P-IS-3);
  - pytest-timeout with the `signal` method, the limit above the slowest test; 900 s held in the trial (DEC-892 b; the tool trials).
- **The evidence block must keep failure text.** Two causes could not be found because the close keeps none: W1-07's `[doctor]` red and W1-46's network reds (I4 F5; I1 F-1; DEC-889 item 12).

### W2-68: batching, reuse, two fingerprints (no ticket file yet)

- **Entry criterion: the record-reading set** (P-IS-2; I2 F6; I3 F5). ⚑ I4 F6 classifies the gap as "other".
- **Read the gate's result:** the set reads the pre-close gate's own `gov check` result for context-reproducibility and core-schema, instead of re-running W2-54's 5-to-6-minute fixture on every head (I3 R5 (a)).
- **A test to re-read against two fingerprints:** W1-30's `test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later` (I2 §2.6).
- **A question for the draft:** is the path map code or record? DEC-880 puts it in the shared core. DEC-896 calls it "a shared record". DEC-891's record list leaves it out. The answer decides whether tests that read it (W1-08's, W2-58's evaluation-set case) must join the set (I1 §4.1 and its rows; I3 §4.1 item 6).
- **A design note:** a reused run inherits any silent skip it held (item C). The reused evidence should state its skip count (I4 F2; my inference).

### W2-67: test hygiene (no card yet)

- **Per-test copies race git's background garbage collection** once a copied tree passes about 6,700 loose objects. Dormant at today's 2,071 files; it errored W1-25's and W1-07's cases in refused closes (I3 F9; I4 F5).
  - Fix in each fixture: commit with `gc.auto=0`, or copy the working files without `.git`.
  - W1-27's old-path case gets a project of its own instead of a whole-tree copy (I4 §2.1).
- **Nested reruns:**
  - W1-05's switch-over and W1-47's builder case: retire (P-IS-3) or move to the nightly (lens H P-H-5);
  - the 15 unit close functions that start a nested pytest with a 60-second limit: bound them (one worker, or a limit a loaded machine meets). They failed under worksteal in the trials (I2 F5).
- **Long cases:** W2-50's large-store and hang cases shrink by a declared short limit (I1 F-11). A fixed `/tmp` folder in a guard unit test becomes `tmp_path` (I1 §2.3 row).
- **Optional slimming:** W1-02's 121 spelling functions; 27 renames ("as a read", "four worker roles") (I1 §2.2, §2.3). Two dead modules and a stale help line: `src/gov/cli/commands/status.py`, `check.py` (I4 §4.1 item 5).
- **The weak-test revisions, if P-IS-7 (a) is taken:**
  - W1-30's 13 and W1-26's 45 (P-I2-3);
  - W1-27's 40 (I4 F1);
  - W2-02's unmeasured case (I4 §2.2);
  - the `secrets` folder's rename, W2-L373, unless W2-69 takes it (P-IS-5).
- **Sequencing** (I4 §2; DEC-892 item 1; P-I1-6):
  - a ticket that only revises other tickets' acceptance tests can close only once W2-07's test-revision class lands;
  - once DEC-769 item 3 is built, only on folders its ticket names.
- ⚑ **Where the revisions go:** I2 widens W2-67 (P-I2-3 (a)). I3 proposes its own small ticket T-A3, or folding into W2-67 (§4.5). I4 sends each to the open ticket that holds the files, or to small per-suite tickets (§2.2). Decided in P-IS-7.

### W2-57: load out of the close; the serial-only list (no ticket file yet)

The full proposal is P-IS-6. In short:
- **Its card contradicts a later owner decision.** It still asks W1-46's live cases to pass "inside the full regression run under its usual parallel load" (WBS line 897), against DEC-889 item 5: live and real-model tests move to the nightly (I2 F14).
- **Its planned paths cannot reach four of its entries,** nor the list it must change (I2 F12). Add:
  - `src/gov/adapters/portability.py` (the probe only) and `tests/acceptance/W1-38/**`;
  - `src/gov/doctor/command.py` (the probes only) and `tests/acceptance/W1-07/**`;
  - `tests/acceptance/serial-only.txt` and W1-30's `test_w1_30_r11_declared_here.py`, which holds today's entries one by one (I2 F9);
  - W1-33's probe helper (I4 F2).
- **Its first item, the rulesync probe, covers four effects** (I4 F2; P-I4-5): the probe's two calls; the fixture's skip, which should fail; the 9 masked cases; W1-33's skip.
- **The serial-only list and a route out for every entry:** P-IS-6's two tables.
- **Smaller items:**
  - W1-50's two live freeze cases remove every `CLAUDE*` variable, as DEC-784 requires (I1 F-7);
  - the network check probes the hosts through the route the session uses (I1 F-1);
  - the close's resource gate covers W1-02's 5-second bound and the guard's 20-second deadline (I1 F-14);
  - one p95 case for a test designer's read (I1 F-10);
  - W2-M332 times W1-19's queries without its memory sampler in the same process (I3 O3 (b));
  - W1-30's r13 case gets a limit a loaded start meets (`Rewrite-Reason: W2-M384`; I2 §2.2).
- **A gap in W2-19's check** (my reading of the path map and W2-19's KPI): only 4 of the 32 entries name a ticket (W2-57); 28 name list rows (W2-M332 ×3, W2-M364 ×23, W2-M384, W2-L352). W2-19's check refuses only "the close of the ticket an entry names", so it will not stop W2-57's close while those 28 remain. Their removal rests on the orchestrator's commit and the dates DEC-890 gives rows (I2 §4.3 notes the four Wave 3 rows).
- **`accepted_reds`:** none of the list is W2-57's; both entries are W1-42's (P-IS-8).

### W2-07: the close by ticket class (`DAEO-r9ss`)

- **Decided (DEC-896 item 3):** decision records measured by their decision; test-revision tickets judged on their declared `acceptance_tests.path`; a stale probe named before the run.
- **Add (P-IS-4):**
  - run the close's commit gates before any test (trailers, task-less work, accepted history, the probe gate, the ratchet's reading of its entries), and stop there when they refuse. Two of 2026-10-22's closes spent about 70 minutes each before refusing on commit findings (I2 F13);
  - the ratchet's reading of both lists as a gate. Until W2-07, a pre-close gate step under DEC-895's standing rule (I4 F14).
- **Name for its test designer the cases it will turn red** (I2 F9): `test_w1_30_no_acceptance_tests.py` (3 functions, 6 cases) and `test_collection_error_refuses_close`. For its engineer: the unit `test_a_collection_error_is_a_finding`.
- **It unblocks revision-only tickets** (W2-63, T-A3, a test-designer W2-67) (I4 §2; DEC-892 item 1).
- **Optional:** the missing case for the packet hash (PF9) is in its paths (§3.3).

### W2-19: language-agnostic test commands; the ratchet's checks (`DAEO-jzvg`)

- **W2-53's six load-sensitive cases (5 functions)** build entries without `fixed_by`, the form DEC-762 replaced. W2-19's KPI refuses such entries, so they turn red unless its test designer revises them (`Rewrite-Reason: DEC-762 item 1`). Its ticket names lens H's field-rule case but not these six (I2 F4).
- **The field-rule case per list** is already a KPI. PF6 confirms the gap at the head (I2 F4; DEC-890 item 2).
- **A record-reading case:** every real entry of both lists passes the ratchet's own R-2 and R-3 reading at the head (I2 F11; with I4 F14's gate step meanwhile).
- **Before its check lands:** W1-42's two entries need a route out, or W2-13 and W2-14 can never close (P-IS-8). W2-57's paths must reach its four entries (P-IS-6). The 28 entries that name rows are outside its check (W2-57 block above).

### W2-69: the secrets check reads what the stores hold (`DAEO-rmbe`)

No report reviewed W2-69's work: its ticket opened at 17:14, after the reviews' head. What lens I gives it:
- **Name the earlier tests it may turn red.** I1 expects W2-50's scale cases to be revised with W2-69 (P-I1-7). But W2-69's ticket names no revision of them, and its paths do not hold `tests/acceptance/W2-50/**` (my reading of `DAEO-rmbe.md`). If scanning rows as text, and compacting stores, changes what they expect, the ticket should name them for its test designer: the pattern of I2 F9 and I4 F16. W2-50's contained duplicate can be retired then (P-I1-7).
- **The `secrets` folder's rename (W2-L373) can ride here.** W2-69 holds `tests/unit/secrets/**` (its ticket). The folder shadows the standard library's `secrets` under some plugins, a red in all five tool trials (I2 F8). The rename is needed before rerunfailures and randomly join the nightly (DEC-892 d). Its paths would gain the new folder name; otherwise W2-67 (P-I2-3).
- DEC-897 (b)'s one proven re-run per close stays until W2-69 is pinned.

### Tickets whose paths or entry criteria must change before they start

- **W2-65** (`DAEO-e82f`, in the first re-pin): its paths gain `src/gov/hooks/subagentstop.py` (kept identical to the template) and `tests/acceptance/W1-29/test_session_hooks.py`, for its test designer. Otherwise its own fix turns W1-29's `TestHookCopiesIdentical` red and its close is refused (I3 F4; P-IS-5).
  - Its engineer already holds `tests/unit/hooks/**`, so the weak unit hook cases can ride along (P-IS-7).
  - ⚑ For `TestStopHook::test_no_ticket_returns_immediately`, I1 proposes W2-65 and I3 proposes T-A3.
  - A note for its test designer: the launcher recognises the guard by `hooks/pretooluse.py`, and W2-65's new hook line must keep that (I1 §2.3 row).
- **W2-04** (`DAEO-u4oz`), entry criteria (I3 F16, F17, F13; P-IS-12):
  - the packet names an unavailable index;
  - status words are compared without regard to case;
  - its paths gain W1-24's `test_w1_24_packet.py` and `test_w1_24_supplementary.py`, for the ceiling and indicator cases;
  - its engineer gives four `test_dropped_order.py` cases a budget above the mandatory inputs;
  - O1 is decided first;
  - a brief's file name carries its ticket, a gap the mutation sample found (I3 §2).
- **W2-21** (`DAEO-1ahb`): its ticket file gains DEC-769 item 3's KPI and source, `src/gov/guard/decide.py` (the designer's rule only), and a revision batch (P-IS-11; I1 F-4):
  - W1-02's 4 cases and 1 multiedit case;
  - W1-03's 2 cases;
  - W1-46's protected-trees reading;
  - W1-46's vacuous designer case (I1 §2.4 row).
- **W2-27 and W2-29** (EXAMIN), entry criteria:
  - the base branch as a project setting (P-IS-10);
  - the path-map rule held in an adopted project (P-IS-9);
  - W1-27's doctor cases able to fail, since "`gov doctor` green" is a KPI (I4 F1);
  - the A5 record type settled before EXAMIN's A5 (P-IS-14);
  - A8's guard tested before EXAMIN's A8 (I4 F4).
- **W2-32** (`DAEO-0pyc`): the order of raising hit@5 to 85 (P-IS-13). Its paths gain W1-19's `test_w1_19_real_models.py` and W1-21's `test_w1_21_dev_tier.py`. W2-54's record-grepping hit@5 case is left out of the correction (I3 O2, R5).
- **W2-37** (`DAEO-6n5k`; its paths hold neither `src/gov/codeintel/**` nor its tests today): when it resumes, its paths gain `tests/unit/codeintel/**` beside the `src/gov/codeintel/**` DEC-859 gives it. Its engineer then (I3 F13):
  - revises the three unit cases that pin the whole-graph read, and the weak error case (P8);
  - extends the callers KPI with a function called through an alias and a module attribute (the watchdog's `watch`);
  - asks `trace_path` for `format: "json"`.
- **W2-11** (`DAEO-k7hz`), riding along (I4 F7, F15, F16):
  - its supersession KPI adds DEC-820 (c) and DEC-542's command list;
  - its test designer revises the 41 weak skill word checks and W1-35's 8 outdated cases;
  - it names W1-33's `test_the_research_role_file_is_unchanged`, which DEC-839 item 5's widening will turn red;
  - the test-design skill gains R5's line: a test that greps its own ticket's evidence record retires at that ticket's close (I3 R5).
- **W2-12** (`DAEO-j8gn`): `core-authority`'s dropped `ACTIVE_UNAPPROVED` (I4 F13; carrier mine). W1-30's r13 owner-decision case revisited under DEC-862 (b) (I2 §2.6).
- **W2-13** (`DAEO-zqvn`) and **W2-14** (`DAEO-7y6v`): P-IS-8. W2-13 also rewrites the chunking parity case with fixed spans (R6).
- **W2-22** (`DAEO-xm6l`): doctor's matcher in DEC-225's language, and `test_match_pattern` revised (I4 F3). I4 narrows W1-07's `[doctor]` red to an exception `gov doctor` does not catch, since `main.py` catches only `GovError` (I4 F5); W2-22 may name it.
- **W2-23** (`DAEO-kmcr`): holds row W2-M214, but its paths cannot reach `src/gov/check/pathmap.py` (I2 F3; I4 F3; P-IS-9).
- **W2-34** (`DAEO-yadm`) (I4 F16, §2.2; I3 F17):
  - name W1-09's three READY cases and W1-14's tasks-template case, which its KPIs reverse (W2-M274, W2-H015, W2-H051);
  - revise W1-09's two weak cases and W1-14's outdated case;
  - give row W2-L164's two context residuals to W2-04.
- **W2-44** (`DAEO-zndm`): holds `tests/unit/containment/**`. PF-7's restore-label case and the five containment duplicates can ride with it (I1 F-6, P-I1-7; carrier mine).
- **W2-52** (`DAEO-siiz`, in progress): the A5 type collision as its entry criterion (P-IS-14); A8's guard case (I4 F4); the adopt skill's line still citing DEC-090 (I4 F8); W1-41's six weak cases, whose fixture it reuses.
- **W2-64:** W1-08's two schema scans read 8 of the 20 schemas; W2-02's unknown-type case (I4 §2.2).
- **W2-16:** W1-39's neither-file case is already rewritten on unmerged `w2/W2-16` (`adbeea77`); it merges with W2-16 (I4 §2.2).
- **W2-08:** W1-40's lefthook case is already in its card (I2 F9).
- **W2-40 (EXP-002):** re-measure the sandbox's Edit rules for glob-named entries (I1 F-9).
- **The ticket that builds DEC-889 item 17 (a)** (owner-approved installs into a named `/tmp` environment): W1-04's auditor and research cells need revising then (I1 §2.1 row).
- **A missing row:** DEC-755 item 5 orders `register-entry.schema.json` aligned, and no row carries it; W2-02's decision-entry case is revised with it (I4 F7).

---

## 5. Retirements and rewrites

Deduplicated across the four reports. "Saved" is case time per close in the rehearsal (parallel unless "serial"). A rewrite keeps the case's time and makes it worth spending (I2 §3).

### 5.1 Proposed retirements (each the owner's decision, DEC-889 item 16 d)

| Test(s) | Verdict | Evidence | Rests on | Package; carrier | Saved |
|---|---|---|---|---|---|
| W1-01: 7 skipped functions (`test_implementer_write_to_acceptance_tests_is_denied`, `test_acceptance_test_deny_covers_every_depth`, `test_install_command_is_denied`, `test_pipe_to_shell_and_sudo_are_denied`, `test_guardrails_leave_ordinary_implementer_work_alone`, `test_interim_rule_stays_in_force_once_introduced`, `test_no_install_is_recorded_before_w1_05`) | Obsolete | Skip in every run since W1-05 closed: 28 skips in every close record (I1 §2.2) | DEC-084, DEC-172 | P-I1-1 | 28 skips |
| W1-01: `test_a_dependency_is_read_in_either_form_of_the_id`, `test_implementer_commits_stay_inside_allowed_paths`; 5 `test_w1_01_bootstrap_record.py` functions; W1-05's `test_the_operator_diff_check_is_recorded_as_retired` | Obsolete | Pin frozen Wave 1 history or a record's text (I1 §2.2) | DEC-084 | P-I1-1 | ≈ 1 s |
| W1-01: `test_the_integration_merges_of_this_repository_pass` | Duplicate | Computes the same offences over the same merges as the MR-3 test (I1 §2.2) | DEC-253 | P-I1-1 | 5.3 s |
| W1-01: `test_docs_source_deny_rules_survive_the_change` (4 cases) | Outdated | Protects a folder removed on 2026-10-01 (I1 §2.2, F-8) | DEC-820 | P-I1-2, with the deny rules' removal (a settings change, CAP-33) | small |
| W1-02: the 22 hook-listing redaction functions (1 in `test_w1_02_hook_listing.py`, 9 in `…_paths.py`, 12 in `…_home_paths.py`) | Outdated | Policy 2 opened the reads the redaction hid (I1 §2.1) | DEC-820 (b), DEC-821 item 3 | P-I1-3: keep as defence in depth, or retire | 7.3 s if retired |
| W1-28: `test_w1_28_fixture_copies.py`, 6 functions (18 cases) | Outdated | DEC-385's basis removed; couples W1-28 to every suite (I1 §2.2) | DEC-820 (b), DEC-821 item 3 | P-I1-4 | small; removes a coupling |
| W1-05: `test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over`; W1-47: `test_the_builder_tests_of_the_guard_pass` | Duplicate | Nested reruns of 5,400 cases the same close runs (I1 F-5) | DEC-889 item 7, DEC-892 a | P-I1-5 → P-IS-3 | **874 s serial**; 78 s (300 s under worksteal) |
| Unit containment: `TestDEC132Defaults` (4) and `TestRepair4HeadMoveNoSnapshot::test_head_move_without_snapshot_is_flagged`; unit install: `test_unfrozen_repo_asks_install_for_orchestrator` | Duplicate | Same steps and assertions as named twins (I1 §2.1, §2.3) | DEC-132, DEC-139 | P-I1-7; W2-44 | negligible |
| W2-50: `test_a_large_clean_store_is_decided_green` | Duplicate | Contained in the large-store-among-many case (I1 F-11) | DEC-853 item 1 | P-I1-7; with W2-69 | **169 s** (on the tail) |
| W1-30: `test_close_runs_containment_check` | Duplicate and weak | Same body as `test_close_runs_acceptance_tests`; passes with containment off (PF4) (I2 §2.5) | CAP-13.a | P-I2-5 | 5.1 s |
| W1-26: `test_exit_0_when_all_checks_green` | Weak | Skips in every run (I2 F7) | CAP-39.d | P-I2-6, with a rewrite of `test_warning_yellow_does_not_change_exit_code` | 8.8 s |
| W1-30: `test_unmeasurable_inputs_listed_with_reason` | Obsolete | Describes behaviour DEC-470 removed; its loop never asserts (I2 P-I2-7) | DEC-470 | P-I2-7 | 5.4 s |
| W1-42: `test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]`, `test_governance_share_is_measured_and_at_most_15_percent_on_each_programme`, with their two `accepted_reds` entries | ⚑ I3: obsolete. I2: valid, a known red rightly listed | Read only the frozen Wave 1 exit record (I2 F1; I3 F1) | DEC-713, DEC-714, DEC-718, DEC-757 | R1 or P-I2-1 A → P-IS-8 | 0.1 s |
| W1-49: `test_the_pinned_cli_has_an_auto_compact_window` | Obsolete | Proves a 300k setting DEC-838 retired (I3 R2) | DEC-838 | R2 | 0.1 s |
| 22 duplicates: W1-10 `test_two_loads_give_the_same_digest`, `test_the_edges_of_a_type_are_exact`; W1-16 `test_two_repositories_have_two_homes`; W1-20 `test_an_unresolved_id_is_told_from_one_beyond_the_depth` (merge first); W1-21 `test_where_nothing_is_indexed_the_check_is_not_green_and_builds_nothing` (merge first); W1-22 `test_canary_runner_is_callable_standalone`, `test_validator_rejects_unresolvable_citation`; W1-23 `TestF1::test_changed_source_invalidates_note`; W1-24 `test_a_record_superseded_by_several_records_cannot_satisfy`, `test_the_same_ticket_and_commit_give_the_same_packet_hash`; W1-29's 10 (`TestAutomaticCheckpointLocation` ×2, `TestCheckpointOnContextUtilisation` ×2, `TestCompactionPreservesState::test_auto_compact_threshold`, `TestNoStopLoop::test_stop_exits_without_side_effects_when_active`, `TestSessionStart::test_orchestrator_compact_carries_prompt_path`, `TestWatchdogBlocksStale` ×3); W1-49 `test_the_hook_file_exists_in_the_kernel_template`; unit hooks `test_resume_section_ends_at_a_heading_of_the_same_or_a_higher_level` | Duplicate | Each twin named in I3 table 2.3 | As each row | R3 | ≈ 6 s |
| W1-25: `test_w1_25_live_session.py` (3) | Weak | Passes the brief as the prompt, bypassing the hook it claims to test (I3 R4) | CAP-37 | R4 | 6.2 s serial; a paid session |
| W2-54: the two closed-record greps (`test_the_change_record_states_the_limit_and_its_measurement`, `test_the_change_record_states_the_cache_s_bound_and_the_setting_that_lowers_it`), the hit@5 record grep, `test_w2_02_s_other_types_are_judged_as_an_unknown_type`, and the two `gov check` repeats | Obsolete or duplicate | I3 F2, F12, F15 | DEC-768, DEC-833, DEC-874 | R5 | ≈ 150 s when green |
| W2-62: three research-record cases (`test_w2_62_documents.py`) | Valid while the ticket was open; W2-62 closed at 16:44 | Their only failure mode is now an edit of a closed record (I3 table 2.3) | DEC-837 | R5's rule | small |
| W1-07: `test_the_envelope_has_no_field_outside_the_interface` | Duplicate | `assert_envelope` already holds it, on the same 13 runs (I4 P-I4-1) | API-0002 | P-I4-1 | 34.5 s |
| W1-07: `test_each_wave_1_operation_is_a_gov_command` | Duplicate | 12 of the envelope case's 13 runs (I4 P-I4-2) | CAP-28.b | P-I4-2 (keep its label) | 34.1 s |
| W1-07: the 8 `--json` cases of `test_a_read_command_leaves_git_status_empty` | Duplicate | Held by `test_a_read_command_changes_no_file_and_no_ref` (I4 P-I4-3) | CAP-27.a | P-I4-3 | 24.9 s |

Kept, though duplicates, by the reports' own advice (no retirement proposed):
- W2-58's two "still refused" functions, as W2-58's failure-KPI evidence (I1 §2.4);
- W1-26's and W1-30's envelope cases (I2 §2.5);
- I4's other 50-odd cheap duplicates (I4 §2.2, F10).

### 5.2 Proposed rewrites (by independent test designers, or engineers for builder tests, each with a `Rewrite-Reason:`)

| Suite: tests | Verdict | Evidence | Rests on | Carrier |
|---|---|---|---|---|
| **W1-02, W1-03, W1-46:** `test_test_designer_can_write_under_acceptance_tests` (4 of 12 cases); multiedit `[a-new-acceptance-test-of-another-ticket]`; `test_the_test_designer_s_changes_stay`; `test_the_test_designer_s_scope_does_not_depend_on_the_ticket_paths`; `test_the_test_designers_settings_carry_no_rule_for_the_acceptance_tests`; W1-46 research-role designer case (vacuous) | Outdated (the last valid) | Pin the designer's whole-folder write (I1 F-4) | DEC-769 item 3 | W2-21 (P-IS-11) |
| **W1-02:** `test_a_path_field_longer_than_the_guard_resolves_…` (and the 168 cases with the 5-second bound); **W1-50:** `test_a_commit_without_trailers_is_judged_against_the_caller` | Flaky (load) | First reds under load in I1's runs (I1 F-14) | DEC-562, DEC-580 | W2-57's resource gate; the bound on CPU time |
| **W1-50:** the two live freeze cases | Valid | Remove 6 named variables, not every `CLAUDE*` (I1 F-7) | DEC-784 | W2-57 |
| **Unit containment:** `TestRepair10ActionTellsTheTruth::test_failed_restore_is_flagged` | Weak (PF-7) | Accepts "flagged" or "reverted"; its restore is never tried (I1 F-6) | DEC-122 | W2-44 (P-IS-7) |
| **Unit guard:** `test_protected.py::test_the_brace_pattern_finds_what_the_one_it_replaced_found` | Weak (PF-5) | Compares two literals of its own (I1 F-6) | DEC-570 | W2-67 or the next guard ticket |
| **Unit hooks** (`test_w29_hooks.py`): `TestStopHook::test_no_ticket_returns_immediately` (PF-6; weak in both I1 and I3); `test_checkpoint_failure_reports_systemmessage` (P9); `TestSessionStartCombined::test_within_cap` (P10); `TestStopHook::test_stop_hook_active_returns_immediately` (P14a); `TestPreCompactCombined::test_no_ticket_no_record` (outdated: DEC-444) | Weak or outdated | I1 F-6; I3 table 2.3 | CAP-37.b, DEC-444 | ⚑ W2-65 (I1; it holds the folder) or T-A3 (I3) (P-IS-7) |
| **W2-58:** `test_with_no_base_branch_nothing_is_refused_under_this_item` | Valid; pins a fail-open default | I1 F-12 | DEC-820 (c) | With P-IS-10 |
| **W1-04:** the install rule's auditor and research cells | Valid | Must change when owner-approved `/tmp` installs work (I1 §2.1) | DEC-889 item 17 (a) | The ticket that builds it |
| **W2-50:** `test_a_large_store_among_many_small_files_is_decided_by_gov_check`, `test_a_scan_that_cannot_finish_fails_closed_and_records_nothing` | Valid | Slow only because the limit is the real 60 s (I1 F-11) | DEC-853 | W2-67 (a declared short limit) |
| **W1-02 and W2-50:** 27 renames ("as a read"; W1-46's "four worker roles") | Valid | Names state a removed rule (I1 F-3, F-13) | DEC-820; DEC-386 | W2-67 or the next guard ticket |
| **W1-30, round 1** (`test_w1_30_close.py`): `test_close_requires_implements_trailer`, `test_close_requires_task_trailer`, `test_close_refuses_when_acceptance_tests_fail`, `test_close_runs_acceptance_tests`, `test_containment_blocks_close_for_out_of_scope_commit`, `test_task_trailer_exact_match_not_substring`, `test_regression_runs_to_end_all_failures_collected`, `test_regression_failure_blocks_close`, `test_close_runs_regression_tests_when_present` | Weak | No checkpoint, or only `ok` asserted; PF4, PF5, PF5b, PF11, PF12, PF12b, PF13, PF15, PF16, PF16b pass them (I2 F2) | CAP-13.a | W2-67 (P-IS-7) |
| **W1-30:** `test_all_six_dispositions_recognized` (PF1), `test_disposition_with_context_failure` (PF2), `test_close_record_packet_hash_matches_context` (PF9), `test_owner_decision_checker_failing_refuses` (PF10) | Weak | I2 §2.7 | CAP-59.c, CAP-50.c, DEC-454 | W2-67 |
| **W1-26:** the overall-red class (26: `test_w1_26_authority.py` ×4, `test_supersession_cycle_flagged`, `test_w1_26_gap_tickets.py` ×4, `test_w1_26_planted_defects.py` ×12, the policy case, `test_w1_26_skill.py` ×2, `test_w1_26_taxonomy.py` ×2); the derived-scope class (8); the always-true assertions (5); `test_family_only_unmeasured_check_not_green` (invalid YAML); W2-L379's three; `test_warning_yellow_does_not_change_exit_code`; `test_duplicate_id_flagged` (duplicate: rewrite one) | Weak | The fixture is red before the defect (R1); PF3, PF7, PF8, PF17, PF20 to PF24 pass them (I2 F3, F7; §2.7) | CAP-38.b, CAP-39.d, DEC-436 | The three path-map cases with P-IS-9's carrier; the rest W2-67 |
| **W2-53:** `test_w2_53_load_sensitive.py` (5 functions, 6 cases) | Outdated when W2-19 lands | Entries without `fixed_by` (I2 F4) | DEC-762 item 1 | W2-19 |
| **W1-30:** `test_w1_30_r11_declared_here.py` (5, 29 cases); `test_w1_30_no_acceptance_tests.py` (3, 6 cases); `test_collection_error_refuses_close` and unit `test_a_collection_error_is_a_finding`; `test_regression_includes_other_acceptance_folders`. **W1-40:** `test_no_lefthook_hook_is_installed_in_this_repository` | Valid; outdated when W2-57, W2-07, W2-66 and W2-08 land | I2 F9 | DEC-889 item 5; DEC-868 item 3, DEC-892 item 1; DEC-880 item 2; DEC-718 F-M4 | W2-57; W2-07; W2-66; W2-08 (already) |
| **Unit close:** the 15 functions that run a nested pytest with a 60-second limit | Not reproducible (red in the trials under worksteal) | I2 F5 | DEC-527 | W2-67, by the engineer, before worksteal |
| **Unit secrets:** the folder's three files (26 cases) | Flaky (collection order) | Shadows the standard library under two plugins (I2 F8) | CAP-03.a | Rename (W2-L373): W2-69 or W2-67 (P-IS-5) |
| **W1-30:** r13's time-limit case | Flaky (its own 5-second limit) | I2 §2.2 | DEC-823 | W2-57 (W2-M384) |
| **W1-10:** the two 2026-10-03 boundary cases (P16); **W1-16:** `test_this_repository_is_not_indexed_by_the_run`; **W1-19:** the rerank tie case (P30); **W1-22:** `test_validator_rejects_absent_span` (P22), `…_citation_with_out_of_range_lines` (P7); **W1-23:** `TestF2::test_all_citations_reference_valid_spans` (P29) and two valid cases tied to O1 | Weak (the last two valid) | I3 table 2.3 | DEC-182, DEC-322, DEC-374, DEC-036, CAP-15.f | T-A3 or W2-67 (P-IS-7) |
| **W1-24:** 13 weak (`test_all_five_store_representable_levels_in_precedence_order`, `test_the_full_precedence_order`, `test_a_hostile_ticket_id_cannot_escape_the_scratch_directory`, `test_the_brief_summary_is_at_most_2500_tokens`, `test_dry_run_with_brief_computes_without_writing`, `test_each_mandatory_input_lists_its_version_or_hash_constraint`, `test_mandatory_inputs_are_not_ranked_by_retrieval`, `test_precedence_is_not_overridden_by_retrieval_rank`, `test_the_packet_stays_under_the_default_ceiling`, `test_the_token_count_is_consistent_with_the_four_character_rule`, `test_supplementary_is_dropped_before_mandatory_inputs`, `test_the_packet_records_what_was_dropped`, `test_the_packet_indicates_supplementary_is_unavailable_when_the_index_is_down`), plus `test_mandatory_inputs_are_delivered_without_the_semantic_store` (duplicate: build its state) | Weak | P1 to P4, P18, P19, P24, P25; index-less fixture (I3 F3) | CAP-01.a, CAP-15 | The ceiling and indicator cases: W2-04; the rest T-A3 or W2-67 |
| **W1-25:** `test_a_checkpoint_is_stale_by_the_commits_since` (P27), `test_an_old_checkpoint_is_stale_by_age` (P13); the three gc-race cases | Weak; flaky | I3 F3, F9 | CAP-37.c; DEC-887 | T-A3 or W2-67; the fixture fix in W2-67 |
| **W1-29:** `test_injection_says_which_path` (P20), `test_large_context_within_cap` (P10), `test_injects_context_brief_on_startup` (P5), `test_orchestrator_compact_carries_resume_section` (P6), `test_reinjects_on_compact_clear_resume` (P5), `TestSubagentStop::test_block_includes_reason_and_is_once` | Weak | I3 F3, F4 | CAP-15.g, CAP-37 | The SubagentStop case: W2-65; the rest T-A3 or W2-67 |
| **W1-19, W1-21:** the two hit@5 cases at 80 | Outdated | Red at 85 today (I3 F12) | DEC-833 item 1 | W2-32 (P-IS-13) |
| **W2-54:** `test_no_hard_block_check_is_weakened`, `test_only_the_timeout_line_is_added_to_the_declaration`, `test_the_declaration_s_other_keys_are_unchanged`, `test_the_schema_file_is_w2_02_s_byte_for_byte`; `test_the_suite_runs_this_worktree_s_code` | Outdated (base pins); weak | P11: a legitimate comment line turns one red (I3 F2) | DEC-874's reading | T-A3, before W2-06 or W2-12 edits a check declaration |
| **Unit checkpoint:** `test_the_latest_checkpoint_is_the_highest_number_not_the_last_name` (P17); `test_the_watchdog_defaults_are_those_of_dec_321` (valid; O4) | Weak; valid | I3 table 2.3 | CAP-37.f; DEC-281 | T-A3; P-IS-16 |
| **Unit codeintel:** three whole-graph cases (valid); `test_an_error_of_the_tool_is_not_an_empty_answer` (P8) | Valid; weak | I3 F13 | DEC-859, DEC-561 | W2-37 |
| **Unit context:** four `test_dropped_order.py` cases | Valid; outdated under W2-04's refusal | I3 F13 | W2-04 KPI | W2-04's engineer |
| **Unit retrieval:** `test_the_chunking_is_the_carried_one` | Obsolete (skips) | Its reference module was deleted (I3 F10) | W1-17 KPI | W2-13: fixed spans (R6) |
| **W2-54:** the two `shared_gpu` cases | Valid, never run | Deselected unless `-m shared_gpu` (I3 F10) | DEC-773, DEC-798 | The nightly with `-m shared_gpu` |
| **W1-06:** the two ccusage install-command cases | Weak (P06-c) | Miss DEC-202's PATH prefix (I4 §2.2) | DEC-192, DEC-202 | A small W1-06 revision |
| **W1-07:** `test_help_names_every_reserved_command` (P07-1); `test_an_error_envelope_carries_the_session_given` (outdated); the copy-race cases | Weak; outdated; flaky | I4 §2.2, F5 | CAP-28.b; DEC-186; DEC-189 | Small revision or W2-67; the fixture in W2-67 |
| **W1-08:** `test_the_state_classes_are_written_in_one_schema_file_only` (P08-3), `test_no_record_schema_writes_an_id_pattern_of_its_own` (P08-4) | Weak | Read 8 of the 20 schemas (I4 §2.2) | DEC-229, DEC-227 | W2-64 |
| **W1-09:** `test_a_created_ticket_is_the_ticket_the_script_writes`, `test_a_package_that_loads_and_is_closed_does_not_block`. **W1-14:** `test_no_ticket_is_derived_without_a_profile_or_a_class` (outdated) | Weak; outdated | I4 §2.2 | DEC-295, DEC-328, DEC-355 | W2-34 |
| **W1-27:** 40 weak (adoption ×3; `test_w1_27_doctor.py` ×8; `doctor_r5` stale path; `doctor_r7` home-tool sha256; drift ×6; held-out ×2; `isolation_r2`; path compliance ×3; path compliance r2 ×3; rebuild ×5; rebuild r2, r3, r4, r8; recovery check r2 ×3); the old-path case (whole-tree copy); `test_rebuild_does_not_silently_drop_lexical_tables` (duplicate: assert the planted row's fate). **Unit doctor:** `test_check_isolation` | Weak | Key names doctor always prints; doctor unhealthy in the copies; fakes off the PATH (I4 F1) | CAP-06, CAP-07, CAP-25.a, CAP-54.a, DEC-425 | W2-67 or a small W1-27 ticket, before doctor changes |
| **Unit doctor:** `test_match_pattern` (P27-8) | Weak | I4 F3 | DEC-225 | W2-22 |
| **W1-32:** `test_status_has_no_sub_command_and_no_argument_that_acts`; `test_the_plain_form_shows_the_same_parts` (P32-1) | Weak | I4 §2.2 | W1-32 KPI | A small W1-32 revision |
| **W1-33:** `test_only_the_test_designer_may_write_the_acceptance_tests[engineer]` and `[product-spec]` (PG-2); `test_the_auditor_writes_only_the_report_path_of_its_own_ticket` (PG-1); two kernel role-file word checks; `test_the_research_definition_is_the_generated_one` (silent skip) | Weak | I4 §2.1, §2.2, F4 | MR-3, DEC-112, DEC-158 | W2-65 or a small revision; W2-11; W2-57 |
| **W1-34:** `test_the_routing_rule_classes_a_contradiction` (P34-1) | Weak | I4 F15 | CAP-34.a | A small W1-34 revision |
| **W1-35:** 30 weak word checks and 8 outdated functions (+2 cases) | Weak; outdated | I4 F7, F15; PS-1, PS-2, PS-5, PS-6, PS-7, PS-13 | CAP-24, CAP-30, CAP-33, CAP-34; DEC-820 (c), DEC-542, DEC-838 item 2 | W2-11 |
| **W1-36:** 11 weak word checks | Weak | I4 F15; PS-3, PS-11 | CAP-47, CAP-16, CAP-56 | W2-11, or a small revision |
| **W1-38:** `TestToolAbsentOrHanging::test_timeout_handling` (P38-1); the 9 masked cases (3 functions, one is `TestBrokenHeldOutFile::test_broken_file_is_not_green_and_no_path_is_printed`); the session fixture's skip | Weak | I4 F2, F4 | DEC-425 | W2-57's first item (P-IS-6) |
| **W1-39:** `test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured` (outdated); `test_copy_installs_the_hooks_and_keeps_them_executable` (weak) | Outdated; weak | I4 §2.2 | DEC-761 item 1; CAP-44.a | W2-16 (`adbeea77`); a small revision |
| **W1-41:** six weak (incl. `test_an_unknown_artefact_blocks_retirement_too`, P41-c). **Unit adopt:** `test_a_move_out_of_a_native_layout_needs_both_grounds` (PU-c) | Weak | I4 F4 | CAP-06.c, CAP-42.a, CAP-44.j, DEC-449 | W2-52 or a small W1-41 revision |
| **W1-44:** `test_retrieve_returns_lessons_for_ticket_in_scope` (P44-a) | Weak | I4 §2.2 | CAP-14, DEC-424 | A small W1-44 revision |
| **W2-02:** `test_a_record_with_an_unknown_type_is_still_refused` (outdated; W2-64); `test_one_kernel_schema_is_a_decision_entry_…` (outdated; DEC-755 item 5); `test_a_type_whose_schema_file_is_absent_is_reported_unmeasured_and_not_green` (weak, PL202-1) | Outdated; weak | I4 §2.2, F7 | DEC-746 item 6, DEC-755 item 5 | W2-64; the missing row; W2-67 |
| **Moved, not rewritten** (P-IS-6): W1-21's `test_the_check_is_green_when_the_dev_tiers_meet_the_baselines`; W2-54's real-embedder and sandboxed-worker cases; W2-62's live resume; W2-58's five launched-session cases | Valid | Live or real-model cases in the parallel phase (I3 F6; I1 F-2) | DEC-889 item 5 | W2-57 / the nightly |

### 5.3 What the retirements save in all

If the owner takes every retirement of §5.1:
- about 880 s of the serial phase (W1-05's switch-over and W1-25's live file);
- about 530 case-seconds of the parallel phase (about 75 s of wall time, more where a case sat on the tail);
- one paid session fewer in every close and nightly (W1-25's file);
- 28 skips leave every close record.

The moves of §2.4 are the larger part of the saving, and they are already decided (DEC-889 item 5).

---

## 6. The owner decisions needed

**In the order the work needs them.**
- **A. They gate the review point** (W2-66, W2-67, W2-68, W2-57, W2-07 and the re-pin plan):
  1. P-IS-1: W2-66's shared core and map;
  2. P-IS-2: the record-reading set (W2-66, W2-68);
  3. P-IS-3: retire the nested reruns; worksteal after (W2-67, every close);
  4. P-IS-4: W2-07's KPIs;
  5. P-IS-5: the first re-pin's three corrections (W2-65, W2-69, W2-66);
  6. P-IS-6: W2-57's ticket file, the lists and every entry's route out;
  7. P-IS-7: the home of the test revisions (W2-67's card).
- **B. They gate other tickets' starts:**
  8. P-IS-8: W1-42's accepted reds (W2-13, W2-14, W2-19);
  9. P-IS-9: the path-map rule in adopted projects (W2-27; W2-23, W2-22);
  10. P-IS-10: Policy 2 (c)'s base branch (W2-27, W2-29, Wave 3);
  11. P-IS-11: DEC-769 item 3 (W2-21);
  12. P-IS-12: CAP-15's synthesis notes and W2-04's entry criteria (W2-04);
  13. P-IS-13: DEC-833's 85 line (W2-32);
  14. P-IS-14: the A5 record type (W2-52, EXAMIN's A5).
- **C. The rest:**
  15. P-IS-15: the retirements;
  16. P-IS-16: DEC-281's 0.30.

Each package keeps the reports' package ids it merges. None proposes a new round.

---

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

### P-IS-8. W1-42's two accepted reds: keep them reachable, or retire them
*Merges P-I2-1 A and R1. ⚑ The two reports differ.*

1. **Context.**
   - `accepted_reds` lists two W1-42 cases: RETR-X-02 (`fixed_by: W2-13`) and the governance share per programme (`fixed_by: W2-14`) (DEC-757).
   - An entry leaves when its fix closes (DEC-766). Once W2-19 lands, the close of a ticket an entry names refuses while that entry is listed (DEC-762 item 2).
   - DEC-718 item 11 closes the two exceptions on the exit report's conditions: a kept bundle with a named parent expansion, or the owner's ruling; and a measured share in `governance-share.json`.
2. **What happened.**
   - Both cases read only the frozen Wave 1 exit record, unchanged since 2026-10-16 (I2 F1; I3 F1).
   - W2-13's paths and KPI do not reach the case or the bundle, and its ruling (Q-1, the adoption-readiness item AR-9) is not in the register. W2-14's only path is its own evidence folder.
   - The kept bundle fails both possible rulings: it holds 20 unrelated items and no expansion (I3 F1). W1-21 already asserts the "stated gap" outcome on the same scenario (I3 F1).
   - So, as written: either W2-13's and W2-14's closes can never pass, or the entries leave and the reds refuse every later close.
3. **Why it matters.** W2-13 and W2-14 are FULL tickets on Track A's path; a deadlock there stalls the wave.
4. **Options.**
   - **(a) Keep and make reachable** (I2's recommendation).
     - The owner rules Q-1.
     - W2-13's KPI names W1-42's RETR-X-02 case for its test designer, restated to the ruling or fed by a new kept bundle.
     - W2-14's paths gain `docs/plan/wave-1-exit/evidence/governance-share.json` and the exit report's share rows.
     - Cost: a ruling and two ticket edits. Risk: low; the Wave 1 record gains a dated Wave 2 addition, as DEC-718 foresaw.
   - **(b) Retire both cases and both entries, in one owner commit,** after recording the AR-9 ruling (I3 R1 (a); I2's option (b), which I2 calls "equally safe").
     - The requirements live in W2-13's own acceptance tests and W2-14's evidence.
     - Cost: one owner commit. Risk: low; the Wave 1 record stays as history.
   - **(c) Widen W2-13 and W2-14 to rewrite the Wave 1 evidence.** Risk: high; it rewrites a closed record that the exit decision rests on (I3 R1 (c)).
5. **Classification:** I2 F1 and I3 F1, "Ordinary work: yes; Consequence: other (fails closed)". No round.
   **Recommendation: (b),** with the AR-9 ruling recorded first. I2 judges (a) and (b) equally safe; I3 prefers (b). I add one reason: under (a), a closed Wave 1 suite stays coupled to two open Wave 2 tickets. Confidence: medium-high. If the owner wants the Wave 1 report to remain the place the exceptions close, take (a).
6. **What it blocks.** W2-13's and W2-14's closes, and W2-19's test design (decide before its test designer starts). Waiting costs nothing until then: the cases fail as accepted, in 0.1 s.

### P-IS-9. The path-map rule in adopted projects: the check, the matcher and the carrier
*Merges P-I2-4 and I4 F3. ⚑ The reports name different carriers.*

1. **Context.**
   - DEC-225's rule: every tracked path in exactly one namespace.
   - `core-pathmap` is the hard-block check of CAP-38.b's path-map family. Row W2-M214 is triaged to W2-23.
   - EXAMIN's adoption on a copy (W2-27) needs `gov check` and `gov doctor` green. So does CAP-44.h's lite adoption verdict (Contract v4.2).
2. **What happened.**
   - `core-pathmap` measures nothing on a real path map (I2 F3; PF3 passes 543 cases).
   - `gov doctor`'s matcher (`fnmatch`) never reports an unclassified path here (I4 F3; P27-8).
   - W1-08's test is the only working check, and an adopted project has none.
   - W2-23's paths do not reach `src/gov/check/pathmap.py` (I2 F3).
   - Fixed as the row reads, with the same matcher, the check would be red on every close (I4 F3).
3. **Why it matters.** EXAMIN's path-map family would be GREEN for any file in no namespace: the defect that refused W2-02's close here.
4. **Options.**
   - **(a) A small new STANDARD ticket before W2-27** (I2's choice):
     - `src/gov/check/pathmap.py` and `tests/unit/check/**`;
     - the check reads the mapping form with one matcher in DEC-225's language (I4's condition);
     - it is unmeasured, never GREEN, when the map is missing, unreadable or of another shape;
     - its test designer revises W1-26's two path-map cases and DEC-436's namespace case to assert the check's own finding;
     - W2-22 takes doctor's matcher and `test_match_pattern`.
     - Cost: about 30 lines, three cases, one STANDARD close.
   - **(b) Widen W2-23** with the check's file, its tests and a KPI naming the matcher (I4's choice; I2's option (b)). Same work inside a broad FULL ticket. Risk: it lands after W2-27 starts.
   - **(c) Leave it with W2-23 as it stands.** Risk: no ticket can fix it.
5. **Classification:** I2 F3 and I4 F3, "Ordinary work: yes; Consequence: fails open" for the checks: feature-gated for adopted projects, an entry criterion of W2-27 (DEC-803). For the forward risk, "other (fails closed)".
   **Recommendation: (a),** with I4's matcher condition as a KPI, whichever carrier. Confidence: medium-high.
6. **What it blocks.** W2-27's start, as an entry criterion. Waiting costs nothing until then.

### P-IS-10. Policy 2 (c)'s base branch is written into the guard (P-I1-9)

1. **Context.** DEC-820 (c) and DEC-826 Q2: the test designer is refused the files its ticket's branch changes against its base. The kernel ships this guard to adopted repositories, EXAMIN first.
2. **What happened.** The base is a constant, `w2/integrate` (`src/gov/guard/reads.py:36`). Without that branch, the rule refuses nothing for the test designer, silently. W2-58's case pins that default (I1 F-12).
3. **Why it matters.** In EXAMIN, or here in Wave 3 on another branch, a test designer would read its ticket's implementation with no refusal and no record. That is the independence MR-3 and CAP-38.c rest on.
4. **Options.**
   - **(a) The base becomes a path-map setting,** read by the guard. A project that declares the rule without it, or names a branch that does not exist, is refused for the test designer (fail closed). W2-58's case is revised. Carried as W2-27's entry criterion. About 20 lines. Changes: the path map's schema and the guard (CAP-33 applies).
   - **(b) Document that every adopted repository names its integration branch `w2/integrate`.** Risk: forgotten.
   - **(c) Wave 3's hardening pass.** Risk: EXAMIN's adoption runs with the rule off.
5. **Classification:** "Ordinary work: yes; Consequence: fails open (feature-gated: an entry criterion of W2-27, W2-29 and Wave 3's start, DEC-803)" (I1 F-12).
   **Recommendation: (a).** Confidence: medium-high.
6. **What it blocks.** W2-27. Waiting costs nothing until a repository without `w2/integrate` launches a test designer.

### P-IS-11. DEC-769 item 3: what "its own acceptance folder" means for revision work (P-I1-6)

1. **Context.** DEC-769 item 3 (owner): the independent test designer writes only `tests/acceptance/` plus its own WBS id. It is folded into W2-21, not started.
2. **What happened.**
   - W2-21's card carries the item; its ticket file, sources and paths do not, and the guard rule lies outside them (I1 F-4; checked in `DAEO-1ahb.md`).
   - Five tests pin the old whole-folder rule.
   - Revision rounds routinely have a designer edit other tickets' folders (DEC-874, DEC-875), and this review sends many more revisions that way (P-IS-7).
3. **Why it matters.** Built as written, the rule refuses every revision round. Left unbuilt, a decision stands with no carrier.
4. **Options.**
   - **(a) "Own folders" means** its ticket's own folder plus the folders its ticket names in `allowed_paths`.
     - W2-21's ticket file gains the KPI, DEC-769 in its sources, `src/gov/guard/decide.py` (the designer's rule only), and the five tests as a revision batch.
   - **(b) The sandbox only** (launched designers held; the guard unchanged). Smaller; an unsandboxed designer helper is not held.
   - **(c) Re-baseline DEC-769 item 3** to "the folders its ticket names".
5. **Classification:** "Ordinary work: yes; Consequence: fails open (feature-gated: an entry criterion of W2-21, DEC-803)" (I1 F-4).
   **Recommendation: (a).** It also lets P-IS-7's revision tickets work under the rule. Confidence: medium.
6. **What it blocks.** W2-21's test design. Waiting costs nothing until W2-21 starts.

### P-IS-12. CAP-15's synthesis notes against W2-04's refusal, and W2-04's entry criteria
*Merges I3 O1 with I3 F16, F17, F13.*

1. **Context.**
   - CAP-15's acceptance (Contract v4.2): when a ticket's evidence exceeds the packet's ceiling, the packet carries synthesis notes that cite source ids.
   - W2-04's decided KPI: when the mandatory inputs alone exceed the ceiling, `gov context` refuses with a named error. DEC-860 adds ranked batches for the supplementary part.
2. **What happened.**
   - Nothing calls the synthesis module; it ignores its budget and raises on real gaps; W1-23's cases cannot see either (I3 F11).
   - Separately, W2-04 is where three context gaps belong: the silently empty packet (§3.1 A), lower-case status words (§3.2 I), and W1-24's ceiling case, which passes while `gov context` reports `ok: true` at 1.19 million tokens against 6,000 (I3 F13, F16, F17).
3. **Why it matters.** W2-04's test designer will start from W2-04's KPI, not from CAP-15. Briefs are to be built with `gov context` (DEC-836).
4. **Options** (DEC-105).
   - **Apply now:** W2-04 also writes synthesis notes when mandatory inputs exceed the ceiling, and W1-23 is revised to real bundles. About 100 to 150 lines. Risk: a second mechanism beside refusal and batching.
   - **Defer:** CAP-15's clause becomes a Wave 3 row. Risk: the clause stays unmet through Wave 2.
   - **Re-baseline:** CAP-15's acceptance says what W2-04 and DEC-860 decided (refusal with a named error; ranked batches), through a CIT-P; W1-23 stays as a library test or is retired. One Contract change.
   - With any of the three: W2-04's entry criteria are the three gaps above, with its paths gaining W1-24's two files (I3 §4.5).
5. **Classification:** I3 F11, "Ordinary work: yes; Consequence: other". I3 F16 and F17, "Ordinary work: yes; Consequence: fails open": they ride along in W2-04 (DEC-802), as its entry criteria. No round.
   **Recommendation: re-baseline,** with the entry criteria. Confidence: medium.
6. **What it blocks.** W2-04's test design. Waiting costs a test designer's guess.

### P-IS-13. DEC-833's line of 85: in what order W2-32 raises it (I3 O2)

1. **Context.** DEC-833 item 1: CAP-10's line stays 85, and W2-32's test designer corrects the tests at 80. Item 4: a figure short of 85 after W2-15b is a named residual, not a new round.
2. **What happened.**
   - The rehearsal measured W1-19 at 83.33 and W1-21 at 81.67.
   - The hard-block retrieval check reads its line from `retrieve_baseline.yaml` (80); raised there, `gov check` goes red and every close stops at the gate.
   - W2-54's third case reads a closed record's figure and should be retired, not corrected (I3 F12, R5).
3. **Why it matters.** As ordered, the correction stops every close.
4. **Options.**
   - **(a) Raise the tests and the baseline once a measured run reaches 85,** with the reason recorded.
   - **(b) Raise W1-19's and W1-21's cases to 85 now as two accepted reds** (`fixed_by: W2-15b`, two owner entries); keep the baseline at 80 until W2-15b.
   - **(c) Raise everything now.** Every close blocked.
5. **Classification:** "Ordinary work: yes; Consequence: other (fails closed under (c))" (I3 F12). No round.
   **Recommendation: (b),** as I3 recommends: it applies DEC-833 now, keeps the closes open, and shows the shortfall in every close record. Confidence: medium. (It is the one proposal that adds to a list; DEC-766 requires it to come as a package, as here.)
6. **What it blocks.** W2-32's test design. Waiting costs nothing until W2-32 starts.

### P-IS-14. One record type for two verdicts: A5's review and CAP-44.h's lite verdict (P-I4-4)

1. **Context.** A5 is the independent review of the path map before any file moves; it accepts only `verdict: pass`. W2-02 gave the type `adoption-verdict` to CAP-44.h's lite verdict, with three health verdicts and required `conditions` (DEC-741, DEC-746 item 4).
2. **What happened.** W1-41's fixture writes the A5 record as `type: adoption-verdict`. A record A5 accepts fails core-schema wherever core-schema reads it; a record core-schema accepts is refused by A5. The cases stay green only because A5 never reads `type` (I4 F9).
3. **Why it matters.** EXAMIN's adoption (W2-26 to W2-28) would stop at the review step either way.
4. **Options** (DEC-105).
   - **(a) Apply now:** A5 gets its own record type, for example `path-map-review`, and A5 reads it; W1-41's two fixtures are revised. A small round before W2-52 merges.
   - **(b) Defer:** the same fix as W2-52's entry criterion (DEC-803).
   - **(c) Re-baseline:** A5 writes CAP-44.h's form. It mixes a review before any move with a health verdict after.
5. **Classification:** "Ordinary work: yes; Consequence: other (fails closed)" (I4 F9). No round.
   **Recommendation: (b), unless EXAMIN's adoption reaches A5 before W2-52 merges; then (a)**, as I4 recommends. Confidence: medium.
6. **What it blocks.** Nothing today. Waiting costs a stopped adoption if A5 runs first.

### P-IS-15. The retirements
*Merges P-I1-1 to P-I1-4, P-I1-7, P-I2-5 to P-I2-7, R2 to R5, P-I4-1 to P-I4-3, and R6 (a rewrite). The nested reruns are P-IS-3; W1-42's reds are P-IS-8.*

1. **Context.** Retiring a test is the owner's decision; each comes with its evidence (DEC-889 item 16 d). §5.1 lists every proposed retirement with its evidence.
2. **What happened.** The reports propose retiring about 70 functions, or about 90 with the helper's 22 redaction cases (P-I1-3):
   - obsolete records of finished transitions (W1-01, W1-05);
   - rules Policy 2 removed (`docs/source`, DEC-385, the helper's redaction);
   - duplicates (W1-07's three whole-tree groups, W2-50's large store, I3's 22, the unit containment and install twins, W1-30's containment case);
   - tests that read their own closed ticket's evidence (W2-54's, W2-62's);
   - a test that cannot see the hook it names (W1-25's live file);
   - two tests for retired settings (W1-49, W1-26's exit case).
3. **Why it matters.** About 880 s of the serial phase (with P-IS-3) and about 530 case-seconds of the parallel phase; 28 skips; a paid session; and fewer double edits when a later decision touches them (§5.3; I3 R3).
4. **Options.**
   - **(a) Retire all of §5.1** in one test-designer commit per area under the owner's word, each with a `Rewrite-Reason:` that names the owner's retirement and its package.
     - First, T-A3's two merges (W1-20's and W1-21's extra assertions into their twins).
     - Retire W2-50's duplicate together with W2-69's revision.
     - P-I1-2's deny rules go with the settings regeneration.
     - Add R5's rule to the test-design skill: a test that greps its own ticket's evidence record retires at that ticket's close.
   - **(b) Retire only the costly and the misleading:** W1-07's three groups, W2-50's duplicate, W2-54's six, W1-25's live file, W1-01's skipped cases. Keep the rest.
   - **(c) Keep them.**
   - **Two choices inside (a):**
     - P-I1-3, the helper's redaction: keep it as defence in depth, with a register line, or retire it (I1 recommends keeping it if the owner wants the helper discreet);
     - R6, the chunking case: rewrite it with fixed spans in W2-13, not retire it.
5. **Classification:** for every item, "Ordinary work: yes; Consequence: other" (I1, I2, I3, I4 packages). No round.
   **Recommendation: (a).** Confidence: high for the duplicates and the obsolete records; medium for P-I1-3 and R4.
6. **What it blocks.** Nothing. Waiting costs their time per close, the 28 skips, a paid session, and noise.

### P-IS-16. DEC-281's context threshold of 0.30, under DEC-838 (I3 O4)

1. **Context.** DEC-281 gave `gov checkpoint --watch` a default `--max-context` of 0.30, "under DEC-208, DEC-237". DEC-838 changed those two (no compaction threshold). DEC-281 is not marked.
2. **What happened.** The default stands (`src/gov/checkpoint/command.py:20-21`), and one builder test pins it. Nothing passes a utilisation today: the close passes none (I3 F14, O4).
3. **Why it matters.** A superseded basis survives without a recorded reason (DEC-866).
4. **Options.**
   - **(a) Keep 0.30 with a recorded reason:** a reminder at 30 % of the window is a handover aid, not an early stop.
   - **(b) Mark DEC-281 changed,** and make the default "context not judged".
   - **(c) Derive it from the model's window.**
5. **Classification:** "Ordinary work: yes; Consequence: other" (I3 F14). No round.
   **Recommendation: (a),** recorded by the orchestrator under its delegation; the owner may overturn it. Confidence: medium.
6. **What it blocks.** Nothing.

### Needs no new owner decision (standing orders or delegation)

- **Mark the status lines DEC-866 requires** (orchestrator, DEC-866 item 1; I1 F-3, I4 F8):
  - DEC-090, DEC-236, DEC-385 (with P-I1-4), DEC-508, DEC-525, DEC-548, DEC-553, DEC-557, DEC-573, DEC-575, DEC-723;
  - correct the stale texts I3 F14 lists (W1-49's failure message, W1-29's README, W1-18 and W1-21 notes).
- **The ratchet's reading of both lists as a pre-close gate step**, under DEC-895 (I4 F14).
- **Ticket and card edits that name the valid tests a planned ticket will turn red:** W2-66, W2-07, W2-57, W2-34, W2-11; and row W2-M357 for W1-27's case (I2 F9; I4 F16).
- **Rows and plan corrections:**
  - row W2-L164's two context residuals moved to W2-04 (I3 F17);
  - a row for DEC-755 item 5 (I4 F7);
  - W2-M332's target date (DEC-890; I1 §4.3);
  - the corrections to lens H's report (I4 F11).
- **Disk space:** I4's folder `/tmp/gov-os-assessment-I4/tmp/bt/` holds about 5.3 million files. On 2026-10-22 it held the shared disk's inodes at 94 to 98 % in use; I4's own `rm` was refused twice (I4 §1.3). Its removal is an orchestrator act, before the next close or rebuild.

---

## 7. Disagreements and limits

### 7.1 Where the reports disagree

| Question | One report, and its evidence | The other, and its evidence | My reading |
|---|---|---|---|
| W1-42's two accepted reds | I2: valid, a known red rightly listed; make them reachable (P-I2-1 A). It rests on DEC-718 item 11: the Wave 1 report is where the exceptions close | I3: obsolete; retire them with their entries (R1). It rests on: they read only a frozen record, no code; the kept bundle fails both possible rulings; W1-21 already asserts the "stated gap" outcome | Both see the same deadlock. I recommend retiring (P-IS-8), the owner's call between the two places the exceptions close |
| Is the record-reading gap a fail-open? | I2 F6, I3 F5: yes, feature-gated. They rest on DEC-883 item 3's reuse, and on lens H finding 18 (three record-made reds in one day) | I4 F6: "other", found late, because the nightly stays (DEC-880 (c)) | Fails open: the reused close has passed before the nightly sees the red (P-IS-2) |
| The carrier of the path-map fix | I2: a small new ticket, or widen W2-23 (P-I2-4) | I4: W2-23 for the check, W2-22 for doctor's matcher; any fix must use DEC-225's matcher, or it is red on every close (F3) | Either carrier, with I4's matcher as a KPI (P-IS-9) |
| The home of the weak-test revisions | I2: widen W2-67 (P-I2-3) | I3: a small ticket T-A3, or fold into W2-67 (§4.5). I4: the open tickets that hold the files, else small tickets or W2-67 | Ride along where an open ticket holds the file; W2-67 for the rest (P-IS-7) |
| `TestStopHook::test_no_ticket_returns_immediately` | I1: weak; revise in W2-65 (F-6) | I3: weak; revise in T-A3 | W2-65: its engineer holds `tests/unit/hooks/**`, and builder tests are the engineer's |
| W1-02's and W1-05's p95 `load_sensitive` entries | I1: still justified. They fail whenever the machine is loaded, pass on a quiet one, and the entry is the net if the quiet window breaks (§4.3) | I2: the entry adds nothing while the case runs serially; it is a second try under the same condition, a narrow fail-open for an intermittent latency fault (F14) | Both measured the same behaviour. Keeping or dropping the two entries is the owner's call (P-IS-6). The fix is W2-M332 with a date |
| The record readers in area 1 | I1's §2.2 rows add the MR-3 history test and W2-58's evaluation-set case to the set | I1's own §4.1 says those paths are fingerprinted as code, so reuse does not hide them | §4.1's reasoning holds if the path map and git history are code. W2-68's draft must decide whether the path map is a record (P-IS-2) |
| How a parallel case-second converts to close time | I1, I3: about a twentieth (20 workers) | I2, I4: the measured 0.142 (13,417 case-seconds in 31.8 minutes) | I use 0.142 throughout (§2.1) |
| Severity scales | I1 calls F-1 high, though it fails closed. I4 calls "high" any yes/yes finding | — | Severities are not comparable across reports; I rank by the two lines only |

Overlaps without disagreement: the gc race (I3 F9, I4 F5); the W2-50 close's refused entry (I2 F11, I4 F14); W2-58's refused close (I2 F13, I4 F17, decided by DEC-896); the live cases in the parallel phase (I1 F-2, I3 F6); the nested runs (I1 F-5, I2 F5); the W1-46 entries' network cause (I1 F-1, I2 F10).

### 7.2 Limits

**What none of the four could review.**
- 2,543 functions of areas 1 and 2 outside the risk-first steps and the samples (§2.5).
- Live sessions were not run in any area; their verdicts rest on recorded closes and the rehearsal.
- No auditor ran the whole estate in the close's form inside the close's quiet window. The machine was shared by the four auditors and the close queue, at 1-minute loads of 13 to 151. So "alone" meant one pytest process, not a quiet machine, and every timing verdict names its load (I1, I2, I3, I4 Limits).
- A close keeps no failure text (`--tb=line`), so two recorded causes could not be found: W1-07's `[doctor]` red and the exact network error of W1-46's hosts (I4 F5; I1 F-1).
- The mutation sample of area 3 ran 12 of 36 mutants (I3 §2). Area 4 made no rebuild and asked no retrieval question (I4 §1.3).
- W2-69's work was not reviewed: its ticket opened after the reviews' head (§4).
- Retrieval's own correctness on the register was not tested by lens I. I3 saw every register item it returned carry the id DEC-891, and I2 saw the same. I checked the decisions my recommendations rest on against the register itself (DEC-757, DEC-762, DEC-766, DEC-813, DEC-862, DEC-866, DEC-880 to DEC-897); other ids are cited as the reports give them.

**My own limits.**
- I ran no test, by rule, and settled no disagreement by running one.
- `gov retrieve` answered none of my questions: twice it returned `FACET_UNAVAILABLE` with the lexical and semantic facets "stale". The questions were which decision limits the test designer to its own folder, and what DEC-889 decides about W2-57's lists (with `--id DEC-889`). A rebuild would be a write, which my brief forbids, so I took every fact from the register, the cards, the ticket files and the path map directly.
- The first `gov retrieve` answer was saved to my session's scratch folder, outside the repository; it is my only write besides this file.
- Several carriers named "mine" (W2-44, W2-12, W2-65 for the unit hooks, W2-69 for W2-L373) come from my reading of ticket files' allowed paths, not from a report.
- Figures I derived, not measured: the serial time of W1-46's live file (from I1 §3), the combined totals, and the sample-based estimates of §2.5.

---

## Appendix: every finding, with its two lines

Each line is the report's own classification, shortened. "→" gives where it goes. Findings merged above are listed once.

| Finding | Ordinary work | Consequence | → |
|---|---|---|---|
| I1 F-1: W1-46's host cases fail on the network; W2-63's close refused | Yes: every close runs them | Other (fails closed) | P-IS-6 |
| I1 F-2: W2-58's live sessions in the parallel phase | Yes: every close runs them | Other (fails closed) | P-IS-6 |
| I1 F-3: the read-rule decisions Policy 2 replaced are unmarked | Yes: agents read entries literally | Other | Orchestrator (§6, no decision) |
| I1 F-4: DEC-769 item 3 missing from W2-21 | Yes: designers revise other folders | Fails open (gated) | P-IS-11 |
| I1 F-5: two nested reruns cost 15 min per close | Yes: every close | Other | P-IS-3 |
| I1 F-6: three weak unit tests | Yes for the restore label; no for the other two | Fails open, latent (restore); other | §3.3; §3.4 |
| I1 F-7: W1-50's live cases lack DEC-784's fix | Yes: closes run from a Claude session | Other (fails closed) | W2-57 |
| I1 F-8: retired rules still tested | Yes | Other | P-IS-15 |
| I1 F-9: glob-named entries, Edit rules unmeasured | No: such files are rare | Fails open in principle | Wave 3 row; W2-40 |
| I1 F-10: no p95 case for a designer's read | Yes | Other | W2-57 |
| I1 F-11: duplicates that are the two slowest cases | Yes | Other | P-IS-15; W2-67 |
| I1 F-12: the base branch is a constant | Yes | Fails open (gated) | P-IS-10 |
| I1 F-13: stale names and constants; the pause tripwire | Yes (names); no (tripwire) | Other | Rows |
| I1 F-14: the 5-second bound and 20-second deadline break under load | Yes: every close | Other (fails closed) | W2-57 |
| I2 F1 = I3 F1: W1-42's reds cannot leave | Yes: closing W2-13, W2-14, W2-19 is ordinary | Other (fails closed) | P-IS-8 |
| I2 F2: W1-30's first-round cases refused for a missing checkpoint | Yes: an engineer reads the case named after a gate | Other | P-IS-7 |
| I2 F3 (with I4 F3): the path-map check measures nothing | Yes: a record copy in no namespace refused W2-02's close | Fails open (the check); other (the tests) | §3.1 B; P-IS-9 |
| I2 F4: W2-53's cases in the old entry form; field rule untested | Yes: W2-19 rewrites the check | Other (fails closed) | W2-19 |
| I2 F5: unit nested runs with a 60-second limit | Yes: heavy load or a new order | Other (fails closed) | P-IS-3 |
| I2 F6 (with I3 F5, I4 F6): record readers outside the set | Yes: record commits daily | Fails open, gated (I2, I3); other (I4) | P-IS-2 |
| I2 F7: `gov check`'s exit cases cannot fail | Yes | Other | P-IS-15; P-IS-7 |
| I2 F8: the `secrets` test package shadows the standard library | Yes: plugins are planned glue | Other (fails closed) | P-IS-5 |
| I2 F9: planned tickets will turn valid cases red | Yes: planned work | Other | §4 |
| I2 F10: three entries' reasons are not their cause | Yes | Other | P-IS-6 |
| I2 F11 (with I4 F14): an owner entry counted for nothing | Yes: every new entry goes the same way | Other (fails closed) | W2-19; gate step |
| I2 F12: W2-57's paths cannot reach four entries | Yes: W2-57 is planned | Other (fails closed) | P-IS-6 |
| I2 F13 (with I4 F17): closes refused after full runs, on commit findings | Yes: ordinary record commits | Other (fails closed) | P-IS-4 |
| I2 F14: 26 entries are a second try alone; W2-57's card against DEC-889 | Yes | Other | P-IS-6 |
| I3 F2: W2-54's base pins | Yes: W2-06, W2-12 edit those files | Other (fails closed) | P-IS-7 (before W2-06, W2-12) |
| I3 F3: 30 planted faults; 19 caught by nothing | Yes (P3 no) | Fails open (P13, P8, P23, P22), loses work (P9), latent; other | §3.3; P-IS-7 |
| I3 F4: the SubagentStop case and W2-65's scope | Yes | Loses work; other for W2-65 | P-IS-5 |
| I3 F6: live and real-model cases in the parallel phase | Yes | Other | P-IS-6 |
| I3 F7: W1-16's serial block is mostly cases with no daemon | Yes | Other | P-IS-6 |
| I3 F8: W1-19's warm p95 measures more than a query | Yes | Other | P-IS-6 |
| I3 F9 (with I4 F5): per-test copies race git's gc | Yes: a large untracked folder is ordinary | Other (fails closed) | W2-67 |
| I3 F10: tests that never run | Yes | Other | P-IS-15 (R6); the nightly |
| I3 F11: synthesis notes have no product path | Yes: briefs are built with `gov context` | Other | P-IS-12 |
| I3 F12: raising hit@5 to 85 stops every close | Yes: W2-32 is told to | Other (fails closed) | P-IS-13 |
| I3 F13: added behaviour untested; W2-37's and W2-04's scope | Yes | Fails open (lens B's F4; traversal, gated); other | §3.2 H, J; W2-37; W2-04 |
| I3 F14: superseded decisions stated as current | Yes | Other | Orchestrator; P-IS-16 |
| I3 F15: W2-54 repeats `gov check` | Yes | Other | P-IS-2; P-IS-15 |
| I3 F16: the silently empty packet | Yes: a fresh clone has no index | Fails open | §3.1 A; P-IS-12 |
| I3 F17: two DEC-579 residuals sent to the wrong ticket | Yes | Fails open | P-IS-12 |
| I4 F1: W1-27's doctor suite cannot fail | Yes: three tickets change doctor | Fails open | §3.3; P-IS-7 |
| I4 F2: the rulesync probe's limit; the silent skip | Yes: every close | Fails open | §3.1 C; P-IS-6 |
| I4 F4: A8's guard untested; four weak cases held elsewhere | Yes | Fails open (A8); other | §3.3; W2-52 |
| I4 F7: 13 outdated tests, three groups with no carrier | Yes | Other | W2-11; a row |
| I4 F8: five changed entries unmarked | Yes | Other | Orchestrator |
| I4 F9: one record type, two meanings | Yes: an adopter writes A5 as the README says | Other (fails closed) | P-IS-14 |
| I4 F10: W1-07's three whole-tree duplicates | Yes | Other | P-IS-15 |
| I4 F11: three corrections to lens H | No: statements, not behaviour | Other | Orchestrator |
| I4 F12: the map's reach beyond declared paths | Yes | Other (I4); fails open bounded by the nightly (mine) | P-IS-1 |
| I4 F13: `core-authority` drops `ACTIVE_UNAPPROVED` | Yes | Fails open, latent | W2-12 |
| I4 F15: a fifth of the skill checks find a word that stays | Yes: W2-11 edits the skills | Fails open | W2-11 |
| I4 F16: valid cases that planned changes will turn red | Yes | Other | §4 (orchestrator) |
