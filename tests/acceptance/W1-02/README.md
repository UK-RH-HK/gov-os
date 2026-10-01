# W1-02 — PreToolUse default-deny guard: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-emkd` (W1-02) and the Contract v4
items it cites: CAP-05, CAP-38.c, CAP-39.a, CAP-58.a, CAP-58.c. Written before implementation.

**This set is partial.** The ticket leaves five parts of the guard's interface open. Those parts are with the owner as
KPI disputes KD-1 to KD-5, and their tests are left out until they are answered. What is tested here needs none of the
five answers.

## Run

```sh
python3 -m pytest tests/acceptance/W1-02 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. Each test builds a small git project
in a temporary directory, copies the hook into it and runs the hook as a process. Nothing in the repository is written.

## KPI → tests → red reason today

Red run on `w1/integrate` at `d35c5b1`: 48 errors, 0 passed (48 cases, 10 test functions). Every case errors in the
`hook` fixture with the same reason: **no file matches `template/governance/kernel/hooks/pretooluse*`** — the guard
does not exist.

| KPI line or covers id | Test function(s) | Expected red reason today |
|---|---|---|
| **Success 1.** Edit/Write/Bash writes are allowed only inside the active ticket `allowed_paths` plus the kernel scratch set, per role [CAP-39.a, CAP-58.a] | G0 tier only: `test_guard_hook_ships_in_the_kernel_template` · `test_guard_decides_before_the_tool_runs`. **The allow-list is left out: KD-1, KD-2, KD-5** | The hook does not exist |
| **Success 2.** The engineer role is denied every write under `tests/acceptance/**`; the independent-test-designer role is allowed only there [CAP-38.c] | **Left out: KD-1** | — |
| **Success 3.** The freeze flag denies every write; the guard reads ticket frontmatter directly; decision in < 100 ms p95 | Latency only, on the path that needs no role: `test_decision_p95_is_under_100_ms`. **Freeze flag left out: KD-3. Frontmatter left out: KD-1** | The hook does not exist |
| **Success 4.** A session with no declared role, or an unknown role, is read-only: every write is denied [CAP-58.c] | No declared role: `test_role_less_session_cannot_edit_or_write` · `test_role_less_session_cannot_edit_a_notebook` · `test_role_less_session_cannot_write_through_bash` · `test_no_ticket_state_gives_a_role_less_session_write_access` · `test_role_less_session_can_still_read_with_file_tools` · `test_role_less_session_can_still_read_through_bash` · `test_deciding_leaves_the_working_tree_unchanged`. **Unknown role left out: KD-1** | The hook does not exist |
| **Failure 1.** Any write outside `allowed_paths` is allowed | **Left out: KD-1** | — |
| **Failure 2.** Guard crash or timeout lets the call through without a recorded finding | **Left out: KD-4** | — |
| **Failure 3.** A session with no or an unknown role can write anywhere | No declared role: the Success 4 tests. **Unknown role left out: KD-1** | The hook does not exist |
| **CAP-39.a** G0 guard tier | `test_guard_hook_ships_in_the_kernel_template` · `test_guard_decides_before_the_tool_runs` | The hook does not exist |
| **CAP-58.c** no or unknown role has no write privilege | The Success 4 tests (no declared role) | The hook does not exist |
| **CAP-58.a** default-deny allow-lists per role and ticket | **Left out: KD-1** | — |
| **CAP-38.c** independent test authorship | **Left out: KD-1** | — |

**Count.** KPI lines with at least one test: 4 of 7, none of them in full. Covers ids with at least one test: 2 of 4
(CAP-39.a in full, CAP-58.c for the "no role" half).

## Open KPI disputes

The decision package is `~/gov-os-workbench/w1-tests/decision-packages/W1-02-kpi-disputes.md`. In short:

| Id | Question | Blocks |
|---|---|---|
| KD-1 (P1) | How does a session declare its role and its active ticket to the guard? | Success 1, 2, 3 (frontmatter), 4 and Failure 3 (unknown role), Failure 1; CAP-58.a, CAP-38.c |
| KD-2 (P2) | Which paths are the kernel scratch set, and who may use it? | Success 1 ("plus the kernel scratch set") |
| KD-3 (P2) | Where is the freeze flag while `gov pause` (W1-28) does not exist? | Success 3 (freeze) |
| KD-4 (P2) | What is a "recorded finding", and does the guard deny or let through when it fails? | Failure 2 |
| KD-5 (P3) | Which Bash commands must the guard itself judge, and what does it do with one it cannot classify? | Success 1 (Bash), the Bash cases already here |

## How the tests drive the guard

- **Entry point.** The file matching `template/governance/kernel/hooks/pretooluse*`. If several files match, exactly one
  must be executable, and that one is run. An executable file is run directly; otherwise `.py` runs under `python3` and
  `.sh` under `bash`.
- **Where it runs.** Every matching file is copied to `governance/kernel/hooks/` of the temporary project, where Copier
  puts it in a product repository (ADR-0002 §5). The hook runs from there.
- **The `gov` package.** `src/` of this repository is on `PYTHONPATH`. That stands in for the installed package.
- **The project** is named three ways, as the harness does: the process working directory, `cwd` in the stdin object,
  and `CLAUDE_PROJECT_DIR`.
- **Stdin** is the harness's PreToolUse object: `session_id`, `transcript_path`, `cwd`, `permission_mode`,
  `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id`. File tools get absolute paths.
- **Environment.** Built from scratch: `PATH`, an empty temporary `HOME`, locale, `PYTHONPATH`, `PYTHONPYCACHEPREFIX`
  and `CLAUDE_PROJECT_DIR`. No variable of the calling session is passed on, so no role is declared by any channel.
- **Decision** (register DEC-025):
  - *denied* — exit code 2, or exit code 0 with `hookSpecificOutput.permissionDecision` = `deny` on stdout;
  - *let through* — exit code 0 with no `deny` and no `ask`;
  - any other exit code is a hook error, which the harness lets through. It counts as neither, so it fails both kinds of
    test.

## Choices the implementer should know

- **A ticket is not a role declaration.** The project's ticket is `in_progress` for the engineer role, and the session
  declares no role. Writes inside that ticket's `allowed_paths` are still denied. The same holds with no `.tickets/`
  directory, with the ticket `open`, and with two tickets in progress.
- **Write tools.** Edit, Write and NotebookEdit.
- **Bash writes tested** (the plain forms; KD-5 asks about the rest): `>`, `>>`, `| tee`, `touch`, `rm`, `mv`, `cp`,
  `mkdir -p`, `sed -i`, each with a relative target, plus `cd <dir> && … >` and absolute targets.
- **Reads stay open.** For a role-less session, Read, Grep and Glob, and the Bash commands `ls -la`, `cat README.md`
  and `git status --porcelain`, are let through. A guard that denies everything fails.
- **No trace in git.** After the guard's decisions `git status --porcelain` of the project is empty. `.gov-runtime/` is
  ignored in the project, so the guard may write there.
- **Latency.** The time measured is the wall-clock time of the hook process, start to exit, which is what the harness
  waits for. p95 over 40 calls after 3 warm-up calls; a round that misses 100 ms is repeated, up to three rounds. Today
  it times the "no role → deny" decision. The decision that reads a ticket's frontmatter is added with KD-1.
