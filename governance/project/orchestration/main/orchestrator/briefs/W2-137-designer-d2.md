# W2-137 — the test designer's second pass: D-2, other tickets' acceptance cases that pin the cap at 16 (DAEO-5emz)

You are the independent test designer for **W2-137** (`.tickets/DAEO-5emz.md`, read its D-2 and "Built" sections). The
engineer raised `rerank.MAX_REQUEST_TEXTS` from 16 to 64 (DEC-1090 (2)). These acceptance cases of other tickets still
expect requests of at most 16 texts, and go red on W2-137's build (named by the engineer's regression run):
- `tests/acceptance/W2-32/`: `s11_pool` ×2, `s7_dec1067[fusion_search]` and `[retrieve]`, `s7_size_bound[fusion_search]`,
  `s8_phrasings[content]` and `[record]`, `s8_routing::test_the_16_text_cap_holds_with_routing_on` (and their support
  module `w2_32_pool.py` where it holds the 16);
- `tests/acceptance/W1-19/test_w1_19_semantic_index.py::test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass`
  (`RERANK_CAP`; requests of 19 and 10).

## The task
Revise each so it expects the cap in force (read it from `gov.retrieval.rerank.MAX_REQUEST_TEXTS` rather than a new
literal where the case's purpose allows), keeping what each case protects: the padded-character bound, one rerank of the
merged pool, no request over the service's bound. Lower no expectation beyond the cap's change. Each changed file's
commit carries `--trailer "Rewrite-Reason: DEC-1090 (2): the reranker's request cap raised from 16 to 64 (W2-137)"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-137-tests`, branch `w2/W2-137-tests` (integrate merged). Write only
  the files named above. You may read W2-137's built code on `w2/W2-137` (`git show w2/W2-137:src/gov/retrieval/rerank.py`):
  you are revising other tickets' tests to the new cap, not testing W2-137's own KPIs.
- Run the revised cases against W2-137's code: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-137/src` with your
  worktree's tests, through the heavy slot (`EMG-common.md`), `-m "not local_only" -k "not real and not green_here and not time_limit"`;
  all green. And against integrate's code (your own `src`): say which go red there (they pin the new cap) — expected.

## Rules
As `W2-137-designer.md`: the hidden-half rule, no GPU, no model, DEC-1080, commit on `w2/W2-137-tests` with
`--trailer "Task: DAEO-5emz" --trailer "Implements: DEC-1090" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
plus the Rewrite-Reason trailer. Return the twelve fields: each case, before and after, and both runs' counts.
