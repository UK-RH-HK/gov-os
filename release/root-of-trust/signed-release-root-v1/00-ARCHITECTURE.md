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

Given an authentic bootstrap verifier/root set and an uncompromised local OS/admin boundary, only releases authorised under that root may enter privileged lifecycle staging; the installed and used bytes are the verified bytes; rollback below known signed floors is refused; stale/unknown currency is reported honestly; and lower-trust project/repository/model/plugin inputs cannot create authority.

## Declared Phase-1 environment

The first profile is private and local:

- product-owner controlled machines;
- private source and release repositories;
- local or administrator-controlled installation;
- no public multi-tenant service boundary;
- no hostile local administrator/OS claim;
- no standard-profile claim of DDC, supplier independence or absolute toolchain correctness.

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
| recovery | authenticated recovery target or installed valid recovery path | bounded local recovery authority | restore one complete valid state |

No ingress trusts a source path, repository manifest, `framework.lock`, Git ref, environment variable or caller statement as release authority.

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
- A signed minimum secure release prevents unsafe rollback while preserving historical authenticity.
- Expired/stale metadata blocks trust-changing lifecycle operations according to the profile.
- Expiry alone does not stop an already authenticated installed system from ordinary governance work.
- A client that has not received newer metadata reports currency `STALE` or `UNKNOWN`; it does not claim current global revocation knowledge.
- Once a valid revocation/minimum is received, protected state prevents forgetting it.
- A known-revoked binary is limited to inspection, export, recovery and uninstall.

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
| rollback/high-water | Freshness and revocation |
| local authority and CI | Headless CI and multiple machines |
| stale/offline honesty | Freshness and revocation |
| domain separation | Trust-domain boundaries |
| assumptions and non-guarantees | Declared environment; acceptance boundary |

## Review boundary

The fresh reviewer uses `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`. R0 is rejected only for a substantiated R0 defect. R1 implementation choices and R2/R3 evidence gaps may be recorded but cannot silently become R0 blockers.
