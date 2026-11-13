# W2-60a acceptance tests: the role, its skills, its model and effort at launch; the launch record

Ticket `DAEO-cv58` (W2-60a, FULL). Written by the independent test designer (MR-3) from the ticket's KPI lines,
its card (`docs/plan/WAVE_2_WBS.md` §2, W2-60 and W2-60a), DEC-826 Q1/Q2/Q5, DEC-832, DEC-838, DEC-839, today's
launcher on `w2/integrate`, and the design's behaviour sections and the lead's corrections as the brief gave them
in text. The design note and the research record (this ticket's own files) were not read (DEC-820 (c)). The tests
were written before the implementation existed, and shown red.

## How to run them: this worktree's own `src/` (DEC-732)

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests/acceptance/W2-60a -q \
        -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"

Every `gov` the tests start is run through `pyproject.toml`'s console-script entry point (no install) with
`PYTHONPATH` set to the runner's own value (DEC-732 sets it per command), else to the `src/` of the worktree that
holds these files (`w2_60a_support.python_path`). So a run from this worktree exercises this worktree's code. Check
it with `PYTHONPATH=<worktree>/src python3 -c "import gov; print(gov.__file__)"`.

The live file runs only when chosen: `-m local_only` (see "Live cases").

## What the tests use

- **A fixture project built from scratch** at `<test home>/work/repo` (`w2_60a_support.make_project`): fixture
  tickets (one with no `class`), a settings file that registers a copy of the kernel guard, **fixture role files**
  at `template/governance/kernel/roles/<role>.md` for the five worker roles, each with
  `- **Version:** <x.y.z>` and `- **Launch default:** model <model>, effort <effort>` (research's model is
  `claude-sonnet-5-5`, so the value is seen to come from the file), **fixture generated agents** at
  `.claude/agents/` whose text is not the role file's, **fixture skills** at `.claude/skills/` (a versioned one with
  extra files, one versioned as unquoted YAML, one with no version, one with no `name`) and **kernel copies** at
  `template/governance/kernel/skills/` with other versions, which the record must not take. Nothing relies on this
  repository's own role files carrying a default line (W2-11 writes them).
  The project also holds the eight **template copies** at `.claude/templates/<stem>.md` (`TEMPLATE_FILES`, any bytes,
  marker `zq60a-template-copy`), since W2-153's launcher refuses a role without its template (`LAUNCH_NO_TEMPLATE`).
