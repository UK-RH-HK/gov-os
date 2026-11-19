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
