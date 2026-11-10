Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 — S3 amended, the independent review (DAEO-8s85)

You are a fresh, read-only independent reviewer. Review **W2-153**'s S3 amendment (`.tickets/DAEO-8s85.md`: read
its body's "S3 amended" in full: the CTO's decision and interface).

## What to review
- **The branch:** `w2/W2-153` in `/home/usain/gov-os-worktrees/W2-153` at `f387de57b`, against `w2/integrate`. It
  holds:
  - `3cf6c4951`: `portability.compose(root, role)`, the S3 comparison against it (`SOURCE_DIFFERS` naming both
    origins), the twelve `.rulesync/subagents/*.md` sources written from `compose()`, and unit tests;
  - `f387de57b`: the evidence;
  - the designer's revision `9a6f55c5af7b` (`Rewrite-Reason:`): W2-153's S3 cases, and W1-38's project builder
    copying the kernel's `templates/` (and the template copies), with W2-05's hooks-source fixtures adjusted.
- **The runs (the CTO's, outside the sandbox):** `gov accept W2-153` 66/66; W2-128 121/121; `tests/unit/adapters`
  and `tests/unit/launch` 314 passed.

## Check
- **`compose()`:** for each of the six roles, is it exactly front matter (with `claudecode.skills`), the role
  template's body, one blank line, and the role file's body?
  - Do the composed sources' labelled fields equal the role file's (W1-33's `fields()` rule, in
    `tests/acceptance/W1-33/w1_33_support.py`)?
  - Does the template contribute none?
  - Generate with rulesync on a temporary copy (`rulesync generate --targets claudecode --features subagents --input-roots <copy>/.rulesync`)
    and check that each generated agent has the six fields, its skills and the template's text.
- **The approved templates:** do they stay byte-unchanged (`git diff w2/integrate -- template/governance/kernel/templates/`)?
  Do the role files stay unchanged?
- **The builder revision:** is it the minimal fix (templates copied file by file as roles and skills are)? Does
  W2-05's adjustment keep its assertions? Is any other project builder missing `templates/`?
- **Robustness:** is a role with no template, or a missing role file, handled by a named finding, never a traceback
  in the check?
- **The ACT that follows:** `.gov-runtime/scratch/orchestrator/tools/build_claude_copies_act.py` now writes role
  sources through the clone's `compose()`. Read its `composed()` helper. Is it the same function, not a copy?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- You write nothing in any tree: tests read-only with `-p no:cacheprovider`, rulesync only into a temporary folder.
  Single simple Bash commands (DEC-1080). Never start a real session. Never open anything under `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - every finding with `scope: in|out`;
  - the fenced `verdict` block in DEC-1010's form, one entry, `"kpi": "S3"`:
    `{"kpis": [{"kpi": "S3", "verdict": "pass|fail", "findings": [...]}]}`.
