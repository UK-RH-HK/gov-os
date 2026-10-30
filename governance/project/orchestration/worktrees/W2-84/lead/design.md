# W2-84 design note: the hidden part refused under every tree (DEC-950 item 1, row W2-H063)

The lead's plan, in behaviour. "Measured" means a session that an evaluation set in its own tree's path map measures, by its role or by any name its ticket goes by, exactly as today. Every refusal below concerns a measured session only.

**1. The trees.**
- The trees of the repository are the main tree and every registered worktree. They are listed with `git worktree list` (porcelain form), run by the guard's existing git runner, with its 5-second timeout and its environment as they stand. Each tree is taken by its real path.
- A registered worktree whose folder is missing is still a tree. Its paths are refused by glob, and it holds no files to walk. If the folder is made again, its files are walked like any other tree's.
- A project with no `.git` entry at its root is not a repository. Its only tree is its own root (plus the runs root, below), as today.
- When the trees cannot be listed (`git worktree list` fails or times out), every call of the measured session is refused with the cause, as a malformed set refuses them today (KPI 4's words).

**2. The run clones.**
- A path is in a hidden part when it lies under the runs root and the hidden globs match it relative to **any** folder below the runs root, at any depth. The runs root is `gov.guard.runs.root()` in the session's home, taken both as named and by its real path.
- **Why not the marker.** The `.gov-os-repository` marker is written only into own folders made by a launch. It names the repository that made the folder, not the clone inside it. A clone can sit at any depth (`~/gov-os-runs/W2-61/clone/`, `~/gov-os-runs/W2-00/a/b/repo/`), and a folder made by hand has no marker at all. Matching at any depth is the stricter rule: it refuses every copy of a hidden path under the runs root, whatever the clone's layout.
- When the runs root exists, it is listed once per call. If it cannot be listed (for any reason but its absence), every call is refused with that cause.

**3. A session that runs in a run clone.** Its root lies under the runs root. Its trees are:
- its own (the clone's `git worktree list`);
- the runs root, matched at any depth, which already covers its own clone and every other clone;
- the repository's trees. These are found from the marker of the own folder that holds the clone (the folder directly below the runs root). The marker must be a regular file, not a link, naming a git common directory. That repository's trees are listed with `git worktree list` run against the directory it names.

If the marker is missing, unreadable or names no git directory, or that listing fails, every call is refused with the cause. It is never "allowed".

**4. The part.**
- There is one hidden part per tree, with the same globs and the same refusal text (`HIDDEN_REFUSAL`), plus the runs root's any-depth part.
- **When a tree is walked.** A tree's files are walked only for a search or listing whose start is at, in or above that tree. The walk takes the globs' literal folders, as today, within the existing bound (per tree).
- **The runs root.** It is walked below the search's start, or whole when the start lies above it, never into `.git`. The walk is bounded: a walk that passes the bound refuses, with "more than the guard reads in bounded time".
- **Failure.** A folder that cannot be walked or stat'ed for any reason but its absence refuses the call. It is never passed over (today `os.walk` passes over it in silence). (c)'s parts keep today's walk.
- **A listing fed at run time whose start cannot be placed** (xargs, `while read`) is refused when any tree holds a hidden file or the runs root holds any entry.

**5. The git routes** (the store the worktrees share).
- **`git show <rev>:<path>`, `git cat-file … <rev>:<path>`:** the path is judged as it is today (relative to the root, or to the cwd for `./` and `../`). It is refused when it names a hidden path, whatever the tree.
- **`git -C <tree> …`:** the cwd moves to that tree, and its paths and pathspecs are judged against that tree's part.
- **The patch routes:** `git show <rev>…`, `git log -p` and `whatchanged -p`, `git diff [<rev> [<rev>]]` (also `--cached`, `--merge-base`, ranges) and `format-patch`. Each is judged when its pathspecs cover the hidden part, which means any of:
  - no pathspec;
  - a pathspec at or above a hidden glob's literal folder;
  - a pathspec inside the hidden part;
  - a glob or magic pathspec.

  The guard then asks git, in a fixed read-only form of its own, whether the patch would show a hidden path. The form names only the changed paths, filtered by the hidden globs as `:(top,glob)` pathspecs. It carries no external diff, no textconv, no `-c` and `--end-of-options` before the revisions. It runs against the repository and tree the command addresses (its `-C`, `--git-dir`, `--work-tree`), with the command's revisions and the options that widen or choose the sides (`--all`, `--branches`, `--tags`, `--remotes`, `--glob`, `-g`/`--reflog`, `--not`, a count, `--cached`/`--staged`, `--merge-base`). Merges are taken parent by parent.
  - **Refused** when git names a hidden path, when its answer cannot be had (an error, a timeout, a word the guard cannot resolve), or when a revision is not a commit (`git show <blob id>`).
  - **Allowed** when the patch shows no hidden path, so that `git show HEAD` on an unrelated commit stays open.
- **`git grep … <rev>`, `git grep --cached`, `git archive <rev>`:** refused when the revision's tree (or the index) holds a hidden path within the command's pathspecs, again asked of git in a fixed read-only form; an answer that cannot be had refuses.
- **`git worktree list`** shows tree paths, which are names: allowed.

**6. The cost.**
- An unmeasured session runs no new git call and reads nothing new.
- A measured session's trees are listed at most once per guard call (one `git worktree list` and one listing of the runs root), even when its session role and its subagent's role are both measured.
- The patch query runs only on a patch route whose pathspecs cover the hidden part.
- W1-05's bound (the hook under 100 ms at p95; its engineer is measured by the memory set) must hold.

**7. Unchanged.**
- (a), (b) and (c);
- the visible parts;
- which sessions are measured;
- the launcher's `check_sets`;
- `_git`'s environment;
- every message's text, except the new fail-closed causes ("the repository's worktrees cannot be listed", "the runs root cannot be read", "a hidden part's folder cannot be walked", "the repository's trees cannot be found from this run clone", "git cannot say whether a revision holds the hidden part"), each rendered as today's `PolicyError` refusals are.

**8. Residuals** (rows, not rounds; DEC-801):
- **R1.** A hidden blob printed by its object id (`git cat-file -p <id>`, `--batch`). The id must be looked up first and then printed by hand: a deliberate route (W2-L374's class).
- **R2.** A link to a hidden folder placed below a search's start and followed by a link-following search (`grep -R`, `rg -L`, `find -L`): DEC-801's planted link. Today's own-tree rule has the same limit.
- **R3.** `git stash show -p`, `range-diff`, `bundle`, `notes`, raw object files under `.git/objects`: not ordinary routes to hidden content.
- **R4.** A set present in another tree's path map but not in the session's own. The session's own map decides whether it is measured, as today; a set reaches each tree on its next merge of `w2/integrate`.
- **R5.** An opaque interpreter that opens a hidden file: W2-L374.
- **R6.** A clone or copy outside the runs root (`/tmp`, elsewhere). It is not a tree, and copying the repository is forbidden to every worker.
