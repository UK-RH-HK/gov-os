---
id: DAEO-6b2q
status: closed
deps: []
links: []
created: 2026-10-31T12:40:26Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-109
tags: [wave-2, specification, contract, standard]
wbs_id: W2-109
title: 'Contract v4.3: DEC-841''s nine items moved to Wave 3 by a CIT-P, CAP-53.b split, and contract.yaml the Contract''s authority with its two forms checked to agree'
class: specification
state_class: AUTHORITATIVE
role: product-spec
depends_on: []
allowed_paths:
- docs/contract/contract.yaml
- docs/contract/CONTRACT_v4.md
- docs/contract/capabilities/**
- docs/contract/SOURCE_MAP.csv
- docs/changes/W2-109-CIT-P.md
- docs/changes/W2-109-CIT-E.md
- docs/plan/tools/validate_w2.py
- tests/unit/plan/test_validate_w2_forms*
kpis:
  success:
  - 'A CIT-P addendum moves DEC-841''s nine items (CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d, CAP-37.e and CAP-53.b) from Wave 2 to Wave 3 in both Contract forms, with its independent review, an answer round and the owner''s approval before the text changes (CAP-33); the version becomes v4.3 [DEC-971 item 2, DEC-841, CAP-33]'
  - 'CAP-53.b is split as v4.2 split others: its id keeps the lite Wave 2 part (impact-selected tests at a close), with W2-66 its provider; the Wave 3 rest (a profile computed from impact) gets a new id [DEC-971 item 2, DEC-880]'
  - 'contract.yaml is the Contract''s authority (DEC-971 item 2): CONTRACT_v4.md gains the three providers it lacks (W1-35 for CAP-28 and CAP-28.a, W1-26 for CAP-30.e), and the 276 capability records'' authority line names DEC-971 instead of DEC-614 [DEC-971 item 2, DEC-825 item 3]'
  - 'A contract-forms-agree check in docs/plan/tools/validate_w2.py compares the two forms item by item (ids, waves, providers, status) and fails on any difference, with builder tests; on v4.3 it passes, and the validator''s contract-items-delivered and contract-items-cited-by-tests no longer fail on the nine [DEC-971 item 2, DEC-825 item 3]'
  - 'A CIT-E records what changed and the validator''s lines before and after [DEC-971 item 2, CAP-33]'
  failure:
  - 'The Contract''s text changed before the CIT-P''s review and the owner''s approval.'
  - 'Either form left with one of the nine in Wave 2, or the two forms differing.'
  - 'CAP-53.b moved whole, or split without W2-66 as the lite part''s provider.'
  - 'A record''s authority line still naming DEC-614.'
profile: STANDARD
sources:
- DEC-971
- DEC-841
- DEC-825
- DEC-880
- DEC-741
- DEC-614
- CAP-33
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W2-109/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer in its own tests worktree (DEC-959 item 7, DEC-963)
track: A
list_rows: []
---
# W2-109 Contract v4.3

From the owner's DEC-971 item 2 (P1-MORNING-2026-10-31 item 2, W2-49's P-A (b) and P-B).

- **Why:** DEC-841 moves nine Wave 2 items to Wave 3 "through W2-49's CIT-P", but W2-49's approved CIT-P (DEC-741) predates it. All nine are still `wave: W2` in `contract.yaml`, so the Contract and the plan disagree, and the validator fails `contract-items-delivered` (CAP-22.c) and `contract-items-cited-by-tests` (eight of the nine). W2-49 closed on v4.2 as built and approved.
- **The forms (P-B):** on v4.2 the two forms differ only on three provider lists (CAP-28 and CAP-28.a lack W1-35, CAP-30.e lacks W1-26 in `CONTRACT_v4.md`). All 276 records name `contract.yaml` the authority "by DEC-614", which names none; DEC-971 now does.
- **Paths:** W2-49's Contract files, and W2-51's validator (W2-51 is closed). No running ticket holds them.
- **The work order:** the CIT-P first, then its review and the owner's answer, then the text. The test designer writes the forms-agree and wave tests from these KPIs in parallel.

**D9-FATES (DEC-1083):** Retired by DEC-1083 (D9-FATES): it built nothing (W-6); K-2 is retired into P1-11's Contract re-baseline.
