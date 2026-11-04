# ACT-G14: role separation from the path map (DEC-1052 G-14; DAEO-sdxk, W2-00)

Drafted 2026-11-03 by the CTO's emergency engineer (session 33b3628c). Revised the same day for review round 2
(`reviews/g14.md`):
- F1 is fixed;
- F2, F8, F3's note, F9 and F10 ride along;
- F4 is decided by the owner: `docs/` stays on the test designer's no-read list, as built;
- the owner's engineer rule (2026-11-03, relayed by the CTO) is built in.

Nothing in it is live until the owner's operator runs §3.

**Basis (DEC-1052):** it passes Q1, Q2, Q3 and Q4.
- Q1: it serves role separation.
- Q2: without it, an engineer can read its own ticket's acceptance tests and fit code to them, and a test designer can
  read the engineer's new code. Ordinary work then fails open on separation.
- Q3: it runs only on Read, Grep and Bash calls, and refuses only for the roles the section names. It costs about
  6–8 ms per call; git is consulted only when an engineer reads another folder's acceptance tests.
- Q4: it adds no record, approval or ping.
- Q5 does not apply: this is the project's own hook. The product's template guard is unchanged.

## 1. What it does
The guard gains one more check, `.claude/hooks/role_reads.py`, called from `main()` after rule 2's read judge. It
judges both the session's role and the acting role. It reads a new block of the **main tree's**
`governance/project/path-map.yaml` (so a branch cannot weaken it):

```yaml
role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
  independent-test-designer:
    reads_denied: ["{ticket_impl}"]
```

**What is refused.** A call is refused when a path it reads, as the call names it, is at or under a denied path.
- The tools: Read, NotebookRead, Grep (its `path`, and its `glob`'s literal lead).
- In Bash, the readers' operands. The readers are `cat`, `head`, `tail`, `sed`, `awk`, `grep`/`rg`, `jq`, `diff`,
  `cp` sources, a `<` redirect, `find -exec cat`, and `git show`/`diff`/`blame`/`grep`/`log -p` with `rev:path`,
  `-- path` or an existing path.
- The scan follows `cd`, the variables the command sets itself, `bash -c` strings and `$(…)` bodies.
- The refusal names the rule, for example `the engineer does not read {ticket_tests} (tests/acceptance/W2-126/**):
  role_paths.engineer.reads_denied (governance/project/path-map.yaml, DEC-1052 G-14)`.

**What is let through,** as rules 1 and 5 since ACT-GUARD-FIX-4 (no shell guessing):
- a target the guard cannot resolve;
- a search from a folder above, such as `grep -r x tests/acceptance`;
- names only: Glob, `ls`, `find` without `-exec`, `wc`, `--stat`/`--name-only`, `git log` without a patch;
- names a command gets at run time (`xargs`);
- inline code (`python3 -c`);
- a command the scan cannot read.

**Section states.**
- No section: no check, which is today's behaviour.
- Only the `role_paths:` block is parsed, from its key to the next line at the margin, as `evaluation_sets()` parses
  its own block (review F2). A YAML error elsewhere in the map, such as a merge's conflict markers, refuses nothing.
- A malformed block (bad YAML, wrong shapes, or the key written twice, as in a conflict inside the block) fails closed
  for every Read, Grep and Bash call, as a malformed `evaluation_sets` does. §3 checks the block before the hook goes
  live.

### The engineer: `{ticket_tests}`, the owner's rule (2026-11-03)
An engineer is refused **its own ticket's acceptance tests, wherever they sit**. Other tickets' acceptance tests stay
readable, for regressions. The session's ticket comes from `GOV_TICKET` (its id, file name and WBS id, as rule 2 reads
it). Two parts are refused, in every tree: the main tree, the worktrees, the run clones and each folder under
`~/gov-os-worktrees/`.

