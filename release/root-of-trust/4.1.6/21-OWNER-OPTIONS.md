# Output 21 — Owner selections for CP-1 (OP-1 … OP-16), surfaced trade-offs, and non-production history

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Rewritten in revision 7. The owner has selected the parameters: OWNER-DESIGN-REQUIREMENTS-0001
> (`release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md`, verbatim text governs). Those selections are
> **binding design inputs**, not approval of D-0008, which stays `PROVISIONAL` / `PROPOSED` with `human_approved: false`.
> - §1 records each selection and where CP-1 applies it (details and enforcement: `35` §2).
> - §2 records the owner trade-offs this revision surfaced; none is decided.
> - §3 maps review r6's open option families (F1, C) onto the selections.
> - §4 states the computed consequences for CP-1 only (generated blocks; `decision-register/statements_check.py`).
> - §9 keeps the revision-6 option tree as **non-production history**. Nothing in §9 is a mode of CP-1; each unselected answer is
>   excluded (`35` §4) and absent or refused.

## 1. The selections

| Parameter | Owner selection (quoted from OWNER-DESIGN-REQUIREMENTS-0001) | Applied in CP-1 |
|---|---|---|
| D-0008 direction | "Selected design target: Option C — RoT-1." "A, B, D, E and F are not supported production alternatives" | profile `governance-os.rot1/CP-1`; EX-22 |
| OP-1 | "keys = 3", "threshold = 2-of-3"; Product Owner, Independent Security and Recovery Root Custodians; offline hardware-backed devices; root ceremony for Trust Policy and root-lineage changes, not ordinary releases | `05` §1, KS-1″, KS-14; ceremony record roles (`05` §7) |
| OP-2 | "(b) delegated registration quorum", "2-of-3", single-purpose hardware-backed registration keys | `05` KS-10″; `30` §5 |
| OP-3 | "Mode A — always_gate"; local human trust gate for adoption, production installation, update, rollback, downgrade and recovery; repository gate records are requests only | `27`; TPS `gating.mode` const |
| OP-4 | separate candidate key "YES"; production final identity threshold-protected (≥ 2 signatures); trust state 2-of-3; certification two independent records; revocation 2-of-3 with root-threshold emergency; separate retrieval-profile purpose; no witness | `05` §1–§3 (KS-15, KS-17, KS-18) |
| OP-5 | "30 days", informational only | display only (`35` §2) |
| OP-6 | "(a) once per machine" (per verifier trust store); a later lineage change requires re-admission and re-confirmation | `06` §3 step 5; `24` §3.2 |
| OP-7 | "(a) anchored only"; workstation anchors ≤ 90 days; CI admission/image anchors ≤ 7 days; production install/update/rollback need a state anchor no older than 24 hours; expiry → C0; no stale state shown as current; high-water never moves backwards | `24` §4.3 (R-ANC-1…R-ANC-5, R-CLK-1); `32` FC-9 |
| OP-8 | "2" independent verification records from separate verifier executions | `30` R-VER-2; AP-5 |
| OP-9 | "(b) 2-of-3" plus "(d) registration includes final binary digests"; mismatch blocks; evidence names exact source, toolchain and environment identities | `30` §7; `05` KS-9′ |
| OP-10 | "(b) diverse, independently bootstrapped compiler agreement"; independence by provenance; a target that cannot satisfy it is not certified | `33` R-BENV-6″; `35` CC-3 |
| OP-11 | "(b) raise the minimum release sequence at every security-relevant content change"; no grace periods; the repository never chooses among eligible releases for the local trust authority | `19` E3′; `29` DR-25 |
| OP-12 | "(a) separate compiled program, registered and reproduced" | `31` R-ADM-1″; `32` FC-8′ |
| OP-13 | "(b) two owner-controlled sources under genuinely separate custody; both must match"; authenticated private release channel and separately controlled immutable/offline mirror or media; byte-identical; mismatch fails closed; one trust-state publisher must not compose the code carried by both | `32` §3–§7 |
| OP-14 | "(b) all admission records expire"; re-admission preserves and enforces the stored high-water | `31` R-ADM-7″, AP-R1…AP-R6 |
| OP-15 | "(a) read-only only" | `31` GB-3′ (C0-R) |
| OP-16 | "(b) require matching builds from at least two genuinely independent supplier classes"; provenance separation; static/self-contained linking; narrow certified target set | `33` R-BENV-5″; `35` §5 |
| First-contact composer/signer | not the ordinary trust-state publisher; "root threshold 2-of-3" after independent reproduction and verification of the admitter | `32` R-FCA-1…R-FCA-4, R-FCS-1…R-FCS-3 |
| Build-environment manifest author/signer | no single authoritative author; deterministic generation; authoritative only with agreeing reproducer evidence and the "2-of-3" registration over that exact identity | `33` R-BENV-2″, R-BENV-3″, R-BENV-7″ |
| Initial certified scope | only Option C, OP-2 (b), OP-3 Mode A, OP-7 (a), OP-10 (b), OP-12 (a), OP-13 (b), OP-16 (b); the listed exclusions; a small number of reproducible static targets | `35` §4, §5 |

## 2. Owner trade-offs surfaced in revision 7 (not decided)

| ID | Conflict | CP-1 meanwhile | Options and consequences |
|---|---|---|---|
| **OT-1** | OP-13 (b)'s offline media channel versus OP-7 (a)'s 24-hour limit for production installation, which includes first admission | the second source is the immutable mirror read at admission; media carry its material and are refused when the state is older than 24 hours | `35` §6 (OT-1a…OT-1c) |
| **OT-2** | OP-10 (b)'s independently bootstrapped compiler agreement for the current compiler version, not yet evidenced | no target is certified until CC-3 holds; no fallback | `35` §6 (OT-2a…OT-2c) |

