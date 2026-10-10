---
type: probe
task: DAEO-7nne
reviewer_session: 12aef0c5-8d9e-4115-a1c7-843ec440d978
implementer_session: c39ec3fb-0eae-4b45-8bce-75db413def44
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ca734550c239ce99bf25804c156eb1b3f1329a88
---

# Probe record: W1-15 second run (DEC-603, DEC-607, DEC-608, DEC-609)

- **What was probed.** The run's code at `ca734550` on `w1/W1-15` (two sessions of a lead since `08b963e4`,
  `1ca87d57-99a3-470e-a579-a2dd8072dac3` and `c39ec3fb-0eae-4b45-8bce-75db413def44`): the seven command
  lines of the template's rulesync hooks source (`template/.rulesync/hooks.jsonc`) in the kernel template's
  form, `python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>"`, with no `PYTHONPATH` prefix. The
  branch was merged directly at the probed head.
- **Who.** A fresh reviewer session started by the orchestrator through `gov launch independent-auditor`,
  read-only, other than the implementer. It wrote nothing to the repository; the worktree was at
  `ca734550` and clean when it left.
- **What held.**
  - The seven strings rulesync 24.0.0 generates equal the kernel template's form byte for byte; every entry
    keeps its limit of 60 and the two post-call entries their Bash matcher.
  - Each of the seven starts its program from the root, a subfolder and a folder outside the project, in a
    plain project, one reached through a link, and projects whose names hold a space, quotes, a dollar
    sign, backticks, non-ASCII letters and a newline: 252 starts, none failed.
  - A whole Bash call from a subfolder: out-of-scope writes are refused by the guard, a failed command's
    out-of-scope change is reported and recorded, a changed acceptance test is restored, in-scope work is
    allowed; findings are written under the project root's runtime folder.
  - The adapter-portability check on a generated project is green; nothing under `src` or `template`
    matches the old form by text.
- **Findings and their judgement (DEC-609).** All lesser, named residuals in
  `governance/project/bootstrap.md`: the session-start and pre-compaction programs still import a
  product's own package named `gov`; a relative `PYTHONPATH=src` in a session's environment; the variable
  unset or empty; the stop program silent where `gov` is not importable; the harness's handling of the
  variable is the orchestrator's measurement on an adopted clone.
- **Judgement.** Pass: no fail-open hole that ordinary work produces, nothing that breaks a Wave 1 exit
  criterion.
