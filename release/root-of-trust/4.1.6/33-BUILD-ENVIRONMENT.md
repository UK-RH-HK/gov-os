# Output 33 — Build environments and toolchains of CP-1: derived manifests, provenance-independent suppliers and lineages (BC6-3)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Rewritten in revision 7 for the certified profile CP-1 (`35`). It closes blocking class **BC6-3** (review r6 RV6-H3: no party
> establishes the environment manifest; its author selects every production binary's bytes) and carries RV6-L3 and RV6-L4. It
> applies the owner requirements OP-16 (b), OP-10 (b), OP-9 (b) + (d) and "Build-environment manifest author/signer"
> (OWNER-DESIGN-REQUIREMENTS-0001). The unselected answers are excluded (EX-15, EX-21); revision 6's authored manifest (recipe,
> tool, key reference, supplier label) is withdrawn; history at `4106885`.
> Amended to match: `30` §4.2, R-REG-3 (c″), R-VER-1, R-REP-2, R-REP-9; `25` AP-6. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Mistaken equivalence (revision 6):** *reproduced from the manifest by independent parties ⇒ the manifest was legitimately
selected.* Revision 6 required a reproduction quorum over an environment manifest whose component selection, placement, recipe,
assembly tool, upstream key reference and supplier-class label no rule assigned to any party. Review r6 (B-A02 A07a/b/c, A08,
A09) showed with the real toolchain that an author of that manifest, in a conforming process, selects the bytes of every
production binary, and that two labels over one supplier satisfy "diversity".

## 2. Invariant (CP-1)

1. Every byte-determining fact of an environment is established at the registration's authority, with a stated establishing
   party: component selection and placement come from registered source (the environment lock); component bytes verify under
   keys pinned at the root threshold; assembly is a fixed function with no free content.
2. The environment manifest has **no author**. It is derived deterministically, and it is authoritative for a release only when
   independent environment reproductions agree with it **and** the 2-of-3 registration names that exact identity.
3. The pipeline selects none of these facts and produces no record that selects one.
4. Supplier-class and toolchain-lineage independence are computed from provenance registered at the root threshold, never
   from labels, filenames or mirrors.

## 3. The environment lock (registered source)

`governance-os.environment-lock/1` (`schemas/environment-lock.schema.json`) is a file of the product's release source tree
(`build/ENVIRONMENT_LOCK.json`). Its digest is `environment_lock_digest` in the input manifest v3 and in the release
registration.

| Field | Content |
|---|---|
| `environments[]` | `{target, supplier_id, components[]}` |
| `components[]` | `{name, version, sha256, placement_path, mode}` and nothing else: no inline content, no scripts, no URLs, no key references (`additionalProperties: false`) |

The lock is changed only by a source change. Source changes are reviewed under OP-8 verification, and the registration
selects source (`30` §5), so the lock's establishing party is the registration authority restricted by two verification records.

## 4. The derived environment manifest

`gov-envmanifest/1` is a normative function of the admitted `gov` (and of the registered checker):

- **Inputs.** One lock entry; the supplier registry of the root-signed Trust Policy (`supply_chain.suppliers[]`); each
  component's upstream signed checksum file, obtained by any carrier.
- **Checks.** Each component's `sha256` appears in a checksum file that verifies under one of `checksum_keys` of the entry's
  `supplier_id`.
- **Output.** `governance-os.environment-manifest/2`: `{target, supplier_id, lock_digest, components[] {name, version, sha256,
  placement_path, mode, checksum_key_id, checksum_file_digest}, assembly_function: "gov-envassemble/1", environment_tree_digest}`.
  `environment_id` is the digest of the canonical manifest.

`gov-envassemble/1` places each component's bytes at `placement_path` with `mode`, fixed owner and timestamps, in sorted order.
The tree digest is the source identity v2 of the tree (`30` §4.1). There is no recipe, no tool choice and no free content.

## 5. Rules (R-BENV, revision 7)

(`R-ENV-1`…`R-ENV-4` in `09` §7 are the environment-variable rules and are unrelated.)

