# W2-84 acceptance tests: the hidden part refused under every tree

Ticket `DAEO-m1u3` (W2-84, FULL, row W2-H063). Written by the independent test designer (MR-3) from the ticket's KPI
lines, its card (`docs/plan/WAVE_2_WBS.md` §2), its sources (DEC-950 item 1, DEC-820 (d), DEC-821 item 2, DEC-845,
DEC-873, DEC-728, DEC-751, DEC-801, DEC-562, DEC-946 item 3, DEC-880, DEC-866, CAP-33.a) and the lead's design note,
before the implementation exists (`git diff --name-only w2/integrate...HEAD` named no file when they were written).
Existing code was read only as it stands on the base.

**329 cases.** On today's code: **209 red, 120 green**, none skipped (see "Red first" below).

## What the tests drive

One public interface: **the guard**, the kernel's PreToolUse hook `template/governance/kernel/hooks/pretooluse.py`,
committed into the planted repository at `governance/kernel/hooks/pretooluse.py` (so every tree and every clone holds
it) and run as the harness runs it: the call on stdin, `GOV_ROLE`, `GOV_TICKET`, `CLAUDE_PROJECT_DIR` set to the
session's root, and the root as the working folder (W2-58's form). The decision is read from the hook's output
(`permissionDecision: deny` with a reason, or nothing: allowed). No private name of the implementation is used. The
only constants taken from `gov` are where the guard reads the held-out list and its key
(`gov.guard.heldout.CONFIG_REL`, `CONFIG_KEY`), so that the stand-in list is planted where the guard looks.

## The code under test (DEC-732)

Run the suite with this worktree's `src/` set per command:

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -m pytest tests/acceptance/W2-84 -q -p no:cacheprovider -rs

Every child (the guard) gets `PYTHONPATH` from `w2_84_support.python_path()`: the runner's own value, else the `src`
folder of the worktree that holds this suite. `test_w2_84_code_under_test.py` shows which `gov` a child imports.

## What is planted (`w2_84_support.py`)

Everything lives in pytest's temporary folders, under a temporary `HOME` used for every call. **Nothing reads, lists
or plants anything in this repository's `fixtures/evaluation/**/hidden/**` or in the real `~/gov-os-runs/`**: the
runs root the guard sees is `<tmp>/home/gov-os-runs`. No real secret, no real held-out path is named.

**The trees world** (`make_world`, one per module, read-only cases):

| Tree | Path under the temporary HOME | Branch | Holds |
|---|---|---|---|
| main tree | `repo/` | `main` | the hidden part |
| worktree W2-81 | `gov-os-worktrees/W2-81/` | `w2/W2-81` (the engineer's own) | the hidden part and the engineer's acceptance tests |
| worktree W2-82 | `gov-os-worktrees/W2-82/` | `w2/W2-82` | the hidden part |
| clean worktree W2-85 | `gov-os-worktrees/W2-85/` | `w2/W2-85` (removes the hidden part) | neither |
| run clone | `gov-os-runs/W2-83/clone/` | a `git clone` of `repo` | the hidden part |
| deep clone | `gov-os-runs/W2-00/a/b/repo/` | a `git clone` made by hand, no marker | the hidden part |

- The own folder `gov-os-runs/W2-83/` carries the marker `.gov-os-repository`, a regular file naming the real path of
  `repo/.git` (DEC-751 1). `W2-00/` has none.
- The planted path map (the kernel template with an `evaluation_sets` block) declares the set `fixture-questions`:
  visible `eval/memory/visible/**`; hidden `eval/memory/hidden/**` and `eval/memory/answers-*.yaml` (a one-folder
  glob); measured: the role `engineer` and the ticket `DAEO-zz86` (a research ticket).
- The engineer's ticket `DAEO-zz84` (`wbs_id: W2-81`): its acceptance tests `tests/acceptance/W2-81/` are its (c)
  part. They are committed on its own branch only, so that (c) refuses nothing outside W2-81 and a refusal elsewhere
  is (d)'s (on `main` they would make every whole-tree patch and every search above the tree refused by (c), which
  would hide (d)).
- A stand-in `.env` (a), and W2-58's form of stand-in held-out material `held-out-material/` named by a planted
  held-out list (b).
- The links: `peek` in the main tree, W2-81 and the run clone, to W2-82's hidden folder; outside every tree,
  `outside/answers-link` (to W2-82's hidden file), `outside/tree-link` (to W2-82) and `outside/clone-link` (to the run
  clone).

