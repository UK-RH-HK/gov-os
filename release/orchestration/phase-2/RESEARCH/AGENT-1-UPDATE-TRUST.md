# Research Agent 1 — secure update and release trust (Level 1)

**Scope**: does mature prior art establish, better than Governance OS's own custom mechanism, that the software/runtime
being installed and executed is the authentic authorised version? Read-only research; no product code touched.

**Primary source examined**: Governance OS's own accepted Level-1 architecture — the Signed Release Root
(`SRR-1` / `ARCH-0003`), R0-accepted (`AR-0025`) and R1-accepted with zero blocking findings (`AR-0033`,
`srr1-r1-accepted`, commit `c7d3fef`) — read directly from `release/root-of-trust/signed-release-root-v1/`,
`release/root-of-trust/signed-release-root-v1-r1-build/00-BUILD-REPORT.md`, and `runtime/src/srr/{crypto,metadata,
staging,state,verifier,installation,breakglass}.rs`. Also examined the retired `CP-1`/`RoT-1` lineage (7 rejected
revisions, `release/root-of-trust/4.1.6*`, memory notes `governance-os-root-of-trust-escalation.md` and its two review
notes) as evidence of *which failure classes a hand-rolled version of this problem actually produces*.

---

## 1. What Governance OS already has, and where it came from

The accepted SRR-1 design (`00-ARCHITECTURE.md`) is, explicitly and by its own comments, a hand-written
implementation of **The Update Framework's role model**, not TUF itself:

- Four metadata roles — `root` (keys/thresholds/delegations/rotation), `release`/`targets`-equivalent (exact
  release identity and payload digests), `snapshot` (one consistent metadata-version set), `timestamp` (bounded
  freshness) — plus a fifth, GovOS-specific `recovery` role for below-floor break-glass.
- Threshold Ed25519 signatures (`ed25519-dalek` 2.x, `verify_strict` only — the permissive verifier that accepts
  small-order/non-canonical signatures was deliberately removed from every call path, `AR27-N4`).
- A TUF-style **root-rotation protocol implemented by hand**: a new root is accepted only if signed by a threshold
  of the *outgoing* root **and** a threshold of its *own* incoming root (`runtime/src/srr/metadata.rs:467-470`),
  which is materially the same two-threshold succession rule as TUF's root-update procedure.
- Monotonic **high-water marks** kept in durable local machine state, separate from the signed metadata: one per
  metadata role (`metadata_high_water`, pure anti-replay) and one for the release itself
  (`release_high_water_version`/`_sequence`, anti-rollback) — `runtime/src/srr/state.rs:374-529`.
- A **verify-then-install transaction** (`runtime/src/srr/staging.rs`) that copies candidate bytes into private
  staging first, measures only the staged copy, re-measures immediately before the atomic rename
  (`confirm_unchanged`), performs the install as a journalled atomic swap (`dest.srr-new` → rename → `dest`,
  previous kept as `dest.srr-old` until a post-swap re-hash confirms the committed tree matches the verified
  measurement), and advances the high-water mark **only after** that re-verification succeeds — deliberately, so a
  crash before commit cannot leave the machine below its own floor.
- Explicit, written non-guarantees: no trusted-time source, no hostile-local-administrator protection, no toolchain
  correctness claim, honest `STALE`/`UNKNOWN` currency reporting against the local clock when no fresher metadata
  has been received.

One deliberate, well-reasoned decision to **not** reimplement something: signatures cover **the raw bytes of the
`signed` JSON member exactly as they appear on disk**, extracted with `serde_json::value::RawValue`
(`runtime/src/srr/metadata.rs:12-20`), specifically *to avoid writing a canonical-JSON (JCS) encoder* — the comment
names encoder-disagreement as "a classic source of signature-bypass bugs." This is the right call and it is the one
place in this subsystem that already reflects the brief's own instruction ("be conservative about `BUILD CUSTOM`").
Notably, the now-retired CP-1/`RoT-1` lineage *did* build a hand-rolled DSSE/JCS canonicalizer — the SRR-1 team
changed approach after that lineage was frozen, which is direct in-repo evidence that avoiding a canonicalization
step is a lesson already learned once, expensively, and should not be relearned.

