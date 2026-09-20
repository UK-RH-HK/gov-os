# P2-AR-0044 — Verification iteration 1: AC-14 R1 preservation

| Field | Value |
|---|---|
| Run | **P2-AR-0044**, fresh independent R1-preservation verifier. Not AR-0027, AR-0029, AR-0031 or AR-0033; no Phase-1 role; no authorship of the implementation, its tests, the iteration-0 audits or any repair; not the orchestrator. |
| Model | `claude-opus-5[1m]` |
| Candidate | `cap2-candidate-1`, commit `0bad524d836f179964ffbac31972856ea6434682` |
| Worktree HEAD verified | `8588813ec1ef9c832879e258ca5acfb573ae996f`, branch `phase2/verify-1-r1-preservation` |
| Reference | `srr1-r1-accepted` → commit `c7d3fefa12f7e5813d3c3d9d9d229b5993b7c112`, `product_code_digest` `bd4d65d9…0547` |
| Question | Does `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` (AR-0033) **remain valid** for this candidate? (Frozen gate contract AC-14, §9.3.) It is not re-issued here. |
| **Verdict** | **`R1_PRESERVED`** |

---

## 1. Pinned inputs — all verified, no STOP

```
$ python3 release/orchestration/phase-2/tools/product_identity.py HEAD
commit: 8588813ec1ef9c832879e258ca5acfb573ae996f
product_code_digest:   e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220   ✓ as dispatched
governed_state_digest: 3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0   ✓ as dispatched

$ python3 release/orchestration/phase-2/tools/product_identity.py 0bad524…   (the tag)
   identical on both digests  ✓   — my worktree carries the candidate's exact product tree and governed state
$ git rev-list -n1 cap2-candidate-1   → 0bad524d836f179964ffbac31972856ea6434682   ✓
```

| Document | SHA-256 | |
|---|---|---|
| `Governance_OS_Capability_Acceptance_Contract_v3.md` | `4c2df291…5ed3` | ✓ |
| `release/orchestration/phase-2/GATES/PHASE-2-FROZEN-GATE-CONTRACT.md` | `d2f33e89…9f25e` | ✓ |
| `release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` | `70977d11…f699c1` | ✓ |

Toolchain `cargo 1.98.1 / rustc 1.98.1`. Full record: `evidence/PINNED-INPUTS.txt`.

