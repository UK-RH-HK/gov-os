# Brief: product-spec worker, W2-11 (DAEO-k7hz) round 2 (DEC-916), STANDARD, a kernel change under the CIT-P (CAP-33)

Hand-written by the ticket lead from `template/governance/kernel/templates/role-product-spec.md` and the lead's brief: `gov context DAEO-k7hz --role product-spec` refused (`BLOCKED: mandatory input 'DEC-1083' not found in the store`).

## Step 0: the sandbox check, before any work (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed: stop and return.

## Who and where
- You are a product-spec session (role `product-spec`, ticket `DAEO-k7hz`). Check: `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11`, `w2/W2-11`). Different: stop and say so.
- You write in `/home/usain/gov-os-worktrees/W2-11` only, inside the ticket's `allowed_paths`. An independent test designer writes the acceptance tests at the same time in another worktree from the same lines (DEC-959 item 7, DEC-963); you build to the ticket's lines, never to tests.
- **Policy 2 (c) (DEC-820 (c)):** never read `tests/acceptance/W2-11/` (its README and cases); every Grep or Glob call that could reach `tests/acceptance/W2-11/` excludes it (`!tests/acceptance/W2-11/**`), and so does every recursive Bash search (`grep -r --exclude-dir`, `rg -g '!…'`, `find … -prune`); if a search shows you a line from there anyway, stop reading it and say so in your return. You may run `gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11` and read only its pass/fail per line and counts (the round-2 cases are not merged yet: expect no row for the new lines). **(d):** never read the hidden half of any evaluation set by which you are measured.

## What to read
- The ticket (read-only): `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`, its KPI lines in full (S9, S13, S14, S15, S16, F1 are yours now) and the DEC-1137 note.
- The decisions, by id, in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`: DEC-952 (item 6), DEC-953 (item 7), DEC-851, DEC-974, DEC-983, DEC-982, DEC-979 (item 1, D2), DEC-991, DEC-994 (item 3), DEC-995, DEC-996, DEC-959 (item 5), DEC-832 (item 2), DEC-1137, DEC-1083, CAP-24.b, CAP-33.
- The files you change: `template/governance/kernel/templates/skill.md`; `template/governance/kernel/skills/orchestration/SKILL.md` and `briefs-and-returns.md`; `template/governance/kernel/skills/test-design/SKILL.md` and `test-kinds.md`; their copies in `.rulesync/skills/` and `template/.rulesync/skills/` (byte-identical to the kernel source today; keep them so); `docs/changes/W2-11-CIT-P.md`.
- **Memory (DEC-836):** use `gov retrieve` first, before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m gov.cli.main retrieve "<question>" --json`. **Search again once (DEC-1092 (1)):** if a bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found"; two searches in all. Never one giant query: a large question in batches (`--batch-size`, then `--continue <token>`) (DEC-860); a code question by small targeted code-graph traversal (DEC-859).
- **Guard read refusals (DEC-849):** the guard may still refuse some reads Policy 2 opened (searches from the repository root, `governance/project/` or `.claude/`). Take the refusal, never another spelling; search named folders; count them in your return.

## What to write (each rule traceable to its decision, ACCEPTED ids only, in brackets or at the line's end; a skill states a method and grants nothing, CAP-24.b; a project's own values as `<placeholders>`, DEC-539)
1. **S9, round 2's half, `templates/skill.md`:** close the front matter to `name`, `version`, `description` and a new `output` (the path class the skill's method writes, or `none`), plus `metadata.version` repeating `version` as the one carried key (rulesync carries only `metadata` into the generated copy, DEC-832 item 2; never drop it); say in the writer's comment that no other key stands, and name the permission fields that never stand there (`allowed-tools`, `permissions`, `paths`, `network`, `model`, `effort`) (DEC-995, DEC-996). Its **Never** section states that the skill changes no role's reads or writes, and that work needing other writes goes back as a package for the role that holds them (DEC-995, DEC-996).
2. **F1's rule:** in `skill.md` (its writing rules) the same rule for every skill: no permission field in a skill's front matter, and no step telling the skill's role to write what its output class does not hold (DEC-995, DEC-996). Check the twelve kernel skills' front matter yourself and report any permission field you find (expected: none) — do not add `output` to existing kernel skills (it would change their copies and versions beyond this round; name it in `discoveries` as a possible follow-up).
3. **S13 (the anti-drift kit), S14 (scope control), S16's skill half (approvals):** in **`briefs-and-returns.md`** (the orchestration skill's reference file), **three places, each under its own heading**, in the ticket's words where it gives them:
   - S13: a fresh orchestrator session every morning from a handover (checkpoint, RESUME HERE, the decisions in force); the digest loaded at start; every rule written into its five places (DEC-851) [DEC-952 item 6, DEC-953 item 7, DEC-983].
   - S14: a new ticket in the WBS goes to the owner as a P1 with a recommendation before it is filed; leads name a needed ticket in their return and never file one [DEC-974, DEC-983].
   - S16 (skill half): the orchestrator reads its own allow list at session start (the settings files' allow, ask and deny rules, and the host's known safety checks: for Claude Code, any `.claude/` path); before each command it classifies it as allowed or as possibly needing the owner's approval; such a call is never chained to other work; by day it notifies the owner first, then runs it; inside the project's `<quiet hours>` it never runs it and queues it for the morning package; one scenario each for day, night and a chained command [DEC-991, DEC-994 item 3].
   - **`SKILL.md` gains nothing beyond what its first paragraph already says** ("Detail: `briefs-and-returns.md`"): its body is at its cap (2,500 tokens = 10,000 characters; it is 9,976 now). If you must touch it at all, the body must stay `OK`.
