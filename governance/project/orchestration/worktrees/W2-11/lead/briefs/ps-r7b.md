# Brief: product-spec worker (repair), W2-11 (DAEO-k7hz) round 2, run r7, STANDARD, a kernel change under the CIT-P (CAP-33)

Hand-written by the ticket lead (`gov context DAEO-k7hz --role product-spec` refused: `BLOCKED: mandatory input 'DEC-1083' not found in the store`). A fresh session after a red: you get the failing output only. The CTO's decision P-W2-11-R6-2 (c) (the ticket file's last paragraph, `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`, read-only): W2-128's cases are met by W2-11's text wherever the text can meet them.

## Step 0: the sandbox check, before any work (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed: stop and return.

## Who and where
- Role `product-spec`, ticket `DAEO-k7hz`. Check `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11`, `w2/W2-11`). Different: stop and say so.
- **Policy 2 (c) (DEC-820 (c)):** never read `tests/acceptance/W2-11/`; every Grep or Glob call that could reach `tests/acceptance/W2-11/` excludes it (`!tests/acceptance/W2-11/**`), and so does every recursive Bash search (`grep -r --exclude-dir`, `rg -g '!…'`, `find … -prune`); if a search shows you a line from there anyway, stop reading it and say so in your return. **(d):** never read the hidden half of any evaluation set by which you are measured.

## The red (all of it you get)
```
tests/acceptance/W2-128/test_w2_128_round2a.py: AssertionError: the test-design skill still bars source code or implementation outright: ['which holds no implementation']
tests/acceptance/W2-128/test_w2_128_round2a.py: AssertionError: the orchestration skill's sections changed
  At index 13 diff: 'Followed by hand' != 'Followed by hand (Wave 2)'
```

## Do (two text changes; nothing else)
1. `template/governance/kernel/skills/test-design/SKILL.md`, section "Red against the ticket's base": "which holds no implementation" bars implementation outright; the rule is that the designer's worktree holds none of *this ticket's* implementation (DEC-820 (c), DEC-963). Say so in that clause.
2. `template/governance/kernel/skills/orchestration/SKILL.md`: the heading `## Followed by hand` goes back to `## Followed by hand (Wave 2)` (the integration branch's heading; the restore shortened it). The body is at its cap: `body_tokens.py` must still say `OK` (now 9,972 characters of 10,000).
- Each change in the kernel source and its two copies, all byte-identical: `template/governance/kernel/skills/<skill>/SKILL.md`, `.rulesync/skills/<skill>/SKILL.md`, `template/.rulesync/skills/<skill>/SKILL.md` (`cmp` after).
- Versions stay 1.4.0 (raised this round, not yet released); `metadata.version` stays.
- `docs/changes/W2-11-CIT-P.md`: extend the P-W2-11-R6-2 (c) row in §7.1 by these two changes, and correct §7.1's sentence that `skills/orchestration/SKILL.md` "gains nothing but its version" (it now also changes the reads line's "apart from" to "except" and this heading back). Status stays PROPOSED.
- Measure: `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py /home/usain/gov-os-worktrees/W2-11/template/governance/kernel/skills/orchestration/SKILL.md /home/usain/gov-os-worktrees/W2-11/template/governance/kernel/skills/test-design/SKILL.md` (both `OK`).
- Run, reading results only: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m pytest /home/usain/gov-os-worktrees/W2-11/tests/acceptance/W2-128/test_w2_128_round2a.py /home/usain/gov-os-worktrees/W2-11/tests/acceptance/W1-35/test_w1_35_orchestration.py -q -p no:cacheprovider --tb=no -o tmp_path_retention_policy=failed` (W2-128 and W1-35 are other tickets' tests; you may read them). Expected after your change: only W2-128's `test_s11_guard_test_design_skill_changes_only_its_read_rule` red (a designer is revising it). Then `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11` once: counts only.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env).
- **Memory (DEC-836):** use `gov retrieve` first if you need to know anything beyond this brief: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.cli.main retrieve "<question>" --json`; **search again once** (DEC-1092 (1)) in your own, different words if a bundle does not answer, then answer from both or say "not found"; two searches in all; never one giant query (DEC-860); small code-graph queries (DEC-859).
- **Guard read refusals (DEC-849):** take a refusal, never another spelling; count them in your return.
- A skill states a method and grants nothing (CAP-24.b). Never write `.claude/**`, a `brief-*.md`, a role template, `src/`, `tests/`, `.tickets/` or the register.

## Commit
`git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Implements: CAP-33, DEC-820, DEC-866, DEC-1137" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <the paths>`. Check `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` first; never `--no-verify`; no amend, rebase, reset, push or merge.

## Rules
- Machine (DEC-898): your share 1 GB and 10,000 files and folders outside the tracked tree; no tree copies (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`); give `du -sh` / `du -s --inodes` of anything you made. Your sandbox may not write `/tmp/gov-os-lead-W2-11`: use its own temp and say so.
- Row W2-L423's rule (DEC-911): under `.gov-runtime/` commit hashes as 12 digits, never 40, and never the keywords of the secrets rule that takes a bare 40-hex string.
- Protected material (DEC-820): never read the held-out material's contents; never print a secret; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- Command forms: one simple command per Bash call; literal paths; no here-documents, backticks, `bash -c`, long inline `python3 -c` with braces. Never `pgrep`, `pkill`, `killall` or the Monitor tool.
- Never ask or notify the owner; install nothing; one role per ticket (DEC-995, DEC-996).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). Never work around a refusal: report it.
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"): stop, return status `AUTH_REQUIRED`.
- Keep your output short.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line, any payload after them; refused twice for the same call, stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
After the twelve fields: the sandbox check's result; the `body_tokens.py` lines; whether you used `gov retrieve`; `guard_refusals:` lines or `none`; `brief_gaps:` lines or `none`.
