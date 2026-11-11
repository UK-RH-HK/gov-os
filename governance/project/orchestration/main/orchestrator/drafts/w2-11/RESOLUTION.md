# W2-11 (`DAEO-k7hz`): merging `w2/integrate` into `w2/W2-11`, worked out read-only (helper, 2026-11-11 ~19:50 UTC)

Status: **the acceptance file is solved and tested read-only; the rest is not "two conflicts" and is not mechanical.** Read section 1 first.

## 1. What the merge really holds

`git merge-tree --write-tree --name-only w2/W2-11 w2/integrate` (W2-11 head `c9f99b28b88b`, 26 ahead; integrate head `1b7641349163`, 1,897 behind; base `c38a5b49bc86`) reports **20 conflicted files, not 2** (the CTO's report of two files does not match what git says today; integrate may have moved since: the list here is today's). All text conflicts, no modify/delete:

| group | files | note |
|---|---|---|
| A. acceptance | `tests/acceptance/W1-35/w1_35_orchestration_support.py` | 1 hunk; solved, section 3 |
| B. five briefs | `template/governance/kernel/templates/brief-{engineer,lead,product-spec,reviewer,test-designer}.md` | 1 hunk each; integrate made each a one-line pointer (W2-128 TPL-1 S4, `a6c83d497`); W2-11 rewrote each (+121 to +296 lines). **Not mechanical, a package: section 4** |
| C. kernel skills (source) | `template/governance/kernel/skills/{discovery,retrieval}/SKILL.md` (1 hunk each, version lines), `.../test-design/SKILL.md` (2 hunks), `.../orchestration/SKILL.md` (5 hunks) | product-spec's, section 5 |
| D. copies of C | `.rulesync/skills/{discovery,retrieval,test-design,orchestration}/SKILL.md`, `template/.rulesync/skills/` the same four | same hunks as C (the orchestration and test-design copies are the same text as the kernel's: resolve once, copy) |
| E. generated | `.claude/skills/orchestration/SKILL.md` (4 hunks), `.claude/skills/test-design/SKILL.md` (1 hunk) | generated through rulesync; not a lead's or a designer's to write (class (b)); the CTO regenerates, section 6 |

W2-11 changed 83 files since the base; integrate changed 27 of them. The other 7 overlapping files auto-merge (for example `template/governance/kernel/roles/orchestrator.md`, `.rulesync/subagents/orchestrator.md`, `.claude/agents/orchestrator.md`, the audit skill), but **three auto-merges are wrong on meaning** and need an edit after the merge (section 5, item 6).

## 2. Class of each file (`governance/project/operator/class-rules.yaml`)

| path | row | class | control path |
|---|---|---|---|
| `template/governance/kernel/**` (the briefs, the skills, the role files) | `agents-skills-kernel` | (b) | yes |
| `.claude/skills/**`, `.claude/agents/**` | `agents-skills-kernel` | (b) | yes |
| `.rulesync/**` | `rulesync-other` | (b) | yes |
| `template/.rulesync/**` | no row names it: `unknown` | (O) | no |
| `tests/acceptance/**` | `unknown` | (O) | no; MR-3: only a test designer writes it |
| `docs/research/`, `src/**`, `docs/probes/**` | `unknown` | (O) | no |

The rows rule an operator ACT. W2-11's own work is the CIT-P route (CAP-33, `docs/changes/W2-11-CIT-P.md`), already approved for round 1. The landing check (S16) will list the (b) control paths W2-11 changes: that is W2-11's known scope, not a new finding.

## 3. Group A: the acceptance file (solved)

**What each side did.** W2-11 replaced the clause "a stated ceiling of tickets in flight" of the row `"parallel tickets"` by "no fixed number of tickets in flight" (DEC-847, DEC-866), and made four other edits that merge cleanly (the third standing sentence gone, `ids: ("DEC-847",)`, the LEAD_CHECKPOINT clause by "a checkpoint at every handover", the DEC-820 row). Integrate (D-4 cut B, DEC-1061, DEC-942; W2-128) **removed** the stated-ceiling clause with a Rewrite-Reason comment, and added the retired-brief helpers (`REPLACEMENTS`, `is_retired`, `brief_texts`, `briefs_stand`, the conditional `verbatim` loop). The two edits sit on the same three lines: git conflicts.

**Resolution (the final content of the hunk):** keep integrate's removal and its comment, and keep W2-11's positive clause, which is the only case that pins the success line "no fixed ceiling of tickets in flight" (no case of `tests/acceptance/W2-11/` does). A positive clause stays good under DEC-942 (no fixed number of leads). The text the merge gives (lines 122 to 130 of the merged file): integrate's three-line comment, then, after the unchanged "the resource gate before each start" clause, W2-11's two-line comment and clause.

**How, with no conflict and no designer writing a template.** A designer cannot write the other 19 files (the guard lets it write only under `tests/acceptance/**`), and the merge commit by another role may not change an acceptance file beyond what git's own merge holds (`tests/acceptance/W1-01/w1_01_support.py::merge_offences`, DEC-253, DEC-912 (1)). So the designer first makes **one ordinary commit on `w2/W2-11`** (role designer, `Rewrite-Reason`) that puts W2-11's clause where git's merge keeps it and gives the old clause back in the lines integrate rewrote. Then git's own merge of the two branches has no conflict in this file, and the merge commit (any role) changes nothing in `tests/acceptance/` beyond git's own merge, which `merge_offences` allows.

Proved read-only: a synthetic commit (objects only, no ref) of `w2/W2-11` with the file replaced by `drafts/w2-11/W1-35-orchestration-support.PRE-MERGE.py` (550 lines), then `git merge-tree --write-tree --name-only` of it with `w2/integrate`: **19 CONFLICT lines, the W1-35 file only "Auto-merging"**; the merged file (`W1-35-orchestration-support.MERGED-EXPECTED.py`, 606 lines) has no marker and parses. (A first try that resolved the hunk by hand and committed it still conflicted: the two sides' hunks differ, so git has no identical change to take.) Both files are in `drafts/w2-11/`; the brief gives the designer two Edit calls and a `cmp` against the PRE-MERGE file, so it writes nothing it has not compared.

**The designer's brief:** `.gov-runtime/scratch/orchestrator/briefs/W2-11-A1-merge.md` (one commit, trailers `Task: DAEO-k7hz`, `Role: independent-test-designer`, `Implements: DEC-847, DEC-866`, `Rewrite-Reason`; no merge; estimate 10 minutes).

**A cost to see.** After this commit and before the merge, W2-11's branch has W1-35's old ceiling clause back in place, red against W2-11's skill. Nothing runs between the two steps; the merge settles it. If the owner would rather not have the intermediate state in history, the alternative is one designer merge commit that also resolves the other 19 files: the guard forbids it, so it is not on offer.

## 4. Group B: the five briefs (a package, DEC-105's three costed options)

Integrate's text is `Replaced by role-<x>.md (the role) and brief.md (the envelope) in this folder (DEC-1050, TPL-1).` Taking it is one command per file and drops W2-11's side of all five, which the merge rule forbids doing by a lead (DEC-750, DEC-754: a conflict not resolved keeping the ticket's side is a PACKAGES). Keeping W2-11's side puts five full briefs back where W2-128's tests, W1-35's `briefs_stand()` and TPL-1 S4 say they are retired. And W2-11's success lines on the briefs (the twelve-field rule, payload after and two-refusal stop in **every brief template**; Policy 2's read rule and DEC-861's record rule; the audit brief's DEC-430; the launcher command as a command; record frontmatter on the **five brief templates**; `brief_gaps:` in the lead template; the brief half of the supersession line) name files that no longer carry text. What integrate's replacements carry today (grep, integrate head): `brief.md` has the twelve fields, a refusal line and `brief_gaps`; `role-lead.md` has the twelve fields; `role-test-designer.md` has DEC-820; the other role templates (20 to 40 lines) have none of: Policy 2's four refusals, DEC-861, two identical refusals, payload after. W2-11's tests `tests/acceptance/W2-11/test_w2_11_briefs.py`, `test_w2_11_brief_gaps.py` and the brief part of `test_w2_11_supersession.py` read `brief-*.md` and would go red after either resolution.

| option | what | cost | risk |
|---|---|---|---|
| (a) apply now | take integrate's pointers; product-spec re-homes the rules W2-11 still wants into `brief.md` and `role-*.md`; a designer revises the W2-11 brief cases to follow a retired brief (the pattern of W1-35's `brief_texts`) | ticket paths widened by the CTO (`brief.md`, `role-*.md`, `keys.yaml`) and the owner's nod (they are W2-128's, class (b)); about 2 to 3 h product-spec, 1 h designer, one more independent review of the new text | W2-128's tests and W1-35 share those files: a round of cross-breakage |
| (b) defer | land W2-11's skills and the rest now with the pointers taken, the brief KPIs listed as open rows for a follow-up ticket | merge about 1 h less; the ticket closes with a named gap | W2-11's success lines on the briefs stay unmet: a close would need the owner's ruling |
| (c) re-baseline | the owner re-baselines W2-11's brief KPIs to what TPL-1 left (a skill, `skill.md`, the orchestration and test-design and qa-review skills, the audit's DEC-430 wording), the CTO edits the ticket; the five pointers are taken; the brief cases go with a designer revision (removal, as W1-35 did) | ticket edit by the CTO, about 1 h designer; the shortest | loses the Policy 2 and DEC-861 rules in the role templates unless a later ticket adds them |

