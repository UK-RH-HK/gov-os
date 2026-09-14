# Output 26 — Legacy-binary damage containment

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 3. Closes R2-H4 and R2-L3 as a class and satisfies HO-0001 §3.4. It replaces the sentinel boundary of
> revision 2 (`13` §3). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

Revision 2 relied on sentinels that old binaries read only *after* acting. The review showed three things:
- real 4.1.5 `update --rollback` and `init --force`, and 4.1.2 `update --rollback`, rewrote a RoT-1 project;
- they deleted a project restricted-classification and reported `verified: true`;
- no RoT-1 remedy restored the classification (review `evidence/P3`).

The mistaken equivalence was *sentinel read afterwards ⇒ boundary*.

Revision 3 requirement: **a pre-RoT binary MUST NOT be able to silently mutate a RoT-1 project into a state it then
treats as valid, and the defence MUST NOT depend on the old binary understanding RoT-1.** The mechanism is structural. Old
binaries find no usable path to write, because every path they would use is occupied by an entry of the wrong type or
does not exist in their vocabulary.

## 2. Layout `rot-1/legacy-path-occupation-v1`

```text
governance/
├── trust/                         RoT-1 root — Protected Path Set; unknown to every pre-RoT binary
│   ├── FORMAT                     {"layout":"legacy-path-occupation-v1","minimum_reader":"4.1.6","trust_format":"rot-1"}
│   ├── framework.lock             lock 3.0.0 (08 §3)
│   ├── kernel/**                  installed kernel (no KERNEL_MANIFEST.json)
│   ├── release.dsse.json · lineage/ · state/ · root/ · profiles/
├── overlay/                       project overlay (relocated from governance/project); GovernedFs, not PPS
├── views/                         generated views (relocated from governance/generated); GovernedFs
├── kernel                         OCCUPIED: regular file (sentinel text)
├── project                        OCCUPIED: regular file
├── generated                      OCCUPIED: regular file
└── framework.lock/                OCCUPIED: directory containing ROT-1-TRUST-FORMAT (sentinel)
spec/audits/GOVERNANCE-ADOPTION    OCCUPIED: regular file (RoT-1 adoption evidence lives at spec/audits/ADOPTION/)
.governance-runtime/migration      OCCUPIED: regular file, tracked in Git (force-added despite the runtime ignore rule)
```

- Sentinel text: `ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-operate-this-project`.
- The occupation entries are **part of the Protected Path Set**: only the install transaction writes them.
- A missing or retyped occupation entry makes the RoT-1 installation state `PARTIAL(occupation)` (`18` §9), doctor D033
  CRITICAL. Restoring the entries is a remedy.

## 3. Why every pre-RoT command fails before its first write (class argument)

The command handlers of 4.1.2 (`8ad06be`), 4.1.3 (`26ab5b6`), 4.1.4 (`47d8394`) and 4.1.5 (`cli/src/main.rs` at base)
partition into two sets.

**(i) Commands that need an installation.** These call `open_project(cli, true)`, that is `Project::require_installed`,
which is `lock_path().exists() && kernel_dir().join("KERNEL_MANIFEST.json").exists()`
(`runtime/src/project.rs:97-99`, identical in 4.1.2).
- With `governance/kernel` a regular file, `governance/kernel/KERNEL_MANIFEST.json` cannot exist, so every such command
  returns `NOT_INSTALLED` before it opens the database or writes.
- This covers `update` including `--rollback` (which reads the legacy snapshot only after the authority check),
  `kernel reinstall`, `recover`, tasks, CIT, gates, `decide`, `rebuild-memory`, `memory *`, `tools *`, `plugins *`,
  `upstream *`, checkpoints, handoffs, adapters, `policy *`, `readiness *` and `claims *`.

**(ii) Commands that run without an installation**, each with its own write or restore root:

