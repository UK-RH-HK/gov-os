---
name: adopt
description: Method for progressive adoption of the Gov OS into a repository through the A0-A11 transaction
version: "1.0.0"
---

# Adopt

A method for progressive adoption. The guard and the role file decide what each session may do; this skill is the method only (CAP-24.b).

## Progressive adoption

A repository is governable from day one (DEC-006). Full A0–A11 remains the target for `ADOPTED_HEALTHY`, but adoption proceeds in stages with one evidence record per stage (CAP-44, CAP-54).

## Wave 1 scope (DEC-090)

Wave 1 delivers `gov adopt --lite`, covering stages A0–A4, A6, A8 and A5:

- **A0** — safety baseline: clean tree and backup ref.
- **A1** — cold inventory of the repository.
- **A2** — classification of artefacts.
- **A3** — target path map.
- **A4** — batched migration plan with rollback points.
- **A5** — independent review of the path map before any move, by the Independent Auditor role (DEC-090).
- **A6** — controlled migration; a failed batch rolls back to its recorded point.
- **A8** — legacy memory extraction and retirement.

Each stage writes an evidence record. `gov doctor` reports the current adoption level (CAP-54).

## Embedding policy (DEC-694, DEC-700)

Every namespace of the target path map states its `embedding_policy`, as one of two values, written exactly so:

- `embedded` — the chunks of the namespace's files reach the semantic vectors.
- `not embedded` — the namespace's files are found by the lexical route only; nothing of them is embedded.

Stage A3 refuses a path map in which a namespace states another value or none, or in which no namespace is `embedded`; it records nothing. Outside adoption an unknown or missing value is read as `not embedded` (DEC-388), and `gov rebuild` and `gov doctor` say "no namespace is embedded" where none is.

## Independent gates (A7 and A10 lite; the rest Wave 3)

Contract v4.2 brings A7 and A10 into Wave 2 in a lite form (CAP-44.f, DEC-741). Each is recorded as its own stage: `gov adopt --lite --stage A7` (or `A10`) `--verdict <path>`, run by the session that ran the stages on the committed record of a fresh Independent Auditor session. That record states `stage`, `verdict` (only `pass` passes), an `auditor_session` that ran no stage, and `checked`: each record checked, with its sha256 at HEAD. It is committed with `Role: independent-auditor`. The gate commits its own record under `governance/adoption/`, with its conditions; a gate that fails commits a failing record.

- **A7** — independent migration verification, by a fresh Independent Auditor session: the A6 migration against the A3 path map and the A4 plan reviewed at A5. The gate also checks that each move of the plan stands in the project.
- **A10** — independent memory verification, by a fresh Independent Auditor session: A8's extraction and retirement, the derived state rebuilt from git (`gov rebuild`, CAP-20), and the canary of each index (CAP-55).
- **The verdict** reads each gate's record as named conditions (CAP-44.h (4), (6), (9)). A missing A7 or A10 record is that gate's condition `not met`, never healthy. No gate and no auditor accepts a condition; only the owner does, by name.

Wave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, the full A9 (its lite form, the Wave 0 memory practice, is the section below), A11 (full audit) and the full verdict.

## A9: Wave 0 memory practice

An adopted repository gets its memory built in Wave 0, in the order below (A9 lite). The practice record `docs/research/W2-88-memory-practice.md` holds the methods, the figures and the lessons behind each step.

1. Assess the repository and plan its refactoring for full indexing.
2. Census the stated links (records, front matter, trailers, text) and build the graph from them.
3. Build the store with the standard (Gov OS's memory standard, pinned and written in the A9 record) and its refresh (the store rebuilt after every merge, a failed build leaving the last good store in service). [DEC-1098 (1), DEC-1072 (2)]
4. Have the verdict set and the tuning set written, by independent writers under the rubric, both held outside every worktree. [DEC-1071 (1)-(3), DEC-1074 (4)]
5. Measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points. [DEC-1071 (1)-(3), DEC-1074 (4)]
6. Declare and measure the verdict set once. A miss stands as it is: the set is never run again. [DEC-1071 (1)-(3), DEC-1098 (1)]
7. Record every method and figure, in the adopted repository's copy of the practice record. [DEC-1072 (2)]

## Verify clauses for adopted tickets

A repository adopted by Gov OS brings tickets written before adoption, and the brief of a ticket is refused while a KPI line has no `Verify:` clause. The pass below gives such a ticket its clauses and leaves the ready check as it is. [DEC-1130, DEC-1083]

- The pass runs for a ticket about to launch, not for the whole tracker. [DEC-1130]
- A product-spec session writes the clauses; the tool never writes one. [DEC-1130, DEC-1050]
- Three things check the clauses: the tool, the ticket's test designer and the auditor's sample. [DEC-1130, DEC-1083]
- The owner approves the rule once, not ticket by ticket. [DEC-1130]

The tool is `gov adopt`. Its list option prints, for each open or in-progress ticket that has a KPI line with no verify, the ticket id and the labels of those lines, and the answers file names only the tickets about to launch. Its apply option takes the answers file (YAML, outside the repository: ticket id, then label, then clause) and checks it before it writes anything: every named ticket exists and is not closed, every named label exists, every line still lacking a verify is answered, and each clause is text of its own. It then appends ` Verify: <clause>` to the lines' text, editing the text only (no YAML dump, which would lose comments), and adds the marker `verify_pass: <date> <session>` to the ticket's front matter. [DEC-1130]

## Governing sources

DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1130, CAP-44, CAP-54.
