# P2-HO-0042 — Repair iteration 1, round 4: residual integration points

| Field | Value |
|---|---|
| Handoff | P2-HO-0042 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0043** |
| Base | the commit your worktree is checked out at (release branch with round 3 integrated, `e4cb662` or later) |
| Output directory | `release/capability-baseline/repair-1/r4-residual/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0043.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`; the round-3 integration report
`release/capability-baseline/repair-1/integration-3/00-INTEGRATION-REPORT.md` (§3 the one P2-ADJ-0002 mechanism, §4 the one
availability host API, §8 observations, §9 stopped items); owner decisions `GATES/OWNER-DECISION-P2-0001-*`, `-0002-*`;
adjudications `GATES/P2-ADJ-0001-*`, `-0002-*`, `-0003-*`.

## Scope

The round-3 integration left builder integration points that were not routed to it, plus four observations (INT3-O1…O4).
You close the ones below over the integrated tree. Each is written in the originating report
(`release/capability-baseline/repair-1/r3-<ws>/00-REPAIR-REPORT.md`, or `integration-3` §8). Implement each as a
requirement, not a patch recipe; if a recipe is wrong for the integrated tree, satisfy its purpose another way and say so; if
an item is obsolete, say why.

## Files you own this round

Everything **except** WS-1's round-4 files, which a parallel builder (P2-AR-0042, evidence map) owns: `runtime/src/contracts.rs`,
`framework/contracts/**`, `framework/schemas/governance-capability-acceptance.schema.json`,
`tests/governance/capability-evidence-map.yaml`, `docs/generated/**`. Do **not rename or remove any existing test**: the
evidence map names tests as owners. Replacing a test is allowed only for IP-R3-WS02-10 below, keeping its name.

## Items routed to you

1. **INT3-O1 (WS-5 × WS-7, MEDIUM) — plugin registration inside a claimed task.** Today `gov plugins register` passes its
   own owner gate, but the task's close is refused `MATERIAL_CHANGE_REQUIRES_CIT` for the descriptor under
   `governance/project/plugins/`. Both requirements hold and neither is an owner question:
   - Contract v3 **K3** (lines 638–647): impact simulation auto-triggers for material **security** and
     **governance/policy** changes — a plugin registration is both.
   - Contract v3 **F4** (lines 425–431): elevated permissions reference an authoritative gate/decision; the descriptor
     cannot authorise itself; registration lives in trusted OS state.
   So the owner-approved registration does not replace change control, and a registration inside a task must end with
   impact simulation linked (auto-triggered, per K3) in a form close accepts. The mechanism is yours (e.g. registration
   proposes/links the CIT and the registration approval and CIT approval reference each other) — do not make the worker
   hand-file a CIT the OS could have triggered, and do not let the registration gate silently stand in for CIT-P/E.
   Prove it with WS-7's probe `ip_task_close_registration.py` (derived copy, labelled) and a certification test.
2. **INT3-O2 (WS-2) — when direct upstream change propagates.** `detect_and_propagate` now runs at claim. Contract v3 W6
   (1128–1136) with O5's G1 (mutation) tier: a direct change observed by an incremental rebuild is a mutation observed at G1,
   so dependent evidence should be marked stale when the change is observed, not only at the next claim. Make the rebuild
   path propagate (IP-R3-WS02-05 allowed either), keep the claim-time path, keep it idempotent, and show zeta-r
   `W12-G1-dependency-evidence-invalidated` unedited.
3. **Remaining builder IPs** (read each in its report):
   - WS-3: IP-R3-WS03-6 (disclose machine-scope sealing on a provisioned machine, through `t2::binding_status()`), -7
     (PROTOCOL.md registry-portability text), -9 (alpha-r A5 control-state path).
   - WS-8: IP-R3-WS08-3 (D033 / `os_binding_integrity` report the binding status, now `t2::binding_status()`).
   - WS-6: IP-R3-WS06-4 (shadowed-rule finding) **together with** WS-2 IP-R3-WS02-10 (retire WS-2's heading-marker
     confirmation step once WS-6's markers in `memory::coverage` make it redundant; if that deletes WS-2's unit test,
     replace it under the same name with a test of the property that still holds); IP-R3-WS06-7 (`skill-bindings.json` to
     `governance/registry/` and `OS_STORES`, with legacy relocation).
   - WS-9: IP-R3-WS09-4 (TOOL_PERMISSIONS for the independent roles).
   - WS-7: IP-W7R3-3 (currency class `tools_plugins` lists `governance/registry/plugin-registry.json`), -5 (relocate the
     registry at upgrade — brownfield projects must not lose registrations), -6 (memory-profile hashing and identity), -7
     (`plugins registry` help text still names `governance/generated/…`), -9 (ARCHITECTURE registry location and template
     rule).
   - WS-4: IP-R3-WS04-11 (block scope for `cit.propose` / `handoff.create`, including `handoff.create` as a remedy for
     remediation handoffs — the availability rule), -09 (docs).
4. **Optional, only if cheap and safe:** INT3-O3 (route WS-2's read-only floors digest through an `srr::state` helper so WS-8's
   R1 structural invariant stays exact — AR-0033 census must stay 0 violations), IP-R3-WS03-8, IP-W7R3-10, IP-R3-WS04-03/-06,
   IP-R3-WS02-11.

Not routed (for the verifier, recorded here so you do not re-open them): INT3-O4 (legacy unsealed task/CIT records rewritten
by `gov` are reported `os_managed_unbound`, not refused, never blessed); R3-WS5-11 (did not reproduce in integration-3).

## Also required

- New or changed subcommands are classified in `COMMAND_GUARDS` / `g0_label`.
- Availability rule on everything you touch: blocks scoped to what they protect; remedies and independent work stay available.
- Regression and R1 exactly as the common protocols require (private path, census). In your report, list every new test you
  add (name, what it proves) so the verifier and the evidence map can use it.

Report as before: per-item claims, files changed, tests changed with reasons, regression and R1 counts with census,
remaining integration points.
