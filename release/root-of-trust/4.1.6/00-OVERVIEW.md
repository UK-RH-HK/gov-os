# Governance OS Root-of-Trust Architecture (RoT-1) — root-cause escalation for 4.1.6

| | |
|---|---|
| **Status** | PROPOSED — `ROOT_OF_TRUST_ARCHITECTURE_READY_FOR_INDEPENDENT_REVIEW` (not approved, not implemented) |
| Author role | Independent Governance OS Root-of-Trust Architect (fresh session; no builder or verifier context carried) |
| Date | 2026-09-13 |
| Rejected baseline | branch `release/4.1.5-rc1`, tag `v4.1.5-rc1`, commit `da9c8518d3fddba6f37bafb4d046ca313335ec1f`, payload `release/releases/4.1.5` (release_hash `962f9848…a314b`) |
| Target | immutable PATCH candidate 4.1.6 on `release/4.1.6-rc1`, migration `M-4.1.5-4.1.6` |
| Governing documents | framework v4.1.2 (§2, §28–32, §72, §75A–75H, §78–83), release/distribution protocol v1.2 (§1–§17), adoption/audit protocol v3.0 (§4, §11, §16) |
| Not modified | No runtime, CLI, kernel (`framework/`), migration, tool registry, fixture, test, released payload or verifier artefact. D-0007 is **not** edited (see §4.4). Additions only: this directory, `spec/decisions/D-0008.yaml` and `spec/architecture/ARCH-0002.yaml` (both **PROPOSED — pending owner approval, not active, not approved**; record status field `PROVISIONAL` because the record schema has no `PROPOSED` value; `state_class: NARRATIVE`, `in_effect: false`, no `chosen_option`), two index rows in `docs/DECISIONS.md` |

## Document map (one file per required output)

| # | Required output | File |
|---|---|---|
| — | Summary, vocabulary, root cause, gate assessment | `00-OVERVIEW.md` (this file) |
| 1 | Root-of-Trust Threat Model | `01-THREAT-MODEL.md` |
| 2 | Complete privileged-ingress map | `02-INGRESS-MAP.md` |
| 3 | Trust-chain diagram | `03-TRUST-CHAIN.md` |
| 4 | Canonical release-authentication architecture | `04-AUTHENTICATION-ARCHITECTURE.md` |
| 5 | Key-management model | `05-KEY-MANAGEMENT.md` |
| 6 | Bootstrap model | `06-BOOTSTRAP.md` |
| 7 | Release-envelope / statement schema specification | `07-RELEASE-ENVELOPE-SPEC.md` + `schemas/*.schema.json` + `examples/` |
| 8 | `framework.lock` changes | `08-FRAMEWORK-LOCK.md` |
| 9 | init/adopt/update/reinstall/rollback/recovery integration | `09-INTEGRATION-REQUIREMENTS.md` |
| 10 | Retrieval-profile trust integration | `10-RETRIEVAL-PROFILE-TRUST.md` |
| 11 | Migration plan from 4.1.5 | `11-MIGRATION-PLAN.md` |
| 12 | Independent acceptance-test plan | `12-ACCEPTANCE-TEST-PLAN.md` |
| 13 | Backwards-compatibility consequences | `13-COMPATIBILITY.md` |
| 14 | Risks / trade-offs | `14-RISKS.md` |
| 15 | D-0007 supersession | `15-D-0007-SUPERSESSION.md` |
| 16 | Proposed ADR for 4.1.6 | `16-ADR-D-0008.md` → `spec/decisions/D-0008.yaml` |
| — | Escalation probe evidence | `evidence/ESCALATION_PROBES.md`, `evidence/probe.sh`, `evidence/regen.py`, `evidence/probe-output.txt` |

---

## 1. Executive summary

**The defect class.** Four consecutive candidates (4.1.3 → 4.1.5) were rejected for the same family of failure: a fact
that confers privilege (*registered*, *approved*, *verified*, *certified*) was derived from an artefact that the party
seeking the privilege could write. D-0007 named the rule correctly — *a lower-trust input may never manufacture a
higher-trust fact* — and closed the use-time instances. V-H3 is the install-time instance: `gov init` / `gov update`
stage an arbitrary source, **regenerate** `KERNEL_MANIFEST.json` from it, write `framework.lock.kernel_manifest_hash`
from that regenerated manifest, and afterwards `kernel_trust` reports `verified: true` because three artefacts written
from the same untrusted bytes agree with one another.

