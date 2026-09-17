# AR-0028 — bounded R1 repair 1 of `srr1-r1-candidate-1`

| Field | Value |
|---|---|
| Run | AR-0028, fresh isolated R1 repair role, repair cycle 1 |
| Handoff | `release/orchestration/phase-1/HANDOFFS/HO-0028-r1-repair-1.md` |
| Branch / worktree HEAD at start | `phase1/srr1-r1-repair-1` @ `7a2ebcfad6cd54375dd0b2b214e51d94ce48ebdc` |
| Repairs | `AR27-B1` (blocking), `AR27-N1`, `AR27-N2`, `AR27-N4` |
| Verdict | **`READY_FOR_INDEPENDENT_OS_VERIFICATION`** — a readiness declaration only, never an acceptance |
| Graded by | a NEW fresh independent verifier, with its own held-out tests. Not by this run. |

Files changed (all of them, nothing else):

```
runtime/src/srr/breakglass.rs   258 +   69 -
runtime/src/srr/crypto.rs        17 +   22 -
runtime/src/srr/metadata.rs     128 +   14 -
runtime/src/srr/verifier.rs      42 +    6 -
tests/certification/srr.rs      177 +    0 -      (purely additive: no pre-existing test touched)
```

---

## 1. `AR27-B1` — the blocking finding

### What was wrong

`runtime/src/srr/breakglass.rs` enforced `OWNER-DECISION-0006` §6 bullet 1 through a **substring deny-list** of 26
strings (`REFUSED_OPERATIONS`). Anything not matching proceeded while the machine was marked
`DEGRADED — RECOVERY ONLY`. AR-0027 measured 23 refused / 12 permitted across the product's own `guard_write`
labels, of which **seven had no §5 cover**: `cit approve`, `cit reject`, `gate revoke`, `handoff return`,
`plugins unregister`, `adopt extract-legacy`, `adopt build-memory`. The doc comment at `breakglass.rs:163` claimed
"The default is **refuse**", and the module requirement map asserted §6 row 6 satisfied. Both were false as written.

### What is true now — the change is structural, not a longer list

The policy is **inverted**. `guard` and `guard_light` now decide through one function:

```rust
pub fn permitted_activity(operation: &str) -> Option<&'static str> {
    PERMITTED_OPERATIONS.iter().find(|(label, _)| *label == operation).map(|(_, activity)| *activity)
}
```

`None` means refuse. Three properties make this a class control rather than an enumeration:

1. **The default is refusal, and the default is what runs.** No table membership is consulted to *refuse*. An
   operation is refused unless it is found on the allow-list, so an operation nobody anticipated — one added to the
   product tomorrow, one this repair never saw — is refused by construction, not by having been listed.
2. **Matching is exact, never substring.** `"kernel reinstall --force"`, `"checkpoint delete"`,
   `"update --apply-unverified"` and `"KERNEL REINSTALL"` are all refused. A deny-list has to be *wider* than the
   thing it names to be safe; an allow-list has to be *narrower*, and exact match is the narrowest.
3. **The one remaining table decides nothing.** `REFUSAL_CLASSES` (renamed from `REFUSED_OPERATIONS` so it cannot
   be mistaken for policy) only chooses which §6 bullet a refusal is *reported* under. Absence from it yields §6
   bullet 1, `normal_privileged_operation` — refusal either way. `refusal_class` is a message function.

A fourth, smaller default-refuse hole in the same two functions was closed with it: a marking record that exists but
cannot be read as a record (`read_json` error, or no `active` member) previously returned `Ok(())` — i.e. "not
marked". It is now `Marking::Unreadable`, which refuses. A machine whose marking cannot be read is not thereby
unmarked. This cannot brick recovery, because the allow-list is consulted **before** any state is read, so the exit
path stays open on a machine with an unreadable marking. `resolve_state_root()` returning `Err` is left fail-open
exactly as it was: that is "this machine has no protected state at all", the ungoverned case, not a degraded one —
and it is the machine-state path resolution this repair is forbidden to touch.

### What is permitted below floor, and under which §5 activity

