# AR-0029 — blocking findings on `srr1-r1-candidate-2`

Gate: `GATE-R1-CANDIDATE-ACCEPT`. Verdict: **`BLOCKING_FINDINGS_PRESENT`**. Two blocking findings, both MEDIUM,
both the same class.

**This section is not empty.**

Convergence label for each finding is stated explicitly, as `HO-0029` requires: whether it is a **residual** of
`AR27-B1` / `N1` / `N2` / `N4`, or a **materially new blocker class**.

---

## `AR29-B1` — MEDIUM — a machine marked `DEGRADED — RECOVERY ONLY` completes a trust-policy mutation

| Field | Value |
|---|---|
| Exact normative source | `OWNER-DECISION-0006` §6 bullet 4: "Below-floor recovery MUST NOT permit: … trust-policy mutation" |
| Original-baseline | no | **Current-owner-approved** | yes (`OWNER-DECISION-0006`, digest `90340772…`) |
| Provenance class | `OWNER-ADDED-NORMATIVE` |
| Lifecycle / gate | **R1** — `OWNER-DECISION-0006` places its implementation, CLI surface and tests at R1; gate `GATE-R1-CANDIDATE-ACCEPT` |
| Falsifies a claim? | **Yes.** `runtime/src/srr/breakglass.rs` requirement map row 6 states §6 is enforced by `guard`/`guard_light`. It is not, on the paths that never call them. It also falsifies AR-0027's disposition "bullets 2–7 hold". |
| Convergence label | **MATERIALLY NEW BLOCKER CLASS** — not a residual of `AR27-B1` |
| `REQUIRES_R0_OR_OWNER_ADJUDICATION` | no |

### What is wrong

`AR27-B1` was a defective *decision procedure* at a guard the operation did reach. The repair fixed that
decision procedure and I confirm it (see `00-VERIFICATION-REPORT.md` §A). This finding is the prior question:
**is the guard on the path at all?**

`gov trust root-update` → `runtime/src/srr/provision.rs:51 root_update()` calls
`MachineState::open`, `refuse_repository_sourced_anchor`, `verifier::trusted_root`,
`metadata::accept_root_succession`, `ms.set_root_metadata`, `Floors::raise_metadata`, `Floors::save`.

It calls **neither `control::guard_write` nor `srr::breakglass::guard`**. There is no enforcement point on the
path, so the allow-list never runs. The implementation's own `REFUSAL_CLASSES` maps
`("trust root-update", "trust_policy_mutation")`, i.e. the code intends to refuse exactly this operation.

### Why AR-0027 did not see it

`heldout_srr3::d3` swept 35 operation **labels** through `guard_light` directly. Eight of those labels
(`upstream export`, `gate present`, `decide`, `release build`, `release certify`, `trust provision`,
`trust root-update`, `skills install`) have no `guard_write` call site anywhere in the product. Refusing the
*label* demonstrated nothing about whether the *operation* is refused. The re-run of `d3` on candidate 2 still
prints `trust root-update` in its REFUSED column — and the operation still succeeds.

### Bounded counterexample (reproducible, dynamic)

`evidence/heldout-tests/ho_b_coverage.rs::b1` and `::b2`, output in `evidence/HELD-OUT-TEST-OUTPUT.txt`:

```text
AR-0029 B1 — marked `DEGRADED — RECOVERY ONLY`; `gov trust root-update` returned Ok(Bool(true))
  trust anchor version before = 1, after = 2; revoked keyids = ["10ba682c8ad1…"]
  machine still marked degraded after the trust-policy mutation = true

AR-0029 B2 — after the below-floor rotation: anchor version = 2, root metadata high-water = 2,
             anchor key held by = eeec86207f875ff6…
```

Preconditions asserted inside the test before the attack runs: `breakglass::is_degraded(&ms, product) == true`;
`permitted_activity("trust root-update") == None`; `guard(&ms, product, "trust root-update")` returns
`SRR_BELOW_FLOOR_REFUSED`. The guard would refuse it. Nothing asks the guard.

**Method disclosure.** The marking record is minted directly into protected machine state with the members
`enter` writes (`active: true`, `marking`, `entered_at`, `product`, `machine_id`, `ingress`, `reason`), rather
than by consuming a signed break-glass token. Every consumer of the marking (`read_marking`, `Degraded::load`,
`is_degraded`) reads only those members, so the machine is in the identical state; and `root_update` does not
consult the marking at all, so the shape of the record cannot affect the result. The signed-authority path is
verified separately and unchanged (AR-0027 `d1`/`d2`, re-run passing).

