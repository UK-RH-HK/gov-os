# HO-0016 — Handoff to independent reviewer B (trust and security), RoT-1 revision 6

| Field | Value |
|---|---|
| Handoff | HO-0016 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh independent trust and security reviewer, run `AR-0016` (role `rot-reviewer-trust-security`) |
| Completed stage | RoT-1 revision 6 authored by architect run `AR-0015` |
| Architecture under review | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at commit **`4106885dadebac55596067a2586cf4d3097fc025`** |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r6-review-b` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/review-r6-b` |
| Your output directory | `release/root-of-trust/4.1.6-review-r6/B-trust-security/` |

You work in parallel with reviewer C (compatibility and transactions). You must not see C's work, and C must not see
yours. A separate synthesis reviewer will consume both reports and issue the architecture verdict. **You do not issue
`ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED` or `…_REJECTED`.**

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Revision 6 (under review) | as above | `4106885dadebac55596067a2586cf4d3097fc025` |
| Revision 5 (rejected) | same paths | `cdb4e14009bba60bea9b805563c1b60e84f30b4b` (`git diff cdb4e14009bba60bea9b805563c1b60e84f30b4b 4106885dadebac55596067a2586cf4d3097fc025 -- release/root-of-trust/4.1.6 spec docs/DECISIONS.md`) |
| Consolidated review of revision 5 (synthesis adjudication governs over its panel) | `release/root-of-trust/4.1.6-review-r5/` (all files and evidence) | `d1228cb77b9253c90406ab0cc3a8c3bd4b480e64` |
| Earlier reviews | `release/root-of-trust/4.1.6-review*/` | in history |
| Decisions | `spec/decisions/D-0007.yaml` (ACTIVE); D-0008 and ARCH-0002 (PROPOSED) | at `4106885dadebac55596067a2586cf4d3097fc025` |
| Implementation the design governs | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `release/releases/4.1.2`–`4.1.5` | at `4106885dadebac55596067a2586cf4d3097fc025` (unchanged since 4.1.5 `da9c851`) |
| Real legacy binaries | `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}` | sha256 in `release/orchestration/phase-1/ORCHESTRATOR_STATE.yaml` `infrastructure` |

The architect's response matrix (`22`) and the pack's own evidence are **claims** to be tested. They are not findings.
Re-derive or re-execute anything you rely on.

## 2. Attack surface (Phase 1 protocol §5 B)

Attack at least:
- root trust;
- constitutional floors;
- key hierarchy;
- signature purpose;
- binary authenticity;
- replay and freshness;
- first-machine bootstrap;
- revocation;
- downgrade;
- offline operation;
- trust-state monotonicity.

The owner's binding requirements that revision 6 must satisfy are in `HO-0001` §3 (constitutional-floor closure,
new-machine bootstrap, binary and root authenticity) and §4 (forward compatibility). Judge each as a **class**: an
instance fix that leaves the class open is not a closure.

The recurring rejection class is: **a lower-trust input yielding a current, higher-trust fact** (D-0007).

## 3. Required work

1. **Prior findings.** Determine the status of blocking classes BC5-1, BC5-2, BC5-3 and BC5-4 as classes; RV5-H1, RV5-H2, RV5-H3; RV5-M1…M5, RV5-M8, RV5-M9; RV5-L1…L6, RV5-L9; RV5-I1, RV5-I2; and the consequence statements of owner options OP-1…OP-16 (including the first-contact root OP-13 and build-environment OP-16 trade-offs):
   `CLOSED`, `NARROWED` or `OPEN`, each with evidence.
2. **Re-execute prior probes.** Run the prior review's decisive probes (review r5 `B-trust-security` RV5-B-A01…A19, the `D-synthesis` RV5-D probes within trust/security scope (including D-A01, D-A02, D-A04, D-A05 and D-A07), and the architect's CS6 calculator, FA6, ENV6, CON6, SRC6, P4r6, DA03r6, DA07r6, `register_check` and `statements_check` evidence as claims) against revision 6
   as written. You may copy scripts into your evidence directory and adapt them, with attribution. Never edit any
   `release/root-of-trust/4.1.6-review*/` directory. Independently check the architect's re-run claims.
