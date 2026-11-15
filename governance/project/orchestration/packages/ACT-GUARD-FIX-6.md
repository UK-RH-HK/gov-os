# ACT-GUARD-FIX-6: the live five-rule hook is brought to W2-42a's merged product parser (DEC-1174 (1), DEC-1133 (2))

**STATUS: option (B) built, as the CTO chose it** (a stricter-only delegated decision, prompt section 7; listed for the owner's reading).
This is the second build of the bundle, with the review's fixes F2 to F5 (the hook files' after-bytes are exactly as reviewed; the manifest
claims class `b`, as ACT-GUARD-FIX-5's did). The first build (manifest `b3e1bb51`) and the reviewed manifest (`99b82c37`) are void. The owner's line below is for this build.

- **For:** the owner (one yes line), through the CTO; **applied by the owner's operator** (class (b): `.claude/hooks/**` is the
  `guard-hook` row of `class-rules.yaml`, a control; `act_class.py` gives **b**, no script hit raises it) after one independent
  review of this bundle (`review.md` with the reviewer's verdict block; **not written yet**).
- **By:** an ACT-preparation helper of the CTO, 2026-11-15 03:02 UTC. **Nothing live was changed or started:** no commit, no stage, no write to
  the main tree's tracked files, `.claude/`, `~/gov-os-operator` or any queue. Built and rehearsed on fresh clones of `w2/integrate`
  (head 4d163c43f179 when the bundle was frozen; the two hook files are unchanged since ACT-GUARD-FIX-4 and ACT-SETS-GLOBS-1) under
  `/tmp/gov-os-act-gf6` and `~/gov-os-runs/W2-00/act-guard-fix-6` (both removed at the end).
- **Under:** **DEC-1174 (1)** (ACT-GUARD-FIX-5 withdrawn; the live hook is brought to W2-42a's parser as one ACT), **DEC-1133 (2)**
  ("each by ACT": the guard's own faults, the error path and the listing rule), **DEC-953 (item 2)** (the five-rule hook),
  **DEC-958**, **DEC-1050 (12)** (G-1: rules 1 and 5 judge the writes the guard resolves). The manifest's `dec` names those five.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-6/` (`build_after.py` makes both after files from the
  repository; `build_bundle.sh`, `build_checks.py`, `build_manifest.py`, the `check_*.py` sources, `apply.sh`, `rehearse.sh`,
  `cases6.py`, `replay6.py`, `prefilter.py`, `diff_calls.py`, `classify_diff.py`, `pairs.py`, `hookrun.py`, `undef.py`,
  `run_old_suites.sh`, `units.sh`, `w242a_acceptance.sh`, `f1_round2_cases.json`, `matrix_cases.py`).
  **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-GUARD-FIX-6/` (exactly `apply.sh`, `list.txt`, `manifest.json`,
  `rehearsal.log`, `before/` and `after/` with the two files each). **Evidence beside it:**
  `.gov-runtime/scratch/orchestrator/acts/ACT-GUARD-FIX-6.evidence/` (`decision-diff.md`, `followup-staged-pretooluse.diff`,
  the rehearsal's case and suite records).

## 0. The short version, the yes line, who applies it

1. **What changes.** Two files of the live hook: `.claude/hooks/bash_writes.py` (1,551 to 2,783 lines) and
   `.claude/hooks/pretooluse.py` (1,146 to 1,556; 417 lines added, 7 changed). The module `bash_writes.py` is a three-way merge
   (base ACT-GUARD-FIX-3's file `e662684a1d25`, ours the live file, theirs W2-42a's `src/gov/guard/bash_writes.py`) with the live
   file's FIX-4 additions kept (`deletes`, `made`, `emptied`, `_tilde`) and a copy of the product's line parser
   (`decide._line_write_targets`) at its end. `pretooluse.py` reads a command through that parser, copies R5's no-path refusal
   and R4's blob-revision reads, takes `git archive -o` as a write, and (option B, the CTO's) refuses under rule 1 a call that holds a run the scan cannot read and names `tests/acceptance`.
2. **Why.** ACT-GUARD-FIX-5 was withdrawn (DEC-1174 (1)) because an apostrophe in a heredoc body's comment opened the whole call; the
   owner chose to test W2-42a's merged parser for that and bring the live hook to it. W2-42a (DAEO-03ub) landed and closed
   2026-11-14 18:33 at `02bdb4fb0385`, on the narrow check PR-DAEO-03ub-r4 (pass, DEC-1154). The live hook keeps today the gaps that parser
   closed: the paired-apostrophe fail-open (two comments with an apostrophe hide a write between them), F1's shells with options,
   R3's here-strings, an unmatched glob, and the D1 fault (a git revision-colon-path refused as rule `error`, DECIDED-NOT-DONE row 122)
   and the judge's `list index out of range` crashes (row 123).
3. **The copy list of row 215 (W2-42a's r4 return), all in:** reads.py's `_blob_ref`, `REV_REFUSAL`, `PLACE_REFUSAL`,
   `_output_joined` and `_Judge.git`, `colon`, `placed`, `cat_file`, `patched`, `stored`, `ask` (copied verbatim by `build_after.py` from the
   merged file into the hook's own `Judge` subclass; the helper names they use are bound from the pinned judge, so they read the same
   before and after a re-pin); decide.py's `NO_PATH_REFUSAL`, `_no_path` and its call (in `main`, before any rule resolves a path);
   bash_writes.py's `_more_targets` and `_GIT_OUTPUT_SUBS` (the merge). **The archive form:** `git archive -o <file>`, `-o<file>`,
   `--output <file>` and `--output=<file>` are a write of that file (rule 1). This one is an addition beside the merged code (the
   product leaves it a missed write, row 215); it is a stricter rule in four lines of `_more_targets` and can be struck from the
   after copy without touching anything else (the shape check and one case then change).
4. **Rows F1 to F6 of the narrow check** (PR-DAEO-03ub-r4.md) are carried as far as the merged code carries them and not further:
   F1 (a lone surrogate in a write tool's path raises) and F2 (a non-dict `tool_input`) fail closed as before (the hook turns any
   exception into a refusal, and takes a non-dict `tool_input` as empty); F3 (`--git-dir` places a blob ref against the cwd's tree),
   F4 (a colon inside a reflog date's braces splits wrongly: refuses), F5 (`format-patch -o` writes missed, `diff-tree -p`
   unchecked) and F6 (`--outp=`) are the merged code's. Nothing was added for them.
5. **Measured, through the whole hook (section 4):** the 45 round 2 cases of ACT-GUARD-FIX-5 and W2-42a's 19 fixture cases are all
   as expected, none looser; the 1,280-call matrix: none refused before is allowed after, 400 newly refused (bodies that write
   there), no harmless body newly refused; **15,891 judgements of the last 48 hours' calls: 15,689 the same, 166 stricter,
   36 looser, of which 31 are the intended row-123 fixes and 5 are among the 7 intended corrections named in section 5; no other looser
   decision**; the planted regress set (option B) is refused as it was before.

**The owner's line, if the CTO ships the bundle: `yes ACT-GUARD-FIX-6 6e6c3927`** (the first 8 digits of the manifest's sha256,
`6e6c3927a52166da659ef2ee1fc6353a5c981c691d5f3fc95b06840b1a8382fa`).

**Who applies it:** class (b): **the owner's operator**, by its gates. By hand, the same steps as the rehearsal, from the repository:
```
G=.gov-runtime/scratch/orchestrator/acts/ACT-GUARD-FIX-6
bash $G/apply.sh check     # exit 0: "state before (sha256 bb246a21735e 74f8dbea4761)"
bash $G/apply.sh apply     # exit 0: puts both files, checks their hashes, runs the manifest's five checks; any failure puts
                           #   the before copies back (exit 5 or 6); prints "state applied (sha256 f03f9ac3e431 9b4228ea095a)"
bash $G/apply.sh verify    # exit 0
```
The hook reads its files at each call: the apply replaces each by `mv`, so a call in flight keeps the modules it loaded and the next
call reads the new files. The commit is the operator's (`Role: owner`, as GUARD-FIX-4's was); it names only the two files.

## 1. What was found (file and line)

- `.claude/hooks/pretooluse.py:257-272` (`bash_judgement`), `:280-293` (`bash_writes_of`) handed the pinned judge's `_extract_bash_write_targets` to `bash_writes.judge`
  as its line parser; `bash_writes_of` and `rm_refusal` read its answer. After a re-pin that carries W2-42a's decide.py,
  `_extract_bash_write_targets` is the product's whole-command wrapper (it runs the product's own `judge`), so the unchanged live
  hook would run the product's whole parser as its judge's line parser: it still decides (measured: the before hook under this tree's
  `src` allows `ls` and refuses an engineer's `touch tests/acceptance/...`), but twice-read and on the pin's code, not its own. The
  copies here make the hook independent of which judge the pin holds: this ACT works under the current pin (`797495bdfc70`, check 5)
  and under a judge with W2-42a's code (check 4).
- `Judge` (`pretooluse.py`, in `classes()`) subclasses the pinned `reads._Judge`, whose `git`, `patched`, `stored` and `ask` raise
  `PolicyError` when git does not resolve a revision word as a commit: the D1 fault (row 122).
- The judge crashes of row 123 (`list index out of range`, 12 of the last 48 hours' Bash calls in the corpus) are in the old module's
  reading of here-strings and heredocs; after the merge none of the 19,003 Bash calls raises.

## 2. The change (after minus before)

`bash_writes.py`: the product's module (`judge`, `Judgement.targets`, `writes`, `unread`, `adopt`, `comment_spans`, `read_view`,
`_shell_script`, `foreign`, `xargs`, here-string and comment handling) with the live file's `deletes`, `made`, `emptied` and `_tilde`
kept: `Judgement.adopt` takes a nested judgement's `deletes` and `made` too; a foreign reader's body takes its `deletes`;
a command only a second reading could read carries those readings' `deletes` and `recovered = True`; `_more_targets` gains the archive
form; `line_write_targets` and `GLOB_OPTIONS_RE` are the product's line parser, copied (its `decide` helpers bound at each call
from the pinned judge). Three conflicts resolved by keeping both sides (`emptied`/`_PARAM` and the product's `_shell_script`; the two
`__init__` blocks; `adopt`).
`pretooluse.py`: `line_parser(command)` (the product's wiring: an unmatched glob is its literal word unless the command may change how
bash expands one); `bash_writes_of` returns `shell` and `findings` plus the product's `writes` as code writes (rule 1 reads them, rule 5
never did: DEC-1050 (12), G-2); `rm_refusal` reads a recovered command's rm crudely too; R5's `NO_PATH_REFUSAL`, `_no_path`,
`_PATH_FIELDS` and the refusal in `main`; R4's constants, `_blob_ref`, `_output_joined` and the seven `Judge` methods.
Option B (the CTO's choice, section 5): in `bash_writes_of`, when `judged.unread` holds the unresolvable target and the call's text (or its
line-joined text) names `tests/acceptance` (`bash_writes.names_tests`), the code list gains `<project root>/tests/acceptance`, so rule 1
refuses it (ACT-GUARD-FIX-3 round 2's rule for an unreadable run, which FIX-4 dropped); rule 5 never read the code list.
Every other line is the live file's.

## 3. What was run (the rehearsal's `rehearsal.log`, last line `failures: 0`; its sha256 `183a4836deb4bf0a024f43c92abadf6e6b2184560344c9dc1ccf567dae6edd6c`)

`rehearse.sh <bed> <repository>`, bed `~/gov-os-runs/W2-00/act-guard-fix-6` (a fresh clone of `w2/integrate`, `--no-hardlinks`, the untracked
tools and the bundle copied in at their own relative paths, only the root substituted), every pytest through `heavy_slot.sh` with `TMPDIR`
in the bed, every hook call with its call log in a temporary folder (never `~/.gov-os`). **A** the bundle (hashes; before = the committed
blob = the main tree's file; no stray file or bytecode; no undefined name; the operator's own `check_act`, `validate_manifest`,
`path_rule`; `act_class.py` = b). **B** the operator's commands in the clone: check, the five checks red before, apply (they run and pass),
verify, apply again, only the two files changed, modes kept, `guard4_check.py --settings <clone>` = PASS (453 cases, 0 failed;
the registered line, the pinned interpreter), undo byte for byte, apply again. **C** the case sets through the hook before and after:
ACT-GUARD-FIX-5's 45 round 2 cases and W2-42a's 19 fixture cases (all as expected; none looser), the fixes and the controls (`cases6.py`:
39 and 27), the regress set (6: option B), and the 1,280-call matrix (none looser, 400 stricter). **D** the suites: the earlier bundles' g14, FIX-3 and FIX-4 case sets on both hooks
(section 4); `tests/unit/hooks`, `test_w2_141_search.py` and `tests/acceptance/W2-141/test_w2_141_hook.py`
with the logged-refusals replay (494 passed, two failed: section 6); W1-02's decision-time cases and W1-05's live-hook cases (the
p95-under-100-ms latency cases of the kernel hook; 21 passed); the live hook's own time per call (this log: median 144 ms before, 160 ms after,
p95 154 and 237 ms, process start and compile included; the first run of build 2: 135 and 188 ms; the reviewer's own run under load
178 and 228 ms: **about 50 ms more per call than before**, well inside the 20 s deadline); **W2-42a's whole acceptance folder against the hook** (its `fixtures/hook`
swapped for the before and the after copy, this tree's `src` as the judge): 76 failing before (the folder was designed on FIX-3's hook),
73 after: five now pass (`fix3 unquoted shell heredoc`, the three `r2 F2` run-a-file forms and logged row 46), and the two strict-xfail
F1 cases now XPASS and fail strict, **on the swapped fixture only**: a real apply leaves W2-42a's own fixture hook, so the marks stay
xfailed (review F3). **E** refusals:
a changed file, a link, a partial apply, and a failing check (the clone's copy of the manifest gets a sixth check that exits 1: apply
puts the before copies back, exit 6). **F** the main tree's `.claude` unchanged. **G** the replay of the CTO's 87 logged refusals
(corpus4.json): 86 the same and 1 stricter (row 46, option B); 2 refused before, 3 after, 0 looser, 0 hook errors.

**Where the rehearsal differs from a real run:** the root is a fresh clone (the real run is in the main tree, with its other worktrees,
which only add to the hook's tree list); the operator agent's own gates (G1 to G9, its walled session, its commit and freeze) are
not run, only its read-only tools on the bundle; a dry run of the operator's G3 plants a HOME, and then the pin-mode check (5) skips
itself (it needs `~/.local/bin/gov`) while the tree-mode check (4) runs; the hook files are read at each call, so no session is restarted.

## 4. The decision diff (`ACT-GUARD-FIX-6.evidence/decision-diff.md`)

The 48-hour call set (26,647 calls, 19,003 Bash, `tools/build_replay_calls.py --no-log`, the same window as build 1) through the live hook
and the after copy, as Claude Code runs them: every Bash call whose in-process judgement differs (613), every Bash call naming git
(4,634 more), 400 other Bash calls and 400 calls of other tools at random; each Bash call as its role, as an engineer and as an auditor:
**15,891 judgements (build 1: 15,873; the 18 more are the calls option B moved into the in-process set and a different draw of the others):
the same 15,689 (56 of them `error` before, a ruled refusal after: the D1 fault); stricter 166; looser 36.**

- **Looser, 36:** **31 intended (row 123):** refused before by the judge raising `list index out of range`, read and allowed after, none
  writes a walled path. **5 are among the 7 judgements of 4 calls that section 5 names as intended corrections.** No other looser decision.
  **0 intended R4:** no logged call flipped by a blob revision (the planted ones do, checks 4 and 5, and the cases).
- **Stricter, 166:** 132 are `git show` or `git diff` of `<rev>:<path>` where git cannot resolve the revision in the replay's present
  state (before, allowed; after, R4's ruled refusal "name a revision and a path that exist"); 2 are an auditor's writes now resolved
  (rule 5); **32 judgements of 15 calls are new in this build, option B (rule 1), on ordinary calls:** a call with a run the scan cannot
  read for certain (a script written and run, a heredoc body an unknown reader may run as shell) whose text names `tests/acceptance`.
  They are 4 calls of the orchestrator (two of its brief-writing heredocs, `cat > briefs/W2-60a... <<'EOF'` and
  `cat > briefs/W2-182-A5-run4.part.md <<'EOF'`; a revision check; a scratch-folder `mkdir ...; cat`), 3 of an engineer (probe
  scripts) and 8 of auditors and designers (W2-42a's probe scripts). They are the false refusals ACT-GUARD-FIX-4 removed for this class,
  given back by the trade the CTO chose; the table in the evidence file lists each with rule `1`. **Logged row 46** (the orchestrator's
  read-only inline-Python check naming an acceptance node id) is refused again by the same rule.
- **The earlier bundles' case sets (rehearsal D1), before and after:** g14 151 passed, 1 skipped, the same. FIX-3's file: 50 failing before,
  44 after (six cases its own file expects refused are refused again). FIX-4's file, in the ACT's re-baselined copy
  (`drafts/act-guard-fix-6/test_guard_fix_4.py`; the diff for the CTO's own copy is `ACT-GUARD-FIX-6.evidence/followup-test_guard_fix_4.diff`):
  6 expectations changed from allow to deny (`fix3 unquoted shell heredoc`, `fix3 unterminated heredoc naming acceptance judged as before`,
  and under option B `row 46 (left refused)...`, `r2 F2 repro 4: chmod +x, cd, then ./name`, `r2 F2 a python file run by uv run`,
  `r2 F2 a file with no #! line run by its name`) and logged row 46 joins its `STILL_REFUSED`; before the change those cases fail
  (8 failing), after it 1 fails (`test_rm_in_a_removed_worktree_passes`, a test of the machine, red before too).
- **The apostrophe cases:** the harmless heredocs with an apostrophe in a comment are allowed before and after in the live hook (it
  never refused them; the product parser did, which is why DEC-1174 (1) fixed it first). The live hook's own defect is the paired
  apostrophes: a write between two such comments is allowed before and refused after (`intend|paired-apostrophes-*`, four cases, and the
  first two of check 4).

## 5. The looser decisions found in build 1, and option (B): chosen by the CTO (stricter only, a delegated decision, prompt section 7; listed for the owner's reading)

Build 1 found a looser decision outside the two intended classes: a script written to a file and run, whose text the product's reader cannot
read for certain (the independent auditor's paired-quote body `echo "${v:-'}" '}" #'; touch tests/acceptance/X/zz.py`, run by `bash s.sh`
or `./s.sh` as an engineer), was refused before and allowed after: the product marks it unresolvable and refuses, the live hook lets an
unresolvable target through under G-1 (DEC-1050 (12)). **The CTO chose option (B)**, now in this build: when the judgement's `unread` holds
the unresolvable target and the call's text names `tests/acceptance`, rule 1 refuses (FIX-3 round 2's rule). Result: the regress set
(6 cases) is refused as before for the engineer and the auditor that name the tests, and stays allowed for the test designer; the
build-1 planted cases are refused again. **Cost, measured (section 4):** 32 judgements of 15 ordinary calls newly refused, and logged row 46.

