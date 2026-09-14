# 00 — Independent compatibility & transaction review (C) of RoT-1 revision 7

| | |
|---|---|
| Run | AR-0021, role `rot-reviewer-compat-transaction` |
| Reviewed | RoT-1 revision 7, commit **`d07d200ac08a52c45071d33074e20cc62fbcc26e`** (`release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md`) — one concrete certified profile CP-1 |
| Rejected prior | revision 6 `4106885`; consolidated review r6 `ab6b1f8` (synthesis adjudication governs its panel) |
| Handoff | `HO-0021`; owner requirements `OWNER-DESIGN-REQUIREMENTS-0001` and (received mid-run) `OWNER-DESIGN-REQUIREMENTS-0002` |
| Branch / base | `phase1/rot1-r7-review-c` from `7e50c6e` |
| Date | 2026-09-14 |
| **Role verdict** | **`BLOCKING_FINDINGS_PRESENT`** (not the architecture verdict; the synthesis reviewer issues that) |

## Scope

Compatibility and transactions (Phase 1 protocol §5 C; `HO-0021` §2–§6) attacked against the concrete profile CP-1 as
specified, including its real combinations and exclusions: the real 4.1.2–4.1.5 binaries over their full command registers
(derived twice, help + source) on the revision-7 layout, from root and every subdirectory depth, with and without `--root`
and environment variables; the first-install layout migration and its crash window (now claimed journalled); `init` on
ABSENT trees holding an overlay; per-project record identity under worktrees, moves, second clones, forks and template
copies; the two stores, first-admission determination and planted files; admission and re-admission as transactional state
(24-hour state age, 90/7-day anchors, expiry to C0, record expiry, high-water preservation, clock high-water, rollback to
admitted binaries); offline media handling and the diagnostic level without fresh state (OWNER-DESIGN-REQUIREMENTS-0002
OT-1); layout durability through clone/checkout/pull/stash/clean/sparse/shallow/archives/line-ending/re-encoding/case;
rollback and recovery; TOCTOU; concurrent gov processes; cross-machine and cross-device behaviour; symlink/hard-link/rename
tricks; corrupted/foreign journals; crash recovery at every step; long-lived processes; write confinement; whether excluded
modes are absent from the transactional/installation surface; conformance with the owner selections touching
compatibility/transactions (OP-3, OP-7, OP-13 media, OP-14, OP-15) and OT-1/OT-2; and D-0008 field state. Whole-tree
before/after digests decide "no write", never named paths.

## Independence and disclosures

- **Authored before by this session:** nothing — no RoT-1 revision, specialist proposal, prior review, the other panel
  review (reviewer B), the product owner's requirements, or the synthesis. I did not read reviewer B's output, other
  branches (`git branch -a` / `git log --all` not used), other worktrees, other scratch directories, session or agent
  transcripts, or task-output files.
- **Orchestration files read (per `HO-0021` §6):** `HO-0021`, `HO-0001`, `AGENT_RUNS/README.md`, and
  `GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` with its `.yaml` index.
- **Mid-run coordinator message (disclosed).** The coordinator sent a routing message that the product owner had resolved
  OT-1 and OT-2 as binding requirements, and permitted me to read **exactly two** files at commit `30542e5a…`:
  `GATES/OWNER-DESIGN-REQUIREMENTS-0002.md` and its `.yaml` index. I read those two files with `git show` and nothing else
  from that commit (not the ledger, state, checkpoints, run records or other handoffs). I treated OT-1/OT-2 as resolved
  owner requirements and attacked the resulting design; RV7-C-H1 and RV7-C-M1 report deviations from OT-1.
- **Treated as claims to test:** the response matrix (`22`), crashmig7, ADM7, CUR7, PPR7, the re-run `matrix6`, and every
  pack evidence file. Each was reproduced or independently re-derived; results in `evidence/`.
- **Disclosures.** The host context included the user's auto-memory index (one-line summaries of earlier Governance OS
  reviews); no memory file was opened. The harness saved some of this session's own large command outputs under a
  `tool-results` path in `~/.claude/projects/`; none was opened (sources re-read from the worktree). `register7.py`,
  `register6.py` and `design7.py` ran `git show` at the four legacy release commits and read pack blobs at `d07d200` in the
  read-only review worktree. No helper sessions. Nothing was written outside this output directory, `AR-0021.report.yaml`
  and the scratch root.

## Hygiene

All probes ran in scratch under `env -i` with `GOV_*` stripped (set only where a probe tests it), `HOME`/`XDG_*`/
`GOV_KERNEL_CACHE` in scratch, and Git with `GIT_CONFIG_NOSYSTEM=1`, `GIT_OPTIONAL_LOCKS=0`, `core.hooksPath=/dev/null`. The
canonical checkout and every other worktree were never written. Legacy binaries were copied read-only. `evidence/README.md`
has the full method and the independence of `c7lib.state_r7` from every prior instrument.

