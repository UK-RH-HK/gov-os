---
id: DAEO-nkk9
status: open
deps: [DAEO-pl6k]
links: []
created: 2026-10-21T23:11:19Z
type: task
priority: 2
assignee: Usain
parent: DAEO-pl6k
state_class: AUTHORITATIVE
disposition: unclassed
---
# Repair DAEO-pl6k: no acceptance tests for DAEO-pl6k in tests/acceptance/W2-63/

Findings of the refused close of DAEO-pl6k (disposition: unclassed):
- no acceptance tests for DAEO-pl6k in tests/acceptance/W2-63/
- "code": "RULESYNC_FAILED",
- FAILED tests/acceptance/W1-38/test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md]
- FAILED tests/acceptance/W1-42/test_w1_42_exit_report.py::test_governance_share_is_measured_and_at_most_15_percent_on_each_programme
- FAILED tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]
- the load-sensitive test tests/acceptance/W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[static.crates.io] failed in the run and failed alone too
- tests/acceptance/W1-38/test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md] is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[static.crates.io] is red (failed) and accepted_reds does not list it
Not measured by that close:
- the acceptance run of DAEO-pl6k: not measured, it has no acceptance tests

