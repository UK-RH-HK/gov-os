# Output 26 — Legacy-binary damage containment and project-owned strength

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 7 (CP-1; review r6 carried items): §6 re-records never drop a failing requirement and pending gate obligations
> survive remedies (CR6-C-9, RV6-M5); §7 the first-install layout migration is journaled step by step with redo and undo
> records and an intent phase before the exchange, and R-INIT-9 governs `init` over an existing overlay (CR6-C-7, RV6-M3); §8
> remedies force-add the migration occupation (CR6-C-2), doctor names `governance/overlay/spec` litter (CR6-C-3), and LR-2's
> triggers include a crash during the first install transaction (CR6-C-7 (e)). The layout is otherwise unchanged; reviewer C's
> `matrix6` re-run: property R2-H4 0 violations.
> Revision 6: the `.gitattributes` member and its stated override condition (§2; RV5-M6); LP-1s restated to what holds (§4;
> RV5-L7); the ignore-source condition with detection (§8; RV5-M7); legacy containment re-run on the revision-6 layout
> (LAY6: property R2-H4 0 violations). The layout is otherwise unchanged.
> Revision 5: §3 scope, §4 LP-1 and §8 LR-2 restated for subdirectory-rooted invocations (carried RV4-M1, RV4-M6); the
> layout is unchanged.
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
│   ├── .gitattributes             exactly `* -text` (revision 6, RV5-M6)
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
- **Line endings (revision 6, RV5-M6, RV5-C-M1).** The install transaction writes `governance/trust/.gitattributes` with the
  exact content `* -text`, a member of the trust top-level entry set (`18` §9.1). Clones with `core.autocrlf=true` (the Git
  for Windows default), with a project `.gitattributes` `* text=auto` and `core.eol=crlf`, or with a project `* text
  eol=crlf`, keep the kernel bytes (`evidence/r6/ATTR6-*`; LAY6 `AUTOCRLF`, `TEXTAUTO_EOLCRLF`: `COMPLETE`). **Stated
  condition:** `.git/info/attributes` has the highest attribute precedence in Git; a clone whose `.git/info/attributes` sets
  `text` (or `text=auto`, or `eol=crlf`) for the kernel paths, with CRLF conversion configured, still converts them. That
  clone fails closed (`PARTIAL(kernel_content_mismatch)`; `KERNEL_TAMPERED`), and doctor D033 names `.git/info/attributes`
  as the source (ATTR6 rows O1–O4; RT-173).
- **Partial state.** A missing or retyped occupation entry makes the RoT-1 installation state `PARTIAL(occupation)`
  (`18` §9), doctor D033 CRITICAL. Doctor also names stray legacy artefacts left by merges or partial removal (C-3).

## 3. Why every pre-RoT command fails before its first write (class argument)

For invocations rooted at the project root, unchanged from revision 3: commands that need an installation return
`NOT_INSTALLED`, because `governance/kernel/KERNEL_MANIFEST.json` cannot exist when `governance/kernel` is a file; commands
that run without an installation meet a wrong-typed entry at their write or restore root.

**Scope restated (revision 5; RV4-M1 (c)).** The argument does **not** cover invocations rooted in a subdirectory. Legacy
`init`, `adopt baseline` and `migrate baseline` root at the working directory and skip `require_installed`
(`cli/src/main.rs` lines 729, 747). From any subdirectory they install a nested legacy project, and legacy commands then
operate beneath it, including inside the Protected Path Set. The reachable outcome and its bound:
- a nested install or litter under `governance/trust/**`, under the occupation directory, or anywhere under `governance/`
  makes the RoT-1 state `PARTIAL` (`18` §9.1) and doctor names every entry;
- a nested-root legacy CIT that edits the installed kernel is `KERNEL_TAMPERED` and `PARTIAL(kernel_content_mismatch)`;
  one that deletes the trust lock is `PARTIAL`;
- a nested install outside `governance/` (for example `product/`) leaves the state unchanged and is reported
  (`NESTED_LEGACY_PROJECT`); its own legacy index is legacy-binary behaviour outside RoT-1 (LR-3 class);
- an overlay rewrite through a nested root leaves `governance/governance/…` behind, so the state is `PARTIAL`; the overlay
  change itself is reported where the strength vector was recorded (LR-4 elsewhere).
RoT-1 commands refuse to run with a working directory inside the Protected Path Set (`18` §9.2).

### 3.1 Legacy runtime residue

Unchanged. `.governance-runtime/update/<v>/` is blocked by set (i) and quarantined by the first RoT-1 transaction.
`.governance-runtime/migration/batch-N/` is occupied by the tracked file, which now also survives untracking (§2).

## 4. Executed property (LP-1)

