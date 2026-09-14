# 01 — Findings

Severity per `HO-0017` §4. **No CRITICAL, no HIGH.** Five MEDIUM and six LOW. Every MEDIUM is carried as a bound, testable
implementation requirement that changes no trust relationship (`04-CARRIED-REQUIREMENTS.md`), so none is blocking. Each
item is fail-closed (a RoT-1 binary refuses: `PARTIAL`, `LEGACY`, `KERNEL_TAMPERED`), inert, fail-safe, or a specification
ambiguity whose unsafe reading an acceptance test already names or a carried rule removes. Where an unsafe reading exists it
is stated, with the carried rule that removes it.

Evidence classes: **E** executed with the real 4.1.2–4.1.5 binaries and/or real Git 2.43.0; **M** the pack's own revision-6
reference executor exercised; **D** design reading of the pack at `4106885`.

| ID | Severity | Title | Evidence |
|---|---|---|---|
| RV6-C-M1 | MEDIUM (carried) | Out-of-project ignore sources still re-drop the migration occupation (RV5-M7 narrowed: condition stated, source named) | E |
| RV6-C-M2 | MEDIUM (carried) | The first-install layout migration and the exchange-to-journal window lie outside the journal phase model; the documented recovery leaves half-migrated trees `LEGACY`, `PARTIAL` or `ABSENT` | E + D |
| RV6-C-M3 | MEDIUM (carried) | The per-project record's identity is unsound under ordinary repository duplication (worktree, second clone, move, fork, template) | E (fact) + D |
| RV6-C-M4 | MEDIUM (carried) | Contradictory re-record rules at install commit can discharge pending weakening and registration obligations through a documented remedy or update | D |
| RV6-C-M5 | MEDIUM (carried) | The verifier trust store's location and owner are specified two incompatible ways, so first-admission, store preservation and AD-2 apply to an undefined store | D + M |
| RV6-C-L1 | LOW | `.git/info/attributes` overrides the trust `.gitattributes` member (fail closed; RV5-M6 closed as a class) | E |
| RV6-C-L2 | LOW | The transaction-area foreign-artefact scan does not exclude the completed-transaction `done/` archive | E + D |
| RV6-C-L3 | LOW | `gov-admit` reference edges: a record-less store with anchors is moved aside; records are honoured by digest across lineage stores | M |
| RV6-C-L4 | LOW | The LP-1s restatement names two litter locations; a third, inside the overlay, stays `COMPLETE` unnamed | E + D |
| RV6-C-L5 | LOW | Evidence and text accuracy in the legacy-containment and transaction sections | E + D |
| RV6-C-L6 | LOW | "Rollback to a previously admitted binary keeps its record" omits that the accepted-TBM high-water refuses that binary | D |

---

## RV6-C-M1 — MEDIUM (carried) — out-of-project ignore sources still re-drop the migration occupation

**Statement (D, E).** The `26` §8 `.gitignore` surgery reaches only the project `.gitignore`. The migration occupation
`.governance-runtime/migration` survives the common "untrack ignored files" idiom (`git ls-files -ci --exclude-standard` →
`git rm --cached`) only when no active ignore source matches `.governance-runtime/`. A user `core.excludesFile` or the
repository's `.git/info/exclude` carrying `.governance-runtime/` defeats the project `.gitignore`'s `!…/migration`
negation. Revision 6 states this condition and names the source through `git check-ignore --no-index -v` (RT-174); the
behaviour is unchanged from revision 5.

**Executed evidence (E)** (`gitops6.json`): with a user `core.excludesFile` (`GLOBALEXCL`) or `.git/info/exclude`
(`INFOEXCL`) the idiom lists `.governance-runtime/migration` and the later clone is `PARTIAL(occupation)`; `check-ignore`
names `…/excl:1` and `.git/info/exclude:7`. Surgery only (`UNTRACK`): the idiom lists nothing, clone `COMPLETE`. A retained
legacy directory-ignore line (`UNTRACK_NOSURG`): `PARTIAL(occupation)`.

