# The sets-root guard (DEC-1082 (3), DEC-1097 (2)): the rehearsal of the rebuild, 2026-11-08

## The line rule's run (readiness review 5 F1; the CTO's option A), 07:04–07:13 GMT: the record
`rehearsal.log` beside this file is this run's: every step in order, from a fresh `env -i` shell, **0 failures**. The
rest of this file (below "The first clean run") is the rebuild's run of 01:19–01:29, before the line rule; its log is
kept beside it as `rehearsal-before-line-rule.log`.

**What changed:** `pretooluse.candidate.py` gains `sets_line_refusal` (DESIGN.md §F), called after the judge for the
six refused roles on Bash lines; `guard4_check.candidate.py` gains V1–V25 (the reviewer's forms and more: a variable,
`cd`, `find -exec`, `os.path.join('…','fresh-80')`, a glob, `$(…)`, a backtick, a brace, `env -C`, `HOME=`, `$_`,
`export`, a `for` loop; `~`, `$HOME` and absolute forms) and A1–A23 (every command of `drafts/fresh80/README.md`, steps
0 to 8, in the `~` form and with the root and HOME spelled absolute), for the CTO and a lead. M4, M6, M7, B14, F22 and
F23 now expect deny.

| File | sha256 (first 12) |
|---|---|
| `pretooluse.candidate.py` | `bd545af83198` |
| `pretooluse.diff` (232 lines) | `b948e7ac831d` |
| `guard4_check.candidate.py` (`CASES`: the 70, equal to the live check's; 527 sets cases) | `ff5321041613` |
| `apply.sh` (AFTER_HOOK updated; everything else as below) | `472bc1c1d226` |
| `rehearse.sh` (override_off now expects 8) | `1da7f7a43643` |
| `path-map.patch`, `optin-lifted-guard.patch`, `replay_sets.py` | unchanged (below) |

| Step | Result |
|---|---|
| Clone | at `91cf43d985c6` (w2/integrate), 86 branches, 0 root mentions left |
| Suites before / after | `test_guard_fix_4.py` 467 passed; `test_g14.py` 151 passed, 1 skipped; the same |
| W2-84 before / after | 7 present → 0; nothing left names them; `test_optin_lifted.py` 16 passed both; 9 → 0 list lines |
| `apply.sh check`, `apply` | every hash as built; applied |
| **R2** | **527 run, 0 failed, PASS** |
| **R1** | **501 run (70 + 431), 0 failed, PASS**; 96 naming `~` or `$HOME` run in R2 |
| **R1, L cases only** | **370 run, 0 failed, PASS**; on the live tree after the ACT, 453 (these 370 plus the 83 L cases naming `~` or `$HOME`) |
| Override switched off | exactly 8 fail: X1, X2 (engineer, CTO) and A7/A7abs, the README's `bash tools/proc.sh wait --max 3600 $(cat ~/gov-os-runs/fresh-80/measure.pid)` (CTO, lead). M6 and M7 no longer need it: the line rule refuses them |
| Measure check | orchestrator all False, engineer all True |
| `apply.sh undo` | every file byte for byte, modes kept; `git diff` clean |
| Live files and the real root's entry | **unchanged** |
| Replay | 9,429 unique calls: 9,396 allow→allow, 9 deny→deny, **24 allow→deny**, 0 deny→allow |

**The replay's 24:**
- **6 meant** (the hidden rule, as in the first run): `stat` of a hidden file, `repin_gold.py` on hidden folders (4),
  a product-spec `find` of `memory-verdict-2`.
- **6 false (the hidden rule), all about this ACT:** names-only checks of `runs`, `transcripts` and
  `fixtures/evaluation/memory-retrieval/hidden` in the repository, where none exists (2 by the rebuilder, 1 by readiness
  reviewer 5's `git check-ignore -v … transcripts runs`), and 3 of the rebuilder's heredoc bodies quoting the globs.
- **12 by the line rule, none reading a hidden file:** reads of open `runs/` outputs (`w4-e0`, `score-once-replay`, a
  trial) through a variable or `python3 -c` code with `[`, `{` or a glob (6: engineer subagents 4, the CTO 2); two
  `python3 - <<'EOF'` bodies naming the root (engineer subagents); names-only `find … -name "REANCHOR-LOG*"` (2) and
  `ls -d <root>/*/` (1); an auditor's `find` with a variable (1). They are the price of option A: the rule cannot tell
  an open folder built at run time from a hidden one.

**Limits of the line rule:** a root spelled in pieces (`A=~; $A/gov-os-eval`, `expanduser('~') + '/gov-os-eval'`), a
positional parameter before the root (`bash -c '… $1/…' _ <root>`); the in-repo hidden folders keep the judge's
variable limit (readiness review 5 F1: not introduced by the ACT).

---

## The first clean run (01:19–01:29, before the line rule)

`rehearse.sh` ran every step in order, in one run, from a fresh `env -i` shell, 01:19:47–01:29:13 GMT, and ended with
**0 failures**. Nothing live was changed. The 11-06 build, its
rehearsal and its log are kept in `build-2026-11-06/`.

## Why a rebuild
- `apply.sh check` stopped on 11-08 (state "other"). **Only the map had moved**: W2-61h's `evaluation_families`
  (`ab18f6f5b`, 9 lines before `role_paths:`) took it from `cc8139a1c8f4` to `6d79946fdbbd`. The live hook is still
  `e406653ef6c9`, the hash the first build was made against.
- The pin moved from `pin-8284fb408bd4` to `pin-bcea09060ebc` (window 4). Its `gov/guard/` is byte for byte the old
  pin's (`diff -rq`: no file differs; `reads.py` `0d67b0f94f17`), so every name the hook change uses is where the 11-06
  check found it (`_hidden` 470, `_Part` 151, `inside` 182, `held` 203, `listing` 1365, `RUNTIME_REFUSAL` 101, the
  `[["cat", "--"]]` stand-in 1327/1332, `_related` 283, `_paths_ok` 405, `load_yaml_unique` 29). The pin's
  `config/loader.py` did change; the patched map still passes `load_config`, `check_sets` and `role_reads.section`.
- DEC-1097 (2) adds two things: the glob `runs/fresh-80/**`, and W2-84's hidden-half test cases deleted with the ACT
  (DEC-1061 (4)).

## The files
| File | sha256 (first 12) | What |
|---|---|---|
| `pretooluse.candidate.py` | `42749e673c50` | **unchanged**: the live hook (`e406653ef6c9`) with spec B; regenerating the diff gives the same bytes |
| `pretooluse.diff` | `892acd89715b` | unchanged, 158 lines |
| `path-map.patch` | `8deead873070` | the block after line 553 (the end of `role_paths:`), with `runs/fresh-80/**`; the map goes `6d79946fdbbd` → `a9d8b97267c4` |
| `optin-lifted-guard.patch` | `676014ab259d` | **new**: `tests/optin-lifted-guard.txt` loses W2-84's 7 lines, the "Decision 4" header and the `hidden-half` tag line; `98f3b69a8ed9` → `868b6e1c8464` |
| `guard4_check.candidate.py` | `df97f76dbbeb` | the 70 existing cases (`CASES` compared equal with the live check's), the 194 sets cases of 11-06 unchanged, and 171 new F cases: 365 sets cases |
| `apply.sh` | `97e1a54c65ba` | `check`, `apply`, `undo` of the three files and the seven deletions, with backups and sha256s |
| `rehearse.sh`, `replay_sets.py` | `c7060cc521bc`, `09313e0a23a6` | the rehearsal and its replay (`runs/fresh-80` added to the replay's hidden folders) |

**W2-84's deletions (DEC-1061 (4)).** `apply.sh` checks each file's hash, backs it up under `backup/del/`, deletes it,
and `undo` restores it byte for byte with its mode:
- `tests/acceptance/W2-84/test_w2_84_code_under_test.py` `5c30ab77becb`, `test_w2_84_every_tree.py` `0c6b02904b89`,
  `test_w2_84_fails_closed.py` `ef6c3dcb0f3e`, `test_w2_84_git_store.py` `789d7f768267`, `test_w2_84_links.py`
  `e268aba3aadd`, `test_w2_84_unchanged.py` `54ffe7787356`;
- `tests/unit/guard/test_w2_84_trees.py` `ac2dbd7398a6`. All 13 of its test functions (34 cases) test the old
  hidden-half rule under every tree (trees, links, the shared store, git routes, fail closed, the unmeasured session's
  cost), so the whole file goes.
- Nothing else names them: `git grep` for `test_w2_84`, `w2_84_support` and `acceptance/W2-84`, outside the folder, finds
  only the list's lines before and **none** after (docs, tickets and orchestration records, which cite them as history,
  aside).
- **Left on disk:** `tests/acceptance/W2-84/README.md` (its KPI map), `conftest.py` and `w2_84_support.py`. They are not
  cases and serve only the deleted ones (for the CTO, §"For the CTO").

## The new cases (F1–F23, 171 in all over the roles)
- **Refused** (every measured role M, or engineer/research/orchestrator): a Read, `cat`, `head`, `ls`, Grep and Glob of
  `runs/fresh-80/...` (L, names that do not exist), and of the planted `USED`, `rows/q01.json`, `kept-1/k01.json` (R);
  `grep -rn` and Grep over `runs/` (it now holds a hidden folder); Write, `cp`, `mkdir … && :>` and `echo >` into it.
- **Open:** `runs/fresh-80b/`, `runs/e0/`, `runs/fresh-80.txt`, `runs/` itself (Read, `cat`, `ls`, Grep), a Write to
  `runs/zz-guard4-e0/`; and every case for the sessions no rule names (no `GOV_ROLE`, ticket-lead, reviewer).
- **The CTO's fresh-80 lines, allowed** (the CTO and a lead): `python3 <script> --sets-root ~/gov-os-eval` (also with
  `--dry`, `"$HOME/gov-os-eval"`, redirections, `env -u GOV_TICKET GOV_ROLE=orchestrator`), the same with the absolute
  root, the measure's `memory-verdict-2 --sets-root <root> --part hidden`, and the root-only line with the planted 80
  present (R).
- **Refused for the CTO:** a line naming `runs/fresh-80/...` (`--rows`, `--out`, `ls …` after `&&`, `test -e …/USED`)
  or `memory-verdict-2/...` (`--set`, `--questions`), in `~`, `$HOME` and absolute forms.
- **A known limit, written as a case (F22, F23: allow):** `GOV_KEEP=<root>/runs/fresh-80/kept-… python3 <script>`. The
  judge does not read a variable assignment's value as a path, and only writes it can resolve are judged (W9's rule).
  The shell reads nothing there. My first draft expected deny; the first run showed allow, and the case states it.

## The results
| Step | Result |
|---|---|
| Clone | `--no-hardlinks` clone at `3552f0f59bb7` (w2/integrate; the three files and the seven unchanged since the build), 86 branches, 0 root mentions left; the old-map worktree has no block |
| Planted root | `~/gov-os-runs/SETS-rehearsal/home/gov-os-eval`: 14 dummy files (the 11-06 ten plus `runs/fresh-80/USED`, `rows/q01.json`, `kept-1/k01.json`, `runs/e0/counts.txt`), no `.git` |
| Suites before | `test_guard_fix_4.py` 467 passed; `test_g14.py` 151 passed, 1 skipped |
| W2-84 before | 7 of 7 present; only the list names them; `test_optin_lifted.py` 16 passed; collection of `tests/acceptance/W2-84` + `tests/unit/guard` with `--optin=lifted`: 1,448 |
| `apply.sh check`, `apply` | every hash as built, both patches give their hashes; applied; 10 files backed up with `SHA256SUMS`; the patched map loads |
| **R2** (HOME substituted, the block as applied, `GUARD4_ONLY=sets`) | **365 run, 0 failed, PASS** |
| **R1** (the registered line, the block's root planted) | **409 run (70 + 339), 0 failed, PASS**; 26 cases naming `~` or `$HOME` run in R2 instead |
| R1, L cases only (what the live tree runs after the ACT) | **310 run (70 + 240), 0 failed, PASS** |
| Override switched off | exactly the 6 it exists for fail (M6, M7; X1, X2 for the engineer and the CTO); no F case needs it |
| Suites after | `test_guard_fix_4.py` 467 passed; `test_g14.py` 151 passed, 1 skipped (the same) |
| W2-84 after | 0 of 7 present; `git status`: 7 `D`, the list `M`; **nothing left names them**; `test_optin_lifted.py` 16 passed (its check that every list entry exists); collection 1,085 (363 fewer: 329 + 34), no error; 0 W2-84 or `hidden-half` lines in the list |
| The operator's staging lines (§3) | `git add` of the three files and `git rm` of the seven: 10 files staged (3 M, 7 D), 129 insertions, 889 deletions; then unstaged (no commit in the rehearsal) |
| Replay | 9,116 unique calls of the last 48 hours: 9,098 allow→allow, 9 deny→deny, **9 allow→deny**, 0 deny→allow (below) |
| Measure check | `_measured` per set: `GOV_ROLE=orchestrator` all False; `GOV_ROLE=engineer` all True (the control) |
| `apply.sh undo` | from the applied state: the three files back to their before hashes and the seven restored, each `cmp` equal to its backup with its mode; `git diff` clean |
| Live files | the hook, the map, the list, the seven, `settings.json` and `settings.local.json` hashed before and after; the real root's entry (inode, size, mtime, ctime): **unchanged** |

A first run (01:08–01:17, kept in the scratchpad, not here) had 2 case failures (the `GOV_KEEP` forms, now F22/F23) and
1 check of my own that was wrong (it tested `cut`'s exit status, not `git grep`'s); its measure, undo and live checks
matched this run, and its replay found 8 of the 9 below (the ninth is a call made after it). Both were fixed, and the clean run above is the record.

## The replay
- **Source and method:** as on 11-06 (tool-call inputs only, never a result; every spelling of `~/gov-os-eval` rewritten
  to the planted root, the main tree to the clone; each call judged by the hook as it is and by the candidate). 9,518
  calls, 366 duplicates, 36 skipped (they name the real root in a form the rewrite cannot place), 9,116 judged, 151
  naming the sets root.
- **No call that does not name a hidden folder changed.**
- **The 9 that the change refuses:**

| Cause | Calls | What they are |
|---|---|---|
| Meant | 6 | the CTO's own work on hidden sets (roles inferred): `stat` of a hidden file, `repin_gold.py` on hidden folders (4), and a `find` of `memory-verdict-2` by a product-spec session. The rule exists to refuse these. |
| False, this session's own calls | 3 | (a) `ls -d runs transcripts; git ls-files 'runs/*' 'transcripts/*'` in the repository: names only, of folders that do not exist there; refused because the globs hold in every tree, as designed on 11-06. (b), (c) two heredoc bodies that quote the block's globs as text (`cat > block.yaml <<'EOF'`, a `python3 - <<'EOF'` edit script). The same class as 11-06's four: words inside a body. A document that quotes these paths is written with the Write tool, not a heredoc. |

**No call naming `runs/fresh-80` existed in the window** (the 80 has not run), so the replay shows only that other `runs/`
calls (the CTO's E0–E5 results) stay allowed.

## For the CTO
1. **The three leftovers in `tests/acceptance/W2-84/`** (`README.md`, `conftest.py`, `w2_84_support.py`): delete them in
   the same commit (three more lines in `DEL`, a re-hash and a short re-run of the W2-84 steps), or leave them.
   `gov accept` for W2-84's ticket would now find a KPI map whose cases are gone; the ticket is closed.
2. **The fresh-80 scripts** must take only `--sets-root` on the line and derive `memory-verdict-2` and `runs/fresh-80`
   (and the `GOV_KEEP` folder) in their own code; check `USED` themselves; and print every count the CTO reads. A
   `test -e`, `ls` or `cat` of `runs/fresh-80/...` from the CTO's shell is refused.
3. **The live check after the ACT:** copy `guard4_check.candidate.py` over `tools/guard4_check.py` and run it on the live
   tree with no `SETS_PLANTED`: expected **331 run, PASS** (the 310 above plus the 21 L cases that name `~` or `$HOME`,
   which run when the root is `~/gov-os-eval`).

## Limits
- As on 11-06: the real sets root's contents were never opened or listed (only its entry); its map was not read (the
  planted map is a stub that copies the repository's `evaluation_sets`); the replay's roles are inferred from each
  session's first message.
- **The writer-session check was not repeated** (a headless `claude -p` session): nothing it showed depends on the map or
  the new glob. The step is kept in `rehearse.sh`, out of the default list.
- The guard walks a hidden part for names when a search starts at or above it, and fails closed above 10,000 files
  (`_MOST_FILES`); `runs/fresh-80` holds far fewer.
