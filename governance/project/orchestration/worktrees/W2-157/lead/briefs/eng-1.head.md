# Brief eng-1: engineer for DAEO-ozyt (W2-157), profile STANDARD, class C2

You are the engineer for ticket DAEO-ozyt (W2-157: the GPU backstop in the product). You implement
`gov resources --backstop <pgid>...` in a new module `src/gov/resources/backstop.py`, the one option in
`src/gov/resources/command.py` and the three configuration checks and this machine's entries in
`src/gov/resources/config.py`, conforming exactly to the Interface below (the ticket's Interface line and the lead's
readings L1-L9), so that the KPI lines S1-S5 hold and F1-F4 never happen. You conform to the Interface; you never
change it. A gap or a clash in it comes back as a package (status PACKAGES: question, options with cost,
recommendation, confidence, what it blocks); do not invent an interface. An independent test designer is writing the
acceptance tests (tests/acceptance/W2-157/) in parallel from the same Interface; you do not see them now and never
write there. Your lead merges them into your branch while you work or after you return.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157 |
| branch | w2/W2-157 |
| your allowed paths | src/gov/resources/backstop.py, src/gov/resources/command.py, src/gov/resources/config.py, tests/unit/resources/test_w2_157*, docs/changes/W2-157-evidence.md |
| the ticket (read it first, whole) | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| W2-20's gate: the command module convention, the configuration file and its checks, the GPU reading | src/gov/resources/command.py, config.py, machine.py (`gpu()`, for its parsing only: the backstop's query is L3's), src/gov/cli/main.py (docstring: exit codes, GovError) |
| W2-20's tests, which must stay green (the template's frozen key set among them) | tests/unit/resources/, tests/acceptance/W2-20/ (test_w2_20_config.py freezes `--init-config`'s keys) |
| the CTO's reference tool (the same triggers and the same pause; read only) | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/gpu_backstop.sh |
| the package the ticket reads | governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md (row D12) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1067, DEC-1068, DEC-1030, DEC-1073, DEC-1119, DEC-1109 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## Safety (the backstop pauses real process groups)
Your unit tests plant everything: their own process groups (children started with `start_new_session=True`), a stand-in
`nvidia-smi` first on `PATH`, stand-in HTTP servers on free ports (never 11434 or 11435), planted logs, a planted
`HOME` and project, all under `tmp_path`; each test's teardown sends SIGCONT then SIGKILL to its own groups. Never run
`--backstop` against a real group, the real GPU, the real HOME's gate.json or the real embedding servers; never signal a
process you did not start; nothing is matched by name.

