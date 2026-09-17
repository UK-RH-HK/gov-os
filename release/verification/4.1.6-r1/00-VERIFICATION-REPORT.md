# AR-0027 — Fresh independent R1 candidate verification of the Signed Release Root v1

| Field | Value |
|---|---|
| Run | `AR-0027`, role `verifier-a` |
| Gate | `GATE-R1-CANDIDATE-ACCEPT` |
| Handoff | `HO-0027` (`release/orchestration/phase-1/HANDOFFS/HO-0027-r1-candidate-verification.md`) |
| Candidate | `srr1-r1-candidate-1` — builder work commit `949c4d343a6d5f203534afa6e3363992fee12488` (AR-0026) |
| Verified at worktree HEAD | `0ce7f9f0a7028d54bc5beef57f0ef35a935e244d`, branch `phase1/srr1-r1-verify` |
| Toolchain | `cargo 1.98.1 (e35f3d1c1 2025-03-11)`, Linux 6.6.87.2-microsoft-standard-WSL2 |
| **Verdict** | **`BLOCKING_FINDINGS_PRESENT`** |
| Blocking findings | 1 (MEDIUM) — `AR27-B1`, see `10-BLOCKING-FINDINGS.md` |
| `REQUIRES_R0_OR_OWNER_ADJUDICATION` | none among the blocking findings; one `NEW_OWNER_DECISION_REQUIRED` item (`AR27-OD1`) is so flagged |

## Independence

I did not author this implementation, the `ARCH-0003` architecture, the R0 correction, or either R0 review. I authored
every test in `evidence/heldout-tests/` myself; the builder has not seen them. They deliberately do **not** reuse
`tests/certification/srr_material.rs`, so the attack material is built from an independent reading of the wire format
rather than inheriting the builder's fixture assumptions.

I modified **no product source**. My held-out suite lives in a standalone cargo crate outside the product tree and
outside its workspace, depending on `gov-runtime` by path, so verifying this candidate required no edit to any product
file, manifest or test. The only capability my crate has that the product deliberately lacks is **signing** — attacking
a signature-verification adapter requires forging, so the harness carries `ed25519-dalek` with the signing feature.

I delegated nothing. No subagent was used. I read no session transcript or task-output store, opened no user
auto-memory, and did not contact the product owner.

## Digest verification (pre-condition — no STOP condition)

Every pinned digest in `HO-0027` was verified before use. All matched.

| Artefact | Expected | Result |
|---|---|---|
| `…/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` | `70977d11…f1699c1` | **match** |
| `…/00-ARCHITECTURE.md` | `695aa185…` | **match** (`695aa185ab32a813cd596b12f80d235afb92d56f147f395b15f16e37d0bcd983`) |
| `OWNER-DECISION-0006` | `90340772…28d1db` | **match** |
| `Governance_OS_Capability_Acceptance_Contract_v3.md` | `4c2df291…7cb5ed3` | **match** |
| `ARCH-0003.yaml` accepted **body scalar** | `093cb78e…f8f71536a` | **match** |
| `ARCH-0003.yaml` file at acceptance commit `2b36b44` | `42681978…` | **match** |

`ARCH-0003.yaml`'s current file digest is `f24ed672…`, which differs from the acceptance-commit digest. I confirmed this
is benign: `git diff 2b36b44 HEAD -- spec/architecture/ARCH-0003.yaml` is **16 insertions, 1 deletion**, entirely the
`r0_acceptance:` governance-annotation block and the `review_state` transition. The accepted **body** is byte-identical,
which the body-scalar digest above proves independently. I also re-verified all eight digests in the builder's own
`REVIEWED-CONTENT-DIGESTS.txt`; all matched.

## Regression reproduced

Run with `GOV_*` stripped from the environment and `CARGO_TARGET_DIR` in scratch:

| Suite | Builder claim | Orchestrator | **Reproduced by AR-0027** |
|---|---|---|---|
| `cargo test --lib` | 26 passed | 26 | **26 passed; 0 failed; 0 ignored** (0.40s) |
| `cargo test --test certification` | 64 passed | 64 | **64 passed; 0 failed; 0 ignored** (98.92s) |

