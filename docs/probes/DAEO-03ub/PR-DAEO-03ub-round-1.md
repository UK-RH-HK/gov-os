---
type: probe
task: DAEO-03ub
reviewer_session: b4ed5672-cd89-4b89-a968-87b10525f0bf
implementer_session: not recorded (the engineer of 94c85f361 to ce03bb8b3, before the emergency's stop of 2026-11-02; its lead's logs were not kept)
reviewer_wrote_nothing: true
commissioned_by: orchestrator (W2-42a ticket lead, session w2-42a-f7)
judged_by: orchestrator (W2-42a ticket lead)
judgement: fail
probed_commit: e9e4f7bacf416016d995ac5190d8e05b644dce80
---

# Probe record: W2-42a (DAEO-03ub), FULL review, round 1 of at most 2 (DEC-1010)

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (Opus, high), launched by the ticket lead with
  `launch_worker.sh`; brief `.gov-runtime/scratch/lead/briefs/a3-1.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a3-1.json`. Head `e9e4f7bac`: acceptance 452 passed, `gov accept` 452/0, the
  scoped set GREEN (6293 tests, 0 failed; serial 5 passed).
- **READY, by code.** The verdict block marks S1, S6 and failure line F1 fail, on finding F1: in scope, ordinary
  work yes, fails open. Not READY.
- **F1 (blocking).** `bash -euo pipefail <<'EOF'` and the other spellings that give the shell an option with a value
  read the heredoc body as data (`_kind`, `src/gov/guard/bash_writes.py:1116-1121`): no target, no sentinel, and the
  read judge drops the body; the base parser caught these writes. The finding went to the CTO at once (2026-11-13);
  the CTO confirmed one fix round for F1 only (DEC-802), with F4's `/dev/stdin` form riding along, and took the live
  hook's same gap by its own route.
- **Rows (DEC-801, DEC-808, DEC-1010).** F2, F3, F4, F5, F7 and F8 (ordinary work no, fails open) and F6 (ordinary
  work no, other: S11's listing rows and existing-root rows do not discriminate base from new since DEC-1070 moved
  the hidden parts out of the trees; the stand-in row 40 and the 155 planted cases do) are Wave 3 hardening rows,
  never a round.
- **Judgement: fail.** Round 2, the last, follows the F1 fix.

## The reviewer's record (as returned)

