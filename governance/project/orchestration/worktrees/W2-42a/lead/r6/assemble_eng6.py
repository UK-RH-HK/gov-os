import re
L = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
log = open(L + "log/r3b2-red.log").read()
lines = log.splitlines()
failed = [l for l in lines if l.startswith("FAILED ")]
blocks, seen = [], set()
starts = [i for i, l in enumerate(lines) if re.match(r"^_+ test_\w+\[", l)]
end_summary = next(i for i, l in enumerate(lines) if "short test summary" in l)
for n, i in enumerate(starts):
    fn = re.match(r"^_+ (test_\w+)\[", lines[i]).group(1)
    j = starts[n + 1] if n + 1 < len(starts) else end_summary
    if fn in seen:
        continue
    seen.add(fn)
    blocks.append("\n".join(lines[i:j]).rstrip())
summary = lines[-1]
head = f"""# Brief: engineer, W2-42a (DAEO-03ub), a here-string read as data must not hide a command it feeds (DEC-1164 (18), R3 F1, second batch)

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh engineer.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head 98eff3c84.
Your paths: src/gov/guard/bash_writes.py and src/gov/guard/decide.py (the fix); tests/unit/guard/test_w2_42a* for unit
cases of what you change; one short paragraph in docs/changes/W2-42a-evidence.md. Nothing else changes. Never
tests/acceptance/ (the test designer's).
Commit with (all trailers in ONE final paragraph; no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The decided scope (the CTO's answer to the narrow check's F1, DEC-1164 (18): F1 (a))
The R3 round made a here-string whose text the shell expands (`"$v"`, `"$(…)"`) fail closed for any reader not on a
short data list, which refuses everyday read-only idioms. The rule to build:
1. `read`, `mapfile` and `readarray` take a here-string as data, whatever its text. Their own writes, if any (e.g. a
   redirect), are judged as usual.
2. A loop's here-string (`while read -r f; do …; done <<< "$(…)"`) is data for the loop; the loop body's commands are
   judged by their own words.
3. Data readers that never run their input (`sed`, `awk` without `system(`/`>`/`|`, `bc`, `grep`, `wc`, `cut`, `tr`,
   `sort`) take an expanded text as data. A reader whose script writes (an `awk` script with `>` or `system(`, `sed`
   with `w`/`-i`) is judged on that script, as today.
4. `bash`, `sh`, `zsh`, `dash`, `xargs`, `source`, `eval` and any reader not named above keep R3's fail-closed rule for
   an unknown text.
5. Nothing that R3's cases refuse becomes allowed; a `$(…)` inside a here-string's text still runs, so its writes are
   still judged. Fail closed: no form that gave a target, the unresolvable target or a refusal on 98eff3c84 gives
   neither after your change, except the read-only forms above. DEC-409's rule is unchanged (no agent Bash call holds
   the lift form of `gov pause` (--off)); its existing cases stay green (grep tests/ for `lift_refusal` and `DEC-409`).
**The second batch (the lead's finding at 885b0d0f6: each form writes T in real bash and is allowed there).** Taking a
here-string as data is safe only while that data is not run. (a) When `read` (alone or as a loop's condition) binds a
variable from a here-string and a later word of the call uses that variable as a command's name (`$f`, `${{f}}`,
`"$f" x`, `$a $b`, or after a prefix such as `env`, `command`, `time`), the guard cannot know the command: the
unresolvable target, whatever the text. A variable used only as an argument of a command that writes nothing stays
free. (b) `mapfile`/`readarray -C <callback>` (also joined, `-tC`) runs the callback as a command: a literal callback is
judged as that command; one the guard cannot know gives the unresolvable target.
Fix it in src/gov/guard/bash_writes.py (and decide.py only if needed). Nothing else changes.

## The failing output (and nothing else)
tests/acceptance/W2-42a/test_w2_42a_here_string_ro_2.py on 98eff3c84: `{summary.strip()}`.

```
""" + "\n".join(failed) + """
```

One full failure block per test function:

```
""" + "\n\n".join(blocks) + """
```

## Done when
- tests/acceptance/W2-42a passes whole (the 23 cases of test_w2_42a_here_string_ro_2.py, the 53 of test_w2_42a_here_string_ro.py and
  every other file there; no case green on 98eff3c84 turns red).
- tests/unit/guard and tests/unit/hooks pass, and DEC-409's lift cases wherever they live.
- One short paragraph in docs/changes/W2-42a-evidence.md naming the fix (DEC-1164 (18), R3 F1, second batch) and the counts (add to the F1 paragraph already there).

## How to run (every pytest through the heavy slot; TMPDIR is your sandbox's own $TMPDIR; /tmp is read-only)
    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \\
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \\
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \\
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \\
      -m "not local_only" -k "not real and not green_here and not time_limit"
(mkdir -p $TMPDIR/empty-home first.) The heavy slot may queue: that is a wait. Anything longer than one line goes in a
script file under $TMPDIR, run with bash or python3; use a unique heredoc delimiter if you write one. Literal paths as
write targets. Search with Read and Grep (no gov retrieve or gov context in the sandbox); search again once in
different words if the first does not answer. Never open the evaluation sets' root or any hidden folder; never print
a secret. If something is refused twice, stop and say so; never work around a refusal. No merge in the sandbox. A
resource gate's refusal is a wait.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (the pytest summary lines) / tests: / discoveries: /
risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers.

## The ticket's context packet (gov context DAEO-03ub --role engineer --budget 12000)

```json
"""
head += open(L + "r6/ctx-engineer.md").read() + "\n```\n"
open(L + "r6/eng-6.md", "w").write(head)
print(len(failed), "failed;", len(blocks), "blocks;", summary)
print("upper slots:", re.findall(r"\{[A-Z_]+\}", head))
