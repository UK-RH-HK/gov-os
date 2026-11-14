# Brief: independent auditor, W2-42a (DAEO-03ub), the narrow check of the R3 F1 follow-up (DEC-1164 (18), DEC-1154)

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL. A narrow independent check (DEC-1154):
you judge ONLY the change since 209ec8464 (209ec8464f9e0c7a148a823279b60323ce348463, the head the R3 narrow check
passed), not the whole ticket and not the earlier rounds again (the ticket passed its FULL review round 2,
docs/probes/DAEO-03ub/PR-DAEO-03ub.md, and the narrow checks PR-DAEO-03ub-apos-2.md and PR-DAEO-03ub-r3.md). This is
the CTO's own P2 follow-up (DEC-1164 (18)), not a review round under DEC-1010.
Head to probe: w2/W2-42a at HEAD_FULL, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
Your one allowed path, named for the launcher only: tests/unit/guard/test_w2_42a_zz.py. Do not write it.
The change: `git -C /home/usain/gov-os-worktrees/W2-42a diff 209ec8464..HEAD_FULL`: two test-design batches (merges
289432d3a, td-8: tests/acceptance/W2-42a/test_w2_42a_here_string_ro.py, 53 cases; and 98eff3c84, td-9:
test_w2_42a_here_string_ro_2.py, 23 cases; README map rows in each) and two engineer commits (885b0d0f6 and
ENG6_COMMIT: src/gov/guard/bash_writes.py, possibly src/gov/guard/decide.py, tests/unit/guard/test_w2_42a_here_string_ro*.py,
docs/changes/W2-42a-evidence.md).

## What the R3 check found, and what the CTO decided (F1 (a), DEC-1164 (18))
- **F1 (RO, docs/probes/DAEO-03ub/PR-DAEO-03ub-r3.md lines 99 to 115):** with an unknown or substituted text, read-only
  here-string idioms got the unresolvable target where the base allowed them (`read -r a <<< "$v"`,
  `while read -r f; do echo "$f"; done <<< "$(git status --porcelain)"`, `mapfile -t L <<< "$(ls)"`,
  `sed 's/a/b/' <<< "$v"`, `bc <<< "$x + 1"`, …).
- **The rule decided:**
  1. `read`, `mapfile` and `readarray` take a here-string as data, whatever its text. Their own writes, if any (e.g. a
     redirect), are judged as usual.
  2. A loop's here-string (`while read -r f; do …; done <<< "$(…)"`) is data for the loop; the loop body's commands are
     judged by their own words.
  3. Data readers that never run their input (`sed`, `awk` without `system(`/`>`/`|`, `bc`, `grep`, `wc`, `cut`, `tr`,
     `sort`) take an expanded text as data. A reader whose script writes (an `awk` script with `>` or `system(`, `sed`
     with `w`/`-i`) is judged on that script, as today.
  4. `bash`, `sh`, `zsh`, `dash`, `xargs`, `source`, `eval` and any reader not named above keep R3's fail-closed rule
     for an unknown text.
  5. Nothing that R3's cases refuse becomes allowed.
- **Recorded rows, not to be re-judged** (the R3 check's F2 to F5: xargs output piped to a shell, `eval "$(…)"`,
  xargs option spellings, `tee 0<<< x …`; and earlier rows): report them only if this change made them worse.
