---
id: DAEO-k1us
status: closed
deps: []
links: [DAEO-5rgj, DAEO-lrre, DAEO-6f0s]
created: 2026-11-18T23:30:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-201
tags: [launch, roles, rubric, usage, hooks, emergency-2]
wbs_id: W2-201
title: "The rubric in code (K1, RT-8) and audit 09's usage rules held by code: the role files and the criticality list carry audit 4's Table 3 with the owner's model changes, the launcher refuses a model the table does not give, the helper hook lets Opus through only for C3 work and refuses a fork, the launched workers keep the 5-minute cache, no wake-up hook is written"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: []
waits_on: []
closes:
- CAP-35.a
- CAP-35.b
- CAP-35.c
allowed_paths:
- src/gov/launch/**
- governance/project/criticality.yaml
- governance/project/model-exceptions.yaml
- .claude/hooks/agent_model.py
- template/governance/kernel/roles/*.md
- template/.rulesync/subagents/*.md
- .rulesync/subagents/*.md
- .claude/agents/*.md
- tests/unit/launch/**
- tests/unit/hooks/**
est_loc: 600
kpis:
  success:
  - 'S1 The role files carry the rubric (audit 4 Table 3 with DEC-1212 (3) and DEC-1214 K1): every role file, in the kernel folder and in each generated copy the existing copy checks hold equal to it, has one `Launch default` line and, where the model varies by class, one `Launch by criticality` line, with these values (effort high everywhere, C0 as today): orchestrator (the CTO) and senior-engineer default Opus, no table line; ticket-lead default Sonnet (every class, every profile), no table line; engineer and independent-test-designer default Sonnet, table C3 Opus, C2 Sonnet, C1 Sonnet, C0 Haiku low; independent-auditor default Sonnet, table C3 Opus, C2 Sonnet, C1 Sonnet, C0 Haiku low (the launcher promotion to Opus after a second failed review stays); qa-engineer default Sonnet, table C3 Opus, C2 Sonnet (no Opus on FULL any more), C1 Sonnet, C0 Haiku low; product-spec and research default Sonnet, no table line. Verify: a test reads each file with the launcher role reader (`gov.launch.role`) and compares model and effort per class with this table; a copy that differs from the kernel file fails it. [audit 4 Table 3, lines 173-190; DEC-1212 (3); DEC-1214 K1]'
  - 'S2 The criticality list is Table 3 with the retired machinery gone: `governance/project/criticality.yaml` gives C3 to the kernel and the Contract (`template/governance/kernel/**`, `governance/kernel/**`, `docs/contract/**`), the landing and close (`src/gov/close/**`, `src/gov/accept/**`, `src/gov/queue/**`, `src/gov/dispatch/landing.py`, `src/gov/tasks/queue.py`, `governance/project/orchestration/tools/merge_queue.py`, `governance/project/operator/landing_check.py`), the memory measure and sets (`src/gov/memaudit/**`, `fixtures/evaluation/**`), release, update and pin (`src/gov/release/**`, `src/gov/update/**`, `src/gov/lock/**`) and the path map (`governance/project/path-map.yaml`); C2 to all other `src/**`, the schemas and the test map; C1 to records and docs; the guard, the hooks, the settings, secrets, walls, held-out and operator entries of the old list are not C3 rules; a FULL ticket is still at least C2. Verify: `gov.launch.criticality.ticket_criticality` on the real file for one ticket per listed path (C3), for `src/gov/guard/x.py`, `.claude/hooks/agent_model.py` and `.claude/settings.json` (not C3), for `src/gov/health/x.py` (C2) and for `docs/x.md` (C1); a FULL ticket on `docs/x.md` is C2. [audit 4 line 174-176; DEC-1214 K1]'
  - 'S3 `gov launch` picks the model and effort from the role file, the ticket class and the table, and states them in its launch record: for a planted worker launch on a stub CLI, an engineer on a C3 ticket runs `claude-opus-5-5`, on a C2 ticket `claude-sonnet-5-5`; an independent-test-designer likewise; an independent-auditor on C2 runs Sonnet and on C3 Opus; a qa-engineer on a FULL C2 ticket runs Sonnet; the record names the model and its source (`by criticality`), the effort and its source, the class and the rubric file; a successful launch still writes nothing to stdout or stderr. Verify: those launches on the stub CLI, reading the record and the `--model` and `--effort` the stub received; the same launch with no criticality file records `role default` and `rubric` null. [RT-8 (DAEO-5rgj); EMERGENCY-2 6.3; DEC-1212 (2)]'
  - 'S4 `gov launch` refuses a caller other model, and an exception comes only from the exceptions file: `gov launch engineer <C2 ticket> -- --model claude-opus-5-5` is refused with `LAUNCH_REFUSED` naming the session model, the ticket class and `governance/project/model-exceptions.yaml`; with an entry `{subagent_type: engineer, model: opus, decided: <text>}` in that file it starts on Opus and the record names `model_source` `exception` and the entry decided text in a key `exception` (null in every other record); an entry that carries `class: C3` lifts the refusal for a C3 ticket only; an exceptions file that cannot be read or is not a map with an `exceptions` list refuses a launch that asks for another model (fail closed) and does not touch a launch that asks for none. The trial and promotion routes of W2-184 stay as they are. Verify: the cases on the stub CLI with a planted exceptions file in each form. [DEC-1212 (2); DEC-1214 K1]'
  - 'S5 The helper hook lets Opus through for a test designer, engineer, independent auditor or qa engineer only for C3 work: `.claude/hooks/agent_model.py` reads the ticket the spawn names in a line `Task: <ticket id>` of its prompt, reads `.tickets/<id>.md` under `CLAUDE_PROJECT_DIR`, computes its class from `governance/project/criticality.yaml` (the same rule as `ticket_criticality`: the highest matching rule, `allowed_paths` and `profile`, the ticket `class` key never read), and lets a spawn that names `opus` or a `claude-opus-` model through only when an exceptions entry names that subagent type and model and, when the entry has `class: C3`, the ticket is C3. `governance/project/model-exceptions.yaml` lists independent-test-designer, engineer, independent-auditor and qa-engineer, each with `class: C3` and a `decided` text naming DEC-1214 K1. A refusal exits 2 and names the reason: the ticket and its class when it is not C3 (saying Opus is for C3 work only), no `Task:` line or more than one different id (the class is unreadable, so Sonnet), a ticket or rubric that cannot be read, or no exception for that type and model. A spawn naming Sonnet or no model is let through whatever the ticket. Verify: the hook run as a subprocess on a JSON event, for a C3 ticket, a C2 ticket, no Task line, two Task lines with different ids, a missing ticket file, an unlisted type, a Sonnet spawn and a spawn with no model; and a test that the hook and `ticket_criticality` give the same class for the real rubric on a table of allowed_paths. [DEC-1214 K1; DEC-1212 (2)]'
  - 'S6 No fork for helper work, by the hook: a spawn with `subagent_type` `fork` (tool name `Agent` or `Task`, with or without a model) is refused with exit 2 and a message that names "a fresh helper from a written brief" and DEC-1212 (4); only an exceptions entry for `subagent_type: fork` lifts it; every other subagent type is judged as before. Verify: the hook on four fork events and on a general-purpose spawn. [audit 09 item 4; DEC-1212 (4)]'
  - 'S7 The 5-minute prompt cache is kept for launched workers and checked: every worker launch (engineer, independent-test-designer, independent-auditor, qa-engineer, product-spec, research) keeps `CLAUDE_CODE_PROMPT_CACHE_TTL=5m` (set since 7f6aaaeb8, audit 09 item 8) in the env block of its `--settings` and in the CLI process environment, and its launch record holds `cache_ttl` `5m`; no other cache variable is added (W2-153 F2 pins the built arguments); a lead session started by the launcher does not get it (a lead waits on long runs and would pay a full rewrite after five idle minutes) and has no record. Verify: planted launches on the stub CLI of one worker role per listed role and of a lead, reading the settings text, the process environment and the record. Evidence, recorded by the lead in the ticket on CLI 2.1.327: one call with `CLAUDE_CODE_PROMPT_CACHE_TTL=5m` wrote 35,269 cache tokens all in the 5-minute tier (`FORCE_PROMPT_CACHING_5M=1` the same, 35,036), one with neither wrote 10,441 all in the 1-hour tier. [audit 09 item 8; DEC-1212 (4)]'
  - 'S8 No inbox waiter and no idle-check wake-up hook is written by the product: the hooks the product ships (`template/.rulesync/hooks.jsonc`, `template/governance/kernel/settings.json`, this repository `.rulesync/hooks.jsonc` and `.claude/settings.json`) and the `--settings` of a worker launch hold no hook whose command names `stop_waiter_check`, `stop_idle_check`, `gov session-watch` or `gov msg wait`; and a worker launch whose repository settings file (`.claude/settings.json` or `.claude/settings.local.json`, the files the launcher already judges) holds such a hook in a `Stop`, `SubagentStop` or `UserPromptSubmit` entry is refused with `LAUNCH_REFUSED` naming the file and the command. Verify: a test per shipped file; a planted launch for each of the four commands, each refused; a launch with the kernel hooks only starts. [audit 09 item 3; DEC-1212 (4)]'
  - 'S9 The rules above hold under the owner temporary Fable substitution (DEC-1215; `governance/project/model-substitution.yaml`, active until 2026-11-22T09:00 London) and are unchanged without it: while it is active, the hook judges a spawn naming `fable` or `claude-fable-5-2` exactly as it judges Opus (an exceptions entry naming `opus` covers it; an entry with `class: C3` needs a C3 ticket by the same `Task:` line, with the same refusal reasons), still refuses a spawn naming Opus with the Fable hint, and a fork is refused as in S6; `gov launch` takes the substituted model for an Opus table entry (the record names `claude-fable-5-2`) and, for a caller `--model claude-fable-5-2` on a role whose exceptions entry names `opus`, applies S4 as for Opus; while it is active a caller `--model claude-opus-*` is refused by the launcher as the hook refuses an Opus spawn (naming DEC-1215 and fable), even with an exceptions entry naming `opus`; with no substitution file, or `active: false`, or a passed `until`, Fable is refused by both as any other non-Sonnet model. Verify: the hook and the launcher on a project planted with an active substitution file, an inactive one and one past its `until`. [DEC-1215]'
  failure:
  - 'F1 Unreadable means Sonnet and never a crash: the hook given an exceptions file that does not parse, a criticality file that does not parse or is missing, a ticket whose front matter cannot be read, or a project folder with no `.tickets`, refuses a spawn naming Opus (exit 2, the reason in the message) and lets a Sonnet or no-model spawn through (exit 0, nothing on stdout); an event that is not JSON, or for another tool, exits 0. Verify: each fault planted in turn on the hook subprocess. [DEC-1214 K1]'
  - 'F2 No usage brake or budget is added: a worker launch with a plant of `log/usage.txt` or any plan reading at 100 percent starts as before with the same record, and neither the launcher nor the hook reads a usage file (the owner removed rationing on 2026-11-18). Verify: the planted launch with a 100 percent reading; a scan of `src/gov/launch/` and the hook for `usage.txt`, `spend.jsonl` and `usage_log`: none. [NIGHT-COMMON; DEC-1212 (4) as the owner changed it]'
  - 'F3 A role file with a missing or malformed line still fails its check, and a table line whose C0 or C1 entry is missing is refused by the reader as before. Verify: W2-33 F2 cases and the W2-184 line cases stay green. [DEC-1120 (2)]'
non_goals:
- 'One plan reading an hour at most (the `EVERY` floor of `usage_log.sh`): that file is an untracked scratch tool of the CTO main tree (`.gov-runtime/scratch/orchestrator/tools/`, ignored by git), so no commit of this branch can hold it; the lead gives the one-line patch in its return.'
- 'The models of the proving runs and of the operator session: they are started by scratch scripts and the owner own settings, outside `gov launch`.'
- 'Any usage brake, daily budget or plan-point reservation (the owner removed rationing on 2026-11-18).'
- 'The Haiku default for C0 helpers: the hook still names Sonnet as the only helper model; a Haiku helper stays an exceptions-file matter.'
- 'A live per-launch check of the cache tier (the lead checked it once on this CLI; the record states the setting).'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [EMERGENCY-2 3.5, EMERGENCY-2 6.3, DEC-1120, DEC-1212, DEC-1214, docs/emergency-2/audits/04-tickets-and-rubric.md, docs/emergency-2/audits/09-usage-last-two-days.md, DAEO-5rgj, DAEO-lrre, DAEO-6f0s]
acceptance_tests:
  path: tests/acceptance/W2-201/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-201: the rubric in code (K1, RT-8) and audit 09's usage rules held by code

A new feature (the CTO's brief of 2026-11-18 night; DEC-1214 K1, DEC-1212 (2) to (4)). The role files are kernel text
(`template/governance/kernel/roles/**`, C3): the CTO approves their change by naming it in the brief (EMERGENCY-2 3.5).
This ticket is C3 itself, so its test designer and engineer run Opus.

## Interface

- **Role files.** The values of S1. The generated copies (`.rulesync/subagents`, `template/.rulesync/subagents`,
  `.claude/agents`) change with the kernel file wherever a copy check holds them equal (W1-28, W1-33, W2-153 S3).
- **`governance/project/criticality.yaml`.** The rules of S2 in the file form `gov.launch.criticality` already reads
  (`version`, `default`, `opus`, `rules`); no new key.
- **`governance/project/model-exceptions.yaml`.** `exceptions: [{subagent_type, model, decided, class?}]`; `class` is
  optional and, when `C3`, limits the entry to C3 tickets. `model` is an alias (`opus`) or a model id; `opus` matches
  every `claude-opus-*`. One reader rule for the launcher and the hook (the hook stays standalone: `python3 -I`,
  stdlib and yaml only; a test holds the two equal).
- **The hook** (`.claude/hooks/agent_model.py`): the order is fork, then model. Ticket found from the spawn prompt line
  `^Task: (DAEO-[a-z0-9]+)\s*$` (every such line; all the same id, else unreadable). Class by the same rule as
  `ticket_criticality`. Exit 2 with the reason on stderr; any other outcome exit 0.
- **The launcher** (`src/gov/launch/launcher.py`): the exceptions route in `_rubric` beside trial and promotion; the
  worker env gains `FORCE_PROMPT_CACHING_5M=1`; the record gains `cache_ttl` and `exception`; the repository-settings
  check gains the wake-hook refusal.

**Evidence of the cache setting (the lead, 2026-11-18, CLI 2.1.327, one `claude -p` call per case on Haiku):** with
`CLAUDE_CODE_PROMPT_CACHE_TTL=5m`, `cache_creation` = `{ephemeral_1h: 0, ephemeral_5m: 35269}`; with
`FORCE_PROMPT_CACHING_5M=1`, `{ephemeral_1h: 0, ephemeral_5m: 35036}`; with neither, `{ephemeral_1h: 10441,
ephemeral_5m: 0}`. Both variables work on this CLI; the launcher keeps the first (already in the base).

**Fix at the land, 2026-11-19 02:17 (the CTO; the merge was at 02:15; EMERGENCY-2 4.2):** the helper rule read a spawn's ticket only from the project's own `.tickets/`, but a lead writes its feature as a ticket on its own branch, so every running C3 lead's Fable helpers would have been refused from the moment this merged (five leads were running, their tickets W2-200, W2-203, W2-204, W2-205, W2-206 on their branches). The hook now reads a ticket the project does not hold from the repository's other worktrees (`git worktree list`); the project's own copy wins; a ticket in no worktree is still unreadable (Sonnet). The failing tests first: `tests/unit/hooks/test_w2_201_agent_model_worktree.py` (2 of 5 red before, 5 green after; the hook's 65 older unit cases green).

**Closed at the land, 2026-11-19 02:28 (the CTO; EMERGENCY-2 4.3 step 5):** merged as bb3a7bb3e (branch `e2/k1-usage` at d5b7caaad), with the fix above (c3c5a836f). On the merged tree, through the slot with workers: `tests/acceptance/W2-201`, `W2-33`, `W2-184`, `W2-153`, `W2-60a`, `W2-60b`, `W2-195`, `W2-156`, `W1-33`, `tests/unit/launch`, `hooks`, `adapters`, `optin`: 2,724 passed, 24 skipped, and 1 collection error that was the CTO's own new unit file (it imported its sibling by bare name; fixed, `tests/unit/hooks` then 201 passed); `gov accept W2-201`: 240 passed, 0 failed. The CTO's rulings on the lead's lines: the QA engineer's C2 review on Sonnet stays (DEC-1214 K1, "C2 auditors included"); the auditor and the QA engineer stay in the exceptions file for C3 only; the senior engineer's model goes to the owner as one line (K1-1); a W2-184 promotion's Opus under DEC-1215's substitution is a fix still owed in this record. The usage logger's one-hour floor (a scratch tool, not held by this ticket's code) was applied by the CTO at 02:17.
