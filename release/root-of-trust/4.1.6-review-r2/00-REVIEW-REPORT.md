# Independent Root-of-Trust Architecture Review — RoT-1 revision 2 (Governance OS 4.1.6)

| | |
|---|---|
| **Verdict** | **ROOT_OF_TRUST_ARCHITECTURE_REJECTED** |
| Reviewer role | Fresh Independent Governance OS Root-of-Trust Architecture Reviewer. This session did not author revision 1, the review of revision 1, or revision 2. No conclusion of the architect or the prior reviewer was inherited; each was re-derived or re-tested. |
| Date | 2026-09-14 |
| Reviewed | `release/root-of-trust/4.1.6/` (00–22, `schemas/`, `examples/`, `evidence/`), `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` and `docs/DECISIONS.md`, as committed in `d37b05c` on `release/4.1.5-rc1` (not tagged). The working tree was clean for these paths. Per-file digests: `evidence/REVIEWED-CONTENT-DIGESTS.txt`. |
| Also read | the review of revision 1 (`release/root-of-trust/4.1.6-review/`, `1c6027c`); the 4.1.5 re-verification memory record and V-H3 finding; the 4.1.5 runtime (`runtime/src/{authority, kernel, kernel_trust, init, update, recovery, exceptions, policy, policy_precedence, records, adapters, tools, util}.rs`, `orchestration/gates.rs`, `security/secrets.rs`, `capabilities/host.rs`, `cit/mod.rs`, `migrations/{executor, classify}.rs`, `cli/src/main.rs`); the kernel under `framework/` and the released payloads 4.1.2–4.1.5 |
| Binaries executed | `gov 4.1.5` (`target/release/gov`; runtime unchanged since `da9c851`) and `gov 4.1.2` (built from `8ad06be`) |
| Rejected baseline | `release/4.1.5-rc1`, tag `v4.1.5-rc1`, commit `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| Not modified | No runtime, CLI, kernel, migration, fixture, test, released payload, verifier artefact, architecture-pack file, prior review, D-0007, D-0008 or ARCH-0002. Additions: this directory only. Consumer projects were created in session scratch space. |
| Approval | **D-0008 is not approved by this review.** It remains PROPOSED. The owner has not selected OP-1…OP-6 and should not do so on revision 2. |

## 1. Executive summary

Revision 2 is a substantial and mostly sound repair. It closes two of the four prior HIGH findings outright:
- **RV-H3:** byte binding inside `gov` is proven by construction in `03` §1.
- **RV-H4:** historical identities are compiled-only and never eligible, and every statement type is purpose-bound.

It also closes most of the MEDIUM findings. The following design elements should be kept:
- the anchor, the purposes, VerifiedBlobs, the install transaction, the KernelSnapshot and the installation state machine;
- GovernedFs as the internal writer rule;
- sticky revocations and admissibility;
- the account-database trust store;
- mode A without a clock.

Four HIGH findings block acceptance. Each is the same class that rejected 4.1.3, 4.1.4, 4.1.5 and revision 1: a
lower-trust input yielding a current, higher-trust fact.

| Finding | Mistaken equivalence | One-line evidence |
|---|---|---|
| **R2-H1** | *registered floor keys ⇒ constitutional policy* | All 145 TPS v1 floors hold on a kernel that makes an L1 role act at L4, gets an AWS credential indexed and retrievable, and lets an agent answer an R5 irreversible gate (executed, `evidence/P1`). 64 of 125 AS-1 leaves are unfloored, including the role→level map. |
| **R2-H2** | *compiled or repository knowledge ⇒ current state* | On a verifier without retained state, a repository writer chooses the effective TPS, revocations and floors. An older binary accepts a revoked older release as `verified`/`CURRENT_KNOWN(1)` with a lowered floor and no gate at use (`evidence/P4-B5`). The ingress gate is a record A2 can commit (`evidence/P2`: update applied from a forged gate file). |
| **R2-H3** | *release key ⇒ binary authenticity* | `artifact-final` rides the threshold-1 `release-final` purpose. `verify-artifact` needs no attestation, certification or gate, and cannot check the binary's compiled trust state (the schema has no field for it). One token forges the TCB. |
| **R2-H4** | *sentinel read afterwards ⇒ boundary* | Real 4.1.5 `update --rollback` and `init --force`, and 4.1.2 `update --rollback`, rewrite a RoT-1 project, delete a project restricted-classification, report `verified: true` and serve the restricted file. No RoT-1 remedy restores the classification. A fail-before-write layout blocks every tested command of both binaries (`evidence/P3`). |

Ten MEDIUM and three LOW findings refine these:
- gate records as authorisation (M1);
- trust-state minimums from the wrong purposes (M2);
- certification-key un-withdraw (M3);
- equivocation (M4);
- skip-version lowering (M5);
- separation constraints (M6);
- long-lived snapshots (M7);
- agent consumption (M8);
- trust-record and recovery-state consistency (M9);
- the acceptance plan cannot detect any of the above (M10).

## 2. Method

1. Read the full pack, the prior review, D-0008 and ARCH-0002. Checked every claim against the 4.1.5 code paths it
   replaces or relies on.
2. Executed probes against real binaries in scratch space (`evidence/`):
   - **P1** floor coverage and consumption;
   - **P2** gate-record forgery;
   - **P3** a 48-run pre-RoT matrix over three layouts and two binaries;
   - **P3b** attribution control.
3. Encoded the trust-state and eligibility rules as written (`17` S2–S9 and §6; `19` §5–§6 and §10) in a small reference
   model (**P4**). Six falsification scenarios were computed; each contradicts a stated claim.
4. Attempted every attack listed in the review brief (A–G) and authored 36 held-out attacks (`08`).
5. Judged each declared residual by explicit acceptance criteria (`09`). Documentation alone was not accepted.

## 3. Confirmed sound (keep)

| Area | Status |
|---|---|
| Compiled root chain, dual-threshold rotation, OP-6 lineage confirmation, fork refusal | sound |
| Nine purposes, compiled payloadType table, SV-1…SV-10, key-id recomputation | sound (D-1…D-8 all closed; `04` §1) |
| Historical 4.1.2–4.1.5 identities: compiled-only, never eligible | sound; RV-H4 closed |
| DSSE, Ed25519 strict verification, GOV-JCS-1, ASCII tree rules | sound |
| Read-once VerifiedBlobs, staging from buffers, read-back, atomic exchange, post-commit CI equality | sound |
| KernelSnapshot as the only in-process source of kernel content; secure no-follow primitives | sound; RV-H3 closed for `gov` (`03` §1) |
| Installation state machine (no unverified directory as policy root) | sound; RV-M2 closed |
| GovernedFs and the Protected Path Set as the internal writer rule | sound; RV-M1 closed for `gov`-internal writers (`05`) |
| Install-authority *required* level never from the target | sound (actor level: R2-H1) |
| Computed migration weakenings; unique migration chain; no lock operation | sound; RV-M8 closed |
| Sticky revocations, admissibility (a)(e), no environment-selected trust store, mode A with no clock | sound against A1, A4, A5 and A13 |
| No cache on any trust path; embedded snapshot in memory | sound |

## 4. Status of the prior HIGH findings

| Prior finding | Status after revision 2 | Why |
|---|---|---|
| RV-H1 authentic historical kernels as policy roots with weaker floors | **NOT CLOSED** (narrowed) | Historical identities are excluded and 145 keys are floored. Authentic eligible releases still confer weaker unfloored constitutional policy (R2-H1). On stateless verifiers, eligibility inputs are attacker-selected (R2-H2). |
| RV-H2 certification, revocation and root-rotation state withheld or replayed | **NOT CLOSED** (narrowed) | Closed against A1 for known facts. Open against A2 on stateless verifiers (R2-H2). New purpose leak (R2-M2), un-withdraw (R2-M3) and equivocation (R2-M4). |
| RV-H3 verified bytes ≠ enforced bytes | **CLOSED** for the `gov` process | Residual long-lived-process and agent-consumption gaps: R2-M7, R2-M8. |
| RV-H4 wrong key purpose attests kernel authenticity | **CLOSED** | New purpose defects elsewhere: R2-H3, R2-M2, R2-M3, R2-M6. |

## 5. Falsification results (brief sections A–G)

| Brief | Result | Detail |
|---|---|---|
| A. Security-floor monotonicity | **falsified for unfloored content** and for stateless verifiers; authenticity still confers eligibility at or above the known minimum sequence | `01` |
| B. Trust-state freshness | Implementable **without** network or clock as roots **for verifiers with retained state**. For stateless verifiers the binary's build date is the only root, and the repository writer selects the rest. Equivocation, purpose leakage and un-withdraw defects. | `02` |
| C. Verified-byte identity / TOCTOU | **proven** inside `gov` (`03` §1), with two unstated conditions (long-lived processes, agent consumption) and trust-record consistency gaps | `03` |
| D. Key-purpose separation | All eight required attempts closed. **New:** TCB via `release-final`; trust-state facts from non-trust-state purposes; certification-only un-withdraw; incomplete KS. | `04` |
| E. Protected write paths | Internal writers closed. Plugins, tool commands and pre-RoT binaries write authorisation records, overlay and PPS. Legacy update snapshots are a live pre-RoT input. | `05` |
| F. Pre-RoT binary boundary | **falsified**: old binaries falsely report trusted after their own remedies, mutate before refusing, overwrite kernel, lock and overlay, and run recovery or reinstall before refusal. A better boundary is **demonstrated feasible**. | `06` |
| G. RT-01…RT-72 | would detect none of the four HIGH findings; self-referential expectations (RT-50, RT-72); three untestable residual variants; builder-supplied [FS] instrumentation | `07`, `08` |

## 6. Residuals named by the architect

| Residual | Determination |
|---|---|
| 1. A machine never receiving newer metadata cannot know it exists | Unavoidable core accepted. **Bound mis-stated and not compatible with the claimed model**: gates don't bound A2, Git-delivered use is ungated, floors *are* affected, and the compiled-T0 bound has no age limit. → R2-H2 |
| 2. A same-user process alters files after a snapshot; the next process detects it | **Accepted for short-lived CLI processes only.** Not bounded for long-lived processes, agent consumption, authorisation records or the overlay. → R2-M7, R2-M8, R2-M1, R2-M9 |
| 3. Old pre-RoT binaries keep their flaws, including destruction before refusal | **Not bounded** (harm beyond availability, persists across RoT-1 remedies) and **not inherent** (layout V3). → R2-H4 |

## 7. Findings

| ID | Severity | Title | Correction |
|---|---|---|---|
| R2-H1 | HIGH | The floor covers 145 keys; the rest of the constitution comes from the installed authentic kernel | CD2-1 |
| R2-H2 | HIGH | Stateless-verifier currency is chosen by the repository writer; stated bounds do not hold | CD2-2 |
| R2-H3 | HIGH | TCB authenticated by one threshold-1 `release-final` signature | CD2-3 |
| R2-H4 | HIGH | Pre-RoT binaries rewrite RoT-1 projects and delete project strengthening; boundary not bounded | CD2-4 |
| R2-M1 | MEDIUM | Gate, decision and exception records authorise trust decisions but are A2/A3-writable | CD2-5 |
| R2-M2 | MEDIUM | Trust-state minimums from non-trust-state purposes; no-override freeze | CD2-6 |
| R2-M3 | MEDIUM | Certification key alone lifts WITHDRAWN/REJECTED | CD2-7 |
| R2-M4 | MEDIUM | Trust-state equivocation undefined | CD2-8 |
| R2-M5 | MEDIUM | Lowering keyed on declared `lowers[]`; mode order undefined | CD2-9 |
| R2-M6 | MEDIUM | Separation constraints incomplete | CD2-10 |
| R2-M7 | MEDIUM | Long-lived snapshot never re-checked | CD2-11 |
| R2-M8 | MEDIUM | Agent-facing kernel content consumed from disk | CD2-12 |
| R2-M9 | MEDIUM | Trust directory exchange drops statements; `.tx/` in Git; `overlay.prev` unguarded | CD2-13 |
| R2-M10 | MEDIUM | Acceptance plan cannot detect the findings | CD2-14 |
| R2-L1 | LOW | `CURRENT_KNOWN` / OP-5 wording hides unproven freshness | CD2-2 |
| R2-L2 | LOW | Hard links accepted until post-commit check | CD2-11 |
| R2-L3 | LOW | F1 evidence inconsistent with `08` §2 and incomplete; `22` relied on it | CD2-4, CD2-14 |

Full statements, evidence and failure scenarios: `10-BLOCKING-FINDINGS.md`. Architectural correction only:
`11-CORRECTION-DELTA.md`.

## 8. Owner options

OP-1…OP-6 must not be answered on revision 2. Revision 3 must:
- add **OP-7**, currency for stateless verifiers (security-material);
- extend **OP-2** to a `release-artifact` purpose;
- restate **OP-4**: "no" also exposes binaries unless CD2-3 separates them;
- note that **OP-3** mode A is not a bound against a repository writer until CD2-5 moves trust-gate answers out of the
  repository.

## 9. Output files

| # | File | Content |
|---|---|---|
| 00 | `00-REVIEW-REPORT.md` | this report |
| 01 | `01-A-FLOOR-MONOTONICITY.md` | security-floor monotonicity; floor coverage; eligibility proof obligation |
| 02 | `02-B-TRUST-STATE-FRESHNESS.md` | freshness attacks; implementability without network or clock roots |
| 03 | `03-C-VERIFIED-BYTE-IDENTITY.md` | byte-identity proof sketch and TOCTOU attacks |
| 04 | `04-D-KEY-PURPOSE-SEPARATION.md` | purpose attacks; single-key blast radius |
| 05 | `05-E-PROTECTED-WRITE-PATHS.md` | complete writer inventory against protected targets |
| 06 | `06-F-PRE-ROT-BINARY-BOUNDARY.md` | executed pre-RoT matrix and alternative layouts |
| 07 | `07-G-ACCEPTANCE-PLAN-QUALITY.md` | RT-01…RT-72 quality, independence, self-reference |
| 08 | `08-HELDOUT-ATTACK-REGISTER.md` | RV2-A01…RV2-A36 |
| 09 | `09-RESIDUAL-DETERMINATION.md` | acceptance criteria and determinations for every declared residual |
| 10 | `10-BLOCKING-FINDINGS.md` | R2-H1…R2-L3 in full |
| 11 | `11-CORRECTION-DELTA.md` | CD2-0…CD2-14, D-0008 rule changes, re-review entry criteria |
| — | `evidence/` | P1–P4 scripts and outputs, reviewed-content digests, README |

## 10. Verdict

`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`
