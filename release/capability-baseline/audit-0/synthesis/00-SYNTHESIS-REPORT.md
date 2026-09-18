# P2-AR-0007: iteration-0 capability baseline synthesis and verdict

## Verdict: `GOVERNANCE_CAPABILITY_BASELINE_REJECTED`

| Field | Value |
|---|---|
| Run | P2-AR-0007, fresh independent `capability-baseline-synthesis` (model `claude-opus-5[1m]`, Opus 5, 1M context) |
| Handoff | P2-HO-0007 (with P2-HO-0000 common protocol) |
| Candidate | `cap2-candidate-0` = `57177a37ea296ece16b185874831462b6a76db18` (annotated tag object `9ee8dff…`) |
| `product_code_digest` | `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547`, equal to `srr1-r1-accepted` (`c7d3fef`) |
| `governed_state_digest` | `3dabf06a25e694f30182fd52549747826edcec29e9574f5a9c2c79705223ad91` (candidate and worktree HEAD) |
| Worktree HEAD / branch | `11d051eb7ef7431acd8edd9178bb46011064a0a4` / `phase2/cap-audit-0-synthesis` (candidate plus orchestration and audit evidence only; no product path changed) |
| Binary | `target/release/gov` 4.1.5, sha256 `3271ce0e4e095561911e0d03d8641aa92fbeda39ef3c8a2ecb2a9f21cacbe81d` (same as every family's build) |
| Frozen gate contract | SHA-256 `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` (matches `ORCHESTRATOR_STATE.yaml`) |
| Contract v3 | SHA-256 `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3`; the canonical import is byte-identical |

The candidate is rejected. Ten of the sixteen acceptance criteria fail on independent, reproduced evidence:

- Six capabilities are ABSENT: J2, V1, V2, V3, V4 and W11 (AC-2).
- 84 capabilities are PARTIAL, and 69 of those have gaps that would undermine advanced qualification (AC-3).
- The post-verification hardening in A2 and F4 is not fully incorporated (AC-4).
- There is no G0–G6 health scheduler (AC-5).
- No Qualification Oracle format exists (AC-6).
- The provisional-retrieval path is not governed (AC-7).
- Gate W fails all three of its rejection conditions (AC-8).
- No capability has a declared evidence owner, and green evidence stays green after relevant changes (AC-10).
- The compiled contract has lost the owner source's semantics and cannot detect that it has (AC-13).
- All seven cross-capability interactions fail at least one end-to-end exercise; S3/S4/S5 ↔ A2 holds only at ingress on a provisioned machine (AC-16).

AC-1, AC-9, AC-11, AC-12, AC-14 and AC-15 hold.

| AC | Result | One-line basis (section) |
|---|---|---|
| AC-1 | **HOLDS** | All 101 owner-source capabilities and all 713 checkbox bullets have a status and an evidence location (§2.1) |
| AC-2 | **FAILS** | J2, V1, V2, V3, V4, W11 ABSENT; no N/A_WITH_REASON claimed (§2.2) |
| AC-3 | **FAILS** | 69 of 84 PARTIAL capabilities have gaps that could undermine qualification (§3) |
| AC-4 | **FAILS** | A2 and F4 not incorporated. R1 is still valid for this byte-identical candidate, but only for what R1 examined (§2.4) |
| AC-5 | **FAILS** | No scheduler; tiers G1–G6 incomplete or absent (§2.5) |
| AC-6 | **FAILS** | No machine-checkable V1–V4 format exists, so nothing can be accepted (§2.6) |
| AC-7 | **FAILS** | Profile components are not identified or bound, and profile change is ungoverned; pipeline defects cap retrieval quality (§2.7) |
| AC-8 | **FAILS** | Matrix verified (226/226 cited observations reproduced); all three rejection conditions triggered (§2.8) |
| AC-9 | **HOLDS** | Commit, tag and both digests are frozen and re-derived (§2.9) |
| AC-10 | **FAILS** | 0 of 101 capabilities have a product-declared owner; 15 have no running owner at all; invalidation fails for 10+ input classes (§2.10) |
| AC-11 | **HOLDS** | Coverage matrix is complete for all 101 capabilities, including not-challengeable routes (§2.11) |
| AC-12 | **HOLDS** | All evidence relied on is fresh for the exact digest and independent; builder tests are used only as regression evidence (§2.12) |
| AC-13 | **FAILS** | Compiled form carries 0 of 344 substantive bullets; Gate U missing from every derived view; O5 and V1–V4 misclassified; `verify` is self-referential (§2.13) |
| AC-14 | **HOLDS** | Not required: `product_code_digest` equals `srr1-r1-accepted` (§2.14) |
| AC-15 | **HOLDS** | `cargo test --lib` 42/42 and `cargo test --test certification` 79/79, zero failures (§2.15) |
| AC-16 | **FAILS** | All seven listed interactions fail at least one cross-family case; S3/S4/S5 ↔ A2 holds only at ingress on a provisioned machine (§2.16) |

**Capability status (final, after synthesis corrections):** PRESENT_AND_SUBSTANTIAL 11, PARTIAL 84, ABSENT 6, UNCLEAR 0,
N/A_WITH_REASON 0. The families recorded 13 / 82 / 6 / 0 / 0.

**Findings:** 180 family findings dispositioned: 165 CONFIRMED, 15 CORRECTED (10 blocking-status corrections, 5 owner-decision reclassifications with blocking confirmed), 0 REFUTED. The synthesis adds 10 findings
(8 blocking, 2 INFO). That gives **134 blocking findings in 52 blocker classes** (`blocker-classes.yaml`), which is the
iteration-0 inventory against which convergence is measured (frozen contract §8).

**Owner decisions:** two genuine ones, OD-P2-01 (agent-role identity binding) and OD-P2-02 (scope of the unprovisioned
posture). All four flagged items (human-approval channel, plugin self-declaration, A2 post-install anchor, unprovisioned
posture) are resolved by accepted sources for their determined parts and become ordinary repair requirements
(`owner-decisions-required.md`).

## 1. Method

1. **Pinned inputs** were verified first (table above; `evidence/AC01-09-13-14-universe-identity-binding.out [AC-9]`).
   No STOP.
2. **Build and regression.** `~/.cargo/bin/cargo build --release` in the worktree produced the families' binary hash. The
   AC-15 commands were run exactly as named, with HOME isolated (`evidence/AC15-regression.*`).
3. **Families' probes re-run** without editing any family directory: every family's probe runner was executed inside a
   disposable local clone of `11d051e`, built there to the same binary hash (`evidence/RERUN-family-probes.sh`,
   `evidence/rerun/*.log`). The regenerated outputs were compared with the committed ones at marker level and after
   normalisation (`evidence/COMPARE-family-outputs.py/.out`):
   - 115 outputs were regenerated.
   - 1 680 PASS/FAIL markers were compared (alpha-r 868, beta-r 212, delta-r 276, zeta-r 324). Every probe outcome is
     identical. The two alpha-r marker differences are a `release/` file count, which grew because audit evidence was
     committed later, and a truncated line.
   - gamma-r and epsilon-r emit no markers. Their outputs were reviewed line by line. Only timings, race winners
     (E4: every trial still grants 3 of 3 concurrent claims), tie ordering and the attempt at which a race was observed
     differ.
   - Not re-run: gamma-r's R1 held-out re-run (AC-14 does not require it) and the builder-test captures of alpha-r, beta-r,
     gamma-r and epsilon-r, which are superseded by my own AC-15 run. delta-r's runner re-ran both suites in the clone:
     42/42 and 79/79 again.
4. **Universe and derived views** were established from the owner source text itself
   (`evidence/AC01-09-13-14-universe-identity-binding.py`).
5. **Cross-family evidence of my own:** AC-16 chains X1 to X3, leads X4 and X5, and an AC-6 search, all independent
   of the families' code except X3, which imports alpha-r's independent ed25519 minter read-only. The AC-8 matrix was
   verified cell by cell (`evidence/AC08-verify-artifact-flow-matrix.*`).
6. **Adjudication.** Every family finding was dispositioned, and the matrices, classes and dispositions were generated
   from one table (`evidence/tools/build_synthesis.py`, whose output lives in this directory). The first-pass audits
   P2-AR-0001…0006 were neither read nor relied on.

## 2. Acceptance criteria

### 2.1 AC-1 — HOLDS
The owner source contains 101 capabilities: A1–A5, B1–B3, C1–C10, D1–D6, E1–E4, F1–F5, G1–G2, H1–H4, I1–I4, J1–J2, K1–K4,
L1–L4, M1–M4, N1–N4, O1–O5, P1–P2, Q1–Q4, R1–R3, S1–S6, T1–T3, U, V1–V4 and W1–W12. There are 713 checkbox bullets between lines
130 and 1196. The union of the six families covers exactly these 101 capabilities, with no duplicates and no extras.
Every owner-source bullet line has a bullet record in its family's audit. Every capability has a status and an evidence
location (`capability-status-matrix.yaml`; `[UNIV]` and `[AC-1]` lines).

### 2.2 AC-2 — FAILS
Six capabilities are ABSENT:
- **J2** (experiment lifecycle): 6 of 7 bullets absent, and the production-merge flag is never enforced.
- **V1–V4** (Qualification Oracle): no format of any kind (§2.6).
- **W11** (artifact-flow metrics): none of the nine metrics is tracked.

No capability is recorded N/A_WITH_REASON. Two bullet-level N/A records were checked and accepted:
- D4:338 (generative/query-planning model, "replaceable where designed"; framework §14.2 "optional").
- W12:1192 (G6 *injection* is Phase-4 execution; the G6 tier's existence stays a Phase-2 obligation under O5:799, which is
  ABSENT and blocking).

### 2.3 Status corrections made by the synthesis
Each correction rests on reproduced evidence from another family or on my own probes.

| Cap | Family → final | Why |
|---|---|---|
| A1 | PARTIAL (bullets 134, 135 P&S → PARTIAL; impact CANNOT → COULD) | Project overlays bypass POLICY_PRECEDENCE (delta-r A0-M1-02 routing floors; gamma-r A0-H3-01 readiness switch). This is exactly the "attempted authority weakening" the A1 challenge (line 140) injects. |
| B1 | P&S → PARTIAL (bullet 188) | S0-B1B3-01: claims, emergency-control state and the OS plugin registry are stored where the product's own contract says `derived`/`generated`. |
| B3 | P&S → PARTIAL (bullet 202) | Same finding. Deleting what the product declares derived deletes claims (C1 current truth) and lifts FREEZE_WRITES (beta-r D6, reproduced). |
| I4 | PARTIAL (bullet 587 P&S → PARTIAL; impact CANNOT → COULD) | S0-I4-01: a BLOCKED task is in the runnable set and is offered by `gov continue` (delta-r lead, reproduced). |
| A5, B2, F1 | impact CANNOT → COULD | A5: the FREEZE_WRITES leak is the blocking G0 guard gap. B2: citations are scored by the Repo B challenge and by V2. F1: same mechanism as blocking epsilon-r A0-O2-01. |

The remaining eleven P&S capabilities were checked against every other family's evidence: S1, C1, C6, G2, H1, H2, I1,
K1, L4, N4, Q3.
- **H1** "live evidence": the task → report trace exists, over an edge whose direction W2 already flags.
- **K1:** the duplicate CIT-P candidates are the per-artefact cap recorded in C9.
- **N4:** the structured result survives. The status-schema collision is a W5 receipt defect, S0-W5-01.

All eleven stand.

### 2.4 AC-4 — FAILS
- **A2 is not incorporated.** These defects are blocking:
  - A consistent post-install rewrite is not detected (BC-P2-35). AC16-X3 [X3d] shows the consequence: with
    AUTHORITY_POLICY rewritten consistently, an L1 worker records a human answer while `kernel verify` still reports
    verified.
  - An unauthenticated installation is presented as current, and doctor and audit report HEALTHY (BC-P2-36; X3a).
  - Trust decisions and identity records are taken from unauthenticated release fields (BC-P2-37).
- **Refinement.** alpha-r's phrase "secrets … indexable" does not hold for path-classified secrets: `.env` stayed
  excluded by a second layer (X3c).
- **F4 is not incorporated.** Blocking defects:
  - Gate not bound to the plugin (BC-P2-11).
  - Forgeable registry (BC-P2-09).
  - Self-declared elevation (BC-P2-39).
  - Security review satisfied by any record (BC-P2-41).
  - **New:** a *registered*, gate-approved, network-elevated plugin in the documented `python3 -m` form has no
    implementation pin, and a post-approval code swap runs with doctor silent (S0-F4-01, BC-P2-40). This also corrects
    gamma-r A0-F4-04 to blocking.
- **R1 acceptance still valid for what it examined.** The candidate's product digest equals `srr1-r1-accepted`. On a
  provisioned machine every ingress still refuses unsigned, tampered and below-floor releases: alpha-r A2-02 re-run is
  identical, and X3b refuses `SRR_PAYLOAD_DIGEST_MISMATCH`.
- **What R1 item 11 does not show (S0-R1-01).** zeta-r handed me the R1 item "the original product controls, Gate W and
  G0–G6 implementation mappings remain valid". AR-0027/29/31/33 all dispositioned it on *unmodified builder suites*.
  None examined whether Gate W or a G0–G6 scheduler exists. So R1-11 is a non-regression statement, not capability
  evidence, and the Phase-2 statuses of W1–W12 and O5 rest on Phase-2 evidence alone.

### 2.5 AC-5 — FAILS
Each required behaviour was exercised (epsilon-r probes re-run; AC16-X1 adds the G4 case):

| Behaviour | Result |
|---|---|
| Impacted-test selection | absent |
| Parallel execution | absent (one thread) |
| Isolation | absent (a deep audit rewrites the live `state.db`) |
| Cache reuse | whole-suite only |
| Cache invalidation | key incomplete (BC-P2-03) |
| Stale evidence | DONE work never re-staled |
| RED/YELLOW/GREEN | per surface only |
| Hard-block vs warning | nothing blocks |
| Provenance | incomplete |
| Remediation/task generation | none |
| Tiers | G0 partial (FREEZE leaks, L0 `init --force`); G1 CIT path only; G2/G3 incomplete; G4 = the 3-check CIT verification (X1: no wider check recorded after a spec CIT); G5 subsets; G6 absent |
| Serial full suite for a trivial mutation | yes — the only remedy for a one-line change is the whole suite, run serially and twice |

Classes: BC-P2-06, -07, -08, -24.

### 2.6 AC-6 — FAILS
`evidence/AC06-oracle-format-search.out` settles this independently of epsilon-r:
- No tracked file defines any V1–V4 field identifier.
- No schema exists, and no qualify/oracle/score subcommand.
- `GATE-P2-ORACLE-FORMAT` is NOT_SATISFIED. The only "oracle" files are Phase-1 root-of-trust review evidence.

With no format there is nothing a fresh reviewer could accept. No hidden fault was generated. Class: BC-P2-51.

### 2.7 AC-7 — FAILS (frozen contract §9.1 reading)
The benchmark → compare → select → pin mechanism exists and discriminates candidates (beta-r D5, re-run identical). But
§9.1's own terms are unmet:
- "Separately identifiable … runtime components": the embedding model artefact and runtime are unidentified and unbound
  (A0-D4-01).
- The pins do not bind what executes (A0-D5-01).
- "Reindex/migration route on profile change": profile change is not bound to evidence, regression or the radius gate
  (A0-D5-02). A re-pin also withholds every deterministic input until a full rebuild (A0-W10-01).
- Pipeline defects cap the quality any profile could reach: list-valued content never indexed, module-level code never
  indexed, filters applied after truncation (BC-P2-25, -26).

Selecting the profile remains Phase 3. Classes: BC-P2-30, -25, -26, -19.

### 2.8 AC-8 — FAILS
- **Matrix verified.** zeta-r's Artifact Flow Coverage Matrix (14 rows × 10 evidence columns + a dedicated challenge per
  row) was checked cell by cell: all 226 cited observations match both the committed and the regenerated outputs, with
  no inconsistency. It is carried forward in `artifact-flow-coverage-matrix.yaml` with that verification recorded. Cell
  counts: 24 EVIDENCED, 55 PARTIAL, 61 GAP.
