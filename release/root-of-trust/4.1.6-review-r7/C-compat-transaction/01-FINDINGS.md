# 01 — Findings (AR-0021, compatibility & transactions, RoT-1 revision 7 `d07d200`)

Severity per `HO-0021` §4. **1 HIGH (blocking), 5 MEDIUM (carried), 4 LOW.** Every finding is stated with its evidence
class (**E** executed real binaries/Git; **M** the pack's revision-7 reference executor; **D** design reading of the pack at
`d07d200`), a failure scenario, and an **architectural** correction direction. Where a finding has an unsafe reading, the
carried rule that removes it is named. The consolidated non-findings (R2-H4 and the closed classes) are in `00-REPORT.md`.

Owner requirements: OWNER-DESIGN-REQUIREMENTS-0001 (OP-1…OP-16, exclusions) and **OWNER-DESIGN-REQUIREMENTS-0002**
(the owner's binding resolution of OT-1 and OT-2), which I was routed to read (disclosed in `00-REPORT.md`).

| ID | Severity | Title | Evidence |
|---|---|---|---|
| **RV7-C-H1** | **HIGH (blocking)** | The running-mode C3 currency proof bounds the anchoring **event** age (≤ 24 h), not the Trust State's own age; an admitted air-gapped / long-offline machine performs production C3 (install, update, rollback, ingress) on a Trust State up to 90 days stale that omits later revocations — contradicting the pack's own RS-1b bound and OWNER-DESIGN-REQUIREMENTS-0002 OT-1 | M + D |
| RV7-C-M1 | MEDIUM (carried) | Protected admission store lost while the account verifier trust store survives (ordinary partial restore / OS reinstall keeping `$HOME`): the next `gov-admit` is a **first** admission and moves the account store aside **without reading its high-water**, silently discarding the machine's retained high-water and pending gate obligations | M + D |
| RV7-C-M2 | MEDIUM (carried) | The per-project record identity ("the Git common-directory identity ... never committed", `20` §9) has **no realizable value** that matches the `20` §9 / RT-196 classification for all of {worktree, moved checkout, second clone, fork, template copy}; PPR7 tests only opaque labels. RV6-M4 is **NARROWED, not CLOSED** | E + D |
| RV7-C-M3 | MEDIUM (carried) | The journal-honouring condition (`18` §5.1: the **per-project record** lists the open TX) contradicts the transaction flow (`18` §4: the per-project record is updated only at the **end**); on a **first** install no record exists until the end, so an interrupted first-install journal is not honoured and `gov recover` treats it as `FOREIGN_TRANSACTION_ARTEFACT` — defeating the recovery story CR6-C-7 was added to provide | E + D |
| RV7-C-M4 | MEDIUM (carried) | The in-migration overlay is **untracked** during the first-install transaction; an ordinary `git clean -fdx` in the crash window removes it, defeating R-INIT-9 (which guards only when `governance/overlay`/`views` still exists), so a later `gov init` produces a `COMPLETE` install with the project's classifications silently absent. RV6-M3 escalation re-opened by a different trigger | E |
| RV7-C-M5 | MEDIUM (carried) | Recovery **roll-forward** after a crash past `RENAME_EXCHANGE` in a first install depends on "migrations from ARO buffers", but the ARO is "in memory only" (`18` §1) and gone after the crash; `crashmig7`'s roll-forward branch is a stub that asserts `COMPLETE (modelled)` and mutates no tree, so the roll-forward path is unproven | E + D |
| RV7-C-L1 | LOW | Recovery undo (`20` §5) has two literal readings; after an ordinary Git/legacy operation between the crash and `gov recover`, the rename-based undo aborts (`ENOTEMPTY`) or silently replaces a file at an undo destination. Fail closed (never `COMPLETE`), but the recovery text is under-specified | E |
| RV7-C-L2 | LOW | `clock_high_water` (`24` §4.5) is raised by "the time of the anchoring event"; an anchoring event recorded while the machine's own RTC is wrong-and-ahead poisons the high-water, leaving the machine `C0-R` until real time passes the recorded value or a **root-signed** `clock_reset` | M |
| RV7-C-L3 | LOW | `floors.json` and the account store's `high-water.json` have no stated atomicity (`31` R-ADM-7″ makes only the record write atomic); a concurrent `gov` process reading floors during an admission gets a torn read | M |
| RV7-C-L4 | LOW | OT-2: the pack's target label is `NOT CERTIFIED — pending criteria`, not the owner's `NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE`, and CC-3's non-circular trusting-trust criterion is not yet executable/testable; both are carried (mostly reviewer-B scope) | D |

---

## RV7-C-H1 — HIGH (blocking) — the C3 currency proof bounds the anchoring event, not the Trust State's age

**Statement (M, D).** For a running admitted binary, `24` §4.3 R-ANC-4 permits C3 (production install, update, rollback,
recovery, ingress, binary acceptance) "only with a currency proof of at most 24 hours naming the effective state." The proof
is defined in `24` §4.4:
- **R-CUR-1 (P1)** — "a pin provisioning or **human confirmation** whose two state codes name *n* itself is **no older than
  24 hours**"; the 24 hours bounds the **event** (`confirmed_at` / `provisioned_at`), and *n* is the **effective** Trust
  State (the highest the machine holds).
- **R-CUR-2 (P2)** — an in-gate confirmation carrying "the two state codes **currently published** by the sources"; clock:
  none.

Neither proof bounds the `issued_at` of the Trust State *n*. FC-9 (`32`) bounds the state's `issued_at` to ≤ 24 h **only at
admission**. The reference executor confirms the split: `gov-admit`'s `accept()` checks `now - issued_at ≤ 24 h`
(`ADMISSION_STATE_MAX_AGE`); the running-mode `gov_run(...)` C3 check is
`anchor["names_effective_state"] and now - anchor["currency_at"] ≤ C3_CURRENCY` — its parameter list has no `issued_at`, and
the only anchor fields it reads are `class`, `anchored_at`, `currency_at`, `names_effective_state` (`cur7x.json`
`M3_running_machine.anchor_fields_read_by_gov_run`).

So a machine admitted from OP-13(b) offline media within the 24-hour window at day 0, that then never receives newer
metadata, has effective state *n* frozen at its anchored chain. On any later day within the 90-day (CI: 7-day) anchor
validity, the operator makes a **fresh** `gov trust confirm-state <n's code> <n's code>` (the codes carried on the same
offline media — OT-1 permits both OP-13(b) channels to be offline immutable media). That confirmation is ≤ 24 h old and
names the effective state, so it is a valid P1 proof, and C3 runs — on a Trust State arbitrarily stale within the anchor
validity.

**Executed evidence (M)** `cur7x.json` (the pack's revision-7 reference executor and statement world `w7world.py`,
unmodified; real Ed25519). World: T10 (`issued_at` 2026-09-13) publishes release **R8, not revoked**; T11 (2026-09-14)
**revokes R8**.
- `M1` — media prepared within 24 h (both codes name T10) at admission → **`ACCEPTED`** (conforms).
- `M2` — the **same** T10 codes at **re-admission** 37 days later → **`FIRST_CONTACT_STATE_TOO_OLD`** (admission fails
  closed; conforms).
- `M3` — the admitted binary, 37 days later, with the store holding only T10, makes `confirm-state` from the T10 media
  (event age 0) and runs C3: **`ALLOWED`**. `effective_state_age_at_C3_hours = 882.0` (36.75 days). `confirm-state` and C1
  are also `ALLOWED`.
- `M4` — control: the same binary on a machine that **did** receive T11 (held negatives include R8) → refused
  (`BINARY_REVOKED_SELF`).

**Verdicts** (`cur7x.json`): `admission_refuses_the_stale_state` **true**;
`running_machine_allows_C3_on_the_same_stale_state` **true**; `decision_has_no_state_age_input` **true**;
`no_issued_at_bound_in_anchoring_or_gate_text` **true**; `control_only_receipt_of_T11_refuses` **true**.

**Failure scenario.** An air-gapped production machine is admitted from courier media prepared within 24 h. A security defect
in release R8 is found and R8 is revoked in T11 the next day. The machine never receives T11 (it is air-gapped; the operator
brings only the original media, or media whose *immutable identity* material is current but whose *state* is the same T10).
For up to 90 days the operator re-confirms the T10 state code and performs `gov update --apply`, `gov kernel reinstall` and
rollback — production C3 operations — selecting R8, which the whole fleet elsewhere treats as revoked. No surface says
`current`; the operation simply proceeds.

**Why this contradicts the pack and the owner.**
- The pack's own residual **RS-1b** (`24` §10) states: "A C3 decision whose proof is a recent anchoring event (P1) can be
  **stale by up to 24 hours**." The executed staleness is **882 hours** (bounded only by the 90-day anchor validity, not 24
  hours). RS-1b's stated bound is **false** for the offline/air-gapped case, which is exactly the OT-1 case.
