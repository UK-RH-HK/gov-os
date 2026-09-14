# Output 27 — Authorisation of trust decisions

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 6: trust gates add `registration_change` (`34` R-CON-5). Under OP-3 mode B each certified update still needs
> a currency proof naming the publishing Trust State (`21` OP-3, RV5-L9). Confirmations need a protected installation
> (`31` GB-4′).
> Revision 5: decision-pin maximum validity and binding groups (§3.2); confinement restated as an allow list with the TCB
> location rule (§3.3). Trust gates run only on admitted binaries (`31` GB-1).
> Revision 3 added this file. Review r3 recorded R2-M1 as NARROWED to RV3-M2: repository records are requests, but pins,
> decision pins and confirmations were writable by the governed account. Revision 4 carries RV3-M2 through three changes:
> - an integrity predicate for pins and decision pins;
> - write confinement of `gov`-executed children;
> - mandatory decision-pin expiry bound to a state (CR-03).
>
> It also adds the in-gate state confirmation, a clockless currency proof (`24` §4.4). Normative keywords: MUST, MUST
> NOT, SHOULD.

## 1. The class

Revision 2 authorised trust transitions with Human Decision Gate records under `spec/decisions/`. A repository writer
could commit those records (review r2 P2). Revision 3 made trust gates local. The review of revision 3 showed that the
local automation path could still be written by processes of the governed account, including a repository command that
`gov` itself ran (RV3-B-A03 executed; RV3-B-A04 computed).

## 2. Trust gates (unchanged set)

| Kind | Raised by | Bound to |
|---|---|---|
| `init_ack` | `init`, `adopt migrate --batch 0` | statement digest, project_trust_id |
| `framework_update` | `update --apply` (OP-3 mode A always) | current and target statement digests |
| `downgrade` | rollback, restore, downgrading recovery | both statement digests |
| `weakening` | computed weakenings over effective policy (`19` §9); `overlay.prev` restore | statement digest, failure-list digest |
| `policy_lowering` | a TPS computed reduction that affects a project's held registration (`19` §10.6) | TPS digest, reduction-list digest |
| `project_strength` | `PROJECT_STRENGTH_WEAKENED` (`26` §6) | recorded and new vector digests |
| `evaluation_candidate` | evaluation-candidate installs | candidate digest |
| `override_kernel_integrity` | `kernel override` | observed kernel-state fingerprint |
| `adopt_lineage` | re-rooting | new lineage id |
| `owner_constitutional_file` | registering an owner constitutional file digest (`23` §7.2) | path and digest |

## 3. What authorises a trust gate

A trust gate is answered **only** by a **local confirmation** recorded in the Verifier Trust Store
(`confirmations/<gate kind>-<project_trust_id>-<digest prefix>.json`, schema `schemas/trust-gate-confirmation.schema.json`,
`x-schema-version` 2.0.0).

| Field | Meaning |
|---|---|
| `gate_kind`, `gate_id` | as raised |
| `project_trust_id`, `repository_path` | binds the decision to this project on this machine |
| `bound_digests[]` | exactly the digests of §2 for the kind |
| `presented_digest` | digest of the decision package `gov` rendered |
| **`state_fingerprint`** | for C3 kinds (`init_ack`, `framework_update`, `downgrade`, `evaluation_candidate`, `adopt_lineage`): the fingerprint the operator typed; it must name the effective TSS (`24` §4.4 P2) |
| `method` | `interactive_terminal` or `operator_decision_pin` |
| `confirmed_at`, `operator`, `consumed_by_transaction` | as revision 3 |

### 3.1 Interactive terminal

`gov trust confirm <gate id>`:
- opens the controlling terminal (`/dev/tty`), never standard input;
- renders the decision package, including every verdict axis, computed lists, the certification view and the currency
  axis;
- requires the operator to type:
  - the first 12 hex characters of the bound digest; and,
  - **for C3 kinds, the state fingerprint currently published in an independent channel** (`24` §3.2 in-gate
    confirmation). A fingerprint that does not name the effective TSS makes the transition refuse
    (`TRUST_STATE_CURRENCY_UNPROVEN`), and it is recorded as a human anchor. If the named TSS is not held, the machine is
    `BELOW_ANCHOR` until it is supplied;
- refuses when there is no controlling terminal (`TRUST_GATE_NEEDS_TERMINAL`).

This raises the bar for agent tool calls, which normally have no controlling terminal. It is not a boundary against a
same-user process that allocates a pseudo-terminal (TG-2).

### 3.2 Operator decision pin (automation; CR-03)

**Revision 5 (CR4-B-09, RV4-L5; RV4-L10).** A decision pin carries `provisioned_at` and `expires_at`, and
`expires_at − provisioned_at ≤` TPS `gating.decision_pin_max_validity_days`; a pin beyond it authorises nothing for every
kind (`DECISION_PIN_OUTSIDE_VALIDITY`); an increase of the parameter is a computed reduction. An
`owner_constitutional_file` pin for a binding group names the group digest; several valid pins resolve by exact set match
only (`23` §7.2). Evidence: P4r5 `GATE-CR4-B-09_decision_pin_beyond_maximum_validity`; DA03r5 mutant detected.

