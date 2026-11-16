---
type: probe
id: PR-DAEO-2bdu-s27w
task: DAEO-2bdu
status: ACTIVE
state_class: EVIDENCE
round: "S27-W (reopened 2026-11-16 by the CTO, DEC-1156 (7)): the narrow independent check (DEC-1154) of the scan keeping S27's bound of 10 texts per gitleaks process whatever the worker width"
reviewer_session: 394ccd2f-5f0b-4bc6-8300-e113e41a82da
implementer_session: "eng-19-2 2ab7dc6f-690b-4711-b18a-b18c994c87ab"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: c5d282ec09cdcf6abd8b2a020becb6da18f67b5f
decisions_applied: [DEC-1183, DEC-1178, DEC-1156, DEC-1154, DEC-1010, DEC-820, DEC-1065, DEC-1142]
---

# Probe record: W2-88 (DAEO-2bdu), round S27-W, the scan keeps S27's bound whatever the width: PASS

## The lead's judgement and runs
- **What changed.** The 11-16 nightly (no slot budget, 20 CPUs) reddened `tests/acceptance/W2-88/test_w2_88_scan_speed.py::test_s27_many_texts_are_judged_per_gitleaks_process`: 300 files over two rule sets started 40 gitleaks processes against the case's bound of 30 (DEC-1183 (2), run 9), because `_batches` sized batches by `ceil(texts / width)` with the width the CPU set. The CTO reopened W2-88 for S27-W (DEC-1156 (7), e185a8a88); the case is unchanged. A fresh engineer (eng-19-2, `2ab7dc6f-690b-4711-b18a-b18c994c87ab`, claude-opus-5-5, effort high, `launch_worker.sh` / `gov launch` under the OS sandbox, the promotion "a fail-open finding" applying) made `_batches` take the number of rule sets and split the texts into at most `max(1, min(width, N // (10 x rule sets)))` batches, spread evenly, the text and byte caps unchanged, and added `tests/unit/secrets/test_w2_88_s27_bound.py` (widths 1, 3, 20, 64; one and two rule sets): `c5d282ec09cd`. No test designer this round (the acceptance case is unchanged; the unit test is in the engineer's paths, the CTO's order).
- **Who checked.** A fresh, read-only Independent Auditor (`394ccd2f-5f0b-4bc6-8300-e113e41a82da`, claude-opus-5-5, effort high, `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-16 with `--owner-named DEC-1154` and the promotion), its brief carrying `governance/project/briefs/JUDGEMENT.md` word for word (`.gov-runtime/scratch/lead/briefs/nc-s27w.md`).
- **The verdict stands as PASS** (success-30 = S27-W, success-27 = S27), no findings.
- **The lead's verification at the head `c5d282ec09cd` (outside the sandbox):**
  - at the base `99769aa51bf7`, unconfined (20 CPUs) with no budget, the S27 case alone: red, 40 processes for 300 files (`.gov-runtime/scratch/lead/log/red-s27w.txt`); at the head, the same form (`heavy_slot.sh --held '' env -u GOV_HEAVY_THREAD_BUDGET`), the S27 case and S27's parallel case: **2 passed** (`log/green-s27w.txt`, `green-s27w.xml`);
  - the rebuild (`rebuild_slot.sh`): ok, complete, four digests (`log/rebuild-11.txt`);
  - `gov accept W2-88`: 322 passed, 1 failed; every KPI line passes (success-27: 38 passed), the one failure unmapped (`log/acc-s27w.txt`);
  - lead_verify: RED, parallel 7,648 tests, 1 failed, 0 errors, 7 skipped; serial 49 passed (`log/verify-11-c5d282e/`). The one red, in both runs, is `tests/acceptance/W2-88/test_w2_88_f5_paths.py::test_f5_a_planted_branch_with_a_change_inside_the_paths_passes` (line 49): the planted case copies the ticket and takes `src/gov/adopt/assess.py` as a path the ticket allows; the reopen narrowed `allowed_paths` to this round's three, so it is red from the ticket's edit (e185a8a88), not from this change (the real branch's F5 case passes). Routed to the CTO as a path case (DEC-1156 (7)); not part of this check.

## The auditor's return (unchanged)

task: DAEO-2bdu (W2-88), round S27-W, narrow independent check (DEC-1154)
status: DONE. The change keeps S27's bound at every width I tried, and S27's other lines still hold. No findings.
work_completed: Did the sandbox and identity checks. Read the diff, the ticket's S27 and S27-W lines, the 11-16 reopen note and DEC-1183 (2). Ran S27's acceptance files in a heavy slot and again unconfined with no budget. Ran `_batches` across 4,165 combinations of width, rule sets, N and file sizes. Ran `indexable` with a stand-in gitleaks at CPU sets of 1, 3, 20, 64 and 128. Ran the unit test against the base's `_batches`. Checked the commit's scope and trailers.
files_changed: none
evidence: the slot run (118 passed); the unconfined run (72 passed); the probes `probe_batches.py` and `probe_indexable.py`, and the unit test's red on the base, all in my TMPDIR (`/tmp/gov-launch-ylc9le05/claude-1000/aud/`)
tests: In a slot (CPUs 0-5, budget 1): `tests/acceptance/W2-88/test_w2_88_scan_speed.py`, `test_w2_88_scan_folder.py` and `tests/unit/secrets/`: 118 passed, none skipped. Unconfined with no budget (20 CPUs, `GOV_HEAVY_THREAD_BUDGET` unset): the two acceptance files plus `tests/unit/secrets/test_w2_88_s27_bound.py`: 72 passed, including the 5,000-file speed case. The exclusion filter deselected nothing in these files. The unit test against the base's `_batches` (keyword removed): 13 red.
discoveries: none blocking. See the notes below.
risks: none in scope
lessons: Wrap a pytest run in a `timeout` shorter than the Bash limit, and pipe it through a final `tail`, so a long neighbour run does not get killed with nothing to show.
proposed_decisions: none
unresolved: My wider neighbour run of `tests/unit/secrets_check/` was killed when it reached the background time limit, which I had left at the default, so I claim nothing for it. The narrow rerun of `test_w2_20_pool.py`, `test_scan_scale.py` and the W2-20 pools case gave 2 passed and 24 deselected by the required filter. The lead's `acc-s27w.txt` was still empty when I finished.
recommended_next_action: Put this check in the probe record beside the lead's `gov accept` and lead_verify results, and close the round if those are green.

# W2-88 (DAEO-2bdu): narrow check of round S27-W (the scan keeps S27's bound whatever the width, DEC-1154)
probed_commit: c5d282ec09cdcf6abd8b2a020becb6da18f67b5f
base: 99769aa51bf7

## Sandbox and identity
- **Sandbox check (a):** writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `OSError: [Errno 30] Read-only file system`, and no file was created.
- **Sandbox check (b):** `echo sandbox-trial | git hash-object -w --stdin` worked (it printed `1ae28402a109c3397a44b19239a00adfa9472eb0`, and step 0 requires it to write that unreferenced object). `git update-index --refresh` also worked, exit 0.
- **Identity:** `GOV_ROLE=independent-auditor` and `GOV_TICKET=DAEO-2bdu`. HEAD is `c5d282ec09cdcf6abd8b2a020becb6da18f67b5f`. `git status --porcelain` was empty at the start and again at the end.
- **CPUs:** `os.sched_getaffinity` gives 20 in this session and in the unconfined `--held ''` run, and 6 inside a slot.
- **Embedders:** `ps` shows no ollama or llama-server process.

## The bound at any width
**`_batches` probe.** I checked 4,165 combinations:
- widths 1, 2, 3, 6, 7, 20, 64 and 128;
- rule sets 0, 1, 2 and 3;
- N from 0 up to 36,001, including 10·R·w ± 1, values that are not multiples, 1000·w ± 1 where the 1,000-text cap binds, and 36,000;
- 3,000 random cases with mixed byte sizes, including texts of exactly the 8 MiB byte cap, one byte over it, and 9 MiB.

Result: no violation. In every case each text appears once and in order, no batch is empty, no batch is over 1,000 texts, and no batch of more than one text is over 8 MiB. With uniform sizes:
- The number of batches is exactly `max(min(w, N // 10R), ceil(N/1000))`, never fewer than 1.
- `batches × 10R ≤ N` whenever N ≥ 10R.
- Batch sizes differ by at most one.
- There are always at least two batches when the width and N allow it.

Sample counts (R=2 unless shown):

| N | width | batches | processes |
|---|---|---|---|
| 300 | 1 | 1 | 2 |
| 300 | 3 | 3 | 6 |
| 300 | 20 | 15 | 30 |
| 300 | 64 | 15 | 30 |
| 300 | 128 | 15 | 30 |
| 300 (R=1) | 20 | 20 | 20 |
| 300 (R=1) | 64 | 30 | 30 |
| 399 | 20 | 19 | 38 |
| 401 | 20 | 20 (sizes 20/21) | 40 |
| 600 | 64 | 30 | 60 |
| 19 | 20 | 1 | 2 |
| 5,000 | 128 | 128 | 256 |
| 36,000 | 20 | 36 × 1,000 | 72 |
| 36,000 | 128 | 128 | 256 |

**`indexable` probe.** Stand-in `gitleaks dir` answering clean, the template's `.gitleaks.toml` (R=2), CPU set monkeypatched, no budget, no cache:

| N | 1 CPU | 3 | 20 | 64 | 128 |
|---|---|---|---|---|---|
| 299 | 2 | 6 | 28 | 28 | 28 |
| 300 | 2 | 6 | 30 | 30 | 30 |
| 301 | 2 | 6 | 30 | 30 | 30 |
| 600 | 2 | 6 | 40 | 60 | 60 |
| 2,001 | 6 | 6 | 40 | 128 | 200 |

The figures are gitleaks processes. Every one is within one per 10 files. Each text was given to each rule set exactly once, and every clean file was kept, in the order asked.

**Acceptance cases:**
- In a slot (budget 1, 6 CPUs): 118 passed.
- Unconfined with no budget (20 CPUs), the nightly's condition: 72 passed. This includes `test_s27_many_texts_are_judged_per_gitleaks_process`, `test_s27_batches_run_in_parallel_and_never_more_than_the_budget_allows`, the per-file verdict case, the second-run case and the 5,000-file "ten times faster" case.

## The planted mistakes
- **The base's `_batches` under the head's unit test.** I copied the base's `src/` into TMPDIR and copied the unit test with the `rule_sets=` keyword removed (that keyword was the only incompatibility). It goes red in 13 cases:
  - 300 texts, R=1, width 64: 60 batches against 30 expected;
  - 300 texts, R=2, width 20: 20 against 15;
  - 300 texts, R=2, width 64: 60 against 15;
  - 600 texts, R=2, width 64: 60 against 30;
  - 7 texts or 15 texts: 3 to 15 batches against 1;
  - the uneven-spread case;
  - the 20-CPU case;
  - the `indexable` case on 20 CPUs: 40 processes, so `40 × 10 ≤ 300` fails.

  The unit test therefore tests the bound itself, not only the signature.
- **The acceptance case's red on the base** is the lead's (`red-s27w.txt`: 40 processes for 300 files). I did not re-run it.

## The caps, the order and the verdicts
- **Text cap:** `per` is always `min(_BATCH_TEXTS, …)`, so no batch is ever over 1,000 texts. Where the cap binds (for example 5,000 texts at width 3), you get 5 batches of 1,000, not 3 of 1,667. A cap remainder can leave a small last batch (2,001 at width 1 gives 1,000, 1,000 and 1), but the average still keeps the bound.
- **Byte cap:**
  - A cut forced by the byte cap closes the batch, counts it as made, and spreads the rest over the batches left (`allowed − made`, at least 1). Once `made ≥ allowed`, the rest goes into batches limited only by the two caps.
  - In 3,000 random mixed-size cases a byte cut never produced an empty batch, a batch over the text cap, or a lost or repeated text.
  - Only byte-forced cuts can take the number of batches past the bound, as the docstring says.
  - A text over the byte cap is still a batch of its own.
- **Order and verdicts:** the batches concatenate to the input order. `indexable` places verdicts by index. The per-file verdict cases and the 5,000-file case pass, both in the slot and unconfined.
- **Scan off (`rules` empty, `rule_sets=0`):** the floor becomes `10 × max(1, 0) = 10`, so the open-only path now uses at most N//10 batches (at least 1), up to the width. No gitleaks runs on that path, and the verdicts are unchanged (probed with r=0 in the `_batches` sweep).
- **Cache:** with a record, a second run on 300 files started 0 gitleaks processes (30 on the first run), with the same verdicts. A batch whose texts are all remembered starts nothing (`if given`).
- **Other callers:** `_batches` is called only from `indexable` (`src/gov/secrets/__init__.py:562`) and the new unit test. The pool width is still `_workers()`, unchanged.

## What I probed and found sound
- **The bound:** at most `N // (10R)` batches at any width from 1 to 128, for R = 1, 2 and 3.
- **Parallelism:** the width still caps the batches, and there are two or more batches wherever N ≥ 20R and the width is 2 or more. The parallel case passes with budget 3.
- **The caps:** text cap and byte cap kept; order kept; no empty, lost or repeated texts.
- **Verdicts and speed:** the one-per-file verdict match and the 5,000-file speed case are green in the slot and unconfined.
- **The unit test:** it covers widths 1, 3, 20 and 64 for R = 1 and 2, as S27-W's verify line asks, plus 128-free 5,000-text cases and the CPU-set path. It goes red on the base's logic.
- **Scope:** the commit touches only `src/gov/secrets/__init__.py` and `tests/unit/secrets/test_w2_88_s27_bound.py`, both within `allowed_paths`. It ends with one trailer paragraph: `Task: DAEO-2bdu`, `Role: engineer`, `Implements: DEC-1183, DEC-1178, DEC-954, CAP-44.f`, `Co-Authored-By`. All four `Implements:` ids are in the ticket's `sources:`. The acceptance case is unchanged.

## Findings
None.

## Notes, not findings
- **N1.** With the scan off, the open-only path now batches 10 texts per batch at least. No gitleaks runs there, and the verdicts are unchanged.
- **N2.** Texts large in bytes can push the number of batches past the bound, by design; the docstring says so. The acceptance case's files are small.
- **N3.** `Implements:` does not name DEC-1156 (the reopen's decision). Nothing requires it.
- **N4.** My wider neighbour run of `tests/unit/secrets_check/` was killed when it reached the background time limit, so I claim nothing for it. The narrow rerun of the W2-20 pool cases, `test_scan_scale.py` and `tests/acceptance/W2-20/test_w2_20_pools.py` gave 2 passed and 24 deselected by the required `-k` filter. The pool's width (`ThreadPoolExecutor(max_workers=_workers())`) is not touched by this change.
- **N5.** Step 0 (b) wrote one unreferenced loose object (`1ae28402…`) into the shared object store, as step 0 requires. The tree status is unchanged.
- **N6.** The lead's `acc-s27w.txt` was still empty when I finished. I did not wait on it.

```verdict
{"kpis": [{"kpi": "success-30", "verdict": "pass", "findings": []}, {"kpi": "success-27", "verdict": "pass", "findings": []}], "overall": "pass"}
```
