---
id: W2-84-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-30
branch: w2/W2-84
base: 6324b0d76e70
ticket: DAEO-m1u3 (W2-84)
author: engineer (W2-84)
decisions_recorded: [DEC-950, DEC-820, DEC-845, DEC-873]
state_class: EVIDENCE
---

# W2-84: change-execution record (CIT-E)

This records the change of W2-84 (DAEO-m1u3) under DEC-950 item 1, the owner's answer (a) to P-W2-H063-1, which
approves this guard change under CAP-33: the refusal of an evaluation set's hidden part (DEC-820 (d), DEC-845)
covers every tree of the repository (the main tree, every registered worktree, the run clones under
`~/gov-os-runs/`) and the object store the worktrees share, matched by real path, fail closed. Before it, the
hidden part was one `_Part` rooted at the session's own project root: the orchestrator's probe of 2026-10-29
(row W2-H063) found the main tree's copy, another worktree's copy and a run clone's copy allowed to a measured
engineer. No write rule changes; a guard error still fails closed.

## 1. The change

| # | File | Change | Evidence |
|---|---|---|---|
| 1 | `src/gov/guard/reads.py` | **The trees.** `_trees`: the session's root and the trees `git worktree list --porcelain -z` names (through `_git`, its 5-second timeout and its environment unchanged), each by its real path; a project with no `.git` entry has its root alone. The runs root is `runs.root()` as named and by its real path, listed once per call. A session whose root lies under the runs root adds the trees of the repository named by the marker of its own folder (`_clone_trees`: `.gov-os-repository`, a regular file opened with `O_NOFOLLOW`, naming a git directory, whose `git worktree list` is run against it). `parts` builds one hidden `_Part` per tree, same globs, same `HIDDEN_REFUSAL`, and one `_Runs` part; `policy_refusal` finds the trees once per call for the session's and the subagent's roles together. | `tests/unit/guard/test_w2_84_trees.py`; acceptance `tests/acceptance/W2-84/` |
| 2 | `src/gov/guard/reads.py` | **The run clones.** `_Runs`: a path under the runs root is in the hidden part when the globs match it relative to any folder below the root, at any depth (not by the marker: a clone sits at any depth and a folder made by hand has none). It is walked below a search's start, or whole from above it, never into `.git`, bounded (folders walked plus files found over `_MOST_FILES` refuses with the existing "more files than the guard reads in bounded time"). | same |
| 3 | `src/gov/guard/reads.py` | **The walk.** A hidden part (`_Part.strict`) is walked only for a search or listing whose start is at, in or above its tree (`below`); `_walk` refuses a folder that cannot be stat'ed or walked for any reason but its absence (`os.walk`'s `onerror`). A registered worktree whose folder is missing holds no files and its paths are still refused by glob. (c)'s parts keep today's walk. `listed` reads `below`; a listing fed at run time (`listing`) asks `held()`: a tree's hidden files, or any entry of the runs root. A glob pathspec (`spec`) reads a hidden part's files only for the tree the command runs in. | same |
| 4 | `src/gov/guard/reads.py` | **The git routes.** `git show <rev>:<path>` and `git cat-file … <rev>:<path>`: the path, relative to the root (or the cwd for `./`, `../`), refused when it names a hidden path, whatever the tree. `git -C <tree>`: the cwd moves and that tree's part judges. `--git-dir`/`--work-tree` are carried into the guard's question. The patch routes (`git show <rev>…`, `git show :/<text>`, `git log -p`, `whatchanged -p`, `git diff` in its forms, `format-patch`), when their pathspecs cover the hidden part (none; a glob or magic one; one at or above a glob's literal folder; one inside), are asked of git (`patched`): first `rev-parse --end-of-options <each end>^{commit}` (a revision that is not a commit refuses; `git log` passes over a blob in silence), then `log` (or `diff`) `--no-ext-diff --no-textconv --name-only --no-renames`, `--diff-merges=separate --full-history` (and `--no-walk` for `show`), the options that widen or choose the sides (`--all`, `--branches`, `--tags`, `--remotes`, `--glob`, `-g`, a count, `--cached`/`--staged`, `--merge-base`), `--end-of-options`, the revisions, and the hidden globs as `:(top,glob)` pathspecs; refused when git names a path. `--not` is not carried: what follows it is taken whole, so the question never sees fewer commits than the command. `git grep … <rev>`, `git grep --cached`, `git archive <rev>` (`stored`): `ls-tree -r --full-tree --name-only -z` of the revision matched against the globs (a `<rev>:<folder>` is prefixed), and `ls-files --cached` with the pathspecs. Any answer that cannot be had (an error, a timeout, a word the guard cannot resolve, `--stdin`) refuses with "git cannot say whether a revision holds the hidden part". | same |

The new fail-closed causes, each rendered as today's `PolicyError` refusals ("…: the call is refused (fail closed,
DEC-820)"): "the repository's worktrees cannot be listed", "the runs root cannot be read", "a hidden part's folder
cannot be walked", "the repository's trees cannot be found from this run clone", "git cannot say whether a
revision holds the hidden part". No other message changes.

