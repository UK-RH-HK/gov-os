# Later-lifecycle notes — not Phase-2 blockers (P2-AR-0007)

The frozen gate contract §7 keeps these out of this gate: R2 certification, R3 high assurance, Phase-3 profile
selection, Phase-4 synthetic qualification and hidden faults, Phase-5 bake-off, public/cloud assurance, and the open
D-0007 transition record. Each note below records the evidence, the lifecycle point it belongs to, and whether a
Phase-2 repair makes it easier or harder.

## R2 — standard release certification

- **Certification can be minted without evidence** (epsilon-r A0-O5-15, INFO). `gov release build --certification
  CERTIFIED` produces a CERTIFIED manifest with empty implementer and verifier evidence. For Phase 2, the *use* of an
  unauthenticated certification claim in gating is blocking (BC-P2-37). Admitting CERTIFIED only with bound certification
  evidence and an independent verifier is R2.
- **R1 item 11 is not capability evidence** (S0-R1-01). R1 dispositioned "Gate W and G0-G6 implementation mappings
  remain valid" on unmodified builder suites. R2 requires "Gate W dependency/consumption evidence" and "G6 and release
  qualification required by Contract v3" (frozen SRR boundary §R2). That evidence must come from repaired BC-P2-04…07 and
  BC-P2-17…23, not from R1-11.
- **Key custody, production signatures, rotation/revocation drill** (alpha-r §9). Only product mechanics were exercised,
  with throw-away keys. The Phase-1 residual AR27-N5 (a `minimum_secure_release` published without a sequence never
  raises the floor, alpha-r A2-05 [K5b]) stays an R2 item, as does the rest of `PHASE-1-RESIDUAL-RISKS.md`.
- **Capability evidence population** (AR27-N7). Phase 1 recorded it as R2. The frozen Phase-2 contract makes
  suite-to-contract owners an AC-10 criterion, so it is a Phase-2 blocker here (BC-P2-02). R2 still needs *current*
  evidence at certification time.
- **OD-P2-02 option C** (embedded production root keys) depends on R2 key custody.

## R3 — optional high assurance

- **Agent-role authentication against a hostile agent** (OD-P2-01 options B/C) needs agent process isolation. It is
  recommended for reconsideration at R3.
- **Protected machine-state relocation** by an owner-privileged process (OWNER-DECISION-0007 §1): accepted in-boundary
  and not reopened.

## Phase 3 — provisional retrieval profile (`PROVISIONAL_RETRIEVAL_PROFILE_READY`)

- Selecting the profile is Phase 3 (frozen contract §9.1). This gate requires the executable, evidenced path to do it,
  and that path is not yet adequate: BC-P2-30, plus pipeline defects BC-P2-25/26 that cap quality whatever profile is
  chosen.
- The starter held-out set generated at `gov init` only tests exact id/path/symbol/literal queries and does not
  discriminate between candidates (beta-r §5). Phase 3 must author paraphrase sets. The mechanism supports this (shown
  with auditor-authored queries).
- No real neural embedder or reranker was exercised. None is available offline and D-0006 ships none. Absolute
  paraphrase quality is a Phase-3 measurement.
- Until BC-P2-19's W10 outage requirement is met, every re-pin makes context delivery fail until a full rebuild
  completes (zeta-r §13). Phase 3 re-pins the embedder.

## Phase 4 — synthetic qualification and hidden oracle

- Hidden-fault generation, the W-QC-* challenge repositories, G6 injection of artefact-flow failures (W12:1192,
  recorded N/A_WITH_REASON at bullet level by zeta-r and accepted), chaos and soak. The qualification coverage matrix
  (`qualification-coverage-matrix.yaml`) is the plan. Its challenges were proposed by the families and checked here
  for completeness, not executed.
- The oracle *format* is a Phase-2 obligation (BC-P2-51, AC-6). Generating faults against it is Phase 4, after a fresh
  independent acceptance.
- If OD-P2-02 is answered A or C, qualification runs on provisioned machines. If answered B, qualification evidence must
  exclude the marked unprovisioned mode.
- If OD-P2-01 is answered A, adversarial-agent fault classes measure a known, accepted gap.
- Scale beyond 3 000 documents, Windows path semantics for rebuild determinism (D6:354), and cross-repository lineage
  (W8:1152, single-repository product) were not exercised and have no Phase-2 normative trigger.

## Phase 5 — reference retrieval bake-off

- Uses the Phase-4 repositories. Depends on BC-P2-30 (bound model artefacts and governed profile change) being
  repaired first.

## Adoption / operations

- Upstream remote transport is not configured (alpha-r §9). The export *gate* is Phase 2 (BC-P2-50); transport is an
  operations matter.
- Model/API spend is self-reported through `gov route --record` (alpha-r A0-A4-01, non-blocking). Real provider spend
  is observable only in operation.
- An adoption re-run (A0 "detect interrupted prior governance work") is expected in operation. BC-P2-33 (OS state
  archived as legacy) and S0-W1-01 (catalogue ids positional) make it unsafe today. Both are Phase-2 blockers, so they
  are not deferred here.

## Open, not requested

- The D-0007 explicit transition record (frozen contract §7). No Phase-2 requirement in `repair-delta.md` needs it:
  BC-P2-35 strengthens detection without amending D-0007's text. If a repair believes it must amend D-0007, that is the
  owner's transition record and must be raised, not assumed.

## Non-product tooling

- `release/orchestration/phase-2/tools/product_identity.py` prints the annotated-tag object id as `commit` when given a
  tag name (S0-AC09-01, INFO). Digests are unaffected. A one-line `^{commit}` fix is recommended before later gates cite
  tag output.
