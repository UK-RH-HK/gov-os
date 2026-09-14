# 01 — Findings

Severity per HO-0003 §4. No CRITICAL or HIGH finding. One MEDIUM, carried (non-blocking) because it can be carried as
a bound, testable implementation/specification requirement without a change to the trust model, and because the RoT-1
trust state is never mutated and a RoT-1 binary never treats the result as valid.

Evidence classes: **E** executed with the real 4.1.2–4.1.5 binaries; **D** design reading of the pack.

---

## C-1 — MEDIUM (carried) — The legacy-path-occupation defence is not robust to removal of the occupation entries; once removed while `governance/trust/` persists, a real pre-RoT `init --force` fully installs a verified legacy kernel that serves restricted material, and residual LR-2 understates this

**Statement.**
The R2-H4 defence (`26`) is structural: every path a pre-RoT binary would write is occupied by an entry of the wrong
type, so the binary fails before its first write. This holds **only while the occupation entries are present with their
exact types** — which `18` §9 makes the `COMPLETE` precondition and which the executed property `P3r3`/RV3-C-A01 only
ever exercises in the present state.

When the occupation entries are **absent** (not retyped) while `governance/trust/` is still present, containment is
lost:
- **RV3-C-A05 (E):** an ordinary user `git rm -r`s the occupation entries (they are inscrutable, extension-less files
  and one directory, each holding a single line `…this-binary-cannot-operate-this-project`; deleting "these strange
  leftover files" is a foreseeable cleanup). A teammate then runs the documented remedy `gov init --force` on the real
  4.1.5 binary: it **succeeds** (`ok:true`), `is_installed` becomes true, `gov kernel trust` reports `verified:true`,
  and the legacy binary **indexes and retrieves `product/restricted-plan.md`** — the exact R2-H4 harm (silent
  exposure of a project-owned restricted classification). `governance/trust/**` is **not** mutated
  (`governance_trust_mutated:false`), and a RoT-1 binary would see `PARTIAL(occupation)` and fail closed.
- **RV3-C-A06 (E):** a non-cone sparse checkout (or partial materialization) that omits the occupation files reaches
  the same class — `init --force` stages a full legacy kernel into the vacated `governance/kernel/`.
- **RV3-C-A04 (E):** removing only the three sentinel *files* (leaving the `framework.lock` **directory**) bounds the
  damage: `init --force` fails `IO_ERROR` at the lock and the legacy binary is left non-functional. The `framework.lock`
  directory is the load-bearing occupation entry; removing it is what unlocks the full harm in A05.

**Why it does not reach HIGH.** In every case `governance/trust/**` is outside every legacy binary's write vocabulary
(they address only `governance/{kernel,project,generated,framework.lock}`, `spec/audits/GOVERNANCE-ADOPTION`,
`.governance-runtime`), so the *new* kernel/trust state is never mutated, and the RoT-1 installation-state machine
(`18` §9) reports `PARTIAL(occupation)` (D033 CRITICAL) and refuses — a RoT-1 binary never treats the result as valid.
The precondition is a deliberate, multi-entry deletion or a non-cone subset materialization, not a routine operation
(fresh clone, `git archive`, `git clean -fdx`, checkout-across-migration, and a divergent dir/file merge all keep the
occupation and keep the legacy binary contained — RV3-C-A02, A03, A09).

**Why it is nonetheless a finding.** The pack's residual **LR-2** (`26` §8) states the bound as: *"A same-user process
(A3) removes occupation entries → RoT-1 reports `PARTIAL(occupation)`; the result is not a RoT-1 layout; A3-class."*
That reads as benign. It omits that the same removal, followed by an ordinary legacy remedy, yields a **verified legacy
install that serves restricted material** while the RoT-1 trust directory sits intact beside it — i.e. the full R2-H4
harm is reachable, not merely "not a RoT-1 layout". Under the review-r2 residual-acceptance test (bound must be stated
correctly), the residual as written is not acceptable. The acceptance plan also never exercises occupation-absent
states: `RT-50` (LP-1) and `RT-81` (occupation removed, then a legacy run) assert the legacy run is "recorded as
expected behaviour on a non-RoT-1 state" but do **not** assert the harm — restricted exposure — nor that a legacy
`init --force` can complete a verified install over the vacated paths.

**Correction direction (architectural / specification, carriable).**
1. Correct `26` §8 LR-2 to state the full reachable outcome: occupation removal + a legacy install-over yields a
   verified legacy install serving project-owned restricted material while `governance/trust/` persists; the bound that
   actually holds is only that `governance/trust/**` is never mutated and RoT-1 fails closed.
2. Strengthen `12` RT-81 to a harm assertion: after occupation removal, a real legacy `init --force`/`adopt` that
   completes a verified install and exposes the restricted classification is the documented, expected loss of
   containment; RoT-1 must report `D037 PROJECT_STRENGTH_WEAKENED` / `PARTIAL(occupation)` and refuse; and add an
   occupation-absent variant to RT-50.
3. Consider making the occupation entries self-describing/harder to delete accidentally (e.g. a documented, doctor-named
   protected set, so `gov doctor` on any surviving RoT-1 sibling flags a sibling occupation removal), acknowledging that
   no RoT-1 mechanism can stop a *legacy* binary from installing over a path the RoT-1 layout no longer occupies.

**Acceptance.** RV3-C-A04, A05, A06 (`evidence/occ_removal.json`, `evidence/full_removal_and_merge.json`,
`evidence/durability.json`).
