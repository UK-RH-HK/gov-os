# W2-174 acceptance tests: the Verify pass and the adoption's facts file

Ticket DAEO-zmo4 (W2-174), profile FULL since its reopening (DEC-1188, 2026-11-15; STANDARD before). The first eight lines
were written by the independent test designer before any implementation, the three launch-field lines (S6, S7, F4) in a
second pass (see "The launch fields" below), from
the ticket's eight KPI lines (five success, three failure), its "Interface" and "Rabbit holes", the two owner sections
at its end (S5 widened by DEC-1148 (2); the skill line moved to W2-88a by DEC-1150 (1), so there is no skill case),
the approach (`governance/project/orchestration/packages/ADOPT-VERIFY-1/APPROACH.md`), the lead's decisions L1 to L9
(the brief's text), `src/gov/brief/build.py` (`kpi_rows`, `ready_check`, `build`: read-only) and
`tests/acceptance/W2-152/` (the form of this folder). Nothing of this ticket's implementation was read.

KPI cells use positions in the ticket: `S<n>` is the n-th success line, `F<n>` the n-th failure line:

| id | line |
|---|---|
| S1 | `gov adopt --verify-list` prints the id and labels of each open or in-progress ticket with a KPI line lacking a verify; `none`, exit 0, when none |
| S2 | `gov adopt --verify-apply` appends ` Verify: <clause>` to each named line and adds `verify_pass: <date> <session>`; every other byte unchanged |
| S3 | after an apply, `ready_check` gives no `KPI_NO_VERIFY` and `gov brief engineer` builds |
| S4 | the answers file is checked by code before anything is written (unknown ticket, closed, unknown label, unanswered line, empty clause) |
| S5 | `gov adopt` writes `governance/project/facts.yaml` when there is none (schema-valid, `ready.new_since` the UTC date, product defaults, named placeholders); an existing one is left byte for byte |
| F1 | all or nothing; an unnamed or closed ticket never edited; no ticket marked while a line lacks a verify |
| F2 | nothing of `gov brief`, the ready check, the template or the schema changes |
| F3 | the verify pass reads and writes nothing outside `<repo>/.tickets/` and the answers file; no model, no network |
| S6 | the list also prints each of role, allowed_paths, kpis, reads, needs, waits_on a ticket lacks; the apply writes them from the answers file so the ticket validates against `ticket.schema.json`, `ready_check` refuses nothing and `gov brief independent-auditor` builds (DEC-1188) |
| S7 | the fields are checked by code before any write (known role, non-empty `allowed_paths` with nothing under `tests/acceptance/` unless the role is independent-test-designer, every KPI line with a verify, list forms); a field the ticket has is refused, never overwritten (DEC-1188) |
| F4 | an apply that overwrites a field, writes a field the answers did not name, or leaves a ticket failing the ticket schema (DEC-1188) |

## How they run

    HOME=<empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-174 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

About 7 s on the finished code. No model, no network, no GPU, no store, no `gov retrieve`. No case is named `real`,
`green_here` or `time_limit` and none is marked `local_only`, so the exclusion leaves nothing out. No skip, xfail, flaky
or rerun mark. The cases need `git`, `PyYAML` and `jsonschema` 4.x. In-process cases import `gov` from the tree under
test (`conftest.py` puts its `src/` first).

## What the cases do

- **Fixture repositories, never this one.** Each case builds `tmp_path/adopted-fixture-q7x` with a `.tickets/` of
  planted tickets (tk's form), optionally the kernel templates (copied from this tree) and a filled facts file (this
  tree's `governance/project/facts.yaml` with `ready.new_since` set to `2026-11-10`: what the project's CTO has after the
  defaults, the ticket's S3 fixture). The answers file lives in a folder beside the repository, never inside it.
  The folder's name is distinctive so S5 can check the facts file does not name it.
- **The public interface.** `python3 -B -m gov.cli.main adopt --verify-list|--verify-apply <file>|--facts --root <tmp>/adopted-fixture-q7x [--session s] [--json]`
  as a subprocess (`PYTHONPATH=<this tree>/src`, an empty `HOME`, `PYTHONDONTWRITEBYTECODE=1`, dead proxies), read
  from the API-0002 envelope (`result`, or `error.code` on exit 1); and the functions `verify_pass.missing(root)`,
  `verify_pass.apply(root, answers_path, session, today)` (with `today` a `datetime.date`) and
  `facts.write_default(root, today)`.
- **Lists (S1).** Three tickets as the ticket's Verify clause says (all lines verified in both forms; two plain lines
  lacking a verify; a closed ticket with one) give exactly the second's `S2 F1`; the all-verified repository gives
  `missing == []`, `text == "none"`; a sorted, mixed repository checks the order (ids sorted, labels in `kpi_rows` order,
  one line per ticket); the list agrees with `ready_check`'s `KPI_NO_VERIFY` details.
- **Byte diff (S2).** A ticket with YAML comments (before keys, after values, on KPI lines, between lines), keys in no
  alphabetical order, five KPI lines (plain, single-quoted, double-quoted, a `{line, verify}` mapping, a plain failure
  line) and a body holding a `---` rule: after the apply the whole file equals the original with the four clauses
  appended and one `verify_pass: <date> <session>` line before the front matter's closing `---`. The mapping and every
  comment are byte-identical. The CLI case accepts the UTC date either side of the run.
- **Refusals (S4, F1).** One case per code of L4, each refused through the CLI (exit 1, code in the envelope) and
  through the function (a `GovError` of the same code), with every file of the tree (repository and the answers folder:
  names, modes, sizes, modification times and SHA-256) byte-identical afterwards. Ten tickets with a nine-good, one-bad
  answers file: the bad entry first or last (by file order and by id), five kinds of fault; an unnamed ticket and the
  closed ones are never edited; no ticket carries `verify_pass` while a line lacks a verify.
- **Facts (S5).** The file validates against `template/governance/kernel/schemas/facts.schema.json` (`jsonschema`
  Draft 2020-12 with the format checker); `ready.new_since` is a quoted ISO string equal to the UTC date of the run (a
  fixed date for the function); the text names neither the repository's path, its folder name, nor `/home/`; every
  command's `run` starts with `gov ` or is exactly `{UNSET_<NAME>}` (and then its `check` is too); `lead_verify` is
  `{UNSET_LEAD_VERIFY}`; `wait_for` starts `gov wait`. `gov brief engineer` there no longer answers
  `BRIEF_FACTS_MISSING`; `gov brief lead <ticket> --run build` is refused `BRIEF_NOT_READY` with a `PLACEHOLDER_LEFT`
  finding naming `UNSET_LEAD_VERIFY`. A repository with its own facts file (valid or not) keeps it byte-identical and gets
  `written: false`.
- **Untouched (F2).** The files this ticket's own change names (the files of its own commits since `f2b1d38af`, found by
  `git log --no-merges --name-only --grep='^Task: DAEO-zmo4$' f2b1d38af..HEAD`, any role; plus tracked changes against
  `HEAD` and `git status`) under test include no file under `src/gov/brief/`, `template/governance/kernel/templates/` or
  `template/governance/kernel/schemas/`, and none of `src/gov/adopt/stages.py` or `tests/acceptance/W2-152/` (lead
  decision L9). **Chosen (batch 3): the ticket's own commits by their `Task:` trailer, not a fixed base**, because a
  fixed base also names every file other tickets changed since it (W2-88's `src/gov/adopt/stages.py`, integrated before
  this reopen), both in the ticket branch and, worse, when the merge queue runs the folder on the ticket merged into
  `w2/integrate`; the trailer judges this ticket's change alone in both places, and the merge commit names nothing.
  `W2_174_BASE` still works as an override: set, the cases judge `git diff --name-only <base> HEAD` (plus tracked changes
  and `git status`) as before. The cases skip, with the reason, only when the tree is not a git checkout or the base
  commit is not in it.
  **`tests/acceptance/W2-152` must still pass unchanged: the lead runs it** (`gov accept W2-152`); it is not rerun here.
