# 01 — Findings

Severity per `HO-0013` §4. **No CRITICAL, no HIGH, no blocking MEDIUM.** Every item below is fail-closed (the RoT-1
binary refuses: `PARTIAL`, `LEGACY` or `KERNEL_TAMPERED`) or inert (litter no trust decision consumes, named by doctor),
so none is a persistent or silent loss of a control and none is a state a RoT-1 binary treats as a **valid trust** state.
Each is carried as a bound, testable requirement without a trust-relationship change (`04-CARRIED-REQUIREMENTS.md`).

Evidence classes: **E** executed with the real 4.1.2–4.1.5 binaries and/or real Git; **D** design reading of the pack at
`cdb4e14`; **M** the pack's own reference model (`gov_admit_reference.py`) exercised.

---

## RV5-C-M1 — MEDIUM (carried) — No `.gitattributes` protects the kernel bytes: a `core.autocrlf=true` or `* text=auto` (Windows) checkout line-ending-converts the installed kernel, so the project is `KERNEL_TAMPERED`/`PARTIAL` and unusable there

**Statement.** The revision-5 `COMPLETE` predicate (`18` §9.1 item 2) and the use-time `KERNEL_TAMPERED` check (`18`
§6.1) both require the installed kernel tree under `governance/trust/kernel/` to equal the release content set byte for
byte. The kernel payload is text (YAML/JSON policies, schemas, templates). The layout (`26` §2, `08` §2) ships **no**
`.gitattributes`, and the pack mentions neither `.gitattributes`, `autocrlf`, `text=auto`, `eol` nor line-ending
normalisation anywhere. On a machine with `core.autocrlf=true` (the Git-for-Windows default) or a repository carrying
`* text=auto` checked out with `core.eol=crlf`, Git rewrites the on-disk line endings of every text file at checkout, so
the installed kernel no longer equals `RCS(D)`.

**Executed evidence (E)** (`gitops.json` AUTOCRLF, TEXTAUTO_EOLCRLF): both trees are `PARTIAL(kernel_content_mismatch)`
with `kernel_tampered = true`; the occupation entry **types** survive (the occupation itself is intact). The signed DSSE
statement files verify regardless (their payloads are base64, unaffected by envelope newlines), so only the raw kernel
files mismatch.

**Failure scenario.** A developer on Windows (or anyone with `autocrlf` set, or any clone of a repo carrying the very
common `* text=auto`) clones a RoT-1 project. Every trust operation above C0 refuses (`KERNEL_TAMPERED` → policy root is
EmbeddedSnapshot ⊔ floor, mutations refused). The project is unusable there until the user reconfigures Git and
re-checks-out. **This is fail closed** (a corrupted kernel is refused, never treated as valid), so it is an availability
and portability defect, not a silent-valid state — hence carried, not blocking.

**Correction direction (carried).** The install transaction MUST write a `.gitattributes` marking `governance/trust/**`
(and the occupation sentinel files, whose single trailing `\n` is likewise EOL-normalised) as `-text` (binary), and
`12` RT-50/RT-122 MUST include an `autocrlf=true` and a `* text=auto`+`core.eol=crlf` clone, asserting `COMPLETE`.

---

## RV5-C-M2 — MEDIUM (carried) — The `.gitignore` surgery reaches only the project file: a user `core.excludesFile` or `.git/info/exclude` carrying `.governance-runtime/` re-drops the migration occupation under the untracking idiom

**Statement.** `26` §8 (RV4-M6) closes the untracking idiom by removing every pre-existing `.governance-runtime/`
directory-ignore line from the **project** `.gitignore` and writing `/.governance-runtime/*` + `!/.governance-runtime/migration`.
The migration occupation `.governance-runtime/migration` survives the idiom only because no active ignore source lists its
parent directory as ignored: Git "cannot re-include a file if a parent directory is excluded". Two ignore sources are
**outside the install transaction's reach**: a user's global `core.excludesFile` (e.g. `~/.config/git/ignore`, where
ignoring runtime/build dirs like `.governance-runtime/` is common) and the repository's `.git/info/exclude`. Either
carrying a directory pattern `.governance-runtime/` makes the project `.gitignore`'s `!…/migration` negation ineffective,
so `git ls-files -ci --exclude-standard` lists `.governance-runtime/migration` and the "untrack ignored files" idiom
drops it.

