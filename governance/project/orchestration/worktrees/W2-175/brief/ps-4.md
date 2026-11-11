# Brief: product-spec, DAEO-wahn (W2-175), run 2: the six template/.rulesync role compositions

You are a fresh **product-spec** session (template `role-product-spec`, in your system prompt), started by the ticket lead. This brief was written by hand: `gov context DAEO-wahn --role product-spec` refused (run 1: `CONTEXT_OVER_CEILING`, 21044 of 6000 tokens; this run: `STORE_MISSING` in the worktree, `BLOCKED: DEC-1137 not found` against the main tree's store). Where this brief and the copied `EMG-common.md` / `EMG-d4b-launched.md` differ, **this brief holds** (your `Implements:` is the list below, not `DEC-1065`).

## Identity
- Check: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec`, `DAEO-wahn`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-175`, `w2/W2-175`). Different: stop and say so.
- **Step 0, the sandbox check, reported first in your return:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wahn','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop and return.

## Where things stand
The seven role templates `template/governance/kernel/templates/role-*.md` are at 1.0.1 (commit `c816990fcdb4`) and final: never edit them. The change record `docs/changes/W2-175-CIT-P.md` is committed (head `6dc99e2c1`). The CTO widened the ticket's `allowed_paths` (P-2 (a), the ticket file's "Scope amended" line): the six rulesync role sources under `template/.rulesync/subagents/` must be re-composed from the new templates, because W2-153's check compares each source with `gov.adapters.portability.compose()`.

## The paths you may write (nothing else)
- `template/.rulesync/subagents/engineer.md`, `independent-auditor.md`, `independent-test-designer.md`, `orchestrator.md`, `product-spec.md`, `research.md` (all six under `template/.rulesync/subagents/`)
- `docs/changes/W2-175-CIT-P.md`
Not the root `.rulesync/` (the copies ACT writes it after the owner's approval, DEC-315), not `.claude/`, not the templates, not `tests/`, not `.tickets/`, not the register.

## The failing output (S6, run 1; you never read `tests/acceptance/W2-175/`)
`tests/acceptance/W2-153/test_w2_153_sources.py::test_s3_each_role_source_is_its_front_matter_its_skills_its_template_s_body_and_its_role_file_s_body[<role>-template/.rulesync]` fails for the six roles (engineer, independent-auditor, independent-test-designer, orchestrator, product-spec, research): the source is not `compose()`'s text since the templates changed. The `[<role>-.rulesync]` cases (root) and `test_s3_guard_...` also fail and stay red until the copies ACT: do not touch them.

## What to do
0. **Scratch folder:** run `printenv TMPDIR` first; call its value `<TMPDIR>` and write every script file there with the Write tool and that absolute path. The worktree's `.gov-runtime/scratch/` is NOT writable for you (ps-3 was refused there twice); a path inside the six sources or the record is.
1. Write a script file `<TMPDIR>/ps4_compose.py` (Write tool) that, for each of the six roles, computes `gov.adapters.portability.compose(Path("/home/usain/gov-os-worktrees/W2-175/template"), role)` and writes the returned text, exactly, to `/home/usain/gov-os-worktrees/W2-175/template/.rulesync/subagents/<role>.md` (`write_text(..., encoding="utf-8")`, no added newline), then prints each file's sha256 (12 digits) and whether it changed. Run it: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src python3 <TMPDIR>/ps4_compose.py`. Read `compose()` first (`src/gov/adapters/portability.py`, around line 176); do not hand-edit a composed file.
2. Check `git diff --stat -- template/.rulesync` shows only the six files, and `git diff -- template/.rulesync` adds only the template lines of c816990fcdb4 (the P2, C-E/C-D/C-R, REC, STOP statements and nothing else).
3. Run the six target cases: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src python3 -m pytest "tests/acceptance/W2-153/test_w2_153_sources.py" -q -p no:cacheprovider -k "template/.rulesync"` and report counts (names, pass or fail, messages). Expected: the six `template/.rulesync` cases pass.
4. Amend `docs/changes/W2-175-CIT-P.md` (only these edits):
   - In section 2, after the seven-row sha256 table, add a second table with the same columns (`File | Base sha256 | New sha256 | Statements added`) for the six `template/.rulesync/subagents/<role>.md` files: base sha256 from `git show 7709021ad6cc:<path> | sha256sum` (a script file in `<TMPDIR>`, `git show` through `subprocess`), new sha256 from `sha256sum` of the file you wrote (full 64 hex, as the existing table), and "composed by `compose()` from the role's template (W2-153 S3)" in the last column. One sentence before it: the CTO's scope amendment (P-2 (a)) added these six byte-determined compositions; the root `.rulesync/` copies follow by the copies ACT after the owner's approval.
   - In the "Not changed:" line, replace "any `.rulesync/` path" with "the root `.rulesync/`".
   - Nothing else: the front matter, the seven-row table and sections 3 to 5 stay as they are.
   Then load the front matter with `yaml.safe_load` in a script file in `<TMPDIR>` and print `status`, `decisions_read`, `decisions_carried` (it must still parse).
5. Run once and report the per-line reading (names, pass or fail, messages only): `env PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src gov accept DAEO-wahn --root /home/usain/gov-os-worktrees/W2-175`. If the sandbox refuses it, say so and go on.
6. Commit once: before it, `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit`; then
   `git commit -m "W2-175: the six template/.rulesync role sources composed from the 1.0.1 templates (compose(), W2-153 S3); CIT-P record names them" --trailer "Task: DAEO-wahn" --trailer "Role: product-spec" --trailer "Implements: DEC-1137, DEC-1116, DEC-1050, DEC-315, CAP-33" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- template/.rulesync/subagents/engineer.md template/.rulesync/subagents/independent-auditor.md template/.rulesync/subagents/independent-test-designer.md template/.rulesync/subagents/orchestrator.md template/.rulesync/subagents/product-spec.md template/.rulesync/subagents/research.md docs/changes/W2-175-CIT-P.md`
   Never amend, rebase, merge, push or `--no-verify`. The temp folder is removed when your session ends.

## Rules
- Policy 2 (c): never read `tests/acceptance/W2-175/` (every Grep/Glob excludes `!tests/acceptance/W2-175/**`; recursive searches `--exclude-dir=W2-175`); if a line from there shows anyway, stop reading it and say so. (d): never the hidden half of an evaluation set (`~/gov-os-eval`), the held-out material's contents, or a secret.
- DEC-732, word for word: **every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src` set per command.**
- Memory: `gov retrieve` is not available in your sandbox (DEC-1065): Read and Grep; search again once in different words if a search does not answer; two searches in all.
- Command forms: one simple command per Bash call; no `cd ... &&`, here-documents, backticks, `$(...)` or shell variables as a write target; no long inline `python3 -c` with braces; anything longer than one line goes in a script file under your session's temp folder `<TMPDIR>` (step 0 of What to do).
- Row W2-L423's rule (DEC-911): in your return, commit hashes and sha256 as 12 digits; never the keywords of the secrets rule that takes a bare 40-hex string.
- Scratch budget (DEC-898): 200 MB and 10,000 files; clean as you go. No installs.
- **Refused twice for the same call: stop and say so. Never work around a refusal: report it.**

## Return (your last message; nothing else is read)
Sandbox check first; in `evidence` the commit (12 digits) with trailers, the six sha256 (12 digits), the pytest counts, the YAML check's output, `gov accept`'s per-line reading.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

The twelve fields come first, each as a labelled line, any payload after them. Refused twice for the same call: stop and say so.
