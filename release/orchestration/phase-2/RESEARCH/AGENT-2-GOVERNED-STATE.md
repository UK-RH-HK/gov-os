# Research Agent 2 — governed configuration and policy authority

| Field | Value |
|---|---|
| Scope | Level 2A (governed state / authority provenance) and 2C (policy/configuration integrity) |
| Status | READ-ONLY research. Nothing implemented, nothing proposed as a candidate. |
| Reads first | `release/orchestration/phase-2/RESEARCH/COMMON-BRIEF.md` (not restated here) |
| Also read for grounding | `release/orchestration/phase-2/PHASE_2_OPTION_B_ESCALATION_PACKAGE.md` (P79-F8/F10 mechanics); `release/releases/4.1.5/kernel/overlay-templates/REPOSITORY_CONTRACT.yaml` (current schema); `release/root-of-trust/meta-review/*.md` (status of the Level‑1 signed-release-root work this report leans on) |

## 0. Headline answer

**Yes — "only authenticated state has authority" is an established, mature, and implementable pattern at our scale.**
It is not one technology; it is the same structural move made independently by at least five unrelated engineering
traditions over three decades: software-update security (TUF), policy engines (OPA bundle signing), OS mandatory
access control (SELinux's compile‑then‑load boundary), software supply-chain attestation (in‑toto/SLSA), and
capability security theory (object‑capabilities, macaroons). Every one of them stops asking *"does this content look
like a legitimate change?"* and instead asks *"did this exact byte sequence arrive through a channel only the
authorized principal can produce?"* — a question a hand edit cannot answer yes to, by construction, without needing to
be recognized as a hand edit at all.

**The smallest mature version of it, at our scale, is not Kubernetes-shaped.** It needs no cluster, no control plane,
no SaaS: one owner-held signing key (an SSH or minisign key, verified through primitives already in git and OpenSSH),
a **structural split** between an immutable, release-sealed "floor" and a project-editable "local" layer, and a kernel
that (a) treats the working-tree file as an unauthoritative proposal, (b) computes effective policy only from the
**last validly-signed** state, and (c) refuses and *visibly reports* whenever that state is missing, stale, or
unverifiable — never silently falling back to the raw file. Full detail and evidence in §3–§6.

**This is not a new invention for Governance OS.** §11 shows the product's own accepted Level‑1 direction (a compact
signed release root) is the *same* primitive already pointed at a *different* problem (trusting the runtime binary).
The recommendation this report supports is extending that one root of trust to also seal authority-bearing
configuration, rather than building a second, unrelated mechanism to answer a structurally identical question.

---

## 1. The reframing question, answered directly

> Can we stop trying to determine whether a file was "hand edited," and instead make effective authority depend on an
> authenticated state transition, so an arbitrary file edit is simply *inert*?

**Yes, and "inert" is the operative word every mature system in this space actually achieves — not "detected," not
"flagged," but structurally without effect.** Four independent mechanisms produce inertness, and they are not
alternatives to pick one of — they compose:

1. **Signature-gated activation** (TUF, OPA bundle signing, cosign/sigstore, git commit signing). The consulted
   artifact is not "the file"; it is "the file **plus** a detached or embedded signature by an authorized key,
   verified before load." An edit to the file without a corresponding valid signature produces a byte sequence the
   loader refuses to activate at all — it never reaches the code that would reason about its *content*. There is no
   comparison step to defeat, because comparison never happens.
2. **Compile/load separation with a privileged transition** (SELinux, AppArmor, systemd sandboxing). The
   human/agent-editable *source* (`.te` files, profile text) has zero runtime effect until it passes through a
   privileged, non-bypassable transition (`load_policy`, `apparmor_parser`, `CAP_MAC_ADMIN`). The kernel never
   consults the source form. An edit to source is inert until someone with that specific privilege performs the
   transition — which is exactly "authenticated state transition" stated in OS terms, predating the phrase.
3. **No ambient authority / capability-only authorization** (object-capabilities, macaroons). Authority is never
   derived from *reading a declaration* (an ambient fact anyone who can see the file can also assert); it is derived
   only from *possessing an unforgeable reference or valid credential*. A config file that "declares" a class or an
   exemption is, in this discipline, not a source of authority at all — merely a request, which is either satisfied
   by a capability the requester already holds or it is not. P79‑F8 is a textbook ambient-authority bug: the `class`
   field is consulted as if reading it were itself authority-granting.
4. **Provenance/process compliance over content diffing** (in‑toto, SLSA). Verification asks "did the expected
   functionary perform the expected step, attested and linked into a continuous chain?" — never "does this output
   look different from a reference in a way that matters?" This is the most literal instance of *sidestepping* the
   comparison problem P79‑F8 exposes: in‑toto's verifier would not need a predicate over `class` transitions at all,
   because an artifact/config lacking a valid link for the "authorize contract change" step simply fails
   verification regardless of what it says.

**Why this specifically closes P79‑F8, and why a bidirectional predicate (Option (i) in the escalation package) does
not.** A bidirectional predicate is still an enumeration — now over *obligations* as well as *grants* — and the
escalation package's own finding is that **12 further consumers exist outside the table it would have to enumerate**.
Every one of the four mechanisms above instead removes the enumeration surface itself: there is no table of
"compared fields" for a hand edit to fall outside of, because the local file's content is never diffed against
anything to decide authority. Authority is decided by (1) whether the byte sequence carries a valid signature/link
from an authorized role, for state-transition mechanisms, or (2) whether the path is even reachable by the
project-editable layer at all, for the floor/local split in §6. Both are yes/no questions independent of what the
edit *says*.

---

## 2. Worked mapping: P79-F8 under this reframing

Current mechanism (from `PHASE_2_OPTION_B_ESCALATION_PACKAGE.md` §2, `policy_precedence.rs:677`, verified by the
prior independent reviewer): one predicate, `if n.flag(field) && !k.flag(field)`, refuses only a **gain**. The hand
edit `{pattern: "product/*.py", class: test}` changes only index flags (all *lost*, none gained), so it passes. The
obligation `MATERIAL_CHANGE_REQUIRES_CIT` is a side effect of `class` read by **12 further consumers** the predicate
does not know about (AR77‑F3 already showed a second, undocumented consumer of the same field).

Under the reframing:

- The kernel-governed obligation (`product/**` requires CIT on material change) is **not derived from the
  project-editable file at all**. It is part of the release-sealed floor — authored once, at release-build time, by
  the `release-agent` role, and delivered as part of the already-accepted Level‑1 signed release root (§11). The
  floor's rule is keyed on the **path pattern**, not on a `class` value someone else's file can assert.
- `REPOSITORY_CONTRACT.yaml` in the working tree becomes a **proposal** for the `governance/project/**` namespace
  only (which the schema already marks `owner_role: change-controller`, `mutation: restricted` — see §11.2). It has
  no channel to reach `governance/kernel/**` or `product/**` obligations, however it is edited, because the kernel
  never asks the project file "what do you say the class is here" for a floor-governed path — it asks the floor.
- Effective policy = **floor(path) AND local(path)** evaluated independently (OPA's own documented multi-bundle
  composition pattern, §6.1) — never floor **compared against** local, and never local **substituting for** floor.
  A hand edit cannot remove an obligation it was never consulted about.
- If the edit is made anyway (say, to a path the project layer *does* legitimately own), it is either (a) within the
  narrowing envelope the floor already permits — inert with respect to obligations, accepted for behavior — or (b) an
  attempt to touch a floor-owned path, which is refused **and reported** (§8), never silently applied.

This is the "delete an enumeration" outcome the brief asks for in §7: the fix is not a smarter table of consumers, it
is removing the question "what does the project file say about kernel-governed obligations" from the code path
entirely.

---

## 3. Candidate catalogue — 2A: governed state and authority provenance

Format per candidate: property **provided** / property **NOT** provided / trust assumptions / maturity & maintenance
/ licence / offline? cloud? root? WSL2? / complexity & performance / fit for single owner / defect mapping /
classification.

### 3.1 TUF — The Update Framework

- **Provides**: compromise-resilient distribution of signed metadata; role separation (root/targets/snapshot/
  timestamp) with **threshold signatures** per role; explicit rollback and freshness protection via versioned,
  expiring metadata. A client that receives an unsigned or under-threshold `targets.json` refuses it outright — no
  partial trust.
