# Signed Release Root v1 — R0 architecture candidate

## Status

- Lineage: `Signed Release Root` (`SRR-1`)
- Architecture record: `spec/architecture/ARCH-0003.yaml`
- Governing owner decision: `spec/decisions/D-0009.yaml`
- Owner directive: `OWNER-DIRECTIVE-0004`
- State: `PROVISIONAL — PENDING FRESH R0 ARCHITECTURE REVIEW`
- Implementation: none authorised or performed
- Predecessor disposition: CP-1/RoT-1 retained as non-active high-assurance research, not revised

## Architecture outcome

The Phase-1 distribution trust boundary is deliberately small:

```text
trusted platform/admin bootstrap
  -> bootstrap verifier + public root metadata
  -> signed root/delegation metadata
  -> signed release/targets + snapshot + timestamp metadata
  -> uniform verifier for init/adopt/update/reinstall/rollback/recovery
  -> private verified-byte staging
  -> atomic commit + protected monotonic high-water
  -> separate installed-kernel integrity verification
```

This chain authenticates Governance OS releases. It does not attempt to prove every property of the build organizations, compilers, suppliers or human custodians at R0.

## Security objective

Given an authentic bootstrap verifier/root set, an uncompromised local OS/admin boundary and a local time source inside that boundary, only releases authorised under that root may enter privileged lifecycle staging; the installed and used bytes are the verified bytes; no lifecycle ingress places the machine on a release below its protected high-water or the signed minimum secure release, except under the explicitly authorised, recorded and marked break-glass recovery mode below; stale/unknown currency is reported honestly against that declared time source; and lower-trust project/repository/model/plugin inputs cannot create authority.

## Declared Phase-1 environment

The first profile is private and local:

- product-owner controlled machines;
- private source and release repositories;
- local or administrator-controlled installation;
- the local time source treated as inside the trusted local boundary, on the OS/administrator side of the line rather than the untrusted network side;
- no public multi-tenant service boundary;
- no hostile local administrator/OS claim;
- no standard-profile claim of DDC, supplier independence or absolute toolchain correctness.

Its explicit non-guarantees are stated in the same register:

- no protection from a hostile local administrator or OS, and no public multi-tenant isolation;
- no claim of absolute compiler/toolchain correctness;
- no knowledge of revocations an offline machine has never received, and no knowledge of future revocations that do not yet exist;
- no claim of correct expiry, staleness or currency when the local clock is materially wrong. Expiry, staleness and currency are determined by comparing signed expiry fields to that local clock. A clock set behind may accept expired metadata as unexpired and report currency as current when it is not; a clock set ahead may treat current metadata as expired and refuse trust-changing operations the profile would otherwise permit. Neither case lowers a signed floor, admits an unauthorised release or breaks the verified-byte binding: the failure is confined to freshness.

No trusted-time service, attested time, monotonic-time source, signed-time floor or clock-independent freshness mechanism is assumed, required or provided by this profile. Expiry durations remain R1/R2 profile parameters.

## Trust-domain boundaries

| Domain | Authority | Guarantee | Explicit limit |
|---|---|---|---|
| Bootstrap | trusted OS/admin installation boundary | verifier and initial public root are authentic | not derived from candidate files |
| Release publication | offline root and delegated signed metadata | authorised release identity and exact payload bytes | does not prove an honest build |
| Local installation | verifier, local admin policy, protected state | verified/use binding, atomic install, downgrade refusal | assumes local OS/admin boundary |
| Installed integrity | D-0007 kernel manifest/lock checks | later tampering is detected | not a first-contact authenticity root |
| Build provenance | signed attestations bound by digest | records source/inputs/builder evidence | not the client distribution root |
| Certification | independent evidence plus owner release decision | exact candidate meets its certification profile | not automatic from a signature |
| Project policy | authenticated kernel plus project strengthening | project cannot weaken protected floors | project cannot create distribution authority |
| Plugin/retrieval | kernel policy/registry plus delegated target identity | descriptor and executable bytes are governed | descriptor/model output cannot self-authorise |

## Metadata roles

| Role | Purpose | Cannot do |
|---|---|---|
| Root | keys, thresholds, delegations, rotation and revocation | ordinary unattended release publication |
| Release/targets | authorise exact release and governed companion artifacts | redefine root authority |
| Snapshot | bind one consistent set of metadata versions | authorise target bytes |
| Timestamp | provide bounded freshness for trust-changing operations | authorise target bytes or rewrite history |