- **OWNER-DESIGN-REQUIREMENTS-0002 OT-1** (binding): "For production admission/install/update: the required **trust-state
  anchor must satisfy the existing 24-hour freshness requirement**; offline media receives no special longer freshness
  window; **stale trust state on otherwise authentic media cannot become current merely because the medium is trusted** ...
  it must NOT ... enter C1-C3 based on stale state." The design lets a stale (up-to-90-day) media state drive production C3.

**Why HIGH (blocking).** An ordinary operation on a supported (air-gapped / long-offline) machine produces a production
trust ingress on a superseded Trust State that omits a known revocation — a silent, persistent loss of the currency control,
for up to the anchor validity (90 days workstation, 7 days CI). It is the recurring rejection class (a lower-trust/stale
input yielding a current, higher-trust fact) surfacing at **use-time on a running admitted machine** in the media path the
owner just constrained. It is a direct deviation from a binding owner resolution and a false stated bound (RS-1b).

**Not CRITICAL.** It needs a real revocation published after the machine's anchored state, an anchor still within validity,
and a machine that does not receive the newer state; the machine never shows `current`, and once it ingests the newer state
the proof stops naming the effective state and C3 refuses.

**Correction direction (architectural).** Bind the **state's** age, not only the event's: a C3 currency proof requires the
effective Trust State's own `issued_at` to be ≤ 24 h (equivalently, R-CUR-1/R-CUR-2 must name a state issued within the
production-currency ceiling), so a machine without fresh state stays at the bounded diagnostic/bootstrap level (the owner's
OT-1c outcome). Restate RS-1b, RS-1/RS-1c and `24` §4.3–§4.4 accordingly; if the owner intends anchored machines to keep C1–C2
on an old-but-anchored chain (the RS-1 core), state that exception explicitly and separately from production C3, and confirm
it against OT-1's "must NOT enter C1-C3 based on stale state." Whether C1–C2 on an anchored-but-stale chain is permitted is a
**genuinely new owner trade-off** raised by OT-1; the C3 production path is an **engineering correction** to R-ANC-4/R-CUR-1.

