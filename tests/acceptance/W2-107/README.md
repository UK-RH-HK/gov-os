# W2-107 acceptance tests: gitleaks verdicts remembered by content hash

Ticket `DAEO-kiar` (W2-107), profile FULL. Written by the independent test designer (MR-3) from the ticket's KPI lines,
the approved design (`governance/project/orchestration/packages/P-SPEED-1.md` §4) and the design note of the designer's
brief, in parallel with the engineer and without reading the implementation (DEC-462, DEC-963). Decisions: DEC-966 item 4,
DEC-967, DEC-911 items 1 and 4, DEC-285, DEC-939 item 2, DEC-898.

## How the tests reach the code under test

- In-process cases import `gov.secrets` from whatever `PYTHONPATH` the run gives (DEC-732). Nothing is hard-coded.
- Every child process gets, on its `PYTHONPATH`, the folder that this run's `gov` was imported from, followed by the
  run's own `PYTHONPATH`. A child therefore runs the same code, and every case checks `gov.secrets.__file__` in the child
  against the parent's.
- Run from the ticket worktree with `PYTHONPATH=<ticket worktree>/src` and they exercise its code:

      cd <worktree> && TMPDIR=/tmp/gov-os-lead-W2-107 PYTHONPATH=<worktree>/src \
        python3 -m pytest tests/acceptance/W2-107 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

Only public interfaces are used:

- `gov.secrets.indexable(root, paths)`;
- `gov.secrets.path_holds_secret(root, path)`;
- `gov.secrets.scan_counts()`;
- the variables `GOV_SECRETS_CACHE`, `GOV_SECRETS_FULL_SCAN`, `PYTEST_CURRENT_TEST` and `HOME`;
- the cache file, read only as a file (its bytes, and whether it exists).

