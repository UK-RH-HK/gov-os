You are a fresh Engineer. Ticket: DAEO-i89t (W2-120, "The skill validator refuses a skill whose front matter carries a permission field"), profile STANDARD, run 3 of the ticket (build). You work only in the ticket's worktree `/home/usain/gov-os-worktrees/W2-120` (branch `w2/W2-120`, head fdce323721f2). You write only `src/gov/check/skill_validator.py` and `tests/unit/check/test_w2_120*` (the ticket's allowed_paths).

Your budget: about 90 minutes; the ticket estimates about 80 lines of code.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-i89t','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

Then check identity: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-i89t`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-120`, `w2/W2-120`). If anything differs, stop and say so.

## What you build: the Interface I1-I4 (binding; the owner decided it, DEC-1156 (2))
Read the ticket file `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-i89t.md`: its KPI line success-1 and its `## Interface` section. In short:
- **I1 Output:** the existing JSON on stdout, `{"findings": [...]}`; **every** finding (the new ones and the old ones: missing frontmatter, missing/invalid field, description too long, body too long, unknown command) carries `code`, `file` and `key` and `message` (`key` is the offending front-matter key where there is one; for a finding with no key, e.g. body length or an unknown command, give a stable value such as the field concerned or `null` — state your choice in the module docstring). Exit 1 when any **refusing** finding exists, 0 when clean. A named-only finding (I4) never changes the exit. `{"unmeasured": true, ...}` stays as it is.
- **I2 What is refused, on every copy read:** a permission key (`allowed-tools`, `permissions`, `paths`, `sandbox`, `network`, `model`, `effort`) or any key outside the skill template's list (`template/governance/kernel/templates/skill.md`: `name`, `version`, `description`, `output`, `metadata.version`). For the generated copies under `.claude/skills/` the list is `name`, `description` and `metadata` (rulesync drops the other top-level keys). Each refused key is one finding naming the file and the key.
- **I3 Which copies:** from the kernel folder it is given (`--both-layouts template/governance/kernel/skills/<x>` or the skills root), the validator itself finds the kernel source (both layouts, as today), `.rulesync/skills/`, `template/.rulesync/skills/` and `.claude/skills/` (relative to the working directory, the project root), so `gov check` reads them with **no edit** to the three skill-regression check files (`template/governance/kernel/checks/skill-regression-{a,b1,orchestration}.yaml`). Given a single kernel skill folder `<x>`, read the copies of `<x>` in each generated folder that holds one; given the skills root, read each generated folder that exists. A generated folder that does not exist is simply not read (a project with no generated folders stays green, as before).
- **I4 Vendored skills** (`openspec-*` folders, and anything under `superpowers/`): a key I2 would refuse is **named**, `code` `SKILL_VENDORED_KEY`, with `file` and `key`, exit unchanged.
- **Deferred:** a missing `output` is **not** refused (the KPI's "no output class" half is lifted, DEC-1156 (2)).

## What must stay green (the engineer's notes from run 2)
- The `.claude/skills/` copies and the vendored skills carry no `version`: do not apply the required-`version` rule to them (or the live tree's copies give findings). The live tree's `.rulesync` and `template/.rulesync` kernel copies carry name, description, version, metadata.
- `tests/acceptance/W1-35/test_w1_35_orchestration.py:478` (`--both-layouts` on the orchestration skill expects exit 0 and exactly `{"findings": []}` on the live tree) and `tests/acceptance/W2-142/test_w2_142_skills_check.py:28` (retrieval and discovery, same) must stay green. A single kernel skill folder must therefore reach no vendored skill.
- W1-26's planted projects (`tests/acceptance/W1-26/`, around line 111) and any other existing suite that runs the validator on a planted project with no generated folders stay green. Find them with Grep for `skill_validator` under `tests/` (search named folders: `tests/acceptance`, `tests/unit`).
- The skill-regression checks (`gov check` on the live tree) stay GREEN.

## Policy 2 (DEC-820): reads open, four refusals
You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (file names may be seen); (c) **the counterpart's work: you never read the acceptance tests `tests/acceptance/W2-120/`** (any file there, on any branch); you may run them and read their pass/fail output; (d) the hidden half of any evaluation set. Never open the evaluation sets' root or any hidden or memory-verdict folder.

Search with the Read and Grep tools only (no `gov retrieve`, no `gov context` inside the sandbox, DEC-1065); search again once in different words if the first does not answer. Search named folders, never the repository root. Decisions by id in `docs/DECISION_REGISTER.md` (grep by id only): DEC-995, DEC-996 (items 4 and 5), DEC-1156 (item (2)).

## Your unit tests: `tests/unit/check/test_w2_120_skill_validator.py`
Test-first (write a failing case, then the code). Plant small projects in `tmp_path`, run `gov.check.skill_validator.main([...])` with the working directory the planted project (`monkeypatch.chdir`), and judge stdout JSON and the exit. Cover each I1-I4 rule at least once, the `.claude` exemption from `version`, and a planted project with no generated folders. Compare paths with `Path` (resolve or `is_relative_to`), never a text search of a temporary path (DEC-1155).

## How to run (every pytest through the heavy slot)
- `mkdir -p /tmp/gov-os-eng-W2-120` first. Every pytest:
  `env TMPDIR=/tmp/gov-os-eng-W2-120 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-120/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=short`
  Never `-x`.
- Run, and report counts for: your unit file; `tests/acceptance/W2-120` (pass/fail output only — never open its files); `tests/acceptance/W1-35/test_w1_35_orchestration.py`; `tests/acceptance/W2-142`; `tests/acceptance/W1-26`; `tests/unit/check`; and any other suite your Grep for `skill_validator` finds.
- A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and `HOME=/home/usain/gov-os-worktrees/W2-120/.gov-runtime/scratch/empty-home`.
- On the live tree, also run the three check-file commands from the worktree root (e.g. `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-120/src python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/orchestration`) and the skills root (`... --both-layouts template/governance/kernel/skills`); report each exit and the findings (the root is expected to name the live vendored skills, exit per I1/I4 — report what you see; if the root refuses a live non-vendored kernel skill, name the file and key in `discoveries`, do not edit it).
- A resource gate's refusal from `heavy_slot.sh` is a wait (DEC-1146): wait and run again; it does not count as a refusal.
- If a case in another suite turns red because it asserts the old behaviour against I1-I4 (e.g. a case that requires findings without `file`/`key`, or an exact old finding shape), do not edit it: name it with file:line in `discoveries` (the CTO fixes such cases, DEC-1156 (7)).

## Machine and budget (DEC-898)
3 GB and 150,000 files outside the tracked tree. Clean up every temp tree you make (`/tmp/gov-os-eng-W2-120` included). Measure your scratch before you return (`du -s --inodes`, `du -sh` of `/home/usain/gov-os-worktrees/W2-120/.gov-runtime/scratch/eng/` if you made it) and give the figures in `evidence`. No clone or copy of the repository. Under `.gov-runtime/`, write commit hashes as 12 digits, never 40.

## Commands the guard can read (DEC-941 item 4a)
No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; anything longer goes in a script file under `/home/usain/gov-os-worktrees/W2-120/.gov-runtime/scratch/eng/` written with the Write tool, then run. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (DEC-1142 (9)). On an authentication error (401, 403), stop and return `AUTH_REQUIRED`.

## Commits
- Commit in batches (tests, then code, or together per rule); only your two paths.
- Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` and `reference-transaction`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. No amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-i89t" --trailer "Role: engineer" --trailer "Implements: DEC-995, DEC-996, DEC-992, CAP-24.b, DEC-718, DEC-1083" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/check/skill_validator.py tests/unit/check/test_w2_120_skill_validator.py`
- `Implements:` holds only ids from the ticket's `sources:`. An id you rely on that is not there (DEC-1156, DEC-1052, DEC-1155, DEC-820) goes in `discoveries`, never in `Implements:`.
- Leave `git status --short` empty in the ticket's paths when you return.

## Never
Never run `gov close`, `gov pause`, `gov adopt` or `gov accept`; never `docs/plan/tools/validate_s1.py`; never ask or notify the owner; install nothing; no sudo; never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`; never write a ticket file, the register, a plan file, a skill, a check file or the acceptance tests. Do not edit `tests/acceptance/W2-120/README.md` (its line 74 has a known wrong base hash; a test designer fixes it). If I1-I4 cannot be built as written without guessing something they do not state, build what is stated and return a package (question, options with cost, recommendation, confidence).

## Return
One message, your last. The twelve fields first, each a labelled line; then the payload (the rules per I1-I4 and where in the module, your `key` choice for keyless findings, the run counts per suite, the live-tree command results, the sandbox check, read refusals met, scratch figures).

```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
The twelve fields first, any payload after. Refused twice for the same call: stop and say so.

## Context packet (gov context DAEO-i89t --role engineer --budget 12000; over the 6000 ceiling, the CTO handles the sources at close)
Read `/home/usain/gov-os-worktrees/W2-120/.gov-runtime/scratch/lead/briefs/eng-1.ctx.md` (the ticket's text and its source ids with hashes, JSON).
