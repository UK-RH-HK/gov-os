---
id: DAEO-kq8b
wbs_id: W2-194
external-ref: W2-194
status: open
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
- tests/unit/close/test_w2_194*
reads:
- src/gov/close/**
- drafts/w2-27-findings/PRODUCT-FINDINGS.md
needs: []
waits_on: []
est_loc: 150
kpis:
  success:
  - line: "S1 A red whose alone re-run is 'absent' but which is red in the base run's own selection at --base counts as a base red, not as the change's [DEC-1203 (3), F-030]"
    verify: "tests/unit/close/test_w2_194_absent.py: a fixture with a red absent in the alone run and red at the base: the verdict names it a base red and does not refuse RED_CAUSED for it"
  - line: "S2 --base accepts a short commit hash that names one commit (as git rev-parse resolves it), refusing an ambiguous or unknown one by name [DEC-1203 (3), F-030]"
    verify: "tests/unit/close/test_w2_194_base.py: --base with a 9-character hash closes as with the full hash; an unknown or ambiguous prefix is refused BASE_UNKNOWN / BASE_AMBIGUOUS"
  - line: "S3 In scoped mode a red that is red at the base and named in an ACCEPTED owner register entry with a Role: owner path-map accepted_reds entry is accepted as in strict mode, or the ticket's CIT-E states why scoped mode keeps no lists and names the owner's route [DEC-1203 (3), F-031]"
    verify: "tests/unit/close/test_w2_194_scoped.py: a scoped fixture with such an entry: accepted (or, if the CIT-E chooses no lists, the refusal names the route); an entry for a red that is new with the change is never accepted"
  failure:
  - line: "F1 A red that is new with the change is accepted, or a red absent in the alone run and green at the base is accepted"
    verify: "tests/unit/close/test_w2_194_absent.py: a red absent alone and green (or missing) at the base still refuses RED_CAUSED"
non_goals:
- "no change to the close's harness processes (W2-193)"
- "the ratchet's owner-entry rule (DEC-757) is kept, not loosened"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1203, DEC-1199, DEC-968, DEC-974]
acceptance_tests: {path: tests/acceptance/W2-194/}
---
# Absent reds matched against the base; scoped mode and owner-named base reds (F-030, F-031)

# W2-194 Absent reds matched against the base; scoped mode and owner-named base reds (F-030, F-031)

Filed 2026-11-16 by the CTO on the owner's word (DEC-1203 (3)).

**Problem (EXAMIN, exa-g6db's close; F-030, F-031).** gov close counted 111 reds of type `absent` as the change's though each is red at the base b17cd5a; `--base` refused a short hash (BASE_UNKNOWN); and `close: scoped` applies no `accepted_reds` (command.py:1136), so a scoped project has no route to accept reds red at its base.

**Approach.** Match absent reds against the base run's own selection; resolve short hashes; let scoped mode accept owner-named base reds under the ratchet's owner-entry rule (or record why not, with the owner's route). Evidence: `drafts/w2-27-findings/PRODUCT-FINDINGS.md` (F-030, F-031).
