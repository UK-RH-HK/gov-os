# Tool trials and lens H's remaining trials, 2026-10-22 (DEC-889 items 9 and 13)

**Run by:** the W2 orchestrator.
- **Script:** `.gov-runtime/scratch/orchestrator/tools/tooltrials.sh`, from 00:22 to 06:09; trial a redone at 09:26 (`tools/trial_a.sh`).
- **Where:** a fresh clone of `w2/integrate` at `4166d8d9`, rebuilt, under `~/gov-os-runs/W2-00/tooltrials/20261022-0022/`.
- **How:** every run used the owner's trial venv (`/tmp/gov-os-tooltrial`, `--system-site-packages`: pytest 9.0.3, pytest-xdist 3.8.0, pytest-timeout 2.4.0, pytest-rerunfailures 16.7, pytest-randomly 5.0.0, grimp 3.17). Each started after 5 minutes of load under 3, with no close or nightly lock. All five full runs are the close's parallel form (`-n auto`, the serial-only list deselected by the close's own plugin).
- **Logs:** `log/tooltrials/20261022-0022/` (each run's text and JUnit XML).

## Lens H's remaining trials (its own runner)
- **Planted faults: all 32 now ran.**

  | Selector | Faults detected | Mean recall (lowest) | Test time (mean; median) |
  |---|---|---|---|
  | W2-66's declared map | 32 of 32 | 0.76 (0.10) | 13.9 %; 18.2 % |
  | Declared map without `tests/unit` | 29 of 32 | — | — |
  | Static import graph | 27 of 32 | — | — |
  | Measured map, by suite | 32 of 32 | 1.00 | 50.9 % |
  | Measured map, by test | 32 of 32 | 1.00 | 28.8 % |

- **The three widest-reaching modules** (`src/gov/config/loader.py`, `src/gov/tasks/tickets.py`, `src/gov/store/loader.py`, each reaching 10 to 30 suites):
  - the declared map detects every fault planted in them;
  - its recall there is low: 0.10 for `config/loader.py:111`, 0.46 for `tasks/tickets.py`, 0.33 for `store/loader.py`.
  - So a scoped close sees the red, but only part of what would fail.
- **The mutation sample**, by module:

  | Module | Killed of run | Score | Not covered | Survivors |
  |---|---|---|---|---|
  | `checkpoint/record.py` | 35 of 38 | 92.1 % | 2 | 3 |
  | `close/ratchet.py` | 38 of 41 | 92.7 % | 2 | 3 (lines 95 and 107 are the field-rule messages, finding 19) |
  | `tasks/claims.py` | 29 of 33 | 87.9 % | — | 4 (a `sleep`, a file mode, an `os.close`) |

  Each survivor is named in `lensH-analyse_a6.txt`.

## Trial b: `--dist worksteal` against `--dist load`

| Run | Wall time | pytest time | Reds |
|---|---|---|---|
| b1, `--dist load` | 2,004 s | 1,890 s | 2 failed, 3 errors |
| b2, `--dist worksteal` | 1,824 s (**−180 s, −9 %**) | 1,716 s | 8 failed, 3 errors |

- **Worksteal also brings 6 reds that load did not.** All are tests that start a nested pytest run of their own with a 60-second limit, which under worksteal land beside the heaviest tests:
  - five of `tests/unit/close` (`test_parallel_runs` ×2, `test_run_and_record` ×2, `test_measured` ×1), whose nested run "exceeded the time limit of 60s";
  - W1-47's `test_the_builder_tests_of_the_guard_pass`, whose nested run of `tests/unit/guard` timed out.
  - These are lens H's nested reruns (P-H-5, W2-67).
- **Worksteal's own spread:** across the four worksteal runs (b2, a-cost, d1, d2) the wall time was 1,824 to 1,986 s, so its saving is real but smaller than one run's noise.
- **The 3 errors in every run** are the venv's: `tests/unit/secrets` collects as a package named `secrets` and shadows the standard library's (row W2-L373); the closes' interpreter does not hit them.

## Trial a: pytest-timeout inside a child `gov` process
- **The setup:** a one-hour sleep planted at the start of `gov doctor`'s `run()` in a clone of the trial clone, a path only a child `gov` process runs. W1-07's `doctor` envelope case ran with `--timeout 60`.
- **The limit fires in all four forms:** the `signal` and `thread` methods, each alone and under `-n 2`. Each ended in 72 to 75 s, and **no child process was left** (`subprocess.run` kills its child when the test is interrupted).
- The `thread` method ends the whole worker, which xdist replaces; `signal` fails just the test. **`signal` is the one to use.**
- (The first attempt, in the night's script, planted nothing: my planting looked for `def run(...):` and doctor's `run` has a return annotation. Its two passes test nothing and are discarded.)
- **Cost on a full run:** a worksteal run with `--timeout 900` took 1,965 s against b2's 1,824 s, inside the four worksteal runs' spread (1,824 to 1,986 s), so no measurable cost.
  - No test reached the 900-second limit.
  - Its 9 reds beyond b1 are the same nested-run class as worksteal's.

## Trial c: grimp against the declared map, on lens H's 32 planted faults

| Selector | Faults detected | Mean recall (lowest) | Test time |
|---|---|---|---|
| Declared map | 32 of 32 | 0.76 (0.10) | 13.9 % |
| grimp (test files importing the module or anything upstream of it, in process) | 27 of 32 | 0.24 (0.00) | 2.9 % |
| grimp or the declared map | 32 of 32 | 0.77 | 16.2 % |

- grimp built the `gov` graph in 0.01 s, 115 modules.
- grimp alone misses 5 faults: the tests run `gov` as a child, and in-process imports do not show it. Added to the declared map it lifts recall by 0.01, for 2.3 points more test time.
- **Verdict:** grimp is no selector here. It may still serve W2-66's test-side import following (shared helpers such as `w1_07_support`), which this trial did not measure.

## Trial d: pytest-rerunfailures and pytest-randomly, as signals
- **rerunfailures** (`--reruns 2`): 2 failed (W1-42's accepted reds), **5 reruns**. **Limit:** the run lacked `-rR`, so the five tests' ids were not kept.
- **randomly:** 3 failed. One beyond b1, the same nested-run class: `test_run_and_record::test_no_test_collected_…`, which also failed under worksteal. No order-dependence failure was seen. **Limit:** `--no-header` hid the seed, so the order cannot be replayed.
- **Both are re-run once more, with `-rR` and the seed shown,** in the next quiet window. Then `/tmp/gov-os-tooltrial` is removed and shown.

## What follows for the drafts (the review point, DEC-889 item 14)
- **Per-test limit:** pytest-timeout with `--timeout-method signal`. It works for child hangs and costs nothing measurable. The limit is set above the slowest test (lens H's top-20 list; 900 s held).
- **Worksteal:** adopt it, after W2-67 removes or bounds the nested reruns (6 tests) or W2-57 puts them in the serial run. Otherwise worksteal turns them red under load.
- **The shared core:** the declared map is safe on all 32 faults, with no widening needed. But in the three widest-reaching modules its recall is 0.10 to 0.46. The W2-66 draft proposes adding `src/gov/config/**`, `src/gov/tasks/tickets.py` and `src/gov/store/**` to the shared core, so a change there runs the full suite.
- **grimp:** not a selector; at most a helper for test-side imports.
