# W2-145 — the independent review (DAEO-2tfd), round 1

You are a fresh, read-only independent reviewer. Review **W2-145** (`.tickets/DAEO-2tfd.md`: read it in full, with its
notes and "The designer's P-1 settled"): no private reranker beside the shared service; a search the shared reranker
cannot answer stays unranked and named; the service holds every reranker GPU slot for its life (DEC-1048 (5),
DEC-1046 (1), DEC-1097 (8)). Profile FULL.

## What to review
- **The branch:** `w2/W2-145` in `/home/usain/gov-os-worktrees/W2-145`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-145`):
  - `src/gov/retrieval/rerank.py`, `rerank_worker.py`, `rerank_service.py`;
  - the engineer's unit tests `tests/unit/retrieval/test_w2_145_no_private_reranker.py` and the revised unit files
    (`test_w2_112_shared_reranker.py`, `tests/unit/semantic/test_rerank_process.py`, `test_w2_32_rerank_fusion.py`,
    `test_w2_32_whole_chunk.py`, `tests/unit/orchestration/test_gov_reranker_gpu_slot.py`);
  - the designer's cases `tests/acceptance/W2-145/` and S6's revisions of `tests/acceptance/W2-112/` and
    `tests/acceptance/W2-32/` (each commit with `Rewrite-Reason: DEC-1048 (5)`);
  - `docs/changes/W2-145-evidence.md`.
- **The CTO's runs outside the sandbox** (stand-ins only, a scratch HOME with no reranker environment, real-model
  cases excluded): `tests/acceptance/W2-145`, the W2-145 unit file, `test_w2_112_shared_reranker.py`,
  `tests/acceptance/W2-112`, `W2-32`, `W2-137`: 501 passed, 3 skipped, 0 failed. W1-19's two parallel-run reds pass
  alone. Round 2 named the connect phase's failure ("no connection … within CONNECT_S") for EAGAIN.

## Check, against S1 to S6 and the five failure lines (S7 is the CTO's after the re-pin)
- **S1:** every failure kind leaves the order given, no score, `unavailable` with the reason, the bundle unranked; no
  process but the shared service ever started by a search; no model in the calling process.
- **S2:** no private path left anywhere in `src/gov/` (search for any process start naming `rerank_worker.py`);
  `GOV_RERANK_ALLOW_CPU` read nowhere; the worker run as a program ends named before torch loads.
- **S3:** the slot-holding thread: can it ever delay an answer, deadlock with the request path, leak a lock, or hold a
  slot after the process ends (SIGTERM, a crash)? Does it change the share check, the memory release, the cap or the
  idle end?
- **S4:** the bounds (P-1: from the end of a refused start); the EAGAIN retry stays inside `CONNECT_S`; one `FALLBACK`
  line per such search, never "private"; a search that cannot write the log still searches.
- **S5, S6:** the evidence's (a), (b), (c); the revised acceptance cases keep what each protected, by the designer only.
- **Ordinary work:** would any honest search now hang, fail, or lose its ranking where today's code ranked it, other
  than by the intended "unranked and named"? A service started by older code (window 4's pin) beside this one?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree; run nothing that writes. Tests read-only (`-p no:cacheprovider`) through the
  heavy slot with `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty scratch HOME;
  Unix sockets are refused in your sandbox (the CTO's run above covers them). No GPU; never the live service, its
  socket or the Ollama servers. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words; then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full (the launcher keeps it; the CTO transcribes it): the twelve
  labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per line, every finding with its two
  lines and `scope: in|out`, and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S2" … "S6"]}`.
