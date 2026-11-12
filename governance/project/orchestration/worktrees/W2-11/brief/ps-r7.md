# Brief: product-spec worker, W2-11 (DAEO-k7hz) round 2, run r7, STANDARD, a kernel change under the CIT-P (CAP-33)

Hand-written by the ticket lead (`gov context DAEO-k7hz --role product-spec` refused: `BLOCKED: mandatory input 'DEC-1083' not found in the store`). The CTO decided package P-W2-11-R6-2 as option (c) (recorded in the ticket file's last paragraph, `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`, read-only): you state in the skills' text what another ticket's (W2-128's) acceptance cases ask where W2-11's text can meet it; a test designer revises the rest in parallel, in another worktree.

## Step 0: the sandbox check, before any work (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed: stop and return.

## Who and where
- Role `product-spec`, ticket `DAEO-k7hz`. Check `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11`, `w2/W2-11`). Different: stop and say so.
- **Policy 2 (c) (DEC-820 (c)):** never read `tests/acceptance/W2-11/`; every Grep or Glob call that could reach `tests/acceptance/W2-11/` excludes it (`!tests/acceptance/W2-11/**`), and so does every recursive Bash search (`grep -r --exclude-dir`, `rg -g '!…'`, `find … -prune`); if a search shows you a line from there anyway, stop reading it and say so in your return. You may run `gov accept DAEO-k7hz` and read only its pass/fail per line and counts. **(d):** never read the hidden half of any evaluation set by which you are measured.

## Do (three text changes; nothing else)
1. **The held-out refusal as a bar (orchestration).** `template/governance/kernel/skills/orchestration/SKILL.md`, the line that begins "- Reads are open:" (section on temp hygiene / reads; about line 90). It lists the four refusals after "apart from". W2-128's case wants the sentence naming the held-out material to carry a refusal word (one of: never, not, no, refused, forbidden, denied, but for, except, only). Reword so the sentence plainly bars the four (for example "except" for "apart from"), keeping every refusal and citation (DEC-820, DEC-525, DEC-1052). The body is at its cap: `body_tokens.py` must still say `OK` (it is at 2,494 of 2,500 tokens; do not lengthen it by more than the cap allows; shorter is better).
2. **CAP-38.c in the read rule (test-design).** `template/governance/kernel/skills/test-design/SKILL.md`, section "## The work order in parallel", second bullet ("It never reads this ticket's implementation …"): cite CAP-38.c (independent test authorship: the designer works from the specification and its KPIs) in that read rule. Do not cite CAP-38.b or DEC-136 in that section. Leave the section headings as they are (the designer's revision finds the read rule under "The work order in parallel").
3. **test-design's front-matter description.** W2-128's guard allows test-design's front matter to change only in its version (and the carried `metadata.version`). No KPI line needs the description changed: put back the integration branch's description word for word: `description: Method for independent test design from specification and KPIs, without reading implementation.` (the body states the parallel work order).
- Each change in the kernel source and its two copies, all byte-identical: `template/governance/kernel/skills/<skill>/SKILL.md`, `.rulesync/skills/<skill>/SKILL.md`, `template/.rulesync/skills/<skill>/SKILL.md` (`cmp` them after; if they differed before your change, say so and keep the copies' other bytes).
- **Versions:** orchestration and test-design are already raised this round to 1.4.0 (not yet released; `version` and `metadata.version` equal): leave both. `metadata.version` stays (the one carried repeat, decided).
- `docs/changes/W2-11-CIT-P.md`: add one short row for these three changes (P-W2-11-R6-2 (c)); status stays PROPOSED.
- Measure: `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py /home/usain/gov-os-worktrees/W2-11/template/governance/kernel/skills/orchestration/SKILL.md /home/usain/gov-os-worktrees/W2-11/template/governance/kernel/skills/test-design/SKILL.md` (both `OK`).
- Then run `gov accept` once and report its counts and failing lines (expected red, not yours: seven copy cases and F1's "declares no output class" cases, which the designer is revising).
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env). So: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11`.
- **Memory (DEC-836):** use `gov retrieve` first if you need to know anything beyond this brief: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.cli.main retrieve "<question>" --json`; **search again once** (DEC-1092 (1)) in your own, different words if a bundle does not answer, then answer from both or say "not found"; two searches in all; never one giant query (batches, DEC-860); small code-graph queries (DEC-859).
- **Guard read refusals (DEC-849):** take a refusal, never another spelling; count them in your return.
- A skill states a method and grants nothing (CAP-24.b). Never write `.claude/**`, a `brief-*.md`, a role template, `src/`, `tests/`, `.tickets/` or the register. List which generated `.claude/skills/` copies now differ from their sources (they follow by the copies ACT, not by you).

## Commit
`git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Implements: CAP-33, DEC-820, DEC-866, DEC-1137" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <the paths>`. Check `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` first; never `--no-verify`; no amend, rebase, reset, push or merge.

## Rules
- Machine (DEC-898): your share 1 GB and 10,000 files and folders outside the tracked tree; no tree copies (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`); give `du -sh` / `du -s --inodes` of anything you made. (Inside your sandbox `/tmp/gov-os-lead-W2-11` may not be writable; then use the sandbox's own temp and say so.)
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
