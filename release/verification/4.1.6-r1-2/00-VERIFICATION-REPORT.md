# AR-0029 — fresh independent R1 re-verification of `srr1-r1-candidate-2`

| Field | Value |
|---|---|
| Run | `AR-0029`, role `verifier-b`, R1 verification **iteration 2** |
| Gate | `GATE-R1-CANDIDATE-ACCEPT` |
| Handoff | `HO-0029` (`release/orchestration/phase-1/HANDOFFS/HO-0029-r1-reverification.md`) |
| Candidate | `srr1-r1-candidate-2` — repair work commit `4c7c40c` (AR-0028) |
| Verified at worktree HEAD | `2baff074095532d0e7ff42dad2f6fa316f771207`, branch `phase1/srr1-r1-verify-2` |
| Prior verdict | AR-0027 `BLOCKING_FINDINGS_PRESENT` on candidate 1 (`AR27-B1`, MEDIUM) |
| Toolchain | `cargo 1.98.1 (797e8a9bc 2026-08-05)`, `rustc 1.98.1`, Linux 6.6.87.2-microsoft-standard-WSL2 |
| **Verdict** | **`BLOCKING_FINDINGS_PRESENT`** |
| Blocking findings | 2, both MEDIUM — `AR29-B1`, `AR29-B2`; see `10-BLOCKING-FINDINGS.md` |
| `NEW_OWNER_DECISION_REQUIRED` | **none** |
| `REQUIRES_R0_OR_OWNER_ADJUDICATION` | **none** |
| STOP conditions | **none** — every pinned digest matched |

## Independence

I am not AR-0027. I did not author this implementation, the repair, `ARCH-0003`, the R0 correction or any prior
review. I authored every test in `evidence/heldout-tests/` myself; neither the builder nor the repair role has
seen them. They share no source line with AR-0027's harness and do not reuse the builder's
`tests/certification/srr_material.rs`: the metadata forge in `mint.rs` is written from my own reading of
`runtime/src/srr/metadata.rs`.

I modified **no product source, no owner record, no frozen boundary, no prior evidence**. My held-out crate is
standalone, outside the product tree and outside its cargo workspace, depending on `gov-runtime` by path — the
pattern AR-0027 used, which works well. The only capability it has that the product deliberately lacks is
**signing**, because attacking a signature-verification adapter requires forging.

I delegated nothing; no subagent was used. I read no session transcript or task-output store, opened no user
auto-memory, and did not contact the product owner.

## Digest verification — no STOP condition

Every pinned digest in `HO-0029` was verified before use. **All matched.**

| Artefact | Expected | Result |
|---|---|---|
| `…/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` | `70977d11…f1699c1` | **match** |
| `…/00-ARCHITECTURE.md` | `695aa185…` | **match** |
| `OWNER-DECISION-0006` | `90340772…28d1db` | **match** |
| `OWNER-DECISION-0007` | `4a0f61c0…bdba7d` | **match** |
| `Governance_OS_Capability_Acceptance_Contract_v3.md` | `4c2df291…7cb5ed3` | **match** |
| `ARCH-0003.yaml` accepted **body scalar** | `093cb78e…f8f71536a` | **match** |

`OWNER-DECISION-0005` (`3831cbf5…`) and `OWNER-DIRECTIVE-0004` (`26243019…`) were read and digested for the
record. Full manifest in `REVIEWED-CONTENT-DIGESTS.txt`.

## Regression reproduced

Run from the worktree with every `GOV_*` authority variable stripped and `CARGO_TARGET_DIR` in scratch:

| Suite | Repair claim | Orchestrator | **Reproduced by AR-0029** |
|---|---|---|---|
| `cargo test --lib` | 31 passed | 31 | **31 passed; 0 failed; 0 ignored** (0.40 s) |
| `cargo test --test certification` | 65 passed | 65 | **65 passed; 0 failed; 0 ignored** (100.04 s) |

Exact match, no pre-existing failures. `git diff --numstat 4c7c40c~1 4c7c40c` confirms the repair touched exactly
the five files claimed, and `tests/certification/srr.rs` is **+177 / −0** — purely additive, no pre-existing
assertion weakened. Raw output in `evidence/REGRESSION.txt`.

