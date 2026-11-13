---
id: W2-33-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-12
branch: w2/W2-33
base: 3df1ac2deb1b (the acceptance tests merged, red)
head: c4b97716164e (the role files as verified; later commits add only records)
ticket: DAEO-lrre (W2-33)
task: DAEO-lrre
author: orchestrator (W2-33 ticket lead)
review: PASS, independent-auditor session bf9dae7f-1b6d-4e7e-80bf-517a182f778a on 3b3a90d74c3e, 7 findings, none blocking; narrow check of the fix c4b977161 (docs/probes/DAEO-lrre/PR-DAEO-lrre.md)
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

| file | version after | sha256 before (`3df1ac2deb1b`) | sha256 after (`c4b97716164e`) | lines +/- |
|---|---|---|---|---|
| `template/governance/kernel/roles/engineer.md` | 1.1.0 | `66c094102c731f9e5e4504af393fca5954c5fe8afdcc93eeba9f457367233c5f` | `c94f98d7fc17b60bfbea3d3bb2fcf7e2d84d698490e3e4464ece957c15f5b423` | +10 / -2 |
| `template/governance/kernel/roles/independent-auditor.md` | 1.1.0 | `4d6f6bdf8596a485dc20388e0529915a128441fc3950665474f062829856a9a9` | `4b4a5f947206517e167d6b39c9531d3fa7a96476b1d0658ea52e84277a92746c` | +8 / -2 |
| `template/governance/kernel/roles/independent-test-designer.md` | 1.1.0 | `62e1ec3f86c0c266d4736c8e510306a9c5a7ed7924de06efcf38f578fc54b340` | `890c91f577c8b934761cbc95a079fbbc50f4201f60f1f7ef52471afb16014fce` | +10 / -2 |
| `template/governance/kernel/roles/orchestrator.md` | 2.0.0 | `97e6d049d6f2478bfb02ee33263e9a99fb5b1e90bc8bce6dea611b4e422b2e4b` | `08ba69e63d51adeb901ef8998f6dc2a21490dff9b326c69a603fafbf14d47d10` | +20 / -60 |
| `template/governance/kernel/roles/product-spec.md` | 1.1.0 | `fd432110627c85b352e8ed268e87177855a1a291679921aaf089a17ff498fb9c` | `bb9a46da12c7b34208cc1f6fcc37f523821783530d3faf8675032502ebf74e43` | +6 / -1 |
| `template/governance/kernel/roles/research.md` | 1.1.0 | `60f9092f37430a096eeb932907b5814661585afaf38c52a045c3d775c933e678` | `f9bc3b721b568bf80210f2f438dce5d18954eb24a986b75d6c82733793b9d1cd` | +6 / -1 |
| `template/governance/kernel/roles/ticket-lead.md` (new) | 1.0.0 | absent | `0c93598c82daf3f5401c9d5c3293a00144a40565682fd878f289926593b355af` | +35 / -0 |
| `template/governance/kernel/roles/qa-engineer.md` (new) | 1.0.0 | absent | `40fd68fdadf35df679a14842f86e6b51ce849eec65d241cf6fca04f63b362f3a` | +28 / -0 |
| `template/governance/kernel/roles/senior-engineer.md` (new) | 1.0.0 | absent | `243e8b8422eca053c7da99f108941d736962e4437bbc0c507fc98feadc25f415` | +29 / -0 |
| `template/.rulesync/subagents/orchestrator.md` (the source, = `portability.compose(root, 'orchestrator')`) | n/a | `7f235d5105881000c8c9443abc11dc6887401d8ab42f536dd533054bdec1520c` | `ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c` | +22 / -62 |

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
- **Generated copies (W2-153, the copies ACT):** `.claude/agents/**`, the root `.rulesync/**` and the five other
  `template/.rulesync/subagents/*` sources are not changed here. Their composition (`portability.compose`) changes
  with the kernel bodies. Until the copies ACT rewrites them, these cases stay red on this branch (the lead's
  full-suite run on `3b3a90d74c3e`: 5590 tests, 50 failed: the 46 that wait on the copies are listed in this bullet, and the other 4 in the next two;
  on the final head `1221ee0e4`, 47 failed, the 3 W2-128 cases being green after the fix; the review's R1):
  - W2-153: 23 cases in `tests/acceptance/W2-153/test_w2_153_sources.py`: the S3 body and fields cases for the
    sources in `.rulesync/` and `template/.rulesync/` (all but the template's orchestrator source), and
    `test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository`;
  - the unit cases `tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition` and
    `tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition`;
  - W1-38: `tests/acceptance/W1-38/test_w1_38_rulesync.py`, `TestRoleFieldAgreement` (5) and
    `TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project`;
    `tests/acceptance/W1-38/test_w1_38_heldout_step.py` (10; each reads `SOURCE_DIFFERS` from the role sources);
  - W1-33: `tests/acceptance/W1-33/test_w1_33_agent_definitions.py::test_the_definition_agrees_with_its_kernel_role_file`
    (5 roles).
  The CTO pairs the copies ACT with the land. When that ACT adds the three new roles' agents,
  `tests/acceptance/W1-33/test_w1_33_agent_definitions.py:86-90` (the roster pinned at six plus research) needs a
  revision too.
- **An older case asserting the old file (the CTO's, DEC-1156 (7)):**
  `tests/acceptance/W1-33/test_w1_33_kernel_role_files.py:149-155` (`test_the_research_role_file_is_unchanged`, DEC-163)
  pins `research.md` at the hash W1-46 placed. The owner's lines in every role file (S2, S4, S5, S7) change it.
- **Older W2-128 cases kept green:** the fix `c4b977161` puts back, in the CTO's file, the kernel templates a lead's
  brief is built from (`role-lead.md`, `brief.md`; DEC-1050), a fact the removed lead section carried. It also keeps
  `engineer.md`'s Purpose on line 5 (`tests/acceptance/W2-128/test_w2_128_round2a.py:222`, `test_w2_128_templates.py:100`).
- **Older cases revised (DEC-1156 (7)):** a test designer revised three cases in
  `tests/acceptance/W1-35/test_w1_35_orchestration.py`, each with a Rewrite-Reason. They now read `ticket-lead.md`
  and the nine-file roster. The rulesync half of the roster case is dropped: the agreement of the generated sources
  with the kernel lives with the copies ACT and W2-153's generation check.

## 5. Evidence

- `gov accept W2-33`: outcome pass, 96 passed, 0 failed, 11 lines mapped, 0 unmapped (on `4c6a47d8c` and again on
  the final head; logs `accept-build-2.txt`, `accept-build-3.txt` in the worktree's lead records).
- Verification and the independent review: see the probe record in `docs/probes/DAEO-lrre/`.

## 6. For the owner

Approve the nine kernel role files and the orchestrator's rulesync source at the hashes above (CAP-33):

Owner approval: W2-33 CIT-P approved at c4b97716164e, C0 Haiku low (owner, 2026-11-13, DEC-1160)
