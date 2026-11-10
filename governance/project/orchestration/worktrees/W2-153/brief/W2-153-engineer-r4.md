Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 — S3 amended: the role file's fields in the composed agent, the engineer's brief (DAEO-8s85)

You are a fresh engineer for **W2-153** (`.tickets/DAEO-8s85.md`). Read its body's **"S3 amended"** in full: it is
the CTO's decision and the interface you build to.
- Each composed `.rulesync/subagents/<role>.md`, and `template/.rulesync/subagents/<role>.md`, is:
  - its rulesync front matter (with `claudecode.skills`) as now;
  - then the role template's body;
  - then one blank line;
  - then the kernel role file's body (`template/governance/kernel/roles/<role>.md`, verbatim, its front matter, if
    any, stripped by portability's `_split` rule).
- `gov.adapters.portability` exposes **`compose(root, role) -> str`**, the expected source's full text. The check
  compares each source with it. Use one implementation; the CTO's ACT builder will call it.
- The approved templates do not change. Never touch `template/governance/kernel/templates/` or the role files.

## The work
1. **`src/gov/adapters/portability.py`:** `compose(root, role)` and the S3 comparison using it. A `SOURCE_DIFFERS`
   finding names both origins, the template and the role file, so a reader knows what the source is built from.
   Keep the `TEMPLATE_COPY_*` checks as they are.
2. **The twelve sources** (the six roles, in both rulesync folders): write each from `compose()`. A tiny script in
   your scratch, run once, is fine. Nothing else in them changes.
3. **Unit tests** in your paths (`tests/unit/adapters/test_w2_153*`): `compose()` on a fixture, and the comparison.
4. **Check:**
   - `gov accept W2-153` on your tree, with the designer's revised cases merged in by the CTO;
   - `tests/unit/adapters` and `tests/unit/launch` in full, with
     `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`;
   - `python3 -m gov.adapters.portability` with `RULESYNC_BIN=/home/usain/.local/bin/rulesync`: only
     `GENERATED_DIFFERS` for the six agents, which ACT-CLAUDE-COPIES-3 regenerates;
   - W1-33's suite (`tests/acceptance/W1-33`), whose role-file field cases read the composed sources' agents: report
     its counts, expecting its `.claude/agents` cases red until the ACT.
5. **Prove the six fields reach the agents:** on a temporary copy, run
   `rulesync generate --targets claudecode --features subagents --input-roots <copy>/.rulesync` into an empty folder.
   Quote one generated agent's field labels.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-153`, branch `w2/W2-153`, with integrate and the designer's cases
  merged in by the CTO. Your paths: the ticket's `allowed_paths`. Use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153/src`.
- **You never read `tests/acceptance/W2-153/`** (DEC-820 (c)). Run it only through `gov accept`, or with
  `python3 -m pytest … -rf` if `gov accept` crashes in the sandbox, and read only the result lines.
- Never start a real session. No GPU, model, network, installs or `gov retrieve`. Never open `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per
  Bash call. Search again once (DEC-1092 (1)) if a search does not answer. Do not merge. Never touch
  `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-153`, only your paths, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the diff summary, the counts, the portability findings and the quoted labels.
