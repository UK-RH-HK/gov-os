You are the ticket lead for ticket `DAEO-m1u3` (`W2-84`, "The guard refuses an evaluation set's hidden part under every tree of the repository: the main tree, every worktree and the run clones (row W2-H063)"). It is profile FULL, on memory's critical path, and you work only in the worktree `/home/usain/gov-os-worktrees/W2-84` on branch `w2/W2-84`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `d808292d88e1`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-m1u3.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-84");
- DEC-950 (item 1), DEC-820 ((d) above all), DEC-821 (item 2), DEC-845, DEC-873, DEC-728, DEC-801, DEC-562 and DEC-946 (item 3); row W2-H063 in `docs/plan/WAVE_2_LIST.md`;
- the orchestrator's probe, `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/probe_hidden_rooting.py` (paths only: it opens no file);
- `src/gov/guard/reads.py`:
  - `_Part` (lines 131 to 196): `inside`, `files`, `below`;
  - `_git` (265 to 271);
  - `_hidden` and `parts` (360 to 398);
  - `_Judge.spellings`, `at` and `above` (568 to 615);
  - `_Judge.git` and `spec` (910 to 972);
  - `policy_refusal` (1163 to 1192);
- `src/gov/guard/runs.py`'s `root()` and its `MARKER`;
- the path map's `evaluation_sets` block (`governance/project/path-map.yaml`, line 489);
- `tests/acceptance/W2-58/`, for how a case drives the guard's read rule.

## Why you start now

- **The hidden-part refusal reaches only the session's own tree.** `parts()` roots the hidden part at the session's own project root. For a measured engineer, the orchestrator's probe found:
  - its own tree's hidden file: refused;
  - the main tree's copy: allowed;
  - another worktree's copy: allowed;
  - a run clone's copy under `~/gov-os-runs/`: allowed.

  Row W2-H063 records it.
- **Nothing has leaked yet.** W2-61h (`DAEO-h2k3`) is held, so no hidden file exists in any tree. Once its questions merge into `w2/integrate`, every measured session in any worktree could read them by an absolute path. The worktrees also share one object store, so a commit that holds them can be shown from any tree.
- **It blocks EXAMIN's copy.** K9's entry criterion is memory measured with both halves (W2-61). The owner chose (a), this fix now, ahead of W2-61h (DEC-950 item 1; priority 3 of DEC-946).

## The decisions for this run

- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour. It is a plan, not code. It says:
  - **the trees:**
    - the main tree and every registered worktree, from `git worktree list --porcelain` run through the existing `_git` (its timeout, its environment as it stands), each taken by its real path;
    - a registered worktree whose folder is missing is still a tree: its paths are refused by glob, and it holds no files to walk;
  - **the run clones:** how a path under the runs root (`gov.guard.runs.root()`) is matched. Either the hidden globs at any depth below it, or by the `.gov-os-repository` marker. The note chooses one, says why, and says which is stricter. A clone's own layout must not let a hidden file through;
  - **a session that runs in a run clone, not a worktree:** what it is refused, and how the repository's trees are found from there. If they cannot be found, the note says what happens, and it is never "allowed";
  - **the part:** one hidden part per tree, or one part with many roots, with the same refusal text. `files` is walked per tree within the existing bound. A folder that cannot be walked refuses, and is never passed over;
  - **the git routes,** against the object store the worktrees share:
    - `git show <rev>:<path>` (already judged by its path);
    - `git -C <tree>`;
    - a patch of a revision that holds the hidden part while the session's own tree does not (`git show <rev>`, `git log -p`, `git diff <rev>`);
    - `git cat-file` and `git archive`.

    For each, the note says how it is refused, or names it as a residual with its reason (W2-L374's class if only a deliberate evasion reaches it);
  - **the cost:**
    - the lister runs only for a session that a set measures, at most once per guard call;
    - a session that no set measures runs no new git call;
    - W1-05's latency bound (the hook under 100 ms at p95) holds;
  - **nothing else changes:** (a), (b) and (c), the visible parts, the launcher's `check_sets`, and every message's text but the new causes.

  It goes into the test designer's and the reviewer's briefs as text.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`, a measured trial for FULL test designers, DEC-839; its brief must not set `TMPDIR`), in `tests/acceptance/W2-84/`.
  - **Everything planted.** The repository, its two worktrees, a run clone under a temporary `~/gov-os-runs/` and a planted evaluation set (in the planted repository's own path map, measuring the engineer) all live in temporary folders, under a temporary `HOME` for every call. **Nothing reads, lists or plants anything in this repository's `fixtures/evaluation/**/hidden/**` or the real `~/gov-os-runs/`.**
  - **Sessions:** a measured engineer with the main tree as its root, and with a worktree as its root. Each is refused every other tree's hidden file, by:
    - Read, Grep and Glob;
    - `cat`, `grep -r` and `rg` from a folder above (the worktrees' parent, the runs root, the temporary home);
    - `find` with an action that opens files;
    - `git -C <tree> show` and `grep`.
  - **The symbolic-link route:** a link inside the session's own tree to another tree's hidden folder, a link outside every tree to a hidden file, and a link to a whole tree. Each is refused as its target is.
  - **The git route:** a commit on another branch holds the hidden part while the session's own tree does not. Every patch route in the design note is refused, or is the named residual.
  - **Fail closed:**
    - git that cannot list the worktrees (a planted failure, and a timeout);
    - an unreadable runs root;
    - an unreadable hidden folder below a search's start.

    Each refuses, and none is taken as empty.
  - **Unchanged:**
    - a session of a role no set measures (the orchestrator, an auditor) reads every tree's hidden file;
    - the visible part stays readable to the measured session;
    - (a) to (c) as before;
    - a session no set measures runs no `git worktree` call (shown by behaviour: a planted `git` on `PATH` that records its calls).
  - The cases drive the guard as W2-58's acceptance cases do.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in the allowed paths:
  - `src/gov/guard/reads.py`: the hidden part, the tree lister and the git route only;
  - new files `tests/unit/guard/test_w2_84*`;
  - `docs/changes/W2-84-CIT-E.md`, in W2-58's form: the change the owner approved under CAP-33 (DEC-950 item 1).

  The engineer is itself measured by the memory set: its own guard refuses it the real hidden folder. Its unit tests also plant everything, as above.
- **Fail closed:**
  - a tree list, a walk or a git answer that cannot be had refuses;
  - nothing falls back to the session's own tree alone;
  - no error is passed over in silence.
- **Running beside you:**
  - **W2-05** (`DAEO-0z8c`) holds `src/gov/**/*.py` for the git environment of git calls. Leave how `_git` builds its environment as it stands. Its sweep may touch `_git` later: a line overlap, and whichever merges second merges back.
  - **W2-67** (`DAEO-9nys`) holds `tests/unit/guard/**`. Write only new `test_w2_84*` files there, and edit no existing file (`test_reads.py` included).
  - **W2-60a and W2-56** hold `src/gov/launch/launcher.py`, `role.py`, `record.py`, `sandbox.py` and `environ.py`.
  - **W2-61** holds `src/gov/retrieval/measure.py` and `fixtures/evaluation/memory-retrieval/visible/**`.
  - **W2-61h** waits on you. Nobody writes under `fixtures/evaluation/`.
  - **The path map** is the orchestrator's. Nobody here writes it.

  Do not touch their files. If your design needs a change there, or the git routes need more than this ticket's size, return PACKAGES with the cost.
- **Verification:** in full, in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no full run. Wait, and go on the moment it is gone.
  - **Closes:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no worker and no suite.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
  - **Locks:** every full run goes under `flock /tmp/gov-os-verify.lock`, and every rebuild under `flock /tmp/gov-os-rebuild.lock` (DEC-939 item 2).
  - **Look hardest at:**
    - `tests/acceptance/W2-58/`, `tests/acceptance/W2-50/` and `tests/unit/guard/`;
    - W1-05's latency case (`test_a_call_waits_under_100_ms_p95_for_the_hook`), run alone at a 1-minute load under 5 if it is red under load.
  - **Known:**
    - W1-42's accepted reds;
    - the load-sensitive cases, re-run alone;
    - W2-54's green-here cases may time out under load (row W2-L429), so re-run them alone;
    - W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **Reviews: one (the ticket).** A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head, given the design note. **A fault here leaks the measure's answers.**
  - **The probe asks above all whether any route lets a measured session read a hidden part in any tree:**
    - the main tree, a worktree, a missing worktree's folder recreated, a run clone, and a session that runs in a run clone;
    - a link, a `..` spelling, a bind of the home folder (`~`, `$HOME`, `/proc/self/cwd`);
    - a search or listing from above any tree, with and without a glob;
    - the shared object store: `git show <rev>`, `git log -p`, `git diff <rev>`, `git cat-file`, `git archive`, `git -C <tree>`, `git worktree list` itself;
    - a tree list or a walk that fails, times out or is too large;
    - a role or ticket measured by name (the ticket's id, file name or WBS id).
  - **And the converse:** no refusal is added for a session no set measures, and (a) to (c) are unchanged.
  - The reviewer uses planted sets only. Nobody reads the real `fixtures/evaluation/**/hidden/**` in any tree.
  - **A finding that shows one of the ticket's failure lines fails the review.** Those lines are a hidden file of any tree read, an unlistable tree taken as empty, a git route left open, and (a) to (c) weakened. Commit the probe record only when it passes. If it fails on such a finding: one test-design batch, one engineer, a full run, and a second, last review (DEC-413). In that batch, a fresh test designer is given the finding as a described behaviour (DEC-136).

## This run's order

1. The design note (yours, in scratch).
2. Tests first (the test designer), then **check red yourself.** Every case that shows another tree's hidden file is red on today's code, and none is skipped. A case green before the fix cannot fail, and is a finding.
3. The engineer, with the CIT-E.
4. Rebuild and verify in full.
5. The review.
6. **Return** DONE or PACKAGES.
   - DONE means the probe passed and the branch is ready to merge. It then goes into the next re-pin, and W2-61h's auditor starts after that.
   - Name every residual route the design note left, with its reason, for the list.

**Estimate:** about 120 lines, about a lead-day with the full run and one review:
- the design note and the tests, about 2 hours;
- the engineer, one 90-minute budget;
- the full run, about 95 minutes;
- the review and the return.

If your session nears its end first, write your checkpoint and return PACKAGES naming what is left; a fresh lead resumes from the checkpoint.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