- **All three rejection conditions hold**, and AC16-X1 reproduces them across families:
  - Mandatory inputs are rediscovered by retrieval (experiments, research, task-level interfaces; datasets never
    delivered; outage withholds everything).
  - Stale versions satisfy work: a DONE task on a superseded criterion stays DONE and its report ACTIVE; an index rebuild
    licenses closing on the pre-change packet.
  - Completion is untraceable: no receipt, fabricated trace accepted.
- **Synthesis additions:** S0-W1-01 (adoption catalogue ids positional) and S0-W5-01 (worker return unusable as the
  receipt).

Classes: BC-P2-04, -05, -07, -16, -17, -19 to -23.

### 2.9 AC-9 — HOLDS
- Commit `57177a37…` and annotated tag `cap2-candidate-0` (object `9ee8dff…` → commit `57177a37…`).
- `product_code_digest` `bd4d65d9…0547` and `governed_state_digest` `3dabf06a…ad91` re-derived with
  `product_identity.py` for HEAD, the tag, the commit and `srr1-r1-accepted`.
- Between the candidate and HEAD only `release/capability-baseline/audit-0/**` and `release/orchestration/phase-2/**`
  changed; no product-code path changed.
- One tooling quirk (INFO, S0-AC09-01): given a tag *name*, the tool prints the tag object as `commit`. The digests are
  unaffected.