**Sandbox check (Step 0):** (a) passed: the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-03ub` was refused (`OSError: [Errno 30] Read-only file system`) and no file exists. (b) passed: `git hash-object -w --stdin` gave `1ae28402…` (exit 0) and `git update-index --refresh` exited 0.
**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
**Head probed:** e9e4f7bacf416016d995ac5190d8e05b644dce80, in /home/usain/gov-os-worktrees/W2-42a. **Session id:** b4ed5672-cd89-4b89-a968-87b10525f0bf.

task: DAEO-03ub (W2-42a), independent audit, FULL profile, round 1 of at most 2
status: done. Verdict: one blocking finding (F1), so the ticket is not ready. Classification: 1 blocking (in scope, ordinary work yes, fails open) and 7 recorded rows (ordinary work no, or not guard behaviour).
work_completed:
- Read the ticket, its six source decisions, the code diff since base 7c6a7427, the port compared line by line with `.claude/hooks/bash_writes.py`, and the acceptance support files and fixtures.
- Ran the base parser (decide.py taken from git history) and the new parser side by side on about 230 of my own commands.
- Called `read_view` directly on 37 heredoc readers.
- Fuzzed the new parser with 9,000 random commands: no exception, no hang.
- Replayed every logged refusal whose worktree still exists (43 rows) through the hook fixture, once with the base `src` and once with the new. Did the same for stand-in row 40, using this tree in place of its vanished folder.
- Ran one strict-mode command through the hook fixture (judged only, not run).
files_changed: none (`git status --porcelain` is empty at the end)
evidence: my scripts are under $TMPDIR/aud: diff.py, c1.txt to c6.txt, rv.py, rv2.py, fuzz.py, s11all.py, s11r40.py, hookpf.py. The base source is under $TMPDIR/basesrc.
tests:
- My run, through the heavy slot: `tests/acceptance/W2-42a tests/unit/guard` with `-m "not local_only" -k "not real and not green_here and not time_limit"` gave **970 passed** in 28 s.
- The quiet output did not print how many cases that filter deselected, so I can't name what it left out.
- I re-ran nothing else the lead ran.
discoveries:
- The live hook (`.claude/hooks/bash_writes.py`, and the copy in `fixtures/hook/`) has the same gap as F1. Through the hook fixture, an engineer's `bash -euo pipefail <<'EOT'` that touches `tests/acceptance/W2-42a/…` is **allowed**. The same body under plain `bash` is refused (MR-3). This repository's own rules 1 and 5 therefore fail open on this spelling today. The hook is outside W2-42a's paths, so it needs an ACT.
- On all 43 replay rows whose worktree still exists, the hook gives the same verdict with the base product code as with the new. The hook's own FIX-3 reading does rules 1 and 5, and no tree holds a hidden part any more. See F6.
risks: F1 ships into every adopted repository, and into EXAMIN's copy, if W2-42a lands as it is.
lessons:
- A heredoc delimiter in my own probe file clashed with test text, so part of the file ran as shell inside $TMPDIR/aud. Its only write was `$TMPDIR/aud/out.txt`, since deleted, and no tree was touched.
- Use a unique delimiter for probe files.
proposed_decisions: none. The fix for F1 is small and can ride along in the resume (DEC-802). In `_kind`, skip option values (`-o`/`+o`/`-O`/`+O`, combined forms like `-euo`, `--rcfile`/`--init-file`). Treat `/dev/stdin`, `/dev/fd/0` and `/proc/self/fd/0` as standard input. Read a shell given options it doesn't know as `shell`, not `data` (fail closed).
unresolved: the live guard refused three of my calls, each a different call, and I worked around none of them:
1. Building a fake project with a hidden evaluation folder (refused as a hidden-part read).
2. A probe file that named a secret file (refused as a secret read).
3. A probe file containing `sudo` (refused as sudo).
I dropped the secret and hidden-folder probes of the read judge. So the read-side half of F1 is shown by how `read_view` handles the body, not by planting a secret name.
recommended_next_action: resume W2-42a for F1 only: the `_kind` fix, plus parser and read-judge unit cases for `bash -euo pipefail <<EOF` and `cat <<EOF | bash -o pipefail`. Then a narrow check of that fix. Record F2 to F8 as Wave 3 rows. Send the same `_kind` gap in the live hook to the CTO as an ACT row.

**Findings**

**F1. Lines S1, S6 and failure line F1.** When `bash` or `sh` reads a heredoc and is given an option that takes a value (`-o pipefail`, `-euo pipefail`, `-eu -o pipefail`, `-o errexit`, `-O extglob`, `--rcfile f`), the option's value is taken for a script name. The body is then read as data:
- **Parser:** gives no target and no sentinel, and the whole command counts as read-only.
- **Read judge:** cuts the body from the text and judges none of it.
- **Base:** the base parser caught every write in these bodies.
This holds both directly (`bash -euo pipefail <<'EOF' … EOF`) and through a pipe (`cat <<'EOF' | bash -o pipefail`). Example: with body `sed -i s/a/b/ tests/acceptance/X/t.py; cp x.py src/other.py`, the new parser returns `[]` where the base returned 3 targets, and `read_view` keeps no body and no code. Through the hook fixture, an engineer's acceptance write in such a body is allowed.
- Where: src/gov/guard/bash_writes.py:1116-1121 (`_kind`, the shell branch counts the option's value as an operand). Used at :1224/:1234 (writes) and :1605-1611 (`read_view`).
- How found: `python3 -I $TMPDIR/aud/rv2.py`, `python3 $TMPDIR/aud/diff.py c6.txt`, `python3 $TMPDIR/aud/hookpf.py`.
- Ordinary work: yes, because `bash -euo pipefail <<'EOF'` is a stock strict-mode spelling that needs no unusual construction. Evidence that would reverse this: the moderator finding the spelling not ordinary. No transcript in ~/.claude/projects uses it outside this session, while 88 transcripts write `set -euo pipefail` inside the body, which is read correctly.
- Consequence: fails open
- Scope: in

**F2. Lines S8 and F1.** A data heredoc written to a script, then run in the same command by a name the parser never compares, gives no target and no sentinel. The base caught these writes. Forms: a glob (`bash *.sh`, `bash s*`, `source ./*.sh`), `find … -exec bash {} \;`, `ls *.sh | xargs -n1 bash`, `run-parts .`, `make` reading a just-written Makefile, and a just-written git hook followed by `git commit`.
- Where: bash_writes.py:1263-1270 (`script` compares basenames literally and never matches a glob).
- How found: `python3 $TMPDIR/aud/diff.py c3.txt` and `c2.txt`.
- Ordinary work: no, because agents run a script they just wrote by its name, which is read and caught. Running it by glob or implicitly is unusual. Evidence that would reverse this: a logged agent command of this shape.
- Consequence: fails open
- Scope: in

**F3. Lines F1 and F2.** A here-string `<<< word` is scanned as `<` followed by a heredoc whose delimiter is `word` (an off-by-one at the `<<<` check). If a later line equals `word`, the lines in between are taken as a data body. Example: `cat <<< hello` / `touch tests/acceptance/X/a` / `hello` gives `[]`, where the base gave the target. Otherwise the scan raises Unreadable and the command falls back to the old line parser, which fails closed.
- Where: bash_writes.py:200 (it advances one character, not three, past `<<<`).
- How found: `diff.py c5.txt`
- Ordinary work: no, because it needs a later line exactly equal to a bare here-string word.
- Consequence: fails open
- Scope: in

**F4. Lines S1 and F1.** A shell reading standard input through a path operand, or through a `-c` string that reads its input, is read as data, so its body is not judged. Forms: `bash /dev/stdin <<EOF`, `sh /dev/fd/0 <<EOF`, `bash -c 'bash' <<EOF`, `sh -c 'cat | sh' <<EOF`. The base caught these writes.
- Where: bash_writes.py:1119-1121
- How found: `diff.py c6.txt`
- Ordinary work: no, because `bash -s` is the usual spelling and these forms are rare.
- Consequence: fails open
- Scope: in

**F5. Lines S10 and S6.** On the read side, a heredoc body run by a shell behind a wrapper the kind check doesn't know (`stdbuf … bash`, `flock f bash`, `ssh host`, `docker exec -i c sh`, `xargs sh`, `busybox sh`) is cut out and judged only by the words it names, not as commands. A run-time listing inside it is no longer judged as a listing, where the base judged the whole text. The write side is fine: `foreign()` judges such bodies as commands.
- Where: bash_writes.py:1615-1626 (`read_view`, code bodies go to `codes`) and reads.py:1343-1348 (word-only judging).
- How found: `python3 -I $TMPDIR/aud/rv.py`
- Ordinary work: no, because it needs a measured session running a run-time listing inside a wrapper heredoc. Also, no tree holds a hidden part since DEC-1070.
- Consequence: fails open
- Scope: in

**F6. Line S11 (strength of the check).**
- **Listing rows don't discriminate:** rows 61, 75, 78, 79 and 80 are allowed through the hook on the base code too, because the main tree holds no hidden part any more. So the Verify clause's "a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing fails it" does not hold through the replay.
- **Existing-root rows don't either:** all 43 rows whose worktree exists give the same verdict on base and new.
- **The stand-in restore is still real:** stand-in row 40 is refused on the base code and allowed on the new. Line 74 refuses only because of the placeholder, which faithfully rebuilds the logged state.
- **What carries the rest:** the 155 planted refusals still guard against fail-open, and KPI 10's read-judge cases cover the listing mechanism without being vacuous.
- How found: `s11all.py new|base` and `s11r40.py new|base`.
- Ordinary work: no, because this is about how strong the test is, not how the guard behaves.
- Consequence: other
- Scope: in

**F7. Line S3.** `command -p touch x` gives no write, though KPI 3 lists `command` as a prefix. The base missed it too, as it missed `stdbuf`, `xargs touch` and `sudo touch` (those three are outside the ticket's scope).
- Where: bash_writes.py:372 (`lead`).
- How found: `diff.py c1.txt`
- Ordinary work: no, because `command -p` is rare.
- Consequence: fails open
- Scope: in

**F8. Line S4.** An unmatched glob is kept as its literal path, but Python's glob doesn't know bash's POSIX classes. So `rm -rf [[:lower:]]ests/acceptance` resolves to a literal path outside the acceptance folder, where bash would match `tests`. The base gave the unresolvable target.
- Where: decide.py:472
- How found: by reading the code, confirmed by Python's glob semantics.
- Ordinary work: no, because it is a deliberate construction.
- Consequence: fails open
- Scope: in

**What I probed and found sound:**
- **Writes and redirects:** heredoc data bodies for cat, tee and grep; quoted and unquoted `$(…)` in bodies; shell bodies; prefixes and keywords; `sh -c`, `eval`, `eval "$X"`; backslash-newline; all the KPI 5 writers; `git checkout <rev> <path>` and `git checkout <branch>`; `cd` tracking; process substitution; every redirect form.
- **Variables and loops:** subshell, function, `||`, prefix-assignment and set-twice variables all stay unresolvable; literal loops are expanded.
- **Heredoc edge cases:** `<<-`, two heredocs on one line, nested heredocs, delimiters with a trailing or leading space, an unterminated heredoc, `<<` in arithmetic.
- **Script runs:** a script run by name, by `./`, through `source`, through a copy, after `cd`, or as Python.
- **Port:** its differences from the hook copy change no judgement against the product beyond those noted above.
- **Robustness:** no crash or hang in 9,000 random commands.

```verdict
{"kpis": [
{"kpi": "S1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
{"kpi": "S2", "verdict": "pass", "findings": []},
{"kpi": "S3", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
{"kpi": "S4", "verdict": "pass", "findings": [{"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
{"kpi": "S5", "verdict": "pass", "findings": []},
{"kpi": "S6", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
{"kpi": "S7", "verdict": "pass", "findings": []},
{"kpi": "S8", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
{"kpi": "S9", "verdict": "pass", "findings": []},
{"kpi": "S10", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
{"kpi": "S11", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "F1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
{"kpi": "F2", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}
]}
```