## AR-0027's held-out suite, re-run unmodified

The five sources at `release/verification/4.1.6-r1/evidence/heldout-tests/` were copied byte-identical (digests
re-checked against AR-0027's own manifest; all matched) and run with no edit. One filesystem symlink
`scratchpad/wt/srr1-r1-verify → srr1-r1-verify-2` lets the crate's relative paths resolve without touching a line
of AR-0027's evidence.

| File | AR-0027 on candidate 1 | **AR-0029 on candidate 2** |
|---|---|---|
| `heldout_srr` | 12 / 0 | **12 passed, 0 failed** |
| `heldout_srr2` | 8 / 0 | **6 passed, 2 failed** |
| `heldout_srr3` | 5 / 0 | **4 passed, 1 failed** |
| `heldout_srr4` | 4 / 0 | **4 passed, 0 failed** |
| total | 29 / 0 | **26 passed, 3 failed** |

**26 / 3, exactly as `HO-0029` predicts.** I confirm the three failures are the intended flips and not
regressions. Each failing assertion is one AR-0027 wrote to pin an observed *weakness*, carries `OBSERVED:` in
its message, and fails because the weakness is gone:

| test | finding | what flipped |
|---|---|---|
| `heldout_srr2::b1` | `AR27-N1` | `+14:00`, lowercase `z` and absent `expires` now all report `expired = true` (they reported `false`); the `assert!` that they do **not** expire fails |
| `heldout_srr2::b2` | `AR27-N1` | a non-emitted-format expiry is no longer "accepted without complaint": it returns `SRR_METADATA_EXPIRED` naming the canonical-form fault |
| `heldout_srr3::d3` | **`AR27-B1`** | the below-floor permitted set fell from 12 to 3 of its 35 labels; `assert!(permitted.contains("cit approve"))` fails |

Every AR-0027 test that pins a **satisfied** property still passes — all of `a1`–`a12`, `c1`–`c6` (including `c4`,
which measures the `AR27-OD1` behaviour that `OWNER-DECISION-0007` closed and which is unchanged), `d1`, `d2`,
`d4`, `d5`, and all of `e1`–`e4`. Nothing failed that was passing for a reason other than these three findings.
Raw output in `evidence/AR-0027-HELD-OUT-RERUN.txt`.

One thing the re-run itself reveals, which becomes finding `AR29-B1`: `d3`'s REFUSED column still lists
`trust root-update`, because `d3` sweeps operation **labels** through `guard_light` rather than driving
operations. Eight of its 35 labels have no guard call site anywhere in the product.

## My own held-out evidence

**35 independently authored tests in six groups; 31 pass, 4 fail.** The four failures are my own `OBSERVED:`
weakness assertions: `ho_b_coverage::b1`, `::b2` (finding `AR29-B1`) and `ho_c_deadlock::c3`, `::c4`
(condition `AR29-C1`). Passing means "the asserted behaviour is what candidate 2 does".

| Group | Tests | Covers | Result |
|---|---|---|---|
| `ho_a_allowlist.rs` | 6 (`a1`–`a6`) | the `AR27-B1` repair: exact-match semantics under 63 near-miss forms, default-refuse for unknown labels, the real guard across all 28 guarded labels, `REFUSAL_CLASSES` decides nothing, no false positives on an unmarked machine, the single exit point | 6 / 0 |
| `ho_b_coverage.rs` | 6 (`b1`–`b6`) | **guard coverage**: is the guard on the path at all, for each §6 bullet; §5 availability below floor | 4 / **2** |
| `ho_c_deadlock.rs` | 5 (`c1`–`c5`) | `Marking::Unreadable`: seven corruption shapes, the restore half, the exit half, the reporting divergence, and a readable-marking control | 3 / **2** |
| `ho_d_expiry.rs` | 5 (`d1`–`d5`) | `AR27-N1`: the canonical-form gate against 20 RFC-3339 variants, four fail-closed directions, does-not-brick, syntactic-only observation, inheritance by every consumer | 5 / 0 |
| `ho_e_rootexpiry.rs` | 6 (`e1`–`e6`) | `AR27-N2`: both limbs of the root-rotation argument measured on the candidate, the enforced half of the profile, honest reporting, no vestigial branch | 6 / 0 |
| `ho_f_preservation.rs` | 7 (`f1`–`f7`) | `AR27-N4` crate-wide, no signing capability, five/five census, the `AuthenticatedRelease` constructor claim, D-0007 separation, Contract v3, floor monotonicity | 7 / 0 |

Sources in `evidence/heldout-tests/`, full output in `evidence/HELD-OUT-TEST-OUTPUT.txt`, reproduction in
`evidence/REPRODUCTION.md`.

---

# Primary focus — is `AR27-B1` structurally closed?

## A. The decision procedure: **YES, genuinely structural**

I attacked the allow-list directly and could not break it.

**Is refusal the default for an operation in neither list?** Yes. `permitted_activity` is the whole decision
procedure; `guard` and `guard_light` both call it first and refuse on `None`. Nothing is consulted *in order to*
refuse. I probed the empty string, whitespace, a bare em dash, a NUL, an emoji, proper prefixes of permitted
labels (`update`, `kernel`), proper substrings (`apply`, `reinstall`, `--apply`), a proper superstring
(`checkpointing`) and invented labels — every one refused, and every one reported under §6 bullet 1
(`ho_a_allowlist.rs::a2`).

**Do exact-match semantics hold?** Yes, against 63 distinct near-miss forms, **0 permitted**
(`ho_a_allowlist.rs::a1`): upper-case, leading/trailing space, tab, newline, NUL suffix, `gov ` prefix, doubled
inner space, NBSP for space, em dash for `--`, a Cyrillic homoglyph for `e`, one-character truncation at each end,
`--force` and `-unverified` suffixes, a `; gate answer` suffix, and the two forms `HO-0029` names specifically,
`kernel reinstall --force` and `update --apply-unverified`.

**Is the permitted set exactly four?** Yes. Sweeping all 28 labels that reach a break-glass guard anywhere in the
product — 27 `guard_write` labels plus `update --rollback` from `update.rs:410` — against the real `guard` on a
marked machine (`ho_a_allowlist.rs::a3`):

```text
PERMITTED ["checkpoint", "update --apply", "kernel reinstall", "update --rollback"]; REFUSED 24 others
```

Every refusal carries `SRR_BELOW_FLOOR_REFUSED`, `refusal_policy = "allow_list_default_refuse"` and the exact
`DEGRADED — RECOVERY ONLY` marking. All seven of `AR27-B1`'s operations (`cit approve`, `cit reject`,
`gate revoke`, `handoff return`, `plugins unregister`, `adopt extract-legacy`, `adopt build-memory`) are refused
through the real guard. **No residual of `AR27-B1` remains at the guard.**

