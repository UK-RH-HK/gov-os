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

## W1-27 follow-up: historical paths in doctor's stale-path check (DEC-456, 2026-10-07)

Merged at `6db36969` (cases `f4ec043c`, code `da877e8a`; sessions on Claude Opus 5.5). `docs/SOURCES.md` and
the old `cli/` tree are historical for the stale-path check; the plan validator's one stale path was fixed in
`4eb9aacd`.

- `gov check` on the branch before the merge (DEC-466, DEC-467; `log/check-at-W1-27b-premerge.json`): no red
  outside the baseline. `secrets-indexing` was not red in that worktree run; it stays in the baseline until
  it is seen green in the main tree.
- Full regression at `6db36969` (`log/reg/at-W1-27b-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- `gov doctor` at `6db36969` (`log/doctor-at-6db36969.json`), exit 3: the stale-path check passes (0 moved
  references, 179 historical excluded). Two parts are still not green: the Claude Code drift (re-recorded at
  the Wave 1 exit, DEC-448), and index freshness (9 stale files): every commit since the one rebuild makes
  the lexical index stale, and no second rebuild is run here (DEC-448). Hooks, canaries and the framework
  lock are reported unmeasured. For the owner at the exit: whether the index is rebuilt once more at
  adoption (W1-41).
- W1-41's adoption review decides whether the old `cli/` tree is archived (DEC-456).

## W1-26 follow-up: the decision-citations check (DEC-463, DEC-473, DEC-474, DEC-475, DEC-479; 2026-10-07)

Merged at `8f0dcc8d` (cases `e3d2cc1b`, `ac952490`; code `c2058c80`, `f2361f1d`; all sessions pinned to
Claude Opus 5.5). `core-decision-citations` (family authority/role limits, tier G1, severity warning) flags a
commit whose message cites a decision id that its own tree does not record, as a decision file or as an
entry of the register file the project names. This repository names `docs/DECISION_REGISTER.md` and the base
commit `46ec8da3` in `governance/project/path-map.yaml`; the check is green here.

- `gov check` on the branch before the merge (`log/check-at-W1-26e-premerge.json`): no red outside the
  baseline; twelve baseline reds; `secrets-indexing` green in the worktree run (third time; it stays in the
  baseline until seen green in the main tree).
- Full regression at `8f0dcc8d` (`log/reg/at-W1-26e-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- Closed with `tk close` (W1-30 is not merged yet, DEC-476).
- The first engineer session of the second part ended before committing (it started its runs in the
  background); a second session ran them in the foreground and committed. No acceptance case was changed
  after implementation began.
- Where the check can still say clean without having measured (for the Wave 2 list, DEC-466): commits after
  the base that cite nothing give the same answer as none compared; whoever moves the base forward takes
  earlier commits out of judgement, unreported; any Markdown file in the tree whose frontmatter carries a
  decision id counts as its record, wherever it lies; a register heading counts whatever the entry's status
  or body says (a heading inside an HTML comment too); only HEAD's history is judged.
- The check imports private helpers of W1-11's decision checker (`_front`, `_git`, `_Objects`, `_once`):
  a change there can break it; the unit tests cover the join.

## W1-30: `gov close` (DEC-453, DEC-454, DEC-470, DEC-476, DEC-480, DEC-482, DEC-483, DEC-484; 2026-10-07)

Merged at `2c71bc64`. Cases by the test designer in seven rounds (last `be2e8c14`, 204 cases); code by the
engineer (last `a1c03c5b`; `src/gov/close/command.py` 833 lines against an estimate of 200). `gov close`
measures or refuses: containment as W1-50 judges it, one context, the ticket's and every earlier suite, the
reviewer's writes, the governance checks as W1-26's runner reports them, the owner's decision on escalation;
every finding goes through one failure path (counted, a repair ticket, escalation at the third, exit code 3).

- `gov check` on the branch before the merge (`log/check-at-W1-30-premerge.json`): the ticket's own check
  `product-traceability-trailers` is red with 735 findings and joins the baseline with that state (DEC-482);
  the twelve earlier baseline reds; `secrets-indexing` green in the worktree run.
- Full regression at `2c71bc64` (`log/reg/at-W1-30-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- Own runs at the branch head (`log/W1-30-r7-own.txt`): W1-30 204, W1-07 218, W1-11 142, W1-24 54, W1-25 52,
  W1-26 294 and 1 skipped (the full project does not pass `gov check` yet), W1-50 666, W1-28 149, unit 1171.
- **`product-traceability-trailers` here:** 408 findings are commits of closed tickets without `Implements:`,
  made before DEC-476; a trailers base commit (here `429815b5`) takes them out of judgement once the setting
  is built (DEC-482; W1-41 or a follow-up). 327 are ids that resolve to no record: the check knows the record
  store, ticket ids and `docs/**` Markdown frontmatter ids, and this repository's capability ids live in
  `docs/contract/contract.yaml` until W1-41's adoption. The check's module keeps one `except Exception` around
  the store read (it reports an error, not a pass) and was not read again after round 4.
- **`core-decision-citations` is yellow from this merge on (10 findings, a warning):** branch commits cite
  DEC-453, DEC-454, DEC-470, DEC-476 and DEC-480, recorded on `w1/integrate` before the changes but not yet
  merged into the branch when the commits were made. History is not rewritten. From now the orchestrator
  merges `w1/integrate` into a ticket branch before a worker turn that will cite a newly recorded decision.
- **The owner's decision on an escalation is read from decision files only**, not from a register file such
  as this repository's: for W1-41's adoption (DEC-483).
- Where `gov close` can still close or refuse on something it did not measure, or says less than it could
  (for the Wave 2 list, DEC-466):
  - a tree with uncommitted changes is measured as its HEAD;
  - an error of the check runner ends the close uncounted (exit code 1), without a repair ticket;
  - "governance-changing" is seven fixed path prefixes;
  - no acceptance case holds a check that runs over the runner's fixed 60-second limit (a case would wait a
    minute); the limit is not configurable;
  - `openspec-validate` is yellow where the tool is absent, and yellow refuses nothing (W1-26's question);
  - a finding raised with `--disposition` records no class and no context on its repair ticket;
  - the repair ticket's `state_class`, `disposition` and `context_hash` are inserted into the ticket tool's
    frontmatter by the close command itself;
  - the model of a session is read from the commits' co-author lines (DEC-470); a launch record per session
    is a Wave 2 item.
- **Run time here:** `gov close` runs the project's tests, about an hour per ticket on this repository
  (accepted, DEC-484).
- History of the branch, for the exit auditor: commit `7674efde` carries no `Role:` trailer (S0a-G-12);
  the lead's rounds 1 to 3 and engineer round 4 (`01c19515`, a session that ran unpinned on Claude Opus 4.6
  before DEC-460 was applied to it) were read and not accepted; the engineer's round-5 session ended without
  a report (its runs were in the background) and its commits were read from the tree; merge commits
  `148f7584` and `29af0646` are flagged by containment for their own change to
  `tests/acceptance/W1-07/w1_07_support.py` (the shared list, DEC-412), left in place.
- Learning metrics: KPI disputes raised by the designer: three (round 6, settled by DEC-480) and the
  baseline question (DEC-476); acceptance cases rewritten after implementation began: the round-4 to round-7
  batches, each for a behaviour the earlier code claimed without measuring, plus one reversed case (a
  warning check whose command is absent, DEC-480) and one W1-07 case that used `gov close` as its
  not-built example.

## W1-38: rulesync adapters and the adapter-portability check (DEC-468, DEC-469, DEC-471, DEC-481; 2026-10-07)

Merged at `ca5889c9` (87 cases; `src/gov/adapters/portability.py` 202 lines against an estimate of 50, the
rest adapter source text and one check declaration). `adapter-portability` (family adapter/model portability,
tier G1, severity hard-block) makes three comparisons: the installed rulesync version with the registered
one; the kernel's roles and skills with their `.rulesync/` sources, tools included; and the project's
generated files, byte for byte, with a fresh generation.

- `gov check` on the branch before the merge (`log/check-at-W1-38-premerge.json`): `adapter-portability` is
  red with 43 findings and joins the baseline with that state (DEC-481): this repository's `.claude/`,
  `CLAUDE.md` and `AGENTS.md` are hand-kept until the owner applies the generated output at the exit (28
  findings under `.claude/skills`, 6 agents, 6 commands, the settings file, `CLAUDE.md`, `AGENTS.md`).
  `product-traceability-trailers` 735 as recorded (DEC-482); the twelve earlier baseline reds.
- Full regression at `ca5889c9` (`log/reg/at-W1-38-merge.txt`): every suite passed, `RESULT: ALL PASS`; no
  suite needed a run alone.
- Own runs (`log/W1-38-own.txt`): W1-38 87, W1-33 113, W1-35 112, W1-36 84, W1-29 45, W1-28 149, W1-26 212 and
  1 skipped, W1-04 336, W1-07 219, unit 1094; again at the merged branch head: W1-38 87, W1-33 113, W1-30 204,
  unit 1251.
- **The check generates.** It runs `rulesync generate` from the project's `.rulesync/` into an empty
  temporary folder of its own and writes nothing in the project (within the owner's rule, DEC-481). It needs
  rulesync and Node where it runs; where they are absent it reports an error, not a match.
- **One edit can give many findings:** a change in a skill that has supporting files gave 11 findings in a
  case; the 43 here are one cause.
- Where the check can still say "matches" without having compared (for the Wave 2 list, DEC-466): paths under
  `.claude/` other than the three generated folders and the settings file are not judged (what a live session
  writes there is looked at in W1-42, DEC-471); `settings.local.json` and `worktrees/` are other owners'; a
  generated file is compared with what the installed rulesync produces, so a wrong but registered rulesync
  gives a wrong reference.
- **For W1-40:** a CI step that runs the same comparison (the first lead's package). **For W1-42:** whether a
  live session loads the generated roles, skills and commands.
- History of the branch, for the exit auditor: the lead's second run (`a95e54a3`) edited eight kernel skill
  files outside the ticket's paths (flagged by containment, left in history); the orchestrator restored them
  from `b8137e35` in `deead8f9`. The lead's two runs were read and not accepted (the version checked only if
  a configuration named one; the kernel never compared with the source copies; cases that held only that a
  file exists); the behaviour was then built by direct designer and engineer turns. One engineer session
  checked out another commit in the worktree and repaired it itself; briefs now forbid it.
- Learning metrics: KPI disputes raised by the designer: two, settled by DEC-468, DEC-469 and DEC-471;
  acceptance cases rewritten after implementation began: the round-3 and round-4 batches, for comparisons
  the lead's code claimed without making.

## W1-30 follow-up: `gov close` after its two independent reviews (DEC-487, DEC-490, DEC-492, DEC-498, DEC-500; 2026-10-07)

The follow-up to the merge at `2c71bc64`: rounds 8 to 10 on `w1/W1-30` (290 cases; `src/gov/close/` is
`command.py`, `repo.py`, `state.py`, `tool.py`). One run of `gov close` now reports every finding in one
refusal, counted once, with one repair ticket; it finds the ticket tool at the kernel's place and, where
that holds nothing, on PATH; it measures the commit and not the tree; it reads every probe record. The first
review (reviewer session `350cc2a3-27ae-4888-834a-c6df2fc31b79`, at `6f2130c8`) returned thirteen findings
and the second and last (session `35e6015b-375b-4173-87df-7d5abfc1e07b`, at `b59d7244`) sixteen; the last
round (designer `1fac7f2a`, engineer `fa5180ed`) came after the second review and was read by the
orchestrator only (DEC-498: no third review). **Deviation (DEC-498):** the ticket was merged before any
independent probe of its final code.

What `gov close` still does not measure, or can be made to pass, each known and none fixed here:

- **From the last review (DEC-500), by its finding number.** (2) A commit without a task that adds a test
  configuration file outside the ticket's folder (`tests/conftest.py`, a root `conftest.py`, `pytest.ini`,
  `pyproject.toml`) decides what the acceptance run measures and refuses nothing: a gap in DEC-490's own
  rule. (4) The range of commits follows git's date order, not ancestry: a backdated commit plus a merge
  hides a task-less commit. (5) "By the orchestrator" on a probe record is a self-written `Role:` trailer;
  whether such a commit can be made is the guard's matter. (9) Any owner decision recorded after an
  escalation lifts it, whatever it is about. (10) Removing both state files resets an escalation, and
  removing the counter before the third refusal resets the count. (11) The close record lists no skills in
  a project with an installed kernel (it reads the template's place only): for W1-41's adoption. (12) An
  interruption while the ticket tool closes leaves the close record and the checkpoint; the next close
  refuses for them. (14) Template kernel folders outside the six listed prefixes do not run the governance
  checks. (15) A ticket argument that is a path is taken as a ticket and writes a counter outside the
  iterations folder; nothing closes. (16) In a project that does not ignore compiled files, a refused
  close's own test run makes the next close answer "tree not committed". (3, other side) A probe record of
  an earlier round refuses beside a passing one: the orchestrator keeps only the record of the final code.
- **Files the commit's own ignore rules ignore** are in the tree the tests run in and not in the commit
  (the ordinary form of finding 6); closing it means running the tests in a clean checkout of the commit.
- **Left open by the last round, by the engineer's own account.** Only the git that `gov close` itself asks
  is cut off from the caller's environment and from replacement refs: containment, the check runner, the
  store, the context and the watchdog call git themselves. The repository's and the caller's git
  configuration files still reach every call (an excludes file they name is caught). Of the interpreter's
  variables three still reach the test runs (`PYTHONUSERBASE`, `PYTHONPYCACHEPREFIX`,
  `PYTHONDONTWRITEBYTECODE`); the rest of the caller's environment reaches them too.
- **From the engineers' lists of rounds 8 and 9.** A regression run that collects or passes nothing counts
  as passed. An acceptance run with one passing test counts as measured whatever was skipped (skips are now
  counted in the record and refuse nothing). The governance checks run only when a commit in the range
  touches a governance prefix; otherwise the close record carries no check result. The tree and `HEAD` are
  checked once at the start, not again before the ticket is closed. A committed `conftest.py` inside the
  ticket's own folder runs. A merge commit without a task that brings ticket work refuses even where the
  merged commits were measured (it over-refuses). `deviations` is always "not measured", and the watchdog
  is given no context utilisation. The status read-back after a ticket tool on PATH checks only the ticket
  file's `status` field. `_work_of` imports a private function of the guard
  (`gov.guard.decide._match_pattern`). `src/gov/close/traceability.py:101` keeps an `except Exception`
  from before these rounds.
- **DEC-487's four residuals** stand: the owner's decision is read from decision files only (DEC-483, for
  W1-41); the escalation state is in files the caller can write; the probe record's sessions are not
  checked against a launch record (Wave 2, DEC-470); the time limit covers each test run, not the whole
  close.
- **The governance share is not yet in the close record:** the call to the counter is a follow-up once
  W1-31 is merged (DEC-495); until then `gov telemetry` is run beside each close.
- **Process notes.** The round-9 test designer edited the suite's support file with a script instead of the
  Edit tool (inside its folder). Rounds 9 and 10 each outlasted the tool's ten-minute limit in the workers'
  foreground runs and finished in the background; each worker waited for the end before committing.
- **KPI disputes:** none raised as disputes. **Acceptance tests rewritten after implementation began:**
  rounds 8 to 10 rewrote none by their designers' accounts (round 8's rewrites carry their reasons in the
  README; the `Rewrite-Reason:` trailer began with DEC-491).

## W1-40: the hooks and the CI job (DEC-489, DEC-494, DEC-497; 2026-10-07)

Merged from `w1/W1-40` (74 cases; `src/gov/ci` 175 lines against an estimate of 80, the rest the evidence
record, the CI gate and the decided install and "unmeasured" behaviour). `lefthook.yml` runs
`gov ci checks G1 G2` and `gov ci staged-secrets` before a commit and `gov ci push <remote>` before a push;
the push hook runs the declared G3 checks and leaves the evidence record, a JSON git note on the head commit
under `refs/notes/gov-evidence`. `.github/workflows/ci.yml` installs the `gov` package from the checkout and
gitleaks from the registry's archive, verified against the registry's checksum before it is unpacked, then
runs `gov ci job`, gitleaks, the tests and `gov ci record`; every step runs after a failed one. The two root
files are byte-identical copies of their templates. **No hook is installed:** `~/.local/bin/lefthook install`
is the owner's step at the Wave 1 exit, once the baseline is empty. The suite's README lists the residuals
as R-1 to R-21; the ones that matter outside the suite:

- **This repository's CI job is red with "unmeasured"** until the owner approves pytest, openspec and
  rulesync for the hosted runner (DEC-497). Once pytest is there, `python3 -m pytest tests` runs every
  acceptance suite of this repository (over an hour, needing tools the runner lacks).
- **The runner is a simulation.** The real checkout, the runner image, the network, the real download and
  its checksum, `python3 -m pip install .` on the runner's system Python, `gov` on PATH after it, PyYAML for
  the gitleaks step, and whether the host accepts the pushed notes ref are all seen for the first time on
  the owner's first push. A failure there is red, never falsely green.
- **Bypasses by design of git and lefthook:** a commit without lefthook on PATH passes (the generated hook
  exits 0); `--no-verify` and `LEFTHOOK=0` skip the hooks. A bypassed push has no record, so CI is red;
  nothing holds against a bypassed commit until the push.
- **The evidence record can be written by hand** (DEC-489), also one that says "no G3 check declared" for a
  project that declares G3 checks; comparing the note with the checkout's declarations is a cheap Wave 2
  addition. Removing a project's G3 declarations turns the gate into a report (DEC-497). The record is bound
  to the head commit while G3 runs on the working tree.
- **Left as built by DEC-497 (Wave 2 list):** the notes ref with several clones (never forced; fetch and
  merge before writing); `gov ci` declares the class "read" though `push` writes a note; the skill-version
  check reads a missing parent commit as green (`src/gov/check/runner.py`, W1-26's code) and only the last
  commit of a push is compared; tier selection calls the check runner's internals (`gov check` has no tier
  option).
- **What passes as yellow in the job:** a warning-severity or not-applicable check whose tool is absent
  (only the finding codes `OPENSPEC_ABSENT` and `RULESYNC_ABSENT` are known as "tool absent"); openspec with
  nothing to validate; a failing warning-severity check; a family with no check; a missing or malformed
  path map yields no policy result at all.
- **gitleaks in CI** scans only the two commits of the checkout; earlier commits of a multi-commit push are
  not scanned there. The install trusts the registry of the pushed commit, and the unpacked binary's version
  is not compared with the registry's. A product project needs a registry with the `archive` fields or the
  step fails. The second, strict gitleaks scan of the pre-commit hook against the canary fixtures is for the
  exit package (DEC-489).
- **The word "unmeasured"** is held for pytest, openspec and rulesync only; a missing `gov` or gitleaks fails
  with "command not found", and the hooks do not use the word.
- **The adapter comparison has no step of its own** (DEC-497); with a stand-in rulesync the case is green:
  what the real rulesync generates is W1-38's.
- **The guard refuses to create the folder of an allowed file** (`mkdir -p .github/workflows` by the
  engineer); the file was produced by `install -D` and `cp` (accepted, DEC-497). The Write tool refuses
  `lefthook.yml` by its name (DEC-489).
- **Not derived:** S0a-G-11 (not in the readable tree).
- **One W1-16 case** (the one that watches `.gov-runtime` for new files) failed once in the lead's full run
  on files of the lead's own wait calls, and passed alone.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** two, both for DEC-497,
  with their `Rewrite-Reason:` trailer (`54829432`).

## W1-39: the Copier template and the framework lock (DEC-488, DEC-493, DEC-499; 2026-10-07)

Merged from `w1/W1-39` (67 cases; 218 source lines added against an estimate of 100, about 40 of them the
update procedure's text in the lock header and in `copier.yml`). `gov.lock.compare(root)` answers `MATCH`,
`DRIFT`, `UNLOCKED` (an answers file and no lock), `MISSING` (neither) or `ERROR`; `gov doctor` reports
`MATCH` as passed, `MISSING` as unmeasured and every other answer as failed. `python3 -m gov.lock` writes
`governance/framework.lock` as the one Copier task. Copier was never pointed at this repository.

- `gov check` on the branch before the merge (`log/check-at-W1-39-premerge.json`): no red outside the
  baseline, and the two baseline checks with a recorded count are unchanged (43 and 735).
- **A project can still silence the comparison (DEC-499):** deleting both the lock and the answers file gives
  "unmeasured" and exit code 0; editing the lock's manifest together with a kernel file gives a match. The
  lock is unsigned until Wave 3 (CAP-02.c). Tag and commit are compared with the answers file only, and the
  project can edit both.
- **What the comparison does not look at:** anything inside a `__pycache__/` folder under the kernel
  (DEC-488); anything outside `governance/kernel/` (the generated `.claude/`, the overlay, `.rulesync/`);
  a file's mode (a hook that loses its executable bit is a match); an added empty folder. One listed kernel
  file that was hashed is enough for a match to be possible.
- **A manifest key that is no valid path** raises a traceback (not a false match).
- **The lock task needs the `python3` on PATH to import `gov`:** where `gov` is installed as an isolated
  tool the copy fails at the task. A `gov lock` subcommand is decided with W1-41 (DEC-499).
- **The shipped path map is not valid against the kernel's path-map schema** (namespaces only, no systems):
  a fresh project is at MINIMAL by it; W1-41's adoption settles validity (DEC-499).
- **Declared check commands still name `template/…` paths** that an installed project does not have: for
  W1-41.
- **Adapter generation is a documented step, not run at the copy** (DEC-488); the cases hold only that the
  procedure names rulesync. Which `.rulesync/` paths are the project's own is in no source (ADR-0002 §5).
- **`gov doctor` on a fresh project:** tools, hooks, index, canaries and isolation are unmeasured (W1-40,
  W1-41, the exit run). The Claude Code part reads the machine's real CLI whatever `HOME` says.
- **Not derived:** G-14 and S0a-G-15 (their text is not in the readable tree). "Nothing else is shipped in
  the overlay" is the brief's reading of DEC-493.
- **Loose case:** `test_a_kernel_folder_that_cannot_be_listed_is_not_passed_over` accepts any of several
  reason words. **No case:** an answers file that cannot be read as a map, with no lock.
- **The writer blocks on a FIFO under the kernel;** the comparison reports it as drift without reading it.
- **W1-19's warm-query latency case** failed twice in the lead's runs at a load average near 20 and passed
  alone; W1-19 passed whole in the orchestrator's run (41 passed).
- **Found only after the merge (2026-10-08):** W1-40 added `lefthook.yml` and the CI workflow to the template,
  and the template's path map did not class them, so `gov doctor` failed on a freshly created project: five
  cases red on the integration branch at `855c0e08`, each branch green alone. Fixed on the ticket's branch
  (`36abb70d`: `lefthook.yml` in the `repository` namespace, `.github/**` in a new `ci` namespace) and
  merged again. **A project installed before this fix does not get it by update:** `governance/project/**`
  is never overwritten, so its path map needs the two entries by hand. No check holds "every file the
  template ships is classed by the path map it ships" outside W1-39's own cases.
- **The regression summary's last line was the plan validator's,** not a verdict on the suites; the
  orchestrator reads every suite's line (script corrected).
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** one
  (`test_a_missing_lock_is_not_a_match`, strengthened by DEC-499, with its `Rewrite-Reason:` trailer).

## W1-31: the governance-share counter (DEC-491, DEC-495, DEC-501, DEC-502, DEC-507, DEC-512; 2026-10-08)

Merged from `w1/W1-31` at `35904984` (131 cases; `src/gov/telemetry` 646 lines against an estimate of 150:
the counter reads the harness's session logs itself, which the estimate did not foresee).
`gov telemetry <ticket> [--json] [--ticket-session <session id>[=<role>]]...` and
`gov.telemetry.counter.measure(root, ticket, sessions)` give a record with the five measured governance
sources, a labelled estimate, three share figures (measured, estimated, total), tokens in and out, cache
creation apart, cache reads outside the share, and "not measured" by name for whatever it could not read.
It outputs counts only, never log text. The log forms were learnt from three specimens made in throwaway
projects in `/tmp` (`specimen/` in the orchestrator's scratch); no worker and no test read a real session
log.

- **The call from `gov close` is not built** (DEC-495: a W1-30 follow-up). `gov close` must write the close
  record first and measure after; the caller supplies each session as `<session id>=<role>`. The close
  record is "not measured" until it exists, so a measure before the close ends with exit code 3.
- **The estimate (DEC-507)** reads the session role's file under `.claude/agents/`, `CLAUDE.md` and
  `AGENTS.md` as they are when the counter runs, not as they were in the session; neither root file exists
  in this repository, so here it is the role file alone. **The role is the caller's word, unverified,**
  until launch records carry it (DEC-470). Without a usable role the estimate and the estimated and total
  shares are "not measured". MCP counts 0 with its reason. A sub-agent's own instruction files are not in
  the estimate (a named gap; DEC-512 F).
- **The counter accepts only logs of Claude Code 2.1.288;** another version is refused until a new specimen
  is read.
- **The denominator is slightly low:** the harness's own totals include calls the log does not show as
  assistant lines, so the share reads slightly high; W1-42 reports the difference once (DEC-501). `cost` is
  ccusage's figure from its built-in prices; only the four token figures are held against the log, and a
  model without a price gives "not measured" for cost.
- **"Not measured" by name, until a fourth specimen shows the form (DEC-512):** an interpreter word other
  than `python3` running `gov.cli.main`; `gov` through a runner on the fixed list (`uv run` and the like); a
  SessionStart with plain text and an added-context line at the same start; a permission rule's denial of a
  tool other than Bash; a user line whose content is a list holding anything but tool results; a text line
  marked `isMeta` of an unknown kind; a feedback line not followed at once by its `system` line.
- **Where the count can be low without a sign:** `gov` inside `bash -c`, `eval`, backticks or a wrapper
  script, or behind a runner outside the fixed list (the first four are named in the record's known gaps,
  the last is not); only Bash tool calls are examined for `gov`; plain output of a successful hook of any
  event but SessionStart counts 0 (DEC-502); governance text in a new key of a known line form; a
  sub-agent's log kept anywhere but the session's `subagents` folder; an over-long result is counted as
  logged (its shortened form; the `tool-results` folder is passed over by name, unchecked); a SessionStart
  run with empty `content` counts 0 without its `stdout` being checked; files in a checkpoint folder whose
  names are not a checkpoint record's; the automatic checkpoint folder of another worktree.
- **Where the larger reading is taken (the record says so):** the text of a blocking, denying or failing
  hook is counted whole, with the harness's prefix (the denial sentence is accepted for any tool word); a
  SessionStart hook's plain text is counted as the packet; a compound, piped or redirected `gov` command has
  its whole result counted.
- **Not shown by any specimen:** an automatic compaction. A PreCompact hook's output is a named gap (it is
  in no hook line); this repository registers such a hook (DEC-512 corrects DEC-502 on that).
- **Order of commits** for "rewritten after implementation began" is git's topological log order, not
  ancestry across parallel branches. `agent.harness` is a literal.
- **The sandbox's added system-prompt tokens** are "not measured" until W1-42 makes the paired measurement
  and places its record (DEC-491, DEC-501).
- **Incident 1:** the run-2 test designer ran a search with a glob over `governance/project/*.yaml`, which
  takes in the held-out file; it reported one hit, in `path-map.yaml`, and nothing else displayed or used.
  Told to the owner; briefs forbid globs, searches and listings over that folder (DEC-508).
- **Incident 2:** the run-4 lead loaded `.claude/settings.json` in a script to list the registered hook
  events (the brief allows `git diff --stat` only on that file). By its own account the script printed the
  `hooks` section only (five event names with matcher and command), so the deny line was not displayed. Told
  to the owner.
- **Launched workers were refused Write under `.gov-runtime/scratch/`** ("directory denied") in this
  worktree. Leads and a test designer fed read-only scripts to the interpreter by here-document; three
  writing commands of the run-4 designer were refused by the guard. The lead's last message of run 3 was a
  note after its return; the return was recovered by resuming that session once without tools.
- **W1-46 in the lead's run 4:** 23 errors at setup from one shared live research session that ran its
  second step from the wrong folder; 493 passed when run alone.
- **KPI disputes:** three in run 3 (settled by DEC-502), six in run 4 (settled by DEC-512). **Acceptance
  tests rewritten after implementation began:** three designer commits (`7fdfb672`, `50e88b9f`, `8e716c60`),
  each with its `Rewrite-Reason:` trailer.

## W1-32: `gov status` and the launcher's two residuals (DEC-392, DEC-449, DEC-526; 2026-10-08)

Merged from `w1/W1-32` at `ff85c968` (81 cases; 266 source lines added against an estimate of 80: about
190 in `src/gov/status/command.py`, about 75 in the launcher). `gov status --json` always answers
`ok: true` with exit 0 (W1-07 holds it to exit 0 without a store) and gives `tickets` (ready, blocked with
reasons, claimed with holder), `decision_packages`, `readiness`, `governance_share`, `pause`, `doctor` and
`not_read`; whatever could not be read is `{read: false, reason}` and is listed under `not_read`. The
launcher ends its session on SIGINT, SIGTERM and SIGHUP (asked first, killed on a second signal or 5 s
later), removes the session's folder and ends with 130; a failed removal keeps the session's exit code.
Merged as built under DEC-526 while package P-19 is with the owner; the ticket is not closed.

Not covered or not built, by name:

- **The natural-language half of CAP-28.a.** No skill, role file or instruction line routes a status
  question to `gov status --json`; the file would lie in `.claude/**`, `CLAUDE.md`, `AGENTS.md` or the
  kernel skills, outside the ticket's paths. No case covers it (P-19 point 2).
- **Governance share in status** is "not measured" for every claimed ticket: nothing records a ticket's
  sessions (DEC-491), so the counter is asked with no session named.
- **Gates:** only open decision packages and specifications with an open required readiness row are
  shown. Audit tickets (DEC-088), the check gates and `gate` records are not.
- **`src/gov/status/command.py`:**
  - a ticket constrained by a package whose record could not load is still listed `ready` (the READY
    rule in `src/gov/tasks/queue.py`, outside the paths, fails open here);
  - an absent `.tickets/` or `openspec/changes/` reads as an empty list;
  - the store is trusted when it holds `HEAD`'s commit and its tables answer: rows removed, or a store of
    a later commit, read as clean; the store is probed once and read again, so a break in between gives
    an unmarked empty `ready`;
  - records come from `HEAD` only: an uncommitted package is not shown and nothing says so;
  - any Markdown record at `HEAD` that the load cannot take appears under `decision_packages` as not
    read, not only likely packages;
  - status imports two private functions (the loader's `_read_records`, the guard's `_mirror_frozen`); a
    missing mirror folder reads as not frozen, the guard's own reading;
  - doctor's part states are passed on as the status word only, without reasons;
  - the exit code is 0 even when parts were not read;
  - it is as slow as doctor (10.9 s under load).
- **`src/gov/cli/commands/status.py`** is dead code, outside the ticket's paths.
- **`src/gov/launch/launcher.py`:**
  - only the session process is signalled, not its process group: a command the session started can
    outlive it;
  - SIGQUIT, SIGUSR1 or SIGKILL to the launcher leaves the session running and the folder in place;
  - a signal ignored on entry (`nohup`) stays ignored;
  - a launcher signal in the instant after the session ended on its own gives 130 instead of its code; a
    session killed by a signal passes on a negative code;
  - an error other than `OSError` from the removal, or an error restoring the handlers, would replace
    the exit code;
  - the handlers need the main thread: `launch()` from another thread raises before anything starts.
- **`src/gov/cli/main.py`** (outside the paths): a refusal printed to an unwritable stderr ends with a
  traceback's code; no session exists on that path.
- **The command list:** `gov --help` shows `ci`, `launch` and `telemetry` beyond the twelve reserved
  names; the suite pins the three as found and goes red when another command is added (P-19 point 3).
- **Checkpoints:** four real records under `docs/checkpoints/DAEO-8goq/`; the command numbered the first
  one 0002 and there is no 0001.
- **Sandbox:** placeholder dotfiles and `docs/source` show as untracked inside a worker's sandbox; the
  designer could not read S0a-G-01 there. The hook's containment notice attributed the designer's files to
  the lead's waiting call (DEC-253 to DEC-255).
- **Latency under load (DEC-372):** in the lead's full runs one W1-05 p95 case and one W1-19 p95 case
  failed while two suite streams ran side by side; each passed alone.
- **KPI disputes:** six (four from the test designer, two from the lead's reading of the diff), all in
  package P-19. **Acceptance tests rewritten after implementation began:** none; eleven cases were added
  after the lead's diff reading (nine red first, two guards).
- **At the close (2026-10-09):** gov close ran once at e57326e9 and refused with 31 findings
  (.gov-runtime/scratch/orchestrator/log/close-W1-32.json): the governance checks red as at the closes of
  W1-31, W1-39 and W1-40; two orchestrator commits of 2026-10-05 without an Implements trailer; the context
  blocked on the outside source S0a-G-01; and two W1-05 latency cases that failed while five leads ran
  (8787 passed, 2 failed, 29 skipped) and passed when W1-05 was run alone afterwards (99 passed, DEC-372).
  Closed with the ticket tool under DEC-492, DEC-511, DEC-516, DEC-519 and DEC-541; listed for the exit
  auditor. **A defect of gov close seen here:** it could not open its repair ticket (the ticket tool was
  called with the whole finding text as one argument: Argument list too long), so the refusal named no
  repair ticket; for the follow-up after W1-41 (DEC-521).

## W1-35 follow-up: the orchestration skill, the ticket lead section and the brief templates (DEC-537, DEC-539, DEC-541, DEC-547, DEC-550; 2026-10-09)

Merged from `w1/W1-35` at `e2797b3b` (54 new cases, 166 in the suite; 675 lines added under `template/`, of
which 127 are the two rulesync copies; the skill is 97 lines, body 2,231 of 2,500 tokens). Delivered:
`template/governance/kernel/skills/orchestration/SKILL.md` (version 1.0.0) with its rulesync source; the
section "The ticket lead" in `template/governance/kernel/roles/orchestrator.md` with its rulesync source;
five brief templates under `template/governance/kernel/templates/` (`brief-test-designer.md`,
`brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md`, `brief-lead.md`); the check
`skill-regression-orchestration`. The skill also states the natural-language route to `gov status --json`
(the half of CAP-28.a moved here from W1-32; the Contract's file names W1-35 as a second provider). Every
row of the orchestrator's report C stands in the skill; none was dropped.

Not covered or not built, by name:

- **Text only.** No case shows a session answering a status question from `gov status --json`, a filled
  brief being followed, or a wave being run this way: each needs a model session and this repository's
  generated `.claude/skills/`. W1-42 runs from the skill and the briefs (its KPI line) and is where this is
  shown.
- **The adapter-portability check at this repository's root has two more findings** (one source missing,
  one source that differs) beside the 43 of DEC-481, until the owner applies the rulesync sources and the
  generated output at the exit (DEC-550). They are in the exit package.
- **Followed by hand, not enforced by a mechanism (Wave 2, DEC-537):** the resource gate, a launch without
  a model, `AUTH_REQUIRED`, leads started through the launcher. The skill says so in its last section.
- **Citations.** Rules that only this repository's orchestrator prompt held are cited with DEC-537. Loose
  citations the lead noticed: "never into the main branch" under DEC-235 and DEC-416; the rule against two
  writing sessions under DEC-254, which records misattributions; "against the last known state" under
  DEC-236 and DEC-449; DEC-183 for identity through the settings argument although DEC-371 superseded it
  for launched roles; DEC-486 for the stop's block although it covers the closed count only.
- **A project's own values are placeholders** (integration branch, ceiling, free memory, model, the CLI's
  path, the decision trailer): nothing fills them or checks that they were filled.
- **The launcher command stands in a code span** in `brief-lead.md` and the role file's lead section; the
  skill validator would flag that inside a skill and does not read templates or role files.
- **The five briefs have no record frontmatter** and no schema; the templates folder's other files do.
- **The orchestrator prompt of this repository is unchanged** and still holds the same rules; from W1-42 on
  the skill and the briefs are the source.
- **Sandbox:** a worker's Write under `.gov-runtime/scratch/` was denied by its permission settings and a
  `mkdir` under `template/.rulesync/skills/` by the guard (it used the Write tool); the containment hook
  twice attributed the test designer's files to the lead's waiting call.
- **Latency under load (DEC-372):** three W1-05 p95 cases failed in the lead's full run at a load of 20 to
  33 and passed alone.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** none; 54 added.

## W1-30 follow-up: the parallel test runs of `gov close`, the serial-only list, the rebuild without embeddings (DEC-527 to DEC-532, DEC-549, DEC-554, DEC-555; 2026-10-09)

Merged from `w1/W1-30` at `c52de7c2` (probed at that commit; 355 cases in the suite). Built: `gov close`
runs the ticket's acceptance tests and the regression tests with the installed runner's parallel option, and
the cases that `tests/acceptance/serial-only.txt` names (53 entries here) alone afterwards, each once; the
plugin that keeps them out is `src/gov/close/pytest_plugin/gov_close_serial_only.py`; the close record and
the result state each run under `test_runs`; `close_workers` (default `auto`) and `close_timeout` are
optional top-level keys of `governance/project/path-map.yaml`, refused with `INVALID_WORKERS` or
`INVALID_TIMEOUT` when of a wrong shape; `gov rebuild --no-embeddings`. Test-side repairs, each with
"defect found by the parallel trial": two W1-50 files that set their own import path, the pause's unit case,
W1-27's own wait for its commands (180 s), W1-30's temporary projects with two workers. This repository's
path map now says `close_timeout: 7200`.

As measured by the lead (two whole regressions in the close form, other leads' suites running beside them):
the ticket's own run 142 to 152 s, everything else in parallel 793 to 1038 s, the declared cases alone 1341
to 1968 s. A close of this repository: about 16 to 20 minutes for the parallel part and 28 to 33 for the
serial part, against 80 to 110 minutes before.

From the probe (session `2e97ad0c-eee6-4500-baae-303e79f117f7`; record in `docs/probes/DAEO-2lwj/`).
**To be built in the follow-up after W1-41 (DEC-555), test designer first:**

- **Fails open, deliberate or unusual shape:** a run of the declared cases that ends with exit code 0 and no
  result (a case that ends its own process with 0) is accepted; the parallel run's passes cover it. Until
  the follow-up, the orchestrator reads each close's `test_runs`.
- **Closes by the caller's input, deliberate:** a file in the project named like the close's plugin (under
  `src/` or at the root) replaces it, so a ticket's own commit can keep a failing case out of every run.
- Parallel workers outlive a run cut at the time limit: they finish their cases during the serial run and
  after the close has returned, and can still write into the project. The close is refused either way.
- A list entry that names an existing file with no case in it refuses nothing (only a file or function that
  does not exist does), against DEC-549's fourth point.
- A byte in the list that is not UTF-8 ends the close in a traceback (fails closed).

**Residuals, not planned:**

- Counts that do not match what ran for entries outside the documented forms: a parent folder as an entry
  counts cases twice in `tests_run`; a trailing slash, `//` or `..` in an entry runs its cases twice.
- `test_runs` says `parallel` with `workers: auto` for a run in which the runner started no worker (a
  machine that sets the runner's own worker-count variable to 0); the record states `auto`, not the number.
- `close_workers` has no upper bound; YAML's own readings (`010` as 8, `1:30` as 90) are accepted; a time
  limit of about 9.2e9 seconds or more ends in a traceback.
- A list path that is a folder declares nothing; a byte-order mark drops the first entry silently (its cases
  then run in parallel).
- An unusable parallel plugin (autoload switched off by the caller, `-p no:xdist` in the project, a project
  folder named like it) is a finding counted against the ticket, not "could not measure".
- Without the parallel plugin the close runs serially with a note and no finding.
- The rebuild mode does not remove vectors an earlier full rebuild left in the store (the semantic status
  reports them stale once an embedded file changed); a full rebuild runs before W1-42's retrieval
  measurements (DEC-530).
- A close started inside a parallel worker passes the runner's worker variable on to its own runs.
- W1-36's helper takes any `PYTHONPATH` that contains the `src` path as a substring for the path itself.
- W1-27's `run_python_snippet` and one literal 30 s wait in its recovery cases keep the old bound.
- W1-07's 30 s wait for a read command was passed once under ten workers (`gov status --json`); re-run
  alone and named until a designer lengthens it in the follow-up after W1-41 (DEC-554).
- The kernel's path-map schema names neither new key (DEC-554, the same follow-up).
- One failure of the unit case `test_options_of_the_callers_environment_do_not_reach_the_run[--collect-only]`
  in run F1 is unexplained; it did not recur in ten unit runs.
- A path map in a small project brings the lexical index into its `gov rebuild`.
- Not probed: another version of the parallel plugin, a very large worker count, a close inside a parallel
  worker.
- **Latency under load (DEC-372):** W1-05's switch-over case failed once in the serial part at a load of 17
  (its child run's W1-02 p95) and passed alone.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** five support or fixture
  commits, each "defect found by the parallel trial"; no assertion changed. Added: rounds 11 and 12.

**W1-35 follow-up closed (2026-10-09)** with the ticket tool under DEC-492, DEC-516, DEC-536, DEC-550 and DEC-558. The close ran on the merge commit and refused as every close does before adoption; its output is kept (the orchestrator's log, close-W1-35F.json). No test failed in it, latency cases included. Its one finding that was not an adoption gap, the test designer's commit a7eb9257 without an Implements trailer, is a named exception (DEC-558). Listed for the exit auditor.

## W1-02 follow-up: the guard refuses reads of the settings file and the held-out file, for every role (DEC-508, DEC-525, DEC-548, DEC-553, DEC-562; 2026-10-09)

Merged from `w1/W1-02` at `e9e6ee25` (probed at that commit; 1690 cases in the suite, 1161 of them new in
three batches). Built: the read rule in `src/gov/guard/protected.py`, called from the guard's decision for
every role and for a session with no role (the reading tool, the search tools, the notebook tool, the
shell); copies at the same project-relative path under another folder are treated as the files are (the
home folder's settings file among them); a second name (move, link, linking copy, in-place edit with a
backup, a move or link of a holding folder) is a read; the helper `python3 -m gov.guard.hooks` lists the
registered hooks with deny values and deny paths redacted. The refusal text names DEC-508 and DEC-525 and
no path. Comparisons over 420,000 and 840,000 random calls against the earlier heads: none refused before
and allowed after. From this merge on, a command or commit message that carries either file's path is
refused: write "the settings file" and "the held-out file".

**Built next, in the round of DEC-557 (after this merge, with its own probe):** a search from the project
root with no path or glob is refused for every role (14 cases of four suites rewritten, "owner decision
P-23"); a shell search with a name filter that names or matches either file (probe finding 1: a read that
gets through in ordinary work, such as `grep -rn . --include='*.<extension>' .`); an answer in bounded time
for every pattern and command (probe finding 7: a glob of many star pairs took 39 s and more; what the
harness does with a hook past its time limit is to be established); a NUL byte refused wherever it stands.

**What a command-line guard cannot see (residuals):**

1. A script file that opens either file; a script on the command line that builds the name; an interpreter
   or shell fed by a pipe or standard input.
2. A name that arrives at run time (substitution, a variable the command sets, `xargs`, `find -exec`):
   refused for writes, not held for reads.
3. A command that names no path and reads the tree or history (`git diff` with no path, `git show`,
   `git log -p`, `git grep`, an archive of the root); a git object read by its id.
4. A second name or copy made earlier, outside the call; a copy under another name or relative path; a copy
   that is itself a symbolic link named through a path that resolves elsewhere.
5. A program that reads the settings file by itself (`claude`, `rulesync`); a tool the guard does not know.
6. `git -C <another checkout>` with a relative path; a `cd` into a folder that exists only at run time.
7. A copy reached by a glob or search that starts above its folder (answered with DEC-557's round where the
   pattern names the file); a path that ends in a file's project-relative path and names no file yet.
8. A second name by a program the guard does not know (`rsync --link-dest`, `install`, `cp --reflink`,
   `git mv`, `tar`, `rename`, a bind mount, an editor's backup); in-place options that cannot be told from a
   suffix (`sed -i bak` without a dot); a move or copy with an option the operand reader cannot read; a move
   or link of the folder a copy's folder lies under, or of a folder above it.
9. A user-level settings file that is not at `$HOME` of the hook's environment.
10. A wildcard-only word in a command that is no reader; other spellings of "everything".

**From the probe (session `cc784d3e-ecb5-4176-8726-847f86f79cf6`; record in `docs/probes/DAEO-emkd/`), each
in a deliberate or unusual shape:**

11. A `cd` is followed whether or not it takes effect (in a subshell, a pipeline, a background job, a branch
    not taken, or to a folder that does not exist): `(cd /tmp); cat <the file>` is allowed; the reverse
    refuses two ordinary listings after a `cd` into the folder above the file.
12. Shell spellings the token expansion gives up on are allowed: `$'…'`, `$"…"`, `~+/`, an unset variable or
    `$@` glued to the name.
13. A script on the command line with an operator glued to the name (`bash -c "cat <the file>|head"`, the
    same with `<`, `>`, `&&`, a backtick), `eval` of the same, and a here-string into a shell are allowed.
14. Search-tool globs with an escaped dot, a leading backslash, single braces, or a comma list are allowed
    (the rule reads only `*`, `?` and `[` as pattern signs).
15. An in-place edit that prints (`sed -i 'w /dev/stdout'`) by a role that may write the file is allowed.
16. The helper prints a deny path when the rule's shape is not the one the project's writer produces (a
    deeper pattern after the path, a shell rule, a tool name with a hyphen, a stray space or newline), when
    the path stands outside `permissions.deny` (in the ask or allow list, in the sandbox's list, a deny that
    is no list), in `matcher` or as an event key, with a doubled slash or `/./`, after a shorter deny value
    was replaced inside it, or resolved with `HOME=/`. Each needs a hook command that carries the path.
17. Helper: a project-relative spelling, `$HOME/…`, `${HOME}/…`, `~user/…`, a longer name that begins with
    a deny path, a rule that is the home folder itself.
18. A reading tool call whose path field is a list or a number is answered allow (the tool cannot run it).
19. A command of 200 KB of short words costs about 8 s in the read rule.

- **Two test-designer commits of the first batch, `15a0dbc4` and `56f1476d`, carry no `Implements:`**: named
  exceptions for the exit auditor (DEC-558).
- **Latency under load (DEC-372):** in the second run one W1-02 p95 case (about 220 ms with three runs in
  parallel) and one W1-05 p95 case (about 190 ms) failed and passed alone; none in the third run.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** none; 1161 added in
  three planned batches, each red first.

**W1-30 follow-up closed (2026-10-09)** with the ticket tool under DEC-492, DEC-505, DEC-516, DEC-536, DEC-555, DEC-563 and DEC-566. The close ran on the merge commit in the parallel form (rebuild without embeddings 204 s, close 2,916 s with three other sessions on the machine; 8,660 passed, 1 failed, 29 skipped in the regression part, the ticket's own 355 passed) and refused as every close does before adoption; its output is kept (the orchestrator's log, close-W1-30F.json). The one failed case, W1-16's test_this_repository_is_not_indexed_by_the_run, passed alone (DEC-563). The probe gate's finding on the orchestrator's commit ccac9506 is covered by DEC-505 (DEC-566). Listed for the exit auditor, with both.

**W1-02 follow-up closed (2026-10-09)** with the ticket tool under DEC-492, DEC-505, DEC-516, DEC-536, DEC-558 and DEC-562. The close ran on the merge commit in the parallel form (rebuild 144 s, close 2,934 s) and refused as every close does before adoption; its output is kept (close-W1-02F.json). No test failed in it. A refused close with no failed test prints no test figures: the orchestrator checked instead that no project file stands in for the close's plugin and that the serial-only list is unchanged since W1-30's own verified runs (DEC-559). The commits 15a0dbc4 and 56f1476d are named exceptions (DEC-558); the probe gate's finding on the residual commit 60961b27 is of DEC-505's kind. Listed for the exit auditor. The ticket is reopened on its branch for the round of DEC-557.

## W1-41: `gov adopt --lite`, the legacy importer and external references in the context (DEC-518 to DEC-523, DEC-535, DEC-551, DEC-552, DEC-568; 2026-10-09)

Merged from `w1/W1-41` at `868d72b9` (182 cases in the suite; probed at `920229dc`, then one fix round of
three behaviours, DEC-552). Built: `gov adopt --lite --stage <A0..A6|A8> [--map <file>] [--verdict <path>]
--session <id>`, its records under `governance/adoption/`, its refs under
`refs/gov/adoption/{backup,rollback,archive}/` of the adopted project; the legacy importer and the
dependency proof (A8); in the context, `governance/project/external-references.yaml` (this repository's
lists `S0a-G-12` and `S0a-G-13`), the packet key `external`, and `gov.context.external_references(root)`.
Source lines: 1,011 added under `src/` against an estimate of 440. `gov adopt` has not been run on this
repository; its adoption is a later, defined step (DEC-522), and the outside sources of DEC-560 are applied
there.

**To the follow-up after W1-41 (DEC-552):** the external list is read from the working tree, so a ticket
whose paths include the file can unblock its own mandatory source without a commit, and repository-held id
forms other than a decision's (`CAP-…`) are accepted in it; `RETIRED` and `REJECTED` records satisfy a
mandatory source in the context (only `SUPERSEDED` blocks); a mandatory record whose file cannot be read
gets the hash of empty bytes and counts 0 tokens, so the packet presents it as read; any retrieval failure
in the supplementary lookup becomes "index unavailable".

**To be read again before this repository's own adoption:** a move to a target that no namespace holds is
accepted and executed and then blocks A8 with `UNKNOWN_ARTEFACT`; a project whose `.gitignore` does not
name `.gov-runtime/` refuses at A8 on a dirty tree after A6's rebuild; a project without `.gitleaks.toml`
refuses an A3 with a move.

**Residuals from the probe** (session `2020c8c7-b490-4464-8b39-64fc3030412a`; record in
`docs/probes/DAEO-cdoi/`):

- After a failed batch the earlier batches stay committed, no A6 record names what they did (a deleted file
  then has no recorded disposition, against success line 6), and the next round, which the refusal tells the
  owner to run, reuses the rollback ref names. Nothing is lost: history and the first backup ref hold it.
- An interruption at a batch's commit leaves the moves staged with the rollback ref set; at the record's
  commit it leaves the batch committed and the record staged. Every later stage refuses on a dirty tree;
  there is no resume.
- A package in a flat layout (a manifest with the package beside it, or `app/`, `pages/`, `lib/` beside a
  `package.json`) moves without the two grounds of success line 7; only `src/` beside a manifest is native.
- A Cursor rule file with unquoted globs refuses A8 before the import is tried; one such file retired while
  another is kept refuses A8, because the import tool takes both. Both fail closed.
- The dependency proof still misses: a word character or `-` directly before the path or id; backslashes,
  URL-encoding, another letter case, a path split across lines; a citation of only the store's folder or a
  glob; `../` followed by only the tail of the path. A record's prose is searched for the store's paths,
  not its ids. A record that wrongly carries `RETIRED` or `REJECTED` releases the store.
- The CIT-E text and the A8 record still say "active records" where the proof reads every record that still
  stands; the chat-database proof accepts any readable record whatever its status.
- A ticket with no `sources`, a read dependency and external dependencies is built; if the ticket file
  changes between the context's two reads the judgement falls back to every declared id.

**Residuals from the build:**

- Verdict independence rests on the `Role` trailer of the commit that brought the verdict and on the
  `auditor_session` the verdict states; both are self-declared.
- Importers come from the code graph for indexed files only: an unparsed language or a bare import with no
  use reads as "no importers"; plain-text mentions are not flagged; nothing is computed for RETIRE or
  DELETE_FROM_ACTIVE_TREE. A6 does not re-check importers, references and consumers at HEAD.
- What the proposal does not name is KEEP; an executed entry with no batch goes into one last batch.
- A batch is checked by path and blob id; file modes are not compared. A8 checks the staged tree, not the
  commit itself as A6 does.
- `gov rebuild` runs after the record's commit; if it fails the stage answers a refusal though the moves or
  the retirement stand. Only the lexical store is held to `recreated`.
- A8 retires only what the path map names; a legacy rule file the proposal did not name stays loaded. The
  proof reads a fixed list of rule places (not `.github/copilot-instructions.md`, `.clinerules`,
  `GEMINI.md`), decodes with "replace", and sees a citation only by path or id, not by folder or glob.
- A `rulesync import` target is held to "contains the source body"; frontmatter is not compared. A tools
  file without `mcpServers` is kept word for word under `.rulesync/legacy/` and retired as imported. An
  `AGENTS.md` section that is only headings is dropped. Imported `.cursorrules` and `.windsurfrules` get
  `targets: ['*']`. `rulesync` 24.0.0 refuses an `.mdc` whose `globs` is a list; the tool then imports it
  itself and the record says so.
- `governance/adoption/**` is outside the inventory and the unknown check. An existing decision package is
  not removed when its artefact is later classified.
- A rollback deletes every untracked, non-ignored file; an untracked directory would make it raise.
- Reading the record graph writes `.gov-runtime/store.db` into the project.
- The tool uses two private functions (`codeintel._graph`, doctor's `_match_pattern`).
- A3 with a move needs `/tmp/gov-cbm-<uid>` writable, so the move cases cannot run in a launched session.
- `gov adopt` without `--lite` is `NOT_IMPLEMENTED`.
- External references: a dangling symlink at the file's path reads as "no file" (the id stays blocked); the
  brief summary is cut at 2500 tokens and could cut an "external, not read" line; a key the file's shape
  does not name is accepted.
- The W1-26 README's count for its planted-defects file is stale. A killed background script leaves its
  running pytest child alive (seen in the lead's verification).
- **Latency under load (DEC-372):** one W1-05 p95 case (189 ms) failed in the fix round's full run and
  passed alone. **W1-16's runtime-folder case** failed once in run 3's long run and passed alone (DEC-563).
- **KPI disputes:** P-9 to P-14 over the runs. **Acceptance tests rewritten after implementation began:**
  two (the W1-26 planted-defect case, "planned: command implemented"; one legacy case, "stricter reading
  decided after the probe (DEC-552)"). **Added after implementation began:** 68, each red first.

**W1-41 closed (2026-10-09)** with the ticket tool under DEC-492, DEC-505, DEC-516, DEC-519, DEC-522, DEC-536, DEC-552, DEC-558 and DEC-572. The close ran on the merge commit in the parallel form (rebuild without embeddings 145 s, close 3,300 s) and refused as every close does before adoption; its output is kept (close-W1-41.json). No test failed in it; the orchestrator checked that no project file stands in for the close's plugin and that the serial-only list is unchanged (DEC-559). Its findings: the baseline red checks (the schema check at 27 with three probe records, DEC-565; 152 more trailer findings about the commits of W1-30 and W1-02, closed since the last measurement, of the kinds DEC-516 and DEC-558 name); a stale checkpoint; the context blocked on the outside source G-10 (DEC-560); the probe gate on the residual commit 9a188b6d (DEC-505); and containment on 803f731c, the orchestrator's merge of the integration branch into the ticket's branch, a named exception (DEC-572). No repair ticket was opened (the findings were too long for one argument; in the follow-up after W1-41). Listed for the exit auditor, with the fix round after the probed commit (DEC-552, DEC-568).

## W1-02 follow-up, the root-search round (DEC-557, DEC-562, DEC-570, DEC-571; 2026-10-09)

Merged from `w1/W1-02` at `02f0294d` (2,762 cases in the suite; probed at `dc9fda16`, then one fix round, DEC-570). Built, for every role and for a session with no role: a search from the project root, or from a folder that carries a copy of either protected file, that gives no path below it and no glob is refused (the search tool and, in the shell, `grep -r`, `egrep`, `fgrep`, `rg`, `find`, `ls -R`), also with a numbered redirect after it, after a shell keyword, behind `timeout`, `command`, `env`, `nice`, `nohup` or `time`, and with a comment after it; a shell search whose name filter names or matches either file is refused; a NUL byte in a path or a command is refused; commands over 32,768 characters, file-tool paths and globs over 4,096 characters, a brace word that expands past 256 words and a call whose paths together hold more than 131,072 folders are refused. A search fed by a pipe or by a redirect of the standard input from a file reads no folder and is allowed.

**What a session writes now** (for the orchestration skill): a search from the project root always names a folder below it or a glob for the files meant (`path: src`, `glob: '*.py'`, `grep -rn <word> src tests`, `rg <word> src`, `find src …` or `find . -name …`, `ls -R src`); a type filter alone is not enough (`rg -t py <word>` is refused; `-g '*.py'` is the way). Inline JSON or scripts with many brace groups go into a file; no digit word stands directly before a redirect in a search.

**The harness's hook time limit** was not measured and this repository's configured limit is not known; by DEC-110 and DEC-179 a hook that passes its limit lets the call through. The rule's own decision stays under 0.4 s for every input the probe found slow.

**Residuals** (the suite's README carries them as 31 to 51):

- What a command-line guard cannot see: a search whose command, keyword, prefix or path is made at run time (a variable, a substitution, `eval`, an alias or a function); a brace word made past the bound by a variable or `eval`, and a sequence such as `{1..1000}`.
- Not built (DEC-570): `find` when any word of the command is a name test; valued options of `grep` and `rg` that the rule does not list are read as flags; a search in a brace group, in a shell started with `-c`, behind `xargs`, or with a substitution or a bare star as its path; `ls -R *`; `git grep` from the root; a file-tool path that is not text; `rg --type-list` is refused.
- Not held by a case either way: `sudo` as a prefix and options of a prefix (`timeout -s KILL 10 …`, `env -i …`, a prefix by its path); a brace word of 65 to 511 expansions that takes neither file in; further keywords and shapes (`case`, `select`, a subshell, `function`, `coproc`); further prefixes (`stdbuf`, `ionice`, `setsid`, `watch`, `strace`, `exec`, `builtin`); `zgrep` and `rgrep`; other numbered redirects (`2>|`, `&>`, `>&2`, `{fd}>`); a command that cannot be tokenised keeps its redirect number as a word; `rg` after a pipe with an assignment in front is taken as fed.
- Over-refusals kept on the safe side: a here-string or here-document feeding the search; a line of a here-document's body that reads as a root search (a commit message line beginning `ls -R` or `find .`; the way round is the file tool or other wording); a pipe continued on a new line; a search in a subshell after a pipe; `rg --version` followed by a pipe or after `cd`; any `find` from the root without a name test, `-maxdepth 1` and `-type d` included; `rg --files`; `rg <word> -m 5 < file`.
- `rg` as the first command with a standard input that is not a terminal may wait on it. Two matcher shapes stay at 0.3 s and 0.6 s. NUL in a search pattern or in written content is allowed.
- A project that holds neither protected file refuses no root search (with the owner as P-27). A very long path-like string in a field that is not a path makes the older held-out check take 40 s and more (with the owner as P-28).
- **Latency under load (DEC-372):** W1-05's p95 case failed for three tool forms in mid-round runs under load (216 to 245 ms) and passed in the final runs.
- **Acceptance tests rewritten after implementation began:** 18, reason "owner decision P-23" (the 14 ordered and 4 more built by the same W1-05 helper). **Added:** 665, 98 and 309 in three batches, each red first.

## W1-02 follow-up, the held-out check and the guard's deadline (DEC-573 to DEC-575, DEC-580, DEC-587; 2026-10-09)

Merged from `w1/W1-02` at `ae6d8a74` (2,917 cases in the suite; code head `60d1a4a8`, probed there; no fix after the probe). The last round of the guard in Wave 1 (DEC-577, DEC-584). Built after the root-search round above: a root search is refused only where a protected file, or a copy of one, lies under the search start (DEC-573, P-27 answered); `rg -t <type>` with no path stays refused (DEC-575); the held-out check resolves no string longer than the system path limit and keeps the literal check (DEC-574, P-28 answered; megabyte inputs that took 30 s and more are decided in a millisecond); the PreToolUse hook program keeps its own deadline of 20 seconds and denies when it reaches it (DEC-580: the decision runs in a forked process in a session of its own; about 4 to 10 ms are added to an ordinary call).

**What a session reads now** (for the orchestration skill): a guard decision that is not reached within 20 seconds is refused with a reason naming DEC-580. If a call gets that refusal, the fault is in the project (a hanging `git`, a pipe in the guard's bookkeeping folder, a very large tree), not in the call: report it, do not retry in a loop.

**Residuals** (the suite's README carries them as 52 to 62; all on the Wave 2 list by DEC-577 unless ordinary work produces one):

- **A read that gets through by a deliberate shape (probe finding 1):** one shell word longer than the path limit that the shell itself shortens, a brace list such as `cat <folder>/{a,b,…}` with some 900 alternatives and no literal held-out path, is allowed and reads a held-out folder. The same word under the limit is refused. Wider than residual 52 (a program that shortens a long string before opening): no helper is needed. The Wave 2 entry is a textual shortening and brace expansion before the skip.
- The held-out check otherwise: `=`, `:` and `,` do not separate Bash words (53); in a non-Bash field a reaching path on a later line is not refused (54); an edit of one of the two files is not looked at beyond its path (55); a denied write of the held-out file carries that file's place in its reason (56); many under-limit strings in one input are not held beyond the named cases (57); the path limit has no lower bound of the guard's own (Linux reports 4096; nothing a worker writes moves it); no case either way for a NUL byte in an edit's path (a hook error, exit 2), a home folder of one character, or variables other than the home variable in a Bash word.
- The deadline: a refusal at the deadline records no finding (58; Wave 2: one guard finding per deadline refusal); a named pipe in the hook's bookkeeping folder refuses every call of that project after 20 seconds until it is removed, where it failed open before (59); one bookkeeping program start that passes its own 10 seconds ends in an allow with a finding (60); the hook starts `git` by name and the freeze look-up has no limit of its own (61); a program the decision starts that puts itself in a session of its own escapes the kill, and one that keeps the pipes open after an in-time decision is left running; the harness ending the hook orphans the forked decision; the hook needs `os.fork`; a hook started with the child signal ignored refuses every call (fails closed; the harness does not start it so); failures of the waiting process leave findings without session and tool name.
- **The other hook programs keep no deadline (62, the lead's package DP-12):** the programs after a tool call cannot refuse a call that has run; what the harness does at their limit was not observed. Wave 2 list, an experiment first (DEC-587).
- The `gov doctor` check that the configured hook limit is above the guard's deadline: Wave 2 list (DEC-580).
- **Launched sessions:** the Write tool and `rm` are refused under the runtime folder's scratch to a launched engineer by the session's permissions; engineers proved their candidate guard files in the session scratchpad.
- **A worker's incomplete save of a guard file stops every session of that worktree** (run 6: a function got a required argument and its callers did not; the guard failed closed; repaired from outside with `git checkout`). The rule given to engineers since: prove the whole new file outside the tree, one save, `git status --short` as the first call after it.
- **Latency under load (DEC-372):** W1-05's p95 cases failed in run 7's serial run at a machine load above 20 and passed alone; W1-46's shared live session gave 23 setup errors in a parallel run and passed alone.
- **Acceptance tests rewritten after implementation began:** none in runs 5 to 8. **Added:** the eighth batch (129 cases) and the ninth (26 cases), each red first.

## W1-02 closed after its last round (2026-10-09; for the exit auditor)

`gov close DAEO-emkd` on the merge (`b40adb4d`, check commit `f01d4b62`) refused, as every close does until this repository's adoption (DEC-522); the output is kept by the orchestrator. Closed with the ticket tool under DEC-492, DEC-505, DEC-516, DEC-522, DEC-536 and DEC-587:

- **Tests:** 8,870 passed, 2 failed, 29 skipped. Both failed while another lead's full run loaded the machine (load 17 to 45) and pass alone and in a parallel run of their suite: W1-05's 100 ms p95 case for `NotebookEdit-engineer` (DEC-372), and `tests/acceptance/W1-30/test_w1_30_r8_test_runs.py::test_a_ticket_whose_only_acceptance_test_is_skipped_refuses`, which had not failed before; the close keeps no failure text for it. **For the exit auditor:** that case is not a latency case by name; its inner `gov close` run has time limits that a loaded machine can pass.
- **Red checks:** the thirteen of the baseline. `core-schema` stands at 35 here (two new probe records, four findings each, until the probe type arrives with the follow-up after W1-41); `product-traceability-trailers` at 961 (W1-41's closing); `secrets-indexing` timed out at 60 seconds (DEC-591).
- **Probe gate:** the orchestrator's residual commit `7cd892ca` after the probed commit (DEC-505; no longer a finding once DEC-581 is merged).
- **Containment and trailers:** `cd233578`, `7d9ab30e`, `15a0dbc4`, `56f1476d`, `d6bb6d5a`, `478a8ed0` and the four commits before DEC-476 that name no task: all as at this ticket's earlier close.
- **Context:** blocked on an outside source (`G-01`), as before.

## W1-30 follow-up after W1-41 (DEC-569, DEC-572, DEC-579 to DEC-581, DEC-586, DEC-588, DEC-592; 2026-10-09)

Merged from `w1/W1-30` at `83d11b2d` (three runs of a lead since `e12df900`; probed at `83d11b2d`, no fix round, DEC-592). Built: `gov close` calls the cost counter; the probe gate refuses only for commits after the probed one that change the ticket's `allowed_paths`, its acceptance folder or its own file, and a merge that brings exactly the probed code is not "after" (DEC-581); the READY rule holds a ticket whose constraining package the store could not load (DEC-544); the records query returns a register entry's heading and title; a register named in the path map and absent from the commit refuses the load; `gov check` and the schema check read an installed kernel too; the probe record type; `lock` as a module command; containment lifts a merge commit's ticket file that equals one parent's version when every commit that brought it passes (DEC-572); the kernel template's settings carry `"timeout": 60` on its three guard hook entries (DEC-580). `trailers_base` is written into the path map with this merge (DEC-482).

**What the orchestrator does now** (for the orchestration skill): probe the ticket branch's final head, after its last merge of the integration branch, and merge that head directly; commit residual notes, the probe record, register entries and checkpoints after it freely (they no longer refuse); do not edit a ticket file on the integration branch while that ticket's branch is open (DEC-588); run `gov rebuild` once after this merge (a store built before it has no register-entries table).

**Residuals** (Wave 2 list unless stated):

- **With the owner:** the limit of 60 seconds is not in the template's rulesync hooks source, so a project's generated harness settings do not carry it, and that source has no entry for a failed tool call (P-34); a commit that names another ticket and changes this ticket's paths after the probe is not judged by the gate (P-35).
- **Probe gate (probe findings):** a merge of the integration branch into the ticket branch after the probe, merged back, refuses (fails closed; this repository's history has the shape twice); a `Task:` trailer with unusual spacing makes a later commit of the ticket escape the gate and the work-without-task check (`src/gov/close/repo.py` finds the ticket's commits by fixed text); a merge of the probed commit that drops or replaces probed code by a hand-resolved conflict passes; `allowed_paths` written twice in a ticket file is the union for the guard and the last block for the close; the gate asks only that the probed commit is a full id and an ancestor of HEAD; a commit that names no task is judged by `allowed_paths` alone; a test designer's commit into another ticket's acceptance folder after the probe has no gate.
- **`gov check` in a project with the installed layout only** is red until its checks can be measured (an empty lexical index, no tickets in the store, the dev tiers not configured), where it ran nothing before; watched in W1-42's exit run. No kernel folder gives no declarations and no refusal; an installed `checks` path that is a file is skipped; one id declared twice inside one layout runs both; file order in the merged list, a schema in one layout only and `allows-not-applicable` in an installed project are not pinned. An absent or unreadable schema is a finding only for the probe type.
- **Containment (DEC-572):** a clean combination of a ticket file stays a finding (DEC-588; `803f731c`); a commit with no trailers that brought the version is judged as the orchestrator's; an owner's commit that brought the version keeps the merge a finding; merges with more than two parents, a ticket file absent from the merge, and which failing commit the reason names are not pinned; the 1000-process bound is held by a unit case only.
- **READY rule and store:** a Markdown file that opens with an unclosed `---` holds every ticket; the key written `Constrains:` gives READY; a ticket held because the store cannot be read carries an empty reason list; no edge from `Amends`, `Refines`, `Under` or a partial supersession; the context hashes the whole register per decision; whether a refused load leaves the earlier store readable; the external list's other id forms; a never-built index says nothing under `dropped`; lower-case status words still satisfy.
- **The close:** its "stated result" check can be satisfied by a printed line; the plugin stand-in check covers the root and `src/` only; the repair-ticket cut counts findings only and `findings_cut` is never set; the counter catches two error types only; `gov status` reads the loader directly; `gov retrieve` maps the register's path to one id; no case holds `SCHEMA_UNREADABLE`, the probe-only shape check, or the code tool's session limits.
- **The template's settings** wire three hook programs; its hooks folder holds four more (compaction, session start, stop, subagent stop) that it does not register.
- **The `secrets-indexing` check** times out at 60 seconds, on a loaded machine and once at a load of 2.5 (DEC-591: measured on a quiet machine before W1-42).
- **Under load (DEC-372):** four parameters of `tests/unit/close/test_measured.py::test_options_of_the_callers_environment_do_not_reach_the_run`, three cases of `tests/unit/close/test_run_and_record.py` and W1-47's `test_the_builder_tests_of_the_guard_pass` failed in the lead's full run at a load of 17 to 45 and pass alone (their inner runs passed 60 s and 300 s limits).
- **Small:** W1-30's README says "30 s" in older rounds; W1-47's README header says 970 cases; a docstring of W1-09 names an old package; the W1-21 retrieval-check case was never seen red; the narrowed W1-16 case has a name-only blind spot; worker slips (an edit by `sed -i`, a script fed by a here-document that the guard did not refuse).
- **Learning metrics:** 330 acceptance cases added over the follow-up, each before its engineer; rewritten before implementation with a reason: the fixtures of DEC-579, one W1-50 case (DEC-572), one W1-30 case (owner decision P-30); none after. `src` +894 −170 and `template` +73 −6 against an estimate of 220.

## W1-30 closed after the follow-up after W1-41 (2026-10-10; for the exit auditor)

**The escalation path, as it ran.** The first `gov close DAEO-2lwj` on the merge (`caa8ac5c`) answered `ESCALATION_BLOCKED` at once (exit code 4, nothing ran): the ticket's refused closes, each refused on this repository's baseline before adoption, had reached three and an escalation was in force. The owner lifted it the built way (P-36 a): the operator committed the register entry DEC-593 with `Role: owner` as the commit's only role (`700bb5b5`), and `gov close DAEO-2lwj --owner-decision DEC-593` then ran whole. The escalation file names `lifted_by: DEC-593`, the counter restarted, and DEC-593 is recorded as used. The path worked as built.

That close refused, as every close does until adoption (DEC-522); its output is kept by the orchestrator. Closed with the ticket tool under DEC-492, DEC-505, DEC-516, DEC-519, DEC-522, DEC-536, DEC-592 and DEC-594:

- **Tests:** the ticket's acceptance run 425 passed; the regression 11,739 passed, 1 failed, 29 skipped. The failed case, `tests/unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it`, passes alone (a time-limit case in the parallel run). The orchestrator's direct regression on the same merge, in the close's form, was green (11,903 passed; 262 serial-only passed).
- **Probe gate:** "ticket commit `caa8ac5c` changes `src/gov/check/commands.py` after the probed commit". The merge holds that file exactly as the probed commit `83d11b2d` does. The ticket has three probe records (its first build, its earlier follow-up, this follow-up) and the gate asks every record everything and ends at its first finding: against an earlier round's probed commit, this round's merge is a later change. **Residual (Wave 2 list): a reopened FULL ticket with an earlier probe record always refuses at the probe gate.** What the gate answers for this round's record alone was not measured by the close.
- **Red checks:** the thirteen of the baseline; `core-schema` 11; `product-traceability-trailers` 294 with the base of DEC-482 in the path map; `secrets-indexing` timed out (the round of DEC-595).
- **Work without a task:** `7674efde`, `478a8ed0` as before, and `e0572d12` (a W1-36 commit of 2026-10-06 without trailers, now inside this ticket's widened paths).
- **Trailers:** 22 commits of the ticket lack `Implements:` (before DEC-476, and the named ones). **Containment:** `29af0646`, `148f7584` (merges, a W1-07 support file), as at this ticket's earlier close.
- **Checkpoint stale; context blocked** on a capability record not in the store (adoption brings them).
- **Repair ticket** `DAEO-fknh` opened by the refused close: not committed, kept by the orchestrator.