No other selected parameter was found infeasible or contradictory to a security invariant.

## 3. Review r6's option families under the selections

Review r6 (`11-CORRECTION-DELTA.md` CD6-1, CD6-2) presented two owner trade-offs. The owner requirements answer them as follows;
this page decides nothing beyond the owner text.

| Review r6 option | Status under OWNER-DESIGN-REQUIREMENTS-0001 | Where |
|---|---|---|
| F1-a each source custodian derives the first-contact value first-hand | applied to the state code: each source custodian publishes a state code only for a Trust State it verified (R-FCS-2) | `32` §5 |
| F1-b lineage and admitter set in a root-threshold record; state per Trust State | applied: the First-Contact Authority record at root threshold ("First-contact composer/signer") | `32` §3 |
| F1-c the composer accepted as a root atom | excluded (EX-23): "must NOT be composed by the ordinary trust-state publisher" | `35` §4 |
| C-a mandatory maximum age per path | applied with the compiled OP-7 (a) ceiling of 24 hours on every path | `32` FC-9, §8 |
| C-b state always read online | not selected as such: OP-13 (b) keeps a media channel; the resulting conflict is OT-1 | `35` §6 |
| C-c mixed | not needed | — |

Computed consequence of the age bound for CP-1 (the control with the revision-6 rules is in the CP-R6-CONTROLS block, `28`):
the CP-REVOKED block of `32` §8.

## 4. Computed consequences for CP-1

Every block below is generated by `evidence/r7/CS7-derivation-calculator.py` for the one production configuration.

First admission:

<!-- CS7:BEGIN CP-FC-ROOT -->
| Victim | First-contact root: minimal sets that admit a malicious first TCB with no key | Other minimal sets |
|---|---|---|
| FA (first admission) | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src} | 49 |
<!-- CS7:END CP-FC-ROOT -->

Malicious bytes for a genuine registration, per victim class (OP-9 (b) + (d), OP-2 (b), OP-8 = 2):

<!-- CS7:BEGIN CP-BYTES -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| Victim | Minimal sets: malicious bytes for a genuine registration (CP-1) |
|---|---|
| P1 | {2 registration custodians, 3 reproducer processes} |
| P1A | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, src2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, desig1}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig2, op1src} |
| P2 | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, src2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, desig1}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, src2, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, desig2}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig1, op1src}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, desig2, op1src} |
| CIR | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, pinprov} |
| FA | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
| RA_held | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
| RA_unheld | {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
<!-- CS7:END CP-BYTES -->

Source, inputs, toolchain, environment and constitutional content: `30` §10 (CP-SRC, CP-INPUTS), `33` §6 (CP-ENV, CP-TOOLCHAIN),
`34` §4 (CP-CONTENT).

**Combinations (RV6-L12).** CP-1 has one combination of OP-10 and OP-16: (b) with (b). Every other pair is excluded (EX-15,
EX-21). Under that combination neither the upstream toolchain lineage alone nor one supplier class alone yields malicious bytes
(INV7-TC, INV7-ENV-B); each residual needs both lineages, both classes, hidden common provenance or the compiler source
(CP-TOOLCHAIN, CP-ENV).

## 9. Non-production history: the revision-6 option tree

The revision-6 option tree (`4106885`, `21`) presented each answer below with computed consequences. None is a production mode
of CP-1. Each is excluded by the mechanism named in `35` §4 and is absent from, or refused by, the certified verifier and
admitter model (PROF7).

| Revision-6 answer (history) | Status in CP-1 |
|---|---|
| OP-2 (a) registration at root threshold | excluded, EX-09 |
| OP-3 mode B (certified updates without the human gate) | excluded, EX-06 |
| OP-4 "no" (one everyday key for candidate and final) | excluded, EX-10 |
| OP-6 (c) confirmation at every `init` | excluded, EX-11 |
| OP-7 (b) maximum anchor age as a mode; (c) expiring freshness witnesses; (d) compiled epoch accepted for use | excluded, EX-12, EX-01, EX-07, EX-08 |
| OP-8 = 1 | excluded, EX-13 |
| OP-9 (a), (c); registration without binary digests | excluded, EX-14 |
| OP-10 (a) accept the upstream archive; (c) owner-built archive as the production answer | excluded, EX-15 |
| OP-11 (a) keep superseded releases eligible; (c) grace period `eligible_until` | excluded, EX-16, EX-07 |
| OP-12 (b) auditable script; (c) helper-machine hand-over | excluded, EX-03, EX-02 |
| OP-13 (a) one source; (c) second authentication path, "either suffices" or "all agree"; (d) media as the only source | excluded, EX-17, EX-04, EX-05, EX-18 |
| OP-14 (a) validity on image records only | excluded, EX-19 |
| OP-15 (b) C0–C2 for a revoked binary | excluded, EX-20 |
| OP-16 (a) accept upstream components; (c) owner-built environment as the production answer | excluded, EX-21 |
| D-0008 options A, B, D, E, F | not supported production alternatives, EX-22 |
| The revision-6 first-contact manifest composed per Trust State; `gov trust fc-procedure` | withdrawn, EX-23, EX-24 |

Reintroducing any of them requires a separately governed and independently reviewed release with a new profile identity (`35` §1).

No selection is approved by this document.
