Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 — W2-128's F6 case meets the composed sources, the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer working under **W2-153** (`.tickets/DAEO-8s85.md`: read its S3 and
Interface). W2-153's S3 makes each `.rulesync/subagents/<role>.md`, and the template's copy under
`template/.rulesync/subagents/`, the role file's rulesync front matter plus `claudecode.skills` plus **the body of the
role's kernel template**. For the orchestrator that is `template/governance/kernel/templates/role-lead.md`'s body
(after its front matter). The old Wave 1 role body goes from those sources.

W2-128's round 2a case
`tests/acceptance/W2-128/test_w2_128_round2a.py::test_review_f6_orchestrator_role_names_no_retired_brief_text_as_content[rulesync]`
(about line 199) asserts that `template/.rulesync/subagents/orchestrator.md` names a kernel template (`role-lead.md` or
the templates folder) for a lead's brief. That was written for the old body. With W2-153 the copy's body is
`role-lead.md`'s own body, which names no retired brief text but does not name itself. So the case fails, though its
purpose holds: no retired `brief-*.md` text as content (W2-128 review F6, round 2b F1).

## The change (DEC-866: `Rewrite-Reason:`)
- Revise the `[rulesync]` parameter so it passes when the copy names no retired `brief-*.md` text as content, **and**
  either names a kernel template, or its body equals the body of `template/governance/kernel/templates/role-lead.md`
  (front matter stripped, as portability's `_split` strips it). Fail otherwise.
- The `[kernel]` parameter (`roles/orchestrator.md`) stays as it is.
- Change nothing else.
- Run W2-128's folder on your tree, which has integrate (the old body, already fixed by round 2b): every case stays
  green.

## Where you work, rules, return
- Worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`, with integrate merged
  (`c667bc49c`). Write only `tests/acceptance/W2-128/`.
- Never open `/home/usain/gov-os-worktrees/W2-153` or read W2-153's implementation files. The composition is stated
  above and in the ticket.
- Run only `tests/acceptance/W2-128`, with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not
  found). No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the
  sandbox.
- **Commit** on `w2/W2-153-tests`, only `tests/acceptance/W2-128/`, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-153 S3 composes the rulesync orchestrator source from role-lead.md's body; F6's rulesync parameter accepts that body (DEC-866)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A one-case round.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the diff, the folder's counts, the commit and `TESTS-READY <hash12>`.
