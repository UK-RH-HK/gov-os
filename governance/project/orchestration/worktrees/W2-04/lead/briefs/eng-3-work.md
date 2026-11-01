## The work: one red acceptance case

The build so far: run 1's `c5b771c61ada` and round 2's `d78d31f216ed` (`supplementary_batches`, a dependency counted by its front matter). The test designer's revised acceptance tests are merged (`d020738197cc`). The lead ran `gov accept DAEO-u4oz` once: KPI lines success-1 to success-6 pass; **success-7 fails, 9 passed, 1 failed.** The failing case and its message, as the lead saw them (this is all you get of the test, DEC-096):

```
FAILED tests/acceptance/W2-04/test_w2_04_batches.py::test_further_batch_is_at_most_one_batch_long
AssertionError: `further_batch` is not the ranked items from the first that was not stacked, in the batches' order:
  [('c7fdb06840f7…', 'docs/ledger/page-03.md'), ('7367772094…', 'docs/ledger/page-04.md'), (… page-05 … page-09 …),
   ('f4e199a123e3…', 'docs/ledger/page-10.md'), ('bf2155fb6b2d…', 'docs/ledger/page-11.md'), ('1db82a3e8292…', 'docs/ledger/page-12.md')]
  read after the stack: [(… page-03.md), (… page-04.md), (… page-05.md), (… page-06.md), (… page-07.md), (… page-08.md), (… page-09.md)]
  Left contains 3 more items, first extra item: ('f4e199a123e3…', 'docs/ledger/page-10.md')
```

That is: under a tight `--budget`, the packet's `further_batch` names ten items, page-03 to page-12, but the batches in `supplementary_batches` read only up to page-09; three of the items in `further_batch` were never read by any batch the context took.

1. Judge it against the specification and its addendum (S7: "`further_batch`: … the ranked items that were not stacked for lack of room, beginning with the first one that did not fit, at most one batch long"; S7a: "The batches' items taken together, in order, are the rank order: … `further_batch` begins with the first ranked item that was not stacked"). If you judge the case's expectation (that `further_batch` continues the batches' own items, in their order, and names nothing no batch read) is within the specification, change the build so it holds, and keep every other rule of S7 and S7a (at most as long as the largest `limit`, strict rank order, no stacked item in it, an empty list when nothing was left, deterministic). Think about the edge where no batch can be taken at all (no room left after the mandatory inputs) and keep it consistent with S7 and S7a; say what you chose.
2. If you judge the expectation contradicts the specification, change nothing and return a package (question, why, options, impact, reversibility, cost, recommendation, confidence). Never bend the code to a test against the specification.
3. Builder tests in `tests/unit/context/` for the change; keep them all green (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m pytest tests/unit/context -q -p no:cacheprovider -o tmp_path_retention_policy=failed`).
4. **Commit first**, then run the acceptance tests once, reading results only, **through `gov accept` only**: `cd /home/usain/gov-os-worktrees/W2-04 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m gov.cli.main accept DAEO-u4oz --json` (run it in the background with the longest timeout your Bash tool allows and an exit-code file, then wait for it with short checks; it takes a few minutes). Pass or fail per KPI line and the counts; never a test's source, assertion text or traceback; never `pytest` on `tests/acceptance/` yourself. A test you think is wrong is a package, never worked around.

Only inside the ticket's `allowed_paths`: `src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`. **Read only, held by running tickets:** W2-13 holds `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/retrieve/**` and `tests/unit/retrieval/**`; W2-92 holds `src/gov/retrieval/graph_route.py`, `code_route.py` and the route list in `src/gov/retrieval/retrieve.py`; you change none of their files. Never make a check fail open. Proportion (DEC-135): nothing beyond this case. **DEC-866:** something you touch that still enforces a superseded decision is named in your return, never fixed silently.

