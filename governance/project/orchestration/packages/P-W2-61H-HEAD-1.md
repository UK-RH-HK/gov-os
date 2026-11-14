# P-W2-61H-HEAD-1 — W2-61h's hidden-form check: the structural fix, and the quickest clean close of W2-134

Short form plus context (a P1: it changes how an owner-set check judges, DEC-1069 (6)'s re-anchor practice; it blocks
W2-134's close only because the CTO tied that close to it). 2026-11-14, CTO session 6ff2ee7c.

## Context
- **The check:** `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py::test_s4_f3_every_hidden_gold_source_resolves_at_head`
  (W2-61h's F3 line), run only in your operator's walled run. Its helper `source_faults()`
  (`tests/acceptance/W2-61h/w2_61h_support.py:204-246`) compares every line-cited block at **HEAD** with the same lines
  at the question's own commit. Any edit to a cited file in ordinary work turns it red.
- **Its premise is spent:** the helper's own comment (line 239) says "the measure ... re-anchors nothing itself, so a
  block that moved is red too". W2-134 (merged, `measure.py`) now re-anchors in memory for the commit it measures
  (S1), never writes the sets root (S2), and names an unresolved source by id and entry and counts it not found (S3:
  fails closed, a lower score, never a false hit).
- **Three reds so far, none caused by code under test:** 11-13 (h22 e1/e2, h23 e1 moved), 11-14 12:05 (h03: cited
  lines changed, a real edit; h11, h16, h23, h37, h38, h39 moved unchanged).
- **The same comparison runs on the visible half:** `test_s4_f3_every_new_visible_gold_source_resolves_at_head` uses
  the same helper, and the nightly and every close run it. The next edit to a cited file reds the nightly in the same way.
- **W2-134:** merged; review READY; fresh `gov accept W2-134` **28 passed, 0 failed** at c451c2180 (just now,
  `log/accept-20261114-w2134/`). The six of seven walled cases that judge the measure and the set's form passed
  (S1 count, form, quotas, S5-F1 held only in the sets root, S6 measured role refused, F2 no repeats).

## Q1. The structural fix
**Question:** how should W2-61h's F3 check judge, so that re-anchoring is routine and a changed gold never blocks a close?

| Option | What | Cost | Risk |
|---|---|---|---|
| **(A)** | **Reopen W2-61h (closed, role independent-test-designer) under DEC-1164 (18) for a test revision of F3, hidden and visible cases alike:** (1) each source is judged **at its own commit** (path a file there, heading or lines a span there); (2) at HEAD, a block that moved unchanged is **no fault** (W2-134 re-anchors it in memory); (3) a block whose lines changed is **listed, not failed**: one line per question id and entry number (never text, path or lines), the walled run's maintenance list. F3's KPI line reworded to match (a KPI edit within the ticket's purpose). **The weekly cycle:** MEMORY-AUDIT-P1's G5 `maintain` pass (W2-187) gains a sixth item: the walled run's maintenance list goes to the walled writer in that week's cycle; until W2-187 lands, your operator runs it with the Monday standing slot (O6). | Test designer ~1.5 lead-hours + narrow independent check ~0.5 h (DEC-1154); then one walled re-run by your operator (expect 7 passed, h03 listed). W2-187's G5 grows by one item (~20 lines). | Low. Fails closed: a changed gold scores "not found" until rewritten. |
| (B) | As (A) but no maintenance list: judge at own commit only. | ~1 h + check | A drifted gold is invisible until the monthly drift check; the score drops silently. |
| (C) | Keep the check; your operator re-anchors (`repin_gold.py --write`) and the writer fixes changed golds before each close that waits on it. | One operator sitting per red | Third red in two days. Blocks closes, and the visible twin will red the nightly. |

**Recommendation: (A), confidence high (~85 %).** It is DEC-1084's own design (the measure re-anchors) brought into the
check that predates it. No new ticket (W2-61h reopens; W2-187 is in your pending MEMORY-AUDIT-P1). Classification of
the finding: ordinary work yes (any edit to a cited file); consequence other (a false red that blocks a close; never
fails open).

## Q2. The quickest clean way to close W2-134
| Option | What | Cost |
|---|---|---|
| **(i)** | **Close W2-134 now** by DEC-953's practice on the fresh accept (28/0 at c451c2180) and the walled run's six passing cases. The one red (h03's label against HEAD) is label maintenance, not W2-134's code, and W2-134's S3 already handles it (fails closed). The close record says so and names the red as Q1's item. | 5 minutes |
| (ii) | Wait for Q1 (A) and the walled re-run (7 passed). | ~3 h + an operator sitting |
| (iii) | Your operator's walled writer rewrites h03 now, then re-runs. | ~1 h of operator time; the next ordinary edit can re-break it |

**Recommendation: (i), confidence high (~90 %).** Nothing of the hidden set is read by me (hidden-form runs stay your operator's, `env -u GOV_ROLE -u GOV_TICKET`).

## What it blocks
W2-134's close (one merged-not-closed ticket). The visible twin is a latent nightly red. Nothing on EXAMIN's path waits.

## Your line
`P-W2-61H-HEAD-1: Q1 (A), Q2 (i)` (or other letters).