### 2.10 AC-10 — FAILS
- **No declared owners.** The product's evidence map declares no owner for any capability: 100 rows, all
  `NOT_YET_MAPPED` with `automated_checks: []`, and Gate U has no row.
- **No running owner at all** for 15 capabilities, even counting G-tier-*equivalent* host checks: J1, J2, K3, K4, M1–M4,
  N3, O1, V1–V4, W11. No capability has a scheduled tier owner, because no scheduler exists.
- **Invalidation.** It was demonstrated working for policy, kernel, schema, migration, repository contract, sensitivity,
  plugin descriptor, retrieval profile, held-out set and decisions. It was demonstrated **failing** (green stays green)
  for requirements, architecture, interfaces, source files, index manifest, tool/plugin registry,
  research/experiment/task/checkpoint/handoff records, adoption evidence, trust state and the runtime implementation.
  AC16-X1 adds a clean case: after a fresh HEALTHY audit, a direct requirement edit leaves D021 "current".

See `suite-to-contract-matrix.yaml`. Classes: BC-P2-02, -03, -06, -07.

### 2.11 AC-11 — HOLDS
`qualification-coverage-matrix.yaml` maps each of the 101 capabilities to:
- a Repo A challenge, a Repo B challenge and a hidden-oracle fault class;
- chaos/scale/soak and retrieval challenges, or a stated "not relevant: reason";
- a not-challengeable route where synthetic repositories cannot exercise the capability, for example A2 key custody →
  R2 ceremony, T1/T2 session holder → harness attestation, V1–V4 → the AC-6 fresh format review.

