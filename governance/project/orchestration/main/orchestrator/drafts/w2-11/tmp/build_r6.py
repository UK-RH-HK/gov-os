"""Build briefs/W2-11-A5-r6-resume.md from the hand-built r5 brief (scratch only; the brief is written once, here).

Pieces kept from r5 by line range (the forms, the commit block, the return block, the model table, the judgement
rules); the rest is new text. The appended LEAD-w2-common.md is read from the main tree with every {SLOT} filled.
"""
import re
from pathlib import Path

import yaml

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ORCH = ROOT / ".gov-runtime/scratch/orchestrator"
r5 = (ORCH / "briefs/W2-11-A5-r5-resume.md").read_text().split("\n")


def lines(a, b):
    """r5's lines a..b (1-based, inclusive)."""
    return "\n".join(r5[a - 1:b])


ticket_text = (ROOT / ".tickets/DAEO-k7hz.md").read_text()
front = yaml.safe_load(ticket_text.split("---")[1])
succ, fail = front["kpis"]["success"], front["kpis"]["failure"]
sources = ", ".join(front["sources"])
paths = ", ".join(f"`{p}`" for p in front["allowed_paths"])
rows = ", ".join(front["list_rows"])
refusal = (ORCH / "drafts/w2-11/tmp/gov-brief.err").read_text().strip()
assert "BRIEF_NOT_READY" in refusal


def cut(line, n=150):
    line = " ".join(line.split())
    return line if len(line) <= n else line[:n].rstrip() + "..."


VERIFY = {
    1: "`gov accept DAEO-k7hz`: the cases its README map names for S1",
    2: "`gov accept DAEO-k7hz`: the cases its README map names for S2 (re-pointed to the skill alone by the designer's commit)",
    3: "`gov accept DAEO-k7hz`: the cases its README map names for S3 (skill alone)",
    4: "`gov accept DAEO-k7hz`: the cases its README map names for S4 (the skill's folder)",
    5: "`gov accept DAEO-k7hz`: the cases its README map names for S5",
    6: "`gov accept DAEO-k7hz`: the cases its README map names for S6 (the .claude copy case is red until the copies ACT)",
    7: "`gov accept DAEO-k7hz`: the cases its README map names for S7",
    8: "`gov accept DAEO-k7hz`: the cases its README map names for S8 (repository-state)",
    9: "`gov accept DAEO-k7hz`: the cases its README map names for S9 (the template's sections; its round-2 half has no case yet: step 5)",
    10: "`gov accept DAEO-k7hz`: the cases its README map names for S10",
    11: "`gov accept DAEO-k7hz`: the cases its README map names for S11",
    12: "no case after the designer's commit: the first half's subject is retired (DEC-1137 (1)), the second half is Wave 3's (DEC-1083); say so, add nothing",
    13: "no case yet: step 5's designer batch writes it (reads the skill's folder)",
    14: "no case yet: step 5's designer batch writes it (reads the skill's folder)",
    15: "no case yet: step 5's designer batch writes it (test-design's folder)",
    16: "no case yet: step 5's designer batch writes it for the skill half; the template half is a package (open point 3)",
}
table = ["| id | line (cut; the ticket file holds the whole line) | verify |", "|---|---|---|"]
for i, line in enumerate(succ, 1):
    table.append(f"| S{i} | {cut(line)} | {VERIFY[i]} |")
table.append(f"| F1 | {cut(fail[0])} | no case yet: step 5's designer batch writes it (kernel skills, their copies, `skill.md`) |")
table.append(f"| F2 | {cut(fail[1])} | `gov accept DAEO-k7hz`: the cases its README map names for F2 |")
assert len(succ) == 16 and len(fail) == 2