Four labels. Every one is in `PERMITTED_OPERATIONS` in `breakglass.rs`, and the unit test
`every_permitted_operation_names_a_real_section_5_activity` fails if any of them names an activity §5 does not.

| operation | `OWNER-DECISION-0006` §5 activity | why it is recovery, not §6 bullet 1 |
|---|---|---|
| `checkpoint` | backup/export | captures resumable state; advances no governed record's lifecycle, decides nothing, grants no authority |
| `kernel reinstall` | uninstall/reinstall | the ingress break-glass exists to serve; the release is still authenticity- and floor-checked inside `admit` |
| `update --apply` | restoration of an authenticated release | same, and independently floor-checked inside `admit` |
| `update --rollback` | restoration of an authenticated release | restores a previously installed release; its target is admitted through `admit` like every other ingress (§9) |

`update --rollback` is not in AR-0027's 35-label set, because it reaches `breakglass::guard` from `update.rs:410`
rather than through a `guard_write` label. It was permitted before this repair (absent from the deny-list) and is
permitted after it (present on the allow-list). Under an allow-list an omission would have silently removed a
recovery path, so it is called out here explicitly.

### Two labels AR-0027 classified as §5 that are refused anyway

AR-0027 judged `task status` "inspection" and `cit simulate` "diagnosis" from their labels. In code both mutate:

* `task status` is `orchestration::tasks::set_status` — it writes `task_status` and `updated` and saves the record,
  behind `authority::require(p, "mutate_task_status")`. It is a governed lifecycle transition.
* `cit simulate` writes `impact` and `cit_status = SIMULATED` back to the change-intent transaction and saves it
  (two records, in one path). It advances a CIT from PROPOSED to SIMULATED.

Both are §6 bullet 1, so both are refused. The criterion applied, and stated in the code beside the table: *an
operation belongs on the allow-list only when it realises a §5 activity **and** it neither advances the lifecycle of
a governed record nor changes trust, authority or policy state.*

Being narrower than AR-0027 suggested is deliberate and is not a deviation from the owner's decision: §5 is
permissive ("Permitted activities **may** include"), while §6 is a MUST NOT. Erring narrow can only cost
availability; erring wide breaks the decision. §5's inspection and diagnosis remain fully available regardless,
because read-only commands (`gov trust status`, `gov doctor`, `gov recover --dry-run`, the `list`/`show` surfaces)
never call `guard_write` and so never reach this guard — verified end to end in the certification suite.

### The falsified claims are corrected, not re-asserted

* The `guard` doc comment no longer claims default-refuse while describing a deny-list. It states the decision
  procedure (`permitted_activity`), that matching is exact, and that `REFUSAL_CLASSES` decides nothing.
* The module requirement map row 6 now reads "a **default-refuse allow-list** (`REFUSAL_POLICY`): every operation
  outside `PERMITTED_OPERATIONS` is refused, so §6 bullet 1 is enforced as a class rather than as an enumeration",
  and row 5 names both the §5 text and the operation labels that realise it.
* `REFUSAL_POLICY = "allow_list_default_refuse"` names the shape of the control in one checkable place, and is
  echoed in the refusal's `details` and in the durable break-glass entry record.

