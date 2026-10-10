---
type: probe
task: DAEO-7nne
reviewer_session: 75fd8431-f637-4ba7-828e-4144e74a7e80
implementer_session: 5d394f12-80e7-4f4c-8bf3-9203142d72d4
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: cddf5ee37a67e16c6d4327c036772b69daa61bd5
---

# Probe record: W1-15 round (DEC-595, DEC-596, DEC-600, DEC-601)

- **What was probed.** The round's code at `cddf5ee3` on `w1/W1-15`, one run of a lead since `108df093`
  (session `5d394f12-80e7-4f4c-8bf3-9203142d72d4`): the secrets-indexing scan in a thread pool
  (`src/gov/secrets/__init__.py`), a time limit a check's declaration may state (`src/gov/cli/checks.py`,
  `src/gov/check/runner.py`, 900 seconds in this check's declaration), and the template's rulesync hooks
  source (`template/.rulesync/hooks.jsonc`: the 60-second limit on seven entries, the entry for a failed
  tool call, the Bash matcher on the post-call entry). The branch was merged directly at the probed head
  (`bcce3d4f`).
- **Who.** A fresh reviewer session started by the orchestrator through `gov launch independent-auditor`,
  read-only, other than the implementer. It wrote nothing to the repository; the worktree was at
  `cddf5ee3` and clean when it left.
- **What held.**
  - The parallel scan answers as the serial form did, same list and order, on thirteen planted shapes at
    1, 2, 7, 64 and the default number of workers. Every failure shape raises and never answers an empty
    list: a file that cannot be read, a folder that cannot be entered, a dangling link, a link loop,
    gitleaks failing, killed or past its limit in one worker, a file deleted after the walk.
  - A check killed at its limit is red, whatever it printed before (a not-applicable answer, an empty
    list, a trapped signal). Values that are no positive whole number are refused as an invalid
    declaration; the key in one layout only is refused.
  - The Bash matcher loses nothing: the containment program ends silently for every other tool before it
    does anything, and the pre-call program snapshots for Bash calls only.
  - What rulesync 24.0.0 generates carries the limit on all seven entries, the matcher, and the
    failed-call entry; a failed command that changed a file out of scope is reported and recorded, a
    changed acceptance test is restored.
- **Findings and their judgement (DEC-601).**
  - The relative command lines of the hooks source exit 2 from a subfolder, all seven entries; older than
    the round. To the owner as package P-38, with the orchestrator's measurement on a dev-tier clone.
  - Named residuals in `governance/project/bootstrap.md`: the `PYTHONPATH` prefix shape, a limit too
    large for the runner, YAML spellings of the limit, the sixth key in `gov check --list`, the commit
    hook's wait on a large store, a file vanishing under the runtime folder during the scan.
- **Judgement.** Pass: no secret gets through, no file is left unscanned, and nothing in the time limit
  turns an unfinished check green.
