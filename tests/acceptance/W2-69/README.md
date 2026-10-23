# W2-69 — The secrets check reads what the stores hold: acceptance tests

Written by the independent test designer (MR-3, DEC-069) from the KPI lines of ticket `DAEO-rmbe` (W2-69, profile
FULL), the card in `docs/plan/WAVE_2_WBS.md` §2, package `P-W2-62-G1` §2 (the cut test), list rows W2-M404,
W2-M395 and W2-L373, and DEC-897, DEC-853, DEC-290, DEC-298, DEC-347, DEC-868, DEC-896, DEC-899, DEC-866, DEC-491,
DEC-221 and DEC-462. **Written before the implementation**: the design note `docs/research/W2-69-secrets-scan.md`
was not read; the design the brief states as behaviour (DEC-897 item 1) is the one tested. The check's code was read
only as it stands on `w2/integrate`, to make the cases red on it.

**215 cases in 7 files**, a support module, a conftest and a pytest plugin of the suite's own:

| File | Cases | KPI |
|---|---|---|
| `test_w2_69_real_token_every_form.py` | 31 | K1, every form |
| `test_w2_69_real_token_across_read_edges.py` | 20 | K1, every offset across the read edges |
| `test_w2_69_word_internal_fragments.py` | 132 | K2 (W2-M404), W2-M395 |
| `test_w2_69_deleted_text_after_rebuild.py` | 4 | K3 |
| `test_w2_69_design_note_first.py` | 1 | K4 |
| `test_w2_69_still_scanned_and_closed.py` | 23 | K5 |
| `test_w2_69_unit_folder_renamed.py` | 4 | K7 (W2-L373) |

K6 (the earlier tests revised only where the change demands it) is answered in "The earlier tests" below: none
needed a change.

## Run

```sh
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-69/td \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src \
  python3 -m pytest tests/acceptance/W2-69 -q -p no:cacheprovider -rs
```

- **The code under test (DEC-732) is this worktree's `src/`.** `PYTHONPATH` is set per command, never in settings.
  Every child process (the check, `gov rebuild`, the pytest run of K7) is given the runner's `PYTHONPATH`, else this
  worktree's `src/` (`w2_69_support.python_path`). The lead checks it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src python3 -c "import gov; print(gov.__file__)"`, which prints
  `/home/usain/gov-os-worktrees/W2-69/src/gov/__init__.py`.
- Standard library, pytest, PyYAML and pytest-xdist (optional) only. Nothing is installed. No network: the stand-in
  embedder of K3 answers on a loopback port of the test's own process.
