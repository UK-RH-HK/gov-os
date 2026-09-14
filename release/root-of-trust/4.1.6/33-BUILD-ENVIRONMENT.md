# Output 33 — The build environment as a first-hand-established input (BC5-2)

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> New in revision 6. It closes blocking class **BC5-2** (review r5 RV5-H2: the build environment selects the bytes of every
> production binary). It applies rule FD-1 (`29`) to the one byte-determining input whose content no party established.
> `30` §4.2, R-REG-3 (c), R-VER-1, R-REP-2 and §12 are amended to match. The residual common-mode environment is owner option
> **OP-16** (`21`; review r5 options E-a…E-c), with consequences computed by the derivation calculator (`evidence/r6/CS6-*`).
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Mistaken equivalence (revision 5):** *every input is named by digest ⇒ every input is legitimately selected.*

A reproduction quorum shows that independent parties obtained the same bytes from the same inputs. It cannot detect an input
that every reproducer is required to use. Revision 5 required every reproducer to fetch the one registered build image by
digest (R-REP-2). It checked that image only against "the owner's image record" (R-REG-3 (c)), and no rule named who produces
that record, from what, or under which authority. RV5-B-A08 showed the result with the real Rust toolchain: two reproducers
with a substituted C runtime object in the image produced bit-identical binaries that ran injected code. The toolchain was
unchanged. The quorum was met and no conflict arose.

Under FD-1 the image record was a **selector** (it decided which bytes every production binary has) with **no assigned
authority**. It could be produced by the release pipeline, rank 5.

## 2. Invariant

1. Every input that determines a binary's bytes has a registered selector whose content is established first-hand. Such
   inputs are the toolchain archive, the base environment, the linker, C runtime objects and system libraries. The only
   exception is an input the owner's OP-16 answer names as a residual, with computed minima (§6).
2. The pipeline selects none of these inputs, and produces no record that selects one.
3. A reproduction counts toward the faithful-build fact only under a registered environment. Its content is established by
   parties independent of the pipeline, and under OP-16 (b) by matching reproductions from environments that share no
   unestablished input.

## 3. The environment manifest

A **build environment** is a registered, digest-addressed input. Each environment of each registered target has an
**environment manifest** (`governance-os.environment-manifest/1`, published; digest `environment_id`):

| Field | Content |
|---|---|
| `components[]` | `{name, version, sha256, upstream_url, upstream_checksum_reference, supplier_class}`: every package, archive or object the environment contains (base system, linker driver, C runtime objects, system libraries) |
| `assembly` | `{recipe_digest, tool}`: the deterministic assembly recipe that turns the components into the environment tree (sorted, fixed timestamps and owners) |
| `environment_tree_digest` | SHA-256 of the assembled tree, computed as `30` §4.1 source identity v2 over the tree |
| `supplier_class` | `A`, `B`, …: the independent upstream from which every component was obtained (OP-16 (b)) |

The input manifest v2 (`30` §4.2) lists `environments[] {target, environment_id, environment_tree_digest, supplier_class}`.
`build_image_digest` is withdrawn.

## 4. Rules (R-BENV)

(`R-ENV-1`…`R-ENV-4` in `09` §7 are the environment-variable rules and are unrelated.)

