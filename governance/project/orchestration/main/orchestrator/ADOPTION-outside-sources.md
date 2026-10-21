# Outside sources for this repository's adoption step (DEC-560; prepared 2026-10-09)

Ids that tickets declare as sources, that live outside the readable tree, and that are neither records nor
(yet) listed. Counted from the ticket files (`.tickets/`), 2026-10-09. Applied in the adoption step
(DEC-522), not before.

## Kind 1: imported as records, with origin path and sha256 (decisions and evidence the repository relies on)

| Id | Origin (as `docs/SOURCES.md` names it) | sha256 (from `docs/SOURCES.md`) |
|---|---|---|
| OWNER-DECISION-P2-0001 (cited as "OWNER-DECISION-P2-0001 BC-P2-08") | `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0001-AGENT-ROLE-IDENTITY.md` | `612849ba65c310c5ff41999e72e3382048842f526048a3fe49ab1a5b5a88b0ce` |
| OWNER-DECISION-P2-0008 | `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0008-COMPLETE-PHASE-2.md` | `c7bb4cbae6a8595c3bba9608d7d31bd7911abf876825e3427a39ad5a10a90af8` |
| OWNER-DIRECTION-BR-0004 | `docs/source/owner-records/bridge/OWNER-DIRECTION-BR-0004-CHECKPOINT-DISCIPLINE.md` | `7783efcba342d765250dc0c1083c518e78788ae4bfdfb1f508cdafd93c84e134` |
| OWNER-AMENDMENT-P2-0010 | `docs/source/owner-records/phase-2/OWNER-AMENDMENT-P2-0010-CONTEXT-RETRIEVAL-BRIDGE.md` | `8cc0f3bbf74238f5d0c8b28f00b581c2878154faa69895af35a7f35447c3c7b3` |
| EXP-001 (its evidence record) | /home/usain/gov-os-workbench/spike-sandbox/EVIDENCE.md (DEC-564; exact-path read only, the folder is never listed) | 84ce1d1390d40a25ae1b5a8af224db871132ebcd8d5b0842b64796f1e0ad7714 (taken 2026-10-09, 266 lines) |

Notes:
- `docs/source/` is not in the tracked tree (the sandbox denies reading it in worktrees). At the import the
  file's bytes are checked against the sha256 above before a record is written; a mismatch stops the import.
- "BC-P2-08" is a clause inside OWNER-DECISION-P2-0001, not an id of its own: the ticket's source is the
  document; the record notes the clause.
- EXP-001: answered by the owner (DEC-564). Nothing is open for the owner in this list.

## Kind 2: listed as external references in `governance/project/external-references.yaml` (research-catalogue ids)

Already listed (W1-41): `S0a-G-12`, `S0a-G-13`.

S0a (location "S0a STACK_OPTIONS §3", as the WBS source table names it), 10 ids:
`S0a-G-01`, `S0a-G-02`, `S0a-G-03`, `S0a-G-04`, `S0a-G-06`, `S0a-G-07`, `S0a-G-09`, `S0a-G-10`, `S0a-G-11`,
`S0a-G-15`.

S0b2 (location "S0b2 GLUE_REQUIREMENTS", as the WBS source table names it), 21 ids:
`G-01`, `G-02`, `G-03`, `G-04`, `G-05`, `G-06`, `G-07`, `G-08`, `G-09`, `G-10`, `G-11`, `G-12`, `G-14`,
`G-15`, `G-17`, `G-18`, `G-19`, `G-20`, `G-21`, `G-22`, `G-25`.

Each entry: `id`, `location`, `reason` ("research catalogue of stage S0a/S0b2, kept outside the repository;
its requirement is restated in the citing ticket's KPI lines").

## Fits neither kind

None among the 36 ids above. `EXP-002` appears in one ticket's prose only (a Wave 2 experiment not yet run)
and is not a declared source.

## Not outside sources (live in the repository; they become records in the adoption step or the follow-up after W1-41)

84 `DEC-` ids (register decisions, DEC-521), 56 `CAP-` ids (capability records from `contract.yaml`), 6 `MR-`
ids, 1 `API-` id, and the `W1-` ids in `depends_on`.
