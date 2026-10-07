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

Owner install (DEC-203): on 2026-10-03 the owner updated the Claude Code CLI from 2.1.284 to 2.1.288 with `claude install 2.1.288`, through the operator console, outside every agent session. `~/.local/bin/claude` resolves to `~/.local/share/claude/versions/2.1.288`. W1-48 records it in the tool registry.

Other copies of Claude Code on this machine, recorded on 2026-10-03:

- **Removed (DEC-204):** the npm global `@anthropic-ai/claude-code` 2.1.59 under Node v18.20.8 was stale, and the owner removed it.
- **Noted, not removed (DEC-205):** a second `claude` is on `PATH` at `/mnt/c/Users/usain/AppData/Roaming/npm/claude`. It is a Windows-side npm install reached through WSL's `PATH`, listed after `~/.local/bin/claude`. It is outside WSL and the owner's choice. Every headless worker is therefore started with the absolute path `~/.local/bin/claude`, never a bare `claude`, so that a changed `PATH` can never start the Windows copy.
- Older versions kept by the native installer under `~/.local/share/claude/versions/` (2.1.59, 2.1.236, 2.1.284) are not linked from `~/.local/bin/claude`.

The install deny rules and the secret-file deny rules (`.env*`, `*.pem`, `*.key`, `config/secrets*`) are carried in each session's `.claude/settings.json`:

| Session | Install deny rules | Secret-file deny rules | Verified |
|---|---|---|---|
| Repository `.claude/settings.json` | `sudo` as a deny rule. Since the switch-over of 2026-10-02 the other install rules (`pip`, `pip3`, `python -m pip`, `python3 -m pip`, `uv`, `npm install`, `cargo install`, `apt`, `apt-get`, `curl`, `wget`) are ask rules, behind the guard's install rule (W1-04). W1-47 removes these ask rules (DEC-172) | Edit on all four patterns | Written by W1-01, 2026-10-01; changed by W1-05, 2026-10-02 |
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

One occurrence of the first of these, recorded by the orchestrator on 2026-10-03 (W1-06, DAEO-ipqy): the
orchestrator started a headless test designer session inside a foreground Bash call and waited for it. The test
designer committed its own tests (`e27633ae`, trailers `Task: DAEO-ipqy` and `Role: independent-test-designer`)
while that call was still running, so the containment check attributed the commit to the orchestrator's call and
wrote a finding to `.gov-runtime/findings.jsonl` ("committed path(s) outside allowed paths", three paths under
`tests/acceptance/W1-06/`, action `flagged`). The orchestrator wrote none of those files; nothing was reverted. The
orchestrator starts worker sessions as background commands, whose Bash call returns at once, so that a worker's
commit is not attributed to it. The owner confirmed this on 2026-10-03 (DEC-206): the finding stays in
`.gov-runtime/findings.jsonl` as written, because that file is append-only evidence; this paragraph explains it, and
the exit audit reads both. Worker sessions always run in the background.

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

The settings rules for install commands remain as the second line (DEC-120): as deny rules until the switch-over, as ask rules since 2026-10-02. The owner has withdrawn that second line (DEC-172): W1-47 removes the ask rules, and from then the guard's install rule stands alone. See "The settings ask rules are withdrawn" below.

## After the sandbox experiment (S2, 2026-10-03)

The owner accepted the sandbox experiment EXP-001 as ADOPT-PARTIAL (DEC-152) and limited the sandbox to worker sessions
started by the launcher (DEC-161). The orchestrator's own session is not sandboxed (DEC-156). This section states which
residuals above are closed, for which sessions, and which stay open. It takes effect when W1-46 (launcher) and W1-47
(guard hardening) close; until then every residual above stands as written.

**Closed for Bash in launched worker sessions** (engineer, independent test designer, independent auditor, research or
experiment):

- A write outside the repository through an opaque Bash form (DEC-123). The OS sandbox stops it without parsing the
  command.
- The install misses of W1-04 (DEC-147), **for installs that write outside the repository**: prefix commands, a
  download piped to a shell in a subshell, package managers the rule does not list, evasive spellings, and an option
  before `-m` or before `uv`'s subcommand. The sandbox's write wall stops them (EXP-001 §3.2, §5.1). For engineer,
  independent test designer and independent auditor the empty network allowlist also blocks the download. The false
  asks stay as they are. Worker roles never install system-wide (DEC-157).
- **Not closed:** an install that writes inside the repository. The write wall does not stop it. For engineer, test
  designer and auditor the guard's install rule and the empty allowlist still apply. A research session can install
  inside the repository from an allowlisted index (PyPI, npm; DEC-158); DEC-163 confines that to its experiment
  folder, through the `Edit` deny rules the launcher generates.
- **The limits of that deny list.** The launcher's deny list is computed at launch, from the paths that exist then. A path
  created later outside the experiment folder is not in the list, and the sandbox does not stop a Bash write to it.
  That path is covered by the guard's per-ticket allow-list, which holds the research role's writes to its ticket's
  `allowed_paths`; a change the guard did not see is reported by the containment check. The list has two exceptions:
  `.git/`, so that the session can commit its evidence record, and an entry whose name contains `*`, `?` or `[`,
  which the sandbox skips on Linux (EXP-001 §1). Both are left to the guard and the containment check. `denyWrite` on
  a path that doesn't exist yet is one of the untested cases of EXP-002. `.git/hooks` and `.git/config` stay protected
  by the sandbox even though `.git/` is left out of the deny list (EXP-001 §1, protected paths), while other changes
  inside `.git/` aren't seen by the containment check.

**Still open for the orchestrator's own session**, which runs under the guard and the settings rules alone:

- Both residuals above: outside-repository writes through opaque Bash forms, and the install misses.
- Once W1-47 has removed the settings ask rules (DEC-172), the commands listed under "Commands that lose their
  settings prompt" below meet no prompt in this session. Four of them get the guard's `ask` back (DEC-174).
- An opaque Bash read of the qualification oracle (DEC-162). The oracle is hidden from every session started in the
  repository root by a `Read` deny rule with its absolute path in the committed `.claude/settings.json` and by the
  guard denying any tool call whose input names the path, Read, Grep, Glob or Bash included (both from W1-47). The
  oracle path is held in `governance/project/held-out.yaml` and in the committed deny rule built from it; register
  entry DEC-067 names the directory historically. The guard and the launcher take the path from `held-out.yaml`, and
  no acceptance test names it. The owner confirms the value in `held-out.yaml` when W1-47 closes. A Bash command that
  reaches the oracle without naming its path is seen by neither layer. The owner accepted this residual (DEC-162).
  What "names the path" covers is decided by DEC-215: the guard denies a call whose input contains the held-out path
  literally anywhere, or reaches it through a relative path, `..`, `~`, `$HOME` or a symbolic link, except edits to
  the two files that hold it. Three forms stay under this residual: a parent directory given to a recursive tool,
  a glob that matches the path without naming it, and a look-alike sibling whose name starts with the same
  characters. The path is held in `governance/project/held-out.yaml` under the key `held_out_paths`, written by the
  owner (DEC-218); the oracle is outside the repository (DEC-213).

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
allowlist of DEC-158. Every other worker role's install commands stay denied. A research or experiment session runs
as `GOV_ROLE=research`.

**The sandbox's cost (EXP-001 §3.6).** About +65 ms per Bash command and about +3,250 input tokens per session (+7 %).
The tokens are reported as a separate line in W1-31, not inside the governance share; whether they count toward it is
decided at the Wave 1 exit, using measured figures (DEC-170).

**Hiding is silent.** A hidden directory looks empty from a worker's Bash; no error is raised.

**Confirmed by the owner (DEC-151):** moving the install settings rules from `deny` to `ask` at the switch-over was
correct, and keeps the second line of DEC-120; W1-01's interim acceptance tests skip after the switch-over by design.
DEC-172 has since withdrawn that second line.

**The settings ask rules are withdrawn (DEC-172).** W1-47 removes the install and download ask rules (`pip`, `pip3`,
`python -m pip`, `python3 -m pip`, `uv`, `npm install`, `cargo install`, `apt`, `apt-get`, `curl`, `wget`) from the
committed `.claude/settings.json`. The `Bash(sudo:*)` deny rule and the other deny rules stay. From then:

- The guard's install rule decides install commands alone: `ask` for the orchestrator, `deny` for engineer,
  independent test designer and independent auditor, and let through for the research role inside its experiment
  folder (DEC-163).
- The owner asked for no test run. W1-05's live attempts (the "Switch-over" table below) showed that the guard's rule
  suffices alone: `pipx install --help`, which no settings rule matches, still got the hook's `ask`.
- In a launched worker session the sandbox backs the guard. In the orchestrator's own session the guard's rule
  stands alone.
- A launched research session therefore meets no settings prompt on `pip`, `uv`, `npm install`, `curl` or `wget`.
  W1-46's install test runs with the repository's committed settings loaded.

**Commands that lose their settings prompt (DEC-172), from a run of the classifier.** On 2026-10-03, S2 ran the
guard's install classifier (`has_install` and `has_sudo` in `src/gov/guard/install.py`, last changed by `0c149f7`)
over 201 commands, without executing any of them. 198 are matched by one of the eleven ask rules that W1-47 removes,
taken as prefix matches on each simple command of the line. The guard's rule still catches 39 of them. The other 159
lose their prompt in the orchestrator's own session. The script and its output are kept at
`~/gov-os-workbench/s2/round3-classifier-run/`.

| Ask rule removed | Still asked by the guard's rule | Loses its prompt |
|---|---|---|
| `pip`, `pip3`, `python -m pip`, `python3 -m pip` | `install` | `download`, `wheel`, `uninstall`, `list`, `freeze`, `show`, `check`, `config`, `cache`, `index`, `inspect`, `hash`, `search`, `debug`, `--version`, `help` |
| `uv` | `pip install` and `tool install`, also after an option that takes no value (`-q`, `--no-cache`) | `add`, `sync`, `run`, `run --with`, `run --with-requirements`, `pip sync`, `pip uninstall`, `pip compile`, `pip list`, `pip freeze`, `pip show`, `pip check`, `pip tree`, `remove`, `lock`, `tool run`, `tool upgrade`, `tool uninstall`, `tool list`, `tool update-shell`, `python install`, `python uninstall`, `python list`, `python pin`, `venv`, `init`, `build`, `publish`, `export`, `tree`, `cache clean`, `self update`, `version`, `--version`, `help`; and `pip install` or `tool install` after an option with a value (`--directory <path>`, `--project <path>`) |
| `npm install` | every form tried | none |
| `cargo install` | every form tried | none |
| `apt`, `apt-get` | `install` | `update`, `upgrade`, `full-upgrade`, `dist-upgrade`, `remove`, `purge`, `autoremove`, `download`, `source`, `build-dep`, `clean`; for `apt` also `list`, `search`, `show`, `edit-sources`. The ones that change the system fail without `sudo`, which stays denied |
| `curl` | `-o` into a `PATH` directory; a pipe to `sh` or `bash`, also through `tee`; a pipe to `sudo sh` (the `sudo` rule) | a fetch to standard output; `-O`; `-o` to a relative path; `--output-dir <PATH directory> -O`; a shell redirect (`>`) into a `PATH` directory; uploads (`-d @file`, `-T`, `-F`); a pipe to `(sh)`, `zsh`, `dash`, `env sh`, `python3` or `tar` (also `tar -C <PATH directory>`); a download followed by a run (`&& sh i.sh`, `; bash i.sh`) |
| `wget` | `-O` or `-qO` into a `PATH` directory; a pipe to `sh` or `bash`; a pipe to `sudo sh` (the `sudo` rule) | a plain download; `-O` to a relative path; `-P` or `--directory-prefix` into a `PATH` directory; `--post-file`; `-r`; a pipe to `(sh)`, `zsh`, `python3` or `tar`; a download followed by `sh i.sh` |

- **Limits of the run.** The 201 commands are every subcommand S2 knows of each tool, plus the download forms above.
  No Claude Code session was run. A command that starts with one of the eleven prefixes and is not on the "still
  asked" side loses its prompt, whether or not it is listed.
- **`uvx`** was matched by no settings rule (`Bash(uv:*)` does not match it) and is not seen by the guard's rule. It
  had no prompt before DEC-172 either.
- **Four forms get the guard's `ask` (DEC-174).** W1-47 extends the guard's install rule to recognise `uv add`,
  `uv sync`, `uv run --with` and `uvx` as installs. They are then `ask` for the orchestrator (DEC-083) and denied for
  engineer, independent test designer and independent auditor. The research role's exception (DEC-163) still lets
  them through inside its experiment folder.
- **What stays without a prompt** in the orchestrator's own session after W1-47: every other entry of the right-hand
  column. Those that fetch or install are `uv run` without `--with`, `uv run --with-requirements`, `uv pip sync`,
  `uv tool run`, `uv tool upgrade`, `uv python install`, `uv self update`, `pip download`, `pip wheel`, and the `curl`
  and `wget` forms listed. In a launched worker session the sandbox's write wall and network profile back the guard.

**Orchestrator write scope and checkpoint (DEC-150, DEC-156).** From W1-45, the orchestrator may write anywhere in the
repository except `tests/acceptance/**`. The acceptance tests of W1-02 and W1-03 that assert the old orchestrator rule
are revised by the Independent Test Designer in W1-45's test design batch (reason: owner correction, DEC-156). An
orchestrator change outside its ticket's paths is then a record, not a containment finding. Its checkpoint lives in `.gov-runtime/scratch/orchestrator/` until W1-25's
`gov checkpoint` replaces it.

**As built and closed (W1-45, 2026-10-03; DEC-175…DEC-178).**

- The wide scope holds only in a session whose own role is orchestrator. An `orchestrator` subagent in another
  role's session keeps the ticket-paths rule (DEC-178).
- Everything under `.gov-runtime/` other than `scratch/**` is denied to the orchestrator by the guard: the freeze
  flag, the snapshots, the findings and the records. Setting or lifting a freeze is the owner's action (DEC-176).
- An orchestrator change outside its ticket's paths writes one line per call to `.gov-runtime/records.jsonl`, with
  the fields of a finding and `action: "recorded"` (DEC-177).

**What the reviewer's probe left at W1-45's close (DEC-137), and the owner's decisions on it (DEC-179…DEC-181).**

- **Opaque Bash writes into `.gov-runtime/`.** The folder is ignored by git, so the containment check never sees a
  change there; DEC-176's protection is the guard alone. An opaque Bash form (an interpreter one-liner, for example)
  that writes the freeze flag, the findings, the records or a snapshot is seen by neither layer. This is the class
  of DEC-123, and it held for every role before W1-45.
- **`ln`.** The guard does not judge `ln`, so a link created under `tests/acceptance/**` or `.gov-runtime/` passes
  it. Under `tests/acceptance/**` the containment check catches the link. Under `.gov-runtime/` nothing does.
- **Closed for launched worker sessions by W1-46 (DEC-180):** the launcher's settings for every worker role carry an
  `Edit` deny rule for `.gov-runtime/**` except `.gov-runtime/scratch/**`, which stops both at OS level (EXP-001: one
  `Edit` rule binds the file tools and Bash). Until W1-46 closes, headless worker sessions run without it.
