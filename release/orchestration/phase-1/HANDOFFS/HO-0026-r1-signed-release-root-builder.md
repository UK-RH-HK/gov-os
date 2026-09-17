# HO-0026 — Handoff for the R1 Signed Release Root implementation build

| Field | Value |
|---|---|
| Handoff | HO-0026 |
| From | orchestrator (routing only) |
| To | fresh isolated builder / implementation role |
| Base commit | `7858b6d7ce750ebcd2e2e3acbb48101eebd917d5` |
| Accepted architecture | ARCH-0003, R0-accepted by AR-0025 at candidate `2b36b44` |
| Active gate | `GATE-BUILDER-READY` |
| Required verdict | `READY_FOR_INDEPENDENT_OS_VERIFICATION` or `INCOMPLETE` |

## Your authority and its limits

R0 acceptance authorises you to implement **the accepted architecture, and only that**. You declare readiness; you
never declare acceptance. A separate fresh independent R1 verifier grades your candidate. You must not author, guess
at or pre-empt its held-out tests.

## Normative sources, in precedence order

1. The three original Governance OS governing documents at the repo root.
2. `Governance_OS_Capability_Acceptance_Contract_v3.md` (repo root) — SHA-256
   `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3`. **Verify this digest and hash-bind it.** Never
   reconstruct contract text from memory, summaries or generated docs.
3. Active owner records: `OWNER-DIRECTIVE-0004`, `D-0009`, `OWNER-DECISION-0005`, `OWNER-DECISION-0006`
   (SHA-256 `903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db`), and `D-0007` which remains ACTIVE.
4. The accepted architecture: `spec/architecture/ARCH-0003.yaml` (accepted body SHA-256
   `42681978d3a7603da857029e68bd120453bd9ff373b8dea2c4247343a857cfda`) and
   `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md` (SHA-256 `695aa185ab32a813cd596b12f80d235afb92d56f147f395b15f16e37d0bcd983`).
5. The frozen boundary's **R1 section**: `release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`
   — SHA-256 `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`. **This is what R1 is graded against.** Read it first.
6. `04-R0-CORRECTION-1.md` and both R0 review packs, for the reasoning behind the accepted text.

Verify every digest before relying on it. A mismatch is a STOP condition: report it, do not work around it.

## What to build

Implement the accepted Signed Release Root architecture in this Rust workspace (`runtime/`, `cli/`, plus
`framework/` data). At minimum, per the frozen R1 section:

1. **A mature, reviewed cryptographic/TUF implementation, used correctly.** Do not hand-roll signature verification or
   metadata parsing. The crates.io registry is reachable; add a well-reviewed dependency (for example `ed25519-dalek`,
   or a TUF client crate) and pin it in `Cargo.toml`/`Cargo.lock`. Record what you chose and why.
2. **Signed root/delegation/release metadata** with version, expiry, thresholds and roles, binding exact
   product/repository identity, release version, monotonic sequence, payload digests and migration identity.
3. **One verification policy across every privileged ingress** — `init`, `adopt`, `update`, `reinstall`, `rollback`,
   `recovery`. Every ingress calls the same verifier. No ingress bypasses it.
4. **Candidate/source files cannot create their own trusted identity.** Repository content, `KERNEL_MANIFEST.json`,
   `framework.lock`, environment variables, caller fields, plugins and model output must never establish release
   authority or Human Gate approval.
5. **Verified-byte binding**: staged bytes are the verified bytes and the installed/used bytes are those same bytes,
   with atomic, crash-safe staging and commit.
6. **Durable monotonic high-water** plus the signed minimum secure release, stored in protected local state separate
   from repository state, and **enforced at every backward-capable ingress**, not only `rollback`.
7. **Break-glass below-floor recovery exactly per `OWNER-DECISION-0006`** — all ten requirements. The authority must
   be owner-controlled local/out-of-band and non-manufacturable by repo content, env vars, caller fields, plugins or
   model output; entry durably recorded with machine identity, floors, recovery release identity, reason and timestamp;
   the machine marked with the exact token `DEGRADED — RECOVERY ONLY` (U+2014 em dash — byte-exact); permitted
   activities limited to inspection, backup/export, diagnosis, repair, uninstall/reinstall and restoration; normal
   privileged operation, Human Gate creation/approval, certification, trust-policy mutation, privileged plugin/profile
   acquisition and floor reset all refused while below floor; the signed floor never lowered; and **recovery must work
   with no network/GitHub access**.
8. **Honest stale/offline semantics.** Report unknown currency as unknown. Claim no knowledge of unseen revocations.
9. **Fail-closed behaviour** on wrong key, wrong product, wrong channel, modified metadata/payload/migration, replay,
   downgrade and expiry.

## R1 conditions you must also close

Carried from both R0 reviews at R1 lifecycle:

