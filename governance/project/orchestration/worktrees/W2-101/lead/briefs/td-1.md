# Brief: independent test designer, DAEO-6icv (W2-101), run 2, batch 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-6icv` (W2-101), profile STANDARD: three kernel
domain skills for the engineer, `frontend`, `ui-ux` and `devops`. You work only in the tests worktree
`/home/usain/gov-os-worktrees/W2-101-tests` on branch `w2/W2-101-tests` (DEC-963); you never read or write the
ticket's own worktree `/home/usain/gov-os-worktrees/W2-101`. You write the ticket's acceptance tests from its KPI lines,
its `## Interface` and its sources, in parallel with the product-spec worker (DEC-959 item 7), and you show them red
against the ticket's base.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6icv','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-6icv`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-101-tests` and
  `w2/W2-101-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732):** every test run and every `gov` command you use runs this worktree's own `src/`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101-tests/src` set per command. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101-tests/src python3 -c "import gov; print(gov.__file__)"` in your
  return. Your tests find the repository from their own location (as `tests/acceptance/W2-98/w2_98_support.py` does,
  `parents[...]` of the support file), never a fixed path, so that merged into `/home/usain/gov-os-worktrees/W2-101`
  they judge that worktree's files and code.
- **Reads (DEC-820):** open, except: (a) secrets and keys, never read or printed; (b) the held-out qualification
  material's contents (never read, print, search, diff or copy the held-out file under `governance/project/`, never
  type its path); **(c) the counterpart's work on this ticket: you never read anything the branch `w2/W2-101` adds or
  changes under `template/governance/kernel/skills/{frontend,ui-ux,devops}/` or their `.rulesync` copies** (by any
  tool; `git diff --name-only e09607093884...w2/W2-101` would name them; do not look); **(d)** never open the
  evaluation sets' root or any hidden or memory-verdict folder.
- **Search (DEC-1065):** no `gov retrieve` and no `gov context` inside the sandbox: search with the Read and Grep
  tools, naming the folder a search starts at; if the first search does not answer, search once more in different
  words, then work from what you read or say "not found". Grep the register only by id. Never search from the
  repository root, `governance/project/` or `.claude/`; name files there one by one. Never read `.claude/settings.json`.
- **Command forms the guard can read (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at
  literal absolute paths; anything longer than a line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-101-tests/.gov-runtime/scratch/td/` and you run that file.
- **Refused twice for the same call: stop and say so; no third try** (DEC-1142 (9)). Never work around a refusal by
  the guard, the sandbox or a hook: report it.
- Never copy the repository or a folder of it (no `cp -r` of the repo, `rsync`, `git archive`, `git worktree`,
  `git clone`). A test that needs a tree builds a small one under pytest's `tmp_path` (copying a few named files is
  fine). Install nothing (an install you need is a P1 package). No subagents that write. Never write `.gov-runtime/**`
  outside `.gov-runtime/scratch/`. Never ask or notify the owner.