HEAD = f"""# HAND-BUILT lead brief: W2-11 (DAEO-k7hz), run r6-resume (DEC-1130 (1)), after the merge and the two commits that land before this run

`gov brief lead DAEO-k7hz --run resume` refuses this ticket today (re-run from the main tree, 2026-11-11 about 21:25 UTC, exit 1, nothing on stdout; recorded below): a reviewed ticket in progress has KPI lines with no `Verify:` text. DEC-1130 (1) (the owner's exception to DEC-1083, for tickets in progress only) lets it launch on a hand-built brief with the refusal recorded in the brief. This brief takes the form `gov brief` produces (template `brief.md`, role template `role-lead`, the facts file `governance/project/facts.yaml`), then the ticket's own run section, then the committed common lead brief, appended whole with its ticket slots filled (prompt section 15). Where the common text and the facts file's steps differ, this part holds: the steps `trailer_gate`, `collect_only` and `checkpoint_record` are off (facts.yaml `steps`: DEC-1057, DEC-953 item 1); `keyword_warn`, `hooks_check`, `scratch_measure`, `context_ceiling` and the guard-refusal lines are on. `EMG-common.md`, `NIGHT-common.md` and `LIFT-common.md` (beside this file in `.gov-runtime/scratch/orchestrator/briefs/`) hold where this file does not change them (the lift's closes are done, the main tree stays clean, the next free decision id is DEC-1139: you never write a decision). A hand-built brief is not checked by `gov brief`: the CTO reads it before launch.

## What `gov brief` said (recorded, DEC-1130 (1))

### Recorded refusal (not a brief): gov brief lead DAEO-k7hz --run resume (live pin pin-797495bdfc70), 2026-11-11 about 21:25 UTC

Command: `gov brief lead DAEO-k7hz --run resume` from the main tree. Exit 1, nothing on stdout. Its stderr, copied (the ticket now has 16 success lines and 2 failure lines, DEC-1137; S1 to S16, F1, F2):

```
{refusal}
```

The KPI table below carries each line's `Verify:` as the one command that measures it (`gov accept`, read from the README map): the ticket file itself is not edited by this brief.

---

# Your assignment
You are a fresh orchestrator session (the ticket lead). Your role's rules are in your system prompt (template `role-lead`); this brief gives this assignment's facts.
Ticket DAEO-k7hz (W2-11), profile STANDARD (C3, kernel). Objective: Briefs and the orchestration skill (W2-11): resume, round 2 of two, on top of the verified round 1, **after** the merge of `w2/integrate` into the branch (merge `4e265aabed5c`) and the two commits that land before this run: a product-spec commit that puts W2-11's own skill text back onto the merged head (brief `W2-11-A4-skills-restore.md`) and a test designer's commit that retires or re-points the brief cases under DEC-1137 and renumbers the README map to the ticket's lines (brief `W2-11-A1-rebaseline.md`). Your run: verify the restored skills against the re-baselined KPI lines; run `gov accept DAEO-k7hz` and the scoped verification; write round 2's lines (S9's round-2 half, S13, S14, S15, S16 and F1, which are not done); one independent review; then DONE for landing. The ticket: the kernel's skills teach the current rules: the twelve-field return, payload after, the two-refusal stop, Policy 2's read rule, the decision-record rule, DEC-430 in the audit brief; no superseded rule (DEC-866); the test-design skill (kinds, proportion, parallel work order, timing tests); one skill template with a closed front matter; orchestration's reference files, the anti-drift kit, scope control and approvals; a qa-review skill. A kernel change: CIT-P, independent review, owner approval (CAP-33). **DEC-1137 (the owner, 2026-11-11, option (c) of DEC-105):** the five `template/governance/kernel/templates/brief-*.md` files are one-line pointers (W2-128) and stay so: nobody in this run writes them; the role templates' Policy 2 refusals, DEC-861's record rule and the two-refusal stop are W2-175's (`DAEO-wahn`).
projection_usd: 18

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-11 |
| branch | w2/W2-11 |
| allowed paths | the ticket's `allowed_paths` is the whole list: the skills `orchestration`, `audit`, `test-design`, `qa-review` and the front-matter version lines of `skills/*/SKILL.md`, `templates/skill.md`, `roles/orchestrator.md`, their `.rulesync` sources, and `docs/changes/W2-11-CIT-P.md`. The list still names `template/governance/kernel/templates/brief-*.md`: they stay pointers, you write none (open point 4). **Every `.claude/**` line is out of your paths: those copies are generated by the copies ACT (DEC-1112 (3), DEC-315)** |
| ticket file (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md |
| your scratch | /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/ |
| the CTO's tools | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools |

## What must be true (KPI lines and how each is checked)
""" + "\n".join(table) + """
README ids: the acceptance README (`tests/acceptance/W2-11/README.md`, read by `gov accept`) names the lines `success-n` and `failure-n` by the n-th line of the ticket. The designer's commit (before your run) renumbers it to the ticket's numbering shown above (S5 to S12 were README success-6 to success-13 until then; the DEC-866 line is F2). If you find it still carries the old numbers, say so at once (PACKAGES): the cases would be read against the wrong lines.
Non-goals (the ticket states none; `gov brief`'s NON_GOALS_MISSING): the skill validator and its case (W2-120); the three layers' roles and typed handoff (W2-33: the role file stays limited to DEC-866's sweep sentences); the role templates' Policy 2 refusals, DEC-861's record rule and the two-refusal stop (W2-175); the five `brief-*.md` pointers; S12's second half (Wave 3, DEC-1083); every `.claude/**` file; the adopt skill's version line while W2-52 holds it; `src/`.
Done when: the DoD lines DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6 hold for your part (DOD-4 here is the independent review of the CIT-P, round 2; the owner's CAP-33 approval and the copies ACT are the CTO's and come after you).

## Inputs
- Sources: """ + sources + """ (all ACCEPTED). Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below). Also DEC-916 (declared rounds), DEC-1010 and DEC-1131 (one bar, two rounds), DEC-1050 (the templates: `role-*.md`, `brief.md`, `facts.yaml`), DEC-1120 (RUBRIC-2), DEC-1130 (1) (why this brief is hand-built), DEC-1057 (no committed checkpoint record at each round boundary), DEC-963 (the work order in parallel, one writer per worktree).
- **What the lead knows of the ground** (state as of 2026-11-11 ~21:30 UTC; the CTO's helpers read the ticket, both trees' text, the checkpoint and the last returns, and measured the restored text on a scratch clone):
  - **The merge is done.** `w2/W2-11` has the merge of `w2/integrate` at `4e265aabed5c` (after a test designer's pre-merge commit for W1-35 and a product-spec pre-merge that took integrate's text for the five brief pointers and twelve skill files; the two generated `.claude/skills/{orchestration,test-design}/SKILL.md` copies were taken from integrate). Two commits sit above it when you start, in either order: **(a)** product-spec, W2-11's skill text restored onto the merged head (versions: discovery 1.1.0, retrieval 1.1.0, test-design 1.3.0, orchestration 1.3.0, each with `metadata.version` equal to `version`; test-design's parallel work order and Inputs; orchestration's no-fixed-ceiling line over integrate's stated ceiling, the twelve-field return and the two-refusal stop, integrate's checkpoint line plus the handover sentence, integrate's Policy 2 lines); **(b)** the designer's re-baseline (the brief cases retired or re-pointed, `Rewrite-Reason: DEC-1137 re-baseline`, the README map renumbered). Check both with `git -C /home/usain/gov-os-worktrees/W2-11 log --format='%h %an %s' 4e265aabed5c..HEAD` and their trailers (`Role: product-spec`, `Role: independent-test-designer`, `Task: DAEO-k7hz`). **Either missing: PACKAGES at once; do not do their work.** Integrate has moved 14 commits since the merge (W2-105's landing and W2-149's probe record; none touches W2-11's files): you do not merge again (one merge per ticket, the merge queue's, DEC-988, DEC-989); before DONE run `git -C /home/usain/gov-os-worktrees/W2-11 merge-tree --write-tree --name-only HEAD w2/integrate` (read-only, exits 1 when there is a conflict) and quote its conflict lines or "none".
  - **The orchestration skill's body is at its cap.** The skill's body is capped at 2,500 tokens (W1-35's `test_the_body_is_within_2500_tokens` and the skill validator, a hard block): `ceil(characters / 4)`, so 10,000 characters. After the restore it is **9,976 characters** (the product-spec's brief carried 21 tightenings to get there). **Round 2's orchestration lines (S13 the anti-drift kit, S14 scope control, S16 the approvals section) therefore do not go into `SKILL.md`:** they go into the skill's reference file `briefs-and-returns.md` (named from the skill's first paragraph; present in the kernel source, `.rulesync/` and `template/.rulesync/`), each under its own heading, and the designer's cases read the skill's folder (`SKILL.md` and its reference files), as S4's case already does (`folder_texts`). The test-design skill (1,342 tokens) has room for S15. Measure after every text change: `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py <SKILL.md> [...]` (read-only; it says `OK` or `OVER THE CAP`).
  - **Generated copies are stale on purpose.** After the restore, four copies differ from their sources: `.claude/skills/{discovery,retrieval,orchestration,test-design}/SKILL.md` (the first two carry `metadata.version` 1.0.0 against 1.1.0; the other two carry integrate's text and no `metadata` block). Check with `python3 -I /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/copies_diff.py /home/usain/gov-os-worktrees/W2-11` (read-only). **Seven W2-11 cases are red until the copies ACT, by design:** `test_w2_11_skills.py::test_every_copy_carries_the_kernel_skills_body[test-design]` and `[orchestration]`, `test_w2_11_skills.py::test_the_skill_carries_one_version_in_all_four_places[discovery]`, `[orchestration]`, `[retrieval]`, `[test-design]`, and `test_w2_11_supersession.py::test_the_file_teaches_no_superseded_rule[.claude/skills/orchestration/SKILL.md]`. They are not yours to fix and not a reason for PACKAGES: name them, and list in your return every generated copy that differs from its source when you return (each path); the copies are one class (b) ACT after your DONE (the owner's yes; ACT-CLAUDE-COPIES-1 to 3 are the precedent; round 1's copies were the CTO's hand run, DEC-992 P-W2-11-5 (b), DEC-991). A launched session cannot write `.claude/**` (DEC-315): never try another form.
  - **Round 2's lines, by the ticket's numbers now:** DEC-983 names brief gaps, the anti-drift kit, scope control and timing tests: in the ticket now S12 (brief gaps: its first half, the `brief_gaps:` section of the lead template, is now in `brief.md`'s return (W2-128); the second half is tagged to Wave 3, W3-P02, W-10, DEC-1083: no case, no text), **S13 (anti-drift kit), S14 (scope control), S15 (a timing test measures the work under test)**; **S16** is DEC-991's and DEC-994 item 3's approvals section. A search of the kernel's skills and templates on the merged head (2026-11-11) finds no text for S13, S14, S15 or S16 and the README has no case for them. **Also not done:** S9's round-2 half (the skill template's front matter closed to `name`, `version`, `description`, `output`, no permission field, and a Never statement: `templates/skill.md` still has the older text) and F1 (no permission field in a skill's front matter, no step telling a role to write what its output class does not hold). Confirm all of this by one `gov accept` before you write anything, and say in your return what you found.
  - **Open points for you.** (1) **S9's `metadata`:** the closed front matter lists four keys, but every kernel skill carries `metadata.version` repeating `version` (the one extra key rulesync carries into the generated copy, DEC-832 item 2, DEC-992 P-W2-11-1, and `skill.md` says so itself). Read the closed set as those four keys plus that one `metadata.version`; if a case or a text cannot be written under that reading, return PACKAGES with the exact conflict (a P2 for the CTO), never drop `metadata.version`. (2) **S13, S14 and S16's sentences** are the ticket's words (read each full line in the ticket file): the product-spec worker writes the method, each rule traceable to its decision (DEC-952 item 6, DEC-953 item 7, DEC-974, DEC-991, DEC-994 item 3, DEC-979 item 1 D2 for S15), the skill states a method and grants nothing (CAP-24.b). (3) **S16's template half:** "the orchestrator brief template carries it" has no file in W2-11's paths (the nearest, `role-cto.md`, is W2-33's and W2-128's approved text; the CTO's helper recommended rewording the line to the skill half only, `drafts/w2-11/REBASELINE.md` section 2, item 1, and the CTO has not decided). Do the skill half; return a package row for the template half (met by what, or needs a ticket line change: a P2 for the CTO); never edit a role template. (4) **Ticket housekeeping the CTO owns** (never yours): the `allowed_paths` entry `brief-*.md` should go, and `list_rows` W2-L257 and W2-L258 end as "no longer applicable, W2-128 retired the files" (DEC-1137): note them in your return only. (5) **Rounds:** this is the ticket's round 2 of two declared (DEC-916). **One review is planned; a second only if the first returns an in-scope finding that an honest agent can hit in ordinary work and that fails open or loses work** (DEC-1010 item 1): then one repair batch and the second and last review.

## Commands (copy them as they are; the `{...}` words in this table are for you to fill at each call)
""" + lines(91, 91) + "\n" + lines(92, 99) + """
| tests_worktree | `git -C /home/usain/gov-os-worktrees/W2-11 worktree add /home/usain/gov-os-worktrees/W2-11-tests -b w2/W2-11-tests HEAD` |
| merge_tests | `git -C /home/usain/gov-os-worktrees/W2-11 merge --no-ff w2/W2-11-tests -F {MESSAGE_FILE}` (the message file ends with `Task: DAEO-k7hz` and `Role: orchestrator`) |
| accept | `gov accept DAEO-k7hz --root /home/usain/gov-os-worktrees/W2-11` |
""" + lines(104, 108) + """
| body_tokens | `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/body_tokens.py {SKILL_FILE}` |
| copies_diff | `python3 -I /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/copies_diff.py /home/usain/gov-os-worktrees/W2-11` |
""" + lines(109, 112) + "\n" + lines(113, 115).replace(
    "No merge inside a sandbox: you merge outside it;", "No merge inside a sandbox: you merge outside it;") + "\n\n" + lines(117, 120) + "\n\n" + lines(122, 142).replace(
    "CAP-33, DEC-959, DEC-983, DEC-991, DEC-995, DEC-996, DEC-866, DEC-820, DEC-1083, DEC-1112",
    "CAP-33, DEC-959, DEC-983, DEC-991, DEC-995, DEC-996, DEC-866, DEC-820, DEC-1083, DEC-1112, DEC-1137") + "\n\n"

