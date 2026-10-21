
## 201. W1-42 lead run 2 returns PACKAGES and the W1-31 round returns DONE: delegated decisions (register v0.201, appended by the W1 orchestrator on branch `w1/integrate`)

Decided 2026-10-12 about 11:35, while the owner's quiet window in the main tree (the B1 apply) was open; appended on 2026-10-13 after the owner reported the apply done (`71ae763f`).

### DEC-662 — W1-42 lead's run 2 packages 2, 3 (names), 4, 6, 7 and 8, and its Wave 2 items
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-12; told to the owner, who may replace it) · **Basis:** the W1-42 lead's second return (`log/W1-42-lead-run2.json`, PACKAGES; branch `w1/W1-42` at `129b81c4`; a-dev clone at `8e517f9`, b-dev clone at `132ca2d`)
- **Decision** (each P3, reversible, on a throwaway clone of a synthetic programme; the lead's recommendation and mine agree; confidence medium or higher):
  - **Package 2, ORION:** the `TypeError` message names each of the two dimensions by its `repr`.
  - **Package 3, ARGUS, the names only:** `retention_decision(kind, created_at, now)`; kinds `"raw"` and `"final_image"`; results `"keep"` and `"expire"`; `ValueError` for both refusals; timezone-aware datetimes, a naive one refused. **Not decided: "now" before `created_at`** (the lead's confidence is low and my recommendation differs: with the owner).
  - **Package 4, a-dev:** `research/experiments/.notebook-export.env` and `research/experiments/deploy-key.pem` get a namespace of their own, `memory_class: product`, never indexed; A6 and A8 then run.
  - **Package 5 needs no decision:** DEC-658 already says b-dev is reported as adopted to A2 with the reason when one worker round is not enough. No second round. ARGUS's `gov close` is attempted once and its refusal reported.
  - **Package 6, a-dev records:** none blocks the cycle; left as the repair worker made them. Wave 2 list: the template's path map ships `paths` only (no `state_class`, `capabilities`, `policies`, `systems`, no `memory_class`, no `tests/**` namespace).
  - **Package 7:** a product-spec round gives the A5 verdict record a type the schema knows; commits in a clone cite in `Implements:` only ids the clone's store holds. History is not rewritten: what the earlier commits leave red is reported with the close.
  - **Package 8, the W1-42 test designer's three readings:** kept (a cycle table's "close: done" means a `gov close` whose answer has `ok` true, a `tk close` is "not reached"; the hit@5 figures are held to a truthful comparison with the baseline, no gate at 85; the clean-close ticket is the ORION implementation ticket).
  - **Wave 2 list additions:** `core-claims` and `gov readiness` disagree on which rows need a gap ticket; `gov rebuild` and the whole `gov check` cannot be used inside a launched session; `checker.close` writes an audit ticket citing DEC-088 and MR-4, which a project's own register does not hold; the adoption auditor could not reproduce the A3 `proposal_sha256`.
  - **Deviations of run 2, for the exit auditor:** the lead wrote clone ticket files and the a-dev path map itself; it wrote the all-KEEP A3 proposal; a-dev had two repair rounds; gap and adoption tickets were closed with `tk close` and a note; one b-dev worker ran a Bash here-document; the containment hook flagged the W1-42 designer's four test files in the lead's session and left them in place.
  - **With the owner at the time (answered in DEC-664 and DEC-666):** package 1 (the template's permission source denies every edit of `tests/acceptance/**`, the test designer's included) and package 3's "now" before `created_at`.

### DEC-663 — The W1-31 round's packages G, H and I
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-12; told to the owner, who may replace it) · **Under:** DEC-655, DEC-584 · **Basis:** the W1-31 round lead's return (`log/W1-31b-lead-run1.json`, DONE at `065f9b83` on `w1/W1-31b`) and the probe (`docs/probes/DAEO-6mk8/PR-DAEO-6mk8-round-DEC-655.md`, pass)
- **Decision** (each P3, reversible; confidence medium):
  - **G, a ticket whose sessions are of more than one Claude Code version:** stays as built. `agent.version` is "not measured" and the sessions are still counted. A named residual and a Wave 2 item (each session's own version in the record). No further round (finish line, DEC-584). The lead recommended a new public key per session; that is the Wave 2 item, so the two recommendations agree on the end state and differ only on when.
  - **H, attachment types and line types no specimen shows:** the standing rule is kept: a form no specimen shows is "not measured" by name. A fresh specimen is read at each CLI update. Wave 2 list: under this rule every log is "not measured" after an update until the new specimen is read.
  - **I, `instructions` and `sandbox_instructions` lines:** they count nothing today. Whether they replace the estimate is on the Wave 2 list.

| Version | Date | Change |
|---|---|---|
| 0.201 | 2026-10-13 | Orchestrator, delegated: DEC-662 (W1-42 lead's run 2 packages 2, 3 names, 4, 6, 7, 8; Wave 2 items; run 2's deviations for the exit auditor), DEC-663 (W1-31 round's packages G, H, I: as built, standing rule kept, Wave 2 items). Decided 2026-10-12, appended after the owner's B1 apply. Next free id: DEC-664. |