1. **Its own folder:** `tests/acceptance/<WBS>/**`.
2. **Its cases in other folders:** each file in another ticket's folder `tests/acceptance/<X>/` that a test designer's
   commit made for this ticket touched. The check finds them in the git history of the main tree's repository (every
   branch, merges left out) from two records:
   - **(i) the commit's `Task:` trailer.** A non-merge commit with `Role: independent-test-designer` whose `Task:`
     names the ticket (its id or WBS id) and that touches `tests/acceptance/<X>/`. Every commit carries these trailers
     by the project's rule (DEC-182). Example: W2-126's revision of W2-123's retry case, 741f9edd, `Task: DAEO-jpr0`,
     `Rewrite-Reason: P-W2-123-4`.
   - **(ii) the ticket's tests branch.** A test designer's non-merge commit on the first-parent line of `w2/<WBS>-tests`
     since that branch left `w2/integrate`. The fork point is the first commit on the branch's first-parent line that
     is also on `w2/integrate`'s first-parent line. It is read from the commit graph, not the reflog, because ACT-D8
     expired every reflog on 2026-11-03 (`git reflog expire --expire=now --all`). The project merges with `--no-ff`,
     so a branch's own commits are never on integrate's first-parent line. This catches a revision made in the
     ticket's own tests tree under another ticket's `Task:`.
     - The known case is W2-54's cases revised for W2-126: 0922aa76 and 816e86dd, trailered `Task: DAEO-0rfi` (W2-54's
       ticket), made on `w2/W2-126-tests`. They touch `tests/acceptance/W2-54/{README.md, conftest.py,
       test_w2_54_cpu_embedder.py, test_w2_54_query_cache.py, test_w2_54_query_vector.py, w2_54_support.py}`.
   - Only files inside a ticket folder count, never `tests/acceptance/conftest.py` or `serial-only.txt` at the root.
   - The ticket's own folder is part 1.
3. **When git is consulted:** only when an engineer reads a path in another ticket's acceptance folder.
   - The list is worked out once per (the method, the repository, the ticket, the heads of `w2/integrate`, `w2/<WBS>`
     and `w2/<WBS>-tests`). The method is `role_reads.py`'s own sha256: a changed rule never reads a list an older rule
     cached, which the rehearsal of 2026-11-03 caught (R2-F12). A new
     commit on any of them makes a new list.
   - It is kept as JSON in the session's own temporary folder (`$TMPDIR/gov-os-role-reads-<uid>/`).
   - On a miss: a `git log --all --grep` and a first-parent log, about 50 ms. On a hit: three `rev-parse` calls, about
     3 ms.
4. **When git cannot say** (an error or timeout): the check falls back to the ticket's own folder, never to allowing
   everything. A refusal then says so: `…; its cases revised in other folders could not be worked out from git, so
   only its own folder is judged`.

Today, W2-126's engineer (DAEO-jpr0) has these files in other folders:

| Folder | Files | Found by |
|---|---|---|
| `tests/acceptance/W2-123/` | 2 | (i) |
| `tests/acceptance/W2-54/` | 6 | (ii) |

W2-91's engineer has 1 (W2-86's case, a31d314e, by (i)). W2-04's has 8 (W2-54's and W1-41's cases, by (i)).

**Completeness: what it finds, and what it misses.**
- I tabulated every test designer's commit that touches another ticket's acceptance folder: 598 designer commits,
  303 (folder, commit) pairs.
- Every revision whose `Task:` names the ticket it was made for is found by (i), by construction.
- The only revisions in the history whose `Task:` names the folder's own ticket although they were made for another
  are W2-126's two of W2-54. (ii) finds them while `w2/W2-126-tests` exists. Its fork point from the graph,
  `d72e8dbe4d96`, is the one its reflog named before ACT-D8 emptied it.