The families proposed the challenges; I checked them for completeness, and none is missing. This is a coverage *plan*.
The qualification it plans cannot run until the rejection is repaired.

### 2.12 AC-12 — HOLDS
Every piece of evidence this verdict relies on was produced on the exact `product_code_digest`, with the same binary hash:
- the families' probes, which I re-ran;
- my own probes;
- my AC-15 run.

Every piece was produced by roles that authored no product code. Builder tests are used only as regression evidence
(AC-15). The first-pass audits are not relied on.

Several families tagged AC-12 on *product-side* defects: A0-O3-01, A0-O4-01, A0-W6-05, A0-J1-03. My reading is that
AC-12 governs the evidence the gate relies on, and those defects block through AC-10 and AC-3 instead. This is recorded,
not double counted.

One disclosed family protocol deviation (beta-r read its own background build output once) touched no evidence.

### 2.13 AC-13 — FAILS
- **Binding chain intact.** The canonical import is byte-identical to the owner source. The lock binds both digests and
  the compiled value's canonical hash. `gov contract verify` reports `CONTRACT_SOURCE_BOUND`.
- **Compiled form not faithful:**
  - It carries only id, title, class, source reference, family and status.
  - 0 of 344 substantive bullets and none of the Contract v3:53-73 fields.
  - Gate U is missing from the compiled form, the evidence map and the generated view; the compiled-form schema's id
    pattern cannot even express `U`.
  - O5 and V1–V4 are compiled ORIGINAL, and O5's title keeps the source marker.
