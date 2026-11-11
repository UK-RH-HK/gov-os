# Re-pin window 5: the preparer's notes (2026-11-11, night; DEC-1125 (3) (i))

For the CTO and the reviewer. The owner's text is `governance/project/orchestration/packages/ACT-REPIN-W5.md`.

## 1. The candidate and the wheel
- Candidate: `797495bdfc70`, w2/integrate on 2026-11-11 01:08:24 UTC.
  Epoch 1794359304 (the commit's time).
- Wheel sha256 `04b094fbd587869036aea6ac1e4af2f86d1254fb484d71826c66ed1bc077d7c3`, two builds from clean exports, the same
  bytes (`pin/dryrun_w5.sh 797495bdfc70 <dir>`, 2.3 s).
- The wheel is built from `src/` and `pyproject.toml` only (`[tool.setuptools.packages.find] where = ["src"]`, package data
  `gov.retrieval: retrieve_baseline.yaml`; no setup.py, setup.cfg, MANIFEST.in, readme or licence file in the export's root).
  The script stops (`STOP: ...`, nothing switched) if any of those, or such a file should one appear, differs between the
  candidate and w2/integrate at run time (three times: at the start, before the rebuild, at the quiet point), or if the main
  tree has an uncommitted change in `src/` or `pyproject.toml`. Both stops were rehearsed (log/repin-w5-rehearsal-neg-src.txt,
  -neg-uncommitted.txt).

## 2. What changed since the live pin (`pin-bcea09060ebc`, window 4)
`git diff --stat bcea09060ebc 797495bdfc70 -- src/ pyproject.toml`: 59 files, 7,219 insertions, 1,525 deletions. No change to
`pyproject.toml`. 789 commits on integrate since; the ones touching `src/` are these tickets:

| ticket | what sessions run differently | check in `repin7_checks.sh` |
|---|---|---|
| W2-20 | the resource gate (`gov resources`, `~/.gov-os/machine/gate.json`, heavy-job slots, trip-wire); every `gov launch` passes the gate; the query server's start carries the interim wrapper's caps; each tree its own rebuild lock | `gov resources --slot`; the gate reads this machine's real `gate.json` (copied to a scratch HOME) with no fault; `gov launch --gate-override`; `gov launch engineer NO-SUCH-TICKET` is refused by name |
| W2-56 | `gov launch` on the guard alone: cleaned environment, refused arguments, the reranker's one socket and log, the sandbox module, a test session's daemon folder | `gov.launch.sandbox/gate/environ/plan_check/launcher` import; the launcher sets `GOV_STORE` |
| W2-136, W2-147 | `gov plan`; `gov launch` checks a lead against the plan | `gov plan --json` answers ok (read-only, in a scratch clone) |
| W2-152 | `gov brief` | `gov brief --run` |
| W2-153 | the role template at launch (`--append-system-prompt-file`), composed subagent sources | the launcher names the flag; `portability.compose` exists |
| W2-141 | the guard refuses an engineer's search that can reach its own acceptance folder (decide side; the hook side is staged) | `BEGIN W2-141 BLOCK` in `gov.guard.reads`; the staged pair's imports resolve; g14 (below) |
| W2-145, W2-137 | no private reranker beside the shared service; the service takes every free reranker slot; the request cap 16 to 64 | `MAX_REQUEST_TEXTS == 64`, no `_started`, `RECALL_S`, `take_free_slots`, `MAX_TEXTS >= 64` |
| W2-138 | the store's commit and folder in every search result; CONTINUATION_INVALID names both commits | the search's `store.commit` and `store.root` are the store's |
| W2-150 | the `gov.util` modules (`role_paths`, `parts`, `gitrun`, `register`, `patterns`, `tickets`, `runs_root`); old names re-import | all import; the old modules (`gov.guard.reads` and the rest) still import |
| W2-96 | `gov accept` enables only breadth for its map's cases; the opt-in suites its map needs (`GOV_TESTS_OPTIN`) | the name is in the runner |
| W2-129, W2-55, W2-92 | D-6 part 2: `gov links` and the loader's change labels | `gov links --since HEAD~1` answers ok (it exits 1 when it finds something new: a notice, so the answer's `ok` is the check) |

Unchanged since window 4: the store's tables, `semantic.py`, `lexical.py`, `chunking.py`. No schema constant moved (a search of
the diff for schema versions, `CREATE TABLE`, the semantic pin and the embedder found none).

