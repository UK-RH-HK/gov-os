# W2-151 evidence: MR-1 to MR-6 regenerated from contract.yaml (DAEO-qzca)

Task: DAEO-qzca. Role: product-spec. Profile LITE. Sources: DEC-623, DEC-1074 (8), DEC-1109 (2), DEC-1073 (2), W2-129.

## What was done

The six master-rule records under `docs/contract/master-rules/` were regenerated from `docs/contract/contract.yaml` at
the branch's base (`661a0a49c57b`), in the form `02ee7e33` (DEC-623) generated them. A one-off script outside the
repository (never committed) read the contract file with `yaml.safe_load` and wrote each record from the same template;
it compared each record line by line before writing it.

The contract file at the base says `id: CONTRACT-v4`, `status: ACCEPTED`, `version: '4.3'` (revised 2026-11-09 by
W2-27's change, DEC-1093). The ticket's card says 4.2; the file has moved on since the card was filed, and S1 asks for
the contract file's version, so the records name 4.3.

## Per record

| Record | status | version in the "Generated from" sentence | title, Text, Acceptance | Other front matter |
|---|---|---|---|---|
| MR-1 | PROPOSED → ACCEPTED | 4.1 → 4.3 | unchanged (already the contract file's) | kept |
| MR-2 | PROPOSED → ACCEPTED | 4.1 → 4.3 | unchanged | kept |
| MR-3 | PROPOSED → ACCEPTED | 4.1 → 4.3 | unchanged | kept |
| MR-4 | PROPOSED → ACCEPTED | 4.1 → 4.3 | unchanged | kept |
| MR-5 | PROPOSED → ACCEPTED | 4.1 → 4.3 | unchanged | kept |
| MR-6 | PROPOSED → ACCEPTED | 4.1 → 4.3 | unchanged | kept |

Each record changed on two lines only (line 4, `status`; line 13, the version): 12 insertions, 12 deletions. "Kept"
means `id`, `type: specification`, `state_class: DERIVED` and `depends_on: [CONTRACT-v4]`.

## KPI rows

| KPI | Result | Evidence |
|---|---|---|
| S1 | met | status ACCEPTED and version 4.3 from `contract.yaml`; title, Text (`text_source`) and Acceptance equal the contract file's entry for each id (the folded YAML joined with single spaces); other keys kept |
| S2 | met | `gov links --all` (below): STATUS_CONFLICT 6 → 0, no other code changed, 0 new; `python3 -m gov.check.schema` (the structural pass's schema family): `ok: true`, 974 records validated, the six included (`docs/` is a record path) |

## gov links --all, before and after

Run as `PYTHONPATH=/home/usain/gov-os-worktrees/W2-151/src python3 -m gov.cli.main links --all`. It reads `HEAD`, so
"after" was measured on the records' commit.

| Code | Before (`661a0a49c57b`) | After (records' commit) |
|---|---|---|
| STATUS_CONFLICT (product-spec) | 6 | 0 |
| UNMARKED_CHANGE | 9 | 9 |
| UNKNOWN_ID | 627 | 627 |
| UNLINKED_ID | 1104 | 1104 |
| NOT_IN_FORCE_AS_RULE | 20 | 20 |
| ENFORCES_SUPERSEDED | 73 | 73 |
| CLOSED_TICKET_EDITED | 117 | 117 |
| TICKET_CHANGE_UNMARKED | 93 | 93 |
| Total | 2049 | 2043 |

The one finding left that names a master rule is `UNLINKED_ID MR-3` in `.tickets/DAEO-8lmb.md:52` (orchestrator's,
outside this ticket's paths).

## Not touched

`docs/contract/contract.yaml` and `docs/contract/CONTRACT_v4.md` (W2-139's), `.tickets/`, `.claude/`.
