# Readiness review 4 of 7: chunking, the line cap and the pool's drop_nested (W2-135; W2-32 S11), before the fresh 80

Reviewer: independent, read-only, 2026-11-08 (DEC-1097 (3); proposal `FRESH-80-READINESS.md` §5 item 4). Branch
`w2/integrate` at `e66f2a696a6e`. Pinned `gov` `pin-bcea09060ebc`, store `~/gov-os-worktrees/W2-00-store` (its HEAD
`e66f2a696a6e`, pool on). Judged by ADR-0001's threat model and the two questions, word for word: "Can an honest agent
hit this in ordinary work?" and "Does it fail open or lose work?" A finding is FIX BEFORE THE 80 only if it is in
scope, reachable in ordinary work, and fails open or would make the fresh-80 verdict wrong. Anything else is a ROW
(DEC-1010).

Nothing under `~/gov-os-eval/` and no hidden or spent question file was opened, listed or read. No commit, no rebuild,
no GPU work, no install. Guard refusals: 0.

## What I read and ran

- **Code:** `src/gov/retrieval/retrieve.py` (`capped`, `item()`, the pool block, `span`, `drop_nested`),
  `pool.py`, `chunking.py`, `config/loader.py` (pool keys), `decisions/register.py` (`leave_out`, `narrowed`) and
  `retrieve/command.py`.
- **Equality with the pin:** `pool.py`, `chunking.py` and `register.py` in the pin are byte-equal to the source.
  `retrieve.py` has changed since `c00d525f` only for W2-138's commit in the token; `capped`, the pool and
  `without_nested` are untouched.
- **Records:** W2-135's ticket (`DAEO-c4pb`), its evidence, and its review (both rounds, `reviews/w2-135.md`); the S11
  review (`reviews/w2-32-s11.md`); `PAT-1-RESULT.md` §7 and `pat/A-`, `B-findings.md`; `E3-RESULT.md`; DEC-1097 (7).
- **Unit tests** (`test_w2_135_item_cap.py`, `test_w2_32_pool.py`, `-m "not local_only"`, TMPDIR in my folder):
  **41 passed**, 30 deselected.
- **Searches:** 8 `gov retrieve --json` searches, one at a time, with my own questions (none from any set).
- **What the searches answered:**
  - q7 answered "how `without_nested` decides" (`pool.py` 92-102, first);
  - q8 answered "the S11 row of W2-32's evidence" (the row was sent cut).
  - The others were taken for their overlap figures; I did not rely on their answers.

## Check 1: the line cap (W2-135): PASS

- **The code:** `capped(body, first)` measures each line without its newline, in characters. A line over 4,000 is sent as
  its first 4,000 plus its own newline, and every other line is sent whole. `cut: {chars, sent, lines}` comes from the
  same per-line condition, so a cut line cannot go out without its key. `item()` sets `path`, the lines, `id`,
  `chunk_id` and `sha256` from the full span. Expanded pieces and narrowed register items (`narrowed()`) go through the
  same function.
- **Live, two cuts seen:**
  - q5: `.tickets/DAEO-2d6f.md` line 34, `{"chars": 16423, "sent": 4001, "lines": [34]}`;
  - q8: `docs/changes/W2-32-evidence.md` line 34, `{"chars": 6850, "sent": 4001, "lines": [34]}`.
- **Checked against the files, all 77 items of q5 to q8:**
  - each item's `sha256` is that of its cited lines;
  - each uncut item's text equals its cited lines exactly, and none of them holds a line over 4,000;
  - each cut item's text equals the per-line cut of its lines.
  - So no ordinary item was cut, no long line went out whole, and the lines are cited unchanged.

## Check 2: the pool as declared (`retrieval.yaml` `pool:`): PASS, with one wording row

- **`route_depth` 60:** passed per search as `top_k` to `lexical.search` and `semantic.search`; neither module's
  `TOP_K` is set.
- **`meaning_uncut`:** the meaning route's phrasings are fused without a cut (`cut=None`).
- **`rerank_depth` 40:** every bundle reports `pool.reranked: 40`, `order: first`, `rerank.by: service`.
- **`drop_nested`:** it drops only an item whose lines lie inside an earlier kept item of the same file. Over 8
  searches it dropped 13 items, each named in `pool.nested`, and each such item's lines were in a kept item of the
  same bundle.