## 3. The decisions
- **Reranker.** `rerank_service.py` and `rerank_worker.py` both differ from the live pin's (W2-145, W2-137): the service must
  run from the new pin (class 3, as window 4). The script compares the running service's file with the new pin's, and
  restarts it after the switch only if they differ. **State tonight:** the running service (pid 1544290, started 01:14 by
  another helper's check clone, `/tmp/gov-os-emg-checks/clone/src/gov/retrieval/rerank_service.py`) has the candidate's own
  bytes, so part C says "no restart needed". The state in the morning may differ (a service started from the live pin; or
  none, after 12 h idle, and then the first search starts it from the new pin). The restart branch itself is not rehearsed
  (the live service is never restarted in a rehearsal; the same as window 4): it is the same code as window 4's, with the
  reason text changed.
- **Hooks (`.git/hooks/reference-transaction`, W2-116): not rewritten.** Window 4's script wrote this file whole. Since then
  ACT-OPERATOR-1 (the commit freeze, `prepared` state) and ACT-SELECT-HOOK-1 (the landing selection) added lines to it
  (live sha256 `099de326c45b`). Window 4's script run again would have **overwritten them**. Window 5's script only reads
  the hook: it must exist, parse and refresh the store through `~/.local/bin/gov` (so the new pin runs it after the
  switch). The old "remove the hook" step of the rollback is gone. The CTO should not copy window 4's part H again.
- **Store: rebuilt at the head of w2/integrate at run time, not at the candidate.** Why: records move (the CTO commits
  tonight, and window 4's hook refreshes the store after each), and the agents in the morning should get the current
  store; the code that builds it is the candidate's own either way, because the script stops unless `src/` and
  `pyproject.toml` are the same bytes at that head (and the seed tool runs the half's own `src/` through `PYTHONPATH`).
  The checks assert the store is at that head (not at the candidate) and that a search names that commit.
- **`--force` on the refresh.** With the hook live, the ready half is already at the head when the owner runs the act, and a
  plain refresh answers "fresh" in 2 s and leaves the store built by the OLD pin's code (found in run 1 of the rehearsal).
  `--force` rebuilds the spare half at the head regardless (33 s to 2 min in the rehearsal, incremental on the half's own
  store, GPU peak 5-8 GB). No schema change forces a cold rebuild.
- **The pool key.** Window 4's script stopped if `retrieval.yaml` held `pool:` (the old pin refused it). The pool has been on
  since window 4 and the live pin accepts it: the check is gone; the new pin is checked against the main tree's own
  `retrieval.yaml`.
- **`gov context`.** `gov context DAEO-sdxk --json` answers `CONTEXT_OVER_CEILING` (18,713 tokens against 6,000) under the
  live pin as well, as it does for every in-progress ticket tried (DAEO-xwro 9,288, DAEO-ouet 10,370, DAEO-8s85 6,902,
  DAEO-o5x1 7,040, DAEO-r30l 28,537, DAEO-wnnz 28,480): a documented answer (DEC-1027), not a pin fault. The check builds
  the packet with `--budget 100000` and requires the default call to answer what the old pin answers. **For the CTO, a
  record finding:** the ceiling is exceeded by every ticket sampled, so `gov context <id> --role <role>` (the briefs'
  line in `facts.yaml`) cannot build a packet at the default ceiling today; `gov brief` is the newer path (W2-152).
- **Named reds, not gates (DEC-1125 (1), DEC-1123 (3)).** The warm real-model latency (W1-19, W2-13): no p95 is measured
  here; the search is timed and printed (2.2-2.4 s with the cold CLI start), and the hook's median must be under 2 s (it is
  0.15-0.17 s). The trailers family: no trailers check runs. The checks that were W4's are all kept.

## 4. Row 88 (what this re-pin carries from W2-141's rebuild `beec1f2f8`)
1. **The four engineer near-miss cases of `drafts/g14/test_g14.py`:** expected red BY NAME while W2-141's hook is live; not
   revised in a copy (a revised copy would hide the rule). `repin7_checks.sh` section 7: with `BEGIN W2-141 BLOCK` in the
   live `role_reads.py`, test_g14 must fail exactly `Glob lists names0`, `Grep from above0`, `a search of the whole
   acceptance folder (from above)`, `grep -r from above`, and nothing else; without it, nothing may fail. The staged pair
   (`docs/changes/W2-141-hook/`, with the live `bash_writes.py`) is run the same way, so the result is the same whichever
   ACT runs first. Result with the candidate pin: live hook (old) 151 passed, 1 skipped, 0 failed; staged pair 4 failed,
   147 passed, 1 skipped, the four by name.
2. **The staged pair rehearsed with the candidate pin (review F4):** `drafts/repin-w5/rehearse_w2141.sh`, a copy of
   `drafts/w2-141-rebase/rehearse.sh` with `PIN` the candidate pin's interpreter and its base under
   `/tmp/gov-os-emg-repin5/w141` (the original writes to `~/gov-os-runs/`, which this night's rules close). Result in
   `drafts/repin-w5/w2141-rehearsal.log` (02:12 GMT, 39 min): sets_globs 573/0 and walls 331/0 before and after; replay of
   48 h, 21,919 unique calls: under DAEO-sdxk 0 changed; under DAEO-xwro 31 allow to deny, all W2-141's S1/S2, 0 deny to
   allow; latency median 133 ms. **Location artifacts:** under `/tmp` the guard treats the clone as scratch, so 9 cases
   are red before and after alike (guard4 sets W8; 6 of test_guard_fix_4: the catastrophic-rm cases, the logged
   refusals, one planted row; test_live_hook's logged-refusals replay; g14's test_w2_91_tests_today): the differential is
   the evidence (the same 9 before and after; the pair adds only the four g14 cases). The rehearsal's own count says
   "failures: 2" (guard4, before and after). The same suites pass in the main tree (part B).
3. **F1 and F3 folded:** the text is in `drafts/repin-w5/W2-141-README-fold.md` (the README is outside this helper's paths:
   the CTO applies it). F2 (the four cases named) is in the same file.
4. **D1 (a `git diff <rev>:<path> <rev>:<path>` falsely refused):** still in the candidate's `gov.guard.reads`
   (`patched()`, `src/gov/guard/reads.py:1638`, each revision word resolved as a commit). A row for the CTO: a guard ticket
   after the lift, not this re-pin (the new pin carries the live pin's behaviour).
Also in `repin7_checks.sh` 6b: every `gov` name the live hooks import (8 imports) and the staged pair's resolves in the new
pin (a missing one would refuse every tool call of every session).

## 5. Differences from window 4's script, in one list
1. New constants (candidate, epoch, sha256, OLD = `bcea09060ebc`).
2. The frozen-src rule (section 1), the registry tree's branch and clean-file preconditions, the old pin runs.
3. The store is rebuilt at the run-time head, with `--force` (section 3).
4. No pool precondition; no hook install, rewrite or removal (section 3).
5. Part B's checks: section 2 of this file; the g14 handling (section 4).
6. The registry entry names window 5 and cites DEC-1125 (3) in the commit (approved_by stays DEC-1037, the re-pin windows'
   decision, as every window's entry).
7. The restart log's reason names W2-145 and W2-137.

## 6. Open points for the reviewer
- The reranker's restart branch is not rehearsed (section 3).
- The CTO tools the script calls are not hashed in the script (`tools/guard4_check.py`, `hook_timing.py`, `heavy_slot.sh`,
  `refresh_integration_store.sh`, `seed_store.py`, `rebuild_slot.sh`, `test_guard_fix_3.py`, `tree_busy.sh`, `proc.sh`, and
  `pin/smoke_repin5.sh`): the package lists their sha256 at the rehearsal; the CTO re-checks them before the hand-over.
- `test_guard_fix_3.py` still fails 49 cases under both pins (ACT-GUARD-FIX-4's design); the check is that they are the same 49.
- The live store moves while the rehearsal runs, because the live hook refreshes it after each CTO commit. The rehearsal
  separates what only a re-pin could change (must be unchanged) from what moves with w2/integrate (shown).
- `gov launch` itself was not exercised past its refusal of an unknown ticket (a real launch starts a Claude session).
- The ACT-OPERATOR-1 freeze: if the operator agent's `act-in-progress.txt` exists when the owner runs part E, the commit
  to w2/integrate may be refused in the `prepared` state (the hook's freeze gate). Not the case tonight.
