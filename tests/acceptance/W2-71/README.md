# W2-71 — The secrets check passes a real commit hash of this repository for row W2-L423's rule only: acceptance tests

Written by the independent test designer (MR-3, DEC-069) from the KPI lines of ticket `DAEO-e8f0` (W2-71, profile
FULL), the card in `docs/plan/WAVE_2_WBS.md` §2, row W2-L423 of `docs/plan/WAVE_2_LIST.md`, and DEC-911 (item 4
above all), DEC-298, DEC-347, DEC-853, DEC-290, DEC-909, DEC-897, DEC-221, DEC-462, DEC-491, DEC-866 and DEC-868.
**Written before the implementation.** The check's code was read only as it stands on `w2/integrate`, for its
public interfaces and to make the cases red on it.

**Row W2-L423's rule** is gitleaks' default rule for one code-search vendor's access token. In every file of this
suite its id and its two keywords are written only in parts and joined at run time (`w2_71_support.VENDOR`,
`PREFIX`, `RULE_ID`, built by `_joined`, which Python does not fold into one constant, so the compiled files do not
hold them whole either). Here they are "the vendor keyword" (`"source" + "graph"`) and "the prefix keyword"
(`"sgp" + "_"`). Assertion messages mask both (`support.say`), and print paths, rule ids and booleans, never a hash
or a token; the run records' `repr` (what pytest prints of a failed assertion) holds the exit code only.

**213 cases in 6 files**, a support module and a conftest:

| File | Cases | KPI | Today |
|---|---|---|---|
| `test_w2_71_exemption.py` | 24 | K1 | **19 red**, 5 premises green |
| `test_w2_71_real_tokens_still_fail.py` | 30 | K2 | guards, green |
| `test_w2_71_only_that_rule_and_match.py` | 87 | K3 (other rules, other matches, other objects) | guards, green |
| `test_w2_71_verification_cannot_run.py` | 35 | K3 (fails closed) | guards, green |
| `test_w2_71_nothing_printed_or_written.py` | 35 | K4 | **4 red**, 31 guards green |
| `test_w2_71_keywords_in_parts.py` | 2 | K5 | guards, green |

## Run

```sh
PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src \
  python3 -m pytest tests/acceptance/W2-71 -q -p no:cacheprovider -rs
```

