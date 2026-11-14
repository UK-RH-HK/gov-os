---
name: audit
description: >-
  Method for running an independent fidelity audit against the Contract and
  governing decisions
metadata:
  version: 1.2.0
---
# Audit

A method for the independent auditor role, and for the reviewer's probe of a FULL ticket. The guard and the role file decide what the session may read and write; this skill is the method only (CAP-24.b).

## Starting the session

The audit runs in a fresh session with no prior context (CAP-47). The only inputs are:

1. The bounded context pack from `gov context`, which carries the mandatory inputs by id and sha256.
2. The repository at the audited commit.

The role file states that the session is read-only with respect to audited files: the auditor does not edit audited files (MR-4). The guard decides what the session may write: an auditor or a reviewer writes only its own audit or review record.

The auditor and the reviewer read everything, tests and code alike (DEC-820 item 3). Only secrets, the contents of the held-out qualification material (its file names are readable) and the hidden half of an evaluation set stay refused; a read the guard still refuses is taken as a refusal, never respelled, and counted in the return (DEC-820 item 6).

## Judgement rules

Every finding of an audit or a review is judged the same way (DEC-801 to DEC-803, DEC-808, DEC-809).

- **The threat model is the project's threat-model record** (`<the project's threat-model record>`): the guards stand against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand, replace refs, an opaque interpreter used to evade the guard) is a row for the project's hardening list, never a new round (DEC-801). So is a guard hole only unsandboxed sessions can reach (DEC-779).
- **Every finding carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808). A finding marked "no" is a row, never a round.
- When a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802). A risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803). A package that proposes a round states its findings' classification on one line first (DEC-809).

## Writing the report

The report is a Markdown file with YAML frontmatter holding three required fields:

- `milestone` — the milestone being audited.
- `commit` — the hexadecimal commit id of the audited commit.
- `pack_sha256` — the SHA-256 hash of the context pack the auditor received.

The body holds one table with three columns: `item | class | evidence`. Evidence values are paths relative to the repository root, separated by commas. A row of class `OK` must cite at least one path. A row of another class may cite no evidence, written as `-`.

The report names its milestone (DEC-088). It has one row per contract item and decision in scope (DEC-088, CAP-47). Each row is classified into exactly one of the six classes:

- **OK** — the item is met as stated.
- **MISSING** — the item is not addressed.
- **WEAKENED** — the item is partially met but weaker than specified.
- **CONTRADICTS** — the implementation contradicts the item.
- **UNJUSTIFIED_DROP** — the item was dropped without a governing decision.
- **SCOPE_CREEP** — work beyond the specification with no governing source.

The report states the pack hash so a reader can verify the inputs the auditor received (CAP-47). Every finding in it carries the two lines of the judgement rules.

## Wave-exit reports

A wave-exit audit report covers every LITE feature specification closed in the wave (DEC-088, CAP-47). Spine, STANDARD and FULL feature specifications each trigger their own audit at closure; LITE specifications are audited together at the wave exit.

## Reviews of FULL tickets

- A fresh reviewer that wrote none of the code probes the ticket's final head before the merge, for behaviour the acceptance tests miss: lost work, writes outside a role's scope, acceptance tests changed by an implementer, a guard or gate failing open (DEC-137, DEC-498). It runs the code; it does not re-run the ticket's suites, whose results the lead gives it (DEC-959 item 1).
- It writes nothing: it returns its probe record's content, each finding as a described behaviour, never as code (DEC-136), with its two lines; the lead commits a passing record under `docs/probes/<ticket id>/` (DEC-733).
- At most two reviews per round declared in the ticket's plan before the round starts (DEC-413, DEC-916).

## Findings and disposition

- **Contested findings** and **owner-level findings** appear as decision packages, in six parts (DEC-818). The owner decides; the orchestrator records the answer in a decision-record commit (MR-4, DEC-070, DEC-861). No auditor or reviewer puts `Role: owner` or `Decided-by:` on a commit.
- **Agreed fixes** become tickets.
- An owner-level finding requires a decision package before it can become a ticket. No finding is silently promoted or demoted.

## Exit audit — MR-3 reading

The exit audit must state DEC-430 (the owner's reading of MR-3): the core tests for every KPI line are written by the independent test designer, not by the implementer. Cases found in review may be added afterwards, by the test designer only, red before their fix (DEC-136). Under the work order in parallel the designer writes them at the same time as the implementer, from the specification, never reading the implementation (DEC-959 item 7); the auditor checks that independence.

## Return

The auditor's report is committed alone, never with a ticket file or the register (DEC-924 item 2); the reviewer's record goes to its lead. Either session's return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with the record's content or path after them (CAP-37). Refused twice for the same call: stop and return (AR-6). An authentication error returns `AUTH_REQUIRED` (DEC-420).

## Governing sources

DEC-070, DEC-088, DEC-136, DEC-137, DEC-413, DEC-420, DEC-430, DEC-498, DEC-733, DEC-779, DEC-801, DEC-802, DEC-803, DEC-808, DEC-809, DEC-818, DEC-820, DEC-861, DEC-916, DEC-924, DEC-959, CAP-37, CAP-47, MR-4, AR-6.