- **DEC-911:** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits.
- **Never a real model call, never a key:** a case that runs `gov skilleval` uses a stub `claude` on a `PATH` you build
  (only the stub's folder, `/usr/bin`, `/bin`), as `tests/acceptance/W2-104/` does. No network.
- **Temp and pytest:** keep the sandbox's own `$TMPDIR` (never set it yourself, never `--basetemp`). Every pytest run
  goes through the slot tool:
  `PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-101-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-101 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  run to the end, never `-x`. A resource gate's refusal from the slot tool is a wait, not a refusal (DEC-1146): wait
  and run it again. Measure your scratch at the end (`du -sh`, `du -s --inodes`) and give the figures.

## What you read

- The ticket file `/home/usain/gov-os-worktrees/W2-101-tests/.tickets/DAEO-6icv.md` (read-only): its KPI lines,
  `allowed_paths`, sources and its `## Interface` section (the CTO's decision at claim, P-W2-100-IF-1 (a)).
- The sources by id in `docs/DECISION_REGISTER.md`: DEC-959 (items 4, 5, 7), DEC-957 (Q5), DEC-616, DEC-645, CAP-24.b
  (in `docs/contract/`), DEC-315, DEC-1112 (3); ROLES-RESEARCH-1 §2.7
  (`governance/project/orchestration/packages/ROLES-RESEARCH-1.md`, lines 135 to 156).
- The skill template `template/governance/kernel/templates/skill.md` (its eight sections and front matter) and an
  example skill with scenarios: `template/governance/kernel/skills/qa-review/` (`SKILL.md`, `scenarios.md`).
- The precedent suite you model yours on: `tests/acceptance/W2-98/` (the spec-writing skill: its own check script,
  the copies, the adapter check `python3 -m gov.adapters.portability` with `SOURCE_DIFFERS` / `GENERATED_DIFFERS`, and
  how it handles `.claude/skills/` and `rulesync`). And `tests/acceptance/W2-104/` for `gov skilleval` with a stub
  model, `--adopt` and `governance/project/skill-imports.yaml`.
- The skill validator `src/gov/check/skill_validator.py` (its docstring: `python3 -m gov.check.skill_validator
  <folder-or-file>`, findings JSON, exit 1) and the harness `src/gov/skilleval/harness.py` (docstring; exit codes in
  `src/gov/skilleval/command.py`: 3 a scenario failed, 6 adoption refused). These are shipped code, not the
  counterpart's work: read freely.
- The live guard `.claude/hooks/pretooluse.py` (for S2's guard half).

## The KPI lines (verbatim from the ticket)

Success:
- S1. Each of the three skills holds the area's conventions, a pre-commit checklist, the unit-test focus, its common
  mistakes and when to escalate, with ROLES-RESEARCH-1 §2.7's main points (frontend: accessibility, state, browser
  support; UI/UX: user flows reviewed by the owner as scenarios, not code; DevOps: hermetic builds, pinned versions,
  rollback). Verify: for each of the three skill folders a grep of its SKILL.md finds a heading or labelled line for
  conventions, pre-commit checklist, unit-test focus, common mistakes and when to escalate, and the area's named
  points; a planted copy missing one of them is named by the skill validator.
- S2. An engineer loads its domain skill beside the engineer role; the skill grants no permission. Verify: a planted
  engineer ticket naming the frontend skill launches with the skill listed beside the engineer role in the launch
  record; a grep of each skill's files for permission grants (allowed-tools, allow rules, permission keys) finds none,
  and the guard's decision for the engineer is the same with and without the skill loaded.
- S3. The skill follows the one skill template: front matter with name, version and a third-person description;
  When / not when; Inputs; Steps as a checklist; Done when; Output and handover in the twelve fields; Escalation
  mapped to P3/P2/P1/Emergency; Never; Sources at the end; the body under about 150 lines, details in reference files
  one level deep. Verify: the skill validator run on each of the three SKILL.md files exits 0; a grep of each finds the
  front matter keys name and version, the third-person description and each named section (Sources at the end);
  `wc -l` of each body is at most about 150 and each reference file sits one folder level below its skill folder.
- S4. Three test scenarios are written before the skill text and committed beside it; each runs on a fresh session
  with the skill loaded and passes, its transcript summarised in the scenario record. Verify: for each skill, `git log`
  shows the scenario files committed no later than the skill text; the scenario record holds three entries, each
  with a pass result and a transcript summary.
- S5. An imported skill or part is adopted only with its licence checked and recorded and its three scenarios
  passing. Verify: a planted imported part with a licence record and three passing scenarios is adopted; one with no
  licence record, and one with a failing scenario, are each refused naming the part.
- S6. The generated copies (.claude/skills/, .rulesync/skills/, template/.rulesync/skills/) match the template's
  source, regenerated by the adapter, not edited by hand. Verify: `diff -r` of each generated copy against the source
  shows no difference; a planted hand edit in one copy makes the adapter check print DRIFT naming the file.

Failure:
- F1. A domain skill that grants or implies a permission: a planted skill copy with an allowed-tools or permission
  line is refused naming the line; the three real skills pass.
- F2. A skill section missing, or the body far over size without reference files: a planted copy with the Never
  section removed, and one with a 400-line body and no reference files, each fail naming the section or the size;
  the real skills pass.
- F3. A scenario written after the skill text, or a skill adopted with a failing scenario: a planted history where the
  skill text is committed before its scenarios, and a planted scenario record with one failing result: each refused
  naming the skill; neither adopted.
- F4. An imported part with no licence record, or a forbidding licence: each refused naming the part; neither adopted.
- F5. A generated copy edited by hand or out of step: the adapter check prints DRIFT naming it; `diff -r` of each copy
  against the source is empty on the real tree.

## How the clauses read (the ticket's `## Interface`, with the lead's mapping and precision; test through this only)

**Numbering.** The ticket's Interface text was written with W2-100's failure numbering and applied to W2-101 "alike".
Map it by content: its "S1, F1 and F3" (section/point/permission named by I1) are W2-101's **S1, F1 and F2 (the
section half)**; its "F4" (commit order, failing scenario) is W2-101's **F3**; its "S6/F6" is W2-101's **S6/F5**; its
"F2" (a security P2 route) has no W2-101 counterpart: do not test it.