**Does `REFUSAL_CLASSES` decide anything?** No (`::a4`). A named label and an invented one are refused
identically, differing only in the `refused_class` string; every class it can report is a §6 activity; no entry
is simultaneously permitted.

**Is the guard free of false positives?** Yes (`::a5`). On an unmarked machine, and after a cleared exit
(`active: false`), all 28 labels proceed. The allow-list has not become a general brake.

**Are all four permitted operations genuinely §5 activities?** Yes, on my own reading of §5, not the repair's:
`checkpoint` is backup/export and advances no governed record; `kernel reinstall` is uninstall/reinstall;
`update --apply` and `update --rollback` are restoration of an authenticated release. Each is asserted to name an
activity §5 actually lists.

**Do all three installation paths stay authenticity- and floor-checked inside `admit`?** Yes. The floor check is
step (9) inside `admit`, scoped over the `Ingress` enum, and `--break-glass` relaxes the floor check only:
`SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE` guards authenticity independently, and break-glass entry additionally
requires an owner-signed `recovery`-role token bound to this machine and to the measured payload digests.

**`update --rollback`, not in AR-0027's 35-label set:** correctly permitted, and still floor-checked.
`update.rs:410` calls `breakglass::guard(&MachineState::open()?, FRAMEWORK_NAME, "update --rollback")`, then
`rollback_internal` runs `srr::admit(Ingress::Rollback, …)` at `update.rs:450` with the break-glass flag. Same
verifier, same floor check. Confirmed permitted at the guard (`::a3`) and present in the `admit` census (`f3`).