- **gitleaks 8.30.1 on `PATH`** (`~/.local/bin`) is needed by every case but K4 and K7; they skip without it. K3's
  first three cases need `sqlite_vec` (the runner's user site, given to the rebuild by `PYTHONUSERBASE`); K3's
  fourth needs `codebase-memory-mcp` on `PATH` and skips without it, as W1-16's cases do. Cases that run a binary
  of this machine are marked `local_only`.
- **Every case builds its own project from scratch** in its temporary folder (a git repository with the kernel's
  `template/.gitleaks.toml`, which extends gitleaks' defaults with the project's four rules: two rule sets, DEC-347),
  with `HOME`, `TMPDIR` and `XDG_CACHE_HOME` inside it, and removes it at its end. No case copies this repository or
  any folder of it, and no case reads or writes this repository's `.gov-runtime/`. K4 reads this repository's git
  history (names and dates of commits only); K7 collects this repository's `tests/unit/`.
- **Under `pytest -n auto`.** The suite runs beside every other suite. Its heavy check runs (the sweeps of K1 and
  K2) take one of three lock files in pytest's shared temporary folder, so at most three of them run at once across
  xdist workers, whatever the number of workers (the check runs as many gitleaks at once as there are processors).
- **The one case that runs alone:**
  `tests/acceptance/W2-69/test_w2_69_deleted_text_after_rebuild.py::test_the_code_graph_store_holds_no_deleted_word_and_no_free_page_after_a_rebuild`
  (real-model-or-daemon: it starts the codebase-memory daemon, as every W1-16 case named in
  `tests/acceptance/serial-only.txt` does). That file is outside this designer's paths: the entry is returned to the
  lead. The other three K3 cases hide the tool from `PATH`, so no daemon starts.
- **Run time** (20 processors, a machine loaded to 13–68 by other sessions; measured file by file with `-n 6` to
  `-n 8`): K1 forms 14 s; K1 read edges 2.6–3.4 min; K2 premises 59 s and sweeps 2.8 min; K3 1.5 min; K5 70 s; K4
  and K7 6 s. The whole suite under `-n 8`: see the red run below. Scratch: each case writes at most about 40 MB
  (a sweep of some 300 files of 128 KiB) and removes it.

## Facts the cases are built on (measured for this ticket)

- **gitleaks' reads of standard input.** On text with no blank line, the reads of an input given through a pipe (as
  Python's `subprocess.run(input=…)` writes it) begin at 90,536, then every 28,672 bytes (119,208, 147,880, …); of an
  input given from a file (standard input redirected, or `gitleaks dir`), at 125,000, then every 28,672. Measured with
  21,429 probe tokens on one line: exactly the tokens across those places were missed, three times in a row. On text
  with a blank line every seven lines, no probe token of 14,894 was missed: the reads end at blank lines.
- **gitleaks' default rules**: 222; **68** begin with a word boundary after their flags and opening groups (the
  brief counts 67: `kubernetes-secret-yaml`'s `\b` stands inside its first group); with the project's four, 72.
  gitleaks has no command to print its defaults: the suite reads them from the binary `PATH` finds and fails, saying
  so, if it cannot.
- **SQLite here** (3.45.1, Python 3.12) has `secure_delete` on by default. The builders of freed space turn it off.
- **Today's rebuild leaves deleted text.** After a full rebuild that followed the deletion of 35 of 40 pages,
  `.gov-runtime/store.db` held 216 to 219 free pages, and a word deleted from the sources was still in its
  `lexical_fts_data` rows (FTS5 keeps a deleted term in its segments until they are merged). The code-graph store
  `codeintel/home/code.db` is built afresh at each rebuild (the code index removes its folder first): no free page,
  no deleted word.
- **Today's check on a SQLite file it cannot read** (a damaged page, a truncated file, a header followed by plain
  bytes, a store another process holds locked) raises and exits 1, naming nothing.

## Where the check reads (how the K1 sweeps find the places)

The new check's own splits cannot be known before it exists. So each K1 sweep first **learns them from a learning
run**: the clean content alone in the runtime folder, and a stand-in `gitleaks` first on `PATH` that hands every
decision to the real gitleaks and keeps a copy of each input it is given (W2-50's public means: it sees only what any
gitleaks on `PATH` sees). The content is made of 9-byte cells `t<offset> ` that each name their own offset, so every
stretch of the content in every input is found, and grown byte by byte to its exact ends. From that:

- **the check's splits**: where an input, or a stretch of one, begins or ends (an input per piece, a separator
  put between pieces, an overlap, a value read on its own);
- **gitleaks' reads**: where gitleaks begins a read inside each input, from the measured mechanism above (both the
  pipe and the file forms).

Up to six places are chosen, half of each kind, spread evenly. For each, one case per offset: the token from its full
length plus 3 bytes before the place to 3 bytes after it, one file or store per case, all judged by one run of the
check with the real gitleaks (no stand-in), the clean content beside them as a control. On today's check the learned
places are gitleaks' reads at 90,535 and 119,207 of a plain file's content (and 124,999 for a file read), so the cases
there are red today.

## KPI lines, tests and red reasons

### K1 — success: "A real token is found at every offset and in every form the derived stores hold it …"; failure: "A real token at a word boundary that the check misses, at any offset or in any stored form."

The token is a github-pat shape (40 word characters), built at run time; any cut of it is no token.

