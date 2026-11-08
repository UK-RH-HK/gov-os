# Review: the fresh-80 scripts (FRESH-80-1 §2 item 19; DEC-1097 (1))

Reviewer: independent, read-only (session `ad44f5fe` subagent), 2026-11-08. The only file written outside the
scratchpad is this one. Nothing under `~/gov-os-eval/` was read, listed or opened. No live search, no GPU, no model call.

**Reviewed** (`drafts/fresh80/`, sha256 prefixes as read): `f80lib.py` 92ae85e27c7b, `preflight.py` bf55986d5a00,
`f80_check.py` c672e86ad3aa, `run_measure.sh` e32f9b8ee5cc, `fresh80_reader.py` ac9438855ee5, `fresh80_figures.py`
1df7fa031696, `fresh80_data.py` 3ebdabf6353e, `f80_e5_live.sh` 8b66d63a8522, `f80_so_measure.sh` 1b4136069038,
`f80_e4_prep.sh` 39d27abc3d5c, `f80_e4_window.sh` 2c660b0cad17, `f80_e4_replays.sh` 42e42b7ca367, `make_f80_e4.py`,
`README.md`, `tests/`.
**Read against:** FRESH-80-1 (§2 items 1-20, §3, §3.5, §4.3), the draft FRESH-80-DECLARATION, DEC-1097; the originals
`d4b/e0_run.sh`, `e2_run.py`, `e5_live.sh`, `score-once/e4_window.sh`, `e4_replays.sh`; `reviews/e4-window.md`,
`readiness-1-store.md`, `readiness-6-search-again.md`, `readiness-7-fresh80.md`; the pin's `gov/retrieval/measure.py`,
`rerank.py`, `retrieve.py`, `semantic.py`, `retrieve/command.py`; `tools/heavy_slot.sh`, `gpu_backstop.sh`.

**Judgement:** JUDGEMENT.md and AUDITOR-common.md as written. A finding blocks only if it is in scope, reachable in
ordinary work, and fails open or loses work; everything else is a row.

## Evidence gathered
- **Tests:** `pytest drafts/fresh80/tests -q -p no:cacheprovider` (TMPDIR in the scratchpad,
  `PYTHONDONTWRITEBYTECODE=1`): **52 passed** in 53 s.
- **`make_f80_e4.py --check`:** "as built". The E4 originals' pins (`E4-REVIEWED.sha256`) check clean.
- **Pinned originals:** `e2_run.py`, `e2g_run.py` and `e3_run.py` hash to `E2_SHA256`, `E2G_SHA256` and `E3_SHA256`
  (f0099fd67ef0, 35e7a4e549b2, 95718dbc6986). The declaration names the same e2 hash.
- **Bar and intervals**, computed with `f80lib`:
  - `bar`: 68/3 passes; 67/0 misses; 68/4 misses; 76 reaches the target.
  - Clopper-Pearson for 70 of 79 is 79.47-94.66 %. Both binomial tails come back at 0.0250, so the bisection is right.
  - Wilson for 70 of 79 is 79.75-93.89 %, FRESH-80-1 §4.3's example.
- **At `c00d525fd420`** (`git show`): `evaluation_families` gives exactly item 5's line (4, 3, 2 members), and
  `retrieval.yaml`'s pool equals `preflight.POOL`.
- **The clone's store is not written by searches:** `store.db` mtime is 2026-11-07 15:58:56 (E0's build), unchanged
  through E2, E3-SA and E5. Searches write only `query-vector-cache.db`, which holds text sha256s, not text. So the
  before/after sha256 rule will not trip on the run's own searches.
- **The live reranker's fallback history** (`~/.cache/gov-os/rerank.log`, kinds only): FALLBACK → `unavailable` on
  11-02 22:52-22:53 and 11-06 11:33-11:37 ("no GPU slot freed within its wait"). Those searches went on unreranked.
- `gov retrieve` was not used: the brief forbids live searches, and a search uses the live GPU reranker. Every
  answer here comes from reading the sources named above. Guard refusals: 0.

## Result
**NOT READY: one blocking finding (F1).** A retrieval answered without the reranker, or without a route, passes
silently. In the measure it makes an attempt "whole"; in the reader's later searches it counts as a good search. The
verdict would then judge a configuration other than the declared one, on the single use, with no rerun allowed. The
fix is one check in two places, plus tests. Everything else the brief asked holds (below). The rows can ride along.