4. **S15:** in test-design's `SKILL.md` (it has room: 1,345 tokens) or `test-kinds.md`: a timing test measures the work under test (its process's CPU time, or against a quiet reference run beside it), never the wall time of a loaded machine, at the same bound [DEC-979 item 1 D2, DEC-983]. Keep the load-sensitive row of `test-kinds.md` consistent with it.
5. **Versions:** raise the version of every skill whose text changes (orchestration, test-design: a minor raise each), in every place it stands: the kernel source, `.rulesync/skills/`, `template/.rulesync/skills/`, `version` and `metadata.version` alike. `skill.md` is a template: raise its own `version`/`metadata.version` only if it is the template's version (it shows `1.0.0` as the version a new skill starts at; leave that as the starting value and say so). The `.claude/**` copies follow by the copies ACT after the lead's DONE: **you never write `.claude/**`** (DEC-315, DEC-1112 (3)); list in your return each generated copy that now differs from its source.
6. **`docs/changes/W2-11-CIT-P.md`:** revise it as round 2: status PROPOSED; what round 2 changes (the lines above), evidence and corroboration; and these rows from the lead's verification: (a) the restore on the merged head verified line by line, S1 to S11 met in the sources; (b) `gov accept` before round 2: 99 passed, 7 failed (the seven copy cases, stale `.claude` copies, by design until the copies ACT), 1 skipped; (c) S12 has no text by design (first half retired by DEC-1137 (1), second half Wave 3, DEC-1083); (d) S16's template half has no file in W2-11's paths (a package with the CTO); (e) the generated copies to regenerate.
- **Never** write a `template/governance/kernel/templates/brief-*.md` (they stay pointers, DEC-1137), a role template (`role-*.md`), the role file `roles/orchestrator.md` (not needed this round), anything under `.claude/**`, `src/`, `tests/`, `.tickets/` or the register.

## Checks after every text change
- `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py /home/usain/gov-os-worktrees/W2-11/template/governance/kernel/skills/orchestration/SKILL.md /home/usain/gov-os-worktrees/W2-11/template/governance/kernel/skills/test-design/SKILL.md` must say `OK` for both (read-only tool outside your tree; reading is allowed).
- `cmp` each kernel file against its two `.rulesync` copies (identical).
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env).
- Run W1-35's and W1-37's skill cases on your result (not W2-11's): `env TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m pytest tests/acceptance/W1-35 tests/acceptance/W1-37 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` — to the end, never `-x`; report the counts; a red you caused is fixed in the text.

## Commit (one or more commits, your paths only)
`git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Implements: CAP-33, DEC-959, DEC-983, DEC-991, DEC-995, DEC-996, DEC-1137" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <paths>`. Name the CIT-P in the commit body (a kernel change, CAP-33). `Implements:` holds only ids from the ticket's `sources:` (you may also use DEC-974, DEC-979, DEC-994, DEC-952, DEC-953, DEC-982; nothing outside the list). No amend, rebase, reset, push or merge. The hooks: check `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` before each commit; never `--no-verify`.

## Rules
- **Machine (DEC-898):** your share of the lead's budget is 4 GB and 100,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-11` for every run; keep pytest's own retention; clean as you go; give `du -sh` / `du -s --inodes` of what you made in `evidence`. No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. No rebuild of the store.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string.
- **Protected material (DEC-820):** never read the held-out material's contents; never print a secret; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- **Command forms the guard reads:** one simple command per Bash call; literal paths; no here-documents, backticks, `bash -c '...'` or long inline `python3 -c` with braces; anything longer in a script file under `/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/` (Write tool). Never `pgrep`, `pkill`, `killall` or the Monitor tool.
- One role per ticket (DEC-995, DEC-996): work needing another role's writes is named in your return as a needed split, never routed round.
- Never ask or notify the owner. Install nothing.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). Never work around a refusal: report it.
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"): stop, return status `AUTH_REQUIRED`.

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
After the twelve fields: the sandbox check's result; the `body_tokens.py` lines; the generated copies that now differ from their sources (each path); whether you used `gov retrieve` (and how many searches); guard refusals met (`guard_refusals:` lines or `none`); `brief_gaps:` lines or `none`.