No test reads the implementation or names its private parts, with one exception from round 2. The reading form case
sets the module's `_FORM`, which the base documents as "the form of the record and of what a scan reads" (see
[Round 2](#round-2-the-reviews-findings)). Nothing is marked `local_only`; every case is skipped (not failed) where
gitleaks or git is not on `PATH`.

## The fixtures

- **The stand-in gitleaks** (`w2_107_support.make_engine`) is first on `PATH`. It is a small Python script that logs one
  line for each scan call (`gitleaks stdin`): the sub-command and the sha256 of the rule set it was given, never content.
  It then hands the call, unchanged, to the real gitleaks (found with `shutil.which` before any case changes `PATH`).
  - Another engine is another stand-in with other bytes, first on `PATH`.
  - In `test_a_gitleaks_whose_bytes_change_in_place_rescans_everything`, the stand-in's own bytes are rewritten in
    place between two processes.
  - While its `fail` file exists, the stand-in "cannot decide" (exit 1): on every call (`all`), or on every call after
    the first (`after-first`).
- **`per_text`** is what one clean text costs with no cache (`GOV_SECRETS_CACHE=""`): one call per rule set in force,
  2 with the kernel's `.gitleaks.toml`. Expectations are built from it and from the measured cost of the findings, not
  from a hard-coded number.
- **The cache.** Every case sets `GOV_SECRETS_CACHE` to a file in its own `tmp_path`, in a folder that exists, and sets
  `HOME` to a folder of its own. No case can reach the real `~/.cache/gov-os/`, even under a filter that ignored
  `GOV_SECRETS_CACHE`. The default-place cases run in child processes with `HOME` set to a temporary folder.
- **The planted secret** is a string of the project's canary rule. Row W2-L423's rule's keyword is also used. Both are
  joined at run time from parts: no file of this suite holds either whole (DEC-911 item 1), and gitleaks run over this
  folder finds nothing.
- **The commit exemption** uses a repository built from scratch in `tmp_path`, as `test_commit_exemption.py` and W2-71
  build theirs: fixed identity and date, and a commit id above the rule's entropy floor.
- **Child processes** run `w2_107_run.py` (not a test module). A child that has not answered in 180 s counts as hung
  and fails the case.

## KPI lines and their tests

The test files are all `test_w2_107_<name>.py`; the tables give `<name>::<case>`.

### Success

| KPI line (short) | Tests |
|---|---|
| S1: each verdict is remembered in one machine-wide cache, keyed by the content's sha256, the kind and the engine's fingerprint; a second rebuild of an unchanged tree scans nothing again | `remembered::test_files_judged_clean_once_are_not_scanned_again`, `::test_path_names_judged_clean_once_are_not_scanned_again`, `::test_a_changed_file_is_scanned_and_its_old_bytes_stay_remembered`, `::test_two_projects_with_the_same_rules_share_what_was_remembered`, `::test_a_content_verdict_and_a_path_verdict_are_kept_apart`; `default_place::test_with_no_cache_named_outside_pytest_the_cache_is_made_in_the_home_folder`; `engine_change::test_a_gitleaks_whose_bytes_change_in_place_rescans_everything` (the cache shared between processes) |
| S2: only a clean verdict is remembered; any finding, the exempt commit hash included, is scanned again every time; a secret is never answered clean | `secrets_never_remembered::test_a_file_holding_the_secret_is_dropped_and_scanned_on_every_call`, `::test_a_path_whose_name_holds_the_secret_is_judged_and_scanned_on_every_call`, `::test_a_commit_of_the_repository_after_the_rules_keyword_is_let_through_and_scanned_on_every_call`; `engine_change::test_a_scan_whose_first_rule_set_ran_and_whose_next_could_not_decide_remembers_nothing` |
| S3: any change to gitleaks or its rules forgets every remembered result | `engine_change::test_a_rule_added_to_the_project_rescans_everything_and_the_old_rules_results_are_forgotten`, `::test_another_gitleaks_first_on_path_rescans_everything_and_switching_back_rescans_again`, `::test_a_gitleaks_whose_bytes_change_in_place_rescans_everything` |
| S4: fail closed: a cache that cannot be opened, is corrupt, has the wrong form or is locked is a miss; a failed write is ignored; a scan that cannot decide still raises | `fail_closed::test_a_cache_file_of_garbage_bytes_is_a_miss_until_removed_and_is_never_replaced`, `::test_an_empty_cache_file_neither_stops_the_scan_nor_answers_wrong`, `::test_a_sqlite_file_of_another_form_is_a_miss_until_removed_and_is_never_replaced`, `::test_a_cache_held_locked_by_another_connection_is_a_miss_after_a_short_wait`, `::test_a_cache_place_that_cannot_be_written_is_a_miss_and_nothing_is_made`; `engine_change::test_a_gitleaks_that_cannot_decide_still_raises_though_the_content_was_remembered_under_another_engine`, `::test_no_gitleaks_on_path_still_raises_though_the_content_was_remembered`; `concurrency::test_several_threads_judging_the_same_files_at_once_get_the_right_verdicts`, `::test_two_processes_judging_the_same_files_at_once_get_the_right_verdicts` |
| S5: the cache holds hashes and verdicts only | `cache_contents::test_the_cache_holds_no_content_no_path_no_name_and_no_secret` |
| S6: a full scan (`GOV_SECRETS_FULL_SCAN=1`) reads nothing from the cache and refreshes it | `full_scan::test_a_full_scan_reads_nothing_from_the_cache_and_refreshes_it[1]`, `[yes]`; `::test_the_setting_empty_or_zero_is_an_ordinary_call[0]`, `[]` |
| S7: the rebuild's record gives the counts; seconds measured before and after on this repository | **Measured by the lead**: the seconds, and the record's line in `src/gov/rebuild/`, which is added at merge, outside this ticket. Testable part: `counts::test_the_counts_have_their_form_and_each_call_gives_a_fresh_dict`, `::test_the_counts_show_scanned_and_remembered_per_kind_and_agree_with_the_gitleaks_calls` |

### Failure

| KPI line | Tests |
|---|---|
| F1: a secret's content answered clean from the cache, or a finding remembered | the three in `secrets_never_remembered`; `engine_change::test_a_scan_whose_first_rule_set_ran_and_whose_next_could_not_decide_remembers_nothing` |
| F2: a changed gitleaks or rule set answered from the old results | the three S3 tests; `engine_change::test_a_gitleaks_that_cannot_decide_still_raises_though_the_content_was_remembered_under_another_engine` |
| F3: a corrupt, missing or locked cache that stops a rebuild or answers clean | the five in `fail_closed`; the two in `concurrency` |
| F4: content, a path or a secret's text written into the cache | `cache_contents::test_the_cache_holds_no_content_no_path_no_name_and_no_secret` |
| F5: the full-scan setting answered from the cache | `full_scan::test_a_full_scan_reads_nothing_from_the_cache_and_refreshes_it` (its second full call, on texts already remembered) |
| F6: no measured before and after, or a second unchanged rebuild that scans everything again | **Measured by the lead** (the seconds). Testable part: `remembered::test_files_judged_clean_once_are_not_scanned_again`, `::test_path_names_judged_clean_once_are_not_scanned_again`, `counts::test_the_counts_show_scanned_and_remembered_per_kind_and_agree_with_the_gitleaks_calls` |

### From the design note, behind the KPIs

| Design note item | Tests |
|---|---|
| 1. Nothing but the content verdict is remembered (namespace, an unreadable file, a link out of the root) | `remembered::test_only_the_content_verdict_is_remembered_namespace_reach_and_reading_are_decided_each_time` |
| 2. `GOV_SECRETS_CACHE=""` uses no cache; under pytest, with no cache named, none is used | `default_place::test_an_empty_cache_setting_uses_no_cache_at_all`, `::test_under_pytest_with_no_cache_named_no_cache_is_used` |
| 11. The verdicts, their order and the dropping are unchanged | `remembered::test_the_verdicts_and_their_order_are_those_of_a_scan_without_a_cache` |

## Red on the base code, and the guards

**Run on the base code: 33 cases; 27 fail, 6 pass. The 6 that pass are the guards.**

| Test | Red reason on the base code (as seen) |
|---|---|
| `remembered::test_files_judged_clean_once_are_not_scanned_again` | the second call starts gitleaks again for every file (6 calls, not 0) |
| `remembered::test_path_names_judged_clean_once_are_not_scanned_again` | the second call scans every name again |
| `remembered::test_a_changed_file_is_scanned_and_its_old_bytes_stay_remembered` | the unchanged files are scanned again beside the changed one |
| `remembered::test_two_projects_with_the_same_rules_share_what_was_remembered` | the other tree's identical bytes are scanned again |
| `remembered::test_a_content_verdict_and_a_path_verdict_are_kept_apart` | its premise fails: nothing is remembered |
| `remembered::test_only_the_content_verdict_is_remembered_namespace_reach_and_reading_are_decided_each_time` | the verdicts are right (the guard part), but the remembered governance file is scanned again (2 calls, not 0) |
| `secrets_never_remembered::*` (3) | on call 2 the clean neighbour is scanned again besides the finding |
| `engine_change::test_a_rule_added_…` | "the first rules again": the second pass scans everything |
| `engine_change::test_another_gitleaks_first_on_path_…` | "engine A again": the second pass scans everything |
| `engine_change::test_a_gitleaks_whose_bytes_change_in_place_…` | "the first bytes again": the second process scans everything |
| `engine_change::test_a_gitleaks_that_cannot_decide_…` | its premise fails: nothing is remembered under engine A |
| `engine_change::test_no_gitleaks_on_path_…` | its premise fails: nothing is remembered |
| `fail_closed::test_a_cache_file_of_garbage_bytes_…` | once the garbage is removed, a working cache does not answer the clean texts |
| `fail_closed::test_a_sqlite_file_of_another_form_…` | the same, once the foreign file is removed |
| `fail_closed::test_a_cache_held_locked_…` | "before the lock": no cache answers the clean texts |
| `full_scan::test_a_full_scan_reads_nothing_…` [1], [yes] | after the full scan, an ordinary call is not answered from the cache |
| `full_scan::test_the_setting_empty_or_zero_…` [0], [] | the call is not answered from the cache |
| `cache_contents::test_the_cache_holds_no_content_…` | no cache file is made, so there is nothing to read |
| `default_place::test_with_no_cache_named_outside_pytest_…` | no file at `<HOME>/.cache/gov-os/secrets-scan.sqlite` |
| `concurrency::*` (2) | the verdicts are right and nothing raises, but after the race the clean texts are not remembered |
| `counts::*` (2) | `AttributeError`: `gov.secrets` has no `scan_counts` |

**The guards** pass on the base code. Each guards a behaviour the change must keep:

- **`remembered::test_the_verdicts_and_their_order_are_those_of_a_scan_without_a_cache`.** With the cache, on its first
  and its second use, the verdicts, order, de-duplication and dropping are those of a scan without a cache (design
  note 11).
- **`engine_change::test_a_scan_whose_first_rule_set_ran_and_whose_next_could_not_decide_remembers_nothing`.** A text
  that one rule set judged and the next could not decide raises, and is scanned in full afterwards: no half verdict is
  remembered (design note 4).
- **`fail_closed::test_an_empty_cache_file_neither_stops_the_scan_nor_answers_wrong`.** An empty file at the cache's
  place stops nothing and answers nothing wrong.
- **`fail_closed::test_a_cache_place_that_cannot_be_written_is_a_miss_and_nothing_is_made`.** A read-only place stops
  nothing, and nothing is made there.
- **`default_place::test_an_empty_cache_setting_uses_no_cache_at_all`.** `GOV_SECRETS_CACHE=""` makes no file anywhere,
  and every call scans.
- **`default_place::test_under_pytest_with_no_cache_named_no_cache_is_used`.** The existing suites keep seeing every
  scan.

## What the tests assume of the code, from the design note

- **The variables are read when a call is made, not once at import.** The in-process cases set `GOV_SECRETS_CACHE` and
  `GOV_SECRETS_FULL_SCAN` between calls in one process (design note 2).
- **The rule sets enter the fingerprint on every call.** `test_a_rule_added_…` changes `.gitleaks.toml` between calls
  in one process. A fingerprint kept per process and binary alone would answer a project with other rules from the old
  results.
- **The engine's identity is the sha256 of the bytes of the gitleaks that `PATH` finds** (design note 3). Round 2
  (addendum A) adds gitleaks' version string to it, so both enter the fingerprint (see
  [Round 2](#round-2-the-reviews-findings)). Round 1's stand-ins hand `version` to the real gitleaks unchanged, so
  the round-1 cases hold as written.
  - In these cases, every stand-in hands its calls to the same real gitleaks, so the version string never changes.
  - A fingerprint of the version string alone therefore fails `test_another_gitleaks_first_on_path_…` and
    `test_a_gitleaks_whose_bytes_change_in_place_…`.
  - Engines are told apart by path within one process. The bytes are rewritten in place only between processes, since
    the design keeps the binary's digest once per process and binary.
- **`GOV_SECRETS_CACHE` always names a file in a folder that exists.** Whether the filter makes a missing folder for a
  named file is not tested; the design says so only of the default place.
- **The lock case.** The lock is held by a connection in exclusive locking mode with a write open. A pass may take at
  most 120 s longer than a pass without a cache.
- **The concurrency cases.** The cache starts absent. A write that fails under contention may be dropped (design
  note 6), so a quiet pass comes before the pass that must answer every clean text.
- **Open questions.** The empty-file case and the file of another form follow the reading in the return's package
  P-W2-107-TD-1:
  - a SQLite file of another form stays a miss until removed and is never written into;
  - whether an empty file becomes a cache is left open.

## Round 2: the review's findings

The FULL review found behaviours the round-1 cases miss. They came to the designer as behaviours, never as code
(DEC-136), with the design note's round 2 addendum (items A to D). The cases are in `test_w2_107_review_findings.py`,
written after the implementation began (DEC-491). No round-1 case was changed.

### The fixtures of round 2

- **The round-2 stand-in** (`make_standin`) logs each scan call and each `version` call, by its tag, never content. It
  can act in three ways, each set when it is made:
  - **An older engine** (`old=`): it hands the scan to the real gitleaks and drops every finding of one rule (the
    kernel's canary rule), as a gitleaks that does not know that rule would.
  - **Its version** (`version=`): a file next to it says how it answers `gitleaks version`: the real answer, a
    non-zero exit with a version on standard output (`exit-1`), no output at all (`empty`), or a string of its own.
    Changing that file never changes the stand-in's bytes or file status.
  - **A swap** (`staged=`): while a staged engine exists, at its `swap_at`-th scan call it renames that engine over
    its own place on `PATH` before it answers.
- **The shim** is a `gitleaks` whose own bytes and file status never change. It runs whichever release a setting file
  next to it names, as a version manager's shim does:
  - release one is an older engine reporting `8.0.0-w2-107-release-one`;
  - release two is the real gitleaks.

### The findings and their tests

| Finding (design note, round 2) | Tests |
|---|---|
| A. An upgrade behind a shim whose bytes stay the same forgets every verdict (the version string is in the fingerprint) | `review_findings::test_a_gitleaks_upgraded_behind_a_shim_whose_bytes_stay_the_same_forgets_every_verdict` |
| A. A version that cannot be read means no cache for that call: every text is scanned every time, nothing is remembered or written | `review_findings::test_a_gitleaks_whose_version_cannot_be_read_scans_every_text_every_time_and_remembers_nothing[exit-1]`, `[empty]` |
| A. The version is asked only when a cache is in use, at most once a process | `review_findings::test_the_version_is_asked_only_when_a_cache_is_used_and_at_most_once_a_process` (a guard) |
| C. One engine per judgement: a gitleaks replaced during a scan has nothing remembered for what it judged, under the new engine or the old | `review_findings::test_a_gitleaks_replaced_during_a_scan_has_nothing_remembered_for_that_text[the-new-engine]`, `[the-old-engine-put-back]` |
| B. A raised reading form forgets every remembered verdict | `review_findings::test_a_raised_reading_form_rescans_every_remembered_text` |
| D. A read-only cache (the file, or its folder) still answers the current engine's clean texts, writes nothing, clears nothing, and never answers another engine's rows | `review_findings::test_a_read_only_cache_still_answers_the_current_engines_clean_texts_and_writes_nothing[the-file]`, `[its-folder]` |
| D. A cache whose write lock is held elsewhere still answers | `review_findings::test_a_cache_whose_write_lock_is_held_elsewhere_still_answers_its_clean_texts` |

### Red on the base code, and the guard

**Run on the base code: 10 cases; 9 fail, 1 passes. The one that passes is the guard.** The whole folder on the base
code: 43 cases; 36 fail, 7 pass (round 1's 6 guards and this one), none skipped.

| Test | Red reason on the base code (as seen) |
|---|---|
| `…_upgraded_behind_a_shim_…` | "release one again": its premise fails, nothing is remembered (10 scan calls, not 0) |
| `…_version_cannot_be_read_…` [exit-1], [empty] | the verdicts and the scans are right, but the filter never asks gitleaks its version (0 `version` calls) |
| `…_replaced_during_a_scan_…` [the-new-engine], [the-old-engine-put-back] | the switch and the rescan after it hold, but the control fails: no clean verdict is remembered afterwards |
| `…_raised_reading_form_…` | "the form as it is, again": nothing is remembered (6 scan calls, not 0) |
| `…_read_only_cache_…` [the-file], [its-folder] | "populated, again": its premise fails, no cache answers the clean texts |
| `…_write_lock_is_held_elsewhere_…` | "populated, again": its premise fails, no cache answers the clean texts |

**The guard**, `test_the_version_is_asked_only_when_a_cache_is_used_and_at_most_once_a_process`, passes on the base
code, which never asks the version. It keeps the cost of every suite that scans:

- with `GOV_SECRETS_CACHE` empty, or under pytest with no cache named, gitleaks is never asked its version;
- with a cache, it is asked at most once in a process.

### What the round-2 cases assume of the code

- **Fresh processes.** The version is asked at most once a process for each binary, by its path and file status. So
  the shim's release is changed only between processes: every pass of the shim and swap cases is a child process.
- **The swap's timing.** The old engine renames the new one over its own place during its last scan call of the
  planted text: its `per_text`-th call, the last rule set's run. So the whole judgement is the old engine's, and the
  switch lands before the filter can compare the file after the scan. The call in which the switch lands may let the
  text through: nothing in the design asks it to scan again. Only what is remembered afterwards is tested.
- **"Nothing written".** It is tested two ways:
  - where the file can be written, by the next pass scanning the text again, and by the main cache file's bytes
    unchanged after a pass whose version cannot be read;
  - where the cache is read-only or its write lock is held, by the main cache file's bytes unchanged.
  The `-wal` and `-shm` companions are not compared: SQLite may make them for a reader.
- **The reading form is a private name.** It can be reached only through the module's `_FORM`. The test sets it on the
  `gov.secrets` the run imports, in-process, between calls, as the round-1 rule case changes `.gitleaks.toml` between
  calls. It therefore assumes the fingerprint reads `_FORM` when a call is made, not a copy taken at import. `_FORM`
  is the base's documented convention ("the form of the record and of what a scan reads"), so the test is kept. A
  move of the constant to another module or name is a dispute for the designer, not a reason to lower the case. The
  engineer's builder test covers the same behaviour from inside.
- **The read-only cases.** "Engine B" is round 1's stand-in with other bytes. On a read-only cache it can clear
  nothing, so the case shows two things:
  - B is answered no row of A's: every text is scanned;
  - A, back again, is answered as before: nothing was cleared.
- **The write-lock case.** Another connection holds `BEGIN IMMEDIATE`: the write lock, under which readers may still
  read. Round 1's lock case holds an exclusive lock with a write open, which keeps readers out too, so it stays a miss.
  A pass under the write lock may take at most 120 s longer than a pass without a cache, as in round 1.

## Not tested here

- The seconds of the secrets stage before and after (the lead's measure, KPI S7 and F6).
- The rebuild record's line (`src/gov/rebuild/`, added at merge).
- The nightly's `GOV_SECRETS_FULL_SCAN=1` line in `nightly.sh` (the orchestrator's, at merge, with `test_nightly.sh`).
- The secrets-indexing check `stores_with_secrets`, which keeps its own record and is unchanged (`tests/unit/secrets_check/`
  and W2-71 cover it).
