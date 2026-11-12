# Brief eng-1: engineer for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You implement ticket DAEO-cb2b (W2-121, part a): `gov dispatch tick` and `gov dispatch status`, the generic core of
the dispatcher. An independent test designer writes the acceptance tests (tests/acceptance/W2-121/) in parallel; you
never read them (the guard refuses the counterpart's work). Write your own unit tests as you go (test first).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121 |
| branch | w2/W2-121 |
| allowed paths | src/gov/dispatch/**, tests/unit/dispatch/** |
| ticket (read it first: KPI lines S1-S10 and F1, and the Interface section at its end) | /home/usain/gov-os-worktrees/W2-121/.tickets/DAEO-cb2b.md |
| the command convention (module, run(), EXIT_CODES, the reserved 0/1/2) | src/gov/cli/main.py (docstring) and an example: src/gov/launch/command.py, src/gov/plan/command.py |
| the gate (W2-20): reuse, never copy | src/gov/resources/config.py (gate.json, memory_floor_bytes, working_size_bytes), gate.py (`read`, `check_disk`), machine.py (memory, load, nproc, busy cores, processes; the GOV_RESOURCES_* planting variables), registry.py / slots.py (slots held, read-only) |
| the identity marker | src/gov/launch/launcher.py `build_lead_settings`, `LEAD_ROLES` |
| the ready list `gov plan --ready` writes (S10) | src/gov/plan/render.py `ready_text` |
| the reference (read for ideas; never a target, never copy its project-specific names) | /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/ (README.md, dispatcher.py, balancer.py) |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## What is in part a, and what is not
In: S1 (minus the installed host entry), S2, S3, S4, S5, S6 (the code generic and the refusals tested), S7, S8, S9,
S10, and F1's start half. Out (W2-121b/c/d or the CTO's ACT at the last close): landing (`land.txt` is only shown as
the queue), health checks, `gov watch`, `gov launch lead` itself, the host's cron entry, the switch-over.
Size: the ticket estimates about 500 lines for the part; keep it plain (standard library, git through subprocess with
a timeout; `yaml` as the repository already uses it). Split the module into a few files (config, state, readiness,
peaks, returns, status, command) rather than one long one.
Exit code 2 for a configuration error: 2 is reserved to the command line for usage errors; find the convention's
legal way (read `src/gov/cli/main.py`: e.g. `CHILD_EXIT_CODE`, or a usage error) and say which in the evidence.