- **Scope (F3).** A decoy file outside `.tickets/` (README, register, code, facts file, notes) and decoys beside the
  answers file are byte-identical after list and apply, through the CLI and the function, and `.tickets/` holds the same
  file names afterwards (no temporary or backup file left). `verify_pass.py`'s imports (read with `ast`, nested ones
  included) name none of `socket`, `http`, `urllib`, `requests`, `httpx`, `anthropic`, `openai`, `subprocess`, and name
  `gov.brief.build`. An audit hook watches every `open` while the functions run in-process: nothing is opened outside
  `<root>/.tickets/` and the answers file (the code files Python itself loads are not counted), nothing connects or
  starts a process, and the spy is shown to see the ticket and answers reads, so it cannot pass by seeing nothing.

## The launch fields (S6, S7, F4; DEC-1188, the second pass, 2026-11-15)

Written from the ticket's S6, S7 and F4 and the lead's interface L10 to L17 (the brief's text: the six fields in order; the
list `{ticket, labels, fields}`; the answers file; the checks and their codes; the insert-only write; scope; fixtures;
what stays), `src/gov/brief/build.py` (read-only), the kernel's `ticket.schema.json` and `common.schema.json`, and the
operator's worked example (the coordination ticket's and the A5 review ticket's fields). The branch `w2/W2-174`'s new
commits and the tree `W2-174` were not read. The cases are in `test_w2_174_fields.py`; `w2_174_support.py` gained helpers
(`bare_text`, `with_fields`, `good_fields`, `schema_errors`, `refusals_of`, `Repo.bare`), nothing of it changed.