- **An open resource gate** (`plant_open_gate`, W2-58's form from W2-136): a dated `gate.json` in the test home's
  `.gov-os/machine/` and readings with room to spare named through `GOV_RESOURCES_*` in every `gov` child's
  environment (`base_environment`), since every launch runs W2-20's gate (DEC-1088 (5)(b)); the gate is not under test.
- **A test home planted** (`plant_home`) with a connector in `~/.claude.json`, a user-level agent and skill, a
  model-side memory file, a user-level `CLAUDE.md` and rule, and a user settings file setting a model, an effort,
  a subagent model, a compaction threshold, an `env` variable, a hook, and `permissions` with `allow`, `ask` and
  `deny` rules and a `defaultMode` (`user_settings`; round 2); the project has a connector in `.mcp.json`.
- **Fixture command files** (round 2, `add_commands`), added by the cases that need them, not by `make_project`:
  `.claude/commands/w260a-top.md` (version quoted, a front matter `name` of another form, as `opsx`'s files have),
  `w260a-ns/unquoted.md` (version unquoted), `w260a-ns/unversioned.md` (none), `w260a-ns/plain.md` (no front matter)
  and `w260a-ns/notes.txt` (not Markdown).
- **A stand-in CLI** at `<test home>/.local/bin/claude` that starts no session: it records its arguments, its
  environment, its `--settings` value, the bytes of the `--append-system-prompt-file` it is handed (the file goes
  with the session's temp folder), and what the record folder held **when it started**.

## KPI lines and their tests

"Red" is the reason each case fails before the implementation, as seen on the run of 2026-10-29 (below).

| KPI line | Tests | Red because |
|---|---|---|
| **S1** the session starts as its role; the record holds the role file's path, version, hash | `test_w2_60a_role_text.py` (15): text appended in `role-<role>.md` in the session's temp folder, per role; the record's `role_text` and `appended_sha256`; the file as it stands at each launch; the copy goes with the temp folder; refused: no role file, a folder in its place, no version line, a version not `x.y.z`; an `agent` key in either repository settings file refused. Live: `test_a_launched_session_has_its_role_text_and_named_skill_at_its_start` | no `--append-system-prompt-file` on the line; no record; the refusals do not refuse |
| **S2** the skills the session can load are recorded from the loaded copy; named skills load; a missing named skill refuses | `test_w2_60a_skills.py` (13): every `.claude/skills/` folder recorded (name, path, version or `no version`, sha256, folder hash, named), never the kernel copy's version, never the user-level skill; the folder hash follows every file of the folder; named skills appended after the role's text, in the order named; a new pack named by the role loads with no code change; refused: a named skill missing, without a version, without its `SKILL.md`, a malformed skills line, a skill folder that is a link or holds one, a front matter that is not YAML; no `.claude/skills/` is an empty list unless a skill is named. Live: the named skill's code word | no record, nothing appended; the refusals do not refuse |
| **S3** default model and effort applied and recorded; missing or malformed line refused; an effort after `--` is the launch's own | `test_w2_60a_model_and_effort.py`: the role's model and effort on the line once and recorded `role default`, per role; `--effort xhigh` / `--effort=xhigh` applied once and recorded `after --`; the role's own model after `--` passed once and recorded `after --`; refused: no default line; nine malformed lines (alias, not `claude-`, upper case, unknown effort, a third field, no space after the comma, text after the effort, indented, two lines) | no `--model`/`--effort` on the line; no record; the refusals do not refuse |
| **S4** a model not the role's refused, naming both; the subagent model set and recorded | same file: five models not the role's (aliases, another model, `=` form, research given Opus) refused naming both; `--model`/`--effort` without a value, empty, twice, or an unknown effort refused; `CLAUDE_CODE_SUBAGENT_MODEL` in the settings' env is the session's model and recorded (engineer, research); the caller's own value does not reach the settings | today's launcher passes any model; the settings carry no subagent model |
| **S5** no compaction threshold | `test_w2_60a_no_compaction_threshold.py` (8): no `--autocompact`, no `CLAUDE_CODE_AUTO_COMPACT_WINDOW` and no `autoCompactWindow` in the settings, the record says `none`; `--autocompact` refused in both spellings; the variable in either repository settings file refused; **the caller's process environment** (green only once W2-56 has merged, see below); **`autoCompactWindow` in the repository's settings** (beyond the design, see below) | no record; the refusals do not refuse; the caller's variable reaches the session today |
| **S6** no connectors, no user-level agents or skills, no model-side memory; a package for what has no switch | `test_w2_60a_kept_out.py` (5, stand-in, planted home): `--strict-mcp-config` once and no `--mcp-config`; `--setting-sources project,local`; `autoMemoryEnabled: false`; the record's `kept_out`; nothing of the test home in the appended text, the settings (but the user's ask and deny rules, round 2) or the recorded skills; the model, effort and subagent model are the role's, not the user settings'. `test_w2_60a_documents.py::test_the_cit_e_states_the_shared_record_folder_and_names_the_packages` (P-W2-60a-1, P-W2-60a-2 named). Live: no connector, no `mcp__` tool, no user-level agent or skill, no memory path in a real session's start | the switches are not on the line or in the settings; no record |
| **S7** `--agent`, `--append-system-prompt` and its file form, `--session-id` refused after `--` | `test_w2_60a_refused_arguments.py` (16 + 1 + 1): each in its spaced and `=` form, and `--fork-session`, `--continue`, `-c`, `-pc`, `--resume` without a UUID or not a UUID, `-r<id>`, `-pr <id>`, each refused with `LAUNCH_REFUSED`, "the CLI arguments carry" and the argument's name; a prompt that names them as words launches; the session id is a new random UUID | today's launcher passes them |
| **S8** one record per launch, keyed by the launcher's `--session-id`, written before the start, in one folder every worktree shares; an unwritable record refuses | `test_w2_60a_launch_record.py` (25): one record `<session id>.json`, there when the session started; every key and value of Behaviour 9; the ticket's class or null; two launches, two ids, two records; the CLI's version from its link's target, never by running it, else "not measured"; a worktree's record in the main checkout's folder, the folder denied by two literal `Edit` rules once each and not on the write list; the folder made when missing; refused: `launches` a file, a link, `.gov-runtime` a link, `launches` read-only; a CLI that cannot start leaves no record; a `.git` naming no directory refused; a tree with no `.git` is its own main checkout; nothing new on stdout or stderr. **Resume:** forks under a new id (three spellings) with a record of its own holding the original's role text and skills, the original's record untouched; refused with no record of the original, for another role or ticket, and for what a fresh launch refuses. Live: the record is keyed by the id the session's own log gives | no `--session-id`, no record, no folder, no deny rules; the refusals do not refuse |
| **S9** the lead's research record | `test_w2_60a_documents.py::test_the_rules_probe_record_answers_its_three_questions`: the record exists and states the `paths:`-scoped `.claude/rules/` file, whether it loads, a token cost, and the worker's Edit, Write and Bash | green: the lead committed the record before these tests (KPI 9 is the lead's; one case is enough) |
| **F1** no role text, an unrecorded skill, a model not the role's, a threshold, a user-level agent, skill or connector, model-side memory | S1, S2, S4, S5, S6 above | as above |
| **F2** a role file without its default line that launches; a launch with no record; a record naming another session | S3's refusals; S8's record cases; S7's `--session-id`, `--continue` and `--resume` forms; every refusal in this suite also asserts that **no record was left** (`assert_refused`) | as above |
| **F3** a refusal of today's that no longer refuses | `test_w2_60a_refused_arguments.py::test_every_refusal_the_launcher_makes_today_still_refuses` (26: DEC-313's bypass flags and modes and `--add-dir` in both spellings, `--settings`, `--bare`, `--setting-sources` (also the launcher's own value), DEC-233's sandbox key in both files, `disableAllHooks`, DEC-313's settings keys, the guard not wired, settings not JSON, DEC-218's malformed held-out list, DEC-242's research folder, the orchestrator and an unknown role, an unknown ticket, a ticket not in progress, another role's ticket, no CLI), each after a control launch in a tree whose role files are well formed; `test_today_s_checks_come_first_with_today_s_message` (5) in a tree with no role file (Behaviour 10's order) | green today: they must stay green |
| **S2, F1** (round 2, F1) the project's command files are skills the session can load; the record names each | `test_w2_60a_command_skills.py` (12): every Markdown file under `.claude/commands/` recorded as `<name>` or `<namespace>:<name>` (never its front matter's `name`), with its path, its version as written or `no version` (quoted, unquoted, none, no front matter), its sha256 and `named: false`; a `.txt` there not recorded; the entry follows the file as it stands at the launch; the `.claude/skills/` entries unchanged beside them; commands with no `.claude/skills/` recorded; refused (after a control launch, naming the file or folder): a command file that is a link (top level, in a namespace), a namespace folder that is a link, a front matter that is not YAML. Green guards: no `.claude/commands/` or an empty one adds nothing; a command's name in a role's skills line refuses. Live: `test_every_project_skill_in_the_session_s_start_is_in_its_record` | the record holds no command entry; the refusals do not refuse |
| **F3** (round 2, F2) no protection a launched worker has today is lost: the user's ask and deny rules | `test_w2_60a_user_permissions.py` (19): every `permissions.ask` and `permissions.deny` string of the test home's `~/.claude/settings.json` in the `--settings` value's `permissions.ask` / `permissions.deny`, per worker role, the launcher's own deny rules kept (those of a launch with no user file all still there); refused (after a control launch, with "settings"): the file unreadable, a folder, not JSON, not an object, `permissions` not a map, `ask` / `deny` not a list or holding a non-string. Green guards: no allow rule, `defaultMode`, `env`, model, `effortLevel` or hook of the file carried; an absent file, or one with no `permissions`, only `allow`, or empty lists, launches carrying no ask rule. **Revised:** `test_w2_60a_kept_out.py::test_nothing_of_the_test_home_but_the_user_s_ask_and_deny_rules_reaches_the_session_s_start` | the settings carry no ask rule and none of the user's deny rules; the refusals do not refuse |
| **S5** (round 2) more spellings of a threshold | `test_w2_60a_no_compaction_threshold.py::test_another_spelling_of_a_threshold_in_the_repository_s_settings_is_refused` (8): `env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `env.CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`, `modelSettings.<the role's model>.autoCompactWindow` and `modelSettings.<another model>.autoCompactWindow`, each in `.claude/settings.json` and `.claude/settings.local.json`, refused with `LAUNCH_REFUSED`, "no launch sets a compaction threshold (DEC-838)" and the key's name. Green guard: a `modelSettings` entry without the key launches (2) | the refusals do not refuse |
| **S1, S5, S6, F1** (round 3) a worktree launch checks the main checkout's local settings | `test_w2_60a_main_checkout_and_adopted_layout.py::test_the_main_checkout_s_local_settings_are_checked_for_a_worktree_launch` (8): `autoCompactWindow`, `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `modelSettings.<model>.autoCompactWindow`, `agent`, `sandbox`, `permissions.defaultMode: bypassPermissions`, `permissions.additionalDirectories`, `disableAllHooks` in the main checkout's `.claude/settings.local.json`, refused from a linked worktree with `LAUNCH_REFUSED` and the words of the tree's own file's case; `..._not_json_refuse_a_worktree_launch` (1, naming `settings.local.json`); each after a control launch from the worktree | the main checkout's local file is not read: "gov launch did not refuse (exit code 0)" |
| **S1** (round 3) an adopted tree's role file | `test_w2_60a_main_checkout_and_adopted_layout.py::test_an_adopted_tree_s_role_file_is_read_from_its_kernel` (1): no `template/`, the role file at `governance/kernel/roles/engineer.md`; the launch starts and the record's `role_text` names that path, version and sha256 | refused: "the role file template/governance/kernel/roles/engineer.md cannot be read" |
| **S2, F3** (round 4, after the merge of `w2/integrate`) a skill copy versioned only under `metadata:`, the form the kernel's generated copies take today | `test_w2_60a_skills.py::test_a_named_skill_versioned_only_under_metadata_launches_and_is_recorded_with_that_version` (1): a role naming a skill whose `SKILL.md` carries only `metadata: version: 1.4.0` launches, its text appended, its record entry version `1.4.0`, the copy's sha256, `named: true`. Green guard: `test_w2_60a_skills.py::test_a_skill_with_a_top_level_version_and_a_metadata_version_is_recorded_with_the_top_level_one` (1): top-level `2.2.0` beside `metadata.version` `9.0.0` is recorded `2.2.0` | refused: the named skill "carries no version" (only the top-level `version` is read) |
| **S4, S6, S7** (round 2) more arguments refused after `--` | `test_w2_60a_refused_arguments.py::test_a_model_connector_or_prompt_argument_is_refused_after_the_double_dash` (6): `--fallback-model` spaced and `=`, `--chrome`, `--ide`, `--system-prompt-snapshot` spaced and `=`, each with `LAUNCH_REFUSED`, "the CLI arguments carry" and its name. Green guards: `--no-chrome` launches, passed unchanged; a prompt naming the four as words launches | today's launcher passes them |

### Counts

| File | Cases | Red on 2026-10-29 | Green (must stay green) |
|---|---|---|---|
| `test_w2_60a_role_text.py` | 15 | 15 | 0 |
| `test_w2_60a_skills.py` | 13 | 13 | 0 |
| `test_w2_60a_model_and_effort.py` | 35 | 35 | 0 |
| `test_w2_60a_no_compaction_threshold.py` | 8 | 8 | 0 |
| `test_w2_60a_kept_out.py` | 5 | 5 | 0 |
| `test_w2_60a_refused_arguments.py` | 49 | 17 | 32 (today's refusals, their order, the prompt control) |
| `test_w2_60a_launch_record.py` | 25 | 24 | 1 (a CLI that cannot start: no record) |
| `test_w2_60a_documents.py` | 2 | 0 | 2 (the lead's research record, the CIT-E) |
| **not live** | **152** | **117** | **35** |
| `test_w2_60a_live_sessions.py` (`local_only`) | 5 | not run here | |

Round 2's counts are in "Round 2 (review 1)" below.

The red run (not live), at the base, in this worktree: `117 failed, 35 passed, 5 deselected`. The failures, by the
first assertion each meets: 65 "gov launch did not refuse (exit code 0)"; 31 "the session's line carries
--session-id 0 times" (so no record); 10 "0 --append-system-prompt-file values"; 7 "--model 0 times"; and one each
for the subagent model, `autoMemoryEnabled`, `--strict-mcp-config`, the record folder at the start, its deny rule
and the caller's `CLAUDE_CODE_AUTO_COMPACT_WINDOW`.

## Round 2 (review 1)

Review 1 of the implementation failed. Its findings were given to the test designer as described behaviours (DEC-136,
DEC-802), with no reading of the implementation, the design note or the research record (DEC-820 (c)); the cases
were written and shown red against the head `3b32a107` (W2-60a's own `src/`, DEC-732) on 2026-10-30:

1. **F1, the command files** (KPI 2, failure 1 "an unrecorded skill"): the CLI loads every Markdown file under
   `.claude/commands/` as a skill (`<name>`, `<namespace>:<name>`; this repository's six `opsx:` files). New file
   `test_w2_60a_command_skills.py`; one live case in `test_w2_60a_live_sessions.py`.
2. **F2, the user's permission rules** (failure 3): `--setting-sources project,local` drops `~/.claude/settings.json`
   whole, and with it the owner's `ask` and `deny` rules a launched worker has today. New file
   `test_w2_60a_user_permissions.py`; the planted home's user settings gain those rules (`w2_60a_support.user_settings`)
   and the kept-out case is revised to allow exactly the two lists (`Rewrite-Reason:` review 1's F2, DEC-136).
3. **More threshold spellings** (KPI 5): new cases in `test_w2_60a_no_compaction_threshold.py`.
4. **More arguments after `--`** (KPI 4, 6, and the resumed session's prompt): new cases in
   `test_w2_60a_refused_arguments.py`.

Every refusal also asserts that no launch record is left (`assert_refused`). Refusals the brief gives no words for
are held to `LAUNCH_REFUSED` and the file's name (command files) or "settings" (the user file), each after a control
launch in the same tree or home, so that the fault is the only change.

| File | Cases now | Added | Red at the head | Green (guards, must stay green) |
|---|---|---|---|---|
| `test_w2_60a_command_skills.py` (new) | 12 | 12 | 8 | 4 (no or an empty `.claude/commands/`; a command named in a skills line refuses, top level and namespaced) |
| `test_w2_60a_user_permissions.py` (new) | 19 | 19 | 14 | 5 (nothing else carried; an absent file; no `permissions`, only `allow`, empty lists) |
| `test_w2_60a_no_compaction_threshold.py` | 18 | 10 | 8 | 2 (a `modelSettings` entry without the key, both files) |
| `test_w2_60a_refused_arguments.py` | 57 | 8 | 6 | 2 (`--no-chrome`; the prompt naming them) |
| `test_w2_60a_kept_out.py` | 5 | 0 (1 revised) | 0 | 5 |
| **not live** | **201** | **49** | **36** new | |
| `test_w2_60a_live_sessions.py` (`local_only`) | 6 | 1 | not run here (the lead's) | |

The run at the head, one file at a time (the nightly was running): `test_w2_60a_command_skills.py` 8 failed,
4 passed; `test_w2_60a_user_permissions.py` 14 failed, 5 passed; `test_w2_60a_no_compaction_threshold.py` 9 failed
(8 new, and the W2-56 case below), 9 passed; `test_w2_60a_refused_arguments.py` 6 failed, 51 passed;
`test_w2_60a_kept_out.py` 5 passed; the other files as before (`role_text` 15, `skills` 13, `model_and_effort` 35,
`launch_record` 25, `documents` 2 passed). So the head stands at 37 failed, 164 passed: 36 red for round 2 and the
W2-56 case. The 36, by the first assertion each meets: 27 "gov launch did not refuse (exit code 0)" (4 command
files, 9 user settings files, 8 threshold spellings, 6 arguments); 5 "the user settings' ask rules ... are not in the
session's permissions.ask" (one per worker role); 4 "the record's skills are not ... the .claude/commands/ Markdown
files" or "the command ... is not recorded" (the record holds no command entry).

## Round 3 (review 2, DEC-951)

Round 3 is the ticket's last (DEC-951 item 4). Review 2's five items were given to the test designer as text (DEC-136),
with no reading of the implementation (DEC-820 (c)); the cases were written and shown red against this tests
worktree's `src/` (the ticket's code before the round, DEC-732) on 2026-10-31:

1. **A worktree's local settings**: the CLI loads a linked worktree session's local settings from the main
   checkout's `.claude/settings.local.json`, so a worktree launch refuses on that file what it refuses on the tree's
   own. New file `test_w2_60a_main_checkout_and_adopted_layout.py`, 9 cases, all red ("gov launch did not refuse").
   The control (a worktree launch with no such file launches) is the existing record case and each case's own first
   launch.
2. **The adopted layout**: with no `template/`, the role file is `governance/kernel/roles/<role>.md`. One case in the
   same file, red (the launch is refused for want of `template/governance/kernel/roles/engineer.md`). W1-38's cases
   are not touched.
3. **The unit cases** `tests/unit/launch/test_runs.py` (6), `test_w1_28.py` (2), `test_w1_32.py` (18): each bare tree
   gets the engineer's role file at `template/governance/kernel/roles/engineer.md` (version `1.0.0`, default
   `claude-opus-5-5`, `high`); nothing else changes (P-W2-60a-6). All 26 pass.
4. **The nightly route**: the live file's line is in `tests/acceptance/serial-only.txt` (P-TD-4).
5. **W2-58's live phantom-deletion pair**: the fixture's role file is written before the fixture's commit (it was
   written after it, so the tree was not clean when the session started).

| File | Cases now | Added | Red at the base | Green |
|---|---|---|---|---|
| `test_w2_60a_main_checkout_and_adopted_layout.py` (new) | 10 | 10 | 10 | 0 |

## Beyond the design, and what waits on another ticket

- `test_a_compaction_threshold_in_the_caller_s_environment_does_not_reach_the_session`: KPI 5's "the session's
  environment" for a parent's `CLAUDE_CODE_AUTO_COMPACT_WINDOW` is W2-56's cleaned process environment, which this
  ticket does not change. **It is green only once W2-56 has merged.**
- `test_an_auto_compact_window_key_in_the_repository_s_settings_is_refused` (2): the repository's settings key
  `autoCompactWindow` sets the compaction window as the variable does (W1-49's README lists it among the CLI's
  routes). The design's Behaviour 6 refuses only the variable in the settings' `env`; KPI failure 1 ("a launch that
  starts with ... a compaction threshold") covers the key. Package P-TD-W2-60a-1 (in the test designer's return)
  asks the lead to take it into the design or rule it out.
- The folder hash's serialisation, the order of the line's options, the separator between the role's and the
  skills' text, and a skill entry's `path` form are the design's; the tests hold them only to what can be seen
  without them (a sha256 that moves with any file of the folder; the caller's arguments last and unchanged; the
  role's text first and the skills after it in the order named; the path of the loaded copy, relative or absolute).
- A file `<session id>.json` already in the folder refuses the launch (Behaviour 9): not tested, since the id is the
  launcher's own new random UUID and cannot be known beforehand.

## Live cases and their route

`test_w2_60a_live_sessions.py`, 5 cases over **one** real session per run, `pytestmark = pytest.mark.local_only`.
The session is started through `gov launch engineer DAEO-zz6a -- -p <prompt> --output-format stream-json --verbose
--model claude-opus-5-5 --effort low --max-turns 2` in a fixture project built from scratch whose engineer role
file's default is `claude-opus-5-5, effort high` and names one skill; the role file and the skill each carry a code
word the session is asked for. The cases read the session's log (the `init` event and the result) and its launch
record. It runs in the caller's real home (a session needs the caller's own sign-in, which no test may read or
copy, so a planted home is the stand-in cases'); the user-level agents and skills it names are the names under the
real `~/.claude/agents/` and `~/.claude/skills/` at the time, plus every `anthropic-skills:` skill, and it asserts
nothing on the CLI's own built-ins (P-W2-60a-1). It needs the CLI, `bwrap`, `socat` and the network, and fails,
naming what is missing, without them. A launched test designer cannot run it: the lead runs it from an unsandboxed
session. The launcher makes the run folder `~/gov-os-runs/W2-60a-fixture` in the real home, as W2-58's live cases
make theirs.

Its route is the nightly, as the other live-session files: the entry for `tests/acceptance/serial-only.txt` is
outside this folder and is returned to the lead as a package, with the exact line:

    tests/acceptance/W2-60a/test_w2_60a_live_sessions.py  # nightly: live-session: one real engineer session through gov launch shows its role text, its named skill and a start with no connector, user-level agent or skill, or memory

## Earlier tests this change touches

### Revised (each in a commit of its own with its `Rewrite-Reason:`)

| Test | What changed | Reason |
|---|---|---|
| `tests/acceptance/W2-50/w2_50_support.py` (the builder of all W2-50 launches: `test_w2_50_launcher.py` and the eight files the design lists) | the fixture project gets one role file per worker role at `template/governance/kernel/roles/`, with a version line and the default line at DEC-839's values | `Rewrite-Reason: DEC-826 Q1`: the launcher reads the role file of the tree; no expectation lowered |
| `tests/acceptance/W2-58/w2_58_support.py` (`make_project`, the builder of the launches in `review`, `test_designer`, `evaluation_sets`, `engineer`, `launched_sessions`) | the same, in the base commit | `Rewrite-Reason: DEC-826 Q1` |
| `tests/acceptance/W1-46/test_w1_46_bypass_and_added_directories.py` (`ORDINARY`), `test_w1_46_guard_wiring.py` (`HEADLESS`) | `--model haiku` in the control arguments becomes `--model claude-opus-5-5`, the role's model; the tail checks hold, since the arguments after `--` pass unchanged | `Rewrite-Reason: DEC-839 item 1`: a model after `--` must be the role's. Both stay class (i): red until W2-11 writes the lines |
| `tests/acceptance/W1-46/test_w1_46_live_sessions.py`, `W1-50/test_w1_50_freeze_launcher.py` (the live case), `W1-50/test_w1_50_freeze_live_pause.py`, `W2-54/test_w2_54_sandboxed_worker.py` | no `--model haiku`; the project's copy of the role file gets the default line `model claude-haiku-4-5-20251001, effort low` (`w1_46_support.set_live_launch_default`, new lines of this ticket's) | `Rewrite-Reason: DEC-839 item 5` (the design's P-W2-60a-5; item 2 keeps live harness tests on Haiku 4.5 at low). They copy this repository's role files, so they also need W2-11's version line: class (i) |
| `tests/acceptance/W2-58/test_w2_58_launched_sessions.py` | the same, through W2-58's builder's role file | `Rewrite-Reason: DEC-839 item 5` |
| `tests/acceptance/W1-46/README.md`, `W2-54/README.md`, `W2-58/README.md` | the line that said `--model haiku` says how the model is now given | the same |

### Left red until W2-11 writes the role files' version and default lines (class (i), by design)

These copy this repository's own role files (`w1_46_support.make_project`, W1-28's and W1-32's builders): after
this ticket a launch in their tree is refused until W2-11's lines exist, and the orchestrator holds W2-60a's merge
until W2-11 has merged. Nothing in them is revised.

- `tests/acceptance/W1-28/test_w1_28_launch_product_spec.py` (42 of 43), `test_w1_28_launch_temp_folder.py` (19);
- `tests/acceptance/W1-32/test_w1_32_launch.py` (13), `test_w1_32_added_cases.py` (its 3 launch cases);
- `tests/acceptance/W1-46/`: the 206 cases that start a session, the two control files above included, and the live
  file;
- `tests/acceptance/W1-50/test_w1_50_freeze_launcher.py` (6 functions) and the two live cases;
- `tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py` l.75;
- `tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py`.

### Not revised: returned as packages

- `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py` l.388, 400, 413 (3 functions): a project made from the
  template keeps its kernel at `governance/kernel/`, so its role files are at `governance/kernel/roles/`, not at the
  path the design reads. Copying them to `template/governance/kernel/roles/` as well would plant a folder a product
  repository never has and make the case pass for a reason a product does not share. Package P-TD-W2-60a-2 (the
  design's P-W2-60a-4).
- `tests/unit/launch/` (the design's class (ii) unit cases): W2-56's folder; the lead's package P-W2-60a-6.
  **Revised in round 3** (DEC-951): see "Round 3".
- The `serial-only.txt` entry for the live file (above). **Added in round 3** (DEC-951).
