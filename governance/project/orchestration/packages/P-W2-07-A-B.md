# P-W2-07-A and P-W2-07-B — W2-07's run 1 stopped short of DONE: the scratch budget against a full run, and 196 earlier cases its KPIs turn red (P1)

From: the W2 orchestrator, 2026-10-23, from W2-07's lead return (run 1, `log/W2-07-A5-run1.json`). Gates: W2-07's DONE, and through it W2-66's merge order (W2-07 merges first, DEC-899 item 2) and the first re-pin. Classification of the findings: Ordinary work: yes, because every lead runs the full regression before it returns and W2-07's KPIs are the owner's. Consequence: other (a resource limit and fail-closed reds; nothing fails open).

## 1. Context

- **W2-07, the close by ticket class with the commit gates first,** is built and tested. Its own 40 acceptance cases pass. The work:
  - a new `src/gov/close/gates.py`;
  - `run()` reordered: commit gates, then the pre-close gate (collection, `gov check`, checkpoint), then the disk floor, then the tests;
  - the declared `acceptance_tests.path` read;
  - decision records measured by their decision;
  - complete repair tickets.
- **What it lacks:** the lead's full verification in the close's form, which DEC-880 and DEC-889 item 6 require before every return.
- **DEC-898 gives a lead 20 GB and 1,000,000 files and folders** for itself and its workers. A session over budget stops its heavy work and returns.

## 2. What happened, with the evidence

**A. The budget.**
- The full parallel run started at 13:27, at a load of up to 95 (shared with W2-69's runs).
- By 13:33, about 13.6 % through, the lead's temp folder held 1,062,156 inodes and 9.5 GB (`/tmp/gov-os-lead-W2-07/pytest-of-usain/pytest-1`). The lead stopped the run there, as DEC-898 says.
- Under pytest's own retention, every test's `tmp_path` stays until the session ends. The suites make whole-tree copies, so a full run needs several million inodes: more than a lead's 1,000,000, and more than the nightly's 2,000,000.
- The lead could not remove the folder itself: `rm -rf` on it needs a permission a non-interactive session cannot get. Its test designer and engineer met the same refusal.
- The folder is still there. No process holds it (`lsof`).

**B. The 196 cases.** The engineer's run on `53ec666a`:
- W2-07: 40 passed;
- W1-30: 317 passed, 192 failed, 3 errors;
- W2-53: 56 passed, 1 failed;
- unit close and telemetry: 463 passed.

The causes:
- **175 W1-30 cases:** the in-close `gov check` (KPI 5, DEC-868) now refuses every W1-30 fixture project, because those fixtures are RED at hard-block checks (adapter-portability `KERNEL_EMPTY`, index-freshness, retrieval-regression).
- **20 cases** hold the old gate order (DEC-492's "every gate asked; one counted refusal"), which DEC-868 item 3 changed: a gate refuses at once, before any test, spending no attempt.
- **1 case** holds the repair ticket left untracked, which KPI 8 changes (AR-9, W2-L209).
- These files are outside the W1-30 files the ticket names for its test designer, so under MR-3 the lead stopped.
- DEC-492's status line had no "Changed by" note; this package's commit adds it (DEC-866).

## 3. Why it matters

- **A:** no lead can return DONE on a full run inside today's budget. W2-66 and W2-69, running now, will meet the same limit.
- **B:** W2-07 must merge before W2-66 and ride the first re-pin. Its own close would refuse on these 196 reds.

## 4. Options

**P-W2-07-A, the budget against a full run:**
- **(a) `-o tmp_path_retention_policy=failed`, measured first.**
  - A passing test's `tmp_path` is removed as the test ends; only failed tests' folders stay. This is pytest's own clean-up, a one-line rule for leads (the common brief), the nightly and, through W2-66, the close.
  - **First, a measured trial:** one full run in the close's form on the nightly's clone, recording the peak inodes and checking the result is unchanged.
  - Cost: about 1.5 hours of machine time. Risk: low. A test that reads another test's leftover folder would show red, which the trial finds.
- **(b) Raise the lead budget for the verification window** to the measured peak, capped (proposal: 5,000,000 inodes and 50 GB, until (a) is measured). Cost: none now. Risk: the disk's floor of 10,000,000 inodes free is then the only net, with three leads at once.
- **(c) An allow rule for a lead to remove its own temp folder by literal path** (`/tmp/gov-os-lead-<its W2 id>`). This is a settings change, so it goes in the regeneration after the first re-pin. Until then, the orchestrator removes a returned lead's temp folder.

**P-W2-07-B, the 196 cases:**
- **(a) Widen W2-07's test-designer revision batch.** A ticket-file commit with its Task (DEC-896) names:
  - (i) W1-30's shared fixture (`w1_30_support.py`, `conftest.py`), given a check set green at `gov check`, with `Rewrite-Reason: DEC-868 item 1 (b)`. It clears the 175;
  - (ii) the 20 gate-order cases, with `Rewrite-Reason: DEC-868 item 3`;
  - (iii) the one repair-ticket case, with `Rewrite-Reason: KPI 8`.
  Each is revised by its independent test designer, with no expectation lowered. Cost: one designer round. Risk: low.
- **(b) A separate test-revision ticket.** W2-07's close would wait for it.
- **(c) Re-baseline KPI 5,** so `gov check` runs only when governance files change. This undoes part of DEC-868, and turns W2-07's own red-check case red.

## 5. Recommendation

- **A: (a) and (c), with (b) as the bridge.**
  - Now: I remove `/tmp/gov-os-lead-W2-07/` (no process holds it; it is newer than 24 hours, so the sweep's rule does not cover it, hence this ask).
  - Leads' verification gets the cap of (b) until (a)'s trial reports.
  - (a)'s trial runs in the first quiet window.
  - (c)'s allow rule rides the settings regeneration.
  Confidence: medium-high.
- **B: (a).** Confidence: medium-high.
- **P-W2-07-C (non-blocking)** I record as delegated, accepting the lead's six interface readings:
  - evidence in `acceptance_tests.evidence`;
  - a probe's findings as a frontmatter list named with their rows;
  - the close commits the repair ticket alone;
  - unnamed classes judged on their acceptance tests;
  - baseline refusals read as gate refusals;
  - a name clash between suites in one process not checked.
- **Rows:**
  - a decision-record commit naming several decisions counts if any one is ACCEPTED;
  - row W2-M149 contradicts DEC-487 and DEC-490 (could-not-measure is uncounted);
  - a refused close now commits its repair ticket, so the next close needs a rebuild.

## 6. What it blocks, and what waiting costs

- **Blocks:** W2-07's DONE. Through it: W2-66's merge order and the first re-pin.
- **A also blocks** every lead's full verification, W2-66's and W2-69's included, as soon as they reach it.
- **Waiting costs** about the time of a lead round per day of delay on the critical path. Nothing fails open.
