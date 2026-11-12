# Brief td-1: independent test designer for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-cb2b (W2-121, part a: `gov dispatch tick` and
`gov dispatch status`). You write the acceptance tests from the ticket's KPI lines and its Interface section, before
the engineer's code exists. You never read the engineer's work on this ticket (branch w2/W2-121 after this brief,
`src/gov/dispatch/**`, `tests/unit/dispatch/**`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121-tests |
| branch | w2/W2-121-tests |
| your allowed paths | tests/acceptance/W2-121/** |
| ticket (read it first: KPI lines S1-S10 and F1 with their Verify, and the Interface section at its end) | /home/usain/gov-os-worktrees/W2-121-tests/.tickets/DAEO-cb2b.md |
| the command convention (how `gov <command>` is built, exit codes, the envelope) | src/gov/cli/main.py (docstring) |
| the gate you plant (read its docstrings: the planting variables, gate.json's form) | src/gov/resources/machine.py, src/gov/resources/config.py, src/gov/resources/gate.py |
| the lead's settings (the identity marker) | src/gov/launch/launcher.py `build_lead_settings` |
| the ready list `gov plan --ready` writes (S10) | src/gov/plan/render.py `ready_text` |
| the model, as a description only (read its README; not its code) | /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/README.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## What is in part a, and what is not
In: S1 (minus the installed host entry), S2, S3, S4, S5, S6 (the grep and the planted refusals; not the review record
or the switch-over), S7, S8 (as passes and items; not the restart of a real host), S9, S10, and F1's start half.
Out (other parts or the CTO's ACT at the last close; do not test): the host's cron or service entry, the switch-over
of this repository's dispatcher, landings (`land.txt` claimed, `land-done.txt`, the landing command, F1's landing
half), health checks, `gov watch`, `gov launch lead` itself.

