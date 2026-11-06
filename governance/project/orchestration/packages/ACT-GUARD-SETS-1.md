# ACT-GUARD-SETS-1: the guard refuses the hidden sets outside the repository to the measured roles (DEC-1082 (3))

- **For:** the owner, to decide the four points in §5, then the owner's operator (a guard change: P-ACT-SPLIT).
- **By:** the CTO, 2026-11-06. A read-only design, built and rehearsed in a clone by an engineer, reviewed by the CTO.
- **Nothing live is changed** until the operator runs §3.

## 1. The gap, and the fix
- **The gap:** the guard (`.claude/hooks/pretooluse.py`) builds its hidden-path checks only for the repository and
  its worktrees, so it never judges a path under the sets root `~/gov-os-eval`, for any role. The health check of
  11-06 showed it: an engineer's Read of `~/gov-os-eval/.../hidden/h01.yaml` was allowed.
- **The fix, two files, no pin change:**
  1. **A new block in the path map**, `sets_root_hidden`, read from the main tree's copy only, so a branch cannot
     weaken it. It names:
     - the root `~/gov-os-eval`;
     - the hidden globs: `memory-retrieval/hidden/**`, `memory-verdict/**`, `memory-verdict-2/**` and
       **`transcripts/**`**;
     - **the refused roles: orchestrator, engineer, research, product-spec, independent-test-designer and
       independent-auditor.**
  2. **The hook:**
     - those globs are refused under the sets root and in every tree, for reads and for the writes the guard can
       resolve;
     - one narrow override, so a listing that cannot reach the sets root is not refused for it (a `git diff | xargs`
       pipeline, a `$(mktemp -d)` on a measure line).
- **Not affected:**
  - **The measure:** its command names only the root, and its own code reads the files. `_measured` stays False for
    the orchestrator, checked.
  - **Your writer, checker and operator:** they run outside the guard. A writer-like headless session read a
    planted hidden file, checked.
- **Two corrections to the CTO's first defaults, for you to approve (§5 (1)):**
  - **Six roles, not three.** The verdict sets also measure product-spec, the test designer and the auditor. With
    only three listed, those three could still read `memory-verdict-2/retired/` (old copies of the questions) and
    `XCHECK.md`.
  - **`transcripts/**` too.** It holds the writer's transcript of the hidden questions (ACT-D8). `runs/**` stays
    open: the CTO's results go there, with no question text.

## 2. The files (drafts, scratch; checked by hash before they apply)
| File (`.gov-runtime/scratch/orchestrator/drafts/sets-root-guard/`) | sha256 (first 12) |
|---|---|
| `pretooluse.candidate.py`: the live hook (`e406653ef6c9`) plus the change, nothing else | `42749e673c50` |
| `pretooluse.diff` (158 lines) | `892acd89715b` |
| `path-map.patch`: the map `cc8139a1c8f4` → `da095dce9171` | `d8351eb83bab` |
| `guard4_check.candidate.py`: the 70 existing cases unchanged, plus 194 new ones | `12af75e62a82` |
| `apply.sh`: `check`, `apply`, `undo`, with backups and sha256s | `39c61ed11919` |

`apply.sh check` and `apply` stop unless both live files still hash as built. **If the path map changes before you
apply (for example W2-61h's `evaluation_families`, or D-9's edits), the CTO rebuilds the patch and re-runs the
rehearsal first.**

## 3. The operator's steps (main tree, about 1 minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/drafts/sets-root-guard
bash $G/apply.sh check     # both files hash as built (exit 0)
bash $G/apply.sh apply     # backups, then the two files; sha256 before and after
git add .claude/hooks/pretooluse.py governance/project/path-map.yaml
git commit -m "ACT-GUARD-SETS-1: the guard refuses the hidden sets outside the repository to the measured roles" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1082" --trailer "Role: owner"
```
**Then the CTO:** copies `guard4_check.candidate.py` over `tools/guard4_check.py` and runs it on the live tree.
Expected: 203 run, PASS (only the cases safe on the live tree run). **Undo:** `bash $G/apply.sh undo` restores both
files byte for byte (rehearsed), then a commit.

## 4. The rehearsal (DEC-1057): `REHEARSAL.md` and `rehearsal.log`, one clean run, 12:03–12:08, 0 failures
| Step | Result |
|---|---|
| R2 (HOME substituted, the block applied, the new cases only) | **194 run, 0 failed** |
| R1 (the block's root planted; the 70 old cases and the new ones) | **250 run, 0 failed** |
| The live-tree subset | 203 run, 0 failed |
| The override switched off | exactly the 6 cases it exists for fail, which shows it is needed and does nothing else |
| `test_guard_fix_4.py`, `test_g14.py` | 467 passed; 151 passed, 1 skipped: the same before and after |
| The measure check | `_measured` False for the orchestrator in every set, True for the engineer (the control) |
| A writer-like session (headless, Haiku) | read a planted hidden file: allowed; no guard runs there |
| `apply.sh undo` | both files back byte for byte |
| The live hook, the live map, the real sets root | **unchanged** (hashed before and after; the sets root's entry only, never its contents) |

**The replay:** the last 48 hours of tool calls (3,612 unique) through the hook before and after.
- **No change:** 3,582 allowed and 5 denied, before and after. No call that does not name the sets root changed.
- **25 go from allowed to refused:**
  - **21 are meant:** the commands name hidden folders. They are the CTO's own work: listings and `stat` of hidden
    folders (names only), `repin_gold.py` and `leak_check.py` on hidden folders, and **12 by independent auditors**
    (the cross-check and hidden-domain diagnostics, such as DEC-1074 (2)'s reading of the spent 60).
  - **4 are false:** the words that name hidden paths sit only inside a `python3 - <<'EOF'` body, scripts that wrote
    the ACT-MSET packages. The CTO now writes documents with the Write tool, so these do not recur.

## 5. For your decision
1. **The two corrections:** six refused roles, and `transcripts/**` (§1). Recommended: yes.
2. **When to apply.** Re-pin window 4 re-pins the hidden sets' gold with `repin_gold.py`, and the leak check runs
   on hidden folders, both today from the CTO's session. Once applied, those calls are refused.
   - **(a) Recommended:** apply right after re-pin window 4. Before that, the CTO changes its hidden-set tools to
     take the sets root as an argument and open the files in their own code, printing ids and counts only, as the
     measure does. That is its own lane, with no guard change. The ACT is then applied with no break.
   - **(b)** Apply now, and the gold re-pin and the leak check move to your operator.
3. **Diagnostics on spent sets.** After this change, no session the guard judges can read a set's questions, the
   auditor included. A diagnostic like DEC-1074 (2)'s auditor read of the spent 60 then runs outside the guard (your
   checker or operator), or under an exception you name. Recommended: outside the guard; no exception in the code.
4. **Worktrees:** each runs its own copy of the hook, so a worktree gets the change when `w2/integrate` is next merged
   into it. Live worktrees with measured roles get that merge as part of the ACT. Recommended: yes, by the CTO, the
   same day.

**What it costs:**
- every hook call runs one git call to find the main tree, about 80 ms;
- a malformed block refuses every call (fail closed, as designed);
- the product's own guard (`reads.parts()`) is a later W2-42a line (D9-FATES).

**Basis:** question 2 (the hidden halves refused to every measured role, wherever they lie) and question 4 (the
measure and your writer, checker and operator unaffected).