## B. Guard coverage: **NO — and this is where the candidate fails**

Having satisfied myself the decision procedure is right, I asked the prior question the repair does not: **is the
guard on the path at all?** For two of §6's bullets it is not.

`gov trust root-update` re-anchors the machine's trusted root and revokes keys by omission —
`trust_policy_mutation`, §6 bullet 4 — and `provision::root_update` calls neither `control::guard_write` nor
`breakglass::guard`. Measured end to end on a marked machine: the anchor moved from version 1 to version 2, one
key was revoked, the root metadata high-water advanced to 2, and the machine remained marked throughout.
That is **`AR29-B1`**.

`gates::create_system` saves a `human-gate` record with no guard, and is reachable below floor from
`gov kernel override` and from inside the allow-listed `update --apply` itself. That is **`AR29-B2`**.

Full statement, classification and counterexamples in `10-BLOCKING-FINDINGS.md`. Both are labelled
**materially new blocker classes**, not residuals of `AR27-B1`: `AR27-B1` was a defective decision procedure at a
guard the operation reached, and that is fixed; these are missing enforcement points on paths that reach no guard.

**Can any privileged governed mutation reach or bypass `guard_write` below floor?** `guard_write` itself cannot
be bypassed — the 27 labels that reach it are all correctly decided. The failure is that `guard_write` is not on
every path §6 covers. One further structural note, non-blocking: `guard_light` returns `Ok` when
`resolve_state_root()` errors. The repair left that untouched and is right to — it is the "no protected state on
this machine" case, and `AR27-OD1` is closed — but it is fail-open, and it is the one remaining `Ok` path in the
guard that is not the allow-list.

---

# The three judgement calls `HO-0029` asked me to weigh

## 1. Deadlock risk from `Marking::Unreadable` — **the repair's claim is half right**

Refusing on an unreadable marking is the safer default and I endorse it. The repair's claim that "the exit path
stays open" is **true for restoration and false for exit**.

Restoration stays open: with an unreadable record, all four permitted operations still pass the guard, because
the allow-list really is consulted before any state read (`ho_c_deadlock.rs::c2`). Exit does not: `try_exit` goes
through `Degraded::load`, which reads the same file with the opposite disposition, returns `None` on an
unreadable record and writes nothing. So a machine that installs an authenticated release above **both** floors —
the exact `OWNER-DECISION-0006` §7 / `OWNER-DECISION-0007` §2 exit condition — still refuses every governed
operation, while `gov trust status` reports `degraded: null` and `gov trust break-glass` reports
`currently_degraded: false` (`::c3`, `::c4`).

I graded this **LOW and non-blocking**, not because the defect is unreal but because reachability is low and the
state is escapable: `write_durable` is atomic so no crash produces it, no product writer emits a record without a
boolean `active`, the refusal names the offending file in `details`, and the owner — inside the `ARCH-0003` §1
trusted boundary — can remove it. A recovery mode you cannot exit would be a defect; this is a wrong state an
operator can see and leave. It is recorded as `AR29-C1`, labelled a **residual of `AR27-B1`** because both the
code and the claim are new in repair 1, and it should be fixed in the same cycle as the blockers. The control
case passes: with a readable marking the machine holds below the high-water, holds on an unauthenticated release,
and clears on an authenticated at-floor release (`::c5`).

## 2. The narrower allow-list — **the reasoning holds; §5 is not stranded**

The repair's argument is that §5 is permissive ("may include") while §6 is a MUST NOT, so erring narrow cannot
breach the owner decision. I verified the reasoning rather than the preference, and it holds.

`task status` is `orchestration::tasks::set_status` behind `authority::require(p, "mutate_task_status")`; it
writes `task_status` and `updated` and saves the record. `cit simulate` writes `impact` and
`cit_status = SIMULATED` back to the transaction. Both advance the lifecycle of a governed record, so both are §6
bullet 1 on the criterion the repair states beside the table. Refusing them is right.

