---
id: DAEO-feon
status: open
deps: [DAEO-blwa]
links: []
created: 2026-11-11T13:38:47Z
type: task
priority: 2
assignee: Usain
parent: DAEO-blwa
state_class: AUTHORITATIVE
disposition: unclassed
role: engineer
allowed_paths:
- src/gov/rebuild/seed.py
- src/gov/rebuild/command.py
- tests/unit/rebuild/test_w2_122*
- docs/changes/W2-122-evidence.md
kpis:
  success:
  - 'gov close DAEO-blwa no longer refuses for: commit 5bf20b53224d names no task and changes .tickets/DAEO-blwa.md, src/gov/rebuild/command.py: work on DAEO-blwa that no ticket measured'
  - 'gov close DAEO-blwa no longer refuses for: commit 419f828a8b51 names no task and changes src/gov/rebuild/command.py: work on DAEO-blwa that no ticket measured'
  - 'gov close DAEO-blwa no longer refuses for: commit 75acb0ff22e7 names no task and changes src/gov/rebuild/command.py: work on DAEO-blwa that no ticket measured'
  - 'gov close DAEO-blwa no longer refuses for: commit ffbf0392d236 names no task and changes .tickets/DAEO-blwa.md: work on DAEO-blwa that no ticket measured'
  - 'gov close DAEO-blwa no longer refuses for: commit 24b3bf2f67e5 names no task and changes .tickets/DAEO-blwa.md: work on DAEO-blwa that no ticket measured'
  - 'gov close DAEO-blwa no longer refuses for: commit 1296a57bc60b names no task and changes .tickets/DAEO-blwa.md, docs/changes/W2-122-evidence.md, src/gov/rebuild/command.py, src/gov/rebuild/seed.py, tests/acceptance/W2-122/README.md, tests/acceptance/W2-122/conftest.py, tests/acceptance/W2-122/test_w2_122_answer_and_record.py, tests/acceptance/W2-122/test_w2_122_configured_base.py, tests/acceptance/W2-122/test_w2_122_evidence.py, tests/acceptance/W2-122/test_w2_122_fail_closed.py, tests/acceptance/W2-122/test_w2_122_seeded_equals_cold.py, tests/acceptance/W2-122/w2_122_support.py, tests/unit/rebuild/test_w2_122_seed.py: work on DAEO-blwa that no ticket measured'
  - 'gov close DAEO-blwa no longer refuses for: the load_sensitive entry tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95 (DEC-757) is refused: DEC-757 is not accepted (its status: DONE (owner, 2026-11-09, DEC-1098 (3)); it was ACCEPTED (owner, 2026-10-17; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-704, DEC-718, DEC-734, DEC-736, DEC-737, DEC-750, DEC-754, DEC-372, DEC-588 · **Basis:** P-W2-19; `log/W2-01-close.json`. · **Changed by:** DEC-900: its two `accepted_reds` entries (W1-42''s RETR-X-02 and governance share) are retired; DEC-899 item 3: the W1-02 and W1-05 p95 `load_sensitive` entries are removed. · **Changed by:** DEC-953 (item 1)); it covers nothing'
  failure:
  - gov close DAEO-blwa refuses again for a finding of this ticket
repair_of_findings: findings-fd1814a0ef6aa30e
---
# Repair DAEO-blwa: commit 5bf20b53224d names no task and changes .tickets/DAEO-

Findings of the refused close of DAEO-blwa (disposition: unclassed):
- commit 5bf20b53224d names no task and changes .tickets/DAEO-blwa.md, src/gov/rebuild/command.py: work on DAEO-blwa that no ticket measured
- commit 419f828a8b51 names no task and changes src/gov/rebuild/command.py: work on DAEO-blwa that no ticket measured
- commit 75acb0ff22e7 names no task and changes src/gov/rebuild/command.py: work on DAEO-blwa that no ticket measured
- commit ffbf0392d236 names no task and changes .tickets/DAEO-blwa.md: work on DAEO-blwa that no ticket measured
- commit 24b3bf2f67e5 names no task and changes .tickets/DAEO-blwa.md: work on DAEO-blwa that no ticket measured
- commit 1296a57bc60b names no task and changes .tickets/DAEO-blwa.md, docs/changes/W2-122-evidence.md, src/gov/rebuild/command.py, src/gov/rebuild/seed.py, tests/acceptance/W2-122/README.md, tests/acceptance/W2-122/conftest.py, tests/acceptance/W2-122/test_w2_122_answer_and_record.py, tests/acceptance/W2-122/test_w2_122_configured_base.py, tests/acceptance/W2-122/test_w2_122_evidence.py, tests/acceptance/W2-122/test_w2_122_fail_closed.py, tests/acceptance/W2-122/test_w2_122_seeded_equals_cold.py, tests/acceptance/W2-122/w2_122_support.py, tests/unit/rebuild/test_w2_122_seed.py: work on DAEO-blwa that no ticket measured
- the load_sensitive entry tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95 (DEC-757) is refused: DEC-757 is not accepted (its status: DONE (owner, 2026-11-09, DEC-1098 (3)); it was ACCEPTED (owner, 2026-10-17; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-704, DEC-718, DEC-734, DEC-736, DEC-737, DEC-750, DEC-754, DEC-372, DEC-588 · **Basis:** P-W2-19; `log/W2-01-close.json`. · **Changed by:** DEC-900: its two `accepted_reds` entries (W1-42's RETR-X-02 and governance share) are retired; DEC-899 item 3: the W1-02 and W1-05 p95 `load_sensitive` entries are removed. · **Changed by:** DEC-953 (item 1)); it covers nothing