**The store world** (`make_store_world`): no tree holds a hidden file. `main` has the base (no hidden part) and
`unrelated` (changes `docs/notes.md` only); the branch `w2/W2-88` has `hidden` (adds the hidden part) then `after`
(changes `docs/notes.md` only, while its tree still holds the hidden part). The main tree is on `main`, a worktree W2-81
on `w2/W2-81` from `main`. No (c) file is on disk.

**A fresh world** (`fresh_world`, per case) for the cases that change something: a mode, a marker, a file, the path
map, or a stand-in `git` first on `PATH`.

**Stand-ins for git** (`install_git_stand_in`), each a Python script in a folder of its own put first on `PATH`:
`fail` (exits 128 on any call holding the word `worktree`, passes every other call to the real git by its absolute
path), `sleep` (sleeps 12 seconds on `worktree`, past the guard's 5-second git timeout, then answers as the real git,
so that only a guard that times out refuses), `record` (writes every call's arguments to a log of the test's own, then
passes it on).

## The KPI lines and their tests

### Success

1. **A measured session is refused the hidden part under every tree** (by role or by ticket; the main tree, every
   worktree, every run clone; wherever it runs; Read, Grep, Glob, a reading command, a search or listing from above,
   `git -C <tree>`).
   - `test_w2_84_every_tree.py::test_a_measured_engineer_is_refused_every_tree_s_hidden_part`: an engineer rooted in
     the main tree, W2-81 and the run clone × the five trees that hold the hidden part × nine routes (Read of the
     hidden file, Read of the one-folder-glob file, Grep of the hidden folder, Glob `eval/memory/hidden/*` in the tree,
     `cat`, `ls` of the hidden folder, `git -C <tree> show HEAD:<path>`, `git -C <tree> show HEAD:./<path>`,
     `git -C <tree> grep <text>`) = 135.
   - `::test_a_search_or_read_from_a_folder_above_the_trees_is_refused`: rooted in the main tree, W2-81, the run clone
     and the clean worktree W2-85 × from the worktrees' parent, the runs root and the temporary home × `grep -rn`,
     `rg -n`, `find -type f -exec cat {} +`, `find -type f | xargs cat`, `cd <start> && cat <relative path>` = 60.
   - `::test_a_listing_fed_at_run_time_is_refused_while_another_tree_holds_the_hidden_part`: `xargs -a names.txt cat`
     and a `while read` loop fed by a redirect, rooted in W2-85 (design note item 4).
   - `::test_a_session_measured_by_its_ticket_is_refused_every_other_tree_s_hidden_part` (4) and
     `::test_a_session_measured_by_its_ticket_is_refused_a_search_of_the_runs_root` (1): a research session measured by
     its ticket `DAEO-zz86`, rooted in W2-81.
2. **Matched by real path** (links from inside or outside a tree, to a hidden file, a hidden folder or a tree; a tree
   reached by a link or by `..`).
   - `test_w2_84_links.py::test_a_link_or_a_dot_dot_path_is_refused_as_its_target_is`: rooted in the main tree, W2-81
     and the run clone × 15 routes (the inside link: Read, `cat`, `grep -rn`, Grep; the outside file link: Read, `cat`;
     the tree link: Read through it, `grep -rn`, Grep; the clone link: Read through it, `grep -rn`; `..`: Read of an
     absolute path with `..`, `cat` of a relative `..` path, `grep -rn` of W2-82 reached by `..`, Glob in W2-82 reached
     by `..`) = 45.
   - `::test_the_links_lead_where_the_cases_say`: the fixture's own check.
