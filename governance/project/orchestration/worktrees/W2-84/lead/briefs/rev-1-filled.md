You are a fresh reviewer. Ticket DAEO-m1u3 (W2-84), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-84` on branch `w2/W2-84`, at the head `02636753062d`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing. **A fault here leaks the measure's answers.**

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-m1u3','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (name any file you made outside this worktree; delete nothing).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-m1u3`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-84` and `w2/W2-84`), and check that `git rev-parse --short=12 HEAD` is `02636753062d`. If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase or tag.
- **Policy 2 (DEC-820):** reviewers read everything, tests and code alike, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) does not bind a reviewer; **(d) nobody in this ticket reads, lists, searches or plants anything in this repository's real `fixtures/evaluation/**/hidden/**`, in any tree, or in the real `~/gov-os-runs/`. You probe with planted sets only:** a repository you build from scratch in your temporary folder, with its own path map and evaluation set, its worktrees and a planted runs root under a temporary `HOME`, and you ask the guard about calls the way the acceptance tests do (`tests/acceptance/W2-84/w2_84_support.py` shows how; reuse it by import if it helps).
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`. Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path. Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; never list or read it.
- **Memory used (DEC-836, DEC-860, DEC-859):** before reading files at random, use `gov retrieve` for what you need to know: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question goes in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **No copy of this repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A probe that needs a repository builds a temporary one in your temporary folder; worktrees and clones of that planted repository are fine.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **What is under review, and the hook you run under (ACT 1, DEC-953, DEC-954, DEC-958):** you judge the product's guard, `src/gov/guard/` (the code this ticket changed), by asking it about planted calls. This repository's own hook, which guards your session, is now the five-rule hook; it is not under review, and command forms are no longer refused by it. A probe script goes in your temporary folder (the sandbox's `TMPDIR`), written with plain shell tools if you have no Write tool (`printf` into a literal path in your temp folder), or run as `python3 -` fed from a file. Any refusal by the hook you meet goes in your return, one line each: the time, the command's form (no secret or file contents), the reason it gave, whether it was a true refusal or a false positive, and the minutes it cost. A true refusal is taken; a false positive is worked round only by an equivalent form that does the same thing.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite. The lead has run the acceptance tests and the scoped selection on this head (results below); you read the tests and the code, and you probe with planted sets.
- **Hashes (row W2-L423's rule, DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token. (In your returned probe record, `probed_commit` is the full id: the lead writes it under `docs/probes/`, not under `.gov-runtime/`.)
- **Disk and temp (DEC-898):** your share of the lead's budget is 2 GB and 100,000 files and folders; keep the sandbox's temp folder; remove what you made as soon as it is no longer needed; give your temp folder's size in your return.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try.**
- You never ask or notify the owner.

## The judgement rules (`governance/project/briefs/JUDGEMENT.md`, word for word)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

## What you read

- The ticket file `.tickets/DAEO-m1u3.md`: its KPI lines (success and failure) and its `allowed_paths` (`src/gov/guard/reads.py`, `tests/unit/guard/test_w2_84*`, `docs/changes/W2-84-CIT-E.md`).
- Row W2-H063 in `docs/plan/WAVE_2_LIST.md`; the card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-84").
- The decisions in `docs/DECISION_REGISTER.md`: DEC-950 (item 1), DEC-820, DEC-821 (item 2), DEC-845, DEC-873, DEC-728, DEC-751, DEC-801, DEC-562, DEC-946 (item 3), DEC-880, DEC-866; CAP-33.a; ADR-0001 (`docs/adr/ADR-0001-threat-model.md`).
- The change: `git diff w2/integrate...HEAD` (the code, the builder tests, the CIT-E), and the acceptance tests `tests/acceptance/W2-84/` with their README.
- The lead's design note, word for word:

---
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
---

## The lead's results on this head

- The fix is the engineer's commits 3d7560e8f39f and c0f35c87fd8a. Since then the branch took three merges of `w2/integrate` (217 files, none under `src/gov/guard/`, `tests/unit/guard/` or `tests/acceptance/W2-84/`) and the lead's checkpoint records; the guard's code at this head is the code at c0f35c87fd8a.
- This repository's own hook is the five-rule hook (ACT 1); it is not under review.
- The lead's runs on this code: acceptance W2-84 plus `tests/unit/guard/test_w2_84_trees.py`, 363 passed (this run, on this head's code); run 1's full parallel phase on c0f35c87fd8a, 16902 passed, 1 failed (W2-66's known DEC-919 red), 31 skipped. The scoped selection (`select_tests.py`: scope `scoped`, core changed `src/gov/guard/reads.py`) runs beside your review; you re-run none of it.

## What you probe for

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

**Above all: does any route let a measured session read a hidden part in any tree?**
- **Where the hidden file lies:** the main tree; a worktree; a registered worktree whose folder was removed and then made again; a run clone (at any depth under the runs root); and the same for a session that itself runs in a run clone.
- **How the path is spelled:** a symbolic link (inside a tree, outside every tree, to a whole tree), a `..` spelling, and a bind of the home folder (`~`, `$HOME`, `/proc/self/cwd`).
- **Searches and listings from above any tree,** with and without a glob: Grep, Glob, `grep -r`, `rg`, `find … -exec`, `ls -R`, and runtime listings such as `find | xargs cat`.
- **The shared object store:** `git show <rev>`, `git log -p` (with and without `--all`), `git diff <rev>`, `git cat-file`, `git archive`, `git grep <text> <rev>`, `git -C <tree> …`, and `git worktree list` itself, where a commit on another branch holds the hidden part while the session's own tree does not.
- **A tree list or a walk that fails, times out or is too large:** a `git` that fails or sleeps on `worktree`; an unreadable runs root; an unreadable hidden folder or parent folder; a walk past the bound. Each must refuse; none may be taken as empty.
- **Who is measured:** a role, and a ticket measured by its id, its file name or its WBS id; a subagent whose type is a measured role.

**And the converse:**
- no refusal is added for a session that no set measures (the orchestrator, an auditor, an unmeasured engineer), and such a session runs no new git call;
- (a) secrets, (b) the held-out names and contents, and (c) the counterpart's work are judged exactly as before;
- the visible part stays readable;
- ordinary git use by a measured session (`git show` or `git log -p` of a commit that touches no hidden path, `git diff` in its own tree) stays open;
- the hook's latency stays within W1-05's bound (look, do not run the whole W1-05 suite).

**The ticket's failure lines.** A finding that shows one of these fails the review:
- a hidden file of any tree read, listed or searched by a measured session;
- an unlistable tree, or an unwalkable folder, taken as empty;
- a git route left open that shows a hidden file's content from another tree or the shared store;
- (a) to (c) weakened, or a refusal added for an unmeasured session.

Judge each against the residuals the design note names (R1 to R6): a route the note names as a residual, reached only as it says, is a row, not a failure. Say whether you agree with each residual's classification.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Say also what you probed and found sound.

Then the probe record's body, ready for the lead to commit under `docs/probes/DAEO-m1u3/`. It is Markdown, with sections Summary, What was probed and found sound, Findings (each with its two lines) and Residuals. Your judgement goes on one line: `judgement: pass` or `judgement: fail`. It is pass unless a finding is "Ordinary work: yes" with "fails open" or "loses work". The lead writes the front matter.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Right after the twelve fields, a section headed `guard_refusals:`, one line per refusal by the hook that you met, or `guard_refusals: none`; then the guard's read refusals (DEC-849) by count, and whether you used `gov retrieve`.

Refused twice for the same call: stop and say so.