- **Location.** The system pin directory, or the account location only when the integrity predicate of `24` §3.5 holds:
  the file and every ancestor are not writable by the effective uid, or the file is on a read-only mount. Otherwise the
  pin authorises nothing (`TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED`, detail `DECISION_PIN_WRITABLE_IGNORED`).
- **Content** (schema `trust-decision-pin.schema.json`): `{gate_kind, bound_digests, project_trust_id or "*",
  approved_under_state {sequence, statement_digest}, provisioned_by, provisioned_at, expires_at}`.
  - **`expires_at` is mandatory.** An expired pin authorises nothing.
  - **`approved_under_state`** must be in the effective chain (inclusion, `24` §3.4). A C3 kind approved by a pin also
    needs a currency proof of `24` §4.4, P1 or P3.
- **Limit.** A pin never approves a kind listed in TPS `gating.local_terminal_only`. The default list is `downgrade`,
  `policy_lowering`, `adopt_lineage` and `override_kernel_integrity`.
- **Trust assumption.** TA-9 restated (`24` §3.5 (4)).

### 3.3 Never agent-resolvable

**Revision 5 restatement (CR4-B-01 (c); RV4-M2).** Write confinement stops **direct** writes only. `confine::spawn`
enforces an **allow list** (the repository working tree excluding `.git/`, plus a per-command temporary directory) and
explicitly denies every `PATH` directory, the running `gov` executable and its ancestors, shell and login start-up files, the
pin locations, the verifier trust store and the Protected Path Set. Code the account later runs unconfined (a planted
executable, start-up line or hook) is A3 (RS-3, TG-2). C3 operations, confirmations and decision-pin evaluation refuse when
the running executable or any ancestor is writable by the effective uid (`TCB_WRITABLE_BY_GOVERNED_ACCOUNT`, `31` GB-4).
Tests: RT-103 (allow list), RT-138 (TCB-location predicate).

A compiled rule, independent of `HUMAN_GATE_POLICY.agent_resolvable_when`:
1. `gov decide` on a trust gate returns `TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED`.
2. Every repository- or plugin-supplied command that `gov` executes runs under write confinement. It can write neither
   the VTS nor any pin location (`24` §3.5 (3)). So an agent path that runs through `gov` cannot create a confirmation or
   a decision pin.
3. An agent with an unconfined shell in the same account is A3. It can write its own VTS and drive a pseudo-terminal
   (TG-2). It cannot write protected pins.

Evidence:
- `evidence/rerun-RV3-B-A03-A14-A16-probes.json`: the real 4.1.5 `gov verify product` still writes both pin files as the
  invoking uid, mode 0644. Under the revision-4 predicate those files are ignored.
- `P4r4` `RV3-B-A03_pin_written_by_governed_account` and `RV3-B-A04_decision_pin_integrity`.

## 4. Repository gate records

Unchanged:
- The OS writes a record under `spec/decisions/` for audit (T2 evidence).
- On any other machine, or without a matching local confirmation, a record is a **request**.
- `answer.by_kind`, `presented_in_chat` and `gate_status` are never consulted for a trust decision.

Evidence: review r2 `P2` (re-run on unchanged 4.1.5 by reviewer B) and `P4r4` `R3_gate_record_from_repository`.

## 5. Non-trust governance gates (unchanged; limit stated)

Ordinary Human Decision Gates keep D-0007 semantics.
- **TA-8.** Against A2, their records remain requests.
- **Consumers.** Consumers of non-trust gates MUST require `by_kind: human`, computed by `gov` at answer time.
- **Caller-declared role (RV3-I1, INFO).** The acting role remains caller-declared (V-L5). ROLES `level_at_most` ceilings
  bind honest declarations only. No trust gate depends on the declared role.

## 6. Exceptions

A `PROJECT_EXCEPTIONS` entry never relaxes a key of class `floor`, `pinned`, `members` or `precedence`, or any key under
the compiled prefixes. For the remaining keys, effective `exception_relaxable` is the **registered** value only
(`23` §4.4). Adding an exception is a weakening against a recorded strength vector (`26` §6).

## 7. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TG-1 | A decision on one machine does not authorise another. | By design: each machine confirms or uses a protected, expiring operator pin. | RT-91 |
| TG-2 | A same-user process (A3) with an unconfined shell can write its own VTS or drive a pseudo-terminal. | Same-user boundary (RS-3). It cannot write protected pins or decision pins; `gov`-executed children are confined. | RT-103 |
| TG-3 | Non-trust gates remain forgeable by A2 as repository records. | TA-8; none changes a trust fact. | RT-89 |
