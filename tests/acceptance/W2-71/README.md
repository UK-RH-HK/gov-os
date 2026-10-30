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

**304 cases in 9 files** (run 1: 213 in 6; run 2: 91 in 3, see "Run 2" below), a support module and a conftest:

| File | Cases | KPI | Red on the code before run 1 / on run 1's code |
|---|---|---|---|
| `test_w2_71_exemption.py` | 24 | K1 | **19 red**, 5 premises green / green |
| `test_w2_71_real_tokens_still_fail.py` | 30 | K2 | guards, green |
| `test_w2_71_only_that_rule_and_match.py` | 87 | K3 (other rules, other matches, other objects) | guards, green |
| `test_w2_71_verification_cannot_run.py` | 35 | K3 (fails closed) | guards, green |
| `test_w2_71_nothing_printed_or_written.py` | 35 | K4 | **4 red**, 31 guards green / green |
| `test_w2_71_keywords_in_parts.py` | 2 | K5 | guards, green |
| `test_w2_71_partial_clone.py` (run 2) | 26 | K4 (a partial clone) | — / **13 red**, 9 premises and 4 guards green |
| `test_w2_71_promisor_config.py` (run 2) | 52 | K4 (a promisor remote, wherever configured; a configuration that cannot be read) | — / **30 red**, 14 premises and 8 guards green |
| `test_w2_71_lazy_fetch_guard.py` (run 2) | 13 | K4 (the second guard), K1 (the control) | — / **2 red**, 3 premises and 8 guards green |

## Run

```sh
PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src \
  python3 -m pytest tests/acceptance/W2-71 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs
```

While the machine is held by a nightly run or a close (`NIGHTLY-RUNNING` or `CLOSE-RUNNING` in the orchestrator's
scratch folder), run one file at a time with the same options.

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