- **Why `verify` misses it (S0-AC13-01):** it compares the compiled file only with a fresh run of the same headings-only
  compiler, and never reads the evidence map or the generated view.

Contract v3:47 makes any semantic difference a hard failure. Class: BC-P2-01.

### 2.14 AC-14 — HOLDS (not required)
`product_code_digest` (HEAD, candidate) equals `product_code_digest` (`srr1-r1-accepted` = `c7d3fef`) =
`bd4d65d9…0547` (`[AC-14]` line). Any repair will change it, and then AC-14 applies to the next candidate.

### 2.15 AC-15 — HOLDS
`cargo test --lib`: 42 passed, 0 failed. `cargo test --test certification`: 79 passed, 0 failed
(`evidence/AC15-regression.out`, 2026-09-18T21:40Z, HOME isolated, XDG/GOV unset).

### 2.16 AC-16 — FAILS
Each interaction was exercised end-to-end across family boundaries. Every chain crosses at least three families.

| Interaction | Exercise | Result |
|---|---|---|
| W12 (Gate W ↔ G0–G6) | X1: after a spec CIT, which tier re-checks? zeta-r W12 re-run | **fails**: no wider check recorded (G4); G2/G3 Gate-W duties absent |
| O4/W6 | X1: DONE task on a changed criterion; fresh green, then direct requirement edit | **fails**: DONE task not re-staled; green record stays current (`X1-O4-green-stale-after-direct-spec-change` FAIL) |
| K2 ↔ D1 ↔ W6 | X1: CIT-E commits (index fresh, D1 PASS), then propagation | **fails**: open task retested (PASS), but the DONE task, its report and the packet are untouched; no rework; after a direct edit the rebuild licenses closing on the pre-change packet |
| N ↔ W9 | X1: checkpoint and handoff after the change | **fails**: checkpoint not marked stale; watchdog does not fire; handoff accepted with the pre-change packet hash |
| L3 ↔ E1 | X2: L1 worker forgery inside its own task → close → CIT approve → execute → audit | **fails**: forgery invisible at close; approval `human_approved: true`; CIT COMMITTED; audit HEALTHY. Default invocation, `--role human` and `GOV_ROLE=human` each record a human answer |
| S3/S4/S5 ↔ A2 | X3: unprovisioned vs provisioned ingress, carried into sensitivity, retrieval, health and authority | **holds on a provisioned machine at ingress** (X3b) and alpha-r's per-ingress table re-runs identically. **Fails** on the default posture (X3a, masquerade) and after install (X3c/X3d: consistent rewrite undetected; lowered authority floor lets L1 record human answers) |
| U ↔ O5 | X1: health after invalid completed work; epsilon-r U/O5 re-run | **fails**: fresh audit HEALTHY and doctor HEALTHY with a DONE task built on a superseded criterion; no SLO observed by any scheduler |

