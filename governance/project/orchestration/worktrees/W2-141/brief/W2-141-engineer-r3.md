Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-141/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-141 — the engineer's brief, round 3: the review's findings (DAEO-xwro)

You are a fresh engineer for **W2-141** (`.tickets/DAEO-xwro.md`). Rounds 1 and 2 (`a3dbf84f`, `c853fbc7` on
`w2/W2-141`) built the decide side, the staged hook copies and the unit-test revisions; `gov accept W2-141` passes
182/182. The independent review (round 1) is **NOT READY**: S2 fails on four findings that are in scope, reachable in
ordinary work and fail open (F1 to F4). The CTO, as moderator, triages:

- **Fix (blocking):** F1, F2, F3, F4.
- **Fix too (cheap, in scope):** F5 (route `zgrep -r` and `grep -d recurse` as recursive), F6 (a brace-expanded
  `--exclude-dir={.git,<T>}` read as the options Bash makes of it, on both sides), F7 (a rollback step in
  `docs/changes/W2-141-hook/README.md`: the live files' sha256 and how to restore them), F8 (the evidence file's stale
  regression section brought up to date).
- **Rows, not this round:** F9 (Glob under the fail-closed rule with a malformed `role_paths`), F10, F11.

Each fix goes on **both sides where the finding names both** (decide in `src/gov/guard/reads.py`, the hook in
`docs/changes/W2-141-hook/role_reads.py`; keep the duplicated block identical, as your test checks). F1's third call
excludes the folder with a git pathspec (`':!tests/acceptance/<T>'`): that exclusion is honoured, and the refusal for
`git grep` says how (`-- . ':!tests/acceptance/<T>'`). F4: a recursive search whose start is a shell glob that can expand
to (or above) the own folder is refused unless excluded. Add a unit case for every call the findings name, refused or
allowed as stated, in `tests/unit/guard/test_w2_141*`.

## The review's findings, as written (round 1)

**F1 (S2, scope: in). The staged hook lets `git grep` through when it searches from a folder holding the own acceptance folder.**
- Calls: `git grep -n zqxw141`, `git grep -n zqxw141 -- .`, `git grep zqxw141 -- . ':!tests/acceptance/W2-941'`. All three are hook=allow.
- Decide refuses them, but with the old `TESTS_REFUSAL` and no "how". It even refuses the third call, which does exclude the folder.
- Cause: `role_reads.py`'s `Bash.git` (around lines 760–841) only records the paths named after the pattern, and `x_search` has no `git` branch.
- Ordinary work: yes, because `git grep` is a standard repo-wide search.
- Consequence: fails open.

**F2 (S2, scope: in). The staged hook lets a `git ls-files` listing piped into a reader through.**
- Calls: `git ls-files | xargs grep zqxw141`, `git ls-files tests | xargs cat`. Both are hook=allow; decide refuses both.
- Cause: only find, `rg --files`, `ag -g` and `ack -f` enter `_listed`.
- Ordinary work: yes, because piping `git ls-files` into a reader is a common idiom.
- Consequence: fails open.

**F3 (S2, scope: in). The staged hook lets a `for` loop over a listing's `$(...)` through when the loop body reads.**
- Calls: `for f in $(find . -name '*.md'); do head -3 $f; done`, `for f in $(rg --files); do head -3 "$f"; done`. Both are hook=allow; decide refuses both through `runtime()`.
- Cause: `_reads_names` checks the `for` word itself, and `_loop_reads` covers only while/until loops.
- Ordinary work: yes, because looping over found files to show their heads is normal.
- Consequence: fails open.