The release/targets record binds product identity, release version and monotonic sequence, supported target, exact payload/kernel/CLI hashes, schema and migration identities, minimum secure release, metadata version/expiry and optional evidence digests. The project lock may reference this authenticated identity but supplies none of its authority.

## Lifecycle ingress invariant

The following operations consume the same verification result before protected writes:

| Ingress | Required authenticated object | Local authority | State effect |
|---|---|---|---|
| init | selected signed Governance OS release | local install/init policy | create governed layout from verified bytes |
| adopt | selected release plus migration identity | authoritative local adoption gate | preserve native project and overlay |
| update | newer eligible signed release | local update policy/gate | atomic upgrade and high-water advance |
| reinstall | same/newer eligible signed release | local reinstall policy | reconstruct from authenticated source |
| rollback | signed release not below security/high-water floor | explicit rollback/recovery policy | atomic transition; never silent downgrade |
| recovery | authenticated recovery target, or an installed complete local copy shown intact by D-0007 records and previously authenticated by this machine — in both cases not below the security/high-water floor | bounded local recovery authority; below floor only under break-glass | restore one complete valid state at or above floor, or a marked `DEGRADED — RECOVERY ONLY` state |

No ingress trusts a source path, repository manifest, `framework.lock`, Git ref, environment variable or caller statement as release authority.

### Signed floors bind every ingress

The signed floors are a property of the machine, not of one operation. No ingress in the table above — `init`, `adopt`, `update`, `reinstall`, `rollback` or `recovery` — may place the machine on a release below its protected local high-water or below the signed minimum secure release. `rollback` is the name of one governed ingress, not the name of the rule; the floor check belongs to the single verification policy every ingress calls.

Local installed-integrity evidence establishes that a local copy is *intact*, never that it is *admissible*. D-0007's payload ↔ `KERNEL_MANIFEST.json` ↔ `framework.lock` chain detects post-install tampering; per OWNER-DIRECTIVE-0004 it is not a first-install authenticity root, and it is not a floor check. Where no current metadata is reachable, the authenticity of an installed local recovery path comes from this machine's own protected record of the release identity it previously verified and installed — not from the manifest, the lock, the repository or mutually consistent files shipped with that copy. Admissibility is still the floor check.

### Below-floor break-glass recovery

A machine whose only complete local state is below its own floor is the one case the floor rule cannot silently decide. Per `OWNER-DECISION-0006`, below-floor recovery is refused by default and is admissible only as an explicit owner-authorised emergency recovery mode with these architectural properties:

- **Authentic release only.** Break-glass relaxes the floor check alone. It never relaxes the authenticity check and never admits arbitrary or unsigned code.
- **Non-manufacturable authority.** Entry authority comes from an owner-controlled local or out-of-band recovery mechanism. Repository content, environment variables, caller fields, plugins and model output cannot manufacture it, and a below-floor or revoked binary cannot authorise its own entry.
- **Works without network.** Network or code-hosting reachability is not the break-glass authority and is not a precondition of it; recovery remains possible with no network or repository-hosting access.
- **Durable entry record.** Entry is durably recorded with, where available, machine identity, the current signed security floor and protected high-water, the recovery release identity, the reason and a timestamp/evidence reference.
- **Explicit marking.** While below floor the machine is marked `DEGRADED — RECOVERY ONLY` and reports that state; the below-floor release is never presented as current or fully trusted.
- **Permitted while below floor:** inspection; backup/export; diagnosis; repair; uninstall/reinstall; restoration of an authenticated Governance OS release.
- **Refused while below floor:** normal privileged Governance OS operation; creation or approval of Human Gates; release certification; trust-policy mutation; privileged plugin/profile acquisition; lowering or resetting the signed floor or high-water; treating the below-floor release as current or fully trusted.
- **The floor is not lowered.** Break-glass records that the machine is knowingly operating beneath its floor; it does not move, reset or forget the floor.
- **Exit condition.** Normal governed operation resumes only once an authenticated release at or above the signed minimum secure release is installed and verified, at which point the marking is cleared.

The authority's storage format, operator surface, identifiers and tests are R1 matters and are deliberately not fixed here. The properties above are R0-normative.

## Transaction invariant

R0 requires the future R1 design to make this true:

