# HO-0010 — Handoff to root-cause specialist architect B (escalation before RoT-1 revision 5)

| Field | Value |
|---|---|
| Handoff | HO-0010 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh root-cause specialist architect B, run `AR-0010` (role `rot-specialist-architect`) |
| Why this exists | Phase 1 protocol §5 escalation. The same blocking classes (BC4-1 independent TCB decisions (RV4-H1; remainder of R2-H3/BC-3), BC4-2 anchored non-circular first TCB acceptance (RV4-H2; remainder of R2-H2/BC-2 where it meets R2-H3/BC-3), BC4-3 release-scoped registration of constitutional content (RV4-H3; remainder of R2-H1/BC-1)) have survived revisions 1–4 in narrowed form. The orchestrator's persistent-remainder threshold has been reached. |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r5-specialist-b` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/spec-r5-b` |
| Your output directory | `release/root-of-trust/4.1.6-alternatives-r5/specialist-b/` |

A second specialist is working independently on the same question. You must not see their work and they must not see
yours. A synthesis architect will read both proposals afterwards and author revision 5. Fresh independent
reviewers will then review that revision.

**You do not edit the RoT-1 pack, D-0008 or ARCH-0002.**

## 1. The question

Why do BC4-1 independent TCB decisions (RV4-H1; remainder of R2-H3/BC-3), BC4-2 anchored non-circular first TCB acceptance (RV4-H2; remainder of R2-H2/BC-2 where it meets R2-H3/BC-3), BC4-3 release-scoped registration of constitutional content (RV4-H3; remainder of R2-H1/BC-1) keep surviving correction? What architecture removes each class at its root rather than
narrowing it?

The recurring rejection class across 4.1.3–4.1.5 and RoT-1 revisions 1–4 is: **a lower-trust input yielding
a current, higher-trust fact** (D-0007).

You may conclude:
- that the current mechanism family is sound and only needs a specific missing invariant; or
- that a different trust model is needed. Examples include removing an input from the decision, changing what is
  compiled versus fetched, changing who may assert currency, or changing what a binary must prove.

State plainly where a genuine product or security trade-off exists that only the owner can decide.

### Starting lens (specialist B)

Start from the **release, build and custody supply chain**: who establishes each fact (faithful build, verified source, content legitimacy, currency), at what threshold, how independent parties' facts compose into one acceptance, and what a verifier can check without trusting the thing being accepted.

This lens sets where you start. It does not limit scope: you must address every persistent class and every `HO-0001`
§3 requirement. The review of revision 4 names the root invariant it found unestablished for each class
(`00-REVIEW-REPORT.md`, `11-CORRECTION-DELTA.md`). Test that diagnosis; do not assume it.

## 2. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Latest rejected revision | `release/root-of-trust/4.1.6/`, D-0008, ARCH-0002 | `bca05a7e2c2791126fde1d3d812facdaa45b2e45` |
| Its consolidated review (synthesis governs) | `release/root-of-trust/4.1.6-review-r4/` | `97a554525a4677035b56c10c6ff6f1096c818e6c` |
| All earlier revisions and reviews | `release/root-of-trust/4.1.6-review*/`; revisions at `676dfce`, `d37b05c`, `ca77a43`, `bca05a7` | Git history |
| Owner requirements (binding) | `release/orchestration/phase-1/HANDOFFS/HO-0001-rot-architect-r3.md` §3–§4 | at base |
| Implementation the design governs | `runtime/`, `cli/`, `framework/`, `migrations/`, released payloads | unchanged since `da9c851` |
| Legacy binaries | `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}` | read-only |

## 3. Deliverables (output directory only)

- `00-ROOT-CAUSE.md`: for each persistent class, trace the chain across revisions:
  - the finding;
  - the correction;
  - the remainder;
  - why it remained.

  Name the invariant that was never established.
- `01-ALTERNATIVE.md`: the proposed mechanism for each class.
  - State its trust inputs, what it removes, what it adds, what it assumes and what it costs operationally.
  - Explain how it meets every `HO-0001` §3 requirement as a class.
  - List what it keeps from the latest revision (the reviews' "retain" lists).
- `02-FALSIFICATION.md`: attack your own proposal with every blocking probe from the latest two reviews, plus new attacks
  of your own. Execute or compute where feasible, with scripts in `evidence/`.
- `03-OWNER-CHOICES.md`: the genuine trade-offs only, each with options and consequences. Decide none.
- `evidence/`: scripts and outputs.

Then write your typed report, `release/orchestration/phase-1/AGENT_RUNS/AR-0010.report.yaml` (schema:
`AGENT_RUNS/README.md`, verdict `ALTERNATIVE_PROPOSED`).

## 4. Constraints

- **Independence.** Under `release/orchestration/`, read only this handoff, `HO-0001` and `AGENT_RUNS/README.md`. Do not
  inspect other branches, worktrees or scratch directories.
- **Writes.** Only your output directory and your report file.
- **Probes.** Scratch only (`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0010/`). Strip `GOV_*` and point `GOV_KERNEL_CACHE` into scratch.
  Keep the worktree clean.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Commits.** Commit the output first:
  `RoT-1 root-cause specialist B alternative before revision 5 (proposal only)`. Then commit the report
  separately. End each message with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
