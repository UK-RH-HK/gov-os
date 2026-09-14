# 01 — Findings (review r7 B, trust and security, AR-0020)

- **Revision reviewed:** RoT-1 revision 7, certified profile CP-1, `d07d200ac08a52c45071d33074e20cc62fbcc26e` (pack, schemas,
  register, profile, D-0008, ARCH-0002 unchanged at the review base `7e50c6e`).
- **Evidence classes:** **executed** = the architect's reference executor `evidence/r7/gov_admit_reference_r7.py` loaded
  unmodified through `w7world.py` (real Ed25519 through OpenSSL, `sha256sum`), or the architect's instruments run unmodified;
  **computed** = the architect's `CS7-derivation-calculator.py` loaded unmodified with functions wrapped and the originals called
  (control reproduces the committed blocks); **code** = the reference executor's source; **design** = pack text at `d07d200`.
- Probe scripts and outputs: `evidence/probes/`, `evidence/outputs/`.
- Severity per HO-0020 §4. This review does not issue an architecture verdict and does not approve D-0008.

| ID | Severity | Title | Blocking |
|---|---|---|---|
| **RV7-B-H1** | HIGH | A revocation issued by the revocation authority is effective at first contact only if a Trust State lists it; no party establishes that listing, so a revoked binary is admitted without limit in time | yes |
| **RV7-B-H2** | HIGH | The C3 currency proof bounds the age of the confirmation or pin, not the age of the Trust State it names: stored or re-stamped state codes make a stale state "published as of now" | yes |
| **RV7-B-M1** | MEDIUM | Both source identities reach the operator in one onboarding record; the stated first-contact root models them as two independent atoms and omits the one-input set | yes (not carriable without an architecture text change; §4) |
| RV7-B-L1 | LOW | Supplier-class and toolchain-lineage "independence by provenance" is inequality of root-signed free-text strings | no (carried CR7-B-01) |
| RV7-B-L2 | LOW | The certified trust-root schema accepts `trust-policy` and `first-contact-authority` grants at threshold 1 on non-root keys; only the compiled check refuses | no (CR7-B-02) |
| RV7-B-L3 | LOW | R-FCS-2 (d) is relative to the custodian's own publication history; a source custodian without history publishes a descendant that drops published revocations | no (CR7-B-03) |
| RV7-B-L4 | LOW | No rule states the Trust State issuance cadence that the compiled 24-hour admission age requires | no (CR7-B-04) |
| RV7-B-L5 | LOW | Evidence fidelity: two committed re-run outputs are stale against the committed pack, and the committed runner is not self-contained | no (CR7-B-05) |
| RV7-B-L6 | LOW | R-FCS-1 requires each source custodian to verify with "its own admitted binary", but admission needs both sources' codes; no genesis procedure says how a custodian's verifier is established before any source publishes | no (CR7-B-07) |
| RV7-B-I1 | INFO | OP-8 record independence is enforced mechanically only as distinct key ids, execution ids and report digests | — |
| RV7-B-I2 | INFO | ARCH-0002 carries no `human_approved` field | — |

---

## RV7-B-H1 — HIGH — Revocation effectiveness at first contact is selected by Trust State listing, which no party establishes

### Statement

1. `gov-admit` computes the negative set of an admission from the selected Trust State only: its `revocations[]` and the
   revocation statements **it lists** in `revocation_statements[]` (`25` AP-4 "the revocation statements it lists"; code:
   `accept`, `if s["digest"] in set(tp.get("revocation_statements", []))`). A revocation statement verified at the revocation
   threshold and present in the bundle is ignored when the state does not list it. At first admission there is no store
   (AP-R4 applies only held negatives).
2. The first-contact sources publish codes, the FCA payload, the procedure text and `gov-admit` bytes (`32` R-FCS-3); they never
   carry revocation statements. The state code names whatever Trust State the trust-state key holders signed.
3. No rule makes any party establish that a Trust State lists the revocations the dedicated revocation authority has issued, or
   bounds the delay:
   - `32` R-FCS-2 (d) refuses only a descendant that **drops** a revocation of the state the custodian last published; a
     revocation never published in any state is not dropped.
   - `30` R-PUB-1′…R-PUB-4′ constrain registrations and binaries, not revocations. `05` §7 has no rule for trust-state signers.
   - `32` §5.1: the publisher "signs Trust States only as one of the trust-state keys' holders"; no rule has the co-signers
     check revocation completeness.