**F4 (S2, scope: in). Decide lets a recursive search through when its start is a shell glob.**
- Calls: `grep -rn zqxw141 */`, `grep -rn zqxw141 tests/*`, `rg zqxw141 tests/*`, `grep -rn zqxw141 tests/acceptance/*`, `grep -rn zqxw141 tests/acc*`. All are decide=allow; the hook refuses all of them.
- Cause: `above()` resolves the literal word (only `*` and `./*` are special-cased), and `glob_word`'s `*` does not cross folders. This predates W2-141, which leaves it open.
- Ordinary work: yes, because `grep -rn foo */` and `tests/*` are plain idioms.
- Consequence: fails open (on the decide and containment side; this repo's hook refuses it after the ACT).

**F5 (S2, scope: in). Decide does not see `zgrep -r` or `grep -d recurse` as recursive.**
- Calls: `zgrep -r zqxw141 .`, `grep -d recurse zqxw141 .`. Both are decide=allow, hook=deny.
- Cause: decide's `_shell_search` only matches `-r`/`-R`, and `zgrep` is not routed.
- Ordinary work: no, because these forms are rare.
- Consequence: fails open.

**F6 (S2, scope: in). A brace-expanded exclusion is refused although it keeps the folder out.**
- Call: `grep -rn --exclude-dir={.git,W2-941} zqxw141 .` is refused on both sides. Bash turns it into two `--exclude-dir` options; the guard sees the literal word.
- Ordinary work: yes, because `--exclude-dir={.git,node_modules}` is a common form.
- Consequence: other (a false refusal; the refusal's own form works).

**F7 (S3, scope: in). The hook README gives no rollback step.**
- It gives the live sha256 and the apply step, but not how to restore the two live files (for example, keep a copy, or check out the tracked files at the pinned commit).
- Ordinary work: yes, because the operator applies this ACT.
- Consequence: other.

**F8 (S3, scope: in). The evidence file's "regression run" section is stale.**
- It says `test_reads.py` is outside the paths with 15 reds. That file was revised in this branch, and its rows pass (550 passed with opt-ins).
- Ordinary work: yes, because the CTO reads it to prepare the ACT.
- Consequence: other.

**F9 (S1, scope: in). Routing Glob to `role_reads` brings Glob calls under its fail-closed rule.**
- With a malformed `role_paths` section, Glob calls are now refused for every role, and each Glob call runs the judges' setup. This is behaviour beyond the searches.
- Ordinary work: no, because a malformed section is rare.
- Consequence: other.

**F10 (S2, scope: out, predates W2-141). Decide refuses a find whose action does not read.**
- Call: `find . -name '*.py' -exec wc -l {} +`. Decide refuses it (now with the find "how"); the hook allows it, since it counts only reading actions. It was refused before W2-141 too.
- Ordinary work: yes, because counting lines this way is normal.
- Consequence: other.

**F11 (S2, scope: out). Decide judges the own folder only in the session's own tree.**
- A search from another tree that holds `tests/acceptance/<T>/` (for example, the main checkout's root) is allowed by decide; the hook judges every tree and refuses it.
- Ordinary work: no, because an engineer works in its own worktree.
- Consequence: fails open.


## Where you work
- `/home/usain/gov-os-worktrees/W2-141`, branch `w2/W2-141`; your paths are the ticket's `allowed_paths`. Never `.claude/`.
- **You never read `tests/acceptance/W2-141/`** (DEC-820 (c)): only `gov accept W2-141`'s results. Every Grep or Glob
  call that could reach it carries `!tests/acceptance/W2-141/**`; recursive grep `--exclude-dir=W2-141`.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-141/src` and your real `HOME`: `tests/unit/guard tests/unit/hooks
  tests/acceptance/W2-84`, standard and with `GOV_TESTS_OPTIN=lifted,breadth`; every red named. Then
  `python3 -m gov.cli.main accept W2-141 --root /home/usain/gov-os-worktrees/W2-141`.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: Read and Grep tools; one simple command per Bash call.
- Search again once (DEC-1092 (1)) if a search does not answer. Never make a guard decision fail open.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-141` with
  `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1093, DEC-1102" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every test run you started has finished.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), each finding and what you changed for it (both sides), the
new unit cases, the regression counts with every red named, `gov accept`'s counts.