One presentational wrinkle, recorded as **V1-R1P-02** (INFO, non-blocking): `product_identity.py` prints
`git rev-parse <rev>` as its `commit:` line, which for the **annotated** tag `srr1-r1-accepted` is the tag object
`b78b5c68…`, not the commit `c7d3fefa…`. The digests are unaffected (`rev-parse <tagobj>:<path>` resolves through
to the commit's tree, and `bd4d65d9…0547` reproduced exactly), so this is not a STOP — but every iteration-1
verifier is told to check a pinned identity with this tool and treat a mismatch as a STOP, so it is worth fixing.

## 2. Method

Nothing in this report rests on a builder or integrator claim. Reports under `release/capability-baseline/repair-1/**`
were read only to learn what is asserted; every figure below is one I produced.

1. **All four prior R1 held-out suites, unedited**, built against this candidate through a private, uniquely named
   path (`<scratch>/p2ar0044-private-rerun/`), with byte identity asserted by `cmp` on every file.
2. **My own held-out tests** (`heldout/`, 41 tests in four files plus a RUN-ALL script), written from the frozen R1
   boundary, ARCH-0003, D-0007, OD-P2-02, OD-P2-03, P2-ADJ-0002 and the product's observable behaviour — not by
   copying any product test, builder probe, or prior verifier's harness. They never enter the product tree.
3. **My own diff** of `srr1-r1-accepted..cap2-candidate-1` over the product tree, to decide which areas the twelve
   frozen R1 items must be re-established for.
4. **The HO-0033 structural invariants re-measured** with my own splitter and greps.
5. **The regression run myself.**

Every run strips the nine refused-authority environment variables plus `GOV_MACHINE_STATE_DIR`, and runs
`--test-threads=1` (the harnesses set process-wide environment). Every probe whose meaning depends on a green
starting point establishes that green baseline first and asserts it (P2-ADJ-0003); the positive controls are called
out individually below, because without them most of this report would be satisfied by a product that refuses
everything.

## 3. The four prior R1 suites — every figure reproduced exactly

Each `.rs` file `cmp`-verified byte-identical against the committed evidence; each `Cargo.toml` is the committed
`Cargo.toml.txt` **verbatim**, with the `gov-runtime` path dependency retargeted at this candidate by **symlink**
rather than by an edit. Details and the SHA-256 census: `evidence/PRIOR-SUITE-BYTE-IDENTITY.txt`.

| Suite | Recorded baseline | **Measured by me on `cap2-candidate-1`** | Failing tests |
|---|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 / 3 | **26 passed / 3 failed** of 29 ✓ | `b1`, `b2`, `d3` — identical |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 of 28, `ho_f` not compiling | **26 passed / 2 failed of 28 compiled; `ho_f_preservation` does not compile** ✓ | `b3`, `b6` — identical |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 | **27 passed / 7 failed** of 34 ✓ | `a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2` — identical |
| AR-0033 (`4.1.6-r1-4`) | 31 / 0 *(at candidate 4)* | **30 passed / 1 failed** of 31 | `hv_a::a1` only — §4 |

Per-binary census, so the totals are checkable:

* **AR-0027** — `heldout_srr` 12/0, `heldout_srr2` 6/2, `heldout_srr3` 4/1, `heldout_srr4` 4/0.
* **AR-0029** — `ho_a` 6/0, `ho_b` 4/2, `ho_c` 5/0, `ho_d` 5/0, `ho_e` 6/0; `ho_f_preservation` **does not compile**.
* **AR-0031** — `hx_a` 5/3, `hx_b` 5/1, `hx_c` 6/2, `hx_d` 11/1.
* **AR-0033** — `hv_a` 9/1, `hv_b` 7/0, `hv_c` 6/0, `hv_d` 8/0.

I ran each suite twice: once with the ambient environment and once under the full strip. The figures are identical
either way (`evidence/PRIOR-SUITES-UNDER-ENV-STRIP.txt`), so no result here depends on ambient environment.

**Every difference from the baselines, explained.**

* **AR-0027, AR-0029, AR-0031 — no differences at all.** All three figures and all twelve failing-test identities
  reproduce exactly. AR-0033 adjudicated each of those twelve in its §9 (structural tripwires asserting the
  pre-repair shape, and location assertions against files a repair deliberately did not edit); I reproduced the
  same twelve on a tree ~3× larger and found no new failure, which is the relevant fact for preservation.
* **AR-0029 `ho_f_preservation` still does not compile**, with the same error:
  `cannot construct AuthenticatedRelease with struct literal syntax due to private fields`. That compile failure
  *is* the seal on the admission token holding — the property, not a regression.
* **AR-0033 `hv_a::a1`** is the single new failure, and it is the one my handoff anticipated: it pins
  `assert_eq!(files.len(), 84)` and `assert_eq!(funcs.len(), 740)`. This tree is legitimately larger. Judged on its
  property in §4.
* **AR-0033 `hv_b::b4`/`b5`/`b6` and `hv_d::d3`** failed on my first attempt because I had not yet supplied the
  runner parameters the suite requires (`AR0033_GOV_BIN`, `AR0033_BASE_SRC`, per AR-0033's own REPRODUCTION.md).
  With them supplied, all four pass. I record this because the first run is in my logs; it was my harness wiring,
  not product behaviour, and `evidence/PRIOR-AR-0033-RERUN.txt` is the corrected run.

Notably, AR-0031's `hx_d` — the suite that carries the HO-0033 structural assertions — still passes `d5` (four-entry
allow-list, exact match), `d6` (five `admit` / five `install_kernel`), `d7` (no signing capability in product
source), `d8` (D-0007 independent of the SRR verdicts), `d9` (Contract v3 canonical import byte-identical and
failing closed), `d10` (single exit-policy point), `d11` (floors monotonic), `d12` (break-glass purely local). And
AR-0033's `hv_d::d7` — "frozen R1 preservation still holds" — passes.

## 4. `hv_a::a1` judged on its property

AR-0033's `a1` re-derives the OWNER-DECISION-0006 §6 census with its author's own splitter and asserts **both** the
scale and the absence of violations. Only the scale moved. A labelled copy with the two **size** assertions printed
instead of asserted — the rename and those two lines are the *only* differences, shown by `diff` in the evidence —
gives:

```
independent walk: 123 files, 2392 functions
SIZE (printed, not asserted): files=123      (AR-0033 pinned 84)
SIZE (printed, not asserted): functions=2392 (AR-0033 pinned 740)
AR-0033 independent §6 census:
  human_gate_create:                      derived 50 / writers 45 / exempt 1 / violations 0
  human_gate_approve:                     derived  1 / writers  1 / exempt 0 / violations 0
  release_certification:                  derived  1 / writers  1 / exempt 0 / violations 0
  trust_policy_mutation:                  derived  8 / writers  1 / exempt 0 / violations 0
  privileged_plugin_acquisition:          derived 13 / writers  3 / exempt 0 / violations 0
  floor_lower_or_reset:                   derived  4 / writers  1 / exempt 0 / violations 0
  present_below_floor_release_as_current: derived  1 / writers  1 / exempt 0 / violations 0
test result: ok. 1 passed
```

**Zero independently derived §6 violations across all seven activities**, over 123 files and 2392 functions — a
function count 3.2× the one AR-0033 accepted on. The property `a1` protects is not merely preserved, it is
demonstrated over substantially more code. `evidence/AR-0033-hv_a-a1-LABELLED-SIZES-PRINTED.txt`.

**AR-0033's `derive.py`**, retargeted at this candidate (the only change is the hard-coded `ROOT` on line 2, shown
by `diff` in the evidence), agrees, in all three of its splitter configurations:

