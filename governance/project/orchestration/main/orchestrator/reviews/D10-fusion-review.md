**Verdict: S1-test_fusion passes.** The engineer's change computes the expected request sizes from the reranker's limits in force (`MAX_REQUEST_TEXTS` and `MAX_REQUEST_CHARS`) instead of a new pinned number. Nothing else in the case changed, and both test files are green at the branch head. I have one finding, F1, and it does not block.

**Sandbox check (step 0):**
- (a) The test write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-137` failed as it should: `OSError: [Errno 30] Read-only file system`, exit 1. `GOV_TICKET=DAEO-5emz`.
- (b) Both git commands worked: `git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args` shows only this sandbox's own shell and `ps` (pids 1–3). No ollama or llama-server process.

- **task:** D-10 red-fix item (6). Independent read-only review of the change to `tests/unit/semantic/test_fusion.py::test_only_the_first_30_fused_chunks_are_scored_and_returned` for DEC-1090 (2) (W2-137, DAEO-5emz, KPI S1).
- **status:** DONE
- **work_completed:**
  - Read the log `bc72066fa417..HEAD`: two commits.
    - `14efc5cf3c9e` is the CTO's line adding the file to `allowed_paths` in `.tickets/DAEO-5emz.md`.
    - `a13fe809d802` is the engineer's change to the test.
  - Read the diff, the whole test file, `rerank.requests` (`src/gov/retrieval/rerank.py:258-274`) and the call in `fusion.search` (`fusion.py:84`, which passes `query` unchanged).
  - Ran both test files.
- **files_changed:** none. I wrote nothing in any tree. The only writes were the git object from step 0(b) and an empty scratch HOME under the sandbox's TMPDIR.
- **evidence:**
  - Both files together: `17 passed, 11 deselected in 0.15s`.
  - `test_fusion.py -v`: both cases PASSED.
  - Each sandbox call starts a fresh empty TMPDIR, so I took no size or file count of it.
- **tests:** `tests/unit/semantic/test_fusion.py` and `tests/unit/retrieval/test_w2_137_request_cap.py`, run through `heavy_slot.sh` with `-p no:cacheprovider -o tmp_path_retention_policy=failed`, `PYTHONPATH=<tree>/src`, empty scratch HOME and `PYTHONUSERBASE=/home/usain/.local`.
  - **What was left out:** I named whole files, not folders, so I added no `-m`/`-k` exclusion.
  - **The 11 deselected:** they come from the root `tests/conftest.py`'s rule that keeps only the first row of a parametrised case unless a run opts in. Every one is a parametrised row of `test_w2_137_request_cap.py`. Neither case of `test_fusion.py` was deselected: the `-v` run shows both.
- **discoveries:**
  - With these 30 pairs of 645 characters each, the character limit allows 24,000 // 645 = 37 texts, so the 64-text cap decides and all 30 go in one request. The new expectation is `[30]`.
  - This case never reaches the character limit. The character-split behaviour is covered by `test_s1_40_long_texts_are_split_by_characters_never_by_count_alone` in `test_w2_137_request_cap.py`, which passed.
- **risks:** none in scope (see F1).
- **lessons:** none.
- **proposed_decisions:** none.
- **unresolved:** none.
- **recommended_next_action:** this item is READY by the verdict block. The CTO can take it into W2-137's close.

### Checks 1–4

**1. No expectation lowered: yes.**
- `fits = max(1, min(rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS // longest))` is the same formula as `rerank.py:270`. `expected` splits `fusion.RERANK_TOP` into groups of `fits`. There is no new literal.
- **A request over the cap:** if the code sent 30 texts while the cap in force were 16, `expected` would be `[16, 14]` and `[30]` would fail. The character limit is caught the same way.
- **A split that was not needed:** `[16, 14]` under today's cap of 64 does not equal `expected == [30]`, so it fails.
- **More than `RERANK_TOP` texts scored:** `expected` always sums to `RERANK_TOP`, and the case still asserts `RERANK_TOP == 30`. Scoring 35 gives `[35] != [30]` and fails.
- If the texts sent were of mixed lengths, the formula (which assumes one length) would not match `requests`' longest-first grouping, so the case fails closed.

**2. Everything else the case protects is unchanged: yes.** Lines 54–59 are byte-identical to before:
- the first 30 scored, in one rerank (`seen` is only filled by that one call);
- the reranker's order `NAMES[29::-1]` and `reranked is True`;
- `limit=2` giving `["chunk-29", "chunk-28"]`;
- the unranked fallback giving `NAMES[:30]` with `reranked is False`.

**3. Only that case changed: yes.**
- The diff touches the import (adds `rerank`, which the new lines need) and the comment and expectation lines in that one case.
- The other case, `test_the_scorer_reads_the_path…`, is untouched. Nothing under `src/` changed.
- The engineer's commit carries the trailers Task (DAEO-5emz), Implements (DEC-1109, DEC-1090), Role (engineer) and Co-Authored-By.
- The only other change on the branch is the CTO's `allowed_paths` line in `14efc5cf3c9e`.

**4. Both test files are green at the head: yes.** 17 passed, 11 deselected (all parametrised rows of `test_w2_137_request_cap.py`, as explained above). Both `test_fusion.py` cases passed.

### Findings

**F1: part of the expectation comes from the observed texts, not fixed by the fixture.** `longest` is computed from the lengths of the texts the scorer actually received (`seen`), not from the fixture's known size (`len("[path: notes/chunk-00.md]\n") + len(_text(...))`). If the code started sending texts of a different but uniform length, the expected split would follow that length rather than flag it.
- Ordinary work: no, because the sibling case pins the exact text sent (`seen[0][0] == "[path: …]\n" + _text("chunk-00")`), so a change in what is sent goes red there. The miss also needs uniform wrong lengths that move the split across a limit while the sibling case is ignored.
- Consequence: other. At most a weaker regression signal in one unit case; nothing fails open and no work is lost.
- scope: in. It concerns this revision. It is a row for the record, not a round.

```verdict
{"kpis": [{"kpi": "S1-test_fusion", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