## 3. AC-3 — FAILS, and the criterion applied

The families applied two different readings of Contract v3 item 3 ("cannot undermine the qualification scenario"):
- alpha-r often used "the gap would be measured as a miss", which yields CANNOT_UNDERMINE.
- beta-r, gamma-r (stated explicitly), delta-r, epsilon-r and zeta-r used "the gap lies on a path qualification
  exercises".

**Criterion applied uniformly.** I adopt the second reading, because the item's purpose is to avoid running
sophisticated qualification on a baseline whose outcome is predetermined. A PARTIAL COULD_UNDERMINE qualification when
any of these holds:
- (i) the gap lies on a path that a Contract v3 advanced-qualification challenge line, a V1–V4 oracle element or a V4
  metric directly exercises, so that element's outcome is predetermined by a known defect;
- (ii) the gap makes evidence qualification relies on untrustworthy (forgeable authority or approval, self-attested
  independence, green results for properties never tested);
- (iii) the gap prevents the G0–G6 or Gate W observation that AC-5 and AC-8 require.

**Result.** 69 PARTIAL capabilities COULD_UNDERMINE. 15 are argued CANNOT_UNDERMINE with an accepted argument: A4, S2,
S3, S6, C10, E2, E3, F2, F5, K4, M4, N1, P1, P2, Q2. The per-capability arguments are in `capability-status-matrix.yaml`.

**Corrections to non-blocking findings.** Under this criterion, ten family findings were re-marked blocking:
- A0-A5-01, A0-S4-03: same mechanism as the blocking G0 findings.
- A0-B2-02: Repo B / V2.
- A0-S4-02: a Repo B with a secret-bearing chat store stalls adoption.
- A0-S5-02: provisioned rollback.
- A0-E1-04: human-approval part.
- A0-E1-06: AC-13/AC-10.
- A0-F1-01: consistency with O2.
- A0-F4-04: registered module-form plugins.
- A0-H3-01: A1 challenge.

Every correction is argued in `findings.yaml`. Five more findings (A0-A2-01, A0-A2-02, A0-L3-01, A0-L3-05, A0-F4-03)
are CORRECTED only in their `owner_decision_required` classification; their blocking status is confirmed
(`owner-decisions-required.md` §A).

## 4. Cross-family leads (P2-HO-0007) — disposition

