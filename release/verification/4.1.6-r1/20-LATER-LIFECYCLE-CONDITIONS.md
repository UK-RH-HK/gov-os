# AR-0027 — Non-blocking findings and later-lifecycle conditions

Recorded against candidate `srr1-r1-candidate-1` (work commit `949c4d34`), verified at worktree HEAD `0ce7f9f0`.

None of these blocks `GATE-R1-CANDIDATE-ACCEPT`. Each states its lifecycle. Per the frozen boundary's finding-intake
contract, a reviewer may recommend stronger security but cannot promote it into a requirement: the R1-lifecycle items
below are recommended for the same bounded repair cycle that closes `AR27-B1` only because they are cheap and local,
not because they gate the verdict.

---

## `AR27-N1` — expiry is compared lexicographically with no canonical-form gate (disclosed residual 3)

- **Normative source:** frozen R1 section, "wrong keys, modified metadata/payload/migration, replay, downgrade and expiry all fail closed"; `ARCH-0003` §7 / 00-ARCHITECTURE "Freshness and revocation".
- **Provenance:** `VERIFIER-HARDENING`. **Lifecycle:** R1 recommended, R2 required.
- **Claim status:** does **not** falsify the R1 criterion. Proposes stronger assurance.
- **Measured** (`heldout_srr2.rs::b1`, `::b2`): `Envelope::is_expired` is `!e.is_empty() && e <= now` (`metadata.rs:140`) against `now_iso()` (`%Y-%m-%dT%H:%M:%SZ`). Three inputs that are valid RFC-3339 but not in the emitted form:
  - `2026-09-17T13:00:00+14:00` — genuinely **13 hours in the past** at local clock `2026-09-17T12:00:00Z` — evaluates as **not expired**;
  - `2026-09-17t11:59:59z` (RFC-3339 permits lowercase `t`/`z`) — one second in the past — evaluates as **not expired**;
  - metadata carrying **no `expires` member at all** never expires (fail-open default), and `Root::parse`/`Release::parse` do not require one.
  `b2` confirms no canonical-form check guards the comparison: a root with `expires: "2099-01-01T00:00:00+00:00"` provisions cleanly.