**Is anything an operator needs for diagnosis now unreachable?** No. I enumerated every label that reaches
`guard_write` from the candidate's source — 27 — and none is a read surface (`ho_b_coverage.rs::b5`).
`gov doctor`, `gov trust status`, `gov trust break-glass`, `gov kernel verify`, `gov kernel trust`,
`gov task list`/`show`, `gov gate list`, `gov cit show`, `gov audit`, `gov verify`, `gov memory query`,
`gov contract verify` and `gov release verify` never touch the guard. §5 "repair" is `gov recover`, which guards
nothing itself and whose only guarded downstream call is `checkpoints::create` — label `checkpoint`, on the
allow-list. §5 backup/export is `gov checkpoint create` and `gov upstream prepare`, both available. On a marked
machine `gov trust status` still reports posture, floors, the marking and the exit condition, and
`gov trust break-glass` reports `requirements.network_required = false`.

One caveat I found and record as `AR29-N4`: `update --apply` is *nominally* permitted but cannot complete below
floor when a Human Gate is required, because answering that gate is (correctly) refused. Not a deadlock —
`kernel reinstall` and `update --rollback` are gate-free — but the allow-list and the reachable behaviour should
be made to agree.

## 3. `ROOT_EXPIRY_PROFILE` — **the reasoning is sound, the profile is honest, the state is reported**

I tested the argument instead of reading it.

**Is root rotation genuinely impossible under the alternative?** Yes. `root_update` loads the current anchor
through `verifier::trusted_root` and `accept_root_succession` step (3) requires the **outgoing** root's quorum to
authorise the successor. If `trusted_root` barred an expired anchor, that call would fail. The only other door is
re-provisioning, and `provision` refuses a provisioned machine with `SRR_ALREADY_PROVISIONED` — measured, not
assumed (`ho_e_rootexpiry.rs::e3`, and again in `ho_b_coverage.rs::b4`). Barring anchor expiry would therefore
brick trust rotation permanently. This matches TUF, which applies the expiry check to the final root of the
succession chain for exactly this reason. **The repair's reasoning is correct.**

**Does rotation actually work from an expired anchor?** Yes, measured: v1 → v2 with one key revoked
(`::e2`). And an expired *successor* is still refused with `SRR_METADATA_EXPIRED`, so freshness is enforced
where the profile says it is.

**Is the profile honest about what expiry does and does not bar?** Yes. Everything it lists as enforced, is:
first provisioning refuses an expired root and `parse_self_signed_root` refuses it directly (`::e4`); succession
refuses an expired candidate; release-metadata expiry is a hard `SRR_METADATA_EXPIRED` at admission;
timestamp/snapshot expiry downgrades currency to `STALE`; a break-glass token's expiry refuses the token; and
after `AR27-N1` "expired" includes absent and non-canonical. Everything it lists as not enforced, is not: an
expired anchor still loads and still authorises its delegated roles (`::e6`).

**Is the state still reported honestly?** Yes. `gov trust status` carries
`trust_anchor.expired_against_local_clock = true` with the anchor's `expires` (`::e1`), and no code or comment
claims an expired anchor is refused. The vestigial identical-arms branch that was `AR27-N2` is gone, and
`trusted_root` names the profile it implements (`::e5`). **`AR27-N2` is closed.**

---

# `AR27-N1` and `AR27-N4`

## `AR27-N1` — **CLOSED**

`Envelope::is_expired` is `self.expiry_fault(now).is_some()`, so every consumer inherits the gate with no
call-site change. I attacked the canonical-form gate with 20 RFC-3339 and near-RFC-3339 forms — offsets
`+00:00`, `+14:00`, `-11:00`, lowercase `t`/`z` in all three combinations, fractional seconds, a space
separator, missing seconds, no zone, date only, two-digit year, a leading `+`, leading/trailing whitespace, a
trailing newline, a trailing NUL, slashes, and empty. **Every one is rejected by the gate and reports as
expired** (`ho_d_expiry.rs::d1`). Fail-closed holds in all four directions including the `expires == now`
boundary (`::d2`).

**Does fail-closed brick legitimate operation?** No (`::d3`). What `util::now_iso` emits passes the gate — I
assert this against the live clock, since a profile whose own clock reading failed its own gate would refuse
everything forever. A real signed root with an ordinary future canonical expiry verifies; the same document with
each of three near-forms fails closed and the message says *why* rather than printing a non-date as a date.
Succession inherits the gate and still accepts a well-formed successor (`::d5`).