- **Accepted residual in the orchestrator's own session (DEC-181):** both stay open there, because that session is
  not sandboxed (DEC-156). The orchestrator doesn't use them.
- **A defect, not a residual (DEC-179):** the guard function `_get_allowed_paths` gives the orchestrator's wide scope
  when its session-role argument is left out. Its only caller passes the argument, so no session gains a write
  today. W1-47 makes it fail closed, with a builder test. A finding that makes the guard fail open is a defect.

**What the reviewer's probe left at W1-47 (DEC-137), recorded by the orchestrator under DEC-135 on 2026-10-04.** The
reviewer found no case in which the hardened guard fails open on a KPI of W1-47, loses work, or lets an implementer
change acceptance tests. These edge cases stay:

- **The held-out rule.**
  - A relative path is resolved against the session's working directory only. A relative path after a `cd` inside
    the same command, or inside `--option=value`, is not resolved.
  - The literal match is a substring match, so a look-alike sibling of a held-out path is denied too.
  - The holder exception follows a symbolic link: if `.claude/settings.json` were replaced by a link to another
    file in a role's scope, a write that carries the path into that file would pass. It needs `ln`, which the
    guard does not judge (see W1-45's probe above), and a ticket whose paths include the settings file.
  - Reading `governance/project/held-out.yaml` or `.claude/settings.json` is not denied: the rule is about the
    held-out path, not about the two files that hold it. An agent that reads them sees the value. Briefs tell
    workers not to, and no agent writes or retypes it (DEC-218). The owner accepted this residual (DEC-223): seeing
    the path isn't seeing the oracle's contents.
  - A missing `held-out.yaml` means no held-out rule; a file with a missing key, an empty list or a broken shape
    makes the guard deny every call until the owner repairs it through the operator (DEC-218, DEC-223). `gov doctor`
    will report a missing file in this repository (W1-27).
  - A key written twice in `held-out.yaml` keeps only its last value (the YAML reader's behaviour). The owner writes
    the file.
  - With some ten thousand held-out paths the hook would pass its 100 ms budget (182 ms measured); with one to three
    paths the rule adds under 1 ms.
- **The escape hatch.** Any truthy value of `dangerouslyDisableSandbox` is denied, not only `true`; the rule is for
  Bash calls.
- **The install rule's `uv` forms (CAP-25.c).** `uv run -w<package>`, with the option joined to its value, is not
  seen. A `-w` or `--with` that belongs to the program after `uv run` is taken for `uv`'s own, so the command is
  asked about or denied. `env uv add …` and `command uv add …` are not seen, as with every prefix command above.
- **A here-string.** `sh <<< "<command>"` is read by the guard as a command that writes nothing, like the other
  opaque forms (`bash -c`, `eval`). Inside the repository the containment check reports or restores the change;
  in a launched worker session the sandbox stops a write outside it.

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

## Parallel run: containment records that are not defects (DEC-254, 2026-10-04)

Until W1-50 (`DAEO-xnbx`) judges a HEAD move commit by commit, by each commit's own `Role` and `Task` trailers, the
post-command containment check (W1-03) writes two kinds of finding for permitted actions of the parallel run
(DEC-235). The owner accepted both as records, not defects (DEC-254). Each is also noted in its ticket's close row in
the orchestrator's checkpoint.

- **An integration merge.** The check flags any HEAD move that contains a merge commit ("HEAD moved (not a forward
  move on the same branch)"). Every merge of a ticket branch into `w1/integrate` by the main orchestrator, as the
  orchestrator prompt's section 3 prescribes, writes one such line to `.gov-runtime/findings.jsonl` in the main tree.
  First seen: the merge of `w1/W1-37`, commit `00e3d539`.
- **A worker's commit attributed to its lead.** In a ticket's worktree the lead (role orchestrator) waits for its
  worker with its own Bash calls. When the test designer commits under `tests/acceptance/<W1-id>/` during such a
  call, the check attributes the commit to the lead's call and flags "committed path(s) outside allowed paths" in
  that worktree's `.gov-runtime/findings.jsonl`. The commit is the designer's, in the designer's scope. Seen in the
  worktrees of W1-37, W1-18 and W1-08. A worktree's findings file is copied to
  `.gov-runtime/scratch/orchestrator/log/<W1-id>-findings.jsonl` in the main tree before the worktree is removed.
- **The W1-01 history test** failed on the first integration merge for the same reason, and is revised under
  DEC-253 in W1-50's test design batch.

## Ollama: started by `gov`, not stopped by `gov` (DEC-261, 2026-10-04)

ADR-0002 §3 says the Ollama daemon is "started and stopped by `gov`". W1-18 (`DAEO-1ve2`) delivers the first half
only: `gov` starts `ollama serve` on demand and never stops it. Ollama's 5-minute idle unload frees the model's GPU
memory, which was the owner's intent; the `serve` process itself stays. The owner accepted this difference (DEC-261).
The ADR is not changed.

## W1-37 residuals (Superpowers three-skill copy, 2026-10-04)

Recorded at W1-37's close, from the ticket lead's summary. None is a defect.

- **Zero headroom on the sizes.** The three `SKILL.md` sizes (2,389, 2,360 and 899 by floor(characters ÷ 4),
  DEC-247) sit exactly on their ceilings. "Characters" is read as decoded UTF-8; counted as bytes the three would be
  2,394, 2,366 and 911 and fail. Any upstream change to a `SKILL.md` breaks the test.
- **File modes are not asserted.** `find-polluter.sh` kept its executable bit in the copy, but no test protects it.
- **No licence in the copy.** `template/governance/kernel/skills/superpowers/` holds no `LICENSE`; the upstream
  licence stays in the vendor folder, which is the only source (DEC-244).
- **CAP-24 for vendored skills.** The version is recorded beside the copies, in `vendored.yaml`, not in each
  `SKILL.md` frontmatter; the owner reads CAP-24 this way for vendored skills (DEC-262). `gov close` (W1-30) reads a
  vendored skill's version from that record.
- **Guard refusals met by the engineer.** `mkdir -p` with `cp -R` onto the `superpowers` folder itself was refused,
  so the files were copied one by one to literal paths.

## W1-08 residuals (record schemas, templates and the path map, 2026-10-04)

Recorded at W1-08's close, from the ticket lead's summaries. None is a defect; each names the ticket that should
settle it.

- **Capability values for this repository.** The entry shape is decided (DEC-251, DEC-265). The values in
  `governance/project/path-map.yaml` (code intelligence on for Python, research corpus off) are the implementer's.
- **Namespace field values are free text.** Sensitivity, retention, export policy, embedding policy, provenance and
  deletion/rebuild behaviour are non-empty strings; the words in this path map are the implementer's. W1-15 fixes
  closed lists when it first reads them.
- **`permitted_roles`** is read as "may access", and all six roles are listed on every namespace. Confirm before
  W1-15.
- **`fixtures/**`** is the only `product` namespace.
- **The ticket schema** requires only `kpis`, `role` and `allowed_paths` beyond the shared frontmatter; the other six
  ticket fields are typed but optional. Consider requiring them at W1-09.
- **`status` and `type`.** `status` is any non-empty string on every record; a lesson's lifecycle is the required
  `lifecycle` key, closed to the six states. `type` is pinned per record type except on tickets.
- **Id grammars.** `lesson_id` is decided (DEC-252). The other four grammars are the implementer's, and `supersedes`,
  `superseded_by` and `consumers` have no grammar.
- **Failure, research, decision package and checkpoint records** have no type-specific fields; the required fields of
  the older schemas under `schemas/records/` were not carried over.
- **Closed and open maps.** `policies`, `systems`, `capabilities` and its two entries refuse unknown keys; namespaces,
  the path map's top level and record frontmatter accept extras. No test covers the open ones.
- **The `systems` snapshot** needs updating as tickets land. Updated at W1-33's close (2026-10-05): the research
  system is `minimal` (the launcher and the research role), and the agent organisation also names the kernel role
  files and the roster.
- **New top-level folders.** The root namespace uses `*`, and `.github/` and `.rulesync/` are pre-listed. Any other
  new top-level folder fails "every tracked path in exactly one namespace" until a namespace is added.
- **The two committed ADRs** lack `state_class` and would not validate against the decision schema until they get it.
- **Untested points:** language names must be non-empty strings (slightly stricter than DEC-251 says); the disabled
  form of `code_intelligence` (DEC-265, for W1-27's test design); that a lesson record's `id` uses `lesson_id` and
  no other grammar.
- **The held-out path string** appeared twice in the product-spec worker's output, from printing a ticket's
  `allowed_paths` and from ADR-0002 §6. Seeing the path is an accepted residual (DEC-223).

## W1-18 residuals (Ollama on-demand lifecycle, 2026-10-04)

Recorded at W1-18's close, from the ticket lead's summary. None is a defect.

- **A `serve` that never becomes healthy is left running**, following DEC-261 ("never stops it"). No test asserts
  this either way.
- **Choices of the engineer the decisions don't name and no test asserts:** an available result has `state`
  `AVAILABLE` and `warning` `None`; `env`, when given, is read for the three variables and passed to the daemon;
  each health probe is capped at 1 s, and the health request bypasses proxy variables; the daemon gets its own
  session with its streams to `/dev/null`.
- **Readings of the test designer:** "within the deadline" allows 2 s on top of `timeout_s`; "FTS-only" matches
  `FTS-only` or `FTS only` in any letter case; the 20 s default is read from the function's signature, not waited for.
- **No test against the real daemon.** Ollama is not installed on this machine; the suite uses a stand-in executable
  and a stand-in loopback endpoint. The embedding model's registry row (DEC-195) was not added: the registry is
  outside the ticket's paths and nothing was installed. It is due when Ollama and the model are installed, at the
  latest for W1-19.
- **G-22's text** exists only in the archived sources; the decisions rest on the in-tree sources (DEC-260, DEC-261,
  DEC-257).
- **The ticket body** still says "on-demand start and stop"; DEC-261 decides start only.

## W1-10 residuals (store and record graph, 2026-10-04)

Recorded at W1-10's close, from the ticket lead's summary. None is a defect; each is for a later ticket.

- **Who writes `.gov-runtime/store.db` in a live session** is decided (DEC-322, 2026-10-04): only orchestrator-role
  sessions write the live store; tests and workers build their own stores in temporary directories; revisit when
  `gov rebuild` is wired (W1-27). The guard keeps
  `.gov-runtime/` outside `scratch/` closed to worker roles, and W1-17, W1-20 and W1-24 read the store in worker
  sessions. Every W1-10 test builds the store in a temporary repository.
- **What loads as a record today (DEC-274).** The charter, the contract and the plan have `id` and `status` but no
  `type`, so the load reports them invalid. The seven kernel templates load as records with placeholder ids.
  Decisions are headings in the register, not files, so every `DEC-…` reference is dangling. Two files with one id
  both load.
- **Dangling edges in this repository (DEC-277).** A ticket's `depends_on` holds WBS ids while its `id` is the tk id.
  Trailer values such as `decision-record`, `owner-prompt` and `CAP-58.a` name no record. Unresolved trailers appear
  in `dangling()` with type `IMPLEMENTS` or `TASK`; `TASK` is outside the eight edge types.
- **The four edge keys DEC-012 does not name** (`evidence_for`, `tests`, `generates`, `validates`) are to be checked
  against the archived Framework §11.2 by a product-spec worker before any real record uses them (DEC-277).
- **Records are read from `HEAD`**, not the working tree: an uncommitted edit to a record is not in the graph.
  Untested.
- **The DEC-182 boundary** uses the committer date in the commit's own time zone; no test fixes which date decides.
- **The digest (DEC-276)** covers records (path, id, type, status), edges, commits, trailers and each commit's
  changed paths. It does not cover other frontmatter keys or the record body, and no `content_hash` is stored.
- **Merge commits** list no changed paths, so they never match `commits(root, path=…)`. Renames are untested.
- **Two new error codes**, `STORE_MISSING` and `STORE_GIT_FAILED`, are untested.
- **Not tested:** the `owner` and free `links` filters of CAP-08.a; no KPI line names them.
- **A load replaces only its own five tables**, in one transaction, so tables a later ticket adds to the same file
  survive.

## W1-15 residuals (secret rules, pre-index filter and the secrets-indexing check, 2026-10-04)

Recorded at W1-15's close, from the ticket lead's summaries and the reviewer's fourteen findings, seven of which were
fixed. None of the following is a defect of the ticket; each names who should settle it.

- **A project can remove or rewrite a template rule** (DEC-299). The project's `.gitleaks.toml` is the one source of
  rules (DEC-287); its allowlists and disabled rules are ignored by the filter and the check (DEC-290, DEC-298), but a
  rule the project deleted, such as the canary rule, is not put back. A file with no rules at all is refused. A
  project file that extends another file with rules of its own still inherits that file's allowlists.
- **The rules over-block.** The token rule flags ordinary identifiers (`pk_…`, `tok_…`, `rk_…`, `sk-…` of 16 or more
  characters), and the canary rule flags any upper-case identifier with the canary word in the middle. This
  repository loses only the W1-15 ticket file from an index; an adopting product could lose code files. Requiring a
  digit or mixed case in the token body is the suggested repair. The owner decided that repair, before W1-41
  (DEC-324); W1-16 carries it (DEC-325). The canary rule's over-blocking stays a residual.
- **Near spellings of the canary are missed** (lower case, other separators, markdown-escaped underscores); they are
  outside DEC-286. The owner still confirms the count of seven canaries against the S0b1 manifest.
- **Path-map patterns match narrowly.** `**/x/**` does not match a top-level `x/`; a trailing slash, a leading `/` or
  `./`, `?` and `[]` match nothing; `paths` given as a string is read character by character with no error. For the
  path-map schema (W1-27 replaces the minimal one, DEC-228).
- **The two W1-08 residuals that named W1-15** (closed lists for the free-text namespace fields; the meaning of
  `permitted_roles`) move to the first ticket that reads export or embedding policy, W1-17 or W1-24 (DEC-289). W1-15
  reads only a namespace's `paths` and `memory_class`.
- **What the check does not see.** Compressed stores and bundles (`.gz`, deflated `.zip`, `.tar.gz`, a gzip BLOB),
  for W1-24 if bundles are compressed; UTF-32 text; a secret in a store file's or folder's name, which is also
  printed in the check's output when the content matches; SQLite WAL side files are scanned as plain bytes only.
- **What the filter cannot see.** A file replaced after the filter answered and before the indexer reads it (for
  W1-16, W1-17 and W1-19; the check is the backstop); a hard link to a product file; a secret split across lines or
  reversed.
- **`.gov-runtime/scratch/` counts as a store for the check**, so the check would be red in this repository on lead
  briefs and worker logs that name the canary. W1-26 settles this before `gov check` runs the check here.
- **gitleaks is trusted by name.** A stand-in `gitleaks` first on `PATH` that exits 0 passes everything; the version
  is not verified. The filter and check cases need gitleaks where they run; putting it on CI is an install for the
  owner, raised with W1-40 (DEC-287).
- **Edges that fail closed or noisily.** A configuration whose only rules come through `[extend] path` is refused as
  "no rules"; one with a TOML date value, or larger than about 128 KB, makes the filter raise; a not-green check on a
  ruleless configuration or an unreadable store exits with a Python traceback; a clean store with an unloadable
  virtual table, or a table name with a double quote, keeps the check red; a FIFO in a governance namespace would
  block the filter (reasoned, not run).
- **The root allowlist.** With the template's rules and no allowlist, gitleaks flags four tracked paths: the W1-15
  ticket file, which names the canary, and three brownfield fixture files. W1-15 allowlisted only the ticket file; the
  fixtures were already allowlisted. The list is the lead's reconstruction, not the first engineer's report.
- **A guard observation.** Twice in the parallel run a worker wrote a file inside its allowed paths through a Python
  script fed by a here-document in Bash, and the guard did not stop it. For W1-46 and W1-47's residual lists.

## W1-49 residuals (light auto-resume hooks, 2026-10-04)

Recorded at W1-49's close, from the ticket lead's summaries and two reviews. None is a defect of the ticket; W1-29
replaces the checkpoint file and settles most of them.

- **An in-place save during the hook's read–write window can be lost** (DEC-306, accepted by the owner). If the
  session saves its checkpoint in place between the PreCompact hook's read and its write, the new text is cut or
  overwritten. A save by rename, or a save while `tk` runs, is safe. PreCompact runs while the session is idle, and
  the reviewer reached the window only by wrapping the hook's file object. Until W1-29.
- **The warning shows after every compaction** until the session rewrites its checkpoint (DEC-283, confirmed by
  DEC-323). W1-29 may refine it. A write in the same second as the compaction gets no warning, and a file time in the
  future never warns.
- **"Pending owner decisions" is not known to the hook** (DEC-284): the block points to the written part.
- **Not proved:** that a compaction really starts near 300k tokens; the `auto` trigger was never run live. The
  auto-compact setting takes effect only in sessions started after the merge (`840f1e37`).
- **A half-written block** after a kill or a double write failure stays as written text and is injected with the last
  section. Eight compactions at once gave this in about 1 of 40 to 1 of 80 rounds.
- **The modification time is not set back** after a kill, or when the user does not own the file, so the warning is
  missing then.
- **File kinds.** A checkpoint that is a symbolic link is written through to its target. A FIFO hangs both hooks
  until Claude Code's hook timeout. An empty checkpoint gets a block with no written part.
- **Text written after the block** freezes the old block into the written part. Whitespace-only lines after the block
  are dropped.
- **Headings and fences.** Heading variants (lower case, bold, indented, after a byte-order mark) are not found; with
  two RESUME HERE sections the first wins; tilde fences, indented fences and an unclosed fence are not handled; a
  form feed or U+2028 before a heading-like line cuts the section.
- **Sizes.** The 10,000 cap is counted in code points, not UTF-16 units. The block has no size limit. A very long or
  multi-line `GOV_TICKET` breaks the cap's promises and is injected verbatim.
- **Process edges.** A timed-out `tk` leaves its children running; there is no fsync; the message is wrong after a
  failed truncate; the hooks exit 120, not 0, when stdout cannot be written (nothing is blocked).
- **Neither hook reads stdin**, so SessionStart would also inject on `startup` if that source were registered. A
  missing or broken `precompact.py` makes SessionStart inject nothing, silently. A `CLAUDE_PROJECT_DIR` at a
  subdirectory only reports the checkpoint missing.
- **Two stale git-ignored `.pyc` files** remain in `template/governance/kernel/hooks/__pycache__/` in the ticket's
  worktree; they went with the worktree.
- **A guard observation.** The batch 4 engineer wrote its two allowed files with `python3 - <<'EOF'` scripts and the
  guard did not refuse them. Same observation as under W1-15; for W1-46's residual list.

## W1-09 residuals (ticket vendoring, claims and the READY rule, 2026-10-04)

Recorded at W1-09's close, from the ticket lead's summary and the reviewer's findings, three of which were fixed.
None is a defect of the ticket; each names who should settle it.

- **Stale store.** The READY rule reads records from the store as last loaded. A specification reopened, a package
  added or an input superseded after the load leaves tickets READY until the next `gov.store.load`. The store has no
  freshness mark. For W1-13 and W1-26, which call the rule.
- **Packages that do not load block nothing** (with DEC-308): broken frontmatter, no `status`, a status in another
  case, a ticket named by its WBS id. For W1-34 and W1-11.
- **Specification gate edges** (with DEC-307): an empty `specification:` key reads as absent; duplicate record ids
  give an order-dependent answer; a `CLOSED` specification superseded by a draft still counts; any record type
  counts. For W1-13.
- **Holder comparison is on the stripped text.** `" a "` is released by `"a"` and not by itself; an empty lock is
  released by anyone passing `""`.
- **A ticket that is `in_progress` without a lock can be claimed.** DEC-292 left the link between `claim` and
  `in_progress` open. `claim` also accepts `status: Closed` (capitalised) and a ticket with no status.
- **`create` trusts the script's last output line** and does not check the script's sha256 before running it. Not
  reachable with the pinned script. Which copy of `tk` `create` runs in this repository is open under DEC-295: it
  always runs `<root>/governance/kernel/bin/tk`.
- **Acceptance folder cases left open under DEC-293 and DEC-300:** a path naming another ticket's folder, and an
  empty folder, both still count.
- **Raw exceptions instead of `GovError`:** ids `.`, `..` or with a NUL in `holder` and `release`; a lock that is a
  directory; a claims folder that is a file; a release on an unreadable claims folder; `create` when the script is
  missing or fails; a holder that cannot be encoded leaves a stuck empty lock. All fail closed.
- **`blocked` can give an empty reason list** for an unreadable ticket, an unreadable store or an unknown status; a
  reason code for "cannot be read" needs a decision.
- **Only `deps` is read, not `depends_on`.** A record with status `SUPERSEDED` or `REJECTED` but no edge is a good
  input.
- **Minor lock and ticket edges.** A dangling-link lock cannot be released through the interface; with two `status`
  keys the last wins; a lock is keyed by file name, not by the frontmatter id. A claims folder that is a symbolic
  link is recorded under DEC-297.
- **The release `flock` is advisory and POSIX-only.** A lock removed by hand is outside it. The double hold the
  reviewer saw was not reproduced (about 1,800 rounds by the designer, 480 by the lead); the fix rests on the lead's
  reading of the diff.

## W1-12 residuals (readiness schema and proposal templates, 2026-10-04)

Recorded at W1-12's close, from the ticket lead's summaries and a product-spec worker's reading of G-07 and G-09
(DEC-310). None is a defect of the ticket; each names who should settle it.

- **The CIT-E rule is stated only** (DEC-309). The schema carries the source and the extension rule of
  `readiness-dimensions.yaml`, and W1-12's suite goes red when the YAML changes without the schema. The check that a
  change to the taxonomy or to the YAML has a linked CIT-E record is a KPI line of W1-26.
- **The kernel `templates/openspec/` folder holds nothing** (DEC-304, DEC-326). G-07 and G-09 name no path there, and
  OpenSpec reads templates only from the schema's own `templates/` folder. The path left the ticket's `allowed_paths`.
- **Names.** G-07 calls the artefact `feature-readiness`; as built, the schema is `feature-readiness` and the
  artefact is `readiness`, file `readiness.yaml` (DEC-305). G-08, W1-13's source, says the checker reads
  `feature-readiness.md`: DEC-305 supersedes that file name. For W1-13's test design brief.
- **The record lacks profile and capability types.** `readiness.yaml` has no `profile` or declared capability-type
  field, and `cell_states` holds only the state names and `requires: [reason]` on N/A. The readiness YAML's
  `meaning`, `satisfies`, `mandatory`, `rules` and `profiles` are not copied. W1-13 needs them or must read the
  contract YAML.
- **Artifact order.** `readiness` requires `specs`, while `tasks` and `apply` keep their upstream requirements, so
  OpenSpec does not force the record before tasks.
- **`validate --strict` parses only the spec deltas and `.openspec.yaml`**; the proposal, design, tasks and readiness
  files cannot fail it. The stock `spec.md` template fails `--strict`, so the fork replaces it with plain "replace
  this" sentences, one SHALL requirement and one scenario. The other three templates are byte-identical to upstream;
  about 317 lines are upstream `spec-driven` text.
- **Free fields.** `evidence` and `gap_ticket` carry no id pattern, so nothing duplicates the shared id grammars
  (DEC-227). Validation falls to W1-13.
- **Untested:** a `config.yaml` naming an unknown schema makes `openspec new change` exit 1 with "Unknown schema".

## W1-34 residuals (decision-package template, 2026-10-04)

Recorded at W1-34's close, from the ticket lead's summaries. None is a defect of the ticket; each names who should
settle it.

- **Nothing enforces the template.** The tests check what the template lets through: nothing renders a package or
  records an answer. Refusing a package without a recommendation or confidence, or an answer without a date, falls to
  W1-35 and W1-11.
- **The schema does not hold the five `status` values** (DEC-328). `status` is still any non-empty string and extra
  keys are accepted, so the five values, "no second state key", `rank`, `cit` and `constrains` hold only in the
  template and its test. W1-34 could not change schemas.
- **What a declined, revoked or stale package does to waiting tickets** is W1-11's (DEC-308).
- **Choices the sources do not fix.** The CIT id has no grammar (`CIT-0000` is a placeholder). The frontmatter key
  `rank` and its default `P2`. Packages over the cap "wait, highest rank first" (DEC-093 gives only the cap and the
  P1 bypass). "Human-resolvable" is read as "precedence does not settle it, or it is one of MR-6's questions that
  matter". "Only an answered gate of the same CIT permits the next actions" also excludes an open gate, which
  CAP-34.d does not list. The answer form reads `ACCEPTED (who, YYYY-MM-DD)`, not `owner`, because DEC-220 records
  delegated answers under the orchestrator.
- **The rules sit in an HTML comment inside the form**, which the author deletes from a filled package. W1-35's
  skills need to carry the routing, batching and state rules themselves.

## W1-25 residuals (gov checkpoint, 2026-10-04)

Recorded at W1-25's close, from the ticket lead's summary. None is a defect of the ticket; each names who should
settle it.

- **Nothing calls the command yet.** W1-25 builds `gov checkpoint` (write, `--watch`, `--resume`) and the
  fresh-agent-reconstruction check declaration. The calls at a ticket transition, a compaction and a stop are
  W1-29's, W1-49's successor hooks' and W1-30's (DEC-280).
- **"Only orchestrator-role sessions run `gov checkpoint`" (DEC-320) is not enforced by the command.** It rests on
  the guard's path rules: a worker's write to `docs/checkpoints/<ticket>/` is outside its `allowed_paths`.
- **No acceptance case holds the DEC-321 defaults** (240 minutes, 20 commits); one builder test does. Thresholds are
  not range-checked.
- **Numbering and writing.** Two sessions writing the same ticket's checkpoint at once, or on two branches, can take
  the same number: there is no lock, and the write is not atomic. Files in the folder that do not match
  `CP-<ticket>-<NNNN>.md` are ignored.
- **What the watchdog reads.** "Commits since" counts from the commit that added the checkpoint file, across the
  whole history of HEAD; an uncommitted checkpoint, or one not reachable from HEAD, counts 0. It checks that each
  input has an id, a version and a well-formed sha256 and does not re-hash the files, so input drift is not
  detected. The `ticket-transition` reason compares the ticket's status only (`task_status`, DEC-336). `--watch` on
  a ticket whose file is gone answers `TICKET_UNKNOWN` (exit 1).
- **The family check passes when no ticket has a checkpoint.** W1-26 runs it; whether "no checkpoint at all" should
  fail is W1-26's or W1-29's to settle.
- **Without `--json` the `--resume` brief is indented JSON text**, because `main.py` prints every result that way
  (DEC-317). W1-29's SessionStart hook injects that text.
- **The W1-46 builder test `tests/unit/launch/test_command_modules.py` uses not-yet-built commands as stand-ins**
  (`pause`, `close`). It broke when `checkpoint` was built and will break again when W1-28 builds `pause` or W1-30
  builds `close`: that ticket's lead renames the stand-in, as W1-25's did (`9c8fec02`).
- **Workers ran unsandboxed** (interim, DEC-183).

## W1-46 residuals (worker session launcher, 2026-10-04)

Recorded at W1-46's close, from the three ticket-lead summaries and the two reviewer passes. `gov launch` is built;
leads and workers were still started unsandboxed during this ticket (DEC-183). Each item names who should settle it
where that is known; the rest go to EXP-002 and the mid-wave audit.

**What a launched session can still do**

- **A new name under `.gov-runtime/` outside `scratch/`, made at the OS level after launch, is not denied**
  (DEC-311): the sandbox skips glob deny paths on Linux, so only the names that exist at launch and the freeze flag
  carry literal rules. Inferred, not run: a project root whose path contains `*`, `?` or `[` would turn those literal
  rules into patterns the sandbox skips.
- **The shared git directory is writable from a launched session in a linked worktree.** It can commit (tested), and
  it can also create a new file directly in the main repository's `.git`, which includes other branches' refs;
  `.git/hooks` and `.git/config` are refused.
- **The held-out path travels in argv**: the built settings are an inline `--settings` argument, visible in the
  process list, the worker's own Bash included.
- **The per-session temp directory is left behind** after the session ends.
- **A research session starts in the repository root**, so a bare `uv add` is denied until it does `cd <folder>`. A
  new directory a research install creates inside the repository is stopped by neither the fence nor the guard, only
  reported by containment, and not at all if it is gitignored.

**What the launcher does not check**

- `~/.claude/settings.json` is not checked for bypass mode, added directories, `disableAllHooks` or a weak `sandbox`
  block (DEC-313 covers the command line and the project's settings).
- Option prefixes, another letter case and `--dangerously-skip-permissions=true` pass the launcher; the reviewer
  infers the real CLI rejects them, and nobody ran it.
- In force and stricter than some callers expect: `--setting-sources` is refused with any value, and a guard
  registered only in `.claude/settings.local.json` refuses the launch (DEC-314).
- `gov launch` ends with the session's exit code (DEC-332), so a session's own 1 to 4 reads like an API-0002 code;
  a refusal is told apart by its envelope.

**What the guard alone lets through** (left to the sandbox of a launched session)

- **Install spellings for non-research roles:** `env` and `command` prefixes (known from W1-04), `exec`, `nice`,
  `time`, `xargs`, `bash -c`, `python3 -mpip`, `uv pip sync`, `uv tool run`, `npm ci`, `npx`, `yarn add`, `pnpm add`,
  `pipx run`, `cargo add`, `go get`, a pipe into a shell. Stopped only by the empty allowlist and the write fence.
  For research: `uv --directory` or `--project`, `pip install --target` or `--user`, and `cd` behind an assignment,
  `builtin`, `command` or `eval`. An orchestrator subagent in a worker session gets "ask" for an install, not "deny".
- **`ln` behind a wrapper** (`env`, `command`, `nice`, `xargs`, `find -exec`, `bash -c`, backticks).
- **Links the guard does not see made:** a write through a hard link already on disk, or through a link made by an
  interpreter one-liner; replacing a symbolic link that already sits inside the acceptance tests and points into the
  role's paths; a link made by `cp -s` followed by a write in the same command.
- **Other programs that take options after operands** (`touch -d`, `tee`, `rsync`, `dd`) are not read the way `cp`
  and `install` now are.
- **An opaque Bash write is not judged**: an engineer changed a guard file inside its own paths with a Python script
  fed through a here-document, and the guard allowed it, while it refuses the orchestrator's here-documents. The
  holder exception follows a symbolic link: if `.claude/settings.json` were a link into scratch, any role could
  write the path there.
- **On a ticket whose `allowed_paths` name `.tickets/` or `.claude/`**, the guard alone allows writes there; only a
  launched session carries the deny rules. DEC-315 has no exception for such a ticket: in a launched session the
  deny rule stays (fail closed), which is why no headless session could write `.claude/agents/research.md` and the
  owner placed it (DEC-312).

**Where the guard is stricter than needed**

- `ln -t`, `ln --`, a destination that is exactly the top directory of an allowed pattern, `ln <own> <own> -S bak`,
  and a hard link whose source is outside the role's paths even when the source is harmless (a file under `docs/`).
- A link to a protected place plus any other write in the same command; `ln -s <relative name>` plus any other
  write; `cp -t <dir>` with a glob operand that matches nothing; `cp a b dir -p` judges the later sources as write
  targets too.

**The generic command line (DEC-317)**

- A stray command module that hard-exits at import makes `gov --help` and a misspelt command end with exit 0.
- A stray `src/gov/status/command.py` takes over `gov status`; `status` and `check` have no precedence guard.
- No acceptance test shows that a new module alone adds a command, its arguments and its act paths. W1-25 was the
  first user and needed no change to `main.py`.

**Carried to other tickets**

- **W1-08's `systems` snapshot** in the path map was updated at W1-33's close (2026-10-05).
- **The experiments root is the fixed name `experiments/`** (DEC-333); a project key waits for a project that needs
  one.
- **Size.** 819 lines added outside tests against an estimate of 220, about 200 of them the DEC-317 change that
  W1-25's package moved here; 214 acceptance cases were added after implementation, almost all for owner and
  delegated decisions.

## W1-17 residuals (lexical index and shared store, 2026-10-04)

Recorded at W1-17's close, from the ticket lead's two summaries. None is a defect of the ticket; each names who
should settle it where that is known.

- **The index-freshness check is red in this repository** until an orchestrator-role session builds the live index
  (DEC-342, DEC-322). It is also not green on an index that holds no chunk (DEC-345), so a project with no
  governance-class file can never be green. W1-26 and W1-27 take both into account.
- **The index reads the working tree; the record graph reads `HEAD`** (DEC-344). The two can describe different
  states of one file. W1-20 settles what a caller sees.
- **A store without graph tables.** If the index is built before any `gov.store.load`, `store.db` exists without the
  graph tables, and `gov.store.digest` and `connect` fail with a raw SQLite error, not `STORE_MISSING`. The fix is in
  `src/gov/store/`: W1-27, which wires `gov rebuild`.
- **`search` can raise.** A default `search` raises when the filter or git fails (no gitleaks binary, for example)
  and does not return the unavailable mapping of DEC-260. W1-20 catches it or this module changes. A machine without
  `gitleaks` on `PATH` skips the whole W1-17 suite.
- **What a query finds.** A query that starts or ends inside a token (`floor_rules` in `partition_floor_rules`) is
  not found, because FTS5 picks candidate chunks by whole tokens. Other letter case, stems, queries across lines,
  ranking, limits and an empty query are unhandled and untested. CAP-11.a's "every occurrence" holds for whole
  tokens only; W1-20 or W1-41 decides whether that is enough.
- **"2.8 s scale"** is held as 10 s on the search after one edited file; G-20 was not read (DEC-341).
- **No version pin in the store.** A change to the chunker or tokenizer needs `.gov-runtime/` deleted and rebuilt;
  nothing detects it. An untracked path map or `.gitleaks.toml` does not trigger re-judging when it changes; a
  committed map change does, and moves unchanged files in and out of the index.
- **Parents are coarse** (DEC-343). Markdown sections are flat, a `#` line inside a code fence counts as a heading,
  and only `.md` and `.markdown` are documents. A Python parent is the outermost function; a method counts as a
  function, a class body and decorator lines belong to the module, and a file that does not parse is module-only.
- **Line numbers** come from `str.splitlines`, so a form feed or a Unicode line separator shifts the reported line.
  Non-UTF-8 and binary files are decoded with replacement and indexed if the filter lets them through; paths with a
  newline and tracked non-regular files are skipped.
- **Removed text stays in SQLite free pages.** This concerns text that passed the filter earlier, a file that later
  gained a secret included. Concurrent refreshes, and a file replaced between the filter's answer and the read, are
  not handled (the W1-15 residual, unchanged).
- **`lexical.py` imports `gov.secrets.CONFIG_REL`**, which is not in `gov.secrets.__all__`; W1-16 keeps or exports
  the name. The `export_policy`, `embedding_policy` and `permitted_roles` residuals that DEC-289 moved here are
  untested.
- **The carried code under `cli/govbridge/` is untouched**, since `cli/tests` still imports it; its query, store,
  freshness, corpus and git-object modules were not ported.
- **Size.** 370 lines against 240 plus 40 to 60 (DEC-343), docstrings and comments included.
- **Workers ran unsandboxed** (interim, DEC-183). The test designer left a throwaway reference implementation in
  its session scratch directory outside the repository.

## W1-13 residuals (gov readiness, 2026-10-05)

Recorded at W1-13's close, from the ticket lead's summaries and the reviewer's pass. The reviewer's two HIGH findings
were fixed, tests first; the fix was not re-probed by a second reviewer. Each item names who should settle it where
that is known.

**What still lets work through** (DEC-348, DEC-350)

- Nothing stops a direct `openspec archive`, and the READY rule of W1-09 trusts a specification status set by hand:
  `gov readiness` only gives the verdict. W1-26 runs it as a check and fails a `CLOSED` record with a required row
  open; W1-35's change skill runs it before apply and archive.
- **Nothing writes the specification frontmatter yet.** Until W1-12's proposal template or W1-35 writes it, the bare
  `gov readiness` answers `READINESS_INVALID` in any project that holds a change written from today's template
  (every folder under `openspec/changes/` except `archive` counts as a change, even an empty one). W1-26 must know
  this before it wires the bare form as a check. `--specification` and `--ticket` judge the named one alone.
- `gap_ticket` is reported as written, even when it names no ticket or a closed one; that check is W1-26's.
- Content is not judged: a reason of `.` or evidence of `['TBD']` passes. An N/A reason made only of a zero-width
  space passes; empty, null, absent, spaces, tabs and a no-break space are rejected.

**`gov.readiness.close`** (DEC-349; no command or skill calls it yet)

- It accepts any file in `.tickets/` with `class: audit` and `audits: <id>` as the audit ticket: a closed one, one
  with another role, a hand-written one. A specification closed again after its audit ticket was closed gets no new
  one. For W1-26 or W1-35.
- A record with no plain `status:` line passes the read command; `close` then creates the audit ticket and fails
  with a raw error, leaving the record unclosed (a retry reuses the ticket). An interrupted `close` can leave an
  orphan ticket; a read-only `proposal.md` fails after the ticket exists; a relative root other than `.` fails.
- The specification id goes unchecked into the audit ticket's `allowed_paths` (`docs/audit/<id>/**`).
- "Fresh" and "authored none of the audited files" (MR-4) rest on the orchestrator's session rules.

**How records are read**

- Duplicated YAML keys are read last-wins (`profile: FULL` then `profile: LITE` is judged at LITE). Row identity is
  loose: `n: 3.0` counts as row 3, `n: true` as row 1, a row's `key` is never compared, and rows numbered outside 1
  to 26 are ignored silently.
- `--ticket` on a ticket with no `specification` key answers `SPECIFICATION_NOT_FOUND` (exit 1), although DEC-307
  says such a ticket is not held: a caller that gates on this code would block it.

**The taxonomy is held in code**

- The 26 row keys, the ten mandatory rows of DEC-085 and the capability-type table are constants in
  `src/gov/readiness/checker.py`, compared by a builder test with `docs/contract/readiness-dimensions.yaml`. A
  project schema whose rows or table differ makes every specification in that project `READINESS_INVALID`. So a
  governed taxonomy change (CAP-30.e) has to change the checker together with the schema and the Contract file.

**Records**

- 299 lines against 170 plus about 40 for `close`; 18 acceptance cases were added after implementation, from the
  reviewer's findings. Workers ran unsandboxed (interim, DEC-183).

## W1-14 residuals (proposal-to-ticket bridge, 2026-10-05)

Recorded at W1-14's close, from the ticket lead's summary. None is a defect of the ticket; each names who should
settle it where that is known.

- **Nothing calls `gov.tasks.bridge.derive` yet**, and `gov.tasks` does not export it (that file is outside the
  ticket's paths). W1-35's planning skill calls it.
- **Nothing teaches authors the task block** (DEC-355). W1-12's `tasks.md` template as delivered is refused. For
  W1-35 or a template change, together with the specification frontmatter (DEC-350).
- **Re-run edges** (DEC-356). A `- [x]` task gets an open ticket; a task edited after derivation never updates its
  ticket, and cycle detection then uses the ticket's `deps`; a removed task's ticket stays, unreported; indented
  sub-task lines are ignored. A hand-written ticket with the same `specification` and `task` is taken as that
  task's ticket.
- **The acceptance-path rule** calls two private names of the guard (`gov.guard.decide._match_pattern` and
  `_is_under_acceptance`), so a rename there breaks the bridge. A glob that reaches the acceptance tests without
  naming the folder (`**/*.py`) is not refused by the bridge; the guard still denies the write.
- **`role` is not checked against the roster**: an unknown role is derived and counts as an implementer for the
  acceptance-path rule. A dependency on an existing ticket accepts any file in `.tickets/`, closed or unreadable.
- **Failures part-way.** If `gov.tasks.create` fails after the ticket script wrote a file, that file is not cleaned
  up; a description that starts with `-` triggers it. Two runs at once on one change can each create a ticket per
  task. The ticket id prefix comes from the project folder name, so a name outside letters and digits gives ids the
  ticket schema rejects (W1-09's `create`).
- **Codes beyond the tests:** `TASKS_NOT_FOUND` and `TICKET_FAILED`.
- **Size and process.** 180 lines against 120. The lead had the engineer build before the five packages were
  decided; they were then decided as built (DEC-355, DEC-356). Workers ran unsandboxed (interim, DEC-183).

## W1-33 residuals (Wave 1 role definitions, 2026-10-05)

Recorded at W1-33's close, from the closing ticket lead's summary. The first lead's own list was not in its returned
result, so this list is the closing lead's; none is a defect of the ticket.

- **The definitions under `.claude/agents/` were placed by the owner** (`0f8b0d29`, DEC-352 P-2), because a headless
  session is refused writes there. They count as generated until W1-38 produces the same files from the same sources.
- **Permission classes are mapped as families** (DEC-352 P-3): `NETWORK_*`, `DB_*`, `CLOUD_*` and `DEPLOY_*`, not each
  member class of Framework §32. For the mid-wave audit to weigh.
- **Orchestrator and product-spec grants** (DEC-352 P-4): the orchestrator has `NETWORK_*` allowed and the database,
  cloud, CI-trigger and deploy classes denied; product-spec has all denied. In these two unsandboxed sessions no
  mechanism holds the denials, and the role files say so.
- **Model tier.** No decision assigns one. The files say "standard" for the four workers and "the model of the
  session the owner starts" for the orchestrator; there is no `model:` frontmatter, so nothing enforces it.
- **The product-spec session.** `gov launch` has no product-spec role, so such a worker still starts under DEC-183
  (DEC-371). Its roster entry has no `session` or `network_profile`.
- **Web tools against `NETWORK_*: denied`.** The worker role files keep WebSearch and WebFetch available outside the
  sandbox (DEC-158) and read the class as the sandbox's network grant. No source settles whether the web tools count
  as a `NETWORK_*` class.
- **`SECRET_READ` and `SYSTEM_INSTALL`.** No guard rule stops a secret read; the denial rests on DEC-074 Q9. An
  orchestrator system install without `sudo` gets the same `ask` as any install.
- **An auditor on another role's ticket.** The launcher starts an auditor on any `in_progress` ticket, but the guard
  gives it a write path only when the ticket's `role` is independent-auditor. The role file states this.
- **The roster's header comment** still says the other roles' entries "come with their own tickets"; it was left
  byte-identical so the research-unchanged test holds.
- **Size.** 306 lines added and 25 removed outside tests, against 300; the tests are 1,079 lines.

## Observations from launched worker sessions (2026-10-05, the first round under DEC-371)

Reported by the W1-19 and W1-28 ticket leads; for W1-32, EXP-002 and the mid-wave audit.

- **A worker copied the held-out file.** The W1-28 test designer bulk-copied the tracked files into its session
  scratchpad for a throwaway stand-in, which took `governance/project/held-out.yaml` with it. It reports it never
  read it; its deletes were refused. The owner removed that folder
  (`/tmp/gov-launch-independent-test-designer-5e58yicw`, 3.4 GB) through the operator (DEC-376). Every worker brief
  now forbids a bulk copy of the tree.
- **Test fixtures copied the held-out file too.** The owner found and deleted 17 more copies, all inside pytest's
  temporary test projects under one launched engineer session's temp folder (`/tmp/gov-launch-engineer-_foa_zpg/`):
  fixtures that copy the working tree took the file with them. None remain. DEC-385 makes every copying fixture
  leave the file out (W1-28). Until that is merged, each run of the copying suites by a launched worker makes new
  copies in its session temp folder.
- **Launcher temp folders pile up.** 78 other `gov-launch-*` folders remained in `/tmp` on 2026-10-05. DEC-386 makes
  the launcher remove its folder at the session's end (W1-28); the operator clears the old ones when no lead is
  running.
- **A worker cannot delete its own scratchpad**: the sandbox refuses `rm -rf` there, so throwaway stand-ins and the
  per-session temp directory stay (the W1-46 residual, seen again).
- **The freeze flag's path is a placeholder inside the sandbox.** A launched session sees `.gov-runtime/freeze` as a
  character device whether or not a flag exists, so code that reads the flag by existence sees the tree as paused
  from inside a worker sandbox. W1-28's suite accepts only that placeholder; W1-32's `gov status` and any engineer's
  own test runs must take it into account.
- **Untracked placeholder files** (`.bashrc`, `.gitconfig`, `.idea`, `docs/source` and others) were seen at a
  worktree's root during a launched session and were gone after it.
- **A Python script fed by a here-document wrote a file inside the worker's paths** and the guard did not stop it
  (the W1-15 residual, seen again).
- **A read beyond DEC-370**: the W1-19 designer's search for G-20 also returned G-17's one row (package DP-7, with
  the owner).

## W1-16 residuals (codebase-memory wrapper, 2026-10-05)

Recorded at W1-16's close, from the four ticket lead rounds' summaries. Fixed findings are left out.

- **The 60 % line is measured on the test designer's own 26 questions** (DEC-377): no S0b2 C1 question set exists.
  The designer's throwaway stand-in scored 26 of 26, so the line is easy to pass. The comparable measurement is
  W1-42's (hit@5 on the dev query set's code classes).
- **The W1-15 gaps apply to the wrapper unchanged:** a hard link to a product-data file is indexed, and a file
  replaced between the filter's answer and the copy is indexed. The window is the whole filter run.
- **A failed re-index leaves no index** until the next successful run (it fails closed; the index is rebuildable).
  One file with a non-UTF-8 name makes the repository unindexable, with a traceback.
- **A tracked file that `.gitignore` names** is staged but missing from the graph, without a message.
- **The graph is cached per process:** a long-lived process does not see another process's re-index. Answers load
  the whole graph into memory once per process, untested at the DEC-078 envelope.
- **`dead_code` lists entry points and test functions;** the tool's similarity edges are not counted as a use.
- **A rename is a symbol rename only** (DP-3); a file or folder move is not tested.
- **Untested refusals:** a symbolic link below `.gov-runtime`; the query functions refuse the same roots as `index`,
  and only `index` is tested.
- **Token rule (DEC-325, DEC-339):** identifiers with one digit or one capital are still flagged; a lower-case-only
  body, a lower-case run followed by `.` and digits, a rest of exactly 15 characters after a leading `_` or `-`, and
  two leading separators (`sk___…`) are not flagged.
- **gitleaks' built-in rules stay sheltered by its own global allowlist** (DEC-347): the second scan covers the
  project's rules only. A project rule that only modifies a default rule keeps a single scan. The uuid stopword is
  covered by the second scan in principle, and no test shows it.
- **`stores_with_secrets` also gets the second scan**, which is stricter than the letter of DEC-347.
- **The filter costs two gitleaks runs per file** (about +55 % on the W1-15 and W1-17 suites, measured under load);
  batching stays the residual of DEC-339.
- **The daemon directory is under shared `/tmp`** (`/tmp/gov-cbm-<uid>/<id>`, DEC-338, DEC-346). Nothing removes a
  repository's lock and turn files there. The wrapper refuses a folder that is a link or not the user's; only a
  builder test holds that check.
- **The loopback UI (DEC-362, as built under DEC-389):** a daemon already running with the UI on keeps port 9749
  open until it ends, about a second after its last call; not tested, by design. Any call, also `projects(root)` on a
  never-indexed repository, now creates the home with `config.json` and `_config.db`; a refused root is still
  refused before anything is written. Each wrapper call starts two processes; the added time was not measured.
- **Cases that need namespaces:** the six DEC-338 cases and the nine UI cases run in a private user, mount or
  network namespace and skip on a machine without them. All ran here.
- **The suite is heavy:** 166 cases in about eleven and a half minutes. Run it alone;
  `test_this_repository_is_not_indexed_by_the_run` failed once when other tool calls ran in the same tree.
- **The suite's `__pycache__` holds planted strings whole** (untracked and git-ignored; a plain gitleaks run over
  the folder reports them). No committed file holds one.
- **The README's fifth-batch section still says its red run was not run;** the lead observed it (8 failed, 1
  passed). Only a test designer may edit that file.
- **Sandbox:** a launched worker cannot run this suite (`/tmp/w16-…` is read-only there, and the daemon's socket is
  refused); the lead runs it. A headless engineer lost its turn to a background test run once; briefs now say to run
  tests in the foreground.
- **Guard gap, seen again:** here-document Bash writes inside a worker's paths were accepted several times and
  refused at other times.
- **Left under `/tmp`:** `/tmp/w16-c1_yis2q` (four empty folders) and possibly
  `/tmp/gov-launch-engineer-9n8d84gs/rt`. `/tmp/cbm-daemon-1000` and `/tmp/gov-cbm-1000` stay by decision.
  `~/.cache/codebase-memory-mcp` was never changed, and no worktree of this repository was indexed.
- **Size.** Production code and rules +282 / −45 against an estimate of 50; 42 cases were added after
  implementation, each by a delegated or owner decision.

## W1-28 residuals (gov pause, copying fixtures and two launcher changes, 2026-10-05)

Recorded at W1-28's close, from the closing ticket lead's summary and its reviewer's findings (none high).

- **Two earlier residuals end with this merge:** the launcher's temp directory is no longer left behind on any exit
  the launcher controls (W1-46), and a product-spec worker is launched sandboxed, with an empty network allowlist
  and held to a ticket of its own role, so the DEC-183 form is ended (W1-33, DEC-371).
- **The temp folder still stays** when the launcher is killed outright, on SIGTERM or SIGHUP (the session then lives
  on), or when the removal fails; a failed removal is a traceback and the session's exit code is lost. DEC-392 fixes
  the last three; W1-32 carries it.
- **Removal is by name:** if the folder is renamed and another directory put at its path, that one is removed. It
  needs write access to the parent, which the sandbox does not give. Not run: a launcher `TMPDIR` that does not
  exist.
- **A worker's scratchpad is gone at the session's end.** Briefs now tell workers to return results in their final
  message or under `.gov-runtime/scratch/`.
- **The DEC-385 exclusion is one exact path.** Another name, a hard link or an absolute symbolic link would be
  copied. The check that fails when a fixture copies the file again does not see a helper called with the root,
  `tarfile`, a copy of `governance/` by name, or `tests/unit/`. Only W1-05's and W1-07's fixtures copied the whole
  tree (W1-25 uses W1-07's).
- **The two whole-tree fixtures still copy `.claude/settings.json`** with its held-out deny line into every
  temporary project; W1-46's and W1-47's fixtures strip it (package DP-15, with the owner).
- **Copies made before the merge:** 1461 files of the held-out file's name were counted, by path only, under
  `/tmp/pytest-of-usain` on 2026-10-05, from earlier runs of the copying fixtures in every tree. None was opened; the
  owner has them removed.
- **The product-spec role file and its agent definition** still say the launcher does not start that role (package
  DP-12, with the owner). `gov launch` by WBS id sets `GOV_TICKET` to the WBS id, and a ticket key written twice
  takes the last value; both are older launcher behaviour that now also holds for product-spec.
- **Pause, as built and held by no test:** untracked files do not make a tree dirty; a conflicting revert is undone
  with `git reset --hard` to the `HEAD` from before the rollback; an empty `GOV_ROLE` is refused, not read as the
  owner; record commits also carry `Role:`.
- **A launched test designer cannot run the live-session cases** (W1-46: 36, W1-25: 3): the sandbox refuses the API
  host. The lead runs them.
- **Latency (DEC-372):** two occurrences during this ticket's rounds, both `test_decision_p95_is_under_100_ms`
  (W1-02) under load, one at 106 ms; each passed alone. None in the post-merge run.
- **Size.** `gov pause` is 120 lines against 80 to 100; the launcher changed by +15 / −6.

## W1-20 residuals (gov closure, 2026-10-05)

Recorded at W1-20's close, from the ticket lead rounds' summaries.

- **Depth numbers are placeholders:** radius R0 and R1 give 1, R2 gives 3, R3 and above give 8 (DEC-035's values,
  read as hops, DEC-391).
- **A start id that is no record depends on the machine:** the stopping reason is `FACET_UNAVAILABLE` without the
  code tool and `UNRESOLVED_IDS` with it (DEC-396). Three cases therefore hold only "not `CLOSURE_COMPLETE`".
- **The symbol side is tested only in the lead's run:** the ten `local_only` cases cannot run in a launched worker's
  sandbox, and `test_a_repository_without_a_code_index_states_the_facet_unavailable` passes inside a sandbox for the
  wrong reason (the sandbox's refusal, not a missing index).
- **`callees` in the wrapper** (DEC-391) has one unit case; against the real tool it is held by two `local_only`
  cases of this suite.
- **`uncommitted` when git fails:** `git status` runs with `check=True`, so it ends in a traceback, not an envelope.
  It fails closed.
- **`HEAD` among the store's commits is not checked;** left to W1-27 (DEC-391 DP-7).
- **Not tested:** two symbols of one name, methods, `referenced_by` on a gap. The reranker's own process is not
  watched by the no-model test.
- **W1-07's `closure` cases** run in a project without a store, so they exercise `STORE_MISSING` only.
- **`S0a-G-03`**, one of the ticket's sources, is not in the tree; no test was derived from it.
- **The two W1-17 residual lines that name W1-20** (`search` can raise; whole-token matching) are not settled here:
  a closure never calls the lexical index. They move on to W1-21 or W1-41.
- **Two branches that revise the same line of an acceptance test cannot be merged:** W1-28's and W1-20's planned
  W1-07 revisions conflicted, a conflicted merge restores acceptance tests from `HEAD` in a lead's call, and nobody
  but a test designer writes them. A designer moved this ticket's revision onto lines of its own before the merge.
  Briefs now say so.
- **Rule slips the guard did not refuse:** an engineer amended a commit of its own before its second (nothing
  pushed; containment flagged it), and wrote files with a Python here-document and `sed -i`, all inside its paths.
- **Run time:** the suite takes about four and a half minutes alone.
- **Size.** Source +119 / −1 against an estimate of 100 (closure 111, wrapper 8).

## W1-19 residuals (semantic retrieval, RRF and rerank, 2026-10-06)

Recorded at W1-19's close, from the ticket lead rounds' summaries. Measured on the dev tiers at the close: mean hit@5
83.33 (pass line 80, DEC-414), warm p95 0.317 s (limit 0.5), the rerank process's peak RAM 2.29 GB (limit 2.5).

- **The 85 baseline is not reached:** query `DQ-B-03` (class decisions) is missed, the one query between 83.3 and
  S0b2's 85. R1's whole-file chunking gives 85.0 on the dev tiers and was not built; the parent-bounded chunks stay
  (DEC-343, DEC-414). 85 is re-measured at the Wave 1 exit run (W1-42) and at qualification.
- **Backlog, W1-17's area, a later wave:** a ranked lexical route for exact identifiers (DEC-414). Today the lexical
  route is an exact-string search and contributes nothing on natural-language questions, so the fusion joins one
  route in practice.
- **One case holds both hit@5 lines** (success 2 and failure 1): since DEC-414 they are the same line.
- **Vectors built before the 512-character cut are not detected as stale:** the manifest records the model and its
  revision, not the cut. Only stores built by the ticket's branch before that change are affected; a rebuild clears
  it.
- **`template/**` is not embedded:** its path-map value `embedded, except vendored code` is read as not embedded
  (DEC-388), so it is found by the lexical route only. Splitting the vendored paths is a path-map edit.
- **Vectors are in a plain table with a brute-force cosine scan per query,** not a `vec0` virtual table, so that the
  store stays readable without the extension. Not measured beyond the dev tiers.
- **`fusion.search` returns at most 30 hits,** whatever `limit` says.
- **A reranker process that dies after loading** (for example out of GPU memory) makes `score` raise; it is not
  handled as "absent" (DEC-374 covers only an absent environment or snapshot).
- **The reranker worker writes a progress bar and one prompt line** to the caller's standard error at first load.
- **Offline loading of the reranker is checked only where the snapshot is absent.**
- **The rerank process's RAM margin is about 0.2 GB** (2.24 to 2.29 GB measured against 2.5).
- **Two dev queries have no gold path,** which caps the mean at 96.3 (DEC-388). The `deletable` class stays at 40 in
  R1 and here: its gold files are secret-like and filtered.
- **`semantic.py` imports the private `_matches` from `gov.secrets`.**
- **The model-dependent cases cannot run in a launched worker's sandbox** (no network profile, no GPU, no model
  cache): the ticket lead ran them.
- **W1-16's `test_this_repository_is_not_indexed_by_the_run` fails when any session's hook writes a snapshot** under
  the tree's `.gov-runtime/snapshots/` during the run; it passes with nothing else calling tools in that tree.
- **Latency occurrence (DEC-372):** in the regression after the merge, W1-02's
  `test_decision_p95_is_under_100_ms[frozen-deny]` failed under load and passed alone.
- **`ollama serve` is left running** by the code under test (DEC-261).

## W1-11 residuals (decision checker and owner-approval facts, 2026-10-06)

- **Speed, for W1-26:** 200 `ACTIVE` decisions under 20,000 commits take 5 to 6 minutes and about 1 GB (341 s,
  1.07 GB measured; linear in decisions times commits, one `cat-file --batch` round trip per decision per commit).
  On this repository the checker takes 0.24 s. Too slow at that size for every `gov check`: a cache, a skip list or
  an early stop is needed.
- **A `tree:0` partial clone fetches through the merge helper:** its `diff-tree` runs without `GIT_NO_LAZY_FETCH`.
  It fails closed (`GovError`), but it is a network read. The fix is in W1-50's helper module
  (`gov.guard.containment_merge`), outside this ticket's paths.
- **`GIT_TRACE` reaches the helper's git** and writes a trace file; no answer changes. Same module.
- **Exact comparisons of status and ids:** `ACTIVE` is case-sensitive; `status: active` passes silently.
- **`type: decision` with an empty `id:`** is followed as `"None"` or `""`, not reported as a decision without id.
  Only an owner-set `ACTIVE` one with a deliberately empty id passes.
- **Heads that look like frontmatter but are not read as such:** a zero-width space, word joiner, form feed or
  vertical tab before `---`; UTF-16 without BOM, UTF-32, spaces only before `---`. DEC-387 names five heads and the
  suite tests those five; the others pass silently and need a deliberate author.
- **Edits that keep `ACTIVE` pass:** an agent that edits the body of an approved decision and keeps its status is
  not flagged. By design (DEC-360).
- **Backdating:** the author date is not compared with the committer date.
- **A signature as the stricter approval fact** (DEC-360) is not built or tested.
- **False alarms on merges, all flagged where a reader would pass them:** two branches edit the body of an approved
  `ACTIVE` decision and git combines them cleanly; an agent resolves a conflict in an `ACTIVE` body; an agent's
  squash merge of an owner-approved branch; the owner approved on both sides with two texts and an agent keeps
  one; a non-UTF-8 file name (every brought decision is flagged); the owner's `ACTIVE` at a non-UTF-8 path; the
  owner's merge with 25 parents. A shallow clone gives `GovError`.
- **Raw exceptions that fail closed:** deeply nested YAML raises a bare `RecursionError`, not `GovError`.
- **Tickets waiting on a dead package are matched by file stem:** a ticket under `.tickets/sub/` is not found.
- **A dead package without `id` fails no ticket;** the schema requires `id`.
- **Gates:** only the key `approval` is read (DEC-331). `Approval:`, `approvals:`, `approved_by:`, an empty
  `approval:`, and `.yaml` or `.MD` files are silent.
- **Overlapping ids** are tested only for identical digit strings; `ADR-0001` beside `DEC-001` is not.
- **The checker imports private helpers from the store's loader** (`_frontmatter`, `_ids`, `TRAILER_RULE_DATE`).
  The loader's `_frontmatter` uses `\x1f` as a marker; a file holding that byte is the loader's matter.
- **On this repository the approval rule judged nothing:** 3 decision files, all `PROPOSED`, and no `Role: owner`
  commit that sets one `ACTIVE`. 181 real merges were replayed through the helper; none raised.
- **W1-16's `test_this_repository_is_not_indexed_by_the_run`** was killed once under load in the lead's run and
  passed alone (166 passed).

## W1-50 residuals (containment by commit trailers, merges, and the freeze, 2026-10-06)

Both branches are merged (`6a978dbc`, `ad392210`). The regression after each was green on every suite.

### Containment by trailers and merges

- **Trailers are self-declared:** the whole check rests on them being truthful. In an orchestrator's own call an
  ordinary commit with test designer trailers passes under `tests/acceptance/**` (DEC-255, DEC-319); only the
  merge-commit route is closed (DEC-410 DP-27). With several `Role` values on one commit, one worker value is
  enough.
- **Findings that are records (DEC-254, DEC-401):** an owner commit that arrives in a move; the commits of
  `gov pause --rollback`; a worker's commit on the lead's waiting call, attributed to the lead; the lead's
  `Role: orchestrator` ticket commit arriving in a worker's call (DEC-319). No decision says whether these stay
  records after this ticket closes.
- **Real merges the rules flag (records):** `5922e24e` (W1-20's merge-back, two W1-07 test files changed on both
  sides), `135ed94e` (the first freeze branch, never merged) and `c90de3b0` (the rebuilt freeze branch's aligning
  merge). Aligning a file does not clear the both-sides rule: only one side back at the merge base's content, or a
  merge-back first (flagged once), gives a silent merge.
- **Noise:** git's clean combination of two orchestrator edits of one ticket file is flagged.
- **An uncommitted edit of an acceptance test is not restored** when a merge commit of the same orchestrator call
  is flagged for that path; the finding names the path.
- **A test both sides changed in the same way** is the merge's own with one merge base (DEC-417); with several
  bases the whole merge fails closed instead.
- **Whole-move findings that name no path (fail closed, nothing attributed):** a non-UTF-8 file name or trailer
  value, a signed commit with `log.showSignature`, a git call over its 10 s limit, a shallow clone, a merge commit
  over 24 parents, a move needing more than 3000 git processes for its merges (DEC-417; recorded as "not a forward
  move" without the reason). A merge in a worker's call names only the merge commits' own ticket files and tests.
- **`read_merge` gives no bound for a whole move;** a caller that reads many merges bounds itself. It takes only a
  full lower-case commit id.
- **Git settings not pinned in the check's calls:** the `GIT_CONFIG_*` family (not writable by an agent's Bash
  call into the hook's environment), `core.commentString`, `trailer.<name>.key` (can add a `Role` or `Task`
  reading, never remove one); `GIT_TRACE` and a `tree:0` partial clone's lazy fetch reach the helper's git (found
  by W1-11's review). W1-03's git calls still obey local configuration. git's grafts hint is prepended to git
  error texts.
- **Two committed ticket files with the same `wbs_id`:** the first in file-name order wins; not a finding.
- **A late commit on a closed ticket passes** when reopen and re-close commits follow it in the same move; a close
  made only by a merge commit flags legitimate work from before the close.
- **The names `tests/acceptance` and `.tickets` themselves** (a link or gitlink at exactly that name) are not
  matched.
- **DEC-182's message-body fallback** for commits before 2026-10-03 is not used by this check.
- **Unseen characters inside the word** (`ow ner`, a zero-width space) are read as `Role: owner`: stricter than
  the decision's words.
- **KPI wording:** success line 2 and failure line 1 of the ticket are not amended for DEC-410 DP-24 and DP-26: a
  merge whose commits each pass is a finding when a test or ticket file was changed on both sides.
- **Stale docstrings** in several W1-50 test files still call decided packages open; the README carries the
  update. Stale text in the READMEs of W1-02, W1-28 and W1-46.
- **`.claude/settings.json` holds no `timeout` key for the hooks;** the 30 s is the test harness's figure.
- **A launched test designer cannot `rm`,** and the orchestrator cannot delete under `tests/acceptance/`: a
  leftover there needs the owner.
- **Here-documents that write nothing** were run by several workers and let through by the guard.

### The freeze

- **With the owner (2026-10-06), a fail-open:** an opaque command (`python3 -c`, `perl -e`, a heredoc-fed script)
  can remove, empty or forge the freeze flag, and remove the snapshots the flag comparison needs, with no finding.
  The guard reads no write target out of such a command, and the comparison answers nothing without a snapshot.
- **The lift-form rule (DEC-409 rule 3) is passed by** a line continuation, ANSI-C quoting, `env -S`, a
  heredoc-fed script, and a script written with the Write tool. Obfuscated forms are a residual by the decision.
- **A real freeze stops only what the guard reads as a write.**
- **A forged snapshot can conjure a freeze** (theoretical).
- **Things at the flag's path:** a directory there blocks pause, `--cancel-agents` and `--rollback` although the
  tree reads frozen (the owner removes it by hand); a regular file at `.gov-runtime` reads as no freeze and makes
  a pause impossible; the link check on `.gov-runtime` runs once, before the write.
- **A killed pause leaves a `freeze.<random>` file** that nothing removes and that `gov launch` then denies by
  name. The flag is not synced to disk before the rename.
- **`gov pause --root <missing path>`** creates the path and reports "paused".
- **A refusal text says "stays frozen"** without asking the guard's reader.
- **After a rollback that reverts a commit touching the flag's path** the tree is dirty there, and a later
  `--rollback` refuses until the owner sorts it out.
- **A pause from inside a sandboxed session** whose flag path is a mount fails (inferred); the orchestrator pauses
  from outside a sandbox. The sandbox's clean-up was observed with one session, not with two overlapping.
- **A long `TMPDIR` makes a launched session's sandbox fail to start** ("bridge sockets"), and the session still
  exits 0.
- **The record is one unbounded line per allowed call;** `_append_finding` and containment's two writers follow
  links and block on a pipe; the hook is slow on huge commands; an install answered "ask" is still recorded.
- **A session's guard is its own tree's code.**
- **Unpinned choices, fine as built (DEC-412):** the error codes `PAUSE_RUNTIME_LINKED`, `PAUSE_NOT_SET`,
  `PAUSE_NOT_LIFTED`; flag mode 0600.
- **The `local_only` mark is not registered for the W1-50 folder** (2 warnings in the suite).

## W1-21 residuals (gov retrieve with completeness, 2026-10-06)

- **Measured on the dev tiers:** mean hit@5 81.67 against the pass line of 80 (DEC-425); 10 queries missed
  (DQ-A-07, DQ-A-09, DQ-A-10, DQ-A-13, DQ-A-18, DQ-A-21, DQ-A-24, DQ-B-03, DQ-B-14, DQ-B-28). Forbidden citations 2,
  at the baseline of 2 with no margin: DQ-B-12 cites `docs/adr/adr-003.md`, DQ-B-13 cites
  `pyargus/src/pyargus/imaging/old_gridder.py`. One more is a red check.
- **`batch_size` of zero or less gives a zero-progress continuation:** empty bundles with the same token, for as
  long as the caller continues. No evidence, no completeness claimed, no forbidden citation.
- **A citation's `sha256` is the hash of the cited span.** The suite's own helper accepts the whole file's hash
  too; W1-22's validator must not.
- **`batch_size=None` and an explicit 10 give equal bundles and different continuation tokens.**
- **`S0a-G-06` was read by nobody:** its text is in none of the places a worker may read, and the launcher refuses
  a product-spec worker for an engineer's ticket. No case is derived from it. With the owner.
- **The model-dependent cases cannot run in a launched worker's sandbox;** the lead ran them. In the regression
  they run beside other suites and passed there (126 passed).
- **The ticket was built far above its estimate:** 453 source lines against 300, and 2,400 lines of tests.
- **Acceptance tests revised after implementation:** the green family-check case (it needs the real models,
  `2165b706`); `tests/acceptance/W1-07/w1_07_support.py` aligned before the merge (owner decision, DEC-412,
  `500089fe`). The merge-back `df16fde6` is flagged by containment for that path: a record (DEC-254).
- **Every command ticket adds lines to `tests/acceptance/W1-07/w1_07_support.py`,** so each one that merges after
  another needs that alignment and leaves one flagged merge.
- **W1-46's live sessions:** 23 errors in the regression after the merge, run beside the other suites (a launched
  session did not finish its probe); 493 passed alone.
- **`ollama serve` is left running** by the code under test (DEC-261).

## Mid-wave audit (DEC-249, 2026-10-06)

A fresh read-only independent auditor, in its own worktree at `734d7dfd`, checked the 31 closed tickets against
Contract v4.1. Verdict: 31 pass (21 clean, 10 with notes), none failed, no covers item claimed and missing, no
contradiction between tickets. Depth: it ran 12 suites itself (the guard, containment, installs, the launcher, the
decision checker, the secrets filter among them) and read the others' tests and source through read-only
sub-agents; the model-dependent and live-session cases, and W1-16's and W1-21's whole suites, were read and not
run. The report is kept in the orchestrator's log folder.

- **MWA-01, high: opaque commands defeat the freeze.** The same fail-open that W1-50's last review found (see
  W1-50's residuals). The auditor names it the first risk to the exit audit (CAP-05.a). With the owner.
- **MWA-02, medium: acceptance tests added after implementation are systematic** (W1-09 15 cases, W1-11 about 44%
  of its suite, W1-20, W1-21), each batch by the test designer and red before its fix (DEC-136). MR-3's words are
  "before implementation": the exit auditor may read this as a standing exception to a master rule. With the
  owner.
- **MWA-03, medium: retrieval passes with thin margins** (hit@5 81.67 against 80; 2 forbidden citations against
  2). Known (DEC-414, DEC-425); re-measured at W1-42 and at qualification.
- **MWA-04, low: W1-03's "and at gov close" is untested.** `gov close` is W1-30, whose KPI line already has it run
  the containment check; the test belongs there.
- **MWA-05, low: CAP-08.a's `owner` and `links` filters are not built** (W1-10; no KPI line names them, no record
  carries an `owner` field). No open ticket picks them up. With the owner.
- **MWA-06, low: W1-10's load-time line runs only where the dev tiers are configured** (`local_only`); it runs in
  this machine's regression.
- **MWA-07, low: four changes outside a ticket's paths, each explained** (W1-16 the tool registry, W1-20 and W1-21
  W1-07's shared test files, W1-28 the roster).
- **MWA-08, low: W1-01's "denied in every session settings file" is shown by the file's presence,** not by parsing
  its rule against what the guard enforces.

The owner's answers (2026-10-06): MWA-01 is built on W1-50 as a mirror of the freeze outside the repository
(DEC-429); MWA-02 is how MR-3 is met, and the exit auditor is told so (DEC-430); **backlog, a later wave: the
`owner` and `links` filters of CAP-08.a, a known partial of W1-10 (DEC-431).**

## W1-44 residuals (Phase-2 lessons as lesson records, 2026-10-06)

- **Each lesson constrains only its own ticket** (`DAEO-wqd6`), which is what makes `gov retrieve` return it there;
  `L-0077` (the anti-snowball rule) also constrains W1-30 (DEC-435). Which other tickets each lesson constrains
  is not decided.
- **The records are `state_class: HISTORICAL`:** a lesson is not authority (CAP-41.b). A ticket that needs the
  rule as authority cites the owner record, not the lesson.
- **Severities and lifecycles were chosen by the product-spec worker** and stand as written (DEC-433).
- **`L-0074` was written from DEC-041 and DEC-046 in the register,** not from an original lesson text; the three
  owner records were read in the archived `docs/source/` (DEC-426, rule C).
- **"A lesson restates policy as authority" (failure line 2)** is checked by the record's fields, not by reading
  its prose.

## W1-22 residuals (evidence validator and zero-result canaries, 2026-10-06)

- **Canaries exist for the lexical and the semantic index only.** DEC-037 also names the code index
  (codebase-memory); it is queried by symbol, not by text, and needs another query type in the runner. Left to
  W1-27 (`gov doctor`) or a later ticket.
- **Nothing runs the canaries after a reindex yet.** `run_canaries(root)` stands alone; the reindex of W1-17 and
  W1-19 does not call it. `gov doctor` (W1-27) is its first caller.
- **The canary runner reads its declarations from a module-level path,** not from a parameter; a test of other
  declarations patches it.
- **The canary result has a `reason` field** where a declaration is empty, null or malformed (reported as
  `FACET_UNAVAILABLE`, never as available). W1-27 is the first consumer.
- **The validator checks a citation's `sha256` against the cited span only** (DEC-435).
- **Two engineer commits (`7fbfae18`, `f6d88832`) and the lead's merge of the integration branch (`613b8f9e`)
  carry no `Role:` trailer.** They change no acceptance test; the containment check judged them against the
  caller. Records.
- **Review rounds:** two; the fail-open found after them (an empty canary declaration counted as available) was
  fixed test-first without a third round (DEC-413).
- **Learning metrics:** 0 KPI disputes; 0 acceptance tests rewritten after implementation began; 9 cases added
  after it (4 fail-open cases, 5 unit cases); source 349 lines against an estimate of 120.
- **Interface:** `gov.retrieval.validate.validate(root, bundle)` returns `valid` and `errors`;
  `gov.retrieval.canary.run_canaries(root)` returns, per index, `passed`, `status`, `misses` and, where it
  applies, `reason`.
- **Regression at `85e9b580`:** every suite green; W1-46 showed 23 errors in its live-session cases beside the
  other suites and 493 passed alone (DEC-372).

## W1-24 residuals (gov context, 2026-10-06)

- **The first round's work was discarded** (DEC-427): its engineer was not a launched worker and its lead wrote
  source. The branch was rebuilt from the test design; one rewrite round.
- **The cross-process hash case exercises the path without an index only;** the ordering of the supplementary
  block across processes is not tested (reviewer F-3).
- **A missing record file gives a default content or hash silently** inside the packet builder (F-4); the store
  has verified the records before, so it is not reachable in a loaded store.
- **The supplementary query is the first long word of the ticket's title** (F-5, DEC-437 DP-3).
- **`gov context` exits 1 for BLOCKED and CONTRADICTION** (DEC-437 DP-2); an entry dropped because an index is
  unavailable carries that reason; `--dry-run` computes without writing the brief file.
- **`S0a-G-07`** is not in the tree. Its text, read by the orchestrator by exact path (DEC-432), has six parts
  (authority block first, supplementary block, token ceiling, sha256, file-path delivery, a summary of at most
  2,500 tokens); each is covered by a KPI-derived case; no case was derived from the text itself.
- **The context-reproducibility check is red on a tree with no loaded store** ("cannot read the store"), and
  unmeasured, never green, where no ticket can be measured (fixed test-first after the review, DEC-437).
- **The engineer's commit `d454ee7a` and the branch's first merge of the integration branch (`ee69d2ef`) carry
  no `Role:` trailer.** They change no acceptance test. Records.
- **Review rounds:** one. **Learning metrics:** 0 KPI disputes; 1 acceptance case revised after implementation
  began ("planned: command implemented"); 3 cases added after it (the fail-open fix); source 387 lines against
  an estimate of 350.
- **Interface:** `gov.context.context(root, ticket, *, brief=False, budget=None, dry_run=False)`; packet keys
  `ticket, authority, mandatory, supplementary, dropped, hash, tokens, budget`;
  `gov context [--json] [--brief] [--dry-run] [--budget N] <ticket>`.
- **Regression at `c01e6058`:** every suite green, no latency occurrence.

## W1-26 residuals (gov check G0-G2, 2026-10-06)

- **`gov check` on this repository exits 3.** Red from real findings: schema/invariants (legacy records without
  `state_class`), graph integrity (dangling `depends_on` references). Red because nothing is measured or built
  here: index freshness (no lexical index in this tree), retrieval regression (unmeasured, no dev tiers
  configured), context reproducibility (no loaded store), and the policy keys change, human_gate, security, test
  and tool (no check registered for them yet). Yellow with "no registered check" (DEC-438): adapter/model
  portability, recovery/rebuild (W1-27), audit reproducibility.
- **The fresh-agent-reconstruction check is red here because `gov` is not on the `PATH` of the check's shell**
  (exit 127). Its declaration is W1-25's.
- **The result lists 24 families:** the Contract's seventeen and the seven policy keys, each as its own entry.
- **The schema check validates the presence of fields,** not their types, enumerations or patterns (reviewer R1).
- **A check's command that exits 0 is green whatever it prints** (DEC-285); a non-JSON output is not a finding.
- **A hard-block check whose tool is absent (`openspec`) is YELLOW, not RED** (reviewer F10).
- **Check commands are run through a shell from their YAML declaration,** with the caller's write access to the
  working directory, and are not validated (F11, F12).
- **Policy coverage matches a key to a check by substring** (F13); the skill-version check accepts any `ACTIVE`
  decision (F14).
- **The provenance `inputs_hash` is the hash of the check's id and the commit,** not of the input files.
- **Four lists remain constants in the code** because the Contract fixes them (the families, the reserved
  commands, the non-authoritative types, the implementer roles); record paths and schema types are derived, and
  an unknown record type is a finding (DEC-436).
- **`wbs_to_id` in `claims.py` is built and never used.**
- **History:** the second round's merge of the integration branch was made without committing in the same
  command and lost other tickets' tests; it was never merged, and the branch was rebuilt (DEC-436). The rebuilt
  branch's merge `b7e75958` was flagged once by the containment check for the shared W1-07 support file,
  byte-identical to the branch's aligned version: a record.
- **Review rounds:** two (the limit). After them, fixed test-first without a further review: an unknown family
  never green, derived record paths, the readiness result (DEC-436); a family with no registered check never
  green (DEC-438, found by the orchestrator's own run).
- **Learning metrics:** 0 KPI disputes; 4 acceptance cases revised after implementation began (2 for DEC-425
  "unmeasured is never green", 2 that named uncovered families by a fixed list); 27 cases added after it;
  source 1,245 lines against an estimate of 290. Every module maps to a KPI line; the estimate was wrong, not
  the scope.
- **Interface:** `gov check [--json] [--list]`; exit 0 all green, 3 `CHECK_FAILED` on any hard-block red;
  `gov.check.runner.run_checks(root)` returns the result and whether a hard-block is red; each family entry has
  `status`, `check_count` and, where it applies, `reason`; each check has `id`, `family`, `severity`, `status`,
  `findings`, `provenance`. Family names are compared normalised (DEC-436).
- **Regression at `6d1848cd`:** every suite green, no latency occurrence.

## W1-23 residuals (hierarchical synthesis notes, 2026-10-06)

- **A note is deterministic and written by no model:** grouped citations with source ids, the hash of each cited
  span and of its file, the path and the lines, and the list of unresolved evidence. A model-written summary is
  not built and no source asked for one.
- **Notes are stored in one file,** `.gov-runtime/synthesis/notes.json`, per project; a second synthesis replaces
  the first.
- **Invalidation is found when `validate_notes(root)` is called,** by hashing the cited files and spans again;
  nothing calls it yet. `gov context` (W1-24) does not import this module; the wave's exit run (W1-42) is the
  first place where notes are derived for evidence above the packet budget.
- **No review round** (STANDARD); the lead read the diff against the two failure lines.
- **Learning metrics:** 0 KPI disputes; 0 acceptance tests rewritten after implementation began; source 114
  lines against an estimate of 100.
- **Interface:** `gov.retrieval.synthesis.synthesize(root, evidence, budget, *, gaps=None)` returns `notes`
  (each with `group` and `citations`) and `unresolved`; `gov.retrieval.synthesis.validate_notes(root)` returns
  `valid` and `errors`.
- **Regression at `c8080e16`:** every suite green, no latency occurrence.

## W1-50 closing follow-up residuals (the freeze mirror and the ticket lead's role, 2026-10-06)

- **The mirror** is the file `freeze` in a folder under `~/.local/state/gov-os/` named by the SHA-256, in hex, of
  the real path of the repository's git common directory (DEC-437). The main tree and every worktree share one
  entry. A moved repository has a new key: its old mirror no longer freezes it, and the in-repository flag
  alone does.
- **The mirror's place follows the home directory the process sees.** A session that starts a child with
  another home makes that child's guard read another mirror. The orchestrator's own unsandboxed session can do
  that; it is inside the residual the owner accepted (DEC-429: an opaque write by that session).
- **A launched worker's sandbox gives it a redirected home,** so it cannot reach the real mirror; its guard
  therefore reads the in-repository flag only. A worker cannot write under `.gov-runtime/` outside its scratch,
  and the containment check around the caller's Bash calls restores a removed flag from the mirror.
- **An empty or unmarked mirror file means frozen;** a lift that cannot remove the mirror refuses and changes
  nothing (DEC-437; the owner may overturn).
- **The role `ticket-lead` exists in the guard** with no allowed paths; it writes its scratch through the
  existing scratch rule. It is not a worker role: `gov launch` does not start it. **No lead runs under it yet:**
  the lead start line in the orchestrator prompt is the owner's to change (`"GOV_ROLE":"ticket-lead"` in place
  of `"GOV_ROLE":"orchestrator"` in the `--settings` of appendix A5). Until then leads keep the orchestrator's
  write rights (DEC-156), and the four rules at the top of the leads' common brief are the only bar.
- **Tests and the real mirror.** In the second start, unit tests wrote six entries into the real
  `~/.local/state/gov-os/` (keys of temporary projects, none of this repository; nothing was frozen). They are
  the owner's to remove. Since then every test that runs the pause command or the guard uses a throwaway home,
  and a tripwire fails the test session if the real folder's listing or modification time changes
  (`tests/acceptance/conftest.py` and the conftest files of `tests/unit/pause`, `guard` and `containment`); it
  finds the real folder from the password database, so a changed `HOME` does not blind it. A new suite that
  runs `gov pause` without a throwaway home is caught by it, not prevented.
- **Cases of other tickets revised for the mirror** (reason "owner decision DEC-429"): W1-07's read-act
  snapshot cases and W1-28's freeze cases; one W1-50 freeze-marker case.
- **The engineer's commit `9f294a9e` carries no `Role:` trailer;** the second start's lead wrote a unit test
  itself, which was removed from the branch and redone by an engineer. The merge `94bb68d7` was flagged once by
  the containment check for the aligned W1-07 support file: a record.
- **The owner's manual check of freeze, pause and lift from a plain terminal** is run at the wave's exit
  (W1-42, DEC-428), now including: after `gov pause`, both the flag and the mirror exist; removing the flag by
  hand leaves the project frozen and the next Bash call of a session restores it with a finding; the lift
  removes both.
- **Learning metrics of the follow-up:** 6 packages (all decided by the orchestrator, DEC-437); 0 KPI disputes;
  5 cases of earlier suites revised after implementation began, each for the mirror; source 159 lines against
  an estimate of 150; three starts (one ended on a running reviewer, one for the packages).
- **Regression at `5d830d3e`:** every suite green (W1-50 642 passed), no latency occurrence; the real mirror
  folder unchanged by it.

## W1-29 residuals (session hooks, 2026-10-07)

- **Built:** SessionStart and PreCompact add W1-29's behaviour to W1-49's hooks (W1-49's suite unchanged and
  green); Stop and SubagentStop are new. SessionStart injects the `gov context --brief` text and the ready
  tickets for a session with a ticket, within the 10,000-character cap, optional parts cut first. PreCompact
  and Stop write a checkpoint record when the session has a ticket; a session with none writes nothing.
  SubagentStop refuses, once, a return that lacks any of the twelve fields or holds an empty one, in JSON or
  in text.
- **Stop and SubagentStop are not registered.** They run only once the owner adds them to the project's
  settings file (the lines are in the lead's return, `W1-29-lead-run3.json`, and were given to the owner).
  The installer may need the same lines for an installed project: for the adoption ticket.
- **KPI line 3 is not met in its literal reading.** "A checkpoint is written when the session's context
  utilisation passes the configured threshold": no hook receives the utilisation. What exists: a checkpoint at
  every stop (once Stop is registered) and at every compaction, and W1-25's watchdog marks a checkpoint stale
  on utilisation when a caller gives it the figure. For the owner.
- **The auto-compact threshold (DEC-208) is not set.** The Claude Code command line has `--autocompact` (seen
  in its help text by the orchestrator); the lead names a settings key `autocompact` with the value 300000,
  which nobody verified. The settings file is the owner's. Until it is set, the KPI's second half holds: the
  orchestrator's CONTEXT_CHECKPOINT stop stays.
- **Checkpoint records written by the hooks are untracked files** under `docs/checkpoints/(ticket)/`. No code
  commits them. A hook is a process of its own, not a tool call: its write is not decided by the guard, so a
  worker whose role may not write `docs/**` still gets these files written in its tree. What becomes of them
  (commit, ignore, clean at close) is open; `gov close` (W1-30) writes its closing checkpoint the same way.
- **"Preserves the open decisions and the loop counts" holds for the orchestrator only,** through W1-49's
  checkpoint file and its RESUME HERE section; a worker's checkpoint record holds its ticket and a next action.
  A session inside a loop never sees a count (DEC-096).
- **`src/gov/hooks/stop.py` and `subagentstop.py` are copies** of the two files under
  `template/governance/kernel/hooks/`; a case pins that they are identical.
- **A case's rewrite is labelled "owner correction"** (`test_auto_compact_threshold`): it was the
  orchestrator's finding that the case could not fail, not an owner's correction. The label stays in the test
  text (the orchestrator does not edit tests); this line corrects the record.
- **Records:** the merge commit `478a8ed0` on the branch carries no `Role:` trailer. Source S0a-G-09 was
  passed to the third start by the orchestrator (DEC-432).
- **Learning metrics:** three starts (the first replaced W1-49's hooks and returned DONE with 65 of W1-49's
  cases red; the second was accepted except six points found by reading each KPI clause against the case
  table); 33 cases; 1 case rewritten after implementation, 5 added after it; about 210 lines of source against
  an estimate of 180, plus 104 lines of copies; two reviews.
- **Regression at `ee5eaf40`:** every suite green. One W1-16 case
  (`test_this_repository_is_not_indexed_by_the_run`) failed in the full run because a tool call of the
  orchestrator's own session wrote a containment snapshot under `.gov-runtime/` while the case watched that
  folder; it passed alone. The real freeze-mirror folder was unchanged by the run.

## W1-26 follow-up residuals (the generic validators and "not applicable until the first audit", 2026-10-07)

- **Why the ticket was reopened:** W1-35's and W1-36's check declarations ran `true` as their command, because
  the validators their KPIs name ("the generic validator from W1-26") did not exist. The orchestrator had
  closed W1-26 without them: its own error, corrected by DEC-439.
- **Built:** `python3 -m gov.check.skill_validator (folders or files)` finds every `SKILL.md` at any depth and
  checks the frontmatter, the version, the description and body sizes (with W1-24's token count) and that
  every `gov` command the file names exists. `python3 -m gov.check.audit_validator (files or folders)` checks a
  report against DEC-441's form: the frontmatter `milestone`, `commit` (a full commit id that exists),
  `pack_sha256`; the table `item | class | evidence`; the six classes of DEC-070; an `OK` row cites at least
  one path, and every cited path exists at the cited commit. Both: any finding exits 1; nothing validated or
  an unreadable file is "unmeasured" and exits 1 (DEC-425).
- **"Not applicable until the first audit" (DEC-447):** a declaration that carries
  `allows-not-applicable: "true"`, whose command exits 2 and prints `{"not_applicable": true, "reason": …}`,
  is YELLOW with that reason. All three are needed; without the field, exit 2 is an ordinary failure. The
  audit validator answers so only when a folder it was given is missing or holds no report; with one report it
  is a hard block again.
- **The opt-in field is read only from a declaration file named `(check id).yaml`.** A declaration whose file
  name differs from its id cannot opt in (it stays red: the safe side).
- **The audit validator does not check the value of `milestone`** (any text passes), nor that `pack_sha256` is
  the hash of an existing pack beyond its form. For the exit audit (W1-43) to read by hand.
- **The skill validator checks `gov` commands against the reserved-command list,** not against what is
  installed on the machine.
- **Declared commands name paths under `template/…`,** which an installed project does not have: for the
  adoption tickets (W1-39, W1-41).
- **Learning metrics:** two lead starts (the first built the skill validator only, with a folder search one
  level deep that found nothing with the given command line), then two designer-and-engineer pairs started by
  the orchestrator (four gaps in the audit validator found by reading DEC-441 against the code; DEC-447); 0
  reviewer rounds (the ticket's two were spent); 450 lines in the two validators plus about 50 in the runner,
  against an estimate of 120; 238 cases in W1-26's suite.
- **Regression at `54b8a404`** (machine load 48): green except the load-sensitive cases of DEC-372 (W1-02,
  W1-05, W1-46), which passed alone, save one W1-05 case in one alone run that was not identified.
  **Regression at `b706e688`:** every suite green, no latency occurrence (W1-05: 99 passed).

**Correction to "W1-29 residuals" above (DEC-451):** the line "The auto-compact threshold (DEC-208) is not set"
is wrong. The project's settings set the environment variable `CLAUDE_CODE_AUTO_COMPACT_WINDOW` to `300000`
since W1-49's merge; the Claude Code documentation names that variable as the setting, and there is no
settings key `autocompact`. The orchestrator's CONTEXT_CHECKPOINT stop is dropped. The other owner items of
that block are answered by DEC-442 (Stop and SubagentStop are registered at the Wave 1 exit run), DEC-444
(the hooks' automatic checkpoints go to `.gov-runtime/scratch/checkpoints/`: W1-29 follow-up) and DEC-445 (the
utilisation-triggered checkpoint is an accepted residual).

## W1-35 residuals (the four method skills: discovery, planning, test design, change, 2026-10-07)

- **Built:** four skill files under `template/governance/kernel/skills/` (discovery, planning, test-design,
  change), each with a versioned frontmatter, within the size limits, citing the decision or capability it
  follows and granting nothing; and the check declaration `skill-regression-a`, which runs W1-26's generic
  skill validator over the four folders.
- **The suite tests the text of the skills, not sessions that follow them.** These KPI clauses are measured
  only by a live session and go to the Wave 1 exit run (W1-42): "0 of the decision packages discovery asks
  are answerable from files its retrieval bundle cites" on the MR-A-02 and MR-B-02 dev scenarios; "its
  transcript reads no file outside them" for test design; "planning emits schema-valid tickets and one linked
  gap ticket per required open readiness row"; the change skill's refusal to archive a kernel change that
  lacks a record; the impact assessment run from a plain-language question. Until then they are unmeasured,
  not met.
- **The declaration's command names paths under `template/…`,** which an installed project does not have (its
  skills are under `governance/kernel/…`). True of every declared check today: for the adoption tickets
  (W1-39, W1-41).
- **The first return declared the check with the command `true`,** because the validator did not exist yet
  (DEC-439 reopened W1-26 for it). The second return runs the real validator.
- **W1-26's fixture was revised for this ticket:** a project built by W1-26's suite now holds the kernel's
  skill folders, copied generically, since a check that finds no skill is unmeasured and red (DEC-425). No
  assertion was changed.
- **This suite and W1-36's cannot be collected in one pytest run:** both import their fixtures from a module
  named `conftest` by its bare name, and the second import finds the first. Each passes alone, which is how the
  regression runs them. For the exit run.
- **Records:** the merge-back `84bf8d12` was made with git's `ours` preference after the plain merge
  conflicted on W1-26's README (the branch's file had been aligned to the integration branch's version plus
  its own lines); the containment check flagged that merge for its own change to that README, and an earlier
  merge `91568f75` for the shared W1-07 support file. Both are byte-level outcomes of aligned files.
- **Learning metrics:** two lead starts, plus two short test-designer turns started by the orchestrator (the
  fixture, the alignment); 112 cases; no reviewer round (STANDARD, self-review); about 200 lines of skill text
  and a 5-line declaration.
- **Regression at `ab1fa23c`:** every suite green, no latency occurrence.

## W1-36 residuals (the skills retrieval, audit, checkpoint and adopt, and their checks, 2026-10-07)

- **Built:** four skill files under `template/governance/kernel/skills/` (retrieval, audit, checkpoint, adopt),
  versioned and within the size limits; the declaration `skill-regression-b1` (W1-26's skill validator over
  the four folders); the declaration `audit-reproducibility` (W1-26's audit validator over `docs/audit/`,
  tier G1, hard block). The audit skill (v1.1.0) describes the report form of DEC-441.
- **"Not applicable until the first audit" (DEC-447):** the audit declaration carries
  `allows-not-applicable: "true"`. With no report under `docs/audit/` the family is YELLOW with that reason;
  with a valid report GREEN; with an invalid one RED, a hard block.
- **The suite tests the text of the skills and the checks on constructed reports, not sessions.** Measured only
  at the Wave 1 exit (W1-42, W1-43): retrieval runs its facets in disposable subagents and only the validated
  bundle returns ("intermediate retrieval batches appear in the main context" is a failure line); the audit
  reports the planted divergence on the MR-A-06 and MR-B-06 dev scenarios; the audit starts a fresh session
  whose only inputs are the context pack and the repository, and edits no audited file; contested and
  owner-level findings appear as decision packages; a wave-exit report has one row per LITE feature
  specification closed in the wave. Until then they are unmeasured, not met.
- **The vendored superpowers skills carry no `version`,** so the skill-regression declaration names the four
  folders instead of the whole skills folder, and those three skills are not validated. Open: add a version to
  the vendored copies (they are committed unchanged, DEC-194) or leave them outside the check.
- **Declared commands name paths under `template/…`,** which an installed project does not have: for the
  adoption tickets (W1-39, W1-41).
- **W1-26's suite was revised for this ticket:** five cases remove the kernel's own audit declaration from
  their temporary project, because a second check of the same family (over another folder) made their family
  status ambiguous; the fixture's skill copy was aligned to the integration branch's. No assertion was changed.
- **Records:** the merge-back `15ac9b54` was flagged by the containment check for the shared W1-26 support
  file (aligned to the integration branch's version before the merge, DEC-412).
- **Learning metrics:** two lead starts (the first declared its checks with commands that exited 0 whatever
  they found), then four short worker turns started by the orchestrator (alignment, DEC-447 cases, the field,
  the W1-26 life-cycle case); 84 cases; no reviewer round (STANDARD); about 165 lines of skill text and two
  declarations.
- **Regression at `087a166a`:** every suite green, no latency occurrence.

## W1-50 follow-up residuals (a public judgement of commits, DEC-453, 2026-10-07)

- **Built:** `gov.guard.containment.judge_commits(root, commit_ids)` returns one finding (commit, paths,
  reason) per commit that the post-command check would flag in an orchestrator's own call; it calls the same
  per-commit judgement and the same reading of commits and merges (the parsing loop was split out so both use
  it; the 642 earlier cases are unchanged and green). It only reads. An empty list, an unknown id, a path that
  is not a repository and a git failure raise `ContainmentError`.
- **For `gov close` (W1-30):** it is called with the ticket's commits; any finding refuses the close. W1-30's
  private rule set is removed in that ticket.
- **It judges as the orchestrator's own call does** (each commit by its own `Role` and `Task` trailers); it has
  no caller's role or ticket to judge against. A commit naming a closed ticket is judged against that
  ticket's close commit, as in the check.
- **Learning metrics:** one designer turn and one engineer turn started by the orchestrator; 24 cases added;
  107 lines added and 19 removed in the module, 237 lines of unit tests.
- **Regression at `3d715a35`:** every suite green except W1-46's 23 live-session cases, which errored while
  three other test runs were going (DEC-372); W1-46 alone: 493 passed.

## W1-29 and W1-25 follow-up residuals (automatic checkpoints in the ignored scratch folder, DEC-444, 2026-10-07)

- **Built:** PreCompact and Stop write their checkpoint record under
  `.gov-runtime/scratch/checkpoints/(ticket)/`; a deliberate `gov checkpoint` still writes under
  `docs/checkpoints/(ticket)/`. `gov.checkpoint.record.write` takes `dest="automatic"` or `"deliberate"` (the
  default). Record numbers are unique per ticket across both places. `brief`, `briefs` and `watch` read the
  newer of the two by creation time (on a tie the deliberate one) and return its path. W1-25 was reopened for
  its module's part.
- **An automatic record carries `head_commit`,** the HEAD when it was written, and the watchdog counts commits
  from it (an ignored file is never committed, so the earlier count from "the commit that added the record"
  would always be zero). A record in the scratch folder **without** that field counts zero commits: the
  product's writer always sets it, so only a hand-placed record can lack it.
- **Automatic records written before this change stay under `docs/checkpoints/`** in the trees where hooks ran
  (untracked); nothing moves them. In this repository and its worktrees they are the orchestrator's to remove.
- **An installed project must ignore `.gov-runtime/`** for the tree to stay clean after a hook: for the
  adoption tickets (W1-39, W1-41).
- **Records:** the designer's commit `3f09f660` names "Claude Opus 4.6" as co-author.
- **Learning metrics:** one designer turn and two engineer turns started by the orchestrator; 12 cases added
  and 6 revised (owner decision); about 95 lines of source.
- **Regression at `b89ba5ce`:** every suite green except one W1-16 case (`test_this_repository_is_not_indexed_by_the_run`), which saw a snapshot file the guard wrote for the orchestrator's own command during the run; W1-16 alone afterwards: 166 passed.

## W1-27 residuals (gov doctor and gov rebuild, 2026-10-07)

- **Built:** `gov doctor [--json]`, a read command with eleven sections (tools, hooks, path map, path
  compliance, index freshness, canaries, framework lock, isolation, Claude Code, held-out file, adoption
  level); exit 3 when unhealthy. `gov rebuild` recreates the derived stores through the code that owns each
  (the record store, the lexical index with its secrets filter, the semantic index and the code index when
  their tool answers) and names each outcome; it returns `digest`, `store` and `stores`. The check
  `gov.rebuild.check` is the recovery/rebuild family check. `gov` validates the path map against W1-08's
  schema; W1-07's provisional cases were revised in this ticket's test design (DEC-228).
- **Rules decided on the way (DEC-440, DEC-448, DEC-452):** an error in a measurement is a failure and an
  absent component is "unmeasured", never the top adoption level; doctor looks for a tool under its own
  registry entry's PATH prefix, then under every prefix the registry carries, then on PATH; a tool passes only
  by a version read and equal to the pin or, where no version can be read, by a hash computed and equal to the
  pin; historical records (the register, CIT records, this file, archived sources) are left out of the
  stale-path check, and the section says how many files it left out.
- **KPI line 6 against DEC-210:** the extension newer than the CLI, both above the minimum, is reported as
  drift and makes doctor exit 3. The owner called this drift harmless (DEC-448); it is re-recorded at the
  Wave 1 exit.
- **Doctor knows six registry entries by name** (`pyyaml`, `superpowers`, `sqlite-vec`, `qwen3-embedding`,
  `reranker-venv`, `reranker`): where each is and what its registered hash is the hash of is written in the
  code, not in the registry. A generic kernel command that knows this repository's tools: the registry needs
  a field for "what the hash is of and where", for the adoption tickets. It computes the vendored folder's
  digest with its own function.
- **A registry entry's PATH prefix is read out of its install command** (`PATH=…:$PATH`); the registry has no
  field for a tool's location. Node's own entry carries none and is found through the prefix of other
  entries.
- **`reranker-venv` passes by the versions in its package metadata,** not by its registered hash (the hash is
  of a package listing made with a tool; `sha256_match` is false for it). The local version suffix of torch
  (`+cu130`) is not compared. `pyyaml`, `ccusage`, `bubblewrap` and `socat` pass by version only: their
  registered hashes are of packages that are not on the machine.
- **Doctor takes about 7.5 s here:** it hashes the embedding model (610 MB) and the reranker model (1.14 GB)
  on every run.
- **Rebuild takes about 157 s on a project of about 955 tracked files** (the secrets filter runs on every
  file), 2.5 s on three files. The suite's rebuild cases run on a small project, and five of W1-07's cases
  that ran every command on a copy of this tree were revised to run rebuild on a two-file project.
- **Rebuild without a path map returns its envelope** with the lexical index named as not recreated and the
  reason; an owner of a store that raises gives the error `REBUILD_FAILED` with the store and the text. An
  optional index (semantic, code) whose tool errors is named `not_recreated` with the reason and exit 0.
- **The recovery check with no store exits 1** ("unmeasured"), so the recovery/rebuild family is not green in
  a project that was never loaded.
- **Earlier defects found by reading the code against the KPI clauses, each fixed test-first:** rebuild wrote
  the lexical index itself, past the secrets filter, and into another module's tables; a false reason "no code
  index module exists"; a tools case that asserted a key name; `socat` passing with no version read and no
  hash match; six entries reported as "hash matched" because a folder existed; three "healthy project" cases
  that depended on this machine's home; rebuild ending in a traceback on a project with no path map; three
  cases that imported the package into the test process and passed only where PYTHONPATH was set.
- **Records:** commit `2e6ec15b` (engineer) names "Claude Opus 4.6" as co-author. Temporary folders
  `/tmp/gov-launch-engineer-en6s9b8e` and `/tmp/gov-launch-engineer-4mcz3fb1` were left by launches. The
  containment check flagged `94bc7635` (a merge-back's own change to W1-07's support file).
- **Learning metrics:** three lead starts, then five designer-and-engineer rounds started by the orchestrator
  (rounds 4 to 10); two review rounds (the limit); 117 cases, of which about 30 were revised after
  implementation began and about 50 added after it; 943 lines of source against an estimate of 230. Every
  section of doctor maps to a KPI clause; the estimate was wrong, not the scope.
- **Regression at `8388138c`:** every suite green except two W1-28 cases: W1-28's check of fixtures that copy from the repository found the new helper of W1-07's suite and could not exercise it. The designer rebuilt the helper without a copy (merge `53fd4293`); W1-28 (149 passed) and W1-07 (219 passed) were then run alone on that state; the full regression was not repeated for this one test-support file.

## The one rebuild of this repository's stores (DEC-448, 2026-10-07)

- **Run once at `5d2390e4`,** after W1-27's merge: `gov rebuild` exit 0 in about 8 minutes; the record store,
  the lexical index, the semantic index and the code index were recreated. The record store names three files
  as invalid (no `type` key): `docs/charter/CHARTER_v5.md`, `docs/contract/CONTRACT_v4.md`,
  `docs/plan/WAVE_1_WBS.md`.
- **`gov doctor` before and after:** index freshness went from unmeasured (no index) to pass, the canaries from
  unmeasured to pass on both indexes. Doctor still exits 3, for two reasons: the Claude Code drift (extension
  2.1.289 above the pinned CLI 2.1.288; harmless by DEC-448, re-recorded at the exit) and path compliance.
  Unmeasured: hooks (no hook-manager configuration, no binary) and the framework lock (none exists).
- **Path compliance reports 180 stale paths and none of them is in a live document to correct by hand:** 156
  are in `docs/SOURCES.md`, which is the table of moves itself (new path, old path, hash); 23 are in the old
  `cli/` tree (its configuration, fixtures and two source files, carried unchanged from the v4 line); one is
  the original Framework's file name in `docs/plan/tools/validate_s1.py`. Doctor counts no file as left out
  as historical on this repository (`historical_excluded: 0`), though the register and this file are full of
  old paths: either the exclusion is not counted or the old paths in those files are not in the move table.
  No ticket holds this: the plan validator admits exactly the fifty Wave 1 tickets, so a cleanup ticket
  (opened as `DAEO-0f1y`, removed in the next commit) cannot be added without the owner. It is a named item
  for the exit: the table of moves is a historical record for the check; whether `cli/` is
  live is the owner's to say.
- Adoption level reported for this repository: INTERMEDIATE, 15 of 22 systems identified.

## `gov check` on this repository: the baseline of red checks (DEC-466, DEC-467, 2026-10-07)

Run at `46ec8da3`: exit 3. Thirteen hard-block checks are red, for reasons that lie in this repository's state
before its adoption (W1-39, W1-41), not in a ticket branch. A merge is blocked by any red outside this list
(DEC-467).

| Check | Reason at the baseline |
|---|---|
| `context-reproducibility` | unmeasured: no tickets in the record store |
| `core-graph` | the tickets' `depends_on` name W1 ids, which are not record ids |
| `core-schema` | records without `state_class` (for instance `docs/adr/ADR-0001-threat-model.md`) |
| `fresh-agent-reconstruction` | its command calls `gov`, which is not on PATH here (exit 127) |
| `index-freshness` | the lexical index is stale after every commit since the one rebuild (DEC-448) |
| `recovery-rebuild` | the store's digest differs from a rebuild's, for the same reason |
| `retrieval-regression` | unmeasured: the dev tiers are not configured |
| `secrets-indexing` | its command exceeds 60 seconds on this tree |
| `policy-security`, `policy-test`, `policy-change`, `policy-human_gate`, `policy-tool` | the policy key has no associated check |

Yellow at the baseline: `audit-reproducibility` (not applicable until the first audit), `core-commands`,
`openspec-validate`, `policy-memory`, `policy-checkpoint`, and the families adapter/model portability (no
registered check until W1-38) and product traceability. Green: `core-authority`, `core-claims`,
`core-mutation`, `core-pathmap`, `skill-regression-a`, `skill-regression-b1`, `skill-version`, `readiness`.
