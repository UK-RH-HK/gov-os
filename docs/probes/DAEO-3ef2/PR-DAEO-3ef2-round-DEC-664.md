---
type: probe
task: DAEO-3ef2
reviewer_session: db5a9d05-4acb-443a-9b50-255783a5c486
implementer_session: 8b5590ed-d1f3-488e-a09a-918cb91cb27e
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: c579c932f73033ca42c381f4c4468ae77ce1cd88
---

# Probe record: W1-38 round, the template's deny rule on the acceptance-test folder taken out, and the designer pass on three cases (DEC-664, DEC-665, DEC-669, DEC-675)

- **What was probed.** The round's code at `c579c932` on `w1/W1-38` (two lead sessions since
  `cdf7f17c`: `8b5590ed…`, then the finishing lead `52412102…`): the one line taken out of
  `template/.rulesync/permissions.jsonc` (`74d83913`), the 19 cases of the piece, the three cases
  rewritten to the decided state (DEC-665), and the split of W1-33's generation helper with one more
  made-up file in W1-28's synthetic repository (`6ce6e8eb`, DEC-675). The branch is merged directly at
  the probed head.
- **Who.** A fresh reviewer session started by the orchestrator through
  `gov launch independent-auditor`, read-only, other than the implementers. It wrote nothing to the
  repository; the worktree was at `c579c932` and clean when it left.
- **What held.** In stand-in projects built from the template (39 calls over 24 session shapes, asked
  through the registered PreToolUse commands):
  - every role but the independent test designer, a session with no, an empty or an unknown role, an
    engineer with no ticket, a closed ticket or a ticket naming the folder, and a test designer with
    no, a closed or an unknown ticket are denied every file-tool write and every Bash write the guard
    can read under the acceptance-test folder; the test designer on an in-progress ticket is allowed;
  - a Bash write the guard cannot read is restored from HEAD after the call, with a finding, for every
    role but the test designer (run for real in stand-ins);
  - the launcher puts a literal and a pattern deny rule on the folder for every worker role except
    the test designer;
  - against the code before the round, the removed rule changed no answer for a non-designer in
    ordinary work; the shapes whose answer changed are sessions acting as the test designer, which is
    the decided purpose;
  - the generated settings lose exactly one deny rule; the install, sudo and ticket-folder rules stay;
  - nothing changed under `src/`, this repository's `.rulesync/`, any generated file, the guard, the
    launcher or the held-out generator;
  - each of the three rewritten cases still fails when its state is absent (shown by mutation);
  - W1-28's check runs six copying helpers, as before, with W1-33's `copy_adapter_source` in place of
    `generate_definition`; its logic is untouched; the made-up file holds the marker text only;
  - of the 19 new cases, 4 fail and 15 pass on the source before the round; the 15 are pins on the
    guard and the launcher, labelled as such.
- **Findings and their judgement.** None for the merge. Lesser, named residuals for
  `governance/project/bootstrap.md` and the Wave 2 list: a worker-role session not started by the
  launcher can spawn a test-designer subagent that writes under the folder (medium-low; not ordinary
  work, workers are launched); the guard does not know `MultiEdit` and answers allow (low; before the
  round); unreadable Bash writes are restored, not prevented, in a session without the launcher's
  sandbox rules (low; before the round); the W1-33 case skips where rulesync is absent; the W1-49
  session case skips outside a session; 15 of the 19 new cases are pins.
- **Not probed, by the brief or by the reviewer's own note.** A real CLI session (whether the
  launcher's rules bind subagents and the sandbox); a research launch; the full suites beyond the four
  changed test files (the finishing lead ran the whole of `tests/`: 12,203 passed, serial 263 passed).
- **Judgement.** Pass: no fail-open hole that ordinary work produces (no role other than the
  independent test designer writes acceptance tests in a project made from the template; the check on
  copies of the held-out file sees no less), nothing that breaks a Wave 1 exit criterion (DEC-584).
