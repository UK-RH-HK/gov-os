# P1-ORCH-APPROVALS-1 — the orchestrator's approval discipline in the Gov OS itself (DEC-991 item 5)

## 1. Context
DEC-991 sets how this repository's CTO handles a command that could need the owner's approval: know the allow list;
by day ping first, then run; in the quiet hours never run it, queue it for the morning package; a hook refuses at
once in the quiet hours (ACT-QUIET-DENY-1); a dead-man's switch as the last net (ACT-DEADMAN-1). You asked where it
goes in the Gov OS's specs and KPIs, so every adopted product's orchestrator behaves the same.

## 2. What exists in the product today
- `template/governance/kernel/roles/orchestrator.md` (the orchestrator role file; W2-11 and W2-113 edit it; W2-33
  splits out the CTO's and the ticket lead's role files) says nothing about approvals or quiet hours.
- `template/governance/kernel/skills/orchestration/SKILL.md` (W2-11) covers the wave, decisions, stops and pings, not
  which commands prompt or what to do with them.
- The brief templates (`template/governance/kernel/templates/brief-*.md`, W2-11) carry no such rule.
- The kernel's hooks (`template/governance/kernel/hooks/`) have no `PermissionRequest` hook; W2-10 ("guardrails
  explain themselves, refuse once, then record") is the ticket closest to it.
- The quiet hours and the morning package are this project's rules (DEC-938, DEC-973), not product configuration.

## 3. Why it matters
An adopted product's orchestrator runs unattended too; one misjudged command freezes it the same way, and its owner
would hear nothing. EXAMIN's copy will be the first.

## 4. The options
- **(a) KPI edits to three existing tickets, no new ticket (recommended):**
  - **W2-11** (the orchestration skill and the brief templates), one KPI: the skill has an "approvals" section: the
    orchestrator reads its own allow list at session start (the settings files' allow, ask and deny rules, plus the
    host's known safety checks: for Claude Code, `.claude/` paths); before each command it classifies it (allowed, or
    could need approval); a call that could need approval is never chained to other work; by day it notifies the owner
    first, then runs it; in the project's quiet hours it never runs it and queues it (`.gov-runtime/approval-queue.jsonl`)
    for the morning package; the orchestrator brief template carries the rule. Test: a skill scenario per branch (day,
    night, chained command). About 1 to 2 hours inside W2-11's next round.
  - **W2-33** (the CTO's role file), one KPI line: the CTO role states the approval classes and the quiet hours as
    role defaults, read from the project's configuration (`quiet_hours`, `morning_package` time), so a product sets
    its own hours. About 30 minutes.
  - **W2-10** (guardrails), one KPI: the kernel ships the `PermissionRequest` hook (this repository's
    `permission_request.py` as the model): inside the configured quiet hours it refuses at once with an explaining
    message and queues the call; outside them it falls through; any error inside them refuses; every prompt is
    recorded; adoption wires it into the orchestrator's local settings only; `gov check` reports it wired. About half
    a day; W2-10 is open.
  - The dead-man's switch goes to `docs/plan/WAVE_3_PARKING.md` as a product feature (cron and a notifier are
    machine-specific; this repository keeps its own, ACT-DEADMAN-1).
- **(b) One new ticket** holding all of it (a P1 under DEC-974): cleaner ownership, but a new ticket, and it touches
  W2-11's and W2-33's files anyway (path overlap: it would wait for both).
- **(c) Defer to Wave 3:** this repository keeps its own discipline; products get it later. Risk: EXAMIN's copy runs
  without it.

What changes: three tickets' KPIs (within the approved roles spec, ROLES-SPEC-1: the CTO's duties); the orchestration
skill and the role file through those tickets' CIT-P; no Contract or Charter change.

## 5. Recommendation
**(a)**, confidence medium-high. The three tickets already own the three places; no new ticket; W2-10's hook is the
product form of ACT-QUIET-DENY-1, built on what that ACT proves here.

## 6. What it blocks, and what waiting costs
It blocks nothing today. W2-11's next round is the cheapest moment for its KPI (it resumes now, P-W2-11-5 to 8);
after that, it is a further round.