- **Does NOT provide**: anything about *what* the policy says being correct, or about execution-time behavior; it is
  purely "is this metadata the one the authorized keys produced." It also does not, by itself, solve key custody —
  that is a deployment decision.
- **Trust assumptions**: private keys for at least the threshold of each role are kept offline/secure; root keys are
  the ultimate trust anchor and their compromise is catastrophic (mitigated by keeping root offline and using
  delegated online keys for lower-stakes roles).
- **Maturity**: CNCF-graduated specification, IETF-adjacent process (`theupdateframework/specification`), production
  use in PyPI (PEP 458), Datadog, VMware, Docker Notary v2, Uptane (automotive). Actively maintained.
- **Licence**: Apache-2.0 (reference implementation `python-tuf`; several ports).
- **Offline/local**: yes — TUF is designed for untrusted, possibly offline mirrors; verification is entirely local
  once metadata is fetched. **No cloud requirement.** **No root requirement.** **Works in WSL2** (pure userspace
  crypto/file I/O).
- **Complexity**: full TUF (4 roles + delegations + a repository) is more machinery than a single-owner deployment
  needs — this is why §11 recommends reusing the *already-scoped-down* Level‑1 direction rather than adopting TUF in
  full for 2A.
- **Fit**: excellent as a **pattern** (signed, versioned, threshold, expiring metadata over "what is authoritative
  right now"); the full role/delegation model is more than one owner with one key needs.
- **Defect mapping**: P79‑F8, P79‑F10 (gives a mechanism to distinguish governed change from hand edit — the missing
  piece F10 identifies), AR77‑F3.
- **Classification**: **ADAPT THE PATTERN** for 2A (do not adopt the full multi-role protocol; adopt "signed,
  versioned, threshold-free single-key metadata with explicit expiry" as the shape).
- Sources: [TUF specification](https://theupdateframework.github.io/specification/latest/), [TUF metadata/roles
  docs](https://theupdateframework.io/docs/metadata/), [TUF on Wikipedia — role/threshold
  summary](https://en.wikipedia.org/wiki/The_Update_Framework).

### 3.2 OPA (Open Policy Agent) — signed policy bundles

- **Provides**: a bundle (`.tar.gz` of Rego + data) plus a `.signatures.json` of JWTs over per-file SHA hashes; OPA
  is configured out-of-band with a verification key and **will not activate** a bundle whose signature does not
  verify. Also provides an explicit **multi-bundle composition** model: independent teams/sources each own a
  package, and a top-level policy combines them (§6.1) — directly relevant to the floor/local split.
- **Does NOT provide**: protection if the verification key itself is only as trusted as the machine it sits on (no
  built-in threshold/multi-key scheme like TUF); does not itself define *how* conflicting bundles should combine —
  that is a Rego authoring decision (deny-overrides is a documented pattern, not a default).
- **Trust assumptions**: the verification public key is provisioned out-of-band and not derivable from the bundle
  itself; signer's private key custody is the deployer's responsibility.
- **Maturity**: CNCF-graduated project, in production at very large scale (Netflix, Pinterest, Capital One,
  Kubernetes Gatekeeper is built on it). Actively maintained.
- **Licence**: Apache-2.0.
- **Offline/local**: yes, filesystem bundles with `--verification-key` need no network. **No cloud. No root.**
  **Works in WSL2** (Go static binary).
- **Complexity**: low to integrate as a library or sidecar; the signing/verification mechanics are a few CLI flags.
  Rego itself is a real language to learn, which is the main integration cost.
- **Fit**: strong. This is arguably the closest off-the-shelf analogue to "seal `REPOSITORY_CONTRACT.yaml`'s derived,
  effective form and refuse to load an unsigned one."
- **Defect mapping**: P79‑F8, P79‑F10, AR77‑F3, and the precedence/floor question directly (§6.1).
- **Classification**: **WRAP / INTEGRATE** if Rego/OPA-as-dependency is acceptable inside a Rust runtime (OPA has a
  Go and WASM-compiled evaluator; embedding WASM-compiled Rego in Rust is a known pattern); otherwise **ADAPT THE
  PATTERN** (JWT-style detached signature over a canonicalized policy document, verified before use) using a
  Rust-native signer (`ed25519-dalek`, or the SSH-signing primitive in §3.6) instead of pulling in the OPA runtime.
- Sources: [OPA bundle signing](https://www.openpolicyagent.org/docs/management-bundles), [OPA CLI `sign`
  reference](https://www.openpolicyagent.org/docs/cli), [OPA bundle signature issue/design
  discussion](https://github.com/open-policy-agent/opa/issues/1757).

### 3.3 in-toto — layouts, functionaries, link metadata

- **Provides**: a **layout** naming the expected sequence of steps and which functionary (by key) is authorized to
  perform each; each performed step produces signed **link metadata**; final verification checks the whole chain of
  links against the layout, including material/product rules tying steps' inputs/outputs together. This is a formal
  model of exactly "authenticated state transition, verified as a chain" rather than as content inspection.
- **Does NOT provide**: anything about the *content* of a step being semantically correct — only that the claimed
  step happened, in order, by an authorized party, on the claimed materials. It also assumes a layout owner key
  exists and is itself trustworthy (bootstrap problem, same shape as TUF root/Level‑1).
- **Trust assumptions**: the layout is signed by a project owner key; each functionary's key is provisioned to the
  layout out-of-band; verification requires the verifier to already hold the layout's public key.
- **Maturity**: CNCF-related, used in production by Datadog, VMware, used inside SLSA's reference implementations,
  actively maintained (`in-toto/in-toto`, v1.0 spec).
- **Licence**: Apache-2.0.
- **Offline/local**: yes, fully local verification once layout + links are present. **No cloud. No root. Works in
  WSL2.**
- **Complexity**: heavier than a single signature check — designed for multi-step, multi-party pipelines (build,
  test, package, sign, deploy). For a single owner performing a single kind of transition ("author a contract
  change"), most of in-toto's machinery (multiple functionaries, material/product rules across many steps) is
  more structure than needed.
- **Fit**: strong as **vocabulary and pattern** (a named step, an authorized key, a link record, chain verification)
  for how "author a governed contract change" should be modeled; heavy as a literal dependency for one step.
- **Defect mapping**: P79‑F10 directly — in-toto is a mature, named answer to "how would a product tell a governed
  change from a hand edit," which the escalation package says the product currently has no mechanism for at all.
- **Classification**: **ADAPT THE PATTERN** (a single-step, single-functionary "link" record — i.e., a signed
  statement "change-controller key X authored this exact byte sequence at this exact path on this exact date" — is
  in-toto's idea reduced to the one step Governance OS actually needs).
- Sources: [in-toto specification v1.0](https://github.com/in-toto/specification/blob/v1.0/in-toto-spec.md),
  [in-toto project](https://github.com/in-toto/in-toto).

### 3.4 SLSA — Supply-chain Levels for Software Artifacts

- **Provides**: a graduated framework (Build track L0–L3, Source track L1–L4) defining what "provenance" must
  guarantee at each level — from "some provenance exists" up to "hermetic, non-falsifiable build with two-party
  reviewed source." Gives standard vocabulary (`build provenance`, `source provenance`) and a way to say *how much*
  authenticity a given artifact's history carries, not just yes/no.
- **Does NOT provide**: an implementation — it is a framework/rubric, not a library; "two-person review" on the
  Source track assumes a second person exists, which a single-owner deployment structurally does not have (this
  caps the achievable Source-track level at this deployment profile, not a product flaw).
- **Trust assumptions**: whatever the underlying attestation mechanism uses (commonly in-toto + Sigstore).
- **Maturity**: graduated OpenSSF project (Google-originated), widely referenced (GitHub, npm, PyPI provenance
  features are SLSA-aligned), actively maintained, current spec v1.2.
- **Licence**: spec is CC-BY-4.0-style documentation; reference tooling is Apache-2.0.
- **Offline/local**: the framework itself has no network requirement; specific tool implementations (e.g.,
  GitHub-hosted provenance generators) do assume CI infra Governance OS's single-owner WSL2 profile does not have.
- **Complexity/fit**: mainly useful here as **a rubric to self-assess** how strong a claim "this contract change is
  authenticated" is allowed to be, given a single owner cannot satisfy two-party review. Not something to integrate
  as code.
- **Defect mapping**: P79‑F10 (frames the target property); informs how far to trust the mechanism recommended in
  §6, i.e., be honest that single-owner "authenticity" tops out below what a two-party SLSA Source L3/L4 claim would
  be, and that is an accepted deployment-profile limit, not a defect to chase.
- **Classification**: **ADAPT THE PATTERN** (as a rubric/vocabulary only — not a dependency).
- Sources: [SLSA levels](https://slsa.dev/spec/v0.1/levels), [SLSA build
  provenance](https://slsa.dev/spec/draft/build-provenance), [Wiz SLSA
  overview](https://www.wiz.io/academy/application-security/slsa-framework) (interpretive, used only for the
  two-track summary, cross-checked against slsa.dev).

### 3.5 Event sourcing / append-only authenticated journal

- **Provides**: current state is **never** stored/edited directly — it is a fold over an append-only sequence of
  events. Applied to authority: a "governed contract change" is an *event* (append `ClassChanged{path, from, to,
  authorized_by}`), and effective state is derived by replaying the event log. A hand edit to a materialized snapshot
  file is not an event at all — it has no place in the fold, so it is inert by construction, not by detection.
- **Does NOT provide**: authentication by itself — event sourcing is silent on *who* may append; that has to be
  layered on (an HMAC/signature per event, or restricting the append path to a privileged process). Without that
  layer, event sourcing alone does not solve P79‑F8 — it only relocates the same problem to "what stops a hand edit
  to the event log." This is a hazard worth stating plainly: **event sourcing is necessary but not sufficient**;
  it must be paired with §3.1/3.2/3.6-style signing on each append, or it is cosmetic.
- **Trust assumptions**: whichever signing mechanism gates the append.
- **Maturity**: architectural pattern, not a product — described by Martin Fowler (2005) and formalized in
  Microsoft's Azure Architecture Center pattern catalogue; extremely well-precedented in finance/ledger systems and
  in git itself (see §3.6 — a git history is, structurally, an append-only authenticated-if-signed event log).
- **Licence**: n/a (pattern).
- **Offline/local**: trivially, a local append-only file or the local git repository already *is* this. **No cloud,
  no root, works in WSL2** by definition — it needs nothing beyond a filesystem.
- **Complexity**: low if git itself is reused as the journal (§3.6); higher if built as a bespoke log format.
- **Fit**: very strong, and very cheap, **if git commit signing is reused as the authenticity layer** rather than
  inventing a parallel log.
- **Defect mapping**: P79‑F8, P79‑F10 — gives the "authenticated state transition" concept its concrete shape.
- **Classification**: **ADAPT THE PATTERN**, realized in practice as §3.6, not as a new bespoke log format
  (**BUILD CUSTOM** would be the wrong call here — git already is this).
- Sources: [Martin Fowler, retrieved via search results characterizing his 2005
  article](https://martinfowler.com/eaaDev/EventSourcing.html) (title/URL known from prior knowledge, confirmed
  concept accurate against [Azure Architecture Center — Event Sourcing
  pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)).

### 3.6 Git commit/tag signing (SSH or GPG) + `allowed_signers`

- **Provides**: git natively supports signing commits/tags with GPG or (since git 2.34) an **SSH key** — the same
  key type already used for repo access on a developer machine — and verifying them against a simple
  `allowed_signers` file (`email <public key>` per line), checked with `git verify-commit` /
  `gpg.ssh.allowedSignersFile`. Combined with git's existing hash-chained, append-only commit history, this turns
  the **repository itself** into the "authenticated state transition" journal from §3.5: a change to
  `REPOSITORY_CONTRACT.yaml` is authoritative only if it arrived as a commit signed by the `change-controller` or
  `release-agent` role's key, on a path git's own history proves is reachable from a trusted ref.
- **Does NOT provide**: enforcement by itself — git will happily accept an unsigned commit unless something (a
  pre-receive hook on a server, or the **consumer** of the file) checks for and requires a valid signature. It also
  does not protect a bare **working-tree** edit that is never committed at all (someone hand-editing the file on
  disk without committing) — that case is only closed if the kernel refuses to read the working tree at all and only
  reads from a verified ref (see §6.3's "read from a sealed ref, not the working tree" recommendation).
- **Trust assumptions**: the private key is kept on the owner's machine (ssh-agent/1Password/gpg-agent); loss of that
  key is the loss of the only authority (single point of failure appropriate to a single-owner deployment, but worth
  naming as a bus-factor risk exactly the size of the deployment).
- **Maturity**: SSH signing has been a stable git feature since 2.34 (2021); extremely mature, used at scale by
  GitHub/GitLab for "Verified" badges.
- **Licence**: git itself is GPL-2.0; OpenSSH is BSD-style.
- **Offline/local**: fully local — signing and verification are local crypto operations, no network required.
  **No cloud. No root. Works in WSL2** (git and ssh-keygen are both first-class in WSL2).
- **Complexity**: very low — this is a few lines of git config and an `allowed_signers` file the kernel can also
  read to perform its own verification independent of the git CLI (git's SSH signature format is documented and
  verifiable with standard SSH signature verification, not exclusively through the `git` binary).
- **Fit**: excellent. This is the **cheapest possible instance** of §3.1–§3.3's pattern, built entirely from
  primitives already on the machine, requiring no new dependency, no new key-management story beyond one already
  used for repo access, and no protocol design.
- **Defect mapping**: P79‑F8, P79‑F10, AR77‑F3 directly; this is the concrete mechanism §6.3 recommends as the
  smallest version of "only authenticated state has authority."
- **Classification**: **USE DIRECTLY** (git's native SSH-signing + `allowed_signers` verification, as-is, no
  wrapper needed for the signing/verification primitive; Governance OS supplies the policy of *which paths* require
  it and *which roles'* keys count).
- Sources: [GitHub Docs — commit signature
  verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification),
  [GitLab — SSH signed commits](https://docs.gitlab.com/user/project/repository/signed_commits/ssh/), [independent
  write-up confirming `allowed_signers` mechanics and git ≥2.34
  requirement](https://dbushell.com/2023/06/20/git-ssh-verify-allowed-signers/).

### 3.7 Sigstore / cosign `sign-blob` / `verify-blob` (offline, local-key mode)

- **Provides**: a purpose-built CLI for signing/verifying arbitrary files (not just container images) with a local
  key pair, entirely independent of Sigstore's public "keyless" infrastructure (Fulcio CA, Rekor transparency log).
  `--offline=true` explicitly disables the Rekor fallback; `--tlog-upload=false` plus
  `--insecure-ignore-tlog=true` on verify skips the transparency log entirely.
- **Does NOT provide**: transparency-log-backed non-repudiation *unless* Rekor is used — in local-key/offline mode
  you get exactly what a raw signature gives you (authenticity + integrity), not "publicly provable this was signed
  at time T," which is the property Rekor exists to add and which a single offline owner has no use for anyway.
- **Trust assumptions**: identical to §3.6 — whoever holds the private key is the authority.
- **Maturity**: cosign is a CNCF Sigstore subproject, very actively developed, industry-standard for container/
  artifact signing (adopted by Kubernetes SIG-security, major registries).
- **Licence**: Apache-2.0.
- **Offline/local**: yes, explicitly designed for this via the flags above. **No cloud required in this mode.
  No root. Works in WSL2** (Go static binary).
- **Complexity**: marginally higher than §3.6 (extra dependency, extra binary) for **no capability gain** over
  reusing git's already-present SSH signing for this specific use case, since Governance OS already depends on git.
- **Fit**: good, but redundant with §3.6 for the "sign a config file with a local key" use case; more relevant if
  Governance OS later needs to sign **non-git artifacts** (e.g., built plugin binaries, release tarballs) where
  there is no natural git history to anchor to — that is closer to Level 1 territory.
- **Defect mapping**: P79‑F8, P79‑F10 (as an alternative implementation, not additive once §3.6 is adopted).
- **Classification**: **USE DIRECTLY**, but only if a non-git-anchored signing need is identified; for
  `REPOSITORY_CONTRACT.yaml` specifically, §3.6 is strictly smaller for the same guarantee. Flag as **USEFUL LATER**
  (candidate for Level‑1 release-artifact signing, not required now for 2A/2C).
- Sources: [cosign offline verification
  discussion](https://github.com/sigstore/cosign/issues/2255), [Sigstore docs — signing
  blobs](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/), [Chainguard Academy — sign/verify
  blobs](https://edu.chainguard.dev/open-source/sigstore/cosign/how-to-sign-blobs-with-cosign/).

### 3.8 TPM sealing (PCR-bound secrets/state)

- **Provides**: hardware-backed sealing of data such that it can only be unsealed when the platform's measured boot
  state (PCR values) matches what it was sealed against — a genuinely different, stronger guarantee than a software
  signature (ties authority to *this specific measured machine state*, not just to key possession).
- **Does NOT provide**: anything if there is no TPM the guest can reach. It also does not protect against an
  authorized owner with admin rights intentionally changing state (which is normal, expected activity in our
  deployment profile) — TPM sealing is aimed at detecting *unauthorized* platform tampering below the OS, a threat
  model largely orthogonal to "did a hand edit change a YAML file."
- **Trust assumptions**: a functioning TPM 2.0, a measured boot chain, and PCR values that are actually meaningful
  (not trivially reset).
- **Maturity**: TPM 2.0 is an ISO/IEC 11889 standard, extremely mature in principle.
- **Licence**: n/a (hardware/firmware standard); Linux tooling (`tpm2-tools`) is BSD-style.
- **Offline/local**: yes in principle. **Requires specific hardware. Works in WSL2: no**, or at best partially and
  indirectly. A 2023 Microsoft/WSL GitHub issue explicitly requests native TPM device support for WSL2 and confirms
  it was **not** available at that time; the only bridge found (`tpm2-send-tbs`) routes through Windows' own TBS
  (TPM Base Services) rather than exposing a real `/dev/tpm0` to the Linux guest, and does not give the Linux kernel
  guest genuine measured-boot PCR semantics for *its own* boot (WSL2's "boot" is a lightweight VM launch, not a
  measured UEFI boot of the guest). I could not confirm current (2026) status changed this fundamentally; see §12.
- **Complexity/fit**: not usable as designed in this deployment. Even where a bridge exists, it changes the trust
  model to "trusting the Windows host's TBS," which is a different and larger claim than this study is scoped to
  evaluate (would need its own threat-model discussion, and the brief explicitly warns against R3 leaking into
  Level 1–2).
- **Defect mapping**: none directly addressable given the platform constraint.
- **Classification**: **HIGH-ASSURANCE ONLY**, and specifically **not available** in the stated deployment
  (WSL2 guest without a verified TPM passthrough path). Do not plan on this for 2A/2C.
- Sources: [microsoft/WSL issue #10777 — "Enable TPM support for
  WSL2"](https://github.com/microsoft/WSL/issues/10777), [tpm2-software/tpm2-send-tbs — bridges to Windows TBS, not
  native passthrough](https://github.com/tpm2-software/tpm2-send-tbs). I could not find an official Microsoft
  statement confirming native TPM device passthrough shipped by 2026; treat "no" as the safer working assumption
  and flag it explicitly as unverified currency in §12.

### 3.9 Object-capability model / no ambient authority

- **Provides**: a formal security discipline (Mark Miller, *Capability Myths Demolished*, and his 2006 PhD thesis)
  in which authority is conveyed **only** by possessing an unforgeable reference, never by an ambient fact anyone can
  assert (such as "this file says class=test"). Directly names the bug class P79‑F8/AR77‑F3 belong to: a
  **confused deputy** (Norm Hardy, 1988) — a component (the integrity checker) that holds authority derived from two
  sources (the kernel's own rules, and whatever a lower-trust file asserts) and has no way to keep them apart.
- **Does NOT provide**: a ready-made library for a Rust YAML-driven policy engine — this is a design discipline/
  vocabulary, not a drop-in component. Applying it fully would mean redesigning how "class" is represented (as a
  capability handed out by the floor, not a field read from a file), which is a larger change than the 2A/2C scope
  of this study authorizes recommending as a concrete build.
- **Maturity**: the theory is mature (Miller's thesis, 2006), and real capability-secure systems/interfaces
  (Fuchsia's Zircon kernel, Capsicum on FreeBSD, seL4, Cap'n Proto RPC) are actively maintained and mature.
- **Licence**: n/a (design discipline); specific implementations vary (seL4: GPL-2.0/BSD dual, Cap'n Proto: MIT).
- **Offline/local**: the discipline itself has no infrastructure requirement. **No cloud, no root** required to
  *apply the principle* (e.g., "the project file is not a capability, so do not treat reading it as authority").
- **Complexity**: adopting the full discipline is a redesign; adopting the **one insight** — "stop letting the
  project file be read *as if* possessing a capability" — is what §6.3's floor/local split already does, cheaply.
- **Fit**: as a lens, essential; as an implementation, out of scope for a low-cost recommendation now.
- **Defect mapping**: P79‑F8, AR77‑F3, and generally, the recurring "representation vs. effect" shape named in
  COMMON-BRIEF §1 is exactly the confused-deputy shape.
- **Classification**: **ADAPT THE PATTERN** (as design vocabulary and the justification for §6.3's split), not
  **BUILD CUSTOM** (do not build a general capability system for this).
- Sources: [Mark S. Miller, *Capability Myths
  Demolished*](https://papers.agoric.com/assets/pdf/papers/capability-myths-demolished.pdf), [summary of no-ambient-
  authority vs. Unix DAC](https://blog.acolyer.org/2016/02/16/capability-myths-demolished/), [Norm Hardy, *The
  Confused Deputy*, ACM SIGOPS OSR 22(4),
  1988](https://dl.acm.org/doi/10.1145/54289.871709), [historical framing of Hardy's original 1970s Tymshare
  example](https://erights.medium.com/norm-hardys-place-in-history-cecf191df641).

### 3.10 Macaroons — attenuation-only delegated authority

- **Provides**: a bearer-credential format (chained HMACs) that can be **attenuated** (have caveats added, narrowing
  what it authorizes) by anyone holding it, but **never amplified** — a formal proof that a derived macaroon's
  authority is always a subset of its parent's. Directly matches the brief's "lower-trust configuration may narrow
  but not widen" requirement, but as an *authorization-token* mechanism (distributed systems / API delegation),
  not obviously as a *config-file* mechanism.
- **Does NOT provide**: a natural fit for "a YAML file describing path classes" — macaroons authorize *requests*
  (bearer tokens presented at call time), not *static declarative policy documents*. Forcing this shape onto
  Governance OS's config model would be a translation exercise with real cost. The **attenuation-only property**
  itself is echoed elsewhere — biscuit tokens are a modern, offline-verifiable descendant using public-key
  cryptography rather than shared-HMAC chaining, worth naming since it removes macaroons' shared-secret-server
  limitation and would be a better fit for a single-owner offline setup if a token-shaped model were ever chosen.
- **Trust assumptions**: possession of the macaroon and its discharge caveats; original minting authority.
- **Maturity**: Google Research/NDSS 2014 paper, adopted by Google Cloud IAM, CockroachDB, and others; the general
  idea (attenuation-only derivation) is what matters here more than the specific HMAC-chain implementation.
- **Licence**: n/a (paper/technique); open implementations exist under various OSS licences.
- **Offline/local**: verifiable locally given the caveat-checking logic; **no cloud required** for the core
  primitive. **No root. Works in WSL2** trivially (it is pure computation).
- **Complexity/fit**: high cost to retrofit onto a file-based config model; the **principle** (derivation can only
  narrow, formally provable) is valuable, the **mechanism** is not the right shape for this problem.
- **Defect mapping**: informs the "narrow only" property required by COMMON-BRIEF §2C, but is not the recommended
  implementation route (see §6.3, which achieves the same narrow-only property structurally via AND-composition,
  more cheaply).
- **Classification**: **ADAPT THE PATTERN** (the attenuation-only property, not the token mechanism).
- Sources: [Birgisson et al., *Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the
  Cloud*, NDSS 2014](https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-
  authorization-in-the-cloud/), [NDSS 2014 programme
  listing](https://www.ndss-symposium.org/ndss2014/ndss-2014-programme/macaroons-cookies-contextual-caveats-
  decentralized-authorization-cloud/).

### 3.11 GitOps (OpenGitOps four principles)

- **Provides**: a named discipline — declarative desired state; stored versioned and immutable; **pulled**
  automatically by an agent (not pushed to it); **continuously reconciled** against live state. The fourth principle
  is the interesting one for us: a reconciler that treats **live state as always subordinate to declared state**,
  self-healing any drift — including a hand edit to a live copy, which is simply overwritten on the next
  reconciliation pass rather than "detected."
- **Does NOT provide**: authentication of the declared state itself — GitOps assumes the git repository holding
  "desired state" is properly access-controlled (branch protection, required review), which is an *organizational*
  control, not something GitOps tooling verifies cryptographically per commit by default. A GitOps loop reconciling
  from an unsigned, freely-editable git branch inherits exactly the P79‑F8 problem one level up.
- **Trust assumptions**: the git repository/branch the reconciler pulls from is itself trustworthy (this is the gap
  §3.6's signing closes).
- **Maturity**: CNCF-incubating specification (OpenGitOps), implemented by mature tools (Flux, Argo CD), widely
  deployed.
- **Licence**: Apache-2.0 (OpenGitOps docs and the reference implementations).
- **Offline/local**: the *principles* have no infrastructure requirement (a reconciler is just a loop); the
  *named tools* (Flux/Argo CD) are Kubernetes-native and assume a control plane, which we do not have.
- **Complexity/fit**: adopting Flux/Argo CD literally is wrong for this deployment (needs a cluster). The
  **reconciliation-not-detection** principle is directly reusable at tiny scale: instead of the kernel *reading* the
  working-tree `REPOSITORY_CONTRACT.yaml`, it reads only a **materialized, sealed copy** produced by a small local
  reconciler that pulls from a verified ref (§3.6) — a hand edit to the working tree is never read as authoritative
  at all, exactly matching "inert."
- **Defect mapping**: P79‑F8, P79‑F10 — gives an operational shape (a reconcile step) to pair with §3.6's signing.
- **Classification**: **ADAPT THE PATTERN** (reconcile-from-verified-ref as an operational discipline); the named
  tools themselves are **HIGH-ASSURANCE / cluster-shaped ONLY**, not applicable here.
- Sources: [OpenGitOps principles](https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md), [OpenGitOps
  1.0 announcement](https://opengitops.dev/blog/1.0-announcement/).

---

## 4. Candidate catalogue — 2C: policy/configuration integrity (floor vs. local)

### 4.1 OPA multi-bundle composition (independent-source conjunction)

- **Provides**: a documented pattern where **independent teams each own a package**, and a top-level policy composes
  them — critically, **not** by one policy reading/diffing another's source, but by both being separately evaluated
  and combined (commonly "deny overrides": if *either* source denies, the result denies). OPA also documents
  "global/hierarchical" org-wide rules composed with team-local rules this same way.
- **Does NOT provide**: composition semantics out of the box — *how* to combine (deny-overrides vs. allow-overrides)
  is something the integrating Rego must state explicitly; get it backwards and a local policy silently wins, which
  would recreate P79‑F8. This must be written deliberately, once, and tested — it is not automatically safe by using
  OPA.
- **Trust assumptions**: both sources are evaluated with equal engine trust; the *safety* comes entirely from which
  composition operator is chosen, so this is a design decision with a right and wrong answer, not a property OPA
  enforces for you.
- **Maturity/licence/offline/WSL2**: as §3.2 (same project).
- **Complexity/fit**: low — this is a Rego authoring pattern more than a new component, and is exactly the shape
  needed for "floor AND local, never floor influenced by local."
- **Defect mapping**: **this is the direct architectural answer to P79‑F8.** The current predicate compares the
  local file against a reference copy of the same file (a single mutable source diffed against itself over time,
  effectively); the fix is not a better diff — it is refusing to have only one source. Floor and local as
  **independently sourced, independently evaluated, AND-composed** inputs means the local source structurally cannot
  suppress a floor obligation, regardless of cleverness, because the floor's evaluation never consults the local
  source's content to decide whether the obligation applies.
- **Classification**: **ADAPT THE PATTERN** (composition-by-independent-AND), realized without necessarily adopting
  OPA/Rego itself — the same operator can be written directly in Rust over the existing predicate structure, once the
  floor is sourced independently of the project file (§6).
- Sources: [OPA FAQ — combining team policies into an overall
  decision](https://www.openpolicyagent.org/docs/latest/faq/), [OPA management/bundles
  docs](https://www.openpolicyagent.org/docs/management-bundles).

### 4.2 Kubernetes admission control model (Gatekeeper / Kyverno) — pattern only

- **Provides**: two guarantees relevant here, both achieved through a control plane we do not have: (1) policy
  objects (`ConstraintTemplate`/`Constraint` in Gatekeeper, `Policy`/`ClusterPolicy` in Kyverno) are themselves
  **ordinary API objects gated by RBAC** — a "local," lower-privileged actor literally cannot write to the object
  that carries authority, which is a cleaner floor/local separation than file-permission-based approaches because
  the write path itself is authenticated per-object, not per-file; and (2) a documented, explicit **fail-mode
  choice** (`failurePolicy: Fail` vs `Ignore`) that makes "what happens if the policy check cannot run" a first-class
  configuration decision rather than an implicit default — directly relevant to OC-P2-04 (§8).
- **Does NOT provide**: anything without a Kubernetes API server + etcd + a running admission webhook — none of
  which exist, or should exist, in a single-owner WSL2 deployment with no cluster. Kyverno's own escape hatch,
  `PolicyException`, is a second RBAC-gated object type specifically because unrestricted local exceptions were
  recognized as a real risk in this ecosystem — worth noting as independent confirmation that "a narrowing local
  override must itself be access-controlled, not just schema-validated," which is exactly the gap in the current
  `class` field (any project-editable actor can write it, with no separate authorization check on *that specific
  write*).
- **Trust assumptions**: cluster RBAC is correctly configured; admission webhook availability (the `Fail`/`Ignore`
  choice exists precisely because a webhook can be down).
- **Maturity**: Gatekeeper and Kyverno are both CNCF-graduated/incubating, mature, widely deployed.
- **Licence**: Apache-2.0 (both).
- **Offline/local/root/WSL2**: **requires a Kubernetes control plane** — none of "offline," "no cloud," "no root
  needed beyond what K8s itself needs," or "runs meaningfully in WSL2 without standing up a cluster (e.g., kind/
  k3d)" are true in a way that fits this deployment. This is the clearest instance in the whole study of "the
  pattern transfers, the implementation does not" that the brief asks to flag explicitly.
- **Complexity/fit**: standing up any of this for one owner on one machine would be materially larger than the
  problem it solves. Not recommended to run.
- **Defect mapping**: informs §6 (RBAC-style write-gating on the authority-bearing field, not the whole file) and §8
  (fail-mode must be an explicit, visible choice).
- **Classification**: **HIGH-ASSURANCE / cluster-shaped ONLY** for the implementation; **ADAPT THE PATTERN** for two
  ideas only — (a) gate the *write path* to authority-bearing fields specifically, not just the file generally, and
  (b) make the fail-mode an explicit, documented, fail-closed default.
- Sources: [Kubernetes — Admission Webhook Good
  Practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/),
  [Kyverno — Policy Exceptions](https://release-1-12-0.kyverno.io/docs/writing-policies/exceptions/).

### 4.3 SELinux — compile-then-load boundary and `neverallow`

- **Provides**: the strongest available real-world precedent for "source text is inert until an authenticated,
  privileged transition loads it," plus a genuine **global floor mechanism**: `neverallow` assertions in the base
  policy are checked at **policy compile time** against the fully expanded policy (including any loaded modules),
  and compilation **fails** if a module — however it is written — would grant something a `neverallow` forbids. This
  is not a runtime comparison of "module vs. base" content; it is a build-time closure check over the *expanded*
  effective policy, which cannot be defeated by phrasing a grant differently (the class of bug P79‑F8 is), because
  the check is semantic (over the expanded access it actually implies) rather than syntactic (over how the rule was
  written).
- **Does NOT provide**: application beyond OS-level mandatory access control (files, sockets, processes) —
  Governance OS's problem (governing a YAML-described policy about *files and change classes*) is analogous but not
  literally SELinux's domain; adopting SELinux itself would only help if Governance OS's operations were mediated by
  the Linux kernel's own MAC hooks (worth a longer-term look, out of Phase‑2 scope) rather than by userspace Rust
  logic reading a config file.
- **Trust assumptions**: `CAP_MAC_ADMIN`/root controls who can load policy; the base policy and its `neverallow` set
  are themselves trusted (chicken problem solved the same way as everywhere else — root of trust ultimately anchors
  in something, here the boot-time-loaded base policy).
- **Maturity**: in the mainline Linux kernel since 2003, extremely mature, maintained by Red Hat/community
  (`selinux-project`), default-on in RHEL/Fedora.
- **Licence**: GPL-2.0 (kernel LSM), refpolicy sources typically public-domain/GPL.
- **Offline/local**: fully local, kernel-resident. **No cloud. Requires root** to load policy (by design — that is
  the point: only root can perform the authenticated transition). **Works in WSL2**: SELinux itself is **not**
  enabled in Microsoft's WSL2 kernel by default and is not a realistic control to turn on for this deployment; cited
  here purely as **pattern evidence**, not as something to run.
- **Complexity/fit**: not deployable as literal SELinux here. The **pattern** — compile a floor to a closed/expanded
  form, check semantically not syntactically, and make loading privileged — maps directly onto §6.3's recommendation
  to seal a **derived, expanded** effective-policy document (not the raw YAML) and gate who/what can produce it.
- **Defect mapping**: P79‑F8 most directly of anything researched — `neverallow`'s semantic, expanded-form check is
  precisely the "bidirectional, obligation-aware, and comparison-proof" property the escalation package's Option (i)
  gropes toward, achieved not by enumerating obligations but by checking the *fully expanded effective access* against
  a floor, which is a different (and stronger) move than "compare fields."
- **Classification**: **ADAPT THE PATTERN** (semantic check over expanded/derived state; privileged-load boundary),
  explicitly not USE DIRECTLY (wrong domain, not available in this kernel).
- Sources: [Red Hat — "Is it possible to add a neverallow statement to the existing SELinux
  policy?"](https://access.redhat.com/solutions/2110661), [SELinux Notebook / community write-up on neverallow as a
  compile-time expand-check](https://mgrepl.wordpress.com/2015/09/09/selinux-insides-part2-neverallow-assertions/),
  [Gentoo wiki — how SELinux policy is compiled and loaded](https://wiki.gentoo.org/wiki/SELinux/Policy).

### 4.4 AppArmor — comparison case (the gap when there is no global floor)

- **Provides**: the same compile/load privilege boundary as SELinux (`apparmor_parser` requires privilege), but
  **no equivalent to `neverallow`** — AppArmor profiles are independent text files with no cross-profile,
  compile-time assertion that one profile cannot grant what another forbids. Included specifically as a **negative
  control**: it shows that "privileged load" alone is not sufficient to get a floor guarantee — you also need the
  `neverallow`-style closed-form check (§4.3) for the floor property specifically. Without it, two independently
  loaded, individually-valid AppArmor profiles can together permit something neither author intended, structurally
  similar to how the current `class` predicate is locally valid per-comparison yet globally wrong.
- **Maturity/licence/offline/WSL2**: mature (mainline since 2010), GPL-2.0, kernel-resident like SELinux — same "not
  present/enabled in the WSL2 kernel" caveat as §4.3; cited for pattern contrast, not deployment.
- **Defect mapping**: cautionary evidence for §6 — the floor/local split must include an explicit, closed-form check
  (like `neverallow`), not just "privileged write access to the floor file," or it inherits AppArmor's gap rather
  than SELinux's guarantee.
- **Classification**: **ADAPT THE PATTERN (negative case)** — informs what to avoid.
- Sources: [Gentoo wiki — SELinux policy compile/load
  process](https://wiki.gentoo.org/wiki/SELinux/Tutorials/How_is_the_policy_provided_and_loaded) (contrast point
  drawn from general AppArmor/SELinux architecture literature cross-referenced above; I did not find a single
  canonical document stating AppArmor's lack of a neverallow-equivalent as explicitly as SELinux's own docs state
  neverallow — see §12).

### 4.5 Bazel / Nix — hermetic, content-addressed derivation

- **Provides**: an effective build/policy output is derived deterministically from a **complete, hashed description
  of its inputs**; with content-addressed derivations, the output store path *is* a hash of the output bytes. Two
  different input descriptions either produce the identical hash (truly equivalent) or a different path entirely —
  there is no "mostly the same, compare field by field" state; equivalence is structural (hash equality) rather than
  semantic diffing.
- **Does NOT provide**: anything about *authorization* — Nix/Bazel hermeticity is about reproducibility and
  correctness of derivation, not about who is allowed to change the inputs. This must be paired with §3.6/§4.1 for
  an authority story; on its own it only guarantees "the same inputs always produce the same, verifiable output,"
  which is a useful building block, not a complete answer.
- **Trust assumptions**: the build sandbox is genuinely hermetic (no ambient network/filesystem leakage) — Nix's own
  sandboxing has had documented edge cases (see the "Nix sandbox is a hidden input" source below) where the sandbox
  configuration itself becomes an unaccounted-for input, a useful caution: hermeticity claims need their own
  scrutiny, not blind trust.
- **Maturity**: Nix (1988-founded research, tool since 2003) and Bazel (Google-internal since ~2006, OSS 2015) are
  both mature, widely used.
- **Licence**: Nix — LGPL-2.1; Bazel — Apache-2.0.
- **Offline/local**: yes, both are designed to work from a local store/cache without network once dependencies are
  fetched. **No cloud required. No root** (Nix can run single-user). **Works in WSL2** (both have documented Linux
  support; Nix explicitly supports WSL2).
- **Complexity/fit**: adopting Nix/Bazel as *build systems* for Governance OS is a much larger decision than this
  study's scope (2A/2C is about runtime policy state, not the build system) — flagging the **pattern** only:
  "effective policy identity = hash of derived output," reusable for verifying that a materialized, sealed policy
  document actually matches what the floor+local composition should have produced, as a cheap self-check independent
  of trusting the composition code path every time.
- **Defect mapping**: P79‑F8 indirectly — a hash-identity check on the *derived* effective policy is a good
  belt-and-suspenders addition to §6.3, catching any composition-logic bug, not just a hand edit.
- **Classification**: **ADAPT THE PATTERN** (content-addressing effective/derived state, not raw source).
- Sources: [Nix manual — content-addressing derivation
  outputs](https://nix.dev/manual/nix/2.34/store/derivation/outputs/content-address.html), [Tweag — derivation
  outputs in a content-addressed world](https://www.tweag.io/blog/2021-02-17-derivation-outputs-and-output-paths/),
  [Farid Zakaria — "The Nix sandbox is a hidden input" (caution on hermeticity
  claims)](https://fzakaria.com/2026/07/30/the-nix-sandbox-is-a-hidden-input).

---

## 5. Precedence: how each system makes a global floor outrank a local declaration

Requested explicitly by the dispatch: how do these systems keep a lower-trust local layer from weakening a floor?

| System | Mechanism that enforces precedence | Is it a content comparison, or structural? |
|---|---|---|
| SELinux (§4.3) | `neverallow` checked against the **expanded** (compiled) policy at build time; compilation fails closed | **Structural/semantic** — checks the implied access, not the rule's wording |
| AppArmor (§4.4) | none — no cross-profile floor exists | N/A (negative case) |
| OPA multi-bundle (§4.1/§6.1) | explicit AND/deny-overrides composition of independently sourced bundles | **Structural** — floor and local are evaluated separately, then combined; local never edits or is diffed against floor |
| Kubernetes admission (§4.2) | RBAC on the policy **object type itself**; only privileged roles can write `ConstraintTemplate`/`ClusterPolicy` | **Structural** — the write path, not the content, is gated |
| TUF (§3.1) | root role's keys ultimately authorize what targets role may say; roles are hierarchical by key delegation, not by content | **Structural** — a lower role literally cannot produce validly-signed metadata outside its delegation |
| Macaroons (§3.10) | cryptographic construction (HMAC chain) makes amplification computationally infeasible, not policy-checked | **Structural**, enforced by the credential's math, not a runtime rule |
| **Current Governance OS `class` predicate** | `if n.flag(field) && !k.flag(field)` — a **single mutable file compared to a snapshot of itself** | **Content comparison** — the one approach in this table that is content comparison, and the one that is broken |

**The pattern across every mature system: precedence is structural (who can write, whose signature counts, what the
expanded closure implies) — never "diff the file against a reference copy of the same file and see what changed."**
The current defect is the outlier in this table by design, not by an implementation slip; §6.3 gives the smallest
change that moves it into the "structural" column.

---

## 6. Recommendation shape (pattern only — not an implementation)

Consistent with the brief, this is not a design to build; it names which researched patterns compose into the
smallest version of "only authenticated state has authority" at this deployment's scale, for the owner's decision.

1. **Split the single file into floor + local, matching the schema's own existing `owner_role`/`mutation` axis**
   (observed directly in `release/releases/4.1.5/kernel/overlay-templates/REPOSITORY_CONTRACT.yaml`: `governance/
   kernel/**` is already `owner_role: release-agent, mutation: prohibited`; `governance/project/**` is already
   `owner_role: change-controller, mutation: restricted`). The schema already gestures at this distinction; §2's
   failure is that `class`-driven obligations for `product/**` do not yet respect it. (§3.9, §4.1, §4.3)
2. **Seal the floor via the pattern in §3.1/§3.2/§3.6**: the floor's path→obligation mapping is produced once, at
   release-build time, by the `release-agent` role, and delivered alongside the artifact Level‑1's already-accepted
   signed release root covers (§11) — reusing one root of trust rather than inventing a second.
3. **Compose floor AND local independently (§4.1)**, never diff local against a reference copy of itself. This is
   the direct fix for P79‑F8's shape, not a smarter version of the same comparison.
4. **Read from a verified/sealed materialization, not the live working tree (§3.11)** — the kernel does not treat
   `REPOSITORY_CONTRACT.yaml` on disk as authoritative at all; it reads a copy produced only by a small local
   reconcile step off a signed git ref (§3.5/§3.6), so an un-committed or unsigned hand edit is never even reached.
5. **Fail closed and report loudly on any verification failure (§8)** — never silently fall back to the raw file.

---

## 7. Classification summary

| # | Candidate | Classification | Primary defect(s) addressed |
|---|---|---|---|
| 3.1 | TUF | ADAPT THE PATTERN | P79-F8, P79-F10, AR77-F3 |
| 3.2 | OPA signed bundles | WRAP/INTEGRATE or ADAPT | P79-F8, P79-F10, AR77-F3 |
| 3.3 | in-toto | ADAPT THE PATTERN | P79-F10 |
| 3.4 | SLSA | ADAPT THE PATTERN (rubric only) | P79-F10 (framing) |
| 3.5 | Event sourcing | ADAPT THE PATTERN | P79-F8, P79-F10 |
| 3.6 | Git SSH commit signing | **USE DIRECTLY** | P79-F8, P79-F10, AR77-F3 |
| 3.7 | cosign sign-blob (offline) | USE DIRECTLY (later, non-git artifacts) | P79-F8, P79-F10 (alt. route) |
| 3.8 | TPM sealing | HIGH-ASSURANCE ONLY / not available | none (platform gap) |
| 3.9 | Object-capabilities | ADAPT THE PATTERN (vocabulary) | P79-F8, AR77-F3 |
| 3.10 | Macaroons | ADAPT THE PATTERN (narrow-only property) | 2C narrowing requirement |
| 3.11 | GitOps principles | ADAPT THE PATTERN (reconcile step) | P79-F8, P79-F10 |
| 4.1 | OPA multi-bundle composition | ADAPT THE PATTERN | **P79-F8 directly** |
| 4.2 | K8s admission (Gatekeeper/Kyverno) | HIGH-ASSURANCE ONLY (pattern: ADAPT) | write-path gating, OC-P2-04 |
| 4.3 | SELinux neverallow | ADAPT THE PATTERN | **P79-F8 directly** |
| 4.4 | AppArmor (negative case) | ADAPT THE PATTERN (what to avoid) | cautionary |
| 4.5 | Nix/Bazel content-addressing | ADAPT THE PATTERN | P79-F8 (integrity self-check) |

**No candidate researched here is BUILD CUSTOM.** Every property Governance OS needs at 2A/2C has a mature,
citable precedent; the recommended shape in §6 assembles existing primitives (git's own signing, a composition
operator, a reconcile step) rather than adding a new one. This matches the brief's demand to be conservative about
custom code, and reduces custom surface rather than growing it.

---

## 8. REQUIRED NOW / USEFUL LATER / HIGH-ASSURANCE ONLY

**REQUIRED NOW** (fits a single owner, one WSL2 machine, offline, no cluster — implementable without new
infrastructure):
- Git SSH commit signing + `allowed_signers` verification (§3.6)
- Floor/local structural split, matching the schema's existing `owner_role`/`mutation` axis (§6.1)
- Independent AND/deny-overrides composition instead of file-vs-reference diffing (§4.1, §5)
- Fail-closed + visibly-reported refusal on any verification gap (§9)
- Event-sourcing framing for how a class change is *authored* (an appended, signed statement, not an edit) (§3.5)

**USEFUL LATER** (real value, but either needs more design than this study should pre-empt, or targets a slightly
later concern than the immediate P79-F8/F10 gap):
- cosign/Sigstore local-key signing for non-git artifacts (built plugins, release tarballs) — closer to Level 1 (§3.7)
- in-toto-style multi-step link chains, if Governance OS ever has more than one authorized functionary/role
  performing distinct steps in a contract change (§3.3)
- SLSA-style leveled self-assessment of how strong the "authenticated" claim actually is, stated honestly given the
  single-owner ceiling on two-party review (§3.4)
- Content-addressed hashing of the *derived* effective policy as an independent integrity self-check (§4.5)

**HIGH-ASSURANCE ONLY** (needs infrastructure this deployment explicitly does not have and should not acquire to
solve this problem):
- Kubernetes admission control, Gatekeeper, Kyverno as literal running systems (§4.2) — control-plane-shaped
- TPM sealing (§3.8) — not reachable from the WSL2 guest as currently configured
- Full TUF multi-role/threshold/delegation protocol (§3.1) — more custodianship than one owner with one key needs
- SELinux/AppArmor as literally-running kernel LSMs (§4.3/§4.4) — not enabled in the WSL2 kernel; cited for pattern
  only

---

## 9. Silence-is-failure (OC-P2-04) across the researched systems

Every mature system in this study treats "the check could not run" or "verification failed" as a **hard, visible**
condition, never a silent pass-through — and the one documented exception in the ecosystem is treated as a known
anti-pattern, worth citing precisely because it is the negative case:

- **OPA**: an unsigned or invalid bundle is **not activated**; OPA keeps serving the last good bundle and exposes
  bundle status (including signature failures) through its own health/status API — failure is observable, not silent.
- **TUF**: signature/threshold/expiry failures are hard client errors with no partial-trust fallback by design — this
  is a named goal of the specification (resilience requires the client to refuse, not degrade quietly).
- **Kubernetes admission webhooks**: the **existence of the `failurePolicy: Ignore` setting, and the fact that
  Kubernetes' own official documentation calls it out as appropriate only for non-security-critical webhooks**, is
  direct, citable, official confirmation that a silent-pass-on-failure default is a recognized security anti-pattern
  in this exact problem family — precisely OC-P2-04's "silence is failure" stated as platform guidance rather than
  our own house rule.
- **SELinux**: a `neverallow` violation is a **compile failure** — the new module simply does not load; there is no
  silent partial-application state.
- **git commit signature verification**: `git verify-commit`/GitHub-style "Verified" badges either state "Good
  signature," or produce an explicit failure/absence of the badge — no ambiguous state.

**Implication for §6**: the recommended reconcile-and-seal step (§3.11) must, on any verification failure, refuse to
update the materialized effective policy (keep serving the last-known-good sealed state, matching OPA's own
documented behavior) **and** emit a reported, non-silent refusal — not merely decline to apply the change quietly.
This is the same discipline that closed AR77-F3/P79-F8's "refused by nothing and reported nowhere" gap: refusal
without a report is, per OC-P2-04, still a defect even if the underlying state itself stayed safe.

---

## 10. Simplification opportunities (per COMMON-BRIEF §7)

- **One authority source instead of several enumerations.** Today: a single mutable `class` field, checked by (per
  the escalation package) **12+ consumers across `cit/`, `context/`, `memory/`**, each a separate place that must
  independently get the enumeration right. Under §6: a single sealed, derived effective-policy document is the one
  thing every consumer reads; the "which consumers need updating when a new obligation is added" problem (the exact
  shape that has failed five times per COMMON-BRIEF §1) is deleted, not enumerated more carefully — every consumer
  reads the *output* of composition, never the raw project file.
- **One root of trust instead of two.** §11 shows Level 1 already has an accepted signed-release-root direction.
  Extending it to also seal the authority floor (§6.2) avoids standing up a second, differently-shaped trust
  mechanism for what is structurally the same question ("is this state the one an authorized party produced").
- **Delete the comparison predicate, not extend it.** `policy_precedence.rs:677`'s one-directional check, and the
  bidirectional version Option (i) in the escalation package considered, are both instances of the enumeration
  pattern the brief specifically asks to stop accumulating. §4.1's AND-composition removes the comparison step
  entirely rather than making it symmetric.
- **Reuse existing git/SSH key material.** No new PKI, no new agent, no new credential store: the same SSH key
  already used for repository access becomes the authority key (§3.6), which is both a complexity reduction and a
  smaller new-attack-surface than any of the alternative signing mechanisms researched.

---

## 11. Relationship to existing Level-1 work — an important caution

COMMON-BRIEF §3 describes Level 1 as "Existing direction: a compact TUF-style release root, accepted at R0/R1." That
framing is accurate for the *original baseline* but incomplete on its own: `release/root-of-trust/meta-review/
00-*.md` (dated within this program, read directly for this report) records that the **subsequent** attempt to
harden and extend that same root of trust — Root-of-Trust revision 1 through 7 (three offline root keys, threshold
custodians, 24-hour trust-state currency, diverse-double-compilation, the CP-1 first-contact protocol) — was
**rejected on every revision**, and the meta-review's own recommended disposition is: *keep the small, original
Phase‑1-normative core (immutable versioned release, manifest, file hashes, independent verification, source
authenticity before install, no source self-authorization) as settled; do **not** create Revision 8; treat the
larger custodianship/threshold/freshness protocol as a separate, later, owner-gated decision, not a Phase‑1 gate.*

**This matters directly for §6's recommendation.** The signed-release-root primitive this report proposes reusing
for authority-bearing configuration is the **small, Phase‑1-normative core the meta-review says is sound** — a
single signing key, hashed and versioned artifacts, independent verification — **not** the larger CP-1/OP-1..16
protocol that is currently frozen pending a meta-architecture review the owner has not yet held. Recommending reuse
of the *contested, high-assurance* extension here would import an unresolved Level‑1/Level‑3 dispute into a Level‑2
research question, which COMMON-BRIEF §3 explicitly warns against ("Do not let Level 3 contaminate Levels 1–2").
Recommending reuse of the **settled small core** avoids that contamination and is consistent with "REQUIRED NOW"
being achievable without waiting on the frozen RoT-1 loop to resolve.

---

## 12. What I could not determine

- **WSL2/TPM current status.** I found a 2023 open GitHub issue on `microsoft/WSL` requesting native TPM support and
  a community bridge tool (`tpm2-send-tbs`) that proxies to the Windows host's TBS rather than providing genuine
  guest-side measured boot. I could not find an authoritative, dated 2025–2026 statement confirming or denying that
  native TPM device passthrough has since shipped. I am treating "not reliably available" as the working assumption
  and flagging it as unverified currency rather than asserting it confidently either way, per the brief's instruction
  to say plainly where evidence is thin.
- **Whether AppArmor genuinely has no floor-equivalent to `neverallow`, stated in AppArmor's own official docs.** My
  claim in §4.4 is drawn from general architecture literature contrasting the two LSMs and from the absence of any
  AppArmor equivalent turning up in searches specifically for one; I could not locate an AppArmor upstream document
  that states this gap in its own voice the way SELinux's ecosystem documents `neverallow`. Treat §4.4 as a
  reasonably confident inference, not a directly-sourced claim, and weight it accordingly.
- **Whether OPA's Go/WASM evaluator is a realistic embed inside the existing Rust kernel**, versus reimplementing
  just the signature-and-composition primitives in Rust directly (§3.2's ADAPT alternative). This is an engineering
  feasibility question for whoever scopes an actual build, not something I could resolve from documentation alone —
  I did not find a canonical, current example of OPA's Rust WASM bindings maintained to production quality, and did
  not attempt to test one, since this is read-only research.
- **The exact current behavior of the 12+ undocumented `class()` consumers** in `cit/`, `context/`, `memory/` cited
  by the escalation package. I read the escalation package's account of them but did not re-derive or re-verify that
  count myself against the current source tree — Level 2A/2C research does not require re-litigating a finding
  Research Agent scope did not ask me to re-prove, and the brief's absolute constraints forbid touching product code
  to check. Treat the "12 further consumers" figure as sourced to the escalation package, not independently
  reproduced here.
- **Whether the product owner would accept single-key (bus-factor-of-one) signing as sufficient "authentication"**
  for a single-owner deployment, versus wanting some form of split custody even at this scale. This is squarely an
  owner decision the brief says I should not make; §6 states the primitive but not this policy choice.

---

## 13. Sources (consolidated)

- [TUF specification](https://theupdateframework.github.io/specification/latest/); [TUF metadata/roles
  docs](https://theupdateframework.io/docs/metadata/)
- [OPA — Bundles / signing](https://www.openpolicyagent.org/docs/management-bundles); [OPA CLI
  reference](https://www.openpolicyagent.org/docs/cli); [OPA FAQ — composing team
  policies](https://www.openpolicyagent.org/docs/latest/faq/)
- [in-toto specification v1.0](https://github.com/in-toto/specification/blob/v1.0/in-toto-spec.md)
- [SLSA — security levels](https://slsa.dev/spec/v0.1/levels); [SLSA — build
  provenance](https://slsa.dev/spec/draft/build-provenance)
- [Azure Architecture Center — Event Sourcing
  pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [GitHub Docs — commit signature
  verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification);
  [GitLab — SSH signed commits](https://docs.gitlab.com/user/project/repository/signed_commits/ssh/)
- [Sigstore — signing blobs](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/); [cosign offline
  verification issue](https://github.com/sigstore/cosign/issues/2255)
- [microsoft/WSL issue #10777 — TPM support](https://github.com/microsoft/WSL/issues/10777)
- [Mark S. Miller — *Capability Myths
  Demolished*](https://papers.agoric.com/assets/pdf/papers/capability-myths-demolished.pdf); [Norm Hardy — *The
  Confused Deputy*, ACM SIGOPS OSR 22(4), 1988](https://dl.acm.org/doi/10.1145/54289.871709)
- [Birgisson et al. — *Macaroons*, NDSS 2014](https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/)
- [OpenGitOps — principles](https://github.com/open-gitops/documents/blob/main/PRINCIPLES.md)
- [Kubernetes — Admission Webhook Good
  Practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/);
  [Kyverno — Policy Exceptions](https://release-1-12-0.kyverno.io/docs/writing-policies/exceptions/)
- [Red Hat — SELinux `neverallow`](https://access.redhat.com/solutions/2110661); [Gentoo wiki — SELinux
  policy](https://wiki.gentoo.org/wiki/SELinux/Policy)
- [Nix manual — content-addressing derivation
  outputs](https://nix.dev/manual/nix/2.34/store/derivation/outputs/content-address.html)
- In-repo: `release/orchestration/phase-2/RESEARCH/COMMON-BRIEF.md`;
  `release/orchestration/phase-2/PHASE_2_OPTION_B_ESCALATION_PACKAGE.md`;
  `release/releases/4.1.5/kernel/overlay-templates/REPOSITORY_CONTRACT.yaml`;
  `release/root-of-trust/meta-review/00-*.md`