**Recommendation: (c), with (a)'s one addition,** that the CTO opens one small ticket for the role templates to carry Policy 2's four refusals, DEC-861's record rule and the two-refusal stop (the rules are live and the role templates do not state them: `role-engineer.md` has none). Confidence: medium (I read the texts, not W2-128's reviews). Not decided here; until it is, the five files are the one part of the merge nobody can write.

## 5. Groups C and D: the skills (product-spec's merge; the rule per hunk)

Both branches bumped the version lines and edited the same skills. Rule for each hunk, the same in the four copies (kernel, `.rulesync`, `template/.rulesync`; the `.claude` copy follows by regeneration):

1. **`discovery`, `retrieval` (version hunk only).** Integrate's `version: "1.1.0"` (W2-142: search again once; the body edit merged cleanly) plus W2-11's `metadata:` block with the **same** number: `version: "1.1.0"` and `metadata:` / `  version: "1.1.0"`. W2-11's case `test_the_skill_carries_one_version_in_all_four_places` needs the number in the kernel source and in the generated `.claude` copy's `metadata.version`.
2. **`test-design` hunk 1 (front matter).** `version` and `metadata.version` equal, one number: integrate's was 1.2.0 and W2-11's 1.1.0, both from 1.0.0, two independent changes merging: use **1.3.0** in all four places (any number works for the test; 1.3.0 states both changes). The description is W2-11's ("... in parallel with the implementer and never reading its work"), which carries integrate's meaning.
3. **`test-design` hunk 2 (the body).** W2-11's three bullets and four Inputs stand, with integrate's two facts folded in: the designer may read the integrated code on `w2/integrate` (DEC-963, DEC-820) and never this ticket's implementation (W2-11's second bullet already says it); keep integrate's citation letters (`CAP-38.c`) over W2-11's (`CAP-38.b`) after checking them against `docs/contract/` (a mismatch there is the product-spec's to settle by the Contract). Do not drop W2-11's "work order in parallel" bullet (DEC-959 item 7: KPI line).
4. **`orchestration` hunk 1 (version):** 1.3.0, four places, as item 2.
5. **`orchestration` hunk 2 (lead line, ceiling line).** Integrate's wording for the lead line (`brief.md` and `role-lead.md`, DEC-236, DEC-1050); W2-11's line "No fixed number of tickets in flight ... (DEC-847)". Integrate still says "A stated ceiling holds: at most `<ceiling>` tickets in flight", which W2-11's failure line forbids (DEC-866, DEC-847, DEC-942) and which integrate's own W1-35 revision removed from the test: do not keep it.
6. **`orchestration` hunk 3 (session start and the returns).** Integrate's first line (envelope plus role templates; the five retired texts are pointers); W2-11's second line (twelve fields, payload after, "Stop after two identical refusals and return", CAP-37, AR-6). Drop W2-11's "Each carries the standing sentences word for word (DEC-537)" unless section 4 keeps the briefs.
7. **`orchestration` hunk 4 (checkpoint).** Integrate's line (DEC-1057: no committed checkpoint record required at each round boundary) followed by W2-11's sentence "A checkpoint is written at every handover (DEC-837 item 3)." (W1-35's clause "a checkpoint at every handover" and `test_w2_11_supersession.py` line 40 need it).
8. **`orchestration` hunk 5 (hygiene and Policy 2).** Integrate's three lines (reads open; held-out contents never read; the temp-folder line with DEC-820); they carry Policy 2. Check that W2-11's `test_w2_11_briefs.py` line 43 ("Policy 2 (c), the counterpart's work") is satisfied by integrate's list ("the counterpart's work on the same ticket"); if a case wants the words "Policy 2", add them to the line.

**After the textual merge, three auto-merged things are wrong on meaning** (the tests catch each; the product-spec fixes them in the same merge commit): (i) `template/governance/kernel/skills/{change,checkpoint,planning}/SKILL.md` and `audit`: if integrate bumped one of them, the `metadata.version` and `version` must agree (they auto-merge to a mixed pair when only one side moved the line); (ii) the `.claude/skills/{discovery,retrieval}/SKILL.md` copies auto-merge with `metadata.version: "1.0.0"` against a source at 1.1.0; (iii) the six role copies of the orchestrator (`template/governance/kernel/roles/orchestrator.md`, the two `.rulesync/subagents/orchestrator.md`, `.claude/agents/orchestrator.md`) merged: re-read the lead line and the ceiling sentence there against item 5.

**The merge, by whom.** The ticket's writing role is product-spec (the lead cannot write under `template/`; a designer cannot). One product-spec session, in `/home/usain/gov-os-worktrees/W2-11`, after the designer's commit: `git merge --no-ff w2/integrate`; resolve groups C and D by the rules above; leave group E and group B (section 4) as the CTO's; then the commit with `Task: DAEO-k7hz`, `Role: product-spec`, `Implements: DEC-866, DEC-959, DEC-983` (ids of the ticket's sources, ACCEPTED) and a message that names each choice. Conflicts the session cannot settle keeping the ticket's side: PACKAGES, no `-s ours`. A product-spec merge that leaves conflict markers or leaves group B open cannot be committed: so **the merge waits on the section 4 decision, or the CTO takes option (c)'s pointers as given**.

## 6. Group E: the generated `.claude/` copies

`.claude/skills/orchestration/SKILL.md` and `.claude/skills/test-design/SKILL.md` conflict because both branches edited generated text. They are written by rulesync from `.rulesync/skills/**` (class (b), the CTO's or the operator's: W2-11's round 1 waited for them the same way, P-W2-11-5 (b)). Settle them **after** groups C and D by regenerating from the resolved `.rulesync` sources, not by hand: the only hand edit allowed is `metadata.version`, which rulesync writes. The `.claude/skills/{discovery,retrieval}` copies (item (ii) above) and the audit and other skills' copies are in the same pass.

## 7. Order and launch

1. Owner decision on group B (section 4); the CTO edits the ticket if (a) or (c).
2. Designer, W1-35 pre-merge commit (10 minutes, about $2). Launch:

```
cd /home/usain/gov-os-worktrees/W2-11 && LAUNCH_TICKET=DAEO-k7hz bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh --model claude-opus-5-5 --class C2 --projection-usd 2 independent-test-designer high /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/W2-11-A1-merge.md
```

3. Product-spec merge (section 5), then the CTO's regeneration (section 6), then `gov accept W2-11` (round 1 ended at 147 passed, 1 skipped), W1-35's and W2-128's acceptance folders, and the scoped run. W2-11's brief cases wait on group B.
4. Re-run `git merge-tree --write-tree --name-only w2/W2-11 w2/integrate` just before step 3: if integrate moved, the 20-file list may change (the designer's brief stops with PACKAGES if the W1-35 file conflicts again).

## 8. Evidence

`drafts/w2-11/tmp/mt.txt` (the merge-tree answer), `tmp/conf/` (each conflicted file with markers), `tmp/mt2.txt` (after the designer's commit, simulated), `tmp/build_pre.py`, `tmp/simulate.sh`. No ref, branch or worktree was touched; `git merge-tree` and the simulation wrote loose objects only. Not read: the generated copies' body diffs beyond the markers; W2-128's reviews; the Contract's CAP-38 letters (item 3); `docs/changes/W2-11-CIT-P.md` (it may name the version to state).