**I1, the skill's own check.** `template/governance/kernel/skills/<skill>/check_domain_skill.py` in each of the three
folders, standard library only, the three files byte-equal. Run as
`python3 <skill-folder>/check_domain_skill.py <path-to-SKILL.md>`. Output and exit:
- a refusal prints one or more lines `REFUSED <skill>: missing <name>` or
  `REFUSED <skill>: permission line <n>: <text>` and exits 1; otherwise it prints `PASS` and exits 0.
- `<skill>` is the SKILL.md front matter's `name` (`frontend`, `ui-ux`, `devops`); the area is chosen from that name,
  so a planted copy keeps its `name` and may sit in any folder.
- **Sections:** the template's eight `## ` headings, in this order: `When / not when`, `Inputs`, `Steps`, `Done when`,
  `Output and handover`, `Escalation`, `Never`, `Sources`; Sources last (no `## ` heading after it). An absent or
  out-of-order section is named by its heading text, e.g. `REFUSED frontend: missing Never`.
- **The five parts:** each present as a heading (`#`, `##` or `###`) or a labelled line (`**<Part>:**`, optionally as
  a list item), matched case-insensitively: `Conventions`, `Pre-commit checklist`, `Unit-test focus`,
  `Common mistakes`, `When to escalate`. A missing one is named, e.g. `REFUSED devops: missing Unit-test focus`.
- **The area's named points:** each present as a labelled line `**<Point>:**` (optionally a list item, label matched
  case-insensitively): frontend `Accessibility`, `State`, `Browser support`; ui-ux `User flows as scenarios`;
  devops `Hermetic builds`, `Pinned versions`, `Rollback`. A missing one is named by that label, e.g.
  `REFUSED frontend: missing Browser support`. (The ui-ux line's text says the owner reviews the flows as scenarios,
  not code; test the label only.)
- **Permission line:** any line of the file (front matter included; `<n>` is its 1-based line number in the file)
  that, after an optional list marker, backticks or quote, begins with `allowed-tools`, `allowed_tools`,
  `permissions`, `permission`, `allow` or `deny` followed by `:` (case-insensitive), e.g. `allowed-tools: Bash`.
- Whatever I1 leaves open (more refusal wording, other checks) you do not test.

