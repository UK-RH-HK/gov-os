# AUDIT-NIGHT-1 (c): open and in-progress tickets against this week's decisions

Night of 2026-11-10/11, before the re-pin. Helper: product-spec, Sonnet high, class C1 (DEC-1125 (3) (iii) c).
Read-only checks first, then reading, then small fixes. Head at the audit: `797495bdf`. Scripts and raw output:
`/tmp/gov-os-emg-audittk/`.

## 1. Counts

| | n |
|---|---|
| Open | 40 |
| In progress | 49 |
| Closed (read for waits only, never edited) | 130 |
| Audited (open + in progress, tracked) | 89 |
| New files, untracked, another helper's (W2-156 and up): not audited | 8 |
| Flagged for something real (the four fixed, plus 13 for the CTO; the three false alarms of section 2 left out) | 17 |
| Fixed now | 4 tickets (6 edits) |
| Left for the CTO or an engineer | 13 tickets, plus the new files' YAML fault, listed in section 4 |

## 2. Deterministic checks (what was run, what it said)

| Check | Result |
|---|---|
| Schema (`python3 -m gov.check.schema`, check-jsonschema 0.38.2) | green: 980 records, no finding |
| `class` present and in the template's list | 89 of 89 |
| `role` equals `assignee`, and fits the class | 89 of 89 (two test-designer tickets carry `class: audit`: DAEO-h2k3, DAEO-6y0x; they write evaluation question sets, so it reads as intended) |
| Every `depends_on`/`deps`/`waits_on` id exists | yes, none dangling |
| A `waits_on` that points at a closed ticket | none |
| `tk dep cycle` | no cycle |
| `wbs_id` unique over all 219 tickets | yes |
| `deps` equals `depends_on` | 87 of 89; two differed (fixed, section 3) |
| `sources` ids resolve in the register | yes. Three false alarms from the script's own bracket match: DAEO-qzrq and DAEO-r30l cite "ACT-OLLAMA-CAP-1/2" (not CAP-1/2); DAEO-swdu keeps DEC-798 in a KPI bracket on purpose (DEC-1123 (2) re-pointed its source to DEC-1033) |
| Context check (`gov.context.context_check`) in the main tree | unmeasured: its store is built from `f6222134c826`, not HEAD. Run against the integration store (same HEAD): 88 refusals over the 6,000-token ceiling (count green) and **1 error**: DAEO-ar89's source `W1-19` (fixed, section 3) |
| `gov links --all` (a notice, never a gate) | 1,575 standing; 183 `UNLINKED_ID` on open tickets are WBS and backlog ids that DEC-1123 (2) took out of `sources` on purpose, so the notice and the context check disagree there; see 4.9 |
| `gov plan` | exit 1 only because of `NEEDS_UNDECLARED`; no cycle, no held ticket, no unknown wait, no override |

## 3. Fixes made (open and in-progress tickets only, the offending lines only)

