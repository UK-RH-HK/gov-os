# D-10's red-fix list: the review of three whole-tree copies limited to src/ (W2-92, DAEO-n0wb)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-whole-tree-review.md`; branch `w2/W2-92-d10b-tests` at `bbea1bb16`; reviewer log `/home/usain/gov-os-worktrees/W2-92-d10b-tests/.gov-runtime/scratch/lead/log/D10-whole-tree-review-2.json` (the first launch ended on a network error, EAI_AGAIN).
- verdict.py: READY (no blocking finding; F1, an inherited GIT_DIR, is closed in the suites by item 1's tests/conftest.py).

**task:** W2-92 / DAEO-n0wb. Review of `bbea1bb16`: the three whole-tree copies limited to `src/` (D-10's red-fix list). KPI id `whole-tree-named-paths`.

**sandbox check (first):**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-n0wb` failed with "Read-only file system", and the file is absent.
- (b) `git hash-object -w --stdin` worked (blob `1ae28402a109`) and `git update-index --refresh` exited 0. That blob is the only thing written, and it is in the shared object store, not in a tree.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing. I started no embedder or model.

**status:** DONE. The verdict is pass, with no blocking finding. Classification: 3 findings, none blocking. F1 is in scope, ordinary work no, fails open (a row). F2 is in scope, ordinary work no, other (a row). F3 is out of scope, ordinary work yes, fails open (a row against W1-28's reader).

**work_completed:**
- Confirmed identity and that the merge at HEAD `60dbb62e754f` leaves the four acceptance folders exactly as at `bbea1bb16`.
- Read the diff, the three helpers and their four callers, W1-28's check and README, W1-50's freeze-settings cases, the trailers and the designer's return.
- Compared the old and new archive output on the real repository, ran W1-28's reader on the before and after sources, and probed a synthetic repository.

**files_changed:** none. `git status --porcelain` is empty and HEAD is unchanged.

**evidence:**
- **Same output on the real repository.** The old and new archive commands give byte-identical output at all three pinned commits and at HEAD. The commits are `8c28aa70fb3f` (LINKS_BASE, also the speed file's BASE), `2a64626532cb` (D6_BASE) and `68ce354a74c7` (PRE_S6_COMMIT). Their tars are 1,648,640, 2,007,040 and 1,536,000 bytes, and HEAD's is 2,088,960.
  - Both tars carry the same commit-id header and the same 184, 212, 180 and 225 members.
  - Every file (149, 174, 145 and 186 of them) matches its blob in `<commit>:src`, and executable bits and links match too.
  - No member lies outside `src/`, and no held-out path appears among the names.
  - Running from working directory `/` gives the same bytes.
  - The worktree holds 40 ignored `.pyc` files under `src/`; none reaches either archive.
- **W1-28's reader, before and after.** At `e74b551bc` it flags all three helpers as whole-tree routes (the bare root plus `archive`), none of them runnable. At `bbea1bb16` it flags none of them.
  - Today it finds exactly two whole-tree copiers, W1-05's and W1-07's `copy_working_tree`, both runnable.
  - Its list of runnable copiers is the six known ones.
- **Synthetic repository (made-up held-out file, in my TMPDIR):** the probes and their results are in the check answers and findings below.
- **Scratch:** peak 812K and 202 inodes, now removed.

**tests:** I re-ran no suite, since the role says "re-run nothing the lead ran". The probes above replace those runs, so the real-model exclusion did not apply. The row arithmetic matches the designer's numbers:
- W1-28 + W1-50 go from 44 rows (14 red) to 32 rows (0 red).
- The 12 rows that disappear are 3 functions × 4 W1-50 rows.
- The 14 reds were W1-28's 1 and W1-50's 13 (12 rows plus its runnability guard).

**discoveries:**
- On git 2.43.0, running the archive from `src/` loses its limit when the process inherits `GIT_DIR`, as it does in a hook or `git bisect run` step in a linked worktree (F1).
- On a commit with no `src/`, the new form exits 0 and produces an empty `src/` (F2). The designer's risk line ("would fail loudly") is wrong for that case.
- W1-28's reader treats `git -C REPO_ROOT/<folder>` as a named path for every git verb (F3).
- I could not find the CTO helper's out-of-sandbox record for `bbea1bb16`. I searched the orchestrator scratch, `D10-REDS.md` and the worktrees' scratch folders.
- **Worked round:** the Write tool's permission for a scratch script in my TMPDIR was not granted in this non-interactive session. I used inline `python3 -I -B -c` instead, which writes no file for the real-repository probes.
- **Self-report:** one `env` listing, run to check for `GIT_DIR`, also showed the sandbox proxy's credentials in my own tool output. I copied them nowhere.

**risks:** F1's condition (an inherited `GIT_DIR`). The designer's lesson, if recorded as written, would lead a future designer into F3.

**lessons:**
- A subfolder `git archive` stays limited only while git finds the repository by itself; an inherited `GIT_DIR` makes the subfolder the top of the work tree.
- `-C <folder>` limits `archive` and `ls-files`, but never `worktree add`, `clone`, `bundle` or `checkout-index -a`.

**proposed_decisions:** none. Three Wave 3 rows:
1. Run the three archive calls with the `GIT_*` variables removed, as `gov.util.gitenv` already does elsewhere.
2. Assert that the extracted tree holds `src/gov` (or that every name starts with `src/`).
3. Have W1-28's reader treat a whole-repository git verb run from `REPO_ROOT / <x>` as a whole-tree route.

**unresolved:** the CTO helper's record was not found, so I judged without it. Because the archives are byte-identical, the revision cannot change W2-92's or W2-13's results, with or without the code-graph tool.

**recommended_next_action:** READY by the block below. The CTO runs its outside-the-sandbox check and merges, sends F1–F3 to Wave 3, and narrows the designer's lesson and risk lines before either is copied anywhere.

**decisions:** DEC-385, DEC-399, DEC-710, DEC-982, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1040 (item 3), DEC-1080.

## Answers to the checks

**1. Same content: yes, byte for byte.**
- On the real tree this holds at all three pinned commits, whose `src/` differs from today's, and at HEAD. It holds with untracked files present and from a different working directory.
- On the synthetic repository the old and new outputs are identical in every case tried:
  - a changed tracked file and an untracked file;
  - an older commit with a different `src/`;
  - a linked worktree;
  - the environment git hands a hook in the main worktree;
  - root attribute rules (`export-ignore`, `export-subst`), which both forms apply the same way.
- A missing commit fails in both forms (exit 128).
- The callers' premises hold. Each extracts the same bytes, and W2-13's check that `loader.py` has no `lexical_policy` still runs. The speed file's `base` now raises an `AssertionError` instead of `pytest.fail` on a missing commit; either way it is a setup error.
- The two exceptions are F1 and F2.

**2. Truly named-path copies, not a slip past the reader.**
- W1-28's README counts a route only when it is "given the bare root", and its planted `copy_one_folder` case shows that a folder below the root is not a whole-tree copy.
- The old form was already limited to `src` by its path argument; the reader just does not read that argument, so its flag was a false positive.
- The new form states the same limit where the reader looks, and the content is identical.
- The held-out file cannot reach either copy at the pinned commits in a normal environment. It can reach the new form only under F1's condition, and never the old one.

**3. No expectation lowered.**
- No assertion, case, parameter, marker, skip or xfail changed in W2-92 or W2-13. W1-28 and W1-50 are untouched.
- Losing W1-50's 12 rows is right, not a coverage loss. Those rows tested settings-stripping on functions that copy only `src/`, have no root parameter and copy no settings file, so they could never pass and carried no KPI meaning.
- KPI line 3 still runs on every true whole-tree copier (W1-05's and W1-07's: 8 rows) plus its two guard cases.

**4. Trailers and paths:** git parses all five trailers (Task, Implements, Role, Rewrite-Reason with the brief's text word for word, Co-Authored-By). Only 5 files changed, all under `tests/acceptance/W2-92/**` and `W2-13/**`. The README lines add no test ids.

## Findings

**F1: an inherited `GIT_DIR` turns the src-only copy into a whole-repository copy.**
- What was done: in a linked worktree, a git hook received `GIT_DIR` and no `GIT_WORK_TREE`, and ran both forms with that environment.
- What happened: the new form archived the whole commit under `src/`, including the made-up `governance/project/held-out.yaml`. The old form stayed limited to `src/`.
- What should have happened: the copy holds `src/` only, whatever the environment.
- On the real tests, the case would then fail (no `gov` package where expected), but the held-out file would already be in its temp folder and kept with the failed run.
- Ordinary work: no, because every runner here clears inherited `GIT_*` before running these suites (`runner_env`/`program_env`, the nightly bisect, `landing_select` from the hook), session shells carry none, and no hook runs these suites.
- Consequence: fails open.
- Scope: in.
- Would be reversed by: git not exporting `GIT_DIR` to a linked-worktree hook (the probe shows it does), or the archive staying inside `src/` under it. A workflow runner that passes `GIT_DIR` would turn ordinary work to yes, and then the finding blocks.

**F2: a commit with no `src/` gives an empty copy instead of a failure.**
- What was done: the new form ran on a commit whose tree has no `src/`.
- What happened: it exited 0 with an empty `src/` folder. The old form failed with "pathspec 'src' did not match any files".
- What should have happened: a failure that names the commit.
- The callers then fail anyway (W2-13 reading `loader.py`, W2-92 importing `gov`), but with a misleading message.
- Ordinary work: no, because all four pinned commits hold `src/` (verified), and new bases come from `w2/integrate`, whose commits all hold it.
- Consequence: other.
- Scope: in.
- Would be reversed by: git 2.43.0 exiting non-zero on such a commit.

**F3: W1-28's reader treats `-C REPO_ROOT/<folder>` as a named path for every git verb.**
- What was done: the reader was given a planted `git -C REPO_ROOT/src worktree add`, and that command was run on the synthetic repository.
- What happened: the reader did not flag it, yet the checkout held the whole tree, held-out file included. The designer's lesson ("name the folder in `-C`") points toward this pattern.
- What should have happened: the reader flags it as a whole-tree route.
- Ordinary work: yes, because a designer following that lesson for a new fixture needs no deliberate construction.
- Consequence: fails open.
- Scope: out (it concerns W1-28's reader, not this revision, whose `archive` form is truly limited).
- Would be reversed by: the reader flagging that planted text, or `worktree add` from a subfolder checking out only the folder.

```verdict
{"kpis": [{"kpi": "whole-tree-named-paths", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
