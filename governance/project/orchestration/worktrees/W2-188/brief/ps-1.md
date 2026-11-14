Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-188 (DAEO-zlog): the adopt skill's step 6 and the practice record, product-spec (brief ps-1, from the ticket lead)

You are the product-spec worker for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C2, by the CIT-P route (a
kernel skill change: the owner approves its bytes after an independent review, before any merge; CAP-33, DEC-1166 (4)).
Use your skill `spec-writing` where it applies.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188 |
| branch | w2/W2-188 (from w2/integrate at 5336a6fca, the base) |
| the ticket (read whole; its **Interface** I1-I6 first: it is binding) | /home/usain/gov-os-worktrees/W2-188/.tickets/DAEO-zlog.md |
| the CIT-P draft to start from (a copy of the CTO's) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/draft-W2-188-CIT-P.md |
| the context packet (`gov context DAEO-zlog --role product-spec`, JSON: ticket and decisions' texts) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/ctx-ps.md |
| the reconciliation (G4, G6) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/MEMORY-AUDIT.md |
| the decision package | /home/usain/gov-os-worktrees/W2-188/governance/project/orchestration/packages/MEMORY-AUDIT-P1.md |
| the figures' sources | governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md, .../LIFT-1/E3-RESULT.md |
| the step matcher | tests/acceptance/W2-88a/w2_88a_support.py (`a9_regions`, `check_steps`, `check_pointer`, `heading_section`) |
| your scratch | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/ps/ |

Allowed paths, and the only ones you write: `template/governance/kernel/skills/adopt/SKILL.md`,
`.rulesync/skills/adopt/SKILL.md`, `template/.rulesync/skills/adopt/SKILL.md`, `docs/research/W2-88-memory-practice.md`,
`docs/changes/W2-188-CIT-P.md`, `docs/probes/DAEO-zlog/**`. Never `.claude/` (the copies ACT regenerates
`.claude/skills/adopt/SKILL.md` after the owner's yes) and never any test file (`tests/**`): F2.

Read the register by id only (`docs/DECISION_REGISTER.md`, 1.6 MB; grep `### DEC-1179` and the others in the ticket's
`sources:`). Search with the Read and Grep tools; if the first search does not answer, search once more in other words.

## The work (the draft's §2 is the text; three gaps to close, and the interface rules)
1. **The skill, four places only** (I1): edit `template/governance/kernel/skills/adopt/SKILL.md`, then copy its bytes to
   the two `.rulesync` copies (`cp`), so all three are byte-equal:
   - line 4 `version: "1.0.0"` -> `version: "1.1.0"`;
   - line 58, step 6, replaced in place by one numbered line as the draft's §2.1 gives it, **with the literal phrase
     `counts only`** (gap 1: the draft says "with only counts leaving its run"; e.g. "behind the walls, counts only: only
     counts leave its run"). It must hold each of: `standing set`, `every week`, `same questions`, `95 %`, `counts only`,
     `never chooses or judges a fix`, `fresh set` and `month`, `fitted` and `replaced`, `DEC-1179`; and say a miss is
     never re-run in the same week and never re-scored. It keeps `Declare` (first word), `measure`, `the verdict set`,
     `once`; it must not contain the step-7 anchor (`record...` then `every|each|all` then `method` within one sentence);
     no `gov.memaudit`, no `standing declare`; never calls the reader a second reranking model; no method figures (they
     belong in the practice record);
   - a new paragraph after line 59 (step 7), one blank line before it, before `## Verify clauses for adopted tickets`, as
     the draft gives it: it holds `cron`, `ACT`, `operator`, `never installs` (or `never installed`), `95 %`, and points to
     the practice record's section 9; consider citing `[DEC-1179 (4), (5), DEC-1101 (2), DEC-1125 (2)]` (S2 cites (4));
   - line 74, the sources line: add DEC-1101, DEC-1125, DEC-1179 in numeric order, nothing else.
   Use plain ASCII spaces (in `95 %` too). Nothing else in the skill changes: `git diff 5336a6fca --
   template/governance/kernel/skills/adopt/SKILL.md` must show exactly those four hunks.
2. **The practice record** `docs/research/W2-88-memory-practice.md` (I4): re-word §3's bullet (lines 91-92), §5 item 6's
   two sub-bullets (lines 190-191) and §6 step 6 (line 221) as the draft's §2.2 quotes them; leave §3's "3 points" and
   step 5's "5 points" as they are. Append `## 9. The standing set (DEC-1179)` after §8, at the end, as the draft gives it,
   with gap 2 closed (§9 holds the literal phrases `counts only` and `never chooses or judges a fix`: e.g. the walls bullet
   "...counts only: only counts leave the run: ..." and the fixes bullet "...the standing set never chooses or judges a
   fix, and never adopts or rejects one") and gap 3 closed: §9's last bullet becomes DEC-1179 (4)'s text, **byte for
   byte** as recorded in the register (the line `  - (4) ` under `### DEC-1179`, from `**Below 95 %:**` to its closing
   `.`; copy it with a script from the register, do not retype it; note its `§` is UTF-8). It begins:
   `**Below 95 %:** the package's §5.1 rules R1 to R9 (a miss recorded by counts only, never re-run or re-scored; ...`.
   Introduce it as the owner's rule in DEC-1179 (4) and keep the quoted bytes unbroken on one line. §9 keeps: what it is;
   the method (the reader ranking the whole bundle, searching again once, A2, E2's 115 and 128 of 138, E3's 114 against
   84); the bar `ceil(0.95 n)`; the walls (no id, question, gold or answer printed, logged or read, not even by the
   auditor); fixes; staleness by count; the monthly check with its two 5-point rules; and the sentence that W2-88 S10's
   second reranking model stays forbidden and the reader is not one. §6 must still pass `check_steps`.
3. **The checks (I5), recorded under `docs/probes/DAEO-zlog/`** (e.g. `checks.md` with the commands and their output):
   `check_steps` on `a9_regions` of each copy and on the practice record's §6 (no problems); `check_pointer` on A9's
   region (no problems); `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt`
   (exit 0; run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-188/src`); `sha256sum` of the three copies (equal);
   `grep -c 'gov.memaudit\|standing declare'` of the three copies (0); the I1 `git diff --stat` and hunk count; and a
   string check of each literal phrase above in step 6, the paragraph and §9, plus §9's verbatim equality with the
   register's DEC-1179 (4). Run them with a python script importing `w2_88a_support` from its path. No test suite.
4. **The CIT-P record** `docs/changes/W2-188-CIT-P.md` (I6), built from the draft, **the last file you change**:
   front matter with `id: W2-188-CIT-P`, `ticket: DAEO-zlog (W2-188)`, `status`, `base: 5336a6fca`, `head` (the commit
   holding the skill's final bytes), `review: PENDING`, `decisions_carried` (add DEC-1072), and
   `owner_approval: 'pending'` (the CTO writes it after the owner's yes; never write an approval); §2 the old and new text
   of each changed place, as finally written (the skill's four places and the practice record's four); §3 the sha256 before
   (`16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0`) and after (the kernel copy as committed, equal in
   all three) and the practice record's before and after, with the skill's lines added and removed as `git diff --numstat`
   gives them; §4 the three options (DEC-105); §5 the impact table (W2-11's
   `test_every_copy_carries_the_kernel_skills_body[adopt]` red from the merge until the copies ACT; W2-11's version cases
   exclude `adopt`; W2-88a's cases unchanged: say you ran its `check_steps` on the new text); §6 the review: say it is
   pending, and write **no `verdict:` line** (the lead adds the reviewer's verdict line after the review). Remove the
   draft's "DAEO-NEW2" and "provisional" wording: DEC-1179 is recorded and ACCEPTED, DEC-1176 is recorded.

## Commits (your paths only; trailers in ONE final paragraph, no blank line inside it)
Commit in batches (the skill's three copies; the practice record; the probe record; the CIT-P last), each as:
```
git commit -m "<subject>" --trailer "Task: DAEO-zlog" --trailer "Role: product-spec" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1074, DEC-1072, DEC-1071, DEC-105, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>
```
`Implements:` lists only ids from the ticket's `sources:`. If anything changes the skill after the CIT-P is written,
recompute the after hash and commit the CIT-P again last.

## Rules
- Write files with the Write and Edit tools and absolute paths; anything longer than one line goes in a script under
  /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/ps/, run with `python3 <file>` or `bash <file>`.
- Use the sandbox's own `$TMPDIR`. You run no pytest; if you ever do, through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
  `PYTHONUSERBASE=/home/usain/.local -p no:cacheprovider -o tmp_path_retention_policy=failed`.
- Never open the evaluation sets' root (`~/gov-os-eval`), any hidden or memory-verdict folder, or secrets.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- No new ticket; a gap comes back in `unresolved` as a question with options, cost and a recommendation.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: each commit's hash and subject; the skill's sha256 after; the CIT-P record's sha256; the I5 results in one line each.