**Executed evidence (E), real Git** (`gitops.json`):

| Ignore source with `.governance-runtime/` | idiom lists | later clone |
|---|---|---|
| none (project `.gitignore` surgery only) — UNTRACK_R5 | `[]` | `COMPLETE` |
| project `.gitignore` legacy line kept (no surgery) — UNTRACK_NOSURG | `[.governance-runtime/migration]` | `PARTIAL(occupation)` |
| user `core.excludesFile` — GLOBALEXCL | `[.governance-runtime/migration]` | `PARTIAL(occupation)` |
| `.git/info/exclude` — INFOEXCL | `[.governance-runtime/migration]` | `PARTIAL(occupation)` |

**Failure scenario.** A maintainer whose global gitignore ignores `.governance-runtime/` runs the common
`git ls-files -ci --exclude-standard | xargs git rm --cached`; the migration occupation is dropped from every later
clone, which are `PARTIAL(occupation)`. **Fail closed** (RoT-1 refuses; D033), hence carried. The occupation's survival
of the idiom is not a property of the project `.gitignore` alone; it holds only when no active ignore source (project,
global, `info/exclude`) matches the migration file's parent.

**Correction direction (carried).** State normatively that the occupation's untracking-idiom survival depends on no
active ignore source matching `.governance-runtime/`; `12` RT-122/RT-145 MUST run the idiom under a global
`core.excludesFile` and under `.git/info/exclude` carrying `.governance-runtime/`, asserting the idiom lists nothing or
that a resulting `PARTIAL(occupation)` clone is named by D033. (The occupation is fail-closed, so this bounds detection,
not a silent-valid state.)

---

## RV5-C-L1 — LOW (carried) — `26` §4 LP-1s overclaims: subtree `adopt baseline`/`migrate baseline` write `governance/spec` and `governance/views/spec` litter and the state stays `COMPLETE`

**Statement.** `26` §4 states LP-1s as "every write under `governance/**` other than the overlay files leaves a state
that is not `COMPLETE`, and every nested legacy install is reported". The architect's own P5-1 checks only writes under
`governance/trust/**` **or the occupation directory** — narrower than "under `governance/**`". The prose claim is false:
legacy `adopt baseline` / `migrate baseline` run from a working directory inside `governance/` root at `current_dir()` and
write `<cwd>/spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml`, i.e. `governance/spec/…`, `governance/views/spec/…` — a
write under `governance/**` (not overlay) — and the revision-5 state stays `COMPLETE` (no marker, no PPS entry).

**Executed evidence (E)** (`matrix5-summary.json` property `LP-1s_as_stated_26_s4`: 16 counterexamples): rows at cwd
`governance` and `governance/views` writing `governance/spec/audits/GOVERNANCE-ADOPTION/…` and
`governance/views/spec/audits/GOVERNANCE-ADOPTION/…`, state `COMPLETE`.

**Why inert / not blocking.** The litter is under `governance/spec/` and `governance/views/spec/` — RoT-1 reads
`governance/trust/`, `governance/overlay/` and `governance/views/` bytes bound to the CI (`VU-8`: an artefact without the
CI binding, e.g. written by a legacy binary, is never served). `governance/spec/` is not read by any trust decision. No
trust or kernel state changes; no classification is lost (`classification_lost_on_rot1_layouts`: 0 rows).

