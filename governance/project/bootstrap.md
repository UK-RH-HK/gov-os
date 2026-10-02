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

Owner install (DEC-141): for the sandbox spike (DEC-138) the owner installed bubblewrap 0.9.0 and socat 1.8.0.0 with `sudo apt-get`, outside every agent session; the `bwrap` smoke test printed OK. Both go into the tool registry when W1-06 creates it.

The install deny rules and the secret-file deny rules (`.env*`, `*.pem`, `*.key`, `config/secrets*`) are carried in each session's `.claude/settings.json`:

| Session | Install deny rules | Secret-file deny rules | Verified |
|---|---|---|---|
| Repository `.claude/settings.json` | `pip`, `pip3`, `python -m pip`, `python3 -m pip`, `uv`, `npm install`, `cargo install`, `apt`, `apt-get`, `sudo`, `curl`, `wget` | Edit on all four patterns | Written by W1-01, 2026-10-01 |
| `w1-build` | `sudo`, `apt`, `apt-get`, `snap`, `npm install\|i\|add`, `npx`, `pip install`, `pip3 install`, `python3 -m pip`, `uv pip\|tool\|add`, `cargo install`, `curl`, `wget`, `docker` | Read and Edit on all four patterns, added by the owner (DEC-101) | Read 2026-10-01 |
| `w1-tests` | Owner-maintained (DEC-098); not readable from the build session | Read and Edit, added by the owner (DEC-101) | Stated by owner (DEC-098, DEC-101) |
| `s1` | Retired by the owner (DEC-101); no agent session runs there | Retired | Stated by owner 2026-10-01. The install-form gap reported on 2026-10-01 is closed by the retirement |
| `s1a` | Retired by the owner (DEC-101); no agent session runs there | Retired | Stated by owner 2026-10-01. The install-form gap reported on 2026-10-01 is closed by the retirement |

The operator console is not listed; it acts as the owner.

From the switch-over (W1-05), every Gov OS session starts in the repository root, and the `w1-build` and `w1-tests` session folders end with the bootstrap (DEC-118).

## Accepted residual

A write outside the repository through an opaque Bash form (for example `perl -e` or `$(…)`) is seen by neither the PreToolUse guard (W1-02) nor the post-command containment check (W1-03), which judges a call by its effect inside the repository. The owner accepted this residual under ADR-0001 on 2026-10-01 (DEC-123, W1-03 KD-2).

The PreToolUse guard's tokeniser drops quotes. In a Bash write target, a single-quoted or escaped `$NAME` is therefore expanded by the guard although the shell keeps it literal, so the guard judges a path other than the one written. The owner accepted this residual (DEC-128).

Four residuals of the post-command containment check (W1-03), accepted by the owner (DEC-134):

- A change made during an agent's Bash call by someone the hooks do not see (the owner in an editor, git in a terminal) is attributed to that call.
- A `HEAD` move in a call with no before-snapshot is checked only against the last `HEAD` the hooks saw.
- While the repository is frozen, an acceptance test changed through an opaque Bash form is restored whoever changed it.
- The before-snapshot adds about 28 ms to the PreToolUse hook of every Bash call.

Under the proportion rule (DEC-135), an edge case of the guard or the containment check that can neither lose work nor let an implementer change acceptance tests is recorded here instead of being closed with more code.

Edge cases of the install rule (W1-04), recorded by the orchestrator under DEC-135 and Contract item CAP-25.c (automated install classification is a non-goal) at the close of W1-04:

- A prefix command (`env`, `command`, `nohup`, `time`, `xargs`) hides `sudo` or an install from the rule.
- A download piped to a shell inside a subshell (`curl … | (sh)`) is not seen.
- `yarn add`, `pnpm add`, `make install` and package managers the rule does not list are not seen.
- Evasive spellings (an alias, a variable holding the command, `bash -c`, `eval`, `base64`) are not seen.
- The rule asks about some commands that install nothing: a line that reads like an install inside a here-document, and the word `install` among a listed package manager's arguments.

The settings rules for install commands remain as the second line (DEC-120).

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

**Scope.** These rules apply to sessions started in the repository root. A session started in a session folder runs under that folder's settings file instead. On 2026-10-01 the `w1-build` file denies Edit on `tests/acceptance/**`, the install commands listed above, and Read and Edit on `.env*`, `*.pem`, `*.key` and `config/secrets*` (added by the owner, DEC-101).
