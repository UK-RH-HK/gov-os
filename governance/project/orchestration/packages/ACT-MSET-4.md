# ACT-MSET-4: the cross-check of the new verdict set's 80 questions (DEC-1074 (3), ACT-MSET-3 section 6)

- **For:** a **second new session the owner opens, outside the CTO's system** (`~/gov-os-checker2`, ACT-MSET-3
  section 9), used only for this. It is neither the writer's session nor the 60's checker, and was never shown the
  writer's work.
- **Nothing about the 80 reaches the CTO's session.** The checker writes its report where only the owner and the
  writer read it, and the CTO receives only the counts line of section 6.
- **By:** the CTO, session `812bc5ce`, 2026-11-05, from ACT-MSET-2 (the 60's cross-check), with the set's name, size and
  quotas changed.

## 1. What it is for
- The new set is the verdict on memory at the next decision point: 80 questions, written blind by the writer
  (ACT-MSET-3), measured once, never used to choose or tune. **The target stands: 95 % hit@5, 85 % the floor.**
- A wrong question misjudges memory in either direction. This check finds wrong questions **by the rubric alone**,
  before the set is ever measured. It never asks how retrieval would do with a question: a question the product
  would miss is not wrong for that, and one it would hit is not right for that (RUBRIC.md section 4).

## 2. What the checker reads, and what it never reads
**Reads:**
- the 80 questions: `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/hidden/v01.yaml` to `v80.yaml`, read-only;
- the repository at `w2/integrate`'s head (`/home/usain/Dynamic-Agentic-Engineering-OS`), read-only;
- the rubric `docs/research/memory-measure-audit/RUBRIC.md` (version 2), sections 1, 2 and 4 in full;
- ACT-MSET-3 section 2 (the size and the quotas).

**Never reads** (the session's settings deny each): every other question set (the visible and hidden tuning sets and
the spent 60, `~/gov-os-eval/fixtures/evaluation/memory-verdict/`); the earlier writers' and checkers' folders; any
measure, search or run output; the records about the measure and its misses (ACT-MSET-3 section 3's list); all of
`.gov-runtime/`; the decision register's DEC-1066 to DEC-1074 for anything beyond the rubric's rules.

**How it searches:**
- A file-name denial does not stop a recursive search started above a denied folder.
- So every `grep -r`, `find` or similar search names its folders (for example `src/`, `docs/contract/`,
  `docs/plan/`, `.tickets/`, `template/`), or excludes the denied ones:
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
3. **Apply R1 to R11 to each of the 80,** exactly as the rubric states. Judge R5 on the set, against ACT-MSET-3
   section 2 (each governing domain at least 8, no subsystem above 20, and the category table with its one allowed
   shift).
4. **R9 is checked among the 80 only.** Overlap with the earlier sets was checked by the writer's overlap script and
   came to 0. The checker cannot run it: its denials keep it from those sets. The writer runs it again after the
   fixes.
5. **A FAIL is major** when it changes what is scored (a wrong or missing gold source, a span that misses the answer,
   a wrong answer). **It is minor** when it does not (a stale detail in the gold answer's text, a category).

## 4. The report
Write one file: `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/XCHECK.md`. It is outside the questions folder,
so the measure never reads it. Its form is the 60's (`~/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md`,
which this session may not read; the form is restated here):

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
question's old copy in `memory-verdict-2/retired/`.

## 5. After the fixes
- The writer runs ACT-MSET-3 section 6's five checks again.
- If any fix was major, the checker re-checks those ids only, and adds a dated section to `XCHECK.md`.

## 6. What reaches the CTO
One line, from the owner:

```
xcheck: <n> as written, <n> minor fix, <n> major fix, <n> drop; after fixes: anchors 0, unresolved 0, overlapping 0, quota PASS
```

The CTO then measures `memory-verdict-2` only at the next decision point (DEC-1074 (3)).

## 7. Start it
From `~/gov-os-checker2` (its settings in ACT-MSET-3 section 9), once the writer says "done". Then paste:

> Read `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-MSET-4.md` and follow
> it exactly. Write your report only to `~/gov-os-eval/fixtures/evaluation/memory-verdict-2/XCHECK.md`. Tell me only
> "done" and the verdict table's four counts.

## Rollback
Delete `XCHECK.md`. The checker writes nothing else.