| Command | Write or restore root | Why it cannot write |
|---|---|---|
| `version`, `help`, `mcp` | none | no project write (`MCP_NOT_IMPLEMENTED`) |
| `init` | `governance/framework.lock` existence check, then `governance/kernel` | `ALREADY_INSTALLED` (the lock path exists as a directory); with `--force`, `install_kernel` into a regular file gives `IO_ERROR` before overlay or lock writes |
| `doctor` | read-only | — |
| `adopt`/`migrate` `baseline` | `create_dir_all(spec/audits/GOVERNANCE-ADOPTION)` (`adopt.rs:97-98`) | occupied by a regular file: `IO_ERROR` |
| `adopt`/`migrate` later stages | read `spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml` | `ADOPTION_NOT_STARTED` |
| `adopt`/`migrate rollback --batch N` | restores from `.governance-runtime/migration/batch-N/` with no precondition (`migrations/executor.rs:304-350`, identical in 4.1.2) | `.governance-runtime/migration` is a regular file, so nothing is restored |
| `capabilities ecosystems`/`plugins`/`serve-embed` | read-only, or stdin protocol | — |
| `capabilities invoke` | plugin descriptors under `governance/project/plugins` | occupied: `PLUGIN_NOT_FOUND` |
| `lessons cluster` | reads `framework/` or `governance/kernel/policies/LEARNING_POLICY.yaml` under `--root` | kernel path is a file, so it fails |
| `release build`/`verify` | canonical root from `GOV_CANONICAL_ROOT` only (`kernel.rs:83-92`) | no canonical root in a consumer project, so it fails; `verify` is read-only |

### 3.1 Legacy runtime residue

- **`.governance-runtime/update/<v>/`** (legacy update snapshots).
  - Only consumer: `update --rollback`, which is in set (i) and therefore blocked.
  - The first RoT-1 install transaction on a machine MUST additionally move it to
    `.governance-runtime/legacy-quarantine/update-<v>/`.
  - P3 deliberately leaves it in place and shows the layout alone suffices.
- **`.governance-runtime/migration/batch-N/`** (legacy adoption snapshots).
  - Consumer: `adopt rollback`, which is in set (ii).
  - It is occupied by a **tracked** regular file, so the occupation travels with Git.
  - Executed Git behaviour (`evidence/G1-git-occupation-behaviour.txt`):
    - pulling the RoT-1 commit into a working copy whose *ignored* residue directory is in the way removes the residue
      and checks out the occupation file;
    - with *unignored* untracked residue, the checkout aborts, and that working copy stays on the legacy layout, which
      holds no RoT-1 state to damage;
    - a fresh clone receives the file.

## 4. Executed property (P3r3)

**Property LP-1** (replaces LC-1 and LC-2): for every pre-RoT binary 4.1.2, 4.1.3, 4.1.4 and 4.1.5, and every invocation
derived from its own register (including mode-flag variants, destructive combinations and stateful chains), on a RoT-1
project carrying a legacy update snapshot and a project restricted-classification:
- no byte outside `.git/` and `.governance-runtime/` changes;
- Git state (HEAD, refs, index entries, stash) is unchanged;
- the classification survives.

**Evidence:** `evidence/P3r3-pre-rot-register-matrix.{py,json,stderr}`.

| Binary | Register (from its own `--help`) | Invocations on L3 | Tree changed | Git changed | Classification lost | Chains on L3 (10 each) with any change | Control L0: invocations changing the tree | Ablation L3A: invocations changing the tree |
|---|---|---|---|---|---|---|---|---|
| 4.1.2 | 104 leaf commands | 159 | **0** | **0** | **0** | **0** | 36 | 4 |
| 4.1.3 | 109 | 171 | **0** | **0** | **0** | **0** | 42 | 4 |
| 4.1.4 | 115 | 180 | **0** | **0** | **0** | **0** | 46 | 4 |
| 4.1.5 | 119 | 185 | **0** | **0** | **0** | **0** | 47 | 4 |

- **L0** is the positive control: an ordinary legacy project. It shows the synthesized arguments reach mutating code
  paths.
- **L3A** is the ablation: the layout without the two adoption occupations, with adoption residue present. Its 4
  changes per binary are `adopt baseline`, `migrate baseline`, `adopt rollback --batch 1` and
  `migrate rollback --batch 1`. They show that both occupations are necessary.
- **Refusal codes on L3 (695 invocations):**
  - `NOT_INSTALLED` 445;
  - `ADOPTION_NOT_STARTED` 140;
  - `IO_ERROR` 30;
  - `ALREADY_INSTALLED` 16;
  - `MCP_NOT_IMPLEMENTED` 8;
  - `PROTOCOL_MISMATCH` 6;
  - `PLUGIN_NOT_FOUND` 4;
  - `UNKNOWN_ROLE` 4;
  - 42 without an error code, 36 of them `ok: true`: `version`, `capabilities ecosystems|plugins`, `release verify`,
    `adopt|migrate rollback` restoring nothing. None changed anything.
