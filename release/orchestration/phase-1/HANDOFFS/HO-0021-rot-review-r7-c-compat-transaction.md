# HO-0021 — Handoff to independent reviewer C (compatibility and transactions), RoT-1 revision 7

| Field | Value |
|---|---|
| Handoff | HO-0021 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh independent compatibility and transaction reviewer, run `AR-0021` (role `rot-reviewer-compat-transaction`) |
| Completed stage | RoT-1 revision 7 authored by architect run `AR-0019` |
| Architecture under review | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at commit **`d07d200ac08a52c45071d33074e20cc62fbcc26e`** |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r7-review-c` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/review-r7-c` |
| Your output directory | `release/root-of-trust/4.1.6-review-r7/C-compat-transaction/` |

You work in parallel with reviewer B (trust and security). You must not see B's work, and B must not see yours. A
separate synthesis reviewer will consume both reports and issue the architecture verdict. **You do not issue
`ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED` or `…_REJECTED`.**

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Revision 7 (under review) | as above | `d07d200ac08a52c45071d33074e20cc62fbcc26e` |
| Revision 6 (rejected) | same paths | `4106885dadebac55596067a2586cf4d3097fc025` (`git diff 4106885dadebac55596067a2586cf4d3097fc025 d07d200ac08a52c45071d33074e20cc62fbcc26e -- release/root-of-trust/4.1.6 spec docs/DECISIONS.md`) |
| Consolidated review of revision 6 (synthesis adjudication governs over its panel) | `release/root-of-trust/4.1.6-review-r6/` (all files and evidence) | `ab6b1f8fab5f9f54261a01e5a0df431a13e9ddcd` |
| Earlier reviews | `release/root-of-trust/4.1.6-review*/` | in history |
| Implementation the design governs | `runtime/` (`init`, `update`, `recovery`, `kernel`, `kernel_trust`, `migrations/`, `util`), `cli/`, `framework/`, `release/releases/4.1.2`–`4.1.5` | at `d07d200ac08a52c45071d33074e20cc62fbcc26e` (unchanged since 4.1.5 `da9c851`) |
| Real legacy binaries | `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}` | sha256 in `ORCHESTRATOR_STATE.yaml` `infrastructure` |
| Legacy source for each binary | tags `v4.1.3-rc1` (`26ab5b6`), `v4.1.4-rc1` (`47d8394`), `v4.1.5-rc1` (`da9c851`); 4.1.2 at `8ad06be` | `git show <commit>:<path>` |

The architect's response matrix (`22`) and the pack's own evidence are **claims** to be tested. They are not findings.

## 2. Attack surface (Phase 1 protocol §5 C)

Attack at least:
- 4.1.2–4.1.5 binaries;
- the new-format path layout;
- rollback and recovery;
- snapshots;
- partial installs;
- TOCTOU;
- concurrent operations;
- cross-machine behaviour;
- symlink and path tricks;
- corrupted state;
- crash recovery.

The owner's binding requirement for this area is in `HO-0001` §3.4 (legacy-binary damage containment as a class). The
requirement is: a pre-RoT binary must not be able to silently mutate the new kernel or trust state into a state it then
treats as valid. The protected set includes kernel paths, legacy lock paths, trust paths, rollback paths, reinstall
paths, init-force paths and migration paths.

## 2b. Owner design requirements and the concrete certified profile

- **The profile under review.** Revision 7 implements one concrete certified production profile per the product
  owner's binding design requirements in `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md`. The
  verbatim text governs; the `.yaml` beside it is a derived index. These are design inputs, not approval of D-0008.
- **Attack the configuration as specified**, including its real combinations and its exclusions. An excluded mode that
  remains reachable, accepted by a schema or verifier, or selectable by a Trust Policy is a finding. The excluded modes
  are:
  - a witness service;
  - helper-machine or script admission;
  - OP-13 (c) "either suffices";
  - a platform package-signing root;
  - mode B;
  - clock or grace-period trust;
  - unanchored governed mutation.
- **Check conformance.** Any place where the architecture deviates from, weakens, or silently reinterprets an owner
  selection is a finding.
- **Do not reopen owner parameters** merely because another design is possible. If an attack shows a selected parameter
  is insufficient, or contradicts a security invariant, report the precise consequence. Then classify whether closing it
  needs an engineering correction or a genuinely new owner trade-off.
- **Check D-0008's state.** D-0008 must remain `status: PROVISIONAL`, `proposal_state: PROPOSED`,
  `human_approved: false` and `in_effect: false`, and D-0007 must remain ACTIVE. Any other state is a finding.

## 3. Required work

