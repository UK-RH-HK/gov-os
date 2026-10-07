---
name: audit
description: Method for running an independent fidelity audit against the Contract and governing decisions
version: "1.1.0"
---
# Audit

A method for the independent auditor role. The guard and the role file decide what the session may read and write; this skill is the method only (CAP-24.b).

## Starting the session

The audit runs in a fresh session with no prior context (CAP-47). The only inputs are:

1. The bounded context pack from `gov context`, which carries the mandatory inputs by id and sha256.
2. The repository at the audited commit.

The role file states that the session is read-only with respect to audited files: the auditor does not edit audited files (MR-4). The guard decides what the session may write.

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

The report states the pack hash so a reader can verify the inputs the auditor received (CAP-47).

## Wave-exit reports

A wave-exit audit report covers every LITE feature specification closed in the wave (DEC-088, CAP-47). Spine, STANDARD and FULL feature specifications each trigger their own audit at closure; LITE specifications are audited together at the wave exit.

## Findings and disposition

- **Contested findings** and **owner-level findings** appear as decision packages in chat. The owner decides; their answer is committed as a decision record (MR-4, DEC-070).
- **Agreed fixes** become tickets.
- An owner-level finding requires a decision package before it can become a ticket. No finding is silently promoted or demoted.

## Exit audit — MR-3 reading

The exit audit must state DEC-430 (the owner's reading of MR-3): the core tests for every KPI line are written by the independent test designer before implementation. Cases found in review may be added afterwards, by the test designer only (DEC-136).

## Governing sources

DEC-088, DEC-070, DEC-430, CAP-47, MR-4.
