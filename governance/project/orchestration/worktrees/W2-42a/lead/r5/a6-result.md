task: DAEO-03ub (W2-42a), narrow independent check of the R3 fix (DEC-1164 (18), DEC-1154), d3ba8e50b..df7468015
status: done. R3, FALLBACK, DEC409 and FC pass. RO fails on its own words but does not block: one finding refuses ordinary work, and it fails closed. Nothing in scope fails open or loses work in ordinary work, so READY is unaffected.
work_completed: I read the source diff and the judge/decide flow. I ran about 7,450 forms through `decide()` at the head and at d3ba8e50b (exported with `git archive`): 56 R3 writer forms, 95 fallback forms, 77 read-only and xargs-option forms, 21 ordinary read idioms, 19 DEC-409 lift forms, 6 xargs-to-shell forms, and a generated set of 7,208 `CMD <<< WORD REST` forms. I ran every T form the head allows (3,041) in real bash, each in a fresh scratch folder. I timed large unreadable commands at both commits, ran the suites, and checked authorship (MR-3).
files_changed: none. `git status --porcelain` is empty at the head.
evidence: scripts and outputs are in $TMPDIR/probe (/tmp/gov-launch-23_k2sk4/claude-1000/probe): `probe.py`, `cmp.py`, `run.sh`, `gen.py`, `realbash.py`, `dbg.py`, `timing.py`, `timing2.py`, form lists `r3/fb/ro/ro2/lift/xp/gen.txt`, results `*.head.jsonl`, `*.base.jsonl`, `gen.cmp`, `rb.out`.
tests: W2-42a acceptance plus tests/unit/guard through the heavy slot: 1617 passed, 2 xfailed, 0 failed. `test_w2_42a_here_string.py` (acceptance): 31 passed at the head, and 12 failed / 19 passed against d3ba8e50b's src, which confirms claim 5's red count. DEC-409 files (W1-50 lift guard rule, unit/pause, the W1-50 freeze flag, W1-28 freeze): 24 passed. The lift-keyword cases across guard, W2-42a, W1-50 and pause: 8 passed. The exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"` left out the real-model, green_here and time_limit cases.
discoveries: the evidence file says read-only here-string forms stay free, but its examples are all literal texts; with a variable text, `read`, `mapfile`, `while…done`, `sed` and `awk` are refused (F1).
risks: the live hook is to copy this parser (DEC-1174 (1)). F1 would then refuse common agent idioms in every session.
lessons: a fail-closed rule for an unknown text given to a "code" reader is right for `bash`/`sh` but too broad for shell builtins that never run their input.
proposed_decisions: none. F1 is for the CTO: a narrow follow-up, or a Wave 3 row.
unresolved: one guard refusal. `git show -s … df7468015` (to read its trailers) was refused: "git cannot say whether a revision holds the hidden part". I did not respell it. I ran one different query, `git log --format=… --name-only d3ba8e50b..df7468015`, which answered.
recommended_next_action: Classification: 0 findings in scope that are ordinary work and fail open or lose work; 1 in scope that is ordinary work and refuses work (F1); 4 rows (F2–F5). Recommendation: land the change. The CTO decides F1 (my suggestion: `read`/`mapfile`/`readarray` take a here-string as data, and a loop's here-string is judged by the loop's own commands), either as a narrow fix before the live hook copies the parser, or as a recorded row.

Sandbox check (step 0), session f309b71b-2755-4f92-b864-c2faf18d8764:
- (a) the `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-03ub','w')…"` write failed with "Read-only file system", and no file exists.
- (b) `git hash-object -w --stdin` gave 1ae28402a…; `git update-index --refresh` exited 0.
- `ps` shows no ollama or llama-server process.
- HEAD is df74680150bb6add79ec8976a803488d3511ace5, GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-03ub.

**The engineer's claims, judged:**
1. **Holds.** 30 R3 forms the base allowed are now refused, and none of the head's refusals there are wrongly placed. That covers tee, `tee -a`, cp, `-a`/`--` after the text, `<<<x`, quoted and unquoted texts, `$v`, `$(…)` and backtick texts, `$'…'`, two here-strings, `< /dev/null`, lists, pipelines, `( )`, `{ }`, if/for, `bash -c`, `sh -c`, eval, and heredoc bodies for bash and `| sh`. `sort -o` and `dd of=` were already caught at the base. Redirects after a here-string stay judged. The `<` rule ("skips only itself after a punctuation word") can only add targets.
2. **Holds, with F1 and F2.**
   - Texts given to bash/sh/zsh/dash/ksh/`source /dev/stdin`/`. /dev/stdin` are judged as commands, also through env, `env -i`, timeout, nohup, nice, command, `X=1`, `/bin/bash`, `/usr/bin/env`, `-s`, `-x`, `-e -u`, `--norc`, nested `bash <<<`, and `| sh` / `| bash`.
   - `xargs [-n1|-n 1|-r|-P4|-L1|-E|-s|-x|-p|-o|--] CMD <<< W` is judged. `-I`, `-i`, `-0`, `--null`, `-d`, `-a`, `--arg-file`, `--replace` and `-J` give the unresolvable target.
   - An unknown text fails closed: `bash <<< "$X"`, `sh <<< "$(…)"`, `xargs touch <<< "$F"`.
3. **Holds.** `python3 -c "open(T…)"` followed by `cat <<EOF`, `cat <<'EOF'`, `cat <<-EOF`, `&& bash <<EOF`, or a body with no end line: T is refused in each.
4. **Holds.**
   - `cat <<< touch T` makes cat read T; real bash writes nothing.
   - In the generated set, 0 of the forms that moved toward allow write T in real bash.
   - `python3 <<< "open(T,'w')"` gets the same answer as `python3 <<EOF` at both commits.
   - Timing: the head is up to about 5× slower than the base on unreadable commands, still under 1 s at sizes no ordinary command reaches:

     | Command | Head | Base |
     |---|---|---|
     | 500 × `xargs touch <<<` | 0.64 s | 0.13 s |
     | `bash <<<` with 1,500 commands | 0.78 s | 0.15 s |
     | 100 × `xargs` | 0.13 s | 0.02 s |