| Lead | Result | Evidence |
|---|---|---|
| delta-r → I4: BLOCKED task handed out as runnable | **Confirmed**; new blocking finding S0-I4-01; I4 corrected | X2 `X2-I4-*` |
| delta-r → E3/E1: any role returns any handoff | Confirmed; already gamma-r A0-E3-01 (non-blocking accepted) | X2 `X2-E3-*` |
| delta-r → C7/D2: nested worker return not indexed | Confirmed; covered by beta-r A0-C3-02 | delta-r N4.b1.6, beta-r C7 (re-runs) |
| delta-r → C9: impact-simulation candidates duplicated | Observed (X1: RPT-0001 twice); consistent with A0-C9-01's per-artefact cap; no new finding | X1 `X1-C9-*` |
| beta-r → F4: `python3 -m` plugins carry no implementation pin | **Confirmed and escalated**: registered, gate-approved elevated plugin runs swapped code; S0-F4-01 (HIGH, AC-4) | `LEAD-X4-*` |
| beta-r → S4/B2: adoption archives the OS's own IDE adapter; ledger/catalogue id mismatch | **Confirmed**: on re-run the adapter is classified LEGACY and moved (S0-S4-01). The mismatch is caused by positional catalogue ids that change on re-run (S0-W1-01) | `LEAD-X5-*` |
| beta-r → N4/E3: valid worker return rejected at task close (status collision) | **Confirmed**: `SCHEMA_INVALID` on `/status: "success"` (S0-W5-01) | X2 `X2-N4xW5-*` |
| beta-r → W6/O5 | Confirmed through the owning families and X1 | X1 |
| zeta-r → how R1 assessed "Gate W and G0–G6 mappings remain valid" | Non-regression only (builder suites unmodified); not capability evidence (S0-R1-01, INFO) | R1 reports item 11 |

## 5. Blocker-class inventory (summary)

52 classes, 134 blocking findings. Full definitions and finding lists are in `blocker-classes.yaml`. Requirements,
acceptance evidence, dependencies and workstreams are in `repair-delta.md`.

| Area | Classes |
|---|---|
| Contract binding / evidence map | BC-P2-01 (9 findings), BC-P2-02 (7) |
| Currency, scheduler, health | BC-P2-03 (6), -06 (6), -07 (6), -24 (2), -42 (2), -43 (1), -44 (2) |
| Authority, human gates, precedence | BC-P2-08 (6), -09 (3), -10 (4), -11 (2), -12 (1), -18 (3), -45 (2), -49 (1) |
| Change control / Gate W | BC-P2-04 (6), -05 (3), -13 (2), -14 (2), -15 (2), -16 (3), -17 (3), -19 (4), -20 (4), -21 (3), -22 (1), -23 (1) |
| Knowledge fabric / retrieval | BC-P2-25 (3), -26 (4), -27 (2), -28 (1), -29 (3), -30 (3), -31 (2), -32 (1) |
| Root of trust (A2) | BC-P2-35 (1), -36 (1), -37 (2), -38 (1) |
| Plugins / tools (F4/F3) | BC-P2-39 (1), -40 (2), -41 (2) |
| Adoption / legacy / independence | BC-P2-33 (4), -34 (4), -52 (1) |
| Records, research, experiments | BC-P2-46 (2), -47 (1), -48 (1) |
| Learning / export | BC-P2-50 (1) |
| Qualification oracle | BC-P2-51 (1) |

**Proposed repair workstreams**, each owning distinct files (`repair-delta.md` §3):

| WS | Scope | Classes |
|---|---|---|
| WS-1 | Contract binding and evidence map | 01, 02 |
| WS-2 | Health scheduler, currency and health verdict | 03, 06, 07, 22, 23, 42, 43, 44 |
| WS-3 | Identity, authority, Human Decision Gates, precedence | 08, 09, 10, 12, 18, 45, 49 |
| WS-4 | Change control, propagation, Gate W delivery and continuity | 04, 05, 11, 13, 17, 19, 20, 21 |
| WS-5 | Task lifecycle, DAG, claims and work generation | 14, 15, 16, 24 |
| WS-6 | Knowledge fabric and retrieval | 25–32 |
| WS-7 | Plugin and tool trust | 39, 40, 41 |
| WS-8 | Root of trust and lifecycle ingress | 35–38 |
| WS-9 | Adoption and legacy | 33, 34, 52 |
| WS-10 | Research, experiment and test-data records | 46, 47, 48 |
| WS-11 | Learning and export | 50 |
| WS-12 | Qualification Oracle format | 51 |

