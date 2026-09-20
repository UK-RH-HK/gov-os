# P2-AR-0047 — iteration-1 verification of capability family `beta`

| Field | Value |
|---|---|
| Run | **P2-AR-0047** |
| Role | fresh, independent capability family verifier (family `beta`), verification iteration 1 |
| Family | C1–C10, D1–D6, R1–R3 — Development Knowledge Fabric; indexing, retrieval and context; legacy, archive and historical state |
| Candidate | `cap2-candidate-1` |
| Verdict | `FAMILY_VERIFICATION_COMPLETE` |
| Worktree / branch | `scratchpad/wt/p2-verify1-beta` / `phase2/verify-1-beta` |

I authored none of the implementation, none of its tests, none of the iteration-0 audits, none of the repairs and no
Phase-1 role. I modified no product source. I do not issue the Phase-2 verdict.

---

## 1. Pinned inputs (all verified; no STOP)

```
git rev-parse HEAD                     8588813ec1ef9c832879e258ca5acfb573ae996f
git rev-list -n1 cap2-candidate-1      0bad524d836f179964ffbac31972856ea6434682
git cat-file -t cap2-candidate-1       tag   (annotated; git rev-parse resolves the TAG OBJECT f75eb7db…,
                                              which is why product_identity.py prints that sha for the tag)
product_identity.py HEAD               product_code_digest  e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220
                                       governed_state_digest 3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0
product_identity.py cap2-candidate-1   the same two digests
Contract v3 SHA-256                    4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3   ✔ matches
Frozen gate contract SHA-256           d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e   ✔ matches
```

Both digests at `HEAD` equal the tag's, as the dispatch said they would. Evidence: `evidence/identity/pinned-inputs.out`.

Sources applied: Contract v3 (the audit universe — every bullet below was read from it, not from a derived view);
the frozen gate contract; the three governing documents; `spec/decisions/`, `spec/architecture/`, `spec/interfaces/`;
OD-P2-01, OD-P2-02, OD-P2-03; P2-ADJ-0001, P2-ADJ-0002, P2-ADJ-0003. I record no finding that any of them is wrongly
implemented.

## 2. Method

A **full re-audit**: all 123 checklist bullets of the nineteen capabilities, established afresh on this candidate.
The bullet set was parsed from the owner source (C 73 bullets, D 36, R 14 = 123) and every bullet has its own
demonstration.

The evidence is a held-out suite I wrote, under `heldout/`, driven by `heldout/RUN-ALL`. It builds its own disposable
projects, never touches the product tree, and copies no builder test or builder probe. Its parts:

* `corpus.sh` — a governed corpus with records of every C1 kind and a five-language source tree (Python, Rust,
  TypeScript, Java, Go) carrying route registrations, ORM models, inheritance/implementation relations and needles
  planted **only** inside list-valued and nested record fields, inside method bodies, and outside every structural
  code unit. Every needle is unique in the corpus, so a hit can only have come from where it was planted.
* `provision.py` — verifier test material only. OWNER-DECISION-P2-0002 makes "provision, then install" the documented
  first-run path, and several obligations in my scope (a task close, and the whole governed retrieval-profile change)
  are only reachable on a provisioned machine with a green governance record. `gov` holds no signing code (SRR-R0-L4),
  so this script produces the administrator-domain material outside the product: a throw-away Signed Release Root with
  `release`, `snapshot`, `timestamp`, `recovery`, `human-gate` and `t2-binding` roles, a release of the candidate's own
  payload measured by the product itself (`gov release build`) and signed, the owner's T2 binding authority and its
  key, and the owner-signed `human-gate-answer` documents. Every key is drawn at run time and written only under the
  run's scratch directory.
