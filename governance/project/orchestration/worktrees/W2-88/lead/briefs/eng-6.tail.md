
## The work (an order that lets the lead merge between items)
1. **S27 first** (the longest to measure): unit tests in `tests/unit/secrets/test_w2_88_scan.py` (the same verdict per file as the one-per-file form on a planted set with planted test secrets built from parts in tmp, a link, a large file, `scan: off`, the order asked; a batch's finding put back on its own file only), red first, then the batching in `gov.secrets`. Measure on a planted 5,000-file tree in your tmp: files per second with a23678e27's code (a `git archive a23678e27 src` export in tmp on `PYTHONPATH`) and with yours, the same machine, the same slot; record both, the tree's shape, the CPU set and the thread budget in a "Run 7: the secret scan's speed (S27)" section of `docs/changes/W2-88-evidence.md`. Under 10 times: say what it would take (e.g. codeintel's per-path `path_holds_secret` calls batched, outside the paths) and record the figure as it is. Commit.
2. **S26:** unit tests, then the check in MA (`assess.py`, a new refusal code `ADOPT_PATH_IGNORED`) and at A0's start, from one list of the paths `gov adopt` writes and commits. Commit.
3. **S24:** unit tests (the resolver's three places and its refusal; no read at import; no `parents[3]` in `src/gov/adopt/`), then the resolver in `fabric.py` and the five reads through it. You may build a wheel in the release form inside a unit test's tmp folder to show it (item 3; only inside the test's code, never typed in Bash; installs nothing on the machine). Record in the evidence file what an installed release now finds and what it refuses (item 4). Commit.
4. **S25:** unit tests with a stand-in for the tool's answers (the whole-graph read refused over the cap; counts answered), then the named refusal in A9 (item 6). Commit.
5. Run your unit tests and the adopt, rebuild, store and secrets unit folders, then `gov accept W2-88` once (results only; the test designer's run-7 cases may be merged by then; the existing 217 must stay green). `git status` clean after your last commit.

## How to run (every pytest through the heavy slot)
`mkdir -p /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home`; use a subfolder of the sandbox's own `$TMPDIR` as `TMPDIR` (`/tmp` is read-only in the sandbox), never a folder in the repository or under `~/gov-os-runs`. From `/home/usain/gov-os-worktrees/W2-88`:
- unit tests: `env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=<your tmp subfolder> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/adopt tests/unit/rebuild tests/unit/store tests/unit/secrets -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- the acceptance suite, results only: `env TMPDIR=<your tmp subfolder> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh gov accept W2-88 --root /home/usain/gov-os-worktrees/W2-88`
- A resource gate's refusal is a wait (DEC-1146). Never `-x`.

## Machine, commands, commits
- 3 GB and 150,000 files outside the tracked tree (the 5,000-file tree included); clean up temp trees; no clone or copy of this repository beyond `git archive` exports of `src` in tmp. Measure your scratch before you return (`du -s --inodes`, `du -sh`).
- Write files with the Write and Edit tools and absolute paths. No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; anything longer goes in a script under `/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/eng/`, written with the Write tool. **Refused twice for the same call: stop and say so** (DEC-1142 (9)). On an authentication error, return `AUTH_REQUIRED`.
- Before each commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file. Never `--no-verify`, `core.hooksPath` on this repository, amend, rebase, reset, merge or push. Never commit while the tree holds a merge in progress (`git status` first).
- Trailers in one final paragraph: `git commit -m "<subject>" --trailer "Task: DAEO-2bdu" --trailer "Role: engineer" --trailer "Implements: DEC-954, CAP-44.b, CAP-44.f, CAP-17, CAP-20" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>`. DEC-1178 and DEC-1052 go in `discoveries`, not `Implements:`.

## Never
Never run `gov close`, `gov pause`, `gov rebuild` or `gov adopt` against this worktree, the main tree or any real repository (only on repositories your tests plant); never touch `~/gov-os-workbench/examin/` or the copies under `~/gov-os-runs/`; never ask or notify the owner; install nothing on the machine; never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`; never write a ticket file, the register, a plan file or a kernel file.

## Return
One message, your last. The twelve fields first, each a labelled line; then: where each interface item is built (path:line), your unit tests' counts, the S27 figures (files per second before and after, the ratio), `gov accept`'s counts and any red line with the reason you see, what you would need outside the paths (S24 item 4, S25 item 5, S27 if under 10 times) with your estimate, the sandbox check, read refusals met, scratch figures, your commits (12-digit hash and subject).

```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
Refused twice for the same call: stop and say so.
