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
- .claude/skills/orchestration/SKILL.md
- docs/emergency-2/audits/04-tickets-and-rubric.md
- docs/emergency-2/briefs/NIGHT-COMMON.md
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

## Fix: what becomes a ticket (DEC-1219 (5))

A fix in this feature, not a new ticket (EMERGENCY-2 4.2; audit 4 Table 3 rows 1 to 4, guardrail 3: it flags, it never
refuses). The owner, 2026-11-19 (DEC-1219 (5), (6)): half of the rubric was in code (model and effort, S1 to S4) and half
was not: what becomes a ticket. A lead can only be launched against a ticket, so a fix to a closed feature or a chore had
no way to start. This fix puts it in code, in release 0.1.4. From now on a new ticket opens only for a new feature
(DEC-1219 (6)). The CTO approved the kernel text of X5 by naming it in the lead brief (EMERGENCY-2 3.5). The test
designer and the engineer run Opus: `src/gov/launch/**` and `src/gov/queue/**` are C3 and the prompts carry `Task: DAEO-k1us`.

**Interface.** `gov launch <role> <ticket> --fix "<one line>"` and `gov launch <role> --chore "<one line>"`, both before
`--`. `<ticket>` becomes optional on the command line. A usage error, exit 2, before the launcher, as W2-184 R1 does it
(nothing read, started or recorded; the launcher refuses the same with `LAUNCH_REFUSED` as the second fence): `--fix` and
`--chore` together; `--fix` with no ticket; `--chore` with a ticket; neither flag and no ticket; a blank line. The launch
record gains two keys, `kind` and `kind_line`: an ordinary launch says `kind` `feature` and `kind_line` null (a launch on an
in_progress ticket is a feature's, as today). `--plan` and `--tests-worktree` take `--fix` too (the failing test of a fix
is written first, by a test designer, in a tests worktree of the closed ticket); `--plan` takes `--chore`, `--tests-worktree`
does not (no ticket). A lead has no launch record (S7), so its kind is carried in its env (X3).

**X1 A fix launches under its owning ticket, closed or not.** `gov launch <role> <ticket> --fix "<line>"` starts the role
on `<ticket>` when the ticket file exists, whatever its status (`closed`, `open`, `in_progress`); an unknown ticket is
refused as today. The launch record holds `kind` `fix`, `ticket` the owning ticket, and `kind_line` the line; model and
effort come from the rubric for that ticket's class as for any launch (the class from its `allowed_paths` and `profile`,
by `ticket_criticality`), with the same sources (`by criticality`). The role still keeps to its own ticket where it did
(`_check_ticket`'s role rule); nothing else about a worker launch changes (gate, one writer, repository settings,
the S4 refusal of another model). Verify: a planted `closed` ticket with C3 and C2 paths and an engineer launched with
`--fix` on the stub CLI: it starts, the record has the three fields, the stub received `--model` and `--effort` of that
class (Opus on C3, Sonnet on C2); `--plan --fix` prints the role's default line; `--tests-worktree --fix` makes the tests
worktree of the closed ticket; the same launches without `--fix` are refused as today (`is not in_progress`).

**X2 A chore launches with no ticket.** `gov launch <role> --chore "<line>"` starts the worker with no ticket: no ticket
file is read, `GOV_TICKET` is absent from the `--settings` env and from the CLI process (unset, not empty), the launch
record holds `kind` `chore`, `kind_line` the line, `ticket` null, `ticket_class` null, `criticality` null and `rubric`
null; model and effort are the role file's `Launch default` (`model_source` and `effort_source` `role default`, whatever
the class table says); the session has no run folder of its own and no ticket-based spend brake. The gate, the one-writer
check, the repository settings and the refusal of another model (S4, with no class to lift it) apply as for any launch.
Verify: a planted launch of an engineer with `--chore` on the stub CLI and no ticket id: it starts, the record says so,
the stub's `--settings` and process env hold no `GOV_TICKET`, the stub received the role default's model and effort; a
second planted record of another ticket in the folder is not read as this chore's.