T = `tests/acceptance/X/zz.py` (an engineer on DAEO-03ub may never write the acceptance folder); an allowed path is
`src/ok.py` (the tests' A).

## What happened in this follow-up (claims and pointers, not facts; check them)
- eng-5 (885b0d0f6) built the rule; its stated risks: a loop with a here-string on `done` is refused only when the call
  holds a shell, Python, `xargs`, `parallel`, `source`, `eval`, `perl`, `node`, `ruby` or `php` reader, so an unlisted
  program that reads stdin and runs it (`ssh`, `docker exec -i`) in a loop body is no longer refused; `_awk_reads_only`
  is conservative (`$1 > 5` counts as a possible redirect).
- The lead's probe of 885b0d0f6 found forms the base refused that real bash shows writing T, now allowed: a command word
  taken from a variable that `read` bound from a here-string (`while read -r f; do $f; done <<< 'touch T'`,
  `read -r a b <<< "$v"; $a $b`, after `env`/`command`/`time`) and `mapfile`/`readarray -C <callback>`. td-9 pinned
  them (refused), and ENG6_COMMIT is the fix. ENG6_CLAIMS
- The lead also saw, allowed at both 209ec8464 and the head (older, not this change): `mapfile -C 'touch T' L < x.py`.

## What to judge
- RO: the decided read-only forms are allowed at the head (directly through `decide()`, and the two acceptance files
  pass), with your own variants (options of `read`/`mapfile`, `IFS=` prefixes, `until` loops, nested loops, here-strings
  inside lists and pipelines, quoted and unquoted texts, `$(…)` and backtick texts), and judge any ordinary read-only
  work the change still refuses.
- NRA (nothing R3 refuses becomes allowed; fail closed over the change): no form that gave a write target, the
  unresolvable target or a refusal at 209ec8464 gives none at the head, except the decided read-only forms. Search hard
  for counterexamples where the data is run after all: a variable `read`/`mapfile`/`readarray` binds that later reaches
  a command name, `eval`, `source`, a shell, `xargs`, an array element run as a command (`"${L[@]}"`, `${L[0]}`), a
  callback, `printf -v`, `declare`/`export` tricks, a loop body program that reads the loop's stdin and runs it, a
  writing `sed`/`awk` script spelled another way (`sed` `e`/`W`/`s///w`/`s///e`, `--in-place`, `-i.bak`, `-s`, `-f`;
  `awk` `system (`, `print >>`, `printf >`, `|&`, `-f`, `gawk`/`mawk`/`nawk`, `bc` with `!`), and the lift form of `gov
  pause` reached through any of these. Run each form that moved toward allow in real bash under $TMPDIR to see whether
  it writes T. Judge eng-5's and eng-6's claims and risks: in scope or not, and does each fail open, lose work, or
  refuse ordinary work.
- DEC409: DEC-409 holds (read DEC-409 by id in docs/DECISION_REGISTER.md): no form in which 209ec8464 found the lift
  form of `gov pause` (--off) is now free of it; its cases stay green (grep tests/ for `lift_refusal` and `DEC-409`).
Report each finding with what you ran. If you can, time the slowest commands you find through `decide()` at the head
and the base.

Verify lines for the verdict block (use these ids): RO = the decided read-only here-string forms are allowed;
NRA = nothing R3 refused becomes allowed (fail closed over the change, the data never run unjudged); DEC409 = DEC-409's
rule and cases held.

The lead's runs at this head: `gov accept W2-42a` and the scoped set, in
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/r3c-accept.log and r3c-scoped.log (SCOPED_LINE).

## How to run
Every pytest through the heavy slot, TMPDIR your sandbox's own $TMPDIR, HOME an empty folder under it (mkdir -p $TMPDIR/empty-home first):

    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

Call `decide("Bash", {"command": cmd}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")` (it returns
`(decision, why)`; pass `root` as a real-path string, not a Path) from a script in your sandbox's $TMPDIR (PYTHONPATH as
above; see /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/r6/probe_gaps.py for a probe to copy); for
the base, export 209ec8464's src with `git archive 209ec8464 src | tar -x -C $TMPDIR/base` and run it there; never
check anything out in the tree. Anything longer than one line goes in a script file under $TMPDIR, with a unique
heredoc delimiter if you write one. Search with Read and Grep; search again once in different words if the first does
not answer. Never open the evaluation sets' root or any hidden or memory-verdict folder; never print a secret. If
something is refused twice, stop and say so; never work around a refusal.