- **`drop_nested` and the register:** it runs before `register.leave_out` (in `command.py`). A Markdown register's
  parent never spans two entries, so no dropped item's lines can be lost when an entry is left out afterwards.
- **`per_file_first10` 2:** holds on the candidates' order, as v456 measured (R4-1 on the wording).

## Findings

**R4-1: `per_file_first10` does not hold on the bundle's first 10 items, as its comment says it does.** (In scope.)
- **What the comment says:** `retrieval.yaml` and `pool.py` read "at most 2 chunks of one file in the first 10 of the
  final order".
- **What the bundles held:**
  - 3 items of one file in the first 10 in q3, q4 and q7: expansion pieces and `drop_nested` shift the items after
    the cap;
  - 7 register items in the first 10 in q6: when a page holds too few other files, `pool.capped` leaves its head
    short and puts the rest after it, in order.
- **Whether it is a defect:** no. It is the code that v456 and E0 to E3 measured, and every item is still sent.
- **Fix:** re-word the comment, for example "of the candidates' order".
- Ordinary work: yes, because any question whose page is dominated by one file (the register) shows it.
- Consequence: other (the order differs from the comment's wording; nothing is lost, nothing fails open, and the
  measured configuration is the same). **ROW.**

**R4-2: the budget's `used` counts a cut line's full length, so a page holding one gets fewer expansions.** (In
scope.)
- **What the bundle showed:** q5's `used` was 7,293 against a limit of 6,000, while it sent 16.7k characters (about
  4.2k tokens). It made no expansions.
- **Why:** W2-135's S3 required this, and E3 shows that expansions are worth +13 right answers on the 138.
- **Whether it changes the 80:** no. The measured window-4 configuration does the same, so the verdict describes it
  honestly.
- **After the lift:** count the sent text. That is a retrieval change, so it goes through the 138 (§4 of
  FRESH-80-READINESS).
- Ordinary work: yes, because a page holds such an item whenever a long-line file ranks (25 tracked files hold a line
  over 4,000).
- Consequence: other (fewer expansions on those pages). **ROW.**

**R4-3: Markdown table rows over 4,000 characters are cut too, not only one-line files.** (In scope.)
- **Where:** `docs/changes/W2-32-evidence.md` holds 7 such rows (S11's row, 6,850 characters, was sent as 4,000 in
  q8). Ten close records each hold an 8,129-character line, and two ticket rows run about 16k.
- **Whether it is a defect:** no. This is DEC-1086 B as re-worded by round 2 (lines, not items). The cut is marked
  with its line numbers, and the item cites the whole line.
- **What could help:** one line in the retrieval skill or briefs: "an item with `cut`: read its cited lines from the
  file before relying on it".
- Ordinary work: yes, because KPI evidence tables are an ordinary form.
- Consequence: other (marked, never silent; the tail is not in the bundle). **ROW.**

