# E2G's result: E2's condition with the prototype glossary consulted (declared in E2G-DECLARATION.md, `772b4a60`)

Run on 2026-11-07, about 22:15 to 22:31 (16 minutes), by the CTO (session `ad44f5fe`). Counts only.
- **Run folder:** `~/gov-os-runs/D4B/search-again/e2g/`.
- **The prototype:** `~/gov-os-runs/D4B/glossary/` (3,158 vocabulary entries, 2,749 code names, built from E0's clone with the evaluation fixtures excluded).
- **The run:** 140 questions, 0 errors, spent $24.32 against a $26 projection; the $52 brake was not reached. The graders agreed on 140 of 140.

## Right end to end, against E2 (the same reader, bundles and graders; E2's run folder)
| | A1 (one search) | **A2 (two searches, the judged comparison)** | A3 (three) | wrong claims at A2 |
|---|---|---|---|---|
| E2 | 115 | **128 (92.8 %)** | 128 | 3 |
| **E2G (glossary consulted)** | 113 | **122 (88.4 %)** | 124 | 3 |
| E2G against E2 (gains, losses, exact McNemar p) | 0, 2, p 0.50 | **0, 6, p 0.031** | 0, 4, p 0.125 | |

- **Correct (the citation aside) at A2:** E2G 129, against E2's 135.
- **The nonexistent-id questions** were right in both.

## How the glossary was used
- **When:** 25 consultations, one at each request to search again.
- **The words changed in all 25:** the reader always took the glossary's words over its own.
- **Recovery:** of E0's 15 first-bundle misses, a later bundle held the gold for **6** (E2: 8). At the answer level, 11 recovered (E2: 13).
- **Cost:** the consultations cost $0.74. The run came to $0.174 a question, against E2's $0.157.

## What it means
- **The glossary as tested does not help; it lowers the right answers by 6** (p 0.031), with no change in wrong claims. Under DEC-1096 (4), **it does not join the fresh-80 configuration in this form.**
- **The likely causes,** read from the counts, not from the hidden questions:
  - the prototype's lookup ranks short names (code constants, error codes) above the decisions and texts that answer a question; the prototype's own report shows DEC-1088 at rank 26 for "who may edit a closed ticket";
  - the consultation step *replaced* the reader's own words in every case, rather than adding to them. A reader that had already found good words was steered to code names.
- **What would be worth testing next** (not run; for the owner):
  - (a) the glossary offered *beside* the reader's own words (search both, or the reader keeps its words unless the glossary names an exact id or term it lacked);
  - (b) a ranking that weights decision and ticket titles and definitions above code constants;
  - (c) the glossary used for *asking* (the agent's question to another agent or the owner), which E2G did not test.

  Any of them is a new experiment on the 138, declared first.
- **What it does not say:** the glossary may still be worth having as a product tool, an index of the repository's names that agents and people can look up. E2G only says that steering the second search with this prototype's lookup made it worse.

**Basis:** question 1 (only what helps agents answer right joins the configuration).
