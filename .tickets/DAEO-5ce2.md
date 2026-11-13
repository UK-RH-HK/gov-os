---
id: DAEO-5ce2
status: closed
deps: []
links: [DAEO-ongl, DAEO-h4rh]
created: 2026-11-07T18:26:34Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-140
tags: [wave-2, tests, contract, standard]
wbs_id: W2-140
title: 'W2-49''s acceptance suite revised for Contract 4.3 (CAP-45 and CAP-45.a to Wave 3), written against the approved CIT-P note before the edit, merged in one batch with W2-139 (DEC-1093 (1))'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-49/**
kpis:
  success:
  - 'S1 Each case the note''s §4 row 18 and the review''s F1 name as red at the edit (the require_v42 helper and its callers, :69, :77, the covers counts, the two "exactly" tests, the D (ii) tests, the source-map test, test_w2_49_owner_answers.py:143, test_w2_49_source_map.py:115, test_w2_49_contract.py:77, the validator edge case) is revised to the approved text, each with Rewrite-Reason naming DEC-1093; no expectation lowered beyond the owner''s change, every 4.2 lite check kept. Verify: the diff and the reasons [DEC-1093 (1), MR-3]'
  - 'S2 The version check reads 4.2 or later; the covers counts W1 149 / W2 19 / W3 39 / NONE 7 (214); CAP-45 and CAP-45.a named as moved by DEC-1093; the D (ii) tests: CAP-45.a is W3 and its authenticated source names the signed tag and the manifest and file hashes; the source-map rows 107, 224 and 286 as moved; the validator edge case on an item that stays W2 (for example CAP-61.f). Verify: the cases [DEC-1093 (1)]'
  - 'S3 Red on integrate before the edit, for the right reason only (the Contract still at 4.2); green on W2-139''s candidate; merged in the same batch. Verify: both runs'' counts [DEC-1093 (1)]'
  failure:
  - 'A case loosened beyond the approved change, or a revision without its Rewrite-Reason.'
profile: STANDARD
sources:
- DEC-1093
- DEC-1090
- DEC-1088
- MR-3
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-49/
  judged_by: 'W2-139''s candidate: tests/acceptance/W2-49/ green on it (the path added for gov accept, DEC-1093, DEC-1109 (2))'
track: B
list_rows: []
needs:
- tests/acceptance/W2-49/
waits_on: []
---
# W2-140 W2-49's acceptance suite for Contract 4.3

The owner's DEC-1093 (1), T (i): W2-49 is closed, so revising its suite is new work (DEC-1088 (6)), by an independent
test designer only (MR-3). Written against the approved note before W2-139's edit; red on integrate until the edit;
merged and closed with W2-139 (`DAEO-ongl`) in one batch on one green run, outside an experiment window.

- **The red list** is the note's §4 row 18 under V (i) and A (i) (the helper plus ten functions with new content) with
  the review's three additions (F1).
- **Est.:** about 3 hours.

[DEC-1093]
