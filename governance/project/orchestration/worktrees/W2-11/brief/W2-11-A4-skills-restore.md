# W2-11 (DAEO-k7hz): put W2-11's own skill text back onto the merged head (one product-spec session, one commit, after the merge of `w2/integrate`)

You are a fresh **product-spec** session (Sonnet, high; class C3, kernel control paths), launched under W2-11's ticket (`.tickets/DAEO-k7hz.md`), in W2-11's worktree. `EMG-common.md`, `NIGHT-common.md` and `LIFT-common.md` (beside this file in `.gov-runtime/scratch/orchestrator/briefs/`) hold where this file does not change them (the lift's closes are done, the main tree stays clean, the next free decision id is DEC-1139: you never write a decision). Commit hashes in anything you write under `.gov-runtime/` are 12 digits (row W2-L423's rule).

## Why you
`w2/integrate` is merged into `w2/W2-11` (merge `4e265aabed5c`). To make that merge possible inside no sandbox, two earlier product-spec commits made the five brief templates and twelve skill files equal to integrate's text (`b5f3679c7c18`, `a78d0974d908`, the pre-merge form); W2-11's own text of the twelve skill files is therefore not on the branch now. It is kept in the history, at `c16dbf41ea77` (W2-11's head before the merge); the common ancestor of the two sides is `c38a5b49bc86`. **Your job: put W2-11's skill text back onto the merged head, hunk by hunk, by the rules below, in one commit.**

Four skills, each in three places (the kernel source, `.rulesync/`, `template/.rulesync/`), 12 files in all. The three copies of a skill are one text at every commit (checked: same blob in all three places at `c16dbf41ea77`, at the base and on the merged head): resolve once, then write the same text into the three places.

**What you do not touch (hard):**
- **`.claude/`** in any form (the generated copies; your sandbox keeps it read-only, DEC-315, DEC-1112 (3)). You only list for the CTO which copies now differ (step 6).
- **The five brief templates** `template/governance/kernel/templates/brief-*.md`: they stay the one-line pointers integrate has (DEC-1137 (1), the owner, 2026-11-11, option (c) of DEC-105).
- Any file but the 12 below: no `tests/`, `src/`, `docs/`, `.tickets/`, the register, the role files, the other skills (`audit`, `change`, `checkpoint`, `planning`, `qa-review`, `adopt`), the orchestration skill's reference files.

The 12 paths (each relative to the worktree):
```
template/governance/kernel/skills/discovery/SKILL.md
template/governance/kernel/skills/orchestration/SKILL.md
template/governance/kernel/skills/retrieval/SKILL.md
template/governance/kernel/skills/test-design/SKILL.md
.rulesync/skills/discovery/SKILL.md
.rulesync/skills/orchestration/SKILL.md
.rulesync/skills/retrieval/SKILL.md
.rulesync/skills/test-design/SKILL.md
template/.rulesync/skills/discovery/SKILL.md
template/.rulesync/skills/orchestration/SKILL.md
template/.rulesync/skills/retrieval/SKILL.md
template/.rulesync/skills/test-design/SKILL.md
```

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-11`, branch `w2/W2-11`. First calls: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-k7hz`); `git -C /home/usain/gov-os-worktrees/W2-11 rev-parse --show-toplevel --abbrev-ref HEAD`; `git -C /home/usain/gov-os-worktrees/W2-11 status --short` must be empty; `git -C /home/usain/gov-os-worktrees/W2-11 rev-parse --short=12 HEAD` must be `4e265aabed5c`. Anything else: stop and return PACKAGES (the CTO runs this session alone in the tree, before the test designer's).
- Your scratch: `/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/restore/` (inside the worktree, untracked, no approval needed; `TMPDIR` the same folder or your session scratchpad). Never a new `/tmp/gov-os-*` folder.

## The method (read-only first, then write)
For each of the four skills (kernel path shown; the other two places take the same text):
1. Get the three versions into your scratch (literal paths, one command per call), for example for `discovery`:
   `git -C /home/usain/gov-os-worktrees/W2-11 show c38a5b49bc86:template/governance/kernel/skills/discovery/SKILL.md` into `restore/discovery.base`, the same with `c16dbf41ea77:` into `restore/discovery.old`, and with `HEAD:` into `restore/discovery.cur` (the Write tool cannot capture command output: use the shell's `>` with the literal path, one command per call; if the guard refuses that form, take the file with the Read tool and write it with the Write tool, and say so in your return).
2. `git merge-file -p -L integrate-HEAD -L base -L W2-11 restore/discovery.cur restore/discovery.base restore/discovery.old` into `restore/discovery.merged` (exit 1 is the number of conflict hunks, not an error). **Expected hunks: discovery 1, retrieval 1, test-design 2, orchestration 5 (9 in all).** A different count means integrate or the branch moved: stop and return PACKAGES.
3. Everything the merge kept outside a hunk stays as it is: those lines are W2-11's additions that do not touch integrate's text (for example orchestration's reference-file line, its work-order line, the lead's return forms and its other session lines) and integrate's own edits. **Do not edit outside the hunks.**
4. Replace each hunk by the text the rule below gives. Write the resolved file with the Write tool (the whole file) to the kernel path, then the **identical** text to the two `.rulesync` paths. No conflict marker may remain.

## The rules, per hunk (the CTO's reading of `drafts/w2-11/RESOLUTION.md` section 5, checked against the merged head on 2026-11-11; W2-11's additions are kept where they do not contradict integrate's newer text, integrate's text is kept elsewhere)

**`discovery`, one hunk (the version lines).** Integrate's `version: "1.1.0"` (W2-142: search again once) plus W2-11's `metadata:` block with the **same** number. Replacement:
```
version: "1.1.0"
metadata:
  version: "1.1.0"
```
**`retrieval`, one hunk (the same).** The same three lines.

**`test-design`, hunk 1 (front matter).** The number is **1.3.0** in both places (integrate went 1.0.0 to 1.2.0, W2-11 1.0.0 to 1.1.0: two independent changes; 1.3.0 states both); the description is W2-11's. Replacement:
```
version: "1.3.0"
metadata:
  version: "1.3.0"
description: Method for independent test design from the specification and KPIs, in parallel with the implementer and never reading its work.
```
**`test-design`, hunk 2 (the work order, the read rule, the Inputs).** W2-11's three bullets and its Inputs stand (DEC-959 item 7 is a KPI line: keep "the work order in parallel"). Fold in integrate's two facts: the designer may read the integrated code it works with, on the integration branch (DEC-963, DEC-820), and never this ticket's implementation (W2-11's second bullet already says it). Integrate's citation letter `CAP-38.c` stands over W2-11's `CAP-38.b` (checked in `docs/contract/`: `CAP-38.c` is "Independent test authorship", `CAP-38.b` is the governance test families). **Do not write the branch name `w2/integrate`** in this skill (W2-11's case `test_no_id_or_path_of_this_repository_in_a_kernel_file` refuses it: say "the integration branch"). Replacement (everything between the two markers, including the blank line and the `## Inputs` heading, which sit inside the hunk):
```
- The work order is in parallel: the designer works from the specification and the KPIs beside the engineer, at the same time as it builds the code from the same specification, in a worktree of its own, and never reads its work; neither waits for the other (DEC-959 item 7, DEC-963).
- It never reads this ticket's implementation: no file the ticket's branch changes against its base, other than its own tests; a retrieval or search result under those paths is dropped unread and named in its return (DEC-820 (c)). It may read the integrated code it must work with, on the integration branch (DEC-963, DEC-820). Its retrieval uses the integration branch's store, never the ticket worktree's (DEC-963 item 2). Everything else is open to it (DEC-820).
- When its tests are committed, the lead merges them and the implementer runs them once, reading results only, through the project's opaque acceptance runner where it has one (DEC-959 item 6).

## Inputs

1. The ticket: its specification, its KPIs (success and failure lines) and its acceptance test path (CAP-38.c).
2. The public interfaces the ticket must work with, as they stand on the integration branch (CAP-38.c, DEC-963).
3. Probe or QA findings, when present, as described behaviours (DEC-136, CAP-38.e).
```
Then the file's last section lists its sources on one line (`CAP-24.b, CAP-38.b, ...`): **add `CAP-38.c`** to it (the body now cites it), in id order; change nothing else on that line.

**`orchestration`, hunk 1 (version).** Replacement:
```
version: "1.3.0"
metadata:
  version: "1.3.0"
```
**`orchestration`, hunk 2 (the lead line, the ceiling line).** Integrate's wording for the lead line (the envelope and the role template, DEC-236, DEC-1050); W2-11's second line, which replaces integrate's "A stated ceiling holds: at most `<ceiling>` tickets in flight" (that sentence is what DEC-866, DEC-847 and DEC-942 forbid and what integrate's own W1-35 revision removed from the test: **do not keep it**). Replacement:
```
- A ticket lead per ticket is started in that worktree with its identity (the orchestrator role and the ticket's id), from the brief envelope `brief.md` and the lead template `role-lead.md` (DEC-236, DEC-1050).
- No fixed number of tickets in flight: the eligible tickets, the resource gate and the owner's usage limits decide, each time a slot could open; every countdown says how many and why (DEC-847). A ticket idle on an owner answer frees its slot (DEC-235, DEC-363).
```
**`orchestration`, hunk 3 (session start and the returns).** Integrate's first line (the envelope plus the role templates; the five retired texts are pointers); W2-11's second line (the twelve fields, the payload after, the two-refusal stop, CAP-37, AR-6). **Drop W2-11's first line** ("Each carries the standing sentences word for word (DEC-537)": it names the five retired templates). Replacement: integrate's one line, unchanged, followed by this line:
```
- Every return starts with the twelve fields, each a labelled line: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action (CAP-37). Any payload comes after them. Stop after two identical refusals and return (AR-6).
```
(the hunk's own marker text shows both lines in full: copy integrate's first line from the `integrate-HEAD` side exactly).

**`orchestration`, hunk 4 (the checkpoint).** Integrate's line (DEC-1057: no committed record is required at each round boundary), with W2-11's sentence added at its end, on the same line, after one space: `A checkpoint is written at every handover (DEC-837 item 3).` Drop W2-11's own first sentence ("A lead writes a real checkpoint with `gov checkpoint` at each round boundary of its ticket"): integrate's line already says a lead's checkpoint is a real one and DEC-1057 changed the round-boundary rule.

**`orchestration`, hunk 5 (hygiene and Policy 2).** Integrate's three lines, unchanged (the temporary folder; reads open; the held-out contents never read): they carry Policy 2 and DEC-820 and cover the words of W2-11's own two lines. Drop W2-11's two lines.

## The size cap: the merged orchestration skill is 780 characters too long, and 21 tightenings bring it under (the helper's finding, 2026-11-11)
The orchestration skill's body (the text after the front matter) is capped at **2,500 tokens**, counted as `ceil(characters / 4)`: at most **10,000 characters**. The cap is held twice: W1-35's case `test_w1_35_orchestration.py::TestOrchestrationSkillForm::test_the_body_is_within_2500_tokens` and the skill validator (`gov check`'s skill regression family, a hard block: `TestSkillRegressionGreen` goes red). Both sides grew the skill (integrate to 9,718 characters, W2-11 to 9,999, from a base of 8,922); after the hunk rules above the body is **10,780 characters (2,695 tokens), over the cap**. The other three skills fit (discovery 780, retrieval 905, test-design 1,342 tokens; description at most 60 tokens). W2-11's own round 1 stayed under by keeping detail in `briefs-and-returns.md`, but W1-35's rows (the corpus is the skill plus the templates the skill names, not the skill's own reference files) pin most of the skill's sentences, so the room has to come out of wording, never out of an idea.

**After the nine hunks, apply the 21 tightenings below to the orchestration text** (each `-` fragment occurs exactly once, inside one line unless the fragment shows a line break; replace it by the `+` fragment; an empty `+` means delete the fragment). Each keeps its idea and its decision ids. The helper measured the result on a scratch clone: the body is **9,976 characters (2,494 tokens)**; W2-11's folder and W1-35's orchestration cases and `TestSkillRegressionGreen` pass except the seven copy cases named below. If you prefer other words, you may use them, but the body stays at or under 10,000 characters and **no idea is dropped**; three tightenings the helper tried were refused by the cases and are not to be used: removing the five retired `brief-*.md` names (`test_the_skill_names_the_five_brief_templates`), merging the two Stops lines (`test_dec_486_is_not_cited_for_the_stops_short_block`), removing the work-order bullet's "red" clause entirely.

```diff
-  The retired texts `brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md` and `brief-lead.md` are one-line pointers to these templates (DEC-1050).
+  The retired `brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md` and `brief-lead.md` point to these (DEC-1050).

- ; then the verification, on the ticket's acceptance tests, the scoped selection and the builder tests, once (MR-3, DEC-968).
+ ; then one scoped verification (MR-3, DEC-968).

- The merge queue: [integration-queue.md](integration-queue.md). A red nightly: [nightly-sheriff.md](nightly-sheriff.md). An Emergency: [incident-response.md](incident-response.md).
+ Merge queue: `integration-queue.md`; red nightly: `nightly-sheriff.md`; Emergency: `incident-response.md`.

- nothing is left in another session's folders, and reading them is open as the next line states (DEC-386, DEC-537, DEC-820).
+ nothing is left in another session's folders (DEC-386, DEC-537).

- the held-out material's contents, the counterpart's work on the same ticket and the hidden half of an evaluation set (DEC-820, DEC-1052).
- - The held-out material's contents are never read, by any role; its file names may be seen (DEC-525, DEC-820).
-
+ the held-out material's contents (its file names may be seen), the counterpart's work on the same ticket and the hidden half of an evaluation set (DEC-820, DEC-525, DEC-1052).
+

- These rules are followed by hand: they are not enforced by a mechanism yet (DEC-537). The resource gate is not a command; the launcher does not refuse a launch without a model; `AUTH_REQUIRED` is a stop the orchestrator names, not a mechanism; and leads are not started through the launcher, which starts workers alone.
+ These rules are followed by hand, not enforced by a mechanism yet (DEC-537): the resource gate is not a command; the launcher does not refuse a launch without a model; `AUTH_REQUIRED` is a stop the orchestrator names; leads are not started through the launcher, which starts workers alone.

- No fixed number of tickets in flight: the eligible tickets, the resource gate and the owner's usage limits decide, each time a slot could open; every countdown says how many and why (DEC-847).
+ No fixed number of tickets in flight: the resource gate and the owner's usage limits decide (DEC-847).

- For a FULL ticket a second review is the last. After it only fail-open holes and losses of work are fixed (DEC-413 names silent changes to tests or ticket files); the rest are residuals (DEC-413).
+ For a FULL ticket a second review is the last: after it only fail-open holes and losses of work are fixed, the rest are residuals (DEC-413).

- Each rule names the decision it follows; a rule that only an orchestrator's prompt held is cited with DEC-537, which ordered it stated here.
+ Each rule names its decision; a rule only an orchestrator's prompt held is cited with DEC-537, which ordered it stated here.

- a fresh test designer and a fresh implementer at the same time, from the spec, neither reading the other's work (DEC-959 item 7); the tests checked red against the ticket's base for the stated reason;
+ a fresh test designer and a fresh implementer at the same time, neither reading the other's work (DEC-959 item 7); the tests checked red against the ticket's base;

- A lead returns one of these forms: DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED (DEC-236), then `brief_gaps:` (DEC-943 item 1).
+ A lead returns one of these forms: DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED (DEC-236).

- The model `<model>` is named on every launch (DEC-460); no launch sets a compaction threshold (DEC-838).
+ The model `<model>` is named on every launch (DEC-460).

- Of every part marked not read it says that the part was not read, and of a share not measured that it was not measured. A status question is never answered from recall (CAP-28, DEC-541).
+ Of a part marked not read it says it was not read, and of a share not measured, that it was not measured. A status question is never answered from recall (CAP-28, DEC-541).

- Detail: [briefs-and-returns.md](briefs-and-returns.md).
+ Detail: `briefs-and-returns.md`.

- a full regression runs (DEC-536), which since DEC-968 is the next nightly's; a close runs the scoped set.
+ a full regression runs (DEC-536), since DEC-968 the next nightly's; a close runs the scoped set.

-  and health (the doctor summary).
+  and health.

- confidence is medium or higher (for a P2 also medium-low, where the owner has widened it as in DEC-416);
+ confidence is medium or higher (medium-low too for a P2, DEC-416);

- a lead with the absolute path of the CLI, `<absolute path of the CLI>`, a worker through the launcher;
+ a lead with the CLI's absolute path `<absolute path of the CLI>`, a worker through the launcher;

- ; leads are not started through the launcher, which starts workers alone.
+ ; leads are not started through the launcher.

- ; the tests checked red against the ticket's base;
+ ; the tests checked red;

- filled from the ticket and the project's facts file,
+ filled from the ticket and the facts file,
```

Measure with the read-only script `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py <file> [...]` (it prints the body's characters and tokens against the cap, and the description's): run it on the four kernel files before you commit; the orchestration file must say `OK`.

## Checks before you commit (all read-only; report each result)
1. No `<<<<<<<`, `=======` or `>>>>>>>` line in any of the 12 files (Grep tool).
2. The three places of each skill are one text: `cmp` of the kernel file with each `.rulesync` file, 8 comparisons, all silent.
3. `git -C /home/usain/gov-os-worktrees/W2-11 diff --numstat HEAD` shows exactly the 12 paths. **Expected, per place:** discovery 2 added 0 removed; retrieval 2 and 0; orchestration 27 and 22 (after the tightenings); test-design 41 and 15 (12 files, 216 added, 111 removed in all). A different count is not an error by itself: say why (the hunk rules left no room, so look for an edit outside a hunk first).
4. **Reference rendering (to compare, not to copy blindly):** the CTO's helper resolved the same hunks by the same rules into `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/resolved/{discovery,orchestration,retrieval,test-design}.md` (`orchestration.md` there is after the 21 tightenings; `orchestration-untrimmed.md` is after the hunks alone). `diff` each of your four files against it: expect no difference. A difference is yours to explain in the return (a better reading, or a slip): say which.
5. Size: the orchestration file's body is at most 10,000 characters (`body_tokens.py` says `OK` for the four kernel files). Versions: in the 12 files `version` and `metadata.version` are equal in every file (discovery 1.1.0, retrieval 1.1.0, test-design 1.3.0, orchestration 1.3.0). Read the four other skills with a version pair, `change`, `checkpoint`, `planning`, `audit` (kernel path): `version` equals `metadata.version` in each (they did on 2026-11-11); if one does not, name it in the return and **do not edit it** (it is outside your 12).
6. The orchestrator role file (`template/governance/kernel/roles/orchestrator.md`, and the two `.rulesync/subagents/orchestrator.md`): Grep each for `ceiling` and `brief-lead`: expect no hit (they were clean on 2026-11-11). Report the result; edit nothing (the role file is not one of your 12).
7. The brief templates are untouched: `git -C /home/usain/gov-os-worktrees/W2-11 diff --quiet HEAD -- template/governance/kernel/templates` exits 0.

## The generated copies you list for the CTO (step 6: read-only, report only)
Run `python3 -I /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/copies_diff.py /home/usain/gov-os-worktrees/W2-11` **after** the commit (it reads the tree, writes nothing). It prints, for every kernel skill, whether the `.claude/skills/<name>/SKILL.md` copy carries the source's body and version. **Expected after your commit (the helper's measure on a scratch clone): exactly four copies differ:** `.claude/skills/discovery/SKILL.md` and `.claude/skills/retrieval/SKILL.md` (copy `metadata.version` 1.0.0 against source 1.1.0), `.claude/skills/orchestration/SKILL.md` and `.claude/skills/test-design/SKILL.md` (body differs; the copy carries no `metadata` block, against sources at 1.3.0). The other skills' copies (`audit`, `change`, `checkpoint`, `planning`, `qa-review`, `adopt`) and the orchestration and test-design reference files agree. Quote the script's lines in `evidence` and say whether they match; any other copy that differs, or the `.claude/agents/orchestrator.md` copy, goes in `discoveries`.

