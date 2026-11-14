# Brief: independent auditor, W2-42a (DAEO-03ub), the narrow check of R4 (blob revision-colon-paths) and R5 (the judge never raises) (DEC-1157 (12), DEC-1180 (4), DEC-1156 (7))

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL. A narrow independent check (DEC-1156
(7)): you judge ONLY the change since d9e7dc859 (d9e7dc8599bec803e11c672586a379372663e6e0, w2/W2-42a with
w2/integrate merged in, the ticket's landed state 77220f814 plus integration), not the whole ticket and not the earlier
rounds again (the ticket passed its FULL review and the narrow checks recorded in docs/probes/DAEO-03ub/). This is the
CTO's reopening within purpose (DEC-1157 (12), DEC-1180 (4)), not a review round under DEC-1010.
Head to probe: w2/W2-42a at HEAD_FULL, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
Your one allowed path, named for the launcher only: tests/unit/guard/test_w2_42a_zz.py. Do not write it.
The change: `git -C /home/usain/gov-os-worktrees/W2-42a diff d9e7dc859..HEAD_FULL`: two test-design batches (merge
15aeb0289, td-10: tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs.py and test_w2_42a_r5_error_path.py, 245 cases; merge
4692b61dd, td-11: test_w2_42a_r4_blob_refs_2.py, 57 cases; README map rows in each) and two engineer commits (eca7a7017,
b42e8628b: src/gov/guard/reads.py, src/gov/guard/decide.py, src/gov/guard/bash_writes.py,
tests/unit/guard/test_w2_42a_blob_refs*.py, docs/changes/W2-42a-evidence.md).

## The KPI lines you judge (the ticket's)
- **R4 (S12, D1):** `git diff REV:PATH REV:PATH` (a revision-colon-path on one or both sides, each naming a blob that
  exists) and `git show REV:PATH` are judged as reads of those paths, under the read rules the path names; a revision
  word that names no commit, tree or blob is refused as today, not passed. Verify: the `test_r4_*` cases pass on planted
  repositories (both sides blobs: judged as reads; a path the role may not read: still refused; a revision that does
  not resolve: refused, rule not `error`).
- **R5 (S13, the error path):** no Bash or tool input makes the guard's judge raise inside itself: the `list index out
  of range` crash and the revision it cannot classify each get a ruled decision (allow, or a refusal naming its rule),
  never rule `error`; the error path stays and still fails closed for a genuine fault (a missing file, the 20-second
  deadline). Verify: the `test_r5_*` cases pass (the crashing forms found in the code each ruled; a property case over
  generated token sequences never sees rule `error` from an exception; a planted genuine fault still gives `error`
  and refuses).
- **F3 (the R4/R5 failure line):** a call refused today that the fix lets through although it writes into a walled
  path or reads a refused one (a fail-open). Verify: the `test_r45_failure_*` cases pass (a blob read of a held-out or
  secrets path, a `git diff` whose output is redirected into tests/acceptance/, each still refused).

## What happened (claims and pointers, not facts; check them)
- The live hook logs rule `error` when an exception escapes the product code it calls (`reads._Judge(...).tool`
  directly, the parser); `decide()`'s `reads.policy_refusal` turns a `PolicyError` into a fail-closed refusal and any
  other exception into the catch-all "the guard could not work out the reads". At d9e7dc859 every revision word was
  resolved as a commit (`rev-parse <word>^{commit}`), so a blob ref made `ask` raise `PolicyError(_REV_FAULT)`.
- td-10 found that the forms the ticket names for R5 (empty words, lone operators, trailing `|`/`&&`/`;`, options with
  no value, an unterminated `$(`) raise nothing at d9e7dc859; the raises it found were the revision classification and
  a Write/Edit path holding a NUL byte or not a string (`decide()` raised `ValueError`/`TypeError`). It could not
  reproduce the logged `list index out of range` in the product (it did not, and you must not, read the guard's call log
  `~/.gov-os/guard-calls`: the bar's held-out source; the guard refuses it).
- eng-7 (eca7a7017) claims: `_blob_ref`, `_Judge.colon` (a blob ref read as its path under the read rules, then
  `git cat-file -t` for a session with a refused part), `REV_REFUSAL` in place of raising in `patched`/`stored`/`ask`
  (git's non-zero answer is now a ruled refusal; git that cannot run still raises: the fault path), and in decide.py
  `_no_path`/`NO_PATH_REFUSAL` for a no-path file tool field. Stated risks: a non-zero git answer is ruled, not an error;
  `git show HEAD:` is now refused for sessions with parts.
- The lead's probe of eca7a7017 found, refused at d9e7dc859 and allowed there: `git diff <subtree id>:hidden/q01.txt
  HEAD:docs/a.md` (the hidden file's text) and `git diff HEAD:docs/a.md HEAD:docs/b.md --output=tests/acceptance/X/zz.txt`
  (git's own write); and allowed at both: `git show`/`git cat-file -p` of a subtree-id ref, `git cat-file blob|-p <blob
  id>`, `git show|diff|log --output=…`. td-11 pinned them; eng-8 (b42e8628b) fixed them: `_Judge.placed` (only a commit,
  the index, `<commit>^{tree}` or HEAD's top tree place a path at the top; else `PLACE_REFUSAL`), `_Judge.cat_file`,
  `_output_joined` (the `--output <file>` word is no revision), and in bash_writes.py `_more_targets`/`_GIT_OUTPUT_SUBS`
  (`--output` is a write target for the git diff family). Stated gaps, not fixed: `git cat-file --batch` from stdin (the
  lead saw it refused at both commits by the hidden-part rule in its probe), `git archive -o <file>` (a missed write,
  allowed at both commits).
- td-10's open points: `git show HEAD:<held-out path inside the repository>` (relative) allowed at d9e7dc859 (heldout.py
  is outside the ticket's paths); the 20-second deadline not pinned (the hook template's alarm, outside src/gov/guard).

## What to judge
- R4: the blob forms are judged as reads of their paths at the head (directly through `decide()` and through the hook
  fixture, tests/acceptance/W2-42a/fixtures/hook/pretooluse.py with this tree's src on PYTHONPATH, as
  tests/acceptance/W2-42a/w2_42a_support.py `run_hook` runs it), with your own variants (`HEAD~n`, `@`, `@{u}`-like and
  reflog words, tags, `<commit>^{tree}:`, `:./`, `:../` from a subfolder, `git -C`, `-c` options before the subcommand,
  `--` and pathspecs after, `--no-index`, `--cached`, `-R`, `--word-diff`, `--stat`, `git show` with several objects,
  `git log -p REV:PATH`, `git difftool`, `git grep REV -- PATH`), and whether ordinary read-only work the change should
  free is still refused.
- F3 (fail closed over the change): no form that gave a refusal at d9e7dc859 gives an allow at the head when it writes
  into a walled path (tests/acceptance/ for an engineer, outside a reviewer's record for a reviewer) or reads a refused
  one (the hidden part, a secret, held-out material, the counterpart's work). Search hard: blob refs whose path git
  places elsewhere than the guard does (subtree ids, tags of trees, `REV^{tree}` of a non-HEAD commit, `REV:path` with
  `..`, symlinks in the tree, case, a submodule, `git -C` into another repository or worktree, `--git-dir`/`--work-tree`,
  `GIT_DIR=`), an object id alone (`git show <tree id>`, `git cat-file -p <tree id>` listing names, `git ls-tree`),
  `--output` spellings (`--output=`, `--output <f>`, `-o` where git takes it, after `--`?), `--ext-diff`/`--textconv`
  drivers, `git diff` piped into a writer, and the R5 change: a git failure that is now a ruled allow rather than a
  refusal (does any non-zero git answer now lead to an allow?), `ask` returning None at every caller. Run each form that
  moved toward allow in real git under $TMPDIR to see whether it shows a refused file's text or writes the walled path.
- R5: with your own generated and hand-made inputs (tool inputs of every tool name the guard knows, odd types,
  NUL bytes, huge or empty strings, every git subcommand route the judge has, unterminated quotes/substitutions/heredocs),
  no exception escapes `decide()` or `reads._Judge.tool`, and no call reaches the catch-all; and a genuine fault (git not
  on PATH, an unreadable path map) still refuses through the error path. Judge whether the change keeps the error path
  for faults and does not turn a fault into an allow.
Report each finding with what you ran. Time the slowest commands you find through `decide()` at the head and the base.

Verify lines for the verdict block (use these ids): R4 = blob revision-colon-paths judged as reads under the read
rules, an unresolved revision refused (ruled); R5 = no input makes the judge raise, the error path kept for genuine
faults; F3 = nothing refused at d9e7dc859 that writes a walled path or reads a refused one becomes allowed.

The lead's runs at this head: `gov accept W2-42a` and the scoped set, in
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/r4-accept.log and r4-scoped.log (SCOPED_LINE).

## How to run
Every pytest through the heavy slot, TMPDIR your sandbox's own $TMPDIR, HOME an empty folder under it (mkdir -p $TMPDIR/empty-home first):

    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

Call `decide("Bash", {"command": cmd}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")` or with role
"research" on a planted project whose evaluation set measures the role (it returns `(decision, why)`; pass `root` as a
real-path string) from a script in your sandbox's $TMPDIR (PYTHONPATH as above; copy
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/r7/probe_failopen2.py, the lead's probe, if useful); for
the base, export d9e7dc859's src with `git archive d9e7dc859 src | tar -x -C $TMPDIR/base` and run it there; never
check anything out in the tree. Run every command in the foreground (a headless session that stops to wait on a
background job ends). Anything longer than one line goes in a script file under $TMPDIR, with a unique heredoc
delimiter if you write one. Search with Read and Grep; search again once in different words if the first does not
answer. Never open the evaluation sets' root or any hidden or memory-verdict folder; never read, list or name
`~/.gov-os/guard-calls`; never print a secret. If something is refused twice, stop and say so; never work around a
refusal (not by another form or tool either).