MODEL = """## Model, effort and class by RUBRIC-2 (DEC-1120 (3)) for each worker you start
Every `launch_worker.sh` call names its class, model and effort; there is no default. A spawn after two failed rounds or a fail-open finding is a promotion, named with `--promoted "<reason>"` (DEC-1120 (3)); you do not promote on your own: return PACKAGES.
| worker | role | class | model | effort | when |
|---|---|---|---|---|---|
| test designer | independent-test-designer | C3 (kernel) | Opus (`claude-opus-5-5`) | high | step 5 (the tests worktree) |
| product-spec | product-spec | C3 (kernel) | Sonnet (`claude-sonnet-5-5`) | high | step 5 (RUBRIC-2-APPLY: product-spec and research on Sonnet) |
| reviewer | independent-auditor (read-only) | C3 (kernel) | Opus (`claude-opus-5-5`) | high | step 8 |
| a fresh worker after a red | the same role as the one that failed | C3 | the same as above | high | a repair of this change; never a promotion without the CTO |
You yourself run as lead on Opus at high. The tools: `--model claude-opus-5-5` for Opus, `--model claude-sonnet-5-5` for Sonnet.

## Your run: r6-resume (only this section is in your brief)
**resume**: read `/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/CHECKPOINT.md` (it is round 1's, run 4: DONE at `c9f99b28b88b`; its NEXT is "nothing for round 1"); then continue in the order below. One writer per worktree; the designer works in the tests worktree, the product-spec worker in your tree, in parallel (DEC-963).
1. First calls: (command `identity`) (expect `orchestrator` and `DAEO-k7hz`), (command `where`) (expect `/home/usain/gov-os-worktrees/W2-11` and `w2/W2-11`), the checkpoint, the ticket file, then `git -C /home/usain/gov-os-worktrees/W2-11 status --short` (clean) and the log check of the first ground bullet (both pre-run commits present, with their trailers). Run (command `hooks_check`) before each commit. No merge of integrate (done; the queue merges at the land).
2. **Verify the restored skills against the re-baselined lines (read-only, before any worker).** Read the skills' text on your branch against each line, and write one row per line in CHECKPOINT.md (met by which file and sentence, or not met and why): S1 test-design's proportion rule (DEC-951); S2 the orchestration skill's twelve fields, payload after and the two-refusal stop; S3 its Policy 2 read lines and the decision-record line (DEC-861, DEC-862); S4 the audit's DEC-430 wording (the skill's folder: `briefs-and-returns.md` and the audit skill); S5 loose citations (identity by DEC-371, not DEC-183; the stop's block by DEC-537 and DEC-948, not DEC-486); S6 no superseded rule (no LEAD_CHECKPOINT, no listing refusal, no fixed ceiling, owner decisions by decision-record commits) in the skill, the role file and the sources; S7 test-design's kinds, cost, no whole-tree copy, live-repository tests declared; S8 the fixed brief gaps (repository-state); S9 `templates/skill.md` (round 1's half); S10 test-design's work order in parallel, red against the base, ISTQB, proportion, the README map; S11 orchestration's three reference files and the qa-review skill. Also: (command `body_tokens`) on the four kernel skill files (all `OK`), `version` equals `metadata.version` in each kernel skill (`change`, `checkpoint`, `planning`, `audit` too), and (command `copies_diff`): expect exactly the four copies named above. Anything unexpected (a line not met, a size over the cap, another copy differing): PACKAGES row, not a repair of your own.
3. After step 2: (command `disk_gate`), then (command `rebuild`) once in the background with an exit-code file, then (command `accept`) once. Write into CHECKPOINT.md which README rows pass, which fail, and which ticket lines have no case. **Expected:** every case passes except the seven copy cases named above; S12's row has no case; S13 to S16, F1 and S9's round-2 half have no case. Any other red: name it with its cause, and decide in step 6 whether it is yours. That list confirms or corrects the "Round 2's lines" bullet; say in your return what you found.
4. (command `tests_worktree`) now, from your head. Tripwire before each worker (the common brief).
5. **Round 2's batch, designer and product-spec in parallel (DEC-963).**
   - **Test design** (a fresh independent-test-designer in the tests worktree, launched with (command `launch_worker`), the brief written by you from `role-test-designer.md`, the common brief's rules and this ticket's lines): from the ticket's lines and the replacing files, no name of the code to be written (DEC-462); it never reads this ticket's implementation (DEC-820 (c)) and drops unread any `gov retrieve` result under the ticket's paths (P-R1). It adds, in proportion (the minimum that shows each line, S1; the profile is STANDARD): cases for **S9's round-2 half** (the skill template's front matter closed to `name`, `version`, `description`, `output` with `metadata.version` as the one carried repeat (open point 1), no permission field, and a Never section stating that the skill changes no role's reads or writes and that work needing other writes goes back as a package), **S13, S14, S16's skill half** (read the orchestration skill's folder, `SKILL.md` and its reference files, as the S4 case does: the text lives in the reference file, see "The orchestration skill's body is at its cap"), **S15** (test-design's folder) and **F1** (every kernel skill, its generated copy and `skill.md`: no permission field in the front matter, no step telling its role to write what its output class does not hold; the copies half is red until the copies ACT, which the README must say in its red reason). Each case red on the base with the README's row stating the red reason, in the code-span form `gov accept` reads (full node ids), under the ticket's numbering. It writes no case for S12 and none for S16's template half. The cases never ask `SKILL.md` for text it cannot hold (10,000 characters). Its brief carries the work order in parallel, DEC-820 (c) and (d), the hidden-half rule, and the scope: only `tests/acceptance/W2-11/` (`test_w2_11_skills.py` and a new file for round 2, `w2_11_support.py` and `README.md` for helpers and rows); the brief cases are not its to touch again.
   - **Product-spec** (a fresh product-spec worker in your tree, launched with (command `launch_worker`)): the text for S9's round-2 half (`templates/skill.md`), S13, S14 and S16's skill half (**in `briefs-and-returns.md`, three places, each under its own heading; `SKILL.md` gains no more than its first paragraph already says (`body_tokens.py` stays `OK`)**), S15 (test-design's `SKILL.md` or `test-kinds.md`) and F1's rule (in `skill.md` and in the skill-writing text it holds), in the kernel sources only, each line traceable to its decision; the skill versions raised where a skill's text changes (every place the version stands: kernel, `.rulesync/`, `template/.rulesync/`, and `metadata.version`; the `.claude` copies follow by the ACT); `docs/changes/W2-11-CIT-P.md` revised as round 2 (status PROPOSED, evidence, corroboration, the rows from step 2's and step 3's findings). It writes nothing under `.claude/**`, nothing in a `brief-*.md`, no role template; it lists which generated copies need regenerating. A skill states a method and grants nothing (CAP-24.b). Its brief carries the size cap and the `metadata` reading above.
6. Merge the tests ((command `merge_tests`)); (command `accept`) once; (command `lead_verify`) once (the scoped verification; W1-35's orchestration cases and the skill-regression family are in it); a red named only from the known-reds list `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json`, or one of the seven copy cases above; a red this change caused: a fresh product-spec worker or designer given the failing output only; three iterations that do not converge: ESCALATION (DEC-096). Remove the tests worktree and its branch at the end ((command `tests_worktree_remove`)). Run (command `body_tokens`) and (command `copies_diff`) again and keep their lines for the return.
7. Quote the scoped selection's scope, `core_changed` and `unplaced` in your return (common brief), and the read-only `merge-tree` check against current integrate (first ground bullet).
8. **Review** (a kernel change): one fresh independent reviewer, read-only, on your final head: the CIT-P's independent review, round 2, against the ticket's lines S1 to S16, F1 and F2 and CAP-33; it carries the judgement rules below word for word and returns the fenced `verdict` block with the ticket's line ids (S1 to S16, F1, F2; S12 is judged on its first half's retirement and its Wave 3 tag). Compute READY with `verdict.ready` (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verdict.py`, in a script file). READY: commit its record as `docs/probes/DAEO-k7hz/CITP-REVIEW-r2.md` (round 1's is `CITP-REVIEW-r1.md`; the profile is STANDARD, so no probe gate reads it) on your branch, alone. Not READY: triage every finding (scope, ordinary work, consequence) and return PACKAGES; a second review only inside the declared round (open point 5); never decide a FAIL away.
9. Return DONE at the exact reviewed head, or PACKAGES. In `unresolved` and `recommended_next_action`: the owner's CAP-33 approval of the combined K3 CIT-P, the **generated copies that need regenerating (each path, with the one class (b) copies ACT after your DONE)**, the packages of open points 1 and 3, the ticket housekeeping of open point 4, and the merge queue's land (the CTO's). Before returning: (command `links`), (command `keyword_warn`), (command `context_ceiling`), the scratch measures, CHECKPOINT.md rewritten, `git status --short` empty.
Estimated at 2.5 to 4 lead-hours and $14 to 20 (E: run 1 was 3.4 h and $15.8, its resume 0.5 h and $8.2, M; the merge, the restore and the re-baseline are already done, so this run is round 2's text, its tests, the verification and one review).

"""

