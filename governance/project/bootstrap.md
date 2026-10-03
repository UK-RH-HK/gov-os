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

At the switch-over (2026-10-02, W1-05), `Edit(tests/acceptance/**)` was removed from the deny rules of the repository's `.claude/settings.json`: it denied the test designer too, and the live PreToolUse guard (W1-02) now decides who may write there. The install rules (`Bash(pip:*)` through `Bash(wget:*)`) moved from `permissions.deny` to `permissions.ask`: a deny rule would stop the orchestrator's approval prompt from ever appearing, and as ask rules they remain the second line behind the install rule of the guard (W1-04, DEC-120). `Bash(sudo:*)` remains as a settings deny rule. The remaining deny rules are: `Read(./docs/source/**)`, `Edit(./docs/source/**)`, `Edit(**/.env*)`, `Edit(**/*.pem)`, `Edit(**/*.key)`, `Edit(config/secrets*)` and `Bash(sudo:*)`.

## Operator diff procedure

At each ticket close, the operator runs `git diff --name-only <base>..<head>` and checks the changed files against the ticket's `allowed_paths`. This procedure is used from the first implementation ticket. The record that it was used is git history through `Task:` trailers (DEC-097). A commit without a `Task:` trailer is not checked (known limit).

The interim operator diff check was retired on 2026-10-02 with the dogfood switch-over (W1-05, DAEO-m7u4). From this date the live PreToolUse guard (W1-02) and the post-command containment check (W1-03) enforce write scope in every session.

## Interim install rule

Install commands are denied in all agent sessions until W1-05 closes (DEC-083, DEC-099). No tool is installed before W1-05. W1-06 (first install) depends on W1-05.

Owner install (DEC-141): for the sandbox spike (DEC-138) the owner installed bubblewrap 0.9.0 and socat 1.8.0.0 with `sudo apt-get`, outside every agent session; the `bwrap` smoke test printed OK. Both go into the tool registry when W1-06 creates it.

The install deny rules and the secret-file deny rules (`.env*`, `*.pem`, `*.key`, `config/secrets*`) are carried in each session's `.claude/settings.json`:

| Session | Install deny rules | Secret-file deny rules | Verified |
|---|---|---|---|
| Repository `.claude/settings.json` | `sudo` as a deny rule. Since the switch-over of 2026-10-02 the other install rules (`pip`, `pip3`, `python -m pip`, `python3 -m pip`, `uv`, `npm install`, `cargo install`, `apt`, `apt-get`, `curl`, `wget`) are ask rules, behind the guard's install rule (W1-04) | Edit on all four patterns | Written by W1-01, 2026-10-01; changed by W1-05, 2026-10-02 |
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

A fifth, accepted with DEC-144: a background command keeps running after its Bash call returns, so its later writes may be attributed to whichever call is active then.

Under the proportion rule (DEC-135), an edge case of the guard or the containment check that can neither lose work nor let an implementer change acceptance tests is recorded here instead of being closed with more code.

