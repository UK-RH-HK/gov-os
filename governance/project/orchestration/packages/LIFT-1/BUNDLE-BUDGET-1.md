# BUNDLE-BUDGET-1: no bundle over its token budget (for the owner; DEC-1085 (1), (8))

**Status:** for the owner's decision. Nothing is built before it.

## The cause (DEC-1085 (8))
The 8,886-token first call is m29's, in the spent set. One of its 20 items is a JSON file written on one line of 24,575
characters, about 6,100 tokens, sent whole. Two rules let it through:
1. **A chunk is never shorter than one line** (`src/gov/retrieval/chunking.py:102`). A file on one line becomes one
   chunk of any size.
2. **The 6,000-token budget only governs parent expansions** (`src/gov/retrieval/retrieve.py:530`). The page's base
   items are always sent whole, whatever their size.

## How often (the 0.6B's kept run on the 138, all calls)
- **13 of 688 calls** are over the budget, by 475 to 6,543 tokens. Three of them are first calls: m29 8,886, Q12 6,527
  and h09 6,475.
- **All 13** hold one item that is a single line over 4,000 characters: JSON files written on one line, a 10,631-character
  line in `docs/changes/W2-32-evidence.md`, and a 16k ticket line.
- **Without those items, the largest call is 4,633 tokens.** Nothing else breaks the budget.
- **What it costs an agent:** those items are mostly unreadable noise (minified JSON), and they push the bundle past the
  budget its caller planned for.

## Options
- **(a) A cap per item (recommended).**
  - An item whose text is over 4,000 characters (about 1,000 tokens) is sent as its first 4,000 characters. It carries
    a mark `cut: {"chars": <total>, "sent": 4000}`, and its path and lines are cited unchanged. An agent that needs
    more reads the file.
  - Nothing else changes: the same items, the same order, the same batches and continuation. The reranker already
    reads only the first `RERANK_CHARS`, so the order cannot move.
  - **The measures do not move:** hit@5, hit@10 and "in the bundle" judge by lines, not text.
  - Cost: one small ticket (W2-135, about 30 lines in `retrieve.py`), tests first by an independent test designer, one
    review. About half a day in all (est.).
  - Timing: after W2-32 and W2-133 merge (all three touch `retrieve.py`), in re-pin window 4. The end-to-end
    experiments (DEC-1085 (6)) then read the bundle that ships.
- **(b) The cap, and the budget enforced on base items.** As (a), and any item after the top 10 that would cross the
  limit is held for the continuation. Today's data never needs it (largest 4,633 without long lines). It changes
  which items a call sends, so the measures would move. Cost: about one day (est.).
- **(c) Split long lines at index time.** The chunker cuts a line over the limit into character pieces. Citations by
  line no longer name one piece, so the bundle, the measure and the stated links would all need a character offset.
  Cost: several days (est.). Not recommended.

**Recommendation: (a), filed as W2-135, in re-pin window 4.**
