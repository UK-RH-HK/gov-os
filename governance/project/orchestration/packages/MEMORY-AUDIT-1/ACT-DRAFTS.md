# The two ACTs the memory audit needs (drafts of what they contain; the CTO builds, rehearses and reviews them)

Written by the product-spec helper for the CTO, 2026-11-11. **Nothing here is built or applied.** Each is a package of
its own (DEC-1057: rehearsed in a clone; DEC-1104 (4): by the owner's operator or the operator agent).

## ACT-MEMORY-AUDIT-INSTALL-1: the three briefs and their lines in the approved list
- **Class: (O).** Both paths it writes are (O) rows of `governance/project/operator/class-rules.yaml`
  (`walled-sessions`): `governance/project/indep-briefs/**` and `gov-os-eval/**` (the list `indep-walls/APPROVED`). The
  yes line has the form of ACT-W2-149-INSTALL-1's (`yes ACT-MEMORY-AUDIT-INSTALL-1 <8 hex of the ready commit>`), and
  the owner's operator applies it by hand, about one minute.
- **Before it:** the owner approves the three briefs' text (`packages/MEMORY-AUDIT-1.md` section 3). The CTO then takes
  their sha256 and builds the ACT from exactly those bytes. A word changed in a brief after approval means a new hash and
  a new approval.
- **What lands:** `governance/project/indep-briefs/memory-audit/writer.md`, `checker.md`, `auditor.md` (byte for byte as
  approved), committed by the operator with `Role: owner`; and three lines appended to the approved list, in the form of
  the existing brief lines:
  ```
  <sha256 of writer.md>   brief writer  governance/project/indep-briefs/memory-audit/writer.md
  <sha256 of checker.md>  brief checker governance/project/indep-briefs/memory-audit/checker.md
  <sha256 of auditor.md>  brief auditor governance/project/indep-briefs/memory-audit/auditor.md
  ```
  Nothing else in the list changes. The walls' template files are not touched, so every template line stays.
- **Rehearsal:** a clone with a planted home and sets root; `apply.sh check`, `apply`, `undo` as in ACT-W2-149-INSTALL-1;
  a dry launch under each of the three briefs (`--seed 17`) passes stage 10 and builds its wall (each brief names its
  `result_schema` and `sample`, and the model comes from the brief's front matter); the set-up A briefs' lines still
  pass.
- **Order:** after W2-173 is merged (so that `effort` is passed), or the sessions run at the CLI's default effort and the
  first audit's record says so.

## ACT-MEMORY-AUDIT-CRON-1: the weekly line
- **Class: (b)**, not (O): the `crontab` row of `class-rules.yaml` is class (b), control. The brief that asked for this
  package said (O); the table decides. By the rule table: the owner's yes, then the operator agent applies it from its
  queue (as ACT-CLAUDE-COPIES-2 was).
- **The line** (one added; the crontab's other lines stay as they are):
  ```
  0 21 * * 1 /usr/bin/bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/memaudit_cron.sh >> /home/usain/gov-os-runs/indep/memaudit-cron.out 2>&1  # DEC-1125 (2): the memory audit; `due` decides weekly or monthly
  ```
  The machine's clock is Europe/London, as the nightly's.
- **Before it:** W2-170, W2-171, W2-172 and W2-173 merged; ACT-MEMORY-AUDIT-INSTALL-1 applied; the baseline line written
  (`python3 -m gov.memaudit baseline`); the dry cycle on planted roots passed (W2-172's evidence).
- **Undo:** the line removed (a commented copy is kept in the ACT's backup, as DEC-1049's were).
- **What it does when it fires:** `memaudit_cron.sh` runs `due`; when none is due it logs one line and exits 0; when due
  it starts the cycle (W2-172). It writes no crontab and starts nothing outside the launch script.
- **Alternative (one line):** the CTO starts each audit by hand with the same tool (rejected for the standing practice:
  DEC-1101 (2) asks for no session opened by the owner or the CTO; kept as the way to run a missed audit).
