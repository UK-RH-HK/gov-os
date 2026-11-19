---
root: true
targets: ["claudecode", "agentsmd"]
description: "Gov OS governance rules"
---

# Governance

This project uses the Gov OS governance framework. It gives agents memory, help with the spec and the KPIs, roles that
keep conflicting work apart, and the launching, landing and closing of tickets. It governs the traffic, not the city.

## The golden rules (the owner's; they hold in every governed repository)

- **Value first.** What matters is tests and code that match the KPIs and the spec and pass green. Everything else,
  practicality and security work included, must justify itself against that.
- **The threat model.** Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work. It
  is not a defence against a same-privilege adversary.
- **Trust, then catch and correct; do not prevent.** No guard, no sandbox, no permission prompts. Agents have full
  permission in the repository, worktree and run folder they work in. `git push` and `sudo` stay the owner's, and so do
  releases.
- **How work is judged** (the `judging-work` skill holds the whole rule):
  - What may block: only a finding within the change's scope that an honest agent can hit in ordinary work and that
    fails open or loses work. A finding that needs a deliberate construction is recorded for later, never a new round.
  - When a review happens: only for a red test, a failed landing or merge, or a feature that does not work as
    intended; batched when several come together. Work that went through green needs none.
  - How reviews converge: a moderator triages every finding against the change's scope; at most two rounds, then the
    owner once, with options.

## How we work

- **Three kinds of work.** A feature is a ticket with a spec and KPIs. A known bug in a feature is a fix: no new
  ticket, recorded in the owning ticket's record, with the failing test first when no test caught it. A chore
  (records, docs, configuration, a tidy-up with the tests unchanged and green) is a direct commit.
- **The flow.** The independent test designer writes the acceptance tests, red on the base; the engineer builds until
  `gov accept` is green; `gov queue` lands the ticket (it merges, runs the impact-selected tests, checks who wrote the
  tests, and writes the close record); the ticket closes at the land.
- **Memory first.** Before grepping for a concept, ask memory: `gov retrieve "<question>"`. Read the whole bundle,
  then search once more in your own words. Look a decision up by id in the decision register.

## Roles

Roles stay apart through the landing, the templates, the briefs, the skills and the path map, not through permissions.
Each role's tools and paths are in its role file under `governance/kernel/roles/`.

- **engineer**: implements one ticket within its allowed paths until its acceptance tests pass.
- **independent-test-designer**: writes acceptance tests from the KPIs before implementation.
- **independent-auditor**: audits finished work as a fresh, read-only session.
- **orchestrator**: runs the wave, coordinates tickets, starts workers.
- **product-spec**: writes schemas, templates, skills, role files and documentation.
- **research**: runs experiments and leaves an evidence record.
- **qa-engineer**: checks a stream's finished tickets before they merge, as a fresh session; writes only its findings report.
- **senior-engineer**: runs one stream's tickets under the CTO, starts each ticket lead and reads its return.
- **ticket-lead**: runs one ticket's loop in its worktree and returns one summary; never merges into integration.
