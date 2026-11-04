# The visible half's 16 new questions, q25 to q40 (DEC-1069 (4), (8))

- **Written by:** a session independent of the retrieval work, blind to every result: no search, measure record,
  figure, rank, research folder, D4B package, draft or review was read. Written at `w2/integrate` `cc9c94d42a54`
  (worktree `emg-new-visible`), in q21 to q24's form, each with `commit: cc9c94d42a54` and every source anchored on
  its own line at that head (a heading taken from the file, checked to be the first line equal to itself).
- **Judged by:** `RUBRIC.md` version 2 (R1 to R11).
- **Checked:** `repin_gold.py` on the 40 prints `unresolved: 0` (105 line-cited, 101 heading-anchored, 0 re-pinned).
  Every span was also resolved with the measure's own rule and read, and every path placed with the path map at
  the head: all in embedded namespaces (`docs`, `tickets`, `gov-source`, `kernel-template`).
- **Not touched:** `tests/` (W2-61's visible-half cases follow, by a test designer).

## 1. The 16

| Id | Question, in short | Governing domain | `category` | Subsystem | Entries (alternatives) |
|---|---|---|---|---|---|
| q25 | New work: a list row, or to the owner first? | plan (WBS §6) | `plan` | plan process | 1 |
| q26 | The exit criterion on the hooks | plan (WBS §5, criterion 2) | `plan` | hooks and CI | 1 |
| q27 | Is W2-41's close-integrity work in Wave 2, and why not? | plan (W2-41's card; revised plan §8) | `plan` | the close | 2 |
| q28 | The triage's "named in" against "fits" a ticket | plan (`WAVE_2_TRIAGE.md`) | `plan` | plan process | 1 |
| q29 | W2-77: the nightly's fallback when its clone will not go | tickets (DAEO-b6hm) | `ticket` | the close's nightly | 1 (2) |
| q30 | Which ticket remembers gitleaks verdicts, and where | tickets (DAEO-kiar) | `ticket` | rebuild and secrets | 2 (2, 2) |
| q31 | What an owner question holds; how many at once | Contract and Charter (MR-6) | `contract` | owner decisions | 2 (1, 3) |
| q32 | Why the Phase 1 write guard let new paths through | lessons (L-0074) | `failure-memory` | the guard | 1 |
| q33 | What a wait loop must have | lessons (L-0075) | `failure-memory` | scripts and tools | 1 |
| q34 | What the anti-snowball rule required before code changed | lessons (L-0077) | `failure-memory` | reviews | 1 |
| q35 | Does an independent auditor fix what it finds? | kernel role (`independent-auditor.md`) | `kernel-template` | reviews and audit | 1 |
| q36 | How a probe finding reaches the test designer | decisions (DEC-136; the test-design skill) | `kernel-template` | test design | 1 (2) |
| q37 | A contradicted closed specification: what goes to the owner | Contract (CAP-33.e; DEC-105, the change skill) | `contract` | owner decisions | 1 (4) |
| q38 | Where the Task, Implements and Role trailers go | decisions (DEC-182) | `decision` | commits | 1 |
| q39 | Routing a serial-only entry to the nightly | code (`src/gov/close/serial.py`) | `code-paraphrase` | the close | 1 |
| q40 | Can a release version be built again? | code (`src/gov/release/__init__.py`; W2-16's KPI) | `code-paraphrase` | releases | 1 (2) |

## 2. The rubric check, per question

Each of the 16 passes R1 to R11. The judgement behind each item:

- **R1:** each gold source is ACCEPTED or the current text (the Charter, the Contract, the plan, closed tickets,
  ACTIVE lessons, a role file, a skill, the code). None is PROPOSED: DEC-041, L-0074's decision, is PROPOSED and is
  left out; MR-6's generated record is PROPOSED and is left out. No source is test-harness code. The gold answers
  carry no line numbers.
  - q27 states both the plan's current reason (DEC-953 and DEC-954: `gov close` is not a gate here) and the revised
    plan's earlier one.
  - q38 states DEC-182's form. That trailers are no longer refused here (DEC-953) does not change where they go.
  - q29 and q39 hold at the head's code (`_remove_clone`; the serial phase's routes).
- **R2:** every alternative is in an embedded namespace. Any entry keyword-only: 0; all entries keyword-only: 0.
- **R3:** each asks at most three facts, presupposes nothing false, and has one reading.
- **R4:** each is asked in work by a named role.
  - Lead: q25, q26, q31, q37.
  - Auditor: q27, q35.
  - Test designer: q28, q29, q36.
  - Engineer: q30, q32, q33, q39, q40.
  - Any worker: q38.
  - Lead after a review: q34.
- **R6:** every span holds its answer and stops at it. `#` headings span their section; other headings span the
  stated lines.
- **R7:** each alternative holds its entry's whole piece. q27, q30 and q31 have two entries because their answers
  need two pieces in two places. Each fits the stack budget.
