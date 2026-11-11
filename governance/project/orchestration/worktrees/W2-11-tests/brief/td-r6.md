# Brief: independent test designer, W2-11 (DAEO-k7hz) round 2 (DEC-916), STANDARD

Hand-written by the ticket lead from `template/governance/kernel/templates/role-test-designer.md` and the lead's brief: `gov context DAEO-k7hz --role independent-test-designer` refused (`BLOCKED: mandatory input 'DEC-1083' not found in the store`).

## Step 0: the sandbox check, before any work (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed: stop and return.

## Who and where
- You are the independent test designer (role `independent-test-designer`, ticket `DAEO-k7hz`). Check: `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11-tests`, `w2/W2-11-tests`). Different: stop and say so.
- You work and commit **only** in `/home/usain/gov-os-worktrees/W2-11-tests`, and only under `tests/acceptance/W2-11/`: `test_w2_11_skills.py`, one new file for round 2 (e.g. `test_w2_11_round2.py`), `w2_11_support.py` (helpers) and `README.md` (the map). The brief cases (`test_w2_11_briefs.py`) and the supersession and brief-gap files are not yours to touch again.
- An implementer (a product-spec worker) writes the text at the same time, in the other worktree, from the same lines (the work order in parallel, DEC-959 item 7, DEC-963). Neither waits for the other.

## What to read
- The ticket (read-only): `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`: its KPI lines in full (front matter) and the DEC-1137 note. Its numbering: success S1..S16, failure F1, F2.
- The decisions, by id, in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`: DEC-959 (item 5), DEC-995, DEC-996, DEC-983, DEC-982, DEC-952 (item 6), DEC-953 (item 7), DEC-851, DEC-974, DEC-979 (item 1, D2), DEC-991, DEC-994 (item 3), DEC-832 (item 2), DEC-1137, DEC-1083, DEC-221, DEC-951.
- Your own earlier work in this folder (tests, `w2_11_support.py`, README): it is yours; read it. Its `folder_texts` helper reads a skill's folder (`SKILL.md` plus its reference files), as the S4 case already does.
- The existing code and kernel text **as it stands on `w2/integrate`**: `git show w2/integrate:<path>`.
- **Policy 2 (c), the counterpart's work (DEC-820 (c)):** never read this ticket's implementation: the files `git diff --name-only w2/integrate...w2/W2-11` names, other than your own tests under `tests/acceptance/W2-11/` (that list includes the kernel skills, their `.rulesync` and `.claude` copies, `templates/skill.md` and the CIT-P). Read their `w2/integrate` form, or work from the ticket's lines. **(d):** never read the hidden half of any evaluation set by which you are measured. Reviewers read everything; you do not.
- **Memory (DEC-836, DEC-963):** ask the integration store first, before reading files at random: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` (outside a sandbox), or, if that is refused inside the sandbox, the Read and Grep tools on `git show w2/integrate:<path>` (DEC-1065). **Search again once (DEC-1092 (1)):** if a bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found"; two searches in all. Never one giant query: a large question in batches (`--batch-size`, then `--continue <token>`) (DEC-860); a code question by small targeted code-graph traversal, never a load of the whole graph (DEC-859). **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (its `allowed_paths` outside `tests/acceptance/`) and name in your return each such result you were served.
- **Guard read refusals (DEC-849):** the guard may still refuse some reads Policy 2 opened (searches from the repository root, `governance/project/` or `.claude/`). Take the refusal, never another spelling; search named folders instead; count the refusals in your return.