**The escalation finding.** This session reproduced V-H3 and demonstrated that the problem is wider than the reported
defect and that the bounded repair proposed in the 4.1.5 report §12 would not close it (`evidence/ESCALATION_PROBES.md`,
all executed against the 4.1.5 binary rebuilt from HEAD in scratch directories):

| Probe | What was shown | Consequence |
|---|---|---|
| **E1** | A tampered 4.1.5 source whose `manifest.json` and `KERNEL_MANIFEST.json` are *regenerated* passes `gov release verify` with `ok: true`, `release_hash_matches_kernel: true` | Verifying a source "against its shipped manifest" (report §12(a)) and "declared vs recomputed release_hash" (§12(b)) are both circular: the attacker supplies the reference data |
| **E2** | The same source with `certification.status: CERTIFIED` written into its own `manifest.json`: `update --check` → `human_gate_required: false`, recommendation "safe"; `update --apply` **without `--approve`** → `applied: true`, no gate record created; `kernel trust verified: true`; installed `never_index_classes: [secret]` | An **authorisation** fact (whether a human gate is required) is read from a caller-controlled file. V-H3 as reported needed an answered gate; E2 needs none |
| **E3** | Poisoning the materialised embedded-kernel cache (`$GOV_KERNEL_CACHE` / `~/.cache/gov/kernels/<v>-<id>`) makes a later `gov init` with no `--source` install the poisoned kernel labelled `embedded:agentic-engineering-os@4.1.5`, `verified: true`; and the V-H2 fail-closed baseline substituted for a tampered kernel is read from the same poisoned cache (effective `never_index_classes: [secret]`) | D-0007's highest trust class ("the embedded kernel payload in the binary") is in practice a mutable directory trusted by a `.complete` marker file |
| **E4** | Editing an installed kernel and regenerating `KERNEL_MANIFEST.json` + `framework.lock` hashes (the shape a `git pull` delivers) → `verified: true`, doctor D003/D004/D029 all ok | Every consumer repository collaborator can install an arbitrary kernel through Git without running `gov` at all |
| **E5** | Tampering an update snapshot under `.governance-runtime/update/<v>/` and running `gov update --rollback` → `kernel_ok: true`, `verified: true`, floor removed | Rollback is an unauthenticated privileged ingress |

**Root cause (§4).** Trust was defined by *agreement among artefacts* rather than by *derivation from an anchor the
artefacts cannot influence*. Hashing cannot fix this: a hash only moves the question to "who chose the hash".

**Recommendation — RoT-1.** One non-circular chain for every ingress:

```text
trust-root metadata compiled into the gov binary (T0)
  → DSSE-signed release statement (Ed25519 over RFC 8785 canonical JSON)
  → release identity + complete kernel file map + component/migration digests
  → authenticate the source bytes in quarantine (signature, role, revocation, identity, digests, compatibility, downgrade)
  → AuthenticatedRelease capability object (the only input install code accepts)
  → transactional install (stage → swap → migrate → governance/trust/ statement → framework.lock commit)
  → use-time kernel_trust v2: installed files ≡ installed statement ∧ statement signature verifies under T0 ∧ not revoked
```

Certification, revocation and reference retrieval profiles are separate signed statements under separate key roles.
`framework.lock` records the authenticated identity and is never consulted as a source of trust. Unsigned development and
test material has explicit, permanently labelled paths that cannot produce a production-authenticated or certified
state. Private GitHub (or any other host) is a transport only; verification is offline.

**Gate assessment (§5).** No architecture-selection Human Decision Gate is raised: the alternatives were evaluated
(`04-AUTHENTICATION-ARCHITECTURE.md` §1) and are not materially equivalent. D-0008 nevertheless requires its ordinary
approval gate before implementation, because it supersedes an ACTIVE constitutional trust decision and assigns key custody
to named humans; the owner-parameterised values it needs are listed in §5 with recommended defaults.

---

## 2. Inputs and method

