# P2-AR-0052 — later-lifecycle notes

Real observations from this verification whose normative home is not Phase 2. Under frozen gate contract §7 none of
them is a Phase-2 blocker, and none was counted toward the verdict. They are recorded so the work is not lost.

## Phase 3 — provisional retrieval profile (`PROVISIONAL_RETRIEVAL_PROFILE_READY`)

- **`V1-BETA-03` is the item to read first.** AC-7 holds: the candidate provides the executable, evidenced path
  frozen §9.1 requires — D4's ten separately identifiable components with an out-of-band swap reported
  `UNGOVERNED`/high, and D5's full governed chain (benchmark → Human Decision Gate → owner-signed answer → pin →
  complete re-index → recorded regression, with automatic rollback). But the held-out set the **product itself**
  generates leaves its semantic paraphrase queries pending, so every embedder candidate measures identically
  (`current` 512-d and a second candidate scored the same), and a governed profile selection can therefore rest on
  evidence that cannot discriminate the component being selected. Phase 3 should not select a profile on the
  generated set as it stands. The product reports `pending_queries` but neither refuses nor flags a selection made
  on it.
- **`V1-BETA-08`** compounds this: two generated graph queries expect the seed itself where the graph route returns
  the seed's dependants, so they can never pass, and every project's Recall@K baseline sits at 0.93 rather than 1.0
  for a reason unrelated to retrieval quality. A Phase-3 bake-off measured against that baseline would be measuring
  partly the defect.
- **`V1-OF-06`** — V1–V3 carry no health-scheduler tier in the evidence map, which matters once a profile is pinned
  and Gate V records begin to be observed.

## Phase 4 — advanced qualification and hidden faults

- **The oracle format is accepted (AC-6) and its remaining findings are Phase-4 authoring work**, all six labelled
  `PROPOSES_STRONGER_LATER_ASSURANCE` by P2-AR-0045 and confirmed by me:
  `V1-OF-01` the hidden-oracle leak scan misses governed-record types and any reformatting of a hidden truth;
  `V1-OF-02` four V4 metrics, three count-metric ref lists and two per-fault judgements are not bound to the oracle;
  `V1-OF-03` three V2 bullets and two V1 detection sub-fields are free text with no vocabulary;
  `V1-OF-05` the acceptance status lives inside the digested definition, so accepting it in the file would change
  the digest — which is why frozen §9.2 puts the acceptance outside it, in P2-AR-0045's report.
  A Phase-4 oracle author should close `V1-OF-01` and `V1-OF-02` **before** generating hidden faults: a leak scan
  that misses a reformatted truth and metrics not bound to the oracle are exactly the failures that would be
  discovered too late.
- **Cross-language / cross-repository relationships in scope (`A1-W8-01`, W8.5)** — Contract v3:1152 conditions the
  bullet on "where in scope", and nothing places such a relationship in scope at Phase 2. When Phase 3/4 design
  Repo A and Repo B, whether either spans languages at an FFI boundary or spans repositories is a real scoping
  choice for the owner, and if it is placed in scope it becomes a new obligation with a repository-contract
  convention to go with it. See `owner-decisions-required.md`.
- **`V1-F5-01`** — the deferred MCP layer is not reported as a capability gap by doctor or readiness, contrary to
  D-0004. It matters when Phase 4 exercises the tool/MCP surface.
- **Qualification design note from AC-3.** Two `CANNOT_UNDERMINE` arguments I accepted record real coverage limits
  a Phase-4 designer should know: gamma's F2 (a fault class modelling a tool correct for one task class and wrong
  for another cannot be run until task-class scoping exists) and delta's M1 (no routing outcome resolves to T0, so
  a design that scores routing determinism or cost has nothing to measure at that tier).

## R2 — standard release certification

Untouched here and out of this gate by frozen §7: production signatures and key custody, the key ceremony,
SBOM/licences/provenance, private-remote publication, and the rotation/revocation drill. Every key used anywhere in
this verification is a throw-away drawn per run. `V1-S2-01` (the release manifest records adapter versions but no
capability or plugin versions) is an R2-adjacent gap recorded non-blocking here: what ships is still pinned by the
signed metadata's per-file digests.

## R3 — high-assurance qualification

Out of this gate in full.

## Adoption and operations

- **`V1-A3-01`** — personal or customer data the project has not classified is indexed and returned by retrieval.
  A3's own bullets are met; this is a default-posture question the contract does not answer, and it belongs to
  adoption guidance and operations rather than to this gate. See `owner-decisions-required.md`.
- **`V1-A5-02` and `V1-A5-03`** — recovery from an emergency control leaves no durable reasoned record, and
  `CANCEL_AGENTS` sets a flag and pauses but revokes no claim or handoff. Both are operations-facing; A5's
  governed-write refusals hold.
- **`V1-A4-01`** — the network-call budget is observed (`gov telemetry summary.over_budget`) but not enforced. The
  classes that can run away without a human are enforced and each stops at a Human Decision Gate.
- **`E-P2-01`** — three of the eight organisational questions P2 names are not answerable from the telemetry the OS
  keeps (retrieval effect on token use, skill repair rate, retrieval misses). Token accounting would come from the
  adapter surface.
- **`E-Q1-01` and `E-Q2-01`** — the lesson lifecycle is modelled in the record but not enforced on the path that
  uses it, and a lesson may record itself `AUTHORITATIVE` with no check contradicting it. The terminal control
  holds: nothing leaves the repository without the owner's signed answer, and a lesson's claim buys no authority in
  a compiled context packet.
- **`E-O5-01`'s operations half** — `TEST_POLICY.product_families` remains `overridable`, so a project can narrow
  what "the product tests" means. Recorded by P2-AR-0050 as an adoption/operations note and not counted here.
- **`V1-R1P-02` / `V1-AC09-01`** — `release/orchestration/phase-2/tools/product_identity.py` prints an annotated
  tag's tag-object id on its `commit:` line. Orchestration tooling, not product source; the digests are correct, so
  it is not a STOP — but every verifier is told to treat a pinned-identity mismatch as one, so it is worth fixing
  before it misleads someone.

## Open and explicitly out of scope

The D-0007 explicit transition record remains open and is not requested by the owner (frozen §7). I did not treat
it as a Phase-2 obligation.
