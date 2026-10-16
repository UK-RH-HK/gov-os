---
id: DAEO-zflj
status: in_progress
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:10Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-02
tags: [wave-2, schema, standard]
wbs_id: W2-02
title: 'Record types: decision entry, audit report, adoption verdict, close record; core-schema green here'
class: schema
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- DAEO-g0ip
allowed_paths:
- template/governance/kernel/schemas/**
- schemas/**
- template/governance/kernel/templates/decision-record.md
- src/gov/check/schema.py
- tests/unit/check/test_schema*
kpis:
  success:
  - 'The kernel schemas define these types [AR-1, AR-3, W2-M316, W2-M317, AR-9]: a decision entry: one register entry, with id, status, owner, date and its own span; an audit report in DEC-441''s form;
    an adoption verdict: the three CAP-44.h verdicts and the conditions behind them, in the lite form Contract v4.2 states; the close record type that gov close writes'
  - Core-schema reads docs/audit/wave-1/W1-43-wave-1-exit-audit.md and the exit report as valid, and is green on this repository [F-M13, W2-M301, W2-M309, W2-M310, W2-L243].
  - A type with no schema file is reported unmeasured, not green [W2-M260, W2-L177].
  - The wbs_id grammar accepts an id with one lower-case letter suffix (W2-15a) and still refuses any other form (W2-15, W2-15ab, W2-15A, W2-1) [DEC-730].
  failure:
  - An audit report missing its milestone or pack hash is invalid [W2-M138]; a record with an unknown type is still SCHEMA_INVALID_TYPE.
profile: STANDARD
sources:
- DEC-441
- CAP-44.h
- DEC-730
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-02/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-1 (schema)
- AR-3
- AR-9 (schema)
list_rows:
- W2-L177
- W2-L217
- W2-L240
- W2-L241
- W2-L242
- W2-L243
- W2-L244
- W2-L248
- W2-L260
- W2-L261
- W2-L267
- W2-M057
- W2-M058
- W2-M138
- W2-M260
- W2-M298
- W2-M299
- W2-M301
- W2-M304
- W2-M309
- W2-M310
- W2-M316
- W2-M317
---
# W2-02 Record types: decision entry, audit report, adoption verdict, close record; core-schema green here

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-02), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `template/governance/kernel/schemas/**`, `schemas/**`, `template/governance/kernel/templates/decision-record.md`, `src/gov/check/schema.py` (the type map only), `tests/unit/check/test_schema*`.
- **KPIs, success:**
  - The kernel schemas define these types [AR-1, AR-3, W2-M316, W2-M317, AR-9]:
    - a decision entry: one register entry, with id, status, owner, date and its own span;
    - an audit report in DEC-441's form;
    - an adoption verdict: the three CAP-44.h verdicts and the conditions behind them, in the lite form Contract v4.2 states;
    - the `close` record type that `gov close` writes.
  - core-schema reads `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` and the exit report as valid, and is green on this repository [F-M13, W2-M301, W2-M309, W2-M310, W2-L243].
  - A type with no schema file is reported unmeasured, not green [W2-M260, W2-L177].
  - The `wbs_id` grammar accepts an id with one lower-case letter suffix (`W2-15a`) and still refuses any other form (`W2-15`, `W2-15ab`, `W2-15A`, `W2-1`) [DEC-730]. The grammar's one definition is `template/governance/kernel/schemas/common.schema.json`.
- **KPIs, failure:** an audit report missing its milestone or pack hash is invalid [W2-M138]; a record with an unknown type is still `SCHEMA_INVALID_TYPE`.
