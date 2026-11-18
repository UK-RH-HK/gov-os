---
id: DAEO-kq8b
wbs_id: W2-194
external-ref: W2-194
status: in_progress
deps: []
links: []
created: 2026-11-16T15:51:18Z
type: task
priority: 2
assignee: Usain
parent: DAEO-sdxk
tags: [wave-2, close, adoption]
class: implementation
role: engineer
profile: STANDARD
state_class: AUTHORITATIVE
allowed_paths:
- src/gov/close/command.py
- src/gov/close/ratchet.py
- src/gov/close/batch.py
- src/gov/close/select.py
- src/gov/close/attribution.py
- tests/unit/close/test_w2_194*
reads:
- src/gov/close/**
- drafts/w2-27-findings/PRODUCT-FINDINGS.md
needs: []
waits_on: []
est_loc: 150
kpis:
  success:
  - line: "S1 A red whose alone re-run is absent but which is red, with the same failure type, in the base run's own selection at the base counts as a base red, not as the change's [DEC-1203 (3), F-030]"
    verify: "tests/acceptance/W2-194/ (README map, S1): a planted red absent in its alone run and red at the base run: the close does not refuse RED_CAUSED for it and its record entry is caused: false"
  - line: "S2 --base accepts a short commit hash that names one commit (as git rev-parse resolves it) and closes as with the full hash; an unknown prefix is refused BASE_UNKNOWN and an ambiguous one BASE_AMBIGUOUS, each naming what was given [DEC-1203 (3), F-030]"
    verify: "tests/acceptance/W2-194/ (S2): --base with a 9-character hash closes as with the full hash (the record's base is the full id); an unknown prefix and an ambiguous prefix are refused by those codes"
  - line: "S3 In scoped mode a red that is red at the base (its alone run there or the base run) and listed by a path-map accepted_reds entry that counts (an ACCEPTED owner register entry naming it, added by Role: owner commits, DEC-757's rule unchanged) is accepted: no RED_CAUSED, the close record's accepted_reds names it with its decision, and no repair ticket is opened for it; an entry that does not count covers nothing and is named in the record [DEC-1203 (3), DEC-1206 (1), F-031]"
    verify: "tests/acceptance/W2-194/ (S3): a scoped planted project with such an entry for a red whose type differs at the base (so the judgement alone calls it caused): the close passes, accepted_reds names it, no repair ticket names it; the same entry added by a commit without Role: owner: RED_CAUSED"
  failure:
  - line: "F1 A red that is new with the change is accepted, or a red absent in the alone run and green (or not collected) at the base is accepted"
    verify: "tests/acceptance/W2-194/ (F1): a listed red green at the base refuses RED_CAUSED; a red absent alone and green or missing at the base run refuses RED_CAUSED"
non_goals:
- "no change to the close's process layout (W2-193)"
- "the ratchet's owner-entry rule (DEC-757) is kept, not loosened; the strict close unchanged"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1203, DEC-1199, DEC-968, DEC-974]
acceptance_tests: {path: tests/acceptance/W2-194/}
---
# Absent reds matched against the base; scoped mode and owner-named base reds (F-030, F-031)

# W2-194 Absent reds matched against the base; scoped mode and owner-named base reds (F-030, F-031)

Filed 2026-11-16 by the CTO on the owner's word (DEC-1203 (3)).

**Problem (EXAMIN, exa-g6db's close; F-030, F-031).** gov close counted 111 reds of type `absent` as the change's though each is red at the base b17cd5a; `--base` refused a short hash (BASE_UNKNOWN); and `close: scoped` applies no `accepted_reds` (command.py:1136), so a scoped project has no route to accept reds red at its base.

**Approach.** Match absent reds against the base run's own selection; resolve short hashes; let scoped mode accept owner-named base reds under the ratchet's owner-entry rule (or record why not, with the owner's route). Evidence: `drafts/w2-27-findings/PRODUCT-FINDINGS.md` (F-030, F-031).
