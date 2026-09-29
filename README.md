# Governance OS

This repository is being rebuilt as an assembled Governance OS. The previous v4 line is
archived, not deleted; see [docs/SOURCES.md](docs/SOURCES.md) for provenance and for how
to retrieve anything from the archive.

## Layout

- `cli/govbridge/` — the carried Python package (authority, lexical, model-pin core and what they import)
- `cli/config/` — configuration the package reads; `cli/config/schemas/` holds its schemas
- `cli/tests/` — tests for the carried package, with fixtures and `support/`
- `schemas/records/` — record, decision, lesson, research and checkpoint schemas
- `fixtures/` — greenfield, brownfield and migration fixture projects (`fixtures/README.md`)
- `docs/adr/` — architecture decision records for the rebuild
- `docs/lessons/` — lessons for the rebuild
- `docs/interfaces/` — interface specifications
- `docs/source/` — reference-only originals, owner records and control panels (excluded from agents)
- `docs/SOURCES.md` — where every carried file came from, and the archive

## Provenance

Everything under `docs/source/` is reference only. Where it conflicts with an ADR in
`docs/adr/`, the ADR wins.