* twelve probe scripts, one PASS/FAIL line per check. The canonical run is
  `evidence/heldout/RUN-ALL.out` — **186 checks passed, 9 failed** — and each probe's full output is beside it. The
  nine failures are exactly the gaps this report records: four for C8 (V1-BETA-01), three for C10 (V1-BETA-02), one
  for the held-out set's discriminating power (V1-BETA-03) and one for archive reachability (V1-BETA-05).
  `evidence/heldout/RUN-ALL.first-pass.out` is an earlier full run, kept because it differs in one line: its
  `ATK-xmachine-no-secrets` check failed on a probe-side heuristic that matched the literal `-----BEGIN` inside
  SECURITY_POLICY.yaml, where that string is a *detection pattern* and not key material. The check was narrowed to
  the actual key bytes and a real PEM block and passes in the canonical run; the earlier log is kept so that
  correction is visible rather than silently overwritten.

`rm` is denied to me. Nothing was deleted anywhere: where a probe had to "delete" a store (D6), it **moved it aside**
to a graveyard outside every project, so the process under test sees the same absence. (The first D6 run moved the
store aside *inside* the repository and the extra directory changed what the indexer walked — that was a probe
artefact, corrected, and is why `aside()` now writes outside the tree.)

Preconditions (P2-ADJ-0003): where a probe needed a green baseline it built one that is legitimately green — a
provisioned machine carrying an authentic, current installation of the candidate's own payload, on which `gov doctor`
returns HEALTHY. Unprovisioned probes ran on a machine whose only doctor failure is D032, the bootstrap-authenticity
disclosure OD-P2-02 requires; that is a posture the contract itself creates, not a product defect.

## 3. Per-capability result

| Cap | Title | Bullets | Status | Note |
|---|---|---:|---|---|
| C1 | Deterministic structured memory | 17/17 | `PRESENT_AND_SUBSTANTIAL` | each of the seventeen kinds created through the OS operation that owns it and read back |
| C2 | Relationship/graph memory | 3/3 | `PRESENT_AND_SUBSTANTIAL` | all twenty relation types stored and read back; orphan/dangling/stale/reversed/ill-typed all detected |
| C3 | Semantic memory | 7/7 | `PRESENT_AND_SUBSTANTIAL` | admission runs before any route truncates: 20 superseded better-matching carriers neither appear nor exhaust the pool |
| C4 | Lexical memory | 6/6 | `PRESENT_AND_SUBSTANTIAL` | list-valued and nested record content, module-level code, error strings and config keys all reachable |
| C5 | Code-structural memory | 8/8 | `PRESENT_AND_SUBSTANTIAL` | spans verified line-by-line in five languages; routes, DB models, inheritance and `implements` extracted |
| C6 | Temporal memory | 5/5 | `PRESENT_AND_SUBSTANTIAL` | what/when from version control, why from the transaction record, causal decision by upstream lineage |
| C7 | Episodic execution memory | 6/6 | `PRESENT_AND_SUBSTANTIAL` | a real close on a provisioned machine; the OS-written report carries session, role, task, tools, files read/changed, tests, discoveries |
| C8 | Failure memory | 3/7 | **`PARTIAL`** | bugs, failed approaches, wrong assumptions and migration failures have a record shape and **no writer** (V1-BETA-01) |
| C9 | Working memory / context packet | 7/7 | `PRESENT_AND_SUBSTANTIAL` | deterministic block carries full normative content + hashes; hash moves when one word of a requirement moves |
| C10 | Capability memory | 4/7 | **`PARTIAL`** | no A2A agent inventory, no resolved dependencies, no observed tool versions (V1-BETA-02) |
| D1 | Incremental indexing / freshness | 6/6 | `PRESENT_AND_SUBSTANTIAL` | reclassification reaches unchanged files; CIT-E refreshes under the post-mutation path map; stale index blocks close and its remedy clears it |
| D2 | Retrieval router | 6/6 | `PRESENT_AND_SUBSTANTIAL` | all six routes; graph answers rank first on a dependency question |
| D3 | Hierarchical retrieval | 4/4 | `PRESENT_AND_SUBSTANTIAL` | methods are chunk units; child-first with bounded parent expansion |
| D4 | Component separation | 10/10 | `PRESENT_AND_SUBSTANTIAL` | each of the ten separately identified; an out-of-band swap is reported `UNGOVERNED`/high |
| D5 | Evidence-driven retrieval model selection | 6/6 | `PRESENT_AND_SUBSTANTIAL` | benchmark → gate → owner-signed answer → pin + full re-index + recorded regression, with automatic rollback |
| D6 | Rebuild guarantee | 4/4 | `PRESENT_AND_SUBSTANTIAL` | all derived state deleted and rebuilt to the same manifest hash, at a second path; claim and FREEZE_WRITES survive |
| R1 | Legacy governance retirement | 7/7 | `PRESENT_AND_SUBSTANTIAL` | full brownfield adoption; a live reference stopped the retirement and rolled the batch back |
| R2 | Chat-memory retirement | 3/4 | **`PARTIAL`** | raw stores never default truth; extraction with a dependency proof; rebuild and an independent-held-out regression — but retirement is not a CIT-E transaction (V1-BETA-09) |
| R3 | Archive policy | 3/3 | `PRESENT_AND_SUBSTANTIAL` | archive out of default retrieval; dead code deleted rather than archived; reference implementations retained explicitly |

