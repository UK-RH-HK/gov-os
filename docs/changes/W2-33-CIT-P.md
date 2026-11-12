---
id: W2-33-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-12
branch: w2/W2-33
base: 3df1ac2deb1b (the acceptance tests merged, red)
head: 4c6a47d8c (the role files as verified; later commits add only records)
ticket: DAEO-lrre (W2-33)
task: DAEO-lrre
author: orchestrator (W2-33 ticket lead)
review: pending (independent-auditor, read-only; docs/probes/DAEO-lrre/)
decisions_carried: [DEC-954, DEC-957, DEC-959, DEC-963, DEC-983, DEC-982, DEC-847, DEC-1010, DEC-1119, DEC-1120, DEC-236, DEC-839]
decisions_applied: [DEC-1052, DEC-1087, DEC-1156, DEC-971]
state_class: EVIDENCE
---

# W2-33: change-impact proposal (CIT-P) on the kernel role files

This change puts the three layers into the kernel's role files, as ROLES-SPEC-1 (approved, DEC-957) states them and
as the ticket's `## Interface` gives the line forms (the owner, DEC-1156 (3)). The kernel roles folder grows from six
files to nine. Every file gets the machine-readable defaults that W2-60a's launcher reads, plus RUBRIC-2's model and
effort, the work order and the one-writer rule. The orchestrator's two copies get the CTO-only install rule (moved
from W2-113 to this ticket by DEC-1156 (4)). Kernel role files change, so this goes to the owner before the merge
(CAP-33).

## 1. What triggers the change

