# D-10's red-fix list, item (6): the unit case that pins reranker requests of 16 texts (DAEO-5emz)

You are an **engineer** under W2-137's ticket (`.tickets/DAEO-5emz.md`; read its KPI S1 and its "Built" section). The
owner's DEC-1109 (2) asks that D-10's red-fix list be made ready before D-10.

## The red
`tests/unit/semantic/test_fusion.py::test_only_the_first_30_fused_chunks_are_scored_and_returned` fails at integrate's
head: `assert fusion.RERANK_TOP == 30 and [len(texts) for texts in seen] == [16, 14]` gets `[30]`. W2-137 raised
`gov.retrieval.rerank.MAX_REQUEST_TEXTS` from 16 to 64 (DEC-1090 (2), merged), so the first 30 fused chunks now go to
the reranker in one request. The case's comment still cites the old cap (DEC-1067 (f)). The CTO put the file in your
ticket's paths (`14efc5cf3c9e`, D-10).

## The task
Change only the request-size expectation of that case to the cap in force: compute the expected request sizes from
`gov.retrieval.rerank.MAX_REQUEST_TEXTS` (and, if the requests can also be split by the padded-character bound, from
that bound the way `requests()` does; with these 600-character texts check which applies and say so), never a new
literal. Keep everything else the case protects: exactly the first 30 (`RERANK_TOP`) scored, one rerank of them, the
reranker's order returned, `limit=2`, and the unranked fallback. Comment the change `DEC-1090 (2)`. Lower no other
expectation; change no other case and no code under `src/`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-137-d10`, branch `w2/W2-137-d10` (from integrate at
  `bc72066fa417`, plus the CTO's ticket commit). Write only `tests/unit/semantic/test_fusion.py`.
- Run through the heavy slot (`EMG-common.md`), `PYTHONPATH=/home/usain/gov-os-worktrees/W2-137-d10/src`:
  `python3 -m pytest tests/unit/semantic/test_fusion.py tests/unit/retrieval/test_w2_137_request_cap.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (if the second file does not exist under that name, the `tests/unit/retrieval/test_w2_137*` files). All green.
  Report the counts before and after your change.

## Rules
- `EMG-common.md` holds; you do not read `tests/acceptance/W2-137/`. The hidden-half rule: never open anything under
  `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no
  model, no shared server, no installs, never the full suite.
- Commit on `w2/W2-137-d10` only, with `--trailer "Task: DAEO-5emz" --trailer "Implements: DEC-1109, DEC-1090"
  --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge,
  push, amend or rebase.
- Estimate: 10 minutes. Return the twelve fields, short: the case before and after, both runs' counts, the head commit.
