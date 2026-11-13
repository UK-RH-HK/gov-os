# Cross-check of the hidden half's 16 new questions, h25 to h40 (DEC-1069 (8))

- **Status:** recommendations for the owner. Nothing in the set is changed here. Any correction is made by the
  checker the owner names (RUBRIC.md section 3, item 5).
- **By:** an independent auditor in W2-61h's role (`.tickets/DAEO-h2k3.md`), 2026-11-04. Read-only, under the
  hidden-half rule. This record quotes no hidden question, gold answer, gold source path, line or heading. Questions
  are named by id only.
- **Audited:** the sets root's hidden `h25.yaml` to `h40.yaml`, written by the owner's operator from the rubric.
- **Judged at:** `w2/integrate` `13947ceaf85e`, the main tree, read-only. Every gold source's `commit` names this
  head. The head then moved to `cd8e5420c125`, which changes only three files under `tests/acceptance/W2-61h/`.
  None of them is a gold source, so every judgement holds at `cd8e5420c125` too.
- **Method:** each source was resolved with the measure's own `_span` (imported from `src/gov/retrieval/measure.py`
  at the head) and read in full. Each path was placed with the path map's own matcher (`src/gov/check/pathmap.py`)
  against `governance/project/path-map.yaml` at the head.
- **Rubric:** `docs/research/memory-measure-audit/RUBRIC.md`, version 2 (R1 to R11).
- **R9 against:** the hidden `h01` to `h24`, the visible `q01` to `q40` at the head, and the 16 against each other.
  h01 to h24 were not judged again.
- **Blind to results:** I read no measure record, search result or run folder, nothing under EXP-003, no D4B
  package, no draft and no review. I ran no retrieval, context, measure or model.

## 1. Verdict

| Verdict | Ids |
|---|---|
| May enter as written | h25, h27, h30, h31, h32, h33, h34, h35, h36, h37, h38, h39, h40 (13). Some carry advisory notes |
| Enter after a minor fix | h26 (re-word), h28 (re-label the gold answer), h29 (re-word) (3) |
| Drop | none |

- No FAIL is major. In each of the three fixes the gold sources stay as they are, so what is scored does not change.
- All 25 alternatives across the 16 resolve at the head.
- Every heading is found, and it is the only line in its file equal to itself.
- Every span holds the part of the answer its entry stands for.
- Every path lies in an embedded namespace.
- No source is any of these:
  - test-harness code or a report;
  - an evaluation document;
  - a PROPOSED or superseded record;
  - a generated Contract record whose own status is not ACCEPTED.

## 2. Per question

All items PASS unless listed. "Advisory" means a note only, not a FAIL.