**Failure scenario.** A maintainer whose global gitignore ignores runtime directories runs the idiom; every later clone is
`PARTIAL(occupation)` until the occupation is re-added. **Fail closed.**

**Correction direction (carried).** As `26` §8 states; RT-174 runs the idiom under both sources and asserts
`PARTIAL(occupation)` with D033 naming the source; a remedy that recreates the occupation MUST also force-add it
(`26` §7 step 4), which `20` §8 does not state for `kernel reinstall`. (`04` CR6-C-2.)

---

## RV6-C-M2 — MEDIUM (carried) — the first-install layout migration and the exchange-to-journal window lie outside the journal phase model

**Statement (D).**
1. `26` §7 requires the first RoT-1 install on a legacy project to perform, "inside one journaled transaction", quarantine,
   moves (kernel, overlay, views, adoption evidence), trust tree, occupation entries, ignore rule, strength vector and ledger.
   `18` §4 performs the layout steps between journal phase `verified-staged` and `RENAME_EXCHANGE`, and **no journal phase
   names them**. `18` §5.3 and `20` §5 recover an honoured `prepared`/`staged`/`verified-staged` journal by "move
   `trust-tx/<TX>` to `trust-tx/abandoned/`; deregister": nothing undoes or completes a layout step already performed. Where
   the legacy kernel and lock are moved to is not specified. `RENAME_EXCHANGE governance/trust ↔ trust.next` presupposes a
   `governance/trust` that a legacy layout does not have.
2. The `18` §9 table has no precedence between `IN_TRANSACTION` ("an honoured journal") and `ABSENT`/`LEGACY`, whose
   conditions do not exclude an honoured journal.
3. `18` §4 writes journal phase `swapped` after the exchange. A crash between the exchange and that write leaves a
   `verified-staged` journal with the new tree already in place; phase-only recovery then abandons a transaction whose
   exchange happened (for an update, moving `trust.prev` — the previous trust tree — into `abandoned/`) and the installation
   is `COMPLETE` without its migrations, strength-vector evaluation, per-project record update and ledger entry.

**Executed evidence (E)** (`crashmig6.json`; real legacy 4.1.5 and 4.1.2; `state_r6`). From the real legacy project, the tree
a crash leaves after each prefix of the layout steps (two orders for the unspecified removal of the legacy lock), with the
staged trust tree and a `verified-staged` journal:
- While the journal is honoured, 12 of 24 prefixes match `IN_TRANSACTION` **and** `LEGACY` or `ABSENT` at once.
- After the documented recovery: prefixes before the moves are `LEGACY`; mid-move prefixes are `PARTIAL`; **order A after
  the kernel, lock, overlay and views moves (A-05, A-06) is `ABSENT`** — the state in which `18` §9 allows `init`, on a tree
  whose `governance/overlay` still carries the project's restricted classifications; after the exchange (A-11, B-11) the
  modelled `verified-staged` journal is abandoned and the tree is `COMPLETE` (facet 3).
- On every non-`COMPLETE` post-recovery prefix up to the occupation files, legacy `init --force` succeeds, and legacy
  `memory query` then serves `product/restricted-plan.md`; on the pre-move prefixes legacy `kernel trust` reports
  `verified: true`. **No prefix becomes `COMPLETE` through a legacy command** (RoT-1 state after the legacy commands:
  `LEGACY` or `PARTIAL`).

**Failure scenarios.**
- A crash (power loss, killed CI job) during the first `gov update --apply` on a legacy project, followed by `gov recover`,
  leaves a tree that is neither the pre-transaction legacy project nor a RoT-1 install; RoT-1 has no roll-forward or undo for
  it (Git restore of tracked files is the only path). Legacy binaries then operate it and serve restricted material — the
  LR-2 outcome, reached by a trigger LR-2's trigger list does not include.
- In order A the recovered tree is `ABSENT`. `18` §9 allows `init`; `19` §9's weakening computation covers update, rollback,
  restore, recovery exchange-back and adoption batch 0, **not `init`**; no per-project record exists (first install). If an
  implementation's `init` writes its overlay templates over, or ignores, the existing `governance/overlay`, the restricted
  classifications are lost and the resulting install is `COMPLETE` with nothing to detect it (LR-4). The pack neither requires
  nor forbids that behaviour.