## Prior-finding status (`HO-0021` §3)

| Finding | Status | Basis |
|---|---|---|
| **R2-H4** pre-RoT binaries damage RoT-1 projects | **CLOSED as a class** (confirmed) | matrix6 reproduced (62,036 rows, R2-H4 0 violations, LP-1r 0 project writes, 0 Git-op elevation); matrix7 independent revision-7 matrix (§05); struct7 (every trust/occupation/member tamper not-`COMPLETE` under every reading); gitops7 (45 operations) |
| **RV6-M3** first-install migration crash; `init` on ABSENT with an overlay | **NARROWED (not fully CLOSED)** | crashmig7 reproduced (21/22 no-op-recovery prefixes roll back to legacy); R-INIT-9 present and refuses over an existing overlay (RV6-D-A10 reproduced). **But** `git clean -fdx` in the crash window removes the untracked overlay and defeats R-INIT-9 → **RV7-C-M4**; the first-install honouring gate is unreachable → **RV7-C-M3**; roll-forward is a stub → **RV7-C-M5** |
| **RV6-M4** per-project record identity | **NARROWED (not CLOSED)** | PPR7 reproduced, but it uses opaque labels; ident7 shows **no realizable** identity satisfies the five named cases → **RV7-C-M2** |
| **RV6-M5** re-record rules clear strength reports / pending gates | **CLOSED (as a class, model level)** | PPR7 reproduced byte-identical: remedies keep the failing requirement and the pending gate; only the gates clear them; the remedy-re-record mutant is detected. Carried as an implementation requirement (CR6-C-9) |
| **RV6-M6** two stores; planted unsigned file | **CLOSED for the attack direction; NARROWED for the defence direction** | ADM7 A07 reproduced (a planted account-store record/anchor/record/confirmation does not survive the first-admission move-aside). **But** the same move-aside discards a **legitimate** surviving account-store high-water after protected-store loss → **RV7-C-M1** |
| **RV6-L5** accepted-TBM high-water at re-admission and use | **CLOSED** | CUR7 reproduced (re-admission below the high-water refused; R-ART-2 at use; floors never lowered) |
| **RV6-L6** out-of-project ignore sources | **CLOSED as a class (fail closed)** | gitops7 `GLOBALEXCL`/`INFOEXCL`/`RM_CACHED_ADD_ALL` → `PARTIAL(occupation)` |
| **RV6-L7** `.gitattributes` member; `.git/info/attributes` override | **CLOSED as a class (fail closed)** | gitops7/attrprec6: the member defeats every in-tree conversion source; `.git/info/attributes` and `working-tree-encoding` (from three sources) → `PARTIAL`/`KERNEL_TAMPERED` |
| **RV6-L8** transaction-area foreign-artefact scan / `done/` scope | **CLOSED in specification** | struct7 (`done/` archive not reported; planted/tracked journals `FOREIGN`); spec-only (RT-201) |
| **RV6-L9** `gov-admit` reference edges (store name, lineage) | **CLOSED** | ADM7 L9 reproduced (64-hex store name; a record of another lineage not honoured) |
| **RV6-L10** overlay-litter naming | **NARROWED** (doctor spec-only) | matrix6 reproduced (8 `governance/overlay/spec` rows `COMPLETE`, inert) |
| **RV6-L11** evidence/text accuracy | **CLOSED** (the `committed` phase withdrawn; totals restated) | design7 (the `20` §5 `committed` row absent) |
| **C-2** cross-device transaction area | **OPEN** (carried; specified, not executable) | `18` §3; RT-123 |
| **C-3** doctor names stray artefacts | **OPEN** (carried; scope extended by RV7-C-M3/M4) | `18` §9; RT-124 |
| **C-4** type by `st_mode`; `st_nlink` at use | **NARROWED** (holds in the state model; use-time guard spec-only) | struct7 (a hard-linked occupation file stays `COMPLETE` at the layout level; VU-12 use-time) |
| **C-5** full-register RT-50 on a genuine install | **OPEN** (carried; matrix6/matrix7 are the independent analogue) | `12` RT-50 |
| **C-6** doctor names nested lock / sparse roots | **NARROWED** (sparse → `PARTIAL(occupation)` executed; doctor naming spec-only) | gitops7 sparse cases |

## Owner-requirement conformance (compatibility/transaction scope)

