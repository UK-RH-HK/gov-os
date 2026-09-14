# Output 24 — Anchoring, currency and new-machine trust bootstrap (CP-1: OP-7 (a) anchored only)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 7** concretises this file to the certified profile CP-1 (`35`) and the owner selection OP-7 (a) "anchored only"
> (OWNER-DESIGN-REQUIREMENTS-0001): workstation anchors at most 90 days, CI anchors at most 7 days, production installation,
> update and rollback need currency of at most 24 hours, expiry leaves C0, and the high-water never moves backwards.
> Removed from the certified profile (history at `4106885`): the witness purpose and its acceptance (EX-01), the unanchored
> modes (EX-07, EX-08), the maximum-age mode and its parameters (EX-12), and the decision rows of those modes. Added: the
> state code read from both first-contact sources as the anchoring and currency value (§3.1); the clock rule **R-CLK-1** (§4.5);
> the two stores (§8). Residual RS-5 is removed by exclusion.
> Revisions 3–6 built the inclusion anchors, bounded pins, currency proofs naming the Trust State they cover, the stateful clock
> high-water and pin integrity that this file keeps. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Revision 2.** The mistaken equivalence was *compiled or repository knowledge ⇒ current state*.

**Revision 3.** Anchors were added; review r3 found *an anchor number is met ⇒ the anchored state is in force* and *anchored once
⇒ current* (RV3-H2).

**Revisions 4–6** removed those inputs from the decision: inclusion anchors (§3.4), bounded pins (§3.2), currency separate from
anchoring (§4.4), no `current` label (§4.1), pin integrity (§3.5), and a stateful clock high-water (§8).

**Revision 7** keeps all of that for one mode. The owner states the unavoidable core: *a machine that has never received newer
metadata cannot be claimed to know it*. CP-1 therefore:
1. runs no governed operation on an unanchored machine or past an anchor's validity;
2. requires currency of at most 24 hours, naming the effective Trust State, for every trust transition;
3. takes the anchoring and currency value from both first-contact sources, which publish only states they verified first-hand
   (`32` R-FCS-2), never from the trust-state publisher alone;
4. refuses every governed operation when the clock is below what the machine has already recorded.

## 2. Safety, anchoring and currency

| Property | Holds without an anchor? | Holds with a satisfied anchor? | Needs a currency proof? | Mechanism |
|---|---|---|---|---|
| Authenticity of every statement and release | yes | yes | no | compiled root chain, purposes (`05`) |
| Integrity of installed and enforced bytes | yes | yes | no | `18` |
| Eligibility against the knowledge held | yes | yes | no | `19` §6 |
| Effective floors ≥ max(compiled TPS, held TPS), joined over the Constitutional Surface | yes | yes | no | `19` §5, `23` |
| Held negative facts stay effective; absence is never positive | yes | yes | no | `17` MS-1, MS-2 |
| Equivocation and fork detection among held statements | yes | yes | no | `17` S3, S4 |
| Trust decisions never authorised by repository records | yes | yes | no | `27` |
| **The effective state descends from the published state as of the anchor time** | no | **yes** (inclusion, §3.4) | no | §3 |
| **No revocation, floor raise or root rotation published after the anchor applies** | no | **no** | **yes**, and only as of the proof time (≤ 24 hours) | §4.4 |

An attacker who controls the transport or the repository can choose which genuine statements a machine sees, down to the
machine's anchored chain. It can never make the machine present a state as current, and never make a statement that does not
descend from the anchor effective.

## 3. Anchors

An **anchor** is a local record that at time *t* the published trust state of lineage *L* included the Trust State Statement
`(e, d_e)`. It is established by a source independent of the repository writer (A2), the source controller (A1) and the
transport (A5).

### 3.1 State code (revision 7)

The anchoring value is the **state code** `gov-fcs:<8 hex of lineage id>:<sequence>:<64 hex digest of the Trust State>`
(`32` §4), read from **both** first-contact sources. The two codes MUST be identical (`TRUST_GATE_STATE_CODES_DISAGREE`
otherwise). Each source publishes a state code only for a Trust State it verified at the trust-state threshold, descending from
the last one it published and dropping nothing (`32` R-FCS-2). The revision-6 state fingerprint (`gov-state:`) is withdrawn.

### 3.2 Anchoring events