Exact match, no pre-existing failures.

## Held-out evidence authored for this verification

29 independently authored tests, all passing, in four groups. Passing here means "the asserted behaviour is what the
candidate does" — several tests deliberately assert an **observed weakness** rather than a desired behaviour, and are
labelled `OBSERVED:` in-source so they read as findings rather than approvals.

| Group | Tests | Covers |
|---|---|---|
| `heldout_srr.rs` | 12 (`a1`–`a12`) | cryptographic/TUF adapter: signature-over-different-document, key-id confusion, role confusion, threshold-by-repetition, unsatisfiable/zero thresholds, trailing bytes, duplicate `signed` member, unsigned envelope, malleability/non-canonical `S`, unsupported scheme, spec-version and role-type confusion |
| `heldout_srr2.rs` | 8 (`b1`–`b2`, `c1`–`c6`) | expiry-comparison attacks; floor binding across the whole ingress set; identity/payload/channel/platform binding; unsigned-input refusal and anchor-removal fail-closed; posture relocation; environment authority; floor durability and monotonicity |
| `heldout_srr3.rs` | 5 (`d1`–`d5`) | all ten `OWNER-DECISION-0006` requirements: authority forgery, wrong machine, expiry, version-only token, wrong payload digest, entry record, byte-exact marking, single-use nonce, floor-not-lowered, exit policy, no-network operation |
| `heldout_srr4.rs` | 4 (`e1`–`e4`) | trust-anchor expiry; timestamp/snapshot optionality and snapshot binding; atomic commit and post-interruption replay; authentic/intact/admissible separation |

Sources in `evidence/heldout-tests/`, full output in `evidence/HELD-OUT-TEST-OUTPUT.txt`, reproduction in
`evidence/REPRODUCTION.md`.

---

# Disposition of the frozen R1 section, item by item

The frozen boundary's R1 section lists twelve criteria. Each is dispositioned below against this exact candidate.

### R1-1 — "a mature reviewed TUF/cryptographic implementation is used correctly" — **SATISFIED**

`ed25519-dalek` 2.2.0 (RustCrypto/dalek-cryptography), `verify_strict` only on the live path. No curve, point-decompression
or malleability logic is reimplemented. Key ids are **derived** from key material (`sha256(pubkey)`) and compared against
the document's claimed id, so metadata cannot rename a key onto another key's authority. Signing is over the **exact
bytes of the `signed` member**, extracted with `serde_json::value::RawValue`, and the policy is parsed from those same
bytes — there is no canonicalisation step for a producer and consumer to disagree about, and no way to present one
byte-string to the signature check and a different parse to the policy.

All twelve adapter attacks failed closed:

| Attack | Result |
|---|---|
| Valid signature over document A presented on document B | `SRR_THRESHOLD_NOT_MET` (control: same signature verifies on its own document) |
| Key id pointed at another key's public bytes | `SRR_KEYID_MISMATCH` |
| Timestamp-role key signs `release.json`; snapshot-role key signs `release.json` | `SRR_THRESHOLD_NOT_MET` |
| One valid signature repeated 4× against a 2-of-2 role | `SRR_THRESHOLD_NOT_MET`, `accepted_keyids` length 1 (control: 2 distinct keys verify) |
| `threshold: 3` with 1 listed key | `SRR_UNSATISFIABLE_THRESHOLD` |
| `threshold: 0` | `SRR_METADATA_MALFORMED` |
| Trailing bytes after the envelope (`{"extra":1}`, `\n{}`, `garbage`, `\0`) | `SRR_METADATA_MALFORMED` (all four) |
| Duplicate `signed` member (last-wins confusion) | `SRR_METADATA_MALFORMED` |
| Empty `signatures` array | `SRR_METADATA_UNSIGNED` |
| Malleated signature (`S + L`, non-canonical) | does not verify |
| `keytype: rsa` | `SRR_UNSUPPORTED_KEY_SCHEME` |
| `spec_version: srr/2`; `_type` confusion | `SRR_UNSUPPORTED_SPEC_VERSION`; `SRR_METADATA_WRONG_ROLE` |