**R4-4: the chunker and the bundle split lines differently.** (In scope as chunking; it is W1-17's and predates W2-135.)
- **The difference:** `chunking.chunk_text` numbers lines with `str.splitlines`. `retrieve.span` and `capped` read
  lines with `bytes.splitlines`.
- **Its effect:** in a file holding U+2028, U+0085, `\f`, `\v` or `\x1c` to `\x1e`, every chunk after that character
  is one line off.
- **In the store:** `tests/unit/check/test_citations.py` (200 lines as bytes) has a chunk `201-201`, and the two
  readings diverge from line 73. Such an item's text and `sha256` still match its cited lines, so citations stay
  self-consistent. But the span ranked is one line off, and the end chunk sends empty text.
- Ordinary work: no, because it needs those rare characters in a source file (1 tracked file in the repository).
- Consequence: other. **ROW** (Wave 3; the fix is one `splitlines` rule used on both sides, which rechunks the store).

**R4-5: W2-135's ticket still reads `status: in_progress`.** (Out of scope: ticket state.)
- **What it is:** the ticket was merged (`ff64f1483`) and is carried by the window-4 pin, and its S4 is the CTO's check
  after the re-pin.
- **What to do:** close it, or name it in the K9 status fix already pending (K7-W2-REMAINDER §5).
- Ordinary work: yes. Consequence: other. **ROW.**

**R4-6: the seven reviewers share one scratch folder, and files with the same names collide.** (Out of scope: the
review's process, not memory.)
- **What happened:** my `q1.json` to `q4.json` in the session scratchpad were overwritten by another reviewer's searches,
  and my `q5.json` to `q7.json` may have overwritten another reviewer's.
- **My figures stand:** each figure above was printed straight from my own output at the moment it was written. The
  files I re-used are copied to `scratchpad/r4-chunking/`.
- **Tell the others:** any reviewer whose record cites `scratchpad/q*.json` should check the file's question first.
  The fresh-80 scripts should give each agent its own folder.
- Ordinary work: yes. Consequence: loses work (others' scratch evidence, not the product). **ROW** (out of scope).

**Known, carried, not counted:** `validate.py` gives `TEXT_NOT_FOUND` on cut items (W2-135 review R2-F6), with no
caller. The measure's stack sizes and family match read the sent text (F4): long-line items only.

## G3: overlapping slices (DEC-1097 (7): no change before the 80)

**My 8 searches (pool on, store at `e66f2a696a6e`):**

| | q1 | q2 | q3 | q4 | q5 | q6 | q7 | q8 | all |
|---|---|---|---|---|---|---|---|---|---|
| items | 18 | 16 | 19 | 17 | 20 | 19 | 19 | 19 | 147 |
| overlapping pairs (same file, shared lines) | 0 | 1 | 0 | 2 | 3 | 3 | 1 | 2 | 12 |
| of which a later item contains an earlier one | 0 | 0 | 0 | 1 | 2 | 1 | 0 | 0 | 4 |
| items in an overlap | 0 | 2 | 0 | 4 | 6 | 6 | 2 | 4 | 24 (16 %) |
| nested items dropped | 2 | 4 | 1 | 3 | 0 | 1 | 1 | 1 | 13 |

- **How often:** 6 of 8 bundles hold at least one overlap. Most share 1 to 3 lines.
- **What it costs:** duplicated characters were 3.3 % of the sent text over q5 to q8 (2,674 of 80,829; per bundle
  1.0 % to 6.2 %; worst q6, register-heavy).
- **PAT-1 for comparison:** 15 of 30 answers held an overlap, about 1.0 overlapping item per answer.
- **Their causes:**
  - `chunk_text`'s 120-character overlap between neighbouring chunks: the register is not chunked by entry, M5 is
    off, so its entries' slices overlap;
  - degenerate overlap chunks lying wholly inside a neighbour (closes, `4-5` inside `1-5`);
  - `drop_nested` keeps a later superset of an earlier item (it drops only the inside-an-earlier case).
- **Their effect:** small. They carry different lines more often than copies, and E3 measured today's bundle,
  overlaps included, best of five (114 of 138).

**Recommendation: no ticket of its own after the lift.**
- **Low value:** at most about 3 % of a bundle, and any change moves hit@5, so it must pass the 138 first.
- **Fold it into M5's retest** (DEC-1073 (3)): one span per register entry with no overlap removes the register's
  overlaps by construction.
- **If a change is still wanted, the cheap one:** drop an earlier item that a later kept item contains, keeping the
  superset (4 cases in 147 items). It goes through the 138 like any ranking change.

## Verdict

**READY for the 80** in this aspect. No finding is in scope, reachable in ordinary work, and fails open or would make
the verdict wrong. FIX BEFORE THE 80: none. Rows: 6 (R4-1 to R4-6).

Evidence: scratch folder `scratchpad/r4-chunking/`, 7 inodes, 420 KB at the end (TMPDIR removed). The disk gate was
open before the test run.

```verdict
{"kpis": [
 {"kpi": "line-cap: a line over 4,000 cut, marked cut with its line numbers, lines cited unchanged", "verdict": "pass", "findings": [{"id": "R4-3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R4-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "line-cap: an item of ordinary lines never cut", "verdict": "pass", "findings": []},
 {"kpi": "chunking: chunk lines and cited lines agree", "verdict": "pass", "findings": [{"id": "R4-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "pool behaves as declared (meaning_uncut, route_depth 60, rerank_depth 40, per_file_first10 2, drop_nested)", "verdict": "pass", "findings": [{"id": "R4-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "G3 overlapping slices described; a ticket after the lift worth it", "verdict": "pass", "findings": []},
 {"kpi": "process and records", "verdict": "pass", "findings": [{"id": "R4-5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R4-6", "scope": "out", "ordinary_work": "yes", "consequence": "loses work"}]}
]}
```
