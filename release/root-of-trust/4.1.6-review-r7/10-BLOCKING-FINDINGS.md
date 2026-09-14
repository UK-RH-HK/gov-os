# 10 — Consolidated findings (RoT-1 revision 7, certified profile CP-1; synthesis D, AR-0022)

- **Revision reviewed:** `d07d200ac08a52c45071d33074e20cc62fbcc26e` (identical at the review base `1d4d9f3` for `release/root-of-trust/4.1.6/`,
  `spec/`, `docs/`).
- **Panel verified:** reviewer B `54be694` (`BLOCKING_FINDINGS_PRESENT`), reviewer C `34633cc` (`BLOCKING_FINDINGS_PRESENT`).
- **Owner requirements applied:** OWNER-DESIGN-REQUIREMENTS-0001 and -0002 (verbatim texts; binding). -0002 post-dates `d07d200`.
- **Evidence classes:** **E** executed (reference executor, real binaries, real Git, real `rustc 1.98.1`, the pack's checker);
  **C** computed (CS7 unmodified, wrapped); **D** design (exact lines at `d07d200`). "Reproduced" means re-run by this review with
  the result stated in `D-synthesis/01-REPRODUCTION.md`.
- **Blocking** means the finding alone prevents `ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED` under HO-0022 §3.

| ID | Severity | Title | Origin | Adjudication | Blocking |
|---|---|---|---|---|---|
| **RV7-H1** | **HIGH** | Restrictive facts issued by authorities other than the trust-state authority (binary and admitter revocations; security-relevant registrations that raise the OP-11 (b) minimum) take effect at first contact only if a Trust State lists them; no party establishes the listing and no rule bounds its delay | B (RV7-B-H1) + D (RV7-D-A01) | CONFIRMED HIGH, extended | yes |
| **RV7-H2** | **HIGH** | Running-machine C3 currency bounds the age of the anchoring event, not of the Trust State it names: stored, replayed or re-stamped codes, or old offline media, give production C3 on a state up to the anchor validity old; deviates from OWNER-DESIGN-REQUIREMENTS-0002 OT-1 | B (RV7-B-H2) + C (RV7-C-H1) | CONFIRMED HIGH; C-H1 is the same root cause (consolidated) | yes |
| **RV7-M1** | MEDIUM | One onboarding record designates both first-contact sources; the stated first-contact root models two independent designation atoms and omits `{onboard}` | B (RV7-B-M1) | CONFIRMED MEDIUM; not carriable | yes |
| **RV7-M2** | MEDIUM | The certification independence criteria are label comparisons and CC-3 is not an executable, non-circular procedure: two distributions pass as two toolchain lineages, "not rooted in an upstream binary archive" is checked by no verifier or schema, and the owner's target label is not adopted (OWNER-DESIGN-REQUIREMENTS-0002 OT-2) | D (RV7-D-A03) + B (RV7-B-L1) + C (RV7-C-L4) | NEW; B-L1 and C-L4 re-rated LOW → MEDIUM and merged | yes |
| **RV7-M3** | MEDIUM | OP-10 (b) × OP-16 (b): one toolchain lineage plus the other supplier class yields accepted malicious bytes; the stated residuals and invariants rest on a full-matrix reproduction that no rule requires | D (RV7-D-A02) | NEW | yes |
| **RV7-M4** | MEDIUM | A clean CI runner cannot reach the governed use CP-1 claims for it: every first governed use of a project raises `project_first_use`, a terminal-only gate no decision pin can answer | D (RV7-D-A04) | NEW | yes |
| RV7-M5 | MEDIUM | First admission after protected-store loss moves aside a surviving account store without reading its high-water, per-project records or pending obligations | C (RV7-C-M1) | CONFIRMED MEDIUM; not escalated | no (CR7-C-1) |
| RV7-M6 | MEDIUM | No realizable per-project record identity satisfies the five cases of `20` §9 / RT-196 | C (RV7-C-M2) | CONFIRMED MEDIUM | no (CR7-C-2) |
| RV7-M7 | MEDIUM | The journal-honouring condition is unreachable for a first install (record written at the end) | C (RV7-C-M3) | CONFIRMED MEDIUM | no (CR7-C-3) |
| RV7-M8 | MEDIUM | `git clean -fdx` in the first-install crash window removes the untracked overlay and defeats R-INIT-9 | C (RV7-C-M4) | CONFIRMED MEDIUM | no (CR7-C-4) |
| RV7-M9 | MEDIUM | Recovery roll-forward after the exchange depends on the in-memory ARO; the evidence stubs it | C (RV7-C-M5) | CONFIRMED MEDIUM | no (CR7-C-5) |
| RV7-M10 | MEDIUM | The shared conformance vectors detect 14 of 22 held-out code-level regressions of normative rules; 8 survive, including the C3 proof naming the effective state and the admitter revoked in the selected state | D (RV7-D-A06) | NEW | no (CR7-D-01) |
| RV7-L1 | LOW | `trust-root.schema.json` accepts `trust-policy` and `first-contact-authority` at threshold 1 on non-root keys; only the compiled check refuses | B (RV7-B-L2) | CONFIRMED | no (CR7-B-02) |
| RV7-L2 | LOW | A source custodian with no publication history publishes a descendant that drops published revocations | B (RV7-B-L3) | CONFIRMED | no (CR7-B-03) |
| RV7-L3 | LOW | No rule states the Trust State issuance and publication cadence that the 24-hour ceilings require | B (RV7-B-L4) | CONFIRMED; becomes load-bearing under the RV7-H1/H2 corrections | no (CR7-B-04) |
| RV7-L4 | LOW | Two committed re-run outputs are stale against the committed pack; the committed runner is not self-contained | B (RV7-B-L5) | CONFIRMED (both stale leaves reproduced) | no (CR7-B-05) |
| RV7-L5 | LOW | No genesis procedure for the source custodians' "own admitted binary" (R-FCS-1) | B (RV7-B-L6) | CONFIRMED | no (CR7-B-07) |
| RV7-L6 | LOW | Recovery undo has two literal readings after an intervening operation; `20` §6 uninstall "leaves `ABSENT`" contradicts `18` §9 | C (RV7-C-L1, RV7-C-A23) | CONFIRMED; merged | no (CR7-C-6) |
| RV7-L7 | LOW | An anchoring event recorded under the machine's own wrong-ahead clock poisons `clock_high_water`; only a root-signed reset recovers | C (RV7-C-L2) | CONFIRMED | no (CR7-C-7) |
| RV7-L8 | LOW | `floors.json` and `high-water.json` atomicity is unstated (torn reads) | C (RV7-C-L3) | CONFIRMED | no (CR7-C-8) |
| RV7-L9 | LOW | `bootstrap.clock_reset` has no replay or persistence semantics; the only executable model applies a reset from any held Trust Policy, continuously | D (RV7-D-A05) | NEW | no (CR7-D-02) |
| RV7-L10 | LOW | No operator procedure states that an air-gapped machine reads the authenticated private release channel independently of the media | D (RV7-D-A08) | NEW | no (CR7-D-03) |
| RV7-L11 | LOW | Default deny does not hold under a wildcard `informational` subtree: new authority-bearing keys under `ROLES.authority_levels.*.*` pass the checker | D (RV7-D-A07) | NEW instance of carried CR4-B-05 (CS-1) | no (CR4-B-05, CR7-D-04) |
| RV7-L12 | LOW | An unflagged security-relevant change of a non-orderable unit is not listed per project (RV6-L1) | review r6 (carried; B re-run) | CONFIRMED open | no (RT-198) |
| RV7-I1 | INFO | OP-8 record independence is mechanically distinct key ids, execution ids and report digests only | B (RV7-B-I1) | CONFIRMED | — (CR7-B-06) |
| RV7-I2 | INFO | ARCH-0002 carries no `human_approved` field | B (RV7-B-I2) | CONFIRMED | — |
| RV7-I3 | INFO | OWNER-DESIGN-REQUIREMENTS-0002 read with OP-7 (a): C1–C2 within anchor validity stands; C3 needs a state within 24 hours; C's "new owner trade-off" is not one | D (RV7-D-A09) | NEW | — |
| RV7-I4 | INFO | `17` still carries witness, mode-B and OP-7 (b)/(c) rows as normative-looking text under a non-production banner; no excluded mode is reachable | D | NEW | — |
| RV7-I5 | INFO | The acting role remains caller-declared; no trust gate depends on it (RV6-I1) | review r6 | unchanged | — |
| RV7-I6 | INFO | Binding-group derivation (Markdown → compiled YAML) carried to the capability-contract phase (RV6-I2, RT-182) | review r6 | unchanged | — |

No CRITICAL finding: every HIGH needs withheld newer statements, an omitted listing, or a stored or old value, and a machine that
holds the negative, or that receives the newer state, refuses.

---

## RV7-H1 — HIGH — Restrictive facts at first contact depend on Trust State listing that no party establishes

**Statement.**
1. At first admission `gov-admit` computes negatives from the selected Trust State only: its `revocations` and the revocation
   statements **it lists** (`25` AP-4; executor `accept`). A revocation verified at the revocation threshold and present in the
   bundle is ignored when the state does not list it. There is no store at first admission.
2. The same holds for the evaluator: FC-8′ "the admitter is not revoked in the selected state", and for OP-11 (b): AP-SEC raises the
   minimum only from registrations "the selected TSS references with `security_relevant_change`".
3. The sources publish codes, the FCA payload, the procedure and `gov-admit` bytes; never revocation or registration statements
   (`32` R-FCS-3). R-FCS-2 (d) refuses only a descendant that **drops** what the custodian last published; a fact that was never
   listed is not dropped.
4. No rule makes any party establish that a Trust State lists the facts the dedicated revocation authority and the registration
   quorum have issued, or bounds the delay (design extraction: listing-completeness absence check 0 hits; DR-18 names no
   establishing party for completeness).
5. The pack states the opposite: CUR-R1 "a revocation issued within the 24 hours before admission" with bound `{win}`, 24 hours
   (`32` §8, §12; `35` §3, §7; `25` §7; `31` §9); CP-REVOKED shows no trust-state or publication set; `24` §6 blast radius; `17` MS-2
   ("stays effective until a root-signed TPS unrevokes it").
6. CS7 cannot see it: `old_state_selected` calls `sources_publish_thief_state(..., drops_revocation=True)`, which returns `False`
   whenever custodians publish first-hand, so every omission is modelled as a refused drop.

**Evidence (reproduced).**
- RV7-B-A01 (**E**, byte-identical): both custodians publish omitting states; R9 revoked 102 h … 342 h earlier is `ACCEPTED` on 11
  daily states and on re-admission over an older store; controls refuse (a held negative, a listed revocation, a drop).
- RV7-B-A01m (**E**, byte-identical): an executor that applies every held revocation statement refuses only when the statement is
  delivered; withheld by the transport, `ACCEPTED`. The executor change alone does not close the class.
- RV7-B-CS7 (**C**, byte-identical): with an omission strategy, `{fcpub}` (as written) or `{2 trust-state keys, fcpub}` (if
  co-signers checked completeness) is a minimal set for FA and RA_unheld.
- RV7-D-A01 (**E**): the revoked **admitter** evaluates first contact on 11 daily states (`ACCEPTED`; control `ADMITTER_REVOKED`); a
  superseded release is admitted on 11 daily states while a security-relevant registration stays unreferenced (`ACCEPTED`;
  control `RELEASE_BELOW_SECURITY_MINIMUM`, minimum 10).

**Failure scenario.** A release is found malicious (TB-S1) or defective, or `gov-admit` itself is found vulnerable. The revocation
authority revokes it. The trust-state publication process (compromised, misconfigured, or holding one key while the co-signer signs
what it is handed) keeps issuing daily states that omit the revocation. Both custodians see no drop and publish. For as long as the
omission lasts, every first install, CI image build and re-admission over an older store admits the revoked binary (or runs the
revoked admitter) as the machine's TCB, and `gov-admit` shows "state 6 h old".

**Severity.** HIGH: a lower-trust input (the rank-3 publication process as written; at most the trust-state threshold, a purpose
OP-4 separates from revocation) yields a current higher-trust fact (a revoked binary or evaluator as the current TCB; an older
release as eligible). The stated bound (24 h) is false; the actual bound is the unbounded listing delay plus 24 h. Precedent:
RV4-H2, RV6-H2. Not CRITICAL: a store holding the negative refuses; a running machine delivered the statement refuses (`17` S5).

**Owner conformance.** OP-4 "Every key/statement purpose must remain domain-separated and mechanically enforced" and "2-of-3
dedicated revocation authority": the trust-state purpose nullifies the revocation purpose at first contact. OP-11 (b) "raise the
minimum … at every security-relevant content change": subordinate to an unbounded listing.

---

## RV7-H2 — HIGH — C3 currency names a Trust State of unbounded age

**Statement.**
1. Admission bounds the selected state's own age: FC-9 refuses a Trust State issued more than 24 hours before the admission clock.
2. The running path does not. `24` R-ANC-4 needs "a currency proof of at most 24 hours naming the effective Trust State"; R-CUR-1
   (P1) bounds the pin provisioning or human confirmation **event** ("no older than 24 hours"); R-CUR-2 (P2) needs two identical
   in-gate codes equal to the effective state's code, clock "none". Neither reads the named state's `issued_at` (design: absence
   check 0 hits in `24`, `25`, `27`, `31`). The reference `gov_run` has no `issued_at` input.
3. The machine can check only that typed or pinned codes are identical and name its effective state. When newer states are withheld
   (transport) or never received (air-gapped), the effective state is old, so a stored code (a runbook, a pin template, cached
   page), a re-stamped CI pin, or the codes on old offline media satisfy the proof, and the state is shown "published as of" now.
4. The pack states the opposite: RS-1b "can be stale by up to 24 hours"; `24` §6 "Replayed … anchoring codes older than 24 hours:
   refused (R-CUR-1)"; `24` §5.2 CI "C3 only within 24 hours of provisioning"; `28` A-R7-08 "no C3". BA11r7 establishes A-R7-08 only
   by hard-coding `sources_latest`.

**Evidence (reproduced).**
- RV7-B-A02 (**E**, byte-identical): C3 `ALLOWED` with stored codes naming a state issued 4.5 months earlier while `gov-admit` refuses
  the same codes (`FIRST_CONTACT_STATE_TOO_OLD`); CI C3 `ALLOWED` with a pin re-stamped today naming a 6-day-old state; controls
  refuse. BA11r7 re-evaluated without the `sources_latest` assumption shows C3 below the revoking state.
- RV7-C cur7x (**E**, byte-identical): an air-gapped machine admitted from media within 24 h; 37 days later `confirm-state` from the
  same media and C3 `ALLOWED` on a state 882 h old that a later state revokes; re-admission with the same codes refused.
- RV7-B-CS7 (**C**, byte-identical): `{transport, stored_old}` minimal for P2; removed by a compiled state age at C3.
- RV7-D-A10 (**D**): on CI, pin currency reaches only gate-less C3 (`trust verify-artifact` acceptance); gated C3 needs a terminal with
  in-gate codes. The workstation and media instances are unaffected.

**Failure scenario.** A workstation or air-gapped production machine never receives the Trust State that revokes release R. The
operator types codes from a runbook, or from the original courier media, into the `update` trust gate. The proof names the
effective (old) state, so `update --apply`, rollback or `kernel reinstall` installs R, which every connected machine refuses.

**Severity.** HIGH: a lower-trust input (a stored, replayed or re-stamped code; stale media, rank 5) yields a current higher-trust
fact (C3 currency "as of now") and a revoked release installed. Review r6 classified "a stored or replayed value of unbounded age
selects the state" as not core. Not CRITICAL: it needs withheld or unreceived newer states and a stored or old value; a machine that
holds the negative or receives the newer state refuses.

**Owner conformance.** OP-7 (a): "production install/update/rollback requires a fresh local trust confirmation/state anchor no
older than 24 hours"; "no stale/unanchored state may be presented as current". OWNER-DESIGN-REQUIREMENTS-0002 OT-1 (binding): "the
required trust-state anchor must satisfy the existing 24-hour freshness requirement; offline media receives no special longer
freshness window; stale trust state on otherwise authentic media cannot become current merely because the medium is trusted".
**Deviation.**

---

## RV7-M1 — MEDIUM (blocking) — One onboarding record designates both sources

**Statement.** `32` R-FCD-2: "Operators receive the two source identities and the procedure at onboarding, from the organisation's
copy of the root ceremony record" (also `06` §2 step 1, `01` TA-5′; register PI-01, DR-38). The operator cannot authenticate that
copy with platform tools, and the FCA's `sources` field is inside the record the look-alike sources serve. CS7 models designation as
two independent atoms (`desig1`, `desig2`); CP-FC-ROOT, FC-R1′/FC-R3′ ("exactly the eight sets"), INV7-FC, `35` §7 and D-0008 rule
(25) present OP-13 (b) as needing two independent compromises.

**Evidence (reproduced).** RV7-B-CS7 (**C**, byte-identical): the atom `onboard ⇒ desig1 ∧ desig2` makes `{onboard}` a minimal set
for FA under G_BYTES and G_REVOKED; the control reproduces the committed CP-FC-ROOT. FA7 S2 D (**E**, byte-identical): both look-alike
pages → `ACCEPTED_BY_SUBSTITUTED_EVALUATOR`.

**Severity.** MEDIUM: the designation input is core when delivered out of band (review r6), so not HIGH. **Not carriable:** the owner
ratifies OP-13 (b) against a stated bound that is false, and either correction is architecture text (a single designation atom in
the stated root, or a rule that the two identities reach operators through independent channels).

---

## RV7-M2 — MEDIUM (blocking) — Certification independence criteria are label comparisons; CC-3 is not executable

**Statement.**
1. `33` R-BENV-6″, `30` R-REP-9′ and `35` CC-3 require lineages "independent by provenance" and "at least one lineage's
   `bootstrap_root` is not an upstream binary compiler archive, and its compiler is itself a registered, reproduced bootstrap
   release". Mechanically: independence is inequality of four free-text strings (`TOOLCHAIN_ATTRS`); no verifier, schema or
   ceremony check reads `bootstrap_registration` or `archive_sha256` or tests "not rooted in an upstream archive"; the schema requires
   only `toolchain_id` and the strings.
2. CC-2 has the same shape for supplier classes (strings plus disjoint key ids, RV7-B-L1).
3. CC-3 names "diverse double-compilation agreement" but defines no procedure (which stages are compared, what evidence schema,
   how a bootstrap chain is evidenced); ENV7 states that it is "not executed here".
4. Targets are labelled `NOT_CERTIFIED_PENDING_CRITERIA`, not the owner's `NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE`.

**Evidence.** RV7-D-A03 (**E**): a distribution's rustc (bootstrapped from the upstream stage0 archive) with distinct strings and no
bootstrap registration, beside the upstream archive lineage → `ACCEPTED`; controls: identical strings refused, honest bootstrap lineage
accepted. RV7-B-A04 (**E**, byte-identical): `sup-A2` naming the same Debian upstream with other spellings and a second Debian key →
`ACCEPTED`. `35` §5 and `profile/CP-1.yaml` labels (**D**).

**Severity.** MEDIUM: no target is certified today and first contact refuses an uncertified target (fail closed); the establishing
party of the registry is the root threshold. **Not carriable:** OWNER-DESIGN-REQUIREMENTS-0002 makes an explicit, executable/testable,
non-circular criterion a precondition of architecture acceptance without a certified target, and states "Do NOT accept 'two
different distributions' or 'two mirrors of the same compiler binary' as independence". The criterion as specified accepts exactly
that. B-L1 and C-L4 are re-rated from LOW because -0002 (binding, received after B completed) turns them into an acceptance
precondition.

---

## RV7-M3 — MEDIUM (blocking) — Cross-axis toolchain and supplier compromise is outside the stated bounds

**Statement.** AP-6 and R-REP-4′ require at least two matching reproductions spanning two independent supplier classes and two
independent lineages, and no valid conflicting reproduction; R-REG-3 (f) requires each custodian's own reproduction. No rule
requires a reproduction, or a custodian build, in every (class × lineage) combination (design: absence check 0 hits). CS7
(`claims`, `custodian_digest`) and ENV7 (`acceptance`: "Every reproducer builds in every … pair") assume full-matrix builds. INV7-TC,
INV7-ENV-B, CP-TOOLCHAIN, CP-ENV, TB-S2″, TA-12″ and `21` §4 ("each residual needs both lineages, both classes, hidden common
provenance or the compiler source") rest on that assumption.

**Evidence.** RV7-D-A02: (**E**) the executor accepts a malicious digest whose two reproductions are (sup-A, tc-up) and (sup-B,
tc-boot); an honest (sup-A, tc-boot) reproduction would conflict. (**E**, real `rustc 1.98.1`) a compromised upstream lineage and a
compromised class-B linker produce bit-identical bytes in (A,up), (B,boot) and (B,up); only (A,boot) is clean. (**C**) with one
build per party, 120 of the 144 assignments that meet AP-6's coverage have a cross pair (`{toolchain_up, env_up_b}` or an analogue)
as a minimal set, and a cross pair is absent exactly when the reproducers' and custodian's combinations cover all four.

**Severity.** MEDIUM: the cross pair still needs two independent upstream compromises that coordinate on identical bytes, the same
count as the stated residual; but the stated bound is false, and the owner is told that OP-10 (b) × OP-16 (b) needs both lineages or
both classes. **Not carriable:** closing it is a normative coverage rule or restated computed blocks.

---

## RV7-M4 — MEDIUM (blocking) — A clean CI runner cannot reach the governed use CP-1 claims

**Statement.** `27` §2 raises `project_first_use` at "first governed use of a project on a machine without a per-project record"
(DR-25; `20` §9). It is a C3 kind with state codes, always in `local_terminal_only` (`27` §3.2), absent from the decision-pin
`gate_kind` enum, and needs a controlling terminal (`TRUST_GATE_NEEDS_TERMINAL`). A clean runner job has no per-project record and
no terminal. No text provisions a record or a selection into CI images (absence check 0 hits). `24` §5.2 nevertheless states "valid
pin, intact repository → `ANCHORED`; C1–C2", and BA11r7 models it without the gate.

**Evidence.** RV7-D-A04 (**D**); RV7-D-A10 (**D**).

**Severity.** MEDIUM: fail closed (no trust is gained), but a machine class HO-0001 §3.2 requires the architecture to solve is
answered with a reachable-class statement that the gate rules make false, and OP-3 Mode A × OP-11 (b) × CI is a real combination the
owner has not been shown. **Not carriable:** the correction is a rule choice (a provisioned per-project selection, a bounded decision
pin for `project_first_use`, or a stated "CI runs no governed project work"), and one of those options may need owner confirmation
(`11` CD7-4).

---

## MEDIUM carried (non-blocking)

| ID | Statement (full text in the origin) | Evidence (this review) | Why carriable | Carried as |
|---|---|---|---|---|
| RV7-M5 | `C/01-FINDINGS.md` RV7-C-M1. First admission is decided by the protected store's marker; the move-aside discards a surviving account-store high-water, per-project records and pending obligations. | adm7x X2 reproduced (identical except run-dependent X5 counts) | Exposure after the loss is bounded by FC-9 (both sources, state ≤ 24 h) and the security minimum; account-store floors are restrictors, so reading them before the move-aside cannot escalate. Not escalated to HIGH: the regression admits only material within 24 hours of both sources' current state. The fix is a bound rule inside R-ADM-8″ with a test. Interacts with RV7-H1 (a surviving held negative is exactly what the omission attack needs to be absent). | CR7-C-1 (strengthened in `11` §6) |
| RV7-M6 | RV7-C-M2 record identity | ident7 reproduced: `every_candidate_contradicts_the_text` true; in this run inode reuse also made I2 match a different repository re-cloned at the same path | fail closed on one side (LR-4 availability); A2 request on the other | CR7-C-2 |
| RV7-M7 | RV7-C-M3 honouring unreachable for a first install | txn7 `first_install_honouring` reproduced equal | fail closed; the registry entry at `prepared` exists in `18` §4 | CR7-C-3 |
| RV7-M8 | RV7-C-M4 `git clean -fdx` defeats R-INIT-9 | txn7 summary reproduced equal | classifications recoverable from Git; a marker rule closes it | CR7-C-4 |
| RV7-M9 | RV7-C-M5 roll-forward depends on the in-memory ARO | txn7 `rollforward_model` reproduced equal | fail closed (`IN_TRANSACTION`) | CR7-C-5 |
| RV7-M10 | RV7-D-A06: 8 of 22 mutants survive the shared vectors (M01 C3 proof need not name the effective state; M07 account-store floors ignored; M08 admitter does not require the two state codes to agree; M11 AP-7 publication not required; M14 FCA root threshold under any chain version; M15 clock skew 30 days; M16 admitter revoked in the selected state not refused; M22 registration equivocation not refused) | executed; controls equal committed verdicts | each rule is already normative; the requirement is a vector that kills the mutant on both executors | CR7-D-01 |

## LOW

| ID | Statement | Evidence | Carried as |
|---|---|---|---|
| RV7-L1 | RV7-B-L2 as stated | RV7-B-A04-A05 byte-identical | CR7-B-02 |
| RV7-L2 | RV7-B-L3 as stated | RV7-B-A01 publication row byte-identical | CR7-B-03 |
| RV7-L3 | RV7-B-L4 as stated. The corrections of RV7-H1 and RV7-H2 both require a Trust State and two-source publication at least every 24 hours; that cadence must be a stated obligation with a failure surface. | design | CR7-B-04 |
| RV7-L4 | RV7-B-L5 as stated | DA07r6 on the revision-7 plan and RV6-B-A03 re-run: exactly the 2 + 2 stale leaves B reports; REGISTER-CHECK, DA09r7, DA04r7 byte-identical when run in the export (the committed `crashmig7.json` present) | CR7-B-05 |
| RV7-L5 | RV7-B-L6 as stated | design | CR7-B-07 |
| RV7-L6 | RV7-C-L1 and the `20` §6 uninstall inconsistency (RV7-C-A23) | txn7 rows and `uninstall` reproduced (44 row differences are commit ids and stash messages only) | CR7-C-6 |
| RV7-L7 | RV7-C-L2 as stated | adm7x X4 reproduced | CR7-C-7 |
| RV7-L8 | RV7-C-L3 as stated | adm7x X5 reproduced (4,220 torn reads in this run; 0 below-floor reads) | CR7-C-8 |
| RV7-L9 | `clock_reset` has no replay or persistence semantics: nothing binds a reset to the effective Trust Policy, one application, or high-water values recorded before the policy was issued. The retained P4r4 model (cited by `17`) applies a reset from any held policy on every ingest; the revision-7 executor does not implement it and no vector tests it. A replayed genuine old policy then lowers the high-water on a machine with a store, which re-opens RS-2b-style clock rollback for as long as the policy is held. Requires a root-signed reset to have existed. | RV7-D-A05 (E on the retained model; D) | CR7-D-02 |
| RV7-L10 | No operator procedure says that, for an air-gapped machine, the authenticated private release channel's codes are read independently of the media (admission and in-gate codes). FC-4′ still needs two identical codes. | RV7-D-A08 (D) | CR7-D-03 |
| RV7-L11 | New authority-bearing keys (a new level, a new key on L5) under the wildcard `informational` subtree `ROLES.authority_levels.*.*` pass the checker (exit 0). New files and new keyed-member keys are refused (exit 2). This is the open wildcard concern of CS-1 (CR4-B-05) in a shape Gate W may use. | RV7-D-A07 (E) | CR4-B-05, CR7-D-04 |
| RV7-L12 | RV6-L1 as stated in review r6 | RV6-B-A10 and RV6-D-A03 re-run by B, byte-identical | RT-198 |

## INFO

| ID | Statement |
|---|---|
| RV7-I1 | RV7-B-I1 as stated. OP-8's "genuinely separate verifier executions/evidence" rests on key custody (TB-4′); carried CR7-B-06. |
| RV7-I2 | RV7-B-I2 as stated. D-0008: `PROVISIONAL`, `PROPOSED`, `human_approved: false`, `in_effect: false`, no `chosen_option`; D-0007 `ACTIVE`; ARCH-0002 `PROVISIONAL`, `PROPOSED`, `in_effect: false`, no `human_approved` field. The HO-0022 §2b states hold. |
| RV7-I3 | OWNER-DESIGN-REQUIREMENTS-0002 read with OP-7 (a) (RV7-D-A09): C1–C2 on an anchored chain within 90 days (CI 7 days) is the owner's selection; C3 needs a Trust State within 24 hours (the RV7-H2 correction). The D-0008 ratification package should state this reading explicitly. Reviewer C's statement that this is a new owner trade-off is refuted. |
| RV7-I4 | `17` §3, §6, §7, §13 and §15 still contain rows for the freshness witness, mode B and OP-7 (b)/(c) under a banner that marks them non-production. PROF7 (113/113 checks, 24/24 exclusions) and RV7-B-A09 (schema sweep) reproduce: no excluded mode is reachable. Text hygiene only. |
| RV7-I5 | RV6-I1 unchanged (`27` §5). |
| RV7-I6 | RV6-I2 unchanged (RT-182). |