Non-blocking: `AR27-N4` (an unreachable permissive-fallback `crypto::verify` on the public surface) and `AR27-N3`
(optional timestamp/snapshot roles, R2).

### R1-2 — "candidate/source files cannot create their own trusted identity" — **SATISFIED**

Verified directly (`heldout_srr4.rs::e4`): a candidate whose payload, `KERNEL_MANIFEST.json` and lock are perfectly
mutually consistent — the exact "mutually consistent files delivered with the copy" case `OWNER-DIRECTIVE-0004`
forbids as an authenticity root — is refused with `SRR_RELEASE_UNVERIFIED` on a provisioned machine. Identity comes
only from signed metadata chaining to the protected root anchor, or from the machine's own protected installed record.
`provision()` additionally refuses an anchor sourced from inside a governed project or from any `.git`/`governance`
path component. `Release::parse` requires `product`, `repository`, `channel`, `release_version`, both payload digests
and at least one payload file; all are compared against the **staged measurement**, never against the candidate's own
claims.

### R1-3 — "wrong keys, modified metadata/payload/migration, replay, downgrade and expiry all fail closed" — **SATISFIED**

Measured end-to-end against a real provisioned machine (`heldout_srr2.rs::c1`, `::c2`):

| Input | Result |
|---|---|
| Release signed by an unauthorised key | `SRR_THRESHOLD_NOT_MET` |
| `product` altered | `SRR_WRONG_PRODUCT` |
| Requested channel ≠ bound channel (`SRR-R0-L2`) | `SRR_WRONG_CHANNEL` |
| `payload_hash` altered | `SRR_PAYLOAD_DIGEST_MISMATCH` |
| Signed file absent from the payload | `SRR_PAYLOAD_FILE_MISSING` |
| Payload file the metadata does not authorise | `SRR_PAYLOAD_FILE_UNAUTHORISED` |
| Migration in the payload the metadata does not name | `SRR_MIGRATION_NOT_AUTHORISED` (encountered organically while building my own fixtures) |
| Unsupported platform | `SRR_UNSUPPORTED_PLATFORM` |
| Expired release metadata (canonical form) | `SRR_METADATA_EXPIRED` |
| Older metadata version replayed | `SRR_METADATA_ROLLBACK` against the protected high-water |
| Lower release sequence (downgrade) at any ingress | `SRR_BELOW_FLOOR` |

Expiry caveats `AR27-N1` (non-canonical RFC-3339 forms, and absent `expires`) and `AR27-N2` (expired trust anchor) are
recorded as non-blocking: both require **publisher** deviation rather than adversary action, because `expires` is
inside the signed byte-string and any adversary edit breaks the signature.

### R1-4 — "all privileged ingress paths call the common verifier" — **SATISFIED**

The claim is compiler-enforced and I confirmed it holds. `kernel::install_kernel` takes `&crate::srr::AuthenticatedRelease`
and there is **no path-taking variant**; `AuthenticatedRelease` has no public constructor and is produced only by
`srr::verifier::admit`. Enumerated exhaustively:

- `srr::admit` call sites — exactly 5: `init.rs:237`, `adopt.rs:638`, `update.rs:213` (apply), `update.rs:450` (rollback), `cli/src/main.rs:939` (kernel reinstall).
- `install_kernel` call sites — exactly 5: `init.rs:244`, `adopt.rs:642`, `update.rs:220`, `update.rs:467`, `cli/src/main.rs:944`. Every one passes a value obtained from `admit`.

The floor check lives **inside** `admit`, scoped over the `Ingress` enum rather than named after one operation, so it
binds the whole set. I verified this at runtime rather than trusting the structure: after a verified install at
sequence 40, a signed release at sequence 9 was refused with `SRR_BELOW_FLOOR` at **`update`, `init`, `adopt`,
`reinstall`, `recovery` and `rollback`** alike (`heldout_srr2.rs::c1`).

