# W1-24 acceptance tests: `gov context`

Written before the implementation by the independent test designer (MR-3) from the ticket's KPI lines, its
`covers` ids and its sources. **54 cases** (34 original + 1 revision + 19 new) in **eight files**. Behaviour is
reached through public interfaces only: the function `gov.context.context`, the command `gov context`, and the
check declaration that `gov check --list --json` lists. Every case builds its own project in a temporary
directory; nothing reads or writes this repository's `.gov-runtime/`.

Run: `python3 -m pytest tests/acceptance/W1-24 -q -p no:cacheprovider`

## The interface the tests fix

Several points are not in the sources. They are written against the recommended option of a decision
package (DP-1 to DP-5, in the designer's return) and marked below; a different decision changes the named
constant in `w1_24_support.py` or the named cases, not the rest.

### Python

    gov.context.context(root, ticket, *, brief=False, budget=None) -> dict

* `root`: the project. The call only reads: it loads no store, makes no `.gov-runtime/`.
* `ticket`: the ticket id (a string). The function resolves the ticket's declared ids (from `sources`,
  `depends_on`, `deps`) against the record store.
* `brief`: when true, writes a brief file under `.gov-runtime/scratch/` and returns `{path, summary}` instead
  of the full packet.
* `budget`: the token ceiling; `None` is the default (~6k tokens, DEC-004).

### The packet (DP-1)

| key | value |
|---|---|
| `ticket` | the ticket id (string) |
| `authority` | list, highest-precedence records first. Each: `id`, `sha256`, `authority` (tier name), `lifecycle` (status), `constraint` (version or sha256), `reason` |
| `mandatory` | list of every mandatory input, same fields as authority. Ordered by precedence |
| `supplementary` | list of supplementary context from retrieval, if room and if the index is available |
| `dropped` | list of what was not included (supplementary items dropped under pressure, or records excluded) |
| `hash` | sha256 of the packet's content (the same ticket and commit give the same hash, CAP-38.b) |
| `tokens` | total token count of the packet |
| `budget` | `{limit, used}`: the ceiling and the token count |

### Token counting (DEC-083)

`ceil(len(text) / 4)` — the same rule as `gov.retrieval.retrieve._tokens`. No tokenizer (DEC-083).

### Precedence tiers (CAP-01.a)

Charter → Contract → ADRs → specifications → tasks → retrieval → inference. Record type maps:
`charter` → Charter, `contract` → Contract, `decision` → ADR, `specification` → specification, `ticket` → task.

### Command (`src/gov/context/command.py`, DEC-317)

    gov context [--json] [--root <dir>] [--brief] [--dry-run] [--budget <N>] <ticket>

The API-0002 envelope with the packet as `result`. Exit 0 with a packet; exit 1 with `ok: false` and
`error.code` for a governance error (`BLOCKED` for a missing mandatory input, `CONTRADICTION` for conflicting
inputs at the same precedence level). `--dry-run` computes the packet without writing.

## KPI lines and covers ids