3. **Constitutional surface.**
   - Run the architect's coverage checker yourself.
   - Construct kernels that change only leaves the architect classified as non-security or content-registered, and show
     whether any of them yields weaker authority, secret handling, gate, plugin or tool, export, override, install or
     exception policy.
   - Inject an unknown constitutional key and a new constitutional file.
4. **Freshness bootstrap.** Model every machine class of `HO-0001` §3.2 under a repository and transport adversary, and
   under each OP-7 option. Report what each class can be made to accept as current.
5. **Binary and TCB.** Try to authenticate a malicious binary, or an older binary, with each key or key subset below the
   declared thresholds, including OP-4 variants. Check that the chain is non-circular.
6. **Author new held-out attacks** `RV6-B-A01…` that are not in the pack's acceptance plan. Execute or compute each
   one where feasible.
7. **Residuals.** Judge every residual the architect declares against explicit acceptance criteria. Documentation alone
   is not a bound.

## 4. Severity and blocking

| Severity | Meaning |
|---|---|
| CRITICAL / HIGH | **Blocking.** A lower-trust input can yield a current higher-trust fact, security control loss, or TCB compromise below the declared threshold. |
| MEDIUM | **Blocking** only when it cannot be carried as a bound, testable implementation requirement without an architecture change. Otherwise list it as a carried requirement with a precise acceptance test. |
| LOW | not blocking |

## 5. Deliverables (in your output directory only)

- `00-REPORT.md`: scope, method, prior-finding status table, summary, verdict `BLOCKING_FINDINGS_PRESENT` or `NO_BLOCKING_FINDINGS`.
- `01-FINDINGS.md`: each finding with statement, evidence class (executed, computed, code, design), failure scenario, severity and the correction direction (architectural only).
- `02-HELDOUT-ATTACKS.md`: your RV6-B register (attack, adversary, expected secure outcome, revision as written, finding).
- `03-RESIDUALS.md`
- `04-CARRIED-REQUIREMENTS.md`: non-blocking items that the implementation and verifier must test.
- `evidence/`: scripts, outputs, `REVIEWED-CONTENT-DIGESTS.txt` (sha256 of every reviewed file at `4106885dadebac55596067a2586cf4d3097fc025`), README.

Then write `release/orchestration/phase-1/AGENT_RUNS/AR-0016.report.yaml` (schema:
`AGENT_RUNS/README.md`).

## 6. Constraints

- **Independence.**
  - You did not author any RoT-1 revision or prior review.
  - Do not read reviewer C's output, other branches or other worktrees (`git branch -a`, `git log --all`, other scratch
    directories).
  - Under `release/orchestration/`, read only this handoff, `HO-0001` and `AGENT_RUNS/README.md`.
- **Writes.** Only your output directory and your report file. Never modify product source, the pack, D-0008,
  ARCH-0002, prior reviews, verification evidence or released payloads.
- **Probes.** Scratch only; never the canonical checkout `/home/usain/Dynamic-Agentic-Engineering-OS`. Strip `GOV_*`
  from child environments and point `GOV_KERNEL_CACHE` into scratch. Scratch root:
  `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0016/`.
- **No transcripts.** Never read, list or search session or agent transcripts or task-output files: anything under `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/*/tasks/` or `~/.claude/projects/`. They hold other roles' work.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Commits.** Commit the output directory first:
  `Independent trust/security review (B) of RoT-1 revision 6 (4106885): <verdict>`. Then commit your
  report separately. End each message with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
  Leave the worktree clean.

## 7. Forbidden assumptions

- That the architect's evidence or response matrix is correct.
- That the CD2 correction delta defines acceptance.
- That reviewer C covers anything you skip.
- That a stateless machine can know unseen metadata, or that attacker-selected stale signed state may become current.
- That a repository-delivered record can authorise a trust decision.
