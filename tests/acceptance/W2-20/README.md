# W2-20 — Machine-wide resource gate: acceptance tests

Written by the independent test designer (MR-3) from the KPI lines of ticket `DAEO-r30l` (W2-20, STANDARD), its
card in `docs/plan/WAVE_2_WBS.md` §2 and §0 rule 9, the list rows W2-M188, W2-M244 and W2-M262
(`docs/plan/WAVE_2_LIST.md`, `docs/plan/WAVE_2_TRIAGE.md`), and DEC-729, DEC-221, DEC-136 and DEC-732. Written before
implementation; no implementation was read. No earlier ticket's test was rewritten.
After implementation began, a fresh test designer recorded `resources` in the command list in the form of DEC-542
(`tests/acceptance/W1-07/w1_07_support.py`) and revised the lines that pin the recorded set in W1-07 and W1-32
(`Rewrite-Reason:`, DEC-491). W1-26 reads the same list, so it now also holds `resources` in `core-commands` and the skill validator.
Run 2 (a fresh test designer, after the engineer's commit): DEC-747 (delegated, staged), item 2 (P-B), a reading
of DEC-742, settles package P-1. It adds one parametrised test of the sessions boundary (3 cases), `--heavy` on the
start check, and these lines; no existing test was revised, none contradicts the decision (`Rewrite-Reason:`).

## Run

```sh
PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/acceptance/W2-20 -q -p no:cacheprovider -rs
```

Standard library and `pytest` only. No network, no dev tier, nothing installed. About 10 seconds.

- **The code under test (DEC-732).** Every command runs as `python3 -m gov.cli.main resources ...` with `PYTHONPATH`
  set to the `src/` folder of the working tree that holds this suite (`w2_20_support.SRC`, computed from the file's
  own location), so in the W2-20 worktree it runs `/home/usain/gov-os-worktrees/W2-20/src`.
  `test_the_suite_runs_this_worktrees_code` checks that `gov.__file__` points there. Bytecode is not written
  (`PYTHONDONTWRITEBYTECODE=1`).
- **The real `~/.gov-os/` is never touched.** Every command runs with an environment built from scratch: `PATH`, a
  temporary `HOME`, `TMPDIR`, locale, `PYTHONPATH` and the three reading variables below. The session's `GOV_ROLE`
  and `GOV_TICKET` are not passed on. Before a test enters its first session, the suite reads the registry folder the
  command names and fails if it is not inside that test's temporary home.
- **No real machine state.** Every reading comes from a file the test writes; repositories are temporary git
  repositories built from scratch (one commit); "live" and "dead" sessions are child processes the test starts and
  stops itself (`python3 -c "time.sleep(600)"`, killed and reaped). Children are killed at the end of every test.

## The public interface these tests define

### The command

| Invocation | What it does | Exit |
|---|---|---|
| `gov resources [--json] [--root R]` | The reading: memory, load, processors, the live sessions of the machine-wide registry, the thresholds, and the gate. Clears stale entries. | 0, whether the gate is open or shut |
| `gov resources --check [--heavy] [--json] [--root R]` | **The start check**, the gate a session start consults before it starts anything. It is asked for the start of one session: a light one (no `--heavy`, the start of a session told nothing about weight) adds 1 to the weighted count, a heavy one (`--heavy`) adds 2 (DEC-747). | 0 and `ok: true` (the reading as `result`) when open; when shut, `ok: false`, `error.code` `RESOURCE_GATE_SHUT`, the reading in `error.details`, and an exit code other than 0 and 2 (a code the command declares, 3–255, or 1). The same exit code without `--json`, and the text names the broken condition. |
| `gov resources --register PID --ticket ID --session-role ROLE [--heavy] [--root R]` | Enters a session in the machine-wide registry: its process id, its repository (the project root, `--root` or the working directory), its ticket, its role, and whether it is heavy. | 0, `ok: true` |

`--session-role` is used because `--role` is already one of `gov`'s own options. **The start check chosen is
`gov resources --check`**: the launcher (`src/gov/launch/launcher.py`, `command.py`) is W2-21's, whose KPI is that the
launch "passes the resource gate"; it may call this check, or the same gate in `src/gov/launch/gate*`. No test runs
`gov launch` or starts a real session. **A heavy start is asked with `--check --heavy`**, the same flag that enters a
heavy session with `--register` (DEC-747 needs the start check to know the new session's weight). `--heavy` with
neither `--check` nor `--register` is not part of this interface.

### The reading (`result`, or `error.details` of a refused start check)

| Key | Meaning |
|---|---|
| `registry` | Absolute path of the registry folder: `$HOME/.gov-os/machine/` or a folder inside it. |
| `available_memory_bytes` | `MemAvailable` in bytes, or `null` when it cannot be read. |
| `load_1m` | The 1-minute load average, or `null` when it cannot be read. |
| `nproc` | The processor count. |
| `sessions` | The live sessions: objects with `pid` (int), `repository` (absolute path), `ticket`, `role`, `heavy` (bool). |
| `weighted_sessions` | The weighted count of live sessions: a light session counts 1, a heavy one 2. |
| `cleared` | The stale entries this read removed from the registry, same shape as `sessions`; `[]` when none. |
| `thresholds` | `{min_available_memory_bytes, max_load_1m, max_weighted_sessions}` in force. |
| `gate` | `{open: bool, reasons: [{condition, reading, threshold}]}`; `condition` is `memory`, `load` or `sessions`; `reasons` is `[]` when open. |

### The gate

Open only when all hold; each broken condition is one reason with its reading and its threshold:

- **memory:** `available_memory_bytes >= min_available_memory_bytes` ("at least": exactly at the minimum **opens**);
- **load:** `load_1m < max_load_1m` ("below": exactly at the limit **shuts**);
- **sessions** (DEC-742 "at most 8", read by DEC-747 (delegated, staged): it holds after the start):
  - **in the reading** (`gov resources` without `--check`): `weighted_sessions < max_weighted_sessions`, room for at
    least a light session. Exactly at the maximum **shuts**. A `sessions` reason carries `reading` =
    `weighted_sessions` (the live count) and `threshold` = `max_weighted_sessions`: 8 of 8 is `(8, 8)`.
  - **in the start check**: `weighted_sessions + weight ≤ max_weighted_sessions`, where `weight` is 1 for a light
    start and 2 for a heavy start (`--heavy`). The gate in `result` or `error.details` is this start's gate. A
    `sessions` reason carries `reading` = `weighted_sessions + weight` (the count the start would make) and
    `threshold` = `max_weighted_sessions`: a light start at 8 of 8 is `(9, 8)`, a heavy start at 7 of 8 is `(9, 8)`.
    The reading's other keys stay as in the reading: `weighted_sessions` is the live count (7 or 8 here).
  - The boundary, with DEC-742's default maximum of 8: 7, a light start opens (7 + 1 = 8); 7, a heavy start is
    refused (7 + 2 = 9); at 8 the reading is shut and a light start is refused. Elsewhere the tests use counts
    clearly within (2 of 3) or clearly over (3 of 1, 4 of 3, 9 of 8).

**Fail closed:** a reading that cannot be taken is `null` and shuts the gate with a reason whose `reading` is `null`.

### Configuration: `$HOME/.gov-os/machine/gate.json`

One JSON object, the one place the thresholds live. A key that is absent (or the file absent) takes its default,
DEC-742's values (P-W2-9, accepted by the owner on 2026-10-17; first proposed as rule 9):

| Key | Default |
|---|---|
| `min_available_memory_bytes` | `4294967296` (4 GiB) |
| `max_load_1m` | the processor count (`nproc`) |
| `max_weighted_sessions` | `8` |

### Where the readings come from

| Variable | Default | Format |
|---|---|---|
| `GOV_RESOURCES_MEMINFO` | `/proc/meminfo` | `/proc/meminfo`'s; the `MemAvailable:` line, in kB (×1024 for bytes) |
| `GOV_RESOURCES_LOADAVG` | `/proc/loadavg` | `/proc/loadavg`'s; the first field |
| `GOV_RESOURCES_NPROC` | the machine's processor count | an integer |

A missing file, a missing `MemAvailable` line, or a first field that is not a number is a reading that cannot be
taken.

### Sessions

A session is live while its process id names a running process. The registry's on-disk format is the
implementation's; the tests enter sessions only with `--register` and read them only with `gov resources`. A stale
entry is removed by the read that finds it: that read lists it under `cleared`, and a later read does not list it
again.

## KPI line and list row → tests → red reason

Red run 1 on `w2/W2-20` at `689bd17e`: **21 failed, 1 passed** (22 cases, 17 test functions). Every failing case fails
on the same reason: `gov resources` does not exist — `gov: error: argument <command>: invalid choice: 'resources'`,
exit code 2, no JSON envelope (`AssertionError: gov resources printed no JSON envelope (exit 2)`). It is raised by the
suite's first call in each test, the registry-location check. The one passing case is the DEC-732 check that the
suite runs this worktree's code.

Red run 2 (DEC-747), on `w2/W2-20` at `2ceae1e9` with the engineer's code: **2 failed, 23 passed** (25 cases, 18 test
functions). The cases the decision makes stricter than the code as built fail; the rest of the suite is green:

- `test_DEC_747_at_most_8_holds_after_the_start[7, a heavy start is refused]`: `gov resources --check --heavy` is
  refused, but not by the gate: `the refusal is not the named error RESOURCE_GATE_SHUT: {'code':
  'RESOURCE_REGISTER_INVALID', 'message': '--ticket, --session-role and --heavy go with --register', ...}`. The start
  check does not take the new session's weight.
- `test_DEC_747_at_most_8_holds_after_the_start[8, the reading shuts and a light start is refused]`: `8 of 8 leaves no
  room and must read shut: {...}` (`assert True is False`): the reading opens at the maximum (within, not below). The
  case stops there; its light start check is not reached.
- `[7, a light start opens]` passes (7 + 1 = 8 opens, as built).

| KPI line / row | File | Tests |
|---|---|---|
| **Success 1.** `gov resources` reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under `~/.gov-os/machine/`, whichever repository started it | `test_w2_20_reading.py` | `test_the_reading_reports_memory_load_processors_and_the_registry_folder` · `test_every_live_session_is_read_with_its_pid_repository_ticket_role_and_weight` · `test_the_registry_belongs_to_the_home_folder_not_to_the_repository` · (another repository: `test_a_session_entered_from_another_repository_counts_against_this_ones_gate`) |
| **Success 2.** The gate opens or shuts with a named reason | `test_w2_20_gate.py` | `test_the_gate_is_open_when_every_condition_holds` · `test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[memory, load [W2-M262], sessions]` · `test_several_broken_conditions_are_all_named` · `test_exactly_at_a_threshold[memory, load]` · `test_a_heavy_session_counts_double_and_tips_the_count_over_the_maximum[two light, two heavy]` · `test_the_proposed_defaults_are_in_force_when_nothing_is_configured` (DEC-742's defaults; the name is the first run's) · `test_a_reading_that_cannot_be_taken_never_opens_the_gate[memory, load]` · the sessions boundary, DEC-747: `test_DEC_747_at_most_8_holds_after_the_start[7, a light start opens; 7, a heavy start is refused; 8, the reading shuts and a light start is refused]` |
| **Success 3.** A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262] | `test_w2_20_stale.py` | `test_W2_M244_W2_M188_W2_M262_a_dead_pid_is_cleared_and_a_live_one_is_kept` · `test_W2_M244_W2_M188_W2_M262_a_stale_entry_does_not_count_against_the_gate` |
| **Failure.** A session in another repository counts against the gate | `test_w2_20_failure.py` | `test_a_session_entered_from_another_repository_counts_against_this_ones_gate` |
| **Failure.** A start while the gate is shut is refused with the reading | `test_w2_20_failure.py` | `test_W2_M244_W2_M188_a_start_while_the_gate_is_shut_is_refused_with_the_reading` · `test_W2_M244_the_refusal_without_json_has_the_same_exit_code_and_names_the_reason` · `test_W2_M188_a_start_while_the_gate_is_open_goes_ahead` · (fail closed: the second half of `test_a_reading_that_cannot_be_taken_never_opens_the_gate`) · (the sessions boundary: the start checks of `test_DEC_747_at_most_8_holds_after_the_start[7, a heavy start is refused; 8, the reading shuts and a light start is refused]`, refused with the reading and the `sessions` reason) |
| **W2-M188** (each rule enforced by a command or check) | | the start-check tests above, and the stale-entry tests |
| **W2-M244** (a gov command refuses to start a ticket when memory or load breaks the gate; a case shows the refusal) | | `test_W2_M244_W2_M188_a_start_while_the_gate_is_shut_is_refused_with_the_reading` (memory) · `test_W2_M244_the_refusal_without_json_has_the_same_exit_code_and_names_the_reason` (load), and the stale-entry tests |
| **W2-M262** (close's cases fail under concurrent machine load) | | `test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[load [W2-M262]]`, and the stale-entry tests |

**Count.** KPI lines with tests: 4 of 4 (3 success, 1 failure with its two halves). List rows named by a test: 3 of 3.
25 cases in 18 test functions (run 1: 22 in 17; run 2 adds the 3 cases of the sessions boundary).

**The test logic was checked** (run 1) against a throwaway stand-in kept outside the repository (never in `src/`, never
committed), driven by a temporary edit of the support module that was reverted before the commit: 22 passed; with
stale entries filtered but not removed, and with an unreadable memory reading treated as open, exactly the stale and
the fail-closed tests failed.

## Package for the orchestrator

**P-1 is decided by DEC-747 (delegated, staged), item 2 (P-B): option (a).** "At most 8" holds after the start: the
start check opens on sessions only when the weighted count of live sessions plus the new session's weight (2 when
heavy) is at most the maximum; the reading shows the gate shut when the weighted count is already at the maximum. Not
"< 8 everywhere" (a heavy start could then reach 9). DEC-742 stands, its values the defaults. The interface and the
test are above ("The gate", `test_DEC_747_at_most_8_holds_after_the_start`). The package as returned in run 1:

**P-1. Does the session limit count the session being started?** The sources say "at most 8 Gov OS sessions on the
machine" (rule 9) and "within the configured maximum" (brief). With 8 live light sessions and a maximum of 8, the gate
reading is open if it tests `weighted ≤ max`, but starting a ninth session then makes 9. Options: (a) the gate tests
the live count, `weighted ≤ max`, and the start check adds the weight of the session being started
(`weighted + weight(new) ≤ max`), which needs the start check to know whether the new session is heavy (for example
`--check --heavy`); (b) the gate opens only while there is room for one more light session (`weighted < max`, same
answer for the reading and the check); (c) `weighted ≤ max` for both, accepting up to max + 2 after a start. Impact:
which side of the boundary opens, and a possible `--heavy` on `--check`. Reversible: yes, one comparison and at most
one option, plus one boundary test. Cost: small. Recommendation: (b), the simplest that keeps "at most 8" true for
light starts, with the heavy case left to the launcher (W2-21). Confidence: medium. Until decided, no test sits on this
boundary. (Decided otherwise: the reading follows (b), the start check (a).)