- **Chains (each on a fresh copy, cumulative digests):**
  - adoption A0–A11 and batch rollback;
  - update check → apply → gate present → decide → apply --approve → rollback;
  - gate create → present → decide → revoke;
  - CIT propose with a manifest writing `governance/overlay/DATA_SENSITIVITY.yaml`,
    `governance/trust/kernel/policies/SECURITY_POLICY.yaml` and deleting `governance/trust/framework.lock` → simulate →
    approve → execute → rollback;
  - task create → claim → status → close;
  - `init --force` → verify → rebuild → query;
  - reinstall → verify → task create;
  - `recover` twice;
  - plugins register → invoke → rebuild;
  - `tools install --execute` → registry → `adapters generate`.

**R2-L3:** the revision-2 F1 probe is superseded. P3r3 writes the exact FORMAT JSON, the lock under
`governance/trust/framework.lock` and the full layout, and runs every command on its own fresh copy.

## 5. Protected paths (HO-0001 §3.4 list)

| Path class | Legacy use | Protection |
|---|---|---|
| Kernel paths | `governance/kernel/**` | regular file occupies the directory; RoT-1 kernel under `governance/trust/kernel/` |
| Legacy lock paths | `governance/framework.lock` | directory occupies the file |
| Trust paths | none in legacy | `governance/trust/**` is unknown to legacy binaries and is PPS |
| Rollback paths | `.governance-runtime/update/<v>/`, overlay and generated restore targets | blocked by set (i); quarantine on the transacting machine; overlay and views relocated, legacy names occupied |
| Reinstall paths | `governance/kernel` | set (i) (`NOT_INSTALLED`) |
| Init-force paths | `governance/kernel`, `governance/project`, `framework.lock` | `IO_ERROR` before first write; overlay relocated |
| Migration paths | `spec/audits/GOVERNANCE-ADOPTION/**`, `.governance-runtime/migration/**` | both occupied |

## 6. Project-owned strength (new rule 20)

Occupation removes the legacy route. Project-owned strengthening can still be removed by a repository writer or a
same-user process, because the overlay is T4. That is legitimate project governance when done through a governed
change. Revision 3 records strength so that silent removal is reported:

1. **Project-strength vector.** Every install transaction and every gated overlay change records, in the VTS per-project
   record, the digest-bound set of:
   - sensitivity classifications;
   - overlay floor raises;
   - repository-contract exclusions (index, retrieval, export);
   - non-overridable overlay keys.
2. **Check.** At every process start, the current overlay is compared with the recorded vector. A computed weakening not
   recorded through a gated transaction produces `PROJECT_STRENGTH_WEAKENED`. Security-relevant C2 operations (indexing,
   export, upstream, retrieval of the affected classes) are refused until a trust gate (`27`) accepts the new vector.
3. **Remedies do not hide it.** `kernel reinstall`, update and recover restore the PPS and occupation entries, but never
   the check. Returning to green requires the gate.
4. **Bound.** A machine with no record (fresh clone) accepts the repository's overlay as the project's current T4
   configuration. That is A2's normal authority over project configuration, stated as residual LR-4.

## 7. Migration into the layout

The first RoT-1 install transaction on a legacy project MUST, inside one journaled transaction:
1. quarantine `.governance-runtime/update/*` and `.governance-runtime/migration/*`;
2. move `governance/kernel` → `governance/trust/kernel` (authenticated content only), `governance/project` →
   `governance/overlay`, `governance/generated` → `governance/views`, and `spec/audits/GOVERNANCE-ADOPTION` →
   `spec/audits/ADOPTION`;
3. write `governance/trust/**`;
4. create the occupation entries, force-adding `.governance-runtime/migration`;
5. record the project-strength vector;
6. write the ledger entry naming the moves.

Git records the renames. Teammates still on legacy binaries then fail before any write (§4). The release protocol MUST
tell teams to retire 4.1.2–4.1.5 binaries.

## 8. Residuals

| ID | Residual | Bound |
|---|---|---|
| LR-1 | Legacy binaries on a working copy that has not checked out the RoT-1 layout commit operate on the legacy layout normally. | No RoT-1 state exists there to damage; the checkout itself is the boundary (§3.1). |
| LR-2 | A same-user process (A3) removes occupation entries. | RoT-1 reports `PARTIAL(occupation)`; the result is not a RoT-1 layout; A3-class. |
| LR-3 | Explicit operator output paths of producer commands (`release build --canonical <checkout> --out <path inside a project>`) write where the operator points them. | Explicit A14/A10 action, not a data effect; RoT-1 detects PPS changes (`KERNEL_TAMPERED`, `PARTIAL`) and project-strength weakening (§6). |
| LR-4 | Fresh clones accept the repository overlay as current project configuration. | T4 authority of the repository writer; per-machine detection after the first record (§6). |
