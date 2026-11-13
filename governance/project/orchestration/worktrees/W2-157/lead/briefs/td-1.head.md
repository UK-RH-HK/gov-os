# Brief td-1: independent test designer for DAEO-ozyt (W2-157), profile STANDARD, class C2

You are the independent test designer (MR-3) for ticket DAEO-ozyt (W2-157: the GPU backstop in the product,
`gov resources --backstop <pgid>...`). You write the acceptance tests from the ticket's KPI lines (S1-S5, F1-F4, each
with its Verify) and the Interface below (the ticket's Interface line and the lead's readings L1-L9), before the
engineer's code exists. You write to the Interface; you never change it. A gap or a clash in it comes back as a package
(status PACKAGES: question, options with cost, recommendation, confidence, what it blocks), not as your own invention;
a small reading the Interface does not settle goes into the test's docstring and `unresolved`. You never read the
engineer's work on this ticket (branch w2/W2-157 after this brief; `src/gov/resources/backstop.py` and any change to
`src/gov/resources/command.py` or `config.py` beyond your base; `tests/unit/resources/test_w2_157*`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157-tests |
| branch | w2/W2-157-tests |
| your allowed paths | tests/acceptance/W2-157/** |
| the ticket (read it first, whole) | /home/usain/gov-os-worktrees/W2-157-tests/.tickets/DAEO-ozyt.md |
| the gate's command and configuration at your base (the integrated code, DEC-963) | src/gov/resources/command.py, src/gov/resources/config.py |
| how `gov resources` is driven in a child process with a planted HOME, gate.json and a stand-in `nvidia-smi` (reuse its ideas; your files live under tests/acceptance/W2-157/) | tests/acceptance/W2-20/w2_20_support.py, conftest.py, test_w2_20_gpu.py, test_w2_20_tripwire.py |
| the CTO's reference tool (the same triggers and pause; read only; not code to test) | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/gpu_backstop.sh and test_gpu_backstop.sh |
| the package the ticket reads | governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md (row D12) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1067, DEC-1068, DEC-1030, DEC-1073, DEC-1119, DEC-1109 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## Safety (the backstop pauses real process groups)
Every test plants its own process groups (children it starts with `start_new_session=True`, each its own group), a
stand-in `nvidia-smi` (a small script first on `PATH`, answering from a planted sequence, one reading per call, and
answering any other argument form with nothing and exit 0), stand-in embedding servers (small HTTP servers in the test on
free ports, never 11434 or 11435) and planted embedder logs, all under pytest's `tmp_path`, with a planted `HOME`
(`gate.json` at `$HOME/.gov-os/machine/gate.json`) and a planted project root (`--root`). Never the real GPU, the real
HOME, the real embedding servers, the reranker, or any process the test did not start; nothing is matched by name. Every
test's teardown sends SIGCONT then SIGKILL to each group it started (they may be stopped) and waits for them.