| ID | Rule | Refusal |
|---|---|---|
| **R-BENV-1** | **Components pinned upstream.** Every component digest in an environment manifest MUST match a checksum signed by that component's upstream release. The registration ceremony (R-REG-3 (c′)) and every independent verifier (R-VER-1) check this themselves, as they already do for toolchain archives. A component with no upstream signed checksum is not admissible under OP-16 (a) or (b). Under (c) it is built by the owner (R-BENV-6). | `ENVIRONMENT_COMPONENT_UNVERIFIED` (ceremony, verifier) |
| **R-BENV-2** | **Environment established by a first-hand reproduction quorum.** At least two environment reproducers, holding `reproducer` keys and independent of the pipeline and of each other (TA-10′), assemble the environment from the pinned components with the registered recipe. Each signs one first-person `environment-reproduction.v1+json` statement `{environment_id, environment_tree_digest, reproduced_at}` with exactly one signature and confirms first-hand to the ceremony. The ceremony registers an environment only when at least two such reproductions agree on the tree digest. | `ENVIRONMENT_NOT_REPRODUCED` (ceremony); `ENVIRONMENT_REPRODUCTION_CONFLICT` when a valid reproduction of the same `environment_id` names another tree digest |
| **R-BENV-3** | **No pipeline record.** No image record produced or supplied by the pipeline is an input to any decision. The producer of the environment identity is the environment reproduction quorum; its authority is the registration (`29` DR-13). Revision 5's "owner's image record" of R-REG-3 (c) is withdrawn. | — |
| **R-BENV-4** | **Reproducers re-assemble.** A binary reproducer (R-REP-2) obtains each component by digest from any carrier and re-assembles the registered environment. Alternatively it obtains an environment by digest and verifies it by re-assembly. It refuses when any component or the tree digest differs. A `binary-reproduction` statement names its `environment_id`. | `INPUT_DIGEST_MISMATCH` (reproducer) |
| **R-BENV-5** | **Diversity under OP-16 (b).** The registration names at least two environments per target from distinct `supplier_class` values. Acceptance (AP-6) counts reproductions only under registered environments, and requires the quorum to include matching reproductions from at least two supplier classes. A target that does not reproduce bit for bit across the registered supplier classes cannot be registered under (b). | `ENVIRONMENT_DIVERSITY_NOT_MET` (verifier, ceremony) |
| **R-BENV-6** | **Owner-built environment under OP-16 (c).** Every component is built by the owner from upstream source. The environment is itself a registered, quorum-reproduced release (`30` §5, §7) whose source identity and inputs follow `30`. Its manifest names those registrations instead of upstream checksums. | as `30` |

**Verifier additions to admission-predicate/1** (`25` AP-6): a reproduction counts only when its `environment_id` is
registered for the target. Under OP-16 (b) R-BENV-5 applies. The TBM carries no environment field: environment identity is a
registration fact, not a binary claim.

## 5. What each party checks first-hand

| Party | Checks itself | Never takes from |
|---|---|---|
| Environment reproducer | component digests against upstream signed checksums; assembly with the registered recipe; the tree digest | the pipeline, a CI-built image, another reproducer |
| Registration custodian | upstream checksums of every component (R-REG-3 (c′)); at least two agreeing first-hand environment reproductions | an image record, the pipeline |
| Independent verifier | upstream checksums of toolchain and environment components (R-VER-1) | the ceremony's own check |
| Binary reproducer | re-assembly or verification by re-assembly (R-BENV-4) | a cached or mirrored image not re-assembled |
| Verifier (`gov`, `gov-admit`) | reproductions name a registered `environment_id`; diversity under (b) | the TBM |

## 6. OP-16 — Common-mode build environment (owner option; review r5 E-a…E-c)

Every answer keeps §4 R-BENV-1…R-BENV-4: components are pinned upstream and the environment is reproduced first-hand. The
answers differ in the common-mode residual that remains when the components themselves are malicious.

<!-- CS6:BEGIN OP-16-ENV -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| OP-16 | OP-9 | Minimal sets: malicious build environment (victim P1, OP-2 (a), OP-8 = 1) |
|---|---|---|
| a | n2q2 | {env_up_a}; {2 reproducer processes} |
| a | n3q2 | {env_up_a}; {3 reproducer processes} |
| b | n2q2 | {2 reproducer processes}; {1 reproducer process, env_up_b}; {1 reproducer process, env_up_a}; {env_up_a, env_up_b} |
| b | n3q2 | {1 reproducer process, env_up_a}; {env_up_a, env_up_b}; {3 reproducer processes}; {2 reproducer processes, env_up_b} |
| c | n2q2 | {owner_env}; {2 reproducer processes} |
| c | n3q2 | {owner_env}; {3 reproducer processes} |
<!-- CS6:END OP-16-ENV -->

Atoms: `env_up_a` is the class-A upstream environment supplier, and `env_up_b` the class-B supplier. `owner_env` is the
owner's environment build or its upstream sources. `rp1`…`rp3` are reproducer processes (they re-assemble the environment,
R-BENV-4).

