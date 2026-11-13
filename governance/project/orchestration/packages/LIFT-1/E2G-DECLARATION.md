# E2G: E2's condition with the repository glossary consultable, declared before its run (DEC-1096 (4))

The CTO, 2026-11-07, session `ad44f5fe`. This record is committed before E2G runs.

## What is tested
**The question:** do agents answer more questions right end to end when they can consult the repository's own vocabulary (the glossary and the code-name map) at the moment a search does not answer?
- **The baseline:** E2 (`E2-RESULT.md`): today's bundle, search again once. A2 128 of 138, A3 128, wrong claims 3.

## The condition
- **The same as E2 in every other respect:**
  - the 138, plus h24 and m60 counted apart;
  - each question's first bundle from E0's kept outputs;
  - E2's reader (`claude-opus-5-5`, effort high, no tools, no transcript, the "may be incomplete" line);
  - up to three attempts, A1 and A2 being A3's run cut;
  - later searches live with the pinned gov on E0's clone;
  - the citation by the measure's matcher;
  - the graders `claude-opus-5-5` (counts) and `claude-sonnet-5-5` (agreement).
- **The one difference: consulting the glossary when a search does not answer.**
  - When the reader asks to search again, the harness looks up the prototype glossary (`~/gov-os-runs/D4B/glossary/`, built from E0's clone at `c00d525f`, the evaluation fixtures excluded) with the question and the reader's proposed words, and takes the top 30 entries (`lookup.py`).
  - It gives them to the reader in one short extra call: "Here are the repository's own terms, ids and code names that match. Give your search words in the repository's vocabulary." The reader answers with words only.
  - The search runs with those words.
  - The glossary is never in the first call and never pasted whole, as DEC-1096 (3) says.
- **Script:** `drafts/d4b/e2g_run.py` (E2's script with the consultation step). It runs once the prototype's tests pass.

## What is reported
- **Right end to end** at A1, A2 and A3, per set and on the 138, with exact McNemar against E2:
  - **A2 against A2 is the judged comparison** (two searches is the practice, DEC-1094 (2));
  - A3 against A3 beside it.
- **Wrong claims; not found;** misses recovered.
- **The extra calls' tokens and cost,** and the cost per question against E2's $0.157.
- **How often the glossary was consulted,** and how often the words it led to differed from the reader's own.
- **A1 is the same prompt as E2's A1,** so any difference there is the reader's run-to-run spread, reported as such.

## Cost and the brake (DEC-1091 (2))
**Projection: $26** (E2's $21.95, plus about 20 short consultation calls). **Brake: $52.**

## What it decides
- **If E2G's A2 is not below E2's,** with fewer or equal wrong claims, the glossary may join the configuration the owner decides for the fresh 80 (DEC-1096 (4)).
- **The test is on the 138,** which are tuning sets. The fresh 80 judges once.

**Basis:** question 1.
