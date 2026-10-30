---
id: DAEO-pl6k
status: closed
deps: []
links: []
created: 2026-10-20T07:13:30Z
type: task
priority: 0
assignee: independent-test-designer
external-ref: W2-63
tags: [wave-2, test-revision, lite]
wbs_id: W2-63
title: 'W1-49''s two window tests follow DEC-838: no compaction threshold, the model''s own window'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W1-49/test_w1_49_live_session.py
- tests/acceptance/W1-49/test_w1_49_threshold.py
- tests/acceptance/W1-49/w1_49_support.py
- tests/acceptance/W1-49/README.md
kpis:
  success:
  - 'tests/acceptance/W1-49/test_w1_49_threshold.py''s case that required CLAUDE_CODE_AUTO_COMPACT_WINDOW to be set for every session on this machine asserts DEC-838 instead: no launch and no settings
    file passes a compaction threshold (the variable is absent from the project''s settings env and from the commands a session gives its tools), so the session uses its model''s full window [DEC-838]'
  - 'tests/acceptance/W1-49/test_w1_49_live_session.py''s case that required the session to report a 300k window from CLAUDE_CODE_AUTO_COMPACT_WINDOW asserts DEC-838 instead: the session reports
    its model''s own window (the default for that model), not a threshold from a setting [DEC-838]'
  - 'Each change carries Rewrite-Reason: DEC-838; no other expectation changes; nothing is deleted or skipped; the README''s table and history name the change [DEC-838, DEC-865]'
  failure:
  - With CLAUDE_CODE_AUTO_COMPACT_WINDOW set in a session's environment or in the project's settings env, the revised threshold case fails; a session that reports a threshold from a setting fails the revised live case.
profile: LITE
sources:
- DEC-838
- DEC-665
- DEC-865
est_loc: 40
acceptance_tests:
  path: tests/acceptance/W1-49/
  author: independent-test-designer (MR-3); the revision is the deliverable
track: A
closes:
- P-W2-52
list_rows: []
---
# W2-63 W1-49's two window tests follow DEC-838: no compaction threshold, the model's own window

From P-W2-52 (a) (owner, 2026-10-20; DEC-865). W1-49's two cases from DEC-636 and DEC-665 require a 300k `CLAUDE_CODE_AUTO_COMPACT_WINDOW` for every session on this machine; DEC-838 (owner, 2026-10-19) retired it: every session uses its model's full window, and no launch sets a compaction threshold. Both cases now fail on every tree, so every close's regression would refuse. **Finish before W2-53's close.**

- **Role:** a fresh independent test designer only (MR-3), run by the ticket's lead; no implementation follows.
- **Allowed paths:** `tests/acceptance/W1-49/test_w1_49_live_session.py`, `tests/acceptance/W1-49/test_w1_49_threshold.py`, `tests/acceptance/W1-49/w1_49_support.py` and `tests/acceptance/W1-49/README.md`, for those two cases only.
- **KPIs, success:**
  - `test_w1_49_threshold.py`'s case that required the variable to be set for every session asserts DEC-838 instead: no launch and no settings file passes a compaction threshold (the variable is absent from the project's settings env and from the commands a session gives its tools), so the session uses its model's full window.
  - `test_w1_49_live_session.py`'s case that required a 300k window from the variable asserts DEC-838 instead: the session reports its model's own window (the default for that model), not a threshold from a setting.
  - Each change carries `Rewrite-Reason: DEC-838`; no other expectation changes; nothing is deleted or skipped; the README's table and history name the change.
- **KPIs, failure:** with the variable set in a session's environment or in the project's settings env, the revised threshold case fails; a session that reports a threshold from a setting fails the revised live case.

**DEC-892 (owner, 2026-10-22):** merged, not closed. Its close refused on NO_ACCEPTANCE_TESTS (2026-10-22 00:11): the close looks for `tests/acceptance/W2-63/`, and a test-revision ticket has none. It waits for W2-07, whose close judges a test-revision ticket on its declared `acceptance_tests.path`. No tests are written into a W2-63 folder, no exception, no decision-close.