Sixteen `PRESENT_AND_SUBSTANTIAL`, three `PARTIAL`, no `ABSENT`, no `UNCLEAR`, no `N/A_WITH_REASON`.
At bullet level: 115 of the 123 bullets `PRESENT_AND_SUBSTANTIAL`, 6 `ABSENT` (the four C8 classes with no
writer, and C10's A2A-agent and package/dependency bullets), 2 `PARTIAL` (C10's observed tool versions and
R2's CIT-E/index-refresh/regression bullet).
Per-bullet detail, with implementation, automated and independent evidence for each, is in `capability-audit.yaml`.

### AC-3 arguments for the three `PARTIAL` capabilities

* **C8 — `COULD_UNDERMINE`.** This is the one call in this report where I judge against the product rather than
  merely record a gap, so the argument is given in full. Four of the seven failure classes cannot be created at all.
  The work generator builds governed follow-up work from open failure-memory records and, for an unrecognised kind,
  defaults to `bug` (`runtime/src/orchestration/generation.rs:1223`) — the machinery is written to act on bug
  records that can never exist. Advanced qualification injects faults and measures whether the OS notices and
  governs them; a scenario that injects a product bug or a failed approach and expects the OS to record it and
  generate linked repair work cannot be satisfied by this candidate. The contrary reading is available and the
  synthesis verifier should weigh it: Gate C carries no "advanced qualification challenge" line of its own, the
  Qualification Oracle (Gate V) measures detection rather than the memory of it, and the three classes the product
  *does* record (retrieval miss, tool failure, regression) are the ones a retrieval-and-memory qualification would
  exercise. I record `COULD_UNDERMINE` because the gap is not safely outside the scenario, and therefore AC-3.
* **R2 — `CANNOT_UNDERMINE`.** The one unmet half of the fourth bullet is that retirement is not executed as a
  change-impact transaction. What it *is* executed as — gated migration batches whose independently authored tests
  roll a batch back, a per-store dependency proof, a full index rebuild and a held-out regression that refuses
  builder-only queries — carries every property CIT-E would give the qualification scenario: simulated impact, a human
  gate, an atomic outcome and recorded evidence. A qualification repository that retires a legacy store is therefore
  governed and measurable either way.
* **C10 — `CANNOT_UNDERMINE`.** The missing facts are an A2A agent inventory, a resolved package/dependency set and
  observed tool versions. Qualification runs in synthetic repositories whose tool and agent set is fixed by the
  harness and declared in the overlay, and every capability qualification work needs is resolved from the declared
  registry, which is present and exercised. The gap makes environment drift invisible in operation; it cannot make a
  qualification scenario pass or fail wrongly.

## 4. AC-7 determination (frozen gate contract §9.1) — **HOLDS**

Item 7, as §9.1 interprets it, asks whether the candidate provides an **executable, evidenced path** to establish a
provisional retrieval profile, without selecting one. I exercised that path end to end on a provisioned machine and
then left the corpus as I found it. No profile is selected as a Phase-2 conclusion.

| §9.1 element | Established by |
|---|---|
| Pluggable, separately identifiable embedder / reranker / runtime components (D4) | all ten D4 components separately identified: the embedder's adapter, model (id, revision, parameters, sha256) and runtime (id, kind, digest) are distinct blocks in `components` of the index manifest and of the live profile; the reranker carries its own identity even when its provider is `none`; the lexical engine and tokenizer, the vector and graph stores, the code-intelligence adapter per artefact, the router's strategy and routes per packet, the context compiler's runtime/index version per packet, and the generative model as an overlay-declared, tier-resolved component |
| Benchmark / compare with golden or held-out queries and the required metrics (D5) | `gov memory benchmark --candidate current --candidate builtin:64 --candidate builtin:8` measured three candidates over 32 held-out queries and reported, per candidate, recall@k, MRR, precision@k, stale-hit and superseded-hit rates, symbol recall, average query latency, index cost and vector count, each row carrying the candidate's own component identities |
| Select and pin | `gov memory select` refuses without evidence (`PROFILE_EVIDENCE_REQUIRED`); with evidence it holds at `WAITING_HUMAN`, radius R5, applying nothing; a CLI- or environment-declared `human` role does not satisfy it; with the owner's signed answer through the authenticated channel it applies, recording a decision and pinning component identities |
| Governed reindex / regression on profile change | the same operation performs a full re-index and a measured held-out regression; a candidate measurably worse than the baseline is rolled back automatically (`PROFILE_REGRESSION_FAILED`, naming the restored profile), the previous profile is restored and a durable `regression` failure record is written |
| Cross-machine | the resulting decision is sealed and is honoured as `GOVERNED` on a second machine of the same owner bound to the same T2 binding authority; a hand-edited copy of it is no longer honoured |

**One qualification on that determination, which Phase 3 must carry.** The held-out set `gov init` generates leaves
its two `semantic_paraphrase` queries pending, so the measured set contains no query that depends on the embedder: on
the generated set, `current` (512-d), `builtin:64` and `builtin:8` all measure recall@k 0.9333 / MRR 0.9333, and the
gate's "the candidate is not worse on every held-out measure" is true and vacuous. Nothing refuses or flags a
selection made on such evidence. The mechanism itself is sound — after I authored three real paraphrase queries the
same benchmark separated the candidates (semantic recall 0.667 / 0.667 / 0.333) and a worse candidate was rolled
back — so this is a Phase-3 precondition, recorded as **V1-BETA-03**, not a Phase-2 blocker: §9.1 asks for the path,
and the path exists and runs. Phase 3 must not earn `PROVISIONAL_RETRIEVAL_PROFILE_READY` on evidence that contains
no measured semantic query. A second defect in the same generated set (**V1-BETA-08**) means its two graph queries
can never pass, so every project's recall baseline is permanently 0.93.

## 5. Findings

Nine findings. **One blocks.**

| id | Cap | Sev | Blocking | Label | Title |
|---|---|---|---|---|---|
| V1-BETA-01 | C8 | MEDIUM | **yes (AC-3)** | `RESIDUAL` of BC-P2-32 | four of the seven failure classes have a record shape and no writer |
| V1-BETA-02 | C10 | MEDIUM | no | `RESIDUAL` (of A0-C10-01; no class) | no A2A agent inventory, no resolved dependencies, no observed tool versions |
| V1-BETA-03 | D5, C3 | MEDIUM | no | `RESIDUAL` of BC-P2-30 | a governed selection may rest on evidence that cannot discriminate the component selected |
| V1-BETA-04 | D1, C7 | MEDIUM | no | `RESIDUAL` of BC-P2-03 | the suite and the close check write into their own currency key, so the first close is always refused as stale |
| V1-BETA-05 | R3 | LOW | no | `RESIDUAL` (of A0-R3-01; no class) | archived material is unreachable on any explicit request (`include_archive` is never set) |
| V1-BETA-06 | C4, D2 | LOW | no | `RESIDUAL` (of A0-C4-02; no class) | identifier-shaped literals are matched as a disjunction of their subtokens |
| V1-BETA-07 | D1, C2 | LOW | no | `RESIDUAL` of BC-P2-29 | an edge owned by an unchanged file survives its target's deletion until a full rebuild (now reported dangling) |
| V1-BETA-08 | D5, D2 | MEDIUM | no | **`MATERIALLY_NEW`** | the generated held-out set's two graph queries expect the seed itself and can never pass |
| V1-BETA-09 | R2 | LOW | no | `RESIDUAL` (of A0-R2-01; no class) | retirement of a chat store is not executed as a CIT-E transaction |

Labels were chosen on the §8 rule and not to avoid escalation. Eight are `RESIDUAL` because they lie in the same
capability and the same defect mechanism as an inventoried class (or, for four of them, as a specific iteration-0
finding the synthesis left outside every class because it was non-blocking), and each is an incomplete fix rather
than a new mechanism. One is `MATERIALLY_NEW`: a generated held-out query whose stated expectation contradicts the
route it declares is in no inventoried class, the nearest class (BC-P2-26) concerns the retrieval pipeline while the
routing here is correct, and the starter generator's graph category was added by a repair round, which §8 treats as
materially new. Full statements, normative sources, reproductions and repair directions are in `findings.yaml`.

## 6. Iteration-0 disposition

All 33 iteration-0 findings in this scope are disposed of in `prior-findings-disposition.yaml`: **25 CLOSED,
7 RESIDUAL, 1 NOT_APPLICABLE**, each on evidence I produced. I did not read any iteration-0 evidence directory.

**Closed (25)** — among them every blocking finding of BC-P2-25 (index content coverage), BC-P2-26 (retrieval
ordering, routing and de-duplication), BC-P2-27 (code-structural extraction), BC-P2-28 (graph integrity), BC-P2-29's
path-map and CIT-E halves, BC-P2-30 (component identity and change governance), BC-P2-31 (the relocated claims,
emergency-control and plugin-registry stores), BC-P2-33 (legacy extraction and dependency proof), and A0-C1-01
(the derived contract views now carry all 123 beta bullets verbatim, with evidence owners).

**Residual (7)** — A0-C4-02 → V1-BETA-06; A0-C6-01 (ungoverned commit history not ingested; recorded INFO in
iteration 0, not a contract bullet, not re-raised); A0-C8-01 → V1-BETA-01; A0-C10-01 → V1-BETA-02; A0-D1-01 →
V1-BETA-07; A0-R2-01 → V1-BETA-09; A0-R3-01 → V1-BETA-05.

**Not applicable (1)** — S0-F4-01, whose mechanism is the plugin registration's implementation binding (Gate F4,
gamma's scope this iteration). Its D5 half was established here: a pinned reranker is re-verified against what the
index recorded, a plugin that does not resolve fails closed and records a tool failure, and a benchmark candidate
takes the revision the declared plugin executes.

## 7. The common protocol's attacks

| Attack | Result |
|---|---|
| **Trust classes** (D-0007; A2/F4/L3) | a hand-written record asserting its own OS-written lifecycle facts is reported `T2 UNSEALED` / `EXPERIMENT_LIFECYCLE_NOT_OS_WRITTEN` and its claims are not honoured; a project override widening the secret namespace is refused by policy precedence and recorded, leaving the effective policy unchanged; declaring the acting role `human` on the command line or in the environment does not apply a retrieval-profile change |
| **Cross-machine continuity** (P2-ADJ-0002) | a retrieval-profile decision sealed on machine A is honoured as `GOVERNED` on a second provisioned machine of the same owner bound to the same T2 binding authority; on an unbound machine it is `GOVERNED_UNVERIFIED` with `binding: FOREIGN` and says so rather than pretending; a hand-edited copy of the sealed decision is no longer honoured; no signing or binding secret is inside the repository |
| **Availability rule** (Contract v3 L4/O5) | a stale index does not refuse ordinary reads; the block's own remedy (`rebuild-memory`) is never refused by the block; independent work (claiming another task) stays available; the stale-close refusal names its remedy, and after the remedy the same close succeeds. One wart: the remedy must be run twice (V1-BETA-04) |
| **Freshness** (Contract v3:95–111) | changing the policy, source, spec, governance-tests or index-manifest input class each marks prior green evidence stale, shown one class at a time from a current green record |

## 8. Regression evidence (O3 — builder tests are regression evidence only)

* `cargo test --lib` — **276 passed, 0 failed** (`evidence/regression/cargo-test-lib.out`).
* `cargo test --test certification` — **207 passed, 0 failed** in 3252 s
  (`evidence/regression/cargo-test-certification.out`).

Both were run by me in this worktree on this candidate, and both reproduce the counts the round-4 integration
recorded. They are regression evidence (O3); the independent evidence for every capability is the held-out suite.

## 9. What I could not establish

1. **The reranker plugin boundary, behaviourally.** That an excluded candidate never crosses the plugin boundary was
   established from the admission code path and from the fail-closed refusals, not by registering a `rerank` plugin
   that records what it receives. Registering one needs an owner-signed execution gate for that plugin identity and
   is Gate F4, which gamma verifies this iteration.
2. **Model/artefact binding for a real external embedder.** The built-in embedder's model and runtime are the running
   binary, so their identity is derived. The declared-artefact binding path (`model: {artefacts: […]}`) was read, not
   exercised, for the same reason as (1).
3. **Scale and soak.** Every probe ran on corpora of 170–280 artefacts. Retrieval latency, index cost and the
   incremental path at 10^4–10^5 artefacts are Phase-4 chaos/scale challenges and are proposed as such per capability
   in `capability-audit.yaml`.
4. **The G0–G6 scheduler's own properties** (impacted-test selection, parallelism, cache reuse and invalidation,
   RED/YELLOW/GREEN aggregation). I exercised the tiers only where a beta capability is observed by them; AC-5 is the
   epsilon family's.

