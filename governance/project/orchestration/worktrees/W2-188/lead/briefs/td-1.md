# W2-188 (DAEO-zlog): acceptance tests, independent test designer (brief td-1, from the ticket lead)

You are the independent test designer for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C2. You write the
ticket's acceptance tests from its KPI lines before the product-spec worker's text lands, and you show each red on
today's code. Use your skill `test-design`.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188-tests |
| branch | w2/W2-188-tests (from w2/integrate at 5336a6fca, the base) |
| the only paths you write | tests/acceptance/W2-188/** |
| the ticket (read whole; its **Interface** I1-I6 is how the KPI lines read) | /home/usain/gov-os-worktrees/W2-188-tests/.tickets/DAEO-zlog.md |
| the context packet (`gov context DAEO-zlog --role independent-test-designer`, JSON; the decisions' texts) | /home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/lead/briefs/ctx-td.md |

Never read /home/usain/gov-os-worktrees/W2-188 (the counterpart's tree, DEC-820). Read freely in your own tree: the
register (`docs/DECISION_REGISTER.md`, grep it by id only, it is 1.6 MB; DEC-1179 is at `### DEC-1179`), the skill
`template/governance/kernel/skills/adopt/SKILL.md` and its two copies `.rulesync/skills/adopt/SKILL.md`,
`template/.rulesync/skills/adopt/SKILL.md` (74 lines, sha256 `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0`
at the base), the practice record `docs/research/W2-88-memory-practice.md` (280 lines at the base),
`tests/acceptance/W2-88a/**` (its `w2_88a_support.py` has `a9_regions`, `check_steps`, `check_pointer`,
`heading_section`, `stated_counts`, `verdicts`, `owner_approval_lines`, `run_skill_validator`: reuse it by import, as a
module loaded from its path, or copy what you need; never edit it), `tests/acceptance/W2-11/**`, and
`docs/changes/W2-88a-CIT-P.md`, `docs/changes/W2-98-CIT-P.md` (earlier CIT-P records, for the form).

## What to test (the ticket's lines; read them in the ticket, with I1-I6)
- **S1** step 6 of A9 in each of the three copies holds `standing set`, `every week`, `same questions`, `95 %`,
  `counts only`, `never chooses or judges a fix`, `fresh set` with `month`, `fitted` with `replaced`, `DEC-1179`; and
  W2-88a's `check_steps` returns no problem on A9's region (`a9_regions`) of each copy. "Step 6's stretch" is the text
  from the line starting `6.` to the line starting `7.` inside A9's section.
- **S2** a paragraph between step 7 and the `## Verify clauses for adopted tickets` heading, in all three copies, with
  `cron`, `ACT`, `operator`, `never installs` or `never installed`, and `95 %`.
- **S3** in the practice record: §3's confirmation bullet (the `Consistency is the proof` bullet) names the standing set;
  §5 item 6's practice sub-bullets name the standing set and that it never chooses or judges a fix; §6 step 6 still passes
  `check_steps` (on §6's section) and names the standing set; a new heading `## 9. The standing set (DEC-1179)` holds:
  `counts only`, `never chooses or judges a fix`, the reader ranking the whole bundle and searching again once, `A2`, the
  E2 figures 115 and 128 of 138, E3's 114 against 84, the bar `ceil(0.95 n)`, staleness by count, the monthly check with
  its two 5-point rules, the sentence that W2-88 S10's second reranking model stays forbidden, and DEC-1179 (4)'s text
  as a verbatim substring. Take that text from the register **at test time**: the line beginning `  - (4) ` inside
  `### DEC-1179`, from `**Below 95 %:**` to the end of the line (the closing `.`). Pin also its expected start
  (`**Below 95 %:** the package's §5.1 rules R1 to R9`) so a register edit is noticed.
- **S4** the three copies byte-equal; front matter `version: "1.1.0"` in all three; `git diff 5336a6fca --
  template/governance/kernel/skills/adopt/SKILL.md` has exactly four hunks: the version line, step 6, the new paragraph
  after step 7, the governing sources line (which gains DEC-1101, DEC-1125 and DEC-1179 in numeric order, and keeps every
  id it had); A9's steps 1-5 and 7 and the Verify section are unchanged from the base;
  `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0.
- **S5** `docs/changes/W2-188-CIT-P.md` exists and holds: the before sha256 `16fd341f...` (full); an after sha256 equal to
  the kernel copy's sha256 as committed at the last commit that changes it; the lines added and removed (W2-88a's
  `stated_counts` reads the usual forms) matching the real diff against the base; the old and new text of each changed
  place; the impact table naming W2-11's case `test_every_copy_carries_the_kernel_skills_body[adopt]` and W2-88a's cases;
  `verdict: PASS` as the last `verdict:` line; an `owner_approval:` line naming the after sha256. **Put the
  owner_approval check in its own test function**, and the verdict check in its own: the owner writes approval after the
  review (the line reads `'pending'` until then), so that one case is expected red at the ticket's DONE and turns green
  only at the owner's yes; name this in the README's map as "red until the owner's approval, by design".
- **F1** no `gov.memaudit` and no `standing declare` in the three copies (a guard, green now), plus the S4 hunk check.
- **F2** `.claude/skills/adopt/SKILL.md` is byte-equal to the base's; no commit after the base with `Task: DAEO-zlog`
  whose `Role:` is not `independent-test-designer` touches `.claude/` or `tests/`.
- **F3** step 6 and §9 hold `never chooses or judges a fix` and `counts only`; §9 says the second reranking model of
  W2-88 S10 stays forbidden and the reader is not one; neither step 6 nor §9 says the standing set may choose, judge,
  adopt or reject a fix (write the negative check as you judge best and state the reading in the README).

## How
- Tests only read files and run child processes (`git`, the skill validator); never a store, model, network or
  `gov retrieve`. Locate the repository from `Path(__file__)`. Give each child this tree's `src/` first on `PYTHONPATH`.
- A `README.md` in `tests/acceptance/W2-188/` with the map: each KPI id to its tests by **full node id**
  (`test_<file>.py::test_<name>`, every item), the expected red reason on the base, the cases green now by design, the
  totals, and your readings where the ticket is silent.
- Show the reds on the base: run the folder through the heavy slot, with the sandbox's own `$TMPDIR`:
  `env HOME=/home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-188-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-188 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (make the empty-home folder first; if the heavy slot refuses for a resource gate, that is a wait: wait and retry; if
  the sandbox refuses the heavy slot itself, run the same pytest line without it and say so).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/.
  Write files with the Write and Edit tools and absolute paths.

## Commit (your paths only; trailers in ONE final paragraph)
```
git commit -m "W2-188 (DAEO-zlog): acceptance tests from S1-S5, F1-F3" --trailer "Task: DAEO-zlog" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1074, DEC-1072, DEC-105, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-188
```

## Rules
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- Never open the evaluation sets' root (`~/gov-os-eval`) or any hidden or memory-verdict folder; never secrets.
- No new ticket; a gap comes back in `unresolved` as a question with options.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: your commit's hash; the pytest counts on the base (passed / failed) with each red's reason in one line; and a
`TESTS-READY` text (the lead writes the marker).
