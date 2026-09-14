# HO-0003 — Handoff to independent reviewer C (compatibility and transactions), RoT-1 revision 3

| Field | Value |
|---|---|
| Handoff | HO-0003 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh independent compatibility and transaction reviewer, run `AR-0003` (role `rot-reviewer-compat-transaction`) |
| Completed stage | RoT-1 revision 3 authored by architect run `AR-0001` |
| Architecture under review | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at commit **`ca77a431418bd6b349f465aa2521ca43bccfd5a6`** |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r3-review-c` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/review-r3-c` |
| Your output directory | `release/root-of-trust/4.1.6-review-r3/C-compat-transaction/` |

You work in parallel with reviewer B (trust and security). You must not see B's work, and B must not see yours. A
separate synthesis reviewer will consume both reports and issue the architecture verdict. **You do not issue
`ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED` or `…_REJECTED`.**

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Revision 3 (under review) | as above | `ca77a431418bd6b349f465aa2521ca43bccfd5a6` |
| Revision 2 (rejected) | same paths | `d37b05cc83741821aad023e5845ecfeb1a396f4c` |
| Review of revision 2 | `release/root-of-trust/4.1.6-review-r2/` (all files, evidence P1–P4, especially `06` and P3/P3b) | `e5a6b8aa39d2a36311489418506d911df2587722` |
| Review of revision 1 | `release/root-of-trust/4.1.6-review/` | `1c6027c18822543d6927d9906b9efa4f7a54ed4e` |
| Implementation the design governs | `runtime/` (`init`, `update`, `recovery`, `kernel`, `kernel_trust`, `migrations/`, `util`), `cli/`, `framework/`, `release/releases/4.1.2`–`4.1.5` | at `ca77a431418bd6b349f465aa2521ca43bccfd5a6` (unchanged since 4.1.5 `da9c851`) |
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

## 3. Required work

1. **Prior findings.** Determine the status of R2-H4, R2-M7, R2-M8, R2-M9, R2-L2 and R2-L3: `CLOSED`, `NARROWED` or
   `OPEN`, each with evidence. Also report the status of any transaction-related part of R2-M1 and R2-M10.
2. **Independent pre-RoT matrix.**
   - Derive each legacy binary's full command register yourself, from its own CLI and source.
   - Run every command of 4.1.2, 4.1.3, 4.1.4 and 4.1.5 against a project laid out exactly as revision 3
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
5. **Author new held-out attacks** `RV3-C-A01…` that are not in the pack's acceptance plan. Execute each where
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
- `02-HELDOUT-ATTACKS.md`: the RV3-C register.
- `03-RESIDUALS.md`
- `04-CARRIED-REQUIREMENTS.md`
- `05-PRE-ROT-MATRIX.md`: summary of the full executed matrix.
- `evidence/`: scripts, raw outputs, `REVIEWED-CONTENT-DIGESTS.txt` (at `ca77a431418bd6b349f465aa2521ca43bccfd5a6`), README.

Then write `release/orchestration/phase-1/AGENT_RUNS/AR-0003.report.yaml` (schema: `AGENT_RUNS/README.md`).

## 6. Constraints

- **Independence.**
  - You did not author any RoT-1 revision or prior review.
  - Do not read reviewer B's output, other branches or other worktrees (`git branch -a`, `git log --all`, other scratch
    directories).
  - Under `release/orchestration/`, read only this handoff, `HO-0001` and `AGENT_RUNS/README.md`.
- **Writes.** Only your output directory and your report file. Never modify product source, the pack, D-0008,
  ARCH-0002, prior reviews, verification evidence or released payloads.
- **Probes.** Scratch only; never the canonical checkout `/home/usain/Dynamic-Agentic-Engineering-OS`. Strip `GOV_*`
  from child environments and point `GOV_KERNEL_CACHE` into scratch. Scratch root:
  `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0003/`. Legacy binaries are read-only; copy them if you need to.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Commits.** Commit the output directory first:
  `Independent compatibility/transaction review (C) of RoT-1 revision 3 (ca77a43): <verdict>`. Then commit
  your report separately. End each message with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
  Leave the worktree clean.

## 7. Forbidden assumptions

- That the architect's P3 evidence or response matrix is correct.
- That a named-path digest shows no write happened.
- That a layout that exists in the author's working tree reaches every clone.
- That reviewer B covers anything you skip.
- That a pre-RoT binary reads any RoT-1 file before it acts.
