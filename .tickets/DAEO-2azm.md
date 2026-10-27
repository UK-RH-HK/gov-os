---
id: DAEO-2azm
status: open
deps: []
links: []
created: 2026-10-27T11:57:11Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-74
tags: [wave-2, tests, settings, lite]
wbs_id: W2-74
title: 'The settings regeneration''s test revisions: the docs/source cases retired, W1-49''s sandbox gov, W2-69''s case name'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W1-01/test_w1_01_settings_deny.py
- tests/acceptance/W1-01/README.md
- tests/acceptance/W1-47/test_w1_47_settings_rules.py
- tests/acceptance/W1-47/README.md
- tests/acceptance/W1-49/test_w1_49_precompact.py
- tests/acceptance/W1-49/README.md
- tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py
- tests/acceptance/W2-69/README.md
kpis:
  success:
  - 'The six docs/source cases are retired, by the owner''s decision (DEC-925 item 1): W1-01''s test_docs_source_deny_rules_survive_the_change (its four cases, Read and Edit on docs/source/framework-v4.1.2.md and docs/source/protocol/distribution-v1.2.md) and W1-47''s test_the_other_deny_rules_are_in_place[Read(./docs/source/**)] and [Edit(./docs/source/**)]. The reason, in the Rewrite-Reason and the README: the docs/source folder left the tree on 2026-10-01, and the settings regeneration of DEC-922 dropped its two deny rules (P-I1-2, DEC-899). Every other deny rule those tests hold stays checked [DEC-925 item 1, DEC-899, DEC-922]'
  - 'W1-49''s test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH] gives its sandbox a gov (a link to the pinned gov, or the sandbox HOME''s .local/bin/gov), so that only tk is missing, as the case intends; the lifecycle hook line of DEC-917 then runs, and the case asserts what it asserted before (exit 0, the block says tk is missing, the rest held). Rewrite-Reason: DEC-917 [DEC-925 item 1]'
  - 'W2-69''s case whose name holds a keyword of row W2-L423''s rule is renamed (its function name or parametrize id), so that no test id holds one; its input and its assertions are unchanged (the keyword may stay in the input, written in parts as row W2-L423''s rule asks of tools and tests). Rewrite-Reason: DEC-911 [DEC-925 item 1]'
  - 'No other expectation is lowered: the full parallel run in the close''s form is green apart from the reds the ticket does not own, which the return names [DEC-866, DEC-906]'
  failure:
  - A deny rule other than the two docs/source ones left unchecked; W1-49's case passing with tk present; W2-69's case asserting less; any test id still holding a keyword of row W2-L423's rule.
profile: LITE
sources:
- DEC-925
- DEC-922
- DEC-917
- DEC-911
- DEC-899
- DEC-906
- DEC-866
est_loc: 30
acceptance_tests:
  path: tests/acceptance/W1-01/
  author: independent-test-designer (MR-3); revisions of W1-01, W1-47, W1-49 and W2-69
track: A
list_rows: []
---
# W2-74 The settings regeneration's test revisions: the docs/source cases retired, W1-49's sandbox gov, W2-69's case name

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-74), from package P-REPIN-R1 (owner, DEC-925 item 1).

- **Why:** W2-70's close (2026-10-26, refused, count 1) and W2-57's lead met the same base reds after the first re-pin's settings regeneration:
  - six cases enforce the two `docs/source` deny rules that were dropped;
  - W1-49's `[not on PATH]` case runs the new lifecycle hook line in a sandbox without gov.
  Every close is refused on them. W2-69's acceptance case with a keyword of row W2-L423's rule in its name puts the keyword into every run's JUnit XML under `.gov-runtime/`, which the early warning reads.
- **Place:** starts at once and merges before the close queue restarts, W2-70 first. A test-revision ticket: it closes on its declared `acceptance_tests.path`.
- **W1-06's red** (the registry entry's `approved_by`) is the orchestrator's record fix under DEC-925, not this ticket's.