| Ticket | Field | Old | New | Why |
|---|---|---|---|---|
| DAEO-ar89 (W2-155) | `sources` | `- W1-19` | `- DAEO-t6hf` | The store holds no record named `W1-19`; it holds its ticket `DAEO-t6hf` (closed). The context check errored on it. Same route as commit `66303c373` (DEC-1123 (2): WBS id to the ticket's id). The KPI bracket still says W1-19, so `gov links` may name it as a notice; that notice stands for 183 other ids already. |
| DAEO-ar89 (W2-155) | `reads`, `waits_on` | missing | `reads: [src/gov/retrieve/**, src/gov/retrieval/**]`, `waits_on: []` | Created 11-11, after `ready.new_since` (2026-11-10): the ready check would refuse it by name (READS_MISSING, WAITS_ON_MISSING; DEC-1088 (3)). I left the acceptance folders out of `reads` on purpose (DEC-1093 (2)). |
| DAEO-l4gf (W2-154) | `reads`, `waits_on` | missing | `reads: [src/gov/close/**, governance/project/orchestration/nightly/**, tests/acceptance/serial-only.txt, tests/optin-lifted*.txt, tests/unit/close/**]`, `waits_on: []` | Created 11-10, same reason. Reads taken from its KPI lines S1 to S4. |
| DAEO-ongl (W2-139) | `deps` | `[DAEO-5ce2]` | `[]` | `deps` (what `tk` reads) said W2-140 first; `depends_on` (what `gov plan` reads) said none. W2-139 and W2-140 merge and close in one batch and W2-140's `judged_by` is W2-139's candidate, so a hard wait either way would be a deadlock. The two fields now agree on the plan's reading. If the CTO wants `tk ready` to hold W2-139, the way is a note in the ticket, not a wait. |
| DAEO-t8mp (W2-128) | `deps` | `[]` | `[DAEO-o5x1, DAEO-8s85]` | Mirrors its `depends_on`, which the plan already used. No change to the batches. |

The `gov plan` batches are the same before and after (section 5). Under DEC-1088 (6) each change to an open ticket is
marked with its decision: the commit that lands these five edits should carry `Implements: DEC-1125, DEC-1088,
DEC-1123` (DEC-1123 (2) for the source line) or `gov links` will flag TICKET_CHANGE_UNMARKED.

## 4. What needs the CTO or an engineer (none fixed: each changes a KPI, a scope or a control)

1. **Four of the new tickets do not parse (P1 for the plan).** DAEO-6lid, DAEO-8a3f, DAEO-ozyt, DAEO-ylsh (the
   W2-157 and up test-design tickets, written 01:21 to 01:23): the `acceptance_tests.author:` line holds `: ` inside an
   unquoted value ("... from these KPI lines: planted ..."). YAML refuses it. `gov plan` stops with `PLAN_CANNOT_RUN` the
   moment they are in the tree. Fix: put the value in quotes. They were still being written when I looked; the other
   helper may have fixed them already. Also DAEO-61vm, DAEO-k1e2, DAEO-p8tv, DAEO-fd0p are stubs with no class, role,
   paths or waits yet. **Before the re-pin, re-run `gov plan` once with all tickets in the tree.**
2. **RUBRIC-2 is not in W2-33 (DAEO-lrre) or W2-60a (DAEO-cv58).** DEC-1120 (5) and DEC-1119 (2) send the rubric into
   the product through these two. Neither ticket cites DEC-1118, DEC-1119 or DEC-1120. W2-60a already applies a role's
   default model and effort and records the ticket's class; it has no line for the class-by-role table (DEC-1120 (2)),
   promotion after two failed reviews or a fail-open finding (3), the trial exception, or the spend log's tier, class
   and promotion. Recommendation: one product-spec session adds the KPI lines and sources to both before the lift (they
   must land before EXAMIN's copy). I did not change KPIs.
3. **W2-115 (DAEO-emq1) has no line for the trailers switch.** DEC-1123 (3), DECIDED-NOT-DONE row 114 and P1-PLAN Q-8
   say W2-115 lands the switch from warning to block; the ticket never mentions trailers, `traceability.py` or the
   `trailers_base` deletion. Recommendation: add the Q-8 line (a KPI), or name another owning ticket.
4. **W2-88 (DAEO-2bdu) has no line for the weekly memory audit.** DEC-1125 (2) names it a home ticket. S12 to S16 hold
   the one-off tuning and verdict sets; nothing says "scheduled, weekly while development is active". It does not cite
   DEC-1101 or DEC-1125. The memory-audit helper's package should settle the wording.
5. **Nine open tickets write `.claude/**`**, which a launched session cannot edit (deny rules, DEC-315) and which is
   generated from `template/` by ACT-CLAUDE-COPIES (DEC-1115 (2), DEC-1116 (2)): DAEO-2bdu, DAEO-6icv, DAEO-k7hz,
   DAEO-kmcr, DAEO-lrre, DAEO-siiz, DAEO-uw5h, DAEO-wi46, DAEO-xwro. They also create phantom waits in the plan (for
   example DAEO-wi46 and DAEO-siiz wait for DAEO-k7hz over `.claude/skills/...`). Recommendation: drop the `.claude/`
   lines from `allowed_paths` and let the copies follow by ACT; the real files are under `template/`. Needs the CTO
   because it changes allowed paths.
6. **W2-154 (DAEO-l4gf) rides a second edit outside its paths.** Its body asks for the `brief` citation in
   `src/gov/check/commands.py:15` and three test docstrings, but `allowed_paths` has none of them (and five other open
   tickets hold `commands.py`). The guard would refuse it. Recommendation: file a tiny ticket after the lift, or add the
   paths with a decision.
7. **`needs:` is undeclared on 73 of 89 tickets and `reads:` on 89 of 89** (plan finding `NEEDS_UNDECLARED`, which is
   why `gov plan` exits 1). `waits_on:` is missing on 74. A plan then orders each of these tickets by its own writes
   alone. I did not write `needs: []` over them: it would claim "none" for work I did not read. Only tickets created
   from 2026-11-10 are refused by the ready check, and I fixed those two. Recommendation: accept the finding for tickets
   already in progress; ask each engineer to declare `needs:` when the ticket is next launched.
8. **A low-priority ticket orders two P1 tickets.** DAEO-ar89 (W2-155, P4, after the lift) writes `src/gov/retrieval/**`;
   DAEO-rmhj (W2-138) and DAEO-2tfd (W2-145) list `retrieve.py` and `rerank.py` in `needs:`, so the plan puts them after
   it (batches 13 and 14). The plan orders needs against every unfinished writer whatever its priority. Both are
   in progress, so it affects only a later launch. Recommendation: if W2-155 should not hold them, give each a
   `plan_override: <DEC-id>` or narrow W2-155's paths (DEC-1125 (1) has its owner note; the ticket's paths are wide for
   a profiling job).
9. **The context check and the links notice disagree about WBS ids in `sources`.** The check needs every source to be a
   store record; the notice asks for any bracketed WBS or backlog id to be listed. DEC-1123 (2) chose the check. A
   KPI that cites a WBS id in brackets will always show an `UNLINKED_ID` notice. Recommendation: let the notice read a
   WBS id as met when its ticket's id is in `sources` (a code change, after the lift).
10. **The main tree's store is stale** (`f6222134c826`, not HEAD). The context check cannot be measured there until it is
    rebuilt. I did not rebuild it (heavy, outside my brief). I did not re-run the context check after the ar89 edit; I
    checked in the integration store that `DAEO-t6hf` is a record (status closed), and closed records satisfy a source
    (`NO_LONGER_STANDS` holds only SUPERSEDED, RETIRED, REJECTED).

## 5. `gov plan` as it reads after the fixes

Run on a copy of the 219 tracked tickets (the eight new files left out so the plan could run), with my five edits.
89 tickets, 22 batches, 435 waits (290 by overlapping writes, the rest by `depends_on`, `needs` and `waits_on`). No
cycle, no held ticket. Run again with all tickets before the re-pin (item 1).

```
batch 1: DAEO-ouet, DAEO-zpdj, DAEO-blwa, DAEO-qzrq, DAEO-r8vq, DAEO-vhad, DAEO-sdxk, DAEO-u4oz, DAEO-k7hz, DAEO-zuiy, DAEO-l78m, DAEO-nqa2, DAEO-g87r, DAEO-ongl, DAEO-5ce2, DAEO-qzca, DAEO-6ox0, DAEO-btcs
batch 2: DAEO-jpr0, DAEO-k4wm, DAEO-6y0x, DAEO-wi46, DAEO-52ku
batch 3: DAEO-c4pb, DAEO-xafn
batch 4: DAEO-0z8c
batch 5: DAEO-zqvn, DAEO-r30l, DAEO-kmcr, DAEO-03ub, DAEO-3r1j, DAEO-o5x1, DAEO-6n5k, DAEO-i89t
batch 6: DAEO-siiz, DAEO-arrl, DAEO-wnnz, DAEO-h2k3, DAEO-fu3n, DAEO-drhj, DAEO-cb2b
batch 7: DAEO-rd0g, DAEO-cv58, DAEO-qvff, DAEO-g29a, DAEO-emq1, DAEO-neam
batch 8: DAEO-0pyc, DAEO-ecac, DAEO-l4gf, DAEO-057v
batch 9: DAEO-a3u2, DAEO-n0wb, DAEO-mb2t, DAEO-m4rq, DAEO-f6x3, DAEO-8s85
batch 10: DAEO-clon, DAEO-t8mp, DAEO-q7lk, DAEO-sdhj
batch 11: DAEO-q8cl, DAEO-p3ln, DAEO-5emz, DAEO-ijf5, DAEO-lrre, DAEO-uw5h, DAEO-6icv
batch 12: DAEO-f58b, DAEO-zi7s, DAEO-jzvg, DAEO-yadm, DAEO-fau3
batch 13: DAEO-xwro, DAEO-2keg, DAEO-w19l, DAEO-ar89
batch 14: DAEO-rmhj, DAEO-2tfd
batch 15: DAEO-qskx
batch 16: DAEO-2bdu
batch 17: DAEO-swdu, DAEO-h4rh
batch 18: DAEO-csj8, DAEO-4k3l
batch 19: DAEO-b926
batch 20: DAEO-60rw
batch 21: DAEO-nn1s
batch 22: DAEO-jip3
```

By WBS id, the same: batch 1 W2-96, W2-105, W2-122, W2-123, W2-131, W1-01b, W2-00, W2-04, W2-11, W2-66b, W2-81,
W2-90b, W2-94, W2-139, W2-140, W2-151, W2-40, W2-66c; batch 22 W2-47. Most of batch 1 is already in progress; the
ready list after the lift is what is still open once the formal closes land.

## 6. What I did not do

No KPI, scope, allowed path or status changed. No closed ticket edited. The new tickets (W2-156 and up) and
`DAEO-ar89` beyond its three wrong lines were left alone. No rebuild, no suite run, nothing committed.
