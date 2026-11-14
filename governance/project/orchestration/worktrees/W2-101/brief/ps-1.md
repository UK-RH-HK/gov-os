# Brief: product-spec, DAEO-6icv (W2-101), run 2, batch 1

You are a fresh product-spec worker. Ticket: `DAEO-6icv` (W2-101), profile STANDARD: three kernel domain skills for
the engineer role, `frontend`, `ui-ux` and `devops`, each the engineer's skill for its area. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-101` on branch `w2/W2-101`. You write to the ticket's specification and KPI
lines (DEC-957: to fulfil the spec, never to make tests pass).

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6icv','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-6icv`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-101` and `w2/W2-101`).
  If anything differs, stop and say so.
- Run everything in the foreground, one command after another; your session ends with your last message. Return only
  after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **Reads (DEC-820):** open, except: (a) secrets and keys, never read or printed; (b) the held-out qualification
  material's contents (never read, print, search, diff or copy the held-out file under `governance/project/`, never
  type its path); **(c) the counterpart's work: never read `tests/acceptance/W2-101/`** (nor the worktree
  `/home/usain/gov-os-worktrees/W2-101-tests`) by any tool; **(d)** never open the evaluation sets' root or any hidden
  or memory-verdict folder.
- **Search (DEC-1065):** no `gov retrieve` and no `gov context` inside the sandbox: search with the Read and Grep tools,
  naming the folder a search starts at; if the first search does not answer, search once more in different words,
  then work from what you read or say "not found". Grep the register only by id. Never search from the repository
  root, `governance/project/` or `.claude/`; name files there one by one. Never read `.claude/settings.json`.