- **The code under test (DEC-732) is this worktree's `src/`.** `PYTHONPATH` is set per command, never in settings.
  Every child process (the check, run by `sh -c` with its declared command `python3 -m gov.secrets`; the filter,
  `gov.secrets.indexable` called by `python3 -c`) is given the runner's `PYTHONPATH`, else this worktree's `src/`
  (`w2_71_support.python_path`). The lead checks it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src python3 -c "import gov; print(gov.__file__)"`, which prints
  `/home/usain/gov-os-worktrees/W2-71/src/gov/__init__.py`.
- Standard library, pytest and PyYAML only; pytest-xdist optional. Nothing is installed. No network.
- **gitleaks 8.30.1 and git on `PATH`** (`~/.local/bin`, `/usr/bin`): every case but K5's and the two gitleaks-file
  cases skips without them. Those cases are marked `local_only`.
- **Every case builds its own projects from scratch** in pytest's temporary folder: a git repository (`git init`, real
  commits with a fixed identity and date, so every object id is the same at each run) with the kernel's
  `template/.gitleaks.toml` (it extends gitleaks' defaults: two rule sets, DEC-347) and a path map whose `docs/**` is
  governance memory (the filter's indexable folder). `HOME`, `TMPDIR` and `XDG_CACHE_HOME` of every child are inside
  the sandbox; `GIT_CEILING_DIRECTORIES` stops git at the sandbox; git reads no configuration of this machine. Each
  scene is removed when its file is done. No case copies this repository or any folder of it, and none reads or
  writes this repository's `.gov-runtime/`. K5 and the gitleaks-file cases read this repository's git (merge base,
  diff names, file contents) only.
- Each file builds one scene (or a few) per xdist worker, runs the check and the filter once over all its cases, and
  each case reads its own file's verdict: the check judges every file on its own, and the filter every path.
- **Parallel load.** No case is serial-only: no case starts a daemon or loads the machine beyond a few gitleaks runs
  over small files. `tests/acceptance/serial-only.txt` is unchanged. The `git-hangs` cases wait for the
  implementation's own limit on a git call, and at most the check's declared limit (900 s).
- **Run time** today: about 40 s for the whole folder, one process.

## Facts the cases are built on (measured for this ticket)

- **The rule** (gitleaks 8.30.1's defaults, read from the binary): case-insensitive; a word boundary, then one of
  the prefix keyword with 16 hex digits or `local`, an underscore and 40 hex digits; the prefix keyword and 40 hex
  digits; or 40 hex digits alone; then a word boundary and a backtick, a quote, a space, `;`, a literal `\n` or `\r`,
  or the end; entropy 3; keywords: the vendor keyword and the prefix keyword. So a hash followed by `.`, `,` or `)` is
  no match: every case puts a space or a line's end after the value. The secret is the whole alternative (for the bare
  form, the 40 digits).
- **git 2.43**: `git cat-file -e <id>^{commit}` answers yes for a commit id in upper case, for its **39-digit and
  12-digit prefixes** (git resolves an unambiguous abbreviation), and for an annotated tag's id (it peels to the
  commit); no for 41 digits, a tree id and a blob id. So a verification that asks git without checking that the match
  is exactly 40 hex digits would widen the exemption to abbreviations.
- **gitleaks merges a project rule of a default rule's id over that rule**: the expression is the project's, the
  keywords stay the default's. The check's second rule set (the project's rules alone, DEC-347) takes it too.
- `generic-api-key` does not take a bare 40-hex value as a secret here (its entropy floor of 3.5 and its own
  stopwords, which stay in the first rule set, DEC-347's residual); `zendesk-secret-key` does (`zendesk_secret =
  "<id>"`, its secret is the id exactly), so it is the default rule of the "another rule" cases.
- **Today's check and filter stop at the first rule set that finds something**: a file whose first-rule-set finding is
  an exempt hash is never given to the second rule set. That is the red of K4's four exempt-file cases.

## KPI lines, tests and red reasons

### K1 — "A match of row W2-L423's rule … that is exactly 40 hex digits naming a commit object of this repository … is no finding … in a file under .gov-runtime/ and in a stored value, leaves the secrets-indexing check and the pre-index filter clean"

`test_w2_71_exemption.py`. A project quotes commits of its own repository after each keyword: in a log under
`.gov-runtime/scratch/` and in a SQLite store under `.gov-runtime/stores/` (one text value among two) for the check;
in a Markdown page and a SQLite file under `docs/` for the filter. **The filter's "stored value"** is a SQLite file in
an indexable path, which the filter judges by its bytes; the value is in its page.

| Test | Red today because |
|---|---|
| `premise_every_quoted_id_names_a_commit_of_the_project`; `premise_the_line_is_a_finding_of_row_w2_l423s_rule_and_of_no_other` × 2 keywords; `premise_the_every_commit_log_…`; `premise_the_worktree_quotes_commits_…` | green: premises (each id is a commit by `git cat-file -e`; each line is a finding of row W2-L423's rule alone in the first rule set and of none in the second) |
| `a_commit_hash_of_this_repository_beside_the_keyword_is_no_finding_of_the_check` × file and store × both keywords, and a log of every commit (the first, the head, a commit on another branch, after both keywords) | **red, 5**: "the check reports `<path>` … as a finding" |
| `the_check_is_clean_on_a_runtime_folder_that_holds_only_commit_hashes_of_this_repository` | **red**: the check exits 1 |
| `a_commit_hash_of_this_repository_beside_the_keyword_passes_the_filter` × the same 5 | **red, 5**: "the filter leaves out `<path>`" |
| `beside_a_real_token_the_check_names_the_token_and_not_the_commit_hash` × file, store | **red, 2**: the check also names the hash's file (the exemption is per match: the token's file is still named) |
| `beside_a_real_token_the_filter_passes_the_commit_hash_and_not_the_token` × file, store | **red, 2**: the filter leaves out the hash's file too |
| `in_a_linked_worktree_a_commit_of_its_repository_is_no_finding_of_the_check` × file, store (the project is a linked worktree of a repository built from scratch, as every ticket's worktree is; it quotes a commit of another branch and the first commit) | **red, 2**: the check names both |
| `in_a_linked_worktree_a_commit_of_its_repository_passes_the_filter` × file, store | **red, 2**: the filter leaves out both |

### K2 — "A real token of that vendor still fails: a token in each of the rule's forms … built at test time beside the keyword, is a finding of the check and of the pre-index filter"

`test_w2_71_real_tokens_still_fail.py`, in a project whose repository has real commits, so a verification runs and
answers no. Six forms, built at run time from hashed seeds: the prefix keyword and 40 hex digits; the prefix keyword,
16 hex digits, an underscore and 40; the prefix keyword, `local_` and 40; 40 hex digits naming no object of the
repository after the vendor keyword, after the prefix keyword, and in upper case.

| Test | Red today because |
|---|---|
| `premise_the_token_is_a_finding_of_row_w2_l423s_rule_and_names_no_object_here` × 6 | green: premise |
| `a_real_token_of_the_vendor_is_a_finding_of_the_check` × 6 forms × file, store | guard, green: today's check finds each |
| `a_real_token_of_the_vendor_is_left_out_by_the_filter` × 6 × file, store | guard, green |

### K3 — "Only that rule and only that match: a finding of any other rule whose match is a commit hash of this repository stays a finding, and so do a match of 39 or 41 hex digits, a shortened hash, a commit of another repository, a tree or blob id, and a match whose verification cannot run (no git, not a repository, an error, a timeout): it fails closed"

`test_w2_71_only_that_rule_and_match.py`, each case in a file and in a stored value, for the check and the filter.
Scene 1, the kernel's rules plus one project rule `w2-71-forty-hex` (a bare 40-hex value after the word `checksum`):

- a default rule whose secret is the commit hash (`zendesk-secret-key`); the project rule whose match is the commit
  hash (both rule sets find it); a project token rule whose match holds the commit hash (`gov-token-*`);
- the same hash found by row W2-L423's rule and by `zendesk-secret-key`; a text that holds an exempt hash and another
  rule's finding (`gov-token-digit`);
- the rule's three prefixed forms holding the commit hash (each match is longer than 40 digits);
- a commit of another repository built from scratch, after each keyword; a tree id and a blob id of this repository.

Scene 2: **row W2-L423's rule never matches 39 or 41 hex digits, nor a shortened hash, on today's rules** (its 40 digits
stand between word boundaries; `premise_row_w2_l423s_rule_as_gitleaks_ships_it_never_matches_the_text` shows it). So
the project's `.gitleaks.toml` rewrites the rule (same id, its keywords kept) to match 39, 41 or 12 hex digits, and the
cases show the exemption does not widen to a match of that rule that is not exactly 40 digits: a 39-digit prefix of
the commit, the commit and one more digit, one more digit and the commit, and the 12-digit hash DEC-911 item 1 writes.
git resolves the 39- and 12-digit prefixes to the commit (a premise), so a verification by git alone would say yes.

| Test | Red today because |
|---|---|
| `premise_the_text_is_a_finding_of_the_rules_the_case_names` × 12; `premise_the_quoted_ids_are_what_the_cases_say`; `premise_the_secret_of_the_default_rules_finding_is_the_commit_hash`; `premise_row_w2_l423s_rule_as_gitleaks_ships_it_never_matches_the_text` × 4; `premise_the_rewritten_rule_finds_the_text` × 4; `premise_git_resolves_the_39_and_the_12_digit_prefixes_to_the_commit` | green: premises |
| `the_check_still_finds_it` × 12 × file, store; `the_filter_still_leaves_it_out` × 12 × file, store | guards, green |
| `the_check_does_not_widen_the_exemption_to_it` × 4 × file, store; `the_filter_does_not_widen_the_exemption_to_it` × 4 × file, store | guards, green |

`test_w2_71_verification_cannot_run.py`: a commit hash the project's repository has (or had) after each keyword, in a
file and a store, for the check and the filter, where the verification cannot run:

- `no-git`: `PATH` is a folder that holds `python3` and `gitleaks` only. (The brief states "no git on `PATH`"; a check
  that ran git from a fixed path would not meet this case.)
- `not-a-repository`: the project's `.git` is moved out of it after the commit; git finds no repository at or above
  it, even without the ceiling (a premise).
- `git-fails`: a `git` first on `PATH` answers every call with exit 128, a fatal line on standard error and `commit` on
  standard output (a verification that reads the output and not the exit code would take it for a yes).
- `git-hangs`: a `git` first on `PATH` does not answer (one process that sleeps ten hours, then would say yes).

**Fails closed** means: the check ends within its declared limit (900 s) with a non-zero exit, and names the file or
names none of the case's files (it stopped undecided, as today's check does on what it cannot read); the filter ends
within the same limit and does not return the path (a filter that raises returns nothing).

| Test | Red today because |
|---|---|
| `premise_no_git_is_on_the_path_of_the_no_git_case`; `premise_the_project_without_its_git_folder_is_no_repository_even_unbounded`; `premise_the_failing_git_answers_with_an_error` | green: premises |
| `the_check_fails_closed_when_the_verification_cannot_run` × 4 environments × 4 places | guards, green: today's check never runs git and finds each (measured: exit 1, every file named, nothing on standard error, in each environment) |
| `the_filter_fails_closed_when_the_verification_cannot_run` × 4 × 4 | guards, green |

### K4 — "The matches are held in memory only: no report file is written, no match is printed, logged or recorded, and the clean-result record (DEC-853) never records a finding; every file the check scans today is still scanned with every rule set, with no allowlist added"

`test_w2_71_nothing_printed_or_written.py`. One project: clean files at three depths of the runtime folder (top,
`scratch/`, `scratch/a/b/c/`) and a clean store, each with a marker word; an exempt log and an exempt store (each with
a marker); four files and stores with findings (a token, a 40-hex id that names no commit, a token store, a store with
an exempt hash and another rule's finding); the same in `docs/` for the filter. A `gitleaks` first on `PATH` hands
every call to the real one unchanged and logs its arguments, its rule set and the marker words its input held, never
content. The check runs twice, then the filter.

| Test | Red today because |
|---|---|
| `premise_every_run_went_through_the_logging_gitleaks_and_ended`; `premise_the_check_found_the_findings_and_the_filter_left_them_out` | green: premises |
| `no_gitleaks_call_is_given_a_report_file` × 2 check runs, the filter (a report path that is not `-`, `/dev/stdout`, `/dev/stderr` or a descriptor is a file) | guard, green: today no report path is given |
| `the_temp_folder_given_to_the_check_holds_no_file_after_the_run` × 3 | guard, green |
| `the_project_holds_no_new_or_changed_file_but_the_clean_record` × 3 (every file's digest before and after) | guard, green |
| `no_match_and_no_keyword_is_printed` × 3 runs × stdout, stderr: none of the case's hashes and tokens in any case, and neither keyword (DEC-911 item 1: a close's logs under `.gov-runtime/` hold the check's output) | guard, green |
| `the_clean_record_holds_no_file_or_store_with_a_finding_and_no_match` × 2 check runs | guard, green |
| `a_finding_is_found_again_on_the_next_run` | guard, green (a finding is never reused, DEC-853) |
| `a_commit_hash_that_cannot_be_verified_is_not_recorded_clean` (no git on `PATH`) | guard, green |
| `the_check_gives_every_clean_or_exempt_file_to_both_rule_sets` × 6 (4 clean, 2 exempt) | **red, 2**: the exempt log and store are given to the first rule set only ("with the rule sets ['extended'], not both"): today the hash is a finding there, and the check stops. The 4 clean files are guards, green |
| `the_filter_gives_every_clean_or_exempt_file_to_both_rule_sets` × 5 (3 clean, 2 exempt) | **red, 2**, for the same reason; the 3 clean files are guards, green |
| `the_branch_changes_neither_gitleaks_file` (`.gitleaks.toml`, `template/.gitleaks.toml` against the merge base with `w2/integrate`; skipped without that branch) | guard, green |
| `no_gitleaks_file_shelters_a_match_by_content` × 2: no allowlist by content (regexes, stopwords, commits), no rule's own allowlist, no disabled rule, no allowlist in the template (DEC-288), neither keyword | guard, green: the root file holds two path allowlists (DEC-290) |

A short-circuit stays allowed: once a file holds a finding that is not exempt, it is a finding, and the second rule set
need not run.

### K5 — "The rule's id and keywords are written only in parts in every tracked file this ticket writes (code, tests, records) …; under .gov-runtime/, commit hashes in its records and returns are 12 digits"

`test_w2_71_keywords_in_parts.py`: every file the branch adds or changes under `src/gov/secrets/`,
`tests/unit/secrets_check/` and `tests/acceptance/W2-71/` (against the merge base with `w2/integrate`, the working tree
and untracked files included; every file of the three folders when that branch is absent) holds neither keyword whole,
in any case, in its content or its path. A premise checks that the list holds this suite's own files.

| Test | Red today because |
|---|---|
| `premise_the_list_holds_this_suites_own_files` | green: premise |
| `no_file_the_branch_writes_holds_a_keyword_of_row_w2_l423s_rule_whole` | guard, green (this suite's files included) |

The 12-digit rule for records and returns under `.gov-runtime/` binds the sessions that write them, not the code; what
the check itself writes there (the clean-result record) is tested by K4 to hold no match.

### The failure KPIs

| Failure KPI | Refused by |
|---|---|
| A real token of any rule let through | K2 (every form, both places, check and filter); K3 scene 1 (other rules, prefixed forms holding a commit) |
| A match let through that names no commit object of this repository | K2 (40 hex digits naming nothing); K3 (another repository's commit, a tree, a blob, 39, 41 and 12 digits, every verification that cannot run) |
| A match or a finding printed, logged or written to a file | K4 (report paths, the temp folder, the project's files, standard output and error, the clean record) |
| A file the check scanned before no longer scanned, or a scan that cannot finish passing as clean | K4 (both rule sets for every clean and exempt file, three depths and `scratch/`, the record never holding a finding); K3 (`git-hangs`: the check ends within its limit and fails closed) |

## Decisions of this suite

- **A hash in upper case.** gitleaks matches case-insensitively and git resolves an upper-case id to its commit, so the
  KPI's own test (`git cat-file -e`) would say yes; DEC-911 item 4's words ("exactly 40 hex digits naming a real commit
  object") hold for both cases. Neither outcome touches a failure KPI: exempting it lets no token through (the string
  is the name of a real commit of this repository), and flagging it fails closed. git writes hashes in lower case, so
  the logs that met the rule (W2-69's run 2) hold lower case. **The suite demands neither**: no case quotes a real
  commit in upper case. What it does demand: an upper-case 40-hex string that names no commit stays a finding (K2), so
  case-insensitive matching opens no gap.
- **An annotated tag's id** peels to its commit under `^{commit}`, so the KPI's test says yes for it. No case demands
  either outcome; no tag object is built.
- **The exemption is per match, not per string or per file**: the same hash found by another rule is a finding (K3),
  and a file with an exempt hash and a real finding elsewhere in the project leaves the real one named (K1).

## The earlier tests

No earlier suite needed a change for these KPI lines: `tests/acceptance/W1-15/` and `tests/acceptance/W2-69/` build
their tokens from rules and shapes this ticket does not exempt.
