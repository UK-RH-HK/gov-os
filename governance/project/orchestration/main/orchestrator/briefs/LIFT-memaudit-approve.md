# ACT-MEMORY-AUDIT-INSTALL-1, part 1: the three approved briefs into the launch script's approved list (DEC-1129 (2))

Read `LIFT-common.md` first (scratch only). Role: ACT-preparation helper, Sonnet high, class C2 (DEC-1120). Scratch
folder: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/memaudit-install-1/`.
**Never open, list or read anything under the sets root (`~/gov-os-eval/`)**, including the live approved list: you
build from the records, exactly as ACT-W2-149-INSTALL-1 did.

## What the owner approved (DEC-1129 (2), read it in the register)
`governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md` (sha256 `bc0894230e3181e5be27726d60e9fb781f9355da1c4f8e76f69b400af97d379b`),
`checker.md` (`cea517b8da7d4834bb2a698b9c7023670da36f0ceca6b3350656c6db77c45248`), `auditor.md`
(`37be41c3fb2fea1654d68f71f1ecfc5ad4b41faaed9356a27ce1f01d8ef94245`), at commit `8c18fa300`. Their hashes go into
`<sets root>/indep-walls/APPROVED` by the owner's install ACT.

## Model
`governance/project/orchestration/packages/ACT-W2-149-INSTALL-1.md` and its drafts
(`.gov-runtime/scratch/orchestrator/drafts/w2-149-install/`, `APPROVED.before`/`APPROVED.after`), and any later ACT that
changed the list (search the register and packages for "APPROVED" and "approved list" after DEC-1113). The launch
script's reader: `governance/project/orchestration/tools/indep_launch.py` (`parse_approved`, the brief check near line
2130: a line `<sha256> brief <kind> <repository path>`, the brief read from the repository at `--commit`; `kinds.yaml`
in `governance/project/indep-walls/` for the kinds and how a brief is resolved — check the three briefs' front matter
resolve for kinds writer, checker, auditor). Whether briefs must also sit under `governance/project/indep-briefs/`
(ACT-W2-149-INSTALL-1 put set-up A's there): follow what the launch script needs, nothing more.

## Build
1. `APPROVED.before`: the list as the last applied ACT left it, rebuilt from its records (its recorded sha256 must
   match); `APPROVED.after`: plus three lines, one per brief. If the records cannot give the exact `before`, say so: the
   ACT then appends with a check that refuses unless the file's sha256 is the expected one.
2. `ACT-MEMORY-AUDIT-INSTALL-1.md`: what, why (DEC-1129 (2)), the class by `governance/project/operator/class-rules.yaml`
   (the sets root is the `walled-sessions` row: say what that means for who applies it), the owner's exact commands
   (sha256 check of before, the write, 0400 kept, the after check), the rollback, and a rehearsal on a planted copy in
   your folder: `indep_launch.py` run in its dry or plan form (find one that starts no session) against a planted sets
   root with `APPROVED.after`: each of the three briefs passes the approved check for its kind; a changed byte refuses.
3. Anything else the install needs before 11-23 that MEMORY-AUDIT-1 §6 names (the cron is a later ACT; W2-170 to W2-173
   are not built yet): list only.

## Return
The twelve fields, short; the files; the rehearsal count. Estimate 1 h.
