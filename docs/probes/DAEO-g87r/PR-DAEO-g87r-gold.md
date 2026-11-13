---
type: probe
task: DAEO-g87r
reviewer_session: c3eb75b3-0434-4362-9f9c-afaaed5a4e22
implementer_session: afd71a8e-9188-42a7-b9be-9a3deb5f4ba6
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 19e9739430ba5d9e1a9e01ab071814c161592269
decisions_applied: [DEC-957, DEC-828, DEC-820, DEC-845]
scope: "W2-94 GOLD: the change to check_gold.py only, (i) to (iii) and the guard cases"
---

# Probe record: W2-94 GOLD (DAEO-g87r), the narrow independent check of the change to `check_gold.py`

## Summary

- **What was probed.** Head `19e9739430ba5d9e1a9e01ab071814c161592269` of `w2/W2-94`: the one-file change to
  `fixtures/evaluation/examin/check_gold.py` (commit `19e973943`, base `6c7772ef6`), against the owner's W2-94 GOLD
  (2026-11-13; to be recorded as DEC-1175, not yet in the register) changes (i) to (iii) and the guard cases. The
  GOLD cases came first, from the independent test designer (`133b79626974`, merged `95ac3ec049bb`; 29 red against the
  unchanged script). The question set is not in the tree; neither the lead, the engineer nor the reviewer read it.
- **Who wrote it.** An engineer: session `afd71a8e-9188-42a7-b9be-9a3deb5f4ba6` (`19e973943`).
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, Opus, effort high, session
  `c3eb75b3-0434-4362-9f9c-afaaed5a4e22`, 2026-11-13, started through `gov launch` under its OS sandbox; its brief
  carried `governance/project/briefs/JUDGEMENT.md` word for word. It wrote nothing in the repository: the lead's
  tripwire shows no change in this worktree and `git status` is empty after its session.
- **Verification at this head.** `gov accept W2-94` pass, 463 passed 0 failed; the scoped run (`lead_verify`, DEC-968)
  GREEN, 5744 tests, 0 failed, 0 errors, 6 skipped.