**The one library evaluation on record** (`00-BUILD-REPORT.md` §1): the R1 builder considered `tough`
(AWS Labs' Rust TUF client, used in production by Bottlerocket) and rejected it, reasoning that GovOS's
release/targets record needs typed, first-class fields — product identity, channel, monotonic sequence,
kernel/CLI payload digests, schema identity, migration identity, minimum secure release — and that expressing
those through a generic client's `custom` metadata escape hatch "would have hidden the bindings this gate is
about." I find this reasoning **partially, not fully, justified** — see §3.

### What seven rejected revisions of the retired lineage actually found

Before SRR-1, a separate architecture (`CP-1`/`RoT-1`, `spec/decisions/D-0008.yaml`) went through **seven** revisions,
each independently reviewed and rejected. Reading the four review-cycle memory notes together, the HIGH findings are,
almost bullet-for-bullet, TUF's own named attack classes, being rediscovered by hand:

| Rejected-revision finding | TUF/mature-primitive name for the same class |
|---|---|
| RV-H1 "no use-time currency floor... an old authenticated kernel becomes the policy root" | rollback attack (no persisted trusted floor) |
| RV-H2 "certification/revocation facts can be omitted or replayed stale" | freeze / indefinite-freeze attack (no bounded, monotonic freshness) |
| RV-H3 "use-time TOCTOU: an inotify racer swapped `SECURITY_POLICY` 0.11ms after verification" | verify/use race — see §4 |
| RV-H4 "legacy-identity statement signed by the certification role, not restricted to T0" | role-confusion / insufficient role separation |
| R2-H1 "64 of 125 leaves unfloored" | incomplete target coverage under a single signed root |
| R2-H2 "a stateless verifier takes its currency from whatever the repository writer leaves... gate records are forgeable" | no persisted local trust state / mix-and-match attack |
| R2-H3 "`artifact-final` signed under threshold-1... one key forges the TCB" | threshold role compromise (single point of failure where multi-sig was claimed) |
| R2-H4 "`update --rollback`/`init --force` rewrite a RoT-1 project... report verified" | rollback attack via an alternate ingress path |

This is the strongest evidence available for the brief's central claim that GovOS's custom mechanisms keep
re-deriving problems mature protocols already solved: the same organisation spent roughly three days and seven
review cycles independently rediscovering TUF's rollback-attack, freeze-attack, mix-and-match-attack and
role-separation requirements one HIGH finding at a time, by hand, before abandoning that lineage and starting over
on a design (SRR-1) that finally mirrors TUF's structure more faithfully — and passed R0/R1 on that basis.

---

## 2. Candidate assessment

Each candidate below is recorded against the brief's §5 fields, compressed to what is decision-relevant for a
**single owner, private, offline-capable, WSL2** deployment.

### 2.1 TUF (The Update Framework) — the specification itself

- **Property provided**: resistance to a named, enumerated attack list — arbitrary-software, rollback, freeze/
  indefinite-freeze, endless-data, extraneous-dependencies, mix-and-match, slow-retrieval, wrong-software-install,
  malicious-mirror attacks — via role separation (root/targets/snapshot/timestamp), signature thresholds, monotonic
  version numbers, and a mandated client workflow (persist trusted metadata locally; never accept a version older
  than the locally trusted one; check thresholds; check expiry against the *client's* clock).
  Source: [TUF specification, latest](https://theupdateframework.github.io/specification/latest/); rollback/freeze
  protocol detail via [`theupdateframework/specification` GitHub, `tuf-spec.md`](https://github.com/theupdateframework/specification/blob/master/tuf-spec.md).
- **Property NOT provided**: build honesty (that the release was built correctly from the claimed source — that's
  SLSA/in-toto's job), execution-time byte binding (verify happens at metadata/target-file level, before install;
  TUF says nothing about what happens between "installed" and "executed" — see §4), and it does not itself supply a
  trusted-time source; the *timestamp* role's freshness guarantee is only as good as an online, frequently-rotated
  signing key, which an offline profile does not have (GovOS's own architecture doc says this explicitly and
  substitutes a durable local high-water mark instead — the correct offline adaptation).
- **Maturity / maintenance**: IEEE-ISTO-hosted specification, versioned (current spec `v1.0`+ family), used in
  production by many ecosystems (PyPI's PEP 458/480 work, Docker Notary v2/Cloud Native lineage, container/OS
  update systems, Sigstore's own trust-root distribution — see §2.3).
- **Licence**: specification is open (Apache-2.0-family docs); reference/most client implementations are
  Apache-2.0 or MIT.
- **Works offline / local**: yes — this is TUF's core design case (a client with a local trusted metadata cache and
  no assumption of a reachable transparency log).
- **Requires cloud / root**: no cloud requirement; no root privilege requirement inherent to the spec (GovOS already
  runs its verifier unprivileged and only escalates for the actual install).
- **WSL2**: not applicable — a specification, not a binary.
- **Classification**: **ADAPT THE PATTERN**, already adopted at the architecture level. GovOS's SRR-1 role model,
  threshold logic, and monotonic-high-water design are TUF-shaped by design and that is correct. What is *not*
  correct is re-deriving TUF's client-side edge cases (root rotation, threshold counting, rollback comparison,
  expiry-vs-clock handling) by hand when a conformant, audited library already implements exactly those edge cases
  — see `tough` below.

### 2.2 `tough` (AWS Labs, Rust TUF client) — the specific rejected-library decision

- **What it is**: a Rust implementation of a TUF client (root/targets/snapshot/timestamp workflow, delegations,
  local-repository support), maintained by AWS Labs and used in production inside Bottlerocket OS's own update
  system — itself a single/few-machine, security-conscious, non-multi-tenant OTA use case, structurally close to
  GovOS's deployment profile.
- **Maintenance status**: actively maintained — latest release (`0.22.0`) within the last ~5 months of this
  research date, 35 published versions, ~473k all-time downloads, ~58k weekly downloads, healthy release cadence.
  Companion crates `tough-kms`/`tough-ssm` for signing, `tuftool` for offline repository authoring.
  Source: [crates.io/crates/tough](https://crates.io/crates/tough/0.22.0), [crates.io/crates/tuftool](https://crates.io/crates/tuftool/0.15.0).
- **Licence**: Apache-2.0 / MIT dual (standard AWS Labs Rust crate licensing).
- **Works offline / local**: yes — `tough` explicitly supports a purely local, filesystem-backed repository with no
  network dependency, which is precisely how `tuftool` is used to author air-gapped update repositories.
- **Requires cloud / root**: no.
- **WSL2**: pure Rust, no platform-specific dependency beyond the standard toolchain GovOS already builds with —
  no reason to expect an issue, though I did not build and run it in this WSL2 environment to confirm (see §7).
- **Re-examining the R1 builder's rejection**: the stated reason ("typed release-specific bindings would be hidden
  in a generic `custom` field") is a real cost, but it is a cost of using `tough` for the **whole** metadata model,
  not a reason to hand-write **all of it**. The generic, security-critical, easy-to-get-wrong parts of TUF —
  threshold counting, root-rotation succession, rollback/version comparison, expiry-vs-clock handling, delegation
  graph walking — are exactly the parts `tough` has already had adversarial review and production use behind it,
  and are exactly the parts the retired `CP-1`/`RoT-1` lineage got wrong seven times (§1 table). The
  GovOS-specific part — schema identity, migration identity, minimum secure release, kernel/CLI digest bindings —
  is naturally expressed as a **signed custom target** whose *authority* still comes from a `tough`-verified
  targets/snapshot/timestamp chain, with GovOS's own schema validated *after* `tough` has already established that
  the bytes are authorised and at-or-above the required version. That is a `custom` field used for **payload**, not
  for **authority** — the builder's stated objection does not actually apply to that split.
- **Classification**: **WRAP** (partially superseding the current **BUILD CUSTOM** choice). Delegate root/snapshot/
  timestamp verification, threshold logic and rollback/freeze comparison to `tough`; keep GovOS's own typed
  release-payload semantics and the `recovery`/break-glass role (which has no TUF equivalent and is genuinely
  product-specific) as custom code layered on top of an already-authorised target. This directly reduces the
  custom-code surface that produced RV-H1/RV-H2/R2-H1/R2-H2/R2-H3 in the retired lineage.
- **What I could not determine**: whether `tough`'s delegation model is expressive enough for GovOS's plugin/
  retrieval delegation use case (`spec` mentions delegated signed targets for "remotely acquired privileged
  plugin/tool/profile," `runtime/src/srr/metadata.rs:566-598`) without modification. This needs a spike, not a
  literature read.

### 2.3 Sigstore (cosign, Fulcio, Rekor) — keyless signing and transparency

- **Property provided (keyless mode)**: identity-bound signing without long-lived private keys — Fulcio issues a
  short-lived certificate binding an ephemeral signing key to an OIDC identity, and Rekor timestamps the signing
  event in a public, append-only transparency log so a signature's existence (and, with monitoring, any
  unauthorised additional signature) is publicly auditable.
- **Property NOT provided offline**: everything that makes keyless signing valuable. Signing requires reaching an
  OIDC provider and Fulcio; verification by default requires reaching Rekor to confirm log inclusion, and requires
  fetching Sigstore's own trust root **via TUF** from `tuf-repo-cdn.sigstore.dev` (refreshed on every verification
  unless a local trust-root file is pinned).
  Source: [Chainguard Academy — Verifying signatures in air-gapped environments](https://edu.chainguard.dev/open-source/sigstore/cosign/verifying-in-air-gapped-environments/).
  Cosign does support `--offline` verification against a locally bundled Rekor inclusion proof, and
  `--tlog-upload=false` for signing without reaching Rekor, but the second option is documented as giving up the
  transparency guarantee that is Sigstore's actual value proposition (same source).
- **A load-bearing observation for this study**: Sigstore's own root-of-trust distribution mechanism *is TUF*. The
  thing GovOS is trying to build (a small, signed, versioned root of trust reachable without a live CA) is
  literally the layer Sigstore itself sits on top of. This reinforces that TUF, not Sigstore, is the correct
  Level-1 foundation for an offline single-owner profile.
- **Non-keyless mode**: `cosign` also supports classical key-pair signing (`cosign generate-key-pair`,
  `cosign sign --key`, local public-key verification) with no Fulcio/Rekor dependency at all. This mode works fully
  offline, but at that point it is providing nothing beyond what GovOS's existing `ed25519-dalek`-based signing
  already provides — it would be adopting Sigstore's *tooling and file conventions* (the DSSE/in-toto attestation
  envelope shape, `cosign`'s bundle format), not its distinguishing security property.
- **Verdict on the brief's direct question**: Sigstore's keyless flow **does not fit** this deployment profile. It
  is architected around an online CA and a public/monitored transparency log; a private, single-owner, offline
  machine has neither the infrastructure nor (for a private repository) the threat model — a public transparency
  log's value is *detecting* an attacker who obtained your signing capability by watching for signatures you didn't
  make, which presumes other parties are watching a log you'd notice being tampered with. In a single-owner setting
  there is no "other party" to notice.
- **Classification**: **NOT APPLICABLE (keyless)** for R1/R2 under this profile; **HIGH-ASSURANCE ONLY** if a future
  posture adds a public/multi-party transparency requirement (out of scope per the brief's Level-3 boundary). The
  **in-toto attestation envelope shape** Sigstore uses (DSSE, typed `Statement`/predicate) is separable and worth
  considering independent of Fulcio/Rekor — see §2.4.

### 2.4 in-toto / SLSA — attestation framework and build-provenance levels

- **Relationship**: SLSA (Supply-chain Levels for Software Artifacts) defines *what* provenance must say; in-toto
  defines the *attestation format* (a signed `Statement` predicate) used to say it. SLSA v1.0 (April, superseding
  v0.1) narrowed scope to a Build track with levels 0–3; later work (referenced as v1.2 in current material) adds a
  Source track. Source: [SLSA blog — in-toto and SLSA](https://slsa.dev/blog/2023/05/in-toto-and-slsa),
  [SLSA v1.1 FAQ](https://slsa.dev/spec/v1.1/faq).
- **Property provided**: a standard, machine-checkable shape for "who built this, from what source, with what
  builder, under what trusted control" — closing the gap between "this artefact is authentic" (TUF's job) and "this
  artefact was honestly built" (SLSA/in-toto's job). GovOS's own trust-domain table already names this distinction
  ("Build provenance | signed attestations bound by digest | records source/inputs/builder evidence | not the
  client distribution root" — `00-ARCHITECTURE.md`), which shows the architecture already knows this is a separate
  concern from release distribution; it has not yet been built.
- **Property NOT provided**: distribution/rollback/freshness (that's TUF's job, not in-toto/SLSA's); nor does it
  say anything about the verify/use gap at execution time.
- **Works offline**: yes — an in-toto attestation is just a signed statement; verifying it needs only the public
  key and the statement, no online service. SLSA's higher build levels (hermetic, reproducible builds under a
  trusted build platform) are a *build-time* requirement on the build environment, not a distribution-time online
  dependency.
- **Fit**: since GovOS's release process is presumably a single owner building on their own machine today, a full
  SLSA Build L3 (isolated, non-falsifiable build platform) is disproportionate; but adopting the **in-toto Statement
  format** for the existing "evidence digests" field the release/targets record already has room for
  (`00-ARCHITECTURE.md` "Metadata roles" table: "optional evidence digests") costs little and gives a standard,
  independently-parseable provenance record instead of an ad hoc one.
- **Classification**: **ADAPT THE PATTERN** (attestation *shape*) now; **USEFUL LATER** for actual SLSA build-level
  qualification once there is more than one machine/builder in the picture.

### 2.5 Package-manager trust models — apt/dpkg, RPM, Cargo, npm

- **apt/dpkg (`apt-secure`)**: a signed `Release`/`InRelease` file lists SHA-256 hashes of the package-index files,
  which list hashes of the `.deb` files; trust reduces to the keys in `/etc/apt/trusted.gpg`. This authenticates
  *that the archive maintainer approved these bytes*; it explicitly does **not** defend against compromise of the
  signing key/master server itself, and, critically for this study, **has no TUF-style role separation or
  monotonic-rollback protection by default** — an attacker who can present an *older, validly-signed* `Release`
  file to a client can roll it back unless the client separately tracks `Valid-Until`/staleness. This is precisely
  the rollback-attack class TUF's role/version model exists to close and apt's flat single-key model does not.
  Source: [Debian `apt-secure(8)`](https://manpages.debian.org/testing/apt/apt-secure.8.en.html),
  [Debian wiki `SecureApt`](https://wiki.debian.org/SecureApt).
- **RPM/dnf**: structurally similar (GPG-signed repo metadata plus per-package signatures); I did not independently
  re-verify RPM's current rollback posture for this report and note it only as "same generation of trust model as
  apt," not as a distinct data point — treat this line as lower-confidence than the apt line above.
- **Cargo/crates.io**: as of this research, crates.io does **not** have package/index signing in production; a
  Sigstore-based signing proposal exists only as internals-forum discussion, not a shipped mechanism.
  Source: [Rust Internals — pre-RFC "using Sigstore for signing and verifying crates"](https://internals.rust-lang.org/t/pre-rfc-using-sigstore-for-signing-and-verifying-crates/18115/31),
  [crates.io development update, 2026-07-13](https://blog.rust-lang.org/2026/07/13/crates-io-development-update/)
  (no signing feature mentioned). This matters directly to GovOS: it is a Rust project, and there is **no**
  upstream Cargo-ecosystem trust mechanism to lean on for its own dependency supply chain — that gap is real and
  outside the scope of what any Level-1 library choice can close.
- **npm**: provenance attestations (in-toto/Sigstore-backed, via `npm publish --provenance`) exist but are a
  public-registry, online-transparency-log feature, structurally in the same "does not fit offline/private" bucket
  as Sigstore keyless (§2.3); not independently re-verified in this pass.
- **Classification**: **ADAPT THE PATTERN** (apt/RPM's "signed index of hashes" shape is exactly what GovOS's
  release/targets record already does, correctly, better than apt in one respect — GovOS has the monotonic
  high-water mark apt lacks). **Not a source of a reusable Rust crate** for GovOS's own needs (apt/RPM are C/Python
  ecosystems); their value here is as a documented **negative** example — proof that "signed hash list" alone,
  without TUF's role/version machinery, is insufficient, reinforcing §2.1/§2.2's recommendation.

### 2.6 OCI image / content-digest model

- **Property provided**: content-addressability — a manifest digest (SHA-256 of the manifest bytes) is an
  immutable identifier; if you know the digest, you can fetch content from an untrusted mirror and verify it
  yourself by recomputing the hash. A tag (`:latest`) is a separate, mutable pointer *to* a digest.
  Source: [OCI image-spec — Content Descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md).
- **Property NOT provided**: authenticity/authorisation. Digest identity says "these are the bytes named `X`"; it
  says nothing about *who* published them or whether they should be trusted — that is a **separate** signature
  step (cosign, Notation, etc.) layered on top, and pulling "by digest" only helps if the digest itself was
  obtained from a trusted channel in the first place (this is exactly the property TUF's target-file hash pinning
  already gives GovOS).
- **Relevance to GovOS**: the useful idea here is not the OCI format itself but the **decoupling of identity from
  mutability** — GovOS's release/targets record already does this (exact hash pinning of kernel/CLI payload). No
  new adoption needed; recorded for completeness because it was in the seed list.
- **Classification**: **ADAPT THE PATTERN**, already effectively present.

### 2.7 Nix / Guix content-addressed stores

- **Property provided**: in Nix's content-addressed derivation mode, a store path's name is (a function of) a hash
  of its *contents* — specifically, of the NAR (Nix ARchive) serialization, which is a canonical, deterministic
  archive format (fixed member order, stripped timestamps, normalised permissions) so the same tree always produces
  the same archive bytes and hence the same hash.
  Source: [Nix manual — Content-Addressing File System Objects](https://nix.dev/manual/nix/2.34/store/file-system-object/content-address.html).
  **Caveat, and it matters here**: Nix/Guix's *default and still-dominant* mode is **input-addressed**, not
  content-addressed — the store-path hash is derived from the build *inputs/derivation*, not the *output* content;
  content-addressed derivations are an explicit, still-maturing opt-in feature, not the ambient default even in
  current Nix. Any claim that "Nix/Guix make exact binding a storage-model property" should be read as "the
  content-addressed *subset* of Nix does this," not "Nix does this by default."
- **Property NOT provided**: authenticity (a content-addressed path's hash proves the *bytes match the name*; it
  proves nothing about whether those bytes should be trusted — you still need a signed binary-cache/substituter
  trust step, which Nix has, separately, via signed `.narinfo`); nor protection against the artefact simply being
  *deleted and replaced* at that path if the local store permissions don't forbid it (in practice Nix enforces
  store-path immutability via filesystem permissions — the Nix daemon owns `/nix/store` and makes paths read-only —
  which is an *operational* enforcement, not a property of the hash itself).
- **Direct answer to the brief's Q5**: yes, partially — a content-addressed store makes **"does this path contain
  the bytes its name claims"** a structural, storage-model-level property (recomputing the hash *is* the check;
  there is no separate "verify" step distinct from "the name") rather than a check that can be skipped, forgotten,
  or done against the wrong file. It does **not**, by itself, make **"is this the artefact you actually meant to
  run"** structural — an attacker who controls `PATH`/`argv` resolution can still point execution at a *different*,
  validly content-addressed path than the one you intended (this is precisely GovOS's `P79-F1`/`PATH=. true` shape
  reframed one level down: content-addressing fixes byte-identity, not resolution-identity). The generalisable
  lesson is therefore narrower than "adopt Nix": it is "make identity-checking non-optional by construction," which
  for GovOS's actual problem (Level 2 exec binding) is better achieved by **hermetic invocation** (a fixed,
  explicit set of inputs and no ambient PATH/CWD/environment-driven resolution) — the same discipline Nix's build
  sandbox already enforces for *builds*. Nix is worth studying as the *architecture* of hermetic, non-ambient
  execution; it is not worth adopting as a *store implementation* for a project whose payload is "one Rust binary
  plus a `framework/` tree," where the operational cost of a real Nix/Guix store (daemon, garbage collection,
  separate `/nix` partition or WSL2-specific store setup) would be disproportionate.
- **Classification**: **ADAPT THE PATTERN** for the "make it structural, not checked" principle, specifically as
  input to Level 2's execution-binding redesign, not as a Level-1 artefact-store replacement.

### 2.8 Reproducible builds

- **Property provided**: "given the same source, any party can recreate bit-for-bit identical artefacts,"
  creating an *independently verifiable path from source to binary* that lets a third party catch a compromised
  build step without trusting the builder.
  Source: [reproducible-builds.org — Definitions](https://reproducible-builds.org/docs/definition/).
- **Property NOT provided**: distribution trust, rollback protection, or anything about the verify/use gap; it is
  purely a build-integrity property, and it requires a *second, independent* builder to actually rebuild and
  compare — with one owner and one build machine, there is nobody to be the second party, so reproducibility alone
  buys nothing until/unless a second independent build environment exists.
- **Classification**: **USEFUL LATER** (R2, once there is more than one build environment) — not a Level-1
  distribution-trust primitive on its own, but a natural complement to a future SLSA build-provenance attestation
  (§2.4).

### 2.9 Uptane

- **What it adds over plain TUF**: a two-repository split (an offline-signed **Image** repository, structurally
  just TUF, plus an online **Director** repository that issues per-vehicle/per-fleet target selections on demand)
  and a Primary/Secondary ECU hierarchy where resource-constrained Secondary ECUs do partial verification and rely
  on a full-verification Primary.
  Source: [Uptane Standard, current](https://uptane.org/docs/2.1.0/standard/uptane-standard).
- **Fit**: neither half applies here. The Director repository exists to solve *fleet personalization with an online
  authority* — GovOS has one owner and no fleet to personalise for. The Primary/Secondary split exists to solve
  *constrained-device partial verification* — GovOS's target is a full Linux machine capable of doing complete TUF
  verification itself, not an embedded ECU. Once the Director/ECU machinery is subtracted, what remains is TUF.
- **Classification**: **NOT APPLICABLE**. Recorded explicitly so the study doesn't have to re-ask the question.

---

## 3. TOCTOU: the priority question (§4 of the brief)

**Framing.** GovOS's own defects (`P79-F11`, `P79-F1`) and the retired lineage's `RV-H3` are not the *same* TOCTOU
shape, and mature prior art answers them differently. Distinguish two threat shapes:

1. **External racer** (`RV-H3`): a second process swaps a file *after* it was verified but *before* it is used,
   within the small window between two operations GovOS itself performs (verify, then later read/act). This is the
   classical TOCTOU race the security literature usually means by the term.
2. **Self-inflicted double resolution** (`P79-F11`, `P79-F1`): no external racer is needed at all. GovOS verifies
   `argv[0]`/a named path once, under one resolution rule (lexical path, or path canonicalisation), and then a
   *different* component (the kernel's `execve`, or a shell) resolves the *same* lexical token again, under a
   *different* rule (through `$PATH`, through a working directory the same invocation controls, through a loader
   environment variable). There need not be a race at all — the two resolutions can be fully deterministic and
   still disagree, because they are different functions applied to the same untrusted input.

This distinction matters because the fixes are different, and conflating them produces solutions that address one
and not the other.

### 3.1 Mechanisms that only narrow or relocate the window (necessary, not sufficient)

- GovOS's own SRR-1 install transaction (§1) is a good example of doing this well for *installation*: stage
  privately → measure staged bytes → re-measure immediately before commit (`confirm_unchanged`) → atomic rename →
  re-verify the committed tree → *then* advance the floor. Every step narrows the window and the final re-hash
  catches an external racer who modified the staging area. It is still, structurally, "verify, then later re-verify,
  then act" — a small number of successively narrower windows, not zero windows. It is the right design for an
  install that only the trusted admin boundary can reach (per the brief's deployment profile, staging under
  `GOV_MACHINE_STATE_DIR` is inside that boundary), but the same pattern applied one layer down, to a governed
  *project* directory a lower-trust AI agent can write to at any time, is exactly the pattern that produced
  `P79-F11`: "hash `<root>/install.sh`, declare it readable, execute `<root>/decoy/install.sh`" is a verify/act
  window with an attacker-controlled resolver sitting inside it, and no amount of re-hashing the *first* path closes
  it, because the defect is that the *second* resolution never goes through the same path at all.
- Most package-manager trust models (apt, RPM, TUF itself, OCI, Nix's binary cache) verify-then-write-to-a-store,
  then *later*, in a separate operation, a package manager or the OS reads that store by path to install/run it.
  This is safe **only** under the assumption that nothing lower-trust can write to that store between the two
  steps — an assumption these ecosystems generally get to make (their store is admin-owned), and one GovOS gets to
  make for its *own* release install, but explicitly cannot make for a *governed project directory*, which is
  exactly where `P79-F11`/`P79-F1` live. None of these ecosystems' TOCTOU posture transfers to a location a
  lower-trust actor can write.

### 3.2 Mechanisms that actually close the gap

**(a) fd-pinned open→verify→exec (`fexecve`/`execveat(..., AT_EMPTY_PATH)`).** Open the file once, obtaining a file
descriptor; hash/verify by reading *from that fd*; then execute *that exact fd* rather than re-naming the file by
path. glibc's `fexecve(fd, argv, envp)` is implemented, on any kernel ≥ 3.19, as
`execveat(fd, "", argv, envp, AT_EMPTY_PATH)`; container runtimes (runc/containerd) already use exactly this pattern
to avoid TOCTOU races between checking and executing a file.
Sources: [`fexecve(3)`, man7.org](https://man7.org/linux/man-pages/man3/fexecve.3.html),
[`execveat(2)`, man7.org](https://man7.org/linux/man-pages/man2/execveat.2.html).
- **What it guarantees**: there is exactly one open, one measurement, one execution, all against the same inode's
  bytes at the same instant — no second path lookup exists for `PATH`, `CWD`, a symlink, or a hard link to diverge
  through. This is a *direct, precise* fix for `P79-F11`'s "verified bytes ≠ executed bytes" — verifying and
  executing become provably the same bytes because they are the same fd.
- **What it does NOT guarantee**: it fixes the *first* resolution of `argv[0]`, not what that program does next. If
  the verified, fd-pinned program is itself an interpreter invoked via a shebang line (`#!/bin/sh`), the kernel
  performs a **second**, independent path lookup to find `/bin/sh` — outside fexecve's control — which is exactly
  the shape of `env --chdir=decoy sh install.sh` (`P79-F11`) if the interpreter itself, not just the script, is
  the attacker-influenced token. Closing that requires **also** fd-pinning (or otherwise explicitly, non-ambiently
  resolving) every interpreter in the chain, not just the outermost `argv[0]`. It also does not address `PATH=.`
  style env-var attacks (`P79-F1`) on their own — that requires refusing ambient `PATH`/env resolution in the first
  place (hermetic invocation, §3.3) rather than merely pinning whatever path was resolved. And it says nothing
  about boundary/policy questions like `AR77-F4`'s hard-link defeat of a *canonicalisation-based* boundary check —
  that is a Level-2 authority question (is this inode inside the governed boundary), not a byte-identity question,
  and needs a device+inode/mount-based boundary check, not fd-pinning.
- **Cost**: pure userspace syscalls, no kernel config, no special filesystem, works today under WSL2's kernel with
  no additional assumption. This is the cheapest, most directly transferable mechanism from this whole study, and
  the recommended first move for the Level-2 exec-binding redesign.

**(b) Kernel-enforced integrity at every access — `fs-verity`, `dm-verity`, IMA-appraisal / IPE.** Rather than
verifying once in userspace, seal a file (or a whole read-only block device) so that the **kernel itself** refuses
to return bytes that don't match a sealed hash, on *every* read/open/mmap/exec — enforced by the filesystem or an
LSM, not by an earlier userspace check.
- `fs-verity`: per-file, built into ext4/f2fs/btrfs; once enabled, in-place modification of the file's content is
  refused by the kernel on every access. Requires kernel ≥ 5.4 with `CONFIG_FS_VERITY`.
  Source: [Linux kernel docs — fs-verity](https://www.kernel.org/doc/html/latest/filesystems/fsverity.html).
  **Explicit non-guarantee, stated by the kernel docs**: fs-verity "only guarantees that a file's contents cannot
  change... it does not protect against deletion and recreation" — a file can be unlinked and a *different* file
  created at the same name, entirely outside fs-verity's protection, because fs-verity protects an inode's content,
  not a name-to-content binding. This means fs-verity alone does not close `P79-F11`/`P79-F1` (which are precisely
  about *which file a name resolves to*), only a stronger variant of the "in-place tamper after verification"
  problem — still useful, but a different guarantee than what P79-F11 needs.
- `dm-verity`: the same idea at block-device granularity (a whole read-only partition backed by a Merkle tree); used
  for whole-OS/read-only-root images (e.g., Android, Chrome OS, Bottlerocket's own root filesystem). It was chosen
  over IMA+EVM in at least one documented case specifically because IMA+EVM, without an accompanying encryption
  layer, remains vulnerable to offline tampering. Source: general Linux kernel `dm-verity` documentation,
  [kernel.org — dm-verity](https://www.kernel.org/doc/html/v6.11/admin-guide/device-mapper/verity.html). Wrong grain
  for GovOS: it protects an entire partition, not an individually-editable project tree that legitimately changes
  under normal (governed) use.
- IMA-appraisal: enforces that a file carries a valid signature in `security.ima` before it may be opened/executed,
  checked by an LSM hook at open time — closer in spirit to "enforce at use," but has its **own documented TOCTOU
  weakness** against a malicious or racing block device, and researchers have specifically proposed backing IMA with
  `dm-verity`/`fs-verity` block-level verification exactly to close that residual gap.
  Source: [Kernel docs — Integrity Policy Enforcement (IPE)](https://docs.kernel.org/security/ipe.html); TOCTOU
  weakness discussed in academic literature surveyed via kernel-integrity documentation search (see §8).
- **WSL2 fit — could not determine.** I could not confirm from available sources whether the current WSL2 kernel
  ships `CONFIG_FS_VERITY` enabled, nor whether IMA/IPE LSM policy is configurable inside WSL2's virtualised boot
  path. This is a concrete, checkable fact (`zgrep FS_VERITY /proc/config.gz` or `cat /boot/config-$(uname -r)` on
  the actual WSL2 kernel) that a follow-up spike should establish before this option is assumed available; it is
  the strongest structural closer of the verify/use gap **if** available, and unusable if not.
- **Classification**: **HIGH-ASSURANCE ONLY / USEFUL LATER**, pending the WSL2 kernel-config check above; not a
  dependency to design Phase-2 around right now given the unresolved platform question.

**(c) Content-addressed naming + hermetic invocation (Nix/Guix pattern, discussed fully in §2.7).** Makes
byte-identity a structural, unskippable property of the *name*, but must be paired with a closed, non-ambient
resolution environment (no `PATH` search, no CWD-relative lookup, an explicit and complete input closure) to also
close resolution-identity — which is the part `P79-F1`/`P79-F11` actually hinge on. This is the deepest fix and the
correct one to study for the Level-2 execution-model redesign the brief anticipates, but it is an architecture
change to *how GovOS invokes anything*, not a Level-1 artefact-store swap.

### 3.3 Ranked recommendation for the transferable Level-2 question

1. **Now, cheap, precise**: fd-pinned open→verify→exec for the outermost `argv[0]` resolution, extended explicitly
   to every interpreter/shebang hop in a resolved chain (closes `P79-F11`'s core "verified bytes ≠ executed bytes"
   claim directly; does not by itself close `P79-F1`'s ambient-env-variable class or `AR77-F4`'s boundary-evasion
   class — those need the item below and a separate inode/device boundary check, respectively).
2. **Architectural, addresses the actual generalisation, not just this instance**: hermetic invocation — a closed,
   explicit set of resolved inputs (program, interpreter, environment, working directory) constructed *once* by the
   verifier and handed to execution as an opaque, already-resolved unit, with no later step permitted to re-derive
   any part of that unit from `argv`/env/cwd. This is the pattern Nix's build sandbox and content-addressed naming
   both express, generalised past "the store," and it is what would make the current per-shape command classifier
   (26/26 loader variables, ~40 command-shape defects and counting) unnecessary rather than merely more complete —
   directly matching the brief's own definition of a good result (§7 of the brief).
3. **Strongest but conditional**: kernel-enforced per-file integrity (`fs-verity`), pending confirmation it is
   available and configurable in this WSL2 environment, and understood correctly as protecting content-in-place,
   not name-to-content binding.

---

## 4. Rollback and high-water marks, single owner, no timestamp authority

GovOS's already-accepted design (durable local monotonic high-water for both metadata-role versions and the
release version/sequence, advanced only after a verified, committed install, §1) is the textbook-correct adaptation
of TUF's rollback protection to a profile with no trusted-time service: TUF's own client workflow requires
persisting trusted metadata locally and never accepting an older version than what is already trusted, independent
of the timestamp role's freshness claim — the freshness (timestamp) role and the rollback (never-go-backward)
property are two different mechanisms in TUF itself, and GovOS correctly kept the second while substituting a local
high-water mark for the first (which needs an online key it does not have). This is not a place I would recommend
building anything new; it is a place I would recommend **finishing the WRAP in §2.2** so the version-comparison and
threshold logic implementing this property is delegated to a reviewed library rather than hand-maintained — the
retired lineage's `RV-H1`/`R2-H2`/`R2-H4` findings show exactly how easy this specific logic is to get wrong by
hand (an alternate ingress like `update --rollback`/`init --force` bypassing the floor a different ingress enforces
is a classic "enforcement point not everywhere the authority is" bug — the same *shape* as the brief's whole Level-2
problem statement, recurring one level down).

---

## 5. Classification summary

| Candidate | Classification | Primary defect/finding class addressed |
|---|---|---|
| TUF (spec/pattern) | ADAPT THE PATTERN (already adopted) | R0/R1-era unauthenticated-source findings; RV-H1/H2, R2-H1/H2/H4 |
| `tough` crate | WRAP (not currently used; should be) | Same as above — replaces hand-rolled threshold/rotation/rollback logic |
| Sigstore keyless (Fulcio/Rekor) | NOT APPLICABLE this profile | — (offline/private mismatch) |
| Sigstore/cosign key-pair mode | REDUNDANT with existing ed25519-dalek use | — |
| in-toto attestation format | ADAPT THE PATTERN | Build-provenance field GovOS's own architecture already reserves |
| SLSA build levels | USEFUL LATER | Build-track hardening once >1 build environment exists |
| apt/dpkg, RPM trust models | ADAPT THE PATTERN (negative example) | Confirms role/version machinery > flat signed-hash-list |
| Cargo/crates.io signing | NO UPSTREAM MECHANISM EXISTS | N/A — noted as an open supply-chain gap, not solvable via library choice |
| OCI content digests | ADAPT THE PATTERN (already effectively present) | Exact artefact binding, already achieved via target hash pinning |
| Nix/Guix content-addressing | ADAPT THE PATTERN → feeds Level 2 | Q5 exact-binding; partial answer, see §2.7/§3.3 |
| Reproducible builds | USEFUL LATER | Build-integrity complement to SLSA, needs a second builder |
| Uptane | NOT APPLICABLE | — (fleet/ECU machinery doesn't map to one owner) |
| `fexecve`/`execveat` | USE DIRECTLY, Level-2 priority | P79-F11 directly; partially P79-F1 |
| Hermetic invocation (pattern) | ADAPT THE PATTERN, Level-2 priority | P79-F1, P79-F11, generalises past the current classifier |
| fs-verity/dm-verity/IMA | HIGH-ASSURANCE ONLY / USEFUL LATER | Strongest TOCTOU closer, WSL2 availability unresolved |

**REQUIRED NOW**: nothing in this Level-1 study is a blocking gap in the *architecture* GovOS already has accepted
(SRR-1's R0/R1 acceptance stands on its own merits); the actionable "required now" item is a **substitution**, not
an addition — replace the hand-rolled root/snapshot/timestamp/threshold/rollback logic with `tough` (§2.2) before
any further hand-written revision of that logic is attempted, given the seven-revision failure history of doing
this by hand.

**USEFUL LATER (R2)**: in-toto/SLSA build-provenance attestation once evidence digests are populated; reproducible
builds once a second build environment exists; RPM/npm ecosystem comparisons if GovOS ever needs to ingest
artefacts from those ecosystems as governed dependencies.

**HIGH-ASSURANCE ONLY (R3)**: Sigstore keyless/transparency-log posture (needs a public/multi-party threat model
this profile does not have); kernel-enforced integrity (`fs-verity`/dm-verity/IMA-IPE) pending WSL2 platform
confirmation; full Uptane-style Director/fleet machinery (no fleet exists).

---

## 6. Simplification opportunities (per the brief's §7)

- **Trusted computing base**: swapping hand-written root-rotation/threshold/rollback logic for `tough` moves that
  code's correctness burden onto a library with production use and public review, out of GovOS's own TCB accounting
  for that specific logic (the code that needs to be re-derived/re-audited on every future change shrinks).
- **Custom security code**: the retired lineage's HIGH findings (§1 table) are a direct measurement of how much
  custom-code risk this exact subsystem has produced historically; each row in that table is a finding class a
  conformant TUF client would not have needed inventing from scratch.
- **Number of authority sources**: none reduced by this study directly (GovOS's five roles — root/release/snapshot/
  timestamp/recovery — are already a minimal, TUF-shaped set); the reduction opportunity is in *implementation*
  provenance, not role count.
- **Test/proof surface**: root-rotation succession, threshold counting, and version-comparison edge cases currently
  need GovOS-authored tests; under a `tough`-based WRAP those edge cases are covered by `tough`'s own test suite,
  and GovOS's tests narrow to "does GovOS correctly consume an authorised target," a smaller and more stable
  surface.
- **Deletable candidate**: the JCS/DSSE canonicalization code path already avoided in SRR-1 (§1) is the model for
  what else should not be written; no further canonicalization code should be added anywhere in this subsystem.

---

## 7. What I could not determine

- Whether `tough`'s delegation model can express GovOS's plugin/tool/profile delegated-target use case without
  modification (needs a implementation spike, not a literature review).
- Whether the current WSL2 kernel (Microsoft's WSL2-Linux-Kernel build) ships `CONFIG_FS_VERITY`, or supports IMA/
  IPE LSM policy configuration — this is a concrete, checkable fact I did not have shell access to a live WSL2
  kernel config to confirm, and it gates whether §3.2(b) is usable at all in this environment.
  [WSL kernel release notes](https://learn.microsoft.com/en-us/windows/wsl/kernel-release-notes) is the right
  starting point for a follow-up.
- RPM/dnf's current (2026) rollback-protection posture — I recorded it only as "same generation as apt" on
  background knowledge, not independently re-verified this session; treat that line as lower-confidence than the
  rest of this report.
- Whether GovOS's actual release-signing ceremony (R2/`GATE-OWNER-KEY-CEREMONY`, not yet performed per the R1 build
  report) has any bearing on which of `tough`'s key-management assumptions would need adaptation — this is future,
  not-yet-built material I had no artefact to examine.
- I did not attempt to build or run `tough` against GovOS's actual metadata to confirm the WRAP is mechanically
  straightforward; the recommendation in §2.2/§5 is an architectural judgement from reading both codebases'
  documentation and source comments, not a verified integration.

---

## 8. Sources

- Governance OS repository (primary source): `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md`,
  `release/root-of-trust/signed-release-root-v1-r1-build/00-BUILD-REPORT.md`, `runtime/src/srr/crypto.rs`,
  `runtime/src/srr/metadata.rs`, `runtime/src/srr/staging.rs`, `runtime/src/srr/state.rs`; memory notes
  `governance-os-root-of-trust-escalation.md`, `governance-os-rot1-independent-review.md`,
  `governance-os-rot1-rev2-independent-review.md`, `governance-os-phase-1-orchestration.md`.
- [The Update Framework — specification, latest](https://theupdateframework.github.io/specification/latest/)
- [TUF specification source, `tuf-spec.md`](https://github.com/theupdateframework/specification/blob/master/tuf-spec.md)
- [`tough` — crates.io](https://crates.io/crates/tough/0.22.0), [`tuftool` — crates.io](https://crates.io/crates/tuftool/0.15.0)
- [Chainguard Academy — Verifying signatures in air-gapped environments](https://edu.chainguard.dev/open-source/sigstore/cosign/verifying-in-air-gapped-environments/)
- [Sigstore Cosign — signing overview](https://docs.sigstore.dev/cosign/signing/overview/)
- [SLSA — in-toto and SLSA](https://slsa.dev/blog/2023/05/in-toto-and-slsa); [SLSA v1.1 FAQ](https://slsa.dev/spec/v1.1/faq)
- [Rust Internals — pre-RFC: Sigstore for signing/verifying crates](https://internals.rust-lang.org/t/pre-rfc-using-sigstore-for-signing-and-verifying-crates/18115/31)
- [crates.io development update, 2026-07-13](https://blog.rust-lang.org/2026/07/13/crates-io-development-update/)
- [Debian `apt-secure(8)`](https://manpages.debian.org/testing/apt/apt-secure.8.en.html); [Debian wiki `SecureApt`](https://wiki.debian.org/SecureApt)
- [OCI image-spec — Content Descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)
- [Nix manual — Content-Addressing File System Objects](https://nix.dev/manual/nix/2.34/store/file-system-object/content-address.html)
- [reproducible-builds.org — Definitions](https://reproducible-builds.org/docs/definition/)
- [Uptane Standard 2.1.0](https://uptane.org/docs/2.1.0/standard/uptane-standard)
- [`fexecve(3)`, man7.org](https://man7.org/linux/man-pages/man3/fexecve.3.html); [`execveat(2)`, man7.org](https://man7.org/linux/man-pages/man2/execveat.2.html)
- [Linux kernel docs — fs-verity](https://www.kernel.org/doc/html/latest/filesystems/fsverity.html)
- [Linux kernel docs — dm-verity](https://www.kernel.org/doc/html/v6.11/admin-guide/device-mapper/verity.html)
- [Linux kernel docs — Integrity Policy Enforcement (IPE)](https://docs.kernel.org/security/ipe.html)
- [WSL kernel release notes, Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/kernel-release-notes)
