# The review of ACT-CLAUDE-COPIES-4: the generated copies of W2-175's approved role templates (DEC-1139)

You are a fresh, read-only independent reviewer of an ACT before it goes to the owner for a yes and then to the
operator agent (class (b); DEC-1104 (2): rehearsal, a READY review and matching hashes). READY is computed by
`verdict.py` from your block.

## The ACT
- **The package:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/claude-copies-4/ACT-CLAUDE-COPIES-4.md`.
- **The bundle:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-4/`
  (`apply.sh`, `list.txt`, `manifest.json` sha256 `6ab06e85cae2d566c9da540c9ef0ec60c9edc366b6d5e5ccb7401a7d6d99fd17`,
  `rehearsal.log`, `before/`, `after/`); its builder `.../drafts/claude-copies-4/build_claude_copies_act_4.py`.
  Precedent: `governance/project/orchestration/packages/ACT-CLAUDE-COPIES-3.md` and `.../acts/ACT-CLAUDE-COPIES-3/review.md`.
- **What it writes (19 files):** the 7 `.claude/templates/role-*.md`, the 6 root `.rulesync/subagents/*.md` and the 6
  `.claude/agents/*.md`, generated from W2-175's templates approved by the owner at `w2/W2-175` `4c0c73472fd8`
  (DEC-1139; the 13 template and source sha256 values in `/home/usain/gov-os-worktrees/W2-175/docs/changes/W2-175-CIT-P.md` §2).

## Check
1. **The bytes are the approved ones:** the 7 templates and 6 sources in `after/` equal CIT-P §2's new sha256 values;
   the 6 agents equal rulesync 24.0.0's output on those sources (as ACT-3's were made); `before/` equals the live files on
   `w2/integrate` today; recompute every hash in the package, `list.txt` and `manifest.json`.
2. **Nothing else, and nothing weaker:** no file outside the 19; diff each agent and template against its before copy:
   only W2-175's added lines (Policy 2's four refusals, DEC-861's record rule, the two-refusal stop, the version line)
   and their composition; no tool list, permission or front-matter field widened.
3. **The order and the window:** the package says the 9 named red cases (W2-153's role-source and guard cases, two unit
   adapter cases) last from the ACT's commit until W2-175 merges, and proposes: hold the merge queue and the nightly,
   apply, merge integrate into `w2/W2-175`, re-run S6 (254/0) and portability (exit 0), CIT-P §4-5 ACCEPTED, merge and close
   W2-175, release. Is that order sound, is the window bounded, and is there a better order? One line each.
4. **apply.sh is safe:** `check` changes nothing; `apply` acts only from the frozen before state; `undo` restores byte for
   byte only from the after state; it is ACT-3's script: are ACT-3's rows F2 (no stop on a failed step) and F3 (a
   leftover `rmdir`) still harmless here?
5. **Class and route:** `governance/project/operator/class-rules.yaml` row `agents-skills-kernel` (and `.claude/` rows)
   give (b); the operator agent applies it on `yes ACT-CLAUDE-COPIES-4 6ab06e85`. Right?
You may re-run the rehearsal in a fresh `--no-hardlinks` clone under your own TMPDIR (never the main tree): one test
folder per pytest run (conftest names clash across folders), through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
`-p no:cacheprovider -o tmp_path_retention_policy=failed`; `python3 -m gov.adapters.portability` reads the current
directory (no --root).

KPI id for the verdict block: `act-claude-copies-4`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT.

## Write and return
- **You write nothing** in any tree; never a live `.claude/` or `.rulesync/` file.
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080). Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
  Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Scratch budget 30 GB and 2,000,000 files and folders, in your own TMPDIR; remove your clone (`chmod -R u+w` first);
  report `du -sh` and `du -s --inodes` in `evidence`.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- Refused twice for the same call: stop and say so; no third try.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields first (task, status, work_completed, files_changed, evidence, tests, discoveries, risks,
    lessons, proposed_decisions, unresolved, recommended_next_action), the sandbox and `ps` checks in `evidence`;
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - then `REVIEW_MD_BEGIN`, a review record in markdown for `review.md`, `REVIEW_MD_END`;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "act-claude-copies-4", "verdict": "pass|fail", "findings": [...]}]}`, each finding
    `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 25 minutes.