3. **No git route shows a hidden file from another tree or the shared object store.**
   - `test_w2_84_git_store.py::test_a_revision_that_holds_the_hidden_part_is_not_shown`: rooted in the store's main
     tree and its worktree × `git show <hidden>`, `git log -p w2/W2-88`, `git log -p --all`, `git diff <hidden>`,
     `git grep <text> <hidden>`, `git archive <hidden>`, `git cat-file -p <hidden>:<path>`,
     `git show <hidden>:<path>` = 16.
   - The converse, `::test_a_patch_that_shows_no_hidden_path_stays_allowed`: `git show <unrelated>`,
     `git show <after>` (its tree holds the hidden part, its patch does not show it), `git log -p` (HEAD's history),
     `git log -p --all -- eval/memory/visible` = 8. These must stay allowed (design note item 5).
   - `git -C <tree> show` and `grep` across the trees: in `test_w2_84_every_tree.py` (above).
   - `::test_the_store_world_is_as_the_cases_say`: the fixture's own check.
4. **Fail closed.** (`test_w2_84_fails_closed.py`; "with the cause" is checked as today's rendering of a `PolicyError`
   refusal, the words `fail closed`, which the design note keeps for its new causes, item 7; the cause's wording is not
   checked.)
   - `::test_git_that_cannot_list_the_worktrees_refuses_with_the_cause`: stand-in `fail`; Read and `cat` of W2-82's
     hidden files and `grep -rn` from the worktrees' parent, rooted in the main tree.
   - `::test_git_that_times_out_listing_the_worktrees_refuses_with_the_cause`: stand-in `sleep` (the one slow case,
     about 6 seconds).
   - `::test_an_unreadable_runs_root_refuses_every_call_with_the_cause`: the runs root at mode 000; three calls that
     are allowed while it can be read (Read of the own README, `cat docs/notes.md`, Read of W2-82's visible file) are
     then refused (design note item 2: every call).
   - `::test_a_hidden_folder_that_cannot_be_walked_below_a_search_s_start_refuses`: the hidden folder at mode 000 in
     the own tree and in W2-82, the one-folder-glob file removed there; `grep -rn` and Grep from `<tree>/eval/memory`.
   - `::test_a_search_above_a_hidden_part_larger_than_the_bound_is_refused_in_bounded_time`: 10,001 files in W2-82's
     hidden part (today's bound per part is 10,000, DEC-562); refused by the guard, not by the hook's deadline.
   - `::test_a_session_in_a_run_clone_whose_marker_is_faulty_is_refused_every_call` (marker missing, a link, naming no
     git directory) and `::test_a_session_in_a_clone_made_by_hand_with_no_marker_is_refused_every_call`: the
     repository's trees cannot be found from the clone (design note item 3); Read of another tree's hidden file and of
     the clone's own README are refused.
   - Modes are restored at teardown (`modes` fixture), so that pytest can remove the folders.
5. **Nothing else changes** (`test_w2_84_unchanged.py`).
   - Sessions no set measures (an orchestrator, an independent auditor, a research session on a ticket no set
     measures) read every tree's hidden part: `::test_a_session_no_set_measures_reads_every_tree_s_hidden_part` (15),
     `::test_a_session_no_set_measures_searches_from_above_every_tree` (3),
     `::test_a_session_no_set_measures_reads_the_store_s_hidden_revision` (1).
   - The visible part stays readable: `::test_the_visible_part_stays_readable_to_the_measured_session` (15).
   - (a): `::test_a_secret_stays_refused_in_every_tree`; (b): `::test_the_held_out_names_stay_readable_and_their_contents_refused`
     (the planted list readable, the stand-in material refused); (c):
     `::test_the_engineer_s_own_acceptance_tests_stay_refused_and_runnable` (refused to read, allowed to run with
     pytest).
   - No new git call: `::test_a_session_no_set_measures_runs_no_new_git_call` (stand-in `record`; no `git worktree`
     call, and the same git calls as for the same calls once the path map's block is taken out: today the guard
     already runs `git rev-parse --git-common-dir` on every call, which is not new).
   - The design note's item 6: `::test_a_measured_session_lists_the_worktrees_at_most_once_per_call` (also with a
     measured subagent type).
   - Not here, by design: the hook's latency case (W1-05), W2-58's and W2-50's acceptance tests, the existing
     `tests/unit/guard` and the close's full regression are their own suites; KPI 5 asks that they stay green.
6. **The CIT-E** (`docs/changes/W2-84-CIT-E.md`): a document, judged by the review, not by a test here.

### Failure

| KPI failure line | Tests |
|---|---|
| A measured session reads, lists or searches a hidden file of any tree: the main tree, a worktree, a run clone, or through a link into one | `test_w2_84_every_tree.py` (all), `test_w2_84_links.py` (all) |
| A tree or a folder that cannot be listed or walked treated as holding no hidden part | `test_w2_84_fails_closed.py` (all) |
| A git route that shows a hidden file's content from another tree or from the shared object store | `test_w2_84_git_store.py::test_a_revision_that_holds_the_hidden_part_is_not_shown`, the `git -C` routes of `test_w2_84_every_tree.py` |
| Any of (a) to (c) weakened, or a refusal added for a session that no set measures | `test_w2_84_unchanged.py` (all), and the converse in `test_w2_84_git_store.py` |
| A test that reads, writes or plants anything in the real `fixtures/evaluation/**/hidden/**` or the real `~/gov-os-runs/` | the whole suite by construction: every path is under pytest's temporary folder and the temporary `HOME` |

## Red first: the expected result on today's code

**The red reason, for every red case: the guard allows the call** (`decision=allow`, no reason). Today the hidden part
is one part rooted at the session's own root: a path in another tree or a clone is never in it, a search is judged only
by the own tree's hidden files, the git routes are judged against the own tree's files on disk, and an unreadable folder
is passed over by `os.walk`. The failure message of each red case reads `... was not refused: decision=allow exit=0
reason=''`.

| Group | Red | Why red today |
|---|---|---|
| every tree × route, another tree as target | 96 | the path lies outside the own root: allowed |
| from above, start not above the own tree's hidden part | 40 | today the search is judged by the own tree's hidden files only |
| run-time listing, rooted in W2-85 | 1 | the own tree holds no file of a part, so the listing is not judged |
| measured by ticket | 5 | as the engineer's |
| links and `..` to W2-82 or to the run clone | 43 | the real path lies outside the own root |
| git store, a revision holding the hidden part | 14 | the trees hold no hidden file on disk, so the patch, grep, archive and cat-file routes find nothing to refuse |
| fail closed | 10 (the bound case included) | the guard does not list the trees, does not read the runs root, nor walk another tree; `os.walk` passes over an unreadable folder |

That is 209 red.

**Green before the fix (120), and why:**

- **The own tree's hidden part** (27 in `test_a_measured_engineer_is_refused_every_tree_s_hidden_part`, target = the
  session's own tree): today's rule already refuses it.
- **`git -C <tree> show HEAD:<path>` for every other tree** (12): today the path of `<rev>:<path>` is judged relative
  to the session's own root, where it names the hidden part, whatever tree `-C` names. The `HEAD:./<path>` form, judged
  today relative to the folder `-C` moves to, is red.
- **A search from a folder above the session's own tree** (20: rooted in the main tree from the home; in W2-81 from the
  worktrees' parent and the home; in the run clone from the runs root and the home; four commands each): today the own
  tree's hidden files below the start refuse it. The `cd && cat` form aims at another tree's file and is red; and every
  start is red rooted in the clean worktree W2-85, which holds no hidden file.
- **The run clone's link to itself** (2 in `test_w2_84_links.py`, rooted in the run clone, `clone-link`): its target is
  the session's own tree.
- **`git show <hidden>:<path>` in the store** (2): judged today relative to the own root, as above.
- **The converse** (8): those patches show no hidden path and are allowed today; they must stay allowed.
- **The fixture checks** (2: the links, the store world) and the code under test (1).
- **Every case of `test_w2_84_unchanged.py`** (46): (a), (b), (c), the visible part, the unmeasured sessions and the
  git calls are as before; they must stay green. `test_a_measured_session_lists_the_worktrees_at_most_once_per_call`
  is green today because today's guard lists no worktree.

## Residuals named, not tested as refused (the design note's item 8)

- **R1.** A hidden blob printed by its object id (`git cat-file -p <blob id>`, `git cat-file --batch`): the id must be
  looked up first and printed by hand, a deliberate route (W2-L374's class). No case asks for its refusal.
- **R2.** A link to a hidden folder placed below a search's start and followed by a link-following search
  (`grep -R`, `rg -L`, `find -L`): DEC-801's planted link. The link cases here aim at the link itself or start the
  search at the link.
- **R3.** `git stash show -p`, `range-diff`, `bundle`, `notes`, raw object files under `.git/objects`.
- **R4.** A set present in another tree's path map but not in the session's own: the session's own map decides.
- **R5.** An opaque interpreter that opens a hidden file (W2-L374).
- **R6.** A clone or copy outside the runs root.

Also not tested: a registered worktree whose folder is missing (design note item 1), the runs root's own walk bound
(its number is not stated), and the runs root reached through a linked `HOME`.

## Running

- Run in the foreground, one process; nothing is marked serial. The suite takes about five minutes (about 0.4 s per
  guard call); the timeout case waits about 6 seconds.
- Module names start with `w2_84_` or `test_w2_84_`, so the suite collects with the rest of `tests/` in one process
  (DEC-868).
- The temporary folders are pytest's own (no `--basetemp`); the fixtures' worlds take a few megabytes each, and the
  bound case writes 10,001 small files in its own temporary folder.
