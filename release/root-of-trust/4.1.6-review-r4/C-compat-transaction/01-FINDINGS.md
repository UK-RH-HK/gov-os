# 01 — Findings

Severity per HO-0007 §4. One HIGH (blocking), one MEDIUM (carried). Evidence classes: **E** executed with the real
4.1.2–4.1.5 binaries and/or real Git; **D** design reading of the pack.

---

## RV4-C-H1 — HIGH (blocking) — The occupation defence protects only the project root; a pre-RoT `init` / `adopt baseline` / `migrate baseline` invoked from a subdirectory writes inside the trust Protected Path Set while a RoT-1 binary still reports `COMPLETE`. R2-H4 is not closed as a class.

**Statement.**
The revision-4 containment class argument (`26` §3) is: *“Commands that need an installation return `NOT_INSTALLED`
[because] `governance/kernel/KERNEL_MANIFEST.json` cannot exist when `governance/kernel` is a file. Commands that run
without an installation meet a wrong-typed entry at their write or restore root.”* This is true only for commands whose
root is the RoT-1 **project root**. Three legacy commands root at `current_dir()`, not at `find_root()`, and do not call
`require_installed()`:

```
cli/src/main.rs:  Cmd::Init  ... let root = cli.root.clone().unwrap_or(std::env::current_dir()?);
                  Cmd::Adopt{stage}|Cmd::Migrate{stage} ... let root = cli.root.clone().unwrap_or(std::env::current_dir()?);
                  (adopt::a0_baseline / a6_migrate write under `root`; init writes under `root`)
```

Run from **any subdirectory** of an intact revision-4 project with no `--root`, `gov init`, `gov adopt baseline` and
`gov migrate baseline` install a fresh **legacy** governance project rooted at that subdirectory — a path the occupation
does not occupy. The occupation only occupies six named entries at the project root; `product/`, `spec/`, and the
interior of the governance tree carry no occupation.

**Executed evidence (E).** Real 4.1.5/4.1.4/4.1.3/4.1.2 on the intact revision-4 R4 layout, no `--root`
(`evidence/matrix-rows.jsonl`, `evidence/subdir_escape.json`):

- **Rooted control:** with `--root <project>`, all 2,504 intact-layout invocations write nothing; every RoT-1 process is
  `COMPLETE`. The defence works as claimed for `--root`.
- **Subtree escape:** the only commands that ever write are `init`, `adopt baseline`, `migrate baseline` — 336
  invocations, each creating a nested legacy install (`<cwd>/governance/framework.lock` becomes a real lock file, a full
  kernel, overlay, adapters and `.governance-runtime/` databases are written, ~228 files).
- **PPS-interior writes:** when `cwd ∈ {governance/trust, governance/trust/state}`, **56** of those invocations write
  **inside `governance/trust/**`** — the Protected Path Set (`18` §8) — e.g. `governance/trust/.gitignore`,
  `governance/trust/.governance-runtime/{claims.db,state.db,telemetry/…}`, `governance/trust/archive/**`,
  `governance/trust/governance/framework.lock`, `governance/trust/governance/kernel/**`, and (for `adopt baseline`)
  `governance/trust/spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml`.
- **Treated as valid:** in every case the outer RoT-1 installation-state machine (`18` §9) computes **`COMPLETE`** (the
  six root occupation entries are intact and `governance/trust/{FORMAT, framework.lock, kernel/, release.dsse.json}` are
  present); the injected content under `governance/trust/**` is neither refused nor named by any check. `18` §9 `COMPLETE`
  does not enumerate the interior of `governance/trust/` beyond those named files, and there is no whole-subtree digest
  over `governance/trust/`.

**Failure scenario.**
On a fully intact, unmodified revision-4 project — no occupation removal, no Git restore, no privileged actor — an agent
or user working in a subdirectory (agents routinely `cd product/`; `gov init` / `gov adopt baseline` are the first
commands an operator reaches for) runs a pre-RoT binary. The binary silently writes a nested legacy installation into the
tree; when that subdirectory is under `governance/trust/`, the write lands inside the RoT-1 trust directory, and a RoT-1
binary afterwards still reports the project healthy (`COMPLETE`). This is exactly the state HO-0001 §3.4 forbids: *“a
pre-RoT binary must not be able to silently mutate the new … trust state into a state it then treats as valid”*, with
“trust paths” named in the protected set. The write is silent (no error, no `PARTIAL`, no doctor finding modelled) and
persistent (it is committed as ordinary tree content).

**Why HIGH / blocking.** The handoff's blocking bar: *“Harm that is silent and persistent, or a state a legacy or
ordinary operation produces that a RoT-1 binary later treats as valid, is blocking.”* Both limbs are met: the pre-RoT
write into `governance/trust/**` is silent and persistent, and the resulting tree is treated as valid (`COMPLETE`). The
fix cannot be a behaviour change to the (immutable) legacy binaries; it must be structural, and the current structure —
occupy six root entries — is insufficient. Making the PPS interior hostile, or redefining `COMPLETE` to reject foreign
entries under `governance/trust/**`, is an architecture change to `18` §9 and to the `26` §3 class argument, so it cannot
be carried as a pure implementation requirement.

