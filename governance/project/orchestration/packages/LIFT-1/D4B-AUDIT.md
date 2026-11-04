# D4B-AUDIT: the audit of the 48 measure questions (DEC-1068), for the owner

By the CTO (session 33b3628c), 2026-11-04 ~10:15. **Nothing has changed: you decide.** A label changes only where it is
wrong, never to fit a result.

The work was done by two sessions, both blind to every result:
- an independent session wrote the rubric and judged the visible half;
- W2-61h's role (an independent auditor) judged the hidden half, read-only.

The files:
- the rubric: `docs/research/memory-measure-audit/RUBRIC.md`, items R1-R10, with pass tests and reason codes;
- the visible half: `docs/research/memory-measure-audit/VISIBLE.md`;
- the hidden half: `docs/audit/memory-measure-hidden.md`, in ids, items and general reasons only. h02 and h24 are
  held back while your operator corrects them, as DEC-1068 (c) ruled.

## The answers to your three questions
**1. Per question, the items failed and why:** see the two reports. In short:

| | visible (24) | hidden (22 judged) |
|---|---:|---:|
| pass every item | 12 | 11 |
| a major fault (it changes what is scored) | 6 | 2 |
| minor faults only | 6 | 9 |
| R1, correct today | 8 (3 major) | 5 (2 major) |
| R3, unambiguous | 1 | 0 |
| R4, what agents ask | 0 | 3 (minor) |
| R6, the sources hold the answer at the head | 4 | 0 (16 advisory: lines-only anchors) |
| R7, entries and alternatives | 2 | 1 (major) |
| R9, distinct | 1 (Q04 asks Q09's fact) | 0 |
| R10, the label's record and form | 2 | 5 (minor: re-anchors without a written reason) |

**2. How many depend on keyword-only locations (tests, close, checkpoints, probes, reviews): none.** No question on
either half has any gold source in a keyword-only namespace. The hidden half's plateau at 17 since G1 is therefore
not explained by M-4.

**3. The recommended changes (the visible half's, by its checker; recommendations only):**
1. Q14 re-label: 13 dependents of W2-03 today, not 9; "in depends_on" stated (high).
2. Q07 re-label and re-anchor: the gate run depends on 23 tickets today, not 27, by DEC-954's change (high).
3. Q04 re-label:
   - drop DEC-004 (only PROPOSED), `CAP-15.g.md` (does not state the ceiling) and `BUNDLE_BUDGET` (a different
     budget);
   - add CAP-15 from `contract.yaml`;
   - category `contract`.
   Confidence high. Its duplicate of Q09 is a separate choice: (a) keep both after the re-label (recommended),
   (b) re-word it, or (c) retire it, which breaks DEC-1009's "lens B's 20".
4. Q13 and Q17 re-anchor: their spans stop short of the lines that state the answer (high).
5. Q03's structure: two entries (where; then the device and why), since no single alternative holds all three facts
   asked (medium). This also confirms or reverts Q03's second re-label (`a9ef6f82`), which I ordered under DEC-1067
   (c)'s form while (c) named Q16 and Q19 only.
6. Minor gold-answer re-words, with no effect on scores: Q02, Q10, Q11, Q12, Q23.
7. The set's spread (R5) fails on both halves:
   - the visible half has no question on the plan or on failure and lesson memory, and 10 of 24 are about retrieval
     itself;
   - the hidden half has decisions 9, code 9, the Contract 2, tickets 0, the plan 0.
   Recommended: new questions governed by the plan, the tickets, the kernel skills and failure memory.
   Separately, decide R5's threshold: the checker proposes each domain at least 10 % of each half, and no one
   subsystem above 25 %. The hidden half's auditor notes that W2-61h's quotas cannot meet it.

**The hidden half's two major faults** (h-ids in the report; general reasons only) are one R1 and one R7. The CTO
does not know which questions or why beyond that. They go to your operator, as h02 and h24 did, if you want them
corrected.

**On the hidden half's R10 note:** five hidden files were re-anchored after the set was fixed. That is the CTO's
measure script (`repin_gold.py --write`, run before each measure). It re-pins moved line anchors to the same block and
adds a per-source `commit:`, keeping a mode-700 backup each time (`backup-hidden-<ts>`). The reason belongs in a
README line in the sets root, which the script did not write: a row, fixed by writing the line from now on.

## For you
- (a) Which of changes 1-6 to apply. For the visible half, an independent session applies them, as for Q16 and Q19.
- (b) Q04's duplicate: (a), (b) or (c).
- (c) Q03: confirm or revert.
- (d) R5: new questions (how many, which domains, who writes them), and the threshold.
- (e) The hidden half's two major faults: to your operator, or left.
- (f) The hidden auditor's P2: whether test-harness code counts as governing for a code fact (R1.3).

Every run from today keeps its per-question ranks (DEC-1068 (4)). Approved label changes can be re-scored on those runs
without running again; last night's runs predate this.
