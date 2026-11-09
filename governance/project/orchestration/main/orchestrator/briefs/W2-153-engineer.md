# W2-153 — the engineer's brief (DAEO-8s85)

You are a fresh engineer for **W2-153** (`.tickets/DAEO-8s85.md`): the role template delivered at launch (W2-128
TPL-4). Read the ticket in full first: five KPI lines, two failure lines, and **its body's "Interface"**: the role →
template map, where the flag goes, the skills lists, and the rule that this ticket commits no `.claude/` file. Then
read `R3-TEMPLATES.md` §B ("Delivery") and §D TPL-4, and `governance/project/orchestration/packages/ACT-CLAUDE-COPIES-1.md`,
the copies ACT this ticket lands with.

## Points the test design settled (follow them)
- **D-1:** the skills lists are the ticket's, not the kernel templates' own `skills:` front matter.
- **D-2:** the kernel role files have no front matter. A `.rulesync/subagents/<role>.md` source keeps its rulesync
  front matter as it is on integrate, adds `skills:`, and takes the kernel role **template**'s body.
  `gov.adapters.portability` compares the source against that composition.
- **D-3:** `--write-templates <dir>` writes exactly the eight copies. `<dir>` may be the copies' folder or a root
  holding `.claude/templates/`. State which in the evidence.
- **D-4:** `launch_now.sh` calls `claude` by absolute path. Keep the call form; add the flag and the refusal.
- **D-5:** the test designer's list leaves out `test-design` until the kernel skill states DEC-963. That has landed on
  `w2/W2-128`, not yet on integrate. Implement the ticket's rule: left out until then, with a comment naming W2-128.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-153`, branch `w2/W2-153`: integrate with the designer's 50
  cases merged (TESTS-READY `0c73fd5a2cbe`). **Your paths:** the ticket's `allowed_paths`:
  - `src/gov/launch/launcher.py` and `src/gov/adapters/portability.py`;
  - `tests/unit/launch/test_w2_153*` and `tests/unit/adapters/test_w2_153*`;
  - `governance/project/orchestration/tools/dispatch/launch_now.sh`;
  - `.rulesync/subagents/*.md` and `template/.rulesync/subagents/*.md`;
  - `docs/changes/W2-153-evidence.md`.
- Rewrite each `.rulesync/subagents/<role>.md` (and the template's) to the S3 composition, for the six roles. The
  generated `.claude/agents/` are the ACT's: never touch `.claude/`. Portability will report `GENERATED_DIFFERS` on
  your branch until the ACT; that is expected, so say so.
- **You never read `tests/acceptance/W2-153/`** (DEC-820 (c)). Run the cases only through
  `python3 -m gov.cli.main accept W2-153 --root /home/usain/gov-os-worktrees/W2-153`. If that crashes in the
  sandbox, run `python3 -m pytest tests/acceptance/W2-153 -q -p no:cacheprovider -rf` with
  `PYTHONUSERBASE=/home/usain/.local`. Read only the result lines. Exclude the folder from every search.
- Also run the existing launcher and portability unit tests (`tests/unit/launch`, `tests/unit/adapters`), with
  `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`. Then run W2-128's
  cases (`gov accept W2-128 --root …`). No whole-suite run. Use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153/src`.
- **Never start a real session.** No GPU, model, network, installs or `gov retrieve`. Never open `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- DEC-1080: one simple command per Bash call. Search again once (DEC-1092 (1)) if a search does not answer.
- Proportion (DEC-135): nothing beyond the KPI lines. A launch changes only by the one flag (F2).
- Do not merge. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-153`, only your paths, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1052" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
Your final message, in full:
- the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
- the files changed and the line count;
- `gov accept W2-153`'s counts, with each failing case's node id and message;
- the existing unit suites' counts and `gov accept W2-128`'s counts;
- the portability check's findings on your branch.
