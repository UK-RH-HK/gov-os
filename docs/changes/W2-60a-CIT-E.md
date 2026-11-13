---
id: W2-60a-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-29
branch: w2/W2-60a
base: a1629f1860ca
ticket: DAEO-cv58 (W2-60a)
author: engineer (DAEO-cv58), design batch; engineer (DAEO-cv58), implementation batch 1, with the lead's corrections; engineer (DAEO-cv58), round 2
decisions_recorded: [DEC-826, DEC-838, DEC-839, DEC-832, DEC-786, DEC-801, DEC-802, DEC-941]
state_class: EVIDENCE
---

# W2-60a: change-execution design (CIT-E), before any code

The design of W2-60a (DAEO-cv58): `gov launch` starts a worker as its role, with the role's text, its skills and its
default model and effort, sets no compaction threshold, keeps connectors, user-level agents and skills, and
model-side memory out, and writes one launch record before the session starts (DEC-826 Q1 and Q5, DEC-838, DEC-839,
DEC-832 item 1). Status **APPLIED**: the code exists (implementation batch 1, §1), with the lead's corrections
after the lead's follow-up measurements (Behaviour 8, P-W2-60a-2; probe part 2b), round 2's changes (§2) and
round 3's (§3).

## 1. The changes

| # | File | Change | Evidence |
|---|---|---|---|
| 1 | `src/gov/launch/role.py` (new) | The role file `template/governance/kernel/roles/<role>.md` read once: its version line, default line and skills line, each found by the line's head, required once, whole and of its form (Behaviour 3, D); the skills folder `.claude/skills/` read, each folder with a `SKILL.md` described from that copy (name, path, version or `no version`, sha256, folder sha256, named), a link, an unreadable file or a front matter that is not a YAML map refused; each named skill at `.claude/skills/<name>/SKILL.md` with a version; the text appended composed (the role file's bytes, then each named `SKILL.md`, in the order named). | `tests/unit/launch/test_role.py` (21 cases); acceptance `test_w2_60a_role_text.py`, `test_w2_60a_skills.py`, `test_w2_60a_model_and_effort.py` |
| 2 | `src/gov/launch/record.py` (new) | The record folder `.gov-runtime/launches/` of the main checkout, found from `.git` with `gov.guard.runs.common_dir` (unchanged), made when missing, refused when `.git` gives no common directory, the common directory is not named `.git`, or a part is a link or not a folder; its two literal `Edit` deny rules; the CLI's version from its link's target; the original's record of a resume, required and of this role and ticket; the record written exclusively (`O_EXCL`, `O_NOFOLLOW`), flushed, a partly written file removed; the record removed when the CLI cannot be started. | `tests/unit/launch/test_launch_record.py` (9 cases); acceptance `test_w2_60a_launch_record.py` |
| 3 | `src/gov/launch/launcher.py` | At Section B's places only: the module's text; imports (`time`, `uuid`, the two modules); constants (the launcher's own switches, the arguments of Behaviour 7, the compaction names); in `_check_repository_settings`, an `agent` key, `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW`, a top-level `autoCompactWindow` or an `env` that is not a map refused; `_check_own_args` (new, after `_check_cli_args`, which is unchanged) and its call; after the sandbox faults the role read, the model after `--` compared, the record folder and its deny rules, the resume's original record; after the temp folder's env, `CLAUDE_CODE_SUBAGENT_MODEL` and `autoMemoryEnabled`; inside `if not state["ended"]:` `role-<role>.md`, the session id and the record; the start's argument list (`cwd=root, env=env` untouched); the record removed before the refusal of a CLI that cannot be started. `build_settings`, `_runtime_rules`, `_tree_rules`, `sandbox_faults` and the git-environment lines are as they were. | acceptance `tests/acceptance/W2-60a/` (151 of 152 not `local_only`; the one red is W2-56's, below) |
| 4 | `docs/research/W2-60-rules-probe.md` | The lead's part 2b (k1, f1, f2) and the opening's count (18 sessions, about USD 2.32). | the lead's scratch record |
| 5 | this note | Status, this table, Behaviour 1's tools, 4's residual, 6's `autoCompactWindow`, 8 as the lead corrected it, 10's steps 4 and 8, P-W2-60a-2. | — |
| 6 | `src/gov/launch/role.py` (round 2) | The command files under `.claude/commands/` described as skills (Behaviour 2): `<name>.md` as `<name>`, `<namespace>/<name>.md` as `<namespace>:<name>`, the same keys as a skill folder's entry, after them in path order; a link (the folder, a namespace folder or a file) or a front matter that is not a YAML map refused. The user settings file's `permissions.ask` and `permissions.deny` read (Behaviour 4), nothing else of it; a file that cannot be read or is not of that shape refused, an absent one carries nothing. | `tests/unit/launch/test_role.py` (45 cases); acceptance `test_w2_60a_command_skills.py`, `test_w2_60a_user_permissions.py` |
| 7 | `src/gov/launch/launcher.py` (round 2) | `SET_ITSELF` gains `--fallback-model`, `--chrome`, `--ide`, `--system-prompt-snapshot` (Behaviour 7); `_check_repository_settings` refuses `env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `env.CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`, `modelSettings.<model>.autoCompactWindow`, and a `modelSettings` that is not a map of maps (Behaviour 6); after the role read, the user's rules read; beside `autoMemoryEnabled`, the user's deny rules added after the launcher's and the user's ask rules set as `permissions.ask` (Behaviour 4). `_check_cli_args`, `build_settings` and the `env=` of the start unchanged. | acceptance `tests/acceptance/W2-60a/` (200 of 201 not `local_only`; the one red is W2-56's, below) |
| 8 | this note (round 2) | Behaviours 2, 4, 6, 7, 9 and 10 for round 2's changes; §2; this table. | — |

**The red that stays** (Section B, "two edges"): `test_w2_60a_no_compaction_threshold.py::test_a_compaction_threshold_in_the_caller_s_environment_does_not_reach_the_session`,
a caller's `CLAUDE_CODE_AUTO_COMPACT_WINDOW` reaching the session's process environment: W2-56's cleaned environment;
the `env=` of the start is not edited here.

- **Sections A** state only what is seen from outside, for the independent test designer (DEC-462): they name no
  function, module or internal name of the code to be written.
- **Section B** places the work in `launcher.py` beside W2-56 (DEC-786); C lists the existing tests the change
  touches; D is what W2-11 must write; E the open points.
- **The facts it rests on** are the lead's measurements in `docs/research/W2-60-rules-probe.md` (CLI 2.1.292),
  cited by session name (w1, r2, x2, c1 …), and the CLI's own `--help` (2.1.292).

## 2. Round 2 (review 1)

Review 1 found two gaps, and the round takes two ride-alongs with them (DEC-802: small, same files, same kind):

- **F1, the command files:** the session also loads each Markdown file under `.claude/commands/` as a skill, and the
  record listed only `.claude/skills/`, so it did not say all the session may load (KPI line 2). The record now holds
  one entry per command file, from that file (Behaviour 2).
- **F2, the user's protections:** `--setting-sources project,local` drops the user settings file, and with it the
  user's `ask` and `deny` rules, so a launched session ran with fewer protections than the caller's own. Those two
  lists are now carried into the `--settings` value, and nothing else of the file (Behaviour 4).
- **Ride-along 1:** three more spellings of a compaction threshold in the repository's settings are refused
  (Behaviour 6).
- **Ride-along 2:** four more arguments are refused after `--`: a fallback model, two connectors, a prompt
  snapshot (Behaviour 7).

Every refusal of round 1 still refuses with its message; round 2's run after them in the same step (Behaviour 10).

## 3. Round 3 (review 2, DEC-951)

The last round, under DEC-413's exception (DEC-951 item 4), strictly two items:

- **F1, the main checkout's local file:** CLI 2.1.292 loads a linked worktree session's local settings from the
  main checkout's `.claude/settings.local.json`, not the worktree's own, and the CLI's `/add-dir` ("remember this
  directory") writes `permissions.additionalDirectories` there in ordinary work. A worktree's launch now judges that
  file too, with every refusal the tree's own copy gets; a main checkout that cannot be found refuses (Behaviour 6,
  Behaviour 10 step 4). `record.py`'s look-up is factored into `main_checkout`, which the record's folder and the
  check share; the record folder's messages are unchanged.
- **P-W2-60a-4 (a), the adopted layout:** a tree with no `template/` reads its role file from
  `governance/kernel/roles/<role>.md` (Behaviour 1). Where `template/` exists, nothing changes; the "both with
  different role files" refusal of option (a) is not taken (DEC-951 item 4 scopes the round to the path).

| # | File | Change | Evidence |
|---|---|---|---|
| 9 | `src/gov/launch/record.py` | `main_checkout(root, what)` factored out of `folder`; `folder` calls it. | `tests/unit/launch/test_launch_record.py` |
| 10 | `src/gov/launch/launcher.py` | `_check_repository_settings` adds the main checkout's local file for a linked worktree; the loop judges each file as before. | the same |
| 11 | `src/gov/launch/role.py` | `ADOPTED_ROLES_REL`; the role file's folder chosen by whether `template` exists. | `tests/unit/launch/test_role.py` |
| 12 | `src/gov/launch/role.py` (after the `w2/integrate` merge) | A skill's or command's version is its top-level `version`, else `metadata.version` when `metadata` is a map (the kernel's generated copies carry it there); neither is `no version`, and a named skill with neither still refuses (S2). | `tests/unit/launch/test_role.py`; acceptance `test_w2_60a_skills.py` |
| 13 | `src/gov/launch/role.py`, `launcher.py` | `gov launch --plan` (routed from W2-33 S2, DEC-1156 (3); DEC-1167 (2)): `launch_default` reads the default line alone, from `read_role`'s file with its refusals; `launcher.plan` checks the role and the ticket as a launch does, prints the line and starts nothing. | `tests/unit/launch/test_role.py` |
| 14 | `src/gov/launch/command.py` (P-6 (a)) | The `--plan` flag (`store_true`, in the usage line); `run` returns `launcher.plan(root, role, ticket)` when it is set, else launches as before. `gov launch --plan <role> <ticket>` prints the one line `model <id>, effort <e>` and exits 0, starting nothing (no session, CLI run, launch record or gate); a role file without the default line, or with a malformed one, refuses with `LAUNCH_REFUSED` naming its path and exits 1. `Launch by criticality` is not read. | `tests/unit/launch/test_role.py` (through `gov.cli.main`); a fixture project run with `python3 -m gov.cli.main launch --plan` |

## A. Behaviour

### Behaviour: the line the session is started with

When every check passes (order in Behaviour 10), `gov launch <role> <ticket> [-- <args>]` starts, in the tree's
root:

```
~/.local/bin/claude --settings <json> --setting-sources project,local --strict-mcp-config
    [--model <the role's model>] [--effort <the role's effort>] --session-id <a new UUID>
    --append-system-prompt-file <the session's temp folder>/role-<role>.md [--fork-session]
    <every argument given after --, unchanged and in its order>
```

- `--model` is put on the line only when the arguments after `--` carry none; `--effort` likewise. Either is then
  passed once: the caller's copy where the caller put it, or the launcher's.
- `--fork-session` only on a resumed launch (Behaviour 8).
- The `--settings` value is today's (the `env` with `GOV_ROLE`, `GOV_TICKET`, `TMPDIR`, `CLAUDE_CODE_TMPDIR`; the
  deny rules; the sandbox block) with these additions: `env.CLAUDE_CODE_SUBAGENT_MODEL` set to the session's model;
  the key `"autoMemoryEnabled": false`; two deny rules naming the launch record's folder literally,
  `Edit(/<folder>)` and `Edit(/<folder>/**)` (Behaviour 9); the user settings file's deny rules after the
  launcher's, and its ask rules as `permissions.ask` (Behaviour 4). It holds no `CLAUDE_CODE_AUTO_COMPACT_WINDOW`.
- The launcher writes nothing new to stdout or stderr.

### Behaviour: the plan, `gov launch --plan <role> <ticket>`

- It prints one line, `model <id>, effort <e>`, from the role file's `- **Launch default:**` line (Behaviour 1's
  file; no `Launch by criticality` line is read), and exits 0. It starts nothing: no session, no CLI run, no launch
  record, no temp folder, no gate.
- A role that is not a worker role, a ticket a launch refuses, a role file that cannot be read, or one without that
  line once, whole and of its form, refuses with `LAUNCH_REFUSED`, naming the role file's path when the refusal is
  the role file's, and the same exit code as a launch's refusal; nothing is printed on stdout.

### Behaviour 1: the role's text

- **Read from** the role file `template/governance/kernel/roles/<role>.md` of the tree the session starts in; in a
  tree with no `template/` (an adopted repository, DEC-487), from `governance/kernel/roles/<role>.md` (round 3,
  P-W2-60a-4 (a)). Anything named `template` keeps the template path, so its absence alone selects the adopted one;
  neither file refuses, naming the path looked for. The record's path and hash and the text appended are the file
  read. The generated agent `.claude/agents/<role>.md` is not the session's own text: it stays what it is today, a subagent
  type the session may start (governed by the guard, DEC-113).
- **How it reaches the session:** appended to the CLI's default system prompt with `--append-system-prompt-file`.
  The launcher writes the role file's bytes (then the named skills', Behaviour 2) into `role-<role>.md` in the
  session's own temp folder and names that file on the line; the folder and the file go when the session ends
  (DEC-386). So the copy the session loads is the role file as the launcher read it at launch, and the record's
  path, version and hash are that file's (Behaviour 9).
- **Why not `--agent <role>`.** Both routes put the role's text at the start (probe r1, r2). `--agent` was refused
  for three measured reasons:
  - it replaces the CLI's default system prompt (start 6,293 tokens against 25,976; r1, r3), which every worker so
    far has run with: a change of behaviour no measurement covers;
  - it narrows the session's tools to the agent's `tools:` list (r1). The generated agents list `Read`, `Write`,
    `Edit`, `Bash`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, and neither `Skill` nor `Task`, so a worker could not
    load a skill on request or start a subagent;
  - the text appended is the role file itself, the copy that carries the version and the default line (D), rather
    than a generated copy that rulesync writes from it.
  The saving of about 19,700 tokens a start is forgone; it is not this ticket's to take.
- **The tools a worker is given are unchanged.** With the default prompt kept, the session has the CLI's default
  tools, as today. `--allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob"`, as the leads pass it, still says
  which tools run without asking. A skill the role names is in the start's text and needs no tool. A skill loaded
  on request goes through the CLI's `Skill` tool, which that list does not name; a `-p` worker loads a project
  skill on request without it (probe k1), so the leads' form needs no `Skill`.
- `CLAUDE.md` and the guard hooks still apply (r4; the project setting source is kept).

### Behaviour 2: the skills

- **The skills the session can load** are the project's generated copies: each folder directly under
  `.claude/skills/` of the tree that holds a `SKILL.md`. The CLI loads all of them and has no switch that narrows
  them to some (`--disable-slash-commands` removes every skill; probe part 2, "What stays"). Each is recorded, from
  that copy: its name (the front matter's `name`, else the folder's), its path, its version (the front matter's
  `version` as written, else the words `no version`, as `gov close` writes it), the sha256 of its `SKILL.md`, the
  sha256 of its folder (each regular file's path and sha256, in path order), and whether the role names it.
- **The command files are skills too** (round 2, F1): the CLI loads each Markdown file under `.claude/commands/` as
  a skill, `<name>.md` as `<name>` and `<namespace>/<name>.md` as `<namespace>:<name>`. Each is recorded from that
  file with the same keys, after the skill folders' entries, in path order: its name from its path (not the front
  matter), its path, its version (the front matter's `version`, else `no version`), the sha256 of the file, as
  `folder_sha256` the same sha256 (the file is the whole command), and `named: false`. Files not ending in `.md` are
  not loaded and not recorded. An absent `.claude/commands/` adds nothing.
- **A role file names its skills** in one line (form in D): `- **Skills:** <name>, <name>`. No line names none.
  Each named skill must be at `.claude/skills/<name>/SKILL.md` and must carry a `version` in its front matter; its
  `SKILL.md` text is appended after the role's text in `role-<role>.md`, in the order named, so it is in the
  session's context at its start (DEC-832 item 1: method text the engineer loads at launch). When W2-33 writes its
  packs into the kernel, generates them into `.claude/skills/` and names them in the engineer's role file, they load
  with no code change.
- **Refused:** a named skill that is missing, unreadable or without a version; a skills line that is malformed;
  any skill folder of `.claude/skills/` that is a link or holds one, or whose `SKILL.md` cannot be read or has a
  front matter that is not YAML (the record could not say what the session may load). An absent `.claude/skills/`
  is an empty list, not a refusal, unless the role names a skill. The same for the commands: a `.claude/commands/`,
  a namespace folder or a command file that is a link, a file that cannot be read, or a front matter that is not a
  YAML map refuses the launch.
- **A role names only skill folders:** a command file is never a named skill; a skills line naming a command's name
  is refused as a skill not at `.claude/skills/<name>/SKILL.md`.
- **Today's loaded copies carry no version** (lens E F15; all 18 under `.claude/skills/` at the base): their record
  says `no version`, and the hashes identify the text. No fallback reads the kernel's copy instead. A named skill
  needs a version in the loaded copy: a requirement on W2-11 (one versioned source per skill, DEC-832 item 2; D).
- **The CLI's built-ins** (19 skills, 5 agents, 3 plugins; probe part 2, "What stays") are the CLI's own, not
  user-level, and no switch removes them alone. They are not passed silently: they are named in package
  P-W2-60a-1 and identified in the record by the CLI's version.

### Behaviour 3: the default line, and the model and effort

- **The line,** read from the same role file as Behaviour 1, exactly once, as a whole line:

  ```
  - **Launch default:** model <model>, effort <effort>
  ```

  `<model>` is a full model id: `claude-` then one or more groups of lower-case letters and digits joined by `-`
  (no alias such as `opus`). `<effort>` is one of `low`, `medium`, `high`, `xhigh`, `max` (the CLI's `--effort`
  values). One space after each `:` and `,`; nothing before the `-` or after `<effort>`; no third field, so it
  cannot carry a compaction threshold (DEC-839 item 5, DEC-838). The lines at DEC-839's values:

  | Role file | Line |
  |---|---|
  | `engineer.md` | `- **Launch default:** model claude-opus-5-5, effort high` |
  | `independent-test-designer.md` | `- **Launch default:** model claude-opus-5-5, effort high` |
  | `research.md` | `- **Launch default:** model claude-opus-5-5, effort high` |
  | `product-spec.md` | `- **Launch default:** model claude-opus-5-5, effort high` |
  | `independent-auditor.md` | `- **Launch default:** model claude-opus-5-5, effort max` |

  (`orchestrator.md` may carry `effort high` for W2-21; `gov launch` does not start the orchestrator.)
- **Missing:** no line of the file begins with `- **Launch default:**`. **Malformed:** a line begins with it and is
  not of the form above, or two lines begin with it. Either refuses the launch, naming the file and the form.
- **Applied:** the role's model and effort go on the line (`--model`, `--effort`) unless given after `--`.
- **An effort after `--`** (`--effort <e>` or `--effort=<e>`, `<e>` one of the five) is applied and recorded as the
  launch's own (`effort_source: "after --"`); it may differ from the default (a FULL ticket's test designer at
  `xhigh`, DEC-839 item 2). An unknown value, a missing value or a second `--effort` is refused.
- **A model after `--`** (`--model <m>` or `--model=<m>`) that is not the role's, compared as written, is refused,
  naming both. The role's own is accepted and passed once, where the caller put it (`model_source: "after --"`).
  A missing value or a second `--model` is refused.

### Behaviour 4: what is kept out

| Kept out | Switch (measured) | Where | The session's start then shows |
|---|---|---|---|
| Connectors (claude.ai's and any `.mcp.json`) | `--strict-mcp-config`, with no `--mcp-config` (w1) | the CLI line | no `mcp__` tool, no connector (w1, c1) |
| User-level agents and skills | `--setting-sources project,local` (w3) | the CLI line | no user-level agent or skill; the project's hooks, agents and skills stay (w3, c1) |
| Model-side memory | `"autoMemoryEnabled": false` (w4) | the `--settings` value | no `memory_paths` (w4, c1) |

- `--setting-sources` stays refused after `--` with today's message: the launcher's own line carries it (the "two
  edges" rule, B). The project and local sources are kept, so the guard's hooks stay wired.
- Dropping the user's settings file also drops what it sets for every session on the machine: `effortLevel` and
  the env `CLAUDE_CODE_SUBAGENT_MODEL` (probe part 2, "Also seen"), and the user's `model`, permissions (but for
  the ask and deny rules, kept below) and hooks.
  The launcher sets model, effort and subagent model itself, so a launched session's values come from the
  repository alone (lens F recommendation 1).
- **The user's ask and deny rules are kept** (round 2, F2). Dropping the user settings file must not take a
  protection away, so the launcher reads `~/.claude/settings.json` and carries its `permissions.ask` and
  `permissions.deny` into the `--settings` value: the deny rules after the launcher's own (no rule twice), the ask
  rules as `permissions.ask`. Nothing else of the file is carried: never an `allow` rule, a `defaultMode`, a model,
  an env or a hook, each of which could only add to what the session may do or change what it is. An absent file
  carries nothing. Refused: a file that cannot be read (a folder, no read permission), that is not JSON or not a
  map, whose `permissions` is not a map, or whose `ask` or `deny` is not a list of strings (it could not be shown to
  keep its rules).
- `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` (w5) is a process-environment switch, W2-56's environment; the settings key
  is used instead.
- **No switch known:** the CLI's built-ins (P-W2-60a-1); user-level `CLAUDE.md` and rules, not measured under
  `--setting-sources project,local`, a named residual (P-W2-60a-2; probe part 2b). Named there, not passed silently.

### Behaviour 5: the subagent model

`CLAUDE_CODE_SUBAGENT_MODEL` in the settings' `env` is set to the session's model (the role's, since another is
refused), and recorded as `subagent_model` (DEC-839 item 3, lens E F14, lens F recommendation 7). A value in the
caller's process environment does not reach the settings; whether it reaches the process falls on W2-56's cleaned
environment (B, "two edges").

### Behaviour 6: no compaction threshold

- No `--autocompact` on the launcher's line; no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in the settings' `env`.
- Refused after `--`: `--autocompact <v>` and `--autocompact=<v>`.
- Refused in the repository's settings: `.claude/settings.json` or `.claude/settings.local.json` whose `env` holds
  `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, or that sets the top-level key `autoCompactWindow` (the CLI would apply either
  to the session), or whose `env` is not a map (it could not be shown to hold neither). Round 2 adds the other
  spellings the CLI takes: `env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `env.CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`, and
  `modelSettings.<model>.autoCompactWindow` for any model, the role's or another; a `modelSettings` that is not a
  map, or holds a value that is not a map, is refused too (it could not be shown to hold none).
- **A worktree's launch also judges the main checkout's `.claude/settings.local.json`** (round 3, review 2's F1):
  the CLI loads a linked worktree's local settings from there. Every refusal of Behaviour 10 step 4 applies to it
  as to the tree's own copy (the guard-wiring requirement stays on the tree's own `.claude/settings.json`), and the
  message names the file by its full path. The main checkout is found as the record's folder is (Behaviour 9): a
  `.git` that cannot be read, gives no common directory or a bare one refuses; a main checkout with no local file
  adds nothing; a launch from the main checkout checks its own file once, as before. A link there is judged as the
  tree's own is: the file the link leads to is read, and a link that leads nowhere cannot be read and refuses; no
  new link rule.
- The record states `"compaction_threshold": "none"` (DEC-838 items 1 and 2).
- The process environment's copy (a parent's `CLAUDE_CODE_AUTO_COMPACT_WINDOW`) falls on W2-56's cleaned
  environment: this ticket does not change what process environment the session is started with.

### Behaviour 7: the arguments the launcher now sets itself, refused after `--`

Each is judged word by word, as today (a prompt that only names one as a word passes):

| Refused | Spellings | Substance of the message |
|---|---|---|
| `--agent` | `--agent <a>`, `--agent=<a>` | the launcher starts the session as its role, with the role file's text appended (DEC-826 Q1) |
| `--append-system-prompt` | spaced, `=` | the launcher appends the role's text itself (DEC-826 Q1) |
| `--append-system-prompt-file` | spaced, `=` | the same |
| `--session-id` | spaced, `=` | the launcher gives the session its id and keys the launch record by it |
| `--fork-session` | as given | the launcher forks a resumed session itself, so that it has an id of its own |
| `--model` not the role's | spaced, `=` | names the model given and the role's (DEC-839 item 1) |
| `--model`, `--effort` without a value or twice; `--effort` not one of the five | spaced, `=` | names the argument and the rule |
| `--autocompact` | spaced, `=` | no launch sets a compaction threshold (DEC-838) |
| `--fallback-model` (round 2) | spaced, `=` | the session runs on the role's model alone, never on another (DEC-839 item 1) |
| `--chrome`, `--ide` (round 2) | as given, `=` | a launched session loads no connector, and these run outside the sandbox (DEC-826 Q5); `--no-chrome` passes |
| `--system-prompt-snapshot` (round 2) | spaced, `=` | the session's prompt is the CLI's default with the role's text appended (DEC-826 Q1) |
| `--continue`, `-c`, a short-option word holding `c` (`-pc`) | as given | a launch resumes a session by its id (`--resume <session id>`), so that the record can name it |
| `--resume`/`-r` without a UUID, or twice; a resume spelled otherwise (`-r<id>`, a short-option word holding `r`) | as given | the same |

Each message begins as today's: `LAUNCH_REFUSED`, "the CLI arguments carry …".

### Behaviour 8: resume

- The leads resume a worker with `--resume <session id>` (or `--resume=<id>`, `-r <id>`) after `--`; the id must be
  a UUID. The CLI refuses `--session-id` with `--resume` unless `--fork-session` is given (x1), and runs with it
  (x2). So a resumed launch is started with `--session-id <a new UUID> --fork-session`, and the passed `--resume
  <id>` unchanged: the session continues the conversation under an id of its own.
- **Measured (probe f2, after this note's design):** a resumed, forked session keeps the original session's system
  prompt and does not take the text appended at the resume.
- **Its record** is a new one, keyed by the new id, with `"resumes": "<the id given>"`; the resumed session's own
  record is never touched. A fresh launch has `"resumes": null`. **Its `role_text`, `appended_sha256` and `skills`
  are the original launch's, taken from the original's launch record** (the text the session has); its model,
  effort, sources, start time and CLI are this launch's.
- **Refused:** a resume when no launch record exists for the id given, or the original's record cannot be read or
  is not of the record's form, or its role or ticket is not this launch's; a second `--resume`.
- **It still refuses all that a fresh launch refuses,** in the same order: the role file, its lines and the skills
  are read afresh (so the default model and effort hold), and `role-<role>.md` is still written and named on the
  line, which the resumed session does not take.

### Behaviour 9: the launch record

- **One record per launch,** a JSON file `<session id>.json` in the record folder, written whole and flushed before
  the session starts. Keys:

  | Key | Value |
  |---|---|
  | `record`, `format` | `"gov-launch"`, `1` |
  | `session_id` | the UUID given with `--session-id` |
  | `resumes` | the id given with `--resume`, or `null` |
  | `started_at` | UTC, `YYYY-MM-DDTHH:MM:SSZ`, when the record is written |
  | `root` | the real path of the tree the session starts in |
  | `role`, `ticket` | as given to `gov launch` |
  | `ticket_class` | the ticket's `class` as written, or `null` when it has none |
  | `model`, `model_source` | the session's model; `"role default"` or `"after --"` |
  | `effort`, `effort_source` | the same for effort |
  | `subagent_model` | the value set in the settings' `env` |
  | `compaction_threshold` | `"none"` |
  | `role_text` | `{"path": "template/governance/kernel/roles/<role>.md", "version": "<x.y.z>", "sha256": "…"}` |
  | `appended_sha256` | the sha256 of `role-<role>.md` as written |
  | `skills` | one entry per skill of Behaviour 2, skill folders then command files: `name`, `path`, `version`, `sha256`, `folder_sha256`, `named` |
  | `kept_out` | `["--strict-mcp-config", "--setting-sources project,local", "autoMemoryEnabled false"]` |
  | `cli` | `{"path": "~/.local/bin/claude", "version": "<x.y.z>"}`, the version read from the name of the file the CLI's link resolves to (`…/versions/2.1.292`); when the CLI is not such a link, `"not measured: <why>"` (W2-60b reads the session's own log) |

  The CLI is not run to read its version: a run would be a second start of the CLI for each launch.
- **The folder:** `.gov-runtime/launches/` of the repository's main checkout, one for every worktree. Found from any
  worktree without running git, from the tree's `.git`: a folder (the tree is the main checkout) or a `gitdir:` file
  whose `commondir` gives the common directory; the main checkout is the folder that holds the common directory when
  it is named `.git`. A tree with no `.git` at all is its own main checkout (one tree, nothing shared). Refused: a
  `.git` that cannot be read or gives no common directory, a common directory not named `.git` (a bare repository),
  a `.gov-runtime` or `launches` that is a link or not a folder. The launcher makes the folder when it is missing,
  before the settings that name it are given, so the sandbox never meets a denied name that does not exist
  (DEC-402); the two rules are added once, also when today's literal rules already name `launches`.
- **A session cannot write it.**
  - A session in a worktree: the folder lies in the main checkout, outside the session's working folder and beside
    the common directory `<main checkout>/.git` (on the sandbox's write list for git), not inside it. Not on the
    write list.
  - A session in the main checkout: the folder is under its `.gov-runtime/`, outside `scratch/`: refused by the
    guard to every role (DEC-180), and named by the two literal `Edit` deny rules, which bind the file tools (how
    the sandbox treats an `Edit` rule is not measured, DEC-873); W2-56's literal write list (no `.gov-runtime/`
    outside scratch) makes the operating system refuse it too.
- **A record that cannot be written refuses the launch,** and no session starts; a partly written file is removed.
  A CLI that then cannot be started (DEC-205) removes the record before the refusal, so no record names a session
  that never ran.
- **A record never names another session.** The id is a new random UUID per launch, given to the CLI by the
  launcher alone (`--session-id` is refused after `--`), and the file is created only if no file of that name
  exists: a name already there refuses the launch. Both hold: a clash cannot happen in practice, and is refused if
  it does.

### Behaviour 10: fail closed, and the order of the checks

Today's checks run first, in today's order and with today's messages; this ticket's run after them, so every
refusal the launcher makes today still refuses with its message:

1. the role is a worker role (today);
2. today's argument refusals (DEC-313's, `--settings`, `--bare`, `--setting-sources`), then W2-56's
   (`--restricted` … `--system-prompt`), then this ticket's (Behaviour 7, with the forms of `--model` and
   `--effort`);
3. the ticket: known, `in_progress`, of the role's own for engineer, research, product-spec (today);
4. the repository's settings: no sandbox key (DEC-233), no `disableAllHooks`, no bypass mode or added directory
   (DEC-313), the guard wired (today); then no `agent` key, no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in `env` and no
   `autoCompactWindow` (this ticket: either would change the session's prompt or threshold); then round 2's
   spellings and `modelSettings` (Behaviour 6); for a linked worktree, the main checkout found first and its
   local file judged after the tree's two, with the same refusals (round 3);
5. the CLI at `~/.local/bin/claude` (DEC-205, today);
6. the settings built: the research folder and allowlist (DEC-242, DEC-273), the held-out list (DEC-218), the
   evaluation sets (DEC-820, DEC-873), the sandbox strict (today);
7. the role file: readable, its version line, its default line, its skills line; the skills folder and each named
   skill; the command files (round 2); then a model after `--` against the role's; then the user settings file's
   ask and deny rules (round 2) (this ticket);
8. the record's folder found and made; on a resume, the original's record (Behaviour 8) (this ticket);
9. the run folder (DEC-728, DEC-743, DEC-751, today; refuses nothing);
10. the temp folder (DEC-159, DEC-386), `role-<role>.md` written in it, the record written, the session started
    (DEC-392's signals as today).

A missing or unreadable role file, version line, default line, named skill or record refuses the launch, as does a
model after `--` that is not the role's. The role file's version line (D) is required as the default line is:
the record holds the version of the copy loaded, and no fallback stands in for it.

## B. The split with W2-56 in `launcher.py` (DEC-786; W2-56's "Beside W2-60a")

**This ticket's files:** `src/gov/launch/role.py` (new: the role file read and hashed, its version, default and
skills lines, the skills folder and the named skills, the text composed for `role-<role>.md`),
`src/gov/launch/record.py` (new: the record's folder found, made and named in the deny rules; the record written
exclusively and removed on a failed start), `tests/unit/launch/test_role*`, `tests/unit/launch/test_launch_record*`,
this note, the probe record.

**This ticket's lines in today's `launcher.py`** (line numbers at `a1629f1860ca`):

| Where | Change |
|---|---|
| l.1–12, the module's text | one sentence: the role, its skills, the default line and the record |
| l.14–34, imports | `uuid`; the two new modules |
| l.36–64, constants | new lines: the launcher's own switches (`--setting-sources project,local`, `--strict-mcp-config`), the arguments of Behaviour 7, the effort values |
| l.214–244, the repository's settings check | two refusals added inside the loop, after the added-directories check: an `agent` key; `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in `env` |
| new, after l.264 | the check of Behaviour 7: refuses those arguments, reads the forms of `--model`, `--effort` and `--resume`, and returns what was given; it does not touch `_check_cli_args` |
| l.289, after today's argument check | its call |
| new, after l.298 (the sandbox faults) | the role read (role.py), the model after `--` compared, the effort chosen, the record's folder (record.py) |
| new, after l.328 (the temp folder's env) | `CLAUDE_CODE_SUBAGENT_MODEL`, `autoMemoryEnabled`, the two deny rules |
| new, l.331–332, inside `if not state["ended"]:` | `role-<role>.md` written in the temp folder; the session id made; the record written |
| l.333, the start | the argument list only: the launcher's switches between `--settings <json>` and the arguments after `--`; `cwd=root, env=env` untouched |
| l.335–336, the CLI that cannot be started | the record removed before today's refusal |

**W2-56's:** `sandbox.py`, `environ.py`, the rest of `tests/unit/launch/**`, `src/gov/codeintel/__init__.py`; in
`launcher.py` the sandbox's write list and filesystem settings (l.329 and what W2-56 builds), the process
environment of the start (l.330, the `env=` of l.333–334), the refusals of `--restricted`, `--safe-mode`,
`--agents`, `--plugin-dir`, `--plugin-url`, `--mcp-config` and `--system-prompt`, the start lock, and the calls to
its modules.

**Two edges.**
- The launcher's own line may carry a flag it refuses after `--`: `--setting-sources` (refused after `--` today,
  kept), and the `--model`, `--effort`, `--session-id`, `--append-system-prompt-file` and `--fork-session` it sets.
- KPI line 5's "no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in the session's environment" (and the same for a parent's
  `CLAUDE_CODE_SUBAGENT_MODEL` and `CLAUDE_EFFORT`, probe part 2) falls on W2-56's cleaned environment. This ticket
  keeps the variable out of the settings and refuses it after `--` and in the repository's settings, and does not
  edit the `env=` line. If W2-60a merges first, a parent's value still reaches the process until W2-56 merges; the
  acceptance case for that clause is green only with both.

**Left as they are:** `_check_cli_args`, `build_settings`, `_runtime_rules`, `_tree_rules` and `sandbox_faults`
(tests call them directly, C); W2-05's git-environment lines (`launcher.py` runs no git, and the record's folder is
found by reading `.git`, as `gov.guard.runs.common_dir` does, which this ticket calls and does not change); W2-20's
`src/gov/launch/gate*`. No change is needed in another ticket's file.

## C. The existing tests the change touches

After this change a launch that passes today's checks is refused when its tree has no role file, or one without the
version and default lines. No case is handled by a fallback that launches without the role. Classes: (i) copies this
repository's role files: refused until W2-11 writes the lines; nothing changes for it, and the orchestrator holds
W2-60a's merge until W2-11 has merged. (ii) builds a tree with no role file, or its own without the lines: its
meaning changes; an acceptance case is revised by the independent test designer with `Rewrite-Reason:` naming
DEC-826 Q1 or DEC-839 item 5; a unit case outside this ticket's test files is a package (W2-56 holds that folder).
(iii) reads the line, the settings or the arguments in a way this change alters. (iv) unaffected. Cases that refuse
on one of today's checks, before the role is read, are (iv) by the order of Behaviour 10.

Counted at the base (`a1629f1860ca`), by reading each folder's builders and fixtures (W1-46's `make_project`
copies this repository's `template/governance/kernel/` and `.claude/agents/` by `git ls-files`, and not
`.claude/skills/`; W2-50's and W2-58's build their trees from scratch with no role file; W1-38's copies the role
files to `governance/kernel/roles/`). "Cases" counts parametrised cases where a function has several.

| Test file | Cases | Class | How it is handled |
|---|---|---|---|
| `tests/acceptance/W1-28/test_w1_28_launch_product_spec.py` | 42 of 43 | (i) | each starts a session first (exit 0); held until W2-11 (the roster case is (iv)) |
| `tests/acceptance/W1-28/test_w1_28_launch_temp_folder.py` | 19 | (i) | expect a session and its temp folder; held until W2-11 |
| `tests/acceptance/W1-28/` other files | all | (iv) | `gov pause`, the guard, the copy checks: no launch |
| `tests/acceptance/W1-32/test_w1_32_launch.py` | 13 | (i) | held until W2-11; their one-line stderr and empty stdout still hold (Behaviour: nothing new is written) |
| `tests/acceptance/W1-32/test_w1_32_added_cases.py` | 3 launch, 8 status | (i), (iv) | the launch cases expect exit 7 or 0; held until W2-11 |
| `tests/acceptance/W1-32/` status and command-set files | all | (iv) | `gov status` only |
| `tests/acceptance/W1-46/` (20 files) | 206 | (i) | 99 of them test a refusal of today's after a control launch that is now refused; held until W2-11 |
| `tests/acceptance/W1-46/test_w1_46_bypass_and_added_directories.py` | 4 | (i)+(iii) | control launch with `--model haiku` after `--` (l.37–38), now refused, and the line's tail compared (l.108): the test designer replaces `haiku` with the role's model or drops `--model` (`Rewrite-Reason:` DEC-839 item 1); the tail check holds, since the arguments after `--` pass unchanged |
| `tests/acceptance/W1-46/test_w1_46_guard_wiring.py` | 6 | (i)+(iii) | the same (l.52–53, l.66) |
| `tests/acceptance/W1-46/test_w1_46_live_sessions.py` | 36 (`local_only`) | (i)+(iii) | real sessions with `--model haiku` (l.127): P-W2-60a-5 |
| `tests/acceptance/W1-46/` the rest | 242 | (iv) | refused by today's checks, or guard and helper cases; `runtime_and_ln` l.72 holds: `launches` gets its literal rule |
| `tests/acceptance/W1-50/test_w1_50_freeze_launcher.py` | 6 functions (l.54, 64, 73, 84, 97, 109) | (i) | W1-46's tree; the `.gov-runtime/` name checks test presence or absence, so `launches`' rule leaves them as they are; held until W2-11 |
| the same file, l.210; `test_w1_50_freeze_live_pause.py` l.210 | 2 (live) | (i)+(iii) | `--model haiku` (l.239; l.245–248): P-W2-60a-5 |
| `tests/acceptance/W1-50/test_w1_50_ticket_lead_role.py` l.228; the other W1-50 files | 1; all | (iv) | refused by the worker-role check, first; or no launch |
| `tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py` l.75 | 1 function (3 roles) | (i) | W1-46's tree; checks only the empty allowlist; held until W2-11 (l.83, the orchestrator refused, is (iv)) |
| `tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py` l.177 | 1 (live) | (i)+(iii) | W1-46's tree, `--model haiku` (l.213–215): P-W2-60a-5 |
| `tests/acceptance/W2-50/test_w2_50_launcher.py` | 10 functions | (ii) | a tree with no role file that expects one session; the test designer adds a role file with both lines to the builder (`w2_50_support.py:269–287`), `Rewrite-Reason:` DEC-826 Q1 |
| `tests/acceptance/W2-50/test_w2_50_extra_review.py`, `guard_own_folder.py`, `guard_refusals.py`, `last_review.py`, `link_replaced.py`, `owner_answers.py`, `review_findings.py`, `short_round.py` | 10, 8, 14, 8, 5, 7, 7, 6 functions | (ii) | the same, through the shared fixtures (`open_own_folder`, `_launched`, `_populate`, `first`, `links`, `places`); one builder change covers all; their other functions launch nothing, (iv) |
| `tests/acceptance/W2-58/test_w2_58_review.py`, `test_designer.py`, `evaluation_sets.py`, `engineer.py`, `launched_sessions.py` (l.73, l.85) | 2, 2, 2, 2, 2 functions | (ii) | a tree from scratch (`w2_58_support.py:315–350`) whose launch must start; the test designer adds the role file to the builder, `Rewrite-Reason:` DEC-826 Q1 |
| `tests/acceptance/W2-58/test_w2_58_launched_sessions.py` l.187, 198, 208, 219 | 4 (live) | (ii)+(iii) | the same, and `--model haiku` (l.160–161): P-W2-60a-5 (the builder's role file can carry the Haiku line); `.gov-runtime/` is ignored there, so the record does not show in `git status` |
| `tests/acceptance/W2-58/test_w2_58_fails_closed.py` l.41; the other W2-58 functions | 1; all | (iv) | refused by today's evaluation-set check before the role is read; or no launch |
| `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py` l.388, 400, 413 | 3 functions | (ii) | the role files are copied to `governance/kernel/roles/` (`w1_38_support.py:366`), not the path read: the test designer copies them to `template/governance/kernel/roles/` as well, `Rewrite-Reason:` DEC-826 Q1, or P-W2-60a-4 (a) is taken |
| `tests/acceptance/W1-07/test_w1_07_recorded_commands.py` | 1 | (iv) | runs `gov launch --help` only |
| `tests/unit/launch/test_runs.py` | 6 | (ii) | expect `launch() == 0` in a bare temporary tree: package P-W2-60a-6 (W2-56's folder); their `allowWrite` counts are W2-56's to revise, not this ticket's |
| `tests/unit/launch/test_w1_28.py` | 2 of 4 | (ii) | `cannot_be_started` and `exit_code_is_the_sessions` need the start: P-W2-60a-6; the settings and ticket cases are (iv) (`build_settings` is unchanged) |
| `tests/unit/launch/test_w1_32.py` | 18 | (ii) | each starts a stand-in session (signals, DEC-392): P-W2-60a-6 |
| `tests/unit/launch/test_launcher.py` | all | (iv) | call `_check_cli_args`, `build_settings`, the rule helpers, or a launch refused at the ticket; l.127 passes `--model haiku` to `_check_cli_args` only, which is unchanged |
| `tests/unit/launch/test_batch4.py`, `test_command_modules.py` | all | (iv) | helpers, or a launch refused by today's argument check |
| `tests/acceptance/W1-30`, `W1-42`, `W1-48`, `W2-62`, `W1-49`, `W1-26`, `W1-35`, `W1-40`, `W2-59` | all | (iv) | no case calls the launcher (the word only, or `claude` started directly) |

**Totals** (W1-28, W1-32, W1-46 and the unit files counted in cases; the other folders in test functions):

| Class | Count |
|---|---|
| (i) | 77 cases (W1-28, W1-32) + 206 cases (W1-46) + 7 functions (W1-50 6, W1-33 1) |
| (i)+(iii) | 46 cases (W1-46: 4 + 6 + 36 live) + 3 live functions (W1-50 2, W2-54 1) |
| (ii) | 26 unit cases (P-W2-60a-6) + 88 functions (W2-50 75, W2-58 10, W1-38 3) |
| (ii)+(iii) | 4 live functions (W2-58) |
| (iii) alone | none |
| (iv) | the rest (W1-46 alone: 242 cases) |

No case compares the whole line, counts the arguments, compares a whole deny list, or asserts that `.gov-runtime/`
stays as it was. Every class (i) case turns green with W2-11's lines and nothing else; the (iii) and (ii) cases need
the revisions named, and none of them is handled by launching without the role.

## D. What W2-11 must write (for the orchestrator to carry)

1. **In each of the six role files** under `template/governance/kernel/roles/`, and so in the generated agents:
   - the default line, exactly as in Behaviour 3, with the values of its table (DEC-839 items 1, 2, 5); it replaces
     the "Model tier" line, whose "the orchestrator may name another model after `--`" is no longer true;
   - a version line, exactly `- **Version:** <major>.<minor>.<patch>` (digits; once; whole line), raised with each
     change of the file (CAP-24's rule for skills, applied to role files);
   - no skills line yet: W2-33 adds `- **Skills:** <name>, <name>` (lower-case letters, digits and `-`; `, `
     between names; once; whole line; no name twice) to the engineer's role file when it writes the packs.
2. **In every generated `.claude/skills/<name>/SKILL.md`** of a kernel skill, the `version` of its kernel source in
   the front matter (lens E F15, R11; DEC-832 item 2). Required for any skill a role names; for the others the
   record says `no version` until then.
3. **For W2-33, after both:** W1-46's and W1-28's launch projects copy this repository's role files and not
   `.claude/skills/` (C): once W2-33 names skills in the engineer's role file, those projects need the skills
   folder too, or every engineer launch in them is refused. W2-33's test designer carries it.

## E. Open points (packages)

### P-W2-60a-1: the CLI's built-in skills, agents and plugins stay

- **Context:** KPI line 6 (no user-level agents or skills); DEC-826 Q5.
- **What happened:** after c1's switches the session still has the CLI's 19 built-in skills, 5 built-in agents and
  3 built-in plugins (`cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-plugin-authoring`). No switch removes
  them alone: `--disable-slash-commands` removes the project's skills too.
- **Why it matters:** they are context the Gov OS did not write (lens E F7), though not user-level.
- **Options:** (a) keep them, identified by the CLI's version in the record (no cost; their text is the CLI's,
  versioned with it); (b) `--disable-slash-commands`, which breaks Behaviour 2 and the skill packs (DEC-832);
  (c) deny the `Skill` tool, the same loss.
- **Recommendation:** (a), high confidence. W2-60b can list the names from the session's start event.
- **Blocks:** nothing.

### P-W2-60a-2: three things not measured (two now answered)

- **Context:** Behaviours 1, 4 and 8; the probe measured each switch's effect on the start, not these.
- **What happened:** the lead took option (a) (probe part 2b, three sessions, about USD 0.52):
  - (2) **answered** (f2): a resumed launch with `--fork-session` keeps the original's appended text and does not
    take this launch's. Behaviour 8 now takes the record's role text and skills from the original's record;
  - (3) **answered** (k1): a `-p` worker whose `--allowedTools` lacks `Skill` still loads a project skill on
    request. The leads' form needs no `Skill`;
  - (1) **a named residual, not measured:** whether `--setting-sources project,local` also drops a user-level
    `~/.claude/CLAUDE.md` and `~/.claude/rules/`. Neither exists on this machine; measuring it would mean planting
    one in the real home, which every running session would load, or copying the CLI's sign-in into a test home,
    which Policy 2 (a) refuses.
- **Why it matters:** (1) is KPI line 6's "planted home"; if they still load, the CLI has no switch for them but
  `--bare`, which skips the hooks (lens E R6), and it goes to the owner.
- **Options for (1):** (a) leave it a named residual, since neither file exists here (no cost); (b) measure it in a
  dedicated machine account with its own sign-in (an owner's setup, about USD 0.15); (c) refuse a launch when
  either exists in the caller's home (a few lines; a check the CLI's own behaviour may make needless).
- **Recommendation:** (a) now, (b) when a second account exists, medium confidence.
- **Blocks:** nothing in this ticket.

### P-W2-60a-3: `--system-prompt-file` is on no refusal list

- **Context:** W2-56 refuses `--system-prompt` (spaced and `=`); this ticket refuses the append forms.
- **What happened:** the CLI also accepts `--system-prompt-file` (`--help`, under `--bare`), which replaces the
  default prompt as `--system-prompt` does, and lies on neither ticket's list.
- **Why it matters:** a session could start with another prompt in place of the CLI's, beside the role's text.
- **Options:** (a) W2-56 adds it beside `--system-prompt` (one line in its list, its acceptance cases); (b) this
  ticket refuses it with the append forms (one more row in Behaviour 7); (c) leave it, for lens E's accepted-list
  idea in Wave 3.
- **Recommendation:** (a), medium confidence: it is the same kind as W2-56's flags. (b) if W2-56 has merged.
- **Blocks:** nothing in this ticket.

### P-W2-60a-4: where the role file is in an adopted repository

- **Context:** Behaviour 1 reads `template/governance/kernel/roles/<role>.md`, the path the ticket names.
- **What happened:** an adopted repository holds the installed kernel at `governance/kernel/` (DEC-487; W1-38's
  fixture copies the role files to `governance/kernel/roles/`, `w1_38_support.py:366`). There the launch is refused.
- **Why it matters:** EXAMIN's copy launches its workers through `gov launch`.
- **Options:** (a) read `governance/kernel/roles/<role>.md` when the tree has no `template/governance/kernel/`,
  and refuse a tree that has both with different role files (about 10 lines; one more refusal); (b) keep the
  template path only and let W2-21 or the adoption work decide; (c) a project setting naming the kernel's place.
- **Recommendation:** (b) now, (a) in W2-21, medium confidence: (a) is small but widens this ticket past its card.
- **Blocks:** launches in an adopted repository (EXAMIN's copy), and W1-38's 3 cases (C).
- **Decided:** (a), the path only, in round 3 (DEC-951 item 4; §3).

### P-W2-60a-5: the live harness tests on Haiku against "a model not the role's is refused"

- **Context:** DEC-839 item 2 gives live harness tests (W1-49, W1-46) effort low and Haiku 4.5 where a case only
  checks that a hook fired; KPI line 4 refuses a model after `--` that is not the role's.
- **What happened:** the live cases of W1-46, W1-50, W2-54 and W2-58 pass `--model haiku` (C); with the role files
  at `claude-opus-5-5` they are refused.
- **Options:** (a) each live case writes, in its own project's copy of the role file, the default line
  `- **Launch default:** model claude-haiku-4-5-20251001, effort low`, and drops `--model` (the test designer,
  `Rewrite-Reason:` DEC-839 item 1; cost as today); (b) the cases pass `--model claude-opus-5-5 --effort low`
  (several times the cost of each live run); (c) the launcher lets a test name another model, which fails open.
- **Recommendation:** (a), high confidence: what the case tests is unchanged, and the launcher stays closed.
- **Blocks:** those live cases' green runs after the merge.

### P-W2-60a-6: the unit cases in W2-56's folder

- **Context:** C's class (ii) unit cases lie in `tests/unit/launch/test_runs.py`, `test_w1_28.py`, `test_w1_32.py`,
  outside this ticket's test files; W2-56 holds `tests/unit/launch/**`.
- **What happened:** their temporary trees have no role file and expect a launch to start (26 cases).
- **Options:** (a) widen this ticket's paths to those three files for its merge-back, as W2-05's were widened
  (DEC-805 item 2, DEC-941 item 2): each gets a fixture role file of a few lines; (b) W2-56's engineer adds the
  fixture in its own run; (c) the orchestrator fixes them at the merge of the second ticket.
- **Recommendation:** (a), medium confidence: the change is caused here, and (b) ties W2-56 to this ticket's form.
- **Blocks:** a green `tests/unit/launch` after W2-60a's code lands.