**The declared exception — the update transaction abort — probed and found not to be a usable bypass.**
`rollback_internal` is a **private** function with exactly two callers: `rollback_opts` (`transaction_abort = false`,
the only public entry, and where the CLI's `update --rollback` lands at `cli/src/main.rs:816`) and one call inside
`apply_update_opts`'s error arm with `transaction_abort = true`. It is therefore unreachable from the CLI, from any
other module, and from any other crate. On that path: the restored bytes come from a snapshot created earlier **in the
same function call** from the machine's own installed tree, after `remove_dir_if_exists(&snap)` destroys anything
pre-planted at that path; `admit` has already succeeded, so the floor check already passed; and `record_installed` is
**not** called (`protected` is `Value::Null`), so no floor advances and no `InstalledRecord` is written. It manufactures
no authenticity and no admissibility claim. The builder's characterisation is accurate.

### R1-5 — "verified bytes are staged, installed and used without substitution" — **SATISFIED**

`staging::stage` copies the candidate into private machine-state staging **first** and measures the staged copy; the
signed digests are compared against that measurement; `AuthenticatedRelease::verified_payload()` returns the same
staging directory and is the only path an installer may read. Nothing re-reads the original source after measurement,
so there is no swap window. `stage` additionally cross-checks its own two measurements and refuses on disagreement
(`SRR_STAGING_MEASUREMENT_INCONSISTENT`). Both per-file and aggregate digests are enforced, in both directions
(missing file **and** unauthorised extra file).

### R1-6 — "staging/install/rollback/recovery are atomic and crash-safe on supported filesystems" — **SATISFIED**

Durability ordering is journal intent (fsync) → build `.srr-new` → journal swap (fsync) → rename `dest`→`.srr-old` →
rename `.srr-new`→`dest` → fsync(parent) → journal committed → verify committed bytes → drop `.srr-old` → **only then**
advance floors → journal done. Floor advancement after commit is the safe ordering: the opposite would leave a crashed
machine below its own floor, recoverable only by break-glass.

Verified by interruption (`heldout_srr4.rs::e3`): after a commit the destination holds the complete new version, the
pre-existing tree is gone rather than merged, and neither `.srr-new` nor `.srr-old` scaffolding is left behind. Forcing
the crash window between the two renames and running `staging::recover` yielded `removed_superseded_installation` and
left exactly one complete installation, never a mixed or competing tree. `write_durable` throughout is
temp → fsync(file) → rename → fsync(dir). `admit` replays any interrupted transaction before starting a new one.

### R1-7 — "metadata/release high-water is durable and monotonic" — **SATISFIED**

Three separately durable floors (`metadata_high_water` per role, `release_high_water`, signed `minimum_secure`) live in
`<state_root>/floors/<product>.json`, outside every repository. Verified (`heldout_srr2.rs::c6`): the floors survive
deletion of the entire project directory (`SRR2-R1-C3`); `raise_*` are monotonic-upward-only, so a lower value is never
written; and an unauthenticated observation (`signed = false`) raises nothing at all — a machine cannot manufacture a
security claim from an unverified install. Enforcement at **every** backward-capable ingress, not only `rollback`, is
demonstrated under R1-4. Non-blocking `AR27-N5` notes one case where a floor fails to *rise*.

### R1-8 — "post-install integrity remains distinct and D-0007 controls remain effective" — **SATISFIED**

The three predicates are separate types with separate sources. `runtime/src/kernel_trust.rs` (D-0007) reads **nothing**
from `srr` — confirmed by exhaustive grep — and the `srr` module reads no D-0007 record. `kernel_trust` establishes
**intact** only; `verifier::Authenticity` establishes **authentic**; `AuthenticatedRelease::below_floor` establishes
**admissible**. `kernel::install_kernel` calls `kernel_trust::clear()` after installing so the D-0007 verdict is
recomputed rather than inherited. `gov kernel override` raises a Human Gate about *integrity* and never touches
authenticity or the floors. The machine's own `gov trust status` states the separation explicitly, and I assert its
three fields directly (`heldout_srr4.rs::e4`).

### R1-9 — "project, CLI, environment, model and plugin inputs cannot create trust or approval" — **SATISFIED**

`refuse_authority_env()` is the first statement in `admit`. All nine listed variables were tested individually and each
produced `SRR_ENV_CANNOT_CREATE_AUTHORITY`; an **empty-valued** variable is also refused, because the check is
`var_os(..).is_some()` rather than a truthiness test (`heldout_srr2.rs::c5`). `--break-glass` only *requests*: with the
flag set and no owner-signed token present, admission fails with `SRR_BREAK_GLASS_NOT_AUTHORISED`
(`heldout_srr3.rs::d1`). Plugin descriptors have their `provenance` field stripped before validation and are classified
by **where the bytes are**, never by what the descriptor claims. `SRR-R0-L3` scopes "repository gate records are only
requests" to trust-changing operations, leaving D-0007 T2 and Contract v3 L2 intact for ordinary governed work.

There is no dev/test trust mode: `grep` across all product source finds **no** `SigningKey`, no secret-key construction
and no private key material; the only signing in the tree is `tests/certification/srr_material.rs`, a dev-dependency
test fixture. There is no `--skip-verify`, `--force-unsigned` or equivalent flag, feature or env var (`SRR-R0-L4`).

### R1-10 — "CI/multi-machine provisioning follows ARCH-0003" — **SATISFIED**

Against 00-ARCHITECTURE "Headless CI and multiple machines": the administrator provisions outside each governed project
(`provision()` refuses repository-sourced anchors); a persistent machine maintains its own protected high-water (floors
are keyed to the machine state root); `GOV_MACHINE_STATE_DIR` is the documented mechanism for provisioning a CI runner
or second machine outside the repository, and is refused once the default root is provisioned; and CI cannot manufacture
a Human Gate decision — `GOV_HUMAN_GATE_APPROVED` is in the refused-authority list, and `update --apply` requires a
presented, answered gate record where `--approve` alone is explicitly not a substitute (`INV-008`). The "trust-changing
automation scoped to the exact operation/release channel" bullet is partially served by channel binding (`SRR-R0-L2`);
a separate workload-policy object does not exist and belongs to R2.

### R1-11 — "the original product controls, Gate W and G0–G6 implementation mappings remain valid" — **SATISFIED**

All 49 pre-existing certification scenarios pass **unmodified** (see residual 5 below), which is the operative evidence
that the original controls are undisturbed. The Capability Acceptance Contract v3 chain is hash-bound and fails closed:
`framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md` is **byte-identical** to the owner source
at the repository root (both `4c2df291…7cb5ed3`), the digest is pinned in code as `OWNER_SOURCE_SHA256`, and
`contracts::verify` refuses on four independent divergences — `CONTRACT_SOURCE_DIVERGED` (digest), `CONTRACT_SOURCE_DIVERGED`
(byte comparison against the owner source), `CONTRACT_LOCK_DIVERGED`, `CONTRACT_COMPILED_DIVERGED` (fresh recompilation).
Capability *evidence* population is R2 (`AR27-N7`).

### R1-12 — "builder evidence and fresh independently authored held-out evidence pin the exact candidate" — **SATISFIED**

The builder's report, requirement-to-code map, digest manifest and test output are present at
`release/root-of-trust/signed-release-root-v1-r1-build/` and name work commit `949c4d34`. This report and its 29
held-out tests pin the same candidate at worktree HEAD `0ce7f9f0`. All builder digests re-verified.

---

# The five disclosed residuals — independent judgement

### 1. Unprovisioned posture — **ACCEPTED as an IMPLEMENTATION-CHOICE, with one owner question raised**

The builder's account is accurate: floors advance only from `Authenticity::Authentic`, so a machine that has never
verified a signed release enforces no release floor and claims no authenticity.

**Can an adversary keep or return a machine to that posture to evade a floor?** Inside the declared boundary, **no**.
Deleting `trust/root.json` fails closed with `SRR_TRUST_ANCHOR_MISSING` — the `provisioned.json` latch is never cleared,
so the machine refuses rather than silently reverting (verified, `c3`). Clearing the latch requires write access to
protected machine state, i.e. owner privilege. **Outside** the declared boundary, yes: relocating `XDG_STATE_HOME` or
`HOME` yields a fresh unprovisioned state root where unsigned bytes are admitted (verified, `c4`). `ARCH-0003` §1
explicitly places that actor inside the trusted boundary, so this is not an R1 defect — but see `AR27-OD1`.

**Does the honesty claim hold everywhere it must?** **Yes, everywhere I tested.** The verifier never reports
`AUTHENTIC` without a chain to the anchor; it returns `UNKNOWN` with an explicit note naming the missing anchor;
`gov trust status` reports `posture: UNPROVISIONED` and a null trust anchor; and `record_installed` on an `UNKNOWN`
release advances no protected floor, so no security claim is fabricated from the evaded state. Refusing to advance a
floor from an unverified observation is also the **correct** choice for a second reason the builder gives and I agree
with: recording one would brick rollback on a machine that has no break-glass authority to unbrick it, since break-glass
is anchored in the trusted root's `recovery` role.

### 2. Protected-state relocation — **reliance is SOUND, NOT CIRCULAR; override genuinely refused; one owner question raised**

`GOV_MACHINE_STATE_DIR` **is** genuinely refused on a provisioned machine (`SRR_PROTECTED_STATE_OVERRIDE_REFUSED`,
verified). The reliance on `ARCH-0003` §1 is sound and not circular: §1 was accepted at R0, its body digest is unchanged
since acceptance, and it independently declares the local OS/administrator boundary trusted and disclaims protection
from a hostile administrator. The implementation is not vouching for itself.

What I do record is the **asymmetry**: the refusal is computed against `default_state_root()`, which is itself derived
from `XDG_STATE_HOME`/`HOME`, so two unguarded variables achieve exactly what the third is refused for. Closing it
changes the bootstrap assumption and collides with the certification harness's own isolation mechanism, so it is routed
to the owner as `AR27-OD1`, flagged `REQUIRES_R0_OR_OWNER_ADJUDICATION`, not to a bounded repair.

### 3. Expiry comparison — **REAL DEFECT, NON-BLOCKING** (`AR27-N1`)

Attacked with valid-RFC-3339-but-not-emitted forms. An expiry thirteen hours in the past (`+14:00` offset) evaluates as
**not expired**; a lowercase-`z` past expiry evaluates as **not expired**; metadata with no `expires` member **never**
expires. No canonical-form gate guards the comparison. This is a genuine correctness gap and I recommend fixing it in the
same bounded cycle as `AR27-B1` — but it does **not** block R1, because `expires` is inside the signed byte-string:
an adversary who alters it invalidates the signature, and replay of canonically-formed expired metadata is refused.
Reaching the fail-open state requires publisher deviation, which makes it a producer-contract gap rather than a
falsification of "expiry fails closed".

### 4. Delegated targets have no issuing tooling — **`SRR-R0-L6` IS GENUINELY CLOSED**

`OWNER-DECISION-0005` §2 states the R1 obligation precisely: "the design is expected to **distinguish** remotely
acquired privileged plugins/tools from built-in/local tools and **decide how delegated signed targets apply to each**."

Both limbs are met. The distinction exists as `Acquisition::{BuiltIn, LocalProject, RemotelyAcquired}`, derived from
**where the implementation bytes actually are** — not from anything the descriptor says about itself, so `provenance`,
`security_review: passed` or a `source` field cannot move a capability into a weaker class. The decision is made and
implemented: built-in capabilities are covered by the release payload digests and need no delegation; local-project
capabilities keep the existing kernel-owned controls; and a **privileged** remotely-acquired capability requires a
delegated signed target and is otherwise refused with `SRR_PLUGIN_NOT_DELEGATED`.

Is enforcement alone enough? **Yes, for R1.** The obligation is a *design* obligation — distinguish, and decide how
delegations apply. It does not require that a delegation be issuable at R1, and production signing and key custody are
placed at **R2** by the frozen boundary. The absence of an admission path is fail-closed and strictly more restrictive
than the pre-SRR product, so it removes no existing capability guarantee. Treating it as an R1 blocker would convert
optional later-lifecycle assurance into a blocker — exactly what `OWNER-DECISION-0005`'s standing direction forbids.

I do record the wiring gap (`AR27-N6`, R2): `guard_acquisition` is called with a hard-coded empty delegation slice, so
delegations parsed from verified release metadata would be ignored even if one existed.

### 5. Certification harness — **CONFIRMED CLEAN AGAINST HISTORY**

`git diff 1e31f6b 949c4d3 -- tests/` is **2026 insertions, 0 deletions**:

```text
tests/certification/common.rs                 |   24 +
tests/certification/main.rs                   |    2 +
tests/certification/srr.rs                    | 1062 +++++++
tests/certification/srr_material.rs           |  332 ++++
tests/governance/capability-evidence-map.yaml |  606 ++++++
```

**Zero deletions across the whole test tree** — no pre-existing line was changed, so no assertion can have been weakened
and no pre-existing test edited to pass. The `common.rs` change is two new helper functions plus one added
`c.env("XDG_STATE_HOME", …)` line; `main.rs` gains two `mod` declarations. The harness comment is candid that it leaves
`GOV_MACHINE_STATE_DIR` unset precisely so the tests probing that override probe a genuine override. Counting confirms
the arithmetic: 64 total certification scenarios − 15 in `srr.rs` = **49 pre-existing, all passing unmodified**, exactly
as claimed.

---

# Also-verify items

| Item | Disposition |
|---|---|
| `SRR2-R1-C1` at exactly one named point | **CONFIRMED.** `breakglass::exit_satisfied`, flag `EXIT_POLICY = "b_stricter_both_floors"`. Exhaustive grep for `effective_floor_*`/`exit_satisfied`/`EXIT_POLICY` finds no other site comparing a release against an exit floor; the other hits are the definition, its own doc/description, record fields and reporting. `try_exit` is the single caller path, reached only from `record_installed`. The stricter interim reading is verified behaviourally (a release between the two floors does not clear the marking) and **is not graded as a defect**. |
| `SRR2-R1-C2` | **SATISFIED.** The offline-recovery basis and the break-glass token both bind **payload digests**, not the version. A token naming only a version is refused at parse; a token binding a different payload is refused at entry with `SRR_BREAK_GLASS_WRONG_PAYLOAD`. |
| `SRR2-R1-C3` | **SATISFIED.** Floors survive project deletion (verified). |
| `SRR-R0-L1` root succession | **SATISFIED.** Same product, version exactly `current + 1` (no gaps, no replay), threshold of the **outgoing** root, threshold of the **incoming** root, candidate not expired, revocation by omission. (Outgoing-root expiry is not checked — `AR27-N2`.) |
| `SRR-R0-L2` channel | **SATISFIED.** Bound metadata field; wrong channel → `SRR_WRONG_CHANNEL` (verified). Delegations may additionally bind a channel. |
| `SRR-R0-L3` | **SATISFIED.** Repository gate records are requests only for the enumerated trust-changing operations; ordinary governed work retains D-0007 T2 / Contract v3 L2 authority. |
| `SRR-R0-L4` — **must remain vacuous** | **VACUOUS, CONFIRMED.** No dev/test trust mode, no flag, env var or cargo feature relaxes verification. No signing key type is constructed anywhere in product source. |
| `SRR-R0-L5` durability ordering | **SATISFIED** (see R1-6). |
| `SRR-R0-L6` | **GENUINELY CLOSED** (see residual 4). |
| `SRR-R0-L7` offline/air-gapped first install | **CORRECTLY ABSENT.** Owner-closed by `OWNER-DECISION-0005` §3. `provision.rs` states its absence explicitly. Break-glass *recovery* works offline — verified under poisoned proxy variables (`heldout_srr3.rs::d5`); the authorisation path reads only the protected inbox, the trusted root and the local clock, and `gov trust status` reports `network_required: false`. |
| D-0007 semantics preserved | **SATISFIED** (see R1-8). |
| No private key material; `gov` verifies and never signs | **SATISFIED** (see R1-9). No `.pem`/`.key` material in the repository. |
| Contract v3 canonical import byte-identical, fails closed | **SATISFIED** (see R1-11). |
| Full regression | **REPRODUCED EXACTLY**: 26 / 64, 0 failed. |

# All ten `OWNER-DECISION-0006` requirements in running code

| § | Requirement | Disposition |
|---|---|---|
| 1 | Recovery release must still be authentic | **SATISFIED.** Break-glass relaxes the floor check only; `SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE` guards the authenticity predicate. Verified the admitted below-floor release is authenticated. |
| 2 | Authority cannot be manufactured | **SATISFIED.** Owner-signed `recovery`-role token in a protected out-of-band inbox. Verified refusals for: no token; non-recovery-role signature; another machine's `machine_id`; expired token; version-only token. `--break-glass` only requests; env vars are refused outright; the binary holds no signing key. |
| 3 | Durable entry record | **SATISFIED.** Verified on disk: machine id, floors at entry (signed minimum, protected high-water, metadata high-water), recovery release identity and digests, reason, `entered_at`, token nonce/issue/expiry/digest, ingress. |
| 4 | Byte-exact `DEGRADED — RECOVERY ONLY` | **SATISFIED.** Asserted against the raw bytes `DEGRADED \xe2\x80\x94 RECOVERY ONLY` in the durable record written by the real entry path — U+2014 EM DASH, not a hyphen or en dash. |
| 5 | Permitted activities | **SATISFIED.** Inspection, backup/export, diagnosis, repair, uninstall/reinstall and restoration remain available below floor. |
| 6 | Refused activities | **NOT SATISFIED — `AR27-B1`.** Bullets 2–7 hold; bullet 1 ("normal privileged Governance OS operation") is enforced as a substring deny-list, so seven privileged governed operations proceed while the machine is marked. |
| 7 | Exit condition | **SATISFIED.** Single policy point; marking persists on a below-floor install and clears on an authenticated at-floor install (both verified). |
| 8 | Floor is not lowered by break-glass | **SATISFIED.** `enter` writes no floor; `raise_*` are monotonic-only; verified the protected high-water was unchanged at 40 across a below-floor break-glass install. |
| 9 | Ingress consistency | **SATISFIED.** The floor check is inside the one verifier every ingress calls; verified across all six ingresses. |
| 10 | Works with no network | **SATISFIED.** Verified under poisoned proxy variables; all inputs are local files. |

# Verdict

**`BLOCKING_FINDINGS_PRESENT`.**

This is a strong implementation. Eleven of the twelve frozen R1 criteria are satisfied on the evidence above, the
compiler-enforced ingress invariant holds under adversarial probing, the cryptographic adapter withstood twelve
independent forgery attacks, the transaction abort is not a bypass, the durability ordering is correct and survives
interruption, and four of the five disclosed residuals are accurately characterised and correctly lifecycled — including
`SRR-R0-L6`, which I judge genuinely closed.

One binding owner requirement is not met in running code: `OWNER-DECISION-0006` §6 bullet 1. The repair is bounded, local
to `runtime/src/srr/breakglass.rs`, needs no architecture change and no new owner decision. I recommend a bounded R1
repair cycle covering `AR27-B1`, and — because they are cheap, local and in the same files — the non-blocking R1-lifecycle
items `AR27-N1`, `AR27-N2` and `AR27-N4`. `AR27-OD1` should go to the owner independently of that cycle.
