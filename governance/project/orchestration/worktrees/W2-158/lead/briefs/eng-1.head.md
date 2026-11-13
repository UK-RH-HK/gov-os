# Brief eng-1: engineer for DAEO-8a3f (W2-158), profile STANDARD, class C2

You are the engineer for ticket DAEO-8a3f (W2-158: `gov check --structural`, one cheap, bounded pass over the declared
check families and the new links on a head, a notice and never a refusal). You implement it to the ticket's KPI lines
(S1-S5, F1-F4) and the Interface below (the ticket's Interface line and the lead's readings L1-L10), test first. You
write to the Interface; you never change it. A gap or a clash comes back as a package (status PACKAGES: question,
options with cost, recommendation, confidence, what it blocks), not as your own invention; a small reading it does not
settle goes into your evidence file and `unresolved`. The independent test designer writes the acceptance tests
(tests/acceptance/W2-158/) at the same time on another branch; you never read them (the guard refuses the
counterpart's work); the lead merges them into your branch later and tells you if they go red.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-158 |
| branch | w2/W2-158 |
| your allowed paths | src/gov/check/structural.py, src/gov/check/command.py, tests/unit/check/test_w2_158*, docs/changes/W2-158-evidence.md |
| the ticket (read it first, whole) | /home/usain/gov-os-worktrees/W2-158/.tickets/DAEO-8a3f.md |
| `gov check` today | src/gov/check/command.py, src/gov/cli/checks.py (declarations, both layouts), src/gov/cli/main.py (the command module convention in its docstring: CHILD_EXIT_CODE, reserved exit codes) |
| `gov links` (what the links line calls; its output form in its docstring) | src/gov/links/command.py, src/gov/links/check.py |
| the CTO's reference tool (the same pass; read it, port what fits; where it differs from the Interface, the Interface wins: no built-in commands, F3) | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/structural_pass.py |
| the package the ticket reads | governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md (row D9) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1052, DEC-1073, DEC-1119, DEC-1109 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