| Requirement | Determination | Basis |
|---|---|---|
| **OP-3** Mode A always-gate | **Conforms.** Every C3 transition needs the local trust gate; decision pins exclude the C3 kinds. | design7 (`27` gate set; `24` C3 list) |
| **OP-7 (a)** anchored-only; 90/7-day anchors; 24-hour production currency; expiry → C0 | **Deviation at use-time (RV7-C-H1).** The **anchor** ceilings and admission 24-hour age (FC-9) conform; the **running-mode currency proof** bounds the event, not the state, so production C3 runs on a state up to 90 days stale. | cur7x; adm7x X7 |
| **OP-13 (b) media** two sources, byte-identical, both required; media is identity, not a longer freshness window (OT-1) | **Admission conforms; running mode deviates.** FC-9 refuses admission on media > 24 h (cur7x M2). But OT-1's "must NOT enter C1-C3 based on stale state" is violated in running mode (RV7-C-H1). | cur7x |
| **OP-14 (b)** all records expire; re-admission preserves the high-water | **Deviation (RV7-C-M1).** Records expire (ADM7 X14); the high-water is preserved on re-admission **when both stores are present**, but a first admission after protected-store loss discards a surviving account-store high-water. | adm7x X2; ADM7 |
| **OP-15 (a)** revoked binary read-only | **Conforms.** C0-R only (ADM7 X15). | ADM7 |
| **OT-1** (OWNER-DESIGN-REQUIREMENTS-0002) offline media identity vs 24-hour freshness; high-water never lowered; no C1–C3 on stale state | **NOT met.** RV7-C-H1 (C3 on stale media state) and RV7-C-M1 (high-water discarded). The **admission** path conforms (FC-9). | cur7x; adm7x |
| **OT-2** (OWNER-DESIGN-REQUIREMENTS-0002) no interim certification; NOT CERTIFIED until non-circular criterion; exact label | **Compatibility surface conforms; carried label/criterion gap (RV7-C-L4).** No target is certified; first contact refuses an uncertified target; the label and the executable non-circular criterion are carried. The trusting-trust evidence route is reviewer-B scope. | design7; struct7/matrix `TARGET_NOT_CERTIFIED` |
| **Excluded modes** absent from the transactional/installation surface | **Conform.** The reference executor refuses a platform-package/witness/single-source/mode-B/OP-7(d) input (`PROFILE_MODE_EXCLUDED` / `PROFILE_NONCONFORMANT`); no `fc-procedure` command; unanchored → C0. | cur7x R6; adm7x X7; design7 EX rows |

## D-0008 / ARCH-0002 / D-0007 state (`HO-0021` §2b)

`design7.json` (parsed at `d07d200`): **D-0008** `status: PROVISIONAL`, `proposal_state: PROPOSED`,
`approval_state: PENDING_OWNER_HUMAN_DECISION_GATE`, `in_effect: false`, `human_approved: false`, `chosen_option` **absent**;
**D-0007** `status: ACTIVE`; **ARCH-0002** `status: PROVISIONAL`, `proposal_state: PROPOSED`, `in_effect: false`. All
required states hold. This review approves nothing.

## Summary of results

- **Legacy containment holds on the revision-7 layout.** matrix6 reproduced (62,036 rows, R2-H4 0 violations); matrix7
  independent revision-7 matrix (§05); struct7, gitops7 (45 operations). R2-H4 is **CLOSED as a class**.
- **Admission-store transactional state** behaves as revision 7 states on the reference executor (ADM7, CUR7 reproduced),
  **with two gaps:** a first admission after protected-store loss discards a surviving high-water (RV7-C-M1), and the
  running-mode currency proof does not bound the state's age (RV7-C-H1).
- **Transaction-state gaps (MEDIUM, carried):** RV7-C-M2 (record identity unrealizable for all five cases), RV7-C-M3
  (first-install journal honouring unreachable), RV7-C-M4 (`git clean -fdx` defeats R-INIT-9), RV7-C-M5 (roll-forward
  unproven / in-memory ARO).
- **One HIGH (blocking):** RV7-C-H1 — a running admitted air-gapped / long-offline machine performs production C3 on a Trust
  State up to 90 days stale that omits later revocations, contradicting the pack's RS-1b bound and
  OWNER-DESIGN-REQUIREMENTS-0002 OT-1.
- **LOW:** RV7-C-L1…L4.

**Verdict: `BLOCKING_FINDINGS_PRESENT`.** One HIGH (RV7-C-H1). Every MEDIUM is stated with a bound, testable carried
requirement (`04`); RV7-C-M1 carries a trust-relationship note the synthesis should weigh (it may escalate if protected-store
loss is treated as ordinary). This is not the architecture verdict; the synthesis reviewer issues that.

## Output files

| File | Content |
|---|---|
| `00-REPORT.md` | this report |
| `01-FINDINGS.md` | RV7-C-H1, RV7-C-M1…M5, RV7-C-L1…L4: statement, evidence class, failure scenario, severity, correction direction |
| `02-HELDOUT-ATTACKS.md` | the RV7-C-A01…A25 register |
| `03-RESIDUALS.md` | residual criteria and determinations |
| `04-CARRIED-REQUIREMENTS.md` | CR7-C-1…9 and the carried CR6-C / C-2…C-6 items with acceptance tests |
| `05-PRE-ROT-MATRIX.md` | registers, trees, the executed matrix, properties, durability, the reproduction cross-check |
| `evidence/` | probes, outputs, reproduction, `REVIEWED-CONTENT-DIGESTS.txt`, README |
