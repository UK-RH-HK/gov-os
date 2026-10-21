---
id: DAEO-8em0
status: open
deps: [DAEO-7rr2]
links: []
created: 2026-10-20T08:54:32Z
type: task
priority: 2
assignee: Usain
parent: DAEO-7rr2
state_class: AUTHORITATIVE
disposition: unclassed
---
# Repair DAEO-7rr2: /home/usain/Dynamic-Agentic-Engineering-OS/tests/acceptance/

Findings of the refused close of DAEO-7rr2 (disposition: unclassed):
- /home/usain/Dynamic-Agentic-Engineering-OS/tests/acceptance/W2-54/test_w2_54_green_here.py:26: AssertionError: context-reproducibility is RED here: [{"code": "CHECK_FAILED", "message": "ERROR: DAEO-pl6k: mandatory input 'DEC-636' is superseded and cannot satisfy a current requirement\ncontext-reproducibility: 0 ticket(s) failed, 1 error(s)"}]
- E   AssertionError: context-reproducibility is RED here: [{"code": "CHECK_FAILED", "message": "ERROR: DAEO-pl6k: mandatory input 'DEC-636' is superseded and cannot satisfy a current requirement\ncontext-reproducibility: 0 ticket(s) failed, 1 error(s)"}]
- ERROR tests/acceptance/W1-07/test_w1_07_check_declarations.py::test_a_declared_check_is_listed_with_its_five_fields[hard-block]
- ERROR tests/acceptance/W1-25/test_w1_25_check_declaration.py::test_gov_check_list_names_the_family_check
- ERROR tests/unit/secrets/test_scan_scale.py - ImportError while importing tes...
- ERROR tests/unit/secrets/test_secrets.py - ImportError while importing test m...
- ERROR tests/unit/secrets/test_token_rule.py - ImportError while importing tes...
- FAILED tests/acceptance/W1-42/test_w1_42_exit_report.py::test_governance_share_is_measured_and_at_most_15_percent_on_each_programme
- FAILED tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]
- FAILED tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here
- FAILED tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit
- tests/acceptance/W1-07/test_w1_07_check_declarations.py::test_a_declared_check_is_listed_with_its_five_fields[hard-block] is red (error) and accepted_reds does not list it
- tests/acceptance/W1-25/test_w1_25_check_declaration.py::test_gov_check_list_names_the_family_check is red (error) and accepted_reds does not list it
- tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here is red (failed) and accepted_reds does not list it
- tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit is red (failed) and accepted_reds does not list it
- governance check context-reproducibility is RED at commit 67245c6be45b: [{"code": "CHECK_FAILED", "message": "ERROR: DAEO-pl6k: mandatory input 'DEC-636' is superseded and cannot satisfy a current requirement\ncontext-reproducibility: 0 ticket(s) failed, 1 error(s)"}]
- governance check core-mutation is RED at commit 67245c6be45b: [{"code": "IMPLEMENTER_COVERS_ACCEPTANCE", "path": ".tickets/DAEO-k7hz.md", "id": "DAEO-k7hz", "pattern": "tests/acceptance/W1-35/test_w1_35_orchestration.py", "message": ".tickets/DAEO-k7hz.md: implementer allowed_paths pattern 'tests/acceptance/W1-35/test_w1_35_orchestration.py' covers tests/acceptance/"}, {"code": "IMPLEMENTER_COVERS_ACCEPTANCE", "path": ".tickets/DAEO-k7hz.md", "id": "DAEO-k7hz", "pattern": "tests/acceptance/W1-35/w1_35_orchestration_support.py", "message": ".tickets/DAEO-k7hz.md: implementer allowed_paths pattern 'tests/acceptance/W1-35/w1_35_orchestration_support.py' covers tests/acceptance/"}]
- governance check family 'context reproducibility' is RED at commit 67245c6be45b
- governance check family 'mutation scope' is RED at commit 67245c6be45b
- the latest checkpoint of DAEO-7rr2 is stale: age, commits

