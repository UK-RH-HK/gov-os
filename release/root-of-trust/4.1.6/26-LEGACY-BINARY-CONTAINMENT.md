# Output 26 — Legacy-binary damage containment and project-owned strength

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 3 added this file. Review r3 recorded R2-H4 **CLOSED as a class**, with HO-0001 §3.4 SATISFIED. Revision 4
> keeps the layout and property LP-1 unchanged: P3r3 was re-run unchanged, with results equal to the committed ones.
> Revision 4 changes three things:
> - residual LR-2 is restated with its reachable outcome (RV3-M6, C-1);
> - the migration occupation survives the "untrack ignored files" idiom (RV3-L7);
> - project-owned strength is evaluated over the effective policy (BC-1 root; rule 20).
>
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Revision 2.** It relied on sentinels that old binaries read only after acting. The mistaken equivalence was *sentinel
read afterwards ⇒ boundary*.

**Requirement (unchanged).** A pre-RoT binary MUST NOT be able to silently mutate a RoT-1 project into a state it then
treats as valid. The defence MUST NOT depend on the old binary understanding RoT-1. The mechanism is structural: every
path the old binary would use is occupied by an entry of the wrong type, or is outside its vocabulary.

**What review r3 confirmed, and what it bounded.**
- **Confirmed.** On the intact layout no pre-RoT byte is written: P3r3 with 695 invocations and 40 chains, and reviewer C
  with 84 destructive invocations.
- **Bounded (RV3-M6).** Once the occupation entries are removed, or pre-migration paths are restored with an ordinary Git
  command, a legacy binary operates a legacy layout it treats as valid. It can then write `governance/trust/**` and the
  overlay. No design stops Git restoring pre-migration history. Revision 4 states that outcome exactly (§8 LR-2) and tests
  it (`12` RT-81, RT-50b).

## 2. Layout `rot-1/legacy-path-occupation-v1`

```text
governance/
├── trust/                         RoT-1 root — Protected Path Set; unknown to every pre-RoT binary
│   ├── FORMAT                     {"layout":"legacy-path-occupation-v1","minimum_reader":"4.1.6","trust_format":"rot-1"}
│   ├── framework.lock             lock 3.0.0 (08 §3)
│   ├── kernel/**                  installed kernel (no KERNEL_MANIFEST.json)
│   ├── release.dsse.json · lineage/ · state/ · root/ · profiles/
├── overlay/                       project overlay (relocated from governance/project); GovernedFs; Overlay Surface (23 §11)
├── views/                         generated views (relocated from governance/generated); GovernedFs
├── kernel                         OCCUPIED: regular file (sentinel text)
├── project                        OCCUPIED: regular file
├── generated                      OCCUPIED: regular file
└── framework.lock/                OCCUPIED: directory containing ROT-1-TRUST-FORMAT (sentinel)
spec/audits/GOVERNANCE-ADOPTION    OCCUPIED: regular file (RoT-1 adoption evidence lives at spec/audits/ADOPTION/)
.governance-runtime/migration      OCCUPIED: regular file, tracked in Git
.gitignore                         /.governance-runtime/*   and   !/.governance-runtime/migration   (revision 4, RV3-L7)
```

- **Sentinel text:** `ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project`.
- **Protection.** The occupation entries are part of the Protected Path Set, and only the install transaction writes
  them. Their type is checked by `st_mode` or `GetFileInformationByHandle`, never by name (C-4).
- **Ignore rule (RV3-L7).**
  - **Revision 3.** The whole of `.governance-runtime/` was ignored, and the occupation force-added. `git ls-files -ci
    --exclude-standard` listed the occupation, so the common "untrack ignored files" idiom removed it from later clones.
  - **Revision 4.** The installer writes `/.governance-runtime/*` and `!/.governance-runtime/migration` instead. The idiom
    lists nothing and a fresh clone keeps the occupation. Doctor names an absent or retyped occupation entry (D033).
  - **Evidence.** `evidence/RV3-D-A05-A07-rerun-r4-layout.json` (the synthesis reviewer's probe, run on the layout with
    this delta: `tracked_but_ignored_listed: []`, occupation in the fresh clone: `file`) and
    `evidence/LR2-installation-state-and-strength-reference.json` (fresh clone after the idiom: `COMPLETE`).
