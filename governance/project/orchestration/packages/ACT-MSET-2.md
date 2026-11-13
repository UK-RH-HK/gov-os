# ACT-MSET-2: the cross-check of the measurement set's 60 questions (DEC-1070 (4), ACT-MSET-1 section 6)

For a **second fresh session the owner opens, outside the CTO's system**, used only for this. It is not the writer's
session and was never shown the writer's work. **Nothing about the 60 reaches the CTO's session:** the checker
writes its report where only the owner and the writer read it, and the CTO receives only the counts line of
section 6.

## 1. What it is for
- The measurement set is the verdict on memory: 60 questions, written blind by the writer (ACT-MSET-1), measured only
  at decision points, never used to choose or tune. **The target stands: 95 % hit@5, 85 % the floor.**
- A wrong question misjudges memory in either direction. This check finds wrong questions **by the rubric alone**,
  before the set is ever measured. It never asks how retrieval would do with a question: a question the product
  would miss is not wrong for that, and one it would hit is not right for that (RUBRIC.md section 4).

## 2. What the checker reads, and what it never reads
**Reads:**
- the 60 questions: `~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/m01.yaml` to `m60.yaml`, read-only;
- the repository at `w2/integrate`'s head (`/home/usain/Dynamic-Agentic-Engineering-OS`), read-only;
- the rubric `docs/research/memory-measure-audit/RUBRIC.md` (version 2), sections 1, 2 and 4 in full.

**Never reads:**
- the tuning sets: the visible questions (`fixtures/evaluation/memory-retrieval/` in the repository) and the hidden ones
  (`~/gov-os-eval/fixtures/evaluation/memory-retrieval/`);
- any measure, search or run output (`~/gov-os-runs/`, `~/gov-os-eval/runs/`);
- the audit and research records about the measure: `docs/research/memory-measure-audit/` other than `RUBRIC.md`,
  `docs/audit/memory-measure-*`, `docs/research/EXP-003/`, and `.gov-runtime/` (the CTO's drafts and logs);
- the decision register's DEC-1066 to DEC-1070 for anything beyond the rubric's rules (they name misses).

**How it searches:**
- A file-name denial does not stop a recursive search started above a denied folder.
- So every `grep -r`, `find` or similar search names its folders (for example `src/`, `docs/contract/`,
  `docs/plan/`, `.tickets/`, `template/`), or excludes the denied ones. For the latter:
  `--exclude-dir=fixtures --exclude-dir=.gov-runtime --exclude-dir=EXP-003 --exclude-dir=memory-measure-audit`, with
  `docs/audit/` and `tests/acceptance/W2-61*` left out.
- It is never run from `~` or from `~/gov-os-eval`.

**Never runs:**
- `gov retrieve`, `gov context`, `gov.retrieval.measure`, or any model;
- any command that writes to the repository or to git.

## 3. The method
1. **Where:** the head of `w2/integrate`, with the path map there. Record the head's 12-character commit in the report.
2. **The sources, by the measure's own rule** (RUBRIC.md section 1, item 2):
   - resolve each `heading` as the first line of the file equal to it, and check it is the only such line;
   - take its span: a Markdown heading runs to the next heading of the same or a higher level; any other heading
     runs as many lines as `lines` state;
   - read every span in full;
   - place every path with the path map's own matcher (`src/gov/check/pathmap.py`) against
     `governance/project/path-map.yaml`.

   The checker may import `_span` from `src/gov/retrieval/measure.py` and the matcher. Running the measure itself is
   not allowed.
3. **Apply R1 to R11 to each of the 60,** exactly as the rubric states. Judge R5 on the set, against ACT-MSET-1
   section 2's counts for 60 (each governing domain at least 6, no subsystem above 15, and the category table).
4. **R9 is checked among the 60 only.** Overlap with the tuning sets was checked by the writer's overlap script and
   came to 0. The checker cannot run it: its denials keep it from the tuning sets. The writer runs it again after
   the fixes (section 5).
5. **A FAIL is major** when it changes what is scored (a wrong or missing gold source, a span that misses the answer,
   a wrong answer). **It is minor** when it does not (a stale detail in the gold answer's text, a category).

## 4. The report
Write one file: `~/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md`. It is outside the questions folder,
so the measure never reads it. Its form is the hidden cross-check's (`docs/audit/memory-measure-new-hidden.md`,
section 1's verdict table and section 2's per-question lines):

1. **A header:** the head judged, the rubric version, and what was read and not read.
2. **The verdict table:** the ids that may enter as written; those that enter after a minor fix; those that need a
   major fix; those to drop.
3. **Per question:** its id, each item PASS or FAIL, the reason code, a reason in general terms, and the
   recommendation in the rubric's five words (re-label, re-anchor, re-word, mark as a keyword question, retire).
   - **A reason in general terms** says what is wrong without quoting the question. For example: "R6-SPAN-MISSES: the
     anchor's span ends before the deciding line".
   - **It never quotes** a question, gold answer, path, heading, line or fact. The writer, who has the files, applies
     each fix from it.
4. **The set:** R5's counts per governing domain, tag and category; R2's two counts; the number of FAILs per item,
   major and minor apart.

The checker makes no fix. The writer's session makes them, by the report and the owner's word, keeping each changed
question's old copy as `<id>-pre-xcheck.yaml` beside `XCHECK.md`, never in the questions folder.

## 5. After the fixes
- The writer runs ACT-MSET-1 section 6's three checks again: `unresolved: 0`, `overlapping ...: 0`, and the category
  counts.
- If any fix was major, the checker re-checks those ids only, and adds a dated section to `XCHECK.md`.

## 6. What reaches the CTO
One line, from the owner:

```
xcheck: <n> as written, <n> minor fix, <n> major fix, <n> drop; after fixes: unresolved 0, overlapping 0
```

The CTO then measures `memory-verdict` only at the decision point DEC-1070 (8) names: the 0.6B's new record.

## 7. The session's folder (for the owner's operator)
- **A copy of the writer's settings:**
  - the same read denials;
  - the same two directories (the repository, and `~/gov-os-eval/fixtures/evaluation/memory-verdict/`);
  - model opus;
  - `acceptEdits`.
- **The one change:** write access only to `~/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md`. Nothing
  else is written, the 60 included.
- **Start it** from that folder as the writer's was. Then paste:

> Read `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-MSET-2.md` and follow
> it exactly. Write your report only to `~/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md`. Tell me only
> "done" and the verdict table's four counts.

## Rollback
Delete `XCHECK.md`. The checker writes nothing else.