1. **Prior findings.** Determine the status of R2-H4 (confirm it remains CLOSED as a class), RV6-M3 (first-install migration crash; `init` on `ABSENT` with an overlay), RV6-M4 (per-project record identity), RV6-M5 (re-record rules), RV6-M6 (two stores; planted unsigned file), RV6-L5…L11 and C-2…C-6: `CLOSED`, `NARROWED` or `OPEN`, each with
   evidence. Re-run the prior review's decisive compatibility and transaction probes (review r6 `C-compat-transaction` probes (`matrix6`, `register6`, gitops, crash, struct, attribute and admission probes) and RV6-C-A01…A19, the `D-synthesis` probes within compatibility scope, and the architect's crashmig7, ADM7 and re-run `matrix6` evidence as claims) against
   revision 7 as written.
2. **Independent pre-RoT matrix.**
   - Derive each legacy binary's full command register yourself, from its own CLI and source.
   - Run every command of 4.1.2, 4.1.3, 4.1.4 and 4.1.5 against a project laid out exactly as revision 7
     specifies. Include a legacy update snapshot, a project restricted-classification and realistic prior state.
   - Record before/after digests of the entire project tree, not only named paths.
   - Include commands run from subdirectories, with environment variables a user might set, and after ordinary Git
     operations on the new layout: fresh clone, checkout, stash, clean, sparse or shallow clones, and Windows or
     case-insensitive semantics where the layout relies on file types.
3. **Layout durability.** Test whether the protective layout survives every way a project reaches a machine or is
   modified by ordinary tools and legacy remedies, and whether its loss is detected before harm.
4. **Transactions.** Attack the install, update, rollback and recover state machine:
   - crash at every step;
   - concurrent `gov` processes;
   - partial installs;
   - corrupted or foreign journals;
   - symlinks, hard links, renames and directory swaps;
   - long-lived processes;
   - cross-machine clones mid-transaction;
   - restore from backup.
5. **Author new held-out attacks** `RV7-C-A01…` that are not in the pack's acceptance plan. Execute each where
   feasible.
6. **Residuals.** Judge every residual the architect declares against explicit acceptance criteria.

## 4. Severity and blocking

| Severity | Meaning |
|---|---|
| CRITICAL / HIGH | **Blocking.** Persistent or silent loss of a security control, a legacy or ordinary operation producing a state later treated as valid, or an unrecoverable trust or project state. |
| MEDIUM | **Blocking** only when it cannot be carried as a bound, testable implementation requirement without an architecture change. Otherwise list it as a carried requirement. |
| LOW | not blocking |

## 5. Deliverables (in your output directory only)

- `00-REPORT.md`: scope, method, prior-finding status table, summary, verdict `BLOCKING_FINDINGS_PRESENT` or `NO_BLOCKING_FINDINGS`.
- `01-FINDINGS.md`: statement, evidence class, failure scenario, severity and correction direction (architectural only).
- `02-HELDOUT-ATTACKS.md`: the RV7-C register.
- `03-RESIDUALS.md`
- `04-CARRIED-REQUIREMENTS.md`
- `05-PRE-ROT-MATRIX.md`: summary of the full executed matrix.
- `evidence/`: scripts, raw outputs, `REVIEWED-CONTENT-DIGESTS.txt` (at `d07d200ac08a52c45071d33074e20cc62fbcc26e`), README.

Then write `release/orchestration/phase-1/AGENT_RUNS/AR-0021.report.yaml` (schema: `AGENT_RUNS/README.md`).

## 6. Constraints

- **Independence.**
  - You did not author any RoT-1 revision or prior review.
  - Do not read reviewer B's output, other branches or other worktrees (`git branch -a`, `git log --all`, other scratch
    directories).
  - Under `release/orchestration/`, read only this handoff, `HO-0001`, `AGENT_RUNS/README.md` and `GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` (with its `.yaml` index).
- **Writes.** Only your output directory and your report file. Never modify product source, the pack, D-0008,
  ARCH-0002, prior reviews, verification evidence or released payloads.
- **Probes.** Scratch only; never the canonical checkout `/home/usain/Dynamic-Agentic-Engineering-OS`. Strip `GOV_*`
  from child environments and point `GOV_KERNEL_CACHE` into scratch. Scratch root:
  `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0021/`. Legacy binaries are read-only; copy them if you need to.
- **No transcripts.** Never read, list or search session or agent transcripts or task-output files: anything under `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/*/tasks/` or `~/.claude/projects/`. They hold other roles' work.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Commits.** Commit the output directory first:
  `Independent compatibility/transaction review (C) of RoT-1 revision 7 (d07d200): <verdict>`. Then commit
  your report separately. End each message with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
  Leave the worktree clean.

## 7. Forbidden assumptions

- That the architect's P3 evidence or response matrix is correct.
- That a named-path digest shows no write happened.
- That a layout that exists in the author's working tree reaches every clone.
- That reviewer B covers anything you skip.
- That a pre-RoT binary reads any RoT-1 file before it acts.