4. The pack states the opposite:
   - `32` §8 and §12, `35` §3 and §7, `25` §7, `31` §9: **CUR-R1** "a revocation issued within the 24 hours before admission"
     with bound `{win}`, **24 hours**.
   - `32` §8 CP-REVOKED: the FA and RA_unheld rows contain no trust-state-key or publication-process set.
   - `17` MS-2: "A verified revocation stays effective until a root-signed TPS `unrevokes` it."
   - `24` §6 "Trust-state key blast radius" covers only descendants that drop a held or published revocation.
   - Register: DR-18 names "the trust-state and revocation key holders at threshold"; the `trust-state-statement` input row
     `revocation_statements` names "revocation keys at threshold or root emergency" as establishing party. Neither names who
     establishes that the listing is complete.
5. The calculator cannot see it. `CS7.old_state_selected` calls `sources_publish_thief_state(C, R, drops_revocation=True)`,
   which returns `False` whenever `H_SOURCE_FIRST_HAND` is on, so every modelled thief state that omits a revocation is treated
   as a drop the custodians refuse. INV7-AGE ("every non-root set admitting a revoked binary needs `win` or stored codes with the
   clock set back") holds only because the strategy is absent.

### Evidence

- **executed** `outputs/RV7-B-A01.json` (reference executor unmodified). REVOC_R9 revokes R9, signed at the revocation threshold,
  issued 2026-09-10; it is in every bundle. T11o is signed by two trust-state keys, issued 2026-09-14T00:00Z, has the content of
  the genuine T11, and does not list REVOC_R9.

  | Row | Result |
  |---|---|
  | both custodians publish T11o after T10, and T12o after T11o (`custodian_publish`) | published |
  | first admission of R9 on T11o, state 6 h old, revocation 102 h old | `ACCEPTED` |
  | ten daily descendants T12o…T21o, each admitted 6 h after issuance (revocation up to 342 h old) | `ACCEPTED` ×11 |
  | re-admission over a store that predates the revocation | `ACCEPTED` |
  | control: a store holding the negative | `BINARY_REVOKED_IN_HELD_STATE` |
  | control: T11L lists R9; T11s lists REVOC_R9 only in `revocation_statements` | `BINARY_REVOKED` ×2 |
  | control: a descendant that drops the published R7 revocations | custodian refuses, `STATE_DROPS_REVOCATIONS` |

- **executed** `outputs/RV7-B-A01m.json`. A scratch copy of the executor is mutated to apply every verified revocation statement
  held (as `17` S5 states for running machines). With REVOC_R9 in the bundle: `BINARY_REVOKED`. With the transport withholding
  it, the machine sees only what the sources name: `ACCEPTED`. The executor change alone does not close the class.
- **computed** `outputs/RV7-B-CS7.json`. The control reproduces the committed CP-REVOKED rows (FA, RA_held, RA_unheld) and
  CP-FC-ROOT exactly. Adding one strategy (a state omitting a never-published revocation) gives new minimal sets:

  | Reading | FA | RA_unheld | RA_held | P2 (running, in-gate codes) |
  |---|---|---|---|---|
  | A01-VA, as written (no party establishes listing completeness) | **{fcpub}** | **{fcpub}** | none | {transport, fcpub} |
  | A01-VB, if trust-state key holders verified completeness first-hand (not stated) | {2 trust-state keys, fcpub} | {2 trust-state keys, fcpub} | none | {2 trust-state keys, transport, fcpub} |

  Both readings contradict INV7-AGE and INV7-NO-COMPOSER as stated for G_REVOKED, and the CP-REVOKED block.
- **design** as listed in the statement. No acceptance case covers it: RT-184 and RT-191 test drops and a 6-hour window
  (A-R7-02, A-R7-05); none tests a revocation older than 24 hours that no state lists.

### Failure scenario

1. TB-S1 is exercised (two registration custodians and the reproducer quorum), or a genuine release is found defective. Its
   binary B is registered and published at T.
2. The revocation authority issues a revocation of B at T+1 day.
3. The trust-state publication process omits it from every later state (compromised, misconfigured, or holding one trust-state
   key while an honest co-signer signs what it is handed). It keeps issuing states daily, so first contact stays available.
4. Both source custodians verify each state at threshold and see no drop, so they publish its codes.
5. For weeks, every first install, every CI image build and every re-admission over a store older than the revocation admits B
   as its TCB. `gov-admit` shows "state 6 h old".
6. The dedicated 2-of-3 revocation authority (OP-4) has no effect on those machines, and no root `unrevokes` was issued.

### Why HIGH

- A lower-trust input selects a current higher-trust fact: a revoked, possibly malicious binary becomes the current TCB of a
  first-install machine.
  - As written, the input is the rank-3 publication process.
  - Under the stricter reading, it is the trust-state threshold. That is below the root threshold MS-2 requires for lifting a
    revocation, and it is a purpose OP-4 separates from revocation.
- The stated bound (24 hours) is false. The actual bound is the listing delay plus 24 hours, and no rule bounds that delay.
- The harm is RV6-H2's: a revoked binary as the current TCB. Precedent: RV4-H2 and RV6-H2 were HIGH.
- **Not CRITICAL:** machines whose store holds the negative refuse. Running machines that are delivered the revocation statement
  refuse (`17` S5).

### Class

Remainder of **BC6-2** (first-contact currency) applied to negative facts, intersecting **BC6-4**: the register names no party
that establishes listing completeness, and the calculator has no strategy for it. This is a new instance, not the replay, media,
CI or re-admission instances of RV6-H2, which are closed (CUR7 re-run byte-identical).

### Correction direction (architectural only)

- Establish the negative set at first contact first-hand, at the authority that issues it. Options:
  - the revocation authority's statements reach both source custodians first-hand, and a custodian refuses to publish a state
    code while a revocation it holds is unlisted; or
  - the sources publish a revocation code set as a selector the admitter requires; or
  - a compiled maximum listing delay, with the custodians checking it against the revocation authority's issued sequence.
- Apply every verified revocation statement held, in both executors.
- Register: name the establishing party of listing completeness (DR-18, the `revocation_statements` and `revocations` rows).
- Calculator: add the omission strategy (G_REVOKED for FA, RA_unheld, P2, CIR). Restate CUR-R1, CP-REVOKED, INV7-AGE, `24` §6
  and `35` §7 from the output.

---

## RV7-B-H2 — HIGH — C3 currency names a state of unbounded age

### Statement

1. The admission path bounds the selected state's own age: FC-9 refuses a Trust State whose `issued_at` is more than 24 hours
   before the admission clock. This is how revision 7 closed RV6-H2's stored, replayed and designated values.
2. The running path does not:
   - `24` §4.4 R-CUR-1 (P1) requires "a pin provisioning or human confirmation whose two state codes name *n* itself is no
     older than 24 hours".
   - R-CUR-2 (P2) requires "two identical state codes equal to *n*'s code", with clock "none".
   - Neither reads *n*'s `issued_at`. `25` AP-3 (running) repeats this.
   - Code: `gov_run` decides C3 from `names_effective_state` and `now − currency_at ≤ 24 h`; it has no input for the named
     state's age.
3. The typed or pinned codes are values a human or provisioning automation supplies. `gov` can check only that the two values
   are identical and name the effective state. A code stored from an earlier reading (a runbook, a pin template, CI provisioning
   that re-stamps `provisioned_at`, a cached page) names an old state. When the transport withholds newer states, that old state
   is the effective state, so the proof is accepted and shown as "state published as of *now*".
4. The pack states the opposite:
   - `24` §6: "Replayed first-contact **or anchoring codes** older than 24 hours | refused (`32` FC-9; **R-CUR-1**)".
   - `24` §10 RS-1b: "can be stale by up to 24 hours".
   - `24` §5.2: CI C3 "only within 24 hours of provisioning".
   - `28` A-R7-08: "A human confirmation naming an old state while the sources publish a newer one | no C3: currency is the state
     both sources publish | BA11r7".
5. BA11r7 does not establish A-R7-08. It hard-codes `sources_latest = "t11"` (the state the sources publish now) and allows C3
   only when the effective state equals it (`c3 = oracle_c3 and eff["d"] == sources_latest`). That encodes an operator who
   always types what the sources show now. It is an assumption, not a mechanism.

### Evidence

- **executed** `outputs/RV7-B-A02.json` part E (reference executor unmodified).

  | Row | Result |
  |---|---|
  | Workstation, R7 admitted 2026-08-01, T9 (revoking R7) withheld; the operator types stored T7 codes (T7 issued 2026-05-01) today; `gov_run` C3 | `ALLOWED` |
  | The same code pair at `gov-admit` (FC-9) | `FIRST_CONTACT_STATE_TOO_OLD` |
  | CI runner: image admitted 6 days ago; pin re-stamped today naming the image-build state; C3 | `ALLOWED` |
  | Control: the same pin as provisioned 6 days ago | `TRUST_STATE_CURRENCY_UNPROVEN` |
  | Control: currency 25 h old | `TRUST_STATE_CURRENCY_UNPROVEN` |
  | Control: T9's negative held | `BINARY_REVOKED_SELF` |
  | `gov_run` has an input for the named state's `issued_at` | no |

- **computed** `outputs/RV7-B-A02.json` part C: BA11r7 is re-evaluated with the typed codes naming the machine's effective state,
  nothing else changed. `no_C3_on_a_state_below_t9` flips to false (row `M1s|OP-7 (a)|A5-strip`). The committed run shows 0 such
  rows only because of the assumption.
- **computed** `outputs/RV7-B-CS7.json` (A02): for victim P2 (in-gate codes), G_REVOKED gains the minimal set
  **{transport, stored_old}**. With a compiled 24-hour state age at C3 (A02-FIX), the set disappears. The pack computes
  G_REVOKED for FA, RA_held and RA_unheld only; P1, P2 and CIR are not computed.

### Failure scenario

- **Workstation.** An engineer's machine was anchored at T5. A proxy or mirror withholds T9 (which revokes R7) and later states.
  Following a team runbook that pasted "the current state codes" in May, the engineer types those codes into the `update` trust
  gate. The in-gate proof names T7, the effective state. `update --apply` installs R7, revoked since T9, and the gate shows "state
  published as of <today>".
- **CI.** Image provisioning writes the pin from codes read at image build and refreshes `provisioned_at` on every job start.
  For the 7-day life of the image, every job has C3 on the image-build state, while OP-7 (a) allows production installation only
  on currency of at most 24 hours.

### Why HIGH

- A lower-trust input (a stored or re-stamped code, rank 5) yields a current higher-trust fact (C3 currency "as of now"). A
  revoked binary is then installed or updated on a running machine that never received the revocation.
- OP-7 (a): "no stale/unanchored state may be presented as current". The admission path treats the same input as an attack and
  bounds it by age; the running path does not.
- Review r6's unavoidable-core table classifies "a stored or replayed value of unbounded age selects the state" as **not core**,
  because a compiled maximum age bounds it. RV6-H2 (HIGH) was this shape at first contact. The r6 synthesis RS-4 determination
  states that TA-9 scoping "does not cover an honest image operator storing an old code".
- **Not CRITICAL:** it needs withheld newer states and a stored code, and a machine holding the negative refuses (GB-3′).

### Class

Remainder of **BC6-2** (currency), running-machine instance. Its false consequence statements (`24` §6, RS-1b, A-R7-08) are the
BC6-4 shape.

### Correction direction (architectural only)

- Every C3 currency proof (P1 pin or confirmation, P2 in-gate) also requires the named Trust State's `issued_at` to be at most
  the compiled 24 hours before the decision clock, under R-CLK-1, exactly as FC-9 does at admission. The architecture already
  requires states within 24 hours of every admission.
- Restate `24` §4.4, §5.2, §6 and §10 (RS-1b, RS-1c), `25` AP-3 and A-R7-08.
- Compute G_REVOKED for P1, P2 and CIR with a stored-code atom. Replace BA11r7's `sources_latest` assumption with the rule.

---

## RV7-B-M1 — MEDIUM — One onboarding record designates both sources; the stated first-contact root omits the one-input set

### Statement

- `32` R-FCD-2: "Operators receive **the two source identities** and the procedure at onboarding, from **the organisation's copy
  of the root ceremony record**". `06` §2 step 1 and `01` TA-5′ repeat this. Register PI-01 and DR-38 name that one record as the
  establishing party.
- The operator cannot authenticate the copy. The procedure uses the platform hash tool only (TA-1b); the FCA's `sources` field
  is inside the record the look-alike sources serve (FC-2′ compares digests the operator read from those same sources).
- CS7 models designation as two independent atoms, `desig1` and `desig2` (`seen(C, i)`), and declares the first-contact root as
  pairs only (`declared_fc_root`).
- Contradicted statements, which present OP-13 (b) as requiring two independent compromises with no key:
  - CP-FC-ROOT (`32` §9, `21` §4), FC-R1′ and FC-R3′ ("exactly the eight sets"), `35` §7, `31` AD-1″;
  - INV7-FC;
  - D-0008 rule (25).

  One altered onboarding copy (an internal wiki page, an onboarding e-mail, a shared drive document) that names two look-alike
  sources satisfies `desig1` and `desig2` at once.

### Evidence

- **computed** `outputs/RV7-B-CS7.json` (A03). Adding the atom `onboard` ⇒ `desig1 ∧ desig2` makes **{onboard}** a minimal set for
  FA under G_BYTES and G_REVOKED. The control without the atom reproduces the committed CP-FC-ROOT exactly.
- **executed** (architect, re-run byte-identical): FA7 S2 D `both_pages_attacker_substituted_evaluator (stated first-contact root:
  desig1+desig2)` → `ACCEPTED_BY_SUBSTITUTED_EVALUATOR`. Both look-alike pages come from the one record in this construction.
- **design** as above. No rule requires the two identities to reach an operator through independent channels.

### Failure scenario

A new engineer is onboarded from the organisation's copy of the ceremony record on the internal documentation site. An attacker
with edit rights to that page replaces both locators with look-alike hosts that serve a self-consistent FCA, state code, procedure
digest and substituted `gov-admit`. FC-1′…FC-3′ pass. The substituted evaluator installs the attacker's `gov`. No source, custodian
or key was touched. The owner was told that one compromised channel yields `FIRST_CONTACT_DISAGREEMENT`.

### Why MEDIUM, and why not carriable

- The designation input was accepted as core by review r6 when delivered out of band (r6 synthesis unavoidable-core table).
  Revision 7 delivers it out of band, so this is not HIGH.
- The owner ratifies OP-13 (b) against a stated consequence that is false: the bound of FC-R1′ is not exact (R-2 (b)).
- Correcting it needs one of two architecture text changes:
  - restate the first-contact root with a single designation atom from the calculator; or
  - add a rule that the two identities are delivered through independent channels, each an atom.

  Neither is an implementation test, so under HO-0020 §4 this MEDIUM is blocking. The synthesis may rule otherwise.

### Class

Remainder of **BC6-1** (designation) intersecting **BC6-4** (consequence statements derived from an atom model the register does
not support).

---

## LOW

| ID | Statement | Evidence | Carried as |
|---|---|---|---|
| **RV7-B-L1** | `independent_classes` counts two registry entries as independent when all four provenance strings differ and checksum-key sets are disjoint. The strings are free text (`maxLength` 256). `sup-A2` naming the same upstream as `sup-A` under other spellings (`debian-12-official-images`, `cdn-fastly.deb.debian.org`, `buildd.debian.org`, `debian-archive-keyring-2023`) with a second key of that upstream counts as a second class, and the reproductions are `ACCEPTED`. `33` §2 (4) says "never from labels"; OP-16 says "A different label naming the same upstream/provenance chain is NOT independent". The establishing party is the root threshold (`05` §7 rule 9) and the residual `env_common` is stated (TB-S2″), so no lower-trust input selects. | executed `outputs/RV7-B-A04-A05.json` A04 (controls: identical strings and a shared key → `ENVIRONMENT_DIVERSITY_NOT_MET`) | CR7-B-01 |
| **RV7-B-L2** | `trust-root.schema.json` constrains `root`, `trust-state`, `revocation`, `release-registration`, `reproducer`, `release-final` and `certification-status`, but `trust-policy` and `first-contact-authority` are a plain `$ref purpose` (threshold ≥ 1, any keys). A root granting both at threshold 1 on a non-root key validates. Compiled `root_conforms` refuses (`threshold(trust-policy)`). OP-1: "no single custodian can exercise root authority". | executed `outputs/RV7-B-A04-A05.json` A05 (jsonschema Draft 2020-12; the committed rev7 example validates with 0 errors) | CR7-B-02 |
| **RV7-B-L3** | `custodian_publish` with no last-published state (a new custodian, or a source rotated per `05` §9) publishes T11d, which drops the published R7 revocations. With one source rotated, the other refuses and first contact fails closed (`FIRST_CONTACT_DISAGREEMENT`). With both, the drop check is empty. Two trust-state keys are still needed. | executed `outputs/RV7-B-A01.json` `custodian_with_no_publication_history_publishes_T11d` → published | CR7-B-03 |
| **RV7-B-L4** | FC-9 needs a Trust State issued within 24 hours of every admission, so the 2-of-3 trust-state custodians (hardware-backed, OP-4) and both source custodians (first-hand, R-FCS-2) must issue and publish at least daily. No rule states that cadence or its surface. `35` OT-1a mentions "a Trust State re-issued at least daily" only for media. Missing a day makes first contact, CI image builds and re-admission refuse everywhere (fail closed). | design (text search: no cadence rule in the pack) | CR7-B-04 |
| **RV7-B-L5** | A re-run against the committed pack differs from two committed outputs; no verdict leaf differs. (1) `evidence/r7/retained/DA07r6-plan-regression-detection.on-revision-7-plan.json`: `RV5-L8 plan_rows` gains RT-201, and `plan_rt_rows` goes from 199 to 202. (2) `evidence/r7/r6-probes/RV6-B-A03.json`: S2 `sets_checked` goes from 7 to 11. The committed `run_r7_evidence.sh` is not self-contained: `crashmig7` needs reviewer C's built trees (`c6lib` absent), and its empty output makes `REGISTER-CHECK`, `DA09r7` and `DA04r7` crash; `make_rev7.py`, copied to `$O/examples`, cannot find `../../schemas`. Run in place and with the committed `crashmig7.json`, the four reproduce the logged digests. | executed `evidence/rerun/COMPARISON.json`, `rerun/architect-runner-log.tsv`, `rerun/dependent-rerun-log.tsv` | CR7-B-05 |

| **RV7-B-L6** | `32` R-FCS-1: a custodian publishes a trust code only for an FCA "it verified itself … using its own admitted binary". Admission (`31` R-ADM-2″/3″, `32` FC-1′…FC-10) needs identical trust and state codes from both sources, and those codes exist only after both custodians publish. At lineage genesis, and for a custodian on a new machine while the other source has not yet published, the verifier the rule requires cannot exist. No text (`06` §2, `05` §7, `32` §5) names the genesis procedure: which binary a custodian uses and how that binary is established (for example, the custodian's own build of the registered admitter source checked against the root ceremony's admitter evidence). The first-contact root then inherits an unspecified tool, the same shape as RV6-L4 (derivation-tool provenance). | design (text search: no genesis rule) | CR7-B-07 |

## INFO

| ID | Statement |
|---|---|
| RV7-B-I1 | AP-5 counts two ACCEPTED attestations with distinct key ids, `verifier_execution_id` values and `verification_report_digest` values. The ids and digests are self-asserted, so one verifier holding two `verification-attestation` keys satisfies the check. OP-8's "genuinely separate verifier executions/evidence" rests on key custody (TA-11; `30` R-REG-3 (d) "received first-hand from two independent verifiers"; R-VER-4). This is stated as TB-4′. |
| RV7-B-I2 | ARCH-0002 has `status: PROVISIONAL`, `proposal_state: PROPOSED` and `in_effect: false`, and no `human_approved` field. D-0008 has `status: PROVISIONAL`, `proposal_state: PROPOSED`, `human_approved: false`, `in_effect: false` and no `chosen_option`. D-0007 is `ACTIVE`. HO-0020 §2b's state requirements hold. |