- **Why it does not block:** `expires` lives inside the signed byte-string. An adversary who alters it invalidates the signature, so *modified* metadata still fails closed, and replay of canonically-formed expired metadata is refused (verified in `heldout_srr2.rs::c2`). Reaching the fail-open state requires the **publisher** to emit a non-canonical form. That is a producer-contract gap across a trust boundary, not an attacker-reachable bypass.
- **Why it still matters:** there is no issuing tooling in the product (see `AR27-N6`), so the emitted format is enforced nowhere — the precondition the lexicographic comparison depends on is assumed rather than checked on the untrusted side.
- **Recommended repair (bounded):** in `Envelope::is_expired`, refuse any `expires` that is not exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`, and treat a missing `expires` as expired. Both are fail-closed and confined to `runtime/src/srr/metadata.rs`.

## `AR27-N2` — an expired trust anchor still authorises trust-changing operations, and the branch that says otherwise is a no-op

- **Normative source:** 00-ARCHITECTURE "Freshness and revocation": "Expired/stale metadata blocks trust-changing lifecycle operations **according to the profile**"; `ARCH-0003` body §7 line 74 ("Root has long expiry ...").
- **Provenance:** `IMPLEMENTATION-CHOICE` with a defective in-code claim. **Lifecycle:** R1 recommended, R2 required.
- **Claim status:** falsifies an **in-code comment**, not a frozen-boundary R1 claim. The clause defers the concrete policy to the profile, and the machine reports the state honestly, so R1 is satisfiable without this.
- **Measured** (`heldout_srr4.rs::e1`): with an expired root anchor in protected state, `gov trust status` correctly reports `trust_anchor.expired_against_local_clock = true`, but `admit` still verifies a release against that anchor and returns `authenticity = AUTHENTIC`. `verifier.rs:312-314` reads:
  ```rust
  if root.envelope.is_expired(now) {
      // An expired root does not brick an installed system, but it cannot authorise a trust change.
      return Ok(Some(root));
  }
  Ok(Some(root))
  ```
  Both arms are identical, so the comment's stated intent is not implemented anywhere. `accept_root_succession` likewise checks the *candidate* root's expiry but never the *outgoing* root's, so an expired root can authorise its own successor.
- **Recommended repair (bounded):** decide the profile explicitly and implement it once — either refuse trust-changing ingresses against an expired anchor, or delete the dead branch and state in the doc that root expiry is reported but not enforced. Leaving a no-op branch whose comment asserts an unimplemented control is the part that should not ship.

## `AR27-N3` — `timestamp.json` and `snapshot.json` are optional, so the TUF freeze-attack controls can be dropped by omission

- **Normative source:** frozen R1 "a mature reviewed TUF/cryptographic implementation is used correctly"; `ARCH-0003` §4 "Snapshot metadata binds one consistent metadata set. Timestamp metadata supplies short-lived freshness for trust-changing operations."
- **Provenance:** `VERIFIER-HARDENING`. **Lifecycle:** **R2**.
- **Claim status:** proposes stronger assurance; falsifies nothing.
- **Measured** (`heldout_srr4.rs::e2`): presenting `release.json` alone — no `timestamp.json`, no `snapshot.json` — is accepted with `authenticity = AUTHENTIC`, `currency = UNKNOWN`, and the trust-changing operation proceeds. An **expired** timestamp yields `currency = STALE` and also proceeds; only `release.json`'s own expiry is a hard refusal. Nothing in the implementation requires `currency == Current` for a trust-changing ingress.
- **Why it does not block:** the controls that actually bound replay and downgrade remain in force and were verified — the monotonic metadata high-water refuses older metadata versions, the release-metadata expiry fails closed, and the protected release floor binds every ingress. When a snapshot *is* present its binding to the release is enforced (`SRR_RELEASE_NOT_IN_SNAPSHOT`, verified). Currency is reported honestly as `UNKNOWN`/`STALE` rather than overclaimed, which is exactly frozen R0 item 10.
- **Recommended for R2:** make both roles mandatory on a provisioned machine, or require non-`UNKNOWN` currency for the trust-changing ingress set. Expiry durations are already named as R1/R2 profile parameters.

## `AR27-N4` — `crypto::verify` carries a permissive fallback that defeats `verify_strict` (unreachable, but live on the public surface)

- **Normative source:** frozen R1 "a mature reviewed TUF/cryptographic implementation is used correctly".
- **Provenance:** `VERIFIER-HARDENING`. **Lifecycle:** R1 recommended (trivial deletion).
- **Measured:** `runtime/src/srr/crypto.rs:70` is `key.verify_strict(message, &sig).or_else(|_| key.verify(message, &sig))` — it retries with the permissive verifier precisely when the strict one refuses, immediately below a comment asserting that strict verification means "a signature cannot be made to verify under more than one identity". The module doc makes the same claim.
- **Why it does not block:** the function has **zero call sites in the product**. Every role signature goes through `crypto::verify_strict` at the single site `metadata.rs:338`, which has no fallback. Held-out test `heldout_srr.rs::a10` confirms a malleated (non-canonical `S`) signature does not verify through the real path.
- **Recommended repair:** delete `crypto::verify`, or make it call `verify_strict` only. It is a public API on `gov_runtime::srr::crypto` and a trap for a future caller.

## `AR27-N5` — a `minimum_secure_release` published without `minimum_secure_sequence` never raises the floor

- **Provenance:** `VERIFIER-HARDENING`. **Lifecycle:** R1 recommended, R2 required.
- **Measured (code):** `Floors::raise_minimum_secure` (`state.rs`) advances only when `sequence > self.minimum_secure_sequence`. `Release::parse` defaults an absent `minimum_secure_sequence` to `0`, so a release that names a minimum secure *version* but omits the sequence silently raises nothing.
- **Why it does not block:** monotonic-upward-only behaviour is preserved and no floor is lowered; the effect is a floor that fails to rise, and it requires publisher omission.
- **Recommended repair:** refuse a `minimum_secure_release` that carries no positive `minimum_secure_sequence`, or fall back to the semantic-version basis for the raise.

## `AR27-N6` — delegated targets are parsed and enforced but never wired to the enforcement point, and cannot be issued (disclosed residual 4)

- **Normative source:** `OWNER-DECISION-0005` §2 (`SRR-R0-L6`, deferred to R1); frozen boundary R2 "production signatures and key-custody evidence".
- **Provenance:** `LATER-QUALIFICATION/CERTIFICATION`. **Lifecycle:** **R2**.
- **Measured:** `runtime/src/capabilities/governance.rs:472` calls `srr::plugins::guard_acquisition(&id, &descriptor, acquisition, &[], &channel)` — the delegation slice is a **hard-coded empty literal**. `Release::parse` does parse `delegations`, and `AuthenticatedRelease.delegations` carries them, but nothing connects the two. No tooling can issue a delegation either.
- **Consequence:** every privileged remotely-acquired capability is refused with `SRR_PLUGIN_NOT_DELEGATED`. This is **fail-closed and strictly more restrictive than the pre-SRR product**, so it is a completeness/availability gap, not a security gap.
- **See `SRR-R0-L6` disposition in `00-VERIFICATION-REPORT.md`:** the owner's R1 obligation is judged **met**.
- **Recommended for R2:** pass `auth.delegations` through to the enforcement point and supply issuing tooling alongside production signing and key custody, which the frozen boundary already places at R2.

## `AR27-N7` — capability evidence map rows are all `NOT_YET_MAPPED`

- **Normative source:** frozen boundary R2, "current capability evidence"; Capability Acceptance Contract v3.
- **Provenance:** `LATER-QUALIFICATION/CERTIFICATION`. **Lifecycle:** **R2**.
- **Measured:** `tests/governance/capability-evidence-map.yaml` (new, 606 lines) declares every capability with `automated_checks: []` and `evidence_class: NOT_YET_MAPPED`. The file states this itself: "Rows are DECLARED, never asserted as satisfied; populating them is governed work, not a builder claim."
- **Assessment:** honest disclosure, correctly lifecycled. No R1 consequence. The contract source chain that backs it *is* hash-bound and fails closed (verified).

---

## `NEW_OWNER_DECISION_REQUIRED`

### `AR27-OD1` — should protected machine state be anchored to a path an owner-privileged process cannot relocate? (disclosed residual 2)

**Flagged `REQUIRES_R0_OR_OWNER_ADJUDICATION`.** Any repair changes the bootstrap assumption and the declared trusted
boundary, so it stops for the owner rather than being routed into a bounded repair.

- **Measured** (`heldout_srr2.rs::c4`): on a provisioned machine, `GOV_MACHINE_STATE_DIR` is genuinely refused with `SRR_PROTECTED_STATE_OVERRIDE_REFUSED` — the named override works as documented. But `resolve_state_root` computes "is the machine provisioned?" against `default_state_root()`, which is itself derived from `XDG_STATE_HOME` then `HOME`. Setting `XDG_STATE_HOME` therefore relocates the *default*, the machine reads as `UNPROVISIONED`, and in that posture entirely unsigned candidate bytes are admitted (`authenticity = UNKNOWN`). Two environment variables achieve exactly what the third is refused for.
- **Is the builder's reliance sound or circular?** **Sound, not circular.** `ARCH-0003` §1 — accepted at R0, body digest `093cb78e…`, unchanged since acceptance — states "R0 assumes the local OS, administrator, bootstrap installation boundary and local time source are uncompromised" and "It does not claim protection from a hostile administrator/OS". A process that can set `XDG_STATE_HOME` for a `gov` invocation runs with owner privilege and is inside that declared boundary. The assumption predates and is independent of the implementation, so the implementation is not vouching for itself.
- **Is the honesty claim preserved?** **Yes, everywhere tested.** On the relocated root the verifier reports `posture = UNPROVISIONED`, `authenticity = UNKNOWN`, never `AUTHENTIC`; it emits an explicit note that no anchor is provisioned; `gov trust status` reports the same; and `record_installed` on an `UNKNOWN` release advances **no** protected floor (verified). No security claim is manufactured from the evaded state.
- **Can an adversary otherwise return a machine to the unprovisioned posture?** **No, inside the declared boundary.** Deleting `trust/root.json` fails closed with `SRR_TRUST_ANCHOR_MISSING` rather than silently unprovisioning, because the `provisioned.json` latch is never cleared (verified, `heldout_srr2.rs::c3`). Deleting the latch requires write access to protected machine state, i.e. owner privilege.
- **The question for the owner:** the implementation already treats env-based relocation as a threat worth refusing for one variable. Should that control be completed — by anchoring protected state to a fixed machine-domain absolute path independent of `HOME`/`XDG_STATE_HOME` — or should the asymmetry stand as an accepted consequence of the §1 boundary? Note the trade-off: the certification harness itself relies on `XDG_STATE_HOME` relocation to give each scenario its own simulated machine (`tests/certification/common.rs`), so closing it requires a different test isolation mechanism. This is a security-versus-usability/testability trade-off of exactly the kind the frozen boundary reserves to the owner.
