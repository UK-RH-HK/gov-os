# Models by role: where the existing code disagrees with the table (MR-1 to MR-3)

Found by the engineer of `models-by-role` on 2026-11-24 while building `governance/project/role-table.yaml`. No value was changed to
make anything agree (DEC-1236 (3), DEC-1242 R-4); each line is where the text stands and what it says. The table's values:
`orchestrator` and `senior-engineer` claude-opus-5-5 high; `lead` claude-sonnet-5-5 medium; `engineer`, `independent-test-designer`,
`product-spec`, `research`, `independent-auditor`, `qa-engineer` claude-sonnet-5-5 high; `audit-wide` claude-opus-5-5 high.

- `governance/project/orchestration/tools/start_lead.sh` (the repository's copy, line 19 and the comment on line 3): says `--model claude-sonnet-5-5 --effort high` ("Sonnet at effort high, the rubric's lead line"); the table's `lead` row (DEC-1236 (2)) says medium. The CTO's own copy under `.gov-runtime/scratch/orchestrator/tools/start_lead.sh` reads `${EFFORT:-medium}` and agrees; `--scripts` on the repository's folder reports it. The scripts are the CTO's: not edited here.
- `governance/project/orchestration/tools/start_audit.sh` does not exist in the repository; the only copy is the CTO's under `.gov-runtime/scratch/orchestrator/tools/` (model claude-opus-5-5, effort high: agrees). `--scripts` on the repository's folder reports it as not readable.
- The role files (`template/governance/kernel/roles/*.md`) and their three copies: every `Launch default` line equals its row (checked by `python3 -m gov.launch.role_table --roles`; `ticket-lead.md` against `lead`). Nothing disagrees.
- `src/gov/launch/launcher.py`: `LEAD_MODEL` (claude-sonnet-5-5) and `LEAD_EFFORT` (medium) agree with the `lead` row; they now serve only a project with no table file.
- `governance/project/criticality.yaml` carried `opus: claude-opus-5-5` (retired by MR-2; a class picks no model).
