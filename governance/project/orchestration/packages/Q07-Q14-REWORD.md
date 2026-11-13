# Q07 and Q14 re-worded to stable facts (DEC-1070 (13))

- **Under:** DEC-1070 (13), kept by DEC-1074 (8), DEC-1097 (12) and DEC-1098 (6); the rubric
  `docs/research/memory-measure-audit/RUBRIC.md`, version 2 (R1 to R11).
- **By:** a session independent of the retrieval work, 2026-11-09, blind at `w2/integrate` `8bb10a68366c`. It read
  only Q07's and Q14's files, the rubric and the repository records the new gold needs. It ran no search and no
  `gov retrieve`, and it read no result, no other question, no hidden or spent set and no audit record.
- **Files:** `fixtures/evaluation/memory-retrieval/visible/q07.yaml` and `q14.yaml` re-written. The originals are
  kept byte for byte as `retired/q07-pre-reword-2026-11-09.yaml` and `retired/q14-pre-reword-2026-11-09.yaml`, named
  after the folder's `<id>-pre-<tag>.yaml` form. The retired README gains a section for them.
- **Loader check:** both files load with the measure's own loader (`gov.retrieval.measure._load`, part `visible`,
  the path map's families, no retriever run). Every alternative resolves by its heading at the head, the spans are
  the stated lines, and none is unresolved. Each heading line occurs once in its file.

## Q07 (category `ticket`, ticket DAEO-0mab, W2-24)

- **Old fact:** the list of tickets the Track A gate run depends on (23 at cc9c94d42a54; 27 in lens B's label).
- **Why it drifted:** it was a list that re-scoping moved. DEC-954 took nine tickets out and put five in, so the gold
  went stale (R11-GROWS; marked volatile by DEC-1069 (6)).
- **New question:** "Did the Track A gate (W2-24) have to wait for the Track A tickets that got pushed back to
  Wave 3?"
- **New stable fact:** no. Under DEC-954 its dependencies are only the Track A tickets that stayed in Wave 2. This is
  a decided rule, and it changes only by a decision.
- **Sources (one entry, three alternatives, each holding the whole rule):**
  - `docs/plan/WAVE_2_WBS.md`: the W2-24 card's DEC-954 line, line 800.
  - `docs/plan/WAVE_2_WBS.md`: the W2-24 table row, line 150 (the old label's second source).
  - `.tickets/DAEO-0mab.md`: the body's `**DEC-954:**` line, line 72.
- **Rubric:**
  - **R1:** DEC-954 is ACCEPTED, and no later entry changes W2-24's dependency rule. W2-24's later retirement
    (DEC-1083, W-8) does not change what it was to wait on. The gold makes no claim about the AR-line reporting
    that DEC-1084 moved to W2-46.
  - **R2:** both paths are embedded (`docs` covers `docs/plan/**`; `tickets`).
  - **R3:** it asks one fact and presupposes nothing false.
  - **R4:** a lead checking a ticket's dependencies would ask it, in its own words ("pushed back", "wait for"). The
    source's words "Wave 2 tickets only" and "removed" are not used.
  - **R6:** each span is the deciding line, with no overrun.
  - **R7:** the three places are alternatives of one entry, and each holds the piece whole. The withdrawn W2-48 is
    left out of the gold because the ticket's line does not name it.
  - **R8:** no source is an evaluation document.
  - **R10:** the form and the record are complete.
  - **R11:** it is a rule, and the ticket is closed.
  - **Open (R5):** the question keeps category `ticket`, so its place in the category quota is unchanged. Its
    governing record is now the plan's DEC-954 line, with the ticket as a restatement. If R5's domain count goes by
    the governing source, the CTO should count it under the plan, not tickets.
  - **Open (R9):** I could not check it, because I read no other question.

## Q14 (category `ticket`, ticket DAEO-ym8a, W2-03, radius 1)

- **Old fact:** the tickets that list W2-03 in `depends_on` (nine in lens B's label; 13 at cc9c94d42a54, over 13
  files).
- **Why it drifted:** a list of dependents grows with every ticket filed against W2-03 (R11-GROWS; marked volatile by
  DEC-1069 (6)).
- **New question:** "Before W2-03 could close, what did it have to show about how decisions get hashed, including
  when one is edited?"
- **New stable fact:** W2-03's KPIs:
  - each `### DEC-nnn` entry is its own record, hashed (sha256) over its own span, so no two decisions share a hash;
  - an edit changes only that entry's hash, and a duplicate id is refused, naming both places.
- **Sources (two entries, three alternatives each):**
  - The per-decision hash: `.tickets/DAEO-ym8a.md` lines 31 (front matter) and 66 (body);
    `docs/plan/WAVE_2_WBS.md` line 325 (the W2-03 card).
  - The edit case: `.tickets/DAEO-ym8a.md` lines 36 and 70; `docs/plan/WAVE_2_WBS.md` line 329.
- **Rubric:**
  - **R1:** the ticket is closed, and the card is approved (DEC-729). No later decision changes these KPIs (DEC-752
    and DEC-755 touch the start and the paths only).
  - **R2:** both paths are embedded.
  - **R3:** it asks two facts, one entry each, and has one reading.
  - **R4:** a test designer or an auditor checking a ticket's KPIs would ask it. The source's words ("record of its
    own", "share", "span") are not in the question.
  - **R6:** each span is the KPI line, with no overrun.
  - **R7:** one entry for each needed piece. The alternatives are the same text in three places.
  - **R8:** no source is an evaluation document.
  - **R10:** the form and the record are complete.
  - **R11:** item 4 applies: it is a closed ticket's front matter plus the plan.
  - **Open (R5):** the WBS card is the plan and the ticket restates it. The question keeps category `ticket`, so
    count its domain as for Q07.
  - **Open (R9):** a code question about decision hashing, if the visible set has one, has a different governing
    source (the code), but the CTO should check it.

## What no source settled

- **The retired-file name:** the brief named `<name>.pre-reword-2026-11-09.<ext>`, and the folder's convention is
  `<id>-pre-<tag>.yaml`. I followed the convention, as the brief allowed.
- **The commit field:** the question's `commit` is `8bb10a68366c`, today's head when written. `w2/integrate` had
  moved past `9546edd6` during the session; none of the cited files changed between the two.
- **To do:** the CTO commits the files and syncs the sets root's visible copy.