Read in full or at the relevant sections: the three governing documents; D-0002, D-0005, D-0006, D-0007, ARCH-0001,
API-0001/0002, RES-0001; all independent verification reports (4.1.2, 4.1.3, 4.1.4, 4.1.5) with `VERDICT.md`, the V-H3
evidence, the 4.1.5 migration-chain report and the four held-out harnesses; the 4.1.5 repair report; `docs/ARCHITECTURE.md`
§4.4a and `docs/RELEASE.md`; and the implementation of every path that can write or select kernel material:
`runtime/build.rs`, `kernel.rs`, `kernel_trust.rs`, `lock.rs`, `release.rs`, `update.rs`, `init.rs`, `adopt.rs`,
`recovery.rs`, `project.rs`, `doctor.rs`, `migrations/framework.rs`, `capabilities/{host,registry,governance}.rs`,
`tools.rs`, `memory/{benchmark,embedder}.rs`, `orchestration/control.rs`, `cli/src/main.rs`, and the reference plugin
`capabilities/python/govos_capabilities/embed_sentence_transformers.py`.

Every claim about current behaviour in this pack cites either source or an executed probe. Nothing from builder or
verifier narrative was taken on trust where it could be checked.

## 3. Vocabulary — four properties the architecture keeps separate

| Property | Question it answers | Mechanism in RoT-1 | What it never implies |
|---|---|---|---|
| **Integrity** | Are these bytes identical to a reference digest? | SHA-256 file map, tree digest, component digests | Anything about who chose the reference digest |
| **Authenticity** | Was the reference digest issued by a key the OS trusts *for this purpose*? | Ed25519 signature over a canonical statement, key and role resolved from trust-root metadata compiled into the binary (T0), not revoked | That the material is good, certified, or permitted here |
| **Provenance** | How was the material produced and delivered (commit, build, verifier, transport)? | Fields *inside* an authenticated statement; ledgers; logical source references | Trust. Provenance outside a signed statement is a descriptive claim |
| **Authorisation** | May this actor adopt this authenticated material into this project now? | Certification statements, human gates bound to the statement digest, authority levels, downgrade and minimum-trust policy | Authenticity. Authorisation is evaluated only on an already authenticated object |

Current artefacts, classified honestly:

| Artefact (4.1.5) | What it actually provides |
|---|---|
| `governance/kernel/KERNEL_MANIFEST.json` | integrity reference **issued by the installer from the bytes it installed** (self-referential) |
| `framework.lock.kernel_manifest_hash` / `release_hash` | integrity record, repository-writable, derived from the above |
| release `manifest.json` / `manifest.yaml` | unsigned descriptive provenance; certification block edited by hand after the build |
| `gov release verify` | self-consistency of a directory against its own manifest (E1) |
| embedded payload in the binary | authentic *as compiled*, but consumed through an unverified disk cache (E3) |
| gate records, plugin registry, governed exceptions | authorisation / OS-written project state (T2) — sound after 4.1.5 |

## 4. Root cause — why D-0007's trust levels became circular at installation ingress

### 4.1 The precise circularity

D-0007 defines T1 as "the embedded kernel payload in the binary, **and an installed kernel whose payload matches
`KERNEL_MANIFEST.json` AND whose manifest matches `framework.lock.kernel_manifest_hash`**". At installation:

1. `kernel::install_kernel_inner` copies the source into `governance/kernel/` and **writes** `KERNEL_MANIFEST.json`
   with `build_manifest(dest)` — the manifest is computed from the bytes just copied;
2. `lock::write_lock` **writes** `kernel_manifest_hash = manifest_hash(manifest)` and `release_hash = payload_hash` from
   that manifest;
3. `kernel_trust::compute` later declares T1 when (1) matches the files and (2) matches (1).

All three inputs to the T1 predicate are outputs of a function whose only input is the untrusted source. The predicate
is therefore a tautology at install time: *any* source satisfies it. D-0007's own rule (2) — "*verified* is a fact of
T1/T2 only" — is violated inside the definition of T1, because the verification computation consumes only T4/T5 data.

### 4.2 Contributing design errors