| Test | Red today because |
|---|---|
| `every_form::test_a_real_token_is_found_in_every_form_a_store_holds_it` × 30 forms: a plain file; one in a nested folder; one with zero bytes; UTF-16LE with and without a byte-order mark, UTF-16BE; a SQLite text value; text in an INTEGER column; a table without row ids; a full-text index; a blob of the token's bytes, of UTF-16LE and of UTF-16BE; a UTF-16LE and a UTF-16BE store; a value of 300,000 characters (longer than a gitleaks read and than a page); a value that is the token alone; the token at a value's start, at its end; one value among 5,000; the schema (a column default, a view, a trigger); freed space (a freeblock, a free page, a dropped table, the unused space of a page, a freed overflow chain, a freeblock of a UTF-16 store); the write-ahead log (the row committed in the log only) | passes today: today's check finds each (raw bytes, rows as text, bytes without zeros). They guard the change: a design that reads values and freed space must keep every one |
| `every_form::test_control_every_form_without_a_token_is_green` | passes today; a form alone (UTF-16, zeros, blobs, freed space, the schema, the log) is no finding |
| `across_read_edges::test_a_real_token_is_found_across_every_place_a_read_begins_or_ends` × 20: forms `plain-oneline`, `plain-lines`, `plain-blank-lines`, `plain-longword` (words of 18,000 bytes), `plain-utf16le`, `sqlite-long-value`, `sqlite-many-values` (72-byte values), `sqlite-utf16-store-value`, `sqlite-blob`, each with the github-pat shape and with the project's digit token at its shortest with five dashes inside (19 characters: a cut at a dash falls at a byte that is not a word character); and a private-key block of five lines (about 260 bytes, at every 7th offset across the place and at each of its spaces and newlines) in `plain-lines` and `sqlite-long-value` | **red today, 9**: the plain forms without a blank line (`oneline`, `lines`, `longword`, `utf16le`) × both tokens, and the key block in `plain-lines`: "the check missed N of M real tokens … content offset 90535 (a read of gitleaks): token start at [-42 … -1] bytes from it" (today's check gives a plain file to gitleaks as one input). **Not red today, 11**: `plain-blank-lines` (gitleaks ends its reads at a blank line there) and the SQLite forms (today's check gives each value three times — raw bytes, rows as text, bytes without zeros — so a token cut in one copy is whole in another); they test the new check's own splits |

### K2 — success: "An embedded fragment of a longer identifier is not flagged … at every offset relative to wherever the check or gitleaks begins a read … for every rule with a leading word boundary"; failure: "A word-internal fragment flagged at a read edge (the chance red of W2-62's queue, 2026-10-22)."

A word-internal string is word characters followed by a string that is a token by the rule when it stands alone.
Every string is checked by the real gitleaks first (the premises): alone it is a finding by its rule, inside its
word it is a finding by no rule, with each rule set.

| Test | Red today because |
|---|---|
| `word_internal::test_premise_a_project_rules_string_is_a_token_alone_and_none_inside_its_word` × 4 rules | passes today (a premise) |
| `word_internal::test_the_default_rules_with_a_leading_boundary_are_the_ones_covered` | passes today: the 68 default rules and the project's 4 are the ones this suite names |
| `word_internal::test_premise_a_default_rules_string_is_a_token_alone_and_none_inside_its_word` × 68 rules (65 strings built from the rules' own expressions, 3 rules without a case, below) | passes today (a premise) |
| `word_internal::test_a_word_internal_string_of_a_project_rule_is_no_finding_at_any_offset` × 12 forms × 4 rules: the string in cells of 24 bytes, in 24 files shifted by 0 to 23 bytes, so that **every byte offset** is where a token-shaped string begins inside a word in one of them; forms: plain one line, lines, blank lines, words of 12,288 bytes, UTF-16LE; a long SQLite value, many small values, a full-text index, a blob, a UTF-16LE blob, a UTF-16 store, deleted rows in freed space | **red today, 40**: "the check flagged N of 24 files that hold token-shaped strings only inside words": in the plain forms, the files whose string begins at gitleaks' read at 90,535 or 119,207; in the SQLite forms also where today's raw-byte scan cuts a value at an overflow page (its 4-byte page number puts a non-word byte before the string) and, for a blob, where the rows-as-text form renders it as `b'…\n…'` (the `n` after the backslash begins a word). **Not red today, 8**: blank lines (reads end at blank lines) and freed rows (a small store, each freed region begins with a cell's header) |
| `word_internal::test_premise_the_w2_62_identifier_is_no_finding_whole_and_a_finding_cut` | passes today: P-W2-62-G1's cut test, on its shape (84 characters, the first 22 lower-case letters and underscores, a 62-byte `gov-token-lower` shape after them) |
| `word_internal::test_the_identifier_of_the_w2_62_stop_is_no_finding_at_any_offset` × 4 forms (plain lines, plain one line, a long value, many values; cells of 88 bytes in 88 files) | **red today, 4**: "flagged 2 of 88 files" (plain), 6 and 15 (SQLite): W2-62's stop, reproduced |
| `word_internal::test_a_word_internal_string_of_every_default_rule_is_no_finding_at_a_read_edge` × 2 forms (plain lines, a long value; 256 KiB) × 2 sides: **a read begins inside the word** (the token-shaped part begins where a read begins) and **a read ends inside the word** (it ends where a read ends, its word going on after it), at up to twelve learned places, one file per rule | **red today, 4**: the start side flags all 65 files at gitleaks' reads; the end side flags the rules whose trailing condition accepts the end of a read (`$`, `\b`, `\z`) |
| `word_internal::test_bytes_of_different_values_never_join_into_a_finding` × 2 (W2-M395): two adjacent text values whose bytes spell a `gov-token-digit` shape; a text, the integer 95 (stored as the byte `_`) and a text | **red today, 2**: today's check scans the raw bytes, where the values join |

**Fewer offsets for the default rules** (the brief allows it): the read edges do not depend on the rule, the
project's four rules show every offset, and a full sweep of 65 rules on both sides would be some 13,000 files
(DEC-221). **Rules without a case**, each named by `test_premise_a_default_rules_string…`, which fails if a case
becomes possible:

- `gitlab-pat-routable`, `gitlab-runner-authentication-token-routable`: inside a word the string is still found, by
  `gitlab-pat` and `gitlab-runner-authentication-token`, which have no leading boundary;
- `kubernetes-secret-yaml`: it applies only to paths matching `\.ya?ml$`, and gitleaks stdin gives no path.

**End side only where it means something:** for `anthropic-admin-api-key`, `anthropic-api-key`, `jwt-base64`,
`openai-api-key`, `sentry-org-token`, `sidekiq-sensitive-url` and `stripe-access-token` the token followed by more word
characters is still a finding, so a read that ends inside the word makes no new match. Two rules,
`airtable-personnal-access-token` and `facebook-access-token`, need their keyword in the same read: the keyword
follows the token, a space apart.

### K3 — success: "Deleted text does not survive a rebuild …"; failure: "Deleted text left in a store's free pages after a rebuild."

| Test | Red today because |
|---|---|
| `deleted::test_after_a_full_rebuild_no_sqlite_store_has_a_free_page` (40 pages of 4,000 characters, 35 deleted, the semantic index rebuilt both times against the stand-in embedder: 1,024 floats a vector) | **red today**: "SQLite stores still hold free pages (not compacted): {'.gov-runtime/store.db': 216}" |
| `deleted::test_a_word_deleted_from_the_sources_is_in_no_store_after_the_next_rebuild` (the word in a page and in a function name; after the rebuild, no file under `.gov-runtime/` holds it as written, in lower case or in UTF-16, and no FTS5 term holds it, read through `fts5vocab` on a copy) | **red today**: "still in the bytes of ['store.db'] after a full rebuild" (its `lexical_fts_data` rows) |
| `deleted::test_a_secret_removed_from_the_sources_leaves_no_residue_the_check_finds` (a value no rule finds when it is indexed; deleted; after the rebuild a rule that finds it is added) | **red today**: the check is red on the deleted value's residue |
| `deleted::test_the_code_graph_store_holds_no_deleted_word_and_no_free_page_after_a_rebuild` (the code-graph tool on `PATH`; runs alone) | **red today** on the record store's 219 free pages; the code-graph store itself is already compact (built afresh), so this case guards it |

### K4 — "The design question is answered with evidence in docs/research/W2-69-secrets-scan.md before the code …"

| Test | Red today because |
|---|---|
| `design_note::test_the_design_note_was_committed_before_any_code_of_this_ticket` (from git history only: the note is in HEAD and not empty; the commit that first added it is an ancestor of, and not the same as, every `Task: DAEO-rmbe` commit that changes `src/`) | passes today (the note's commit `6ebc7cf7` precedes every commit of the ticket; none changes code yet). It guards the order. The note's words are not read |

### K5 — success: "Every file under .gov-runtime/ the check scans today is still scanned, with every rule set; a scan that cannot finish still fails closed; the reuse of a clean result keyed on the store's hash (DEC-853) stays, and a finding is never reused"; failure: "A store or file the check scanned before and no longer scans; a scan that cannot finish passing as clean."

| Test | Red today because |
|---|---|
| `still::test_every_file_the_check_scans_today_is_still_scanned_with_every_rule_set` (15 kinds: plain, nested, zero bytes, UTF-16 file, JSON, a SQLite value, a blob, a UTF-16 blob, a UTF-16 store, a full-text index, the schema, freed space, the write-ahead log, a linked folder elsewhere, an empty file; each kind's marker word given to gitleaks under each rule set of the run) | passes today; guards the change |
| `still::test_a_sqlite_file_that_cannot_be_read_and_holds_a_token_is_red_naming_it` × 3 (a header then plain bytes, a damaged page, truncated) | **red today, 3**: today's check raises and names nothing ("did not judge the file it cannot read by its raw bytes … it names no …") |
| `still::test_a_sqlite_file_that_cannot_be_read_and_holds_no_token_is_scanned_by_its_raw_bytes` × 3 | **red today, 3**: today's check raises (exit 1) instead of judging the raw bytes |
| `still::test_a_store_another_process_holds_locked_is_judged_by_its_raw_bytes` × 2 (a token; no token) | **red today, 2**: "database is locked", the check raises |
| `still::test_a_scan_that_cannot_finish_fails_closed` × 7 (gitleaks hangs, is killed or exits with a code it does not give, on a SQLite value, freed space or a plain file; then the next run scans it in full) | passes today; guards the change |
| `still::test_without_gitleaks_the_check_fails_closed` | passes today |
| `still::test_an_unchanged_sqlite_store_is_reused_and_a_change_in_its_freed_space_is_scanned_again` | passes today (DEC-853 as W2-50 built it) |
| `still::test_a_finding_in_freed_space_is_never_reused` (three runs) | passes today |
| `still::test_a_value_only_the_projects_own_rules_find_is_red_in_every_form` × 4 (a value, freed space, a UTF-16 blob, a plain file; DEC-347) | passes today |

### K6 — "The earlier tests this change affects are … revised only where scanning the rows as text or compacting the stores changes what they expect …"

See "The earlier tests" below: none needed a change; none was changed.

### K7 — "tests/unit/secrets/ is renamed tests/unit/secrets_check/ … collection is clean with pytest-rerunfailures and pytest-randomly loaded"

**pytest-rerunfailures and pytest-randomly are not installed on this machine, and nothing may be installed.** What
they need is tested instead: the suite's own plugin `w2_69_stdlib_secrets_first.py`, loaded first with `-p`, imports
the standard library's `secrets` before any test is collected, as they do (W2-L373).

| Test | Red today because |
|---|---|
| `unit::test_the_unit_folder_named_secrets_is_gone` | **red today**: "tests/unit/secrets still exists" |
| `unit::test_the_checks_builder_tests_are_under_secrets_check` (`test_scan_scale.py`, `test_secrets.py`, `test_token_rule.py`) | **red today**: "tests/unit/secrets_check does not exist" |
| `unit::test_unit_collection_is_clean_with_a_plugin_that_imports_the_standard_librarys_secrets_first` × 2 (one process with `--collect-only`; two xdist workers, each collecting, no test selected) | **red today, 2**: "No module named 'secrets.test_scan_scale'; 'secrets' is not a package" (3 errors) |

## Red run

Run file by file to its end (never `-x`) on `w2/W2-69` at `e4687ef4` plus this suite, with the command above and
`-n 6` to `-n 8`: **75 failed, 140 passed, 0 skipped** — K1 forms 0/31 red, K1 read edges 9/20, K2 50/132 (the 74
premises and the coverage case pass), K3 4/4, K4 0/1, K5 8/23, K7 4/4. Each red case fails for the reason its row
states. The whole suite in one run: see the designer's return.

## Readings chosen (the lead's to confirm)

- **R1 — a finding** is exit code 1 and a line of standard output naming the file's project-relative path (as
  `python3 -m gov.secrets` prints today); a run that names no file but exits non-zero fails a K2 case too.
- **R2 — "scanned"** is "each of the file's marker words given to gitleaks under every rule set of the run", the
  rule sets being those the run's fresh file was scanned with (W2-50's D1).
- **R3 — an unreadable SQLite file** (one SQLite cannot open, or read in full, or that another process holds
  locked) is judged by its raw bytes, as the design says: with a token, red naming it; without, green, its bytes
  given to gitleaks under every rule set. Failing closed without a verdict would fail these cases.
- **R4 — the K1 tokens** are ones that any cut makes no token (a fixed-length shape, the digit token at its
  shortest, a key block), so a token across a place is missed only if the check lets a read cut it.
- **R5 — K2's words** are up to 12,288 bytes long (18,000 for K1). Words longer than one gitleaks read are not
  tested: gitleaks itself begins a read inside such a word whatever the check gives it (package P-2 in the
  designer's return).
- **R6 — freed space**: a token or a word-internal string whole within one freed region of one page. A token cut by
  a page edge in freed space (a freed overflow chain, whose pages are no longer joined), and a word-internal string
  at the start of a freed overflow page, are not tested (package P-1 in the designer's return).
- **R7 — K3's full rebuild** is `gov rebuild --json` without `--no-embeddings`, the semantic index built against a
  stand-in embedder; "free pages" is `PRAGMA freelist_count`; "in no store's bytes" is no file under `.gov-runtime/`
  holding the word as written, in lower case or in UTF-16, and no FTS5 term holding it.
- **R8 — K4** is judged from git history only: ancestry of the commit that first added the note, never its words.

## The earlier tests (K6, MR-3, P-IS-5 (a), DEC-899)

**None needed a change; none was changed.** Each named file was read against the design:

- `test_w2_50_secrets_scan_scale.py` and `w2_50_scan_support.py`: their SQLite store holds its marker words in
  row values (`sqlite_store`: filler, a word, filler, one row each), which a check that reads values gives gitleaks
  under every rule set; their large stores are plain files (raw bytes, as before); `replace_one_byte` changes a
  value's bytes in place, which a value read sees; the stand-in sees every input whatever the check splits, and the
  reuse label (path and SHA-256) is DEC-853's, which stays. No case rebuilds, so compaction changes nothing there.
- `test_w2_50_never_indexed.py` (its secrets cases): plain files under `.gov-runtime/` and links; its rebuild cases
  compare stores before and after another project's rebuild and look for words that never reach a store. Compacting
  the clone's stores changes neither.
- `test_w2_50_last_review.py` (its secrets cases): plain files under `.gov-runtime/` reached through links.

No earlier test enforces a superseded decision (DEC-866). W1-15's B6 cases (a canary in a deleted row's bytes, in a
view's text) still hold under the design (the freed-space backstop, the schema table).

## Discoveries of this round (no test)

- **The pre-index filter misses a real token across gitleaks' first read too.** `gov.secrets.indexable(root, paths)`
  gives each file to gitleaks as today's check does: a 128 KiB page with a token across content offset 90,535 was let
  through to the index; the same token at offset 1,000 was kept out. It fails open at indexing time; the check is the
  backstop. Package P-3 in the designer's return.
- `gov retrieve` gave `FACET_UNAVAILABLE` (both facets stale); the sources were read by name.