One observation, non-blocking and R2 (`AR29-N2`): the gate is syntactic, so `9999-99-99T99:99:99Z` passes as a
future expiry. Not adversary-reachable — `expires` is inside the signed byte-string — and ordering stays sound.

## `AR27-N4` — **CLOSED**

`crypto::verify` is `verify_strict(public_hex, sig_hex, message)` and nothing else. Scanning all 83 product
source files with comments stripped: **zero** imports of `ed25519_dalek::Verifier` and **zero** bare `.verify(`
calls (`ho_f_preservation.rs::f1`). The permissive verifier is out of scope crate-wide, not merely unused —
`verify_strict` is an inherent method on `VerifyingKey`, so choosing the wrong entry point cannot weaken a
signature check. Behaviourally, `verify` and `verify_strict` are one behaviour: a good signature verifies through
both, and a signature malleated by `S + L` is refused by both with the same code.

---

# Disposition of the frozen R1 section, item by item

The frozen boundary's R1 section (digest `70977d11…`) lists twelve criteria.

### R1-1 — "a mature reviewed TUF/cryptographic implementation is used correctly" — **SATISFIED**

`ed25519-dalek` 2.x, `verify_strict` only, with the permissive trait out of scope crate-wide (`AR27-N4` closed,
`f1`). No curve, point-decompression or malleability logic reimplemented. Key ids derived from key material, not
taken from the document. Signatures are over the exact bytes of the `signed` member via `RawValue`, and the
policy is parsed from those same bytes. I re-ran AR-0027's twelve adapter attacks unmodified — all 12 still pass
(signature lifted across documents, key-id confusion, role confusion, threshold-by-repetition,
unsatisfiable/zero thresholds, trailing bytes, duplicate `signed`, unsigned envelope, malleability, unsupported
scheme, spec-version and `_type` confusion). I additionally confirmed threshold accounting rejects an expired
successor while accepting a well-formed one, and that a role key of the correct role verifies while the document
is otherwise identical.

### R1-2 — "candidate/source files cannot create their own trusted identity" — **SATISFIED**

Unchanged by the repair and re-confirmed by AR-0027's `e4` re-run (passing): a candidate whose payload, manifest
and lock are perfectly mutually consistent is refused with `SRR_RELEASE_UNVERIFIED` on a provisioned machine.
Identity comes only from signed metadata chaining to the protected anchor, or from the machine's own protected
installed record matched on **payload digests** (`SRR2-R1-C2`). `provision` refuses an anchor sourced from inside
a governed project or any `.git`/`governance` path component (re-read at `provision.rs:84`).

### R1-3 — "wrong keys, modified metadata/payload/migration, replay, downgrade and expiry fail closed" — **SATISFIED, and strengthened**

All of AR-0027's `c1`/`c2` matrix still passes. The expiry limb is materially stronger than at candidate 1:
`AR27-N1` is closed, and the three fail-open forms AR-0027 measured now all fail closed. My own group D adds 20
forms and the four fail-closed directions.

### R1-4 — "all privileged ingress paths call the common verifier" — **SATISFIED**

Exactly **5** `srr::admit` sites (`init.rs:237`, `adopt.rs:638`, `update.rs:213`, `update.rs:450`,
`cli/src/main.rs:939`) and exactly **5** `install_kernel` call sites (`init.rs:244`, `adopt.rs:642`,
`update.rs:220`, `update.rs:467`, `cli/src/main.rs:944`), each paired, enumerated by the test rather than by
grep (`f3`). `install_kernel` takes `&AuthenticatedRelease` and has no path-taking variant. The floor check is
inside `admit`, scoped over the `Ingress` enum, and binds all six ingresses.

The transaction abort is still not a usable bypass: `rollback_internal` is private with exactly two callers —
`rollback_opts` (`transaction_abort = false`, the only public entry, where the CLI lands) and one call inside
`apply_update_opts`'s error arm. On the abort path `admit` has already succeeded, `record_installed` is not
called and no floor advances.

