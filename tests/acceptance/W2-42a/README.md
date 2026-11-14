# W2-42a acceptance tests: the product's guard reads what a Bash command writes, replayed on every logged refusal

Ticket `DAEO-03ub` (W2-42a), profile FULL. Written by an independent test designer before implementation (MR-3),
from the ticket's 11 success and 2 failure KPI lines, DEC-1040 item 2, DEC-1028 item 4, DEC-958, DEC-953 item 2,
the package `P1-GUARD-PARSER-W2` and ACT-GUARD-FIX-3 §7, against the base `w2/integrate` at `a58ba344`. The
engineer's worktree and branch were not read (DEC-820 (c)).

Run from the tree under test (through the gate, DEC-1038 (4)):

```
cd <tree> && TMPDIR=/tmp/gov-os-emg-<name> PYTHONPATH=<tree>/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-42a -q -n auto -o tmp_path_retention_policy=failed -p no:cacheprovider
```

885 cases in seven files (the 452 of the first design, td-2's 41, td-4's 312 and td-5's 80, below). The replay and the planted cases run the hook once each (about 1 to 3 s a call: the
hook lists every worktree for rules 2 and 5), so run with `-n auto`.

## What judges what

- **The write parser:** `gov.guard.decide._extract_bash_write_targets(command, cwd)`, as `gov.guard` exposes it
  today (the ticket names it): a list of real paths, `/<guard-unresolvable>` among them for a write it cannot
  resolve, or `None` for no write. The cases run in a `tmp_path` of their own, with none of the session's variables
  and none of the command's own variables set, so a target is resolved only from the command's text.
- **The read judge:** `gov.guard.reads.policy_refusal("Bash", …)` (which runs `_set_aside` and
  `_Judge.tool`/`command`), for a research session in a project of the case's own whose evaluation set measures
  research and whose hidden part holds a file, so the listing rule ("the call reads files whose names another
  command gives at run time …", DEC-820 (d)) is live, as for the sessions it refused. `HOME` is the case's own.
- **The hook:** the reviewed `drafts/act-guard-fix-3/pretooluse.py` with `bash_writes.py` beside it, copied to
  `fixtures/hook/` (SHA-256 first 12: `b7e96a89d092`, `df7be57c6bdd`; the same as the live `.claude/hooks/` on
  2026-11-02), run as `python3 fixtures/hook/pretooluse.py` with `PYTHONPATH=<tree>/src`: the five-rule hook as it
  runs once this tree is pinned (re-pin window 2). Event JSON on stdin (`tool_name`, `tool_input`, `cwd`,
  `agent_type`); `GOV_ROLE`, `CLAUDE_PROJECT_DIR` and `TMPDIR` in its environment. No output and exit 0 is allow;
  a JSON `permissionDecision` is the answer; exit 2 (an error) is a refusal by no rule, which no case accepts.

## The fixtures

- **`fixtures/refusals.json`** (built by `tools/build_refusals.py` from the CTO's `log/guard-refusals.jsonl`, 80
  lines on 2026-11-02 at 20:22): for each line with a tool-use id, the full tool input from the `tool_use` block of
  that id in the line's transcript; the tool; the cwd (the transcript entry's); the project folder (the worktree the
  cwd lies in, else the main tree); the session's role (a main session: the role of its launch folder
  `gov-launch-<role>-<id>` when its own scratchpad lies in one, else `orchestrator`, as the CTO and the leads run;
  a subagent: its parent's role so found, and its type from its `.meta.json` as `agent_type`); the launch folder as
  `TMPDIR`; the verdict; the rule that refused it.
  - **Recovered: 76** (74 judged false, 2 judged true: line 74, a hidden-part read; line 77, a reviewer's Write).
  - **Left out: 4**, lines 51 to 54: summary rows with no tool-use id (each summarises a later row of the same
    session, ACT-GUARD-FIX-3 §2: lines 55, 56, 59, 60, which are replayed).
  - **Secrets:** gitleaks (`gitleaks dir <file> --no-banner --redact`) found none in either fixture; nothing was
    replaced. (`planted.json` was scanned before its `base_caught` booleans were added.)
- **Stand-ins for vanished worktrees** (`w2_42a_support.replayable`, td-1, 2026-11-13): 33 of the 76 rows name a
  project folder that has since gone (W2-16, -64, -67, -76, -84, -90, -95, -96, -107, -112: landed, worktrees
  removed). The hook reads its project folder for the held-out list, the hidden globs, `tree_roots` (the tree's
  worktrees and its `origin`), the ticket and the acceptance folder, so a missing folder, or an unrelated one, is not
  its judgement of the logged call. For each such folder the fixture makes one stand-in: a `git clone --shared` of
  the tree under test, checked out detached at its HEAD, named as the vanished folder, with the tree under test as
  `origin` (so `tree_roots` reaches the same worktree list as from the logged tree). A clone, not `git worktree add`,
  because the clone writes only under the run's own tmp folder (a worktree would add an entry to the main
  repository's `.git/worktrees`, which the sandbox keeps read-only). The vanished path is replaced by the stand-in's
  in the row's `cwd`, `root`, `tmpdir` and every string of `input`, only where it stands whole (`W2-95` never matches
  inside `W2-95-tests`); the worktrees folder that held it, named as itself (`find /home/usain/gov-os-worktrees …`,
  line 74), becomes the stand-ins' folder; and the logged `cwd` is made inside the stand-in, since the session ran
  there. Each stand-in also holds a placeholder file of its own (`stand-in.txt`, never the hidden half's contents) in
  each evaluation set's hidden folder named in its path map. A tree of the logged time held those parts on disk, and
  line 74's logged rule is a read of one. Today no tree does (moved to `~/gov-os-eval`, DEC-1070). Rule 2 judges a
  listing by what it reaches, so without the placeholder line 74 is allowed even with a root that still exists. Role,
  agent type, verdict, rule and the hook are the row's and unchanged; rows whose folder exists run as before. One
  stand-in per folder serves all of a run's workers (made once, by an atomic rename, under a shared lock) and the
  last worker removes them. No row is skipped. A planted parser change that refuses line 40 (`rm -f chain-*.json`,
  root W2-16, a stand-in row) fails the case, so the substitution does not make it vacuous.
- **`fixtures/planted.json`** (built by `tools/build_planted.py` from the reviewed `test_guard_fix_3.py`,
  `b6f8216c97bc`): 155 cases the hook must refuse: ACT-GUARD-FIX-3's 137 planted writes and unknown forms (rule 1,
  acceptance folder; rule 5, outside a reviewer's record; its one key-read case, rule 3, left out), its logged pattern
  left refused by design (row 46), and guard4_check.py's 17 planted writes of rules 1 and 5. Row 39's pattern (an
  unmatched glob in `/tmp`) is left out: KPI line 4 makes it pass. The main tree's path is written `{ROOT}` and
  replaced by the tree under test. `base_caught`: whether the base's parser catches each Bash case (computed on
  `a58ba344`, for failure line 1).
