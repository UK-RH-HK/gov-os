---
name: adopt
description: >-
  Method for progressive adoption of the Gov OS into a repository through the
  A0-A11 transaction
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

Wave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, A9 itself, A11 (full audit) and the full verdict.

## Governing sources

DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, CAP-44, CAP-54.
