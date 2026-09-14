# 00 — Independent compatibility & transaction review (C) of RoT-1 revision 3

| | |
|---|---|
| Run | AR-0003, role `rot-reviewer-compat-transaction` |
| Reviewed | RoT-1 revision 3, commit `ca77a431418bd6b349f465aa2521ca43bccfd5a6` (`release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`) |
| Handoff | HO-0003 |
| Independence | This session authored no RoT-1 revision, no prior review, and did not read reviewer B's output, other branches or other worktrees. The architect's response matrix (`22`) and evidence (P1r3/P3r3/P4r3/G1/CSI) were treated as claims to test. |
| **Verdict** | **NO_BLOCKING_FINDINGS** |

## Scope
Compatibility and transactions (Phase 1 protocol §5 C, HO-0003 §2–§4): the real 4.1.2–4.1.5 binaries over their
command registers; the revision-3 legacy-path-occupation layout and its durability through clone/checkout/pull/stash/
clean/sparse/archive/merge/revert and Windows/case-insensitive semantics; rollback, recovery, snapshots, partial
installs, TOCTOU, concurrency, cross-machine, symlink/hard-link/rename tricks, corrupted/foreign journals, crash
recovery, long-lived processes. Because the RoT-1 install/transaction machinery is architecture-only (unimplemented),
the transaction state machine was reviewed as a design (`18`, `20`, `26`, `27`) and the legacy-binary boundary was
attacked with the real binaries.

## Method
- Built a real 4.1.5 base project and the revision-3 occupation layout, committed on legacy history (`build_base.py`).
- Ran 84 destructive invocations of all four real binaries on the intact layout with whole-tree (type-aware) digests
  (`run_destructive.py`) — independent reproduction of the LP-1 property.
- Attacked layout durability: fresh clone, `git archive`, `git clean -fdx`, checkout across the migration commit,
  non-cone sparse checkout, `git revert`, divergent dir/file merge, case-collision enumeration
  (`durability.py`), and occupation removal + legacy install-over (`occ_removal.py`, `full_removal_and_merge.py`).
- Judged every declared compatibility/transaction residual (`03`).

## Summary of results
- **LP-1 (R2-H4 core) holds and is independently reproduced.** 84 destructive invocations, 4 real binaries, intact
  layout: 0 writes to the tree, to `governance/trust/`, or to Git; classification intact. `governance/trust/**` is
  structurally outside every legacy binary's write vocabulary, so the *new* trust state cannot be mutated by a pre-RoT
  binary. Durability holds through fresh clone, tarball, `git clean -fdx`, checkout-across-migration (types restored),
  and a divergent dir/file merge (Git resolves to the RoT-1 types; the legacy binary stays contained). `git revert` of
  the migration commit is a clean full downgrade to a legacy project with no RoT-1 state (LR-1).
- **One residual gap (C-1, MEDIUM, carried, non-blocking).** The occupation defence is not robust to *removal* of the
  occupation entries. After an ordinary user deletes the inscrutable extension-less sentinel entries (or a non-cone
  sparse checkout omits them) while `governance/trust/` persists, a real legacy `gov init --force` completes a
  `verified:true` legacy install that indexes and retrieves the project's restricted material — the full R2-H4 harm —
  while `governance/trust/**` is never mutated and a RoT-1 binary fails closed (`PARTIAL(occupation)`). The pack's
  residual LR-2 states this bound too weakly and the acceptance plan never exercises occupation-absent states. This is
  carriable as a specification/wording + test correction with no change to the trust model, so it is not blocking.
- **Carried engineering constraints C-2…C-5** (cross-device/overlayfs transaction area, stray dir/file-merge and
  partial-removal artefacts, type-by-`st_mode` not name, full-register RT-50 with type-aware digests) — `04`.

## Prior-finding status (HO-0003 §3)

| Prior finding | Status | Basis |
|---|---|---|
| R2-H4 pre-RoT binaries damage RoT-1 projects | **NARROWED** | Executed LP-1 no-write property independently reproduced on the intact layout (`05`, `destructive.json`); `governance/trust/**` never in any legacy write set. Residual durability gap C-1 remains but does not reopen the class for the new trust state (never mutated; RoT-1 fails closed). |
| R2-M7 long-lived snapshot never re-checked | **CLOSED (design), OPEN (executable)** | `18` VU-11 generation discipline + bounded snapshot age; spec-only (RT-86), not testable pre-implementation. |
| R2-M8 agent-facing content consumed from disk | **CLOSED (design)** | `18` §12 pointers + VTS rendering record + D036; spec-only (RT-88). |
| R2-M9 exchange drops statements; `.tx` in Git; `overlay.prev` unguarded | **CLOSED (design)** | Union trust record (`18` §5.2); transaction area moved to untracked `.governance-runtime/trust-tx/`, journals honoured only if VTS-registered (committed/copied journals → `FOREIGN_TRANSACTION_ARTEFACT`); `overlay.prev` restore behind the `weakening` gate (`20` §5). I confirmed `.governance-runtime/` is gitignored and only the tracked occupation `.governance-runtime/migration` travels in Git. |
| R2-L2 hard links / `st_nlink` | **CLOSED (design)** | VU-12 `st_nlink==1` before exchange and at use; spec-only (RT-87). |
| R2-L3 F1 evidence hygiene | **CLOSED** | P3r3 uses the exact FORMAT JSON, lock location and full layout with a fresh copy per command; independently corroborated by `run_destructive.py`. |
| R2-M1 (transaction part): gate/decision records authorising downgrade/rollback | **CLOSED (design)** | Trust gates answered only by local VTS confirmations bound to kind/project/digests, consumed once; `gov decide` refuses trust gates; repository records are requests (`27`); spec-only (RT-89/90). |
| R2-M10 (transaction part): acceptance plan cannot detect the findings | **CLOSED (design) with a gap** | RV2-A24/A25/A26/A31…A36 mapped to RT-50/RT-83…85/RT-99 with property assertions and OS tracing. Gap: RT-50/RT-81 do not exercise occupation-absent + legacy install-over (C-1, C-5). |

## Verdict
**NO_BLOCKING_FINDINGS.** No CRITICAL/HIGH finding: no pre-RoT binary mutates `governance/trust/**`, and no ordinary or
legacy operation produces a state a **RoT-1** binary treats as valid — RoT-1 fails closed in every occupation-broken
case. C-1 is a MEDIUM residual that is carriable as a bound, testable specification/test correction (with C-2…C-5) and
does not require a trust-model change. This is a role verdict, not the architecture verdict; the synthesis reviewer
issues that.
