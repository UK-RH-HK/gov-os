import re
L = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
log = open(L + "log/r3-red.log").read()
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
head = f"""# Brief: engineer, W2-42a (DAEO-03ub), the fix of R3 and the here-string fail-opens (DEC-1164 (18))

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh engineer.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head ed77eb353.
Your paths: src/gov/guard/bash_writes.py and src/gov/guard/decide.py (the fix); tests/unit/guard/test_w2_42a* for unit
cases of what you change; one short paragraph in docs/changes/W2-42a-evidence.md. Nothing else changes. Never
tests/acceptance/ (the test designer's).
Commit with (all trailers in ONE final paragraph; no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The decided scope (the CTO's reopening of 2026-11-14 under DEC-1164 (18))
1. **The rule:** the word after `<<<` is the here-string's text, never the command's end. The words after it stay the
   command's arguments, so their write targets are judged (`tee <<< "x" T`, `tee -a <<< "x" T`, `cp <<< x x.py T`).
2. The text given to `bash <<<` / `sh <<<` is a command and is judged as one; `xargs CMD <<< WORDS` runs CMD with the
   text's words as arguments. A text the guard cannot know (`bash <<< "$X"`, `sh <<< "$(…)"`) fails closed.
3. A body-less heredoc (no body, no end line) after a `python3 -c` write must not lose that write.
4. Anything still unreadable fails closed. Read-only forms stay free (`grep -c b <<< "a"`, `wc -l <<< "$v"`,
   `cat <<< T`, `bash <<< 'echo hi'`).
5. Fail closed: no form that gave a target, the unresolvable target or a refusal before your change gives neither after
   it. DEC-409's rule is unchanged (no agent Bash call holds the lift form of `gov pause` (--off)); its existing cases
   stay green (grep tests/ for `lift_refusal` and `DEC-409`).

## The failing output (and nothing else)
tests/acceptance/W2-42a/test_w2_42a_here_string.py on ed77eb353: `{summary.strip()}`.

```
""" + "\n".join(failed) + """
```

One full failure block per test function:

```
""" + "\n\n".join(blocks) + """
```

## Done when
- tests/acceptance/W2-42a passes whole (the 31 cases of test_w2_42a_here_string.py and every other file there; no
  case green on ed77eb353 turns red).
- tests/unit/guard and tests/unit/hooks pass, and DEC-409's lift cases wherever they live.
- One short paragraph in docs/changes/W2-42a-evidence.md naming the fix (DEC-1164 (18), R3) and the counts.

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
head += open(L + "r5/ctx-engineer.md").read() + "\n```\n"
open(L + "r5/eng-4.md", "w").write(head)
print(len(failed), "failed;", len(blocks), "blocks;", summary)
print("upper slots:", re.findall(r"\{[A-Z_]+\}", head))