`test_w2_71_keywords_in_parts.py`: every file the ticket writes under `src/gov/secrets/`,
`tests/unit/secrets_check/` and `tests/acceptance/W2-71/` holds neither keyword whole, in any case, in its content or
its path. The ticket's files are the paths changed there by every commit reachable from HEAD whose `Task:` trailer
names DAEO-e8f0 (merges left out: they bring other tickets' work), plus the working tree's changed and untracked files;
nothing depends on `w2/integrate` or a merge base, so the list is the same on the branch and in the main tree after the
merge. When git cannot list them, every file of the three folders on disk is read. A premise checks that the list holds
this suite's own file and a file under `src/gov/secrets/`. Rewrite-Reason: the close of 2026-10-30 02:12 was refused
because the merge-base diff was empty once the ticket was merged.

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
| A match or a finding … written to a file, read as **sent off the machine** (run 2) | Run 2: a partial clone and every promisor configuration send no request to the remote during the check or the filter; the source-only commit is not fetched; in a partial clone git is asked about no object; elsewhere every object lookup carries `GIT_NO_LAZY_FETCH` |

## Run 2 — partial clones, promisor remotes and lazy fetches

Written by a fresh test designer (MR-3) for run 2 of the ticket, from KPI 4 ("the matches are held in memory only"),
the failure KPI "a match … written to a file" (read as "sent off the machine"), DEC-911 item 4 and the orchestrator's
delegated decision P1-MORNING-2026-10-29 item 4 (stricter only). **Written before run 2's implementation**; run 1's
implementation (this branch's head when written) was not read: it was only run, to show the red.

**What run 1's review found:** in a partial clone, when the check or the filter asks git whether a candidate names a
commit, git fetches an object it does not hold from the promisor remote (a lazy fetch), so the candidate, which may be
a real token, leaves the machine; and a commit present only on the remote is fetched during the check, then exempt.

**The decided behaviour the cases state:**

1. In a partial clone, no exemption, and git is asked about no object: a match of row W2-L423's rule stays a finding
   even when it names a real commit of the repository, and no fetch is made. A repository counts as a partial clone
   when the configuration git would use for it has `extensions.partialClone`, any remote with `promisor` true (git's
   spellings of a boolean), or any remote with a `partialclonefilter`; a configuration that cannot be read counts as
   one (fail closed).
2. The second guard, never the only one: every git process the check or the filter starts to look up objects runs
   with `GIT_NO_LAZY_FETCH` true in its environment; a process that only reads configuration need not.
3. Unchanged: in a full clone with an ordinary remote, a real commit's hash beside a keyword stays exempt, and run 1's
   213 cases still hold (none was changed).

### Facts the run-2 cases are built on (measured on this machine)

- **A partial clone** is built at test time: a bare source built from scratch (`make_source`: a committed project
  pushed to `git init --bare`, with `uploadpack.allowFilter` and `uploadpack.allowAnySHA1InWant`), cloned with
  `git clone --filter=blob:none file://<source>` (a plain path would ignore the filter). git 2.43 writes
  `remote.origin.promisor = true` and `remote.origin.partialclonefilter = blob:none` (and format version 1), **not**
  `extensions.partialClone`; a premise checks the clone is partial (those keys, an old blob missing from its store).
- **git lazy-fetches a missing id in every form the decision names**, measured with a plain `git cat-file -e`: a real
  partial clone; a full clone with only `promisor` (`[Remote "origin"] Promisor = yes`); only a `partialclonefilter`;
  only `extensions.partialClone` (format version 1, and also 0); `promisor = 1` through `include.path`; `promisor =
  true` in the user's global file only. Each scene's control shows it.
- **This machine's git (2.43.0 as packaged) honours `GIT_NO_LAZY_FETCH=1`**: with it, a lookup of a missing id in the
  partial clone prints "lazy fetching disabled" and makes no request (the security fixes of git 2.43.4 appear
  backported). The brief's premise ("2.43.0 ignores that variable") does not hold here. The cases do not depend on it:
  the partial-clone and promisor cases state item 1 (no exemption, no request, and in the partial clone no object
  lookup at all), which no setting of the variable meets alone.
- **A configuration that cannot be read:** the repository's `.git/config` at mode 000, a malformed `.git/config`
  (`[broken`), a `.git/config` that is a folder, and an `include.path` naming an unreadable file all make every git
  command fail (`git config --list` and `git cat-file` both exit 128). So run 1's verification fails and fails
  closed: those cases are **guards, green today**. **A form where git still reads the object store but part of the
  configuration cannot be read was found at one level only:** the user's global `.gitconfig` at mode 000 is skipped by
  git without a word (`git config --list` exits 0, `git cat-file` reads the commit). git then does not use what that
  file says either, so a promisor named there is not a promisor to git and no lazy fetch can follow from it. Whether
  that file "cannot be read" in the decision's sense is not settled: no case demands either outcome (returned to the
  lead as a package).

### How "no fetch" is proved, and how the counter is shown to count

Each clone's remote has a logging `uploadpack` program (`remote.origin.uploadpack`, `upload_pack_counter`): a shell
script that writes one line (`request`, never an argument or an id) to its log, then runs the real `git upload-pack`.
Every fetch over `file://`, lazy or not, starts it once. The counts are taken around the check's run and the filter's
run only. **Controls**, after the runs, in each scene's own environment:

- the partial clone: the test's own `git cat-file -e <an old blob the filter left out>` makes at least one request and
  the blob lands in the clone (no run asks about that blob);
- each promisor scene: the test's own `git cat-file -e <an id no run quotes>^{commit}` makes at least one request;
- the full clone: the test's own `git fetch origin` makes at least one request.

Measured on run 1's code: the partial clone's check run 3 requests, its filter run 2; each promisor scene's check
and filter 1 each; every control 1 or more; the full clone 0.

Object presence is read by enumerating the store (`git cat-file --batch-all-objects --batch-check=%(objectname)`,
`local_objects`), which names no object and so asks no remote.

### The second guard: how an object lookup is told from a configuration read

A recording `git` first on `PATH` (`recording_git`) records, per call, its arguments (hex runs of 16 digits or more
masked), whether a 40-hex string stood in its arguments or its standard input (a boolean), and the value of
`GIT_NO_LAZY_FETCH`; it then runs the real git with the same arguments, environment and input (input passed through
as it comes, so a long-running `--batch` call works; output untouched). The rule (`looks_up_objects`), loose on
purpose:

- a `git config` call is a configuration read, never a lookup;
- any other call is a lookup when a 40-hex string stands in its arguments or its input (a candidate is asked about),
  or when its command is one of git's object readers: `cat-file`, `rev-list`, `show`, `log`, `merge-base`,
  `name-rev`, `describe`, `ls-tree`, `fsck`, or `rev-parse --verify`;
- anything else is free (`rev-parse` with options only, `ls-files`, `status`, `--version`).

"Carries it" means `GIT_NO_LAZY_FETCH` is `1` or another of git's spellings of true. git's own child processes (the
fetch a lazy fetch starts) run from git's exec path, not `PATH`, so they are not recorded. The cases expect the check
to find git on `PATH`, as run 1's `no-git` and `git-fails` cases already do. A premise runs the recorder on four known
calls and checks its classification and that its log holds no whole hash.

### KPI 4 — "The matches are held in memory only" (run 2)

`test_w2_71_partial_clone.py`: one partial clone quoting, after each keyword, in a log under `.gov-runtime/scratch/`
(the check) and a page under `docs/` (the filter): its own head commit (`own-commit`), 40 random hex digits
(`random`), and a commit made in the source after the clone (`source-only`). The check and the filter run through a
recording git.

| Test | Red on run 1's code because |
|---|---|
| `premise_the_clone_is_a_partial_clone_of_the_source`; `premise_the_source_holds_the_source_only_commit_and_not_the_random_id`; `premise_the_line_is_a_finding_of_row_w2_l423s_rule_and_of_no_other` × 6; `premise_the_counter_sees_a_lazy_fetch_in_the_clone` | green: premises and the control |
| `in_a_partial_clone_the_match_stays_a_finding_of_the_check` × own-commit, source-only × 2 keywords | **red, 4**: "the check passes `<path>` … as clean" (it exempts the own commit; it fetches the source-only commit, then exempts it) |
| the same × random × 2 keywords | guard, green: the fetch fails and the id stays a finding |
| `in_a_partial_clone_the_match_is_left_out_by_the_filter` × own-commit, source-only × 2 | **red, 4**: "the filter lets `<path>` through" |
| the same × random × 2 | guard, green |
| `in_a_partial_clone_the_check_sends_nothing_to_the_remote` | **red**: "reached the promisor remote 3 times" |
| `in_a_partial_clone_the_filter_sends_nothing_to_the_remote` | **red**: "reached the promisor remote 2 times" |
| `the_commit_only_the_remote_has_is_not_fetched_into_the_clone` | **red**: the commit is in the clone's store after the runs (3 objects added) |
| `in_a_partial_clone_the_check_asks_git_about_no_object`; `…_the_filter_asks_git_about_no_object` | **red, 2**: "asked git about objects, 6 calls: `cat-file` …" |

`test_w2_71_promisor_config.py`: seven full clones, each with one setting (module docstring): `promisor-only`
(`[Remote "origin"] Promisor = yes`: a mixed-case section and key, `yes` for true), `filter-only`, `extension-only`,
`global-promisor` (a temporary `HOME` with a `.gitconfig`, `XDG_CONFIG_HOME` an empty folder, `GIT_CONFIG_GLOBAL`
unset), `included-promisor` (`promisor = 1` through `include.path`), `unreadable-config` (mode 000 during the runs),
`malformed-config`. Each quotes its own head commit after each keyword, and a random id after the vendor keyword (a
lookup of it reaches the remote on code that asks git).

| Test | Red on run 1's code because |
|---|---|
| `premise_the_scene_is_configured_as_said` × 5; `premise_the_global_setting_is_read_only_through_the_users_file`; `premise_the_counter_sees_a_lazy_fetch_in_the_scene` × 5; `premise_git_cannot_read_the_configuration` × 2 (not root; `git config --list` and `git cat-file` fail); `premise_the_own_commit_lines_are_findings_of_row_w2_l423s_rule` | green: premises and controls |
| `with_a_promisor_remote_its_own_commit_stays_a_finding_of_the_check` × 5 scenes × 2 keywords | **red, 10**: "`<scene>`: the check passes `<path>` … as clean" |
| `with_a_promisor_remote_its_own_commit_is_left_out_by_the_filter` × 5 × 2 | **red, 10**: "the filter lets `<path>` through" |
| `with_a_promisor_remote_the_check_sends_nothing_to_the_remote` × 5 | **red, 5**: "reached the remote 1 times" |
| `with_a_promisor_remote_the_filter_sends_nothing_to_the_remote` × 5 | **red, 5**: "reached the remote 1 times" |
| `with_a_configuration_that_cannot_be_read_its_own_commit_stays_a_finding_of_the_check` × 2 scenes × 2 keywords (fails closed: a non-zero exit naming the file, or naming none of the case's files) | guard, green: git cannot read the configuration, so run 1's verification fails closed |
| `with_a_configuration_that_cannot_be_read_its_own_commit_is_left_out_by_the_filter` × 2 × 2 | guard, green, for the same reason |

`test_w2_71_lazy_fetch_guard.py`:

| Test | Red on run 1's code because |
|---|---|
| `premise_the_control_clone_is_a_full_clone_with_an_ordinary_remote`; `premise_the_counter_sees_a_fetch_in_the_full_clone`; `premise_the_recording_git_records_as_said` | green: premises and the control |
| **The control (item 3):** `in_a_full_clone_a_commit_of_its_own_history_is_still_no_finding_of_the_check` × 2 keywords; `…_still_passes_the_filter` × 2; `in_a_full_clone_the_check_fetches_nothing`; `in_a_full_clone_the_filter_fetches_nothing` | guards, green: run 1 exempts the commit, judges the random id a finding, and fetches nothing |
| `through_the_recording_git_the_check_still_exempts_the_commit`; `…_the_filter_still_passes_the_commit` | guards, green: the recorder changes nothing |
| `every_git_call_of_the_check_that_looks_up_objects_carries_git_no_lazy_fetch`; `…_of_the_filter_…` (at least one call recorded, at least one lookup, every lookup carrying the variable) | **red, 2**: "2 git calls recorded, 2 look up objects, 2 of them without `GIT_NO_LAZY_FETCH` set to true: `cat-file`, `cat-file`" |

### Run 2: how the tests run this worktree's `src/`, and load

- The check and the filter run as in run 1 (`run_check`, `run_filter`), with the runner's `PYTHONPATH`, else this
  worktree's `src/` (DEC-732). The global-config scene's environment is run 1's (`base_environment`) with `HOME` and
  `XDG_CONFIG_HOME` replaced and `GIT_CONFIG_GLOBAL` removed; every other git setting of this machine stays unread.
- Everything is local (`file://` to a bare repository in the case's temporary folder); no network. Every repository
  is built from scratch; none clones this repository. Commit ids are fixed by run 1's fixed identity and date.
- **Parallel load:** no case is serial-only. Each scene has its own source, clone, counter log and recorder log; no
  count is shared. The `unreadable-config` premise needs a user other than root (mode 000 does not stop root); it says
  so when it fails. Run time: about 25 s for the three files, one process.

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
