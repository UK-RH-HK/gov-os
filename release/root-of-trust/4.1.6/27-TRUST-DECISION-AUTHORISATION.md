# Output 27 — Authorisation of trust decisions

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 3. Closes R2-M1 as a class. Implements D-0008 rule (18) revision 3. Normative keywords: MUST, MUST
> NOT, SHOULD.

## 1. The class

Revision 2 authorised production installs, downgrades, computed weakenings, hint mismatches, floor-lowering acceptance and
exceptions with Human Decision Gate records under `spec/decisions/`. A repository writer can commit those records (A2).
A plugin or a same-user process can write them (A3). `gov decide` accepts a caller-declared role, and `is_answered_yes`
ignores `by_kind`.

Review evidence `P2` applied an update from an edited gate file without `gate present` or `decide`. The mistaken
equivalence was *a gate record in the repository ⇒ a human decision*.

## 2. Trust gates

A **trust gate** is a gate whose answer changes a trust fact or authorises a trust transition. The set is compiled and
independent of `HUMAN_GATE_POLICY`:

| Kind | Raised by | Bound to |
|---|---|---|
| `init_ack` | `init`, `adopt migrate --batch 0` | statement digest, project_trust_id (or its creation) |
| `framework_update` | `update --apply` (OP-3 mode A always; mode B per `17` §13) | current and target statement digests |
| `downgrade` | rollback, restore, recovery that lowers the sequence (`20` §4–§5) | both statement digests |
| `weakening` | computed overlay weakenings during migration (`19` §9); `overlay.prev` restore (`20` §5) | statement digest and the digest of the computed list |
| `policy_lowering` | a TPS computed reduction (`19` §10, `23` §7) | TPS digest and reduction-list digest |
| `project_strength` | `PROJECT_STRENGTH_WEAKENED` (`26` §6) | recorded vector digest and new vector digest |
| `evaluation_candidate` | evaluation-candidate installs | candidate digest |
| `override_kernel_integrity` | `kernel override` | observed kernel-state fingerprint |
| `adopt_lineage` | re-rooting after a threshold compromise (`06` §4) | new lineage id |
| `owner_constitutional_file` | registering an owner-supplied constitutional file digest (`23` §7.1) | file path and digest |

## 3. What authorises a trust gate

A trust gate is answered **only** by a **local confirmation** recorded in the Verifier Trust Store:
`confirmations/<gate kind>-<project_trust_id>-<digest prefix>.json` (schema
`schemas/trust-gate-confirmation.schema.json`).

| Field | Meaning |
|---|---|
| `gate_kind`, `gate_id` | as raised |
| `project_trust_id`, `repository_path` | binds the decision to this project on this machine |
| `bound_digests[]` | exactly the digests of §2 for the kind |
| `presented` | the decision package `gov` rendered, including verdict axes (`19` §6, `24` §4), computed lists and the certification view |
| `method` | `interactive_terminal` or `operator_decision_pin` |
| `confirmed_at`, `operator` | informational |
| `consumed_by_transaction` | set when the install transaction uses it; a consumed confirmation authorises nothing else |

### 3.1 Interactive terminal

`gov trust confirm <gate id>`:
- opens the controlling terminal (`/dev/tty`), never standard input;
- renders the decision package;
- requires the operator to type the first 12 hex characters of the bound digest displayed;
- refuses when there is no controlling terminal (`TRUST_GATE_NEEDS_TERMINAL`).

This raises the bar for agent tool calls, which normally have no controlling terminal. It is **not** a boundary against
a same-user process (A3), which can allocate a pseudo-terminal (residual TG-2).

### 3.2 Operator decision pin (automation)

- **Location:** `<account-home>/.config/gov/approved-trust-decisions`, resolved from the account database.
- **Content:** lines of `{gate_kind, bound_digests, project_trust_id or "*", expires_at?}`.
- **Use:** operators pre-approve a specific transition, for example a CI image approved to install exactly one final
  statement digest.
- **Trust assumption:** TA-9 (provisioned outside the repository writer's control).
- **Limit:** a pin never approves a kind the TPS gating marks `local_terminal_only`. The default for `downgrade`,
  `policy_lowering`, `adopt_lineage` and `override_kernel_integrity` is `local_terminal_only`.

### 3.3 Never agent-resolvable

A compiled rule, independent of `HUMAN_GATE_POLICY.agent_resolvable_when`: a trust gate MUST NOT be answerable by
`gov decide` or by any agent path. `gov decide` on a trust gate returns `TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED`.

## 4. Repository gate records

- The OS still writes a record under `spec/decisions/` for audit (T2 evidence). It contains the gate, the package, and
  after confirmation the digest of the local confirmation.
- On any other machine, or when present without a matching local confirmation, the repository record is a **request**.
  It raises the gate on that machine; it never authorises.
- `answer.by_kind`, `presented_in_chat` and `gate_status` in a repository record are never consulted for a trust decision.
- Result: review `P2` (A2 edits `HDG-0001` to answered) yields `HUMAN_GATE_REQUIRED` plus
  `TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED` (reference model `evidence/P4r3` `R3_gate_record_from_repository`).

## 5. Non-trust governance gates (unchanged; limit stated)

Ordinary Human Decision Gates keep the D-0007 semantics: product direction, CIT approvals, tool installs outside trust
transitions. Their records are T2 evidence against A1, A3 and A5.

**TA-8 limit (restated):**
- **Repository writer.** Against A2 these records remain requests: A2 can commit an answered record. A2 can also commit
  the code the gate governs, so the gate is not a boundary against A2 for non-trust matters.
- **Agents.** Consumers of non-trust gates that `HUMAN_GATE_POLICY.raise_for` covers MUST require `by_kind: human`
  computed by `gov` at answer time and recorded with the acting session. That stops agent answers through `gov`, not
  forged records.
- **Plugins and tool subprocesses** can write gate, decision and exception records (VR-3 extended, `02` §4). The effects
  are these requests only.

## 6. Exceptions

A `PROJECT_EXCEPTIONS` entry can never relax a key of class `floor`, `pinned`, `members` or `precedence`, or any key under
the compiled prefixes, whatever its decision record says (`23` §4). For the remaining relaxable keys, the decision record
stays T2 and the exception is a project-layer T4 relaxation within registered precedence. No trust fact depends on it.

## 7. Residuals

| ID | Residual | Bound |
|---|---|---|
| TG-1 | A trust decision on one machine does not authorise another machine. | By design: each machine confirms, or uses an operator pin. |
| TG-2 | A same-user process (A3) can write the VTS or drive a pseudo-terminal. | Same-user boundary (RS-3); A3 can already alter the user's files. |
| TG-3 | Non-trust gates remain forgeable by A2 as repository records. | TA-8 limit (§5); none of them changes a trust fact. |
