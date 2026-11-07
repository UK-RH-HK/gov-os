# W2-137 — the independent review (DAEO-5emz), one round

You are a fresh, read-only independent reviewer. Review **W2-137** (`.tickets/DAEO-5emz.md`: read it in full, with its
"designer's points settled" and "Built" sections): the shared reranker's request cap raised from 16 to 64 (DEC-1090 (2)).

## What to review
- **The branch:** `w2/W2-137` in `/home/usain/gov-os-worktrees/W2-137`, against `w2/integrate` (`git diff w2/integrate...w2/W2-137`):
  - `src/gov/retrieval/rerank.py`, `src/gov/retrieval/rerank_service.py`;
  - the engineer's unit tests `tests/unit/retrieval/test_w2_137_request_cap.py`, and the D-1 changes in
    `test_w2_112_shared_reranker.py`, `test_w2_32_whole_chunk.py`, `test_w2_32_pool.py`, `test_w2_32_routing.py`;
  - the designer's cases `tests/acceptance/W2-137/` and the D-2 revisions in `tests/acceptance/W2-32/` and
    `tests/acceptance/W1-19/` (each with its `Rewrite-Reason: DEC-1090 (2)`);
  - `docs/changes/W2-137-evidence.md`.
- **The CTO's runs:** `gov accept W2-137` 37/37. The scoped regression outside the sandbox: 943 passed, 1 failed. The one failure is `test_w1_19_embedding_policy.py::test_only_the_namespace_that_says_embedded_reaches_the_vectors`, a known parallel-run red on D-10's list, red at the base too, and it passes alone. The W2-112 socket cases: 85 passed.

## Check, against each KPI line S1 to S4 (S5 is the CTO's GPU window after the merge)
- **S1:** a 40-candidate search goes in one request when it fits the padded-character bound. The character bound still splits long texts.
- **S2:** the service's own bound is at least the cap. A request over it is refused with a named reason, never truncated.
- **S3:** the scores and order do not change with how the texts are split.
- **S4:** the memory release and its MEMORY line come for any request size.
- **The D-2 revisions:** they keep what each case protected, read the cap in force rather than lowering an expectation, and no other expectation was weakened.
- **Memory on the GPU:** a request of 40 to 64 texts within 24,000 padded characters. Is the larger request's peak bounded? (`CrossEncoder.predict` batches internally at 32.) Name any risk for S5's window.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **Write** your record at `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/w2-137.md`, the only file you write. End it with the fenced `verdict` block, `{"kpis": [{"kpi": "S1", ...}, ... "S4", {"kpi": "D-2", ...}]}`.
- **Run** nothing that writes. You may run the tests read-only through the heavy slot. No GPU. Use single simple Bash commands (DEC-1080). The hidden-half rule holds.
- **Return** the twelve fields: your verdict per line, and every finding with its two lines.