---

## RV7-C-M1 — MEDIUM (carried) — first admission after protected-store loss discards the surviving account-store high-water

**Statement (M, D).** Two stores exist (`24` §8, `31` R-STORE-1): the **protected admission store**
(`/var/lib/gov/admission/<lineage>/`, root-owned; holds `admission-store.json`, records, `floors.json` with the high-water)
and the **account verifier trust store** (`<home>/.local/state/gov/trust/<lineage>/`; holds `high-water.json`, anchors,
per-project records, confirmations). `31` R-STORE-2 and R-ADM-8″: "the first-admission determination, the move-aside and the
honoured admission records read **only** the protected admission store"; first admission is the case where the protected
store has no `admission-store.json` marker, and it **moves the account store aside** (never read again, AD-2′).

If the **protected** store is lost but the **account** store survives — an ordinary partial restore, an OS reinstall that
keeps `$HOME` but not `/var/lib`, a home-directory migration — the next `gov-admit` finds no protected marker → **first
admission** → it moves the account store aside without reading its `high-water.json`. The retained high-water (state
sequence, root version, security minimum, negatives, accepted-TBM), the per-project records (E10 sequences, strength
vectors) and pending `registration_change`/`policy_lowering` obligations are silently discarded. `read_floors` then finds no
floor source (both stores empty/moved), so floors reset from the new admission's state.

