---
id: DAEO-2upp
status: open
deps: [DAEO-uzme]
links: []
created: 2026-10-26T23:24:29Z
type: task
priority: 2
assignee: Usain
parent: DAEO-uzme
state_class: AUTHORITATIVE
disposition: unclassed
role: independent-test-designer
allowed_paths:
- tests/acceptance/W1-05/**
- tests/acceptance/W1-47/**
- tests/acceptance/serial-only.txt
- tests/acceptance/W1-30/test_w1_30_r11_declared_here.py
- tests/acceptance/W1-01/test_w1_01_history.py
- tests/acceptance/W1-01/w1_01_support.py
- tests/acceptance/W1-01/test_w1_01_integration_merges.py
kpis:
  success:
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Edit-docs/source/framework-v4.1.2.md] is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Edit-docs/source/protocol/distribution-v1.2.md] is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Read-docs/source/framework-v4.1.2.md] is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Read-docs/source/protocol/distribution-v1.2.md] is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-06/test_w1_06_install_approvals.py::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-47/test_w1_47_settings_rules.py::test_the_other_deny_rules_are_in_place[Edit(./docs/source/**)] is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-47/test_w1_47_settings_rules.py::test_the_other_deny_rules_are_in_place[Read(./docs/source/**)] is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W1-49/test_w1_49_precompact.py::test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH] is red (failed) and accepted_reds does not list it'
  - 'gov close DAEO-uzme no longer refuses for: tests/acceptance/W2-69/test_w2_69_unit_folder_renamed.py::test_the_unit_folder_named_secrets_is_gone is red (failed) and accepted_reds does not list it'
  failure:
  - gov close DAEO-uzme refuses again for a finding of this ticket
repair_of_findings: findings-1c3cda3bf5ee90d4
---
# Repair DAEO-uzme: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_doc

Findings of the refused close of DAEO-uzme (disposition: unclassed):
- tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Edit-docs/source/framework-v4.1.2.md] is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Edit-docs/source/protocol/distribution-v1.2.md] is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Read-docs/source/framework-v4.1.2.md] is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_docs_source_deny_rules_survive_the_change[Read-docs/source/protocol/distribution-v1.2.md] is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-06/test_w1_06_install_approvals.py::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-47/test_w1_47_settings_rules.py::test_the_other_deny_rules_are_in_place[Edit(./docs/source/**)] is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-47/test_w1_47_settings_rules.py::test_the_other_deny_rules_are_in_place[Read(./docs/source/**)] is red (failed) and accepted_reds does not list it
- tests/acceptance/W1-49/test_w1_49_precompact.py::test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH] is red (failed) and accepted_reds does not list it
- tests/acceptance/W2-69/test_w2_69_unit_folder_renamed.py::test_the_unit_folder_named_secrets_is_gone is red (failed) and accepted_reds does not list it

