# W1-10 — Store and record graph: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-4yyl` (W1-10), the Contract v4
items its KPI lines name (CAP-13.a, CAP-08.a, CAP-09.a, CAP-09.b, with the acceptance lines of CAP-08, CAP-09 and
CAP-13), ADR-0002 §2.1 (L6), and DEC-012, DEC-182, DEC-221 and DEC-239. Written before implementation. Profile
STANDARD. No earlier ticket's test was rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-10 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. Nothing is installed: SQLite comes with Python.

- **Every call runs in a new Python process**, through a small driver written to a temporary directory, with this
  worktree's `src/` on `PYTHONPATH`. That gives each load its own hash seed and time zone.
- **The store is never built in this worktree.** Every project is a temporary git repository, and `load` writes
  `.gov-runtime/store.db` there.
- **Environment, built from scratch:** `PATH`, an empty temporary `HOME`, `TMPDIR`, locale, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX`. The session's `GOV_ROLE` and `GOV_TICKET` are not passed on.
- **The fixture** is twelve records (seven decisions, a requirement, a ticket, a test result, a research record, a
  lesson), three files that are not records, and five commits with fixed dates. Each record's links are in its own
  frontmatter. It is in `w1_10_support.py`, with the edges, the ACTIVE set and the trailers it must give.
- **Dev tier.** Four cases are marked `local_only`. They clone `$GOV_DEV_TIERS/a-dev` and `b-dev` (default
  `~/gov-os-workbench/synthetic/`) into a temporary directory and are skipped when the tier is absent. Deselect them
  with `-m "not local_only"`.

About seven seconds once the store exists.

## The public interface

No `gov` command belongs to this ticket: `src/gov/cli/**` is outside its `allowed_paths`, so the reserved
`gov rebuild` stays `NOT_IMPLEMENTED` and its case in `tests/acceptance/W1-07/test_w1_07_registry.py` is unchanged.
The tests call two packages. The engineer builds to exactly this:

**`gov.store`** (`src/gov/store/`)

| Function | Returns |
|---|---|
| `load(root)` | Builds `<root>/.gov-runtime/store.db` (a SQLite database) from the git repository at `root`, replacing what an earlier load left. Returns a map with at least `digest` (the store's digest) and `invalid` (a list of `{"path", "reason"}`, one per record that could not be loaded; empty when there is none). |
| `digest(root)` | The digest of the store at `root`: a sha256 in lower-case hex (64 characters) of the store's logical content. |

**`gov.records`** (`src/gov/records/`), each reading the store that `load` wrote

| Function | Returns |
|---|---|
| `records(root, type=None, status=None)` | A list of maps, one per record that matches every filter given, each with at least `id`, `type`, `status` and `path` (the record's path in the repository, with `/`). |
| `active(root, type=None)` | A list of ids: the records whose frontmatter `status` is `ACTIVE` and that nothing supersedes. |
| `edges(root, type=None, source=None, target=None)` | A list of `{"type", "source", "target"}`, one per edge that matches every filter given; each edge once. A dangling edge is included. |
| `dangling(root)` | A list of `{"type", "source", "target"}`: every reference whose `target` is the id of no record. |
| `commits(root, path=None)` | A list of `{"commit", "task", "implements"}`, one per commit of `HEAD`'s history, or per commit that changed `path`. `commit` is the full commit id; `task` and `implements` are lists of the ids in the commit's `Task:` and `Implements:` trailers. |

`root` is a `pathlib.Path`. Every return value is plain JSON data (maps, lists, strings, numbers). The tests sort
every list themselves, so its order is not part of the interface. The store's tables are not part of the interface
either: no test opens the database, beyond checking that the file is a SQLite database.

## KPI → tests → red reason today

Red run on `w1/W1-10` at `2b88df5b`: **76 errors, 0 passed, 0 failed** (76 cases, 60 test functions). Every case
errors in the `api` fixture with the same reason: **`the store and record graph do not exist: ModuleNotFoundError: No
module named 'gov.store'`**. The last column gives what each group fails on first once the two packages exist.

| KPI line | Test file | Test functions | Red reason after the modules exist |
|---|---|---|---|
| **Success 1.** Frontmatter of every record and `Implements:`/`Task:` trailers load into `.gov-runtime/store.db` deterministically (same digest twice) **[CAP-13.a]** | `test_w1_10_load.py` | `test_load_writes_the_store_as_a_sqlite_database` · `test_load_writes_nothing_in_the_project_outside_gov_runtime` · `test_the_frontmatter_of_every_record_is_loaded` · `test_a_record_carries_its_canonical_path` · `test_the_fixture_has_no_invalid_record` · `test_two_loads_give_the_same_digest` · `test_the_digest_query_returns_the_digest_of_the_load` · `test_every_commit_is_loaded` · `test_trailers_of_the_final_block_are_loaded` · `test_a_trailer_with_several_ids_gives_each_id` · `test_a_commit_before_2026_10_03_falls_back_to_the_message_body` · `test_a_commit_from_2026_10_03_is_read_from_the_final_block_only` · `test_a_commit_without_trailers_has_none` · `test_a_changed_file_returns_its_commits_with_their_trailers` · `test_the_trailers_of_a_file_resolve_to_records` · `test_a_file_no_commit_changed_has_no_commits` | No load: no store file, no records, no commits |
| **Success 2.** Queries return the exact ACTIVE set, IMPLEMENTS/VALIDATES/SUPERSEDES/DEPENDS_ON edges and dangling references by id **[CAP-08.a, CAP-09.b]** | `test_w1_10_queries.py` | ACTIVE set: `test_the_active_decisions_are_exactly_those_active_and_not_superseded` · `test_a_record_another_record_supersedes_is_not_active` · `test_a_record_that_names_its_own_successor_is_not_active` · `test_the_active_set_without_a_type_covers_every_record_type` · `test_the_active_set_of_a_type_without_active_records_is_empty`. Structured queries **[CAP-08.a]**: `test_records_by_type_and_status_are_exact` · `test_records_by_type_are_exact` · `test_records_by_status_are_exact` · `test_a_query_that_matches_nothing_returns_nothing`. Edges: `test_the_edges_of_a_type_are_exact[4]` · `test_every_implements_and_validates_edge_of_a_requirement_is_returned` · `test_the_edges_of_one_source_are_exact` · `test_a_record_without_links_has_no_edges` · `test_a_link_named_from_both_sides_is_one_edge` · `test_superseded_by_gives_a_supersedes_edge_from_the_successor`. Dangling **[CAP-09.b]**: `test_dangling_references_are_reported_by_id` · `test_a_dangling_reference_is_still_an_edge` · `test_a_reference_that_resolves_is_not_dangling` · `test_a_dangling_reference_goes_once_its_target_is_committed` · `test_a_trailer_that_names_no_record_is_reported_by_id` | No queries |
| **Success 3.** Full load of a dev tier < 5 s | `test_w1_10_dev_tier.py` | `test_a_full_load_of_a_dev_tier_takes_less_than_5_seconds[2]` · `test_a_dev_tier_loads_to_the_same_digest_twice[2]` (all `local_only`) | No load |
| **Success 4.** The graph stores all eight typed edges **[CAP-09.a]** | `test_w1_10_edges.py` | `test_the_graph_stores_the_typed_edge[8]` · `test_the_edges_between_records_are_exactly_those_of_the_frontmatter` · `test_every_edge_has_one_of_the_eight_types` · `test_an_edge_type_outside_the_eight_has_no_edges` | No edges |
| **Failure 1.** A record present in git is missing from the graph | `test_w1_10_completeness.py` | `test_every_record_of_the_fixture_is_in_the_graph` · `test_a_record_committed_later_is_in_the_graph_after_a_load` · `test_a_changed_status_is_in_the_graph_after_a_load` · `test_a_record_removed_from_git_leaves_the_graph` · `test_a_record_in_any_folder_is_in_the_graph` · `test_a_file_without_record_frontmatter_is_not_a_record` · `test_a_record_with_broken_frontmatter_is_reported_and_stops_no_other_record` · `test_a_record_without_a_required_key_is_reported_by_its_path` · `test_a_record_without_state_class_is_loaded` · `test_a_file_git_does_not_track_is_not_in_the_graph` · `test_every_committed_ticket_and_adr_of_this_repository_is_in_the_graph` (the 50 tickets and 2 ADRs of this repository, copied to a temporary repository) | No load |
| **Failure 2.** Graph content depends on file order or time | `test_w1_10_determinism.py` | `test_a_later_load_gives_the_same_digest` · `test_a_load_into_a_new_store_gives_the_same_digest` · `test_a_clone_elsewhere_gives_the_same_digest_and_content` (another path, files 400 days older, another time zone, another hash seed) · `test_the_digest_does_not_depend_on_the_hash_seed[3]` · `test_the_order_the_files_were_written_in_does_not_change_the_graph` · `test_a_store_loaded_again_after_a_commit_equals_a_new_store` · `test_the_digest_changes_when_the_content_changes[3]` | No load, no digest |

Covers ids: CAP-13.a (`test_w1_10_load.py`, the trailer tests), CAP-08.a (the ACTIVE set and structured queries),
CAP-09.a (`test_w1_10_edges.py`), CAP-09.b (the dangling tests).

**Checked that the suite can go green and catches the failure lines.** The tests were run against a throwaway
reference outside the tracked tree: 76 passed. With a digest made in set order seeded into it, 15 cases failed (the
hash-seed, clone and file-order tests among them). With a load that keeps the rows of the earlier load, 6 cases
failed (`test_a_record_removed_from_git_leaves_the_graph`, `test_a_store_loaded_again_after_a_commit_equals_a_new_store`
and the same-digest tests). The reference is not in the repository.

## Readings

1. **The store's place.** `load(root)` writes `<root>/.gov-runtime/store.db`, as the KPI names it, and the tests give
   it a temporary repository as `root`. Who may write the store in a live session is not tested (package DP-3).
2. **Trailers** (DEC-182). A commit dated before 2026-10-03 with `Task:` and `Implements:` lines in the body, outside
   the last paragraph, has those trailers. A commit dated after it with the same message has none. The fixture sets
   the author date and the commit date to the same value, far from the boundary, so the tests do not say which date
   decides or in which time zone.
3. **Several ids in one trailer.** `Implements: ADR-0001, ADR-0002` gives two ids. This is the form this repository's
   history uses (for example `Implements: DEC-199, DEC-200`).
4. **Commits.** `commits(root)` lists every commit of `HEAD`'s history, with or without trailers; `path` narrows it
   to the commits that changed that file. Merge commits and renames are not tested.
5. **ACTIVE** is the contract's sentence (CAP-08): frontmatter `status` exactly `ACTIVE`, and no SUPERSEDES edge
   points at the record. `records(status="ACTIVE")` is the frontmatter alone, so it differs from `active()` by the
   superseded records.
6. **Edges whose source is a commit** are left out by the tests of the frontmatter edges, so those tests hold
   whether or not an `Implements:` trailer is also an edge (package DP-5).
7. **`state_class`** is not required by the store: the two committed ADRs lack it (W1-08 residual) and must not be
   lost from the graph for it.
8. **The digest** changes when a status changes, an edge is added or a commit with a trailer is added. What else
   belongs to the logical content (the frontmatter's other keys, the record body) is not tested.
9. **Under five seconds** is the time of the `load` call itself, measured inside the process, on a clone of the tier.

Not tested: `owner` and free `links` filters of CAP-08.a (no KPI line names them and no committed record carries an
`owner` key); two records with one id; querying before any load; a `root` that is not a git repository; whether a
tracked file is read from the working tree or from `HEAD` (every fixture file is committed and unchanged).

## Decision packages

Each package's affected tests are written on its recommended option. Every other test holds under any option.

### DP-1 — What "every record" is, and what an invalid one does to a load

- **Question.** Which tracked files are records, and what does `load` do with a record it cannot load?
- **Why now.** KPI success 1 says "every record" and failure 1 says no record may be missing; no source says how a
  record is told from another file. This repository shows the cases: 50 tickets and 2 ADRs carry `id`, `type` and
  `status`; the charter, the contract and the plan carry `id` and `status` but no `type`; the 7 kernel templates
  carry placeholder records (`ADR-0000`); the role files carry frontmatter with no `id`; the decision register
  holds DEC entries as headings, not as files.
- **Options.**
  - (a) A record is a tracked Markdown file whose YAML frontmatter carries an `id`. With `id`, `type` and `status`
    (DEC-239) it is loaded; `state_class` is not required. A file whose frontmatter cannot be read, or that has an
    `id` but lacks `type` or `status`, is listed in `invalid` by path with a reason, and the load goes on. Untracked
    files are not records.
  - (b) Records are found by folder, from the path map's namespaces or a fixed list (`.tickets/`, `docs/adr/`,
    `docs/lessons/`).
  - (c) As (a), but any invalid record fails the whole load with a GovError.
- **Impact.** Under (a) the charter, the contract and the plan are reported as invalid until they get a `type`, and
  the seven templates load as records with placeholder ids; both want a follow-up (give the three a `type`; leave
  `template/**` out, or mark templates). Under (b) a record in a new folder is silently missing, which is failure
  line 1. Under (c) one bad file takes the graph away from every later command.
- **Reversibility.** High: a rule inside `load`.
- **Cost.** (a) and (c) about the same; (b) needs the path map read here.
- **Recommendation.** (a). **Confidence:** medium.
- **Tests that depend on it:** `test_a_record_in_any_folder_is_in_the_graph`,
  `test_a_file_without_record_frontmatter_is_not_a_record`,
  `test_a_record_with_broken_frontmatter_is_reported_and_stops_no_other_record`,
  `test_a_record_without_a_required_key_is_reported_by_its_path`, `test_a_record_without_state_class_is_loaded`,
  `test_a_file_git_does_not_track_is_not_in_the_graph`, `test_the_fixture_has_no_invalid_record`, and the `invalid`
  key of `load`.
- **Left open inside it:** whether the DEC entries of `docs/DECISION_REGISTER.md` become records (today every
  `DEC-…` reference of an ADR or a trailer would be dangling); whether templates are records; two files with one id.

### DP-2 — The public interface

- **Question.** Is the Python interface above the one the engineer builds, with `gov rebuild` left reserved?
- **Why now.** The tests need an entry point and the ticket's paths exclude `src/gov/cli/**`.
- **Options.** (a) The seven functions above; a later ticket wires `gov rebuild` to `load` and revises its registry
  case (DEC-190). (b) Add `src/gov/cli/**` to this ticket and test through `gov rebuild` and a query command.
- **Impact.** (a) keeps the ticket's paths; W1-17 and W1-20 call the functions. (b) changes `allowed_paths`, adds a
  command surface no source defines, and revises W1-07's registry case now.
- **Reversibility.** High for (a): a command can wrap the functions later.
- **Cost.** (a) none beyond the ticket; (b) about 60 lines and a new batch of tests.
- **Recommendation.** (a). **Confidence:** high.
- **Tests that depend on it:** all, through `w1_10_support.Api`.

### DP-3 — Who writes `.gov-runtime/store.db` in a live session

- **Question.** The guard closes `.gov-runtime/` outside `scratch/` to worker roles. Which role runs the load in a
  live session, and by what path?
- **Why now.** Later tickets (W1-17, W1-20, W1-24) read the store in worker sessions.
- **Options.** (a) Only the orchestrator, or `gov` run by it, writes the store. (b) `gov` commands may write
  `.gov-runtime/store.db` for any role, as a declared act path. (c) Workers build their own copy under `scratch/`.
- **Impact.** No test here depends on it: every store is built in a temporary repository.
- **Recommendation.** None; returned as a question. **Confidence:** not applicable.

### DP-4 — What the digest covers

- **Question.** Is "the same digest twice" the digest of the store's logical content, or of the file's bytes?
- **Why now.** KPI success 1 and failure 2.
- **Options.** (a) Logical content: records, edges, commits and trailers, in a fixed order. (b) The bytes of
  `store.db`.
- **Impact.** (b) ties the digest to SQLite's page layout and version, and W1-17 adds FTS5 and vector tables to
  the same file; (a) stays stable across them.
- **Reversibility.** High. **Cost.** Equal.
- **Recommendation.** (a). **Confidence:** high.
- **Tests that depend on it:** none would fail under (b) if the bytes are in fact stable; the tests never read the
  file's bytes. `digest(root)` being a sha256 in hex is fixed by the interface.

### DP-5 — The source of each edge, and trailers in the graph

- **Question.** Which frontmatter key gives each of the eight edges, in which direction, and are trailers edges?
- **Why now.** KPI success 4 and CAP-09.a name the eight types; DEC-012 names only `supersedes`, `superseded_by`,
  `depends_on`, `implements` and `constrains`. CAP-09's acceptance names VALIDATES. Framework §11.2 is archived.
- **Options.**
  - (a) Each edge's key is its name in lower case (`evidence_for`, `constrains`, `implements`, `tests`,
    `generates`, `validates`, `supersedes`, `depends_on`), from the record that carries the key to each id listed.
    `superseded_by` gives the same SUPERSEDES edge from the successor, stored once. Other keys (`consumers`,
    `decisions`, `deps`) give no edge. Trailers are returned by `commits()`; a trailer id that names no record is
    also in `dangling()`.
  - (b) As (a), and each `Implements:` trailer is also an IMPLEMENTS edge from the commit to the record.
  - (c) A product-spec worker reads the archived Framework §11.2 (DEC-222) for the mapping first.
- **Impact.** The tests of the frontmatter edges hold under (a) and (b). Under (c) the four keys DEC-012 does not
  name may change.
- **Reversibility.** Medium: records written with these keys would need rewriting if the names change.
- **Cost.** (a) and (b) equal; (c) one product-spec batch.
- **Recommendation.** (a). **Confidence:** medium (high for the five keys of DEC-012, medium for the other four).
- **Tests that depend on it:** `test_the_graph_stores_the_typed_edge[EVIDENCE_FOR]`, `[TESTS]`, `[GENERATES]`,
  `[VALIDATES]`; `test_the_edges_between_records_are_exactly_those_of_the_frontmatter`;
  `test_every_edge_has_one_of_the_eight_types`; `test_the_edges_of_a_type_are_exact[VALIDATES]`;
  `test_every_implements_and_validates_edge_of_a_requirement_is_returned`;
  `test_dangling_references_are_reported_by_id`; `test_a_record_that_names_its_own_successor_is_not_active`;
  `test_superseded_by_gives_a_supersedes_edge_from_the_successor`; `test_a_link_named_from_both_sides_is_one_edge`;
  `test_a_trailer_that_names_no_record_is_reported_by_id`.
- **Left open inside it:** a ticket's `depends_on` holds WBS ids (`W1-07`) while a ticket's `id` is the tk id, so
  those DEPENDS_ON edges are dangling in this repository until ids are resolved through `wbs_id`, or `deps` is the
  source for tickets. `Task:` values such as `decision-record` and `owner-prompt`, and `Implements:` values such as
  `CAP-58.a`, name no record and would all be dangling.

### DP-6 — Which dev tier, and what is timed

- **Question.** Does "a dev tier" mean each tier under `GOV_DEV_TIERS`, and is the limit on the `load` call?
- **Options.** (a) Both `a-dev` and `b-dev`, the `load` call alone timed. (b) `a-dev` only, as W1-07 does. (c) The
  whole process, with interpreter start.
- **Recommendation.** (a). **Confidence:** medium-high. The tiers are small (18 and 44 commits, about 150 files).
- **Tests that depend on it:** the four cases of `test_w1_10_dev_tier.py`.