| ID | Rule | Refusal |
|---|---|---|
| **R-BENV-1″** | **Supplier registry pinned at root threshold.** The Trust Policy lists each supplier `{supplier_id, provenance {base_image_lineage, package_source, build_system, signing_infrastructure}, checksum_keys[]}`. A component verifies only under a key of its own supplier's entry. A key named anywhere else, in a manifest, a lock or a pipeline record, is never a selector. | `ENVIRONMENT_COMPONENT_UNVERIFIED` |
| **R-BENV-2″** | **Selection in source.** Component selection, versions, digests, placement and mode come only from the environment lock of the registered source. A lock carrying content, scripts or key references is not a lock. | `ENVIRONMENT_ASSEMBLY_NONCONFORMANT` |
| **R-BENV-3″** | **Derived, never authored.** Every party that uses a manifest (environment reproducers, custodians, verifiers, reproducers) recomputes it with `gov-envmanifest/1` from the registered lock and the pinned registry. A manifest that differs from the derivation is refused. No pipeline-supplied manifest or image record is an input to any decision. | `ENVIRONMENT_MANIFEST_NOT_DERIVED` |
| **R-BENV-4″** | **Fixed assembly; reproducers re-assemble.** Environments are assembled only by `gov-envassemble/1`. A binary reproducer obtains each component by digest from any carrier and re-assembles; a component or tree digest that differs refuses. A `binary-reproduction` statement names its `environment_id` and `toolchain_id`. | `ENVIRONMENT_ASSEMBLY_NONCONFORMANT` / `INPUT_DIGEST_MISMATCH` |
| **R-BENV-5″** | **Supplier-class independence by provenance (OP-16 (b)).** Two suppliers are independent only when all four provenance attributes differ, their checksum key sets are disjoint, and their locks share no component digest. The registration names at least two environments per target from independent suppliers. Acceptance (AP-6) requires matching reproductions under at least two independent supplier classes. A target that does not reproduce bit for bit across them is not certified (CC-2). | `ENVIRONMENT_DIVERSITY_NOT_MET` |
| **R-BENV-6″** | **Toolchain lineages (OP-10 (b)).** The Trust Policy lists each toolchain `{toolchain_id, provenance {bootstrap_root, package_source, build_system, signing_infrastructure}, archive_sha256 or bootstrap_registration}`. Two lineages are independent only when all four attributes differ. At least one lineage's `bootstrap_root` is not an upstream binary compiler archive, and its compiler is itself a registered, reproduced bootstrap release. Acceptance requires matching reproductions from at least two independent lineages. A target without them is not certified (CC-3); there is no fallback to an upstream archive alone (EX-15). | `TOOLCHAIN_DIVERSITY_NOT_MET` |
| **R-BENV-7″** | **Authority of an environment identity.** An environment is authoritative for release R only when (1) at least two environment reproductions, each by a distinct `reproducer` key with one signature, first-hand and independent of the pipeline, assemble the derived manifest and agree on its tree digest; and (2) the 2-of-3 registration of R lists that exact `environment_id` with those reproductions. | `ENVIRONMENT_NOT_REPRODUCED` / `ENVIRONMENT_REPRODUCTION_CONFLICT` |
| **R-BENV-8** | **Verification environment (RV6-L3, CR6-B-06).** Before registration, verifiers derive the environments from the lock of the candidate's source (R-BENV-3″) and build there. Verification attestations name the `environment_ids` and `toolchain_ids` they reproduced in. An attestation that does not name the registered environments is not counted. | not counted (`VERIFICATION_RECORDS_BELOW_MINIMUM`) |
| **R-BENV-9** | **Derivation-tool provenance (RV6-L4, CR6-B-07).** `gov-envmanifest/1`, `gov-envassemble/1` and the R-CON-1 content derivation run only from an admitted `gov` or from a build of the registered source made by the party itself. A ceremony record naming a pipeline-supplied tool digest is refused. | `DERIVATION_TOOL_UNREGISTERED` (specification; RT-186) |

## 6. What each party checks first-hand

| Party | Checks itself | Never takes from |
|---|---|---|
| Environment reproducer | derivation of the manifest from the registered lock and pinned registry; component checksums under pinned keys; assembly; the tree digest | the pipeline, a CI image, another reproducer, a manifest it did not derive |
| Registration custodian | the same derivation; at least two agreeing environment reproductions; supplier and lineage independence from the registry | an image record, the pipeline |
| Independent verifier | derivation and assembly for the candidate's source before registration (R-BENV-8) | the ceremony's own check |
| Binary reproducer | re-assembly from components by digest; the registered toolchain lineage | a cached or mirrored environment not re-assembled |
| Verifier (`gov`, `gov-admit`) | reproductions name registered environments and toolchains; independent classes and lineages by registered provenance | labels, the TBM |

Computed consequences for CP-1 (victim P1 for both; FA for the environment):

<!-- CS7:BEGIN CP-ENV -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| Victim | Minimal sets: malicious build environment (CP-1, two independent supplier classes) |
|---|---|
| P1 | {env_common}; {env_up_a, env_up_b}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 3 reproducer processes}; {2 registration custodians, 2 verification keys, 2 reproducer processes}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck} |
| FA | {env_common}; {env_up_a, env_up_b}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 3 reproducer processes}; {2 registration custodians, 2 verification keys, 2 reproducer processes}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck}; {2 registration custodians, 1 reproducer key, 2 trust-state keys, env_up_a, fcpub}; {2 registration custodians, 1 reproducer key, 2 trust-state keys, env_up_b, fcpub}; {2 registration keys, 2 reproducer keys, 2 trust-state keys, fcpub} |
<!-- CS7:END CP-ENV -->

<!-- CS7:BEGIN CP-TOOLCHAIN -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| Victim | Minimal sets: compromised toolchain (CP-1, two independent lineages) |
|---|---|
| P1 | {tc_src}; {toolchain_up, diverse_tc}; {2 registration custodians, 3 reproducer processes} |
<!-- CS7:END CP-TOOLCHAIN -->

