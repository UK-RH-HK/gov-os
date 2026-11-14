# Brief: independent test designer, W2-42a (DAEO-03ub), R4 (blob revision-colon-paths judged as reads) and R5 (the guard's judge never raises), with the R4/R5 failure line (DEC-1157 (12), DEC-1180 (4))

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh test designer: you write
tests from the behaviour stated here (DEC-136), from the KPI lines, the code and planted repositories only. No fix
exists yet; you design the cases and show them red on the base.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head d9e7dc859
(w2/W2-42a with w2/integrate merged in).
Your paths: tests/acceptance/W2-42a/** only. Add NEW files (suggested: tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs.py
and tests/acceptance/W2-42a/test_w2_42a_r5_error_path.py; the failure-line cases may sit in either) and update
tests/acceptance/W2-42a/README.md (its map) in the SAME commit. Do not edit the other test files, the fixtures or the
support module (copy what you need into your files).
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1157 (12), W2-42a R4 R5" --trailer "Implements: DEC-1157, DEC-1180, DEC-1128, DEC-1133" -- <your new files> tests/acceptance/W2-42a/README.md`

**Never** read, list or name the guard's call log `~/.gov-os/guard-calls` (the bar's held-out source, SETUP-A-BAR S2,
DEC-1108 (4)); the guard refuses it. The crashing forms are found by reading the code, not the log.

## The KPI lines you pin (the ticket's S12, S13 and F3)
- **S12 (R4, D1):** `git diff REV:PATH REV:PATH` (a revision-colon-path on one or both sides, each naming a blob that
  exists) and `git show REV:PATH` are judged as reads of those paths, under the read rules the path names; a revision
  word that names no commit, tree or blob is refused as today, not passed. Verify: the `test_r4_*` cases pass on
  planted repositories (both sides blobs: judged as reads; a path the role may not read: still refused; a revision that
  does not resolve: refused, rule not `error`).
- **S13 (R5, the error path):** no Bash or tool input makes the guard's judge raise inside itself: the
  `list index out of range` crash and the revision it cannot classify each get a ruled decision (allow, or a refusal
  naming its rule), never rule `error`; the error path stays and still fails closed for a genuine fault (a missing
  file, the 20-second deadline). Verify: the `test_r5_*` cases pass: the crashing forms found in the code (empty words,
  a lone operator, a trailing pipe, `&&` or `;`, an option with no value, an unterminated `$(`), each ruled; a property
  case over generated token sequences that never sees rule `error` from an exception; a planted genuine fault still
  gives `error` and refuses.
- **F3 (R4/R5 failure line):** a call refused today that the fix lets through although it writes into a walled path or
  reads a refused one (a fail-open). Verify: the `test_r45_failure_*` cases pass (a blob read of a held-out or secrets
  path, a `git diff` whose output is redirected into tests/acceptance/, each still refused).

## The ground (read it yourself; these are pointers, not the answer)
- The read judge: `src/gov/guard/reads.py`, class `_Judge` (`tool`, `command`), and the revision handling around
  lines 1640-1730: each revision word is resolved as a commit (`rev-parse ... <word>^{commit}`, about line 1721), so a
  blob word `HEAD:docs/a.md` makes git fail, and `ask` raises `PolicyError(_REV_FAULT)` ("git cannot say whether a
  revision holds the hidden part"). The judge only asks git when the session has hidden parts that the command might
  reach (`covers`), so plant an evaluation set that measures the role (the support module's `project()` does).
- The product's entry: `decide()` in `src/gov/guard/decide.py` (call it as tests/acceptance/W2-42a/test_w2_42a_here_string_ro.py
  does). Inside it, `reads.policy_refusal` turns a `PolicyError` into "<message>: the call is refused (fail closed,
  DEC-820)" and ANY other exception into the catch-all "the guard could not work out the reads this session is
  refused: the call is refused (fail closed, DEC-820)"; other parts of `decide()` (`_extract_bash_write_targets`,
  `lift_refusal`, `names_held_out`, `read_refusal`) may raise straight out of `decide()`.
- The live five-rule hook as it runs (tests/acceptance/W2-42a/fixtures/hook/pretooluse.py, with this tree's `src` on
  `PYTHONPATH`; `w2_42a_support.run_hook`): it calls `reads._Judge(...).tool(...)` directly and the product's
  `_extract_bash_write_targets`/`_expand_token`; any exception that escapes is logged as rule `error` and the hook
  exits 2 ("guard (DEC-953): could not decide: <exc>; refused"); `run_hook` returns `("deny", "ERROR: …", 2)` then.

## What "rule `error`" and "a ruled decision" mean in your cases
- **Rule `error` (the judge raised):** (a) `reads._Judge(root, parts).tool(tool, input, cwd)` raises (any exception,
  `PolicyError` included: that is what the live hook logs as `error`); (b) `decide()` raises; (c) `decide()` returns
  the catch-all "the guard could not work out the reads this session is refused" (an exception hidden by the
  catch-all); (d) through the hook, exit 2. Build the parts for (a) the way `policy_refusal` builds them (read it) or
  through a small helper of your own; state in a comment how you build them.
- **A ruled decision:** allow, or a deny whose reason is a rule's own text (the hidden-part, secret, listing,
  held-out, write-path refusals, or a refusal naming why a revision is refused), with no exception raised.
- A form whose ruled answer could be either allow or a rule's refusal (e.g. a lone `;`): assert only "ruled, not
  `error`", and for a form that writes or reads something refused, assert deny.

## The behaviour to pin
**R4 (planted repositories: `git init` in `tmp_path`, commits holding visible files, a hidden-part file, a `.env`):**
1. `git diff HEAD:docs/a.md HEAD:docs/b.md`, `git diff HEAD~1:docs/a.md HEAD:docs/a.md`, a one-sided form
   (`git diff HEAD:docs/a.md docs/b.md` or with `--no-index` if that is how git takes it: check in real git first),
   `git show HEAD:docs/a.md`, also with an abbreviated hash and a branch name for REV: allowed for a role the
   evaluation set measures (the paths are visible) — red today (refused by the revision fault).
2. The same forms naming a path the role may not read: the hidden part (`HEAD:fixtures/evaluation/<set>/hidden/q01.txt`):
   refused by the hidden-part rule; a secret (`HEAD:.env`): refused (the secret rule). Assert deny and, where the
   reason is a rule's text, which rule; not the catch-all and not an exception.
3. A revision word that names no commit, tree or blob (`git show nosuchref:docs/a.md`, `git diff nosuch:docs/a.md
   HEAD:docs/b.md`, `HEAD:docs/missing.md`): refused, and ruled (not an exception, not the catch-all).
   Check each form with real git in `$TMPDIR` first and say what git does with it.

**R5 (the crashing forms, found by reading `reads.py` and `decide.py` — and `src/gov/guard/bash_writes.py` if
`decide()` reaches it — every place that indexes a word list, a token list or a split result without a length check
is a candidate):** for each form you find that raises today (an `IndexError` or other), a case through `decide()` and,
where the live hook calls that code, through `reads._Judge.tool` or `run_hook`: ruled, never `error`. The ticket names
at least: empty words (`""`, `''`, `"" ""`), a lone operator (`;`, `&&`, `|`, `&`), a trailing pipe, `&&` or `;`
(`ls |`, `ls &&`, `ls ;`), an option with no value at the end (`git -C`, `git diff -U`, `git show --format`,
`cd -`, `find -name`, `grep -e`, `sed -i`, …: find which ones index past the end), an unterminated `$(`
(`echo $(ls`, `cat "$(ls"`). Also try them after a `cd`, inside `$(…)`, after `git -C <dir>`, and as a revision word.
For each, state in the test's docstring the code line that raises today (file:function) — or that it is already
green and why.

A **property case**: a seeded generator (no hypothesis installed; use `random.Random(<fixed seed>)`, a few thousand
sequences, bounded run time well under a minute) over token sequences drawn from shell words, operators (`;`, `&&`,
`||`, `|`, `&`, `>`, `<<`, `<<<`, `$(`, `)`, `` ` ``, quotes), git words (`git`, `diff`, `show`, `-C`, `HEAD:`,
`HEAD:docs/a.md`, `--`, `-U`), and empty strings, joined by spaces; through `decide()` and `reads._Judge.tool` on a
planted project with a hidden part: never an exception, never the catch-all. On failure, print the minimal failing
sequence it found (shrink by dropping tokens). Keep it deterministic.

**The error path stays (genuine faults):** at least one planted genuine fault still refuses through the error path:
e.g. git not on `PATH` for a `git diff` the judge must ask git about (fails closed: deny), an unreadable
`governance/project/path-map.yaml` (a folder in its place, or bad YAML) — choose what the code treats as a fault, and
check it refuses today (green on the base is expected for these; say so). The 20-second deadline lives in the hook
templates; pin it only if you can do it without a 20-second test (otherwise name it as not pinned, and why).

**F3 (fail-open guards; each refused today, must stay refused):** `git show HEAD:<a held-out path>` (plant
`governance/project/held-out.yaml` naming a path, as the existing W2-42a cases or `src/gov/guard/heldout.py` show),
`git show HEAD:.env` and `git diff HEAD:.env HEAD:docs/a.md` (secret), `git show HEAD:<hidden part file>`,
`git diff HEAD:docs/a.md HEAD:docs/b.md > tests/acceptance/X/zz.txt` and `>> tests/acceptance/…` for an engineer on a
ticket whose allowed paths do not hold tests/acceptance/ (a write refusal), and the same diff piped to `tee
tests/acceptance/X/zz.txt`. Assert deny; for these the reason may be any rule's, but not an exception.

## Names and marks
Name every test so it states the behaviour: `test_r4_…`, `test_r5_…`, `test_r45_failure_…`. Parametrize per form with
readable ids. No xfail marks. No network. Planted repositories only under `tmp_path`; git calls with
`-c user.name=t -c user.email=t@t -c commit.gpgsign=false`.

## The README map (same commit)
- A file-list entry for each new file (td-10, 2026-11-14, R4 R5, Rewrite-Reason DEC-1157 (12), W2-42a R4 R5).
- In "The KPI map": change the line "S1 to S11 are the ticket's success lines in order, F1 and F2 its failure lines"
  to say S1 to S13 and F1 to F3, and add rows `S12` (the `test_r4_*` cases), `S13` (the `test_r5_*` cases) and `F3`
  (the `test_r45_failure_*` cases), each test by full `file.py::test_name` as the other rows.
- In "KPI lines, their cases and the expected red reasons": a row each for S12, S13 and F3 with counts and the red
  reason; and a round-table row: "Red on d9e7dc859: N failed, M passed".
Check the map reads (`mkdir -p $TMPDIR/empty-home` first):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src python3 -c "import pathlib; from gov.accept import runner; print({k: len(v) for k, v in runner.parse_map(pathlib.Path('tests/acceptance/W2-42a/README.md').read_text()).items()})"`
(it must show S12, S13 and F3; never run gov accept itself in the sandbox).

## Red check (report it)
Run your new files at your head d9e7dc859. Expected: RED = R4 groups 1 and 3 (the revision fault: an exception in
the judge, or a refusal where an allow is due), each R5 crashing form you found, the property case (if it finds a
crash on the base: say which); GREEN (and named so, with why) = R4 group 2's refusals, the genuine-fault cases, the F3
guards. Run pytest only this way (one line):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <your files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Also run the whole folder once (same line, `tests/acceptance/W2-42a`, adding `-n auto -m "not local_only" -k "not real and not green_here and not time_limit"`)
and report its counts: nothing outside your new files may change (the folder is green at the base). The heavy slot
may queue: that is a wait. Anything longer than one line goes in a script file under `$TMPDIR`, run with bash or
python3 (a unique heredoc delimiter if you write one). Use the sandbox's own `$TMPDIR`; never write outside `$TMPDIR`
and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12), the red
run's counts, one failure's reason line per group, the list of crashing forms you found with the file:function that
raises, and the map reader's output line; in `tests`: the case count per group and which are red. A refusal twice for
the same call by the guard, the sandbox or a hook: stop and say so; never work around it. Search with Read and Grep
only (no gov retrieve, no gov context in the sandbox); search again once, in other words. Never open the evaluation
sets' root or any hidden or memory-verdict folder. No merge in the sandbox. A resource gate's refusal is a wait.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer --budget 20000, from the integration store's root: the main tree's store lacks DEC-1180)

```json