JUDGE = lines(166, 193)

common = (ROOT / "governance/project/briefs/LEAD-w2-common.md").read_text()
meta = ("This is the part of every Wave 2 ticket lead's brief that does not depend on the ticket. The orchestrator writes the ticket's own part (why it starts now, the decisions staged for it, this run's order, its probe's focus) before it, fills `{ID}` (the tk id), `{W2}` (the WBS id), `{PROFILE}`, `{PATHS}`, `{ROWS}`, `{SOURCES}`, `{IMPL}` and `{EST}`, and gives the lead the result.")
assert meta in common
common = common.replace(meta, "This is the part of every Wave 2 ticket lead's brief that does not depend on the ticket. The orchestrator writes the ticket's own part (why it starts now, the decisions staged for it, this run's order, its probe's focus) before it, fills the ticket's ids, profile, paths, rows, sources, implements list and estimate in this text (done below for DAEO-k7hz, W2-11), and gives the lead the result.")
VALUES = {
    "{ID}": "DAEO-k7hz",
    "{W2}": "W2-11",
    "{PROFILE}": "STANDARD",
    "{PATHS}": paths,
    "{ROWS}": rows,
    "{SOURCES}": sources,
    "{IMPL}": "DEC-866, DEC-959, DEC-983",
    "{EST}": f"{front['est_loc']} lines (the ticket's est_loc)",
}
for slot, value in VALUES.items():
    common = common.replace(slot, value)
left = re.findall(r"\{[A-Z_0-9]+\}", common)
assert not left, left

out = HEAD + MODEL + JUDGE + "\n\n\n---\n\n# The common lead brief (committed, `governance/project/briefs/LEAD-w2-common.md`), appended whole, its ticket slots filled for DAEO-k7hz (W2-11)\n\n" + common
(ORCH / "briefs/W2-11-A5-r6-resume.md").write_text(out)
print(len(out), "chars; unfilled slots in the appended part:", left)