**Who regenerates them (the CTO's decision; the helper's reading, put in your return as `unresolved` so the CTO sees it with your list):** the copies are class (b) control paths (`class-rules.yaml`, row `agents-skills-kernel`: `.claude/skills/**`, `.claude/agents/**` and `template/governance/kernel/**`; the `.rulesync/**` sources are row `rulesync-other`, (b)), so the change is an ACT with the owner's yes (DEC-1112 (3), DEC-315). Round 1's 16 copies were the CTO's hand run of rulesync with the owner's approval by day (`c895bb6283a6`, DEC-992 P-W2-11-5 (b), DEC-991); since then the copies went by operator-applied class (b) ACTs (ACT-CLAUDE-COPIES-1 to 3, for example `2059048f2eb4`, the orchestration and test-design copies, Approved-by: owner). **The recommendation is one copies ACT, after round 2's text is final** (the lead's product-spec batch changes these skills again; two regenerations would double the ACT). Until then the four copies are stale by design, and the cases that compare a copy with its source (`test_every_copy_carries_the_kernel_skills_body[test-design, orchestration]`, `test_the_skill_carries_one_version_in_all_four_places[discovery, orchestration, retrieval, test-design]`, `test_the_file_teaches_no_superseded_rule[.claude/skills/orchestration/SKILL.md]`) are red: the helper measured exactly these seven reds in the skill and supersession files on a scratch clone with this text (the two skill-and-supersession files plus W1-35's orchestration cases and `TestSkillRegressionGreen` otherwise pass); the other reds there are the five brief templates' cases, which the test designer retires (DEC-1137 (1)).

## Commit (one commit; never amend, rebase, reset, push or merge)
Hooks check first: `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit`. Then:
```
git -C /home/usain/gov-os-worktrees/W2-11 commit -m "W2-11 (DAEO-k7hz): W2-11's skill text put back onto the merged head: the four skills' versions, test-design's work order, orchestration's lead, ceiling, returns, checkpoint and policy lines (DEC-1137)" -m "Under the ticket's CIT-P (docs/changes/W2-11-CIT-P.md), CAP-33. The pre-merge commits (b5f3679c7c18, a78d0974d908) made the twelve files equal to integrate's text so that the merge (4e265aabed5c) had nothing to resolve; this commit restores W2-11's text of them from c16dbf41ea77 by the per-hunk rules of drafts/w2-11/RESOLUTION.md section 5: discovery and retrieval 1.1.0 with metadata.version; test-design 1.3.0 with W2-11's work order and Inputs and integrate's read facts (CAP-38.c); orchestration 1.3.0, the no-fixed-ceiling line over integrate's stated ceiling (DEC-847, DEC-866), the twelve-field return and the two-refusal stop, integrate's checkpoint line (DEC-1057) with the handover sentence (DEC-837), integrate's Policy 2 lines. Not touched: .claude/ (the four copies that now differ are listed in the return for the copies ACT), the five brief pointers (DEC-1137 (1))." --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Implements: DEC-1137, DEC-866, DEC-959, DEC-847" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <the 12 paths>
```
Then: `git -C /home/usain/gov-os-worktrees/W2-11 status --short` empty; `git -C /home/usain/gov-os-worktrees/W2-11 log -2 --format='%h %an%n%B'` shows your commit and its trailers; `git -C /home/usain/gov-os-worktrees/W2-11 diff --name-only 4e265aabed5c..HEAD` names exactly the 12 paths.

## Rules
- Step 0, the sandbox check, first and reported first: `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must fail; `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
- No test run, except what this paragraph allows: the helper ran W2-11's folder, W1-35's orchestration cases and `TestSkillRegressionGreen` on a scratch clone with this text, and the lead re-runs after the test designer. You may run `gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11` once at the end, results only (the five brief templates' cases are red until the designer retires them, and the seven copy cases until the copies ACT; name any other red), and `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py` as above. Nothing else heavy. No installs. Never the full suite. Never `git merge`, `git stash`, push, or a commit on another branch.
- A refusal is taken, never routed round; a false refusal is worked round at once with an equivalent form (named in your return), never a form chosen to pass a true refusal (DEC-849, DEC-1040). One simple command per Bash call; the Edit and Write tools for file changes (no here-documents); no `cd ... &&` chains (use `git -C <dir>`).
- The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any folder named `hidden`, `memory-verdict` or `memory-verdict-2`.
- `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` is optional (at most twice, then once more in different words if it did not answer); say whether you used it. Policy 2: reads are open; only secrets, the held-out material's contents, the counterpart's work on the ticket and an evaluation set's hidden half are refused.
- Refused twice for the same call: stop and say so.
- Estimate: 30 to 40 minutes, about 70 tool calls, about $4 (E). Return the twelve fields as labelled lines first (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), short; any payload after them. `evidence` holds the commit (12 digits, with its trailers), the nine hunk counts, the 21 tightenings (applied as given, or each difference and why), the check results (1 to 7), the `copies_diff.py` lines, and the form you used to capture the three versions. `tests`: the `gov accept` counts and the names of its reds (or why you did not run it), and the `body_tokens.py` lines. `discoveries`: any difference from the reference rendering, any `.claude` copy beyond the four. `unresolved`: the copies ACT's route (the CTO decides), the list of stale copies.