**Correction to a record this run may not edit.** `release/root-of-trust/signed-release-root-v1-r1-build/00-BUILD-REPORT.md:159`
(AR-0026's build report, a historical record) says `guard_light` "refuses only what §6 lists". That was true of the
candidate and is false of this repair: it now refuses everything §5 does not list. The historical report is left
untouched; the correction is recorded here.

### Evidence that it is closed rather than moved

AR-0027's own held-out test `heldout_srr3.rs::d3`, **byte-identical and unmodified**, now prints:

```
AR-0027 D3 — while marked `DEGRADED — RECOVERY ONLY`:
  REFUSED   (32): [upstream submit, upstream export, memory select, gate create, gate answer, gate revoke,
                   gate present, decide, tools install, replan, plugins register, plugins unregister,
                   handoff create, handoff return, readiness plan, cit propose, cit simulate, cit approve,
                   cit reject, cit execute, adopt migrate, adopt extract-legacy, adopt build-memory,
                   task create, task status, task claim, task close, release build, release certify,
                   trust provision, trust root-update, skills install]
  PERMITTED (3):  [checkpoint, update --apply, kernel reinstall]
```

against 23 / 12 before. The test then **fails**, at
`assert!(permitted.contains(&gap))` for `"cit approve"` — its `OBSERVED:` assertion that the gap exists. That
failure is the finding being closed; see §5.

A new certification test, `below_floor_refusal_is_default_refuse_across_the_whole_operation_surface`, pins it in the
product's own suite: it enters genuine break-glass through the real `admit` path, sweeps all 36 real labels plus four
that do not exist, asserts the permitted set is exactly the four §5 entries, asserts each of AR27-B1's seven is
refused, and then drives `cit approve`, `cit reject` and `gate revoke` through the real `gov` binary (which exercises
`guard_light` inside `guard_write`) expecting `SRR_BELOW_FLOOR_REFUSED` with `refusal_policy =
allow_list_default_refuse`. It finishes by restoring a release above both floors and asserting the marking clears, so
§7 and §10 are shown not to be collateral damage.

---

## 2. `AR27-N1` — expiry compared lexicographically with no canonical-form gate

`Envelope::is_expired` was `!e.is_empty() && e <= now`. A `+14:00` expiry thirteen hours in the past sorted as
future; lowercase `z` likewise; an absent `expires` never expired.

The comparison's precondition — both sides in the one form this profile emits — is now **checked instead of
assumed**, in `runtime/src/srr/metadata.rs`:

* `is_canonical_utc_timestamp(s)` accepts exactly `YYYY-MM-DDTHH:MM:SSZ`, which is exactly what `util::now_iso`
  emits;
* `expiry_fault(expires, now) -> Option<String>` is the whole decision, fail-closed in four directions: absent
  `expires`, non-canonical `expires`, non-canonical `now`, or canonical `expires <= now`;
* `Envelope::is_expired` is `self.expiry_fault(now).is_some()`, so every existing caller inherits the gate with no
  call-site change: root provisioning, root succession, release metadata, timestamp, snapshot, break-glass tokens
  and `gov trust status`.

Refusal messages now carry the fault rather than formatting an absent or non-canonical value as if it were a date
(`metadata.rs` ×2, `verifier.rs` ×2, `breakglass.rs` ×1). The error **codes** are unchanged
(`SRR_METADATA_EXPIRED`).

Measured by AR-0027's unmodified `heldout_srr2.rs::b1`: all three of its attack forms now report `expired = true`
(they reported `false` before), and `b2` — "a non-emitted-format expiry is accepted without complaint" — now fails,
because it is no longer accepted.

---

## 3. `AR27-N2` — an expired trust anchor, and a branch whose two arms were identical

`verifier.rs:312-314` was:

```rust
if root.envelope.is_expired(now) {
    // An expired root does not brick an installed system, but it cannot authorise a trust change.
    return Ok(Some(root));
}
Ok(Some(root))
```

Both arms identical: the comment asserted a control implemented nowhere.

Of the two dispositions the finding authorises — implement the control, or remove the claim and state the profile —
**the claim is removed and the profile is decided and named**, as `verifier::ROOT_EXPIRY_PROFILE =
"reported_not_admission_blocking_r1"`. The constant's documentation states what is enforced and what is not:

*Enforced, fail-closed:* first provisioning refuses an expired root; root succession refuses an expired **candidate**
root; release-metadata expiry is a hard refusal at admission; timestamp/snapshot expiry downgrades currency to
`STALE`; a break-glass token's expiry refuses the token; and after `AR27-N1`, "expired" includes absent and
non-canonical.

*Not enforced, deliberately:* an expired installed anchor bars neither release admission nor authorising its own
successor.

Implementing the control instead was considered and rejected on evidence, not preference:

1. TUF walks the root succession chain and applies the expiry check to the *final* root, precisely so an expired
   root can still sign its successor. Barring it would make root rotation **permanently impossible** on a machine
   whose root has expired, because `provision::provision` refuses to re-anchor a provisioned machine
   (`SRR_ALREADY_PROVISIONED`). An expired root would brick trust rotation rather than protect it, recoverable only
   by deleting protected machine state.
2. Making anchor expiry an admission bar would disable an already authenticated installed system, which ARCH-0003
   §7 declines to do, and the architecture's own clause defers the concrete policy to the profile.

Nothing now claims the unimplemented property, and the state is still reported honestly:
`gov trust status` carries `trust_anchor.expired_against_local_clock`, and AR-0027's `heldout_srr4.rs::e1`
still passes — the observed behaviour is unchanged, only the false claim is gone. Requiring non-`UNKNOWN` currency
for trust-changing ingresses, alongside mandatory timestamp/snapshot roles, stays R2 work under `AR27-N3`.

---

## 4. `AR27-N4` — the permissive fallback in `crypto::verify`

`crypto.rs:70` was `key.verify_strict(...).or_else(|_| key.verify(...))` — a retry with the permissive verifier
exactly when the strict one refused. Zero product call sites, but public API.

`verify` is now `verify_strict(public_hex, sig_hex, message)` and nothing else. Beyond that, the
`ed25519_dalek::Verifier` **trait import is removed**: `verify_strict` is an inherent method on `VerifyingKey`, so
the permissive `verify` is no longer in scope anywhere in the crate and cannot be reached by accident. The module
doc no longer claims a property the code contradicted. AR-0027's `heldout_srr.rs::a10` (malleated, non-canonical `S`)
still passes.

---

## 5. Regression and the AR-0027 held-out re-run

Toolchain `cargo 1.98.1 (797e8a9bc 2026-08-05)`. Every run with
`env -u GOV_BREAK_GLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_MACHINE_STATE_DIR`.

| Suite | Before (baseline at `7a2ebcf`) | After | File |
|---|---|---|---|
| `cargo test --lib` | 26 passed, 0 failed | **31 passed, 0 failed** | `evidence/REGRESSION-LIB.txt` |
| `cargo test --test certification` | 64 passed, 0 failed | **65 passed, 0 failed** | `evidence/REGRESSION-CERTIFICATION.txt` |
| `cargo clippy --all-targets` | clean | clean | — |

All 26 pre-existing lib tests and all 64 pre-existing certification tests still pass. **No pre-existing test was
edited and no assertion was weakened** — `git diff --numstat` on `tests/certification/srr.rs` is `177 insertions,
0 deletions`. The deltas are 5 new lib tests (3 in `srr::breakglass`, 2 in `srr::metadata`) and 1 new certification
test.

### AR-0027's held-out suite, re-run unmodified

The five held-out files were copied byte-identical (SHA-256s in `REVIEWED-CONTENT-DIGESTS.txt` match AR-0027's
manifest exactly, `Cargo.toml` included). The only adaptation was a filesystem symlink
`scratchpad/wt/srr1-r1-verify -> scratchpad/wt/srr1-r1-repair-1`, so the crate's `../wt/srr1-r1-verify/...` paths
resolve without editing a single line of the verifier's evidence.

| File | Before | After |
|---|---|---|
| `heldout_srr` | 12 passed, 0 failed | **12 passed, 0 failed** |
| `heldout_srr2` | 8 passed, 0 failed | **6 passed, 2 failed** |
| `heldout_srr3` | 5 passed, 0 failed | **4 passed, 1 failed** |
| `heldout_srr4` | 4 passed, 0 failed | **4 passed, 0 failed** |
| total | 29 / 0 | **26 passed, 3 failed** |

The three failures are **exactly the three assertions AR-0027 wrote to pin an observed weakness**, each carrying an
`OBSERVED:` message in-source. They are the findings closing, and nothing else fails:

| test | finding | failing assertion |
|---|---|---|
| `heldout_srr2::b1` | `AR27-N1` | `OBSERVED: a non-UTC RFC-3339 expiry that is genuinely in the past is NOT treated as expired` |
| `heldout_srr2::b2` | `AR27-N1` | `a non-emitted-format expiry is accepted without complaint` |
| `heldout_srr3::d3` | **`AR27-B1`** | `OBSERVED: 'cit approve' is permitted while the machine is marked DEGRADED — RECOVERY ONLY` |

Every held-out test that pins a *satisfied* property still passes, including `c4` (`AR27-OD1`, out of scope — the
behaviour it measures is unchanged), `e1` (`AR27-N2`, unchanged by design), `e2` (`AR27-N3`, R2), `d4` (`SRR2-R1-C1`
exit policy), `d5` (offline break-glass), `c2`, `c3`, `c6` and `a1`–`a12`. Full output:
`evidence/AR-0027-HELD-OUT-RERUN.txt`.

---

## 6. Preservation obligations — re-verified after the repair

| Obligation | Check | Result |
|---|---|---|
| Compiler-enforced no-bypass | `install_kernel` takes `&AuthenticatedRelease`, constructible only by `admit` | unchanged, untouched |
| Exactly five `admit` sites | `grep -rn "srr::admit(" runtime/src cli/src` | **5** |
| Exactly five `install_kernel` call sites | `grep` less definition and inner | **5** |
| Floors at all six ingresses | `verifier.rs` ingress set untouched | unchanged |
| Durability ordering, floors last | `state.rs`, `staging.rs` untouched | unchanged |
| D-0007 separate, establishes **intact** only | untouched; `heldout_srr4::e4` passes | preserved |
| `SRR-R0-L4` vacuous | `grep -rn "SigningKey\|SecretKey\|PRIVATE KEY" runtime/src cli/src` → 1 hit, the secret-**detector** regex in `security/secrets.rs`; no key files; no flag/env/feature relaxing verification | preserved |
| `gov` verifies, never signs | `crypto.rs` gained no signing path; it *lost* the permissive verifier | preserved and strengthened |
| Contract v3 canonical import byte-identical | `4c2df291…` == repository-root source | identical |
| `SRR2-R1-C1` untouched | `EXIT_POLICY = "b_stricter_both_floors"`, `exit_satisfied` unchanged, still the single point comparing a release against an exit floor | unchanged, not widened |
| `SRR-R0-L7` | no offline/air-gapped first install added; break-glass recovery still passes `heldout_srr3::d5` with the network poisoned | unchanged |

## 7. Out of scope — not touched

* **`AR27-OD1`** (`REQUIRES_R0_OR_OWNER_ADJUDICATION`): **not implemented, not partially implemented.**
  `resolve_state_root`, `default_state_root` and `runtime/src/srr/state.rs` are **not in the diff at all**. No
  machine-state path resolution changed. `guard_light` calls `resolve_state_root()` exactly as before, including
  its fail-open-on-`Err` behaviour, which is the "no protected state on this machine" case and not the marking.
  `heldout_srr2::c4`, which measures this, still passes with the same result.
* R2-lifecycle `AR27-N3`, `AR27-N5`, `AR27-N6`, `AR27-N7`: recorded, carried, untouched.
* `SRR2-R1-C1`: `exit_satisfied` and `EXIT_POLICY` left at the stricter both-floors interim, not widened, still the
  single exit-floor comparison. They live in the file that was repaired, so the diff was kept away from them.
* `SRR-R0-L7`: no first-install ceremony added.
* No RoT-1 Revision 8, no CP-1 resumption, no D-0008/ARCH-0002 activation. No owner record, frozen boundary,
  `release/verification/**`, `release/root-of-trust/*-review*/**` or `release/releases/**` content was modified — the
  five changed files are all under `runtime/src/srr/` and `tests/`.

## 8. Nothing stubbed; one item carried

Nothing in this repair is stubbed, mocked or left partially implemented. No
`NEW_OWNER_DECISION_REQUIRED` item arose: `AR27-B1` implements a policy the owner already decided in
`OWNER-DECISION-0006` §5 and §6, and `AR27-N2` takes a disposition the finding itself authorises.

One judgement the next verifier should weigh deliberately, stated plainly rather than buried: this repair refuses
`task status` and `cit simulate` below floor, which AR-0027 classified as §5 activities. The reasoning and the code
evidence are in §1. If the product owner wants either available during recovery, it is a one-line addition to
`PERMITTED_OPERATIONS` with a §5 activity named — the table is the only place the answer lives.
