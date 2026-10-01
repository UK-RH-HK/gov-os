# Interim bootstrap guardrails

This file records the interim guardrails in force during Wave 1 bootstrap (DEC-084). It holds until W1-02, W1-03 and W1-04 pass their acceptance tests and W1-05 closes.

## Settings deny rules

The repository's `.claude/settings.json` carries the following `permissions.deny` rules:

- `Edit(tests/acceptance/**)` — denies Edit/Write on acceptance tests at every depth
- `Edit(**/.env*)` — denies Edit/Write on `.env*` files at every depth
- `Edit(**/*.pem)` — denies Edit/Write on `*.pem` files at every depth
- `Edit(**/*.key)` — denies Edit/Write on `*.key` files at every depth
- `Edit(config/secrets*)` — denies Edit/Write on `config/secrets*`
- `Bash(pip:*)`, `Bash(pip3:*)`, `Bash(python -m pip:*)`, `Bash(python3 -m pip:*)` — deny pip installs
- `Bash(uv:*)` — denies uv commands
- `Bash(npm install:*)` — denies npm install
- `Bash(cargo install:*)` — denies cargo install
- `Bash(apt:*)`, `Bash(apt-get:*)` — deny system package installs
- `Bash(sudo:*)` — denies sudo
- `Bash(curl:*)`, `Bash(wget:*)` — deny curl and wget
- `Read(./docs/source/**)`, `Edit(./docs/source/**)` — deny access to source documents (pre-existing)

## Operator diff procedure

At each ticket close, the operator runs `git diff --name-only <base>..<head>` and checks the changed files against the ticket's `allowed_paths`. This procedure is used from the first implementation ticket. The record that it was used is git history through `Task:` trailers (DEC-097). A commit without a `Task:` trailer is not checked (known limit).

## Interim install rule

Install commands are denied in all agent sessions until W1-05 closes (DEC-083, DEC-099). No tool is installed before W1-05. W1-06 (first install) depends on W1-05.

The install deny rules are carried in each session's `.claude/settings.json`:

| Session | Install deny rules | Verified |
|---|---|---|
| Repository `.claude/settings.json` | `pip`, `pip3`, `python -m pip`, `python3 -m pip`, `uv`, `npm install`, `cargo install`, `apt`, `apt-get`, `sudo`, `curl`, `wget` | Written by W1-01, 2026-10-01 |
| `w1-build` | `sudo`, `apt`, `apt-get`, `snap`, `npm install\|i\|add`, `npx`, `pip install`, `pip3 install`, `python3 -m pip`, `uv pip\|tool\|add`, `cargo install`, `curl`, `wget`, `docker` | Read 2026-10-01 |
| `w1-tests` | Owner-maintained (DEC-098); not readable from the build session | Stated by owner (DEC-098) |
| `s1` | `sudo`, `npm`, `npx`, `pip install`, `uv`, `cargo`, `curl`, `wget`, `gh`, `docker` | Read 2026-10-01. Gap: does not name `pip3 install`, `python3 -m pip`, `apt`, `apt-get`; reported to owner |
| `s1a` | `sudo`, `npm`, `npx`, `pip install`, `uv`, `cargo`, `curl`, `wget`, `gh`, `docker` | Read 2026-10-01. Gap: does not name `pip3 install`, `python3 -m pip`, `apt`, `apt-get`; reported to owner |

The operator console is not listed; it acts as the owner.

## Denied attempts

One attempt per class (DEC-100), made in a headless session started in the repository root, where `.claude/settings.json` applies. The session ran in `acceptEdits` mode with `Write` and `pip install` allowed, so each refusal comes from a deny rule. No file was created.

| Date | Tool | Attempt | Result |
|---|---|---|---|
| 2026-10-01 | Write | `tests/acceptance/W1-01/denied_attempt_probe.txt` | denied by `Edit(tests/acceptance/**)` |
| 2026-10-01 | Write | `.env.probe` | denied by `Edit(**/.env*)` |
| 2026-10-01 | Write | `deploy/tls/probe.pem` | denied by `Edit(**/*.pem)` |
| 2026-10-01 | Write | `deploy/tls/probe.key` | denied by `Edit(**/*.key)` |
| 2026-10-01 | Write | `config/secrets.probe.yaml` | denied by `Edit(config/secrets*)` |
| 2026-10-01 | Bash | `pip install --dry-run --no-index requests` | denied by `Bash(pip:*)` |

The session log is kept by the orchestrator at `~/gov-os-workbench/w1-build/log/w1-01-probe-2026-10-01.jsonl`.

**Scope.** These rules apply to sessions started in the repository root. A session started in a session folder runs under that folder's settings file instead. On 2026-10-01 the `w1-build` file denies Edit on `tests/acceptance/**` and the install commands listed above, and does not name `.env*`, `*.pem`, `*.key` or `config/secrets*`; reported to the owner.
