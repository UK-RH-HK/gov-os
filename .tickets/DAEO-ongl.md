---
id: DAEO-ongl
status: in_progress
deps: [DAEO-5ce2]
links: [DAEO-h4rh, DAEO-5ce2]
created: 2026-11-07T18:26:33Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-139
tags: [wave-2, record, contract, standard]
wbs_id: W2-139
title: 'CAP-45.a to Wave 3: the approved CIT-P note applied to the Contract as version 4.3, with its CIT-E, merged in one batch with W2-140 (DEC-1093 (1))'
class: specification
state_class: AUTHORITATIVE
role: product-spec
depends_on: []
allowed_paths:
- docs/plan/tools/validate_w2.py  # the validator's ids: §2's cards with §1's table; an id after a hyphen is not a Contract id (D-10's red-fix list) [DEC-1112 (3), DEC-1109 (2)]
- tests/unit/plan/test_validate_w2.py  # its cases for those two reads [DEC-1109 (2)]
- docs/contract/contract.yaml
- docs/contract/CONTRACT_v4.md
- docs/contract/capabilities/**
- docs/contract/SOURCE_MAP.csv
- docs/changes/W2-27-CIT-P.md
- docs/changes/W2-27-CIT-E.md
kpis:
  success:
  - 'S1 The CIT-P note as approved (docs/changes/W2-27-CIT-P.md, 33f72aab on w2/W2-27-citp, with the owner''s answers V (i), A (i), C (i), R (a), T (i), N (b) written into it) is applied exactly: CAP-45 and CAP-45.a to Wave 3; the "in Wave 2" clause withdrawn, the manifest and file hashes kept beside the signed tag; version 4.3 with its change-log entry; every capability record''s version line 4.2 to 4.3 by the note''s exact rule; the three SOURCE_MAP rows. Verify: the note''s §5 patches against the diff, line by line [DEC-1093 (1), DEC-1090 (5)]'
  - 'S2 docs/changes/W2-27-CIT-E.md records each difference from the note, with its reason, or states there is none. Verify: the record [CAP-33, DEC-1093 (1)]'
  - 'S3 It merges and closes in one merge-queue batch with W2-140, on one green run of tests/acceptance/W2-49/ and the plan validator over the combined candidate, outside an experiment window. Verify: the queue''s record [DEC-988 (3), DEC-989 (2), DEC-1093 (1)]'
  failure:
  - 'A Contract change the approved note does not name.'
  - 'A merge apart from W2-140, or a red W2-49 run at the merge.'
profile: STANDARD
sources:
- DEC-1093
- DEC-1090
- DEC-1089
- DEC-105
- DEC-988
- DEC-989
- CAP-33
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-49/
  judged_by: 'tests/acceptance/W2-49/ as W2-140 leaves it, and the plan validator (docs/plan/tools/validate_w2.py) (the path added for gov accept, DEC-1093, DEC-1109 (2))'
track: B
list_rows: []
needs:
- docs/contract/contract.yaml
waits_on: []
---
# W2-139 CAP-45.a to Wave 3: the Contract edit (version 4.3)

The owner's DEC-1093 (1), approving the CIT-P note `docs/changes/W2-27-CIT-P.md` (drafted in W2-27, `DAEO-h4rh`,
DEC-1089 (2)(b), DEC-1090 (5); review `governance/project/orchestration/reviews/w2-27-citp.md`, READY) with V (i),
A (i), C (i), R (a), T (i) and N (b).

- **Why its own ticket (R (a)):** a ticket merges once and closes on merge (DEC-988 (3), DEC-989 (2)); W2-27 is
  EXAMIN's adoption and closes only after K9's entry criteria. This ticket carries the approved note to integrate with
  the edit.
- **With W2-140 (`DAEO-5ce2`):** W2-49's acceptance suite goes red at the edit; W2-140 revises it against the approved
  text first; both merge and close in one batch on one green run, outside an experiment window (the edit rewrites
  about 279 files, which shifts the store's line numbers).
- **N (b):** DEC-841's nine items stay for P1-11; if P1-11 is not applied when W2-46 starts, W2-46's record names them
  as exceptions for the owner. Not this ticket's.
- **Est.:** about 1 to 2 hours of product-spec, plus the queue batch.

[DEC-1093]