**Scope note (honest bound).** The injected entries are a separate legacy install (litter), not an overwrite of the
kernel manifest or of a signed statement (those are one directory deeper, e.g. `governance/trust/governance/…`, and
signatures cannot be forged). I did **not** demonstrate that the injected content subverts a specific RoT-1 trust
decision; the behaviour of the union-record / trust-state enumeration when foreign directories and files exist under
`governance/trust/state/` is **unspecified** in the pack. The blocking claim rests on the demonstrated fact — silent,
undetected pre-RoT writes into the PPS accepted as `COMPLETE` — not on a proven enforcement bypass. A related exposure
risk (a nested legacy install in a content subdirectory indexes the project's material under a fresh overlay carrying
none of the RoT-1 classifications) is plausible: I confirmed directly that a legacy install *without* a classification
retrieves a marked file that the same install *with* the classification suppresses (`evidence/` direct test), but I did
**not** reproduce retrieval of a specifically-classified file through a nested-in-subdirectory index in the tree layouts
tried, because the fresh install's default content roots did not include the file's nested-relative path.

**Correction direction (architectural).**
- The installation-state machine must treat the interior of `governance/trust/**` as an integrity-checked set: `COMPLETE`
  must require that `governance/trust/` contains no entries beyond the RoT-1 set (a whole-subtree check / manifest), else
  `PARTIAL(foreign_trust_entry)` with a doctor CRITICAL. Equivalently, extend the occupation/hostility argument to cover
  writes rooted **inside** the protected tree, not only at the project root.
- The class argument in `26` §3 must be restated: it holds only for invocations rooted at the project root; the pack must
  state the containment (or its absence) for invocations rooted in a subdirectory, and the acceptance plan (`12` RT-50 /
  RT-50b) must run the full register from representative subdirectories (`product/`, `spec/`, `governance/overlay/`,
  `governance/trust/`, `governance/trust/state/`) with **no** `--root`, asserting no byte under `governance/trust/**`
  changes and that a resulting tree with foreign PPS entries is not `COMPLETE`.

**Acceptance.** `evidence/subdir_escape.py` / `subdir_escape.json`; `evidence/matrix.py` / `matrix-rows.jsonl`
(positions `P-CWD:governance/trust`, `P-CWD:governance/trust/state`); `evidence/matrix-chains.json`.

---

## RV4-C-M1 — MEDIUM (carried) — The RV3-L7 fix depends on the migrated `.gitignore` holding only the replace-form rule; a real migrated project retains the legacy `.governance-runtime/` line, under which the untracking idiom again drops the migration occupation.

**Statement.**
Revision 4 closes RV3-L7 by writing the ignore rule `/.governance-runtime/*` + `!/.governance-runtime/migration` and
describing it as *“replaces ignoring the whole directory”* (`13` §10; `08` §2; `26` §2). The closure holds **only if**
the migrated project's `.gitignore` contains that rule **alone**. But:

1. A real legacy project's `.gitignore` already contains the line `.governance-runtime/`, written by legacy `init.rs`
   (`runtime/src/init.rs`: appends `.governance-runtime/\n` if absent). The revision-4 layout is reached by migrating
   such a project.
2. `.gitignore` is a **user-authored file** that may hold arbitrary user entries. For the *replace* reading to hold, the
   install transaction must locate and **remove** the specific pre-existing `.governance-runtime/` line while preserving
   the rest. No pack rule specifies this surgery: `26` §7 step 5 and `18` §4 say only *“write the ignore rule”*; `08` §2
   says *“writes two `.gitignore` lines”*. The non-destructive default — append — retains the legacy line.

**Executed evidence (E), direct Git** (`evidence/durability.json`, `evidence/subdir_escape` build facts):

| Migrated `.gitignore` | `git ls-files -ci --exclude-standard` | untracking idiom result | fresh clone state |
|---|---|---|---|
| `/.governance-runtime/*` + `!…/migration` (replace — the pack's tested tree) | `[]` | drops nothing | `COMPLETE` |
| `.governance-runtime/` + `/.governance-runtime/*` + `!…/migration` (append — legacy line retained) | `[.governance-runtime/migration]` | **drops `.governance-runtime/migration`** | **`PARTIAL(occupation)`** |

Git's re-inclusion rule (*“cannot re-include a file if a parent directory is excluded”*) means the trailing-slash
directory pattern `.governance-runtime/` keeps `ls-files -ci` reporting the tracked-but-ignored migration file even though
the later negation exists; the idiom then untracks it. The architect's closure evidence
(`evidence/RV3-D-A05-A07-rerun-r4-layout.json`) was produced on a hand-built tree carrying **only** the replace-form
rule, so the retained-line case was not exercised.

**Failure scenario.** After migration, the migration occupation `.governance-runtime/migration` is dropped from every
later clone by an ordinary maintainer running the common “untrack ignored files” idiom; those clones are
`PARTIAL(occupation)`. This is fail-closed (RoT-1 refuses, D033), and P3r3's L3A ablation shows the migration occupation
is load-bearing only when legacy adoption residue is present. Availability and one adoption occupation are lost, not a
silently-valid state — hence carriable, not blocking.

**Correction direction (specification / carried).** State normatively that the install transaction (a) removes any
pre-existing `.governance-runtime/` (with or without a trailing slash) directory-ignore line from `.gitignore` before
writing the child-glob rule, preserving all other user content, and is idempotent under re-run; and (b) `12` RT-122 must
build the migrated project from a real legacy `.gitignore` (retained legacy line) and assert the idiom lists nothing.

**Acceptance.** `evidence/durability.py` / `durability.json` (R4 vs R4APP §10); `evidence/subdir_escape` /
`trees-build.json` (`R4APP.tracked_but_ignored == [".governance-runtime/migration"]`).