- **The lead's judgement: pass.** 4 findings, all scope out. F1 and F2 are ordinary work yes and fail open, but each is
  the owner-decided rule implemented to the letter ((i) with the unchanged rule 2b; (ii)'s substring segments), so they
  go to the owner as rows; F3 and F4 are ordinary work no, Wave 3 rows. No finding is in scope, ordinary work yes and
  fails open or loses work, so none blocks and no round follows (DEC-1010 item 1).
- **Rows for the CTO and the owner.** F1 and F2: the reviewer's option (b) is a read-only count on the real set before
  the close (answers that lost every token under (i) and have no content word; path tokens held only by the segment
  rule); 0 in each means the row is not realised in this set.

## The reviewer's record (verbatim)

task: DAEO-g87r
decisions: [DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-828, DEC-957, W2-94 GOLD (to be recorded as DEC-1175; not yet in the register)]

## What I probed
- **The change:** commit `19e973943`, one file, `fixtures/evaluation/examin/check_gold.py` (base `6c7772ef6`), at head `19e9739430ba5d9e1a9e01ab071814c161592269`.
- **How:**
  1. Read the diff, the whole script and the GOLD cases (`w2_94_cases.py` lines 199–279 and 429–523) with their tests.
  2. Ran old-vs-new probes of `tokens`, `answer_in` and `DRAW_LINE` on made-up text.
  3. Ran the folder against the base script and against 12 copies, each with one change undone, all under `$TMPDIR`.
- **Walls:** nothing under `~/gov-os-eval`, `~/gov-os-runs`, any `hidden` or `visible` set folder, the workbench or EXAMIN was opened.

## Found sound
**Q1. (i), (ii) and (iii) are implemented exactly.**
- **(i):**
  - `level-2`, `top-3`, `Level-2`, `zqxw-9451` and the `D-3` inside `2D-3` are no longer tokens.
  - `DEC-051`, `W2-94`, `CAP-10`, `X-5`, `ZQXW94-7`, `UTF-8` and `API-v2` stay tokens.
  - Every other token kind gives the same result old and new: `_x`, `a::b`, `--flag-2`, `fooBar`, `abc123`, `DEC-051.md`, `src/level-2`.
  - Only the hyphen branch reads the new "character before" argument.
- **(ii):**
  - The segment test runs after the literal and own-path rules.
  - A token without `/` is unaffected: removing that guard changes nothing, because such a token splits into itself (a surviving copy with identical behaviour, so not a test gap).
  - Segments out of order, a missing segment and a segment named twice but held once are all not held.
- **(iii):**
  - Only the lowercase literal `k` is newly accepted.
  - `SEED+K=`, `SEED+<k>=`, `SEED+x=`, `SEED+kk=`, `SEED+k1=`, `SEED+1k=` and `SEED+k =` are refused.
  - The digit form is parsed as before, and its `k != k2` check (`DRAW_CATEGORY_MISMATCH`) is intact.
  - Seed, parity, table, ids and the parity rule are applied to both forms.
- **Docstring:** it changes only at rule 2a and at the DRAW line form.

**Q4. No new output path.** The diff adds no print and no message. The new code returns booleans and integers only, and the output stays counts, ids and codes. No new exception path exists: the "character before" index is guarded at position 0, and `int()` is called only on digits.

**Q5. Every GOLD and guard behaviour is caught by its cases.**

| Copy (one change undone) | Result | Cases that catch it |
|---|---|---|
| Base `6c7772ef6` | 29 failed | the 29 GOLD reds |
| M1: (i) reverted | 8 failed | the four non-id-shaped holds |
| M2: no "character before" check | 2 failed | `2D-3` |
| M9: lowercase allowed in the head | 6 failed | the non-id-shaped holds |
| M10: no digits allowed in the head | 2 failed | `ZQXW94-7` |
| M3: no segment rule | 6 failed | joined path, leading/doubled slash, subsequence |
| M4: segments in any order | 6 failed | reverse order, middle swapped, named twice |
| M5: position not advanced past a match | 2 failed | named twice |
| M6: (iii) reverted | 15 failed | the literal draw forms |
| M7: `K` accepted | 2 failed | `an-upper-case-K` |
| M8: no `k != k2` check | 1 failed | `digit-form-k-differs-from-the-first-field` |
| M11: no "no `/`" guard | survives | none needed: identical behaviour |
| M12: empty segments kept | survives | none needed: differs only for a token made only of slashes |

**Q3. No correct set fails that GOLD meant to accept.** Every case that should hold does hold. A path the code builds with a join and a literal path both hold, and the literal draw is accepted for either seed parity.

## Findings

**F1: S4, scope out.** (i) combined with the unchanged rule 2b lets some answers hold with no check at all.
- **What was done:** an answer whose only identifier is a lowercase hyphen-digit word, with no content word of 5 or more letters, is checked against a span that does not contain it. Examples: `utf-8`, `It uses utf-8.`, `sha-256`.
- **What happened:** the answer now holds against any span. Under `6c7772ef6` it was checked literally and failed (probe: `answer_in('utf-8', ['nothing related here'])` was False, is now True). The word is no longer a token, the answer becomes prose, and prose with no content word "cannot be judged and holds" (docstring rule 2b).
- **What should have happened:** this is exactly the owner's (i) working with the existing 2b clause. The diff implements the decision faithfully, and it cannot be "fixed" without changing the decision.
- **Where:** `check_gold.py:233-236` together with `:279-281`.
- `Ordinary work: yes, because exact-string answers such as utf-8 or x86-64 are plausible, and the writer brief does not require back-quoting.`
- `Consequence: fails open`
- **Scope:** out. This is the owner-decided rule, not the implementation. It goes to the owner as a row.
- **What would reverse it:** the CTO's count on the real set of answers that lost every token under (i) and have no content word is 0. Or the owner states the case is accepted.

**F2: S4, scope out.** (ii) can hold a path token that names a wrong middle folder.
- **What was done:** the answer back-quotes `docs/old/foo.md`. The span mentions "docs", then any word containing "old" (for example "hold"), then "foo.md".
- **What happened:** the token holds (probe: True; was False). Short segments such as `old`, `src` or `lib` match inside ordinary words.
- **Still caught:** the clean wrong-folder case, where the span holds `docs/new/foo.md` literally (probe: False).
- **Docstring:** its "what it cannot catch" list does not name this gap. Adding it was outside the brief's "nothing else".
- **Where:** `check_gold.py:256-267` and `:277`.
- `Ordinary work: yes, because short folder names are common substrings of prose and code, although the span must also name the file after them.`
- `Consequence: fails open`
- **Scope:** out. This is the owner-decided rule (ii), implemented to the letter.
- **What would reverse it:** the owner's decision intends substring segments, as its text says. Or no real-set path token holds only through the segment rule (the CTO can count these: segment-held versus literal-held tokens).

**F3: S4, scope out.** (i) also reaches rule 3, the names in a nonexistent question, through the shared token definition.
- **What was done:** a nonexistent question names something like "level-2" or "retry-3" without back-quotes.
- **What happened:** that word is no longer a name.
  - When it was the only name, the question now gets `NONEXISTENT_NO_NAME`. This fails closed.
  - When it sits beside a nonexistent identifier and itself exists in the copy, outside any path, the `NONEXISTENT_NAME_FOUND` flag that called for a hand check is no longer raised.
  - Probe: the names of "Where does fooCache read level-2 settings?" were `['fooCache', 'level-2']` and are now `['fooCache']`.
- **Is it beyond the three changes?** The brief's (i) says "(rule 2a)". Rule 3 defines names as "identifier-shaped words", which is the 2a definition, so this follows from that definition rather than being a separate change. I name it under Q1 for the CTO to confirm the intent.
- **Where:** `check_gold.py:429` uses `tokens()`.
- `Ordinary work: no, because it needs an un-back-quoted lowercase hyphen-digit word that exists in the copy, beside the asked name, in a nonexistent question.`
- `Consequence: other` (mostly fails closed; a rare hand-check flag is lost)
- **Scope:** out. A Wave 3 row.
- **What would reverse it:** the owner's GOLD text limits (i) to rule 2a only. Then this becomes a narrow fix to ride along when the ticket resumes.

**F4: S4, scope out.** The "tail of a word" test is broader than the brief says.
- **What was done:** an id-shaped word follows a non-ASCII letter with no space between them, for example `éDEC-051` or `见DEC-051`.
- **What happened:** the word is dropped. The brief limits the drop to the tail of a word that starts with a digit.
- **Where:** `check_gold.py:236` uses `before.isalnum()`.
- `Ordinary work: no, because the set is English prose and ids are separated from the words before them.`
- `Consequence: other`
- **Scope:** out. A Wave 3 row.
- **What would reverse it:** a real answer that writes an id directly after a non-ASCII letter.

**Classification:** 4 findings, all scope out. F1 and F2 are ordinary work yes and fail open, but each is the owner's decided rule, so they go to the owner as rows. F3 and F4 are ordinary work no, so they are Wave 3 rows. Nothing blocks, and no round is proposed.

**Options for the owner on F1 and F2 (rows only):**
- (a) Accept them as decided.
- (b) The CTO runs the read-only counts named above on the real set before the close. This costs minutes and changes nothing in the code.
- (c) A later change makes a lowercase hyphen-digit answer count as literal when it is the answer's only content, and makes segments match whole words. This would be a new owner decision.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}]}
```

Overall judgement: **pass**.
