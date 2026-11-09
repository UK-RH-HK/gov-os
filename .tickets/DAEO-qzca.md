---
id: DAEO-qzca
status: open
deps: []
links: []
created: 2026-11-09T21:30:00Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-151
tags: [wave-2, specification, links, lite]
wbs_id: W2-151
title: 'MR-1 to MR-6 regenerated from contract.yaml: the master-rule records say what the Contract says (D-6 part 2; DEC-1074 (8), DEC-1109 (2))'
class: specification
state_class: AUTHORITATIVE
role: product-spec
depends_on: []
allowed_paths:
- docs/contract/master-rules/MR-*.md
- docs/changes/W2-151-evidence.md
kpis:
  success:
  - 'S1 Each of docs/contract/master-rules/MR-1.md to MR-6.md is regenerated from docs/contract/contract.yaml at the branch''s base: its status is the Contract''s status (ACCEPTED today), its title and its Text and Acceptance lines are the contract file''s for that id, the Contract version it names is the contract file''s version, and its other front-matter keys (id, type, state_class DERIVED, depends_on CONTRACT-v4) are kept [DEC-623, DEC-1074 (8), DEC-1109 (2)]'
  - 'S2 gov links --all on the branch gives no STATUS_CONFLICT for MR-1 to MR-6 (six today) and no new finding of any code; the schema family of the structural pass passes on the six records [DEC-1073 (2), W2-129 S5]'
  failure:
  - 'A master-rule record whose status, title, text or acceptance differs from contract.yaml after the change.'
  - 'Any file changed outside the six records and the evidence note; contract.yaml or CONTRACT_v4.md touched (W2-139''s).'
profile: LITE
sources:
- W2-129
- DEC-1074
- DEC-1109
- DEC-623
- DEC-1073
est_loc: 20
track: B
list_rows: []
needs: []
waits_on: []
---
# W2-151 MR-1 to MR-6 regenerated from contract.yaml

Card: DEC-1074 (8)'s "MR-1..MR-6 status row", and the W2-130 sitting's row to D-6 part 2 (DECIDED-NOT-DONE row 24).
`02ee7e33` (DEC-623) generated one record per master rule from `contract.yaml` so the ids resolve; they still say
`status: PROPOSED` and "Contract v4, version 4.1", while `contract.yaml` says `ACCEPTED`, version 4.2. `gov links`
reports six STATUS_CONFLICTs, owner product-spec (W2-129's settled point (10)).

- **Why a new ticket (checked):** no open ticket holds `docs/contract/master-rules/`; W2-139 holds `contract.yaml`,
  `CONTRACT_v4.md` and `capabilities/**`, not these records; D-5's list carried the row but no ticket of D-5 holds the
  path. This ticket takes the row out of D-5's list.
- **Order:** after W2-139 lands if it changes a master rule's text in `contract.yaml`; otherwise now (a re-run after
  W2-139 costs minutes).
- **Plan:** `governance/project/orchestration/packages/LIFT-1/D6-PART2.md` item C: a product-spec worker, one review.

**Filed 2026-11-09 by the CTO (DEC-1109 (2)).**