**Restated (revision 5).** LP-1 is two properties. **LP-1r (root-anchored):** every invocation of each binary's own register
with `--root <project>` writes nothing (P3r3 re-run on revision 5: 2,085 jobs, summary, property and chain results equal to
the committed output, `evidence/r5/P3r3-rerun-r5-summary.json`; reviewer C's 2,504 root-anchored rows). **LP-1s
(subdirectory-rooted; restated in revision 6, RV5-L7):** invocations with no `--root` from any working directory may write;
every write under `governance/trust/**` or the occupation directory leaves a state that is not `COMPLETE`, and every nested
legacy install is reported. Subtree `adopt baseline` and `migrate baseline` litter under `governance/spec` and
`governance/views/spec` stays `COMPLETE` (inert: nothing reads it) and doctor names it (RT-176). Revision 5's wording
("every write under `governance/**` other than the overlay files") was false for that litter (review r5 16 counterexamples).
Evidence: `evidence/r5/ST5-subdir-matrix-summary.json` (6,292 invocations); `evidence/r6/LAY6/` (reviewer C's matrix on the
revision-6 layout: 30,735 rows, R2-H4 0 violations; LP-1s as restated 0 counterexamples over 540 rows; as stated in revision 5,
16).
RT-50 and RT-50b run both (`12`).


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
   the check. Only the gate re-records the vector. **Revision 7 (CR6-C-9):** a re-record never drops a failing requirement unless the
   `weakening` or `project_strength` gate accepted it; pending `policy_lowering` and `registration_change` obligations are
   per-project record fields that no install transaction clears (`evidence/r7/PPR7-project-records.json`).
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

**Revision 7 (CR6-C-7 (a), (d), (e); RV6-M3).** Each step above is a journal phase (`18` §5.3) with an idempotent redo record and
an undo record written before the step, including where the legacy kernel, lock and residue were moved; an intent phase
precedes `RENAME_EXCHANGE`; recovery rolls the layout forward only when every redo record is complete and the exchange happened,
and otherwise undoes to exactly the pre-transaction legacy layout. No recovered prefix is `ABSENT` or `PARTIAL` (`18` §9).

| ID | Rule |
|---|---|
| R-INIT-9 | RoT-1 `init` on a tree holding `governance/overlay` or `governance/views` refuses (`INIT_OVER_EXISTING_OVERLAY`) unless it evaluates `19` §9 item 5 over the pre-transaction overlay before commit and obtains the `weakening` trust gate for a non-empty failure list. |

Evidence: `evidence/r7/LAY7/crashmig7.json`: 24 crash prefixes in both lock orders; 22 rolled back to the legacy layout, byte-equal
to the legacy project; 2 rolled forward; never `ABSENT` or `PARTIAL` after recovery; legacy behaviour on rolled-back trees equals
the control; RoT-1 `init` never runs over an overlay. Test: RT-195.

## 8. Residuals

**Revision 7 (CR6-C-2, CR6-C-3, CR6-C-7 (e)).** Every remedy that recreates the occupation (`kernel reinstall`, `update --apply`,
`recover`, `init --force`) force-adds `.governance-runtime/migration`. Doctor names stray `governance/spec`, `governance/views/spec`
and `governance/overlay/spec` trees and distinguishes overlay litter from a genuine overlay change. LR-2's triggers include a crash
during the first install transaction; its bound is the recovery of §7.

**Revision 6 (RV5-M7, RV5-C-M2): ignore sources.** The `.gitignore` surgery reaches only the project file. The occupation's
survival of the "untrack ignored files" idiom **requires that no active ignore source matches `.governance-runtime/`**: not
the project `.gitignore` (the surgery ensures it), not a user `core.excludesFile`, not `.git/info/exclude`. Under either of
the latter the idiom lists `.governance-runtime/migration`, and a later clone is `PARTIAL(occupation)` (fail closed; LAY6
`GLOBALEXCL`, `INFOEXCL`). Doctor D033 names the resulting `PARTIAL(occupation)` together with the ignore source that
matches, as reported by `git check-ignore --no-index -v .governance-runtime/migration` (LAY6 check-ignore rows: the user
excludes file line 1 and `.git/info/exclude` line 7; control: the project `.gitignore` negation). Test: RT-174.

**Revision 5 restatement of LR-2 (RV4-M1 (c)).** LR-2's bounds apply to every trigger that removes occupation entries or
restores pre-migration paths **and** to the subdirectory trigger on the intact layout: after any of them RoT-1 binaries fail
closed (`PARTIAL`, `LEGACY` or `KERNEL_TAMPERED`) and report lost project strength where it was recorded; the subdirectory
trigger can no longer leave `COMPLETE` (`18` §9.1). **RV4-M6:** the install transaction removes every pre-existing
`.governance-runtime/` directory-ignore line (with or without leading or trailing slash) before writing the child-glob
rules, preserving all other lines, idempotently (`evidence/r5/ST5-gitignore-surgery.json`: second run changes no byte; the
untracking idiom lists nothing; a fresh clone is `COMPLETE`; control without the surgery: `PARTIAL`).


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