## What to write (round 2, in proportion: the minimum that shows each line, STANDARD: each line's success and failure plus the key edge cases, DEC-221, DEC-951 item 5)
Cases, each **red on the base** (this worktree's head as it is now), with a README row in the code-span form `gov accept` reads (full node ids, `test_<file>.py::test_<name>`, under the ticket's numbering `success-N` / `failure-N`) and its red reason:
1. **success-9, round 2's half** (`template/governance/kernel/templates/skill.md`): its front matter is closed to `name`, `version`, `description` and `output` (the path class the skill's method writes, or none), plus `metadata.version` as the one carried repeat of `version` (rulesync carries only `metadata` into the generated copy; DEC-832 item 2): no other key; no permission field (`allowed-tools`, `permissions`, `paths`, `network`, `model`, `effort`); and a **Never** section stating that the skill changes no role's reads or writes and that work needing other writes goes back as a package for the role that holds them (DEC-995, DEC-996). Add these to the existing success-9 row (keep the round-1 cases).
2. **success-13** (the anti-drift kit), **success-14** (scope control) and **success-16's skill half** (the approvals section; one scenario each for day, night and a chained command): read **the orchestration skill's folder** (`SKILL.md` and its reference files, via `folder_texts`), not `SKILL.md` alone: `SKILL.md`'s body is at its cap (2,500 tokens, `ceil(characters / 4)`, W1-35's case and the skill validator), so the text will stand in a reference file. A case never asks `SKILL.md` for text it cannot hold. Match ideas, not fixed sentences (your README's reading rules), except where the ticket quotes words.
3. **success-15** (a timing test measures the work under test, its process's CPU time or against a quiet reference beside it, never the wall time of a loaded machine, at the same bound; DEC-979 item 1 D2): read the test-design skill's folder (`SKILL.md` and its reference files).
4. **failure-1** (DEC-995, DEC-996): every kernel skill (`template/governance/kernel/skills/*/SKILL.md`; not the vendored skills, not openspec; `adopt` is W2-52's for its version line only), its generated copy (`.claude/skills/<name>/SKILL.md`) and `skill.md` carry no permission field in their front matter, and no step telling the skill's role to write what its output class does not hold. Show the check with a planted file in `tmp_path` (as the DEC-866 failure-2 cases do) as well as on the real files. If a case on the generated copies is red only because the copies are stale (they are regenerated by a class (b) ACT after the lead's DONE), its README red reason says so in those words.
- **No case** for success-12 (retired / Wave 3) and none for success-16's template half (no file in this ticket's paths; a package the lead holds). Leave the README's success-12 row as it is. Move the round-2 lines out of the "not in the table" paragraph into the table.
- No name of code to be written (DEC-462): you state behaviour and sources. Text checks of files; deterministic; no network; planted files in `tmp_path`; no copy of the tree.
- **Show red:** `env TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` in your worktree, to the end (never `-x`): every new case fails for its README reason; the existing cases keep their results (seven copy cases are already red on this base, by design: the copies ACT). Also `gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11-tests` once, to show the README map reads (no `ACCEPT_MAP_UNREADABLE`). A new case green on the base: fix it or report it.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src` set **per command** (never in a session's `--settings` env).
- An ambiguous line is never guessed: return it in `proposed_decisions` with options, recommendation and confidence. If `metadata.version` cannot be read as the one carried repeat under the closed set, return the exact conflict; never drop `metadata.version`.

## Commit
`git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959, DEC-983, DEC-991, DEC-995, DEC-996" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-11/<files>`. Only your paths; no amend, rebase, reset or push; no merge (the lead merges). `Implements:` holds only ids from the ticket's `sources:`.

## Rules
- **Machine (DEC-898):** your share of the lead's budget is 4 GB and 100,000 files and folders outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-11` for every run; keep pytest's own retention, no `--basetemp`; clean as you go; measure `du -sh` and `du -s --inodes` of what you made and give the figures in `evidence`. No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string.
- **Protected material (DEC-820):** never read the held-out material's contents; never print a secret; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- **Command forms the guard reads:** one simple command per Bash call; literal paths, no shell variable as a write target; no here-documents, backticks, `bash -c '...'` or long inline `python3 -c` with braces; anything longer in a script file under `/home/usain/gov-os-worktrees/W2-11-tests/.gov-runtime/scratch/` (Write tool), run with `bash`/`python3`. Never `pgrep`, `pkill`, `killall` or the Monitor tool.
- Never ask or notify the owner. Install nothing. Never write `.claude/**`.
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
After the twelve fields: the sandbox check's result; each new case with its red reason as observed; whether you used `gov retrieve` (and how many searches); any P-R1 results served; guard refusals met (`guard_refusals:` lines or `none`); `brief_gaps:` lines or `none`.
