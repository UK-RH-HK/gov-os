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
- **The `systems` snapshot** (13 minimal, 9 absent, none implemented) needs updating as tickets land, W1-46 first
  (research).
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