- **`fixtures/f1_shell_options.json`** (td-2, 2026-11-13; the FULL review's finding F1, round 1, with F4's
  `/dev/stdin` ride-along): a shell that reads its commands from standard input is a shell whatever options it is
  given, so its heredoc body is commands. 19 plain-data cases `{id, command, expect, targets_include, note}`: 15
  spellings that must give the body's writes (`bash -euo pipefail`, `-e -u -o pipefail`, `-eu -o pipefail` unquoted,
  `sh -o errexit`, `-O extglob`, `+o posix`, `--noprofile --norc`, `--rcfile f`, `cat <<'EOF' | bash -o pipefail` and
  `| bash -euo pipefail`, `-s`, `/dev/stdin`, `/dev/fd/0`, an unknown `--some-new-flag` read as a shell (fail closed),
  and the auditor's `sed -i …; cp …` body) and 4 kept-as-data controls (`cat`, `tee f`, `grep -e x`, `bash script.sh`).
  Paths are relative to the case's folder; the JSON names no secret and no hidden folder, and is meant to be reused
  to check the live hook's own fix. `test_w2_42a_f1_shell_options.py` drives it through the product: the write parser
  (each target or the unresolvable target; a control gives its own targets only) and the read judge (the same head
  with a body naming the case project's hidden file is refused under a shell, not refused as data). Its two hook-level
  cases judge the hook fixture, which has the same gap and is not changed here: they are `xfail(strict=True)` and in
  no KPI row; strict so that they fail loudly (XPASS) the moment the hook is fixed by ACT-GUARD-FIX-5
  (P1-GUARD-HEREDOC-OPTS-1), whose companion removes the marks (td-3, the CTO's request of 2026-11-13). **Red on `e9e4f7bac`: 24 failed, 15 passed, 2 xfailed**: 12 spellings fail on both sides (no write, no
  read); `--noprofile --norc`, `-s` and the unknown flag, the 4 controls on both sides and the data-file check pass.
- **`test_w2_42a_apostrophe.py`** (td-4, 2026-11-13; the reopen under DEC-1164 (18), DEC-1174 (1), Rewrite-Reason
  DEC-1174 (1)): an apostrophe in a comment of a shell's heredoc body is no quote. Each case asks the product guard
  itself, `gov.guard.decide.decide("Bash", {"command": …}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")`, in
  a `tmp_path` project of its own: an in-progress engineer ticket `DAEO-03ub` allowing `src/**`, so a write under
  `src/` passes and a refusal of `T` = `tests/acceptance/X/zz.py` is about `T`; no session variable, its own `HOME`.
  The heads are the F1 fixture's `bash -euo pipefail`, `-o pipefail`, `-O extglob`, `--rcfile f`, `/dev/stdin`,
  `cat <<… | bash -o pipefail` and plain `bash`, each with a quoted and an unquoted delimiter (14). (a) a harmless body
  with an apostrophe comment (`# don't overwrite` / `echo hi`, `# it's fine` / `ls`, a trailing and an indented
  comment) is allowed, also when the call then writes `src/ok.py` (70). (b) the call then writing `T` by `> T`, `cp`
  or `python3 -c` is refused (42), and ACT-GUARD-FIX-5 round 2's four F1 reversal calls by name (4). (c) a body
  writing `T` after such a comment (28); a write of `T` between two apostrophe comments (42); the comment drop's
  edges, each a body line writing `T`, with and without an apostrophe comment above (`a#b`, `${#v}`, `${v#a}`, `$#`,
  `#` inside double and single quotes, `"it's # here"`, a comment after the write; 64): all refused. (d) a real
  unclosed quote outside a comment, also after an apostrophe comment, after `a#b` and after `$#`, is refused (20).
  Controls (42, green on the base): the same bodies without the apostrophe are allowed; without it a write of
  `src/ok.py` passes and a write of `T` is refused naming `T`. **Red on `d73bd2756`: 120 failed, 192 passed**: the
  70 (a) cases, each refused "the command cannot be read, so it is not known to be free of the lift form of gov pause
  (--off)" (`lift_refusal` in `decide.py` reads the body as shell); and 50 cases the base **allows** (a fail-open):
  the 42 writes of `T` between two apostrophe comments, the 4 edges with a comment after the write below an
  apostrophe comment, and the 4 unclosed quotes after an apostrophe comment. Read as text the two apostrophes pair
  into one quote and hide what lies between; a shell reads both as comments and runs it. The other 142 pass.
- **`test_w2_42a_apostrophe_2.py`** (td-5, 2026-11-13; the narrow check's F1 and F4 and departure 1, the CTO's
  P-03ub-APOS-3 (1) and P-03ub-APOS-4 (a), DEC-1174 (1), Rewrite-Reason DEC-1174 (1), APOS-3/APOS-4): the same `proj`
  and `decide` call as td-4's file, `T` = `tests/acceptance/X/zz.py`, `A` = `src/ok.py`. Every form was first run
  through real bash in a scratch folder: each write named is one bash performs. (F1) a `#` inside `${…}` never starts
  a comment: 8 forms (`${v%% #*}` of a quoted value, `${x:- #a}; echo x > …`, `${v/ #/}`, two `while read` loops,
  an allowed write then `cp x.py …`, the double-quoted and the nested form), each at the top level, as a
  `bash <<'EOF'` body and inside `bash -c '…'`: writing `T` refused naming `T` (24), writing `A` allowed (24); the
  forms that never were comments (`${#v}`, `${v#a}`, `$#`) in the same three places, `T` refused and `A` allowed
  (9 + 9); `echo hi # it's fine` allowed, `echo hi > T # it's fine` refused. (F4) `grep -c b <<< "a # b"`,
  `wc -w <<< "one # two"`, `jq -r '.x' <<< '{"x": "a # b"}'` allowed; `grep -c …`/`tr a b <<< 'x # y'` writing `T`
  refused with a reason naming `T`, not "cannot be read", and writing `A` allowed. No `bash <<< "…"` case (out of
  scope). (dep1) a standalone `python3 -c` write of `T` refused, of `A` allowed, three read-only one-liners allowed.
  **Red on `692bc41bd`: 28 failed, 52 passed**: 21 F1 writes of `T` allowed (a fail-open), 7 F4 cases refused "the
  command cannot be read"; the double-quoted F1 form is green on the head in all three places.
- **`test_w2_42a_here_string.py`** (td-6, 2026-11-14; the CTO's reopening under DEC-1164 (18) for R3 and the fallback's
  here-string fail-opens, DEC-1028, DEC-958): bash takes `<<< word` anywhere in a simple command; the word is the
  here-string's text and the words after it stay the command's arguments. The same `proj` and `decide` call as the
  apostrophe files, `T` = `tests/acceptance/X/zz.py`, `A` = `src/ok.py`; every form was run through real bash. (R3, 12
  cases) a write argument after a here-string (`tee <<< "x" W`, `tee -a`, `cp <<< x x.py W`, `tee … W; echo done`,
  `echo a && tee <<< "$v" W`): `T` refused naming `T` (5), `A` allowed (5); `cat <<< "x" > W`: `T` refused, `A`
  allowed. (fallback, 10) `bash <<< 'touch W'`, `sh <<< 'touch W'`, `xargs touch <<< W`: `T` refused (3), `A` allowed
  (3); `bash <<< "$X"` and `sh <<< "$(cat x.py)"`, text the guard cannot know, refused (2); a `python3 -c` write of `T`
  then a body-less `cat <<EOF` or `cat <<'EOF'`, refused (2). (read-only, 9) `grep -c`, `wc -l`, `tr`, `cat`, `read`,
  `grep`/`cat` whose text names `T`, `bash <<< 'echo hi'`, `sh <<< 'ls src'`: allowed. **Red on `d3ba8e50b`: 12 failed,
  19 passed.**
- **`test_w2_42a_here_string_ro.py`** (td-8, 2026-11-14; the narrow check's R3 F1, the CTO's F1 (a), DEC-1164 (18),
  Rewrite-Reason DEC-1164 (18), W2-42a R3 F1): the read-only here-string forms with an expanded text (`"$v"`,
  `"$(…)"`). The decided rule: `read`/`mapfile`/`readarray` and a loop's here-string are data, whatever the text;
  `sed`, `awk` (a script without `>`/`system(`), `bc`, `grep`, `wc`, `cut`, `tr`, `sort` take an expanded text as data;
  the loop body's commands and every redirect are judged by their own words; `bash`/`sh`/`zsh`/`dash`/`xargs`/
  `source`/`eval` and any reader not named keep R3's fail-closed rule. The same `proj` and `decide` call as td-6's file,
  `T` = `tests/acceptance/X/zz.py`, `A` = `src/ok.py`; every form was run through real bash (each write named is one bash
  performs; each RO form writes no file). (RO, 18 cases) `read -r a <<< "$v"`, `IFS=: read`, `read` of `$(git rev-parse …)`,
  `v=$(git log -1); read`, `mapfile -t`, `readarray -t`, `while read … done <<< "$(git status --porcelain)"`, `sed`,
  `awk '{print $1}'`, `bc`, and three variants (`read -ra`, `until read`, `while IFS= read`): allowed (13); `grep`, `wc`,
  `cut`, `tr`, `sort` over an expanded text: allowed, guards green today (5). (RW, 18 cases) nine forms with a write:
  `read … > W`, `mapfile …; touch W`, `while read …; do touch W`, `while read …; do cp "$f" W`, `sed … > W`, `sort -o W`,
  `read <<< "$(touch W)"`, `while read … <<< "$(touch W)"`, `sed … <<< "$(touch W)"`: `T` refused naming `T` (9), `A`
  allowed (9). (FC, 17 cases) `bash`, `sh` (a substitution), `zsh`, `dash`, `xargs touch`, `source /dev/stdin`,
  `. /dev/stdin`, `eval "$v"`, `python3`, `perl`, `awk … | sh`, a loop body `bash -c "$f"` and `eval "$f"`: refused (13);
  an `awk` script with `>` or `system(`, `sed 'w …'`, `sed -i` writing `T` over a here-string: refused (4); the `A`
  forms of those writing scripts are not pinned (refusing them as unreadable is allowed). **Red on `209ec8464`: 21 failed,
  32 passed.**
- **`test_w2_42a_here_string_ro_2.py`** (td-9, 2026-11-14; R3 F1 second batch, the lead's finding at `885b0d0f6`,
  DEC-1164 (18), Rewrite-Reason DEC-1164 (18), W2-42a R3 F1): a here-string read as data must not hide a command it
  feeds. Taking the text as data is safe only while it is not run; bash runs it when a variable `read` bound from it is
  used as a command's name, and when `mapfile`/`readarray` has a callback (`-C cb`, `-tC cb`, run per `-c n` lines).
  The same `proj` and `decide` call as td-8's file, `T` = `tests/acceptance/X/zz.py`, `A` = `src/ok.py`; each refused form
  with a literal `touch T` text or callback was run through real bash and wrote `T` (the `"$v"` forms with
  `v='touch T'`; `"$f" x` with `v` a script path touching `T`). (V, 13 cases) `while read -r f; do $f; done <<< 'touch W'`,
  `while read -r a b; do $a $b`, `read -r a b <<< 'touch W'; $a $b`: `T` refused (3), `A` refused too, as the guard
  cannot know the command (3); `"$v"` forms `read -r a b … ; $a $b`, `read -r a …; $a`, `${l}`, `"$f" x`, `env $f`,
  `command $f`, `time $f`: refused (7). (CB, 4 cases) `mapfile -C 'touch T' -c 1` and `readarray -tC 'touch T' -c1`:
  refused (2; the `A` forms are not pinned); `mapfile -C cb`, `mapfile -t -C "$cb"`, a callback the guard cannot know:
  refused (2). (G, 6 cases) `while read … echo "$f"`, `read … ; echo "$a" "$b"`, `printf` over a porcelain listing,
  `mapfile -t L <<< "$(ls)"`, `readarray … echo "${L[0]}"`, `grep -c x "$f"` over a listing: allowed, a variable used as
  data and not as a command name (all six allowed at the base). **Red on `885b0d0f6`: 17 failed, 6 passed.**
- **`test_w2_42a_r4_blob_refs.py`** (td-10, 2026-11-14, R4 R5, Rewrite-Reason DEC-1157 (12), W2-42a R4 R5; the CTO's
  reopening for R4 (D1) and the R4/R5 failure line, DEC-1157 (12), DEC-1180 (4), DND row 122): a revision-colon-path
  naming a blob is judged as a read of that path. A planted repository per module (`git init` under `tmp_path`): two
  commits (`docs/a.md` changes), a branch `feature`, `docs/a.md`/`docs/b.md`, a hidden-part file of a set measuring
  `research` and `engineer`, a `.env` stand-in (no secret), the engineer's own `tests/acceptance/W2-42a/x.py`, the
  ticket DAEO-03ub (engineer, `src/**`) and a held-out list naming a second repository outside the project. Every form
  was first run through real git (the file's docstring says what git does with each: a one-sided `git diff REV:PATH
  FILE` diffs the blob against the file; `--no-index` with a blob fails; `nosuch:…` and `HEAD:docs/missing.md` fail
  with exit 128). Each case asks the read judge as the live hook calls it (`reads._Judge(root, reads.parts(…)).tool`,
  any exception = rule `error`) and the product (`decide`; rule `error` = raised, the catch-all, or a `PolicyError`
  turned into "…: the call is refused (fail closed, DEC-820)"), and a few the hook fixture. (G1, 15 + 1 + 1 cases)
  two-sided blob diffs of visible paths (HEAD/HEAD, parent/HEAD, an abbreviated hash and a branch, `main~1`/`main`,
  `HEAD:./a.md` from `docs/`, after `git -C <root>`) allowed (6, red), an engineer's (1, red), through the hook (1,
  red); `git show REV:PATH` (HEAD, a hash, a branch, two blobs, after `git -C docs`), the one-sided diff against a
  file and `--stat` stay allowed (8, guards). (G2, 12) the hidden part, a secret and the engineer's own tests named in
  a blob ref, refused by that rule's own text. (G3, 6) a revision word naming nothing, or a path missing in the
  revision, refused by a ruled refusal. (F3, 21) held-out (after `git -C <held-out repo>`, or its path named in the ref),
  secret, hidden (also as tree refs holding the part) blob reads, and a blob diff whose output goes into
  `tests/acceptance/X/zz.txt` (`>`, `>>`, `| tee`, `| tee -a`) for the engineer: refused today, still refused (any
  rule, never an exception), through the product and the hook.
- **`test_w2_42a_r5_error_path.py`** (td-10, 2026-11-14, R4 R5, Rewrite-Reason DEC-1157 (12), W2-42a R4 R5; R5, DND
  row 123, DEC-1128 (3), DEC-1133 (2)): the judge never raises; its error path stays for a genuine fault. The crashing
  forms were looked for by reading `reads.py`, `decide.py`, `heldout.py`, `install.py` and `protected.py` at every index
  into a word, token or split list, and by a seeded sweep (the file's docstring names each function read). Found: every
  such index on those paths is guarded, so the ticket's named forms are **ruled on the base** (kept as guards); the
  judge **raises** `PolicyError(_REV_FAULT)` for a revision it cannot classify (`_Judge.patched`, `_Judge.ask`); and
  `decide()` **raises** for a Write/Edit whose path holds a NUL byte or is not a string. (named, 108 + 27 + 10) empty
  words, a lone `;`/`&&`/`|`/`&`/`||`, a trailing pipe/`&&`/`;`/`||`, an option with no value (`git -C`, `git diff -U`,
  `git show --format`, `git log -n`, `git --git-dir`, `cd -`, `find -name`, `grep -e`, `sed -i`, `xargs -I`,
  `cp -t`), an unterminated `$(`/backtick, each plain, after a `cd`, inside `$(…)` and after `git -C docs`; for an
  engineer; ten through the hook: ruled (guards). (revision, 18 + 3) `HEAD:`, `:`, `^`, `:/`, empty quoted paths, an
  unset variable, a `$(…)`, `--stdin`, unknown revisions and ranges, words taken for revisions, after a `cd` and inside
  `$(…)`: ruled (red). (tool inputs, 4 + 13) a Write/Edit whose path is a NUL byte, a number or a list: a ruled refusal
  (red); odd Read/Grep/Glob/Bash inputs: ruled (guards). (property, 1) 1500 token sequences from `random.Random(20261114)`
  through the judge and the product, shrunk and printed on a failure (red). (genuine faults, 4 + 2) git missing from
  `PATH` (the product refuses by the error path, a blob diff is not allowed, the hook exits 2), and a path map that is a
  folder or does not parse (the error path for Bash and Read, the hook exits 2): green, kept. The 20-second deadline is
  not pinned: it is the hook template's `signal.alarm(20)`, outside `src/gov/guard`, and a case would wait 20 s.
- **`test_w2_42a_r4_blob_refs_2.py`** (td-11, 2026-11-14, R4 R5 second batch, Rewrite-Reason DEC-1157 (12), W2-42a R4
  R5; the lead's probe of `eca7a70176de`): a revision-colon-path whose path the guard cannot place, an object named by
  its blob id alone, and git's own `--output` write. A planted repository per module (`git init` under `tmp_path`): two
  commits (the second changes `docs/a.md` only, so the log forms can be limited to `HEAD~1..HEAD` or `-- docs/a.md`),
  `docs/a.md`/`docs/b.md`, the hidden part `fixtures/evaluation/w242d/hidden/**` holding `q01.txt` of a set measuring
  `research` and `engineer`, an empty `tests/acceptance/X/`, the ticket DAEO-03ub (engineer, `src/**`); the ids `SUB`
  (the set's subtree), `HTREE` (the hidden folder's tree) and `BLOB` (the hidden file) named by `git rev-parse`. Every
  form was first run through real git 2.43.0 under `$TMPDIR` (each group 1 and 2 form prints the hidden file's text;
  each `--output` form creates `tests/acceptance/X/zz.txt`; the file's docstring says what git does with each). Each
  case asks the product (`decide`; rule `error` = raised, the catch-all, or a `PolicyError` turned refusal), group 1
  the hook fixture too. (G1, 14 + 7) `git diff SUB:hidden/q01.txt HEAD:docs/a.md` (both orders), `git diff
  HTREE:q01.txt HEAD:docs/a.md`, `git show SUB:…`/`HTREE:…`, `git cat-file -p SUB:…`, `git cat-file blob HTREE:…`, for
  research and engineer: a ruled refusal; through the hook (research): deny. (G2, 4 + 14) `git cat-file blob BLOB`,
  `git cat-file -p BLOB`: a ruled refusal; `cat-file -t/-s/-e BLOB`, `cat-file -p HEAD`, `git show HEAD:docs/a.md`,
  `git diff HEAD:docs/a.md HEAD:docs/b.md`, `cat-file -p HEAD:docs/a.md` stay allowed (guards). (G3, 15 + 3) `git
  diff`/`git show`/`git log -p` with `--output=T` or `--output T`, at the top, after `git -C <root>` from `docs/` and
  after `cd tests &&` with `acceptance/X/zz.txt`, for the engineer: refused by the write refusal naming `T` (resolved
  from the top); `--output=src/out.txt` stays allowed (guards). Left out: `git log -p -1 --output=T` with no path or
  range (refused in the planted repository by the hidden-part read rule, whatever its write) and the guard `git diff
  --output src/out.txt HEAD~0 HEAD` (refused at the head by the revision rule: not green, so no guard).

## The KPI map (read by `gov close`)

S1 to S13 are the ticket's success lines in order, F1 to F3 its failure lines.

| KPI | Tests |
|---|---|
| S1 | `test_w2_42a_parser.py::test_kpi1_a_data_body_for_cat_is_no_write_and_its_quotes_do_not_break_the_reading`, `test_w2_42a_parser.py::test_kpi1_a_data_body_for_tee_is_no_write`, `test_w2_42a_parser.py::test_kpi1_a_data_body_for_grep_is_no_write`, `test_w2_42a_parser.py::test_kpi1_a_quoted_data_body_s_substitution_is_text`, `test_w2_42a_parser.py::test_kpi1_an_unquoted_data_body_s_substitution_is_judged`, `test_w2_42a_parser.py::test_kpi1_a_shell_body_is_judged_as_commands`, `test_w2_42a_f1_shell_options.py::test_review_f1_the_data_file_holds_every_spelling_of_the_finding`, `test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands`, `test_w2_42a_f1_shell_options.py::test_review_f1_a_data_body_stays_data`, `test_w2_42a_apostrophe.py::test_apostrophe_a_a_harmless_shell_body_with_an_apostrophe_comment_is_allowed`, `test_w2_42a_apostrophe.py::test_apostrophe_a_the_call_then_writing_an_allowed_path_is_allowed`, `test_w2_42a_apostrophe.py::test_apostrophe_c_two_apostrophe_comments_do_not_pair_into_a_quote_that_hides_a_write`, `test_w2_42a_apostrophe.py::test_apostrophe_c_a_hash_that_starts_no_comment_keeps_the_write_on_its_line`, `test_w2_42a_apostrophe.py::test_apostrophe_control_the_same_body_without_an_apostrophe_is_allowed`, `test_w2_42a_apostrophe.py::test_apostrophe_control_without_the_apostrophe_an_allowed_write_passes_and_a_write_of_t_is_refused_for_t`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_hash_inside_a_parameter_expansion_with_a_write_of_an_allowed_path_is_allowed`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_hash_that_never_was_a_comment_with_a_write_of_an_allowed_path_is_allowed`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_real_comment_with_an_apostrophe_and_no_write_is_allowed`, `test_w2_42a_apostrophe_2.py::test_apos2_f4_a_here_string_holding_a_hash_that_writes_nothing_is_allowed`, `test_w2_42a_apostrophe_2.py::test_apos2_f4_a_here_string_command_writing_an_allowed_path_is_allowed`, `test_w2_42a_apostrophe_2.py::test_apos2_dep1_a_python3_c_write_of_an_allowed_path_is_allowed`, `test_w2_42a_apostrophe_2.py::test_apos2_dep1_a_read_only_python3_c_one_liner_is_allowed`, `test_w2_42a_here_string.py::test_r3_a_write_argument_after_a_here_string_to_an_allowed_path_is_allowed`, `test_w2_42a_here_string.py::test_r3_a_redirect_after_a_here_string_to_an_allowed_path_is_allowed`, `test_w2_42a_here_string.py::test_hstr_fallback_a_here_string_whose_text_writes_an_allowed_path_is_allowed`, `test_w2_42a_here_string.py::test_hstr_read_only_a_here_string_that_writes_nothing_is_allowed`, `test_w2_42a_here_string_ro.py::test_hsro_read_only_a_reader_of_an_expanded_here_string_that_writes_nothing_is_allowed`, `test_w2_42a_here_string_ro.py::test_hsro_read_only_a_data_reader_of_an_expanded_here_string_stays_allowed`, `test_w2_42a_here_string_ro.py::test_hsro_write_a_read_only_form_that_writes_an_allowed_path_is_allowed`, `test_w2_42a_here_string_ro_2.py::test_hsro2_guard_a_variable_used_as_data_and_not_as_a_command_name_stays_allowed` |
| S2 | `test_w2_42a_parser.py::test_kpi2_a_variable_set_once_at_the_top_before_use_is_expanded`, `test_w2_42a_parser.py::test_kpi2_a_variable_built_from_one_set_before_it_is_expanded`, `test_w2_42a_parser.py::test_kpi2_a_literal_for_loop_s_words_are_judged_one_by_one`, `test_w2_42a_parser.py::test_kpi2_any_other_binding_is_unresolvable` |
| S3 | `test_w2_42a_parser.py::test_kpi3_a_substitution_in_quotes_sh_c_and_eval_are_judged_as_commands`, `test_w2_42a_parser.py::test_kpi3_shell_keywords_are_not_the_command_s_name`, `test_w2_42a_parser.py::test_kpi3_prefixes_are_not_the_command_s_name` |
| S4 | `test_w2_42a_parser.py::test_kpi4_an_unmatched_glob_is_its_literal_path`, `test_w2_42a_parser.py::test_kpi4_an_unmatched_glob_after_a_cd_is_its_literal_path`, `test_w2_42a_parser.py::test_kpi4_a_matched_glob_is_still_its_matches` |
| S5 | `test_w2_42a_parser.py::test_kpi5_the_named_writers_write_their_paths`, `test_w2_42a_parser.py::test_kpi5_git_mv_writes_both_paths`, `test_w2_42a_parser.py::test_kpi5_rsync_writes_into_its_destination`, `test_w2_42a_parser.py::test_kpi5_patch_appliers_write_unresolvable_targets` |
| S6 | `test_w2_42a_read_judge.py::test_kpi6_arithmetic_is_no_command_substitution`, `test_w2_42a_read_judge.py::test_kpi6_a_data_body_naming_a_secret_is_no_read`, `test_w2_42a_read_judge.py::test_kpi6_a_data_body_for_tee_naming_a_key_is_no_read`, `test_w2_42a_read_judge.py::test_kpi6_a_data_body_holding_a_listing_loop_is_no_listing`, `test_w2_42a_read_judge.py::test_kpi6_a_shell_body_is_still_read`, `test_w2_42a_read_judge.py::test_kpi6_an_unquoted_data_body_s_substitution_is_still_read`, `test_w2_42a_read_judge.py::test_kpi6_a_substitution_inside_arithmetic_is_still_read`, `test_w2_42a_read_judge.py::test_kpi6_a_plain_secret_read_is_still_refused`, `test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused`, `test_w2_42a_f1_shell_options.py::test_review_f1_a_data_body_naming_a_hidden_file_is_no_read` |
| S7 | `test_w2_42a_parser.py::test_kpi7_a_continued_word_is_one_word`, `test_w2_42a_parser.py::test_kpi7_a_continued_command_writes_its_target`, `test_w2_42a_parser.py::test_kpi7_a_continued_copy_writes_its_destination_and_nothing_with_a_newline`, `test_w2_42a_parser.py::test_kpi7_a_backslash_newline_inside_single_quotes_is_kept`, `test_w2_42a_read_judge.py::test_kpi7_a_secret_named_across_a_continued_line_is_refused`, `test_w2_42a_read_judge.py::test_kpi7_a_hidden_file_named_across_a_continued_line_is_refused` |
| S8 | `test_w2_42a_parser.py::test_kpi8_a_script_written_then_run_by_bash_is_judged_as_its_code`, `test_w2_42a_parser.py::test_kpi8_a_script_written_after_a_cd_then_run_by_its_path_is_judged`, `test_w2_42a_parser.py::test_kpi8_a_python_file_written_then_run_is_its_code_or_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_the_parser_cannot_read_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_by_a_word_that_does_not_expand_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_written_file_that_is_only_read_is_judged_as_data` |
| S9 | `test_w2_42a_measured.py::test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_measured.py::test_kpi9_the_measures_are_stated_in_the_evidence_file` |
| S10 | `test_w2_42a_read_judge.py::test_kpi10_a_loop_over_seq_reading_a_literal_file_is_judged_by_that_file`, `test_w2_42a_read_judge.py::test_kpi10_a_substitution_that_yields_no_file_name_leaves_the_literal_files`, `test_w2_42a_read_judge.py::test_kpi10_a_python_heredoc_naming_its_files_literally_is_judged_by_them`, `test_w2_42a_read_judge.py::test_kpi10_a_data_heredoc_appended_to_a_record_is_judged_by_its_file`, `test_w2_42a_read_judge.py::test_kpi10_names_given_at_run_time_are_still_judged_as_a_listing`, `test_w2_42a_read_judge.py::test_kpi10_a_literal_hidden_file_is_still_refused` |
| S11 | `test_w2_42a_replay.py::test_kpi11_each_logged_refusal_replayed`, `test_w2_42a_replay.py::test_kpi11_the_replay_holds_every_recoverable_line`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |
| S12 | `test_w2_42a_r4_blob_refs.py::test_r4_a_diff_of_blob_refs_naming_visible_paths_is_judged_as_reads_and_allowed`, `test_w2_42a_r4_blob_refs.py::test_r4_an_engineer_s_diff_of_two_visible_blobs_is_judged_by_those_paths_and_allowed`, `test_w2_42a_r4_blob_refs.py::test_r4_a_show_or_one_sided_diff_of_a_visible_blob_stays_allowed`, `test_w2_42a_r4_blob_refs.py::test_r4_a_diff_of_two_visible_blobs_is_allowed_through_the_hook`, `test_w2_42a_r4_blob_refs.py::test_r4_a_blob_ref_naming_a_path_the_role_may_not_read_is_refused_by_that_rule`, `test_w2_42a_r4_blob_refs.py::test_r4_a_diff_whose_revision_word_names_nothing_is_refused_by_a_ruled_refusal`, `test_w2_42a_r4_blob_refs.py::test_r4_a_show_whose_revision_word_names_nothing_is_refused_by_a_ruled_refusal`, `test_w2_42a_r4_blob_refs_2.py::test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_is_refused_by_a_ruled_refusal`, `test_w2_42a_r4_blob_refs_2.py::test_r4_an_object_named_by_its_blob_id_alone_shown_as_text_is_refused_by_a_ruled_refusal`, `test_w2_42a_r4_blob_refs_2.py::test_r4_a_cat_file_or_blob_ref_that_shows_no_refused_text_stays_allowed`, `test_w2_42a_r4_blob_refs_2.py::test_r4_git_s_output_option_into_a_path_the_engineer_may_write_stays_allowed` |
| S13 | `test_w2_42a_r5_error_path.py::test_r5_a_named_crashing_form_gets_a_ruled_decision`, `test_w2_42a_r5_error_path.py::test_r5_a_named_crashing_form_gets_a_ruled_decision_for_an_engineer`, `test_w2_42a_r5_error_path.py::test_r5_a_named_crashing_form_is_not_an_error_through_the_hook`, `test_w2_42a_r5_error_path.py::test_r5_a_revision_the_judge_cannot_classify_gets_a_ruled_decision`, `test_w2_42a_r5_error_path.py::test_r5_a_revision_the_judge_cannot_classify_is_not_an_error_through_the_hook`, `test_w2_42a_r5_error_path.py::test_r5_a_write_tool_input_whose_path_is_no_path_is_refused_by_a_ruled_refusal`, `test_w2_42a_r5_error_path.py::test_r5_an_odd_read_or_bash_tool_input_gets_a_ruled_decision`, `test_w2_42a_r5_error_path.py::test_r5_property_no_generated_token_sequence_makes_the_judge_raise`, `test_w2_42a_r5_error_path.py::test_r5_a_genuine_fault_git_missing_from_path_still_refuses_by_the_error_path`, `test_w2_42a_r5_error_path.py::test_r5_a_genuine_fault_git_missing_from_path_refuses_a_blob_diff`, `test_w2_42a_r5_error_path.py::test_r5_a_genuine_fault_git_missing_from_path_is_an_error_through_the_hook`, `test_w2_42a_r5_error_path.py::test_r5_a_genuine_fault_an_unreadable_path_map_still_refuses_by_the_error_path` |
| F1 | `test_w2_42a_measured.py::test_failure1_no_write_the_base_parser_catches_is_missed`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused`, `test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands`, `test_w2_42a_apostrophe.py::test_apostrophe_b_the_call_writing_the_acceptance_folder_after_the_heredoc_is_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_b_the_four_f1_reversal_calls_of_act_guard_fix_5_stay_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_c_a_body_writing_the_acceptance_folder_after_an_apostrophe_comment_is_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_c_a_hash_that_starts_no_comment_keeps_the_write_on_its_line`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_hash_inside_a_parameter_expansion_starts_no_comment_so_its_write_of_t_is_refused`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_hash_that_never_was_a_comment_keeps_its_write_of_t_refused`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_write_of_t_before_a_real_comment_with_an_apostrophe_is_refused`, `test_w2_42a_apostrophe_2.py::test_apos2_f4_a_here_string_command_writing_t_is_refused_for_t_not_as_unreadable`, `test_w2_42a_apostrophe_2.py::test_apos2_dep1_a_python3_c_write_of_t_is_refused`, `test_w2_42a_here_string.py::test_r3_a_write_argument_after_a_here_string_is_seen_and_t_is_refused`, `test_w2_42a_here_string.py::test_r3_a_redirect_after_a_here_string_to_t_stays_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_here_string_whose_text_writes_t_is_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_bodyless_heredoc_after_a_python_write_of_t_is_refused`, `test_w2_42a_here_string_ro.py::test_hsro_write_a_read_only_form_that_writes_t_is_refused_naming_t`, `test_w2_42a_here_string_ro.py::test_hsro_fail_closed_a_writing_script_over_a_here_string_writing_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_literal_callback_that_writes_t_is_refused` |
| F2 | `test_w2_42a_parser.py::test_failure2_an_unparseable_or_unknown_form_is_unresolvable`, `test_w2_42a_parser.py::test_failure2_a_form_read_uncertainly_keeps_its_write`, `test_w2_42a_read_judge.py::test_failure2_an_unparseable_command_naming_a_secret_is_refused`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_d_a_body_with_an_unclosed_quote_outside_a_comment_is_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_here_string_to_a_shell_whose_text_cannot_be_known_is_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_bodyless_heredoc_after_a_python_write_of_t_is_refused`, `test_w2_42a_here_string_ro.py::test_hsro_fail_closed_a_shell_or_unknown_reader_of_an_expanded_text_is_refused`, `test_w2_42a_here_string_ro.py::test_hsro_fail_closed_a_writing_script_over_a_here_string_writing_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_literal_callback_that_writes_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_callback_the_guard_cannot_know_is_refused` |
| F3 | `test_w2_42a_r4_blob_refs.py::test_r45_failure_a_blob_or_tree_read_of_a_refused_path_stays_refused`, `test_w2_42a_r4_blob_refs.py::test_r45_failure_a_blob_diff_whose_output_is_written_into_the_acceptance_folder_stays_refused`, `test_w2_42a_r4_blob_refs.py::test_r45_failure_a_blob_diff_written_into_the_acceptance_folder_stays_refused_through_the_hook`, `test_w2_42a_r4_blob_refs.py::test_r45_failure_a_blob_read_of_a_refused_path_stays_refused_through_the_hook`, `test_w2_42a_r4_blob_refs_2.py::test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook`, `test_w2_42a_r4_blob_refs_2.py::test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule` |

## KPI lines, their cases and the expected red reasons

| KPI line | Cases (file: test) | Expected red reason on the base |
|---|---|---|
| S1 heredoc bodies | parser: `test_kpi1_*` (7) | the body is read as shell: an apostrophe makes the command unreadable (sentinel), a body's `touch` or `>` is taken as a write, a quoted body's `$(…)` as a command. Green on the base: the unquoted body's `$(…)` and the shell bodies (both already caught) |
| S2 own variables, literal loops | parser: `test_kpi2_*` (8) | `$W242A_B` is read from the environment only (sentinel); `do touch` is taken as the command `do` (no write), the loop over a substitution too (4 red). Green: the other four "any other binding" cases (already unresolvable) |
| S3 quotes, `sh -c`, `eval`, keywords, prefixes | parser: `test_kpi3_*` (14) | `echo "$(touch b)"`, `sh -c`, `eval`, `then rm`, `timeout 5 touch` give no write (the command's name is `echo`, `sh`, `then`, `timeout`) |
| S4 unmatched glob | parser: `test_kpi4_*` (3) | an unmatched glob is the sentinel. Green: the matched glob |
| S5 the writers it did not read | parser: `test_kpi5_*` (13) | `git checkout`/`restore`/`rm`/`mv`, `dd`, `truncate`, `sort -o`, `rsync`, `git apply`/`am`, `patch` give no write (all 13 red) |
| S6 read judge: `$((…))`, data bodies | read judge: `test_kpi6_*` (9) | `$((n+6))` is set aside as a substitution, so `sed` reads names given at run time (listing refusal); a data body's `cat .env` and `cat ~/.ssh/…` are secret reads (4 red). Green: the four kept refusals (a shell body, an unquoted body's `$(cat .env)`, `$(…)` inside `$((…))`, `cat .env`), and the data body holding a listing loop (the base places that listing) |
| S7 backslash-newline | parser: `test_kpi7_*` (4); read judge: `test_kpi7_*` (2) | the newline stays in the word: `accep\ntance`, `\n/…/f`, a `\n` operand of `cp`; `cat .e\␤nv` and the hidden file split over two lines are not seen (the base fails open) (5 red). Green: the single-quoted case |
| S8 a written body that is run | parser: `test_kpi8_*` (6) | a body the command only reads is taken as a write; a Python or ruby body run by its interpreter gives no target and no sentinel (3 red). Green: the shell script run by `bash` or `./s.sh`, and the run by `$S` (the body read as shell, or `$S`, catches it) |
| S9 measured | measured: `test_kpi9_*` (1 + 81 + 1) | the base leaves 22 of the 61 logged commands unresolvable (lines 24, 33, 35–38, 40–44, 46–49, 51, 52, 54–57, 60; more than 2); it misses 30 of the 81 planted shell writes (no target there, no sentinel); `docs/changes/W2-42a-evidence.md` does not exist (32 red; 51 planted shell writes green) |
| S10 literal paths are no listing | read judge: `test_kpi10_*` (11) | a `for` over `$(seq …)`, `$(wc -l < f)`, `$(nproc)`, `$(date …)` in a reading command, and a data heredoc appended to a record whose body holds `$(…)` text, are read as listings the guard cannot place (listing refusal; 5 red). Green: the five kept refusals, and the Python heredoc case (the base passes this shape; lines 75 and 79 of the replay are the shapes it refuses) |
| S11 replay and planted, through the hook | replay: `test_kpi11_*` (76 + 1 + 155) | see "The replay" (5 red) |
| F1 no write the base catches is missed | measured: `test_failure1_*` (53) | green by construction on the base (each is a case the base catches) |
| F2 unknown forms fail closed | parser: `test_failure2_*` (6); read judge: `test_failure2_*` (1); and the planted unknown forms in S9 and S11 | `eval "$X"`, `sh -c "$X"` and `bash -c` with unbalanced quotes give no write on the base (3 red); the unbalanced quotes, the unterminated heredoc, the shift in arithmetic and the unparseable secret read are green |
| review F1 (td-2): a shell with options reading a heredoc | f1: `test_review_f1_*` (1 + 15 + 4 + 15 + 4; 2 hook cases xfail strict until ACT-GUARD-FIX-5, in no row) | the head reads `bash -euo pipefail <<'EOF'` and the other 11 red spellings as data: no write and no read from the body (24 red). Green: `--noprofile --norc`, `-s`, the unknown flag, the 4 controls on both sides, the data-file check |
| reopen (td-4, DEC-1174 (1)): an apostrophe comment in a shell body (S1, F1, F2) | apostrophe: `test_apostrophe_a_*` (56 + 14), `test_apostrophe_b_*` (42 + 4), `test_apostrophe_c_*` (28 + 42 + 64), `test_apostrophe_d_*` (20), `test_apostrophe_control_*` (28 + 14) | (a) all 70 red: refused "the command cannot be read" (`lift_refusal` reads the apostrophe as an unclosed quote). Red too, the base allows them (a fail-open): the 42 writes of `T` between two apostrophe comments, the 4 edges with a comment after the write below an apostrophe comment, the 4 unclosed quotes after an apostrophe comment (the two apostrophes pair into one quote). Green: (b), the rest of (c) and (d), the controls (120 red, 192 green on `d73bd2756`) |
| reopen, second round (td-5, DEC-1174 (1), P-03ub-APOS-3 (1), P-03ub-APOS-4 (a)): a `#` inside `${…}`, a here-string holding ` #`, `python3 -c` writes (S1, F1) | apostrophe_2: `test_apos2_f1_*` (24 + 24 + 9 + 9 + 1 + 1), `test_apos2_f4_*` (3 + 2 + 2), `test_apos2_dep1_*` (1 + 1 + 3) | F1: 21 of the 24 writes of `T` red, **allowed** (a fail-open): the guard takes the `#` after a blank inside `${…}` for a comment and drops the write after it, at the top level, in a `bash <<'EOF'` body and in `bash -c '…'`. Green: the double-quoted `"${v%% #*}"` in each of the three (the base already reads a `#` in double quotes as no comment), the 24 writes of `A`, `${#v}`/`${v#a}`/`$#` (18), the two real-comment guards. F4: all 7 red, refused "the command cannot be read … (DEC-409)" (the 3 no-write here-strings, the 2 writes of `A`, the 2 writes of `T` whose reason must name `T`). dep1: 5 green (in the head since `669d87c91`). **Red on `692bc41bd`: 28 failed, 52 passed** |
| reopen, third round (td-6, DEC-1164 (18), the CTO's reopening of 2026-11-14): a write argument after a here-string (R3), the fallback's here-string forms, here-strings that write nothing (S1, F1, F2) | here_string: `test_r3_*` (5 + 5 + 1 + 1), `test_hstr_fallback_*` (3 + 3 + 2 + 2), `test_hstr_read_only_*` (9) | R3, 12 cases, 5 red: the write argument after `<<< word` is not seen, so the 5 writes of `T` (`tee`, `tee -a`, `cp`, `tee … ; echo done`, `tee` inside a list) are **allowed** (a fail-open). Green: the 5 writes of `A`, the redirect after a here-string (both). Fallback, 10 cases, 7 red: `bash <<<`/`sh <<<` text and `xargs touch <<<` writing `T` allowed (3), the two shells whose text cannot be known allowed (2), the two body-less heredocs after a `python3 -c` write of `T` allowed (2); green: the 3 writes of `A`. Read-only, 9 cases, 0 red. **Red on `d3ba8e50b`: 12 failed, 19 passed** |
| reopen, fourth round (td-8, DEC-1164 (18), the narrow check's R3 F1, the CTO's F1 (a)): read-only here-string forms with an expanded text stay allowed; the write forms and R3's fail-closed forms are kept (S1, F1, F2) | here_string_ro: `test_hsro_read_only_*` (13 + 5), `test_hsro_write_*` (9 + 9), `test_hsro_fail_closed_*` (13 + 4) | RO, 18 cases, 13 red: `read`, `IFS=: read`, `read` of a substitution, `read` of a variable set by one, `mapfile`, `readarray`, a `while read` loop, `sed`, `awk '{print $1}'`, `bc` and the three variants are refused "Bash write to '/<guard-unresolvable>'" (the text is expanded and the reader is not on R3's data list); green: the 5 data readers (`grep`, `wc`, `cut`, `tr`, `sort`). RW, 18 cases, 8 red: the 8 forms writing `A` are refused as `/<guard-unresolvable>`; green: the 9 writes of `T` (refused naming `T`) and `sort -o A`. FC, 17 cases, 0 red (green guards: R3 keeps them refused). **Red on `209ec8464`: 21 failed, 32 passed** |
| reopen, fifth round (td-9, DEC-1164 (18), R3 F1 second batch): a here-string read as data must not hide a command it feeds: a command name taken from a variable `read` bound, a `mapfile`/`readarray` callback; the guards stay allowed (S1, F1, F2) | here_string_ro_2: `test_hsro2_read_var_command_*` (3 + 3 + 7), `test_hsro2_callback_*` (2 + 2), `test_hsro2_guard_*` (6) | V, 13 cases, all 13 red: every form is allowed (`$f`, `$a $b`, `${l}`, `"$f" x`, `env $f`, `command $f`, `time $f`, with a literal or an `"$v"` text; `A` too) where bash runs the text read. CB, 4 cases, all 4 red: a literal callback writing `T` and a callback the guard cannot know are allowed. G, 6 cases, 0 red (green guards: a variable used as data stays allowed). **Red on `885b0d0f6`: 17 failed, 6 passed** |
| S12 (td-10, R4, D1, DEC-1157 (12), DEC-1180 (4)): a blob ref is judged as a read of its path | r4_blob_refs: `test_r4_a_diff_of_blob_refs_naming_visible_paths_*` (6), `test_r4_an_engineer_s_diff_*` (1), `test_r4_a_show_or_one_sided_diff_*` (8), `test_r4_a_diff_of_two_visible_blobs_is_allowed_through_the_hook` (1), `test_r4_a_blob_ref_naming_a_path_*` (12), `test_r4_a_diff_whose_revision_word_*` (4), `test_r4_a_show_whose_revision_word_*` (2) | 22 red. G1 (8 red): each two-sided blob diff raises `PolicyError(_REV_FAULT)` in the judge ("git cannot say whether a revision holds the hidden part": `_Judge.patched` asks `rev-parse <word>^{commit}`, which fails for a blob; the hook exits 2), and the engineer's is refused by the counterpart rule (taken for a patch of the whole tree). G2 (8 red): the two-sided diffs naming the hidden part or a secret raise the same fault before any path rule; the one-sided `git diff HEAD:<hidden or .env> docs/a.md` (and after `--`) are **allowed** (a fail-open: git prints the blob). G3 (6 red): the diffs naming nothing are refused by the raised fault (rule `error`); `git show nosuchref:docs/a.md` and `git show HEAD:docs/missing.md` are **allowed**. Green (12): the 8 guards (`git show` of a visible blob, the one-sided diff against a file, `--stat`) and the 4 `git show`/whole-tree refusals of G2 |
| S13 (td-10, R5, DEC-1128 (3), DEC-1133 (2)): the judge never raises; the error path stays | r5_error_path: `test_r5_a_named_crashing_form_*` (108 + 27 + 10), `test_r5_a_revision_the_judge_cannot_classify_*` (18 + 3), `test_r5_a_write_tool_input_*` (4), `test_r5_an_odd_read_or_bash_tool_input_*` (13), `test_r5_property_*` (1), `test_r5_a_genuine_fault_*` (2 + 1 + 1 + 2) | 26 red: the 21 revision forms (the judge raises `PolicyError(_REV_FAULT)` in `_Judge.patched`/`_Judge.ask`; the hook exits 2), the 4 Write/Edit paths (`decide()` raises `ValueError`/`TypeError`), the property case (269 of 1500 sequences give rule `error`, all the revision fault). Green (164): the named forms (ruled on the base: every index is guarded; the ticket's `list index out of range` is not reproduced by the product at `d9e7dc859`), the odd read inputs, and the 6 genuine-fault cases (kept) |
| F3 (td-10, R4/R5 failure line): refused today, still refused | r4_blob_refs: `test_r45_failure_*` (10 + 5 + 3 + 3) | green by construction (each is refused today, by `names_held_out`, the secret or hidden-part rule, the revision fault, or the write rule) |
| round R4 R5 (td-10, 2026-11-14) | r4_blob_refs (55), r5_error_path (190) | **Red on `d9e7dc859`: 48 failed, 197 passed** (S12 22, S13 26, F3 0); the whole folder at the same head (`-n auto -m "not local_only" -k "not real and not green_here and not time_limit"`): 48 failed, 1185 passed, 2 xfailed, 2 deselected (td-5's two `…_real_comment_…` cases, caught by `-k "not real"`); every failure is one of the 48 above, nothing outside the two new files changed |
| S12 (td-11, R4 second batch, DEC-1157 (12), DEC-1180 (4)): a path under a tree that is not the commit's top, and a blob id alone shown as text, are refused ruled; guards stay allowed | r4_blob_refs_2: `test_r4_a_path_under_a_tree_that_is_not_the_commit_s_top_*` (14), `test_r4_an_object_named_by_its_blob_id_alone_*` (4), `test_r4_a_cat_file_or_blob_ref_that_shows_no_refused_text_stays_allowed` (14), `test_r4_git_s_output_option_into_a_path_the_engineer_may_write_stays_allowed` (3) | 18 red, each **allowed** at `eca7a70176de` (a fail-open: real git prints the hidden file's text): `git diff SUB:hidden/q01.txt HEAD:docs/a.md` (both orders), `git diff HTREE:q01.txt …`, `git show SUB:…`/`HTREE:…`, `git cat-file -p SUB:…`, `git cat-file blob HTREE:…`, `git cat-file blob BLOB`, `git cat-file -p BLOB`, for research and engineer ("a fail-open: want a ruled refusal, got ('allow', '')"). Green (17): the 14 cat-file/blob-ref guards and the 3 `--output` into `src/` guards |
| F3 (td-11, R4/R5 failure line, second batch): a hidden blob under a subtree through the hook; git's own `--output` into `tests/acceptance/X/` | r4_blob_refs_2: `test_r45_failure_a_hidden_blob_named_under_a_subtree_is_refused_through_the_hook` (7), `test_r45_failure_git_s_own_output_option_writing_the_acceptance_folder_is_refused_by_the_write_rule` (15) | 22 red. Hook (7): each group 1 form exits 0 with no answer (allowed). `--output` (15): the 12 `--output=` forms (diff of blobs or commits, show, log over a range or a path; at the top, after `git -C <root>`, after `cd tests`) **allowed** (real git creates `tests/acceptance/X/zz.txt`); the 3 `--output <file>` forms refused by the revision rule ("the call names a revision the guard cannot resolve …"), not by the write refusal naming the file |
| round R4 R5 second batch (td-11, 2026-11-14) | r4_blob_refs_2 (57) | **Red on `eca7a70176de`: 40 failed, 17 passed** (S12 18, F3 22; guards 17 green); the whole folder at the same head (`-n auto -m "not local_only" -k "not real and not green_here and not time_limit"`): 40 failed, 1250 passed, 2 xfailed; every failure is one of the 40 above, nothing outside the new file changed |

**The red run on the base** (`a58ba344`, through the gate, `-n auto`): **94 failed, 358 passed**, no errors, each
failure for the reason above: S1 4, S2 4, S3 14, S4 2, S5 13, S6 4, S7 5, S8 3, S9 32, S10 5, S11 5, F2 3.

## The replay (S11)

Parametrised by refusal: `line<NN>-<tool-use id>`. A line judged false must be allowed; a line judged true must be
refused with the hook's reason equal to the logged rule. On the base (`a58ba344`, this hook) 64 of the 74 false lines
already pass (ACT-GUARD-FIX-1 to -3 fixed them in the hook); the 10 still refused are:

| Line | Rule | Why the base refuses it | In W2-42a's reach? |
|---|---|---|---|
| 40 | rule 5, unreadable writes | `rm -f chain-*.json` matches nothing: the parser's sentinel (S4) | yes: **red, must pass** |
| 75 | listing | a Python heredoc's body read as shell (S10) | yes: **red, must pass** |
| 78 | listing | `for i in $(seq 1 16); do grep … <file>` (S10) | yes: **red, must pass** |
| 79 | listing | a Python heredoc's body read as shell (S10) | yes: **red, must pass** |
| 80 | listing | a data heredoc appended to a record, its body read as shell (S6, S10) | yes: **red, must pass** |
| 47 | rule 1 | the hook's own Python reading | no: **held** |
| 65 | rule 1 | a write in a folder known only at run time, in a command naming the tests | no (a fail-open): **held** |
| 72 | rule 1 | the hook's own Python reading (F4) | no: **held** |
| 73 | rule 1 | the hook's own Python reading (F4) | no: **held** |
| 76 | rule 5, record paths | a reviewer's write to `scratch/orchestrator/reviews/` | no (the rule, not a misreading): **held** |

The two true lines (74, 77) are refused on the base by their logged rules and must stay so. The 155 planted cases
are refused on the base by their write rules (ACT-GUARD-FIX-3 measured 0 missed) and must stay so.

### Held refusals (a decision package to the CTO)

The KPI line says each line judged false must now pass. Five cannot, within W2-42a's paths (`src/gov/guard/**`),
without failing open or changing a rule; the tests expect each still refused by its logged rule (`HELD` in
`test_w2_42a_replay.py`, one line each, so the CTO's decision is one edit):

- **47:** ACT-GUARD-FIX-3 left this pattern refused by design (its row 46): an unquoted Python heredoc the shell
  rewrites with `$(echo "$out" | sed …)`, in a command naming the tests. Judged by `bash_writes.py`'s Python reading,
  which `src/` does not reach.
- **65:** `cd $TMPDIR 2>/dev/null || cd $(ls -dt /tmp/tmp.* | head -1)`, then `cat > probe.py`, in a command whose
  heredoc data names the tests: the write's folder is known only at run time. Rule 1 refuses an unresolvable write
  when the command names the tests; letting it pass is a fail-open.
- **72, 73:** the hook's Python reading (ACT-GUARD-FIX-3 F4): an f-string path from `sys.argv` (72), a computed path
  while the code runs a module of the acceptance folder (73), in code naming the tests. The product's parser adds
  nothing to either; only a change to `bash_writes.py` (an owner ACT) could.
- **76:** the log's "false-positive" is the harvester's automatic verdict ("the live hook now allows it", judged as
  an engineer); the same reviewer's Write of the same file seconds later (line 77) is judged true. Rule 5 keeps a
  reviewer to `docs/probes/`, `docs/audit/`, `docs/assessment/`, its own scratch and `/tmp`.

## Notes

- The replay runs against this machine's trees: each refusal's cwd and project folder (worktrees under
  `~/gov-os-worktrees/`, the main tree). A tree removed later is replayed in a stand-in (The fixtures, "Stand-ins
  for vanished worktrees"); the fixture states each logged path.
- No case reads a secret, the held-out material or a hidden half: the read-judge cases name `.env`, a key path and a
  hidden file of their own stand-in project as words; the replay passes the logged commands to the hook, which runs
  none of them.