- **Fixtures (L16).** `exa-dt1z` (a coordination ticket) and `exa-a5rv` (the A5 review ticket), each as `tk` writes a ticket
  plus `id`, `type`, `status`, `state_class` and a comment between keys and one after a value, and none of the six fields,
  no `class`, no `non_goals`; the kernel templates, a filled facts file and a file the review waits on. The coordination
  ticket is given role `orchestrator` and paths under `governance/` (not `**`: L13 refuses `**` for any role but the test
  designer); the review ticket role `independent-auditor`, `governance/project/audits/adoption-A5/**`, KPI lines in the
  `{line, verify}` form and as a string carrying `Verify:`, `reads`, `needs: []`, and `waits_on` as a `{ref, reason}` item
  and a path string. A refusal case uses two bare tickets, `exa-aa01` spoiled in one field and `exa-bb02` answered well, so
  a refusal also shows the good entry was not written.
- **S6.** The list gives exactly the six fields of each bare ticket, in `missing` and `text` (CLI and function); a mixed
  repository checks L10 order beside the labels, that a key present with any value (`[]` included) is set, that a ticket
  without `kpis` has no labels, that `state_class` and the other keys are never listed, that a ticket with all six and
  every verify is not listed, and that closed tickets are skipped. After the apply (CLI and function): each ticket validates
  against the kernel schema (`jsonschema`, `common.schema.json` resolved), `ready_check` returns no refusal, each field reads
  back as given, the list prints `none`, and `gov brief independent-auditor exa-a5rv` exits 0. Before the apply each check
  refuses, so the fixture is the cause of nothing. A byte check: the applied file is the original with only the inserted field
  lines (YAML in L10 order, equal to the answers) and the one marker line, last; every original line before the closing `---`,
  the closing line and the body are as they were; the comments stay. A ticket that also lacks clauses gets its fields and
  its clauses and nothing else (a line diff: only the three KPI lines change; everything else is inserted before the `---`).
- **S7.** One case per refusal, each through the CLI (exit 1, code in the envelope) and the function (a `GovError` of the same
  code), the whole tree (repository and answers folder: names, modes, sizes, times, SHA-256) byte-identical afterwards and the
  good entry of the second ticket not written: unknown role (`wizard`, `Engineer`, `lead`); an empty `allowed_paths` and
  every non-schema form of L12 (`VERIFY_PASS_BAD_FIELD`, 24 values, including a `..` segment and a leading `/`); an acceptance
  path for an engineer (14 patterns that reach `tests/acceptance/`: the literal part before the first `*`, `?` or `[`, after a
  leading `./` is dropped, starts with it or is a prefix of it: `**`, `tests/**`, `t*`, `tests/acceptance`, `[t]ests/**` ...),
  for every other role, and for a ticket's own role when the answers give none; a designer with `tests/acceptance/W2-9/**`,
  `**`, `tests/**` is accepted, and so are eight patterns that cannot reach it (`src/**`, `tests/acceptance_helpers/**` ...);
  a KPI line without a verify (`VERIFY_PASS_KPI_NO_VERIFY`: a string with no `Verify:`, one with nothing after it) and a
  verify that is only TBD, TODO, n/a or none (`VERIFY_PASS_EMPTY_CLAUSE`, mapping and string forms); a field the ticket
  already has (each of the six, `reads: []` included); and, from L13, `VERIFY_PASS_UNANSWERED` (each field left out, an empty
  entry, fields answered while a line still lacks its verify, the ticket unmarked). Each of the six roles is accepted.