| configuration | files / functions | violations |
|---|---|---|
| indentation splitter, `cfg(test)` cut (the product's own) | 123 / 2392 | **0** in every activity |
| brace-depth splitter, `cfg(test)` cut (independent) | 123 / 2392 | **0** in every activity |
| indentation splitter, **no** `cfg(test)` cut | 123 / 2758 | **0** in every activity |

`evidence/AR-0033-derive-py.txt`.

## 5. The diff, and the changed areas the R1 items must be re-established for

```
$ git diff --shortstat srr1-r1-accepted^{commit} 0bad524 -- runtime cli tests framework capabilities \
                                                             migrations tools fixtures bin scripts Cargo.*
204 files changed, 116505 insertions(+), 4817 deletions(-)      (61 added, 143 modified)
```

This is a very large delta, so I did not sample. Areas touching an R1 item, and what is new
(`evidence/CHANGED-AREAS.txt`):

| Changed area | Files | R1 items reached |
|---|---|---|
| **T2 binding authority (new)** | `runtime/src/srr/binding.rs` (+832, new), `runtime/src/t2.rs` (+1673, new), `gov trust bind`/`reseal` | 1, 2, 3, 9, 10 |
| **Admission / install** | `runtime/src/srr/verifier.rs` (+355/-33), `srr/installation.rs` (+1166, new), `srr/present.rs`, `srr/state.rs`, `srr/mod.rs` | 2, 3, 4, 5, 7 |
| **`gov update` and the scheduler** | `runtime/src/update.rs` (+318/-76), `runtime/src/scheduler/*` (+3717, new) | 3, 4, 5, 6 |
| **Kernel payload / bootstrap** | `runtime/src/kernel.rs` (+542/-74), `kernel_trust.rs`, `authority.rs` (+298/-8), `init.rs`, `framework/KERNEL.yaml` | 5, 8, 10 |
| **Relocated OS stores** | `runtime/src/paths.rs` (+710/-4): `OS_STORES`, `store_path`, `relocate_legacy` | 8, 9 |
| **Tool-installation change control (OD-P2-03)** | `runtime/src/tools.rs` (+1664/-76), `CHANGE_POLICY.yaml`, `TOOL_POLICY.yaml`, `tools/registry/TOOLS.yaml` | 9 |
| **Plugin binding / registry** | `capabilities/binding.rs` (new), `pincache.rs` (new), `capabilities/registry.rs` | 9 *(registry half only — §8)* |
| **Contract import** | `runtime/src/contracts.rs` (+6134/-243), `framework/contracts/*` | 11 |

## 6. My own held-out tests

`heldout/` — 41 tests in four files, driving the real `gov` binary against disposable projects and the library
through a harness, on simulated owner machines each with its own protected state root, HOME and project. `RUN-ALL`
re-runs everything, including the four prior suites, and prints one PASS/FAIL line per test.

| File | Tests | What it attacks |
|---|---|---|
| `p1_t2_binding.rs` | 13 | the new cross-machine T2 binding authority end to end |
| `p2_update_and_kernel.rs` | 9 | `gov update` admission, the OD-P2-02 bootstrap, payload consistency, rollback availability, the high-water |
| `p3_stores_and_tools.rs` | 11 | the relocated OS stores, and OD-P2-03 tool-installation change control |
| `p6_structural.rs` | 8 | the HO-0033 structural invariants, re-measured |

**Result: 40 passed, 1 failed** — `p1` 13/0, `p2` 9/0, `p3` 10/1, `p6` 8/0 (`evidence/HELDOUT-RUN-ALL.txt`).
The single failure is `p3::c5`, which is deliberate: it asserts the safe behaviour of `relocate_legacy` on an
unreadable store, and its failure *is* finding V1-R1P-01 (§9). Every other test passes.

### 6.1 The new T2 binding authority (`p1`, 13/13)

The substantive question is whether this new authority can be created by anything other than the owner's
provisioned root, and whether `gov` ever signs.

* **`a1`** — repository content cannot manufacture an honoured T2 fact. Four forgeries, all refused: an unsealed
  hand-written record is `Unsealed`; an invented seal block of the right shape does not verify; a genuine seal
  **lifted** onto different content does not verify; one flipped field on a genuinely sealed record is `Broken`.
* **`a2`** — a record sealed on one unprovisioned machine is `Foreign` on another.
* **`a3`** — an unprovisioned machine cannot be bound: `T2_BINDING_UNPROVISIONED`, and the refusal names
  `gov trust provision` as its remedy.
* **`a4`** — only the root-delegated `t2-binding` role can create an authority. A signature by an attacker's key
  presented under the delegated key id → `SRR_THRESHOLD_NOT_MET`; role confusion (signed by the **root** key) →
  `SRR_THRESHOLD_NOT_MET`; no signatures → `SRR_METADATA_UNSIGNED`; **and the genuine article is accepted**, so
  none of the three is a vacuous pass.
* **`a5`** — an authority or key placed **inside the repository** is refused (ARCH-0003 §8), and all five
  refused-authority environment variables are refused at `trust bind` with `SRR_ENV_CANNOT_CREATE_AUTHORITY`.
* **`a6`** — version rollback → `T2_BINDING_AUTHORITY_ROLLBACK`; a different document at an accepted version →
  `T2_BINDING_AUTHORITY_CONFLICT`.
* **`a7`** — an unlisted key → `T2_BINDING_KEY_NOT_AUTHORISED`; the right id against the wrong commitment →
  `T2_BINDING_KEY_MISMATCH`.
* **`a8`** — a root that does not delegate `t2-binding` authorises nothing → `T2_BINDING_NOT_DELEGATED`, naming
  root succession as the route.
* **`a9`** — an authority that does not list this machine → `T2_BINDING_MACHINE_NOT_AUTHORISED`.
* **`a10` (the positive control, P2-ADJ-0002)** — two machines of the same owner, both provisioned under the same
  root with the product's own `gov trust provision` and both bound with `gov trust bind`: a fact sealed on machine
  one **is** honoured on machine two. A third machine under a **different owner's** root and authority does **not**
  honour it. So the cross-machine continuity is real and bounded, not "nothing is ever honoured".
* **`a11`** — `gov trust` exposes no minting or signing subcommand, and neither new file carries a signing
  capability.
* **`a12`** — expiry fails closed in all five forms I could construct: plainly past, absent, lowercase `t`/`z`,
  a `+14:00` numeric offset (which is thirteen hours in the *past* yet sorts *after* a `Z` time), and fractional
  seconds. All five → `T2_BINDING_AUTHORITY_EXPIRED`. The AR27-N1 canonical-form gate binds the **new** document
  type too. The same document with a canonical future expiry is accepted, so the five are not vacuous.
* **`a13`** — nothing secret is in any repository. After a full provision-and-bind ceremony and a live seal, the
  binding key appears in **no** file anywhere under the project tree; it lives in protected machine state outside
  every repository, in a file with no group or world permission bits (mode `0600`).

Incidentally, while building this harness the product refused two of my own mistakes correctly: a key id I chose
rather than derived (`SRR_KEYID_MISMATCH` — "a document cannot point one key id at another key's bytes"), and a
second owner's root that reused the first owner's key ids. Both are the profile working.

### 6.2 `gov update`, the kernel payload and OD-P2-02 (`p2`, 9/9)

* **`b1`** — external-source kernel material on an unprovisioned machine is refused with
  `SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED`, **before staging** (`refused_before_staging: true`), nothing is
  applied, the attacker file never reaches `governance/kernel/`, and the refusal names both remedies. This is
  OD-P2-02 option A, implemented.
* **`b2` (positive control)** — the same ingress on the same machine still bootstraps from the binary's own
  embedded payload (`source: embedded:agentic-engineering-os@4.1.6`), and that bootstrap is reported
  `certification: UNCERTIFIED` with `authenticated: false`. The block refuses only what it protects.
* **`b3`** — six refused-authority environment variables, one at a time, admit nothing.
* **`b4`** — `--channel stable`, `--channel trusted`, `--by human`, `--by owner`, `--approve`,
  `--reason "approved by the owner"`: none changes the admission decision. CLI strings are requests.
* **`b5`** — a command-line `--break-glass` claim admits nothing; the authority is protected machine state.
* **`b6`** — the installed payload's `KERNEL.yaml` mirrors the source's version, and every schema it declares ships
  at the declared version (`schema_version_problems` empty).
* **`b7` (also the AC-10 freshness demonstration)** — green baseline asserted first (`kernel verify` →
  `result.ok: true`); then one installed policy file is modified. Verification goes red, names
  `policies/TOOL_POLICY.yaml`, and the **protected installation record** reads `state: DIVERGED` with the basis
  *"KERNEL_MANIFEST.json and framework.lock agreeing with it does not make it intact"*. Prior green evidence went
  stale in the same run, and the machine's protected record — not a repository-controlled record — is what decided.
* **`b8`** — `update --rollback` is one of the two named `GATE_FREE_RESTORATION_ROUTES`, both named remedies are
  themselves on the §5 allow-list (a block does not refuse its own remedy), and the ingress answers typed.
* **`b9`** — the release high-water raised to sequence 100 does not fall when a lower raise is saved; the floors
  file is durable and lives outside the repository.

### 6.3 Relocated OS stores and OD-P2-03 (`p3`, 10/11 — `c5` is finding V1-R1P-01)

* **`c1`** — every declared store resolves through `store_path`; every machine-local store lands under
  `.governance-state/`; the two tracked stores are declared `authoritative`.
* **`c2`** — with every store present at **both** its legacy location and where it belongs, the framework §19
  derived-deletion set contains none of them. This is the defect BC-P2-31 named, closed.
* **`c3`** — relocation moves bytes intact, is idempotent, and refuses a genuine differing-bytes conflict with a
  typed `STATE_LOCATION_CONFLICT` that touches neither copy and carries a remediation.
* **`c4`** — the two `authoritative` stores live **inside the repository** (`governance/registry/…`), so project
  content can write the file. An attacker "registration" written straight into both is **not** an honoured T2 fact,
  and both locations are classified `os_managed_location` so the unsealed state is reported rather than ignored.
  **This is the answer to "does any trusted state become writable by project content?": the bytes are writable, the
  fact is not.**
* **`c5`** — **fails, deliberately**: see §9.
* **`d1`** — a descriptor declaring nothing elevated but installing with `sudo` is an authority expansion anyway.
* **`d2`** — nine attacker-chosen declarations (`human_approved`, `approved`, `trust: T1`, `authority_level: 5`,
  `expands_authority: false`, `gate_required: false`, a fabricated `security_review` verdict, `registered`,
  `auto_install`) each fail to clear the expansion verdict. Contract v3 F4 holds: a descriptor cannot authorise
  itself.
* **`d3`** — an installation the OS cannot derive gates, fail-closed, and says why.
* **`d4`** — an acting role the project never authorised carries nothing.
* **`d5`** — a project-written `TOOLS.yaml` does not enlarge the kernel's network allowlist.
* **`d6`** — an `install_tool` operation aimed at kernel policy is an expansion.

## 7. The HO-0033 structural invariants, re-measured (`p6`, 8/8)

Measured with my own file walk, my own `#[cfg(test)]` cut and my own greps. Where a count stands for a property,
the test checks the property too, because on a tree this much larger a matching count proves less than it did.

| HO-0033 invariant | Measured | Holds? |
|---|---|---|
| four-operation §5 allow-list, **exact match** | exactly `checkpoint`, `kernel reinstall`, `update --apply`, `update --rollback`; nine near-miss forms per label (prefix, suffix, case, whitespace, `--force`) all refused; five unrelated labels refused by default | **yes** |
| five `admit` sites paired with five `install_kernel` sites | 5 `srr::admit` — `adopt.rs:1691`, `init.rs:242`, `update.rs:339`, `update.rs:610`, `main.rs:2212`; 5 `install_kernel` — `adopt.rs:1695`, `init.rs:249`, `update.rs:356`, `update.rs:622`, `main.rs:2218`; **each install preceded by an admit in the same function** | **yes** |
| one `by_admit` | 1 call site (`srr/verifier.rs:840`), one `pub(super)` definition | **yes** |
| one `AuthenticatedRelease` literal | 1, inside the verifier (`srr/verifier.rs:838`) | **yes** |
| zero `Clearance` constructions outside `breakglass` | 0 | **yes** |
| floors at all six ingresses, advancing last | no mutator lowers; every floor mutator is a raise, bound inside `Floors::save`; behaviourally `p2::b9` | **yes** |
| transaction abort is not a bypass | `srr/staging.rs` (+5/-3) and `write_durable` essentially untouched; AR-0027 `heldout_srr4::e3` (atomic install transaction replays after interruption) passes; 207 certification tests incl. failure injection | **yes** |
| D-0007 establishes **intact**, never **authentic**/**admissible** | `kernel_trust.rs` establishes `intact`; no line claims authenticity or admissibility other than to deny it; AR-0031 `hx_d::d8` and AR-0033 `hv_d::d7` pass | **yes** |
| `SRR-R0-L4` vacuous — `gov` never signs | zero `SigningKey` / `Signer` / `.sign(` / `Keypair` in product source outside `#[cfg(test)]`; the non-dev `ed25519-dalek` carries no `rand_core` | **yes** |
| Contract v3 canonical import byte-identical at `4c2df291…`, failing closed | owner source hashes to `4c2df291…5ed3`; canonical import **byte-identical**; digest pinned in `contracts.rs`; `embedded_model()` loads | **yes** |

**No count changed.** Every one of the five/five, one, one, zero counts is exactly what HO-0033 pins, on a tree with
3.2× the functions — and each is now also checked as a property rather than only as a number.

## 8. The twelve frozen R1 items, for every changed area

| # | Frozen R1 item | Disposition | My basis |
|---|---|---|---|
| 1 | a mature reviewed TUF/cryptographic implementation is used correctly | **HOLDS** | AR-0027 `heldout_srr` 12/12 and `heldout_srr4` 4/4; AR-0029 `ho_d`/`ho_e` 11/11; AR-0033 `hv_d::d5`; the new binding authority verifies through the **same** `Root::verify_role` and `verify_strict` (`p1::a4`: forged signature and role confusion both `SRR_THRESHOLD_NOT_MET`) |
| 2 | candidate/source files cannot create their own trusted identity | **HOLDS** | `p6::f3` (one `by_admit`, one `AuthenticatedRelease` literal), `p6::f4` (zero `Clearance` outside breakglass); AR-0029 `ho_f` still does not compile against the sealed type; **and for the new authority** `p1::a1/a5/a8` — repository content, a repository-sourced document, and an undelegated root each create nothing |
| 3 | wrong keys, modified metadata/payload/migration, replay, downgrade, expiry fail closed | **HOLDS** | AR-0027 and AR-0029 reruns unchanged; `p1::a4` (wrong key), `p1::a6` (rollback + same-version conflict), `p1::a7` (key not authorised / commitment mismatch), `p1::a12` (expiry, in all five forms including the three non-canonical timestamp shapes), `p2::b7` (modified payload), `p2::b9` (downgrade of the high-water) |
| 4 | all privileged ingress paths call the common verifier | **HOLDS** | `p6::f2` — five `srr::admit` sites pair one-to-one with five `install_kernel` sites, each install preceded by an admit **in the same function** (the filter excludes only the `fn install_kernel(` definition line, not the defining module, so a call added inside `kernel.rs` would still have to pair); AR-0031 `hx_d::d6` passes. The **new** ingresses: `gov update` is one of the five admit/install pairs and is refused before staging when it cannot verify (`p2::b1`); `gov trust bind` is not a kernel ingress but *is* a privileged ingress for externally supplied signed material, and it verifies through the **same** common verifier — `Root::verify_role` → `crypto::verify_strict` — which is why a forged signature and a role-confused signature both come back `SRR_THRESHOLD_NOT_MET` (`p1::a4`); tool installation ingests no signed material and is governed by the OD-P2-03 envelope instead (`p3::d1–d6`) |
| 5 | verified bytes staged, installed and used without substitution | **HOLDS** | `p2::b1` (nothing unverified is staged), `p2::b6` (installed payload matches what `KERNEL.yaml` declares, schemas at declared versions), `p2::b7` (a post-install substitution is detected and the payload is no longer admitted); AR-0027 `heldout_srr` passes |
| 6 | staging/install/rollback/recovery atomic and crash-safe | **HOLDS** | I read the whole delta for the transaction-bearing files: `srr/staging.rs` is **+5/-3** and the change only *removes* a `built_at` timestamp from the committed manifest so a second machine re-commits byte-identical files — the copy-beside-then-atomic-rename and the `fsync` sequence are untouched, and no abort path is altered. `srr/state.rs` (+37/-2) is purely additive (a read-only state view, `installed_dir`, and a BC-P2-38 hardening of `vouches_for`). `write_durable` unchanged. AR-0027 `heldout_srr4::e3` (install transaction replays after interruption) passes; `p2::b8`; 207 certification tests incl. failure injection, 0 failures. *(The OS **operational**-store relocation is a different mechanism and carries finding V1-R1P-01 — §9.)* |
| 7 | metadata/release high-water durable and monotonic | **HOLDS** | `p2::b9` — a lower raise does not move the floor down; the floors file is durable and outside every repository; `p6::f8` — no mutator lowers; AR-0031 `hx_d::d11` passes |
| 8 | post-install integrity distinct; D-0007 controls effective | **HOLDS — strengthened** | `p2::b7` — the machine's **protected installation record** now decides (`DIVERGED`), explicitly outranking `KERNEL_MANIFEST.json` and `framework.lock`; `p6::f5`; `p3::c4` — the relocated authoritative stores are T2-bound; AR-0031 `hx_d::d8` and AR-0033 `hv_d::d7` pass. This is BC-P2-35 closing |
| 9 | project, CLI, environment, model and plugin inputs cannot create trust or approval | **HOLDS — and broadened** | `p1::a1/a2/a5` (project content, foreign machine, environment), `p2::b3/b4/b5` (environment, `--channel`, `--by`, `--approve`, `--reason`, `--break-glass`), `p3::c4` (repository-resident authoritative stores), `p3::d1–d6` (descriptor self-declaration, unauthorised role, project-written allowlist); AR-0033 `hv_c` 6/6 |
| 10 | CI/multi-machine provisioning follows ARCH-0003 | **HOLDS** | `p1::a10` — two machines provisioned with the product's own `gov trust provision` and bound with `gov trust bind`, facts portable between them and not beyond; `p1::a3` (unprovisioned refused), `p1::a5` (never from the repository), `p1::a13` (**nothing secret is in any repository**: after a full ceremony the binding key appears in no file under the project tree, and lives outside it at mode `0600`); `p2::b1/b2` (OD-P2-02 on an unprovisioned machine); AR-0033 `hv_c::c6` passes |
| 11 | original product controls, Gate W and G0–G6 mappings remain valid | **HOLDS** | 276 lib + 207 certification tests pass, zero failures, run by me; `p6::f7` — the Contract v3 canonical import is byte-identical at `4c2df291…` and pinned in the binary; `p6::f1` — the §5 allow-list and its exact-match decision unchanged |
| 12 | builder evidence and fresh independently authored held-out evidence pin the exact candidate | **HOLDS** | this run: 41 held-out tests authored against `0bad524`/`e6332fc7…`, 40 passing and one deliberate failure that is a recorded finding; all four prior suites rerun unedited at their recorded figures; the §6 census re-derived independently at 123 files / 2392 functions with zero violations |

## 9. Findings

Two, neither blocking AC-14. Full records in `findings.yaml`.

**V1-R1P-01 — LOW, `MATERIALLY_NEW`, non-blocking.** `paths::relocate_legacy` decides whether a legacy OS store is
safe to delete with `read(&f).ok() == read(&t).ok()`. When both files exist but **neither can be read**, both sides
are `None`, the comparison succeeds, and the function deletes the legacy copy reporting
`"action": "removed identical legacy copy"` — having read no byte of either file. Demonstrated: with different
content in both places and mode `0o000` on each, the legacy file was removed. The stores this moves are, in the
module's own words, *non-rebuildable*. This contradicts the function's own stated contract ("different bytes at
both places is `STATE_LOCATION_CONFLICT`; nothing is overwritten").

*Why it does not block R1:* it falsifies none of the twelve items. Item 6 is the kernel install transaction, which
is untouched and independently confirmed by AR-0027 `heldout_srr4::e3`; this is the OS **operational**-store
relocation, a different mechanism. Whether it bears on capability D6/B1 acceptance is for the family verifier who
owns those capabilities.

*Why `MATERIALLY_NEW` and not `RESIDUAL`:* same capability area as BC-P2-31, **different mechanism**. BC-P2-31's
inventoried mechanism is non-rebuildable state *stored in, or classified as, derived state* — a location and
classification defect, which `p3::c1`/`c2` show is genuinely closed. This is an incorrect identity comparison
inside `relocate_legacy`, a function that did not exist at `cap2-candidate-0` and was written by the repair that
closed BC-P2-31. Frozen gate contract §8 makes a new mechanism, and a regression a repair introduced, MATERIALLY_NEW.
I have not shaded a new class into a residual to let the phase finish; equally I have not inflated it — it is LOW,
narrow, and non-blocking for AC-14, and I say so plainly.

**V1-R1P-02 — INFO, `MATERIALLY_NEW`, non-blocking.** `product_identity.py` prints an annotated tag's tag-object id
as `commit:` (§1). Orchestration tooling, not product source; no R1 item depends on it.

**Prior findings.** `prior-findings-disposition.yaml` disposes of the iteration-0 findings my evidence bears on.
**CLOSED (5)** — A0-E1-02 and A0-F4-02 (BC-P2-09, T2 binding), A0-D6-01 (BC-P2-31, OS stores), A0-A2-01
(BC-P2-35, post-install integrity), A0-A2-02 (BC-P2-36, unauthenticated presentation).
**NOT_APPLICABLE to this scope (5)** — A0-F4-03, A0-A2-03, A0-S5-02, A0-F4-04, A0-F3-01 — plus the 43 remaining
blocker classes, which belong to the iteration-1 family verifiers.

A0-F4-03 deserves a word, because it would have been easy to over-claim. BC-P2-39's mechanism is specifically that
plugin `authorize`/`register` derive the gate decision from a **plugin** descriptor's own declarations. What I
tested (`p3::d1`–`d6`) is the **tool-installation** surface added under OD-P2-03 — a different code path that
shares the principle (Contract v3 F4) but not the implementation. The principle holds where I tested it; that is
not evidence about the plugin path, so I record A0-F4-03 as not established by me rather than as closed.

No iteration-0 status was adopted; every CLOSED rests on a test I wrote and ran on this candidate.

## 10. Regression, reproduced independently

| Suite | **My run** |
|---|---|
| `cargo test --lib` | **276 passed; 0 failed; 0 ignored** |
| `cargo test --test certification` | **207 passed; 0 failed; 0 ignored** (1230s) |

Run in one pass each — no chunking, so no union argument is needed. `evidence/REGRESSION.txt`. These match the
figures the orchestration commit message records for this candidate — that message was visible in my dispatch
context, so I do not claim to have been blind to them; the runs, and the logs, are mine.

## 11. What I could not establish

Stated plainly, because a verification is only as good as its boundaries.

1. **A provisioned machine holding a genuine signed *release*.** My harness mints roots and binding authorities and
   drives `gov trust provision`/`bind` for real, but I did not mint a full signed release payload and install it.
   So item 5's "verified bytes installed without substitution" rests on the OD-P2-02 refusal path, the payload
   consistency check, the tamper-detection path and the prior suites — not on my own end-to-end signed install.
   BC-P2-37 and BC-P2-38 are `NOT_APPLICABLE` for the same reason.
2. **The plugin path of BC-P2-39, and BC-P2-40.** `capabilities/binding.rs` and `pincache.rs` are new and
   substantial. I established the T2 binding of the plugin *registry* (`p3::c4`), not the plugin
   `authorize`/`register` gate decision and not the binding of plugin implementation bytes. The OD-P2-03
   tool-installation surface I did test shares Contract v3 F4 as a principle but not an implementation, so I do
   not carry it across. Plugin family verifier's scope.
3. **Key rotation and revocation through a root succession that drops the `t2-binding` delegation.** `t2.rs`
   documents `Unauthorised` for this; I tested the version-rollback and unlisted-key paths (`p1::a6`, `a7`) but not
   a live succession. Later-lifecycle (R2 requires a rotation/revocation drill), not a Phase-2 blocker.
4. **Concurrency and crash behaviour of the new scheduler** (`scheduler/mod.rs`, 2299 new lines). I established that
   its `admit` is a different function from `srr::admit` and does not install kernel bytes, so it is not a kernel
   ingress; its own correctness is the relevant family verifier's.
5. **Attacker with the operator's full OS privileges.** `t2.rs` states plainly that against that attacker the
   primitive is detection-grade, not proof. I did not test it because the product does not claim it. Recorded as a
   later-lifecycle note, not a defect.

## 12. Verdict

**`R1_PRESERVED`.**

All twelve frozen R1 items hold for `cap2-candidate-1` across every changed area, established with my own
independently authored held-out evidence on this exact candidate. All four prior R1 held-out suites reproduce their
recorded figures exactly — AR-0027 26/3, AR-0029 26/2 of 28 with `ho_f` still not compiling, AR-0031 27/7 with the
same seven tests — and the only new failure anywhere is AR-0033's `hv_a::a1` size pin, whose property holds with
zero §6 violations over 3.2× the functions. Every HO-0033 structural count and shape is unchanged. The regression
is 276/0 and 207/0, run by me.

`ROT_PHASE1_CANDIDATE_ACCEPTED_R1` **remains valid for this candidate**. It is not re-issued here (frozen gate
contract §9.3).

The two findings are recorded for the orchestrator and the family verifiers: neither falsifies an R1 item, and
V1-R1P-01 is labelled `MATERIALLY_NEW` honestly, because its mechanism is not the one BC-P2-31 inventoried.

*Verdict token.* `AGENT_RUNS/README.md` lists this role's vocabulary as
`R1_ACCEPTANCE_PRESERVED` / `R1_ACCEPTANCE_NOT_PRESERVED`, while P2-HO-0045 and my dispatch require
`R1_PRESERVED` / `R1_NOT_PRESERVED` / `INCOMPLETE`. I follow the handoff, which is the specific and later
instruction for this run; the run report carries `R1_PRESERVED` and records the README's alias, so the
orchestrator can reconcile the two without guessing which I meant. Bookkeeping only — not a finding.

## 13. Reproducing this

```bash
release/capability-baseline/verify-1/r1-preservation/heldout/RUN-ALL [<scratch dir>]
```

It verifies the candidate identity, builds the candidate, asserts byte identity of every prior suite file, runs all
four prior suites plus my 41 tests with one PASS/FAIL line each, runs the labelled `hv_a::a1` and `derive.py`, and
runs both regression suites. Expected: my suite 40 pass / 1 fail (`p3::c5`, finding V1-R1P-01); AR-0027 26/3;
AR-0029 26/2 with `ho_f` not compiling; AR-0031 27/7; AR-0033 30/1 (`hv_a::a1` size pin); labelled `a1` zero
violations; `derive.py` zero violations in all three configurations; lib 276/0; certification 207/0.

**How the script was exercised, stated exactly.** `RUN-ALL` was run end to end and reached every section: it
staged and `cmp`-verified all 26 prior-suite files, produced a PASS/FAIL line for all four prior suites and all
four of mine, ran the labelled `hv_a::a1` and `derive.py`, and ran the regression. Two defects in the script
itself surfaced during that exercise and were fixed in the committed version: a `local a=$1 b=$a` that expands
`$a` before `local` assigns it (which `set -u` turned into an abort), and a crate label printed after `shift`.
The evidence files in `evidence/` are the transcripts of the **dedicated runs** of each section rather than of a
single final end-to-end invocation: late in the run the machine reached a load average above 90 (several
iteration-1 verifiers building at once) and a re-run purely to reproduce one consolidated transcript would have
taken hours of contended CPU for no new information, so I stopped it rather than add load. Every figure in this
report comes from a run recorded in `evidence/`, and every one of them is reproducible with the command above.