`cli/src/main.rs`, `tasks.rs` and `records.rs` are the named integration hot spots.

## 6. Owner decisions (summary; full text in `owner-decisions-required.md`)

- **Determined by sources; ordinary repair requirements, not owner decisions:**
  - The human-approval and presentation channel (BC-P2-10). Contract v3:679; D-0007 rule 2; ARCH-0003 §8;
    OWNER-DIRECTIVE-0004; the authority class is defined by OWNER-DECISION-0006 req. 2.
  - The default role (BC-P2-08; framework §23).
  - Plugin self-declaration (BC-P2-39; Contract v3 F4 and ARCH-0003 §9 outrank the agent-approved D-0005).
  - The A2 post-install anchor (BC-P2-35; Contract v3:146; D-0007 rule 1; ARCH-0003 §7/§8; no D-0007 amendment).
  - Non-masquerade of unauthenticated installs (BC-P2-36; A2:150).
- **OD-P2-01, agent-role identity binding (L0–L4).** D-0007 consequence 5 (adapter boundary) and Contract v3 E1:365 /
  framework §23 pull in different directions on *who* enforces role assignment. Minimum decision: keep the adapter
  boundary for agent roles (recommended), issue OS role credentials, or bind L3+ only.
- **OD-P2-02, unprovisioned posture scope.** A2:143 literal vs A2:150 vs the R1 IMPLEMENTATION-CHOICE is a
  security/availability posture that OWNER-DECISION-0005 §1 reserves to the owner. Minimum decision: refuse
  external-source ingress until provisioned (recommended), keep a marked non-production mode, or embed production root
  keys.

## 7. What I could not establish, and limits

- **Human presence in the loop.** Whether a gate actually reaches a human cannot be shown in a synthetic repository. The
  repair acceptance for BC-P2-10 therefore requires a verifier-authored attack by an agent process running with the
  operator's own OS privileges.
- **Real neural embedders and provider spend** were not exercised (offline). Scale beyond 3 000 documents and Windows
  path semantics were not tested.
- **R1 held-out suites** were not re-run (AC-14 does not require it; gamma-r re-ran R1-4's 31 tests unedited and reported
  31/31).
- **Reproducibility of committed outputs.** My probe outputs contain absolute scratch paths. Re-run with the commands in
  each probe's docstring.

## 8. Evidence index (`evidence/`)

| File | Content |
|---|---|
| `AC15-regression.sh/.out` | AC-15 regression, exact commands |
| `RERUN-family-probes.sh`, `rerun/*.log`, `rerun/epsilon-r.RUN-ALL.out` | Families' probes re-run in a disposable clone of `11d051e` |
| `COMPARE-family-outputs.py/.out` | Committed vs regenerated outputs (markers and normalised text) |
| `AC01-09-13-14-universe-identity-binding.py/.out` | Universe (AC-1), identity (AC-9, AC-14), contract binding and derived-view fidelity (AC-13), evidence-map owners (AC-10) |
| `AC06-oracle-format-search.sh/.out` | Independent AC-6 search |
| `AC08-verify-artifact-flow-matrix.py/.out` | AC-8 matrix verification |
| `AC16-X1-upstream-change-chain.py/.out` | K2↔D1↔W6, O4/W6, N↔W9, W12, U↔O5, C9 lead |
| `AC16-X2-authority-gate-chain.py/.out` | L3↔E1 chain; fabrication; framework §23; E1-01; E3, N4/W5, I4 leads; B1/B3 |
| `AC16-X3-ingress-root-of-trust-chain.py/.out` | S3/S5↔A2 on unprovisioned and provisioned machines; consequences in A3/C4/U; authority-floor rewrite (A2↔E1↔L3) |
| `LEAD-X4-registered-module-plugin-unpinned.py/.out` | F4 lead (S0-F4-01) |
| `LEAD-X5-adoption-rerun-archives-os-adapter.py/.out` | S4/B2 lead (S0-S4-01, S0-W1-01) |
| `lib/synth.py` | Probe harness (isolated HOME/XDG per project; GOV_* stripped; embedded kernel) |
| `tools/build_synthesis.py/.out` | Generator for the matrices, dispositions and classes; the adjudication table |