- **F4.** A set field answered with a different value and with the same value (`VERIFY_PASS_FIELD_SET`, `role` and `reads`);
  a ticket that would fail the schema (no `state_class`; an id outside the ticket-id grammar: `VERIFY_PASS_SCHEMA`); the
  schema judged is the one shipped with gov: a permissive copy inside the repository does not rescue a ticket without
  `state_class`, and a copy requiring an impossible key does not refuse a good one (and is left byte-identical); eleven names
  the pass does not write (`state_class`, `non_goals`, `class`, `type`, `profile`, `title`, `status`, `ROLE`, `deps`,
  `verify_pass`, `sources`) refused `VERIFY_PASS_UNKNOWN_LABEL`, the same answers without the key then applying (so the key
  was the only fault) and the key's value never written; a closed and an unknown ticket named with fields; and one good
  apply of two tickets (all six; reads, needs and waits_on of a half-fielded one) beside four tickets it does not name (bare,
  closed, complete, and one that would fail the schema), through the CLI and the function: the keys after are the keys
  before plus the named fields plus the marker, every earlier value unchanged, the inserted lines are exactly the named fields
  and the marker, the unnamed tickets byte for byte as they were, and nothing else in the tree changed or added.
- **L15 (F3 stands).** An audit hook watches every `open` while `missing` and `apply` run on the field fixtures with decoys in
  the repository (a README, decoy kernel schemas): nothing of the repository outside `.tickets/` is opened, nothing connects
  or starts a process, and the spy sees the ticket reads.

### Earlier cases the interface required to change (second pass)

- `test_w2_174_list.py`: seven equality checks gain `"fields": []` in each expected item (L11: every item carries both
  lists, either may be empty). Their `text` lines are unchanged (no field after the labels).
- `test_w2_174_checks.py`: the ten-ticket fixture's ids `DAEO-t01`..`DAEO-t10` become `DAEO-t001`..`DAEO-t010` (three
  places). L13's `VERIFY_PASS_SCHEMA` judges every ticket an apply would write, and the ticket-id grammar is a prefix and four
  characters of `[a-z0-9]`, which the old ids did not meet.
- `test_w2_174_scope.py`: `_stray_opens` also counts as allowed a read under the kernel's schema folders (L15: the pass reads
  the schema shipped with gov); nothing else of that case changed.
- **F2 no longer judges a stale base (batch 3).** `test_f2_the_adoption_stages_and_w2_152s_acceptance_folder_are_unchanged`
  failed at the ticket's head because its base `f2b1d38af` is older than the integrated `src/gov/adopt/stages.py`
  change (W2-88 S26). Both F2 cases now judge this ticket's own commits (see the F2 paragraph above) and are green with no
  variable set; `W2_174_BASE` remains an override.

## Readings of the interface where it is silent (the implementation may differ in these only where noted)

- **A plain scalar cannot take ` Verify: <clause>`.** `: ` inside a plain YAML scalar opens a mapping, so
  `- The widget prints its name. Verify: a test` is not a string. The tool must re-quote the item it edits (L5 says an item
  "may" be turned into a single-quoted scalar when the clause holds `: `; it must always, because ` Verify: ` itself holds
  one). The cases therefore accept a plain item edited into either quote style, its trailing note kept, and check by
  re-reading with `kpi_rows` that the clause is exactly the verify; the two quoted items are checked byte for byte.
  Fixtures hold already-verified plain strings in single quotes for the same reason.