| Event | How | Currency it carries | Trust assumption |
|---|---|---|---|
| **Pin** | `trust-state-pin` v3 (`schemas/trust-state-pin.schema.json`: `machine_class` `workstation` or `ci`, `state_code`, `provisioned_at`, `valid_until`) in the system pin directory (§3.5). `valid_until − provisioned_at` ≤ 90 days (workstation) or ≤ 7 days (CI). A pin outside `[provisioned_at, valid_until]` is **not an anchor** (`PIN_OUTSIDE_VALIDITY`). | a currency proof for C3 only within 24 hours of `provisioned_at`, and only for the Trust State it names | TA-9 (§3.5); TA-7 |
| **Human confirmation** | `gov trust confirm-state <state code> <state code>`, the code typed from each source; `gov` never supplies the value. If the confirmed statement is not held, the anchor is recorded and the machine is `BELOW_ANCHOR` until it is supplied. The first confirmation of a verifier trust store also confirms the lineage (OP-6 (a)). | a currency proof for C3 within 24 hours of `confirmed_at`, for the Trust State it names | TA-5′; TA-7 for the window |
| **In-gate state confirmation** | the trust-gate confirmation of a C3 transition (`27` §3.1) carries the two state codes currently published by the sources (`trust-gate-confirmation` v3 `state_codes`); they must name the effective Trust State | a currency proof **for that transition only**, with no clock | TA-5′ |
| **Retained** | an anchor recorded earlier in this store; later verified statements raise the held state monotonically | none (safety floor only); it is an anchor only within the validity of the event that made it (90 days, CI 7 days) | the stores survive (RS-3) |

**Pin anchors are recomputed from the pin file in every process.** They are never persisted as retained anchors, so a pin cannot
outlive its validity through the store.

### 3.3 Witness authority — removed by exclusion