**X3 A lead launches the same way.** `orchestrator` and `lead` take `--fix` and `--chore` as workers do. `--fix`: the
ticket must exist, whatever its status, and the plan's check (`check_lead`: in the ready list, waits met) is not applied,
because a fix is not planned; `--chore`: no ticket, no plan check. A lead writes no record, so the kind goes in its env:
for a fix or a chore only, `GOV_LAUNCH_KIND` (`fix` or `chore`) and `GOV_LAUNCH_LINE` (the line) are added to its
`--settings` env and the CLI process env; `GOV_TICKET` is the owning ticket for a fix and absent for a chore. A chore
lead's registry entry and inbox address use the label `chore-<8 hex>` where the ticket would be. A lead launch without
the flags is unchanged (same env, same plan check, same refusal of a closed ticket). `--reason`, `--trial`,
`--owner-named` and `--projection-usd` stay refused for a lead, with `--fix` and `--chore` as with any launch. Verify:
as X1 and X2 for the `orchestrator` role on the stub CLI, reading the stub's env; a planted `closed` ticket outside the
ready list launches with `--fix` and is refused without it; the gate and `gov pause` still stop it.

**X4 A new ticket that is not a feature is flagged at the landing, never refused.** For each candidate, `gov queue` lists
the ticket files `.tickets/<id>.md` that the candidate's change adds (added between its `since` and its tip: a path that
is new, not an edit of one at the base). A new ticket is a feature when it holds a spec and KPIs. The ticket schema has
no spec key, so the fields read are: **KPIs** = `kpis.success` holds at least one line with a `verify` (the mapping form's
non-blank `verify`, or the string form's text containing `Verify:`); **spec** = the ticket's body after its front matter
is not blank (the template puts Problem, Approach and Interface there). For one that lacks either, or whose front matter
cannot be read, the landing records one notice `NEW_TICKET_NOT_FEATURE <id>: <what is missing>` (`<what is missing>`:
`no kpis.success line with a verify`, `no spec (the ticket's body is empty)`, `front matter unreadable`, joined by `; `),
prints it as one line on stderr, and lands anyway: the answer's new key `ticket_notices` (`{ticket, id, code, notice}`
each, the same in `queue.json`, the dry run's answer and the landed ticket's close record) and the exit code are those
of a landing without it. A new ticket that is a feature gives no notice; an edited existing ticket gives none; a branch
that adds no ticket file gives `ticket_notices` `[]`. Verify: three planted branches through `gov queue` (and its
`--dry-run`): a new ticket with no KPI verify and no body (notice naming both, landed, exit as without), a new ticket with
both (no notice), an edit of an existing ticket file (no notice).