| KPI line | covers | cases |
|---|---|---|
| S1 packet form, ceiling, hash | CAP-15.a, CAP-15.e | `test_w1_24_packet.py` (8): mandatory inputs by id and sha256, authority block first, ceiling, hash, hash stability, supplementary separate, **token count consistent with ceil(len/4)**, **custom budget overrides default** |
| S2 --brief | CAP-15.g | `test_w1_24_brief.py` (5): file path + summary, file under `.gov-runtime/scratch/`, summary ≤ 2.5k tokens, **hostile ticket id cannot escape scratch**, **brief writes nothing outside the brief file** |
| S3 token pressure, index down | CAP-15.d | `test_w1_24_pressure.py` (4): supplementary dropped before mandatory, records what was dropped, mandatory without lexical index, mandatory without semantic store |
| S4 mandatory resolution | CAP-15.b, CAP-01.d | `test_w1_24_mandatory.py` (9): resolved from declared ids, not ranked by retrieval, each lists authority/lifecycle/constraint/reason, deterministic, **depends_on ids are resolved**, **precedence not overridden by retrieval rank (all 5 levels)** |
| S5 BLOCKED, superseded, contradiction | CAP-15.c | `test_w1_24_blocked.py` (6): missing → BLOCKED, superseded → can't satisfy, **R1: conflicting with supersession → BLOCKED** (revised from BLOCKED|CONTRADICTION), **BLOCKED error names the superseded record**, **multi-superseder → BLOCKED**, **pure contradiction without supersession → CONTRADICTION** |
| S6 family check | CAP-38.b | `test_w1_24_family_check.py` (8): check registered, required fields, same ticket+commit → same hash, **check command is runnable**, **same hash across separate processes and directories**, **all computations fail → unmeasured and not green**, **some computations fail → each failure named and not green**, **no tickets → unmeasured and not green** |
| S7 authority precedence | CAP-01.a | `test_w1_24_authority.py` (4): higher precedence in authority block, lower marked superseded, full order (3 levels), **all five store-representable levels in order** |
| supplementary | CAP-15.d | `test_w1_24_supplementary.py` (3): **supplementary non-empty with a built index**, **supplementary dropped before mandatory under pressure**, **packet indicates supplementary unavailable without index** |
| command | — | `test_w1_24_command.py` (7): API-0002 envelope, result is the packet, BLOCKED error, deterministic, --brief, **--dry-run computes without writing**, **--budget sets the limit** |
| F1 a mandatory input is missing | — | `test_w1_24_packet.py::test_the_packet_holds_every_mandatory_input_by_id_and_sha256` (detects missing inputs); `test_w1_24_blocked.py::test_a_missing_mandatory_input_refuses_with_blocked` |
| F2 lower-precedence in authority | — | `test_w1_24_authority.py::test_the_authority_block_holds_only_the_higher_precedence_record` |

Items in **bold** are new or revised in this deepening round.

## Decision packages

### DP-1: the public interface and the form of the packet

The ticket's sources, the contract items and the existing command modules fix what the command takes and returns,
but not every key name. The tests hold the names in constants in `w1_24_support.py` (the block starting at
`K_TICKET`). A different choice of names changes those constants, not the tests.

The Python function is assumed to be `gov.context.context(root, ticket, *, brief=False, budget=None)`. If the
function name or signature is different, change the `CONTEXT` and `FUNCTION` constants.

### DP-2: BLOCKED vs. exit code 4

The tests assume a missing mandatory input raises `GovError("BLOCKED", ...)` with exit code 1 (a governance
error). API-0002 defines exit code 4 as "blocked by control state (pause/freeze) or human gate." If BLOCKED for a
missing mandatory input should use exit code 4 instead, the test assertions in `test_w1_24_blocked.py` and
`test_w1_24_command.py` need to be updated.

**Recommendation**: exit code 1 (governance error). Exit 4 is for control-plane blocking (pause/freeze), not for
a data-plane missing record. Confidence: high (the code in `src/gov/cli/main.py` line 226 already gates exit
codes through `command.exit_codes`; unless the `context` command declares `4` in its `EXIT_CODES`, it will map
to 1).

### DP-3: supplementary context integration

How `gov.context` queries `gov.retrieval.retrieve.retrieve` for supplementary context is not fully specified. The
tests in `test_w1_24_supplementary.py` verify that supplementary context appears when the index is built, that it
is dropped first under pressure, and that its absence is indicated — but the query text and the mapping from
retrieval bundles to supplementary entries are not tested.

