# W2-50: W2-67's revision of the large-store and hang cases (DAEO-9nys, run 3, batch 7)

Independent test designer (MR-3), 2026-10-24, on `w2/W2-67` from `67a743335449`, on W2-69's merged scan (form 4:
each value and freed region in overlapping pieces, key blocks whole; DEC-897, DEC-909). The ticket's third KPI line:
"W2-50's large-store and hang cases run against a declared short limit" (lens I1 F-11, I1 §2.3; DEC-914 item 1).
Its failure line: "a revised case that cannot fail for its fault; an expectation lowered".

Four cases of `test_w2_50_secrets_scan_scale.py` are revised; every other case of the file is as W2-50 wrote it:

- `test_a_large_clean_store_is_decided_green`
- `test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it`
- `test_a_large_store_among_many_small_files_is_decided_by_gov_check`
- `test_a_scan_that_cannot_finish_fails_closed_and_records_nothing[hang]` (its `signal` and `exit-code` forms are
  unchanged: the declaration is made for the hang form only)

The revision is commit `8b4fcf067410` (`Rewrite-Reason: I1 F-11: its time came from the check's real limit; the
same property against a declared short limit (DEC-914)`). No name states a figure that changed, so every name is kept. `test_a_large_clean_store_is_decided_green` is kept and
revised as the others are: its retirement as a duplicate of the pool case is P-I1-7 inside P-IS-15, still undecided.

## Before: the head as merged

On `67a743335449`, by node id, `-n 4`, 1-minute load 1.6 to 2.3: **all 23 cases of the file passed**. The four cases
above took 275.0 s, 138.2 s, 275.6 s and 63.2 s. The other 19 took 0.9 to 3.7 s each (19 passed in 15.4 s). No case
is red after W2-69's change, so nothing is a finding for W2-69's owner.

The large cases take longer than I1 measured (about 170 s) because W2-69's pieces overlap: a 160 MiB store is given
to gitleaks as about 1.62 times its bytes (272 MB), read at 2 MB/s by the stand-in, once for each of the two rule
sets (2 × 136 s). The canary case stops at the first rule set's finding (136 s).

## The declared short limit

**Where the limit lives.** The check states the limit on one gitleaks run in figures of its own in `gov.secrets`
(`src/gov/secrets/__init__.py`): a base of 60 s (`_TIMEOUT_S`) plus a second for every 1,000,000 bytes given
(`_FLOOR`, DEC-853's working figure); a file of 64 MiB or more (`_LARGE`) is a large file of the pool, read and
scanned at most two at a time. No public means declares them: the environment names none, and the check's
declaration (`timeout-seconds: 900`) is the runner's limit on the whole check, not on one gitleaks run. So the
declaration is made from the test side, as the brief allows, under its three conditions.

**How it is declared** (`w2_50_scan_support.declare_short_limit`). The case writes a `sitecustomize.py` into its own
`elsewhere/short-limit/` folder; `environment()` puts that folder first on the check's `PYTHONPATH`, with this
worktree's `src/` after it (DEC-732: the code under test is unchanged). The module adds one import hook: once
`gov.secrets` has been imported, it sets two figures and nothing else, and writes a proof line (its process, each
figure as it found it and as it left it, and `_FLOOR` as it found it and left it). It then runs the interpreter's
own `sitecustomize`, so that nothing else of the process changes. `gov check`'s runner keeps `PYTHONPATH` (it puts
the project's `src/` in front), so the declaration reaches the check under both runners.

| Figure | The check's own | Declared | Why |
|---|---|---|---|
| Base of one gitleaks run (`_TIMEOUT_S`) | 60 s | **4 s** | the short limit |
| Seconds per byte given (`_FLOOR`) | 1 s per 1,000,000 bytes | unchanged | DEC-853's working figure: the property itself |
| Large file of the pool (`_LARGE`) | 64 MiB | **6,710,886 bytes** (6.4 MiB) | scaled with the store, so that the store takes the same path |
| The store (the test's) | 160 MiB | **16 MiB** | read at 2 MB/s: 8.4 s, more than twice the base |
| The stand-in's rate (the test's) | 2 MB/s | unchanged | twice the working figure, as before |

**Only figures change, never a code path.** The limit is still computed by the check as base plus bytes over the
floor; the store still goes through the large-file semaphore (64 MiB is to 160 MiB as 6.4 MiB is to 16 MiB); the
pool, the pieces, the record and the scan are the check's own. The rate stays 2 MB/s and the floor 1 MB/s, so
the expectation "a store is decided whenever gitleaks reads at 1 MB/s or faster" is checked at the same rate as
before. Nothing is lowered.

**Why the case still shows the same property.** Before: a 160 MiB store read at 2 MB/s takes 83.9 s, past the base of
60 s, so a limit that does not grow with the content's size cannot decide it. Now: a 16 MiB store read at 2 MB/s
takes 8.4 s, more than twice the declared base of 4 s (`short_limit()` asserts this premise, and that the large-file
figure lies between the small stores and the large one). The limit it is decided within is 4 s + 27.2 s (the 27.2 MB
the check gives gitleaks for it), as it was 60 s + 272 s. The hang form waits out 4 s + the small store's share
instead of 60 s + that share.

**Shown to have reached the check's process.** The stand-in `gitleaks` now also logs its parent process (one line
added to it). `assert_declared(run, declaration)`, called by every revised case for each of its runs, asserts that
every gitleaks run of the run was started by a process whose proof line shows both declared figures in force, and that
each figure replaced a larger figure of the check's own. If the check renames or drops `_TIMEOUT_S` or `_LARGE`, or
makes its own figure no larger than the declared one, the case fails and names the figure: it never passes silently
against the real limit. The fixed-limit plant below also shows it from the check's side: the limit it found on the
large store was 31.233 s, which is 4 s plus 27.233 MB at 1 MB/s.