The witness purpose, statement and acceptance path of revisions 4–6 are not part of CP-1 (EX-01; owner text: "No witness service
in the initial certified profile because OP-7 is anchored-only"). A root granting the purpose is refused
(`PROFILE_NONCONFORMANT`); an offered witness statement is refused (`PROFILE_MODE_EXCLUDED`).

### 3.4 Anchor satisfaction (normative; unchanged)

For a set of anchors *A* (valid pins, human confirmations, in-gate confirmations, retained anchors within validity), let *H* be
the resolved Trust State Statements the machine holds:

1. *A* is **satisfied** by TSS *T* ∈ *H* iff, for every `(e, d) ∈ A`:
   - `(e, d)` is held in *H*; and
   - `(e, d) = (T.sequence, digest(T))` or `(e, d) ∈ T.prior_states`.
2. **Candidates** are the TSSs in *H* that satisfy *A*. Admissibility (`17` S4 (d)) runs over the candidates together with the
   ancestors in the top anchor's chain. The effective TSS is the highest admissible candidate.
3. If there is no candidate, freshness is `BELOW_ANCHOR`. No operation above C0 runs.
4. Resolved TSSs outside the anchored chain are **orphans** (at or below the top anchor; reported, never effective) or
   **unchained above the anchor** (never effective; with a candidate they make the trust state `REGRESSION`, C0).
5. Two anchors neither of whose statements chains the other → `ANCHOR_CONFLICT` (C0).

### 3.5 Anchor and decision-pin integrity (unchanged)

1. **Pin locations** are resolved from the OS, never from `HOME`, `XDG_*`, `GOV_*` or the repository: `/etc/gov/` on Linux,
   `/Library/Application Support/gov/` on macOS, `%ProgramData%\gov\` on Windows. Account-location pins are not honoured for
   anchoring (`31` GB-4′).
2. **Integrity predicate.** A pin file or decision pin file is honoured only if neither it nor any ancestor directory is writable
   by the effective uid (on Windows, the equivalent ACL check), or it is on a read-only mount. Otherwise the pin yields
   `PIN_WRITABLE_IGNORED` and a decision pin authorises nothing (`TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED`). An effective uid of
   0 treats every path as writable (`31` GB-6).
3. **Confined execution.** Every repository-supplied or plugin-supplied command that `gov` executes MUST run under OS write
   confinement. The confinement is an allow list: writes are permitted only to the project working tree outside the Protected
   Path Set, the command's own temporary directory and the paths its registered descriptor names. It denies writes to the system
   pin locations, both stores (§8), `governance/trust/**`, the occupation entries and the transaction area. Mechanisms: Linux
   Landlock (ABI ≥ 1) or a mount namespace; a macOS sandbox profile; a Windows restricted token or AppContainer. Where
   confinement is unavailable, `gov` refuses to run the command (`REPOSITORY_COMMAND_CONFINEMENT_UNAVAILABLE`). Every trust
   decision of a unit of work is made before any such child starts.
4. **TA-9.** Pins and decision pins are provisioned by an operator whom the repository writer does not control, and no process
   the repository writer controls runs, before `gov`'s trust decision, with an identity that can write the pin location. On CI
   this means a root-owned `/etc/gov` in the runner image and jobs that run as another user (RS-4).
5. **The rule of `27` §3.3** covers `gov decide` and every `gov`-executed child. An agent with an unconfined shell in the same
   account is A3 (RS-3, TG-2).

### 3.6 Not anchors

The repository (PTR, lock hints, gate records), bundles, `gov trust refresh` input, environment variables and CLI flags, CI
configuration committed to the repository, the compiled T0, a store record of a pin, and any value printed by an unadmitted
binary are never anchors. The compiled T0 is a safety floor and never grants governed use (EX-07).

## 4. Verdict axes, operation classes and the decision rule

### 4.1 Axes

| Axis | Values |
|---|---|
| `trust_state` (`17` S9) | `KNOWN(n)` · `INCOMPLETE(n′)` · `REGRESSION` · `EQUIVOCATION` |
| `freshness` | `ANCHORED(e, method, as-of t, age, valid until)` · `ANCHOR_EXPIRED(e, age)` · `BELOW_ANCHOR` · `UNANCHORED(held n)` · `ANCHOR_CONFLICT` · `CLOCK_BELOW_HIGH_WATER` |
| `currency` | `CURRENCY(proof, established t)` · `CURRENCY_UNPROVEN(age of the last proof)` |

- Every surface (`gov status`, `gov kernel trust`, context packets, doctor D032/D035, gate text) MUST show all three axes.
- **The word `current` MUST NOT appear on any surface.** A proof is shown as "state published as of *t*".
- The OP-5 age warning (30 days) is shown with the anchor age. It is informational and read by no decision.

### 4.2 Operation classes (compiled command register)

| Class | Commands (examples) |
|---|---|
| **C0-R** read-only diagnostics | `version`, `doctor`, `status`, `kernel trust` report, `trust show` |
| **C0** diagnostics and knowledge intake | C0-R, `kernel verify`, `trust refresh --from`, `trust confirm-root` / `confirm-state`, trust-gate confirmation (`27`); anchoring ceremonies are refused on a user-writable installation (`31` GB-4′) |
| **C1** governed read | `context compile`, `memory query`, `continue`, readiness views |
| **C2** governed mutation | tasks, CIT, non-trust gates, `rebuild-memory`, `plugins register`, `tools install`, adoption batches ≥ 1, `upstream`, checkpoints |
| **C3** trust ingress | `init`, `adopt migrate --batch 0`, `update --apply`, rollback and restore, `kernel reinstall` with another envelope, recovery exchange, `trust verify-artifact` acceptance, profile install, lineage adoption |

### 4.3 Decision rule (one rule; the most restrictive applicable row wins)

| Condition | C0-R | C0 | C1 | C2 | C3 |
|---|---|---|---|---|---|
| the clock is below the machine's recorded high-water (R-CLK-1) | yes | no | no | no | no |
| the running binary is revoked in held state (OP-15 (a), `31` GB-3′) | yes | no | no | no | no |
| `EQUIVOCATION`, `REGRESSION`, `BELOW_ANCHOR`, `ANCHOR_CONFLICT` | yes | yes | no | no | no |
| `INCOMPLETE` | yes | yes | yes | **no** | no |
| `UNANCHORED` (R-ANC-1) | yes | yes | no | no | no |
| `ANCHOR_EXPIRED`: the latest anchoring event older than 90 days on a workstation or 7 days on CI (R-ANC-2, R-ANC-3, R-ANC-5) | yes | yes | no | no | no |
| `ANCHORED`, `KNOWN`, within validity | yes | yes | yes | yes | **only with a currency proof of at most 24 hours naming the effective state** (R-ANC-4) |

| ID | Rule | Refusal |
|---|---|---|
| **R-ANC-1** | A machine without an honoured anchor runs C0 only. No compiled epoch, clock or repository record substitutes (EX-07, EX-08). | `TRUST_STATE_UNANCHORED` |
| **R-ANC-2** | A workstation anchor (pin, confirmation or retained anchor) is valid for at most 90 days from the anchoring event. | `TRUST_ANCHOR_EXPIRED` |
| **R-ANC-3** | A CI anchor (image pin or record) is valid for at most 7 days from provisioning. | `TRUST_ANCHOR_EXPIRED` / `PIN_OUTSIDE_VALIDITY` |
| **R-ANC-4** | C3 (production installation, update, rollback, recovery, ingress, binary acceptance) needs a currency proof (§4.4) of at most 24 hours naming the effective Trust State. | `TRUST_STATE_CURRENCY_UNPROVEN` |
| **R-ANC-5** | After the applicable anchor expires, governed mutation degrades to C0 until re-anchored; no stale or unanchored state is presented as current. | `TRUST_ANCHOR_EXPIRED` |
| **R-CLK-1** | A clock earlier than the machine's recorded high-water (§4.5) leaves C0-R only. | `TRUST_CLOCK_BELOW_HIGH_WATER` |

The ceilings are compiled; the Trust Policy's `bootstrap.admission_ceilings` may only lower them (schema maxima 90, 7, 24, 24).
Each refusal carries `required`, `held` and `remedy` (refresh, confirm-state from both sources, re-provision the pin,
re-admit, or correct the clock).

### 4.4 Currency proof (normative)

A **currency proof** for effective TSS *n* exists iff the machine is `KNOWN` and `ANCHORED` within validity, the clock passes
R-CLK-1, and one of these holds:

| ID | Proof | Condition | Clock |
|---|---|---|---|
| **R-CUR-1** | (P1) recent anchoring event naming *n* | a pin provisioning or human confirmation whose two state codes name *n* itself is no older than 24 hours; an event naming an ancestor of *n* is not a proof for *n* | TA-7 |
| **R-CUR-2** | (P2) in-gate confirmation | the trust-gate confirmation for this transition carries two identical state codes equal to *n*'s code | none |

A proof establishes that *n* was the state both sources published **as of** the proof time. It is used for exactly one C3
decision (P2), or within the window (P1). It is never displayed as `current`. The witness proof of revisions 4–6 is excluded
(EX-01).

### 4.5 Clock rule R-CLK-1 (revision 7)

The **recorded high-water** of a machine is the maximum of:
- `clock_high_water` of both stores (§8), raised by every verified non-future statement ingested and by every admission;
- the `admitted_at` of the admission record of the running binary;
- the time of the anchoring event and of the currency proof in use.

If that maximum exceeds the local clock by more than the compiled skew (300 seconds), the clock is wrong. Every age, validity
and window computed from it is meaningless, so only C0-R runs (`TRUST_CLOCK_BELOW_HIGH_WATER`). A statement of any purpose
whose `issued_at` exceeds the local clock by more than the skew is refused at ingest (`STATEMENT_ISSUED_IN_FUTURE`) and never
recorded. A root-signed Trust Policy `bootstrap.clock_reset {reset_to, reason}` lowers the high-water after a wrong future clock
raised it. Evidence: ADM7 `CLK_clock_below_high_water` (executed, with the revision-6 reading as a mutant); BA11r7 (the
revision-6 oracle's CLOCK-back rows admitting a revoked release are removed by the rule).

## 5. The machine list (HO-0001 §3.2), CP-1 parameters

"Store" means both stores of §8. Evidence ids refer to `evidence/r7/BA11r7-machine-classes.json` (the retained P4r4/P4r5/P4r6
model with the CP-1 parameters and rules), ADM7 and CUR7.

### 5.1 First install (M1)

- **Starting state.** No store.
- **Before admission.** C0-R only: the candidate is never run; `gov-admit` performs the first-contact procedure (`32`).
- **After admission.** The admitted binary runs C0. The operator confirms the lineage once (OP-6 (a)) and the state code from both
  sources: the machine is `ANCHORED` with a currency proof (P1) for 24 hours, and `init` proceeds through its trust gate.
- **If the source withholds the confirmed TSS** or supplies statements that do not chain through it: `BELOW_ANCHOR`.
- **Persisted.** Lineage confirmation, the anchor, verified statements, the per-project record, `clock_high_water`.

### 5.2 Clean CI runner (M2)

- **Starting state.** A runner image built by `gov-admit` within 24 hours of the state it admitted; a root-owned admission record
  and a CI pin, each valid for at most 7 days; jobs run as another user.
- **Behaviour.**

  | Condition | Result |
  |---|---|
  | valid pin, intact repository | `ANCHORED`; C1–C2; C3 only within 24 hours of provisioning, for the Trust State the pin names |
  | valid pin, stripped repository | `BELOW_ANCHOR` |
  | pin or record older than 7 days | not an anchor: `PIN_OUTSIDE_VALIDITY` / `ADMISSION_RECORD_EXPIRED`; C0 |
  | pin writable by the job's uid | ignored (`PIN_WRITABLE_IGNORED`) |

- **Evidence.** BA11r7 `M2-pin*`; ADM7 X14.

### 5.3 Machine restored from backup (M3)

- **Starting state.** A store rolled back to an anchor 400 days old.
- **Result.** The anchor is past its 90-day validity: C0 (R-ANC-5). Remedy: confirm the state code from both sources (P1), or
  re-admit if the record expired.
- **Clock.** If the clock is set back into the restored anchor's validity and any later statement is delivered, it is refused as
  future and clock-based proofs are unusable; with R-CLK-1, a clock below the restored store's high-water leaves C0-R. If the
  clock is set back and **every** later statement is withheld, the machine cannot distinguish the past: residual RS-2b (§10).

### 5.4 Old trust epoch (M4)

Anchored 20 days ago at t5: the effective state is never below t5; C1–C2 run at the anchored chain; C3 refuses without a
currency proof of at most 24 hours.

### 5.5 No trust epoch (M5)

`UNANCHORED`: C0 only (R-ANC-1).

### 5.6 Two machines at different epochs (M6)

Each machine enforces its own anchor by inclusion; B learns t10 when a carrier delivers it, because t10 chains through B's anchor;
A never accepts a statement that does not descend from t10; lock hints are warnings.

### 5.7 Offline machine after a long absence (M7)

Anchored 1095 days ago: past validity, C0. There is no mode in which an old anchor keeps governed use (EX-12). Re-anchoring needs
both sources.

## 6. Replay, equivocation, forks and incomplete state

| Case | Rule | Evidence |
|---|---|---|
| Replay of genuine older TSS or TPS | knowledge is a union; replay lowers nothing | P4r4 `R1_signed_state_replay` |
| Replayed first-contact or anchoring codes older than 24 hours | refused (`32` FC-9; R-CUR-1) | CUR7 R |
| Same-sequence fork | `EQUIVOCATION`, C0 | P4r4 `B3_same_sequence_fork` |
| Fork across a gap | cumulative `prior_states[]`; `REGRESSION` | P4r4 `E1_fork_across_a_gap` |
| Higher TSS that does not chain through the anchor | not a candidate | P4r4 `RV3-B-A12_RV3-D-A12_higher_unchained_tss` |
| Pin names a digest the effective chain does not contain | `BELOW_ANCHOR` | P4r4 `R5_pin_digest_mismatch` |
| TSS referencing an unknown root or policy | `INCOMPLETE` (C0–C1) | P4r4 `B4_unresolvable_references` |

**Trust-state key blast radius.** Two trust-state keys (the threshold) can sign a descendant. On an anchored machine a descendant
that omits a held revocation is non-admissible (`REGRESSION`). The sources do not publish a descendant that drops a revocation
they published (`32` R-FCS-2), so such a descendant never carries both state codes. A descendant on a machine that never held the
revocation admits what withholding already admits: RS-1. One trust-state key signs nothing (KS-17; BA12r7).

## 7. Gate records supplied from repository state

Unchanged. A repository gate record never authorises a trust decision (`27`).

## 8. Monotonic local state: two stores (R-STORE-1)

| Store | Location, owner | Holds | Written by |
|---|---|---|---|
| **Protected admission store** | per platform, root- or administrator-owned (`/var/lib/gov/admission/<64-hex lineage>/` on Linux); outside every governed account's write reach | `admission-store.json` (first-admission marker), `admissions/<binary digest>.json` (records v3), `floors.json` (state sequence and digest, root version, policy version, `fca_sequence`, negatives, security minimum, `accepted_tbm`, `clock_high_water`) | `gov-admit` only, under an exclusive lock (`31` R-ADM-13) |
| **Account verifier trust store** | `<account-home>/.local/state/gov/trust/<64-hex lineage>/`, resolved from the account database | `statements/`, `high-water.json` (the floors above, raised by ingest), `anchors.json`, `lineage.json` (OP-6 (a)), `projects/<project_trust_id>.json`, `confirmations/` | the admitted `gov` |

- **Restrictors only.** Floors are merged from both stores as maxima and unions; a planted higher floor can only refuse.
- **Never backwards.** No component decreases, except `clock_high_water` by a root-signed `clock_reset` and `accepted_tbm` by a
  root-signed `accepted_tbm_reset`.
- **First admission** is decided only by the protected store's marker; it moves the account store for the lineage aside
  (`31` R-ADM-8″, R-STORE-2). Re-admission keeps both.
- **Pin anchors are not stored.** A3 can delete or rewrite its own account store (RS-3); it cannot write the protected store.

## 9. OP-7 (a) — selected

Architecture minima: inclusion anchors (§3.4); no C3 or binary acceptance without a currency proof (§4.4); mandatory pin validity
(§3.2); pin and decision-pin integrity with confined execution (§3.5); no `current` label (§4.1); R-CLK-1 (§4.5).

| Parameter | CP-1 value | Encoded |
|---|---|---|
| workstation anchor validity | 90 days | compiled `ANCHOR_VALIDITY`; TPS `bootstrap.admission_ceilings.workstation_anchor_days` ≤ 90 |
| CI anchor validity | 7 days | compiled; `ci_anchor_days` ≤ 7 |
| production currency | 24 hours | compiled `C3_CURRENCY`; `production_currency_hours` ≤ 24 |
| admission state age | 24 hours | compiled `ADMISSION_STATE_MAX_AGE`; `admission_state_hours` ≤ 24 |
| clock skew | 300 seconds | compiled |

The revision-6 answers (b) maximum anchor age as a mode, (c) expiring witnesses and (d) compiled epoch accepted for use are
non-production history (`21` §9); they are excluded (EX-12, EX-01, EX-07, EX-08) and their parameters are absent from the schema.

## 10. Residuals, restated for CP-1

| ID | Residual | Bound | Test that fails if exceeded |
|---|---|---|---|
| RS-1 | **Core (owner text).** A machine anchored before a revocation that never receives later metadata cannot know about it. | C1–C2 at any genuine descendant of its anchor, within the anchor's validity (90 days; CI 7 days); shown `ANCHORED(e, method, as-of t, age) CURRENCY_UNPROVEN`, never `current`; never C3 without a proof of at most 24 hours; C0 after expiry | RT-80, RT-101, RT-189; BA11r7 |
| RS-1b | A C3 decision whose proof is a recent anchoring event (P1) can be stale by up to 24 hours. | 24 hours; zero for an in-gate proof (P2) | RT-101, RT-102 |
| RS-1c | A valid pin provisioned before a revocation admits the stale descendant for C1–C2. | 90 days (workstation), 7 days (CI) | RT-102; BA11r7 `M2-pin*` |
| RS-2 | On a machine **without any store**, pin validity and the 24-hour window rest on the local clock (TA-7). | machines with a store fail closed below the high-water (R-CLK-1) | RT-56, RT-148, RT-189; CUR7 A08; ADM7 CLK |
| RS-2b | A store restored from backup, the clock set back into its range, and **every** statement issued after the backup withheld. | the machine behaves as of the backup, within that anchor's validity; any delivered later statement refuses C3; a 90-day anchor validity bounds it | RT-178 |
| RS-3 | A3 deletes or rewrites its own account store. | deletion leaves the machine `UNANCHORED` (fail closed); A3 cannot write the protected store or pins; `gov`-run children are confined | RT-91, RT-103 |
| RS-4 | A pin provisioned by a party the repository writer controls, or a CI job that runs repository-controlled steps as a user who can write the pin location before `gov`. | outside TA-9 (§3.5) | RT-103 (d) |
| RS-5 | (Revisions 4–6: witness key compromise.) | removed by exclusion (EX-01) | PROF7 EX-01 |
