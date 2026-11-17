---
name: registry-dec-names-the-tool
description: a decision that approves a tool-registry entry (re-pin) must name the tool ("gov") in its register title, or W1-06's install-approvals case goes red after the registry commit
metadata:
  type: feedback
---

DEC-1198's title said "go 0.1.1", not "gov". The 0.1.1 re-pin's registry entry carries `approved_by: DEC-1198`, so after the owner's registry commit (c5ec26c36, 11-16 14:07) the landing check went red on tests/acceptance/W1-06/test_w1_06_install_approvals.py:176 ("approved by a decision that does not name the tool").

**Why:** the test reads the approving decision's title and requires the tool's name in it.

**How to apply:** when I record the decision that a re-pin's registry entry cites (the --dec of fill_release.sh), its title names the tool: e.g. "... release 0.1.1 and gov's re-pin ...". Check before handing the operator the line. Related: [[dec866-marks-with-every-changes]].