1. receive candidate bytes in a private staging area;
2. verify signed metadata and the exact staged bytes;
3. retain a typed authenticated-release handle/value;
4. install only those measured bytes;
5. atomically commit one complete version;
6. verify the committed representation;
7. durably update journal and high-water;
8. recover after interruption to the old complete version or new complete version.

Specific filesystem primitives are an R1 implementation choice. The safety outcome is an R0 requirement.

## Freshness and revocation

Standard signed metadata versions and expiry replace the CP-1 universal Trust State. Expiry durations are profile parameters selected and qualified later.

- A client never accepts an older metadata version than its protected high-water.
- A signed minimum secure release prevents unsafe downgrade at every ingress, not only at `rollback`, while preserving historical authenticity.
- Expired/stale metadata blocks trust-changing lifecycle operations according to the profile.
- Expiry alone does not stop an already authenticated installed system from ordinary governance work.
- A client that has not received newer metadata reports currency `STALE` or `UNKNOWN`; it does not claim current global revocation knowledge, and it claims no knowledge of future revocations that do not yet exist.
- Expiry, staleness and currency are determined against the local clock declared under *Declared Phase-1 environment*. Given an authentic bootstrap verifier/root set, an uncompromised local OS/admin boundary and a local time source inside that boundary, those reports are honest; when the clock is materially wrong they are wrong in the corresponding direction, and the declared non-guarantee says so rather than concealing it.
- Once a valid revocation/minimum is received, protected state prevents forgetting it, and break-glass does not lower, reset or forget it.
- A known-revoked binary is limited to inspection, export, diagnosis, repair, uninstall and participation in restoring an admissible release. That allowance is a path back to an admissible state, not an authority to re-establish the revoked release itself: a revoked or below-floor release is not an admissible recovery object under the floor check, and returning the machine to one requires break-glass authorisation, which the revoked binary cannot issue to itself and which leaves the machine marked `DEGRADED — RECOVERY ONLY`.

## Keys and custody

The target root policy is three offline root keys at 2-of-3. A standard delegated release/targets threshold replaces bespoke registration. Snapshot/timestamp roles are purpose-restricted. Production custody, concrete algorithms, library/version selection and ceremonies are R1/R2 evidence—not assumptions silently embedded in R0.

No production private key may exist in a repository, release package, log, general CI environment or ordinary developer workspace.

## Headless CI and multiple machines

- The administrator provisions verifier, public root metadata and protected machine/workload policy outside each governed project repository.
- An ephemeral runner begins from a signed trusted image/baseline, refreshes current metadata and verifies the pinned Governance OS release before privileged lifecycle work.
- A persistent machine maintains its own protected metadata/release high-water.
- CI may consume already authoritative Human Gate decisions; an environment variable, job input or repository file cannot manufacture one.
- Trust-changing automation is allowed only by administrator/workload policy provisioned outside the repository and scoped to the exact operation/release channel.

## Preservation of Governance OS

This architecture changes only release-source authenticity and lifecycle admission. It preserves ARCH-0001, D-0007 and Contract v3 capabilities, including the knowledge fabric, task DAG/readiness/checkpoints, Human Gates, CIT-P/CIT-E, governed plugins/tools, Gate W, G0–G6, migration, observability, recovery and learning.

## R0 traceability

| R0 requirement | Architecture section |
|---|---|
| explicit bootstrap assumption | Declared environment; Bootstrap trust domain |
| signed root/delegation/release metadata | Metadata roles |
| identity/payload/migration binding | release/targets binding |
| rotation/revocation | Metadata roles; Freshness and revocation |
| all privileged ingress | Lifecycle ingress invariant |
| verify/use binding and atomic install | Transaction invariant |
| rollback/high-water | Lifecycle ingress invariant (Signed floors bind every ingress; Below-floor break-glass recovery); Freshness and revocation |
| local authority and CI | Headless CI and multiple machines |
| stale/offline honesty | Freshness and revocation |
| domain separation | Trust-domain boundaries |
| assumptions and non-guarantees (OS/admin/time/network) | Declared Phase-1 environment, including the declared local time source and its non-guarantee; acceptance boundary |

## Review boundary

The fresh reviewer uses `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`. R0 is rejected only for a substantiated R0 defect. R1 implementation choices and R2/R3 evidence gaps may be recorded but cannot silently become R0 blockers.