- **Partial state.** A missing or retyped occupation entry makes the RoT-1 installation state `PARTIAL(occupation)`
  (`18` §9), doctor D033 CRITICAL. Doctor also names stray legacy artefacts left by merges or partial removal (C-3).

## 3. Why every pre-RoT command fails before its first write (class argument)

Unchanged from revision 3. Commands that need an installation return `NOT_INSTALLED`, because
`governance/kernel/KERNEL_MANIFEST.json` cannot exist when `governance/kernel` is a file. Commands that run without an
installation meet a wrong-typed entry at their write or restore root.

### 3.1 Legacy runtime residue

Unchanged. `.governance-runtime/update/<v>/` is blocked by set (i) and quarantined by the first RoT-1 transaction.
`.governance-runtime/migration/batch-N/` is occupied by the tracked file, which now also survives untracking (§2).

## 4. Executed property (LP-1)

**Property LP-1** (unchanged). For every pre-RoT binary 4.1.2–4.1.5, and every invocation derived from its own register,
on a RoT-1 project carrying a legacy update snapshot and a project restricted classification:
- no byte outside `.git/` and `.governance-runtime/` changes;
- Git state is unchanged;
- the classification survives.

| Evidence | Result |
|---|---|
| `evidence/P3r3-pre-rot-register-matrix.{py,json}` (revision 3, unchanged) | 695 invocations, 40 chains, 0 changes; control L0 36/42/46/47; ablation L3A 4 per binary |
| **`evidence/P3r3-rerun-r4-summary.json`** (re-run unchanged by AR-0005, real 4.1.2–4.1.5; binary SHA-256 recorded) | `summary`, `property_L3`, `chain_summary` and `job_count` **equal** to the committed output |
| `evidence/rerun-RV3-C-destructive.json` (reviewer C's 84 destructive invocations, re-run) | 0 tree, trust or Git writes |
| `evidence/rerun-RV3-C-durability.json`, `rerun-RV3-C-occ_removal.json`, `rerun-RV3-C-full_removal_and_merge.json` | as review r3 |

## 5. Protected paths (HO-0001 §3.4 list)

Unchanged from revision 3: kernel, legacy lock, trust, rollback, reinstall, init-force and migration paths.

## 6. Project-owned strength (rule 20; revision 4)

**Revision 3.** It recorded overlay categories and compared overlay bytes. A kernel-side or Trust Policy change removed
project strengthening while the overlay was unchanged, and the detector was blind (RV3-H1).

**Revision 4.** It records strength as **requirements over the effective inputs**.

1. **Vector.** Every install transaction and every gated overlay change records, in the VTS per-project record:
   - **constitutional strength:** for every key where the project layer contributes an admitted strengthening over the
     root kernel's effective value, a requirement on the **effective** value in the key's registered direction. Examples:
     `AUTHORITY_POLICY.authority_levels_required.resume_control ≥ L5`, `SECURITY_POLICY.never_index_classes ⊇
     [confidential]`, `HUMAN_GATE_POLICY.agent_resolvable_when.max_radius ≤ R0`;
   - **overlay strength:** a requirement for every overlay input with an Overlay Surface direction (`23` §11.2);
   - **default deny:** every unclassified overlay file by digest; every plugin descriptor set;
   - **owner constitutional files:** confirmed slot digests (`23` §7.2);
   - **held registration:** the TPS registration the vector was recorded under.
2. **Check.** At every unit of work, the recorded requirements are evaluated over the current effective policy and
   overlay, **whatever changed them**:
   - a kernel, a Trust Policy or a precedence registration;
   - a migration, a recovery or a remedy;
   - an overlay edit, a Git restore, or a legacy binary.

   A failing requirement not accepted through a gated transaction is `PROJECT_STRENGTH_WEAKENED`. Security-relevant C2
   operations are refused until the `project_strength` trust gate (`27`) accepts the new vector. Those operations are
   indexing, export, upstream, retrieval of affected classes and plugin execution.
3. **Remedies do not hide it.** `kernel reinstall`, update and recover restore the PPS and occupation entries, but never
   the check. Only the gate re-records the vector.
4. **Bound (LR-4).** A machine with no record (a fresh clone) accepts the repository's overlay as the project's current T4
   configuration.

Evidence:
- `evidence/P1r4-project-strength-and-absence.json` part C: the vector reports the loss of every revision-3 effective kernel and stays quiet for every
  revision-4 one. Migration weakenings are reported (`19` §9).
- `evidence/LR2-installation-state-and-strength-reference.json`: on real trees after the synthesis reviewer's legacy
  probes:
  - the checkout-and-legacy-CIT tree (RV3-D-A05a/A06) reports `PROJECT_STRENGTH_WEAKENED` (3 failures);
  - the `git restore --source` tree (RV3-D-A05c) reports 9;
  - the targeted checkout that leaves the overlay alone (A05b) reports none.

## 7. Migration into the layout

Unchanged, plus one item. The first RoT-1 install transaction on a legacy project MUST, inside one journaled transaction:
1. quarantine legacy runtime residue;
2. move the kernel, overlay, views and adoption evidence;
3. write `governance/trust/**`;
4. create the occupation entries, force-adding `.governance-runtime/migration`;
5. **write the ignore rule of §2;**
6. record the project-strength vector;
7. write the ledger entry.

## 8. Residuals

| ID | Residual | Bound | Tests |
|---|---|---|---|
| LR-1 | Legacy binaries on a working copy not yet on the RoT-1 layout commit, including after `git revert` of the migration commit, operate on a legacy layout. | No RoT-1 state exists there. `LR2` evaluates reviewer C's revert tree as `LEGACY`: a RoT-1 binary is read-only on it. | RT-50, RT-82 |
| **LR-2** (restated, RV3-M6) | **Trigger.** Occupation entries are removed, by a person, a non-cone sparse checkout or A3; **or** pre-migration governance paths are restored with an ordinary Git command, such as `git checkout <pre-migration> -- governance` or `git restore --source <pre-migration> -- governance`. **Reachable legacy outcome (executed on the real 4.1.5 binary).** (i) The legacy binary goes from `NOT_INSTALLED` to a `verified: true` legacy install, directly or after `init --force`. (ii) It indexes and retrieves project material without the classifications added after migration; the RoT-1 overlay classifies it, the legacy overlay does not. (iii) A legacy CIT, answered by a caller-declared `decide --by owner`, can rewrite `governance/trust/**` (for example `governance/trust/kernel/policies/SECURITY_POLICY.yaml`), delete `governance/trust/framework.lock`, and remove overlay classifications. | **Only these bounds hold.** (1) A RoT-1 binary never treats the resulting tree as valid: `PARTIAL(occupation)` or `LEGACY` (`LR2`: every restored, removed or merged tree with legacy entries); policy root EmbeddedSnapshot ⊔ floors; mutations refused; doctor D033 CRITICAL names the mixed layout and stray artefacts; an edited trust kernel is `KERNEL_TAMPERED`. (2) Removal of project strength is reported `PROJECT_STRENGTH_WEAKENED` on every machine that recorded the vector (`LR2`: A05a, A05c). (3) LR-4 applies on machines without a record. No RoT-1 mechanism can stop a legacy binary from installing over paths the layout no longer occupies. | RT-81 (harm assertions for C A04–A06 and D A05/A06), RT-50b (occupation-absent register), RT-99 |
| LR-3 | Explicit operator output paths of producer commands. | Explicit A14/A10 action; PPS changes detected; strength weakening reported | — |
| LR-4 | Fresh clones accept the repository overlay as current project configuration. | T4 authority of the repository writer; per-machine detection after the first record | RT-99 |

**Carried engineering constraints (review r3 C-2…C-5).** These are specified in `18` §3 and §9, and tested in `12`:
- cross-device transaction area refusal;
- doctor naming stray merge and partial-removal artefacts;
- occupation type by `st_mode`;
- a full-register RT-50 with type-aware digests on a genuine 4.1.6 install.