Edge cases of the containment check recorded by the orchestrator under DEC-135 at the close of the W1-03 repair (from the reviewer's probe, DEC-137):

- Snapshots older than one hour are cleaned up. A `GOV_PENDING_SNAPSHOT_TIMEOUT_S` above 3600 is therefore undercut: the snapshot is gone before that timeout has passed.
- The PreToolUse hook notes "a later tool call by this actor" before it checks its input, so an unusable input that names an actor also clears that actor's leftover snapshot.
- After an acceptance test is restored from the pre-call `HEAD` (DEC-143), the path is staged with that content. Where the pre-call `HEAD` and the current `HEAD` differ for the path, the index holds a state the call did not create.

Edge cases of the install rule (W1-04), recorded by the orchestrator under DEC-135 and Contract item CAP-25.c (automated install classification is a non-goal) at the close of W1-04:

- A prefix command (`env`, `command`, `nohup`, `time`, `xargs`) hides `sudo` or an install from the rule.
- A download piped to a shell inside a subshell (`curl … | (sh)`) is not seen.
- `yarn add`, `pnpm add`, `make install` and package managers the rule does not list are not seen.
- Evasive spellings (an alias, a variable holding the command, `bash -c`, `eval`, `base64`) are not seen.
- The rule asks about some commands that install nothing: a line that reads like an install inside a here-document, and the word `install` among a listed package manager's arguments.
- An option before `-m` (`python3 -u -m pip install …`), or an option with a value before `uv`'s subcommand (`uv --directory <path> pip install …`), hides the install. Found by the reviewer's probe of the W1-04 repair.
- A program name that is a listed package manager followed by digits, where no such program exists (`gem2 install …`), is asked about; so is `uv` with an option whose value is the word `pip` or `tool`.

The settings rules for install commands remain as the second line (DEC-120): as deny rules until the switch-over, as ask rules since 2026-10-02.

## After the sandbox experiment (S2, 2026-10-03)

The owner accepted the sandbox experiment EXP-001 as ADOPT-PARTIAL (DEC-152) and limited the sandbox to worker sessions
started by the launcher (DEC-161). The orchestrator's own session is not sandboxed (DEC-156). This section states which
residuals above are closed, for which sessions, and which stay open. It takes effect when W1-46 (launcher) and W1-47
(guard hardening) close; until then every residual above stands as written.

**Closed for Bash in launched worker sessions** (engineer, independent test designer, independent auditor, research or
experiment):

- A write outside the repository through an opaque Bash form (DEC-123). The OS sandbox stops it without parsing the
  command.
- The install misses of W1-04 (DEC-147): prefix commands, a download piped to a shell in a subshell, package managers
  the rule does not list, evasive spellings, and an option before `-m` or before `uv`'s subcommand. The sandbox's write
  wall and network wall stop them. The false asks stay as they are. Worker roles never install system-wide (DEC-157).

**Still open for the orchestrator's own session**, which runs under the guard and the settings rules alone:

- Both residuals above: outside-repository writes through opaque Bash forms, and the install misses.
- An opaque Bash read of the qualification oracle (DEC-162). The oracle is hidden from every session started in the
  repository root by a `Read` deny rule with its absolute path in the committed `.claude/settings.json` and by the
  guard denying any Read, Grep, Glob or Bash call whose input names the path (both from W1-47). A Bash command that
  reaches the oracle without naming its path is seen by neither layer. The owner accepted this residual (DEC-162).

**Open for every session:**

- File-tool reads and writes (Read, Edit, Write). They run outside the sandbox; the guard and the permission rules
  are the only wall.
- Anything a hook or an MCP server does. Both run outside the sandbox.
- The untested sandbox cases: `denyWrite` on a path that doesn't exist yet, symlink and hard-link tricks, the seccomp
  filter, and `bypassPermissions` mode. They go to a Wave 2 experiment, EXP-002 (DEC-160).
- Subagents inside a sandboxed worker session. Whether a subagent started inside a launched worker runs inside the
  same sandbox is not tested. It goes to EXP-002 (DEC-164).
- `excludedCommands`. A command listed there runs outside the sandbox. The launcher sets none (DEC-164); what the
  setting does when present is not tested, and goes to EXP-002.

**The shared `$TMPDIR`.** The launcher sets a per-session temp directory for each worker session (DEC-159). If
W1-46's acceptance test shows the temp directory can't be overridden, the shared `$TMPDIR` is recorded here as a
residual. The orchestrator's own session keeps the shared temp directory.

**Unchanged:** the guard's quoting limit (DEC-128), the residuals of the containment check (DEC-134, DEC-144) and the
DEC-135 edge cases. They concern writes inside the repository.

**The research role's installs (DEC-163).** From W1-46, the Wave 1 roster has a minimal research role. It may install
only into a venv or local prefix inside its own experiment folder, within its ticket's `allowed_paths`. A system-wide
install is denied to it, and the sandbox's write fence is what enforces that. Its network profile is the research
allowlist of DEC-158. Every other worker role's install commands stay denied.

**Hiding is silent.** A hidden directory looks empty from a worker's Bash; no error is raised.

**Confirmed by the owner (DEC-151):** moving the install settings rules from `deny` to `ask` at the switch-over was
correct, and keeps the second line of DEC-120; W1-01's interim acceptance tests skip after the switch-over by design.

**Orchestrator write scope and checkpoint (DEC-150, DEC-156).** From W1-45, the orchestrator may write anywhere in the
repository except `tests/acceptance/**`. The acceptance tests of W1-02 and W1-03 that assert the old orchestrator rule
are revised by the Independent Test Designer under W1-45 (reason: owner correction, DEC-156). Its checkpoint lives in `.gov-runtime/scratch/orchestrator/` until W1-25's
`gov checkpoint` replaces it.

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

## Switch-over

On 2026-10-02, the dogfood switch-over (W1-05, DAEO-m7u4) wired the live hooks into this repository's `.claude/settings.json`:

- **PreToolUse** (every tool, no matcher): the PreToolUse guard (`template/governance/kernel/hooks/pretooluse.py`). Registered for every tool so that a later tool call of any kind reaches the hook, which is how the containment check learns that an actor's earlier call is over (DEC-142, DEC-144).
- **PostToolUse** (Bash): the post-command containment check (`template/governance/kernel/hooks/posttooluse.py`).
- **PostToolUseFailure** (Bash): the same containment check, because a failed or interrupted call may still have written.

A session declares its role and its active ticket with the environment variables `GOV_ROLE` and `GOV_TICKET` at session start. A session without a known role is read-only (DEC-107, DEC-125). Inside a role subagent, the subagent's type name decides the role (DEC-117); a subagent whose type is not a defined role is read-only (DEC-113). Every Gov OS session now starts in the repository root (DEC-118).

Measured PreToolUse hook p95 wall-clock times (40 runs after 3 warm-ups, in a copy of this repository):

| Call type | p95 |
|---|---|
| Read (read-only, no role) | 38 ms |
| Write (engineer) | 36 ms |
| Bash (engineer, includes before-snapshot) | 35 ms |

The 100 ms budget is for the guard's decision (DEC-149). All three are within budget. The Bash total includes W1-03's before-snapshot and is reported for the record.

Live attempts on 2026-10-02, in headless sessions started in the repository root with `GOV_ROLE=orchestrator` and `GOV_TICKET=DAEO-m7u4`, after the hooks were wired (DEC-120, and the follow-up of DEC-107):

| Mode | Call | Result |
|---|---|---|
| Auto | Bash `pip install --dry-run --no-index requests` | The hook answered `ask` ("install command requires owner approval"). The session had no approval surface, so the call was denied automatically and not performed |
| Auto | Bash `pipx install --help`, which no settings rule matches | The hook's `ask` alone had the same effect: not performed |
| default | Write `docs/w1-05-live-probe-main.txt` on the main thread | Denied by the hook: "denied for role 'orchestrator'" |
| default | Write `docs/w1-05-live-probe-subagent.txt` by an `engineer` subagent | Denied by the hook: "denied for role 'engineer'". The hook input inside a subagent carries `agent_type` on the live guard |
| default | Read `README.md` | Allowed |

No file was created and nothing was installed. The session logs are kept by the orchestrator at `~/gov-os-workbench/w1-build/log/w1-05-live-*.jsonl`.