**Why MEDIUM, not HIGH.** RoT-1 never reaches `COMPLETE` from a half-migrated tree by any legacy command; the tracked
pre-migration files remain restorable with Git; the classification-loss path needs an `init` behaviour the pack leaves
unspecified. It is carriable as bound transaction rules and crash-injection tests without a trust-relationship change. **If an
implementation's `init` on `ABSENT` overwrites or ignores an existing `governance/overlay`, this becomes a silent persistent
control loss (HIGH).**

**Correction direction (carried).** (a) Journal every layout-migration step as a phase with an idempotent redo and undo
record (including where the legacy kernel, lock and residue are moved), and make recovery roll the layout forward or back to
exactly the pre-transaction legacy layout; (b) give `IN_TRANSACTION` precedence over every other row, and add a state for a
detected incomplete layout migration (never `ABSENT` or `LEGACY` while any migration artefact or journal exists); (c) `ABSENT`
additionally requires no `governance/overlay` and no `governance/views`, and `init` on a tree holding either refuses or runs the
`19` §9 item 5 computation; (d) write an intent phase before `RENAME_EXCHANGE`, or make recovery determine from the tree
whether the exchange happened (identity of `governance/trust` against `trust.next`/`trust.prev`); (e) add "crash during the
first install transaction" to LR-2's triggers; (f) RT-16 injects a crash after every layout step and between the exchange and
the journal write. (`04` CR6-C-7.)

---

## RV6-C-M3 — MEDIUM (carried) — the per-project record's identity is unsound under ordinary repository duplication

**Statement (D).** The per-project record carries E10 downgrade detection (highest installed sequence), the project-strength
vector and the held registration. Its identity is stated three ways:
- `20` §9: "per `(repository path, project_trust_id)`";
- `24` §8: one file `projects/<project_trust_id>.json` holding "repository paths" (plural);
- `18` §5.1 and `27` bind journals and confirmations to `project_trust_id` **and** repository path.

`project_trust_id` is a field of the Git-tracked, A2-writable lock (`08` §3), so every clone, `git worktree`, archive, fork
and "template repository" copy carries it.

**Executed fact (E)** (`ptid-duplication.json`): R6, a second machine, a clone, a `git worktree add` and a `git archive`
extraction all carry the same `project_trust_id` at different repository paths.