Atoms: `env_up_a`, `env_up_b` are the two supplier classes compromised (TA-12′). `env_common` is hidden common provenance between
the registered classes (TA-12″). `toolchain_up` is the upstream binary toolchain lineage compromised, `diverse_tc` the
independently bootstrapped lineage, and `tc_src` the compiler source common to every lineage (TA-12″).

## 7. Invariants (computed)

The calculator (`evidence/r7/CS7-derivation-calculator.py`, goals `G_ENV`, `G_TOOLCHAIN`) models the environment with rules
`H_ENV_LOCK_IN_SOURCE`, `V_SUPPLIER_PINNED_KEYS`, `V_SUPPLIER_PROVENANCE`, `V_ENV_DIVERSITY`, `H_REG_ENV_QUORUM`,
`H_REP_ENV_REASSEMBLE` and `V_TOOLCHAIN_DIVERSITY`:
- **INV7-ENV.** Every minimal set contains both supplier classes, hidden common provenance, a supplier with a reproducer
  compromise, two reproducer compromises, or source selection (the registration threshold with two verification compromises, or
  the pipeline with two verification processes).
- **INV7-ENV-PIPELINE.** The pipeline, infrastructure, trust-state and release keys never select the environment.
- **INV7-ENV-B.** No minimal set holds one supplier class without the other class, a reproducer compromise or hidden common
  provenance.
- **INV7-TC.** No minimal set holds one toolchain lineage without the other lineage, a reproducer compromise or the compiler
  source.

The revision-6 rule shapes (manifest authored, label diversity, manifest-named keys) survive only as the labelled non-production
control, where the pipeline selects the environment again (CP-R6-CONTROLS, `28` §12).

## 8. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-S2″ (TA-12′, TA-12″) | Both supplier classes compromised together, or hidden common provenance between them that the registry does not show | CP-ENV block | ENV7 A08 control; RT-186 |
| TA-12″ (toolchain) | Both toolchain lineages compromised, or the compiler source | CP-TOOLCHAIN block | ENV7 T3; RT-187 |
| TB-S1 (environment) | Environment reproducers at the quorum compromised together | registration refuses a conflict with any honest reproducer (R-BENV-7″) | ENV7 T1, control rows |
| TB-4 / TB-4′ (lock) | A lock change accepted by honest verification (insider), or by two verification processes with the pipeline | the source route of `30` §10 (CP-SRC) | ENV7 A07b source-authority control |
| OT-2 | No evidenced independent bootstrap lineage for the current compiler | no target certified until CC-3 holds (`35` §6) | — |

## 9. Evidence (`evidence/r7/ENV7-environment-authority.{py,json}`; executed with the real Rust toolchain `rustc 1.98.1`)

| Case | Construction | Result |
|---|---|---|
| E0 | honest lock, both supplier classes, both lineages | registered in both classes; 8 builds bit-identical; `ACCEPTED` |
| A07a | a lock carrying inline component content; a pipeline-supplied manifest carrying an injected object | `ENVIRONMENT_ASSEMBLY_NONCONFORMANT`; `ENVIRONMENT_MANIFEST_NOT_DERIVED` |
| A07b | a pipeline manifest selecting instrumented artefacts | `ENVIRONMENT_MANIFEST_NOT_DERIVED`; control: the same selection made by a lock change in reviewed source is registered and accepted, which is the TB-4/TB-4′ source route, not the pipeline |
| A07c | the same injection offered for both classes | `ENVIRONMENT_MANIFEST_NOT_DERIVED` twice |
| A08 | two labels over one compromised supplier | `ENVIRONMENT_DIVERSITY_NOT_MET`; control (label counting): accepted with injected code |
| A09 | a checksum key named by the manifest | `ENVIRONMENT_COMPONENT_UNVERIFIED`; control (revision-6 shape): registered |
| T1 | the upstream binary lineage compromised, the bootstrapped lineage honest | `REPRODUCTION_CONFLICT` |
| T2 | the second lineage is the upstream lineage relabelled | `TOOLCHAIN_DIVERSITY_NOT_MET`; control (label counting): accepted with injected code |
| T3 | both lineages compromised | `ACCEPTED`, injected: the stated residual |
| control | one compromised class with an independent honest class | `REPRODUCTION_CONFLICT` |

ENV7 also recomputes `G_ENV` for victims P1, FA and CIR with the CP-1 rules on (the pipeline is never minimal and the invariants
hold) and with each of `H_ENV_LOCK_IN_SOURCE`, `V_SUPPLIER_PINNED_KEYS` and `V_SUPPLIER_PROVENANCE` off (each is load-bearing).
The toolchain provenance of T1–T3 is modelled: the lineages are distinct toolchain identities built with `rustc 1.98.1` under
distinct registered provenance, not a diverse double-compilation of the compiler itself (OT-2).
