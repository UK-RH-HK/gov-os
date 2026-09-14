# F — Pre-RoT binary boundary

Questions: can an old binary
- (a) falsely report the new project as trusted;
- (b) mutate it before recognising incompatibility;
- (c) overwrite kernel or trust state;
- (d) execute recovery or reinstall before refusal?

## 1. Evidence (executed, `evidence/P3-pre-rot-binary-matrix.{py,json}`, `evidence/P3b-attribution-control.*`)

**Binaries:** the real `gov 4.1.5` (`target/release/gov`) and the real `gov 4.1.2` (built from `8ad06be`).

**Base project**, built with 4.1.5:
1. Installed 4.1.4.
2. Ran an ordinary gated update to 4.1.5. This leaves the normal unconsumed snapshot `.governance-runtime/update/4.1.5/`.
3. Added project-owned strengthening **after** the update: a `DATA_SENSITIVITY` classification making
   `product/restricted-plan.md` restricted.
4. Control: the file is not retrievable and `kernel trust` reports `verified: true`.

**Layout V0.** The project is then rewritten into the layout of `13` §3.1 and `08` §2–§3:
- lock sentinels and `kernel.*` fields;
- tombstone `KERNEL_MANIFEST.json`;
- `governance/trust/FORMAT` as JSON;
- `governance/trust/release.dsse.json`.

The 4.1.5 payload stands in for the 4.1.6 kernel, as in the architect's F1.

Each command ran on a fresh copy.