- **Command forms the guard can read (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at
  literal absolute paths; anything longer than a line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/ps/` (if that write is refused, under your session's own
  `$TMPDIR`) and you run that file.
- **Refused twice for the same call: stop and say so; no third try** (DEC-1142 (9)). Never work around a refusal by
  the guard, the sandbox or a hook: report it.
- Never copy the repository or a folder of it with `rsync`, `git archive`, `git worktree` or `git clone`. Install
  nothing. No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never ask or notify
  the owner. Keep the sandbox's own `$TMPDIR`; never set it. Any pytest goes through
  `PYTHONUSERBASE=/home/usain/.local bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest … -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (you should need none). A resource gate's refusal is a wait (DEC-1146).
- **DEC-911:** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits.
- **No real model call:** you do not run `gov skilleval`; the lead runs it on the real model after your batch.

## What you read

- The ticket `/home/usain/gov-os-worktrees/W2-101/.tickets/DAEO-6icv.md` (read-only): KPI lines, `allowed_paths`,
  sources and its `## Interface` (the CTO's decision at claim).
- The sources by id in `docs/DECISION_REGISTER.md`: DEC-959 (items 4, 5), DEC-957 (Q5 and the escalation rubric
  P3/P2/P1/Emergency), DEC-616, DEC-645, CAP-24.b (`docs/contract/`), DEC-315, DEC-1112 (3); and
  ROLES-RESEARCH-1 §2.7 (`governance/project/orchestration/packages/ROLES-RESEARCH-1.md`, lines 135 to 156): the
  content of the three skills comes from there.
- The skill template `template/governance/kernel/templates/skill.md` (follow it exactly; delete its comment) and its
  model skills: `template/governance/kernel/skills/qa-review/` (`SKILL.md`, `scenarios.md`: the scenario form) and
  `template/governance/kernel/skills/spec-writing/` (`SKILL.md`, its own check script `check_spec.py`: the model
  for I1's shape, and its byte copies in `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/`).
- The engineer role file `template/governance/kernel/roles/engineer.md` (what the skill sits beside; never restate its
  permissions).
- The tools you check with: `src/gov/check/skill_validator.py` (docstring), `src/gov/adapters/portability.py`
  (`python3 -m gov.adapters.portability`), `src/gov/skilleval/harness.py` (docstring: the `scenarios.md` form it
  parses).

## What must be true (the KPI lines, verbatim)

- S1. Each of the three skills holds the area's conventions, a pre-commit checklist, the unit-test focus, its common
  mistakes and when to escalate, with ROLES-RESEARCH-1 §2.7's main points (frontend: accessibility, state, browser
  support; UI/UX: user flows reviewed by the owner as scenarios, not code; DevOps: hermetic builds, pinned versions,
  rollback).
- S2. An engineer loads its domain skill beside the engineer role; the skill grants no permission (no
  `allowed-tools`, allow rule or permission key anywhere in the skill's files).
- S3. The skill follows the one skill template: front matter with `name`, `version`, a third-person `description`
  (what it does and when, under 60 tokens), `output`, `metadata.version`; When / not when; Inputs; Steps as a
  checklist; Done when; Output and handover in the twelve fields; Escalation mapped to P3/P2/P1/Emergency; Never;
  Sources at the end; the body under about 150 lines, details in reference files directly in the skill's folder (one
  level deep), each linked from the body, none linking on.
- S4. Three test scenarios per skill are written before the skill text and committed beside it (they run later on a
  fresh session through `gov skilleval`, run by the lead).
- S5. Nothing is imported or copied from another collection (Anthropic's or other) unless its licence is checked and
  recorded and its three scenarios pass. **Write all three skills yourself; import nothing.** If you think an import
  is needed, return a package instead.
- S6. The generated copies `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/` are byte-equal to the
  kernel source folder (every file). `.claude/skills/<skill>/` is out of your paths: the copies ACT places it after
  the owner's yes (DEC-315, DEC-1112 (3)); never write there.
- F1 to F5: no permission line; no section missing; the body not far over size; scenarios not after the text; no copy
  edited out of step.

## The interface you build to (the ticket's `## Interface`, with the lead's precision; the test designer tests this)

**I1, `check_domain_skill.py`:** one standard-library Python script at
`template/governance/kernel/skills/<skill>/check_domain_skill.py` in each of the three folders, the **three files
byte-equal**. Run as `python3 <skill-folder>/check_domain_skill.py <path-to-SKILL.md>`.
- Refusal: prints one line per finding, `REFUSED <skill>: missing <name>` or
  `REFUSED <skill>: permission line <n>: <text>`, and exits 1. Otherwise prints `PASS` and exits 0. A file it cannot
  read or with no front matter `name` is a refusal (exit 1), never a pass.
- `<skill>` is the SKILL.md front matter's `name`; the area (its point list) is chosen from that name, so the script
  works on a copy in any folder. A name with no point list is refused (`REFUSED <name>: missing point list`).
- **Sections:** the template's eight `## ` headings, in order: `When / not when`, `Inputs`, `Steps`, `Done when`,
  `Output and handover`, `Escalation`, `Never`, `Sources`; Sources last (no `## ` heading after it). An absent or
  out-of-order section is named by its heading text (`REFUSED frontend: missing Never`).
- **The five parts:** each a heading (`#` to `###`) or a labelled line `**<Part>:**` (optionally a list item),
  matched case-insensitively: `Conventions`, `Pre-commit checklist`, `Unit-test focus`, `Common mistakes`,
  `When to escalate` (`REFUSED devops: missing Unit-test focus`).
- **The area's named points:** each a labelled line `**<Point>:**` (optionally a list item, case-insensitive):
  frontend `Accessibility`, `State`, `Browser support`; ui-ux `User flows as scenarios`; devops `Hermetic builds`,
  `Pinned versions`, `Rollback` (`REFUSED frontend: missing Browser support`). The point lists live in the script.
- **Permission line:** any line of the file, front matter included (`<n>` 1-based), that after an optional list
  marker, backticks or quote begins with `allowed-tools`, `allowed_tools`, `permissions`, `permission`, `allow` or
  `deny` followed by `:` (case-insensitive). So the skills' own text must never start a line that way.
- About 100 lines; no other checks needed. The skill validator keeps the front-matter permission key and size halves.

**Where the parts go.** Put the five parts and the named points where the template lets them sit naturally (for
example Conventions, Unit-test focus and Common mistakes as labelled lines or `###` sub-headings under Steps or a
reference file linked from Steps; the Pre-commit checklist as checklist items; When to escalate under Escalation,
mapped to P3/P2/P1/Emergency). They must be in SKILL.md itself (I1 reads only SKILL.md); details may go to one
reference file per skill if the body would pass about 150 lines. The ui-ux `User flows as scenarios` line must say the
owner reviews user flows as scenarios, not code. Each skill states a method and grants nothing (CAP-24.b); it refers
to rules the briefs already carry rather than restating them; every `gov <command>` in a code span must be a recorded
command (the validator checks).

**Scenarios (S4).** Each folder's `scenarios.md` holds exactly three scenarios in the form `gov skilleval` parses:
`## <n>. <title>` (n = 1, 2, 3), each followed by the bullets `- **Situation:** …`, `- **Expected:** …`,
`- **Pass line:** …`. Each Situation is something a fresh session holding only that skill can act on in one reply
(no repository access is guaranteed: give the material in the Situation itself, for example a short diff, a component,
a Dockerfile or CI file, or a flow description), and each Pass line is judgeable from the reply alone. Cover, per
skill, the named points (for example frontend: an inaccessible control and unmanaged state in a diff; ui-ux: a
requested change to a user flow that the owner must review as a scenario, not code; devops: an unpinned base image or
a deploy without a rollback path) and one escalation case. `scenario-records.yaml` and `scenario-summaries.md` come
later from the lead's `gov skilleval` runs; do not write them.

## Batches and commits (the order matters: S4, F3)

1. **Commit A, the scenarios first:** the three `scenarios.md` files only (kernel source folders), one commit.
2. **Commit B, the skill text:** each `SKILL.md`, the three byte-equal `check_domain_skill.py`, any reference file.
3. **Commit C, the copies:** byte copies of each kernel source folder into `.rulesync/skills/<skill>/` and
   `template/.rulesync/skills/<skill>/` (every file, `scenarios.md` included).

Before commit B and again after C, check and quote the results:
- `python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md` → `PASS`, each skill;
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.check.skill_validator template/governance/kernel/skills/frontend template/governance/kernel/skills/ui-ux template/governance/kernel/skills/devops` → no finding, exit 0;
- `wc -l` of each SKILL.md body (lines after the front matter) ≤ about 150;
- `cmp` of the three check scripts, and `diff -r` of each kernel folder against its two `.rulesync` copies → empty;
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.adapters.portability` → no finding naming the three skills (findings about `.claude/skills/<skill>` being absent are expected until the copies ACT; quote them);
- show I1 bites, in your scratch: a copy with `## Never` removed, one without the `**Browser support:**` line, and one with an `allowed-tools: Bash` line each give the expected `REFUSED` line and exit 1.

Every commit carries the trailers in one final paragraph and names only your paths:

    git commit -m "W2-101: <subject>" --trailer "Task: DAEO-6icv" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-957, DEC-616, DEC-645, CAP-24.b, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

## The acceptance tests

The independent test designer writes `tests/acceptance/W2-101/` in parallel; your lead merges them into your branch.
You never read them. If `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/TESTS-READY` exists once your
commit C exists, run them once through `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.cli.main accept W2-101 --root /home/usain/gov-os-worktrees/W2-101`
and report its result per KPI line (some repository-state cases stay red until the lead's `gov skilleval` runs and
the scenario summaries: name them). If it does not exist, return after commit C.

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):
task / status / work_completed / files_changed / evidence / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Include: the sandbox check first in `evidence`; your
commits' 12-digit hashes with subjects; each check's output above; the body line counts; the lines added; anything
you chose where the interface left something open; the guard refusals you met (time, form, reason); any package
(question, options with cost, recommendation, confidence). Status is one of DONE, PACKAGES, ESCALATION,
ESCALATION_BLOCKED, LAUNCH_BLOCKED, AUTH_REQUIRED.
