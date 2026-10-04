# W1-01 — Interim bootstrap guardrails: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-dtv3` (W1-01) and the items it
cites: DEC-084, DEC-074 Q9, CAP-03, CAP-58. Written before implementation.

## Run

```sh
python3 -m pytest tests/acceptance/W1-01 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. The tests read
`.claude/settings.json`, `governance/project/bootstrap.md`, `.tickets/` and git history; they write nothing.

## KPI → tests → red reason today

Red run on `w1/integrate` at `b4d7ede`: 49 failed, 10 errors, 0 passed (59 cases, 16 test functions).

| KPI line | Test function(s) | Expected red reason today |
|---|---|---|
| **Success 1.** Implementer sessions deny Edit/Write on `tests/acceptance/**` and on `.env*`, `*.pem`, `*.key`, `config/secrets*` (one denied attempt each) | `test_implementer_write_to_acceptance_tests_is_denied` · `test_acceptance_test_deny_covers_every_depth` · `test_write_to_secret_file_is_denied` · `test_guardrails_leave_ordinary_implementer_work_alone` · `test_interim_rule_stays_in_force_once_introduced[acceptance-tests]` · `test_a_denied_attempt_is_recorded_for_each_path_class` (KD-4) | `.claude/settings.json` holds only the two `docs/source` rules, so every attempt is "not denied"; `bootstrap.md` does not exist, so no attempt is on record |
| **Success 2.** The operator diff procedure (`git diff --name-only` vs `allowed_paths` at each ticket close) is written and used from the first implementation ticket | `test_operator_diff_procedure_is_written` ("written") · `test_implementer_commits_stay_inside_allowed_paths` ("used", KD-1) | Error in the fixture: `governance/project/bootstrap.md` does not exist |
| **Success 3.** Interim install rule recorded and in force until W1-05; install commands denied in every session settings file | `test_install_command_is_denied` · `test_pipe_to_shell_and_sudo_are_denied` (KD-3) · `test_interim_install_rule_is_recorded` · `test_install_rule_lists_every_agent_session_settings_file` (KD-2) · `test_a_denied_install_attempt_is_recorded` (KD-4) · `test_interim_rule_stays_in_force_once_introduced[installs]` | No `Bash(...)` deny rule exists; `bootstrap.md` does not exist |
| **Failure 1.** Any implementer commit touching `tests/acceptance/**` before W1-05 lands | `test_only_the_test_designer_commits_to_acceptance_tests` · the tests of `test_w1_01_integration_merges.py` (DEC-253, see below) | The guardrail is not in force: Edit on `tests/acceptance/**` is not denied |
| **Failure 2.** An existing `docs/source` deny rule is lost | `test_docs_source_deny_rules_survive_the_change` | W1-01's rules are not in place: Edit on `.env` is not denied |
| **Failure 3.** Any install runs before W1-05 | `test_no_install_is_recorded_before_w1_05` | The interim install rule is not in force: `pip install` is not denied |

**Covers ids:** none. Contract v4 names W1-01 as a provider of CAP-03 and CAP-58 at capability level, and no `covers`
item names it; the ticket's KPI lines carry no bracketed id.

## How the tests decide "denied"

A pytest run cannot open a live harness session, so each attempt is evaluated against `permissions.deny` by the rule
model in `w1_01_support.py`. The model takes the strict reading of the rule syntax, so rules that pass here deny under
every reading:

- `Edit(<glob>)` covers Edit, Write and NotebookEdit. `Write(<glob>)` covers Write only. `Read(<glob>)` covers Read
  only. A bare tool name covers every use of the tool.
- `//x` is absolute, `~/x` is under the home directory, and `/x`, `./x` and `x` are relative to the repository root.
- `*` and `?` stay inside one path segment; `**` crosses segments. A pattern without a slash covers the root only, so
  `*.pem` does not reach `deploy/tls/server.pem`, and `**/*.pem` does.
- `Bash(<prefix>:*)` and `Bash(<prefix> *)` match the prefix alone or followed by arguments. Any other `*` matches any
  run of characters. A rule without `*` matches the exact command. A compound command is denied when one part is.

## Choices the implementer should know

- **Secret files at every depth.** `.env*`, `*.pem` and `*.key` name no directory, so the tests attempt them at the root
  and in a subdirectory. `config/secrets*` is attempted at the root only.
- **Install commands** are the package-manager installs of the pinned stack (ADR-0002 §2): `pip`, `pip3`,
  `python -m pip`, `python3 -m pip`, `uv pip`, `uv tool`, `npm install` (bare, with a package, global, and after `cd`),
  `cargo install`, `apt` and `apt-get`. By KD-3 the rule also denies `curl` or `wget` piped to `sh` or `bash`, and
  `sudo`. Plain `curl` and `wget` may be denied or allowed. Shell aliases and functions are W1-03's and are not
  attempted here.
- **Not over-blocking.** With the rules in place, an Edit under `src/gov/guard/`, a Write under `tests/unit/guard/`,
  `python3 -m pytest tests/unit/guard -q` and `git diff --name-only` must stay allowed.
- **`docs/source`** is checked by behaviour: Read and Edit under `docs/source/**` stay denied. The rule text may change.
- **Failure 1** treats every commit that touches `tests/acceptance/**` without the trailer
  `Role: independent-test-designer` as an implementer commit.
- **Failure 3** checks what the repository can show: the deny rule is in force, W1-06 still depends on W1-05 and is
  `open`, and `governance/project/tool-registry.yaml` does not exist. An install that leaves no record in the
  repository is beyond a deterministic test.
- **Gates.** The three failure-KPI tests and the over-blocking test first assert that W1-01's rules are in place, and
  the commit-history test for KD-1 first needs `bootstrap.md`. A check that only says "nothing bad has happened yet"
  would pass before implementation.
- **After W1-05.** The checks on `tests/acceptance/**` and on installs are interim (DEC-084). They skip once the ticket
  with `wbs_id: W1-05` has `status: closed`. The secret-file, `docs/source`, record and commit-history checks keep
  running.

## What `bootstrap.md` must hold

The tests read the record by section (a heading and the text under it) and by line. They prescribe no other layout.

- **Diff procedure:** one section with `git diff --name-only`, `allowed_paths` and ticket close.
- **Install rule:** one section that says install commands are denied until W1-05.
- **Session list (KD-2):** a section that says installs are denied and names every agent session folder — `w1-build`,
  `w1-tests`, `s1`, `s1a` — and the repository's own `.claude/settings.json`. The operator console acts as the owner
  and is not listed.
- **Denied attempts (KD-4):** one line per class, each holding an ISO date, the tool, the concrete path or command
  attempted, and the denial ("denied", "deny", "denial"). A table row is one line.
  - Five path classes with `Edit` or `Write`: a path under `tests/acceptance/`, a `.env*` file, a `*.pem` file, a
    `*.key` file, a `config/secrets*` file. The pattern itself (`*.pem`) does not count as a path.
  - One install command with `Bash`: a package-manager install such as `pip install requests`.

## Commit history as the record of the diff check (KD-1)

`test_implementer_commits_stay_inside_allowed_paths` reads every commit on HEAD's history up to the commit that closes
W1-05. A commit with a `Task:` trailer naming a ticket (`W1-02` or `DAEO-emkd`), and without
`Role: independent-test-designer`, may touch only that ticket's `allowed_paths` and the ticket's own file in
`.tickets/`. A `Task: W1-nn` that names no ticket fails. A commit without a `Task:` trailer is not checked.

## Integration merges (DEC-253, 2026-10-04)

Rewrite after implementation, reason "owner decision: integration merges". It was written in the test design batch
of W1-50 (`DAEO-xnbx`). One test was rewritten: `test_only_the_test_designer_commits_to_acceptance_tests`.

The first integration merge of the parallel run (DEC-235), commit `00e3d539` with `Role: orchestrator`, brought a
test-designer commit under `tests/acceptance/W1-37/`. The test listed the merge commit among the commits touching
`tests/acceptance/**` and failed, because the merge commit does not carry the test designer's role.

The rule now, in `w1_01_support.acceptance_test_offenders`:

- A commit that carries `Role: independent-test-designer` passes, as before.
- Any other non-merge commit that touches `tests/acceptance/**` is an offender, as before.
- Any other merge commit passes only when both hold:
  - every file under `tests/acceptance/` in which the merge differs from its first parent is, in the merge, exactly
    what one of its other parents holds (the same content, or absent in both);
  - every non-merge commit on the merged side (reachable from another parent and not from the first) that touches
    `tests/acceptance/**` carries `Role: independent-test-designer`.
- A merge commit on the merged side is judged by the same rule when the history walk reaches it.

A merge commit that holds content under `tests/acceptance/` that none of its parents holds fails. This includes a
conflict in an acceptance test resolved by hand in the merge commit, and a file that git merged from changes on both
sides. The second case is stricter than DEC-253 requires. It needs no write to the repository to check, and it fails
closed: such a merge is made by a test designer, or the owner decides.

`test_w1_01_integration_merges.py` shows both directions in small temporary repositories, and the real history:

| Case | Test | Result |
|---|---|---|
| A merge of a ticket branch with a test-designer commit and an engineer commit | `test_a_merge_of_test_designer_commits_passes` | passes |
| The merged side removes a test in a test-designer commit | `test_a_merge_that_removes_a_test_as_the_test_designer_did_passes` | passes |
| The integration branch merged into a ticket branch | `test_a_merge_of_the_integration_branch_into_a_ticket_branch_passes` | passes |
| The merge commit carries no `Role` trailer | `test_a_merge_commit_without_any_role_passes_on_the_same_terms` | passes |
| The merged side changes a test in a commit without the role (engineer, orchestrator, no role) | `test_a_merge_that_brings_a_change_from_a_commit_without_the_role_fails` | offender, and the commit is named |
| The merge commit changes or adds a test itself | `test_a_merge_that_changes_an_acceptance_test_itself_fails` · `test_a_merge_that_adds_an_acceptance_test_itself_fails` | offender |
| A conflict in a test is resolved in the merge commit | `test_a_merge_that_drops_the_merged_side_s_change_to_a_test_fails` | offender |
| A non-merge commit without the role; with the role | `test_a_non_merge_commit_without_the_role_still_fails` · `test_a_non_merge_commit_with_the_role_still_passes` | as before |
| Every merge on this repository's history that touches `tests/acceptance/**` | `test_the_integration_merges_of_this_repository_pass` | passes |

These tests build their repositories under pytest's temporary directory. They write nothing in this repository.

## Owner answers to the KPI disputes (2026-10-01)

| Id | KPI | Answer | Test |
|---|---|---|---|
| KD-1 | Success 2 | "Used" is shown by git history through `Task:` trailers | `test_implementer_commits_stay_inside_allowed_paths` |
| KD-2 | Success 3 | The record lists every agent session folder and the repository's settings; not the operator console | `test_install_rule_lists_every_agent_session_settings_file` |
| KD-3 | Success 3 | Deny `curl`/`wget` piped to a shell, `sudo` and package managers until W1-05; aliases and functions are W1-03's | `test_pipe_to_shell_and_sudo_are_denied` |
| KD-4 | Success 1 | One recorded denied attempt per class in `bootstrap.md` | `test_a_denied_attempt_is_recorded_for_each_path_class` · `test_a_denied_install_attempt_is_recorded` |

No dispute is open.
