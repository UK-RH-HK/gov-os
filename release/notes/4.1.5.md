# agentic-engineering-os 4.1.5 — release notes (repair candidate)

Third repair iteration, after the independent re-verification rejected 4.1.4
(`release/verification/4.1.4/INDEPENDENT_REVERIFICATION_REPORT.md`, verdict OS_RELEASE_CANDIDATE_REJECTED). Every
previously confirmed repair is preserved; 4.1.4 stays immutable and rejected. The kernel payload changed (plugin
governance, authority classes, precedence rules, schemas), so the version is bumped.
Repair mapping: `release/repair/4.1.5/REPAIR_REPORT.md`.

## Repaired (HIGH)
- **V-H1 — a plugin descriptor can no longer authorise itself.** `TOOL_POLICY.plugins.min_authority` now applies to
  every plugin execution, registered or not, and is read from verified kernel policy. A descriptor's `approved_roles`
  may only *narrow*; its `provenance`/`status` prove nothing. Registration is an OS-written record in
  `governance/generated/plugin-registry.json` binding plugin id, version, descriptor bytes and implementation bytes to
  the governed act (and to the answered gate for elevated permissions). An edited, re-versioned or id-spoofing
  descriptor fails closed with `PLUGIN_REGISTRY_MISMATCH`. Doctor D028 and the `plugin_governance` suite family report
  self-authorising descriptors whatever the acting role, and stale registrations. An L0 independence role obtains no
  execution by any of these routes.
- **V-H2 — constitutional enforcement now requires a verified kernel trust root.** `kernel_trust` authenticates the
  installed payload against `KERNEL_MANIFEST.json` *and* the manifest against `framework.lock.kernel_manifest_hash`
  before any policy is consumed. `PolicySet`, policy precedence, `ROLES.yaml`, routing, handoffs, adapters and the
  migration secret scanner read kernel content only through that boundary. On failure the embedded immutable baseline
  is substituted explicitly (never mixed), the substitution is recorded in `policy overrides`, the context packet,
  doctor D029 and the `policy_precedence` family, and every mutating operation — including `rebuild-memory` — fails
  closed with `KERNEL_TAMPERED` until `gov kernel reinstall` or an L4+ role answers a gate bound to that exact kernel
  state (`gov kernel override`). The human-decision channel stays open so the remedy can be recorded.

## Repaired (MEDIUM)
- **V-M1 — `PROJECT_EXCEPTIONS` decisions are resolved, not believed.** An exception applies only when its `decision`
  resolves to an existing ACTIVE decision record that is not superseded, revoked or expired, was approved at
  `AUTHORITY_POLICY.authority_levels_required.grant_policy_exception` (or by a human), names the exception id or its
  policy key (`authorises_exceptions` / `permits_policy_keys`), and is scoped to this project. Everything else is
  refused, recorded in `policy overrides --refused` and reported by doctor D027.

## Trust-boundary audit (directive §5, decision D-0007)
Trust classes are now stated and enforced: immutable release state, OS-written project state, verified registry state,
project configuration, caller input, plugin/model output. A field named `approved`, `registered`, `verified`,
`human_approved`, `authority`, `role`, `provenance`, `exception` or `override` arriving from a lower class is a
*request* — recorded and ignored. One further equivalent bypass was found and repaired: `gov tools install` treated a
descriptor's own `security_review: passed` as evidence; it now requires `security_review_record` to resolve to a
governed record, otherwise the auto-install condition fails and a gate is raised. The caller-declared acting role
(`--role`) remains a documented adapter boundary.

## New surface
`gov plugins register|unregister|registry|list|health` · `gov kernel trust|override [--reason]` ·
`gov policy overrides` now reports `kernel_trust` · doctor D028 (plugin governance, widened) and D029 (verified policy
source) · suite families `plugin_governance` and `policy_precedence` extended.

## Supported migration paths
- 4.1.1 → 4.1.2 → 4.1.3 → 4.1.4 → 4.1.5, and any suffix of that chain, via `M-4.1.4-4.1.5` (non-breaking; no overlay
  shape change, lock schema 1.1.0, full index rebuild because the index version changed).

## Known limits (honest scope)
- The acting role is caller-declared; binding it to an authenticated channel is an adapter responsibility (V-L5).
- HV-08b remains a non-blocker (D-0006); NV-09/NV-19 read the immutable 4.1.3 payload and are frozen-input failures.
- Vector/graph stores remain SQLite-fixed with brute-force cosine (V-M2); temporal git lineage and an LSP-grade code
  intelligence plugin remain future work (V-M3).

## Certification
Implementer tests and evidence only. Status: READY_FOR_INDEPENDENT_REVERIFICATION (not certified).