One correction to how this item has been worded, recorded as `AR29-N1` and **not** blocking: the property is
**not** type-enforced. Every field of `AuthenticatedRelease`, `Staged`, `MachineState` and `Floors` is `pub`, so
a struct literal compiles from outside the crate — `f4` is that literal and it runs. The claim that holds is the
enumerated five/five one, which I verify. AR-0027's "no public constructor" and the repair report's
"constructible only by `admit`" overstate it.

### R1-5 — "verified bytes are staged, installed and used without substitution" — **SATISFIED**

Untouched by the repair. `staging::stage` copies into private machine-state staging first and measures the staged
copy; `verified_payload()` returns that same directory; `install_kernel_inner` re-checks the committed manifest's
`payload_hash` against `auth.payload_hash` and refuses with `SRR_COMMITTED_BYTES_MISMATCH`. Per-file and
aggregate digests are enforced in both directions.

### R1-6 — "staging/install/rollback/recovery are atomic and crash-safe" — **SATISFIED**

Ordering re-read at `staging.rs`: journal intent (fsync) → build `.srr-new` → journal swap (fsync) → rename
`dest`→`.srr-old` → rename `.srr-new`→`dest` → fsync(parent) → journal committed → verify committed bytes → drop
`.srr-old` → **(9) advance the floors** → journal done. Floors last, which is the safe order. AR-0027's `e3`
interruption test passes unmodified.

### R1-7 — "metadata/release high-water is durable and monotonic" — **SATISFIED**

`raise_release`, `raise_minimum_secure` and `raise_metadata` are upward-only, and an unauthenticated observation
(`signed = false`) raises nothing at all (`f7`). Floors live outside every repository and survive project
deletion (AR-0027 `c6`, passing). `AR27-N5` (a case where a floor fails to *rise*) stays R2-carried.

### R1-8 — "post-install integrity remains distinct and D-0007 controls remain effective" — **SATISFIED**

`kernel_trust.rs` contains no reference to `srr::admit`, `AuthenticatedRelease`, `Authenticity`, `breakglass`,
`below_floor` or `Floors`; `admit_inner` contains no reference to `kernel_trust` (`f5`). D-0007 establishes
**intact** only; `verifier::Authenticity` establishes **authentic**; `below_floor` establishes **admissible**.
`install_kernel` calls `kernel_trust::clear()` so the integrity verdict is recomputed, never inherited.

### R1-9 — "project, CLI, environment, model and plugin inputs cannot create trust or approval" — **SATISFIED**

`refuse_authority_env()` is the first statement in `admit`, and all nine variables are refused on
`var_os(..).is_some()`, so an empty value is refused too (AR-0027 `c5`, passing). No signing capability exists
anywhere in product source — zero hits for `SigningKey`, `ed25519_dalek::Signer`, `from_keypair_bytes` or a PEM
private-key header, once the secret-**detector** regex in `security/secrets.rs` is excluded by name (`f2`). No
`--skip-verify`, `--force-unsigned` or equivalent flag, env var or cargo feature.

**Qualification.** This item is about *inputs* creating trust. The two blocking findings are about *operations*
proceeding below floor with owner-held authority, not about an input manufacturing authority, so I do not fail
R1-9 on them. They fail the owner decision, not this criterion.

### R1-10 — "CI/multi-machine provisioning follows ARCH-0003" — **SATISFIED**

Unchanged by the repair; `state.rs` is not in the diff at all. `provision` refuses repository-sourced anchors;
`GOV_MACHINE_STATE_DIR` provisions a second machine and is refused once the default root is provisioned;
`GOV_HUMAN_GATE_APPROVED` is refused. `AR27-OD1` is closed by `OWNER-DECISION-0007` §1 and not reopened.

### R1-11 — "the original product controls, Gate W and G0–G6 implementation mappings remain valid" — **SATISFIED**

All 64 pre-existing certification scenarios plus the repair's one new one pass (65 / 0), with `srr.rs` purely
additive at +177 / −0 and no pre-existing test edited. The Contract v3 canonical import is **byte-identical** to
the owner source at the repository root — both `4c2df291…` — the digest is pinned in `contracts.rs`, and
`CONTRACT_SOURCE_DIVERGED` is present (`f6`).

### R1-12 — "builder evidence and fresh independently authored held-out evidence pin the exact candidate" — **SATISFIED**

