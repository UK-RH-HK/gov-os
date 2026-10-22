---
id: DAEO-h8r2
status: open
deps: [DAEO-kl5e]
links: []
created: 2026-10-22T10:40:23Z
type: task
priority: 2
assignee: Usain
parent: DAEO-kl5e
state_class: AUTHORITATIVE
disposition: unclassed
---
# Repair DAEO-kl5e: merge eb0f1454f7e7 holds the probed commit and its probed pa

Findings of the refused close of DAEO-kl5e (disposition: unclassed):
- merge eb0f1454f7e7 holds the probed commit and its probed paths are not the probed code (git cannot compute its own merge of its parents): src/gov/guard/decide.py, src/gov/guard/protected.py, src/gov/launch/launcher.py, tests/acceptance/W2-50/test_w2_50_one_reader.py, tests/unit/guard/test_protected.py, tests/unit/guard/test_protected_one_reader.py
- the load_sensitive entry tests/acceptance/W1-38/test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md] (DEC-892) is refused: DEC-892 does not name the test tests/acceptance/W1-38/test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md]; it covers nothing
Not measured by that close:
- what the probe gate of DAEO-kl5e asks after this finding: not measured, the gate ends at its first

