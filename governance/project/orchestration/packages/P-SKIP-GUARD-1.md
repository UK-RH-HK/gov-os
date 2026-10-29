# P-SKIP-GUARD-1 — The interim skip guard's fixed count of 31 cannot hold once closes are scoped (P2)

From: the W2 orchestrator, 2026-10-24, at W2-66's merge (`c60c9704`). Gates: every close after the first re-pin, beginning with the merged-not-closed tickets (W2-58, W2-63, W2-70, W2-07, W2-69, W2-66). Nothing is stopped today. Classification: ordinary work yes; consequence other (fails closed: the queue stops, nothing passes).

## 1. Context

- **DEC-899 item 7 (yours):** until W2-57 lands, after each `gov close` the queue reads the close's skip count. A count other than the expected 31 stops the queue, as a P1, before the close's outputs are committed.
- **What it guards (lens I's I4 F2):** W1-38's `rulesync_bin` fixture skips silently with "rulesync is not installed" when rulesync's version probe times out. That turns up to 40 W1-38 cases into skips.
- **The guard** (`tools/skip_gate.py`) counts the skips of the close's full parallel regression. If the close ran no full regression, it stops the queue.

## 2. What happened

- **W2-66 is merged:** after the re-pin, a close runs only the suites its change can affect. A scoped close has no full parallel regression, so the guard stops the queue on every scoped close.
- **Even a full close changes the count:** removing `test_inputs` from the path map at the merge (DEC-903 item 4, `8f56ada1`) turns one W2-66 case into a deliberate skip. Its reason is "the path map no longer holds test_inputs".
- **The close's evidence block** (W2-66, `src/gov/close/evidence.py`) lists every skip with its test id and its reason, from each run's JUnit XML.

## 3. Why it matters

Left as it is, the first close after the re-pin stops the queue, and so does every one after it. The guard fails closed, but it blocks the closes the re-pin exists for.

## 4. Options (DEC-105)

- **(a) Guard on the reason, not the count.** After each close, the guard reads the evidence block's skips and stops the queue if either:
  - any skip's reason is W1-38's "rulesync is not installed" while `rulesync --version` answers on the machine (the I4 F2 case, wherever the close ran it, scoped or full);
  - any skip's (test, reason) pair is not on a known-skip list I take from the last green full run (today's 31, plus the one deliberate W2-66 skip). The list is a scratch file in my tools, shown in the digest.

  **What it could let through:** a test that newly starts skipping for a reason and test already on the known list. The guarded case itself cannot pass silently.
  **Cost:** about 30 lines in my scratch tools, no product change; validated on W2-66's and W2-70's full-run JUnit before use.
- **(b) Keep the count, set it to 32, and run every close full until W2-57.** It lets through nothing new, but it throws away W2-66's scoped closes (about 50 minutes a close, against about 11.5).
- **(c) Drop the guard at the re-pin.** It lets W1-38's silent skip through again until W2-57 (I4 F2: fails open). Not recommended.

## 5. Recommendation

**(a).** It guards the very case DEC-899 item 7 names, in scoped and full closes alike. It also catches any new skip reason, which a count would miss if one skip appeared as another went. The count's job ends with W2-57, as before.

## 6. What I need from you

Yes or no to (a), or choose (b) or (c). This needs an answer before the first close after the re-pin, not before the re-pin itself.