**The skill validator** keeps its own halves: a front-matter permission key (`SKILL_PERMISSION_KEY`-style finding
naming the key) and the body size (the 400-line body is named by the validator's body-size finding, `key: body`).
The real three SKILL.md files must give no finding.

**S2.** Test now: the grep half (no `allowed-tools`, allow rule or permission key in any of the three folders' files)
and the guard half (the live guard's decision for an engineer on a set of representative calls is the same with a
planted `.claude/skills/frontend/` present and absent, in a tree you plant). "Listed beside the engineer role in the
launch record" is checked after the copies ACT places `.claude/skills/<skill>/`, not in this suite: do not test it.

**S4.** Each skill folder holds `scenarios.md` in W2-11's form (three `## <n>. <title>` headings with the bullets
`Situation`, `Expected`, `Pass line`; `gov skilleval` parses it), `scenario-records.yaml` written by `gov skilleval`
(key `records`; each entry `skill`, `scenario`, `verdict`, `run_at`, …) and a hand-written `scenario-summaries.md`
beside it, one entry per run (scenario, verdict, the record's `run_at`, a three-line summary of the reply). The
records and summaries arrive after the real `gov skilleval` runs, late in the ticket: the cases that read them are
**repository-state** cases and are red until then. The commit-order half: on the real history, the first commit that
adds each `scenarios.md` is no later than the first that adds its `SKILL.md` (read `git log` from the repository the
test sits in; if the repository is shallow or the files are absent, fail naming why).

**F3.** The commit-order half: the acceptance test reads `git log` on a planted history (a small git repository under
`tmp_path` where SKILL.md is committed before scenarios.md) with the same reading as on the real history and names
the skill; the failing-scenario half is `gov skilleval`'s exit 3 on a planted skill with a stub model whose judgement
fails one scenario, and `--adopt` refuses (exit 6) leaving `adopted: false`. No new adoption gate exists.

**S5/F4.** Through `gov skilleval <planted part> --adopt` with the stub model and a planted
`governance/project/skill-imports.yaml`: adopted with a full record (`licence_verdict: allowed`) and three passes;
refused (exit 6, the part named in the result) with no record, a forbidding `licence_verdict`, or a failing scenario.

**S6/F5.** `DRIFT` reads as the adapter check's `SOURCE_DIFFERS` and `GENERATED_DIFFERS`, naming the file. On the real
tree: `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/` hold the same files as the kernel source
(byte-equal); `.claude/skills/<skill>/` is placed by the copies ACT after the owner's yes (DEC-315; outside the
ticket's paths), so follow W2-98's handling for that copy (compare when present; say in the README how its absence is
treated, and that a merged-but-unplaced copy is not a pass of the `.claude` half). A planted hand edit in a planted
minimal tree's `.rulesync` copy is named `SOURCE_DIFFERS`.

## What you write

- Only `tests/acceptance/W2-101/**` in the tests worktree (support module, cases, `README.md`). Revise no earlier
  suite; if you find one that must change, return it as a package.
- In proportion (STANDARD): each KPI line's success and failure, run on each of the three skills where the line is
  per skill, plus the key edge cases; no combinatorial expansion.
- Planted copies: copy the real SKILL.md (and the check script) into `tmp_path` and edit it there; never edit the
  real files.
- A `README.md` mapping each KPI line (S1 to S6, F1 to F5) to its tests, with each case's expected red reason on the
  base, which cases are repository-state, and how the tests find the code.
- Red first: run the suite to the end against the base (your worktree, which holds none of the three skills). Every
  case that judges the real skills is red for the reason the README states (no skill folder, no check script); cases
  that judge shipped code only (the adapter, the validator and `gov skilleval` on planted input) may be green; name
  them.
- A KPI line you find ambiguous, untestable through the reading above, or in dispute is never a guess: return a
  package (question, why now, options with cost, recommendation, confidence).

## Commit

Commit only `tests/acceptance/W2-101/`, trailers in one final paragraph:

    git commit -m "W2-101 tests: <subject>" --trailer "Task: DAEO-6icv" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959, DEC-957, DEC-616, DEC-645, CAP-24.b" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-101

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):
task / status / work_completed / files_changed / evidence / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Include: the sandbox check first in `evidence`; your
commits' 12-digit hashes; the case count; each KPI line with its cases; the red result as you saw it (counts, and
which cases are green on the base and why); the `gov.__file__` line; the guard refusals you met (time, form, reason);
your scratch figures; any package. Status is one of DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED,
AUTH_REQUIRED.
