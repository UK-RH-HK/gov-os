Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent auditor, W2-42a (DAEO-03ub), the narrow check of R4 (blob revision-colon-paths) and R5 (the judge never raises) (DEC-1157 (12), DEC-1180 (4), DEC-1156 (7))

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL. A narrow independent check (DEC-1156
(7)): you judge ONLY the change since d9e7dc859 (d9e7dc8599bec803e11c672586a379372663e6e0, w2/W2-42a with
w2/integrate merged in, the ticket's landed state 77220f814 plus integration), not the whole ticket and not the earlier
rounds again (the ticket passed its FULL review and the narrow checks recorded in docs/probes/DAEO-03ub/). This is the
CTO's reopening within purpose (DEC-1157 (12), DEC-1180 (4)), not a review round under DEC-1010.
Head to probe: w2/W2-42a at b42e8628b835675fc4d1513805b7902c8a062dab, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
Your one allowed path, named for the launcher only: tests/unit/guard/test_w2_42a_zz.py. Do not write it.
The change: `git -C /home/usain/gov-os-worktrees/W2-42a diff d9e7dc859..b42e8628b835675fc4d1513805b7902c8a062dab`: two test-design batches (merge
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
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/r4-accept.log and r4-scoped.log (gov accept exit 0, every KPI line passed; the scoped run with GOV_TESTS_OPTIN=lifted,breadth: 6 failed, 4431 passed, 2 xfailed, the 6 being W2-33's copy_folder cases in W1-50 and W1-28, red on d9e7dc859 too (log/r4-base-reds.log: 6 failed); lead_verify: 1 failed of 8250 (tests/unit/retrieval/test_w2_112_shared_reranker.py, passes alone: log/r4-rerank-alone.log)).

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

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.



## The ticket's context packet (gov context DAEO-03ub --role independent-auditor --budget 20000, from the integration store's root)


```json
{
  "ticket": "DAEO-03ub",
  "ticket_text": "---\nid: DAEO-03ub\nstatus: in_progress\ndeps: []\nlinks: [DAEO-fau3]\ncreated: 2026-11-02T10:58:34Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-42a\ntags: [wave-2, implementation, guard, full]\nwbs_id: W2-42a\ntitle: 'The product''s guard reads what a Bash command writes: ACT-GUARD-FIX-3''s eight parser lines in src/gov/guard, before EXAMIN''s copy (DEC-1028 item 4)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- docs/probes/DAEO-03ub/**  # the probe record (the resume after the emergency, DEC-1158; CTO)\n- src/gov/guard/decide.py\n- src/gov/guard/reads.py\n- src/gov/guard/bash_writes.py\n- tests/unit/guard/test_w2_42a*\n- docs/changes/W2-42a-evidence.md\n- tests/unit/guard/test_decide.py\nkpis:\n  success:\n  - 'A heredoc''s body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body''s `$(\u2026)` is text, an unquoted body''s `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body''s `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body''s `$(\u2026)`, fails them'\n  - 'A variable the command sets once at its top level, before any use, is expanded; a literal `for` loop''s words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them'\n  - '`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command''s name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command''s name gives no write and fails them'\n  - 'An unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both'\n  - '`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them'\n  - 'The read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc''s body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body''s `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them'\n  - 'A backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them'\n  - 'A data heredoc''s body written to a file that a later word of the command may run is judged as that file''s code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them'\n  - 'Measured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product''s parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer''s record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it'\n  - 'The read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them'\n  - 'Replayed against every refusal in the CTO''s `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it'\n  - 'R4 (D1, 2026-11-14): `git diff REV:PATH REV:PATH` (a revision-colon-path on one or both sides, each naming a blob that exists) and `git show REV:PATH` are judged as reads of those paths, under the read rules the path names; a revision word that names no commit, tree or blob is refused as today, not passed [DND row 122, W2-141''s review, DEC-1157 (12), DEC-1180 (4)] Verify: the `test_r4_*` cases in tests/acceptance/W2-42a/ pass on planted repositories (both sides blobs: judged as reads; a path the role may not read: still refused; a revision that does not resolve: refused, rule not `error`)'\n  - 'R5 (the error path, 2026-11-14): no Bash or tool input makes the guard''s judge raise inside itself: the `list index out of range` crash and the revision it cannot classify each get a ruled decision (allow, or a refusal naming its rule), never rule `error`; the error path stays and still fails closed for a genuine fault (a missing file, the 20-second deadline) [DND row 123, DEC-1128 (3), DEC-1133 (2), DEC-1157 (12)] Verify: the `test_r5_*` cases in tests/acceptance/W2-42a/ pass: the crashing forms the engineer finds in the code (empty words, a lone operator, a trailing pipe, `&&` or `;`, an option with no value, an unterminated `$(`), each ruled; a property case over generated token sequences that never sees rule `error` from an exception; a planted genuine fault still gives `error` and refuses'\n  failure:\n  - 'Any write the parser misses that today''s parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write'\n  - 'An unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them'\n  - 'R4/R5: a call refused today that the fix lets through although it writes into a walled path or reads a refused one (a fail-open). Verify: the `test_r45_failure_*` cases in tests/acceptance/W2-42a/ pass (a blob read of a held-out or secrets path, a `git diff` whose output is redirected into tests/acceptance/, each still refused)'\nprofile: FULL\nsources:\n- DEC-1040\n- DEC-1028\n- DEC-1027\n- DEC-958\n- DEC-953\n- DEC-1044\n- DEC-1128\n- DEC-1133\n- DEC-1157\n- DEC-1180\nest_loc: 600\nacceptance_tests:\n  path: tests/acceptance/W2-42a/\n  author: independent-test-designer (MR-3)\ntrack: A\nlist_rows: []\n---\n# W2-42a The product's guard reads what a Bash command writes\n\nThe owner's DEC-1028 item 4 (P1-GUARD-PARSER-W2 (a)): ACT-GUARD-FIX-3 fixed this repository's five-rule hook\n(`.claude/hooks/bash_writes.py`, `e662684a`), but the product's guard, which every adopted repository runs, keeps the\nold parser (`_extract_bash_write_targets` in `src/gov/guard/decide.py`; `_set_aside` and `_Judge.tool`/`command` in\n`src/gov/guard/reads.py`) and refuses the writes of 22 of the 61 logged commands it cannot resolve. EXAMIN's agents\nwould meet those refusals. This ticket brings the eight parser lines (ACT-GUARD-FIX-3 \u00a77) into the product, before\nEXAMIN's copy. The engineer may port the reviewed `bash_writes.py` as its basis (a new `src/gov/guard/bash_writes.py`\nmodule); the test designer works from the KPIs and may take the package's planted cases and the logged corpus as\nfixtures (no secrets in them). W2-42 (`DAEO-fau3`) keeps its other rows in Wave 3. W2-09 and W2-10 hold\n`src/gov/guard/**`: start beside W2-09 only with the files split, or after it. Once it lands, the five-rule hook can\ncall the product's parser and `bash_writes.py` slims away (a later ACT).\n\n**Reopened 2026-11-13 by the CTO under DEC-1164 (18) (DEC-1174 (1), a P2 listed for the owner's reading).** A defect\ninside this ticket's scope: a Bash call whose heredoc body (to a shell) holds a comment with an apostrophe\n(`bash <<'EOF'` / `# it's fine` / `ls` / `EOF`) is refused whole, \"the command cannot be read\", although it writes\nnothing; the same body without the comment is allowed. It fails closed (the four F1 reversal calls of ACT-GUARD-FIX-5's\nround-2 review stay refused), but it refuses ordinary work, and the live hook is to copy this parser (DEC-1174 (1)).\nThe fix: comment text in a shell body is dropped before the body is tokenised (a `#` that starts a word, outside\nquotes, to the end of its line), so an apostrophe there is no unclosed quote; a body still unreadable after that stays\nrefused. A test designer adds the cases (the harmless forms allowed; the F1 reversal calls and a body that writes into\n`tests/acceptance/` after such a comment still refused), the engineer fixes `bash_writes.py`, then a narrow independent\ncheck of that change only.\n\n**Reopened 2026-11-14 by the CTO under DEC-1164 (18) (a P2 listed for the owner's reading): R3 and the fallback's here-string forms.** A defect inside this ticket's scope, found by its own apos-2 check: the line parser splits a command at `<<`/`<<<` (`decide.py` `_line_write_targets`), so a write argument after a here-string is missed (`tee <<< \"x\" T`, `tee -a <<< \"x\" T`): ordinary work yes, fails open. The same check named three older fail-opens in the unreadable fallback: `bash <<< 'touch T'`, `xargs touch <<< T`, and a body-less heredoc after a `python3 -c` write. The live hook is to copy this parser (DEC-1174 (1)), so they are fixed before that ACT. The fix: the word after `<<<` is the here-string's text (judged, as a `bash <<<`/`sh <<<` body is a command), never the command's end; the words after it stay the command's arguments; anything still unreadable fails closed. A test designer adds the cases, the engineer fixes `src/gov/guard/` within these paths, then a narrow independent check of that change only (DEC-1154).\n\n**Reopened 2026-11-14 by the CTO within the ticket's purpose (DEC-1157 (12), DEC-1180 (4); listed for the owner's reading): R4 (D1) and R5 (the error path).** The DND sweep of 11-14 found both still in the code (rows 122 and 123, triggers met: the lift DEC-1158; DEC-1128 (3) \"the guard's own error-path faults are fixed first after the lift\"): `reads.py:1721-1725` resolves every revision word as a commit, so a blob ref is refused; and nothing guards the judge against the three `list index out of range` crashes logged on 11-10. Both sit in `reads.py`/`decide.py`, already in this ticket's paths. Order: a fresh test designer writes R4, R5 and the failure line as described behaviour (DEC-136), from the code and planted repositories only (never the guard's call log `~/.gov-os/guard-calls`, the bar's held-out source, SETUP-A-BAR S2, DEC-1108 (4)); a fresh engineer fixes; gov accept; a narrow independent check (DEC-1156 (7)). The live hook takes the fix by ACT (DEC-1133 (2): \"each by ACT\"), with the parser copy already planned (DEC-1174 (1)). The CTO's own Bash line naming a revision-colon-path in text was refused on 11-14 by this very fault.\n",
  "authority": [
    {
      "id": "DEC-1040",
      "sha256": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "reason": "declared in sources",
      "tokens": 551
    },
    {
      "id": "DEC-1028",
      "sha256": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "reason": "declared in sources",
      "tokens": 708
    },
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1044",
      "sha256": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "reason": "declared in sources",
      "tokens": 328
    },
    {
      "id": "DEC-1128",
      "sha256": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "reason": "declared in sources",
      "tokens": 978
    },
    {
      "id": "DEC-1133",
      "sha256": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "reason": "declared in sources",
      "tokens": 557
    },
    {
      "id": "DEC-1157",
      "sha256": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "reason": "declared in sources",
      "tokens": 1274
    },
    {
      "id": "DEC-1180",
      "sha256": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "reason": "declared in sources",
      "tokens": 6270
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1040",
      "sha256": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "reason": "declared in sources",
      "tokens": 551
    },
    {
      "id": "DEC-1028",
      "sha256": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "reason": "declared in sources",
      "tokens": 708
    },
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1044",
      "sha256": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "reason": "declared in sources",
      "tokens": 328
    },
    {
      "id": "DEC-1128",
      "sha256": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "reason": "declared in sources",
      "tokens": 978
    },
    {
      "id": "DEC-1133",
      "sha256": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "reason": "declared in sources",
      "tokens": 557
    },
    {
      "id": "DEC-1157",
      "sha256": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "reason": "declared in sources",
      "tokens": 1274
    },
    {
      "id": "DEC-1180",
      "sha256": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "reason": "declared in sources",
      "tokens": 6270
    }
  ],
  "supplementary": [
    {
      "id": "0f50d7866981142a47af9c53",
      "path": "tests/acceptance/W2-42a/README.md",
      "text": "| S8 | `test_w2_42a_parser.py::test_kpi8_a_script_written_then_run_by_bash_is_judged_as_its_code`, `test_w2_42a_parser.py::test_kpi8_a_script_written_after_a_cd_then_run_by_its_path_is_judged`, `test_w2_42a_parser.py::test_kpi8_a_python_file_written_then_run_is_its_code_or_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_the_parser_cannot_read_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_by_a_word_that_does_not_expand_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_written_file_that_is_only_read_is_judged_as_data` |\n| S9 | `test_w2_42a_measured.py::test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_measured.py::test_kpi9_the_measures_are_stated_in_the_evidence_file` |\n",
      "tokens": 210
    },
    {
      "id": "090ab9463dcab3f765d7a9ea",
      "path": "tests/acceptance/W2-42a/README.md",
      "text": "| F2 | `test_w2_42a_parser.py::test_failure2_an_unparseable_or_unknown_form_is_unresolvable`, `test_w2_42a_parser.py::test_failure2_a_form_read_uncertainly_keeps_its_write`, `test_w2_42a_read_judge.py::test_failure2_an_unparseable_command_naming_a_secret_is_refused`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_d_a_body_with_an_unclosed_quote_outside_a_comment_is_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_here_string_to_a_shell_whose_text_cannot_be_known_is_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_bodyless_heredoc_after_a_python_write_of_t_is_refused`, `test_w2_42a_here_string_ro.py::test_hsro_fail_closed_a_shell_or_unknown_reader_of_an_expanded_text_is_refused`, `test_w2_42a_here_string_ro.py::test_hsro_fail_closed_a_writing_script_over_a_here_string_writing_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_is_refused_even_for_an_allowed_path`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_name_taken_from_a_read_variable_of_an_unknown_text_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_literal_callback_that_writes_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_callback_the_guard_cannot_know_is_refused` |\n",
      "tokens": 395
    },
    {
      "id": "a8ca59f092eea1e16b95fd93",
      "path": "tests/acceptance/W2-42a/README.md",
      "text": "| F1 | `test_w2_42a_measured.py::test_failure1_no_write_the_base_parser_catches_is_missed`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused`, `test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands`, `test_w2_42a_apostrophe.py::test_apostrophe_b_the_call_writing_the_acceptance_folder_after_the_heredoc_is_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_b_the_four_f1_reversal_calls_of_act_guard_fix_5_stay_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_c_a_body_writing_the_acceptance_folder_after_an_apostrophe_comment_is_refused`, `test_w2_42a_apostrophe.py::test_apostrophe_c_a_hash_that_starts_no_comment_keeps_the_write_on_its_line`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_hash_inside_a_parameter_expansion_starts_no_comment_so_its_write_of_t_is_refused`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_hash_that_never_was_a_comment_keeps_its_write_of_t_refused`, `test_w2_42a_apostrophe_2.py::test_apos2_f1_a_write_of_t_before_a_real_comment_with_an_apostrophe_is_refused`, `test_w2_42a_apostrophe_2.py::test_apos2_f4_a_here_string_command_writing_t_is_refused_for_t_not_as_unreadable`, `test_w2_42a_apostrophe_2.py::test_apos2_dep1_a_python3_c_write_of_t_is_refused`, `test_w2_42a_here_string.py::test_r3_a_write_argument_after_a_here_string_is_seen_and_t_is_refused`, `test_w2_42a_here_string.py::test_r3_a_redirect_after_a_here_string_to_t_stays_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_here_string_whose_text_writes_t_is_refused`, `test_w2_42a_here_string.py::test_hstr_fallback_a_bodyless_heredoc_after_a_python_write_of_t_is_refused`, `test_w2_42a_here_string_ro.py::test_hsro_write_a_read_only_form_that_writes_t_is_refused_naming_t`, `test_w2_42a_here_string_ro.py::test_hsro_fail_closed_a_writing_script_over_a_here_string_writing_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_read_var_command_a_command_word_fed_by_a_here_string_that_would_write_t_is_refused`, `test_w2_42a_here_string_ro_2.py::test_hsro2_callback_a_literal_callback_that_writes_t_is_refused` |\n",
      "tokens": 528
    },
    {
      "id": "3b0ab1061f84fe664ab86ef1",
      "path": "tests/acceptance/W2-42a/README.md",
      "text": "| S9 | `test_w2_42a_measured.py::test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_measured.py::test_kpi9_the_measures_are_stated_in_the_evidence_file` |\n| S10 | `test_w2_42a_read_judge.py::test_kpi10_a_loop_over_seq_reading_a_literal_file_is_judged_by_that_file`, `test_w2_42a_read_judge.py::test_kpi10_a_substitution_that_yields_no_file_name_leaves_the_literal_files`, `test_w2_42a_read_judge.py::test_kpi10_a_python_heredoc_naming_its_files_literally_is_judged_by_them`, `test_w2_42a_read_judge.py::test_kpi10_a_data_heredoc_appended_to_a_record_is_judged_by_its_file`, `test_w2_42a_read_judge.py::test_kpi10_names_given_at_run_time_are_still_judged_as_a_listing`, `test_w2_42a_read_judge.py::test_kpi10_a_literal_hidden_file_is_still_refused` |\n| S11 | `test_w2_42a_replay.py::test_kpi11_each_logged_refusal_replayed`, `test_w2_42a_replay.py::test_kpi11_the_replay_holds_every_recoverable_line`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |\n",
      "tokens": 277
    },
    {
      "id": "cfe76d6913b9cbde21f9b215",
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "text": "| 121 | DEC-1103 (3): `~/gov-os-writer` and `~/gov-os-checker` left as they are until the launch script is the default, then retired; the budgets and timeouts decided with the fixed briefs | (added audit a, 11-11) WAITS: the launch script as the default (rows 43-45, 117). Home: DAEO-sdxk (an ACT for the operator at that point); the budgets and timeouts go with row 44's briefs |\n| 122 | D1: the guard refuses a git diff of two blob refs (revision-colon-path on both sides; `src/gov/guard/reads.py:1638`, W2-141's review) | NOT STARTED, trigger met (the lift: DEC-1158; the re-pin 8f00bb90810b): an engineer round, a reopening of W2-42a (reads.py is in its allowed_paths) or a ticket from the owner; W2-42a's closes 77220f814 did not touch reads.py (sweep 11-14 notes, DEC-1180 (4); evidence: reads.py:1721-1725 still resolves each revision word with ^{commit}; W2-42a's commits 9196ce961, df7468015, 885b0d0f6, 07fb14799, 1388fcec6, fa77bb331, 669d87c91, f16075e43 change bash_writes.py and decide.py only) \u00b7 was: NOT STARTED: after the lift |\n",
      "tokens": 262
    },
    {
      "id": "095f578c7b0b5f81621f236c",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py",
      "text": "def test_failure1_no_write_the_base_parser_catches_is_missed(row):\n    assert s.parser_caught(row, s.REPO), \"the base's parser catches this planted write and this one misses it\"\n",
      "tokens": 45
    }
  ],
  "supplementary_query": "The product's guard reads what a Bash command writes: ACT-GUARD-FIX-3's eight parser lines in src/gov/guard, before EXAMIN's copy (DEC-1028 item 4)\nA heredoc's body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body's `$(\u2026)` is text, an unquoted body's `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body's `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body's `$(\u2026)`, fails them\nA variable the command sets once at its top level, before any use, is expanded; a literal `for` loop's words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them\n`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command's name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command's name gives no write and fails them\nAn unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both\n`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them\nThe read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc's body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body's `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them\nA backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them\nA data heredoc's body written to a file that a later word of the command may run is judged as that file's code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them\nMeasured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product's parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer's record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it\nThe read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them\nReplayed against every refusal in the CTO's `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it\nR4 (D1, 2026-11-14): `git diff REV:PATH REV:PATH` (a revision-colon-path on one or both sides, each naming a blob that exists) and `git show REV:PATH` are judged as reads of those paths, under the read rules the path names; a revision word that names no commit, tree or blob is refused as today, not passed [DND row 122, W2-141's review, DEC-1157 (12), DEC-1180 (4)] Verify: the `test_r4_*` cases in tests/acceptance/W2-42a/ pass on planted repositories (both sides blobs: judged as reads; a path the role may not read: still refused; a revision that does not resolve: refused, rule not `error`)\nR5 (the error path, 2026-11-14): no Bash or tool input makes the guard's judge raise inside itself: the `list index out of range` crash and the revision it cannot classify each get a ruled decision (allow, or a refusal naming its rule), never rule `error`; the error path stays and still fails closed for a genuine fault (a missing file, the 20-second deadline) [DND row 123, DEC-1128 (3), DEC-1133 (2), DEC-1157 (12)] Verify: the `test_r5_*` cases in tests/acceptance/W2-42a/ pass: the crashing forms the engineer finds in the code (empty words, a lone operator, a trailing pipe, `&&` or `;`, an option with no value, an unterminated `$(`), each ruled; a property case over generated token sequences that never sees rule `error` from an exception; a planted genuine fault still gives `error` and refuses\nAny write the parser misses that today's parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write\nAn unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them\nR4/R5: a call refused today that the fix lets through although it writes into a walled path or reads a refused one (a fail-open). Verify: the `test_r45_failure_*` cases in tests/acceptance/W2-42a/ pass (a blob read of a held-out or secrets path, a `git diff` whose output is redirected into tests/acceptance/, each still refused)",
  "further_batch": [
    {
      "id": "a67dded8c554b7c80a31f241",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
    },
    {
      "id": "a93879dc54f9351547516c3e",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
    },
    {
      "id": "f00d65bcd2c2b623dfc0e1ac",
      "path": "tests/acceptance/W2-42a/test_w2_42a_replay.py"
    },
    {
      "id": "91dd68a10ac78f279d046799",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "0f50d7866981142a47af9c53",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "090ab9463dcab3f765d7a9ea",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "a8ca59f092eea1e16b95fd93",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "3b0ab1061f84fe664ab86ef1",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "cfe76d6913b9cbde21f9b215",
          "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
        },
        {
          "id": "095f578c7b0b5f81621f236c",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        },
        {
          "id": "a67dded8c554b7c80a31f241",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        },
        {
          "id": "a93879dc54f9351547516c3e",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        },
        {
          "id": "f00d65bcd2c2b623dfc0e1ac",
          "path": "tests/acceptance/W2-42a/test_w2_42a_replay.py"
        },
        {
          "id": "91dd68a10ac78f279d046799",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "91dd68a10ac78f279d046799",
      "reason": "budget exceeded"
    },
    {
      "id": "a67dded8c554b7c80a31f241",
      "reason": "budget exceeded"
    },
    {
      "id": "a93879dc54f9351547516c3e",
      "reason": "budget exceeded"
    },
    {
      "id": "f00d65bcd2c2b623dfc0e1ac",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 19920,
  "budget": {
    "limit": 20000,
    "used": 19920
  },
  "hash": "db3fc9adfdffbf82c58a856068abaebdb66610264f78108477dcb6fd7fb757a8"
}

```

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing):
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then each finding as: id, KPI line, what, where (file:line), how found (the command), `Ordinary work: yes|no, because ...`,
`Consequence: fails open|loses work|other`, scope in|out.
Then the fenced verdict block, one entry per line R4, R5, F3:

```verdict
{"kpis": [{"kpi": "R4", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

Also state your session id if you know it, and the head you probed.