- **`SRR2-R1-C1`** (owner question open, non-blocking): implement the **stricter fail-safe** exit — clearing
  `DEGRADED — RECOVERY ONLY` requires a verified release at or above **both** the signed minimum secure release **and**
  the protected local high-water. Implement it as **one isolated, clearly named policy point** with a comment citing
  `SRR2-R1-C1` and `GATE-OWNER-R1-BREAK-GLASS-EXIT`, so the owner can flip it to the looser reading with a single
  change. Do not scatter the condition through the code.
- **`SRR2-R1-C2`**: bind the protected offline-recovery record to the payload/kernel digests or
  `kernel_manifest_hash` actually verified — not to the release version alone.
- **`SRR2-R1-C3`**: the protected high-water and signed minimum secure release must survive uninstall and project
  removal. Implement and test it.
- **`SRR-R0-L1`**: make root succession/rotation acceptance semantics concrete rather than imported by reference.
- **`SRR-R0-L2`**: bind the release channel in metadata rather than using it only as a scoping concept.
- **`SRR-R0-L3`**: scope "repository gate records are requests" to **trust-changing** operations, so it does not
  collide with D-0007 T2 / Contract v3 L2.
- **`SRR-R0-L4`**: do not introduce an unguarded dev/test trust mode (Contract v3 A2 bullet 8 masquerade). It is
  vacuous today; keep it that way.
- **`SRR-R0-L5`**: define and implement high-water/journal durability ordering relative to atomic commit.
- **`SRR-R0-L6`** (owner-deferred to R1): implement the distinction between **built-in/local capabilities** and
  **remotely acquired privileged plugins/tools/profiles**, and how delegated signed targets apply to each.
- **`SRR-R0-L7`** (owner-closed): offline/air-gapped **first install** is **OUT OF SCOPE**. Do not build it. This does
  not weaken requirement 7 above: break-glass *recovery* must still work without network.

## Preservation obligations — do not regress the product

- Preserve every valid pre-RoT Governance OS control and capability. `D-0007` remains ACTIVE and its trust-direction
  semantics must be preserved, not replaced: installed-kernel integrity stays a separate control, and its records
  establish that a copy is *intact*, never that it is *authentic* or *admissible*.
- Keep the private/local owner-controlled deployment boundary. Do not introduce public SaaS, multi-tenant or cloud
  assumptions, and do not import R2 ceremony or R3 high-assurance requirements.
- The existing test suites under `tests/unit` and `tests/certification` must still pass. Run the full regression and
  report results honestly, including any pre-existing failure you did not cause.

## Capability Contract scaffolding

Build the contract-source scaffolding the gate register expects, hash-bound to the owner's root file:
`framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md` as a byte-identical canonical import, a
source lock recording SHA-256 `4c2df291…`, and the executable/schema/evidence-map scaffolding. The canonical import
must be verifiably identical to the owner source; a divergence must fail closed. Do not paraphrase, summarise or
"improve" the contract text.

## Hard prohibitions

- No RoT-1 Revision 8; no CP-1 resumption; no D-0008/ARCH-0002 activation or mutation.
- Do not amend or supersede D-0007, D-0009, ARCH-0003's accepted body, the frozen boundary, or any owner record.
- Do not modify `release/root-of-trust/*-review*/**`, `release/verification/**`, `release/releases/**` or any prior
  kernel payload or historical evidence.
- No private keys in the repository, in a log, or in your context. Test/fixture keys must be clearly marked as test
  material and must not be usable as a production root.
- No production signing ceremony, no key custody ceremony — those are R2.
- Do not read, list or search session/agent transcripts or task-output stores. Do not open or write user auto-memory.
- Do not contact the product owner. Record any `NEW_OWNER_DECISION_REQUIRED` item in your report instead.
- Do not author or speculate about the independent verifier's held-out tests.

## If the scope exceeds what you can complete

Do not fake completion and do not silently narrow scope. Build in the priority order above, and if you cannot finish,
return `INCOMPLETE` with a precise account of what is done, what is not, and what remains. An honest `INCOMPLETE` is
routed to a follow-on build; a false readiness claim wastes an independent verification cycle and is the worse outcome.

## Deliverables

- The implementation, committed on branch `phase1/srr1-r1-build`.
- Builder regression evidence under `release/root-of-trust/signed-release-root-v1-r1-build/`: what you implemented,
  the crypto/TUF dependency chosen and why, a requirement-to-code map covering the frozen R1 section, all ten
  `OWNER-DECISION-0006` requirements, and each R1 condition above; plus your test output and a
  `REVIEWED-CONTENT-DIGESTS.txt`.
- `release/orchestration/phase-1/AGENT_RUNS/AR-0026.report.yaml` per the `AGENT_RUNS/README.md` schema, committed
  **after** the work commit and naming it in `output.commit`.

A run without a durable committed report is INCOMPLETE and advances no gate.