**Correction direction (carried).** Restate LP-1s to what holds ("every write under `governance/trust/**` or the
occupation directory leaves not-`COMPLETE`"), and extend doctor (C-3/C-6) to name stray `governance/spec` and
`governance/views` entries so a subtree adopt does not read green.

---

## RV5-C-L2 — LOW (carried) — The `18` §9.2 cwd-refusal set and `18` §9.1 closed-entry-set omit the transaction area, though `18` §8 lists it in the PPS

**Statement.** `18` §8 defines the Protected Path Set to include `.governance-runtime/trust-tx/**`. But `18` §9.2 item 2
refuses a working directory only inside "`governance/trust/**`, the occupation directory, an occupation file", and `18`
§9.1's closed-entry-set checks only `governance/trust/` and the occupation directory — neither covers the transaction
area. A legacy `init` (which roots at `current_dir()`) run from `.governance-runtime/trust-tx/` therefore is not refused
and installs a nested legacy project there; the revision-5 state stays `COMPLETE` because the nested marker is "elsewhere"
(not under the project's `governance/`), so `18` §9.1 item 5 only **reports** it (`NESTED_LEGACY_PROJECT`, doctor D039).

**Executed evidence (E)** (`matrix5-summary.json` property `legacy_writes_in_transaction_area_18_s8`: 96 rows, all
`COMPLETE`; the writing-rows file shows `reports_after: [{"NESTED_LEGACY_PROJECT": [".governance-runtime/trust-tx/governance"]}]`).

**Why inert / not blocking.** The litter is not consumed as a trust fact: `gov recover` honours a journal at
`.governance-runtime/trust-tx/<TX>/journal.json` **only if** the VTS lists `<TX>` open for this project **and** the path
is untracked (`18` §5.1, `20` §5). The legacy litter creates no VTS-registered `<TX>/journal.json`, so recover treats it
as `FOREIGN_TRANSACTION_ARTEFACT` (reported, ignored). The nested install is reported (D039 HIGH). This is the accepted
"nested install elsewhere → reported, state unchanged" bound (`26` §3, LR-3), applied here inside a PPS subtree.

**Correction direction (carried).** Reconcile the three definitions: either extend `18` §9.2's refusal and `18` §9.1's
closed-entry-set to the full `18` §8 PPS (including `.governance-runtime/trust-tx/**`), or state explicitly that the
transaction area's containment rests on the recover VTS-registration gate rather than on the state predicate.

---

## RV5-C-L3 — LOW (carried) — gov-admit "first admission" is not defined operationally; the reference discards the monotonic verifier trust store on re-run, and R-ADM-7's record placement is inconsistent with the reference

**Statement.** `31` R-ADM-8 says a verifier trust store present for the lineage "before the first admission is moved
aside". The pack gives no rule to detect "first admission" versus an operator re-running `gov-admit` on an
already-provisioned machine, and AP-10 (running-mode acceptance of binary N+1) references R-ADM-6/R-ADM-7 but **not**
R-ADM-8. R-ADM-7 says the admission record is "written beside the binary"; the reference executor writes it **inside**
the verifier trust store and unconditionally move-asides the whole store whenever it exists.

**Model evidence (M)** (`admit_tx.json`):
- `RV5-C-A08` crash after install, before record → binary installed, `C3` = `BINARY_NOT_ADMITTED`, `C0` = `ALLOWED`
  (fail closed). **Sound.**
- `RV5-C-A09` re-run on a store holding `high-water.json` (clock high-water, accepted-TBM), `anchors.json`,
  `projects/` → all three moved aside; the new store holds only the admission record. So a re-run of the documented
  first-admission command discards the machine's monotonic clock high-water (which defends against clock rollback,
  `24` §8 / RS-2) and its anchors.
- `RV5-C-A10` admitting a second binary through the same helper drops the first binary's record; per R-ADM-7 ("beside
  the binary") the record would instead be per-binary and survive a rollback — the reference's in-store placement
  contradicts the spec.

**Why not blocking.** `RV5-C-A09` needs a deliberate operator action (re-running `gov-admit`); its anchor loss is fail
closed (`UNANCHORED`, re-anchor required); only the clock-high-water reset is a genuine weakening, and exploiting it
additionally needs a clock adversary — this interacts with reviewer B's freshness/clock scope (RS-2). The reference is
architecture evidence, not the product; the defect is spec-clarity.

**Correction direction (carried).** Define first-admission detection so the fresh-store step (R-ADM-8) fires only when no
verifier trust store for the lineage exists, never on an operator re-run, so `clock_high_water`, anchors and per-project
records are never silently discarded; and reconcile R-ADM-7's "record beside the binary" with the record store so
rollback to a previously admitted binary keeps that binary's record. (Cross-scope with reviewer B on the clock
high-water.)
