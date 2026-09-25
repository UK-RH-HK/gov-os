# run-1: protocol notes, recorded before dispatch

* **View and store.** The frozen bridge tip is `94d0211`. The store is `$HOME/.cache/gov-bridge/store-BR-AR-0010`
  (manifest `11372e02…d5b0`). `govbridge freshness` reports NOOP. The packet is `packet/`, with `packet_sha256`
  `b5126140…2019`, and `packet verify` PASSES.
* **Task inputs added by the orchestrator.** The public query set (41 queries), the answers schema and the receipt
  schema all live under `ARCHITECTURE/`. The demonstration task's `retrieval_exclusions` forbid the agent from reading
  that directory, and neither the packet nor the bootstrap carries them. Without them the task cannot be answered.
  The orchestrator therefore copied them **verbatim** into `task-inputs/`; `PROVENANCE.txt` gives their blob ids and
  sha256.
  * They are public, builder-visible design data. They contain **no oracle content**.
  * The agent reads them as task inputs. They are **not** declared as external reads.
  * A verifier may judge that the compiler should carry the query set in section I itself. Recorded as OBS-BR-07.
* **Supplementary query outputs** go to `supplementary/queries/` (OBS-BR-06).
* **run-0** (`../run-0-predispatch-g-empty`) was compiled before BR-AR-0015 and never dispatched.
