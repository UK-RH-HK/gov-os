# AR-0027 — Blocking findings for `GATE-R1-CANDIDATE-ACCEPT`

| Field | Value |
|---|---|
| Run | AR-0027 (`verifier-a`), fresh independent R1 candidate verification |
| Candidate | `srr1-r1-candidate-1`, work commit `949c4d343a6d5f203534afa6e3363992fee12488` |
| Verified at worktree HEAD | `0ce7f9f0a7028d54bc5beef57f0ef35a935e244d` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` |
| Blocking findings | **1** (MEDIUM) |
| `REQUIRES_R0_OR_OWNER_ADJUDICATION` among them | none |

---

## `AR27-B1` — `DEGRADED — RECOVERY ONLY` refusal is a deny-list, so normal privileged governed operation is not refused as a class

| Intake item | Statement |
|---|---|
| 1. Exact normative source and clause | `OWNER-DECISION-0006` (SHA-256 `903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db`), **Binding requirement §6, bullet 1**: "Below-floor recovery MUST NOT permit: normal privileged Governance OS operation". Verification scope item 8 of `HO-0027`: "All ten `OWNER-DECISION-0006` requirements hold **in running code**". |
| 2. Original-baseline / current-owner-approved | Original baseline: no. Current owner-approved: **yes** — `OWNER-DECISION-0006` is a binding owner product/security decision, rank 1 in the frozen boundary's normative hierarchy. |
| 3. Provenance class | `OWNER-ADDED-NORMATIVE` |
| 4. Lifecycle / gate | **R1** — `OWNER-DECISION-0006` itself states "Its implementation, storage format, CLI surface and tests are R1". Active gate `GATE-R1-CANDIDATE-ACCEPT`. |
| 5. Claim falsified | **Falsifies an existing candidate claim.** `runtime/src/srr/breakglass.rs:163` documents `guard` as "The default is **refuse**: an operation is allowed only when it matches nothing in [`REFUSED_OPERATIONS`]" — that sentence describes a deny-list while asserting default-refuse semantics. The module's own requirement map (`breakglass.rs:12`) asserts row 6, "§6 refused activities → `REFUSED_ACTIVITIES` + `guard`", as satisfied. Both are falsified by the measured permit set below. |
| 6. Impact | **Security:** a machine knowingly running a below-floor, owner-acknowledged-unsafe release may still perform state-mutating privileged governed work, including approving and rejecting change-intent transactions and revoking Human Gate records. **Availability:** repairing this slightly narrows what is possible below floor; `OWNER-DECISION-0006` §5 already names the intended permitted set, so no new owner trade-off is created. **Usability/cost:** low — a bounded edit at one chokepoint. |
| 7. Reproducible evidence | `evidence/heldout-tests/heldout_srr3.rs::d3_below_floor_refusal_surface_against_owner_decision_0006_section_6`; output in `evidence/HELD-OUT-TEST-OUTPUT.txt`. |
| 8. Owner decision needed | **No.** The owner already decided the policy in `OWNER-DECISION-0006` §5/§6; this is an implementation defect *within* the accepted boundary and routes to a bounded R1 repair. |

### What was measured

`runtime/src/srr/breakglass.rs` enforces §6 through `guard` and `guard_light`, which refuse an operation only when its
label contains one of the 26 substrings in `REFUSED_OPERATIONS`. Every other operation proceeds. The test entered
genuine break-glass (owner-signed `recovery`-role token, real `admit` path), confirmed the machine was marked, and
then submitted every operation label the product itself passes to `orchestration::control::guard_write`:

```text
REFUSED   (23): upstream submit, upstream export, memory select, gate create, gate answer, gate present,
                decide, tools install, replan, plugins register, handoff create, readiness plan, cit propose,
                cit execute, adopt migrate, task create, task claim, task close, release build,
                release certify, trust provision, trust root-update, skills install
PERMITTED (12): checkpoint, gate revoke, update --apply, plugins unregister, handoff return, cit simulate,
                cit approve, cit reject, adopt extract-legacy, adopt build-memory, task status,
                kernel reinstall
```

Of the permitted set, four are correct: `kernel reinstall` and `update --apply` are §5 "uninstall/reinstall" and
"restoration of an authenticated Governance OS release" (and `update --apply` is independently floor-checked inside
`admit`); `task status` and `cit simulate` are §5 "inspection"/"diagnosis"; `checkpoint` is §5 "backup/export".

The remaining **seven are not covered by any §5 permitted activity** and are normal privileged Governance OS
operation under §6 bullet 1:

| Operation | Why it is §6 bullet 1, not §5 |
|---|---|
| `cit approve` | Approves a change-intent transaction — an approval-class privileged governed decision. Sharpest case. |
| `cit reject` | The paired privileged disposition of a governed transaction. |
| `gate revoke` | Mutates a Human Gate record. (§6 bullet 2 names creation/approval; revocation is still normal privileged operation.) |
| `handoff return` | Orchestration state mutation. |
| `plugins unregister` | Mutates the registered capability set. |
| `adopt extract-legacy` | Adoption pipeline work. |
| `adopt build-memory` | Adoption pipeline work. |

Nothing else gates these while degraded: `guard_write` (`runtime/src/orchestration/control.rs:58`) calls
`kernel_trust::guard`, then `breakglass::guard_light`, then the freeze/pause checks. `authority::require` enforces
role authority, which is orthogonal to the below-floor marking. The test asserts both `guard` and `guard_light`
return `Ok` for `cit approve`.

### Bounded repair that closes it

Invert the policy at the single existing chokepoint so it matches the decision text — an **allow-list derived from
`PERMITTED_ACTIVITIES` (§5)** with everything else refused — or, if the deny-list shape is preferred, extend it to
cover the class rather than an enumeration. Either way the change is confined to `runtime/src/srr/breakglass.rs`
(`guard`, `guard_light`, and the `REFUSED_OPERATIONS`/`PERMITTED_ACTIVITIES` tables) plus the doc comment at
`breakglass.rs:163`, which must be corrected to describe what the code actually does. No architecture change, no
ingress change, no owner decision.

### Explicitly not claimed

This finding does **not** assert that any §6 bullet other than bullet 1 fails. Bullets 2–7 were tested and hold:
Human Gate creation/approval (`gate create`, `gate present`, `gate answer`, `decide`), release certification,
trust-policy mutation, privileged plugin/profile acquisition and floor lowering are all refused, and §8 (the floor
is never lowered by break-glass) was verified directly.