**X5 Words match code.** The kernel lines that tell a CTO or lead how to launch work say: a new ticket only for a new
feature; a fix launches under its owning ticket with `gov launch <role> <ticket> --fix "<line>"`; a chore with
`gov launch <role> --chore "<line>"` and no ticket. Changed lines only, in: `template/governance/kernel/roles/orchestrator.md`,
`senior-engineer.md` and `ticket-lead.md` (the `Tools:` line, where `gov launch` is named) and
`template/governance/kernel/skills/orchestration/SKILL.md` (`## Parallel tickets`, one line), each with its copies where a
copy check holds them equal (`.rulesync/subagents`, `template/.rulesync/subagents`, `.claude/agents`, the skill's copies
under `.rulesync/skills`, `template/.rulesync/skills` and `.claude/skills`), regenerated with the project's generator,
not by hand where it generates. Verify: each of those files holds the three statements (the strings `new ticket only for a
new feature`, `--fix` and `--chore` in the line that names `gov launch`, or in the skill's line); a copy equals what its
kernel file generates; `gov accept W2-201` and the copy checks (W1-28, W1-33, W2-153 S3) stay green.

**Landed:** merged into `w2/integrate` at `2031f758d` on 2026-11-19 (the CTO); on the merged tree W2-201, `tests/unit/launch`, `tests/unit/queue`, W2-202, W2-206, W2-195 and `tests/unit/optin`: 1,576 passed. Follow-up X6 to X8 (a fix under a closed ticket lands and relaunches): lead `rubric-tickets-2`.

## Fix, part 2: a fix under a closed ticket lands, relaunches and has a run folder (DEC-1219 (5)), lines X6 to X8

The first part (X1 to X5) lets a fix start under a closed ticket, but the owner's model says a fix is recorded in its owning
ticket, open or closed (EMERGENCY-2 4.2), and three places still treat a closed ticket as the end: `gov queue` refuses it
(`TICKET_CLOSED`), the relaunch of a dead session restarts it as a plain launch (which a closed ticket refuses), and a worker
on a closed ticket gets no run folder. The test designer and the engineer run Opus (`src/gov/queue/**` and
`src/gov/launch/**` are C3; the prompts carry `Task: DAEO-k1us`). The README maps X6 to X8 as `S15` to `S17`, as it maps X1 to
X5 as `S10` to `S14`. "The relaunch" is `gov.dispatch.relaunch` (the watch pass's relaunch of a dead registry entry); there is
no `gov relaunch` command.

**X6 A fix branch under a closed ticket lands through `gov queue`; a plain branch on a closed ticket is still refused.** The
signal is a commit trailer, because the launch record's `kind` is machine-local (`.gov-runtime/launches`) and a branch carries
nothing of it. A branch is a **fix landing** when the ticket at the integration head is `closed` and at least one commit of
`<since>..<tip>` has both a `Task: <the ticket>` trailer and a `Fix: <one line>` trailer (the line is the first such
commit's `Fix:` value, non-blank). Any other branch for a closed ticket is refused `TICKET_CLOSED` as today (a branch whose
commits carry `Task:` of the closed ticket and no `Fix:` is a plain branch; so is a `Fix:` trailer on commits of another
ticket's `Task:`). A fix landing runs as any candidate does (G-1, the path and ticket notices, the impact-selected tests, and
the ticket's acceptance folder through the runner of `gov accept`: the folder named by the ticket file at the integration
head or the tip), and a red it causes keeps it out of the batch as for any candidate. It lands with **no second close**:
`tk close` and `CLOSE_RECORD_FAILED` on a closed ticket are not reached, the ticket file stays `closed`, and the landing's
close commit (subject `fix: <ticket> (gov queue landed at <tested12>)`, `Task: <ticket>`) appends to the ticket's close
record `docs/close/<ticket>/CL-<ticket>.md` one entry of its front-matter key `fixes` (a list, created when the record has
none; each entry `{line, branch, tip, tested, landed}`: the `Fix:` line, the branch name, its tip, the tested commit, the
UTC time) and one body line `- fix landed: <line> (<branch> @ <tip12>)`, keeping everything else of the record as it was;
where the ticket has no close record, one is written with `fixes` only the way the landing writes a record, and nothing
else of a first close. The answer's `closes` entry for it adds `fix: true` and `fix_line`; `queue.json` says the same. The
dry run's `closes` stays empty for an ordinary ticket (W2-206) and holds only the entry each fix would get, with `commit`
and `close_record` null, `fix: true` and `fix_line` (a dry run changes nothing and appends nothing); a landed feature's
entry is as today. A second fix on
the same ticket lands the same way and appends a second entry. A fix `Fix:` trailer on an `open` or `in_progress` ticket's
branch is an ordinary landing (the ticket closes as today; no `fixes` entry). Verify: planted branches through `gov queue`
and its `--dry-run` on W2-115b's planted project with a closed ticket that has an acceptance folder: (a) a fix branch
(`Task:` + `Fix:`) lands, the ticket stays closed, the close record gains `fixes` with the line and the body line, the
exit code is 0, a second fix branch appends a second entry; (b) a branch whose commits carry the closed ticket's `Task:` and
no `Fix:`, and a branch with `Fix:` under another ticket's `Task:`, are each refused `TICKET_CLOSED`, exit 1, nothing moved;
(c) a fix branch whose change breaks the ticket's acceptance folder or a selected test is not landed; (d) the dry run of
(a) answers the same, changes no ref or file and appends nothing; (e) a `Fix:` branch on an `in_progress` ticket closes it
as today.

**X7 The relaunch keeps the kind.** The launch's `kind` and `kind_line` are carried in the registry entry (`kind`,
`kind_line`: for a worker from the plan, for a lead from `build_lead_settings`'s env values; a feature's entry holds
`feature` and null, or neither key), and `relaunch.spawn` starts the same kind: a `fix` entry is
`gov launch <role> <ticket> --fix "<line>" --root <repository> -- --resume <session id> "<text>"` and a `chore` entry is
`gov launch <role> --chore "<line>" --root <repository> -- --resume ...` with no ticket (the chore's `ticket` in the entry is
its `chore-<8 hex>` label, which is not a ticket and is not passed), for a worker and for a lead; a feature entry, or an
entry from before this change with neither key, spawns exactly as today (no flag). The claim, the idempotence, `twice` and
`unresumable` rules, the notify address and the checkpoint text are unchanged (a chore has no checkpoint: the
`FALLBACK_STEP` text, which names no ticket file for it). Verify: planted dead registry entries (the form W2-205's
relaunch tests plant) of a worker fix, a worker chore, a lead fix, a lead chore and a feature: the command the pass spawns
(the stand-in `gov` that records its argv) holds `--fix <line>` with the owning ticket, `--chore <line>` with no ticket id,
the same for the leads, and neither flag for the feature and the old-form entry; a relaunched fix launch (run on the stub
CLI through `gov launch`) is not refused and its record holds `kind` `fix` and the same `kind_line`.

**X8 A worker fix gets a run folder.** A worker launched with `--fix` on a closed (or open) ticket gets the run folder an
`in_progress` ticket's worker gets: `runs.folder` takes the launch's kind and, for `fix`, does not judge the ticket's
status (every other rule of it stays: the plain name, the root, the project not inside it, the name given once; a feature
launch on a ticket that is not `in_progress` still gets none, and a chore none, X2); the launcher makes it with its marker
when it is not there (reusing the ticket's earlier folder where one is marked as this repository's, never removing or
rewriting what it holds) and hands it to the session as an `in_progress` worker's. Verify: a planted `--fix` launch of an
engineer on a closed ticket (the stub CLI, a planted runs root): the folder exists under the root with its marker naming the
repository, the same launch repeated reuses it, and the session's env/settings carry it as an `in_progress` ticket's launch
does; the same launch without `--fix` on the closed ticket is refused as today; `--chore` makes none.

## Fix, part 3: the model rubric of DEC-1225 in code (a fix under W2-201; lead `models-rubric`, 2026-11-22), lines R1 to R5

The owner's DEC-1225 changes the rubric W2-201 put in code (S1, S3, S4, S5, S9): Opus only for each app's CTO and the senior
engineer; every other agent Sonnet, C3 work included; one exception, a comprehensive audit the owner asks for, on Opus; no
session runs Fable. The test designer (Sonnet, `Rewrite-Reason: DEC-1225`) revises the cases that pin the old table (S1's
`TABLE`, S3's C3 Opus, S4/S5's `class: C3` entries and C3 Opus helpers, S9's whole substitution, the W2-184 and W2-60a cases that
read C3 Opus or C0 Haiku from this repository's role files); the new cases below are written red on the base. Decisions the lead
took where the brief leaves a choice: the `Launch by criticality` line goes from every role file (Sonnet at every class, C0
Haiku included: the helper hook refuses Haiku already, and DEC-1225 says every other agent runs Sonnet); the promotion and the
second-review probe keep their records, their effort and their review-round rules but no longer choose Opus (the model stays
the table's, Sonnet) unless an exceptions entry covers it; DEC-1215's substitution file and every reader of it are removed.

**R1 The role files carry the new table.** In `template/governance/kernel/roles/*.md`, and each copy the portability check holds
equal to them (`template/.rulesync/subagents/`, `.rulesync/subagents/`, `.claude/agents/`, regenerated with the project's
generator, `gov.adapters.portability`'s `rulesync generate` step), `orchestrator` and `senior-engineer` carry `Launch default`
`claude-opus-5-5`, effort high, and no table line; every other role file (`ticket-lead`, `engineer`,
`independent-test-designer`, `independent-auditor`, `qa-engineer`, `product-spec`, `research`) carries `Launch default`
`claude-sonnet-5-5`, effort high, and no `Launch by criticality` line (so Sonnet at every class and profile; no
`claude-opus-5-5` and no `claude-haiku-5-5` is left in a role file but the two Opus roles' default). `independent-auditor`'s
`Model tier` line says an Opus audit is only the exceptions file's entry for a comprehensive audit the owner asked for
(DEC-1225 (2)), not a role default. Each changed role file's `Version` goes up by one minor. `governance/project/criticality.yaml`'s
comments say a class no longer picks a model (the key `opus` stays for the file's form and names the model an exceptions entry
may cover), and audit 4's Table 3 (`docs/emergency-2/audits/04-tickets-and-rubric.md`, the rubric's source) carries the same
table with a note naming DEC-1225. Verify: a test reads every role file with `gov.launch.role` (`launch_default`,
`read_by_criticality`) and compares the model and effort per role with this table, for the kernel file and for each copy
(a copy that differs from the kernel file fails it); a scan of `template/governance/kernel/roles/`, the three copy folders and
`criticality.yaml` for `claude-opus-5-5` and `claude-haiku-5-5` finds them only as the two Opus roles' default and in
`criticality.yaml`'s `opus` key; `gov adapters` portability check is green on the tree.

**R2 `gov launch` picks the model by role.** A lead (`gov launch orchestrator|lead <ticket>`, with `--fix` or `--chore`) is
started with `--model claude-sonnet-5-5` added by the launcher (the CLI's own default, the CTO's Opus, is never its model); a
worker's model is its role file's default (Sonnet) at every class, a trial's model and a promotion's or probe's included
(a trial file naming a model other than Sonnet is refused `LAUNCH_REFUSED` unless an exceptions entry covers it; a promotion
or probe keeps its record and effort rule and the table's model). `--model` after `--` naming any model other than the session's
is refused `LAUNCH_REFUSED` naming DEC-1225 and `governance/project/model-exceptions.yaml`, for a lead and for a worker, unless
the exceptions file has an entry for that role and model whose limiter (R3) the launch meets; a `--model` naming Sonnet is not
doubled; a model naming Fable (`fable` or `claude-fable-5-2`) is refused whatever the file holds (no session runs Fable, DEC-1225
(3)). The skill evaluation harness's default model (`src/gov/skilleval/harness.py`, `DEFAULT_MODEL`) is Sonnet. Verify: on the stub
CLI, planted launches of a lead, of a lead `--fix`, of a lead `--chore`, of a C3 engineer and of a C3 test designer record or
pass `claude-sonnet-5-5` (the record's `model` and the stub's received `--model`); `--model claude-opus-5-5` for an engineer, for
a test designer and for a lead is refused with no session and no record; `--model claude-fable-5-2` and `--model fable` are
refused for each, also with an exceptions entry naming them; `--model claude-sonnet-5-5` starts one session with one `--model`;
a trial naming Opus is refused; a ticket with two failed probe records (a promotion) on an auditor launches Sonnet, its record
keeping `promotion`.

**R3 The helper rule's Opus exception is limited to the audits the owner asks for.** An exceptions entry that names Opus lifts
the refusal only when it carries a limiter and the spawn or launch meets it: `class: C3` (as before), `task: <id or list>`
(the spawn prompt's one line `Task: <id>`, or the launch's ticket, is one of them) and `decision: <DEC-id or list>` (the spawn
prompt carries a line `Decision: <DEC-id>`, or the launch is given `--owner-named <DEC-id>`, one of them); every limiter an
entry carries must be met; an entry that names Opus and carries none lifts nothing. `governance/project/model-exceptions.yaml`
holds one entry, `independent-auditor`, `opus`, `decision: [DEC-1230]`. The hook (`.claude/hooks/agent_model.py`) and
`gov.launch.model_exceptions` read it by the same rule. A refusal exits 2 (the hook) or `LAUNCH_REFUSED` (the launcher) and says
which limiter is not met. Fable is refused by both with no Fable hint and no substitution reading: DEC-1215's
`governance/project/model-substitution.yaml` is deleted, with `roles.substitute`, `roles.substitution_active`, the hook's
`substitution` and `model_matches`' substituted case, and the CTO's start script no longer reads it (it starts the CTO on
`claude-opus-5-5`). Verify: the hook as a subprocess on events for an `independent-auditor` naming `opus` and `claude-opus-5-5`:
with a prompt carrying `Decision: DEC-1230` (let through), with none (refused, naming the limiter), with `Decision: DEC-1299`
(refused), with `Task:` only (refused); an `engineer` naming Opus (refused: no entry); an entry with `task: DAEO-x` met and
unmet; an Opus entry with no limiter lifts nothing; `fable` and `claude-fable-5-2` refused for every type with an entry naming
them, the reason carrying no word `substitut`; the launcher's matching cases with `--owner-named DEC-1230` (an auditor
`--model claude-opus-5-5`, started and recorded `model_source` `exception`) and without it (refused); no file
`governance/project/model-substitution.yaml`, and no `substitut` in `src/gov/launch/`, the hook and `start_cto.sh`.

**R4 The memory measure's reader and grader run Sonnet.** `src/gov/memaudit/judge.py`'s `READER` and `GRADER` are
`claude-sonnet-5-5` (`CHECK` already is); the models the call passes (`claude.py`'s `--model`), the shipped briefs under
`src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/` that name `claude-opus-5-5` and the shipped
`indep-walls/kinds.yaml` models are Sonnet; the judged run's record (`FIGURES.json` and the run's declared record) names the
reader, grader and checker models, so DEC-1098's figures stay comparable only from the first fresh 80 graded on Sonnet, which is
the new baseline (DEC-1225 (4)); W2-81's runner already forces Sonnet. Verify: a unit test on the call the judge builds (the stub
`claude` records `--model`) for a reader, a grader and a check, each `claude-sonnet-5-5`; `FIGURES.json` of a planted judged
run holds `models` with the three; no `claude-opus` in `src/gov/memaudit/` or the shipped briefs and kinds file.

**R5 EXAMIN's copy is listed.** The lead reads `/home/usain/gov-os-runs/W2-27/examin` (read only) and returns what carries the old
table: its kernel role files and copies (reached by `gov update` to 0.1.5), its `.claude/hooks/agent_model.py` and
`governance/project/model-exceptions.yaml`, its start scripts; for what the kit does not carry, the exact change for the EXAMIN
CTO. Verify: the list in the lead's return, each item with its path, the line and the change; no file of that folder is written.

## Fix: the hook writes the model into the spawn (F13, fixes-015a)

Found 2026-11-22: a spawn that named no model relied on CLAUDE_CODE_SUBAGENT_MODEL, which the harness does not always read, so such a helper could run the session's model. No test caught it. Required: `.claude/hooks/agent_model.py` writes model `sonnet` into every Agent spawn that names no model, through PreToolUse `updatedInput` with the full input kept; an Opus spawn the exceptions file allows keeps its model; Fable stays refused; no kit copy of the hook exists and none is added. Kind: a fix, no new ticket; the ticket stays closed. Failing test first: `tests/acceptance/W2-201/test_w2_201_fix_f13_model_written.py` (15 cases); code `.claude/hooks/agent_model.py` (`write_model`; a non-object `tool_input` is left alone); units `tests/unit/hooks/test_w2_201_agent_model.py` (`written`, the no-model cases for Agent and Task). Result: the 15 cases and the units are green. Four older acceptance files of this ticket still assert that a no-model spawn prints nothing (`test_w2_201_f1_hook_unreadable.py`, `test_w2_201_s5_hook_class.py` cases `*-no-model`, `test_w2_201_s6_hook_fork.py::..[no-model]`: 11 cases) and are red against the line this fix states: they need the test designer's revision (the builder never edits them).

## Fix: connectors off in every launched session; leads run Sonnet at medium; a role file's other model never launches (F1 launch side, F14, F19; fixes-015a; DEC-1232, DEC-1233, DEC-1236 (2))

Found by the E2 audits (3: claude.ai connectors reach a launched session; the rubric audit: leads at high, a role file's
Opus table still launches Opus in an adopted repository). No test caught them. Required. F1: `gov launch` starts every
role, leads included, with `--strict-mcp-config` and an `--mcp-config` built from the role file's `- **MCP tools:** a, b`
line (no line is an empty list; every role's is empty today), sets `ENABLE_CLAUDEAI_MCP_SERVERS=false` in the CLI process's
environment, and accepts a caller's `--mcp-config` after `--` only when every server it holds is in that list (named
refusal otherwise). F14: a ticket, fix or chore lead runs Sonnet at `--effort medium`; no other role's model or effort
changes. F19: `_rubric` replaces any model that is not Sonnet, from a table or a default line, with the rubric's Sonnet
whatever the role file says; only an exceptions entry runs another model. Kind: fixes; the ticket stays closed. Failing
tests first: `tests/acceptance/W2-201/test_w2_201_fix_f1_connectors.py`, `..._fix_f14_lead_effort.py`,
`..._fix_f19_rubric_model.py` (README "Fixes of fixes-015a"), `361802ceb`; code `src/gov/launch/launcher.py`
(`_mcp_args`, `_lead_effort_args`, the rubric clamp), `src/gov/launch/role.py` (`mcp_tools`), `83b73ba96` (F1) and `4c95fcc08`
(F14, F19: `ticket-lead.md` and its three copies say medium; `criticality.yaml`'s comment; the dispatcher's dead-man push
and `deadman.py` launch Sonnet, not Haiku; `LEAD-w2-common.md`'s `--model claude-opus-5-5` lines follow the rubric); the
planted Opus and Haiku role tables of `tests/unit/launch` and of W2-184, W2-33 and W2-60a moved to Sonnet, each file under
a `# Rewrite-Reason: DEC-1225 / DEC-1236 (2): F19` comment; units `tests/unit/launch/test_fixes_015a_connectors.py`.
Open: `tests/acceptance/W2-60a/test_w2_60a_kept_out.py::test_the_line_keeps_connectors_and_user_level_settings_out`
asserts the launch line carries no `--mcp-config`, which F1 now requires (an empty one); it is the old reading of "no
connector" and needs the designer's revision (not edited here).

## Fix: fix-w2-56 (W2-56's S5 and S6 cases after DEC-1225 and DEC-1232 (6))
Seven of W2-56's 154 cases were red in the third run of the 0.1.5 full suite. No product bug: the launcher behaves as
DEC-1225 and F1 say; the two test files held the old readings. S5 (`test_w2_56_environment.py`, `1c8eb1ff8`): the
session's `CLAUDE_CODE_SUBAGENT_MODEL` is the launcher's own Sonnet helper model (DEC-1225), never the parent's planted
value, which differs from it, so a leak stays detectable (six cases). S6 (`test_w2_56_refused_arguments.py`,
`e0a84c16c`): `--mcp-config` is refused when it names a server outside the role's list (case `rogue`); an empty
`{"mcpServers": {}}` holds none outside the list, F1 accepts it, and a new case pins that (DEC-1232 (6)). Both commits
by the independent test designer, each with a `Rewrite-Reason`. Green: `tests/acceptance/W2-56` (weekly),
`tests/acceptance/W2-201`, `tests/unit/launch`, `tests/unit/optin`: 1828 passed; `gov accept W2-201` exit 0, 649 passed.

## Fix: models and effort by role, from one table, held by code (MR-1, MR-2, MR-3; DEC-1246 (3)(b); INTEGRATION-PLAN rows 2-9, 2-10, 2-7; lead `models-by-role`, 2026-11-24)

Found by the integration plan (T-10 (c), R-4, R-5): the model and effort of a role stand in four places that can drift (role
files' `Launch default` lines, `LEAD_MODEL` and `LEAD_EFFORT` in the launcher, `criticality.yaml`'s `opus:` key with the
launcher's promotion and probe, three start scripts). No value changes (DEC-1236 (3)): CTO (`orchestrator` run by its own start
script) and `senior-engineer` Opus high; ticket, fix and chore leads Sonnet medium; `engineer`, `independent-test-designer`,
`product-spec`, `research`, `independent-auditor`, `qa-engineer` Sonnet high; a wide audit the owner asks for Opus high
(`independent-auditor` with `Decision: DEC-1230`); no Fable anywhere. The CTO approved the kernel text (the role files' model and
effort lines) by naming it in the brief. Required; the ticket stays closed. Code area `src/gov/launch/**`,
`governance/project/criticality.yaml`, `governance/project/role-table.yaml` (new), `template/governance/kernel/roles/*.md`.

**MR-1 The table in one file (2-9).** `governance/project/role-table.yaml`: `version: 1`, `rows: [{role, model, effort,
decided}]` for `orchestrator`, `senior-engineer`, `lead`, `engineer`, `independent-test-designer`, `product-spec`, `research`,
`independent-auditor`, `qa-engineer`, `audit-wide`; each `decided: DEC-1242 R-4` (or the DEC that set it). A copy ships in the kit
(`template/governance/project/role-table.yaml`, byte-equal). `gov launch` reads the row for the role when the file is present
(`lead` for a ticket, fix or chore lead; `orchestrator` is the CTO's row and the launcher still gives a launched lead the `lead`
row); the launch record names it (`model_source`/`effort_source` `role table`); with no table file the role file's `Launch default`
line is used as before (an adopted repository not yet updated). Each role file's `Launch default` line must equal the table's row (a
check in `gov.launch.role_table`; no role file may name another value). A table that cannot be read, repeats a role, holds a model
that is Fable, or a model/effort the launcher does not know refuses a launch (`LAUNCH_REFUSED`, fail closed). Changing a row in a
commit without the trailer `Decided-by: owner` is reported by `python3 -m gov.launch.role_table --check <range>` (`gov launch
--table-check [range]`), which the basis check calls for a range that touches the file. Verify: `gov launch engineer <ticket>` on the stub CLI
records `high` and `claude-sonnet-5-5` read from a planted table row whose values are then changed (the stub receives the changed
values); a lead gets `medium`; a commit that edits a row with no trailer is reported with the role, old and new value, one with the
trailer is not; each role file equals its row; a planted unreadable or Fable table refuses. Failure: a role file that says `medium` for
the engineer while the table says `high` is reported by the check and cannot launch an effort other than the table's.

**MR-2 Criticality no longer varies the model (2-10).** `governance/project/criticality.yaml` has no `opus:` key
(`gov.launch.criticality.load` accepts `version, default, rules`; a file that still carries `opus` is refused with a message naming
the key). The launcher's promotion (probe-record verdict) and probe (second review round on Opus) are retired: a C3 ticket launches its
engineer on Sonnet; a planted probe record or a review round of two or more changes neither model nor effort (no `max`), and an
explicit request for promotion or probe (`--trial` naming Opus without an exceptions entry, a caller's `--model claude-opus-*`) is refused as any other
non-Sonnet model. Criticality still gives the class, the profile and the review depth. The hook's class limiter (`class: C3`) still reads the class.
Verify: a planted C3 ticket launches its engineer, test designer and qa-engineer on Sonnet, high; a planted probe record with a promoting verdict and a
ticket in review round 2 launch Sonnet, not max; `criticality.yaml` has no `opus:`; `load` refuses a file with it; a promoting `--trial` on Opus is refused.
Failure: no launch record holds `model_source` `promotion` or `probe`.

**MR-3 The start scripts match the table (2-7).** `python3 -m gov.launch.role_table --scripts <dir>` (`gov launch --table-check --scripts <dir>`) prints each of `start_lead.sh`, `start_cto.sh`,
`start_audit.sh` with its `--model` and `--effort` beside the table's row (`lead`, `orchestrator`, `audit-wide`) and exits 0 when
they agree, non-zero when not (a `${EFFORT:-medium}` default is read as its value; an `--effort` read from the environment counts as its default).
`start_cto.sh` no longer calls the Fable substitution reader (the scripts are the CTO's: only that call is removed in this change). Verify: the
real three scripts agree and exit 0; a copy of `start_cto.sh` with `--effort medium` planted exits non-zero naming it and the table's value; a copy that
still names the substitution reader is reported. Failure: a script with no `--model` or `--effort` is reported, not skipped.
