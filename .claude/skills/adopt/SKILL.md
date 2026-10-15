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

## Independent gates (Wave 3)

The independent gates A7 (independent migration verification), A10 (independent memory verification) and A11 (full audit) are Wave 3, together with CAP-47. The final verdict — `ADOPTED_HEALTHY`, `ADOPTED_WITH_ACCEPTED_EXCEPTIONS` or `NOT_ADOPTED_HEALTHY` — is issued from Wave 3 (DEC-090).

## Governing sources

DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, CAP-44, CAP-54.