**Recommendation**: the implementation decides the query (likely the ticket title or its sources' text). The tests
will pass as long as the contract (non-empty with index, dropped before mandatory, indicated when absent) holds.

### DP-4: index unavailable indication

When the lexical index is not built, the packet's supplementary list is empty. The tests check that the packet
indicates why (via a `dropped` entry, a `facets` field, or some other mechanism). The exact indicator is not
specified.

**Recommendation**: a `dropped` entry with a reason like `"index unavailable"`. The test is flexible enough to
pass with any of several indicators.

### DP-5: --dry-run semantics

`--dry-run` is listed in the command signature (CAP-27, W1-07's `READ_COMMANDS`) but its semantics for `context`
are not fully specified beyond "compute without writing." The test verifies that `--dry-run --brief` produces a
valid envelope with a summary but does not write the brief file.

**Recommendation**: `--dry-run` computes the packet (or brief summary) and returns it without writing any files.
Confidence: high.

## Rewrites

### R1: `test_conflicting_inputs_at_the_same_level_raise_a_contradiction`

**File**: `test_w1_24_blocked.py`
**Change**: assert `BLOCKED` only (was `BLOCKED` or `CONTRADICTION`).
**Reason**: the fixture's `ADR_CONFLICT_2` has `supersedes: [ADR_CONFLICT_1]`, which makes `ADR_CONFLICT_1`
superseded. This is a supersession, not a contradiction — the error should be `BLOCKED`. The new test
`test_two_active_records_at_the_same_level_without_supersession_raise_contradiction` covers the genuine
contradiction case with two ACTIVE records and no supersession edge.

## Red reasons

Every test fails on import because `gov.context` does not exist (`src/gov/context/` is not built). The family
check tests fail because nothing matches `template/governance/kernel/checks/context-reproducibility*`. The command
tests fail because `src/gov/context/command.py` does not exist. The supplementary context tests that need an
index skip when `gitleaks` is not on PATH.

## S0a-G-07 note

Source S0a-G-07 is listed in the ticket's sources but its text is archived in `docs/source/` and was not available
to the test designer (Read deny rules). No test case is derived from a text nobody read.

## W1-07 revision

`tests/acceptance/W1-07/w1_07_support.py` is revised: `context` joins `BUILT_LATER`, leaves `NOT_BUILT`, its
ticket argument is added to `REQUIRED_ARGUMENTS`, and `READ_COMMANDS` is updated so that
`("context", "--dry-run")` includes the ticket argument.

## G-07 coverage

Source S0a-G-07 text: "`gov context`: authority block first, supplementary block, token ceiling, sha256, file-path delivery + ≤ 2.5k-token summary". Six parts:

1. **authority block first** — `test_w1_24_packet.py::test_the_authority_block_is_first_in_the_packet` (S1)
2. **supplementary block** — `test_w1_24_supplementary.py::test_supplementary_context_is_non_empty_with_a_built_index` and `test_w1_24_packet.py::test_the_supplementary_block_is_separate_from_the_authority_block` (S1, supplementary)
3. **token ceiling** — `test_w1_24_packet.py::test_the_packet_stays_under_the_default_ceiling` (S1)
4. **sha256** — `test_w1_24_packet.py::test_the_packet_carries_its_own_hash` and `test_w1_24_packet.py::test_the_packet_holds_every_mandatory_input_by_id_and_sha256` (S1)
5. **file-path delivery** — `test_w1_24_brief.py::test_brief_delivers_a_file_path_and_a_summary` (S2)
6. **≤ 2.5k-token summary** — `test_w1_24_brief.py::test_the_brief_summary_is_at_most_2500_tokens` (S2)

## Sources that stand, files that cannot be read, a lookup that fails (the follow-up after W1-41, piece 11)

Added by a fresh Independent Test Designer on ticket `DAEO-2lwj` (W1-30, reopened; DEC-569), before any
code. Sources: DEC-552 (finding 10 goes to the follow-up; finding 6 for "stands"), DEC-568, and the W1-41
section of the bootstrap ("`RETIRED` and `REJECTED` records satisfy a mandatory source in the context
(only `SUPERSEDED` blocks); a mandatory record whose file cannot be read gets the hash of empty bytes and
counts 0 tokens, so the packet presents it as read; any retrieval failure in the supplementary lookup
becomes "index unavailable""). File: `test_w1_24_standing_sources.py`, 16 cases. No case of the suite was
rewritten; `w1_24_support.py` is unchanged. Finding 9 is in W1-41's suite, which holds the external
references.

### As settled here (each proposed; a decision may replace it)

1. **Only a record that stands satisfies a mandatory source.** "Stands" is DEC-552's finding 6 as
   DEC-568 gives it: a record stands unless its status says it no longer does, and the statuses that say
   so are `SUPERSEDED`, `RETIRED` and `REJECTED`. `ACTIVE`, `ACCEPTED`, `PROPOSED`, `DRAFT`, `DEPRECATED`
   and a status the kernel does not know still stand and satisfy, as today. The status is compared as it
   is compared today (the word in capitals); a record superseded by an edge alone is treated as today.
2. **The refusal** is `BLOCKED`, and its message names the record and the status word (`RETIRED`,
   `REJECTED`), as it names a superseded record today.
3. **A mandatory record whose file cannot be read** (deleted from the working tree, a folder in its
   place, no permission to read) is `BLOCKED`; the message names the file's path, and the refusal names
   the record. No packet is built.
4. **A failure of the supplementary lookup** leaves the packet built with no supplementary context and
   an entry under `dropped` whose reason says what failed, in that failure's own words. The reason
   holds the words "index unavailable" only where the index is what is unavailable. Two causes give two
   statements, and so two packet hashes.

### Cases and why each is red (at `85066f4e`)

| Case | Holds | Today |
|---|---|---|
| `test_a_source_that_no_longer_stands_does_not_satisfy_and_is_named_with_its_status` (2: `RETIRED`, `REJECTED`) | settlements 1 and 2 | red, both: "a RETIRED record satisfied a mandatory source: the context was built" |
| `test_a_superseded_source_is_refused_and_named_with_its_status_as_today` | the form the two above take | **green**: holds what stays |
| `test_a_source_that_stands_satisfies` (6: `ACTIVE`, `ACCEPTED`, `PROPOSED`, `DRAFT`, `DEPRECATED`, an unknown status) | settlement 1, the other side | **green**, each: holds what stays |
| `test_a_mandatory_record_whose_file_cannot_be_read_is_refused_and_the_file_is_named` (3: deleted, a folder in its place, no permission to read) | settlement 3 | red, each: "the packet presents ADR-W24-STAND as read, with the hash of empty bytes" |
| `test_a_mandatory_record_that_is_read_has_the_hash_of_its_file` | the hash of the file, not of empty bytes | **green**: holds what stays |
| `test_a_lookup_that_fails_on_a_file_it_cannot_read_says_so_and_not_that_the_index_is_unavailable` | settlement 4: the index answers, a file it names cannot be read; the reason names that file | red: "a file that cannot be read is reported as an index that is unavailable" |
| `test_a_lookup_that_fails_on_a_damaged_index_says_that_the_index_is_unavailable` | settlement 4, the failure that is an unavailable index (its table is gone) | **green**: holds what stays |
| `test_the_two_failures_give_two_packets` | two causes, two statements, two hashes | red: both say "index unavailable" |

7 red, 9 green. Run: `env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-24 -q -p no:cacheprovider -rs`:
70 cases, 63 passed, 7 failed, none skipped, 23 s.

The three cases of the lookup build a lexical index and skip without `gitleaks` on PATH, as the suite's
other cases of the supplementary context do. The three cases that take a permission away skip for a
user that permissions do not hold (root). The damaged index is made by removing one table of the
index from the project's runtime store; if the index moves, that fixture step moves with it.

### Names proposed

None new. `BLOCKED` and the `dropped` entry with its `reason` are today's; the words of a reason other
than "index unavailable" are the failure's own and are not fixed, beyond naming the file that could not
be read.

### Packages

**P-11.2. An index that was never built says nothing.**
- *Question.* In a project with no lexical index the packet has no supplementary context and an empty
  `dropped` list: nothing says why. Should it say "index unavailable"?
- *Why now.* DP-4 of this suite asked for the indicator; its case
  (`test_the_packet_indicates_supplementary_is_unavailable_when_the_index_is_down`) passes on an empty
  list because its last condition is always true. The follow-up orders the wording of a *failure*; a
  lookup that answers "no index" is not one, so no case here changes it.
- *Options.* (a) Leave it. (b) The packet says "index unavailable" under `dropped`; every packet of a
  project without an index then changes its hash once, and the vacuous case is rewritten to hold it.
- *Impact.* (b) changes the packet hash that close records of index-less projects hold.
- *Reversibility.* High. *Cost.* (b) two lines and one rewrite.
- *Recommendation.* (b), in its own step. *Confidence:* medium.

**P-11.3. Status words in another letter case.** `superseded`, `Retired` and `rejected` satisfy a
mandatory source today and after this piece, because the comparison is with the word in capitals.
Options: (a) leave; (b) compare without regard to case. Recommendation (b), stricter, in the same
change if the lead agrees; no case holds either. *Confidence:* medium.