| Id | Failed items | Reason, in general terms | Recommendation |
|---|---|---|---|
| h25 | none | Advisory: a later owner decision clarifies one step's meaning. It adds no step, so the answer holds | Keep |
| h26 | R3-AMBIGUOUS (minor) | The second part, in the past tense, also reads as a history question (what was actually done with that audit's findings). A later decision answers that reading from a different source | Re-word the second part into the rule's tense; the sources stay |
| h27 | none | Advisory: a count in the gold answer is the governing source's own figure, written when that source was. The record it counts has grown since. The asked rule is unchanged | Keep. Optionally re-label the answer so the figure is attributed to the source or left out |
| h28 | R1-INCOMPLETE (minor) | A later standing decision adds a case to a subsidiary clause of the gold answer. That clause goes beyond what is asked. The main rule asked about is correct and in force | Re-label the gold answer: drop the subsidiary clause, or add the later case |
| h29 | R3-AMBIGUOUS (minor) | The question asks how a tool that has been built behaves. Read that way, its governing source is the tool's code (R1, a code fact), which is not an alternative. The gold source states the requirement, and the code agrees with it in substance | Re-word to ask what the ticket requires, as the visible half's comparable question does. Adding the code as an alternative is not advised: its summary span holds only part of the answer (R7.1) |
| h30 | none | Advisory: a code implementation exists. "Must" points to the requirement, so the reading is single | Keep |
| h31 | none | | Keep |
| h32 | none | Advisory (R6): the span crosses the record's other front-matter fields. Both asked fields lie at its two ends, so that is unavoidable. One detail of the gold answer lies just outside the span and is not asked | Keep |
| h33 | none | Advisory: a higher record states the principle more generally. The alternatives are the testable statement of what is asked, and a span of the higher record alone would be a partial alternative. The question shares some wording with the source, but it is common vocabulary in this repository (R4 passes) | Keep |
| h34 | none | Advisory: some echo of the source's wording, in ordinary terms (R4 passes) | Keep |
| h35 | none | A question with a negative answer, settled by records that state it. It is scorable as asked (R3.5 does not apply) | Keep |
| h36 | none | Advisory: the code agrees with the governing source | Keep |
| h37 | none | Advisory: the higher record that the source restates, an ACCEPTED one, is not an alternative. That is allowed: the source is a faithful restatement of it, and R5's tag wants this kind of source cited. Lines-only anchor (R6.4) | Keep. Optionally anchor on a unique line |
| h38 | none | Advisory (R9): the same governing record is a visible question's source, for a different fact. That is no duplicate, but the visible question's span covers this one's, so a hit there is also a hit here. Lines-only anchor | Keep. The owner may weigh the overlap between the halves |
| h39 | none | Advisory: lines-only anchor | Keep. Optionally anchor on a unique line |
| h40 | none | Advisory: the second alternative is a faithful restatement, in the project overlay, of the decision's line. The decision has no later change | Keep |

## 3. Counts per item (the 16)

| Item | PASS | FAIL | Major | Minor | Advisory notes |
|---|---|---|---|---|---|
| R1 Correct, governing | 15 | 1 | 0 | 1 (h28) | h25, h27, h33, h37, h40 |
| R2 Searchable | 16 | 0 | 0 | 0 | none |
| R3 Unambiguous | 14 | 2 | 0 | 2 (h26, h29) | h30 |
| R4 Real agent question | 16 | 0 | 0 | 0 | h33, h34 (wording echo, common terms) |
| R5 Spread | set level, section 4 | | | | |
| R6 Span holds answer | 16 | 0 | 0 | 0 | lines-only anchors 3 (h37, h38, h39); h32 |
| R7 Well formed | 16 | 0 | 0 | 0 | all within the stack budget (the largest stacked need is under 300 tokens) |
| R8 Not from evaluation | 16 | 0 | 0 | 0 | none |
| R9 Distinct | 16 | 0 | 0 | 0 | h38 |
| R10 Record and form | 16 | 0 | 0 | 0 | none. New questions, so no label-change record is due |
| R11 Stable | 16 | 0 | 0 | 0 | h27 (the figure in the answer; the asked rule is stable) |

- 13 of the 16 pass every item. None has a major FAIL.
- Recommendations: re-word 2, re-label 1, re-anchor 0 (3 optional), mark as a keyword question 0, retire 0, keep 13.

**R2, keyword-only:**

- **The 16:** any entry keyword-only **0**; all entries keyword-only **0**. Entries in neither index 0; paths in no
  namespace 0.
- **The hidden 40:** any **0**; all **0**. One alternative in the 24 is keyword-only, but its entry also has an
  embedded alternative.

## 4. R5 for the hidden 40

**Governing domains** (the main entry's governing source). Threshold: at least 4 each.

| Governing domain | h01-h24 | h25-h40 | Hidden 40 |
|---|---|---|---|
| Decisions | 9 | 1 | 10 |
| Code | 9 | 0 | 9 |
| Contract and Charter | 2 | 4 | 6 |
| Tickets | 0 | 4 | 4 |
| The plan | 0 | 4 | 4 |
| None of the five | 4 | 3 | 7 |

Every domain reaches 4 of 40: **PASS**. The 24's counts are the earlier audit's
(`docs/research/memory-measure-audit/HIDDEN.md`), checked against the 24's sources at the head.

**Subsystems:** the largest holds at most 8 of 40 (20 %) even in the worst case. By my count it holds 6, and the
16 add at most 2 to any one subsystem. The limit is 10: **PASS**.

**Tags and limits:**

| Limit | Count | Result |
|---|---|---|
| Kernel template | 3, of which 2 on roles or skills (at least 2) | PASS |
| Failure or lesson memory citing a lesson or failure record | 3, all among the 16 (at least 3) | PASS |
| Supersession with a superseded naive answer | at least 2 (at least 2 required). The earlier audit counted at least 4 among the 24; the 16 add none | PASS |

**Category table** (the `category` values, which sum to 40):

| Category | Count | At least | Result |
|---|---|---|---|
| decision | 5 | 6 | short 1 |
| contract | 4 | 4 | met |
| plan | 4 | 4 | met |
| ticket | 4 | 4 | met |
| exact-string | 4 | 4 | met |
| callers | 3 | 4 | short 1 |
| code-paraphrase | 2 | 3 | short 1 |
| kernel-template | 3 | 3 | met |
| multi-file | 3 | 3 | met |
| failure-memory | 5 | 3 | met |
| history | 2 | 1 | met |
| nonexistent-id | 1 | 1 | met |

**R5-QUOTA** on `decision`, `callers` and `code-paraphrase`, one short each. This is the shortfall the operator
noted and the brief says the owner accepted. I found no register entry that records that acceptance; recording it
under DEC-1069 is recommended. Items 2 to 5 (domains, subsystems, tags and supersession) all pass.

## 5. Not judged here

- h01 to h24 (audited before). h02, h03, h08 and h24 were corrected by the operator. They were read only for R9 and
  for R5's counts.