| Binary | Command | Envelope | `governance/` changed | `spec/` changed | Classification survives | Old binary's trust view afterwards | Restricted file retrievable afterwards | RoT-1 installation state (`18` §9) |
|---|---|---|---|---|---|---|---|---|
| 4.1.5 | `kernel verify` | runs | no | no | yes | — | — | COMPLETE, intact |
| 4.1.5 | `doctor` | `UNHEALTHY` | no | no | yes | — | — | COMPLETE, intact |
| 4.1.5 | `task create` | `KERNEL_TAMPERED` | no | no | yes | — | — | COMPLETE, intact |
| 4.1.5 | `rebuild-memory` | `KERNEL_TAMPERED` | no | no | yes | — | — | COMPLETE, intact |
| 4.1.5 | **`update --rollback`** | **ok** | yes | yes (ledger) | **no** | **`verified: true`** | **yes** | COMPLETE, `KERNEL_TAMPERED` |
| 4.1.5 | **`init --force`** | **ok** | yes | yes | **no** | **`verified: true`** | **yes** | COMPLETE, `KERNEL_TAMPERED` |
| 4.1.5 | `kernel reinstall` | `KERNEL_MISMATCH` **after overwriting** | yes | no | yes | — | — | COMPLETE, `KERNEL_TAMPERED` |
| 4.1.5 | `recover` | `KERNEL_TAMPERED` | no | no | yes | — | — | COMPLETE, intact |
| 4.1.2 | `kernel verify` | runs | no | no | yes | — | — | COMPLETE, intact |
| 4.1.2 | `doctor` | `UNHEALTHY` | no | no | yes | — | — | COMPLETE, intact |
| 4.1.2 | **`task create`** | **ok** | no | **yes** | yes | — | — | COMPLETE, intact |
| 4.1.2 | **`rebuild-memory`** | **ok** | yes | no | yes | `kernel verify` not ok | **yes** (4.1.2's own defect, see P3b) | COMPLETE, intact |
| 4.1.2 | **`update --rollback`** | **ok** | yes | no | **no** | **`kernel verify` ok** | **yes** | COMPLETE, `KERNEL_TAMPERED` |
| 4.1.2 | `init --force` | `DB_ERROR` **after overwriting** | yes | no | **no** | — | — | COMPLETE, `KERNEL_TAMPERED` |
| 4.1.2 | `kernel reinstall` | `KERNEL_SOURCE_NOT_FOUND` | no | no | yes | — | — | COMPLETE, intact |
| 4.1.2 | `recover` | `DB_ERROR` | no | no | yes | — | — | COMPLETE, intact |

**P3b attribution control.** 4.1.2 also returns the restricted file on a plain 4.1.5 project, so that exposure is the
4.1.2 binary's own defect (LC-2 class). The layout's contribution is that it does not stop 4.1.2 from operating.

## 2. Answers

**(a) Falsely report the project trusted — yes, after its own exempt remedy.**
- 4.1.5 `update --rollback` and `init --force`, and 4.1.2 `update --rollback`, succeed on the RoT-1 project. They rewrite
  kernel, lock and overlay into 4.1.x form, and the old binary then reports `verified: true` or `kernel verify` ok.
- F1's conclusion "never interprets a RoT-1 project as verified" holds only until any of these commands runs.
- `update --rollback` and `recover` are exempt from the 4.1.5 kernel-trust guard (`kernel_trust.rs:31-43`).

**(b) Mutate before recognising incompatibility — yes.**
- 4.1.2 creates tasks (writes to `spec/`) without any refusal.
- 4.1.5 `kernel reinstall` and 4.1.2 `init --force` write first and fail afterwards.

**(c) Overwrite kernel or trust state — kernel, lock, overlay and generated views yes.**
- `governance/trust/` is left behind, so a RoT-1 binary later sees COMPLETE with `KERNEL_TAMPERED` and fails closed for
  the kernel.
- `governance/project/` is restored from the legacy snapshot (`update.rs:348-420`) or rewritten from templates
  (`init.rs:43-82` with `--force`).

**(d) Execute recovery or reinstall before refusal — yes.**

## 3. Why LC-1 is not "availability impact only"

1. The legacy rollback and `init --force` **delete project-owned strengthening** added after the legacy snapshot.
   Here, the restricted classification.
2. The overlay is not a Protected Path, is not signed, and is not recorded in the lock, the trust record or the VTS. A
   RoT-1 binary sees `KERNEL_TAMPERED` and offers `gov kernel reinstall` or an update (`20` §8). Both are install
   transactions over Protected Paths only. By specification the kernel and trust record are restored and **the
   classification is not**.
3. The RoT-1 binary then indexes the file under the default class. Nothing in revision 2 reports the weakening. This step
   is by specification reading, since no RoT-1 binary exists.
4. Team members still on 4.1.5 or 4.1.2 operate normally on 4.1.x floors after the rewrite and share their records
   through Git.
5. No attacker is needed. A teammate who has not upgraded runs a routine command (`gov update --rollback` is the
   documented recovery of the 4.1.x line), or A10 asks them to.

## 4. The residual is not inherent (layouts V1 and V3, executed)

| Layout | Change | Result |
|---|---|---|
| V1 | legacy lock path occupied by a **directory**; RoT-1 lock elsewhere | **insufficient.** `update --rollback` in both binaries still overwrites kernel and overlay before failing on the lock copy (the loop order in `update.rs:348-420`). |
| V3 | V1 **and** legacy kernel path occupied by a **regular file**; RoT-1 kernel relocated | **every tested command in both binaries refused** (`NOT_INSTALLED` or `IO_ERROR`), with **no change to `governance/` or `spec/`** and the classification intact: `kernel verify`, `doctor`, `task create`, `rebuild-memory`, `update --rollback`, `init --force`, `kernel reinstall`, `recover` |

Data can therefore turn pre-RoT behaviour into fail-before-write. LC-2's statement that "RoT-1 cannot change their
behaviour through data" is refuted for the tested commands.

The remaining obligation is the full command register of each pre-RoT binary 4.1.2–4.1.5, notably:
- `adopt *`;
- `cit execute` and `cit rollback`;
- `tools install`;
- `plugins register`;
- `upstream`;
- `gate` and `decide`;
- `memory select`.

## 5. Determination

**R2-H4.** The mitigation is not sufficient, and the stated bound is false. A strictly better boundary is feasible, so
the residual cannot be accepted as inherent.