### Consequence

Security: a machine knowingly running a below-floor release can re-anchor its trusted root, revoking by omission
every key the successor omits, and advance the protected `root` metadata high-water — the three things §6 bullet 4
exists to prevent while the machine is not trustworthy. Availability: none. Usability: none. Cost of repair: low
and local (one guard call in `provision::root_update`, or moving the §6 enforcement point to a place every
trust-changing ingress passes).

Mitigating, and stated so the severity is not overstated: the operation additionally requires a successor root
signed by the **outgoing root quorum**, which is owner-held offline key material. So this is a policy violation
rather than a privilege escalation for an attacker who does not already hold root keys. That is why it is MEDIUM
and not HIGH — the same severity AR-0027 assigned `AR27-B1`, on the same footing.

---

## `AR29-B2` — MEDIUM — new Human Gates are created below floor

| Field | Value |
|---|---|
| Exact normative source | `OWNER-DECISION-0006` §6 bullet 2: "Below-floor recovery MUST NOT permit: … creation or approval of new Human Gates" |
| Original-baseline | no | **Current-owner-approved** | yes |
| Provenance class | `OWNER-ADDED-NORMATIVE` |
| Lifecycle / gate | **R1**, `GATE-R1-CANDIDATE-ACCEPT` |
| Falsifies a claim? | **Yes**, the same claim as `AR29-B1` (requirement-map row 6), and AR-0027's "bullets 2–7 hold" |
| Convergence label | **MATERIALLY NEW BLOCKER CLASS** — same class as `AR29-B1` (missing enforcement point), not a residual of `AR27-B1` |
| `REQUIRES_R0_OR_OWNER_ADJUDICATION` | no |

### What is wrong

`orchestration::gates::create` is guarded (`guard_write(p, "gate create")`). Its sibling
`orchestration::gates::create_system` (`gates.rs:143`) builds and saves the same `human-gate` record and calls
`block_tasks`, with **no guard at all**. Two of its callers are reachable below floor:

1. `kernel_trust::request_override` (`kernel_trust.rs:329`), i.e. `gov kernel override` — no guard anywhere on
   that path. An operator below floor can raise a kernel-integrity Human Gate.
2. `update::apply_update_opts` (`update.rs:157`) — reached **through an allow-listed operation**.
   `guard_write(p, "update --apply")` returns `Ok` (the allow-list permits it), and the next reachable code
   creates a Human Gate with no guard in between. The test asserts that emptiness of the intervening span
   directly.

`human_gate_required` is `!breaking.is_empty() || !human_gates.is_empty() || cert != "CERTIFIED"`, so a
non-certified target — the ordinary break-glass case — always raises the gate.

### Bounded counterexample (structural, with the decision half measured)

`evidence/heldout-tests/ho_b_coverage.rs::b3` and `::b6`. `b6` asserts from the candidate's own source that no
guard sits between the allow-list entry and `gates::create_system`, and measures that `update --apply` passes the
guard while `gate create` and `gate answer` are refused with `human_gate_create` / `human_gate_approve`.

I did not drive `gov kernel override` end to end, which needs a fully initialised governed project and a
tampered kernel; the finding rests on the call graph, which the test pins against the source rather than
asserting from memory. This is a scope limitation I disclose rather than paper over.

### Consequence

Security: §6 bullet 2 is a MUST NOT and is not enforced; the gate `gov kernel override` raises is the one that,
once answered, permits operating on a kernel that failed its integrity check. Availability: a second-order
effect, recorded separately as `AR29-N4` — the gate `update --apply` creates below floor cannot be answered
(`gate answer` is correctly refused), so that allow-listed restoration route cannot complete when a gate is
required. `kernel reinstall` and `update --rollback` are gate-free and remain open, so this is not a deadlock.
Cost of repair: low and local.

---

## Not raised as blockers — recorded elsewhere

- `AR27-OD1` and `SRR2-R1-C1` are **closed by `OWNER-DECISION-0007`** and were not reopened. `exit_satisfied`
  remains the single exit-floor comparison with `EXIT_POLICY = "b_stricter_both_floors"`; verified, not graded.
- The `Marking::Unreadable` exit gap (`AR29-C1`), the `AuthenticatedRelease` constructor claim (`AR29-N1`) and the
  rest are in `20-LATER-LIFECYCLE-CONDITIONS.md` with their lifecycles.
- `AR27-N3`, `N5`, `N6`, `N7` are R2-carried and were not raised.