**Executed evidence (M)** `adm7x.json` `X2_protected_store_lost_account_store_restored`: the account store held anchors, a
per-project record `P1` with a pending `registration_change` and an open transaction, and `high-water.json`;
`is_first_admission` **true**; `moved_aside_to` `<lineage>.pre-admission-0`; `account_store_after` **null**;
`per_project_record_with_pending_registration_change_and_open_tx_still_read` **false**. `X1_multi_account` and
`X3_shared_home_two_machines` show the related under-specification that `31`/`24` §8 name **no** account (the invoking user,
`SUDO_USER`, every account, a CI job account): a first admission triggered by one account moves aside one account's store
and leaves another account's pre-existing state untouched.

**Failure scenario.** A workstation's high-water reached sequence 11 (revocations, a raised security minimum). `/var/lib` is
lost and rebuilt from a fresh image while `$HOME` is restored from backup. The first `gov-admit` on the rebuilt machine is a
first admission; it discards the account store's high-water. A binary or state that was below the previous high-water — a
lower-TBM binary, or a state the machine previously refused — is now admissible within the FC-9 window. The
never-backwards invariant (`24` §8, OP-7/OP-14(b), and OWNER-DESIGN-REQUIREMENTS-0002 OT-1 "the machine's previously known
trust high-water can never be lowered") is silently violated.

**Why MEDIUM.** It needs the specific ops condition (protected store lost, account store kept) and a subsequent re-admission
with genuinely lower-but-within-24h material to be exploitable; the account store's floors are "restrictors only", so absent
the move-aside they would refuse. It is carriable, but the fix touches R-STORE-2 (which store the first-admission move-aside
consults).

**Escalation.** If the synthesis regards protected-store loss with a surviving home as an **ordinary** operation, this is a
persistent silent high-water regression and rises to HIGH.

**Correction direction (carried).** State which account(s) a first admission moves aside; require the first-admission
move-aside to **read and preserve** any surviving account-store high-water and per-project records into the new protected
store (or to fail closed) so the high-water never moves backwards even when the protected store is rebuilt; distinguish
"protected marker absent because this is genuinely the first admission" from "protected store lost while a higher account
high-water survives." (`04` CR7-C-1.)

---

## RV7-C-M2 — MEDIUM (carried) — no realizable per-project record identity satisfies the `20` §9 / RT-196 cases

**Statement (E, D).** `20` §9 (CR6-C-8) keys the per-project record by `project_trust_id` **and** "a locally recorded
repository identity (the **Git common-directory identity** recorded by the first install on this machine, never committed)."
RT-196 requires: worktree, moved checkout and container bind-mount **keep** E10 and the strength report ("same identity");
a second clone, a fork and a template copy are **reported** (`PROJECT_IDENTITY_MISMATCH`) and never overwrite the original
("different identity"). PPR7 (the architect's closure evidence) models the identity as **opaque labels** (`"git-A"`,
`"git-B"`) and never tests what the identity can be.

**Executed evidence (E)** `ident7.json` (real Git 2.43.0) enumerates every concrete identity a conforming implementation
could record and compares "same as the original" with the `20` §9 requirement. **Every** candidate contradicts the text in at
least one named case (`every_candidate_contradicts_the_text` **true**):
- **realpath of the common dir (I1):** a moved checkout (same- or cross-filesystem) → different → the text says "same" →
  `PROJECT_IDENTITY_MISMATCH`, fail-closed loss of E10/strength (the RV6-M4 harm reshaped). A **different** repository
  re-cloned at the **same path** → I1 unchanged → the text says "different" → the two share one record (cross-contamination).
- **(st_dev, st_ino) of the common dir (I2):** a cross-filesystem moved checkout → different → fail-closed loss.
- **a recorded random id in `.git/` (I3):** survives a directory copy / tar copy of the whole checkout including `.git`
  (an ordinary "template repository" / "download ZIP" / backup-restore) → the text says "different" (template copy) → the
  copy **inherits the original's identity** and shares its record.
- **root commit id (I4):** a fork and a second clone share the root commit → the text says "different" → cross-contamination.

The best candidate (I3) is correct for worktree, moved checkout, second clone and template-reinit, but still wrong for a raw
`cp -r`/`tar` copy of a checkout that includes `.git`.

**Failure scenario.** *Fail-closed side:* a developer moves a checkout, adds a worktree on a different mount, or bind-mounts
it in a container; under I1/I2 the record is not found → `PROJECT_IDENTITY_MISMATCH` → E10 downgrade detection and the
strength report are lost at the new location (LR-4/RR-2′ availability; the RV6-M4 (2) "reported on every machine" overclaim
resurfaces). *Cross-contamination side:* under I3/I4 a template-repository copy or a backup restored elsewhere shares the
original's record, so project B's install re-records the vector project A relies on.

**Why MEDIUM.** Both sides are bounded: the fail-closed side is availability (a new location behaves as a fresh clone,
LR-4, an accepted residual); the cross-contamination side needs a repository writer (A2) — a request, not a trust escalation
(the RV6-M4 argument). But the class is **narrowed, not closed** as `22` claims, because no implementation of the named
identity satisfies all five cases, and PPR7 does not exercise the identity's realization.

**Correction direction (carried).** Define the recorded identity concretely and cover the copy case: a recorded local id
plus a check that the identity was not copied in with `.git` (for example, bind the id to the common-dir inode/creation and
to the first-install transaction id, and treat a mismatch between a copied id and the local common dir as a new project);
state the exact behaviour for each of {worktree, moved same-fs, moved cross-fs, bind mount, second clone, fork, `cp -r`,
`tar`, `--shared`, reinit}; extend PPR7/RT-196 to run over real Git relocations rather than opaque labels. (`04` CR7-C-2.)

---

## RV7-C-M3 — MEDIUM (carried) — the journal-honouring condition is unreachable for a first install

**Statement (E, D).** `18` §5.1: "A journal is honoured **only if** (a) the **per-project record** lists `<TX>` as an open
transaction for this `project_trust_id`, repository path and locally recorded repository identity, and (b) the journal path
is not tracked." `18` §4's flow updates the per-project record only at the **end** ("VTS per-project record updated; TX
deregistered" is the last line), while a separate "VTS open-transaction registry: TX registered" appears early. On a **first**
install of a legacy project there is **no** per-project record until the transaction's last step; so during the whole
migration the per-project record cannot list the open TX, and by `18` §5.1 the journal is **not honoured** →
`FOREIGN_TRANSACTION_ARTEFACT` → `gov recover` ignores it.

**Executed evidence (E)** `txn7.json` `first_install_honouring`: with the record created early (`record_created_at_prepared`)
the journal is honoured (`IN_TRANSACTION`, recoverable); with the record written at the end as `18` §4 orders
(`record_written_at_end_as_18_s4_orders`) the journal is **not honoured** (`foreign` lists the journal, state
`LAYOUT_MIGRATION_INCOMPLETE`, recovery `not_honoured`). The architect's `crashmig7` assumes the journal is honoured
(`vts_open=(TX,)`) for a first install; that assumption depends on this ambiguity being resolved in favour of an early
registry entry that `18` §5.1 does not name.

**Failure scenario.** A crash during the very first `gov update --apply` on a legacy project. `gov recover` reads `18` §5.1,
finds no per-project record listing the TX, declares the journal foreign, and refuses to recover it. The half-migrated tree
is left to a Git restore — the outcome CR6-C-7/RV6-M3 was added to avoid.

**Why MEDIUM.** Fail-closed (RoT-1 never treats the half-migrated tree as `COMPLETE`); the intended honouring gate (the early
open-transaction registry) is stated in `18` §4, so a conforming implementation is testable. But the two texts contradict
each other for the first-install case.

**Correction direction (carried).** State that honouring reads the **open-transaction registry** (written at `prepared`,
before any layout step), not the per-project record; for a first install the registry entry and its repository identity are
created before the first `layout-*` phase; align `18` §5.1 with `18` §4 and `20` §5; RT-16/RT-195 inject a crash before the
record exists and assert `gov recover` still honours the journal. (`04` CR7-C-3.)

---

## RV7-C-M4 — MEDIUM (carried) — an ordinary `git clean -fdx` in the first-install crash window defeats R-INIT-9

**Statement (E).** During the first-install transaction the overlay is moved from the tracked `governance/project` to the
**untracked** `governance/overlay` (the user commits the new layout only after the transaction completes). R-INIT-9
(`09`/`26`) refuses/gates `init` only when `governance/overlay` or `governance/views` **exists**. An ordinary
`git clean -fdx` in the crash window removes the untracked in-migration overlay (and the untracked transaction area and
legacy quarantine); the tree then presents as `ABSENT`, R-INIT-9's guard no longer fires, and a subsequent `gov init`
produces a `COMPLETE` install with the project's restricted classifications silently absent.

**Executed evidence (E)** `txn7.json` `summary.post_recovery_ABSENT_any_reading_L`/`_S` list the prefixes that reach
`ABSENT` after `GIT_CLEAN_FDX` (e.g. `06:move-views:post:GIT_CLEAN_FDX`, `07:...:post`, `08:layout-occupation:mid`), with
`classifications_after_recovery` empty and `rinit9_refuses` **false**. `summary.journal_not_honoured_after_intervening`
shows `GIT_CLEAN_FDX` also removes the journal, so `gov recover` cannot roll back either.

**Failure scenario.** A crash during the first install; the operator runs `git clean -fdx` (a habitual "reset my tree"
command) before `gov recover`; the untracked in-migration overlay is deleted; `gov init` then creates a fresh install whose
classifications are the defaults — the project's `restricted` classes are gone with nothing to report. Recovery from Git
(the tracked pre-migration commit) is still possible, so the loss is not permanent, but a `gov init` produces a valid-looking
install without them.

**Why MEDIUM.** It needs a crash in the first-install window plus `git clean -fdx` plus a `gov init` (rather than a Git
restore); the classifications remain in Git history. But R-INIT-9 (revision 7's fix for RV6-M3) is defeated by removing the
overlay it keys on.

**Correction direction (carried).** During the first-install transaction, keep the moved overlay tracked (or force-add it,
as the migration occupation is), so `git clean` cannot remove it; and make `init` refuse on a tree that carries an
interrupted-first-install marker/journal (not only a present `governance/overlay`), evaluating `19` §9 item 5 before commit.
(`04` CR7-C-4; extends CR6-C-7.)

---

## RV7-C-M5 — MEDIUM (carried) — recovery roll-forward after a post-exchange crash is unproven and depends on the in-memory ARO

**Statement (E, D).** `26` §7 / `20` §5 (CR6-C-7): after the exchange in a first install, recovery "rolls the layout forward
only when every redo record is complete and the exchange happened" — running the remaining steps, i.e. "migrations from ARO
buffers" (`18` §4). But the ARO is "`{...}`, **in memory only**" (`18` §1). After a crash the ARO is gone, so the remaining
overlay migrations, strength vector, per-project record and ledger cannot be reconstructed from it. The architect's
`crashmig7` roll-forward branch is a **stub**: it returns `{"action": "roll_forward", ..., "state_after_roll_forward":
"COMPLETE (modelled)"}` and performs no file operation.

**Executed evidence (E)** `txn7.json` `rollforward_model.mutates_tree` **false** (the quoted `crashmig7` branch never renames,
opens, unlinks or makes a directory); `rows["11:RENAME_EXCHANGE:post:NONE"]` → `recovery_L = roll_forward_required`,
`state_after_recovery_L = IN_TRANSACTION` (the model cannot actually complete it). `22` §1 claims "A-11 and B-11 roll forward
to `COMPLETE`"; that claim is asserted, not achieved.

**Failure scenario.** A crash between `RENAME_EXCHANGE` and the `verified` phase of a first install. `gov recover` must roll
forward, but the migrations it needs are only in the crashed process's memory. Without a rule to **re-authenticate the source**
(rebuild the ARO) or to journal the post-exchange overlay migration with redo records the way the layout steps are, recovery
cannot complete, and the machine is left `IN_TRANSACTION` needing manual intervention.

**Why MEDIUM.** Fail-closed (the machine stays `IN_TRANSACTION`, refuses mutation, never `COMPLETE` without the steps). The
design intent (roll back to legacy, or forward to complete) is sound; only the roll-forward's feasibility after a crash is
unspecified and the evidence stubs it.

**Correction direction (carried).** State that roll-forward re-authenticates the source to reconstruct the ARO before
replaying the post-exchange migrations, or journal the post-exchange overlay migration / strength vector with idempotent redo
records (not from the in-memory ARO); execute the roll-forward in the crash evidence rather than asserting `COMPLETE
(modelled)`. (`04` CR7-C-5.)

---

## LOW

### RV7-C-L1 — recovery undo aborts or silently replaces after an intervening ordinary operation

`txn7.json`: between a first-install crash and `gov recover`, an ordinary Git/legacy operation changes the tree; the
rename-based undo then either `aborted_ENOTEMPTY` (59/176 cases under reading L: an undo destination directory is
non-empty) or `replaced_existing_file` (21 cases: e.g. `git stash -u` restored a real `governance/project`, and the undo
`mv governance/overlay governance/project` replaces it). Both are **fail closed** (the tree is never `COMPLETE`; RoT-1
refuses; legacy binaries see `LEGACY`/`NOT_INSTALLED`). The two literal recovery readings (L rename-and-skip, S
refuse-on-precondition) diverge (`recovery_actions_L` vs `_S`), so `20` §5's undo must state its precondition handling. (`04`
CR7-C-6.)

### RV7-C-L2 — the clock high-water can be poisoned by the machine's own wrong-ahead clock

`adm7x.json` `X4_clock_high_water_from_ordinary_clock_error`: an anchoring event recorded while the RTC is 10 h ahead raises
`clock_high_water` past real time; after the clock is corrected the machine runs `TRUST_CLOCK_BELOW_HIGH_WATER` (C0-R) until
real time passes the recorded value, and the only reset is a **root-signed** `bootstrap.clock_reset`. `24` §4.5 discusses a
future *statement* poisoning the clock (refused at ingest) but not a future *anchoring-event time* raising the high-water.
Fail-closed availability (never grants trust). Bound: `clock_high_water` should not be raised past the local clock by an
anchoring event, and the reset path for an honest wrong-clock incident should not require a root ceremony. (`04` CR7-C-7.)

### RV7-C-L3 — `floors.json` / `high-water.json` atomicity is unstated

`adm7x.json` `X5_floors_write_vs_read`: 3 reader threads and 1 writer over 4 s produced ~1,994 `JSONDecodeError` torn reads
of `floors.json` (0 below-floor reads). `31` R-ADM-7″ makes the **record** write atomic (`os.replace`) but states no
atomicity for `floors.json` or the account store's `high-water.json`. An implementation must write both atomically and
readers must tolerate a concurrent write. Fail-safe (a decode error, not a wrong value). (`04` CR7-C-8.)

### RV7-C-L4 — OT-2 target label and non-circular criterion (mostly reviewer-B scope)

`design7.json`: the pack labels both initial targets `NOT CERTIFIED — pending criteria`
(`NOT_CERTIFIED_PENDING_CRITERIA`), not OWNER-DESIGN-REQUIREMENTS-0002's exact `NOT CERTIFIED — TOOLCHAIN ASSURANCE
INCOMPLETE`, and CC-3's non-circular trusting-trust criterion ("at least one toolchain lineage not rooted in an upstream
binary compiler archive; bit-identical") is not yet expressed as an explicit, executable/testable acceptance procedure. The
compatibility surface conforms (no target is certified; first contact refuses an uncertified target,
`struct7`/matrix `TARGET_NOT_CERTIFIED` shape). Adopt the owner's exact label and make the criterion executable. The
trusting-trust evidence route is reviewer B's scope. (`04` CR7-C-9.)