| Answer | Trust added | Residual (computed above) | Operational cost |
|---|---|---|---|
| **(a)** accept the registered upstream components (TA-12′) | the upstream component suppliers of the one class used | a compromised upstream component that passes its checksum check yields identical malicious bytes from every reproducer; otherwise the reproducer quorum | component pinning and upstream checksum checks by ceremony and verifiers; two first-hand environment reproductions per environment change |
| **(b)** environment diversity | the suppliers of every class used, jointly | compromise of every supplier class used, or one supplier with the reproducers of the other class | static or self-contained linking and per-target engineering so that a target reproduces bit for bit across supplier classes; longer builds; **a target that does not reproduce across classes cannot be registered** (`ENVIRONMENT_DIVERSITY_NOT_MET`); at least one reproducer per class |
| **(c)** owner-built environment | the owner's environment build and its upstream sources | compromise of the owner's environment build or its upstream sources | highest engineering and maintenance cost: a registered and reproduced environment release per change |

OP-16 is independent of OP-10, which covers the toolchain archive. Their residuals add: `21` states the combinations.

## 7. Minimal-set claims and invariants (computed)

The calculator (`evidence/r6/CS6-derivation-calculator.py`, goal `G_ENV`) models the environment as a selector with
strategies for every environment substitution: a pipeline-produced record (rule `H_REG_ENV_QUORUM` off), a component not
re-assembled by reproducers (`H_REP_ENV_REASSEMBLE` off), an unverified upstream component (`H_VER_UPSTREAM`,
`H_REG_UPSTREAM` off), and diversity not enforced (`V_ENV_DIVERSITY` off). Invariants, checked over every configuration:
- **INV-ENV.** Every minimal set contains one of: an OP-16 residual atom; at least q reproducer compromises; or the
  registration threshold with OP-8 verification compromises.
- **INV-ENV-PIPELINE.** Pipeline, infrastructure and the trust-state key never select the environment, alone or together.
- **INV-ENV-B.** Under (b), no minimal set holds a single supplier compromise without a second supplier or a reproducer of
  the other class.

Result: 0 failures (`22` §1).
Control (review r5, revision-5 rule profile `R5`): {pipeline} and {cust1, cust2, …} again select the environment, as review r5 found.

## 8. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-S2′ (TA-12′) | A malicious upstream environment component that passes its signed checksum (OP-16 (a)); every supplier class used (b); the owner's environment build (c) | §6 minimal sets; OP-16 | CS6 `G_ENV`; ENV6 E4, E6 |
| TB-S1 (environment) | Environment reproducers at the quorum compromised together | registration refuses a conflict with any honest reproducer (R-BENV-2) | ENV6 E8a, E8b |
| TB-S3 | Environment reproducers under common custody | procedural; ceremony record (CR5-B-02) | — |

## 9. Evidence (`evidence/r6/ENV6-build-environment.{py,json}`; executed)

The probe uses the real Rust toolchain (`rustc 1.98.1`) and system C compiler. Components are signed by Ed25519
upstream-checksum keys and builds use reviewer B's normative flags. Two runs are bit-identical.

| Case | Construction | Result |
|---|---|---|
| E0 | honest components, OP-16 (a) | registered; two reproducers bit-identical; `ACCEPTED` |
| E1 | revision-5 shape: the pipeline supplies the image digest; independent environment reproduction yields another tree | `ENVIRONMENT_NOT_REPRODUCED` (the injected binary runs when built with the pipeline image; revision 5 would register it) |
| E2 | one component substituted (`bin/cc` with the injected object), its checksum not signed upstream | `ENVIRONMENT_COMPONENT_UNVERIFIED` at the ceremony |
| E3 | a carrier substitutes the component after registration | `INPUT_DIGEST_MISMATCH` at the reproducer |
| E4 | the class-A upstream supplier itself compromised, OP-16 (a) | `ACCEPTED`, injected code runs: the stated residual (a) |
| E5 | class A compromised, class B clean, OP-16 (b) | `REPRODUCTION_CONFLICT` |
| E6 | both classes compromised, OP-16 (b) | `ACCEPTED`, injected: the stated residual (b) |
| E7 | both classes clean, OP-16 (b) | `ACCEPTED`, bit-identical across classes |
| E8a / E8b | one or both environment reproducers compromised | `ENVIRONMENT_REPRODUCTION_CONFLICT` / registered (TB-S1 residual) |
| E9 | OP-16 (b) with reproductions from one class only | `ENVIRONMENT_DIVERSITY_NOT_MET` |

The probe was written by a helper session under this architect's specification. It follows reviewer B's
`RV5-B-A08-build-image-selects-bytes.py` for image construction and flags (`22` §1 states the attribution).