## Findings

### F1 (blocking): a degraded retrieval (reranker "unavailable", or a route facet down) is accepted silently
- **Where:**
  - `f80_check.py attempt` / `control` count only the question lines, the total line and the number of kept files.
  - `f80lib.search` fails a search only on a bad exit, `ok: false` or no bundle.
  - `grep -i 'rerank|fallback|unavailable'` over the fresh-80 code finds nothing outside the E4 copies.
- **Why it happens:**
  - The pin's `rerank.default_reranker` (rerank.py 196-203) says: "the service down, in any way: this search falls
    back, never fails". The order is shared service, then a private worker (GPU slot), then `unavailable`, which keeps
    the fused order.
  - `retrieve.py` 678 reports this only as `result.rerank.by`.
  - A route that is down shows only as `result.facets.<route>.available: false`.
  - The measure faults only on exit, `ok` or an unparsed output (measure.py 357), so it exits 0.
  - `run_measure.sh` then writes DONE and COUNTS, the reader reads those bundles, and `fresh80_figures.py` prints the
    verdict under the judged condition's name.
  - A later search in the reader goes the same way: ok True, an unreranked bundle, not counted under item 17.
- **Ordinary work: yes,** because the live log shows that very fallback twice in the last week, in ordinary use, for a
  GPU slot not freed in time. The live service is shared with every agent's searches during the run: the hold stops
  commits, rebuilds and GPU windows, not other searches. W2-130 and P-SELECT-GRAPH run beside the 80 (DEC-1097 (9)).
  The control catches only an outage that already exists when it runs.
