# W2-141 — the independent review (DAEO-xwro), round 2 (the last)

You are a fresh, read-only independent reviewer. Review round 2 of **W2-141** (`.tickets/DAEO-xwro.md`: read it in
full): the guard refuses an engineer's Grep, Glob or recursive Bash search that can reach its own ticket's acceptance
folder unless the call excludes it, and the refusal says how (DEC-1093 (2), DEC-1102).

Round 1's review (verdict NOT READY: S2 failed on F1-F4) is quoted at the end. The engineer's round 3 (`7716610e2` on
`w2/W2-141`) fixed F1 to F8 on both sides; F9, F10 and F11 were triaged as rows. This is the last review round
(DEC-1010: at most two): judge whether S1, S2 and S3 now hold.

## What to review
- `git diff c853fbc7e..7716610e2` in `/home/usain/gov-os-worktrees/W2-141` (round 3's change), and the whole branch
  against `w2/integrate` where you need it: `src/gov/guard/reads.py`, `docs/changes/W2-141-hook/role_reads.py`,
  `pretooluse.py`, `README.md` (now with a rollback section), `tests/unit/guard/test_w2_141*`,
  `docs/changes/W2-141-evidence.md`.
- **The runs:** the CTO's `gov accept W2-141` outside the sandbox: 182/182. The engineer's regression (`tests/unit/guard
  tests/unit/hooks tests/acceptance/W2-84`, standard and with every opt-in row): no reds.

## Check
- Each of round 1's calls for F1 to F6, through decide and through the staged hook, refused or allowed as the finding
  says; the refusal names the folder and the tool's exclusion (`git grep`: `-- . ':!tests/acceptance/<T>'`).
- Round 3's new readings did not open anything else: `git grep` with a revision, `git ls-files` as a listing, braced
  options (the engineer names one rare self-defeating form, a quoted brace word, as allowed), glob starts for the own
  folder only. Did any new false refusal appear for an honest engineer's ordinary searches (its own `src/`, named files,
  other tickets' tests, `git log`, `git diff`)?
- The duplicated block in the hook copy and `reads.py` still identical; the README's apply and rollback steps enough
  for the operator.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree; run nothing that writes (tests read-only, `-p no:cacheprovider`, through the
  heavy slot, your real HOME). Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words.
- **Your record is your session's final message**, in full (the launcher keeps it; the CTO transcribes it): the twelve
  labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per line, every finding with its two
  lines and `scope: in|out`, and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R2-F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S2", "S3"]}`.

## Round 1's findings, as written

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