- **`today`** is passed to `apply` as a `datetime.date` (as `write_default`'s is), and `str(today)` is the marker's date.
- **`--session ""` / no `--session`** on `--verify-apply`: the usage error must mention the session, exit 2, write nothing.
- **A named ticket with no label answered** (`{}`) is `VERIFY_PASS_UNANSWERED` when it has a line lacking a verify.
- **A clause starting with a placeholder word** (`none of the files change: ...`) is accepted: only a clause that is
  *only* TBD, TODO, n/a or none (case, padding and trailing dots ignored) is refused.
- **An answers file naming a label already answered** (including a second apply of the same file) is
  `VERIFY_PASS_UNKNOWN_LABEL`, as L4 says.
- **(second pass) The first refusal.** Cases give one fault at a time (every other field of the answers is good), so no case
  depends on which L13 check runs first. Where L13 lists two codes for one value, the case is left out: a `{line, verify}`
  mapping whose verify is empty or only spaces (KPI_NO_VERIFY by `kpi_rows`, EMPTY_CLAUSE by "empty"), a `{line}` mapping
  with no `verify` key, a non-string `role`, `waits_on` items with extra keys, and a `kpis` with no `failure` key.
- **(second pass) The values are written as given.** Each applied field reads back equal to the answers' value
  (`yaml.safe_load` of the inserted lines), whatever block or flow style the tool chooses; a pattern such as `./src/widget/**`
  is not normalized.
- The default facts' other keys, and whether `launch_worker` has a product form, are the engineer's call; the cases only
  check what L7 states.

## Map

| KPI line | Test (node id) | On base | Why |
|---|---|---|---|
| S1 | `test_w2_174_list.py::test_s1_cli_names_exactly_the_open_ticket_with_two_lines_lacking_a_verify` | red (second pass) | the items carry no `fields` key (L11); on the integrated code before this pass it was green |
| S1 | `test_w2_174_list.py::test_s1_function_names_exactly_the_open_ticket_with_two_lines_lacking_a_verify` | red (second pass) | the items carry no `fields` key (L11); on the integrated code before this pass it was green |
| S1 | `test_w2_174_list.py::test_s1_cli_without_json_prints_the_result_as_gov_does` | red (second pass) | the items carry no `fields` key (L11); on the integrated code before this pass it was green |
| S1 | `test_w2_174_list.py::test_s1_all_verified_repository_prints_none_and_exits_0_cli` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_all_verified_repository_prints_none_function` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S1 | `test_w2_174_list.py::test_s1_nothing_to_list_is_none_with_exit_0[no-tickets]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_nothing_to_list_is_none_with_exit_0[only-closed-with-a-missing-line]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S1 | `test_w2_174_list.py::test_s1_open_and_in_progress_listed_sorted_by_id_labels_in_kpi_order` | red (second pass) | the items carry no `fields` key (L11); on the integrated code before this pass it was green |
| S1 | `test_w2_174_list.py::test_s1_the_list_agrees_with_the_ready_check` | red (second pass) | the items carry no `fields` key (L11); on the integrated code before this pass it was green |
| S2 | `test_w2_174_apply.py::test_s2_byte_diff_shows_only_the_appended_clauses_and_the_one_added_line[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_byte_diff_shows_only_the_appended_clauses_and_the_one_added_line[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_the_mapping_line_and_its_comment_are_byte_identical[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_the_mapping_line_and_its_comment_are_byte_identical[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_the_marker_is_one_line_just_before_the_closing_rule[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_the_marker_is_one_line_just_before_the_closing_rule[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_the_applied_ticket_reads_back_with_each_clause_and_every_other_value_unchanged[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_the_applied_ticket_reads_back_with_each_clause_and_every_other_value_unchanged[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_a_clause_the_style_cannot_hold_is_escaped_and_only_its_item_changes[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_a_clause_the_style_cannot_hold_is_escaped_and_only_its_item_changes[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_an_existing_marker_is_replaced_in_place_and_stays_the_only_one[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_an_existing_marker_is_replaced_in_place_and_stays_the_only_one[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_two_tickets_are_both_changed_and_each_marked[cli]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S2 | `test_w2_174_apply.py::test_s2_two_tickets_are_both_changed_and_each_marked[function]` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S2 | `test_w2_174_apply.py::test_s2_apply_without_a_session_is_a_usage_error_and_writes_nothing` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S3 | `test_w2_174_apply.py::test_s3_after_an_apply_the_ticket_is_ready_and_gov_brief_engineer_builds_its_brief` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S3 | `test_w2_174_apply.py::test_s3_the_function_applied_ticket_is_ready_too` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| S4 | `test_w2_174_checks.py::test_s4_the_good_answers_are_applied_to_prove_the_fixture_is_not_the_cause` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_key_that_is_no_ticket_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_closed_ticket_is_refused_and_never_edited` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_the_ticket_does_not_have_is_refused[S9]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_the_ticket_does_not_have_is_refused[F7]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_the_ticket_does_not_have_is_refused[S0]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_whose_line_already_has_a_verify_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_label_answered_twice_over_an_earlier_apply_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_f1_a_line_still_lacking_a_verify_is_refused_and_the_ticket_unmarked` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_f1_a_named_ticket_with_no_label_answered_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[empty]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[spaces]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[tab]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TBD]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[tbd]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[Tbd]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TODO]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[todo]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[n-a]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[N-A]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[none]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[None]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[NONE]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[none-padded]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TBD-dot]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[none-dot]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[n-a-dots]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[TODO-padded-dot]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[number]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_empty_or_placeholder_clause_is_refused[null]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_a_clause_with_words_of_its_own_is_accepted_even_when_it_starts_with_a_placeholder_word` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[missing-file]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[not-yaml]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[a-list]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[a-mapping-of-text]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S4 | `test_w2_174_checks.py::test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused[empty-file]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_a_repository_without_a_facts_file_gets_one_that_validates_and_is_a_product_default` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_the_default_file_is_the_same_text_on_a_second_repository` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_gov_brief_there_no_longer_answers_facts_missing` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_gov_brief_lead_names_the_unset_lead_verify_placeholder_as_a_refusal` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_a_repository_with_its_own_facts_file_keeps_it_byte_identical` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_a_valid_facts_file_of_the_project_is_kept_too` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_running_the_step_twice_changes_nothing_the_second_time` | red | `gov adopt --facts` is not a flag: exit 2, `unrecognized arguments` |
| S5 | `test_w2_174_facts.py::test_s5_function_write_default_with_a_fixed_date` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_write_default_leaves_an_existing_file_alone` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_new_since_is_the_date_given[date0]` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_new_since_is_the_date_given[date1]` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| S5 | `test_w2_174_facts.py::test_s5_function_new_since_is_the_date_given[date2]` | red | src/gov/adopt/facts.py is missing (no `write_default`) |
| F1 | `test_w2_174_checks.py::test_s4_f1_a_line_still_lacking_a_verify_is_refused_and_the_ticket_unmarked` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_s4_f1_a_named_ticket_with_no_label_answered_is_refused` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[empty-clause-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[empty-clause-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-label-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-label-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unanswered-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unanswered-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[closed-ticket-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[closed-ticket-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-ticket-last]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical[unknown-ticket-first]` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_a_ticket_the_answers_file_does_not_name_is_never_edited` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F1 | `test_w2_174_checks.py::test_f1_the_function_never_edits_an_unnamed_ticket_either` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| F1 | `test_w2_174_checks.py::test_f1_no_ticket_is_marked_while_a_line_of_it_lacks_a_verify` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F2 | `test_w2_174_scope.py::test_f2_the_diff_against_the_base_names_no_file_of_gov_brief_the_templates_or_the_schemas` | green | a guard: this ticket's own commits (by trailer) and uncommitted changes name no guarded file |
| F2 | `test_w2_174_scope.py::test_f2_the_adoption_stages_and_w2_152s_acceptance_folder_are_unchanged` | green | a guard: this ticket's own commits (by trailer) and uncommitted changes name no guarded file |
| F3 | `test_w2_174_scope.py::test_f3_a_decoy_outside_tickets_is_byte_identical_after_list_and_apply_cli` | red | `gov adopt --verify-list` / `--verify-apply` are not flags: exit 2, `unrecognized arguments` |
| F3 | `test_w2_174_scope.py::test_f3_a_decoy_outside_tickets_is_byte_identical_after_list_and_apply_function` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| F3 | `test_w2_174_scope.py::test_f3_the_module_imports_no_network_or_model_package` | red | src/gov/adopt/verify_pass.py is missing |
| F3 | `test_w2_174_scope.py::test_f3_list_and_apply_open_nothing_outside_tickets_and_the_answers_file_and_start_no_connection` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| F3 | `test_w2_174_scope.py::test_f3_a_refusal_opens_nothing_outside_either` | red | src/gov/adopt/verify_pass.py is missing (`gov.adopt.verify_pass` does not import) |
| F3 | `test_w2_174_fields.py::test_l15_the_field_pass_opens_nothing_of_the_repository_but_tickets_starts_no_process_and_no_connection` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_overwriting_a_set_field_is_refused_and_the_tree_is_byte_identical[different]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| F4 | `test_w2_174_fields.py::test_f4_overwriting_a_set_field_is_refused_and_the_tree_is_byte_identical[same]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| F4 | `test_w2_174_fields.py::test_f4_a_ticket_that_would_fail_the_ticket_schema_is_refused_and_nothing_is_written[no-state-class]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_SCHEMA`: a field name is no label yet (L12) |
| F4 | `test_w2_174_fields.py::test_f4_a_ticket_that_would_fail_the_ticket_schema_is_refused_and_nothing_is_written[id-not-a-ticket-id]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_SCHEMA`: a field name is no label yet (L12) |
| F4 | `test_w2_174_fields.py::test_f4_the_schema_judged_is_the_one_shipped_with_gov_never_a_copy_inside_the_repository` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_SCHEMA`: a field name is no label yet (L12) |
| F4 | `test_w2_174_fields.py::test_f4_a_stricter_copy_inside_the_repository_does_not_refuse_a_ticket_the_kernel_schema_accepts` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[state_class]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[non_goals]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[class]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[type]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[profile]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[title]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[status]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[ROLE]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[deps]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[verify_pass]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_field_name_the_pass_does_not_write_is_refused_unknown_label_and_nothing_is_written[sources]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_closed_ticket_and_an_unknown_one_are_refused_with_fields_too` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_CLOSED`: a field name is no label yet (L12) |
| F4 | `test_w2_174_fields.py::test_f4_a_good_apply_of_several_tickets_adds_no_key_the_answers_did_not_name[cli]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| F4 | `test_w2_174_fields.py::test_f4_a_good_apply_of_several_tickets_adds_no_key_the_answers_did_not_name[function]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S6 | `test_w2_174_fields.py::test_s6_the_list_names_the_six_fields_of_each_ticket_that_has_none[cli]` | red | `missing` carries no `fields` (L11): no ticket lists a lacking field |
| S6 | `test_w2_174_fields.py::test_s6_the_list_names_the_six_fields_of_each_ticket_that_has_none[function]` | red | `missing` carries no `fields` (L11): no ticket lists a lacking field |
| S6 | `test_w2_174_fields.py::test_s6_the_cli_text_without_json_is_gov_s_result_dict` | red | `missing` carries no `fields` (L11): no ticket lists a lacking field |
| S6 | `test_w2_174_fields.py::test_s6_the_list_mixes_labels_and_lacking_fields_and_skips_what_is_set[cli]` | red | `missing` carries no `fields` (L11): no ticket lists a lacking field |
| S6 | `test_w2_174_fields.py::test_s6_the_list_mixes_labels_and_lacking_fields_and_skips_what_is_set[function]` | red | `missing` carries no `fields` (L11): no ticket lists a lacking field |
| S6 | `test_w2_174_fields.py::test_s6_after_the_apply_both_tickets_validate_are_ready_and_the_auditor_brief_builds[cli]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S6 | `test_w2_174_fields.py::test_s6_after_the_apply_both_tickets_validate_are_ready_and_the_auditor_brief_builds[function]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S6 | `test_w2_174_fields.py::test_s6_the_applied_file_is_the_original_plus_only_the_inserted_field_lines_and_the_marker[cli]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S6 | `test_w2_174_fields.py::test_s6_the_applied_file_is_the_original_plus_only_the_inserted_field_lines_and_the_marker[function]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S6 | `test_w2_174_fields.py::test_s6_a_ticket_that_also_lacks_a_clause_gets_its_fields_and_its_clause_and_nothing_else[cli]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S6 | `test_w2_174_fields.py::test_s6_a_ticket_that_also_lacks_a_clause_gets_its_fields_and_its_clause_and_nothing_else[function]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_unknown_role_is_refused[wizard]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNKNOWN_ROLE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_unknown_role_is_refused[Engineer]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNKNOWN_ROLE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_unknown_role_is_refused[lead]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNKNOWN_ROLE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_each_role_a_ticket_is_launched_under_is_accepted[orchestrator]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_each_role_a_ticket_is_launched_under_is_accepted[product-spec]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_each_role_a_ticket_is_launched_under_is_accepted[independent-test-designer]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_each_role_a_ticket_is_launched_under_is_accepted[engineer]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_each_role_a_ticket_is_launched_under_is_accepted[independent-auditor]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_each_role_a_ticket_is_launched_under_is_accepted[research]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_empty_allowed_paths_is_refused` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[allowed_paths-not-a-list]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[allowed_paths-an-empty-item]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[allowed_paths-a-number]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[allowed_paths-dotdot-first]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[allowed_paths-dotdot-inside]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[allowed_paths-absolute]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[allowed_paths-absolute-acceptance]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[reads-not-a-list]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[reads-an-empty-item]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[reads-a-number]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[needs-not-a-list]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[needs-an-empty-item]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[needs-a-number]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[waits_on-not-a-list]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[waits_on-a-number]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[waits_on-an-empty-string]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[waits_on-no-reason]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[waits_on-no-ref]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[waits_on-an-empty-ref]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[kpis-no-success]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[kpis-an-empty-success]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[kpis-a-string]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[kpis-success-not-a-list]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_value_that_is_not_the_schemas_form_is_refused_bad_field[kpis-a-number-item]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_BAD_FIELD`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/acceptance/**]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/acceptance/W2-1/x.py]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[**]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/**]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[t*]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[./tests/acceptance/**]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/acc*/x]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/accept?nce/**]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/acceptance/]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/acceptance]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[[t]ests/**]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[*]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[tests/a*]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_acceptance_path_for_an_engineer_is_refused[te?ts/**]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_the_acceptance_rule_holds_for_every_role_but_the_test_designer[orchestrator]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_the_acceptance_rule_holds_for_every_role_but_the_test_designer[research]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_the_acceptance_rule_holds_for_every_role_but_the_test_designer[independent-auditor]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_the_acceptance_rule_holds_for_every_role_but_the_test_designer[product-spec]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_the_ticket_s_own_role_judges_the_acceptance_path_when_the_answers_give_no_role` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_ACCEPTANCE_PATH`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[cli-tests/acceptance/W2-9/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[cli-**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[cli-tests/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[cli-tests/acceptance/W2-1/x.py]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[function-tests/acceptance/W2-9/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[function-**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[function-tests/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_an_independent_test_designer_may_hold_an_acceptance_path[function-tests/acceptance/W2-1/x.py]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_ticket_whose_own_role_is_the_test_designer_may_hold_an_acceptance_path` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[src/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[tests/unit/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[tests/acceptance_helpers/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[tests/acceptancex/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[docs/tests/acceptance/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[tests/unit/test_*.py]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[governance/project/audits/adoption-A5/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_pattern_that_cannot_reach_the_acceptance_folder_is_accepted_for_an_engineer[./src/widget/**]` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[success-without-verify]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_KPI_NO_VERIFY`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[failure-without-verify]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_KPI_NO_VERIFY`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[second-line-without-verify]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_KPI_NO_VERIFY`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[verify-label-and-nothing-after]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_KPI_NO_VERIFY`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[mapping-verify-tbd]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_EMPTY_CLAUSE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[mapping-verify-na]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_EMPTY_CLAUSE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[mapping-verify-none]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_EMPTY_CLAUSE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[mapping-verify-todo-dot]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_EMPTY_CLAUSE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[string-verify-tbd]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_EMPTY_CLAUSE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_kpi_line_without_a_verify_of_its_own_is_refused[failure-mapping-verify-todo]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_EMPTY_CLAUSE`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_verify_that_starts_with_a_placeholder_word_is_text_of_its_own` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |
| S7 | `test_w2_174_fields.py::test_s7_a_field_the_ticket_already_has_is_refused_never_overwritten[role]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_field_the_ticket_already_has_is_refused_never_overwritten[allowed_paths]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_field_the_ticket_already_has_is_refused_never_overwritten[kpis]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_field_the_ticket_already_has_is_refused_never_overwritten[reads]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_field_the_ticket_already_has_is_refused_never_overwritten[needs]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_field_the_ticket_already_has_is_refused_never_overwritten[waits_on]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_FIELD_SET`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_lacking_field_the_answers_do_not_supply_is_refused_unanswered[role]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_lacking_field_the_answers_do_not_supply_is_refused_unanswered[allowed_paths]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_lacking_field_the_answers_do_not_supply_is_refused_unanswered[kpis]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_lacking_field_the_answers_do_not_supply_is_refused_unanswered[reads]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_lacking_field_the_answers_do_not_supply_is_refused_unanswered[needs]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_lacking_field_the_answers_do_not_supply_is_refused_unanswered[waits_on]` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_a_named_ticket_with_nothing_answered_is_refused_unanswered` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_fields_answered_while_a_line_still_lacks_its_verify_is_refused_and_the_ticket_unmarked` | red | refused `VERIFY_PASS_UNKNOWN_LABEL`, expected `VERIFY_PASS_UNANSWERED`: a field name is no label yet (L12) |
| S7 | `test_w2_174_fields.py::test_s7_the_good_answers_apply_to_prove_the_fixture_is_not_the_cause` | red | the answers' field names are refused `VERIFY_PASS_UNKNOWN_LABEL`: the fields are not written yet (L12, L14) |

Cases per KPI line: S1 9, S2 15, S3 2, S4 36, S5 12, F1 15, F2 2, F3 5 (+1 L15), S6 11, S7 96, F4 20 (a case naming two lines counts for both).

On base for S1 to S5 and F1 to F3: the first pass's rows say red for that pass's base. At `aa717e110` those cases are green (the first ticket's code is integrated) except the five S1 list cases above. The 128 cases of the second pass are red at `aa717e110`, 0 green.