**A public means would be better.** The declaration depends on two private names of `gov.secrets`. A declared limit in
the check's declaration or the environment, owned by the secrets check's ticket, would remove that dependence (the
return's package P-W2-67-TD7-A).

## Plants: red against the property, then green on the head

`src/` is never written and the tree is never copied. Each fault is a `usercustomize.py` in a folder of its own under
`.gov-runtime/scratch/td-7/plant/<fault>/`, put first on `PYTHONPATH` for the pytest run, so that every process of
the run imports it (the declaration is a `sitecustomize`, so both load). It loads the shared
`.gov-runtime/scratch/td-7/plant/lib/td7_plants.py`, which hooks the import of `gov.secrets` and, after the module
and the declared figures are in place, replaces one behaviour, then logs to `<fault>/ran.jsonl` each time the
planted behaviour acts. Each fault's `junit.xml` is beside it. A run:

    PYTHONPATH=<worktree>/.gov-runtime/scratch/td-7/plant/fixed-limit:<worktree>/src \
      python3 -m pytest -p no:cacheprovider -o tmp_path_retention_policy=failed -n 3 \
      --junitxml=<plant>/fixed-limit/junit.xml <node ids>

| Fault | Planted as | Cases | Red, and why | The plant's log |
|---|---|---|---|---|
| **fixed-limit**: the limit no longer grows with the content's size | `gov.secrets.subprocess.run` given `timeout=_TIMEOUT_S` alone | clean, canary, pool | all 3 failed in 8 s: `TimeoutExpired … timed out after 4 seconds` on the large store; the clean case "the check is not green", the canary "red but names no .gov-runtime/store-large.bin" (red by failure), the pool `['RED'], not GREEN` under `gov check` | 3 processes installed; the large store's limit cut from 31.233 s to 4 s, 27,232,602 bytes |
| **first-half-pieces**: a large store's later pieces are never scanned | `gov.secrets._pieces` yields the first half of each text's pieces | clean, pool | both failed: "gitleaks was not given all of .gov-runtime/store-large.bin: the word at its middle was seen under 0 of the run's 2 rule sets" | 567 of 1,135 pieces given, 16,777,216 bytes, in each case's check |
| **halves-at-middle**: a large text is cut at its middle byte, no overlap across the cut | `gov.secrets._scan` given each text over two pieces as two halves | canary | failed: "a large store with a canary: the check is green" | one cut at byte 8,388,608 of 16,777,216 |
| **hang-green**: a run that does not end within its limit is taken as clean | `subprocess.run`'s `TimeoutExpired` returned as exit code 0 | hang | failed: "gitleaks hang on a store, and the check is green" | 2 timeouts of 4.012 s taken as clean |
| **hang-records-clean**: the check fails on a hang but records the stores as clean first | `stores_with_secrets` records every store's digest, then raises | hang | failed: "after a failed run (gitleaks hang), the store was not scanned in full: a clean result was recorded from the failed run" | one record of 3 stores after `TimeoutExpired` |

**A first plant run was void**: the declaration's import hook and the plant's each asked every other finder, so each
asked the other without end (`RecursionError`), and the three cases were red for that reason, not for the fault. The
declaration's hook (and the plant's) now steps aside while it asks the others. That run is not counted. Its
`junit.xml` was overwritten by the counted run.

**The pool case and starvation.** No deterministic fault was found that reddens the pool case and not the clean case:
with the stand-in's rate made by sleeping, a full pool slows no run, and the per-run limit starts when a run starts.
Planted faults that make a store wait in the pool count against its limit (largest-last ordering with the wait
counted) would go red only when the 300 small stores take more than the base, which depends on the machine; this was
worked out from the figures, not run as a plant, because a plant that is red on one machine and green on another
shows nothing. The pool case
keeps what it asserted (the large store decided under `gov check`, scanned in full, with the small stores given), and
I1 F-11's reading, "any fault that reddens this case reddens the other", still holds for it after the revision.

## Durations on the head

| Case | Before (s) | After (s) |
|---|---|---|
| `test_a_large_clean_store_is_decided_green` | 275.0 | 28.9 (28.2 alone, load 14) |
| `test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it` | 138.2 | 14.7 |
| `test_a_large_store_among_many_small_files_is_decided_by_gov_check` | 275.6 | 47.0 |
| `test_a_scan_that_cannot_finish_fails_closed_and_records_nothing[hang]` | 63.2 | 12.8 (7.7 alone, load 14) |

Before: `-n 4`, load 1.6 to 2.3. After: `-n 4` beside the unchanged `signal` and `exit-code` forms, load 13.7 to
26.9 (the machine carried other sessions' runs). The large cases now write a 16 MiB store instead of 160 MiB.

**Margin under load.** Every gitleaks run of the revised cases, including each of the pool's 300 small stores, now
has 4 s plus its bytes' share instead of 60 s. A small gitleaks run (16 KB, default rules) took 0.62 s median and
0.70 s at most over 20 runs at a 1-minute load of 24: about five times inside the base. On a machine loaded far past
that, the pool case could fail by time, never pass wrongly.