- **Consequence: loses work** (the single use is spent on an undeclared configuration, and §3.4 items 5-6 forbid a
  rerun) **and fails open** (the verdict line carries the judged condition's name). This is the brief's check (8):
  "the live reranker down … counted, not silently 'no gold'".
- **Fix (small):**
  1. In `f80_check.py`, for `attempt` and `control`, parse every kept output. Mark the attempt not whole if:
     - an output does not parse, or has no `result.evidence` list (this also catches a kept file truncated by a full
       disk);
     - its evidence is not empty and `result.rerank.by` is neither `service` nor `private`;
     - `result.facets.lexical.available` or `result.facets.semantic.available` is false.

     Exempt the empty-evidence `UNRESOLVED_IDS` bundle (command.py `_stated_gap` carries no `rerank`). Print the counts
     by `rerank.by` and by facet: counts only, never an id-category pair. A not-whole attempt then takes the §3.5 path
     already in `run_measure.sh`.
  2. In `f80lib.search`, return `ok False` with the reason ("reranker unavailable", "route unavailable") under the
     same conditions. Item 17 then counts and names the search, and the empty-bundle fallback stays as in E2.
  3. Keep `rerank.by` in each `searches` entry of a reader row, and report a count of `private` (same model and
     revision on a GPU slot: report it, do not fault it).
  4. Tests:
     - the fake gov returns `"rerank": {"by": "unavailable"}` once in an attempt: that attempt faults and attempt-2
       counts;
     - it returns the same once on a later search: the search is counted as failed.
  5. Declaration §5: add "a retrieval answered without the reranker or a route" to the measure's fault list.

### R1 (row, ride along with F1): the in-script restart skips the control
- **Where:** `run_measure.sh` loop: after a fault in attempt-1, attempt-2 starts at once with no control. On
  `--restart` the control does run again (README open item 5).
- Once F1 makes a server outage a fault, an outage still in place takes attempt-2 straight into the same outage. That
  is a second fault: STOPPED, to the owner.
- **Fix:** run the control (and the families check) before attempt-2 too. A failed control stops before `attempt-2`
  exists, so `--restart` stays available once the servers are back. This still respects §3.5: no partial figure is
  read, and the restart is taken whatever attempt-1 showed.
- **Ordinary work:** yes, after F1. **Consequence:** other (the restart is spent and the owner decides; nothing fails
  open).

### R2 (row; concurs with readiness-7 F2): item 6's declared drop cannot be reached
- `preflight.item6` returns not ok when a token now exists, so `all_ok` is false and `run_measure.sh` refuses.
  `test_nonexistent_id_now_exists` asserts rc 1.
- **Fix:** record the drop, keep it ok, and let `fresh80_figures` print "DROPPED". Fold it in now: any change after
  the pin needs another look.
- **Ordinary work:** yes. **Consequence:** other (fails closed).

### R3 (row): no lock against two runners at once
- `run_measure.sh` takes no lock. If `--restart` is started while attempt-1 is still alive (README says: stop the
  group first), two measures run and each writes `COUNTS`; the later one wins.
- `fresh80_reader.py` takes no lock either. Two readers can run the same question, and the later row replaces the
  earlier one.
- USED's noclobber already stops two first starts.
- **Fix:** `flock -n` on `$RUNS/.run.lock` in `run_measure.sh`, and a `fcntl` lock on `reader/.lock`.
- **Ordinary work:** no, because it needs the operator to skip README step 4's group stop. **Consequence:** other.

### R4 (row): E5's live part and E4's prep take "the judged run finished" from `summary.json` alone
- A brake-stopped reader writes `summary.json` too. `fresh80_data.py` checks properly (rows equal questions);
  `f80_e5_live.sh` and `f80_e4_prep.sh` do not.
- **Fix:** the same rows-equal-planned check (from `summary.json`'s `rows` and `questions_planned`).
- **Ordinary work:** no (a brake stop, then the data started before the owner's word). **Consequence:** other (data
  only; the judged folders are not touched).

### R5 (row): no free-space check before USED
- If the disk fills mid-measure, attempt-1 faults and attempt-2 faults within seconds.
- **Fix:** run `tools/disk_gate.sh` (or a `df` floor for `$RUNS` and `/tmp`) among the step-1 refusals.
- **Ordinary work:** yes (the disk gate exists because the disk has filled before). **Consequence:** other (STOPPED,
  to the owner; F1's parse check keeps a truncated kept file from counting).

### R6 (row): no timeout on `gov retrieve` or `claude` subprocesses (as in E2)
- A hang stalls one worker. The resume recovers it.
- **Ordinary work:** yes. **Consequence:** other.

### R7 (row): an exception after the reader answered leaves no row
- For example, a null `start_line` in a citation, which the schema forbids. On resume the question runs again, with a
  new answer.
- **Fix:** catch the exception in `one()` and write an error row.
- **Ordinary work:** no. **Consequence:** other.

### R8 (row): the reader does not re-check the gov link, the clone or the store around its later searches
- `run_measure.sh` does this for the measure. The reader's later searches are part of the judged run too.
- **Fix:** call `preflight.item12` at the reader's start, and record the store sha256 at its end.
- **Ordinary work:** no (the hold, and the lift comes after). **Consequence:** other.

### R9 (row): one sub-second gap with no way forward
- A machine stop between USED's write and `mkdir attempt-1` leaves both a fresh start and `--restart` refused.
- **Fix:** allow `--restart` when USED exists and no `attempt-*` exists.
- **Ordinary work:** no. **Consequence:** other (to the owner).

### R10 (row): `fresh80_figures` does not assert a denominator of 79
- The pre-flight enforces 80 files and one question apart.
- **Fix:** refuse unless `len(plan["main"]) == 79`.
- **Ordinary work:** no. **Consequence:** other.

### R11 (row): stale names
- `make_f80_e4.py`'s docstring names `test_e4_copies.py`; the test is
  `test_figures_and_data.py::test_e4_copies_as_built_with_f1_kept`.
- **Ordinary work:** no. **Consequence:** other.

**Carried, not mine:**
- readiness-7 **F1** (no check that ACT-GUARD-SETS-1 is applied) is still absent from these files. It blocks under
  that review.
- Its F6 (digest not recomputed at the run) and F10 (Python tracebacks reach `~/gov-os-runs/fresh-80/*.out`) are open
  rows.
- Both fixes change pinned files, so the pin follows both fixes.

## The brief's checks, one by one
1. **One shot: holds.**
   - Every refusal comes before anything is written.
   - USED is written with noclobber after the control and the families check, and before the 80's first search.
   - A second run is refused while USED exists.
   - `--restart` is allowed only with attempt-1 present and not DONE, no attempt-2, no COUNTS and no STOPPED.
   - Every attempt gets its own folder (`mkdir` fails when the folder exists) and its own `.n` counter.
   - A second fault, or a store change, stops everything.
   - The control fails closed (exit and 34 ± 2 on 40 lines), and so does the families line.
   - Nothing else searches the 80 before COUNTS exists: the reader needs COUNTS and DONE, the data scripts need the
     judged run.
2. **The judged figure: holds.**
   - Only the reader folder's rows go in, through E2's own `outcome(r, 2)` (by syntax tree, pinned).
   - `n = len(plan.main)` is 79: the apart question is found by category, and the drop never shrinks n.
   - A missing row counts as not right and is named.
   - A grade that never came is a wrong claim.
   - §4.3's rounding is exact in integers.
   - Data rows live under `data/<condition>` and never enter the verdict.
3. **Output: holds.**
   - `say` refuses hidden-folder lines, and only ids and counts are printed.
   - The apart question is printed without its id.
   - Every command line takes `--sets-root ~/gov-os-eval` only.
   - Rows: readiness-7 F10 (tracebacks) and R5.
4. **Resume and brakes: hold.**
   - Rows are written whole (tmp file, then rename), and a question with a row is skipped.
   - The ledger survives a crash and tolerates a half line.
   - The brake is checked at each question's start, at 2 × projection.
   - A call that returned nothing is run once more, never a third time.
   - Rows: R3 and R7.
5. **Data after the judged run: holds.**
   - Each data script refuses while the hold stands.
   - `fresh80_data` refuses until every judged row exists.
   - Their folders are separate: `data/e3` and so on, `e2g` through `RD.one` with `run=data/e2g`, E5's and E4's
     outputs under `data/`.
   - Row: R4.
6. **E4's window: holds.**
   - F1's two parts survive: cleanup's first line is `trap '' INT TERM PIPE`, and the restore runs `setsid -w` with
     signals back to default.
   - The new redaction stage runs `tee -p | sed` inside a subshell that ignores INT and TERM; both children inherit
     the ignore. `tee -p` ignores SIGPIPE, so a dead `sed` or a closed output still leaves the log written and the
     script alive.
   - The stuck path (F3) keeps the live service down on purpose, as reviewed.
7. **The measure command: holds.** It is e0_run.sh's, item for item: the pin's python, default budgets,
   `GOV_ROLE=orchestrator`, GOV_STORE and GOV_TICKET unset, the same `GOV_KEEP` wrapper, E0's clone, `heavy_slot.sh`.
   The differences are the set and folders, and the rebuild dropped on purpose (readiness-1 S7).
8. **Failure modes: F1 fails.**
   - A crash mid-reader: holds.
   - A full disk: fails closed (R5; F1's parse check covers a truncated kept file).
   - The live reranker down: **silent (F1)**.
   - A gov crash or a bad output: counted, in the measure (a fault) and in later searches (item 17).

**Classification (DEC-809):** 1 finding in scope, ordinary work yes, loses work / fails open (F1); 11 rows (R1-R11),
all other. **Recommendation:** fix F1 and readiness-7 F1, with R1 and R2 riding along. Then a delta check of those
diffs only (round 2 of at most two), then pin the files as README step 0 says.

```verdict
{"kpis": [
 {"kpi": "(1) one shot: USED before the first search, second run refused, restart per §3.5, control first and fail-closed", "verdict": "pass", "findings": [
   {"id": "R3", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "R9", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "(2) judged figure from A2 of the judged condition only, bar 68/79 and <=3 wrong, apart question apart, denominator fixed", "verdict": "pass", "findings": [
   {"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "R10", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "(3) no question text, answer or category-id pairing on stdout/logs; no hidden path on a command line", "verdict": "pass", "findings": []},
 {"kpi": "(4) resume never re-runs a finished question; brakes", "verdict": "pass", "findings": [
   {"id": "R7", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "R6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "(5) data conditions cannot touch the judged folders or figures and run only after it", "verdict": "pass", "findings": [
   {"id": "R4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "(6) E4 window keeps the F1 restore fix and restores the live reranker on every exit path", "verdict": "pass", "findings": [
   {"id": "R11", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "(7) the measure command equals E0's except the set", "verdict": "pass", "findings": [
   {"id": "R8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "(8) failure modes: crash mid-reader, disk full, live reranker down counted not silent", "verdict": "fail", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"},
   {"id": "R5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```

**Verdict: NOT READY.** Must change: F1. Do not pin until F1 and readiness-7 F1 are in and their diffs are checked.

**Evidence (scratch):** `scratchpad/f80-review` 100 MB, 25,151 inodes, pytest's temp trees only, removed at the end.

## Round 2 (the last, DEC-1010), 2026-11-08

**Read, in context** (sha256 prefixes):
- `f80lib.py` f54516b82a92;
- `preflight.py` 53c5b44aff1f;
- `f80_check.py` c0e5f9f30452;
- `run_measure.sh` 355ea3d4501e;
- `fresh80_reader.py` 5d6ee47f11a7;
- `fresh80_figures.py` e24e6e5c0679;
- `fresh80_data.py` cfdbcf54d4f8;
- `f80_e5_live.sh` c23cbb36ce4a;
- `f80_e4_prep.sh` 18e1c6c7312c;
- `hold.sh` a592c1b301a9 (new);
- the tests.

The E4 window, the replays and `f80_so_measure.sh` are unchanged; `make_f80_e4.py --check` reports "as built".

**Read against:**
- the ACT's final candidate: `drafts/sets-root-guard/`, `pretooluse.candidate.py` bd545af83198, `path-map.patch`,
  `apply.sh`, DESIGN.md §A and §B.1, REHEARSAL.md;
- the pin's `retrieve.py` (the `pool` block, `rerank`, `facets`), `semantic.search` and `command._stated_gap`;
- the live rerank log's READY line and the live service's command line.

**Tests:** 74 passed (78 s; TMPDIR in the scratchpad; 151 MB and 38,046 files and folders, removed at the end).

### The round-1 findings, as fixed
- **F1: fixed.**
  - `f80lib.degraded` judges a search degraded when:
    - the bundle is missing;
    - the lexical or semantic route is missing or unavailable;
    - a non-empty bundle has `rerank.by` other than `service`;
    - `pool.fallback` is set.
  - It exempts only the empty `UNRESOLVED_IDS` bundle. `command._stated_gap` carries no `rerank`, so the exemption is
    needed and correctly narrow.
  - Every key exists in the pin's bundle:
    - `pool.fallback` (retrieve.py 696);
    - `rerank` (678);
    - `facets.lexical` and `facets.semantic` (328; `_stated_gap`).
  - A continuation call carries `rerank.by` from the pool token, so a sound question never trips it.
  - `f80_check` parses every kept output for `attempt` and `control`. A kept file that does not parse counts as
    "no bundle", which also covers a file truncated by a full disk. It prints counts by `rerank.by` and by kind only.
  - In the reader, `L.search` returns ok False with the reason, and `rerank_by` is kept per later search, so item 17
    counts and names it.
  - Tests: `test_degraded_search_is_a_fault_then_one_restart`, `test_degraded`, `test_degraded_later_search_counted`.
- **R1: fixed.**
  - `ready()` runs before the first attempt and before the restart:
    - `check live`: the last READY line's pid runs the pin's `rerank_service.py`;
    - a probe search must come back not degraded;
    - the control, which also must have no degraded search;
    - the families check;
    - the declaration check.
  - If any fail before the restart, the run stops before `attempt-2` exists, so `--restart` stays open.
  - The live service's command line (pid 2961782) contains `pin-bcea09060ebc/.../rerank_service.py`, so the check
    matches the live service as it runs today.
- **R2: fixed.** Item 6's existing id is reported as the declared drop, not a stop.
- **R3: fixed.** `flock -n` on `.run.lock` (taken after the refusals, before anything else is written), and a
  `fcntl` lock on `reader/.lock`.
- **R4: fixed.** E5's live part and E4's prep check that rows equal planned and that there was no brake stop.
- **R5: fixed.** At least 2 GiB free under the sets root and `/tmp`.
- **R9: fixed.** `--restart` is allowed when USED stands and no attempt exists; it then runs `attempt-1`.
- **R10: fixed.** `fresh80_figures.py` refuses unless the judged questions are 79.

### Readiness-7, as fixed
- **F1: fixed.**
  - `act_applied` checks by content, and every Python tool runs through `run_tool`; `run_measure.sh`,
    `f80_e5_live.sh` and `f80_e4_prep.sh` check too. It reads the main tree's `sets_root_hidden`:
    - `root`, after `expanduser` and `realpath`, must equal the sets root;
    - `hidden` must hold both `runs/fresh-80/**` and `fixtures/evaluation/memory-verdict-2/**`;
    - `refused_roles` must hold the orchestrator;
    - the live hook must hold `def sets_root_rule(` and `sets_root_hidden`.
  - **Checked against the final candidate:** the keys `root`, `hidden` and `refused_roles` are those
    `sets_root_rule` reads (candidate line 231; DESIGN §B.1). `path-map.patch`, which `apply.sh` applies, holds
    `root: "~/gov-os-eval"`, both globs and the orchestrator. Candidate bd545af83198 holds both hook strings. **The
    check passes once the ACT is applied with `apply.sh`.**
  - The E4 window and replays carry no check of their own, but they need `f80_e4_prep.sh`'s outputs, and that script
    checks first.
- **F2: fixed** (as R2).
- **F5: fixed.** `hold.sh begin` writes only when no mark exists (noclobber); `end` moves only a mark whose first line
  starts with "FRESH-80 HOLD".
- **F6 and F12: fixed.** `check declared` requires:
  - the declaration tracked and clean against HEAD;
  - no `____` left;
  - the 64-hex digest on its "Its digest" line equal to `set_digest` now and to the pre-flight's.

  It is checked in step 1 and again in each `ready()`. The reader rechecks the digest, and the figures print it.
- **F10: fixed.** Python standard error goes to `<run folder>/<tool>.err`; the CTO sees only the error's class.

### New in this round (none blocks)
- **N1 (row): the declaration's own header holds a literal `____`.** Line 4 says "the blanks (`____`) are filled
  from the pre-flight's output". `check declared` counts it, so `run_measure.sh` refuses until that sentence is
  reworded.
  - **Fix:** reword the header when the blanks are filled, or have the check skip the header.
  - **Ordinary work:** yes. **Consequence:** other (fails closed; one more commit before the hold).
- **N2 (row): `private` now counts as degraded.**
  - In the measure it is a fault. In the reader, a later search answered by the private worker is dropped as failed,
    and the reader gets an empty bundle.
  - The private worker runs the same model and revision on a GPU slot, so this is a strictness choice, confirmed by
    the CTO.
  - It raises the chance that both attempts fault, or that a judged question loses a usable bundle. Both fail closed:
    STOPPED to the owner, or a lower figure with the failed searches named.
  - **Suggest:** the result record names the failed later searches beside the verdict, and the figure "right, with no
    failed later search" is printed beside the verdict line, as data.
  - **Ordinary work:** yes (a 30 s service timeout under load falls back to the private worker). **Consequence:** other.
- **N3 (row): `check live` reads the READY line before the probe search.**
  - If the service had exited idle, the probe would restart it, yet the check fails.
  - Before USED this is only a "fix, then start again". Before a restart, the stop says "--restart once the servers
    are back".
  - **Fix:** read READY after the probe.
  - **Ordinary work:** yes (an idle exit). **Consequence:** other (fails closed).
- **N4 (row): the README's step 0 "Set once: F=…; PY=…" does not survive between the CTO's tool calls.**
  - Each Bash call starts fresh, so every step's line needs its own assignments.
  - An empty `$F` simply fails.
  - **Ordinary work:** yes. **Consequence:** other.
- **N5 (row, the ACT's record, not these scripts): DESIGN.md §A's printed block lacks `runs/fresh-80/**`.**
  - `path-map.patch`, which `apply.sh` uses, has it.
  - If the block were pasted from DESIGN instead, `act_applied` would refuse, which fails closed.
  - **Fix:** align DESIGN §A with the patch.
  - **Ordinary work:** no (`apply.sh` is the way the ACT is applied). **Consequence:** other.

Rows R6, R7, R8 and R11 from round 1 stand as rows.

**Classification (DEC-809):** 0 findings that are in scope, ordinary work yes, and fail open or lose work; 5 new rows
(N1-N5), all fail closed or other. N1 should be fixed in the declaration before it is committed.

```verdict
{"kpis": [
 {"kpi": "R2-a F1 fixed: a degraded search is a fault in the measure and control, a counted failure in the reader", "verdict": "pass", "findings": [
   {"id": "N2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "R2-b R1, R3, R4, R5, R9, R10 fixed; one shot, restart and denominator still hold", "verdict": "pass", "findings": [
   {"id": "N3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "R2-c readiness-7 F1 (ACT by content) matches the final candidate's block and hook", "verdict": "pass", "findings": [
   {"id": "N5", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "R2-d readiness-7 F2, F5, F6, F10, F12 fixed", "verdict": "pass", "findings": [
   {"id": "N1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "R2-e nothing new fails open or loses work; tests pass (74)", "verdict": "pass", "findings": [
   {"id": "N4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```

**Verdict (round 2): READY.** The CTO may pin the files as README step 0 lists them, `hold.sh` included. The
declaration's header sentence with `____` (N1) is reworded before it is committed.