## 10. Later-lifecycle notes (never Phase-2 blockers)

* **Phase 3.** Before `PROVISIONAL_RETRIEVAL_PROFILE_READY`, the pending `semantic_paraphrase` queries must be
  authored and the two generated graph queries corrected (V1-BETA-03, V1-BETA-08), or the selection will rest on
  evidence that measures nothing about the embedder and on a baseline that is wrong for an unrelated reason.
* **Phase 4.** Every capability carries a Repo A challenge, a Repo B challenge, a hidden-oracle fault class and, where
  relevant, chaos/scale/soak and retrieval challenges in `capability-audit.yaml`. The fault class worth naming here is
  C8's: a failure of a class with no writer must be recorded, not lost.
* **Operations.** C10's gap (V1-BETA-02) is an operational blind spot rather than a qualification one: environment
  drift — a different installed tool version, a changed dependency set — is invisible to capability memory.
* **Archive reachability.** V1-BETA-05 makes retained reference implementations reachable only through Git; that is a
  usability limit on R3's third bullet, not a breach of its first.

## 11. Contents of this directory

```
00-VERIFICATION-REPORT.md          this report
capability-audit.yaml              19 capabilities, 123 bullets, per-bullet status and evidence
findings.yaml                      8 findings, each labelled RESIDUAL / MATERIALLY_NEW with its reason
prior-findings-disposition.yaml    33 iteration-0 findings disposed of
heldout/                           the held-out suite (RUN-ALL, lib.sh, corpus.sh, provision.py, 12 probes)
evidence/identity/                 pinned-input verification
evidence/heldout/                  the captured output of every probe, and of RUN-ALL
evidence/regression/               cargo test --lib and --test certification
evidence/currency/, ac7/, lexical/, prior/   the focused artefacts the findings cite
```
