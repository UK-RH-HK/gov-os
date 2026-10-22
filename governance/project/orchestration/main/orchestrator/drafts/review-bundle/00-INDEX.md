# The review bundle (DEC-889 item 14): drafts, results and the decisions they need

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