**Residual, named, a class and not one case (the review's F1):** when a command can only be read on the second try (`judge()`'s fallback
after the first reading fails), all its targets go to the code list, which rule 5 never reads (DEC-1050 (12), G-2). So an auditor's or
reviewer's write to `src/` or `.claude/` behind quoting such as `msg="${1:-don't know}"; printf '%s\n' "$msg" > <path>` (or
`echo "${X#*'}"; touch <path>`, or the paired-quote body, at top level, in a /tmp script or in a heredoc) was refused before by rule 5 and is
let through after. Engineers stay refused by rule 1, which reads the code list; 2b-write, 2d and `rm` read it too. The planted case
`regress|script-then-run-paired-quotes-auditor-src` is one instance. It is rare: 15 of 19,002 Bash calls of the 48-hour set hold an apostrophe
inside a `${...}`, none loses a real write, and no auditor judgement of this kind is in either decision diff. The backstop is the reviewed
tree's `git status` (G-2); rule 5 is partial by design (an auditor's `dd`, `truncate`, `sort -o`, `rsync`, `git checkout`, python writes
are let through before and after). **It stays a named residual, with a Wave 3 row: rule 5 reads a second-try command's code writes**; closing
it is a rule-5 change beyond the delegated option B.

**The 7 judgements of 4 calls, intended corrections of refusals on made-up targets** (named as the CTO asked; not a weakening: the live
hook REFUSED them for a target its old reader made up): (1) `toolu_01XnH2yQZxcfZyVcTEhH8orC` (an auditor, rule 5; made-up target
`<cwd>/SP=...`), (2) `toolu_014AfDw8RqMv2SQGyhg88E2F` (an auditor, rule 5; `.../...`), (3) `toolu_019XJXZC2ncJniwQFa8mJKxd` (an auditor,
rule 5; `<cwd>/cd`), (4) `toolu_01UsNdv9cmndGQN6YrF1om4H` (an auditor, rule 5; `<cwd>/cd`), and (5) `toolu_01Hn2DFhjeBLQD7y6TkwrRfZ` as an
engineer, a test designer and an auditor (`cd $TMPDIR/rb && rm -rf w2 && ...`, refused by the crude `rm` fallback against the call's own,
vanished folder; read after, `w2` is under the `cd`'s folder in /tmp). In this build 5 of the 7 are still looser; the engineer's and
the auditor's judgements of call (5) are refused again, now by rule 1 (option B: the call names the tests and holds an unreadable run).

## 6. Follow-ups outside this ACT (the CTO's routes; `tests/` and `docs/` are not an ACT's paths)

- **The staged W2-141 copy and its unit test:** `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`
  asserts the staged `docs/changes/W2-141-hook/pretooluse.py` is the live `pretooluse.py` with one replacement (Glob in G-14's tools); it goes
  red after the apply. **Route:** the CTO commits `ACT-GUARD-FIX-6.evidence/followup-staged-pretooluse.diff` right after the operator's apply
  commit (the diff regenerates the staged copy from this build's after file, with the same one replacement; W2-141's Glob line itself is
  still not live, rows 78 and 135).
- **`tests/unit/hooks/test_live_hook.py::test_the_logged_refusals_replay_as_decided` goes red after the apply too** (a finding of this
  build): its `STILL_REFUSED` is `[64, 80]`, and option B refuses logged row 46 again, so the replay reads `[46, 64, 80]`. **Route:** the CTO's
  path-case route (DEC-1156 (7)), one line, with the staged follow-up in the same commit.
- **W2-42a's two strict `xfail` marks: no follow-up** (the review's F3): W2-42a's tests run the folder's own fixture hook, not `.claude/hooks/`,
  so after a real apply they stay `xfailed`; only the rehearsal's swapped-fixture run turns them red. W2-111's non-strict change is harmless
  and not needed.
- **`tests/unit/hooks/test_live_hook.py`'s new cases** (F1 round 2, the paired apostrophes, here-strings, `git archive -o`, no-path fields, the
  blob reads, the regress set: `cases6.py`'s sets): a later row.
- **ACT-GUARD-FIX-4's scratch file** `drafts/act-guard-fix-4/test_guard_fix_4.py`: its six expectations and `STILL_REFUSED` change as in
  section 4; I did not write into that folder (my writes are limited to this ACT's paths): the ACT's re-baselined copy is
  `drafts/act-guard-fix-6/test_guard_fix_4.py` and the patch for yours is `ACT-GUARD-FIX-6.evidence/followup-test_guard_fix_4.diff`.

## 7. Risks

1. **A guard-code change on the live path, 1,276 lines added to the module and 417 to the hook.** Most of it is the product's reviewed code; a bug raises and the
   hook turns any exception into a refusal (fail closed). The rehearsal's 15,873-judgement diff shows no exception after.
2. **More refusals of git revision-colon forms that do not resolve** (132 of the 166 stricter judgements): by design (R4, W2-42a's own
   rule), but a stale revision in an ordinary call is now refused where it used to be allowed. **And option B's cost** (32 judgements of
   15 ordinary calls, row 46): a script or heredoc the scan cannot read, in a call that names `tests/acceptance`, is refused for every role
   but the test designer, a read-only check included; the way out is to write the script to a file with a name the reader can read, or to
   keep the tests' folder out of its text.
3. **The rule-5 residual class** (section 5, the review's F1): a Wave 3 row, "rule 5 reads a second-try command's code writes".
   **About 50 ms more per hook call** (section 3). **Checks 3, 4 and 5 clean up their temporary folders when they pass** (the review's F5; a failing check, as in the red-before run,
   leaves its empty folder): done in this build; it changes no byte of the hook files (the after copies are as built), only the check sources in the manifest.
4. **A re-pin changes nothing here** (the copies bind their names from whichever judge runs the hook); without this ACT a re-pin would
   make the hook read every command with the product's whole parser inside its own judge (section 1), which still decides.
5. **Unverified:** the R4 variants W2-42a's reviewer could not run in real git (`HEAD~n`, reflog, tag and `@{u}` sides, `:./`, `--git-dir`)
   are the merged code's, judged from code only; the copies are verbatim.

## 8. Undo

`bash $G/apply.sh undo` puts the frozen before copies back byte for byte, only when each file is as this ACT left it (rehearsal B12, B13, E3, E8);
then the operator's revert of the commit. The follow-ups in section 6 are reverted with it.

## 9. Hashes

| file | sha256 |
|---|---|
| `before/repo/.claude/hooks/bash_writes.py` | `bb246a21735e70ad0b3a8213102a942bfcf1688838977aae618052c2f1f54732` |
| `after/repo/.claude/hooks/bash_writes.py` | `f03f9ac3e431a4eeceade8965a7d92cbf8490060cbc76b728b0caa1fe1bea683` |
| `before/repo/.claude/hooks/pretooluse.py` | `74f8dbea4761de37628305e5d58125641ae39a409a7ed0a2babb379b1ceca5b8` |
| `after/repo/.claude/hooks/pretooluse.py` | `9b4228ea095a52688f7311494836a55a014ef717cf1a7917c4b0e408666b0073` |
| `apply.sh` | `3e8c4296a47ac809b0cf91b1d2f701d7c7a5a5fe76c04d4841f17e5017725e54` |
| `list.txt` | `494dc8bd956da91e13675d8ded50ff386149d70602de0e113fe9be3e9d505fd4` |
| `rehearsal.log` | `183a4836deb4bf0a024f43c92abadf6e6b2184560344c9dc1ccf567dae6edd6c` |
| `manifest.json` | `6e6c3927a52166da659ef2ee1fc6353a5c981c691d5f3fc95b06840b1a8382fa` |

## 10. Before the yes

- One independent review of this build (`review.md`, verdict block; **not written yet**), by the operator's `reviewer-brief.md`. Build 1
  (manifest `b3e1bb51`) is void and must not be queued.
- The CTO's route in section 6: the staged-copy and `STILL_REFUSED` commit right after the operator's apply commit (no xfail follow-up).