- **R8:** no source is an evaluation document.
- **R9:** each fact is asked once, among the 16 and against the 24. The nearest pairs are distinct facts:
  - q32 (the guard's lesson) and Q19 (MR-3);
  - q35 (the auditor repairs nothing) and Q15 (the two lines a finding carries);
  - q36 (probe findings) and Q19.
- **R10:** form as q21 to q24 (no `id` field; the file name gives it). The category fits the governing domain or
  the tag.
- **R11:** no count, list or state that ordinary work moves.
  - q29 and q30 are closed tickets.
  - q25 to q28 are plan rules and records that change only by a decision.
  - q30's cache path and q40's rule are settled code.

## 3. R5 for the visible half's 40

The existing 24 are counted as `VISIBLE.md` placed them, Q04 under the Contract (DEC-1069 (1)).

| Governing domain | Existing 24 | New 16 | Of 40 | Share | At least 10 % (4) |
|---|---|---|---|---|---|
| Decisions | 8 (Q01, Q02, Q03, Q05, Q15, Q16, Q18, Q21) | 2 (q36, q38) | 10 | 25 % | yes |
| Code | 8 (Q10, Q11, Q12, Q13, Q17, Q22, Q23, Q24) | 2 (q39, q40) | 10 | 25 % | yes |
| Tickets | 4 (Q06, Q07, Q08, Q14) | 2 (q29, q30) | 6 | 15 % | yes (4 without Q07 and Q14) |
| The Contract and the Charter | 4 (Q04, Q09, Q19, Q20) | 2 (q31, q37) | 6 | 15 % | yes |
| The plan | 0 | 4 (q25, q26, q27, q28) | 4 | 10 % | yes |
| Lessons (no domain of the five) | 0 | 3 (q32, q33, q34) | 3 | 7.5 % | n/a |
| A kernel role (no domain of the five) | 0 | 1 (q35) | 1 | 2.5 % | n/a |
| **Total** | 24 | 16 | **40** | | |

| Tag or limit | Count of 40 | Required | Met |
|---|---|---|---|
| Failure or lesson memory, citing a lesson | 3 (q32, q33, q34) | at least 3 | yes |
| The kernel's skills or roles | q35 (role), q36 (test-design skill), q37 (change skill, an alternative); Q19 (role files, alternatives) | at least 2 | yes |
| Supersession, naive answer superseded | 4 (Q03, Q05, Q16, Q21) | at least 2 | yes |
| Retrieval and the context packet as the subject | 10 (Q01, Q02, Q03, Q04, Q09, Q10, Q11, Q12, Q13, Q17); none of the 16 | at most 10 (25 %) | yes, at the limit |
| Any other subsystem | the close and the nightly 4 (Q23, q27, q29, q39); the guard 3 (Q19, Q22, q32); rebuild and secrets 2 (Q24, q30); checkpoints and resume 2 (Q18, Q20); owner decisions 2 (q31, q37) | at most 10 | yes |

**The category quotas** (`RUBRIC.md` R5 item 6) are counted here as information: on the visible half, items 2 to 5
decide. Each lens B question is placed under the category its asked fact fits.

| Category | Count of 40 | Quota |
|---|---|---|
| `decision` | 8 (Q01, Q02, Q03, Q05, Q15, Q16, Q21, q38) | 6 |
| `contract` | 5 (Q04, Q09, Q19, q31, q37) | 4 |
| `plan` | 4 (q25 to q28) | 4 |
| `ticket` | 6 (Q06, Q07, Q08, Q14, q29, q30) | 4 |
| `exact-string` | 2 (Q12, Q23) | 4: short 2 |
| `callers` | 3 (Q10, Q11, Q22) | 4: short 1 |
| `code-paraphrase` | 5 (Q13, Q17, Q24, q39, q40) | 3 |
| `kernel-template` | 2 (q35, q36) | 3: short 1 |
| `multi-file` | 2 (Q18, Q20) | 3: short 1 (q27, q30 and q31 need two files each, but are put under their domain) |
| `failure-memory` | 3 (q32 to q34) | 3 |
| `history` | 0 | 1: short 1 |
| `nonexistent-id` | 0 | 1: short 1 |

The brief set the domain, tag and subsystem targets, and these 16 were chosen to meet them. With lens B's 20 fixed,
reaching the code categories (exact strings, callers) as well would have taken code questions away from the plan
and the lessons. If the owner wants the category quotas met on the visible half as well, the next visible additions
should be 2 exact-string questions, 1 callers, 1 history and 1 id that exists nowhere (scored apart, R3 item 5).

## 4. Notes for the owner

- **Q07 and Q14 fail R11 as labelled:** a ticket's dependency list and its dependents grow with ordinary work.
  They pass only once marked as computed (R11 item 3) or re-worded to a fact that is settled. The tickets domain
  meets 10 % without them (q29, q30, Q06, Q08).
- **Retrieval and the context packet are at the 25 % limit.** Any new visible question on them needs one of the 10
  retired or re-worded first.
