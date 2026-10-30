---
id: DAEO-ha8z
status: in_progress
deps: [DAEO-g0ip, DAEO-egsy]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-49
tags: [wave-2, specification, standard]
wbs_id: W2-49
title: 'Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)'
class: specification
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- DAEO-g0ip
- DAEO-egsy
allowed_paths:
- docs/contract/contract.yaml
- docs/contract/CONTRACT_v4.md
- docs/changes/W2-49-CIT-P.md
- docs/changes/W2-49-CIT-E.md
- docs/contract/capabilities/**
- docs/contract/SOURCE_MAP.csv
kpis:
  success:
  - 'The CIT-P names each change, its source (DEC-722) and its impact (W2-02, W2-16, W2-18, W2-27 to W2-30, exit criteria 6 and 7): CAP-44.h, lite: the three verdicts and the conditions a lite verdict checks;
    the A7 and A10 gates of CAP-44.f, lite, with what each lite gate checks and what stays for Wave 3; CAP-43.b, lite: the manifest and file hashes'
  - Contract v4.2 moves exactly those parts to Wave 2. CAP-02.c, A9, A11, the qualification certificate and the rest of CAP-43.b stay in Wave 3.
  - The plan validator's two-way check covers the moved parts.
  - The CIT-E record matches the CIT-P, or lists the differences.
  failure:
  - A Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator.
profile: STANDARD
sources:
- DEC-722
- CAP-33
- CAP-44.h
- CAP-44.f
- CAP-43.b
- CAP-02.c
- DEC-741
- DEC-744
- DEC-745
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-49/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- DEC-722
list_rows:
- W2-I017
- W2-L343
---
# W2-49 Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-49), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md` (the v4.2 text), `docs/changes/W2-49-CIT-P.md`, `docs/changes/W2-49-CIT-E.md`.
- **Route:** CIT-P, independent review, the owner's approval, versioned promotion (CAP-33).
- **KPIs, success:**
  - The CIT-P names each change, its source (DEC-722) and its impact (W2-02, W2-16, W2-18, W2-27 to W2-30, exit criteria 6 and 7):
    - CAP-44.h, lite: the three verdicts and the conditions a lite verdict checks;
    - the A7 and A10 gates of CAP-44.f, lite, with what each lite gate checks and what stays for Wave 3;
    - CAP-43.b, lite: the manifest and file hashes.
  - Contract v4.2 moves exactly those parts to Wave 2. CAP-02.c, A9, A11, the qualification certificate and the rest of CAP-43.b stay in Wave 3.
  - The plan validator's two-way check covers the moved parts.
  - The CIT-E record matches the CIT-P, or lists the differences.
- **KPIs, failure:** a Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator.
- **CIT-P approved (DEC-741, 2026-10-17, `0faa0664`)** with answers A to J. K: `docs/contract/capabilities/**` joins the paths for the version line in every record (and, as the orchestrator reads CIT-P §8, the records of the split and moved items; to be confirmed by the owner). Row W2-L343 (`contract.yaml` PROPOSED, `CONTRACT_v4.md` ACCEPTED) is this ticket's. It closes after W2-51 (DEC-744), whose validator its KPI uses. W2-I017 is carried to Wave 3 at W2-30's close (J).
- **DEC-745 (2026-10-17):** K confirmed (the eight records CAP-43, 43.b, 43.d, 44, 44.f, 44.h, 44.k, 44.l rewritten from the approved `contract.yaml`, in a commit of their own); `docs/contract/SOURCE_MAP.csv` joins the paths for the CIT-P §8's eight rows only, aligned with v4.2, made in the round that merges `w2/integrate` before the close.
