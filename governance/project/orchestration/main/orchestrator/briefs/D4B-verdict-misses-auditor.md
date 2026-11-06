# The spent 60's 19 misses, classified by kind (DEC-1074 (2)): the brief for an independent auditor in W2-61h's role

You are an independent auditor acting in W2-61h's role (the hidden half's checker, `.tickets/DAEO-h2k3.md`), for the
CTO, under the owner's order of 2026-11-05. You classify why each of 19 questions of the spent measurement set
(`memory-verdict`) missed. **You report kinds and counts only.** The CTO, who tunes memory, must never see a question,
an answer, a gold path, a heading, a line or a fact of this set.

## Why this matters
- The measurement set (60 questions, written blind outside the CTO's system) scored 40 of 59 on the final structure
  (67.8 %), against 85.0 % and 84.6 % on the two tuning halves. The owner recorded 67.8 % as the honest figure and made
  the 60 a diagnostic set (DEC-1074 (1), (2)).
- The owner chooses the next lever from your kinds: **mostly ranked low → the reranker trial next; mostly never
  retrieved → the embedder and the query's phrasing first.** Nothing is tuned until then. So the classification must be
  honest, in either direction.
- The path map's line for `memory-verdict` refuses the auditor role. It was written while the set was the verdict.
  DEC-1074 (2) now makes it a diagnostic set and orders an independent role to classify its misses; the owner named you
  for it (2026-11-05). This read is that order, and only for the 19 files below.

## The rules
- **Read-only**, except your one report file (below). Nothing is run: no `gov`, no `gov retrieve`, no measure, no model,
  no GPU. You may run small Python to resolve spans and read the store, as the earlier diagnosis did.
- **The hidden-half rule.** Your report and your return hold ids, kinds, counts, tiers and general phrases only. Never a
  question's text, a gold answer, a gold path or file name, a heading, a line number, a fact, a code symbol or a
  distinctive phrase from any of them, nor the path of a competing chunk. Describe in general terms ("a decision record
  on the same subject", "a numbered list item", "the question uses the user's word; the record uses a label").
- **No label is judged.** If a question seems wrong to you, write only "label doubt" against its id, with a rubric code
  (`docs/research/memory-measure-audit/RUBRIC.md`), and classify it as it stands.
- **Do not read:** the other 41 questions of the set; the tuning sets (`fixtures/evaluation/memory-retrieval/` in the
  repository and `~/gov-os-eval/fixtures/evaluation/memory-retrieval/`); `XCHECK.md`; the CTO's drafts under
  `.gov-runtime/scratch/orchestrator/drafts/` other than the two stage files named below.
- **Searches:** name the folders (`src/`, `docs/`, `.tickets/`, `template/` …) inside the clone. Never a recursive search
  from `~` or `~/gov-os-eval`.
- Your guard: the five rules of `EMG-common.md` hold. A refusal is taken, never routed round; name it in your return.

## What you read
1. **The 19 questions**, by id, in `~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/`:
   m02, m03, m05, m09, m12, m15, m18, m20, m22, m24, m26, m30, m33, m37, m39, m41, m42, m43, m51. (m60, the
   nonexistent-id question, passed and is scored apart.)
2. **The structure that was measured:** the clone `~/gov-os-runs/D4B/g1/repo` at `e884675b` (m6's code with the stated
   links), its store `.gov-runtime/store.db` (read-only), and the harness configuration v456: the meaning route not cut
   after its phrasings are fused, both routes 60 deep, the first 40 fused candidates reranked in one pass by
   Qwen3-Reranker-0.6B, at most 2 chunks of a file in the first 10, nested repeats dropped. Resolve each gold span with
   the measure's own `_span` (`src/gov/retrieval/measure.py`).
3. **The kept outputs** of that run, `~/gov-os-eval/runs/verdict/v-run1/` (one file per search, in call order). Each
   miss's first call:
   m02 00006, m03 00011, m05 00021, m09 00041, m12 00056, m15 00071, m18 00086, m20 00095, m22 00105, m24 00115,
   m26 00125, m30 00144, m33 00154, m37 00174, m39 00184, m41 00195, m42 00200, m43 00205, m51 00245
   (`<n>.json`; the later calls of a question follow it up to the next one's first call). `evidence` holds the 40
   reranked in order; `gaps` with reason `NOT_GATHERED` hold the fused candidates cut below them, in order.
4. **The CTO's stage rows** (ids and ranks): `~/gov-os-runs/D4B/diag/stage1-verdict.json` (where each gold piece first
   appears in the first call: in the 40, cut, a sibling of its section in the 40, or absent) and
   `~/gov-os-runs/D4B/diag/stage2-verdict-depth1000.json` (each piece's rank in the keyword and meaning routes, 1,000
   deep, with the product's phrasings, by its own span or its parent's). In stage 1's text, "in the 20" means "in the
   reranked pool", which is 40 under v456.
5. The route code as needed: `retrieve.py`, `routing.py`, `lexical.py`, `semantic.py`, `chunking.py`, `rerank.py`.
6. For comparison of form only: the earlier diagnosis `docs/audit/memory-recall-diagnosis-hidden.md` (its K1-K8 kinds).

## What you decide, per id
1. **Stage** (from the stage rows; check them against the kept output):
   - `NEVER`: neither the gold's chunk nor its section is in either route's top 60, so it never reached the pool;
   - `CUT`: in the fused list, cut below the 40;
   - `SECTION`: a chunk of the gold's section is in the 40, but not the answering lines;
   - `LOW`: the gold is in the 40, reranked below 5.
2. **The main cause**, one of:
   - `VOCABULARY`: the question asks in other words than the gold states (a user's word against a record's label, a
     paraphrase with few shared distinguishing words), and that is what keeps it out or down;
   - `RERANK`: the routes bring the gold high enough, and the reranker puts below it chunks that answer the question
     less well (say what kind and tier, in general terms). Note whether a route had the gold in its own top 5 (stage 2);
   - `FORM`: the answer is one item (list item, row, field, single line) diluted in its chunk, or split from its heading;
   - `CROWDING`: the same topic restated across files, tiers or copies fills the places;
   - `HOP`: the answer sits in a record linked from the one the question names (supersession, citation, a ticket's
     source), not in it;
   - `MULTI-PART`: a two-part question whose pieces each match half its words;
   - `OTHER`: name it in general terms.
   Also list any secondary causes, and the earlier K1-K8 kinds that apply.
3. **The owner's kind (the headline), by this rule:** `vocabulary` if the main cause is VOCABULARY; otherwise
   `never retrieved` if the stage is NEVER; otherwise `ranked below 5` if the stage is LOW or CUT; otherwise `other`
   (SECTION with a non-vocabulary cause, or anything else).
4. **The levers that plausibly reach it** (all that apply, with "strong" or "weak"): a stronger reranker; a stronger
   embedder (the meaning route's grasp of other words); query phrasing or term mapping; widening a gathered chunk to its
   section; a deeper pool; a hop; answer-unit chunks; none of these.

## The report
Write one file: `docs/audit/memory-verdict-misses-kinds.md`, in the form of the earlier diagnosis:
1. A header: by, date, what was read, what was not, the hidden-half rule kept, no label judged.
2. A table per id: stage, main cause, secondary causes, K-kinds, what outranked the gold (kind and tier, in general
   terms), levers.
3. **The counts over the 19:** the owner's four kinds; the stages; the main causes; the cross-table of stage against
   main cause; the levers (strong and weak apart); for LOW and CUT, how many had a route's own top 5 holding the gold.
4. One short paragraph, in general terms: what the misses have in common, and which lever reaches most of them. No
   recommendation to the owner; that is the CTO's.

Before you return, run the leak check on your report and fix it until it prints 0 and 0:
```
python3 -I /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/leak_check.py \
  ~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden /home/usain/Dynamic-Agentic-Engineering-OS/docs/audit/memory-verdict-misses-kinds.md
```
Do not commit; the CTO commits the report after its own leak check.

## Your return
The labelled lines task, status (DONE, PARTIAL or PACKAGES), work_completed, files_changed, evidence (the leak check's
line), tests (none), discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action. Then the
counts tables of section 3 only. Nothing else about the questions.
