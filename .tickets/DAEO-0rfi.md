---
id: DAEO-0rfi
status: in_progress
deps: []
links: []
created: 2026-10-18T03:12:15Z
type: task
priority: 1
assignee: engineer
external-ref: W2-54
tags: [wave-2, implementation, full]
wbs_id: W2-54
title: The context packet's dropped list in a stable order; the context check's declared time limit; the audit-report type
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/context/**
- template/governance/kernel/checks/context-reproducibility.yaml
- src/gov/check/schema.py
- template/governance/kernel/schemas/audit-report.schema.json
- tests/unit/context/**
- tests/unit/check/test_schema_audit_report*
- docs/changes/W2-54-CIT-E.md
kpis:
  success:
  - "Two computations of any ticket's context in one store give one hash: the `dropped` list is sorted stably with a full tie-break, whatever order retrieval returns tied items in [DEC-768]."
  - "The context-reproducibility check declares a time limit that fits its measured run on this repository; the measurement (the run's seconds, the tickets measured, the machine's load) is recorded in the change record [DEC-768]."
  - "`gov check` gives context-reproducibility green on `w2/integrate` [DEC-768]."
  - "The `audit-report` type exactly as W2-02 defines it on `w2/W2-02` (`2a35fd7b`): its schema file byte for byte as W2-02's; in `src/gov/check/schema.py`, W2-02's lines for that type (its `SCHEMA_MAP` entry, the type among the standalone types, the audit-report folder `docs/audit` and its reading of a record there that states no `type` as an audit report), nothing of W2-02's other types. Core-schema is green on `w2/integrate`, with the W1-43 audit report's body untouched [DEC-768 item 1]."
  failure:
  - "A context whose items or hash differ between two computations still fails the check, naming the ticket."
  - "A check that runs past its declared limit still fails; no hard-block check is weakened [DEC-768 item 4]."
  - "A record outside `docs/audit/` that states no `type` still fails core-schema; an audit report that lacks `milestone`, `commit` or `pack_sha256` fails it, naming the field."
profile: FULL
sources:
- DEC-768
- DEC-626
- DEC-441
- DEC-565
- CAP-33
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-54/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- DEC-768 (items 1 and 3)
list_rows: []
---
# W2-54 The context packet's dropped list in a stable order; the context check's declared time limit; the audit-report type

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-54), added by DEC-768 (owner, 2026-10-18; P-W2-26 (a), P-W2-28 (a) refined). Starts right after the owner's commit `7d689987`, alone, tests first, one review; W2-53 is closed again after it.

- **Why:** W2-53's close (merge `c9537e39`) refused on three pre-existing hard-block checks. Two are this ticket's: context-reproducibility runs 122 seconds against the 60 seconds a check without a declared limit gets, and fails on 15 tickets because two computations of a ticket's context give its `dropped` list in two orders; core-schema refuses `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`, which states no `type`. (The third, W1-42's claim commit without `Implements:`, is accepted history under DEC-717, DEC-768 item 2.)
- **The kernel files** `template/governance/kernel/checks/context-reproducibility.yaml` (the `timeout-seconds` line only) and `template/governance/kernel/schemas/audit-report.schema.json` are approved by DEC-768 (CAP-33); the change record `docs/changes/W2-54-CIT-E.md` records the change and the measurement.
- **W2-02 shares `src/gov/check/schema.py`** (held, not running). This ticket takes W2-02's `audit-report` type exactly, so W2-02's later merge adds nothing new for it; the standalone-types line will differ (W2-02's also names `adoption-verdict`), and W2-02's resume resolves it to W2-02's line, with a fresh probe (owner, 2026-10-18).
- **No hard-block check is weakened** (DEC-768 item 4). The W1-43 audit report's body is not touched by this ticket; its sha256 before is `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`, and the orchestrator records it after this ticket merges.