5. **Holds** (see tests). MR-3 holds: df7468015 (Role: engineer) touches only allowed paths and no acceptance file. The acceptance cases come from 91922819a and 56e0e0207 (Role: independent-test-designer).

**F1. RO: read-only here-strings with a variable text are now refused**
- What: with an unknown or substituted text, these read-only idioms now get the unresolvable target, where the base allowed them:
  - `read -r a <<< "$v"`
  - `IFS=: read -r a b <<< "$line"`
  - `read -r a b <<< "$(git rev-parse HEAD HEAD)"`
  - `while read -r f; do echo "$f"; done <<< "$(git status --porcelain)"`
  - `mapfile -t L <<< "$(ls)"` and `readarray -t L <<< "$v"`
  - `sed 's/a/b/' <<< "$v"` and `awk '{print $1}' <<< "$line"`
  - `bc <<< "$x + 1"` and `v=$(git log -1); read -r a <<< "$v"`

  They should stay free, as `grep`, `cat`, `jq`, `sort`, `head` and `tr` do with the same texts. Literal texts stay free.
- Where: src/gov/guard/bash_writes.py:1778. In the new `hstr` reading, a here-string the shell expands, given to any reader not on the data list, becomes the unresolvable target. `read`, `mapfile`, `readarray`, a loop's `done`, `sed`, `awk` and `bc` are "code" readers, so the strict reading raises and the `hstr` reading adds the sentinel.
- How found: `run.sh ro2.txt ro2`; traced with `dbg.py` (strict reading raises "a here-string a command may run"; `strings` gives `[]`; `hstr` gives the unresolvable target).
- What would reverse it: those forms allowed through `decide()` at the head.
- Ordinary work: yes, because `read … <<< "$v"` and `while read …; done <<< "$(cmd)"` are everyday shell idioms for agents.
- Consequence: other (it refuses ordinary work and fails closed).
- Scope: in.

**F2. FALLBACK: xargs's output piped on to a shell is not judged**
- What: `xargs <<< 'touch T' | sh`, `xargs echo <<< 'touch T' | sh`, `xargs -n1 <<< 'touch T' | bash` and `xargs printf '%s\n' <<< 'touch T' | sh` are allowed. Real bash writes T for the first. The new xargs reading stops at "xargs runs echo" (bash_writes.py:1766) and never judges the shell stage after it. The base allowed these too, so this change did not make them worse.
- How found: `run.sh xp.txt xp`; `realbash.py` (`xargs <<< 'touch T' | sh` wrote T).
- What would reverse it: real bash not writing T for these, or the head refusing them.
- Ordinary work: no, because it needs a deliberate chain of xargs into a shell.
- Consequence: fails open.
- Scope: in.

**F3. FC: `eval "$(…)"` and output piped to a shell (older, not worse)**
- What: `eval "$(cat <<< 'touch T')"`, `eval "$(echo touch T)"` and `echo 'touch T' | xargs echo | sh` are allowed at both commits, and real bash writes T. The other forms that write T in real bash and are allowed at both are `… | xargs touch T` and `echo T | xargs touch`, which round 1's F7 already records as `xargs touch`, outside the ticket's scope.
- How found: `run.sh ro.txt ro`, `run.sh fb.txt fb`, `realbash.py`.
- What would reverse it: the base refusing any of them.
- Ordinary work: no, because it needs a deliberate construction (eval of computed text).
- Consequence: fails open.
- Scope: out (older than this change).

**F4. FALLBACK: xargs options the reading does not know are refused**
- What: these give the unresolvable target, also for an allowed A, where the base allowed them:
  - combined flags such as `xargs -rn1`
  - `--max-args 1` with its value as a separate word
  - `-e`, `-l` and `-i`

  `-0`/`--null`, `-d`, `-I`, `-a` and `-J` are also refused, as claim 2 states by design.
- How found: `run.sh ro.txt ro`.
- What would reverse it: those forms allowed through `decide()` at the head.
- Ordinary work: no, because xargs with a here-string and these option spellings is rare.
- Consequence: other (fails closed).
- Scope: in.

**F5. R3: `tee 0<<< x src/ok.py` is refused naming `0`**
- What: refused at both commits, naming the target `0` rather than T. This is the lead's observation, confirmed; the change did not alter it.
- How found: `run.sh r3.txt r3`.
- What would reverse it: the base allowing it.
- Ordinary work: no, because an fd prefix on a here-string is unusual.
- Consequence: other (fails closed).
- Scope: out.

**What I probed and found sound:**
- DEC-409: all 19 lift forms give the same answer at head and base, including `bash <<< 'gov pause --off'`, `cat <<< … | sh`, `xargs gov pause <<< --off`, `gov <<< x pause --off`, the lift form after a here-string, and the comment-apostrophe refusal. Its tests pass.
- No form that gave a target, the unresolvable target or a refusal at d3ba8e50b now passes and writes T in real bash.

```verdict
{"kpis": [{"kpi": "R3", "verdict": "pass", "findings": [{"id": "F5", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "FALLBACK", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "RO", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "DEC409", "verdict": "pass", "findings": []}, {"kpi": "FC", "verdict": "pass", "findings": [{"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}]}
```

Head probed: df74680150bb6add79ec8976a803488d3511ace5 (w2/W2-42a). Session: f309b71b-2755-4f92-b864-c2faf18d8764.