- The other candidates were checked and are not misses:
  - 31186ebf (W2-54's cases revised to DEC-1033, a decision, reached by merges);
  - 49f1f81e (W2-54's own run);
  - 9e603f70 and e66ca851 (the CTO's revisions under DAEO-sdxk, so they go with W2-00).
- **Misses, by design:**
  - a mis-trailered revision made outside the ticket's tests branch;
  - one whose tests branch is gone;
  - one merged into `w2/integrate` by fast-forward, which is not the project's practice.
  - The landing's trailer check (G-1) is the backstop: the D-5 templates should require `Task: <the ticket it is
    for>` on a revision.
- **Over-inclusion, at the file level:**
  - a revised file is refused whole, its unrevised cases too;
  - a designer's fixture repair for the ticket in another folder counts as the ticket's (W2-54's list holds 20 files
    in W1-19 … W1-22, from its DEC-798 revisions).
  - Both lean towards separation. The replay shows no false refusal from them (§2).
- **The coordination ticket W2-00 (DAEO-sdxk):** the CTO's revisions link 4 files to it (`W2-54/README.md`,
  `test_w2_54_time_limit.py`, `W2-66/README.md`, `test_w2_66_live_test_map.py`). The CTO's emergency engineers are
  refused those 4 and read every other acceptance test.
- **Not as the coordinator phrased it:** the brief asked for "a W2-54-style revised case readable to W2-54's
  engineer". Under the owner's rule it is not readable: the file sits in `tests/acceptance/W2-54/`, W2-54's own folder.
  The planted cases pin that, and a third ticket's engineer reads it.

### The test designer: `{ticket_impl}`, the owner's decision (c3), as DEC-1054
The decision was taken by the owner on 2026-11-03, as relayed by the CTO. It covers the ticket's `allowed_paths` but
`tests/acceptance/`: its code, its documents and its new unit tests. Shared test files stay readable: any
`conftest.py`, `__init__.py`, `*support*.py` and `*helper*.py`.

The paths count in three places:
- the engineer's tree `~/gov-os-worktrees/<WBS>`;
- its branch (`git show w2/<WBS>:path`, `git diff … w2/<WBS> -- path`);
- the designer's `<WBS>-tests` tree, for the files the engineer's commits carried in.

Every other tree holds the integrated code, which the designer reads (DEC-963): the main tree and the `W2-00-store`
trees. So does `git show w2/integrate:path`.

- **The designer's tests tree (review F1).** The lead brief forks `~/gov-os-worktrees/<WBS>-tests` from the ticket
  branch's head, so in a revision round it carries the engineer's commits. There the ticket's paths name only the
  files those commits carried in: git's name list of the commits reachable from the tree's fork point with `w2/<WBS>`
  but not from its merge base with `w2/integrate`. The designer's own commits after the fork are not among them; with
  no `w2/<WBS>` ref, every commit since the merge base counts. The designer's own `tests/acceptance/<WBS>/` files are
  never refused to it. Today, in W2-91-tests, the rule names exactly `governance/project/path-map.yaml`,
  `tests/unit/retrieval/test_w2_91_full_embeddings.py` and `docs/changes/W2-91-evidence.md`.
- **A designer in the engineer's own tree** (the layout until about W2-104): only the files that branch changes
  against `w2/integrate` count, whether committed, uncommitted or new.
- **When git cannot say:** the read is let through.

## 2. The evidence
**The replay.** Every real transcript was replayed: the 93 worktree folders `-home-usain-gov-os-worktrees-W2-*` and
the main tree's, with their subagents. Only the tool calls' inputs were read, never a result or a file's contents. The
calls judged: 8,228 engineer calls and 9,015 test-designer calls. The full counts are in `replay-counts.json`.

Each variant's link files are counted from their linking commit's time on.

| Variant | Would-be refusals | Sessions | Honest | False |
|---|---|---|---|---|
| **(d) engineer `{ticket_tests}`, the owner's rule (in the patch)** | **178** | **35** | **178** | **0** |
| (b) engineer, its own folder only | 173 | 35 | 173 | 0 |
| (a) engineer, all of `tests/acceptance/**` (round 1's patch) | 567 | 89 | by the words only | 394 other tickets' |
| (c1) designer: paths outside `tests/` | 32 | 15 | 32 | 0 |
| (c2) (c1) + every ticket path under `tests/` | 35 | 16 | 35 | 0 |
| **(c3) designer, the owner's decision (in the patch)** | **35** | **16** | **35** | **0** |
| (c3) without `docs/` (`{ticket_impl_code}`; not chosen, F4) | 11 | 4 | 11 | 0 |
| (c3) as path checks alone, before the own-tree rule | 106 | — | 35 | 71 (integrated code) |

- **(d)'s 178:**
  - 173 reads of the engineer's own folder;
  - 5 of cases revised for its ticket in other folders, each read after the linking commit:
    - W2-16 reading W1-39's drift case;
    - W2-53 reading W1-30's r14 case ×2;
    - W2-54 reading W1-19's semantic-index case ×2.
  - All 178 are the separation the owner asked for. 0 false refusals, 0 crashes.
  - (a)'s other 389 reads of other tickets' tests, 40 of them the CTO's emergency engineers, are now readable.
- **(c3)'s 35:**
  - 8 reads of the engineer's committed code, 3 of its unit tests, and 24 of the engineer's documents;
  - all after the engineer's commits; 34 in the engineer's own tree, 1 from W2-112-tests.
  - The round-2 tests-tree rule (F1) adds none. Its first stand-in added 2 W2-04-tests reads that were false (the
    engineer's commits reached that tree only on 2026-11-03), and the corrected stand-in removes them. The reviewer
    counted 0 such reads in 2,523 `-tests` calls.
  - The 24 document reads: the owner decided F4 (2026-11-03). `docs/` stays on the designer's no-read list, so
    they are refusals as intended.
  - No designer read the engineer's new unit tests through a shared file or a whole-branch diff. The replay's coarse
    count is 5 calls; a per-command scan found 14 path-less `git` calls naming `w2/<W2>` (F10). All were
    `--name-only` or `git log --oneline`.
- **Parse errors found and fixed:** `tr` as a reader; `-n` in `git grep`; `w2/integrate:` judged as the work tree; a
  crash on a quoted `$(…)`.

**Planted cases.** `test_g14.py`: **146 passed**, about 4 s. The suite covers:
- each role and each tool form: 40 true reads refused and 37 near misses let through;
- the absent block (no check);
- the narrow block (`{ticket_impl_code}`);
- the malformed block, which fails closed;
- the five rules beside the check;
- the own-tree rule;
- the readers' words;
- **the engineer's revised cases**, in a fixture repository:
  - the case revised for the ticket by `Task:` is refused, and so is the one revised in its tests branch under the
    other ticket's `Task:`, by Read, Bash and `git show`, also in another tree;
  - the other ticket's unrevised case is readable;
  - the other ticket's engineer is refused its own folder;
  - a third ticket's engineer reads both revised cases;
- the unreadable link source, which falls back to the own folder and names the fallback;
- **today's real pattern:** W2-126's list holds W2-54's `test_w2_54_query_cache.py` and W2-123's retry case, and
  W2-91's holds neither (skipped once `w2/W2-126-tests` is gone);
- the tests-tree rule (F1): an injected case, and W2-91-tests today with exactly three files;
- conflict markers elsewhere in the map (F2): the block still works and `git merge --abort` passes; a conflict inside
  the block fails closed;
- a list cached by an older method is never read (R2-F12, found by the rehearsal).

**Latency** (the real repository, an engineer on DAEO-jpr0, a simulated copy that reads the patched map, 10 calls each):

| Call | Answer | Candidate, cached | Live hook | First call per key |
|---|---|---|---|---|
| A code read | allow | 47 ms | 44 ms | — |
| Its own folder | deny | 52 ms | 46 ms | 99 ms |
| W2-54's case revised for it | deny | 52 ms | 44 ms | 99 ms |
| W2-64's tests | allow | 52 ms | 44 ms | 99 ms |

So the check adds about 6–8 ms per call, and once per (ticket, heads) about 50 ms more.

**The five rules on the candidate (no block yet, as on the day of the ACT):**
- `tools/guard4_check.py`: PASS (65).
- `drafts/g14/guard4_check.py`: PASS (70: the 65, plus 5 G-14 cases).
- `drafts/act-guard-fix-4/test_guard_fix_4.py` (re-baselined): 462 passed.

**With the block (a simulation in `/tmp` that reads the patched map):**
- **0 of the 500 planted cases change answer**, and 0 of the 89 logged and recovered calls. `{ticket_tests}` refuses
  only the ticket's own tests, and those cases run as W2-00's engineer.
- Round 1's re-baselining is gone: the original `tools/guard4_check.py` and `drafts/act-guard-fix-4/test_guard_fix_4.py`
  stay valid after the ACT.
- In the simulation:
  - both guard4 files: PASS;
  - the 5 G-14 cases: W2-126's engineer is refused its own README and W2-123's case revised for it, and reads W2-64's;
    a grep pattern and an orchestrator are let through;
  - the original `test_guard_fix_4.py`, re-baselined: 467 passed in the rehearsal (§3).

**The stale expectation: `test_logged_refusals` (not G-14's; re-baselined by a test designer, 2026-11-03).** The test
replays ACT-GUARD-FIX-4's 87 logged
refusals and expects 13 to stay refused: `STILL_REFUSED = [64, 65, 73, 74, 77, 78, 79, 80, 82, 83, 84, 85, 86]`
(`drafts/act-guard-fix-4/test_guard_fix_4.py`; now line 401, re-baselined).
- Today it gets `[64, 80]`, on the live hook with no ACT, and the same with the block live.
- Rows 65, 73, 74, 77–79 and 82–86 were refused by rule 2's hidden-part and run-time-listing checks (DEC-820 (d),
  W2-58), which refuse only while the hidden part lies in the trees.
- ACT-D8 (2ae4e094 and 23625eb2, 2026-11-03 15:19–15:34; DEC-1055 (4), G-3) took the hidden half out of every tree,
  so those 11 calls now pass. That is the guard working as decided, not a regression.
- The re-baseline is now made by a test designer: `STILL_REFUSED = [64, 80]`, with comments naming ACT-D8,
  DEC-1055 (4) and G-3. Against the live hook it gives 462 passed; with the ACT's `guard4_check.py`, 467 passed.
- The owner's operator's run of §3 stopped at this line. It was not caused by ACT-G14.

**The test selection.** A path-map change is in the selection's shared core, so it selects everything. Run instead
the scoped tests: the 35 unit files that name `path-map.yaml` (`scoped_tests.sh`).
- On today's tree: 747 passed.
- In a patched export of HEAD: 745 passed; its 2 reds are the export's own (no `.git`) and pass in the main tree.
- The patched map validates with `gov.config.loader._validate_path_map`.

## 3. The commands (your operator, in the main tree)
Preconditions:
- no merge-queue landing is running, and ACT-D8 is not running (never at the same time);
- **a fresh shell** (a new terminal, or `env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" LANG="$LANG"
  bash --noprofile --norc`), in which `D` and `T` are not exported: `env | grep -c '^[DT]='` prints `0`. The guard
  expands a test's `$D` from its own environment, and an exported `D` turns two planted cases red (the rehearsal
  showed it);
- the failed run of 2026-11-03 left `drafts/g14/backup/` with today's three live files (`8cf1daf2804b`,
  `592e542b748c`, `4136269dc4c4`) and no `act-commit`. §3's `mkdir -p` leaves the folder, `cp -p` overwrites the three
  files with the same content, and `act-commit` is written only after §3's commit;
- `git status --short -- .claude/ governance/project/path-map.yaml` shows nothing.

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
rm -rf /tmp/gov-os-act-g14
D=.gov-runtime/scratch/orchestrator/drafts/g14
T=.gov-runtime/scratch/orchestrator/tools
git status --short -- .claude/ governance/project/path-map.yaml
sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml $T/guard4_check.py | cut -c1-12
sha256sum $D/pretooluse.py $D/role_reads.py $D/guard4_check.py $D/path-map-role_paths.patch | cut -c1-12
GUARD_FIX4_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14 bash $T/heavy_slot.sh python3 -m pytest -q -o tmp_path_retention_policy=failed -p no:cacheprovider .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py -k test_logged_refusals -rf | grep -E "^FAILED|failed|passed"
mkdir -p $D/backup
cp -p .claude/hooks/pretooluse.py governance/project/path-map.yaml $T/guard4_check.py $D/backup/
git apply --check -p1 $D/path-map-role_paths.patch && git apply -p1 $D/path-map-role_paths.patch
PYTHONPATH=src python3 -c "import yaml; from gov.config import loader; d=yaml.safe_load(open('governance/project/path-map.yaml')); loader._validate_path_map(d, 'path-map'); print(d['role_paths'])"
cp $D/pretooluse.py $D/role_reads.py .claude/hooks/
cp $D/guard4_check.py $T/guard4_check.py
python3 $T/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS | tail -1
GUARD_FIX4_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14 bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py -rf | grep -E "^FAILED|failed|passed"
G14_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14 bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider $D/test_g14.py | tail -1
bash $D/scoped_tests.sh
git add .claude/hooks/pretooluse.py .claude/hooks/role_reads.py governance/project/path-map.yaml
git commit -m "ACT-G14: role separation from the path map (DEC-1052 G-14): role_paths: engineer {ticket_tests}, test designer {ticket_impl} (c3)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1052" --trailer "Role: owner"
git rev-parse HEAD > $D/backup/act-commit && cut -c1-12 $D/backup/act-commit
```

What each line must show (stop at the first that differs and tell the CTO):
- `rm -rf /tmp/gov-os-act-g14`: silent. It removes the tests' scratch and the link caches of any earlier run, so a
  re-run starts clean.
- `git status`: nothing, both times.
- Today's hashes:

  | File | Hash |
  |---|---|
  | `.claude/hooks/pretooluse.py` | `8cf1daf2804b` |
  | `governance/project/path-map.yaml` | `592e542b748c` |
  | `tools/guard4_check.py` | `4136269dc4c4` |

- The drafts' hashes:

  | File | Hash |
  |---|---|
  | `drafts/g14/pretooluse.py` | `e406653ef6c9` |
  | `drafts/g14/role_reads.py` | `8c1ea44b2313` |
  | `drafts/g14/guard4_check.py` | `2a2050872724` |
  | `drafts/g14/path-map-role_paths.patch` | `f8372ccdc4dd` |

  `bash_writes.py` is unchanged (`bb246a21735e`) and is not copied.
- The pre-check (`-k test_logged_refusals`, on the live hook before anything changes): `1 passed, 461 deselected in
  …`, and no `FAILED` line. The 87 logged refusals give today's expected `[64, 80]` (the test designer's re-baseline
  after ACT-D8). It is kept as a green check: a red here means the guard has changed since this ACT was rehearsed, so
  stop before anything is copied.
- `git apply`: silent.
- The `python3 -c` check prints `{'engineer': {'reads_denied': ['{ticket_tests}']}, 'independent-test-designer':
  {'reads_denied': ['{ticket_impl}']}}`.
- `guard4_check.py --settings`: ends `PASS`. The five `G-14 …` lines show W2-126's engineer refused its own README and
  W2-123's revised case (`want deny, got deny`), and the rest allowed.
- `test_guard_fix_4.py` (ACT-GUARD-FIX-4's own, re-baselined), with the new `guard4_check.py`'s 5 G-14 cases:
  `467 passed in …`, and no `FAILED` line.
- `test_g14.py`: `146 passed`. The two "today" cases are skipped if W2-91-tests or `w2/W2-126-tests` is gone.
- `scoped_tests.sh`: `scoped files: 35`, then `747 passed`.
- `git rev-parse`: the ACT commit's hash, saved in `backup/act-commit` for the rollback (review F8).
- **A red check:** the hook and the map are live from the `cp` line on. If a check is red, stop, restore by hand
  (§4) and tell the CTO (review F9).

**Rehearsed end to end on 2026-11-03 16:23:38–16:25:30 GMT, from a fresh shell** (`env -i` with only HOME, USER,
LOGNAME, PATH and LANG), with the test designer's re-baselined `test_guard_fix_4.py`, in a clone at `f451207018ce`
(today's head of `w2/integrate`), `~/gov-os-runs/G14-rehearsal/Dynamic-Agentic-Engineering-OS`, by
`drafts/g14/rehearse_act_g14.sh` (§3 line for line, then §4). Its output is attached as `drafts/g14/rehearsal.log`.
- How the clone stands in for the main tree:
  - `git clone --no-hardlinks` with every local branch recreated at the same commit, and their (now empty) reflogs;
  - the untracked `tools/`, `drafts/g14/` and `drafts/act-guard-fix-4/` copied in, with the root's path written as the
    clone's in their text files;
  - the same folder name as the main tree (one rm case names it), outside `/tmp`;
  - `D` and `T` not exported;
  - every test line through the shared slot gate.
- What the rehearsal found:
  - the stale expectation above, which is the operator's failure;
  - R2-F12, a cached list read by a changed method, now keyed by the method;
  - the reflog loss, now read from the commit graph;
  - the exported-`D` trap, now a precondition;
  - two of `test_g14.py`'s own cases assumed `$TMPDIR` existed (false right after §3's `rm -rf /tmp/gov-os-act-g14`);
    they now use pytest's `tmp_path`. That was a test fix only.
- Round 2's copy `drafts/g14/test_guard_fix_4.py` (still expecting the 13 old rows) is removed (D-F4), so no one runs
  it by mistake; §3 and the script name only ACT-GUARD-FIX-4's own file.
- In the log, the two `guard4_check.py` hashes read `5f1b94fafe45` (tools) and `727ba3eb5be5` (drafts) instead of
  `4136269dc4c4` and `2a2050872724`. Both files name the root, which the clone substitutes; with that one
  substitution the main tree's files hash to exactly the clone's. Every other hash and output is the main tree's.

**When it takes effect:**
- The main tree: at the next tool call of a session in it (the hook is read at each call).
- A worktree: when `w2/integrate` is merged into it, which brings the new hook. The block is read from the main tree
  whatever the worktree's own map says.

**Check after (the next day):** the guard-refusal log's `role_paths` refusals, one per call. Expected:
- engineers' reads of their own ticket's tests (its folder and its revised cases);
- designers' reads in `~/gov-os-worktrees/<W2>`, or of the engineer's carried files in `<W2>-tests`.

Any other is a false refusal, so tell the CTO. Also tell the CTO if a refusal says the link source could not be worked
out.

**Notes for the D-5 templates.**
- Engineers (review F3): for a whole-branch diff after TESTS-READY, use `git diff --stat …` or
  `git diff … -- . ':!tests/acceptance'`. The guard does not judge a pathless diff, and that diff shows the acceptance
  tests.
- Test designers: a case revised for a ticket carries that ticket's `Task:` trailer. (ii) catches a lapse only inside
  the ticket's own tests branch.

## 4. The rollback (one command)
It reverts the hash §3 saved (review F8), with the trailers, and puts the old `guard4_check.py` back.
```
cd /home/usain/Dynamic-Agentic-Engineering-OS && D=.gov-runtime/scratch/orchestrator/drafts/g14 && read -r H < $D/backup/act-commit && git revert --no-commit "$H" && git commit -m "Revert ACT-G14 (${H:0:12}): role separation from the path map" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1052" --trailer "Role: owner" && cp -p $D/backup/guard4_check.py .gov-runtime/scratch/orchestrator/tools/guard4_check.py && python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings $PWD | tail -1
```
- It ends `PASS` (the 65 cases of ACT-GUARD-FIX-4).
- The revert takes out the hook change, `role_reads.py` and the block together. If a later commit changed lines near
  the block in the map, the revert can conflict; then remove the block by hand.
- Before the commit exists (a red check in §3), restore by hand: `cp -p $D/backup/pretooluse.py .claude/hooks/ && cp -p
  $D/backup/path-map.yaml governance/project/ && rm .claude/hooks/role_reads.py && cp -p $D/backup/guard4_check.py
  .gov-runtime/scratch/orchestrator/tools/`.
- A lighter undo is to remove only the `role_paths:` block from the map. With no block there is no check.
- The link cache needs no undo. It is a scratch file per session in its own TMPDIR.

## 5. The risk
- **The engineer's linked cases depend on the records.** A revision without the right `Task:`, made outside the
  ticket's tests branch, is not found. Neither is one whose tests branch or reflog is gone. The own folder is always
  refused.
- **Over-inclusion at the file level.** A whole revised file is refused, and a designer's fixture repair for the
  ticket counts as the ticket's. The replay shows 0 false refusals from it.
- **The cache can be written by the session.** It sits in the session's TMPDIR. A session that rewrote it could empty
  its list, but that is a deliberate route round a refusal (DEC-849), outside the threat model of honest sessions;
  the own folder does not depend on the cache.
- **The CTO's emergency engineers (W2-00)** are refused the 4 files the CTO's own revisions link to W2-00.
- **(c3) refuses the engineer's documents** (24 of its 35): CIT-P, CIT-E and research notes. The owner decided F4:
  `docs/` stays on the designer's no-read list, as built. `{ticket_impl_code}` remains in the code, unused.
- **Not judged, by design (no shell guessing):**
  - reads by inline code or a script;
  - searches from a folder above;
  - run-time names;
  - a whole-branch diff without a path (F3);
  - `gov retrieve` results.
- **Shared-file exceptions are by name** (F5). An engineer who writes a new test into a `conftest.py` or a
  `*support*.py` leaves it readable to the designer, which is the owner's (c3) choice.
- **A malformed `role_paths:` block** fails closed on every Read, Grep and Bash call; a YAML error elsewhere does not
  (F2).
- **When git cannot answer** (5–10 s timeouts): the designer's rules let the read through (F7), and the engineer's
  rule falls back to its own folder, as the reason says.
- **The replay's approximations:**
  - role from the brief's first line: 1,021 calls of unclassified sessions were not judged;
  - the main tree's `.tickets/` for `allowed_paths`;
  - today's disk for globs and bare `git` path words;
  - commit times as the stand-in for a past call's branch state;
  - (ii) only where the tests branch still exists.
- **The rehearsal's limits:** it ran in a clone whose root path differs (the tests name the root, so it was written as
  the clone's), and the clone's `origin` is the main tree. Every line's output matched what this ACT now says.

## 6. Recommendation
Apply. Confidence:
- **high** on the replay and the planted cases;
- **medium-high** on the new code on the guard's path: about 850 lines in `role_reads.py` and 15 in the hook, pinned
  by 145 planted cases, the 462 + 70 rule tests and the replay of 17,243 real calls.

**Independent review:** `reviews/g14.md`, round 1: not READY (F1 blocking).
- Round 2 fixes F1 and rides F2, F8, F3's note, F9 and F10.
- It also builds the owner's engineer rule (DEC-1056).
- **Round 2: READY** (`verdict.py`: `(True, [])`; G14-1 to G14-7 pass, no finding blocks). The link method's limits
  are rows, not blocks: R2-F11 (a mis-trailered revision made outside the tests branch, or after the branch and its
  reflog are gone), R2-F12 (the cache keyed on three heads), R2-F13 (the fallback leaves no trace on an allowed read).
  For D-5: take the tests-branch link from the lead's merges of `w2/<W2>-tests` instead of the reflog, and the template
  line requiring `Task: <the ticket it is for>` on a revision.
- F4 (`docs/` in `{ticket_impl}`): decided by the owner, 2026-11-03. `docs/` stays on the designer's no-read list,
  as built.
- The delta check (`_fork`, `_method`, the cache key) and the test designer's re-baseline: READY (`verdict.py`
  `(True, [])`), with no code change asked.
- **Run it apart from ACT-D8** (before or after, never at the same time): ACT-D8's prune must not race this ACT's commit.
- **After the round-2 review (the operator's stopped run and the rehearsal):** three fixes in `role_reads.py`, about
  30 lines:
  - (ii)'s fork point from the commit graph instead of the reflog (`_fork`; ACT-D8 had emptied the reflogs, so W2-54's
    six revised cases were no longer linked to W2-126);
  - the link cache keyed by the method and the repository as well (R2-F12: a list cached by the reflog-based rule
    was read by the fixed rule for the same heads);
  - a test fixture merging with `--no-ff`, as the project does.

  `pretooluse.py` is unchanged. The CTO decides whether the reviewer re-checks this delta.

## 7. Applied (the owner, 2026-11-03 ~16:50)
The operator ran §3 from a fresh shell; every line matched `drafts/g14/rehearsal.log`: pre-check 1 passed, 461
deselected; `role_paths` as stated; `guard4_check.py` PASS (70); `test_guard_fix_4.py` 467 passed; `test_g14.py` 146
passed; `scoped_tests.sh` 35 files, 747 passed; the commit `4edd196c5878` (three files, `Role: owner`), saved in
`backup/act-commit`. The first run (~16:00) stopped at the stale `test_logged_refusals` and was restored by hand
(DEC-1059). Recorded as DEC-1059; the CTO's hold ended at 16:54.
