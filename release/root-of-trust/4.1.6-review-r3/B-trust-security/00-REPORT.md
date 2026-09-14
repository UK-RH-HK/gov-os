# Independent trust and security review (B) — RoT-1 revision 3 (Governance OS 4.1.6)

| | |
|---|---|
| **Role verdict** | **BLOCKING_FINDINGS_PRESENT** (reviewer B; not the architecture verdict, which belongs to the synthesis reviewer) |
| Run | AR-0002, role `rot-reviewer-trust-security`, handoff `HO-0002` |
| Revision under review | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` at `ca77a431418bd6b349f465aa2521ca43bccfd5a6`. Per-file digests: `evidence/REVIEWED-CONTENT-DIGESTS.txt`. The pack is unchanged between `ca77a43` and the review base `83aa822`. |
| Branch and base | `phase1/rot1-r3-review-b` from `83aa822` |
| Date | 2026-09-14 |
| D-0008 | Not approved by this review. It remains PROPOSED. |

## Independence

- **What this session authored before:** no RoT-1 revision, no prior review, and not reviewer C's work.
- **Orchestration files read:** only `HO-0002`, `HO-0001` and `AGENT_RUNS/README.md`.
- **Not read:** the architect's AGENT_RUNS report, other branches, other worktrees, other scratch directories.
- **Treated as claims, not findings:** the architect's response matrix and evidence. Both were re-executed or re-derived.

## Scope and method

1. **Read.**
   - Revision 3 files `00`, `03`, `05`, `06`, `07`, `17`–`27`: in full.
   - Files `01`, `02`, `04`, `09`, `12`, `13`, `14`: the sections relevant to trust.
   - `constitutional-surface/` and the trust schemas.
   - D-0008, ARCH-0002, and the review r2 report, findings, correction delta, held-out register, residuals and P1/P2/P4.
   - The 4.1.5 runtime paths that consume the changed content: `policy_precedence.rs`, `policy.rs`, `authority.rs`, `orchestration/gates.rs`, `verification/mod.rs`, `tools.rs`, `migrations/framework.rs`, `memory/embedder.rs`, `upstream.rs`, `project.rs`, `paths.rs`, `capabilities/{host,governance}.rs`.
2. **Re-executed.**
   - Review r2 P1, P2 and P4, unmodified apart from paths.
   - The architect's coverage checker, including its self-test.
   - The architect's P1r3 and P4r3.
3. **Built an independent reference model** of the revision-3 trust-state, anchoring, OP-7, lift, `verify-artifact` and trust-gate rules, from the text. With it: re-ran B1–B6 and computed the HO-0001 §3.2 machine list × OP-7 × adversary matrix (HO-0002 §3.4).
4. **Authored 18 held-out attacks** (`02`). Three were executed on the real 4.1.5 binary, four with the pack's checker, and twelve were computed; the rest are design or code readings. Also ran independent constitutional-surface injections.
5. **Judged every declared residual** against explicit criteria (`03`).

Legacy-binary containment (P3r3, G1) and the transaction internals are reviewer C's scope and were not re-executed.

## Summary

Revision 3 closes a great deal. The following hold under test:
- **Default-deny surface.** Unknown keys, files and directories are denied (checker re-run; independent injections I01–I07).
- **Review r2 tamper.** It is ineligible, and its harms flip (architect P1r3 re-run, byte-identical).
- **Release-local references.** Candidate references are release-local (B1).
- **Unresolvable TSS.** It is ignored below the effective sequence and `INCOMPLETE` above it (B4).
- **Equivocation.** Same-sequence forks are refused (B3).
- **Lowering.** Computed lowering with a cumulative history works (B6).
- **Separation.** The pairwise purpose whitelist and KS-8…KS-10 hold.
- **Repository gate records.** They are requests, not authorisation (P2 flips in the model).
- **Unanchored machines.** Under OP-7 (a)–(c) they are read-only.
- **Binaries.** `release-artifact` carries threshold ≥ 2.

Three HIGH findings remain. Each is an instance of the recurring class: a lower-trust input yielding a current, higher-trust fact.

| Finding | Mistaken equivalence | One-line evidence |
|---|---|---|
| **RV3-B-H1** | *`immutable` ⇒ strongest precedence* | A kernel whose only change is three precedence modes set to `immutable` passes the checker (exit 0). On 4.1.5 it drops the project's L5 authority raise, its `confidential` never-index class (customer file indexed and retrievable), and its R0 agent-gate limit. The overlay is unchanged, so no revision-3 detector fires (executed, A01). |
| **RV3-B-H2** | *an anchor number ⇒ current state* | Revoked R7 becomes an anchored C2 policy root and C3 target in several cases: a CI runner with a stale pin under the proposed OP-7 (a), which the pack says makes B5 "impossible everywhere"; a current pin or first-install anchor bypassed by one trust-state key presenting a higher unchained TSS; a stateless runner under OP-7 (c) given a thief-minted witness (computed, A02, A06, A12, 132-row matrix). |
| **RV3-B-H3** | *reproducible build ⇒ verified source* | `verify-artifact` accepts a binary built from a `release_commit` that only `release-final` chose. The final reuses a verified candidate's identical kernel tree, the rebuilder faithfully reproduces the malicious commit, and no rule checks source legitimacy (computed and design, A08). |

**MEDIUM findings.** Five, each carried as a bounded requirement in `04`:
- M1: lift with two keys;
- M2: same-account writers of pins and decision pins, executed via `gov verify product`;
- M3: `issued_at` high-water poisoning;
- M4: playbook against admissibility;
- M5: migration weakenings outside the computed set.

**LOW and INFO.** Five LOW findings and one INFO. All statements are in `01`.

## Prior-finding status (review r2)

| Finding | Status | Evidence |
|---|---|---|
| **R2-H1** constitutional floor coverage | **NARROWED** | Closed for floor, pinned and member leaves. Default deny is total: checker exits reproduced (`framework/` 0; 4.1.5 payload 0; 4.1.2 2; 4.1.3 and 4.1.4 3); self-test 26/26; injections I01–I07 fail closed; the architect's P1r3 re-run is identical, with the r2 harms flipped. Open: the precedence order discards project strengthening (H1, executed A01); `project_tunable` leaves are read by security decision points (L2, A16). |
| **R2-H2** stateless-verifier currency | **NARROWED** | Unanchored machines refuse C2/C3 under (a)–(c) (model B5 and matrix, no-pin rows); `CURRENT_KNOWN` is withdrawn. Open: stale pins under (a); anchors satisfied by sequence number; witness minting under (c) (H2). |
| **R2-H3** TCB via threshold-1 `release-final` | **NARROWED** | Purpose, threshold, build attestation, TSS reference and TBM resolution hold (architect A27–A29 re-run; model A08 checks A2–A9). Open: the built source is chosen by `release-final` and not bound to verified source (H3). |
| **R2-M1** repository records authorise trust decisions | **NARROWED** | Repository records are requests (the r2 P2 re-run still applies the forged record on unchanged 4.1.5; under the revision-3 rules the model refuses it). Open: same-account decision pins and pins (M2; A03 executed, A04). |
| **R2-M2** minimums from the wrong purposes; trust-state blast radius | **NARROWED** | Release-local references hold (B1); unresolvable TSS is ignored or `INCOMPLETE` (B4). Open: trust-state theft is not a freeze only (H2 A12, A06); any purpose raises the clock high-water (M3). |
| **R2-M3** certification key alone lifts WITHDRAWN | **NARROWED** | One key no longer lifts (B2). Two keys suffice by reusing the pre-withdrawal attestation (M1, A05; the architect's P4r3 B2 uses exactly that). |
| **R2-M4** equivocation undefined | **CLOSED** | Same-sequence fork gives `EQUIVOCATION` (B3); fork across a gap gives `REGRESSION` (architect E1 re-run); anchored orphans are defined. The dependence of anchored-fork handling on the anchored TSS being held is filed under H2. |
| **R2-M5** skip-version lowering; mode order | **NARROWED** | The cumulative computed lowering holds (B6). The order is now defined but unsound for the project layer (H1), and non-surface TPS fields are outside the computed set (L5). |
| **R2-M6** separation constraints | **CLOSED** | Compiled pairwise whitelist, KS-8…KS-10 (architect K1–K3 re-run; whitelist read). The "minimum distinct keys" table is wrong for lifts (M1) and for code authority (H3), but those are not separation defects. |
| **R2-M10** acceptance plan cannot detect the findings | **NARROWED** | RV2-A01…A36 are mapped with codes and property assertions. The plan would not detect H1–H3 or M1–M5: RT-75, RT-80, RT-91, RT-92, RT-97, RT-98 and RT-99 lack these cases (`02`, nearest RT per attack). |
| **R2-L1** `CURRENT_KNOWN` and OP-5 wording | **NARROWED** | `CURRENT_KNOWN` is withdrawn and the freshness axis added. `current` is still permitted for any `ANCHORED`, including stale or bypassed anchors (H2). |

## Probe reproduction

| Probe | Against | Result |
|---|---|---|
| Review r2 **P1** (`evidence/r2rerun-P1-*`) | 4.1.5 binary (implementation unchanged) | Reproduced: 145 floors hold on the tamper. L1 `resume` succeeds (genuine `AUTHORITY_DENIED`); AWS credential indexed and retrievable; agent answers the R5 gate. |
| P1 against revision 3 | architect P1r3 re-run (`evidence/arch-rerun-P1r3-*`) | Tamper ineligible; effective harm keys equal genuine; harms (a)–(c) flip; raised floors (d), (e) enforced. Output identical to the committed JSON. New counter-example: A01 passes E7 with harm. |
| Review r2 **P2** (`evidence/r2rerun-P2-*`) | 4.1.5 binary | Reproduced: control `applied: false`; forged `HDG-0001` gives `applied: true` (4.1.4 → 4.1.5). |
| P2 against revision 3 | independent model | Repository record: `TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED` (flips). New path: a same-account decision pin authorises `framework_update` (A04). |
| Review r2 **P4** (`evidence/r2rerun-P4-*`) | revision 2 rules | Reproduced: B1–B6 all `agrees: false`. |
| P4 against revision 3 | independent model (`evidence/RV3-B-M-*`) | B1, B2, B3, B4 and B6 claims hold. The B5 claim holds only without a pin, or with a current pin whose TSS is held. It fails with a stale pin (A02) and with a higher unchained TSS (A12). |
| Architect **P4r3** | re-run | 34/34, byte-identical to the committed output. Its `freshness()` compares anchor sequence numbers only; its B2 lift reuses the pre-withdrawal attestation. |
| Architect **coverage checker** | re-run | Exits reproduced; self-test 26/26 as expected. |

## Held-out attacks

- **Authored:** 18 (RV3-B-A01…A18).
- **By evidence class:** executed on 4.1.5, 3; executed with the pack's checker, 4; computed, 12; design or code only, 3.
- **Pack claims:** every attack contradicts a stated claim.
- **Blocking:** A01 (H1); A02, A06, A12, A13 (H2); A08 (H3).
- **Surface injections:** I01–I09 recorded separately.

## Owner options

This review answers no owner option. It notes three facts for the synthesis reviewer:
- the stated consequences of OP-7 (a) and (c) are materially incorrect (H2);
- the OP-2 and TB-3 blast radius for binaries is overstated (H3);
- the OP-2 `release-final` sentence is inexact (L2).

## Unresolved and not done

- **P3r3 and G1** (legacy-binary containment) were not re-executed by B; they are reviewer C's scope.
- **Specification-only mechanisms** were judged by design reading only: VU-11, VU-12, the adapter rendering record and foreign-journal handling.
- **No RoT-1 binary exists.** Revision-3 behaviour is established by the pack's checker, the architect's scripts and this review's model. The 4.1.5 executions demonstrate consumption semantics that revision 3 retains.
- **Assumed OP-7 parameters:** `max_anchor_age_days` 180 and `witness_max_validity_days` 7.
- **Severity calibration.** The synthesis reviewer should confirm whether M2 and M5 can be carried (CR-02, CR-03) or need an architecture change.

## Output files

| File | Content |
|---|---|
| `00-REPORT.md` | this report |
| `01-FINDINGS.md` | findings H1–H3, M1–M5, L1–L5, I1 with evidence and correction direction |
| `02-HELDOUT-ATTACKS.md` | RV3-B-A01…A18 and the surface injections |
| `03-RESIDUALS.md` | criteria and determination for every declared residual |
| `04-CARRIED-REQUIREMENTS.md` | CR-01…CR-12 and re-review acceptance cases for H1–H3 |
| `evidence/` | scripts, outputs, reviewed-content digests, README |

## Verdict (role vocabulary)

`BLOCKING_FINDINGS_PRESENT`
