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

Red run on `w1/integrate` at `8f458d8`: 42 failed, 2 errors, 0 passed (44 cases, 11 test functions).

| KPI line | Test function(s) | Expected red reason today |
|---|---|---|
| **Success 1.** Implementer sessions deny Edit/Write on `tests/acceptance/**` and on `.env*`, `*.pem`, `*.key`, `config/secrets*` (one denied attempt each) | `test_implementer_write_to_acceptance_tests_is_denied` · `test_acceptance_test_deny_covers_every_depth` · `test_write_to_secret_file_is_denied` · `test_guardrails_leave_ordinary_implementer_work_alone` · `test_interim_rule_stays_in_force_once_introduced[acceptance-tests]` | `.claude/settings.json` holds only the two `docs/source` rules, so every attempt is "not denied" |
| **Success 2.** The operator diff procedure (`git diff --name-only` vs `allowed_paths` at each ticket close) is written and used from the first implementation ticket | `test_operator_diff_procedure_is_written` — covers "written". "Used" has no test: KPI dispute KD-1 | Error in the fixture: `governance/project/bootstrap.md` does not exist |
| **Success 3.** Interim install rule recorded and in force until W1-05; install commands denied in every session settings file | `test_install_command_is_denied` · `test_interim_install_rule_is_recorded` · `test_interim_rule_stays_in_force_once_introduced[installs]` | No `Bash(...)` deny rule exists; `bootstrap.md` does not exist |
| **Failure 1.** Any implementer commit touching `tests/acceptance/**` before W1-05 lands | `test_only_the_test_designer_commits_to_acceptance_tests` | The guardrail is not in force: Edit on `tests/acceptance/**` is not denied |
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
  `cargo install`, `apt` and `apt-get`. `curl | sh`, binary downloads, `sudo` and aliases are in KD-3.
- **Not over-blocking.** With the rules in place, an Edit under `src/gov/guard/`, a Write under `tests/unit/guard/`,
  `python3 -m pytest tests/unit/guard -q` and `git diff --name-only` must stay allowed.
- **`docs/source`** is checked by behaviour: Read and Edit under `docs/source/**` stay denied. The rule text may change.
- **Failure 1** treats every commit that touches `tests/acceptance/**` without the trailer
  `Role: independent-test-designer` as an implementer commit.
- **Failure 3** checks what the repository can show: the deny rule is in force, W1-06 still depends on W1-05 and is
  `open`, and `governance/project/tool-registry.yaml` does not exist. An install that leaves no record in the
  repository is beyond a deterministic test.
- **Gates.** The three failure-KPI tests and the over-blocking test first assert that W1-01's rules are in place. A
  check that only says "nothing bad has happened yet" would pass before implementation.
- **After W1-05.** The checks on `tests/acceptance/**` and on installs are interim (DEC-084). They skip once the ticket
  with `wbs_id: W1-05` has `status: closed`. The secret-file, `docs/source` and commit-history checks keep running.

## Open KPI disputes

Sent to the owner as decision packages (`~/gov-os-workbench/w1-tests/decision-packages/W1-01-kpi-disputes.md`). The
tests for these clauses are left out until they are answered.

| Id | KPI | Question |
|---|---|---|
| KD-1 | Success 2 | Which record shows the diff procedure was "used from the first implementation ticket"? |
| KD-2 | Success 3 | Does "every session settings file" include the session settings outside the repository? |
| KD-3 | Success 3 | Does the interim rule also cover `curl \| sh`, binary downloads, `sudo` and install aliases? |
| KD-4 | Success 1 | Is a recorded live denied attempt required, and where is it recorded? |
