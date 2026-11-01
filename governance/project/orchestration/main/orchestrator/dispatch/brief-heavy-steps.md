# Draft for the common lead brief: every heavy step takes a slot (DEC-1008 item 5)

*To replace the brief's "Rebuilds share the heavy-job slots" bullet; the CTO commits it after review.*

- **Every heavy step takes one of the machine's three heavy-job slots (owner, DEC-979 D1, DEC-1001, DEC-1008 item 5).**
  A heavy step is anything that keeps several cores or gigabytes busy for minutes. Run each one through a slot, and
  only through a slot:
  - **test runs:** `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <the pytest command>` (unchanged);
  - **rebuilds:** `PYTHONPATH=<tree>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh <tree>` (unchanged);
  - **`gov check`**, the **context check** (`python3 -m gov.context.context_check`), the **retrieval check**
    (`python3 -m gov.retrieval.retrieve_check`), the **schema check** (`python3 -m gov.check.schema`) and the **memory
    measure** (`python3 -m gov.retrieval.measure`, or `tools/` scripts that run it):
    `PYTHONPATH=<tree>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <the command and its arguments>`.
- `heavy_slot.sh` waits for a free slot (it says so once on stderr), holds it for the whole command, frees it when the
  command's own process ends, and exits with the command's code. It caps pytest-xdist's `-n auto` at the slot's
  workers (6), so a run inside it never takes the whole machine. Start it in the background with an exit-code file,
  like any long run.
- Not heavy (no slot): a single test or a single file of tests, `gov retrieve` for one question, `gov accept`, `git`,
  reading and writing files.
- Why: on 2026-11-01 the steps outside the slots (the leads' `gov check`, context and retrieval checks) used about
  17.7 of the 20 cores between them, against 7.5 for all the slotted test runs, and kept the load near 60 while the
  gate read only the moment. The dispatcher now admits a lead by each job's measured peak, and names a heavy step
  running outside a slot for more than 5 minutes as a finding that holds new starts.