The builder's report and the repair report are present with digest manifests; this report and its 35 held-out
tests pin worktree HEAD `2baff074…`, candidate tag `srr1-r1-candidate-2`, repair work commit `4c7c40c`.

---

# All ten `OWNER-DECISION-0006` requirements against candidate 2

| § | Requirement | Disposition |
|---|---|---|
| 1 | Recovery release must still be authentic | **SATISFIED.** Break-glass relaxes the floor check only; `SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE` guards authenticity separately. `try_exit` also refuses to clear on an unauthenticated release (`c5`). |
| 2 | Authority cannot be manufactured | **SATISFIED.** Owner-signed `recovery`-role token in a protected out-of-band inbox, bound to product, `machine_id`, a single-use nonce and the measured payload digests. AR-0027's `d1`/`d2` pass unmodified. |
| 3 | Durable entry record | **SATISFIED.** `enter` writes machine id, both floors at entry, recovery release identity and digests, reason, `entered_at`, token nonce/issue/expiry/digest and ingress, durably, before consuming the nonce. |
| 4 | Byte-exact `DEGRADED — RECOVERY ONLY` | **SATISFIED.** U+2014, pinned against raw bytes. |
| 5 | Permitted activities | **SATISFIED.** Inspection, diagnosis, repair, backup/export, uninstall/reinstall and restoration all reachable below floor (`b5`). One caveat, `AR29-N4`. |
| 6 | Refused activities | **PARTLY SATISFIED — `AR29-B1`, `AR29-B2`.** Bullet 1 is now genuinely a class control and is **closed**; bullets 5, 6 and 7 hold. **Bullet 2 (Human Gate creation) and bullet 4 (trust-policy mutation) are not enforced**, because the operations that perform them reach no guard. |
| 7 | Exit condition | **SATISFIED with one condition.** Single policy point, stricter both-floors reading, verified behaviourally. `AR29-C1` records the unreadable-marking case where exit is unreachable. |
| 8 | Floor is not lowered by break-glass | **SATISFIED.** `enter` writes no floor; `raise_*` are monotonic-only. |
| 9 | Ingress consistency | **SATISFIED.** The floor check is inside the one verifier every ingress calls, including `update --rollback` via `admit(Ingress::Rollback)`. |
| 10 | Works with no network | **SATISFIED.** Every break-glass input is a local file; `gov trust break-glass` reports `requirements.network_required = false`; AR-0027's `d5` (poisoned proxy variables) passes. |

---

# Verdict

**`BLOCKING_FINDINGS_PRESENT`.**

The repair did what it set out to do. `AR27-B1` is **structurally closed**: the allow-list is genuinely
exact-match and genuinely default-refuse, it survived 63 near-miss forms and every invented label I could think
of, and the below-floor permitted set is exactly the four §5 entries across all 28 guarded labels.
`AR27-N1`, `AR27-N2` and `AR27-N4` are all closed, and I verified the `ROOT_EXPIRY_PROFILE` reasoning
independently rather than accepting it — it is correct. The regression reproduces exactly, no pre-existing test
was weakened, and the preservation obligations hold.

What the repair did not do — and was not asked to, because nobody had found it — is put the guard on every path
`OWNER-DECISION-0006` §6 covers. A perfect decision procedure at a chokepoint enforces nothing for an operation
that never passes through it. On candidate 2 a machine marked `DEGRADED — RECOVERY ONLY` can re-anchor its
trusted root and revoke keys by omission, and can have new Human Gates created on it. Both are explicit MUST NOTs
in the same owner record `AR27-B1` came from. I record both as **materially new blocker classes**, not residuals,
and I say so plainly for the convergence count: the repair converged on what it was given.

**Recommended next action.** A second bounded R1 repair cycle covering `AR29-B1` and `AR29-B2`, and — because
they are cheap and in the same files — `AR29-C1`, `AR29-N3` and `AR29-N4`. The right shape is probably not a
guard call bolted onto `root_update` and `create_system` one at a time, but a single enforcement point every
trust-changing and gate-creating path must pass, so the next operation added to the product inherits it. That is
the same lesson `AR27-B1` taught one level down. No new owner decision is required; `OWNER-DECISION-0006` §6
already decides the policy.