## 2. Unchanged

- (a) secrets, (b) the held-out material (`heldout.py`), (c) the counterpart's work: judged as before; (c)'s parts
  keep their walk and their patch check (`others.spec`, the hidden parts set aside); `cat-file`, `format-patch` and
  `archive` still go through `reads` first.
- The visible parts; which sessions are measured (`_hidden`); the launcher's `check_sets`; `_git` and its environment
  (W2-05's).
- A session that no set measures: no tree listing, no runs-root listing, no new git call (`hidden` is empty, so
  `patched`, `stored` and `_trees` are never reached).

## 3. Cost

A measured session pays, per guard call, one `git worktree list` and one listing of the runs root (two `worktree
list`s in a run clone); a tree's hidden folders are walked only for a start at, in or above it; the patch question
(two git calls) only on a patch route whose pathspecs cover the hidden part; the tree question only on a `grep`
with a revision or `--cached`, or an `archive`, whose pathspecs cover it.

## 4. Tests

Every run in this worktree with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src` (DEC-732), at `3d7560e8f39f`.

| Suite | Result |
|---|---|
| `tests/acceptance/W2-84` | 329 passed (209 failed, 120 passed before, `6324b0d76e70`) |
| `tests/unit/guard/test_w2_84_trees.py` | 34 passed |
| `tests/unit/guard` | 1103 passed |
| `tests/acceptance/W2-58` | 803 passed; 2 failed, 3 errors, all in `test_w2_58_launched_sessions.py`: live sessions, `api.anthropic.com` refused by the engineer's sandbox (as W2-58's CIT-E §4 records) |
| `tests/acceptance/W2-50` (by file, 13 files) | 636 passed |
| W1-05 `test_a_call_waits_under_100_ms_p95_for_the_hook` | 9 passed (1-minute load 6.81 before, 7.73 after) |

## 5. Residuals (rows, not rounds; DEC-801)

1. **R1.** A hidden blob printed by its object id (`git cat-file -p <id>`, `--batch`): the id must be looked up
   first, a deliberate route (W2-L374's class).
2. **R2.** A link to a hidden folder placed below a search's start and followed by a link-following search
   (`grep -R`, `rg -L`, `find -L`): DEC-801's planted link; the own-tree rule had the same limit.
3. **R3.** `git stash show -p`, `range-diff`, `bundle`, `notes`, raw object files under `.git/objects`.
4. **R4.** A set present in another tree's path map but not in the session's own: the session's own map decides.
5. **R5.** An opaque interpreter that opens a hidden file: W2-L374.
6. **R6.** A clone or copy outside the runs root: not a tree; copying the repository is forbidden to every worker.
7. Over-refusals kept on the fail-closed side: a `git diff` of two trees or blobs (`<rev>:<folder>`), a patch route
   whose operand names a path that no longer exists (taken as a revision git cannot resolve), and any route after
   `--not` taken whole. A run clone's walk counts against the same bound as a tree's: a search from above a runs
   root of many large clones is refused as more than the guard reads in bounded time.
8. Proportion: about 335 lines added and 25 removed in `reads.py` against the estimate of 120; the git question
   (`covers`, `patched`, `stored`, `ask`, about 110 lines) and the run clones' part (about 50) are the bulk.