| # | Error | Where it shows |
|---|---|---|
| C1 | **Class by agreement, not by derivation.** T1 membership was a relation among artefacts that live in repository-writable locations (`governance/**` is Git-tracked; T4 write access) | V-H3, E4 |
| C2 | **No class for incoming material.** A `--source` path, a release directory, `GOV_CANONICAL_ROOT`, a snapshot or a Git merge is caller- or repository-controlled (T5/T4) by provenance, yet was consumed as "immutable release state" | V-H3, E5 |
| C3 | **Authorisation read from the source.** `update::check` sets `human_gate_required = … \|\| cert != "CERTIFIED"` with `cert` read from the source's own `manifest.json`; `supported_from_versions`, `migration_ids`, `breaking_changes` and `human_gates` come from the same file | E2 |
| C4 | **The only independent anchor was never used at ingress, and was not itself protected.** The embedded payload is consulted only as the use-time fallback; it is materialised into a user cache reused on a `.complete` marker, and "embedded" vs "release" vs "source" labels are assigned by path-string matching (`is_embedded_dir`, `source_label`) | E3 |
| C5 | **Rules constrained readers, not writers.** D-0007 rule (1) governs where enforcement *reads* floors; nothing governs which code paths may *write* T1 locations (init, init --force, adopt batch 0, update, automatic rollback, explicit rollback, kernel reinstall, Git) | ingress map I-01…I-15 |
| C6 | **"Authenticated" was never defined and was implemented as integrity.** The same word `verified` is used for both properties in `kernel trust`, doctor D029 ("authenticated against the release identity") and `docs/ARCHITECTURE.md` §4.4a | V-H3 wording |
| C7 | **The proposed bounded repair inherits the error.** Verifying a source against its shipped manifest is verifying against attacker-supplied reference data | E1 |

### 4.3 Why only an asymmetric anchor closes the class

A non-circular check needs a reference value that (a) exists before the source is seen, (b) cannot be produced by
whoever controls the source, repository, cache, environment or transport, and (c) can still be extended after the binary
ships (new releases, certification, revocation). A digest compiled into the binary satisfies (a) and (b) but not (c).
A public key compiled into the binary, validating signatures made by a private key that never touches any of those
locations, satisfies all three. RoT-1 uses both: signed statements for extensibility, compiled-in trust-root metadata
and revocation floors for the anchor.

### 4.4 How D-0007 is treated

D-0007 is superseded, not silently contradicted and not partially amended (`15-D-0007-SUPERSESSION.md`). Its rules (1)–(4)
remain correct and are restated verbatim in D-0008; its trust-class table is replaced (T0 added, T1 redefined by
derivation, installed files and all incoming material explicitly placed in T4/T5) and five rules are added. This session
does **not** mark D-0007 SUPERSEDED: changing an ACTIVE authoritative decision before the owner approves D-0008 would
itself be a lower-trust actor manufacturing a higher-trust fact. The status change is part of the approved 4.1.6
implementation.

## 5. Human Decision Gate assessment and owner parameters

**No architecture-selection gate.** Six trust-root designs were evaluated (`04-AUTHENTICATION-ARCHITECTURE.md` §1):
hash hardening only, a binary-embedded digest registry only, signed statements with compiled-in keys (RoT-1), keyless
transparency-log signing, Git-signed tags, and a full TUF deployment. Only RoT-1 meets every mandatory requirement
(non-circular, offline, extensible after ship, provider-neutral, key rotation and revocation, dev/test separation).
The others fail at least one hard requirement or reduce to a component of RoT-1.

**Ordinary approval gate for D-0008 (required).** D-0008 is R5 (constitutional trust model, key custody). It must be
presented and answered by the product owner before implementation begins. The following parameters are decided in that
gate; none of them changes the architecture:

| ID | Parameter | Recommended default |
|---|---|---|
| OP-1 | Root role: number of keys, threshold, custodians | 3 keys, threshold 2, three named human custodians, offline hardware-backed or air-gapped storage |
| OP-2 | Release role custody | 1 active key on a hardware token used on an isolated signing host, plus 1 pre-registered standby key held separately |
| OP-3 | Adoption policy for authenticated-but-uncertified releases | `init`: allowed and labelled; `update`: Human Decision Gate bound to the statement digest (preserves today's behaviour); `REJECTED`: gate; `REVOKED`: refused |
| OP-4 | Separate `candidate` signing role? | No — candidates are signed by the release role; certification is a separate statement |
| OP-5 | Revocation-freshness warning age | 180 days, informational (doctor MEDIUM), overlay may make it gating |
| OP-6 | Require `--confirm-trust-root <id>` on first `gov init` | No in automation; the fingerprint is always printed in human output |

## 6. Verdict of this escalation

The recommended architecture is RoT-1 as specified in outputs 1–16. It closes V-H3 and E1–E5 at the root, gives every
ingress one authentication boundary, keeps integrity checking after installation, and keeps D-0007's use-time repairs
(V-H1, V-H2, V-M1) intact.

`ROOT_OF_TRUST_ARCHITECTURE_READY_FOR_INDEPENDENT_REVIEW`
