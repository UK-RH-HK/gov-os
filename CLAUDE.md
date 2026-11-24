# Governance

This project uses the Gov OS governance framework.

**Read `docs/emergency-2/EMERGENCY-2.md` first.** It is the strategy in force (the owner's, approved 2026-11-17) and supersedes anything that contradicts it, the Contract included, until the Contract is re-baselined. The Contract (`docs/contract/`) and the decision register (`docs/DECISION_REGISTER.md`) hold where they do not contradict it. The old checkpoint, start-next-session page, decisions-in-force list and orchestrator prompt are history in `docs/emergency-2/archive/`; do not work from them.

## How we work (EMERGENCY-2 §2, §4)

- **Trust, then catch and correct; do not prevent.** No guard, no sandbox, no permission prompts. Agents have full permission in the repository they work in, their worktree and their run folder; sessions stay apart by where they start, the folders they are given and their brief. Two denies stay, in the project settings: `git push` and `sudo`. Releases and re-pins are the owner's.
- **Three kinds of work.** A *feature* is a ticket with a spec and KPIs. A known bug in a feature is a *fix*: no new ticket, recorded in the owning ticket's record, with the failing test first when no test caught it. A *chore* (records, docs, configuration, a tidy-up with the tests unchanged and green) is a direct commit, listed in the digest. A new KPI line on a closed feature is a new ticket.
- **The flow.** The independent test designer writes the acceptance tests, red on the base; the engineer builds until `gov accept` is green; the landing merges and runs the impact-selected tests by code and checks the paths and who wrote the tests; if it is red, find and fix the cause; the ticket closes at the land.
- **Memory first (§5).** Before grepping for a concept, ask memory: `gov retrieve "<question>"`. Read the whole bundle, never cut it short, then search once more in your own words. Look a decision up by id in the register.

## Roles

Roles stay apart through the landing, the templates, the briefs, the skills and the path map, not through permissions (EMERGENCY-2 §1.2).

- **engineer**: implements one ticket until its acceptance tests pass.
- **independent-test-designer**: writes acceptance tests from the KPIs before implementation; the builder never writes its own acceptance tests.
- **independent-auditor**: audits as a fresh, read-only session, when an audit is called for.
- **orchestrator** (the CTO): runs the flow and the build list, starts workers, decides what EMERGENCY-2 leaves to it.
- **senior engineer**: runs one stream's tickets under the CTO when several streams run.
- **product-spec**: writes schemas, templates, skills, role files and documentation.
- **research**: runs experiments and leaves an evidence record.
- **ticket lead**: an orchestrator session in one ticket's worktree; runs that ticket's loop and returns; it never merges.

Each role's tools and paths are in its role file under `template/governance/kernel/roles/` (generated as `.claude/agents/`). Kernel and instruction text (role files, templates, skills, CLAUDE.md, AGENTS.md) changes only when the CTO decides, approves and makes the change (EMERGENCY-2 §3.5).

## Golden rule: how work is judged (DEC-1204, as EMERGENCY-2 §3 applies it)

- **Value first.** What matters is tests and code that match the KPIs and the spec and pass green. Everything else, practicality and security work included, must justify itself against that.
- **Threat model:** honest agent mistakes, plausible accidents and drift in ordinary work, not a same-privilege adversary.
- **What may block:** only a finding within the change's scope that an honest agent can hit in ordinary work and that fails open or loses work. A finding that needs a deliberate construction is a Wave 3 row, never a new round.
- **When a review happens:** only for a red test, a failed landing or merge, or a feature that does not work as intended; batched when several come together. Work that went through green needs none. Most causes are found and fixed by the CTO, a senior engineer or the engineer, without review.
- **How reviews converge:** a moderator triages every finding against the change's scope; at most two rounds, then the owner once with options; READY is computed by code.

<!-- gov:generated begin -->
# Governance

This project uses the Gov OS governance framework.

**Read `docs/emergency-2/EMERGENCY-2.md` first.** It is the strategy in force (the owner's, approved 2026-11-17) and supersedes anything that contradicts it, the Contract included, until the Contract is re-baselined. The Contract (`docs/contract/`) and the decision register (`docs/DECISION_REGISTER.md`) hold where they do not contradict it. The old checkpoint, start-next-session page, decisions-in-force list and orchestrator prompt are history in `docs/emergency-2/archive/`; do not work from them.

**The golden workflow** (`docs/emergency-2/GOLDEN-WORKFLOW.md`, approved by the owner on 2026-11-24, DEC-1244) is the spine: it says how work flows, step by step, and what code holds at each step; it stands beside the golden rule below, which says how work is judged. Whatever contradicts it is wrong.

## How we work (EMERGENCY-2 §2, §4)

- **Trust, then catch and correct; do not prevent.** No guard, no sandbox, no permission prompts. Agents have full permission in the repository they work in, their worktree and their run folder; sessions stay apart by where they start, the folders they are given and their brief. Two denies stay, in the project settings: `git push` and `sudo`. Releases and re-pins are the owner's.
- **Three kinds of work.** A *feature* is a ticket with a spec and KPIs. A known bug in a feature is a *fix*: no new ticket, recorded in the owning ticket's record, with the failing test first when no test caught it. A *chore* (records, docs, configuration, a tidy-up with the tests unchanged and green) is a direct commit, listed in the digest. A new KPI line on a closed feature is a new ticket.
- **The flow.** The independent test designer writes the acceptance tests, red on the base; the engineer builds until `gov accept` is green; the landing merges and runs the impact-selected tests by code and checks the paths and who wrote the tests; if it is red, find and fix the cause; the ticket closes at the land.
- **Memory first (§5).** Before grepping for a concept, ask memory: `gov retrieve "<question>"`. Read the whole bundle, never cut it short, then search once more in your own words. Look a decision up by id in the register.

## Roles

Roles stay apart through the landing, the templates, the briefs, the skills and the path map, not through permissions (EMERGENCY-2 §1.2).

- **engineer**: implements one ticket until its acceptance tests pass.
- **independent-test-designer**: writes acceptance tests from the KPIs before implementation; the builder never writes its own acceptance tests.
- **independent-auditor**: audits as a fresh, read-only session, when an audit is called for.
- **orchestrator** (the CTO): runs the flow and the build list, starts workers, decides what EMERGENCY-2 leaves to it.
- **senior engineer**: runs one stream's tickets under the CTO when several streams run.
- **product-spec**: writes schemas, templates, skills, role files and documentation.
- **research**: runs experiments and leaves an evidence record.
- **ticket lead**: an orchestrator session in one ticket's worktree; runs that ticket's loop and returns; it never merges.

Each role's tools and paths are in its role file under `template/governance/kernel/roles/` (generated as `.claude/agents/`). Kernel and instruction text (role files, templates, skills, CLAUDE.md, AGENTS.md) changes only when the CTO decides, approves and makes the change (EMERGENCY-2 §3.5).

## Golden rule: how work is judged (DEC-1204, as EMERGENCY-2 §3 applies it)

- **Value first.** What matters is tests and code that match the KPIs and the spec and pass green. Everything else, practicality and security work included, must justify itself against that.
- **Threat model:** honest agent mistakes, plausible accidents and drift in ordinary work, not a same-privilege adversary.
- **What may block:** only a finding within the change's scope that an honest agent can hit in ordinary work and that fails open or loses work. A finding that needs a deliberate construction is a Wave 3 row, never a new round.
- **When a review happens:** only for a red test, a failed landing or merge, or a feature that does not work as intended; batched when several come together. Work that went through green needs none. Most causes are found and fixed by the CTO, a senior engineer or the engineer, without review.
- **How reviews converge:** a moderator triages every finding against the change's scope; at most two rounds, then the owner once with options; READY is computed by code.
<!-- gov:generated end -->
