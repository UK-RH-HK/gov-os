# W1-24 acceptance tests: `gov context`

Written before the implementation by the independent test designer (MR-3) from the ticket's KPI lines, its
`covers` ids and its sources. 34 cases in seven files. Behaviour is reached through public interfaces only: the
function `gov.context.context`, the command `gov context`, and the check declaration that
`gov check --list --json` lists. Every case builds its own project in a temporary directory; nothing reads or
writes this repository's `.gov-runtime/`.

Run: `python3 -m pytest tests/acceptance/W1-24 -q -p no:cacheprovider`

## The interface the tests fix

Several points are not in the sources. They are written against the recommended option of a decision
package (DP-1 to DP-2, in the designer's return) and marked below; a different decision changes the named
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
| S1 packet form, ceiling, hash | CAP-15.a, CAP-15.e | `test_w1_24_packet.py`: mandatory inputs by id and sha256, authority block first, ceiling, hash, supplementary separate, two runs same hash |
| S2 --brief | CAP-15.g | `test_w1_24_brief.py`: file path + summary, file under `.gov-runtime/scratch/`, summary ≤ 2.5k tokens |
| S3 token pressure, index down | CAP-15.d | `test_w1_24_pressure.py`: supplementary dropped before mandatory, records what was dropped, mandatory without lexical index, mandatory without semantic store |
| S4 mandatory resolution | CAP-15.b, CAP-01.d | `test_w1_24_mandatory.py`: resolved from declared ids, not ranked by retrieval, each lists authority/lifecycle/constraint/reason, deterministic |
| S5 BLOCKED, superseded, contradiction | CAP-15.c | `test_w1_24_blocked.py`: missing → BLOCKED, superseded → can't satisfy, conflicting at same level → contradiction |
| S6 family check | CAP-38.b | `test_w1_24_family_check.py`: check registered, required fields, same ticket+commit → same hash |
| S7 authority precedence | CAP-01.a | `test_w1_24_authority.py`: higher precedence in authority block, lower marked superseded, full order |
| command | — | `test_w1_24_command.py`: API-0002 envelope, result is the packet, BLOCKED error, deterministic, --brief |
| F1 a mandatory input is missing | — | `test_w1_24_packet.py::test_the_packet_holds_every_mandatory_input_by_id_and_sha256` (detects missing inputs); `test_w1_24_blocked.py::test_a_missing_mandatory_input_refuses_with_blocked` |
| F2 lower-precedence in authority | — | `test_w1_24_authority.py::test_the_authority_block_holds_only_the_higher_precedence_record` |

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

## Red reasons

Every test fails on import because `gov.context` does not exist (`src/gov/context/` is not built). The family
check tests fail because nothing matches `template/governance/kernel/checks/context-reproducibility*`. The command
tests fail because `src/gov/context/command.py` does not exist.

## S0a-G-07 note

Source S0a-G-07 is listed in the ticket's sources but its text is archived in `docs/source/` and was not available
to the test designer (Read deny rules). No test case is derived from a text nobody read.

## W1-07 revision

`tests/acceptance/W1-07/w1_07_support.py` is revised: `context` joins `BUILT_LATER`, leaves `NOT_BUILT`, its
ticket argument is added to `REQUIRED_ARGUMENTS`, and `READ_COMMANDS` is updated so that
`("context", "--dry-run")` includes the ticket argument.