| # | Trigger | Source |
|---|---|---|
| T1 | The ticket lead gets a role file of its own; `orchestrator.md` loses its `## The ticket lead` section and becomes the CTO's file (role id kept) | DEC-954, DEC-957 Q2, DEC-236 |
| T2 | A Senior Engineer role file (a stream's sub-orchestrator) | DEC-954 Q6, Q13; DEC-1087 (13); DEC-1156 (3) |
| T3 | The QA engineer replaces the planned independent reviewer; it is the moderator, at most two rounds | DEC-959 item 3, DEC-1010 item 1 |
| T4 | Machine-readable defaults per role (`Version`, `Launch default`, `Skills`) and RUBRIC-2's model and effort by role and criticality | DEC-954, DEC-839 item 5, DEC-1119 (2), DEC-1120 (2) |
| T5 | Every role file states the work order and one writer per worktree | DEC-959 item 7, DEC-963, DEC-847, DEC-983, DEC-982 |
| T6 | Both orchestrator copies state the CTO-only install rule and drop the old "the guard asks on every install" | DEC-971 item 4, DEC-1156 (4) |

## 2. The kernel files and their sha256

| file | version after | sha256 before (`3df1ac2deb1b`) | sha256 after (`4c6a47d8c`) | lines +/- |
|---|---|---|---|---|
| `template/governance/kernel/roles/engineer.md` | 1.1.0 | `66c094102c731f9e5e4504af393fca5954c5fe8afdcc93eeba9f457367233c5f` | `4c422966365c7f0974aae64d934413ab76f4078a259045065404a39be36ff217` | +10 / -2 |
| `template/governance/kernel/roles/independent-auditor.md` | 1.1.0 | `4d6f6bdf8596a485dc20388e0529915a128441fc3950665474f062829856a9a9` | `4b4a5f947206517e167d6b39c9531d3fa7a96476b1d0658ea52e84277a92746c` | +8 / -2 |
| `template/governance/kernel/roles/independent-test-designer.md` | 1.1.0 | `62e1ec3f86c0c266d4736c8e510306a9c5a7ed7924de06efcf38f578fc54b340` | `890c91f577c8b934761cbc95a079fbbc50f4201f60f1f7ef52471afb16014fce` | +10 / -2 |
| `template/governance/kernel/roles/orchestrator.md` | 2.0.0 | `97e6d049d6f2478bfb02ee33263e9a99fb5b1e90bc8bce6dea611b4e422b2e4b` | `4489e5eef43e620ca88a382491f9d2d64d9caf602acc00ca7b595160d1fcfa0a` | +20 / -60 |
| `template/governance/kernel/roles/product-spec.md` | 1.1.0 | `fd432110627c85b352e8ed268e87177855a1a291679921aaf089a17ff498fb9c` | `bb9a46da12c7b34208cc1f6fcc37f523821783530d3faf8675032502ebf74e43` | +6 / -1 |
| `template/governance/kernel/roles/research.md` | 1.1.0 | `60f9092f37430a096eeb932907b5814661585afaf38c52a045c3d775c933e678` | `f9bc3b721b568bf80210f2f438dce5d18954eb24a986b75d6c82733793b9d1cd` | +6 / -1 |
| `template/governance/kernel/roles/ticket-lead.md` (new) | 1.0.0 | absent | `0c93598c82daf3f5401c9d5c3293a00144a40565682fd878f289926593b355af` | +35 / -0 |
| `template/governance/kernel/roles/qa-engineer.md` (new) | 1.0.0 | absent | `40fd68fdadf35df679a14842f86e6b51ce849eec65d241cf6fca04f63b362f3a` | +28 / -0 |
| `template/governance/kernel/roles/senior-engineer.md` (new) | 1.0.0 | absent | `243e8b8422eca053c7da99f108941d736962e4437bbc0c507fc98feadc25f415` | +29 / -0 |
| `template/.rulesync/subagents/orchestrator.md` (the source, = `portability.compose(root, 'orchestrator')`) | n/a | `7f235d5105881000c8c9443abc11dc6887401d8ab42f536dd533054bdec1520c` | `59cfd390088ce8a4589f914455c7e0061205eca4d581db6047c04395fa2e5367` | +22 / -62 |

There is no `independent-reviewer.md`, before or after.

## 3. What each file states now (the Interface's line forms, each once and whole)

- In all nine files: `- **Version:**`, `- **Launch default:** model <id>, effort high`, `- **Skills:**` (existing
  skills only), `- **Model tier:** see Launch default`, the work-order sentence and the one-writer sentence, word for
  word as the Interface gives them.
- `- **Launch by criticality:**` appears only where RUBRIC-2 varies. Engineer and test designer: C3 Opus high, C2 and
  C1 Sonnet high, C0 Haiku low. QA engineer: C3 Opus high, C2 Opus high on FULL and Sonnet high otherwise, C1 Sonnet
  high, C0 Haiku low. The C0 value is the writer's reading of RUBRIC-2-APPLY ("Haiku or deterministic") and DEC-1120
  (3) ("low or medium for C0"); S7 sets no C0 value.
- Launch defaults: orchestrator (CTO), ticket lead, senior engineer and independent auditor run Opus high;
  engineer, test designer, QA engineer, product-spec and research run Sonnet high.
- Skills stand in for the two names ROLES-SPEC-1 proposes that have no folder. `ticket-loop` and
  `stream-orchestration` are both covered by `orchestration`. The ticket lead and the senior engineer each list
  `orchestration, checkpoint, retrieval`.

## 4. Impact

- **Launcher (W2-60a):** reads `Version`, `Launch default` and `Skills` from each file; all nine are in its form.
- **Guard (W2-60b):** `qa-engineer` and `senior-engineer` are not yet known role ids. The guard's refusal of a QA
  write elsewhere and the launcher's refusal of two writers in one worktree are judged there (the Interface).
- **Generated copies (W2-153, the copies ACT):** `.claude/agents/**`, the root `.rulesync/**` and the other
  `template/.rulesync/subagents/*` sources are not changed here. Until the copies ACT, these cases stay red:
  - W1-33's kernel-equals-generated cases (`tests/acceptance/W1-33/test_w1_33_agent_definitions.py:56-68`);
  - W1-38's field agreement (`tests/acceptance/W1-38/test_w1_38_rulesync.py:56-90`).
  The CTO pairs the copies ACT with the land.
- **Older cases revised (DEC-1156 (7)):** a test designer revised three cases in
  `tests/acceptance/W1-35/test_w1_35_orchestration.py`, each with a Rewrite-Reason. They now read `ticket-lead.md`
  and the nine-file roster. The rulesync half of the roster case is dropped: the agreement of the generated sources
  with the kernel lives with the copies ACT and W2-153's generation check.

## 5. Evidence

- `gov accept W2-33` on `4c6a47d8c`: outcome pass, 96 passed, 0 failed, 11 lines mapped, 0 unmapped
  (`.gov-runtime/scratch/lead/log/accept-build-2.txt` in the worktree).
- Verification and the independent review: see the probe record in `docs/probes/DAEO-lrre/`.

## 6. For the owner

Approve the nine kernel role files and the orchestrator's rulesync source at the hashes above (CAP-33):

Owner approval: ______________________ (date, decision id)