**Failure scenarios.**
- *Keyed by (path, id).* A developer whose machine recorded the strength vector and sequence 11 adds a worktree, moves the
  checkout, bind-mounts it into a container at another path, or clones a second copy. At the new path there is no record, so
  an A2-delivered overlay weakening or eligible older release is accepted there **silently**. `26` §8 LR-2 bound (2) ("reported
  on every machine that recorded the vector") and LR-4 ("a machine with no record") are therefore overclaimed.
- *Keyed by id.* Two different projects that share an id (a fork or a template-repository copy) share one record on a
  machine: an install or gated overlay change in project B re-records the vector and raises the sequence that project A's
  detection relies on, so A's later weakening is undetected, or A is refused `downgrade_without_transaction` (availability).

**Why MEDIUM.** Either reading converts a recorded machine into fresh-machine behaviour, an accepted residual (LR-4, RR-2); no
trust is granted beyond what a fresh clone accepts. The bound is misstated and the identity rule is unsound, but a bound rule
closes it.

**Correction direction (carried).** Key the record by `project_trust_id` with a set of repository paths **and** an identity
the repository writer cannot copy into an unrelated project (for example the root commit plus the first-install transaction
id recorded locally); a known id at a new path inherits the strongest recorded vector and highest sequence and is reported
(`PROJECT_PATH_ADDED`); the same id with a different repository identity is reported and fails closed for gated operations
(`PROJECT_TRUST_ID_COLLISION`); restate LR-2 (2) and LR-4 per record identity, not per machine. RT-99 and RT-118 extended to a
worktree, a moved checkout, and a fork on one machine. (`04` CR6-C-8.)

---

## RV6-C-M4 — MEDIUM (carried) — contradictory re-record rules at install commit can discharge pending obligations

**Statement (D).**
- `19` §9 item 3: a non-empty weakening list needs the `weakening` trust gate before commit; item 4: "After commit, the vector
  is re-recorded from the committed effective inputs." `18` §4, phase `verified`: "strength vector re-recorded over effective
  policy; held registration recorded", then "VTS per-project record updated".
- `26` §6 item 3: "`kernel reinstall`, update and recover restore the PPS and occupation entries, but never the check. Only the
  gate re-records the vector." `20` RB-3: reinstall "never clears `PROJECT_STRENGTH_WEAKENED`". `20` §8 item 4: "Each remedy is
  an install transaction. It restores PPS and occupation entries, never project strength: the strength check remains until
  its trust gate."
- `19` §2 item 3 and §10.6: an explained reduction applies to a project holding the stronger registration only after its
  `policy_lowering` gate. `34` R-CON-5: a security-classified registration change is listed "on every machine whose
  per-project record holds an earlier registration, and security-relevant use of the new release waits for that gate". `24`
  §8 lists the record's fields as the installed sequence and CI and the "held Trust Policy registration"; it names no field
  for a pending gate.

**Failure scenario (the unsafe reading).** After LR-2 (occupation removed, legacy CIT drops an overlay classification), a
recorded machine reports `PROJECT_STRENGTH_WEAKENED`. The operator runs the documented remedy `gov kernel reinstall`, an
install transaction. Under `20` §8 it commits without the gate; under `19` §9 item 4 and `18` §4 the vector is then re-recorded
from the weakened overlay, and the report disappears: the weakened configuration is treated as valid. Likewise an update
commits, the record's installed CI and held registration advance at `verified`, and on the next unit of work no record "holds
an earlier registration", so the `policy_lowering` or `registration_change` gate is never listed.

**Why MEDIUM.** The texts contradict each other; the safe reading (remedies commit with failing requirements retained; pending
gates survive the record update) is what RT-81 and RT-167 assert, so a conforming implementation is testable. A bound rule
removes the unsafe reading without a trust-relationship change.

**Correction direction (carried).** State one rule: a re-record never drops a failing requirement unless the `weakening` or
`project_strength` gate accepted it; a pending `policy_lowering` or `registration_change` obligation is itself a per-project
record field that only its gate clears, and no install transaction (update, `kernel reinstall`, `update --apply` from
`PARTIAL`, recover exchange-back, `init --force`) advances the held registration or clears the obligation. RT-81 and RT-167
extended across each remedy and across a completed update followed by a second unit of work. (`04` CR6-C-9.)

---

## RV6-C-M5 — MEDIUM (carried) — the verifier trust store's location and owner are specified two incompatible ways

**Statement (D).**
- `17` §4 and `24` §8: the Verifier Trust Store is `<account-home>/.local/state/gov/trust/<trust_root_id>/`, resolved from the
  account database, writable by the same OS user; it holds anchors, high-waters, per-project records and confirmations.
- `31` R-ADM-7′: the admission record is written "only inside the verifier trust store for the lineage, as
  `vts-<lineage prefix>/admissions/<binary digest>.json`"; GB-1′ honours it "only when the record is held in the protected
  verifier trust store location that `gov-admit` writes"; GB-4′ requires, for C3 and every anchoring ceremony, that "the
  executable, the admission record and every ancestor directory" are not writable by the governed account.
- `06` §3 and `31` §7 (M2): a CI image "writes a root-owned store and admission record … and runs jobs as another user".
- `31` R-ADM-8′: first admission is decided on "the store"; re-admission "keeps the store: anchors, clock and accepted-TBM
  high-waters, per-project records, earlier admission records"; AD-2's bound is the fresh store at first admission.

A record the governed account cannot write cannot live in a store in that account's home that the governed binary writes. So
either (i) records are in the account VTS, GB-4′ fails on every installation, and C3 and `confirm-state` "on a protected
installation" (`06` §3 step 2) are unreachable; or (ii) there are two stores, and first-admission detection, the move-aside and
"keeps anchors, high-waters, per-project records" apply to a root-owned admission store that holds none of those, while a root
`gov-admit` never examines or moves aside the governed account's VTS, so AD-2's fresh store does not reach it. The pack states
neither. The reference executor, ADM6 and AR-0017's `admtx6` model one directory holding both, so none tests the split.

**Why MEDIUM.** Reading (i) fails closed (refusal); under reading (ii) the pre-admission VTS planted by same-account code
survives admission, which same-account code after admission can equally produce (RS-3). Defining two stores and their rules
is a specification change that alters no trust relationship.

**Correction direction (carried).** Specify the protected admission store (location per platform, owner, write path) and the
account VTS separately; state which store R-ADM-8′'s first-admission test, move-aside and preservation apply to, and that a
first admission also moves aside the governed account's VTS for the lineage (AD-2); align GB-1′/GB-4′, `06` §3, `17`, `24` §8
and the reference executor; RT-139, RT-170 and RT-171 run with a root-owned admission store and a non-root job account.
(`04` CR6-C-10.)

---

## RV6-C-L1 — LOW (carried) — `.git/info/attributes` overrides the trust `.gitattributes` member

**Statement (D, E).** Revision 6 adds `governance/trust/.gitattributes` = `* -text\n` to the trust top-level entry set
(`18` §9.1, `26` §2). With the member, `core.autocrlf=true`, a project `* text=auto` with `core.eol=crlf`, and a project
`* text eol=crlf` clone keep the kernel bytes and are `COMPLETE` (`gitops6` `AUTOCRLF`, `TEXTAUTO_EOLCRLF`, `TEXTEOL_CRLF`: no
CRLF on disk). A repo-root `.gitattributes` cannot override the member (the member is deeper); a kernel-level
`.gitattributes` converts but is an extra kernel file → `kernel_content_mismatch` (`attrprec6`). The one override is the
out-of-tree `.git/info/attributes` (`gitops6` `INFOATTR`, configuration persisted): `PARTIAL(kernel_content_mismatch,
foreign_trust_entry(.gitattributes_content))`, `KERNEL_TAMPERED`. **RV5-C-M1/RV5-M6 is closed as a class**; what remains is
a fail-closed availability condition the pack states exactly. (`04` CR6-C-1.)

---

## RV6-C-L2 — LOW (carried) — the transaction-area foreign-artefact scan does not exclude the `done/` archive

**Statement (D, E).** `18` §4 moves a finished transaction to `trust-tx/done/<TX>` and deregisters it; `18` §5.1 reports any
journal not VTS-open as `FOREIGN_TRANSACTION_ARTEFACT` (doctor HIGH). Read literally, every completed transaction's
`done/<TX>/journal.json` is reported HIGH on a healthy machine (`state_r6` on R6 and R6CRASH). Both readings are fail-safe
(a `done/` journal is never honoured; the state stays `COMPLETE`). State the scan scope. (`04` CR6-C-6.)

---

## RV6-C-L3 — LOW (M, carried) — `gov-admit` reference edges

1. A store holding anchors but no admission record is treated as first admission and moved aside (`admtx6` T3a); admission
   precedes anchoring (`31` R-ADM-9), and after a crash during the move-aside the re-run makes a fresh store and reads no stale
   anchor (T7). Fail safe (`UNANCHORED`).
2. `gov_run` honours a record by `binary_digest` across every `vts-<16>` store under the record root, without binding the store
   to the binary's own lineage although GB-1′ reads "for the lineage" (T8). Planting it needs the protected root (A3/RS-3);
   lineage is enforced separately (`TRUST_ROOT_LINEAGE_MISMATCH`). The reference also names the store by `lineage[:16]`,
   which is `sha256:` plus 9 hexadecimal digits; `31` does not fix the prefix length.

Clarify R-ADM-8′ for a store without a record, bind honoured records to the binary's lineage, and fix the store-name length.

---

## RV6-C-L4 — LOW (carried) — a third litter location, inside the overlay, stays `COMPLETE` unnamed

**Statement (E, D).** Revision 6 restates LP-1s (`26` §4) and D-0008 rule (12) and names the subtree `adopt baseline` /
`migrate baseline` litter under `governance/spec` and `governance/views/spec` as `COMPLETE`, "inert: nothing reads it",
named by doctor (RT-176). The same commands from `governance/overlay/` write
`governance/overlay/spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml`; state `COMPLETE`, classifications intact, no report
(matrix: 8 rows, 4.1.2–4.1.5). The overlay is read: under the Overlay Surface (`overlay_surface.default: deny`, `23` §11.2)
the file is an unclassified overlay file — granting nothing, but a weakening candidate reported `PROJECT_STRENGTH_WEAKENED`
on recorded machines (fail safe). "Nothing reads it" is not accurate here, and RT-176 does not cover it. Name it. (`04`
CR6-C-3.)

---

## RV6-C-L5 — LOW (carried) — evidence and text accuracy

1. **LAY6 `INFOATTR` row does not exercise its condition.** Committed and reproduced state `COMPLETE`, under its own note
   "stated condition: PARTIAL with kernel_content_mismatch": the row passes `core.autocrlf` as a command-level `git -c` on
   `clone` (not persisted) and re-materialises without it. The override claim holds on ATTR6 and on AR-0017 `gitops6`
   `INFOATTR`; the LAY6 row supports nothing. (LAY6's `AUTOCRLF` row converts during the clone's own checkout and is effective.)
2. **"30,735 writing rows"** (`18` §9 evidence, `22` LAY6 row): 30,735 is the total row count (30,450 executed); LAY6's
   writing-rows file holds 4,333 rows. `26` §4 ("30,735 rows") is right.
3. **`props6`** input: the committed `props6.json` (540 rows touching trust/occupation, 30,450 active) was computed over all
   rows including 26 L0-control rows; over the writing-rows file it is 514 and 4,333. Counterexamples 0 either way.
4. `20` §5 recovers a `committed (lock written)` phase that `18` §5.3 does not define (the lock is written during staging).
5. `08` §2: "Every file under `governance/trust/` except `FORMAT`, `framework.lock` and `development.json` is signed" omits
   the unsigned `.gitattributes` member.

(`04` CR6-C-11.)

---

## RV6-C-L6 — LOW (carried) — binary rollback and the accepted-TBM high-water

**Statement (D).** `20` (revision-6 header) and `31` R-ADM-7′ state that a rollback to a previously admitted binary keeps that
binary's record; RT-170 asserts only that the rollback "passes GB-1′". `09` R-ART-2 and `25` AP-8 refuse trusted operations
for a binary whose Trust Base Manifest is below the verifier trust store's accepted-TBM high-water (`BINARY_T0_ROLLBACK`),
and re-admission keeps that high-water (R-ADM-8′). After binary N+1 with a higher TBM has run, rollback to N passes GB-1′ and
is then refused above C0 until a root-signed `bootstrap.accepted_tbm_reset`. Fail closed; state the consequence in `20`/`31`/
`21` and extend RT-170. (`04` CR6-C-12.)

---

## Non-findings confirmed (executed)

- **R2-H4 remains closed as a class.** Matrix: 62,036 rows; 592 trust/occupation-writing rows, none `COMPLETE` without
  `KERNEL_TAMPERED`; LP-1r 2,492 root-anchored rows, 0 project writes; 0 Git-op trees written into `COMPLETE`; LAY6 reproduced.
- **The closed entry sets fail closed under structural tampering** (`struct6`): occupation entry → symlink or wrong type, a
  symlink below `governance/trust/`, a deleted or altered `.gitattributes` member, a kernel edit/add/remove, a foreign file in
  `state/` or at the trust top level, an occupation removal. A hard-linked occupation entry stays `COMPLETE` at the layout
  level; VU-12 is the use-time guard (`04` C-4).
- **§9.2 working-directory refusal** covers `governance/trust/**`, the occupation directory and the transaction area,
  including `done/` (`discover_r6`); D-0008 rules (10) and (12) are restated accordingly.
- **Re-admission and concurrent admission** on the reference executor: store kept, earlier record kept, one store under eight
  concurrent admissions (`admtx6`; ADM6 reproduced).
