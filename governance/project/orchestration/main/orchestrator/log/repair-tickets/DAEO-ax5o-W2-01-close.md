---
id: DAEO-ax5o
status: open
deps: [DAEO-g0ip]
links: []
created: 2026-10-17T12:46:26Z
type: task
priority: 2
assignee: Usain
parent: DAEO-g0ip
state_class: AUTHORITATIVE
disposition: unclassed
---
# Repair DAEO-g0ip: merge-back 3022c2df7b79 brings the probed commit but not the

Findings of the refused close of DAEO-g0ip (disposition: unclassed):
- merge-back 3022c2df7b79 brings the probed commit but not the probed code: .tickets/DAEO-g0ip.md differ from the probed commit
- FAILED tests/acceptance/W1-42/test_w1_42_exit_report.py::test_governance_share_is_measured_and_at_most_15_percent_on_each_programme
- FAILED tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]
- FAILED tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role]
- the latest checkpoint of DAEO-g0ip is stale: commits
- the context of DAEO-g0ip cannot be built: BLOCKED: mandatory input 'DEC-750' not found in the store
Not measured by that close:
- what the probe gate of DAEO-g0ip asks after this finding: not measured, the gate ends at its first

