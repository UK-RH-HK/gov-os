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
- **A test home planted** (`plant_home`) with a connector in `~/.claude.json`, a user-level agent and skill, a
  model-side memory file, a user-level `CLAUDE.md` and rule, and a user settings file setting a model, an effort,
  a subagent model and a compaction threshold; the project has a connector in `.mcp.json`.
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
| **S6** no connectors, no user-level agents or skills, no model-side memory; a package for what has no switch | `test_w2_60a_kept_out.py` (5, stand-in, planted home): `--strict-mcp-config` once and no `--mcp-config`; `--setting-sources project,local`; `autoMemoryEnabled: false`; the record's `kept_out`; nothing of the test home in the appended text, the settings or the recorded skills; the model, effort and subagent model are the role's, not the user settings'. `test_w2_60a_documents.py::test_the_cit_e_states_the_shared_record_folder_and_names_the_packages` (P-W2-60a-1, P-W2-60a-2 named). Live: no connector, no `mcp__` tool, no user-level agent or skill, no memory path in a real session's start | the switches are not on the line or in the settings; no record |
| **S7** `--agent`, `--append-system-prompt` and its file form, `--session-id` refused after `--` | `test_w2_60a_refused_arguments.py` (16 + 1 + 1): each in its spaced and `=` form, and `--fork-session`, `--continue`, `-c`, `-pc`, `--resume` without a UUID or not a UUID, `-r<id>`, `-pr <id>`, each refused with `LAUNCH_REFUSED`, "the CLI arguments carry" and the argument's name; a prompt that names them as words launches; the session id is a new random UUID | today's launcher passes them |
| **S8** one record per launch, keyed by the launcher's `--session-id`, written before the start, in one folder every worktree shares; an unwritable record refuses | `test_w2_60a_launch_record.py` (25): one record `<session id>.json`, there when the session started; every key and value of Behaviour 9; the ticket's class or null; two launches, two ids, two records; the CLI's version from its link's target, never by running it, else "not measured"; a worktree's record in the main checkout's folder, the folder denied by two literal `Edit` rules once each and not on the write list; the folder made when missing; refused: `launches` a file, a link, `.gov-runtime` a link, `launches` read-only; a CLI that cannot start leaves no record; a `.git` naming no directory refused; a tree with no `.git` is its own main checkout; nothing new on stdout or stderr. **Resume:** forks under a new id (three spellings) with a record of its own holding the original's role text and skills, the original's record untouched; refused with no record of the original, for another role or ticket, and for what a fresh launch refuses. Live: the record is keyed by the id the session's own log gives | no `--session-id`, no record, no folder, no deny rules; the refusals do not refuse |
| **S9** the lead's research record | `test_w2_60a_documents.py::test_the_rules_probe_record_answers_its_three_questions`: the record exists and states the `paths:`-scoped `.claude/rules/` file, whether it loads, a token cost, and the worker's Edit, Write and Bash | green: the lead committed the record before these tests (KPI 9 is the lead's; one case is enough) |
| **F1** no role text, an unrecorded skill, a model not the role's, a threshold, a user-level agent, skill or connector, model-side memory | S1, S2, S4, S5, S6 above | as above |
| **F2** a role file without its default line that launches; a launch with no record; a record naming another session | S3's refusals; S8's record cases; S7's `--session-id`, `--continue` and `--resume` forms; every refusal in this suite also asserts that **no record was left** (`assert_refused`) | as above |
| **F3** a refusal of today's that no longer refuses | `test_w2_60a_refused_arguments.py::test_every_refusal_the_launcher_makes_today_still_refuses` (26: DEC-313's bypass flags and modes and `--add-dir` in both spellings, `--settings`, `--bare`, `--setting-sources` (also the launcher's own value), DEC-233's sandbox key in both files, `disableAllHooks`, DEC-313's settings keys, the guard not wired, settings not JSON, DEC-218's malformed held-out list, DEC-242's research folder, the orchestrator and an unknown role, an unknown ticket, a ticket not in progress, another role's ticket, no CLI), each after a control launch in a tree whose role files are well formed; `test_today_s_checks_come_first_with_today_s_message` (5) in a tree with no role file (Behaviour 10's order) | green today: they must stay green |

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

The red run (not live), at the base, in this worktree: `117 failed, 35 passed, 5 deselected`. The failures, by the
first assertion each meets: 65 "gov launch did not refuse (exit code 0)"; 31 "the session's line carries
--session-id 0 times" (so no record); 10 "0 --append-system-prompt-file values"; 7 "--model 0 times"; and one each
for the subagent model, `autoMemoryEnabled`, `--strict-mcp-config`, the record folder at the start, its deny rule
and the caller's `CLAUDE_CODE_AUTO_COMPACT_WINDOW`.

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
- The `serial-only.txt` entry for the live file (above).
