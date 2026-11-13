p='/home/usain/gov-os-worktrees/W2-33/docs/changes/W2-33-CIT-P.md'
t=open(p).read()
rep=[
("head: 4c6a47d8c (the role files as verified; later commits add only records)","head: c4b97716164e (the role files as verified; later commits add only records)"),
("review: pending (independent-auditor, read-only; docs/probes/DAEO-lrre/)","review: PASS, independent-auditor session bf9dae7f-1b6d-4e7e-80bf-517a182f778a on 3b3a90d74c3e, 7 findings, none blocking; narrow check of the fix c4b977161 (docs/probes/DAEO-lrre/PR-DAEO-lrre.md)"),
("| sha256 after (`4c6a47d8c`) |","| sha256 after (`c4b97716164e`) |"),
("`4c422966365c7f0974aae64d934413ab76f4078a259045065404a39be36ff217`","`c94f98d7fc17b60bfbea3d3bb2fcf7e2d84d698490e3e4464ece957c15f5b423`"),
("`4489e5eef43e620ca88a382491f9d2d64d9caf602acc00ca7b595160d1fcfa0a`","`08ba69e63d51adeb901ef8998f6dc2a21490dff9b326c69a603fafbf14d47d10`"),
("`59cfd390088ce8a4589f914455c7e0061205eca4d581db6047c04395fa2e5367`","`ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c`"),
("""- **Generated copies (W2-153, the copies ACT):** `.claude/agents/**`, the root `.rulesync/**` and the other
  `template/.rulesync/subagents/*` sources are not changed here. Until the copies ACT, these cases stay red:
  - W1-33's kernel-equals-generated cases (`tests/acceptance/W1-33/test_w1_33_agent_definitions.py:56-68`);
  - W1-38's field agreement (`tests/acceptance/W1-38/test_w1_38_rulesync.py:56-90`).
  The CTO pairs the copies ACT with the land.""",
"""- **Generated copies (W2-153, the copies ACT):** `.claude/agents/**`, the root `.rulesync/**` and the five other
  `template/.rulesync/subagents/*` sources are not changed here. Their composition (`portability.compose`) changes
  with the kernel bodies. Until the copies ACT rewrites them, these cases stay red on this branch (the lead's
  full-suite run on `3b3a90d74c3e`: 5590 tests, 50 failed, all listed here; the review's R1):
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
  `engineer.md`'s Purpose on line 5 (`tests/acceptance/W2-128/test_w2_128_round2a.py:222`, `test_w2_128_templates.py:100`)."""),
("- `gov accept W2-33` on `4c6a47d8c`: outcome pass, 96 passed, 0 failed, 11 lines mapped, 0 unmapped\n  (`.gov-runtime/scratch/lead/log/accept-build-2.txt` in the worktree).",
 "- `gov accept W2-33`: outcome pass, 96 passed, 0 failed, 11 lines mapped, 0 unmapped (on `4c6a47d8c` and again on\n  the final head; logs `accept-build-2.txt`, `accept-build-3.txt` in the worktree's lead records)."),
]
for a,b in rep:
    assert a in t, a[:60]
    t=t.replace(a,b)
open(p,'w').write(t)
print('ok')
